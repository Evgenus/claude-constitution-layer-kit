#!/usr/bin/env python3
"""Kit tooling, never shipped in a module, and no check: run the eval cases of modules in a throwaway
container and write each run's attempt into the receipts file, save a passing rerun of a passing receipt
(decisions dec-0093-module-evals-with-local-receipts and
dec-0094-eval-runs-record-only-what-changes-the-verdict).

    python3 scripts/run-evals.py --token-file <file> [--module <module>]... [--verbose]
    python3 scripts/run-evals.py --self-test

With no `--module`, every module folder. Every case runs in a throwaway container of the image
scripts/eval-container/Dockerfile defines, built once through `docker` as kit-evalbox:<version>-<hash>, the
Claude Code version scripts/claude-code.version pins and the Dockerfile's hash; no case runs on the host,
so every receipt comes from one environment. The container holds no secret of the host: the module's copy
is mounted read-only, beside it a copy of the change's shared code, read-only too, and a results folder of
the run's own writable. It runs with Docker's seccomp filter
and its /proc mask lifted
(`--security-opt seccomp=unconfined --security-opt systempaths=unconfined`), which the eval's own Bash
sandbox, bwrap, needs to start; under Docker's defaults every Bash command of a case fails before it runs.
Docker Desktop's Linux machine still separates the container from the host. The token file, which the
runner never opens, reaches it as Docker's `--env-file`; it holds CLAUDE_CODE_OAUTH_TOKEN, a subscription
token from `claude setup-token`, and must be readable by its owner alone, which the runner checks before it
asks docker for the image. For each module, in turn:
  1. its eval files (`kit_evals.eval_files`) and the image's Dockerfile must all be committed
     (`kit_evals.dirty`), else the module is refused with the fix, so that the receipt names what CI checks;
  2. its eval files are copied, links followed, save a link to the shared package, into a temporary
     folder, a copy of the module's eval files: its cases, and its `plugin/` save `INSTALL.md`, the plugin the
     cases load through their `plugins:` line; and the files git tracks in the shared package,
     `shared/constitution_layer_kit/`, the files the receipt's hash names with the module's
     (`kit_evals.shared_files`, decision dec-0099-shared-code-installed-as-a-pip-package, R18), are copied
     beside it as `shared/constitution_layer_kit/`, so that the container runs the change's shared code and
     never a release installed on the host or in the image;
  3. one container per case: the module's copy mounted read-only at /plugin and the copy of the shared code
     read-only at /shared; its guard unsets the variables that would bill by usage (ANTHROPIC_API_KEY,
     ANTHROPIC_AUTH_TOKEN, CLAUDE_CODE_USE_BEDROCK, CLAUDE_CODE_USE_VERTEX, CLAUDE_CODE_USE_FOUNDRY), refuses
     to go on unless `claude --version` is the pinned version and `claude auth status` reports a
     subscription login, `oauth_token` or `claude.ai`; then, at the run's start and in the way the checks of
     `scripts/kit_install.py` do (`shared_environment`), it makes a virtual environment, at
     /opt/kit-shared-env (`CONTAINER_SHARED_ENV`), of the image's python3, with its system packages (the
     image's PyYAML) and no pip, writes into its site-packages a `.pth` file that names /shared, and
     puts its `bin` first on PATH, so that the python3 the case's hooks and scans start imports the
     mounted package; a python3 that does not import `constitution_layer_kit`
     from /shared and `yaml`, whether the folder lacks the package or another copy stands ahead of it, ends
     the container with exit 5 after two lines, the case not run: the step it was in, with the last line
     of that step's own output, and a line that says why with its one fix; the runner's BROKEN for that run
     is the step's line in brackets and then the fix line, with no fix of its own after it. The
     environment lies on a Docker tmpfs (`--tmpfs`, owned by the image's user `node`) and not in the home:
     the eval's own Bash sandbox replaces /home/node with an empty tmpfs, binding back only the plugin roots
     and the environment's `bin`, and hides /tmp, /var/tmp, /dev/shm and /run/shm, so an environment in
     any of them loses its pyvenv.cfg and its .pth file there, and the python3 a case runs through Bash, which
     PYTHONPATH does not reach, starts as the image's own and prints C15 (found 2026-10-23 in the run of
     2026-10-22: hooks and this check are not sandboxed and saw nothing). The runner therefore reads each
     case's copied traces after the case and, when one holds the start of C15, C16 or C17 of shared/GATE.md
     section 3 (`PACKAGE_FAILURE`), reports one BROKEN line naming the case, the trace, the line found and
     the fix, and counts the attempt as failed, as a partial result is: a command of the case did not see the
     change's shared code, so the receipt would not hold what it says (R18). The
     image is unchanged for this: its Debian python3 makes the environment with no package of its own, and
     a virtual environment's `.pth` entries come before the system's folders on `sys.path`. Then it runs
     `claude plugin eval` on the copy, `--case
     <name>`, with `--model` from scripts/eval-model, `--runs 3 --threshold 1 --ablation none`,
     `--trust-plugin --no-publish --scaffold`, and `--allow-tools` granting those of Bash, Write and Edit
     that the case lists in its `allowed_tools` — a skill or command case lists Read, Glob, Grep, Write,
     Edit, Skill and Bash, the tools a session at its moment would have, and a start-rule case only what
     its rule needs; its JSON result and report are kept in local/evals/<module>/, with each run's trace,
     which `--keep-temp` leaves in the container, copied out as <case>-trace<n>.jsonl, so that a failing run
     can be read. The runs count against the subscription's plan, never against usage;
  4. the cases' `casesTotal` and `casesPassed` summed, and their `overallScore` weighted by cases, become
     one attempt, stamped with the time in UTC. It is appended to the module's entry of
     scripts/eval-receipts.json unless the entry names the run's hash, Claude Code version and model, its
     last attempt passed and this one passed too: then the receipt stands and nothing is written, so a
     passing run made only to watch owes no commit, while every failure since the entry began, and the pass
     after it, is kept; an attempt that is written is committed, a failure as much as a pass (decision
     dec-0094-eval-runs-record-only-what-changes-the-verdict). An entry whose hash, Claude Code version or
     model differs from the run's is replaced by a new one. A partial result counts as a failed attempt.
The `docker` commands run in the person's environment less the four variables of `kit_module_doc.claude_env`
and the usage-billing ones above; the container gets none of it but the token file.

Prints one line per case and one per module, and where the results are kept; a module's line ends "the
receipt stands, …, so nothing is recorded" when its attempt was not written. With `--verbose`, which
`just evals` passes, each case first prints what the model is told and each grader's rule, then the
container's output as it comes, then for each run its verdict, the start hooks' output, every tool call and
text of the model, and each grader's verdict with the eval's explanation (`scripts/kit_eval_report.py`).
`--self-test` proves the guards without a model or docker: the token file's mode and a token file that does
not exist; the container's options (the token as an env file, never its text, the copy read-only, the
seccomp filter and the /proc mask lifted, the shared code mounted read-only beside the module's copy, the
tmpfs of the shared code's environment, which lies outside the home and the temporary folders the eval's
Bash sandbox hides); its
guard, run under sh against a fake claude (the billing variables unset, the pinned version and a subscription
login required, in that order); its command after the guard, run under sh (the shared code made importable:
the python3 a fake claude starts imports a toy package from the mounted folder, the environment's `bin`
first on its PATH, and a mounted folder without the package, a second copy of it ahead on the python3's
path, or a virtual environment that cannot be made, ends the container with exit 5, the case not run,
after the line of the step it failed in; the eval's exit code kept, each run's trace copied
whatever its folder, and mapped to the path the eval's result names); the trace guard, red for a trace that
holds the line of C15, C16 or C17, typed by hand, green for a clean trace, its fixed words held to the
shared messages and the entry files; the shared code copied from a toy
kit's tracked files alone, and a kit that tracks none a Broken with the fix; `run_module` against a fake
docker: the folder mounted at /shared holds the copy when the container starts, a container that exits 5
after a stray line, the line of its step and its fix line, or after those two lines alone, ends the run
with the step's line in brackets and the fix line, one fix, while one that exits 5 with the fix line alone
or with no output, and another exit, keep the run's fix; the environment of the
docker commands; the image's tag following the pin
and the Dockerfile's text, and the image inspected and built under that tag, against a fake docker; a token
file judged before docker is asked for an image; the Dockerfile's refusal of an architecture reaching the
person with its own fix, from BuildKit's log and from the legacy builder's coloured output, and a failed
download in the same step, whose ERROR line quotes the step's command, the refusal's echo included, told
apart and given the exact build to run; the Dockerfile's refusal opening with the words the runner looks
for; the shell the Dockerfile names in CLAUDE_CODE_SHELL, run with a socket on stdin, reading no ~/.bashrc
where bash itself does, so that no Bash call of a case opens with that file's error; each scaffold that makes
a git repository leaving out of git the sandbox's placeholders the runs showed; the verbose story of a
fixed case, run by run; an attempt recorded only when it changes the receipt's verdict; a missing token file
argument; the files a rename leaves not committed; an eval image not committed; and a missing git.
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
import socket
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
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
    shared_files,
    write_receipts,
)
from kit_module_doc import DocumentError, claude_env, hiding_shared, module_folders, pinned_claude

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
CONTAINER_SHARED = "/shared"  # where the change's shared code is mounted, read-only, beside the module's copy
# Where the virtual environment of the shared code stands. It must lie outside the home and the temporary
# folders: the eval's own Bash sandbox (bwrap, Claude Code 2.1.282) replaces /home/node with an empty tmpfs,
# binding back only the plugin roots and the environment's `bin`, and hides /tmp, /var/tmp, /dev/shm and
# /run/shm, so an environment there loses its pyvenv.cfg and its .pth file inside the sandbox and the python3
# a case runs through Bash cannot import the package. A Docker tmpfs, since the image's /opt is not
# writable by `node`, uid 1000 in the image.
CONTAINER_SHARED_ENV = "/opt/kit-shared-env"
SHARED_ENV_TMPFS = f"{CONTAINER_SHARED_ENV}:exec,uid=1000,gid=1000,mode=755"
CONTAINER_OUT = "/out"  # where the results folder is mounted, writable
SHARED_ENV_EXIT = 5  # the exit of a container that could not make the shared code importable
SHARED_ENV_SAID = (  # the container's last line, with its one fix, which `run_case` prints after the step's
    "the shared code cannot be made importable in the container, where a case must run the change's own"
    " shared code and no release — fix: correct the cause of the failed step, in"
    " shared/constitution_layer_kit/ or in scripts/eval-container/Dockerfile, and run the evals again"
)
SHARED_STEPS = (  # what the container was doing when it failed, in the order of its steps
    "making the virtual environment",
    "writing the .pth file that names the mounted shared folder",
    "importing constitution_layer_kit from the mounted shared folder, and yaml",
)
SHARED_PTH_WRITE = (  # run by the environment's python3: its .pth file, naming the mounted shared folder
    "import pathlib, sys, sysconfig; "
    "pathlib.Path(sysconfig.get_path('purelib'), 'kit-shared.pth').write_text(sys.argv[1] + '\\n')"
)
SHARED_PROBE = (  # run by the environment's python3: the package comes from the mounted shared folder, else
    # it says where from, as its last line
    "import constitution_layer_kit, sys, yaml; "
    "sys.exit(0 if constitution_layer_kit.__file__.startswith(sys.argv[1] + '/') else "
    '"constitution_layer_kit comes from " + constitution_layer_kit.__file__ + ", not from " + sys.argv[1])'
)
PACKAGE_FAILURE = re.compile(  # the fixed middles of C15, C16 and C17 of shared/GATE.md section 3, which the
    # self-test holds to the shared messages and the entry files
    r"BROKEN: [^\s\"\\]+ (?:needs the Python package constitution-layer-kit |needs constitution-layer-kit "
    r"|was written for constitution-layer-kit ).{0,200}"
)
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
HEARTBEAT = 30  # seconds between the verbose mode's lines while a case runs
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


def shared_environment(shared: str = CONTAINER_SHARED, env: str = CONTAINER_SHARED_ENV) -> str:
    """The shell a container runs after its guard and before its case, to make the change's shared code
    importable the way the kit's other checks do (decision dec-0099-shared-code-installed-as-a-pip-package,
    R18): a virtual environment `env` (`CONTAINER_SHARED_ENV`, outside the home and the temporary folders that
    the eval's Bash sandbox hides) of the image's python3, with its system packages (the
    image's PyYAML) and no pip, whose site-packages holds a `.pth` file naming the mounted folder `shared`;
    then its `bin` first on PATH, for the `claude` the case runs and so for the python3 its hooks and scans
    start. The environment's python3 must import `constitution_layer_kit` from that folder and `yaml`, else
    the container exits `SHARED_ENV_EXIT`, the case not run, after two lines on its standard error: the step
    it was in, `SHARED_STEPS`, with the last line of that step's own output, and `SHARED_ENV_SAID`."""
    python = shlex.quote(f"{env}/bin/python3")
    making, writing, importing = (shlex.quote(step) for step in SHARED_STEPS)
    venv = f"python3 -m venv --system-site-packages --without-pip {shlex.quote(env)}"
    return (
        f"step={making}; out=$({venv} 2>&1) && "
        f"step={writing} && out=$({python} -c {shlex.quote(SHARED_PTH_WRITE)} {shlex.quote(shared)} 2>&1) && "
        f'step={importing} && export PATH={shlex.quote(f"{env}/bin")}:"$PATH" && '
        f"out=$(python3 -c {shlex.quote(SHARED_PROBE)} {shlex.quote(shared)} 2>&1) || "
        '{ echo "failed while $step: $(printf \'%s\\n\' "$out" | tail -n 1)" >&2; '
        f"echo {shlex.quote(SHARED_ENV_SAID)} >&2; exit {SHARED_ENV_EXIT}; }}; "
    )


def then_for(
    copy: Path,
    case: str,
    argv: list[str],
    tmp: str = "/tmp",
    out: str = CONTAINER_OUT,
    plugin: str = CONTAINER_PLUGIN,
    home: str = CONTAINER_HOME,
    shared: str = CONTAINER_SHARED,
    env: str = CONTAINER_SHARED_ENV,
) -> str:
    """What a container runs after its guard: the environment of the shared code (`shared_environment`), the
    eval, then each run's trace, which `--keep-temp` leaves in a read-only folder under /tmp, copied to /out
    as <case>-trace<n>.jsonl, and a line `<n> <its path>` in /out/<case>-traces.txt, the path the eval's
    result names for its run; the container exits with the eval's code. The paths are the container's; the
    self-test passes its own."""
    return (
        f"{shared_environment(shared, env)}"
        f"cp -r {shlex.quote(plugin)} {shlex.quote(f'{home}/{copy.name}')} && cd {shlex.quote(home)} && "
        f"{shlex.join(argv)}; code=$?; "
        f": > {shlex.quote(f'{out}/{case}-traces.txt')}; "
        f"find {shlex.quote(tmp)} -name trace.jsonl -path '*/out/trace.jsonl' 2>/dev/null | "
        "{ n=0; while IFS= read -r t; do n=$((n+1)); "
        f'cp "$t" {shlex.quote(out)}/{shlex.quote(case)}-trace$n.jsonl; '
        f'printf \'%s %s\\n\' "$n" "$t" >> {shlex.quote(f"{out}/{case}-traces.txt")}; done; }}; exit $code'
    )


def in_box(box: Box, copy: Path, out: Path, argv: list[str], case: str, shared: Path) -> list[str]:
    """The `docker run` that runs `argv` in a throwaway container, after its guard: the module's copy
    mounted read-only, and beside it, read-only too, the folder `shared` that holds the change's shared
    package, and the tmpfs that holds the shared code's virtual environment (`CONTAINER_SHARED_ENV`)."""
    then = then_for(copy, case, argv)
    return [
        "docker", "run", "--rm", *SANDBOX_OPTIONS, "--env-file", str(box.token_file),
        "-v", f"{copy}:{CONTAINER_PLUGIN}:ro", "-v", f"{shared}:{CONTAINER_SHARED}:ro",
        "-v", f"{out}:{CONTAINER_OUT}", "--tmpfs", SHARED_ENV_TMPFS,
        box.image, "sh", "-c", guard(box.pinned, then),
    ]  # fmt: skip


def streamed(
    argv: list[str], cwd: Path, env: dict[str, str], timeout: float, heartbeat: float = HEARTBEAT
) -> tuple[int, str]:
    """Run `argv`, printing each line of its output, stdout and stderr together, as it comes; its exit code
    and the whole output. Past `timeout` seconds it is killed and `subprocess.TimeoutExpired` raised."""
    said: list[str] = []
    printing = threading.Lock()  # print writes a line and its end in two calls, so two threads could mix them

    def say(line: str) -> None:
        with printing:
            print(line, flush=True)

    with subprocess.Popen(
        argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
    ) as running:  # fmt: skip

        def echo() -> None:
            assert running.stdout is not None
            for line in running.stdout:
                said.append(line)
                say(f"  | {line.rstrip()}")

        reader = threading.Thread(target=echo, daemon=True)
        reader.start()
        started = time.monotonic()
        while True:  # a line every `heartbeat` seconds, since the eval prints little while a case runs
            elapsed = time.monotonic() - started
            if elapsed >= timeout:
                running.kill()
                raise subprocess.TimeoutExpired(argv, timeout)
            try:
                code = running.wait(timeout=min(heartbeat, timeout - elapsed))
                break
            except subprocess.TimeoutExpired:
                say(f"  … running, {int(time.monotonic() - started)} s")
        reader.join()
    return code, "".join(said)


def package_failures(case: str, traces: list[Path]) -> tuple[str, ...]:
    """One line for each of the case's copied `traces` that holds the start of a package failure, C15, C16 or
    C17 of shared/GATE.md section 3 (`PACKAGE_FAILURE`): the case, the trace, the text found, and the fix.
    A command a case ran printed it, so the eval's Bash sandbox did not see the change's shared code."""
    lines = []
    for trace in traces:
        found = PACKAGE_FAILURE.search(trace.read_text(encoding="utf-8", errors="replace"))
        if found:
            lines.append(
                f"BROKEN: case {case}: the trace {trace.name} holds the line {found.group(0)!r}, so a command"
                " of the case could not import the shared package — fix: the eval's Bash sandbox does not see"
                " the change's shared code: see step 3 in the docstring of scripts/run-evals.py"
            )
    return tuple(lines)


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
    argv = in_box(
        box, copy, out, eval_argv(plugin, case.name, model, CONTAINER_OUT, tools), case.name, shared_copy(tmp)
    )
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
        if done.returncode == SHARED_ENV_EXIT and len(said) > 1:  # its last two lines: the step, then the fix
            step, fix = said[-2:]
            raise Broken(
                f"the eval of case {case.name} exited {done.returncode} with no result ({step}) — {fix}"
            )
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
    outcome = outcome_of(result)
    broken = package_failures(case.name, sorted(kept.glob(f"{case.name}-trace*.jsonl")))
    if broken:  # as a partial result: the attempt counts as failed
        passed = min(outcome.passed, outcome.cases - 1)
        return Outcome(outcome.cases, passed, outcome.score, (*outcome.lines, *broken))
    return outcome


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


def shared_copy(tmp: Path) -> Path:
    """Where a run's copy of the change's shared code stands under the run's temporary folder `tmp`: the
    folder `run_module` fills with `copy_shared` and `run_case` mounts in each container, named once."""
    return tmp / "shared"


def copy_shared(kit: Path, into: Path) -> None:
    """The files git tracks in the kit's shared package (`kit_evals.shared_files`) copied under `into`, as
    `into/constitution_layer_kit/...`: the folder a container mounts as the change's shared code, holding
    exactly the files the receipt's hash names. A kit that tracks none is a Broken."""
    files = shared_files(kit)
    if not files:
        raise Broken(
            "git tracks no file under shared/constitution_layer_kit/ — fix: run the command from a clone of"
            " the kit, which holds the shared package"
        )
    for _, path in files:
        (into / path.relative_to(kit / "shared")).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, into / path.relative_to(kit / "shared"))


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
        copy_shared(KIT, shared_copy(Path(tmp)))
        outcomes = [run_case(case, copy, model, env, Path(tmp), box, verbose) for case in cases]
    total = sum(o.cases for o in outcomes)
    score = sum(o.score * o.cases for o in outcomes) / total if total else 0.0
    lines = tuple(line for o in outcomes for line in o.lines)
    return Outcome(total, sum(o.passed for o in outcomes), score, lines)


def recorded(old: Receipt | None, now: str, claude: str, model: str, attempt: Attempt) -> Receipt | None:
    """The module's entry after a run's `attempt`, or None when nothing is recorded: the entry names the
    run's eval hash, Claude Code version and model, its last attempt passed, and this one passed too
    (decision dec-0094-eval-runs-record-only-what-changes-the-verdict). Else the attempt is added, to a new
    entry when the hash, the version or the model differs."""
    current = old is not None and (old.hash, old.claude, old.model) == (now, claude, model)
    kept = old.attempts if old is not None and current else ()
    if kept and kept[-1].passing and attempt.passing:
        return None
    return Receipt(now, claude, model, (*kept, attempt))


def record(module: str, outcome: Outcome, claude: str, model: str) -> bool:
    """Record the run's attempt in the receipts file as `recorded` rules; whether it was recorded."""
    receipts = read_receipts(KIT)
    attempt = Attempt(
        datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), outcome.cases, outcome.passed, outcome.score
    )
    entry = recorded(receipts.get(module), eval_hash(KIT, module), claude, model, attempt)
    if entry is None:
        return False
    receipts[module] = entry
    write_receipts(KIT, receipts)
    return True


