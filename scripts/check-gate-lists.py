#!/usr/bin/env python3
"""Kit check: every scan a module declares stands in the kit's gate list and in its CI list.

A module declares its scan in its document's enforcement section (template §9): a code span in a
row of that section that reads exactly `<entry> --scan`, or `<entry>.py --scan` — nothing after
the flag, so an explain mode (`--scan --command …`) or a report (`--scan --since …`) is no tree
scan. For each declared scan:
  - the gate list, the entries `sh scripts/gate-list.sh --names gate` prints, has one whose
    commands (`--show <entry>`) run `modules/<module>/scripts/<entry>.sh --scan` or `….py --scan`;
  - the CI list is every entry of that script, when the lines of `.github/workflows/gates.yml`,
    comments aside, call `sh scripts/gate-list.sh --json` and `sh scripts/gate-list.sh --run`; a
    workflow that does not leaves every declared scan out of CI. That the matrix is built from the
    one and runs the other is the workflow's own text, held by review and by its run.
Every folder under `modules/` whose name opens with neither a dot nor an underscore is a module
and must hold its `MODULE.md`. A module that declares no scan is examined and needs neither
(decisions dec-0056-portability-grep-and-gate-lists and dec-0058-ci-runs-each-check-in-parallel).

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree: a scan missing from the gate list, or
                       from a workflow that does not read the list, red; a scan in both green; an
                       extra entry no gate; a span with more after the flag no scan; the report of
                       one finding as literal lines with exit 2; a list that cannot be read, a
                       module document without its enforcement anchor and a module folder without
                       its document, each a BROKEN line; a `.py` scan held by its python3 line and
                       taught by it.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
GATE_LIST = "scripts/gate-list.sh"
WORKFLOW = ".github/workflows/gates.yml"
READS_LIST = ("sh scripts/gate-list.sh --json", "sh scripts/gate-list.sh --run")
DECLARED = re.compile(r"`([a-z][a-z0-9-]*?(?:\.py)?) --scan`")
WHY = "a scan the kit does not run holds nothing, and the lists are where the kit says what it runs"


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    module: str
    entry: str
    where: str

    def render(self) -> str:
        if self.where == "gate list":
            run = (
                f"python3 modules/{self.module}/scripts/{self.entry} --scan"
                if self.entry.endswith(".py")
                else f"sh modules/{self.module}/scripts/{self.entry}.sh --scan"
            )
            fix = f"add an entry to the gate group of {GATE_LIST} that runs `{run}`"
        else:
            fix = (
                f"let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
                f" `{READS_LIST[1]} <entry>`"
            )
        return (
            f"RED: {self.module}: its scan `{self.entry} --scan` is not in the {self.where}\n"
            f"  why: {WHY}\n"
            f"  fix: {fix}"
        )


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


def gate_list(root: Path) -> str:
    return "\n".join(listed(root, "--show", name) for name in listed(root, "--names", "gate").split())


def ci_reads_list(root: Path) -> bool:
    if not (root / WORKFLOW).is_file():
        return False
    steps = "\n".join(
        line.split(" #")[0] for line in read(root, WORKFLOW).splitlines() if not line.lstrip().startswith("#")
    )
    return all(phrase in steps for phrase in READS_LIST)


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    base = root / "modules"
    if not base.is_dir():
        raise Broken(f"{root} has no modules/ directory — fix: run the check from a checkout of the kit")
    gates, ci = gate_list(root), ci_reads_list(root)
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
            stem = entry.removesuffix(".py")
            runs = re.search(
                rf"modules/{re.escape(module)}/scripts/{re.escape(stem)}\.(?:sh|py) --scan\b", gates
            )
            if runs is None:
                findings.append(Finding(module, entry, "gate list"))
            if not ci:
                findings.append(Finding(module, entry, "CI list"))
    return findings, len(modules), scans


def report(findings: list[Finding], modules: int, scans: int) -> int:
    counts = f"{modules} module document(s) examined, {scans} declared scan(s)"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every declared scan stands in the gate list and the CI list — {counts}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on a throwaway tree: a scan missing from the gate group, and one in a kit whose
    workflow does not read the list, are red with one finding each and green once listed and read;
    an extra entry is no gate; a span with more after the flag is no scan; a module with no scan
    needs no entry; the report of one finding is its literal text with exit 2; a list script that
    fails, a module document without its enforcement anchor and a module folder without its
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
    reads = f'jobs:\n  list:\n    run: {READS_LIST[0]}\n  check:\n    run: {READS_LIST[1]} "$ENTRY"\n'
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` is not in the CI list",
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs",
        f"  fix: let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
        f" `{READS_LIST[1]} <entry>`",
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s)",
    ]

    def script(gates: dict[str, str], extras: dict[str, str]) -> str:
        arms = "".join(f"            {name}) echo '{cmd}' ;;\n" for name, cmd in {**gates, **extras}.items())
        return (
            '#!/bin/sh\ncase "$1" in\n'
            f'    --names) for n in {" ".join(gates)}; do echo "$n"; done ;;\n'
            f'    --show) case "$2" in\n{arms}            *) exit 1 ;;\n        esac ;;\n'
            "    *) exit 1 ;;\nesac\n"
        )

    def build(root: Path, gates: dict[str, str], extras: dict[str, str], workflow: str) -> None:
        for path, text in (
            ("modules/const-x/MODULE.md", module_text),
            ("modules/const-quiet/MODULE.md", quiet_text),
            (GATE_LIST, script(gates, extras)),
            (WORKFLOW, workflow),
        ):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")

    def findings_of(gates: dict[str, str], extras: dict[str, str], workflow: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, gates, extras, workflow)
            return [f.where for f in check_kit(root)[0]]

    failed = 0
    Case = tuple[dict[str, str], dict[str, str], str, list[str]]
    cases: dict[str, Case] = {
        "a gate runs the scan and CI reads the list, and the module with none needs none": (
            {"x": scan},
            {},
            reads,
            [],
        ),
        "the gate group lacks it (an extra entry does not count)": (
            {"other": "python3 scripts/other.py"},
            {"extra": scan},
            reads,
            ["gate list"],
        ),
        "the workflow names --json only in a comment line": (
            {"x": scan},
            {},
            f"# {READS_LIST[0]}\njobs:\n  one:\n    run: {READS_LIST[1]} x\n",
            ["CI list"],
        ),
        "the workflow names --run only in a trailing comment": (
            {"x": scan},
            {},
            f"jobs:\n  one:\n    run: {READS_LIST[0]}\n  two:\n    run: make # {READS_LIST[1]}\n",
            ["CI list"],
        ),
        "the workflow does not read the list": (
            {"x": scan},
            {},
            "jobs:\n  one:\n    run: make\n",
            ["CI list"],
        ),
    }
    for name, (gates, extras, workflow, wanted) in cases.items():
        ok = findings_of(gates, extras, workflow) == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    with tempfile.TemporaryDirectory() as tmp:  # a scan declared by its Python file, run by python3
        root = Path(tmp).resolve()
        build(root, {"x": scan, "p": "python3 modules/const-p/scripts/check-p.py --scan"}, {}, reads)
        text = module_text.replace("check-x", "check-p").replace("`check-p --scan`", "`check-p.py --scan`")
        (root / "modules/const-p").mkdir()
        (root / "modules/const-p/MODULE.md").write_text(text, encoding="utf-8")
        ok = check_kit(root)[0] == []
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a scan declared as `<entry>.py --scan` is held by its python3 line")
    ok = declared_scans(module_text) == ["check-x"] and declared_scans(quiet_text) == []
    ok = ok and "runs `python3 modules/const-y/scripts/check-y.py --scan`" in (
        Finding("const-y", "check-y.py", "gate list").render()
    )
    ok = ok and declared_scans(module_text.replace("`check-x --scan`", "`check-x.py --scan`")) == [
        "check-x.py"
    ]
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] a span with more after the flag is no scan;"
        " a .py entry is taught by python3"
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        build(root, {"x": scan}, {}, "jobs: {}\n")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    for name, change, said in (
        ("a list script that fails", "LIST", f"{GATE_LIST} --names gate exited"),
        ("a module document without its anchor", "NO-T9", "modules/const-x/MODULE.md has no enforcement"),
        ("a module folder without its document", "NO-DOC", "modules/empty has no MODULE.md"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, {"x": scan}, {}, reads)
            if change == "LIST":
                (root / GATE_LIST).write_text(
                    "#!/bin/sh\necho 'BROKEN: no list' >&2\nexit 1\n", encoding="utf-8"
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
    total = len(cases) + 6
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
