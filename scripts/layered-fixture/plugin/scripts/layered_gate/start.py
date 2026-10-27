"""Says which gate this is and hands over to the shared command line. The modes are loaded
by the shared guard only after its preflight, because they need the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit import cli
from constitution_layer_kit.identity import HOOK_SECONDS, Identity

from .model import LAYER_DIALECT_KEY

# A gate of another layer: the dials file of its own layer, and that file's kernel keys, `module_prefix`
# among them. The policies are read from the constitution's file inside a scope of their own.
GATE = Identity(
    namespace="know-check",
    gate="check-layered",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="layer.yaml",
    kernel_keys=("module_prefix", LAYER_DIALECT_KEY),
    hook_seconds=HOOK_SECONDS,
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)