def case_shell(recipe: Path, folder: Path) -> Path | None:
    """The shell the Dockerfile names in CLAUDE_CODE_SHELL, written into `folder` from the `printf` that makes
    it in the image, for the self-test; None when the Dockerfile names no such shell or does not make it."""
    text = recipe.read_text(encoding="utf-8")
    named = re.search(r"^ENV CLAUDE_CODE_SHELL=(\S+)$", text, re.M)
    if not named:
        return None
    made = re.search(r"printf '([^']*)' > " + re.escape(named.group(1)) + r"\s", text)
    if not made:
        return None
    shell = folder / "bash"
    shell.write_text(made.group(1).replace("\\n", "\n"), encoding="utf-8")
    shell.chmod(0o755)
    return shell


def startup_errors(recipe: Path, folder: Path) -> tuple[str, str | None]:
    """What /bin/bash and the image's shell print on stderr for `-c true` with a socket on stdin, as Claude
    Code gives each Bash call, and a ~/.bashrc they cannot read, as under the eval's sandbox; None for the
    image's shell when the Dockerfile makes none. For the self-test."""
    home = folder / "home"
    (home / ".bashrc").mkdir(parents=True)  # a directory: unreadable as a file, whoever runs the self-test
    shell = case_shell(recipe, folder)
    said: list[str] = []
    env = {"PATH": os.environ["PATH"], "HOME": str(home)}
    for program in ("/bin/bash", *([str(shell)] if shell else [])):
        left, right = socket.socketpair()
        with left, right:
            said.append(
                subprocess.run(
                    [program, "-c", "true"], stdin=left.fileno(), env=env,
                    capture_output=True, text=True, check=False,
                ).stderr
            )  # fmt: skip
    return said[0], said[1] if shell else None


