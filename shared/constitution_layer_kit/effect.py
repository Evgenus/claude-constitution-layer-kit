"""The effect report: at each moment where one of a module's rules applies, whether it was applied, bypassed
or missed (template §13; kit-shared-gate-code §1, `effect`, and §2, item 10).

A module's plugin ships the code that finds its rules' moments, as a list of ``Rule``; its entry
``effect-report.sh``, in its scripts folder, hands that list to ``run``. This runner reads the evidence —
the transcripts the module's log names, and those of a folder ``--transcripts`` names; the module's log —
counts each rule's moments, and prints the report. A rule judged by a pattern finds each moment with its
outcome; a rule judged by a reader finds each moment with an excerpt, and the reader of ``judge`` gives the
outcome, with ``--reader`` alone. The two judges' counts stand on lines of their own and are never added
together, and counts are summed per module and never across modules. The report blocks nothing, sets no
threshold and is never red: it exits 0 once printed, and 1 when it could not run.

Run as ``python3 -m constitution_layer_kit.effect``, this file is the shared entry: it asks Claude Code for
the plugins enabled for the project in the current folder, runs the entry of each one that ships it with the
same flags, and prints their reports in turn. It names no module.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from . import identity, judge, messages, preflight
from .cli import Parser, guarded
from .dials import load_dials
from .errors import ConfigurationFailure
from .history import HookRun, LogRecord, Session, ToolCall, read_log, read_transcript, script_of
from .identity import Identity
from .model import EXIT_BROKEN, Mode
from .output import Output
from .pipeline import route_log
from .repository import repo_root

ENTRY = ("scripts", "effect-report.sh")  # a plugin's entry, by its parts below the plugin's root
FLAGS = ("--reader", "--transcripts", "--since")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
LIST_SECONDS = 60.0  # the plugin list's clock
REPORT_SECONDS = 3600.0  # one plugin's report, a run of its reader included
EXCERPT_EVENTS = 6  # events on each side of a moment in its excerpt
EXCERPT_CHARS = 400  # characters of one event in an excerpt


class Judge(StrEnum):
    PATTERN = "pattern"
    READER = "reader"


class Way(StrEnum):
    """The six ways a rule fails, as template §13 names them."""

    B1 = "B1"  # path bypass: a file of the gate's territory changed with no hook of the gate examining it
    B2 = "B2"  # switch-off: the module off for a clone, its severity lowered, or a dial loosened
    B3 = "B3"  # workaround after a red: the next act another path to the same end, not the taught fix
    B4 = "B4"  # escape: the invariant broken on the main branch anyway
    B5 = "B5"  # skill skipped: the act at the skill's moment with no load of the skill before it
    B6 = "B6"  # shape missed: the rule's visible form absent where it asks for it


class Outcome(StrEnum):
    APPLIED = "applied"
    BYPASSED = "bypassed"
    MISSED = "missed"


@dataclass(frozen=True, slots=True)
class Moment:
    """One place where a rule applies. A pattern's moment carries its outcome, and a way unless it is
    applied; a reader's carries the excerpt the reader judges, and no outcome."""

    session: str
    at: str
    where: str
    outcome: Outcome | None = None
    way: Way | None = None
    excerpt: str = ""


@dataclass(frozen=True, slots=True)
class Rule:
    key: str  # the row's key in the module's section "Effect"
    judge: Judge
    ways: tuple[Way, ...]  # the ways it can fail
    text: str  # the rule as the reader is given it
    find: Callable[[History], Iterable[Moment]]


