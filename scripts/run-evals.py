#!/usr/bin/env python3
"""Kit tooling, never shipped in a module, and no check: run the eval cases of modules and write each run's
attempt into the receipts file (decision dec-0093-module-evals-with-local-receipts).

    python3 scripts/run-evals.py [--module <module>]...

With no `--module`, every module folder. For each module, in turn:
  1. its eval files (`kit_evals.eval_files`) must all be committed, else the module is refused with the fix,
     so that the receipt names what CI checks;
  2. those files are copied, links followed, into a temporary folder, the plugin the run loads;
  3. `claude plugin eval` runs on the copy, from the temporary folder, with `--model` from scripts/eval-model,
     `--runs 3 --threshold 1 --ablation none`, `--trust-plugin --no-publish --scaffold` and `--allow-tools
     Bash Write Edit`, its JSON result written beside the copy. The run uses the login of the person who runs
     this script: it counts against that account's plan or bill;
  4. the result's `casesTotal`, `casesPassed` and `overallScore` become one attempt, stamped with the time in
     UTC, appended to the module's entry of scripts/eval-receipts.json. An entry whose hash, Claude Code
     version or model differs from the run's is replaced by a new one. A partial result counts as a failed
     attempt.
The `claude` used is the one scripts/claude-code.version pins: the clone's `.claude-code-pinned/` from
`sh scripts/setup-claude.sh`, put first on PATH when it is there; on any other version the script refuses.
The environment of each run drops the four variables of `kit_module_doc.claude_env`.

Prints one line per case and one per module, and the path of the run's HTML report.
Exit:   0 every module's attempt passed; 2 an attempt failed; 1 a module could not be run.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from kit_evals import (
    EVALS,
    Attempt,
    EvalError,
    Receipt,
    dirty,
    eval_files,
    eval_hash,
    eval_model,
    read_receipts,
    write_receipts,
)
from kit_module_doc import DocumentError, claude_env, claude_note, module_folders

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
RUNS = 3
TURN_SECONDS = 300  # a case's default `timeout_seconds`, the bound of one run


class Broken(Exception):
    """A module could not be run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Outcome:
    cases: int
    passed: int
    score: float
    lines: tuple[str, ...]


def pinned_path(env: dict[str, str]) -> dict[str, str]:
    """`env` with the clone's pinned Claude Code first on PATH, when scripts/setup-claude.sh installed it."""
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=KIT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    pinned = Path(common).parent / ".claude-code-pinned/node_modules/.bin"
    if common and os.access(pinned / "claude", os.X_OK):
        return env | {"PATH": f"{pinned}{os.pathsep}{env.get('PATH', '')}"}
    return env


def case_count(module: Path) -> int:
    return sum(1 for _ in (module / EVALS).glob("*/case.yaml")) + sum(
        1 for _ in (module / EVALS).glob("*/prompt.md")
    )


def outcome_of(result: Path) -> Outcome:
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
        totals = data["aggregates"]
        cases, passed, score = (
            int(totals["casesTotal"]),
            int(totals["casesPassed"]),
            float(totals["overallScore"]),
        )
        lines = tuple(
            f"  case {c['name']}: score {float(c['aggregates']['score']):.2f}" for c in data.get("cases", [])
        )
        partial = bool(data.get("partial"))
    except (OSError, ValueError, KeyError, TypeError) as bad:
        raise Broken(
            f"the eval result {result} cannot be read ({bad!r})"
            " — fix: run the eval by hand and read its output"
        ) from bad
    if partial:
        reason = data.get("partialReason", "unknown")
        lines += (f"  the run is partial ({reason}): counted as failed",)
        passed = min(passed, cases - 1) if cases else 0
    return Outcome(cases, passed, score, lines)


