"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code; the checks themselves live in ``checks``."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import messages as shared
from const_gate import pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.index import build_index, collect_void_namespaces
from const_gate.model import Finding, Key, PendingDocument
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.territory import Matcher

from . import messages
from .checks import check_root_policy, examine

# configuration failures a write to the root policy can itself cause
ROOT_KEYS = (Key.C6, Key.C7, Key.C8, Key.C9)


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    rel, dials = target.rel, target.dials
    writes_root = rel == target.root_policy
    if writes_root:
        root_findings = check_root_policy(dials, rel, target.text)
        if root_findings:
            return pipeline.report_hook(output, root_findings, (), rel, dials.severity)
    try:
        with Matcher() as matcher:
            pending = PendingDocument(rel, target.text)
            index = build_index(target.root, dials, target.root_policy, matcher, pending)
            collect_void_namespaces(index, dials, matcher)
            examination = examine(index, rel, target.text)
    except ConfigurationFailure as failure:
        if writes_root and failure.broken.key in ROOT_KEYS:  # this write would break governance
            finding = messages.f14_root_breaks_governance(rel, failure.broken)
            return pipeline.report_hook(output, [finding], (), rel, dials.severity)
        raise
    if examination.outside:
        void = index.void_namespaces_claiming(rel)
        reason = (
            messages.g1_skip_void_territory(rel, void) if void else messages.g1_skip_outside_territory(rel)
        )
        return pipeline.skip(output, reason, index.notes)
    if examination.findings:
        return pipeline.report_hook(output, examination.findings, index.notes, rel, dials.severity)
    return pipeline.green_hook(output, examination.policy or "", index.notes)


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    findings: list[Finding] = []
    examined = 0
    with Matcher() as matcher:
        index = build_index(target.root, target.dials, target.root_policy, matcher)
        collect_void_namespaces(index, target.dials, matcher)
        for rel in index.paths:
            text = index.text(rel)
            if text is None:
                raise ConfigurationFailure(shared.c12_unreadable(rel))
            examination = examine(index, rel, text)
            if examination.outside:
                continue
            examined += 1
            findings.extend(examination.findings)
    notes = index.notes + [messages.n1_note_void_namespace(name) for name in sorted(index.void)]
    tail = messages.f9_scan_tail(examined, len(index.paths), len(index.policies))
    return pipeline.report_scan(output, findings, notes, tail)
