"""The command line and the single guard.

Parameters are parsed with argparse, whose own default is to exit 2 on bad usage; 2 is
reserved for findings, so a misinvoked hook must not read as "blocked, here is the
feedback" having produced no verdict. The parser here raises a configuration failure
instead, and the guard turns every configuration failure, and every unexpected exception,
into exit 1 — never 0.
"""

from __future__ import annotations

import argparse
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from . import messages, preflight
from .errors import ConfigurationFailure
from .model import EXIT_BROKEN, GATE, Mode
from .output import Output


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.c12_invocation(message))


def make_parser() -> Parser:
    parser = Parser(prog=GATE, description="Write-time guard of claimed territory. With no arguments: read a"
                                           " PreToolUse event on stdin and judge the write.")
    parser.add_argument("--scan", nargs="?", const=".", default=None, metavar="DIR",
                        help="check every Markdown document in claimed territory of the repository"
                             " containing DIR (default: the current directory)")
    return parser


def main(argv: Sequence[str], output: Output) -> int:
    args = make_parser().parse_args(list(argv))
    preflight.check()
    from . import modes                 # imported after the preflight: it needs the declared libraries
    if args.scan is not None:
        output.mode = Mode.SCAN
        return modes.scan_mode(output, Path(args.scan))
    return modes.hook_mode(output, sys.stdin)


def run(argv: Sequence[str]) -> int:
    """The guard: the one place exit codes are decided for failures."""
    output = Output(Mode.HOOK)
    try:
        return main(argv, output)
    except ConfigurationFailure as failure:
        output.err(failure.broken.render())
    except Exception as exc:            # not fail-open: an unexpected failure exits 1, never 0
        output.err(traceback.format_exc().rstrip())
        output.err(messages.c12_unexpected(f"{type(exc).__name__}: {exc}").render())
    output.err(messages.broken_count())
    return EXIT_BROKEN
