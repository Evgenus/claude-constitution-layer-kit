"""The checks, as functions of typed inputs: has an item's file name the catalog's form, is
its id that name — and, over a whole catalog, does any number stand on two items. Which
catalog a document is an item of is decided by the modes, who hold the territory matcher."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from pathlib import PurePosixPath

from const_gate.envelope import parse_envelope, string_field
from const_gate.model import Envelope, EnvelopeState, Finding

from . import messages
from .model import Catalog, Item


def catalog_of(claiming: Sequence[Catalog], stem: str) -> Catalog | None:
    """Of several catalogs whose territories hold one document, the one whose prefix the file
    name carries judges it, else the first listed; of none, None."""
    carried = next((c for c in claiming if stem.startswith(c.prefix + "-")), None)
    return carried or next(iter(claiming), None)


def check_id(rel: str, stem: str, envelope: Envelope) -> list[Finding]:
    if envelope.state is not EnvelopeState.OK:
        detail = messages.k2_no_envelope(envelope.state, envelope.detail)
        return [messages.k2_id_is_not_the_name(rel, stem, detail)]
    errors: list[str] = []
    doc_id = string_field(envelope, "id", errors)
    if doc_id is not None and doc_id != stem:
        errors.append(messages.k2_differs(doc_id, stem))
    return [messages.k2_id_is_not_the_name(rel, stem, error) for error in errors]


def stem_of(rel: str) -> str:
    return PurePosixPath(rel).name[: -len(".md")]  # only Markdown documents reach a check


def examine(catalog: Catalog, rel: str, text: str) -> Item:
    stem = stem_of(rel)
    number = catalog.number_of(stem)
    findings = (
        [messages.k1_name_without_form(rel, stem, catalog)]
        if number is None
        else check_id(rel, stem, parse_envelope(text))
    )
    return Item(rel, catalog, number, tuple(findings))


def shared_numbers(items: Sequence[Item]) -> list[Finding]:
    """One finding per number that stands on more than one item of a catalog."""
    carriers: dict[tuple[str, int], list[Item]] = defaultdict(list)
    for item in items:
        if item.number is not None:
            carriers[item.catalog.prefix, item.number].append(item)
    return [
        messages.k3_number_shared(group[0].catalog, number, sorted(item.rel for item in group))
        for (_prefix, number), group in sorted(carriers.items())
        if len(group) > 1
    ]
