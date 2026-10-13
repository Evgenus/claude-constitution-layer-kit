#!/usr/bin/env python3
"""Kit check: every module that uses the shared gate code reaches it through a link, and the
link leads to the one source; its fixture runner reaches the module's own packages the same way.

The shared code has one source in the kit: shared/const_gate/ for the gates, shared/tests/
for the fixture harness. A module's scripts/const_gate and tests/const_gate, and the harness files
in its tests/, are symbolic links to it, relative ones leading straight to it, never through another
link, so that they survive a clone into any directory. The platform copies what such a link points at
into an installed plugin, so an installed module carries the code; inside the kit there is one copy to
read, to fix and to review. The runner, tests/run.py, imports from its own folder, which Python puts
first on the import path, so it reaches each package of the module's scripts/ through a link
tests/<package> -> ../scripts/<package>: it never edits its own import path, and never imports a
copy that has drifted from what the gate runs.

The links a module owes are derived from the folders, never typed apart from them: scripts/const_gate
and tests/const_gate, each `.py` file at the top of shared/tests/ whose name starts with neither `.`
nor `_`, as tests/<name>, and each folder at the top of the module's scripts/, itself no link, that
holds an `__init__.py`, whose name starts with neither `.` nor `_`, save const_gate, as tests/<name>.
The check is a failure to run (BROKEN) when shared/const_gate/ is no directory or when
shared/tests/ lacks one of the three files shared/GATE.md names (the FLOOR), so that a list read from
the folders cannot shrink in silence. The modules are the folders of `kit_module_doc.module_folders`, the
kit's one listing — each folder under modules/ whose name starts with neither `.` nor `_` and holds its
MODULE.md, a folder without it a BROKEN whether it uses the shared code or not. A module owes the links
when it has hooks/hooks.json, when a line of a `.py` file under its scripts/, at any depth, begins,
after white space, with `from const_gate` or `import const_gate` (the link scripts/const_gate is not
entered; a comment, a string on one line, a shell script and a
`__pycache__` are no import, while such a line inside a string of several lines counts), or when it
already has one of the links.
A module of skills alone owes none. Findings come by module, the gate package first in scripts/ and
then in tests/, then the shared files by name, then the module's own packages by name.

Modes:  no arguments   check every module under modules/;
        --self-test    prove the check on a throwaway tree: red for a missing link, a copy, a dangling
                       link, a link leading elsewhere or to its source through another link, an
                       absolute one, a text file left by a
                       checkout without symlink support, and a shared test file no module links,
                       in one module and in two; a missing, copied, misdirected, dangling or
                       absolute link to the module's own package, one through another link, and
                       a text file in its place; green for the right link, a `.`, `_`, README or
                       folder in shared/tests/ no one owes, a folder of scripts/ that is no
                       package, and the imports read over their cases;
                       a folder `.x` or `_x` skipped, a plain file of modules/ and a name without
                       `const-` by the listing's rule; BROKEN for a missing gate package or a
                       missing floor file, a folder without its MODULE.md and no modules/.
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
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, module_folders, own_packages

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

# The links a module owes are never typed: links_of() derives them from the kit's own folders.
GATE_LINK = ("scripts/const_gate", "shared/const_gate")  # the gate package: link in a module -> its source
RUNNER_GATE_LINK = ("tests/const_gate", "shared/const_gate")  # the same package, for the fixture runner
FLOOR = ("harness.py", "consumer.py", "shared_items.py")  # the files shared/GATE.md item 7 names today
IMPORT = re.compile(r"^\s*(from|import)\s+const_gate\b")  # a line that imports the shared gate package
WHY = "the shared code has one source; a module that carries its own copy drifts from it silently"
OWN_WHY = "the runner must import the code the gate runs; a copy in tests/ drifts from it silently"


class Broken(Exception):
    """The check cannot run: the shared code it derives its links from is not as the kit keeps it."""


@dataclass(frozen=True)
class Finding:
    headline: str
    fix: str
    why: str = WHY

    def render(self) -> str:
        return f"RED: {self.headline}\n  why: {self.why}\n  fix: {self.fix}"


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
    return dict([GATE_LINK, RUNNER_GATE_LINK, *((f"tests/{name}", f"shared/tests/{name}") for name in names)])


def own_links_of(kit: Path, module: Path) -> dict[str, str]:
    """The links the module's fixture runner owes to the module's own packages, link inside the module ->
    its package in the kit: each folder at the top of scripts/, itself no link, that holds an __init__.py,
    whose name starts with neither . nor _, save the shared const_gate, which links_of() covers."""
    base = module.relative_to(kit).as_posix()
    return {f"tests/{path.name}": f"{base}/scripts/{path.name}" for path in own_packages(module)}


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


def check_link(kit: Path, module: Path, link: str, source: str, why: str = WHY) -> Finding | None:
    path, target = module / link, kit / source
    shown = path.relative_to(kit).as_posix()
    wanted = os.path.relpath(target, path.parent)
    make = f"from {path.parent.relative_to(kit).as_posix()}/ run: ln -s {wanted} {path.name}"
    if not path.is_symlink():
        if path.is_dir():
            return Finding(
                f"{shown} is a directory of its own, not a link to {source}", f"remove it; {make}", why
            )
        if path.is_file():
            return Finding(
                f"{shown} is a plain file, not a link to {source} (a checkout without symlink support"
                " leaves one)",
                f"enable symlinks (git config core.symlinks true), remove the file; {make}",
                why,
            )
        return Finding(f"{shown} is missing", make, why)
    if os.path.isabs(os.readlink(path)):
        return Finding(
            f"{shown} is an absolute link, which breaks in any other clone", f"remove it; {make}", why
        )
    if not path.exists():
        return Finding(f"{shown} is a dangling link to {os.readlink(path)}", f"remove it; {make}", why)
    if path.resolve() != target.resolve():
        return Finding(f"{shown} leads to {os.readlink(path)}, not to {source}", f"remove it; {make}", why)
    if os.path.normpath(os.readlink(path)) != wanted:
        return Finding(
            f"{shown} reaches {source} through {os.readlink(path)}, not straight", f"remove it; {make}", why
        )
    return None


def check_kit(kit: Path) -> tuple[list[Finding], int, int]:
    links = links_of(kit)
    try:
        folders = module_folders(kit)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    modules = [m for m in folders if uses_shared_code(m, links)]
    owed = {
        module: [*((link, source, WHY) for link, source in links.items())]
        + [(link, source, OWN_WHY) for link, source in own_links_of(kit, module).items()]
        for module in modules
    }
    findings = [
        finding
        for module in modules
        for link, source, why in owed[module]
        if (finding := check_link(kit, module, link, source, why)) is not None
    ]
    return findings, len(modules), sum(len(each) for each in owed.values())


def report(findings: list[Finding], modules: int, links: int) -> int:
    counts = f"{links} link(s) in {modules} module(s) examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(
        "GREEN: every module reaches the shared code, and its runner the module's own packages, through"
        f" a link to their one source — {counts}"
    )
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


OWED = 2 + len(FLOOR)  # the links a module owes on a fresh tree: the gate package twice, the floor


@dataclass
class Tally:
    """The cases the self-test has judged, and those that failed."""

    judged: int = 0
    failed: int = 0

    def judge(self, ok: bool, text: str) -> None:
        """Count one case and print its line."""
        self.judged += 1
        self.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")


def root_of(link: Path) -> Path:
    return link.parent.parent.parent.parent


def add_module(root: Path, name: str) -> Path:
    module = root / "modules" / name
    (module / "hooks").mkdir(parents=True)
    (module / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
    (module / "MODULE.md").write_text("A module.\n", encoding="utf-8")
    for link, source in links_of(root).items():
        (module / link).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(root / source, (module / link).parent), module / link)
    return module


def fresh_kit(root: Path) -> Path:
    (root / "shared" / "const_gate").mkdir(parents=True)
    (root / "shared" / "tests").mkdir()
    for name in FLOOR:
        (root / "shared" / "tests" / name).write_text("", encoding="utf-8")
    return add_module(root, "const-sample") / "scripts" / "const_gate"


def as_copy(link: Path) -> None:
    link.unlink()
    link.mkdir()


def as_package_copy(link: Path) -> None:
    """scripts/const_gate a real folder holding an __init__.py: a copy, and a package by its look."""
    as_copy(link)
    (link / "__init__.py").write_text("", encoding="utf-8")


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


def hookless(path: str, text: str | bytes, keep: str | None = None) -> Callable[[Path], None]:
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
        if isinstance(text, bytes):
            script.write_bytes(text)
        else:
            script.write_text(text, encoding="utf-8")

    return damage


def beside_dangling_script(damage: Callable[[Path], None]) -> Callable[[Path], None]:
    """The damage, then a script scripts/x.py that is a dangling symbolic link."""

    def both(link: Path) -> None:
        damage(link)
        os.symlink("no_such_script.py", link.parent / "x.py")

    return both


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


def unlinked_module(name: str, document: bool = True) -> Callable[[Path], None]:
    """A folder of modules/ that has a hook and none of the links, its MODULE.md written or not."""

    def damage(link: Path) -> None:
        folder = root_of(link) / "modules" / name
        (folder / "hooks").mkdir(parents=True)
        (folder / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
        if document:
            (folder / "MODULE.md").write_text("A module.\n", encoding="utf-8")

    return damage


def plain_file(link: Path) -> None:
    """A plain file of modules/ named like a module."""
    (root_of(link) / "modules" / "const-file").write_text("not a folder\n", encoding="utf-8")


def skills_only_without_document(link: Path) -> None:
    """A folder of skills alone, owing no link, with no MODULE.md."""
    (root_of(link) / "modules" / "const-skills" / "skills").mkdir(parents=True)


def modules_gone(link: Path) -> None:
    shutil.rmtree(root_of(link) / "modules")


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


def own_package(name: str = "sample_gate", linked: str | None = None) -> Callable[[Path], None]:
    """A package scripts/<name>/ of the module's own, its link in tests/ made to `linked` or none."""

    def damage(link: Path) -> None:
        module = link.parent.parent
        (module / "scripts" / name).mkdir()
        (module / "scripts" / name / "__init__.py").write_text("", encoding="utf-8")
        if linked is not None:
            os.symlink(linked, module / "tests" / name)

    return damage


