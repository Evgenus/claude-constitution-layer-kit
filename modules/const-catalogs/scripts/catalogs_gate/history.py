"""What the branch's history ever added, read for advice only: the next number named to a
new item is one more than the highest the catalog has held, so the number of a deleted item
is not suggested again. No verdict rests on this, and none waits for it: the hook reads
history only once a finding that names a number is certain, and gives up after a few seconds.
A repository whose history cannot be read — no commit yet, a shallow clone, a history too long
to read in time — gives the working tree's answer, and the text that names the number says so."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .checks import stem_of
from .model import EXTENSION, Catalog

HOOK_SECONDS = 5.0  # the hook's patience; the scan has no clock to beat and passes None

# --no-renames: a rename is then an addition and a deletion, so the name renamed to is seen as added
ADDED = ["log", "-z", "--format=", "--name-only", "--diff-filter=A", "--no-renames", "--", "*" + EXTENSION]
SHALLOW = ["rev-parse", "--is-shallow-repository"]


@dataclass(frozen=True, slots=True)
class History:
    stems: tuple[str, ...]  # the file name, without .md, of every Markdown file ever added
    shallow: bool = False
    unread: bool = False  # git gave no list: no commit yet, a failure, or the clock ran out

    @property
    def complete(self) -> bool:
        return not self.shallow and not self.unread

    def highest(self, catalog: Catalog) -> int | None:
        """The highest number a name of the catalog's form ever carried, wherever it was added,
        under its old name and its new one alike when it was renamed."""
        numbers = [number for stem in self.stems if (number := catalog.number_of(stem)) is not None]
        return max(numbers, default=None)


def read_history(root: Path, seconds: float | None = None) -> History:
    try:
        added = _git(ADDED, root, seconds)
        shallow = _git(SHALLOW, root, seconds)
    except subprocess.TimeoutExpired:
        return History((), unread=True)
    if added.returncode != 0:  # no commit yet, most likely; whatever the cause, nothing was read
        return History((), unread=True)
    names = [name.strip() for name in os.fsdecode(added.stdout).split("\0")]
    return History(_stems(names), shallow=shallow.stdout.strip() == b"true")


def _git(args: Sequence[str], root: Path, seconds: float | None) -> subprocess.CompletedProcess[bytes]:
    """Git has answered this run already, so it is there; what is new here is the clock."""
    env = {**os.environ, "LC_ALL": "C"}
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=False, env=env, timeout=seconds
    )


def _stems(names: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({stem_of(name) for name in names if name.endswith(EXTENSION)}))
