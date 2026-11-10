"""The module's rules of the effect report (template section 13): where each rule applies, and whether it
was applied, bypassed or missed. W2 and W4 are built by the helpers of `constitution_layer_kit.ways` with
what only this module knows, its skill and its moment; W1 and W3 are found by this module's own code, since
their evidence is the module's logs in git's common directory, which no helper reads. The module has no
dials file, so W4 keeps the plugin list's moment and drops the helper's moments for the dials file. Every
rule is judged by a pattern."""

from __future__ import annotations

import re
import shlex
from bisect import bisect_right
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.effect import History, Judge, Moment, Outcome, Rule, Way
from constitution_layer_kit.history import Session, ToolCall
from constitution_layer_kit.repository import git

from . import git as gitpart
from . import logs

W1_TEXT = "Every commit a session makes is logged in the clone's commit log."
W2_TEXT = "Load the skill share-costs before a pull request is opened or merged."
W3_TEXT = "A merge commit that lands counted commits carries the Change-Cost: trailer."
W4_TEXT = "The module stays on for the project."
SHARE_SKILL = "share-costs"
GIT_OPTIONS_WITH_ARGUMENT = ("-C", "-c", "--git-dir", "--work-tree", "--namespace")
MERGE_STOPS = ("--abort", "--continue", "--quit")
COMMIT_STOPS = ("--dry-run",)
OPENERS = {("gh", "pr", "create"), ("gh", "pr", "merge")}
MAIN_REFS = ("origin/HEAD", "main", "master")
TRAILER = re.compile(r"^Change-Cost:[ \t]+\S", re.MULTILINE)
WHERE_CHARS = 80


# ---------------------------------------------------------------- the words of a shell command


def _git_words(words: Sequence[str]) -> tuple[str, ...]:
    """A `git` command line with its options before the subcommand dropped; other commands as they are."""
    if not words or words[0] != "git":
        return tuple(words)
    kept, skip = ["git"], False
    for word in words[1:]:
        if skip:
            skip = False
        elif word in GIT_OPTIONS_WITH_ARGUMENT:
            skip = True
        elif not word.startswith("-") or len(kept) > 1:
            kept.append(word)
    return tuple(kept)


def commands(line: str) -> list[tuple[str, ...]]:
    """The commands of a shell line, each as its words, a `git` command with its leading options dropped."""
    found: list[tuple[str, ...]] = []
    for segment in ways.SEGMENT.split(line):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        while words and ways.ASSIGNMENT.match(words[0]):
            words = words[1:]
        if words:
            found.append(_git_words(words))
    return found


def commits(call: ToolCall) -> bool:
    """Whether a shell call runs `git commit`; `--dry-run` makes no commit."""
    if call.name != "Bash":
        return False
    return any(
        words[:2] == ("git", "commit") and not any(stop in words for stop in COMMIT_STOPS)
        for words in commands(call.names())
    )


def opens_or_merges(call: ToolCall, _session: Session) -> bool:
    """The moment of W2: a shell command that opens or merges a pull request, or merges a branch."""
    if call.name != "Bash":
        return False
    for words in commands(call.names()):
        if words[:3] in OPENERS:
            return True
        if words[:2] == ("git", "merge") and not any(stop in words for stop in MERGE_STOPS):
            return True
    return False


# ---------------------------------------------------------------- W1: a commit a session makes is logged


def _milliseconds(at: str) -> int | None:
    """A transcript's time, such as 2026-11-01T10:00:05.500Z, in milliseconds since the epoch."""
    try:
        moment = datetime.fromisoformat(at)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return round(moment.timestamp() * 1000)


def _where(call: ToolCall) -> str:
    return " ".join(call.names().split())[:WHERE_CHARS]


