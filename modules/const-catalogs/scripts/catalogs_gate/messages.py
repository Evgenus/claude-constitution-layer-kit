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

from const_gate.messages import shown
from const_gate.model import DIALS_FILE, Broken, EnvelopeState, Finding, SharedKey

from .model import DEFAULT_WIDTH, Catalog, Key

_DECLARATION = f"catalog: {{prefix: <lowercase letters and digits>, width: {DEFAULT_WIDTH}}}"


def _form(catalog: Catalog) -> str:
    return f"{catalog.prefix}-<{catalog.width} digits>-<kebab-slug>"


# ---------------------------------------------------------------- findings: one item


def k1_name_without_form(rel: str, stem: str, catalog: Catalog) -> Finding:
    return Finding(
        Key.K1,
        f"{rel}: file name '{shown(stem)}' is not {_form(catalog)}, the form of catalog"
        f" '{catalog.prefix}' (declared by policy {catalog.policy})",
        "an item of a numbered kind is cited by its number, and a citation resolves only when the"
        " number stands in the file's name, in one form for the whole catalog",
        f"name the file {catalog.prefix}-<number>-<slug>.md: the number is the catalog's highest plus"
        f" one, written with exactly {catalog.width} digits, zero-padded; the slug is lowercase words"
        " and digits joined by '-'; then set id to that name without .md",
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


# ---------------------------------------------------------------- count line and skips


def f9_scan_tail(items: int, scanned: int, catalogs: int) -> str:
    return f"{items} catalogued item(s) examined, {scanned} Markdown file(s) scanned, {catalogs} catalog(s)"


def g1_skip_no_catalog() -> str:
    return (
        "no catalog is declared, so no document is known to be numbered — to declare one, write"
        f" {_DECLARATION} under the id of the kind's policy in {DIALS_FILE}, beside its territory"
    )


def g1_skip_not_an_item(rel: str, catalogs: Sequence[Catalog]) -> str:
    declared = ", ".join(f"{c.prefix} by {c.policy}" for c in catalogs)
    return f"{rel} is not governed by a policy that declares a catalog ({declared})"


# ---------------------------------------------------------------- this module's dial failures


def c5_catalog_shape(policy_id: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {policy_id}.catalog must be a mapping of prefix, lowercase letters and"
        " digits, and an optional width, a whole number of at least 1, with no other key",
        f"write it as {policy_id}: {{{_DECLARATION}}}, or remove the key",
    )


def c5_prefix_declared_twice(prefix: str, first: str, second: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: prefix '{prefix}' is declared by both {first} and {second}",
        "one prefix names one catalog, or a number would cite two kinds: give one of the two another"
        " prefix — before it has items, since an id never changes",
    )
