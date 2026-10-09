"""The acceptance items of what every gate shares — the exit-code split, the absence of each
external tool, hook input, paths, the warn channel, the output log — written once and run by
each module's runner through that module's real entry point.

A module hands over a Subject: its harness, a function that runs its gate on a prepared
consumer, one write it passes and one it blocks. Each item carries its number in the file, from
101 on, the numbers unique and rising, and the number a module gives must equal the first
(`shared_assertions` raises a ValueError for either).
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from const_gate import envelope as envelope_reader
from const_gate import messages, pipeline, preflight, repository
from const_gate.envelope import ID_RE, declared_policy, document_id, parse_envelope
from const_gate.model import DECLARATION, DIALECT, Broken, EnvelopeState, Finding, SharedKey
from const_gate.output import ROTATE_AT, log_name
from const_gate.repository import list_markdown
from consumer import ROOT_POLICY
from harness import (
    Assertion,
    Edit,
    Harness,
    Result,
    Write,
    ask_reason,
    bash_json,
    broken_first_line,
    event_json,
    expect,
    red_lines,
    stop_json,
)

NO_ENVELOPE = "# Fixture\n\nNo envelope at all.\n"

# Run at the start of a gate's process, through a `sitecustomize` on PYTHONPATH — any module's entry
# point, whatever its wrapper. It logs the `timeout=` each git call is given, one line, the call after it;
# and where the environment names a trigger and a lower budget, it lowers the budget of the one call whose
# arguments hold the trigger — and only where the gate gave that call a budget at all, so that a gate with
# none stays without one. Every other call keeps the real budget, so a loaded machine cannot trip it.
GIT_PATCH = """\
import os
import subprocess
import sys

scripts = os.environ["GIT_PATCH_SCRIPTS"]
sys.path.insert(0, scripts)
from const_gate import repository

sys.path.remove(scripts)
lowered = os.environ.get("GIT_PATCH_SECONDS")
trigger = os.environ.get("GIT_PATCH_TRIGGER")
log, run = os.environ["GIT_PATCH_LOG"], subprocess.run


def spy(command, *args, **kwargs):
    if command[0] == "git":
        with open(log, "a") as out:
            out.write(repr(kwargs.get("timeout")) + " " + repr(command[1:]) + "\\n")
        if lowered and trigger in command[1:] and kwargs.get("timeout") is not None:
            repository.GIT_SECONDS = kwargs["timeout"] = float(lowered)
    return run(command, *args, **kwargs)


subprocess.run = spy
"""
HANG_SECONDS = 0.5  # the budget of the one call a hang case lowers it for: the case waits well under a second
# What a hang case allows the whole run, the gate's start-up included. It only stops an endless wait, so it is
# far above anything a loaded machine takes; the assertion that matters is the line from the 0.5 s budget.
HANG_BOUND = 20.0


def git_patch(
    h: Harness, seconds: float | None = None, trigger: str | None = None
) -> tuple[dict[str, str], Path]:
    """The environment that makes a gate's process log the `timeout=` of each git call it makes, and,
    with `seconds` and a `trigger`, give the call whose arguments hold the trigger that many seconds;
    with the log it writes."""
    folder = h.scratch_dir()
    (folder / "sitecustomize.py").write_text(GIT_PATCH, encoding="utf-8")
    log = folder / "git-calls"
    env = {
        "PYTHONPATH": os.pathsep.join(filter(None, [str(folder), os.environ.get("PYTHONPATH")])),
        "GIT_PATCH_SCRIPTS": str(h.scripts),
        "GIT_PATCH_LOG": str(log),
    }
    if seconds is not None and trigger is not None:
        env["GIT_PATCH_SECONDS"] = repr(seconds)
        env["GIT_PATCH_TRIGGER"] = trigger
    return env, log


def git_timeouts(log: Path) -> list[str]:
    """The `timeout=` of each git call the log holds, as `repr` wrote it: "None" for no clock."""
    return [line.split(" ", 1)[0] for line in log.read_text().splitlines()] if log.exists() else []


def hook_budget(calls: list[str]) -> tuple[bool, str]:
    """Every git call of a process declared a hook carried the hook's budget, and there was one."""
    return bool(calls) and set(calls) == {repr(repository.GIT_SECONDS)}, f"the git calls' timeouts: {calls}"


def no_clock(calls: list[str]) -> tuple[bool, str]:
    """Every git call of a scan or an act carried no timeout, and there was one."""
    return bool(calls) and set(calls) == {"None"}, f"the git calls' timeouts: {calls}"


class GateOn(Protocol):
    def __call__(
        self,
        action: Write | Edit,
        dials_patch: dict[str, object] | None = None,
        env: dict[str, str] | None = None,
        raw_dials: str | None = None,
        files: dict[str, str] | None = None,
        remove: str | None = None,
    ) -> tuple[Result, Path]: ...


class OwnPatch(Protocol):
    def __call__(self, **dials: object) -> dict[str, object]: ...


class Claim(Protocol):
    def __call__(self, territory: Sequence[str]) -> dict[str, object]: ...


@dataclass(frozen=True)
class PatternDial:
    """A dial of the module's own that holds path patterns, for the item that gives it a pattern git
    would read as a comment."""

    path: str  # the dial as a person finds it under the module's namespace: "territories", "lanes[1].home"
    patch: Callable[[str], dict[str, object]]  # the dials patch that puts the pattern there and keeps
    # the module working


@dataclass(frozen=True)
class Subject:
    harness: Harness
    gate_on: GateOn
    own: OwnPatch  # a patch of the module's namespace that keeps it working
    valid: Write  # a write the gate passes, its green line ending in `green`
    red: Write  # a write the gate blocks
    red_finding: Finding
    green: str  # what the green line says `valid` is: `governed by <policy>`, or the module's words
    territory: Sequence[str]  # the patterns of the territory that holds `valid` and `red`
    claim: Claim  # the dials patch that declares that territory with other patterns
    resolves_policies: bool = True  # False: the gate reads only its own dials, so the items about
    # the root policy and the policies' documents are not its own, and are left out
    bare_readme: str = "0 documents examined"  # what the count line says of a README with no envelope
    # at the repository's top: outside every territory for most gates, examined by one that covers
    # every Markdown file
    judges_envelopes: bool = True  # False: an envelope nobody can read is no finding of this gate,
    # so the item about one is left out, and the module proves in its own items that it is no crash
    event_driven: bool = True  # False: the module is only a generator — no hook event, no verdict,
    # no scan — so the items about hook input, paths and skips, the warn channel and the scan are
    # not its own and are left out; `gate_on` then turns the Write it is handed into the generator's
    # command line, `red` being a run it refuses and `valid` one it completes
    closing: str = messages.c11_broken_count()  # the line that closes a failure: a gate's count
    # line, or a generator's own ("nothing was written")
    act_args: Sequence[str] = ()  # a generator only: the arguments of a run that completes on a fresh
    # consumer, from inside it — for the item that runs the scripts copied with links followed
    event: str = "PreToolUse"  # the hook event the gate is wired to. "Stop": the gate examines the
    # repository the event's cwd lies in and no written file, so the items about one are left out,
    # and so are those about git's file list, the territory's scratch repository and a document a
    # scan reads (`about_listing`), which such a gate never reaches;
    # `gate_on` is still handed `valid` and `red`, and turns each into the tree the gate passes or
    # blocks; where an item builds a payload itself it builds a Stop one
    outside: str | None = None  # the module's skip reason for `red.target` once a negated pattern takes
    # it out of the territory, typed by hand; required by the item about negation wherever it runs
    long_value: Write | None = None  # a write the gate blocks with one finding that echoes a value of
    # 12,000 characters "x"; None leaves the item about a value cut short out
    # `event` may also be "Bash": a PreToolUse gate on the shell tool, which examines the command the
    # event carries and no written file — the items left out are those a Stop gate leaves out; `valid`
    # and `red` are then Writes whose `text` is the command, `target` unused, and a payload an item
    # builds itself is the shell tool's
    ask: bool = False  # True: the gate's block is an `ask` verdict — exit 0, one JSON object on stdout
    # asking the platform to prompt, the finding in its reason — so the items about a red run read
    # that reason where they would read stderr, and expect exit 0 where they would expect 2
    hook_lists_files: bool = True  # False: the gate's hook mode never asks git for the file list — it
    # matches the written file against its territories by pattern alone — so the item about git failing
    # to list the files runs the scan on the prepared consumer, where the gate does ask
    noted: Write | None = None  # a write the gate passes with one note; None leaves the item about notes
    # reaching the model out
    note: str = ""  # the note `noted` earns, typed by hand
    pattern_dial: PatternDial | None = None  # a dial of the module's own that holds path patterns;
    # None leaves the item about a pattern git would misread in it out
    scan_only: bool = False  # True: the gate has no hook mode — it scans a tree and judges no single
    # write, and run as a hook it is its own configuration failure — so the items about hook input,
    # a written file, the warn channel and a negated pattern's skip are not its own and are left out;
    # `gate_on` then writes the action's file into the consumer and runs `--scan` there, `valid` and
    # `red` being the documents the scan passes or reports, `green` the whole green line of a scan
    # over the consumer holding `valid` alone, and the items about a red run read stdout, where a
    # scan prints its verdict; `bare_readme` is that scan's green line with a README at the top


