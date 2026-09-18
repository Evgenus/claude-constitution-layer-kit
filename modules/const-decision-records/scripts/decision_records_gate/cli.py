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
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from . import messages, preflight
from .errors import ConfigurationFailure
from .model import EXIT_BROKEN, GATE, Mode
from .output import Output

SCAN_FLAG = "--scan"


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.c12_invocation(message))


def make_parser() -> Parser:
    parser = Parser(prog=GATE, add_help=False)
    parser.add_argument(SCAN_FLAG, nargs="?", const=".", default=None, metavar="DIR")
    return parser


def main(argv: Sequence[str], output: Output) -> int:
    args = make_parser().parse_args(list(argv))
    preflight.check()
    from . import modes  # imported after the preflight: it needs the declared libraries

    if args.scan is not None:
        return modes.scan_mode(output, Path(args.scan))
    return modes.hook_mode(output, sys.stdin)


def run(argv: Sequence[str]) -> int:
    """The guard: the one place exit codes are decided for failures."""
    output = Output(Mode.SCAN if any(a.startswith(SCAN_FLAG) for a in argv) else Mode.HOOK)
    try:
        return main(argv, output)
    except ConfigurationFailure as failure:
        output.err(failure.broken.render())
        output.err(messages.c11_broken_count())
    except Exception as exc:  # not fail-open: an unexpected failure exits 1, never 0
        # the BROKEN line first: in hook mode only the first stderr line reaches the user
        output.err(messages.c12_unexpected(f"{type(exc).__name__}: {exc}").render())
        output.err(messages.c11_broken_count())
        output.err(traceback.format_exc().rstrip())
    finally:
        output.flush()
    return EXIT_BROKEN
