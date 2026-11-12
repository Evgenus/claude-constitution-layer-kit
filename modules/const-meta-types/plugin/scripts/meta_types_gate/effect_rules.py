"""The rules of const-meta-types' effect report (its module document, §13), all judged by a pattern, each
built by one helper of `constitution_layer_kit.ways` with what only this module knows: its claimed territory
and its skill. Its one dial that loosens, `severity`, the helper judges alone. The territory is read as the
hook reads it, through the shared index of policies and the shared matcher, never a second time."""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Callable, Sequence
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import History, Moment, Rule
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.history import Session, ToolCall
from constitution_layer_kit.index import build_index
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

SKILL = "choose-meta-type"
SCRIPT = "check-governed-document.sh"
_TERRITORIES: dict[Path, list[tuple[str, ...]]] = {}  # the territories of one run, by root
_CLAIMED: dict[str, bool] = {}  # the answers of one run, by root and path


def _territories(root: Path) -> list[tuple[str, ...]]:
    """The root policy's territory and the territory of every policy it holds, on the current tree. A
    project with no dials file, no readable root policy or a malformed file claims nothing."""
    if root not in _TERRITORIES:
        found: list[tuple[str, ...]] = []
        try:
            loaded = load_dials(root)
            if loaded is not None and loaded.root_policy is not None:
                with Matcher() as matcher:
                    index = build_index(root, loaded, loaded.root_policy, matcher)
                found = [index.root_territory, *(policy.territory for policy in index.policies.values())]
        except ConfigurationFailure:
            found = []
        _TERRITORIES[root] = found
    return _TERRITORIES[root]


def claimed(rel: str) -> bool:
    """Whether some policy's territory, or the root policy's, claims the file `rel`, relative to the root:
    the hook's own notion of claimed territory, read on the current tree."""
    root = repo_root(Path(os.getcwd()).resolve())
    if root is None:
        return False
    key = f"{root}\0{rel}"
    if key not in _CLAIMED:
        territories = [territory for territory in _territories(root) if territory]
        with Matcher() as matcher:
            _CLAIMED[key] = any(matcher.match(territory, [rel]) for territory in territories)
    return _CLAIMED[key]


def writes_a_claimed_document(history_of: Callable[[], History]) -> Callable[[ToolCall, Session], bool]:
    """The moment of W5: a Write of a Markdown file in claimed territory."""

    def at(call: ToolCall, _session: Session) -> bool:
        if call.name != "Write":
            return False
        rel = ways.relative(history_of(), call.names(), call.cwd)
        return rel is not None and rel.lower().endswith(".md") and claimed(rel)

    return at


def skill_before_governed_write() -> Rule:
    """W5, built by `ways.skill_before`, whose moment needs the history's root to place a path: the rule
    keeps the history of the run it finds in."""
    held: list[History] = []
    base = ways.skill_before("W5", W5_TEXT, SKILL, writes_a_claimed_document(lambda: held[-1]))

    def find(history: History) -> list[Moment]:
        held.append(history)
        try:
            return list(base.find(history))
        finally:
            held.pop()

    return dataclasses.replace(base, find=find)


W1_TEXT = "A Markdown document in claimed territory is changed only where the guard examines it."
W2_TEXT = "The guard of claimed territory stays on, at severity block."
W3_TEXT = "After a red of the guard, the document is fixed as the finding teaches, not walked around."
W4_TEXT = "After a red, the skill it names is loaded before the document is touched again."
W5_TEXT = "Load choose-meta-type before writing a governed document."
W6_TEXT = "The main branch holds no document in claimed territory that the guard's scan finds red."


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, claimed),
        # the module's one dial that takes strictness away is `severity`, which the helper judges alone:
        # the commit that adds the namespace lowers nothing, so a project may adopt the module at warn
        ways.switch_off("W2", W2_TEXT),
        ways.after_red("W3", W3_TEXT),
        ways.skill_after_red("W4", W4_TEXT),
        skill_before_governed_write(),
        ways.escape("W6", W6_TEXT, script=SCRIPT),
    )
