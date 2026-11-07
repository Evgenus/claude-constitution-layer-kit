"""Says which gate each entry point is and hands over to the shared command line. The modes
are loaded by the shared guard only after its preflight, because they need the declared
libraries. Three entry points, one process each: the shell gate, the list scan, the
session-start printer."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit import cli
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import KERNEL_KEYS

from . import session
from .model import COMMAND_FLAG

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = "const-interaction"

GATE = Identity(
    namespace=NAMESPACE,
    gate="check-destructive",
    plugin_root=PLUGIN_ROOT,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then shell commands pass unchecked",
)
LISTS = Identity(
    namespace=NAMESPACE,
    gate="check-list-handles",
    plugin_root=PLUGIN_ROOT,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    until_installed="until then no list is scanned",
)
SESSION = Identity(
    namespace=NAMESPACE,
    gate="session-start",
    plugin_root=PLUGIN_ROOT,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then the gate's state is not said at session start",
)

# the effect report's own identity: the same plugin and dials file, the entry file effect-report.py
REPORT = Identity(
    namespace=NAMESPACE,
    gate="effect-report",
    plugin_root=PLUGIN_ROOT,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then the effect report is not made",
)

ARGUMENTS = (cli.Argument(COMMAND_FLAG, "text"),)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode, scan_with=modes.scan_with)


def load_list_modes() -> cli.Modes:
    from . import lists  # noqa: PLC0415 — the same reason

    return cli.Modes(hook=lists.hook_mode, scan=lists.scan_mode)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes, ARGUMENTS)


def main_lists(argv: Sequence[str]) -> int:
    return cli.run(argv, LISTS, load_list_modes)


def main_session(argv: Sequence[str]) -> int:
    return session.run(argv, SESSION)
