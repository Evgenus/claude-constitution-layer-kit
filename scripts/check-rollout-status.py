#!/usr/bin/env python3
"""Kit check: the status matrix of the rollout plan, docs/rollout-plan.md, matches the plan's items, and
the items keep the form that lets them be counted (rules 3, 4, 5, 8 and 10 of the policy
plc-0008-rollout-plan; decision dec-0103-rollout-plan-status-matrix, R4 and R5).

The plan opens with a table, the status matrix, of one row for each step. A step is a numbered line with
an anchor, `<n>. <a id="s<n>"></a>`. A phase is a line `<a id="phase-<x>"></a>`, and a step stands in the
phase of the last phase line above it. The items of a step are the list lines under it, each opening with
one mark: ✅ done, ⏳ open, 💤 waiting. The check counts the marks, derives every cell of the matrix from
the counts, and is red wherever the table says otherwise. It reads the file by lines, with the standard
library alone. A finding is one line of the file, with what failed, why the rule exists and the exact fix.

What it holds, each failure a finding of its own:
  1. The matrix. Exactly one table with the matrix's header, standing before the first phase line, whose
     header row is `| Step | Title | Phase | Status | Done | Open | Waiting | % done |`, with a separator row
     under it; a table with another header is not read. Every row has 8 cells, a `\\|` staying inside its
     cell. The first cell of a step row is the link `[s<n>](#s<n>)`; the first cell of the last row is `all`.
  2. The rows against the steps. One row for each step, none for a step the plan lacks, none twice, in
     the order the steps stand in the plan, and the row `all` last. A row whose first cell names no step
     is a finding. A step's number stands once.
  3. The cells. Each cell is of its form: the phase one capital letter (the word `all` on the last row),
     the status one of ✅ ⏳ 🔄 💤, the counts whole numbers, the percent a whole number with `%` or `n/a`.
     Each cell is also what the items give: the phase is that of the last phase line above the step; done,
     open and waiting count the ✅, ⏳ and 💤 items of the step; the percent is done * 100 // (done + open),
     rounded down, and `n/a` where done + open is 0; the status is ✅ when no item is open or waiting, ⏳
     when an item is open and none is done, 🔄 when an item is done and another is open, 💤 when no item
     is open and one is waiting. The row `all` holds the sums of the steps, its percent and status by the
     same rules. A step stands under a phase line. Where an item of a step has no mark, the counts, the
     percent and the status of its row, and of the row `all`, are left uncompared until it has one.
  4. The items. Every list line of a step, outside a fenced block, is an item: a line that starts, indented
     or not, with `-`, `*` or `+` and a space, or with digits, `.` or `)` and a space, the line of a step
     itself excepted. An item is one line, its link on that line, and reads
     `- <a id="s<n>-<m>"></a>**<n>.<m>** <mark> <text>`: <n> the number of its step, <m> its number in the
     step, anchor and handle agreeing with each other and with the step, one mark of ✅ ⏳ 💤, a space and
     words. A list line in any other form is a finding. The numbers ascend, gaps allowed: the first <m> is
     any whole number from 1, with a letter or none, and each next item is numbered above the one before
     it, a letter standing after the same number without one and a before b. A number that is not above
     the one before is a finding, since a number once used is not used again; a leading zero is a finding.
     A fenced block is opened by a line that starts, after up to three spaces, with ``` or ~~~ and closed
     by a line of the same fence; what it holds is no list line and no step line.
  5. The steps' own marks. A step with items opens its own text, after its anchor, with no mark. A step
     with no items is its own one item: its text opens with one mark and a space.
  6. The links. A done item holds an inline Markdown link, `[text](target)`, on its own line, and so does
     a done step with no items.

What it leaves to review: whether a mark matches the words of its item, whether a link is the proof of its
item, a done item's words, a row's title, and every other content of the plan; the style, the language and
the length of the plan are held by the modules that hold them.

Modes:  no arguments   check docs/rollout-plan.md at the kit root;
        --self-test    prove the check on throwaway texts: a valid plan green, and each hold above red
                       alone; the report of one finding as literal lines with exit 2; an absent plan and a
                       plan that is not UTF-8 each a BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import enum
import io
import re
import sys
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
PLAN = "docs/rollout-plan.md"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
HEADER = "| Step | Title | Phase | Status | Done | Open | Waiting | % done |"
SEPARATOR_ROW = "| --- | --- | --- | --- | --- | --- | --- | --- |"
CELLS = 8

PHASE_LINE = re.compile(r'^<a id="phase-([a-z])"></a>\s*$')
STEP_LINE = re.compile(r'^(\d+[a-z]?)\. <a id="s\1"></a>(.*)$')
LIST_LINE = re.compile(r"^\s*(?:[-*+]|\d+[.)]) ")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
ITEM_FORM = re.compile(r'^\s*- <a id="([^"]*)"></a>\*\*([^*]*)\*\* (.*)$')
HANDLE = re.compile(r"(\d+[a-z]?)\.(\d+[a-z]?)")
ANCHOR = re.compile(r"s(\d+[a-z]?)-(\d+[a-z]?)")
NUMBER = re.compile(r"(\d+)([a-z]?)")
LINK = re.compile(r"\[[^\]]+\]\([^)\s][^)]*\)")
CELL_BOUNDARY = re.compile(r"(?<!\\)\|")
SEPARATOR = re.compile(r"^\|[\s:|-]*-[\s:|-]*\|$")
STEP_KEY = re.compile(r"s\d+[a-z]?")

WHY_MATRIX = (
    "the plan opens with one summary row for each step, in order, as rule 10 of plc-0008-rollout-plan says"
)
WHY_DRIFT = "the matrix is the plan's summary, and a count typed by hand drifts from its items"
WHY_MARK = "an item is counted by its one mark, as rule 5 of plc-0008-rollout-plan says"
WHY_STEP_MARK = "a step with items is counted by its items alone, as rule 5 of plc-0008-rollout-plan says"
WHY_LINK = "a done item's link is its proof, the record or the document its change concerns"
WHY_ID = (
    "an item is cited by its anchor and its handle, which rule 4 of plc-0008-rollout-plan ties to its step"
)
WHY_NUMBER = (
    "an item keeps its number for good, and rule 4 of plc-0008-rollout-plan numbers the items of a step in"
    " ascending order from 1"
)
WHY_LIST = "every list line under a step is counted as an item, so a line that is none cannot stand there"
WHY_PHASE = "each step stands in the phase above it, and its row names that phase"
WHY_STEPS = "a step is cited by its number, and its row is found by it"


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


class Mark(enum.Enum):
    DONE = "✅"
    OPEN = "⏳"
    WAITING = "💤"
    PARTLY = "🔄"  # a step's status only, never an item's mark


ITEM_MARKS = {mark.value: mark for mark in (Mark.DONE, Mark.OPEN, Mark.WAITING)}
SIGNS = frozenset(mark.value for mark in Mark)


@dataclass(frozen=True)
class Finding:
    line: int
    what: str
    why: str
    fix: str

    def render(self) -> str:
        return f"RED: {PLAN}:{self.line}: {self.what}\n  why: {self.why}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Counts:
    done: int = 0
    open: int = 0
    waiting: int = 0

    def __add__(self, other: Counts) -> Counts:
        return Counts(self.done + other.done, self.open + other.open, self.waiting + other.waiting)

    def percent(self) -> str:
        if self.done + self.open == 0:
            return "n/a"
        return f"{self.done * 100 // (self.done + self.open)}%"

    def status(self) -> Mark:
        if self.open == 0:
            return Mark.WAITING if self.waiting > 0 else Mark.DONE
        return Mark.PARTLY if self.done > 0 else Mark.OPEN


@dataclass(frozen=True)
class Item:
    line: int
    shaped: bool  # the line reads `- <a id="…"></a>**…** …`
    anchor: str
    handle: str
    mark: Mark | None


@dataclass(frozen=True)
class Step:
    number: str
    line: int
    phase: str  # the letter, upper case; empty above the first phase line
    items: tuple[Item, ...]

    @property
    def key(self) -> str:
        return f"s{self.number}"


@dataclass
class Span:
    """The lines of one step: its own line, and the list lines under it."""

    number: str
    line: int
    phase: str
    text: str
    lines: list[tuple[int, str]]


@dataclass(frozen=True)
class Derived:
    """What the items give for one row of the matrix."""

    phase: str
    counts: Counts
    settled: bool  # every item carries a mark, so the counts mean something

    def cells(self) -> tuple[str, ...]:
        counts = self.counts
        return (
            self.phase,
            counts.status().value,
            str(counts.done),
            str(counts.open),
            str(counts.waiting),
            counts.percent(),
        )


@dataclass(frozen=True)
class Column:
    name: str
    form: re.Pattern[str]
    words: str
    said: str
    held: str


COLUMNS = (
    Column("Phase", re.compile(r"[A-Z]"), "one capital letter", "phase {}", "the step stands under phase {}"),
    Column("Status", re.compile("[✅⏳🔄💤]"), "one of ✅ ⏳ 🔄 💤", "status {}", "its items give {}"),
    Column("Done", re.compile(r"\d+"), "a whole number", "{} done", "its items hold {}"),
    Column("Open", re.compile(r"\d+"), "a whole number", "{} open", "its items hold {}"),
    Column("Waiting", re.compile(r"\d+"), "a whole number", "{} waiting", "its items hold {}"),
    Column(
        "% done",
        re.compile(r"\d+%|n/a"),
        "a whole number with %, or n/a",
        "{} as its percent done",
        "its items give {}",
    ),
)
ALL_PHASE = Column("Phase", re.compile("all"), "the word all", "phase {}", "{}")


@dataclass(frozen=True)
class Row:
    line: int
    key: str | None  # `s9`, or `all`, or None where the first cell names no step
    cells: tuple[str, ...]


@dataclass(frozen=True)
class Matrix:
    header: int
    separated: bool
    rows: tuple[Row, ...]


@dataclass(frozen=True)
class Result:
    findings: tuple[Finding, ...]
    steps: int
    items: int
    counts: Counts


def label(key: str) -> str:
    return "the row all" if key == "all" else f"the row of {key}"


def split_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").split("\n")


def first_phase_line(lines: list[str]) -> int | None:
    return next((n for n, line in enumerate(lines, start=1) if PHASE_LINE.match(line)), None)


def fence_opening(line: str) -> str:
    """The fence a line opens, three or more ` or ~, or an empty string where it opens none. The words after
    a ` fence hold no `, or the line is inline code and no fence."""
    found = FENCE.match(line)
    if found is None or (found.group(1)[0] == "`" and "`" in found.group(2)):
        return ""
    return found.group(1)


def closes_fence(fence: str, line: str) -> bool:
    """Whether the line closes the block the fence opened: the same character, as many or more, no words."""
    found = FENCE.match(line)
    if found is None:
        return False
    return found.group(1)[0] == fence[0] and len(found.group(1)) >= len(fence) and not found.group(2).strip()


def unfenced(lines: list[str]) -> Iterator[tuple[int, str]]:
    """The lines outside the fenced blocks, each with its number from 1; the fence lines and what they
    enclose are left out. A block left open runs to the end of the file."""
    fence = ""
    for number, line in enumerate(lines, start=1):
        if fence:
            fence = "" if closes_fence(fence, line) else fence
        else:
            fence = fence_opening(line)
            if not fence:
                yield number, line


def split_steps(lines: list[str]) -> list[Span]:
    """The steps of the plan, each with the list lines of its span: from its line to the next step line, the
    next phase line or the end of the file; a fenced block holds none."""
    spans: list[Span] = []
    phase = ""
    current: Span | None = None
    for number, line in unfenced(lines):
        opened = PHASE_LINE.match(line)
        step = STEP_LINE.match(line)
        if opened:
            phase, current = opened.group(1).upper(), None
        elif step:
            current = Span(step.group(1), number, phase, step.group(2), [])
            spans.append(current)
        elif current is not None and LIST_LINE.match(line):
            current.lines.append((number, line))
    return spans


def read_mark(name: str, after: str, line: int, rest: str) -> tuple[Mark | None, list[Finding]]:
    """The one mark an item opens with, and what is wrong with the way it opens."""
    mark = ITEM_MARKS.get(rest[:1])
    if mark is None:
        fix = f"write one of ✅ ⏳ 💤 and a space {after}"
        return None, [Finding(line, f"{name} opens with no status mark", WHY_MARK, fix)]
    text = rest[1:]
    if not text.startswith(" ") or not text.strip():
        fix = "write a space and the words of the item after the mark"
        return mark, [Finding(line, f"{name} has no space and no text after its mark", WHY_MARK, fix)]
    if text.strip()[:1] in SIGNS:
        fix = "keep one of ✅ ⏳ 💤 and delete the other"
        return mark, [Finding(line, f"{name} opens with two marks", WHY_MARK, fix)]
    return mark, []


def link_finding(name: str, line: int) -> Finding:
    fix = (
        "link its record, or the document or the module its routine change concerns, or, once its record is"
        " deleted, the current-state document that carries its ruling"
    )
    return Finding(line, f"done {name} holds no link", WHY_LINK, fix)


def read_item(line_no: int, line: str) -> tuple[Item, list[Finding]]:
    shaped = ITEM_FORM.match(line.rstrip())
    if shaped is None:
        return Item(line_no, False, "", "", None), []
    anchor, handle, rest = shaped.groups()
    name = f"item {handle}"
    mark, findings = read_mark(name, f"after **{handle}**", line_no, rest)
    if mark is Mark.DONE and LINK.search(rest) is None:
        findings.append(link_finding(name, line_no))
    return Item(line_no, True, anchor, handle, mark), findings


def read_solo(span: Span) -> tuple[Item, list[Finding]]:
    """A step with no items is its own one item, its mark right after its anchor."""
    name = f"step {span.number}, which has no items,"
    after = f"right after the anchor of step {span.number}"
    mark, findings = read_mark(name, after, span.line, span.text)
    if mark is Mark.DONE and LINK.search(span.text) is None:
        findings.append(link_finding(name, span.line))
    return Item(span.line, True, "", name, mark), findings


def parse_number(text: str) -> tuple[int, str] | None:
    parts = NUMBER.fullmatch(text)
    return None if parts is None else (int(parts.group(1)), parts.group(2))


def render_number(number: tuple[int, str]) -> str:
    return f"{number[0]}{number[1]}"


def after(previous: tuple[int, str] | None) -> tuple[int, str]:
    """A number above the one before, to write where an item reads none: the next whole number."""
    return (1, "") if previous is None else (previous[0] + 1, "")


def rises(previous: tuple[int, str] | None, own: tuple[int, str]) -> bool:
    """Whether an item's number may follow the one before: the first is any whole number from 1, each next
    is above the one before, a letter after the same number without one and a before b."""
    return own[0] >= 1 if previous is None else own > previous


def own_number(item: Item) -> tuple[int, str] | None:
    """The number an item claims: its handle's <m>, else its anchor's."""
    for pattern, text in ((HANDLE, item.handle), (ANCHOR, item.anchor)):
        parts = pattern.fullmatch(text)
        if parts is not None:
            return parse_number(parts.group(2))
    return None


def number_fix(number: str, previous: tuple[int, str]) -> str:
    """How to number an item that is not above the one before: this item alone changes."""
    count, letter = previous
    end = "a number above the highest of the step"
    options = end
    if letter != "z":
        between = f"{number}.{count}{'a' if not letter else chr(ord(letter) + 1)}"
        options = f"{between} for an item between two items, or {end} for an item at its end"
    return (
        f"give it a number above {number}.{render_number(previous)} in its handle and its anchor: {options};"
        " a number once used is not used again"
    )


def order_finding(number: str, item: Item, previous: tuple[int, str] | None) -> Finding:
    if previous is None:
        what = f"item {item.handle} opens step {number}, and its number is below 1"
        fix = (
            "give it a number from 1 up in its handle and its anchor; the items of a step are numbered from 1"
        )
        return Finding(item.line, what, WHY_NUMBER, fix)
    what = (
        f"item {item.handle} follows item {number}.{render_number(previous)}, and its number is not above it"
    )
    return Finding(item.line, what, WHY_NUMBER, number_fix(number, previous))


def id_finding(number: str, item: Item, current: tuple[int, str]) -> Finding | None:
    handle = f"{number}.{render_number(current)}"
    anchor = f"s{number}-{render_number(current)}"
    if (item.handle, item.anchor) == (handle, anchor):
        return None
    what = (
        f"the handle {item.handle} and the anchor {item.anchor} of an item do not agree with each other"
        f" and with step {number}"
    )
    return Finding(item.line, what, WHY_ID, f"write the handle **{handle}** and the anchor {anchor}")


def list_finding(number: str, line: int) -> Finding:
    shape = f'- <a id="s{number}-<m>"></a>**{number}.<m>** <mark> <text>'
    fix = (
        f"write it as an item, {shape}, with an <m> above every number before it in the step,"
        " or join its words to the sentence above"
    )
    return Finding(line, f"this list line of step {number} does not read as an item", WHY_LIST, fix)


def number_findings(number: str, items: list[Item]) -> list[Finding]:
    """The handle and anchor of each item against its step, and its number against the one before."""
    findings: list[Finding] = []
    previous: tuple[int, str] | None = None
    for item in items:
        if not item.shaped:
            findings.append(list_finding(number, item.line))
            continue
        own = own_number(item)
        if own is not None and not rises(previous, own):
            findings.append(order_finding(number, item, previous))
        current = own if own is not None else after(previous)
        misplaced = id_finding(number, item, current)
        if misplaced is not None:
            findings.append(misplaced)
        previous = current
    return findings


def read_step(span: Span) -> tuple[Step, list[Finding]]:
    findings: list[Finding] = []
    if not span.phase:
        fix = f'put the line <a id="phase-<letter>"></a> of its phase above step {span.number}'
        findings.append(
            Finding(span.line, f"step {span.number} stands above the first phase anchor", WHY_PHASE, fix)
        )
    if not span.lines:
        solo, found = read_solo(span)
        return Step(span.number, span.line, span.phase, (solo,)), findings + found
    if span.text.lstrip()[:1] in SIGNS:
        what = f"step {span.number} has items and opens with a mark of its own"
        fix = f"delete the mark from the line of step {span.number}; its items carry the marks"
        findings.append(Finding(span.line, what, WHY_STEP_MARK, fix))
    items: list[Item] = []
    for line_no, line in span.lines:
        item, found = read_item(line_no, line)
        items.append(item)
        findings += found
    findings += number_findings(span.number, items)
    return Step(span.number, span.line, span.phase, tuple(items)), findings


def read_steps(lines: list[str]) -> tuple[list[Step], list[Finding]]:
    """The steps of the plan, a step that stands twice left out after its finding, and the findings of
    their items."""
    steps: list[Step] = []
    findings: list[Finding] = []
    seen: dict[str, int] = {}
    for span in split_steps(lines):
        step, found = read_step(span)
        findings += found
        if step.key in seen:
            what = f"step {step.key} stands twice, first at line {seen[step.key]}"
            fix = "give the later step a number of its own, in its line, its anchor and its items"
            findings.append(Finding(step.line, what, WHY_STEPS, fix))
            continue
        seen[step.key] = step.line
        steps.append(step)
    return steps, findings


def derive(step: Step) -> Derived:
    marks = [item.mark for item in step.items]
    counts = Counts(marks.count(Mark.DONE), marks.count(Mark.OPEN), marks.count(Mark.WAITING))
    return Derived(step.phase, counts, None not in marks)


def derive_total(steps: list[Step]) -> Derived:
    parts = [derive(step) for step in steps]
    return Derived("all", sum((part.counts for part in parts), Counts()), all(part.settled for part in parts))


def split_cells(line: str) -> tuple[str, ...]:
    inner = line.strip()[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return tuple(cell.strip() for cell in CELL_BOUNDARY.split(inner))


def row_key(first: str) -> str | None:
    if first == "all":
        return "all"
    found = STEP_KEY.search(first)
    return found.group(0) if found else None


def read_matrix(lines: list[str], header: int) -> Matrix:
    """The rows under the header row at the 1-based line `header`, up to the first line that is no row."""
    index = header  # the 0-based index of the line under the header
    separated = index < len(lines) and SEPARATOR.match(lines[index].strip()) is not None
    index += 1 if separated else 0
    rows: list[Row] = []
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        cells = split_cells(lines[index])
        rows.append(Row(index + 1, row_key(cells[0]), cells))
        index += 1
    return Matrix(header, separated, tuple(rows))


def row_text(key: str, derived: Derived) -> str:
    first = "all" if key == "all" else f"[{key}](#{key})"
    return "| " + " | ".join((first, "<title>", *derived.cells())) + " |"


def index_rows(rows: tuple[Row, ...]) -> tuple[dict[str, Row], list[Finding]]:
    """The first row of each key, in the matrix's order; the rows that name no step, and the second row of
    a key, are findings."""
    by_key: dict[str, Row] = {}
    findings: list[Finding] = []
    for row in rows:
        if row.key is None:
            what = f'the first cell of this matrix row reads "{row.cells[0]}", which names no step'
            fix = (
                "write [s<n>](#s<n>) for the step the row sums up, or all for the last row, or delete the row"
            )
            findings.append(Finding(row.line, what, WHY_MATRIX, fix))
        elif row.key in by_key:
            fix = f"delete this second row of {row.key}"
            findings.append(Finding(row.line, f"the matrix has two rows for {row.key}", WHY_MATRIX, fix))
        else:
            by_key[row.key] = row
    return by_key, findings


def missing_findings(
    matrix: Matrix, derived: dict[str, Derived], total: Derived, by_key: dict[str, Row]
) -> list[Finding]:
    findings: list[Finding] = []
    line, previous = matrix.header, None
    for key, wanted in derived.items():
        row = by_key.get(key)
        if row is None:
            where = (
                f"after the row of {previous}" if previous else "as the first row, under the separator row"
            )
            fix = f"add the row {row_text(key, wanted)} {where}"
            findings.append(Finding(line, f"the matrix has no row for {key}", WHY_MATRIX, fix))
        else:
            line = row.line
        previous = key
    if "all" not in by_key:
        line = matrix.rows[-1].line if matrix.rows else matrix.header
        fix = f"add the row {row_text('all', total)} as the last row"
        findings.append(
            Finding(line, "the matrix has no last row all, the sums of its steps", WHY_MATRIX, fix)
        )
    return findings


def extra_findings(by_key: dict[str, Row], derived: dict[str, Derived]) -> list[Finding]:
    return [
        Finding(
            row.line,
            f"the matrix has a row for {key}, and the plan has no step {key}",
            WHY_MATRIX,
            f"delete the row of {key}",
        )
        for key, row in by_key.items()
        if key != "all" and key not in derived
    ]


def order_findings(by_key: dict[str, Row], derived: dict[str, Derived]) -> list[Finding]:
    placed = [row for key, row in by_key.items() if key in derived]
    wanted = [key for key in derived if key in by_key]
    for row, want in zip(placed, wanted, strict=True):
        if row.key != want:
            what = f"the row of {row.key} stands where the plan's order puts the row of {want}"
            fix = f"move the rows into the plan's order: {', '.join(wanted)}"
            return [Finding(row.line, what, WHY_MATRIX, fix)]
    return []


def all_position_findings(by_key: dict[str, Row], derived: dict[str, Derived]) -> list[Finding]:
    total = by_key.get("all")
    if total is None:
        return []
    for key, row in by_key.items():
        if key in derived and row.line > total.line:
            what = f"the row all stands above the row of {key}"
            return [Finding(total.line, what, WHY_MATRIX, "move the row all to the end of the matrix")]
    return []


def column_finding(row: Row, key: str, index: int, wanted: str) -> Finding | None:
    if not wanted:  # the step stands above the first phase line, and has its own finding
        return None
    column = ALL_PHASE if key == "all" and index == 0 else COLUMNS[index]
    shown = row.cells[2 + index]
    if column.form.fullmatch(shown) is None:
        what = f'the {column.name} cell of {label(key)} reads "{shown}", which is not {column.words}'
    elif shown != wanted:
        what = f"{label(key)} says {column.said.format(shown)}, and {column.held.format(wanted)}"
    else:
        return None
    return Finding(row.line, what, WHY_DRIFT, f"write {wanted} in the {column.name} cell of the row {key}")


def cell_findings(row: Row, key: str, derived: Derived) -> list[Finding]:
    if len(row.cells) != CELLS:
        what = f"{label(key)} has {len(row.cells)} cells, and the matrix has {CELLS}"
        fix = f"write the row with {CELLS} cells, escaping a | in its title as \\|: {row_text(key, derived)}"
        return [Finding(row.line, what, WHY_MATRIX, fix)]
    findings: list[Finding] = []
    if key != "all" and row.cells[0] != f"[{key}](#{key})":
        what = f'the first cell of {label(key)} reads "{row.cells[0]}", which is not a link to the step'
        fix = f"write [{key}](#{key}) in the first cell of the row {key}"
        findings.append(Finding(row.line, what, WHY_MATRIX, fix))
    shown = len(COLUMNS) if derived.settled else 1  # the counts, percent and status come from the marks
    for index, wanted in enumerate(derived.cells()[:shown]):
        found = column_finding(row, key, index, wanted)
        if found is not None:
            findings.append(found)
    return findings


def row_findings(matrix: Matrix, steps: list[Step]) -> list[Finding]:
    derived = {step.key: derive(step) for step in steps}
    total = derive_total(steps)
    by_key, findings = index_rows(matrix.rows)
    findings += missing_findings(matrix, derived, total, by_key)
    findings += extra_findings(by_key, derived)
    findings += order_findings(by_key, derived)
    findings += all_position_findings(by_key, derived)
    for key, row in by_key.items():
        wanted = total if key == "all" else derived.get(key)
        if wanted is not None:
            findings += cell_findings(row, key, wanted)
    return findings


def matrix_findings(lines: list[str], steps: list[Step]) -> list[Finding]:
    first_phase = first_phase_line(lines)
    headers = [n for n, line in enumerate(lines, start=1) if line.strip() == HEADER]
    if not headers or (first_phase is not None and headers[0] > first_phase):
        fix = (
            f"add a table with the header row {HEADER} before the first phase anchor, with one row for each"
            " step and a last row all, as rule 10 of plc-0008-rollout-plan says"
        )
        return [
            Finding(first_phase or 1, "the plan has no status matrix before its first phase", WHY_MATRIX, fix)
        ]
    matrix = read_matrix(lines, headers[0])
    findings: list[Finding] = []
    if len(headers) > 1:
        fix = f"delete this table; the matrix is the one at line {headers[0]}"
        findings.append(Finding(headers[1], "the plan holds a second status matrix", WHY_MATRIX, fix))
    if not matrix.separated:
        fix = f"add the row {SEPARATOR_ROW} under the header row"
        what = "the status matrix has no separator row under its header row"
        findings.append(Finding(matrix.header, what, WHY_MATRIX, fix))
    return findings + row_findings(matrix, steps)


def check_text(text: str) -> Result:
    """Every finding of a plan's text, in the order of its lines, and what was examined."""
    lines = split_lines(text)
    steps, findings = read_steps(lines)
    findings += matrix_findings(lines, steps)
    findings.sort(key=lambda found: found.line)
    return Result(
        tuple(findings),
        len(steps),
        sum(len(step.items) for step in steps),
        derive_total(steps).counts,
    )


def report(result: Result) -> int:
    examined = f"{result.steps} step(s), {result.items} item(s)"
    if result.findings:
        for finding in result.findings:
            print(finding.render())
        print(f"RED: {len(result.findings)} finding(s) — {examined} examined")
        return EXIT_RED
    counts = result.counts
    print(
        f"GREEN: {PLAN}: the status matrix matches its items — {examined}:"
        f" {counts.done} done, {counts.open} open, {counts.waiting} waiting"
    )
    return EXIT_GREEN


def load(path: Path) -> str:
    if not path.is_file():
        raise Broken(f"no {PLAN} at {path.parent.parent} — fix: run the check from a clone of the kit")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(f"{PLAN} is not UTF-8 text ({bad.reason}) — fix: save the file as UTF-8") from bad


def run_check(path: Path) -> int:
    try:
        return report(check_text(load(path)))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 items examined")
        return EXIT_BROKEN


# ---- the self-test: throwaway texts, the plan itself never read -------------------------------------------

ROW_1 = "| [s1](#s1) | First | A | ✅ | 1 | 0 | 0 | 100% |"
ROW_2 = "| [s2](#s2) | Second | B | 🔄 | 1 | 1 | 1 | 50% |"
ROW_3 = "| [s3](#s3) | Third | B | ⏳ | 0 | 1 | 0 | 0% |"
ROW_4 = "| [s4](#s4) | Fourth | B | 💤 | 0 | 0 | 1 | n/a |"
ROW_ALL = "| all | All steps | all | 🔄 | 2 | 2 | 2 | 50% |"
STEP_1 = '1. <a id="s1"></a>✅ Rule made, [the record](records/first.md).'
STEP_2 = '2. <a id="s2"></a>The second step.'
ITEM_1 = '   - <a id="s2-1"></a>**2.1** ✅ Done thing, [the record](records/second.md).'
ITEM_2 = '   - <a id="s2-2"></a>**2.2** ⏳ Open thing.'
ITEM_3 = '   - <a id="s2-3"></a>**2.3** 💤 Waiting thing.'
STEP_3 = '3. <a id="s3"></a>⏳ Open step with no items.'
STEP_4 = '4. <a id="s4"></a>💤 Waiting step with no items.'
TABLE = "\n".join((HEADER, SEPARATOR_ROW, ROW_1, ROW_2, ROW_3, ROW_4, ROW_ALL)) + "\n"
# the lines of the valid plan, by number: the header row at 6, the rows 8 to 12, the steps at 17, 22, 26, 27
BASE = (
    "\n".join(
        (
            "---",
            "id: demo-plan",
            "---",
            "# Plan",
            "",
            TABLE.rstrip("\n"),
            "",
            '<a id="phase-a"></a>',
            "## Phase A",
            "",
            STEP_1,
            "",
            '<a id="phase-b"></a>',
            "## Phase B",
            "",
            STEP_2,
            ITEM_1,
            ITEM_2,
            ITEM_3,
            STEP_3,
            STEP_4,
        )
    )
    + "\n"
)
# a second valid plan: a percent rounded down, items numbered with letters, a step numbered with a letter
LETTERS = f"""---
id: demo-plan
---
# Plan

{HEADER}
{SEPARATOR_ROW}
| [s1](#s1) | Rounded | A | 🔄 | 2 | 1 | 0 | 66% |
| [s2](#s2) | Letters | A | 💤 | 2 | 0 | 2 | 100% |
| [s2a](#s2a) | Added | B | ⏳ | 0 | 1 | 0 | 0% |
| all | All steps | all | 🔄 | 4 | 2 | 2 | 66% |

<a id="phase-a"></a>
## Phase A

1. <a id="s1"></a>The first step.
- <a id="s1-1"></a>**1.1** ✅ One, [a](a.md).
- <a id="s1-2"></a>**1.2** ✅ Two, [b](b.md).
- <a id="s1-3"></a>**1.3** ⏳ Three.
2. <a id="s2"></a>The second step.
   - <a id="s2-1"></a>**2.1** ✅ One, [a](a.md).
   - <a id="s2-1a"></a>**2.1a** 💤 Between.
   - <a id="s2-1b"></a>**2.1b** 💤 Between again.
   - <a id="s2-2"></a>**2.2** ✅ Two, [b](b.md).

<a id="phase-b"></a>
## Phase B

2a. <a id="s2a"></a>The added step.
   - <a id="s2a-1"></a>**2a.1** ⏳ Open.
"""

Want = list[tuple[int, str, str]]  # the line, what and fix of each finding, in the order of the lines


def edit(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"the self-test edits a text that does not hold {old!r}")
    return text.replace(old, new)


def matrix_cases() -> dict[str, tuple[str, Want]]:
    def row(old: str, new: str) -> str:
        return edit(BASE, old, new)

    add = "add the row "
    return {
        "a wrong Done cell is a finding": (
            row(ROW_2, ROW_2.replace("| 1 | 1 | 1 |", "| 2 | 1 | 1 |")),
            [
                (
                    9,
                    "the row of s2 says 2 done, and its items hold 1",
                    "write 1 in the Done cell of the row s2",
                )
            ],
        ),
        "a wrong Open cell is a finding": (
            row(ROW_2, ROW_2.replace("| 1 | 1 | 1 |", "| 1 | 2 | 1 |")),
            [
                (
                    9,
                    "the row of s2 says 2 open, and its items hold 1",
                    "write 1 in the Open cell of the row s2",
                )
            ],
        ),
        "a wrong Waiting cell is a finding": (
            row(ROW_2, ROW_2.replace("| 1 | 1 | 1 |", "| 1 | 1 | 0 |")),
            [
                (
                    9,
                    "the row of s2 says 0 waiting, and its items hold 1",
                    "write 1 in the Waiting cell of the row s2",
                )
            ],
        ),
        "a wrong percent cell is a finding": (
            row(ROW_2, ROW_2.replace("50%", "67%")),
            [
                (
                    9,
                    "the row of s2 says 67% as its percent done, and its items give 50%",
                    "write 50% in the % done cell of the row s2",
                )
            ],
        ),
        "a wrong status cell is a finding": (
            row(ROW_2, ROW_2.replace("🔄", "⏳")),
            [
                (
                    9,
                    "the row of s2 says status ⏳, and its items give 🔄",
                    "write 🔄 in the Status cell of the row s2",
                )
            ],
        ),
        "a wrong phase cell is a finding": (
            row(ROW_2, ROW_2.replace("| B |", "| A |")),
            [
                (
                    9,
                    "the row of s2 says phase A, and the step stands under phase B",
                    "write B in the Phase cell of the row s2",
                )
            ],
        ),
        "a percent of 0% where done + open is 0 is a finding": (
            row(ROW_4, ROW_4.replace("n/a", "0%")),
            [
                (
                    11,
                    "the row of s4 says 0% as its percent done, and its items give n/a",
                    "write n/a in the % done cell of the row s4",
                )
            ],
        ),
        "n/a where done + open is above 0 is a finding": (
            row(ROW_3, ROW_3.replace("0%", "n/a")),
            [
                (
                    10,
                    "the row of s3 says n/a as its percent done, and its items give 0%",
                    "write 0% in the % done cell of the row s3",
                )
            ],
        ),
        "a wrong Done cell of the row all is a finding": (
            row(ROW_ALL, ROW_ALL.replace("| 2 | 2 | 2 |", "| 3 | 2 | 2 |")),
            [
                (
                    12,
                    "the row all says 3 done, and its items hold 2",
                    "write 2 in the Done cell of the row all",
                )
            ],
        ),
        "a phase cell of the row all that is not the word all is a finding": (
            row(ROW_ALL, ROW_ALL.replace("| all | 🔄 |", "| B | 🔄 |")),
            [
                (
                    12,
                    'the Phase cell of the row all reads "B", which is not the word all',
                    "write all in the Phase cell of the row all",
                )
            ],
        ),
        "a cell of the wrong form is a finding": (
            row(ROW_2, ROW_2.replace("| 1 | 1 | 1 |", "| x | 1 | 1 |")),
            [
                (
                    9,
                    'the Done cell of the row of s2 reads "x", which is not a whole number',
                    "write 1 in the Done cell of the row s2",
                )
            ],
        ),
        "a row of seven cells is a finding": (
            row(ROW_3, ROW_3.replace(" 0% |", "")),
            [
                (
                    10,
                    "the row of s3 has 7 cells, and the matrix has 8",
                    "write the row with 8 cells, escaping a | in its title as \\|:"
                    " | [s3](#s3) | <title> | B | ⏳ | 0 | 1 | 0 | 0% |",
                )
            ],
        ),
        "a first cell that is no link is a finding": (
            row(ROW_3, ROW_3.replace("[s3](#s3)", "s3")),
            [
                (
                    10,
                    'the first cell of the row of s3 reads "s3", which is not a link to the step',
                    "write [s3](#s3) in the first cell of the row s3",
                )
            ],
        ),
        "a first cell that names no step is a finding, and its step has no row": (
            row(ROW_3, ROW_3.replace("[s3](#s3)", "Third step")),
            [
                (
                    9,
                    "the matrix has no row for s3",
                    f"{add}| [s3](#s3) | <title> | B | ⏳ | 0 | 1 | 0 | 0% | after the row of s2",
                ),
                (
                    10,
                    'the first cell of this matrix row reads "Third step", which names no step',
                    "write [s<n>](#s<n>) for the step the row sums up,"
                    " or all for the last row, or delete the row",
                ),
            ],
        ),
    }


def row_cases() -> dict[str, tuple[str, Want]]:
    def row(old: str, new: str) -> str:
        return edit(BASE, old, new)

    add = "add the row "
    no_matrix = "the plan has no status matrix before its first phase"
    table_fix = (
        f"add a table with the header row {HEADER} before the first phase anchor, with one row for each step"
        " and a last row all, as rule 10 of plc-0008-rollout-plan says"
    )
    return {
        "a missing row is a finding": (
            row(ROW_3 + "\n", ""),
            [
                (
                    9,
                    "the matrix has no row for s3",
                    f"{add}| [s3](#s3) | <title> | B | ⏳ | 0 | 1 | 0 | 0% | after the row of s2",
                )
            ],
        ),
        "a missing first row is a finding": (
            row(ROW_1 + "\n", ""),
            [
                (
                    6,
                    "the matrix has no row for s1",
                    f"{add}| [s1](#s1) | <title> | A | ✅ | 1 | 0 | 0 | 100% |"
                    " as the first row, under the separator row",
                )
            ],
        ),
        "an extra row is a finding": (
            row(ROW_4, ROW_4 + "\n| [s5](#s5) | Fifth | B | ⏳ | 0 | 1 | 0 | 0% |"),
            [(12, "the matrix has a row for s5, and the plan has no step s5", "delete the row of s5")],
        ),
        "rows out of order are a finding": (
            row(ROW_2 + "\n" + ROW_3, ROW_3 + "\n" + ROW_2),
            [
                (
                    9,
                    "the row of s3 stands where the plan's order puts the row of s2",
                    "move the rows into the plan's order: s1, s2, s3, s4",
                )
            ],
        ),
        "a row twice is a finding": (
            row(ROW_2, ROW_2 + "\n" + ROW_2),
            [(10, "the matrix has two rows for s2", "delete this second row of s2")],
        ),
        "no row all is a finding": (
            row(ROW_ALL + "\n", ""),
            [
                (
                    11,
                    "the matrix has no last row all, the sums of its steps",
                    f"{add}| all | <title> | all | 🔄 | 2 | 2 | 2 | 50% | as the last row",
                )
            ],
        ),
        "the row all above a step row is a finding": (
            row(ROW_4 + "\n" + ROW_ALL, ROW_ALL + "\n" + ROW_4),
            [(11, "the row all stands above the row of s4", "move the row all to the end of the matrix")],
        ),
        "no matrix is a finding": (row(TABLE + "\n", ""), [(6, no_matrix, table_fix)]),
        "a matrix after the first phase line is no matrix before it": (
            edit(row(TABLE + "\n", ""), "## Phase A\n\n", "## Phase A\n\n" + TABLE + "\n"),
            [(6, no_matrix, table_fix)],
        ),
        "a plan with no phase line and no matrix is a finding at its first line": (
            "# Plan\n",
            [(1, no_matrix, table_fix)],
        ),
        "a matrix of no row lacks the row all": (
            f"# Plan\n\n{HEADER}\n{SEPARATOR_ROW}\n",
            [
                (
                    3,
                    "the matrix has no last row all, the sums of its steps",
                    f"{add}| all | <title> | all | ✅ | 0 | 0 | 0 | n/a | as the last row",
                )
            ],
        ),
        "two matrices are a finding": (
            BASE + "\n" + TABLE,
            [
                (
                    29,
                    "the plan holds a second status matrix",
                    "delete this table; the matrix is the one at line 6",
                )
            ],
        ),
        "a matrix with no separator row is a finding": (
            row(SEPARATOR_ROW + "\n", ""),
            [
                (
                    6,
                    "the status matrix has no separator row under its header row",
                    f"add the row {SEPARATOR_ROW} under the header row",
                )
            ],
        ),
    }


def step_cases() -> dict[str, tuple[str, Want]]:
    def edited(old: str, new: str) -> str:
        return edit(BASE, old, new)

    wording = "write one of ✅ ⏳ 💤 and a space"
    id_what = "do not agree with each other and with step 2"
    id_fix = "write the handle **2.2** and the anchor s2-2"
    link_fix = (
        "link its record, or the document or the module its routine change concerns, or, once its record is"
        " deleted, the current-state document that carries its ruling"
    )
    return {
        "a step above the first phase line is a finding": (
            edited('<a id="phase-a"></a>\n', ""),
            [
                (
                    16,
                    "step 1 stands above the first phase anchor",
                    'put the line <a id="phase-<letter>"></a> of its phase above step 1',
                )
            ],
        ),
        "a step that stands twice is a finding": (
            edited(STEP_4, STEP_4 + '\n3. <a id="s3"></a>⏳ Again.'),
            [
                (
                    28,
                    "step s3 stands twice, first at line 26",
                    "give the later step a number of its own, in its line, its anchor and its items",
                )
            ],
        ),
        "an item with no mark is a finding, and its row is left uncompared": (
            edited(ITEM_2, ITEM_2.replace("⏳ ", "")),
            [(24, "item 2.2 opens with no status mark", f"{wording} after **2.2**")],
        ),
        "an item with two marks is a finding": (
            edited(ITEM_2, ITEM_2.replace("⏳ ", "⏳ ✅ ")),
            [(24, "item 2.2 opens with two marks", "keep one of ✅ ⏳ 💤 and delete the other")],
        ),
        "a mark with no space and no text is a finding": (
            edited(ITEM_2, '   - <a id="s2-2"></a>**2.2** ⏳'),
            [
                (
                    24,
                    "item 2.2 has no space and no text after its mark",
                    "write a space and the words of the item after the mark",
                )
            ],
        ),
        "an anchor that does not match its handle is a finding": (
            edited(ITEM_2, ITEM_2.replace("s2-2", "s2-9")),
            [(24, f"the handle 2.2 and the anchor s2-9 of an item {id_what}", id_fix)],
        ),
        "an anchor of another step is a finding": (
            edited(ITEM_2, ITEM_2.replace("s2-2", "s3-2")),
            [(24, f"the handle 2.2 and the anchor s3-2 of an item {id_what}", id_fix)],
        ),
        "a handle of another step is a finding": (
            edited(ITEM_2, ITEM_2.replace("**2.2**", "**3.2**")),
            [(24, f"the handle 3.2 and the anchor s2-2 of an item {id_what}", id_fix)],
        ),
        "a step with items that carries a mark of its own is a finding": (
            edited(STEP_2, STEP_2.replace("</a>", "</a>✅ ")),
            [
                (
                    22,
                    "step 2 has items and opens with a mark of its own",
                    "delete the mark from the line of step 2; its items carry the marks",
                )
            ],
        ),
        "a step with no items that carries no mark is a finding": (
            edited(STEP_3, STEP_3.replace("⏳ ", "")),
            [
                (
                    26,
                    "step 3, which has no items, opens with no status mark",
                    f"{wording} right after the anchor of step 3",
                )
            ],
        ),
        "a done item with no link is a finding": (
            edited(ITEM_1, '   - <a id="s2-1"></a>**2.1** ✅ Done thing.'),
            [(23, "done item 2.1 holds no link", link_fix)],
        ),
        "a done step with no items and no link is a finding": (
            edited(STEP_1, '1. <a id="s1"></a>✅ Rule made.'),
            [(17, "done step 1, which has no items, holds no link", link_fix)],
        ),
        "brackets and an empty target are no link": (
            edited(ITEM_1, '   - <a id="s2-1"></a>**2.1** ✅ Done thing, [the record] and [a]().'),
            [(23, "done item 2.1 holds no link", link_fix)],
        ),
        "a step with no items and a mark but no words is a finding": (
            edited(STEP_3, '3. <a id="s3"></a>⏳ '),
            [
                (
                    26,
                    "step 3, which has no items, has no space and no text after its mark",
                    "write a space and the words of the item after the mark",
                )
            ],
        ),
        "a handle that reads no number is a finding, its number taken from the anchor": (
            edited(ITEM_2, ITEM_2.replace("**2.2**", "**two**")),
            [(24, f"the handle two and the anchor s2-2 of an item {id_what}", id_fix)],
        ),
        "a handle and an anchor that read no number are a finding, the next number is wanted": (
            edited(ITEM_2, ITEM_2.replace("s2-2", "x").replace("**2.2**", "**two**")),
            [(24, f"the handle two and the anchor x of an item {id_what}", id_fix)],
        ),
        "a number with a leading zero is a finding": (
            edited(ITEM_1, ITEM_1.replace("s2-1", "s2-01").replace("2.1", "2.01")),
            [
                (
                    23,
                    f"the handle 2.01 and the anchor s2-01 of an item {id_what}",
                    "write the handle **2.1** and the anchor s2-1",
                )
            ],
        ),
    }


def numbered(first: str, second: str, third: str) -> str:
    """The valid plan with the three items of step 2 numbered as given in their anchors and handles, such
    as "1", "2a" or "5"."""
    text = BASE
    for item, old, new in ((ITEM_1, "1", first), (ITEM_2, "2", second), (ITEM_3, "3", third)):
        renamed = item.replace(f"s2-{old}", f"s2-{new}").replace(f"**2.{old}**", f"**2.{new}**")
        text = edit(text, item, renamed)
    return text


def number_cases() -> dict[str, tuple[str, Want]]:
    unused = "a number once used is not used again"
    end = "a number above the highest of the step"
    between = "for an item between two items, or"
    return {
        "an equal number is a finding": (
            numbered("1", "2", "2"),
            [
                (
                    25,
                    "item 2.2 follows item 2.2, and its number is not above it",
                    f"give it a number above 2.2 in its handle and its anchor: 2.2a {between} {end}"
                    f" for an item at its end; {unused}",
                )
            ],
        ),
        "a lower number is a finding, and the item after it is judged by it alone": (
            numbered("5", "2", "3"),
            [
                (
                    24,
                    "item 2.2 follows item 2.5, and its number is not above it",
                    f"give it a number above 2.5 in its handle and its anchor: 2.5a {between} {end}"
                    f" for an item at its end; {unused}",
                )
            ],
        ),
        "a letter before its plain number is a finding": (
            numbered("1", "2a", "2"),
            [
                (
                    25,
                    "item 2.2 follows item 2.2a, and its number is not above it",
                    f"give it a number above 2.2a in its handle and its anchor: 2.2b {between} {end}"
                    f" for an item at its end; {unused}",
                )
            ],
        ),
        "a letter b before a is a finding": (
            numbered("1", "2b", "2a"),
            [
                (
                    25,
                    "item 2.2a follows item 2.2b, and its number is not above it",
                    f"give it a number above 2.2b in its handle and its anchor: 2.2c {between} {end}"
                    f" for an item at its end; {unused}",
                )
            ],
        ),
        "after the letter z no letter is offered": (
            numbered("1", "2z", "2z"),
            [
                (
                    25,
                    "item 2.2z follows item 2.2z, and its number is not above it",
                    f"give it a number above 2.2z in its handle and its anchor: {end}; {unused}",
                )
            ],
        ),
        "a first item numbered 0 is a finding": (
            numbered("0", "2", "3"),
            [
                (
                    23,
                    "item 2.0 opens step 2, and its number is below 1",
                    "give it a number from 1 up in its handle and its anchor;"
                    " the items of a step are numbered from 1",
                )
            ],
        ),
    }


def list_cases() -> dict[str, tuple[str, Want]]:
    def edited(old: str, new: str) -> str:
        return edit(BASE, old, new)

    what = "this list line of step 2 does not read as an item"
    fix = (
        'write it as an item, - <a id="s2-<m>"></a>**2.<m>** <mark> <text>,'
        " with an <m> above every number before it in the step, or join its words to the sentence above"
    )
    return {
        "a list line that is no item is a finding": (
            edited(ITEM_3, ITEM_3 + "\n   - A plain note."),
            [(26, what, fix)],
        ),
        "a * bullet is a finding, though it reads as an item otherwise": (
            edited(ITEM_3, ITEM_3.replace("   - ", "   * ")),
            [(25, what, fix)],
        ),
        "a + bullet is a finding": (edited(ITEM_3, ITEM_3 + "\n   + A plain note."), [(26, what, fix)]),
        "an indented numbered line is a finding": (
            edited(ITEM_3, ITEM_3 + "\n   1. A plain note."),
            [(26, what, fix)],
        ),
        "a numbered line with a parenthesis is a finding": (
            edited(ITEM_3, ITEM_3 + "\n   2) A plain note."),
            [(26, what, fix)],
        ),
        "a list line that stands at the left edge is a finding": (
            edited(ITEM_3, ITEM_3 + "\n* A plain note."),
            [(26, what, fix)],
        ),
        "a list line after a closed fenced block is read again": (
            edited(ITEM_3, ITEM_3 + "\n```\n- inside\n```\n- A plain note."),
            [(29, what, fix)],
        ),
        "a fence line with backticks in its words opens no block": (
            edited(ITEM_3, ITEM_3 + "\n```not a fence``` here\n- A plain note."),
            [(27, what, fix)],
        ),
        "a fence line indented four spaces opens no block": (
            edited(ITEM_3, ITEM_3 + "\n    ```\n- A plain note."),
            [(27, what, fix)],
        ),
        "a shorter fence line does not close a longer fence": (
            edited(ITEM_3, ITEM_3 + "\n````\n```\n- inside\n```\n````\n- A plain note."),
            [(31, what, fix)],
        ),
    }


