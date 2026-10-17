#!/usr/bin/env python3
"""Kit tooling, never shipped in a module, and no check: run the eval cases of modules and write each run's
attempt into the receipts file (decision dec-0093-module-evals-with-local-receipts).

    python3 scripts/run-evals.py [--module <module>]... [--container --token-file <file>]

With no `--module`, every module folder. For each module, in turn:
  1. its eval files (`kit_evals.eval_files`) must all be committed, else the module is refused with the fix,
     so that the receipt names what CI checks;
  2. those files are copied, links followed, into a temporary folder, the plugin the run loads;
  3. `claude plugin eval` runs on the copy once per case, `--case <name>`, from the temporary folder,
     with `--model` from scripts/eval-model, `--runs 3 --threshold 1 --ablation none`, `--trust-plugin
     --no-publish --scaffold`, and `--allow-tools` granting those of Bash, Write and Edit that the case
     lists in its `allowed_tools`; its JSON result and report are kept in local/evals/<module>/. A Bash
     grant is asked only for a case that needs it: the eval refuses one on a machine whose Docker credential
     store holds a link it cannot exclude, and one grant in a module's run would refuse every case of it.
     The run uses the login of the person who runs this script: it counts against that account's plan or
     bill;
  4. the cases' `casesTotal` and `casesPassed` summed, and their `overallScore` weighted by cases, become
     one attempt, stamped with the time in UTC, appended to the module's entry of scripts/eval-receipts.json.
     An entry whose hash, Claude Code version or model differs from the run's is replaced by a new one. A
     partial result counts as a failed attempt.
With `--container --token-file <file>`, each case runs instead in a throwaway container of the image
scripts/eval-container/Dockerfile defines, built once as kit-evalbox:<version> with the version the kit pins,
through `docker`. The container holds no secret of the host: the module's copy is mounted read-only and the
results folder writable, and the file, which the runner never opens, reaches it as Docker's `--env-file`. The
file holds CLAUDE_CODE_OAUTH_TOKEN, a subscription token from `claude setup-token`, and must be readable by
its owner alone. Inside, the run drops the same usage-billing variables, and refuses to start unless
`claude auth status` reports a subscription login, `oauth_token` or `claude.ai`. A case that grants Bash runs
there on a machine whose Docker credential store holds links, which the eval refuses on the host.
The `claude` used is the one scripts/claude-code.version pins: the clone's `.claude-code-pinned/` from
`sh scripts/setup-claude.sh`, put first on PATH when it is there; on any other version the script refuses.
The environment of each run drops the four variables of `kit_module_doc.claude_env`, and those that would
bill the runs by usage rather than to the person's subscription: ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN and
the three that select a cloud provider, CLAUDE_CODE_USE_BEDROCK, CLAUDE_CODE_USE_VERTEX and
CLAUDE_CODE_USE_FOUNDRY. Claude Code prefers each of them over a subscription login, so a key set in the
shell would otherwise bill the runs without a word. A subscription token from `claude setup-token`,
CLAUDE_CODE_OAUTH_TOKEN, stays.

Prints one line per case and one per module, and where the results are kept.
Exit:   0 every module's attempt passed; 2 an attempt failed; 1 a module could not be run.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml
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
from kit_module_doc import DocumentError, claude_env, claude_note, module_folders, pinned_claude

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
RUNS = 3
GATED = ("Bash", "Write", "Edit")
IMAGE = "kit-evalbox"
CONTAINER_HOME = "/home/node"
SUBSCRIPTION = (
    "oauth_token",
    "claude.ai",
)  # the `authMethod` values of `claude auth status` that bill a plan
USAGE_BILLED = (  # the variables Claude Code prefers over a subscription login, each billing by usage
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
)  # the tools `claude plugin eval` grants only through --allow-tools
TURN_SECONDS = 300  # a case's default `timeout_seconds`, the bound of one run


class Broken(Exception):
    """A module could not be run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Box:
    """Where a case runs in container mode: the image and the token file Docker reads."""

    image: str
    token_file: Path


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


