"""The rules of the effect report, W1 to W6 of the module's section "Effect". All six are judged by a pattern
and built by one helper of `constitution_layer_kit.ways` with what only this module knows: its territories,
its loosened dials, its skill's moment and its scan."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from functools import cache
from pathlib import Path

from constitution_layer_kit import ways
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.effect import History, Judge, Moment, Rule, Way
from constitution_layer_kit.history import HookRun, Session, ToolCall
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from .dials import parse
from .model import Catalog

SKILL = "catalog-item"
SCAN = "check-catalog-item.sh"

W1_TEXT = (
    "A Markdown document in a catalog's territory is written through a Write or an Edit that the gate's hook"
    " examines, so that its name, its id and its number are held."
)
W2_TEXT = "The module stays on, with severity block and with every catalog and territory it was set to."
W3_TEXT = (
    "After a block for a name, an id or a number, the document is fixed; the check is not walked around."
)
W4_TEXT = "After a block, the skill catalog-item that the block names is loaded before the file is touched."
W5_TEXT = "The skill catalog-item is loaded before a numbered document is written."
W6_TEXT = "The main branch holds no item whose name or id is not its catalog's form, and no number twice."


@cache
def _catalogs() -> tuple[Catalog, ...]:
    """The catalogs of the module's `catalogs` dial in the project the report runs in, by the module's own
    reader of its dials; none where the project has no dials file, where the gate examines nothing."""
    root = repo_root(Path.cwd())
    dials = load_dials(root) if root is not None else None
    return parse(dials.own).catalogs if dials is not None else ()


@cache
def in_territory(rel: str) -> bool:
    """Whether some catalog's territory holds the Markdown file `rel` (from the project's root) on the
    current tree: then the file is an item and the gate examines it."""
    catalogs = _catalogs()
    if not catalogs:
        return False
    with Matcher() as matcher:
        return any(rel in matcher.match(catalog.territory, [rel]) for catalog in catalogs)


def _entries(values: Mapping[str, object]) -> dict[str, list[str]]:
    """The catalogs a namespace lists, by prefix, each with its territory patterns."""
    listed = values.get("catalogs")
    found: dict[str, list[str]] = {}
    for entry in listed if isinstance(listed, list) else []:
        if isinstance(entry, dict) and isinstance(entry.get("prefix"), str):
            patterns = entry.get("territory")
            found[entry["prefix"]] = [str(p) for p in patterns] if isinstance(patterns, list) else []
    return found


def loosened(old: Mapping[str, object], new: Mapping[str, object]) -> bool:
    """A change of the namespace that lets a document through that the gate held: severity from block (the
    default) to warn, a catalog no longer listed, a territory pattern of a catalog removed or a negated one
    added."""
    if old.get("severity", "block") == "block" and new.get("severity", "block") == "warn":
        return True
    before, after = _entries(old), _entries(new)
    for prefix, patterns in before.items():
        if prefix not in after:
            return True
        dropped = {p for p in patterns if not p.startswith("!")} - set(after[prefix])
        negated = {p for p in after[prefix] if p.startswith("!")} - set(patterns)
        if dropped or negated:
            return True
    return False


def numbered_write(history: History, call: ToolCall) -> bool:
    """Whether a call is a Write of a Markdown file in a catalog's territory: the moment of the skill."""
    if call.name != "Write":
        return False
    rel = ways.relative(history, call.names(), call.cwd)
    return rel is not None and rel.lower().endswith(".md") and in_territory(rel)


def skill_before_write(history: History) -> list[Moment]:
    """W5: the helper's rule, with the moment read on the history it is asked about."""

    def at(call: ToolCall, _session: Session) -> bool:
        return numbered_write(history, call)

    return list(ways.skill_before("W5", W5_TEXT, SKILL, at).find(history))


def _named(history: History, run: HookRun) -> HookRun:
    """A refusal that names its command as `command hook <n>` carries no script, and the helpers of the
    after-red rules count only the runs of the module's scripts; one that names this plugin is given the
    gate's script, so that it counts."""
    if run.script or not run.plugin or run.plugin != history.namespace:
        return run
    return replace(run, script=SCAN)


def with_named_refusals(history: History) -> History:
    """The history with each hook run of this plugin that names no script given the gate's script."""
    sessions = tuple(
        replace(
            session,
            events=tuple(_named(history, e) if isinstance(e, HookRun) else e for e in session.events),
        )
        for session in history.sessions
    )
    return replace(history, sessions=sessions, scripts=history.scripts | {SCAN})


def after_red_named(rule: Rule) -> Rule:
    """The rule with its moments read on the history of `with_named_refusals`."""
    return replace(rule, find=lambda history: rule.find(with_named_refusals(history)))


def rules() -> Sequence[Rule]:
    return (
        ways.path_bypass("W1", W1_TEXT, in_territory),
        ways.switch_off("W2", W2_TEXT, loosened),
        after_red_named(ways.after_red("W3", W3_TEXT)),
        after_red_named(ways.skill_after_red("W4", W4_TEXT)),
        Rule("W5", Judge.PATTERN, (Way.B5,), W5_TEXT, skill_before_write),
        ways.escape("W6", W6_TEXT, script=SCAN),
    )
