#!/usr/bin/env python3
"""Kit report, never a gate: measure each module from what the kit already holds, and print it.

Advisory in the sense of law 5 of CLAUDE.md: it judges nothing and blocks nothing. Its numbers are read
by a person, who decides what they mean; no number here is a threshold, and none is held anywhere. The
kit's CI runs it, the default mode and --complexity, in the job `gates`, after that job's verdict, on
every pull request and on main, where its failure never changes the verdict (decision
dec-0087-module-metrics-report). Test coverage is no metric of this report: each module's fixtures
entry measures it in the module's own job, and scripts/module-coverage.py reports it (decision
dec-0089-module-coverage-report). Nor is mutation score: it takes minutes per module, too slow for a
step that runs on every change.

Per module folder (the kit's one listing, `module_folders` of scripts/kit_module_doc.py), one row of
these keys, the JSON keys as written:
  rows              the data rows of the first table of the section of anchor t3 of MODULE.md;
  gate_entries,     the rows of the first table of the section of anchor t9 whose `kind` cell opens
  advisory_entries  with `gate`, or with `advisory`, its code spans read as text;
  limits            the numbered items, unindented, after the line that opens `**Honest limits**` in t9;
  dials             the data rows of the first table of t7, 0 when it holds none;
  decisions_cited   the distinct `dec-<4 digits>` ids in t4;
  deferred          the items, numbered or bulleted and unindented, of t12, plus the acceptance items
                    whose kind holds the word `deferred`;
  proof_kinds       the acceptance items of the first table of t10, per kind: fixture, kit check, live,
                    review, deferred (a kind that holds the word), other; a cell of handles counts each
                    handle, and a range `T1–T5` counts five;
  skills,           the files skills/*/SKILL.md, and their characters;
  skill_chars
  always_on_chars   the characters every SessionStart command of hooks/hooks.json writes to stdout, run
                    from the kit root with CLAUDE_PLUGIN_ROOT set to the module folder and, on stdin, the
                    least event a session's start sends (`EVENT`; an empty stdin makes a hook print its
                    BROKEN line for input that is no JSON, not what a session sees), plus the
                    `description` of each skill's front matter: what reaches the model at every session
                    start before anything is asked;
  hook_events       the event keys of hooks/hooks.json, 0 when it is absent;
  code_lines,       the non-blank lines that are no comment and, in Python, no docstring, of the `.py` and
  test_lines        `.sh` files git tracks under scripts/ and hooks/ (code) and tests/ (tests), a
                    symbolic link never read;
  functions,        the functions of the module's own Python under scripts/ (links, and so the shared
  cc_max,           const_gate, never read) and their cyclomatic complexity, counted by this script from
  cc_over_10        the syntax tree, not by ruff's C901: 1, plus 1 per if, for, while, except, conditional
                    expression, comprehension, assert and match case, plus n-1 per boolean operation of n
                    operands; a nested function is its own function and adds nothing to the one around it;
  shared_imports,   the import statements of that same Python that import const_gate, against those that
  own_imports       import the module's own packages (`own_packages` of kit_module_doc), a relative
                    import counted as the module's own;
  churn_90d         the commits, merges left out, of the last 90 days that touch modules/<module>.
A totals row sums every key, save cc_max, which is the largest.

Modes:  no arguments    the three tables on stdout: the documents, the proof kinds, the code;
        --json <path>   the tables on stdout and the same numbers as one JSON object in <path>;
        --json -        the JSON object on stdout, and no tables;
        --complexity [<n>]
                        the <n> most complex functions of the modules' own Python under scripts/ (the
                        functions counted above), 20 when <n> is not given, most complex first, ties
                        by length, as one table on stdout; with --json <path> the table too and the
                        same list as JSON in <path>; with --json -, the JSON on stdout and no table.
                        Per function, the JSON keys as written:
                          module, path, line  where it stands;
                          function            its name, under its class or enclosing function;
                          cc                  its cyclomatic complexity, counted as above;
                          lines               the lines from its `def` to its last, docstring included;
                          depth               the deepest nesting of if, for, while, with, try and
                                              match blocks in its own body, an elif at its if's level;
                          params              its parameters, a `self` or `cls` in the first place
                                              left out, *args and **kwargs counted;
                          churn_90d           the commits, merges left out, of the last 90 days that
                                              touch its file.
                        This mode reads no module document and runs no hook. It names functions; it
                        gives no advice, and no number in it is a threshold.
Notes on stderr: a SessionStart command that exits other than 0 or times out (its stdout still counted,
none when it timed out), and a shallow clone, whose churn is short.
Exit:   0 whenever the inputs could be read, whatever they measure; 1, with a BROKEN line that says what
        failed, why and the fix, when they cannot: the module folders, a module document whose section
        is missing or out of order, a module document, a skill, hooks/hooks.json or a tracked file that
        cannot be read, PyYAML not installed, hooks/hooks.json or a skill's front matter that does not
        parse, a tracked Python file that does not parse, git that does not answer, the arguments
        misused, or the JSON file that cannot be written.
No --self-test: no list runs it, so a self-test would be a test that nothing runs. The CI step runs the
script itself on every change, where only its output shows, and the kit's `lint` and `types` entries of
scripts/gate-list.sh hold its code, as they hold every script at the top of scripts/.
Its name is metrics, never check-: the kit's check-gate-lists holds every scripts/check-*.py to the gate
group, and this script is no check.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from kit_module_doc import DocumentError, cells, module_folders, own_packages, section

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed\n  why: the report reads each skill's front matter as YAML")
    print("  fix: python3 -m pip install pyyaml")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
OK, BROKEN = 0, 1
CHURN_DAYS = 90
CC_LIMIT = 10  # cc_over_10 counts the functions above it
HOOK_TIMEOUT = 60  # seconds, for a SessionStart handler that names no timeout
EVENT = {"hook_event_name": "SessionStart", "source": "startup", "session_id": "metrics", "cwd": str(KIT)}
KINDS = ("fixture", "kit check", "live", "review", "deferred", "other")
SEPARATOR = re.compile(r"\|(?:\s*:?-+:?\s*\|)+")
ENTRY = re.compile(r"\**E\d+\**")  # an enforcement row's first cell, `E<n>` or `**E<n>**`
NUMBERED = re.compile(r"\d+\. ")
BULLETED = re.compile(r"[-*] ")
DECISION = re.compile(r"\bdec-\d{4}\b")
HANDLE = re.compile(r"([A-Z]?)(\d+)[a-z]?(?:[–-]([A-Z]?)(\d+)[a-z]?)?")
SPAN = re.compile(r"`([^`]*)`")
WHY_READ = "a number read from a document it cannot parse would be a guess, and the report states no guess"
LINK_MODE = "120000"  # git's mode of a symbolic link


class Broken(Exception):
    """An input the report needs cannot be read: the message is its BROKEN line, what failed and the fix."""


@dataclass
class Metrics:
    rows: int = 0
    gate_entries: int = 0
    advisory_entries: int = 0
    limits: int = 0
    dials: int = 0
    decisions_cited: int = 0
    deferred: int = 0
    proof_kinds: dict[str, int] = field(default_factory=lambda: dict.fromkeys(KINDS, 0))
    skills: int = 0
    skill_chars: int = 0
    always_on_chars: int = 0
    hook_events: int = 0
    code_lines: int = 0
    test_lines: int = 0
    functions: int = 0
    cc_max: int = 0
    cc_over_10: int = 0
    shared_imports: int = 0
    own_imports: int = 0
    churn_90d: int = 0


DOCUMENT_KEYS = (
    "rows",
    "gate_entries",
    "advisory_entries",
    "limits",
    "dials",
    "decisions_cited",
    "deferred",
    "skills",
    "skill_chars",
    "always_on_chars",
)
CODE_KEYS = (
    "hook_events",
    "code_lines",
    "test_lines",
    "functions",
    "cc_max",
    "cc_over_10",
    "shared_imports",
    "own_imports",
    "churn_90d",
)


# --- reading -------------------------------------------------------------------------------------


def first_table(lines: list[tuple[int, str]]) -> tuple[list[str], list[list[str]]]:
    """The header and the data rows of the first table among the lines: a line that opens with `|`
    followed by a separator line is its header, and its rows run to the first line that is no table
    line. No such table: no header and no rows."""
    for at, ((_, line), (_, below)) in enumerate(zip(lines, lines[1:], strict=False)):
        if line.strip().startswith("|") and SEPARATOR.fullmatch(below.strip()):
            rows: list[list[str]] = []
            for _, raw in lines[at + 2 :]:
                if not raw.strip().startswith("|"):
                    break
                rows.append(cells(raw))
            return cells(line), rows
    return [], []


def plain(cell: str) -> str:
    """A cell read as text: its code spans unwrapped, lowercased."""
    return SPAN.sub(r"\1", cell).strip().lower()


def items(cell: str) -> int:
    """The acceptance items a cell of handles names: each handle one, a range `T1–T5` its length; a
    token that is no handle counts as one item, since the row is one at least."""
    count = 0
    for token in cell.split(","):
        found = HANDLE.fullmatch(token.strip())
        if (
            found is not None
            and found[4] is not None
            and found[3] == found[1]
            and int(found[4]) > int(found[2])
        ):
            count += int(found[4]) - int(found[2]) + 1
        else:
            count += 1
    return count


def kind(cell: str) -> str:
    """The proof kind of an acceptance item's kind cell."""
    text = plain(cell)
    if re.search(r"\bdeferred\b", text):
        return "deferred"
    for name in KINDS[:4]:
        if re.match(rf"{re.escape(name)}\b", text):
            return name
    return "other"