def granted(paths: list[Path]) -> list[str]:
    """The gated tools the cases at `paths` list, of Bash, Write and Edit, for `--allow-tools`."""
    listed: set[str] = set()
    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            tools = data["execution"]["allowed_tools"]
        except (OSError, yaml.YAMLError, KeyError, TypeError) as bad:
            raise Broken(f"{path} cannot be read as a case ({bad!r}) — fix: restore the case.yaml") from bad
        listed |= {str(t) for t in tools or []}
    return [t for t in GATED if t in listed]


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


def cases_of(module: Path) -> list[Path]:
    return sorted(p.parent for p in (module / EVALS).glob("*/case.yaml"))


def eval_argv(plugin: str, case: str, model: str, out: str, tools: list[str]) -> list[str]:
    argv = [
        "claude", "plugin", "eval", plugin, "--case", case,
        "--model", model, "--runs", str(RUNS), "--threshold", "1", "--ablation", "none",
        "--trust-plugin", "--no-publish", "--scaffold",
        "--json", f"{out}/{case}.json", "--report", f"{out}/{case}.html",
    ]  # fmt: skip
    return argv + (["--allow-tools", *tools] if tools else [])


def in_box(box: Box, copy: Path, out: Path, argv: list[str]) -> list[str]:
    """The `docker run` that runs `argv` in a throwaway container, after its guard: the usage-billing
    variables dropped, and a subscription login required."""
    accepted = " ".join(SUBSCRIPTION)
    guard = (
        f"unset {' '.join(USAGE_BILLED)}; "
        "method=$(claude auth status 2>/dev/null | python3 -c "
        '\'import json,sys; print(json.load(sys.stdin).get("authMethod", ""))\' 2>/dev/null); '
        f'case " {accepted} " in *" $method "*) ;; '
        '*) echo "not a subscription login: ${method:-none}" >&2; exit 3 ;; esac; '
        f"cp -r /plugin {CONTAINER_HOME}/{copy.name} && cd {CONTAINER_HOME} && exec {shlex.join(argv)}"
    )
    return [
        "docker", "run", "--rm", "--env-file", str(box.token_file),
        "-v", f"{copy}:/plugin:ro", "-v", f"{out}:/out", box.image, "sh", "-c", guard,
    ]  # fmt: skip


def run_case(case: Path, copy: Path, model: str, env: dict[str, str], tmp: Path, box: Box | None) -> Outcome:
    """One case of the module's copy, granted only the gated tools it lists, on the host or in the container,
    its result kept in local/."""
    out = tmp / "out"
    out.mkdir(exist_ok=True)
    tools = granted([case / "case.yaml"])
    if box is None:
        argv = eval_argv(str(copy), case.name, model, str(out), tools)
    else:
        argv = in_box(
            box, copy, out, eval_argv(f"{CONTAINER_HOME}/{copy.name}", case.name, model, "/out", tools)
        )
    timeout = RUNS * TURN_SECONDS + 300
    try:
        done = subprocess.run(
            argv, cwd=tmp, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout,
            check=False,
        )  # fmt: skip
    except FileNotFoundError as missing:
        raise Broken(f"{argv[0]} is not installed — fix: install it and put it on PATH") from missing
    except subprocess.TimeoutExpired as late:
        raise Broken(f"the eval of case {case.name} ran past {timeout} s — fix: run it again") from late
    result = out / f"{case.name}.json"
    if not result.is_file():
        said = (done.stderr or done.stdout).strip().splitlines()
        raise Broken(
            f"the eval of case {case.name} exited {done.returncode} with no result"
            f" ({said[-1] if said else 'no output'})"
            " — fix: run `claude plugin eval` on the module by hand and read why it stops"
        )
    kept = KIT / "local" / "evals" / copy.name
    kept.mkdir(parents=True, exist_ok=True)
    for made in (result, out / f"{case.name}.html"):
        if made.is_file():
            shutil.copy2(made, kept / made.name)
    return outcome_of(result)


