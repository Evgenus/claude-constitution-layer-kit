"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code; the checks themselves live in ``checks``."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import messages as shared
from const_gate import pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.index import Index, build_index
from const_gate.model import Finding, PendingDocument
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.territory import Matcher

from . import dials as record_dials
from . import messages
from .checks import examine
from .model import RecordDials


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own = record_dials.parse(target.dials.own)
    if not own.record_policies:
        return pipeline.skip(output, messages.g1_skip_no_record_policies())
    rel = target.rel
    with Matcher() as matcher:
        pending = PendingDocument(rel, target.text)
        index = build_index(target.root, target.dials, target.root_policy, matcher, pending)
        _refuse_root_as_record_policy(index, own)
        examination = examine(index, own.record_policies, rel, target.text)
    notes = _notes(index, own)
    if examination.outside:
        return pipeline.skip(output, messages.g1_skip_not_a_record(rel, own.record_policies), notes)
    if examination.findings:
        return pipeline.report_hook(output, examination.findings, notes, rel, target.dials.severity)
    return pipeline.green_hook(output, examination.policy or "", notes)


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own = record_dials.parse(target.dials.own)
    if not own.record_policies:
        return pipeline.skip(output, messages.g1_skip_no_record_policies())
    findings: list[Finding] = []
    examined = 0
    with Matcher() as matcher:
        index = build_index(target.root, target.dials, target.root_policy, matcher)
        _refuse_root_as_record_policy(index, own)
        for rel in index.paths:
            text = index.text(rel)
            if text is None:
                raise ConfigurationFailure(shared.c12_unreadable(rel))
            examination = examine(index, own.record_policies, rel, text)
            if examination.outside:
                continue
            examined += 1
            findings.extend(examination.findings)
    known = sum(1 for policy in own.record_policies if policy in index.policies)
    tail = messages.f9_scan_tail(examined, len(index.paths), known)
    return pipeline.report_scan(output, findings, _notes(index, own), tail)


def _refuse_root_as_record_policy(index: Index, own: RecordDials) -> None:
    if index.root_id in own.record_policies:
        raise ConfigurationFailure(messages.c5_record_policy_is_root(index.root_id))


def _notes(index: Index, own: RecordDials) -> list[str]:
    """The index's notes, then one per record policy the dial names that is no policy."""
    dangling = [policy for policy in own.record_policies if policy not in index.policies]
    return [*index.notes, *(messages.n2_note_dangling_record_policy(policy) for policy in dangling)]
