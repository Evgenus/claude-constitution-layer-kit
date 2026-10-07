"""The case runner. It drives a module's real entry point — the POSIX wrapper, stdin, exit
code — with real PreToolUse events, exactly as the platform does.

A Case is one acceptance item with both halves: the red half must exit 2 AND teach the
expected message, its RED lines exactly that finding's headline and the count line, so a
second finding or a stray line fails it; the green half must pass, printing the whole green
line the case names. A fixture that proves only one half cannot tell a working check from
one that always answers the same. An Assertion is an acceptance item with no failing half
(an exit-code property, a count, a log line); the two kinds are reported separately so they
are never mistaken for each other.

The runner that imports this file reaches the shared package and the module's own packages
through links in its own folder, which Python puts first on the import path: no file a module
ships edits the import path of its own process, the runner included.
"""

from __future__ import annotations

import atexit
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from const_gate.model import Finding
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
        if red_lines(red.stderr) != wanted:  # exactly the one finding and the count line, nothing more
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
        typed by hand, nothing more — and green prints the whole green line."""
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
        if red_lines(red.stdout) != wanted:  # exactly the one finding and the count line, nothing more
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

    def run_all(
        self, cases: Sequence[Case], assertions: Sequence[Assertion], argv: Sequence[str] | None = None
    ) -> int:
        """Run every item, or with `--item <n>[,<n>…]` on the command line only the items named.
        A filtered run never prints the full line, `N/T acceptance items green — …`, which only a full
        run may print: its last line says how many items of how many ran and that it is not a full
        pass. A filter the runner cannot honour — an unknown number, a malformed list, any other
        argument — is a configuration failure, exit 1, never a silent full or empty run."""
        items: list[Case | Assertion] = sorted([*cases, *assertions], key=lambda i: i.number)
        total = len(items)
        try:
            wanted = item_filter(sys.argv[1:] if argv is None else argv, [i.number for i in items])
        except Misuse as misuse:
            print(f"BROKEN: {misuse}", file=sys.stderr)
            print(f"BROKEN: the runner could not run — 0 of {total} items run", file=sys.stderr)
            return 1
        failed = run = 0
        for item in items:
            if wanted is not None and item.number not in wanted:
                continue
            kind = "red→green" if isinstance(item, Case) else "assertion"
            ok, evidence = self.run_case(item) if isinstance(item, Case) else item.check()
            failed += 0 if ok else 1
            run += 1
            print(f"[{'ok' if ok else 'FAIL'}] {item.number:>3}. ({kind}) {item.title}\n        {evidence}")
        if wanted is not None:
            print(f"{run - failed}/{run} selected items green — {run} of {total} items run, not a full pass")
        else:
            print(
                f"{total - failed}/{total} acceptance items green — {len(cases)} red→green cases,"
                f" {len(assertions)} assertions examined"
            )
        return 0 if failed == 0 else 2


class Misuse(Exception):
    """The runner's command line cannot be honoured; the message says what, why and the fix."""


ITEM_FLAG = "--item"
ITEM_LIST = re.compile(r"[0-9]+(?:,[0-9]+)*")
RUN_FORMS = f"run with no arguments for a full run, or with {ITEM_FLAG} <n>[,<n>…] to run only those items"


def item_filter(argv: Sequence[str], numbers: Sequence[int]) -> frozenset[int] | None:
    """The item numbers `--item <n>[,<n>…]` (or `--item=<n>[,<n>…]`) names, or None for a full run
    when the command line is empty. Every number must be one of `numbers`."""
    if not argv:
        return None
    if len(argv) == 2 and argv[0] == ITEM_FLAG:
        given = argv[1]
    elif len(argv) == 1 and argv[0].startswith(ITEM_FLAG + "="):
        given = argv[0].removeprefix(ITEM_FLAG + "=")
    else:
        raise Misuse(
            f"misinvocation: {shlex.join(argv)} — why: the runner takes one option, and an argument it"
            f" ignored could pass for a filter — fix: {RUN_FORMS}"
        )
    if ITEM_LIST.fullmatch(given) is None:
        raise Misuse(
            f"{ITEM_FLAG} {given!r} is no list of item numbers — why: a filter the runner cannot read"
            f" would run nothing, or everything — fix: {RUN_FORMS}"
        )
    wanted = frozenset(int(part) for part in given.split(","))
    unknown = sorted(wanted - set(numbers))
    if unknown:
        held = ", ".join(spans(sorted(set(numbers))))
        raise Misuse(
            f"{ITEM_FLAG} {given}: no item numbered {', '.join(map(str, unknown))} in this runner — why: a"
            f" filter that matches nothing runs nothing, and nothing run looks green — fix: name items this"
            f" runner holds: {held}"
        )
    return wanted


def spans(numbers: Sequence[int]) -> list[str]:
    """Sorted numbers as runs: [1, 2, 3, 101] gives ["1–3", "101"]."""
    runs: list[list[int]] = []
    for number in numbers:
        if runs and number == runs[-1][1] + 1:
            runs[-1][1] = number
        else:
            runs.append([number, number])
    return [f"{a}–{b}" if a != b else f"{a}" for a, b in runs]


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
