"""What the branch's history ever added, read for advice only: the next number named to a
new item is one more than the highest the catalog has held, so the number of a deleted item
is not suggested again. No verdict rests on this: a clone without history — a shallow one, a
repository with no commit yet — gives the working tree's answer, and the scan's line says so."""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from const_gate.repository import git

from .checks import stem_of
from .model import Catalog


@dataclass(frozen=True, slots=True)
class History:
    stems: tuple[str, ...]  # the file name, without .md, of every Markdown file ever added
    shallow: bool

    def highest(self, catalog: Catalog) -> int | None:
        """The highest number a name of the catalog's form ever carried, wherever it was added."""
        numbers = [number for stem in self.stems if (number := catalog.number_of(stem)) is not None]
        return max(numbers, default=None)


def read_history(root: Path) -> History:
    # --no-renames: a rename is then an addition and a deletion, so the new name is seen as added
    added = git(
        ["log", "-z", "--format=", "--name-only", "--diff-filter=A", "--no-renames", "--", "*.md"], root
    )
    if added.returncode != 0:  # no commit yet: nothing was ever added
        return History((), shallow=False)
    names = [name.strip() for name in os.fsdecode(added.stdout).split("\0")]
    shallow = git(["rev-parse", "--is-shallow-repository"], root).stdout.strip() == b"true"
    return History(_stems(names), shallow)


def _stems(names: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({stem_of(name) for name in names if name.lower().endswith(".md")}))
