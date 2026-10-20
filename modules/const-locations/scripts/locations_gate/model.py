"""The closed vocabularies and the structures that cross function boundaries in this module."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from constitution_layer_kit.model import MetaType


class ActKey(StrEnum):
    """The stable handle of the generator's refusals (the lines L1–L4 are plain text)."""

    L5 = "L5"


class HomeClass(StrEnum):
    """The shapes of territory a home follows from, and the two it does not."""

    DIRECTORY = "directory"  # <dir>/** or <dir>/**/*.md: the home is <dir>/<stem>.md
    SEGMENT = "segment"  # <dir>/*/NAME.md: one free segment, the file name fixed
    SINGLE = "single"  # one path, no glob: nothing new is born there
    NONE = "none"  # anything else: no home follows


@dataclass(frozen=True, slots=True)
class HomeRule:
    """What one policy's territory says about where a new document goes."""

    kind: HomeClass
    pattern: str  # the deciding pattern as declared (the single one, for the three named classes)
    directory: str = ""  # DIRECTORY: the prefix, without a trailing slash
    fixed_name: str = ""  # SEGMENT: the file name the pattern fixes, without .md
    before: str = ""  # SEGMENT: the path before the free segment
    after: str = ""  # SEGMENT: the path after it, the file name included


@dataclass(frozen=True, slots=True)
class LocationsDials:
    """This module's own dials, parsed once."""

    templates: Mapping[str, str]  # policy id -> repository-relative template path


@dataclass(frozen=True, slots=True)
class Request:
    """What the command line asked for."""

    kind: str
    stem: str | None
    title: str | None
    meta_type: MetaType | None
    segment: str | None
    doc_id: str | None
    dry_run: bool


@dataclass(frozen=True, slots=True)
class Plan:
    """Everything proven before the write: where the document goes and what it will hold."""

    home: str
    pattern: str
    template: str | None  # the template's path, or None for the envelope alone
    text: str
