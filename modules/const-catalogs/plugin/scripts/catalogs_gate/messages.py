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

from constitution_layer_kit import identity
from constitution_layer_kit.messages import echoed, escaped
from constitution_layer_kit.model import DIALS_FILE, Broken, EnvelopeState, Finding, SharedKey

from .model import DEFAULT_WIDTH, MAX_WIDTH, Advice, Catalog, Key, NameToTake, Reach, Read

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

_SLUG = "the slug is lowercase words and digits joined by '-'"
_THEN_ID = "then set id to that name without .md"


def _name_to_take(catalog: Catalog, take: NameToTake) -> str:
    """The fix both findings about a name end in."""
    match take.advice:
        case Advice.NEXT:
            name = catalog.written(take.number or 0)
            reason = (
                f"{name} is the catalog's next number, one more than the highest it has held, deleted"
                " items included"
                if take.history_read
                else f"{name} is one more than the highest number seen — this clone's history is"
                " incomplete or could not be read (a shallow clone, a history too long to read in time,"
                " or a git that gave no list), so check that no deleted item went higher"
            )
            return f"name the file {name}-<slug>.md: {reason}; {_SLUG}; {_THEN_ID}"
        case Advice.KEEP:
            name = catalog.written(take.number or 0)
            return (
                f"rename the file with git mv to {name}-<slug>.md: it keeps its number, which others may"
                f" already cite, written in lowercase with exactly {catalog.width} digit(s), zero-padded;"
                f" {_SLUG}; {_THEN_ID}, and rewrite the links to the old name"
            )
        case Advice.CONTESTED:
            name = catalog.written(take.number or 0)
            return (
                f"the name shows number {take.number}, and so does {escaped(take.other)}: only one of the"
                f" two can be {name}. The one that others already cite by that number keeps it — rename it"
                f" with git mv to {name}-<slug>.md; the other takes one more than the highest the catalog has"
                f" held, which the scan's last line names; {_SLUG}; {_THEN_ID}"
            )
        case Advice.WIDE:
            return (
                f"no name can be given: the name shows number {take.number}, which {catalog.width}"
                " digit(s) cannot write. A wider width renames every item and every link to one — settle"
                " that with the project, or give this document a number the width can write"
            )
        case Advice.FULL:
            return (
                f"no name can be given: catalog '{catalog.prefix}' has used every number"
                f" {catalog.width} digit(s) can write. A wider width renames every item and every link to"
                " one — settle that with the project before writing this document"
            )
        case _:
            return (
                f"rename the file to {catalog.prefix}-<number>-<slug>.md: the number it is already cited"
                " by, or, if it has none, one more than the highest the catalog has held — the scan's"
                f" last line names it — written with exactly {catalog.width} digit(s), zero-padded;"
                f" {_SLUG}; {_THEN_ID}"
            )


def k1_name_without_form(rel: str, stem: str, catalog: Catalog, take: NameToTake) -> Finding:
    return Finding(
        Key.K1,
        f"{escaped(rel)}: file name '{echoed(stem)}' is not {_form(catalog)}, the form of catalog"
        f" '{catalog.prefix}', whose territory holds this file",
        "an item of a numbered kind is cited by its number, and a citation resolves only when the"
        " number stands in the file's name, in one form for the whole catalog",
        _name_to_take(catalog, take),
    )


def k4_number_taken(rel: str, catalog: Catalog, number: int, holder: str, take: NameToTake) -> Finding:
    return Finding(
        Key.K4,
        f"{escaped(rel)}: number {catalog.written(number)} is already carried by {escaped(holder)}",
        "a number cites one item; two items under one number make every reference to it ambiguous",
        f"{escaped(holder)} keeps its number; {_name_to_take(catalog, take)}",
    )


_K2_WHY = (
    "a catalogued document has one identifier: its id is its file name without .md, so a reference"
    " by id and a search by file name find the same document"
)


def k2_id_is_not_the_name(rel: str, stem: str, detail: str) -> Finding:
    """detail is one of the two field-level parts every gate shares — `id missing`, `id must be
    a quoted string …` — or `k2_differs`: each already begins with the field's name."""
    return Finding(
        Key.K2,
        f"{escaped(rel)}: {detail}",
        _K2_WHY,
        f"set id: {stem} in the YAML block between the two '---' lines that open the file; if other"
        " documents already cite the id as it stands, rename the file to match the id instead",
    )


def k2_differs(value: str, stem: str) -> str:
    return f"id '{echoed(value)}' differs from the file name '{stem}'"


def k2_no_envelope(rel: str, stem: str, state: EnvelopeState, yaml_detail: str = "") -> Finding:
    """state is NONE, UNTERMINATED or INVALID; yaml_detail says what YAML could not read."""
    match state:
        case EnvelopeState.UNTERMINATED:
            detail = "the file's YAML block is opened with '---' but never closed"
            fix = f"close the YAML block with a line holding only '---'; the block carries id: {stem}"
        case EnvelopeState.INVALID:
            detail = f"the block between the '---' lines is not readable YAML: {escaped(yaml_detail)}"
            fix = f"repair the YAML between the '---' lines; the block carries id: {stem}"
        case _:
            detail = "the file does not start with a '---' line"
            fix = f"start the file with a YAML block between two '---' lines carrying at least id: {stem}"
    return Finding(Key.K2, f"{escaped(rel)}: id cannot be read: {detail}", _K2_WHY, fix)


