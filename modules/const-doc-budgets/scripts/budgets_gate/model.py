"""This module's own structures: its dials — the ceilings and the departures — the level of a
ceiling, a measured document, and the key of its one finding."""

from __future__ import annotations

import datetime
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

WINDOW_DAYS = 30  # a ceiling blocks only on this many days of observed data or more
MARGIN_PERCENT = 10  # the rule of thumb: the window's longest document plus this many percent ...
ROUND_TO = 1000  # ... rounded up to a multiple of this


class Level(StrEnum):
    """What an excess over a ceiling is: a finding, or a note."""

    ERROR = "error"
    WARNING = "warning"


class Key(StrEnum):
    """Stable handles of this module's findings."""

    B1 = "B1"  # a document over a ceiling at level error


@dataclass(frozen=True, slots=True)
class Window:
    """The first and the last day of the observed data a ceiling's number was set from; its span,
    `days`, is the last day minus the first."""

    start: datetime.date
    end: datetime.date

    @property
    def days(self) -> int:
        return (self.end - self.start).days


@dataclass(frozen=True, slots=True)
class Ceiling:
    """One entry of the ceilings dial: its name, the documents it holds as path patterns, the most
    characters one of them may have, what an excess is, and the data the number came from."""

    name: str
    paths: tuple[str, ...]
    max: int
    level: Level
    window: Window


@dataclass(frozen=True, slots=True)
class Departure:
    """One entry of the departures dial: the documents it covers, as path patterns; the ceilings it
    lifts there, by name; and the one-line reason — the route for a document that must stand over
    its ceiling, an accepted record among them."""

    paths: tuple[str, ...]
    allow: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class BudgetDials:
    ceilings: tuple[Ceiling, ...]
    departures: tuple[Departure, ...]


def characters(text: str) -> int:
    """The length of a document in characters as the project's conventions define them: Unicode code points of
    the file read as UTF-8, a CRLF counted as one, nothing normalized and nothing left out — bytes
    that are not UTF-8 counted as the replacement characters the decoder put in their place."""
    return len(text) - text.count("\r\n")


def rule_of_thumb(length: int) -> int:
    """The window's longest document plus the margin, rounded up: a number no document of the
    window is over on the day it is set, with room for the edits that lengthen a frozen one."""
    raised = length + (length * MARGIN_PERCENT + 99) // 100
    return -(-raised // ROUND_TO) * ROUND_TO


def longer(item: tuple[str, int], than: tuple[str, int] | None) -> bool:
    """Whether a (path, length) is longer than another, or as long and first in path order: the one
    tie rule of the scan and the report, so both name the same document."""
    return than is None or item[1] > than[1] or (item[1] == than[1] and item[0] < than[0])


def longest(items: Sequence[tuple[str, int]]) -> tuple[str, int] | None:
    best: tuple[str, int] | None = None
    for item in items:
        if longer(item, best):
            best = item
    return best
