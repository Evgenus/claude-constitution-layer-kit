#!/usr/bin/env python3
"""Kit check: every copy of the Python floor names the floor's one minor.

The floor's one source is `FLOOR` in `shared/const_gate/preflight.py`, read here by `ast` and never
imported: a module-level assignment, the last one, plain or annotated, of a tuple of two integer
literals, `(3, <minor>)`. A tuple of any other shape, a major other than 3, a missing `FLOOR`, and a
file that is missing or no Python are BROKEN, with the fix. No gate reads the source at run time: each
entry file keeps its own literal, since it must parse on any Python 3 (template §6, rule 3), and this
check holds every copy to the source, so that a floor moved in one place and left in another is red in
CI instead of a traceback where an entry's teaching line should stand (law 6 of CLAUDE.md).

A copy is a mention of the floor in a file `git ls-files` lists, in one of these forms, each matched in
any line, a fenced block and a code span included (`N` stands for a whole number):
  - `Python 3.N`, `python 3.N`, not followed by a digit nor by `.<digit>`: a measured `Python 3.N.M`
    is no mention, `Python 3.N+` and a sentence's `Python 3.N.` are;
  - `(3, N)` closing right after N, so a tuple of three numbers and a tool's `(0, N, M)` are none;
    `FLOOR = (3, N)` in an entry file is one of these;
  - `(3.N)`; `below 3.N` and `floor 3.N`, either case of the first letter, not followed by a digit nor
    by `.<digit>`; `py3N`, one or two digits between word bounds; `python_version = "3.N"` of the type
    checker; `python-version: "3.N"` of the workflow.
Each of these must name the source's minor. Three more forms name the minor one below the floor, the
version under which a fixture runs an entry to see its refusal, and each must name the source's minor
minus one: `found 3.N` and `an interpreter of 3.N`, not followed by a digit nor by `.<digit>`, and
`version_info = (3, N, 0`. A mention that names another minor is RED, with its path and line, the value
found, the source, why a floor copied apart drifts and the fix.

Not read: a symbolic link, mode 120000, whatever it points at, a dangling one too, since its target is
read through its own listing, once; `docs/decisions/` and `docs/research/` at the kit root, where
records and frozen comparisons keep their words; a file git sees as binary, which is git's own test, a
NUL byte among its first 8000 bytes; and every version that is no copy of the floor, `uv run -p 3.N`,
a tool's own `FLOOR`, a measured `Python 3.N.M`. One form the check cannot tell from a copy is read as
one: the arguments of a call, `f(3, N)`. A file git sees as text that is not UTF-8 is BROKEN with the
fix, never a crash and never a skip, and so is a file git lists that the working tree lacks.

Findings are sorted by path, then line, then column, whatever order git lists the files in. The green
line gives the mentions and the number of files that hold them.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway repository: a baseline of four entry pairs, their
                       module documents and install notes, the tool configuration and the workflow,
                       green with its literal line; an entry's floor and an install note red with their
                       literal lines; every form of the two lists, right green and one above and one
                       below red, and each form's closing guard green; records, comparisons, links, a
                       binary file, and the forms that are no copy green, with the edges of the binary
                       test; the source with no floor, a float, a string, three numbers, another major,
                       a nested one, an unreadable or a missing file, a file that is not UTF-8, git
                       missing and no repository, each a literal BROKEN line; the source moved with
                       every copy left, red on each of them; the order of the findings under an
                       adversarial listing; the misinvocation.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import ast
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

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
SOURCE = "shared/const_gate/preflight.py"
NOT_READ = ("docs/decisions/", "docs/research/")  # records and frozen comparisons keep their words
REGULAR = ("100644", "100755")  # a symbolic link (120000) and a submodule (160000) are never read
GIT_BINARY = 8000  # git's own test: a NUL byte among the first 8000 bytes
WHY = (
    "a floor copied apart drifts, and the entry file that drifts prints a traceback where its designed"
    " teaching line should stand (law 6 of CLAUDE.md)"
)
GUARD = r"(?!\d|\.\d)"  # not followed by a digit nor `.<digit>`: a longer minor, or a measured `3.N.M`

Lister = Callable[[Path], list[tuple[str, str]]]


@dataclass(frozen=True)
class Form:
    name: str
    pattern: re.Pattern[str]  # group 1 is the minor
    below: int  # 0: names the floor's minor; 1: names the minor one below it


FORMS = (
    Form("python", re.compile(rf"[Pp]ython 3\.(\d+){GUARD}"), 0),
    Form("tuple", re.compile(r"\(3, (\d+)\)"), 0),
    Form("parenthesised", re.compile(r"\(3\.(\d+)\)"), 0),
    Form("below", re.compile(rf"[Bb]elow 3\.(\d+){GUARD}"), 0),
    Form("floor", re.compile(rf"[Ff]loor 3\.(\d+){GUARD}"), 0),
    Form("py", re.compile(r"\bpy3(\d{1,2})\b"), 0),
    Form("type checker", re.compile(r'python_version = "3\.(\d+)"'), 0),
    Form("workflow", re.compile(r'python-version: "3\.(\d+)"'), 0),
    Form("found", re.compile(rf"found 3\.(\d+){GUARD}"), 1),
    Form("version_info", re.compile(r"version_info = \(3, (\d+), 0"), 1),
    Form("interpreter", re.compile(rf"an interpreter of 3\.(\d+){GUARD}"), 1),
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Mention:
    form: str
    text: str
    found: int
    below: int
    line: int
    column: int


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    what: str
    why: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.path}:{self.line}: {self.what}\n  why: {self.why}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Result:
    findings: list[Finding]
    minor: int  # the source's
    mentions: int
    files: int  # the files that hold a mention


def listed(root: Path) -> list[tuple[str, str]]:
    """The files `git ls-files` lists, as (mode, path), in the order git gives them."""
    try:
        done = subprocess.run(
            ["git", "ls-files", "-z", "-s"], cwd=root, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as missing:
        raise Broken("git is not on PATH — fix: install git, then run the check again") from missing
    if done.returncode != 0:
        first = (done.stderr.splitlines() or ["no message"])[0]
        raise Broken(f"git ls-files failed: {first} — fix: run the check from a checkout of the kit")
    files: list[tuple[str, str]] = []
    for record in done.stdout.split("\0"):
        if record:
            meta, _, path = record.partition("\t")
            files.append((meta.split(" ")[0], path))
    return files


def floor_of(root: Path) -> int:
    """The minor of the source's `FLOOR`, else BROKEN with the fix."""
    shape = "write it as `FLOOR = (3, <minor>)`"
    try:
        tree = ast.parse((root / SOURCE).read_text(encoding="utf-8"), filename=SOURCE)
    except FileNotFoundError as missing:
        raise Broken(
            f"{SOURCE} is missing — fix: restore the shared preflight, the floor's one source"
        ) from missing
    except (SyntaxError, ValueError, UnicodeDecodeError) as bad:  # ValueError: a NUL byte
        raise Broken(f"{SOURCE} cannot be read as Python ({bad}) — fix: repair the file") from bad
    except OSError as bad:
        raise Broken(f"{SOURCE} cannot be read ({bad.strerror}) — fix: make it readable") from bad
    value: ast.expr | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "FLOOR" for target in node.targets
        ):
            value = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "FLOOR"
            and node.value is not None  # a bare annotation assigns nothing
        ):
            value = node.value
    if value is None:
        raise Broken(f"{SOURCE} declares no FLOOR at the top level — fix: declare it, {shape}")
    parts = value.elts if isinstance(value, ast.Tuple) else []
    numbers: list[int] = []
    for part in parts:
        if (
            isinstance(part, ast.Constant)
            and isinstance(part.value, int)
            and not isinstance(part.value, bool)
        ):
            numbers.append(part.value)
    if len(parts) != 2 or len(numbers) != 2:
        raise Broken(
            f"FLOOR in {SOURCE}:{value.lineno} is not a tuple of two integer literals — fix: {shape}"
        )
    if numbers[0] != 3:
        raise Broken(
            f"FLOOR in {SOURCE}:{value.lineno} names major {numbers[0]}, and the forms this check reads are"
            f" those of Python 3 — fix: {shape}"
        )
    return numbers[1]


