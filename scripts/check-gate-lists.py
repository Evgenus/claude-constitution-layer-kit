#!/usr/bin/env python3
"""Kit check: every scan a module declares stands in the kit's gate list, in its CI list and in its
module's job, and the list's modules are exactly the module folders.

A module declares its scan in its document's enforcement section (template §9): a code span in a
row of that section that reads exactly `<entry> --scan`, or `<entry>.py --scan` — nothing after
the flag, so an explain mode (`--scan --command …`) or a report (`--scan --since …`) is no tree
scan. For each declared scan:
  - the gate list, the entries `sh scripts/gate-list.sh --names gate` prints, has one whose
    commands (`--show <entry>`) run `modules/<module>/scripts/<entry>.sh --scan` or `….py --scan`;
  - one such entry stands in the module's own job, the entries `--names <module>` prints for a job
    `--json` names, never in `kit` or another module's job, where a red would name no module or the
    wrong one;
  - the CI list is every entry of that script, when the lines of `.github/workflows/gates.yml`,
    comments aside — a whole comment line, or a `#` after a space or a tab — call
    `sh scripts/gate-list.sh --json` and `sh scripts/gate-list.sh --run`; a workflow that does not
    leaves every declared scan out of CI. That the matrix is built from the one and runs the other
    is the workflow's own text, held by review and by its run; that each entry falls in one of the
    jobs `--json` prints is the list script's own, its jobs read from its entries, not this check's.
Every folder under `modules/` whose name opens with neither a dot nor an underscore is a module
and must hold its `MODULE.md`. A module that declares no scan is examined and needs no scan entry.
The list's modules, its `MODULES`, are read from its entries `install-<module>`, `fixtures-<module>`,
`lint-<module>` and `types-<module>` in `--names all`: each module folder has all four, and no
module that has one lacks its folder (decisions dec-0056-portability-grep-and-gate-lists,
dec-0058-ci-runs-each-check-in-parallel and dec-0061-ci-runs-one-job-per-module).

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree: a scan missing from the gate list, or
                       from a workflow that does not read the list, red; a scan in both green; an
                       extra entry no gate; a span with more after the flag no scan; a scan whose
                       entry falls into `kit` or another module's job red; a module folder the list
                       leaves out, and a listed module with no folder, red; the report of each kind
                       of finding as literal lines with exit 2; a list that cannot be read, jobs
                       that are no JSON list, a module document without its enforcement anchor and
                       a module folder without its document, each a BROKEN line; a `.py` scan held
                       by its python3 line and taught by it.
Exit:   0 green; 2 a finding; 1 the check could not run.
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
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
GATE_LIST = "scripts/gate-list.sh"
WORKFLOW = ".github/workflows/gates.yml"
READS_LIST = ("sh scripts/gate-list.sh --json", "sh scripts/gate-list.sh --run")
DECLARED = re.compile(r"`([a-z][a-z0-9-]*?(?:\.py)?) --scan`")
KINDS = ("install", "fixtures", "lint", "types")  # the entries the list gives each of its MODULES
OF_MODULE = re.compile(rf"({'|'.join(KINDS)})-(.+)")
WHY = "a scan the kit does not run holds nothing, and the lists are where the kit says what it runs"
WHY_JOB = (
    "a module's scan runs in that module's job, so a red CI line names the module whose rule the tree broke"
)
WHY_MISSING = "a module the list leaves out is never installed, run, linted or typed in CI"
WHY_STRAY = (
    "the list's modules are exactly the module folders, and an entry of a missing module checks nothing"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


class Where(StrEnum):
    GATE = "gate list"
    CI = "CI list"
    JOB = "module's job"
    MISSING = "list's modules"
    STRAY = "module folders"


@dataclass(frozen=True)
class Finding:
    module: str
    where: Where
    entry: str = ""  # the declared scan, `<entry>` or `<entry>.py`
    runner: str = ""  # the list's entry that runs the scan
    job: str = ""  # the job that entry stands in, empty for none
    names: tuple[str, ...] = field(default=())  # the list's entries of a module

    def render(self) -> str:
        spans = ", ".join(f"`{name}`" for name in self.names)
        if self.where is Where.GATE:
            run = (
                f"python3 modules/{self.module}/scripts/{self.entry} --scan"
                if self.entry.endswith(".py")
                else f"sh modules/{self.module}/scripts/{self.entry}.sh --scan"
            )
            what = f"its scan `{self.entry} --scan` is not in the {self.where}"
            why, fix = WHY, f"add an entry to the gate group of {GATE_LIST} that runs `{run}`"
        elif self.where is Where.CI:
            what = f"its scan `{self.entry} --scan` is not in the {self.where}"
            why = WHY
            fix = (
                f"let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
                f" `{READS_LIST[1]} <job>`"
            )
        elif self.where is Where.JOB:
            held = f"the CI job `{self.job}`" if self.job else "no CI job"
            what = (
                f"its scan `{self.entry} --scan`, the entry `{self.runner}`, runs in {held}, not in its own"
            )
            why = WHY_JOB
            fix = (
                f"map the entry to its module in job() of {GATE_LIST}: `{self.runner}) echo {self.module} ;;`"
            )
        elif self.where is Where.MISSING:
            what = f"the list lacks its entries {spans}"
            why = WHY_MISSING
            fix = (
                f"add `{self.module}` to MODULES in {GATE_LIST}, which gives each module its install,"
                " fixtures, lint and types entries"
            )
        else:
            what = f"the list has its entries {spans}, but modules/{self.module} is no module folder"
            why = WHY_STRAY
            fix = (
                f"remove `{self.module}` from MODULES in {GATE_LIST}, or restore modules/{self.module}"
                " with its MODULE.md"
            )
        return f"RED: {self.module}: {what}\n  why: {why}\n  fix: {fix}"


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


def declared_scans(text: str, path: str = "the module document") -> list[str]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == '<a id="t9"></a>'), None)
    if start is None:
        raise Broken(f"{path} has no enforcement section, anchor t9 — fix: restore the anchor")
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() == '<a id="t10"></a>'), len(lines)
    )
    rows = [line for line in lines[start:end] if line.startswith("| E")]
    return sorted({m[1] for row in rows for m in DECLARED.finditer(row)})


def listed(root: Path, *args: str) -> str:
    """What `sh scripts/gate-list.sh <args>` prints, run from `root`."""
    try:
        done = subprocess.run(["sh", GATE_LIST, *args], cwd=root, capture_output=True, text=True, check=False)
    except OSError as bad:
        raise Broken(f"{GATE_LIST} cannot be run ({bad.strerror}) — fix: install a POSIX sh") from bad
    if done.returncode != 0:
        said = (done.stderr or done.stdout).strip().splitlines()
        raise Broken(
            f"{GATE_LIST} {' '.join(args)} exited {done.returncode}"
            f" ({said[-1] if said else 'no output'}) — fix: restore the list script"
        )
    return done.stdout


def gate_list(root: Path) -> dict[str, str]:
    """Each entry of the gate group, with its commands."""
    return {name: listed(root, "--show", name) for name in listed(root, "--names", "gate").split()}


def jobs_of(root: Path) -> dict[str, str]:
    """Each entry of the list, with the job `--json` and `--names <job>` put it in."""
    try:
        jobs = json.loads(listed(root, "--json"))
    except json.JSONDecodeError as bad:
        raise Broken(
            f"{GATE_LIST} --json printed no JSON ({bad.msg}) — fix: restore the list script"
        ) from bad
    if not isinstance(jobs, list) or not all(isinstance(job, str) for job in jobs):
        raise Broken(f"{GATE_LIST} --json printed no list of job names — fix: restore the list script")
    return {entry: job for job in jobs for entry in listed(root, "--names", job).split()}


def ci_reads_list(root: Path) -> bool:
    if not (root / WORKFLOW).is_file():
        return False
    steps = "\n".join(
        re.split(r"\s#", line, maxsplit=1)[0]
        for line in read(root, WORKFLOW).splitlines()
        if not line.lstrip().startswith("#")
    )
    return all(phrase in steps for phrase in READS_LIST)


def check_scan(
    module: str, entry: str, gates: dict[str, str], jobs: dict[str, str], ci: bool
) -> list[Finding]:
    stem = re.escape(entry.removesuffix(".py"))
    runs = re.compile(rf"modules/{re.escape(module)}/scripts/{stem}\.(?:sh|py) --scan\b")
    runners = [name for name, commands in gates.items() if runs.search(commands)]
    findings: list[Finding] = []
    if not runners:
        findings.append(Finding(module, Where.GATE, entry))
    elif all(jobs.get(name) != module for name in runners):
        findings.append(Finding(module, Where.JOB, entry, runners[0], jobs.get(runners[0], "")))
    if not ci:
        findings.append(Finding(module, Where.CI, entry))
    return findings


def check_modules(modules: list[str], entries: list[str]) -> list[Finding]:
    """The list's modules, read from its entries of each kind, against the module folders."""
    named: dict[str, list[str]] = {}
    for entry in entries:
        if (match := OF_MODULE.fullmatch(entry)) is not None:
            named.setdefault(match[2], []).append(entry)
    findings: list[Finding] = []
    for module in modules:
        lacking = tuple(f"{kind}-{module}" for kind in KINDS if f"{kind}-{module}" not in entries)
        if lacking:
            findings.append(Finding(module, Where.MISSING, names=lacking))
    for module in sorted(set(named) - set(modules)):
        findings.append(Finding(module, Where.STRAY, names=tuple(named[module])))
    return findings


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    base = root / "modules"
    if not base.is_dir():
        raise Broken(f"{root} has no modules/ directory — fix: run the check from a checkout of the kit")
    gates, jobs, ci = gate_list(root), jobs_of(root), ci_reads_list(root)
    findings: list[Finding] = []
    directories = sorted(d for d in base.iterdir() if d.is_dir() and not d.name.startswith((".", "_")))
    for directory in directories:
        if not (directory / "MODULE.md").is_file():
            raise Broken(f"modules/{directory.name} has no MODULE.md — fix: restore the module document")
    modules = [d.name for d in directories]
    scans = 0
    for module in modules:
        document = f"modules/{module}/MODULE.md"
        for entry in declared_scans(read(root, document), document):
            scans += 1
            findings += check_scan(module, entry, gates, jobs, ci)
    findings += check_modules(modules, listed(root, "--names", "all").split())
    return findings, len(modules), scans


