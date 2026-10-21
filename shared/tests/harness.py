"""The case runner. It drives a module's real entry point — the POSIX wrapper, stdin, exit
code — with real PreToolUse events, as the platform does, save that git is asked with no clock
(`UNCLOCKED_GIT`).

A Case is one acceptance item with both halves: the red half must exit 2 AND teach the
expected message, its RED lines exactly that finding's headline and the count line, so a
second finding or a stray line fails it; the green half must pass, printing the whole green
line the case names. A fixture that proves only one half cannot tell a working check from
one that always answers the same. The other items, with no failing half (an exit-code
property, a count, a log line), are plain tests; `acceptance` holds the checks that assert.

The tests that import this file reach the shared package and the module's own packages through
links in their own folder, which pytest puts first on the import path: no Python file of a
module edits the import path of its own process, the tests included.
"""

from __future__ import annotations

import atexit
import json
import os
import shutil
import signal
import subprocess
import tempfile
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from constitution_layer_kit.model import Finding
from consumer import Consumer


@dataclass(frozen=True)
class Write:
    target: str
    text: str


@dataclass(frozen=True)
class Edit:
    target: str
    old: str
    new: str
    replace_all: bool = False


@dataclass(frozen=True)
class Result:
    code: int
    stdout: str
    stderr: str


NO_ANSWER = 124  # the code of a run that did not end within its bound, as timeout(1) gives it
WARM = "CONSTITUTION_KIT_FAKE_WARM"  # set only for the one start `fake_program` makes
# Run at the start of every gate process `run_gate` starts, through a `sitecustomize` last on PYTHONPATH:
# git is asked with no clock. In a hook the gate gives each git call 3 s, and on a loaded machine a real git
# that answers in 0.02 s at rest has taken longer (2026-10-16, -n auto at a load average of 16), so a
# verdict no case is about would hang on the machine's speed. Python loads the first `sitecustomize` on the
# path, so a test that puts one of its own on PYTHONPATH (`git_patch` of the shared items, or a patch of
# its own) sets the clocks itself: a test that proves a time limit keeps the one it proves. A folder that
# only hides a library holds none, and this one still loads. It imports only the standard library and
# prints nothing.
UNCLOCKED_GIT = """\
import subprocess

_run = subprocess.run


def _unclocked(command, *args, **kwargs):
    if command and command[0] == "git":
        kwargs.pop("timeout", None)
    return _run(command, *args, **kwargs)


subprocess.run = _unclocked
"""


def fake_program(path: Path, body: str) -> Path:
    """A fake program at `path`: a shell script that runs `body`, made executable and started once. The
    first start of a file just made executable is slow on a loaded machine (0.2 to 3.1 s measured on macOS
    on 2026-10-16, then 0.02 s each time), and inside a gate's clock it can cut a wait no case chose to
    cut. So the script's first line ends it at once under `WARM`, and that start is made here, before any
    clock: nothing the body does, logs or waits for happens in it."""
    path.write_text(f'#!/bin/sh\n[ -z "${WARM}" ] || exit 0\n{body}', encoding="utf-8")
    path.chmod(0o755)
    subprocess.run([str(path)], env={WARM: "1"}, capture_output=True, check=False)
    return path


@dataclass(frozen=True)
class Case:
    number: int
    title: str
    red: Write | Edit
    green: Write | Edit
    expect: Finding
    green_what: str  # what the green line says the green half's document is, typed by hand — for a
    # gate without a hook mode, the whole tail of the scan's green line over the consumer holding the
    # green half's document
    setup: Sequence[Write] = ()
    count: str | None = None  # a gate without a hook mode only: the scan's count line for the red
    # half, typed by hand, since "1 document examined" is a hook's


def event_json(
    repo: Path, action: Write | Edit, session: str = "fixture-session", event: str = "PreToolUse"
) -> str:
    tool_input: dict[str, object] = {"file_path": str(repo / action.target)}
    if isinstance(action, Write):
        tool_input["content"] = action.text
    else:
        tool_input.update(
            {"old_string": action.old, "new_string": action.new, "replace_all": action.replace_all}
        )
    return json.dumps(
        {
            "hook_event_name": event,
            "session_id": session,
            "cwd": str(repo),
            "tool_name": type(action).__name__,
            "tool_input": tool_input,
        }
    )


