#!/usr/bin/env python3
"""Kit check: every copy of the Python floor names the floor's one minor, the `requires-python` of the
shared distribution is that floor, and each entry's three first lines close with its Identity's clause.

The floor's one source is `FLOOR` in `shared/constitution_layer_kit/preflight.py`, read here by `ast` and
never imported: a module-level assignment, the last one, plain or annotated, of a tuple of two integer
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

The distribution `constitution-layer-kit` holds a floor of its own that no form above can tell, since
pip reads it, not a person: `requires-python` under `[project]` in `shared/pyproject.toml`, read here by
`tomllib` and never matched as text. It must be the string `>=3.<minor>` with the source's minor, and no
other form: a `requires-python` of any other minor is RED, with its path and the line of the key, the value
found, the source, why and the fix. A file that is missing, unreadable, no TOML or not UTF-8, one with no
`requires-python` under `[project]`, one whose value is no string, and a string of another form, such as
a range `>=3.<minor>,<4`, a patch `>=3.<minor>.1`, `>3.<minor>` or `~=3.<minor>`, are BROKEN with the fix:
a floor in a form this check does not read could move unseen.

Not read: a symbolic link, mode 120000, whatever it points at, a dangling one too, since its target is
read through its own listing, once; a submodule, mode 160000; `docs/decisions/` and `docs/research/` at
the kit root, where records and frozen comparisons keep their words; a file git sees as binary, which is
git's own test, a NUL byte among its first 8000 bytes; and every version that is no copy of the floor,
`uv run -p 3.N`, a tool's own `FLOOR`, a measured `Python 3.N.M`. One form the check cannot tell from a
copy is read as one: the arguments of a call, `f(3, N)`. A file git sees as text that is not UTF-8 is
BROKEN with the fix, never a crash and never a skip, and so is a file git lists that the working tree lacks.

Each entry holds its clause in three places, which the Identity names a fourth time. An entry is a
file `modules/<module>/plugin/scripts/<stem>.py` directly under the `plugin/scripts/` of a module folder,
as `kit_module_doc.module_folders` lists them, that has a line opening `FLOOR = (3, `; a `.py` with that
line elsewhere, in `scripts/` of the kit, in a module's `scripts/` outside its `plugin/`, below
`plugin/scripts/`, or in a folder that is no module, is none. Its Identity is the
`Identity(...)` call, bare or through a module, found by `ast` in a `.py` file under
`modules/<module>/plugin/scripts/*_gate/` (at any depth), whose `gate=` keyword is the string `<stem>`, a call
that gives its gate any other way being none: exactly one, else BROKEN with the fix. Its clause is the
`until_installed=` keyword, a string literal, or, where the call has none, the default of the
`until_installed` field of the `Identity` class in `shared/constitution_layer_kit/identity.py`, also read by
`ast`. The texts are the first echo `BROKEN: ... needs python3 ...` of `<stem>.sh` (C1), and the string
constants `TOO_OLD` (C14) and `NO_SHARED_CODE` (C15) of the entry, the last top-level plain assignment of
each, read by `ast`; their first line is the text up to the first line feed. A first line reads `<what> — fix:
<fix>`, and what follows ` — ` after the fix is its clause. For a gate each of the three first lines must
close with ` — <the Identity's clause>` exactly. An entry is a generator when the second line of `TOO_OLD`
opens with neither `BROKEN: the check could not run` (C11) nor `BROKEN: the session-start line could not be
printed` (S1): its three first lines carry no clause, and its Identity's clause closes C2 alone, whatever
it is (template §6, rule 3; GATE.md §2, item 6). A disagreement is RED, with the file and line, the text,
the clause found, the clause the Identity names and where, why and the fix. BROKEN, with the fix: no entry
at all, a missing `.sh`, no or two Identities for a gate, a clause that is no string literal, an
`identity.py` that is missing, unreadable or without its default, which is read on every run, even when
every Identity names its own clause, a text that is missing or no string constant, a `TOO_OLD` with
no second line or an empty one, a first line with no ` — fix: ` part, and a file that is not Python.

Findings are sorted by path, then line, then column, whatever order git lists the files in. The green
line gives the mentions and the number of files that hold them, and the entries read.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway repository: a baseline of four entry pairs, their
                       module documents and install notes, the tool configuration and the workflow,
                       green with its literal line; an entry's floor and an install note red with their
                       literal lines; every form of the two lists, right green and one above and one
                       below red, and each form's closing guard green; records, comparisons, links, a
                       binary file, and the forms that are no copy green, with the edges of the binary
                       test, typed as numbers; the source with no floor, a float, a string, three numbers,
                       another major, a nested one, an unreadable or a missing file, a file that is not
                       UTF-8, git
                       missing and no repository, each a literal BROKEN line; the source moved with
                       every copy left, red on each of them; the order of the findings under an
                       adversarial listing; the misinvocation. The `requires-python` of the shared
                       distribution, in a baseline of its own: right green with its line in the report,
                       one minor above and one below red with literal lines, at the line of its key, the
                       source moved up with it left red, a comment naming another minor not read, and each
                       file or value that cannot be read as the form `>=3.<minor>` a literal BROKEN
                       line. The clauses, over the four kinds of entry, a gate on the default clause, a
                       gate with its own, a session-start printer and a generator: each of the three
                       texts of each kind changed alone red, the whole set in one loop, with literal
                       reports; an Identity's clause changed alone red three times, a generator's green;
                       the default of `identity.py` changed red for the gates on it alone, the keyword
                       and the default read wherever each stands among others; the first echo that
                       needs python3 read as C1, a tab after `echo` too, and a line whose fix dash has
                       no space before it no fix part; the shell files executable, as the kit's are;
                       two Identities, none, no `.sh`, a text missing, no string constant, one line, no
                       fix part and the other BROKEN cases as literal lines; entries outside any
                       module's plugin/scripts/ not read.
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
import tomllib
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, module_folders

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
SOURCE = "shared/constitution_layer_kit/preflight.py"
PROJECT = "shared/pyproject.toml"  # the shared distribution; its requires-python holds a floor
REQUIRES = re.compile(r"^>=3\.(\d+)$")  # the one form of requires-python this check reads
REQUIRES_KEY = re.compile(r"^requires-python\s*=", re.MULTILINE)  # where the key stands, for the line
NOT_READ = ("docs/decisions/", "docs/research/")  # records and frozen comparisons keep their words
REGULAR = ("100644", "100755")  # a symbolic link (120000) and a submodule (160000) are never read
GIT_BINARY = 8000  # git's own test: a NUL byte among the first 8000 bytes
WHY = (
    "a floor copied apart drifts, and the entry file that drifts prints a traceback where its designed"
    " teaching line should stand (law 6 of CLAUDE.md)"
)
GUARD = r"(?!\d|\.\d)"  # not followed by a digit nor `.<digit>`: a longer minor, or a measured `3.N.M`
IDENTITY = "shared/constitution_layer_kit/identity.py"  # the default clause's source
ENTRY_FLOOR = re.compile(
    r"^FLOOR = \(3, ", re.MULTILINE
)  # what makes a `.py` of a module's plugin/scripts/ an entry
SHELL_C1 = re.compile(r'^[ \t]*echo[ \t]+"(BROKEN: [^"\n]*needs python3[^"\n]*)"', re.MULTILINE)
CLOSINGS = (
    "BROKEN: the check could not run",
    "BROKEN: the session-start line could not be printed",
)  # C11, S1
FIX_PART = re.compile(r"^(.*? — fix: .*?)(?: — (.*))?$")  # a first line: what, the fix, the clause if any
WHY_CLAUSE = (
    "one gate's failure lines say one consequence, so a clause reworded in one place tells the user two"
    " things (law 6 of CLAUDE.md)"
)

Lister = Callable[[Path], list[tuple[str, str]]]
Build = Callable[[Path], None]  # a change the self-test makes to a fresh tree


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
    entries: int  # the entries whose clauses were read


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


def requires_floor(root: Path) -> tuple[int, int, str]:
    """The minor, the line of the key and the value of `requires-python` under `[project]` in the shared
    distribution's pyproject.toml, which must read `>=3.<minor>`, else BROKEN with the fix."""
    shape = 'write it as `requires-python = ">=3.<minor>"` under [project]'
    try:
        text = (root / PROJECT).read_text(encoding="utf-8")
        data = tomllib.loads(text)
    except FileNotFoundError as missing:
        raise Broken(
            f"{PROJECT} is missing — fix: restore the shared distribution's description, whose"
            " requires-python holds a copy of the floor"
        ) from missing
    except OSError as bad:
        raise Broken(f"{PROJECT} cannot be read ({bad.strerror}) — fix: make it readable") from bad
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as bad:
        raise Broken(f"{PROJECT} cannot be read as TOML ({bad}) — fix: repair the file") from bad
    project = data.get("project")
    value = project.get("requires-python") if isinstance(project, dict) else None
    key = REQUIRES_KEY.search(text)
    line = 1 if key is None else text.count("\n", 0, key.start()) + 1
    if not isinstance(value, str):
        raise Broken(f"{PROJECT} has no requires-python under [project] as a string — fix: {shape}")
    found = REQUIRES.match(value)
    if found is None:
        raise Broken(
            f"requires-python in {PROJECT}:{line} is '{value}', and this check reads the form >=3.<minor>"
            f" alone — fix: {shape}"
        )
    return int(found[1]), line, value


