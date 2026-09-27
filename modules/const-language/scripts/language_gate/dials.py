"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import math
from collections.abc import Mapping

from const_gate.errors import ConfigurationFailure

from . import messages, rules
from .model import (
    DEFAULT_GRADE_CEILING,
    DEFAULT_LEVELS,
    DEFAULT_SENTENCE_WORDS,
    DEFAULT_TERRITORIES,
    LanguageDials,
    Level,
    Rule,
)

KEYS = (
    "severity",
    "log_dir",
    "territories",
    "grade_ceiling",
    "sentence_words",
    "levels",
    "forbidden",
    "simpler",
    "exceptions",
)  # the first two are every gate's, read by the shared code


def parse(own: Mapping[str, object]) -> LanguageDials:
    unknown = sorted(str(key) for key in own if key not in KEYS)
    if unknown:
        raise ConfigurationFailure(messages.c5_unknown_key(unknown[0], KEYS))
    territories = _texts(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    for pattern in territories:
        if pattern.startswith("#") or "\n" in pattern or "\r" in pattern:
            raise ConfigurationFailure(messages.c5_pattern(pattern))
    grade = own.get("grade_ceiling", DEFAULT_GRADE_CEILING)
    if isinstance(grade, bool) or not isinstance(grade, int | float) or not math.isfinite(grade) or grade < 0:
        raise ConfigurationFailure(messages.c5_grade_ceiling())
    words = own.get("sentence_words", DEFAULT_SENTENCE_WORDS)
    if isinstance(words, bool) or not isinstance(words, int) or words < 1:
        raise ConfigurationFailure(messages.c5_sentence_words())
    levels = _levels(own.get("levels"))
    forbidden_extra = _phrases_or_none(own.get("forbidden"), "forbidden")
    simpler_extra = _simpler(own.get("simpler"))
    exceptions = _phrases_or_none(own.get("exceptions"), "exceptions")
    forbidden = [*rules.FORBIDDEN, *(p for p in forbidden_extra if p not in rules.FORBIDDEN)]
    simpler = {**rules.SIMPLER, **simpler_extra}
    lowered = tuple(
        phrase.lower() for phrase in exceptions
    )  # the lists match case-insensitively; so do exceptions
    for phrase in exceptions:
        if phrase.lower() not in forbidden and phrase.lower() not in simpler:
            raise ConfigurationFailure(messages.c5_exception(phrase))
    return LanguageDials(
        territories=territories,
        grade_ceiling=float(grade),
        sentence_words=words,
        levels=levels,
        forbidden=tuple(p for p in forbidden if p.lower() not in lowered),
        simpler={k: v for k, v in simpler.items() if k.lower() not in lowered},
        exceptions=exceptions,
    )


def _levels(value: object) -> dict[Rule, Level]:
    levels = dict(DEFAULT_LEVELS)
    if value is None:
        return levels
    if not isinstance(value, dict):
        raise ConfigurationFailure(messages.c5_levels())
    known = {r.value for r in Rule}
    for raw_rule, raw_level in value.items():
        rule = str(raw_rule)
        if rule not in known:
            raise ConfigurationFailure(
                messages.c5_unknown_key(f"levels.{rule}", [f"levels.{r.value}" for r in Rule])
            )
        if raw_level is False:  # a bare `off` is a boolean to YAML: read as the level it was written as
            raw_level = Level.OFF.value
        if not isinstance(raw_level, str) or raw_level not in {lv.value for lv in Level}:
            raise ConfigurationFailure(messages.c5_level(rule, str(raw_level)))
        levels[Rule(rule)] = Level(raw_level)
    if all(level is Level.OFF for level in levels.values()):
        raise ConfigurationFailure(messages.c5_all_off())
    return levels


def _phrases(value: object) -> tuple[str, ...]:
    """The non-empty one-line strings of a list; empty when the value is no such list."""
    if not isinstance(value, list) or not all(_one_line(t) for t in value):
        return ()
    return tuple(str(t).strip() for t in value)


def _phrases_or_none(value: object, key: str) -> tuple[str, ...]:
    if value is None or value == []:
        return ()
    phrases = _phrases(value)
    if not phrases:
        raise ConfigurationFailure(messages.c5_phrases(key))
    return phrases


def _simpler(value: object) -> dict[str, str]:
    if value is None or value == {}:
        return {}
    if not isinstance(value, dict) or not all(_one_line(k) and _one_line(v) for k, v in value.items()):
        raise ConfigurationFailure(messages.c5_simpler())
    return {str(k).strip(): str(v).strip() for k, v in value.items()}


def _texts(value: object) -> tuple[str, ...]:
    """The non-empty strings of a list, line breaks included; empty when the value is no such list."""
    if not isinstance(value, list) or not all(isinstance(t, str) and t.strip() for t in value):
        return ()
    return tuple(str(t) for t in value)


def _one_line(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and "\n" not in value and "\r" not in value
