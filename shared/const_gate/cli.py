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
from collections.abc import Callable, Mapping, Sequence
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
class Argument:
    """A module's own flag on the one parser, scan mode only, one value each: `--since <ref>`."""

    flag: str
    metavar: str


Values = Mapping[str, str | None]  # a module's flags by flag, None where not given


@dataclass(frozen=True, slots=True)
class Modes:
    """The module's two modes. Each returns an exit code. A module with flags of its own gives
    `scan_with`, which receives their values, and `scan` is then not called."""

    hook: Callable[[Output, TextIO], int]
    scan: Callable[[Output, Path], int]
    scan_with: Callable[[Output, Path, Values], int] | None = None


class Parser(argparse.ArgumentParser):
    def __init__(self, usage: str, prog: str) -> None:
        super().__init__(prog=prog, add_help=False, allow_abbrev=False)  # --sc is not --scan
        self.usage_line = usage

    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.c12_invocation(message, self.usage_line))


def usage(arguments: Sequence[Argument]) -> str:
    return messages.USAGE + "".join(f" [{a.flag} <{a.metavar}>]" for a in arguments)


def make_parser(arguments: Sequence[Argument] = ()) -> Parser:
    parser = Parser(usage(arguments), identity.current().gate)
    parser.add_argument(SCAN_FLAG, nargs="?", const=".", default=None, metavar="DIR")
    for argument in arguments:
        parser.add_argument(argument.flag, dest=argument.flag, default=None, metavar=argument.metavar)
    return parser


def main(
    argv: Sequence[str],
    output: Output,
    load_modes: Callable[[], Modes],
    arguments: Sequence[Argument] = (),
) -> int:
    parser = make_parser(arguments)
    args = parser.parse_args(list(argv))
    values: dict[str, str | None] = {a.flag: getattr(args, a.flag) for a in arguments}
    if args.scan is None:
        given = [flag for flag, value in values.items() if value is not None]
        if given:
            raise ConfigurationFailure(
                messages.c12_invocation(f"{given[0]} applies to --scan", parser.usage_line)
            )
    preflight.check()
    modes = load_modes()  # the module's code is imported after the preflight: it needs the libraries
    if args.scan is not None:
        if modes.scan_with is not None:
            return modes.scan_with(output, Path(args.scan), values)
        return modes.scan(output, Path(args.scan))
    return modes.hook(output, sys.stdin)


def run(
    argv: Sequence[str],
    gate: Identity,
    load_modes: Callable[[], Modes],
    arguments: Sequence[Argument] = (),
) -> int:
    """A gate's entry: the entry point says which gate this is, how to load its two modes, and
    which flags of its own the scan takes — none for a gate that takes only --scan."""
    mode = Mode.SCAN if any(a.startswith(SCAN_FLAG) for a in argv) else Mode.HOOK
    return guarded(gate, mode, lambda output: main(argv, output, load_modes, arguments))


def guarded(
    gate: Identity,
    mode: Mode,
    body: Callable[[Output], int],
    could_not_run: Callable[[], str] = messages.c11_broken_count,
) -> int:
    """The guard: the one place exit codes are decided for failures. A gate reaches it through
    `run`; a second entry point — a generator with a command line of its own — calls it with its
    own body, which parses its arguments with `Parser`'s kind, runs `preflight.check`, and only
    then imports what needs the declared libraries; a session-start printer does the same, in hook
    mode, with no arguments to parse and a closing line saying the gate's state is not said.
    `could_not_run` is the line that closes a
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