# The sandbox's placeholders in a case's folder, as the kept traces of runs on Claude Code 2.1.282 list them;
# golden data of the self-test, so that each scaffold's exclude list is held against what the runs showed.
SEEN_PLACEHOLDERS = (
    ".bash_profile", ".bashrc", ".eval-artifacts", ".gitconfig", ".gitmodules", ".idea", ".mcp.json",
    ".profile", ".ripgreprc", ".vscode", ".zprofile", ".zshrc",
    ".claude/agents", ".claude/commands", ".claude/hooks", ".claude/launch.json", ".claude/loop.md",
    ".claude/output-styles", ".claude/routines", ".claude/scheduled_tasks.json", ".claude/settings.json",
    ".claude/settings.local.json", ".claude/skills", ".claude/workflows",
)  # fmt: skip


def placeholders_shown(root: Path, folder: Path) -> list[str]:
    """For each case of the kit at `root` whose scaffold makes a git repository: the case and the
    placeholders the runs showed that `git status` still lists as untracked once the scaffold has run in
    `folder` and they are made there as 0-byte files, under no system or global config, as the eval's git
    has. For the self-test; an empty list when every such scaffold leaves them all out."""
    env = {
        "PATH": os.environ["PATH"], "HOME": str(folder), "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }  # fmt: skip
    shown: list[str] = []
    for module in module_folders(root):
        for case in cases_of(module):
            scaffold = case / "scaffold.sh"
            if not scaffold.is_file() or "git init" not in scaffold.read_text(encoding="utf-8"):
                continue
            work = folder / module.name / case.name
            work.mkdir(parents=True)
            subprocess.run(["sh", str(scaffold)], cwd=work, env=env, capture_output=True, check=True)
            for name in SEEN_PLACEHOLDERS:
                (work / name).parent.mkdir(parents=True, exist_ok=True)
                (work / name).write_text("", encoding="utf-8")
            status = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=all"], cwd=work, env=env,
                capture_output=True, text=True, check=True,
            ).stdout  # fmt: skip
            left = [n for n in SEEN_PLACEHOLDERS if f"?? {n}\n" in status]
            if left:
                shown.append(f"{module.name}/{case.name}: {' '.join(left)}")
    return shown


