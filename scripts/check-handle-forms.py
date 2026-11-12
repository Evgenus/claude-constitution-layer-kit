#!/usr/bin/env python3
"""Kit check: the forms in which a document names a handle of another document.

One scan over the Markdown files git lists, one rule function per form; each rule returns its
findings and the scan reports them all. Four rules are read:

  ruling citations  a citation of a ruling of a decision record from another document links the
                    ruling's anchor, the record's id the link's text: `R7 of [dec-…](…#r7)`
                    (rule 2 of plc-0004-decision-records). Several rulings named at once link the
                    first: `R5 and R34 of [dec-…](…#r5)`, `R18 to R27 of [dec-…](…#r18)`. Three
                    findings:
                    (a) a list of rulings, then " of ", then a link to a decision record whose
                        fragment is missing or is not `#r<n>` of the first ruling of the list;
                    (b) a link to a decision record, then " R<n>" or "'s R<n>" on the same line,
                        whose fragment is missing or is not `#r<n>`;
                    (c) a list of rulings, then " of ", then a record's id with no link at all.
                    A list is handles joined by ", ", " and ", " or ", " to " or "–". A link leads to
                    a decision record when its file is named `dec-<four digits>-….md`. A range takes
                    an unspaced dash, as the kit writes its ranges: in `R2 – R3 of [dec-…](…)` form
                    (a) reads R3 alone, so where a spaced dash stands right before the list, the
                    finding quotes the whole citation and its fix says to close up the dash and link
                    the anchor of the range's first ruling, never R3's, which would be green and wrong.

  message keys      a module's own message table (its MODULE.md §6, anchor t6) takes a key of the
                    shared table (shared/MESSAGES.md, anchor g3) only to state the module's part of
                    that message, and only the keys named in the paragraph of anchor g3a. A key's
                    family is its letters and its first number: `C5.a` and `C5.10` are family C5,
                    `C4b` is family C4. Finding: a key of the module's table whose family is a
                    family of the shared table and not one of the paragraph's keys. The check reads
                    the shared keys from the first column of the table of shared/MESSAGES.md and the
                    allowed ones from the code spans of the paragraph of g3a, so the
                    page is the one source.

  handle prefixes   one prefix per kind of handle in a module document (rule 8 of
                    plc-0006-module-documents). A prefix is the capital letters before the number
                    (`T1` is T). The kinds read: the message keys of the table of anchor t6, the
                    enforcement rows of anchor t9, and the acceptance items of anchor t10, the first
                    cell of each row; the live, review and kit-check items may continue the fixture
                    items' numbering under T, so those are one kind. Finding: a prefix that two kinds
                    of one document use. The prefixes the document uses are compared, never the
                    letters a policy reserves; bare numbers have no prefix, a path in a cell
                    (`hooks/V1.json`) holds no handle, and the advisory rules' `T-a` form is another
                    prefix and not read. The fix names the kind that moves: rule 8 fixes E for the
                    enforcement rows and T, S, L or V for the acceptance items, and the message keys
                    are the module's own (its messages.py). The kind that moves is the one that uses
                    a prefix rule 8 gives to another kind; where rule 8 gives the prefix to none of
                    the kinds that use it, each kind it fixes moves; the message keys move only when
                    rule 8 gives the prefix to the other kind. The one prefix of two owners is L:
                    rule 8 gives the live, review and kit-check items L, and V where L is the
                    module's message prefix, so where the message keys and the acceptance items both
                    use L, the acceptance items move and the message keys stay.
                    The fix names what applies to that pair alone.

  table keys        from the record that brought the sentence of rule 10 of plc-0004-decision-records
                    (number 39), handles are unique in a record, tables included. Finding: in a
                    record numbered 39 or above, a table row whose first cell has the form of a ruling
                    handle: its first handle is `R<n>`, in bold or in a code span, alone, in a range
                    (`R2–R3`, `R2-R3`), in a list (`R4, R5`) or followed by other words (`R7 (x)`),
                    outside fenced code and outside the "Carry list" section. A first cell that writes
                    the handle as a key of another document stays: `R1 of the module`, a range or a
                    list it opens qualified so (`R2–R3 of the module`, `R4, R5 of the module`), or a
                    handle after "message", "key" or "row". A range qualified so takes an unspaced
                    dash, as the kit writes its ranges: in `R2 – R3 of the module` the "of" follows
                    R3 alone, and the row is red. An earlier record is not read.

Not read: the research comparisons (docs/research/), which keep the form they were frozen with
(rule 7 of plc-0005-research); and in every other document a section titled "Carry list", under a
"#" heading of any level, whose links in a record lead to no record; fenced code, indented code, inline code
spans and HTML comments. The two module rules read only the tables of anchors t6, t9 and t10 of
each modules/<name>/MODULE.md, the first of them t6 alone, and fail loud (BROKEN, with the fix)
where a section, the shared messages page or its anchors g3 and g3a cannot be read.
Not a ruling: a handle after a word that names another kind of key, "message R4 of …" or "the
table keys R1 to R4 of …" (rule 10 of plc-0004 writes such a key qualified). Left to review: a
handle with a suffix letter (`R4b`), a record's citation of its own rulings ("R3",
"R3 of this record"), and an indirect one ("that record's R3").

Modes:  no arguments   check the kit;
        --self-test    prove each form red and its correct spelling green on a throwaway
                       repository, with the findings' lines typed by hand; every place not read
                       green; the report of one finding of each kind as literal lines with exit 2;
                       a file that is not UTF-8 and a misinvocation as BROKEN lines.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Collection
from dataclasses import dataclass, field
from pathlib import Path

from kit_module_doc import SEPARATOR, SPAN, DocumentError, cells, section

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

NOT_READ = ("docs/research/",)  # frozen comparisons keep their form (rule 7 of plc-0005-research)
LAST_SECTION = "Carry list"  # the record section whose links lead to no record
SP = r"(?:[ \t]+|[ \t]*\n[ \t>]*)"  # one space, or a line break of a wrapped paragraph
SEP = rf"(?:,{SP}(?:(?:and|or){SP})?|{SP}(?:and|or|to){SP}|[–—-])"
CITE = rf"(?<![\w.])R(\d+)(?![A-Za-z0-9])(?:{SEP}R\d+[a-z]?)*{SP}of{SP}"
LINK = (
    r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]"
    r"\(\s*<?([^()\s<>]*)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
CITED_LINK = re.compile(CITE + LINK)  # (a)
LINK_THEN_HANDLE = re.compile(LINK + r"(?:['’]s)?[ \t]+R(\d+)(?![A-Za-z0-9])")  # (b), on one line
CITED_BARE = re.compile(CITE + r"(dec-\d{4}(?:-[a-z0-9-]*[a-z0-9])?)")  # (c)
# the words that make a handle a qualified key of another kind, no ruling (rule 10 of plc-0004):
# "message R4 of …", "the table keys R1 to R4 of …"
QUALIFIERS = frozenset(
    {"key", "keys", "message", "messages", "row", "rows"}
)  # never "item": rulings are items
WORD_BEFORE = re.compile(r"([A-Za-z]+)[ \t]*\n?[ \t>]*$")
RECORD_FILE = re.compile(r"(?:^|/)dec-\d{4}-[^/#?]*\.md$")
TICKS = re.compile(r"`+")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")
LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d{1,9}[.)])[ \t]")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SHARED_DOC = "shared/MESSAGES.md"  # the shared messages: the table after anchor g3, its allowed keys at g3a
MODULE_DOC = re.compile(r"modules/[^/]+/MODULE\.md")
KEY = r"[A-Z]+\d+[A-Za-z0-9]*(?:\.[A-Za-z0-9]+)*"  # a message key: C11, C5.a, C5.10, C4b
KEY_FULL = re.compile(KEY)
KEY_IN_CELL = re.compile(rf"(?<![\w.]){KEY}")
FAMILY = re.compile(r"[A-Z]+\d+")  # the letters and the first number of a key
# a handle of a table's first cell: T1, S101, L1b, bold or not; the part of a path (hooks/V1.json) is none
HANDLE_IN_CELL = re.compile(r"(?<![\w./])([A-Z]+)\d+")
KIND_MESSAGE = "message keys"
KIND_ENFORCEMENT = "enforcement rows"
KIND_ACCEPTANCE = "acceptance items"  # fixture, live, review and kit-check items alike: they may share T
# the prefixes rule 8 of plc-0006-module-documents fixes for a kind; the message keys are the module's own
FIXED_PREFIXES: dict[str, tuple[str, ...]] = {
    KIND_ENFORCEMENT: ("E",),
    KIND_ACCEPTANCE: ("T", "S", "L", "V"),
}
LIVE_PREFIX = "L"  # the live, review and kit-check items' prefix, the message keys' where they use it
ITEM_PREFIX_BESIDE_L = "V"  # and theirs where L is the module's message prefix
COUNT_WORDS = {2: "two", 3: "three"}
RECORD_NUMBER = re.compile(r"(?:^|/)dec-(\d{4})-[^/#?]*\.md$")
UNIQUE_FROM = 39  # the record that brought the sentence of rule 10 of plc-0004-decision-records:
# handles run in order, contiguous and unique in the record, tables included
# the first handle of a table row's first cell, its bold marks and backticks taken off: R3, R2–R3, R7 (x)
CELL_HANDLE = re.compile(r"(?<![\w./])([A-Z]+)(\d+)(?![A-Za-z0-9]|\.[A-Za-z]|/)")
OF_AFTER = re.compile(r"[ \t]+of\b")  # "R1 of the module": a key of another document
RUN_REST = re.compile(rf"(?:{SEP}R\d+[a-z]?)*")  # the rest of a range or a list a handle opens: "–R3", ", R5"
# a range or a list that ends in a spaced dash right before a citation of form (a): "R1, R2 – " of
# "R1, R2 – R3 of …", which (a) reads as a citation of R3 alone; its first ruling, and the handle
# before the dash
SPACED_BEFORE = re.compile(rf"(?<![\w.])R(\d+)[a-z]?(?:{SEP}R(\d+)[a-z]?)*{SP}[–—-]{SP}\Z")
SPACED_REACH = 300  # how far back from a citation the spaced run is looked for, in characters
WHY = (
    "a link to the ruling's own anchor takes a reader to the ruling in one click, and a record moved"
    " by the mover is repaired in every link (rule 2 of plc-0004-decision-records)"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


KEY_WHY = (
    "one key names one message in every module, so a reader who meets the key in a log or a document"
    " finds the same message wherever it stands (paragraph g3a of shared/MESSAGES.md)"
)


PREFIX_WHY = (
    "one prefix names one kind of handle in a document, so a reader who meets L1 or T3 knows at once"
    " which table to open (rule 8 of plc-0006-module-documents)"
)
TABLE_WHY = (
    "a handle names one thing in a record, so a table row keyed R3 beside a ruling R3 leaves a citation"
    " of R3 with two readings (rule 10 of plc-0004-decision-records)"
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    what: str
    fix: str
    why: str = WHY

    def render(self) -> str:
        return f"RED: {self.path}:{self.line}: {self.what}\n  why: {self.why}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Document:
    path: str
    text: str  # as written
    masked: str  # the same length, with every place not read blanked; line breaks kept

    def line_of(self, offset: int) -> int:
        return self.masked.count("\n", 0, offset) + 1


@dataclass(frozen=True)
class Context:
    root: Path  # the checkout read, for a rule that reads a document it was not handed
    tracked: tuple[str, ...]  # every Markdown file git lists, for a rule that resolves a name
    # what a rule read once for the whole scan: "shared" holds the families of the shared messages
    cache: dict[str, tuple[frozenset[str], frozenset[str]]] = field(default_factory=dict)


Rule = Callable[[Document, Context], list[Finding]]


def listed_markdown(root: Path) -> list[str]:
    try:
        done = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.md"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as missing:
        raise Broken("git is not on PATH — fix: install git, then run the check again") from missing
    if done.returncode != 0:
        first = (done.stderr.splitlines() or ["no message"])[0]
        raise Broken(f"git ls-files failed: {first} — fix: run the check from a checkout of the kit")
    return sorted(p for p in done.stdout.split("\0") if p and (root / p).is_file())


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


def blank(text: str) -> str:
    return "".join(c if c == "\n" else " " for c in text)


def code_spans(line: str) -> list[tuple[int, int]]:
    """Where the code spans of one line stand: a run of backticks closed by the next run of the
    same length, as CommonMark reads them."""
    spans: list[tuple[int, int]] = []
    runs = list(TICKS.finditer(line))
    i = 0
    while i < len(runs):
        close = next((j for j in range(i + 1, len(runs)) if len(runs[j][0]) == len(runs[i][0])), None)
        if close is None:
            i += 1
            continue
        spans.append((runs[i].start(), runs[close].end()))
        i = close + 1
    return spans


def mask(text: str) -> str:
    """The text with every place no rule reads blanked: fenced blocks, indented code blocks (a
    block after a blank line, outside a list item), the section "Carry list" up to the next heading
    of its level or a higher one, HTML comments, and inline code spans."""
    kept: list[str] = []
    fence: str | None = None
    carry_level: int | None = None
    in_list = False
    after_blank = True  # the line before was blank, or there was none
    in_code = False  # the last line that is not blank was indented code
    for line in text.split("\n"):
        opener = FENCE.match(line)
        if fence is not None:  # a closing fence carries no info string
            if opener and opener[1][0] == fence[0] and len(opener[1]) >= len(fence) and not opener[2].strip():
                fence = None
            kept.append(blank(line))
            continue
        if opener:
            fence = opener[1]
            kept.append(blank(line))
            continue
        if not line.strip():
            after_blank = True
            kept.append(line)
            continue
        indented = line.startswith(("    ", "\t"))
        if indented and (in_code or (after_blank and not in_list)):
            in_code = True
            after_blank = False
            kept.append(blank(line))
            continue
        in_code = False
        after_blank = False
        if LIST_ITEM.match(line):
            in_list = True
        elif not line[0].isspace():
            in_list = False
        heading = HEADING.match(line)
        if heading:
            if carry_level is not None and len(heading[1]) <= carry_level:
                carry_level = None
            if carry_level is None and heading[2] == LAST_SECTION:
                carry_level = len(heading[1])
        kept.append(blank(line) if carry_level is not None else line)
    joined = HTML_COMMENT.sub(lambda m: blank(m[0]), "\n".join(kept))
    lines = joined.split("\n")
    for number, line in enumerate(lines):
        for start, end in code_spans(line):
            line = line[:start] + " " * (end - start) + line[end:]
        lines[number] = line
    return "\n".join(lines)


def split_fragment(destination: str) -> tuple[str, str | None]:
    path, hash_mark, fragment = destination.partition("#")
    return path, fragment if hash_mark else None


def shown(text: str) -> str:
    return " ".join(text.split())


def linked_wrongly(
    document: Document,
    start: int,
    end: int,
    destination: str,
    number: str,
    spaced: re.Match[str] | None = None,
) -> Finding | None:
    """A finding when the link's fragment is not the anchor of R<number>. With spaced, the run that ends
    in a spaced dash right before start, the fix names the range's own first ruling, never R<number>."""
    path, fragment = split_fragment(destination)
    anchor = f"r{number}"
    if not RECORD_FILE.search(path) or fragment == anchor:
        return None
    got = "no anchor" if fragment is None else f'"#{fragment}"'
    if spaced is None:
        return Finding(
            document.path,
            document.line_of(start),
            f'the citation "{shown(document.text[start:end])}" links {got} where the anchor of R{number}'
            f' is "#{anchor}"',
            f"link the anchor of the first ruling named, with the destination {path}#{anchor}",
        )
    before = spaced[2] or spaced[1]
    return Finding(
        document.path,
        document.line_of(spaced.start()),
        f'the citation "{shown(document.text[spaced.start() : end])}" spaces the dash of its range, so it'
        f" reads as a citation of R{number} alone, and links {got} where the anchor of R{number}"
        f' is "#{anchor}"',
        f'write the range with an unspaced dash, "R{before}–R{number}", as the kit writes its ranges, and'
        f" link the anchor of its first ruling, with the destination {path}#r{spaced[1]}",
    )


