"""The texts of this module's own findings, skips and dial failures, as functions with typed
parameters; the texts every gate shares live in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (k1_, g1_, c5_, ...), so a text can be
cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Sequence

from const_gate import identity
from const_gate.messages import shown
from const_gate.model import DIALS_FILE, Broken, EnvelopeState, Finding, SharedKey

from .model import DEFAULT_WIDTH, Catalog, Key

_ENTRY = (
    "{prefix: <lowercase letters and digits>, territory: [<patterns of the paths where the numbered"
    f" documents live>], width: {DEFAULT_WIDTH}}}"
)


def _ns() -> str:
    return identity.current().namespace


def _declaration() -> str:
    return f"{_ns()}: {{catalogs: [{_ENTRY}]}}"


def _form(catalog: Catalog) -> str:
    return f"{catalog.prefix}-<{catalog.width} digits>-<kebab-slug>"


# ---------------------------------------------------------------- findings: one item


def _name_to_take(catalog: Catalog, free: int | None) -> str:
    """The fix both findings about a name end in. `free` is the catalog's next free number,
    known when the file is new and the width can still write it."""
    if free is None:
        return (
            f"name the file {catalog.prefix}-<number>-<slug>.md: the number is the catalog's highest"
            f" plus one, written with exactly {catalog.width} digits, zero-padded; the slug is lowercase"
            " words and digits joined by '-'; then set id to that name without .md"
        )
    return (
        f"name the file {catalog.written(free)}-<slug>.md: {catalog.written(free)} is the catalog's next"
        " free number, its highest plus one; the slug is lowercase words and digits joined by '-';"
        " then set id to that name without .md"
    )


def k1_name_without_form(rel: str, stem: str, catalog: Catalog, free: int | None = None) -> Finding:
    return Finding(
        Key.K1,
        f"{rel}: file name '{shown(stem)}' is not {_form(catalog)}, the form of catalog"
        f" '{catalog.prefix}', whose territory holds this file",
        "an item of a numbered kind is cited by its number, and a citation resolves only when the"
        " number stands in the file's name, in one form for the whole catalog",
        _name_to_take(catalog, free),
    )


def k4_number_taken(rel: str, catalog: Catalog, number: int, holder: str, free: int | None) -> Finding:
    return Finding(
        Key.K4,
        f"{rel}: number {catalog.written(number)} is already carried by {holder}",
        "a number cites one item; two items under one number make every reference to it ambiguous",
        f"{holder} keeps its number; {_name_to_take(catalog, free)}",
    )


def k2_id_is_not_the_name(rel: str, stem: str, detail: str) -> Finding:
    return Finding(
        Key.K2,
        f"{rel}: id {detail}",
        "a catalogued document has one identifier: its id is its file name without .md, so a"
        " reference by id and a search by file name find the same document",
        f"set id: {stem} in the YAML block between the two '---' lines that open the file; if other"
        " documents already cite the id as it stands, rename the file to match the id instead",
    )


# the details of K2, beside the two field-level parts every gate shares


def k2_differs(value: str, stem: str) -> str:
    return f"'{shown(value)}' differs from the file name '{stem}'"


def k2_no_envelope(state: EnvelopeState, yaml_detail: str = "") -> str:
    """state is NONE, UNTERMINATED or INVALID; yaml_detail says what YAML could not read."""
    match state:
        case EnvelopeState.UNTERMINATED:
            return "cannot be read: the file's YAML block is opened with '---' but never closed"
        case EnvelopeState.INVALID:
            return f"cannot be read: the block between the '---' lines is not readable YAML: {yaml_detail}"
        case _:
            return "cannot be read: the file does not start with a '---' line"


# ---------------------------------------------------------------- finding: one catalog


def k3_number_shared(catalog: Catalog, number: int, paths: Sequence[str]) -> Finding:
    return Finding(
        Key.K3,
        f"catalog '{catalog.prefix}': {len(paths)} items carry number {catalog.written(number)}:"
        f" {', '.join(paths)}",
        "a number cites one item; two items under one number make every reference to it ambiguous",
        "an item already on the main branch keeps its number; the other takes the catalog's highest"
        " number plus one: rename its file, set its id to the new name, and rewrite the references to"
        " it made on its own branch",
    )


# ---------------------------------------------------------------- green line, count line, skips


def g1_item_of(catalog: Catalog) -> str:
    return f"an item of catalog '{catalog.prefix}'"


def f9_scan_tail(items: int, scanned: int, highest: Sequence[tuple[Catalog, int | None]]) -> str:
    """`highest` pairs every listed catalog with the highest number its items carry in the
    working tree, None while it has none: the number a new item's is one more than."""
    reached = ", ".join(
        f"{catalog.prefix} up to {catalog.written(number)}"
        if number is not None
        else f"{catalog.prefix} none yet"
        for catalog, number in highest
    )
    return (
        f"{items} catalogued item(s) examined, {scanned} Markdown file(s) scanned,"
        f" {len(highest)} catalog(s): {reached}"
    )


def g1_skip_no_catalog() -> str:
    return (
        f"{_ns()}.catalogs lists no catalog, so no document is known to be numbered — to declare"
        f" one, write {_declaration()} in {DIALS_FILE}"
    )


def g1_skip_not_an_item(rel: str, catalogs: Sequence[Catalog]) -> str:
    return f"{rel} lies in no catalog's territory ({', '.join(c.prefix for c in catalogs)})"


# ---------------------------------------------------------------- this module's dial failures


def c5_catalogs_not_a_list() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.catalogs must be a list of catalogs",
        f"write it as {_declaration()}, or remove the key",
    )


def c5_catalog_entry(position: int) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: entry {position} of {_ns()}.catalogs must be a mapping of prefix, lowercase"
        " letters and digits; territory, a non-empty list of path patterns; and an optional width, a"
        " whole number of at least 1 — with no other key",
        f"write the entry as {_ENTRY}",
    )


def c5_prefix_listed_twice(prefix: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.catalogs lists prefix '{prefix}' twice",
        "one prefix names one catalog, or a number would cite two kinds: join the two entries'"
        " territories in one entry, or give one of them another prefix — before it has items, since"
        " an id never changes",
    )