def red_lines(text: str) -> list[str]:
    """The RED lines of an output, in order: what an item compares whole, so that a finding too
    many, or a stray line, is seen."""
    return [line for line in text.splitlines() if line.startswith("RED:")]


def stop_json(root: Path, active: bool = False, session: str = "fixture-session") -> str:
    """A Stop payload as the platform sends it, reduced to what a gate reads: the session's
    directory and the loop guard."""
    return json.dumps(
        {"hook_event_name": "Stop", "session_id": session, "cwd": str(root), "stop_hook_active": active}
    )


def bash_json(root: Path, command: str, session: str = "fixture-session") -> str:
    """A PreToolUse payload of the shell tool as the platform sends it, reduced to what a gate
    reads: the session's directory and the command."""
    return json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "session_id": session,
            "cwd": str(root),
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
    )


def ask_reason(result: Result) -> str | None:
    """The reason of an `ask` verdict — exit 0, one JSON object on stdout asking the platform to
    prompt — or None when the output is not that."""
    if result.code != 0:
        return None
    try:
        answer = json.loads(result.stdout)
    except ValueError:
        return None
    if not isinstance(answer, dict):
        return None
    specific = answer.get("hookSpecificOutput")
    if not isinstance(specific, dict) or specific.get("permissionDecision") != "ask":
        return None
    reason = specific.get("permissionDecisionReason")
    return reason if isinstance(reason, str) else None


