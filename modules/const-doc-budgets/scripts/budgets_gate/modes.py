"""The two modes and the history report. Each wires the shared pipeline to this module's
measurement and returns an exit code. No policy is resolved and no envelope is read: a document is
held to the ceiling whose paths match it, among the Markdown files git lists, and its length is
counted in characters. A document held by two ceilings is a configuration failure. The plugin wires
the hook after the write; wired before it, the same finding would refuse the write."""

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
from .model import Ceiling, Departure, Level, characters, longest

SINCE = "--since"


def judge(rel: str, length: int, ceiling: Ceiling) -> Finding | str | None:
    """A measured document against its ceiling: nothing at or under it; over it, a finding at level
    error and a note at level warning."""
    if length <= ceiling.max:
        return None
    if ceiling.level is Level.WARNING:
        return messages.n2_warning(rel, length, ceiling)
    return messages.b1_over(rel, length, ceiling)


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
        lifted = _lifted(matcher, dials.departures, [rel])
    ceiling = holding.get(rel)
    if ceiling is None:
        return pipeline.skip(output, messages.g1_skip_not_covered(rel))
    length = characters(target.text)
    lifting = lifted.get(rel, {}).get(ceiling.name)
    if lifting is not None:
        what = messages.g1_lifted(length, ceiling, lifting)
        return pipeline.green_hook(output, what, (), target.event_name)
    verdict = judge(rel, length, ceiling)
    what = messages.g1_measured(length, ceiling)
    if verdict is None:
        return pipeline.green_hook(output, what, (), target.event_name)
    if isinstance(verdict, str):
        return pipeline.green_hook(output, what, [verdict], target.event_name)
    return pipeline.report_hook(output, [verdict], (), rel, target.dials.severity, target.event_name)


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
        lifted = _lifted(matcher, dials.departures, sorted(holding))
        notes = [
            messages.n3_stale_departure(index, departure)
            for index, departure in enumerate(dials.departures, 1)
            if not _lifts(matcher, departure, holding)
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
        top = longest([(rel, lengths[rel]) for rel in measured])
        notes.append(messages.n4_ceiling(ceiling, len(held), len(held) - len(measured), top))
        for rel in measured:
            verdict = judge(rel, lengths[rel], ceiling)
            if isinstance(verdict, str):
                warnings.append(verdict)
            elif verdict is not None:
                findings.append(verdict)
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


def _lifted(
    matcher: Matcher, departures: Sequence[Departure], rels: Sequence[str]
) -> dict[str, dict[str, int]]:
    """The ceilings each document's departures lift: {rel: {ceiling name: the first entry's number}}."""
    lifted: dict[str, dict[str, int]] = {}
    for index, departure in enumerate(departures, 1):
        for rel in matcher.match(departure.paths, rels):
            for name in departure.allow:
                lifted.setdefault(rel, {}).setdefault(name, index)
    return lifted


def _lifts(matcher: Matcher, departure: Departure, holding: dict[str, Ceiling]) -> bool:
    """Whether an entry matches a document held by a ceiling it names: one that matches only
    documents under other ceilings lifts nothing, and is as stale as one that matches none."""
    return any(
        holding[rel].name in departure.allow for rel in matcher.match(departure.paths, sorted(holding))
    )


def _day(value: str) -> datetime.date:
    """A date written YYYY-MM-DD, and no other of the forms the standard library would take."""
    try:
        day = datetime.date.fromisoformat(value) if own_dials.DATE.fullmatch(value) else None
    except ValueError:
        day = None
    if day is None:
        raise ConfigurationFailure(messages.c12_since(value))
    return day