def record_path(document: Document, context: Context, bare: str) -> str | None:
    found = [
        p
        for p in context.tracked
        if RECORD_FILE.search(p) and (Path(p).stem == bare or Path(p).stem.startswith(bare + "-"))
    ]
    return os.path.relpath(found[0], os.path.dirname(document.path) or ".") if len(found) == 1 else None


def qualified(document: Document, start: int) -> bool:
    """The handle at start follows a word that names another kind of key: no ruling is cited."""
    word = WORD_BEFORE.search(document.masked, 0, start)
    return word is not None and word[1].lower() in QUALIFIERS


def ruling_citations(document: Document, context: Context) -> list[Finding]:
    """Rule 2 of plc-0004-decision-records: forms (a), (b) and (c) of the docstring."""
    findings: list[Finding] = []
    for match in CITED_LINK.finditer(document.masked):
        if qualified(document, match.start()):
            continue
        spaced = SPACED_BEFORE.search(document.masked, max(0, match.start() - SPACED_REACH), match.start())
        found = linked_wrongly(document, match.start(), match.end(), match[2], match[1], spaced)
        if found:
            findings.append(found)
    for match in LINK_THEN_HANDLE.finditer(document.masked):
        found = linked_wrongly(document, match.start(), match.end(), match[1], match[2])
        if found:
            findings.append(found)
    for match in CITED_BARE.finditer(document.masked):
        if qualified(document, match.start()):
            continue
        where = record_path(document, context, match[2])
        target = f"{where}#r{match[1]}" if where else f"<path to that record>#r{match[1]}"
        name = Path(where).stem if where else match[2]
        findings.append(
            Finding(
                document.path,
                document.line_of(match.start()),
                f'the citation "{shown(document.text[match.start() : match.end()])}" names the record by its'
                " id with no link",
                f"write {shown(document.text[match.start() : match.start(2)])} [{name}]({target})",
            )
        )
    return sorted(findings, key=lambda f: f.line)


def family(key: str) -> str:
    """The letters and the first number of a message key: C5.a and C5.10 are C5, C4b is C4."""
    found = FAMILY.match(key)
    return found[0] if found else key


