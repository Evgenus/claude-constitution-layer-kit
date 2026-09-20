"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code; the checks themselves live in ``checks``. No policy is resolved here: a catalog's items
are the Markdown documents in the territory its dial entry declares."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import TextIO

from const_gate import messages as shared
from const_gate import pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import dials as catalog_dials
from . import messages
from .checks import catalog_of, examine, numbers_taken, shared_numbers, stem_of
from .history import HOOK_SECONDS, read_history
from .model import Catalog, Item, Key, Reach, Taken

NAMES_A_NUMBER = (Key.K1, Key.K4)  # the findings whose fix names the catalog's next number


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    catalogs = catalog_dials.parse(target.dials.own).catalogs
    if not catalogs:
        return pipeline.skip(output, messages.g1_skip_no_catalog())
    rel = target.rel
    taken: Taken | None = None
    with Matcher() as matcher:
        catalog = _catalogs_by_path(matcher, catalogs, [rel]).get(rel)
        if catalog is not None and not (target.root / rel).exists():  # a new item: its number must be free
            taken = _numbers_taken(matcher, catalogs, catalog, target.root)
    if catalog is None:
        return pipeline.skip(output, messages.g1_skip_not_an_item(rel, catalogs))
    item = examine(catalog, rel, target.text, taken)
    if taken is not None and any(finding.key in NAMES_A_NUMBER for finding in item.findings):
        # Only now is history worth reading: the verdict stands, and its fix is about to name a number.
        item = examine(catalog, rel, target.text, _with_history(taken, target.root))
    if item.findings:
        return pipeline.report_hook(output, item.findings, (), rel, target.dials.severity)
    return pipeline.green_hook(output, messages.g1_item_of(catalog))


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    catalogs = catalog_dials.parse(target.dials.own).catalogs
    if not catalogs:
        return pipeline.skip(output, messages.g1_skip_no_catalog())
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        by_path = _catalogs_by_path(matcher, catalogs, paths)
    items = [examine(catalog, rel, _text(target.root, rel)) for rel, catalog in sorted(by_path.items())]
    findings = [finding for item in items for finding in item.findings] + shared_numbers(items)
    history = read_history(target.root)
    reach = [Reach(catalog, _shown(catalog, items), history.highest(catalog)) for catalog in catalogs]
    tail = messages.f9_scan_tail(len(items), len(paths), reach, history.shallow)
    return pipeline.report_scan(output, findings, (), tail)


def _numbers_taken(matcher: Matcher, catalogs: Sequence[Catalog], catalog: Catalog, root: Path) -> Taken:
    """What a new item of `catalog` is judged against: the numbers its other items carry in the
    working tree."""
    by_path = _catalogs_by_path(matcher, catalogs, list_markdown(root))
    return numbers_taken(catalog, [rel for rel, its in by_path.items() if its == catalog])


def _with_history(taken: Taken, root: Path) -> Taken:
    history = read_history(root, HOOK_SECONDS)
    return replace(taken, in_history=history.highest(taken.catalog), history_read=history.complete)


def _shown(catalog: Catalog, items: Sequence[Item]) -> int | None:
    """The highest number any of the catalog's items shows, a malformed name's included: the next
    number goes above it, so that a legacy item's number is not given away before it is renamed."""
    numbers = [catalog.number_hinted(stem_of(item.rel)) for item in items if item.catalog == catalog]
    return max((number for number in numbers if number is not None), default=None)


def _catalogs_by_path(
    matcher: Matcher, catalogs: Sequence[Catalog], paths: Sequence[str]
) -> dict[str, Catalog]:
    """Each path that lies in some catalog's territory, with the catalog that judges it."""
    claiming: dict[str, list[Catalog]] = {}
    for catalog in catalogs:
        for rel in matcher.match(catalog.territory, paths):
            claiming.setdefault(rel, []).append(catalog)
    chosen = {rel: catalog_of(claimants, stem_of(rel)) for rel, claimants in claiming.items()}
    return {rel: catalog for rel, catalog in chosen.items() if catalog is not None}


def _text(root: Path, rel: str) -> str:
    """A file git lists and nobody can read is a configuration failure: a scan that skipped it
    would report a count it did not examine."""
    text = read_text(root, rel)
    if text is None:
        raise ConfigurationFailure(shared.c12_unreadable(rel))
    return text
