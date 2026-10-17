#!/usr/bin/env python3
"""Kit check: every module has a passing eval receipt for the files it has now (decision
dec-0093-module-evals-with-local-receipts).

The receipts stand in scripts/eval-receipts.json, written by scripts/run-evals.py on the login of the person
who runs the evals; `kit_evals` defines the file, the eval hash and the model pin. For each module folder,
the check is red when:
  the module has no entry;
  the entry's hash is not the module's eval hash now, a file a session loads, or a case, having changed since
  the run;
  the entry's Claude Code version is not the one scripts/claude-code.version pins;
  the entry's model is not the one scripts/eval-model names;
  the entry's last attempt did not pass, or there is none.
An entry for a name that is no module folder is red too. The check holds that a passing run was declared
for the files as they are, never that it ran: the run uses a model and a login that CI does not have. A
module whose receipt is stale owes a local run before the merge, `python3 scripts/run-evals.py --token-file
<file> --module <module>`, and the receipts file it writes, committed.

Modes:  no arguments   check the kit;
        --self-test    prove the check on throwaway kits: a current receipt green; an edit of a skill, of a
                       script, of a case and of a file a link leads to each a finding; an edit of MODULE.md,
                       README.md, INSTALL.md, a test and a tracked result left out, green; a missing entry,
                       an entry for no module, another version, another model, no attempt, a failed last
                       attempt and a last attempt that ran no case each a finding; the report of one
                       finding as literal lines with exit 2; a receipts file that is no JSON, a model file
                       that is no model id and a link that leads out of the kit each a BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from kit_evals import (
    RECEIPTS,
    Attempt,
    EvalError,
    Receipt,
    eval_hash,
    eval_model,
    read_receipts,
    write_receipts,
)
from kit_module_doc import CLAUDE_PIN, DocumentError, module_folders, pinned_claude

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
WHY = (
    "a module's skills and start rules reach the model only as a run shows, and the receipt is the kit's"
    " record that a passing run was made for the files as they are"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    module: str
    what: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.module}: {self.what}\n  why: {WHY}\n  fix: {self.fix}"


def run_fix(module: str) -> str:
    return (
        f"run python3 scripts/run-evals.py --token-file <file> --module {module},"
        f" then commit {RECEIPTS}"
    )


def judge(module: str, receipt: Receipt | None, now: str, claude: str, model: str) -> list[Finding]:
    """The findings of one module's receipt against its eval hash `now` and the pins."""
    if receipt is None:
        return [Finding(module, f"has no eval receipt in {RECEIPTS}", run_fix(module))]
    found: list[Finding] = []
    if receipt.hash != now:
        found.append(
            Finding(
                module,
                f"the receipt names {receipt.hash},"
                f" but the files a session loads and the cases hash to {now}",
                run_fix(module),
            )
        )
    if receipt.claude != claude:
        found.append(
            Finding(
                module,
                f"the receipt was made on Claude Code {receipt.claude}, not the pinned {claude}",
                run_fix(module),
            )
        )
    if receipt.model != model:
        found.append(
            Finding(
                module, f"the receipt was made on {receipt.model}, not the pinned {model}", run_fix(module)
            )
        )
    last: Attempt | None = receipt.attempts[-1] if receipt.attempts else None
    if last is None:
        found.append(Finding(module, "the receipt holds no attempt", run_fix(module)))
    elif not last.passing:
        found.append(
            Finding(
                module,
                f"the last attempt, at {last.at}, passed {last.passed} of {last.cases} case(s)",
                "fix the rule, skill or case the failing case names at its cause, commit, then "
                + run_fix(module),
            )
        )
    return found


def check(root: Path) -> tuple[list[Finding], int]:
    try:
        modules = [m.name for m in module_folders(root)]
        claude = pinned_claude(root)
        model = eval_model(root)
        receipts = read_receipts(root)
        hashes = {m: eval_hash(root, m) for m in modules}
    except (DocumentError, EvalError) as bad:
        raise Broken(str(bad)) from bad
    findings = [f for m in modules for f in judge(m, receipts.get(m), hashes[m], claude, model)]
    findings += [
        Finding(
            name,
            f"has an entry in {RECEIPTS} but no module folder",
            f"remove the entry of {name} from {RECEIPTS}",
        )
        for name in sorted(set(receipts) - set(modules))
    ]
    return findings, len(modules)


def report(findings: list[Finding], modules: int) -> int:
    counts = f"{modules} module(s) examined against {RECEIPTS}"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every module has a passing eval receipt for its files — {counts}")
    return EXIT_GREEN


Act = Callable[[Path], None]


def git_quiet(root: Path, *args: str) -> None:
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, check=True)


