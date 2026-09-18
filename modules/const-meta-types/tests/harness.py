"""The case runner. It drives the real entry point — the POSIX wrapper, stdin, exit code —
with real PreToolUse events, exactly as the platform does.

A Case is one acceptance item with both halves: the red half must exit 2 AND teach the
expected message; the green half must pass. A fixture that proves only one half cannot
tell a working check from one that always answers the same. An Assertion is an acceptance
item with no failing half (an exit-code property, a count, a log line); the two kinds are
reported separately so they are never mistaken for each other.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
WRAPPER = SCRIPTS / "check-governed-document.sh"
ENTRY = SCRIPTS / "check-governed-document.py"
sys.path.insert(0, str(SCRIPTS))           # test code only: shipped code never edits the path

from meta_types_gate.model import Finding  # noqa: E402

from consumer import Consumer  # noqa: E402


@dataclass(frozen=True)
class Write:
    target: str
    text: str


@dataclass(frozen=True)
class Edit:
    target: str
    old: str
    new: str


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


def event_json(repo: Path, action: Write | Edit, session: str = "fixture-session") -> str:
    tool_input: dict[str, object] = {"file_path": str(repo / action.target)}
    if isinstance(action, Write):
        tool_input["content"] = action.text
    else:
        tool_input.update({"old_string": action.old, "new_string": action.new, "replace_all": False})
    return json.dumps({"hook_event_name": "PreToolUse", "session_id": session, "cwd": str(repo),
                       "tool_name": type(action).__name__, "tool_input": tool_input})


def run_gate(stdin: str, args: Sequence[str] = (), env: Mapping[str, str] | None = None,
             command: Sequence[str] | None = None) -> Result:
    merged = dict(os.environ)
    merged.pop("CLAUDE_PLUGIN_DATA", None)
    merged.update(env or {})
    done = subprocess.run([*(command or ["/bin/sh", str(WRAPPER)]), *args], input=stdin, text=True,
                          capture_output=True, env=merged, check=False)
    return Result(done.returncode, done.stdout, done.stderr)


def fresh_consumer(tmp: str, setup: Sequence[Write] = ()) -> Consumer:
    consumer = Consumer(Path(os.path.realpath(tmp))).build()
    for item in setup:
        consumer.write(item.target, item.text)
    if setup:
        consumer.commit()
    return consumer


def run_case(case: Case) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        consumer = fresh_consumer(tmp, case.setup)
        red = run_gate(event_json(consumer.root, case.red))
    if red.code != 2:
        return False, f"red half exited {red.code}, not 2: {red.stdout}{red.stderr}".strip()
    if case.expect.headline not in red.stderr:
        return False, f"red fired but did not teach {case.expect.key} {case.expect.headline!r}: {red.stderr.strip()}"
    with tempfile.TemporaryDirectory() as tmp:
        consumer = fresh_consumer(tmp, case.setup)
        green = run_gate(event_json(consumer.root, case.green))
    if green.code != 0 or "1 document examined, governed by" not in green.stdout:
        return False, f"green half did not pass (exit {green.code}): {green.stdout}{green.stderr}".strip()
    return True, f"red → {case.expect.key}: {case.expect.headline}"


def run_all(cases: Sequence[Case], assertions: Sequence[Assertion]) -> int:
    failed = 0
    items: list[Case | Assertion] = [*cases, *assertions]
    for item in sorted(items, key=lambda i: i.number):
        kind = "red→green" if isinstance(item, Case) else "assertion"
        ok, evidence = run_case(item) if isinstance(item, Case) else item.check()
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {item.number:>2}. ({kind}) {item.title}\n        {evidence}")
    total = len(cases) + len(assertions)
    print(f"{total - failed}/{total} acceptance items green — {len(cases)} red→green cases,"
          f" {len(assertions)} assertions examined")
    return 0 if failed == 0 else 2
