"""The texts of this module's own lines, notes and configuration failures, as functions with typed
parameters, each under the key the module's MODULE.md gives it; the texts every gate shares live in the
shared package's messages module.

A failure is one self-sufficient line, what failed and the exact fix, followed by the entry's closing line.
A fix of J6 closes with the clause of the entry's identity, if it has one: the count's is `until then no
commit is counted`. Every value taken from git, a transcript, ccusage, npm, the command line or the
environment goes through a shared helper: a path, a SHA and a session's id are shown whole and escaped, a
tool's first line is cut at 80 characters and escaped.
"""

from __future__ import annotations

from collections.abc import Sequence

from constitution_layer_kit import identity
from constitution_layer_kit.messages import echoed, escaped
from constitution_layer_kit.model import Broken

from .model import (
    CCUSAGE_SECONDS,
    HOOK_COMMIT,
    HOOK_MERGE,
    LOCK_SECONDS,
    NPM_SECONDS,
    PIN,
    SHA_SHOWN,
    Key,
    NotCounted,
    Reason,
)


def _ns() -> str:
    return identity.current().namespace


SETUP_GATE = "setup-commit-log"


def _until() -> str:
    """The closing clause of a failure's fix: the entry's own, and none for the setup, a generator whose
    clause closes the shared C2 alone."""
    current = identity.current()
    if current.gate == SETUP_GATE:
        return ""
    return f" — {current.until_installed}" if current.until_installed else ""


def _fail(key: Key, what: str, fix: str) -> Broken:
    return Broken(key, what, fix + _until())


def sha12(sha: str) -> str:
    return escaped(sha[:SHA_SHOWN])


def _seconds(seconds: float) -> str:
    return f"{seconds:g}"


# ---------------------------------------------------------------- the lines of the count


def j3_counted(counted: int, before: int, waiting: int, never: int) -> str:
    return (
        f"COUNTED: {counted} commit(s) counted now, {before} counted before, {waiting} waiting for a later"
        f" record, {never} never to be counted — cost-report.sh shows them"
    )


def j4_not_counted() -> str:
    return "BROKEN: the count could not run — no commit was counted"


# ---------------------------------------------------------------- the notes


def j5_1_unreadable_line(file: str, number: int, detail: str) -> str:
    return f"note: a log line cannot be read and is left out: {escaped(file)} line {number}: {echoed(detail)}"


def j5_2_lock_held() -> str:
    return (
        f"note: another count kept the lock on the file of counts for {_seconds(LOCK_SECONDS)} s — this pass"
        " counts nothing, and the next pass counts what is left"
    )


def j5_3_installed(data: str) -> str:
    return f"note: the pinned ccusage {PIN} was installed into {escaped(data)}"


# ---------------------------------------------------------------- why a log line cannot be read


def detail_not_json() -> str:
    return "it is not JSON"


def detail_not_an_object() -> str:
    return "it is not a JSON object"


def detail_field(name: str) -> str:
    return f"the field {name} is missing or has the wrong type"


# ---------------------------------------------------------------- configuration failures


def j6_1_no_node() -> Broken:
    return _fail(
        Key.J6_1,
        f"{_ns()} needs node on PATH, which runs ccusage",
        "install Node.js (https://nodejs.org/en/download)",
    )


def j6_2_no_npm(data: str) -> Broken:
    return _fail(
        Key.J6_2,
        f"{_ns()} needs npm on PATH to install the pinned ccusage into {escaped(data)}",
        "install Node.js, which brings npm (https://nodejs.org/en/download), then start a session again",
    )


def j6_3_no_ccusage(root: str) -> Broken:
    return _fail(
        Key.J6_3,
        f"{_ns()} needs ccusage {PIN}, which its package-lock.json pins, and found none under"
        f" {escaped(root)} or in the plugin's data folder",
        "start a Claude Code session in this project, whose start installs it, or run npm ci"
        f" --ignore-scripts in {escaped(root)}",
    )


def j6_4_other_version(found: str, where: str) -> Broken:
    return _fail(
        Key.J6_4,
        f"{_ns()} needs ccusage {PIN} and found {echoed(found)} under {escaped(where)}",
        "start a Claude Code session in this project, whose start installs the pinned one, or run npm ci"
        f" --ignore-scripts in {escaped(where)}",
    )


def detail_npm_line(line: str) -> str:
    return echoed(line)


def detail_npm_silent() -> str:
    return f"no answer in {_seconds(NPM_SECONDS)} s"


def j6_5_npm_failed(data: str, detail: str) -> Broken:
    return _fail(
        Key.J6_5,
        f"npm could not install the pinned ccusage into {escaped(data)}: {detail}",
        "repair what npm names — the network, the registry, the folder's rights — then start a session again",
    )


def detail_ccusage_exit(code: int, line: str) -> str:
    return f"exit {code}: {echoed(line)}"


def detail_ccusage_silent() -> str:
    return f"no answer in {_seconds(CCUSAGE_SECONDS)} s"


def detail_ccusage_output(detail: str) -> str:
    return f"output that is no session report: {echoed(detail)}"


