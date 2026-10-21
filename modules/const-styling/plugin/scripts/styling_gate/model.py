"""This module's own structures: its dials, the signatures the scan knows, a hit in a document,
and the keys of its findings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

DEFAULT_TERRITORIES = ("*.md",)


class Signature(StrEnum):
    """The closed set of traces the scan knows — each the mechanical half of one default of the
    style guide; the dial `departures` names them by these keys."""

    PLANTUML = "plantuml"  # a plantuml or puml fence, or a line opening with @startuml
    FORMULA = "formula"  # a math, latex or tex fence, or a line opening with $$
    CALLOUT = "callout"  # a blockquote line opening with [!, the alert syntax
    DEEP_HEADING = "deep-heading"  # a heading of level four or deeper
    SKIPPED_LEVEL = "skipped-level"  # a heading more than one level below the heading before it
    SECOND_H1 = "second-h1"  # a second heading of level one
    FENCE_LANGUAGE = "fence-language"  # a fence that names no language
    LIST_MARKER = "list-marker"  # a bullet item opening with * or +
    LIST_NUMBERING = "list-numbering"  # an ordered item whose number is not the one before it plus one
    UNDERSCORE_EMPHASIS = "underscore-emphasis"  # emphasis by _ or __
    TABLE_COLUMNS = "table-columns"  # a table row with more or fewer cells than its header
    TABLE_EMPTY_CELL = "table-empty-cell"  # a table cell that holds nothing


class Key(StrEnum):
    """Stable handles of this module's findings, one per signature."""

    Y1 = "Y1"  # plantuml
    Y2 = "Y2"  # formula
    Y3 = "Y3"  # callout
    Y4 = "Y4"  # deep-heading
    Y5 = "Y5"  # skipped-level
    Y6 = "Y6"  # second-h1
    Y7 = "Y7"  # fence-language
    Y8 = "Y8"  # list-marker
    Y9 = "Y9"  # list-numbering
    Y10 = "Y10"  # underscore-emphasis
    Y11 = "Y11"  # table-columns
    Y12 = "Y12"  # table-empty-cell


KEY_OF: dict[Signature, Key] = {
    Signature.PLANTUML: Key.Y1,
    Signature.FORMULA: Key.Y2,
    Signature.CALLOUT: Key.Y3,
    Signature.DEEP_HEADING: Key.Y4,
    Signature.SKIPPED_LEVEL: Key.Y5,
    Signature.SECOND_H1: Key.Y6,
    Signature.FENCE_LANGUAGE: Key.Y7,
    Signature.LIST_MARKER: Key.Y8,
    Signature.LIST_NUMBERING: Key.Y9,
    Signature.UNDERSCORE_EMPHASIS: Key.Y10,
    Signature.TABLE_COLUMNS: Key.Y11,
    Signature.TABLE_EMPTY_CELL: Key.Y12,
}


@dataclass(frozen=True, slots=True)
class Departure:
    """One entry of the departures dial: the documents it covers, as path patterns; the
    signatures it allows there; and the one-line reason."""

    paths: tuple[str, ...]
    allow: tuple[Signature, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class StylingDials:
    territories: tuple[str, ...]
    guides: tuple[str, ...]
    departures: tuple[Departure, ...]


@dataclass(frozen=True, slots=True)
class Hit:
    """One trace of a signature in a document: which, where, and the text the finding echoes —
    the line's own words, or what the check measured."""

    signature: Signature
    line: int
    text: str
