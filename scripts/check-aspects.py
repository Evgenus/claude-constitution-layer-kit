#!/usr/bin/env python3
"""Kit check: every acceptance item names the matrix rows it proves, and each row gets a result.

The matrix of docs/requirements.md holds the rows; each module document's rows section (template
§3) says which of them the module holds; its acceptance table (template §10) is
`| item | kind | rows | what it proves |`, the `rows` cell linking each row the item proves or
saying `none` for an item that proves no row of the module. A row's status is derived here on
each run and stored nowhere: the matrix carries no status, and a module's progress stays in the
rollout plan (decision dec-0054-acceptance-items-name-their-rows).

The gate, a plain run, reads the documents and runs nothing. It is red on:
  - an acceptance table without the `rows` column;
  - an item cell that is not a list of handles and closed ranges, `T1–T4, T7`, `S101`, `L1b`;
  - a kind that opens with none of the words fixture, kit check, live, eval, review — `live,
    deferred` opening with live;
  - an eval item, whose "what it proves" cell names its case as the one code span `evals/<case>/`
    (a case's name: lowercase letters, digits and hyphens), that names no case in that form, or names
    more than one; one that names a case folder its module does not have; a case folder of the module
    that no eval item names; a case two eval items name. A case folder is a folder of the module's
    `evals/` that holds a `case.yaml`, `evals/results/` and a folder holding a `prompt.md` alone being none
    (decision dec-0093-module-evals-with-local-receipts, R9);
  - a fixture item whose handle is no runner number: a prefix other than `T` or `S`, or a suffix after
    the number;
  - a `rows` cell that is empty, or holds anything but row links or the one word `none`;
  - a link to a row the matrix does not hold;
  - an item that names a row its module's rows section does not hold;
  - a row a module's rows section holds that no item of that module names;
  - a row the matrix gives a module (its destination opens with M and a number) that no
    module's rows section holds;
  - a row whose destination opens with none of the four classes `kernel §<n>`, `M<n>`, `binding`,
    `template`, typed here once with their patterns and matched at the start of the cell, its links
    read for their text, a name that goes on in a word or a digit that is not ASCII being none;
  - a shared acceptance item whose number does not follow the one before it, the numbers of the
    `@item(<n>, …)` markers of `shared/constitution_layer_kit/testing/items.py`
    standing unique and rising from 101 (an item's number is never reissued, rule 4 of
    plc-0009-shared-code), and every `S<n>` handle and
    range `S<n>–S<m>` (a hyphen too) in `shared/ITEMS.md`, its table and its prose, anchor
    `g5` to the end of the page, that names a number the shared tests do not
    hold, a range whose end is not above its start included. Every run holds them, `--run --module`
    too, and the counts line says how many shared items were read.

The documents are read in the forms their rules state, and a read that cannot be sure is no pass: the
check could not run (BROKEN, exit 1), with the fix, on
  - a matrix line that holds `<a id="aN-M"></a>` or `<a id="aN"></a>` and is not in the form
    `| <a id="aN-M"></a>AN.M | … |` of a row, four cells, or `| <a id="aN"></a>**AN — Title**` of an
    aspect, a prose line that shows the anchor included; two lines that open with the same row or aspect
    anchor; a
    matrix with no row;
  - a preamble without the sentence "Destination classes: …", or one whose bold names are not exactly
    the four classes the check types, so that the typed set never drifts from the preamble (every
    run reads it, `--run --module` too);
  - `shared/constitution_layer_kit/testing/items.py`, read by `ast` and never by
    import, when it cannot be parsed, holds no top-level test marked `@item(<n>, …)`, or has such a
    marker that opens with no int literal (a string, a float, a boolean, a negative number, a keyword);
    and `shared/ITEMS.md` without its anchor `g5` alone on a line, or with it twice;
  - a module folder with no MODULE.md, or no modules/ at all (the folders are those of
    `kit_module_doc.module_folders`, the kit's one listing: sorted by name, a folder whose name opens
    with a dot or an underscore and a plain file no module, a name without `const-` one), and a module
    document whose rows section (anchor `t3`) or acceptance section (anchor `t10`) is missing or stands
    twice, or whose next section's anchor is missing once any later one stands (`t4` after `t3`, `t11`
    after `t10`), or stands elsewhere, with another anchor, or none, after this one (`t11` before
    `t10`), each read by `kit_module_doc.section`.
A table line of those two sections is read whatever its indent: a line whose stripped form starts
with `|`. The last cell of any table line it reads, the matrix's rows too, is read whether or not
the line closes with a bar (`kit_module_doc.cells`).

The report, `--run`, also runs each module's tests, its runner, under pytest, `python3 -m pytest
modules/<name>/tests -p no:cacheprovider -W error -q`, with `-n <value>` from pytest-xdist when the
environment's CONSTITUTION_KIT_JOBS names a value: first collected serially, so that a stop of the shared
acceptance.collected is read whole; then run with a JUnit report, from which each item's result is read,
its number the testcase's property `item`, a skipped item left out and so not counted in the runner's
total T. pytest exit 0 is green and 1 a run with red items; a collection that fails, any other exit, a
report whose counts differ from its testcases or a testcase without one number, a number twice, or an exit
that disagrees with the report means the runner could not be read: the check could not run, never a pass.
pytest, or xdist where a value is named, not installed is BROKEN before the run, with the pinned install
command. A run, or a collection, that exits other than 0 has its whole output, stdout then stderr, printed
first, line for line, under one line naming the runner and its exit, so that a red item's own lines stand
where the run is read — as in the kit's CI, which runs each module's fixtures through `--run --module
<name>`. A fixture item's handle is its test's number, bare or under `T` or `S` — `T12` and `12` are item
12, `S101` is item 101. Also red under `--run`, with or without `--module`: a runner item no table row
names, and a fixture item a table names that the runner did not report. Also red under `--run`, for each
module whose runner ran: a number typed on the `Runner:` line of section 10 of its document (`<digits>
items green`, the first such line outside code fences, the first such match on it) that is not the
runner's total T; a Runner line without that form, or none, is no finding, and the gate, which runs no
runner, compares nothing.

Under `--run`, with or without `--module`, an eval item's result comes from its module's receipt in
`scripts/eval-receipts.json`, read once for the module with `kit_evals`, and only for a module that has an
eval item: `green` where the receipt is current — its hash the module's eval hash now, its Claude Code
version the one `scripts/claude-code.version` pins, its model the one `scripts/eval-model` names — and its
last attempt passes; `red` where it is current and the last attempt does not pass, which makes the run red
as a red fixture item does; otherwise no result, the item's label `eval, no current receipt`, never green
and never red, since `scripts/check-eval-receipts.py` turns a stale receipt red. A receipt with no attempt
is no current receipt. The item's line reads `eval — green (receipt of <date of the last attempt>)` or
`eval, no current receipt — not run`. A receipt, a pin or a hash that cannot be read is BROKEN with the
fix, never a pass. The gate reads no receipt.

Each row a module holds is printed with its destination as the matrix states it, every module
that holds a part of it with the version of its manifest, and every item that names it — from
every such module alike — with its kind and its result. Then one verdict. `red` when an item of
it is red. `green` when at least one of its items was run and every item run was green, an eval item
counting as run when its module's receipt is current — a run declared, not one the kit sees,
which narrows R1 and R10 of dec-0054-acceptance-items-name-their-rows (R9 of
dec-0093-module-evals-with-local-receipts); the
items no run examines, of any module that holds a part of the row, are listed beside and do not
lower it. `carrier green` instead of `green` for an advisory row — its enforcement cell in the
matrix opens with the word `advisory` and holds the word `gate` or `gates` nowhere, matched as
whole words, so that "ungateable" is no gate and "gate-lite" is one — since a fixture there
proves the carrier of a judgment, never the judgment. Otherwise the kinds of its items joined
by " + ": `live, done <date>`, `live` for a live item that names no date, `live, deferred`,
`review`, `kit check`, `eval` for an eval item no run examined, `eval, no current receipt` for one a run
found no current receipt for, and `fixture, not read` for a fixture item the runner did not report —
none of them a green. A row a module holds that no item names is `no item`, a finding of the
gate as well. A row no module holds is printed as
"held by" its destination and its enforcement cell as the matrix states them, counted as
`no module`, and never green. A shared-items line carries every row a fixture item of the
module, run through the same entry point, names, so a red there turns those rows red. Items
marked `none` are listed per module outside every row; a red one still makes the run red.

Modes:  no arguments         the gate;
        --run                every runner, then the per-row report, the gate's findings and the
                             run's, and one verdict;
        --run --module NAME  the same for one module: its findings alone, and those of the shared
                             items, its rows' verdicts from its items alone;
        --self-test          prove the check on a throwaway tree: each finding red→green, the
                             openings of a destination over a whole set (classed or red), indented
                             table lines read, a matrix line off its form, a doubled anchor, a
                             preamble that is missing or names other classes, a module document
                             without or with a doubled anchor and a folder without its document
                             each a BROKEN line, no modules/ too, a folder opening `.` or `_`
                             skipped, a name without `const-` listed, sorted whatever order the
                             folder lists, the report
                             of one finding as literal lines, a full run green and red, a runner
                             that cannot be read as a BROKEN line, each run pytest's on a throwaway
                             module, a typed runner count equal to the
                             total, off it, absent, in another form, inside a fence, and off it
                             run without `--run`; the shared items over their
                             whole set of cases: numbers and ranges of the table green and red,
                             a file or form it cannot read BROKEN, the report as literal lines;
                             the coverage mode, a green run and a red one each writing the file,
                             a gate's child process measured and a file no run imports missed,
                             no file with the variable unset, and a red run whose file cannot be
                             written printing its output before the BROKEN line; the shared pytest
                             wiring on a throwaway module that links the kit's own shared test
                             files, check_case red on either half, a test with no number and a
                             number carried twice stopping the run, serially and with xdist, the
                             message of a number carried twice over its cases as literal lines,
                             and the number in the JUnit report — it needs coverage.py, pytest and
                             pytest-xdist, at the versions .github/workflows/gates.yml pins; the eval
                             kind: an item for a case folder green, and each of an item with no case,
                             with a case in capitals or with no closing slash, with two cases, with a
                             folder the module does not have, with one that holds no case file, with
                             `evals/results/`, a folder no item names, a folder with a prompt.md alone, and
                             a case two or three items name red with one finding, the report of one as
                             literal lines, and under `--run`, a git tree with a receipt: an item green on
                             a current receipt whose last attempt passes, red on one whose last attempt
                             fails, no current receipt after an edit of a script or of the case, another
                             Claude Code pin or model, no entry, no file and no attempt — the edit of a
                             test or of MODULE.md leaving it current — and a receipts file, a model file
                             or a pin that cannot be read, and a tree that is no git repository, each a
                             BROKEN line with the fix while the gate stays green.
With CONSTITUTION_KIT_COVERAGE naming a folder, `--run` runs each runner under coverage.py and writes
`<folder>/<module>.json`, a red run too, before it reads the runner's lines (scripts/kit_coverage.py
says how); a runner that runs past its time is a BROKEN line, as without the variable, and writes no
file. coverage.py not installed is a BROKEN line before the runner starts; a step of it that fails
after the run is one too, printed after the output of a runner that exited other than 0, never in its
place. The kit's CI sets the variable in each module's job, and scripts/module-coverage.py reads the
files: a report, whose numbers no check holds (decision dec-0089-module-coverage-report). Empty or
absent, the runner runs plain.
With GITHUB_STEP_SUMMARY naming a file, as GitHub Actions does in every job, `--run` appends to it, for
each module whose report was read, a red run too, a Markdown section: the module and its counts of passed,
failed, error and skipped tests, each count that is not zero, then one table row for each test, its item
number, its name and its result, in number order. A report for a person, never a verdict: a summary that
cannot be written is a note, and the run's verdict stands; the self-test clears the variable, save in the
case that sets it.
Exit:   0 green; 2 a finding or a red item; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import importlib.util
import io
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from functools import partial
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import kit_coverage
from kit_evals import (
    EVAL_MODEL,
    EVALS,
    RECEIPTS,
    Attempt,
    EvalError,
    Receipt,
    eval_hash,
    eval_model,
    read_receipts,
    write_receipts,
)
from kit_module_doc import CLAUDE_PIN, DocumentError, cells, module_folders, pinned_claude, section

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
SPEC = "docs/requirements.md"
RUNNER_TIMEOUT = 1800  # seconds; the slowest runner takes a few minutes
JOBS_ENV = "CONSTITUTION_KIT_JOBS"  # pytest-xdist workers, a number or `auto`; empty or unset: one process
PYTEST_RED = 1  # pytest's exit when a test failed; 0 is green, and every other exit could not run
JUNIT_PROPERTY = "item"  # the property acceptance.collected hands each test's number to the report as
SUMMARY_ENV = "GITHUB_STEP_SUMMARY"  # the file GitHub Actions shows on a run's page; unset outside a job
RESULTS = ("passed", "failed", "error", "skipped")  # a test's result in the job summary, in its counts' order

ASPECT = re.compile(r'^\| <a id="(a\d+)"></a>\*\*(A\d+ — [^*]+)\*\*')
ROW = re.compile(r'^\| <a id="(a\d+-\d+)"></a>(A\d+\.\d+) \|')
ASPECT_ANCHOR = re.compile(r'<a id="(a\d+)"></a>')
ROW_ANCHOR = re.compile(r'<a id="(a\d+-\d+)"></a>')
ROW_LINK = re.compile(r"\[([^\[\]]*)\]\(([^()\s]*)\)")
LINK_TEXT = re.compile(r"\[([^\[\]]*)\]\([^()]*\)")
HANDLE = r"[A-Z]?\d+[a-z]?"
ITEM_TOKEN = re.compile(rf"^(?P<a>{HANDLE})(?:–(?P<b>{HANDLE}))?$")
HANDLE_PARTS = re.compile(r"^(?P<p>[A-Z]?)(?P<n>\d+)(?P<s>[a-z]?)$")
RUNNER_COUNT = re.compile(r"\b([0-9]+) items green\b")  # the one form of a typed count that is read
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
DONE = re.compile(r"\bdone (\d{4}-\d{2}-\d{2})\b")
MODULE_DEST = re.compile(r"^M\d+\b")
# The closed set of destination classes, typed once: the name the preamble of the matrix writes in bold,
# and the pattern that classes a cell, read through `plain()`, at the cell's start (rule 7 of
# plc-0007-requirements). The tie to the preamble is `check_classes`.
DEST_CLASSES: dict[str, re.Pattern[str]] = {
    "kernel §n": re.compile(r"^kernel §[0-9]+\b"),
    "Mx": re.compile(r"^M[0-9]+\b"),
    "binding": re.compile(r"^binding\b"),
    "template": re.compile(r"^template\b"),
}
CLASSES_SENTENCE = "Destination classes:"
CODE_SPAN = re.compile(r"`[^`\n]*`")
CASE_SPAN = re.compile(r"evals/([a-z0-9-]+)/")  # an eval case as an item names it, between backticks
SENTENCE_END = re.compile(r"\.(?:\s|$)")
BOLD_SPAN = re.compile(r"\*\*([^*]+)\*\*")
ACCEPTANCE_HEADER = ["item", "kind", "rows", "what it proves"]

WHY_TAG = "a row's result comes only from the items that name it, so every item says which rows it proves"
WHY_HANDLES = (
    "the full run matches each item to the runner's numbered lines, and a cell it cannot read matches nothing"
)
WHY_KIND = "the kind says whether a run examines the item, and a kind outside the set cannot be judged"
WHY_EVAL = (
    "an eval case is a run on the pinned model whose receipt the kit keeps, so one item per case traces every"
    " case to the rows it proves (law 4 of CLAUDE.md)"
)
WHY_SCOPE = "a module implements exactly the rows its rows section holds (law 4 of CLAUDE.md)"
WHY_RUN = "a row is green only where a run examined it, so every item the runner prints must be in the table"
WHY_COUNT = "a count typed by hand drifts without a sound, and the runner's total is the one count"
WHY_CLASSES = (
    "the destination classes are a closed set, defined once in the preamble (rule 7 of"
    " plc-0007-requirements), and a destination outside it takes its row out of every check that reads it"
)

# The shared acceptance items (shared/ITEMS.md): the pinned numbers of their tests' markers,
# read by `ast`, and the handles of the page's table, from its anchor to the page's end.
# the shared items as pytest tests, `@item(<n>, …)` each
SHARED_TESTS = "shared/constitution_layer_kit/testing/items.py"
SHARED_MARKER = "item"
SHARED_GATE = "shared/ITEMS.md"
SHARED_FIRST = 101
SHARED_ANCHOR = '<a id="g5"></a>'
# `S<n>` or a range `S<n>–S<m>` (an en dash, or a hyphen), not part of a longer word or a dotted name
SHARED_HANDLE = re.compile(r"(?<![A-Za-z0-9_.])S(\d+)(?:[–-]S?(\d+))?(?![A-Za-z0-9_])")
SHARED_SHOWN = 5  # the numbers a finding names before it counts the rest
WHY_SHARED_NUMBERS = (
    "an item's number is never reissued (rule 4 of docs/policies/plc-0009-shared-code.md), so the shared"
    " tests hold each number once, in rising order from 101, and the tables that name an item by its"
    " number keep naming the same item"
)
WHY_SHARED_TABLE = (
    "the table of shared/ITEMS.md is where the kit says what each shared item proves, so every"
    " number it names must be an item the shared tests hold"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    what: str
    why: str
    fix: str

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"RED: {where}: {self.what}\n  why: {self.why}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Row:
    anchor: str
    handle: str
    aspect: str
    destination: str
    enforcement: str


@dataclass
class Item:
    module: str
    line: int
    handles: str
    kind: str  # fixture | kit check | live | live, deferred | eval | review
    rows: list[str]  # anchors; empty for `none`
    numbers: list[int]  # runner numbers, fixture items only
    done: str | None
    results: dict[int, bool] = field(default_factory=dict)
    case: str | None = None  # the case folder under evals/, eval items only
    eval_state: str | None = None  # eval items read under --run: green | red | stale (no current receipt)
    eval_day: str = ""  # the date of the receipt's last attempt, when eval_state is green or red

    def label(self) -> str:
        if self.kind == "live" and self.done:
            return f"live, done {self.done}"
        if self.kind == "eval" and self.eval_state == "stale":
            return "eval, no current receipt"
        return "fixture, not read" if self.kind == "fixture" else self.kind

    def outcome(self) -> str | None:
        """'green' or 'red' for a fixture item every number of which was read, and for an eval item whose
        receipt is current; None otherwise."""
        if self.kind == "eval":
            return self.eval_state if self.eval_state in ("green", "red") else None
        if self.kind != "fixture" or not self.numbers or any(n not in self.results for n in self.numbers):
            return None
        return "green" if all(self.results[n] for n in self.numbers) else "red"


@dataclass
class Module:
    name: str
    path: str
    version: str
    held: dict[str, int]  # anchor → line in the rows section
    items: list[Item]
    acceptance: list[tuple[int, str]] = field(default_factory=list)  # the lines of section 10, as read


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


def plain(cell: str) -> str:
    return LINK_TEXT.sub(r"\1", cell).replace("**", "").strip()


def off_form(number: int, line: str) -> Broken | None:
    """The BROKEN for a line that holds an aspect's or a row's anchor and is not in the form of `ASPECT`
    or `ROW`; None for a line that holds neither, whatever else it says."""
    for found, kind, form in (
        (ASPECT_ANCHOR.search(line), "an aspect's", '| <a id="aN"></a>**AN — Title**'),
        (ROW_ANCHOR.search(line), "a row's", '| <a id="aN-M"></a>AN.M | …'),
    ):
        if found is not None:
            return Broken(
                f"{SPEC}:{number}: the line holds {kind} anchor {found[0]} but is not in the matrix's form"
                f" — why: a line off its form drops out of the matrix without a word — fix: write it as"
                f" `{form}`, the line opening with `| ` at its start and no space between the anchor and"
                " what follows it"
            )
    return None


def read_matrix(root: Path) -> dict[str, Row]:
    """The rows of the matrix. A line that holds an aspect's or a row's anchor is read in the one form
    `ASPECT` or `ROW` states, or the check is BROKEN; so are two lines that open with the same anchor. A
    line that holds
    no such anchor, prose and a link to `#a1-4` among them, is read as before."""
    rows: dict[str, Row] = {}
    stands: dict[str, int] = {}
    aspect = ""
    for number, line in enumerate(read(root, SPEC).splitlines(), start=1):
        heading, row = ASPECT.match(line), ROW.match(line)
        if heading is None and row is None:
            if (bad := off_form(number, line)) is not None:
                raise bad
            continue
        anchor = heading[1] if heading is not None else row[1]  # type: ignore[index]
        if anchor in stands:
            raise Broken(
                f'{SPEC} holds the anchor <a id="{anchor}"></a> twice, lines {stands[anchor]} and {number}'
                " — why: the second would overwrite the first in the matrix"
                " — fix: keep the one anchor, on its own row or aspect"
            )
        stands[anchor] = number
        if heading is not None:
            aspect = heading[2].strip()
        else:
            parts = cells(line)
            if len(parts) != 4:
                raise Broken(
                    f"{SPEC}: the row {line[:40]}… has {len(parts)} cells, not 4 — fix: restore the"
                    " matrix's four columns"
                )
            rows[row[1]] = Row(row[1], row[2], aspect, plain(parts[2]), plain(parts[3]))  # type: ignore[index]
    if not rows:
        raise Broken(f"{SPEC} holds no matrix row — fix: run the check from a checkout of the kit")
    return rows


def preamble_classes(text: str) -> list[str] | None:
    """The bold names of the sentence that opens "Destination classes:", sorted and each once; None when
    no such sentence stands. The sentence runs to the first full stop that ends a word, code spans
    taken out first (one holds `constitution.yaml`); a bold span before it or after its end is no class."""
    start = text.find(CLASSES_SENTENCE)
    if start < 0:
        return None
    rest = CODE_SPAN.sub("", text[start + len(CLASSES_SENTENCE) :])
    end = SENTENCE_END.search(rest)
    sentence = rest[: end.start()] if end else rest
    return sorted({name.strip() for name in BOLD_SPAN.findall(sentence)})


def check_classes(root: Path) -> None:
    """BROKEN unless the preamble's bold class names are exactly the classes `DEST_CLASSES` types."""
    found = preamble_classes(read(root, SPEC))
    typed = sorted(DEST_CLASSES)
    quoted = ", ".join(f"'{name}'" for name in typed)
    if found is None:
        raise Broken(
            f'{SPEC} holds no sentence that opens "{CLASSES_SENTENCE}" — why: the check types the classes'
            f" {quoted} and holds them to the preamble's sentence, so a preamble it cannot read is a"
            " tie it cannot check — fix: restore the sentence in the preamble, or change the preamble"
            " and the check's classes together"
        )
    if found != typed:
        named = ", ".join(f"'{name}'" for name in found) or "none"
        raise Broken(
            f'{SPEC} names the destination classes {named} in its "{CLASSES_SENTENCE}" sentence, and this'
            f" check types {quoted} — why: the classes are a closed set defined once in the preamble"
            " (rule 7 of plc-0007-requirements), and the check's patterns are typed here, so the two"
            " must say the same names — fix: change the preamble and the check's classes together"
        )


