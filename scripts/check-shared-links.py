#!/usr/bin/env python3
"""Kit check: no plugin holds the shared gate code, every module's fixture runner reaches it through a
link, and the link leads to the one source; the runner reaches the module's own packages the same way.

The shared code has one source in the kit: shared/constitution_layer_kit/ for the gates, shared/tests/
for the fixture harness. A plugin holds none of it: its entry files import the Python package
constitution-layer-kit that pip installed for python3 (decision
dec-0099-shared-code-installed-as-a-pip-package). So nothing may stand at
plugin/scripts/constitution_layer_kit, in any module, whether or not the module uses the shared code: no
link, no copy, no file, a dangling link included, since a script's folder comes first on Python's path and
whatever stood there would shadow the installed package. The finding names what stands there and teaches
`git rm -r` of the path. The tests keep their links: a module's tests/constitution_layer_kit and the harness
files in its tests/ are symbolic links to the source, relative ones leading straight to it, never through
another link, so that they survive a clone into any directory, and the fixtures test the modules and the
shared code of one commit together. The tests, run by pytest, import from their own folder, which pytest puts
first on the import path, so they reach each package of the module's plugin/scripts/ through a link
tests/<package> -> ../plugin/scripts/<package>: they never edit their own import path, and never import a
copy that has drifted from what the gate runs.

The links a module owes are derived from the folders, never typed apart from them:
tests/constitution_layer_kit, each `.py` file at the top of shared/tests/ whose name starts with neither `.`
nor `_`, as tests/<name>, and each folder at the top of the module's plugin/scripts/, itself no link, that
holds an `__init__.py`, whose name starts with neither `.` nor `_`, save constitution_layer_kit, as
tests/<name>. The check is a failure to run (BROKEN) when shared/constitution_layer_kit/ is no directory or
when shared/tests/ lacks one of the four files shared/GATE.md names (the FLOOR), so that a list read from the
folders cannot shrink in silence. The modules are the folders of `kit_module_doc.module_folders`, the kit's
one listing — each folder under modules/ whose name starts with neither `.` nor `_` and holds its MODULE.md,
a folder without it a BROKEN whether it uses the shared code or not. A module owes the links when it has
plugin/hooks/hooks.json, when a line of a `.py` file under its plugin/scripts/, at any depth, begins, after
white space, with `from constitution_layer_kit` or `import constitution_layer_kit` (a folder
plugin/scripts/constitution_layer_kit is not entered; a comment, a string on one line, a shell script and a
`__pycache__` are no import, while such a line inside a string of several lines counts), or when it already
has one of the links. A module of skills alone owes none. Findings come by module, what stands at
plugin/scripts/constitution_layer_kit first, then the gate package in tests/, then the shared files by name,
then the module's own packages by name.

Modes:  no arguments   check every module under modules/;
        --self-test    prove the check on a throwaway tree: red for a link, a copy, a copy that is a
                       package, a plain file, a dangling link, a link leading elsewhere and an absolute link
                       at plugin/scripts/constitution_layer_kit, in a module with a hook and in one of
                       skills alone; red for a missing runner link to the gate package, a copy, a package
                       copy, a dangling, misdirected or absolute link, a text file left by a checkout
                       without symlink support, and a link through plugin/scripts/, and for a shared test
                       file no module links, in one module and in two; a missing, copied, misdirected,
                       dangling or absolute link to the module's own package, one through another link,
                       and a text file in its place; green for the right links, a `.`, `_`, README or
                       folder in shared/tests/ no one owes, a folder of plugin/scripts/ that is no
                       package, and the imports read over their cases;
                       a folder `.x` or `_x` skipped, a plain file of modules/ and a name without
                       `const-` by the listing's rule; BROKEN for a missing gate package or a
                       missing floor file, a folder without its MODULE.md and no modules/.
Exit:   0 green; 2 a link is wrong or a plugin holds shared code; 1 the check could not run.
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
PLUGIN_PATH = "plugin/scripts/constitution_layer_kit"  # where a plugin holds nothing
RUNNER_GATE_LINK = (
    "tests/constitution_layer_kit",
    "shared/constitution_layer_kit",
)  # the gate package, for the fixture runner: link in a module -> its source
FLOOR = ("harness.py", "consumer.py", "acceptance.py", "test_shared_items.py")  # those GATE.md item 7 names
IMPORT = re.compile(
    r"^\s*(from|import)\s+constitution_layer_kit\b"
)  # a line that imports the shared gate package
WHY = "the shared code has one source; a module that carries its own copy drifts from it silently"
PLUGIN_WHY = (
    "a plugin imports the package that pip installed for python3, and anything at this place would shadow"
    " it, since a script's folder comes first on Python's path"
)
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
    in the kit: the gate package for the runner, and each regular .py file at the top of shared/tests/
    whose name starts with neither . nor _. Broken when the gate package is no directory, or when
    shared/tests/ lacks a file of the floor, so a derived list cannot shrink in silence."""
    if not (kit / RUNNER_GATE_LINK[1]).is_dir():
        raise Broken(f"{RUNNER_GATE_LINK[1]}/ is no directory — fix: restore it from the kit's history")
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
    return dict([RUNNER_GATE_LINK, *((f"tests/{name}", f"shared/tests/{name}") for name in names)])


