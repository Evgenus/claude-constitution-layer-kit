"""Kit tooling, never shipped in a module: the mutants of a module's own Python, and what its tests do
to each. `scripts/module-mutation.py` is the report that calls this file and prints the numbers
(decision dec-0122-module-mutation-report); nothing here judges anything.

A mutant is the text of one file with one small change. A test run kills it when a test fails, and it
survives when every test passes. The mutated code is the module's own Python under
modules/<module>/plugin/scripts, links and caches left out; the shared constitution_layer_kit is not
mutated.

The mutants. Each file is parsed with Python's `ast`; a mutant replaces the source text of one syntax
node and keeps the file's line count, so that the line map made on the unmutated file still names the
mutant's lines. A mutant that does not compile, or whose syntax tree equals the original's, is dropped.
Docstrings, type annotations and the literal parts of an f-string are never mutated. A mutant's id is
`<file>:<line>:<column>:<operator>`, with `:<n>` after it from the second of one place and operator on.
The operators, the key `op` of a mutant:
  cmp-negate    == <-> !=, < <-> >=, > <-> <=, is <-> is not, in <-> not in, in a comparison of one operator;
  cmp-boundary  < <-> <=, > <-> >=, in the same;
  bool-swap     and <-> or;
  not-drop      not x -> x;
  cond-negate   the test of an if, a while, a conditional expression, a comprehension's if or an assert,
                when it is no comparison of one operator and no `not`: test -> not (test);
  arith         + <-> -, * -> /, / -> *, // -> *, % -> *, ** -> *, | <-> &, never where an operand is a
                string or bytes literal or an f-string;
  aug           += <-> -=;
  num           a number n -> n + 1;
  bool-const    True <-> False;
  str           a string literal or an f-string s -> 'XX' + s;
  return        return x -> return None;
  call-del      a call that is a statement -> None;
  loop-jump     break <-> continue;
  for-zero      for … in xs -> for … in ().
The operators are the kit's own choice, and the score is a property of them as much as of the tests: a
change of this list moves every score with no change in any test. No outside mutation tool is used or
pinned: this file makes the mutants and runs them.

The line map. One run of the module's tests under coverage.py, one by one, gives for each line the
tests that run it. The pytest process switches coverage's context to each test's node id, through
`scripts/kit_mutation_plugin.py`. A child process a test starts takes its context from the environment
variable PYTEST_CURRENT_TEST, which pytest sets and the child inherits: the rc file says
`context = ${PYTEST_CURRENT_TEST-}`, and the child reads that file itself, since COVERAGE_PROCESS_START
names it and coverage.py's own `.pth` file starts coverage there. `patch = subprocess`, which
`scripts/kit_coverage.py` uses, is not used here: it hands a child the parent's settings already
expanded, so a child would carry the parent's empty context. A line that runs outside any test, at
import or during collection, has the context ``. The unmutated tests must be green in that run; a red
one is a MutationError, since a mutant's red would then mean nothing. Three kinds of run reach the map
that coverage.py alone would not see (decision dec-0127-mutation-line-map-blind-spots):
  copies        the run measures every file whose path holds a folder named `scripts`, not the module's
                folder alone. A file measured outside the copy of the kit stands for the module's file
                that the part of its path after its last such folder names, below plugin/scripts: a
                copy a test made of the plugin, and ran. A path that holds a line break is not matched;
  -S            in this run alone, the plugin makes `<work>/python` the tests' sys.executable. It runs
                `-S <file>` through `scripts/kit_mutation_boot.py`, which starts coverage.py before the
                file, and hands every other call on unchanged. A child started any other way under
                `-S` is not measured;
  no bytecode   a line that holds none, as in the continuation lines of a constant the compiler folds
                into one, is looked up as the first line of the nearest node around the mutant, up to
                its statement, that holds some: the field `reach` of a Mutant, which no file holds.

The run of one mutant. The mutant's text is written over the file in a copy of the kit, so that a child
process meets it too. The file's modification time is set to a value no other text of that copy
carries, so that Python never loads the cached bytecode of another text of the file. pytest then runs,
stopped at the first failure, only the tests whose coverage the line map says reaches one of the
mutant's lines, the quickest first; when one of those lines also runs outside any test, every other test
follows, since any test may depend on it. The file is restored after the run, whatever happened. The
outcome, the key `status`:
  killed        pytest exited 1, a test failed, or 2, the tests could not be collected;
  timeout       the run passed its limit and was stopped: four times the chosen tests' own time and 15
                seconds more, and never less than 30 seconds; counted with the killed, as a run that
                does not end does not pass;
  survived      pytest exited 0;
  not covered   no test reaches a line of the mutant; nothing is run, and no test can kill it. Some
                children are not measured: one started with an environment of its own, without
                coverage's variable, and one under a limit on the size of the files it writes, which
                cannot write coverage.py's data file. So this count can be too high and the score too
                low, never too high;
  unsure        with more than one copy alone: the test that failed with the mutant was run again at
                once on the unmutated file in the same copy, and failed there too, so the load and not
                the mutant may have failed it. Left out of the score. A kill at collection, where no
                test ran, and a timeout are not run again: neither names a test that failed, and the
                limit already allows four times the tests' own time;
  error         any other exit of pytest. Left out of the score.
Copies. Each worker owns a copy of the kit, made from the files git lists, or from the whole folder
where git lists none, and takes mutants from one queue, in an order shuffled by the seed. With a budget
in seconds, wall-clock time counted from the moment the copies start on the mutants, after the line map,
no worker takes a new mutant once the budget is spent; a mutant begun is finished. The mutants not begun
are not run, and the score is then an estimate from a sample.

The file of one module, the JSON keys as written:
  module        the module folder's name;
  seed          the seed of the order, a string;
  budget        the budget in seconds, or null for a whole run;
  copies        the number of copies that ran side by side;
  tests         the tests that passed in the line map's run;
  map_seconds   that run's wall-clock time;
  seconds       the wall-clock time of the mutants' runs;
  mutants       the number of mutants made, run or not;
  results       per mutant run, in the order they ended: `id`, `file`, `line`, `op`, `old` (the source
                replaced, cut at 120 characters), `new` (what replaced it), `status`, `seconds`, `tests`
                (how many were chosen) and `killer` (the node id of the test that failed, or null).
"""

