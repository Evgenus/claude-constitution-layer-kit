"""The fixture's two rules of the effect report, as a module's effect code will hold its own: one judged by a
pattern, one by a reader. Kit tooling, and never shipped."""

from __future__ import annotations

from collections.abc import Sequence

from constitution_layer_kit.effect import History, Judge, Moment, Outcome, Rule, Way
from constitution_layer_kit.history import HumanTurn

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


def rules() -> Sequence[Rule]:
    return (
        Rule("W1", Judge.PATTERN, (Way.B1,), "Every write of a Markdown file is examined.", markdown_writes),
        Rule("W2", Judge.READER, (Way.B6,), W2_TEXT, human_turns),
    )
