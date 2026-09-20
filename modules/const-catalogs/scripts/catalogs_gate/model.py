"""This module's own structures: a declared catalog, its dials, an item, the keys of its findings."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import cache

from const_gate.model import Finding

DEFAULT_WIDTH = 4
PREFIX_RE = re.compile(r"^[a-z0-9]+$")
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"


class Key(StrEnum):
    """Stable handles of this module's findings."""

    K1 = "K1"
    K2 = "K2"
    K3 = "K3"
    K4 = "K4"


@dataclass(frozen=True, slots=True)
class Catalog:
    """A numbered kind, as the dial declares it: the Markdown documents in its territory are
    its items."""

    prefix: str
    width: int
    territory: tuple[str, ...]

    def number_of(self, stem: str) -> int | None:
        """The number a file name carries, or None when the name has not the catalog's form."""
        found = _form(self.prefix, self.width).match(stem)
        return int(found.group(1)) if found else None

    def written(self, number: int) -> str:
        return f"{self.prefix}-{number:0{self.width}d}"


@cache
def _form(prefix: str, width: int) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(prefix)}-(\d{{{width}}})-{SLUG}$")


@dataclass(frozen=True, slots=True)
class Taken:
    """The numbers the other items of one catalog carry in the working tree, each with the
    file that carries it: what a file that does not exist yet is judged against."""

    catalog: Catalog
    holders: Mapping[int, str]
    in_history: int | None  # the highest number the branch's history ever added; advice only

    @property
    def next(self) -> int | None:
        """The number to name to a new item: one more than the highest the catalog has held, in
        the working tree or in history; None once the width cannot write it."""
        number = max(max(self.holders, default=0), self.in_history or 0) + 1
        return number if number < 10**self.catalog.width else None


@dataclass(frozen=True, slots=True)
class Reach:
    """How far a catalog's numbers go: in the working tree, and in history where it went further."""

    catalog: Catalog
    in_tree: int | None
    in_history: int | None


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