def requires_finding(found: int, line: int, value: str, minor: int) -> Finding:
    what = f"requires-python = '{value}' names 3.{found}, the floor is 3.{minor} ({SOURCE})"
    fix = f"write >=3.{minor}, or move the floor in {SOURCE} and every copy together"
    return Finding(PROJECT, line, 1, what, WHY, fix)


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


@dataclass(frozen=True)
class Entry:
    module: str
    stem: str
    path: str  # the entry's `.py`

    @property
    def shell(self) -> str:
        return f"modules/{self.module}/plugin/scripts/{self.stem}.sh"


@dataclass(frozen=True)
class Clause:
    """What an Identity names for `until_installed`, and where it says so."""

    text: str
    where: str


LABELS = {"C1": "C1, the shell entry's line", "C14": "C14, TOO_OLD", "C15": "C15, NO_SHARED_CODE"}


def parse(root: Path, path: str) -> ast.Module:
    text = contents(root, path)
    if text is None:
        raise Broken(f"{path} is binary, and the check reads it as Python — fix: restore the file")
    try:
        return ast.parse(text, filename=path)
    except (SyntaxError, ValueError) as bad:
        raise Broken(f"{path} cannot be read as Python ({bad}) — fix: repair the file") from bad


def string_constant(tree: ast.Module, name: str) -> tuple[str, int] | None:
    """The value and the line of the last top-level assignment of `name` to a string constant (adjacent
    literals are one constant), None when there is none or the last is anything else."""
    found: tuple[str, int] | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            value = node.value
            found = (
                (value.value, node.lineno)
                if isinstance(value, ast.Constant) and isinstance(value.value, str)
                else None
            )
    return found


def entries_of(root: Path, tracked: list[str]) -> list[Entry]:
    """The entries of the kit: a `.py` directly under `plugin/scripts/` of a module folder that has a line
    opening `FLOOR = (3, `, sorted by path; `tracked` is every regular file git lists."""
    try:
        modules = [folder.name for folder in module_folders(root)]
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    found: list[Entry] = []
    for path in tracked:
        parts = path.split("/")
        if (
            len(parts) == 5
            and parts[0] == "modules"
            and parts[1] in modules
            and parts[2] == "plugin"
            and parts[3] == "scripts"
            and parts[4].endswith(".py")
            and ENTRY_FLOOR.search(contents(root, path) or "")
        ):
            found.append(Entry(parts[1], parts[4].removesuffix(".py"), path))
    if not found:
        raise Broken(
            "no entry file found, no .py directly under plugin/scripts/ of a module with a line opening"
            " `FLOOR = (3, ` — fix: run the check from a checkout of the kit, whose modules carry them"
        )
    return sorted(found, key=lambda entry: entry.path)


def default_clause(root: Path) -> Clause:
    """The default of the `until_installed` field of the `Identity` class in the shared identity."""
    if not (root / IDENTITY).is_file():
        raise Broken(
            f"{IDENTITY} is missing — fix: restore the shared identity, whose Identity holds the"
            " default clause"
        )
    for node in parse(root, IDENTITY).body:
        if isinstance(node, ast.ClassDef) and node.name == "Identity":
            for field in node.body:
                if (
                    isinstance(field, ast.AnnAssign)
                    and isinstance(field.target, ast.Name)
                    and field.target.id == "until_installed"
                    and isinstance(field.value, ast.Constant)
                    and isinstance(field.value.value, str)
                ):
                    where = f"the default of until_installed, {IDENTITY}:{field.lineno}"
                    return Clause(field.value.value, where)
            raise Broken(
                f"class Identity in {IDENTITY} has no until_installed field with a string literal as its"
                ' default — fix: restore `until_installed: str = "until then ..."`, the default clause'
            )
    raise Broken(f"{IDENTITY} has no class Identity — fix: restore the shared identity")


def identities_of(tree: ast.Module, stem: str) -> list[ast.Call]:
    """The calls of `Identity`, bare or through a module, with the keyword `gate="<stem>"`."""
    found: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        named = (isinstance(func, ast.Name) and func.id == "Identity") or (
            isinstance(func, ast.Attribute) and func.attr == "Identity"
        )
        if named and any(
            keyword.arg == "gate" and isinstance(keyword.value, ast.Constant) and keyword.value.value == stem
            for keyword in node.keywords
        ):
            found.append(node)
    return found


def identity_clause(root: Path, tracked: list[str], entry: Entry, default: Clause) -> Clause:
    """The clause of the one Identity whose `gate=` is the entry's stem, in a `.py` under
    `modules/<module>/plugin/scripts/*_gate/`, at any depth."""
    folder = f"modules/{entry.module}/plugin/scripts/"
    calls: list[tuple[str, ast.Call]] = []
    for path in tracked:
        parts = path.split("/")
        if path.startswith(folder) and path.endswith(".py") and len(parts) > 5 and parts[4].endswith("_gate"):
            calls.extend((path, node) for node in identities_of(parse(root, path), entry.stem))
    calls.sort(key=lambda found: (found[0], found[1].lineno))
    if not calls:
        raise Broken(
            f'{entry.path} has no Identity(...) with gate="{entry.stem}" in a .py under {folder}*_gate/'
            f' — fix: declare it there, with gate="{entry.stem}", the Identity its clauses are held to'
        )
    if len(calls) > 1:
        at = " and ".join(f"{path}:{node.lineno}" for path, node in calls)
        raise Broken(
            f'{entry.path} has {len(calls)} Identities with gate="{entry.stem}", at {at}'
            " — fix: keep one, since an entry's clauses are held to its one Identity"
        )
    path, call = calls[0]
    for keyword in call.keywords:
        if keyword.arg == "until_installed":
            where = f"{path}:{keyword.value.lineno}"
            if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                return Clause(keyword.value.value, where)
            raise Broken(
                f"until_installed of the Identity at {where} is no string literal — fix: write it as one,"
                " which this check reads by ast"
            )
    return default


def first_clause(label: str, path: str, line: int, first: str) -> str | None:
    """The clause a first line closes with, after its fix: None when it has none."""
    found = FIX_PART.match(first)
    if found is None:
        raise Broken(
            f"the first line of {label} in {path}:{line} has no ' — fix: ' part, so its clause cannot be"
            " told — fix: write it as 'BROKEN: <what failed> — fix: <the fix>', and for a gate"
            " ' — <the Identity's clause>' after it"
        )
    return found[2]


def clause_finding(
    entry: Entry,
    name: str,
    path: str,
    line: int,
    found: str | None,
    declared: Clause,
    closing: str | None,
) -> Finding:
    """The disagreement of one text's clause; `closing` is `TOO_OLD`'s second line when the entry is a
    generator's, None for a gate."""
    label = LABELS[name]
    if closing is not None:
        what = (
            f"{label} of {entry.stem} ends in the clause '{found}', and a generator's entry lines carry none:"
            f" its Identity's clause, '{declared.text}' ({declared.where}), closes C2 alone"
        )
        why = (
            f"the second line of its TOO_OLD, '{closing}', is neither C11 nor S1, so the entry is a"
            " generator's, which changes files and lets no write through: a clause is true of C2 alone"
            " (template §6, rule 3; GATE.md §2, item 6)"
        )
        fix = "end the line at its fix, with no clause after it"
    else:
        got = "no clause" if found is None else f"'{found}'"
        what = (
            f"{label} of {entry.stem} ends in {got}, and its Identity names '{declared.text}'"
            f" ({declared.where})"
        )
        why = WHY_CLAUSE
        fix = (
            f"close the line with ' — {declared.text}', or change the Identity's until_installed and every"
            f" entry line of {entry.stem} together"
        )
    return Finding(path, line, 1, what, why, fix)


