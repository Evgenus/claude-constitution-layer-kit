"""The session-start printer: one line while the catalog gate examines nothing — no repository,
no dials file, the `catalogs` dial empty or absent — and nothing while a catalog is listed. Advisory:
it prints to the model's context and blocks nothing; a configuration failure is still exit 1 with its
line first, as every script of the kit."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING

from const_gate import cli, preflight
from const_gate import messages as shared
from const_gate.errors import ConfigurationFailure
from const_gate.identity import Identity
from const_gate.model import Mode, SkipKind
from const_gate.output import Output

from . import messages

if TYPE_CHECKING:
    from const_gate.pipeline import Skip

USAGE = "session-start takes no arguments; it reads one SessionStart event on stdin"


def body(output: Output, argv: Sequence[str]) -> int:
    if argv:
        raise ConfigurationFailure(shared.c12_invocation(f"unexpected argument {argv[0]}", USAGE))
    preflight.check()
    # Necessary here, not at the top: the pipeline and the dials import the declared library, and
    # only after the preflight does a missing one become its designed message instead of a traceback.
    from const_gate import pipeline  # noqa: PLC0415
    from const_gate.pipeline import Skip  # noqa: PLC0415

    from . import dials as own_dials  # noqa: PLC0415

    target = pipeline.locate_event(output, sys.stdin)
    if isinstance(target, Skip):  # no dials to read: why the gate is off
        output.out(_zero_line(target))
        return 0
    if not own_dials.parse(target.dials.own).catalogs:
        output.out(messages.z1_empty())
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
