#!/usr/bin/env python3
"""Kit check, never shipped in a module: the shared acceptance items hold for a gate of another layer.

The shared package serves gates of other kits' layers, whose dials file is not the constitution's: such a gate
names its own file and that file's kernel keys in its identity, and reads the policies from the constitution's
file in a scope of its own. The shared items, `constitution_layer_kit.testing.items`, are written once and run
by every module of this kit, all of which read the constitution's file alone. An item that quietly assumed
that single file would hold for every module and fail the first gate of a second layer, with no gate here to
show it. So the kit keeps a fixture gate of such a layer, `scripts/layered-fixture/`, namespace
`know-check`, its namespace and its layer's keys in `layer.yaml` and its policies in `constitution.yaml`, and
this check runs the shared items against it: they all hold, or each failing item is named with the failure it
met.

The fixture is kit tooling, not a module: it stands under `scripts/`, in no marketplace, no settings, no
coverage pair and no install guide. The check copies it into a throwaway folder, the link of its `tests/` to
the shared package recreated to reach this tree's `shared/constitution_layer_kit`, and runs pytest there on
`tests/`, with `-W error` as a module's fixtures run, and with `-n <value>` when CONSTITUTION_KIT_JOBS names
one.

Modes:  no arguments   run the fixture's tests against this tree's shared package; GREEN with the number of
                       items run and skipped (an item the fixture's Subject leaves out is skipped, its reason
                       naming the flag), or RED with pytest's own output and the fix;
        --self-test    prove the check: green on the real fixture; red on a copy of the shared package, in a
                       throwaway folder and never in the tree, whose `identity.reading` no longer shadows the
                       file, and on another whose `load_kernel_part` refuses the reader as `C5.12`; BROKEN for
                       a missing pytest, a missing fixture, a missing package and tests pytest cannot collect.
Exit:   0 green; 2 a shared item fails for the fixture; 1 the check could not run (pytest or PyYAML missing,
        the fixture or the shared package gone, pytest unable to collect or to finish, its summary unread).
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
FIXTURE = Path("scripts", "layered-fixture")
PACKAGE = Path("shared", "constitution_layer_kit")
WORKFLOW = KIT / ".github" / "workflows" / "gates.yml"
JOBS_ENV = "CONSTITUTION_KIT_JOBS"  # pytest-xdist workers, a number or `auto`; empty or unset: one process
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
PYTEST_RED = 1  # pytest's exit when a test failed; 0 is green, and every other exit could not run
RUNNER_TIMEOUT = 540.0  # seconds one pytest run may take: under the ten minutes a foreground command gets
WHAT = "the shared acceptance items do not all hold for a gate of another layer"
WHY = (
    "an item that reads only this kit's single dials file holds for every module here and fails the first"
    " gate of a second layer, with no gate in the kit to show it"
)
FIX = (
    "read the failing items above: an item that names the gate's file, its kernel keys or its prefix takes"
    " them from the identity the session declares, in shared/constitution_layer_kit/testing/items.py, and a"
    " failure of the fixture gate itself is fixed in scripts/layered-fixture/"
)
SUMMARY = re.compile(r"(\d+) (passed|failed|skipped|errors?)")


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Counts:
    run: int
    failed: int
    skipped: int


@dataclass(frozen=True)
class Verdict:
    code: int
    counts: Counts
    output: str  # pytest's own output, as it printed it


Have = Callable[[str], bool]  # whether a package is installed for this interpreter


def installed(package: str) -> bool:
    return importlib.util.find_spec(package) is not None


def pins(*names: str) -> str:
    """The install command of the named packages at the versions the kit's CI pins, read from the workflow,
    which alone names them."""
    try:
        text = WORKFLOW.read_text(encoding="utf-8")
    except OSError:
        text = ""
    wanted = []
    for name in names:
        found = re.search(rf'"{re.escape(name)}==([^"\s]+)"', text)
        wanted.append(f'"{name}=={found[1]}"' if found else name)
    return f"{sys.executable} -m pip install {' '.join(wanted)}"


def counts_of(text: str) -> Counts:
    """The numbers of pytest's summary line, the last line of its quiet output."""
    lines = [line for line in text.splitlines() if line.strip()]
    found = {kind: int(number) for number, kind in SUMMARY.findall(lines[-1] if lines else "")}
    if not found:
        raise Broken(
            f"pytest's summary line was not read ({lines[-1] if lines else 'no output'!r}) — fix: run"
            f" python3 -m pytest {FIXTURE.as_posix()}/tests -W error and read its last line"
        )
    failed = found.get("failed", 0) + found.get("error", 0) + found.get("errors", 0)
    return Counts(found.get("passed", 0) + failed, failed, found.get("skipped", 0))


