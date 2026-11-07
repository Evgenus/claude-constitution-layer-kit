"""The module's rules of the effect report (template section 13): where each rule applies, and whether it
was applied, bypassed or missed. W1, W3, W4 and W5 are built by the helpers of `constitution_layer_kit.ways`
with what only this module knows; W2 is found by its own code, since its red is a turn's end and no call.
Every rule is judged by a pattern."""

from __future__ import annotations

import shlex
from collections.abc import Mapping, Sequence

from constitution_layer_kit import ways
from constitution_layer_kit.effect import History, Judge, Moment, Outcome, Rule, Way
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.history import HookRun, HumanTurn, Session, ToolCall

from . import dials
from .model import TaskCloseDials

W1_TEXT = "The module stays on and its coverage map stays as wide as it was."
W2_TEXT = "After a dirty tree is reported at the end of a turn, the work is committed, or stashed."
W3_TEXT = "Every change that landed on the main branch passed the range check."
W4_TEXT = "Load the skill commit-before-edit before the first edit after each human turn."
W5_TEXT = "Load the skill close-task before a pull request or a branch is merged."
COMMIT_SKILL = "commit-before-edit"
CLOSE_SKILL = "close-task"
EDITS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
MERGERS = {("gh", "pr", "merge"), ("git", "merge")}
MERGE_STOPS = ("--abort", "--continue", "--quit")
GIT_OPTIONS_WITH_ARGUMENT = ("-C", "-c", "--git-dir", "--work-tree", "--namespace")
TREE_READS = ("status", "diff", "log", "show", "add", "ls-files", "rev-parse")
PLAIN_READS = ("cd", "ls", "cat", "pwd")
ANSWERS = ("commit", "stash")


def _read(values: Mapping[str, object]) -> TaskCloseDials | None:
    """The namespace as this module's own reader sees it; None where the reader refuses it."""
    try:
        return dials.parse(values)
    except ConfigurationFailure:
        return None


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """A dial loosened: a pair of the coverage map gone, or a pair that lost a pattern of its code."""
    before, after = _read(old), _read(new)
    if before is None or after is None:
        return False
    kept = {pair.name: set(pair.code) for pair in after.coverage}
    for pair in before.coverage:
        if pair.name not in kept or not set(pair.code) <= kept[pair.name]:
            return True
    return False


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


def merges(call: ToolCall, _session: Session) -> bool:
    """The moment of W5: a shell command that merges a pull request or a branch."""
    if call.name != "Bash":
        return False
    for words in commands(call.names()):
        if words[:3] == ("gh", "pr", "merge") or words[:2] == ("git", "merge"):
            if not any(stop in words for stop in MERGE_STOPS):
                return True
    return False


# ---------------------------------------------------------------- W2: the answer to a red at a turn's end


def _is_neutral(words: tuple[str, ...]) -> bool:
    if words[0] == "git":
        return len(words) > 1 and words[1] in TREE_READS
    return words[0] in PLAIN_READS


def _answer(call: ToolCall) -> Outcome | None:
    """What a shell command, or another act, says of the red: applied where it commits or stashes, bypassed
    where it is anything else, none where it only looks at the tree or stages it."""
    if call.name != "Bash":
        return Outcome.BYPASSED
    found = commands(call.names())
    if any(len(words) > 1 and words[0] == "git" and words[1] in ANSWERS for words in found):
        return Outcome.APPLIED
    if all(_is_neutral(words) for words in found):
        return None
    return Outcome.BYPASSED


def _turn_end_red(history: History, event: object) -> HookRun | None:
    """The module's turn-end hook run that blocked the turn."""
    if (
        isinstance(event, HookRun)
        and event.blocked
        and event.script in history.scripts
        and event.hook.startswith("Stop")
    ):
        return event
    return None


def after_turn_end_red(history: History) -> list[Moment]:
    """W2: for each red of the turn-end hook, the first act before a human turn that is more than a look at
    the tree or a staging of it: a commit or a stash is applied, any other act bypassed by B3. A human turn
    first, or no act, is no moment."""
    found: list[Moment] = []
    for session in history.sessions:
        for index, event in enumerate(session.events):
            run = _turn_end_red(history, event)
            if run is not None:
                moment = _decide(session, index, run)
                if moment is not None:
                    found.append(moment)
    return found


def _decide(session: Session, index: int, run: HookRun) -> Moment | None:
    for later in session.events[index + 1 :]:
        if isinstance(later, HumanTurn):
            return None
        if isinstance(later, ToolCall) and later.name in ways.ACTS:
            outcome = _answer(later)
            if outcome is Outcome.APPLIED:
                return Moment(session.id, run.at, "turn end", outcome)
            if outcome is Outcome.BYPASSED:
                return Moment(session.id, run.at, "turn end", outcome, Way.B3)
    return None


# ---------------------------------------------------------------- W4: the first edit after a human turn


def first_edit(call: ToolCall, session: Session) -> bool:
    """The moment of W4: a call of a tool that edits a file, when no call of one came since the last human
    turn."""
    if call.name not in EDITS:
        return False
    since: list[object] = []
    for event in session.events:
        if event is call:
            break
        if isinstance(event, HumanTurn):
            since = []
        else:
            since.append(event)
    return not any(isinstance(event, ToolCall) and event.name in EDITS for event in since)


def range_check(commit: str) -> list[str]:
    """The scan's arguments at a commit of the main branch: that change alone."""
    return ["--scan", "--change", commit]


def rules() -> Sequence[Rule]:
    return (
        ways.switch_off("W1", W1_TEXT, loosened),
        Rule("W2", Judge.PATTERN, (Way.B3,), W2_TEXT, after_turn_end_red),
        ways.escape("W3", W3_TEXT, range_check, "check-task-close.sh"),
        ways.skill_before("W4", W4_TEXT, COMMIT_SKILL, first_edit),
        ways.skill_before("W5", W5_TEXT, CLOSE_SKILL, merges),
    )