def mentions(text: str) -> list[Mention]:
    """Every mention of the floor in `text`, one per match of a form, in no particular order."""
    found: list[Mention] = []
    for form in FORMS:
        for match in form.pattern.finditer(text):
            start = match.start()
            found.append(
                Mention(
                    form.name,
                    match[0],
                    int(match[1]),
                    form.below,
                    text.count("\n", 0, start) + 1,
                    start - (text.rfind("\n", 0, start) + 1) + 1,
                )
            )
    return found


def contents(root: Path, path: str) -> str | None:
    """The text of a tracked file, or None for a file git sees as binary."""
    try:
        data = (root / path).read_bytes()
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: restore or remove the file") from bad
    if b"\0" in data[:GIT_BINARY]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad


def finding(path: str, mention: Mention, minor: int) -> Finding:
    wanted = minor - mention.below
    if mention.below:
        what = (
            f"'{mention.text}' names 3.{mention.found}, and one minor below the floor, 3.{minor}"
            f" ({SOURCE}), is 3.{wanted}"
        )
    else:
        what = f"'{mention.text}' names 3.{mention.found}, the floor is 3.{minor} ({SOURCE})"
    fix = f"write 3.{wanted}, or move the floor in {SOURCE} and every copy together"
    return Finding(path, mention.line, mention.column, what, WHY, fix)


