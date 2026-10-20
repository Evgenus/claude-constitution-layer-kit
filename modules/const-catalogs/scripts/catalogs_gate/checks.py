"""The checks, as functions of typed inputs: has an item's file name the catalog's form, is
its id that name, is a new item's number free — and, over a whole catalog, does any number
stand on two items. Which catalog a document is an item of is decided by the modes, who hold
the territory matcher."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import PurePosixPath

from constitution_layer_kit.envelope import parse_envelope, string_field
from constitution_layer_kit.model import Envelope, EnvelopeState, Finding

from . import messages
from .model import EXTENSION, Advice, Catalog, Item, NameToTake, Taken

Shown = Mapping[int, Sequence[str]]  # a number, and the paths whose names show it


def catalog_of(claiming: Sequence[Catalog], stem: str) -> Catalog | None:
    """Of several catalogs whose territories hold one document, the one whose prefix the file
    name carries judges it, else the first listed; of none, None."""
    carried = next((c for c in claiming if stem.startswith(c.prefix + "-")), None)
    return carried or next(iter(claiming), None)


def check_id(rel: str, stem: str, envelope: Envelope) -> list[Finding]:
    if envelope.state is not EnvelopeState.OK:
        return [messages.k2_no_envelope(rel, stem, envelope.state, envelope.detail)]
    errors: list[str] = []
    doc_id = string_field(envelope, "id", errors)
    if doc_id is not None and doc_id != stem:
        errors.append(messages.k2_differs(doc_id, stem))
    return [messages.k2_id_is_not_the_name(rel, stem, error) for error in errors]


def stem_of(rel: str) -> str:
    """The file name without `.md`. An extension in another case is no part of the form, so it
    stays in the stem, where the form refuses it."""
    name = PurePosixPath(rel).name
    return name[: -len(EXTENSION)] if name.endswith(EXTENSION) else name


def name_to_take(catalog: Catalog, rel: str, taken: Taken | None, shown: Shown | None) -> NameToTake:
    """`taken` is given for a file that does not exist yet, which takes the catalog's next
    number. A file that exists keeps the number its name shows — it may be cited by it —
    unless the width cannot write it, or another file of the catalog shows it too (`shown`)."""
    if taken is not None:
        free = taken.next
        return NameToTake(Advice.NEXT if free is not None else Advice.FULL, free, taken.history_read)
    number = catalog.number_shown(stem_of(rel))
    if number is None:
        return NameToTake(Advice.WORDS)
    if not catalog.can_write(number):
        return NameToTake(Advice.WIDE, number)
    other = next((path for path in (shown or {}).get(number, ()) if path != rel), None)
    if other is not None:
        return NameToTake(Advice.CONTESTED, number, other=other)
    return NameToTake(Advice.KEEP, number)


def examine(
    catalog: Catalog, rel: str, text: str, taken: Taken | None = None, shown: Shown | None = None
) -> Item:
    """`taken` is given for a file that does not exist yet: only then is a number that another
    item carries refused. An item that exists is judged on its name and its id; which of two
    that collide keeps its number is a question of branches, which the scan's finding answers.
    `shown` changes no verdict: it lets the fix of a malformed name that exists see its rivals."""
    stem = stem_of(rel)
    number = catalog.number_of(stem)
    if number is None:
        take = name_to_take(catalog, rel, taken, shown)
        findings = [messages.k1_name_without_form(rel, stem, catalog, take)]
    elif taken is not None and number in taken.holders:
        take = name_to_take(catalog, rel, taken, shown)
        findings = [messages.k4_number_taken(rel, catalog, number, taken.holders[number], take)]
    else:
        findings = check_id(rel, stem, parse_envelope(text))
    return Item(rel, catalog, number, tuple(findings))


def numbers_shown(catalog: Catalog, paths: Sequence[str]) -> Shown:
    """Every number a name among `paths` shows, formed or not, with the paths that show it."""
    shown: dict[int, list[str]] = defaultdict(list)
    for rel in sorted(paths):
        number = catalog.number_shown(stem_of(rel))
        if number is not None:
            shown[number].append(rel)
    return shown


def numbers_taken(catalog: Catalog, others: Sequence[str]) -> Taken:
    """`others` are the paths of the catalog's other items. Of two that already share a number,
    the first by path is named as its holder."""
    holders: dict[int, str] = {}
    for rel in sorted(others):
        number = catalog.number_of(stem_of(rel))
        if number is not None:
            holders.setdefault(number, rel)
    return Taken(catalog, holders, highest_shown(catalog, numbers_shown(catalog, others)))


def highest_shown(catalog: Catalog, shown: Shown) -> int | None:
    """The highest number the width can write: one it cannot write is nobody's neighbour."""
    return max((number for number in shown if catalog.can_write(number)), default=None)


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
