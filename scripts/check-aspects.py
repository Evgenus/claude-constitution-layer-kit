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
  - a kind that opens with none of the words fixture, kit check, live, review — `live,
    deferred` opening with live;
  - a `rows` cell that is empty, or holds anything but row links or the one word `none`;
  - a link to a row the matrix does not hold;
  - an item that names a row its module's rows section does not hold;
  - a row a module's rows section holds that no item of that module names;
  - a row the matrix gives a module (its destination opens with M and a number) that no
    module's rows section holds.

The report, `--run`, also runs each module's `tests/run.py` and reads its item lines, which
the shared harness prints as `[ok]` or `[FAIL]`, the number, the kind in round brackets and the
title, and its last line, `N/T acceptance items green — …`. An item line out of that form, a
count of item lines that differs from T, a count N of green lines that differs from the `[ok]`
lines, an exit other than 0 or 2, or an exit that disagrees with the item lines means the runner
could not be read: the check could not run, never a pass. A fixture item's handle is its runner
number, bare or under `T` or `S` — `T12` and `12` are item 12, `S101` is item 101. Also red in a
full run: a runner item no table row names, and a fixture item a table names that the runner did
not print.

Each row a module holds is printed with its destination as the matrix states it, every module
that holds a part of it with the version of its manifest, and every item that names it — from
every such module alike — with its kind and its result. Then one verdict. `red` when an item of
it is red. `green` when at least one of its items was run and every item run was green; the
items no run examines, of any module that holds a part of the row, are listed beside and do not
lower it. `carrier green` instead of `green` for an advisory row — its enforcement cell in the
matrix opens with the word `advisory` and holds the word `gate` or `gates` nowhere, matched as
whole words, so that "ungateable" is no gate and "gate-lite" is one — since a fixture there
proves the carrier of a judgment, never the judgment. Otherwise the kinds of its items joined
by " + ": `live, done <date>`, `live` for a live item that names no date, `live, deferred`,
`review`, `kit check`, and `fixture, not read` for a fixture item the runner did not print —
none of them a green. A row a module holds that no item names is `no item`, a finding of the
gate as well. A row no module holds is printed as
"held by" its destination and its enforcement cell as the matrix states them, counted as
`no module`, and never green. A shared-items line carries every row a fixture item of the
module, run through the same entry point, names, so a red there turns those rows red. Items
marked `none` are listed per module outside every row; a red one still makes the run red.

Modes:  no arguments         the gate;
        --run                the gate, then every runner and the per-row report;
        --run --module NAME  the same for one module: its findings alone, its rows' verdicts from
                             its items alone;
        --self-test          prove the check on a throwaway tree: each finding red→green, the
                             report of one finding as literal lines, a full run green and red,
                             a runner that cannot be read as a BROKEN line.
Exit:   0 green; 2 a finding or a red item; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from kit_module_doc import DocumentError, section

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
SPEC = "docs/requirements.md"
RUNNER_TIMEOUT = 1800  # seconds; the slowest runner takes a few minutes

ASPECT = re.compile(r'^\| <a id="(a\d+)"></a>\*\*(A\d+ — [^*]+)\*\*')
ROW = re.compile(r'^\| <a id="(a\d+-\d+)"></a>(A\d+\.\d+) \|')
ASPECT_ANCHOR = re.compile(r'<a id="(a\d+)"></a>')
ROW_ANCHOR = re.compile(r'<a id="(a\d+-\d+)"></a>')
CELL_SPLIT = re.compile(r"(?<!\\)\|")
ROW_LINK = re.compile(r"\[([^\[\]]*)\]\(([^()\s]*)\)")
LINK_TEXT = re.compile(r"\[([^\[\]]*)\]\([^()]*\)")
HANDLE = r"[A-Z]?\d+[a-z]?"
ITEM_TOKEN = re.compile(rf"^(?P<a>{HANDLE})(?:–(?P<b>{HANDLE}))?$")
HANDLE_PARTS = re.compile(r"^(?P<p>[A-Z]?)(?P<n>\d+)(?P<s>[a-z]?)$")
ITEM_LINE = re.compile(r"^\[(ok|FAIL)\] +(\d+)\. \((red→green|assertion)\) ")
ITEM_LIKE = re.compile(r"^\[(?:ok|FAIL)\]")
LAST_LINE = re.compile(r"^(\d+)/(\d+) acceptance items green — ")
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
SENTENCE_END = re.compile(r"\.(?:\s|$)")
BOLD_SPAN = re.compile(r"\*\*([^*]+)\*\*")
ACCEPTANCE_HEADER = ["item", "kind", "rows", "what it proves"]

