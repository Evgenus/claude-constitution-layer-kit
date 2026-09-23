"""This module's own dials, parsed once from its namespace as the shared reader hands it over:
`record_policies`, a list of policy ids. A key that is none of the six this module's gate and
skills read is a configuration failure, never a setting ignored; the three skill-read keys are
refused by name only, their shape being the agent's to read."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate.envelope import ID_RE
from const_gate.errors import ConfigurationFailure

from . import messages
from .model import RecordDials

KEYS = {"severity", "log_dir", "record_policies", "boundary_examples", "deciders", "note_trailer"}


def parse(own: Mapping[str, object]) -> RecordDials:
    for key in own:
        if key not in KEYS:
            raise ConfigurationFailure(messages.c5_unknown_dial(key))
    value = own.get("record_policies")
    if value is None:
        return RecordDials(())
    if not isinstance(value, list) or not all(isinstance(i, str) and ID_RE.match(i) for i in value):
        raise ConfigurationFailure(messages.c5_record_policies())
    return RecordDials(tuple(dict.fromkeys(str(i) for i in value)))  # a policy named twice counts once
