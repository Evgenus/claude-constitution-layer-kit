"""The dials file: read once, validated against the kernel's rules for the keys this gate
reads — the two kernel-owned keys, `territory` of every namespace that could be a
policy's, and this module's own dials. A namespace named like a module (const-*) is a
policy's only when a policy document carries that id, so its `territory` is read leniently:
a well-formed one is kept for that case, anything else is another module's business."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from . import messages
from .envelope import ID_RE
from .errors import ConfigurationFailure
from .model import DIALECT, DIALS_FILE, NAMESPACE, Dials, Namespace, Severity

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
        raise ConfigurationFailure(messages.c4_dials_invalid_yaml(str(exc).splitlines()[0])) from exc
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
    own = raw.get(NAMESPACE, {})
    if own is None:
        own = {}
    if not isinstance(own, dict):
        raise ConfigurationFailure(messages.c5_own_namespace_not_mapping())
    return Dials(
        root_policy=_root_policy(raw.get("root_policy")),
        severity=_severity(own.get("severity")),
        log_dir=_relative_dir(own.get("log_dir")),
        record_policies=_policy_ids(own.get("record_policies")),
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
    for pattern in patterns:
        if pattern.startswith("#") or "\n" in pattern or "\r" in pattern:
            raise ConfigurationFailure(messages.c5_territory_pattern(name, pattern))
    return patterns


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


def _policy_ids(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(i, str) and ID_RE.match(i) for i in value):
        raise ConfigurationFailure(messages.c5_record_policies())
    return tuple(str(i) for i in value)