def ensure_image(pinned: str, env: dict[str, str]) -> str:
    """The image of the pinned version, built from scripts/eval-container/ when Docker does not have it."""
    image = f"{IMAGE}:{pinned}"
    try:
        found = subprocess.run(
            ["docker", "image", "inspect", image], env=env, capture_output=True, check=False
        )
        if found.returncode == 0:
            return image
        built = subprocess.run(
            ["docker", "build", "-q", "-t", image, "--build-arg", f"CLAUDE_CODE={pinned}",
             str(KIT / "scripts" / "eval-container")],
            env=env, capture_output=True, text=True, check=False,
        )  # fmt: skip
    except FileNotFoundError as missing:
        raise Broken("docker is not installed — fix: install Docker and put docker on PATH") from missing
    if built.returncode != 0:
        said = (built.stderr or built.stdout).strip().splitlines()
        raise Broken(
            f"docker build of {image} exited {built.returncode} ({said[-1] if said else 'no output'})"
            " — fix: start Docker, then run again"
        )
    return image


def token_box(token_file: str, image: str) -> Box:
    path = Path(token_file).expanduser()
    if not path.is_file():
        raise Broken(
            f"no token file {path} — fix: run `claude setup-token`, then save its token as one line"
            " CLAUDE_CODE_OAUTH_TOKEN=<token> in that file, chmod 600"
        )
    if path.stat().st_mode & 0o077:
        raise Broken(f"{path} is readable by others — fix: chmod 600 {path}")
    return Box(image, path)


def run_module(module: str, model: str, env: dict[str, str], box: Box | None) -> Outcome:
    root = KIT / "modules" / module
    cases = cases_of(root)
    if not cases:
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
        outcomes = [run_case(case, copy, model, env, Path(tmp), box) for case in cases]
    total = sum(o.cases for o in outcomes)
    score = sum(o.score * o.cases for o in outcomes) / total if total else 0.0
    lines = tuple(line for o in outcomes for line in o.lines)
    return Outcome(total, sum(o.passed for o in outcomes), score, lines)


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
    parser.add_argument("--container", action="store_true")
    parser.add_argument("--token-file")
    try:
        args = parser.parse_args(argv)
        if bool(args.container) != bool(args.token_file):
            raise SystemExit(2)
    except SystemExit:
        print(
            "BROKEN: misinvocation — fix: python3 scripts/run-evals.py [--module <module>]..."
            " [--container --token-file <file>]"
        )
        return EXIT_BROKEN
    kept = {k: v for k, v in claude_env(dict(os.environ)).items() if k not in USAGE_BILLED}
    env = pinned_path(kept)
    box: Box | None = None
    try:
        known = [m.name for m in module_folders(KIT)]
        model = eval_model(KIT)
        if args.container:
            pinned = pinned_claude(KIT)
            box = token_box(args.token_file, ensure_image(pinned, env))
        else:
            note = claude_note(KIT, env)
            if note.found:
                raise Broken(
                    f"claude is {note.found}, not the pinned {note.pinned}"
                    " — fix: run sh scripts/setup-claude.sh"
                )
            pinned = note.pinned
    except (DocumentError, EvalError, Broken) as bad:
        print(f"BROKEN: {bad}")
        return EXIT_BROKEN
    unknown = [m for m in args.module if m not in known]
    if unknown:
        print(f"BROKEN: no module folder {', '.join(unknown)} — fix: name one of {', '.join(known)}")
        return EXIT_BROKEN
    worst = EXIT_GREEN
    for module in args.module or known:
        try:
            outcome = run_module(module, model, env, box)
            record(module, outcome, pinned, model)
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