def copy_fixture(source: Path, package: Path, into: Path) -> Path:
    """The fixture in `into`, its tests' link to the shared package pointing at `package`: the links of the
    tree are relative to the kit's own folders, so the one to the package is made again, and the one to the
    gate's own package, relative inside the fixture, is kept as it is."""
    where = into / "layered-fixture"
    shutil.copytree(
        source,
        where,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            "__pycache__", ".mypy_cache", ".pytest_cache", "constitution_layer_kit"
        ),
    )
    (where / "tests" / "constitution_layer_kit").symlink_to(package.resolve())
    return where


def run_pytest(where: Path, arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests",
                "-p",
                "no:cacheprovider",
                "-W",
                "error",
                "-q",
                *arguments,
            ],
            cwd=where,
            capture_output=True,
            text=True,
            timeout=RUNNER_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise Broken(
            f"pytest did not end in {RUNNER_TIMEOUT:g} s — fix: run python3 -m pytest"
            f" {FIXTURE.as_posix()}/tests -W error and find the item that waits"
        ) from None


def last_words(done: subprocess.CompletedProcess[str]) -> str:
    lines = [line for line in (done.stdout + done.stderr).splitlines() if line.strip()]
    return lines[-1].strip() if lines else "no output"


def examine(source: Path, package: Path, have: Have = installed, stop_early: bool = False) -> Verdict:
    """The fixture's tests against `package`, in a throwaway copy of the fixture. `stop_early` ends the run at
    the first failed item, for a proof that only needs to see one."""
    jobs = os.environ.get(JOBS_ENV, "").strip()
    needed = {"pytest": "pytest", "yaml": "PyYAML", **({"xdist": "pytest-xdist"} if jobs else {})}
    missing = [name for module, name in needed.items() if not have(module)]
    if missing:
        raise Broken(
            f"{' and '.join(missing)} not installed for {sys.executable}, and the shared items run under"
            f" pytest against a gate that reads YAML — fix: {pins(*missing)}"
        )
    if not (source / "tests").is_dir() or not (source / "plugin" / "scripts").is_dir():
        raise Broken(
            f"{FIXTURE.as_posix()} is gone or incomplete: it holds no tests/ or no plugin/scripts/ — fix:"
            f" restore it, git restore {FIXTURE.as_posix()}"
        )
    if not (package / "__init__.py").is_file():
        raise Broken(
            f"{PACKAGE.as_posix()} is gone: it holds no __init__.py — fix: restore it, git restore"
            f" {PACKAGE.as_posix()}"
        )
    with tempfile.TemporaryDirectory(prefix="layered-items-") as scratch:
        where = copy_fixture(source, package, Path(scratch))
        collected = run_pytest(where, ["--collect-only"])
        if collected.returncode != 0:
            raise Broken(
                f"pytest could not collect the tests of {FIXTURE.as_posix()} (exit {collected.returncode}):"
                f" {last_words(collected)} — fix: run python3 -m pytest {FIXTURE.as_posix()}/tests -W error"
                " --collect-only and repair what it names"
            )
        done = run_pytest(where, [*(["-x"] if stop_early else []), *(["-n", jobs] if jobs else [])])
    if done.returncode not in (EXIT_GREEN, PYTEST_RED):
        raise Broken(
            f"pytest exited {done.returncode} on the tests of {FIXTURE.as_posix()}: {last_words(done)} — fix:"
            f" run python3 -m pytest {FIXTURE.as_posix()}/tests -W error and repair what it names"
        )
    counts = counts_of(done.stdout)
    if (done.returncode == EXIT_GREEN) != (counts.failed == 0) or counts.run == 0:
        raise Broken(
            f"pytest exited {done.returncode} against its own summary ({last_words(done)}) — fix: run"
            f" python3 -m pytest {FIXTURE.as_posix()}/tests -W error"
        )
    return Verdict(done.returncode, counts, done.stdout + done.stderr)


def report(verdict: Verdict) -> int:
    counts = verdict.counts
    if verdict.code == EXIT_GREEN:
        print(
            "GREEN: every shared acceptance item holds for a gate of another layer —"
            f" {counts.run} item(s) run, {counts.skipped} skipped ({FIXTURE.as_posix()})"
        )
        return EXIT_GREEN
    print(verdict.output.rstrip())
    print(
        f"RED: {WHAT} — {counts.failed} failed, {counts.run - counts.failed} passed,"
        f" {counts.skipped} skipped ({FIXTURE.as_posix()})"
    )
    print(f"  why: {WHY}")
    print(f"  fix: {FIX}")
    return EXIT_RED


def broken(message: str) -> int:
    print(f"BROKEN: {message}")
    print("BROKEN: the check could not run — 0 items examined")
    return EXIT_BROKEN


