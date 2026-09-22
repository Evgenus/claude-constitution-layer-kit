"""This module's own structures: its dials, a lane, a link, the keys of its findings."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

DEFAULT_TERRITORIES = ("*.md",)


class Key(StrEnum):
    """Stable handles of this module's findings."""

    R1 = "R1"  # a project's bare form, declared as a lane
    R2 = "R2"  # a governed id in backticks that is no link
    R3 = "R3"  # a link whose text is a governed id and whose target is another file
    R4 = "R4"  # a path on one machine
    R5 = "R5"  # a link whose target does not exist
    R6 = "R6"  # a link whose target carries no such anchor
    R7 = "R7"  # a link that resolves only through a heading's generated name
    R8 = "R8"  # outside Markdown, a name of the form of an id that no covered document carries


class ToolKey(StrEnum):
    """Stable handles of this module's own configuration failures: the link checker."""

    X1 = "X1"  # not installed
    X2 = "X2"  # below the floor
    X3 = "X3"  # gave no report


class ActKey(StrEnum):
    """The mover's refusals, under one key: each changes nothing."""

    V5 = "V5"


class Switch(StrEnum):
    """A check that a project may switch off."""

    REFUSE = "refuse"
    ALLOW = "allow"


@dataclass(frozen=True, slots=True)
class Lane:
    """A bare form of the project's own: how it looks, what it cites, what to write instead,
    and the documents where it is the local alias."""

    pattern: re.Pattern[str]
    names: str
    fix: str
    home: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Mention:
    """How a document's id looks where it is named outside Markdown, and in which files."""

    pattern: re.Pattern[str]
    files: tuple[str, ...]  # empty: every file git lists that is no Markdown


@dataclass(frozen=True, slots=True)
class ReferencingDials:
    territories: tuple[str, ...]
    governed_only: bool
    bare_ids: Switch
    local_paths: Switch
    heading_anchors: Switch
    lanes: tuple[Lane, ...]
    mentions: tuple[Mention, ...]


class LinkKind(StrEnum):
    INLINE = "inline"  # [text](destination), an image included
    DEFINITION = "definition"  # [label]: destination
    HREF = "href"  # <a href="destination">
    USAGE = "usage"  # [text][label], opening what the definition of the label names; nothing to rewrite


@dataclass(frozen=True, slots=True)
class Link:
    """One link of a document. `start` and `end` bound the whole link in the text, `at` and
    `until` its destination alone — what a repair rewrites."""

    kind: LinkKind
    text: str
    destination: str
    start: int
    end: int
    at: int
    until: int


@dataclass(frozen=True, slots=True)
class Ids:
    """The ids the covered documents carry, each with the paths of the documents carrying it —
    one, unless the repository is wrong in a way another gate reports."""

    owners: dict[str, tuple[str, ...]]

    def owners_of(self, doc_id: str) -> tuple[str, ...]:
        return self.owners.get(doc_id, ())
