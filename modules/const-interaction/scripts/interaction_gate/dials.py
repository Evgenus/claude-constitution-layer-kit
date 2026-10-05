"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from const_gate import identity
from const_gate.dials import GATE_KEYS, refuse_unknown_keys, refuse_unreadable_patterns, texts
from const_gate.errors import ConfigurationFailure
from const_gate.messages import echoed

from . import messages, tokens
from .model import (
    DEFAULT_DESTRUCTIVE,
    DEFAULT_HANDLES,
    DEFAULT_SHELLS,
    DEFAULT_TERRITORIES,
    DEFAULT_WRAPPERS,
    Dropped,
    Entry,
    InteractionDials,
    OptionFault,
    Pair,
    ReaderLists,
    Shell,
    Verbosity,
    Wrapper,
)

KEYS = (
    *GATE_KEYS,
    "destructive",
    "wrappers",
    "shells",
    "territories",
    "handles",
    "boundary_examples",
    "verbosity",
)
ENTRY_KEYS = ("command", "flags", "teach", "alternative")
PAIR_KEYS = ("violates", "complies")
WRAPPER_FIELDS = ("command", "with_value", "positionals", "numbers", "command_flags", "drop")
SHELL_FIELDS = ("command", "with_value", "command_flags", "drop")
# The signs an option of each starts with: the reader takes a wrapper's options as the words that start
# with `-`, a shell's as those that start with `-` or `+`.
OPTION_SIGNS = {"wrappers": "-", "shells": "-+"}


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
    reader, dropped = _reader_lists(own)  # first: an entry of `destructive` is read through these lists
    return InteractionDials(
        destructive=_entries(own.get("destructive"), reader),
        territories=territories,
        handles=handles,
        boundary_examples=_pairs(own.get("boundary_examples")),
        verbosity=_verbosity(own.get("verbosity")),
        reader=reader,
        dropped=dropped,
    )


def _reader_lists(own: Mapping[str, object]) -> tuple[ReaderLists, tuple[Dropped, ...]]:
    """The wrappers and the shells of the reader: the defaults, each list the dials give applied to them
    by command, and the defaults dropped. A word is a wrapper or a shell, never both."""
    listed, dropped_wrappers = _merged("wrappers", own.get("wrappers"), WRAPPER_FIELDS, DEFAULT_WRAPPERS)
    wrappers = tuple(entry for entry in listed if isinstance(entry, Wrapper))
    listed, dropped_shells = _merged("shells", own.get("shells"), SHELL_FIELDS, DEFAULT_SHELLS)
    shells = tuple(entry for entry in listed if isinstance(entry, Shell))
    wrapper_commands = {wrapper.command for wrapper in wrappers}
    for shell in shells:
        if (shell.command,) in wrapper_commands:
            raise ConfigurationFailure(messages.c5_reader_both(shell.command))
    return ReaderLists(wrappers, shells), (*dropped_wrappers, *dropped_shells)


def _words_of(entry: Wrapper | Shell) -> tuple[str, ...]:
    return (entry.command,) if isinstance(entry, Shell) else entry.command