def check_kit(root: Path, listing: Lister = listed) -> Result:
    minor = floor_of(root)
    findings: list[Finding] = []
    total = holding = 0
    for mode, path in listing(root):
        if mode not in REGULAR or path.startswith(NOT_READ):
            continue
        text = contents(root, path)
        found = [] if text is None else mentions(text)
        total += len(found)
        holding += 1 if found else 0
        findings.extend(finding(path, m, minor) for m in found if m.found != minor - m.below)
    findings.sort(key=lambda f: (f.path, f.line, f.column))
    return Result(findings, minor, total, holding)


def report(result: Result) -> int:
    counts = f"{result.mentions} mention(s) in {result.files} file(s) examined"
    if result.findings:
        for item in result.findings:
            print(item.render())
        print(f"RED: {len(result.findings)} finding(s) — {counts}, the floor 3.{result.minor} ({SOURCE})")
        return EXIT_RED
    print(f"GREEN: every copy of the Python floor names 3.{result.minor} ({SOURCE}) — {counts}")
    return EXIT_GREEN


class Cases:
    """The self-test's tally: one line per case, the total counted as the cases run."""

    def __init__(self) -> None:
        self.total = 0
        self.failed = 0

    def check(self, ok: bool, text: str) -> None:
        self.total += 1
        self.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")


def put(root: Path, path: str, text: str | bytes) -> None:
    """Write a file of the throwaway tree, not yet staged."""
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        (root / path).write_bytes(text)
    else:
        (root / path).write_text(text, encoding="utf-8")


def write(root: Path, path: str, text: str | bytes) -> None:
    put(root, path, text)
    subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)


def link(root: Path, path: str, target: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    os.symlink(target, root / path)
    subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)


# The fixture names its minors through these, never as digits: this file is a file git lists, and a
# mention typed here would be read by the check on the kit.
BASE = 12  # the baseline's floor and every copy of it
OLD = BASE - 1  # one minor below, and the minor of a record that kept its words
OVER = BASE + 1  # a floor moved up, or a copy that drifted up
DEFAULT_CLAUSE = "until then Markdown writes pass unchecked"
GATE_CLOSING = "BROKEN: the check could not run — 0 documents examined"
SESSION_CLOSING = "BROKEN: the session-start line could not be printed — the gate's state is unknown"
GENERATOR_CLOSING = "BROKEN: the thing could not be made — nothing was written"
# the fixture's four entries: module, entry stem, the clause its Identity names (None: a generator's entry
# files carry none), the closing line of its entry files
ENTRIES = (
    ("const-a", "check-a", DEFAULT_CLAUSE, GATE_CLOSING),  # a gate on the default clause
    ("const-b", "check-b", "until then shell commands pass unchecked", GATE_CLOSING),  # a gate's own clause
    ("const-c", "session-start", "until then the gate's state is not said at session start", SESSION_CLOSING),
    ("const-d", "make-thing", None, GENERATOR_CLOSING),  # a generator
)


def entry_python(module: str, minor: int, clause: str | None, closing: str) -> str:
    """An entry file as the kit's entries are written: the floor, then two texts of concatenated
    literals, each a first line and a closing line."""
    tail = "" if clause is None else f" — {clause}"
    texts = []
    for name, first in (
        (
            "TOO_OLD",
            f"BROKEN: {module} needs Python %d.%d or newer, found %d.%d — fix: install a Python{tail}",
        ),
        ("NO_SHARED_CODE", f"BROKEN: {module} is installed without its shared code — fix: install it{tail}"),
    ):
        cut = len(first) // 2  # the first line stands in two literals, the cut inside it
        texts.append(
            f"{name} = (\n    {first[:cut]!r}\n    {(first[cut:] + chr(10))!r}\n"
            f"    {(closing + chr(10))!r}\n)\n"
        )
    return f'"""An entry file."""\n\nimport sys\n\nFLOOR = (3, {minor})\n\n' + "\n".join(texts)


