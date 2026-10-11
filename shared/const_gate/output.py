"""Everything this gate prints, printed once and also appended to a log — through the
standard library's ``logging``, not a hand-made tee.

A blocked write leaves no trace in git, and neither does a warn-level finding or a
configuration failure; the log is where those events survive. Each call of ``out`` or
``err`` becomes one JSON line: timestamp, module, gate, mode, session, stream, text — a
text of several lines, a verdict or a traceback, stays one record, its newlines escaped
by JSON. The log holds what was printed and nothing more.

How ``logging`` is wired:

- one named logger, propagation off, so nothing another library logs can reach the screen:
  in hook mode stdout and stderr are a protocol, not a console;
- two stream handlers split by level: INFO is stdout, WARNING and above is stderr. The
  stream is chosen by the caller (``out`` or ``err``) because it is part of the platform's
  contract — exit 2 feeds stderr to the model, severity warn needs stdout to be one JSON
  object — and the level merely carries that choice;
- a ``MemoryHandler`` holds the records until the log location is known (the dial is read
  after the first lines are printed), so one run lands in one place;
- a ``RotatingFileHandler`` is its target: rotation at a fixed size, one old file kept.

Location, first that applies: the dial ``log_dir`` (repository-relative, verified
git-ignored by the caller); the platform's per-plugin data directory; nowhere.

A logging failure never changes a verdict. ``logging.raiseExceptions`` is switched off so
that a handler's own error is swallowed by the library instead of being printed to stderr,
where it would become the first line the user sees; the one ``except OSError`` below covers
creating the directory. This is the output log's one swallowed error, deliberately: a full disk
must not turn a finding into a pass or a pass into a failure. A module that keeps an advisory memo
beside the log swallows that memo's failures the same way, said so at its place.
"""

from __future__ import annotations

import io
import json
import logging
import logging.handlers
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from . import identity
from .model import Mode, Stream


def log_name() -> str:
    return identity.current().namespace + ".jsonl"


ROTATE_AT = 1_048_576  # bytes; the previous log is kept as <name>.1
HELD_RECORDS = 1_000_000  # the memory handler never flushes on its own; the guard flushes once

_LEVEL = {Stream.STDOUT: logging.INFO, Stream.STDERR: logging.WARNING}


class _Context(logging.Filter):
    """Stamps every record with the run's mode and session."""

    def __init__(self, mode: Mode) -> None:
        super().__init__()
        self.mode = mode
        self.session = ""

    def filter(self, record: logging.LogRecord) -> bool:
        record.gate_mode = self.mode.value
        record.gate_session = self.session
        return True


class _JsonLine(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        stream = Stream.STDERR if record.levelno >= logging.WARNING else Stream.STDOUT
        return json.dumps(
            {
                "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="seconds"),
                "module": identity.current().namespace,
                "gate": identity.current().gate,
                "mode": getattr(record, "gate_mode", ""),
                "session": getattr(record, "gate_session", ""),
                "stream": stream.value,
                "text": record.getMessage(),
            },
            ensure_ascii=False,
        )


class _Below(logging.Filter):
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.level


class Output:
    def __init__(self, mode: Mode) -> None:
        logging.raiseExceptions = False  # see the module docstring
        for stream in (sys.stdout, sys.stderr):  # a verdict line must survive a stream that cannot encode '—'
            if isinstance(stream, io.TextIOWrapper):
                stream.reconfigure(errors="backslashreplace")
        data_dir = os.environ.get("CLAUDE_PLUGIN_DATA", "")
        self.log_file: Path | None = Path(data_dir) / log_name() if data_dir else None
        self._context = _Context(mode)
        self._held = logging.handlers.MemoryHandler(HELD_RECORDS, flushLevel=logging.CRITICAL + 1)
        to_stdout = logging.StreamHandler(sys.stdout)
        to_stdout.addFilter(_Below(logging.WARNING))
        to_stderr = logging.StreamHandler(sys.stderr)
        to_stderr.setLevel(logging.WARNING)
        self._logger = logging.getLogger(identity.current().namespace)
        self._logger.handlers.clear()
        self._logger.propagate = False
        self._logger.setLevel(logging.INFO)
        self._logger.addFilter(self._context)
        for handler in (to_stdout, to_stderr, self._held):
            self._logger.addHandler(handler)

    @property
    def session(self) -> str:
        return self._context.session

    @session.setter
    def session(self, value: str) -> None:
        self._context.session = value

    def use_log_dir(self, directory: Path) -> None:
        self.log_file = directory / log_name()

    def out(self, text: str) -> None:
        self._emit(Stream.STDOUT, text)

    def err(self, text: str) -> None:
        self._emit(Stream.STDERR, text)

    def _emit(self, stream: Stream, text: str) -> None:
        self._logger.log(_LEVEL[stream], text)  # one record, and so one log line, per call

    def flush(self) -> None:
        """Write what was printed. Called once, by the guard, however the run ended."""
        if self.log_file is not None:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass  # deliberate: see the module docstring
            else:
                target = logging.handlers.RotatingFileHandler(
                    self.log_file, maxBytes=ROTATE_AT, backupCount=1, encoding="utf-8", delay=True
                )
                target.setFormatter(_JsonLine())
                self._held.setTarget(target)
                self._held.flush()
                target.close()
        self._held.close()
