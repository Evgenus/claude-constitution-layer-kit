"""The rules of const-language's effect report (its module document, §13): W1 to W6 judged by a pattern, each
built by one helper of `constitution_layer_kit.ways` with what only this module knows — its territory, the
dials it counts as loosened, its skill — and W7 judged by a reader. The territory is read through this
module's own dials reader and matcher, never a second time."""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import History, Moment, Rule
from constitution_layer_kit.history import AssistantText, HumanTurn, Session, ToolCall
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from . import dials as own_dials
from .model import DEFAULT_GRADE_CEILING, DEFAULT_LEVELS, DEFAULT_SENTENCE_WORDS, Level

SKILL = "plain-language"
RANK = {Level.OFF: 0, Level.WARNING: 1, Level.ERROR: 2}
_COVERED: dict[str, bool] = {}  # the answers of one run, by root and path


def covered(rel: str) -> bool:
    """Whether the covered documents of this project include the Markdown file `rel`, relative to the
    root: the dial `territories` read on the current tree, as the hook reads it. A project with no dials
    file claims nothing."""
    root = repo_root(Path(os.getcwd()).resolve())
    if root is None:
        return False
    key = f"{root}\0{rel}"
    if key not in _COVERED:
        loaded = load_dials(root)
        if loaded is None:
            _COVERED[key] = False
        else:
            territories = own_dials.parse(loaded.own).territories
            with Matcher() as matcher:
                _COVERED[key] = rel in matcher.match(territories, [rel])
    return _COVERED[key]


def _number(value: object, default: float) -> float:
    return float(value) if isinstance(value, int | float) and not isinstance(value, bool) else default


def _levels(values: Mapping[str, object]) -> dict[str, Level]:
    """The level each rule has, as the dial `levels` and the defaults give them; a level that is none of the
    three is read as the default, since the gate itself refuses it."""
    given = values.get("levels")
    found: dict[str, Level] = {rule.value: level for rule, level in DEFAULT_LEVELS.items()}
    if isinstance(given, dict):
        for name, level in given.items():
            text = Level.OFF.value if level is False else level
            if str(name) in found and text in {lv.value for lv in Level}:
                found[str(name)] = Level(text)
    return found


def _entries(values: Mapping[str, object], key: str) -> list[object]:
    entries = values.get(key)
    return entries if isinstance(entries, list) else []


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """Whether the change of the namespace takes strictness away: a threshold raised, a rule lowered to
    warning or off, an exception or a departure added."""
    if _number(new.get("grade_ceiling"), DEFAULT_GRADE_CEILING) > _number(
        old.get("grade_ceiling"), DEFAULT_GRADE_CEILING
    ):
        return True
    if _number(new.get("sentence_words"), DEFAULT_SENTENCE_WORDS) > _number(
        old.get("sentence_words"), DEFAULT_SENTENCE_WORDS
    ):
        return True
    before, after = _levels(old), _levels(new)
    if any(RANK[after[rule]] < RANK[before[rule]] for rule in before):
        return True
    return any(
        entry not in _entries(old, key)
        for key in ("exceptions", "departures")
        for entry in _entries(new, key)
    )


def writes_a_covered_document(history_of: Callable[[], History]) -> Callable[[ToolCall, Session], bool]:
    """The moment of W5: a Write or Edit of a Markdown file of the covered documents."""

    def at(call: ToolCall, _session: Session) -> bool:
        if call.name not in ways.WRITES:
            return False
        rel = ways.relative(history_of(), call.names(), call.cwd)
        return rel is not None and rel.lower().endswith(".md") and covered(rel)

    return at


def skill_before_covered_write() -> Rule:
    """W5, built by `ways.skill_before`, whose moment needs the history's root to place a path: the rule
    keeps the history of the run it finds in."""
    held: list[History] = []
    base = ways.skill_before("W5", W5_TEXT, SKILL, writes_a_covered_document(lambda: held[-1]))

    def find(history: History) -> list[Moment]:
        held.append(history)
        try:
            return list(base.find(history))
        finally:
            held.pop()

    return dataclasses.replace(base, find=find)


def final_texts(session: Session) -> list[int]:
    """W7's moments: the last text of the assistant before each human turn, and the last of the session."""
    found: list[int] = []
    last: int | None = None
    for index, event in enumerate(session.events):
        if isinstance(event, AssistantText):
            last = index
        elif isinstance(event, HumanTurn) and last is not None:
            found.append(last)
            last = None
    if last is not None:
        found.append(last)
    return found


W1_TEXT = "A covered document is changed only where the language check examines it."
W2_TEXT = "The language check stays on, at its severity, and its thresholds and lists stay as strict."
W3_TEXT = (
    "After a red of the language check, the document is fixed as the finding teaches, not walked around."
)
W4_TEXT = "After a red, the skill it names is loaded before the document is touched again."
W5_TEXT = "Load plain-language before writing prose in a covered document."
W6_TEXT = "The main branch holds no covered document that the language check finds red."
W7_TEXT = (
    "The final reply of each turn is plain English: short sentences, short words, no idiom, the actor named."
)


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, covered),
        ways.switch_off("W2", W2_TEXT, loosened),
        ways.after_red("W3", W3_TEXT),
        ways.skill_after_red("W4", W4_TEXT),
        skill_before_covered_write(),
        ways.escape("W6", W6_TEXT, script="check-language.sh"),
        ways.reader_rule("W7", W7_TEXT, final_texts),
    )