def shared_numbers(root: Path) -> list[tuple[int, int]]:
    """(number, line) of each top-level test of the shared pytest file decorated `@item(<n>, …)`, in the
    file's order, read by `ast`, never by import. BROKEN when the file cannot be read or parsed, holds no
    such test, or a decorator `item(…)` opens with no int literal (a boolean, a string, a float, a negative
    number and a keyword are none)."""
    reading = "the check reads the numbers of the shared tests from their markers, by `ast`, never by import"
    try:
        tree = ast.parse(read(root, SHARED_TESTS))
    except SyntaxError as bad:
        raise Broken(
            f"{SHARED_TESTS} cannot be parsed ({bad.msg}, line {bad.lineno}) — why: {reading}"
            " — fix: repair the file's syntax"
        ) from bad
    found: list[tuple[int, int]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not (isinstance(decorator, ast.Call) and getattr(decorator.func, "id", None) == SHARED_MARKER):
                continue
            number = decorator.args[0] if decorator.args else None
            if not (isinstance(number, ast.Constant) and type(number.value) is int):
                raise Broken(
                    f"{SHARED_TESTS}:{decorator.lineno}: a marker `{SHARED_MARKER}(…)` opens with no int"
                    f" literal — why: {reading}, and a test with no number of its own is no item"
                    f' — fix: write it as `@{SHARED_MARKER}(<number>, "<title>")`'
                )
            found.append((number.value, decorator.lineno))
    if not found:
        raise Broken(
            f"{SHARED_TESTS} holds no test marked `@{SHARED_MARKER}(<number>, …)` — why: {reading}"
            f" — fix: restore the shared tests, each with its marker"
        )
    return found


def gate_section(root: Path) -> list[tuple[int, str]]:
    """The lines (1-based number in the file, text) of the page of shared items: after the line that is
    its anchor alone on a line to the end of the page. BROKEN when the anchor stands nowhere or twice."""
    lines = read(root, SHARED_GATE).splitlines()
    at = [number for number, line in enumerate(lines, start=1) if line.strip() == SHARED_ANCHOR]
    if len(at) != 1:
        raise Broken(
            f"{SHARED_GATE} holds the anchor {SHARED_ANCHOR}"
            f" {'nowhere on a line of its own' if not at else 'twice'}"
            " — why: the check reads the table of the shared items from that anchor to the next one, and"
            f" a section it cannot find is a table it cannot hold — fix: keep {SHARED_ANCHOR} alone on the"
            " line above the lead of the table"
        )
    return [(number, lines[number - 1]) for number in range(at[0] + 1, len(lines) + 1)]


def check_shared(root: Path) -> tuple[list[Finding], int]:
    """The findings of the shared acceptance items and how many items were read. Both files are read
    first, so a file that cannot be read is BROKEN whatever else is red. RED: a number that does not
    rise above the one before it, the first number if not 101, and in shared/ITEMS.md, its table
    and its prose, every handle or range that names a number the shared tests do not hold, and every
    range whose end is not above its start."""
    entries = shared_numbers(root)
    section_lines = gate_section(root)
    findings: list[Finding] = []
    previous: int | None = None
    for number, line in entries:
        if previous is None and number != SHARED_FIRST:
            findings.append(
                Finding(
                    SHARED_TESTS,
                    line,
                    f"the first shared item is numbered {number}, not {SHARED_FIRST}",
                    WHY_SHARED_NUMBERS,
                    f"number the first item {SHARED_FIRST}, and give a new item a number no item has had, at"
                    " the end of the file",
                )
            )
        elif previous is not None and number <= previous:
            findings.append(
                Finding(
                    SHARED_TESTS,
                    line,
                    f"the shared item numbered {number} follows {previous}, and the numbers are not unique"
                    " and rising",
                    WHY_SHARED_NUMBERS,
                    "give a new item a number no item has had, at the end of the file, and put a moved item"
                    " back in its place; a removed item's number is never given again",
                )
            )
        previous = number
    held = {number for number, _ in entries}
    for line, text in section_lines:
        for found in SHARED_HANDLE.finditer(text):
            first = int(found[1])
            last = int(found[2]) if found[2] is not None else first
            if last <= first and found[2] is not None:
                findings.append(
                    Finding(
                        SHARED_GATE,
                        line,
                        f"the range {found[0]} ends at or below its start",
                        WHY_SHARED_TABLE,
                        "write one handle for one item, or a range with its lower number first, `S<n>–S<m>`",
                    )
                )
                continue
            missing = (number for number in range(first, last + 1) if number not in held)
            shown = [f"S{number}" for number in itertools.islice(missing, SHARED_SHOWN + 1)]
            if shown:
                count = last - first + 1 - sum(1 for number in held if first <= number <= last)
                more = f" and {count - SHARED_SHOWN} more" if count > SHARED_SHOWN else ""
                findings.append(
                    Finding(
                        SHARED_GATE,
                        line,
                        f"the range {found[0]} names {', '.join(shown[:SHARED_SHOWN])}{more},"
                        " which the shared tests do not hold"
                        if found[2] is not None
                        else f"the handle {found[0]} names an item the shared tests do not hold",
                        WHY_SHARED_TABLE,
                        f"change the {'range' if found[2] is not None else 'handle'} to numbers"
                        f" {SHARED_TESTS} holds, or give the item that number in its marker",
                    )
                )
    return findings, len(entries)


def row_anchors(cell: str) -> tuple[list[str], str]:
    """The row anchors a cell links, and whatever else it holds besides separators."""
    anchors: list[str] = []
    for link in ROW_LINK.finditer(cell):
        target = link[2]
        path, _, anchor = target.partition("#")
        if path.endswith(SPEC) and re.fullmatch(r"a\d+-\d+", anchor):
            anchors.append(anchor)
        else:
            return anchors, link[0]
    rest = re.sub(r"[\s,;]+", "", ROW_LINK.sub("", cell))
    return anchors, rest


def parse_handles(cell: str) -> list[tuple[str, int, int, str]] | None:
    """(prefix, first, last, suffix) per token; None when the cell is not handles and closed ranges."""
    tokens = [t.strip() for t in cell.split(",")]
    out: list[tuple[str, int, int, str]] = []
    for token in tokens:
        m = ITEM_TOKEN.match(token)
        if not m:
            return None
        a = HANDLE_PARTS.match(m["a"])
        b = HANDLE_PARTS.match(m["b"]) if m["b"] else a
        if a is None or b is None or a["p"] != b["p"]:
            return None
        if m["b"] and (a["s"] or b["s"] or int(b["n"]) <= int(a["n"])):
            return None
        out.append((a["p"], int(a["n"]), int(b["n"]), a["s"]))
    return out


def kind_of(cell: str) -> str | None:
    """The kind a cell opens with, as a whole word: `fixtures` or `reviewer` is no kind."""
    text = cell.lower()
    for prefix, kind in (
        ("fixture", "fixture"),
        ("kit check", "kit check"),
        ("live, deferred", "live, deferred"),
        ("live", "live"),
        ("eval", "eval"),
        ("review", "review"),
    ):
        if re.match(rf"{re.escape(prefix)}\b", text):
            return kind
    return None


def module_version(directory: Path) -> str:
    """The version a module's manifest holds; Broken when the manifest is unreadable or no JSON object."""
    name = directory.name
    manifest = directory / "plugin" / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as bad:
        raise Broken(
            f"modules/{name}/plugin/.claude-plugin/plugin.json cannot be read ({bad}) — fix: restore the"
            " manifest"
        ) from bad
    if not isinstance(data, dict):
        raise Broken(
            f"modules/{name}/plugin/.claude-plugin/plugin.json is no JSON object, it holds a"
            f" {type(data).__name__}"
            " — fix: restore it as a JSON object"
        )
    return str(data.get("version", "?"))


def held_rows(rows_section: list[tuple[int, str]], matrix: dict[str, Row]) -> dict[str, int]:
    """The matrix rows a module's rows section links, each at the line of its first link."""
    held: dict[str, int] = {}
    for number, raw in rows_section:
        line = raw.strip()
        if not line.startswith("|"):
            continue
        first = cells(line)[0] if cells(line) else ""
        for link in ROW_LINK.finditer(first):
            path_part, _, anchor = link[2].partition("#")
            if path_part.endswith(SPEC) and anchor in matrix:
                held.setdefault(anchor, number)
    return held


def fixture_numbers(
    module: Module, number: int, handles: str, parsed: list[tuple[str, int, int, str]]
) -> list[int] | Finding:
    """The runner numbers a fixture item names, or the finding when a handle is no runner number."""
    if any(p not in ("", "T", "S") or s for p, _, _, s in parsed):
        return Finding(
            module.path,
            number,
            f"the fixture item {handles} has a handle that is no runner number",
            WHY_HANDLES,
            "write a fixture item as its runner number, bare or under `T` or `S`",
        )
    return [n for _, first, last, _ in parsed for n in range(first, last + 1)]


def eval_case(module: Module, number: int, handles: str, proves: str, findings: list[Finding]) -> str | None:
    """The case an eval item's 'what it proves' cell names, as the one code span `evals/<case>/`; None
    after a finding for a cell that names no case in that form, or more than one."""
    spans = [s[1:-1] for s in CODE_SPAN.findall(proves) if s[1:-1].startswith(f"{EVALS}/")]
    named = [m[1] for s in spans if (m := CASE_SPAN.fullmatch(s))]
    if len(spans) == 1 and len(named) == 1:
        return named[0]
    if len(spans) > 1:
        what = f"the eval item {handles} names {len(spans)} cases in its 'what it proves' cell, not one"
        fix = "keep one case in the cell, and give the other case an eval item of its own"
    else:
        what = f"the eval item {handles} names no case as `evals/<case>/` in its 'what it proves' cell"
        fix = (
            "write the case the item proves in that cell as a code span `evals/<case>/`, the folder's name"
            " of lowercase letters, digits and hyphens"
        )
    findings.append(Finding(module.path, number, what, WHY_EVAL, fix))
    return None


def case_folders(directory: Path) -> list[str]:
    """The eval cases of a module: each folder of `evals/` that holds a `case.yaml`, the one form the kit's
    runner runs, `evals/results/` being no case, sorted by name."""
    base = directory / EVALS
    if not base.is_dir():
        return []
    return sorted(
        d.name for d in base.iterdir() if d.is_dir() and d.name != "results" and (d / "case.yaml").is_file()
    )


def listed(handles: list[str]) -> str:
    """`L3`, `L3 and L4`, `L3, L4 and L5`."""
    return handles[0] if len(handles) == 1 else f"{', '.join(handles[:-1])} and {handles[-1]}"


def eval_findings(module: Module, directory: Path, header: int) -> list[Finding]:
    """The findings where the module's eval items and its case folders do not agree one to one: an item
    that names a folder the module does not have, a folder no item names, a case two items name."""
    folders = case_folders(directory)
    by_case: dict[str, list[Item]] = {}
    found: list[Finding] = []
    for item in module.items:
        if item.kind != "eval" or item.case is None:
            continue
        by_case.setdefault(item.case, []).append(item)
        if item.case not in folders:
            found.append(
                Finding(
                    module.path,
                    item.line,
                    f"the eval item {item.handles} names `evals/{item.case}/`, a case folder the module"
                    " does not have",
                    WHY_EVAL,
                    f"add the case folder `evals/{item.case}/` holding a `case.yaml`, or"
                    " name a case folder the module has",
                )
            )
    for case, same in by_case.items():
        if len(same) > 1:
            names = listed([i.handles for i in same])
            found.append(
                Finding(
                    module.path,
                    same[1].line,
                    f"the case `evals/{case}/` is named by the eval items {names}",
                    WHY_EVAL,
                    "keep one eval item for the case: merge the items, or name another case folder in one"
                    " of them",
                )
            )
    for case in folders:
        if case not in by_case:
            found.append(
                Finding(
                    module.path,
                    header,
                    f"the case folder `evals/{case}/` is named by no eval item",
                    WHY_EVAL,
                    f"add an eval item whose 'what it proves' cell names `evals/{case}/` and whose rows"
                    " cell links the rows the case proves, or remove the folder",
                )
            )
    return found


def row_findings(
    module: Module, number: int, handles: str, anchors: list[str], matrix: dict[str, Row]
) -> list[Finding]:
    """The findings for the rows an item links that the matrix or the module's rows section does not hold."""
    found: list[Finding] = []
    for anchor in anchors:
        if anchor not in matrix:
            found.append(
                Finding(
                    module.path,
                    number,
                    f"item {handles} links #{anchor}, a row the matrix does not hold",
                    WHY_TAG,
                    "link a row the matrix holds, or remove the link",
                )
            )
        elif anchor not in module.held:
            found.append(
                Finding(
                    module.path,
                    number,
                    f"item {handles} names {matrix[anchor].handle}, a row the rows section does not hold",
                    WHY_SCOPE,
                    "remove the link, or add the row to the rows section if the module implements it",
                )
            )
    return found


def read_item(
    module: Module, number: int, parts: list[str], matrix: dict[str, Row], findings: list[Finding]
) -> Item | None:
    """The acceptance item of one table row, or None after a finding for a row that cannot be read."""
    path = module.path
    if len(parts) != 4:
        findings.append(
            Finding(
                path,
                number,
                f"the acceptance item has {len(parts)} cells, not 4",
                WHY_TAG,
                "give the item its four cells: item, kind, rows, what it proves",
            )
        )
        return None
    handles, kind_cell, rows_cell, proves = parts
    parsed = parse_handles(handles)
    if parsed is None:
        findings.append(
            Finding(
                path,
                number,
                f"the item cell '{handles}' is not a list of handles and closed ranges",
                WHY_HANDLES,
                "write each handle out, as `T1–T4, T7` or `S101–S106, S111`",
            )
        )
        return None
    kind = kind_of(kind_cell)
    if kind is None:
        findings.append(
            Finding(
                path,
                number,
                f"the kind '{kind_cell}' of item {handles} is none of the set",
                WHY_KIND,
                "open the cell with one of `fixture`, `kit check`, `live`, `live, deferred`, `eval`,"
                " `review`",
            )
        )
        return None
    case = eval_case(module, number, handles, proves, findings) if kind == "eval" else None
    if kind == "eval" and case is None:
        return None
    numbers: list[int] = []
    if kind == "fixture":
        named = fixture_numbers(module, number, handles, parsed)
        if isinstance(named, Finding):
            findings.append(named)
            return None
        numbers = named
    anchors, rest = row_anchors(rows_cell)
    if rows_cell == "none":
        anchors = []
    elif not anchors or rest:
        findings.append(
            Finding(
                path,
                number,
                f"the rows cell of item {handles} is '{rows_cell}'",
                WHY_TAG,
                "link each row the item proves, [A1.4](../../docs/requirements.md#a1-4), or write"
                " `none` for an item that proves no row of the module",
            )
        )
        return None
    findings.extend(row_findings(module, number, handles, anchors, matrix))
    done = DONE.search(proves)
    return Item(
        module.name,
        number,
        handles,
        kind,
        [a for a in anchors if a in module.held],
        numbers,
        done[1] if done else None,
        case=case,
    )


def read_module(root: Path, directory: Path, matrix: dict[str, Row], findings: list[Finding]) -> Module:
    """One module document read: its version, the rows it holds and its acceptance items, each finding
    of its tables added to `findings`."""
    name = directory.name
    path = f"modules/{name}/MODULE.md"
    text = read(root, path)
    version = module_version(directory)
    try:
        rows_section, acceptance_section = section(text, "t3", path), section(text, "t10", path)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    held = held_rows(rows_section, matrix)
    module = Module(name, path, version, held, [], acceptance_section)
    table = [(n, raw.strip()) for n, raw in acceptance_section if raw.strip().startswith("|")]
    header = next(((n, cells(line)) for n, line in table if cells(line) and cells(line)[0] == "item"), None)
    if header is None or header[1] != ACCEPTANCE_HEADER:
        findings.append(
            Finding(
                path,
                header[0] if header else 0,
                "the acceptance table has no `rows` column",
                WHY_TAG,
                "make its header `| item | kind | rows | what it proves |` and give each item the row"
                " links it proves, or `none`",
            )
        )
        return module
    for number, line in table:
        parts = cells(line)
        if not parts or parts[0] == "item" or set(parts[0]) <= {"-", ":"}:
            continue
        item = read_item(module, number, parts, matrix, findings)
        if item is not None:
            module.items.append(item)
    findings.extend(eval_findings(module, directory, header[0]))
    for anchor, number in held.items():
        if not any(anchor in item.rows for item in module.items):
            findings.append(
                Finding(
                    path,
                    number,
                    f"{matrix[anchor].handle} is held by the rows section and named by no acceptance item",
                    WHY_TAG,
                    "add it to the rows cell of each item that proves it, or an item that does",
                )
            )
    return module


def modules_of(root: Path) -> list[Path]:
    """The module folders, through the kit's one listing; its error is this check's BROKEN."""
    try:
        return module_folders(root)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def check_structure(
    root: Path, only: str | None = None
) -> tuple[dict[str, Row], list[Module], list[Finding], int]:
    """The matrix, the modules, the findings and the number of shared items read; the shared items'
    findings and their BROKEN stand in every run, one module's too, as the tie to the preamble does."""
    matrix = read_matrix(root)
    check_classes(root)
    shared_findings, shared = check_shared(root)
    findings: list[Finding] = []
    modules = [read_module(root, d, matrix, findings) for d in modules_of(root)]
    held_anywhere = {a for m in modules for a in m.held}
    for row in matrix.values():
        if MODULE_DEST.match(row.destination) and row.anchor not in held_anywhere:
            findings.append(
                Finding(
                    SPEC,
                    0,
                    f"{row.handle} is given to a module, and no module's rows section holds it",
                    WHY_SCOPE,
                    "add the row to the rows section of the module that implements it",
                )
            )
        if not any(form.match(row.destination) for form in DEST_CLASSES.values()):
            findings.append(
                Finding(
                    SPEC,
                    0,
                    f"{row.handle} has the destination '{row.destination}', a destination the check"
                    " cannot class",
                    WHY_CLASSES,
                    "open the cell with one of the four classes — `kernel §<n>`, `M<n>`, `binding`,"
                    " `template` — or add a class to the preamble and to this check together",
                )
            )
    if only is not None:
        if only not in {m.name for m in modules}:
            raise Broken(
                f"no module '{only}' under modules/ — fix: name a directory of modules/ with --module"
            )
        modules = [m for m in modules if m.name == only]
        findings = [
            f for f in findings if f.path == modules[0].path
        ]  # the matrix's own findings are the gate's
    return matrix, modules, findings + shared_findings, shared


def counts(matrix: dict[str, Row], modules: list[Module], shared: int) -> str:
    items = sum(len(m.items) for m in modules)
    return (
        f"{len(matrix)} row(s) of the matrix, {len(modules)} module document(s),"
        f" {items} acceptance item(s) examined, {shared} shared item(s)"
    )


def run_once(
    root: Path, module: Module, command: list[str]
) -> tuple[subprocess.CompletedProcess[str], str | None]:
    """One run of the runner, `command` after the interpreter, under coverage.py when kit_coverage asks
    for it: the run, and the message of a coverage step that failed after it, for the caller to raise once
    the runner's output is printed."""
    out = kit_coverage.wanted()
    with tempfile.TemporaryDirectory(prefix="aspects-coverage-") as scratch:
        prefix: list[str] = [sys.executable]
        env: dict[str, str] | None = None
        if out is not None:
            try:
                prefix, env = kit_coverage.prepare(root, module.name, Path(scratch))
            except kit_coverage.CoverageError as bad:
                raise Broken(str(bad)) from bad
        started = time.monotonic()
        try:
            done = subprocess.run(
                [*prefix, *command],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=RUNNER_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired as slow:
            raise Broken(
                f"the runner of {module.name} ran past {RUNNER_TIMEOUT} s"
                " — fix: run it alone and see where it hangs"
            ) from slow
        if out is not None:
            seconds = round(time.monotonic() - started)
            try:
                kit_coverage.save(root, module.name, Path(scratch), out, done.returncode, seconds)
            except kit_coverage.CoverageError as bad:
                return done, str(bad)
    return done, None


def pins(*names: str) -> str:
    """The install command of the named packages at the versions the kit's CI pins, read from the
    workflow, which alone names them."""
    try:
        text = kit_coverage.WORKFLOW.read_text(encoding="utf-8")
    except OSError:
        text = ""
    wanted = []
    for name in names:
        found = re.search(rf'"{re.escape(name)}==([^"\s]+)"', text)
        wanted.append(f'"{name}=={found[1]}"' if found else name)
    return f"{sys.executable} -m pip install {' '.join(wanted)}"


def echo(module: Module, done: subprocess.CompletedProcess[str]) -> None:
    """A run that exited other than 0, printed whole, stdout then stderr, under one line naming it."""
    print(f"the runner of {module.name} exited {done.returncode}; its output, as it printed it:")
    for text in done.stdout.splitlines() + done.stderr.splitlines():
        print(text)


def last_words(done: subprocess.CompletedProcess[str]) -> str:
    return ((done.stderr.strip() or done.stdout.strip()).splitlines() or ["no message"])[-1]


def read_report(path: Path, name: str) -> dict[int, bool]:
    """Each item's result from pytest's JUnit report: its number the property `item`, red on a failure
    or an error, a skipped item left out. BROKEN when the report cannot be read or does not hold to
    itself: a testcase without one `item` property, a number twice, counts that differ from the
    testcases."""
    fix = f"run python3 -m pytest modules/{name}/tests -W error and repair what it names"
    try:
        top = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError) as bad:
        raise Broken(f"the JUnit report of {name}'s tests cannot be read ({bad}) — fix: {fix}") from bad
    suites = [top] if top.tag == "testsuite" else list(top.iter("testsuite"))
    declared = sum(int(suite.get("tests", "0")) for suite in suites)
    declared_skips = sum(int(suite.get("skipped", "0")) for suite in suites)
    cases = [case for suite in suites for case in suite.findall("testcase")]
    results: dict[int, bool] = {}
    seen: set[int] = set()
    skips = 0
    for case in cases:
        numbers = [p.get("value", "") for p in case.iter("property") if p.get("name") == JUNIT_PROPERTY]
        test = f"{case.get('classname')}::{case.get('name')}"
        if len(numbers) != 1 or not numbers[0].isascii() or not numbers[0].isdigit():
            raise Broken(
                f"the test {test} of {name} carries {len(numbers)} `{JUNIT_PROPERTY}` properties in the"
                f" JUnit report, not one number — fix: let the module's conftest call acceptance.collected"
                " from its pytest_collection_modifyitems"
            )
        number = int(numbers[0])
        if number in seen:
            raise Broken(f"two tests of {name} report the item number {number} — fix: {fix}")
        seen.add(number)
        tags = {child.tag for child in case}
        if "skipped" in tags:
            skips += 1
            continue
        results[number] = not ({"failure", "error"} & tags)
    if len(cases) != declared or skips != declared_skips:
        raise Broken(
            f"the JUnit report of {name}'s tests counts {declared} tests and {declared_skips} skips, and"
            f" holds {len(cases)} testcases, {skips} of them skipped — fix: {fix}"
        )
    return results


def report_rows(path: Path) -> list[tuple[int, str, str]]:
    """(item number, test name, result) of each testcase of a JUnit report read_report has held to
    itself, in number order; the result one of RESULTS."""
    rows = []
    for case in ElementTree.parse(path).getroot().iter("testcase"):
        number = next(p.get("value", "") for p in case.iter("property") if p.get("name") == JUNIT_PROPERTY)
        tags = {child.tag for child in case}
        result = (
            "failed" if "failure" in tags else next((t for t in ("error", "skipped") if t in tags), "passed")
        )
        rows.append((int(number), case.get("name", ""), result))
    return sorted(rows)


def write_summary(module: str, rows: list[tuple[int, str, str]]) -> None:
    """Append the module's section to the job summary GITHUB_STEP_SUMMARY names, when it names one: a
    heading with the module and its counts, then one table row for each test. A report, never a verdict:
    a summary that cannot be written is a note, and the run's verdict stands."""
    target = os.environ.get(SUMMARY_ENV, "").strip()
    if not target:
        return
    counts = ", ".join(f"{n} {r}" for r in RESULTS if (n := sum(1 for *_, x in rows if x == r)))
    table = [f"| {n} | `{name.replace('|', '\\|')}` | {result} |" for n, name, result in rows]
    text = "\n".join([f"### {module}: {counts}", "", "| item | test | result |", "|---|---|---|", *table, ""])
    try:
        with open(target, "a", encoding="utf-8") as summary:
            summary.write(text + "\n")
    except OSError as bad:
        print(
            f"note: the job summary {target} could not be written ({bad.strerror}); the run's verdict stands"
        )


def run_runner(root: Path, module: Module) -> dict[int, bool]:
    """The module's pytest tests: collected serially first, so that a stop of acceptance.collected is
    read whole even where the run is parallel; then run, under coverage.py when kit_coverage asks for it,
    with `-n <value>` when the environment's CONSTITUTION_KIT_JOBS names one; then each item's result
    read from the JUnit report. pytest exit 0 is green and 1 a run with red items; any other exit, a
    report that does not hold to itself, or an exit that disagrees with the report, could not run."""
    jobs = os.environ.get(JOBS_ENV, "").strip()
    needed = ["pytest", *(["xdist"] if jobs else [])]
    missing = [package for package in needed if importlib.util.find_spec(package) is None]
    if missing:
        named = ["pytest", *(["pytest-xdist"] if jobs else [])]
        raise Broken(
            f"{' and '.join(missing)} not installed for {sys.executable}, and the tests of {module.name}"
            f" run under pytest{f' with -n {jobs}' if jobs else ''} — fix: {pins(*named)}"
        )
    base = [f"modules/{module.name}/tests", "-p", "no:cacheprovider", "-W", "error", "-q"]
    collect = subprocess.run(
        [sys.executable, "-m", "pytest", *base, "--collect-only"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=RUNNER_TIMEOUT,
        check=False,
    )
    if collect.returncode != 0:
        echo(module, collect)
        raise Broken(
            f"pytest could not collect the tests of {module.name} (exit {collect.returncode}):"
            f" {last_words(collect)} — fix: run python3 -m pytest modules/{module.name}/tests -W error"
            " --collect-only and repair what it names"
        )
    with tempfile.TemporaryDirectory(prefix="aspects-junit-") as scratch:
        report = Path(scratch) / "report.xml"
        command = ["-m", "pytest", *base, f"--junitxml={report}", *(["-n", jobs] if jobs else [])]
        done, lost = run_once(root, module, command)
        if done.returncode != 0:
            echo(module, done)
        if lost is not None:
            raise Broken(lost)
        if done.returncode not in (0, PYTEST_RED):
            raise Broken(
                f"the runner of {module.name} exited {done.returncode}: {last_words(done)} — fix: run"
                f" python3 -m pytest modules/{module.name}/tests -W error and repair what it names"
            )
        results = read_report(report, module.name)
        write_summary(module.name, report_rows(report))
    if (done.returncode == 0) != all(results.values()):
        raise Broken(
            f"the runner of {module.name} exited {done.returncode} against its own report — fix: run"
            f" python3 -m pytest modules/{module.name}/tests -W error"
        )
    return results


def typed_count(lines: list[tuple[int, str]]) -> tuple[int, int] | None:
    """The first line of section 10, outside code fences, that opens with `Runner:` and holds
    `<digits> items green`: its line number and the number; None when the section has no such line,
    the count being optional."""
    fence = ""  # the opening run of a fence, while one is open
    for number, raw in lines:
        marker = FENCE.match(raw)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = ""
            continue
        if marker and not (marker[1][0] == "`" and "`" in marker[2]):
            fence = marker[1]
            continue
        found = RUNNER_COUNT.search(raw) if raw.startswith("Runner:") else None
        if found:
            return number, int(found[1])
    return None


def count_finding(module: Module, total: int) -> Finding | None:
    """The finding for a count typed on the Runner line of the module's section 10 that is not the
    runner's total `total`; None when the line holds no count or the count is the total."""
    typed = typed_count(module.acceptance)
    if typed is None or typed[1] == total:
        return None
    line, written = typed
    return Finding(
        module.path,
        line,
        f"the Runner line of section 10 says {written} items green, and the runner's total is {total}",
        WHY_COUNT,
        f"write the runner's total on the Runner line of section 10: change `{written} items green` to"
        f" `{total} items green`",
    )


def advisory_only(enforcement: str) -> bool:
    """An advisory row, as the matrix classes it: the cell opens with `advisory` and names no gate."""
    text = enforcement.lower()  # a word, so that "ungateable" is no gate and "gate-lite" is one
    return re.match(r"advisory\b", text) is not None and not re.search(r"\bgates?\b", text)


def verdict(items: list[Item], advisory: bool = False) -> str:
    outcomes = [i.outcome() for i in items]
    if "red" in outcomes:
        return "red"
    if "green" in outcomes:
        return "carrier green" if advisory else "green"
    labels: list[str] = []
    for item in items:
        if item.outcome() is None and item.label() not in labels:
            labels.append(item.label())
    return " + ".join(labels) if labels else "no item"


def item_line(item: Item) -> str:
    outcome = item.outcome()
    if outcome and item.kind == "eval":
        result = f"{outcome} (receipt of {item.eval_day})"
    elif outcome:
        result = f"{outcome} ({len(item.numbers)} run)"
    else:
        result = "not read" if item.kind == "fixture" else "not run"
    kind = item.kind if item.kind == "fixture" else item.label()
    return f"      {item.module} {item.handles}: {kind} — {result}"


def attach_results(module: Module, results: dict[int, bool], findings: list[Finding]) -> None:
    """Give each item the results of the numbers it names; a number the runner did not report, and a runner
    item no item names, are findings."""
    named: set[int] = set()
    for item in module.items:
        for n in item.numbers:
            named.add(n)
            if n in results:
                item.results[n] = results[n]
            else:
                findings.append(
                    Finding(
                        module.path,
                        item.line,
                        f"item {item.handles} names runner item {n}, which the runner did not report",
                        WHY_RUN,
                        "remove the number from the item cell, or restore the item in the runner",
                    )
                )
    for n in sorted(set(results) - named):
        findings.append(
            Finding(
                module.path,
                0,
                f"runner item {n} is named by no acceptance item",
                WHY_RUN,
                "add its number to the item cell that proves the same thing, or a new item",
            )
        )


def attach_evals(root: Path, module: Module) -> None:
    """Give each eval item of the module the result of the module's receipt, read once: green where the
    receipt is current (its hash the module's eval hash now, its Claude Code the pinned one, its model the
    pinned one) and its last attempt passes, red where it is current and the last attempt does not, else
    `stale`, no result. A module with no eval item reads nothing; a read that fails is no pass."""
    items = [i for i in module.items if i.kind == "eval"]
    if not items:
        return
    try:
        now, claude, model = eval_hash(root, module.name), pinned_claude(root), eval_model(root)
        receipt = read_receipts(root).get(module.name)
    except (DocumentError, EvalError) as bad:
        raise Broken(f"the eval items of {module.name} cannot be judged: {bad}") from bad
    if (
        receipt is None
        or not receipt.attempts
        or (receipt.hash, receipt.claude, receipt.model)
        != (
            now,
            claude,
            model,
        )
    ):
        for item in items:
            item.eval_state = "stale"
        return
    last = receipt.attempts[-1]
    for item in items:
        item.eval_state = "green" if last.passing else "red"
        item.eval_day = last.at.partition("T")[0]


def run_modules(
    root: Path,
    modules: list[Module],
    findings: list[Finding],
    runner: Callable[[Path, Module], dict[int, bool]],
) -> int:
    """Run each module's runner and hold its items to the results; the number of runner items read."""
    read_items = 0
    for module in modules:
        results = runner(root, module)
        read_items += len(results)
        mismatch = count_finding(module, len(results))  # read_report held len(results) to the report's counts
        if mismatch is not None:
            findings.append(mismatch)
        attach_results(module, results, findings)
        attach_evals(root, module)
    return read_items


def print_rows(
    matrix: dict[str, Row], modules: list[Module], only: str | None
) -> tuple[dict[str, int], bool]:
    """Print each row with its verdict and items; the tally of verdicts, and whether one is red."""
    tally: dict[str, int] = {}
    red = False
    aspect = None
    for row in matrix.values():
        if row.aspect != aspect:
            aspect = row.aspect
            print(aspect)
        items = [i for m in modules for i in m.items if row.anchor in i.rows]
        holders = [m for m in modules if row.anchor in m.held]
        if holders:
            v = verdict(items, advisory_only(row.enforcement))
            who = ", ".join(f"{m.name} {m.version}" for m in holders)
            print(f"  {row.handle}  {v} — {row.destination} — {who}")
            for item in items:
                print(item_line(item))
        elif only is None:
            v = "no module"
            print(f"  {row.handle}  held by {row.destination} — {row.enforcement}")
        else:
            continue
        red = red or v == "red"
        tally[v] = tally.get(v, 0) + 1
    return tally, red


def print_loose(modules: list[Module]) -> bool:
    """Print each module's items that prove no row; whether one of them is red."""
    red = False
    for module in modules:
        loose = [i for i in module.items if not i.rows]
        if loose:
            print(f"{module.name} — items that prove no row")
            for item in loose:
                print(item_line(item))
                red = red or item.outcome() == "red"
    return red


def full_run(
    root: Path, only: str | None, runner: Callable[[Path, Module], dict[int, bool]] = run_runner
) -> int:
    matrix, modules, findings, shared = check_structure(root, only)
    read_items = run_modules(root, modules, findings, runner)
    tally, red = print_rows(matrix, modules, only)
    red = print_loose(modules) or red
    summary = "; ".join(f"{n} {v}" for v, n in sorted(tally.items(), key=lambda kv: -kv[1]))
    runs = f"{read_items} runner item(s) read from {len(modules)} runner(s)"
    for finding in findings:
        print(finding.render())
    if findings or red:
        print(
            f"RED: {len(findings)} finding(s), {'a red item' if red else 'no red item'} — {summary}"
            f" — {counts(matrix, modules, shared)}; {runs}"
        )
        return EXIT_RED
    print(f"GREEN: every item read is green — {summary} — {counts(matrix, modules, shared)}; {runs}")
    return EXIT_GREEN


def gate(root: Path) -> int:
    matrix, modules, findings, shared = check_structure(root)
    for finding in findings:
        print(finding.render())
    if findings:
        print(f"RED: {len(findings)} finding(s) — {counts(matrix, modules, shared)}")
        return EXIT_RED
    print(
        "GREEN: every acceptance item names its rows, and every row a module holds has an item"
        f" — {counts(matrix, modules, shared)}"
    )
    return EXIT_GREEN


# --- self-test ---------------------------------------------------------------------------------

# The preamble's sentence as the requirements document writes it, a period inside a code span of it;
# the paragraph's first bold span stands before it and a sentence follows it.
PREAMBLE = (
    "**Traceability matrix** — every aspect decomposed into requirement parts. Destination classes:"
    " **kernel §n** (shared semantics), **Mx** (module, with artifact kind), **binding** (per-project"
    " `constitution.yaml` — never module content), **template** (authoring law). An authoring session"
    " for module X takes exactly its rows."
)
MATRIX = f"""# R
{PREAMBLE}
| Part | Requirement | Destination | Recommended enforcement |
|---|---|---|---|
| <a id="a1"></a>**A1 — Sample** | | | |
| <a id="a1-1"></a>A1.1 | one | M1 hook | **gate** |
| <a id="a1-2"></a>A1.2 | two | [kernel §2](constitution/CONVENTIONS.md#k2) | definitional — through A1.1 |
| <a id="a1-3"></a>A1.3 | three | M1 skill | advisory |
"""
LINK_1 = "[A1.1](../../docs/requirements.md#a1-1)"
LINK_3 = "[A1.3](../../docs/requirements.md#a1-3)"


def module_text(acceptance: str, rows: str = f"| {LINK_1} | r |\n| {LINK_3} | r |\n") -> str:
    return (
        '<a id="t3"></a>\n## 3. Rows\n\n| row | this module\'s reading |\n|---|---|\n'
        + rows
        + '\n<a id="t4"></a>\n## 4\n\n<a id="t10"></a>\n## 10. Acceptance\n\n'
        + acceptance
        + '\n<a id="t11"></a>\n## 11\n\n<a id="t12"></a>\n## 12\n'
    )


GOOD_TABLE = (
    "| item | kind | rows | what it proves |\n|---|---|---|---|\n"
    f"| T1–T2 | fixture, red→green | {LINK_1} | the gate |\n"
    "| T3 | fixture, assertion | none | the hooks file |\n"
    f"| S101 | fixture, shared | {LINK_1} | shared |\n"
    f"| L1 | live | {LINK_3} | done 2026-09-01, a live run |\n"
    f"| L2 | review | {LINK_1}, {LINK_3} | the pairs |\n"
)


def echoed(out: str, code: int, said: str = "") -> bool:
    """A runner that exited other than 0 has its whole output printed under one header, `said` among
    the lines after it; a green one prints nothing of its own."""
    header = f"the runner of const-sample exited {code}; its output, as it printed it:"
    printed = out.splitlines()
    if code == 0:
        return "the runner of const-sample exited" not in out
    if header not in printed:
        return False
    return any(said in line for line in printed[printed.index(header) + 1 :])


SAMPLE_ITEMS = ((1, "a"), (2, "b"), (3, "c"), (101, "s"))  # the sample module's items: number, title


def entries(*numbers: int) -> list[str]:
    """The shared tests, one for each number, each `@item(<n>, "item <n>")`: in `shared_source` each takes
    five lines, the two blank ones after it included, so the marker of the k-th, from 0, stands on line
    4 + 5k of the file."""
    return [f'@item({n}, "item {n}")\ndef test_{n}(subject):\n    pass\n' for n in numbers]


def shared_source(tests: list[str], head: str = "", tail: str = "") -> str:
    """A shared test file: `head`, the import of the marker, the tests, then `tail`."""
    body = "".join(f"{test}\n\n" for test in tests)
    return f"{head}from .acceptance import item\n\n\n{body}{tail}"


def gate_text(rows: list[str], after: str = "") -> str:
    """GATE.md as the check reads it: a handle before the anchor, which is read by no one, then the
    section of the anchor `g5` with one table row per entry of `rows`, then `after`."""
    table = "".join(f"| {row} | proves |\n" for row in rows)
    return (
        "# Gate\n\n## 1. Earlier\n\nan old handle S900–S999, S5, read by no one.\n\n"
        f"{SHARED_ANCHOR}\n## 5. Shared acceptance items\n\nprose.\n\n| item | what it proves |\n|---|---|\n"
        f"{table}| K1 | kit check, not in the list |\n\nclosing prose.\n{after}"
    )


SHARED_GOOD = shared_source(entries(101, 102, 103))
GATE_GOOD = gate_text(["S101–S102", "S103"])


def build(
    root: Path,
    table: str,
    rows: str | None = None,
    matrix: str = MATRIX,
    shared: str = SHARED_GOOD,
    gate: str = GATE_GOOD,
) -> None:
    (root / SHARED_TESTS).parent.mkdir(parents=True, exist_ok=True)
    for init in (root / SHARED_TESTS).parents[:2]:
        (init / "__init__.py").write_text("", encoding="utf-8")
    (root / SHARED_TESTS).write_text(shared, encoding="utf-8")
    (root / SHARED_GATE).write_text(gate, encoding="utf-8")
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / SPEC).write_text(matrix, encoding="utf-8")
    module = root / "modules" / "const-sample"
    (module / "plugin" / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (module / "plugin" / ".claude-plugin" / "plugin.json").write_text(
        '{"name": "const-sample", "version": "0.0.1"}\n', encoding="utf-8"
    )
    text = module_text(table) if rows is None else module_text(table, rows)
    (module / "MODULE.md").write_text(text, encoding="utf-8")
    sample_module(root)


WHY_NUMBERS_TYPED = (
    "an item's number is never reissued (rule 4 of docs/policies/plc-0009-shared-code.md), so the shared"
    " tests hold each number once, in rising order from 101, and the tables that name an item by its number"
    " keep naming the same item"
)
WHY_TABLE_TYPED = (
    "the table of shared/ITEMS.md is where the kit says what each shared item proves, so every"
    " number it names must be an item the shared tests hold"
)
FIX_FOLLOWS_TYPED = (
    "give a new item a number no item has had, at the end of the file, and put a moved item back in its"
    " place; a removed item's number is never given again"
)


def shared_follows(number: int, before: int) -> str:
    return f"the shared item numbered {number} follows {before}, and the numbers are not unique and rising"


def shared_names(text: str, names: str) -> str:
    return f"the range {text} names {names}, which the shared tests do not hold"


@dataclass
class Tally:
    """The cases a self-test group has run and the ones that failed."""

    failed: int = 0
    total: int = 0

    def record(self, ok: bool) -> None:
        """Count one case, failed unless `ok`."""
        self.failed += 0 if ok else 1
        self.total += 1


N64 = entries(*range(101, 165))


def shared_green(tally: Tally) -> None:
    """The cases where the numbers and the table of ITEMS.md read green."""
    n64 = N64
    green: dict[str, tuple[list[str], str, int]] = {  # case: the entries, the GATE.md text, items read
        "101 to 164 in the file's order": (n64, gate_text(["S101–S164"]), 64),
        "101 to 164 with a hyphen range": (n64, gate_text(["S101-S164"]), 64),
        "a gap kept rising, 101 and 103": (entries(101, 103), gate_text(["S101", "S103"]), 2),
        "steps of more than one": (entries(101, 105, 164), gate_text(["S101", "S105", "S164"]), 3),
        "one item, 101": (entries(101), gate_text(["S101"]), 1),
        "rows of the table in no order": (entries(101, 102, 103), gate_text(["S103", "S101–S102"]), 3),
        "a number of the list that no row names (completeness is not asked)": (
            entries(101, 102, 103),
            gate_text(["S101", "S103"]),
            3,
        ),
        "a name that merely ends in S, a dotted name and a word after a handle": (
            entries(101, 102),
            gate_text(["S101–S102", "CAS170", "x.S171", "S172x", "K164"]),
            2,
        ),
        "a handle in another section, before the anchor": (entries(101), gate_text(["S101"]), 1),
        "a handle on the last line, held": (entries(101, 102), gate_text(["S101"], "S102"), 2),
    }
    for name, (tests, doc, items_read) in green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, shared=shared_source(tests), gate=doc)
            found, read_count = check_shared(root)
        ok = not found and read_count == items_read
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] shared items: {name} is green, {items_read} read")
        if not ok:
            print(f"        got: {[f.render() for f in found]}, {read_count} read")


