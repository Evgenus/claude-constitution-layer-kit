"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code; the checks themselves live in ``checks``. No policy is resolved here: a catalog's items
are the Markdown documents in the territory its dial entry declares."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import TextIO

from constitution_layer_kit import identity, pipeline
from constitution_layer_kit import messages as shared
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.output import Output
from constitution_layer_kit.pipeline import Skip, WriteTarget
from constitution_layer_kit.repository import list_markdown, read_text
from constitution_layer_kit.territory import Matcher

from . import dials as catalog_dials
from . import messages
from .checks import catalog_of, examine, highest_shown, numbers_shown, numbers_taken, shared_numbers, stem_of
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
    with Matcher() as matcher:
        catalog = _catalogs_by_path(matcher, catalogs, [rel]).get(rel)
        if catalog is None:
            return pipeline.skip(output, messages.g1_skip_not_an_item(rel, catalogs))
        item = _examine_write(matcher, catalogs, catalog, target)
    if item.findings:
        return pipeline.report_hook(output, item.findings, (), rel, target.dials.severity)
    return pipeline.green_hook(output, messages.g1_item_of(catalog))


def _examine_write(
    matcher: Matcher, catalogs: Sequence[Catalog], catalog: Catalog, target: WriteTarget
) -> Item:
    """The verdict first, from the working tree alone. Only when it is a finding whose fix names
    a number is the advice gathered — history for a new file, the rivals for a file that exists —
    and the same verdict rendered again with it: advice costs a green write nothing, and no
    verdict waits for it."""
    root, rel, text = target.root, target.rel, target.text
    # a file that does not exist yet is a new item, and its number must be free
    taken = (
        None if (root / rel).exists() else numbers_taken(catalog, _items(matcher, catalogs, catalog, root))
    )
    item = examine(catalog, rel, text, taken)
    if not any(finding.key in NAMES_A_NUMBER for finding in item.findings):
        return item
    if taken is not None:
        return examine(catalog, rel, text, _with_history(taken, root))
    return examine(catalog, rel, text, shown=numbers_shown(catalog, _items(matcher, catalogs, catalog, root)))


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
    shown = {c.prefix: numbers_shown(c, [rel for rel, its in by_path.items() if its == c]) for c in catalogs}
    items = [
        examine(catalog, rel, _text(target.root, rel), shown=shown[catalog.prefix])
        for rel, catalog in sorted(by_path.items())
    ]
    findings = [finding for item in items for finding in item.findings] + shared_numbers(items)
    history = read_history(target.root)
    reach = [Reach(c, highest_shown(c, shown[c.prefix]), history.highest(c)) for c in catalogs]
    tail = messages.f9_scan_tail(len(items), len(paths), reach, history.read)
    return pipeline.report_scan(output, findings, (), tail)


def _items(matcher: Matcher, catalogs: Sequence[Catalog], catalog: Catalog, root: Path) -> list[str]:
    """The paths of the catalog's items in the working tree."""
    by_path = _catalogs_by_path(matcher, catalogs, list_markdown(root))
    return [rel for rel, its in by_path.items() if its == catalog]


def _with_history(taken: Taken, root: Path) -> Taken:
    """The hook's history read: its own `HOOK_SECONDS` at most, and no more than the hook's deadline has
    left (`left_of`, which never raises: the history is advice, and a deadline spent when it is asked starts
    no git and ends in the working tree's answer, history not read, the verdict standing); the read keeps
    its own clock inside that number."""
    history = read_history(root, identity.left_of(HOOK_SECONDS))
    return replace(taken, in_history=history.highest(taken.catalog), history_read=history.complete)


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
