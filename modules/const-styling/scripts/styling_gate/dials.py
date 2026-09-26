"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_TERRITORIES, Departure, Signature, StylingDials

KEYS = (
    "log_dir",
    "territories",
    "guides",
    "departures",
)  # the first is every gate's, read by the shared code
ENTRY_KEYS = ("paths", "allow", "reason")


def parse(own: Mapping[str, object]) -> StylingDials:
    unknown = sorted(str(key) for key in own if key not in KEYS)
    if unknown:
        raise ConfigurationFailure(messages.c5_unknown_key(unknown[0], KEYS))
    territories = _texts(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    for pattern in territories:
        if _unreadable(pattern):
            raise ConfigurationFailure(messages.c5_pattern("territories", pattern))
    raw_guides = own.get("guides", [])
    guides = _texts(raw_guides) if raw_guides != [] else ()
    if raw_guides != [] and not guides:
        raise ConfigurationFailure(messages.c5_guides())
    for pattern in guides:
        if _unreadable(pattern):
            raise ConfigurationFailure(messages.c5_pattern("guides", pattern))
    return StylingDials(
        territories=territories,
        guides=guides,
        departures=_departures(own.get("departures")),
    )


def _unreadable(pattern: str) -> bool:
    """A pattern git would read as a comment, or as two lines."""
    return pattern.startswith("#") or "\n" in pattern or "\r" in pattern


def _departures(value: object) -> tuple[Departure, ...]:
    """Absent or an empty list: no departure. Anything else is a list of well-formed entries, or a
    configuration failure naming the first bad one."""
    if value is None or value == []:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_departures())
    entries: list[Departure] = []
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ConfigurationFailure(messages.c5_departure(index, "it is not a mapping"))
        unknown = sorted(str(key) for key in item if key not in ENTRY_KEYS)
        if unknown:
            raise ConfigurationFailure(
                messages.c5_departure(index, f"'{unknown[0]}' is no field of an entry")
            )
        paths = _texts(item.get("paths"))
        if not paths:
            raise ConfigurationFailure(
                messages.c5_departure(index, "paths must be a non-empty list of path patterns")
            )
        for pattern in paths:
            if _unreadable(pattern):
                raise ConfigurationFailure(messages.c5_pattern(f"departures entry {index} paths", pattern))
        allow = _texts(item.get("allow"))
        if not allow:
            raise ConfigurationFailure(
                messages.c5_departure(index, "allow must be a non-empty list of signature keys")
            )
        known = {s.value for s in Signature}
        for key in allow:
            if key not in known:
                raise ConfigurationFailure(
                    messages.c5_departure(index, f"'{key}' is no signature this scan knows")
                )
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip() or any(c in reason.strip() for c in "\r\n"):
            raise ConfigurationFailure(
                messages.c5_departure(index, "reason must be one non-empty line saying why")
            )
        entries.append(Departure(paths, tuple(Signature(key) for key in allow), reason.strip()))
    return tuple(entries)


def _texts(value: object) -> tuple[str, ...]:
    """The non-empty strings of a list; empty when the value is no such list."""
    if not isinstance(value, list) or not all(isinstance(t, str) and t.strip() for t in value):
        return ()
    return tuple(str(t) for t in value)
