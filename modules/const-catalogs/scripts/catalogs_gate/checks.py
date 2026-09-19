"""The checks, as functions of typed inputs: is this document an item of a catalog, has its
file name the catalog's form, is its id that name — and, over a whole catalog, does any number
stand on two items."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from pathlib import PurePosixPath

from const_gate.envelope import parse_envelope, string_field
from const_gate.index import Index
from const_gate.model import Envelope, EnvelopeState, Examination, Finding, Resolution
from const_gate.resolution import resolve

from . import messages
from .model import Catalog, Item


def catalog_of(resolution: Resolution, catalogs: Sequence[Catalog], stem: str) -> Catalog | None:
    """The catalog the document is an item of, or None. Where the resolution is a defect — an
    overlap nobody resolved, a declaration against the path — every policy whose territory
    matches still counts: the defect is another check's. Of several catalogs that claim one
    document, the one whose prefix the file name carries is taken, else the first."""
    governing = (
        [resolution.policy] if resolution.policy is not None else [m.policy_id for m in resolution.matches]
    )
    claiming = [catalog for catalog in catalogs if catalog.policy in governing]
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


def examine(
    index: Index, catalogs: Sequence[Catalog], rel: str, text: str
) -> tuple[Examination, Item | None]:
    envelope = parse_envelope(text)
    stem = stem_of(rel)
    if rel in index.in_root:  # where policies live: a policy, whatever else claims the path
        catalog = next((c for c in catalogs if c.policy == index.root_id), None)
    else:
        catalog = catalog_of(resolve(index, rel, envelope), catalogs, stem)
    if catalog is None:
        return Examination((), None), None
    number = catalog.number_of(stem)
    findings = (
        [messages.k1_name_without_form(rel, stem, catalog)]
        if number is None
        else check_id(rel, stem, envelope)
    )
    return Examination(tuple(findings), catalog.policy), Item(rel, catalog, number)


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
