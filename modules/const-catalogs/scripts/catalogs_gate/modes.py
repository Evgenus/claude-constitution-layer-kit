"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code; the checks themselves live in ``checks``."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import pipeline
from const_gate.index import build_index
from const_gate.model import Finding, PendingDocument
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.territory import Matcher

from . import messages
from .checks import examine, shared_numbers
from .declarations import declared
from .model import Item


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    rel = target.rel
    with Matcher() as matcher:
        pending = PendingDocument(rel, target.text)
        index = build_index(target.root, target.dials, target.root_policy, matcher, pending)
        catalogs = declared(index, target.dials)
        if not catalogs:
            return pipeline.skip(output, messages.g1_skip_no_catalog(), index.notes)
        examination, _item = examine(index, catalogs, rel, target.text)
    if examination.outside:
        return pipeline.skip(output, messages.g1_skip_not_an_item(rel, catalogs), index.notes)
    if examination.findings:
        return pipeline.report_hook(output, examination.findings, index.notes, rel, target.dials.severity)
    return pipeline.green_hook(output, examination.policy or "", index.notes)


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    findings: list[Finding] = []
    items: list[Item] = []
    with Matcher() as matcher:
        index = build_index(target.root, target.dials, target.root_policy, matcher)
        catalogs = declared(index, target.dials)
        if not catalogs:
            return pipeline.skip(output, messages.g1_skip_no_catalog(), index.notes)
        for rel, text in index.documents():
            examination, item = examine(index, catalogs, rel, text)
            if item is not None:
                items.append(item)
                findings.extend(examination.findings)
    findings.extend(shared_numbers(items))
    tail = messages.f9_scan_tail(len(items), len(index.paths), len(catalogs))
    return pipeline.report_scan(output, findings, index.notes, tail)
