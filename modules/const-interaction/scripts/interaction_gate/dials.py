"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import re
from collections.abc import Mapping

from const_gate import identity
from const_gate.dials import GATE_KEYS, refuse_unknown_keys, refuse_unreadable_patterns, texts
from const_gate.errors import ConfigurationFailure
from const_gate.messages import echoed

from . import messages, tokens
from .model import (
    DEFAULT_DESTRUCTIVE,
    DEFAULT_HANDLES,
    DEFAULT_READER_LISTS,
    DEFAULT_TERRITORIES,
    Entry,
    InteractionDials,
    Pair,
    Verbosity,
)

KEYS = (
    *GATE_KEYS,
    "destructive",
    "territories",
    "handles",
    "boundary_examples",
    "verbosity",
)
ENTRY_KEYS = ("command", "flags", "teach", "alternative")
PAIR_KEYS = ("violates", "complies")


def parse(own: Mapping[str, object]) -> InteractionDials:
    refuse_unknown_keys(own, KEYS)
    territories = texts(own.get("territories", list(DEFAULT_TERRITORIES)))
    if not territories:
        raise ConfigurationFailure(messages.c5_territories())
    refuse_unreadable_patterns(f"{identity.current().namespace}.territories", territories)
    handles = texts(own.get("handles", list(DEFAULT_HANDLES)))
    if not handles:
        raise ConfigurationFailure(messages.c5_handles())
    for handle in handles:
        try:
            re.compile(handle)
        except re.error as exc:
            raise ConfigurationFailure(messages.c5_handle_pattern(handle, str(exc))) from exc
    return InteractionDials(
        destructive=_entries(own.get("destructive")),
        territories=territories,
        handles=handles,
        boundary_examples=_pairs(own.get("boundary_examples")),
        verbosity=_verbosity(own.get("verbosity")),
    )


def _entries(value: object) -> tuple[Entry, ...]:
    """Absent: the defaults. An empty list: nothing is gated, said at session start. Anything else
    is a list of well-formed entries, or a configuration failure naming the first bad one."""
    if value is None:
        return DEFAULT_DESTRUCTIVE
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_destructive())
    entries: list[Entry] = []
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ConfigurationFailure(messages.c5_entry(index, "it is not a mapping"))
        unknown = sorted(str(key) for key in item if key not in ENTRY_KEYS)
        if unknown:
            raise ConfigurationFailure(
                messages.c5_entry(index, f"'{echoed(unknown[0])}' is no field of an entry")
            )
        command = texts(item.get("command"))
        if not command or any(" " in word for word in command):
            raise ConfigurationFailure(messages.c5_entry(index, "command must be a non-empty list of words"))
        read = tokens.reading(command, DEFAULT_READER_LISTS)
        if read != list(command):
            raise ConfigurationFailure(messages.c5_entry_unread(index, command, read))
        raw_flags = item.get("flags", [])
        flags = texts(raw_flags) if raw_flags != [] else ()
        if raw_flags != [] and (not flags or any(not flag.startswith("-") or " " in flag for flag in flags)):
            raise ConfigurationFailure(
                messages.c5_entry(index, "flags must be a list of flags, each starting with '-'")
            )
        teach, alternative = item.get("teach"), item.get("alternative")
        if not isinstance(teach, str) or not teach.strip():
            raise ConfigurationFailure(messages.c5_entry(index, "teach must be a non-empty text"))
        if not isinstance(alternative, str) or not alternative.strip():
            raise ConfigurationFailure(messages.c5_entry(index, "alternative must be a non-empty text"))
        entries.append(Entry(command, flags, teach.strip(), alternative.strip()))
    return tuple(entries)


def _verbosity(value: object) -> Verbosity:
    if value is None:
        return Verbosity.TRIGGERED
    if not isinstance(value, str) or value not in {v.value for v in Verbosity}:
        raise ConfigurationFailure(messages.c5_verbosity())
    return Verbosity(value)


def _pairs(value: object) -> tuple[Pair, ...]:
    if value is None or value == []:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_boundary_examples())
    pairs: list[Pair] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != set(PAIR_KEYS):
            raise ConfigurationFailure(messages.c5_boundary_examples())
        violates, complies = item["violates"], item["complies"]
        if not isinstance(violates, str) or not isinstance(complies, str):
            raise ConfigurationFailure(messages.c5_boundary_examples())
        pairs.append(Pair(violates.strip(), complies.strip()))
    return tuple(pairs)