def shared_decoys(tally: Tally) -> None:
    """The cases where a number stands where the check must not read it."""
    good = entries(101, 102, 103)
    decoys = {  # case: the shared test file, a number standing where the check must not read it
        "a call of item(…) that marks no test, out of order": shared_source(
            good, tail='LATER = [item(103, "x"), item(102, "y")]\n'
        ),
        "a marker on a function inside a function, out of order": shared_source(
            good, tail='def helper():\n    @item(103, "x")\n    def inner():\n        pass\n'
        ),
        "a marker on a method of a class, out of order": shared_source(
            good, tail='class Later:\n    @item(103, "x")\n    def test_x(self):\n        pass\n'
        ),
        "another decorator's numbers beside item(…), out of order": shared_source(good).replace(
            '@item(101, "item 101")\n', '@item(101, "item 101")\n@other(103, "x")\n@other(102, "y")\n'
        ),
        "a marker inside a string, out of order": shared_source(good, head='"""@item(103, "x")"""\n'),
    }
    for name, source in decoys.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, shared=source)
            found, read_count = check_shared(root)
        ok = not found and read_count == 3
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] shared items: {name} is not read, the tests' own markers are")


def shared_red_data() -> dict[str, tuple[list[str], str, list[tuple[str, str]]]]:
    """The red cases of the shared items: the entries, the GATE.md text, what each finding says and the text
    of the line that each names."""
    n64 = N64
    red: dict[str, tuple[list[str], str, list[tuple[str, str]]]] = {
        "a swap, 102 after 103": (
            entries(101, 103, 102),
            gate_text(["S101–S103"]),
            [(shared_follows(102, 103), "(102,")],
        ),
        "a duplicate, 102 after 102": (
            entries(101, 102, 102),
            gate_text(["S101–S102"]),
            [(shared_follows(102, 102), "(102,")],
        ),
        "a list that starts at 102": (
            entries(102, 103),
            gate_text(["S102–S103"]),
            [("the first shared item is numbered 102, not 101", "(102,")],
        ),
        "a list that starts at 100": (
            entries(100, 101),
            gate_text(["S100–S101"]),
            [("the first shared item is numbered 100, not 101", "(100,")],
        ),
        "a reversed list": (
            entries(103, 102, 101),
            gate_text(["S101–S103"]),
            [
                ("the first shared item is numbered 103, not 101", "(103,"),
                (shared_follows(102, 103), "(102,"),
                (shared_follows(101, 102), "(101,"),
            ],
        ),
        "two swaps apart, 103 after 105 and 102 after 104": (
            entries(101, 105, 103, 104, 102),
            gate_text(["S101–S105"]),
            [(shared_follows(103, 105), "(103,"), (shared_follows(102, 104), "(102,")],
        ),
        "the last two of 64 swapped": (
            [*entries(*range(101, 163)), *entries(164, 163)],
            gate_text(["S101–S164"]),
            [(shared_follows(163, 164), "(163,")],
        ),
        "a range naming 165": (
            n64,
            gate_text(["S101–S165"]),
            [(shared_names("S101–S165", "S165"), "S101–S165")],
        ),
        "a hyphen range naming 165": (
            n64,
            gate_text(["S101-S165"]),
            [(shared_names("S101-S165", "S165"), "S101-S165")],
        ),
        "a single handle S170": (
            n64,
            gate_text(["S101–S164", "S170"]),
            [("the handle S170 names an item the shared tests do not hold", "| S170 |")],
        ),
        "a range whose end is below its start": (
            n64,
            gate_text(["S110–S101"]),
            [("the range S110–S101 ends at or below its start", "S110–S101")],
        ),
        "a hyphen range whose end is below its start": (
            n64,
            gate_text(["S110-S101"]),
            [("the range S110-S101 ends at or below its start", "S110-S101")],
        ),
        "a range that ends where it starts": (
            n64,
            gate_text(["S110–S110"]),
            [("the range S110–S110 ends at or below its start", "S110–S110")],
        ),
        "a range that starts below the list": (
            entries(101, 102),
            gate_text(["S100–S102"]),
            [(shared_names("S100–S102", "S100"), "S100–S102")],
        ),
        "a range across a gap": (
            entries(101, 103),
            gate_text(["S101–S103"]),
            [(shared_names("S101–S103", "S102"), "S101–S103")],
        ),
        "a range that names more numbers than the finding shows": (
            n64,
            gate_text(["S101–S175"]),
            [(shared_names("S101–S175", "S165, S166, S167, S168, S169 and 6 more"), "S101–S175")],
        ),
        "a range of exactly five missing numbers": (
            n64,
            gate_text(["S101–S169"]),
            [(shared_names("S101–S169", "S165, S166, S167, S168, S169"), "S101–S169")],
        ),
        "a handle on the last line of the file, no anchor after it": (
            n64,
            gate_text(["S101–S164"], "S170"),
            [("the handle S170 names an item the shared tests do not hold", "S170")],
        ),
        "a handle after another anchor, read to the end of the page": (
            n64,
            gate_text(["S101–S164"], '<a id="g6"></a>\n## 6. Later\n\nS170 and S101.\n'),
            [("the handle S170 names an item the shared tests do not hold", "S170")],
        ),
        "a handle after an indented anchor, read to the end of the page": (
            n64,
            gate_text(["S101–S164"], '   <a id="g6"></a>\nS170\n'),
            [("the handle S170 names an item the shared tests do not hold", "S170")],
        ),
        "the anchor g5 indented by spaces and followed by spaces, its handles read": (
            n64,
            gate_text(["S101–S164"], "S170\n").replace(SHARED_ANCHOR, f"   {SHARED_ANCHOR}   "),
            [("the handle S170 names an item the shared tests do not hold", "S170")],
        ),
        "the anchor g5 after a tab, its handles read": (
            n64,
            gate_text(["S101–S164"], "S170\n").replace(SHARED_ANCHOR, f"\t{SHARED_ANCHOR}"),
            [("the handle S170 names an item the shared tests do not hold", "S170")],
        ),
        "a swap and a range naming 104 together": (
            entries(101, 103, 102),
            gate_text(["S101–S104"]),
            [(shared_follows(102, 103), "(102,"), (shared_names("S101–S104", "S104"), "S101–S104")],
        ),
        "a handle in a code span and in bold": (
            entries(101),
            gate_text(["`S101`, **S102**, `S103–S104`"]),
            [
                ("the handle S102 names an item the shared tests do not hold", "**S102**"),
                (shared_names("S103–S104", "S103, S104"), "`S103–S104`"),
            ],
        ),
    }
    return red