WHY_TAG = "a row's result comes only from the items that name it, so every item says which rows it proves"
WHY_HANDLES = (
    "the full run matches each item to the runner's numbered lines, and a cell it cannot read matches nothing"
)
WHY_KIND = "the kind says whether a run examines the item, and a kind outside the set cannot be judged"
WHY_SCOPE = "a module implements exactly the rows its rows section holds (law 4 of CLAUDE.md)"
WHY_RUN = "a row is green only where a run examined it, so every item the runner prints must be in the table"
WHY_CLASSES = (
    "the destination classes are a closed set, defined once in the preamble (rule 7 of"
    " plc-0007-requirements), and a destination outside it takes its row out of every check that reads it"
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
    kind: str  # fixture | kit check | live | live, deferred | review
    rows: list[str]  # anchors; empty for `none`
    numbers: list[int]  # runner numbers, fixture items only
    done: str | None
    results: dict[int, bool] = field(default_factory=dict)

    def label(self) -> str:
        if self.kind == "live" and self.done:
            return f"live, done {self.done}"
        return "fixture, not read" if self.kind == "fixture" else self.kind

    def outcome(self) -> str | None:
        """'green' or 'red' for a fixture item every number of which was read; None otherwise."""
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


def cells(line: str) -> list[str]:
    parts = CELL_SPLIT.split(line.strip())
    return [p.strip() for p in parts[1:-1]]


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
    `ASPECT` or `ROW` states, or the check is BROKEN; so is an anchor on two lines. A line that holds
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
        ("review", "review"),
    ):
        if re.match(rf"{re.escape(prefix)}\b", text):
            return kind
    return None


def read_module(root: Path, directory: Path, matrix: dict[str, Row], findings: list[Finding]) -> Module:
    name = directory.name
    path = f"modules/{name}/MODULE.md"
    text = read(root, path)
    manifest = directory / ".claude-plugin" / "plugin.json"
    try:
        version = str(json.loads(manifest.read_text(encoding="utf-8")).get("version", "?"))
    except (OSError, ValueError) as bad:
        raise Broken(
            f"modules/{name}/.claude-plugin/plugin.json cannot be read ({bad}) — fix: restore the manifest"
        ) from bad
    try:
        rows_section, acceptance_section = section(text, "t3", path), section(text, "t10", path)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
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
    module = Module(name, path, version, held, [])
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
            continue
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
            continue
        kind = kind_of(kind_cell)
        if kind is None:
            findings.append(
                Finding(
                    path,
                    number,
                    f"the kind '{kind_cell}' of item {handles} is none of the set",
                    WHY_KIND,
                    "open the cell with one of `fixture`, `kit check`, `live`, `live, deferred`, `review`",
                )
            )
            continue
        numbers: list[int] = []
        if kind == "fixture":
            if any(p not in ("", "T", "S") or s for p, _, _, s in parsed):
                findings.append(
                    Finding(
                        path,
                        number,
                        f"the fixture item {handles} has a handle that is no runner number",
                        WHY_HANDLES,
                        "write a fixture item as its runner number, bare or under `T` or `S`",
                    )
                )
                continue
            numbers = [n for _, first, last, _ in parsed for n in range(first, last + 1)]
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
            continue
        for anchor in anchors:
            if anchor not in matrix:
                findings.append(
                    Finding(
                        path,
                        number,
                        f"item {handles} links #{anchor}, a row the matrix does not hold",
                        WHY_TAG,
                        "link a row the matrix holds, or remove the link",
                    )
                )
            elif anchor not in held:
                findings.append(
                    Finding(
                        path,
                        number,
                        f"item {handles} names {matrix[anchor].handle}, a row the rows section does not hold",
                        WHY_SCOPE,
                        "remove the link, or add the row to the rows section if the module implements it",
                    )
                )
        done = DONE.search(proves)
        module.items.append(
            Item(
                name,
                number,
                handles,
                kind,
                [a for a in anchors if a in held],
                numbers,
                done[1] if done else None,
            )
        )
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
    base = root / "modules"
    if not base.is_dir():
        raise Broken(f"{root} has no modules/ directory — fix: run the check from a checkout of the kit")
    directories = sorted(d for d in base.iterdir() if d.is_dir() and not d.name.startswith((".", "_")))
    for directory in directories:
        if not (directory / "MODULE.md").is_file():
            raise Broken(f"modules/{directory.name} has no MODULE.md — fix: restore the module document")
    return directories


