"""The dials file: read once, validated against the kernel's rules for the keys every gate
reads — the two kernel-owned keys, `territory` of every namespace that could be a policy's,
and the two dials every gate has, `severity` and `log_dir`. The rest of the module's own
namespace is handed over as read, for the module to parse.

A namespace named like a module (const-*) is a policy's only when a policy document carries
that id, so its `territory` is read leniently: a well-formed one is kept for that case,
anything else is another module's business."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml

from . import identity, messages
from .envelope import yaml_error_line
from .errors import ConfigurationFailure
from .model import DIALECT, DIALECT_KEY, DIALS_FILE, KERNEL_KEYS, ROOT_POLICY_KEY, Dials, Namespace, Severity

SEVERITY_KEY = "severity"
LOG_DIR_KEY = "log_dir"
GATE_KEYS = (SEVERITY_KEY, LOG_DIR_KEY)  # the two dials every gate has, read here; a module whose gate
# blocks nothing has no severity, and lists LOG_DIR_KEY alone
MODULE_PREFIX = "const-"


def load_dials(root: Path) -> Dials | None:
    """None when the file is absent (nothing is claimed); ConfigurationFailure when malformed."""
    path = root / DIALS_FILE
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:  # a byte that is not UTF-8: the file's content, not the gate
        raise ConfigurationFailure(messages.c4_dials_invalid_yaml(messages.detail_not_utf8(exc))) from exc
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
    _check_dialect(raw.get(DIALECT_KEY, DIALECT))
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
        root_policy=_root_policy(raw.get(ROOT_POLICY_KEY)),
        severity=_severity(own.get(SEVERITY_KEY)),
        log_dir=_relative_dir(own.get(LOG_DIR_KEY)),
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
    patterns = texts(value)
    if not patterns and value != []:  # no list of non-empty strings; an empty list is a territory of nothing
        if lenient:
            return ()
        raise ConfigurationFailure(messages.c5_territory_shape(name))
    refuse_unreadable_patterns(f"{name}.territory", patterns)
    return patterns


def refuse_unreadable_patterns(where: str, patterns: Sequence[str]) -> None:
    """A pattern git would read as something else — a comment, two lines — is a configuration
    failure wherever a territory is declared: under a policy's id, or in a module's own dials.
    `where` is the dial's whole path, as a person would write it to find it."""
    for pattern in patterns:
        if pattern.startswith("#") or "\n" in pattern or "\r" in pattern:
            raise ConfigurationFailure(messages.c5_territory_pattern(where, pattern))


def refuse_unknown_keys(own: Mapping[str, object], known: Sequence[str]) -> None:
    """A key of the module's namespace that is none of `known` is a configuration failure, never a
    setting ignored in silence: the first in sorted order is named, so the verdict does not depend
    on the order the file lists them."""
    unknown = sorted(str(key) for key in own if str(key) not in known)
    if unknown:
        raise ConfigurationFailure(messages.c5_unknown_dial(unknown[0], known))


def texts(value: object) -> tuple[str, ...]:
    """The non-empty strings of a list, as written — line breaks included; empty when the value is no
    such list, or when it is an empty one: the caller that must tell the two apart asks for `[]`."""
    if not isinstance(value, list) or not all(isinstance(t, str) and t.strip() for t in value):
        return ()
    return tuple(str(t) for t in value)


def relative_path(value: str) -> str | None:
    """A repository-relative path, normalised and written with `/`; None when it is blank, absolute,
    or leaves the repository by `..`. The separator is the platform's own — `\\` splits a path only
    where the platform says so — so a path is read as the file system will read it."""
    if not value.strip() or os.path.isabs(value):
        return None
    normal = os.path.normpath(value)
    if ".." in normal.split(os.sep):
        return None
    return normal.replace(os.sep, "/")


def _root_policy(value: object) -> str | None:
    if value is None:
        return None
    path = relative_path(value) if isinstance(value, str) else None
    if path is None:
        raise ConfigurationFailure(messages.c5_root_policy_path())
    return path


def _severity(value: object) -> Severity:
    if value is None:
        return Severity.BLOCK
    if not isinstance(value, str) or value not in {s.value for s in Severity}:
        raise ConfigurationFailure(messages.c5_severity())
    return Severity(value)


def _relative_dir(value: object) -> str | None:
    if value is None:
        return None
    path = relative_path(value) if isinstance(value, str) else None
    if path is None:
        raise ConfigurationFailure(messages.c5_log_dir())
    return path