@dataclass(frozen=True, slots=True)
class History:
    """What a rule's code reads: the project's sessions, the module's log, and which hook runs are its."""

    root: Path
    scripts: frozenset[str]  # the file names of the scripts the module's hooks run
    sessions: tuple[Session, ...]
    log: tuple[LogRecord, ...]  # the records of hook and scan runs, within the window
    since: str
    namespace: str = ""  # the module's name: its dials namespace, as the plugin list names it
    dials_file: str = ""  # the dials file's name below the project's root
    plugin_root: Path | None = None  # the module's plugin folder
    notes: list[str] = field(default_factory=list)  # the lines a rule's code asks the report to print

    def note(self, line: str) -> None:
        """A line for the report, printed after the counts of the rule that asked: a note, never a finding."""
        self.notes.append(line)

    def runs(self, session: Session) -> list[tuple[ToolCall | None, HookRun]]:
        """The module's hook runs of a session, each with the tool call it examined, where it names one."""
        calls = {call.id: call for call in session.calls()}
        return [(calls.get(run.tool_use_id), run) for run in session.hook_runs() if self.ours(run)]

    def ours(self, run: HookRun) -> bool:
        """Whether a hook run is the module's: its script is one the module's hooks run, or its text names the
        module's plugin, as a run whose command names no script does. The one test every helper uses."""
        return run.script in self.scripts or bool(run.plugin and run.plugin == self.namespace)

    def log_only(self) -> list[LogRecord]:
        """The log's hook records of the sessions no transcript holds: they count where no transcript does
        (kit-shared-gate-code §1, `effect`)."""
        held = {session.id for session in self.sessions}
        return [r for r in self.log if r.mode == Mode.HOOK.value and r.session and r.session not in held]

    def excerpt(self, session: Session, at: int) -> str:
        """The events around the event at index `at`, one line each, for the reader."""
        lo, hi = max(0, at - EXCERPT_EVENTS), at + EXCERPT_EVENTS + 1
        return "\n".join(_line(event) for event in session.events[lo:hi])


def _line(event: object) -> str:
    if isinstance(event, ToolCall):
        said = f"tool {event.name}: {event.names() or json.dumps(event.input, ensure_ascii=False)}"
    elif isinstance(event, HookRun):
        said = f"hook {event.hook} {event.script}{' blocked' if event.blocked else ''}: {event.text}"
    else:
        said = f"{type(event).__name__}: {getattr(event, 'text', '')}"
    return said[:EXCERPT_CHARS]


@dataclass(frozen=True, slots=True)
class Flags:
    reader: bool
    transcripts: Path | None
    since: str


def parse(argv: Sequence[str], usage: str) -> Flags:
    parser = Parser(usage, "effect-report")
    parser.add_argument("--reader", action="store_true")
    parser.add_argument("--transcripts", default=None, metavar="DIR")
    parser.add_argument("--since", default="", metavar="DATE")
    args = parser.parse_args(list(argv))
    if args.since and not _is_date(args.since):
        raise ConfigurationFailure(messages.u5_since(args.since))
    folder = Path(args.transcripts) if args.transcripts else None
    if folder is not None and not folder.is_dir():
        raise ConfigurationFailure(messages.u5_transcripts(args.transcripts))
    return Flags(bool(args.reader), folder, str(args.since))


def _is_date(text: str) -> bool:
    """A calendar date written YYYY-MM-DD: the form, and a day the calendar has."""
    if DATE.fullmatch(text) is None:
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


USAGE = "[--reader] [--transcripts <dir>] [--since <YYYY-MM-DD>]"


def run(argv: Sequence[str], gate: Identity, rules: Callable[[], Sequence[Rule]]) -> int:
    """A module's effect entry: which gate it is, and how to load its rules once the libraries are there."""
    return guarded(gate, Mode.REPORT, lambda output: _report(argv, output, rules), messages.u5_could_not_run)


def _report(argv: Sequence[str], output: Output, rules: Callable[[], Sequence[Rule]]) -> int:
    flags = parse(argv, USAGE)
    preflight.check()
    loaded = list(rules())
    _refuse_two_keys(loaded)
    history = gather(output, flags)
    version, model = (
        judge.ready() if flags.reader and any(r.judge is Judge.READER for r in loaded) else ("", "")
    )
    unread = sum(session.unread for session in history.sessions)
    output.out(messages.u1_headline(len(loaded), len(history.sessions), flags.since, unread))
    if not history.sessions:
        output.out(messages.u1_no_session())
    for record in disagreements(history):
        output.out(messages.u3_disagree(record.path, record.session, record.at))
    for rule in loaded:
        model = _rule_lines(output, rule, history, flags.reader, model)
        for line in history.notes:
            output.out(line)
        history.notes.clear()
    if version:
        output.out(messages.u4_reader(model or "the default model", version))
    return 0