def shared_message_keys(root: Path) -> tuple[frozenset[str], frozenset[str]]:
    """The families of the shared table (the first column of the page from anchor g3 of the shared
    messages page to its end) and the families a module's table may take, read from the code spans of the
    paragraph of anchor g3a. A document that cannot be read this way is Broken, never an empty list."""
    if not (root / SHARED_DOC).is_file():
        raise Broken(
            f"{SHARED_DOC} is missing, and a module's message table is read against it"
            " — fix: restore the file; every module document is read against its table of shared messages"
        )
    lines = read(root, SHARED_DOC).splitlines()
    marks: dict[str, int] = {}
    for name in ("g3", "g3a"):
        found = [n for n, line in enumerate(lines) if line.strip() == f'<a id="{name}"></a>']
        if not found:
            raise Broken(
                f'{SHARED_DOC} has no anchor <a id="{name}"></a> alone on a line, and the check reads'
                " the table and the paragraph by it — fix: restore the anchor, in the order g3, g3a"
            )
        if len(found) > 1:
            raise Broken(
                f'{SHARED_DOC} holds the anchor <a id="{name}"></a> {len(found)} times, and the check reads'
                " it once — fix: keep the anchor once, alone on its line, in the order g3, g3a"
            )
        marks[name] = found[0]
    if not marks["g3"] < marks["g3a"]:
        raise Broken(f"{SHARED_DOC} holds the anchors g3 and g3a out of order — fix: put them in that order")
    shared: set[str] = set()
    for line in lines[marks["g3"] + 1 :]:
        row = cells(line) if line.strip().startswith("|") and not SEPARATOR.fullmatch(line.strip()) else []
        if row and KEY_FULL.fullmatch(row[0]):
            shared.add(family(row[0]))
    if not shared:
        raise Broken(
            f"{SHARED_DOC} has no message key in the first column of its table — fix: restore the table"
        )
    paragraph: list[str] = []
    for line in lines[marks["g3a"] + 1 :]:
        if not line.strip():
            break
        paragraph.append(line)
    allowed = {family(span) for span in SPAN.findall(" ".join(paragraph)) if KEY_FULL.fullmatch(span)}
    if not allowed:
        raise Broken(
            f"{SHARED_DOC}: the paragraph after the anchor g3a names no key in a code span"
            " — fix: name the keys a module's table may take, each in a code span"
        )
    unknown = sorted(allowed - shared)
    if unknown:
        raise Broken(
            f"{SHARED_DOC}: the paragraph of g3a names {', '.join(unknown)},"
            " which the table of messages lacks — fix: name only keys of that table"
        )
    return frozenset(shared), frozenset(allowed)


def table_rows(document: Document, anchor: str) -> list[tuple[int, list[str]]]:
    """The table rows (line number, cells) of the section of a module document that opens at the
    anchor; the separator line is no row. A document without the section is Broken."""
    try:
        body = section(document.text, anchor, document.path)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    rows: list[tuple[int, list[str]]] = []
    for number, raw in body:
        line = raw.strip()
        if line.startswith("|") and not SEPARATOR.fullmatch(line):
            rows.append((number, cells(line)))
    return rows


def module_message_keys(document: Document, context: Context) -> list[Finding]:
    """A module's message table (anchor t6) takes a key of the shared table only for the module's
    part of it, the keys of the paragraph of g3a (the "message keys" rule of the docstring)."""
    if not MODULE_DOC.fullmatch(document.path):
        return []
    if "shared" not in context.cache:  # read and parsed once for the scan, not once per module
        context.cache["shared"] = shared_message_keys(context.root)
    shared, allowed = context.cache["shared"]
    findings: list[Finding] = []
    for number, row in table_rows(document, "t6"):
        for key in KEY_IN_CELL.findall(row[0] if row else ""):
            if family(key) in shared and family(key) not in allowed:
                findings.append(
                    Finding(
                        document.path,
                        number,
                        f'the module\'s message table takes the key "{key}", which the shared table'
                        f" of {SHARED_DOC} holds for a message of its own (family {family(key)})",
                        f'rename "{key}" to a key whose family (letters and first number) the shared'
                        " table does not use, e.g. the next free number of the module's own prefix, in the"
                        " module's messages.py, in its tests and in this table together",
                        KEY_WHY,
                    )
                )
    return findings


def handle_prefixes(cell: str) -> list[tuple[str, str]]:
    """The handles of one cell, each as (prefix, handle): the capital letters before a number, so that
    the cell `T1–T4, T7` gives T1, T4 and T7, and a bare number none."""
    return [(found[1], found[0]) for found in HANDLE_IN_CELL.finditer(cell)]


def prefix_kinds(document: Document) -> dict[str, dict[str, tuple[int, str]]]:
    """Where each prefix stands in a module document, by kind: prefix -> kind -> (line, handle) of its
    first use. The kinds are the message keys of the table of anchor t6, the enforcement rows of t9
    and the acceptance items of t10; the live, review and kit-check items of t10 may continue the
    fixture items' numbering under T (rule 8 of plc-0006-module-documents), so the two are one kind."""
    uses: dict[str, dict[str, tuple[int, str]]] = {}

    def note(kind: str, number: int, cell: str) -> None:
        for prefix, handle in handle_prefixes(cell):
            uses.setdefault(prefix, {}).setdefault(kind, (number, handle))

    for number, row in table_rows(document, "t6"):
        note(KIND_MESSAGE, number, row[0] if row else "")
    for number, row in table_rows(document, "t9"):
        note(KIND_ENFORCEMENT, number, row[0] if row else "")
    for number, row in table_rows(document, "t10"):
        note(KIND_ACCEPTANCE, number, row[0] if row else "")
    return uses


def module_handle_prefixes(document: Document, context: Context) -> list[Finding]:
    """Rule 8 of plc-0006-module-documents: one prefix per kind of handle in a module document (the
    "handle prefixes" rule of the docstring). The prefixes a document uses are compared, never the
    letters a policy reserves."""
    if not MODULE_DOC.fullmatch(document.path):
        return []
    findings: list[Finding] = []
    for prefix, kinds in prefix_kinds(document).items():
        if len(kinds) < 2:
            continue
        stands = sorted(kinds.items(), key=lambda item: item[1][0])
        named = [f"the {kind} ({handle}, line {at})" for kind, (at, handle) in stands]
        owners = [kind for kind in kinds if owns_prefix(kind, prefix, kinds)]
        movers = [kind for kind, _ in stands if kind not in owners and (owners or kind in FIXED_PREFIXES)]
        line = min(kinds[kind][0] for kind in movers)
        findings.append(
            Finding(
                document.path,
                line,
                f'the prefix "{prefix}" names {COUNT_WORDS[len(kinds)]} kinds of handle in this document: '
                + ", ".join(named[:-1])
                + " and "
                + named[-1],
                "; and ".join(move_fix(kind, prefix, kinds) for kind in movers),
                PREFIX_WHY,
            )
        )
    return sorted(findings, key=lambda f: f.line)


def owns_prefix(kind: str, prefix: str, kinds: Collection[str]) -> bool:
    """Whether rule 8 of plc-0006-module-documents gives the prefix to the kind, among the kinds that use
    it: the letters it fixes, save that L is the message keys' where they use it, and the live, review
    and kit-check items take V. V stays the items' even where the message keys use it too: items of L
    beside message keys of L and V move to V, and the next run moves the message keys of V."""
    if prefix == LIVE_PREFIX and KIND_MESSAGE in kinds:
        return kind == KIND_MESSAGE
    return prefix in FIXED_PREFIXES.get(kind, ())


def move_fix(kind: str, prefix: str, kinds: Collection[str]) -> str:
    """The fix for the kind that moves off a prefix: rule 8 of plc-0006-module-documents fixes the letters
    of the enforcement rows and the acceptance items, and the message keys are the module's own; the
    acceptance items that share L with the message keys take V."""
    if kind == KIND_ACCEPTANCE and prefix == LIVE_PREFIX and KIND_MESSAGE in kinds:
        return (
            f"give the live, review and kit-check items the prefix {ITEM_PREFIX_BESIDE_L}, which rule 8 of"
            " plc-0006-module-documents gives them where L is the module's message prefix, in their table"
            " and in every citation of them together"
        )
    if kind == KIND_MESSAGE:
        return (
            f"rename the message keys that begin with {prefix} to a prefix that this document uses for no"
            " other kind, in the module's messages.py, in its tests and in the table of its section 6"
            " together"
        )
    letters = FIXED_PREFIXES[kind]
    gives = (
        f"the prefix {letters[0]}, which rule 8 of plc-0006-module-documents fixes for them"
        if len(letters) == 1
        else f"one of the prefixes {', '.join(letters[:-1])} or {letters[-1]}, which rule 8 of"
        " plc-0006-module-documents fixes for them, the one that this document uses for no other kind"
    )
    return f"give the {kind} {gives}, in their table and in every citation of them together"


def record_table_keys(document: Document, context: Context) -> list[Finding]:
    """Rule 10 of plc-0004-decision-records: from the record that brought the sentence on, handles are
    unique in the record, tables included, so no table row of a record has a first cell whose first
    handle is an unqualified handle of the form of a ruling handle
    (the "table keys" rule of the docstring)."""
    numbered = RECORD_NUMBER.search(document.path)
    if numbered is None or int(numbered[1]) < UNIQUE_FROM:
        return []
    findings: list[Finding] = []
    written = document.text.split("\n")
    for number, line in enumerate(document.masked.split("\n"), start=1):
        if not line.strip().startswith("|"):  # a fenced block, the carry list, a comment: blanked
            continue
        row = written[number - 1].strip()  # the unmasked line, since a code span is a first cell too
        if SEPARATOR.fullmatch(row) or not cells(row):
            continue
        key = cells(row)[0].replace("*", "").replace("`", "")
        handle = ruling_handle(key)
        if handle:
            findings.append(
                Finding(
                    document.path,
                    number,
                    f'a table row opens with "{key}", which has the form of a ruling handle of this record',
                    'before the record\'s yes, key the rows of this table with another letter, e.g. "K" for'
                    f' "R", so that "{handle}" names a ruling alone; where the cell names a key of another'
                    ' document, write "of <that document>", by its name or a link to it, after the handle or'
                    ' after the range or list it opens, a range with an unspaced dash ("R2–R3 of the'
                    ' module"); rule 14 of plc-0004-decision-records allows this in an accepted record too',
                    TABLE_WHY,
                )
            )
    return findings


