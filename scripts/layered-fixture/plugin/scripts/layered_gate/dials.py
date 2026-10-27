"""This gate's own dials, and its layer's key, held as the shared reader hands them over.

The gate has no dial beyond the two every gate has, `severity` and `log_dir`, which the shared code reads;
refusing any other key makes a misspelt one a configuration failure, never a setting ignored in silence. Its
layer's key, `layer_dialect`, stands in `Dials.layer` as YAML read it: when it is there it must be the one
dialect the layer knows. A policy namespace in this file is refused, since the policies stand in the
constitution's file."""

from __future__ import annotations

from constitution_layer_kit.dials import GATE_KEYS, refuse_unknown_keys
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import Dials

from . import messages
from .model import LAYER_DIALECT, LAYER_DIALECT_KEY

KEYS = GATE_KEYS


def parse(dials: Dials) -> None:
    refuse_unknown_keys(dials.own, KEYS)
    if LAYER_DIALECT_KEY in dials.layer and dials.layer[LAYER_DIALECT_KEY] != LAYER_DIALECT:
        raise ConfigurationFailure(messages.l1_dialect(str(dials.layer[LAYER_DIALECT_KEY])))
    for name in dials.namespaces:
        if not name.startswith(dials.module_prefix):  # a namespace no prefix claims is a policy's
            raise ConfigurationFailure(messages.l2_policy_namespace(name))
