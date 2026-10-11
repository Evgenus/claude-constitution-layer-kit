#!/usr/bin/env python3
"""Kit check: the forms in which a document names a handle of another document.

One scan over the Markdown files git lists, one rule function per form; each rule returns its
findings and the scan reports them all. Two rules are read:

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
                    a decision record when its file is named `dec-<four digits>-….md`.

  message keys      a module's own message table (its MODULE.md §6, anchor t6) takes a key of the
                    shared table (shared/GATE.md §3, anchor g3) only to state the module's part of
                    that message, and only the keys named in the paragraph of anchor g3a. A key's
                    family is its letters and its first number: `C5.a` and `C5.10` are family C5,
                    `C4b` is family C4. Finding: a key of the module's table whose family is a
                    family of the shared table and not one of the paragraph's keys. The check reads
                    the shared keys from the first column of the §3 table and the allowed ones from
                    the code spans of the paragraph of g3a, so the document is the one source.

Not read: the research comparisons (docs/research/), frozen ones keep the form
they were frozen with (rule 7 of plc-0005-research); in every document it skips the "Carry list"
section of a record, whose links lead to no record, fenced code, indented code, inline code spans
and HTML comments. The message-key rule
reads only the table of anchor t6 of each modules/<name>/MODULE.md, and fails loud (BROKEN, with
the fix) where the shared document or its anchors g3, g3a and g4 cannot be read.
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
from collections.abc import Callable
from dataclasses import dataclass
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
SHARED_DOC = "shared/GATE.md"  # the shared messages: the table of anchor g3, its allowed keys at g3a
MODULE_DOC = re.compile(r"modules/[^/]+/MODULE\.md")
KEY = r"[A-Z]+\d+[A-Za-z0-9]*(?:\.[A-Za-z0-9]+)*"  # a message key: C11, C5.a, C5.10, C4b
KEY_FULL = re.compile(KEY)
KEY_IN_CELL = re.compile(rf"(?<![\w.]){KEY}")
FAMILY = re.compile(r"[A-Z]+\d+")  # the letters and the first number of a key
WHY = (
    "a link to the ruling's own anchor takes a reader to the ruling in one click, and a record moved"
    " by the mover is repaired in every link (rule 2 of plc-0004-decision-records)"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


KEY_WHY = (
    "one key names one message in every module, so a reader who meets the key in a log or a document"
    " finds the same message wherever it stands (paragraph g3a of shared/GATE.md)"
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


def linked_wrongly(document: Document, start: int, end: int, destination: str, number: str) -> Finding | None:
    path, fragment = split_fragment(destination)
    anchor = f"r{number}"
    if not RECORD_FILE.search(path) or fragment == anchor:
        return None
    got = "no anchor" if fragment is None else f'"#{fragment}"'
    return Finding(
        document.path,
        document.line_of(start),
        f'the citation "{shown(document.text[start:end])}" links {got} where the anchor of R{number}'
        f' is "#{anchor}"',
        f"link the anchor of the first ruling named, with the destination {path}#{anchor}",
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
        found = linked_wrongly(document, match.start(), match.end(), match[2], match[1])
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
    """The families of the shared table (the first column of the section of anchor g3 of the shared
    document) and the families a module's table may take, read from the code spans of the paragraph
    of anchor g3a. A document that cannot be read this way is Broken, never an empty list."""
    if not (root / SHARED_DOC).is_file():
        raise Broken(
            f"{SHARED_DOC} is missing, and a module's message table is read against it"
            " — fix: restore the file; every module document is read against its section 3"
        )
    lines = read(root, SHARED_DOC).splitlines()
    marks: dict[str, int] = {}
    for name in ("g3", "g3a", "g4"):
        found = [n for n, line in enumerate(lines) if line.strip() == f'<a id="{name}"></a>']
        if len(found) != 1:
            raise Broken(
                f'{SHARED_DOC} holds the anchor <a id="{name}"></a> {len(found)} time(s), and the check reads'
                " it once — fix: keep the anchor alone on its line, once, in the order g3, g3a, g4"
            )
        marks[name] = found[0]
    if not marks["g3"] < marks["g3a"] < marks["g4"]:
        raise Broken(
            f"{SHARED_DOC} holds the anchors g3, g3a and g4 out of order — fix: put them in that order"
        )
    shared: set[str] = set()
    for line in lines[marks["g3"] + 1 : marks["g4"]]:
        row = cells(line) if line.strip().startswith("|") and not SEPARATOR.fullmatch(line.strip()) else []
        if row and KEY_FULL.fullmatch(row[0]):
            shared.add(family(row[0]))
    if not shared:
        raise Broken(
            f"{SHARED_DOC} has no message key in the first column of its section 3 — fix: restore the table"
        )
    paragraph: list[str] = []
    for line in lines[marks["g3a"] + 1 : marks["g4"]]:
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
            " which the table of section 3 lacks — fix: name only keys of that table"
        )
    return frozenset(shared), frozenset(allowed)


def module_message_keys(document: Document, context: Context) -> list[Finding]:
    """A module's message table (anchor t6) takes a key of the shared table only for the module's
    part of it, the keys of the paragraph of g3a (the "message keys" rule of the docstring)."""
    if not MODULE_DOC.fullmatch(document.path):
        return []
    shared, allowed = shared_message_keys(context.root)
    try:
        body = section(document.text, "t6", document.path)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    findings: list[Finding] = []
    for number, raw in body:
        line = raw.strip()
        if not line.startswith("|") or SEPARATOR.fullmatch(line):
            continue
        row = cells(line)
        for key in KEY_IN_CELL.findall(row[0].replace("*", "").replace("`", "") if row else ""):
            if family(key) in shared and family(key) not in allowed:
                prefixes = ", ".join(sorted({re.sub(r"\d.*", "", f) for f in shared}))
                findings.append(
                    Finding(
                        document.path,
                        number,
                        f'the module\'s message table takes the key "{key}", which the shared table'
                        f" of {SHARED_DOC} holds for a message of its own (family {family(key)})",
                        f'rename "{key}" to a prefix that neither table uses (the shared table uses'
                        f" {prefixes}), in the module's messages.py, in its tests and in this table together",
                        KEY_WHY,
                    )
                )
    return findings


RULES: tuple[Rule, ...] = (ruling_citations, module_message_keys)


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


def self_test() -> int:
    """Red→green on a throwaway repository: each form is red where the check reads, with the lines
    of its findings typed by hand, and its correct spelling is green; every place not read stays
    green with the wrong spelling; the report of one finding of each kind is its literal text with
    exit 2; and a file that is not UTF-8 and a misinvocation are teaching BROKEN lines. The total
    counts every case judged, never a sum typed by hand."""
    record = "docs/decisions/dec-0016-yes-on-the-change.md"
    note = "docs/policies/p.md"
    bad_a = "See R7 of [dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md) here.\n"
    red: dict[str, tuple[str, str, str, tuple[int, ...]]] = {  # case: path, green, red, lines by hand
        "a ruling of a record linked with no anchor": (
            note,
            "See R7 of [dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md#r7) here.\n",
            bad_a,
            (1,),
        ),
        "a ruling linked to another ruling's anchor": (
            note,
            "See R7 of [dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md#r7) here.\n",
            "See R7 of [dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md#r8) here.\n",
            (1,),
        ),
        "a ruling called an item, with no anchor": (
            note,
            "The deferred item R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) holds.\n",
            "The deferred item R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md) holds.\n",
            (1,),
        ),
        "a range with a hyphen linking its last ruling": (
            note,
            "R1-R4 of [dec-0018-dials-schema](dec-0018-dials-schema.md#r1) holds.\n",
            "R1-R4 of [dec-0018-dials-schema](dec-0018-dials-schema.md#r4) holds.\n",
            (1,),
        ),
        "a range linking its last ruling": (
            note,
            "R18 to R27 of [dec-0018-dials-schema](dec-0018-dials-schema.md#r18) holds.\n",
            "R18 to R27 of [dec-0018-dials-schema](dec-0018-dials-schema.md#r27) holds.\n",
            (1,),
        ),
        "a list with 'and' linking its second ruling": (
            note,
            "R5 and R34 of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md#r5) hold.\n",
            "R5 and R34 of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md#r34) hold.\n",
            (1,),
        ),
        "a list with a comma and 'or' linking no anchor": (
            note,
            "R5, R6 or R7 of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md#r5) hold.\n",
            "R5, R6 or R7 of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md) hold.\n",
            (1,),
        ),
        "a list with an en dash linking a wrong anchor": (
            note,
            "R5–R7 of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md#r5) hold.\n",
            "R5–R7 of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md#r7) hold.\n",
            (1,),
        ),
        "a citation wrapped over two lines": (
            note,
            "Text R7 of\n[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) here.\n",
            "Text R7 of\n[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md) here.\n",
            (1,),
        ),
        "a citation in a list item's continuation line": (
            note,
            "- a note\n    R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)\n",
            "- a note\n    R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md)\n",
            (2,),
        ),
        "a record linked, then its handle, with no anchor": (
            note,
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) R7 holds.\n",
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md) R7 holds.\n",
            (1,),
        ),
        "a record linked, then its handle, with another anchor": (
            note,
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) R7 holds.\n",
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r6) R7 holds.\n",
            (1,),
        ),
        "a record's 's handle with another anchor": (
            note,
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r24)'s R24 holds.\n",
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r4)'s R24 holds.\n",
            (1,),
        ),
        "a ruling of a record named by its bare id": (
            note,
            "See R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) here.\n",
            "See R7 of dec-0016-yes-on-the-change here.\n",
            (1,),
        ),
        "a ruling of a record named by a short bare id": (
            note,
            "See R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) here.\n",
            "See R7 of dec-0016 here.\n",
            (1,),
        ),
        "two findings on two lines, one correct between them": (
            note,
            "R1 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r1)\n"
            "R2 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r2)\n"
            "R3 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r3)\n",
            "R1 of dec-0016-yes-on-the-change\n"
            "R2 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r2)\n"
            "R3 of dec-0016-yes-on-the-change\n",
            (1, 3),
        ),
        "a citation after the section Carry list ends": (
            "docs/decisions/dec-0005-reference-forms.md",
            "## Carry list\n\nR7 of dec-0016-yes-on-the-change\n\n## After\n\n"
            "R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)\n",
            "## Carry list\n\nR7 of dec-0016-yes-on-the-change\n\n## After\n\n"
            "R7 of dec-0016-yes-on-the-change\n",
            (7,),
        ),
        "a citation after a fenced block closes": (
            note,
            "```\nR7 of dec-0016-yes-on-the-change\n```\n"
            "R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)\n",
            "```\nR7 of dec-0016-yes-on-the-change\n```\nR7 of dec-0016-yes-on-the-change\n",
            (4,),
        ),
        "a citation after a code span on the same line": (
            note,
            "`R1 of dec-0016-yes-on-the-change` and "
            "R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)\n",
            "`R1 of dec-0016-yes-on-the-change` and R7 of dec-0016-yes-on-the-change\n",
            (1,),
        ),
        "a citation after a comment closes": (
            note,
            "<!-- R7 of dec-0016-yes-on-the-change -->\n"
            "R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)\n",
            "<!-- R7 of dec-0016-yes-on-the-change -->\nR7 of dec-0016-yes-on-the-change\n",
            (2,),
        ),
    }
    wrong = (
        "R7 of dec-0016-yes-on-the-change"
        " and R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r8) R7.\n"
    )
    green: dict[str, tuple[str, str]] = {  # case: path, text with the wrong spelling not read
        "a research comparison": ("docs/research/r.md", wrong),
        "the section Carry list": (
            "docs/decisions/dec-0005-reference-forms.md",
            "## Carry list\n\n1. " + wrong,
        ),
        "a section Carry list of a deeper heading, up to the end": (
            "docs/decisions/dec-0005-reference-forms.md",
            "## Rulings\n\n### Carry list\n\n" + wrong + "\n#### Inside\n\n" + wrong,
        ),
        "a fenced block": (note, "```\n" + wrong + "```\n"),
        "a tilde fence": (note, "~~~\n" + wrong + "~~~\n"),
        "an indented code block": (note, "Text.\n\n    " + wrong),
        "a code span": (
            note,
            "Write `R7 of dec-0016-yes-on-the-change`, never `[a](dec-0016-yes-on-the-change.md) R7`.\n",
        ),
        "a double-backtick code span": (note, "Write `` R7 of dec-0016-yes-on-the-change ``.\n"),
        "an HTML comment": (note, "<!-- " + wrong + "-->\n"),
        "an HTML comment over several lines": (note, "<!--\n" + wrong + "-->\n"),
        "a handle with a suffix letter": (
            note,
            "R4b of dec-0016-yes-on-the-change and R4b of [a](dec-0016-yes-on-the-change.md).\n",
        ),
        "a record's own ruling": (note, "R3 holds, R3 of this record too, and that record's R3.\n"),
        "a key qualified by its kind": (
            note,
            "The table keys R1 to R4 of [a](dec-0016-yes-on-the-change.md) and message\n"
            "R4 of dec-0016-yes-on-the-change.\n",
        ),
        "a link to what is no record": (
            note,
            "R3 of [plc-0004](plc-0004-decision-records.md#r2)"
            " and [plc-0004](plc-0004-decision-records.md) R3.\n",
        ),
        "a link to a record with the right anchor, then 'R7'": (
            note,
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7) R7 and"
            " [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)'s R7.\n",
        ),
        "a link at a line's end, a handle at the next line's start": (
            note,
            "[dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md)\nR7 holds, see below.\n",
        ),
        "a range linking its first ruling": (
            note,
            "R18 to R27 of [dec-0018-dials-schema](dec-0018-dials-schema.md#r18), R5 and R34 of"
            " [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md#r5).\n",
        ),
        "a handle with no 'of' after it": (note, "R3 and the record dec-0016-yes-on-the-change, R7.\n"),
        "a link with a title": (
            note,
            'R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7 "t") holds.\n',
        ),
        "a link whose destination stands in <>": (
            note,
            "R7 of [dec-0016-yes-on-the-change](<dec-0016-yes-on-the-change.md#r7>).\n",
        ),
        "a citation in a list item, indented four spaces": (
            note,
            "- item\n\n    R7 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r7)\n",
        ),
    }
    why_line = (  # typed by hand: a message function cannot check itself
        "  why: a link to the ruling's own anchor takes a reader to the ruling in one click, and a"
        " record moved by the mover is repaired in every link (rule 2 of plc-0004-decision-records)"
    )
    reports: dict[str, tuple[str, str, list[str]]] = {  # case: path, text, literal lines by hand
        "no anchor": (
            "docs/policies/c.md",
            bad_a,
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "R7 of [dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md)"'
                ' links no anchor where the anchor of R7 is "#r7"',
                why_line,
                "  fix: link the anchor of the first ruling named, with the destination"
                " ../decisions/dec-0016-yes-on-the-change.md#r7",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "the last ruling of a range": (
            "docs/policies/c.md",
            "R5 and R34 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r34).\n",
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "R5 and R34 of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md#r34)"'
                ' links "#r34" where the anchor of R5 is "#r5"',
                why_line,
                "  fix: link the anchor of the first ruling named, with the destination"
                " dec-0016-yes-on-the-change.md#r5",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "a handle after the link": (
            "docs/policies/c.md",
            "[dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md#r6)'s R7 holds.\n",
            [
                "RED: docs/policies/c.md:1: the citation"
                ' "[dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md#r6)\'s R7"'
                ' links "#r6" where the anchor of R7 is "#r7"',
                why_line,
                "  fix: link the anchor of the first ruling named, with the destination"
                " ../decisions/dec-0016-yes-on-the-change.md#r7",
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
                " [dec-0016-yes-on-the-change](../decisions/dec-0016-yes-on-the-change.md#r7)",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
        "a bare id of a record not in the tree": (
            "docs/policies/c.md",
            "See R9 of dec-0004-catalogs-module here.\n",
            [
                'RED: docs/policies/c.md:1: the citation "R9 of dec-0004-catalogs-module"'
                " names the record by its id with no link",
                why_line,
                "  fix: write R9 of [dec-0004-catalogs-module](<path to that record>#r9)",
                "RED: 1 finding(s) — 3 document(s) examined",
            ],
        ),
    }

    gate_path = "shared/GATE.md"
    module_path = "modules/const-x/MODULE.md"
    shared_lines = (  # the shared document in miniature: a table, and the paragraph of g3a
        '<a id="g3"></a>\n## 3. Shared messages\n\nLead.\n\n<a id="g3a"></a>\n'
        "A module takes `G1` and `C5` for its part, as `scripts/check-handle-forms.py` reads it.\n\n"
        "| key | text |\n|---|---|\n| G1 | a |\n| G1.1 | b |\n| N1.1 | c |\n| N1.2 | d |\n"
        "| C4b | e |\n| C5.1 | f |\n| H2 | g |\n\n"
        '<a id="g4"></a>\n## 4. Limits\n'
    )

    def module_doc(rows: str, after: str = "") -> str:  # the table's first row is line 6
        return (
            '<a id="t6"></a>\n## 6. Artifacts\n\n| key | text |\n|---|---|\n'
            + rows
            + '\n<a id="t7"></a>\n## 7. Next\n\n'
            + after
        )

    keys_red: dict[str, tuple[str, str, tuple[int, ...]]] = {  # case: rows green, rows red, lines by hand
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
            "BROKEN: shared/GATE.md is missing, and a module's message table is read against it",
        ),
        "the paragraph of g3a missing": (
            shared_lines.replace('<a id="g3a"></a>\n', ""),
            "| X1 | a |\n",
            'BROKEN: shared/GATE.md holds the anchor <a id="g3a"></a> 0 time(s)',
        ),
        "the paragraph of g3a naming no key": (
            shared_lines.replace("`G1` and `C5`", "none"),
            "| X1 | a |\n",
            "BROKEN: shared/GATE.md: the paragraph after the anchor g3a names no key in a code span",
        ),
        "the paragraph of g3a naming a key the table lacks": (
            shared_lines.replace("`C5`", "`Q9`"),
            "| X1 | a |\n",
            "BROKEN: shared/GATE.md: the paragraph of g3a names Q9, which the table of section 3 lacks",
        ),
        "a module document without its anchor t6": (
            shared_lines,
            "",
            'BROKEN: modules/const-x/MODULE.md has no anchor <a id="t6"></a>',
        ),
    }

    def fresh(root: Path) -> None:
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
        write(root, record, "A record.\n")
        write(root, "docs/policies/plc-0004-decision-records.md", "A policy.\n")

    def write(root: Path, path: str, text: str) -> None:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")

    judged = 0
    failed = 0

    def judge(ok: bool, text: str) -> None:
        nonlocal judged, failed
        judged += 1
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")

    for name, (path, good, bad, lines) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, good)
            green_before = not check_kit(root)[0]
            write(root, path, bad)
            findings = check_kit(root)[0]
        red_after = tuple(f.line for f in findings) == lines and all(f.path == path for f in findings)
        judge(green_before and red_after, f"the correct form is green, {name} is red")
    for name, (path, text) in green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, text)
            judge(not check_kit(root)[0], f"the wrong form in {name} is not read")
    for name, (path, text, expected) in reports.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, text)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = report(*check_kit(root))
        judge(
            code == EXIT_RED and printed.getvalue().splitlines() == expected,
            f"the report of one finding, {name}, is its literal text, exit 2",
        )
    for name, (good_rows, bad_rows, lines) in keys_red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, gate_path, shared_lines)
            write(root, module_path, module_doc(good_rows))
            green_before = not check_kit(root)[0]
            write(root, module_path, module_doc(bad_rows))
            findings = check_kit(root)[0]
        red_after = tuple(f.line for f in findings) == lines and all(f.path == module_path for f in findings)
        judge(green_before and red_after, f"the correct key is green, {name} is red")
    for name, (rows, after) in keys_green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, gate_path, shared_lines)
            write(root, module_path, module_doc(rows, after))
            judge(not check_kit(root)[0], f"{name} is not a finding")
    for name, (gate_text, rows, start) in keys_broken.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            if gate_text is not None:
                write(root, gate_path, gate_text)
            write(root, module_path, module_doc(rows) if rows else "A document with no sections.\n")
            try:
                check_kit(root)
                said = "no BROKEN: the check passed"
            except Broken as broken:
                said = f"BROKEN: {broken}"
        judge(
            said.startswith(start) and " — fix: " in said, f"{name} is a teaching BROKEN line, never a pass"
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, gate_path, shared_lines)
        write(root, module_path, module_doc("| N1 | a |\n"))
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    judge(
        code == EXIT_RED
        and printed.getvalue().splitlines()
        == [
            'RED: modules/const-x/MODULE.md:6: the module\'s message table takes the key "N1", which the'
            " shared table of shared/GATE.md holds for a message of its own (family N1)",
            "  why: one key names one message in every module, so a reader who meets the key in a log or a"
            " document finds the same message wherever it stands (paragraph g3a of shared/GATE.md)",
            '  fix: rename "N1" to a prefix that neither table uses (the shared table uses C, G, H, N), in'
            " the module's messages.py, in its tests and in this table together",
            "RED: 1 finding(s) — 4 document(s) examined",
        ],
        "the report of one finding, a shared key in a module's table, is its literal text, exit 2",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
        judge(
            code == EXIT_GREEN
            and printed.getvalue().splitlines()
            == ["GREEN: every handle is written in its form — 2 document(s) examined"],
            "the report of a green tree is its literal line, exit 0",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
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
    judge(ok, "a file that is not UTF-8 is a teaching BROKEN line, never a traceback")
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(io.StringIO()):
        code = main(["--bogus"])
    judge(
        code == EXIT_BROKEN
        and printed.getvalue().splitlines()
        == [
            "BROKEN: misinvocation — fix: run with no arguments, or with --self-test",
            "BROKEN: the check could not run — 0 documents examined",
        ],
        "a misinvocation is a teaching BROKEN line, exit 1",
    )
    print(f"{judged - failed}/{judged} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


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
