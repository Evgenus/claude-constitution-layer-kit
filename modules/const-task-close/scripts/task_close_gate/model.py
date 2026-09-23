"""This module's own structures: a coverage pair, the dials, a declaration, a range, the keys
of its findings."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")  # a pair's name, kebab-case; used with fullmatch
KEY_RE = re.compile(r"[A-Za-z0-9-]+")  # a trailer key as git reads one; used with fullmatch
DEFAULT_TRUNK = "main"
DEFAULT_KEY = "No-Doc-Impact"
BODY = "the body"  # where a declaration read from the --body file stands
SHOWN_PATHS = 3  # how many of the paths a finding lists before "…"
SHOWN_LINES = 5  # how many of git status's lines the turn-end finding lists before "…"


class Key(StrEnum):
    """Stable handles of this module's findings and its own configuration failure."""

    T1 = "T1"  # the working tree is dirty at turn end
    T2 = "T2"  # a covered pair neither updated nor declared
    T3 = "T3"  # a declaration naming no pair
    T4 = "T4"  # a declaration without a reason
    X1 = "X1"  # a pair's document does not exist at the range's tip
    X2 = "X2"  # a pair's document is a directory at HEAD, which no change can update


@dataclass(frozen=True, slots=True)
class Pair:
    """One entry of the coverage map: the code these documents describe."""

    name: str
    code: tuple[str, ...]  # gitignore patterns
    docs: tuple[str, ...]  # repository-relative paths


@dataclass(frozen=True, slots=True)
class TaskCloseDials:
    """This module's own dials, validated. The two every gate has are read by the shared code."""

    coverage: tuple[Pair, ...]
    trunk: str
    declaration_key: str
    working_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Declaration:
    """One no-impact line, wherever it was read: `<pair> — <reason>` after the key."""

    where: str  # `commit <short hash>` or `the body`
    value: str  # the whole value, as written
    pair: str  # before the dash, stripped — a name to check against the map
    reason: str  # after the dash, stripped; empty when the line carries none


@dataclass(frozen=True, slots=True)
class Range:
    """The change under examination: the commits after `base` up to `tip`, and the paths
    their diff names — a deleted or renamed path among them, since renames are not folded."""

    base: str | None  # a full hash; None when the tip is a root commit and nothing landed before
    tip: str
    base_short: str  # what the count line shows; the tip's own short hash when base is None
    tip_short: str
    commits: int
    paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PairVerdict:
    """One pair against the range."""

    pair: Pair
    touched: tuple[str, ...]  # the range's paths that match the pair's code, its documents excluded
    updated: tuple[str, ...]  # the pair's documents that are among the range's paths

    @property
    def covered(self) -> bool:
        return bool(self.touched)
