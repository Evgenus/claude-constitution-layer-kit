"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code. No policy is resolved here: the covered documents are the Markdown files git lists
that the module's own territories hold."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from const_gate import messages as shared
from const_gate import pipeline
from const_gate.envelope import id_of_text
from const_gate.errors import ConfigurationFailure
from const_gate.model import Finding
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import dials as own_dials
from . import lint, messages
from .model import Ids, Lane, ReferencingDials, Switch


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    rel = target.rel
    paths = sorted({*list_markdown(target.root), rel})
    with Matcher() as matcher:
        covered = _covered(matcher, dials, paths)
        if rel not in covered:
            return pipeline.skip(output, messages.g1_skip_not_covered(rel))
        lanes = _lanes_abroad(matcher, dials, [rel])[rel]
    texts = {path: target.text if path == rel else _text(target.root, path) for path in covered}
    findings, _ = _examine(rel, texts, _ids(texts), lanes, dials)
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
        covered = _covered(matcher, dials, paths)
        lanes = _lanes_abroad(matcher, dials, covered)
    texts = {path: _text(target.root, path) for path in covered}
    ids = _ids(texts)
    findings: list[Finding] = []
    links = 0
    for rel in covered:
        found, count = _examine(rel, texts, ids, lanes[rel], dials)
        findings += found
        links += count
    tail = messages.f9_scan_tail(len(covered), links, len(paths), len(dials.lanes))
    return pipeline.report_scan(output, findings, (), tail)


def _examine(
    rel: str, texts: dict[str, str], ids: Ids, lanes: Sequence[Lane], dials: ReferencingDials
) -> tuple[list[Finding], int]:
    text = texts[rel]
    return lint.examine(rel, text, id_of_text(text), ids, lanes, dials.bare_ids is Switch.REFUSE)


def _covered(matcher: Matcher, dials: ReferencingDials, paths: Sequence[str]) -> list[str]:
    return sorted(matcher.match(dials.territories, paths))


def _lanes_abroad(matcher: Matcher, dials: ReferencingDials, paths: Sequence[str]) -> dict[str, list[Lane]]:
    """For each document the lanes that judge it: all but those at home there."""
    abroad: dict[str, list[Lane]] = {path: [] for path in paths}
    for lane in dials.lanes:
        at_home = matcher.match(lane.home, paths)
        for path in paths:
            if path not in at_home:
                abroad[path].append(lane)
    return abroad


def _ids(texts: dict[str, str]) -> Ids:
    """A document whose envelope cannot be read carries no id here; saying so is another gate's."""
    owners: dict[str, list[str]] = {}
    for path, text in sorted(texts.items()):
        doc_id = id_of_text(text)
        if doc_id is not None:
            owners.setdefault(doc_id, []).append(path)
    return Ids({doc_id: tuple(paths) for doc_id, paths in owners.items()})


def _text(root: Path, rel: str) -> str:
    """A file git lists and nobody can read is a configuration failure: a scan that skipped it
    would report a count it did not examine."""
    text = read_text(root, rel)
    if text is None:
        raise ConfigurationFailure(shared.c12_unreadable(rel))
    return text