def runner_gate_through_scripts(link: Path) -> None:
    """tests/const_gate made a link to ../scripts/const_gate: it resolves to the source, not straight."""
    (link.parent.parent / "tests" / "const_gate").unlink(missing_ok=True)
    os.symlink("../scripts/const_gate", link.parent.parent / "tests" / "const_gate")


def own_package_as_text(link: Path) -> None:
    """The module's own package, its link in tests/ a one-line text file, as a checkout without links."""
    own_package()(link)
    (link.parent.parent / "tests" / "sample_gate").write_text("../scripts/sample_gate", encoding="utf-8")


def own_package_through_alias(link: Path) -> None:
    """The module's own package reached from tests/ through a second link in scripts/."""
    own_package()(link)
    os.symlink("sample_gate", link.parent / "alias")
    os.symlink("../scripts/alias", link.parent.parent / "tests" / "sample_gate")


def own_package_copied(link: Path) -> None:
    """The module's own package, copied into tests/ instead of linked."""
    own_package()(link)
    shutil.copytree(link.parent / "sample_gate", link.parent.parent / "tests" / "sample_gate")


def not_packages(link: Path) -> None:
    """Folders of scripts/ that are no package of the module's own: no __init__.py, a `.` or `_` name, and
    the shared const_gate, a package through its link."""
    scripts = link.parent
    (scripts / "data").mkdir()
    (scripts / "data" / "x.py").write_text("", encoding="utf-8")
    for name in ("__pycache__", "_private", ".mypy_cache"):
        (scripts / name).mkdir()
        (scripts / name / "__init__.py").write_text("", encoding="utf-8")
    (scripts / "single.py").write_text("", encoding="utf-8")
    shared_gate = root_of(link) / "shared" / "const_gate"
    (shared_gate / "__init__.py").write_text("", encoding="utf-8")  # scripts/const_gate, a package
    (scripts / "linked_gate").symlink_to(shared_gate)  # a link to a package, no package of its own