def own_links_of(kit: Path, module: Path) -> dict[str, str]:
    """The links the module's fixture runner owes to the module's own packages, link inside the module ->
    its package in the kit: each folder at the top of plugin/scripts/, itself no link, that holds an
    __init__.py, whose name starts with neither . nor _, save the shared constitution_layer_kit, which
    links_of() covers. own_packages reads <folder>/scripts/, so it is given the module's plugin/ folder."""
    base = module.relative_to(kit).as_posix()
    return {
        f"tests/{path.name}": f"{base}/plugin/scripts/{path.name}" for path in own_packages(module / "plugin")
    }


def imports_shared_code(module: Path) -> bool:
    """A line of a .py file under the module's plugin/scripts/, at any depth, imports
    constitution_layer_kit. A folder plugin/scripts/constitution_layer_kit is not entered, since a finding
    names it as it is, and a __pycache__ is not read."""
    scripts = module / "plugin" / "scripts"
    for folder, directories, files in os.walk(scripts):
        directories[:] = [
            each
            for each in directories
            if each != "__pycache__" and not (Path(folder) == scripts and each == "constitution_layer_kit")
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
    scan or a generator — or when it already has one of the links of its tests/. A module of skills alone
    owes none."""
    return (
        (module / "plugin" / "hooks" / "hooks.json").is_file()
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


def check_plugin_path(kit: Path, module: Path) -> Finding | None:
    """Anything at the module's plugin/scripts/constitution_layer_kit: a link, a directory, a plain file, a
    dangling link. A plugin holds no shared code, so the finding names what stands there and teaches its
    removal."""
    path = module / PLUGIN_PATH
    if not os.path.lexists(path):
        return None
    shown = path.relative_to(kit).as_posix()
    if path.is_symlink():
        found = f"a link to {os.readlink(path)}"
    else:
        found = "a directory" if path.is_dir() else "a plain file"
    return Finding(
        f"{shown} exists, {found}, in a plugin that holds no shared code",
        f"git rm -r {shown} (rm -r where it is not tracked)",
        PLUGIN_WHY,
    )


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
    findings: list[Finding] = []
    for module in folders:
        if (stray := check_plugin_path(kit, module)) is not None:
            findings.append(stray)
        findings += [
            finding
            for link, source, why in owed.get(module, [])
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
        "GREEN: no plugin holds the shared code, and every runner reaches it and the module's own packages"
        f" through a link to their one source — {counts}"
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


OWED = 1 + len(FLOOR)  # the links a module owes on a fresh tree: the runner's gate package, the floor


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


def module_of(link: Path) -> Path:
    """The module folder of the path modules/<m>/plugin/scripts/constitution_layer_kit, where a plugin holds
    nothing: the anchor every case is given, a path that stands empty on a fresh tree."""
    return link.parent.parent.parent


def root_of(link: Path) -> Path:
    return module_of(link).parent.parent


def add_module(root: Path, name: str) -> Path:
    module = root / "modules" / name
    (module / "plugin" / "hooks").mkdir(parents=True)
    (module / "plugin" / "scripts").mkdir()
    (module / "plugin" / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
    (module / "MODULE.md").write_text("A module.\n", encoding="utf-8")
    for link, source in links_of(root).items():
        (module / link).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(root / source, (module / link).parent), module / link)
    return module


def fresh_kit(root: Path) -> Path:
    """A kit with one module and every link it owes; returns the anchor, the path where its plugin holds
    nothing."""
    (root / "shared" / "constitution_layer_kit").mkdir(parents=True)
    (root / "shared" / "tests").mkdir()
    for name in FLOOR:
        (root / "shared" / "tests" / name).write_text("", encoding="utf-8")
    return add_module(root, "const-sample") / PLUGIN_PATH


def runner_link(anchor: Path) -> Path:
    """The runner's link to the gate package, tests/constitution_layer_kit of the anchor's module."""
    return module_of(anchor) / "tests" / "constitution_layer_kit"


def as_copy(link: Path) -> None:
    link.unlink()
    link.mkdir()


def as_package_copy(link: Path) -> None:
    """A real folder holding an __init__.py: a copy, and a package by its look."""
    as_copy(link)
    (link / "__init__.py").write_text("", encoding="utf-8")


def as_text_file(link: Path) -> None:
    link.unlink()
    link.write_text("../../../shared/constitution_layer_kit", encoding="utf-8")


def as_dangling(link: Path) -> None:
    link.unlink()
    os.symlink("../../../shared/no_such_gate", link)


def as_elsewhere(link: Path) -> None:
    link.unlink()
    os.symlink("../plugin", link)


def as_absolute(link: Path) -> None:
    target = link.resolve()
    link.unlink()
    os.symlink(target, link)


def as_missing(link: Path) -> None:
    link.unlink()


def on_runner(damage: Callable[[Path], None]) -> Callable[[Path], None]:
    """The damage done to the runner's link to the gate package."""
    return lambda anchor: damage(runner_link(anchor))


def stray_link(anchor: Path) -> None:
    """A link to the shared code where a plugin holds nothing: what every plugin had before the package."""
    os.symlink(os.path.relpath(root_of(anchor) / "shared" / "constitution_layer_kit", anchor.parent), anchor)


def stray_copy(anchor: Path) -> None:
    anchor.mkdir()


def stray_package_copy(anchor: Path) -> None:
    anchor.mkdir()
    (anchor / "__init__.py").write_text("", encoding="utf-8")


def stray_text_file(anchor: Path) -> None:
    anchor.write_text("../../../../shared/constitution_layer_kit", encoding="utf-8")


def stray_dangling(anchor: Path) -> None:
    os.symlink("../../../../shared/no_such_gate", anchor)


def stray_elsewhere(anchor: Path) -> None:
    os.symlink("../../tests", anchor)


def stray_absolute(anchor: Path) -> None:
    os.symlink(root_of(anchor) / "shared" / "constitution_layer_kit", anchor)


def skills_only_with_stray(anchor: Path) -> None:
    """A module of skills alone, owing no link, with a link to the shared code in its plugin/scripts/."""
    folder = root_of(anchor) / "modules" / "const-skills"
    (folder / "plugin" / "skills").mkdir(parents=True)
    (folder / "plugin" / "scripts").mkdir()
    (folder / "MODULE.md").write_text("A module.\n", encoding="utf-8")
    stray_link(folder / PLUGIN_PATH)


def harness_as_copy(link: Path) -> None:
    harness = module_of(link) / "tests" / "harness.py"
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
    (module_of(link) / "tests" / "new.py").write_text("", encoding="utf-8")


def hookless(path: str, text: str | bytes, keep: str | None = None) -> Callable[[Path], None]:
    """No hook; the links gone, bar the one kept; one script written at `path` under plugin/scripts/."""

    def damage(link: Path) -> None:
        module = module_of(link)
        if keep == "new.py":  # a shared file the module alone links
            new_shared(root_of(link))
            os.symlink("../../../shared/tests/new.py", module / "tests" / "new.py")
        (module / "plugin" / "hooks" / "hooks.json").unlink()
        (module / "plugin" / "hooks").rmdir()
        for each in links_of(root_of(link)):  # only the import or the kept link can make the module owe
            if each != f"tests/{keep}":
                (module / each).unlink()
        script = module / "plugin" / "scripts" / path
        script.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            script.write_bytes(text)
        else:
            script.write_text(text, encoding="utf-8")

    return damage


def beside_dangling_script(damage: Callable[[Path], None]) -> Callable[[Path], None]:
    """The damage, then a script plugin/scripts/x.py that is a dangling symbolic link."""

    def both(link: Path) -> None:
        damage(link)
        os.symlink("no_such_script.py", link.parent / "x.py")

    return both


def hidden_folders(link: Path) -> None:
    """Folders of modules/ that start with . or _ and hold a hook, with no link: no module."""
    for name in (".wip", "_draft"):
        (root_of(link) / "modules" / name / "plugin" / "hooks").mkdir(parents=True)
        (root_of(link) / "modules" / name / "plugin" / "hooks" / "hooks.json").write_text(
            "{}", encoding="utf-8"
        )


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
        (folder / "plugin" / "hooks").mkdir(parents=True)
        (folder / "plugin" / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
        if document:
            (folder / "MODULE.md").write_text("A module.\n", encoding="utf-8")

    return damage


def plain_file(link: Path) -> None:
    """A plain file of modules/ named like a module."""
    (root_of(link) / "modules" / "const-file").write_text("not a folder\n", encoding="utf-8")


def skills_only_without_document(link: Path) -> None:
    """A folder of skills alone, owing no link, with no MODULE.md."""
    (root_of(link) / "modules" / "const-skills" / "plugin" / "skills").mkdir(parents=True)


def modules_gone(link: Path) -> None:
    shutil.rmtree(root_of(link) / "modules")


def without_harness(link: Path) -> None:
    (root_of(link) / "shared" / "tests" / "harness.py").unlink()


def without_gate(link: Path) -> None:
    shutil.rmtree(root_of(link) / "shared" / "constitution_layer_kit")


def tests_emptied(link: Path) -> None:
    for name in FLOOR:
        (root_of(link) / "shared" / "tests" / name).unlink()


def tests_gone(link: Path) -> None:
    tests = root_of(link) / "shared" / "tests"
    for name in FLOOR:
        (tests / name).unlink()
    tests.rmdir()


def own_package(name: str = "sample_gate", linked: str | None = None) -> Callable[[Path], None]:
    """A package plugin/scripts/<name>/ of the module's own, its link in tests/ made to `linked` or none."""

    def damage(link: Path) -> None:
        module = module_of(link)
        (link.parent / name).mkdir()
        (link.parent / name / "__init__.py").write_text("", encoding="utf-8")
        if linked is not None:
            os.symlink(linked, module / "tests" / name)

    return damage


def runner_gate_through_scripts(link: Path) -> None:
    """A link to the shared code where a plugin holds nothing, and tests/constitution_layer_kit made a link to
    it: the runner's link resolves to the source, not straight, and the plugin's path is a finding of its
    own."""
    stray_link(link)
    runner_link(link).unlink()
    os.symlink("../plugin/scripts/constitution_layer_kit", runner_link(link))


def own_package_as_text(link: Path) -> None:
    """The module's own package, its link in tests/ a one-line text file, as a checkout without links."""
    own_package()(link)
    (module_of(link) / "tests" / "sample_gate").write_text("../plugin/scripts/sample_gate", encoding="utf-8")


def own_package_through_alias(link: Path) -> None:
    """The module's own package reached from tests/ through a second link in plugin/scripts/."""
    own_package()(link)
    os.symlink("sample_gate", link.parent / "alias")
    os.symlink("../plugin/scripts/alias", module_of(link) / "tests" / "sample_gate")


def own_package_copied(link: Path) -> None:
    """The module's own package, copied into tests/ instead of linked."""
    own_package()(link)
    shutil.copytree(link.parent / "sample_gate", module_of(link) / "tests" / "sample_gate")


def not_packages(link: Path) -> None:
    """Folders of plugin/scripts/ that are no package of the module's own: no __init__.py, a `.` or `_`
    name, and a link to a package of the shared code."""
    scripts = link.parent
    (scripts / "data").mkdir()
    (scripts / "data" / "x.py").write_text("", encoding="utf-8")
    for name in ("__pycache__", "_private", ".mypy_cache"):
        (scripts / name).mkdir()
        (scripts / name / "__init__.py").write_text("", encoding="utf-8")
    (scripts / "single.py").write_text("", encoding="utf-8")
    shared_gate = root_of(link) / "shared" / "constitution_layer_kit"
    (shared_gate / "__init__.py").write_text("", encoding="utf-8")  # the shared package, a package
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
        "the runner's gate package link missing": (on_runner(as_missing), 1),
        "the module's own package with no link in tests/": (own_package(), 1),
        "the runner's gate package linked through plugin/scripts/constitution_layer_kit": (
            runner_gate_through_scripts,
            2,  # the runner's link, not straight; and what stands at the plugin's path
        ),
        "the module's own package copied into tests/": (own_package_copied, 1),
        "the module's own package linked through another link": (own_package_through_alias, 1),
        "the module's own package's link left a plain file in tests/": (own_package_as_text, 1),
        "the module's own package's link dangling": (own_package(linked="../plugin/scripts/no_such_gate"), 1),
        "the module's own package linked to the shared gate package": (
            own_package(linked="../../../shared/constitution_layer_kit"),
            1,
        ),
        "the module's own package by an absolute link": (
            lambda link: own_package(linked=str(link.parent / "sample_gate"))(link),
            1,
        ),
        "a copied harness in tests/": (harness_as_copy, 1),
        "a hookless module importing the shared code, its links missing": (
            hookless("generate.py", "from constitution_layer_kit import cli\n"),
            OWED,
        ),
        "a hookless module importing the shared code in plugin/scripts/lib/, its links missing": (
            hookless("lib/gen.py", "from constitution_layer_kit import cli\n"),
            OWED,
        ),
        "a hookless module with `import constitution_layer_kit` in plugin/scripts/x.py, its links missing": (
            hookless("x.py", "import constitution_layer_kit\n"),
            OWED,
        ),
        "a hookless module importing the shared code in plugin/scripts/lib/constitution_layer_kit/, its"
        " links missing": (
            hookless("lib/constitution_layer_kit/x.py", "from constitution_layer_kit import cli\n"),
            # only the folder at the top of plugin/scripts/ is the link; a nested one is read
            OWED,
        ),
        "a hookless module with a dangling plugin/scripts/x.py beside a script importing the shared code": (
            beside_dangling_script(hookless("y.py", "import constitution_layer_kit\n")),
            OWED,
        ),
        "a hookless module with non-UTF-8 bytes in a script before its import, its links missing": (
            hookless("x.py", b"# caf\xe9\nimport constitution_layer_kit\n"),
            OWED,
        ),
        "a hookless module with an indented import inside a function, its links missing": (
            hookless("lib/f.py", "def f() -> None:\n    from constitution_layer_kit import cli\n"),
            OWED,
        ),
        "a hookless module with an import line indented by a tab, its links missing": (
            hookless("lib/g.py", "def g() -> None:\n\tfrom constitution_layer_kit import cli\n"),
            OWED,
        ),
        "a hookless module with `import` and the name apart by a tab, its links missing": (
            hookless("lib/h.py", "import\tconstitution_layer_kit\n"),
            OWED,
        ),
        "a hookless module with `from constitution_layer_kit.cli import y`, its links missing": (
            hookless("y.py", "from constitution_layer_kit.cli import y\n"),
            OWED,
        ),
        "a hookless module that has only the link of a new shared file": (
            hookless("empty.txt", "", keep="new.py"),
            OWED,  # the gate package and the four of the floor, of the six links it owes
        ),
        "a hookless module that has only one link": (hookless("empty.txt", "", keep="consumer.py"), OWED - 1),
        "a shared test file no module links": (new_file_unlinked, 1),
        "a shared test file no one of two linking modules links": (new_file_in_two_modules, 2),
        "a folder named without const- that uses the shared code, its links missing": (
            unlinked_module("glossary"),
            OWED,  # the listing has no name rule: the folder owes the links like any module
        ),
        "a copy of the gate package in the runner's tests/": (on_runner(as_copy), 1),
        "a copy that is a package, owed once as the gate package and never as one of its own": (
            on_runner(as_package_copy),
            1,
        ),
        "a text file in the runner's place": (on_runner(as_text_file), 1),
        "a dangling link of the runner": (on_runner(as_dangling), 1),
        "a link of the runner leading elsewhere": (on_runner(as_elsewhere), 1),
        "an absolute link of the runner": (on_runner(as_absolute), 1),
        "a link to the shared code at plugin/scripts/constitution_layer_kit": (stray_link, 1),
        "a copy at plugin/scripts/constitution_layer_kit": (stray_copy, 1),
        "a copy that is a package at plugin/scripts/constitution_layer_kit": (stray_package_copy, 1),
        "a plain file at plugin/scripts/constitution_layer_kit": (stray_text_file, 1),
        "a dangling link at plugin/scripts/constitution_layer_kit": (stray_dangling, 1),
        "a link leading elsewhere at plugin/scripts/constitution_layer_kit": (stray_elsewhere, 1),
        "an absolute link at plugin/scripts/constitution_layer_kit": (stray_absolute, 1),
        "a link to the shared code in a module of skills alone": (skills_only_with_stray, 1),
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
            own_package(linked="../plugin/scripts/sample_gate"),
            EXIT_GREEN,
            ("GREEN:", "6 link(s) in 1 module(s) examined"),
        ),
        "the runner's gate package link missing, taught with its ln -s": (
            on_runner(as_missing),
            EXIT_RED,
            (
                "RED: modules/const-sample/tests/constitution_layer_kit is missing",
                f"why: {WHY}",
                "fix: from modules/const-sample/tests/ run:"
                " ln -s ../../../shared/constitution_layer_kit constitution_layer_kit",
                "RED: 1 finding(s) — 5 link(s) in 1 module(s) examined",
            ),
        ),
        "a link to the shared code in a plugin, taught with git rm": (
            stray_link,
            EXIT_RED,
            (
                "RED: modules/const-sample/plugin/scripts/constitution_layer_kit exists, a link to"
                " ../../../../shared/constitution_layer_kit, in a plugin that holds no shared code",
                f"why: {PLUGIN_WHY}",
                "fix: git rm -r modules/const-sample/plugin/scripts/constitution_layer_kit (rm -r where it"
                " is not tracked)",
                "RED: 1 finding(s) — 5 link(s) in 1 module(s) examined",
            ),
        ),
        "a copy in a plugin, named as a directory": (
            stray_package_copy,
            EXIT_RED,
            (
                "RED: modules/const-sample/plugin/scripts/constitution_layer_kit exists, a directory, in a"
                " plugin that holds no shared code",
                "RED: 1 finding(s) — 5 link(s) in 1 module(s) examined",
            ),
        ),
        "a plain file in a plugin, named as one": (
            stray_text_file,
            EXIT_RED,
            (
                "RED: modules/const-sample/plugin/scripts/constitution_layer_kit exists, a plain file, in a"
                " plugin that holds no shared code",
            ),
        ),
        "a dangling link in a plugin, named by its target": (
            stray_dangling,
            EXIT_RED,
            (
                "RED: modules/const-sample/plugin/scripts/constitution_layer_kit exists, a link to"
                " ../../../../shared/no_such_gate, in a plugin that holds no shared code",
            ),
        ),
        "a link in a module of skills alone, which owes no link": (
            skills_only_with_stray,
            EXIT_RED,
            (
                "RED: modules/const-skills/plugin/scripts/constitution_layer_kit exists, a link to",
                "RED: 1 finding(s) — 5 link(s) in 1 module(s) examined",
            ),
        ),
        "the module's own package missing in tests/, taught with its ln -s": (
            own_package(),
            EXIT_RED,
            (
                "RED: modules/const-sample/tests/sample_gate is missing",
                f"why: {OWN_WHY}",
                "fix: from modules/const-sample/tests/ run: ln -s ../plugin/scripts/sample_gate sample_gate",
                "RED: 1 finding(s) — 6 link(s) in 1 module(s) examined",
            ),
        ),
        "folders of plugin/scripts/ that are no package of the module's own owe nothing": (
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
        "a comment holding the word constitution_layer_kit owes nothing": (
            hookless("tool.py", "# constitution_layer_kit\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a commented-out import owes nothing": (
            hookless("tool.py", "# from constitution_layer_kit import cli\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a string holding the word constitution_layer_kit owes nothing": (
            hookless("tool.py", 'NAME = "constitution_layer_kit"\n'),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a name that only starts with constitution_layer_kit owes nothing": (
            hookless("tool.py", "import constitution_layer_kit_x\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "an import in a shell script owes nothing": (
            hookless("x.sh", "import constitution_layer_kit\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "an import in a __pycache__ owes nothing": (
            hookless("__pycache__/x.py", "import constitution_layer_kit\n"),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "a dangling plugin/scripts/x.py alone owes nothing": (
            beside_dangling_script(hookless("empty.txt", "")),
            EXIT_GREEN,
            ("GREEN:", "0 link(s) in 0 module(s) examined"),
        ),
        "an import inside plugin/scripts/constitution_layer_kit is not read, the folder is the finding": (
            hookless("constitution_layer_kit/x.py", "from constitution_layer_kit import cli\n"),
            EXIT_RED,
            (
                "RED: modules/const-sample/plugin/scripts/constitution_layer_kit exists, a directory, in a"
                " plugin that holds no shared code",
                "RED: 1 finding(s) — 0 link(s) in 0 module(s) examined",
            ),
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
        "shared/constitution_layer_kit/ removed": (
            without_gate,
            EXIT_BROKEN,
            (
                "BROKEN: shared/constitution_layer_kit/ is no directory — fix: restore it from the kit's"
                " history",
            ),
        ),
        "shared/tests/ emptied": (
            tests_emptied,
            EXIT_BROKEN,
            (
                "BROKEN: shared/tests/ lacks harness.py, consumer.py, acceptance.py, test_shared_items.py,"
                " which",
            ),
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
            (
                "BROKEN: shared/tests/ lacks harness.py, consumer.py, acceptance.py, test_shared_items.py,"
                " which",
            ),
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
    """The findings of two modules come by module, what stands at the plugin's path first, then the gate
    package, the files by name and the module's own packages by name."""
    # the order of the findings, held whole: no row of `reads` compares order, which asks the one list
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh_kit(root)
        shutil.rmtree(root / "modules" / "const-sample")
        for module in ("const-a", "const-b"):
            (root / "modules" / module / "plugin" / "hooks").mkdir(parents=True)
            (root / "modules" / module / "plugin" / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
            (root / "modules" / module / "MODULE.md").write_text("A module.\n", encoding="utf-8")
            for package in ("a_gate", "b_gate"):
                (root / "modules" / module / "plugin" / "scripts" / package).mkdir(parents=True)
                (root / "modules" / module / "plugin" / "scripts" / package / "__init__.py").write_text(
                    "", encoding="utf-8"
                )
            stray_link(root / "modules" / module / PLUGIN_PATH)
        out = io.StringIO()
        # modules/ and shared/tests/ are listed reversed, whatever the filesystem lists
        with contextlib.redirect_stdout(out), listed_in_reverse():
            code_after = run(root)
    heads = [line for line in out.getvalue().splitlines() if line.startswith("RED: modules/")]
    expected = [
        line
        for module in ("const-a", "const-b")
        for line in (
            f"RED: modules/{module}/plugin/scripts/constitution_layer_kit exists, a link to"
            " ../../../../shared/constitution_layer_kit, in a plugin that holds no shared code",
            *(
                f"RED: modules/{module}/{link} is missing"
                for link in (
                    "tests/constitution_layer_kit",
                    "tests/acceptance.py",
                    "tests/consumer.py",
                    "tests/harness.py",
                    "tests/test_shared_items.py",
                    "tests/a_gate",
                    "tests/b_gate",
                )
            ),
        )
    ]
    ok = code_after == EXIT_RED and heads == expected
    tally.judge(
        ok,
        "findings by module, what stands in plugin/scripts/ then the gate package in tests/,"
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
