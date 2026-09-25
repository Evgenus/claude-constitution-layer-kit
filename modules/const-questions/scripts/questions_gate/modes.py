"""The two modes. Each wires the shared pipeline to this module's check and returns an exit
code. No policy is resolved here: the covered documents are the Markdown files git lists
that the module's own territories hold."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import messages as shared
from const_gate import pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.model import PRE_WRITE, Finding
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import checks, messages
from . import dials as own_dials
from .model import QuestionsDials


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    if target.event_name != PRE_WRITE:
        raise ConfigurationFailure(messages.c12_event(target.event_name))
    dials = own_dials.parse(target.dials.own)
    rel = target.rel
    with Matcher() as matcher:
        covered = matcher.match(dials.territories, sorted({*list_markdown(target.root), rel}))
    if rel not in covered:
        return pipeline.skip(output, messages.g1_skip_not_covered(rel))
    findings = _findings(rel, target.text, dials)
    if findings:
        return pipeline.report_hook(output, findings, (), rel, target.dials.severity)
    return pipeline.green_hook(output, messages.g1_covered())


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        covered = sorted(matcher.match(dials.territories, paths))
    findings: list[Finding] = []
    for rel in covered:
        text = read_text(target.root, rel)
        if text is None:  # a file git lists and nobody can read: a count that skipped it would lie
            raise ConfigurationFailure(shared.c12_unreadable(rel))
        findings += _findings(rel, text, dials)
    tail = messages.f9_scan_tail(len(covered), len(dials.markers), len(paths))
    return pipeline.report_scan(output, findings, (), tail)


def _findings(rel: str, text: str, dials: QuestionsDials) -> list[Finding]:
    return [
        messages.q1_marker(rel, hit.line, hit.marker, hit.text) for hit in checks.examine(text, dials.markers)
    ]
