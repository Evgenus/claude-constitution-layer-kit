"""The two modes and the history report. Each wires the shared pipeline to this module's
measurement and returns an exit code. No policy is resolved and no envelope is read: a document is
held to the ceiling whose paths match it, among the Markdown files git lists, and its length is
counted in characters. A document held by two ceilings is a configuration failure."""

from __future__ import annotations

import datetime
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from const_gate import cli, pipeline
from const_gate import messages as shared
from const_gate.errors import ConfigurationFailure
from const_gate.model import POST_WRITE, PRE_WRITE, Finding
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import dials as own_dials
from . import history, messages
from .model import BudgetDials, Ceiling, Level, characters

SINCE = "--since"


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    if target.event_name not in (PRE_WRITE, POST_WRITE):
        raise ConfigurationFailure(messages.c12_event(target.event_name))
    dials = own_dials.parse(target.dials.own)
    if not dials.ceilings:
        return pipeline.skip(output, messages.g1_skip_no_ceiling())
    rel = target.rel
    with Matcher() as matcher:
        holding = _holding(matcher, dials.ceilings, [rel])
        lifted = _lifted(matcher, dials, [rel])
    ceiling = holding.get(rel)
    if ceiling is None:
        return pipeline.skip(output, messages.g1_skip_not_covered(rel))
    length = characters(target.text)
    lifting = lifted.get(rel, {}).get(ceiling.name)
    if lifting is not None:
        return pipeline.green_hook(
            output, messages.g1_lifted(length, ceiling, lifting), (), target.event_name
        )
    what = messages.g1_measured(length, ceiling)
    if length <= ceiling.max:
        return pipeline.green_hook(output, what, (), target.event_name)
    if ceiling.level is Level.WARNING:
        return pipeline.green_hook(
            output, what, [messages.n2_warning(rel, length, ceiling)], target.event_name
        )
    finding = messages.b1_over(rel, length, ceiling)
    return pipeline.report_hook(output, [finding], (), rel, target.dials.severity, target.event_name)


def scan_mode(output: Output, start: Path) -> int:
    return scan_with(output, start, {SINCE: None})


def scan_with(output: Output, start: Path, values: cli.Values) -> int:
    since = values.get(SINCE)
    day = None if since is None else _day(since)  # a bad date is refused before anything is read
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    if day is not None:
        return history.report(output, target.root, dials, day)
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        holding = _holding(matcher, dials.ceilings, paths)
        lifted = _lifted(matcher, dials, sorted(holding))
        matched = [set(matcher.match(d.paths, sorted(holding))) for d in dials.departures]
    notes = [
        messages.n3_stale_departure(index, departure)
        for index, (departure, files) in enumerate(zip(dials.departures, matched, strict=True), 1)
        if not files
    ]
    lengths: dict[str, int] = {}
    for rel in sorted(holding):
        text = read_text(target.root, rel)
        if text is None:  # a file git lists and nobody can read: a count that skipped it would lie
            raise ConfigurationFailure(shared.c12_unreadable(rel))
        lengths[rel] = characters(text)
    findings: list[Finding] = []
    warnings: list[str] = []
    for ceiling in dials.ceilings:
        held = [rel for rel in sorted(holding) if holding[rel] is ceiling]
        measured = [rel for rel in held if ceiling.name not in lifted.get(rel, {})]
        longest = max(((rel, lengths[rel]) for rel in measured), key=lambda p: (p[1], p[0]), default=None)
        notes.append(messages.n4_ceiling(ceiling, len(held), len(held) - len(measured), longest))
        for rel in measured:
            if lengths[rel] <= ceiling.max:
                continue
            if ceiling.level is Level.WARNING:
                warnings.append(messages.n2_warning(rel, lengths[rel], ceiling))
            else:
                findings.append(messages.b1_over(rel, lengths[rel], ceiling))
    tail = messages.f9_tail(len(holding), len(dials.ceilings), len(dials.departures), len(paths))
    return pipeline.report_scan(output, findings, [*notes, *warnings], tail)


def _holding(matcher: Matcher, ceilings: Sequence[Ceiling], rels: Sequence[str]) -> dict[str, Ceiling]:
    """The one ceiling each document is held to: {rel: ceiling}, a document under none absent. A
    document two ceilings hold is a configuration failure, the first such document in path order."""
    holding: dict[str, Ceiling] = {}
    overlaps: dict[str, tuple[str, str]] = {}
    for ceiling in ceilings:
        for rel in matcher.match(ceiling.paths, rels):
            if rel in holding:
                overlaps.setdefault(rel, (holding[rel].name, ceiling.name))
            else:
                holding[rel] = ceiling
    if overlaps:
        rel = min(overlaps)
        raise ConfigurationFailure(messages.c5_overlap(*overlaps[rel], rel))
    return holding


def _lifted(matcher: Matcher, dials: BudgetDials, rels: Sequence[str]) -> dict[str, dict[str, int]]:
    """The ceilings each document's departures lift: {rel: {ceiling name: the first entry's number}}."""
    lifted: dict[str, dict[str, int]] = {}
    for index, departure in enumerate(dials.departures, 1):
        for rel in matcher.match(departure.paths, rels):
            for name in departure.allow:
                lifted.setdefault(rel, {}).setdefault(name, index)
    return lifted


def _day(value: str) -> datetime.date:
    """A date written YYYY-MM-DD, and no other of the forms the standard library would take."""
    try:
        day = datetime.date.fromisoformat(value) if own_dials.DATE.fullmatch(value) else None
    except ValueError:
        day = None
    if day is None:
        raise ConfigurationFailure(messages.c12_since(value))
    return day
