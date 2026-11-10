"""The two entries: which tool each is, its input, and the hand-over to the shared guard. The
generator's act is loaded only after the preflight, because it needs the declared libraries; the
grant reads no library beyond the standard one before it answers, and its preflight runs once a call
is its own command."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from constitution_layer_kit import cli, preflight
from constitution_layer_kit import messages as shared_messages
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import KERNEL_KEYS, MetaType, Mode
from constitution_layer_kit.output import Output

from . import granting, messages
from .model import Request

if TYPE_CHECKING:
    from constitution_layer_kit.effect import Rule

GENERATOR = Identity(
    namespace="const-locations",
    gate="new-document",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then nothing is created",  # a generator: no write passes, none is made
    until_fixed="until it is fixed nothing is created",
)

GRANT = Identity(
    namespace="const-locations",
    gate="grant-new-document",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then the command asks for approval as any other command does",
    until_fixed="until it is fixed the command asks for approval as any other command does",
)

EFFECT = Identity(
    namespace="const-locations",
    gate="effect-report",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then the effect report is not made",
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


def load_rules() -> Sequence[Rule]:
    # Necessary here, not at the top: the rules import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import effect_rules  # noqa: PLC0415

    return effect_rules.rules()


def main(argv: Sequence[str]) -> int:
    return cli.guarded(GENERATOR, Mode.ACT, lambda output: _body(argv, output), messages.l4_nothing_written)


def _grant(argv: Sequence[str], output: Output) -> int:
    if argv:
        raise ConfigurationFailure(shared_messages.c12_invocation(" ".join(argv), messages.l8_usage()))
    # The root the platform gives the hook: the same text it put in the skill's command line.
    return granting.grant(output, sys.stdin, os.environ.get("CLAUDE_PLUGIN_ROOT", ""))


def grant_main(argv: Sequence[str]) -> int:
    return cli.guarded(GRANT, Mode.HOOK, lambda output: _grant(argv, output), messages.l7_not_granted)