from __future__ import annotations

import ast
import json
import os
import queue
import random
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import types
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKFLOW = HERE.parent / ".github" / "workflows" / "gates.yml"
PLUGIN = "kit_mutation_plugin"
BOOT = "kit_mutation_boot"
SELECT_ENV = "KIT_MUTATION_SELECT"  # names a JSON list of node ids: the plugin runs those alone, in order
SEEN_ENV = "KIT_MUTATION_SEEN"  # names a file: the plugin writes each test's outcome and seconds there
PYTHON_ENV = "KIT_MUTATION_PYTHON"  # names the interpreter the plugin makes sys.executable, in the map's run
MEASURED = "*/scripts/*"  # the files the map's run measures: the module's own, and any copy of them
STRIPPED = (  # never handed to a run: each would change which tests run or what they measure
    "COVERAGE_PROCESS_START",
    "COVERAGE_PROCESS_CONFIG",
    "CONSTITUTION_KIT_COVERAGE",
    "CONSTITUTION_KIT_JOBS",
    "PYTEST_ADDOPTS",
    "PYTEST_CURRENT_TEST",
    SELECT_ENV,
    SEEN_ENV,
    PYTHON_ENV,
)
PHASE = re.compile(r" \((?:setup|call|teardown)\)$")
OLD_CUT = 120
DETECTED = ("killed", "timeout")
JUDGED = (*DETECTED, "survived", "not covered")
STATUSES = (*JUDGED, "unsure", "error")

Node = ast.expr | ast.stmt
Run = Callable[[list[str], Path, dict[str, str], float], tuple[int | None, str, float]]

NEGATE: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Lt: ast.GtE,
    ast.GtE: ast.Lt,
    ast.Gt: ast.LtE,
    ast.LtE: ast.Gt,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
}
BOUNDARY: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
}
ARITH: dict[type[ast.operator], type[ast.operator]] = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.Div,
    ast.Div: ast.Mult,
    ast.FloorDiv: ast.Mult,
    ast.Mod: ast.Mult,
    ast.Pow: ast.Mult,
    ast.BitOr: ast.BitAnd,
    ast.BitAnd: ast.BitOr,
}


class MutationError(Exception):
    """A measure cannot be made: the message says what failed, why and the fix."""


@dataclass(frozen=True)
class Mutant:
    id: str
    file: str  # from the kit root, with forward slashes
    line: int
    end_line: int
    reach: tuple[int, ...]  # the lines whose coverage stands for the mutant's, as the line map says
    op: str
    old: str
    new: str
    text: str  # the file's whole text with the mutant applied