def sample_results(root: Path, module: Module) -> dict[int, bool]:
    """The sample module's items, each green, read without a run: for the cases that hold what a run
    prints of the shared items, not what its runner does."""
    return {number: True for number, _ in SAMPLE_ITEMS}


def shared_red(tally: Tally) -> None:
    """The cases where the numbers or the table of the shared items are red, each finding on its line."""
    for name, (tests, doc, wanted) in shared_red_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, shared=shared_source(tests), gate=doc)
            found, _ = check_shared(root)
            _, _, structure, _ = check_structure(root)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = full_run(root, "const-sample", sample_results)
        sources = {
            SHARED_TESTS: shared_source(tests).splitlines(),
            SHARED_GATE: doc.splitlines(),
        }
        ok = [f.what for f in found] == [what for what, _ in wanted] and structure == found
        ok = ok and len(found) == len(wanted)
        for finding, (_, at) in zip(found, wanted, strict=False):
            ok = ok and finding.path in sources and finding.line > 0
            ok = ok and at in sources[finding.path][finding.line - 1]
            ok = ok and finding.why in (WHY_NUMBERS_TYPED, WHY_TABLE_TYPED)
            ok = ok and bool(finding.fix)
        ok = ok and code == EXIT_RED and all(f.render() in printed.getvalue() for f in found)
        tally.record(ok)
        print(
            f"[{'ok' if ok else 'FAIL'}] shared items: {name} is red with {len(wanted)} finding(s),"
            " each on its line, in the plain run and in the run of one module"
        )
        if not ok:
            print(f"        got: {[(f.path, f.line, f.what) for f in found]}")


def shared_starts(tally: Tally) -> None:
    """The whole set of numbers the shared tests can start with and be red."""
    for start in (0, 1, 100, 102, 164):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, shared=shared_source(entries(start, start + 1)), gate=gate_text(["S101"]))
            found, _ = check_shared(root)
        starts = [f for f in found if f.what.startswith("the first shared item")]
        ok = len(starts) == 1 and starts[0].what == f"the first shared item is numbered {start}, not 101"
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] shared items: numbers that start at {start} are red")


def shared_steps(tally: Tally) -> None:
    """The steps of the shared numbers that make them red at one place."""
    for before, after in ((101, 101), (102, 101), (164, 163), (110, 109), (110, 110)):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(
                root,
                GOOD_TABLE,
                shared=shared_source(entries(*range(101, before + 1), after)),
                gate=gate_text([f"S101–S{before}" if before > 101 else "S101"]),
            )
            found, _ = check_shared(root)
        ok = [f.what for f in found] == [shared_follows(after, before)]
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] shared items: {after} after {before} is the one red step")


def shared_broken_data() -> dict[str, tuple[str | None, str | None, str]]:
    """The cases of a file or a form the check cannot read: the shared test file, the GATE.md text, what the
    BROKEN line says; a text of None is the file's own good one."""
    anchor_words = f"{SHARED_GATE} holds the anchor {SHARED_ANCHOR}"
    nowhere = f"{anchor_words} nowhere on a line of its own — why: "
    reading = "— why: the check reads the numbers of the shared tests from their markers"
    none_marked = f"{SHARED_TESTS} holds no test marked `@item(<number>, …)` {reading}"
    bad_marker = f"{SHARED_TESTS}:14: a marker `item(…)` opens with no int literal {reading}"
    bad_markers: dict[str, str] = {  # case: the bad marker; each on a test after two good ones, line 14
        "no argument": "@item()",
        "a string number": '@item("101", "t")',
        "a float number": '@item(101.0, "t")',
        "a boolean number": '@item(True, "t")',
        "a negative number": '@item(-1, "t")',
        "a number given by a sum": '@item(100 + 1, "t")',
        "a number given by a name": '@item(FIRST, "t")',
        "a number given by keyword": '@item(number=101, title="t")',
        "a number that is no first argument": '@item("t", 101)',
        "a starred argument": "@item(*more)",
    }
    broken: dict[str, tuple[str | None, str | None, str]] = {
        "a syntax error in the shared test file": (
            "def test_x(:\n",
            None,
            f"{SHARED_TESTS} cannot be parsed (",
        ),
        "no marked test": ("def test_x(subject):\n    pass\n", None, none_marked),
        "an empty shared test file": ("", None, none_marked),
        "markers on the methods of a class only": (
            "class TestK:\n    @item(101, 'a')\n    def test_x(self):\n        pass\n",
            None,
            none_marked,
        ),
        "markers on a function inside a test only": (
            "def test_x(subject):\n    @item(101, 'a')\n    def inner():\n        pass\n",
            None,
            none_marked,
        ),
        "the anchor g5 missing": (None, GATE_GOOD.replace(SHARED_ANCHOR + "\n", ""), nowhere),
        "the anchor g5 renamed g4": (None, GATE_GOOD.replace("g5", "g4"), nowhere),
        "the anchor g5 written in prose, not alone": (
            None,
            GATE_GOOD.replace(SHARED_ANCHOR + "\n", f"see {SHARED_ANCHOR} here\n"),
            nowhere,
        ),
        "the anchor g5 twice": (
            None,
            GATE_GOOD.replace("prose.\n", f"prose.\n{SHARED_ANCHOR}\n", 1),
            f"{anchor_words} twice — why: ",
        ),
    }
    for case, marker in bad_markers.items():
        broken[f"a marker with {case}"] = (
            shared_source(
                [*entries(101, 102), f"{marker}\ndef test_bad(subject):\n    pass\n", *entries(104)]
            ),
            None,
            bad_marker,
        )
    broken["an unnumbered marker in tests also out of order, BROKEN and no RED"] = (
        shared_source([*entries(103, 101), "@item()\ndef test_bad(subject):\n    pass\n"]),
        gate_text(["S101–S190"]),
        bad_marker,
    )
    broken["a bad GATE.md anchor beside numbers out of order, BROKEN and no RED"] = (
        shared_source(entries(103, 101)),
        GATE_GOOD.replace(SHARED_ANCHOR + "\n", ""),
        nowhere,
    )
    return broken


def shared_broken(tally: Tally) -> None:
    """The cases where the shared items cannot be read, as one BROKEN line each."""
    for name, (shared_text, gate_text_or_none, said) in shared_broken_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shared = SHARED_GOOD if shared_text is None else shared_text
            build(
                root,
                GOOD_TABLE,
                shared=shared,
                gate=GATE_GOOD if gate_text_or_none is None else gate_text_or_none,
            )
            ok = True
            got: list[str] = []
            for only in (None, "const-sample"):
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        if only is None:
                            check_structure(root)
                        else:
                            full_run(root, only)
                    ok = False
                    got.append("no BROKEN")
                except Broken as bad:
                    ok = ok and str(bad).startswith(said) and "— fix: " in str(bad)
                    got.append(str(bad))
        tally.record(ok)
        print(
            f"[{'ok' if ok else 'FAIL'}] shared items: {name} is one BROKEN line naming it,"
            " in the plain run and in the run of one module"
        )
        if not ok:
            print(f"        got: {got}")


def shared_dropped(tally: Tally) -> None:
    """The cases where a file of the shared items is gone from the tree."""
    drop = {  # case: the file taken from the tree
        "the shared test file missing": (SHARED_TESTS, f"{SHARED_TESTS} cannot be read"),
        "GATE.md missing": (SHARED_GATE, f"{SHARED_GATE} cannot be read"),
    }
    for name, (gone, said) in drop.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            (root / gone).unlink()
            ok = True
            for only in (None, "const-sample"):
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        if only is None:
                            check_structure(root)
                        else:
                            full_run(root, only)
                    ok = False
                except Broken as bad:
                    ok = ok and str(bad).startswith(said) and "— fix: " in str(bad)
        tally.record(ok)
        print(
            f"[{'ok' if ok else 'FAIL'}] shared items: {name} is one BROKEN line naming it,"
            " in the plain run and in the run of one module"
        )


def shared_literal_data() -> dict[str, tuple[str, str, list[str]]]:
    """The reports of the shared items as literal lines: the shared test file, the GATE.md text, the lines
    printed."""
    n64 = N64
    literal = {  # typed by hand: a message function cannot check itself
        "a swap": (
            shared_source(entries(101, 103, 102)),
            gate_text(["S101–S103"]),
            [
                "RED: shared/constitution_layer_kit/testing/items.py:14: the shared item numbered 102"
                " follows 103, and the numbers are not unique and rising",
                f"  why: {WHY_NUMBERS_TYPED}",
                f"  fix: {FIX_FOLLOWS_TYPED}",
                "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s)"
                " examined, 3 shared item(s)",
            ],
        ),
        "a start above 101": (
            shared_source(entries(102, 103)),
            gate_text(["S102–S103"]),
            [
                "RED: shared/constitution_layer_kit/testing/items.py:4: the first shared item"
                " is numbered 102, not 101",
                f"  why: {WHY_NUMBERS_TYPED}",
                "  fix: number the first item 101, and give a new item a number no item has had, at the end"
                " of the file",
                "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s)"
                " examined, 2 shared item(s)",
            ],
        ),
        "a range naming 165": (
            shared_source(n64),
            gate_text(["S101–S165"]),
            [
                "RED: shared/ITEMS.md:14: the range S101–S165 names S165, which the shared tests do not hold",
                f"  why: {WHY_TABLE_TYPED}",
                "  fix: change the range to numbers shared/constitution_layer_kit/testing/items.py"
                " holds, or give the item that number in its marker",
                "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s)"
                " examined, 64 shared item(s)",
            ],
        ),
        "a handle S170": (
            shared_source(n64),
            gate_text(["S101–S164", "S170"]),
            [
                "RED: shared/ITEMS.md:15: the handle S170 names an item the shared tests do not hold",
                f"  why: {WHY_TABLE_TYPED}",
                "  fix: change the handle to numbers shared/constitution_layer_kit/testing/items.py"
                " holds, or give the item that number in its marker",
                "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s)"
                " examined, 64 shared item(s)",
            ],
        ),
        "a range that ends below its start": (
            shared_source(n64),
            gate_text(["S110–S101"]),
            [
                "RED: shared/ITEMS.md:14: the range S110–S101 ends at or below its start",
                f"  why: {WHY_TABLE_TYPED}",
                "  fix: write one handle for one item, or a range with its lower number first, `S<n>–S<m>`",
                "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s)"
                " examined, 64 shared item(s)",
            ],
        ),
    }
    return literal


def shared_literal(tally: Tally) -> None:
    """The cases where the report of a shared finding is its literal text, exit 2."""
    for name, (source, doc, want_lines) in shared_literal_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, shared=source, gate=doc)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = gate(root)
        ok = code == EXIT_RED and printed.getvalue().splitlines() == want_lines
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] shared items: the report of {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())


def shared_counts(tally: Tally) -> None:
    """The case where the green lines of the gate and of a full run say how many shared items were read."""
    with tempfile.TemporaryDirectory() as tmp:  # the green line, and the full run's, say how many were read
        root = Path(tmp).resolve()
        build(root, GOOD_TABLE)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = gate(root)
        full = io.StringIO()
        with contextlib.redirect_stdout(full):
            full_code = full_run(root, None)
    ok = code == EXIT_GREEN and printed.getvalue().splitlines() == [
        "GREEN: every acceptance item names its rows, and every row a module holds has an item"
        " — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s) examined, 3 shared item(s)"
    ]
    ok = ok and full_code == EXIT_GREEN and ", 3 shared item(s); " in full.getvalue().splitlines()[-1]
    tally.record(ok)
    print(
        f"[{'ok' if ok else 'FAIL'}] shared items: the green lines of the gate and of a full run count them"
    )


def self_test_shared() -> tuple[int, int]:
    """The shared acceptance items, over their whole set of cases, each on a throwaway tree: the numbers
    of the markers green and red (a swap, a duplicate, a start above 101, the numbers reversed, two swaps
    apart, the last two of 64), the table of ITEMS.md green and red (a range, a handle, a hyphen
    range, a range that ends at its start, more missing numbers than are named, a section read to the
    end of the file, another section not read), a file or a form it cannot read as a BROKEN line in the
    plain run and in the run of one module, and the report as literal lines. Returns (failed, total)."""
    tally = Tally()
    shared_green(tally)
    shared_decoys(tally)
    shared_red(tally)
    shared_starts(tally)
    shared_steps(tally)
    shared_broken(tally)
    shared_dropped(tally)
    shared_literal(tally)
    shared_counts(tally)
    return tally.failed, tally.total


@contextlib.contextmanager
def listed_in_reverse() -> Iterator[None]:
    """For the cases inside, `Path.iterdir` yields its entries sorted by name and reversed, whatever the
    filesystem lists: a case that holds an order is then red on every filesystem for a check that does not
    sort, never by the chance of a listing that happens to be unsorted. Restored on leaving."""
    real = Path.iterdir

    def reversed_iterdir(self: Path) -> Iterator[Path]:
        return iter(sorted(real(self), key=lambda path: path.name, reverse=True))

    Path.iterdir = reversed_iterdir  # type: ignore[method-assign,assignment]
    try:
        yield
    finally:
        Path.iterdir = real  # type: ignore[method-assign]


def main_over(root: Path, argv: list[str]) -> tuple[int, list[str]]:
    """`main` as the command line runs it, over the tree `root` for the kit: its exit and the lines it
    printed."""
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = main(argv, root)
    return code, printed.getvalue().splitlines()