def check_structure(
    root: Path, only: str | None = None
) -> tuple[dict[str, Row], list[Module], list[Finding]]:
    matrix = read_matrix(root)
    check_classes(root)
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
    return matrix, modules, findings


def counts(matrix: dict[str, Row], modules: list[Module]) -> str:
    items = sum(len(m.items) for m in modules)
    return (
        f"{len(matrix)} row(s) of the matrix, {len(modules)} module document(s),"
        f" {items} acceptance item(s) examined"
    )


def run_runner(root: Path, module: Module) -> dict[int, bool]:
    runner = root / "modules" / module.name / "tests" / "run.py"
    if not runner.is_file():
        raise Broken(f"modules/{module.name}/tests/run.py does not exist — fix: restore the module's runner")
    try:
        done = subprocess.run(
            [sys.executable, str(runner)],
            cwd=root,
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
    if done.returncode not in (0, 2):
        first = ((done.stderr or done.stdout).strip().splitlines() or ["no message"])[-1]
        raise Broken(
            f"the runner of {module.name} exited {done.returncode}: {first} — fix: run"
            f" python3 modules/{module.name}/tests/run.py and repair what it names"
        )
    results: dict[int, bool] = {}
    lines = [text for text in done.stdout.splitlines() if text.strip()]
    for line in lines:
        if ITEM_LIKE.match(line):
            m = ITEM_LINE.match(line)
            if m is None:
                raise Broken(
                    f"the runner of {module.name} printed an item line out of form: {line[:80]} — fix: the"
                    " harness prints `[ok] N. (kind) title`; repair the runner or this check's reading"
                )
            results[int(m[2])] = m[1] == "ok"
    last = LAST_LINE.match(lines[-1]) if lines else None
    if last is None or int(last[2]) != len(results) or int(last[1]) != sum(results.values()):
        raise Broken(
            f"the runner of {module.name} printed {len(results)} item line(s), and its last line does not"
            " count them — fix: run it alone; the harness's last line is `N/T acceptance items green — …`"
        )
    if (done.returncode == 0) != all(results.values()):
        raise Broken(
            f"the runner of {module.name} exited {done.returncode} against its own item lines"
            " — fix: run it alone"
        )
    return results


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
    result = (
        f"{outcome} ({len(item.numbers)} run)"
        if outcome
        else ("not read" if item.kind == "fixture" else "not run")
    )
    kind = item.kind if item.kind == "fixture" else item.label()
    return f"      {item.module} {item.handles}: {kind} — {result}"


def full_run(
    root: Path, only: str | None, runner: Callable[[Path, Module], dict[int, bool]] = run_runner
) -> int:
    matrix, modules, findings = check_structure(root, only)
    read_items = 0
    for module in modules:
        results = runner(root, module)
        read_items += len(results)
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
                            f"item {item.handles} names runner item {n}, which the runner did not print",
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
    for module in modules:
        loose = [i for i in module.items if not i.rows]
        if loose:
            print(f"{module.name} — items that prove no row")
            for item in loose:
                print(item_line(item))
                red = red or item.outcome() == "red"
    summary = "; ".join(f"{n} {v}" for v, n in sorted(tally.items(), key=lambda kv: -kv[1]))
    runs = f"{read_items} runner item(s) read from {len(modules)} runner(s)"
    for finding in findings:
        print(finding.render())
    if findings or red:
        print(
            f"RED: {len(findings)} finding(s), {'a red item' if red else 'no red item'} — {summary}"
            f" — {counts(matrix, modules)}; {runs}"
        )
        return EXIT_RED
    print(f"GREEN: every item read is green — {summary} — {counts(matrix, modules)}; {runs}")
    return EXIT_GREEN


def gate(root: Path) -> int:
    matrix, modules, findings = check_structure(root)
    for finding in findings:
        print(finding.render())
    if findings:
        print(f"RED: {len(findings)} finding(s) — {counts(matrix, modules)}")
        return EXIT_RED
    print(
        "GREEN: every acceptance item names its rows, and every row a module holds has an item"
        f" — {counts(matrix, modules)}"
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
| <a id="a1-2"></a>A1.2 | two | [kernel §2](../kernel/CONVENTIONS.md#k2) | definitional — through A1.1 |
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
        + '\n<a id="t11"></a>\n## 11\n'
    )


GOOD_TABLE = (
    "| item | kind | rows | what it proves |\n|---|---|---|---|\n"
    f"| T1–T2 | fixture, red→green | {LINK_1} | the gate |\n"
    "| T3 | fixture, assertion | none | the hooks file |\n"
    f"| S101 | fixture, shared | {LINK_1} | shared |\n"
    f"| L1 | live | {LINK_3} | done 2026-09-01, a live run |\n"
    f"| L2 | review | {LINK_1}, {LINK_3} | the pairs |\n"
)


def fake_runner(lines: list[str], code: int) -> str:
    body = "\n".join(f"print({line!r})" for line in lines)
    return f"import sys\n{body}\nsys.exit({code})\n"


GREEN_RUN = [
    "[ok]   1. (red→green) a",
    "        evidence",
    "[ok]   2. (assertion) b",
    "[ok]   3. (assertion) c",
    "[ok] 101. (assertion) s",
    "4/4 acceptance items green — 1 red→green cases, 3 assertions examined",
]


def harness_runner(argv: list[str]) -> str:
    """A runner on the kit's own shared harness — the items of GREEN_RUN, each an assertion — with
    `argv` as its command line, so the self-test reads what the harness prints, never a copy of it."""
    shared = KIT / "shared"
    return (
        "import sys\n"
        f"sys.path[:0] = [{str(shared)!r}, {str(shared / 'tests')!r}]\n"
        f"sys.argv[1:] = {argv!r}\n"
        "from pathlib import Path\n"
        "from harness import Assertion, Harness\n"
        "H = Harness(Path('.'), 'none.sh', 'none.py', 'const-sample')\n"
        "NAMED = ((1, 'a'), (2, 'b'), (3, 'c'), (101, 's'))\n"
        "ITEMS = [Assertion(n, t, lambda: (True, 'evidence')) for n, t in NAMED]\n"
        "sys.exit(H.run_all([], ITEMS))\n"
    )


def build(
    root: Path, table: str, rows: str | None = None, runner: str | None = None, matrix: str = MATRIX
) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / SPEC).write_text(matrix, encoding="utf-8")
    module = root / "modules" / "const-sample"
    (module / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (module / ".claude-plugin" / "plugin.json").write_text(
        '{"name": "const-sample", "version": "0.0.1"}\n', encoding="utf-8"
    )
    text = module_text(table) if rows is None else module_text(table, rows)
    (module / "MODULE.md").write_text(text, encoding="utf-8")
    (module / "tests").mkdir(exist_ok=True)
    (module / "tests" / "run.py").write_text(runner or fake_runner(GREEN_RUN, 0), encoding="utf-8")


def self_test() -> int:
    """Red→green on a throwaway tree: every finding of the gate red with its table broken one way
    and green with the good table; the report of one finding as literal lines; a full run green,
    one red with a red item, one red for an item the runner did not print and one it printed
    unnamed; a runner out of form and one whose count disagrees as BROKEN."""
    header = "| item | kind | rows | what it proves |\n|---|---|---|---|\n"
    red: dict[str, tuple[str, str | None]] = {  # case: its table (or rows section), what the finding says
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
            header + f"| T1 | fixture | {LINK_1} | x |\n",
            "named by no acceptance item",
        ),
        "an indented item whose rows cell is no link": (
            GOOD_TABLE + "  | T9 | fixture | A1.1 | x |\n",
            "the rows cell of item T9",
        ),
    }
    failed = 0
    for name, (table, said) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE)
            green_before = not check_structure(root)[2]
            build(root, table)
            findings = check_structure(root)[2]
        ok = green_before and len(findings) == 1 and said is not None and said in findings[0].what
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the good table is green, {name} is red with one finding")
    with tempfile.TemporaryDirectory() as tmp:  # a module row no module holds
        root = Path(tmp).resolve()
        build(root, header + f"| T1 | fixture | {LINK_1} | x |\n", rows=f"| {LINK_1} | r |\n")
        findings = check_structure(root)[2]
    ok = (
        len(findings) == 1
        and findings[0].what == "A1.3 is given to a module, and no module's rows section holds it"
    )
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a row the matrix gives a module that no rows section holds is red")
    destinations = {  # the whole set of openings: the cell, whether the check classes it
        "M1 hook": True,
        "M47 skill + hook": True,
        "**M1** skill": True,
        "[kernel §2](../kernel/CONVENTIONS.md#k2)": True,
        "kernel §12": True,
        "[kernel §2](../kernel/CONVENTIONS.md#k2) + template": True,
        "binding": True,
        "binding (thresholds)": True,
        "template": True,
        "module `const-x` skill": False,
        "kernel": False,
        "kernel §": False,
        "kernel §n": False,
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
    for cell, classed in destinations.items():
        seen: list[list[str]] = []
        for old in ("M1 hook", "[kernel §2](../kernel/CONVENTIONS.md#k2)"):
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
        failed += 0 if ok else 1
        print(
            f"[{'ok' if ok else 'FAIL'}] the destination '{cell}' is"
            f" {'classed' if classed else 'red as one the check cannot class'},"
            " on a row a module holds and on one none holds"
        )
        if not ok:
            print(f"        got: {seen}")
    with tempfile.TemporaryDirectory() as tmp:  # a table line is read whatever its indent
        root = Path(tmp).resolve()
        indented_rows = f"  | {LINK_1} | r |\n\t|{LINK_3} | r |\n"  # the second row: no space after the bar
        build(
            root,
            GOOD_TABLE + f"  | T9 | fixture | {LINK_1} | x |\n\t|T8 | fixture | {LINK_1} | x |\n",
            rows=indented_rows,
        )
        _, modules, findings = check_structure(root)
    ok = not findings and len(modules[0].items) == 7 and sorted(modules[0].held.values()) == [6, 7]
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] an indented row of the rows section and an indented acceptance item,"
        " each also with no space after the bar, are read, never dropped"
    )
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
    # the matrix, line 6 the row A1.1 (a module holds it), line 7 the row A1.2 (none does), line 5 the
    # aspect: every way its line can leave the form `ROW` or `ASPECT` states, each on both rows
    row_line = {1: MATRIX.splitlines()[5], 2: MATRIX.splitlines()[6]}
    aspect_line = MATRIX.splitlines()[4]
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
    classes_text = PREAMBLE[PREAMBLE.index(CLASSES_SENTENCE) : PREAMBLE.index(" An authoring")]
    typed_names = "'Mx', 'binding', 'kernel §n', 'template'"
    names_found = f'{SPEC} names the destination classes %s in its "Destination classes:" sentence, and this'

    def preamble_as(edited: str) -> str:
        return MATRIX.replace(PREAMBLE, edited)

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
                    got.append(str(bad))
        failed += 0 if ok else 1
        print(
            f"[{'ok' if ok else 'FAIL'}] a kit tree with {name} is one BROKEN line naming it,"
            " in the plain run and in the run of one module"
        )
        if not ok:
            print(f"        got: {got}")
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
    for name, (matrix_text, anchors) in read_as_before.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, matrix=matrix_text)
            try:
                matrix, _, findings = check_structure(root)
                ok = not findings and sorted(matrix) == anchors
            except Broken:
                ok = False
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
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
                _, modules, findings = check_structure(root)
                ok = not findings and [m.name for m in modules] == ["const-sample"]
            except Broken:
                ok = False
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} of modules/ is no module, and is skipped")
    literal = [  # typed by hand: a message function cannot check itself
        "RED: modules/const-sample/MODULE.md:22: the rows cell of item T9 is 'A1.1'",
        "  why: a row's result comes only from the items that name it,"
        " so every item says which rows it proves",
        "  fix: link each row the item proves, [A1.4](../../docs/requirements.md#a1-4),"
        " or write `none` for an item that proves no row of the module",
        "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s) examined",
    ]
    literal_class = [  # the same, for a destination the check cannot class
        "RED: docs/requirements.md: A1.2 has the destination 'kernel', a destination the check cannot class",
        "  why: the destination classes are a closed set, defined once in the preamble (rule 7 of"
        " plc-0007-requirements), and a destination outside it takes its row out of every check that"
        " reads it",
        "  fix: open the cell with one of the four classes — `kernel §<n>`, `M<n>`, `binding`, `template` —"
        " or add a class to the preamble and to this check together",
        "RED: 1 finding(s) — 3 row(s) of the matrix, 1 module document(s), 5 acceptance item(s) examined",
    ]
    reports = {  # case: the table, the matrix, the lines the gate prints
        "of a finding in a module's document": (red["a bare handle in the rows cell"][0], MATRIX, literal),
        "of a destination the check cannot class": (
            GOOD_TABLE,
            MATRIX.replace("[kernel §2](../kernel/CONVENTIONS.md#k2)", "kernel"),
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
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the report {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())
    runs: dict[
        str, tuple[list[str], int, int, str]
    ] = {  # case: runner lines, its exit, the check's exit, a line to find
        "all green": (GREEN_RUN, 0, EXIT_GREEN, "  A1.1  green — M1 hook — const-sample 0.0.1"),
        "a red item": (
            [
                *GREEN_RUN[:2],
                "[FAIL]   2. (assertion) b",
                *GREEN_RUN[3:5],
                "3/4 acceptance items green — 1 red→green cases, 3 assertions examined",
            ],
            2,
            EXIT_RED,
            "  A1.1  red — M1 hook — const-sample 0.0.1",
        ),
        "an item the runner did not print": (
            [
                *GREEN_RUN[:3],
                GREEN_RUN[4],
                "3/3 acceptance items green — 1 red→green cases, 2 assertions examined",
            ],
            0,
            EXIT_RED,
            "names runner item 3, which the runner did not print",
        ),
        "an item not read on a row": (
            [GREEN_RUN[3], "1/1 acceptance items green — 0 red→green cases, 1 assertions examined"],
            0,
            EXIT_RED,
            "  A1.1  fixture, not read + review — M1 hook — const-sample 0.0.1",
        ),
        "a runner item no table names": (
            [
                *GREEN_RUN[:5],
                "[ok]   7. (assertion) x",
                "5/5 acceptance items green — 1 red→green cases, 4 assertions examined",
            ],
            0,
            EXIT_RED,
            "runner item 7 is named by no acceptance item",
        ),
    }
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
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] an advisory row proved by a green fixture is carrier green, never green"
    )
    if not ok:
        print(out)
    for name, (lines, runner_exit, want, needle) in runs.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, runner=fake_runner(lines, runner_exit))
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
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] a full run with {name} exits {want} and says so")
        if not ok:
            print(out)
    broken: dict[str, tuple[list[str], int, str]] = {
        "an item line out of form": (
            ["[ok] one (assertion) a", *GREEN_RUN[1:]],
            0,
            "an item line out of form",
        ),
        "a last line that does not count": (
            [*GREEN_RUN[:5], "9/9 acceptance items green — x"],
            0,
            "does not count them",
        ),
        "an exit that is no verdict": (GREEN_RUN, 1, "exited 1"),
    }
    for name, (lines, runner_exit, needle) in broken.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, runner=fake_runner(lines, runner_exit))
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    full_run(root, None)
                ok = False
            except Broken as said:
                ok = needle in str(said) and "fix:" in str(said)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] a runner with {name} is a BROKEN line, never a pass")
    unknown = (  # typed by hand: a message function cannot check itself
        "BROKEN: --item 7: no item numbered 7 in this runner — why: a filter that matches nothing runs"
        " nothing, and nothing run looks green — fix: name items this runner holds: 1–3, 101"
    )
    misused = (
        "BROKEN: misinvocation: --items 2 — why: the runner takes one option, and an argument it ignored"
        " could pass for a filter — fix: run with no arguments for a full run, or with --item <n>[,<n>…]"
        " to run only those items"
    )
    filtered: dict[str, tuple[list[str], int, int, list[str], str | None]] = {
        # case: the command line; the runner's exit; its item lines; its last lines, on stdout, or on
        # stderr when it could not run; what the full run's BROKEN line says, None when it reads green
        "no filter, a full run": (
            [],
            0,
            4,
            ["4/4 acceptance items green — 0 red→green cases, 4 assertions examined"],
            None,
        ),
        "--item 2,101": (
            ["--item", "2,101"],
            0,
            2,
            ["2/2 selected items green — 2 of 4 items run, not a full pass"],
            "does not count them",
        ),
        "--item 7, a number it does not hold": (
            ["--item", "7"],
            1,
            0,
            [unknown, "BROKEN: the runner could not run — 0 of 4 items run"],
            "exited 1",
        ),
        "--items 2, an argument it does not take": (
            ["--items", "2"],
            1,
            0,
            [misused, "BROKEN: the runner could not run — 0 of 4 items run"],
            "exited 1",
        ),
    }
    for name, (argv, runner_exit, count, tail, reason) in filtered.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, GOOD_TABLE, runner=harness_runner(argv))
            done = subprocess.run(
                [sys.executable, str(root / "modules" / "const-sample" / "tests" / "run.py")],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            lines_out = done.stdout.splitlines()
            shown = done.stderr.splitlines() if runner_exit == 1 else lines_out
            ok = done.returncode == runner_exit and shown[-len(tail) :] == tail
            ok = ok and sum(1 for line in lines_out if ITEM_LINE.match(line)) == count
            ok = ok and (
                not argv or not any(LAST_LINE.match(line) for line in lines_out)
            )  # never the full line
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = full_run(root, None)
                ok = ok and reason is None and code == EXIT_GREEN
            except Broken as why:
                ok = ok and reason is not None and reason in str(why)
        failed += 0 if ok else 1
        print(
            f"[{'ok' if ok else 'FAIL'}] the shared harness run with {name} prints its literal last lines"
            f" and {'reads green' if reason is None else 'is a BROKEN line, never a pass'}"
        )
        if not ok:
            print(f"exit {done.returncode}\n{done.stdout}{done.stderr}")
    total = (
        len(red)
        + 3  # the row no module holds, the indented rows, the carrier row
        + len(destinations)
        + len(reports)
        + len(read_as_before)
        + len(unreadable)
        + len(skipped)
        + len(runs)
        + len(broken)
        + len(filtered)
    )
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
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
        return full_run(KIT, args.module) if args.run else gate(KIT)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 rows examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