@dataclass(frozen=True)
class Point:
    """One place a file can be mutated at: the node that names it, the bytes replaced, and what replaces
    them, as text shown to a person and as the bytes written."""

    op: str
    node: Node
    start: int
    end: int
    new: str
    written: bytes


@dataclass(frozen=True)
class LineMap:
    tests: dict[str, float]  # node id -> seconds, of the tests that passed
    lines: dict[str, dict[int, list[str]]]  # file -> line -> the node ids that run it; `` is outside any test
    seconds: float


@dataclass(frozen=True)
class Limits:
    """A mutant's run is stopped after `max(floor, 4 x the chosen tests' seconds + slack)` seconds."""

    floor: float = 30.0
    slack: float = 15.0


class Source:
    def __init__(self, path: Path) -> None:
        self.data = path.read_bytes()
        self.tree = ast.parse(self.data)
        self.dump = ast.dump(self.tree)
        self.starts = [0]
        for line in self.data.splitlines(keepends=True):
            self.starts.append(self.starts[-1] + len(line))
        self.code = code_lines(compile(self.data, str(path), "exec", dont_inherit=True))
        self.parents = {
            id(child): node for node in ast.walk(self.tree) for child in ast.iter_child_nodes(node)
        }

    def reach(self, node: Node, first: int, last: int) -> tuple[int, ...]:
        """The lines of `first` to `last` that hold bytecode; where none does, as in the continuation lines
        of a constant the compiler folds into one, the first line of the nearest node around `node`, up to
        its statement, that holds some, since that bytecode runs the node; none where no such line is."""
        lines = tuple(line for line in range(first, last + 1) if line in self.code)
        if lines or isinstance(node, ast.stmt):
            return lines
        around = self.parents.get(id(node))
        while around is not None:
            line = getattr(around, "lineno", None)
            if line in self.code:
                return (line,)
            if isinstance(around, ast.stmt):
                return ()
            around = self.parents.get(id(around))
        return ()

    def span(self, node: Node) -> tuple[int, int]:
        end_line = node.lineno if node.end_lineno is None else node.end_lineno
        end_column = node.col_offset if node.end_col_offset is None else node.end_col_offset
        return self.starts[node.lineno - 1] + node.col_offset, self.starts[end_line - 1] + end_column

    def text(self, node: Node) -> str:
        start, end = self.span(node)
        return self.data[start:end].decode("utf-8")

    def wrapped(self, op: str, node: Node, new: str) -> Point:
        """`node` replaced by `(new)`, padded with newlines inside the parentheses so the line count holds."""
        start, end = self.span(node)
        last = node.lineno if node.end_lineno is None else node.end_lineno
        pad = "\n" * (last - node.lineno - new.count("\n"))
        return Point(op, node, start, end, new, f"({new}{pad})".encode())

    def applied(self, point: Point) -> bytes | None:
        """The file with the point's bytes replaced; None when the result does not compile, changes
        nothing a parser sees, or has another line count."""
        out = self.data[: point.start] + point.written + self.data[point.end :]
        try:
            tree = ast.parse(out)
            compile(tree, "<mutant>", "exec")
        except (SyntaxError, ValueError):
            return None
        if ast.dump(tree) == self.dump or out.count(b"\n") != self.data.count(b"\n"):
            return None
        return out


def code_lines(code: types.CodeType) -> set[int]:
    """The lines that hold bytecode in `code` and every code object inside it: the only lines coverage.py
    can see run."""
    lines = {line for _, _, line in code.co_lines() if line is not None}
    for inner in code.co_consts:
        if isinstance(inner, types.CodeType):
            lines |= code_lines(inner)
    return lines


def is_text(node: ast.AST) -> bool:
    return isinstance(node, ast.JoinedStr) or (
        isinstance(node, ast.Constant) and isinstance(node.value, str | bytes)
    )


def docstrings(tree: ast.AST) -> set[int]:
    found: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) and node.body:
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                found.add(id(first.value))
    return found


def annotation_nodes(tree: ast.AST) -> set[int]:
    """Every node inside a type annotation, which is never evaluated where annotations are deferred."""
    inside: set[int] = set()
    for node in ast.walk(tree):
        for name in ("annotation", "returns"):
            sub = getattr(node, name, None)
            if isinstance(sub, ast.AST):
                inside.update(id(n) for n in ast.walk(sub))
    return inside


