"""Says which gate this entry point is and hands over to the shared command line. The modes are
loaded by the shared guard only after its preflight, because they need the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit import cli
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import Mode

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = "const-language"

GATE = Identity(
    namespace=NAMESPACE,
    gate="check-language",
    plugin_root=PLUGIN_ROOT,
    hook_seconds=HOOK_SECONDS,
    skills={Mode.HOOK: "plain-language", Mode.SCAN: "plain-language"},  # the skill a red names (F10)
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)
