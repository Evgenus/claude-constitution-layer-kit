"""The session-start printer: one line while the length gate measures nothing — no repository,
no dials file, the `ceilings` dial empty or absent — and nothing while a ceiling is set. Advisory:
it prints to the model's context and blocks nothing; a configuration failure is still exit 1 with its
line first, as every script of the plugin."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING

from constitution_layer_kit import cli, preflight
from constitution_layer_kit import messages as shared
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.identity import Identity
from constitution_layer_kit.model import EXIT_GREEN, Mode, SkipKind
from constitution_layer_kit.output import Output

from . import messages

if TYPE_CHECKING:
    from constitution_layer_kit.pipeline import Skip

USAGE = "session-start takes no arguments; it reads one SessionStart event on stdin"


def body(output: Output, argv: Sequence[str]) -> int:
    if argv:
        raise ConfigurationFailure(shared.c12_invocation(f"unexpected argument {argv[0]}", USAGE))
    preflight.check()
    # Necessary here, not at the top: the pipeline and the dials import the declared library, and
    # only after the preflight does a missing one become its designed message instead of a traceback.
    from constitution_layer_kit import pipeline  # noqa: PLC0415
    from constitution_layer_kit.pipeline import Skip  # noqa: PLC0415

    from . import dials as own_dials  # noqa: PLC0415

    target = pipeline.locate_event(output, sys.stdin)
    if isinstance(target, Skip):  # no dials to read: why the gate is off
        output.out(_zero_line(target))
        return EXIT_GREEN
    if not own_dials.parse(target.dials.own).ceilings:
        output.out(messages.z1_empty())
    return EXIT_GREEN


def _zero_line(skip: Skip) -> str:
    """The shared skip, said in this module's own words for the session; a skip of another kind is
    printed whole after the module's name."""
    if skip.kind is SkipKind.NO_DIALS:
        return messages.z1_no_dials(skip.where)
    if skip.kind is SkipKind.NO_REPO:
        return messages.z1_no_repo(skip.where)
    return f"{messages.z1_prefix()}: {skip.reason}"


def run(argv: Sequence[str], gate: Identity) -> int:
    return cli.guarded(
        gate, Mode.HOOK, lambda output: body(output, argv), could_not_run=messages.z1_could_not_run
    )
