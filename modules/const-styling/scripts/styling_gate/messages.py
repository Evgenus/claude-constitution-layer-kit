"""The texts of this module's own findings, notes, count lines and dial failures, as functions
with typed parameters; the texts every gate shares live in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists (one
clause), and the exact fix; a configuration failure is one self-sufficient line. Every function
name starts with the stable key of its text (y1_ to y12_, n2_, f9_, c5_, c12_), so a text can be
cited, reviewed and asserted by key. A reader must be able to act on a message without holding
any other document: no text here cites one.
"""

from __future__ import annotations

from const_gate import identity
from const_gate.messages import shown
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import KEY_OF, Departure, Hit, Signature


def _ns() -> str:
    return identity.current().namespace


AMENDED = (
    "; where your guide changed this default, the pattern is your whole tree and the reason names"
    " the guide's entry"
)


def _allow(signature: Signature, what: str, *, default: bool = False) -> str:
    """The second half of every fix: how a departure is declared, with the reason it needs. For a
    signature that holds a shipped default, it adds how a project that changed the default says so."""
    return (
        f"or declare the departure with its reason: add to {_ns()}.departures in {DIALS_FILE} an entry"
        f" {{paths: [<the file, or a pattern of the documents that depart>], allow: [{signature.value}],"
        f" reason: <{what}>}}" + (AMENDED if default else "")
    )


# ---------------------------------------------------------------- the findings, one per signature


def finding(rel: str, hit: Hit) -> Finding:
    """The finding of a hit, by its signature."""
    return _BY_SIGNATURE[hit.signature](rel, hit.line, hit.text)


def y1_plantuml(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.PLANTUML],
        f"{rel}:{line}: PlantUML, where the shipped default is Mermaid — {shown(text)}",
        "Mermaid renders on GitHub, GitLab and in editor previews with no server; PlantUML needs one",
        "draw the diagram in a ```mermaid fence, "
        + _allow(Signature.PLANTUML, "the capability Mermaid lacks, in one line", default=True),
    )


def y2_formula(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.FORMULA],
        f"{rel}:{line}: a formula, where the shipped default is pseudocode — {shown(text)}",
        "a formula renders only in a web view and is invisible to a prose reader and a linter;"
        " pseudocode reads everywhere",
        "write the computation as pseudocode in a fenced block, "
        + _allow(Signature.FORMULA, "why this must be a formula, in one line", default=True),
    )


def y3_callout(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.CALLOUT],
        f"{rel}:{line}: a callout, where the shipped default is none — {shown(text)}",
        "a callout pulls a sentence out of its argument; an aside is a clause, and a warning about an act"
        " is a sentence where the act is described",
        "write the sentence in the paragraph it belongs to, "
        + _allow(
            Signature.CALLOUT, "why the reader must see this apart from the text, in one line", default=True
        ),
    )


def y4_deep_heading(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.DEEP_HEADING],
        f"{rel}:{line}: a heading of level {text}, deeper than the shipped default of three",
        "a fourth level is a section too small to stand on its own, and most renderers stop showing"
        " levels below three in a page's outline",
        "make it a bold run-in label at the start of a paragraph, or split the document, "
        + _allow(Signature.DEEP_HEADING, "why this document needs the level, in one line", default=True),
    )


def y5_skipped_level(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.SKIPPED_LEVEL],
        f"{rel}:{line}: a heading of level {text}, skipping a level",
        "a skipped level makes a section look nested in one that does not exist, and an outline built from"
        " the headings mis-nests it",
        "use the next level down from the heading before it, "
        + _allow(Signature.SKIPPED_LEVEL, "why the levels are read this way here, in one line"),
    )


def y6_second_h1(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.SECOND_H1],
        f"{rel}:{line}: a second level-one heading — {shown(text)}",
        "a document has one title; a second level-one heading is a second document or a section",
        "make it a level-two heading, or move what follows it into a document of its own, "
        + _allow(Signature.SECOND_H1, "why this document carries two titles, in one line"),
    )


def y7_fence_language(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.FENCE_LANGUAGE],
        f"{rel}:{line}: a fenced block that names no language",
        "the language after the fence tells a renderer how to highlight the block and a reader what it is"
        " looking at; without it every viewer guesses",
        "name the language after the opening fence — ```bash, ```yaml, ```text for a directory tree or"
        " plain output, " + _allow(Signature.FENCE_LANGUAGE, "why no language fits this block, in one line"),
    )


def y8_list_marker(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.LIST_MARKER],
        f"{rel}:{line}: a bullet item whose marker is not the shipped default, a dash — {shown(text)}",
        "one marker for every bullet list keeps the source uniform, so a diff shows a change of content"
        " and never a change of marker",
        "open the item with the shipped default, '- ', "
        + _allow(Signature.LIST_MARKER, "why this list keeps its marker, in one line", default=True),
    )


