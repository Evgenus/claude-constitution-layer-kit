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
No line of the list script or of the workflow, comments aside, passes a fixture runner's filter,
`--item <n>` or `--item=<n>`: a filtered run runs only the items named and is never a full pass,
so the gate list and CI always run every item.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree: a scan missing from the gate list, or
                       from a workflow that does not read the list, red; a scan in both green; an
                       extra entry no gate; a span with more after the flag no scan; a scan whose
                       entry falls into `kit` or another module's job red; a module folder the list
                       leaves out, and a listed module with no folder, red; an `--item` in the
                       list or the workflow red, and one in a comment green; the report of each kind
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
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from kit_module_doc import DocumentError, Fault, Problem, enforcement

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
GATE_LIST = "scripts/gate-list.sh"
WORKFLOW = ".github/workflows/gates.yml"
READS_LIST = ("sh scripts/gate-list.sh --json", "sh scripts/gate-list.sh --run")
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
ITEM_FILTER = re.compile(r"(?<![\w-])--item(?![\w-])")  # the runners' filter, `--item <n>` or `--item=<n>`
WHY_FILTER = "the gate list and CI run every item of every runner, so that their green is a full pass"
WHY_FORM = "a scan the check cannot read is never held in the gate list and CI"
KIT_CHECK = re.compile(
    r"scripts/check-[^/]+\.py"
)  # a tracked path, whole: a check stands at the top of scripts/
WHY_CHECK = "a kit check no entry runs is never run in CI, and its green says nothing"


FORM_WHAT = {  # what a problem of the enforcement section says; its text is the first cell or the span
    Fault.FIRST_CELL: "a row of its enforcement table opens with {}, not E<n>",
    Fault.SPAN: "its enforcement table names `--scan` in a form the check cannot read: {}",
    Fault.UNMARKED: (
        "its enforcement table has a flag after `--scan` in {}, and the words `not a tree scan` are not in"
        " the artifact cell of its row"
    ),
    Fault.PROSE: "{} declares a scan outside the enforcement table",
}
_FORM_SPAN_FIX = (
    "write it `<entry> --scan`, or, for a mode that is no tree scan, `<entry> --scan --<flag> …`"
    " with the words `not a tree scan` in its row"
)
FORM_FIX = {
    Fault.FIRST_CELL: "open the row with E<n>, its number in the table",
    Fault.SPAN: _FORM_SPAN_FIX,
    Fault.UNMARKED: _FORM_SPAN_FIX,
    Fault.PROSE: "move it into a row of the enforcement table, or write it another way",
}


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


class Where(StrEnum):
    GATE = "gate list"
    CI = "CI list"
    JOB = "module's job"
    MISSING = "list's modules"
    STRAY = "module folders"
    FILTER = "item filter"
    FORM = "enforcement table"
    CHECK = "kit checks"


