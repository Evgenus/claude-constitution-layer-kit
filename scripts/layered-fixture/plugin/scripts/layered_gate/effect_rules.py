"""The fixture's rules of the effect report, as a module's effect code will hold its own: W1 to W3 written
by hand, W4 to W12 each built by one helper of `constitution_layer_kit.ways`, with what only the gate knows.
Kit tooling, and never shipped."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from constitution_layer_kit import ways
from constitution_layer_kit.effect import History, Judge, Moment, Outcome, Rule, Way
from constitution_layer_kit.history import AssistantText, HumanTurn, Session, ToolCall

WRITES = ("Write", "Edit")
W2_TEXT = (
    "When the person asks for a change to a document, the change is made in the document the person named,"
    " and no other document is touched."
)


def markdown_writes(history: History) -> list[Moment]:
    """W1: each write of a Markdown file in a session is a moment; a run of the fixture's hook script that
    examined that call makes it applied, and none makes it bypassed by way B1."""
    found: list[Moment] = []
    for session in history.sessions:
        examined = {call.id for call, _ in history.runs(session) if call is not None}
        for call in session.calls():
            path = call.names()
            if call.name not in WRITES or not path.endswith(".md"):
                continue
            if call.id in examined:
                found.append(Moment(session.id, call.at, path, Outcome.APPLIED))
            else:
                found.append(Moment(session.id, call.at, path, Outcome.BYPASSED, Way.B1))
    return found


def human_turns(history: History) -> list[Moment]:
    """W2: one moment for each human turn, with the events around it for the reader."""
    found: list[Moment] = []
    for session in history.sessions:
        for index, event in enumerate(session.events):
            if isinstance(event, HumanTurn):
                found.append(
                    Moment(session.id, event.at, "human turn", excerpt=history.excerpt(session, index))
                )
    return found


def unheld_hook_records(history: History) -> list[Moment]:
    """W3: each hook record of the log whose session no transcript holds is a moment, applied: the log
    alone says the hook ran there."""
    return [Moment(r.session, r.at, r.path, Outcome.APPLIED) for r in history.log_only()]


def in_notes(rel: str) -> bool:
    """The fixture's territory for the way rules: the Markdown files of the notes folder."""
    return rel.startswith("docs/notes/")


def lenient(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """The fixture's loosened dial: the key `lenient` turned on."""
    return new.get("lenient") is True and old.get("lenient") is not True


def writes_a_note(call: ToolCall, _session: Session) -> bool:
    """The moment of W8: a write of a Markdown file of the notes folder."""
    return call.name in ways.WRITES and "/docs/notes/" in call.names()


def names_a_note(text: str) -> bool:
    return "docs/notes/" in text


def links_the_note(text: str) -> bool:
    return "](docs/notes/" in text


def assistant_texts(session: Session) -> list[int]:
    return [i for i, event in enumerate(session.events) if isinstance(event, AssistantText)]


def rules() -> Sequence[Rule]:
    return (
        Rule("W1", Judge.PATTERN, (Way.B1,), "Every write of a Markdown file is examined.", markdown_writes),
        Rule("W2", Judge.READER, (Way.B6,), W2_TEXT, human_turns),
        Rule("W3", Judge.PATTERN, (), "The hook ran, where only the log says so.", unheld_hook_records),
        ways.path_bypass("W4", "A note is changed only where the hook examines it.", in_notes),
        ways.switch_off("W5", "The plugin stays on and its dials stay as strict.", lenient),
        ways.after_red("W6", "After a red, the file is fixed and the check is not walked around."),
        ways.skill_after_red("W7", "After a red, the skill it names is loaded before the file is touched."),
        ways.skill_before(
            "W8", "Load the notes skill before a note is written.", "notes-guide", writes_a_note
        ),
        ways.escape("W9", "The main branch holds no red note."),
        ways.shape("W10", "A note named in chat is a link.", names_a_note, links_the_note),
        ways.reader_rule("W11", "Each reply of the assistant keeps to the notes.", assistant_texts),
    )
