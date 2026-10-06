"""Kit tooling, never shipped in a module: where a kit check reads a section of a module document.

A module document (template `MODULE.md`) puts the anchor `<a id="tN"></a>` alone on the line above
the heading of its section N. `section` reads one section by that anchor, so that a heading's number,
its wording or its place never decides what is read, and it fails loud where a read would otherwise
go quietly wrong: an anchor gone, an anchor twice, or an anchor with text on its line.

Only a line whose stripped form is exactly the anchor counts; the same anchor written inside other
text, as in prose that shows it, is plain text and no anchor. The section ends at the next such
anchor, whatever its number, or at the end of the file. There is no runner of its own: each check
that reads through it proves it in its own `--self-test`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

ANCHOR = re.compile(r'^<a id="(t\d+)"></a>$')


class DocumentError(Exception):
    """A section of a module document cannot be read; the message says why and how to fix it."""


def section(text: str, anchor: str, path: str) -> list[tuple[int, str]]:
    """The lines (1-based number, text) after the line of `anchor` up to, not including, the next
    section anchor of any number, or to the end of the text; `path` names the document in a message."""
    lines = text.splitlines()
    stands: dict[str, list[int]] = {}
    for number, line in enumerate(lines, start=1):
        if (found := ANCHOR.match(line.strip())) is not None:
            stands.setdefault(found[1], []).append(number)
    if anchor not in stands:
        raise DocumentError(
            f'{path} has no anchor <a id="{anchor}"></a> on a line of its own'
            " — fix: restore the template's anchor, alone on its line"
        )
    for name, numbers in stands.items():
        if len(numbers) > 1:
            raise DocumentError(
                f'{path} holds the anchor <a id="{name}"></a> twice, lines {numbers[0]} and {numbers[1]}'
                " — fix: keep the one before its section's heading"
            )
    start = stands[anchor][0]
    later = sorted(number for numbers in stands.values() for number in numbers if number > start)
    end = later[0] if later else len(lines) + 1
    return [(number, lines[number - 1]) for number in range(start + 1, end)]


class Fault(StrEnum):
    """What is wrong with a line of the enforcement section."""

    FIRST_CELL = "first cell"  # a table row that opens with anything but `E<n>` or `**E<n>**`
    SPAN = "span"  # a table row's code span that holds `--scan` in a form the check cannot read
    UNMARKED = "unmarked"  # a flag after `--scan` in a row whose artifact cell lacks the mark
    PROSE = "prose"  # a span in the declared form outside the table


@dataclass(frozen=True)
class Problem:
    line: int  # the line in the document
    fault: Fault
    text: str  # the first cell, or the span


ENTRY = r"[a-z][a-z0-9-]*(?:\.py)?"
DECLARED = re.compile(rf"({ENTRY}) --scan")  # `<entry> --scan` or `<entry>.py --scan`, nothing after
EXPLAIN = re.compile(rf"({ENTRY}) --scan(?: --[a-z][a-z0-9-]*(?: [^\s-]\S*)?)+")  # a flag or more after
HANDLE = re.compile(r"E\d+|\*\*E\d+\*\*")
SPAN = re.compile(r"`([^`]*)`")
SEPARATOR = re.compile(r"\|(?:\s*:?-+:?\s*\|)+")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
MARK = re.compile(r"\bnot a tree scan\b")  # the words that make a flag after `--scan` another mode


def cells(line: str) -> list[str]:
    """The cells of a table line, outer bars dropped, each stripped."""
    return [part.strip() for part in CELL_SPLIT.split(line.strip())[1:-1]]


def enforcement(text: str, path: str) -> tuple[list[str], list[Problem]]:
    """The scans a module document declares, sorted, and what is wrong with its enforcement section
    (anchor `t9`): a table line is a line whose stripped form starts with `|`, the separator and the
    header line above it skipped; a row opens with `E<n>` or `**E<n>**`; a code span in a row that holds
    `--scan` reads `<entry> --scan`, which declares the scan, or `<entry> --scan --<flag> …` in a row
    whose artifact cell, the cell that holds the span, also holds the words `not a tree scan` outside
    any code span, which declares none; any other such span is a problem; outside the table, a span in
    the declared form is a problem and any other is ignored."""
    body = section(text, "t9", path)
    headers = {
        number
        for (number, _), (_, below) in zip(body, body[1:], strict=False)
        if SEPARATOR.fullmatch(below.strip())
    }
    scans: set[str] = set()
    problems: list[Problem] = []
    for number, raw in body:
        line = raw.strip()
        if not line.startswith("|"):
            problems += [
                Problem(number, Fault.PROSE, span)
                for span in SPAN.findall(line)
                if DECLARED.fullmatch(span) is not None
            ]
            continue
        if number in headers or SEPARATOR.fullmatch(line):
            continue
        row = cells(line)
        if not row or HANDLE.fullmatch(row[0]) is None:
            problems.append(Problem(number, Fault.FIRST_CELL, row[0] if row else ""))
        for cell in row:
            for span in SPAN.findall(cell):
                if "--scan" not in span:
                    continue
                if (found := DECLARED.fullmatch(span)) is not None:
                    scans.add(found[1])
                elif EXPLAIN.fullmatch(span) is None:
                    problems.append(Problem(number, Fault.SPAN, span))
                elif MARK.search(SPAN.sub("", cell)) is None:
                    problems.append(Problem(number, Fault.UNMARKED, span))
    return sorted(scans), problems
