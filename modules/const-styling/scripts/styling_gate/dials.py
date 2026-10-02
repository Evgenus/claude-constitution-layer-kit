"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate import identity
from const_gate.dials import refuse_unknown_keys, refuse_unreadable_patterns
from const_gate.errors import ConfigurationFailure
from const_gate.messages import echoed

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
    refuse_unknown_keys(own, KEYS)
    namespace = identity.current().namespace
    territories = _texts(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    refuse_unreadable_patterns(f"{namespace}.territories", territories)
    raw_guides = own.get("guides", [])
    guides = _texts(raw_guides) if raw_guides != [] else ()
    if raw_guides != [] and not guides:
        raise ConfigurationFailure(messages.c5_guides())
    refuse_unreadable_patterns(f"{namespace}.guides", guides)
    return StylingDials(
        territories=territories,
        guides=guides,
        departures=_departures(own.get("departures")),
    )


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
                messages.c5_departure(index, f"'{echoed(unknown[0])}' is no field of an entry")
            )
        paths = _texts(item.get("paths"))
        if not paths:
            raise ConfigurationFailure(
                messages.c5_departure(index, "paths must be a non-empty list of path patterns")
            )
        refuse_unreadable_patterns(f"{identity.current().namespace}.departures entry {index} paths", paths)
        allow = _texts(item.get("allow"))
        if not allow:
            raise ConfigurationFailure(
                messages.c5_departure(index, "allow must be a non-empty list of signature keys")
            )
        known = {s.value for s in Signature}
        for key in allow:
            if key not in known:
                raise ConfigurationFailure(
                    messages.c5_departure(index, f"'{echoed(key)}' is no signature this scan knows")
                )
        reason = item.get("reason")
        if not _reason(reason):
            raise ConfigurationFailure(
                messages.c5_departure(index, "reason must be one non-empty line saying why")
            )
        entries.append(Departure(paths, tuple(Signature(key) for key in allow), str(reason).strip()))
    return tuple(entries)


def _texts(value: object) -> tuple[str, ...]:
    """The non-empty strings of a list; empty when the value is no such list."""
    if not isinstance(value, list) or not all(isinstance(t, str) and t.strip() for t in value):
        return ()
    return tuple(str(t) for t in value)


def _reason(value: object) -> bool:
    """A reason is one non-empty line; a line break at its end, which a YAML block scalar gives,
    is trimmed, one in the middle is refused."""
    if not isinstance(value, str):
        return False
    text = value.strip()
    return bool(text) and "\n" not in text and "\r" not in text
