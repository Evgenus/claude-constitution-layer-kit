"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import re
from collections.abc import Mapping

from constitution_layer_kit import identity
from constitution_layer_kit.dials import GATE_KEYS, refuse_unknown_keys, refuse_unreadable_patterns
from constitution_layer_kit.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_TERRITORIES, Lane, Mention, ReferencingDials, Switch

KEYS = {
    *GATE_KEYS,
    "territories",
    "governed_only",
    "heading_anchors",
    "bare_ids",
    "local_paths",
    "lanes",
    "mentions",
}
LANE_KEYS = {"pattern", "names", "fix", "home"}
MENTION_KEYS = {"pattern", "files"}


def parse(own: Mapping[str, object]) -> ReferencingDials:
    refuse_unknown_keys(own, sorted(KEYS))
    territories = _patterns(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    refuse_unreadable_patterns(f"{identity.current().namespace}.territories", territories)
    governed_only = own.get("governed_only", False)
    if not isinstance(governed_only, bool):
        raise ConfigurationFailure(messages.c5_governed_only())
    return ReferencingDials(
        territories,
        governed_only,
        _switch(own, "bare_ids"),
        _switch(own, "local_paths"),
        _switch(own, "heading_anchors"),
        _lanes(own.get("lanes")),
        _mentions(own.get("mentions")),
    )


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
    control = _control_character(texts["pattern"])
    if control is not None:
        raise refuse(messages.lane_pattern_control(control))
    try:
        pattern = re.compile(texts["pattern"])
    except re.error as error:
        raise refuse(messages.lane_pattern(str(error))) from error
    return Lane(pattern, texts["names"], texts["fix"], home)


def _mentions(value: object) -> tuple[Mention, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_mentions_not_a_list())
    return tuple(_mention(position, entry) for position, entry in enumerate(value, start=1))


def _mention(position: int, entry: object) -> Mention:
    def refuse(what: str) -> ConfigurationFailure:
        return ConfigurationFailure(messages.c5_mention(position, what))

    if not isinstance(entry, dict):
        raise refuse(messages.mention_not_a_mapping())
    unknown = sorted(str(key) for key in entry if key not in MENTION_KEYS)
    if unknown:
        raise refuse(messages.mention_unknown_key(unknown[0]))
    text = entry.get("pattern")
    if not isinstance(text, str) or not text.strip():
        raise refuse(messages.lane_needs("pattern"))
    files = _patterns(entry.get("files", []))
    if files is None:
        raise refuse(messages.mention_files())
    refuse_unreadable_patterns(f"{identity.current().namespace}.mentions[{position}].files", files)
    control = _control_character(text)
    if control is not None:
        raise refuse(messages.lane_pattern_control(control))
    try:
        return Mention(re.compile(text), files)
    except re.error as error:
        raise refuse(messages.lane_pattern(str(error))) from error


def _control_character(pattern: str) -> str | None:
    """The first control character of a pattern, or None. YAML's double quotes turn `\\b` into a
    backspace: the pattern then compiles, matches nothing and passes in silence, so it is refused
    before it is compiled."""
    return next((c for c in pattern if ord(c) < 0x20 or ord(c) == 0x7F), None)


def _patterns(value: object) -> tuple[str, ...] | None:
    """None when the value is no list of non-empty strings; an empty list is the caller's to judge."""
    if not isinstance(value, list):
        return None
    if not all(isinstance(pattern, str) and pattern.strip() for pattern in value):
        return None
    return tuple(str(pattern) for pattern in value)