def make_kit(tmp: Path) -> Path:
    """A throwaway kit: one module const-x with a skill, a script, a test, a document, a case, a result and a
    link to shared code; the pins; and a git repository that tracks all of it, the result added by force, so
    that its exclusion from the hash is held."""
    root = tmp / "kit"
    files = {
        "modules/const-x/MODULE.md": "# const-x\n",
        "modules/const-x/README.md": "# const-x\n",
        "modules/const-x/INSTALL.md": "# install\n",
        "modules/const-x/skills/s/SKILL.md": "skill\n",
        "modules/const-x/scripts/start.sh": "echo rule\n",
        "modules/const-x/tests/test_x.py": "pass\n",
        "modules/const-x/evals/load/case.yaml": "name: load\n",
        "shared/const_gate/core.py": "x = 1\n",
        "scripts/eval-model": "claude-opus-5-5\n",
        CLAUDE_PIN: "2.1.282\n",
        ".gitignore": "evals/results/\n",
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
    (root / "modules/const-x/scripts/const_gate").symlink_to("../../../shared/const_gate")
    (root / "modules/const-x/evals/results").mkdir(parents=True)
    (root / "modules/const-x/evals/results/r.json").write_text("{}\n", encoding="utf-8")
    git_quiet(root, "init", "-q")
    git_quiet(root, "add", "-A")
    git_quiet(
        root, "add", "-f", "modules/const-x/evals/results/r.json"
    )  # tracked, so that its exclusion is held
    passing = Attempt("2026-10-16T00:00:00Z", 1, 1, 1.0)
    write_receipts(
        root, {"const-x": Receipt(eval_hash(root, "const-x"), "2.1.282", "claude-opus-5-5", (passing,))}
    )
    return root


def edit(path: str, text: str = "changed\n") -> Act:
    def act(root: Path) -> None:
        (root / path).write_text(text, encoding="utf-8")

    return act


def with_receipt(
    *, claude: str | None = None, model: str | None = None, attempts: tuple[Attempt, ...] | None = None
) -> Act:
    def act(root: Path) -> None:
        r = read_receipts(root)["const-x"]
        changed = Receipt(
            r.hash,
            r.claude if claude is None else claude,
            r.model if model is None else model,
            r.attempts if attempts is None else attempts,
        )
        write_receipts(root, {"const-x": changed})

    return act


def no_entry(root: Path) -> None:
    write_receipts(root, {})


def extra_entry(root: Path) -> None:
    receipts = read_receipts(root)
    write_receipts(root, receipts | {"const-y": receipts["const-x"]})


def link_out(outside: Path) -> Act:
    def act(root: Path) -> None:
        link = root / "modules/const-x/scripts/const_gate"
        link.unlink()
        link.symlink_to(outside)

    return act


def self_test() -> int:
    """Red→green on throwaway kits, one per case."""
    failing = (Attempt("2026-10-16T00:00:00Z", 1, 1, 1.0), Attempt("2026-10-16T01:00:00Z", 2, 1, 0.5))
    cases: dict[str, tuple[Act, list[str]]] = {
        "a current receipt is green": (edit("modules/const-x/scripts/start.sh", "echo rule\n"), []),
        "an edited skill is a finding": (edit("modules/const-x/skills/s/SKILL.md"), ["const-x"]),
        "an edited script is a finding": (edit("modules/const-x/scripts/start.sh"), ["const-x"]),
        "an edited file behind a link is a finding": (edit("shared/const_gate/core.py"), ["const-x"]),
        "an edited case is a finding": (edit("modules/const-x/evals/load/case.yaml"), ["const-x"]),
        "an edited MODULE.md is green": (edit("modules/const-x/MODULE.md"), []),
        "an edited test is green": (edit("modules/const-x/tests/test_x.py"), []),
        "an edited README.md is green": (edit("modules/const-x/README.md"), []),
        "an edited INSTALL.md is green": (edit("modules/const-x/INSTALL.md"), []),
        "an edited result, tracked, is green": (edit("modules/const-x/evals/results/r.json", "[]\n"), []),
        "a missing entry is a finding": (no_entry, ["const-x"]),
        "an entry for no module is a finding": (extra_entry, ["const-y"]),
        "another Claude Code version is a finding": (with_receipt(claude="2.1.251"), ["const-x"]),
        "another model is a finding": (with_receipt(model="claude-haiku-5-5"), ["const-x"]),
        "a failed last attempt is a finding": (with_receipt(attempts=failing), ["const-x"]),
        "no attempt is a finding": (with_receipt(attempts=()), ["const-x"]),
        "a last attempt that ran no case is a finding": (
            with_receipt(attempts=(Attempt("2026-10-16T02:00:00Z", 0, 0, 0.0),)),
            ["const-x"],
        ),
    }
    failed = 0
    for name, (act, wanted) in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = make_kit(Path(tmp))
            act(root)
            got = [f.module for f in check(root)[0]]
        ok = got == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        got {got}")
    with tempfile.TemporaryDirectory() as tmp:
        root = make_kit(Path(tmp))
        with_receipt(model="claude-haiku-5-5")(root)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check(root))
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: the receipt was made on claude-haiku-5-5, not the pinned claude-opus-5-5",
        f"  why: {WHY}",
        "  fix: run python3 scripts/run-evals.py --token-file <file> --module const-x, then commit"
        " scripts/eval-receipts.json",
        "RED: 1 finding(s) — 1 module(s) examined against scripts/eval-receipts.json",
    ]
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    broken_cases: dict[str, tuple[Callable[[Path], Act], str]] = {
        "a receipts file that is no JSON": (lambda _: edit(RECEIPTS, "{\n"), "cannot be read as JSON"),
        "a model file that is no model id": (
            lambda _: edit("scripts/eval-model", "Opus 5.5\n"),
            "is not one model id",
        ),
        "a link that leads out of the kit": (link_out, "not a file or folder of the kit"),
    }
    for name, (make, said) in broken_cases.items():
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = make_kit(Path(tmp))
            make(Path(outside))(root)
            try:
                check(root)
                ok = False
            except Broken as broken:
                ok = said in str(broken) and "fix:" in str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line")
    total = len(cases) + 1 + len(broken_cases)
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-eval-receipts", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
