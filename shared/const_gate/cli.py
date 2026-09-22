"""The command line and the single guard.

Parameters are parsed with argparse, whose own default is to exit 2 on bad usage; 2 is
reserved for findings, so a misinvoked hook must not read as "blocked, here is the
feedback" having produced no verdict. The parser here raises a configuration failure
instead, and carries no built-in help action: argparse's help prints and exits on its
own, past the guard and the log. The usage is one line, in the misinvocation message.
The guard turns every configuration failure, and every unexpected exception, into
exit 1 — never 0 — and flushes the log however the run ended.
"""

from __future__ import annotations

import argparse
import sys
import traceback
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, TextIO

from . import identity, messages, preflight
from .errors import ConfigurationFailure
from .identity import Identity
from .model import EXIT_BROKEN, Mode
from .output import Output

SCAN_FLAG = "--scan"


@dataclass(frozen=True, slots=True)
class Modes:
    """The module's two modes. Each returns an exit code."""

    hook: Callable[[Output, TextIO], int]
    scan: Callable[[Output, Path], int]


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.c12_invocation(message))


def make_parser() -> Parser:
    parser = Parser(prog=identity.current().gate, add_help=False, allow_abbrev=False)  # --sc is not --scan
    parser.add_argument(SCAN_FLAG, nargs="?", const=".", default=None, metavar="DIR")
    return parser


def main(argv: Sequence[str], output: Output, load_modes: Callable[[], Modes]) -> int:
    args = make_parser().parse_args(list(argv))
    preflight.check()
    modes = load_modes()  # the module's code is imported after the preflight: it needs the libraries
    if args.scan is not None:
        return modes.scan(output, Path(args.scan))
    return modes.hook(output, sys.stdin)


def run(argv: Sequence[str], gate: Identity, load_modes: Callable[[], Modes]) -> int:
    """A gate's entry: the entry point says which gate this is and how to load its two modes."""
    mode = Mode.SCAN if any(a.startswith(SCAN_FLAG) for a in argv) else Mode.HOOK
    return guarded(gate, mode, lambda output: main(argv, output, load_modes))


def guarded(
    gate: Identity,
    mode: Mode,
    body: Callable[[Output], int],
    could_not_run: Callable[[], str] = messages.c11_broken_count,
) -> int:
    """The guard: the one place exit codes are decided for failures. A gate reaches it through
    `run`; a second entry point — a generator with a command line of its own — calls it with its
    own body, which parses its arguments with `Parser`'s kind, runs `preflight.check`, and only
    then imports what needs the declared libraries. `could_not_run` is the line that closes a
    failure: a gate's says that nothing was examined, a generator's that nothing was changed."""
    identity.declare(gate)  # first: every text, and the log's name, ask which gate this is
    output = Output(mode)
    try:
        return body(output)
    except ConfigurationFailure as failure:
        output.err(failure.broken.render())
        output.err(could_not_run())
    except Exception as exc:  # not fail-open: an unexpected failure exits 1, never 0
        # the BROKEN line first: in hook mode only the first stderr line reaches the user
        output.err(messages.c12_unexpected(f"{type(exc).__name__}: {exc}").render())
        output.err(could_not_run())
        output.err(traceback.format_exc().rstrip())
    finally:
        output.flush()
    return EXIT_BROKEN
