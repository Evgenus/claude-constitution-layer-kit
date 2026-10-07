#!/usr/bin/env python3
"""Kit check: every scan a module declares stands in the kit's gate list, in its CI list and in its
module's job, the list's modules are exactly the module folders, each module folder is named
`const-<aspect>`, named so by its manifest, listed once in the marketplace and enabled in the kit's
settings, which declare the marketplace, and every kit check is run by an entry of the gate group.

A module declares its scan in its document's enforcement section (template §9, anchor `t9`), read
by `kit_module_doc.enforcement` row by row, whatever a row's indent: a line whose stripped form
starts with `|`, the header and the separator skipped. A row opens `E<n>` or `**E<n>**`. A code span
in a row that reads exactly `<entry> --scan`, or `<entry>.py --scan`, declares a scan. A span
`<entry> --scan --<flag> …`, an explain mode (`--scan --command …`) or a report (`--scan --since …`),
is no tree scan and declares none, when the cell that holds it also holds the words `not a tree scan`
outside a code span. Each of these is a finding of the form, with the line, why and fix: a row whose
first cell is anything else; a span in a row that holds `--scan` in any other form; a flag after
`--scan` in a cell without the words; a span in the declared form in the section's prose, outside
the table (any other span there is not read). A row whose first cell is off has its spans read all
the same, and every row's last cell is read whether or not the row closes with a bar. A module
document whose enforcement section has no end, `t10` gone while a later anchor stands, or whose
`t10` stands elsewhere while another anchor, or none, follows `t9`, is no document the check can read
(BROKEN), since the section would run on into the acceptance table; the first message says to restore
`t10`, the second to put the sections in the template's order. For each
declared scan:
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
and must hold its `MODULE.md`: `kit_module_doc.module_folders`, the kit's one listing, which every
kit check that walks the modules reads, gives them sorted by name and fails when `modules/` or a
`MODULE.md` is missing, as a BROKEN here, and the self-test proves it over every class of entry
(`folder_probes`). A module that declares no scan is examined and needs no scan entry.
The list's modules, its `MODULES`, are read from its entries `install-<module>`, `fixtures-<module>`,
`lint-<module>` and `types-<module>` in `--names all`: each module folder has all four, and no
module that has one lacks its folder (decisions dec-0056-portability-grep-and-gate-lists,
dec-0058-ci-runs-each-check-in-parallel and dec-0061-ci-runs-one-job-per-module).
Each of those folders is also held against the three files that name a module, one RED finding with
why and fix for each copy that disagrees, listed by folder and then by file, the entries and keys that
name no module folder by name:
  - its name matches `const-[a-z0-9]+(-[a-z0-9]+)*` in full, kernel §7;
  - `modules/<m>/.claude-plugin/plugin.json` is a JSON object, and its `name` is the string `<m>`;
  - `.claude-plugin/marketplace.json` is a JSON object with a `name`, a non-empty string, the
    marketplace's name, read there and typed nowhere in this check, and a list `plugins`: for each
    folder exactly one entry, an object, whose `name` is `<m>` and whose `source` is the string
    `./modules/<m>`; no entry names anything that is no module folder, and an entry's other keys, the
    marketplace's other keys and its `owner` are the platform's and are never read;
  - `.claude/settings.json` is a JSON object: under `enabledPlugins` the key `<m>@<marketplace name>`
    is `true`, the JSON boolean and nothing else, for each folder, a committed `false` included, the one
    switch-off being a clone's git-ignored `.claude/settings.local.json`, which this check never reads;
    no other key ends `@<marketplace name>`, and keys of other marketplaces stand; under
    `extraKnownMarketplaces` the key `<marketplace name>` has a `source` that is exactly
    `{"source": "directory", "path": "."}`, the kit's own folder, other marketplaces and other keys of
    the value standing.
A file that cannot be read is BROKEN, not RED: one that is missing, is no JSON or is no JSON object, a
manifest included; a marketplace with no `name` that is a non-empty string, no list `plugins` or an
entry that is no object with a string `name`, since it is then no marketplace the check can compare;
`enabledPlugins` or `extraKnownMarketplaces` present and no object. A key the platform lets stand
absent, `enabledPlugins` or `extraKnownMarketplaces` in the settings, is read as empty and is RED for
what it leaves out. The green line counts the marketplace's entries and the enabled keys it read.
No line of the list script or of the workflow, comments aside, passes a fixture runner's filter,
`--item <n>` or `--item=<n>`: a filtered run runs only the items named and is never a full pass,
so the gate list and CI always run every item.
Every `scripts/check-*.py` that git tracks at the top of `scripts/` (`git ls-files`; an untracked
file, a library such as `kit_module_doc.py` and a file in a folder are none) is run by an entry of the
gate group: a code line of that entry's `--show`, comments aside, holds `python3 scripts/check-<x>.py`
as whole words, with or without arguments — not after a name or path character, so `xpython3` and
`/usr/bin/python3` are no run, and not before one, so `check-<x>.py.bak` is none. The kit root must be
the git repository itself.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree, itself a git repository: a scan missing
                       from the gate list, or from a workflow that does not read the list, red; a
                       scan in both green; an extra entry no gate; a span with a flag after `--scan`
                       and the words no scan; a scan whose entry falls into `kit` or another
                       module's job red; a module folder the list leaves out, and a listed module
                       with no folder, red; an `--item` in the list or the workflow red, and one in
                       a comment green; the folder name over a whole set of names; a manifest, a
                       marketplace entry, an enabled key and the declaration each changed one at
                       a time, the platform's other keys allowed, the marketplace renamed in all
                       three places green and in each pair of them red or green as the rule says,
                       the name read and never typed; the findings of every kind as literal
                       lines with exit 2, whatever the order of the files' keys, of their lists
                       and of the folder listing, and each file the check cannot read as its
                       literal BROKEN line with exit 1; the forms of the enforcement table over
                       one whole set of probes (indent, bold, first cells, span forms, the words,
                       an escaped bar);
                       a tracked check no entry of the gate group runs red, also when only an
                       extra entry, a fixtures entry or a comment names it, one a gate entry runs
                       green, with arguments too, the same file untracked, a library and a
                       module's script of that name no check, and the name filter over a whole
                       set of names; the report of each kind of finding, the form's and the
                       checks' included, as literal lines with exit 2, and of a green kit as its
                       literal line; a list that cannot be read, jobs that are no JSON list, a
                       module document without its enforcement anchor, with it on a heading or
                       twice, without its end anchor with a later one standing, or with `t11` before
                       it, a module folder without its document, a tree that is no repository
                       and a git that cannot be run, each a BROKEN line; a `.py` scan held by its
                       python3 line and taught by it.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from kit_module_doc import DocumentError, Fault, Problem, enforcement, module_folders

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
NAME = re.compile(
    r"const-[a-z0-9]+(?:-[a-z0-9]+)*"
)  # kernel §7: `const-<aspect>`, kebab-case, the whole name
MARKETPLACE_FILE = ".claude-plugin/marketplace.json"
SETTINGS_FILE = ".claude/settings.json"
DIRECTORY_SOURCE = {"source": "directory", "path": "."}  # the kit's own folder, as a settings source
WHY_NAME = (
    "the kernel names every module `const-<aspect>`, lowercase kebab-case, and the CI gives a job"
    " Claude Code by that prefix"
)
WHY_MANIFEST = (
    "a plugin installs under its manifest's name, so a name that is not the folder's splits the install"
    " from the marketplace entry and the settings key"
)
WHY_MARKET = "a module the marketplace leaves out cannot be installed, by the kit's CI or by a consumer"
WHY_SOURCE = (
    "the marketplace tells the platform where a plugin loads from, and a source that is not the module's"
    " folder loads another plugin or none"
)
WHY_TWICE = (
    "a plugin's name must lead to one source, and with two entries it is open which one an install reads"
)
WHY_MARKET_STRAY = (
    "the marketplace lists exactly the module folders, and an entry that names no module folder is a"
    " plugin no module backs"
)
WHY_ENABLED = (
    "the kit's sessions load only the plugins its committed settings enable, and the one switch-off,"
    " `false`, belongs in a clone's .claude/settings.local.json"
)
WHY_ENABLED_STRAY = (
    "the settings enable exactly the module folders, and a key that names no module folder enables a"
    " plugin no module backs"
)
WHY_KNOWN = (
    "a session finds the kit's plugins only through a marketplace its settings declare, and the enabled"
    " keys name it"
)
WHY_KNOWN_SOURCE = (
    "the kit loads its own modules from its own folder, so any other source loads another marketplace or none"
)


FORM_WHAT = {  # what a problem of the enforcement section says; its text is the first cell or the span
    Fault.FIRST_CELL: "a row of its enforcement table opens with {}, not E<n>",
    Fault.SPAN: "its enforcement table names `--scan` in a form the check cannot read: {}",
    Fault.UNMARKED: (
        "its enforcement table has a flag after `--scan` in {}, and the words `not a tree scan` are not in"
        " the cell that holds the span, outside a code span"
    ),
    Fault.PROSE: "{} declares a scan outside the enforcement table",
}
_FORM_SPAN_FIX = (
    "write it `<entry> --scan`, or, for a mode that is no tree scan, `<entry> --scan --<flag> …`"
    " with the words `not a tree scan` in the same cell as the span, outside the code span"
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
    NAME = "folder name"
    MANIFEST = "manifest"
    MARKETPLACE = "marketplace entry"
    MARKET_SOURCE = "marketplace source"
    MARKET_TWICE = "marketplace entries"
    MARKET_STRAY = "marketplace strays"
    SETTINGS = "enabled plugin"
    SETTINGS_STRAY = "enabled strays"
    KNOWN_MISSING = "declared marketplace"
    KNOWN_SOURCE = "marketplace source declared"


REGISTRY = frozenset(
    {
        Where.NAME,
        Where.MANIFEST,
        Where.MARKETPLACE,
        Where.MARKET_SOURCE,
        Where.MARKET_TWICE,
        Where.MARKET_STRAY,
        Where.SETTINGS,
        Where.SETTINGS_STRAY,
        Where.KNOWN_MISSING,
        Where.KNOWN_SOURCE,
    }
)  # the findings about the files that name a module, in `Finding.registry`


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
    said: str = ""  # a registry finding: what the file holds, as JSON text; empty: it holds nothing there
    tag: str = ""  # a registry finding: the marketplace name, read from marketplace.json

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
        elif self.where in REGISTRY:
            what, why, fix = self.registry()
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

    def registry(self) -> tuple[str, str, str]:
        """What, why and fix of a finding about the files that name a module: `module` is the folder, the
        entry's name or the key, `said` what the file holds there as JSON text, `tag` the marketplace name."""
        m, said, tag = self.module, self.said, self.tag
        manifest = f"modules/{m}/.claude-plugin/plugin.json"
        enable = f"{json.dumps(f'{m}@{tag}')}: true"
        named = m.removesuffix(f"@{tag}")  # a stray's folder name: the entry's name, the key's before `@`
        # modules/<named> could become a module folder, and pass every hold, only when it bears a module's
        # name, `const-<aspect>`; for any other name, "" included, the removal is the one fix
        possible = NAME.fullmatch(named) is not None
        make = f", or make modules/{named} a module folder holding its MODULE.md" if possible else ""
        if self.where is Where.NAME:
            if not m.startswith("const") and NAME.fullmatch(f"const-{m}"):
                rename = f"to modules/const-{m}"
            else:
                rename = "to a name `const-<aspect>`, lowercase letters and digits joined by single hyphens"
            fix = (
                f"rename modules/{m} {rename}, and name its manifest, marketplace entry, settings key and"
                " entry in MODULES the same"
            )
            return "a module folder's name is not const-<aspect>", WHY_NAME, fix
        if self.where is Where.MANIFEST:
            named = (
                f"is named {said}, not {json.dumps(m)}"
                if said
                else f"has no name, where it must be {json.dumps(m)}"
            )
            return (
                f"its manifest {manifest} {named}",
                WHY_MANIFEST,
                f'set "name": {json.dumps(m)} in {manifest}',
            )
        if self.where is Where.MARKETPLACE:
            entry = json.dumps({"name": m, "source": f"./modules/{m}"})
            return (
                "the marketplace has no entry for it",
                WHY_MARKET,
                f"add {entry} to plugins in {MARKETPLACE_FILE}",
            )
        if self.where is Where.MARKET_SOURCE:
            what = f"its marketplace entry has {said}, not source {json.dumps(f'./modules/{m}')}"
            fix = (
                f'set "source" to {json.dumps(f"./modules/{m}")} in the entry named {json.dumps(m)}'
                f" of plugins in {MARKETPLACE_FILE}"
            )
            return what, WHY_SOURCE, fix
        if self.where is Where.MARKET_TWICE:
            fix = (
                f"remove all but one entry named {json.dumps(m)} from plugins in {MARKETPLACE_FILE},"
                f" the one whose source is {json.dumps(f'./modules/{m}')}"
            )
            return f"the marketplace has {said} entries for it", WHY_TWICE, fix
        if self.where is Where.MARKET_STRAY:
            what = f"the marketplace has an entry for it, but modules/{m} is no module folder"
            fix = f"remove the entry named {json.dumps(m)} from plugins in {MARKETPLACE_FILE}{make}"
            return what, WHY_MARKET_STRAY, fix
        if self.where is Where.SETTINGS:
            what = (
                f"the kit's settings set {json.dumps(f'{m}@{tag}')} to {said}, not true"
                if said
                else "the kit's settings do not enable it"
            )
            return what, WHY_ENABLED, f"set {enable} under enabledPlugins in {SETTINGS_FILE}"
        if self.where is Where.SETTINGS_STRAY:
            what = f"the kit's settings enable it, but modules/{named} is no module folder"
            fix = f"remove the key {json.dumps(m)} from enabledPlugins in {SETTINGS_FILE}{make}"
            return what, WHY_ENABLED_STRAY, fix
        declared = f'{json.dumps(m)}: {{"source": {json.dumps(DIRECTORY_SOURCE)}}}'
        if self.where is Where.KNOWN_MISSING:
            what = "the kit's settings do not declare the marketplace under extraKnownMarketplaces"
            return what, WHY_KNOWN, f"add {declared} under extraKnownMarketplaces in {SETTINGS_FILE}"
        what = (
            f"the kit's settings declare the marketplace with {said},"
            f" not source {json.dumps(DIRECTORY_SOURCE)}"
        )
        fix = (
            f"set the source of {json.dumps(m)} under extraKnownMarketplaces in {SETTINGS_FILE}"
            f" to {json.dumps(DIRECTORY_SOURCE)}"
        )
        return what, WHY_KNOWN_SOURCE, fix


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


