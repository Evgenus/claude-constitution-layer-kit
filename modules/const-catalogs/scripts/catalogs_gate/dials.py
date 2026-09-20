"""This module's own dials, parsed once from its namespace as the shared reader hands it over:
`catalogs`, a list of `{prefix, territory, width}`."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate import identity
from const_gate.dials import refuse_unreadable_patterns
from const_gate.errors import ConfigurationFailure

from . import messages
from .model import DEFAULT_WIDTH, PREFIX_RE, Catalog, CatalogDials

KEYS = {"prefix", "territory", "width"}


def parse(own: Mapping[str, object]) -> CatalogDials:
    """An entry of the wrong shape, and one prefix listed twice, are configuration failures."""
    value = own.get("catalogs")
    if value is None:
        return CatalogDials(())
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_catalogs_not_a_list())
    catalogs: list[Catalog] = []
    for position, entry in enumerate(value, start=1):
        catalog = _entry(position, entry)
        if any(earlier.prefix == catalog.prefix for earlier in catalogs):
            raise ConfigurationFailure(messages.c5_prefix_listed_twice(catalog.prefix))
        catalogs.append(catalog)
    return CatalogDials(tuple(catalogs))


def _entry(position: int, entry: object) -> Catalog:
    if not isinstance(entry, dict) or not set(entry) <= KEYS:
        raise ConfigurationFailure(messages.c5_catalog_entry(position))
    prefix = _prefix(entry.get("prefix"))
    territory = _territory(entry.get("territory"))
    width = _width(entry.get("width", DEFAULT_WIDTH))
    if prefix is None or territory is None or width is None:
        raise ConfigurationFailure(messages.c5_catalog_entry(position))
    refuse_unreadable_patterns(f"{identity.current().namespace}.catalogs[{prefix}]", territory)
    return Catalog(prefix, width, territory)


def _prefix(value: object) -> str | None:
    return value if isinstance(value, str) and PREFIX_RE.match(value) else None


def _territory(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not value:
        return None
    if not all(isinstance(pattern, str) and pattern.strip() for pattern in value):
        return None
    return tuple(str(pattern) for pattern in value)


def _width(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):  # YAML's true is an int to Python
        return None
    return value if value >= 1 else None
