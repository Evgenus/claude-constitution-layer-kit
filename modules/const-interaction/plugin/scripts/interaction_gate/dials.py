"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from constitution_layer_kit import identity
from constitution_layer_kit.dials import GATE_KEYS, refuse_unknown_keys, refuse_unreadable_patterns, texts
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.messages import echoed

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
    ReaderDial,
    ReaderField,
    ReaderLists,
    Replaced,
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
WRAPPER_FIELDS = (
    ReaderField.COMMAND,
    ReaderField.WITH_VALUE,
    ReaderField.POSITIONALS,
    ReaderField.NUMBERS,
    ReaderField.COMMAND_FLAGS,
    ReaderField.SHELL_TEXT,
    ReaderField.DROP,
)
SHELL_FIELDS = (
    ReaderField.COMMAND,
    ReaderField.WITH_VALUE,
    ReaderField.COMMAND_FLAGS,
    ReaderField.DROP,
)
# The signs an option of each starts with: the reader takes a wrapper's options as the words that start
# with `-`, a shell's as those that start with `-` or `+`.
OPTION_SIGNS = {ReaderDial.WRAPPERS: "-", ReaderDial.SHELLS: "-+"}


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
    reader, changed = _reader_lists(own)  # first: an entry of `destructive` is read through these lists
    return InteractionDials(
        destructive=_entries(own.get("destructive"), reader),
        territories=territories,
        handles=handles,
        boundary_examples=_pairs(own.get("boundary_examples")),
        verbosity=_verbosity(own.get("verbosity")),
        reader=reader,
        changed=changed,
    )


def _reader_lists(own: Mapping[str, object]) -> tuple[ReaderLists, tuple[Dropped | Replaced, ...]]:
    """The wrappers and the shells of the reader: the defaults, each list the dials give applied to them
    by command, and the defaults dropped or replaced. A word is a wrapper or a shell, never both."""
    listed, changed_wrappers = _merged(
        ReaderDial.WRAPPERS, own.get(ReaderDial.WRAPPERS), WRAPPER_FIELDS, DEFAULT_WRAPPERS
    )
    wrappers = tuple(entry for entry in listed if isinstance(entry, Wrapper))
    listed, changed_shells = _merged(
        ReaderDial.SHELLS, own.get(ReaderDial.SHELLS), SHELL_FIELDS, DEFAULT_SHELLS
    )
    shells = tuple(entry for entry in listed if isinstance(entry, Shell))
    wrapper_words = {wrapper.command[0] for wrapper in wrappers}  # a wrapper strips from its first word
    for shell in shells:
        if shell.command in wrapper_words:
            raise ConfigurationFailure(messages.c5_reader_both(shell.command))
    return ReaderLists(wrappers, shells), (*changed_wrappers, *changed_shells)


def _words_of(entry: Wrapper | Shell) -> tuple[str, ...]:
    return (entry.command,) if isinstance(entry, Shell) else entry.command


def _merged(
    dial: ReaderDial, value: object, fields: tuple[ReaderField, ...], defaults: Sequence[Wrapper | Shell]
) -> tuple[list[Wrapper | Shell], tuple[Dropped | Replaced, ...]]:
    """Absent: the defaults. A list: each entry applied to the defaults by its command — one of a
    default's command replaces that default whole, a new command is added, `drop: true` removes the
    default — or a configuration failure naming the first bad entry of the loop. A shell given with no
    command flag is judged after the loop, so an entry the loop would refuse later in the list is named
    before it. An empty list leaves the defaults. The defaults dropped and the defaults replaced come
    back together, in the order of their entries."""
    merged = list(defaults)
    if value is None:
        return merged, ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_reader_list(dial))
    changed: list[Dropped | Replaced] = []
    bare: list[tuple[int, str]] = []  # the shells given without a command flag, with their entry numbers
    seen: dict[tuple[str, ...], int] = {}
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ConfigurationFailure(messages.c5_reader_entry(dial, index, "it is not a mapping"))
        command = _new_command(dial, index, item, fields, seen)
        if ReaderField.DROP in item:
            _refuse_bad_drop(dial, index, item, command, defaults)
            changed.append(Dropped(dial, command))
            merged = [entry for entry in merged if _words_of(entry) != command]
            continue
        built: Wrapper | Shell = (
            _wrapper(dial, index, item, command)
            if dial is ReaderDial.WRAPPERS
            else _shell(dial, index, item, command)
        )
        if isinstance(built, Shell) and not built.command_flags:
            bare.append((index, built.command))
        place = next((at for at, entry in enumerate(merged) if _words_of(entry) == command), None)
        if place is None:
            merged.append(built)
        else:
            merged[place] = built
            changed.append(Replaced(dial, command))
    if bare:  # judged after the loop: the twice check of a later entry is the first line of a list
        raise ConfigurationFailure(messages.c5_reader_no_flags(*bare[0]))
    return merged, tuple(changed)


def _new_command(
    dial: ReaderDial,
    index: int,
    item: dict[str, object],
    fields: tuple[ReaderField, ...],
    seen: dict[tuple[str, ...], int],
) -> tuple[str, ...]:
    """The command of an entry whose every key is a field, given by no earlier entry; `seen` records it
    with the entry's number."""
    unknown = sorted(str(key) for key in item if key not in fields)
    if unknown:
        raise ConfigurationFailure(messages.c5_reader_unknown(dial, index, unknown[0]))
    command = _reader_command(dial, index, item)
    if command in seen:
        raise ConfigurationFailure(messages.c5_reader_twice(dial, index, command, seen[command]))
    seen[command] = index
    return command


