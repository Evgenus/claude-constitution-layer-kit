"""This module's own dials, parsed once from its namespace as the shared reader hands it over:
`record_policies`, a list of policy ids. A key that is none of the six this module's gate and
skills read is a configuration failure, never a setting ignored; the three skill-read keys are
refused by name only, their shape being the agent's to read."""

from __future__ import annotations

from collections.abc import Mapping

from constitution_layer_kit.dials import GATE_KEYS, refuse_unknown_keys
from constitution_layer_kit.envelope import ID_RE
from constitution_layer_kit.errors import ConfigurationFailure

from . import messages
from .model import RecordDials

KEYS = (*GATE_KEYS, "record_policies", "boundary_examples", "deciders", "note_trailer")


def parse(own: Mapping[str, object]) -> RecordDials:
    refuse_unknown_keys(own, KEYS)
    value = own.get("record_policies")
    if value is None:
        return RecordDials(())
    if not isinstance(value, list) or not all(isinstance(i, str) and ID_RE.fullmatch(i) for i in value):
        raise ConfigurationFailure(messages.c5_record_policies())
    return RecordDials(tuple(dict.fromkeys(str(i) for i in value)))  # a policy named twice counts once