def read_document(text: str, path: str, into: Metrics) -> None:
    """The document's numbers, from the sections of anchors t3, t4, t7, t9, t10 and t12."""
    try:
        rows, decisions, dials, enforcement, acceptance, deferred = (
            section(text, anchor, path) for anchor in ("t3", "t4", "t7", "t9", "t10", "t12")
        )
    except DocumentError as bad:
        raise Broken(f"{bad}\n  why: {WHY_READ}") from bad
    into.rows = len(first_table(rows)[1])
    into.decisions_cited = len({found for _, line in decisions for found in DECISION.findall(line)})
    into.dials = len(first_table(dials)[1])
    header, table = first_table(enforcement)
    at = header.index("kind") if "kind" in header else -1
    for row in table:
        if row and ENTRY.fullmatch(row[0]) and len(row) > at:
            written = plain(row[at])
            into.gate_entries += written.startswith("gate")
            into.advisory_entries += written.startswith("advisory")
    within = False
    for _, line in enforcement:
        if line.startswith("**Honest limits**"):
            within = True
        elif within and line.startswith("**"):
            break
        elif within and NUMBERED.match(line):
            into.limits += 1
    header, table = first_table(acceptance)
    if "item" in header and "kind" in header:
        first, at = header.index("item"), header.index("kind")
        for row in table:
            if len(row) > max(first, at):
                into.proof_kinds[kind(row[at])] += items(row[first])
    into.deferred = sum(1 for _, line in deferred if NUMBERED.match(line) or BULLETED.match(line))
    into.deferred += into.proof_kinds["deferred"]