def report_story(folder: Path) -> list[str]:
    """The verbose story of a fixed case of two runs, the second failing, written into `folder`, for the
    self-test."""
    folder.mkdir(parents=True)
    (folder / "case.yaml").write_text(
        "execution:\n  prompt: Rename count_items to total_items.\ngraders:\n"
        "  - {type: tool_used, name: loads, tool: Skill, input_match: commit-before-edit}\n"
        "  - {type: regex, name: renamed, target: {source: file, path: src/a.py},"
        " pattern: def total_items}\n"
        "  - {type: tool_order, name: order, before: {tool: Skill, input_match: x}, after: {tool: Bash}}\n",
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


def shared_copy_said(kit: Path, scratch: Path, env: dict[str, str]) -> tuple[list[str], str]:
    """For the self-test: the files `copy_shared` copies from the toy kit `kit` into `scratch/copied`, the
    paths below it; and what it raises for a new git repository under `scratch` that tracks no shared
    package."""
    copied = scratch / "copied"
    copy_shared(kit, copied)
    empty = scratch / "no-shared-kit"
    empty.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=empty, env=env, capture_output=True, check=True)
    try:
        copy_shared(empty, scratch / "none")
    except Broken as nothing:
        return sorted(str(f.relative_to(copied)) for f in copied.rglob("*") if f.is_file()), str(nothing)
    return [], "no Broken"