def _refuse_two_keys(rules: Sequence[Rule]) -> None:
    keys = Counter(rule.key for rule in rules)
    twice = [key for key, count in keys.items() if count > 1]
    if twice:
        raise ValueError(f"two rules share the key {twice[0]!r}: a defect of the module's effect code")


def _rule_lines(output: Output, rule: Rule, history: History, reader: bool, model: str) -> str:
    moments = [m for m in rule.find(history) if not history.since or m.at >= history.since]
    if rule.judge is Judge.PATTERN:
        for moment in moments:
            _check(rule, moment)
        output.out(_counted(rule, moments))
        return model
    if not reader:
        output.out(messages.u2_not_judged(rule.key, len(moments)))
        return model
    judged: list[Moment] = []
    for moment in moments:
        outcome, model = judge.verdict(rule.text, moment.excerpt, model)
        if outcome is not None:
            judged.append(Moment(moment.session, moment.at, moment.where, Outcome(outcome)))
    output.out(_counted(rule, judged, len(moments)))
    if len(judged) < len(moments):
        output.out(messages.u2_no_verdict(rule.key, len(moments) - len(judged)))
    return model


def _check(rule: Rule, moment: Moment) -> None:
    if moment.outcome is None:
        raise ValueError(f"rule {rule.key}: a pattern's moment carries its outcome")
    if (moment.outcome is Outcome.APPLIED) != (moment.way is None):
        raise ValueError(f"rule {rule.key}: a way stands with a bypass or a miss, and with nothing else")
    if moment.way is not None and moment.way not in rule.ways:
        raise ValueError(f"rule {rule.key}: way {moment.way} is not one of the rule's ways")


def _counted(rule: Rule, moments: Sequence[Moment], total: int | None = None) -> str:
    outcomes = Counter(m.outcome for m in moments)
    ways = Counter(m.way for m in moments if m.way is not None)
    by = ", ".join(f"{way.value} {ways[way]}" for way in Way if ways[way])
    counts = [outcomes[Outcome.APPLIED], outcomes[Outcome.BYPASSED], outcomes[Outcome.MISSED]]
    return messages.u2_counted(
        rule.key, rule.judge.value, len(moments) if total is None else total, counts, by
    )


def gather(output: Output, flags: Flags) -> History:
    """The evidence: the dials' log, the transcripts it names and those of the folder, within the window."""
    root = repo_root(Path(os.getcwd()).resolve())
    if root is None:
        raise ConfigurationFailure(messages.c12_no_repo(os.getcwd()))
    dials = load_dials(root)
    log_dir: Path | None = None
    if dials is not None:
        route_log(output, root, dials)
        log_dir = root / dials.log_dir if dials.log_dir else None
    data = os.environ.get("CLAUDE_PLUGIN_DATA", "")
    log_dir = log_dir or (Path(data) if data else None)
    namespace = identity.current().namespace
    log = read_log(log_dir, namespace) if log_dir is not None else []
    log = [r for r in log if r.mode in (Mode.HOOK.value, Mode.SCAN.value) and r.at >= flags.since]
    # one file read once, however it is named: by the log's absolute path and by a folder given relatively
    paths = {Path(r.transcript).resolve() for r in log if r.transcript}
    if flags.transcripts is not None:
        paths.update(found.resolve() for found in flags.transcripts.rglob("*.jsonl"))
    sessions = [s for s in map(read_transcript, sorted(paths)) if s is not None and _ours(s, root)]
    gate = identity.current()
    return History(
        root,
        _scripts(gate.plugin_root),
        tuple(sessions),
        tuple(log),
        flags.since,
        gate.namespace,
        gate.dials_file,
        gate.plugin_root,
    )