def _refuse_bad_drop(
    dial: ReaderDial,
    index: int,
    item: dict[str, object],
    command: tuple[str, ...],
    defaults: Sequence[Wrapper | Shell],
) -> None:
    """A drop is `drop: true` beside the command alone, and names a default."""
    if item[ReaderField.DROP] is not True:
        raise ConfigurationFailure(messages.c5_reader_drop_value(dial, index))
    beside = sorted(ReaderField(key) for key in item if key not in (ReaderField.COMMAND, ReaderField.DROP))
    if beside:
        raise ConfigurationFailure(messages.c5_reader_drop_beside(dial, index, beside[0]))
    if not any(_words_of(default) == command for default in defaults):
        names = [" ".join(_words_of(default)) for default in defaults]
        raise ConfigurationFailure(messages.c5_reader_drop_unknown(dial, index, command, names))


def _reader_command(dial: ReaderDial, index: int, item: dict[str, object]) -> tuple[str, ...]:
    """The words of an entry's `command`: a non-empty list, no word empty or holding white space, the
    first with no `/` — the reader reduces only the program to its base name, so a first word with a `/`
    can never match, while a later word is compared as written — and for a shell one word."""
    command = texts(item.get(ReaderField.COMMAND))
    if not command or "/" in command[0] or any(any(letter.isspace() for letter in word) for word in command):
        raise ConfigurationFailure(messages.c5_reader_command(dial, index))
    if dial is ReaderDial.SHELLS and len(command) != 1:
        raise ConfigurationFailure(messages.c5_reader_shell_words(index, command))
    return command


def _refuse_stripped_first_word(dial: ReaderDial, index: int, word: str) -> None:
    """An entry whose first word the reader would take off before it looks for a wrapper or a shell
    never matches."""
    if tokens.ASSIGNMENT.match(word) or word in tokens.SHELL_WORDS:
        raise ConfigurationFailure(messages.c5_reader_first_word(dial, index, word))


def _wrapper(dial: ReaderDial, index: int, item: dict[str, object], command: tuple[str, ...]) -> Wrapper:
    _refuse_stripped_first_word(dial, index, command[0])
    with_value = _options(dial, index, item, ReaderField.WITH_VALUE)
    positionals = _count(dial, index, item, ReaderField.POSITIONALS)
    numbers = _count(dial, index, item, ReaderField.NUMBERS)
    command_flags = _options(dial, index, item, ReaderField.COMMAND_FLAGS)
    _refuse_shared_option(dial, index, with_value, command_flags)
    shell_text = item.get(ReaderField.SHELL_TEXT, False)
    if not isinstance(shell_text, bool):
        raise ConfigurationFailure(messages.c5_reader_shell_text_value(index))
    if shell_text and not command_flags:
        raise ConfigurationFailure(messages.c5_reader_shell_text_alone(index))
    return Wrapper(
        command,
        with_value=with_value,
        positionals=positionals,
        numbers=numbers,
        command_flags=command_flags,
        shell_text=shell_text,
    )


def _shell(dial: ReaderDial, index: int, item: dict[str, object], command: tuple[str, ...]) -> Shell:
    _refuse_stripped_first_word(dial, index, command[0])
    with_value = _options(dial, index, item, ReaderField.WITH_VALUE)
    command_flags = _options(dial, index, item, ReaderField.COMMAND_FLAGS)
    _refuse_shared_option(dial, index, with_value, command_flags)
    return Shell(command[0], with_value=with_value, command_flags=command_flags)


def _refuse_shared_option(
    dial: ReaderDial, index: int, with_value: tuple[str, ...], command_flags: tuple[str, ...]
) -> None:
    """An option in both fields has one of its two places dead: the reader tries command_flags first."""
    shared = next((option for option in with_value if option in command_flags), None)
    if shared is not None:
        raise ConfigurationFailure(messages.c5_reader_both_fields(dial, index, shared))


def _options(dial: ReaderDial, index: int, item: dict[str, object], field: ReaderField) -> tuple[str, ...]:
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


def _option_fault(dial: ReaderDial, option: str) -> OptionFault | None:
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


def _count(dial: ReaderDial, index: int, item: dict[str, object], field: ReaderField) -> int:
    value = item.get(field, 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ConfigurationFailure(messages.c5_reader_count(dial, index, field))
    return value


def _entries(value: object, reader: ReaderLists) -> tuple[Entry, ...]:
    """Absent: the defaults, each read through the wrappers and shells `reader` holds as a written entry
    is, or a configuration failure naming the first the reader dials make it read as other than itself.
    An empty list: nothing is gated, said at session start. Anything else is a list of well-formed
    entries, or a configuration failure naming the first bad one; an entry is read through the wrappers
    and shells `reader` holds, the lists being loaded."""
    if value is None:
        _refuse_defaults_unread(reader)
        return DEFAULT_DESTRUCTIVE
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_destructive())
    return tuple(_entry(index, item, reader) for index, item in enumerate(value, 1))


def _refuse_defaults_unread(reader: ReaderLists) -> None:
    """Each default entry is read through the reader lists as it is written."""
    for default in DEFAULT_DESTRUCTIVE:
        read = tokens.reading(default.command, reader)
        if read != list(default.command):
            raise ConfigurationFailure(messages.c5_default_unread(default.command, read))


def _entry(index: int, item: object, reader: ReaderLists) -> Entry:
    """Entry `index` of the list, well formed and read as written, or a configuration failure naming
    what is wrong."""
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
    return Entry(command, flags, teach.strip(), alternative.strip())


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
