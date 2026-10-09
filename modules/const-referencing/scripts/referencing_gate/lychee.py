"""The one place the link checker is found, its version read, its invocation built and its
report parsed.

The gate owns the invocation. lychee loads a `lychee.toml` from its working directory
unasked and honours a `.lycheeignore` there, so it is started in an empty scratch directory
with the module's own configuration file and absolute inputs: nothing in the checked
repository can change the verdict. It exits 2 on a broken link and on bad usage alike, the
second with nothing on stdout, so a finding is believed only with a parsed report.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from time import monotonic
from urllib.parse import unquote, urlsplit

from const_gate.errors import ConfigurationFailure

from . import messages

TOOL = "lychee"
FLOOR = (0, 24, 2)
HOOK_SECONDS = 20  # a check after a write's one budget: reading, masking and the run; the scan has none
VERSION_SECONDS = 5  # the probe's own, in every mode, outside HOOK_SECONDS; both under the handler's timeout
LEAST_FOR_THE_RUN = 0.01  # the run's timeout when the budget is spent by then: a timeout of 0 would not wait
CONFIG = Path(__file__).resolve().parent.parent / "lychee.toml"
_VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")
_NO_FRAGMENT = "Cannot find fragment"
_NO_FILE = "File not found"


class BreakKind(StrEnum):
    NO_FILE = "no file"
    NO_FRAGMENT = "no fragment"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Break:
    """One link the checker could not resolve. `target` is repository-relative where the
    address lies inside the repository, else as the checker gave it."""

    source: str
    line: int
    target: str
    fragment: str | None
    kind: BreakKind
    words: str  # the checker's own, for a kind this module has no text for


@dataclass(frozen=True, slots=True)
class Budget:
    """The one deadline of a check after a write. It starts once the file list, the territory matching
    and the version probe are done, before the covered texts are read, and the reads, the masking and
    the link checker's run draw on it together; the scan has none."""

    seconds: float  # the whole budget, as it is told to the user
    deadline: float  # on the monotonic clock

    @classmethod
    def start(cls, seconds: float) -> Budget:
        return cls(seconds, monotonic() + seconds)

    def check(self) -> None:
        """Called after each document is read and after each is masked: once the deadline has passed,
        the check stops here, before the link checker is run, and says whose time it was."""
        if monotonic() >= self.deadline:
            raise ConfigurationFailure(messages.x3_out_of_time(self.seconds))

    def left(self) -> float:
        """What the run may take: the deadline's remainder, but not under `LEAST_FOR_THE_RUN` and not
        over the budget."""
        return min(max(self.deadline - monotonic(), LEAST_FOR_THE_RUN), self.seconds)


def find_breaks(root: Path, inputs: Sequence[str], budget: Budget | None, binary: str | None) -> list[Break]:
    """Every unresolved link of the inputs, repository-relative paths of files that exist. `budget` is
    the check's deadline, of which the run gets what is left, None for no limit: the caller chooses,
    there is no default. `binary` is the checker the caller found and probed with `require`, before
    it began the budget; None finds and probes it here, as the scan does. The version probe has its
    own `VERSION_SECONDS`, wherever it runs, and takes none of the budget."""
    if binary is None:
        binary = require()
    if not inputs:
        return []
    with tempfile.TemporaryDirectory() as elsewhere:
        try:
            done = subprocess.run(
                [
                    binary,
                    "--offline",
                    "--include-fragments",
                    "--no-progress",
                    "--format",
                    "json",
                    "--config",
                    str(CONFIG),
                    "--root-dir",
                    str(root),
                    "--files-from",
                    "-",
                ],
                input="".join(f"{root / rel}\n" for rel in inputs),
                cwd=elsewhere,
                capture_output=True,
                text=True,
                timeout=None if budget is None else budget.left(),
                check=False,
            )
        except subprocess.TimeoutExpired as late:
            whole = late.timeout if budget is None else budget.seconds
            raise ConfigurationFailure(messages.x3_too_slow(whole)) from late
    breaks = _parse(root, done.stdout)
    if done.returncode not in (0, 2) or breaks is None:
        first = (done.stderr.strip().splitlines() or [""])[0]
        raise ConfigurationFailure(messages.x3_no_report(f"exit {done.returncode}", first))
    return breaks


def require() -> str:
    """The checker's path, or the configuration failure that says what is missing. Public so
    that an act that changes files can ask before it changes any."""
    return _binary()


def _binary() -> str:
    binary = shutil.which(TOOL)
    if binary is None:
        raise ConfigurationFailure(messages.x1_no_lychee(_floor()))
    try:
        said = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=VERSION_SECONDS, check=False
        ).stdout
    except subprocess.TimeoutExpired as late:
        raise ConfigurationFailure(messages.x3_no_report(f"no answer in {VERSION_SECONDS} s", "")) from late
    except OSError:
        said = ""
    version = _VERSION.search(said)
    if version is None or tuple(int(part) for part in version.groups()) < FLOOR:
        raise ConfigurationFailure(messages.x2_lychee_too_old(_floor(), said.strip()))
    return binary


def _floor() -> str:
    return ".".join(str(part) for part in FLOOR)


def _parse(root: Path, stdout: str) -> list[Break] | None:
    """The report, parsed once into typed breaks; None when stdout holds no report."""
    try:
        loaded: object = json.loads(stdout)
    except ValueError:
        return None
    error_map = loaded.get("error_map") if isinstance(loaded, dict) else None
    if not isinstance(error_map, dict):
        return None
    real_root = Path(os.path.realpath(root))
    found: list[Break] = []
    for source, entries in error_map.items():
        for entry in entries if isinstance(entries, list) else []:
            if isinstance(entry, dict):
                found.append(_break(real_root, str(source), entry))
    return sorted(found, key=lambda b: (b.source, b.line, b.target, b.fragment or ""))


def _break(real_root: Path, source: str, entry: Mapping[object, object]) -> Break:
    status, span = entry.get("status"), entry.get("span")
    words = str(status.get("text", "")) if isinstance(status, dict) else ""
    line = span.get("line") if isinstance(span, dict) else None
    url = str(entry.get("url", ""))
    address = urlsplit(url)
    kind = (
        BreakKind.NO_FRAGMENT
        if words.startswith(_NO_FRAGMENT)
        else BreakKind.NO_FILE
        if words.startswith(_NO_FILE)
        else BreakKind.OTHER
    )
    target = _within(real_root, unquote(address.path)) if address.scheme == "file" else url
    fragment = unquote(address.fragment) or None
    return Break(
        _within(real_root, source), line if isinstance(line, int) else 0, target, fragment, kind, words
    )


def _within(real_root: Path, path: str) -> str:
    try:
        return Path(os.path.realpath(path)).relative_to(real_root).as_posix()
    except ValueError:
        return path
