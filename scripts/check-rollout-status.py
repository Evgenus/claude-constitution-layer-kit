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
     The header row and the first phase line are looked for outside the fenced blocks (7), as the steps
     and the items are: a fenced header row is no matrix, and a fenced phase anchor is no phase.
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
     itself excepted. An item is one line, its link on that line: a non-blank line right under an item
     line, itself no list line, no step line, no phase line and no fence line, is a finding, and so is each
     such line right under that one, since the mark, the words and the link of an item are read together;
     the fix is to join the line to the one above, or to put a blank line above it where it is no part of
     the item, as a heading, a comment or a quote under an item is none. A line after a blank line or a
     fenced block is a paragraph of the step and no item. An item reads
     `- <a id="s<n>-<m>"></a>**<n>.<m>** <mark> <text>`: <n> the number of its step, <m> its number in
     the step, anchor and handle agreeing with each other and with the step, one mark of ✅ ⏳ 💤, a space
     and words. Where anchor and handle disagree the number is the anchor's, which other documents cite,
     and the fix rewrites the handle; the handle's number is read only where the anchor reads none. A
     list line in any other form is a finding. The numbers ascend, gaps allowed: the first <m> is any
     whole number from 1, with a letter or none, and each next item is numbered above the one before it
     (P), a letter standing after the same number without one and a before b. A number that is not above
     P is a finding, since a number once used is not used again; a leading zero is a finding. A number is
     never offered from the gap between P and the next item that reads a number (N), since a whole number
     there is one a removed item held: where an N stands, the offer is the letter after P's, `a` where P
     has none; where none stands, the next whole number above P. The fix names for that item a number
     above P and below N, both bounds and that example, so that no other item turns red. Where none fits
     — N not above the letter after P, N of P's whole number, the letters between them having been given
     in order, or P ending in `z` — it says so and names item P, the one before, as the one that may be
     out of place. A first item has no P, and 1 bounds it from below: where an N stands, no number fits,
     and the fix says so, names N, the next one numbered, with the reason that applies — below item 1 the
     items are numbered from 1, below a higher one a step that starts above 1 lost its item 1 and a
     number once used is not used again — and says that an item added before the first stands after it
     instead; where none stands, it offers 1. The same holds for the number a list
     line that is no item is told to take, which has the bounds alone, and for the number offered to an
     item whose handle and anchor read none. An item that is the first of its step to read a number is
     named so, whatever list line stands before it.
  5. The steps' own marks. A step with items opens its own text, after its anchor, with no mark. A step
     with no items is its own one item: its text opens with one mark, a space and words, and it is one
     line, as an item is, with the finding and the fix of 4 for the line right under it that runs on. A
     line right under the line of a step with items is the step's own text, and no finding.
  6. The links. A done item holds an inline Markdown link, `[text](target)`, on its own line, and so does
     a done step with no items. The link is looked for in the item's line and the lines that run on under
     it, joined by a space, and may hold spaces right after its `(`, so that a link split across the
     lines, as CommonMark reads it, gives the finding of 4 alone; a split between `]` and `(` is no link in
     CommonMark, and there the finding of no link stands beside it. The same for a done step with no
     items.
  7. The fenced blocks, for every scan above: the steps, the phase lines, the items, and the header row and
     the first phase line of the matrix. A fence is a line whose text, after any spaces, starts with three
     or more backticks or tildes, since inside a list item a fence stands four spaces in or more; a
     backtick fence whose words hold a backtick opens nothing, being inline code. A fence closes only on a
     line of the same character, as long or longer, with no words after it. What a block holds is no list
     line, no step line, no phase line, no header row and no line that runs on under an item. A block that
     opens and never closes runs to the end of the file and hides every line after it, so it is a finding
     at its opening line; while one stands, the rows of the matrix are not read against the steps at all,
     and the matrix's absence or place is not reported, since the lines below the block are not read.

What it leaves to review: whether a mark matches the words of its item, whether a link is the proof of its
item, a done item's words, a row's title, and every other content of the plan; the style, the language and
the length of the plan are held by the modules that hold them. A known limit: a thematic break written
`* * *` under a step still reads as a list line, and is a finding.

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
FENCE = re.compile(
    r"^\s*(`{3,}|~{3,})(.*)$"
)  # at any indent: inside a list item a fence stands four in or more
ITEM_FORM = re.compile(r'^\s*- <a id="([^"]*)"></a>\*\*([^*]*)\*\* (.*)$')
HANDLE = re.compile(r"(\d+[a-z]?)\.(\d+[a-z]?)")
ANCHOR = re.compile(r"s(\d+[a-z]?)-(\d+[a-z]?)")
NUMBER = re.compile(r"(\d+)([a-z]?)")
LINK = re.compile(r"\[[^\]]+\]\(\s*[^)\s][^)]*\)")
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
WHY_ONE_LINE = "an item is one line, so its mark, its words and its link are read together"
WHY_PHASE = "each step stands in the phase above it, and its row names that phase"
WHY_STEPS = "a step is cited by its number, and its row is found by it"
WHY_FENCE = "every line after it is read as code, so the steps and items below are not checked"
RUN_FIX = "join this line to the line above, or put a blank line above it where it is no part of the item"
BEFORE_FIRST = "an item added before the first stands after it instead"
FROM_ONE = "the items of a step are numbered from 1"
ON_STEP = -1  # the index a line gets that runs on under the line of a step, as a list line gets its own


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


Number = tuple[int, str]  # an item's <m>: the whole number and its letter or none, ordered as written


@dataclass
class Span:
    """The lines of one step: its own line, the list lines under it, and the lines that run on under them."""

    number: str
    line: int
    phase: str
    text: str
    lines: list[tuple[int, str]]
    tails: list[tuple[int, int, str]]  # the index of a list line or ON_STEP, and the number and text under it


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