def inside_fstrings(tree: ast.AST) -> set[int]:
    """The literal parts of an f-string and its format specs: text of the f-string, no places of their own."""
    inside: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            for part in node.values:
                if isinstance(part, ast.Constant):
                    inside.add(id(part))
                elif isinstance(part, ast.FormattedValue) and part.format_spec is not None:
                    inside.update(id(n) for n in ast.walk(part.format_spec))
    return inside


def condition_tests(tree: ast.AST) -> set[int]:
    tests: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If | ast.While | ast.IfExp | ast.Assert):
            tests.add(id(node.test))
        elif isinstance(node, ast.comprehension):
            tests.update(id(test) for test in node.ifs)
    return tests


def constant_points(src: Source, node: ast.Constant) -> Iterator[Point]:
    if isinstance(node.value, bool):
        yield src.wrapped("bool-const", node, repr(not node.value))
    elif isinstance(node.value, int | float):
        yield src.wrapped("num", node, repr(node.value + 1))
    elif isinstance(node.value, str):
        yield src.wrapped("str", node, "'XX' + " + src.text(node))


def expression_points(src: Source, node: ast.expr) -> Iterator[Point]:
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        kind = type(node.ops[0])
        for name, table in (("cmp-negate", NEGATE), ("cmp-boundary", BOUNDARY)):
            if kind in table:
                changed = ast.Compare(left=node.left, ops=[table[kind]()], comparators=node.comparators)
                yield src.wrapped(name, node, ast.unparse(changed))
    elif isinstance(node, ast.BoolOp):
        other: ast.boolop = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        yield src.wrapped("bool-swap", node, ast.unparse(ast.BoolOp(op=other, values=node.values)))
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        yield src.wrapped("not-drop", node, src.text(node.operand))
    elif isinstance(node, ast.BinOp) and type(node.op) in ARITH:
        if not (is_text(node.left) or is_text(node.right)):
            swapped = ast.BinOp(left=node.left, op=ARITH[type(node.op)](), right=node.right)
            yield src.wrapped("arith", node, ast.unparse(swapped))
    elif isinstance(node, ast.Constant):
        yield from constant_points(src, node)
    elif isinstance(node, ast.JoinedStr):
        yield src.wrapped("str", node, "'XX' + " + src.text(node))


def augmented(src: Source, node: ast.AugAssign) -> Point | None:
    """`+=` <-> `-=`, replaced as text between the target and the value; None for any other operator,
    or where that text holds the operator more than once."""
    if not isinstance(node.op, ast.Add | ast.Sub):
        return None
    start, end = src.span(node.target)[1], src.span(node.value)[0]
    old, new = (b"+=", b"-=") if isinstance(node.op, ast.Add) else (b"-=", b"+=")
    middle = src.data[start:end]
    if middle.count(old) != 1:
        return None
    return Point("aug", node, start, end, new.decode(), middle.replace(old, new))


def statement_points(src: Source, node: ast.stmt) -> Iterator[Point]:
    if isinstance(node, ast.Return) and node.value is not None:
        if not (isinstance(node.value, ast.Constant) and node.value.value is None):
            yield src.wrapped("return", node.value, "None")
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        yield src.wrapped("call-del", node.value, "None")
    elif isinstance(node, ast.For):
        yield src.wrapped("for-zero", node.iter, "()")
    elif isinstance(node, ast.Break | ast.Continue):
        word = "continue" if isinstance(node, ast.Break) else "break"
        start, end = src.span(node)
        yield Point("loop-jump", node, start, end, word, word.encode())
    elif isinstance(node, ast.AugAssign):
        point = augmented(src, node)
        if point is not None:
            yield point


def points(src: Source) -> Iterator[Point]:
    """Every place the file can be mutated at, in no order."""
    skip = docstrings(src.tree) | annotation_nodes(src.tree) | inside_fstrings(src.tree)
    tests = condition_tests(src.tree)
    for node in ast.walk(src.tree):
        if id(node) in skip:
            continue
        if isinstance(node, ast.expr):
            yield from expression_points(src, node)
            single = isinstance(node, ast.Compare) and len(node.ops) == 1
            negated = isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not)
            if id(node) in tests and not single and not negated:
                yield src.wrapped("cond-negate", node, "not (" + src.text(node) + ")")
        elif isinstance(node, ast.stmt):
            yield from statement_points(src, node)