def toy_eval_kit(folder: Path, env: dict[str, str]) -> Path:
    """For the self-test: a git repository at `folder` that tracks a module const-x with one eval case,
    `load`, and a shared package of one file, `core.py`; its path."""
    files = {
        "modules/const-x/plugin/skills/s/SKILL.md": "skill\n",
        "modules/const-x/evals/load/case.yaml": "execution:\n  allowed_tools: [Read]\n",
        "shared/constitution_layer_kit/core.py": "x = 1\n",
    }
    for name, text in files.items():
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")
    for git_args in (
        ["init", "-q"],
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
    ):
        subprocess.run(["git", *git_args], cwd=folder, env=env, capture_output=True, check=True)
    return folder


def fake_run_docker(folder: Path, log: Path, said: Path, pair: Path) -> dict[str, str]:
    """For the self-test: a `docker` in `folder` that runs no container. It appends to `log` what the folder
    mounted at /shared holds (the tracked file `core.py`, else a line saying it is missing) and then answers
    as the container would: a result for the case `load` in the folder mounted at /out; with
    FAKE_DOCKER_EXIT=5 the lines of `said` on its standard error and exit 5, with `5-pair` the lines of
    `pair`, exactly the two a real container prints, with `5-alone` the last line of `said` alone, with
    `5-silent` no line; with 3 a login refusal. The environment that puts it first on PATH."""
    folder.mkdir()
    result = json.dumps(
        {"aggregates": {"casesTotal": 1, "casesPassed": 1, "overallScore": 1.0},
         "cases": [{"name": "load", "aggregates": {"score": 1.0}}]}
    )  # fmt: skip
    (folder / "docker").write_text(
        "#!/bin/sh\n"
        "shared=; out=; prev=\n"
        'for a in "$@"; do\n'
        '  if [ "$prev" = -v ]; then\n'
        '    case "$a" in *:/shared:ro) shared=${a%:/shared:ro} ;; *:/out) out=${a%:/out} ;; esac\n'
        "  fi\n"
        "  prev=$a\n"
        "done\n"
        'core="$shared/constitution_layer_kit/core.py"\n'
        f"exec 3>> '{log}'\n"
        'if [ -f "$core" ]; then cat "$core" >&3; else echo "no core.py at $shared" >&3; fi\n'
        'case "$FAKE_DOCKER_EXIT" in\n'
        f"  5) cat '{said}' >&2; exit 5 ;;\n"
        f"  5-pair) cat '{pair}' >&2; exit 5 ;;\n"
        f"  5-alone) tail -n 1 '{said}' >&2; exit 5 ;;\n"
        "  5-silent) exit 5 ;;\n"
        "  3) echo 'not a subscription login: none' >&2; exit 3 ;;\n"
        "esac\n"
        f"printf '%s' '{result}' > \"$out/load.json\"\n",
        encoding="utf-8",
    )
    (folder / "docker").chmod(0o755)
    return {"PATH": f"{folder}{os.pathsep}{os.environ['PATH']}"}


class Heard(io.StringIO):
    """For the self-test: what `streamed` prints, kept. Once a line `  … running, ` follows the line
    `  | one`, it makes the file `gate`, which the program waits for before it prints its last line."""

    def __init__(self, gate: Path) -> None:
        super().__init__()
        self.gate = gate

    def write(self, text: str) -> int:
        written = super().write(text)
        lines = self.getvalue().splitlines()
        if "  | one" in lines and any(
            line.startswith("  … running, ") for line in lines[lines.index("  | one") + 1 :]
        ):
            self.gate.touch()
        return written


def streamed_in_order(tmp: Path) -> bool:
    """For the self-test: `streamed` echoes a program's lines as they come, stderr too, with a heartbeat line
    while it runs. The program prints `one`, waits for the gate that `Heard` makes once a heartbeat line has
    followed `one`, then prints `two` on stderr. So the order holds by construction, never by a clock: the
    first start of `sh` or the reader's turn may come late on a loaded machine, past any heartbeat. A
    `streamed` that held its lines until the end, or printed no heartbeat, never opens the gate, and the
    program is stopped at the timeout, which only ends a hang."""
    gate = tmp / "stream-gate"
    heard = Heard(gate)
    program = f"echo one; while [ ! -e '{gate}' ]; do sleep 0.05; done; echo two >&2"
    try:
        with contextlib.redirect_stdout(heard):
            code_said = streamed(["sh", "-c", program], tmp, dict(os.environ), 20, 0.2)
    except subprocess.TimeoutExpired:
        return False
    echoed = heard.getvalue().splitlines()
    if code_said != (0, "one\ntwo\n") or "  | one" not in echoed or "  | two" not in echoed:
        return False
    between = echoed[echoed.index("  | one") + 1 : echoed.index("  | two")]
    return any(line.startswith("  … running, ") for line in between)