def y9_list_numbering(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.LIST_NUMBERING],
        f"{rel}:{line}: an ordered item numbered {text}",
        "an item is cited by the number written in the source, so the numbers must be the ones a reader"
        " sees: each the one before it plus one, never all ones and never a jump",
        "renumber the list so that each item is the one before it plus one, or start a new list after a"
        " paragraph, " + _allow(Signature.LIST_NUMBERING, "why this list is numbered so, in one line"),
    )


def y10_underscore_emphasis(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.UNDERSCORE_EMPHASIS],
        f"{rel}:{line}: emphasis by underscores — {shown(text)}",
        "one emphasis marker keeps the source uniform, and an underscore inside a word or a name is text,"
        " which a second marker makes ambiguous",
        "use the shipped default, *italic* and **bold**; put a name that carries underscores in a"
        " code span, "
        + _allow(
            Signature.UNDERSCORE_EMPHASIS, "why this document marks emphasis so, in one line", default=True
        ),
    )


def y11_table_columns(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.TABLE_COLUMNS],
        f"{rel}:{line}: a table row with {text}",
        "a row with more or fewer cells than the header puts values under the wrong heads, or drops them"
        " in silence, in every renderer",
        "give the row exactly one cell per column of the header, a backslash before a pipe that belongs"
        " inside a cell, " + _allow(Signature.TABLE_COLUMNS, "why this table's rows differ, in one line"),
    )


def y12_table_empty_cell(rel: str, line: int, text: str) -> Finding:
    return Finding(
        KEY_OF[Signature.TABLE_EMPTY_CELL],
        f"{rel}:{line}: an empty cell in column {text}",
        "an empty cell does not say whether the value is none, unknown or forgotten",
        "write none, or the value, in the cell, "
        + _allow(Signature.TABLE_EMPTY_CELL, "what an empty cell means in this table, in one line"),
    )


_BY_SIGNATURE = {
    Signature.PLANTUML: y1_plantuml,
    Signature.FORMULA: y2_formula,
    Signature.CALLOUT: y3_callout,
    Signature.DEEP_HEADING: y4_deep_heading,
    Signature.SKIPPED_LEVEL: y5_skipped_level,
    Signature.SECOND_H1: y6_second_h1,
    Signature.FENCE_LANGUAGE: y7_fence_language,
    Signature.LIST_MARKER: y8_list_marker,
    Signature.LIST_NUMBERING: y9_list_numbering,
    Signature.UNDERSCORE_EMPHASIS: y10_underscore_emphasis,
    Signature.TABLE_COLUMNS: y11_table_columns,
    Signature.TABLE_EMPTY_CELL: y12_table_empty_cell,
}


# ---------------------------------------------------------------- notes and count


def n2_stale_departure(index: int, departure: Departure) -> str:
    return (
        f"note: {_ns()}.departures entry {index} ({', '.join(departure.paths)}) matches no covered"
        " document; the documents it allowed were deleted or moved, or the pattern is wrong"
    )


def f9_tail(documents: int, signatures: int, departures: int, scanned: int) -> str:
    return (
        f"{documents} document(s) examined for {signatures} signature(s) under {departures} departure(s),"
        f" {scanned} Markdown file(s) scanned"
    )


# ---------------------------------------------------------------- this module's dial failures (C5)


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_territories() -> Broken:
    return _c5(
        f"{_ns()}.territories must be a non-empty list of path patterns",
        'write the patterns of the documents to scan, one per line under "- ", or leave the key out to'
        " cover every Markdown file; an empty list would examine nothing in silence",
    )


def c5_guides() -> Broken:
    return _c5(
        f"{_ns()}.guides must be a list of path patterns",
        'write the patterns of the style guides, one per line under "- ", or leave the key out; the'
        " scan reads nothing from them — the skill does",
    )


def c5_departures() -> Broken:
    return _c5(
        f"{_ns()}.departures must be a list of entries",
        'write one entry per "- " item with the fields paths (a list of patterns), allow (a list of'
        " signature keys) and reason (one line); leave the key out, or write [], for no departure",
    )


def c5_departure(index: int, detail: str) -> Broken:
    return _c5(
        f"{_ns()}.departures entry {index}: {detail}",
        "write the entry as paths: [<patterns>], allow: [<signature keys>], reason: <one line saying why"
        " these documents depart>; the keys are " + ", ".join(s.value for s in Signature),
    )


# ---------------------------------------------------------------- this module's own C12


def c12_hook() -> Broken:
    return Broken(
        SharedKey.C12,
        "this check has no hook mode: it scans a tree and judges no single write",
        "run it with --scan [<dir>]; the plugin wires it to no event",
    )
