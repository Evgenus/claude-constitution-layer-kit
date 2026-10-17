#!/usr/bin/env python3
"""Kit tooling, never shipped in a module, and no check: run the eval cases of modules in a throwaway
container and write each run's attempt into the receipts file (decision
dec-0093-module-evals-with-local-receipts).

    python3 scripts/run-evals.py --token-file <file> [--module <module>]... [--verbose]
    python3 scripts/run-evals.py --self-test

With no `--module`, every module folder. Every case runs in a throwaway container of the image
scripts/eval-container/Dockerfile defines, built once through `docker` as kit-evalbox:<version>-<hash>, the
Claude Code version scripts/claude-code.version pins and the Dockerfile's hash; no case runs on the host,
so every receipt comes from one environment. The container holds no secret of the host: the module's copy
is mounted read-only and a results folder of the run's own writable. It runs with Docker's seccomp filter
and its /proc mask lifted
(`--security-opt seccomp=unconfined --security-opt systempaths=unconfined`), which the eval's own Bash
sandbox, bwrap, needs to start; under Docker's defaults every Bash command of a case fails before it runs.
Docker Desktop's Linux machine still separates the container from the host. The token file, which the
runner never opens, reaches it as Docker's `--env-file`; it holds CLAUDE_CODE_OAUTH_TOKEN, a subscription
token from `claude setup-token`, and must be readable by its owner alone, which the runner checks before it
asks docker for the image. For each module, in turn:
  1. its eval files (`kit_evals.eval_files`) and the image's Dockerfile must all be committed
     (`kit_evals.dirty`), else the module is refused with the fix, so that the receipt names what CI checks;
  2. its eval files are copied, links followed, into a temporary folder, the plugin the run loads;
  3. one container per case: its guard unsets the variables that would bill by usage (ANTHROPIC_API_KEY,
     ANTHROPIC_AUTH_TOKEN, CLAUDE_CODE_USE_BEDROCK, CLAUDE_CODE_USE_VERTEX, CLAUDE_CODE_USE_FOUNDRY), refuses
     to go on unless `claude --version` is the pinned version and `claude auth status` reports a
     subscription login, `oauth_token` or `claude.ai`, then runs `claude plugin eval` on the copy, `--case
     <name>`, with `--model` from scripts/eval-model, `--runs 3 --threshold 1 --ablation none`,
     `--trust-plugin --no-publish --scaffold`, and `--allow-tools` granting those of Bash, Write and Edit
     that the case lists in its `allowed_tools` — a skill or command case lists Read, Glob, Grep, Write,
     Edit, Skill and Bash, the tools a session at its moment would have, and a start-rule case only what
     its rule needs; its JSON result and report are kept in local/evals/<module>/, with each run's trace,
     which `--keep-temp` leaves in the container, copied out as <case>-trace<n>.jsonl, so that a failing run
     can be read. The runs count against the subscription's plan, never against usage;
  4. the cases' `casesTotal` and `casesPassed` summed, and their `overallScore` weighted by cases, become
     one attempt, stamped with the time in UTC, appended to the module's entry of scripts/eval-receipts.json.
     An entry whose hash, Claude Code version or model differs from the run's is replaced by a new one. A
     partial result counts as a failed attempt.
The `docker` commands run in the person's environment less the four variables of `kit_module_doc.claude_env`
and the usage-billing ones above; the container gets none of it but the token file.

Prints one line per case and one per module, and where the results are kept. With `--verbose`, which
`just evals` passes, each case first prints what the model is told and each grader's rule, then the
container's output as it comes, then for each run its verdict, the start hooks' output, every tool call and
text of the model, and each grader's verdict with the eval's explanation (`scripts/kit_eval_report.py`).
`--self-test` proves the guards without a model or docker: the token file's mode and a token file that does
not exist; the container's options (the token as an env file, never its text, the copy read-only, the
seccomp filter and the /proc mask lifted); its guard, run under sh against a fake claude (the billing
variables unset, the pinned version and a subscription login required, in that order); its command after the
guard, run under sh (the eval's exit code kept, each run's trace copied whatever its folder, and mapped to
the path the eval's result names); the environment of the docker commands; the image's tag following the pin
and the Dockerfile's text, and the image inspected and built under that tag, against a fake docker; a token
file judged before docker is asked for an image; the Dockerfile's refusal of an architecture reaching the
person with its own fix, from BuildKit's log and from the legacy builder's coloured output, and a failed
download in the same step, whose ERROR line quotes the step's command, the refusal's echo included, told
apart and given the exact build to run; the Dockerfile's refusal opening with the words the runner looks
for; the verbose story of a fixed case, run by run; a missing token file argument; the files a rename leaves
not committed; an eval image not committed; and a missing git.
The gate list runs it.
Exit:   0 every module's attempt passed; 2 an attempt failed; 1 a module could not be run.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

import yaml
from kit_eval_report import case_preamble, case_story, trace_map
from kit_evals import (
    EVAL_IMAGE,
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
from kit_module_doc import DocumentError, claude_env, module_folders, pinned_claude

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
RUNS = 3
GATED = ("Bash", "Write", "Edit")  # the tools `claude plugin eval` grants only through --allow-tools
IMAGE = "kit-evalbox"
SANDBOX_OPTIONS = (  # what the eval's own Bash sandbox, bwrap, needs to start inside the container
    "--security-opt",
    "seccomp=unconfined",
    "--security-opt",
    "systempaths=unconfined",
)
CONTAINER_HOME = "/home/node"
CONTAINER_PLUGIN = "/plugin"  # where the module's copy is mounted, read-only
CONTAINER_OUT = "/out"  # where the results folder is mounted, writable
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
)
TURN_SECONDS = 300  # a case's default `timeout_seconds`, the bound of one run
ARCH_REFUSAL = "no Vale and lychee for TARGETARCH"  # the first words of the Dockerfile's refusal
# a line of the failed step's own log that opens with the refusal, as BuildKit prints it, "#7 0.215 …" in
# its progress and "0.215 …" in its error summary, and as the legacy builder prints it once its colour is
# stripped; BuildKit's ERROR lines and the legacy builder's "Step n/n : RUN …" and "The command '…'
# returned a non-zero code" lines quote the whole command, the refusal's echo included, and so never open
# with it
COLOUR = re.compile(r"\x1b\[[0-9;]*m")  # the legacy builder colours a step's stderr on its stdout
REFUSAL_LINE = re.compile(r"(?:#\d+ )?(?:\d+(?:\.\d+)? )?" + re.escape(ARCH_REFUSAL))


class Broken(Exception):
    """A module could not be run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Box:
    """Where every case runs: the image, the version it must hold, and the token file Docker reads."""

    image: str
    pinned: str
    token_file: Path