def shared_assertions(s: Subject, first: int) -> list[Assertion]:  # noqa: C901 — a flat list of small items
    h, ns = s.harness, s.harness.namespace
    stop = s.event == "Stop"
    shell = s.event == "Bash"
    no_file = stop or shell  # the gate examines no written file: the items about one are not its own

    def payload(root: Path, action: Write | Edit) -> str:
        """The event an item sends itself: the write, or, for a Stop gate, a Stop in that repository,
        or, for a shell gate, the shell tool with the action's text as its command."""
        if stop:
            return stop_json(root)
        if shell:
            return bash_json(root, action.text if isinstance(action, Write) else action.new)
        return event_json(root, action)

    def red_said(result: Result) -> str:
        """What a red run said: stderr for a block, the reason of the ask verdict for an asking gate,
        stdout for a scan."""
        if s.scan_only:
            return result.stdout
        return (ask_reason(result) or "") if s.ask else result.stderr

    red_code = 0 if s.ask else 2

    def scan_args(root: Path) -> list[str]:
        """The scan of a gate without a hook mode, on the consumer's root."""
        return ["--scan", str(root)]

    def broken(result: Result, failure: Broken) -> tuple[bool, str]:
        return broken_as_typed(result, failure.render())

    def broken_as_typed(result: Result, line: str) -> tuple[bool, str]:
        """The failure's line first — typed by hand where the item types it — then the closing line."""
        ok, evidence = broken_first_line(result, line)
        counted = s.closing in result.stderr  # a run that examined, or changed, nothing says so
        return ok and counted, evidence if counted else f"no count line after: {evidence}"

    def bin_with(*tools: str) -> str:
        """A PATH directory holding only the named tools, to simulate the absence of the rest."""
        directory = h.scratch_dir()
        for tool in tools:
            source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
            assert source, tool
            os.symlink(source, directory / tool)
        return str(directory)

    # ---------------------------------------------------------------- the dials file

    def malformed_dials() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, raw_dials="root-policy: [\n")
        return expect(result, 1, "BROKEN: constitution.yaml is not valid YAML", "stderr")

    def dials_not_mapping() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, raw_dials="- a\n- b\n")
        line = (  # typed by hand: both kernel keys, the second said to be needed only off the default
            "BROKEN: constitution.yaml is not a mapping — fix: the file holds top-level keys: root_policy,"
            " and territory_dialect when the dialect is not gitignore, then one namespace per policy or"
            " module"
        )
        return broken_as_typed(result, line)

    def dials_bad_severity() -> tuple[bool, str]:
        line = (  # typed by hand
            f"BROKEN: constitution.yaml: {ns}.severity must be block or warn — fix: under {ns}, set severity:"
            " block or severity: warn, or remove that line"
        )
        return broken_as_typed(s.gate_on(s.valid, dials_patch=s.own(severity="loud"))[0], line)

    def dials_own_namespace() -> tuple[bool, str]:
        line = (  # typed by hand
            f"BROKEN: constitution.yaml: namespace '{ns}' must be a mapping of this module's dials — fix:"
            " write this module's dials under it as a mapping, or remove the key"
        )
        return broken_as_typed(s.gate_on(s.valid, dials_patch={ns: "x"})[0], line)

    def dials_comment_pattern() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"notes-policy": {"territory": ["#docs/notes/**"]}})
        line = (  # typed by hand: the dial's whole path, then the pattern in single quotes
            "BROKEN: constitution.yaml: notes-policy.territory holds a pattern git would not read as one:"
            " '#docs/notes/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a line"
            " break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break"
        )
        return broken_as_typed(result, line)

    def dials_unsupported_dialect() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"territory_dialect": "regex"})
        return broken(result, messages.c5_dialect_unsupported("regex"))

    def dials_own_namespace_null() -> tuple[bool, str]:
        return broken(s.gate_on(s.valid, dials_patch={ns: None})[0], messages.c5_own_namespace_not_mapping())

    def dials_other_pairs() -> tuple[bool, str]:
        pairs: list[tuple[dict[str, object], Broken | str]] = [  # a string is a line typed by hand
            (
                {"root_policy": "/absolute/root.md"},
                "BROKEN: constitution.yaml: root_policy must be a repository-relative path — fix:"
                " root_policy: <path of the root policy, relative to the repository root>",
            ),
            (
                {"territory_dialect": ""},
                "BROKEN: constitution.yaml: territory_dialect must be a non-empty string — fix: remove the"
                " key, or set territory_dialect: gitignore — the one dialect supported",
            ),
            ({"notes-policy": "docs/notes/**"}, messages.c5_namespace_not_mapping("notes-policy")),
            ({"notes-policy": {"territory": "docs/notes/**"}}, messages.c5_territory_shape("notes-policy")),
            # a list holding a blank string is no list of non-empty strings
            (
                {"notes-policy": {"territory": ["docs/notes/**", " "]}},
                messages.c5_territory_shape("notes-policy"),
            ),
            (
                s.own(log_dir="/absolute/logs"),
                f"BROKEN: constitution.yaml: {ns}.log_dir must be a repository-relative directory — fix:"
                f" under {ns}, set log_dir: <a git-ignored directory>, or remove that line",
            ),
            # a path that leaves the repository by `..`, written plain or after a step down
            ({"root_policy": "../root.md"}, messages.c5_root_policy_path()),
            ({"root_policy": "docs/../../root.md"}, messages.c5_root_policy_path()),
            (s.own(log_dir="../logs"), messages.c5_log_dir()),
            (s.own(log_dir="logs/../../logs"), messages.c5_log_dir()),
            ({"root_policy": " "}, messages.c5_root_policy_path()),
        ]
        results = [
            broken_as_typed(s.gate_on(s.valid, dials_patch=patch)[0], failure)
            if isinstance(failure, str)
            else broken(s.gate_on(s.valid, dials_patch=patch)[0], failure)
            for patch, failure in pairs
        ]
        failed = [evidence for ok, evidence in results if not ok]
        # the same dials written the long way read as written the short way: the verdict is the plain
        # run's, never a refusal — `./` and `//` dropped, a step down and back up undone
        plain = s.gate_on(s.valid)[0]
        long_way: list[tuple[str, dict[str, object]]] = [
            ("root_policy", {"root_policy": "./docs//../" + ROOT_POLICY}),
            # the kernel's one dialect, written out: a kernel-owned key, never refused as a namespace
            ("territory_dialect", {"territory_dialect": DIALECT}),
        ]
        for name, patch in long_way:
            got = s.gate_on(s.valid, dials_patch=patch)[0]
            if (got.code, "BROKEN" in got.stderr) != (plain.code, "BROKEN" in plain.stderr):
                failed.append(f"{name}: exit {got.code}, the plain run exit {plain.code}: {got.stderr[:200]}")
        return not failed, "; ".join(failed) or (
            f"{len(pairs)} dial failures, each exit 1 with its own line; the long way reads as plain"
        )

    def root_missing() -> tuple[bool, str]:
        return broken(s.gate_on(s.valid, remove=ROOT_POLICY)[0], messages.c6_root_missing(ROOT_POLICY))

    def root_without_id() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, files={ROOT_POLICY: NO_ENVELOPE})
        return broken(result, messages.c7_root_without_id(ROOT_POLICY))

    def root_claims_nothing() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"root-policy": {}})
        return broken(result, messages.c8_root_claims_nothing("root-policy"))

    def root_outside_own_territory() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"root-policy": {"territory": ["docs/elsewhere/**"]}})
        return broken(
            result, messages.c9_root_outside_own_territory(ROOT_POLICY, ["docs/elsewhere/**"], "root-policy")
        )

    # ---------------------------------------------------------------- absence of what the gate needs

    def python_absent() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, env={"PATH": bin_with("dirname")})
        return expect(result, 1, f"BROKEN: {ns} needs python3", "stderr")

    def python_below_floor() -> tuple[bool, str]:
        """The entry file run, under the interpreter at hand, as one a minor below the floor would run it:
        a shim sets `sys.version_info` to that minor, puts the entry's folder first on the path as a real
        run does, and runs the entry as `__main__`. The line is C14's, up to its clause."""
        floor, below = preflight.FLOOR, (preflight.FLOOR[0], preflight.FLOOR[1] - 1)
        line = (
            f"BROKEN: {ns} needs Python {floor[0]}.{floor[1]} or newer, found {below[0]}.{below[1]}"
            " — fix: install a current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
        )
        shim = (
            "import os, runpy, sys\n"
            "entry, below = sys.argv[1], tuple(int(n) for n in sys.argv[2].split('.'))\n"
            "sys.version_info = (*below, 0, 'final', 0)\n"
            "sys.argv = [entry]\n"
            "sys.path.insert(0, os.path.dirname(entry))\n"
            "runpy.run_path(entry, run_name='__main__')\n"
        )
        result = h.run_gate(
            "{}", command=[sys.executable, "-c", shim, str(h.entry), f"{below[0]}.{below[1]}"]
        )
        first = result.stderr.splitlines()[0] if result.stderr else ""
        ok = result.code == 1 and (first == line or first.startswith(line + " — "))
        if ok:
            return True, f"exit 1 under a faked Python {below[0]}.{below[1]}, first stderr line: {first}"
        return False, (
            f"wanted exit 1 under a faked Python {below[0]}.{below[1]} with first stderr line {line!r},"
            f" at its end or followed by ' — ' and a clause; got exit {result.code}, first stderr line"
            f" {first!r}, stderr ends {result.stderr.strip()[-200:]!r},"
            f" stdout {result.stdout.strip()[:200]!r}"
        )

    def git_absent() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, env={"PATH": bin_with("python3", "dirname")})
        return broken(result, messages.c3_git_missing())

    def git_failing() -> tuple[bool, str]:
        """A git that fails for any reason other than "not a repository" is never a green skip."""
        config = h.scratch_dir() / "gitconfig"
        config.write_text("[broken\n", encoding="utf-8")
        result, _ = s.gate_on(s.valid, env={"GIT_CONFIG_GLOBAL": str(config)})
        return expect(result, 1, "BROKEN: git could not answer where the repository is", "stderr")

    def library_absent() -> tuple[bool, str]:
        shadow = h.scratch_dir()
        (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
        result, _ = s.gate_on(s.valid, env={"PYTHONPATH": str(shadow)})
        return broken(result, messages.c2_library_missing("PyYAML", str(preflight.requirements_file())))

    def shared_code_absent() -> tuple[bool, str]:
        """The plugin as an install that dropped the link to the shared code would leave it."""
        plugin = h.scratch_dir() / "plugin"
        shutil.copytree(h.scripts, plugin / "scripts", symlinks=True)
        shared = plugin / "scripts" / "const_gate"
        shared.unlink() if shared.is_symlink() else shutil.rmtree(shared)
        consumer = h.fresh_consumer()
        result = h.run_gate(
            payload(consumer.root, s.valid), command=[h.sh, str(plugin / "scripts" / h.wrapper.name)]
        )
        first = expect(result, 1, f"BROKEN: {ns} is installed without its shared code", "stderr")
        shared.mkdir()  # an install that left an empty directory behind: importable, and still no code
        result = h.run_gate(
            payload(consumer.root, s.valid), command=[h.sh, str(plugin / "scripts" / h.wrapper.name)]
        )
        second = expect(result, 1, f"BROKEN: {ns} is installed without its shared code", "stderr")
        return first[0] and second[0], f"link removed: {first[1][:60]}…; empty directory: {second[1][:60]}…"

    def copy_with_links_followed() -> tuple[bool, str]:
        """The plugin's scripts copied the way an install copies them: what the link points at."""
        plugin = h.scratch_dir() / "plugin"
        shutil.copytree(h.scripts, plugin / "scripts", symlinks=False)
        shutil.copy(preflight.requirements_file(), plugin / "requirements.txt")
        copied = [h.sh, str(plugin / "scripts" / h.wrapper.name)]
        consumer = h.fresh_consumer()
        if not s.event_driven:  # a generator: a run that completes, from inside the consumer
            result = h.run_gate("", args=s.act_args, command=copied, cwd=consumer.root)
            return expect(result, 0, s.green, "stdout")
        if s.scan_only:  # the consumer holding the passed document, scanned by the copy
            consumer.write(s.valid.target, s.valid.text)
            result = h.run_gate("", args=scan_args(consumer.root), command=copied)
            return expect(result, 0, s.green, "stdout")
        if no_file:  # a clean consumer at a turn's end, or a command the gate passes: the gate's green
            result = h.run_gate(payload(consumer.root, s.valid), command=copied)
            return expect(result, 0, s.green, "stdout")
        result = h.run_gate(event_json(consumer.root, Write("README.md", NO_ENVELOPE)), command=copied)
        return expect(result, 0, s.bare_readme, "stdout")

    def unexpected_failure() -> tuple[bool, str]:
        """Not fail-open: an exception nobody planned for exits 1, its BROKEN line first, the
        traceback after it."""
        shadow = h.scratch_dir()
        (shadow / "yaml.py").write_text(
            "class YAMLError(Exception): pass\n\n\n"
            "def safe_load(text): raise RuntimeError('simulated defect')\n",
            encoding="utf-8",
        )
        result, _ = s.gate_on(s.valid, env={"PYTHONPATH": str(shadow)})
        failure = messages.c12_unexpected("RuntimeError: simulated defect")
        ok, evidence = broken(result, failure)
        return ok and "Traceback (most recent call last)" in result.stderr, evidence

    # ---------------------------------------------------------------- invocation and hook input

    def misinvocation() -> tuple[bool, str]:
        return expect(h.run_gate("", args=["--bogus"]), 1, "BROKEN: misinvocation:", "stderr")

    def help_is_not_special() -> tuple[bool, str]:
        return expect(h.run_gate("", args=["--help"]), 1, "BROKEN: misinvocation:", "stderr")

    def abbreviated_flag() -> tuple[bool, str]:
        return expect(h.run_gate("", args=["--sc", "."]), 1, "BROKEN: misinvocation:", "stderr")

    def unparseable_input() -> tuple[bool, str]:
        return expect(
            h.run_gate("not json"), 1, "BROKEN: hook input cannot be used (it is not JSON", "stderr"
        )

    def input_not_an_object() -> tuple[bool, str]:
        detail = "it is JSON, but the top level is not an object"  # typed by hand
        return broken(h.run_gate("[1, 2]"), messages.c12_input(detail))

    def malformed_event() -> tuple[bool, str]:
        event = json.dumps({"tool_name": "Write", "tool_input": ["not", "an", "object"]})
        return broken(h.run_gate(event), messages.c12_input(messages.detail_tool_input("Write", "file_path")))

    def edit_without_fields() -> tuple[bool, str]:
        event = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "/x/a.md", "old_string": "a"}})
        return broken(h.run_gate(event), messages.c12_input(messages.detail_tool_input("Edit", "new_string")))

    def stdout_cannot_encode() -> tuple[bool, str]:
        """The count line carries a dash; a stream that cannot encode it must not swallow the line."""
        if no_file:
            result, _ = s.gate_on(s.valid, env={"PYTHONIOENCODING": "ascii"})
            return expect(result, 0, s.green, "stdout")
        result, _ = s.gate_on(Write("README.md", NO_ENVELOPE), env={"PYTHONIOENCODING": "ascii"})
        return expect(result, 0, s.bare_readme, "stdout")

    def deeply_nested_envelope() -> tuple[bool, str]:
        """Brackets nested past the parser's depth are an unreadable envelope, never a crash that
        lets the write through."""
        text = "---\nid: " + "[" * 600 + "\n---\n"
        result, _ = s.gate_on(Write(s.valid.target, text))  # a path where the envelope is the only defect
        return expect(result, 2, "brackets are nested too deeply to read", "stderr")  # typed by hand

    def other_tool() -> tuple[bool, str]:
        event = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x.md"}})
        skip = messages.g1_green_skip(messages.g1_skip_no_file("Read"))
        return expect(h.run_gate(event), 0, skip, "stdout")

    def scan_missing_path() -> tuple[bool, str]:
        result = h.run_gate("", args=["--scan", "no-such-directory"])
        return broken(result, messages.c12_scan_path("no-such-directory"))

    def scan_outside_repository() -> tuple[bool, str]:
        directory = h.scratch_dir()
        result = h.run_gate(
            "", args=["--scan", str(directory)], env={"GIT_CEILING_DIRECTORIES": str(directory.parent)}
        )
        return broken(result, messages.c12_no_repo(str(directory)))

    def scan_forms() -> tuple[bool, str]:
        """--scan=DIR, and a scan started from a subdirectory, examine the same repository."""
        _, root = s.gate_on(s.valid, files={s.valid.target: s.valid.text})
        whole = h.run_gate("", args=["--scan", str(root)])
        equals = h.run_gate("", args=[f"--scan={root}"])
        below = h.run_gate("", args=["--scan", str((root / s.valid.target).parent)])
        ok = whole.code == 0 and whole.stdout == equals.stdout == below.stdout
        return ok, whole.stdout.strip().splitlines()[-1] if ok else f"{whole}\n{equals}\n{below}"

    # ---------------------------------------------------------------- paths and skips

    def not_markdown() -> tuple[bool, str]:
        """Markdown means `.md`: a `.markdown` file is skipped, and the reason names the ending, not
        the format, since the file may well be Markdown."""
        target = str(Path(s.valid.target).with_suffix(".markdown"))
        result, root = s.gate_on(Write(target, "x"))
        skip = messages.g1_green_skip(messages.g1_skip_not_markdown(str(root / target)))
        ok, said = expect(result, 0, skip, "stdout")
        # a path of over 80 characters with a line break in it: shown whole, the break escaped — typed
        # by hand, since the reader opens that path and the line is read by a later step
        name = "docs/" + "d" * 90 + "\nx.markdown"
        long_result, long_root = s.gate_on(Write(name, "x"))
        line = (
            f"GREEN: {ns}: 0 documents examined — {long_root}/docs/"
            + "d" * 90
            + "\\nx.markdown is not a .md file"
        )
        long_ok, long_said = expect(long_result, 0, line, "stdout")
        return ok and long_ok, said if ok and long_ok else f"{said}; {long_said}"

    def relative_path() -> tuple[bool, str]:
        """A relative file_path is resolved against the event's cwd."""
        _, root = s.gate_on(s.valid)  # prepares the consumer; the event below is the one judged
        event = json.loads(event_json(root, s.red))
        event["tool_input"]["file_path"] = s.red.target
        return expect(h.run_gate(json.dumps(event)), 2, s.red_finding.render(), "stderr")

    def outside_any_repository() -> tuple[bool, str]:
        directory = h.scratch_dir()
        event = payload(directory, Write("loose.md", NO_ENVELOPE))
        result = h.run_gate(event, env={"GIT_CEILING_DIRECTORIES": str(directory.parent)})
        where = directory if no_file else directory / "loose.md"  # no file named: its cwd is the place
        skip = messages.g1_green_skip(messages.g1_skip_no_repo(str(where)))
        ok, said = expect(result, 0, skip, "stdout")
        if no_file:
            return ok, said
        # the written file's path with a line break in it and over 80 characters: whole, escaped
        name = "a\n" + "b" * 90 + ".md"
        long_event = payload(directory, Write(name, NO_ENVELOPE))
        long_result = h.run_gate(long_event, env={"GIT_CEILING_DIRECTORIES": str(directory.parent)})
        line = (
            f"GREEN: {ns}: 0 documents examined — {directory}/a\\n" + "b" * 90 + ".md is not inside a git"
            " repository; the constitution is silent there"
        )
        long_ok, long_said = expect(long_result, 0, line, "stdout")
        return ok and long_ok, said if ok and long_ok else f"{said}; {long_said}"

    def no_dials_file() -> tuple[bool, str]:
        consumer = h.fresh_consumer()
        (consumer.root / "constitution.yaml").unlink()
        if s.scan_only:
            consumer.write(s.red.target, s.red.text)
            result = h.run_gate("", args=scan_args(consumer.root))
        else:
            result = h.run_gate(payload(consumer.root, s.red))
        skip = messages.g1_green_skip(messages.g1_skip_no_dials(str(consumer.root)))
        return expect(result, 0, skip, "stdout")

    def no_root_policy() -> tuple[bool, str]:
        result, _ = s.gate_on(s.red, raw_dials="notes-policy:\n  territory: ['docs/notes/**']\n")
        reason = "constitution.yaml has no root_policy: nothing is claimed"  # typed by hand
        return expect(result, 0, messages.g1_green_skip(reason), "stdout")

    def byte_order_mark() -> tuple[bool, str]:
        result, _ = s.gate_on(Write(s.valid.target, "\ufeff" + s.valid.text))
        return expect(result, 0, s.green, "stdout")

    def negated_pattern() -> tuple[bool, str]:
        """A file-level negated pattern takes the file out of the territory, and the skip says why."""
        if s.outside is None:  # an empty default would make the item pass on any skip at all
            return False, "Subject.outside not given"
        territory = [*s.territory, "!" + s.red.target]
        result, _ = s.gate_on(s.red, dials_patch=s.claim(territory))
        line = f"GREEN: {ns}: 0 documents examined — {s.outside}"
        ok = result.code == 0 and line in result.stdout.splitlines()
        return (
            ok,
            f"exit 0: {line}"
            if ok
            else f"wanted exit 0 printing {line!r}; got exit {result.code}: {result.stdout}",
        )

    def policy_without_id_note() -> tuple[bool, str]:
        """A document where policies live with no readable id earns note N1.1. An id written as a YAML
        block scalar ends in a line break, which the kernel schema's pattern does not accept: it is no
        readable id either, and earns the note too — the note typed by hand."""
        block = "---\nid: |\n  zz-block\ntype: current-state\ntitle: T\nstatus: active\n---\n"
        files = {"docs/policies/zz-no-id.md": NO_ENVELOPE, "docs/policies/zz-block.md": block}
        result, _ = s.gate_on(s.valid, files=files)
        said = Result(result.code, green_said(result), result.stderr)
        lead = (
            " lies in the root policy's territory but carries no readable id; it claims nothing until it does"
        )
        ok, evidence = expect(
            said, 0, messages.n1_note_policy_without_id("docs/policies/zz-no-id.md"), "stdout"
        )
        block_ok = "note: docs/policies/zz-block.md" + lead in said.stdout
        return (
            ok and block_ok,
            evidence
            if ok and block_ok
            else f"{evidence}; no note for the block-scalar id: {said.stdout[:300]}",
        )

    def edit_empty_old_string() -> tuple[bool, str]:
        """An empty old_string on a file that exists matches everywhere: the tool refuses it."""
        action = Edit(s.valid.target, "", "junk ")
        result, _ = s.gate_on(action, files={s.valid.target: s.valid.text})
        skip = messages.g1_green_skip(messages.g1_skip_edit_unappliable(s.valid.target))
        return expect(result, 0, skip, "stdout")

    def edit_unappliable() -> tuple[bool, str]:
        action = Edit(s.valid.target, "no such text anywhere", "x")
        result, _ = s.gate_on(action, files={s.valid.target: s.valid.text})
        skip = messages.g1_green_skip(messages.g1_skip_edit_unappliable(s.valid.target))
        return expect(result, 0, skip, "stdout")

    def green_said(result: Result) -> str:
        """What a green run said: the additionalContext of the one JSON object a hook run with notes
        prints, or stdout as it is — a run without notes, a scan, a generator."""
        try:
            answer = json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout
        context = (
            answer.get("hookSpecificOutput", {}).get("additionalContext")
            if isinstance(answer, dict)
            else None
        )
        return context if isinstance(context, str) else result.stdout

    def notes_reach_the_model() -> tuple[bool, str]:
        """A green hook run with notes answers with one JSON object, the notes and the green line in
        additionalContext: the platform writes a write event's plain stdout to its debug log, where the
        model never reads it. A green run without notes prints its green line alone, as before."""
        if s.noted is None:  # the item is left out then; a direct call must not pass vacuously
            return False, "Subject.noted not given"
        result, _ = s.gate_on(s.noted)
        try:
            answer = json.loads(result.stdout)
        except json.JSONDecodeError:
            return False, f"exit {result.code}; stdout is not one JSON object: {result.stdout.strip()[:400]}"
        output = answer.get("hookSpecificOutput") if isinstance(answer, dict) else None
        lines = str(output.get("additionalContext", "")).split("\n") if isinstance(output, dict) else []
        plain, _ = s.gate_on(s.valid)
        ok = (
            result.code == 0
            and isinstance(output, dict)
            and set(answer) == {"hookSpecificOutput"}
            and set(output) == {"hookEventName", "additionalContext"}
            and output["hookEventName"] == s.event
            and s.note in lines
            and lines[-1].startswith(f"GREEN: {ns}: ")
            and not any(line.startswith("RED") for line in lines)
            and not result.stderr
            and plain.code == 0
            and plain.stdout.startswith(f"GREEN: {ns}: ")
        )
        return ok, (
            "exit 0; the note and the green line in additionalContext, one JSON object; no note, a plain line"
            if ok
            else f"exit {result.code}: {result.stdout.strip()[:400]} / no notes: {plain.stdout.strip()[:200]}"
        )

    # ---------------------------------------------------------------- the warn channel

    def severity_warn() -> tuple[bool, str]:
        result, _ = s.gate_on(s.red, dials_patch=s.own(severity="warn"))
        if result.code != 0:
            return False, f"warn must let the write through; exit {result.code}: {result.stderr}"
        answer = json.loads(result.stdout)
        if stop:  # the user's notice alone: context handed to the model at a turn's end continues it
            ok = (
                set(answer) == {"systemMessage"}
                and s.red_finding.render() in answer["systemMessage"]
                and answer["systemMessage"].startswith(f"{ns} (warn):\n")  # typed by hand
            )
            return (
                ok,
                "exit 0, the whole finding in systemMessage and nothing else" if ok else f"bad: {answer}",
            )
        context = answer["hookSpecificOutput"]["additionalContext"]
        ok = (
            s.red_finding.render() in context
            and f"{ns}: severity is warn: the write proceeds, but the finding stands and recurs on every"
            " write until fixed"
            in context  # typed by hand, as the system line below
            and answer["systemMessage"] == f"{ns} (warn): {s.red_finding.headline}"
        )
        return ok, "exit 0, finding in additionalContext and systemMessage" if ok else f"bad: {answer}"

    # ---------------------------------------------------------------- the output log

    def log_lines(path: Path) -> list[dict[str, str]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def log_in_plugin_data() -> tuple[bool, str]:
        data = h.scratch_dir()
        result, _ = s.gate_on(s.red, env={"CLAUDE_PLUGIN_DATA": str(data)})
        lines = log_lines(data / log_name())
        line = lines[0]
        first = ("RED: " if s.event_driven else "BROKEN: ") + s.red_finding.headline
        said = {
            stream: [each["text"] for each in lines if each["stream"] == stream]
            for stream in ("stdout", "stderr")
        }
        # an asking gate prints its verdict as one JSON object on stdout, the finding inside it; a scan
        # prints its finding and its count line on stdout, one record each
        verdict_stream = "stdout" if (s.ask or s.scan_only) else "stderr"
        records = 2 if s.scan_only else 1
        ok = (
            set(line) == {"ts", "module", "gate", "mode", "session", "stream", "text"}
            and (first in line["text"] if s.ask else line["text"].startswith(first))
            and line["module"] == ns
            and line["stream"] == verdict_stream
            and line["session"] == ("fixture-session" if s.event_driven and not s.scan_only else "")
            # one record per print: the records rebuild both streams exactly, and a block verdict,
            # printed at once, is one record of several lines
            and "".join(text + "\n" for text in said["stdout"]) == result.stdout
            and "".join(text + "\n" for text in said["stderr"]) == result.stderr
            and (
                not s.event_driven
                or (len(said[verdict_stream]) == records and (s.ask or "\n" in line["text"]))
            )
        )
        return ok, f"{len(lines)} log lines; first: {line}"

    def log_in_ignored_dir() -> tuple[bool, str]:
        data = h.scratch_dir()
        result, root = s.gate_on(
            s.valid,
            files={".gitignore": ".gate-logs/\n"},
            env={"CLAUDE_PLUGIN_DATA": str(data)},
            dials_patch=s.own(log_dir="./docs//../.gate-logs//"),  # read as `.gate-logs`
        )
        log = root / ".gate-logs" / log_name()
        ok = (
            result.code == 0
            and log.is_file()
            and s.green in log_lines(log)[-1]["text"]
            and not (data / log_name()).exists()
        )
        return ok, f"exit {result.code}; the whole run logged inside the repository, nothing split off"

    def log_dir_not_ignored() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch=s.own(log_dir="gate-logs"))
        return broken(result, messages.c13_log_dir_not_ignored("gate-logs"))

    def log_rotates() -> tuple[bool, str]:
        data = h.scratch_dir()
        (data / log_name()).write_text("x" * (ROTATE_AT + 1), encoding="utf-8")
        s.gate_on(s.valid, env={"CLAUDE_PLUGIN_DATA": str(data)})
        kept = (data / (log_name() + ".1")).stat().st_size > ROTATE_AT
        started = log_lines(data / log_name())  # only this run's lines: a gate's one, a generator's few
        return kept and bool(started) and all(line["module"] == ns for line in started), (
            "the old log kept as .1, a new one started"
        )

    def log_failure_keeps_verdict() -> tuple[bool, str]:
        blocker = h.scratch_dir() / "a-file-not-a-directory"
        blocker.write_text("", encoding="utf-8")
        red, _ = s.gate_on(s.red, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
        green, _ = s.gate_on(s.valid, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
        refused = red_code if s.event_driven else 1  # a gate's finding; a generator's refusal
        ok = red.code == refused and green.code == 0 and (not s.ask or ask_reason(red) is not None)
        return ok, f"log location unwritable: red still exits {red.code}, green still exits {green.code}"

    def declared_libraries() -> tuple[bool, str]:
        declared = {
            line.split(">=")[0].split("==")[0].strip()
            for line in preflight.requirements_file().read_text().splitlines()
            if line.strip()
        }
        ok = declared == set(preflight.declared())
        return ok, f"requirements.txt {sorted(declared)} == preflight table {sorted(preflight.declared())}"

    def long_value_is_cut() -> tuple[bool, str]:
        """A value a page long is echoed cut, so the whole verdict stays under the platform's cap —
        and the cut is said, not silent."""
        if s.long_value is None:  # the item is left out then; a direct call must not pass vacuously
            return False, "Subject.long_value not given"
        result, _ = s.gate_on(s.long_value)
        said = red_said(result)
        ok = (
            result.code == red_code
            and len(red_lines(said)) == 2  # the one finding and the count line
            and "… [12000 characters]" in said  # the marker, typed by hand
            and "x" * 81 not in said
            and len(said) < 2_000
        )
        return ok, (
            f"exit {red_code}; {len(said)} characters of verdict for a 12,000-character value, cut and said"
            if ok
            else f"exit {result.code}; {len(said)} characters of verdict: {said[:400]}"
        )

    # ---------------------------------------------------------------- git failing in one way; a file unread

    def git_failing_at(
        trigger: str,
        code: int,
        line: Callable[[Path], str],
        through_scan: bool = False,
        then: str = "",
        hangs: bool = False,
    ) -> tuple[bool, str]:
        """A git first on PATH that exits `code` when one of its arguments is `trigger`, and hands every
        other call to the real git — so the gate gets as far as that one call. `through_scan`: the
        failing git is met by the scan on the prepared consumer, for a gate whose hook never makes
        the call. `then`: a second stderr line the failing git adds, which no message may carry.
        `hangs`: the git does not fail but never answers — it becomes a process that waits for ever,
        which the budget kills — and the hook run, whose budget is lowered to `HANG_SECONDS`, is bounded
        by the case itself, so that a gate with no budget reads as a red item, not an endless wait."""
        real, silent = shutil.which("git"), shutil.which("tail")
        if real is None or silent is None:
            return False, "no git or no tail on PATH: the fake git hands every other call to the real one"
        directory = h.scratch_dir()
        fake = directory / "git"
        said = [f"fatal: simulated {trigger} failure", *([then] if then else [])]
        refusal = "".join(f"    echo {shlex.quote(line)} >&2\n" for line in said) + f"    exit {code}\n"
        stall = f"    exec {shlex.quote(silent)} -f /dev/null\n"  # the very process the timeout kills
        fake.write_text(
            "#!/bin/sh\n"
            'for a in "$@"; do\n'
            f'  if [ "$a" = {shlex.quote(trigger)} ]; then\n'
            + (stall if hangs else refusal)
            + f'  fi\ndone\nexec {shlex.quote(real)} "$@"\n',
            encoding="utf-8",
        )
        fake.chmod(0o755)
        env = {"PATH": str(directory) + os.pathsep + os.environ.get("PATH", os.defpath)}
        if hangs:
            env.update(git_patch(h, HANG_SECONDS, trigger)[0])
        with h.bounded(HANG_BOUND) if hangs else nullcontext():
            if through_scan:
                _, root = s.gate_on(s.valid)
                result = h.run_gate("", args=scan_args(root), env=env)
            else:
                result, root = s.gate_on(s.valid, env=env)
        return broken_as_typed(result, line(root))

    def ls_files_fails() -> tuple[bool, str]:
        return git_failing_at(
            "ls-files",
            1,
            lambda root: (
                f"BROKEN: git could not list the files of {root}: fatal: simulated ls-files failure"
                " — fix: repair what git names in the message, then check by hand: git -C <that directory>"
                " ls-files"
            ),
            through_scan=not s.hook_lists_files,
        )

    def init_fails() -> tuple[bool, str]:
        return git_failing_at(
            "init",
            128,
            lambda _: (
                "BROKEN: git init of the scratch repository failed: fatal: simulated init failure — fix:"
                " repair what git names in the message; the scratch repository lives in the system's"
                " temporary directory"
            ),
        )

    def check_ignore_fails() -> tuple[bool, str]:
        """Exit 128: check-ignore's exit 1 means no path matched, which is no failure. Git's second
        line of stderr stays out of the message, whose first line is the one that reaches the user."""
        return git_failing_at(
            "--no-index",
            128,
            lambda _: (
                "BROKEN: git check-ignore failed: fatal: simulated --no-index failure — fix: territory"
                " patterns must be gitignore syntax; check constitution.yaml"
            ),
            then="hint: a second line of git's message",
        )

    # ---------------------------------------------------------------- the budget of a git call

    def silent_git(subcommand: str, directory: str, call: str, quoted: str | None = None) -> str:
        """C12.12 as the hang cases type it, for the budget they lower it to: a call in the person's
        repository, the directory and the call as a person types them into the fix. `quoted`: the
        directory as the fix shows it to a shell, typed by the case; none, the directory quoted here."""
        where = shlex.quote(directory) if quoted is None else quoted
        return (
            f"BROKEN: git gave no answer in {HANG_SECONDS:g} s to git {subcommand} in {directory}"
            " — fix: a git that hangs is a stalled file system or, for a call that reads the index, a"
            " core.fsmonitor hook, set in the repository's or in your own configuration: find the setting"
            f" with git -C {where} config --show-origin --get core.fsmonitor (no output means none is set),"
            f" repair or unset it or the file system, and run git -C {where} {call} by hand until it"
            " answers; the scan, which gives git as long as it takes, checks the same tree"
        )

    def silent_scratch(subcommand: str) -> str:
        """C12.13 as the hang cases type it: a call in the scratch repository, which names the system's
        temporary directory and the configuration outside any repository, and asks for nothing by hand
        in the scratch repository."""
        temporary = tempfile.gettempdir()
        return (
            f"BROKEN: git gave no answer in {HANG_SECONDS:g} s to git {subcommand} in a scratch folder under"
            f" {temporary} — fix: the system's temporary directory ({temporary}; TMPDIR names it) may sit"
            " on a stalled file system, or your git configuration outside any repository may hang git:"
            " read it with git config --global --list --show-origin and git config --system --list"
            " --show-origin, repair the setting, or free that file system or set TMPDIR to a folder on a"
            " working one, then run again; the scan, which gives git as long as it takes, checks the same"
            " tree"
        )

    def quoted_by_hand(path: str) -> str:
        """A path as a shell takes it whole, typed out: single quotes, and each single quote inside closed,
        written between double quotes, and opened again."""
        return "'" + path.replace("'", "'\"'\"'") + "'"

    def nearest_folder(root: Path) -> str:
        """Where the hook's `rev-parse` runs: the written file's folder, or the nearest one that exists,
        for a gate on a file; the event's directory for one without a file."""
        probe = root if no_file else (root / s.valid.target).parent
        while not probe.is_dir():
            probe = probe.parent
        return str(probe)

    def git_calls(run: Callable[[dict[str, str]], object]) -> list[str]:
        """The `timeout=` of each git call `run` made, as logged by the patch in its environment."""
        env, log = git_patch(h)
        run(env)
        return git_timeouts(log)

    def budget_by_mode() -> tuple[bool, str]:
        """The rule at its one decision point, in a process of its own for each mode: a hook gives git
        `GIT_SECONDS`; a scan, an act and a process declared with no mode give it no clock."""
        program = (
            "import json, sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from const_gate import identity, repository\n"
            "from const_gate.model import Mode\n"
            "mode = {'hook': Mode.HOOK, 'scan': Mode.SCAN, 'act': Mode.ACT, 'none': None}[sys.argv[2]]\n"
            "identity.declare(identity.Identity('x', 'y', Path('.')), mode)\n"
            "print(json.dumps(repository.budget()))\n"
        )
        seen: dict[str, object] = {}
        for mode in ("hook", "scan", "act", "none"):
            done = subprocess.run(
                [sys.executable, "-c", program, str(h.scripts), mode],
                capture_output=True,
                text=True,
                check=False,
            )
            seen[mode] = json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip()
        wanted: dict[str, object] = {"hook": repository.GIT_SECONDS, "scan": None, "act": None, "none": None}
        return seen == wanted, f"the budget by mode: {seen}"

    def git_words() -> tuple[bool, str]:
        """git's subcommand is the first argument that is no option and no option's value; the call as a
        person runs it keeps the arguments, quoted, without `-z`, and reads `/dev/null` for a stdin."""
        subcommands = {
            ("status", "--porcelain"): "status",
            ("-C", "/a b", "log", "-1"): "log",
            ("-c", "core.x=y", "-c", "core.z=w", "diff"): "diff",
            ("--git-dir=/g", "--work-tree=/w", "check-ignore", "-v"): "check-ignore",
            ("--git-dir", "/g", "--work-tree", "/w", "ls-files"): "ls-files",
            ("--namespace", "n", "--config-env", "a=B", "show-ref"): "show-ref",
            ("--version",): "--version",
        }
        got = {args: repository.subcommand(list(args)) for args in subcommands}
        words = [
            (repository.by_hand(["ls-files", "-z", "--cached"]), "ls-files --cached"),
            (repository.by_hand(["log", "--format=%H %s", "a b"]), "log '--format=%H %s' 'a b'"),
            (repository.by_hand(["check-ignore", "--stdin"], b"x\0"), "check-ignore --stdin < /dev/null"),
        ]
        ok = got == subcommands and all(real == typed for real, typed in words)
        return ok, f"subcommands {got}; the call as typed {[real for real, _ in words]}"

    def declaration_is_one() -> tuple[bool, str]:
        """A process is one gate in one mode: the same identity twice with different modes is a defect,
        the same identity and mode twice is not."""
        program = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from const_gate import identity\n"
            "from const_gate.model import Mode\n"
            "who = identity.Identity('x', 'y', Path('.'))\n"
            "identity.declare(who, Mode.HOOK)\n"
            "identity.declare(who, Mode.HOOK)\n"
            "print('same twice: fine')\n"
            "try:\n"
            "    identity.declare(who, Mode.SCAN)\n"
            "except RuntimeError as failure:\n"
            "    print('other mode: RuntimeError', failure)\n"
        )
        done = subprocess.run(
            [sys.executable, "-c", program, str(h.scripts)], capture_output=True, text=True, check=False
        )
        lines = done.stdout.splitlines()
        ok = (
            done.returncode == 0
            and lines[:1] == ["same twice: fine"]
            and (len(lines) == 2 and lines[1].startswith("other mode: RuntimeError"))
        )
        return ok, f"exit {done.returncode}: {lines or done.stderr.strip()[-200:]}"

    def handlers_outlive_git(plugin: Path) -> tuple[bool, str]:
        """Every handler of the plugin's hooks file whose script names python3 has a timeout longer
        than `GIT_SECONDS` (limit 16): a git that hangs ends with the gate's own line before the platform
        cuts the hook, which says nothing. A handler's scripts are each of its `args` and each word of
        its `command` that is a path, once `${CLAUDE_PLUGIN_ROOT}` is replaced; a handler whose `command`
        names python3 as a word is held too, and a script that cannot be read counts as one that does."""
        hooks = plugin / "hooks" / "hooks.json"
        try:
            spec = json.loads(hooks.read_text(encoding="utf-8"))
            handlers = [
                (event, handler)
                for event, groups in spec["hooks"].items()
                for group in groups
                for handler in group["hooks"]
            ]
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            return False, f"{hooks} cannot be read as a hooks file: {type(exc).__name__}: {exc}"
        checked, short = 0, []
        for event, handler in handlers:
            command = handler.get("command", "")
            command = command if isinstance(command, str) else ""
            try:
                words = shlex.split(command)
            except ValueError:  # an unbalanced quote: the words as a shell would not take them
                words = command.split()
            root = str(plugin)
            scripts = [a.replace("${CLAUDE_PLUGIN_ROOT}", root) for a in handler.get("args", [])] + [
                w.replace("${CLAUDE_PLUGIN_ROOT}", root)
                for w in words
                if os.sep in w.replace("${CLAUDE_PLUGIN_ROOT}", root)
            ]
            try:
                names_python = re.search(r"(?<![\w-])python3(?![\w-])", command) is not None or any(
                    b"python3" in Path(a).read_bytes() for a in scripts
                )
            except OSError:
                names_python = True  # a handler whose script cannot be read is held to the rule too
            if not names_python:
                continue
            checked += 1
            timeout = handler.get("timeout")
            numeric = isinstance(timeout, int | float) and not isinstance(timeout, bool)
            if not numeric or timeout <= repository.GIT_SECONDS:
                short.append(f"{event} handler {command!r} {scripts} has timeout {timeout!r}")
        if checked == 0:
            return False, f"{hooks} holds no handler whose script names python3"
        if short:
            return False, (
                f"{'; '.join(short)} — not above GIT_SECONDS ({repository.GIT_SECONDS:g} s): a git that"
                " hangs would be cut by the platform before the gate said so"
            )
        return (
            True,
            f"{checked} handler(s) whose script names python3 outlive GIT_SECONDS"
            f" ({repository.GIT_SECONDS:g} s)",
        )

    def the_tie_catches_a_short_handler() -> tuple[bool, str]:
        """The tie on hooks files made here: a timeout at GIT_SECONDS fails and one above passes, for a
        handler whose script names python3 given as `command: sh` with `args` and given in shell form
        (`command` alone, naming python3 or a script that does), and a handler whose command and
        scripts name no python3 is not held to it."""
        plugin = h.scratch_dir()
        (plugin / "hooks").mkdir()
        (plugin / "scripts").mkdir()
        (plugin / "scripts" / "gate.sh").write_text('exec python3 "$0.py"\n', encoding="utf-8")
        (plugin / "scripts" / "print.sh").write_text("cat rule.txt\n", encoding="utf-8")
        root = "${CLAUDE_PLUGIN_ROOT}/scripts/"
        budget = repository.GIT_SECONDS

        def exec_form(name: str, timeout: float) -> dict[str, object]:
            return {"type": "command", "command": "sh", "args": [root + name], "timeout": timeout}

        def shell_form(command: str, timeout: float) -> dict[str, object]:
            return {"type": "command", "command": command, "timeout": timeout}

        def holds(*handlers: dict[str, object]) -> tuple[bool, str]:
            spec = {"hooks": {"PreToolUse": [{"matcher": "Write", "hooks": list(handlers)}]}}
            (plugin / "hooks" / "hooks.json").write_text(json.dumps(spec), encoding="utf-8")
            return handlers_outlive_git(plugin)

        cases: list[tuple[str, bool, tuple[dict[str, object], ...]]] = [
            ("exec form, at the budget", False, (exec_form("gate.sh", budget),)),
            (
                "exec form above it, a print handler at 1 s",
                True,
                (exec_form("gate.sh", budget + 1), exec_form("print.sh", 1)),
            ),
            # Shell form (N55): no `args`, the handler's `command` alone. A held handler at the
            # budget stands beside one above it, so that a handler the tie skips is a green, never
            # the red of a file with no handler to hold.
            (
                "shell form naming python3, at the budget",
                False,
                (shell_form(f"python3 {root}x.py", budget), exec_form("gate.sh", budget + 1)),
            ),
            ("shell form naming python3, above it", True, (shell_form(f'python3 "{root}x.py"', budget + 1),)),
            (
                "shell form naming a script that names python3, at the budget",
                False,
                (shell_form(f"sh {root}gate.sh", budget), exec_form("gate.sh", budget + 1)),
            ),
            (
                "shell form naming a script that names python3, above it",
                True,
                (shell_form(f"sh {root}gate.sh", budget + 1),),
            ),
            (
                "shell form naming no python3 beside a held handler above the budget",
                True,
                (shell_form(f"sh {root}print.sh", 1), exec_form("gate.sh", budget + 1)),
            ),
        ]
        results = [(label, expected, holds(*handlers)) for label, expected, handlers in cases]
        ok = all(got[0] == expected for _, expected, got in results)
        said = "; ".join(
            f"{label}: {'green' if got[0] else 'red'} (wanted {'green' if expected else 'red'})"
            for label, expected, got in results
        )
        return ok, said

    def hangs_in_a_folder_to_quote() -> tuple[bool, str]:
        """The folder C12.12 names stands in the fix's two commands quoted for a shell: a repository
        whose folder holds a space and a single quote, a git that hangs at the root's `rev-parse` (the call
        every hook makes first), the line typed with the folder as a shell takes it whole."""
        kept = h.scratch
        odd = kept / "a folder it's"
        odd.mkdir()
        h.scratch = odd  # every consumer the gate runs on is made under it, for as long as the case runs
        try:
            return git_failing_at(
                "rev-parse",
                0,
                lambda root: silent_git(
                    "rev-parse",
                    nearest_folder(root),
                    "rev-parse --show-toplevel",
                    quoted_by_hand(nearest_folder(root)),
                ),
                hangs=True,
            )
        finally:
            h.scratch = kept

    def attempted(check: Callable[[], tuple[bool, str]]) -> tuple[bool, str]:
        """One check of the item that cannot run is a red check with its error, and hides no other."""
        try:
            return check()
        except Exception as error:  # noqa: BLE001 — any failure of the check is its red
            return False, f"{check.__name__} raised {type(error).__name__}: {error}"

    def git_has_a_budget_in_a_hook() -> tuple[bool, str]:
        """N22: the shared `git` gives a call `GIT_SECONDS` in a hook and no clock in a scan or an act. In a
        hook a git that never answers — at the file list, at the scratch repository, at the repository's
        root — ends in the shared line `C12.12` with the count line after it; a git that answers is
        unchanged; and the plugin's handlers outlive the budget, so the line is the hook's last word."""
        results: list[tuple[bool, str]] = [
            attempted(check)
            for check in (budget_by_mode, declaration_is_one, git_words, the_tie_catches_a_short_handler)
        ]
        if s.event_driven and not s.scan_only:  # a gate with a hook run
            lines: dict[str, Callable[[Path], str]] = {
                "rev-parse": lambda root: silent_git(
                    "rev-parse", nearest_folder(root), "rev-parse --show-toplevel"
                ),
                "ls-files": lambda root: silent_git(
                    "ls-files", str(root), "ls-files --cached --others --exclude-standard"
                ),
                "init": lambda _: silent_scratch("init"),
                "check-ignore": lambda _: silent_scratch("check-ignore"),
            }
            reached = ["rev-parse"]
            if not no_file:
                reached += ["init", "check-ignore"]
                if s.hook_lists_files:  # the hook asks git for the file list
                    reached.append("ls-files")

            def hangs_at(trigger: str) -> tuple[bool, str]:
                return git_failing_at(trigger, 0, lines[trigger], hangs=True)

            results += [hangs_at(trigger) for trigger in reached]
            results.append(attempted(hangs_in_a_folder_to_quote))
            budgeted = git_calls(lambda env: s.gate_on(s.valid, env=env))
            every_call = set(budgeted) == {repr(repository.GIT_SECONDS)}
            results.append(
                (every_call, f"a hook run's {len(budgeted)} git calls' timeouts: {sorted(set(budgeted))}")
            )
            results.append(handlers_outlive_git(preflight.requirements_file().parent))
        if s.event_driven or s.scan_only:  # a scan, on the prepared consumer
            _, scanned = s.gate_on(s.valid)
            unclocked = git_calls(lambda env: h.run_gate("", args=scan_args(scanned), env=env))
            results.append(
                (bool(unclocked) and set(unclocked) == {"None"}, f"a scan's git calls: {unclocked}")
            )
        else:  # a generator's act
            acted = git_calls(lambda env: s.gate_on(s.valid, env=env))
            results.append((bool(acted) and set(acted) == {"None"}, f"an act's git calls: {acted}"))
        failed = [evidence for ok, evidence in results if not ok]
        if failed:
            return False, f"{len(failed)} of {len(results)} checks red: " + " | ".join(failed)
        return (
            True,
            f"{len(results)} checks: a hang ends in the line within {HANG_SECONDS:g} s; scan, act: no clock",
        )

    def unreadable(path: Path, run: Callable[[], Result], line: str) -> tuple[bool, str]:
        """`run` with `path` made unreadable, its mode restored whatever happens: the runner's cleanup
        must be able to remove it."""
        mode = path.stat().st_mode
        path.chmod(0o000)
        try:
            result = run()
        finally:
            path.chmod(mode)
        return broken_as_typed(result, line)

    as_root = (
        "NOT EXERCISED: running as root, where a mode bit does not deny a read — 0 unreadable files examined"
    )

    def dials_unreadable() -> tuple[bool, str]:
        if os.geteuid() == 0:
            return True, as_root
        _, root = s.gate_on(s.valid)
        dials = root / "constitution.yaml"

        def again() -> Result:
            if s.scan_only:
                return h.run_gate("", args=scan_args(root))
            if s.event_driven:
                return h.run_gate(payload(root, s.valid))
            return h.run_gate("", args=list(s.act_args), cwd=root)  # refused before the home is looked at

        line = (
            f"BROKEN: constitution.yaml cannot be read ([Errno 13] Permission denied: '{dials}') — fix: check"
            " the file's permissions"
        )
        return unreadable(dials, again, line)

    def document_unreadable() -> tuple[bool, str]:
        if os.geteuid() == 0:
            return True, as_root
        sibling = str(Path(s.valid.target).with_name("unreadable.md"))
        _, root = s.gate_on(s.valid, files={sibling: s.valid.text})
        line = (
            f"BROKEN: {sibling} is listed by git but cannot be read — fix: check that the file can be read:"
            " its permissions, or a link that leads nowhere"
        )
        return unreadable(root / sibling, lambda: h.run_gate("", args=["--scan", str(root)]), line)

    def policy_unreadable() -> tuple[bool, str]:
        """A file where policies live is a policy by the kernel's rule: one nobody can read is C12.10
        in a hook run too, never a policy with no id and the green skip that would follow."""
        if os.geteuid() == 0:
            return True, as_root
        policy = "docs/policies/zz-unreadable.md"
        _, root = s.gate_on(s.valid, files={policy: NO_ENVELOPE})
        runs: list[Result] = []

        def again() -> Result:
            if s.event_driven:
                runs.append(h.run_gate(payload(root, s.valid)))
            else:
                (root / s.valid.target).unlink(missing_ok=True)  # the first run wrote it
                runs.append(h.run_gate("", args=list(s.act_args), cwd=root))
            return runs[-1]

        line = (
            f"BROKEN: {policy} is listed by git but cannot be read — fix: check that the file can be read:"
            " its permissions, or a link that leads nowhere"
        )
        ok, evidence = unreadable(root / policy, again, line)
        said = (runs[-1].stdout + runs[-1].stderr).splitlines()
        noted = [each for each in said if "carries no readable id" in each]
        if noted:  # note N1.1, its fragment typed by hand: the file taken for a policy with no id
            return False, f"note N1.1 printed for a file nobody can read: {noted[0]}"
        return ok, evidence

    def dials_not_utf8() -> tuple[bool, str]:
        """A byte that is not UTF-8 is the file's content: C4 naming its line and column, never C12.11."""
        _, root = s.gate_on(s.valid)
        dials = root / "constitution.yaml"
        # "# é", then the byte: two bytes, one character, so the column counts characters, not bytes
        dials.write_bytes(b"# \xc3\xa9\xff\n" + dials.read_bytes())
        if s.scan_only:
            result = h.run_gate("", args=scan_args(root))
        elif s.event_driven:
            result = h.run_gate(payload(root, s.valid))
        else:
            result = h.run_gate("", args=list(s.act_args), cwd=root)  # refused before the home is looked at
        line = (
            "BROKEN: constitution.yaml is not valid YAML (byte 0xff at line 1, column 4 is not UTF-8; save"
            " the file as UTF-8) — fix: repair the YAML at the place the message names; nothing is checked"
            " until the file parses"
        )
        return broken_as_typed(result, line)

    def shared_texts_escape_or_cut() -> tuple[bool, str]:
        """The two helpers and the shared texts that use them, every expectation typed by hand. A
        value the reader opens or types into a fix — a path, an id in a fix, git's diagnosis — stands
        whole, however long, with its backslash and line breaks escaped; a value that only points —
        a key, a pattern, a command word — is cut at 80 characters and then escaped. An id never
        ends in a line break."""
        path = "docs/" + "d" * 90 + "\nx.md"  # over 80 characters, with a line break
        esc = "docs/" + "d" * 90 + "\\nx.md"  # the same, escaped, typed by hand
        cut = "a" * 80 + "… [100 characters]"  # a value of 100 characters, cut
        broken = {
            "C4 detail whole": messages.c4_dials_invalid_yaml("at " + "w" * 100 + "\\x"),
            "C5.3 dialect": messages.c5_dialect_unsupported("d\n" + "e" * 100),
            "C5.4 key": messages.c5_namespace_not_mapping("a\nb"),
            "C5.6 key": messages.c5_territory_shape("a" * 100),
            "C5.7 where": messages.c5_territory_pattern("k" * 100, "#x"),
            "C6": messages.c6_root_missing(path),
            "C7": messages.c7_root_without_id(path),
            "C8": messages.c8_root_claims_nothing(path),
            "C9": messages.c9_root_outside_own_territory(path, ["p" * 100, "q\\"], path),
            "C12.1": messages.c12_ls_files(path, "fatal: x\\y" + "z" * 100),
            "C12.2": messages.c12_init("w\\" + "w" * 118),
            "C12.3": messages.c12_check_ignore("w\\" + "w" * 118),
            "C12.5": messages.c12_git_failed("g\\" + "g" * 118),
            "C12.6": messages.c12_scan_path(path),
            "C12.8": messages.c12_no_repo(path),
            "C12.9": messages.c12_invocation("bad " + "a\nb" + "c" * 100),
            "C12.10": messages.c12_unreadable(path),
            "C12.11": messages.c12_unexpected("ValueError: " + "v" * 100),
            "C13": messages.c13_log_dir_not_ignored(path),
        }
        wanted = {
            "C4 detail whole": f"BROKEN: constitution.yaml is not valid YAML (at {'w' * 100}\\\\x) — fix: "
            "repair the YAML at the place the message names; nothing is checked until the file parses",
            "C5.3 dialect": "BROKEN: constitution.yaml: territory_dialect 'd\\n"
            + "e" * 78
            + "… [102 characters]'"
            f" is not supported by {ns} (supports: gitignore) — fix: set territory_dialect: gitignore, or"
            " remove the key",
            "C5.4 key": "BROKEN: constitution.yaml: namespace 'a\\nb' must be a mapping — fix: write it as"
            " a\\nb: {territory: [...]}",
            "C5.6 key": f"BROKEN: constitution.yaml: {cut}.territory must be a list of non-empty strings"
            f' — fix: write it as {cut}: {{territory: ["<pattern>", ...]}}',
            "C5.7 where": f"BROKEN: constitution.yaml: {'k' * 80}… [100 characters] holds a pattern git would"
            " not read as one: '#x' — fix: a pattern may not start with '#' (a comment to git) nor contain a"
            " line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes,"
            " and remove a line break",
            "C6": f"BROKEN: constitution.yaml names root_policy '{esc}' but no such file exists — fix: create"
            " it, or point root_policy at the policy for policies",
            "C7": f"BROKEN: root policy '{esc}' carries no readable id in its envelope — fix: give it the"
            " envelope (id, type, title, status); its id names its namespace",
            "C8": f"BROKEN: root policy '{esc}' claims no territory in constitution.yaml — fix: write {esc}:"
            " {territory: [<where policies live, including the root itself>]} — nothing is governed until"
            " then",
            "C9": f"BROKEN: root policy '{esc}' lies outside its own territory ['"
            + "p" * 80
            + "… [100 characters]', 'q\\\\'] — fix: every chain of governance ends at the root; widen"
            f" {esc}.territory to include it",
            "C12.1": f"BROKEN: git could not list the files of {esc}: fatal: x\\\\y{'z' * 100} — fix: repair"
            " what git names in the message, then check by hand: git -C <that directory> ls-files",
            "C12.2": f"BROKEN: git init of the scratch repository failed: w\\\\{'w' * 118} — fix: repair what"
            " git names in the message; the scratch repository lives in the system's temporary directory",
            "C12.3": f"BROKEN: git check-ignore failed: w\\\\{'w' * 118} — fix: territory patterns must be"
            " gitignore syntax; check constitution.yaml",
            "C12.5": f"BROKEN: git could not answer where the repository is: g\\\\{'g' * 118} — fix: repair"
            " the git setup named in the message (configuration, ownership, installation)",
            "C12.6": f"BROKEN: {esc} does not exist — fix: pass --scan an existing directory, or none for"
            " the current one",
            "C12.8": f"BROKEN: {esc} is not inside a git repository — fix: run --scan from a repository, or"
            " pass its path",
            "C12.9": "BROKEN: misinvocation: bad a\\nb"
            + "c" * 73
            + "… [107 characters] — fix: "
            + messages.USAGE,
            "C12.10": f"BROKEN: {esc} is listed by git but cannot be read — fix: check that the file can be"
            " read: its permissions, or a link that leads nowhere",
            "C12.11": "unexpected failure inside the checker: ValueError: " + "v" * 68 + "… [112 characters]",
            "C13": f"BROKEN: constitution.yaml: {ns}.log_dir '{esc}' is not ignored by git — fix: a log"
            " inside the working tree must be git-ignored, or every verdict dirties the tree; add the"
            " directory to .gitignore, or remove the key",
        }
        rendered = [
            ("escaped keeps a path whole", messages.escaped("p" * 200), "p" * 200),
            ("escaped shows backslash and breaks", messages.escaped("a\\b\nc\rd"), "a\\\\b\\nc\\rd"),
            (
                "echoed cuts, then escapes",
                messages.echoed("ba\\d\nkey" + "x" * 100),
                "ba\\\\d\\nkey" + "x" * 72 + "… [108 characters]",
            ),
            (
                "G1.1",
                messages.g1_skip_no_file("T\n" + "t" * 100),
                "tool 'T\\n" + "t" * 78 + "… [102 characters]' carries no file to examine",
            ),
            ("G1.2", messages.g1_skip_not_markdown(path), f"{esc} is not a .md file"),
            (
                "G1.3",
                messages.g1_skip_no_repo(path),
                f"{esc} is not inside a git repository; the constitution is silent there",
            ),
            ("G1.4", messages.g1_skip_no_dials(path), f"no constitution.yaml in {esc}: nothing is claimed"),
            (
                "G1.6",
                messages.g1_skip_edit_unappliable(path),
                f"the Edit cannot be applied to {esc}; the tool will report it",
            ),
            ("G1.7", messages.g1_skip_gone(path), f"{esc} is not there after the write"),
            (
                "F9 count line",
                messages.f9_count_hook(2, path),
                f"RED: 2 finding(s) — 1 document examined ({esc})",
            ),
            ("G1 governed by", messages.governed_by("a" * 100), f"governed by {cut}"),
            (
                "N1.1",
                messages.n1_note_policy_without_id(path),
                f"note: {esc} lies in the root policy's territory but carries no readable id; it claims"
                " nothing until it does",
            ),
            (
                "N1.2",
                messages.n1_note_policy_id_shared(path, path, "a" * 100),
                f"note: {esc} and {esc} both carry id '{cut}'; the first claims, the second is ignored",
            ),
        ]
        for label, failure in broken.items():
            # C12.11's closing clause is the entry point's own identity: its headline is what is typed
            got = failure.headline if label == "C12.11" else failure.render()
            rendered.append((label, got, wanted[label]))
        block = "---\nid: |\n  abc-d\ntype: policy\n---\n"  # a key after it keeps the break
        declared = f"---\n{DECLARATION}: |\n  abc-d\ntype: policy\n---\n"
        rendered += [
            ("an id ending in a line break is refused by the pattern", repr(ID_RE.match("abc-d\n")), "None"),
            ("a block-scalar id is no id", repr(document_id(parse_envelope(block))), "None"),
            (
                "a block-scalar declaration is no declaration",
                repr(declared_policy(parse_envelope(declared))),
                "None",
            ),
            ("a plain id is an id", repr(document_id(parse_envelope("---\nid: abc-d\n---\n"))), "'abc-d'"),
        ]
        wrong = [f"{label}: got {got!r}, wanted {want!r}" for label, got, want in rendered if got != want]
        return not wrong, (
            f"{len(rendered)} typed expectations of the shared texts hold" if not wrong else wrong[0][:600]
        )

    def unknown_dial_is_one_line() -> tuple[bool, str]:
        """A key of the module's namespace that holds a line break and is a page long: C5 on one line,
        the backslash and the line break shown escaped, the key cut — in hook mode only the first stderr
        line reaches the user — and, of two keys, the first in sorted order named."""
        key = "ba\\d\nkey" + "x" * 12_000  # a backslash and a line break, each shown escaped
        # a second key that sorts later, written first: the one named is the first in sorted order
        result, _ = s.gate_on(s.valid, dials_patch=s.own(**{"zz_second": 1, key: 1}))
        first = (  # typed by hand: the key cut at 80 characters, its break escaped; the list that
            # follows is the module's own
            f"BROKEN: constitution.yaml: {ns}.ba\\\\d\\nkey" + "x" * 72 + "… [12008 characters] is no dial of"
            " this module — fix: a misspelt dial would be ignored in silence, so none is: write one of "
        )
        lines = result.stderr.splitlines()
        one_line = len(lines) == 1 + len(s.closing.splitlines())  # the failure, then the closing line
        ok = result.code == 1 and one_line and lines[0].startswith(first) and len(result.stderr) < 2_000
        texts_ok, texts = shared_texts_escape_or_cut()  # the same two helpers at the other shared texts
        return ok and texts_ok, (
            f"exit 1; the failure on one line, {len(result.stderr)} characters in all; {texts}"
            if ok and texts_ok
            else f"exit {result.code}; {len(lines)} lines; {result.stderr[:300]}; {texts}"
        )

    def file_named_md() -> tuple[bool, str]:
        """A file named just `.md` is Markdown to the hook as to the scan, which lists it: the hook
        does not skip it for its ending."""
        result, root = s.gate_on(Write(".md", NO_ENVELOPE))
        said = result.stdout + result.stderr
        (root / ".md").write_text(NO_ENVELOPE, encoding="utf-8")  # the hook never applied the write
        listed = ".md" in list_markdown(root)  # what the scan examines
        ok = "is not a .md file" not in said and "BROKEN:" not in said and listed
        return ok, (
            "the hook examines a file named .md, as the scan does"
            if ok
            else f"listed by the scan: {listed}; the hook said: {said[:400]}"
        )

    def cap_keeps_the_first() -> tuple[bool, str]:
        """The findings a hook shows after one write: the first always, however long; then while the
        text fits 8,000 characters; never more than `most` — each number typed by hand."""

        def finding(size: int) -> Finding:  # renders as 3 lines: its headline carries the size
            return Finding(SharedKey.C5, "h" * size, "w", "f")

        big, small = finding(9_000), finding(3_000)  # renders 9,000+ and 3,000+ characters
        a, b, c = finding(4_000), finding(3_900), finding(4_100)  # render 4,023, 3,923 and 4,123
        checks = [
            (pipeline.within_the_cap([big]) == [big], "a first finding over the cap is still shown"),
            (pipeline.within_the_cap([big, small]) == [big], "nothing follows it"),
            (pipeline.within_the_cap([small, small]) == [small, small], "6,000 characters fit"),
            (pipeline.within_the_cap([small, small, small]) == [small, small], "the third is past 8,000"),
            # each counts its render and a line break: 4,024 + 3,924 = 7,948 fit; 4,024 + 4,124 = 8,148 do not
            (pipeline.within_the_cap([a, b]) == [a, b], "7,948 characters fit"),
            (pipeline.within_the_cap([a, c]) == [a], "8,148 characters do not"),
            (pipeline.within_the_cap([small] * 3, most=1) == [small], "`most` stops it at one"),
            (pipeline.within_the_cap([]) == [], "no finding, none shown"),
        ]
        failed = [what for ok, what in checks if not ok]
        return not failed, "; ".join(failed) or "the first always, then what fits, never more than `most`"

    def pattern_in_own_dial_is_one_line() -> tuple[bool, str]:
        """A pattern git would read as a comment, in a dial of the module's own, a page long: C5.7
        naming the dial as it is written — no policy's `.territory` after it — on one line, the pattern
        cut."""
        if s.pattern_dial is None:  # the item is left out then; a direct call must not pass vacuously
            return False, "Subject.pattern_dial not given"
        dial = s.pattern_dial
        result, _ = s.gate_on(s.valid, dials_patch=dial.patch("#" + "x" * 12_000))
        first = (  # typed by hand
            f"BROKEN: constitution.yaml: {ns}.{dial.path} holds a pattern git would not read as one: '#"
            + "x" * 79
            + "… [12001 characters]' — fix: a pattern may not start with '#' (a comment to git) nor contain"
            " a line break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break"
        )
        lines = result.stderr.splitlines()
        one_line = len(lines) == 1 + len(s.closing.splitlines())
        ok = result.code == 1 and one_line and lines[0] == first and len(result.stderr) < 2_000
        if not ok:
            return ok, f"exit {result.code}; {len(lines)} lines; {result.stderr[:300]}"
        # the escape the message teaches passes: `\#drafts/**`, typed by hand, is a pattern git reads as one,
        # so it is no C5.7 and no configuration failure
        escaped, _ = s.gate_on(s.valid, dials_patch=dial.patch("\\#drafts/**"))
        refused = "holds a pattern git would not read as one" in escaped.stderr + escaped.stdout
        if escaped.code == 1 or refused:
            return False, (
                f"the taught escape \\#drafts/** was refused: exit {escaped.code}; {escaped.stderr[:300]}"
            )
        return True, (
            f"exit 1; {ns}.{dial.path} named whole, on one line, {len(result.stderr)} characters in all;"
            f" the escape \\#drafts/** passes, exit {escaped.code}"
        )

    def envelope_delimiters() -> tuple[bool, str]:
        """A `---` line with trailing whitespace opens and closes the envelope, and a line ends at
        `\\n`, `\\r\\n` or a lone `\\r` only: a delimiter after any other break character is none. The
        offsets typed by hand, a byte-order mark counted."""
        closer = "\n---\n"
        at = s.valid.text.find(closer)
        if not s.valid.text.startswith("---\n") or at < 0:
            return False, "the module's valid write holds no plain envelope to vary"
        head, body = s.valid.text[:at], s.valid.text[at + len(closer) :]
        # an envelope that stays whole in every case: the opener, the closer and the line endings vary
        green = {
            "the opener `--- `": "--- \n" + s.valid.text[4:],
            "the closer `--- `": head + "\n--- \n" + body,
            "the closer `---` and a tab": head + "\n---\t\n" + body,
            "CRLF throughout": s.valid.text.replace("\n", "\r\n"),
        }
        failed = []
        for what, text in green.items():
            result, _ = s.gate_on(Write(s.valid.target, text))
            ok, evidence = expect(result, 0, s.green, "stdout")
            if not ok:
                failed.append(f"{what}: {evidence[:300]}")
        # a form feed before the only closer is no delimiter: the envelope never closes, whatever the
        # reader's `splitlines()` would say
        unclosed = head + "\n\x0c---\n" + body
        result, _ = s.gate_on(Write(s.valid.target, unclosed))
        if result.code != red_code or s.green in result.stdout:
            failed.append(f"a form feed before the closer was not blocked: exit {result.code}")
        # the reader and the helper themselves, on text typed by hand
        for breaker in "\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029":
            if parse_envelope(f"---\nid: a\n{breaker}---\nBODY\n").state is not EnvelopeState.UNTERMINATED:
                failed.append(f"{breaker!r} before the closer makes a delimiter")
        for what, text in {"closer `--- `": "---\nid: a\n--- \n", "CRLF": "---\r\nid: a\r\n---\r\n"}.items():
            if parse_envelope(text).state is not EnvelopeState.OK:
                failed.append(f"the {what} does not close the envelope")
        bounds_of = getattr(envelope_reader, "envelope_bounds", None)  # the helper, by its name
        if bounds_of is None:
            failed.append("no envelope_bounds in the shared envelope reader")
        else:
            offsets = {
                "BOM, then a plain envelope": ("\ufeff---\nid: a\n---\nBODY\n", (5, 11, 15)),
                "two BOMs, both skipped and counted": ("\ufeff\ufeff---\nid: a\n---\nB", (6, 12, 16)),
                "CRLF, the closer `--- `": ("---\r\nid: a\r\n--- \r\nB", (5, 12, 18)),
                "a closer that is the last line, with no ending": ("---\nid: a\n---", (4, 10, 13)),
                "a lone CR ends a line": ("---\rid: a\r---\rB", (4, 10, 14)),
                "a form feed before the closer": ("---\nid: a\n\x0c---\n", (4, None, None)),
            }
            for what, (text, wanted) in offsets.items():
                got = bounds_of(text)
                if got is None or (got.yaml_start, got.yaml_end, got.end) != wanted:
                    failed.append(f"{what}: got {got}, wanted {wanted}")
            if bounds_of("# no envelope\n---\n") is not None or bounds_of("") is not None:
                failed.append("an envelope found where the first line is no `---`")
        # the line splitter every reader of a block shares, by its name: (offset, content, next offset)
        lines_of = getattr(envelope_reader, "envelope_lines", None)
        if lines_of is None:
            failed.append("no envelope_lines in the shared envelope reader")
        else:
            cuts = {
                "LF, CRLF and a lone CR": (
                    "a\nb\r\nc\rd",
                    [(0, "a", 2), (2, "b", 5), (5, "c", 7), (7, "d", 8)],
                ),
                "an empty line, a CRLF and a lone CR in a row": (
                    "a\n\r\n\rb\n",
                    [(0, "a", 2), (2, "", 4), (4, "", 5), (5, "b", 7)],
                ),
                "a form feed and U+2028 end nothing": ("a\x0cb c\n", [(0, "a\x0cb c", 6)]),
            }
            for what, (text, wanted_lines) in cuts.items():
                got_lines = list(lines_of(text, 0, len(text)))
                if got_lines != wanted_lines:
                    failed.append(f"envelope_lines, {what}: got {got_lines}, wanted {wanted_lines}")
            # the stop is a wall: a CR at the stop is a lone CR, though a LF follows it
            if list(lines_of("a\r\nb", 0, 2)) != [(0, "a", 2)]:
                failed.append("envelope_lines read past its stop")
        return not failed, (
            "trailing whitespace and CRLF delimit the envelope, a form feed before the closer does not;"
            " the offsets and the line cuts hold"
            if not failed
            else "; ".join(failed)[:600]
        )

    items: list[tuple[int, str, Callable[[], tuple[bool, str]]]] = [
        (101, "exit-code split: a malformed dials file exits 1, never 2, never 0", malformed_dials),
        (102, "C4b: a dials file that is not a mapping", dials_not_mapping),
        (103, "C5: a severity outside block | warn", dials_bad_severity),
        (104, "C5: the module's own namespace must be a mapping", dials_own_namespace),
        (105, "C5: a territory pattern git would read as a comment", dials_comment_pattern),
        (106, "C5: an unsupported territory dialect", dials_unsupported_dialect),
        (107, "C6: the root policy file is missing", root_missing),
        (108, "C7: the root policy on disk has no readable id", root_without_id),
        (109, "C8: the root policy claims no territory", root_claims_nothing),
        (110, "C9: the root policy lies outside its own territory", root_outside_own_territory),
        (111, "absence: python3", python_absent),
        (112, "absence: an interpreter below the floor", python_below_floor),
        (113, "absence: git", git_absent),
        (114, "absence: a declared library (PyYAML)", library_absent),
        (
            115,
            "absence: the shared code, as an install that dropped its link would leave the plugin",
            shared_code_absent,
        ),
        (116, "a failing git is a configuration failure, never a green skip", git_failing),
        (117, "misinvocation exits 1: argparse's exit 2 is overridden", misinvocation),
        (
            118,
            "--help is a misinvocation like any other: no exit path past the guard and the log",
            help_is_not_special,
        ),
        (119, "an abbreviated flag is a misinvocation, not a scan logged as a hook run", abbreviated_flag),
        (120, "unparseable hook input is a configuration failure, not an empty event", unparseable_input),
        (121, "hook input that is JSON but no object says so", input_not_an_object),
        (122, "a Write event without its documented fields is a configuration failure", malformed_event),
        (123, "an event for a tool the gates do not judge is a visible skip", other_tool),
        (124, "--scan on a path that does not exist is a configuration failure", scan_missing_path),
        (125, "examined count: a non-Markdown file prints 0 and exits 0", not_markdown),
        (126, "a relative file_path is resolved against the event's cwd", relative_path),
        (127, "a file outside any git repository is a visible skip", outside_any_repository),
        (128, "no dials file: a visible skip", no_dials_file),
        (129, "a dials file with no root_policy: a visible skip", no_root_policy),
        (130, "an Edit whose old_string is absent is a visible skip; the tool reports it", edit_unappliable),
        (
            131,
            "severity warn: exit 0 with the whole finding as JSON for the model and the user",
            severity_warn,
        ),
        (132, "output log: each print is one record, in the plugin data directory", log_in_plugin_data),
        (
            133,
            "output log: the log_dir dial routes the whole run to a git-ignored directory",
            log_in_ignored_dir,
        ),
        (
            134,
            "output log: a log_dir that git does not ignore is a configuration failure",
            log_dir_not_ignored,
        ),
        (135, "output log: rotation past the size limit", log_rotates),
        (136, "output log: a logging failure never changes the verdict", log_failure_keeps_verdict),
        (137, "declared dependencies: requirements.txt equals the preflight table", declared_libraries),
        (138, "C5: the module's own namespace given as null", dials_own_namespace_null),
        (
            139,
            "C5: root_policy, an empty dialect, a namespace and a territory of the wrong shape, log_dir;"
            " the dials written the long way, and the dialect written out, read as plain",
            dials_other_pairs,
        ),
        (
            140,
            "absence, the other way round: the scripts copied with links followed run",
            copy_with_links_followed,
        ),
        (
            141,
            "not fail-open: an unexpected exception exits 1, BROKEN first, the traceback after",
            unexpected_failure,
        ),
        (142, "an Edit event without its documented fields is a configuration failure", edit_without_fields),
        (143, "a stdout that cannot encode the dash still carries the count line", stdout_cannot_encode),
        (
            144,
            "an envelope nested past the parser's depth is blocked, never a crash that lets it through",
            deeply_nested_envelope,
        ),
        (145, "--scan outside any repository is a configuration failure", scan_outside_repository),
        (146, "--scan=DIR and a scan from a subdirectory examine the same repository", scan_forms),
        (147, "a byte-order mark before the envelope is not part of it", byte_order_mark),
        (148, "a file-level negated pattern takes the file out, and the skip names why", negated_pattern),
        (149, "a document where policies live with no readable id earns a note", policy_without_id_note),
        (
            150,
            "an Edit with an empty old_string on an existing file is a visible skip",
            edit_empty_old_string,
        ),
        (
            151,
            "an echoed value a page long is cut, and the cut is said: the verdict stays a message",
            long_value_is_cut,
        ),
        (152, "C12.1: git failing to list the files is a configuration failure", ls_files_fails),
        (153, "C12.2: git failing to make the scratch repository is a configuration failure", init_fails),
        (
            154,
            "C12.3: git check-ignore failing, not merely matching nothing, is a configuration failure",
            check_ignore_fails,
        ),
        (155, "C12.7: a dials file the process cannot read is a configuration failure", dials_unreadable),
        (
            156,
            "C12.10: a document git lists and the scan cannot read is a configuration failure",
            document_unreadable,
        ),
        (
            157,
            "C4: a dials file that is not UTF-8 is C4, its line and column named, never a defect of the gate",
            dials_not_utf8,
        ),
        (
            158,
            "C12.10: a file where policies live that nobody can read is a configuration failure, never a"
            " policy with no id",
            policy_unreadable,
        ),
        (
            159,
            "a green hook run with notes hands them to the model as JSON, one without notes stays plain",
            notes_reach_the_model,
        ),
        (
            160,
            "C5: a key with a line break, a page long, in the module's namespace is one line, cut",
            unknown_dial_is_one_line,
        ),
        (
            161,
            "C5.7: a pattern git would misread in a dial of the module's own is one line, naming it",
            pattern_in_own_dial_is_one_line,
        ),
        (162, "a file named just .md is Markdown to the hook as to the scan", file_named_md),
        (
            163,
            "the findings shown after a write: the first always, then what fits, never more than most",
            cap_keeps_the_first,
        ),
        (
            164,
            "a `---` line with trailing whitespace opens and closes the envelope, and a line-break character"
            " other than \\n, \\r\\n or \\r makes no delimiter",
            envelope_delimiters,
        ),
        (
            165,
            "C12.12, C12.13: a git that gives no answer in a hook ends in a shared line within the budget,"
            " a scan and an act give git no clock, and the hook's handlers outlive the budget",
            git_has_a_budget_in_a_hook,
        ),
    ]
    # Each item carries its number, so it keeps that number in every module and when the list is
    # reordered; a gate that resolves no policy leaves gaps where the items about policies stand. A new
    # item takes the next number after the last, and a removed item leaves its number free: a number
    # is never reissued (rule 4 of plc-0009-shared-code). The numbers are held below, on every build.
    about_policies = {
        root_missing,
        root_without_id,
        root_claims_nothing,
        root_outside_own_territory,
        no_root_policy,
        policy_without_id_note,
        policy_unreadable,
    }
    # A generator has no event, no verdict and no scan: these items are a gate's alone.
    about_events = {
        unparseable_input,
        input_not_an_object,
        malformed_event,
        edit_without_fields,
        other_tool,
        scan_missing_path,
        scan_outside_repository,
        scan_forms,
        not_markdown,
        relative_path,
        outside_any_repository,
        no_dials_file,
        no_root_policy,
        edit_unappliable,
        edit_empty_old_string,
        severity_warn,
        stdout_cannot_encode,
        deeply_nested_envelope,
        envelope_delimiters,
        byte_order_mark,
        negated_pattern,
        document_unreadable,
        file_named_md,
    }
    # A gate wired to Stop examines a repository, never a written file: these items are a tool gate's.
    about_files = {
        other_tool,
        not_markdown,
        relative_path,
        edit_unappliable,
        edit_empty_old_string,
        byte_order_mark,
        negated_pattern,
        deeply_nested_envelope,
        envelope_delimiters,
        file_named_md,
    }
    # A gate wired to Stop never reaches git's file list, the territory's scratch repository or its
    # check-ignore, nor reads a document the scan lists: these items are a tool gate's.
    about_listing = {ls_files_fails, init_fails, check_ignore_fails, document_unreadable}
    # A gate without a hook mode never reads hook input, a written file or the warn channel, and
    # takes a file out of its territory with a count, not a skip: these items are a hook gate's.
    about_hooks = {
        unparseable_input,
        input_not_an_object,
        malformed_event,
        edit_without_fields,
        other_tool,
        not_markdown,
        relative_path,
        outside_any_repository,
        edit_unappliable,
        edit_empty_old_string,
        severity_warn,
        negated_pattern,
        file_named_md,
    }
    numbers = [number for number, _, _ in items]
    for before, after in zip(numbers, numbers[1:], strict=False):
        if after <= before:
            raise ValueError(
                f"shared item number {after} follows {before}: the numbers must be unique and rising"
            )
    if first != numbers[0]:
        raise ValueError(f"shared items start at number {numbers[0]}, but first={first} was asked")
    return [
        Assertion(number, title, check)
        for number, title, check in items
        if (s.resolves_policies or check not in about_policies)
        and (s.judges_envelopes or check not in (deeply_nested_envelope, envelope_delimiters))
        and (s.event_driven or check not in about_events)
        and (not no_file or check not in about_files)
        and (not no_file or check not in about_listing)
        and (not s.scan_only or check not in about_hooks)
        and (s.long_value is not None or check is not long_value_is_cut)
        and (s.pattern_dial is not None or check is not pattern_in_own_dial_is_one_line)
        and (s.noted is not None or check is not notes_reach_the_model)
    ]