def logged_commits(history: History) -> list[Moment]:
    """W1: a moment for each shell call, not failed, that runs `git commit`: applied where the commit log
    holds a line of its session dated from the call's time and before the session's next such call, missed
    by B6 where it holds none. A line belongs to the last such call at or before its time, so one line makes
    one call applied; a call whose time cannot be read is no moment."""
    common = gitpart.common_or_none(history.root)
    if common is None:
        return []
    lines, notes = logs.read_commits(logs.folder_of(common))
    for note in notes:
        history.note(note)
    found: list[Moment] = []
    for session in history.sessions:
        calls = sorted(
            (
                (moment, call)
                for call in session.calls()
                if commits(call) and not call.failed
                for moment in [_milliseconds(call.at)]
                if moment is not None
            ),
            key=lambda held: held[0],
        )
        starts = [held[0] for held in calls]
        owned: set[int] = set()
        for line in lines:
            index = bisect_right(starts, line.ms) - 1
            if line.session == session.id and index >= 0:
                owned.add(index)
        for index, (_, call) in enumerate(calls):
            if index in owned:
                found.append(Moment(session.id, call.at, _where(call), Outcome.APPLIED))
            else:
                found.append(Moment(session.id, call.at, _where(call), Outcome.MISSED, Way.B6))
    return found


# ---------------------------------------------------------------- W3: the trailer on a merge of counts


def _main_branch(root: Path) -> str | None:
    for ref in MAIN_REFS:
        if git(["rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], root).returncode == 0:
            return ref
    return None


def _out(args: list[str], root: Path) -> str | None:
    done = git(args, root)
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else None


def _carries_trailer(message: str) -> bool:
    """Whether the last paragraph of a commit message holds a `Change-Cost:` trailer."""
    paragraphs = re.split(r"\n[ \t]*\n", message.strip())
    return bool(paragraphs) and TRAILER.search(paragraphs[-1]) is not None


def merges_that_land_counts(history: History) -> list[Moment]:
    """W3: a moment for each first-parent merge commit of the main branch in the window whose merged side
    holds a commit with a kept line: applied where its message's last paragraph holds the `Change-Cost:`
    trailer, missed by B6 where it does not. A merge that lands no counted commit is no moment."""
    root = history.root
    common = gitpart.common_or_none(root)
    branch = _main_branch(root)
    if common is None or branch is None:
        return []
    kept, notes = logs.read_counts(logs.folder_of(common))
    for note in notes:
        history.note(note)
    counted = {line.sha for line in kept}
    args = ["log", "--first-parent", "--merges", "--format=%H %cI"]
    if history.since:
        args.append(f"--since={history.since} 00:00:00")
    listed = _out([*args, branch], root)
    found: list[Moment] = []
    for row in reversed((listed or "").splitlines()):
        sha, _, at = row.partition(" ")
        side = _out(["rev-list", sha, "--not", f"{sha}^1"], root)
        if side is None or not counted.intersection(side.split()):
            continue
        message = _out(["log", "-1", "--format=%B", sha], root) or ""
        if _carries_trailer(message):
            found.append(Moment("", at, sha[:12], Outcome.APPLIED))
        else:
            found.append(Moment("", at, sha[:12], Outcome.MISSED, Way.B6))
    return found


# ---------------------------------------------------------------- W4: the module stays on


def plugin_enabled(history: History) -> list[Moment]:
    """W4: the plugin as the plugin list shows it for the project. The helper of way B2 also looks at the
    dials file for a dial lowered; the module has no dials, so its moments for that file are dropped."""
    held = ways.switch_off("W4", W4_TEXT).find(history)
    return [moment for moment in held if not moment.where.endswith(f" {history.dials_file}")]


def rules() -> Sequence[Rule]:
    return (
        Rule("W1", Judge.PATTERN, (Way.B6,), W1_TEXT, logged_commits),
        ways.skill_before("W2", W2_TEXT, SHARE_SKILL, opens_or_merges),
        Rule("W3", Judge.PATTERN, (Way.B6,), W3_TEXT, merges_that_land_counts),
        Rule("W4", Judge.PATTERN, (Way.B2,), W4_TEXT, plugin_enabled),
    )