def run_module_cases(case: Callable[[str, bool], None], box: Box, tmp: Path, quiet: dict[str, str]) -> None:
    """For the self-test: `run_module` over a toy kit against a docker that runs no container, which notes
    what the folder mounted at /shared holds. The cases: the change's shared code is there when the
    container starts and the case's result counts; a container that exits 5 after a stray traceback line,
    the line of the failed step and its fix line ends the run with the step's line in brackets and then the
    fix line, and no other fix after it, and so does one that prints those two lines alone, as a real
    container does; one that exits 5 with the fix line alone, or with no output, and one that exits
    otherwise, keep the run's fix."""
    eval_kit = toy_eval_kit(tmp / "eval-kit", quiet)
    said_file, run_log = tmp / "shared-env-said.txt", tmp / "run-docker.log"
    stray = "Traceback (most recent call last):"  # typed by hand, the lines the container printed
    step = (
        "failed while importing constitution_layer_kit from the mounted shared folder, and yaml:"
        " ModuleNotFoundError: No module named 'constitution_layer_kit'"
    )
    said_file.write_text(f"{stray}\n{step}\n{SHARED_ENV_SAID}\n", encoding="utf-8")
    pair_file = tmp / "shared-env-pair.txt"  # exactly the two lines a real container prints
    pair_file.write_text(f"{step}\n{SHARED_ENV_SAID}\n", encoding="utf-8")
    run_env_of = fake_run_docker(tmp / "run-bin", run_log, said_file, pair_file)
    exits: dict[str, str] = {}
    with mock.patch.dict(globals(), {"KIT": eval_kit}):
        ran = run_module("const-x", "m", run_env_of, box)
        for exit_code in ("5", "5-pair", "5-alone", "5-silent", "3"):
            try:
                run_module("const-x", "m", run_env_of | {"FAKE_DOCKER_EXIT": exit_code}, box)
                exits[exit_code] = "no Broken"
            except Broken as stopped:
                exits[exit_code] = str(stopped)
    case(
        "a run gives each container the change's shared code: the folder mounted at /shared holds the"
        " tracked files of the shared package, copied before the case runs, and the case's result counts",
        run_log.read_text(encoding="utf-8").splitlines()[:1] == ["x = 1"]
        and (ran.cases, ran.passed) == (1, 1),
    )
    fix_line = (  # typed by hand: the container's last line, and the one fix of the run's Broken
        "the shared code cannot be made importable in the container, where a case must run the change's own"
        " shared code and no release — fix: correct the cause of the failed step, in"
        " shared/constitution_layer_kit/ or in scripts/eval-container/Dockerfile, and run the evals again"
    )
    case(
        "a container that exits 5, the shared code not importable, ends the run with the line of the failed"
        " step in brackets, not the line before it, and then the container's fix line, the only 'fix:'",
        SHARED_ENV_SAID == fix_line
        and exits["5"] == f"the eval of case load exited 5 with no result ({step}) — {fix_line}"
        and exits["5"].count("fix:") == 1,
    )
    case(
        "a container that exits 5 after exactly two lines, the step and its fix, as a real one does, ends the"
        " run with the same line as one that printed a stray line before them",
        exits["5-pair"] == f"the eval of case load exited 5 with no result ({step}) — {fix_line}",
    )
    general = (  # typed by hand: the fix of the run for every exit but a container's line pair
        " — fix: the line in brackets says why: for a version not the pinned one, run docker image rm img and"
        " run again, which rebuilds it; for a login, save a token from claude setup-token in the token file"
    )
    case(
        "a container that exits 5 with no output, or with its fix line alone and no step, keeps the fix of"
        " the run after the line in brackets, or after 'no output'",
        exits["5-silent"] == f"the eval of case load exited 5 with no result (no output){general}"
        and exits["5-alone"] == f"the eval of case load exited 5 with no result ({fix_line}){general}",
    )
    case(
        "a container that exits otherwise with no result keeps the fix of the run: the line in brackets, the"
        " image to remove and the login",
        exits["3"]
        == f"the eval of case load exited 3 with no result (not a subscription login: none){general}",
    )


def recording_holds() -> bool:
    """Whether `recorded` keeps exactly the attempts that change a receipt's verdict, for the self-test."""
    good, bad, once = Attempt("t2", 2, 2, 1.0), Attempt("t2", 2, 1, 0.5), Attempt("t1", 2, 2, 1.0)
    failed_once = Attempt("t1", 2, 1, 0.5)

    def entry(*attempts: Attempt, of: str = "sha256:h", claude: str = "2.1.282", model: str = "m") -> Receipt:
        return Receipt(of, claude, model, attempts)

    def then(
        old: Receipt | None, attempt: Attempt, of: str = "sha256:h", claude: str = "2.1.282", model: str = "m"
    ) -> Receipt | None:
        return recorded(old, of, claude, model, attempt)

    return (
        then(None, good) == entry(good)
        and then(entry(once), good) is None
        and then(entry(once), bad) == entry(once, bad)
        and then(entry(failed_once), good) == entry(failed_once, good)
        and then(entry(once), good, of="sha256:other") == entry(good, of="sha256:other")
        and then(entry(once), good, claude="2.1.283") == entry(good, claude="2.1.283")
        and then(entry(once), good, model="other") == entry(good, model="other")
    )  # fmt: skip


def environment_cases(case: Callable[[str, bool], None], argv: list[str], tmp: Path) -> None:
    """For the self-test: the tmpfs of the shared code's environment in the argv of `docker run`, its place
    outside the folders the eval's Bash sandbox hides, and the trace guard on traces typed by hand."""
    case(
        "the container holds the shared code's virtual environment on a Docker tmpfs the container's user"
        " owns, executable, in the argv of docker run before the image",
        "--tmpfs" in argv
        and argv[argv.index("--tmpfs") + 1] == "/opt/kit-shared-env:exec,uid=1000,gid=1000,mode=755"
        and argv.index("--tmpfs") < argv.index("img"),
    )
    case(
        "the shared code's environment lies under none of /home, /tmp, /var/tmp, /dev/shm and /run/shm,"
        " the folders the eval's Bash sandbox replaces or hides, so that its pyvenv.cfg and .pth file are"
        " seen by the python3 a case starts through Bash",
        not any(
            CONTAINER_SHARED_ENV == hidden or CONTAINER_SHARED_ENV.startswith(hidden + "/")
            for hidden in ("/home", "/tmp", "/var/tmp", "/dev/shm", "/run/shm")
        )
        and shared_environment().count(CONTAINER_SHARED_ENV) >= 3,
    )
    holds = {  # typed by hand: the lines of C15, C16 and C17 as the traces of a case hold them
        "c15": '{"output": "BROKEN: const-x needs the Python package constitution-layer-kit 1.0.0 or a'
        " later 1.x release, and python3 cannot import it — fix: install it for python3 as /p/INSTALL.md"
        ' says — until then Markdown writes pass unchecked\\n"}',
        "c16": '{"output": "BROKEN: const-x needs constitution-layer-kit 1.2.0 or a later 1.x release,'
        ' found 1.0.0 — fix: install one for python3 as /p/INSTALL.md says — nothing"}',
        "c17": '{"output": "BROKEN: const-x was written for constitution-layer-kit 1.0.0, a 1.x release,'
        ' found 2.0.0 — fix: update the plugin"}',
        "clean": '{"output": "ok: 3 documents examined", "text": "the BROKEN line of the check is gone"}',
    }
    traces = tmp / "traces"
    traces.mkdir()
    said_of = {}
    for key, text in holds.items():
        (traces / f"{key}-trace1.jsonl").write_text(text + "\n", encoding="utf-8")
        said_of[key] = package_failures("load", [traces / f"{key}-trace1.jsonl"])
    case(
        "a trace that holds the C15 line, typed by hand, is BROKEN in one line that names the case, the"
        " trace, the line found and the fix; a C16 line and a C17 line likewise",
        all(
            len(said_of[k]) == 1
            and said_of[k][0].startswith("BROKEN: case load: the trace ")
            and f"{k}-trace1.jsonl" in said_of[k][0]
            and "— fix: the eval's Bash sandbox" in said_of[k][0]
            for k in ("c15", "c16", "c17")
        )
        and "needs the Python package constitution-layer-kit 1.0.0" in said_of["c15"][0]
        and "needs constitution-layer-kit 1.2.0" in said_of["c16"][0],
    )
    case("a clean trace, one that only names BROKEN, is no finding", said_of["clean"] == ())
    shared_text = (KIT / "shared" / "constitution_layer_kit" / "messages.py").read_text(encoding="utf-8")
    entry_text = "".join(
        f.read_text(encoding="utf-8", errors="replace")
        for f in sorted((KIT / "modules").glob("*/plugin/scripts/*.py"))
    )
    case(
        "the fixed middles of C15, C16 and C17 that the trace guard looks for stand in the shared messages"
        " and the entry files",
        "needs the Python package constitution-layer-kit " in entry_text
        and "needs constitution-layer-kit " in shared_text
        and "was written for constitution-layer-kit " in shared_text,
    )