def fence_opening(line: str) -> str:
    """The fence a line opens, three or more ` or ~ after any spaces, or an empty string where it opens none.
    The words after a ` fence hold no `, or the line is inline code and no fence."""
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


def fence_after(fence: str, line: str) -> str:
    """The fence still open after a line, given the one open before it; an empty string where none is."""
    if fence:
        return "" if closes_fence(fence, line) else fence
    return fence_opening(line)


def unfenced(lines: list[str]) -> Iterator[tuple[int, str]]:
    """The lines outside the fenced blocks, each with its number from 1; the fence lines and what they
    enclose are left out. A block left open runs to the end of the file."""
    fence = ""
    for number, line in enumerate(lines, start=1):
        outside = not fence
        fence = fence_after(fence, line)
        if outside and not fence:
            yield number, line


def unclosed_fence(lines: list[str]) -> int | None:
    """The line where a fenced block opens and never closes, or None where every block closes."""
    fence, opened = "", 0
    for number, line in enumerate(lines, start=1):
        opened = opened if fence else number
        fence = fence_after(fence, line)
    return opened if fence else None


def first_phase_line(lines: list[str]) -> int | None:
    return next((n for n, line in unfenced(lines) if PHASE_LINE.match(line)), None)


def split_steps(lines: list[str]) -> list[Span]:
    """The steps of the plan, each with the list lines of its span: from its line to the next step line, the
    next phase line or the end of the file; a fenced block holds none. A non-blank line right under a list
    line or a step line, with no fence line between, that is no list line, step line or phase line runs on
    under it, and so does each such line right under that one."""
    spans: list[Span] = []
    phase = ""
    current: Span | None = None
    from_item: int | None = None  # the index of the list line, or ON_STEP, the line above runs on from
    last = 0
    for number, line in unfenced(lines):
        runs_on = from_item if number == last + 1 else None
        last, from_item = number, None
        opened, step = PHASE_LINE.match(line), STEP_LINE.match(line)
        if opened:
            phase, current = opened.group(1).upper(), None
        elif step:
            current = Span(step.group(1), number, phase, step.group(2), [], [])
            spans.append(current)
            from_item = ON_STEP
        elif current is not None and LIST_LINE.match(line):
            current.lines.append((number, line))
            from_item = len(current.lines) - 1
        elif current is not None and runs_on is not None and line.strip():
            current.tails.append((runs_on, number, line))
            from_item = runs_on
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


def read_item(line_no: int, line: str, tail: str) -> tuple[Item, list[Finding]]:
    """An item line with its findings of mark and link. The link is looked for in the line and `tail`, the
    lines that run on under it, joined: a link split across them gives the finding of those lines alone,
    until they are joined."""
    shaped = ITEM_FORM.match(line.rstrip())
    if shaped is None:
        return Item(line_no, False, "", "", None), []
    anchor, handle, rest = shaped.groups()
    name = f"item {handle}"
    mark, findings = read_mark(name, f"after **{handle}**", line_no, rest)
    if mark is Mark.DONE and LINK.search(f"{rest} {tail}") is None:
        findings.append(link_finding(name, line_no))
    return Item(line_no, True, anchor, handle, mark), findings


def tail_of(span: Span, at: int) -> str:
    """The words of the lines that run on under the list line of index `at`, or under the line of the step
    for ON_STEP, joined."""
    return " ".join(text for index, _, text in span.tails if index == at)


def run_finding(subject: str, first: int, line: int) -> Finding:
    """A line that runs on under `subject`, a line at `first`: an item, a list line that is no item, or a
    step with no items."""
    words = "second" if line == first + 1 else "further"
    return Finding(line, f"this is a {words} line of {subject}", WHY_ONE_LINE, RUN_FIX)


def run_findings(span: Span, items: list[Item]) -> list[Finding]:
    """The lines that run on under the list lines of a step with items; those right under the step's own
    line are its text, and no finding."""
    findings: list[Finding] = []
    for index, line, _ in span.tails:
        if index != ON_STEP:
            item = items[index]
            subject = f"item {item.handle}" if item.shaped else f"the list line at line {item.line}"
            findings.append(run_finding(subject, item.line, line))
    return findings


def read_solo(span: Span) -> tuple[Item, list[Finding]]:
    """A step with no items is its own one item, its mark right after its anchor, and one line: the lines
    that run on under it are findings, and its link is looked for in them as in an item's."""
    name = f"step {span.number}, which has no items,"
    after = f"right after the anchor of step {span.number}"
    mark, findings = read_mark(name, after, span.line, span.text)
    if mark is Mark.DONE and LINK.search(f"{span.text} {tail_of(span, ON_STEP)}") is None:
        findings.append(link_finding(name, span.line))
    subject = f"step {span.number}, which has no items"
    findings += [run_finding(subject, span.line, line) for _, line, _ in span.tails]
    return Item(span.line, True, "", name, mark), findings


def parse_number(text: str) -> Number | None:
    parts = NUMBER.fullmatch(text)
    return None if parts is None else (int(parts.group(1)), parts.group(2))


def render_number(number: Number) -> str:
    return f"{number[0]}{number[1]}"


def after(previous: Number | None, bound: Number | None) -> Number | None:
    """A number above the one before (P) and below the bound (N), to write where an item reads none and in
    a fix. A whole number in the gap between P and N is never offered, since a removed item held it and a
    number once used is not used again. Where an N stands: the letter after P's, `a` where P has none, if
    it is below N; None where it is not, where N has P's whole number, after the letter z, and for a first
    item, which has no P. Where no N stands: the next whole number above P, and 1 for a first item."""
    if bound is None:
        return (1, "") if previous is None else (previous[0] + 1, "")
    if previous is None or previous[1] == "z" or bound[0] == previous[0]:
        return None
    count, letter = previous
    successor = (count, chr(ord(letter) + 1) if letter else "a")
    return successor if successor < bound else None


