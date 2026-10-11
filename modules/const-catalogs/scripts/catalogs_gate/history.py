"""What the branch's history ever added, read for advice only: the next number named to a
new item is one more than the highest the catalog has held, so the number of a deleted item
is not suggested again. No verdict rests on this, and none waits for it: the hook reads
history only once a finding that names a number is certain, against one clock for all of
git's answers, and whatever goes wrong here — the clock, a git that fails or has vanished —
ends in the working tree's answer and a text that says history was not read. Nothing in this
module raises."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .checks import stem_of
from .model import EXTENSION, Catalog, Read

# The most the hook waits for all of history: a cap, which the caller passes shortened to what is left of the
# hook's deadline; the scan has no clock to beat and passes None.
HOOK_SECONDS = 5.0

HEAD = ["rev-parse", "--verify", "-q", "HEAD"]
SHALLOW = ["rev-parse", "--is-shallow-repository"]
# --no-renames: a rename is then an addition and a deletion, so the name renamed to is seen as added;
# log.showSignature=true would print a signature check before the names of each commit
ADDED = [
    "-c",
    "log.showSignature=false",
    "log",
    "-z",
    "--format=",
    "--name-only",
    "--diff-filter=A",
    "--no-renames",
    "--",
    "*" + EXTENSION,
]


@dataclass(frozen=True, slots=True)
class History:
    stems: tuple[str, ...]  # the file name, without .md, of every Markdown file ever added
    read: Read = Read.ALL

    @property
    def complete(self) -> bool:
        return self.read is Read.ALL

    def highest(self, catalog: Catalog) -> int | None:
        """The highest number a name of the catalog's form ever carried, wherever it was added,
        under its old name and its new one alike when it was renamed."""
        numbers = [number for stem in self.stems if (number := catalog.number_of(stem)) is not None]
        return max(numbers, default=None)


def read_history(root: Path, seconds: float | None = None) -> History:
    deadline = None if seconds is None else time.monotonic() + seconds
    try:
        if _git(HEAD, root, deadline).returncode != 0:
            return History(())  # no commit yet
        shallow = _git(SHALLOW, root, deadline)
        answer = shallow.stdout.strip()
        added = _git(ADDED, root, deadline)
    except (subprocess.TimeoutExpired, OSError):  # the clock; or git is gone, or cannot be started
        return History((), Read.NOT)
    if shallow.returncode != 0 or answer not in (b"true", b"false") or added.returncode != 0:
        return History((), Read.NOT)
    names = [name.strip() for name in os.fsdecode(added.stdout).split("\0")]
    return History(_stems(names), Read.SHALLOW if answer == b"true" else Read.ALL)


def _git(args: Sequence[str], root: Path, deadline: float | None) -> subprocess.CompletedProcess[bytes]:
    left = None if deadline is None else max(deadline - time.monotonic(), 0.01)
    env = {**os.environ, "LC_ALL": "C"}
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=False, env=env, timeout=left)


def _stems(names: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({stem_of(name) for name in names if name.endswith(EXTENSION)}))