def ruling_handle(key: str) -> str | None:
    """The ruling handle a table row's first cell opens with, bold marks and backticks already taken off:
    its first handle, when that is R<n> and the cell does not write it as a key of another document,
    "R1 of the module" (a range or a list it opens qualified so, "R2–R3 of the module", too), or after
    the word "message", "key" or "row"."""
    found = CELL_HANDLE.search(key)
    if found is None or found[1] != "R":
        return None
    word = WORD_BEFORE.search(key, 0, found.start())
    run = RUN_REST.match(key, found.end())
    after = run.end() if run else found.end()
    if (word is not None and word[1].lower() in QUALIFIERS) or OF_AFTER.match(key, after):
        return None
    return found[0]


RULES: tuple[Rule, ...] = (
    ruling_citations,
    module_message_keys,
    module_handle_prefixes,
    record_table_keys,
)


def check_document(document: Document, context: Context) -> list[Finding]:
    return [finding for rule in RULES for finding in rule(document, context)]


def check_kit(root: Path) -> tuple[list[Finding], int]:
    tracked = tuple(listed_markdown(root))
    context = Context(root, tracked)
    paths = [p for p in tracked if not p.startswith(NOT_READ)]
    findings: list[Finding] = []
    for path in paths:
        text = read(root, path)
        findings.extend(check_document(Document(path, text, mask(text)), context))
    return findings, len(paths)


def report(findings: list[Finding], documents: int) -> int:
    counts = f"{documents} document(s) examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every handle is written in its form — {counts}")
    return EXIT_GREEN


RECORD_PATH = "docs/decisions/dec-0016-sample-ruling.md"
NOTE_PATH = "docs/policies/p.md"
BAD_NO_ANCHOR = "See R7 of [dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md) here.\n"
GATE_PATH = "shared/MESSAGES.md"
MODULE_PATH = "modules/const-x/MODULE.md"
SHARED_LINES = (  # the shared messages page in miniature: a table, and the paragraph of g3a
    '<a id="g3"></a>\nLead.\n\n<a id="g3a"></a>\n'
    "A module takes `G1` and `C5` for its part, as `scripts/check-handle-forms.py` reads it.\n\n"
    "| key | text |\n|---|---|\n| G1 | a |\n| G1.1 | b |\n| N1.1 | c |\n| N1.2 | d |\n"
    "| C4b | e |\n| C5.1 | f |\n| H2 | g |\n"
)
BARE_ITEM = "| 1 | fixture | none | a |\n"  # the items table's default row
RULINGS = "## Rulings\n\n1. **R1.** A rule.\n\n| key | what |\n|---|---|\n"  # the first row is line 7


@dataclass
class Tally:
    """The cases the self-test has judged, and those that failed."""

    judged: int = 0
    failed: int = 0

    def judge(self, ok: bool, text: str) -> None:
        """Count one case and print its line."""
        self.judged += 1
        self.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")


def miniature_doc(
    rows: str = "| X1 | a |\n",
    after: str = "",
    enforcement: str = "| E1 | a |\n",
    items: str = "| 1 | fixture | none | a |\n",
) -> str:
    """The sections the rules read, in miniature. With one row in each of the first two tables and
    nothing after t7, the message rows start at line 6, the enforcement rows at 17 and the items
    at 24."""
    return (
        '<a id="t6"></a>\n## 6. Artifacts\n\n| key | text |\n|---|---|\n'
        + rows
        + '\n<a id="t7"></a>\n## 7. Next\n\n'
        + after
        + '\n<a id="t9"></a>\n## 9. Enforcement\n\n| # | artifact | kind |\n|---|---|---|\n'
        + enforcement
        + '\n<a id="t10"></a>\n## 10. Acceptance\n\n| item | kind | rows | what |\n|---|---|---|---|\n'
        + items
        + '\n<a id="t11"></a>\n## 11. Siblings\n'
    )


def record_at(number: int) -> str:
    """The path of the decision record of this number in a throwaway repository."""
    return f"docs/decisions/dec-{number:04d}-t.md"


def fresh_repo(root: Path) -> None:
    """A git repository at root holding a record and the policy of decision records."""
    try:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    except OSError as missing:
        raise Broken(
            f"git cannot start ({missing.strerror}) — fix: install git, then run the self-test"
        ) from missing
    except subprocess.CalledProcessError as failed:
        said = (failed.stderr.decode(errors="replace").splitlines() or ["no message"])[0]
        raise Broken(
            f"git init failed in {root}: {said} — fix: repair what git names, then run the self-test"
        ) from failed
    write_file(root, RECORD_PATH, "A record.\n")
    write_file(root, "docs/policies/plc-0004-decision-records.md", "A policy.\n")


def write_file(root: Path, path: str, text: str) -> None:
    """Write text to path under root, making its folders."""
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def cases_forms(tally: Tally) -> None:
    """A ruling citation is red where the check reads, and green where the place is not read."""
    red: dict[str, tuple[str, str, str, tuple[int, ...]]] = {  # case: path, green, red, lines by hand
        "a ruling of a record linked with no anchor": (
            NOTE_PATH,
            "See R7 of [dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md#r7) here.\n",
            BAD_NO_ANCHOR,
            (1,),
        ),
        "a ruling linked to another ruling's anchor": (
            NOTE_PATH,
            "See R7 of [dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md#r7) here.\n",
            "See R7 of [dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md#r8) here.\n",
            (1,),
        ),
        "a ruling called an item, with no anchor": (
            NOTE_PATH,
            "The deferred item R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) holds.\n",
            "The deferred item R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md) holds.\n",
            (1,),
        ),
        "a range with a hyphen linking its last ruling": (
            NOTE_PATH,
            "R1-R4 of [dec-0018-sample-range](dec-0018-sample-range.md#r1) holds.\n",
            "R1-R4 of [dec-0018-sample-range](dec-0018-sample-range.md#r4) holds.\n",
            (1,),
        ),
        "a range with a spaced dash, read as its last ruling": (
            NOTE_PATH,
            "R2–R3 of [dec-0018-sample-range](dec-0018-sample-range.md#r2) holds.\n",
            "R2 – R3 of [dec-0018-sample-range](dec-0018-sample-range.md#r2) holds.\n",
            (1,),
        ),
        "a range linking its last ruling": (
            NOTE_PATH,
            "R18 to R27 of [dec-0018-sample-range](dec-0018-sample-range.md#r18) holds.\n",
            "R18 to R27 of [dec-0018-sample-range](dec-0018-sample-range.md#r27) holds.\n",
            (1,),
        ),
        "a list with 'and' linking its second ruling": (
            NOTE_PATH,
            "R5 and R34 of [dec-0020-sample-list](dec-0020-sample-list.md#r5) hold.\n",
            "R5 and R34 of [dec-0020-sample-list](dec-0020-sample-list.md#r34) hold.\n",
            (1,),
        ),
        "a list with a comma and 'or' linking no anchor": (
            NOTE_PATH,
            "R5, R6 or R7 of [dec-0020-sample-list](dec-0020-sample-list.md#r5) hold.\n",
            "R5, R6 or R7 of [dec-0020-sample-list](dec-0020-sample-list.md) hold.\n",
            (1,),
        ),
        "a list with an en dash linking a wrong anchor": (
            NOTE_PATH,
            "R5–R7 of [dec-0020-sample-list](dec-0020-sample-list.md#r5) hold.\n",
            "R5–R7 of [dec-0020-sample-list](dec-0020-sample-list.md#r7) hold.\n",
            (1,),
        ),
        "a citation wrapped over two lines": (
            NOTE_PATH,
            "Text R7 of\n[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) here.\n",
            "Text R7 of\n[dec-0016-sample-ruling](dec-0016-sample-ruling.md) here.\n",
            (1,),
        ),
        "a citation in a list item's continuation line": (
            NOTE_PATH,
            "- a note\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "- a note\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md)\n",
            (2,),
        ),
        "a citation on an indented line that continues a paragraph": (
            NOTE_PATH,
            "Text.\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "Text.\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md)\n",
            (2,),
        ),
        "a citation in a list item's paragraph after a blank line, indented four spaces": (
            NOTE_PATH,
            "- item\n\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "- item\n\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md)\n",
            (3,),
        ),
        "a record linked, then its handle, with no anchor": (
            NOTE_PATH,
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) R7 holds.\n",
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md) R7 holds.\n",
            (1,),
        ),
        "a record linked, then its handle, with another anchor": (
            NOTE_PATH,
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) R7 holds.\n",
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r6) R7 holds.\n",
            (1,),
        ),
        "a record's 's handle with another anchor": (
            NOTE_PATH,
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r24)'s R24 holds.\n",
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r4)'s R24 holds.\n",
            (1,),
        ),
        "a ruling of a record named by its bare id": (
            NOTE_PATH,
            "See R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) here.\n",
            "See R7 of dec-0016-sample-ruling here.\n",
            (1,),
        ),
        "a ruling of a record named by a short bare id": (
            NOTE_PATH,
            "See R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) here.\n",
            "See R7 of dec-0016 here.\n",
            (1,),
        ),
        "two findings on two lines, one correct between them": (
            NOTE_PATH,
            "R1 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r1)\n"
            "R2 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r2)\n"
            "R3 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r3)\n",
            "R1 of dec-0016-sample-ruling\n"
            "R2 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r2)\n"
            "R3 of dec-0016-sample-ruling\n",
            (1, 3),
        ),
        "a citation after the section Carry list ends": (
            "docs/decisions/dec-0005-sample-path.md",
            "## Carry list\n\nR7 of dec-0016-sample-ruling\n\n## After\n\n"
            "R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "## Carry list\n\nR7 of dec-0016-sample-ruling\n\n## After\n\nR7 of dec-0016-sample-ruling\n",
            (7,),
        ),
        "a citation after a fenced block closes": (
            NOTE_PATH,
            "```\nR7 of dec-0016-sample-ruling\n```\n"
            "R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "```\nR7 of dec-0016-sample-ruling\n```\nR7 of dec-0016-sample-ruling\n",
            (4,),
        ),
        "a citation after a code span on the same line": (
            NOTE_PATH,
            "`R1 of dec-0016-sample-ruling` and "
            "R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "`R1 of dec-0016-sample-ruling` and R7 of dec-0016-sample-ruling\n",
            (1,),
        ),
        "a citation after a comment closes": (
            NOTE_PATH,
            "<!-- R7 of dec-0016-sample-ruling -->\n"
            "R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
            "<!-- R7 of dec-0016-sample-ruling -->\nR7 of dec-0016-sample-ruling\n",
            (2,),
        ),
    }
    wrong = (
        "R7 of dec-0016-sample-ruling and R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r8) R7.\n"
    )
    green: dict[str, tuple[str, str]] = {  # case: path, text with the wrong spelling not read
        "a research comparison": ("docs/research/r.md", wrong),
        "the section Carry list": (
            "docs/decisions/dec-0005-sample-path.md",
            "## Carry list\n\n1. " + wrong,
        ),
        "a section Carry list of a deeper heading, up to the end": (
            "docs/decisions/dec-0005-sample-path.md",
            "## Rulings\n\n### Carry list\n\n" + wrong + "\n#### Inside\n\n" + wrong,
        ),
        "a fenced block": (NOTE_PATH, "```\n" + wrong + "```\n"),
        "a tilde fence": (NOTE_PATH, "~~~\n" + wrong + "~~~\n"),
        "an indented code block": (NOTE_PATH, "Text.\n\n    " + wrong),
        "a code span": (
            NOTE_PATH,
            "Write `R7 of dec-0016-sample-ruling`, never `[a](dec-0016-sample-ruling.md) R7`.\n",
        ),
        "a double-backtick code span": (NOTE_PATH, "Write `` R7 of dec-0016-sample-ruling ``.\n"),
        "an HTML comment": (NOTE_PATH, "<!-- " + wrong + "-->\n"),
        "an HTML comment over several lines": (NOTE_PATH, "<!--\n" + wrong + "-->\n"),
        "a handle with a suffix letter": (
            NOTE_PATH,
            "R4b of dec-0016-sample-ruling and R4b of [a](dec-0016-sample-ruling.md).\n",
        ),
        "a record's own ruling": (NOTE_PATH, "R3 holds, R3 of this record too, and that record's R3.\n"),
        "a key qualified by its kind": (
            NOTE_PATH,
            "The table keys R1 to R4 of [a](dec-0016-sample-ruling.md) and message\n"
            "R4 of dec-0016-sample-ruling.\n",
        ),
        "a link to what is no record": (
            NOTE_PATH,
            "R3 of [plc-0004](plc-0004-decision-records.md#r2)"
            " and [plc-0004](plc-0004-decision-records.md) R3.\n",
        ),
        "a link to a record with the right anchor, then 'R7'": (
            NOTE_PATH,
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7) R7 and"
            " [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)'s R7.\n",
        ),
        "a link at a line's end, a handle at the next line's start": (
            NOTE_PATH,
            "[dec-0016-sample-ruling](dec-0016-sample-ruling.md)\nR7 holds, see below.\n",
        ),
        "a range linking its first ruling": (
            NOTE_PATH,
            "R18 to R27 of [dec-0018-sample-range](dec-0018-sample-range.md#r18), R5 and R34 of"
            " [dec-0020-sample-list](dec-0020-sample-list.md#r5).\n",
        ),
        "a handle with no 'of' after it": (NOTE_PATH, "R3 and the record dec-0016-sample-ruling, R7.\n"),
        "a link with a title": (
            NOTE_PATH,
            'R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7 "t") holds.\n',
        ),
        "a link whose destination stands in <>": (
            NOTE_PATH,
            "R7 of [dec-0016-sample-ruling](<dec-0016-sample-ruling.md#r7>).\n",
        ),
        "a citation in a list item, indented four spaces": (
            NOTE_PATH,
            "- item\n\n    R7 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r7)\n",
        ),
    }
    for name, (path, good, bad, lines) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, path, good)
            green_before = not check_kit(root)[0]
            write_file(root, path, bad)
            findings = check_kit(root)[0]
        red_after = tuple(f.line for f in findings) == lines and all(f.path == path for f in findings)
        tally.judge(green_before and red_after, f"the correct form is green, {name} is red")
    for name, (path, text) in green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, path, text)
            tally.judge(not check_kit(root)[0], f"the wrong form in {name} is not read")


