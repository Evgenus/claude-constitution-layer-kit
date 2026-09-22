"""The case runner. It drives a module's real entry point — the POSIX wrapper, stdin, exit
code — with real PreToolUse events, exactly as the platform does.

A Case is one acceptance item with both halves: the red half must exit 2 AND teach the
expected message; the green half must pass. A fixture that proves only one half cannot
tell a working check from one that always answers the same. An Assertion is an acceptance
item with no failing half (an exit-code property, a count, a log line); the two kinds are
reported separately so they are never mistaken for each other.

The runner that imports this file has already put the module's scripts directory on the
import path — the runner only: no gate code ever edits the path.
"""

from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from const_gate.model import Finding
from consumer import Consumer

GREEN_MARK = "1 document examined, "  # the shared green line of hook mode; what follows is the module's


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


@dataclass(frozen=True)
class Case:
    number: int
    title: str
    red: Write | Edit
    green: Write | Edit
    expect: Finding
    setup: Sequence[Write] = ()


@dataclass(frozen=True)
class Assertion:
    number: int
    title: str
    check: Callable[[], tuple[bool, str]]


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


class Harness:
    """One module's entry point under test."""

    def __init__(self, scripts: Path, wrapper: str, entry: str, namespace: str) -> None:
        self.scripts = scripts
        self.wrapper = scripts / wrapper
        self.entry = scripts / entry
        self.namespace = namespace
        self.sh = shutil.which("sh") or "sh"
        self.scratch = Path(tempfile.mkdtemp(prefix=namespace + "-fixtures-"))
        atexit.register(shutil.rmtree, self.scratch, ignore_errors=True)

    def run_gate(
        self,
        stdin: str,
        args: Sequence[str] = (),
        env: Mapping[str, str] | None = None,
        command: Sequence[str] | None = None,
        cwd: Path | None = None,
    ) -> Result:
        """`cwd` is where the entry point runs — a generator that locates the repository from where it
        stands is run inside a consumer; a gate, which reads the path from its event, runs anywhere."""
        merged = dict(os.environ)
        merged.pop("CLAUDE_PLUGIN_DATA", None)
        merged.update(env or {})
        done = subprocess.run(
            [*(command or [self.sh, str(self.wrapper)]), *args],
            input=stdin,
            text=True,
            capture_output=True,
            env=merged,
            check=False,
            cwd=cwd,
        )
        return Result(done.returncode, done.stdout, done.stderr)

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
        red = self.run_gate(event_json(self.fresh_consumer(case.setup).root, case.red))
        if red.code != 2:
            return False, f"red half exited {red.code}, not 2: {red.stdout}{red.stderr}".strip()
        if case.expect.render() not in red.stderr:  # what failed, why, and the fix: all three lines
            return (
                False,
                f"red fired but did not teach {case.expect.key}:\n{case.expect.render()}\n"
                f"got:\n{red.stderr.strip()}",
            )
        green = self.run_gate(event_json(self.fresh_consumer(case.setup).root, case.green))
        if green.code != 0 or f"GREEN: {self.namespace}: {GREEN_MARK}" not in green.stdout:
            return False, f"green half did not pass (exit {green.code}): {green.stdout}{green.stderr}".strip()
        return True, f"red → {case.expect.key}: {case.expect.headline}"

    def run_all(self, cases: Sequence[Case], assertions: Sequence[Assertion]) -> int:
        failed = 0
        items: list[Case | Assertion] = [*cases, *assertions]
        for item in sorted(items, key=lambda i: i.number):
            kind = "red→green" if isinstance(item, Case) else "assertion"
            ok, evidence = self.run_case(item) if isinstance(item, Case) else item.check()
            failed += 0 if ok else 1
            print(f"[{'ok' if ok else 'FAIL'}] {item.number:>3}. ({kind}) {item.title}\n        {evidence}")
        total = len(cases) + len(assertions)
        print(
            f"{total - failed}/{total} acceptance items green — {len(cases)} red→green cases,"
            f" {len(assertions)} assertions examined"
        )
        return 0 if failed == 0 else 2


def expect(result: Result, code: int, text: str, where: str = "both") -> tuple[bool, str]:
    haystack = {"stdout": result.stdout, "stderr": result.stderr, "both": result.stdout + result.stderr}[
        where
    ]
    ok = result.code == code and text in haystack
    return ok, (
        f"exit {result.code}: {text}"
        if ok
        else f"wanted exit {code} teaching {text!r}; got exit {result.code}: {haystack.strip()}"
    )


def broken_first_line(result: Result, first_line: str) -> tuple[bool, str]:
    """A configuration failure: exit 1 — never 2, never 0 — and its line is the FIRST stderr line."""
    first = result.stderr.splitlines()[0] if result.stderr else ""
    ok = result.code == 1 and first == first_line
    return ok, (
        f"exit 1, first stderr line: {first}"
        if ok
        else f"wanted exit 1 with first line {first_line!r}; got exit {result.code}: {result.stderr.strip()}"
    )
