"""The rules of the effect report, W1 to W8 of the module's section "Effect". Seven are judged by a pattern,
six of them built by one helper of `constitution_layer_kit.ways` with what only this module knows (its
territory, its loosened dials, its scan), W5 by a `find` of its own, since its moment is a text of the
assistant and not a tool call; W8 is judged by a reader."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import cache
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import History, Judge, Moment, Outcome, Rule, Way
from constitution_layer_kit.history import AssistantText, Session, ToolCall
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from .dials import parse
from .model import DEFAULT_MARKERS, DEFAULT_TERRITORIES

SKILL = "ask-or-decide"
SCAN = "check-open-questions.sh"

W1_TEXT = (
    "A Markdown file the gate covers is written through a Write or an Edit that its hook examines, so that no"
    " open-question marker is delivered."
)
W2_TEXT = "The module stays on, with severity block and with the territories and markers it was set to."
W3_TEXT = "After a block for a marker, the document is fixed; the check is not walked around."
W4_TEXT = "After a block, the skill ask-or-decide that the block names is loaded before the file is touched."
W5_TEXT = "The skill ask-or-decide is loaded before a message that puts lettered options."
W6_TEXT = (
    "A choice is put as lettered options, each a bullet with Pros: and Cons: sub-bullets, then one"
    " recommendation, and the decider named."
)
W7_TEXT = "The main branch holds no document that carries an open-question marker."
W8_TEXT = (
    "A question is put to the user only at recorded stakes or at a genuine blocker; below that line the"
    " session makes the reasonable call and notes it in the commit message."
)

OPTION = re.compile(r"^[ \t]{0,3}(?:[-*][ \t]+)?\*\*([A-Z])(?:[.):]|\*\*| [—–-])", re.MULTILINE)
PROS = re.compile(r"^[ \t]+[-*][ \t]+\*\*Pros:\*\*", re.MULTILINE)
CONS = re.compile(r"^[ \t]+[-*][ \t]+\*\*Cons:\*\*", re.MULTILINE)
RECOMMENDATION = re.compile(r"recommend", re.IGNORECASE)
DECIDER = re.compile(r"\bdecider\b", re.IGNORECASE)
FENCE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$|^[ \t]*(```|~~~).*\Z", re.MULTILINE | re.DOTALL)
CODE_SPAN = re.compile(r"`[^`\n]*`")
QUESTION = re.compile(r"\?[\s*_\"')\]]*$", re.MULTILINE)


@cache
def _territories() -> tuple[str, ...]:
    """The patterns of the module's `territories` dial in the project the report runs in, by the module's
    own reader of its dials; none where the project has no dials file, where the gate skips every file."""
    root = repo_root(Path.cwd())
    dials = load_dials(root) if root is not None else None
    return parse(dials.own).territories if dials is not None else ()


@cache
def in_territory(rel: str) -> bool:
    """Whether the gate covers the Markdown file `rel` (from the project's root) on the current tree."""
    patterns = _territories()
    if not patterns:
        return False
    with Matcher() as matcher:
        return rel in matcher.match(patterns, [rel])


def _list(value: object, default: Sequence[str]) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else list(default)


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """A change of the namespace that lets a document through that the gate held, besides severity, which
    the shared `switch_off` judges, where the commit that adds the namespace at warn lowers nothing: a
    marker no longer listed, a territory pattern removed or a negated one added."""
    markers_old = _list(old.get("markers"), DEFAULT_MARKERS)
    if set(markers_old) - set(_list(new.get("markers"), DEFAULT_MARKERS)):
        return True
    land_old, land_new = (
        _list(old.get("territories"), DEFAULT_TERRITORIES),
        _list(new.get("territories"), DEFAULT_TERRITORIES),
    )
    dropped = {p for p in land_old if not p.startswith("!")} - set(land_new)
    negated = {p for p in land_new if p.startswith("!")} - set(land_old)
    return bool(dropped or negated)


def lettered(text: str) -> bool:
    """Whether a text puts lettered options: bullets that open with a bold letter, A and B among them."""
    letters = {match[1] for match in OPTION.finditer(text)}
    return {"A", "B"} <= letters


def has_shape(text: str) -> bool:
    """Whether a text of lettered options shows the decision shape: Pros: and Cons: sub-bullets beneath each
    option, a recommendation, and the decider named."""
    starts = [match.start() for match in OPTION.finditer(text)]
    ends = [*starts[1:], len(text)]
    for start, end in zip(starts, ends, strict=True):
        part = text[start:end]
        if not (PROS.search(part) and CONS.search(part)):
            return False
    return bool(RECOMMENDATION.search(text)) and bool(DECIDER.search(text))


def puts_question(text: str) -> bool:
    """Whether a text puts the user a question: a line outside code that ends in a question mark, or lettered
    options."""
    prose = CODE_SPAN.sub("", FENCE.sub("", text))
    return QUESTION.search(prose) is not None or lettered(text)


def _loaded(call: ToolCall) -> bool:
    given = call.input.get("skill")
    return call.name == "Skill" and isinstance(given, str) and given.rpartition(":")[2] == SKILL


def skill_before_options(history: History) -> list[Moment]:
    """W5: each text of the assistant that puts lettered options is a moment, applied where a Skill call
    naming ask-or-decide came earlier in the same session, missed by B5 otherwise. A skill loaded once stays
    in context until compaction, so a load earlier in the session counts (limit 18 of §4 of the shared
    code's guide)."""
    found: list[Moment] = []
    for session in history.sessions:
        loaded = False
        for event in session.events:
            if isinstance(event, ToolCall) and _loaded(event):
                loaded = True
            elif isinstance(event, AssistantText) and lettered(event.text):
                where = " ".join(event.text.split())[:60]
                if loaded:
                    found.append(Moment(session.id, event.at, where, Outcome.APPLIED))
                else:
                    found.append(Moment(session.id, event.at, where, Outcome.MISSED, Way.B5))
    return found


def question_texts(session: Session) -> list[int]:
    """W8's moments: the index of each text of the assistant that puts a question."""
    return [
        index
        for index, event in enumerate(session.events)
        if isinstance(event, AssistantText) and puts_question(event.text)
    ]


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, in_territory),
        ways.switch_off("W2", W2_TEXT, loosened),
        ways.after_red("W3", W3_TEXT),
        ways.skill_after_red("W4", W4_TEXT),
        Rule("W5", Judge.PATTERN, (Way.B5,), W5_TEXT, skill_before_options),
        ways.shape("W6", W6_TEXT, lettered, has_shape),
        ways.escape("W7", W7_TEXT, script=SCAN),
        ways.reader_rule("W8", W8_TEXT, question_texts),
    )