def file_mutants(path: Path, shown: str) -> list[Mutant]:
    """The mutants of one file, by line, column and operator; `shown` is its path in every id."""
    src = Source(path)
    made: list[tuple[int, int, str, Point, bytes]] = []
    for point in points(src):
        data = src.applied(point)
        if data is not None:
            made.append((point.node.lineno, point.node.col_offset, point.op, point, data))
    made.sort(key=lambda one: one[:3])
    out: list[Mutant] = []
    seen: dict[tuple[int, int, str], int] = {}
    for line, column, op, point, data in made:
        count = seen[(line, column, op)] = seen.get((line, column, op), 0) + 1
        old = src.text(point.node)
        end_line = line + old.count("\n")
        out.append(
            Mutant(
                id=f"{shown}:{line}:{column}:{op}" + (f":{count}" if count > 1 else ""),
                file=shown,
                line=line,
                end_line=end_line,
                reach=src.reach(point.node, line, end_line),
                op=op,
                old=old if len(old) <= OLD_CUT else old[:OLD_CUT] + "…",
                new=point.new,
                text=data.decode("utf-8"),
            )
        )
    return out


def mutants(root: Path, module: str) -> list[Mutant]:
    """Every mutant of the module's own Python under `root`, links and caches left out, by file."""
    folder = root / "modules" / module / "plugin" / "scripts"
    out: list[Mutant] = []
    for path in sorted(folder.rglob("*.py")):
        if path.is_symlink() or "__pycache__" in path.parts:
            continue
        try:
            out.extend(file_mutants(path, path.relative_to(root).as_posix()))
        except (OSError, SyntaxError, ValueError) as bad:
            raise MutationError(
                f"{path} cannot be read as Python ({bad})\n  why: a mutant is made from the file's syntax"
                " tree\n  fix: repair the file; the module's lint entry names what is wrong with it"
            ) from bad
    return out


def pinned(package: str) -> str:
    """The install command of the version the kit's CI pins, read from the workflow, which alone names it."""
    try:
        found = re.search(rf'"{re.escape(package)}==([^"\s]+)"', WORKFLOW.read_text(encoding="utf-8"))
    except OSError:
        found = None
    if found is None:
        return f"{sys.executable} -m pip install {package}, at the version .github/workflows/gates.yml pins"
    return f'{sys.executable} -m pip install "{package}=={found[1]}"'


def preflight() -> None:
    """MutationError when coverage.py or pytest is not installed for this interpreter."""
    for package in ("coverage", "pytest"):
        found = subprocess.run(
            [sys.executable, "-c", f"import {package}"], capture_output=True, text=True, check=False
        )
        if found.returncode != 0:
            raise MutationError(
                f"{package} is not installed for {sys.executable}\n  why: the line map is one run of the"
                " module's tests under coverage.py, and every mutant is a run of pytest\n"
                f"  fix: {pinned(package)}"
            )


def tracked(root: Path) -> list[str] | None:
    """The files git lists in `root`, tracked or new and not ignored; None where git lists none."""
    done = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    names = [name for name in done.stdout.split("\0") if name] if done.returncode == 0 else []
    inside = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True, check=False
    )
    if not names or inside.returncode != 0 or Path(inside.stdout.strip()).resolve() != root.resolve():
        return None
    return names


def make_copy(root: Path, target: Path) -> None:
    """A copy of the kit in `target`, links kept as links: the files git lists, so that no worktree, cache
    or scratch folder comes along; the whole folder, caches aside, where `root` is no repository's top."""
    names = tracked(root)
    if names is None:
        shutil.copytree(root, target, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    else:
        for name in names:
            source = root / name
            if not (source.is_symlink() or source.is_file()):
                continue  # listed and deleted in the working tree
            (target / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target / name, follow_symlinks=False)
    # the bytecode of the unmutated files, written once, so that each run compiles the mutated file alone
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "shared", "modules"],
        cwd=target,
        capture_output=True,
        check=False,
    )


