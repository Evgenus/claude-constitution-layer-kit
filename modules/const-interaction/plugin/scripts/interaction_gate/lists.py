"""The scan of list handles: the second entry point's one mode. It has no hook mode — it scans
a tree and judges no single write — and says so when run as one."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from constitution_layer_kit import messages as shared
from constitution_layer_kit import pipeline
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import Finding
from constitution_layer_kit.output import Output
from constitution_layer_kit.pipeline import Skip
from constitution_layer_kit.repository import list_markdown, read_text
from constitution_layer_kit.territory import Matcher

from . import checks, messages
from . import dials as own_dials


def hook_mode(output: Output, stdin: TextIO) -> int:
    raise ConfigurationFailure(messages.c12_lists_hook())


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
        findings += [
            messages.l1_list_item(rel, hit.line, hit.text)
            for hit in checks.examine_lists(text, dials.handles)
        ]
    tail = messages.f9_lists_tail(len(covered), len(dials.handles), len(paths))
    return pipeline.report_scan(output, findings, (), tail)
