"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code; the checks themselves live in ``checks``."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.index import build_index
from const_gate.messages import governed_by
from const_gate.model import Finding, PendingDocument, SharedKey
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.territory import Matcher

from . import dials as own_dials
from . import messages
from .checks import check_root_policy, examine, id_owners, void_claims
from .pointer import policy_pointer

# configuration failures a write to the root policy can itself cause
ROOT_KEYS = (SharedKey.C6, SharedKey.C7, SharedKey.C8, SharedKey.C9)


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own_dials.parse(target.dials.own)
    rel, dials, root_policy = target.rel, target.dials, target.dials.root_policy
    if root_policy is None:
        return pipeline.no_root_policy(output)
    writes_root = rel == root_policy
    if writes_root:
        root_findings = check_root_policy(dials, rel, target.text)
        if root_findings:
            return pipeline.report_hook(output, root_findings, (), rel, dials.severity)
    try:
        with Matcher() as matcher:
            pending = PendingDocument(rel, target.text)
            index = build_index(target.root, dials, root_policy, matcher, pending)
            void = void_claims(index, dials, matcher)
            examination = examine(index, lambda: id_owners(index), rel, target.text)
    except ConfigurationFailure as failure:
        if writes_root and failure.broken.key in ROOT_KEYS:  # this write would break governance
            finding = messages.f14_root_breaks_governance(rel, failure.broken)
            return pipeline.report_hook(output, [finding], (), rel, dials.severity)
        raise
    if examination.outside:
        claiming = [name for name, claims in void.items() if rel in claims]
        reason = (
            messages.g1_skip_void_territory(rel, claiming)
            if claiming
            else messages.g1_skip_outside_territory(rel)
        )
        return pipeline.skip(output, reason, index.notes, target.event_name)
    if examination.findings:
        return pipeline.report_hook(output, examination.findings, index.notes, rel, dials.severity)
    policy = index.policies[examination.policy] if examination.policy in index.policies else None
    pointer = (
        policy_pointer(output, output.session, target.root, policy.path, index.text(policy.path))
        if policy is not None
        else None
    )
    notes = [*index.notes, *([pointer] if pointer else [])]  # the pointer last, before the green line
    return pipeline.green_hook(output, governed_by(examination.policy or ""), notes, target.event_name)


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own_dials.parse(target.dials.own)
    root_policy = target.dials.root_policy
    if root_policy is None:
        return pipeline.no_root_policy(output)
    findings: list[Finding] = []
    examined = 0
    with Matcher() as matcher:
        index = build_index(target.root, target.dials, root_policy, matcher)
        void = void_claims(index, target.dials, matcher)
        owners = id_owners(index)
        for rel, text in index.documents():
            examination = examine(index, lambda: owners, rel, text)
            if examination.outside:
                continue
            examined += 1
            findings.extend(examination.findings)
    notes = index.notes + [messages.n2_note_void_namespace(name) for name in sorted(void)]
    tail = messages.f9_scan_tail(examined, len(index.paths), len(index.policies))
    return pipeline.report_scan(output, findings, notes, tail)
