"""This module's own dials, parsed once from its namespace as the shared reader hands it over.
The module has no dial beyond the two every gate has, `severity` and `log_dir`, which the shared
code reads; parsing here refuses any other key, so that a misspelt one is a configuration
failure, never a setting ignored in silence."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate.errors import ConfigurationFailure

from . import messages

KEYS = {"severity", "log_dir"}


def parse(own: Mapping[str, object]) -> None:
    for key in own:
        if key not in KEYS:
            raise ConfigurationFailure(messages.c5_unknown_dial(key))