def prepare(work: Path) -> dict[str, str]:
    """The environment of every run: a `python3` that is this interpreter first on PATH, so that a gate's
    `python3` is the one that holds coverage.py and pytest, and that is the map's interpreter where
    KIT_MUTATION_PYTHON names it, in the map's run alone; the plugin's folder first on PYTHONPATH, a copy
    of the one file, so that no other kit script can be imported by a test; and none of STRIPPED."""
    shim = work / "bin"
    shim.mkdir(parents=True, exist_ok=True)
    python3 = shim / "python3"
    python3.write_text(
        "#!/bin/sh\n"
        f'if [ -n "${{{PYTHON_ENV}-}}" ]; then\n    exec "${PYTHON_ENV}" "$@"\nfi\n'
        f'exec {shlex.quote(sys.executable)} "$@"\n',
        encoding="utf-8",
    )
    python3.chmod(0o755)
    plugin = work / "plugin"
    plugin.mkdir(exist_ok=True)
    shutil.copy2(HERE / f"{PLUGIN}.py", plugin / f"{PLUGIN}.py")
    map_interpreter(work)
    env = {name: value for name, value in os.environ.items() if name not in STRIPPED}
    env["PATH"] = f"{shim}{os.pathsep}{env.get('PATH', '')}"
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(plugin), env.get("PYTHONPATH")]))
    return env


def map_interpreter(work: Path) -> Path:
    """The interpreter of the map's run: `work/python`, a shell file that runs this interpreter, which the
    plugin makes the tests' sys.executable and the `python3` on PATH hands on to. Asked for `-S <file>`,
    it runs the boot file under `-S` first, which starts coverage.py from a folder that holds coverage.py
    alone, put last on the path, so that the child measures what `-S` would leave unmeasured and imports
    nothing else it could not. Asked for `<file>` under a soft limit on the size of files below the hard
    one, which the plugin leaves where a test sets such a limit, it runs the boot file first too, which
    lifts the soft limit once the file has ended, so that coverage.py can save. Any other call it hands
    on unchanged."""
    import coverage  # noqa: PLC0415 — preflight has made sure it is there; only the map's run needs it

    boot = work / "boot"
    boot.mkdir(exist_ok=True)
    shutil.copy2(HERE / f"{BOOT}.py", boot / f"{BOOT}.py")
    lib = work / "coverage-only"
    lib.mkdir(exist_ok=True)
    if not (lib / "coverage").exists():
        (lib / "coverage").symlink_to(Path(coverage.__file__).resolve().parent)
    real, started = shlex.quote(sys.executable), shlex.quote(str(boot / f"{BOOT}.py"))
    python = work / "python"
    python.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-S" ] && [ "$#" -ge 2 ] && [ "${2#-}" = "$2" ]; then\n'
        "    shift\n"
        f'    exec {real} -S {started} {shlex.quote(str(lib))} "$@"\n'
        "fi\n"
        'if [ "$#" -ge 1 ] && [ "${1#-}" = "$1" ] && [ "$(ulimit -S -f)" != "$(ulimit -H -f)" ]; then\n'
        f'    exec {real} {started} {shlex.quote(str(lib))} "$@"\n'
        "fi\n"
        f'exec {real} "$@"\n',
        encoding="utf-8",
    )
    python.chmod(0o755)
    return python


def pytest_command(module: str, *more: str) -> list[str]:
    return [
        "-m",
        "pytest",
        f"modules/{module}/tests",
        "-p",
        "no:cacheprovider",
        "-p",
        PLUGIN,
        "-W",
        "error",
        "-q",
        *more,
    ]


def run_process(
    command: list[str], cwd: Path, env: dict[str, str], limit: float
) -> tuple[int | None, str, float]:
    """The command's exit, output and seconds; the exit None when it passed `limit` seconds and was
    stopped with every process it started."""
    began = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    code: int | None
    try:
        out, _ = process.communicate(timeout=limit)
        code = process.returncode
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        out, _ = process.communicate()
        code = None
    return code, out, round(time.monotonic() - began, 2)


def last_lines(text: str, count: int = 30) -> str:
    return "\n".join("    " + line for line in text.strip().splitlines()[-count:])


