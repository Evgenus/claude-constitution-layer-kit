"""This module's own dials, parsed once from its namespace as the shared reader hands it over. The
month rule is a check of the dials alone: a ceiling at level error on a window shorter than the
rule's days is a configuration failure at every read, hook and scan alike — no clock is read."""

from __future__ import annotations

import datetime
import re
from collections.abc import Callable, Mapping

from constitution_layer_kit import identity
from constitution_layer_kit.dials import GATE_KEYS, refuse_unknown_keys, refuse_unreadable_patterns, texts
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.messages import echoed

from . import messages
from .model import WINDOW_DAYS, BudgetDials, Ceiling, Departure, Level, Window

KEYS = (*GATE_KEYS, "ceilings", "departures")
CEILING_KEYS = ("name", "paths", "max", "level", "window")
WINDOW_KEYS = ("from", "to")
DEPARTURE_KEYS = ("paths", "allow", "reason")
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def parse(own: Mapping[str, object]) -> BudgetDials:
    refuse_unknown_keys(own, KEYS)
    ceilings = _ceilings(own.get("ceilings"))
    return BudgetDials(ceilings, _departures(own.get("departures"), [c.name for c in ceilings]))


def _ceilings(value: object) -> tuple[Ceiling, ...]:
    """Absent or an empty list: no ceiling, and the gate measures nothing. Anything else is a list
    of well-formed entries, or a configuration failure naming the first bad one."""
    if value is None or value == []:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_ceilings())
    entries: list[Ceiling] = []
    for index, item in enumerate(value, 1):
        entries.append(_ceiling(index, item))
    names = [c.name for c in entries]
    for name in names:
        if names.count(name) > 1:
            raise ConfigurationFailure(messages.c5_duplicate_name(name))
    return tuple(entries)


def _ceiling(index: int, item: object) -> Ceiling:
    def bad(detail: str) -> ConfigurationFailure:
        return ConfigurationFailure(messages.c5_ceiling(index, detail))

    if not isinstance(item, dict):
        raise bad("it is not a mapping")
    unknown = sorted(str(key) for key in item if key not in CEILING_KEYS)
    if unknown:
        raise bad(f"'{echoed(unknown[0])}' is no field of an entry")
    name = item.get("name")
    if not isinstance(name, str) or not KEBAB.fullmatch(name):
        raise bad("name must be a kebab-case name, such as records")
    paths = texts(item.get("paths"))
    if not paths:
        raise bad("paths must be a non-empty list of path patterns")
    refuse_unreadable_patterns(f"{identity.current().namespace}.ceilings entry {index} paths", paths)
    most = item.get("max")
    if isinstance(most, bool) or not isinstance(most, int) or most < 1:
        raise bad("max must be a whole number of characters, 1 or more")
    level = item.get("level")
    if not isinstance(level, str) or level not in {lv.value for lv in Level}:
        raise bad("level must be warning or error")
    window = _window(item.get("window"), bad)
    ceiling = Ceiling(name, paths, most, Level(level), window)
    if ceiling.level is Level.ERROR and window.days < WINDOW_DAYS:
        raise ConfigurationFailure(messages.c5_window(name, window.days, window.start, window.end))
    return ceiling


def _window(value: object, bad: Callable[[str], ConfigurationFailure]) -> Window:
    if not isinstance(value, dict) or sorted(str(k) for k in value) != sorted(WINDOW_KEYS):
        raise bad("window must be a mapping of exactly from and to, each a date written YYYY-MM-DD")
    start, end = _date(value["from"]), _date(value["to"])
    if start is None or end is None:
        raise bad("window.from and window.to must each be a date written YYYY-MM-DD")
    if end < start:
        raise bad(f"window.to {end.isoformat()} is before window.from {start.isoformat()}")
    return Window(start, end)


def _date(value: object) -> datetime.date | None:
    """A date as YAML reads it unquoted — a date object — or quoted, as a string of the same form;
    a timestamp, a number or any other text is no date here."""
    if isinstance(value, datetime.datetime):
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and DATE.fullmatch(value):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _departures(value: object, names: list[str]) -> tuple[Departure, ...]:
    """Absent or an empty list: no departure. Anything else is a list of well-formed entries, or a
    configuration failure naming the first bad one."""
    if value is None or value == []:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_departures())
    entries: list[Departure] = []
    for index, item in enumerate(value, 1):

        def bad(detail: str, index: int = index) -> ConfigurationFailure:
            return ConfigurationFailure(messages.c5_departure(index, detail, names))

        if not isinstance(item, dict):
            raise bad("it is not a mapping")
        unknown = sorted(str(key) for key in item if key not in DEPARTURE_KEYS)
        if unknown:
            raise bad(f"'{echoed(unknown[0])}' is no field of an entry")
        paths = texts(item.get("paths"))
        if not paths:
            raise bad("paths must be a non-empty list of path patterns")
        refuse_unreadable_patterns(f"{identity.current().namespace}.departures entry {index} paths", paths)
        allow = texts(item.get("allow"))
        if not allow:
            raise bad("allow must be a non-empty list of ceiling names")
        for name in allow:
            if name not in names:
                raise bad(f"'{echoed(name)}' names no ceiling")
        reason = item.get("reason")
        if not _reason(reason):
            raise bad("reason must be one non-empty line saying why")
        entries.append(Departure(paths, allow, str(reason).strip()))
    return tuple(entries)


def _reason(value: object) -> bool:
    """A reason is one non-empty line; a line break at its end, which a YAML block scalar gives,
    is trimmed, one in the middle is refused."""
    if not isinstance(value, str):
        return False
    text = value.strip()
    return bool(text) and "\n" not in text and "\r" not in text
