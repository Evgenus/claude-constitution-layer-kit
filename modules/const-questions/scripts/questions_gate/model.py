"""This module's own structures: its dials and the keys of its findings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

DEFAULT_TERRITORIES = ("*.md",)
DEFAULT_MARKERS = ("[decide:", "TODO", "TBD", "FIXME")


class Key(StrEnum):
    """Stable handles of this module's findings."""

    Q1 = "Q1"  # a line of a covered document carries an open-question marker


@dataclass(frozen=True, slots=True)
class QuestionsDials:
    territories: tuple[str, ...]
    markers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Hit:
    """A marker found on a line: where, which, and the line as written."""

    line: int
    marker: str
    text: str
