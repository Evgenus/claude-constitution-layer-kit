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

from const_gate import identity
from const_gate.errors import ConfigurationFailure

from . import messages

TOOL = "lychee"
FLOOR = (0, 24, 2)
# In a hook these are caps: each wait takes the smaller of its cap and what is left of the hook's one deadline
# (`identity.hook_seconds`), which the gate's tie holds them to fit together.
HOOK_SECONDS = 20  # the cap of a hook check's one budget: reading, masking and the run; the scan has none
VERSION_SECONDS = 5  # the probe's cap, in every mode, outside the budget of HOOK_SECONDS
# What each wait is, as the shared lines name it: "the hook's budget is spent before <this>", asked of the
# deadline as the wait begins and named again when the deadline cuts the wait.
PROBE_BEFORE = "lychee reported its version"
READ_BEFORE = "the covered documents were read"  # the budget of the check before a write
RUN_BEFORE = "lychee finished the link check"  # the budget of the check after a write
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
    """The one deadline of a hook's check, before a write or after it, within the hook's own. It starts once
    the file list and the territory matching are done, and in a check after a write the version probe too,
    before the covered texts are read. After a write the reads, the masking and the link checker's run draw
    on it together; before a write only the reads do, since no checker is run there. The scan has none."""

    seconds: float  # the whole budget, as it is told to the user
    deadline: float  # on the monotonic clock
    before_write: bool = False  # the check before a write: it reads and runs no checker

    @classmethod
    def start(cls, seconds: float, before_write: bool = False) -> Budget:
        return cls(seconds, monotonic() + seconds, before_write)

    def check(self) -> None:
        """Called after each document is read and after each is masked: once the deadline has passed,
        the check stops here, before it is done, and says whose time it was: the reading of the tree
        before a write, the reading and the masking before the checker could be run after one. A budget
        that the hook's deadline shortened ends in the shared C12.14 line, which says whose time it was."""
        if monotonic() >= self.deadline:
            own = messages.x3_out_of_time(self.seconds, self.before_write)
            before = READ_BEFORE if self.before_write else RUN_BEFORE
            raise identity.ran_out(self.seconds, HOOK_SECONDS, before, own)

    def left(self) -> float:
        """What the run may take: the deadline's remainder, but not under `LEAST_FOR_THE_RUN` and not
        over the budget."""
        return min(max(self.deadline - monotonic(), LEAST_FOR_THE_RUN), self.seconds)


def find_breaks(root: Path, inputs: Sequence[str], budget: Budget | None, binary: str | None) -> list[Break]:
    """Every unresolved link of the inputs, repository-relative paths of files that exist. `budget` is
    the check's deadline, of which the run gets what is left, None for no limit: the caller chooses,
    there is no default. `binary` is the checker the caller found and probed with `require`, before
    it began the budget; None finds and probes it here, as the scan does. The version probe has its
    own seconds, `VERSION_SECONDS` unless the caller gives `require` fewer, and takes none of the budget."""
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
            if budget is None:
                raise ConfigurationFailure(messages.x3_too_slow(late.timeout)) from late
            too_slow = messages.x3_too_slow(budget.seconds)
            raise identity.ran_out(budget.seconds, HOOK_SECONDS, RUN_BEFORE, too_slow) from late
    breaks = _parse(root, done.stdout)
    if done.returncode not in (0, 2) or breaks is None:
        first = (done.stderr.strip().splitlines() or [""])[0]
        raise ConfigurationFailure(messages.x3_no_report(f"exit {done.returncode}", first))
    return breaks


def require(seconds: float = VERSION_SECONDS) -> str:
    """The checker's path, or the configuration failure that says what is missing. Public so
    that an act that changes files can ask before it changes any. `seconds` is how long the version
    probe may take: its cap, unless a hook has less of its deadline left, and a probe given less that then
    runs out is the shared C12.14 line, not this module's, which would name the shortened number."""
    return _binary(seconds)


def _binary(seconds: float) -> str:
    binary = shutil.which(TOOL)
    if binary is None:
        raise ConfigurationFailure(messages.x1_no_lychee(_floor()))
    try:
        said = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=seconds, check=False
        ).stdout
    except subprocess.TimeoutExpired as late:
        no_answer = messages.x3_no_report(f"no answer in {seconds:g} s", "")
        raise identity.ran_out(seconds, VERSION_SECONDS, PROBE_BEFORE, no_answer) from late
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