def read_skills(module: Path, into: Metrics) -> int:
    """The skills' count and characters into `into`; returns the characters of their descriptions."""
    described = 0
    for skill in sorted(module.glob("skills/*/SKILL.md")):
        text = readable(skill)
        into.skills += 1
        into.skill_chars += len(text)
        where = skill.relative_to(KIT)
        head, _, rest = text.partition("\n")
        front, mark, _ = rest.partition("\n---")
        try:
            data = yaml.safe_load(front) if head.strip() == "---" and mark else None
        except yaml.YAMLError as bad:
            raise Broken(
                f"{where}: the front matter is no YAML ({bad})\n  why: {WHY_READ}\n"
                "  fix: write the front matter as YAML between two `---` lines"
            ) from bad
        if not isinstance(data, dict) or not isinstance(data.get("description"), str):
            raise Broken(
                f"{where}: no front matter with a `description` string\n  why: {WHY_READ}\n"
                "  fix: open the file with `---`, a `description:` key and its text, and `---`"
            )
        described += len(data["description"])
    return described


@dataclass(frozen=True)
class Handler:
    argv: list[str]
    timeout: float


def session_start(module: Path) -> tuple[int, list[Handler]]:
    """The number of event keys of hooks/hooks.json, and its SessionStart command handlers."""
    path = module / "hooks" / "hooks.json"
    if not path.is_file():
        return 0, []
    where = path.relative_to(KIT)
    fix = '  fix: restore it as a JSON object whose "hooks" maps each event to its handler groups'
    try:
        data = json.loads(readable(path))
    except ValueError as bad:
        raise Broken(f"{where} is no JSON ({bad})\n  why: {WHY_READ}\n{fix}") from bad
    events = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(events, dict):
        raise Broken(f'{where} has no "hooks" object\n  why: {WHY_READ}\n{fix}')
    root = str(module)
    handlers: list[Handler] = []
    for group in events.get("SessionStart", []):
        for hook in group.get("hooks", []) if isinstance(group, dict) else []:
            if not isinstance(hook, dict) or hook.get("type") != "command":
                continue
            command, args = str(hook.get("command", "")), hook.get("args")
            if isinstance(args, list):
                argv = [command] + [str(a).replace("${CLAUDE_PLUGIN_ROOT}", root) for a in args]
            else:
                argv = ["sh", "-c", command]
            handlers.append(Handler(argv, float(hook.get("timeout", HOOK_TIMEOUT))))
    return len(events), handlers