def cases_reports(tally: Tally) -> None:
    """The report of one finding of each form of citation is its literal text, exit 2."""
    why_line = (  # typed by hand: a message function cannot check itself
        "  why: a link to the ruling's own anchor takes a reader to the ruling in one click, and a"
        " record moved by the mover is repaired in every link (rule 2 of plc-0004-decision-records)"
    )
    reports: dict[str, tuple[str, str, list[str]]] = {  # case: path, text, literal lines by hand
        "no anchor": (
            "docs/policies/c.md",
            BAD_NO_ANCHOR,
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "R7 of [dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md)"'
                ' links no anchor where the anchor of R7 is "#r7"',
                why_line,
                "  fix: link the anchor of the first ruling named, with the destination"
                " ../decisions/dec-0016-sample-ruling.md#r7",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "the last ruling of a range": (
            "docs/policies/c.md",
            "R5 and R34 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r34).\n",
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "R5 and R34 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r34)"'
                ' links "#r34" where the anchor of R5 is "#r5"',
                why_line,
                "  fix: link the anchor of the first ruling named, with the destination"
                " dec-0016-sample-ruling.md#r5",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "a range with a spaced dash": (
            "docs/policies/c.md",
            "R2 – R3 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r2).\n",
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "R2 – R3 of [dec-0016-sample-ruling](dec-0016-sample-ruling.md#r2)"'
                ' spaces the dash of its range, so it reads as a citation of R3 alone, and links "#r2"'
                ' where the anchor of R3 is "#r3"',
                why_line,
                '  fix: write the range with an unspaced dash, "R2–R3", as the kit writes its ranges, and'
                " link the anchor of its first ruling, with the destination dec-0016-sample-ruling.md#r2",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "a handle after the link": (
            "docs/policies/c.md",
            "[dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md#r6)'s R7 holds.\n",
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "[dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md#r6)\'s R7"'
                ' links "#r6" where the anchor of R7 is "#r7"',
                why_line,
                "  fix: link the anchor of the first ruling named, with the destination"
                " ../decisions/dec-0016-sample-ruling.md#r7",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "a bare id of a record in the tree": (
            "docs/policies/c.md",
            "See R7 and R8 of dec-0016 here.\n",
            [
                'RED: docs/policies/c.md:1: the citation "R7 and R8 of dec-0016" names the record by its id'
                " with no link",
                why_line,
                "  fix: write R7 and R8 of"
                " [dec-0016-sample-ruling](../decisions/dec-0016-sample-ruling.md#r7)",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "a bare id of a record not in the tree": (
            "docs/policies/c.md",
            "See R9 of dec-0004-sample-bare here.\n",
            [
                'RED: docs/policies/c.md:1: the citation "R9 of dec-0004-sample-bare"'
                " names the record by its id with no link",
                why_line,
                "  fix: write R9 of [dec-0004-sample-bare](<path to that record>#r9)",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
    }
    for name, (path, text, expected) in reports.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, path, text)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = report(*check_kit(root))
        tally.judge(
            code == EXIT_RED and printed.getvalue().splitlines() == expected,
            f"the report of one finding, {name}, is its literal text, exit 2",
        )


def cases_keys(tally: Tally) -> None:
    """A message key of the shared table is red in a module's table, and each unreadable state is BROKEN."""
    after_paragraph = "a key named in a code span of a table row after the paragraph, N1"
    own_shared = {  # the cases that read a shared document of their own, by case name: a table row
        # right after the paragraph names N1 in a code span; the paragraph ends at its blank line,
        # so the row's span is no allowed key
        after_paragraph: SHARED_LINES.replace("| N1.2 | d |", "| N1.2 | see `N1` |"),
    }
    keys_red: dict[str, tuple[str, str, tuple[int, ...]]] = {  # case: rows green, rows red, lines by hand
        after_paragraph: ("| X1 | a |\n", "| N1 | a |\n", (6,)),
        "a key of a shared family that is not allowed, N1": ("| X1 | a |\n", "| N1 | a |\n", (6,)),
        "a key that is a shared key itself, H2": ("| X1 | a |\n", "| H2 | a |\n", (6,)),
        "a key of a shared family by its sub-key, C4b": ("| X1 | a |\n", "| C4b | a |\n", (6,)),
        "a bold key, N1": ("| **X1** | a |\n", "| **N1** | a |\n", (6,)),
        "a key in a code span, N1": ("| `X1` | a |\n", "| `N1` | a |\n", (6,)),
        "one key of a joined cell, N1": ("| C5, X1 | a |\n", "| C5, N1 | a |\n", (6,)),
        "a second row, H2": ("| X1 | a |\n| X2 | a |\n", "| X1 | a |\n| H2 | a |\n", (7,)),
        "two rows between a correct one": (
            "| X1 | a |\n| C5.a | a |\n| X2 | a |\n",
            "| N1 | a |\n| C5.a | a |\n| H2 | a |\n",
            (6, 8),
        ),
    }
    keys_green: dict[str, tuple[str, str]] = {  # case: rows, text after the next anchor
        "a sub-key of an allowed key, C5.a": ("| C5.a | a |\n", ""),
        "a sub-key with a number, G1.3": ("| G1.3 | a |\n", ""),
        "an allowed key itself, G1": ("| G1 | a |\n| C5 | a |\n", ""),
        "a prefix the shared table does not use, X1": ("| X1 | a |\n", ""),
        "a prefix of the shared table with another number, N2": ("| N2 | a |\n| H6 | a |\n", ""),
        "the artifacts table's rows": (
            "| hook | `hooks/hooks.json` | a |\n| script (py) | `x.py` | a |\n",
            "",
        ),
        "a shared key in a section after the table": ("| X1 | a |\n", "| N1 | a |\n"),
        "a shared key in a later cell": ("| X1 | N1 and H2 |\n", ""),
    }
    keys_broken: dict[str, tuple[str | None, str, str]] = {  # case: shared text, rows, start
        "the shared document missing": (
            None,
            "| X1 | a |\n",
            "BROKEN: shared/MESSAGES.md is missing, and a module's message table is read against it",
        ),
        "the paragraph of g3a missing": (
            SHARED_LINES.replace('<a id="g3a"></a>\n', ""),
            "| X1 | a |\n",
            'BROKEN: shared/MESSAGES.md has no anchor <a id="g3a"></a> alone on a line',
        ),
        "the paragraph of g3a naming no key": (
            SHARED_LINES.replace("`G1` and `C5`", "none"),
            "| X1 | a |\n",
            "BROKEN: shared/MESSAGES.md: the paragraph after the anchor g3a names no key in a code span",
        ),
        "the paragraph of g3a naming a key the table lacks": (
            SHARED_LINES.replace("`C5`", "`Q9`"),
            "| X1 | a |\n",
            "BROKEN: shared/MESSAGES.md: the paragraph of g3a names Q9, which the table of messages lacks",
        ),
        "the anchor g3a twice": (
            SHARED_LINES + '<a id="g3a"></a>\n',
            "| X1 | a |\n",
            'BROKEN: shared/MESSAGES.md holds the anchor <a id="g3a"></a> 2 times',
        ),
        "the anchors out of order": (
            '<a id="g3a"></a>\nA module takes `G1`.\n\n<a id="g3"></a>\n| key | text |\n|---|---|\n'
            "| G1 | a |\n",
            "| X1 | a |\n",
            "BROKEN: shared/MESSAGES.md holds the anchors g3 and g3a out of order",
        ),
        "the table with no key in its first column": (
            '<a id="g3"></a>\nLead.\n\n<a id="g3a"></a>\nA module takes `G1`.\n\n| key | text |\n|---|---|\n'
            "| first | a |\n",
            "| X1 | a |\n",
            "BROKEN: shared/MESSAGES.md has no message key in the first column of its table",
        ),
        "a module document without its anchor t6": (
            SHARED_LINES,
            "",
            'BROKEN: modules/const-x/MODULE.md has no anchor <a id="t6"></a>',
        ),
    }
    for name, (good_rows, bad_rows, lines) in keys_red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, GATE_PATH, own_shared.get(name, SHARED_LINES))
            write_file(root, MODULE_PATH, miniature_doc(good_rows))
            green_before = not check_kit(root)[0]
            write_file(root, MODULE_PATH, miniature_doc(bad_rows))
            findings = check_kit(root)[0]
        red_after = tuple(f.line for f in findings) == lines and all(f.path == MODULE_PATH for f in findings)
        tally.judge(green_before and red_after, f"the correct key is green, {name} is red")
    for name, (rows, after) in keys_green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, GATE_PATH, SHARED_LINES)
            write_file(root, MODULE_PATH, miniature_doc(rows, after))
            tally.judge(not check_kit(root)[0], f"{name} is not a finding")
    for name, (gate_text, rows, start) in keys_broken.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            if gate_text is not None:
                write_file(root, GATE_PATH, gate_text)
            write_file(root, MODULE_PATH, miniature_doc(rows) if rows else "A document with no sections.\n")
            try:
                check_kit(root)
                said = "no BROKEN: the check passed"
            except Broken as broken:
                said = f"BROKEN: {broken}"
        tally.judge(
            said.startswith(start) and " — fix: " in said, f"{name} is a teaching BROKEN line, never a pass"
        )


def cases_prefixes(tally: Tally) -> None:
    """A prefix of two kinds of handle in a module document is red, with the kind that moves named."""
    kinds_red: dict[str, tuple[dict[str, str], dict[str, str], tuple[int, ...]]] = {
        # case: the arguments of module_doc green, red, and the lines by hand
        "a message key L1 and a live item L1": (
            {"rows": "| L1 | a |\n", "items": BARE_ITEM + "| V1 | live | none | a |\n"},
            {"rows": "| L1 | a |\n", "items": BARE_ITEM + "| L1 | live | none | a |\n"},
            (25,),
        ),
        "a message key E1 and an enforcement row E1": (
            {"rows": "| X1 | a |\n"},
            {"rows": "| E1 | a |\n"},
            (6,),
        ),
        "a message key T1 and a fixture item T1": (
            {"rows": "| X1 | a |\n", "items": "| T1 | fixture | none | a |\n"},
            {"rows": "| T1 | a |\n", "items": "| T1 | fixture | none | a |\n"},
            (6,),
        ),
        "a bold message key V2 and a live range V1–V3": (
            {"rows": "| **X2** | a |\n", "items": "| V1–V3 | live | none | a |\n"},
            {"rows": "| **V2** | a |\n", "items": "| V1–V3 | live | none | a |\n"},
            (6,),
        ),
        "an acceptance item E1 and an enforcement row E1": (
            {"items": "| T1 | fixture | none | a |\n"},
            {"items": "| E1 | fixture | none | a |\n"},
            (24,),
        ),
        "an enforcement row X1 and a message key X1": (
            {"rows": "| X1 | a |\n"},
            {"rows": "| X1 | a |\n", "enforcement": "| X1 | a |\n"},
            (17,),
        ),
        "an enforcement row X5 and an item X5, neither of E, T, S, L or V": (
            {"items": "| T1 | fixture | none | a |\n"},
            {"enforcement": "| X5 | a |\n", "items": "| X5 | fixture | none | a |\n"},
            (17,),
        ),
        "a message key E1, an enforcement row E1 and an item E1": (
            {"rows": "| X1 | a |\n", "items": "| T1 | fixture | none | a |\n"},
            {"rows": "| E1 | a |\n", "items": "| E1 | fixture | none | a |\n"},
            (6,),
        ),
        "a sub-key C5.a and an item C1": (
            {"rows": "| C5.a | a |\n", "items": "| T1 | fixture | none | a |\n"},
            {"rows": "| C5.a | a |\n", "items": "| C1 | review | none | a |\n"},
            (24,),
        ),
        "an enforcement row S1 and an item S101": (
            {
                "rows": "| X1 | a |\n",
                "enforcement": "| E1 | a |\n",
                "items": "| S101 | fixture | none | a |\n",
            },
            {
                "rows": "| X1 | a |\n",
                "enforcement": "| S1 | a |\n",
                "items": "| S101 | fixture | none | a |\n",
            },
            (17,),
        ),
    }
    kinds_green: dict[str, dict[str, str]] = {  # case: the arguments of module_doc
        "message keys T1 to T4 and bare item numbers": {
            "rows": "| T1 | a |\n| T4 | a |\n",
            "items": "| 1–3 | fixture | none | a |\n| 101–106, 111 | fixture | none | a |\n",
        },
        "the shared keys beside the items T, S, L and V": {
            "rows": "| G1 | a |\n| F9 | a |\n| C5, C12 | a |\n| N2 | a |\n",
            "items": "| T1–T4 | fixture | none | a |\n| S101–S106 | fixture | none | a |\n"
            "| L1 | live | none | a |\n| V1 | review | none | a |\n",
        },
        "one prefix for the fixture items and the live items": {
            "items": "| T1 | fixture | none | a |\n| T50 | kit check | none | a |\n"
            "| T51 | live | none | a |\n",
        },
        "message keys L1 and L2 and the items T1": {
            "rows": "| L1 | a |\n| L2 | a |\n",
            "items": "| T1 | fixture | none | a |\n",
        },
        "a handle in a later cell, not the first": {
            "rows": "| X1 | L1 and E1 |\n",
            "items": "| T1 | fixture | L1 | E1 |\n",
        },
        "a handle after the table of its section": {"after": "| L1 | a |\n| E1 | a |\n"},
        "a path in the first cell of an item, hooks/L1.json": {
            "rows": "| L1 | a |\n",
            "items": "| `hooks/L1.json` | fixture | none | a |\n",
        },
        "bold handles of two kinds, L1 and T1": {
            "rows": "| **L1** | a |\n",
            "items": "| **T1–T4** | fixture | none | a |\n",
        },
    }
    prefix_pairs: dict[str, tuple[dict[str, str], tuple[str, str, str]]] = {
        # case: the arguments of module_doc, and the lines by hand of the report with one finding: the
        # finding's first line, its fix line and the last line; the pair decides which kind moves
        "a message key against an enforcement row: the message key moves": (
            {"rows": "| E1 | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:6: the prefix "E" names two kinds of handle in this document:'
                " the message keys (E1, line 6) and the enforcement rows (E1, line 17)",
                "  fix: rename the message keys that begin with E to a prefix that this document uses for no"
                " other kind, in the module's messages.py, in its tests and in the table of its section 6"
                " together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "an enforcement row against an item of S: the enforcement row moves": (
            {"enforcement": "| S1 | a |\n", "items": "| S101 | fixture | none | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:17: the prefix "S" names two kinds of handle in this'
                " document: the enforcement rows (S1, line 17) and the acceptance items (S101, line 24)",
                "  fix: give the enforcement rows the prefix E, which rule 8 of plc-0006-module-documents"
                " fixes for them, in their table and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "an enforcement row against an item of E: the item moves": (
            {"items": "| E1 | fixture | none | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:24: the prefix "E" names two kinds of handle in this'
                " document: the enforcement rows (E1, line 17) and the acceptance items (E1, line 24)",
                "  fix: give the acceptance items one of the prefixes T, S, L or V, which rule 8 of"
                " plc-0006-module-documents fixes for them, the one that this document uses for no other"
                " kind, in their table and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "a message key against an item of C, no kind owning it: the item moves": (
            {"rows": "| C5.a | a |\n", "items": "| C1 | review | none | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:24: the prefix "C" names two kinds of handle in this'
                " document: the message keys (C5, line 6) and the acceptance items (C1, line 24)",
                "  fix: give the acceptance items one of the prefixes T, S, L or V, which rule 8 of"
                " plc-0006-module-documents fixes for them, the one that this document uses for no other"
                " kind, in their table and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "a message key against an enforcement row of X, no kind owning it: the enforcement row moves": (
            {"enforcement": "| X1 | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:17: the prefix "X" names two kinds of handle in this'
                " document: the message keys (X1, line 6) and the enforcement rows (X1, line 17)",
                "  fix: give the enforcement rows the prefix E, which rule 8 of plc-0006-module-documents"
                " fixes for them, in their table and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "an enforcement row against an item, both of X: both move": (
            {"enforcement": "| X5 | a |\n", "items": "| X5 | fixture | none | a |\n", "rows": "| Y1 | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:17: the prefix "X" names two kinds of handle in this'
                " document: the enforcement rows (X5, line 17) and the acceptance items (X5, line 24)",
                "  fix: give the enforcement rows the prefix E, which rule 8 of plc-0006-module-documents"
                " fixes for them, in their table and in every citation of them together; and give the"
                " acceptance items one of the prefixes T, S, L or V, which rule 8 of"
                " plc-0006-module-documents fixes for them, the one that this document uses for no other"
                " kind, in their table and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "a message key, an enforcement row and an item, all of E: the key and the item move": (
            {"rows": "| E1 | a |\n", "items": "| E1 | fixture | none | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:6: the prefix "E" names three kinds of handle in this'
                " document: the message keys (E1, line 6), the enforcement rows (E1, line 17) and the"
                " acceptance items (E1, line 24)",
                "  fix: rename the message keys that begin with E to a prefix that this document uses for no"
                " other kind, in the module's messages.py, in its tests and in the table of its section 6"
                " together; and give the acceptance items one of the prefixes T, S, L or V, which rule 8 of"
                " plc-0006-module-documents fixes for them, the one that this document uses for no other"
                " kind, in their table and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "a message key and a live item, both of L: the live item moves": (
            {"rows": "| L1 | a |\n", "items": "| L1 | live | none | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:24: the prefix "L" names two kinds of handle in this'
                " document: the message keys (L1, line 6) and the acceptance items (L1, line 24)",
                "  fix: give the live, review and kit-check items the prefix V, which rule 8 of"
                " plc-0006-module-documents gives them where L is the module's message prefix, in their table"
                " and in every citation of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
        "a message key, an enforcement row and an item, all of L: the enforcement row and the item move": (
            {"rows": "| L1 | a |\n", "enforcement": "| L1 | a |\n", "items": "| L1 | live | none | a |\n"},
            (
                'RED: modules/const-x/MODULE.md:17: the prefix "L" names three kinds of handle in this'
                " document: the message keys (L1, line 6), the enforcement rows (L1, line 17) and the"
                " acceptance items (L1, line 24)",
                "  fix: give the enforcement rows the prefix E, which rule 8 of plc-0006-module-documents"
                " fixes for them, in their table and in every citation of them together; and give the"
                " live, review and kit-check items the prefix V, which rule 8 of plc-0006-module-documents"
                " gives them where L is the module's message prefix, in their table and in every citation"
                " of them together",
                "RED: 1 finding(s) — 4 document(s) examined",
            ),
        ),
    }
    for name, (good_args, bad_args, lines) in kinds_red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, GATE_PATH, SHARED_LINES)
            write_file(root, MODULE_PATH, miniature_doc(**good_args))
            green_before = not check_kit(root)[0]
            write_file(root, MODULE_PATH, miniature_doc(**bad_args))
            findings = check_kit(root)[0]
        red_after = tuple(f.line for f in findings) == lines and all(f.path == MODULE_PATH for f in findings)
        tally.judge(green_before and red_after, f"the correct prefixes are green, {name} is red")
    for name, args in kinds_green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, GATE_PATH, SHARED_LINES)
            write_file(root, MODULE_PATH, miniature_doc(**args))
            tally.judge(not check_kit(root)[0], f"{name} is not a finding")
    for name, (args, expected_lines) in prefix_pairs.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, GATE_PATH, SHARED_LINES)
            write_file(root, MODULE_PATH, miniature_doc(**args))
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = report(*check_kit(root))
        got = printed.getvalue().splitlines()
        tally.judge(
            code == EXIT_RED
            and len(got) == len(expected_lines) + 1
            and (got[0], got[2], got[3]) == expected_lines,
            f"the report of a prefix of several kinds, {name}, has its literal first and fix lines, exit 2",
        )


def cases_sections(tally: Tally) -> None:
    """A module document without an anchor the rules read is a teaching BROKEN line."""
    sections_broken: dict[str, tuple[str, str]] = {  # case: module document, start of the BROKEN line
        "a module document without its anchor t9": (
            miniature_doc().replace('<a id="t9"></a>\n', ""),
            'BROKEN: modules/const-x/MODULE.md has no anchor <a id="t9"></a>',
        ),
        "a module document without its anchor t10": (
            miniature_doc().replace('<a id="t10"></a>\n', ""),
            'BROKEN: modules/const-x/MODULE.md has no anchor <a id="t10"></a>',
        ),
    }
    for name, (text, start) in sections_broken.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, GATE_PATH, SHARED_LINES)
            write_file(root, MODULE_PATH, text)
            try:
                check_kit(root)
                said = "no BROKEN: the check passed"
            except Broken as broken:
                said = f"BROKEN: {broken}"
        tally.judge(
            said.startswith(start) and " — fix: " in said, f"{name} is a teaching BROKEN line, never a pass"
        )


def cases_tables(tally: Tally) -> None:
    """A table row keyed as a ruling of its record is red, and what is not read is green."""
    after_carry = (
        "## Carry list\n\n| R1 | x |\n\n## After\n\n| key | what |\n|---|---|\n"  # the first row is 9
    )
    tables_red: dict[str, tuple[int, str, str, tuple[int, ...]]] = {
        # case: the record's number, the text green, the text red, the lines by hand
        "a row R1 in a record numbered 39": (39, RULINGS + "| K1 | a |\n", RULINGS + "| R1 | a |\n", (7,)),
        "a row R1 in a record numbered 100": (100, RULINGS + "| K1 | a |\n", RULINGS + "| R1 | a |\n", (7,)),
        "a bold row key R1": (40, RULINGS + "| **K1** | a |\n", RULINGS + "| **R1** | a |\n", (7,)),
        "a bold row key with a full stop, R2.": (
            40,
            RULINGS + "| K2. | a |\n",
            RULINGS + "| **R2.** | a |\n",
            (7,),
        ),
        "a row key with a full stop, R3.": (40, RULINGS + "| K3. | a |\n", RULINGS + "| R3. | a |\n", (7,)),
        "a second row R2 beside a correct one": (
            41,
            RULINGS + "| K1 | a |\n| K2 | b |\n",
            RULINGS + "| K1 | a |\n| R2 | b |\n",
            (8,),
        ),
        "a row key R1 in a code span": (40, RULINGS + "| K1 | a |\n", RULINGS + "| `R1` | a |\n", (7,)),
        "a row key R1 in a bold code span": (
            40,
            RULINGS + "| K1 | a |\n",
            RULINGS + "| **`R1`** | a |\n",
            (7,),
        ),
        "a row key range R2–R3 with an en dash": (
            40,
            RULINGS + "| K2–K3 | a |\n",
            RULINGS + "| R2–R3 | a |\n",
            (7,),
        ),
        "a row key range R2-R3 with a hyphen": (
            40,
            RULINGS + "| K2-K3 | a |\n",
            RULINGS + "| R2-R3 | a |\n",
            (7,),
        ),
        "a row key range in a code span, R2–R3": (
            40,
            RULINGS + "| K2–K3 | a |\n",
            RULINGS + "| `R2–R3` | a |\n",
            (7,),
        ),
        "a row key list R4, R5": (40, RULINGS + "| K4, K5 | a |\n", RULINGS + "| R4, R5 | a |\n", (7,)),
        "a row key list in a code span, R4, R5": (
            40,
            RULINGS + "| K4, K5 | a |\n",
            RULINGS + "| `R4, R5` | a |\n",
            (7,),
        ),
        "a row key R7 followed by other words": (
            40,
            RULINGS + "| K7 (x) | a |\n",
            RULINGS + "| R7 (x) | a |\n",
            (7,),
        ),
        "a row key range R2–R3 whose of follows other words, not the range": (
            40,
            RULINGS + "| K2–K3 (x) of the module | a |\n",
            RULINGS + "| R2–R3 (x) of the module | a |\n",
            (7,),
        ),
        "a row key range with a spaced dash, R2 – R3 of the module": (
            40,
            RULINGS + "| R2–R3 of the module | a |\n",
            RULINGS + "| R2 – R3 of the module | a |\n",
            (7,),
        ),
        "a row key R7 after other words, not a qualifier": (
            40,
            RULINGS + "| the K7 row | a |\n",
            RULINGS + "| the R7 row | a |\n",
            (7,),
        ),
        "a row R1 in a table after the section Carry list ends": (
            42,
            after_carry + "| K1 | a |\n",
            after_carry + "| R1 | a |\n",
            (9,),
        ),
    }
    tables_green: dict[str, tuple[str, str]] = {  # case: path, text
        "a record numbered 38": (record_at(38), RULINGS + "| R1 | a |\n"),
        "a document that is no record": ("docs/policies/p.md", RULINGS + "| R1 | a |\n"),
        "the section Carry list": (record_at(39), "## Carry list\n\n| key | what |\n|---|---|\n| R1 | a |\n"),
        "a fenced block": (record_at(39), "```\n| R1 | a |\n```\n"),
        "a code span in a fenced block": (record_at(39), "```\n| `R1` | a |\n```\n"),
        "a code span in the section Carry list": (
            record_at(39),
            "## Carry list\n\n| key | what |\n|---|---|\n| `R1` | a |\n",
        ),
        "a later cell": (record_at(39), RULINGS + "| K1 | R1 |\n"),
        "a first cell whose first handle is no ruling's, K1, R1": (
            record_at(39),
            RULINGS + "| K1, R1 | a |\n",
        ),
        "a first handle of another document, R1 of the module": (
            record_at(39),
            RULINGS + "| R1 of the module | a |\n",
        ),
        "a first handle of another document, R1 of a link to it": (
            record_at(39),
            RULINGS
            + "| R1 of [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r1) | a |\n",
        ),
        "a range of another document, R2–R3 of the module": (
            record_at(39),
            RULINGS + "| R2–R3 of the module | a |\n",
        ),
        "a list of another document, R4, R5 of the module": (
            record_at(39),
            RULINGS + "| R4, R5 of the module | a |\n",
        ),
        "a first handle of another document, in a code span": (
            record_at(39),
            RULINGS + "| `R1` of the module | a |\n",
        ),
        "a handle after the word message": (record_at(39), RULINGS + "| message R1 | a |\n"),
        "a handle after the word key": (record_at(39), RULINGS + "| the key R1 | a |\n"),
        "a handle after the word row": (record_at(39), RULINGS + "| **row R1** | a |\n"),
        "a path with a handle in its name, hooks/R1.json": (
            record_at(39),
            RULINGS + "| hooks/R1.json | a |\n",
        ),
        "a file name that opens with a handle, R1.json": (record_at(39), RULINGS + "| `R1.json` | a |\n"),
        "a handle with a suffix letter, R1b": (record_at(39), RULINGS + "| R1b | a |\n"),
        "a cell with no handle": (record_at(39), RULINGS + "| the rule | a |\n"),
        "a ruling outside a table": (record_at(39), "1. **R1.** A rule.\n\nR1 stands.\n"),
    }
    for name, (number, good_text, bad_text, lines) in tables_red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, record_at(number), good_text)
            green_before = not check_kit(root)[0]
            write_file(root, record_at(number), bad_text)
            findings = check_kit(root)[0]
        red_after = tuple(f.line for f in findings) == lines and all(
            f.path == record_at(number) for f in findings
        )
        tally.judge(green_before and red_after, f"the correct row key is green, {name} is red")
    for name, (path, text) in tables_green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_repo(root)
            write_file(root, path, text)
            tally.judge(not check_kit(root)[0], f"{name} is not a finding")


def cases_literal_reports(tally: Tally) -> None:
    """The report of one finding of each module rule is its literal text, exit 2."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_repo(root)
        write_file(root, GATE_PATH, SHARED_LINES)
        write_file(
            root, MODULE_PATH, miniature_doc("| L1 | a |\n", items=BARE_ITEM + "| L1 | live | none | a |\n")
        )
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    tally.judge(
        code == EXIT_RED
        and printed.getvalue().splitlines()
        == [
            'RED: modules/const-x/MODULE.md:25: the prefix "L" names two kinds of handle in this document:'
            " the message keys (L1, line 6) and the acceptance items (L1, line 25)",
            "  why: one prefix names one kind of handle in a document, so a reader who meets L1 or T3 knows"
            " at once which table to open (rule 8 of plc-0006-module-documents)",
            "  fix: give the live, review and kit-check items the prefix V, which rule 8 of"
            " plc-0006-module-documents gives them where L is the module's message prefix, in their table"
            " and in every citation of them together",
            "RED: 1 finding(s) — 4 document(s) examined",
        ],
        "the report of one finding, a message key and a live item of L, the item moving,"
        " is its literal text, exit 2",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_repo(root)
        write_file(root, record_at(39), RULINGS + "| R1 | a |\n")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    tally.judge(
        code == EXIT_RED
        and printed.getvalue().splitlines()
        == [
            f'RED: {record_at(39)}:7: a table row opens with "R1", which has the form of a ruling handle of'
            " this record",
            "  why: a handle names one thing in a record, so a table row keyed R3 beside a ruling R3 leaves a"
            " citation of R3 with two readings (rule 10 of plc-0004-decision-records)",
            '  fix: before the record\'s yes, key the rows of this table with another letter, e.g. "K" for'
            ' "R", so that "R1" names a ruling alone; where the cell names a key of another document,'
            ' write "of <that document>", by its name or a link to it, after the handle or after the range'
            ' or list it opens, a range with an unspaced dash ("R2–R3 of the module"); rule 14 of'
            " plc-0004-decision-records allows this in an accepted record too",
            "RED: 1 finding(s) — 3 document(s) examined",
        ],
        "the report of one finding, a table row keyed as a ruling, is its literal text, exit 2",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_repo(root)
        write_file(root, record_at(39), RULINGS + "| **`R2–R3`** | a |\n")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    tally.judge(
        code == EXIT_RED
        and printed.getvalue().splitlines()
        == [
            f'RED: {record_at(39)}:7: a table row opens with "R2–R3", which has the form of a ruling handle'
            " of this record",
            "  why: a handle names one thing in a record, so a table row keyed R3 beside a ruling R3 leaves a"
            " citation of R3 with two readings (rule 10 of plc-0004-decision-records)",
            '  fix: before the record\'s yes, key the rows of this table with another letter, e.g. "K" for'
            ' "R", so that "R2" names a ruling alone; where the cell names a key of another document,'
            ' write "of <that document>", by its name or a link to it, after the handle or after the range'
            ' or list it opens, a range with an unspaced dash ("R2–R3 of the module"); rule 14 of'
            " plc-0004-decision-records allows this in an accepted record too",
            "RED: 1 finding(s) — 3 document(s) examined",
        ],
        "the report of one finding, a bold range in a code span, quotes the key without its marks, exit 2",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_repo(root)
        write_file(root, GATE_PATH, SHARED_LINES)
        write_file(root, MODULE_PATH, miniature_doc("| N1 | a |\n"))
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    tally.judge(
        code == EXIT_RED
        and printed.getvalue().splitlines()
        == [
            'RED: modules/const-x/MODULE.md:6: the module\'s message table takes the key "N1", which the'
            " shared table of shared/MESSAGES.md holds for a message of its own (family N1)",
            "  why: one key names one message in every module, so a reader who meets the key in a log or a"
            " document finds the same message wherever it stands (paragraph g3a of shared/MESSAGES.md)",
            '  fix: rename "N1" to a key whose family (letters and first number) the shared table does not'
            " use, e.g. the next free number of the module's own prefix, in the module's messages.py, in"
            " its tests and in this table together",
            "RED: 1 finding(s) — 4 document(s) examined",
        ],
        "the report of one finding, a shared key in a module's table, is its literal text, exit 2",
    )


def cases_edges(tally: Tally) -> None:
    """A green tree, a file that is not UTF-8, a folder that is no repository and a misinvocation each
    give the line the check promises."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_repo(root)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
        tally.judge(
            code == EXIT_GREEN
            and printed.getvalue().splitlines()
            == ["GREEN: every handle is written in its form — 2 document(s) examined"],
            "the report of a green tree is its literal line, exit 0",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_repo(root)
        (root / "docs" / "latin1.md").write_bytes(b"caf\xe9\n")
        try:
            check_kit(root)
            ok = False
        except UnicodeDecodeError:  # the decoding escaped the check: its fix is gone
            ok = False
        except Broken as broken:
            ok = str(broken).startswith("docs/latin1.md is not UTF-8") and "fix: save it as UTF-8" in str(
                broken
            )
    tally.judge(ok, "a file that is not UTF-8 is a teaching BROKEN line, never a traceback")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            check_kit(Path(tmp).resolve())
            said = "nothing raised"
        except Broken as broken:
            said = str(broken)
    tally.judge(
        said.startswith("git ls-files failed: fatal: not a git repository")  # typed by hand: git's own words
        and said.endswith(" — fix: run the check from a checkout of the kit"),
        "a folder that is no repository is a BROKEN line quoting git's first line",
    )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(io.StringIO()):
        code = main(["--bogus"])
    tally.judge(
        code == EXIT_BROKEN
        and printed.getvalue().splitlines()
        == [
            "BROKEN: misinvocation — fix: run with no arguments, or with --self-test",
            "BROKEN: the check could not run — 0 documents examined",
        ],
        "a misinvocation is a teaching BROKEN line, exit 1",
    )


def self_test() -> int:
    """Red→green on a throwaway repository: each form is red where the check reads, with the lines
    of its findings typed by hand, and its correct spelling is green; every place not read stays
    green with the wrong spelling; the report of one finding of each kind is its literal text with
    exit 2; and a file that is not UTF-8 and a misinvocation are teaching BROKEN lines. The total
    counts every case judged, never a sum typed by hand."""
    tally = Tally()
    cases_forms(tally)
    cases_reports(tally)
    cases_keys(tally)
    cases_prefixes(tally)
    cases_sections(tally)
    cases_tables(tally)
    cases_literal_reports(tally)
    cases_edges(tally)
    print(f"{tally.judged - tally.failed}/{tally.judged} cases green")
    return EXIT_GREEN if tally.failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-handle-forms", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 documents examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check_kit(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 documents examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
