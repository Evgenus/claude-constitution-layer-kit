"""Which policies declare their kind as numbered: `catalog: {prefix, width}` in a policy's
namespace of the dials file, read only for the ids the index found a policy for."""

from __future__ import annotations

from const_gate.errors import ConfigurationFailure
from const_gate.index import Index
from const_gate.model import Dials

from . import messages
from .model import DEFAULT_WIDTH, PREFIX_RE, Catalog

KEYS = {"prefix", "width"}


def declared(index: Index, dials: Dials) -> list[Catalog]:
    """Every declared catalog, in the order of the policies' ids. A declaration of the wrong
    shape, and one prefix declared by two policies, are configuration failures."""
    catalogs: list[Catalog] = []
    for policy_id in sorted(index.policies):
        value = dials.as_read_of(policy_id).get("catalog")
        if value is None:
            continue
        catalog = _parse(policy_id, value)
        earlier = next((c for c in catalogs if c.prefix == catalog.prefix), None)
        if earlier is not None:
            failure = messages.c5_prefix_declared_twice(catalog.prefix, earlier.policy, policy_id)
            raise ConfigurationFailure(failure)
        catalogs.append(catalog)
    return catalogs


def _parse(policy_id: str, value: object) -> Catalog:
    if not isinstance(value, dict) or not set(value) <= KEYS:
        raise ConfigurationFailure(messages.c5_catalog_shape(policy_id))
    prefix, width = value.get("prefix"), value.get("width", DEFAULT_WIDTH)
    well_formed = (
        isinstance(prefix, str)
        and PREFIX_RE.match(prefix) is not None
        and isinstance(width, int)
        and not isinstance(width, bool)  # YAML's true is an int to Python
        and width >= 1
    )
    if not well_formed:
        raise ConfigurationFailure(messages.c5_catalog_shape(policy_id))
    return Catalog(str(prefix), int(width), policy_id)
