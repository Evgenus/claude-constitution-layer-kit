#!/usr/bin/env python3
"""Kit check: every scan a module declares stands in the kit's gate list and in its CI list.

A module declares its scan in its document's enforcement section (template §9): a code span in a
row of that section that reads exactly `<entry> --scan`, or `<entry>.py --scan` — nothing after
the flag, so an explain mode (`--scan --command …`) or a report (`--scan --since …`) is no tree
scan. For each declared scan:
  - the gate list, the numbered list of `.claude/agents/gate-list-runner.md` before its
    on-request item, has a line that runs `modules/<module>/scripts/<entry>.sh --scan` or
    `….py --scan`;
  - the CI list of step 10 of `docs/rollout-plan.md`, the sentence that opens "Then CI wiring",
    links the module's specification, `requirements.md#<module>`.
A module that declares no scan is examined and needs neither (decision
dec-0056-portability-grep-and-gate-lists).

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree: a scan missing from each list red,
                       a scan in both green, a span with more after the flag no scan, the report
                       of one finding as literal lines with exit 2, a list whose anchor moved as
                       a BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
GATE_LIST = ".claude/agents/gate-list-runner.md"
PLAN = "docs/rollout-plan.md"
LIST_OPENS = "The list, in this order:"
ON_REQUEST = re.compile(r"^\d+\. When the message asks")
STEP_10 = '<a id="s10"></a>'
CI_OPENS = "Then CI wiring"
CI_CLOSES = "All but the last"
DECLARED = re.compile(r"`([a-z][a-z0-9-]*?)(?:\.py)? --scan`")
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
            fix = (
                f"add a line `sh modules/{self.module}/scripts/{self.entry}.sh --scan`"
                f" to the list of {GATE_LIST}"
            )
        else:
            fix = f"link [`{self.module}`](requirements.md#{self.module}) in the CI list of step 10 of {PLAN}"
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


def declared_scans(text: str) -> list[str]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == '<a id="t9"></a>'), None)
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() == '<a id="t10"></a>'), len(lines)
    )
    rows = [line for line in lines[start:end] if line.startswith("| E")]
    return sorted({m[1] for row in rows for m in DECLARED.finditer(row)})


def gate_list(root: Path) -> str:
    lines = read(root, GATE_LIST).splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == LIST_OPENS), None)
    if start is None:
        raise Broken(f"{GATE_LIST} has no line '{LIST_OPENS}' — fix: restore the heading of the gate list")
    end = next((i for i in range(start, len(lines)) if ON_REQUEST.match(lines[i])), None)
    if end is None:
        raise Broken(f"{GATE_LIST} has no item 'When the message asks' — fix: restore the on-request item")
    return "\n".join(lines[start:end])


def ci_list(root: Path) -> str:
    text = read(root, PLAN)
    at = text.find(STEP_10)
    if at < 0:
        raise Broken(f"{PLAN} has no anchor s10 — fix: restore step 10's anchor")
    step = text[at : text.find("\n", at) if "\n" in text[at:] else len(text)]
    opens = step.find(CI_OPENS)
    closes = step.find(CI_CLOSES, opens)
    if opens < 0 or closes < 0:
        raise Broken(
            f"step 10 of {PLAN} has no sentence from '{CI_OPENS}' to '{CI_CLOSES}' — fix: keep the CI list in"
            " that sentence, or change this check with it"
        )
    return step[opens:closes]


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    base = root / "modules"
    if not base.is_dir():
        raise Broken(f"{root} has no modules/ directory — fix: run the check from a checkout of the kit")
    gates, ci = gate_list(root), ci_list(root)
    findings: list[Finding] = []
    modules = sorted(d.name for d in base.iterdir() if (d / "MODULE.md").is_file())
    scans = 0
    for module in modules:
        for entry in declared_scans(read(root, f"modules/{module}/MODULE.md")):
            scans += 1
            runs = re.search(
                rf"modules/{re.escape(module)}/scripts/{re.escape(entry)}\.(?:sh|py) --scan\b", gates
            )
            if runs is None:
                findings.append(Finding(module, entry, "gate list"))
            if f"requirements.md#{module})" not in ci:
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
    """Red→green on a throwaway tree: a scan missing from the gate list, and one missing from the CI
    list, are red with one finding each and green once listed; a span with more after the flag is no
    scan; a module with no scan needs no line; the report of one finding is its literal text with
    exit 2; a gate list or a plan whose anchor moved is a teaching BROKEN line."""
    module_text = (
        '<a id="t9"></a>\n## 9\n\n| # | artifact | kind |\n|---|---|---|\n'
        "| E1 | hook + `check-x` (hook mode) | `gate` |\n| E2 | `check-x --scan`: all | `gate` |\n"
        "| E3 | `check-x --scan --since <date>` | `advisory` |\n\n"
        "A sibling's `check-y --scan` is not this module's.\n\n<a id=\"t10\"></a>\n"
    )
    quiet_text = '<a id="t9"></a>\n| E1 | `explain --scan --command <text>` | `gate` |\n<a id="t10"></a>\n'
    scan = "`sh modules/const-x/scripts/check-x.sh --scan`"
    link = "[`const-x`](requirements.md#const-x)"
    listed = f"The list, in this order:\n\n1. {scan}\n2. When the message asks: x\n"
    unlisted = (
        f"The list, in this order:\n\n1. `python3 scripts/other.py`\n2. When the message asks: {scan}\n"
    )
    plan_in = f'10. <a id="s10"></a>Remote. Then CI wiring the scan of module {link}. All but the last run.\n'
    plan_out = f'10. <a id="s10"></a>Remote. Then CI wiring nothing. All but the last run. {link}\n'
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` is not in the CI list",
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs",
        "  fix: link [`const-x`](requirements.md#const-x) in the CI list of step 10 of docs/rollout-plan.md",
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s)",
    ]

    def build(root: Path, gates: str, plan: str) -> None:
        for path, text in (
            ("modules/const-x/MODULE.md", module_text),
            ("modules/const-quiet/MODULE.md", quiet_text),
            (GATE_LIST, gates),
            (PLAN, plan),
        ):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")

    def findings_of(gates: str, plan: str) -> list[Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, gates, plan)
            return check_kit(root)[0]

    failed = 0
    cases = {
        "both lists hold the scan, and the module with none needs none": (listed, plan_in, []),
        "the gate list lacks it (an on-request mention does not count)": (unlisted, plan_in, ["gate list"]),
        "the CI list lacks it (a link after the list does not count)": (listed, plan_out, ["CI list"]),
    }
    for name, (gates, plan, wanted) in cases.items():
        ok = [f.where for f in findings_of(gates, plan)] == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    ok = declared_scans(module_text) == ["check-x"] and declared_scans(quiet_text) == []
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a span with more after the flag is no scan")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        build(root, listed, plan_out)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    for name, gates, plan, said in (
        ("a gate list without its heading", "1. x\n2. When the message asks: y\n", plan_in, "has no line"),
        ("a plan whose CI sentence moved", listed, '10. <a id="s10"></a>CI later.\n', "has no sentence"),
    ):
        try:
            findings_of(gates, plan)
            ok = False
        except Broken as broken:
            ok = said in str(broken) and "fix:" in str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line")
    total = len(cases) + 4
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
