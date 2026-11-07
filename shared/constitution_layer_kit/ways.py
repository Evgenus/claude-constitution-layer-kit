"""The ways a rule of the effect report fails, as rules a module builds by naming what only it knows
(kit-shared-gate-code §1, `ways`, and §2, item 10; template §13).

A module's ``effect_rules.py`` calls one of the nine helpers for each rule of its section "Effect" and passes
its territory, its loosened dial, its moment, its scan arguments or its skill; the helper gives back the
``effect.Rule``. Every helper judges by a pattern, save ``reader_rule``, which only finds the moments the
reader judges. All of them read heuristically (limit 18 of §4 of kit-shared-gate-code): a shell command is
read for the Markdown paths it seems to change, a skill loaded earlier in a session counts for a later
moment of it, and the escape check runs the current plugin's scan over an older tree.

What a helper cannot read it says in a note line (``Rule.find`` has no output of its own, so the note goes
through ``History.note``), and counts no moment for it: a failed program is never a moment, and never a crash.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import tempfile
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

import yaml

from . import judge, messages
from .effect import History, Judge, Moment, Outcome, Rule, Way
from .history import AssistantText, HookRun, HumanTurn, Session, ToolCall

WRITES = ("Write", "Edit")  # the platform's tools that write one file by its `file_path`, as the hooks match
FILE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
ACTS = (*FILE_TOOLS, "Bash")  # the tool calls that change something
GIT_SECONDS = 60.0
LIST_SECONDS = 60.0
CLONE_SECONDS = 600.0
SCAN_SECONDS = 300.0
COMMIT_CAP = 50  # the most commits of the main branch the escape check scans
SEGMENT = re.compile(r"&&|\|\||[;|\n]")
REDIRECT = re.compile(r"(?<![0-9&>])>>?\s*([\"']?)([^\s\"';|&<>()]+)\1")
PYTHON_WRITE = re.compile(
    r"""Path\(\s*(["'])([^"']+)\1\s*\)\s*\.\s*write_(?:text|bytes)\(|open\(\s*(["'])([^"']+)\3\s*,\s*["'][wax]"""
)
IN_PLACE = re.compile(r"-[A-Za-z]*i|--in-place")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
WORKTREE = re.compile(r"/\.claude/worktrees/[^/]+/")
ASK = re.compile(r'"permissionDecision"\s*:\s*"ask"')
LOAD = re.compile(r"load the skill ([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+)")


# ---------------------------------------------------------------- H1: what a shell command changes


def shell_changes(command: str) -> list[str]:
    """The Markdown paths a shell command seems to change, in the order met, each once: a redirect `>` or
    `>>`, `tee`, `sed -i`, `perl -pi`, `git mv` and `mv` (both paths), `git rm` and `rm`, `cp` (its last
    path), and a Python `Path("x.md").write_text(` or `open("x.md", "w"`. A pattern's reading, not a
    shell's: a quoted `>` or a path built in a variable is misread (limit 18 of §4)."""
    found = [match[2] for match in REDIRECT.finditer(command)]
    found.extend(match[2] or match[4] for match in PYTHON_WRITE.finditer(command))
    for segment in SEGMENT.split(command):
        found.extend(_segment_paths(_words(segment)))
    return _markdown(found)


def _words(segment: str) -> list[str]:
    try:
        words = shlex.split(segment)
    except ValueError:
        words = segment.split()
    while words and ASSIGNMENT.match(words[0]):
        words = words[1:]
    return words


def _segment_paths(words: Sequence[str]) -> list[str]:
    """The paths one command of a shell line takes, as the command's own arguments say."""
    if not words:
        return []
    name, rest = words[0], list(words[1:])
    if name == "git":
        return _git_paths(rest)
    plain = [word for word in rest if not word.startswith("-")]
    if name in ("tee", "mv", "rm"):
        return plain
    if name == "cp":
        return plain[-1:]
    if name in ("sed", "perl") and any(IN_PLACE.match(word) for word in rest if word.startswith("-")):
        return plain
    return []


def _git_paths(rest: Sequence[str]) -> list[str]:
    options = [word for word in rest if not word.startswith("-")]
    if len(options) < 2 or options[0] not in ("mv", "rm"):
        return []
    return options[1:]


def _markdown(paths: Iterable[str]) -> list[str]:
    seen: dict[str, None] = {}
    for path in paths:
        if path.lower().endswith(".md"):
            seen.setdefault(path)
    return list(seen)


# ---------------------------------------------------------------- the paths of a project


def _under(top: str, full: str) -> str | None:
    if full == top:
        return ""
    return full[len(top) + 1 :] if full.startswith(top + os.sep) else None


def _run_git(args: Sequence[str], cwd: str | Path, seconds: float = GIT_SECONDS) -> str | None:
    """The standard output of one git call, or None when git failed, was not found or ran out of time."""
    try:
        done = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=seconds,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


@cache
def _checkout_of(cwd: str) -> tuple[str, str] | None:
    """The top of the checkout a folder lies in, and the common git directory it shares, while the folder
    exists."""
    if not os.path.isdir(cwd):
        return None
    top = _run_git(["rev-parse", "--show-toplevel"], cwd)
    common = _run_git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    if top is None or common is None:
        return None
    return os.path.realpath(top.strip()), os.path.realpath(common.strip())


def relative(history: History, path: str, cwd: str = "") -> str | None:
    """A path as the project's root sees it, or None for a path outside the project. A path below
    `.claude/worktrees/<name>/` of the root is read as the same path in the root; a path in another checkout
    of the project is read from that checkout's top, found by git from the call's folder while it exists."""
    if not path:
        return None
    base = cwd or str(history.root)
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(base, path))
    top = str(history.root)
    marker = WORKTREE.search(full)
    if marker is not None and full[: marker.start()] == top:
        return full[marker.end() :]
    found = _under(top, full)
    if found is not None:
        return found
    checkout = _checkout_of(cwd) if cwd else None
    root_common = _checkout_of(top)
    if checkout is None or root_common is None or checkout[1] != root_common[1]:
        return None
    return _under(checkout[0], full)


def _subject(history: History, call: ToolCall) -> str:
    """What a call acts on, as one comparable string: the file relative to the root, else as written."""
    name = call.names()
    return relative(history, name, call.cwd) or name


def _on_file(history: History, act: ToolCall, red: ToolCall) -> bool:
    """Whether an act is on the red's file: a write of it, or a shell command that names it."""
    if act.name in FILE_TOOLS:
        return _subject(history, act) == _subject(history, red)
    if act.name == "Bash":
        command = act.names()
        return _subject(history, red) in command or red.names() in command
    return False


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _where(call: ToolCall) -> str:
    return " ".join((call.names() or call.name).split())[:80]


# ---------------------------------------------------------------- H2: path bypass (B1)


def path_bypass(key: str, text: str, in_territory: Callable[[str], bool]) -> Rule:
    """B1. A moment for each Write or Edit of a Markdown file in the territory, applied where a run of the
    module's hook examined the call and bypassed where none did, and for each shell command that seems to
    change a Markdown file in the territory, bypassed. `in_territory` takes a path relative to the project's
    root and reads the territory on the current tree; a path outside the project is no moment."""

    def find(history: History) -> list[Moment]:
        return [m for session in history.sessions for m in _path_moments(history, session, in_territory)]

    return Rule(key, Judge.PATTERN, (Way.B1,), text, find)


def _path_moments(
    history: History, session: Session, in_territory: Callable[[str], bool]
) -> Iterator[Moment]:
    examined = {call.id for call, _ in history.runs(session) if call is not None}
    for call in session.calls():
        if call.name in WRITES:
            rel = relative(history, call.names(), call.cwd)
            if rel is not None and rel.lower().endswith(".md") and in_territory(rel):
                if call.id in examined:
                    yield Moment(session.id, call.at, rel, Outcome.APPLIED)
                else:
                    yield Moment(session.id, call.at, rel, Outcome.BYPASSED, Way.B1)
        elif call.name == "Bash":
            for path in shell_changes(call.names()):
                rel = relative(history, path, call.cwd)
                if rel is not None and in_territory(rel):
                    yield Moment(session.id, call.at, rel, Outcome.BYPASSED, Way.B1)


# ---------------------------------------------------------------- H3: switch-off (B2)


def switch_off(
    key: str,
    text: str,
    loosened: Callable[[Mapping[str, object], Mapping[str, object]], bool] | None = None,
    default_severity: str = "block",
) -> Rule:
    """B2. A moment for the module's plugin in `claude plugin list --json` for this project, applied where it
    is enabled and bypassed where it is listed and disabled; and one for each commit in the window that
    changes the module's namespace in the dials file, bypassed where `severity` went from `block` to `warn`
    — an absent `severity` read as `default_severity`, the module's default — or where `loosened(old, new)`
    says so, with the namespace's two values as mappings, and applied otherwise. A commit that adds the
    namespace is no lowering of its severity: a project may adopt a module at warn. What cannot be read is a
    note."""

    def find(history: History) -> list[Moment]:
        return [*_plugin_moments(history, key), *_dials_moments(history, key, loosened, default_severity)]

    return Rule(key, Judge.PATTERN, (Way.B2,), text, find)


def _plugin_entries(history: History, key: str) -> list[Mapping[str, object]]:
    try:
        done = subprocess.run(
            ["claude", "plugin", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=LIST_SECONDS,
            check=False,
            env={name: value for name, value in os.environ.items() if name not in judge.USAGE_BILLED},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        history.note(messages.u7_no_plugin_list(key, type(exc).__name__))
        return []
    try:
        listed: object = json.loads(done.stdout)
    except ValueError:
        listed = None
    if done.returncode != 0 or not isinstance(listed, list):
        history.note(messages.u7_no_plugin_list(key, f"exit {done.returncode}, no JSON list"))
        return []
    top = str(history.root)
    mine: list[Mapping[str, object]] = [
        e for e in listed if isinstance(e, dict) and _is_here(e, history.namespace, top)
    ]
    if not mine:
        history.note(messages.u7_not_listed(key))
    return mine


def _is_here(entry: Mapping[str, object], namespace: str, top: str) -> bool:
    name, project = entry.get("id"), entry.get("projectPath")
    if not isinstance(name, str) or name.partition("@")[0] != namespace:
        return False
    return not isinstance(project, str) or os.path.realpath(project) == top


def _plugin_moments(history: History, key: str) -> list[Moment]:
    found: list[Moment] = []
    for entry in _plugin_entries(history, key):
        where = str(entry.get("id"))
        if entry.get("enabled") is True:
            found.append(Moment("", _now(), where, Outcome.APPLIED))
        else:
            found.append(Moment("", _now(), where, Outcome.BYPASSED, Way.B2))
    return found


def _dials_moments(
    history: History,
    key: str,
    loosened: Callable[[Mapping[str, object], Mapping[str, object]], bool] | None,
    default_severity: str,
) -> list[Moment]:
    name = history.dials_file
    if not name:
        return []
    args = ["log", "--format=%H %cI"]
    if history.since:
        args.append(f"--since={history.since}")
    listed = _run_git([*args, "--", name], history.root)
    if listed is None:
        history.note(messages.u7_no_history(key, "git log failed"))
        return []
    found: list[Moment] = []
    failed: list[str] = []
    for line in reversed(listed.splitlines()):
        commit, _, at = line.partition(" ")
        try:
            moment = _dials_change(history, commit, at, loosened, default_severity)
        except yaml.YAMLError as exc:
            failed.append(type(exc).__name__)
            continue
        if moment is not None:
            found.append(moment)
    if failed:
        history.note(messages.u7_no_history(key, f"{len(failed)} commit(s) with {failed[0]}"))
    return found


def _dials_change(
    history: History,
    commit: str,
    at: str,
    loosened: Callable[[Mapping[str, object], Mapping[str, object]], bool] | None,
    default_severity: str,
) -> Moment | None:
    name = history.dials_file
    old = _namespace_values(_run_git(["show", f"{commit}^:{name}"], history.root), history.namespace)
    new = _namespace_values(_run_git(["show", f"{commit}:{name}"], history.root), history.namespace)
    if old == new:
        return None
    where = f"{commit[:12]} {name}"
    went_down = (
        bool(old)
        and old.get("severity", default_severity) == "block"
        and new.get("severity", default_severity) == "warn"
    )
    if went_down or (loosened is not None and loosened(old, new)):
        return Moment("", at, where, Outcome.BYPASSED, Way.B2)
    return Moment("", at, where, Outcome.APPLIED)


def _namespace_values(text: str | None, namespace: str) -> dict[str, object]:
    if text is None:
        return {}
    loaded: object = yaml.safe_load(text)
    value = loaded.get(namespace) if isinstance(loaded, dict) else None
    return {str(k): v for k, v in value.items()} if isinstance(value, dict) else {}


# ---------------------------------------------------------------- H4 and H5: after a red (B3, B5)


def _is_red(run: HookRun) -> bool:
    return run.blocked or ASK.search(run.text) is not None


def _reds(history: History, session: Session) -> Iterator[tuple[int, ToolCall | None, HookRun]]:
    """Each red run of the module's hooks in a session: where it stands among the events, the call it
    examined, and the run."""
    calls = {call.id: call for call in session.calls()}
    for index, event in enumerate(session.events):
        if isinstance(event, HookRun) and history.ours(event) and _is_red(event):
            yield index, calls.get(event.tool_use_id), event


def _after(session: Session, index: int, call: ToolCall | None) -> list[object]:
    """The events after a red: after the run and after the call it examined."""
    start = index
    if call is not None:
        start = max(start, session.events.index(call))
    return list(session.events[start + 1 :])


def _next_act(events: Sequence[object]) -> tuple[ToolCall | None, list[object]]:
    """The first act in the events before a human turn, and the events after it; none if a human turn, or
    the end, comes first."""
    for position, event in enumerate(events):
        if isinstance(event, HumanTurn):
            return None, []
        if isinstance(event, ToolCall) and event.name in ACTS:
            return event, list(events[position + 1 :])
    return None, []


def _later_on_file(history: History, events: Sequence[object], red: ToolCall) -> ToolCall | None:
    for event in events:
        if isinstance(event, ToolCall) and event.name in ACTS and _on_file(history, event, red):
            return event
    return None


def _writes(_red: ToolCall, act: ToolCall) -> bool:
    """The default `fixed_by`: it is asked of an act on the red's file, and a write of it is the fix."""
    return act.name in FILE_TOOLS


def after_red(key: str, text: str, fixed_by: Callable[[ToolCall, ToolCall], bool] = _writes) -> Rule:
    """B3. A moment for each red run of the module's hook (a blocked run, or an `ask` verdict in its output)
    on a call that writes a file, when an act follows before a human turn. The next act on the red's file
    is the answer: applied where `fixed_by(red_call, act)` holds, by default a write of the file, and
    bypassed B3 where it is a shell command naming the file or a `git mv` of it, or where `fixed_by` fails.
    An act on another file first does not decide: the first later act on the file in the session does, and
    none leaves the red standing, bypassed. `fixed_by` is asked only of an act on the red's file."""

    def find(history: History) -> list[Moment]:
        found: list[Moment] = []
        for session in history.sessions:
            for index, call, run in _reds(history, session):
                moment = _after_red_moment(history, session, index, call, run, fixed_by)
                if moment is not None:
                    found.append(moment)
        return found

    return Rule(key, Judge.PATTERN, (Way.B3,), text, find)


def _after_red_moment(
    history: History,
    session: Session,
    index: int,
    call: ToolCall | None,
    run: HookRun,
    fixed_by: Callable[[ToolCall, ToolCall], bool],
) -> Moment | None:
    if call is None or call.name not in FILE_TOOLS:
        return None
    first, later = _next_act(_after(session, index, call))
    if first is None:
        return None
    target = first if _on_file(history, first, call) else _later_on_file(history, later, call)
    where = _subject(history, call)
    if target is not None and fixed_by(call, target):
        return Moment(session.id, run.at, where, Outcome.APPLIED)
    return Moment(session.id, run.at, where, Outcome.BYPASSED, Way.B3)


def skill_after_red(key: str, text: str) -> Rule:
    """B5. A moment for each red run of the module's hook whose text names `load the skill <plugin>:<skill>`:
    applied where a Skill call naming that skill comes after the red and before the next act on the red's
    file (before the next act of any kind where the red names no file call), missed B5 otherwise."""

    def find(history: History) -> list[Moment]:
        found: list[Moment] = []
        for session in history.sessions:
            for index, call, run in _reds(history, session):
                named = LOAD.search(run.text)
                if named is not None:
                    found.append(_skill_moment(history, session, index, call, run, named[1], named[2]))
        return found

    return Rule(key, Judge.PATTERN, (Way.B5,), text, find)


def _skill_moment(
    history: History,
    session: Session,
    index: int,
    call: ToolCall | None,
    run: HookRun,
    plugin: str,
    skill: str,
) -> Moment:
    where = _subject(history, call) if call is not None else run.hook
    for event in _after(session, index, call):
        if isinstance(event, ToolCall):
            if _skill_named(event, f"{plugin}:{skill}"):
                return Moment(session.id, run.at, where, Outcome.APPLIED)
            if event.name in ACTS and (call is None or _on_file(history, event, call)):
                break
    return Moment(session.id, run.at, where, Outcome.MISSED, Way.B5)


def _skill_named(call: ToolCall, wanted: str) -> bool:
    """Whether a call is the Skill tool naming `wanted`, written `<plugin>:<skill>` or as the bare skill."""
    given = call.input.get("skill")
    if call.name != "Skill" or not isinstance(given, str):
        return False
    if ":" in given and ":" in wanted:
        return given == wanted
    return given.rpartition(":")[2] == wanted.rpartition(":")[2]


# ---------------------------------------------------------------- H6: a skill before the act (B5)


def skill_before(key: str, text: str, skill: str, at: Callable[[ToolCall, Session], bool]) -> Rule:
    """B5. A moment for each tool call for which `at(call, session)` holds: applied where a Skill call naming
    `skill` (`<plugin>:<skill>` or the bare name) came earlier in the same session, missed B5 otherwise. A
    skill loaded once stays in context until the session is compacted, so a load earlier in the session
    counts for every later moment (limit 18 of §4)."""

    def find(history: History) -> list[Moment]:
        found: list[Moment] = []
        for session in history.sessions:
            loaded = False
            for call in session.calls():
                if _skill_named(call, skill):
                    loaded = True
                elif at(call, session):
                    if loaded:
                        found.append(Moment(session.id, call.at, _where(call), Outcome.APPLIED))
                    else:
                        found.append(Moment(session.id, call.at, _where(call), Outcome.MISSED, Way.B5))
        return found

    return Rule(key, Judge.PATTERN, (Way.B5,), text, find)


# ---------------------------------------------------------------- H7: escape (B4)


def _default_scan(_commit: str) -> list[str]:
    return ["--scan"]


def escape(
    key: str,
    text: str,
    scan_argv: Callable[[str], list[str]] = _default_scan,
    script: str = "",
) -> Rule:
    """B4. A moment for each first-parent commit of the main branch (`origin/HEAD`, else `main`, else
    `master`) in the window, the last 50 of them: the module's own scan wrapper run with `scan_argv(commit)`
    in a throwaway `git clone --shared` of the project made at that commit, in a temporary folder outside
    the project. Exit 0 is applied, exit 2 bypassed B4, anything else a note and no moment. The wrapper is
    `script`, a file name below the plugin's `scripts` folder, or else the first script of the module's
    hooks file that lies there. The scan is the current plugin's, run over an older tree (limit 18 of §4)."""

    def find(history: History) -> list[Moment]:
        return _escape_moments(history, key, scan_argv, script)

    return Rule(key, Judge.PATTERN, (Way.B4,), text, find)


def _main_branch(root: Path) -> str | None:
    for ref in ("origin/HEAD", "main", "master"):
        if _run_git(["rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], root) is not None:
            return ref
    return None


def _wrapper(history: History, script: str) -> Path | None:
    if history.plugin_root is None:
        return None
    names = [script] if script else sorted(history.scripts, key=lambda n: (not n.startswith("check-"), n))
    for name in names:
        path = history.plugin_root / "scripts" / name
        if name.endswith(".sh") and path.is_file():
            return path
    return None


def _window_commits(history: History, branch: str) -> list[tuple[str, str]]:
    args = ["log", "--first-parent", "--format=%H %cI"]
    if history.since:
        args.append(f"--since={history.since}")
    listed = _run_git([*args, branch], history.root)
    lines = (listed or "").splitlines()
    return [(line.partition(" ")[0], line.partition(" ")[2]) for line in lines]


def _escape_moments(
    history: History, key: str, scan_argv: Callable[[str], list[str]], script: str
) -> list[Moment]:
    branch, wrapper = _main_branch(history.root), _wrapper(history, script)
    if branch is None or wrapper is None:
        history.note(messages.u7_no_scan(key, "no main branch" if branch is None else "no scan script"))
        return []
    commits = _window_commits(history, branch)
    if len(commits) > COMMIT_CAP:
        history.note(messages.u7_capped(key, COMMIT_CAP, len(commits)))
    commits = list(reversed(commits[:COMMIT_CAP]))
    if not commits:
        return []
    with tempfile.TemporaryDirectory() as folder:
        clone, data = Path(folder) / "clone", Path(folder) / "data"
        data.mkdir()
        cloned = _run_git(
            ["clone", "--shared", "--no-checkout", "--quiet", str(history.root), str(clone)],
            folder,
            CLONE_SECONDS,
        )
        if cloned is None:
            history.note(messages.u7_no_scan(key, "git clone failed"))
            return []
        return _scan_commits(history, key, clone, data, wrapper, scan_argv, commits)


def _scan_commits(
    history: History,
    key: str,
    clone: Path,
    data: Path,
    wrapper: Path,
    scan_argv: Callable[[str], list[str]],
    commits: Sequence[tuple[str, str]],
) -> list[Moment]:
    found: list[Moment] = []
    failed: list[tuple[str, str]] = []
    env = {**os.environ, "CLAUDE_PLUGIN_DATA": str(data), "CLAUDE_PROJECT_DIR": str(clone)}
    for commit, at in commits:
        code = _scan_at(clone, wrapper, commit, scan_argv(commit), env)
        if code == 0:
            found.append(Moment("", at, commit[:12], Outcome.APPLIED))
        elif code == 2:
            found.append(Moment("", at, commit[:12], Outcome.BYPASSED, Way.B4))
        else:
            failed.append((commit[:12], "the scan could not run" if code is None else f"exit {code}"))
    if failed:
        history.note(messages.u7_scan_failed(key, len(failed), failed[0][0], failed[0][1]))
    return found


def _scan_at(clone: Path, wrapper: Path, commit: str, argv: list[str], env: Mapping[str, str]) -> int | None:
    """The exit code of the scan on the clone at a commit; None where the checkout or the scan did not run."""
    checkout = ["-c", "core.hooksPath=/dev/null", "checkout", "-q", "-f", "--detach", commit]
    if _run_git(checkout, clone) is None:
        return None
    try:
        done = subprocess.run(
            ["sh", str(wrapper), *argv],
            cwd=clone,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=SCAN_SECONDS,
            env=dict(env),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    finally:
        _run_git(["clean", "-fdxq"], clone)
    return done.returncode


# ---------------------------------------------------------------- H8 and H9: the visible form, the reader


def shape(key: str, text: str, owed: Callable[[str], bool], shown: Callable[[str], bool]) -> Rule:
    """B6. A moment for each text of the assistant for which `owed(text)` holds, applied where `shown(text)`
    holds and missed B6 otherwise."""

    def find(history: History) -> list[Moment]:
        found: list[Moment] = []
        for session in history.sessions:
            for event in session.events:
                if isinstance(event, AssistantText) and owed(event.text):
                    where = " ".join(event.text.split())[:60]
                    if shown(event.text):
                        found.append(Moment(session.id, event.at, where, Outcome.APPLIED))
                    else:
                        found.append(Moment(session.id, event.at, where, Outcome.MISSED, Way.B6))
        return found

    return Rule(key, Judge.PATTERN, (Way.B6,), text, find)


def reader_rule(
    key: str,
    text: str,
    at: Callable[[Session], Iterable[int]],
    ways: tuple[Way, ...] = (Way.B6,),
) -> Rule:
    """A rule the reader judges: one moment for each event index `at(session)` gives, with the events
    around it as its excerpt. The reader gives the outcome, with `--reader` alone."""

    def find(history: History) -> list[Moment]:
        found: list[Moment] = []
        for session in history.sessions:
            for index in at(session):
                event = session.events[index]
                found.append(
                    Moment(
                        session.id,
                        event.at,
                        type(event).__name__,
                        excerpt=history.excerpt(session, index),
                    )
                )
        return found

    return Rule(key, Judge.READER, ways, text, find)