class Harness:
    """One module's entry point under test."""

    def __init__(
        self, scripts: Path, wrapper: str, entry: str, namespace: str, scan_only: bool = False
    ) -> None:
        self.scripts = scripts
        self.wrapper = scripts / wrapper
        self.entry = scripts / entry
        self.namespace = namespace
        self.scan_only = scan_only  # the gate has no hook mode: a case writes its document and scans
        self.sh = shutil.which("sh") or "sh"
        self.bound: float | None = None  # set by `bounded`: the seconds a run may take
        self.scratch = Path(tempfile.mkdtemp(prefix=namespace + "-fixtures-"))
        atexit.register(shutil.rmtree, self.scratch, ignore_errors=True)
        self.unclocked = self.scratch / "unclocked-git"  # the folder of `UNCLOCKED_GIT`, put on PYTHONPATH
        self.unclocked.mkdir()
        (self.unclocked / "sitecustomize.py").write_text(UNCLOCKED_GIT, encoding="utf-8")

    def run_gate(
        self,
        stdin: str,
        args: Sequence[str] = (),
        env: Mapping[str, str] | None = None,
        command: Sequence[str] | None = None,
        cwd: Path | None = None,
    ) -> Result:
        """`cwd` is where the entry point runs — a generator that locates the repository from where it
        stands is run inside a consumer; a gate, which reads the path from its event, runs anywhere. The
        gate asks git with no clock (`UNCLOCKED_GIT`, last on PYTHONPATH) unless a `sitecustomize` the test
        puts before it sets the clocks."""
        merged = dict(os.environ)
        merged.pop("CLAUDE_PLUGIN_DATA", None)
        merged.update(env or {})
        merged["PYTHONPATH"] = os.pathsep.join(filter(None, [merged.get("PYTHONPATH"), str(self.unclocked)]))
        argv = [*(command or [self.sh, str(self.wrapper)]), *args]
        if self.bound is not None:
            return self.run_bounded(argv, stdin, merged, cwd, self.bound)
        done = subprocess.run(
            argv, input=stdin, text=True, capture_output=True, env=merged, check=False, cwd=cwd
        )
        return Result(done.returncode, done.stdout, done.stderr)

    @contextmanager
    def bounded(self, seconds: float) -> Iterator[None]:
        """Every `run_gate` inside the block ends within `seconds`: past them the run and everything it
        started is killed, and the result is `NO_ANSWER` — a gate that never answers is a red item, not an
        endless wait."""
        self.bound = seconds
        try:
            yield
        finally:
            self.bound = None

    def run_bounded(
        self, argv: Sequence[str], stdin: str, env: Mapping[str, str], cwd: Path | None, seconds: float
    ) -> Result:
        process = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=dict(env),
            cwd=cwd,
            start_new_session=True,  # its own process group: the kill reaches what the run started
        )
        try:
            out, err = process.communicate(stdin, timeout=seconds)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            out, err = process.communicate()
            line = f"NO ANSWER: the run did not end in {seconds:g} s and was killed with what it started\n"
            return Result(NO_ANSWER, out, err + line)
        return Result(process.returncode, out, err)

    def scratch_dir(self) -> Path:
        """A fresh directory under the runner's scratch root, removed when the runner exits."""
        return Path(os.path.realpath(tempfile.mkdtemp(dir=self.scratch)))

    def fresh_consumer(self, setup: Sequence[Write] = ()) -> Consumer:
        consumer = Consumer(self.scratch_dir()).build()
        for item in setup:
            consumer.write(item.target, item.text)
        if setup:
            consumer.commit()
        return consumer

    def run_case(self, case: Case) -> tuple[bool, str]:
        if self.scan_only:
            return self.run_scan_case(case)
        red = self.run_gate(event_json(self.fresh_consumer(case.setup).root, case.red))
        if red.code != 2:
            return False, f"red half exited {red.code}, not 2: {red.stdout}{red.stderr}".strip()
        if case.expect.render() not in red.stderr:  # what failed, why, and the fix: all three lines
            return (
                False,
                f"red fired but did not teach {case.expect.key}:\n{case.expect.render()}\n"
                f"got:\n{red.stderr.strip()}",
            )
        wanted = [
            f"RED: {case.expect.headline}",
            f"RED: 1 finding(s) — 1 document examined ({case.red.target})",
        ]
        if red_lines(red.stderr) != wanted:  # exactly the one finding and the count line, no other RED line
            return False, f"red taught more or less than {wanted}:\n{red.stderr.strip()}"
        if red_lines(red.stdout):  # and nothing RED on the other stream
            return False, f"red printed RED on stdout: {red.stdout.strip()}"
        green = self.run_gate(event_json(self.fresh_consumer(case.setup).root, case.green))
        line = f"GREEN: {self.namespace}: 1 document examined, {case.green_what}"
        if green.code != 0 or line not in green.stdout.splitlines() or red_lines(green.stdout + green.stderr):
            return (
                False,
                f"green half did not print {line!r} (exit {green.code}): {green.stdout}{green.stderr}",
            )
        return True, f"red → {case.expect.key}: {case.expect.headline}"

    def run_scan_case(self, case: Case) -> tuple[bool, str]:
        """A gate without a hook mode: each half is a document written into a fresh consumer and the
        scan run over it; red prints its verdict on stdout — the one finding whole and the count line
        typed by hand, and no other RED line — and green prints the whole green line."""
        if case.count is None or not isinstance(case.red, Write) or not isinstance(case.green, Write):
            return False, "a scan-only case needs its count line and two Writes"
        consumer = self.fresh_consumer(case.setup)
        consumer.write(case.red.target, case.red.text)
        red = self.run_gate("", args=["--scan", str(consumer.root)])
        if red.code != 2:
            return False, f"red half exited {red.code}, not 2: {red.stdout}{red.stderr}".strip()
        if case.expect.render() not in red.stdout:  # what failed, why, and the fix: all three lines
            return (
                False,
                f"red fired but did not teach {case.expect.key}:\n{case.expect.render()}\n"
                f"got:\n{red.stdout.strip()}",
            )
        wanted = [f"RED: {case.expect.headline}", case.count]
        if red_lines(red.stdout) != wanted:  # exactly the one finding and the count line, no other RED line
            return False, f"red taught more or less than {wanted}:\n{red.stdout.strip()}"
        if red_lines(red.stderr):  # and nothing RED on the other stream
            return False, f"red printed RED on stderr: {red.stderr.strip()}"
        consumer = self.fresh_consumer(case.setup)
        consumer.write(case.green.target, case.green.text)
        green = self.run_gate("", args=["--scan", str(consumer.root)])
        line = f"GREEN: {self.namespace}: {case.green_what}"
        if green.code != 0 or line not in green.stdout.splitlines() or red_lines(green.stdout + green.stderr):
            return (
                False,
                f"green half did not print {line!r} (exit {green.code}): {green.stdout}{green.stderr}",
            )
        return True, f"red → {case.expect.key}: {case.expect.headline}"