def rises(previous: Number | None, own: Number) -> bool:
    """Whether an item's number may follow the one before: the first is any whole number from 1, each next
    is above the one before, a letter after the same number without one and a before b."""
    return own[0] >= 1 if previous is None else own > previous


def own_number(item: Item) -> Number | None:
    """The number an item claims: its anchor's <m>, which other documents cite, else its handle's."""
    for pattern, text in ((ANCHOR, item.anchor), (HANDLE, item.handle)):
        parts = pattern.fullmatch(text)
        if parts is not None:
            return parse_number(parts.group(2))
    return None


def range_words(number: str, previous: Number | None, bound: Number | None) -> str:
    """Where a number may stand: from 1 up or above the one before, and below the bound where there is one."""
    low = "from 1 up" if previous is None else f"above {number}.{render_number(previous)}"
    return low if bound is None else f"{low} and below {number}.{render_number(bound)}"


def no_room(number: str, previous: Number | None, bound: Number | None, tail: str = "") -> str | None:
    """The clause that says no number fits between the one before and the bound; None where a number fits.
    Before a first item it names the bound, the next one numbered, and says where an item added before the
    first stands. After an item it names that one as the one that may be out of place, and `tail`, if any,
    says what to do about it, after a colon."""
    if bound is None or after(previous, bound) is not None:
        return None
    if previous is None:
        reason = FROM_ONE if bound == (1, "") else "a number once used is not used again"
        return (
            f"no number fits before item {number}.{render_number(bound)}, the next one numbered, since"
            f" {reason}, and {BEFORE_FIRST}"
        )
    culprit = f"item {number}.{render_number(previous)}, the one before,"
    clause = f"no number fits {range_words(number, previous, bound)}; {culprit} may be the one out of place"
    return f"{clause}: {tail}" if tail else clause


def example(number: str, previous: Number | None, bound: Number | None) -> str:
    offered = after(previous, bound)
    return "" if offered is None else f", such as {number}.{render_number(offered)}"


def order_finding(number: str, item: Item, previous: Number | None, bound: Number | None) -> Finding:
    """An item whose number is not above the one before. The fix changes this item alone, to a number above
    the one before and below the next one numbered, so that no other item turns red; where none fits, it
    says so and names the item before as the one out of place, or, for a first item, the next one numbered,
    after which an item added before the first stands."""
    if previous is None:
        what = (
            f"item {item.handle} is the first item of step {number} that reads a number, and its number is"
            " below 1"
        )
        reason = "the items of a step are numbered from 1"
    else:
        what = (
            f"item {item.handle} follows item {number}.{render_number(previous)}, and its number is not"
            " above it"
        )
        reason = "a number once used is not used again"
    room = no_room(
        number, previous, bound, "renumber it in its handle and its anchor so that the numbers ascend"
    )
    if room is None:
        where = range_words(number, previous, bound)
        room = f"give it a number {where} in its handle and its anchor{example(number, previous, bound)}"
    return Finding(item.line, what, WHY_NUMBER, f"{room}; {reason}")


def id_finding(number: str, item: Item, current: Number | None, room: str | None) -> Finding | None:
    """The handle and the anchor against the step and the number the item claims, which is the anchor's;
    `current` is None where an item reads no number and none fits, and `room` says so, with what to do."""
    if current is None:
        fix = room or "no number fits"
    else:
        handle = f"{number}.{render_number(current)}"
        anchor = f"s{number}-{render_number(current)}"
        if (item.handle, item.anchor) == (handle, anchor):
            return None
        fix = f"write the handle **{handle}** and the anchor {anchor}"
    what = (
        f"the handle {item.handle} and the anchor {item.anchor} of an item do not agree with each other"
        f" and with step {number}"
    )
    return Finding(item.line, what, WHY_ID, fix)


def list_finding(number: str, line: int, previous: Number | None, bound: Number | None) -> Finding:
    shape = f'- <a id="s{number}-<m>"></a>**{number}.<m>** <mark> <text>'
    room = no_room(number, previous, bound)
    if room is None:
        where = range_words(number, previous, bound)
        fix = f"write it as an item, {shape}, with an <m> {where}, or join its words to the sentence above"
    elif previous is None:
        fix = f"join its words to the sentence above, or write it as an item after the first one: {room}"
    else:
        fix = f"join its words to the sentence above, or renumber first and then write it as an item: {room}"
    return Finding(line, f"this list line of step {number} does not read as an item", WHY_LIST, fix)


def upper_bounds(owns: list[Number | None]) -> list[Number | None]:
    """For each item, the number the nearest later item claims; None where no later item claims one."""
    bounds: list[Number | None] = []
    nearest: Number | None = None
    for own in reversed(owns):
        bounds.append(nearest)
        nearest = own or nearest
    return bounds[::-1]


def number_findings(number: str, items: list[Item]) -> list[Finding]:
    """The handle and anchor of each item against its step, and its number against the one before and the
    next one numbered: a fix to one item never turns another red."""
    findings: list[Finding] = []
    owns = [own_number(item) if item.shaped else None for item in items]
    previous: Number | None = None
    for item, own, bound in zip(items, owns, upper_bounds(owns), strict=True):
        if not item.shaped:
            findings.append(list_finding(number, item.line, previous, bound))
            continue
        if own is not None and not rises(previous, own):
            findings.append(order_finding(number, item, previous, bound))
        current = own if own is not None else after(previous, bound)
        room = no_room(
            number, previous, bound, "renumber it in its handle and its anchor, then number this item"
        )
        misplaced = id_finding(number, item, current, room)
        if misplaced is not None:
            findings.append(misplaced)
        previous = previous if current is None else current
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
    for index, (line_no, line) in enumerate(span.lines):
        item, found = read_item(line_no, line, tail_of(span, index))
        items.append(item)
        findings += found
    findings += run_findings(span, items)
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


