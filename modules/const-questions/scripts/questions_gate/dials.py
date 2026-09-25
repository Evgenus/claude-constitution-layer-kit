"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate import identity
from const_gate.dials import refuse_unreadable_patterns
from const_gate.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_MARKERS, DEFAULT_TERRITORIES, QuestionsDials

KEYS = (
    "severity",
    "log_dir",
    "territories",
    "markers",
    "preferences",
    "boundary_examples",
)  # the first two are every gate's, read by the shared code; the last two are the skill's, refused
# by name only and read by nobody here


def parse(own: Mapping[str, object]) -> QuestionsDials:
    unknown = sorted(str(key) for key in own if key not in KEYS)
    if unknown:
        raise ConfigurationFailure(messages.c5_unknown_key(unknown[0], KEYS))
    territories = _texts(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    refuse_unreadable_patterns(f"{identity.current().namespace}.territories", territories)
    markers = _texts(own.get("markers", list(DEFAULT_MARKERS)))
    if not markers or any("\n" in marker or "\r" in marker for marker in markers):
        raise ConfigurationFailure(messages.c5_markers())  # a marker with a line break could never match
    return QuestionsDials(territories, markers)


def _texts(value: object) -> tuple[str, ...]:
    """The non-empty strings of a list; empty when the value is no such list."""
    if not isinstance(value, list) or not all(isinstance(t, str) and t.strip() for t in value):
        return ()
    return tuple(str(t) for t in value)