def _merged(
    dial: str, value: object, fields: tuple[str, ...], defaults: Sequence[Wrapper | Shell]
) -> tuple[list[Wrapper | Shell], tuple[Dropped, ...]]:
    """Absent: the defaults. A list: each entry applied to the defaults by its command — one of a
    default's command replaces that default whole, a new command is added, `drop: true` removes the
    default — or a configuration failure naming the first bad entry. An empty list leaves the defaults."""
    merged = list(defaults)
    if value is None:
        return merged, ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_reader_list(dial))
    dropped: list[Dropped] = []
    seen: dict[tuple[str, ...], int] = {}
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ConfigurationFailure(messages.c5_reader_entry(dial, index, "it is not a mapping"))
        unknown = sorted(str(key) for key in item if key not in fields)
        if unknown:
            raise ConfigurationFailure(messages.c5_reader_unknown(dial, index, unknown[0]))
        command = _reader_command(dial, index, item)
        if command in seen:
            raise ConfigurationFailure(messages.c5_reader_twice(dial, index, command, seen[command]))
        seen[command] = index
        if "drop" in item:
            if item["drop"] is not True:
                raise ConfigurationFailure(messages.c5_reader_drop_value(dial, index))
            beside = sorted(str(key) for key in item if key not in ("command", "drop"))
            if beside:
                raise ConfigurationFailure(messages.c5_reader_drop_beside(dial, index, beside[0]))
            if not any(_words_of(default) == command for default in defaults):
                names = [" ".join(_words_of(default)) for default in defaults]
                raise ConfigurationFailure(messages.c5_reader_drop_unknown(dial, index, command, names))
            dropped.append(Dropped(dial, command))
            merged = [entry for entry in merged if _words_of(entry) != command]
            continue
        built: Wrapper | Shell = (
            _wrapper(dial, index, item, command) if dial == "wrappers" else _shell(dial, index, item, command)
        )
        place = next((at for at, entry in enumerate(merged) if _words_of(entry) == command), None)
        if place is None:
            merged.append(built)
        else:
            merged[place] = built
    return merged, tuple(dropped)


def _reader_command(dial: str, index: int, item: dict[str, object]) -> tuple[str, ...]:
    """The words of an entry's `command`: a non-empty list, no word empty, holding white space or a
    `/` — a program is read by its base name, so such a word can never match — and for a shell one word."""
    command = texts(item.get("command"))
    if not command or any("/" in word or any(letter.isspace() for letter in word) for word in command):
        raise ConfigurationFailure(messages.c5_reader_command(dial, index))
    if dial == "shells" and len(command) != 1:
        raise ConfigurationFailure(messages.c5_reader_shell_words(index, command))
    return command


def _wrapper(dial: str, index: int, item: dict[str, object], command: tuple[str, ...]) -> Wrapper:
    return Wrapper(
        command,
        with_value=_options(dial, index, item, "with_value"),
        positionals=_count(dial, index, item, "positionals"),
        numbers=_count(dial, index, item, "numbers"),
        command_flags=_options(dial, index, item, "command_flags"),
    )


def _shell(dial: str, index: int, item: dict[str, object], command: tuple[str, ...]) -> Shell:
    return Shell(
        command[0],
        with_value=_options(dial, index, item, "with_value"),
        command_flags=_options(dial, index, item, "command_flags"),
    )


def _options(dial: str, index: int, item: dict[str, object], field: str) -> tuple[str, ...]:
    """The options of a field, each one the reader could match, or a configuration failure naming the
    first that it could not. Absent or an empty list: none."""
    raw = item.get(field, [])
    if raw == []:
        return ()
    options = texts(raw)
    if not options:
        raise ConfigurationFailure(messages.c5_reader_option(dial, index, field, "", OptionFault.NOT_A_LIST))
    for option in options:
        fault = _option_fault(dial, option)
        if fault is not None:
            raise ConfigurationFailure(messages.c5_reader_option(dial, index, field, option, fault))
    return options


def _option_fault(dial: str, option: str) -> OptionFault | None:
    """Why the reader could never match this option, or None: it reads the words that start with the
    dial's signs, a long option by its name before any `=`, a short one a letter at a time."""
    if any(letter.isspace() for letter in option):
        return OptionFault.WHITE_SPACE
    if option[0] not in OPTION_SIGNS[dial]:
        return OptionFault.NO_SIGN
    if not option.lstrip("-+"):
        return OptionFault.LONE_SIGN
    if option.startswith("--"):
        return OptionFault.EQUALS if "=" in option else None
    return OptionFault.LETTERS if len(option) != 2 else None


def _count(dial: str, index: int, item: dict[str, object], field: str) -> int:
    value = item.get(field, 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ConfigurationFailure(messages.c5_reader_count(dial, index, field))
    return value


def _entries(value: object, reader: ReaderLists) -> tuple[Entry, ...]:
    """Absent: the defaults. An empty list: nothing is gated, said at session start. Anything else
    is a list of well-formed entries, or a configuration failure naming the first bad one; an entry
    is read through the wrappers and shells `reader` holds, the lists being loaded."""
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
        read = tokens.reading(command, reader)
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