def self_test() -> int:
    """The runner's guards, run without a model or docker: the token file's mode and its absence, the
    container's options, its guard and its command after the guard, each run under sh, the environment of
    the docker commands, the image's tag, the token file judged before the image, a missing token file
    argument, the Dockerfile's refusal of an architecture from either builder and a failed download in the
    same step, told the exact build to run, the refusal's words in the Dockerfile, the image's shell reading
    no ~/.bashrc, each git scaffold leaving out the sandbox's placeholders, an attempt recorded only when it
    changes the receipt's verdict, an eval image not committed, the files a rename leaves not committed, and a
    missing git."""
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
        argv = in_box(
            box,
            Path(tmp) / "const-x",
            Path(tmp) / "out",
            ["claude", "plugin", "eval"],
            "case",
            Path(tmp) / "shared",
        )
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
            "the container mounts the change's shared code read-only beside the module's copy",
            f"{Path(tmp) / 'shared'}:/shared:ro" in argv
            and argv.index(f"{Path(tmp) / 'shared'}:/shared:ro")
            == argv.index(f"{Path(tmp) / 'const-x'}:/plugin:ro") + 2,
        )
        case(
            "the container runs the guard before its case",
            argv[-1]
            == guard("2.1.282", then_for(Path(tmp) / "const-x", "case", ["claude", "plugin", "eval"])),
        )
        environment_cases(case, argv, Path(tmp))
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
        bare, wrapped = startup_errors(KIT / EVAL_IMAGE, Path(tmp) / "shell")
        case(
            "the image's shell, which the Dockerfile names in CLAUDE_CODE_SHELL, reads no ~/.bashrc with a"
            " socket on stdin, where bash itself does",
            ".bashrc" in bare and wrapped == "",
        )
        shown = placeholders_shown(KIT, Path(tmp) / "scaffolds")
        case(
            "every scaffold that makes a git repository leaves out of git each placeholder the sandbox put in"
            " a case's folder in the runs" + "".join(f"\n        shown: {line}" for line in shown),
            not shown,
        )
        box_root = Path(tmp) / "box root"  # a space, so that then_for's quoting is held
        for folder in ("tmp/claude-eval-a/out", "tmp/e-b/out", "out", "plugin", "home", "bin"):
            (box_root / folder).mkdir(parents=True)
        (box_root / "shared" / "constitution_layer_kit").mkdir(parents=True)
        (box_root / "shared" / "constitution_layer_kit" / "__init__.py").write_text("", encoding="utf-8")
        (box_root / "plugin" / "case.yaml").write_text("x\n", encoding="utf-8")
        (box_root / "bin" / "claude").write_text(
            "#!/bin/sh\n"
            "python3 -c 'import constitution_layer_kit as c; print(c.__file__)'"
            f" > '{box_root}/seen.txt' 2>&1\n"
            f"echo \"${{PATH%%:*}}\" > '{box_root}/first-on-path.txt'\n"
            f"echo 1 > '{box_root}/tmp/claude-eval-a/out/trace.jsonl'\n"
            f"echo 2 > '{box_root}/tmp/e-b/out/trace.jsonl'\nexit 7\n",
            encoding="utf-8",
        )
        (box_root / "bin" / "claude").chmod(0o755)
        box_env = {"PATH": f"{box_root / 'bin'}{os.pathsep}{os.environ['PATH']}"}
        script = then_for(
            Path("const-x"), "load", ["claude", "plugin", "eval"], tmp=str(box_root / "tmp"),
            out=str(box_root / "out"), plugin=str(box_root / "plugin"), home=str(box_root / "home"),
            shared=str(box_root / "shared"), env=str(box_root / "env"),
        )  # fmt: skip
        boxed = subprocess.run(["sh", "-c", script], env=box_env, capture_output=True, check=False)
        seen_file, first_file = box_root / "seen.txt", box_root / "first-on-path.txt"
        case(
            "the container makes the shared code importable for the case: the python3 its claude starts"
            " imports the package from the mounted folder, the environment's bin first on its PATH",
            seen_file.read_text(encoding="utf-8").strip()
            == f"{box_root}/shared/constitution_layer_kit/__init__.py"
            and first_file.read_text(encoding="utf-8").strip() == f"{box_root}/env/bin",
        )
        seen_file.unlink()
        (Path(tmp) / "hide").mkdir()  # a folder of its own for PYTHONPATH, so that nothing else is put on it
        refused = subprocess.run(
            ["sh", "-c", then_for(
                Path("const-x"), "none", ["claude", "plugin", "eval"], tmp=str(box_root / "tmp"),
                out=str(box_root / "out"), plugin=str(box_root / "plugin"), env=str(box_root / "env-2"),
                shared=str(box_root / "nothing"),
            )],
            env=box_env | {"PYTHONPATH": hiding_shared(Path(tmp) / "hide")},  # a release is no copy either
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        importing = "failed while importing constitution_layer_kit from the mounted shared folder, and yaml: "
        case(
            "a mounted folder without the package ends the container with exit 5, the line of the step it"
            " failed in with that step's last output line, then a line that says why, the case not run",
            refused.returncode == SHARED_ENV_EXIT
            and refused.stderr.splitlines()[-2:]
            == [importing + "ModuleNotFoundError: No module named 'constitution_layer_kit'", SHARED_ENV_SAID]
            and not seen_file.exists()
            and not (box_root / "out" / "none-traces.txt").exists(),
        )
        (box_root / "a-file").write_text("", encoding="utf-8")
        unmade = subprocess.run(
            ["sh", "-c", then_for(
                Path("const-x"), "unmade", ["claude", "plugin", "eval"], tmp=str(box_root / "tmp"),
                out=str(box_root / "out"), plugin=str(box_root / "plugin"),
                env=str(box_root / "a-file" / "env"), shared=str(box_root / "shared"),
            )],
            env=box_env, capture_output=True, text=True, check=False,
        )  # fmt: skip
        case(
            "a virtual environment that cannot be made ends the container with exit 5, the line of that step"
            " first, then the line that says why, the case not run",
            unmade.returncode == SHARED_ENV_EXIT
            and unmade.stderr.splitlines()[-2].startswith(
                "failed while making the virtual environment: Error: [Errno 20] Not a directory"
            )
            and unmade.stderr.splitlines()[-1] == SHARED_ENV_SAID
            and not (box_root / "out" / "unmade-traces.txt").exists(),
        )
        (box_root / "second" / "constitution_layer_kit").mkdir(parents=True)
        (box_root / "second" / "constitution_layer_kit" / "__init__.py").write_text("", encoding="utf-8")
        crowded = subprocess.run(
            ["sh", "-c", then_for(
                Path("const-x"), "crowded", ["claude", "plugin", "eval"], tmp=str(box_root / "tmp"),
                out=str(box_root / "out"), plugin=str(box_root / "plugin"), env=str(box_root / "env-3"),
                shared=str(box_root / "shared"),
            )],
            env=box_env | {"PYTHONPATH": str(box_root / "second")},
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        second = box_root / "second" / "constitution_layer_kit" / "__init__.py"
        case(
            "a second copy of the package ahead of the mounted folder on the python3's path ends the"
            " container with exit 5, the line of the step that says where the package came from, then a line"
            " that says why, the case not run",
            crowded.returncode == SHARED_ENV_EXIT
            and crowded.stderr.splitlines()[-2:]
            == [
                f"{importing}constitution_layer_kit comes from {second}, not from {box_root}/shared",
                SHARED_ENV_SAID,
            ]
            and not seen_file.exists()
            and not (box_root / "out" / "crowded-traces.txt").exists(),
        )
        copied = sorted(p.name for p in (box_root / "out").glob("load-trace*.jsonl"))
        case(
            "the container keeps the eval's exit code and copies each run's trace, whatever its folder",
            boxed.returncode == 7 and copied == ["load-trace1.jsonl", "load-trace2.jsonl"],
        )
        case(
            "the verbose mode echoes the container's output as it comes, stderr too, with a line while it"
            " runs",
            streamed_in_order(Path(tmp)),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                streamed(["sh", "-c", "sleep 30"], Path(tmp), dict(os.environ), 1, 0.3)
                case("the verbose mode stops a case past its time", False)
            except subprocess.TimeoutExpired:
                case("the verbose mode stops a case past its time", True)
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
                "tool_used: Skill whose input matches 'commit-before-edit'",
                "tool_order: Skill (input matches 'x') before Bash", "load the skill X",
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
        (kit / "modules/const-x/plugin/skills/s").mkdir(parents=True)
        (kit / "modules/const-x/plugin/skills/s/SKILL.md").write_text("skill\n", encoding="utf-8")
        (kit / "shared/constitution_layer_kit").mkdir(parents=True)
        (kit / "shared/constitution_layer_kit/core.py").write_text("x = 1\n", encoding="utf-8")
        quiet = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "PATH": os.environ["PATH"]}
        for git_args in (
            ["init", "-q"],
            ["add", "-A"],
            ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
        ):
            subprocess.run(["git", *git_args], cwd=kit, env=quiet, capture_output=True, check=True)
        (kit / "shared/constitution_layer_kit/untracked.py").write_text("y = 2\n", encoding="utf-8")
        files, nothing = shared_copy_said(kit, Path(tmp), quiet)
        case(
            "the shared code is copied from the files git tracks alone, as constitution_layer_kit/ under the"
            " folder a container mounts",
            files == ["constitution_layer_kit/core.py"],
        )
        case(
            "a kit that tracks no shared package is a Broken with the fix",
            "git tracks no file under shared/constitution_layer_kit/" in nothing
            and "fix: run the command from a clone of the kit" in nothing,
        )
        run_module_cases(case, box, Path(tmp), quiet)
        (kit / "shared/constitution_layer_kit/untracked.py").unlink()
        skill = kit / "modules/const-x/plugin/skills/s"
        (skill / "SKILL.md").rename(skill / "OTHER.md")  # a rename in the working tree, ` R` in porcelain
        subprocess.run(
            ["git", "add", "-N", "modules/const-x/plugin/skills/s/OTHER.md"],
            cwd=kit, env=quiet, capture_output=True, check=True,
        )  # fmt: skip
        with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}):
            case(
                "a rename not committed, marked in the working tree's column, names its new path and no"
                " fragment of its source",
                dirty(kit, "const-x") == ["modules/const-x/plugin/skills/s/OTHER.md"],
            )
            (kit / "shared/constitution_layer_kit/core.py").write_text("x = 2\n", encoding="utf-8")
            case(
                "an edit of a file of the shared package, not committed, refuses the run too, since the"
                " receipt's hash names it",
                "shared/constitution_layer_kit/core.py" in dirty(kit, "const-x"),
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
    case(
        "a run records its attempt only when it changes what the receipt says: a first run, a failure, a pass"
        " after a failure and a run on other files, version or model are recorded; a pass on a passing"
        " receipt is not",
        recording_holds(),
    )
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
            kept = record(module, outcome, pinned, model)
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
            + (
                ""
                if kept
                else "; the receipt stands, already passing for these files, this Claude Code and this model,"
                " so nothing is recorded"
            )
        )
        if not passing and worst == EXIT_GREEN:
            worst = EXIT_RED
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
