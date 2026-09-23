"""The generator's entry: which tool this is, its command line, and the hand-over to the shared
guard. The act is loaded only after the preflight, because it needs the declared libraries."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from const_gate import cli, preflight
from const_gate.errors import ConfigurationFailure
from const_gate.identity import Identity
from const_gate.model import MetaType, Mode
from const_gate.output import Output

from . import messages
from .model import Request

GENERATOR = Identity(
    namespace="const-locations",
    gate="new-document",
    plugin_root=Path(__file__).resolve().parents[2],
    until_installed="until then nothing is created",  # a generator: no write passes, none is made
    until_fixed="until it is fixed nothing is created",
)


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.l5_usage(message))


def make_parser() -> Parser:
    parser = Parser(prog=GENERATOR.gate, add_help=False, allow_abbrev=False)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--stem")
    parser.add_argument("--title")
    parser.add_argument("--type", dest="meta_type", choices=[t.value for t in MetaType])
    parser.add_argument("--segment")
    parser.add_argument("--id", dest="doc_id")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _body(argv: Sequence[str], output: Output) -> int:
    args = make_parser().parse_args(list(argv))
    preflight.check()
    # Necessary here, not at the top: the act imports the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import creating  # noqa: PLC0415

    request = Request(
        kind=args.kind,
        stem=args.stem,
        title=args.title,
        meta_type=MetaType(args.meta_type) if args.meta_type else None,
        segment=args.segment,
        doc_id=args.doc_id,
        dry_run=args.dry_run,
    )
    return creating.act(output, request)


def main(argv: Sequence[str]) -> int:
    return cli.guarded(GENERATOR, Mode.ACT, lambda output: _body(argv, output), messages.l4_nothing_written)
