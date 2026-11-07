"""The rules of the effect report of const-referencing, W1 to W7 of the module's section "Effect": each is
built by one helper of `constitution_layer_kit.ways` with what only this module knows — its territory, its
loosened dials, its moments and its visible form. The report counts and blocks nothing."""

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
from constitution_layer_kit.pipeline import ScanTarget
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from . import dials as own_dials
from . import modes
from .links import find_links
from .lint import target_of
from .masking import mask
from .model import Link, ReferencingDials, Switch

W1_TEXT = "A Markdown document the module covers is written where the check examines it."
W2_TEXT = "The module stays on, and no dial that judges a reference is loosened."
W3_TEXT = "After a red, the document is fixed as the finding teaches."
W4_TEXT = "After a red, the skill it names is loaded before the document is touched."
W5_TEXT = "Before a write that adds a link to a document, the skill `referencing` is loaded."
W6_TEXT = "In chat, every reference to a file is a markdown link."
W7_TEXT = "No commit of the main branch holds a broken or malformed reference."

# a file name with a known extension, bare or below folders; not inside a URL, an address or a longer name
PATH = re.compile(
    r"(?<![\w/.:@~-])(?:[\w.-]+/)*[\w-][\w.-]*\.(?:md|py|sh|ya?ml|json|toml|txt|cfg|js|ts)\b(?![\w/-])"
)


@cache
def covered(rel: str) -> bool:
    """Whether the module's territories, read on the current tree, hold the path `rel` of the project."""
    root = repo_root(Path.cwd().resolve())
    dials = load_dials(root) if root is not None else None
    if root is None or dials is None:
        return False
    with Matcher() as matcher:
        found = modes.covered_documents(matcher, own_dials.parse(dials.own), ScanTarget(root, dials), [rel])
    return bool(found)


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """Whether a change of the namespace loosens a judgment: a switch turned to `allow`, a lane removed, or a
    pattern that takes documents out of the territories added."""
    try:
        before, after = own_dials.parse(old), own_dials.parse(new)
    except ConfigurationFailure:
        return False
    return (
        any(_allowed(b, a) for b, a in _switches(before, after))
        or len(after.lanes) < len(before.lanes)
        or _negations(after) - _negations(before) != set()
    )


def _switches(before: ReferencingDials, after: ReferencingDials) -> list[tuple[Switch, Switch]]:
    return [
        (before.bare_ids, after.bare_ids),
        (before.local_paths, after.local_paths),
        (before.heading_anchors, after.heading_anchors),
    ]


def _allowed(before: Switch, after: Switch) -> bool:
    return after is Switch.ALLOW and before is not Switch.ALLOW


def _negations(dials: ReferencingDials) -> set[str]:
    return {pattern for pattern in dials.territories if pattern.startswith("!")}


def _text_of(value: object) -> str:
    return value if isinstance(value, str) else ""


def _links_of(rel: str, text: str) -> set[tuple[str, str]]:
    """The links of a text that name a file of the project: the pair of their text and destination."""
    links: list[Link] = find_links(text, mask(text))
    return {(link.text, link.destination) for link in links if target_of(rel, link.destination) is not None}


def adds_a_link(call: ToolCall, _session: Session) -> bool:
    """The moment of W5: a write or an edit of a Markdown file whose new text holds a link to a file of the
    project that the replaced text did not hold."""
    if call.name not in ways.WRITES or not call.names().lower().endswith(".md"):
        return False
    given = call.input
    new = _text_of(given.get("content")) or _text_of(given.get("new_string"))
    return bool(_links_of(call.names(), new) - _links_of(call.names(), _text_of(given.get("old_string"))))


def _bare_paths(text: str, drop_links: bool) -> list[str]:
    """The file names in the prose of a chat text, fenced blocks and comments left out; with `drop_links`,
    those that stand outside every link."""
    prose = list(mask(text).blocks)
    if drop_links:
        for link in find_links(text, mask(text)):
            for position in range(link.start, link.end):
                prose[position] = " "
    return PATH.findall("".join(prose))


def names_a_file(text: str) -> bool:
    return bool(_bare_paths(text, False))


def links_every_file(text: str) -> bool:
    return not _bare_paths(text, True)


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, covered),
        ways.switch_off("W2", W2_TEXT, loosened),
        ways.after_red("W3", W3_TEXT),
        ways.skill_after_red("W4", W4_TEXT),
        ways.skill_before("W5", W5_TEXT, "referencing", adds_a_link),
        ways.shape("W6", W6_TEXT, names_a_file, links_every_file),
        ways.escape("W7", W7_TEXT),
    )
