"""The session-start printer: after the rules, the value of the verbosity dial — the default where
no dials file can be read — then one line about the state of the destructive-command gate where it
examines nothing — no repository, no dials file, an empty list — then one line for each default
wrapper or shell the dials drop or replace, and the project's own boundary examples. Advisory: it
prints to the model's context and blocks nothing; a configuration failure is still exit 1 with its
line first, as every script of the kit."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING

from constitution_layer_kit import cli, preflight
from constitution_layer_kit import messages as shared
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.identity import Identity
from constitution_layer_kit.model import Mode, SkipKind
from constitution_layer_kit.output import Output

from . import messages

if TYPE_CHECKING:
    from constitution_layer_kit.pipeline import Skip
from .model import Replaced, Verbosity

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
    if isinstance(target, Skip):  # no dials to read: the default value, then why the gate is off
        output.out(messages.z1_verbosity(Verbosity.TRIGGERED))
        output.out(_zero_line(target))
        return 0
    dials = own_dials.parse(target.dials.own)
    output.out(messages.z1_verbosity(dials.verbosity))
    if not dials.destructive:
        output.out(messages.z1_empty())
    for change in dials.changed:
        if isinstance(change, Replaced):
            output.out(messages.z1_replaced(change.dial, change.command))
        else:
            output.out(messages.z1_dropped(change.dial, change.command))
    if dials.boundary_examples:
        output.out(messages.z1_pairs_heading())
        for number, pair in enumerate(dials.boundary_examples, 1):
            output.out(messages.z1_pair(number, pair.violates, pair.complies))
    return 0


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
