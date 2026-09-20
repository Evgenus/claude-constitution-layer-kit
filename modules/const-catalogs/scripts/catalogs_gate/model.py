"""This module's own structures: a declared catalog, its dials, an item, the keys of its findings."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import cache

from const_gate.model import Finding

DEFAULT_WIDTH = 4
MAX_WIDTH = 9  # a billion items; past it a fix line would outgrow what the platform shows
PREFIX_RE = re.compile(r"[a-z0-9]+")  # used with fullmatch: '$' would let a trailing line break through
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"  # ASCII on purpose, like the digits: \d would take any script's
EXTENSION = ".md"


class Key(StrEnum):
    """Stable handles of this module's findings."""

    K1 = "K1"
    K2 = "K2"
    K3 = "K3"
    K4 = "K4"


class Advice(StrEnum):
    """Which number the fix of a finding about a name tells the file to carry."""

    NEXT = "next"  # a new file: the catalog's next number
    KEEP = "keep"  # a file that exists and whose name shows its number: that number, in the form
    FULL = "full"  # a new file, and the width cannot write the next number
    WIDE = "wide"  # a file that exists and shows a number the width cannot write
    CONTESTED = "contested"  # a file that exists and shows a number another file shows too
    WORDS = "words"  # a file that exists and shows no number: the rule, in words


class Read(StrEnum):
    """How much of history was read."""

    ALL = "all"  # every commit of the branch — or there is no commit yet, and nothing was ever added
    SHALLOW = "shallow"  # what a shallow clone holds: a part
    NOT = "not"  # nothing: the clock ran out, or git failed or gave an answer nobody expects


@dataclass(frozen=True, slots=True)
class Catalog:
    """A numbered kind, as the dial declares it: the Markdown documents in its territory are
    its items."""

    prefix: str
    width: int
    territory: tuple[str, ...]

    def number_of(self, stem: str) -> int | None:
        """The number a file name carries, or None when the name has not the catalog's form.
        Verdicts rest on this."""
        found = _form(self.prefix, self.width).fullmatch(stem)
        return int(found.group(1)) if found else None

    def number_shown(self, stem: str) -> int | None:
        """The number a name shows though it may lack the form — another case, another width, no
        slug. Advice rests on this, never a verdict: a legacy item keeps the number it is cited
        by, and the next number goes above every number shown."""
        found = _hint(self.prefix).match(stem)
        return int(found.group(1)) if found else None

    def can_write(self, number: int) -> bool:
        return len(str(number)) <= self.width

    def written(self, number: int) -> str:
        return f"{self.prefix}-{number:0{self.width}d}"


@cache
def _form(prefix: str, width: int) -> re.Pattern[str]:
    return re.compile(rf"{re.escape(prefix)}-([0-9]{{{width}}})-{SLUG}")


@cache
def _hint(prefix: str) -> re.Pattern[str]:
    return re.compile(rf"{re.escape(prefix)}[-_ ]?([0-9]{{1,18}})(?![0-9])", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Taken:
    """The numbers the other items of one catalog carry in the working tree, each with the
    file that carries it: what a file that does not exist yet is judged against."""

    catalog: Catalog
    holders: Mapping[int, str]  # the verdict's: numbers on names that have the form
    shown: int | None  # advice only: the highest number any name in the territory shows, formed or not
    in_history: int | None = None  # advice only: the highest the branch's history ever added
    history_read: bool = False  # False: not read yet, or a clone whose history cannot be read

    @property
    def next(self) -> int | None:
        """The number to name to a new item: one more than the highest the catalog has held, in
        the working tree or in history; None once the width cannot write it."""
        number = max(self.shown or 0, self.in_history or 0) + 1
        return number if self.catalog.can_write(number) else None


@dataclass(frozen=True, slots=True)
class NameToTake:
    """The advice a finding about a name ends in."""

    advice: Advice
    number: int | None = None
    history_read: bool = True
    other: str = ""  # CONTESTED: the other file that shows the number


@dataclass(frozen=True, slots=True)
class Reach:
    """How far a catalog's numbers go: in the working tree, and in history where it went further."""

    catalog: Catalog
    in_tree: int | None
    in_history: int | None

    @property
    def full(self) -> bool:
        highest = max(self.in_tree or 0, self.in_history or 0)
        return not self.catalog.can_write(highest + 1)


@dataclass(frozen=True, slots=True)
class CatalogDials:
    """This module's own dials, validated. The two every gate has are read by the shared code."""

    catalogs: tuple[Catalog, ...]


@dataclass(frozen=True, slots=True)
class Item:
    """One document of a catalog, examined."""

    rel: str
    catalog: Catalog
    number: int | None  # None: the file name carries none, which is finding K1
    findings: tuple[Finding, ...]
