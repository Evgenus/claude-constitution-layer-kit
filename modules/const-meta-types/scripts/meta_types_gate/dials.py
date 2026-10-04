"""This module's own dials, parsed once from its namespace as the shared reader hands it over.
The module has no dial beyond the two every gate has, `severity` and `log_dir`, which the shared
code reads; parsing here refuses any other key, so that a misspelt one is a configuration
failure, never a setting ignored in silence."""

from __future__ import annotations

from collections.abc import Mapping

from const_gate.dials import GATE_KEYS, refuse_unknown_keys

KEYS = GATE_KEYS


def parse(own: Mapping[str, object]) -> None:
    refuse_unknown_keys(own, KEYS)