def row_findings(matrix: Matrix, steps: list[Step], unread: bool) -> list[Finding]:
    """The findings of the rows. Where `unread` is true, a fenced block left open hides the steps below it,
    and the rows are not read against the steps at all."""
    derived = {step.key: derive(step) for step in steps}
    total = derive_total(steps)
    by_key, findings = index_rows(matrix.rows)
    if unread:  # the steps an open block hides are not read, so no row, count or sum can be held
        return findings
    findings += missing_findings(matrix, derived, total, by_key)
    findings += extra_findings(by_key, derived)
    findings += order_findings(by_key, derived)
    findings += all_position_findings(by_key, derived)
    for key, row in by_key.items():
        wanted = total if key == "all" else derived.get(key)
        if wanted is not None:
            findings += cell_findings(row, key, wanted)
    return findings


def matrix_findings(lines: list[str], steps: list[Step], unread: bool) -> list[Finding]:
    first_phase = first_phase_line(lines)
    headers = [n for n, line in unfenced(lines) if line.strip() == HEADER]
    if not headers or (first_phase is not None and headers[0] > first_phase):
        if unread:  # an open block above may hide the matrix; its own finding comes first
            return []
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
    return findings + row_findings(matrix, steps, unread)


def fence_finding(line: int) -> Finding:
    return Finding(
        line,
        "this fenced block never closes",
        WHY_FENCE,
        "close it with a line of the same fence, with nothing after it, where its code ends",
    )


