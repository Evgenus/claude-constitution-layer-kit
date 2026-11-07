"""The rules of the effect report, W1 to W3 of the module's section "Effect". All three are judged by a
pattern and built by one helper of `constitution_layer_kit.ways` with what only this module knows: the
dials it counts as loosened, its scan wrapper and the moment of its skill. The module has no hook mode, so
it has no rule of the ways B1 and B3."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from constitution_layer_kit import ways
from constitution_layer_kit.effect import Rule
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.history import Session, ToolCall

from .dials import parse
from .model import StylingDials

SKILL = "style-defaults"
SCAN = "check-style.sh"

W1_TEXT = (
    "The module stays on, and its dials stay as strict: no departure added or widened, no guide dropped."
)
W2_TEXT = "The main branch holds no document that carries a style trace no departure allows."
W3_TEXT = (
    "The skill style-defaults is loaded before a write whose content holds a table, a fenced block, a"
    " heading of level four or deeper, or a list."
)

TABLE = re.compile(
    r"^[ \t]*\|.*\|[ \t]*\n[ \t]*\|?[ \t]*:?-{2,}:?[ \t]*(?:\|[ \t]*:?-{2,}:?[ \t]*)*\|?[ \t]*$", re.M
)
FENCE = re.compile(r"^[ \t]{0,3}(?:```|~~~)", re.M)
DEEP_HEADING = re.compile(r"^[ \t]{0,3}#{4,}[ \t]", re.M)
LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\S", re.M)


def _dials(values: Mapping[str, object]) -> StylingDials | None:
    """The module's own reading of a namespace, or None where it is not a working one."""
    try:
        return parse(values)
    except ConfigurationFailure:
        return None


def _allowed(dials: StylingDials) -> set[tuple[str, str]]:
    """What the departures allow: each pair of a path pattern and a signature key."""
    return {(path, key.value) for entry in dials.departures for path in entry.paths for key in entry.allow}


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """A change of the namespace that lets a trace through that the scan held: a departure added or widened,
    so that a pair of a path pattern and a signature is allowed that was not, or a guide dropped. A
    namespace that is not a working one on either side is read as no change."""
    before, after = _dials(old), _dials(new)
    if before is None or after is None:
        return False
    return bool(_allowed(after) - _allowed(before)) or bool(set(before.guides) - set(after.guides))


def _written(call: ToolCall) -> list[str]:
    """The new content a Write, an Edit or a MultiEdit puts into a file."""
    texts = [call.input.get("content"), call.input.get("new_string")]
    edits = call.input.get("edits")
    if isinstance(edits, list):
        texts.extend(edit.get("new_string") for edit in edits if isinstance(edit, dict))
    return [text for text in texts if isinstance(text, str)]


def has_style_choice(text: str) -> bool:
    """Whether a text holds a table, a fenced block, a heading of level four or deeper, or a list."""
    return any(pattern.search(text) for pattern in (TABLE, FENCE, DEEP_HEADING, LIST_ITEM))


def writes_a_styled_document(call: ToolCall, _session: Session) -> bool:
    """The moment of W3: a Write, an Edit or a MultiEdit of a Markdown file whose new content makes one of
    the choices of style the skill answers."""
    if call.name not in ways.WRITES and call.name != "MultiEdit":
        return False
    return call.names().endswith(".md") and any(has_style_choice(text) for text in _written(call))


def rules() -> Sequence[Rule]:
    return (
        ways.switch_off("W1", W1_TEXT, loosened),
        ways.escape("W2", W2_TEXT, script=SCAN),
        ways.skill_before("W3", W3_TEXT, SKILL, writes_a_styled_document),
    )