def run_module(module: str, model: str, env: dict[str, str]) -> Outcome:
    root = KIT / "modules" / module
    if case_count(root) == 0:
        raise Broken(
            f"{module} has no eval case — fix: add one under modules/{module}/{EVALS}/<case>/case.yaml"
        )
    changed = dirty(KIT, module)
    if changed:
        raise Broken(
            f"{module} has files not committed ({', '.join(changed[:3])}) — fix: commit them, then run again,"
            " so that the receipt names what CI checks"
        )
    with tempfile.TemporaryDirectory(prefix="run-evals-") as tmp:
        copy = Path(tmp) / module
        for name, path in eval_files(KIT, module):
            (copy / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, copy / name)
        result = Path(tmp) / "result.json"
        argv = [
            "claude", "plugin", "eval", str(copy),
            "--model", model, "--runs", str(RUNS), "--threshold", "1", "--ablation", "none",
            "--trust-plugin", "--no-publish", "--scaffold", "--allow-tools", "Bash", "Write", "Edit",
            "--json", str(result), "--report", str(Path(tmp) / "report.html"),
        ]  # fmt: skip
        timeout = case_count(root) * RUNS * TURN_SECONDS + 300
        try:
            done = subprocess.run(
                argv,
                cwd=tmp,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as late:
            raise Broken(f"the eval of {module} ran past {timeout} s — fix: run it again") from late
        if not result.is_file():
            said = (done.stderr or done.stdout).strip().splitlines()
            raise Broken(
                f"the eval of {module} exited {done.returncode} with no result"
                f" ({said[-1] if said else 'no output'})"
                f" — fix: run `claude plugin eval` on the module by hand and read why it stops"
            )
        kept = KIT / "local" / "evals" / module
        kept.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result, kept / "result.json")
        if (Path(tmp) / "report.html").is_file():
            shutil.copy2(Path(tmp) / "report.html", kept / "report.html")
        return outcome_of(result)


def record(module: str, outcome: Outcome, claude: str, model: str) -> None:
    receipts = read_receipts(KIT)
    now = eval_hash(KIT, module)
    attempt = Attempt(
        datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), outcome.cases, outcome.passed, outcome.score
    )
    old = receipts.get(module)
    kept = old.attempts if old and (old.hash, old.claude, old.model) == (now, claude, model) else ()
    receipts[module] = Receipt(now, claude, model, (*kept, attempt))
    write_receipts(KIT, receipts)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="run-evals", add_help=False, allow_abbrev=False)
    parser.add_argument("--module", action="append", default=[])
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: python3 scripts/run-evals.py [--module <module>]...")
        return EXIT_BROKEN
    env = pinned_path(claude_env(dict(os.environ)))
    try:
        known = [m.name for m in module_folders(KIT)]
        note = claude_note(KIT, env)
        model = eval_model(KIT)
    except (DocumentError, EvalError) as bad:
        print(f"BROKEN: {bad}")
        return EXIT_BROKEN
    if note.found:
        print(
            f"BROKEN: claude is {note.found}, not the pinned {note.pinned}"
            " — fix: run sh scripts/setup-claude.sh"
        )
        return EXIT_BROKEN
    unknown = [m for m in args.module if m not in known]
    if unknown:
        print(f"BROKEN: no module folder {', '.join(unknown)} — fix: name one of {', '.join(known)}")
        return EXIT_BROKEN
    worst = EXIT_GREEN
    for module in args.module or known:
        try:
            outcome = run_module(module, model, env)
            record(module, outcome, note.pinned, model)
        except (Broken, EvalError) as bad:
            print(f"BROKEN: {bad}")
            worst = EXIT_BROKEN
            continue
        for line in outcome.lines:
            print(line)
        passing = outcome.cases > 0 and outcome.passed == outcome.cases
        verdict = "GREEN" if passing else "RED"
        print(
            f"{verdict}: {module}: {outcome.passed} of {outcome.cases} case(s) passed,"
            f" score {outcome.score:.2f} — report in local/evals/{module}/"
        )
        if not passing and worst == EXIT_GREEN:
            worst = EXIT_RED
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