def printed(module: Path, handler: Handler, notes: list[str]) -> int:
    """The characters a SessionStart handler writes to stdout, run from the kit root; a note when it
    exits other than 0 or times out."""
    env = os.environ | {"CLAUDE_PLUGIN_ROOT": str(module), "CLAUDE_PROJECT_DIR": str(KIT)}
    shown = " ".join(handler.argv).replace(str(KIT) + "/", "")
    try:
        done = subprocess.run(
            handler.argv,
            cwd=KIT,
            env=env,
            input=json.dumps(EVENT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=handler.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        notes.append(f"{module.name}: `{shown}` timed out after {handler.timeout:g} s; counted as 0")
        return 0
    except OSError as bad:
        notes.append(f"{module.name}: `{shown}` did not start ({bad.strerror}); counted as 0")
        return 0
    if done.returncode != 0:
        notes.append(f"{module.name}: `{shown}` exited {done.returncode}; its stdout counted")
    return len(done.stdout)


def git(*args: str) -> str:
    """git's stdout, run from the kit root, or Broken."""
    try:
        done = subprocess.run(
            ["git", *args], cwd=KIT, capture_output=True, text=True, encoding="utf-8", check=False
        )
    except OSError as bad:
        raise Broken(
            f"git did not start ({bad.strerror})\n  why: the files and the churn are git's\n"
            "  fix: install git and run the report from a clone of the kit"
        ) from bad
    if done.returncode != 0:
        raise Broken(
            f"`git {' '.join(args)}` exited {done.returncode} ({done.stderr.strip()})\n"
            "  why: the files and the churn are git's\n  fix: run the report from a clone of the kit"
        )
    return done.stdout


def tracked(module: Path, folders: Iterable[str]) -> list[Path]:
    """The `.py` and `.sh` files git tracks under the module's folders, symbolic links left out."""
    out: list[Path] = []
    for line in git(
        "ls-files", "-s", "--", *(str(module.relative_to(KIT) / f) for f in folders)
    ).splitlines():
        mode, _, rest = line.partition(" ")
        name = rest.partition("\t")[2]
        if mode != LINK_MODE and name.endswith((".py", ".sh")):
            out.append(KIT / name)
    return out


def parse(path: Path) -> ast.Module:
    try:
        return ast.parse(readable(path))
    except (SyntaxError, ValueError) as bad:
        raise Broken(
            f"{path.relative_to(KIT)} does not parse as Python ({bad})\n  why: {WHY_READ}\n"
            "  fix: make it valid Python, as the kit's lint entries ask"
        ) from bad


def docstring_lines(tree: ast.Module) -> set[int]:
    """The line numbers the docstrings of the module, its classes and its functions take."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                end = body[0].end_lineno or body[0].lineno
                lines.update(range(body[0].lineno, end + 1))
    return lines


def lines_of(path: Path) -> int:
    """The file's non-blank lines that are no comment and, in Python, no docstring."""
    text = readable(path)
    skipped = docstring_lines(parse(path)) if path.suffix == ".py" else set()
    return sum(
        1
        for number, line in enumerate(text.splitlines(), start=1)
        if line.strip() and not line.strip().startswith("#") and number not in skipped
    )


BRANCHES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ExceptHandler,
    ast.IfExp,
    ast.comprehension,
    ast.Assert,
    ast.match_case,
)
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
NESTS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try, ast.TryStar, ast.Match)
TOP = 20  # the functions --complexity lists when it is given no number