def check_text(text: str) -> Result:
    """Every finding of a plan's text, in the order of its lines, and what was examined."""
    lines = split_lines(text)
    steps, findings = read_steps(lines)
    unclosed = unclosed_fence(lines)
    if unclosed is not None:
        findings.append(fence_finding(unclosed))
    findings += matrix_findings(lines, steps, unclosed is not None)
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
        "a matrix in a fenced block is no matrix": (
            edit(BASE, TABLE.rstrip("\n"), "```\n" + TABLE + "```"),
            [(16, no_matrix, table_fix)],
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
    nameless = unnumbered(ITEM_2, "2", "x")
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
        "a handle that does not match its anchor is a finding, the fix rewrites the handle": (
            edited(ITEM_2, ITEM_2.replace("**2.2**", "**2.9**")),
            [(24, f"the handle 2.9 and the anchor s2-2 of an item {id_what}", id_fix)],
        ),
        "an anchor's number is the item's, though it breaks the order after it": (
            edited(ITEM_2, ITEM_2.replace("s2-2", "s2-9")),
            [
                (
                    24,
                    f"the handle 2.2 and the anchor s2-9 of an item {id_what}",
                    "write the handle **2.9** and the anchor s2-9",
                ),
                (
                    25,
                    "item 2.3 follows item 2.9, and its number is not above it",
                    "give it a number above 2.9 in its handle and its anchor, such as 2.10;"
                    " a number once used is not used again",
                ),
            ],
        ),
        "an anchor that reads no number gives way to the handle's": (
            edited(ITEM_2, ITEM_2.replace("s2-2", "x").replace("**2.2**", "**2.2a**")),
            [
                (
                    24,
                    f"the handle 2.2a and the anchor x of an item {id_what}",
                    "write the handle **2.2a** and the anchor s2-2a",
                )
            ],
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
        "a handle and an anchor that read no number are a finding, the letter after the one before": (
            edited(ITEM_2, nameless),
            [
                (
                    24,
                    f"the handle two and the anchor x of an item {id_what}",
                    "write the handle **2.1a** and the anchor s2-1a",
                )
            ],
        ),
        "an item that reads no number at the end of its step is offered the next whole number": (
            edited(ITEM_3, unnumbered(ITEM_3, "3", "z")),
            [
                (
                    25,
                    f"the handle two and the anchor z of an item {id_what}",
                    "write the handle **2.3** and the anchor s2-3",
                )
            ],
        ),
        "items that read no number are numbered from 1 up, each above the one before": (
            edit(
                edit(edited(ITEM_1, unnumbered(ITEM_1, "1", "y")), ITEM_2, nameless),
                ITEM_3,
                unnumbered(ITEM_3, "3", "z"),
            ),
            [
                (
                    23,
                    f"the handle two and the anchor y of an item {id_what}",
                    "write the handle **2.1** and the anchor s2-1",
                ),
                (
                    24,
                    f"the handle two and the anchor x of an item {id_what}",
                    "write the handle **2.2** and the anchor s2-2",
                ),
                (
                    25,
                    f"the handle two and the anchor z of an item {id_what}",
                    "write the handle **2.3** and the anchor s2-3",
                ),
            ],
        ),
        "an item that reads no number before the first item that reads one is told no number fits": (
            edited(ITEM_1, unnumbered(ITEM_1, "1", "y")),
            [
                (
                    23,
                    f"the handle two and the anchor y of an item {id_what}",
                    "no number fits before item 2.2, the next one numbered, since a number once used is not"
                    " used again, and an item added before the first stands after it instead",
                )
            ],
        ),
        "an item that reads no number is offered one below the next item's": (
            edit(edited(ITEM_3, renumbered(ITEM_3, "3", "2")), ITEM_2, nameless),
            [
                (
                    24,
                    f"the handle two and the anchor x of an item {id_what}",
                    "write the handle **2.1a** and the anchor s2-1a",
                )
            ],
        ),
        "an item that reads no number, where none fits, is told so": (
            edit(edited(ITEM_3, renumbered(ITEM_3, "3", "1a")), ITEM_2, nameless),
            [
                (
                    24,
                    f"the handle two and the anchor x of an item {id_what}",
                    "no number fits above 2.1 and below 2.1a; item 2.1, the one before, may be the one out of"
                    " place: renumber it in its handle and its anchor, then number this item",
                )
            ],
        ),
        "an item that reads no number, where none fits, leaves the item before as the one to beat": (
            edit(edited(ITEM_3, renumbered(ITEM_3, "3", "1")), ITEM_2, nameless),
            [
                (
                    24,
                    f"the handle two and the anchor x of an item {id_what}",
                    "no number fits above 2.1 and below 2.1; item 2.1, the one before, may be the one out of"
                    " place: renumber it in its handle and its anchor, then number this item",
                ),
                (
                    25,
                    "item 2.1 follows item 2.1, and its number is not above it",
                    "give it a number above 2.1 in its handle and its anchor, such as 2.2;"
                    " a number once used is not used again",
                ),
            ],
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


def renumbered(item: str, old: str, new: str) -> str:
    """An item line of step 2 with its number in the anchor and the handle changed from <old> to <new>."""
    return item.replace(f"s2-{old}", f"s2-{new}").replace(f"**2.{old}**", f"**2.{new}**")


def first_room(bound: str) -> str:
    """The clause for a number wanted before the item numbered <bound>, the first of its step to read one:
    below 2.1 the items are numbered from 1, below any other a number once used is not used again."""
    reason = (
        "the items of a step are numbered from 1"
        if bound == "2.1"
        else "a number once used is not used again"
    )
    return (
        f"no number fits before item {bound}, the next one numbered, since {reason}, and an item added before"
        " the first stands after it instead"
    )


def unnumbered(item: str, old: str, anchor: str) -> str:
    """An item line of step 2 whose anchor is <anchor> and whose handle is **two**: both read no number."""
    return item.replace(f"s2-{old}", anchor).replace(f"**2.{old}**", "**two**")


def numbered(first: str, second: str, third: str) -> str:
    """The valid plan with the three items of step 2 numbered as given in their anchors and handles, such
    as "1", "2a" or "5"."""
    text = BASE
    for item, old, new in ((ITEM_1, "1", first), (ITEM_2, "2", second), (ITEM_3, "3", third)):
        text = edit(text, item, renumbered(item, old, new))
    return text


def number_cases() -> dict[str, tuple[str, Want]]:
    unused = "a number once used is not used again"
    ascend = "renumber it in its handle and its anchor so that the numbers ascend"
    from_one = "the items of a step are numbered from 1"
    first_what = "is the first item of step 2 that reads a number, and its number is below 1"
    return {
        "an equal number is a finding, the last item has no upper bound": (
            numbered("1", "2", "2"),
            [
                (
                    25,
                    "item 2.2 follows item 2.2, and its number is not above it",
                    f"give it a number above 2.2 in its handle and its anchor, such as 2.3; {unused}",
                )
            ],
        ),
        "a lower number is a finding, and the item after it is judged by it alone": (
            numbered("5", "2", "3"),
            [
                (
                    24,
                    "item 2.2 follows item 2.5, and its number is not above it",
                    "no number fits above 2.5 and below 2.3; item 2.5, the one before, may be the one out of"
                    f" place: {ascend}; {unused}",
                )
            ],
        ),
        "a letter before its plain number is a finding": (
            numbered("1", "2a", "2"),
            [
                (
                    25,
                    "item 2.2 follows item 2.2a, and its number is not above it",
                    f"give it a number above 2.2a in its handle and its anchor, such as 2.3; {unused}",
                )
            ],
        ),
        "a letter b before a is a finding": (
            numbered("1", "2b", "2a"),
            [
                (
                    25,
                    "item 2.2a follows item 2.2b, and its number is not above it",
                    f"give it a number above 2.2b in its handle and its anchor, such as 2.3; {unused}",
                )
            ],
        ),
        "after the letter z the next whole number is offered": (
            numbered("1", "2z", "2z"),
            [
                (
                    25,
                    "item 2.2z follows item 2.2z, and its number is not above it",
                    f"give it a number above 2.2z in its handle and its anchor, such as 2.3; {unused}",
                )
            ],
        ),
        "a first item numbered 0 is a finding, no number fits before the item after it": (
            numbered("0", "2", "3"),
            [(23, f"item 2.0 {first_what}", f"{first_room('2.2')}; {from_one}")],
        ),
        "a first item numbered 0 is told to take 1 where no item after it reads a number": (
            edit(edit(numbered("0", "2", "3"), ITEM_2, "   - A note."), ITEM_3, "   - Another note."),
            [
                (
                    23,
                    f"item 2.0 {first_what}",
                    f"give it a number from 1 up in its handle and its anchor, such as 2.1; {from_one}",
                ),
                (24, "this list line of step 2 does not read as an item", list_fix("above 2.0")),
                (25, "this list line of step 2 does not read as an item", list_fix("above 2.0")),
            ],
        ),
        "an item numbered 0 is the first of its step to read a number, a list line standing before it": (
            edit(
                numbered("0", "2", "3"),
                renumbered(ITEM_1, "1", "0"),
                "   * A note.\n" + renumbered(ITEM_1, "1", "0"),
            ),
            [
                (
                    23,
                    "this list line of step 2 does not read as an item",
                    "join its words to the sentence above, or write it as an item after the first one:"
                    f" {first_room('2.0')}",
                ),
                (24, f"item 2.0 {first_what}", f"{first_room('2.2')}; {from_one}"),
            ],
        ),
        "a fix names a number above the item before and below the item after": (
            numbered("3", "2", "5"),
            [
                (
                    24,
                    "item 2.2 follows item 2.3, and its number is not above it",
                    "give it a number above 2.3 and below 2.5 in its handle and its anchor, such as 2.3a;"
                    f" {unused}",
                )
            ],
        ),
        "after a letter the next letter is offered, not a whole number in the gap": (
            numbered("3a", "2", "5"),
            [
                (
                    24,
                    "item 2.2 follows item 2.3a, and its number is not above it",
                    "give it a number above 2.3a and below 2.5 in its handle and its anchor, such as 2.3b;"
                    f" {unused}",
                )
            ],
        ),
        "no letter is offered where the item after has the whole number of the item before": (
            numbered("3", "2", "3b"),
            [
                (
                    24,
                    "item 2.2 follows item 2.3, and its number is not above it",
                    "no number fits above 2.3 and below 2.3b; item 2.3, the one before, may be the one out"
                    f" of place: {ascend}; {unused}",
                )
            ],
        ),
        "no number fits after the letter z, though whole numbers lie before the item after": (
            numbered("2z", "2", "4"),
            [
                (
                    24,
                    "item 2.2 follows item 2.2z, and its number is not above it",
                    "no number fits above 2.2z and below 2.4; item 2.2z, the one before, may be the one out"
                    f" of place: {ascend}; {unused}",
                )
            ],
        ),
        "the upper bound is the next item that reads a number, a list line between skipped": (
            edit(
                numbered("3", "2", "5"),
                renumbered(ITEM_3, "3", "5"),
                "   * A plain note.\n" + renumbered(ITEM_3, "3", "5"),
            ),
            [
                (
                    24,
                    "item 2.2 follows item 2.3, and its number is not above it",
                    "give it a number above 2.3 and below 2.5 in its handle and its anchor, such as 2.3a;"
                    f" {unused}",
                ),
                (
                    25,
                    "this list line of step 2 does not read as an item",
                    list_fix("above 2.2 and below 2.5"),
                ),
            ],
        ),
        "a letter is named where the next whole number is the bound": (
            numbered("2", "2", "3"),
            [
                (
                    24,
                    "item 2.2 follows item 2.2, and its number is not above it",
                    "give it a number above 2.2 and below 2.3 in its handle and its anchor, such as 2.2a;"
                    f" {unused}",
                )
            ],
        ),
        "no number fits below the letter a after the same number": (
            numbered("2", "2", "2a"),
            [
                (
                    24,
                    "item 2.2 follows item 2.2, and its number is not above it",
                    "no number fits above 2.2 and below 2.2a; item 2.2, the one before, may be the one out of"
                    f" place: {ascend}; {unused}",
                )
            ],
        ),
        "no number fits between the letter z and the next whole number": (
            numbered("2z", "2", "3"),
            [
                (
                    24,
                    "item 2.2 follows item 2.2z, and its number is not above it",
                    "no number fits above 2.2z and below 2.3; item 2.2z, the one before, may be the one out"
                    f" of place: {ascend}; {unused}",
                )
            ],
        ),
    }


def list_fix(where: str) -> str:
    """The fix for a list line of step 2 that is no item, with the numbers its <m> may take."""
    return (
        'write it as an item, - <a id="s2-<m>"></a>**2.<m>** <mark> <text>,'
        f" with an <m> {where}, or join its words to the sentence above"
    )


def list_cases() -> dict[str, tuple[str, Want]]:
    def edited(old: str, new: str) -> str:
        return edit(BASE, old, new)

    what = "this list line of step 2 does not read as an item"
    fix = list_fix("above 2.3")
    note = "   * A plain note."
    return {
        "a list line that is no item is a finding": (
            edited(ITEM_3, ITEM_3 + "\n   - A plain note."),
            [(26, what, fix)],
        ),
        "a * bullet is a finding, though it reads as an item otherwise": (
            edited(ITEM_3, ITEM_3.replace("   - ", "   * ")),
            [(25, what, list_fix("above 2.2"))],
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
        "a list line before every item is told no number fits, and to write it after the first one": (
            edited(ITEM_1, note),
            [
                (
                    23,
                    what,
                    "join its words to the sentence above, or write it as an item after the first one:"
                    f" {first_room('2.2')}",
                )
            ],
        ),
        "a list line above item 2.1 is told the items of a step are numbered from 1": (
            edit(BASE, ITEM_1, note + "\n" + ITEM_1),
            [
                (
                    23,
                    what,
                    "join its words to the sentence above, or write it as an item after the first one:"
                    f" {first_room('2.1')}",
                )
            ],
        ),
        "list lines and no item are told to number from 1 up": (
            edit(
                edit(edited(ITEM_1, note), ITEM_2, "   * A second note."),
                ITEM_3,
                "   * A third note.",
            ),
            [
                (23, what, list_fix("from 1 up")),
                (24, what, list_fix("from 1 up")),
                (25, what, list_fix("from 1 up")),
            ],
        ),
        "a list line between two items is told both bounds": (
            edited(ITEM_2, note),
            [(24, what, list_fix("above 2.1 and below 2.3"))],
        ),
        "a list line where no number fits is told to join its words, or to make room": (
            edit(edited(ITEM_3, renumbered(ITEM_3, "3", "1a")), ITEM_2, note),
            [
                (
                    24,
                    what,
                    "join its words to the sentence above, or renumber first and then write it as an item:"
                    " no number fits above 2.1 and below 2.1a; item 2.1, the one before, may be the one out"
                    " of place",
                )
            ],
        ),
        "a list line after a closed fenced block is read again": (
            edited(ITEM_3, ITEM_3 + "\n```\n- inside\n```\n- A plain note."),
            [(29, what, fix)],
        ),
        "a fence line with backticks in its words opens no block": (
            edited(ITEM_3, ITEM_3 + "\n\n```not a fence``` here\n- A plain note."),
            [(28, what, fix)],
        ),
        "a fence line indented four spaces opens a block": (
            edited(ITEM_3, ITEM_3 + "\n    ```\n- inside\n    ```\n- A plain note."),
            [(29, what, fix)],
        ),
        "a closing fence line at another indent closes the block": (
            edited(ITEM_3, ITEM_3 + "\n```\n- inside\n      ```\n- A plain note."),
            [(29, what, fix)],
        ),
        "a shorter fence line does not close a longer fence": (
            edited(ITEM_3, ITEM_3 + "\n````\n```\n- inside\n```\n````\n- A plain note."),
            [(31, what, fix)],
        ),
        "a ~~~ line does not close a ``` block": (
            edited(ITEM_3, ITEM_3 + "\n```\n~~~\n- inside\n```\n- A plain note."),
            [(30, what, fix)],
        ),
        "a ``` line with words inside an open fence does not close it": (
            edited(ITEM_3, ITEM_3 + "\n```\n```text\n- inside\n```\n- A plain note."),
            [(30, what, fix)],
        ),
    }


def run_cases() -> dict[str, tuple[str, Want]]:
    def edited(old: str, new: str) -> str:
        return edit(BASE, old, new)

    join = "join this line to the line above, or put a blank line above it where it is no part of the item"
    done = '   - <a id="s2-1"></a>**2.1** ✅ Done thing,'
    rule = '1. <a id="s1"></a>✅ Rule made,'
    link_fix = (
        "link its record, or the document or the module its routine change concerns, or, once its record is"
        " deleted, the current-state document that carries its ruling"
    )
    return {
        "an item that runs on to a second line is a finding": (
            edited(ITEM_2, ITEM_2 + "\n   and more words"),
            [(25, "this is a second line of item 2.2", join)],
        ),
        "a third line under an item is a finding of its own": (
            edited(ITEM_2, ITEM_2 + "\n   and more words\n   and yet more"),
            [
                (25, "this is a second line of item 2.2", join),
                (26, "this is a further line of item 2.2", join),
            ],
        ),
        "a heading right under an item is a finding, the fix offers a blank line above it": (
            edited(ITEM_3, ITEM_3 + "\n## A heading"),
            [(26, "this is a second line of item 2.3", join)],
        ),
        "a done item whose link stands on the second line has the finding of that line alone": (
            edited(ITEM_1, done + "\n   [the record](records/second.md)."),
            [(24, "this is a second line of item 2.1", join)],
        ),
        "a done item whose link is split across two lines has the finding of the second alone": (
            edited(ITEM_1, done + " [the record\n   of it](records/second.md)."),
            [(24, "this is a second line of item 2.1", join)],
        ),
        "a done item whose link is split right after its ( has the finding of the second line alone": (
            edited(ITEM_1, done + " [the record](\n   records/second.md)."),
            [(24, "this is a second line of item 2.1", join)],
        ),
        "a done item with no link on either line has both findings": (
            edited(ITEM_1, done + "\n   and more words."),
            [
                (23, "done item 2.1 holds no link", link_fix),
                (24, "this is a second line of item 2.1", join),
            ],
        ),
        "a list line that is no item and runs on is a finding": (
            edited(ITEM_3, ITEM_3 + "\n   * A plain note\n   continued."),
            [
                (26, "this list line of step 2 does not read as an item", list_fix("above 2.3")),
                (27, "this is a second line of the list line at line 26", join),
            ],
        ),
        "a further line under a list line that is no item names that list line": (
            edited(ITEM_3, ITEM_3 + "\n   * A plain note\n   continued\n   and continued."),
            [
                (26, "this list line of step 2 does not read as an item", list_fix("above 2.3")),
                (27, "this is a second line of the list line at line 26", join),
                (28, "this is a further line of the list line at line 26", join),
            ],
        ),
        "a step with no items that runs on to a second line is a finding": (
            edited(STEP_3, STEP_3 + "\nand more words"),
            [(27, "this is a second line of step 3, which has no items", join)],
        ),
        "a third line under a step with no items is a finding of its own": (
            edited(STEP_3, STEP_3 + "\nand more words\nand yet more"),
            [
                (27, "this is a second line of step 3, which has no items", join),
                (28, "this is a further line of step 3, which has no items", join),
            ],
        ),
        "a done step with no items whose link stands on the second line has the finding of that line alone": (
            edited(STEP_1, f"{rule}\n[the record](records/first.md)."),
            [(18, "this is a second line of step 1, which has no items", join)],
        ),
        "a done step with no items whose link is split across two lines has the second line's finding": (
            edited(STEP_1, f"{rule} [the record\nof it](records/first.md)."),
            [(18, "this is a second line of step 1, which has no items", join)],
        ),
        "a done step with no items and no link on either line has both findings": (
            edited(STEP_1, f"{rule}\nand more words."),
            [
                (17, "done step 1, which has no items, holds no link", link_fix),
                (18, "this is a second line of step 1, which has no items", join),
            ],
        ),
    }


def fence_cases() -> dict[str, tuple[str, Want]]:
    def edited(old: str, new: str) -> str:
        return edit(BASE, old, new)

    never = "this fenced block never closes"
    close = "close it with a line of the same fence, with nothing after it, where its code ends"
    visible_sums = "| all | All steps | all | 🔄 | 2 | 1 | 1 | 66% |"  # the sums of steps 1 and 2 alone
    return {
        "a fenced block that never closes is a finding at its opening line": (
            edited(STEP_4, STEP_4 + "\n```\n- inside"),
            [(28, never, close)],
        ),
        "a tilde block that never closes is a finding": (
            edited(STEP_4, STEP_4 + "\n~~~\ninside"),
            [(28, never, close)],
        ),
        "a closing line with words does not close the block": (
            edited(STEP_4, STEP_4 + "\n```\n```text"),
            [(28, never, close)],
        ),
        "a block that never closes after a closed one is found at its own opening line": (
            edited(STEP_4, STEP_4 + "\n```\ninside\n```\n~~~\ninside"),
            [(31, never, close)],
        ),
        "a block left open hides the steps below it, and no row is reported as lacking its step": (
            edit(edited(STEP_3, "```\n" + STEP_3), ROW_ALL, visible_sums),
            [(26, never, close)],
        ),
        "a block left open inside a step with items holds no row against the items": (
            edited(ITEM_2, "```\n" + ITEM_2),
            [(24, never, close)],
        ),
        "a block left open above the matrix gives its own finding alone": (
            edited(HEADER, "```\n" + HEADER),
            [(6, never, close)],
        ),
        "a block left open leaves the row all unheld, its sums standing for every step": (
            edited(STEP_3, "```\n" + STEP_3),
            [(26, never, close)],
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
        "a fence indented five spaces inside an item holds no items: green": fenced(
            "     ```", "     - A plain note.", "     ```"
        ),
        "a tilde fence indented four spaces holds no items: green": fenced(
            "    ~~~", "    1. Another.", "    ~~~"
        ),
        "a longer fence holds what a shorter one shows: green": fenced("````", "```", example, "```", "````"),
        "a step line and a phase line in a fence are none: green": fenced(
            "```", '5. <a id="s5"></a>⏳ Not a step.', '<a id="phase-c"></a>', "```"
        ),
        "a line after a fenced block under an item is no second line: green": fenced(
            "```", "- inside", "```", "A line after the block."
        ),
        "a paragraph after a blank line under an item is no second line: green": edit(
            BASE, ITEM_3, ITEM_3 + "\n\nA paragraph of the step,\nin two lines."
        ),
        "a phase line right under an item is no second line: green": edit(
            edit(
                edit(BASE, ITEM_3, ITEM_3 + '\n<a id="phase-c"></a>'), ROW_3, ROW_3.replace("| B |", "| C |")
            ),
            ROW_4,
            ROW_4.replace("| B |", "| C |"),
        ),
        "a line right under the line of a step with items is the step's own text: green": edit(
            BASE, STEP_2, STEP_2 + "\nMore words of the step."
        ),
        "a blank line, a phase line or a fenced block under a step with no items ends its line: green": edit(
            edit(BASE, STEP_3, STEP_3 + "\n\nA paragraph of the step."),
            STEP_4,
            STEP_4
            + "\n```\ninside\n```\nA line after the block.\n"
            + '<a id="phase-c"></a>\nAfter the phase line.',
        ),
        "a phase anchor in a fenced block above the matrix is none: green": edit(
            BASE, "# Plan\n\n", '# Plan\n\n```\n<a id="phase-z"></a>\n```\n\n'
        ),
        "a header row in a fenced block above the matrix is none: green": edit(
            BASE, "# Plan\n\n", f"# Plan\n\n```\n{HEADER}\n```\n\n"
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
    for cases in (
        matrix_cases(),
        row_cases(),
        step_cases(),
        number_cases(),
        list_cases(),
        run_cases(),
        fence_cases(),
    ):
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
    number_why = (
        "  why: an item keeps its number for good, and rule 4 of plc-0008-rollout-plan numbers the items of"
        " a step in ascending order from 1"
    )
    order_lines = [
        "RED: docs/rollout-plan.md:25: item 2.2 follows item 2.2, and its number is not above it",
        number_why,
        "  fix: give it a number above 2.2 in its handle and its anchor, such as 2.3; a number once used is"
        " not used again",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    bounds_lines = [
        "RED: docs/rollout-plan.md:24: item 2.2 follows item 2.3, and its number is not above it",
        number_why,
        "  fix: give it a number above 2.3 and below 2.5 in its handle and its anchor, such as 2.3a; a number"
        " once used is not used again",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    first_lines = [
        "RED: docs/rollout-plan.md:23: item 2.0 is the first item of step 2 that reads a number, and its"
        " number is below 1",
        number_why,
        "  fix: no number fits before item 2.2, the next one numbered, since a number once used is not used"
        " again, and an item added before the first stands after it instead; the items of a step are"
        " numbered from 1",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    no_fit_lines = [
        "RED: docs/rollout-plan.md:24: item 2.2 follows item 2.5, and its number is not above it",
        number_why,
        "  fix: no number fits above 2.5 and below 2.3; item 2.5, the one before, may be the one out of"
        " place: renumber it in its handle and its anchor so that the numbers ascend; a number once used is"
        " not used again",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    run_lines = [
        "RED: docs/rollout-plan.md:25: this is a second line of item 2.2",
        "  why: an item is one line, so its mark, its words and its link are read together",
        "  fix: join this line to the line above, or put a blank line above it where it is no part of the"
        " item",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    fence_lines = [
        "RED: docs/rollout-plan.md:28: this fenced block never closes",
        "  why: every line after it is read as code, so the steps and items below are not checked",
        "  fix: close it with a line of the same fence, with nothing after it, where its code ends",
        "RED: 1 finding(s) — 4 step(s), 6 item(s) examined",
    ]
    red_text = edit(BASE, ROW_2, ROW_2.replace("| 1 | 1 | 1 |", "| 2 | 1 | 1 |"))
    link_text = edit(BASE, ITEM_1, '   - <a id="s2-1"></a>**2.1** ✅ Done thing.')
    run_text = edit(BASE, ITEM_2, ITEM_2 + "\n   and more words")
    fence_text = edit(BASE, STEP_4, STEP_4 + "\n```\n- inside")
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
        red_outcome(
            "the report of a number between two bounds is its literal text, exit 2",
            numbered("3", "2", "5"),
            bounds_lines,
        ),
        red_outcome(
            "the report of a number where none fits is its literal text, exit 2",
            numbered("5", "2", "3"),
            no_fit_lines,
        ),
        red_outcome(
            "the report of a first item with no room before the next is its literal text, exit 2",
            numbered("0", "2", "3"),
            first_lines,
        ),
        red_outcome("the report of an item that runs on is its literal text, exit 2", run_text, run_lines),
        red_outcome(
            "the report of a fenced block that never closes is its literal text, exit 2",
            fence_text,
            fence_lines,
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
