"""The dials file: read once, validated against the kernel's rules for the keys every gate
reads — the two kernel-owned keys, `territory` of every namespace that could be a policy's,
and the two dials every gate has, `severity` and `log_dir`. The rest of the module's own
namespace is handed over as read, for the module to parse.

A namespace named like a module (const-*) is a policy's only when a policy document carries
that id, so its `territory` is read leniently: a well-formed one is kept for that case,
anything else is another module's business."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

import yaml

from . import identity, messages
from .envelope import yaml_error_line
from .errors import ConfigurationFailure
from .model import DIALECT, DIALS_FILE, Dials, Namespace, Severity

KERNEL_KEYS = ("root_policy", "territory_dialect")
MODULE_PREFIX = "const-"


def load_dials(root: Path) -> Dials | None:
    """None when the file is absent (nothing is claimed); ConfigurationFailure when malformed."""
    path = root / DIALS_FILE
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationFailure(messages.c12_dials_unreadable(str(exc))) from exc
    try:
        loaded: object = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigurationFailure(messages.c4_dials_invalid_yaml(yaml_error_line(exc))) from exc
    except RecursionError as exc:
        failure = messages.c4_dials_invalid_yaml(messages.detail_nested_too_deeply())
        raise ConfigurationFailure(failure) from exc
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ConfigurationFailure(messages.c4b_dials_not_mapping())
    return _parse(loaded)


def _parse(raw: dict[object, object]) -> Dials:
    _check_dialect(raw.get("territory_dialect", DIALECT))
    namespaces: dict[str, Namespace] = {}
    for key, value in raw.items():
        name = str(key)
        if name in KERNEL_KEYS:
            continue
        if name.startswith(MODULE_PREFIX):
            if isinstance(value, dict):
                namespaces[name] = Namespace(name, _territory(name, value.get("territory"), lenient=True))
            continue
        if not isinstance(value, dict):
            raise ConfigurationFailure(messages.c5_namespace_not_mapping(name))
        namespaces[name] = Namespace(name, _territory(name, value.get("territory"), lenient=False))
    own = raw.get(
        identity.current().namespace, {}
    )  # absent: defaults; present: a mapping, as the schema says
    if not isinstance(own, dict):
        raise ConfigurationFailure(messages.c5_own_namespace_not_mapping())
    return Dials(
        root_policy=_root_policy(raw.get("root_policy")),
        severity=_severity(own.get("severity")),
        log_dir=_relative_dir(own.get("log_dir")),
        own={str(key): value for key, value in own.items()},
        namespaces=namespaces,
    )


def _check_dialect(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationFailure(messages.c5_dialect_empty())
    if value != DIALECT:
        raise ConfigurationFailure(messages.c5_dialect_unsupported(value))


def _territory(name: str, value: object, lenient: bool) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(p, str) and p.strip() for p in value):
        if lenient:
            return ()
        raise ConfigurationFailure(messages.c5_territory_shape(name))
    patterns = tuple(str(p) for p in value)
    refuse_unreadable_patterns(name, patterns)
    return patterns


def refuse_unreadable_patterns(name: str, patterns: Sequence[str]) -> None:
    """A pattern git would read as something else — a comment, two lines — is a configuration
    failure wherever a territory is declared: under a policy's id, or in a module's own dials."""
    for pattern in patterns:
        if pattern.startswith("#") or "\n" in pattern or "\r" in pattern:
            raise ConfigurationFailure(messages.c5_territory_pattern(name, pattern))


def _is_relative(value: str) -> bool:
    return (
        bool(value.strip()) and not os.path.isabs(value) and ".." not in os.path.normpath(value).split(os.sep)
    )


def _root_policy(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _is_relative(value):
        raise ConfigurationFailure(messages.c5_root_policy_path())
    return os.path.normpath(value).replace(os.sep, "/")


def _severity(value: object) -> Severity:
    if value is None:
        return Severity.BLOCK
    if not isinstance(value, str) or value not in {s.value for s in Severity}:
        raise ConfigurationFailure(messages.c5_severity())
    return Severity(value)


def _relative_dir(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _is_relative(value):
        raise ConfigurationFailure(messages.c5_log_dir())
    return os.path.normpath(value).replace(os.sep, "/")