@dataclass(frozen=True)
class Outcome:
    cases: int
    passed: int
    score: float
    lines: tuple[str, ...]


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
        "--trust-plugin", "--no-publish", "--scaffold", "--keep-temp",
        "--json", f"{out}/{case}.json", "--report", f"{out}/{case}.html",
    ]  # fmt: skip
    return argv + (["--allow-tools", *tools] if tools else [])


def guard(pinned: str, then: str) -> str:
    """The shell a container runs before its case, `then` last: the usage-billing variables unset, then the
    pinned version required (exit 4), then a subscription login (exit 3)."""
    return (
        f"unset {' '.join(USAGE_BILLED)}; "
        "version=$(claude --version 2>/dev/null | awk '{print $1; exit}'); "
        f'[ "$version" = "{pinned}" ] || '
        f'{{ echo "claude in the image is ${{version:-none}}, not the pinned {pinned}" >&2; exit 4; }}; '
        "method=$(claude auth status 2>/dev/null | python3 -c "
        '\'import json,sys; print(json.load(sys.stdin).get("authMethod", ""))\' 2>/dev/null); '
        f'case "$method" in {"|".join(SUBSCRIPTION)}) ;; '
        '*) echo "not a subscription login: ${method:-none}" >&2; exit 3 ;; esac; '
        f"{then}"
    )


def then_for(
    copy: Path,
    case: str,
    argv: list[str],
    tmp: str = "/tmp",
    out: str = CONTAINER_OUT,
    plugin: str = CONTAINER_PLUGIN,
    home: str = CONTAINER_HOME,
) -> str:
    """What a container runs after its guard: the eval, then each run's trace, which `--keep-temp` leaves in a
    read-only folder under /tmp, copied to /out as <case>-trace<n>.jsonl, and a line `<n> <its path>` in
    /out/<case>-traces.txt, the path the eval's result names for its run; the container exits with the eval's
    code. The paths are the container's; the self-test passes its own."""
    return (
        f"cp -r {shlex.quote(plugin)} {shlex.quote(f'{home}/{copy.name}')} && cd {shlex.quote(home)} && "
        f"{shlex.join(argv)}; code=$?; "
        f": > {shlex.quote(f'{out}/{case}-traces.txt')}; "
        f"find {shlex.quote(tmp)} -name trace.jsonl -path '*/out/trace.jsonl' 2>/dev/null | "
        "{ n=0; while IFS= read -r t; do n=$((n+1)); "
        f'cp "$t" {shlex.quote(out)}/{shlex.quote(case)}-trace$n.jsonl; '
        f'printf \'%s %s\\n\' "$n" "$t" >> {shlex.quote(f"{out}/{case}-traces.txt")}; done; }}; exit $code'
    )


