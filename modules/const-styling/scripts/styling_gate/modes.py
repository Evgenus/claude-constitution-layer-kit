"""The one mode of the scan. It has no hook mode — it scans a tree and judges no single write —
and says so when run as one."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import messages as shared
from const_gate import pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.model import Finding
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import checks, messages
from . import dials as own_dials
from .model import Signature


def hook_mode(output: Output, stdin: TextIO) -> int:
    raise ConfigurationFailure(messages.c12_hook())


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        covered = sorted(matcher.match(dials.territories, paths))
        allowed = [set(matcher.match(d.paths, covered)) for d in dials.departures]
    notes = [
        messages.n2_stale_departure(index, departure)
        for index, (departure, files) in enumerate(zip(dials.departures, allowed, strict=True), 1)
        if not files
    ]
    findings: list[Finding] = []
    for rel in covered:
        text = read_text(target.root, rel)
        if text is None:  # a file git lists and nobody can read: a count that skipped it would lie
            raise ConfigurationFailure(shared.c12_unreadable(rel))
        for hit in checks.examine(text):
            if not any(
                hit.signature in departure.allow and rel in files
                for departure, files in zip(dials.departures, allowed, strict=True)
            ):
                findings.append(messages.finding(rel, hit))
    tail = messages.f9_tail(len(covered), len(Signature), len(dials.departures), len(paths))
    return pipeline.report_scan(output, findings, notes, tail)
