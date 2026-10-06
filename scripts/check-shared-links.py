#!/usr/bin/env python3
"""Kit check: every module that uses the shared gate code reaches it through a link, and the
link leads to the one source.

The shared code has one source in the kit: shared/const_gate/ for the gates, shared/tests/
for the fixture harness. A module's scripts/const_gate, and the harness files in its tests/,
are symbolic links to it, relative ones, so that they survive a clone into any directory. The
platform copies what such a link points at into an installed plugin, so an installed module
carries the code; inside the kit there is one copy to read, to fix and to review.

Modes:  no arguments   check every module under modules/;
        --self-test    prove the check on a throwaway tree: red for a missing link, a copy, a dangling
                       link, a link leading elsewhere, an absolute one, a text file left by a
                       checkout without symlink support; green for the right link.
Exit:   0 green; 2 a link is wrong; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

# The links a module owes are never typed: links_of() derives them from the kit's own folders.
GATE_LINK = ("scripts/const_gate", "shared/const_gate")  # the gate package: link in a module -> its source
FLOOR = ("harness.py", "consumer.py", "shared_items.py")  # the files shared/GATE.md item 7 names today
IMPORT = re.compile(r"^\s*(from|import)\s+const_gate\b")  # a line that imports the shared gate package
WHY = "the shared code has one source; a module that carries its own copy drifts from it silently"


class Broken(Exception):
    """The check cannot run: the shared code it derives its links from is not as the kit keeps it."""


@dataclass(frozen=True)
class Finding:
    headline: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.headline}\n  why: {WHY}\n  fix: {self.fix}"


def links_of(kit: Path) -> dict[str, str]:
    """Every link a module that uses the shared code owes, link inside the module -> its one source
    in the kit: the gate package, and each regular .py file at the top of shared/tests/ whose name
    starts with neither . nor _. Broken when the gate package is no directory, or when shared/tests/
    lacks a file of the floor, so a derived list cannot shrink in silence."""
    if not (kit / GATE_LINK[1]).is_dir():
        raise Broken(f"{GATE_LINK[1]}/ is no directory — fix: restore it from the kit's history")
    tests = kit / "shared" / "tests"
    names = sorted(
        path.name
        for path in (tests.iterdir() if tests.is_dir() else [])
        if path.name.endswith(".py") and not path.name.startswith((".", "_")) and path.is_file()
    )
    if lacking := [name for name in FLOOR if name not in names]:
        raise Broken(
            f"shared/tests/ lacks {', '.join(lacking)}, which shared/GATE.md names for every module's tests/"
            " — fix: restore it from the kit's history"
        )
    return dict([GATE_LINK, *((f"tests/{name}", f"shared/tests/{name}") for name in names)])


def imports_shared_code(module: Path) -> bool:
    """A line of a .py file under the module's scripts/, at any depth, imports const_gate. The link
    scripts/const_gate is not followed into the shared code, and a __pycache__ is not read."""
    scripts = module / "scripts"
    for folder, directories, files in os.walk(scripts):
        directories[:] = [
            each
            for each in directories
            if each != "__pycache__" and not (Path(folder) == scripts and each == "const_gate")
        ]
        for name in files:
            path = Path(folder) / name
            if name.endswith(".py") and path.is_file():
                text = path.read_text(encoding="utf-8", errors="replace")
                if any(IMPORT.match(line) for line in text.splitlines()):
                    return True
    return False


def uses_shared_code(module: Path, links: dict[str, str]) -> bool:
    """A module owes the links when it has a hook, when a script of it imports the shared code — a
    scan or a generator — or when it already has one of the links. A module of skills alone owes none."""
    return (
        (module / "hooks" / "hooks.json").is_file()
        or imports_shared_code(module)
        or any((module / link).is_symlink() for link in links)
    )


def check_link(kit: Path, module: Path, link: str, source: str) -> Finding | None:
    path, target = module / link, kit / source
    shown = path.relative_to(kit).as_posix()
    wanted = os.path.relpath(target, path.parent)
    make = f"from {path.parent.relative_to(kit).as_posix()}/ run: ln -s {wanted} {path.name}"
    if not path.is_symlink():
        if path.is_dir():
            return Finding(f"{shown} is a directory of its own, not a link to {source}", f"remove it; {make}")
        if path.is_file():
            return Finding(
                f"{shown} is a plain file, not a link to {source} (a checkout without symlink support"
                " leaves one)",
                f"enable symlinks (git config core.symlinks true), remove the file; {make}",
            )
        return Finding(f"{shown} is missing", make)
    if os.path.isabs(os.readlink(path)):
        return Finding(f"{shown} is an absolute link, which breaks in any other clone", f"remove it; {make}")
    if not path.exists():
        return Finding(f"{shown} is a dangling link to {os.readlink(path)}", f"remove it; {make}")
    if path.resolve() != target.resolve():
        return Finding(f"{shown} leads to {os.readlink(path)}, not to {source}", f"remove it; {make}")
    return None


def check_kit(kit: Path) -> tuple[list[Finding], int, int]:
    links = links_of(kit)
    modules = sorted(
        m
        for m in (kit / "modules").iterdir()
        if m.is_dir() and not m.name.startswith((".", "_")) and uses_shared_code(m, links)
    )
    findings = [
        finding
        for module in modules
        for link, source in links.items()
        if (finding := check_link(kit, module, link, source)) is not None
    ]
    return findings, len(modules), len(modules) * len(links)


def report(findings: list[Finding], modules: int, links: int) -> int:
    counts = f"{links} link(s) in {modules} module(s) examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every module reaches the shared code through a link to its one source — {counts}")
    return EXIT_GREEN


def run(kit: Path) -> int:
    """The plain run on a kit: its output and its exit code."""
    if not (kit / "modules").is_dir():
        print(f"BROKEN: {kit} has no modules/ directory — fix: run the script from a checkout of the kit")
        print("BROKEN: the check could not run — 0 links examined")
        return EXIT_BROKEN
    try:
        result = check_kit(kit)
    except Broken as error:
        print(f"BROKEN: {error}")
        print("BROKEN: the check could not run — 0 links examined")
        return EXIT_BROKEN
    return report(*result)


def self_test() -> int:
    """Red→green on a throwaway kit: each wrong state must be red, the right link green."""
    owed = 1 + len(FLOOR)  # the links a module owes on a fresh tree

    def root_of(link: Path) -> Path:
        return link.parent.parent.parent.parent

    def add_module(root: Path, name: str) -> Path:
        module = root / "modules" / name
        (module / "hooks").mkdir(parents=True)
        (module / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
        for link, source in links_of(root).items():
            (module / link).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(os.path.relpath(root / source, (module / link).parent), module / link)
        return module

    def fresh(root: Path) -> Path:
        (root / "shared" / "const_gate").mkdir(parents=True)
        (root / "shared" / "tests").mkdir()
        for name in FLOOR:
            (root / "shared" / "tests" / name).write_text("", encoding="utf-8")
        return add_module(root, "const-sample") / "scripts" / "const_gate"

    def as_copy(link: Path) -> None:
        link.unlink()
        link.mkdir()

    def as_text_file(link: Path) -> None:
        link.unlink()
        link.write_text("../../../shared/const_gate", encoding="utf-8")

    def as_dangling(link: Path) -> None:
        link.unlink()
        os.symlink("../../../shared/no_such_gate", link)

    def as_elsewhere(link: Path) -> None:
        link.unlink()
        os.symlink("../tests", link)

    def as_absolute(link: Path) -> None:
        target = link.resolve()
        link.unlink()
        os.symlink(target, link)

    def as_missing(link: Path) -> None:
        link.unlink()

    def harness_as_copy(link: Path) -> None:
        harness = link.parent.parent / "tests" / "harness.py"
        harness.unlink()
        harness.write_text("", encoding="utf-8")

    def new_shared(root: Path) -> None:
        (root / "shared" / "tests" / "new.py").write_text("", encoding="utf-8")

    def new_file_unlinked(link: Path) -> None:
        """A fourth shared test file appears; no module links it."""
        new_shared(root_of(link))

    def new_file_in_two_modules(link: Path) -> None:
        """The same, with a second linking module: each owes the file."""
        add_module(root_of(link), "const-other")
        new_shared(root_of(link))

    def new_file_as_copy(link: Path) -> None:
        """The wrong fix: a plain copy of the new file in the module's tests/."""
        new_shared(root_of(link))
        (link.parent.parent / "tests" / "new.py").write_text("", encoding="utf-8")

    def hookless(path: str, text: str, keep: str | None = None) -> Callable[[Path], None]:
        """No hook; the links gone, bar the one kept; one script written at `path` under scripts/."""

        def damage(link: Path) -> None:
            module = link.parent.parent
            if keep == "new.py":  # a shared file the module alone links
                new_shared(root_of(link))
                os.symlink("../../../shared/tests/new.py", module / "tests" / "new.py")
            (module / "hooks" / "hooks.json").unlink()
            (module / "hooks").rmdir()
            for each in links_of(root_of(link)):  # only the import or the kept link can make the module owe
                if each != f"tests/{keep}":
                    (module / each).unlink()
            script = module / "scripts" / path
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text(text, encoding="utf-8")

        return damage

    def hidden_folders(link: Path) -> None:
        """Folders of modules/ that start with . or _ and hold a hook, with no link: no module."""
        for name in (".wip", "_draft"):
            (root_of(link) / "modules" / name / "hooks").mkdir(parents=True)
            (root_of(link) / "modules" / name / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")

    def not_shared_files(link: Path) -> None:
        """Files of shared/tests/ that are no .py file at its top: a README, a folder with a .py in it."""
        tests = root_of(link) / "shared" / "tests"
        (tests / "README.md").write_text("", encoding="utf-8")
        (tests / "__pycache__").mkdir()
        (tests / "__pycache__" / "inner.py").write_text("", encoding="utf-8")

    def without_harness(link: Path) -> None:
        (root_of(link) / "shared" / "tests" / "harness.py").unlink()

    def without_gate(link: Path) -> None:
        shutil.rmtree(root_of(link) / "shared" / "const_gate")

    def tests_emptied(link: Path) -> None:
        for name in FLOOR:
            (root_of(link) / "shared" / "tests" / name).unlink()

    def tests_gone(link: Path) -> None:
        tests = root_of(link) / "shared" / "tests"
        for name in FLOOR:
            (tests / name).unlink()
        tests.rmdir()

    wrong: dict[str, tuple[Callable[[Path], None], int]] = {  # the damage, and the findings it earns
        "a missing link": (as_missing, 1),
        "a copied harness in tests/": (harness_as_copy, 1),
        "a hookless module importing the shared code, its links missing": (
            hookless("generate.py", "from const_gate import cli\n"),
            owed,
        ),
        "a hookless module importing the shared code in scripts/lib/, its links missing": (
            hookless("lib/gen.py", "from const_gate import cli\n"),
            owed,
        ),
        "a hookless module with `import const_gate` in scripts/x.py, its links missing": (
            hookless("x.py", "import const_gate\n"),
            owed,
        ),
        "a hookless module with an indented import inside a function, its links missing": (
            hookless("lib/f.py", "def f() -> None:\n    from const_gate import cli\n"),
            owed,
        ),
        "a hookless module with `from const_gate.cli import y`, its links missing": (
            hookless("y.py", "from const_gate.cli import y\n"),
            owed,
        ),
        "a hookless module that has only the link of a new shared file": (
            hookless("empty.txt", "", keep="new.py"),
            owed,  # the gate package and the three of the floor, of the five links it owes
        ),
        "a hookless module that has only one link": (hookless("empty.txt", "", keep="consumer.py"), owed - 1),
        "a shared test file no module links": (new_file_unlinked, 1),
        "a shared test file no one of two linking modules links": (new_file_in_two_modules, 2),
        "a copy": (as_copy, 1),
        "a text file": (as_text_file, 1),
        "a dangling link": (as_dangling, 1),
        "a link leading elsewhere": (as_elsewhere, 1),
        "an absolute link": (as_absolute, 1),
    }
    # what the plain run prints: the damage, the exit code, the words the output must hold
    reads: dict[str, tuple[Callable[[Path], None], int, tuple[str, ...]]] = {
        "a shared test file no module links, taught with its ln -s": (
            new_file_in_two_modules,
            EXIT_RED,
            (
                "RED: 2 finding(s) — 10 link(s) in 2 module(s) examined",
                "RED: modules/const-sample/tests/new.py is missing",
                "fix: from modules/const-sample/tests/ run: ln -s ../../../shared/tests/new.py new.py",
                "RED: modules/const-other/tests/new.py is missing",
            ),
        ),
        "a plain copy of a new shared test file": (
            new_file_as_copy,
            EXIT_RED,
            ("modules/const-sample/tests/new.py is a plain file, not a link to shared/tests/new.py",),
        ),
        "folders . and _ of modules/ holding a hook skipped": (
            hidden_folders,
            EXIT_GREEN,
            ("GREEN:", "4 link(s) in 1 module(s) examined"),
        ),
        "a README and a folder in shared/tests/ not owed": (
            not_shared_files,
            EXIT_GREEN,
            ("GREEN:", "4 link(s) in 1 module(s) examined"),
        ),
        "a comment holding the word const_gate owes nothing": (
            hookless("tool.py", "# const_gate\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a commented-out import owes nothing": (
            hookless("tool.py", "# from const_gate import cli\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a string holding the word const_gate owes nothing": (
            hookless("tool.py", 'NAME = "const_gate"\n'),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a name that only starts with const_gate owes nothing": (
            hookless("tool.py", "import const_gate_x\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "an import in a shell script owes nothing": (
            hookless("x.sh", "import const_gate\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "an import in a __pycache__ owes nothing": (
            hookless("__pycache__/x.py", "import const_gate\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "an import inside a folder scripts/const_gate of its own is not read": (
            hookless("const_gate/x.py", "from const_gate import cli\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "shared/tests/harness.py removed": (
            without_harness,
            EXIT_BROKEN,
            (
                "BROKEN: shared/tests/ lacks harness.py, which shared/GATE.md names",
                "fix: restore it from the kit's history",
                "BROKEN: the check could not run — 0 links examined",
            ),
        ),
        "shared/const_gate/ removed": (
            without_gate,
            EXIT_BROKEN,
            ("BROKEN: shared/const_gate/ is no directory — fix: restore it from the kit's history",),
        ),
        "shared/tests/ emptied": (
            tests_emptied,
            EXIT_BROKEN,
            ("BROKEN: shared/tests/ lacks harness.py, consumer.py, shared_items.py, which",),
        ),
        "shared/tests/ gone": (
            tests_gone,
            EXIT_BROKEN,
            ("BROKEN: shared/tests/ lacks harness.py, consumer.py, shared_items.py, which",),
        ),
    }
    # the name filter over its whole set: name, a folder, owed, and why
    names = (
        ("a.py", False, True, "a .py file at the top"),
        ("_a.py", False, False, "starts with _"),
        (".a.py", False, False, "starts with ."),
        ("a.pyc", False, False, "does not end in .py"),
        ("a.py.bak", False, False, "does not end in .py"),
        ("A.PY", False, False, "the suffix is .py, matched as written"),
        ("d.py", True, False, "a folder, no regular file"),
        ("__pycache__", True, False, "a folder, and starts with _"),
        ("README.md", False, False, "does not end in .py"),
    )
    failed = 0
    for name, (damage, findings) in wrong.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            link = fresh(root)
            green_before = not check_kit(root)[0]
            damage(link)
            red_after = len(check_kit(root)[0]) == findings
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the right link is green, {name} is red")
    for name, (damage, code, words) in reads.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            link = fresh(root)
            with contextlib.redirect_stdout(io.StringIO()):
                green_before = run(root) == EXIT_GREEN
            damage(link)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code_after = run(root)
        ok = green_before and code_after == code and all(word in out.getvalue() for word in words)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the right link is green, {name} reads exit {code}")
    for name, folder, is_owed, why in names:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            path = root / "shared" / "tests" / name
            if folder:
                path.mkdir()
                (path / "inner.py").write_text("", encoding="utf-8")
            else:
                path.write_text("", encoding="utf-8")
            found = check_kit(root)[0]
        ok = len(found) == (1 if is_owed else 0) and (
            not is_owed or f"tests/{name} is missing" in found[0].headline
        )
        failed += 0 if ok else 1
        shown, verdict = name + ("/" if folder else ""), "owed" if is_owed else "not owed"
        print(f"[{'ok' if ok else 'FAIL'}] shared/tests/{shown} is {verdict}: {why}")
    total = len(wrong) + len(reads) + len(names)
    print(f"{total - failed}/{total} red→green cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-shared-links", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 links examined")
        return EXIT_BROKEN
    if args.self_test:
        return self_test()
    return run(KIT)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
