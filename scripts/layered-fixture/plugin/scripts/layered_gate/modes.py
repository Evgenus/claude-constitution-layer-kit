"""The two modes. Each reads the gate's own file, joins the constitution's part to it inside a scope of that
file, and judges the documents there, so that every failure of the policies names the file they stand in."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TextIO

from constitution_layer_kit import identity, pipeline
from constitution_layer_kit.dials import load_kernel_part
from constitution_layer_kit.envelope import parse_envelope
from constitution_layer_kit.index import Index, build_index
from constitution_layer_kit.messages import governed_by
from constitution_layer_kit.model import KERNEL_KEYS, Dials, Examination, Finding, PendingDocument
from constitution_layer_kit.output import Output
from constitution_layer_kit.pipeline import Skip
from constitution_layer_kit.resolution import resolve
from constitution_layer_kit.territory import Matcher

from . import dials as own_dials
from . import messages
from .model import CONSTITUTION_FILE, FORBIDDEN_LABEL


def forbidden(policy_text: str | None) -> list[str]:
    """The phrases a policy forbids its documents to hold: the rest of each line that starts `FORBIDDEN:`."""
    lines = (policy_text or "").splitlines()
    return [
        phrase
        for line in lines
        if line.startswith(FORBIDDEN_LABEL) and (phrase := line[len(FORBIDDEN_LABEL) :].strip())
    ]


def examine(index: Index, rel: str, text: str) -> Examination:
    """The document's verdict: outside every territory nothing is said; one policy, that policy's text is
    read for the phrases it forbids; any other resolution is a finding of its own."""
    resolution = resolve(index, rel, parse_envelope(text))
    if resolution.outside:
        return Examination((), None)
    if resolution.defect is not None:
        return Examination((messages.l4_unresolved(rel, resolution.defect),), None)
    policy = resolution.policy or ""
    found = [phrase for phrase in forbidden(index.text(index.policies[policy].path)) if phrase in text]
    return Examination(tuple(messages.l3_forbidden(rel, policy, phrase) for phrase in found), policy)


def joined(root: Path, own: Dials) -> Dials | None:
    """The gate's own dials with the constitution's part joined: its root policy and its policy namespaces.
    None where that file holds no root policy, which the caller says as the skip. It reads inside the scope of
    that file, which the caller has opened."""
    part = load_kernel_part(root)
    if part is None or part.root_policy is None:
        return None
    return replace(own, root_policy=part.root_policy, namespaces=part.namespaces)


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own_dials.parse(target.dials)
    with identity.reading(CONSTITUTION_FILE, KERNEL_KEYS):
        dials = joined(target.root, target.dials)
        if dials is None or dials.root_policy is None:
            return pipeline.no_root_policy(output)
        with Matcher() as matcher:
            index = build_index(
                target.root, dials, dials.root_policy, matcher, PendingDocument(target.rel, target.text)
            )
        examination = examine(index, target.rel, target.text)
    if examination.outside:
        reason = messages.g1_skip_outside_territory(target.rel)
        return pipeline.skip(output, reason, index.notes, target.event_name)
    if examination.findings:
        return pipeline.report_hook(output, examination.findings, index.notes, target.rel, dials.severity)
    green = governed_by(examination.policy or "")
    return pipeline.green_hook(output, green, index.notes, target.event_name)


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own_dials.parse(target.dials)
    findings: list[Finding] = []
    examined = 0
    with identity.reading(CONSTITUTION_FILE, KERNEL_KEYS):
        dials = joined(target.root, target.dials)
        if dials is None or dials.root_policy is None:
            return pipeline.no_root_policy(output)
        with Matcher() as matcher:
            index = build_index(target.root, dials, dials.root_policy, matcher)
        for rel, text in index.documents():
            examination = examine(index, rel, text)
            if not examination.outside:
                examined += 1
                findings.extend(examination.findings)
    tail = messages.f9_scan_tail(examined, len(index.paths), len(index.policies))
    return pipeline.report_scan(output, findings, index.notes, tail)