def in_box(box: Box, copy: Path, out: Path, argv: list[str], case: str) -> list[str]:
    """The `docker run` that runs `argv` in a throwaway container, after its guard."""
    then = then_for(copy, case, argv)
    return [
        "docker", "run", "--rm", *SANDBOX_OPTIONS, "--env-file", str(box.token_file),
        "-v", f"{copy}:{CONTAINER_PLUGIN}:ro", "-v", f"{out}:{CONTAINER_OUT}",
        box.image, "sh", "-c", guard(box.pinned, then),
    ]  # fmt: skip


def streamed(argv: list[str], cwd: Path, env: dict[str, str], timeout: int) -> tuple[int, str]:
    """Run `argv`, printing each line of its output, stdout and stderr together, as it comes; its exit code
    and the whole output. Past `timeout` seconds it is killed and `subprocess.TimeoutExpired` raised."""
    said: list[str] = []
    with subprocess.Popen(
        argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
    ) as running:  # fmt: skip

        def echo() -> None:
            assert running.stdout is not None
            for line in running.stdout:
                said.append(line)
                print(f"  | {line.rstrip()}", flush=True)

        reader = threading.Thread(target=echo, daemon=True)
        reader.start()
        try:
            code = running.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            running.kill()
            raise
        reader.join()
    return code, "".join(said)


def run_case(
    case: Path, copy: Path, model: str, env: dict[str, str], tmp: Path, box: Box, verbose: bool = False
) -> Outcome:
    """One case of the module's copy, in its own container, granted only the gated tools it lists, its result
    kept in local/. With `verbose`, its prompt and graders first, the container's output as it comes, and then
    the story of each run."""
    out = tmp / "out"
    out.mkdir(exist_ok=True)
    tools = granted([case / "case.yaml"])
    plugin = f"{CONTAINER_HOME}/{copy.name}"
    argv = in_box(box, copy, out, eval_argv(plugin, case.name, model, CONTAINER_OUT, tools), case.name)
    timeout = RUNS * TURN_SECONDS + 300
    if verbose:
        print(f"── case {case.name}, {RUNS} runs on {model}", flush=True)
        for line in case_preamble(case / "case.yaml"):
            print(line, flush=True)
    try:
        if verbose:
            code, output = streamed(argv, tmp, env, timeout)
            done = subprocess.CompletedProcess(argv, code, output, "")
        else:
            done = subprocess.run(
                argv, cwd=tmp, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                timeout=timeout, check=False,
            )  # fmt: skip
    except FileNotFoundError as missing:
        raise Broken("docker is not installed — fix: install Docker and put docker on PATH") from missing
    except subprocess.TimeoutExpired as late:
        raise Broken(f"the eval of case {case.name} ran past {timeout} s — fix: run it again") from late
    result = out / f"{case.name}.json"
    if not result.is_file():
        said = (done.stderr or done.stdout).strip().splitlines()
        raise Broken(
            f"the eval of case {case.name} exited {done.returncode} with no result"
            f" ({said[-1] if said else 'no output'})"
            " — fix: the line in brackets says why: for a version not the pinned one, run docker image rm"
            f" {box.image} and run again, which rebuilds it; for a login, save a token from claude"
            " setup-token in the token file"
        )
    kept = KIT / "local" / "evals" / copy.name
    kept.mkdir(parents=True, exist_ok=True)
    for stale in kept.glob(f"{case.name}-trace*"):  # an earlier attempt's, never mixed with this one's
        stale.unlink()
    for made in (result, out / f"{case.name}.html", *sorted(out.glob(f"{case.name}-trace*"))):
        if made.is_file():
            shutil.copy2(made, kept / made.name)
    if verbose:
        for line in case_story(kept / result.name, kept / f"{case.name}-traces.txt"):
            print(line, flush=True)
    return outcome_of(result)


def image_name(pinned: str, recipe: Path = KIT / "scripts" / "eval-container" / "Dockerfile") -> str:
    """kit-evalbox:<pinned version>-<the first twelve hex digits of the Dockerfile's SHA-256>, so that a
    changed Dockerfile, or a new pin, is always built again."""
    return f"{IMAGE}:{pinned}-{hashlib.sha256(recipe.read_bytes()).hexdigest()[:12]}"


