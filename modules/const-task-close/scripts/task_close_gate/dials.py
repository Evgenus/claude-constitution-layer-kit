"""This module's own dials, parsed once from its namespace as the shared reader hands it over:
`coverage`, a list of `{name, code, docs}`; `trunk`; `declaration_key`; `working_files`. A key
that is none of the six this module reads is a configuration failure, never a setting ignored."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate import identity
from const_gate.dials import refuse_unreadable_patterns
from const_gate.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_KEY, DEFAULT_TRUNK, KEY_RE, NAME_RE, Pair, TaskCloseDials

KEYS = {"severity", "log_dir", "coverage", "trunk", "declaration_key", "working_files"}
PAIR_KEYS = {"name", "code", "docs"}


def parse(own: Mapping[str, object]) -> TaskCloseDials:
    for key in own:
        if key not in KEYS:
            raise ConfigurationFailure(messages.c5_unknown_dial(key))
    coverage = _coverage(own.get("coverage"))
    working_files = _patterns(own.get("working_files"))
    if working_files is None:
        raise ConfigurationFailure(messages.c5_working_files())
    refuse_unreadable_patterns(f"{identity.current().namespace}.working_files", working_files)
    return TaskCloseDials(
        coverage=coverage,
        trunk=_trunk(own.get("trunk")),
        declaration_key=_key(own.get("declaration_key")),
        working_files=working_files,
    )


def _coverage(value: object) -> tuple[Pair, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_coverage_not_a_list())
    pairs: list[Pair] = []
    for position, entry in enumerate(value, start=1):
        pair = _pair(position, entry)
        if any(earlier.name == pair.name for earlier in pairs):
            raise ConfigurationFailure(messages.c5_pair(position, messages.pair_name_repeated(pair.name)))
        pairs.append(pair)
    return tuple(pairs)


def _pair(position: int, entry: object) -> Pair:
    if not isinstance(entry, dict):
        raise ConfigurationFailure(messages.c5_pair(position, messages.pair_not_a_mapping()))
    unknown = sorted(str(key) for key in entry if key not in PAIR_KEYS)
    if unknown:
        raise ConfigurationFailure(messages.c5_pair(position, messages.pair_unknown_key(unknown[0])))
    name = entry.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise ConfigurationFailure(messages.c5_pair(position, messages.pair_name()))
    code = _patterns(entry.get("code"))
    if not code:
        raise ConfigurationFailure(messages.c5_pair(position, messages.pair_code()))
    docs = _paths(entry.get("docs"))
    if not docs:
        raise ConfigurationFailure(messages.c5_pair(position, messages.pair_docs()))
    refuse_unreadable_patterns(f"{identity.current().namespace}.coverage[{name}].code", code)
    return Pair(name, code, docs)


def _patterns(value: object) -> tuple[str, ...] | None:
    """A list of non-empty strings; () for an absent key; None for anything else."""
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(p, str) and p.strip() for p in value):
        return None
    return tuple(str(p) for p in value)


def _paths(value: object) -> tuple[str, ...] | None:
    """Repository-relative paths, normalised to forward slashes with no leading './'."""
    patterns = _patterns(value)
    if patterns is None:
        return None
    paths: list[str] = []
    for path in patterns:
        clean = path.strip().replace("\\", "/")
        while clean.startswith("./"):
            clean = clean[2:]
        if clean.startswith("/") or ".." in clean.split("/") or not clean:
            return None
        paths.append(clean.rstrip("/"))
    return tuple(paths)


def _trunk(value: object) -> str:
    if value is None:
        return DEFAULT_TRUNK
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationFailure(messages.c5_trunk())
    return value.strip()


def _key(value: object) -> str:
    if value is None:
        return DEFAULT_KEY
    if not isinstance(value, str) or not KEY_RE.fullmatch(value):
        raise ConfigurationFailure(messages.c5_declaration_key())
    return value