def entry_findings(root: Path, tracked: list[str], entry: Entry, default: Clause) -> list[Finding]:
    declared = identity_clause(root, tracked, entry, default)
    if entry.shell not in tracked:
        raise Broken(
            f"{entry.shell} is missing — fix: restore the entry's POSIX file, which prints C1 when python3"
            " is missing"
        )
    shell = contents(root, entry.shell)
    c1 = SHELL_C1.search(shell or "")
    if shell is None or c1 is None:
        raise Broken(
            f'{entry.shell} has no echo "BROKEN: ... needs python3 ..." line — fix: restore the line that'
            " is C1, the first such echo"
        )
    tree = parse(root, entry.path)
    constants: dict[str, tuple[str, int]] = {}
    for name in ("TOO_OLD", "NO_SHARED_CODE"):
        constant = string_constant(tree, name)
        if constant is None:
            raise Broken(
                f"{entry.path} has no {name} as a string constant at the top level — fix: write"
                f' {name} = ("..."), the text its entry prints'
            )
        constants[name] = constant
    too_old, line_old = constants["TOO_OLD"]
    lines = too_old.split("\n")
    if len(lines) < 2 or not lines[1]:
        raise Broken(
            f"TOO_OLD in {entry.path}:{line_old} has no second line — fix: end its first line with a line"
            " feed and give the closing line, C11, S1 or the generator's own"
        )
    closing = None if lines[1].startswith(CLOSINGS) else lines[1]  # not C11 nor S1: a generator's
    wanted = declared.text if closing is None else None
    found: list[Finding] = []
    for name, path, line, first in (
        ("C1", entry.shell, shell.count("\n", 0, c1.start()) + 1, c1[1]),
        ("C14", entry.path, line_old, lines[0]),
        ("C15", entry.path, constants["NO_SHARED_CODE"][1], constants["NO_SHARED_CODE"][0].split("\n")[0]),
    ):
        clause = first_clause(LABELS[name], path, line, first)
        if clause != wanted:
            found.append(clause_finding(entry, name, path, line, clause, declared, closing))
    return found


def check_kit(root: Path, listing: Lister = listed) -> Result:
    minor = floor_of(root)
    findings: list[Finding] = []
    total = holding = 0
    files = listing(root)
    for mode, path in files:
        if mode not in REGULAR or path.startswith(NOT_READ):
            continue
        text = contents(root, path)
        found = [] if text is None else mentions(text)
        total += len(found)
        holding += 1 if found else 0
        findings.extend(finding(path, m, minor) for m in found if m.found != minor - m.below)
    required, key_line, required_text = requires_floor(root)
    if required != minor:
        findings.append(requires_finding(required, key_line, required_text, minor))
    tracked = sorted(path for mode, path in files if mode in REGULAR)
    entries = entries_of(root, tracked)
    default = default_clause(root)
    for entry in entries:
        findings.extend(entry_findings(root, tracked, entry, default))
    findings.sort(key=lambda f: (f.path, f.line, f.column))
    return Result(findings, minor, total, holding, len(entries))


def report(result: Result) -> int:
    counts = f"{result.mentions} mention(s) in {result.files} file(s) examined"
    if result.findings:
        for item in result.findings:
            print(item.render())
        print(
            f"RED: {len(result.findings)} finding(s) — {counts} and {result.entries} entries read,"
            f" the floor 3.{result.minor} ({SOURCE})"
        )
        return EXIT_RED
    print(
        f"GREEN: every copy of the Python floor names 3.{result.minor} ({SOURCE}) — {counts}, requires-python"
        f" of {PROJECT} is >=3.{result.minor}, and each of {result.entries} entries' C1, C14 and C15 closes"
        " with its Identity's clause"
    )
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
OWN_CLAUSE = "until then shell commands pass unchecked"
PRINTER_CLAUSE = "until then the gate's state is not said at session start"
GENERATOR_CLAUSE = "until then nothing is made"
CHANGED = "until then it is changed"  # a clause that no Identity of the fixture names
GATE_CLOSING = "BROKEN: the check could not run — 0 documents examined"
SESSION_CLOSING = "BROKEN: the session-start line could not be printed — the gate's state is unknown"
GENERATOR_CLOSING = "BROKEN: the thing could not be made — nothing was written"


@dataclass(frozen=True)
class Spec:
    """One of the fixture's entries."""

    module: str
    stem: str
    clause: str | None  # what its entry lines close with; None: a generator's carry none
    identity: str | None  # the until_installed of its Identity; None: the keyword is left out
    closing: str  # the closing line of its entry files

    @property
    def package(self) -> str:
        return self.module.removeprefix("const-") + "_gate"

    def file(self, text: str) -> str:
        """The file that holds one of its texts: `sh`, `too_old` or `no_shared`."""
        return f"modules/{self.module}/plugin/scripts/{self.stem}.{'sh' if text == 'sh' else 'py'}"


SPECS = (
    Spec("const-a", "check-a", DEFAULT_CLAUSE, None, GATE_CLOSING),  # a gate on the default clause
    Spec("const-b", "check-b", OWN_CLAUSE, OWN_CLAUSE, GATE_CLOSING),  # a gate with its own clause
    Spec("const-c", "session-start", PRINTER_CLAUSE, PRINTER_CLAUSE, SESSION_CLOSING),  # a printer
    Spec("const-d", "make-thing", None, GENERATOR_CLAUSE, GENERATOR_CLOSING),  # a generator
)


def entry_python(module: str, minor: int, old: str | None, shared: str | None, closing: str) -> str:
    """An entry file as the kit's entries are written: the floor, then two texts of concatenated
    literals, each a first line and a closing line; `old` and `shared` are the clauses of TOO_OLD and
    NO_SHARED_CODE, None for none."""
    texts = []
    for name, first, clause in (
        (
            "TOO_OLD",
            f"BROKEN: {module} needs Python %d.%d or newer, found %d.%d — fix: install a Python",
            old,
        ),
        (
            "NO_SHARED_CODE",
            f"BROKEN: {module} is installed without its shared code — fix: install it",
            shared,
        ),
    ):
        first += "" if clause is None else f" — {clause}"
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


def put_entry(root: Path, spec: Spec, minor: int = BASE, given: dict[str, str | None] | None = None) -> None:
    """The entry pair of `spec`, its three texts closing with its clause but for those `given`, by `sh`,
    `too_old` and `no_shared`."""
    clauses = {"sh": spec.clause, "too_old": spec.clause, "no_shared": spec.clause} | (given or {})
    python = entry_python(spec.module, minor, clauses["too_old"], clauses["no_shared"], spec.closing)
    put(root, spec.file("too_old"), python)
    put(root, spec.file("sh"), entry_shell(spec.module, spec.stem, minor, clauses["sh"], spec.closing))
    (root / spec.file("sh")).chmod(0o755)  # the kit's entry files are executable: git lists them as 100755


def put_identity(root: Path, spec: Spec, clause: str | None, name: str = "start.py", gate: str = "") -> None:
    """The Identity of `spec` in its package, with the keyword for `clause` unless it is None."""
    until = "" if clause is None else f"    until_installed={clause!r},\n"
    put(
        root,
        f"modules/{spec.module}/plugin/scripts/{spec.package}/{name}",
        "from constitution_layer_kit.identity import Identity\n\nGATE = Identity(\n"
        f"    namespace={spec.module!r},\n    gate={(gate or spec.stem)!r},\n"
        f"    plugin_root=None,\n{until})\n",
    )


def identity_source(default: str, fixed_first: bool = False, other_first: str | None = None) -> str:
    """The shared identity of the fixture: `fixed_first` puts the `until_fixed` field before
    `until_installed`; `other_first` puts a class of another name, holding an `until_installed` field with
    that default, before `class Identity`."""
    fixed = "    until_fixed: str = 'until it is fixed'\n"
    installed = f"    until_installed: str = {default!r}\n"
    other = "" if other_first is None else f"class Other:\n    until_installed: str = {other_first!r}\n\n\n"
    return (
        '"""The identity."""\n\nfrom dataclasses import dataclass\n\n\n' + other + "@dataclass(frozen=True)\n"
        "class Identity:\n    namespace: str\n    libraries: str = 'none'\n"  # a default before, one after
         + (fixed + installed if fixed_first else installed + fixed)
    )


def stage(root: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)


def remove(root: Path, path: str) -> None:
    subprocess.run(["git", "rm", "-q", "-f", path], cwd=root, check=True, capture_output=True)