def read_json(root: Path, path: str) -> dict[str, Any]:
    """A JSON object of the tree; a file that is missing, is no JSON or is no object is BROKEN."""
    if not (root / path).is_file():
        raise Broken(f"{path} is no file — fix: restore it as a JSON file holding an object")
    try:
        data = json.loads(read(root, path))
    except json.JSONDecodeError as bad:
        raise Broken(
            f"{path} is no JSON ({bad.msg}, line {bad.lineno}) — fix: restore it as a JSON object"
        ) from bad
    if not isinstance(data, dict):
        raise Broken(
            f"{path} is no JSON object, it holds a {type(data).__name__} — fix: restore it as a JSON object"
        )
    return data


def shown(value: object) -> str:
    """A JSON value as text for a finding, its keys sorted so that the file's order never shows."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def read_marketplace(root: Path) -> tuple[str, dict[str, list[dict[str, Any]]], int]:
    """The marketplace's name, its entries by name, and how many entries it has. The name is read here,
    never typed in the check. A file with no name, no list `plugins` or an entry that is no object with
    a name is no marketplace the check can read."""
    market = read_json(root, MARKETPLACE_FILE)
    tag = market.get("name")
    if not isinstance(tag, str) or not tag:
        raise Broken(
            f'{MARKETPLACE_FILE} has no marketplace name, "name" is no non-empty string'
            " — fix: restore it, the name the kit's settings enable plugins under"
        )
    plugins = market.get("plugins")
    if not isinstance(plugins, list):
        raise Broken(
            f'{MARKETPLACE_FILE} has no list "plugins" — fix: restore it as a list of entries'
            ' {"name": …, "source": …}'
        )
    entries: dict[str, list[dict[str, Any]]] = {}
    for position, entry in enumerate(plugins, start=1):
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise Broken(
                f"{MARKETPLACE_FILE}: entry {position} of plugins is no object with a string name"
                ' — fix: write each entry as {"name": …, "source": …}'
            )
        entries.setdefault(entry["name"], []).append(entry)
    return tag, entries, len(plugins)


def settings_object(settings: dict[str, Any], key: str) -> dict[str, Any]:
    """A key of the kit's settings that must be an object where it stands; absent is the empty one, as
    the platform reads it."""
    value = settings.get(key, {})
    if not isinstance(value, dict):
        raise Broken(f"{SETTINGS_FILE}: {key} is no JSON object — fix: restore it as an object")
    return value


def check_registries(root: Path, modules: list[str]) -> tuple[list[Finding], int, int]:
    """Each module folder is named `const-<aspect>` (kernel §7), is named so by its manifest, stands once in
    the marketplace with `./modules/<folder>` as its source, and is enabled, `true`, in the kit's settings,
    which declare the marketplace by a `directory` source at `.`; neither file names anything else of the
    marketplace. The marketplace's name is read from marketplace.json. The findings come in a fixed
    order, whatever the files' key order: by folder, name then manifest; the marketplace entries by folder,
    then the strays by name; the enabled keys the same; the declaration last. Returns them, the entry
    count of the marketplace and the count of its keys in `enabledPlugins`."""
    findings: list[Finding] = []
    for module in modules:
        if not NAME.fullmatch(module):
            findings.append(Finding(module, Where.NAME))
        manifest = read_json(root, f"modules/{module}/.claude-plugin/plugin.json")
        if manifest.get("name") != module:
            said = shown(manifest["name"]) if "name" in manifest else ""
            findings.append(Finding(module, Where.MANIFEST, said=said))
    tag, entries, plugins = read_marketplace(root)
    for module in modules:
        got = entries.get(module, [])
        wanted = f"./modules/{module}"
        if not got:
            findings.append(Finding(module, Where.MARKETPLACE))
        elif len(got) > 1:
            findings.append(Finding(module, Where.MARKET_TWICE, said=str(len(got))))
        elif got[0].get("source") != wanted:
            said = f"source {shown(got[0]['source'])}" if "source" in got[0] else "no source"
            findings.append(Finding(module, Where.MARKET_SOURCE, said=said))
    findings += [Finding(name, Where.MARKET_STRAY) for name in sorted(set(entries) - set(modules))]
    settings = read_json(root, SETTINGS_FILE)
    enabled = settings_object(settings, "enabledPlugins")
    known = settings_object(settings, "extraKnownMarketplaces")
    for module in modules:
        value = enabled.get(f"{module}@{tag}")
        if value is not True:
            said = shown(value) if f"{module}@{tag}" in enabled else ""
            findings.append(Finding(module, Where.SETTINGS, said=said, tag=tag))
    ours = sorted(key for key in enabled if key.endswith(f"@{tag}"))
    findings += [
        Finding(key, Where.SETTINGS_STRAY, tag=tag)
        for key in ours
        if key.removesuffix(f"@{tag}") not in modules
    ]
    if tag not in known:
        findings.append(Finding(tag, Where.KNOWN_MISSING))
    else:
        entry = known[tag]
        source = entry.get("source") if isinstance(entry, dict) else None
        if source != DIRECTORY_SOURCE:
            said = f"source {shown(source)}" if isinstance(entry, dict) and "source" in entry else "no source"
            findings.append(Finding(tag, Where.KNOWN_SOURCE, said=said))
    return findings, plugins, len(ours)


def check_kit(root: Path) -> tuple[list[Finding], int, int, int, int, int]:
    try:
        modules = [folder.name for folder in module_folders(root)]
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    gates, jobs, ci = gate_list(root), jobs_of(root), ci_reads_list(root)
    findings: list[Finding] = []
    scans = 0
    for module in modules:
        document = f"modules/{module}/MODULE.md"
        entries, problems = declared_scans(read(root, document), document)
        findings += [Finding(document, Where.FORM, p.text, line=p.line, fault=p.fault) for p in problems]
        for entry in entries:
            scans += 1
            findings += check_scan(module, entry, gates, jobs, ci)
    findings += check_modules(modules, listed(root, "--names", "all").split())
    registry, plugins, enabled = check_registries(root, modules)
    findings += registry
    findings += item_filters(root)
    checks = tracked_checks(root)
    findings += check_checks(checks, gates)
    return findings, len(modules), scans, len(checks), plugins, enabled


def report(findings: list[Finding], modules: int, scans: int, checks: int, plugins: int, enabled: int) -> int:
    counts = f"{modules} module document(s) examined, {scans} declared scan(s), {checks} kit check(s)"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job, the"
        " list's modules are the module folders, each named const-<aspect> and by its manifest, listed"
        " once in the marketplace and enabled in the kit's settings, which declare the marketplace,"
        " neither list filters a runner's items, and every kit check is run by an entry of the gate group"
        f" — {counts}, {plugins} marketplace plugin(s), {enabled} enabled plugin(s)"
    )
    return EXIT_GREEN


def broken_report(broken: Broken) -> int:
    print(f"BROKEN: {broken}")
    print("BROKEN: the check could not run — 0 module documents examined")
    return EXIT_BROKEN


def run(root: Path) -> int:
    """The plain run on `root`: its report, or the two BROKEN lines."""
    try:
        return report(*check_kit(root))
    except Broken as broken:
        return broken_report(broken)


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
    documents: dict[str, str] = field(default_factory=dict)  # another folder's module document, by name
    scripts: dict[str, bool] = field(default_factory=dict)  # a file of the tree, a path: git tracks it
    comment: str = ""  # a comment line at the head of the list script
    repo: bool = True  # the tree is a git repository
    tag: str = "kit-test"  # the marketplace name of the default registry files
    files: dict[str, object] = field(default_factory=dict)
    # the registry files, by path, when the case writes its own: an object or list is written as JSON, a
    # text as it is, None leaves the file out; empty: `registry_tree(folders, tag)`


def registry_tree(folders: tuple[str, ...], tag: str) -> dict[str, Any]:
    """The files that name the modules, matching `folders`: a manifest each, the marketplace `tag` with one
    entry each, and the settings that enable each and declare the marketplace. Extra keys the platform
    allows stand in each, which the check never reads."""
    files: dict[str, Any] = {
        f"modules/{m}/.claude-plugin/plugin.json": {"name": m, "version": "0.0.1"} for m in folders
    }
    files[MARKETPLACE_FILE] = {
        "name": tag,
        "owner": {"name": "Someone"},
        "plugins": [
            {"name": m, "source": f"./modules/{m}", "description": f"The module {m}."} for m in folders
        ],
    }
    files[SETTINGS_FILE] = {
        "permissions": {"allow": []},
        "extraKnownMarketplaces": {tag: {"source": dict(DIRECTORY_SOURCE)}},
        "enabledPlugins": {f"{m}@{tag}": True for m in folders},
    }
    return files


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


def folder_probes() -> bool:
    """`kit_module_doc.module_folders`, the kit's one listing, over every class of what can stand under
    `modules/`, in one loop, the listing having no self-test of its own (the other checks that read
    through it prove their own mapping). A probe is a throwaway `modules/` of folders each with its
    MODULE.md, folders without one, plain files, and a MODULE.md that is a folder; `modules` None leaves
    it out, "file" makes it a plain file; the folders the listing gives, or the message of its error,
    with `{root}` for the tree. The listing is handed adversarial order, entries reversed. A probe that
    fails prints what it got."""
    gone = "{root} has no modules/ directory — fix: run the check from a checkout of the kit"
    undocumented = "modules/{} has no MODULE.md — fix: restore the module document"
    # name: documented folders, folders with no MODULE.md, plain files, folders whose MODULE.md is a folder
    probes: dict[str, tuple[list[str], list[str], list[str], list[str], str | None, list[str] | str]] = {
        "a folder `.x` and a folder `_x` are skipped silently, with a MODULE.md or without": (
            [".x", "_x", "const-a"],
            [".y", "_y"],
            [],
            [],
            "dir",
            ["const-a"],
        ),
        "a plain file of modules/ is not listed, whatever its name": (
            ["const-a"],
            [],
            ["const-file", ".hidden", "zzz"],
            [],
            "dir",
            ["const-a"],
        ),
        "a folder named without `const-` is listed": (
            ["glossary", "const-a"],
            [],
            [],
            [],
            "dir",
            ["const-a", "glossary"],
        ),
        "a name that only starts like the prefix is listed": (
            ["const", "const-"],
            [],
            [],
            [],
            "dir",
            ["const", "const-"],
        ),
        "the folders are sorted by name, whatever order the folder lists": (
            ["const-b", "const-c", "const-a", "x-d"],
            [],
            [],
            [],
            "dir",
            ["const-a", "const-b", "const-c", "x-d"],
        ),
        "a folder without its MODULE.md is an error naming the folder": (
            ["const-a"],
            ["const-ghost"],
            [],
            [],
            "dir",
            undocumented.format("const-ghost"),
        ),
        "the first folder without its MODULE.md, in sorted order, is named": (
            ["const-a"],
            ["const-z", "const-b"],
            [],
            [],
            "dir",
            undocumented.format("const-b"),
        ),
        "a MODULE.md that is a folder is no document": (
            [],
            [],
            [],
            ["const-a"],
            "dir",
            undocumented.format("const-a"),
        ),
        "no modules/ directory is an error naming the tree": ([], [], [], [], None, gone),
        "modules/ a plain file is no directory": ([], [], [], [], "file", gone),
    }
    ok = True
    for name, (documented, bare, files, trap, modules, wanted) in probes.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            if modules == "file":
                (root / "modules").write_text("not a folder\n", encoding="utf-8")
            elif modules == "dir":
                (root / "modules").mkdir()
            for folder in (*documented, *bare, *trap):
                (root / "modules" / folder).mkdir()
            for folder in documented:
                (root / "modules" / folder / "MODULE.md").write_text("A module.\n", encoding="utf-8")
            for folder in trap:
                (root / "modules" / folder / "MODULE.md").mkdir()
            for file in files:
                (root / "modules" / file).write_text("not a folder\n", encoding="utf-8")
            try:
                with listed_in_reverse():
                    got: list[str] | str = [d.name for d in module_folders(root)]
            except DocumentError as bad:
                got = str(bad)
            want = wanted.replace("{root}", str(root)) if isinstance(wanted, str) else wanted
        if got != want:
            ok = False
            print(f"        {name}: got {got!r}, wanted {want!r}")
    return ok


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
        "a span in the kind cell is read like one in any other cell": (
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
        "the mark in capitals is no mark": (
            [row(f"{explain}: Not a tree scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark with a longer last word is no mark": (
            [row(f"{explain}: not a tree scanner")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark at the end of a longer first word is no mark": (
            [row(f"{explain}: cannot a tree scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark inside parentheses is a mark": (
            [row(f"{explain} (not a tree scan)")],
            [],
            [],
        ),
        "an explain's argument that starts with `-` is a problem": (
            [row("`x --scan --command -y`: not a tree scan")],
            [],
            [(2, Fault.SPAN)],
        ),
        "an escaped bar in the span keeps it in its cell, so the unmarked flag is found": (
            [row("`x --scan --command <a\\|b>`")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "an escaped bar before the mark keeps the mark in the cell of the span": (
            [row("`x --scan --command <text>`: the a\\|b form, not a tree scan")],
            [],
            [],
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
        "no closing bar, the span in the last cell is read": (
            ["| E2 | `gate` | `x --scan`"],
            ["x"],
            [],
        ),
        "no closing bar, the span in the second and last cell is read": (["| E2 | `x --scan`"], ["x"], []),
        "no closing bar, a flag after `--scan` without the mark is a problem": (
            ["| E2 | `gate` | `x --scan --command <t>`"],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "no closing bar, a flag after `--scan` with the mark is no scan and no problem": (
            ["| E2 | `gate` | `x --scan --command <t>`: not a tree scan"],
            [],
            [],
        ),
        "no closing bar, a span of another form in the last cell is a problem": (
            ["| E2 | `gate` | `sh x.sh --scan`"],
            [],
            [(2, Fault.SPAN)],
        ),
        "a row that closes with a bar reads its last cell as before": (
            ["| E2 | `gate` | `x --scan` |", "| E3 | `gate` | `y --scan` |  "],
            ["x", "y"],
            [],
        ),
        "a one-cell line with no closing bar is a row, `E2` its first cell": (["| E2"], [], []),
        "a one-cell line with no closing bar, `G2`, is a first-cell problem": (
            ["| G2"],
            [],
            [(2, Fault.FIRST_CELL)],
        ),
        "a line of one bar has no cell, so no first cell": (["|"], [], [(2, Fault.FIRST_CELL)]),
        "a flag with a hyphen and a digit, with the mark, is no scan and no problem": (
            [row("`x --scan --since-2 <d>`: not a tree scan")],
            [],
            [],
        ),
        "a flag with a hyphen inside, with the mark, is no scan and no problem": (
            [row("`x --scan --a-b`: not a tree scan")],
            [],
            [],
        ),
        "a flag with a hyphen and a digit, without the mark, is an unmarked problem": (
            [row("`x --scan --since-2 <d>`")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "a `--scan` span in a first cell that is no `E<n>` is a problem and is read": (
            ["| `x --scan` | `gate` |"],
            ["x"],
            [(2, Fault.FIRST_CELL)],
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


REGISTRY_TAG = "kit-test"  # the marketplace name of the self-test's registry files, never the kit's own
MANIFEST_X = "modules/const-x/.claude-plugin/plugin.json"


def registry_case(
    scan: str,
    change: Callable[[dict[str, Any]], object],
    folders: tuple[str, ...] = ("const-x", "const-quiet"),
) -> Case:
    """A case whose registry files are the matching ones for `folders` after `change` edited them."""
    files = registry_tree(folders, REGISTRY_TAG)
    change(files)
    return Case({"x": scan}, folders=folders, files=files)


def registry_cases(scan: str) -> dict[str, tuple[Case, list[Where]]]:
    """The cases of the files that name a module, each a matching registry edited once: the findings it
    must give, in their fixed order. The registry's plugins stand in the order of its folders, const-x
    first, the folders' sorted order being const-quiet, const-x."""
    market, settings, tag = MARKETPLACE_FILE, SETTINGS_FILE, REGISTRY_TAG

    def entry(f: dict[str, Any], at: int = 0) -> dict[str, Any]:
        entries: dict[str, Any] = f[market]["plugins"][at]
        return entries

    def enabled(f: dict[str, Any]) -> dict[str, Any]:
        keys: dict[str, Any] = f[settings]["enabledPlugins"]
        return keys

    def known(f: dict[str, Any]) -> dict[str, Any]:
        declared: dict[str, Any] = f[settings]["extraKnownMarketplaces"]
        return declared

    def edit(change: Callable[[dict[str, Any]], object], wanted: list[Where]) -> tuple[Case, list[Where]]:
        return registry_case(scan, change), wanted

    def declared_as(source: object) -> Callable[[dict[str, Any]], object]:
        return lambda f: known(f)[tag].update({"source": source})

    def enabled_as(value: object) -> Callable[[dict[str, Any]], object]:
        return lambda f: enabled(f).update({f"const-x@{tag}": value})

    cases: dict[str, tuple[Case, list[Where]]] = {
        "an entry, a manifest and the settings carry the platform's other keys: allowed": edit(
            lambda f: (
                enabled(f).update({"other@elsewhere": True, "const-gone@elsewhere": False}),
                enabled(f).update({f"const-gone@{tag}-2": True, f"const-gone@x{tag}": True}),
                known(f).update({"elsewhere": {"source": {"source": "github", "repo": "a/b"}}}),
                known(f)[tag].update({"autoUpdate": True}),
                entry(f).update({"version": "9", "homepage": "https://example.org"}),
            ),
            [],
        ),
        "the marketplace renamed in all three places": (Case({"x": scan}, tag="kit-b"), []),
        "the marketplace renamed in its own file only": edit(
            lambda f: f[market].update({"name": "kit-b"}),
            [Where.SETTINGS, Where.SETTINGS, Where.KNOWN_MISSING],
        ),
        "the marketplace renamed in its file and the declaration, the enabled keys left": edit(
            lambda f: (
                f[market].update({"name": "kit-b"}),
                f[settings].update({"extraKnownMarketplaces": {"kit-b": {"source": dict(DIRECTORY_SOURCE)}}}),
            ),
            [Where.SETTINGS, Where.SETTINGS],
        ),
        "the marketplace renamed in its file and the enabled keys, the declaration left": edit(
            lambda f: (
                f[market].update({"name": "kit-b"}),
                f[settings].update(
                    {"enabledPlugins": {f"{m}@kit-b": True for m in ("const-x", "const-quiet")}}
                ),
            ),
            [Where.KNOWN_MISSING],
        ),
        "a manifest that names another plugin": edit(
            lambda f: f[MANIFEST_X].update({"name": "const-y"}), [Where.MANIFEST]
        ),
        "a manifest with no name": edit(lambda f: f[MANIFEST_X].pop("name"), [Where.MANIFEST]),
        "a manifest whose name is no string": edit(
            lambda f: f[MANIFEST_X].update({"name": 5}), [Where.MANIFEST]
        ),
        "a manifest whose name differs from the folder's in case": edit(
            lambda f: f[MANIFEST_X].update({"name": "CONST-X"}), [Where.MANIFEST]
        ),
        "a module the marketplace leaves out": edit(
            lambda f: f[market]["plugins"].pop(0), [Where.MARKETPLACE]
        ),
        "a marketplace with no entry at all": edit(
            lambda f: f[market].update({"plugins": []}), [Where.MARKETPLACE, Where.MARKETPLACE]
        ),
        "an entry whose source is another folder": edit(
            lambda f: entry(f).update({"source": "./modules/other"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose source is another module's folder": edit(
            lambda f: entry(f).update({"source": "./modules/const-quiet"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose source is an object": edit(
            lambda f: entry(f).update({"source": {"source": "github", "repo": "a/b"}}), [Where.MARKET_SOURCE]
        ),
        "an entry with no source": edit(lambda f: entry(f).pop("source"), [Where.MARKET_SOURCE]),
        "an entry whose source ends in a slash": edit(
            lambda f: entry(f).update({"source": "./modules/const-x/"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose source has no `./`": edit(
            lambda f: entry(f).update({"source": "modules/const-x"}), [Where.MARKET_SOURCE]
        ),
        "an entry with no folder": edit(
            lambda f: f[market]["plugins"].append({"name": "const-gone", "source": "./modules/const-gone"}),
            [Where.MARKET_STRAY],
        ),
        "two entries of a name with no folder are one finding": edit(
            lambda f: f[market]["plugins"].extend([{"name": "const-gone"}, {"name": "const-gone"}]),
            [Where.MARKET_STRAY],
        ),
        "two entries for one module": edit(
            lambda f: f[market]["plugins"].append(dict(entry(f))), [Where.MARKET_TWICE]
        ),
        "two entries for one module, one with another source, are one finding": edit(
            lambda f: f[market]["plugins"].append({"name": "const-x", "source": "./modules/other"}),
            [Where.MARKET_TWICE],
        ),
        "a module the settings leave out": edit(lambda f: enabled(f).pop(f"const-x@{tag}"), [Where.SETTINGS]),
        "settings with no enabledPlugins at all": edit(
            lambda f: f[settings].pop("enabledPlugins"), [Where.SETTINGS, Where.SETTINGS]
        ),
        "a key with no folder": edit(
            lambda f: enabled(f).update({f"const-gone@{tag}": True}), [Where.SETTINGS_STRAY]
        ),
        "a key with no folder, set to false": edit(
            lambda f: enabled(f).update({f"const-gone@{tag}": False}), [Where.SETTINGS_STRAY]
        ),
        "a key of the marketplace with no module name": edit(
            lambda f: enabled(f).update({f"@{tag}": True}), [Where.SETTINGS_STRAY]
        ),
        "a declaration the settings lack": edit(lambda f: known(f).pop(tag), [Where.KNOWN_MISSING]),
        "a declaration of another marketplace only": edit(
            lambda f: f[settings].update(
                {"extraKnownMarketplaces": {"elsewhere": {"source": dict(DIRECTORY_SOURCE)}}}
            ),
            [Where.KNOWN_MISSING],
        ),
        "settings with no extraKnownMarketplaces at all": edit(
            lambda f: f[settings].pop("extraKnownMarketplaces"), [Where.KNOWN_MISSING]
        ),
    }
    for what, source in {  # the declaration's source must be exactly a directory at `.`
        "a path ./x": {"source": "directory", "path": "./x"},
        "a path ./": {"source": "directory", "path": "./"},
        "no path": {"source": "directory"},
        "a github source": {"source": "github", "repo": "a/b"},
        "a key beside the two": {"source": "directory", "path": ".", "extra": 1},
        "an empty object": {},
        "a string": ".",
        "null": None,
    }.items():
        cases[f"a declaration whose source is {what}"] = edit(declared_as(source), [Where.KNOWN_SOURCE])
    cases["a declaration with no source"] = edit(lambda f: known(f)[tag].pop("source"), [Where.KNOWN_SOURCE])
    cases["a declaration that is a string"] = edit(
        lambda f: known(f).update({tag: "."}), [Where.KNOWN_SOURCE]
    )
    for what, value in {  # a module is enabled by the JSON boolean `true` and nothing else
        "false": False,
        "1": 1,
        "1.0": 1.0,
        '"true"': "true",
        "null": None,
        "a list": [True],
        "an object": {"enabled": True},
    }.items():
        cases[f"a module enabled as {what}"] = edit(enabled_as(value), [Where.SETTINGS])
    return cases


def backwards(value: Any) -> Any:
    """`value` with the keys of every object and the items of every list in reverse order."""
    if isinstance(value, dict):
        return {key: backwards(item) for key, item in reversed(list(value.items()))}
    if isinstance(value, list):
        return [backwards(item) for item in reversed(value)]
    return value


def messy_case(scan: str, reverse: bool) -> Case:
    """One tree with a finding of every kind of registry finding but the declaration's absence, over six
    folders; `reverse` writes every object's keys and every list in the opposite order, which must change
    nothing of the report."""
    market, settings, tag = MARKETPLACE_FILE, SETTINGS_FILE, REGISTRY_TAG
    folders = ("const-x", "glossary", "const-A", "const-m", "const-n", "const-s")
    files = registry_tree(folders, tag)
    files["modules/const-m/.claude-plugin/plugin.json"]["name"] = "const-y"
    files["modules/const-n/.claude-plugin/plugin.json"].pop("name")
    plugins: list[dict[str, Any]] = files[market]["plugins"]
    plugins[:] = [entry for entry in plugins if entry["name"] != "const-m"]
    for entry in plugins:
        if entry["name"] == "const-n":
            entry["source"] = {"type": "github", "repo": "a/b"}
        if entry["name"] == "const-s":
            plugins.append(dict(entry))
            break
    # six strays, written in neither their sorted order nor its reverse, nor in the order `backwards` gives
    # them: no chance order of a set is likelier than 1 in 720 to be the sorted one, so a sort holds it
    strays = ("const-gone", "const-away", "const-zed", "const-mid", "const-bar", "const-old")
    plugins += [{"name": name, "source": f"./modules/{name}"} for name in strays]
    enabled: dict[str, Any] = files[settings]["enabledPlugins"]
    enabled.update({f"const-m@{tag}": False, f"const-s@{tag}": "true", "other@elsewhere": True})
    enabled.update({f"const-gone@{tag}": True, f"const-away@{tag}": True})
    enabled.pop(f"const-n@{tag}")
    files[settings]["extraKnownMarketplaces"][tag]["source"]["path"] = "./x"
    return Case({"x": scan}, folders=folders, files=backwards(files) if reverse else files)


def strays_case(scan: str) -> Case:
    """One tree whose marketplace and settings name seven things that are no module folder: a module's
    name whose folder is missing, a plain file of a module's name, a missing folder of another name, one
    opening with `_`, one opening with `.`, a name of two path parts and the empty name; the folders that
    exist but are no module's carry a MODULE.md, the file a plain one."""
    market, settings, tag = MARKETPLACE_FILE, SETTINGS_FILE, REGISTRY_TAG
    names = ("", ".x", "_x", "a/b", "const-gone", "const-plain", "gone")
    files = registry_tree(("const-x", "const-quiet"), tag)
    files[market]["plugins"] += [{"name": name, "source": f"./modules/{name}"} for name in names]
    files[settings]["enabledPlugins"].update({f"{name}@{tag}": True for name in names})
    return Case(
        {"x": scan},
        scripts={"modules/_x/MODULE.md": False, "modules/.x/MODULE.md": False, "modules/const-plain": False},
        files=files,
    )


def broken_cases(scan: str) -> dict[str, tuple[Case, str]]:
    """The files the check cannot read, each a matching registry with one file or key spoilt: the first
    line of the BROKEN report, which names the file and how to fix it."""
    m, s, x = MARKETPLACE_FILE, SETTINGS_FILE, MANIFEST_X
    quiet = "modules/const-quiet/.claude-plugin/plugin.json"
    object_fix = "restore it as a JSON object"
    entry_fix = '{"name": …, "source": …}'

    def spoil(change: Callable[[dict[str, Any]], object]) -> Case:
        return registry_case(scan, change)

    def put(path: str, text: str | None) -> Case:  # `text`: the file's whole text, None for no file
        return spoil(lambda f: f.update({path: text}))

    def no_json(path: str) -> str:
        said = "Expecting property name enclosed in double quotes, line 1"
        return f"{path} is no JSON ({said}) — fix: {object_fix}"

    def no_object(path: str, kind: str) -> str:
        return f"{path} is no JSON object, it holds a {kind} — fix: {object_fix}"

    def no_file(path: str) -> str:
        return f"{path} is no file — fix: restore it as a JSON file holding an object"

    name_line = (
        f'{m} has no marketplace name, "name" is no non-empty string'
        " — fix: restore it, the name the kit's settings enable plugins under"
    )
    plugins_line = f'{m} has no list "plugins" — fix: restore it as a list of entries {entry_fix}'
    one_line = (
        f"{m}: entry 2 of plugins is no object with a string name — fix: write each entry as {entry_fix}"
    )

    def market(change: Callable[[dict[str, Any]], object]) -> Case:
        return spoil(lambda f: change(f[MARKETPLACE_FILE]))

    def settings(change: Callable[[dict[str, Any]], object]) -> Case:
        return spoil(lambda f: change(f[SETTINGS_FILE]))

    return {
        "a manifest that is missing": (put(x, None), no_file(x)),
        "a manifest that is no JSON": (put(x, "{ not json\n"), no_json(x)),
        "a manifest that is empty": (
            put(x, ""),
            f"{x} is no JSON (Expecting value, line 1) — fix: {object_fix}",
        ),
        "a manifest that is a list": (put(x, "[]\n"), no_object(x, "list")),
        "a manifest that is a string": (put(x, '"const-x"\n'), no_object(x, "str")),
        "a manifest that is null": (put(x, "null\n"), no_object(x, "NoneType")),
        "two manifests that are broken: the first folder in sorted order is named": (
            spoil(lambda f: f.update({x: None, quiet: "[]"})),
            no_object(quiet, "list"),
        ),
        "a manifest and the marketplace broken: the manifest is named": (
            spoil(lambda f: f.update({x: "[]", m: "[]"})),
            no_object(x, "list"),
        ),
        "a marketplace that is missing": (put(m, None), no_file(m)),
        "a marketplace that is no JSON": (put(m, "{ not json\n"), no_json(m)),
        "a marketplace that is a list": (put(m, "[]\n"), no_object(m, "list")),
        "a marketplace with no name": (market(lambda d: d.pop("name")), name_line),
        "a marketplace whose name is empty": (market(lambda d: d.update({"name": ""})), name_line),
        "a marketplace whose name is no string": (market(lambda d: d.update({"name": 5})), name_line),
        "a marketplace with no plugins": (market(lambda d: d.pop("plugins")), plugins_line),
        "a marketplace whose plugins are an object": (
            market(lambda d: d.update({"plugins": {"const-x": {}}})),
            plugins_line,
        ),
        "a marketplace whose plugins are null": (market(lambda d: d.update({"plugins": None})), plugins_line),
        "a marketplace with an entry that is a string": (
            market(lambda d: d["plugins"].__setitem__(1, "const-quiet")),
            one_line,
        ),
        "a marketplace with an entry that has no name": (
            market(lambda d: d["plugins"][1].pop("name")),
            one_line,
        ),
        "a marketplace with an entry whose name is no string": (
            market(lambda d: d["plugins"][1].update({"name": 7})),
            one_line,
        ),
        "settings that are missing": (put(s, None), no_file(s)),
        "settings that are no JSON": (put(s, "{ not json\n"), no_json(s)),
        "settings that are a list": (put(s, "[]\n"), no_object(s, "list")),
        "settings whose enabledPlugins are a list": (
            settings(lambda d: d.update({"enabledPlugins": ["const-x@kit-test"]})),
            f"{s}: enabledPlugins is no JSON object — fix: restore it as an object",
        ),
        "settings whose enabledPlugins are null": (
            settings(lambda d: d.update({"enabledPlugins": None})),
            f"{s}: enabledPlugins is no JSON object — fix: restore it as an object",
        ),
        "settings whose extraKnownMarketplaces are a string": (
            settings(lambda d: d.update({"extraKnownMarketplaces": "kit-test"})),
            f"{s}: extraKnownMarketplaces is no JSON object — fix: restore it as an object",
        ),
        "settings whose two objects are wrong: enabledPlugins is named": (
            settings(lambda d: d.update({"enabledPlugins": [], "extraKnownMarketplaces": []})),
            f"{s}: enabledPlugins is no JSON object — fix: restore it as an object",
        ),
    }


def self_test() -> int:
    """Red→green on a throwaway tree: a scan missing from the gate group, and one in a kit whose
    workflow does not read the list or names it only in a comment line or a trailing comment, are red
    with one finding each and green once listed and read;
    an extra entry is no gate; a span with a flag after `--scan` and the words is no scan; a module
    with no scan needs no entry; a scan whose entry falls into `kit` or into another module's job is
    red; a module folder the list's modules leave out, and a listed module with no folder, are red; a
    tracked kit check no entry of the gate group runs is red; the forms of the enforcement table are
    held by `form_probes`; the report of each kind of finding is its literal text with exit 2; a list
    script that fails, jobs that are no JSON list, a module document without its enforcement anchor
    or with it twice, a module folder without its document, a tree that is no repository and a git
    that cannot be run are each a teaching BROKEN line; a scan declared as `<entry>.py --scan` is held
    by its python3 line and taught by it; the files that name a module are held by `registry_cases`
    (a copy changed one at a time), the name over a whole set of names, the reports of `messy_case`
    written in order and backwards, the scans' and the list's findings of three folders in the folders'
    sorted order, and `broken_cases` (each file the check cannot read, its literal
    BROKEN line with exit 1)."""
    module_text = (
        '<a id="t9"></a>\n## 9\n\n| # | artifact | kind |\n|---|---|---|\n'
        "| E1 | hook + `check-x` (hook mode) | `gate` |\n| E2 | `check-x --scan`: all | `gate` |\n"
        "| E3 | `check-x --scan --since <date>`: the report, not a tree scan | `advisory` |\n\n"
        "A sibling's `check-y` is not this module's.\n\n<a id=\"t10\"></a>\n## 10\n\n"
        "| item | kind | rows | what it proves |\n|---|---|---|---|\n| T1 | fixture | none | x |\n\n"
        '<a id="t11"></a>\n## 11\n\n<a id="t12"></a>\n## 12\n'
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
        documents = {"const-x": case.document or module_text, "const-quiet": quiet_text, **case.documents}
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
        for path, content in (case.files or registry_tree(case.folders, case.tag)).items():
            if content is not None:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                text = content if isinstance(content, str) else json.dumps(content, indent=2)
                (root / path).write_text(text, encoding="utf-8")
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
        # the word bounds of the run match, one gate entry whose only command line is the form named
        "a name that continues past .py (check-new.py.bak) is no run of the kit check": (
            Case({"x": scan, "new": f"{run_new}.bak"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a name that continues past .py (check-new.pyc) is no run of the kit check": (
            Case({"x": scan, "new": f"{run_new}c"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a word that ends in python3 (xpython3) is no run of the kit check": (
            Case({"x": scan, "new": f"x{run_new}"}, scripts=tracked),
            [Where.CHECK],
        ),
        "an absolute python3 (/usr/bin/python3), as the code stands, is no run of the kit check": (
            Case({"x": scan, "new": f"/usr/bin/{run_new}"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a run after other commands on its line (cd x && python3 ...) is a run of the kit check": (
            Case({"x": scan, "new": f"cd x && {run_new}"}, scripts=tracked),
            [],
        ),
        "a name that follows a dot (.python3) is no run of the kit check": (
            Case({"x": scan, "new": f".{run_new}"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a name that continues with a hyphen (check-new.py-x) is no run of the kit check": (
            Case({"x": scan, "new": f"{run_new}-x"}, scripts=tracked),
            [Where.CHECK],
        ),
        "a check named with a metacharacter (check-a+b.py) is run by its own line": (
            Case({"x": scan, "new": "python3 scripts/check-a+b.py"}, scripts={"scripts/check-a+b.py": True}),
            [],
        ),
        "a check named with a metacharacter (check-a+b.py) is no run by the line of check-aab.py": (
            Case({"x": scan, "new": "python3 scripts/check-aab.py"}, scripts={"scripts/check-a+b.py": True}),
            [Where.CHECK],
        ),
    }
    cases.update(registry_cases(scan))
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
    folder_names = {  # which folder name is a module's: `const-<aspect>` in full, over the whole set of names
        "const-a": True,
        "const-a-b": True,
        "const-a1": True,
        "const-1": True,
        "const-a-b-c2": True,
        "glossary": False,
        "const-": False,
        "const": False,
        "const--a": False,
        "const-a-": False,
        "const-A": False,
        "const-a-B": False,
        "Const-a": False,
        "xconst-a": False,
        "const_a": False,
        "const-a.b": False,
        "const-ä": False,
        "const-٣": False,  # an Arabic-Indic digit is no digit here
        "const-a\n": False,  # a newline at the end is no name: `$` lets it stand
    }
    ok = True
    for folder, is_module in folder_names.items():
        # the list's names are read split on whitespace, so a name with a newline cannot stand in MODULES:
        # it is left out of `listed`, and of its findings only the name's own is held
        newline = "\n" in folder
        case = Case({"x": scan}, folders=("const-x", folder), listed=("const-x",) if newline else None)
        held = [(f.where, f.module) for f in findings_of(case) if f.where is Where.NAME or not newline]
        if held != ([] if is_module else [(Where.NAME, folder)]):
            ok = False
            print(f"        folder {folder!r}: got {held}, a module name is {is_module}")
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] only `const-<aspect>` in full is a module's name,"
        " over the whole set of names"
    )
    name_report = (  # the NAME finding's whole report, typed by hand, `{fix}` what is said after "rename"
        "RED: {m}: a module folder's name is not const-<aspect>\n"
        "  why: the kernel names every module `const-<aspect>`, lowercase kebab-case, and the CI gives a job"
        " Claude Code by that prefix\n"
        "  fix: rename modules/{m} {fix}, and name its manifest, marketplace entry, settings key and entry in"
        " MODULES the same"
    )
    to_aspect = "to a name `const-<aspect>`, lowercase letters and digits joined by single hyphens"
    renames = {  # a name `const-<name>` would be is offered only to a name that does not open with `const`
        "glossary": "to modules/const-glossary",
        "const": to_aspect,  # not `const-const`: it opens with `const`
        "constx": to_aspect,  # nor `const-constx`
        "Glossary": to_aspect,  # `const-Glossary` is no name either
        "g_s": to_aspect,
    }
    ok = True
    for folder, fix in renames.items():
        got = [
            f.render()
            for f in findings_of(Case({"x": scan}, folders=("const-x", folder)))
            if f.where is Where.NAME
        ]
        if got != [name_report.format(m=folder, fix=fix)]:
            ok = False
            print(f"        folder {folder!r}: got {got}, wanted the rename {fix!r}")
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] the rename told for a folder name offers `const-<name>` only to a name"
        " that does not open with `const` and would then be a module's name"
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
    # no anchor above the section's: it reads to the end, whether t12 is gone or t11 and t12 both
    ok = ok and scans_of(module_text.replace('<a id="t12"></a>\n', "")) == ["check-x"]
    ok = ok and scans_of(module_text[: module_text.index('<a id="t11"></a>')]) == ["check-x"]
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
        " last, is empty when the end anchor follows at once, an anchor inside prose is plain text, an"
        " anchor of another id alone on its line neither ends it nor counts as doubled, and it is read when"
        " no anchor stands above it, t11 and t12, or t12, gone"
    )
    ok = form_probes()
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the enforcement table's forms, over the whole set of probes")
    ok = folder_probes()
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] the module folders of the kit's one listing, over every class of entry"
    )
    form_text = (
        '<a id="t9"></a>\n| E1 | `check-x --scan` | `gate` |\n| G2 | `sh scripts/x.sh --scan` | `gate` |\n'
        "| E3 | `x --scan --since <date>` | `gate` |\n|  | none | `gate` |\n"
        'Declared in `y.py --scan` here.\n<a id="t10"></a>\n'
    )
    form_why = "  why: a scan the check cannot read is never held in the gate list and CI"
    form_fix = (
        "  fix: write it `<entry> --scan`, or, for a mode that is no tree scan,"
        " `<entry> --scan --<flag> …` with the words `not a tree scan` in the same cell as the span,"
        " outside the code span"
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
        " `x --scan --since <date>`, and the words `not a tree scan` are not in the cell that holds the span,"
        " outside a code span",
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
    name_why = (  # the registry reports, typed by hand: a message function cannot check itself
        "  why: the kernel names every module `const-<aspect>`, lowercase kebab-case, and the CI gives a job"
        " Claude Code by that prefix"
    )
    manifest_why = (
        "  why: a plugin installs under its manifest's name, so a name that is not the folder's splits the"
        " install from the marketplace entry and the settings key"
    )
    source_why = (
        "  why: the marketplace tells the platform where a plugin loads from, and a source that is not the"
        " module's folder loads another plugin or none"
    )
    stray_why = (
        "  why: the marketplace lists exactly the module folders, and an entry that names no module folder is"
        " a plugin no module backs"
    )
    enabled_why = (
        "  why: the kit's sessions load only the plugins its committed settings enable, and the one"
        " switch-off, `false`, belongs in a clone's .claude/settings.local.json"
    )
    key_why = (
        "  why: the settings enable exactly the module folders, and a key that names no module folder enables"
        " a plugin no module backs"
    )
    make_fix = ", or make modules/{} a module folder holding its MODULE.md"  # a stray named `const-<aspect>`
    market = ".claude-plugin/marketplace.json"
    settings = ".claude/settings.json"
    renamed = "and name its manifest, marketplace entry, settings key and entry in MODULES the same"
    messy_lines = [
        "RED: const-A: a module folder's name is not const-<aspect>",
        name_why,
        "  fix: rename modules/const-A to a name `const-<aspect>`, lowercase letters and digits joined by"
        f" single hyphens, {renamed}",
        'RED: const-m: its manifest modules/const-m/.claude-plugin/plugin.json is named "const-y", not'
        ' "const-m"',
        manifest_why,
        '  fix: set "name": "const-m" in modules/const-m/.claude-plugin/plugin.json',
        "RED: const-n: its manifest modules/const-n/.claude-plugin/plugin.json has no name, where it must be"
        ' "const-n"',
        manifest_why,
        '  fix: set "name": "const-n" in modules/const-n/.claude-plugin/plugin.json',
        "RED: glossary: a module folder's name is not const-<aspect>",
        name_why,
        f"  fix: rename modules/glossary to modules/const-glossary, {renamed}",
        "RED: const-m: the marketplace has no entry for it",
        "  why: a module the marketplace leaves out cannot be installed, by the kit's CI or by a consumer",
        f'  fix: add {{"name": "const-m", "source": "./modules/const-m"}} to plugins in {market}',
        'RED: const-n: its marketplace entry has source {"repo": "a/b", "type": "github"}, not source'
        ' "./modules/const-n"',
        source_why,
        f'  fix: set "source" to "./modules/const-n" in the entry named "const-n" of plugins in {market}',
        "RED: const-s: the marketplace has 2 entries for it",
        "  why: a plugin's name must lead to one source, and with two entries it is open which one an install"
        " reads",
        f'  fix: remove all but one entry named "const-s" from plugins in {market}, the one whose source is'
        ' "./modules/const-s"',
        *(  # the six strays of the marketplace, by name
            line
            for stray in ("away", "bar", "gone", "mid", "old", "zed")
            for line in (
                f"RED: const-{stray}: the marketplace has an entry for it, but modules/const-{stray} is no"
                " module folder",
                stray_why,
                f'  fix: remove the entry named "const-{stray}" from plugins in {market}'
                + make_fix.format(f"const-{stray}"),
            )
        ),
        'RED: const-m: the kit\'s settings set "const-m@kit-test" to false, not true',
        enabled_why,
        f'  fix: set "const-m@kit-test": true under enabledPlugins in {settings}',
        "RED: const-n: the kit's settings do not enable it",
        enabled_why,
        f'  fix: set "const-n@kit-test": true under enabledPlugins in {settings}',
        'RED: const-s: the kit\'s settings set "const-s@kit-test" to "true", not true',
        enabled_why,
        f'  fix: set "const-s@kit-test": true under enabledPlugins in {settings}',
        "RED: const-away@kit-test: the kit's settings enable it, but modules/const-away is no module folder",
        key_why,
        f'  fix: remove the key "const-away@kit-test" from enabledPlugins in {settings}'
        + make_fix.format("const-away"),
        "RED: const-gone@kit-test: the kit's settings enable it, but modules/const-gone is no module folder",
        key_why,
        f'  fix: remove the key "const-gone@kit-test" from enabledPlugins in {settings}'
        + make_fix.format("const-gone"),
        "RED: kit-test: the kit's settings declare the marketplace with source"
        ' {"path": "./x", "source": "directory"}, not source {"source": "directory", "path": "."}',
        "  why: the kit loads its own modules from its own folder, so any other source loads another"
        " marketplace or none",
        f'  fix: set the source of "kit-test" under extraKnownMarketplaces in {settings} to'
        ' {"source": "directory", "path": "."}',
        "RED: 19 finding(s) — 6 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    known_why = (
        "  why: a session finds the kit's plugins only through a marketplace its settings declare, and the"
        " enabled keys name it"
    )
    absent_lines = [
        'RED: const-quiet: its marketplace entry has no source, not source "./modules/const-quiet"',
        source_why,
        '  fix: set "source" to "./modules/const-quiet" in the entry named "const-quiet" of plugins in'
        f" {market}",
        "RED: const-quiet: the kit's settings do not enable it",
        enabled_why,
        f'  fix: set "const-quiet@kit-test": true under enabledPlugins in {settings}',
        "RED: const-x: the kit's settings do not enable it",
        enabled_why,
        f'  fix: set "const-x@kit-test": true under enabledPlugins in {settings}',
        "RED: kit-test: the kit's settings do not declare the marketplace under extraKnownMarketplaces",
        known_why,
        '  fix: add "kit-test": {"source": {"source": "directory", "path": "."}} under'
        f" extraKnownMarketplaces in {settings}",
        "RED: 4 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    declared_source_lines = [
        "RED: kit-test: the kit's settings declare the marketplace with no source, not source"
        ' {"source": "directory", "path": "."}',
        "  why: the kit loads its own modules from its own folder, so any other source loads another"
        " marketplace or none",
        f'  fix: set the source of "kit-test" under extraKnownMarketplaces in {settings} to'
        ' {"source": "directory", "path": "."}',
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
        green_files = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
        # a key of another marketplace stands and is no enabled plugin of the kit: the count has two
        green_files[SETTINGS_FILE]["enabledPlugins"]["other@elsewhere"] = True
        build(root, Case({"x": scan, "new": run_new}, scripts=tracked, files=green_files))
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    green_line = (
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job, the list's"
        " modules are the module folders, each named const-<aspect> and by its manifest, listed once in the"
        " marketplace and enabled in the kit's settings, which declare the marketplace, neither list filters"
        " a runner's items, and every kit check is run by an entry of the gate group — 2 module document(s)"
        " examined, 1 declared scan(s), 1 kit check(s), 2 marketplace plugin(s), 2 enabled plugin(s)"
    )
    ok = code == EXIT_GREEN and printed.getvalue().splitlines() == [green_line]
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of a kit whose checks all run is its literal green line")
    if not ok:
        print(printed.getvalue())

    scan_why = (
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs"
    )
    missing_why = "  why: a module the list leaves out is never installed, run, linted or typed in CI"
    ordered_lines = [  # the scans' findings by folder, then the list's, `const-z` being no scan's
        "RED: const-x: its scan `check-x --scan` is not in the gate list",
        scan_why,
        "  fix: add an entry to the gate group of scripts/gate-list.sh that runs"
        " `sh modules/const-x/scripts/check-x.sh --scan`",
        "RED: const-y: its scan `check-w --scan` is not in the gate list",
        scan_why,
        "  fix: add an entry to the gate group of scripts/gate-list.sh that runs"
        " `sh modules/const-y/scripts/check-w.sh --scan`",
        *(
            line
            for m in ("x", "y", "z")
            for line in (
                f"RED: const-{m}: the list lacks its entries `install-const-{m}`, `fixtures-const-{m}`,"
                f" `lint-const-{m}`, `types-const-{m}`",
                missing_why,
                f"  fix: add `const-{m}` to MODULES in scripts/gate-list.sh, which gives each module its"
                " install, fixtures, lint and types entries",
            )
        ),
        "RED: 5 finding(s) — 3 module document(s) examined, 2 declared scan(s), 0 kit check(s)",
    ]
    without_quiet = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
    without_quiet[MARKETPLACE_FILE]["plugins"].pop(1)  # const-quiet: the marketplace leaves it out
    kinds_lines = [  # the list's modules, then the registry files, then the item filters, then the kit checks
        "RED: const-quiet: the list lacks its entries `install-const-quiet`, `fixtures-const-quiet`,"
        " `lint-const-quiet`, `types-const-quiet`",
        missing_why,
        "  fix: add `const-quiet` to MODULES in scripts/gate-list.sh, which gives each module its install,"
        " fixtures, lint and types entries",
        "RED: const-quiet: the marketplace has no entry for it",
        "  why: a module the marketplace leaves out cannot be installed, by the kit's CI or by a consumer",
        f'  fix: add {{"name": "const-quiet", "source": "./modules/const-quiet"}} to plugins in {market}',
        *filter_lines[:-1],
        "RED: scripts/check-new.py is run by no entry of the gate group",
        "  why: a kit check no entry runs is never run in CI, and its green says nothing",
        "  fix: add an entry to GATES in scripts/gate-list.sh and an arm in commands() that runs"
        f" `{run_new}`, with its `--self-test` where it has one",
        "RED: 4 finding(s) — 2 module document(s) examined, 1 declared scan(s), 1 kit check(s)",
    ]
    strays_lines = [  # typed by hand; a name that no folder can bear has the removal for its one fix
        "RED: : the marketplace has an entry for it, but modules/ is no module folder",
        stray_why,
        f'  fix: remove the entry named "" from plugins in {market}',
        "RED: .x: the marketplace has an entry for it, but modules/.x is no module folder",
        stray_why,
        f'  fix: remove the entry named ".x" from plugins in {market}',
        "RED: _x: the marketplace has an entry for it, but modules/_x is no module folder",
        stray_why,
        f'  fix: remove the entry named "_x" from plugins in {market}',
        "RED: a/b: the marketplace has an entry for it, but modules/a/b is no module folder",
        stray_why,
        f'  fix: remove the entry named "a/b" from plugins in {market}',
        "RED: const-gone: the marketplace has an entry for it, but modules/const-gone is no module folder",
        stray_why,
        f'  fix: remove the entry named "const-gone" from plugins in {market}'
        + make_fix.format("const-gone"),
        "RED: const-plain: the marketplace has an entry for it, but modules/const-plain is no module folder",
        stray_why,
        f'  fix: remove the entry named "const-plain" from plugins in {market}'
        + make_fix.format("const-plain"),
        "RED: gone: the marketplace has an entry for it, but modules/gone is no module folder",
        stray_why,
        f'  fix: remove the entry named "gone" from plugins in {market}',
        "RED: .x@kit-test: the kit's settings enable it, but modules/.x is no module folder",
        key_why,
        f'  fix: remove the key ".x@kit-test" from enabledPlugins in {settings}',
        "RED: @kit-test: the kit's settings enable it, but modules/ is no module folder",
        key_why,
        f'  fix: remove the key "@kit-test" from enabledPlugins in {settings}',
        "RED: _x@kit-test: the kit's settings enable it, but modules/_x is no module folder",
        key_why,
        f'  fix: remove the key "_x@kit-test" from enabledPlugins in {settings}',
        "RED: a/b@kit-test: the kit's settings enable it, but modules/a/b is no module folder",
        key_why,
        f'  fix: remove the key "a/b@kit-test" from enabledPlugins in {settings}',
        "RED: const-gone@kit-test: the kit's settings enable it, but modules/const-gone is no module folder",
        key_why,
        f'  fix: remove the key "const-gone@kit-test" from enabledPlugins in {settings}'
        + make_fix.format("const-gone"),
        "RED: const-plain@kit-test: the kit's settings enable it, but modules/const-plain is no module"
        " folder",
        key_why,
        f'  fix: remove the key "const-plain@kit-test" from enabledPlugins in {settings}'
        + make_fix.format("const-plain"),
        "RED: gone@kit-test: the kit's settings enable it, but modules/gone is no module folder",
        key_why,
        f'  fix: remove the key "gone@kit-test" from enabledPlugins in {settings}',
        "RED: 14 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    for name, case, lines in (
        (
            "a marketplace entry and a settings key naming a module's missing folder or plain file, another"
            " missing folder, `_x`, `.x`, `a/b` or nothing, each told by the literal why and fix — the"
            " folder offered only to a module's name",
            strays_case(scan),
            strays_lines,
        ),
        (
            "every kind of finding about the files that name a module, written in order",
            messy_case(scan, reverse=False),
            messy_lines,
        ),
        (
            "the same findings, every object's keys and every list written backwards",
            messy_case(scan, reverse=True),
            messy_lines,
        ),
        (
            "the declaration and the enabled keys missing, an entry with no source",
            registry_case(
                scan,
                lambda f: (
                    f[SETTINGS_FILE].pop("enabledPlugins"),
                    f[SETTINGS_FILE].update({"extraKnownMarketplaces": {"elsewhere": {}}}),
                    f[MARKETPLACE_FILE]["plugins"][1].pop("source"),
                ),
            ),
            absent_lines,
        ),
        (
            "findings of three folders written in the opposite order, the scans' and the list's together",
            Case(
                {"other": "true"},
                folders=("const-z", "const-y", "const-x"),
                listed=(),
                documents={"const-y": module_text.replace("check-x", "check-w")},
            ),
            ordered_lines,
        ),
        (
            "a list's module, a marketplace entry, an item filter and a kit check, in the order of the kinds",
            Case(
                {"x": scan},
                workflow=f"{reads}  filtered:\n    run: python3 modules/const-x/tests/run.py --item 3\n",
                listed=("const-x",),
                scripts=tracked,
                files=without_quiet,
            ),
            kinds_lines,
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed), listed_in_reverse():
                code = report(*check_kit(root))
        ok = code == EXIT_RED and printed.getvalue().splitlines() == lines
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the report of {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())
    no_source = Finding("kit-test", Where.KNOWN_SOURCE, said="no source").render()
    ok = no_source == "\n".join(declared_source_lines)
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of a declaration with no source is its literal text")
    if not ok:
        print(no_source)

    blocks: list[list[str]] = [[]]  # the document cut before each section anchor
    for line in module_text.splitlines(keepends=True):
        if re.fullmatch(r'<a id="t\d+"></a>', line.strip()):
            blocks.append([])
        blocks[-1].append(line)
    order = [block[0].strip() for block in blocks[1:]]
    at10, at11 = order.index('<a id="t10"></a>') + 1, order.index('<a id="t11"></a>') + 1
    blocks[at10], blocks[at11] = blocks[at11], blocks[at10]  # the sections t11 and t10 trade places
    swapped = "".join("".join(block) for block in blocks)
    with tempfile.TemporaryDirectory() as tmp:  # t11 before t10: BROKEN; the fix applied, by number: read
        root = Path(tmp).resolve()
        build(root, Case({"x": scan}, document=swapped))
        try:
            check_kit(root)
            before = None
        except Broken as bad:
            before = str(bad)
        blocks[1:] = sorted(blocks[1:], key=lambda block: int(re.findall(r"\d+", block[0])[0]))  # the fix
        build_text = "".join("".join(block) for block in blocks)
        (root / "modules/const-x/MODULE.md").write_text(build_text, encoding="utf-8")
        ok = before is not None and "the anchor after" in before
        ok = ok and build_text == module_text and check_kit(root)[0] == []
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] a document whose t11 section stands before t10, put in the"
        " template's order as the fix says, is read"
    )
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
        (
            "a module document without its end anchor, t11 and t12 standing",
            "NO-T10",
            'modules/const-x/MODULE.md has no anchor <a id="t10"></a> after <a id="t9"></a>',
        ),
        (
            "a module document whose t11 anchor stands before t10",
            "T11-BEFORE-T10",
            'modules/const-x/MODULE.md: the anchor after <a id="t9"></a> is <a id="t11"></a>, not'
            ' <a id="t10"></a> — fix: put the sections in the template\'s order, t1 to t12, each anchor'
            " alone on the line above its section's heading",
        ),
        (
            "a module document whose t9 anchor is its last",
            "T9-LAST",
            'modules/const-x/MODULE.md: no anchor follows <a id="t9"></a>, and <a id="t10"></a> stands'
            " before it — fix: put the sections in the template's order, t1 to t12",
        ),
        ("a module folder without its document", "NO-DOC", "modules/empty has no MODULE.md"),
        (
            "a tree with no modules/",
            "NO-MODULES",
            "has no modules/ directory — fix: run the check from a checkout of the kit",
        ),
        ("a tree that is no git repository", "NO-REPO", "git ls-files scripts exited"),
        (  # the folder around the tree is a repository: its index is never read for the kit's
            "a tree that is no git repository, inside a folder that is one",
            "NESTED-NO-REPO",
            "git ls-files scripts exited",
        ),
        ("a git that cannot be run", "NO-GIT", "git cannot be run"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            if change == "NESTED-NO-REPO":  # the temp folder is a repository, the kit tree a folder in it
                subprocess.run(["git", "init", "-q"], cwd=root, check=True)
                root = root / "kit"
                root.mkdir()
            build(root, Case({"x": scan}, repo=change not in ("NO-REPO", "NESTED-NO-REPO")))
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
            if change in ("T9-ON-HEADING", "T9-TWICE", "T10-TWICE", "NO-T10", "T11-BEFORE-T10", "T9-LAST"):
                broken_text = {
                    "T9-ON-HEADING": module_text.replace('<a id="t9"></a>\n## 9', '## 9 <a id="t9"></a>'),
                    "T9-TWICE": module_text.replace("## 9\n", '## 9\n<a id="t9"></a>\n', 1),
                    "T10-TWICE": module_text.replace("| E2 |", '<a id="t10"></a>\n| E2 |', 1),
                    "NO-T10": module_text.replace('<a id="t10"></a>\n', ""),
                    "T9-LAST": module_text.replace('<a id="t9"></a>\n', "") + '<a id="t9"></a>\n',
                    "T11-BEFORE-T10": module_text.replace('<a id="t10"></a>\n', "@@")
                    .replace('<a id="t11"></a>\n', '<a id="t10"></a>\n')
                    .replace("@@", '<a id="t11"></a>\n'),
                }[change]
                (root / "modules/const-x/MODULE.md").write_text(broken_text, encoding="utf-8")
            if change == "NO-DOC":
                (root / "modules/empty").mkdir()
            if change == "NO-MODULES":
                shutil.rmtree(root / "modules")
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
    unreadable = broken_cases(scan)
    for name, (case, line) in unreadable.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                code = run(root)
        lines = [f"BROKEN: {line}", "BROKEN: the check could not run — 0 module documents examined"]
        ok = code == EXIT_BROKEN and printed.getvalue().splitlines() == lines
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is its literal BROKEN line, exit 1")
        if not ok:
            print(printed.getvalue())
    total = len(cases) + len(unreadable) + 29 + 7
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
    if not args.self_test:
        return run(KIT)
    try:
        return self_test()
    except Broken as broken:
        return broken_report(broken)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
