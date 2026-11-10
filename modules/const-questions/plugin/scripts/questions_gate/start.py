"""Says which gate this is and hands over to the shared command line. The modes are loaded
by the shared guard only after its preflight, because they need the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from constitution_layer_kit import cli
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import KERNEL_KEYS, Mode

if TYPE_CHECKING:
    from constitution_layer_kit.effect import Rule

GATE = Identity(
    namespace="const-questions",
    gate="check-open-questions",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    skills={Mode.HOOK: "ask-or-decide", Mode.SCAN: "ask-or-decide"},  # the skill a red names (F10)
)

EFFECT = (
    Identity(  # the effect report's own: it names no skill, and its failures end "the report is not made"
        namespace=GATE.namespace,
        gate="effect-report",
        plugin_root=GATE.plugin_root,
        dials_file=GATE.dials_file,
        kernel_keys=KERNEL_KEYS,
        hook_seconds=HOOK_SECONDS,
        until_installed="until then the effect report is not made",
    )
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def load_rules() -> Sequence[Rule]:
    # Necessary here, not at the top: the rules import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import effect_rules  # noqa: PLC0415

    return effect_rules.rules()


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)