# the name filter over its whole set: name, a folder, owed, and why
NAME_CASES = (
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


def wrong_cases() -> dict[str, tuple[Callable[[Path], None], int]]:
    """The damages to a kit that must each be red, by case, with the findings each earns."""
    return {  # the damage, and the findings it earns
        "a missing link": (as_missing, 1),
        "the runner's gate package link missing": (
            lambda link: (link.parent.parent / "tests/const_gate").unlink(missing_ok=True),
            1,
        ),
        "the module's own package with no link in tests/": (own_package(), 1),
        "the runner's gate package linked through scripts/const_gate": (runner_gate_through_scripts, 1),
        "the module's own package copied into tests/": (own_package_copied, 1),
        "the module's own package linked through another link": (own_package_through_alias, 1),
        "the module's own package's link left a plain file in tests/": (own_package_as_text, 1),
        "the module's own package's link dangling": (own_package(linked="../scripts/no_such_gate"), 1),
        "the module's own package linked to the shared gate package": (
            own_package(linked="../../../shared/const_gate"),
            1,
        ),
        "the module's own package by an absolute link": (
            lambda link: own_package(linked=str(link.parent / "sample_gate"))(link),
            1,
        ),
        "a copied harness in tests/": (harness_as_copy, 1),
        "a hookless module importing the shared code, its links missing": (
            hookless("generate.py", "from const_gate import cli\n"),
            OWED,
        ),
        "a hookless module importing the shared code in scripts/lib/, its links missing": (
            hookless("lib/gen.py", "from const_gate import cli\n"),
            OWED,
        ),
        "a hookless module with `import const_gate` in scripts/x.py, its links missing": (
            hookless("x.py", "import const_gate\n"),
            OWED,
        ),
        "a hookless module importing the shared code in scripts/lib/const_gate/, its links missing": (
            hookless("lib/const_gate/x.py", "from const_gate import cli\n"),
            OWED,  # only the folder scripts/const_gate at the top is the link; a nested one is read
        ),
        "a hookless module with a dangling scripts/x.py beside a script importing the shared code": (
            beside_dangling_script(hookless("y.py", "import const_gate\n")),
            OWED,
        ),
        "a hookless module with non-UTF-8 bytes in a script before its import, its links missing": (
            hookless("x.py", b"# caf\xe9\nimport const_gate\n"),
            OWED,
        ),
        "a hookless module with an indented import inside a function, its links missing": (
            hookless("lib/f.py", "def f() -> None:\n    from const_gate import cli\n"),
            OWED,
        ),
        "a hookless module with an import line indented by a tab, its links missing": (
            hookless("lib/g.py", "def g() -> None:\n\tfrom const_gate import cli\n"),
            OWED,
        ),
        "a hookless module with `import` and the name apart by a tab, its links missing": (
            hookless("lib/h.py", "import\tconst_gate\n"),
            OWED,
        ),
        "a hookless module with `from const_gate.cli import y`, its links missing": (
            hookless("y.py", "from const_gate.cli import y\n"),
            OWED,
        ),
        "a hookless module that has only the link of a new shared file": (
            hookless("empty.txt", "", keep="new.py"),
            OWED,  # the gate package twice and the three of the floor, of the six links it owes
        ),
        "a hookless module that has only one link": (hookless("empty.txt", "", keep="consumer.py"), OWED - 1),
        "a shared test file no module links": (new_file_unlinked, 1),
        "a shared test file no one of two linking modules links": (new_file_in_two_modules, 2),
        "a folder named without const- that uses the shared code, its links missing": (
            unlinked_module("glossary"),
            OWED,  # the listing has no name rule: the folder owes the links like any module
        ),
        "a copy": (as_copy, 1),
        "a copy that is a package, owed once as the gate package and never as one of its own": (
            as_package_copy,
            1,
        ),
        "a text file": (as_text_file, 1),
        "a dangling link": (as_dangling, 1),
        "a link leading elsewhere": (as_elsewhere, 1),
        "an absolute link": (as_absolute, 1),
    }


def reads_cases() -> dict[str, tuple[Callable[[Path], None], int, tuple[str, ...]]]:
    """The damages whose plain run must print the given words and give the given exit code."""
    # what the plain run prints: the damage, the exit code, the words the output must hold
    return {
        "a shared test file no module links, taught with its ln -s": (
            new_file_in_two_modules,
            EXIT_RED,
            (
                "RED: 2 finding(s) — 12 link(s) in 2 module(s) examined",
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
        "the module's own package, linked from tests/, taught and counted": (
            own_package(linked="../scripts/sample_gate"),
            EXIT_GREEN,
            ("GREEN:", "6 link(s) in 1 module(s) examined"),
        ),
        "the module's own package missing in tests/, taught with its ln -s": (
            own_package(),
            EXIT_RED,
            (
                "RED: modules/const-sample/tests/sample_gate is missing",
                f"why: {OWN_WHY}",
                "fix: from modules/const-sample/tests/ run: ln -s ../scripts/sample_gate sample_gate",
                "RED: 1 finding(s) — 6 link(s) in 1 module(s) examined",
            ),
        ),
        "folders of scripts/ that are no package of the module's own owe nothing": (
            not_packages,
            EXIT_GREEN,
            ("GREEN:", "5 link(s) in 1 module(s) examined"),
        ),
        "folders . and _ of modules/ holding a hook skipped": (
            hidden_folders,
            EXIT_GREEN,
            ("GREEN:", "5 link(s) in 1 module(s) examined"),
        ),
        "a plain file of modules/ named like a module is no module": (
            plain_file,
            EXIT_GREEN,
            ("GREEN:", "5 link(s) in 1 module(s) examined"),
        ),
        "a README and a folder in shared/tests/ not owed": (
            not_shared_files,
            EXIT_GREEN,
            ("GREEN:", "5 link(s) in 1 module(s) examined"),
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
        "a dangling scripts/x.py alone owes nothing": (
            beside_dangling_script(hookless("empty.txt", "")),
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
        "a hooked folder without its MODULE.md": (
            unlinked_module("const-ghost", document=False),
            EXIT_BROKEN,
            (
                "BROKEN: modules/const-ghost has no MODULE.md — fix: restore the module document",
                "BROKEN: the check could not run — 0 links examined",
            ),
        ),
        "a folder of skills alone without its MODULE.md": (
            skills_only_without_document,
            EXIT_BROKEN,
            (
                "BROKEN: modules/const-skills has no MODULE.md — fix: restore the module document",
                "BROKEN: the check could not run — 0 links examined",
            ),
        ),
        "no modules/ directory": (
            modules_gone,
            EXIT_BROKEN,
            (
                "has no modules/ directory — fix: run the script from a checkout of the kit",
                "BROKEN: the check could not run — 0 links examined",
            ),
        ),
        "shared/tests/ gone": (
            tests_gone,
            EXIT_BROKEN,
            ("BROKEN: shared/tests/ lacks harness.py, consumer.py, shared_items.py, which",),
        ),
    }


def judge_wrong(tally: Tally) -> None:
    """Each damage is red against a kit that was green."""
    for name, (damage, findings) in wrong_cases().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            link = fresh_kit(root)
            green_before = not check_kit(root)[0]
            damage(link)
            red_after = len(check_kit(root)[0]) == findings
        tally.judge(green_before and red_after, f"the right link is green, {name} is red")


def judge_reads(tally: Tally) -> None:
    """The plain run of each damaged kit gives its exit code and holds its words."""
    for name, (damage, code, words) in reads_cases().items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            link = fresh_kit(root)
            with contextlib.redirect_stdout(io.StringIO()):
                green_before = run(root) == EXIT_GREEN
            damage(link)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code_after = run(root)
        ok = green_before and code_after == code and all(word in out.getvalue() for word in words)
        tally.judge(ok, f"the right link is green, {name} reads exit {code}")


def judge_order(tally: Tally) -> None:
    """The findings of two modules come by module, the gate package first, the files by name."""
    # the order of the findings, held whole: no row of `reads` compares order, which asks the one list
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_kit(root)
        shutil.rmtree(root / "modules" / "const-sample")
        for module in ("const-a", "const-b"):
            (root / "modules" / module / "hooks").mkdir(parents=True)
            (root / "modules" / module / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
            (root / "modules" / module / "MODULE.md").write_text("A module.\n", encoding="utf-8")
            for package in ("a_gate", "b_gate"):
                (root / "modules" / module / "scripts" / package).mkdir(parents=True)
                (root / "modules" / module / "scripts" / package / "__init__.py").write_text(
                    "", encoding="utf-8"
                )
        out = io.StringIO()
        # modules/ and shared/tests/ are listed reversed, whatever the filesystem lists
        with contextlib.redirect_stdout(out), listed_in_reverse():
            code_after = run(root)
    heads = [line for line in out.getvalue().splitlines() if line.startswith("RED: modules/")]
    expected = [
        f"RED: modules/{module}/{link} is missing"
        for module in ("const-a", "const-b")
        for link in (
            "scripts/const_gate",
            "tests/const_gate",
            "tests/consumer.py",
            "tests/harness.py",
            "tests/shared_items.py",
            "tests/a_gate",
            "tests/b_gate",
        )
    ]
    ok = code_after == EXIT_RED and heads == expected
    tally.judge(
        ok,
        "findings by module, the gate package in scripts/ then in tests/,"
        " the shared files by name, then the module's own packages by name",
    )


def judge_names(tally: Tally) -> None:
    """A file or folder at the top of shared/tests/ is owed a link by its name alone."""
    for name, folder, is_owed, why in NAME_CASES:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh_kit(root)
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
        shown, verdict = name + ("/" if folder else ""), "owed" if is_owed else "not owed"
        tally.judge(ok, f"shared/tests/{shown} is {verdict}: {why}")


def self_test() -> int:
    """Red→green on a throwaway kit: each wrong state must be red, the right link green; what a module
    owes follows the folders (a new shared test file is owed at once, a name that starts `.` or `_` or is
    no `.py` file is not), and the shared code missing its floor is BROKEN."""
    tally = Tally()
    judge_wrong(tally)
    judge_reads(tally)
    judge_order(tally)
    judge_names(tally)
    print(f"{tally.judged - tally.failed}/{tally.judged} red→green cases green")
    return EXIT_GREEN if tally.failed == 0 else EXIT_RED


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