@dataclass(frozen=True)
class Finding:
    module: str
    where: Where
    entry: str = ""  # the declared scan, `<entry>` or `<entry>.py`
    runner: str = ""  # the list's entry that runs the scan
    job: str = ""  # the job that entry stands in, empty for none
    names: tuple[str, ...] = field(default=())  # the list's entries of a module
    line: int = 0  # an item filter or a form: its line in the file, `module` holding the file's path
    fault: Fault = Fault.SPAN  # a form: what is wrong; `entry` then holds the first cell or the span

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
        elif self.where is Where.FILTER:
            return (
                f"RED: {self.module}:{self.line}: it runs a fixture runner with `--item`, which runs only"
                f" the items named\n  why: {WHY_FILTER}\n  fix: remove the `--item` option and its numbers"
                f" from line {self.line} of {self.module}"
            )
        elif self.where is Where.CHECK:  # `module` holds the check's path
            return (
                f"RED: {self.module} is run by no entry of the gate group\n  why: {WHY_CHECK}"
                f"\n  fix: add an entry to GATES in {GATE_LIST} and an arm in commands() that runs"
                f" `python3 {self.module}`, with its `--self-test` where it has one"
            )
        elif self.where is Where.FORM:
            shown = f"`{self.entry}`" if self.entry else "nothing"
            return (
                f"RED: {self.module}:{self.line}: {FORM_WHAT[self.fault].format(shown)}"
                f"\n  why: {WHY_FORM}\n  fix: {FORM_FIX[self.fault]}"
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


def declared_scans(text: str, path: str = "the module document") -> tuple[list[str], list[Problem]]:
    """The scans a module document declares and what is wrong with the form of its enforcement section."""
    try:
        return enforcement(text, path)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


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


def tracked_checks(root: Path) -> list[str]:
    """The kit checks git tracks: `scripts/check-*.py` at the top of scripts/; an untracked file is none."""
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(root.parent)}  # the repository is `root` itself
    try:
        done = subprocess.run(
            ["git", "ls-files", "-z", "--", "scripts"],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as bad:
        raise Broken(f"git cannot be run ({bad.strerror}) — fix: install git") from bad
    if done.returncode != 0:
        said = done.stderr.strip().splitlines()
        raise Broken(
            f"git ls-files scripts exited {done.returncode} ({said[-1] if said else 'no output'})"
            " — fix: run the check from a clone of the kit"
        )
    return sorted(path for path in done.stdout.split("\0") if KIT_CHECK.fullmatch(path))


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


def code_of(line: str) -> str:
    """A line of the list script or the workflow, comments aside: a whole comment line, or a `#`
    after a space or a tab."""
    return "" if line.lstrip().startswith("#") else re.split(r"\s#", line, maxsplit=1)[0]


def ci_reads_list(root: Path) -> bool:
    if not (root / WORKFLOW).is_file():
        return False
    steps = "\n".join(code_of(line) for line in read(root, WORKFLOW).splitlines())
    return all(phrase in steps for phrase in READS_LIST)


def item_filters(root: Path) -> list[Finding]:
    """Every line of the list script and of the workflow, comments aside, that passes a runner's
    `--item`: a filtered run is never a full pass, so neither list may run one."""
    return [
        Finding(path, Where.FILTER, line=number)
        for path in (GATE_LIST, WORKFLOW)
        if (root / path).is_file()
        for number, line in enumerate(read(root, path).splitlines(), start=1)
        if ITEM_FILTER.search(code_of(line))
    ]


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


def check_checks(checks: list[str], gates: dict[str, str]) -> list[Finding]:
    """A tracked kit check that no line of the gate group runs as `python3 scripts/check-<x>.py`, with or
    without arguments: the lines are `--show`'s, comments aside, and a path under modules/ is no kit check."""
    code = [code_of(line) for commands in gates.values() for line in commands.splitlines()]
    findings: list[Finding] = []
    for check in checks:
        runs = re.compile(rf"(?<![\w/.-])python3 {re.escape(check)}(?![\w.-])")
        if not any(runs.search(line) for line in code):
            findings.append(Finding(check, Where.CHECK))
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


def check_kit(root: Path) -> tuple[list[Finding], int, int, int]:
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
        entries, problems = declared_scans(read(root, document), document)
        findings += [Finding(document, Where.FORM, p.text, line=p.line, fault=p.fault) for p in problems]
        for entry in entries:
            scans += 1
            findings += check_scan(module, entry, gates, jobs, ci)
    findings += check_modules(modules, listed(root, "--names", "all").split())
    findings += item_filters(root)
    checks = tracked_checks(root)
    findings += check_checks(checks, gates)
    return findings, len(modules), scans, len(checks)


def report(findings: list[Finding], modules: int, scans: int, checks: int) -> int:
    counts = f"{modules} module document(s) examined, {scans} declared scan(s), {checks} kit check(s)"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job, the"
        " list's modules are the module folders, neither list filters a runner's items, and every kit"
        " check is run by an entry of the gate group"
        f" — {counts}"
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
    document: str = ""  # const-x's module document; empty: the self-test's own
    scripts: dict[str, bool] = field(default_factory=dict)  # a file of the tree, a path: git tracks it
    comment: str = ""  # a comment line at the head of the list script
    repo: bool = True  # the tree is a git repository


def form_probes() -> bool:
    """The forms of the enforcement table, over one whole set of probes in one loop: each is the rows of
    a `t9` section, the scans it declares and the problems it holds, each as (line, fault); the section's
    anchor is line 1, its first row line 2. A probe that fails prints what it got."""
    explain = "`x --scan --command <text>`"
    marked = f"{explain}: not a tree scan"

    def row(artifact: str, handle: str = "E2", kind: str = "`gate`") -> str:
        return f"| {handle} | {artifact} | {kind} |"

    probes: dict[str, tuple[list[str], list[str], list[tuple[int, Fault]]]] = {
        "an indented row is read": ([f"   {row('`x --scan`')}"], ["x"], []),
        "a bold handle is read": ([row("`x --scan`", "**E2**")], ["x"], []),
        "no space after the bar is read": (["|E2 | `x --scan` | `gate` |"], ["x"], []),
        "no space round any cell is read": (["|E2|`x --scan`|`gate`|"], ["x"], []),
        "a `.py` entry is declared as written": ([row("`x.py --scan`: all")], ["x.py"], []),
        "a row with two scans declares both": ([row("`y --scan`, `x --scan`")], ["x", "y"], []),
        "`sh scripts/x.sh --scan` is a problem": ([row("`sh scripts/x.sh --scan`")], [], [(2, Fault.SPAN)]),
        "`python3 scripts/x.py --scan` is a problem": (
            [row("`python3 scripts/x.py --scan`")],
            [],
            [(2, Fault.SPAN)],
        ),
        "`x.py --scan [DIR]` is a problem": ([row("`x.py --scan [DIR]`")], [], [(2, Fault.SPAN)]),
        "the entry and the flag in two spans is a problem": (
            [row("`x.py` `--scan`")],
            [],
            [(2, Fault.SPAN)],
        ),
        "a word after the flag is a problem": ([row("`x --scan all`")], [], [(2, Fault.SPAN)]),
        "a space after the flag is a problem": ([row("`x --scan `")], [], [(2, Fault.SPAN)]),
        "a capital in the entry is a problem": ([row("`X --scan`")], [], [(2, Fault.SPAN)]),
        "a span in the kind cell is read as one in the artifact cell": (
            [row("`x`", kind="`sh x.sh --scan`")],
            [],
            [(2, Fault.SPAN)],
        ),
        "a first cell `G2` is a problem, its scan still read": (
            [row("`x --scan`", "G2")],
            ["x"],
            [(2, Fault.FIRST_CELL)],
        ),
        "a first cell `Example` is a problem": ([row("`x`", "Example")], [], [(2, Fault.FIRST_CELL)]),
        "an empty first cell is a problem": (["|  | `x` | `gate` |"], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `E` with no number is a problem": ([row("`x`", "E")], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `E1a` is a problem": ([row("`x`", "E1a")], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `e1` is a problem": ([row("`x`", "e1")], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `**E1` is a problem": ([row("`x`", "**E1")], [], [(2, Fault.FIRST_CELL)]),
        "a flag after `--scan` with the mark is no scan and no problem": (
            [row(marked)],
            [],
            [],
        ),
        "a flag after `--scan` without the mark is a problem": (
            [row(explain)],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the words only inside a code span are no mark": (
            [row(f"{explain}: `not a tree scan`")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the words in another cell of the row are no mark": (
            [row(explain, kind="not a tree scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the words in another row are no mark": (
            [row(marked), row(explain, "E3")],
            [],
            [(3, Fault.UNMARKED)],
        ),
        "the words one word short are no mark": (
            [row(f"{explain}: not a scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "`x --scan --since <date>` with the mark is no scan": (
            [row("`x --scan --since <date>`: the history report, not a tree scan")],
            [],
            [],
        ),
        "two flags and a word with the mark are no scan": (
            [row("`x --scan --all --since today`: not a tree scan")],
            [],
            [],
        ),
        "a flag with no argument and the mark is no scan": (
            [row("`x.py --scan --all`: not a tree scan")],
            [],
            [],
        ),
        "the mark beside a declared scan leaves it declared": (
            [row("`x --scan`, `y --scan --since <date>`: not a tree scan")],
            ["x"],
            [],
        ),
        "a declared scan beside an unmarked flag form is read, the other a problem": (
            [row("`x --scan`, `y --scan --since <date>`")],
            ["x"],
            [(2, Fault.UNMARKED)],
        ),
        "a header and its separator are skipped": (
            ["| # | artifact | kind |", "|---|---|---|", row("`x --scan`")],
            ["x"],
            [],
        ),
        "an aligned separator is skipped": (
            ["| # | artifact | kind |", "|:--|:-:|--:|", row("`x --scan`")],
            ["x"],
            [],
        ),
        "a table with no header reads every row": (
            [row("`x --scan`"), row("`y --scan`", "E3")],
            ["x", "y"],
            [],
        ),
        "a row below the header is read as a row": (
            ["| # | artifact | kind |", "|---|---|---|", row("`x`", "G1")],
            [],
            [(4, Fault.FIRST_CELL)],
        ),
        "no table, `t9` directly followed by `t10`": ([], [], []),
        "a scan named in prose is a problem": (
            [row("`y`"), "", "It runs `x --scan` here."],
            [],
            [(4, Fault.PROSE)],
        ),
        "a `.py` scan named in prose is a problem": (["Run `x.py --scan`."], [], [(2, Fault.PROSE)]),
        "`--scan --command` in prose, with no entry, is no problem": (
            ["Backstop: the explain, `--scan --command`, shows it."],
            [],
            [],
        ),
        "another mode named in prose is no problem": (
            ["See `x --scan --since <date>` and `sh x.sh --scan`."],
            [],
            [],
        ),
    }
    ok = True
    for name, (rows, scans, faults) in probes.items():
        text = '<a id="t9"></a>\n' + "".join(f"{line}\n" for line in rows) + '<a id="t10"></a>\n'
        got_scans, problems = declared_scans(text)
        got_faults = [(p.line, p.fault) for p in problems]
        if (got_scans, got_faults) != (scans, faults):
            ok = False
            print(f"        probe {name!r}: got {got_scans} and {got_faults}, wanted {scans} and {faults}")
    return ok


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
        "| E3 | `check-x --scan --since <date>`: the report, not a tree scan | `advisory` |\n\n"
        "A sibling's `check-y` is not this module's.\n\n<a id=\"t10\"></a>\n"
    )
    quiet_text = (
        '<a id="t9"></a>\n| E1 | `explain --scan --command <text>`: not a tree scan | `gate` |\n'
        '<a id="t10"></a>\n'
    )
    scan = "sh modules/const-x/scripts/check-x.sh --scan"

    def scans_of(text: str) -> list[str]:
        return declared_scans(text)[0]

    reads = f'jobs:\n  list:\n    run: {READS_LIST[0]}\n  check:\n    run: {READS_LIST[1]} "$JOB"\n'
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` is not in the CI list",
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs",
        f"  fix: let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
        f" `{READS_LIST[1]} <job>`",
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
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
        "RED: 3 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    filter_lines = [
        "RED: .github/workflows/gates.yml:7: it runs a fixture runner with `--item`, which runs only the"
        " items named",
        "  why: the gate list and CI run every item of every runner, so that their green is a full pass",
        "  fix: remove the `--item` option and its numbers from line 7 of .github/workflows/gates.yml",
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]

    def script(case: Case) -> str:
        """A stand-in for the list script: `--names gate|all|<job>`, `--json` and `--show <entry>`."""
        own = {
            f"{kind}-{m}": m for m in (case.folders if case.listed is None else case.listed) for kind in KINDS
        }
        extras = {**dict.fromkeys((n for n in own if n not in case.gates), "true"), **case.extras}
        jobs = {**{name: "kit" for name in {**case.gates, **extras}}, "x": "const-x", **own, **case.jobs}
        names = {"gate": list(case.gates), "all": [*case.gates, *extras]}
        for name, job in jobs.items():
            names.setdefault(job, []).append(name)
        groups = "".join(f"            {key}) set -- {' '.join(value)} ;;\n" for key, value in names.items())
        arms = "".join(
            f"            {name}) echo '{cmd}' ;;\n" for name, cmd in {**extras, **case.gates}.items()
        )
        listing = json.dumps(sorted(set(jobs.values())))
        return (
            f'#!/bin/sh\n{f"# {case.comment}" if case.comment else ""}\ncase "$1" in\n'
            f'    --names) case "$2" in\n{groups}            *) exit 1 ;;\n        esac\n'
            '        for n in "$@"; do echo "$n"; done ;;\n'
            f"    --json) echo '{listing}' ;;\n"
            f'    --show) case "$2" in\n{arms}            *) exit 1 ;;\n        esac ;;\n'
            "    *) exit 1 ;;\nesac\n"
        )

    def build(root: Path, case: Case) -> None:
        documents = {"const-x": case.document or module_text, "const-quiet": quiet_text}
        for path, text in (
            *((f"modules/{m}/MODULE.md", documents.get(m, quiet_text)) for m in case.folders),
            (GATE_LIST, script(case)),
            (WORKFLOW, case.workflow or reads),
        ):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")
        for path in case.scripts:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        if case.repo:  # `git add` for the tracked files alone, so an untracked one is no kit check
            git = ["git", "-c", "init.defaultBranch=main"]
            subprocess.run([*git, "init", "-q"], cwd=root, check=True)
            tracked = [path for path, yes in case.scripts.items() if yes]
            if tracked:
                subprocess.run(["git", "add", "--", *tracked], cwd=root, check=True)

    def findings_of(case: Case) -> list[Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            return check_kit(root)[0]

    trailing = f"\t# {READS_LIST[1]}\n"
    new = "scripts/check-new.py"
    tracked = {new: True}
    run_new = f"python3 {new}"
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
        "the list runs a fixture runner with --item": (
            Case({"x": scan}, {"filtered": "python3 modules/const-x/tests/run.py --item 3"}),
            [Where.FILTER],
        ),
        "the workflow runs a fixture runner with --item=": (
            Case(
                {"x": scan},
                workflow=f"{reads}  more:\n    run: python3 modules/const-x/tests/run.py --item=3\n",
            ),
            [Where.FILTER],
        ),
        "a row of the enforcement table the check cannot read is a finding of its own": (
            Case(
                {"x": scan},
                document='<a id="t9"></a>\n| G2 | `check-x --scan` | `gate` |\n<a id="t10"></a>\n',
            ),
            [Where.FORM],
        ),
        "--item only in comments, and --items, filter nothing": (
            Case(
                {"x": scan},
                {"noted": "python3 modules/const-x/tests/run.py  # not --item 3"},
                workflow=f"{reads}  # run.py --item 3\n  more:\n    run: run.py --items 3\n",
            ),
            [],
        ),
        "a tracked kit check an entry of the gate group runs": (
            Case({"x": scan, "new": f"{run_new}\n{run_new} --self-test"}, scripts=tracked),
            [],
        ),
        "a tracked kit check no entry runs": (Case({"x": scan}, scripts=tracked), [Where.CHECK]),
        "the same file untracked is no kit check": (Case({"x": scan}, scripts={new: False}), []),
        "a kit check run only by its --self-test": (
            Case({"x": scan, "new": f"{run_new} --self-test"}, scripts=tracked),
            [],
        ),
        "a kit check run only by --module in an install entry of the gate group": (
            Case({"x": scan, "install-const-x": f"{run_new} --module const-x"}, scripts=tracked),
            [],
        ),
        "a kit check run only by the extra entry lint": (
            Case({"x": scan}, {"lint": run_new}, scripts=tracked),
            [Where.CHECK],
        ),
        "a kit check run only by a fixtures entry": (
            Case({"x": scan}, {"fixtures-const-x": f"{run_new} --self-test"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a kit check named in a comment of the list script only": (
            Case({"x": scan}, comment=run_new, scripts=tracked),
            [Where.CHECK],
        ),
        "a kit check named after a # in a gate's command only": (
            Case({"x": scan, "noted": f"true  # {run_new}"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a kit check no entry runs, beside one whose name it opens": (
            Case(
                {"x": scan, "newer": "python3 scripts/check-newer.py"},
                scripts={**tracked, "scripts/check-newer.py": True},
            ),
            [Where.CHECK],
        ),
        "a module's script of that name is no run of the kit check": (
            Case({"x": scan, "new": "python3 modules/const-x/scripts/check-new.py --scan"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a library and a helper no entry runs are no kit checks": (
            Case({"x": scan}, scripts={"scripts/kit_module_doc.py": True, "scripts/helper.py": True}),
            [],
        ),
    }
    for name, (case, wanted) in cases.items():
        ok = [f.where for f in findings_of(case)] == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    names = {  # which tracked path is a kit check: the name filter over its whole set
        "scripts/check-x.py": True,
        "scripts/check-x.sh": False,
        "scripts/check_x.py": False,
        "scripts/checkx.py": False,
        "scripts/check-.py": False,
        "scripts/Check-x.py": False,
        "scripts/check-x.pyc": False,
        "scripts/check-x.py.bak": False,
        "scripts/kit_module_doc.py": False,
        "scripts/helper.py": False,
        "scripts/sub/check-y.py": False,  # a script under a folder is none: only the top of scripts/ counts
        "scripts/check-sub/z.py": False,  # nor is one in a folder whose name opens `check-`
        "modules/const-x/scripts/check-x.py": False,
    }
    ok = True
    for path, is_check in names.items():
        got = [f.module for f in findings_of(Case({"x": scan}, scripts={path: True}))]
        if got != ([path] if is_check else []):
            ok = False
            print(f"        name {path!r}: got {got}, a kit check is {is_check}")
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] only `scripts/check-<x>.py` at the top of scripts/ is a kit check,"
        " over the whole set of names"
    )
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
    ok = scans_of(module_text) == ["check-x"] and scans_of(quiet_text) == []
    ok = ok and "runs `python3 modules/const-y/scripts/check-y.py --scan`" in (
        Finding("const-y", Where.GATE, "check-y.py").render()
    )
    ok = ok and scans_of(module_text.replace("`check-x --scan`", "`check-x.py --scan`")) == ["check-x.py"]
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] a span with more after the flag is no scan;"
        " a .py entry is taught by python3"
    )
    last_section = '## 9 <a id="t9"></a> is prose here\n\n<a id="t9"></a>\n| E1 | `check-x --scan` |\n'
    ok = scans_of(last_section) == ["check-x"]  # the last section reads to the end of the file
    ok = ok and scans_of('<a id="t9"></a>\n<a id="t10"></a>\n| E1 | `check-x --scan` |\n') == []
    ok = ok and scans_of('  <a id="t9"></a>  \n| E1 | `check-x --scan` |\n') == ["check-x"]
    # an anchor of another id, alone on its line, ends no section: the E-row after it is still read
    other_id = (
        '<a id="t9"></a>\n<a id="x"></a>\n| E1 | `check-x --scan` |\n'
        '<a id="r2"></a>\n| E2 | `check-y --scan` |\n'
    )
    ok = ok and scans_of(other_id) == ["check-x", "check-y"]
    try:  # nor does it count as doubled: two of one id are no error
        ok = ok and scans_of(other_id.replace('<a id="r2"></a>', '<a id="x"></a>')) == [
            "check-x",
            "check-y",
        ]
    except Broken:
        ok = False
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] the enforcement section reads to the end of the file when it is the"
        " last, is empty when the end anchor follows at once, an anchor inside prose is plain text, and an"
        " anchor of another id alone on its line neither ends it nor counts as doubled"
    )
    ok = form_probes()
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the enforcement table's forms, over the whole set of probes")
    form_text = (
        '<a id="t9"></a>\n| E1 | `check-x --scan` | `gate` |\n| G2 | `sh scripts/x.sh --scan` | `gate` |\n'
        "| E3 | `x --scan --since <date>` | `gate` |\n|  | none | `gate` |\n"
        'Declared in `y.py --scan` here.\n<a id="t10"></a>\n'
    )
    form_why = "  why: a scan the check cannot read is never held in the gate list and CI"
    form_fix = (
        "  fix: write it `<entry> --scan`, or, for a mode that is no tree scan,"
        " `<entry> --scan --<flag> …` with the words `not a tree scan` in its row"
    )
    form_lines = [  # typed by hand
        "RED: modules/const-x/MODULE.md:3: a row of its enforcement table opens with `G2`, not E<n>",
        form_why,
        "  fix: open the row with E<n>, its number in the table",
        "RED: modules/const-x/MODULE.md:3: its enforcement table names `--scan` in a form the check cannot"
        " read: `sh scripts/x.sh --scan`",
        form_why,
        form_fix,
        "RED: modules/const-x/MODULE.md:4: its enforcement table has a flag after `--scan` in"
        " `x --scan --since <date>`, and the words `not a tree scan` are not in the artifact cell of its row",
        form_why,
        form_fix,
        "RED: modules/const-x/MODULE.md:5: a row of its enforcement table opens with nothing, not E<n>",
        form_why,
        "  fix: open the row with E<n>, its number in the table",
        "RED: modules/const-x/MODULE.md:6: `y.py --scan` declares a scan outside the enforcement table",
        form_why,
        "  fix: move it into a row of the enforcement table, or write it another way",
        "RED: 5 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    two_lines = [  # typed by hand
        "RED: scripts/check-a.py is run by no entry of the gate group",
        "  why: a kit check no entry runs is never run in CI, and its green says nothing",
        "  fix: add an entry to GATES in scripts/gate-list.sh and an arm in commands() that runs"
        " `python3 scripts/check-a.py`, with its `--self-test` where it has one",
        "RED: scripts/check-b.py is run by no entry of the gate group",
        "  why: a kit check no entry runs is never run in CI, and its green says nothing",
        "  fix: add an entry to GATES in scripts/gate-list.sh and an arm in commands() that runs"
        " `python3 scripts/check-b.py`, with its `--self-test` where it has one",
        "RED: 2 finding(s) — 2 module document(s) examined, 1 declared scan(s), 3 kit check(s)",
    ]
    for name, case, lines in (
        (
            "two kit checks no entry runs, in sorted order",
            Case(
                {"x": scan, "c": "python3 scripts/check-c.py"},
                scripts={f"scripts/check-{n}.py": True for n in ("b", "c", "a")},
            ),
            two_lines,
        ),
        ("one finding", Case({"x": scan}, workflow="jobs: {}\n"), report_lines),
        ("the findings of a table the check cannot read", Case({"x": scan}, document=form_text), form_lines),
        (
            "the job and module findings",
            Case({"x": scan}, jobs={"x": "kit"}, listed=("const-x", "const-gone")),
            placed_lines,
        ),
        (
            "an item filter",
            Case(
                {"x": scan},
                workflow=f"{reads}  filtered:\n    run: python3 modules/const-x/tests/run.py --item 3\n",
            ),
            filter_lines,
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
    with tempfile.TemporaryDirectory() as tmp:  # the green line, with every kit check run
        root = Path(tmp).resolve()
        build(root, Case({"x": scan, "new": run_new}, scripts=tracked))
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    green_line = (
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job, the list's"
        " modules are the module folders, neither list filters a runner's items, and every kit check is run"
        " by an entry of the gate group — 2 module document(s) examined, 1 declared scan(s), 1 kit check(s)"
    )
    ok = code == EXIT_GREEN and printed.getvalue().splitlines() == [green_line]
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of a kit whose checks all run is its literal green line")
    if not ok:
        print(printed.getvalue())
    for name, change, said in (
        ("a list script that fails", "LIST", f"{GATE_LIST} --names gate exited"),
        ("jobs that are no JSON list", "JSON", f"{GATE_LIST} --json printed no list of job names"),
        (
            "a module document without its anchor",
            "NO-T9",
            'modules/const-x/MODULE.md has no anchor <a id="t9"></a> on a line of its own',
        ),
        (
            "a module document whose anchor has text on its line",
            "T9-ON-HEADING",
            'modules/const-x/MODULE.md has no anchor <a id="t9"></a> on a line of its own',
        ),
        (
            "a module document whose enforcement anchor stands twice",
            "T9-TWICE",
            'modules/const-x/MODULE.md holds the anchor <a id="t9"></a> twice, lines 1 and 3',
        ),
        (
            "a module document with a second end anchor above its E-row",
            "T10-TWICE",
            'modules/const-x/MODULE.md holds the anchor <a id="t10"></a> twice, lines 7 and 13',
        ),
        ("a module folder without its document", "NO-DOC", "modules/empty has no MODULE.md"),
        ("a tree that is no git repository", "NO-REPO", "git ls-files scripts exited"),
        ("a git that cannot be run", "NO-GIT", "git cannot be run"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, Case({"x": scan}, repo=change != "NO-REPO"))
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
            if change in ("T9-ON-HEADING", "T9-TWICE", "T10-TWICE"):
                broken_text = {
                    "T9-ON-HEADING": module_text.replace('<a id="t9"></a>\n## 9', '## 9 <a id="t9"></a>'),
                    "T9-TWICE": module_text.replace("## 9\n", '## 9\n<a id="t9"></a>\n', 1),
                    "T10-TWICE": module_text.replace("| E2 |", '<a id="t10"></a>\n| E2 |', 1),
                }[change]
                (root / "modules/const-x/MODULE.md").write_text(broken_text, encoding="utf-8")
            if change == "NO-DOC":
                (root / "modules/empty").mkdir()
            path = os.environ["PATH"]
            if change == "NO-GIT":
                os.environ["PATH"] = ""
            try:
                tracked_checks(root) if change == "NO-GIT" else check_kit(root)
                ok = False
            except Broken as broken:
                ok = said in str(broken) and "fix:" in str(broken)
            finally:
                os.environ["PATH"] = path
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line")
    total = len(cases) + 20
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
