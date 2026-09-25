"""The session-start printer: after the rules, one line about the state of the destructive-command
gate where it examines nothing — no repository, no dials file, an empty list — and the project's
own boundary examples. Advisory: it prints to the model's context and blocks nothing; a
configuration failure is still exit 1 with its line first, as every script of the kit."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from const_gate import cli, preflight
from const_gate import messages as shared
from const_gate.errors import ConfigurationFailure
from const_gate.identity import Identity
from const_gate.model import Mode
from const_gate.output import Output

from . import messages
from .model import Verbosity

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
    if isinstance(target, Skip):  # no dials to read: the default value, then why the gate is off
        output.out(messages.s1_verbosity(Verbosity.TRIGGERED))
        output.out(_zero_line(target.reason))
        return 0
    dials = own_dials.parse(target.dials.own)
    output.out(messages.s1_verbosity(dials.verbosity))
    if not dials.destructive:
        output.out(messages.s1_empty())
    if dials.boundary_examples:
        output.out(messages.s1_pairs_heading())
        for number, pair in enumerate(dials.boundary_examples, 1):
            output.out(f"{number}. {pair.violates} / {pair.complies}")
    return 0


def _zero_line(reason: str) -> str:
    """The shared skip reasons, said in this module's own words for the session."""
    if reason.startswith("no constitution.yaml in "):
        return messages.s1_no_dials(reason.removeprefix("no constitution.yaml in ").split(":", 1)[0])
    if " is not inside a git repository" in reason:
        return messages.s1_no_repo(reason.split(" is not inside a git repository", 1)[0])
    return f"{messages.s1_prefix()}: {reason}"


def run(argv: Sequence[str], gate: Identity) -> int:
    return cli.guarded(
        gate, Mode.HOOK, lambda output: body(output, argv), could_not_run=messages.s1_could_not_run
    )
