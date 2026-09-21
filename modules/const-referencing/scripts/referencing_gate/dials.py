"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import re
from collections.abc import Mapping

from const_gate import identity
from const_gate.dials import refuse_unreadable_patterns
from const_gate.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_TERRITORIES, Lane, ReferencingDials, Switch

LANE_KEYS = {"pattern", "names", "fix", "home"}


def parse(own: Mapping[str, object]) -> ReferencingDials:
    territories = _patterns(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    refuse_unreadable_patterns(f"{identity.current().namespace}.territories", territories)
    return ReferencingDials(territories, _switch(own, "bare_ids"), _lanes(own.get("lanes")))


def _switch(own: Mapping[str, object], dial: str) -> Switch:
    value = own.get(dial, Switch.REFUSE.value)
    if not isinstance(value, str) or value not in {s.value for s in Switch}:
        raise ConfigurationFailure(messages.c5_switch(dial))
    return Switch(value)


def _lanes(value: object) -> tuple[Lane, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_lanes_not_a_list())
    return tuple(_lane(position, entry) for position, entry in enumerate(value, start=1))


def _lane(position: int, entry: object) -> Lane:
    def refuse(what: str) -> ConfigurationFailure:
        return ConfigurationFailure(messages.c5_lane(position, what))

    if not isinstance(entry, dict):
        raise refuse(messages.lane_not_a_mapping())
    unknown = sorted(str(key) for key in entry if key not in LANE_KEYS)
    if unknown:
        raise refuse(messages.lane_unknown_key(unknown[0]))
    texts: dict[str, str] = {}
    for field in ("pattern", "names", "fix"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            raise refuse(messages.lane_needs(field))
        texts[field] = value
    home = _patterns(entry.get("home", []))
    if home is None:
        raise refuse(messages.lane_home())
    refuse_unreadable_patterns(f"{identity.current().namespace}.lanes[{position}].home", home)
    try:
        pattern = re.compile(texts["pattern"])
    except re.error as error:
        raise refuse(messages.lane_pattern(str(error))) from error
    return Lane(pattern, texts["names"], texts["fix"], home)


def _patterns(value: object) -> tuple[str, ...] | None:
    """None when the value is no list of non-empty strings; an empty list is the caller's to judge."""
    if not isinstance(value, list):
        return None
    if not all(isinstance(pattern, str) and pattern.strip() for pattern in value):
        return None
    return tuple(str(pattern) for pattern in value)
