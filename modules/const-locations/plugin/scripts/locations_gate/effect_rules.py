"""The rules of const-locations' effect report (MODULE.md §13): W1 and W2 on one moment, a new governed
document of a kind whose home the create command derives, W3 on the plugin. The territory is read through
this module's own code, the index of policies, the matcher and the home rules of the command, never a second
time. The module has no gate and no severity, so no rule reads a red or a dial."""

from __future__ import annotations

import dataclasses
import os
import re
from collections.abc import Callable, Sequence
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import History, Judge, Moment, Outcome, Rule, Way
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.history import Session, ToolCall
from constitution_layer_kit.index import build_index
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from . import homes
from .model import HomeClass

SKILL = "new-document"
COMMAND = "new-document.sh"
# a shell command line that runs the create command: `sh` or `bash`, any flags, then a path to the script
RUNS_COMMAND = re.compile(r"(?:^|[\s;&|(])(?:sh|bash)\s+(?:-\S+\s+)*[\"']?\S*" + re.escape(COMMAND) + r"\b")
DRY_RUN = re.compile(r"(?:^|\s)--dry-run(?:\s|$)")
SEEN = ("Read", *ways.FILE_TOOLS)  # the tools after which a Write of the file is no creation

_TERRITORIES: dict[str, list[tuple[str, ...]]] = {}  # the answer of one run, by root
_HOMED: dict[str, bool] = {}  # by root and path


def homed_territories(root: Path) -> list[tuple[str, ...]]:
    """The territories of the project's policies at whose paths the create command derives a home: one
    pattern, a folder or a segment. A territory of a single path, or of several patterns, gets no home from
    the command, so a Write there is no bypass of it. A project with no readable dials claims nothing."""
    key = str(root)
    if key not in _TERRITORIES:
        found: list[tuple[str, ...]] = []
        loaded = load_dials(root)
        if loaded is not None and loaded.root_policy is not None:
            try:
                with Matcher() as matcher:
                    index = build_index(root, loaded, loaded.root_policy, matcher)
            except ConfigurationFailure:
                index = None
            if index is not None:
                found = [
                    policy.territory
                    for policy in index.policies.values()
                    if homes.rule_of(policy.territory).kind in (HomeClass.DIRECTORY, HomeClass.SEGMENT)
                ]
        _TERRITORIES[key] = found
    return _TERRITORIES[key]


def has_home(rel: str) -> bool:
    """Whether the create command would derive a home for the Markdown file `rel`, relative to the root: it
    lies in the territory of a policy that has one."""
    root = repo_root(Path(os.getcwd()).resolve())
    if root is None:
        return False
    key = f"{root}\0{rel}"
    if key not in _HOMED:
        territories = homed_territories(root)
        if not territories:
            _HOMED[key] = False
        else:
            with Matcher() as matcher:
                _HOMED[key] = any(matcher.match(territory, [rel]) for territory in territories)
    return _HOMED[key]


def runs_command(call: ToolCall) -> bool:
    """Whether a Bash call runs the create command and writes: a dry run writes nothing."""
    if call.name != "Bash":
        return False
    text = call.names()
    return RUNS_COMMAND.search(text) is not None and DRY_RUN.search(text) is None


def creating_write(history: History, call: ToolCall, session: Session) -> str | None:
    """The path, relative to the root, that a Write of `call` creates in a territory with a home, or None.
    A Write overwrites a file only after the session has read, written or edited it, as the platform
    requires, so a Write with none of those before it creates the file."""
    if call.name != "Write":
        return None
    rel = ways.relative(history, call.names(), call.cwd)
    if rel is None or not rel.lower().endswith(".md") or not has_home(rel):
        return None
    for earlier in session.calls():
        if earlier.id == call.id:
            return rel
        if earlier.name in SEEN and ways.relative(history, earlier.names(), earlier.cwd) == rel:
            return None
    return None


def where(call: ToolCall) -> str:
    return " ".join((call.names() or call.name).split())[:80]


def creations(history: History) -> list[Moment]:
    """W1: a Bash call that runs the create command is applied; a Write that creates a Markdown file in a
    territory with a home is missed by B6, the document born with no command."""
    found: list[Moment] = []
    for session in history.sessions:
        for call in session.calls():
            if runs_command(call):
                found.append(Moment(session.id, call.at, where(call), Outcome.APPLIED))
            else:
                rel = creating_write(history, call, session)
                if rel is not None:
                    found.append(Moment(session.id, call.at, rel, Outcome.MISSED, Way.B6))
    return found


def skill_before_creation() -> Rule:
    """W2, built by `ways.skill_before`, whose moment needs the history's root to place a path: the rule
    keeps the history of the run it finds in."""
    held: list[History] = []

    def at(call: ToolCall, session: Session) -> bool:
        return runs_command(call) or creating_write(held[-1], call, session) is not None

    base = ways.skill_before("W2", W2_TEXT, SKILL, at)

    def find(history: History) -> list[Moment]:
        held.append(history)
        try:
            return list(base.find(history))
        finally:
            held.pop()

    return dataclasses.replace(base, find=find)


def plugin_only() -> Rule:
    """W3, built by `ways.switch_off`, whose commits of the dials file are dropped: this module has no
    severity and no strictness to lower, so only the plugin's state is a moment."""
    base = ways.switch_off("W3", W3_TEXT)

    def find(history: History) -> list[Moment]:
        return [m for m in base.find(history) if not m.where.endswith(history.dials_file)]

    return dataclasses.replace(base, find=find)


W1_TEXT = "A governed document is born through the create command, never by writing the file by hand."
W2_TEXT = "Load new-document before a new document is created."
W3_TEXT = "The plugin stays enabled, so that its command, skills and grant are there."


def rules() -> Sequence[Rule]:
    w1: Callable[[History], list[Moment]] = creations
    return (
        Rule("W1", Judge.PATTERN, (Way.B6,), W1_TEXT, w1),
        skill_before_creation(),
        plugin_only(),
    )