def cli(work: Path, cwd: Path, env: dict[str, str], *args: str) -> None:
    done = subprocess.run(
        [sys.executable, "-m", "coverage", *args, "--rcfile", str(work / "coveragerc")],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        said = (done.stderr or done.stdout).strip().splitlines()
        raise MutationError(
            f"`coverage {args[0]}` exited {done.returncode}: {said[-1] if said else 'no output'}\n"
            "  why: the line map is read from coverage.py's data\n"
            f"  fix: {pinned('coverage')}, the version the report is written against; at that version"
            " already, repair the cause that coverage.py's own line, quoted above, names"
        )


def line_map(copy: Path, module: str, work: Path, env: dict[str, str]) -> LineMap:
    """The per-test line map of the module, from one run of its unmutated tests in `copy`; MutationError
    when that run is not green or its data cannot be read."""
    rc = work / "coveragerc"
    rc.write_text(
        f"[run]\nparallel = true\ndata_file = {work / 'data'}\n"
        "context = ${PYTEST_CURRENT_TEST-}\n"
        f"include =\n    {MEASURED}\n",
        encoding="utf-8",
    )
    seen = work / "tests.json"
    code, out, seconds = run_process(
        [sys.executable, "-m", "coverage", "run", "--rcfile", str(rc), *pytest_command(module)],
        copy,
        {**env, "COVERAGE_PROCESS_START": str(rc), SEEN_ENV: str(seen), PYTHON_ENV: str(work / "python")},
        3600.0,
    )
    if code != 0:
        raise MutationError(
            f"the unmutated tests of {module} are not green"
            f" ({'no end within an hour' if code is None else f'pytest exit {code}'}):\n{last_lines(out)}\n"
            "  why: a mutant is killed when a test turns red, which means nothing where a test is red"
            " without it\n"
            f"  fix: run python3 scripts/check-aspects.py --run --module {module} and repair what it names"
        )
    cli(work, work, env, "combine", "-q")
    try:
        from coverage import CoverageData  # noqa: PLC0415 — preflight has made sure it is there

        data = CoverageData(basename=str(work / "data"))
        data.read()
        ran = json.loads(seen.read_text(encoding="utf-8"))
        lines: dict[str, dict[int, list[str]]] = {}
        for name in data.measured_files():
            shown = module_file(name, copy, module)
            if shown is None:
                continue
            per = lines.setdefault(shown, {})
            for line, contexts in data.contexts_by_lineno(name).items():
                per[line] = sorted({*per.get(line, ()), *(PHASE.sub("", context) for context in contexts)})
        tests = {node: float(one["seconds"]) for node, one in ran.items() if one["outcome"] == "passed"}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as bad:
        raise MutationError(
            f"the line map of {module} cannot be read ({bad})\n  why: the map says which tests run for"
            f" each mutant\n  fix: {pinned('coverage')} and {pinned('pytest')}, the versions the report is"
            " written against"
        ) from bad
    return LineMap(tests, lines, seconds)


def module_file(name: str, copy: Path, module: str) -> str | None:
    """The path from the copy's root that a file measured in the map's run stands for: its own, when it
    lies in the copy; the module's file below plugin/scripts named by the part of its path after its last
    folder named `scripts`, when it lies elsewhere, a copy a test made of the plugin; None when there is
    no such file of the module."""
    path = Path(name).resolve()
    root = copy.resolve()
    if path.is_relative_to(root):
        return path.relative_to(root).as_posix()
    parts = path.parts
    if "scripts" not in parts[:-1]:
        return None
    below = parts[len(parts) - parts[::-1].index("scripts") :]
    target = root / "modules" / module / "plugin" / "scripts" / Path(*below)
    return target.relative_to(root).as_posix() if target.is_file() else None


def select(mutant: Mutant, table: LineMap) -> list[str] | None:
    """The node ids to run for the mutant, in order; None when no test reaches it."""
    per = table.lines.get(mutant.file, {})
    reach: set[str] = set()
    for line in mutant.reach:
        reach.update(per.get(line, ()))
    if not reach:
        return None
    tests = table.tests
    chosen = sorted((test for test in reach if test in tests), key=lambda test: (tests[test], test))
    if "" in reach:  # the line also runs at import or during collection: any test may depend on it
        chosen += sorted((test for test in tests if test not in reach), key=lambda test: (tests[test], test))
    return chosen or None


def failed_test(seen: Path) -> str | None:
    """The node id of the first test the plugin saw fail in the run that wrote `seen`, or None."""
    try:
        ran = json.loads(seen.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return next((node for node, one in ran.items() if one.get("outcome") == "failed"), None)


@dataclass
class Worker:
    """One copy of the kit and what a run in it needs."""

    copy: Path
    module: str
    env: dict[str, str]
    scratch: Path
    table: LineMap
    limits: Limits
    confirm: bool
    run: Run
    stamp: int

    def tests_run(self, chosen: list[str], limit: float) -> tuple[int | None, str, float, str | None]:
        listed = self.scratch / "select.json"
        seen = self.scratch / "seen.json"
        listed.write_text(json.dumps(chosen), encoding="utf-8")
        seen.unlink(missing_ok=True)
        code, out, seconds = self.run(
            [sys.executable, *pytest_command(self.module, "-x")],
            self.copy,
            {**self.env, SELECT_ENV: str(listed), SEEN_ENV: str(seen)},
            limit,
        )
        return code, out, seconds, failed_test(seen)

    def one(self, mutant: Mutant) -> dict[str, object]:
        """The mutant's result: applied, run against its chosen tests, restored, and a kill confirmed."""
        result: dict[str, object] = {
            "id": mutant.id,
            "file": mutant.file,
            "line": mutant.line,
            "op": mutant.op,
            "old": mutant.old,
            "new": mutant.new,
        }
        chosen = select(mutant, self.table)
        if chosen is None:
            return {**result, "status": "not covered", "seconds": 0.0, "tests": 0, "killer": None}
        limit = max(self.limits.floor, 4 * sum(self.table.tests[test] for test in chosen) + self.limits.slack)
        target = self.copy / mutant.file
        original = target.read_bytes()
        before = target.stat()
        self.stamp += 1
        try:
            target.write_text(mutant.text, encoding="utf-8")
            os.utime(target, (self.stamp, self.stamp))
            code, _, seconds, killer = self.tests_run(chosen, limit)
        finally:
            target.write_bytes(original)
            os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns))
        status = {0: "survived", 1: "killed", 2: "killed", None: "timeout"}.get(code, "error")
        if status == "killed" and self.confirm and killer is not None:
            again, _, more, _ = self.tests_run([killer], limit)
            seconds = round(seconds + more, 2)
            if again != 0:
                status = "unsure"
        return {**result, "status": status, "seconds": seconds, "tests": len(chosen), "killer": killer}


