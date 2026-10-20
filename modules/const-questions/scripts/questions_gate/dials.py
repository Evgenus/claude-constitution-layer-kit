"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

from collections.abc import Mapping

from constitution_layer_kit import identity
from constitution_layer_kit.dials import GATE_KEYS, refuse_unknown_keys, refuse_unreadable_patterns, texts
from constitution_layer_kit.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_MARKERS, DEFAULT_TERRITORIES, QuestionsDials

KEYS = (
    *GATE_KEYS,
    "territories",
    "markers",
    "preferences",
    "boundary_examples",
)  # the last two are the skill's, refused by name only and read by nobody here


def parse(own: Mapping[str, object]) -> QuestionsDials:
    refuse_unknown_keys(own, KEYS)
    territories = texts(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    refuse_unreadable_patterns(f"{identity.current().namespace}.territories", territories)
    markers = texts(own.get("markers", list(DEFAULT_MARKERS)))
    if not markers or any("\n" in marker or "\r" in marker for marker in markers):
        raise ConfigurationFailure(messages.c5_markers())  # a marker with a line break could never match
    return QuestionsDials(territories, markers)
