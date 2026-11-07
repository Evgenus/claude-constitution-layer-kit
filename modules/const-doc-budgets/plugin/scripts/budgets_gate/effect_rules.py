"""The rules of the effect report, W1 to W4 of the module's section "Effect". All four are judged by a
pattern, and each is built by one helper of `constitution_layer_kit.ways` with what only this module knows:
the documents a ceiling holds, the changes of its dials that loosen it, the edits of the dials file that
touch the ceilings, and the wrapper of its scan."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import cache
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import Rule
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.history import Session, ToolCall
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from .dials import parse
from .model import Ceiling
from .start import GATE

SKILL = "set-ceilings"
SCAN = "check-budgets.sh"
TOUCHES = re.compile(r"ceilings|departures|\bmax\s*:|\bwindow\s*:|\blevel\s*:")

W1_TEXT = (
    "A Markdown file that a ceiling holds is written through a Write or an Edit that its hook examines,"
    " so that its length is measured."
)
W2_TEXT = "The module stays on; no ceiling is raised, lowered to a warning or removed, no departure added."
W3_TEXT = "The main branch holds no document over a ceiling at level error."
W4_TEXT = (
    "The skill set-ceilings is loaded before the dials file is edited where the edit touches the ceilings."
)


@cache
def _ceilings() -> tuple[Ceiling, ...]:
    """The ceilings of the project the report runs in, by the module's own reader of its dials; none where
    the project has no dials file or the dials are malformed, where the gate measures nothing."""
    root = repo_root(Path.cwd())
    dials = load_dials(root) if root is not None else None
    if dials is None:
        return ()
    try:
        return parse(dials.own).ceilings
    except ConfigurationFailure:
        return ()


@cache
def in_territory(rel: str) -> bool:
    """Whether a ceiling holds the Markdown file `rel` (from the project's root) on the current tree."""
    ceilings = _ceilings()
    if not ceilings:
        return False
    with Matcher() as matcher:
        return any(rel in matcher.match(ceiling.paths, [rel]) for ceiling in ceilings)


def _entries(value: object) -> list[Mapping[str, object]]:
    return [entry for entry in value if isinstance(entry, dict)] if isinstance(value, list) else []


def _number(value: object) -> float:
    return float(value) if isinstance(value, int | float) and not isinstance(value, bool) else 0.0


def _ceiling_loosened(old: Mapping[str, object], new: Mapping[str, object] | None) -> bool:
    """One ceiling of the old namespace against the new: removed, its number raised, or its level moved
    from error to warning."""
    if new is None:
        return True
    if _number(new.get("max")) > _number(old.get("max")):
        return True
    return old.get("level") == "error" and new.get("level") == "warning"


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """A change of the namespace that lets a document through that the gate held: a ceiling raised, moved
    from error to warning or removed, or a departure added."""
    if not old:  # the namespace is born: nothing was held before it, so nothing is let through
        return False
    now = {entry.get("name"): entry for entry in _entries(new.get("ceilings"))}
    if any(_ceiling_loosened(entry, now.get(entry.get("name"))) for entry in _entries(old.get("ceilings"))):
        return True
    before = _entries(old.get("departures"))
    return any(entry not in before for entry in _entries(new.get("departures")))


def edits_ceilings(call: ToolCall, _session: Session) -> bool:
    """The moment of W4: a Write or an Edit of the dials file whose text, new or old, names the ceilings or
    the departures or one of a ceiling's fields. Read from the call alone, so an Edit of a line that carries
    none of those words is not seen (limit 18 of kit-shared-gate-code §4)."""
    if call.name not in ways.WRITES or Path(call.names()).name != GATE.dials_file:
        return False
    parts = ("content", "old_string", "new_string")
    return any(
        isinstance(call.input.get(part), str) and TOUCHES.search(str(call.input[part])) for part in parts
    )


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, in_territory),
        ways.switch_off("W2", W2_TEXT, loosened),
        ways.escape("W3", W3_TEXT, script=SCAN),
        ways.skill_before("W4", W4_TEXT, SKILL, edits_ceilings),
    )