def ensure_image(pinned: str, env: dict[str, str]) -> str:
    """The image of the pinned version and the Dockerfile as it is, built from scripts/eval-container/ when
    Docker does not have it."""
    image = image_name(pinned)
    try:
        found = subprocess.run(
            ["docker", "image", "inspect", image], env=env, capture_output=True, check=False
        )
        if found.returncode == 0:
            return image
        built = subprocess.run(
            build_command(image, pinned), env=env, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as missing:
        raise Broken("docker is not installed — fix: install Docker and put docker on PATH") from missing
    if built.returncode != 0:
        # the legacy builder writes the step's output to stdout, in colour; BuildKit its log to stderr
        said = [COLOUR.sub("", line).strip() for line in f"{built.stdout}\n{built.stderr}".splitlines()]
        said = [line for line in said if line]
        refused = [line for line in said if REFUSAL_LINE.match(line)]
        if refused:  # the Dockerfile's own refusal, which the builder's last line would hide
            words = refused[-1][refused[-1].index(ARCH_REFUSAL) :]  # without the log's step and time
            raise Broken(
                f"docker build of {image} refused: {words} — fix: build with BuildKit, Docker Desktop's"
                " default (unset DOCKER_BUILDKIT, or install the docker buildx plugin), on an amd64 or"
                " arm64 machine, then run again"
            )
        errors = [line for line in said if line.startswith("ERROR") or "returned a non-zero code" in line]
        last = (errors or said or ["no output"])[-1]
        raise Broken(
            f"docker build of {image} exited {built.returncode} ({last}) — fix: start Docker if it is"
            f" stopped; else run {shlex.join(build_command(image, pinned))} and fix what its output"
            " names, then run again"
        )
    return image


def build_command(image: str, pinned: str) -> list[str]:
    """The build of the image; no -q, which would keep BuildKit from printing the failed step's log."""
    return [
        "docker", "build", "-t", image, "--build-arg", f"CLAUDE_CODE={pinned}",
        str(KIT / "scripts" / "eval-container"),
    ]  # fmt: skip


def run_env(environ: dict[str, str]) -> dict[str, str]:
    """The environment of the docker commands: the person's, less the plugin-place and usage-billing
    variables."""
    return {k: v for k, v in claude_env(environ).items() if k not in USAGE_BILLED}


def token_file(given: str) -> Path:
    path = Path(given).expanduser()
    if not path.is_file():
        raise Broken(
            f"no token file {path} — fix: run `claude setup-token`, then save its token as one line"
            " CLAUDE_CODE_OAUTH_TOKEN=<token> in that file, chmod 600"
        )
    if path.stat().st_mode & 0o077:
        raise Broken(f"{path} is readable by others — fix: chmod 600 {path}")
    return path


def run_module(module: str, model: str, env: dict[str, str], box: Box, verbose: bool = False) -> Outcome:
    root = KIT / "modules" / module
    cases = cases_of(root)
    if not cases:
        raise Broken(
            f"{module} has no eval case — fix: add one under modules/{module}/{EVALS}/<case>/case.yaml"
        )
    changed = dirty(KIT, module)
    if changed:
        raise Broken(
            f"{module}: the files its receipt names are not all committed ({', '.join(changed[:3])})"
            " — fix: commit them, then run again,"
            " so that the receipt names what CI checks"
        )
    with tempfile.TemporaryDirectory(prefix="run-evals-") as tmp:
        copy = Path(tmp) / module
        for name, path in eval_files(KIT, module):
            (copy / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, copy / name)
        outcomes = [run_case(case, copy, model, env, Path(tmp), box, verbose) for case in cases]
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


def report_story(folder: Path) -> list[str]:
    """The verbose story of a fixed case of two runs, the second failing, written into `folder`, for the
    self-test."""
    folder.mkdir(parents=True)
    (folder / "case.yaml").write_text(
        "execution:\n  prompt: Rename count_items to total_items.\ngraders:\n"
        "  - {type: tool_used, name: loads, tool: Skill, input_match: commit-before-edit}\n"
        "  - {type: regex, name: renamed, target: {source: file, path: src/a.py},"
        " pattern: def total_items}\n",
        encoding="utf-8",
    )

    def run(n: int, passed: bool, score: float, turns: int, seconds: int, renamed: str) -> dict[str, object]:
        return {
            "passed": passed, "score": score, "turns": turns, "durationSeconds": seconds, "error": None,
            "tracePath": f"/tmp/e-{n}/out/trace.jsonl",
            "graders": [
                {"name": "loads", "passed": True, "explanation": "called Skill"},
                {"name": "renamed", "passed": passed, "explanation": renamed},
            ],
        }  # fmt: skip

    result = {"cases": [{"arms": {"with": [run(1, True, 1.0, 3, 9, "matched"),
                                           run(2, False, 0.5, 2, 7, "pattern not found")]}}]}  # fmt: skip
    (folder / "c.json").write_text(json.dumps(result), encoding="utf-8")

    def said(kind: str, part: dict[str, object]) -> str:
        return json.dumps({"type": kind, "message": {"content": [part]}})

    first = [
        json.dumps({"type": "system", "subtype": "hook_response", "hook_name": "SessionStart:startup",
                    "output": "load the skill X\n"}),
        said("assistant", {"type": "tool_use", "name": "Skill",
                           "input": {"skill": "const-x:commit-before-edit"}}),
        said("assistant", {"type": "tool_use", "name": "Edit", "input": {"file_path": "src/a.py"}}),
        said("user", {"type": "tool_result", "is_error": True, "content": "no"}),
        said("assistant", {"type": "text", "text": "Renamed it."}),
    ]  # fmt: skip
    (folder / "c-trace2.jsonl").write_text("\n".join(first) + "\n", encoding="utf-8")
    (folder / "c-trace1.jsonl").write_text(said("assistant", {"type": "text", "text": "Done."}) + "\n",
                                          encoding="utf-8")  # fmt: skip
    (folder / "c-traces.txt").write_text(
        "1 /tmp/e-2/out/trace.jsonl\n2 /tmp/e-1/out/trace.jsonl\n", encoding="utf-8"
    )  # find's order, against the runs': run 1's trace was copied second
    return case_preamble(folder / "case.yaml") + case_story(folder / "c.json", folder / "c-traces.txt")


def self_test() -> int:
    """The runner's guards, run without a model or docker: the token file's mode and its absence, the
    container's options, its guard and its command after the guard, each run under sh, the environment of
    the docker commands, the image's tag, the token file judged before the image, a missing token file
    argument, the Dockerfile's refusal of an architecture from either builder and a failed download in the
    same step, told the exact build to run, the refusal's words in the Dockerfile, an eval image not
    committed, the files a rename leaves not committed, and a missing git."""
    failed, total = 0, 0

    def case(name: str, ok: bool) -> None:
        nonlocal failed, total
        total += 1
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")

    with tempfile.TemporaryDirectory() as tmp:
        token = Path(tmp) / "token.env"
        token.write_text("CLAUDE_CODE_OAUTH_TOKEN=probe-token-value\n", encoding="utf-8")
        for mode, wanted in ((0o600, True), (0o400, True), (0o640, False), (0o604, False), (0o660, False)):
            token.chmod(mode)
            try:
                token_file(str(token))
                ok = wanted
            except Broken as broken:
                ok = not wanted and f"chmod 600 {token}" in str(broken)
            case(
                f"a token file of mode {mode:o} is {'taken' if wanted else 'refused, the fix chmod 600'}", ok
            )
        try:
            token_file(str(Path(tmp) / "none.env"))
            case("a token file that does not exist is refused", False)
        except Broken as broken:
            case("a token file that does not exist is refused", "claude setup-token" in str(broken))
        token.chmod(0o600)
        box = Box("img", "2.1.282", token)
        argv = in_box(box, Path(tmp) / "const-x", Path(tmp) / "out", ["claude", "plugin", "eval"], "case")
        case(
            "the container gets the token file as --env-file, never its text",
            argv[argv.index("--env-file") + 1] == str(token) and "probe-token-value" not in " ".join(argv),
        )
        case(
            "the container lifts the seccomp filter and the /proc mask, so the eval's own sandbox can start",
            all(
                f"--security-opt {o}" in " ".join(argv)
                for o in ("seccomp=unconfined", "systempaths=unconfined")
            ),
        )
        case(
            "the container mounts the module's copy read-only", f"{Path(tmp) / 'const-x'}:/plugin:ro" in argv
        )
        case(
            "the container runs the guard before its case",
            argv[-1]
            == guard("2.1.282", then_for(Path(tmp) / "const-x", "case", ["claude", "plugin", "eval"])),
        )
        fake_bin = Path(tmp) / "bin"
        fake_bin.mkdir()
        (fake_bin / "claude").write_text(
            '#!/bin/sh\ncase "$1" in --version) echo "$FAKE_VERSION (Claude Code)" ;;'
            ' auth) m=$FAKE_METHOD; [ -n "$ANTHROPIC_API_KEY$ANTHROPIC_AUTH_TOKEN" ] && m=api_key;'
            ' echo "{\\"authMethod\\": \\"$m\\"}" ;; esac\n',
            encoding="utf-8",
        )
        (fake_bin / "claude").chmod(0o755)
        then = "echo ran " + " ".join(f"{name}=${{{name}:-unset}}" for name in USAGE_BILLED)
        unset_all = " ".join(f"{name}=unset" for name in USAGE_BILLED)
        runs = (
            ("the pinned version and a token login run the case, all five billing variables unset first",
             "2.1.282", "oauth_token", 0, f"ran {unset_all}"),
            ("a claude.ai login runs the case", "2.1.282", "claude.ai", 0, f"ran {unset_all}"),
            ("an API key login is refused with exit 3, the case not run", "2.1.282", "api_key", 3,
             "not a subscription login: api_key"),
            ("no login is refused with exit 3", "2.1.282", "", 3, "not a subscription login: none"),
            ("two accepted words together are no login", "2.1.282", "oauth_token claude.ai", 3,
             "not a subscription login"),
            ("another version is refused with exit 4, before the login is asked", "2.1.283", "api_key", 4,
             "not the pinned 2.1.282"),
        )  # fmt: skip
        for name, version, method, code, said in runs:
            env = {
                "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
                "FAKE_VERSION": version,
                "FAKE_METHOD": method,
            } | {name: "1" for name in USAGE_BILLED}
            done = subprocess.run(
                ["sh", "-c", guard("2.1.282", then)], env=env, capture_output=True, text=True, check=False
            )
            ran = "ran " in done.stdout
            case(
                f"the guard run: {name}",
                done.returncode == code and said in done.stdout + done.stderr and ran == (code == 0),
            )
        billed = {name: "x" for name in USAGE_BILLED} | {"CLAUDE_CODE_OAUTH_TOKEN": "t", "PATH": "/bin"}
        kept = run_env(billed)
        case(
            "the docker commands' environment drops every usage-billing variable",
            not set(kept) & set(USAGE_BILLED),
        )
        token.chmod(0o644)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed), mock.patch.dict(os.environ, {"PATH": tmp}):
            code = main(["--token-file", str(token)])
        case(
            "a token file readable by others is refused before docker is asked for an image",
            code == EXIT_BROKEN and "is readable by others" in printed.getvalue(),
        )
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = main(["--module", "const-x"])
        recipe = Path(tmp) / "Dockerfile"
        recipe.write_text("FROM a\n", encoding="utf-8")
        before = image_name("2.1.282", recipe)
        recipe.write_text("FROM b\n", encoding="utf-8")
        after = image_name("2.1.282", recipe)
        case(
            "the image's tag names the pin and follows the Dockerfile's text, so a new text is built again",
            before != after
            and all(re.fullmatch(r"kit-evalbox:2\.1\.282-[0-9a-f]{12}", n) for n in (before, after))
            and image_name("2.1.283", recipe) != after,
        )
        docker_bin = Path(tmp) / "docker-bin"
        docker_bin.mkdir()
        log = Path(tmp) / "docker.log"
        (docker_bin / "docker").write_text(
            f'#!/bin/sh\necho "$*" >> {log}\n[ "$1" = image ] && exit 1\nexit 0\n', encoding="utf-8"
        )
        (docker_bin / "docker").chmod(0o755)
        built = ensure_image("2.1.282", {"PATH": f"{docker_bin}{os.pathsep}{os.environ['PATH']}"})
        logged = log.read_text(encoding="utf-8").splitlines()
        case(
            "the runner inspects and builds the image under the tag with the Dockerfile's hash",
            built == image_name("2.1.282")
            and logged[0] == f"image inspect {built}"
            and logged[1]
            == f"build -t {built} --build-arg CLAUDE_CODE=2.1.282 {KIT / 'scripts/eval-container'}",
        )
        command = (
            f'process "/bin/sh -c case \\"$TARGETARCH\\" in *) echo \\"{ARCH_REFUSAL} …\\" ;; esac && curl …"'
        )
        details = "View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/x"
        legacy_command = f'\'/bin/sh -c case "$TARGETARCH" in *) echo "{ARCH_REFUSAL} …" ;; esac\''
        failures = {  # what each builder printed on a failed step, on Docker 28, each line with its stream
            "buildkit refusal": [
                (2, f"#7 0.215 {ARCH_REFUSAL} 'arm64': build with BuildKit, on amd64 or arm64"),
                (2, f"#7 ERROR: {command} did not complete successfully: exit code: 1"),
                (2, f"0.215 {ARCH_REFUSAL} 'arm64': build with BuildKit, on amd64 or arm64"),
                (2, f"ERROR: failed to build: failed to solve: {command} did not complete successfully:"
                    " exit code: 1"),
                (2, details),
            ],
            "legacy refusal": [  # the step's output on stdout, in colour; the warning and verdict on stderr
                (1, f"Step 3/3 : RUN case \"$TARGETARCH\" in *) echo \"{ARCH_REFUSAL} …\" ;; esac"),
                (1, " ---> Running in 09b32a11094f"),
                (1, f"\x1b[91m{ARCH_REFUSAL} '': build with BuildKit, on amd64 or arm64"),
                (1, "\x1b[0m"),
                (2, "DEPRECATED: The legacy builder is deprecated and will be removed in a future release."),
                (2, f"The command {legacy_command} returned a non-zero code: 1"),
            ],
            "download": [
                (2, "#7 0.512 curl: (22) The requested URL returned error: 404"),
                (2, f"#7 ERROR: {command} did not complete successfully: exit code: 2"),
                (2, f"ERROR: failed to build: failed to solve: {command} did not complete successfully:"
                    " exit code: 2"),
                (2, details),
            ],
        }  # fmt: skip
        told: dict[str, str] = {}
        for name, lines in failures.items():
            outputs = []
            for stream in (1, 2):
                output = Path(tmp) / f"build-{name.replace(' ', '-')}-{stream}.txt"
                output.write_text(
                    "".join(f"{line}\n" for to, line in lines if to == stream), encoding="utf-8"
                )
                outputs.append(f'cat "{output}" >&{stream}')
            (docker_bin / "docker").write_text(
                f'#!/bin/sh\n[ "$1" = image ] && exit 1\n{chr(10).join(outputs)}\nexit 1\n', encoding="utf-8"
            )
            try:
                ensure_image("2.1.282", {"PATH": f"{docker_bin}{os.pathsep}{os.environ['PATH']}"})
            except Broken as failure:
                told[name] = str(failure)
        for name in ("buildkit refusal", "legacy refusal"):
            case(
                f"the Dockerfile's refusal of an architecture reaches the person with its own fix: {name}",
                f"refused: {ARCH_REFUSAL} '" in told.get(name, "")
                and "Docker Desktop's default" in told.get(name, "")
                and "start Docker" not in told.get(name, ""),
            )
        download = told.get("download", "refused")
        case(
            "a download that fails in the same step is no refusal, though the builder quotes the command"
            " with the echo; the message names its ERROR line and the exact build to run",
            "refused" not in download
            and "exit code: 2)" in download
            and shlex.join(build_command(image_name("2.1.282"), "2.1.282")) in download,
        )
        case(
            "the Dockerfile's refusal opens with the words the runner looks for",
            f'echo "{ARCH_REFUSAL} ' in (KIT / EVAL_IMAGE).read_text(encoding="utf-8"),
        )
        box_root = Path(tmp) / "box root"  # a space, so that then_for's quoting is held
        for folder in ("tmp/claude-eval-a/out", "tmp/e-b/out", "out", "plugin", "home", "bin"):
            (box_root / folder).mkdir(parents=True)
        (box_root / "plugin" / "case.yaml").write_text("x\n", encoding="utf-8")
        (box_root / "bin" / "claude").write_text(
            f"#!/bin/sh\necho 1 > '{box_root}/tmp/claude-eval-a/out/trace.jsonl'\n"
            f"echo 2 > '{box_root}/tmp/e-b/out/trace.jsonl'\nexit 7\n",
            encoding="utf-8",
        )
        (box_root / "bin" / "claude").chmod(0o755)
        script = then_for(
            Path("const-x"), "load", ["claude", "plugin", "eval"], tmp=str(box_root / "tmp"),
            out=str(box_root / "out"), plugin=str(box_root / "plugin"), home=str(box_root / "home"),
        )  # fmt: skip
        boxed = subprocess.run(
            ["sh", "-c", script],
            env={"PATH": f"{box_root / 'bin'}{os.pathsep}{os.environ['PATH']}"},
            capture_output=True,
            check=False,
        )
        copied = sorted(p.name for p in (box_root / "out").glob("load-trace*.jsonl"))
        case(
            "the container keeps the eval's exit code and copies each run's trace, whatever its folder",
            boxed.returncode == 7 and copied == ["load-trace1.jsonl", "load-trace2.jsonl"],
        )
        mapped = trace_map(box_root / "out" / "load-traces.txt")
        case(
            "the container maps each copied trace to the path the eval's result names, so that a run finds"
            " its own",
            sorted(mapped) == sorted(f"{box_root}/tmp/{d}/out/trace.jsonl" for d in ("claude-eval-a", "e-b"))
            and sorted(path.name for path in mapped.values()) == copied
            and all(path.read_text(encoding="utf-8") == ("1\n" if "claude-eval-a" in key else "2\n")
                    for key, path in mapped.items()),
        )  # fmt: skip
        story = report_story(Path(tmp) / "report")
        case(
            "the verbose story names the prompt, each grader's rule, the start hook's text, the tool calls,"
            " the reply, a tool's failure, and each grader's verdict with its explanation, run by run",
            all(any(want in line for line in story) for want in (
                "Rename count_items", "regex on file src/a.py, contains: def total_items",
                "tool_used: Skill whose input matches 'commit-before-edit'", "load the skill X",
                "→ Skill const-x:commit-before-edit", "→ Edit src/a.py", "Renamed it.", "the tool failed: no",
                "run 1: passed", "run 2: FAILED", "✓ loads: called Skill", "✗ renamed: pattern not found",
            )) and story.index("  run 1: passed, score 1.00, 3 turn(s), 9 s")
            < next(n for n, line in enumerate(story) if "→ Skill" in line)
            < story.index("  run 2: FAILED, score 0.50, 2 turn(s), 7 s")
            < next(n for n, line in enumerate(story) if "Done." in line),
        )  # fmt: skip
        case(
            "a run without --token-file is a misinvocation",
            code == EXIT_BROKEN and "--token-file" in printed.getvalue(),
        )
        kit = Path(tmp) / "kit"
        (kit / "modules/const-x/skills/s").mkdir(parents=True)
        (kit / "modules/const-x/skills/s/SKILL.md").write_text("skill\n", encoding="utf-8")
        quiet = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "PATH": os.environ["PATH"]}
        for git_args in (
            ["init", "-q"],
            ["add", "-A"],
            ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
        ):
            subprocess.run(["git", *git_args], cwd=kit, env=quiet, capture_output=True, check=True)
        skill = kit / "modules/const-x/skills/s"
        (skill / "SKILL.md").rename(skill / "OTHER.md")  # a rename in the working tree, ` R` in porcelain
        subprocess.run(
            ["git", "add", "-N", "modules/const-x/skills/s/OTHER.md"],
            cwd=kit, env=quiet, capture_output=True, check=True,
        )  # fmt: skip
        with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}):
            case(
                "a rename not committed, marked in the working tree's column, names its new path and no"
                " fragment of its source",
                dirty(kit, "const-x") == ["modules/const-x/skills/s/OTHER.md"],
            )
            image = kit / "scripts/eval-container/Dockerfile"
            image.parent.mkdir(parents=True)
            image.write_text("FROM scratch\n", encoding="utf-8")
            case(
                "an eval image not committed refuses the run too, since the receipt's hash names it",
                "scripts/eval-container/Dockerfile" in dirty(kit, "const-x"),
            )
        with mock.patch.dict(os.environ, {"PATH": tmp}):
            try:
                dirty(kit, "const-x")
                case("a missing git is a teaching error, never a traceback", False)
            except EvalError as missing:
                case("a missing git is a teaching error, never a traceback", "install it" in str(missing))
            except OSError:
                case("a missing git is a teaching error, never a traceback", False)
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="run-evals", add_help=False, allow_abbrev=False)
    parser.add_argument("--module", action="append", default=[])
    parser.add_argument("--token-file")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    try:
        args = parser.parse_args(argv)
        if args.self_test == bool(args.token_file) or (args.self_test and (args.module or args.verbose)):
            raise SystemExit(2)
    except SystemExit:
        print(
            "BROKEN: misinvocation — fix: python3 scripts/run-evals.py --token-file <file>"
            " [--module <module>]... [--verbose], or --self-test"
        )
        return EXIT_BROKEN
    if args.self_test:
        return self_test()
    env = run_env(dict(os.environ))
    try:
        known = [m.name for m in module_folders(KIT)]
        model = eval_model(KIT)
        pinned = pinned_claude(KIT)
        token = token_file(args.token_file)  # judged before docker is asked for an image
        box = Box(ensure_image(pinned, env), pinned, token)
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
            if args.verbose:
                print(f"══ {module}", flush=True)
            outcome = run_module(module, model, env, box, args.verbose)
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
