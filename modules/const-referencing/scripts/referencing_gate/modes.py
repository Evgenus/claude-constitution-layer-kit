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
from const_gate.index import build_index
from const_gate.model import POST_WRITE, PRE_WRITE, Finding, PendingDocument
from const_gate.output import Output
from const_gate.pipeline import ScanTarget, Skip, WriteTarget
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import dials as own_dials
from . import lint, mentions, messages, tree
from .model import Ids, Lane, ReferencingDials, Switch

SHOWN_AFTER_WRITE = 20  # findings printed after one write; the count line carries the total


def hook_mode(output: Output, stdin: TextIO) -> int:
    """Before the write: the forms of the document's references, which can block. After it: the
    whole tree, which cannot — the findings that involve the written document are feedback."""
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    if target.event_name not in (PRE_WRITE, POST_WRITE):
        raise ConfigurationFailure(messages.c12_event(target.event_name))
    dials = own_dials.parse(target.dials.own)
    if target.event_name == POST_WRITE:
        return _after_write(output, target, dials)
    rel = target.rel
    paths = sorted({*list_markdown(target.root), rel})
    with Matcher() as matcher:
        covered = covered_documents(matcher, dials, target, paths, PendingDocument(rel, target.text))
        if covered is None:
            raise ConfigurationFailure(messages.c5_governed_only_without_root())
        if rel not in covered:
            return pipeline.skip(output, messages.g1_skip_not_covered(rel))
        lanes = _lanes_abroad(matcher, dials, [rel])[rel]
    texts = {path: target.text if path == rel else _text(target.root, path) for path in covered}
    placed, _ = _examine(rel, texts, ids_of(texts), lanes, dials)
    findings = [finding for _, finding in placed]
    if findings:
        return pipeline.report_hook(output, findings, (), rel, target.dials.severity)
    return pipeline.green_hook(output, messages.g1_covered())


def _after_write(output: Output, target: WriteTarget, dials: ReferencingDials) -> int:
    """The written document need not be covered itself: covered documents may link into it, and
    a write that takes an anchor away breaks them all the same."""
    rel = target.rel
    with Matcher() as matcher:
        covered = covered_documents(matcher, dials, target, list_markdown(target.root))
    if covered is None:
        raise ConfigurationFailure(messages.c5_governed_only_without_root())
    texts = {path: _text(target.root, path) for path in covered}
    found, links = tree.examine(target.root, texts, dials.heading_anchors, about=rel)
    findings = [finding for path in sorted(found) for _, finding in found[path]]
    if not findings:
        if rel not in covered:
            return pipeline.skip(output, messages.g1_skip_not_covered(rel))
        return pipeline.green_hook(output, messages.g1_covered())
    shown = pipeline.within_the_cap(findings, most=SHOWN_AFTER_WRITE)
    cut = len(shown) if len(shown) < len(findings) else None
    count = "RED: " + messages.f9_after_write(rel, links, len(findings), cut)
    return pipeline.report_hook(output, shown, (), rel, target.dials.severity, POST_WRITE, count)


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        covered = covered_documents(matcher, dials, target, paths)
        if covered is None:
            raise ConfigurationFailure(messages.c5_governed_only_without_root())
        lanes = _lanes_abroad(matcher, dials, covered)
        texts = {path: _text(target.root, path) for path in covered}
        ids = ids_of(texts)
        others = mentions.other_files(target.root) if dials.mentions else []
        named, read = mentions.examine(target.root, others, dials.mentions, ids, matcher)
    in_tree, _ = tree.examine(target.root, texts, dials.heading_anchors)
    findings: list[Finding] = []
    links = 0
    for rel in covered:
        found, count = _examine(rel, texts, ids, lanes[rel], dials)
        in_order = sorted([*found, *in_tree.get(rel, [])], key=lambda pair: pair[0])  # stable: by line
        findings += [finding for _, finding in in_order]
        links += count
    tail = messages.f9_scan_tail(len(covered), links, len(paths), len(dials.lanes), len(dials.mentions), read)
    return pipeline.report_scan(output, [*findings, *named], (), tail)


def _examine(
    rel: str, texts: dict[str, str], ids: Ids, lanes: Sequence[Lane], dials: ReferencingDials
) -> tuple[list[tuple[int, Finding]], int]:
    text = texts[rel]
    return lint.examine(
        rel,
        text,
        id_of_text(text),
        ids,
        lanes,
        dials.bare_ids is Switch.REFUSE,
        dials.local_paths is Switch.REFUSE,
    )


def covered_documents(
    matcher: Matcher,
    dials: ReferencingDials,
    target: WriteTarget | ScanTarget,
    paths: Sequence[str],
    pending: PendingDocument | None = None,
) -> list[str] | None:
    """The covered documents: those the module's territories hold — and, under governed_only,
    that a policy governs too, the policies themselves included. None: governed_only is set and
    the dials name no root policy, so nobody can say what is governed — a configuration failure
    for the gate and a refusal for the mover, each in its own words, never a skip that lets a
    write through with nothing examined."""
    in_territory = sorted(matcher.match(dials.territories, paths))
    if not dials.governed_only:
        return in_territory
    root_policy = target.dials.root_policy
    if root_policy is None:
        return None
    index = build_index(target.root, target.dials, root_policy, matcher, pending)
    return [rel for rel in in_territory if rel in index.in_root or index.matches(rel)]


def _lanes_abroad(matcher: Matcher, dials: ReferencingDials, paths: Sequence[str]) -> dict[str, list[Lane]]:
    """For each document the lanes that judge it: all but those at home there."""
    abroad: dict[str, list[Lane]] = {path: [] for path in paths}
    for lane in dials.lanes:
        at_home = matcher.match(lane.home, paths)
        for path in paths:
            if path not in at_home:
                abroad[path].append(lane)
    return abroad


def ids_of(texts: dict[str, str]) -> Ids:
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