def j6_6_no_count(session: str, detail: str, launcher: str) -> Broken:
    return _fail(
        Key.J6_6,
        f"ccusage gave no count for session {escaped(session)}: {detail}",
        "this is a defect of the count or of the installed ccusage, not of the repository; run"
        f" {escaped(launcher)} --version and report both to whoever maintains the plugin",
    )


def j6_7_no_repository(directory: str) -> Broken:
    return _fail(
        Key.J6_7,
        f"{escaped(directory)} is not inside a git repository",
        "run it inside the clone whose commits it counts",
    )


def j6_8_no_session() -> Broken:
    return _fail(
        Key.J6_8,
        "--session needs CLAUDE_CODE_SESSION_ID, which Claude Code sets in its hooks and its shell tool",
        "run it in a Claude Code session, or run count-costs.sh --all",
    )


def j6_9_no_folder(session: str, error: str) -> Broken:
    return _fail(
        Key.J6_9,
        f"the throwaway folder for session {escaped(session)} could not be made: {escaped(error)}",
        "free or repair the system's temporary directory, which TMPDIR names, then count again",
    )


COUNT_USAGE = "count-costs.sh [--all | --session]"
SETUP_USAGE = "setup-commit-log.sh [--remove | --check]"
START_USAGE = "session-start.sh with no argument and one SessionStart event on its standard input"


def j6_10_old_git(version: str) -> Broken:
    return _fail(
        Key.J6_10,
        f"{_ns()} needs git 2.54 or newer, which runs hooks set in its configuration, and found"
        f" {echoed(version)}",
        "install a newer git (https://git-scm.com/downloads), then run setup-commit-log.sh again",
    )


def j6_11_misinvocation(detail: str, usage: str) -> Broken:
    return _fail(Key.J6_11, f"misinvocation: {echoed(detail)}", f"run it as {usage}")


def j6_15_no_write(key: str, config: str, detail: str) -> Broken:
    return _fail(
        Key.J6_15,
        f"git could not write {escaped(key)} into {escaped(config)}: {echoed(detail)}",
        "repair what git names, such as the file's rights, then run setup-commit-log.sh --check",
    )


# ---------------------------------------------------------------- the start hook and the setup


def detail_event_field(name: str) -> str:
    return f"a SessionStart event must carry a string {name}"


def j1_start_line(keys: Sequence[str], root: str) -> str:
    return (
        f"{_ns()} (advisory): this clone logs no commit, so none of its commits is counted — git's"
        f" configuration lacks {' and '.join(keys)}. Load the skill {_ns()}:share-costs, tell the person,"
        f' and run sh "{escaped(root)}/scripts/setup-commit-log.sh" only when they ask.'
    )


def j2_not_logged() -> str:
    return f"BROKEN: {_ns()} could not log this session's start — its commits will get no count"


def j8_setup_broken() -> str:
    return "BROKEN: the setup could not run — setup-commit-log.sh --check shows what stands"


def j17_set(config: str) -> str:
    return (
        f"SET: {HOOK_COMMIT} on post-commit and {HOOK_MERGE} on post-merge written into {escaped(config)}"
        " — every commit of this clone is logged from now on"
    )


def j18_removed(config: str, folder: str) -> str:
    return (
        f"REMOVED: {HOOK_COMMIT} and {HOOK_MERGE} removed from {escaped(config)} — the logs and the counts"
        f" stay in {escaped(folder)}"
    )


def j19_check(missing: Sequence[str]) -> str:
    if not missing:
        return "CHECK: both hooks of the commit log stand in git's configuration"
    return f"CHECK: git's configuration lacks {' and '.join(missing)} — setup-commit-log.sh writes them"


# ---------------------------------------------------------------- a commit that has no kept line (J11)


def j11_1_no_log() -> str:
    return (
        "no line in the commit log: made before setup-commit-log.sh ran, by a tool that runs no git hook,"
        " or on a forge"
    )


def j11_2_no_session() -> str:
    return "the commit log names no session: made outside Claude Code"


def j11_3_no_start(session: str) -> str:
    return (
        f"session {escaped(session)} has no start in the start log: it started before the plugin was"
        " enabled, or in another folder"
    )


def j11_4_waiting(session: str) -> str:
    return (
        f"its window is not complete: no record of session {escaped(session)} is dated after the commit yet;"
        " a later pass counts it"
    )


def j11_5_no_transcript(session: str, path: str) -> str:
    return (
        f"no transcript of session {escaped(session)} stands at {escaped(path)}: swept by Claude Code's"
        " cleanup, or never kept"
    )


def j11_reason(not_counted: NotCounted) -> str:
    match not_counted.reason:
        case Reason.NO_LOG:
            return j11_1_no_log()
        case Reason.NO_SESSION:
            return j11_2_no_session()
        case Reason.NO_START:
            return j11_3_no_start(not_counted.session)
        case Reason.WAITING:
            return j11_4_waiting(not_counted.session)
        case Reason.NO_TRANSCRIPT:
            return j11_5_no_transcript(not_counted.session, not_counted.path)


def j11_not_counted(not_counted: NotCounted) -> str:
    return f"{sha12(not_counted.sha)}: not counted — {j11_reason(not_counted)}"