ACCEPTANCE_GATE = (  # a fake gate: MODE decides whether it blocks the text it is handed
    "import json, sys\n"
    "text = json.load(sys.stdin)['tool_input'].get('content', '')\n"
    "red = {'right': 'RED-TEXT' in text, 'always-pass': False, 'always-block': True}[MODE]\n"
    "if red:\n"
    "    sys.stderr.write('RED: doc.md: a red text\\n  why: a fixture\\n  fix: take it out\\n'\n"
    "                     'RED: 1 finding(s) — 1 document examined (doc.md)\\n')\n"
    "    sys.exit(2)\n"
    "print('GREEN: const-sample: 1 document examined, a covered document')\n"
)
ACCEPTANCE_CONFTEST = (
    "import pytest\nfrom constitution_layer_kit.testing import acceptance\n\n\n"
    "def pytest_configure(config: pytest.Config) -> None:\n    acceptance.configure(config)\n\n\n"
    "def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:\n    acceptance.collected(items)\n"
)
ACCEPTANCE_TESTS = (
    "from enum import StrEnum\nfrom pathlib import Path\n\nimport pytest\n"
    "from constitution_layer_kit.model import Finding\n"
    "from constitution_layer_kit.testing.acceptance import check_case, item\n"
    "from constitution_layer_kit.testing.harness import Case, Harness, Write\n\n\n"
    "class Key(StrEnum):\n    X1 = 'X1'\n\n\n"
    "H = Harness(Path(__file__).resolve().parent.parent / 'plugin' / 'scripts',\n"
    "            'gate.sh', 'gate.py', 'const-sample')\n"
    "CASE = Case(1, 'a red text', Write('doc.md', 'RED-TEXT\\n'), Write('doc.md', 'fine\\n'),\n"
    "            Finding(Key.X1, 'doc.md: a red text', 'a fixture', 'take it out'),\n"
    "            'a covered document')\n\n\n"
    "@pytest.mark.parametrize('case', [pytest.param(CASE, id='T1', marks=item(1, CASE.title))])\n"
    "def test_case(case: Case) -> None:\n    check_case(H, case)\n"
)


def acceptance_tree(root: Path, mode: str, extra: str = "") -> Path:
    """A throwaway module whose tests use the kit's own shared test files, linked: the fake gate in
    `mode`, one red→green case, and `extra` appended to its test file. The tests folder."""
    module = root / "modules" / "const-sample"
    scripts = module / "plugin" / "scripts"
    tests = module / "tests"
    scripts.mkdir(parents=True)
    tests.mkdir()
    (scripts / "gate.sh").write_text('exec python3 "$(dirname "$0")/gate.py"\n', encoding="utf-8")
    (scripts / "gate.py").write_text(f"MODE = {mode!r}\n{ACCEPTANCE_GATE}", encoding="utf-8")
    (tests / "constitution_layer_kit").symlink_to(KIT / "shared" / "constitution_layer_kit")
    (tests / "conftest.py").write_text(ACCEPTANCE_CONFTEST, encoding="utf-8")
    (tests / "test_sample.py").write_text(ACCEPTANCE_TESTS + extra, encoding="utf-8")
    return tests


def acceptance_cases() -> dict[str, tuple[str, str, list[str], int, list[str]]]:
    """case: the gate's mode, what the test file adds, pytest's extra arguments, the exit, the texts
    the output must hold."""
    doubled = "\n\n@item(1, 'again')\ndef test_again() -> None:\n    pass\n"
    unmarked = "\n\ndef test_unmarked() -> None:\n    pass\n"
    checks = (  # expect and broken_first_line on the results RUN, EXIT and FIRST, typed after them
        "\n\nfrom constitution_layer_kit.testing.acceptance import broken_first_line, expect\n"
        "from constitution_layer_kit.testing.harness import Result\n\n\n"
        "@item(2, 'expect')\ndef test_expect() -> None:\n"
        "    expect(RUN, 2, 'RED: x', 'stderr', label='case a')\n    expect(EXIT, 2, 'RED: x')\n\n\n"
        "@item(3, 'first line')\ndef test_first() -> None:\n    broken_first_line(FIRST, 'BROKEN: a')\n"
    )
    shown = (
        "RUN = Result(2, '', 'RED: x\\n')\nEXIT = Result(2, 'RED: x\\n', '')\n"
        "FIRST = Result(1, '', 'BROKEN: a\\nBROKEN: b\\n')\n"
    )
    return {  # typed by hand: the messages of check_case, expect, broken_first_line and acceptance.collected
        "a gate that does both halves right: the case is green": ("right", "", [], 0, ["1 passed"]),
        "a gate that always passes: check_case is red on the red half": (
            "always-pass",
            "",
            [],
            1,
            ["red half exited 0, not 2"],
        ),
        "a gate that always blocks: check_case is red on the green half": (
            "always-block",
            "",
            [],
            1,
            ["green half did not print 'GREEN: const-sample: 1 document examined, a covered document'"],
        ),
        "expect and broken_first_line on runs that show what they ask: green": (
            "right",
            checks + shown,
            [],
            0,
            ["3 passed"],
        ),
        "expect on its text on the other stream: red, its label first": (
            "right",
            checks + shown.replace("RUN = Result(2, '', 'RED: x\\n')", "RUN = Result(2, 'RED: x\\n', '')"),
            [],
            1,
            ["case a: wanted exit 2 teaching 'RED: x'; got exit 2:", "1 failed, 2 passed"],
        ),
        "expect on another exit: red": (
            "right",
            checks + shown.replace("EXIT = Result(2,", "EXIT = Result(0,"),
            [],
            1,
            ["wanted exit 2 teaching 'RED: x'; got exit 0: RED: x", "1 failed, 2 passed"],
        ),
        "broken_first_line on another first line, and on another exit: red": (
            "right",
            checks
            + shown.replace("'BROKEN: a\\nBROKEN: b", "'BROKEN: b\\nBROKEN: a")
            + "\n\n@item(4, 'exit')\ndef test_exit() -> None:\n"
            "    broken_first_line(Result(2, '', 'BROKEN: a\\n'), 'BROKEN: a')\n",
            [],
            1,
            [
                "wanted exit 1 with first line 'BROKEN: a'; got exit 1: BROKEN: b",
                "wanted exit 1 with first line 'BROKEN: a'; got exit 2: BROKEN: a",
                "2 failed, 2 passed",
            ],
        ),
        "a test without item(…): the run stops before any test": (
            "right",
            unmarked,
            [],
            4,
            [
                "test_sample.py::test_unmarked carries no item(<number>, <title>) — why: a test outside the"
                " acceptance table is examined by no row — fix: give it @item(<number>, <title>) from"
                " acceptance",
                "no tests ran",
            ],
        ),
        "a number two tests carry: the run stops before any test, the fix naming the module's file": (
            "right",
            doubled,
            [],
            4,
            [
                "item number 1 is carried by 2 items, 'a red text', 'again' — why: one number, one item, or a"
                " result and a node id cannot say which item they mean — fix: keep one of them at 1, and in"
                " the module's own tests/test_sample.py give the other one the number 2 — a number no other"
                " item holds, below 101",
                "no tests ran",
            ],
        ),
        "a number two tests carry, run with -n 2: xdist's internal error, never green": (
            "right",
            doubled,
            ["-n", "2"],
            3,
            ["no tests ran"],
        ),
    }


def case_acceptance(tally: Tally) -> None:
    """The shared pytest wiring, `acceptance`, on a throwaway module that links the kit's own shared test
    files: check_case red on either half of a gate that always answers the same, the run stopped on a
    test without a number and on a number two tests carry — serially with the lines, with xdist as its
    internal error — and the number handed to the JUnit report."""
    missing = [name for name in ("pytest", "xdist") if importlib.util.find_spec(name) is None]
    if missing:
        tally.record(False)
        print(
            f"[FAIL] acceptance: {', '.join(missing)} not installed — fix: {pins('pytest', 'pytest-xdist')}"
        )
        return
    for name, (mode, extra, args, code, said) in acceptance_cases().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            tests = acceptance_tree(root, mode, extra)
            report = root / "report.xml"
            done = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(tests),
                    "-p",
                    "no:cacheprovider",
                    "-W",
                    "error",
                    "-q",
                    f"--junitxml={report}",
                    *args,
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
                timeout=RUNNER_TIMEOUT,
            )
            out = done.stdout + done.stderr
            ok = done.returncode == code and all(text in out for text in said)
            if code == 0:  # the green run: the item's number in the report, as the property `item`
                ok = ok and '<property name="item" value="1" />' in report.read_text(encoding="utf-8")
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] acceptance: {name}")
        if not ok:
            print(f"        exit {done.returncode}, wanted {code}: {out.strip()[-800:]}")


COVERED_GATE = "import sys\nif len(sys.argv) > 5:\n    print('many')\nprint('gate')\n"


def sample_tests(
    root: Path,
    red: tuple[int, ...] = (),
    extra: str = "",
    conftest: str = ACCEPTANCE_CONFTEST,
    named: tuple[tuple[int, str], ...] = SAMPLE_ITEMS,
    module: str = "const-sample",
) -> None:
    """The sample module's conftest and its test file: one test for each of `named`, red where `red`
    names its number, item 2 running the module's gate as a child process; then `extra`."""
    tests = root / "modules" / module / "tests"
    (tests / "conftest.py").write_text(conftest, encoding="utf-8")
    body = "import subprocess\nfrom pathlib import Path\n\n"
    body += "from constitution_layer_kit.testing.acceptance import item\n\n"
    body += "ENTRY = Path(__file__).resolve().parent.parent / 'plugin' / 'scripts' / 'entry.sh'\n"
    seen: set[int] = set()
    for index, (number, title) in enumerate(named):
        name = f"test_{number}" if number not in seen else f"test_{number}_{index}"
        seen.add(number)
        run = "    subprocess.run(['sh', str(ENTRY)], check=True)\n" if number == 2 else ""
        head = f"\n\n@item({number}, {title!r})\ndef {name}() -> None:\n"
        body += f"{head}{run}    assert {number not in red}\n"
    (tests / "test_sample.py").write_text(body + extra, encoding="utf-8")


def sample_module(root: Path, module: str = "const-sample") -> None:
    """The sample module's scripts and tests: a gate one item runs and a file no item runs, the kit's own
    shared package linked, which holds the shared test files, and the items of SAMPLE_ITEMS, each green."""
    folder = root / "modules" / module
    tests = folder / "tests"
    scripts = folder / "plugin" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    tests.mkdir(exist_ok=True)
    (scripts / "entry.sh").write_text('exec python3 "$(dirname "$0")/gate.py"\n', encoding="utf-8")
    (scripts / "gate.py").write_text(COVERED_GATE, encoding="utf-8")
    (scripts / "unused.py").write_text("print('never run')\n", encoding="utf-8")
    if not (tests / "constitution_layer_kit").is_symlink():
        (tests / "constitution_layer_kit").symlink_to(KIT / "shared" / "constitution_layer_kit")
    sample_tests(root, module=module)


def pytest_run_cases() -> dict[str, tuple[tuple[int, ...], str, str, str | None, int, list[str]]]:
    """case: the red items, what the test file adds, the conftest, CONSTITUTION_KIT_JOBS, the check's
    exit, the texts its output must hold."""
    exited = (  # a test that ends the run with an exit pytest never gives a verdict by
        "\n\n@item(7, 'x')\ndef test_exit() -> None:\n    import os\n\n    os._exit(3)\n"
    )
    against = (  # a conftest whose run, never its collection, exits 1 with every item green
        ACCEPTANCE_CONFTEST + "\n\ndef pytest_sessionfinish(session: pytest.Session) -> None:\n"
        "    if not session.config.getoption('collectonly'):\n        session.exitstatus = 1\n"
    )
    bare = (  # a conftest that registers the marker and hands no number to the report
        "import pytest\nfrom constitution_layer_kit.testing import acceptance\n\n\n"
        "def pytest_configure(config: pytest.Config) -> None:\n    acceptance.configure(config)\n"
    )
    doubled = "\n\n@item(3, 'again')\ndef test_again() -> None:\n    pass\n"
    green_row = "  A1.1  green — M1 hook — const-sample 0.0.1"
    header = "the runner of const-sample exited"
    return {  # typed by hand
        "pytest, every item green": ((), "", ACCEPTANCE_CONFTEST, None, EXIT_GREEN, [green_row]),
        "pytest with -n 2, every item green": ((), "", ACCEPTANCE_CONFTEST, "2", EXIT_GREEN, [green_row]),
        "pytest, item 2 red: the row red and pytest's output echoed": (
            (2,),
            "",
            ACCEPTANCE_CONFTEST,
            None,
            EXIT_RED,
            ["  A1.1  red — M1 hook — const-sample 0.0.1", f"{header} 1; its output, as it printed it:"],
        ),
        "pytest, a number two tests carry: could not collect, the lines echoed first": (
            (),
            doubled,
            ACCEPTANCE_CONFTEST,
            "2",
            EXIT_BROKEN,
            [
                f"{header} 4; its output, as it printed it:",
                "item number 3 is carried by 2 items",
                "BROKEN: pytest could not collect the tests of const-sample (exit 4)",
            ],
        ),
        "pytest, a conftest that hands no number to the report": (
            (),
            "",
            bare,
            None,
            EXIT_BROKEN,
            [
                "BROKEN: the test modules.const-sample.tests.test_sample::test_1 of const-sample carries 0",
                "fix: let the module's conftest call acceptance.collected from its"
                " pytest_collection_modifyitems",
            ],
        ),
        "pytest, a test file that does not parse: could not collect, the lines echoed first": (
            (),
            "\ndef broken(:\n",
            ACCEPTANCE_CONFTEST,
            None,
            EXIT_BROKEN,
            [
                f"{header} 2; its output, as it printed it:",
                "SyntaxError",
                "BROKEN: pytest could not collect the tests of const-sample (exit 2)",
                "fix: run python3 -m pytest modules/const-sample/tests -W error --collect-only and repair"
                " what it names",
            ],
        ),
        "pytest, an exit that is no verdict: the output echoed, then BROKEN": (
            (),
            exited,
            ACCEPTANCE_CONFTEST,
            None,
            EXIT_BROKEN,
            [
                f"{header} 3; its output, as it printed it:",
                "BROKEN: the runner of const-sample exited 3",
                "fix: run python3 -m pytest modules/const-sample/tests -W error and repair what it names",
            ],
        ),
        "pytest, an exit of 1 against a green report": (
            (),
            "",
            against,
            None,
            EXIT_BROKEN,
            [
                f"{header} 1; its output, as it printed it:",
                "BROKEN: the runner of const-sample exited 1 against its own report — fix: run python3 -m"
                " pytest modules/const-sample/tests -W error",
            ],
        ),
        "pytest, a skipped test: left out of the results, and no finding of an unnamed item": (
            (),
            "\n\nimport pytest\n\n\n@item(9, 'not this gate')\ndef test_skipped() -> None:\n"
            "    pytest.skip('not this gate')\n",
            ACCEPTANCE_CONFTEST,
            None,
            EXIT_GREEN,
            [green_row, "4 runner item(s) read from 1 runner(s)"],
        ),
        "pytest, a warning a test file gives: an error under -W error, could not collect": (
            (),
            "\n\nimport warnings\n\nwarnings.warn('a warning at import', UserWarning)\n",
            ACCEPTANCE_CONFTEST,
            None,
            EXIT_BROKEN,
            [
                "UserWarning: a warning at import",
                "BROKEN: pytest could not collect the tests of const-sample",
            ],
        ),
    }


def case_job_summary(tally: Tally) -> None:
    """With GITHUB_STEP_SUMMARY naming a file, a run appends its module's section, every test in number
    order with its result, as literal lines, a red run too; unset, it writes nothing; naming a folder, a
    note, the verdict standing."""
    skipped = (
        "\n\nimport pytest\n\n\n@item(9, 'not this gate')\ndef test_skipped() -> None:\n"
        "    pytest.skip('no')\n"
    )
    wanted = [  # typed by hand: the section of a run with item 2 red and item 9 skipped
        "### const-sample: 3 passed, 1 failed, 1 skipped",
        "",
        "| item | test | result |",
        "|---|---|---|",
        "| 1 | `test_1` | passed |",
        "| 2 | `test_2` | failed |",
        "| 3 | `test_3` | passed |",
        "| 9 | `test_skipped` | skipped |",
        "| 101 | `test_101` | passed |",
        "",
    ]
    for case, red, want in (
        ("a file", (2,), EXIT_RED),
        ("unset", (), EXIT_GREEN),
        ("a folder", (), EXIT_GREEN),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            sample_tests(root, red, skipped)
            target = root / ("summary.md" if case != "a folder" else "docs")
            if case != "unset":
                os.environ[SUMMARY_ENV] = str(target)
            try:
                code, lines = main_over(root, ["--run", "--module", "const-sample"])
            finally:
                os.environ.pop(SUMMARY_ENV, None)
            written = target.read_text(encoding="utf-8").split("\n") if target.is_file() else None
        if case == "a file":
            ok = code == want and written == [*wanted, ""]
        elif case == "unset":
            ok = code == want and written is None and not (root / "summary.md").exists()
        else:
            ok = code == want and any(line.startswith(f"note: the job summary {target}") for line in lines)
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] the job summary, its variable {case}: as the rule says")
        if not ok:
            print(f"        exit {code}: {written} {lines[-3:]}")


def missing_spec(
    package: str, real: Callable[[str, str | None], ModuleSpec | None], name: str, near: str | None = None
) -> ModuleSpec | None:
    """importlib.util.find_spec as it answers where `package` is not installed."""
    return None if name == package else real(name, near)


def case_pytest_runs(tally: Tally) -> None:
    """A full run of a module whose tests are pytest's: green, red, stopped at collection, run in
    parallel, a report without the numbers, and the libraries missing."""
    for name, (red, extra, conftest, jobs, want, needles) in pytest_run_cases().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            sample_tests(root, red, extra, conftest)
            saved = os.environ.pop(JOBS_ENV, None)
            if jobs is not None:
                os.environ[JOBS_ENV] = jobs
            try:
                code, lines = main_over(root, ["--run", "--module", "const-sample"])
            finally:
                os.environ.pop(JOBS_ENV, None)
                if saved is not None:
                    os.environ[JOBS_ENV] = saved
        out = "\n".join(lines)
        ok = code == want and all(needle in out for needle in needles)
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] a run of {name} exits {want} and says so")
        if not ok:
            print(f"        exit {code}: {out.strip()[-900:]}")
    for jobs in (None, "2"):  # the coverage mode, serial and in parallel: the gate a test runs is measured
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            folder = root / "coverage-out"
            os.environ[kit_coverage.ENV] = str(folder)
            if jobs is not None:
                os.environ[JOBS_ENV] = jobs
            try:
                code, lines = main_over(root, ["--run", "--module", "const-sample"])
            finally:
                os.environ.pop(kit_coverage.ENV, None)
                os.environ.pop(JOBS_ENV, None)
            written = folder / "const-sample.json"
            measured: dict[str, Any] = (
                json.loads(written.read_text(encoding="utf-8")) if written.is_file() else {}
            )
        files = measured.get("files", {})
        gate_file = files.get("modules/const-sample/plugin/scripts/gate.py", {})
        unused = files.get("modules/const-sample/plugin/scripts/unused.py", {})
        ok = (
            code == EXIT_GREEN
            and measured.get("runner_exit") == 0
            and gate_file.get("executed_lines") == [1, 2, 4]
            and unused.get("missing_lines") == [1]
        )
        tally.record(ok)
        parallel = " with -n 2" if jobs else ""
        print(f"[{'ok' if ok else 'FAIL'}] pytest's tests under coverage{parallel}: the gate measured")
        if not ok:
            print(f"        exit {code}: {measured or 'no file'} {lines[-5:]}")
    for package, jobs in (("pytest", None), ("xdist", "2")):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            real = importlib.util.find_spec
            importlib.util.find_spec = partial(missing_spec, package, real)
            os.environ.pop(JOBS_ENV, None)
            if jobs is not None:
                os.environ[JOBS_ENV] = jobs
            try:
                code, lines = main_over(root, ["--run", "--module", "const-sample"])
            finally:
                importlib.util.find_spec = real
                os.environ.pop(JOBS_ENV, None)
        out = "\n".join(lines)
        wanted = (
            f"BROKEN: {package} not installed for {sys.executable}, and the tests of const-sample run under"
        )
        ok = code == EXIT_BROKEN and wanted in out and "-m pip install" in out and '"pytest==' in out
        tally.record(ok)
        print(
            f"[{'ok' if ok else 'FAIL'}] a run of pytest's tests with {package} missing is BROKEN,"
            " naming the pin"
        )
        if not ok:
            print(f"        exit {code}: {out.strip()[-600:]}")


