"""The examination of one document: every trace of a signature it carries, as a function of
its text. Lines are read once, in order; a fenced block, at any indentation, hides everything
but a PlantUML opener and is closed only by a bare fence of its kind; an HTML comment hides
its lines from its opener to its closing line, the text before the opener read, and a comment
on one line is masked; code spans, link destinations and bare URLs hide emphasis; the state the multi-line
signatures need — the heading before, the numbers of the open ordered lists, the table being
read — is kept as the lines go by and dropped where the construct ends."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .model import Hit, Signature

FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*#*[ \t]*$")
ITEM = re.compile(r"^([ \t]*)([-*+]|[0-9]{1,9}[.)])[ \t]+(.*)$")
ALERT = re.compile(r"^ {0,3}>[ \t]*\[!")
BLOCK_MATH = re.compile(r"^ {0,3}\$\$")
CODE_SPAN = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
MASKED = re.compile(
    r"\]\([^)]*\)|<[a-z]+://[^>]*>|[a-z]+://\S+|<!--.*?-->"
)  # a link's destination, a URL, a comment
UNDERSCORE = re.compile(r"(?<![\w\\])(__?)(?=[^\s_])(.+?)(?<=[^\s_])\1(?!\w)")
DELIMITER_CELL = re.compile(r"^:?-+:?$")
PLANTUML_LANGUAGES = {"plantuml", "puml"}
FORMULA_LANGUAGES = {"math", "latex", "tex"}
DEEPEST = 3


@dataclass(slots=True)
class _Lists:
    """The open ordered lists by indentation: the last number written at each."""

    numbers: dict[int, tuple[int, str]] = field(default_factory=dict)

    def item(self, indent: int, ordered: int | None, delimiter: str) -> int | None:
        """An item at `indent`: the number the last ordered item at that indent had, when this one
        is ordered and follows one with the same delimiter — a change of delimiter, `.` to `)`,
        starts a new list; deeper lists are closed by it."""
        for deeper in [i for i in self.numbers if i > indent]:
            del self.numbers[deeper]
        before = self.numbers.get(indent)
        if ordered is None:
            self.numbers.pop(indent, None)
            return None
        self.numbers[indent] = (ordered, delimiter)
        return before[0] if before is not None and before[1] == delimiter else None

    def end(self) -> None:
        self.numbers.clear()


@dataclass(slots=True)
class _Table:
    columns: int
    header_line: int


def examine(text: str) -> list[Hit]:
    """Every trace of a signature in the document, in line order."""
    hits: list[Hit] = []
    fence: str | None = None
    fence_is_plantuml = False
    heading_before: int | None = None
    h1_seen = False
    lists = _Lists()
    table: _Table | None = None
    comment = False
    lines = text.removeprefix("﻿").split("\n")
    for number, line in enumerate(lines, 1):
        if comment:  # inside a comment: its lines are hidden, the closing line whole
            comment = "-->" not in line
            continue
        opener = FENCE.match(line)
        if fence is not None:
            if (
                opener
                and opener.group(1)[0] == fence[0]
                and len(opener.group(1)) >= len(fence)
                and not opener.group(2).strip()
            ):
                fence = None
            elif not fence_is_plantuml and line.lstrip().startswith("@startuml"):
                hits.append(Hit(Signature.PLANTUML, number, line.strip()))
            continue
        if opener and (opener.group(1)[0] == "~" or "`" not in opener.group(2)):
            fence = opener.group(1)
            info = opener.group(2).strip()
            language = info.split()[0].lower() if info else ""
            fence_is_plantuml = language in PLANTUML_LANGUAGES
            if fence_is_plantuml:
                hits.append(Hit(Signature.PLANTUML, number, line.strip()))
            elif language in FORMULA_LANGUAGES:
                hits.append(Hit(Signature.FORMULA, number, line.strip()))
            elif not language:
                hits.append(Hit(Signature.FENCE_LANGUAGE, number, ""))
            lists.end()
            table = None
            continue
        spanless = CODE_SPAN.sub(_blank, line)
        if "<!--" in spanless and "-->" not in line[spanless.index("<!--") :]:  # a comment opens here
            comment = True  # its opener is no opener inside a code span; its closer closes anywhere
            line = line[: spanless.index("<!--")]
            lists.end()
            table = None
        table = _table_line(line, number, lines, table, hits)
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if level > DEEPEST:
                hits.append(Hit(Signature.DEEP_HEADING, number, str(level)))
            if heading_before is not None and level > heading_before + 1:
                hits.append(Hit(Signature.SKIPPED_LEVEL, number, str(level)))
            if level == 1:
                if h1_seen:
                    hits.append(Hit(Signature.SECOND_H1, number, (heading.group(2) or "").strip()))
                h1_seen = True
            heading_before = level
            lists.end()
            continue
        if ALERT.match(line):
            hits.append(Hit(Signature.CALLOUT, number, line.strip()))
        if BLOCK_MATH.match(line):
            hits.append(Hit(Signature.FORMULA, number, line.strip()))
        if line.lstrip().startswith("@startuml"):
            hits.append(Hit(Signature.PLANTUML, number, line.strip()))
        masked = MASKED.sub(_blank, CODE_SPAN.sub(_blank, line))
        for found in UNDERSCORE.finditer(masked):
            hits.append(Hit(Signature.UNDERSCORE_EMPHASIS, number, found.group(2)))
        item = ITEM.match(line)
        if item:
            indent = len(item.group(1).expandtabs(4))
            marker = item.group(2)
            ordered = int(marker[:-1]) if marker[-1] in ".)" else None
            if marker in ("*", "+"):
                hits.append(Hit(Signature.LIST_MARKER, number, item.group(3).strip()))
            before = lists.item(indent, ordered, marker[-1])
            if ordered is not None and before is not None and ordered != before + 1:
                hits.append(Hit(Signature.LIST_NUMBERING, number, f"{ordered} after {before}"))
            continue
        if line.strip() == "" or line.startswith((" ", "\t")):
            continue
        lists.end()
    return hits


def _blank(match: re.Match[str]) -> str:
    return " " * len(match.group(0))


def _cells(line: str) -> list[str]:
    """The cells of a table line: split on pipes that are not escaped, the outer pipes dropped."""
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            current.append(char)
            escaped = True
        elif char == "|":
            cells.append("".join(current))
            current = []
        else:
            current.append(char)
    cells.append("".join(current))
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return cells


def _is_delimiter_row(line: str) -> bool:
    cells = _cells(line)
    return bool(cells) and "|" in line and all(DELIMITER_CELL.match(c.strip()) for c in cells)


def _table_line(
    line: str, number: int, lines: list[str], table: _Table | None, hits: list[Hit]
) -> _Table | None:
    """Reads one line as part of a table, or as the header of one: a table opens on a line of
    cells followed by a delimiter row, and ends on a blank line or a line without a pipe."""
    if table is None:
        if "|" in line and number < len(lines) and _is_delimiter_row(lines[number]):
            return _Table(len(_cells(line)), number)
        return None
    if number == table.header_line + 1:  # the delimiter row: its cells are the alignment marks
        cells = _cells(line)
        if len(cells) != table.columns:
            hits.append(
                Hit(
                    Signature.TABLE_COLUMNS, number, f"{len(cells)} cell(s) under a header of {table.columns}"
                )
            )
        return table
    if line.strip() == "" or "|" not in line:
        return None
    cells = _cells(line)
    if len(cells) != table.columns:
        hits.append(
            Hit(Signature.TABLE_COLUMNS, number, f"{len(cells)} cell(s) under a header of {table.columns}")
        )
    for column, cell in enumerate(cells, 1):
        if cell.strip() == "":
            hits.append(Hit(Signature.TABLE_EMPTY_CELL, number, str(column)))
    return table