def measure(
    root: Path,
    module: str,
    work: Path,
    *,
    seed: str = "0",
    budget: float | None = None,
    copies: int = 1,
    limits: Limits | None = None,
    run: Run = run_process,
) -> dict[str, object]:
    """The file of one module, as the docstring defines it: copies of the kit made under `work`, the line
    map built in the first, every mutant run in the seed's order until the budget is spent. MutationError
    when the measure cannot be made. `root` itself is only read."""
    preflight()
    env = prepare(work)
    folders = [work / f"copy-{index}" for index in range(copies)]
    for folder in folders:
        make_copy(root, folder)
    found = mutants(folders[0], module)
    table = line_map(folders[0], module, work, env)
    order = list(found)
    random.Random(seed).shuffle(order)
    todo: queue.Queue[Mutant] = queue.Queue()
    for mutant in order:
        todo.put(mutant)
    untouched = {
        (folder, name): (folder / name).read_bytes()
        for folder in folders
        for name in sorted({mutant.file for mutant in found})
    }
    results: list[dict[str, object]] = []
    faults: list[Exception] = []
    lock = threading.Lock()
    began = time.monotonic()
    base = int(time.time()) - 400 * 24 * 3600  # a time no file of a copy carries; each text gets its own

    def work_through(index: int) -> None:
        scratch = work / f"run-{index}"
        scratch.mkdir()
        worker = Worker(
            folders[index],
            module,
            env,
            scratch,
            table,
            limits or Limits(),
            copies > 1,
            run,
            base + index * 1_000_000,
        )
        try:
            while budget is None or time.monotonic() - began < budget:
                try:
                    mutant = todo.get_nowait()
                except queue.Empty:
                    return
                result = worker.one(mutant)
                with lock:
                    results.append(result)
        except Exception as bad:  # handed to the caller's thread, which raises it
            with lock:
                faults.append(bad)

    threads = [threading.Thread(target=work_through, args=(index,)) for index in range(copies)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if faults:
        raise faults[0]
    seconds = round(time.monotonic() - began, 1)
    for (folder, name), text in untouched.items():
        if (folder / name).read_bytes() != text:
            raise MutationError(
                f"{folder / name} is not the file it was before the run\n  why: every mutant is written"
                " over the file and taken back, and a file left mutated would spoil the results after it\n"
                "  fix: this is a fault of scripts/kit_mutation.py; run it again, and report the mutant"
                " the results end with"
            )
    return {
        "module": module,
        "seed": seed,
        "budget": budget,
        "copies": copies,
        "tests": len(table.tests),
        "map_seconds": table.seconds,
        "seconds": seconds,
        "mutants": len(found),
        "results": results,
    }
