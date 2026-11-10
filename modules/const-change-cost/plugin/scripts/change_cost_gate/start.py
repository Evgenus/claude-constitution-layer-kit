"""The entries: which tool each is, its input, and the hand-over to the shared guard. The count is an act:
its git calls have no clock, and its closing line says that no commit was counted."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from constitution_layer_kit import cli, preflight
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import KERNEL_KEYS, Mode
from constitution_layer_kit.output import Output

from . import counting, messages

NAMESPACE = "const-change-cost"
SESSION_VARIABLE = "CLAUDE_CODE_SESSION_ID"

COUNT = Identity(
    namespace=NAMESPACE,
    gate="count-costs",
    plugin_root=Path(__file__).resolve().parents[2],
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then no commit is counted",
)


class CountParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.j6_11_misinvocation(message))


def make_count_parser() -> CountParser:
    parser = CountParser(prog=COUNT.gate, add_help=False, allow_abbrev=False)
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--all", action="store_true")
    which.add_argument("--session", action="store_true")
    return parser


def _count(argv: Sequence[str], output: Output) -> int:
    args = make_count_parser().parse_args(list(argv))
    preflight.check()
    if args.all:
        return counting.run(output, counting.Scope(None), Path.cwd())
    session = os.environ.get(SESSION_VARIABLE, "")
    if not session:
        raise ConfigurationFailure(messages.j6_8_no_session())
    return counting.run(output, counting.Scope(session), Path.cwd())


def count_main(argv: Sequence[str]) -> int:
    return cli.guarded(COUNT, Mode.ACT, lambda output: _count(argv, output), messages.j4_not_counted)
