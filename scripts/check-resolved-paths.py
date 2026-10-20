#!/usr/bin/env python3
"""Kit check, never shipped in a module: every package the fixture runner imports through a link
reads `__file__` only through `Path(__file__).resolve()` (template §6, rule 1; decision
dec-0073-packages-resolve-their-own-file).

A module's runner imports the shared package, the shared test files and the module's own packages
through relative links in its `tests/` (item 7 of kit-shared-gate-code §2). Python sets `__file__`
of a module imported so to the path through the link, never to the file's own place, so a package
that derives a path from `__file__` without resolving it finds one thing under its fixtures and
another in a hook run. Resolving it first gives the file's own place in both.

The files read: every `.py` file, at any depth, of each module's own packages, as `own_packages` of
`kit_module_doc` derives them, of `shared/constitution_layer_kit/`, and at the top of `shared/tests/` whose
name
starts with neither `.` nor `_`, as for the links of item 7 of kit-shared-gate-code §2; a
`__pycache__` is never read, nor a folder that is a link. Each use of the name `__file__` must stand
as the one argument of a call of `Path` — the name, or `pathlib.Path` — whose result is at once
resolved, `.resolve()`; any other use is a finding: `Path(__file__).parent`, `os.path.dirname(__file__)`,
`Path(__file__).absolute()`, the name passed on or bound to another name. The entry files at the top
of a module's `scripts/`, run by path, and the module's own test files in `tests/`, which pytest imports
from where they stand, are never reached through a link, and are not read.

Modes:  no arguments   check the kit;
        --self-test    prove the check on throwaway kits: a resolved read green in a module's package,
                       in the shared package and through `pathlib.Path`; `.parent`, `os.path`,
                       `.absolute()`, an unresolved `Path` and the bare name each a finding; a folder
                       with no `__init__.py`, a `_` folder, a `_` shared test file, an entry file
                       and three links to an outside package not read; the report of one finding
                       as literal lines with exit 2; a file that does not parse and a module
                       folder without its document each a BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, module_folders, own_packages

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
WHY = (
    "the fixture runner imports this package through a link in tests/, where `__file__` is the link's "
    "path and not the file's own"
)
FIX = "write Path(__file__).resolve() and derive every path from it"


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int

    def render(self) -> str:
        return (
            f"RED: {self.path}:{self.line}: `__file__` read without Path(__file__).resolve()\n"
            f"  why: {WHY}\n"
            f"  fix: {FIX}"
        )


def files_of(kit: Path) -> tuple[list[Path], int]:
    """The .py files the check reads, sorted, and the number of folders read, shared/tests one of them."""
    try:
        modules = module_folders(kit)
    except DocumentError as bad:
        raise Broken(str(bad)) from None
    roots = [package for module in modules for package in own_packages(module)]
    roots.append(kit / "shared" / "constitution_layer_kit")
    files: list[Path] = []
    for root in roots:
        if root.is_dir():
            files.extend(walk(root))
    tests = kit / "shared" / "tests"
    if tests.is_dir():
        files.extend(
            sorted(
                p
                for p in tests.iterdir()
                if p.suffix == ".py"
                and p.is_file()
                and not p.is_symlink()
                and not p.name.startswith((".", "_"))
            )
        )
    return sorted(files), len(roots) + 1


def walk(folder: Path) -> list[Path]:
    """Every .py file under the folder, a __pycache__ and a linked folder left out."""
    found: list[Path] = []
    for path in sorted(folder.iterdir()):
        if path.is_symlink() or path.name == "__pycache__":
            continue
        if path.is_dir():
            found.extend(walk(path))
        elif path.suffix == ".py":
            found.append(path)
    return found


def resolved(node: ast.Name, parents: dict[int, ast.AST]) -> bool:
    """The name is the one argument of Path(...) or pathlib.Path(...), and that call is at once
    resolved with .resolve()."""
    call = parents.get(id(node))
    if not (isinstance(call, ast.Call) and call.args == [node] and not call.keywords):
        return False
    func = call.func
    named = (isinstance(func, ast.Name) and func.id == "Path") or (
        isinstance(func, ast.Attribute)
        and func.attr == "Path"
        and isinstance(func.value, ast.Name)
        and func.value.id == "pathlib"
    )
    attribute = parents.get(id(call))
    if not (named and isinstance(attribute, ast.Attribute) and attribute.attr == "resolve"):
        return False
    outer = parents.get(id(attribute))
    return isinstance(outer, ast.Call) and outer.func is attribute


def findings_in(path: Path, shown: str) -> list[Finding]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as bad:
        raise Broken(f"{shown} cannot be read or parsed ({bad}) — fix: make it valid UTF-8 Python") from None
    parents = {id(child): parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    return [
        Finding(shown, node.lineno)
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "__file__" and not resolved(node, parents)
    ]


def check(kit: Path) -> tuple[list[Finding], int, int]:
    files, packages = files_of(kit)
    findings = [f for path in files for f in findings_in(path, path.relative_to(kit).as_posix())]
    return sorted(findings, key=lambda f: (f.path, f.line)), len(files), packages


def report(findings: list[Finding], files: int, packages: int) -> int:
    counts = f"{files} file(s) in {packages} folder(s) examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every package a runner imports through a link reads __file__ resolved — {counts}")
    return EXIT_GREEN


def toy_kit(root: Path, start: str, shared: str = "") -> None:
    """One module const-a with its package a_gate, its entry file, a non-package folder, a `_` folder,
    and links to an outside package from scripts/, from inside a_gate and from shared/tests/; the
    shared package, one shared test file and a `_` file beside it. Every file the check must not read
    holds an unresolved read, so reading one turns a green case red."""
    module = root / "modules" / "const-a"
    (module / "scripts" / "a_gate").mkdir(parents=True)
    (module / "MODULE.md").write_text("# const-a\n", encoding="utf-8")
    (module / "scripts" / "a_gate" / "__init__.py").write_text("", encoding="utf-8")
    (module / "scripts" / "a_gate" / "start.py").write_text(start, encoding="utf-8")
    unread = "from pathlib import Path\nHERE = Path(__file__).parent\n"
    (module / "scripts" / "check-a.py").write_text(unread, encoding="utf-8")
    for folder, marker in (("data", False), ("_private", True)):
        (module / "scripts" / folder).mkdir()
        if marker:
            (module / "scripts" / folder / "__init__.py").write_text("", encoding="utf-8")
        (module / "scripts" / folder / "x.py").write_text(unread, encoding="utf-8")
    (root / "shared" / "constitution_layer_kit").mkdir(parents=True)
    (root / "shared" / "tests").mkdir()
    (root / "shared" / "constitution_layer_kit" / "__init__.py").write_text("", encoding="utf-8")
    (root / "shared" / "constitution_layer_kit" / "where.py").write_text(shared, encoding="utf-8")
    (root / "shared" / "tests" / "harness.py").write_text("", encoding="utf-8")
    (module / "scripts" / "constitution_layer_kit").symlink_to(
        Path("..", "..", "..", "shared", "constitution_layer_kit")
    )
    (root / "shared" / "tests" / "_private.py").write_text(unread, encoding="utf-8")
    outside = root / "elsewhere" / "pkg"
    outside.mkdir(parents=True)
    (outside / "__init__.py").write_text("", encoding="utf-8")
    (outside / "x.py").write_text(unread, encoding="utf-8")
    (module / "scripts" / "linked").symlink_to(Path("..", "..", "..", "elsewhere", "pkg"))
    (module / "scripts" / "a_gate" / "inner").symlink_to(Path("..", "..", "..", "..", "elsewhere", "pkg"))
    (root / "shared" / "tests" / "linked.py").symlink_to(Path("..", "..", "elsewhere", "pkg", "x.py"))


def self_test() -> int:
    """Red→green on throwaway kits: each case's lines of findings, as path:line, typed by hand."""
    ok_read = "from pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n"
    cases: list[tuple[str, str, str, list[str]]] = [
        ("a resolved read in a module's package is green", ok_read, "", []),
        (
            "pathlib.Path(__file__).resolve() is green",
            "import pathlib\nROOT = pathlib.Path(__file__).resolve().parent\n",
            "",
            [],
        ),
        (
            "Path(__file__).parent is a finding",
            "from pathlib import Path\nROOT = Path(__file__).parent\n",
            "",
            ["modules/const-a/scripts/a_gate/start.py:2"],
        ),
        (
            "os.path.dirname(__file__) is a finding",
            "import os\nROOT = os.path.dirname(__file__)\n",
            "",
            ["modules/const-a/scripts/a_gate/start.py:2"],
        ),
        (
            "Path(__file__).absolute() is a finding",
            "from pathlib import Path\nROOT = Path(__file__).absolute()\n",
            "",
            ["modules/const-a/scripts/a_gate/start.py:2"],
        ),
        (
            "an unresolved Path(__file__) and a resolve never called are findings",
            "from pathlib import Path\nA = Path(__file__)\nB = Path(__file__).resolve\n",
            "",
            ["modules/const-a/scripts/a_gate/start.py:2", "modules/const-a/scripts/a_gate/start.py:3"],
        ),
        (
            "the bare name bound or passed on is a finding",
            "NAME = __file__\nprint(__file__)\n",
            "",
            ["modules/const-a/scripts/a_gate/start.py:1", "modules/const-a/scripts/a_gate/start.py:2"],
        ),
        (
            "an unresolved read in the shared package is a finding",
            ok_read,
            "from pathlib import Path\nHERE = Path(__file__).parent\n",
            ["shared/constitution_layer_kit/where.py:2"],
        ),
    ]
    failed = 0
    for name, start, shared, wanted in cases:
        with tempfile.TemporaryDirectory() as tmp:
            toy_kit(Path(tmp), start, shared)
            got = [f"{f.path}:{f.line}" for f in check(Path(tmp))[0]]
        ok = got == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        got {got}")
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: modules/const-a/scripts/a_gate/start.py:2: `__file__` read without Path(__file__).resolve()",
        "  why: the fixture runner imports this package through a link in tests/, where `__file__` is the "
        "link's path and not the file's own",
        "  fix: write Path(__file__).resolve() and derive every path from it",
        "RED: 1 finding(s) — 5 file(s) in 3 folder(s) examined",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        toy_kit(Path(tmp), "from pathlib import Path\nROOT = Path(__file__).parent\n")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check(Path(tmp)))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    broken_cases = [
        ("a file that does not parse", "modules/const-a/scripts/a_gate/start.py cannot be read or parsed"),
        ("a module folder without its document", "modules/const-b has no MODULE.md"),
    ]
    for name, said in broken_cases:
        with tempfile.TemporaryDirectory() as tmp:
            toy_kit(Path(tmp), "def (\n" if "parse" in name else ok_read)
            if "document" in name:
                (Path(tmp) / "modules" / "const-b").mkdir()
            try:
                check(Path(tmp))
                ok = False
            except Broken as broken:
                ok = str(broken).startswith(said) and "fix:" in str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line")
    total = len(cases) + 1 + len(broken_cases)
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-resolved-paths", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 files examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 files examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
