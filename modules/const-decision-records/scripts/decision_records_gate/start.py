"""Says which gate this is and hands over to the shared command line. The modes are loaded
by the shared guard only after its preflight, because they need the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from const_gate import cli
from const_gate.identity import Identity

GATE = Identity(
    namespace="const-decision-records",
    gate="check-decision-record",
    plugin_root=Path(__file__).resolve().parents[2],
)


def load_modes() -> cli.Modes:
    from . import modes

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)