def entry_shell(module: str, stem: str, minor: int, clause: str | None, closing: str) -> str:
    tail = "" if clause is None else f" — {clause}"
    return (
        "#!/bin/sh\n"
        f"# {module}: the entry point.\n"
        "if ! command -v python3 >/dev/null 2>&1; then\n"
        f'  echo "BROKEN: {module} needs python3 — fix: install Python 3.{minor} or newer{tail}" >&2\n'
        f'  echo "{closing}" >&2\n'
        "  exit 1\nfi\n"
        f'exec python3 "$(dirname "$0")/{stem}.py" "$@"\n'
    )


def fresh(root: Path, minor: int = BASE, floor: int | None = None) -> None:
    """A throwaway kit whose every copy of the floor names `minor`, the source `floor` (default the
    same): four modules, each with its document, install note and entry pair; the root install note, the
    tool configuration, the workflow, a record and a comparison that name another minor."""
    try:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as failed:
        raise Broken(f"git init failed in {root} — fix: install git, then run the self-test") from failed
    put(root, SOURCE, f'"""The preflight."""\n\nFLOOR = (3, {minor if floor is None else floor})\n')
    put(root, "INSTALL.md", f"# Install\n\nNeeds Python 3.{minor} or newer.\n")
    put(
        root,
        "pyproject.toml",
        f'[tool.ruff]\ntarget-version = "py3{minor}"\n\n[tool.mypy]\npython_version = "3.{minor}"\n',
    )
    put(root, ".github/workflows/gates.yml", f'steps:\n  - with:\n      python-version: "3.{minor}"\n')
    put(root, "docs/decisions/dec-0001-old.md", f"The floor was Python 3.{OLD} once.\n")
    put(root, "docs/research/res-0001-survey.md", f"A survey on Python 3.{OLD}, frozen.\n")
    for module, stem, clause, closing in ENTRIES:
        put(
            root,
            f"modules/{module}/MODULE.md",
            f"A module: needs git, Python 3.{minor}. The floor (3.{minor}).\n",
        )
        put(root, f"modules/{module}/INSTALL.md", f"Install it. Python 3.{minor} or newer.\n")
        put(root, f"modules/{module}/scripts/{stem}.py", entry_python(module, minor, clause, closing))
        put(root, f"modules/{module}/scripts/{stem}.sh", entry_shell(module, stem, minor, clause, closing))
    put(  # the forms that name one minor below the floor, where a runner fakes the interpreter
        root,
        "modules/const-a/tests/run.py",
        f"CODE = 'import sys; sys.version_info = (3, {minor - 1}, 0)'\nSAID = 'found 3.{minor - 1}'\n",
    )
    put(root, "modules/const-a/NOTE.md", f"The runner uses an interpreter of 3.{minor - 1}.\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)


# The mentions of the baseline tree, by hand: the source 1; INSTALL.md 1; pyproject.toml 2 (`py3N` and the
# type checker's); the workflow 1; four MODULE.md 2 each (`Python 3.N`, `(3.N)`) = 8; four install notes 1
# each = 4; four entry pairs 2 each (`FLOOR = (3, N)` and the `.sh`'s `Python 3.N`) = 8; the runner 2
# (`found`, `version_info`) and the note 1 (`an interpreter of`) = 3: 28, in 1 + 1 + 1 + 1 + 4 + 4 + 8 + 2
# = 22 files.
BASE_MENTIONS, BASE_FILES = 28, 22

# Every form the check reads, as a line of text: `{}` is the minor; the number says whether the form names
# the floor (0) or the minor one below it (1).
TEMPLATES = (
    ("python", "Needs Python 3.{} or newer.", 0),
    ("python, a sentence's end", "The floor: Python 3.{}.", 0),
    ("python, a plus", "Python 3.{}+ is needed", 0),
    ("python, lower case", "needs python 3.{} here", 0),
    ("entry floor", "FLOOR = (3, {})", 0),
    ("tuple", "if sys.version_info < (3, {}):", 0),
    ("parenthesised", "the interpreter floor (3.{})", 0),
    ("below", "an interpreter below 3.{} is refused", 0),
    ("below, capital", "Below 3.{} is refused", 0),
    ("floor", "the interpreter floor 3.{} holds", 0),
    ("floor, capital", "Floor 3.{} holds", 0),
    ("py", 'target-version = "py3{}"', 0),
    ("type checker", 'python_version = "3.{}"', 0),
    ("workflow", 'python-version: "3.{}"', 0),
    ("found", "BROKEN: needs Python, found 3.{}", 1),
    ("version_info", "sys.version_info = (3, {}, 0)", 1),
    ("interpreter", "run under an interpreter of 3.{}", 1),
)
# The same forms with a closing that makes them no mention, written with a minor that would be red if read.
GUARDS = (
    ("python, a measured version", "Measured on Python 3.{}.4."),
    ("tuple of three numbers", "VALE = (3, {}, 0)"),
    ("parenthesised, a longer version", "the floor (3.{}.1)"),
    ("below, a longer version", "below 3.{}.1 is refused"),
    ("floor, a longer version", "floor 3.{}.1 holds"),
    ("py, more digits", "py3{}5"),
    ("py, a word before it", "xpy3{}"),
    ("type checker, a patch", 'python_version = "3.{}.1"'),
    ("workflow, a patch", 'python-version: "3.{}.1"'),
    ("found, a measured version", "found 3.{}.4"),
    ("version_info, not at zero", "sys.version_info = (3, {}, 1)"),
    ("interpreter, a measured version", "an interpreter of 3.{}.4"),
    ("a tool's own tuple of three", "RULES = (0, {}, 2)"),
    ("uv run's interpreter option", "uv run -p 3.{} script.py"),
)


def run_report(root: Path, listing: Lister = listed) -> tuple[int, list[str]]:
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report(check_kit(root, listing))
    return code, printed.getvalue().splitlines()


def self_test() -> int:
    cases = Cases()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        code, lines = run_report(root)
        cases.check(
            code == EXIT_GREEN
            and lines
            == [
                f"GREEN: every copy of the Python floor names 3.{BASE} (shared/const_gate/preflight.py)"
                f" — {BASE_MENTIONS} mention(s) in {BASE_FILES} file(s) examined"
            ],
            "the baseline is green, with its literal line",
        )
    self_test_reds(cases)
    self_test_forms(cases)
    self_test_guards(cases)
    self_test_not_read(cases)
    self_test_broken(cases)
    self_test_order(cases)
    print(f"{cases.total - cases.failed}/{cases.total} cases green")
    return EXIT_GREEN if cases.failed == 0 else EXIT_RED


def self_test_reds(cases: Cases) -> None:
    """The literal report of the findings the brief names, then the source moved with every copy left."""
    why = (
        "  why: a floor copied apart drifts, and the entry file that drifts prints a traceback where its"
        " designed teaching line should stand (law 6 of CLAUDE.md)"
    )
    counts = (
        f"{BASE_MENTIONS} mention(s) in {BASE_FILES} file(s) examined,"
        f" the floor 3.{BASE} (shared/const_gate/preflight.py)"
    )
    move = "or move the floor in shared/const_gate/preflight.py and every copy together"
    fix = f"  fix: write 3.{BASE}, {move}"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(
            root,
            "modules/const-a/scripts/check-a.py",
            entry_python("const-a", OLD, DEFAULT_CLAUSE, GATE_CLOSING),
        )
        code, lines = run_report(root)
        cases.check(
            code == EXIT_RED
            and lines
            == [
                f"RED: modules/const-a/scripts/check-a.py:5: '(3, {OLD})' names 3.{OLD},"
                f" the floor is 3.{BASE} (shared/const_gate/preflight.py)",
                why,
                fix,
                f"RED: 1 finding(s) — {counts}",
            ],
            "an entry's FLOOR one minor below is red, with its literal lines",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "modules/const-c/INSTALL.md", f"Install it. Python 3.{OVER} or newer.\n")
        code, lines = run_report(root)
        cases.check(
            code == EXIT_RED
            and lines
            == [
                f"RED: modules/const-c/INSTALL.md:1: 'Python 3.{OVER}' names 3.{OVER}, the floor is 3.{BASE}"
                " (shared/const_gate/preflight.py)",
                why,
                fix,
                f"RED: 1 finding(s) — {counts}",
            ],
            f"an install note at 3.{OVER} is red, with its literal lines",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "modules/const-a/tests/run.py", f"SAID = 'found 3.{BASE}'\n")
        code, lines = run_report(root)
        cases.check(
            code == EXIT_RED
            and lines[0]
            == f"RED: modules/const-a/tests/run.py:1: 'found 3.{BASE}' names 3.{BASE}, and one minor below"
            f" the floor, 3.{BASE} (shared/const_gate/preflight.py), is 3.{OLD}"
            and lines[2] == f"  fix: write 3.{OLD}, {move}",
            "a form for the minor below the floor, naming the floor itself, is red with its literal lines",
        )
    with tempfile.TemporaryDirectory() as tmp:  # the source moved, every copy left
        root = Path(tmp).resolve()
        fresh(root, minor=BASE, floor=OVER)
        result = check_kit(root)
        paths = {f.path for f in result.findings}
        cases.check(
            len(result.findings) == BASE_MENTIONS - 1  # the source's own literal names the new floor
            and result.minor == OVER
            and SOURCE not in paths
            and len(paths) == BASE_FILES - 1,
            f"the source moved up with every copy left: red on each of the other {BASE_MENTIONS - 1}"
            f" mentions, in each of their {BASE_FILES - 1} files",
        )


def self_test_forms(cases: Cases) -> None:
    """Every template, alone in a file beside the baseline: right is green, one above and one below red."""
    for name, template, below in TEMPLATES:
        for delta, red in ((0, False), (1, True), (-1, True)):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                fresh(root)
                write(
                    root,
                    "docs/form.md",
                    "first line\n" + template.format(BASE - below + delta) + "\nlast line\n",
                )
                result = check_kit(root)
            red_at = [(f.path, f.line) for f in result.findings]
            ok = red_at == ([("docs/form.md", 2)] if red else []) and result.mentions == BASE_MENTIONS + 1
            word = {0: "right", 1: "one above", -1: "one below"}[delta]
            cases.check(ok, f"the form '{name}' with its minor {word} is {'red' if red else 'green'}")


def self_test_guards(cases: Cases) -> None:
    for name, template in GUARDS:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, "docs/guard.md", template.format(OVER) + "\n")
            result = check_kit(root)
        cases.check(
            result.findings == [] and result.mentions == BASE_MENTIONS,
            f"the guard '{name}' is no mention",
        )
    with tempfile.TemporaryDirectory() as tmp:  # a longer minor is a mention of that minor
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "docs/long.md", f"Python 3.{BASE}0 is far off.\n")
        result = check_kit(root)
    cases.check(
        [(f.path, f.what.split("'")[1], f"names 3.{BASE}0, the floor" in f.what) for f in result.findings]
        == [("docs/long.md", f"Python 3.{BASE}0", True)],
        "a minor of one more digit is a mention of that minor, read whole",
    )
    with tempfile.TemporaryDirectory() as tmp:  # the one form the check cannot tell from a copy
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "docs/call.md", f"scan_tail(3, {OVER}) is a call\n")
        result = check_kit(root)
    cases.check(
        [(f.path, f.what.split("'")[1]) for f in result.findings] == [("docs/call.md", f"(3, {OVER})")],
        "the arguments of a call, f(3, N), read as the tuple form, are red: the check cannot tell them apart",
    )
    with tempfile.TemporaryDirectory() as tmp:  # a measured version in prose, the floor moved up
        root = Path(tmp).resolve()
        fresh(root, minor=OVER)
        write(root, "docs/measured.md", f"Measured on Python 3.{BASE}.4.\n")
        result = check_kit(root)
    cases.check(
        result.findings == [] and result.minor == OVER,
        f"Python 3.{BASE}.4 in prose, the floor at (3, {OVER}), is green",
    )
    with tempfile.TemporaryDirectory() as tmp:  # several forms in a line, in the order of their columns
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "docs/crlf.md", f"one\r\n(3, {OVER}) and Python 3.{OVER}\r\nlast (3, {OLD})\r\n".encode())
        result = check_kit(root)
    cases.check(
        [(f.line, f.column, f.what.split("'")[1]) for f in result.findings]
        == [(2, 1, f"(3, {OVER})"), (2, 13, f"Python 3.{OVER}"), (3, 6, f"(3, {OLD})")],
        "mentions of several forms in a file with CRLF lines stand by line, then by column",
    )


