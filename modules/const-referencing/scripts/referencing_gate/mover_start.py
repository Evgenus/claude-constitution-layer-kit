"""The mover's entry: which tool this is, its command line, and the hand-over to the shared
guard. The acts are loaded only after the preflight, because they need the declared libraries."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from const_gate import cli, preflight
from const_gate.errors import ConfigurationFailure
from const_gate.identity import Identity
from const_gate.model import Mode
from const_gate.output import Output

from . import messages
from .closing import Closing

MOVER = Identity(
    namespace="const-referencing",
    gate="move-document",
    plugin_root=Path(__file__).resolve().parents[2],
    until_installed="until then nothing is moved",  # a generator: no write passes, none is made
    until_fixed="until it is fixed do not move documents with it",  # true before and after a move
)


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.v5_usage(message))


def make_parser() -> Parser:
    parser = Parser(prog=MOVER.gate, add_help=False, allow_abbrev=False)
    parser.add_argument("--moved", action="store_true")
    parser.add_argument("--ids", action="store_true")
    parser.add_argument("paths", nargs="*")
    return parser


def _body(argv: Sequence[str], output: Output, closing: Closing) -> int:
    args = make_parser().parse_args(list(argv))
    wanted = 0 if args.ids else 2
    if len(args.paths) != wanted or (args.ids and args.moved):
        raise ConfigurationFailure(messages.v5_usage(f"{len(args.paths)} path(s) given"))
    preflight.check()
    # Necessary here, not at the top: the acts import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import moving  # noqa: PLC0415

    old, new = args.paths if args.paths else ("", "")
    return moving.act(output, moving.Request(args.ids, args.moved, old, new), closing)


def main(argv: Sequence[str]) -> int:
    closing = Closing()  # knows, when a failure is closed, whether anything had been changed by then
    return cli.guarded(MOVER, Mode.ACT, lambda output: _body(argv, output, closing), closing)