def fenced(*lines: str) -> str:
    """The valid plan with a fenced block of the given lines under the items of step 2."""
    return edit(BASE, ITEM_3, "\n".join((ITEM_3, *lines)))


def green_cases() -> dict[str, str]:
    example = '   - <a id="s2-4"></a>**2.4** ✅ An example item, [the record](records/third.md).'
    return {
        "a valid plan is green": BASE,
        "a percent is rounded down, items take letters, a step takes a letter: green": LETTERS,
        "a gap in the numbers of a step is green": numbered("1", "3", "5"),
        "a step that starts at item 2 is green": numbered("2", "3", "4"),
        "a first item that carries a letter, its plain number gone, is green": numbered("1a", "2", "3"),
        "a lettered item after its plain number is green": numbered("1", "2", "2a"),
        "a letter z between two numbers is green": numbered("1", "2z", "3"),
        "list lines in a backtick fence are no items: green": fenced(
            "```", "- A plain note.", "1. Another.", "```"
        ),
        "an item line in a backtick fence is not counted: green": fenced("```text", example, "```"),
        "a tilde fence indented three spaces holds no items: green": fenced(
            "   ~~~", "- A plain note.", "   ~~~"
        ),
        "a longer fence holds what a shorter one shows: green": fenced("````", "```", example, "```", "````"),
        "a step line and a phase line in a fence are none: green": fenced(
            "```", '5. <a id="s5"></a>⏳ Not a step.', '<a id="phase-c"></a>', "```"
        ),
        "an escaped bar stays inside its cell: green": edit(
            BASE, ROW_1, ROW_1.replace("First", "First \\| A")
        ),
        "a plan with CRLF line ends reads the same: green": BASE.replace("\n", "\r\n"),
        "a separator row with alignment colons is a separator row: green": edit(
            BASE, SEPARATOR_ROW, "| :--- | :---: | ---: | --- | --- | --- | --- | --- |"
        ),
        "a plan of no step and the row all alone is green": (
            f"# Plan\n\n{HEADER}\n{SEPARATOR_ROW}\n| all | All steps | all | ✅ | 0 | 0 | 0 | n/a |\n"
        ),
    }


