"""The entries: which tool each is, its input, and the hand-over to the shared guard. The count is an act:
its git calls have no clock, and its closing line says that no commit was counted."""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from constitution_layer_kit import cli, preflight
from constitution_layer_kit import messages as shared
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.events import read_event
from constitution_layer_kit.identity import HOOK_SECONDS, Identity
from constitution_layer_kit.model import KERNEL_KEYS, Mode
from constitution_layer_kit.output import Output

from . import counting, logs, messages, report, setup
from . import git as gitpart
from .model import STARTS

if TYPE_CHECKING:
    from constitution_layer_kit.effect import Rule

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


SESSION = Identity(
    namespace=NAMESPACE,
    gate="session-start",
    plugin_root=COUNT.plugin_root,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    until_installed="until then no session's start is logged, and its commits get no count",
)

SETUP = Identity(
    namespace=NAMESPACE,
    gate="setup-commit-log",
    plugin_root=COUNT.plugin_root,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    # the clause of C2 and C12.11 alone: messages._until leaves it off the setup's own failures
    until_installed="until then no hook of the commit log is written",
)

REPORT = Identity(
    namespace=NAMESPACE,
    gate="cost-report",
    plugin_root=COUNT.plugin_root,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    # the clause of C2 and C12.11 alone: messages._until leaves it off the report's own failures
    until_installed="until then no report or export is made",
)

EFFECT = Identity(
    namespace=NAMESPACE,
    gate="effect-report",
    plugin_root=COUNT.plugin_root,
    dials_file="constitution.yaml",
    kernel_keys=KERNEL_KEYS,
    hook_seconds=HOOK_SECONDS,
    # the clause of C2 alone, as a generator's: the shared runner closes its failures with its own line
    until_installed="until then the effect report is not made",
)


class CountParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.j6_11_misinvocation(message, messages.COUNT_USAGE))


class SetupParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.j6_11_misinvocation(message, messages.SETUP_USAGE))


class ReportParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.j6_11_misinvocation(message, messages.REPORT_USAGE))


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
    output.session = session  # the records of the output log name the session, as rule 12 asks
    return counting.run(output, counting.Scope(session), Path.cwd())


def count_main(argv: Sequence[str]) -> int:
    return cli.guarded(COUNT, Mode.ACT, lambda output: _count(argv, output), messages.j4_not_counted)


def _text(event: dict[object, object], name: str) -> str:
    value = event.get(name)
    if not isinstance(value, str):
        raise ConfigurationFailure(shared.c12_input(messages.detail_event_field(name)))
    return value


def _optional_text(event: dict[object, object], name: str) -> str:
    """A field the shared reader takes as optional: absent, or not a string, is the empty string."""
    value = event.get(name)
    return value if isinstance(value, str) else ""


def _event(text: str) -> dict[object, object]:
    try:
        loaded: object = json.loads(text)
    except ValueError as exc:
        raise ConfigurationFailure(shared.c12_input(shared.detail_not_json(str(exc)))) from exc
    if not isinstance(loaded, dict):
        raise ConfigurationFailure(shared.c12_input(shared.detail_not_an_object()))
    return loaded


def _start(argv: Sequence[str], output: Output) -> int:
    """Logs this session's start, and names the hooks of the commit log while one is missing. The clock is
    taken first, so that the start is the moment the hook ran."""
    started = int(time.time() * 1000)
    if argv:
        raise ConfigurationFailure(
            messages.j6_11_misinvocation(f"unexpected argument {argv[0]}", messages.START_USAGE)
        )
    preflight.check()
    text = sys.stdin.read()
    event = _event(text)
    # the records of the output log name the session and its transcript, as rule 12 asks, from here on
    output.stamp(read_event(io.StringIO(text)))
    session = _text(event, "session_id")
    source = _text(event, "source")
    transcript = _optional_text(event, "transcript_path")
    cwd = event.get("cwd")
    directory = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    common = gitpart.common_or_none(directory)
    if common is None:  # outside a git repository: nothing to log, nothing to say
        return 0
    named = os.environ.get("CLAUDE_PLUGIN_DATA")
    if named:  # kept for a run by hand, whose shell has no such variable
        logs.record_plugin_data(logs.folder_of(common), named)
    logs.append_line(
        logs.folder_of(common) / STARTS,
        {"session": session, "ms": started, "source": source, "transcript_path": transcript},
    )
    missing = gitpart.missing_hooks(directory)
    if missing:
        output.out(messages.j1_start_line(missing, str(SESSION.plugin_root)))
    return 0


def start_main(argv: Sequence[str]) -> int:
    return cli.guarded(SESSION, Mode.HOOK, lambda output: _start(argv, output), messages.j2_not_logged)


def _setup(argv: Sequence[str], output: Output) -> int:
    parser = SetupParser(prog=SETUP.gate, add_help=False, allow_abbrev=False)
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--remove", action="store_true")
    which.add_argument("--check", action="store_true")
    args = parser.parse_args(list(argv))
    preflight.check()
    if args.remove:
        return setup.run_remove(output, Path.cwd())
    if args.check:
        return setup.run_check(output, Path.cwd())
    return setup.run_set(output, Path.cwd())


def setup_main(argv: Sequence[str]) -> int:
    return cli.guarded(SETUP, Mode.ACT, lambda output: _setup(argv, output), messages.j8_setup_broken)


def _report(argv: Sequence[str], output: Output) -> int:
    parser = ReportParser(prog=REPORT.gate, add_help=False, allow_abbrev=False)
    parser.add_argument("range", nargs="?")
    which = parser.add_mutually_exclusive_group()
    for flag in ("--trailer", "--pr", "--notes"):
        which.add_argument(flag, metavar="RANGE")
    args = parser.parse_args(list(argv))
    exported = {flag: getattr(args, flag[2:]) for flag in ("--trailer", "--pr", "--notes")}
    if args.range is not None and any(value is not None for value in exported.values()):
        raise ConfigurationFailure(
            messages.j6_11_misinvocation(f"unexpected argument {args.range}", messages.REPORT_USAGE)
        )
    preflight.check()
    directory = Path.cwd()
    if args.trailer is not None:
        return report.run_trailer(output, directory, args.trailer)
    if args.pr is not None:
        return report.run_pr(output, directory, args.pr)
    if args.notes is not None:
        return report.run_notes(output, directory, args.notes)
    return report.run_report(output, directory, args.range)


def report_main(argv: Sequence[str]) -> int:
    """`--pr` and `--notes` change something, so they run as an act; the rest only read."""
    writes = any(held in ("--pr", "--notes") or held.startswith(("--pr=", "--notes=")) for held in argv)
    return cli.guarded(
        REPORT,
        Mode.ACT if writes else Mode.REPORT,
        lambda output: _report(argv, output),
        messages.j7_report_broken,
    )


def load_rules() -> Sequence[Rule]:
    # Necessary here, not at the top: the rules import the declared libraries, and only after the
    # preflight does a missing one become its designed message instead of a traceback.
    from . import effect_rules  # noqa: PLC0415

    return effect_rules.rules()