def complexity(function: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """1, plus 1 per branch, plus n-1 per boolean operation of n operands, over the function's own body:
    a nested function or class is not walked."""
    count, todo = 1, list(ast.iter_child_nodes(function))
    while todo:
        node = todo.pop()
        if isinstance(node, SCOPES):
            continue
        if isinstance(node, BRANCHES):
            count += 1
        elif isinstance(node, ast.BoolOp):
            count += len(node.values) - 1
        todo.extend(ast.iter_child_nodes(node))
    return count


def is_elif(parent: ast.AST, child: ast.AST) -> bool:
    """`elif`: an `if` that is its parent `if`'s whole else branch, in the parent's column."""
    return (
        isinstance(parent, ast.If)
        and isinstance(child, ast.If)
        and parent.orelse == [child]
        and child.col_offset == parent.col_offset
    )


def nesting(node: ast.AST, level: int = 0) -> int:
    """The deepest block nesting under `node`, a nested function or class not walked."""
    deepest = level
    for child in ast.iter_child_nodes(node):
        if isinstance(child, SCOPES):
            continue
        step = isinstance(child, NESTS) and not is_elif(node, child)
        deepest = max(deepest, nesting(child, level + step))
    return deepest


def parameters(function: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """The parameters, `self` or `cls` in the first place left out, *args and **kwargs counted."""
    given = function.args
    names = [a.arg for a in (*given.posonlyargs, *given.args, *given.kwonlyargs)]
    starred = (given.vararg is not None) + (given.kwarg is not None)
    return len(names) + starred - (bool(names) and names[0] in ("self", "cls"))


@dataclass(frozen=True)
class Function:
    module: str
    path: str
    line: int
    function: str
    cc: int
    lines: int
    depth: int
    params: int
    churn_90d: int


def defined(
    node: ast.AST, prefix: str, out: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]
) -> None:
    """Every function under `node`, named under its classes and enclosing functions."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
            out.append((prefix + child.name, child))
            defined(child, f"{prefix}{child.name}.", out)
        elif isinstance(child, ast.ClassDef):
            defined(child, f"{prefix}{child.name}.", out)
        else:
            defined(child, prefix, out)


def own_python(module: Path) -> list[Path]:
    """The module's own tracked Python under scripts/: links, and so the shared const_gate, left out."""
    return [
        path
        for path in tracked(module, ("scripts",))
        if path.suffix == ".py" and "const_gate" not in path.relative_to(module).parts
    ]


def churn(path: Path) -> int:
    """The commits, merges left out, of the last 90 days that touch the file."""
    since = f"--since={CHURN_DAYS} days ago"
    return len(git("log", "--no-merges", since, "--format=%H", "--", str(path.relative_to(KIT))).split())


def complex_functions(folders: list[Path], top: int) -> list[Function]:
    """The `top` most complex functions of the modules' own Python, most complex first, ties by length."""
    found: list[Function] = []
    for module in folders:
        for path in own_python(module):
            named: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []
            defined(parse(path), "", named)
            for name, node in named:
                end = node.end_lineno or node.lineno
                where = str(path.relative_to(KIT))
                found.append(
                    Function(
                        module.name,
                        where,
                        node.lineno,
                        name,
                        complexity(node),
                        end - node.lineno + 1,
                        nesting(node),
                        parameters(node),
                        0,
                    )
                )
    found.sort(key=lambda f: (-f.cc, -f.lines, f.path, f.line))
    chosen = found[:top]
    churned = {f.path: churn(KIT / f.path) for f in chosen}
    return [replace(f, churn_90d=churned[f.path]) for f in chosen]


def read_code(module: Path, into: Metrics) -> None:
    """Lines, functions, complexity and imports of the module's tracked code."""
    into.code_lines = sum(lines_of(p) for p in tracked(module, ("scripts", "hooks")))
    into.test_lines = sum(lines_of(p) for p in tracked(module, ("tests",)))
    packages = {p.name for p in own_packages(module)}
    for path in own_python(module):
        for node in ast.walk(parse(path)):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                score = complexity(node)
                into.functions += 1
                into.cc_max = max(into.cc_max, score)
                into.cc_over_10 += score > CC_LIMIT
            elif isinstance(node, ast.Import | ast.ImportFrom):
                if isinstance(node, ast.ImportFrom) and node.level > 0:
                    into.own_imports += 1
                    continue
                names = (
                    [node.module or ""] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names]
                )
                tops = {name.partition(".")[0] for name in names}
                into.shared_imports += "const_gate" in tops
                into.own_imports += bool(tops & packages)


