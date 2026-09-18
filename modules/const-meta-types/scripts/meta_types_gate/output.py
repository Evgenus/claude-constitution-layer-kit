"""Everything this gate prints, printed once and also appended to a log.

A blocked write leaves no trace in git, and neither does a warn-level finding or a
configuration failure; the log is where those events survive. Each printed line becomes
one JSON line: timestamp, module, gate, mode, session, stream, text. The log holds what
was printed and nothing more.

Location, first that applies: the dial ``log_dir`` (repository-relative, verified
git-ignored by the caller); the platform's per-plugin data directory; nowhere. Lines are
held in memory until ``flush``, so that everything one invocation printed lands in one
place even when the dial is read after the first line was printed.
A logging failure never changes a verdict: this is the one place the gate swallows an
exception, deliberately, because a full disk must not turn a finding into a pass or a
pass into a failure.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .model import GATE, NAMESPACE, Mode, Stream

LOG_NAME = NAMESPACE + ".jsonl"
ROTATE_AT = 1_048_576          # bytes; the previous log is kept as <name>.1


class Output:
    def __init__(self, mode: Mode) -> None:
        self.mode = mode
        self.session = ""
        data_dir = os.environ.get("CLAUDE_PLUGIN_DATA", "")
        self.log_file: Path | None = Path(data_dir) / LOG_NAME if data_dir else None
        self._pending: list[str] = []

    def use_log_dir(self, directory: Path) -> None:
        self.log_file = directory / LOG_NAME

    def out(self, text: str) -> None:
        self._emit(Stream.STDOUT, text)

    def err(self, text: str) -> None:
        self._emit(Stream.STDERR, text)

    def _emit(self, stream: Stream, text: str) -> None:
        target = sys.stdout if stream is Stream.STDOUT else sys.stderr
        print(text, file=target)
        self._append(stream, text)

    def _append(self, stream: Stream, text: str) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for line in text.splitlines() or [""]:
            self._pending.append(json.dumps(
                {"ts": now, "module": NAMESPACE, "gate": GATE, "mode": self.mode.value,
                 "session": self.session, "stream": stream.value, "text": line}, ensure_ascii=False))

    def flush(self) -> None:
        """Write what was printed. Called once, by the guard, however the run ended."""
        if self.log_file is None or not self._pending:
            return
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            if self.log_file.exists() and self.log_file.stat().st_size > ROTATE_AT:
                os.replace(self.log_file, self.log_file.with_name(LOG_NAME + ".1"))
            with self.log_file.open("a", encoding="utf-8") as log:
                log.write("\n".join(self._pending) + "\n")
        except OSError:
            pass    # deliberate: see the module docstring
        self._pending.clear()
