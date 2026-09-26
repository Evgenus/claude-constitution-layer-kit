"""Says which gate this entry point is and hands over to the shared command line. The mode is
loaded by the shared guard only after its preflight, because it needs the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from const_gate import cli
from const_gate.identity import Identity

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = "const-styling"

GATE = Identity(
    namespace=NAMESPACE,
    gate="check-style",
    plugin_root=PLUGIN_ROOT,
    until_installed="until then no document is scanned for style",
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)