def report(findings: list[Finding], modules: int, scans: int) -> int:
    counts = f"{modules} module document(s) examined, {scans} declared scan(s)"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job, and the"
        f" list's modules are the module folders — {counts}"
    )
    return EXIT_GREEN


@dataclass(frozen=True)
class Case:
    """One self-test tree: the gate and extra entries with their commands, the workflow, the job of
    each entry that is not `kit` beyond the module entries' own, the folders and the listed modules."""

    gates: dict[str, str]
    extras: dict[str, str] = field(default_factory=dict)
    workflow: str = ""
    jobs: dict[str, str] = field(default_factory=dict)
    folders: tuple[str, ...] = ("const-x", "const-quiet")
    listed: tuple[str, ...] | None = None  # the list's MODULES; None: the folders


def self_test() -> int:
    """Red→green on a throwaway tree: a scan missing from the gate group, and one in a kit whose
    workflow does not read the list or names it only in a comment line or a trailing comment, are red
    with one finding each and green once listed and read;
    an extra entry is no gate; a span with more after the flag is no scan; a module with no scan
    needs no entry; a scan whose entry falls into `kit` or into another module's job is red; a module
    folder the list's modules leave out, and a listed module with no folder, are red; the report of
    each kind of finding is its literal text with exit 2; a list script that fails, jobs that are no
    JSON list, a module document without its enforcement anchor and a module folder without its
    document are each a teaching BROKEN line; a scan declared as `<entry>.py --scan` is held by its
    python3 line and taught by it."""
    module_text = (
        '<a id="t9"></a>\n## 9\n\n| # | artifact | kind |\n|---|---|---|\n'
        "| E1 | hook + `check-x` (hook mode) | `gate` |\n| E2 | `check-x --scan`: all | `gate` |\n"
        "| E3 | `check-x --scan --since <date>` | `advisory` |\n\n"
        "A sibling's `check-y --scan` is not this module's.\n\n<a id=\"t10\"></a>\n"
    )
    quiet_text = '<a id="t9"></a>\n| E1 | `explain --scan --command <text>` | `gate` |\n<a id="t10"></a>\n'
    scan = "sh modules/const-x/scripts/check-x.sh --scan"
    reads = f'jobs:\n  list:\n    run: {READS_LIST[0]}\n  check:\n    run: {READS_LIST[1]} "$JOB"\n'
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` is not in the CI list",
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs",
        f"  fix: let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
        f" `{READS_LIST[1]} <job>`",
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s)",
    ]
    placed_lines = [
        "RED: const-x: its scan `check-x --scan`, the entry `x`, runs in the CI job `kit`, not in its own",
        "  why: a module's scan runs in that module's job, so a red CI line names the module whose rule"
        " the tree broke",
        "  fix: map the entry to its module in job() of scripts/gate-list.sh: `x) echo const-x ;;`",
        "RED: const-quiet: the list lacks its entries `install-const-quiet`, `fixtures-const-quiet`,"
        " `lint-const-quiet`, `types-const-quiet`",
        "  why: a module the list leaves out is never installed, run, linted or typed in CI",
        "  fix: add `const-quiet` to MODULES in scripts/gate-list.sh, which gives each module its install,"
        " fixtures, lint and types entries",
        "RED: const-gone: the list has its entries `install-const-gone`, `fixtures-const-gone`,"
        " `lint-const-gone`, `types-const-gone`, but modules/const-gone is no module folder",
        "  why: the list's modules are exactly the module folders, and an entry of a missing module checks"
        " nothing",
        "  fix: remove `const-gone` from MODULES in scripts/gate-list.sh, or restore modules/const-gone"
        " with its MODULE.md",
        "RED: 3 finding(s) — 2 module document(s) examined, 1 declared scan(s)",
    ]

    def script(case: Case) -> str:
        """A stand-in for the list script: `--names gate|all|<job>`, `--json` and `--show <entry>`."""
        own = {
            f"{kind}-{m}": m for m in (case.folders if case.listed is None else case.listed) for kind in KINDS
        }
        extras = {**case.extras, **dict.fromkeys(own, "true")}
        jobs = {**{name: "kit" for name in {**case.gates, **extras}}, "x": "const-x", **own, **case.jobs}
        names = {"gate": list(case.gates), "all": [*case.gates, *extras]}
        for name, job in jobs.items():
            names.setdefault(job, []).append(name)
        groups = "".join(f"            {key}) set -- {' '.join(value)} ;;\n" for key, value in names.items())
        arms = "".join(
            f"            {name}) echo '{cmd}' ;;\n" for name, cmd in {**case.gates, **extras}.items()
        )
        listing = json.dumps(sorted(set(jobs.values())))
        return (
            '#!/bin/sh\ncase "$1" in\n'
            f'    --names) case "$2" in\n{groups}            *) exit 1 ;;\n        esac\n'
            '        for n in "$@"; do echo "$n"; done ;;\n'
            f"    --json) echo '{listing}' ;;\n"
            f'    --show) case "$2" in\n{arms}            *) exit 1 ;;\n        esac ;;\n'
            "    *) exit 1 ;;\nesac\n"
        )

    def build(root: Path, case: Case) -> None:
        documents = {"const-x": module_text, "const-quiet": quiet_text}
        for path, text in (
            *((f"modules/{m}/MODULE.md", documents.get(m, quiet_text)) for m in case.folders),
            (GATE_LIST, script(case)),
            (WORKFLOW, case.workflow or reads),
        ):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")

    def findings_of(case: Case) -> list[Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            return check_kit(root)[0]

    trailing = f"\t# {READS_LIST[1]}\n"
    failed = 0
    cases: dict[str, tuple[Case, list[Where]]] = {
        "a gate runs the scan in its module's job, CI reads the list, a module with none needs none": (
            Case({"x": scan}),
            [],
        ),
        "the gate group lacks it (an extra entry does not count)": (
            Case({"other": "python3 scripts/other.py"}, {"extra": scan}),
            [Where.GATE],
        ),
        "the workflow names --json only in a comment line": (
            Case({"x": scan}, workflow=f"# {READS_LIST[0]}\njobs:\n  one:\n    run: {READS_LIST[1]} x\n"),
            [Where.CI],
        ),
        "the workflow names --run only in a trailing comment": (
            Case(
                {"x": scan},
                workflow=f"jobs:\n  one:\n    run: {READS_LIST[0]}\n  two:\n    run: make{trailing}",
            ),
            [Where.CI],
        ),
        "the workflow does not read the list": (
            Case({"x": scan}, workflow="jobs:\n  one:\n    run: make\n"),
            [Where.CI],
        ),
        "the scan's entry falls into `kit`": (Case({"x": scan}, jobs={"x": "kit"}), [Where.JOB]),
        "the scan's entry stands in another module's job": (
            Case({"x": scan}, jobs={"x": "const-quiet"}),
            [Where.JOB],
        ),
        "a second entry runs the scan in its module's job": (
            Case({"x": scan, "again": scan}, jobs={"x": "kit", "again": "const-x"}),
            [],
        ),
        "the list's modules leave a module folder out": (
            Case({"x": scan}, listed=("const-x",)),
            [Where.MISSING],
        ),
        "the list names a module with no folder": (
            Case({"x": scan}, listed=("const-x", "const-quiet", "const-gone")),
            [Where.STRAY],
        ),
    }
    for name, (case, wanted) in cases.items():
        ok = [f.where for f in findings_of(case)] == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    with tempfile.TemporaryDirectory() as tmp:  # a scan declared by its Python file, run by python3
        root = Path(tmp).resolve()
        p = "python3 modules/const-p/scripts/check-p.py --scan"
        build(
            root,
            Case({"x": scan, "p": p}, jobs={"p": "const-p"}, folders=("const-x", "const-quiet", "const-p")),
        )
        text = module_text.replace("check-x", "check-p").replace("`check-p --scan`", "`check-p.py --scan`")
        (root / "modules/const-p/MODULE.md").write_text(text, encoding="utf-8")
        ok = check_kit(root)[0] == []
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a scan declared as `<entry>.py --scan` is held by its python3 line")
    ok = declared_scans(module_text) == ["check-x"] and declared_scans(quiet_text) == []
    ok = ok and "runs `python3 modules/const-y/scripts/check-y.py --scan`" in (
        Finding("const-y", Where.GATE, "check-y.py").render()
    )
    ok = ok and declared_scans(module_text.replace("`check-x --scan`", "`check-x.py --scan`")) == [
        "check-x.py"
    ]
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] a span with more after the flag is no scan;"
        " a .py entry is taught by python3"
    )
    for name, case, lines in (
        ("one finding", Case({"x": scan}, workflow="jobs: {}\n"), report_lines),
        (
            "the job and module findings",
            Case({"x": scan}, jobs={"x": "kit"}, listed=("const-x", "const-gone")),
            placed_lines,
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = report(*check_kit(root))
        ok = code == EXIT_RED and printed.getvalue().splitlines() == lines
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the report of {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())
    for name, change, said in (
        ("a list script that fails", "LIST", f"{GATE_LIST} --names gate exited"),
        ("jobs that are no JSON list", "JSON", f"{GATE_LIST} --json printed no list of job names"),
        ("a module document without its anchor", "NO-T9", "modules/const-x/MODULE.md has no enforcement"),
        ("a module folder without its document", "NO-DOC", "modules/empty has no MODULE.md"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, Case({"x": scan}))
            if change == "LIST":
                (root / GATE_LIST).write_text(
                    "#!/bin/sh\necho 'BROKEN: no list' >&2\nexit 1\n", encoding="utf-8"
                )
            if change == "JSON":
                text = (root / GATE_LIST).read_text(encoding="utf-8")
                (root / GATE_LIST).write_text(
                    re.sub(r"--json\) echo '[^']*'", "--json) echo '{\"kit\": 1}'", text), encoding="utf-8"
                )
            if change == "NO-T9":
                (root / "modules/const-x/MODULE.md").write_text("no anchor\n", encoding="utf-8")
            if change == "NO-DOC":
                (root / "modules/empty").mkdir()
            try:
                check_kit(root)
                ok = False
            except Broken as broken:
                ok = said in str(broken) and "fix:" in str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line")
    total = len(cases) + 8
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-gate-lists", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 module documents examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check_kit(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 module documents examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