# ---------------------------------------------------------------- finding: one catalog


def k3_number_shared(catalog: Catalog, number: int, paths: Sequence[str]) -> Finding:
    return Finding(
        Key.K3,
        f"catalog '{catalog.prefix}': {len(paths)} items carry number {catalog.written(number)}:"
        f" {', '.join(escaped(p) for p in paths)}",
        "a number cites one item; two items under one number make every reference to it ambiguous",
        "the item already on the main branch keeps its number; every other one takes a number of its"
        " own, one more than the highest the catalog has held: rename its file, set its id to the new"
        " name, and rewrite the references to it made on its own branch; of two items both on the main"
        " branch, the one that landed second renumbers the same way, and every reference to it in the"
        " tree is rewritten",
    )


# ---------------------------------------------------------------- green line, count line, skips


def g1_item_of(catalog: Catalog) -> str:
    return f"an item of catalog '{catalog.prefix}'"


def f9_scan_tail(items: int, scanned: int, reach: Sequence[Reach], read: Read = Read.ALL) -> str:
    """Names, for every listed catalog, the highest number a name in its territory shows, and
    the highest in history where history went further: a new item's number is one more than the
    highest named. Where history was read in part or not at all, the line says so."""
    tail = (
        f"{items} catalogued item(s) examined, {scanned} Markdown file(s) scanned,"
        f" {len(reach)} catalog(s): {', '.join(_reach(r) for r in reach)}"
    )
    match read:
        case Read.SHALLOW:
            return tail + "; history incomplete in a shallow clone"
        case Read.NOT:
            return tail + "; history could not be read"
        case _:
            return tail


def _reach(reach: Reach) -> str:
    catalog = reach.catalog
    in_tree = f"up to {catalog.written(reach.in_tree)}" if reach.in_tree is not None else "none yet"
    full = " (full: the width can write no higher number)" if reach.full else ""
    if reach.in_history is None or reach.in_history <= (reach.in_tree or 0):
        return f"{catalog.prefix} {in_tree}{full}"
    return f"{catalog.prefix} {in_tree}, {catalog.written(reach.in_history)} in history{full}"


def g1_skip_no_catalog() -> str:
    return (
        f"{_ns()}.catalogs lists no catalog, so no document is known to be numbered — to declare"
        f" one, write {_declaration()} in {DIALS_FILE}"
    )


def g1_skip_not_an_item(rel: str, catalogs: Sequence[Catalog]) -> str:
    return f"{escaped(rel)} lies in no catalog's territory ({', '.join(c.prefix for c in catalogs)})"


# ---------------------------------------------------------------- session start: the visible zero (Z1)


def z1_empty() -> str:
    return f"{_ns()}: no document is examined — {_ns()}.catalogs is an empty list in {DIALS_FILE}"


def z1_no_dials(root: str) -> str:
    return (
        f"{_ns()}: no {DIALS_FILE} in {escaped(root)} — the catalog gate examines nothing there until"
        f" the file lists a catalog in {_ns()}.catalogs"
    )


def z1_no_repo(cwd: str) -> str:
    return f"{_ns()}: {escaped(cwd)} is not inside a git repository — the catalog gate examines nothing there"


def z1_prefix() -> str:
    return _ns()


def z1_could_not_run() -> str:
    return "BROKEN: the session-start line could not be printed — the gate's state is unknown"


# ---------------------------------------------------------------- this module's dial failures


def c5_catalogs_not_a_list() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.catalogs must be a list of catalogs",
        f"write it as {_declaration()}, or remove the key",
    )


def c5_catalog_entry(position: int, what: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: entry {position} of {_ns()}.catalogs {what}",
        f"write the entry as {_ENTRY}",
    )


# what is wrong with an entry: the parts of the C5 line above


def entry_not_a_mapping() -> str:
    return "is not a mapping of prefix, territory and width"


def entry_unknown_key(key: str) -> str:
    return f"carries the key '{echoed(key)}'; an entry holds prefix, territory and width, and nothing else"


def entry_prefix() -> str:
    return "needs a prefix of lowercase letters and digits — in quotes when it is all digits"


def entry_territory() -> str:
    return "needs a territory: a non-empty list of path patterns"


def entry_width() -> str:
    return f"has a width that is not a whole number from 1 to {MAX_WIDTH}"


def c5_prefix_listed_twice(prefix: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.catalogs lists prefix '{prefix}' twice",
        "one prefix names one catalog, or a number would cite two kinds: join the two entries'"
        " territories in one entry, or give one of them another prefix — before it has items, since"
        " an id never changes",
    )
