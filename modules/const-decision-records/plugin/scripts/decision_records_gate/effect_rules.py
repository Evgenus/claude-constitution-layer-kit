"""The rules of the effect report, W1 to W7 of the module's section "Effect". Six are judged by a pattern,
each built by one helper of `constitution_layer_kit.ways` with what only this module knows (its record
territory, its loosened dials, its scan, its skill and its moment); W7 is judged by a reader, and its
moments are the human turns that answer a lettered choice."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import History, Moment, Rule
from constitution_layer_kit.history import AssistantText, HookRun, HumanTurn, Session, ToolCall
from constitution_layer_kit.index import build_index
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from . import dials as record_dials

SKILL = "record-decision"
SCAN = "check-decision-record.sh"

W1_TEXT = (
    "A Markdown file in the territory of a record policy is written through a Write or an Edit that the"
    " gate's hook examines, so that every decision record carries its type, stakes and decider."
)
W2_TEXT = "The module stays on, with severity block and every record policy it was set to name."
W3_TEXT = "After a block for a record, the record is fixed; the check is not walked around."
W4_TEXT = (
    "After a block, the skill record-decision that the block names is loaded before the file is touched."
)
W5_TEXT = "The skill record-decision is loaded before a decision record is written."
W6_TEXT = "The main branch holds no decision record with a missing or invalid type, stakes or decider."
W7_TEXT = (
    "A ruling the user makes in chat at recorded stakes (process, product, architecture) is written down as a"
    " decision record, and one below that line is left as a commit note."
)

OPTION = re.compile(r"^[ \t]{0,3}(?:[-*][ \t]+)?(?:\*\*)?([A-Z])(?:[.):]|\*\*)", re.MULTILINE)
LETTER = re.compile(r"(?<![A-Za-z0-9])([A-Za-z])(?![A-Za-z0-9])")
PICK_CHARS = 300  # a human turn longer than this is an argument, not an answer by letter


@dataclass(frozen=True, slots=True)
class Territory:
    records: tuple[tuple[str, ...], ...]  # the territory of each record policy the dial names
    policies: frozenset[str]  # the documents where policies live, never records


@cache
def _territory() -> Territory:
    """What the gate examines as a record in the project the report runs in, by the module's own dials
    reader and the shared index; nothing where the project has no dials file, no root policy or no record
    policy, where the gate examines nothing."""
    root = repo_root(Path.cwd().resolve())
    dials = load_dials(root) if root is not None else None
    if root is None or dials is None or dials.root_policy is None:
        return Territory((), frozenset())
    own = record_dials.parse(dials.own)
    with Matcher() as matcher:
        index = build_index(root, dials, dials.root_policy, matcher)
    records = tuple(index.policies[p].territory for p in own.record_policies if p in index.policies)
    return Territory(records, frozenset(index.in_root))


@cache
def in_territory(rel: str) -> bool:
    """Whether the gate examines the Markdown file `rel` (from the project's root) as a record on the current
    tree: a record policy's territory takes it, and a document where policies live never is one."""
    found = _territory()
    if rel in found.policies:
        return False
    with Matcher() as matcher:
        return any(rel in matcher.match(territory, [rel]) for territory in found.records)


def _list(value: object) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """A change of the namespace that lets a document through that the gate held: severity from block (the
    default, where none stands) to warn, or a record policy no longer named."""
    if old.get("severity", "block") == "block" and new.get("severity", "block") == "warn":
        return True
    return bool(set(_list(old.get("record_policies"))) - set(_list(new.get("record_policies"))))


@cache
def _root() -> History:
    """A history that holds only the project's root, for `ways.relative`, which reads nothing else."""
    top = repo_root(Path.cwd().resolve()) or Path.cwd().resolve()
    return History(top, frozenset(), (), (), "")


def writes_a_record(call: ToolCall, _session: Session) -> bool:
    """The moment of W5: a Write of a Markdown file in record territory."""
    if call.name != "Write":
        return False
    rel = ways.relative(_root(), call.names(), call.cwd)
    return rel is not None and rel.lower().endswith(".md") and in_territory(rel)


def _options(text: str) -> set[str]:
    """The letters that open the options of a message, when it puts A and B among them; else none."""
    letters = {match[1] for match in OPTION.finditer(text)}
    return letters if {"A", "B"} <= letters else set()


def lettered_answers(session: Session) -> list[int]:
    """W7's moments: the index of each human turn that answers a message of lettered options with a
    letter of them. The message is the assistant's last text before the turn; a long turn is no answer."""
    found: list[int] = []
    offered: set[str] = set()
    for index, event in enumerate(session.events):
        if isinstance(event, AssistantText):
            offered = _options(event.text)
        elif isinstance(event, HumanTurn):
            if offered and _answers(event.text, offered):
                found.append(index)
            offered = set()
    return found


def _answers(text: str, offered: set[str]) -> bool:
    if len(text) > PICK_CHARS:
        return False
    return any(
        match[1].upper() in offered and (match[1].isupper() or len(text.strip()) <= 12)
        for match in LETTER.finditer(text)
    )


def attributed(rule: Rule) -> Rule:
    """The rule over a history in which a blocked run whose command names no script (`[command hook 7]`)
    but whose text names this plugin carries the name of the gate's script, as `History.runs` counts such a
    run as the module's already; the helpers of the after-a-red ways read a run by its script alone."""

    def find(history: History) -> Iterable[Moment]:
        sessions = tuple(_with_scripts(session, history.namespace) for session in history.sessions)
        return rule.find(replace(history, sessions=sessions))

    return replace(rule, find=find)


def _with_scripts(session: Session, namespace: str) -> Session:
    events = tuple(
        replace(event, script=SCAN)
        if isinstance(event, HookRun) and not event.script and event.plugin == namespace
        else event
        for event in session.events
    )
    return replace(session, events=events)


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, in_territory),
        ways.switch_off("W2", W2_TEXT, loosened),
        attributed(ways.after_red("W3", W3_TEXT)),
        attributed(ways.skill_after_red("W4", W4_TEXT)),
        ways.skill_before("W5", W5_TEXT, SKILL, writes_a_record),
        ways.escape("W6", W6_TEXT, script=SCAN),
        ways.reader_rule("W7", W7_TEXT, lettered_answers),
    )
