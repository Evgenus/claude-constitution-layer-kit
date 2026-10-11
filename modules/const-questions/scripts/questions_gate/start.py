"""Says which gate this is and hands over to the shared command line. The modes are loaded
by the shared guard only after its preflight, because they need the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from const_gate import cli
from const_gate.identity import HOOK_SECONDS, Identity
from const_gate.model import Mode

GATE = Identity(
    namespace="const-questions",
    gate="check-open-questions",
    plugin_root=Path(__file__).resolve().parents[2],
    hook_seconds=HOOK_SECONDS,
    skills={Mode.HOOK: "ask-or-decide", Mode.SCAN: "ask-or-decide"},  # the skill a red names (F10)
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)