def self_test_coverage() -> tuple[int, int]:
    """The coverage mode of kit_coverage: with the variable set, a green run and a red one each write
    the module's file, the gate a child process ran counted as executed and a file no run imported
    as missed; with it unset, no file; with it naming a path where no folder can be made, a red run
    prints its runner's output and then the BROKEN line. The failed cases, and the cases."""
    cases = {  # case: the red items, pytest's exit, the variable (folder, unset or file), the exit
        "a green run under coverage writes the coverage file": ((), 0, "folder", EXIT_GREEN),
        "a red run under coverage writes the coverage file": ((3,), PYTEST_RED, "folder", EXIT_RED),
        "a run with the variable unset writes no coverage file": ((), 0, "unset", EXIT_GREEN),
        "a red run whose coverage file cannot be written prints its output, then BROKEN": (
            (3,),
            PYTEST_RED,
            "file",
            EXIT_BROKEN,
        ),
    }
    failed = 0
    for name, (red, runner_exit, variable, want) in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            sample_tests(root, red)
            out = root / "coverage-out"
            if variable == "file":
                out.write_text("a file where the folder would go\n", encoding="utf-8")
            if variable != "unset":
                os.environ[kit_coverage.ENV] = str(out)
            printed = io.StringIO()
            reason = ""
            try:
                with contextlib.redirect_stdout(printed):
                    code = full_run(root, None)
            except Broken as why:
                code, reason = EXIT_BROKEN, str(why)
            finally:
                os.environ.pop(kit_coverage.ENV, None)
            written = out / "const-sample.json"
            ok = code == want and written.is_file() == (variable == "folder")
            if ok and variable == "file":
                ok = echoed(printed.getvalue(), runner_exit, "FAILED") and "cannot be written" in reason
            if ok and variable == "folder":
                saved = json.loads(written.read_text(encoding="utf-8"))
                files = saved["files"]
                gate_file = files.get("modules/const-sample/plugin/scripts/gate.py", {})
                unused = files.get("modules/const-sample/plugin/scripts/unused.py", {})
                ok = (
                    saved["runner_exit"] == runner_exit
                    and gate_file.get("executed_lines") == [1, 2, 4]
                    and gate_file.get("missing_lines") == [3]
                    and gate_file.get("missing_branches") == [[2, 3]]
                    and unused.get("executed_lines") == []
                    and unused.get("missing_lines") == [1]
                )
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"exit {code}\n{printed.getvalue()}{reason}")
    return failed, len(cases)


TABLE_HEAD = "| item | kind | rows | what it proves |\n|---|---|---|---|\n"
RED_TABLES: dict[str, tuple[str, str | None]] = {  # case: its table (or rows section), what the finding says
    "no rows column": (
        "| item | kind | what it proves |\n|---|---|---|\n| T1 | fixture | x |\n",
        "no `rows` column",
    ),
    "an open range": (
        GOOD_TABLE + f"| S101– | fixture, shared | {LINK_1} | s |\n",
        "not a list of handles",
    ),
    "prose in the item cell": (
        GOOD_TABLE + f"| S101–S158 less seven | fixture | {LINK_1} | s |\n",
        "not a list of handles",
    ),
    "a kind outside the set": (GOOD_TABLE + f"| T9 | probe | {LINK_1} | x |\n", "is none of the set"),
    "a kind that is a longer word": (
        GOOD_TABLE + f"| T9 | fixtures | {LINK_1} | x |\n",
        "is none of the set",
    ),
    "a live handle as a fixture": (GOOD_TABLE + f"| L3 | fixture | {LINK_1} | x |\n", "no runner number"),
    "an empty rows cell": (GOOD_TABLE + "| T9 | fixture |  | x |\n", "the rows cell of item T9"),
    "a bare handle in the rows cell": (
        GOOD_TABLE + "| T9 | fixture | A1.1 | x |\n",
        "the rows cell of item T9",
    ),
    "none beside a link": (
        GOOD_TABLE + f"| T9 | fixture | none, {LINK_1} | x |\n",
        "the rows cell of item T9",
    ),
    "a row the matrix does not hold": (
        GOOD_TABLE + "| T9 | fixture | [A1.9](../../docs/requirements.md#a1-9) | x |\n",
        "a row the matrix does not hold",
    ),
    "a row the module does not hold": (
        GOOD_TABLE + "| T9 | fixture | [A1.2](../../docs/requirements.md#a1-2) | x |\n",
        "does not hold",
    ),
    "a held row no item names": (
        TABLE_HEAD + f"| T1 | fixture | {LINK_1} | x |\n",
        "named by no acceptance item",
    ),
    "an indented item whose rows cell is no link": (
        GOOD_TABLE + "  | T9 | fixture | A1.1 | x |\n",
        "the rows cell of item T9",
    ),
}


def case_red_tables(tally: Tally) -> None:
    """Each finding of the gate: red with its table broken one way, green with the good table."""
    for name, (table, said) in RED_TABLES.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            green_before = not check_structure(root)[2]
            build(root, table)
            findings = check_structure(root)[2]
        ok = green_before and len(findings) == 1 and said is not None and said in findings[0].what
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] the good table is green, {name} is red with one finding")


def case_unheld_row(tally: Tally) -> None:
    """The case where a row the matrix gives a module, and no rows section holds, is red."""
    with tempfile.TemporaryDirectory() as tmp:  # a module row no module holds
        root = Path(tmp).resolve()
        build(root, TABLE_HEAD + f"| T1 | fixture | {LINK_1} | x |\n", rows=f"| {LINK_1} | r |\n")
        findings = check_structure(root)[2]
    ok = (
        len(findings) == 1
        and findings[0].what == "A1.3 is given to a module, and no module's rows section holds it"
    )
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] a row the matrix gives a module that no rows section holds is red")


DESTINATIONS = {  # the whole set of openings: the cell, whether the check classes it
    "M1 hook": True,
    "M47 skill + hook": True,
    "**M1** skill": True,
    "[kernel §2](constitution/CONVENTIONS.md#k2)": True,
    "kernel §12": True,
    "[kernel §2](constitution/CONVENTIONS.md#k2) + template": True,
    "binding": True,
    "binding (thresholds)": True,
    "template": True,
    "module `const-x` skill": False,
    "kernel": False,
    "kernel §": False,
    "kernel §n": False,
    "kernel§2": False,  # a space is part of the class, `kernel §`
    "M 1 hook": False,  # so is the number's place: `M` directly before its digits
    "kernel §2x": False,  # the class ends at a word boundary: a digit run that goes on in letters is none
    "Mx": False,
    "M": False,
    "m1": False,
    "M1x": False,
    "bindings": False,
    "templates": False,
    "Template": False,
    "": False,
    "—": False,
    "K2": False,
    "M١ hook": False,  # an Arabic-Indic digit, not an ASCII one
    "kernel §٢": False,
}


def case_destinations(tally: Tally) -> None:
    """Each opening of a destination cell: classed, or red as one the check cannot class."""
    for cell, classed in DESTINATIONS.items():
        seen: list[list[str]] = []
        for old in ("M1 hook", "[kernel §2](constitution/CONVENTIONS.md#k2)"):
            with tempfile.TemporaryDirectory() as tmp:  # A1.1 a module holds, A1.2 none holds
                root = Path(tmp).resolve()
                build(root, GOOD_TABLE, matrix=MATRIX.replace(f"| {old} |", f"| {cell} |"))
                seen.append([f.what for f in check_structure(root)[2]])
        on_held, on_unheld = seen
        refused = f"has the destination '{cell.replace('**', '')}', a destination the check cannot class"
        given = ["A1.2 is given to a module, and no module's rows section holds it"]
        if classed:  # a row given to a module that no module holds stays red beside it (R7)
            ok = not on_held and on_unheld == (
                given if cell in ("M1 hook", "M47 skill + hook", "**M1** skill") else []
            )
        else:
            # R7's own red (MODULE_DEST, read as before, takes any digit) is held by its case above
            unheld_red = [what for what in on_unheld if what != given[0]]
            ok = on_held == [f"A1.1 {refused}"] and unheld_red == [f"A1.2 {refused}"]
        tally.record(ok)
        print(
            f"[{'ok' if ok else 'FAIL'}] the destination '{cell}' is"
            f" {'classed' if classed else 'red as one the check cannot class'},"
            " on a row a module holds and on one none holds"
        )
        if not ok:
            print(f"        got: {seen}")


def case_indented_rows(tally: Tally) -> None:
    """The case where an indented table line is read whatever its indent."""
    with tempfile.TemporaryDirectory() as tmp:  # a table line is read whatever its indent
        root = Path(tmp).resolve()
        indented_rows = f"  | {LINK_1} | r |\n\t|{LINK_3} | r |\n"  # the second row: no space after the bar
        build(
            root,
            GOOD_TABLE + f"  | T9 | fixture | {LINK_1} | x |\n\t|T8 | fixture | {LINK_1} | x |\n",
            rows=indented_rows,
        )
        _, modules, findings, _ = check_structure(root)
    ok = not findings and len(modules[0].items) == 7 and sorted(modules[0].held.values()) == [6, 7]
    tally.record(ok)
    print(
        f"[{'ok' if ok else 'FAIL'}] an indented row of the rows section and an indented acceptance item,"
        " each also with no space after the bar, are read, never dropped"
    )


def case_unclosed_rows(tally: Tally) -> None:
    """The case where the last cell is read when a line has no closing bar."""
    with tempfile.TemporaryDirectory() as tmp:  # the last cell is read when the line has no closing bar
        root = Path(tmp).resolve()
        unclosed_rows = f"| {LINK_1} | r\n| {LINK_3}\n"  # the second row is one cell, `| link`
        build(root, GOOD_TABLE + f"| T7 | fixture | {LINK_1} | x\n", rows=unclosed_rows)
        _, modules, findings, _ = check_structure(root)
    ok = not findings and len(modules[0].items) == 6 and sorted(modules[0].held.values()) == [6, 7]
    tally.record(ok)
    print(
        f"[{'ok' if ok else 'FAIL'}] a row of the rows section and an acceptance item with no closing bar"
        " are read to their last cell, never dropped or short of one"
    )


def case_open_ended_section(tally: Tally) -> None:
    """The case where a section with no anchor above it reads to the end of the document."""
    with tempfile.TemporaryDirectory() as tmp:  # no anchor stands above the last one: it reads to the end
        root = Path(tmp).resolve()
        build(root, GOOD_TABLE)
        module_file = root / "modules" / "const-sample" / "MODULE.md"
        text_now = module_file.read_text(encoding="utf-8").replace('<a id="t12"></a>\n', "")
        module_file.write_text(text_now, encoding="utf-8")
        findings = check_structure(root)[2]
        module_file.write_text(
            text_now[: text_now.index('<a id="t11"></a>')], encoding="utf-8"
        )  # t11, t12 gone
        findings += check_structure(root)[2]
    ok = not findings
    tally.record(ok)
    print(
        f"[{'ok' if ok else 'FAIL'}] a document without its t12 anchor, or without t11 and t12, is read:"
        " the acceptance section reads to the end when no anchor stands above it"
    )


def case_sections_reordered(tally: Tally) -> None:
    """The case where sections t10 and t11 trade places, and the fix the BROKEN line gives restores them."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        build(root, GOOD_TABLE)
        module_file = root / "modules" / "const-sample" / "MODULE.md"
        original = module_file.read_text(encoding="utf-8")
        blocks: list[list[str]] = [[]]  # the document cut before each section anchor
        for line in original.splitlines(keepends=True):
            if re.fullmatch(r'<a id="t\d+"></a>', line.strip()):
                blocks.append([])
            blocks[-1].append(line)
        names = [block[0].strip() for block in blocks[1:]]
        at10, at11 = names.index('<a id="t10"></a>') + 1, names.index('<a id="t11"></a>') + 1
        blocks[at10], blocks[at11] = blocks[at11], blocks[at10]  # the sections t11 and t10 trade places
        module_file.write_text("".join("".join(block) for block in blocks), encoding="utf-8")
        try:
            check_structure(root)
            before = None
        except Broken as bad:
            before = str(bad)
        blocks[1:] = sorted(blocks[1:], key=lambda block: int(re.findall(r"\d+", block[0])[0]))  # the fix
        module_file.write_text("".join("".join(block) for block in blocks), encoding="utf-8")
        ok = before is not None and "the anchor after" in before and not check_structure(root)[2]
        ok = ok and module_file.read_text(encoding="utf-8") == original
    tally.record(ok)
    print(
        f"[{'ok' if ok else 'FAIL'}] a document whose t11 section stands before t10, put in the template's"
        " order as the fix says, is read"
    )


def unreadable_anchors() -> dict[str, tuple[str, str, str]]:
    """The module documents whose section anchors are missing, doubled or out of order."""
    path = "modules/const-sample/MODULE.md"
    text = module_text(GOOD_TABLE)
    unreadable = {  # case: the document, its text, what the BROKEN line says
        "no t3 anchor": (
            path,
            text.replace('<a id="t3"></a>\n', ""),
            f'{path} has no anchor <a id="t3"></a>',
        ),
        "no t10 anchor": (
            path,
            text.replace('<a id="t10"></a>\n', ""),
            f'{path} has no anchor <a id="t10"></a>',
        ),
        "no t4 anchor, t10 standing after it": (
            path,
            text.replace('<a id="t4"></a>\n', ""),
            f'{path} has no anchor <a id="t4"></a> after <a id="t3"></a>',
        ),
        "no t11 anchor, t12 standing after it": (
            path,
            text.replace('<a id="t11"></a>\n', ""),
            f'{path} has no anchor <a id="t11"></a> after <a id="t10"></a>',
        ),
        "the t11 anchor before the t10 anchor": (
            path,
            text.replace('<a id="t10"></a>\n', "@@")
            .replace('<a id="t11"></a>\n', '<a id="t10"></a>\n')
            .replace("@@", '<a id="t11"></a>\n'),
            f'{path}: the anchor after <a id="t10"></a> is <a id="t12"></a>, not <a id="t11"></a> — fix: put'
            " the sections in the template's order, t1 to t12, each anchor alone on the line above its"
            " section's heading",
        ),
        "the t10 anchor last, t11 standing before it": (
            path,
            text.replace('<a id="t10"></a>\n', "") + '<a id="t10"></a>\n',
            f'{path}: no anchor follows <a id="t10"></a>, and <a id="t11"></a> stands before it — fix: put'
            " the sections in the template's order, t1 to t12",
        ),
        "text on the line of the t10 anchor": (
            path,
            text.replace('<a id="t10"></a>\n## 10.', '## 10. <a id="t10"></a>'),
            f'{path} has no anchor <a id="t10"></a>',
        ),
        "a t3 anchor twice": (
            path,
            text.replace("| row |", '<a id="t3"></a>\n| row |'),
            f'{path} holds the anchor <a id="t3"></a> twice, lines 1 and 4',
        ),
        "a second t4 anchor inside the rows section": (
            path,
            text.replace(f"| {LINK_3} |", f'<a id="t4"></a>\n| {LINK_3} |'),
            f'{path} holds the anchor <a id="t4"></a> twice, lines 7 and 10',
        ),
    }
    return unreadable


# the matrix, line 6 the row A1.1 (a module holds it), line 7 the row A1.2 (none does), line 5 the
# aspect: every way its line can leave the form `ROW` or `ASPECT` states, each on both rows
ROW_LINE = {1: MATRIX.splitlines()[5], 2: MATRIX.splitlines()[6]}
ASPECT_LINE = MATRIX.splitlines()[4]


def unreadable_matrix_lines() -> dict[str, tuple[str, str, str]]:
    """The matrix with a row or an aspect line off its form or doubled; a module folder with no document."""
    unreadable: dict[str, tuple[str, str, str]] = {}
    row_line, aspect_line = ROW_LINE, ASPECT_LINE
    row_forms: dict[str, Callable[[str, int], str]] = {  # case: the line's edit
        "a space after the anchor": lambda x, n: x.replace(f'"></a>A1.{n}', f'"></a> A1.{n}'),
        "no space after the first pipe": lambda x, n: x.replace("| <a", "|<a", 1),
        "an indent of one space": lambda x, n: f" {x}",
        "a tab indent": lambda x, n: f"\t{x}",
        "a linked handle": lambda x, n: x.replace(f"A1.{n} |", f"[A1.{n}](#a1-{n}) |", 1),
        "a bold handle": lambda x, n: x.replace(f"A1.{n} |", f"**A1.{n}** |", 1),
        "no space before the pipe after the handle": lambda x, n: x.replace(f"A1.{n} |", f"A1.{n}|", 1),
        "the handle before the anchor": lambda x, n: x.replace(
            f'<a id="a1-{n}"></a>A1.{n}', f'A1.{n} <a id="a1-{n}"></a>'
        ),
    }
    for form, edit in row_forms.items():
        for n, line in row_line.items():
            unreadable[f"A1.{n}'s line with {form}"] = (
                SPEC,
                MATRIX.replace(line, edit(line, n)),
                f'{SPEC}:{n + 5}: the line holds a row\'s anchor <a id="a1-{n}"></a> but is not in the'
                " matrix's form",
            )
    aspect_forms = {
        "a space after the anchor": aspect_line.replace("></a>**", "></a> **"),
        "no space after the first pipe": aspect_line.replace("| <a", "|<a", 1),
        "an indent": f"  {aspect_line}",
        "no bold": aspect_line.replace("**", ""),
        "a bold left open": aspect_line.replace("Sample**", "Sample"),
    }
    for form, edited in aspect_forms.items():
        unreadable[f"the aspect line with {form}"] = (
            SPEC,
            MATRIX.replace(aspect_line, edited),
            f"{SPEC}:5: the line holds an aspect's anchor <a id=\"a1\"></a> but is not in the matrix's form",
        )
    unreadable["a row anchor on two lines"] = (
        SPEC,
        MATRIX + row_line[2] + "\n",
        f'{SPEC} holds the anchor <a id="a1-2"></a> twice, lines 7 and 9',
    )
    unreadable["a row anchor on two lines, a row a module holds"] = (
        SPEC,
        MATRIX.replace(row_line[1], row_line[1] + "\n" + row_line[1]),
        f'{SPEC} holds the anchor <a id="a1-1"></a> twice, lines 6 and 7',
    )
    unreadable["an aspect anchor on two lines"] = (
        SPEC,
        MATRIX + aspect_line + "\n",
        f'{SPEC} holds the anchor <a id="a1"></a> twice, lines 5 and 9',
    )
    unreadable["a row anchor on two lines, under two handles"] = (
        SPEC,
        MATRIX + row_line[2].replace("A1.2", "A1.5") + "\n",
        f'{SPEC} holds the anchor <a id="a1-2"></a> twice, lines 7 and 9',
    )
    unreadable["a row anchor on two lines, a row a module holds, under two handles"] = (
        SPEC,
        MATRIX.replace(row_line[1], row_line[1] + "\n" + row_line[1].replace("A1.1", "A1.5")),
        f'{SPEC} holds the anchor <a id="a1-1"></a> twice, lines 6 and 7',
    )
    unreadable["an aspect anchor on two lines, under two titles"] = (
        SPEC,
        MATRIX + aspect_line.replace("Sample", "Other") + "\n",
        f'{SPEC} holds the anchor <a id="a1"></a> twice, lines 5 and 9',
    )
    unreadable["a prose line that quotes a row's anchor"] = (
        SPEC,
        MATRIX + 'The form is `<a id="a1-1"></a>A1.1`.\n',
        f"{SPEC}:9: the line holds a row's anchor <a id=\"a1-1\"></a> but is not in the matrix's form",
    )
    unreadable["a prose line that quotes an aspect's anchor"] = (
        SPEC,
        MATRIX + 'The form is `<a id="a1"></a>**A1 — Sample**`.\n',
        f"{SPEC}:9: the line holds an aspect's anchor <a id=\"a1\"></a> but is not in the matrix's form",
    )
    unreadable["a folder of modules/ with no MODULE.md"] = (
        "modules/const-empty/README.md",
        "a folder with no module document\n",
        "modules/const-empty has no MODULE.md — fix: restore the module document",
    )
    return unreadable


MANIFEST_PATH = "modules/const-sample/plugin/.claude-plugin/plugin.json"
MANIFEST_FIX = "— fix: restore it as a JSON object"


def unreadable_manifests() -> dict[str, tuple[str, str, str]]:
    """The manifests that are valid JSON and no object, or no JSON."""
    unreadable: dict[str, tuple[str, str, str]] = {}
    manifest_path, manifest_fix = MANIFEST_PATH, MANIFEST_FIX
    for kind, manifest_text in (("a list", "[]\n"), ("a str", '"const-sample"\n'), ("a NoneType", "null\n")):
        unreadable[f"a manifest that is valid JSON and no object, it holds {kind}"] = (
            manifest_path,
            manifest_text,
            f"{manifest_path} is no JSON object, it holds {kind} {manifest_fix}",
        )
    unreadable["a manifest that is no JSON"] = (  # the line the check always gave
        manifest_path,
        "{not json\n",
        f"{manifest_path} cannot be read (Expecting property name enclosed in double quotes: line 1 column 2"
        " (char 1)) — fix: restore the manifest",
    )
    return unreadable


CLASSES_TEXT = PREAMBLE[PREAMBLE.index(CLASSES_SENTENCE) : PREAMBLE.index(" An authoring")]


def preamble_as(edited: str) -> str:
    """The matrix with its preamble replaced by `edited`."""
    return MATRIX.replace(PREAMBLE, edited)


def unreadable_preamble() -> dict[str, tuple[str, str, str]]:
    """The matrix with the preamble's sentence of classes missing, reworded or off the typed four."""
    unreadable: dict[str, tuple[str, str, str]] = {}
    classes_text = CLASSES_TEXT
    typed_names = "'Mx', 'binding', 'kernel §n', 'template'"
    names_found = f'{SPEC} names the destination classes %s in its "Destination classes:" sentence, and this'
    unreadable["the preamble's classes sentence missing"] = (
        SPEC,
        preamble_as(PREAMBLE.replace(classes_text, "")),
        f'{SPEC} holds no sentence that opens "Destination classes:" — why: the check types the classes'
        f" {typed_names} and holds them to the preamble's sentence, so a preamble it cannot read is a tie"
        " it cannot check — fix: restore the sentence in the preamble, or change the preamble and the"
        " check's classes together",
    )
    unreadable["the preamble's classes sentence reworded"] = (
        SPEC,
        preamble_as(PREAMBLE.replace(CLASSES_SENTENCE, "Destination kinds:")),
        f'{SPEC} holds no sentence that opens "Destination classes:" — why: ',
    )
    unreadable["a fifth bold class in the preamble's sentence"] = (
        SPEC,
        preamble_as(PREAMBLE.replace("(authoring law).", "(authoring law), **extra** (a fifth).")),
        names_found % "'Mx', 'binding', 'extra', 'kernel §n', 'template'",
    )
    unreadable["one of the four renamed in the preamble"] = (
        SPEC,
        preamble_as(PREAMBLE.replace("**Mx**", "**Mn**")),
        f"{SPEC} names the destination classes 'Mn', 'binding', 'kernel §n', 'template' in its \"Destination"
        f' classes:" sentence, and this check types {typed_names} — why: the classes are a closed set'
        " defined once in the preamble (rule 7 of plc-0007-requirements), and the check's patterns are"
        " typed here, so the two must say the same names — fix: change the preamble and the check's"
        " classes together",
    )
    unreadable["one of the four missing from the preamble"] = (
        SPEC,
        preamble_as(PREAMBLE.replace(", **template** (authoring law)", "")),
        names_found % "'Mx', 'binding', 'kernel §n'",
    )
    unreadable["a class of the preamble not in bold"] = (
        SPEC,
        preamble_as(PREAMBLE.replace("**binding**", "binding")),
        names_found % "'Mx', 'kernel §n', 'template'",
    )
    return unreadable