def mutated(into: Path, name: str, old: str, new: str) -> Path:
    """A copy of the shared package in `into`, one file of it changed: `old` is written `new`. The tree is
    never touched. A change that no longer finds its text is the self-test's own defect, not a pass."""
    package = into / "shared" / "constitution_layer_kit"
    shutil.copytree(KIT / PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
    source = package / name
    text = source.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise Broken(
            f"the self-test's change of {PACKAGE.as_posix()}/{name} finds its text {text.count(old)} times,"
            " not once — fix: update the change in scripts/check-layered-items.py to the file's present text"
        )
    source.write_text(text.replace(old, new), encoding="utf-8")
    return package


SHADOW = "    shadow = replace(outer.identity, dials_file=dials_file, kernel_keys=kernel_keys)\n"
PREFIX_FORM = (
    "    value = raw.get(PREFIX_KEY)\n"
    "    if not isinstance(value, str) or not _PREFIX_SHAPE.fullmatch(value):\n"
    "        raise ConfigurationFailure(messages.c5_prefix_invalid_kernel_part())\n"
)
# The changes the self-test makes to a copy of the shared package, each one a way the shared code could come
# to serve this kit's modules and fail a gate of another layer: the scope that shadows no file, and the
# reader of the constitution part that holds the file's prefix to the reading gate's namespace.
MUTATIONS = {
    "identity.reading no longer shadows the file": (
        "identity.py",
        SHADOW,
        "    shadow = outer.identity\n",
    ),
    "load_kernel_part refuses the reader as C5.12": (
        "dials.py",
        PREFIX_FORM,
        "    value = _module_prefix(raw.get(PREFIX_KEY))\n",
    ),
}


def run_captured(
    source: Path, package: Path, have: Have = installed, stop_early: bool = False
) -> tuple[int, str]:
    """The check's exit code and everything it printed, for a case to read."""
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        try:
            code = report(examine(source, package, have, stop_early))
        except Broken as bad:
            code = broken(str(bad))
    return code, printed.getvalue()


def self_test() -> int:
    """Red→green on throwaway copies: each case's exit and its literal lines, typed by hand."""
    source, package = KIT / FIXTURE, KIT / PACKAGE
    green = re.compile(
        r"GREEN: every shared acceptance item holds for a gate of another layer — [1-9][0-9]* item\(s\) run,"
        r" [0-9]+ skipped \(scripts/layered-fixture\)"
    )
    cases: list[tuple[str, bool]] = []
    code, said = run_captured(source, package)
    cases.append(
        (
            "the fixture gate is green against the shared package",
            code == EXIT_GREEN and bool(green.fullmatch(said.strip())),
        )
    )
    for name, (file, old, new) in MUTATIONS.items():
        with tempfile.TemporaryDirectory(prefix="layered-items-self-") as scratch:
            code, said = run_captured(source, mutated(Path(scratch), file, old, new), stop_early=True)
        lines = said.splitlines()
        red = [line for line in lines if line.startswith(f"RED: {WHAT} — 1 failed, ")]
        ok = (
            code == EXIT_RED
            and len(red) == 1
            and lines[-3] == red[0]
            and lines[-2:]
            == [
                f"  why: {WHY}",
                f"  fix: {FIX}",
            ]
        )
        cases.append((f"{name}: red, pytest's own output first, the fix last", ok and "FAILED" in said))
    with tempfile.TemporaryDirectory(prefix="layered-items-self-") as scratch:
        cases += broken_cases(source, package, Path(scratch))
    for name, ok in cases:
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    failed = sum(not ok for _, ok in cases)
    print(f"{len(cases) - failed}/{len(cases)} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def broken_cases(source: Path, package: Path, scratch: Path) -> list[tuple[str, bool]]:
    """The runs that could not run, each exit 1 with its line first and the closing line after it: pytest not
    installed, the fixture gone, the shared package gone, and tests pytest cannot collect."""
    closing = "BROKEN: the check could not run — 0 items examined"
    cases: list[tuple[str, bool]] = []

    def said(
        name: str, first: str, source: Path = source, package: Path = package, have: Have = installed
    ) -> None:
        code, text = run_captured(source, package, have)
        lines = text.splitlines()
        cases.append(
            (
                f"{name} is BROKEN, never a pass",
                code == EXIT_BROKEN
                and len(lines) == 2
                and lines[1] == closing
                and lines[0].startswith(first),
            )
        )

    said(
        "pytest not installed",
        f"BROKEN: pytest not installed for {sys.executable}",
        have=lambda name: name != "pytest",
    )
    said(
        "the fixture folder gone",
        "BROKEN: scripts/layered-fixture is gone or incomplete",
        source=scratch / "nothing",
    )
    said(
        "the shared package gone",
        "BROKEN: shared/constitution_layer_kit is gone",
        package=scratch / "nothing",
    )
    unreadable = scratch / "unreadable"
    shutil.copytree(
        source, unreadable, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", ".mypy_cache")
    )
    (unreadable / "tests" / "test_layered.py").write_text("def (\n", encoding="utf-8")
    said(
        "tests pytest cannot collect",
        "BROKEN: pytest could not collect the tests of scripts/layered-fixture",
        source=unreadable,
    )
    return cases


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-layered-items", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return broken("misinvocation — fix: run with no arguments, or with --self-test")
    try:
        if args.self_test:
            return self_test()
        return report(examine(KIT / FIXTURE, KIT / PACKAGE))
    except Broken as bad:
        return broken(str(bad))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