def readable(path: Path) -> str:
    """The file's text, or Broken naming it."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as bad:
        raise Broken(
            f"{path.relative_to(KIT)} cannot be read ({bad})\n  why: {WHY_READ}\n"
            "  fix: restore it as a UTF-8 text file the user running the report can read"
        ) from bad


def measure(module: Path, notes: list[str]) -> Metrics:
    into = Metrics()
    path = module / "MODULE.md"
    read_document(readable(path), str(path.relative_to(KIT)), into)
    described = read_skills(module, into)
    into.hook_events, handlers = session_start(module)
    into.always_on_chars = described + sum(printed(module, h, notes) for h in handlers)
    read_code(module, into)
    since = f"--since={CHURN_DAYS} days ago"
    into.churn_90d = len(
        git("log", "--no-merges", since, "--format=%H", "--", str(module.relative_to(KIT))).split()
    )
    return into


def totals(measured: dict[str, Metrics]) -> Metrics:
    total = Metrics()
    for one in measured.values():
        for key, value in asdict(one).items():
            if key == "proof_kinds":
                for name, count in value.items():
                    total.proof_kinds[name] += count
            elif key == "cc_max":
                total.cc_max = max(total.cc_max, value)
            else:
                setattr(total, key, getattr(total, key) + value)
    return total


# --- reporting -----------------------------------------------------------------------------------


def table(title: str, keys: tuple[str, ...], rows: list[tuple[str, dict[str, int]]]) -> str:
    """One plain-text table: a module column, then one column per key, right-aligned."""
    width = max(len("module"), *(len(name) for name, _ in rows))
    head = [title, "module".ljust(width) + "".join(f"  {key:>{len(key)}}" for key in keys)]
    body = [
        name.ljust(width) + "".join(f"  {values[key]:>{len(key)}}" for key in keys) for name, values in rows
    ]
    rule = "-" * len(head[1])
    return "\n".join([*head, rule, *body[:-1], rule, body[-1]])


def tables(measured: dict[str, Metrics], total: Metrics) -> str:
    named = [*measured.items(), ("totals", total)]
    flat = [(name, {k: v for k, v in asdict(m).items() if k != "proof_kinds"}) for name, m in named]
    kinds = [(name, m.proof_kinds) for name, m in named]
    return "\n\n".join(
        [
            table(
                "Documents (MODULE.md, skills, session start), advisory: a report, never a verdict",
                DOCUMENT_KEYS,
                flat,
            ),
            table("Acceptance items per proof kind (MODULE.md section 10)", KINDS, kinds),
            table("Code (git-tracked .py and .sh, links left out)", CODE_KEYS, flat),
        ]
    )


def report(measured: dict[str, Metrics], total: Metrics, commit: str, notes: list[str]) -> str:
    return json.dumps(
        {
            "advisory": "a report of law 5 of CLAUDE.md: it judges nothing",
            "commit": commit,
            "modules": {name: asdict(m) for name, m in measured.items()},
            "totals": asdict(total),
            "notes": notes,
        },
        indent=2,
        ensure_ascii=False,
    )


def ranking(functions: list[Function]) -> str:
    """The complexity list as one plain-text table, most complex first."""
    keys = ("cc", "lines", "depth", "params", "churn_90d")
    head = "  ".join(keys) + "  function"
    rows = [
        "  ".join(f"{getattr(f, key):>{len(key)}}" for key in keys) + f"  {f.function}  {f.path}:{f.line}"
        for f in functions
    ]
    title = (
        f"The {len(functions)} most complex functions of the modules' own code, advisory: a list, no verdict"
    )
    return "\n".join([title, head, "-" * len(head), *rows])


def write(path: str | None, text: str) -> None:
    """The JSON into the file `path` names, or Broken."""
    if path is None:
        return
    try:
        Path(path).write_text(text + "\n", encoding="utf-8")
    except OSError as bad:
        raise Broken(
            f"{path} cannot be written ({bad.strerror})\n  why: the JSON is the report's copy for CI's"
            " artifact\n  fix: name a path in a folder that exists and can be written to"
        ) from bad


def positive(text: str) -> int:
    """A count of at least 1, for --complexity."""
    number = int(text)
    if number < 1:
        raise ValueError(text)
    return number


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="metrics", add_help=False, allow_abbrev=False)
    parser.add_argument("--json")
    parser.add_argument("--complexity", nargs="?", const=TOP, type=positive)
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print(
            "BROKEN: misinvocation\n  why: an option or value the report does not know would measure"
            " something other than what was asked\n"
            "  fix: run with no arguments, with --json <path>, with --json -, or with --complexity [<n>],"
            " <n> a whole number of at least 1, alone or with --json"
        )
        return BROKEN
    notes: list[str] = []
    try:
        try:
            folders = module_folders(KIT)
        except DocumentError as bad:
            raise Broken(f"{bad}\n  why: the report measures each module folder") from bad
        if git("rev-parse", "--is-shallow-repository").strip() == "true":
            notes.append(
                "a shallow clone: churn_90d counts only the commits fetched — fetch the whole history"
            )
        if args.complexity is not None:
            functions = complex_functions(folders, args.complexity)
            listed = json.dumps(
                {
                    "advisory": "a list of law 5 of CLAUDE.md: it judges nothing",
                    "commit": git("rev-parse", "HEAD").strip(),
                    "functions": [asdict(f) for f in functions],
                },
                indent=2,
                ensure_ascii=False,
            )
            if args.json == "-":
                print(listed)
            else:
                write(args.json, listed)
                print(ranking(functions))
            for note in notes:
                print(f"note: {note}", file=sys.stderr)
            return OK
        measured = {module.name: measure(module, notes) for module in folders}
        commit = git("rev-parse", "HEAD").strip()
        total = totals(measured)
        written = report(measured, total, commit, notes)
        if args.json == "-":
            print(written)
        else:
            write(args.json, written)
            print(tables(measured, total))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        return BROKEN
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    return OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
