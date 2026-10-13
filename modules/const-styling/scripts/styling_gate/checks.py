"""The examination of one document: every trace of a signature it carries, as a function of
its text. Lines are read once, in order; a fenced block, at any indentation, hides everything
but a PlantUML opener and is closed only by a bare fence of its kind; an HTML comment hides
its lines from its opener to its closing line, the closing line whole — a comment reopening
there is hidden with it — the text before the opener read, and a comment on one line is
masked, one after another closed hiding the rest; code spans, link destinations and bare URLs
hide emphasis; the state the multi-line signatures need — the heading before, the numbers of
the open ordered lists, the table being read — is kept as the lines go by and dropped where
the construct ends."""

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
    lines = text.removeprefix("﻿").split("\n")
    reader = _Reader(lines)
    for number, line in enumerate(lines, 1):
        reader.read(number, line)
    return reader.hits


@dataclass(slots=True)
class _Reader:
    """The state the lines are read in — the open fence, comment, table and lists, the heading
    before — and the hits found so far."""

    lines: list[str]
    hits: list[Hit] = field(default_factory=list)
    fence: str | None = None
    fence_is_plantuml: bool = False
    heading_before: int | None = None
    h1_seen: bool = False
    lists: _Lists = field(default_factory=_Lists)
    table: _Table | None = None
    comment: bool = False

    def read(self, number: int, line: str) -> None:
        """Reads one line: hidden by a comment or a fence, opening a fence, or read as text."""
        if self.comment:  # inside a comment: its lines are hidden, the closing line whole
            self.comment = "-->" not in line
            return
        opener = FENCE.match(line)
        if self.fence is not None:
            self._fenced(self.fence, number, line, opener)
            return
        if opener and (opener.group(1)[0] == "~" or "`" not in opener.group(2)):
            self._open_fence(number, line, opener)
            return
        line = self._hide_comments(line)
        self.table = _table_line(line, number, self.lines, self.table, self.hits)
        heading = HEADING.match(line)
        if heading:
            self._heading(number, heading)
            return
        self._line_traces(number, line)
        item = ITEM.match(line)
        if item:
            self._item(number, item)
        elif line.strip() != "" and not line.startswith((" ", "\t")):
            self.lists.end()

    def _fenced(self, fence: str, number: int, line: str, opener: re.Match[str] | None) -> None:
        """A line inside a fence: a bare fence of its kind closes it; a PlantUML opener in a fence
        of another language is still a trace."""
        if (
            opener
            and opener.group(1)[0] == fence[0]
            and len(opener.group(1)) >= len(fence)
            and not opener.group(2).strip()
        ):
            self.fence = None
        elif not self.fence_is_plantuml and line.lstrip().startswith("@startuml"):
            self.hits.append(Hit(Signature.PLANTUML, number, line.strip()))

    def _open_fence(self, number: int, line: str, opener: re.Match[str]) -> None:
        """A fence opens: its language is a trace when PlantUML or a formula, its absence too; it
        ends the open lists and table."""
        self.fence = opener.group(1)
        info = opener.group(2).strip()
        language = info.split()[0].lower() if info else ""
        self.fence_is_plantuml = language in PLANTUML_LANGUAGES
        if self.fence_is_plantuml:
            self.hits.append(Hit(Signature.PLANTUML, number, line.strip()))
        elif language in FORMULA_LANGUAGES:
            self.hits.append(Hit(Signature.FORMULA, number, line.strip()))
        elif not language:
            self.hits.append(Hit(Signature.FENCE_LANGUAGE, number, ""))
        self.lists.end()
        self.table = None

    def _hide_comments(self, line: str) -> str:
        """The line with its comments blanked: a comment on one line is masked, one that runs on
        hides the rest of the line, opens the comment state and ends the open lists and table."""
        while "<!--" in (spanless := CODE_SPAN.sub(_blank, line)):  # an opener outside a code span
            start = spanless.index("<!--")
            end = line.find("-->", start)  # a closer closes anywhere, a code span included
            if end < 0:  # a comment opens here and runs on: the rest of the line is hidden
                self.comment = True
                self.lists.end()
                self.table = None
                return line[:start]
            line = line[:start] + " " * (end + 3 - start) + line[end + 3 :]  # a comment on one line
        return line

    def _heading(self, number: int, heading: re.Match[str]) -> None:
        """A heading: too deep, a skipped level, a second level one; it ends the open lists."""
        level = len(heading.group(1))
        if level > DEEPEST:
            self.hits.append(Hit(Signature.DEEP_HEADING, number, str(level)))
        if self.heading_before is not None and level > self.heading_before + 1:
            self.hits.append(Hit(Signature.SKIPPED_LEVEL, number, str(level)))
        if level == 1:
            if self.h1_seen:
                self.hits.append(Hit(Signature.SECOND_H1, number, (heading.group(2) or "").strip()))
            self.h1_seen = True
        self.heading_before = level
        self.lists.end()

    def _line_traces(self, number: int, line: str) -> None:
        """The traces a line of text carries on its own: a callout, a block formula, a PlantUML
        opener outside a fence, emphasis by underscores outside code spans and links."""
        if ALERT.match(line):
            self.hits.append(Hit(Signature.CALLOUT, number, line.strip()))
        if BLOCK_MATH.match(line):
            self.hits.append(Hit(Signature.FORMULA, number, line.strip()))
        if line.lstrip().startswith("@startuml"):
            self.hits.append(Hit(Signature.PLANTUML, number, line.strip()))
        masked = MASKED.sub(_blank, CODE_SPAN.sub(_blank, line))
        for found in UNDERSCORE.finditer(masked):
            self.hits.append(Hit(Signature.UNDERSCORE_EMPHASIS, number, found.group(2)))

    def _item(self, number: int, item: re.Match[str]) -> None:
        """A list item: a marker other than `-`, a number that does not follow the one before."""
        indent = len(item.group(1).expandtabs(4))
        marker = item.group(2)
        ordered = int(marker[:-1]) if marker[-1] in ".)" else None
        if marker in ("*", "+"):
            self.hits.append(Hit(Signature.LIST_MARKER, number, item.group(3).strip()))
        before = self.lists.item(indent, ordered, marker[-1])
        if ordered is not None and before is not None and ordered != before + 1:
            self.hits.append(Hit(Signature.LIST_NUMBERING, number, f"{ordered} after {before}"))


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