def text_outcomes() -> list[tuple[str, bool, str]]:
    outcomes: list[tuple[str, bool, str]] = []
    for name, text in green_cases().items():
        got = [(f.line, f.what, f.fix) for f in check_text(text).findings]
        outcomes.append((name, got == [], f"got {got}"))
    for cases in (matrix_cases(), row_cases(), step_cases(), number_cases(), list_cases()):
        for name, (text, wanted) in cases.items():
            got = [(f.line, f.what, f.fix) for f in check_text(text).findings]
            outcomes.append((name, got == wanted, f"got {got}"))
    return outcomes


def capture(call: Callable[[], int]) -> tuple[int, list[str]]:
    """Run a call with stdout and stderr caught: its exit code and the lines it printed."""
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(io.StringIO()):
        code = call()
    return code, printed.getvalue().splitlines()


def red_outcome(name: str, text: str, wanted: list[str]) -> tuple[str, bool, str]:
    """The report of a plan's text is exit 2 and the lines wanted, typed by hand."""
    code, printed = capture(lambda: report(check_text(text)))
    return name, code == EXIT_RED and printed == wanted, f"got {printed}"


def report_outcomes() -> list[tuple[str, bool, str]]:
    # typed by hand: a message function cannot check itself
    red_lines = [
        "RED: docs/rollout-plan.md:9: the row of s2 says 2 done, and its items hold 1",
        "  why: the matrix is the plan's summary, and a count typed by hand drifts from its items",
        "  fix: write 1 in the Done cell of the row s2",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    green_line = (
        "GREEN: docs/rollout-plan.md: the status matrix matches its items — 4 step(s), 6 item(s):"
        " 2 done, 2 open, 2 waiting"
    )
    link_lines = [
        "RED: docs/rollout-plan.md:23: done item 2.1 holds no link",
        "  why: a done item's link is its proof, the record or the document its change concerns",
        "  fix: link its record, or the document or the module its routine change concerns, or, once its"
        " record is deleted, the current-state document that carries its ruling",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    order_lines = [
        "RED: docs/rollout-plan.md:25: item 2.2 follows item 2.2, and its number is not above it",
        "  why: an item keeps its number for good, and rule 4 of plc-0008-rollout-plan numbers the items of"
        " a step in ascending order from 1",
        "  fix: give it a number above 2.2 in its handle and its anchor: 2.2a for an item between two items,"
        " or a number above the highest of the step for an item at its end; a number once used is not used"
        " again",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    red_text = edit(BASE, ROW_2, ROW_2.replace("| 1 | 1 | 1 |", "| 2 | 1 | 1 |"))
    link_text = edit(BASE, ITEM_1, '   - <a id="s2-1"></a>**2.1** ✅ Done thing.')
    green_code, green_printed = capture(lambda: report(check_text(BASE)))
    return [
        red_outcome("the report of one finding is its literal text, exit 2", red_text, red_lines),
        red_outcome(
            "the report of a done item with no link is its literal text, exit 2", link_text, link_lines
        ),
        red_outcome(
            "the report of a number that is not above the one before is its literal text, exit 2",
            numbered("1", "2", "2"),
            order_lines,
        ),
        (
            "the report of a valid plan is its literal line, exit 0",
            green_code == EXIT_GREEN and green_printed == [green_line],
            f"got {green_printed}",
        ),
    ]


def broken_outcomes() -> list[tuple[str, bool, str]]:
    closing = "BROKEN: the check could not run — 0 items examined"
    with tempfile.TemporaryDirectory() as tmp:
        kit = Path(tmp)
        plan = kit / PLAN
        absent_code, absent_printed = capture(lambda: run_check(plan))
        plan.parent.mkdir()
        plan.write_bytes(b"\xff\xfe")
        utf8_code, utf8_printed = capture(lambda: run_check(plan))
    misuse_code, misuse_printed = capture(lambda: main(["--bogus"]))
    absent = [f"BROKEN: no {PLAN} at {kit} — fix: run the check from a clone of the kit", closing]
    utf8 = [f"BROKEN: {PLAN} is not UTF-8 text (invalid start byte) — fix: save the file as UTF-8", closing]
    misuse = ["BROKEN: misinvocation — fix: run with no arguments, or with --self-test", closing]
    return [
        (
            "an absent plan is a teaching BROKEN line, exit 1",
            absent_code == EXIT_BROKEN and absent_printed == absent,
            f"got {absent_printed}",
        ),
        (
            "a plan that is not UTF-8 is a teaching BROKEN line, exit 1",
            utf8_code == EXIT_BROKEN and utf8_printed == utf8,
            f"got {utf8_printed}",
        ),
        (
            "a misinvocation is a teaching BROKEN line, exit 1",
            misuse_code == EXIT_BROKEN and misuse_printed == misuse,
            f"got {misuse_printed}",
        ),
    ]


def self_test() -> int:
    """Red→green on throwaway texts: a valid plan is green, and each hold of the docstring is red alone; the
    report of one finding is its literal text, exit 2; an absent plan, a plan that is not UTF-8 and a
    misinvocation are each a teaching BROKEN line, exit 1."""
    outcomes = [*text_outcomes(), *report_outcomes(), *broken_outcomes()]
    failed = 0
    for name, ok, detail in outcomes:
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        {detail}")
    print(f"{len(outcomes) - failed}/{len(outcomes)} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-rollout-status", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 items examined")
        return EXIT_BROKEN
    return self_test() if args.self_test else run_check(KIT / PLAN)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
