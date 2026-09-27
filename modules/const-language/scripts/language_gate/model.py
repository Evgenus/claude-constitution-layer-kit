"""This module's own structures: its dials, the rules the gate knows and their levels, a hit
Vale reported or the preparation found, and the keys of its findings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

DEFAULT_TERRITORIES = ("*.md",)
DEFAULT_GRADE_CEILING = 10.0  # Flesch–Kincaid grade; a document above it is a finding
DEFAULT_SENTENCE_WORDS = 25  # words per sentence; a sentence over it is a finding
VALE_FLOOR = (3, 23, 0)  # scoped metric rules need 3.21.0, the built-in scores 3.23.0
STYLE = "Language"  # the generated Vale style; every rule is Language.<Rule>


class Rule(StrEnum):
    """The closed set of rules the gate generates for Vale, keyed as the dial `levels` names them."""

    GRADE = "grade"  # the document's Flesch–Kincaid grade against the ceiling
    SENTENCE = "sentence"  # words per sentence against the limit
    FORBIDDEN = "forbidden"  # idioms and formal phrases with no plain word
    SIMPLER = "simpler"  # words and phrases that have a plain word
    PASSIVE = "passive"  # a form of "be" followed by a past participle


class Level(StrEnum):
    """What a rule's hit is: a finding, a note, or nothing."""

    ERROR = "error"
    WARNING = "warning"
    OFF = "off"


DEFAULT_LEVELS: dict[Rule, Level] = {
    Rule.GRADE: Level.ERROR,
    Rule.SENTENCE: Level.ERROR,
    Rule.FORBIDDEN: Level.ERROR,
    Rule.SIMPLER: Level.ERROR,
    Rule.PASSIVE: Level.WARNING,  # on most prose a register, not a defect: reported, never red by default
}

VALE_RULE_NAME: dict[Rule, str] = {
    Rule.GRADE: "Grade",
    Rule.SENTENCE: "Sentence",
    Rule.FORBIDDEN: "Forbidden",
    Rule.SIMPLER: "Simpler",
    Rule.PASSIVE: "Passive",
}


class Key(StrEnum):
    """Stable handles of this module's findings."""

    L1 = "L1"  # the grade ceiling
    L2 = "L2"  # the sentence limit
    L3 = "L3"  # a forbidden construction
    L4 = "L4"  # a word with a plain replacement
    L5 = "L5"  # passive voice
    L6 = "L6"  # a Vale comment in the document


KEY_OF: dict[Rule, Key] = {
    Rule.GRADE: Key.L1,
    Rule.SENTENCE: Key.L2,
    Rule.FORBIDDEN: Key.L3,
    Rule.SIMPLER: Key.L4,
    Rule.PASSIVE: Key.L5,
}


@dataclass(frozen=True, slots=True)
class LanguageDials:
    territories: tuple[str, ...]
    grade_ceiling: float
    sentence_words: int
    levels: dict[Rule, Level]
    forbidden: tuple[str, ...]  # the founding list plus the repository's, the exceptions removed
    simpler: dict[str, str]  # observed -> plain, likewise
    exceptions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Hit:
    """One thing Vale reported in a document: the rule, the line, the column where it starts, the
    matched text, and the rule's message — a number for the two metric rules, the plain word for the
    substitution, the match itself for the rest."""

    rule: Rule
    line: int
    column: int
    match: str
    message: str


@dataclass(frozen=True, slots=True)
class Prepared:
    """A document as Vale reads it: the envelope and every Vale comment blanked, line numbers kept;
    and where the comments were, each a finding of its own."""

    text: str
    comments: tuple[tuple[int, str], ...]  # (line, the comment's text)


@dataclass(frozen=True, slots=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def at_least(self, floor: tuple[int, int, int]) -> bool:
        return (self.major, self.minor, self.patch) >= floor