def case_unreadable(tally: Tally) -> None:
    """Each tree the check cannot read is one BROKEN line naming it, in the plain run and in a module's."""
    unreadable = {
        **unreadable_anchors(),
        **unreadable_matrix_lines(),
        **unreadable_manifests(),
        **unreadable_preamble(),
    }
    fix_forms = {  # the fix of an off-form line names the form of its own kind, never the other's
        "A1.1's line with a space after the anchor": 'write it as `| <a id="aN-M"></a>AN.M | …`',
        "A1.2's line with a tab indent": 'write it as `| <a id="aN-M"></a>AN.M | …`',
        "the aspect line with a space after the anchor": 'write it as `| <a id="aN"></a>**AN — Title**`',
        "the aspect line with an indent": 'write it as `| <a id="aN"></a>**AN — Title**`',
    }
    for name, (document, broken_text, said) in unreadable.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            (root / document).parent.mkdir(parents=True, exist_ok=True)
            (root / document).write_text(broken_text, encoding="utf-8")
            ok = True
            got: list[str] = []
            for only in (None, "const-sample"):  # the plain run's reading, and the full run of one module
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        if only is None:
                            check_structure(root)
                        else:
                            full_run(root, only)
                    ok = False
                    got.append("no BROKEN" if only is None else "no BROKEN under --module")
                except Broken as bad:
                    ok = ok and str(bad).startswith(said) and "— fix:" in str(bad)
                    ok = ok and (name not in fix_forms or f"— fix: {fix_forms[name]}" in str(bad))
                    got.append(str(bad))
                except (AttributeError, TypeError) as crash:  # a traceback is a case that fails, not the run
                    ok = False
                    got.append(f"{type(crash).__name__}: {crash}")
        tally.record(ok)
        print(
            f"[{'ok' if ok else 'FAIL'}] a kit tree with {name} is one BROKEN line naming it,"
            " in the plain run and in the run of one module"
        )
        if not ok:
            print(f"        got: {got}")


def case_manifest_commands(tally: Tally) -> None:
    """A manifest that is no JSON object is one BROKEN line and the could-not-run line, under each command."""
    manifest_path, manifest_fix = MANIFEST_PATH, MANIFEST_FIX
    command_lines: tuple[list[str], ...] = ([], ["--run"], ["--run", "--module", "const-sample"])
    for kind, manifest_text in (("a list", "[]\n"), ("a str", '"const-sample"\n')):
        for command_line in command_lines:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                build(root, GOOD_TABLE)
                (root / manifest_path).write_text(manifest_text, encoding="utf-8")
                try:
                    code, main_lines = main_over(root, command_line)
                except (AttributeError, TypeError) as crash:  # a traceback is a case that fails, not the run
                    code, main_lines = -1, [f"{type(crash).__name__}: {crash}"]
            expected = [
                f"BROKEN: {manifest_path} is no JSON object, it holds {kind} {manifest_fix}",
                "BROKEN: the check could not run — 0 rows examined",
            ]
            ok = code == EXIT_BROKEN and main_lines == expected
            tally.record(ok)
            print(
                f"[{'ok' if ok else 'FAIL'}] a manifest that holds {kind} is one BROKEN line and the"
                f" could-not-run line, exit 1, under `{' '.join(command_line) or 'no argument'}`"
            )
            if not ok:
                print(f"        got: {code} {main_lines}")


def case_manifest_versions(tally: Tally) -> None:
    """A manifest object is read with its version as text, or with `?` when it holds none."""
    version_read = {  # case: the manifest's text; the version the module is read with
        "a manifest object without a version is read with the version ?": ('{"name": "const-sample"}\n', "?"),
        "a manifest object with a numeric version is read with it as text": ('{"version": 3}\n', "3"),
        "a manifest object with a string version is read with it": ('{"version": "0.0.2"}\n', "0.0.2"),
    }
    for name, (manifest_text, version) in version_read.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            (root / MANIFEST_PATH).write_text(manifest_text, encoding="utf-8")
            try:
                _, modules, findings, _ = check_structure(root)
                ok = not findings and [m.version for m in modules] == [version]
            except Broken:
                ok = False
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] {name}")


def read_as_before_data() -> dict[str, tuple[str, list[str]]]:
    """The matrices that are read as before: the matrix, the rows it gives."""
    row_line, classes_text = ROW_LINE, CLASSES_TEXT
    prose = "See [A1.2](#a1-2) and [A1.1](../docs/requirements.md#a1-1); an aspect is [A1](#a1).\n"
    read_as_before = {  # case: the matrix, the rows it gives; what holds no anchor of a row or an aspect
        "a prose line that links a row and a module's own anchor are no anchor": (
            MATRIX + "\n" + prose + '<a id="const-sample"></a>\n## A module\n',
            ["a1-1", "a1-2", "a1-3"],
        ),
        "a handle that stands under two anchors is two rows": (  # each keyed by its anchor
            MATRIX.replace(row_line[2], row_line[2] + "\n" + row_line[2].replace("a1-2", "a1-9")),
            ["a1-1", "a1-2", "a1-3", "a1-9"],
        ),
    }
    reordered = (
        "Destination classes: **template** (authoring law), **binding** (per-project), **Mx** (module),"
        " **kernel §n** (shared semantics)."
    )
    read_as_before.update(  # the sentence read as the four names whatever stands round it
        {
            "the preamble's four classes in another order": (
                preamble_as(PREAMBLE.replace(classes_text, reordered)),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a bold span before the preamble's sentence is no class": (
                preamble_as(PREAMBLE.replace("requirement parts.", "requirement parts, **each** homed.")),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a period inside a code span of the preamble's sentence does not end it": (
                preamble_as(PREAMBLE.replace("(shared semantics)", "(shared `a.b. c` semantics)")),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a period inside a word of the preamble's sentence, outside a code span, does not end it": (
                preamble_as(PREAMBLE.replace("(shared semantics)", "(shared semantics, as in v1.2)")),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a class written twice in bold in the sentence is one name": (  # the names are a set
                preamble_as(PREAMBLE.replace("(authoring law).", "(authoring law), **binding** (again).")),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a bold class with a space inside its stars is the class, the name stripped": (
                preamble_as(PREAMBLE.replace("**Mx**", "** Mx **")),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a bold word in the sentence after the classes is no class": (
                preamble_as(PREAMBLE.replace("module X", "module **X**")),
                ["a1-1", "a1-2", "a1-3"],
            ),
            "a bold word in the paragraph after the classes is no class": (
                preamble_as(
                    PREAMBLE + "\n\n**Enforcement classes** — the set: **gate** (a), **advisory** (b)."
                ),
                ["a1-1", "a1-2", "a1-3"],
            ),
        }
    )
    return read_as_before


def case_read_as_before(tally: Tally) -> None:
    """Each matrix whose rows are the same whatever stands round them."""
    for name, (matrix_text, anchors) in read_as_before_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, matrix=matrix_text)
            try:
                matrix, _, findings, _ = check_structure(root)
                ok = not findings and sorted(matrix) == anchors
            except Broken:
                ok = False
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] {name}")


def case_skipped_folders(tally: Tally) -> None:
    """A folder of modules/ that starts with an underscore or a dot is no module."""
    skipped = {  # case: the folders added beside const-sample, each holding a MODULE.md and no manifest
        "a folder starting with an underscore": "_draft",
        "a folder starting with a dot": ".hidden",
    }
    for name, folder in skipped.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            (root / "modules" / folder).mkdir()
            (root / "modules" / folder / "MODULE.md").write_text("a draft\n", encoding="utf-8")
            (root / "modules" / "README.md").write_text("a file, no folder\n", encoding="utf-8")
            try:
                _, modules, findings, _ = check_structure(root)
                ok = not findings and [m.name for m in modules] == ["const-sample"]
            except Broken:
                ok = False
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] {name} of modules/ is no module, and is skipped")


def case_listing(tally: Tally) -> None:
    """The kit's one listing: a name without `const-` is a module, and the modules come sorted by name."""
    listed = {  # case: the reading of a tree that holds const-sample and a copy of it named `glossary`
        "a folder named without const- is a module": False,
        "the modules are read sorted by name, whatever order the folder lists": True,
    }
    for name, reversed_listing in listed.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            shutil.copytree(root / "modules" / "const-sample", root / "modules" / "glossary")
            try:
                with listed_in_reverse() if reversed_listing else contextlib.nullcontext():
                    _, modules, findings, _ = check_structure(root)
                ok = not findings and [m.name for m in modules] == ["const-sample", "glossary"]
            except Broken:
                ok = False
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] {name}")


def case_no_modules(tally: Tally) -> None:
    """A tree with no modules/ is a teaching BROKEN line."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        build(root, GOOD_TABLE)
        shutil.rmtree(root / "modules")
        try:
            check_structure(root)
            ok = False
        except Broken as why:
            ok = (
                str(why)
                == f"{root} has no modules/ directory — fix: run the check from a checkout of the kit"
            )
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] a tree with no modules/ is a teaching BROKEN line")


def case_reports(tally: Tally) -> None:
    """The report of a finding in a module's document, and of an unclassed destination, as literal lines."""
    literal = [  # typed by hand: a message function cannot check itself
        "RED: modules/const-sample/MODULE.md:22: the rows cell of item T9 is 'A1.1'",
        "  why: a row's result comes only from the items that name it,"
        " so every item says which rows it proves",
        "  fix: link each row the item proves, [A1.4](../../docs/requirements.md#a1-4),"
        " or write `none` for an item that proves no row of the module",
        "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s) examined,"
        " 3 shared item(s)",
    ]
    literal_class = [  # the same, for a destination the check cannot class
        "RED: docs/requirements.md: A1.2 has the destination 'kernel', a destination the check cannot class",
        "  why: the destination classes are a closed set, defined once in the preamble (rule 7 of"
        " plc-0007-requirements), and a destination outside it takes its row out of every check that"
        " reads it",
        "  fix: open the cell with one of the four classes — `kernel §<n>`, `M<n>`, `binding`, `template` —"
        " or add a class to the preamble and to this check together",
        "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s) examined,"
        " 3 shared item(s)",
    ]
    reports = {  # case: the table, the matrix, the lines the gate prints
        "of a finding in a module's document": (
            RED_TABLES["a bare handle in the rows cell"][0],
            MATRIX,
            literal,
        ),
        "of a destination the check cannot class": (
            GOOD_TABLE,
            MATRIX.replace("[kernel §2](constitution/CONVENTIONS.md#k2)", "kernel"),
            literal_class,
        ),
    }
    for name, (table, matrix_text, want_lines) in reports.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, table, matrix=matrix_text)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = gate(root)
        ok = code == EXIT_RED and printed.getvalue().splitlines() == want_lines
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] the report {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())


def case_carrier_row(tally: Tally) -> None:
    """An advisory row that a green fixture names is carrier green, never green."""
    carrier_table = GOOD_TABLE.replace(
        "| T3 | fixture, assertion | none |", f"| T3 | fixture, assertion | {LINK_3} |"
    )
    with tempfile.TemporaryDirectory() as tmp:  # an advisory row a green fixture names is carrier green
        root = Path(tmp).resolve()
        build(root, carrier_table)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = full_run(root, None)
    out = printed.getvalue()
    ok = code == EXIT_GREEN and "  A1.3  carrier green — M1 skill — const-sample 0.0.1" in out
    ok = ok and "  A1.1  green — M1 hook" in out and "1 carrier green" in out
    ok = (
        ok
        and not advisory_only("advisory; optional gate-lite: a script")
        and advisory_only("advisory — honestly ungateable")
        and not advisory_only("advisoryish — a word of its own")
        and not advisory_only("advisory procedure — caught by A1.4 gates")
    )
    tally.record(ok)
    print(
        f"[{'ok' if ok else 'FAIL'}] an advisory row proved by a green fixture is carrier green, never green"
    )
    if not ok:
        print(out)


def case_full_runs(tally: Tally) -> None:
    """A full run with each kind of pytest run exits as it should and says so."""
    runs: dict[
        str, tuple[tuple[int, ...], tuple[tuple[int, str], ...], int, str]
    ] = {  # case: the red items, the items the module's tests hold, the check's exit, a line to find
        "all green": ((), SAMPLE_ITEMS, EXIT_GREEN, "  A1.1  green — M1 hook — const-sample 0.0.1"),
        "a red item": ((2,), SAMPLE_ITEMS, EXIT_RED, "  A1.1  red — M1 hook — const-sample 0.0.1"),
        "an item the runner did not report": (
            (),
            ((1, "a"), (2, "b"), (101, "s")),
            EXIT_RED,
            "names runner item 3, which the runner did not report",
        ),
        "an item not read on a row": (
            (),
            ((3, "c"),),
            EXIT_RED,
            "  A1.1  fixture, not read + review — M1 hook — const-sample 0.0.1",
        ),
        "a runner item no table names": (
            (),
            (*SAMPLE_ITEMS, (7, "x")),
            EXIT_RED,
            "runner item 7 is named by no acceptance item",
        ),
    }
    for name, (red, named, want, needle) in runs.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            sample_tests(root, red, named=named)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = full_run(root, None)
        out = printed.getvalue()
        ok = (
            code == want
            and needle in out
            and "  A1.2  held by kernel §2 — definitional — through A1.1" in out
        )
        ok = ok and "      const-sample L1: live, done 2026-09-01 — not run" in out
        ok = ok and echoed(out, PYTEST_RED if red else 0, "FAILED modules/const-sample/tests/test_sample.py")
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] a full run with {name} exits {want} and says so")
        if not ok:
            print(out)


RUNNER_LINE = "Runner: `python3 -m pytest tests` (needs git), {} items green."


def runner_counts_data() -> dict[str, tuple[str, list[str], int | None]]:
    """The Runner lines of section 10 and the command lines they are read under, with the count the one
    finding says is written (None: no finding)."""
    runner_line = RUNNER_LINE
    counted: dict[str, tuple[str, list[str], int | None]] = {  # case: section 10 before the table, the
        # command line, the count the one finding says is written (None: no finding); the runner's total is 4
        "a Runner line whose count is the total": (runner_line.format(4), ["--run"], None),
        "a Runner line whose count differs": (runner_line.format(5), ["--run"], 5),
        "a Runner line whose count differs, run without --run": (runner_line.format(5), [], None),
        "a Runner line whose count differs, run with --run --module": (
            runner_line.format(5),
            ["--run", "--module", "const-sample"],
            5,
        ),
        "a Runner line without a count": ("Runner: `python3 -m pytest tests` (needs git).", ["--run"], None),
        "a Runner line with the count in another form": (
            "Runner: `python3 -m pytest tests`, 9 items, green: 7, 8 tests green.",
            ["--run"],
            None,
        ),
        "no Runner line": ("The runner is started by hand.", ["--run"], None),
        "a count inside a fenced block only": (
            "```\n" + runner_line.format(9) + "\n```\n\n~~~~\n" + runner_line.format(9) + "\n~~~~",
            ["--run"],
            None,
        ),
        "a Runner line after a fenced block that closed": (
            "```\n" + runner_line.format(9) + "\n```\n\n" + runner_line.format(5),
            ["--run"],
            5,
        ),
        "a differing count inside a four-backtick fence that holds a three-backtick line": (
            "````\n```\n" + runner_line.format(5) + "\n````",
            ["--run"],
            None,
        ),
        "a differing count inside a backtick fence that holds a tilde line": (
            "```\n~~~\n" + runner_line.format(5) + "\n```",
            ["--run"],
            None,
        ),
        "a differing count inside a fence that holds a backtick line with an info string": (
            "```\n```text\n" + runner_line.format(5) + "\n```",
            ["--run"],
            None,
        ),
        "a Runner line whose count is below the total": (runner_line.format(3), ["--run"], 3),
        "a differing count after a line of backticks whose info string holds a backtick": (
            "```a`b\n" + runner_line.format(5),
            ["--run"],
            5,
        ),
        "a differing count after a line of backticks indented four spaces": (
            "    ```\n" + runner_line.format(5),
            ["--run"],
            5,
        ),
        "a differing count on a line that holds Runner: after other words": (
            "The " + runner_line.format(5),
            ["--run"],
            None,
        ),
    }
    return counted


def case_runner_counts(tally: Tally) -> None:
    """A count typed on the Runner line of section 10 is red when it differs from the runner's total, and
    green again once the fix is followed."""
    for name, (preface, command_line, written) in runner_counts_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, preface + "\n\n" + GOOD_TABLE)
            doc_file = root / "modules" / "const-sample" / "MODULE.md"
            doc_lines = doc_file.read_text(encoding="utf-8").splitlines()
            where = next(
                (
                    n
                    for n, text in enumerate(doc_lines, start=1)
                    if text.startswith("Runner:") and f" {written} " in text
                ),
                0,
            )
            code, got = main_over(root, command_line)
            if written is None:
                ok = code == EXIT_GREEN and not any(line.startswith("RED:") for line in got)
                ok = ok and got[-1].startswith(("GREEN: every item read", "GREEN: every acceptance item"))
            else:  # the finding as literal lines, typed by hand, then its fix followed to green
                block = [
                    f"RED: modules/const-sample/MODULE.md:{where}: the Runner line of section 10 says"
                    f" {written} items green, and the runner's total is 4",
                    "  why: a count typed by hand drifts without a sound, and the runner's total is the one"
                    " count",
                    "  fix: write the runner's total on the Runner line of section 10: change"
                    f" `{written} items green` to `4 items green`",
                ]
                start = got.index(block[0]) if block[0] in got else -1
                ok = code == EXIT_RED and start >= 0 and got[start : start + 3] == block
                ok = ok and sum(1 for line in got if line.startswith("RED: modules/")) == 1
                ok = ok and got[-1].startswith("RED: 1 finding(s), no red item")
                spans = re.findall(r"`([^`]+)`", block[2])
                doc_file.write_text(
                    doc_file.read_text(encoding="utf-8").replace(spans[0], spans[1]), encoding="utf-8"
                )
                code, after = main_over(root, command_line)
                ok = ok and code == EXIT_GREEN and not any(line.startswith("RED:") for line in after)
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] section 10 with {name} is {'green' if written is None else 'red'}")
        if not ok:
            print(f"        got: {code} {got}")


def case_runner_echo(tally: Tally) -> None:
    """A runner's stdout without its last line break, then its stderr, are echoed as lines of their own."""
    sample = Module("const-sample", "modules/const-sample/MODULE.md", "0.0.1", {}, [])
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        echo(sample, subprocess.CompletedProcess(["pytest"], 1, "tail", "err\n"))
    ok = printed.getvalue().splitlines() == [
        "the runner of const-sample exited 1; its output, as it printed it:",
        "tail",
        "err",
    ]
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] a runner's stdout and stderr are echoed as lines of their own")