def self_test_not_read(cases: Cases) -> None:
    old = f"Python 3.{OLD} and (3, {OLD})\n"
    for path, name in (
        ("docs/decisions/dec-0002-old.md", "a record under docs/decisions/"),
        ("docs/research/res-0002-old.md", "a comparison under docs/research/"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, old)
            result = check_kit(root)
        cases.check(
            result.findings == [] and result.mentions == BASE_MENTIONS, f"{name} naming 3.{OLD} is not read"
        )
    for path, name in (
        ("docs/decisions-notes.md", "a file whose name only starts like docs/decisions/"),
        (
            "modules/const-a/docs/research/r.md",
            "a docs/research/ below a module, the aside being the kit root's",
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, f"Python 3.{OLD}\n")
            result = check_kit(root)
        cases.check([f.path for f in result.findings] == [path], f"{name} is read")
    with tempfile.TemporaryDirectory() as tmp:  # links: not read, whatever they point at
        root = Path(tmp).resolve()
        fresh(root)
        link(root, "modules/const-a/linked.md", "../../docs/research/res-0001-survey.md")
        link(root, "modules/const-a/dangling.md", "nowhere.md")
        link(root, "modules/const-a/INSTALL-copy.md", "INSTALL.md")
        result = check_kit(root)
    cases.check(
        result.findings == [] and result.mentions == BASE_MENTIONS,
        f"a link to a file naming 3.{OLD}, a dangling link and a link to a file naming 3.{BASE} are not read:"
        " the last file's mention counts once, through its source",
    )
    with tempfile.TemporaryDirectory() as tmp:  # a link to a file the check reads, whose source is wrong
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "docs/notes.md", f"Python 3.{OLD}\n")
        link(root, "modules/const-a/notes-copy.md", "../../docs/notes.md")
        result = check_kit(root)
    cases.check(
        [f.path for f in result.findings] == ["docs/notes.md"],
        f"a link to a file naming 3.{OLD} is red once, through its source",
    )
    # git's own test of a binary file: a NUL byte among the first 8000 bytes
    for name, data, red in (
        ("a NUL at the first byte", b"\0" + old.encode(), False),
        (
            "a NUL as the last of the first 8000 bytes",
            old.encode() + b" " * (GIT_BINARY - len(old) - 1) + b"\0",
            False,
        ),
        ("a NUL as the first byte after them", old.encode() + b" " * (GIT_BINARY - len(old)) + b"\0", True),
        ("bytes that are no UTF-8 behind a NUL", b"\0\xff\xfe" + old.encode(), False),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, "docs/blob.bin", data)
            result = check_kit(root)
        cases.check(
            bool(result.findings) == red and (result.mentions == BASE_MENTIONS + (2 if red else 0)),
            f"{name}: a file git sees as {'text, read' if red else 'binary, skipped'}",
        )


def broken_line(root: Path) -> str:
    try:
        check_kit(root)
    except Broken as broken:
        return str(broken)
    return "no BROKEN"


def self_test_broken(cases: Cases) -> None:
    shape = "write it as `FLOOR = (3, <minor>)`"
    where = f"FLOOR in {SOURCE}"
    not_two = f"{where}:2 is not a tuple of two integer literals — fix: {shape}"
    for name, source, said in (
        (
            "a source with no FLOOR",
            '"""x"""\nOTHER = 1\n',
            f"{SOURCE} declares no FLOOR at the top level — fix: declare it, {shape}",
        ),
        (
            "a FLOOR inside a function",
            f"def f():\n    FLOOR = (3, {OLD})\n",
            f"{SOURCE} declares no FLOOR at the top level — fix: declare it, {shape}",
        ),
        ("a FLOOR that is a float", f"X = 1\nFLOOR = 3.{BASE}\n", not_two),
        ("a FLOOR with a string in it", f'X = 1\nFLOOR = (3, "{BASE}")\n', not_two),
        ("a FLOOR of three numbers", f"X = 1\nFLOOR = (3, {BASE}, 0)\n", not_two),
        ("a FLOOR of one number", "X = 1\nFLOOR = (3,)\n", not_two),
        ("a FLOOR that is a list", f"X = 1\nFLOOR = [3, {BASE}]\n", not_two),
        ("a FLOOR with a name in it", f"X = 1\nFLOOR = (X, {BASE})\n", not_two),
        ("a FLOOR with a boolean in it", "X = 1\nFLOOR = (3, True)\n", not_two),
        ("a FLOOR with a negative number", "X = 1\nFLOOR = (3, -1)\n", not_two),
        (
            "a FLOOR of another major",
            f"X = 1\nFLOOR = (4, {BASE})\n",
            f"{where}:2 names major 4, and the forms this check reads are those of Python 3 — fix: {shape}",
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, SOURCE, source)
            cases.check(broken_line(root) == said, f"{name} is a teaching BROKEN line")
    for name, source, minor in (
        ("an annotated FLOOR", f"FLOOR: tuple[int, int] = (3, {OVER})\n", OVER),
        ("the last of two assignments", f"FLOOR = (3, {OLD})\nFLOOR = (3, {OVER})\n", OVER),
        ("a FLOOR among other names", f"A = (3, {OLD})\nFLOOR = (3, {OVER})\nB = (3, {BASE})\n", OVER),
        ("a bare annotation after the assignment", f"FLOOR = (3, {OVER})\nFLOOR: tuple[int, int]\n", OVER),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, SOURCE, source)
            cases.check(check_kit(root).minor == minor, f"{name} is read")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        subprocess.run(["git", "rm", "-q", "-f", SOURCE], cwd=root, check=True, capture_output=True)
        cases.check(
            broken_line(root)
            == f"{SOURCE} is missing — fix: restore the shared preflight, the floor's one source",
            "a missing source is a teaching BROKEN line",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, SOURCE, "FLOOR = (3, \n")
        cases.check(
            broken_line(root).startswith(f"{SOURCE} cannot be read as Python (")
            and broken_line(root).endswith(") — fix: repair the file"),
            "a source that is no Python is a teaching BROKEN line",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "docs/latin.md", f"caf\xe9 Python 3.{BASE}\n".encode("latin-1"))
        cases.check(
            broken_line(root)
            == "docs/latin.md is not UTF-8 (invalid continuation byte at byte 3) — fix: save it as UTF-8",
            "a file git sees as text that is no UTF-8 is a teaching BROKEN line, never a crash",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        (root / "INSTALL.md").unlink()
        cases.check(
            broken_line(root)
            == "INSTALL.md cannot be read (No such file or directory) — fix: restore or remove the file",
            "a listed file the working tree lacks is a teaching BROKEN line",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        write_plain(root / SOURCE, f"FLOOR = (3, {BASE})\n")
        said = broken_line(root)
        cases.check(
            said.startswith("git ls-files failed: ")
            and said.endswith(" — fix: run the check from a checkout of the kit"),
            "a tree that is no git repository is a teaching BROKEN line",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        path = os.environ["PATH"]
        os.environ["PATH"] = ""
        try:
            said = broken_line(root)
        finally:
            os.environ["PATH"] = path
        cases.check(
            said == "git is not on PATH — fix: install git, then run the check again",
            "a git that cannot be run is a teaching BROKEN line",
        )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(io.StringIO()):  # argparse's usage
        code = main(["--bogus"])
    cases.check(
        code == EXIT_BROKEN
        and printed.getvalue().splitlines()
        == [
            "BROKEN: misinvocation — fix: run with no arguments, or with --self-test",
            "BROKEN: the check could not run — 0 mentions examined",
        ],
        "a misinvocation is its literal BROKEN lines, exit 1",
    )


def write_plain(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def self_test_order(cases: Cases) -> None:
    """The findings by path, line and column, whatever order git lists the files in."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root, minor=BASE, floor=OVER)
        write(root, "docs/two.md", f"first (3, {BASE})\nPython 3.{BASE} and (3, {BASE})\n")
        listings: dict[str, Lister] = {
            "as git lists them": listed,
            "reversed": lambda r: list(reversed(listed(r))),
            "by the reverse of each path": lambda r: sorted(listed(r), key=lambda entry: entry[1][::-1]),
        }
        orders = {
            name: [(f.path, f.line, f.column) for f in check_kit(root, listing).findings]
            for name, listing in listings.items()
        }
    expected = sorted(orders["as git lists them"])
    cases.check(
        len(set(expected)) == len(expected) == BASE_MENTIONS - 1 + 3
        and expected[0][0] == ".github/workflows/gates.yml"
        and expected[-1][0] == "pyproject.toml"
        and [o for o in expected if o[0] == "docs/two.md"]
        == [("docs/two.md", 1, 7), ("docs/two.md", 2, 1), ("docs/two.md", 2, 17)],
        "the findings are sorted by path, line and column, with the first and last typed by hand",
    )
    for name, order in orders.items():
        cases.check(order == expected, f"the findings stand in that order when git lists the files {name}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-copies", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 mentions examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(check_kit(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 mentions examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