REQUIRES_LINE = 6  # the line of requires-python in the fixture's shared pyproject.toml


def requires_toml(value: str) -> str:
    """The shared distribution's pyproject.toml of the fixture, its requires-python at REQUIRES_LINE."""
    return (
        f'[build-system]\nrequires = ["setuptools"]\n\n[project]\nname = "x"\nrequires-python = "{value}"\n'
    )


def fresh(root: Path, minor: int = BASE, floor: int | None = None) -> None:
    """A throwaway kit whose every copy of the floor names `minor`, the source `floor` (default the
    same): four modules, each with its document, install note, entry pair and Identity, and the shared
    identity and distribution, whose requires-python is `>=3.<minor>`; the root install note, the tool
    configuration, the workflow, a record and a comparison that name another minor."""
    try:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as failed:
        raise Broken(f"git init failed in {root} — fix: install git, then run the self-test") from failed
    put(root, SOURCE, f'"""The preflight."""\n\nFLOOR = (3, {minor if floor is None else floor})\n')
    put(root, IDENTITY, identity_source(DEFAULT_CLAUSE))
    put(root, PROJECT, requires_toml(f">=3.{minor}"))
    put(root, "INSTALL.md", f"# Install\n\nNeeds Python 3.{minor} or newer.\n")
    put(
        root,
        "pyproject.toml",
        f'[tool.ruff]\ntarget-version = "py3{minor}"\n\n[tool.mypy]\npython_version = "3.{minor}"\n',
    )
    put(root, ".github/workflows/gates.yml", f'steps:\n  - with:\n      python-version: "3.{minor}"\n')
    put(root, "docs/decisions/adr-0001-old.md", f"The floor was Python 3.{OLD} once.\n")
    put(root, "docs/research/rfc-0001-survey.md", f"A survey on Python 3.{OLD}, frozen.\n")
    for spec in SPECS:
        put(
            root,
            f"modules/{spec.module}/MODULE.md",
            f"A module: needs git, Python 3.{minor}. The floor (3.{minor}).\n",
        )
        put(root, f"modules/{spec.module}/plugin/INSTALL.md", f"Install it. Python 3.{minor} or newer.\n")
        put_entry(root, spec, minor)
        put_identity(root, spec, spec.identity)
    put(  # the forms that name one minor below the floor, where a runner fakes the interpreter
        root,
        "modules/const-a/tests/run.py",
        f"CODE = 'import sys; sys.version_info = (3, {minor - 1}, 0)'\nSAID = 'found 3.{minor - 1}'\n",
    )
    put(root, "modules/const-a/NOTE.md", f"The runner uses an interpreter of 3.{minor - 1}.\n")
    stage(root)


# The mentions of the baseline tree, by hand: the source 1; INSTALL.md 1; pyproject.toml 2 (`py3N` and the
# type checker's); the workflow 1; four MODULE.md 2 each (`Python 3.N`, `(3.N)`) = 8; four install notes 1
# each = 4; four entry pairs 2 each (`FLOOR = (3, N)` and the `.sh`'s `Python 3.N`) = 8; the runner 2
# (`found`, `version_info`) and the note 1 (`an interpreter of`) = 3: 28, in 1 + 1 + 1 + 1 + 4 + 4 + 8 + 2
# = 22 files.
BASE_MENTIONS, BASE_FILES = 28, 22
BASE_ENTRIES = len(SPECS)

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