def collisions_data() -> dict[str, tuple[tuple[tuple[int, str], ...], list[str]]]:
    """The tests a module may hold that acceptance.collected refuses: the items, beside the four of
    SAMPLE_ITEMS, and the lines of its stop, each a fault, in order."""
    shared_kept = " — the shared one, if one is shared, since a shared number is never moved or reissued"
    below = "no other item holds, below 101"
    decision = "raise it as a decision, since the shared numbers are never moved"

    def carried(n: int, held: int, titles: str, fix: str) -> str:  # typed by hand: as collected says it
        return (
            f"item number {n} is carried by {held} items, {titles} — why: one number, one item, or a result"
            f" and a node id cannot say which item they mean — fix: {fix}"
        )

    def own_101(to: int) -> str:
        return carried(
            101,
            2,
            "'s', 'own'",
            f"keep one of them at 101{shared_kept}, and in the module's own tests/test_sample.py give the"
            f" other one the number {to} — a number {below}",
        )

    twice_7 = carried(
        7,
        2,
        "'x', 'y'",
        f"keep one of them at 7, and in the module's own tests/test_sample.py give the other one the number 8"
        f" — a number {below}",
    )
    unmarked = (
        "modules/const-sample/tests/test_sample.py::test_unmarked carries no item(<number>, <title>) — why: a"
        " test outside the acceptance table is examined by no row — fix: give it @item(<number>, <title>)"
        " from acceptance"
    )
    twice = ((7, "x"), (7, "y"))
    thrice = (*twice, (7, "z"))
    return {  # case: the items beside the four, the lines of the stop
        "an own item 101 beside the shared 101": (((101, "own"),), [own_101(4)]),
        "two own items numbered 7": (twice, [twice_7]),
        "two numbers carried twice, 7 and 101, one line each in number order": (
            (*twice, (101, "own")),
            [twice_7, own_101(9)],
        ),
        "three own items numbered 7": (
            thrice,
            [
                carried(
                    7,
                    3,
                    "'x', 'y', 'z'",
                    "keep one of them at 7, and in the module's own tests/test_sample.py give each of the"
                    f" other 2 the numbers 8, 9 — numbers {below}",
                )
            ],
        ),
        "an own item 100 and 7 twice, no number free below 101": (
            (*twice, (100, "top")),
            [
                carried(
                    7,
                    2,
                    "'x', 'y'",
                    f"keep one of them at 7; but no number is free below 101 for the other one — {decision}",
                )
            ],
        ),
        "an own item 99 and 7 three times, one number free below 101 and two needed": (
            (*thrice, (99, "top")),
            [
                carried(
                    7,
                    3,
                    "'x', 'y', 'z'",
                    "keep one of them at 7, and in the module's own tests/test_sample.py give 1 of the other"
                    f" 2 the number 100 — a number {below}; 1 item is then left with no free number"
                    f" — {decision}",
                )
            ],
        ),
        "an own item 99 and 7 four times, one number free below 101 and three needed": (
            (*thrice, (99, "top"), (7, "w")),
            [
                carried(
                    7,
                    4,
                    "'x', 'y', 'z', 'w'",
                    "keep one of them at 7, and in the module's own tests/test_sample.py give 1 of the other"
                    f" 3 the number 100 — a number {below}; 2 items are then left with no free number"
                    f" — {decision}",
                )
            ],
        ),
        "two own items numbered 170, no shared item there": (
            ((170, "p"), (170, "q")),
            [
                carried(
                    170,
                    2,
                    "'p', 'q'",
                    f"keep one of them at 170{shared_kept}, and in the module's own tests/test_sample.py give"
                    f" the other one the number 4 — a number {below}",
                )
            ],
        ),
        "a test without item(…) and 7 twice, the test first": (twice, [unmarked, twice_7]),
    }


def case_collisions(tally: Tally) -> None:
    """acceptance.collected stops the collection of a module's tests with its literal lines on stderr, in
    order, for each set of tests it refuses, pytest's usage error 4."""
    for name, (more, lines) in collisions_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            extra = "\n\ndef test_unmarked() -> None:\n    pass\n" if lines[0].startswith("modules/") else ""
            sample_tests(root, extra=extra, named=(*SAMPLE_ITEMS, *more))
            done = subprocess.run(
                [sys.executable, "-m", "pytest", "modules/const-sample/tests", "-p", "no:cacheprovider", "-q"]
                + ["--collect-only"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
                timeout=RUNNER_TIMEOUT,
            )
        said = [line for line in done.stderr.splitlines() if line]
        ok = done.returncode == 4 and said == [f"ERROR: {lines[0]}", *lines[1:]]
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] acceptance: {name} stops the collection with its literal lines")
        if not ok:
            print(f"        exit {done.returncode}: {said}")
    with tempfile.TemporaryDirectory() as tmp:  # a module named with a hyphen: the fix names its file
        root = Path(tmp).resolve()
        build(root, GOOD_TABLE)
        sample_module(root, "const-two-words")
        sample_tests(root, named=(*SAMPLE_ITEMS, (7, "x"), (7, "y")), module="const-two-words")
        done = subprocess.run(
            [sys.executable, "-m", "pytest", "modules/const-two-words/tests", "-p", "no:cacheprovider", "-q"]
            + ["--collect-only"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=RUNNER_TIMEOUT,
        )
    ok = done.returncode == 4 and (
        "in the module's own tests/test_two_words.py give the other one the number 8" in done.stderr
    )
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] acceptance: in const-two-words the fix names tests/test_two_words.py")
    if not ok:
        print(f"        exit {done.returncode}: {done.stderr.strip()[-600:]}")


LOAD_CASE = {"evals/load/case.yaml": "name: load\n"}  # a case folder of the sample module
LOAD_NOTE = "the load case `evals/load/`"
WHY_EVAL_TYPED = (
    "an eval case is a run on the pinned model whose receipt the kit keeps, so one item per case traces every"
    " case to the rows it proves (law 4 of CLAUDE.md)"
)
FIX_NO_CASE_TYPED = (
    "write the case the item proves in that cell as a code span `evals/<case>/`, the folder's name of"
    " lowercase letters, digits and hyphens"
)
FIX_KINDS_TYPED = (
    "open the cell with one of `fixture`, `kit check`, `live`, `live, deferred`, `eval`, `review`"
)


def eval_row(handle: str, proves: str, rows: str = LINK_1) -> str:
    return f"| {handle} | eval | {rows} | {proves} |\n"


def eval_tree(root: Path, table: str, files: dict[str, str]) -> None:
    """The sample tree with `table` as its acceptance table and `files` written into the sample module."""
    build(root, table)
    for name, text in files.items():
        path = root / "modules" / "const-sample" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def eval_green_data() -> dict[str, tuple[str, dict[str, str]]]:
    """case: the rows added to GOOD_TABLE, the files of the sample module; the gate reads no finding."""
    return {
        "one item for a case folder": (eval_row("L3", LOAD_NOTE), LOAD_CASE),
        "one item for each of two case folders": (
            eval_row("L3", LOAD_NOTE) + eval_row("L4", "the start case `evals/start-2/`", LINK_3),
            {**LOAD_CASE, "evals/start-2/case.yaml": "name: start\n"},
        ),
        "a folder that holds a prompt.md alone is no case": (
            eval_row("L3", LOAD_NOTE),
            {**LOAD_CASE, "evals/ask/prompt.md": "ask\n"},
        ),
        "evals/results/ and a folder with no case file are no case": (
            eval_row("L3", LOAD_NOTE),
            {**LOAD_CASE, "evals/results/r.json": "{}\n", "evals/notes/README.md": "notes\n"},
        ),
        "a kind that opens with eval and goes on after a comma": (
            eval_row("L3", LOAD_NOTE).replace("| eval |", "| eval, on the pinned model |"),
            LOAD_CASE,
        ),
    }


def eval_red_data() -> dict[str, tuple[str, dict[str, str], str, str, str]]:
    """case: the rows added to GOOD_TABLE, the files of the sample module, the one finding's what and fix,
    typed, and the text the finding's line holds."""
    no_case = "the eval item L3 names no case as `evals/<case>/` in its 'what it proves' cell"
    missing = "the eval item L3 names `evals/gone/`, a case folder the module does not have"
    missing_fix = (
        "add the case folder `evals/gone/` holding a `case.yaml`, or name a case folder the module has"
    )
    no_item = "the case folder `evals/load/` is named by no eval item"
    no_item_fix = (
        "add an eval item whose 'what it proves' cell names `evals/load/` and whose rows cell links the rows"
        " the case proves, or remove the folder"
    )
    twice = "the case `evals/load/` is named by the eval items L3 and L4"
    twice_fix = "keep one eval item for the case: merge the items, or name another case folder in one of them"
    two_cases = "the eval item L3 names 2 cases in its 'what it proves' cell, not one"
    two_cases_fix = "keep one case in the cell, and give the other case an eval item of its own"
    return {  # typed by hand: a message function cannot check itself
        "an eval item that names no case": (
            eval_row("L3", "the load case"),
            {},
            no_case,
            FIX_NO_CASE_TYPED,
            "L3",
        ),
        "a case in capital letters": (eval_row("L3", "`evals/Load/`"), {}, no_case, FIX_NO_CASE_TYPED, "L3"),
        "a case without its closing slash": (
            eval_row("L3", "`evals/load`"),
            {},
            no_case,
            FIX_NO_CASE_TYPED,
            "L3",
        ),
        "an eval item that names two cases": (
            eval_row("L3", "`evals/load/` and `evals/other/`"),
            {},
            two_cases,
            two_cases_fix,
            "L3",
        ),
        "a case folder the module does not have": (
            eval_row("L3", "`evals/gone/`"),
            {},
            missing,
            missing_fix,
            "L3",
        ),
        "a folder with no case.yaml": (
            eval_row("L3", "`evals/gone/`"),
            {"evals/gone/notes.md": "x\n"},
            missing,
            missing_fix,
            "L3",
        ),
        "an item that names evals/results/": (
            eval_row("L3", "`evals/results/`"),
            {"evals/results/r.json": "{}\n"},
            missing.replace("gone", "results"),
            missing_fix.replace("gone", "results"),
            "L3",
        ),
        "a case folder no eval item names": ("", LOAD_CASE, no_item, no_item_fix, "| item |"),
        "an item that names a folder with a prompt.md alone": (
            eval_row("L3", "`evals/gone/`"),
            {"evals/gone/prompt.md": "gone\n"},
            missing,
            missing_fix,
            "L3",
        ),
        "a case named by two eval items": (
            eval_row("L3", LOAD_NOTE) + eval_row("L4", LOAD_NOTE, LINK_3),
            LOAD_CASE,
            twice,
            twice_fix,
            "L4",
        ),
        "a case named by three eval items": (
            eval_row("L3", LOAD_NOTE) + eval_row("L4", LOAD_NOTE, LINK_3) + eval_row("L5", LOAD_NOTE),
            LOAD_CASE,
            twice.replace("L3 and L4", "L3, L4 and L5"),
            twice_fix,
            "L4",
        ),
    }


def case_eval_gate(tally: Tally) -> None:
    """The eval kind in the gate: a case folder and its item agree both ways, one item to one case; each
    finding red on its tree and no finding on a tree the fix would leave."""
    for name, (rows, files) in eval_green_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            eval_tree(root, GOOD_TABLE + rows, files)
            found = check_structure(root)[2]
        ok = not found
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] eval items: {name} is green")
        if not ok:
            print(f"        got: {[f.what for f in found]}")
    for name, (rows, files, what, fix, at) in eval_red_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            eval_tree(root, GOOD_TABLE + rows, files)
            found = check_structure(root)[2]
            lines = (root / "modules/const-sample/MODULE.md").read_text(encoding="utf-8").splitlines()
        ok = len(found) == 1 and found[0].what == what and found[0].fix == fix
        ok = ok and found[0].why == WHY_EVAL_TYPED and found[0].path == "modules/const-sample/MODULE.md"
        ok = ok and found[0].line > 0 and at in lines[found[0].line - 1]
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] eval items: {name} is red with one finding")
        if not ok:
            print(f"        got: {[(f.line, f.what, f.fix) for f in found]}")
    with tempfile.TemporaryDirectory() as tmp:  # the kind word is whole, and the fix lists the kind
        root = Path(tmp).resolve()
        eval_tree(root, GOOD_TABLE + "| T9 | evaluation | " + LINK_1 + " | x |\n", {})
        found = check_structure(root)[2]
    ok = len(found) == 1 and "is none of the set" in found[0].what and found[0].fix == FIX_KINDS_TYPED
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] eval items: `evaluation` is no kind, and the fix lists eval")
    literal = [
        "RED: modules/const-sample/MODULE.md:22: the eval item L3 names no case as `evals/<case>/` in its"
        " 'what it proves' cell",
        f"  why: {WHY_EVAL_TYPED}",
        f"  fix: {FIX_NO_CASE_TYPED}",
        "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s) examined,"
        " 3 shared item(s)",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        eval_tree(root, GOOD_TABLE + eval_row("L3", "the load case"), {})
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = gate(root)
    ok = code == EXIT_RED and printed.getvalue().splitlines() == literal
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] eval items: the report of a finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())


RUN_TABLE = (
    TABLE_HEAD
    + f"| T1–T2 | fixture | {LINK_1} | the gate |\n"
    + "| T3 | fixture | none | the hooks file |\n"
    + f"| S101 | fixture, shared | {LINK_1} | shared |\n"
    + eval_row("L3", LOAD_NOTE, LINK_3)
)
PASSED = Attempt("2026-10-16T00:00:00Z", 1, 1, 1.0)
FAILED_EARLY = Attempt("2026-10-15T00:00:00Z", 2, 1, 0.5)
FAILED_LAST = Attempt("2026-10-17T01:00:00Z", 2, 1, 0.5)


def eval_git_tree(root: Path, attempts: tuple[Attempt, ...]) -> None:
    """The sample tree with the eval pins and its case, made a git repository that tracks it, and a receipt
    that is current for the files as they stand."""
    eval_tree(root, RUN_TABLE, LOAD_CASE)
    (root / "scripts").mkdir(exist_ok=True)
    (root / EVAL_MODEL).write_text("claude-opus-5-5\n", encoding="utf-8")
    (root / CLAUDE_PIN).write_text("2.1.282\n", encoding="utf-8")
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    for args in (["init", "-q"], ["add", "-A"]):
        subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, check=True)
    receipt = Receipt(eval_hash(root, "const-sample"), "2.1.282", "claude-opus-5-5", attempts)
    write_receipts(root, {"const-sample": receipt})


def eval_edit(path: str, text: str = "changed\n") -> Callable[[Path], None]:
    def act(root: Path) -> None:
        (root / path).write_text(text, encoding="utf-8")

    return act


def eval_append(path: str) -> Callable[[Path], None]:
    def act(root: Path) -> None:
        with (root / path).open("a", encoding="utf-8") as handle:
            handle.write("\nappended\n")

    return act


def eval_run_data() -> dict[str, tuple[tuple[Attempt, ...], Callable[[Path], None], int, str, str]]:
    """case: the receipt's attempts, what is done to the tree after the receipt, the run's exit, the line of
    the eval item and the line of the row it alone proves; typed by hand."""
    green = (
        "      const-sample L3: eval — green (receipt of 2026-10-16)",
        "  A1.3  carrier green — M1 skill — const-sample 0.0.1",
    )
    red = (
        "      const-sample L3: eval — red (receipt of 2026-10-17)",
        "  A1.3  red — M1 skill — const-sample 0.0.1",
    )
    stale = (
        "      const-sample L3: eval, no current receipt — not run",
        "  A1.3  eval, no current receipt — M1 skill — const-sample 0.0.1",
    )
    untracked = eval_edit("scripts/untracked.txt")  # a file git does not track: no file a session loads
    appended = eval_append("modules/const-sample/MODULE.md")  # the document, left out of the hash
    gate_py = "modules/const-sample/plugin/scripts/gate.py"
    return {
        "a current receipt whose last attempt passes": ((PASSED,), untracked, EXIT_GREEN, *green),
        "a pass after an earlier failure": ((FAILED_EARLY, PASSED), untracked, EXIT_GREEN, *green),
        "a current receipt whose last attempt fails": ((PASSED, FAILED_LAST), untracked, EXIT_RED, *red),
        "an edit of MODULE.md after the receipt": ((PASSED,), appended, EXIT_GREEN, *green),
        "an edit of a test after the receipt": (
            (PASSED,),
            eval_edit("modules/const-sample/tests/test_sample.py", "pass\n"),
            EXIT_GREEN,
            *green,
        ),
        "an edit of a script after a passing receipt": ((PASSED,), eval_edit(gate_py), EXIT_GREEN, *stale),
        "an edit of a script after a failing receipt": (
            (PASSED, FAILED_LAST),
            eval_edit(gate_py),
            EXIT_GREEN,
            *stale,
        ),
        "an edit of the case after a passing receipt": (
            (PASSED,),
            eval_edit("modules/const-sample/evals/load/case.yaml"),
            EXIT_GREEN,
            *stale,
        ),
        "another Claude Code pin": ((PASSED,), eval_edit(CLAUDE_PIN, "2.1.251\n"), EXIT_GREEN, *stale),
        "another model pin": ((PASSED,), eval_edit(EVAL_MODEL, "claude-haiku-5-5\n"), EXIT_GREEN, *stale),
        "a receipts file with no entry of the module": (
            (PASSED,),
            partial(write_receipts, receipts={}),
            EXIT_GREEN,
            *stale,
        ),
        "no receipts file": ((PASSED,), lambda root: (root / RECEIPTS).unlink(), EXIT_GREEN, *stale),
        "a receipt with no attempt": ((), untracked, EXIT_GREEN, *stale),
    }


def eval_broken_data() -> dict[str, tuple[Callable[[Path], None], str]]:
    """case: what is done to the tree, what the BROKEN line says; each a read of the receipt that fails."""
    return {
        "a receipts file that is no JSON": (eval_edit(RECEIPTS, "{\n"), "cannot be read as JSON"),
        "a model file that is no model id": (eval_edit(EVAL_MODEL, "Opus 5.5\n"), "is not one model id"),
        "a pin that is no version": (eval_edit(CLAUDE_PIN, "latest\n"), "is not one version"),
    }


def case_eval_runs(tally: Tally) -> None:
    """The eval kind under --run: the item's result is read from the module's receipt, green or red only
    where the receipt is current, else no result; a read that fails is a BROKEN line; the gate reads none."""
    for name, (attempts, act, want, item_line_text, row_line) in eval_run_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            eval_git_tree(root, attempts)
            act(root)
            outs = []
            for only in (None, "const-sample"):
                printed = io.StringIO()
                with contextlib.redirect_stdout(printed):
                    code = full_run(root, only, sample_results)
                outs.append((code, printed.getvalue()))
        ok = all(code == want and item_line_text in out and row_line in out for code, out in outs)
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] eval items: {name}, a run exits {want} with the item's line")
        if not ok:
            print(outs[0][1])
    for name, (act, said) in eval_broken_data().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            eval_git_tree(root, (PASSED,))
            act(root)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                gate_code = gate(root)
            try:
                with contextlib.redirect_stdout(printed):
                    full_run(root, None, sample_results)
                message = ""
            except Broken as broken:
                message = str(broken)
        ok = gate_code == EXIT_GREEN and said in message and "fix:" in message
        ok = ok and message.startswith("the eval items of const-sample cannot be judged: ")
        tally.record(ok)
        print(f"[{'ok' if ok else 'FAIL'}] eval items: {name} is a BROKEN line with the fix, the gate green")
        if not ok:
            print(f"        got: {gate_code} {message}")
    with tempfile.TemporaryDirectory() as tmp:  # a tree that is no git repository: the hash cannot be read
        root = Path(tmp).resolve()
        eval_tree(root, RUN_TABLE, LOAD_CASE)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                full_run(root, None, sample_results)
            message = ""
        except Broken as broken:
            message = str(broken)
    ok = "git ls-files exited" in message and "fix: run the command from a clone of the kit" in message
    tally.record(ok)
    print(f"[{'ok' if ok else 'FAIL'}] eval items: a tree that is no git repository is a BROKEN line")
    if not ok:
        print(f"        got: {message}")


def self_test() -> int:
    """Red→green on a throwaway tree: every finding of the gate red with its table broken one way
    and green with the good table; the report of one finding as literal lines; a full run green,
    one red with a red item, one red for an item the runner did not report and one it reported
    unnamed; a run that cannot be read as BROKEN; the stop of acceptance.collected; the destination classes,
    the form of the matrix and of the module documents, and the tie to the preamble, each over its
    whole set of cases."""
    os.environ.pop(kit_coverage.ENV, None)  # every case runs its runner plain, save those that set it
    os.environ.pop(
        SUMMARY_ENV, None
    )  # and writes no job summary, CI's own page included, save the case that sets it
    tally = Tally()
    case_red_tables(tally)
    case_unheld_row(tally)
    case_destinations(tally)
    case_indented_rows(tally)
    case_unclosed_rows(tally)
    case_open_ended_section(tally)
    case_sections_reordered(tally)
    case_unreadable(tally)
    case_manifest_commands(tally)
    case_manifest_versions(tally)
    case_read_as_before(tally)
    case_skipped_folders(tally)
    case_listing(tally)
    case_no_modules(tally)
    case_reports(tally)
    case_carrier_row(tally)
    case_full_runs(tally)
    case_runner_counts(tally)
    case_runner_echo(tally)
    case_acceptance(tally)
    case_collisions(tally)
    case_eval_gate(tally)
    case_eval_runs(tally)
    case_pytest_runs(tally)
    case_job_summary(tally)
    shared_failed, shared_total = self_test_shared()
    coverage_failed, coverage_total = self_test_coverage()
    total = tally.total + shared_total + coverage_total
    failed = tally.failed + shared_failed + coverage_failed
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str], kit: Path) -> int:
    """The command line over the kit at `kit`: the gate, the run, or the self-test."""
    parser = argparse.ArgumentParser(prog="check-aspects", add_help=False, allow_abbrev=False)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--module")
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
        if (args.module is not None and not args.run) or (args.self_test and (args.run or args.module)):
            raise SystemExit(2)
    except SystemExit:
        print(
            "BROKEN: misinvocation — fix: run with no arguments,"
            " with --run [--module NAME], or with --self-test"
        )
        print("BROKEN: the check could not run — 0 rows examined")
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        return full_run(kit, args.module) if args.run else gate(kit)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 rows examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], KIT))