def _ours(session: Session, root: Path) -> bool:
    top = str(root.resolve())
    return any(
        os.path.realpath(cwd) == top or os.path.realpath(cwd).startswith(top + os.sep) for cwd in session.cwds
    )


def _scripts(plugin_root: Path) -> frozenset[str]:
    """The file names of the scripts the module's hooks run, read from its hooks file."""
    try:
        loaded: object = json.loads((plugin_root / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return frozenset()
    found: set[str] = set()
    stack: list[object] = [loaded]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            # a hook is `"command": "sh"` with the script in `"args"`, or the whole line in `"command"`
            args = item.get("args")
            words = [item.get("command"), *(args if isinstance(args, list) else [])]
            found.update(script_of(word) for word in words if isinstance(word, str) and script_of(word))
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return frozenset(found)


def disagreements(history: History) -> list[LogRecord]:
    """The log's hook records that name a file or a command which no run of the module's hooks in their
    session's transcript examined, in a session a transcript holds; the transcript's count stands."""
    named: dict[str, set[str]] = {}
    for session in history.sessions:
        named.setdefault(session.id, set()).update(
            call.names() for call, _ in history.runs(session) if call is not None
        )
    return [
        r
        for r in history.log
        if r.mode == Mode.HOOK.value and r.path and r.session in named and r.path not in named[r.session]
    ]


# ---------------------------------------------------------------- the shared entry


def main_all(argv: Sequence[str]) -> int:
    """Every enabled plugin's effect report for the project in the current folder, in turn."""
    try:
        parse(argv, USAGE)  # refuse what no entry takes, as an entry would
        plugins = enabled_plugins(Path(os.getcwd()).resolve())
    except ConfigurationFailure as failure:
        print(failure.broken.render(), file=sys.stderr)
        print(messages.u6_could_not_run(), file=sys.stderr)
        return EXIT_BROKEN
    reports = [(name, path.joinpath(*ENTRY)) for name, path in plugins if path.joinpath(*ENTRY).is_file()]
    print(messages.u6_headline(len(reports), len(plugins)), flush=True)
    for name, entry in reports:
        try:
            code = subprocess.run(["sh", str(entry), *argv], timeout=REPORT_SECONDS, check=False).returncode
        except subprocess.TimeoutExpired:
            code = EXIT_BROKEN
        if code != 0:
            print(messages.u6_report_failed(name, code), flush=True)
    return 0


def enabled_plugins(top: Path) -> list[tuple[str, Path]]:
    """The plugins enabled for the project at `top`, by `claude plugin list --json`, each once."""
    try:
        done = subprocess.run(
            ["claude", "plugin", "list", "--json"], capture_output=True, text=True, timeout=LIST_SECONDS
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConfigurationFailure(messages.u6_no_list(f"{type(exc).__name__}: {exc}")) from exc
    try:
        listed: object = json.loads(done.stdout)
    except ValueError as exc:
        raise ConfigurationFailure(messages.u6_no_list(f"exit {done.returncode}, no JSON list")) from exc
    if done.returncode != 0 or not isinstance(listed, list):
        raise ConfigurationFailure(messages.u6_no_list(f"exit {done.returncode}, no JSON list"))
    found: dict[str, Path] = {}
    for entry in listed:
        if not isinstance(entry, dict) or entry.get("enabled") is not True:
            continue
        name, where, project = entry.get("id"), entry.get("installPath"), entry.get("projectPath")
        if not isinstance(name, str) or not isinstance(where, str):
            continue
        if isinstance(project, str) and os.path.realpath(project) != str(top):
            continue  # enabled for another project
        found.setdefault(name, Path(where))
    return sorted(found.items())


if __name__ == "__main__":
    sys.exit(main_all(sys.argv[1:]))