@contextlib.contextmanager
def listed_in_reverse() -> Iterator[None]:
    """For the cases inside, `Path.iterdir` yields its entries sorted by name and reversed, whatever the
    filesystem lists. Restored on leaving."""
    real = Path.iterdir

    def reversed_iterdir(self: Path) -> Iterator[Path]:
        return iter(sorted(real(self), key=lambda path: path.name, reverse=True))

    Path.iterdir = reversed_iterdir  # type: ignore[method-assign,assignment]
    try:
        yield
    finally:
        Path.iterdir = real  # type: ignore[method-assign]


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
                f"GREEN: every copy of the Python floor names 3.{BASE}"
                " (shared/constitution_layer_kit/preflight.py)"
                f" — {BASE_MENTIONS} mention(s) in {BASE_FILES} file(s) examined, requires-python of"
                f" shared/pyproject.toml is >=3.{BASE}, and each of {BASE_ENTRIES} entries' C1, C14 and C15"
                " closes with its Identity's clause"
            ],
            "the baseline is green, with its literal line",
        )
    self_test_reds(cases)
    self_test_forms(cases)
    self_test_guards(cases)
    self_test_not_read(cases)
    self_test_broken(cases)
    self_test_requires(cases)
    self_test_clauses(cases)
    self_test_clause_reports(cases)
    self_test_identities(cases)
    self_test_clause_broken(cases)
    self_test_entry_scope(cases)
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
        f"{BASE_MENTIONS} mention(s) in {BASE_FILES} file(s) examined and {BASE_ENTRIES} entries read,"
        f" the floor 3.{BASE} (shared/constitution_layer_kit/preflight.py)"
    )
    move = "or move the floor in shared/constitution_layer_kit/preflight.py and every copy together"
    fix = f"  fix: write 3.{BASE}, {move}"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(
            root,
            "modules/const-a/plugin/scripts/check-a.py",
            entry_python("const-a", OLD, DEFAULT_CLAUSE, DEFAULT_CLAUSE, GATE_CLOSING),
        )
        code, lines = run_report(root)
        cases.check(
            code == EXIT_RED
            and lines
            == [
                f"RED: modules/const-a/plugin/scripts/check-a.py:5: '(3, {OLD})' names 3.{OLD},"
                f" the floor is 3.{BASE} (shared/constitution_layer_kit/preflight.py)",
                why,
                fix,
                f"RED: 1 finding(s) — {counts}",
            ],
            "an entry's FLOOR one minor below is red, with its literal lines",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "modules/const-c/plugin/INSTALL.md", f"Install it. Python 3.{OVER} or newer.\n")
        code, lines = run_report(root)
        cases.check(
            code == EXIT_RED
            and lines
            == [
                f"RED: modules/const-c/plugin/INSTALL.md:1: 'Python 3.{OVER}' names 3.{OVER}, the floor is"
                f" 3.{BASE}"
                " (shared/constitution_layer_kit/preflight.py)",
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
            f" the floor, 3.{BASE} (shared/constitution_layer_kit/preflight.py), is 3.{OLD}"
            and lines[2] == f"  fix: write 3.{OLD}, {move}",
            "a form for the minor below the floor, naming the floor itself, is red with its literal lines",
        )
    with tempfile.TemporaryDirectory() as tmp:  # the source moved, every copy left
        root = Path(tmp).resolve()
        fresh(root, minor=BASE, floor=OVER)
        result = check_kit(root)
        paths = {f.path for f in result.findings}
        cases.check(
            len(result.findings) == BASE_MENTIONS - 1 + 1  # the source's own literal names the new floor
            and result.minor == OVER
            and SOURCE not in paths
            and PROJECT in paths
            and len(paths) == BASE_FILES - 1 + 1,
            f"the source moved up with every copy left: red on each of the other {BASE_MENTIONS - 1}"
            f" mentions, in each of their {BASE_FILES - 1} files, and on requires-python of {PROJECT}",
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
        ("docs/decisions/adr-0002-old.md", "a record under docs/decisions/"),
        ("docs/research/rfc-0002-old.md", "a comparison under docs/research/"),
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
        link(root, "modules/const-a/linked.md", "../../docs/research/rfc-0001-survey.md")
        link(root, "modules/const-a/dangling.md", "nowhere.md")
        link(root, "modules/const-a/plugin/INSTALL-copy.md", "INSTALL.md")
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
        # the same edges typed as numbers, so that a moved GIT_BINARY cannot move them with it
        ("a NUL at byte offset 7999, the 8000th", old.encode() + b" " * (7999 - len(old)) + b"\0", False),
        ("a NUL at byte offset 8000, the 8001st", old.encode() + b" " * (8000 - len(old)) + b"\0", True),
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


def with_project(text: str) -> Build:
    """A change to a fresh tree that gives the shared pyproject.toml this text."""
    return lambda root: put(root, PROJECT, text)


def self_test_requires(cases: Cases) -> None:
    """The `requires-python` of the shared distribution, held to the source's floor."""
    why = (
        "  why: a floor copied apart drifts, and the entry file that drifts prints a traceback where its"
        " designed teaching line should stand (law 6 of CLAUDE.md)"
    )
    counts = (
        f"{BASE_MENTIONS} mention(s) in {BASE_FILES} file(s) examined and {BASE_ENTRIES} entries read,"
        f" the floor 3.{BASE} (shared/constitution_layer_kit/preflight.py)"
    )
    move = "or move the floor in shared/constitution_layer_kit/preflight.py and every copy together"
    for word, found in (("above", OVER), ("below", OLD), ("far above, a longer minor", int(f"{BASE}0"))):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, PROJECT, requires_toml(f">=3.{found}"))
            code, lines = run_report(root)
        cases.check(
            code == EXIT_RED
            and lines
            == [
                f"RED: shared/pyproject.toml:{REQUIRES_LINE}: requires-python = '>=3.{found}' names"
                f" 3.{found}, the floor is 3.{BASE} (shared/constitution_layer_kit/preflight.py)",
                why,
                f"  fix: write >=3.{BASE}, {move}",
                f"RED: 1 finding(s) — {counts}",
            ],
            f"a requires-python {word} the floor is red, with its literal lines",
        )
    right = f">=3.{BASE}"
    for name, text, line in (
        (
            "a comment that names another minor, above the key: the key is the one at its own line",
            f'# was ">=3.{OLD}"\n[project]\nname = "x"\nrequires-python = ">=3.{OVER}"\n',
            4,
        ),
        (
            "the key among others, in single quotes and with no space before the equal sign",
            f"[project]\nname = 'x'\ndependencies = []\nrequires-python='>=3.{OVER}'\n",
            4,
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, PROJECT, text)
            result = check_kit(root)
        cases.check(
            [(f.path, f.line, f.column) for f in result.findings] == [(PROJECT, line, 1)],
            f"{name}: red once, at line {line}",
        )
    for name, text in (
        (
            "a comment that names another minor, below the right key",
            f'# was ">=3.{OLD}"\n' + requires_toml(right),
        ),
        ("the right value in single quotes", f"[project]\nrequires-python = '{right}'\n"),
        (
            "the right key after other tables and keys",
            f'[tool.x]\nrequires-python = ">=3.{OLD}"\n\n[project]\nrequires-python = "{right}"\n',
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, PROJECT, text)
            result = check_kit(root)
        cases.check(result.findings == [] and result.mentions == BASE_MENTIONS, f"{name} is green")
    shape = 'write it as `requires-python = ">=3.<minor>"` under [project]'
    no_key = f"{PROJECT} has no requires-python under [project] as a string — fix: {shape}"
    for name, text, expected in (
        ("a table with no [project]", '[build-system]\nrequires = ["setuptools"]\n', no_key),
        ("a [project] with no requires-python", '[project]\nname = "x"\n', no_key),
        ("a requires-python under another table", f'[tool.x]\nrequires-python = "{right}"\n', no_key),
        ("a requires-python that is a list", f'[project]\nrequires-python = ["{right}"]\n', no_key),
        ("a requires-python that is a number", f"[project]\nrequires-python = {BASE}\n", no_key),
        (
            "an empty file",
            "",
            no_key,
        ),
    ):
        cases.check(
            broken_with(with_project(text)) == expected,
            f"{name} is its literal BROKEN line",
        )
    for form in (
        f">=3.{BASE},<4",
        f">=3.{BASE}.1",
        f">3.{BASE}",
        f"~=3.{BASE}",
        f"<=3.{BASE}",
        f"== 3.{BASE}",
        f">= 3.{BASE}",
        ">=3",
        "",
    ):
        cases.check(
            broken_with(with_project(requires_toml(form))) == f"requires-python in {PROJECT}:"
            f"{REQUIRES_LINE} is '{form}', and this check reads the form >=3.<minor> alone — fix: {shape}",
            f"a requires-python of the form '{form}' is its literal BROKEN line",
        )
    said = broken_with(lambda r: put(r, PROJECT, "requires-python = \n"))
    cases.check(
        said.startswith(f"{PROJECT} cannot be read as TOML (") and said.endswith(") — fix: repair the file"),
        "a shared pyproject.toml that is no TOML is a teaching BROKEN line",
    )
    cases.check(
        broken_with(lambda r: remove(r, PROJECT))
        == f"{PROJECT} is missing — fix: restore the shared distribution's description, whose requires-python"
        " holds a copy of the floor",
        "a missing shared pyproject.toml is its literal BROKEN line",
    )
    with tempfile.TemporaryDirectory() as tmp:  # the file git does not list, so the loop never reads it
        root = Path(tmp).resolve()
        fresh(root)
        subprocess.run(["git", "rm", "--cached", "-q", PROJECT], cwd=root, check=True, capture_output=True)
        put(root, PROJECT, b"\xff\xfe")
        said = broken_line(root)
        cases.check(
            said.startswith(f"{PROJECT} cannot be read as TOML (")
            and "invalid start byte" in said
            and said.endswith(") — fix: repair the file"),
            "a shared pyproject.toml that git does not list and that is no UTF-8 is a teaching BROKEN line",
        )


def write_plain(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# the clauses' cases name their lines and labels by hand: the line of each text in the fixture's entry files
TEXT_LINES = {"sh": 4, "too_old": 7, "no_shared": 13}
TEXT_LABELS = {
    "sh": "C1, the shell entry's line",
    "too_old": "C14, TOO_OLD",
    "no_shared": "C15, NO_SHARED_CODE",
}
KINDS = (
    ("a gate on the default clause", SPECS[0]),
    ("a gate with its own clause", SPECS[1]),
    ("a session-start printer", SPECS[2]),
    ("a generator", SPECS[3]),
)
ALL_CHANGED: dict[str, str | None] = {"sh": CHANGED, "too_old": CHANGED, "no_shared": CHANGED}
UNTIL_LINE = 7  # the line of `until_installed=` in the fixture's Identity file
IDENTITY_LINE = 10  # the line of the default in the fixture's identity.py


def self_test_clauses(cases: Cases) -> None:
    """The whole set, kinds by texts: each text changed alone is red once, at its own line, whatever
    the kind; the three together are red three times, in the order of path and line."""
    for kind, spec in KINDS:
        changes: list[tuple[str, str | None]] = (
            [("given a clause", CHANGED)]
            if spec.clause is None
            else [
                ("reworded", CHANGED),
                ("dropped", None),
                ("with a stray part before it", f"stray — {spec.clause}"),
                ("with a part after it", f"{spec.clause} — more"),
            ]
        )
        for text, label in TEXT_LABELS.items():
            for change, clause in changes:
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp).resolve()
                    fresh(root)
                    put_entry(root, spec, given={text: clause})
                    result = check_kit(root)
                found = [(f.path, f.line, f.what.startswith(label)) for f in result.findings]
                cases.check(
                    found == [(spec.file(text), TEXT_LINES[text], True)],
                    f"{kind}: its {label} {change} alone is red, once, at its own line",
                )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            put_entry(root, spec, given=ALL_CHANGED)
            result = check_kit(root)
        cases.check(
            [(f.path, f.line) for f in result.findings]
            == [
                (spec.file("too_old"), TEXT_LINES["too_old"]),
                (spec.file("no_shared"), TEXT_LINES["no_shared"]),
                (spec.file("sh"), TEXT_LINES["sh"]),
            ],
            f"{kind}: its three texts changed together are red three times, by path and line",
        )
    with tempfile.TemporaryDirectory() as tmp:  # the last of two assignments is the text
        root = Path(tmp).resolve()
        fresh(root)
        text = (root / SPECS[0].file("too_old")).read_text(encoding="utf-8")
        put(
            root,
            SPECS[0].file("too_old"),
            text + 'TOO_OLD = "BROKEN: x — fix: y — z\\nBROKEN: the check could not run\\n"\n',
        )
        wrong = [(f.path, f.line) for f in check_kit(root).findings]
        put(
            root,
            SPECS[0].file("too_old"),
            'TOO_OLD = "BROKEN: x — fix: y — z\\nBROKEN: the check could not run\\n"\n' + text,
        )
        right = check_kit(root).findings
    cases.check(
        wrong == [(SPECS[0].file("too_old"), 18)] and right == [],
        "TOO_OLD assigned twice: the last assignment is the text",
    )
    with tempfile.TemporaryDirectory() as tmp:  # the kit's entry files are executable, mode 100755
        root = Path(tmp).resolve()
        fresh(root)
        modes = {path: mode for mode, path in listed(root)}
        executable = [modes[spec.file("sh")] for spec in SPECS]
        put(
            root,
            SPECS[0].file("sh"),  # a floor mention one minor up, and a clause reworded, in an executable file
            entry_shell("const-a", "check-a", OVER, CHANGED, GATE_CLOSING),
        )
        result = check_kit(root)
    cases.check(
        executable == ["100755"] * BASE_ENTRIES
        and [(f.path, f.line, f.column, f.what.startswith("C1")) for f in result.findings]
        == [(SPECS[0].file("sh"), 4, 1, True), (SPECS[0].file("sh"), 4, 54, False)]
        and result.mentions == BASE_MENTIONS
        and result.entries == BASE_ENTRIES,
        "an executable shell entry, mode 100755, is read: its C1 is checked and its floor mention counted",
    )


def self_test_clause_reports(cases: Cases) -> None:
    """The report of a disagreement as literal lines, one for each kind of finding."""
    why = (
        "  why: one gate's failure lines say one consequence, so a clause reworded in one place tells the"
        " user two things (law 6 of CLAUDE.md)"
    )
    summary = (
        f"RED: 1 finding(s) — {BASE_MENTIONS} mention(s) in {BASE_FILES} file(s) examined and"
        f" {BASE_ENTRIES} entries read, the floor 3.{BASE} (shared/constitution_layer_kit/preflight.py)"
    )
    default_where = (
        f"the default of until_installed, shared/constitution_layer_kit/identity.py:{IDENTITY_LINE}"
    )
    printer_where = f"modules/const-c/plugin/scripts/c_gate/start.py:{UNTIL_LINE}"
    generator_where = f"modules/const-d/plugin/scripts/d_gate/start.py:{UNTIL_LINE}"
    for name, spec, text, clause, expected in (
        (
            "a gate on the default clause, C1 reworded",
            SPECS[0],
            "sh",
            CHANGED,
            [
                "RED: modules/const-a/plugin/scripts/check-a.sh:4: C1, the shell entry's line of check-a"
                " ends in"
                f" '{CHANGED}', and its Identity names '{DEFAULT_CLAUSE}' ({default_where})",
                why,
                f"  fix: close the line with ' — {DEFAULT_CLAUSE}', or change the Identity's until_installed"
                " and every entry line of check-a together",
                summary,
            ],
        ),
        (
            "a printer, C14 dropped",
            SPECS[2],
            "too_old",
            None,
            [
                "RED: modules/const-c/plugin/scripts/session-start.py:7: C14, TOO_OLD of session-start ends"
                " in no"
                f" clause, and its Identity names '{PRINTER_CLAUSE}' ({printer_where})",
                why,
                f"  fix: close the line with ' — {PRINTER_CLAUSE}', or change the Identity's until_installed"
                " and every entry line of session-start together",
                summary,
            ],
        ),
        (
            "a generator, C15 given a clause",
            SPECS[3],
            "no_shared",
            CHANGED,
            [
                "RED: modules/const-d/plugin/scripts/make-thing.py:13: C15, NO_SHARED_CODE of make-thing ends"
                " in"
                f" the clause '{CHANGED}', and a generator's entry lines carry none: its Identity's clause,"
                f" '{GENERATOR_CLAUSE}' ({generator_where}), closes C2 alone",
                f"  why: the second line of its TOO_OLD, '{GENERATOR_CLOSING}', is neither C11 nor S1, so the"
                " entry is a generator's, which changes files and lets no write through: a clause is true of"
                " C2 alone (template §6, rule 3; GATE.md §2, item 6)",
                "  fix: end the line at its fix, with no clause after it",
                summary,
            ],
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            put_entry(root, spec, given={text: clause})
            code, lines = run_report(root)
        cases.check(code == EXIT_RED and lines == expected, f"{name} is its literal report, exit 2")


def self_test_identities(cases: Cases) -> None:
    """What an entry's clause is held to: its Identity's keyword, else the default; and which Identity."""
    for kind, spec in KINDS[:3]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            put_identity(root, spec, CHANGED)
            result = check_kit(root)
        where = f"modules/{spec.module}/plugin/scripts/{spec.package}/start.py:{UNTIL_LINE}"
        cases.check(
            [(f.path, f.line) for f in result.findings]
            == [(spec.file("too_old"), 7), (spec.file("no_shared"), 13), (spec.file("sh"), 4)]
            and all(f"names '{CHANGED}' ({where})" in f.what for f in result.findings),
            f"{kind}: its Identity's clause changed alone is red three times, naming where it is",
        )
    with tempfile.TemporaryDirectory() as tmp:  # a generator's Identity clause closes C2 alone
        root = Path(tmp).resolve()
        fresh(root)
        put_identity(root, SPECS[3], CHANGED)
        result = check_kit(root)
    cases.check(
        result.findings == [], "a generator's Identity clause changed alone is green: it closes C2 alone"
    )
    with tempfile.TemporaryDirectory() as tmp:  # the default, read from identity.py
        root = Path(tmp).resolve()
        fresh(root)
        put(root, IDENTITY, identity_source(CHANGED))
        result = check_kit(root)
    cases.check(
        [(f.path, f.line) for f in result.findings]
        == [(SPECS[0].file("too_old"), 7), (SPECS[0].file("no_shared"), 13), (SPECS[0].file("sh"), 4)]
        and all(
            f"(the default of until_installed, {IDENTITY}:{IDENTITY_LINE})" in f.what for f in result.findings
        ),
        "the default of identity.py changed is red three times, for the gate on the default alone",
    )
    other = SPECS[1]
    builds: list[tuple[str, Build]] = [
        (
            "the Identity of another gate name in the same package",
            lambda r: put_identity(r, SPECS[0], CHANGED, "other.py", "check-a-x"),
        ),
        (
            "an Identity of the same gate name in another module",
            lambda r: put_identity(r, other, CHANGED, "other.py", "check-a"),
        ),
        (
            "an Identity of the same gate name outside a package ending in _gate",
            lambda r: put(
                r,
                "modules/const-a/plugin/scripts/helpers/x.py",
                "Identity(gate='check-a', until_installed='x')\n",
            ),
        ),
        (
            "an Identity of the same gate name in a package named _gates",
            lambda r: put(
                r,
                "modules/const-a/plugin/scripts/a_gates/x.py",
                "Identity(gate='check-a', until_installed='x')\n",
            ),
        ),
        (
            "an Identity whose gate is no literal",
            lambda r: put(
                r, "modules/const-a/plugin/scripts/a_gate/x.py", "Identity(gate=NAME, until_installed='x')\n"
            ),
        ),
        (
            "an Identity of the same gate name with its arguments in a mapping",
            lambda r: put(r, "modules/const-a/plugin/scripts/a_gate/x.py", "Identity(**ARGS)\n"),
        ),
        (
            "an Identity of the same gate name in a file of the package that is no .py",
            lambda r: put(r, "modules/const-a/plugin/scripts/a_gate/notes.md", "Identity(gate='check-a')\n"),
        ),
        (
            "an Identity of the same gate name in a symbolic link to the Identity file",
            lambda r: link(r, "modules/const-a/plugin/scripts/a_gate/second.py", "start.py"),
        ),
        (
            "a C1 echo behind a commented one and another echo: the first of the live echoes is read",
            lambda r: put(
                r,
                SPECS[0].file("sh"),
                '#!/bin/sh\n# echo "BROKEN: const-a needs python3 — fix: x — wrong"\necho "hello"\n'
                f'  echo "BROKEN: const-a needs python3 — fix: x — {DEFAULT_CLAUSE}" >&2\n'
                '  echo "BROKEN: const-a needs python3 — fix: x — wrong" >&2\n',
            ),
        ),
    ]
    for name, build in builds:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            build(root)
            stage(root)
            result = check_kit(root)
        cases.check(
            result.findings == [] and result.entries == BASE_ENTRIES,
            f"{name} is not the entry's Identity: green",
        )
    for name, place, call in (
        ("an Identity in a folder of the package, deeper than its top", "a_gate/sub/start.py", "Identity"),
        ("an Identity called through a module", "a_gate/start.py", "identity.Identity"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            remove(root, "modules/const-a/plugin/scripts/a_gate/start.py")
            put(
                root,
                f"modules/const-a/plugin/scripts/{place}",
                f"GATE = {call}(namespace='const-a', gate='check-a')\n",
            )
            stage(root)
            result = check_kit(root)
        cases.check(result.findings == [], f"{name} is read, the default clause applying")
    self_test_c1_line(cases)
    self_test_which_clause(cases)


def self_test_c1_line(cases: Cases) -> None:
    """Which echo of the `.sh` is C1: the first `BROKEN: ... needs python3 ...`, a tab after `echo` read."""
    head = "#!/bin/sh\nif true; then\n"
    right = f'"BROKEN: const-a needs python3 — fix: x — {DEFAULT_CLAUSE}"'
    wrong = '"BROKEN: const-a needs python3 — fix: x — wrong"'
    for name, text in (
        (
            "a BROKEN echo without needs python3 before the real C1",
            f'{head}  echo "BROKEN: const-a could not start — fix: x — wrong" >&2\n  echo {right} >&2\nfi\n',
        ),
        (
            "a tab after echo in the C1 line, before a spaced echo with another clause",
            f"{head}  echo\t{right} >&2\n  echo {wrong} >&2\nfi\n",
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            put(root, SPECS[0].file("sh"), text)
            result = check_kit(root)
        cases.check(
            result.findings == [] and result.entries == BASE_ENTRIES,
            f"{name}: the line that needs python3 is C1, green",
        )


def self_test_which_clause(cases: Cases) -> None:
    """Which text is an Identity's clause: its `until_installed` keyword, wherever it stands among the
    keywords, else the default of the `until_installed` field of `class Identity`, wherever that stands."""
    other = SPECS[1]
    wins: list[tuple[str, Spec, Build]] = [
        (
            "an Identity with until_fixed= before until_installed=: the clause is until_installed's",
            other,
            lambda r: put(
                r,
                f"modules/{other.module}/plugin/scripts/{other.package}/start.py",
                f"GATE = Identity(gate={other.stem!r}, until_fixed='until it is fixed',"
                f" until_installed={OWN_CLAUSE!r})\n",
            ),
        ),
        (
            "an identity.py with the until_fixed field before until_installed: the default is the latter's",
            SPECS[0],
            lambda r: put(r, IDENTITY, identity_source(DEFAULT_CLAUSE, fixed_first=True)),
        ),
        (
            "an identity.py with another class holding until_installed before class Identity: the default"
            " is Identity's",
            SPECS[0],
            lambda r: put(r, IDENTITY, identity_source(DEFAULT_CLAUSE, other_first=CHANGED)),
        ),
    ]
    for name, spec, build in wins:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            build(root)
            stage(root)
            result = check_kit(root)
        cases.check(
            result.findings == [] and result.entries == BASE_ENTRIES,
            f"{name}: {spec.stem} stays green",
        )


def broken_with(build: Build) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        build(root)
        stage(root)
        return broken_line(root)


def remove_entries(root: Path) -> None:
    for spec in SPECS:
        remove(root, spec.file("too_old"))


def remove_identity_of_named(root: Path) -> None:
    """The shared identity gone, with no gate left that needs its default."""
    put_identity(root, SPECS[0], DEFAULT_CLAUSE)
    remove(root, IDENTITY)


def self_test_clause_broken(cases: Cases) -> None:
    """Every tree the clauses cannot be read from, as the literal BROKEN line it teaches."""
    entry, shell = SPECS[0].file("too_old"), SPECS[0].file("sh")
    folder = "modules/const-a/plugin/scripts/"
    start = f"{folder}a_gate/start.py"
    closing = "BROKEN: the check could not run\\n"
    py_head = f"FLOOR = (3, {BASE})\n"
    no_constant = (
        ' as a string constant at the top level — fix: write {} = ("..."), the text its entry prints'
    )
    no_fix = (
        " has no ' — fix: ' part, so its clause cannot be told — fix: write it as 'BROKEN: <what failed>"
        " — fix: <the fix>', and for a gate ' — <the Identity's clause>' after it"
    )
    no_second = (
        " has no second line — fix: end its first line with a line feed and give the closing line, C11, S1"
        " or the generator's own"
    )
    no_default = (
        f"class Identity in {IDENTITY} has no until_installed field with a string literal as its default"
        ' — fix: restore `until_installed: str = "until then ..."`, the default clause'
    )
    for name, build, expected in (
        (
            "two Identities of one gate name in two files",
            lambda r: put_identity(r, SPECS[0], None, "second.py"),
            f'{entry} has 2 Identities with gate="check-a", at {folder}a_gate/second.py:3 and {start}:3'
            " — fix: keep one, since an entry's clauses are held to its one Identity",
        ),
        (
            "two Identities of one gate name in one file",
            lambda r: put(
                r, start, (r / start).read_text(encoding="utf-8") + "\nOTHER = Identity(gate='check-a')\n"
            ),
            f'{entry} has 2 Identities with gate="check-a", at {start}:3 and {start}:9'
            " — fix: keep one, since an entry's clauses are held to its one Identity",
        ),
        (
            "two Identities, the later in the file nested the deeper",
            lambda r: put(
                r,
                start,
                "def make():\n    return Identity(namespace='const-a', gate='check-a')\n\n"
                "GATE = Identity(namespace='const-a', gate='check-a')\n",
            ),
            f'{entry} has 2 Identities with gate="check-a", at {start}:2 and {start}:4'
            " — fix: keep one, since an entry's clauses are held to its one Identity",
        ),
        (
            "an entry with no Identity",
            lambda r: remove(r, start),
            f'{entry} has no Identity(...) with gate="check-a" in a .py under {folder}*_gate/'
            ' — fix: declare it there, with gate="check-a", the Identity its clauses are held to',
        ),
        (
            "an entry with no shell file",
            lambda r: remove(r, shell),
            f"{shell} is missing — fix: restore the entry's POSIX file, which prints C1 when python3 is"
            " missing",
        ),
        (
            "a shell file with no C1 line",
            lambda r: put(r, shell, "#!/bin/sh\necho hello\n"),
            f'{shell} has no echo "BROKEN: ... needs python3 ..." line — fix: restore the line that is C1,'
            " the first such echo",
        ),
        (
            "a shell file whose only BROKEN echo does not say it needs python3",
            lambda r: put(r, shell, '#!/bin/sh\necho "BROKEN: const-a could not start — fix: x — y" >&2\n'),
            f'{shell} has no echo "BROKEN: ... needs python3 ..." line — fix: restore the line that is C1,'
            " the first such echo",
        ),
        (
            "an entry with no TOO_OLD",
            lambda r: put(r, entry, py_head + "NO_SHARED_CODE = 'a — fix: b'\n"),
            f"{entry} has no TOO_OLD" + no_constant.format("TOO_OLD"),
        ),
        (
            "an entry with no NO_SHARED_CODE",
            lambda r: put(r, entry, py_head + f"TOO_OLD = 'a — fix: b\\n{closing}'\n"),
            f"{entry} has no NO_SHARED_CODE" + no_constant.format("NO_SHARED_CODE"),
        ),
        (
            "a TOO_OLD that is two literals added",
            lambda r: put(r, entry, py_head + "TOO_OLD = 'a' + 'b'\nNO_SHARED_CODE = 'c'\n"),
            f"{entry} has no TOO_OLD" + no_constant.format("TOO_OLD"),
        ),
        (
            "a NO_SHARED_CODE that is an f-string",
            lambda r: put(
                r, entry, py_head + f"TOO_OLD = 'a — fix: b\\n{closing}'\nNO_SHARED_CODE = f'c{{1}}'\n"
            ),
            f"{entry} has no NO_SHARED_CODE" + no_constant.format("NO_SHARED_CODE"),
        ),
        (
            "a TOO_OLD that is last assigned a number",
            lambda r: put(
                r, entry, py_head + f"TOO_OLD = 'a — fix: b\\n{closing}'\nTOO_OLD = 1\nNO_SHARED_CODE = 'c'\n"
            ),
            f"{entry} has no TOO_OLD" + no_constant.format("TOO_OLD"),
        ),
        (
            "a TOO_OLD of one line",
            lambda r: put(r, entry, py_head + "TOO_OLD = 'BROKEN: x — fix: y'\nNO_SHARED_CODE = 'c'\n"),
            f"TOO_OLD in {entry}:2" + no_second,
        ),
        (
            "a TOO_OLD whose first line ends the text",
            lambda r: put(r, entry, py_head + "TOO_OLD = 'BROKEN: x — fix: y\\n'\nNO_SHARED_CODE = 'c'\n"),
            f"TOO_OLD in {entry}:2" + no_second,
        ),
        (
            "a TOO_OLD first line with no fix part",
            lambda r: put(r, entry, py_head + f"TOO_OLD = 'BROKEN: x\\n{closing}'\nNO_SHARED_CODE = 'c'\n"),
            f"the first line of C14, TOO_OLD in {entry}:2" + no_fix,
        ),
        (
            "a NO_SHARED_CODE first line with no fix part",
            lambda r: put(
                r,
                entry,
                py_head
                + f"TOO_OLD = 'BROKEN: x — fix: y — {DEFAULT_CLAUSE}\\n{closing}'\nNO_SHARED_CODE = 'c'\n",
            ),
            f"the first line of C15, NO_SHARED_CODE in {entry}:3" + no_fix,
        ),
        (
            "a shell C1 line with no fix part",
            lambda r: put(
                r, shell, '#!/bin/sh\n# c\nif true; then\n  echo "BROKEN: const-a needs python3" >&2\nfi\n'
            ),
            f"the first line of C1, the shell entry's line in {shell}:4" + no_fix,
        ),
        (
            "a shell C1 line whose dash after the fix word has no space before it",
            lambda r: put(
                r,
                shell,
                '#!/bin/sh\n# c\nif true; then\n  echo "BROKEN: const-a needs python3— fix: x'
                f' — {DEFAULT_CLAUSE}" >&2\nfi\n',
            ),
            f"the first line of C1, the shell entry's line in {shell}:4" + no_fix,
        ),
        (
            "an until_installed that is no literal",
            lambda r: put(
                r,
                "modules/const-b/plugin/scripts/b_gate/start.py",
                "GATE = Identity(gate='check-b', until_installed=CLAUSE)\n",
            ),
            "until_installed of the Identity at modules/const-b/plugin/scripts/b_gate/start.py:1 is no string"
            " literal"
            " — fix: write it as one, which this check reads by ast",
        ),
        (
            "a shared identity that is missing",
            lambda r: remove(r, IDENTITY),
            f"{IDENTITY} is missing — fix: restore the shared identity, whose Identity holds the default"
            " clause",
        ),
        (
            "a shared identity that is missing, every Identity naming its own until_installed",
            remove_identity_of_named,
            f"{IDENTITY} is missing — fix: restore the shared identity, whose Identity holds the default"
            " clause",
        ),
        (
            "a shared identity with no class Identity",
            lambda r: put(r, IDENTITY, "X = 1\n"),
            f"{IDENTITY} has no class Identity — fix: restore the shared identity",
        ),
        (
            "an Identity class with no until_installed",
            lambda r: put(r, IDENTITY, "class Identity:\n    gate: str\n"),
            no_default,
        ),
        (
            "an until_installed with no default",
            lambda r: put(r, IDENTITY, "class Identity:\n    until_installed: str\n"),
            no_default,
        ),
        (
            "an until_installed whose default is no literal",
            lambda r: put(r, IDENTITY, "class Identity:\n    until_installed: str = CLAUSE\n"),
            no_default,
        ),
        (
            "a kit with no entry",
            remove_entries,
            "no entry file found, no .py directly under plugin/scripts/ of a module with a line opening"
            " `FLOOR = (3, ` — fix: run the check from a checkout of the kit, whose modules carry them",
        ),
        (
            "a module folder with no MODULE.md",
            lambda r: put(r, "modules/const-x/plugin/INSTALL.md", "Install.\n"),
            "modules/const-x has no MODULE.md — fix: restore the module document",
        ),
    ):
        cases.check(broken_with(build) == expected, f"{name} is its literal BROKEN line")
    for name, build, source, ending in (
        (
            "an entry that is no Python",
            lambda r: put(r, entry, f"FLOOR = (3, {BASE}\n"),
            entry,
            ") — fix: repair the file",
        ),
        (
            "a shared identity that is no Python",
            lambda r: put(r, IDENTITY, "x = (\n"),
            IDENTITY,
            ") — fix: repair the file",
        ),
    ):
        said = broken_with(build)
        cases.check(
            said.startswith(f"{source} cannot be read as Python (") and said.endswith(ending),
            f"{name} is a teaching BROKEN line",
        )


def self_test_entry_scope(cases: Cases) -> None:
    """What is no entry: only a `.py` directly under `plugin/scripts/` of a module folder, with the floor line
    at a line's start, is read."""
    shape = f"FLOOR = (3, {BASE})\n"
    for name, path, text in (
        ("a .py with the floor line in scripts/ of the kit", "scripts/check-z.py", shape),
        (
            "a .py with the floor line in a folder that is no module",
            "modules/_scratch/plugin/scripts/x.py",
            shape,
        ),
        (
            "a .py with the floor line in scripts/ at the module's top, outside plugin/",
            "modules/const-a/scripts/x.py",
            shape,
        ),
        (
            "a .py with the floor line directly under plugin/, outside its scripts/",
            "modules/const-a/plugin/x.py",
            shape,
        ),
        (
            "a .py with the floor line below plugin/scripts/ of a module",
            "modules/const-a/plugin/scripts/sub/x.py",
            shape,
        ),
        (
            "a .py with the floor line in a scripts/ below a module's folder other than plugin/",
            "modules/const-a/hooks/scripts/x.py",
            shape,
        ),
        (
            "a .py with the floor line in a folder of plugin/ other than its scripts/",
            "modules/const-a/plugin/hooks/x.py",
            shape,
        ),
        ("a .py of a module outside its plugin/scripts/", "modules/const-a/tests/x.py", shape),
        (
            "a .py with an indented floor line",
            "modules/const-a/plugin/scripts/x.py",
            f"if True:\n    FLOOR = (3, {BASE})\n",
        ),
        (
            "a .py with a tool's FLOOR of three numbers",
            "modules/const-a/plugin/scripts/x.py",
            "FLOOR = (0, 24, 2)\n",
        ),
        (
            "a .py with a prefixed floor name",
            "modules/const-a/plugin/scripts/x.py",
            "VALE_FLOOR = (3, 23, 0)\n",
        ),
        ("a .py with a floor of another major", "modules/const-a/plugin/scripts/x.py", "FLOOR = (4, 1)\n"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, text)
            result = check_kit(root)
        cases.check(
            result.findings == [] and result.entries == BASE_ENTRIES,
            f"{name} is no entry: not read, the {BASE_ENTRIES} entries stand",
        )
    with tempfile.TemporaryDirectory() as tmp:  # an entry of a fifth module is read
        root = Path(tmp).resolve()
        fresh(root)
        extra = Spec("const-e", "check-e", DEFAULT_CLAUSE, None, GATE_CLOSING)
        put(root, "modules/const-e/MODULE.md", "A module.\n")
        put_entry(root, extra, given={"too_old": CHANGED})
        put_identity(root, extra, None)
        stage(root)
        result = check_kit(root)
    cases.check(
        [f.path for f in result.findings] == [extra.file("too_old")] and result.entries == BASE_ENTRIES + 1,
        "an entry of one more module is read: five entries, one finding",
    )


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
        len(set(expected)) == len(expected) == BASE_MENTIONS - 1 + 3 + 1  # the last 1: requires-python
        and expected[0][0] == ".github/workflows/gates.yml"
        and expected[-2][0] == "pyproject.toml"
        and expected[-1] == ("shared/pyproject.toml", REQUIRES_LINE, 1)
        and [o for o in expected if o[0] == "docs/two.md"]
        == [("docs/two.md", 1, 7), ("docs/two.md", 2, 1), ("docs/two.md", 2, 17)],
        "the findings are sorted by path, line and column, with the first and last typed by hand",
    )
    for name, order in orders.items():
        cases.check(order == expected, f"the findings stand in that order when git lists the files {name}")
    with tempfile.TemporaryDirectory() as tmp:  # the clauses' findings, over every entry, in every order
        root = Path(tmp).resolve()
        fresh(root)
        for spec in SPECS:
            put_entry(root, spec, given=ALL_CHANGED)
        runs = {
            "as git lists them": check_kit(root).findings,
            "reversed": check_kit(root, lambda r: list(reversed(listed(r)))).findings,
        }
        with listed_in_reverse():  # modules/ and every folder listed reversed too
            runs["with every folder listed reversed"] = check_kit(
                root, lambda r: sorted(listed(r), key=lambda entry: entry[1][::-1])
            ).findings
    expected_clauses = [
        (spec.file(text), TEXT_LINES[text]) for spec in SPECS for text in ("too_old", "no_shared", "sh")
    ]
    cases.check(
        [(f.path, f.line) for f in runs["as git lists them"]] == expected_clauses
        and len(expected_clauses) == 3 * BASE_ENTRIES,
        "the clauses' findings are sorted by path and line, the first and the last typed by hand",
    )
    for name, found in runs.items():
        cases.check(
            [(f.path, f.line) for f in found] == expected_clauses,
            f"the clauses' findings stand in that order when the files are listed {name}",
        )


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
