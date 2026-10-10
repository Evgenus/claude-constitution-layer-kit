"""Says which gate each entry point is and hands over to the shared command line. The modes are
loaded by the shared guard only after its preflight, because they need the declared libraries. Two
entry points, one process each: the gate, the session-start printer."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from const_gate import cli
from const_gate.identity import Identity
from const_gate.model import Mode

from . import session

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = "const-decision-records"

GATE = Identity(
    namespace=NAMESPACE,
    gate="check-decision-record",
    plugin_root=PLUGIN_ROOT,
    skills={Mode.HOOK: "record-decision", Mode.SCAN: "record-decision"},  # the skill a red names (F10)
)
SESSION = Identity(
    namespace=NAMESPACE,
    gate="session-start",
    plugin_root=PLUGIN_ROOT,
    until_installed="until then the gate's state is not said at session start",
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes)


def main_session(argv: Sequence[str]) -> int:
    return session.run(argv, SESSION)
