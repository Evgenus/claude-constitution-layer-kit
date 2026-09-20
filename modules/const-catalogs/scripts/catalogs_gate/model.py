"""This module's own structures: a declared catalog, its dials, an item, the keys of its findings."""

from __future__ import annotations

import re
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
