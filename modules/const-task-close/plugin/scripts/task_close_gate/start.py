"""Says which gate this is, which flags its scan takes, and hands over to the shared command
line. The modes are loaded by the shared guard only after its preflight, because they need
the declared libraries."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit import cli
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import Mode

GATE = Identity(
    namespace="const-task-close",
    gate="check-task-close",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="constitution.yaml",
    hook_seconds=HOOK_SECONDS,
    # what a failure to install leaves unchecked: the turn-end tree and a change's documents, not a write
    until_installed="until then neither the tree at turn end nor a change's documents are checked",
    # the skill a red names (F10): the turn-end tree's rule, then the range check's
    skills={Mode.HOOK: "commit-before-edit", Mode.SCAN: "close-task"},
)

ARGUMENTS = (
    cli.Argument("--since", "ref"),
    cli.Argument("--change", "commit"),
    cli.Argument("--body", "file"),
)


def load_modes() -> cli.Modes:
    # Necessary here, not at the top: the modes import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import modes  # noqa: PLC0415

    return cli.Modes(hook=modes.hook_mode, scan=modes.scan_mode, scan_with=modes.scan_with)


def main(argv: Sequence[str]) -> int:
    return cli.run(argv, GATE, load_modes, ARGUMENTS)
