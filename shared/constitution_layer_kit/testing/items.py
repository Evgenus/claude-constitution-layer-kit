"""The acceptance items of what every gate shares — the exit-code split, the absence of each
external tool, hook input, paths, the warn channel, the output log — written once and run by
pytest in each module's folder through that module's real entry point.

A module hands over a Subject, as the session fixture `subject` of its conftest: its harness, a
function that runs its gate on a prepared consumer, one write it passes and one it blocks. Each
item is a test carrying its number, from 101 on, the numbers unique and rising in the file; an item
the module's Subject leaves out is skipped, the reason naming the flag, and its number stays free.
"""

from __future__ import annotations

import ast
import contextvars
import importlib
import inspect
import json
import os
import re
import shlex
import shutil
import site
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from contextlib import nullcontext
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

import pytest

from constitution_layer_kit import __version__ as package_version
from constitution_layer_kit import cli, identity, messages, pipeline, preflight, repository
from constitution_layer_kit import envelope as envelope_reader
from constitution_layer_kit.dials import load_dials, load_kernel_part
from constitution_layer_kit.envelope import ID_RE, declared_policy, document_id, parse_envelope
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import (
    DECLARATION,
    DIALECT,
    KERNEL_KEYS,
    Broken,
    EnvelopeState,
    Finding,
    Mode,
    SharedKey,
)
from constitution_layer_kit.output import ROTATE_AT, log_name
from constitution_layer_kit.repository import list_markdown

from .acceptance import broken_first_line, expect, item
from .consumer import CONSTITUTION_FILE, CONSTITUTION_PREFIX, ROOT_POLICY, own_prefix
from .harness import (
    SHARED,
    TRANSCRIPT,
    Edit,
    Harness,
    Result,
    Write,
    ask_reason,
    bash_json,
    event_json,
    red_lines,
    stop_json,
)

NO_ENVELOPE = "# Fixture\n\nNo envelope at all.\n"
PACKAGE = "constitution_layer_kit"  # the shared package, a folder of the kit's `shared/`

# Run at the start of a gate's process, through a `sitecustomize` on PYTHONPATH — any module's entry
# point, whatever its wrapper. It logs the `timeout=` each git call is given, one line, the call after it;
# and where the environment names a trigger and a lower budget, it lowers the budget of the one call whose
# arguments hold the trigger — and only where the gate gave that call a budget at all, so that a gate with
# none stays without one. Where the environment asks for it, every other call runs with no clock and the
# deadline's clock stands still: a fake git the case has just written takes seconds to start the first time
# on a loaded machine (0.2 to 3.1 s measured on macOS on 2026-10-16, 0.02 s each time after), so the real
# budget of 3 s could cut a call the case never meant to cut.
# It also logs the `hook_seconds` of each scope the process opens (`identity.declared`), and where the
# environment names a lower hook budget it opens the scope with that many seconds in place of the gate's
# own: the one deadline of a hook run, lowered for the case that spends it.
GIT_PATCH = """\
import dataclasses
import os
import subprocess
import sys
import types

from constitution_layer_kit import identity, repository

lowered = os.environ.get("GIT_PATCH_SECONDS")
trigger = os.environ.get("GIT_PATCH_TRIGGER")
hook_lowered = os.environ.get("GIT_PATCH_HOOK_SECONDS")
late = os.environ.get("GIT_PATCH_LATE")
unclocked = os.environ.get("GIT_PATCH_UNCLOCKED")
log, run, declared = os.environ["GIT_PATCH_LOG"], subprocess.run, identity.declared
if late or unclocked:  # the deadline's clock stands still but for the lateness of git's answers
    clock = [0.0]
    identity.time = types.SimpleNamespace(monotonic=lambda: clock[0])


def spy(command, *args, **kwargs):
    if command[0] == "git":
        with open(log, "a") as out:
            out.write(repr(kwargs.get("timeout")) + " " + repr(command[1:]) + "\\n")
        if lowered and trigger in command[1:] and kwargs.get("timeout") is not None:
            repository.GIT_SECONDS = kwargs["timeout"] = float(lowered)
        elif unclocked:  # only the call the case cuts waits on a clock: the machine's speed cuts none
            kwargs.pop("timeout", None)
        if late and kwargs.get("timeout") is not None:  # the fake clock alone decides whether it is cut
            given = kwargs.pop("timeout")
            if float(late) >= given:
                clock[0] += given
                raise subprocess.TimeoutExpired(command, given)
            clock[0] += float(late)
    return run(command, *args, **kwargs)


def declaring(gate, mode=None):
    if hook_lowered:
        gate = dataclasses.replace(gate, hook_seconds=float(hook_lowered))
    with open(log + "-hook-seconds", "a") as out:
        out.write(repr(gate.hook_seconds) + "\\n")
    return declared(gate, mode)


subprocess.run = spy
identity.declared = declaring
"""
HANG_SECONDS = 0.5  # the budget of the one call a hang case lowers it for: the case waits well under a second
# What a hang case allows the whole run, the gate's start-up included. It only stops an endless wait, so it is
# far above anything a loaded machine takes; the assertion that matters is the line from the 0.5 s budget.
HANG_BOUND = 20.0


def git_patch(
    h: Harness,
    seconds: float | None = None,
    trigger: str | None = None,
    hook_seconds: float | None = None,
    late: float | None = None,
    unclocked: bool = False,
) -> tuple[dict[str, str], Path]:
    """The environment that makes a gate's process log the `timeout=` of each git call it makes and the
    `hook_seconds` its scope is opened with, and, with `seconds` and a `trigger`, give the call whose
    arguments hold the trigger that many seconds, and, with `hook_seconds`, declare the gate with that hook
    budget in place of its own; with the log it writes. With `late`, the deadline reads a clock of the patch's
    own, which starts at 0 and moves only when git answers: by `late` seconds for each call given more,
    and by the whole of what a call was given when `late` is as much or more, that call then cut as the
    timeout cuts it, with no git started. So which call the deadline meets follows from the numbers
    alone, never from how fast the machine runs; a call that answers runs with no clock. With `unclocked`,
    every call but the one `trigger` and `seconds` lower runs with no clock, and the deadline's clock stands
    still: the log still holds the budget the gate gave each call, and no call the case did not choose is cut
    by a slow start of a fake git just written."""
    folder = h.scratch_dir()
    (folder / "sitecustomize.py").write_text(GIT_PATCH, encoding="utf-8")
    log = folder / "git-calls"
    env = {
        "PYTHONPATH": os.pathsep.join(filter(None, [str(folder), os.environ.get("PYTHONPATH")])),
        "GIT_PATCH_LOG": str(log),
    }
    if seconds is not None and trigger is not None:
        env["GIT_PATCH_SECONDS"] = repr(seconds)
        env["GIT_PATCH_TRIGGER"] = trigger
    if hook_seconds is not None:
        env["GIT_PATCH_HOOK_SECONDS"] = repr(hook_seconds)
    if late is not None:
        env["GIT_PATCH_LATE"] = repr(late)
    if unclocked:
        env["GIT_PATCH_UNCLOCKED"] = "1"
    return env, log


def git_timeouts(log: Path) -> list[str]:
    """The `timeout=` of each git call the log holds, as `repr` wrote it: "None" for no clock."""
    return [line.split(" ", 1)[0] for line in log.read_text().splitlines()] if log.exists() else []


def declared_hook_seconds(log: Path) -> list[str]:
    """The `hook_seconds` of each declaration the process made, as `repr` wrote it, one per line."""
    kept = log.with_name(log.name + "-hook-seconds")
    return kept.read_text().splitlines() if kept.exists() else []


def entry_requires(entry: Path) -> str:
    """The release of the shared package that an entry file requires: the string it assigns to `REQUIRES`
    at the top of the file, read from its syntax tree, never run."""
    for node in ast.parse(entry.read_text(encoding="utf-8")).body:
        if (
            isinstance(node, ast.Assign)
            and [target.id for target in node.targets if isinstance(target, ast.Name)] == ["REQUIRES"]
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    pytest.fail(f"{entry} assigns no string to REQUIRES at its top level")


def hook_budget(calls: list[str]) -> None:
    """Every git call of a run whose scope opened in hook mode carried the hook's budget; there was one."""
    assert bool(calls) and set(calls) == {repr(repository.GIT_SECONDS)}, f"the git calls' timeouts: {calls}"


def no_clock(calls: list[str]) -> None:
    """Every git call of a scan or an act carried no timeout, and there was one."""
    assert bool(calls) and set(calls) == {"None"}, f"the git calls' timeouts: {calls}"


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
    skill: str = ""  # the skill a red of `red` names after its count line (F10), typed by hand; empty: the
    # gate names none for that mode, and the item about the line is left out


AS_ROOT = (
    "NOT EXERCISED: running as root, where a mode bit does not deny a read — 0 unreadable files examined"
)


def reader_delimiter_failures() -> list[str]:
    """What the envelope reader makes of a break character before the closer and of the closers that
    still close, on text typed by hand."""
    failed = []
    for breaker in "\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029":
        if parse_envelope(f"---\nid: a\n{breaker}---\nBODY\n").state is not EnvelopeState.UNTERMINATED:
            failed.append(f"{breaker!r} before the closer makes a delimiter")
    for what, text in {"closer `--- `": "---\nid: a\n--- \n", "CRLF": "---\r\nid: a\r\n---\r\n"}.items():
        if parse_envelope(text).state is not EnvelopeState.OK:
            failed.append(f"the {what} does not close the envelope")
    return failed


def envelope_bounds_failures() -> list[str]:
    """The offsets the shared helper `envelope_bounds` gives, typed by hand, a byte-order mark counted."""
    bounds_of = getattr(envelope_reader, "envelope_bounds", None)  # the helper, by its name
    if bounds_of is None:
        return ["no envelope_bounds in the shared envelope reader"]
    failed = []
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
    return failed


def envelope_lines_failures() -> list[str]:
    """The cuts the shared line splitter `envelope_lines` makes, as (offset, content, next offset)."""
    lines_of = getattr(envelope_reader, "envelope_lines", None)
    if lines_of is None:
        return ["no envelope_lines in the shared envelope reader"]
    failed = []
    cuts = {
        "LF, CRLF and a lone CR": (
            "a\nb\r\nc\rd",
            [(0, "a", 2), (2, "b", 5), (5, "c", 7), (7, "d", 8)],
        ),
        "an empty line, a CRLF and a lone CR in a row": (
            "a\n\r\n\rb\n",
            [(0, "a", 2), (2, "", 4), (4, "", 5), (5, "b", 7)],
        ),
        "a form feed and U+2028 end nothing": ("a\x0cb\u2028c\n", [(0, "a\x0cb\u2028c", 6)]),
    }
    for what, (text, wanted_lines) in cuts.items():
        got_lines = list(lines_of(text, 0, len(text)))
        if got_lines != wanted_lines:
            failed.append(f"envelope_lines, {what}: got {got_lines}, wanted {wanted_lines}")
    # the stop is a wall: a CR at the stop is a lone CR, though a LF follows it
    if list(lines_of("a\r\nb", 0, 2)) != [(0, "a", 2)]:
        failed.append("envelope_lines read past its stop")
    return failed


class SharedItems:
    """The shared acceptance items of one Subject, one method each, and the helpers they use."""

    def __init__(self, s: Subject) -> None:
        self.s = s
        self.h = s.harness
        self.ns = s.harness.namespace
        self.stop = s.event == "Stop"
        self.shell = s.event == "Bash"
        # the gate examines no written file: the items about one are not its own
        self.no_file = self.stop or self.shell
        self.red_code = 0 if s.ask else 2
        # The gate's layer, from the identity the session's scope declares: its own dials file, that file's
        # kernel keys and its prefix. A gate of this kit reads everything from the constitution's file; a
        # gate of another layer reads its namespace from its own and the policies from the constitution's,
        # whose consumer prefix is then the consumer's own.
        declared = identity.current()
        self.file = declared.dials_file
        self.kernel_keys = declared.kernel_keys
        self.prefix = own_prefix(self.ns)
        self.layered = self.file != CONSTITUTION_FILE
        self.constitution_prefix = CONSTITUTION_PREFIX if self.layered else self.prefix

    def payload(self, root: Path, action: Write | Edit) -> str:
        """The event an item sends itself: the write, or, for a Stop gate, a Stop in that repository,
        or, for a shell gate, the shell tool with the action's text as its command."""
        if self.stop:
            return stop_json(root)
        if self.shell:
            return bash_json(root, action.text if isinstance(action, Write) else action.new)
        return event_json(root, action)

    def red_said(self, result: Result) -> str:
        """What a red run said: stderr for a block, the reason of the ask verdict for an asking gate,
        stdout for a scan."""
        if self.s.scan_only:
            return result.stdout
        return (ask_reason(result) or "") if self.s.ask else result.stderr

    def scan_args(self, root: Path) -> list[str]:
        """The scan of a gate without a hook mode, on the consumer's root."""
        return ["--scan", str(root)]

    def of_constitution(self, build: Callable[[], Broken]) -> Broken:
        """A shared failure of the constitution's file, built as the gate builds it: for a gate of another
        layer, which reads the policies and resolves them in a scope of `reading` that file, inside one."""
        if not self.layered:
            return build()
        with identity.reading(CONSTITUTION_FILE, KERNEL_KEYS):
            return build()

    def broken(self, result: Result, failure: Broken) -> None:
        self.broken_as_typed(result, failure.render())

    def broken_as_typed(self, result: Result, line: str, label: str = "") -> None:
        """The failure's line first — typed by hand where the item types it — then the closing line."""
        broken_first_line(result, line, label)
        counted = self.s.closing in result.stderr  # a run that examined, or changed, nothing says so
        said = f"no count line after: {result.stderr.strip()}"
        assert counted, f"{label}: {said}" if label else said

    def bin_with(self, *tools: str) -> str:
        """A PATH directory holding only the named tools, to simulate the absence of the rest."""
        directory = self.h.scratch_dir()
        for tool in tools:
            source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
            assert source, tool
            os.symlink(source, directory / tool)
        return str(directory)

    # ---------------------------------------------------------------- the shared package: absent, old, new

    def clause(self) -> str:
        """What closes `C15`, `C16` and `C17` behind a dash in the entry file: the identity's
        `until_installed`; a generator's closing carries none, its text ending after `says`."""
        return f" — {identity.current().until_installed}" if self.s.event_driven else ""

    def guide(self) -> Path:
        """The install note the lines send to: `INSTALL.md` in the folder above the entry file's."""
        return self.h.entry.parent.parent / "INSTALL.md"

    def package_missing(self, guide: Path) -> str:
        """`C15` as the entry file prints it, typed by hand: the version it requires and that version's
        major, the path of the plugin's own install note, escaped, and the module's clause."""
        required = entry_requires(self.h.entry)
        return (
            f"BROKEN: {self.ns} needs the Python package constitution-layer-kit {required} or a later"
            f" {required.partition('.')[0]}.x release, and python3 cannot import it — fix: install it for"
            f" python3 as {messages.escaped(str(guide))} says{self.clause()}"
        )

    def package_too_old(self, found: str, guide: Path) -> str:
        """`C16` as the entry file prints it, typed by hand, for an installed release `found`."""
        required = entry_requires(self.h.entry)
        return (
            f"BROKEN: {self.ns} needs constitution-layer-kit {required} or a later"
            f" {required.partition('.')[0]}.x release, found {found} — fix: install one for python3 as"
            f" {messages.escaped(str(guide))} says{self.clause()}"
        )

    def module_too_old(self, found: str, guide: Path) -> str:
        """`C17` as the entry file prints it, typed by hand, for an installed release `found`."""
        required = entry_requires(self.h.entry)
        return (
            f"BROKEN: {self.ns} was written for constitution-layer-kit {required}, a"
            f" {required.partition('.')[0]}.x release, found {found} — fix: update the plugin to a release"
            f" written for {found.partition('.')[0]}.x, or install a {required.partition('.')[0]}.x release"
            f" of constitution-layer-kit for python3 as {messages.escaped(str(guide))} says{self.clause()}"
        )

    def release_with(self, version: str) -> dict[str, str]:
        """The environment that puts a copy of the shared package first on PYTHONPATH, its `__version__`
        set to `version`: the gate imports the copy, since the harness's own folder comes after it."""
        folder = self.h.scratch_dir()
        copy = folder / PACKAGE
        shutil.copytree(SHARED / PACKAGE, copy, ignore=shutil.ignore_patterns("__pycache__"))
        init = copy / "__init__.py"
        text = init.read_text(encoding="utf-8")
        stated = f'__version__ = "{package_version}"'
        assert text.count(stated) == 1, f"{init} does not state its version as {stated}"
        init.write_text(text.replace(stated, f'__version__ = "{version}"'), encoding="utf-8")
        return {"PYTHONPATH": str(folder)}

    def installed_release(self) -> tuple[dict[str, str], Path, Path]:
        """A release of the shared package where an install puts it, behind every folder of PYTHONPATH: the
        site-packages of a new virtual environment, made as the kit's install check makes its own (from the
        python3 the tests run under, with that python3's packages, PyYAML among them, named by a `.pth` file
        of its own). The copy is of the working tree's version, which serves every module, and it is marked:
        importing it creates the file `mark`. Returns the environment that puts the new environment's `bin`
        first on PATH and leaves PYTHONPATH empty, that mark, and the copy's `__init__.py`."""
        home = self.h.scratch_dir() / "installed"
        made = [sys.executable, "-m", "venv", "--system-site-packages", "--without-pip", str(home)]
        subprocess.run(made, capture_output=True, check=True)
        python = home / "bin" / "python3"
        where = subprocess.run(
            [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = Path(where.stdout.strip())
        outer = [*site.getsitepackages(), site.getusersitepackages()]
        (packages / "outer.pth").write_text("".join(f"{folder}\n" for folder in outer), encoding="utf-8")
        copy = packages / PACKAGE
        shutil.copytree(SHARED / PACKAGE, copy, ignore=shutil.ignore_patterns("__pycache__"))
        mark = home / "imported"
        with (copy / "__init__.py").open("a", encoding="utf-8") as init:
            init.write(f"\nopen({str(mark)!r}, 'a', encoding='utf-8').close()  # the mark of this copy\n")
        path = os.pathsep.join(filter(None, [str(home / "bin"), os.environ.get("PATH")]))
        return {"PATH": path, "PYTHONPATH": ""}, mark, copy / "__init__.py"

    def valid_run(
        self, env: dict[str, str] | None = None, command: Sequence[str] | None = None
    ) -> tuple[Result, str]:
        """A run the gate passes, as each kind of gate is run: a generator's act from inside a fresh
        consumer, a scan over a consumer holding the passed document, the event of a gate on no file, and
        for a gate on a file a README with no envelope. The result, and the green line it says."""
        consumer = self.h.fresh_consumer()
        if not self.s.event_driven:
            result = self.h.run_gate("", args=self.s.act_args, env=env, command=command, cwd=consumer.root)
            return result, self.s.green
        if self.s.scan_only:
            consumer.write(self.s.valid.target, self.s.valid.text)
            result = self.h.run_gate("", args=self.scan_args(consumer.root), env=env, command=command)
            return result, self.s.green
        if self.no_file:
            result = self.h.run_gate(self.payload(consumer.root, self.s.valid), env=env, command=command)
            return result, self.s.green
        event = event_json(consumer.root, Write("README.md", NO_ENVELOPE))
        return self.h.run_gate(event, env=env, command=command), self.s.bare_readme

    # ---------------------------------------------------------------- the dials file

    # ---------------------------------------------------------------- absence of what the gate needs

    # ---------------------------------------------------------------- invocation and hook input

    # ---------------------------------------------------------------- paths and skips

    def green_said(self, result: Result) -> str:
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

    # ---------------------------------------------------------------- the warn channel

    # ---------------------------------------------------------------- the output log

    def log_lines(self, path: Path) -> list[dict[str, str]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    # ---------------------------------------------------------------- git failing in one way; a file unread

    def git_failing_at(
        self,
        trigger: str,
        code: int,
        line: Callable[[Path], str],
        through_scan: bool = False,
        then: str = "",
        hangs: bool = False,
    ) -> None:
        """A git first on PATH that exits `code` when one of its arguments is `trigger`, and hands every
        other call to the real git — so the gate gets as far as that one call. `through_scan`: the
        failing git is met by the scan on the prepared consumer, for a gate whose hook never makes
        the call. `then`: a second stderr line the failing git adds, which no message may carry.
        `hangs`: the git does not fail but never answers — it becomes a process that waits for ever,
        which the budget kills — and the hook run, whose budget is lowered to `HANG_SECONDS`, is bounded
        by the case itself, so that a gate with no budget reads as a red item, not an endless wait. Every
        other call runs with no clock (`git_patch`, `unclocked`): the fake is a file just written, whose
        first start on a loaded machine has taken longer than the 3 s a hook gives git."""
        real, silent = shutil.which("git"), shutil.which("tail")
        if real is None or silent is None:
            pytest.fail("no git or no tail on PATH: the fake git hands every other call to the real one")
        directory = self.h.scratch_dir()
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
        cut = (HANG_SECONDS, trigger) if hangs else (None, None)
        env.update(git_patch(self.h, *cut, unclocked=True)[0])
        with self.h.bounded(HANG_BOUND) if hangs else nullcontext():
            if through_scan:
                _, root = self.s.gate_on(self.s.valid)
                result = self.h.run_gate("", args=self.scan_args(root), env=env)
            else:
                result, root = self.s.gate_on(self.s.valid, env=env)
        self.broken_as_typed(result, line(root))

    # ---------------------------------------------------------------- the budget of a git call

    def silent_git(self, subcommand: str, directory: str, call: str, quoted: str | None = None) -> str:
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

    def silent_scratch(self, subcommand: str) -> str:
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

    def quoted_by_hand(self, path: str) -> str:
        """A path as a shell takes it whole, typed out: single quotes, and each single quote inside closed,
        written between double quotes, and opened again."""
        return "'" + path.replace("'", "'\"'\"'") + "'"

    def nearest_folder(self, root: Path) -> str:
        """Where the hook's `rev-parse` runs: the written file's folder, or the nearest one that exists,
        for a gate on a file; the event's directory for one without a file."""
        probe = root if self.no_file else (root / self.s.valid.target).parent
        while not probe.is_dir():
            probe = probe.parent
        return str(probe)

    def git_calls(self, run: Callable[[dict[str, str]], object]) -> list[str]:
        """The `timeout=` of each git call `run` made, as logged by the patch in its environment."""
        env, log = git_patch(self.h)
        run(env)
        return git_timeouts(log)

    def budget_by_mode(self) -> None:
        """The rule at its one decision point, in a process of its own for each mode: a hook gives git
        `GIT_SECONDS`; a scan, an act and a scope opened with no mode give it no clock."""
        program = (
            "import json, sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from constitution_layer_kit import identity, repository\n"
            "from constitution_layer_kit.model import Mode\n"
            "mode = {'hook': Mode.HOOK, 'scan': Mode.SCAN, 'act': Mode.ACT, 'none': None}[sys.argv[2]]\n"
            "who = identity.Identity('x', 'y', Path('.'), 'x.yaml', ('module_prefix',))\n"
            "with identity.declared(who, mode):\n"
            "    print(json.dumps(repository.budget()))\n"
        )
        seen: dict[str, object] = {}
        for mode in ("hook", "scan", "act", "none"):
            done = subprocess.run(
                [sys.executable, "-c", program, str(SHARED), mode],
                capture_output=True,
                text=True,
                check=False,
            )
            seen[mode] = json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip()
        wanted: dict[str, object] = {"hook": repository.GIT_SECONDS, "scan": None, "act": None, "none": None}
        assert seen == wanted, f"the budget by mode: {seen}"

    def git_words(self) -> None:
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
        assert ok, f"subcommands {got}; the call as typed {[real for real, _ in words]}"

    def scopes_shadow(self) -> None:
        """A scope opened inside another shadows the outer declaration until it closes, and the outer one
        holds again after it, whether the inner one is the same identity in the same mode or not. Read in a
        process of its own as the gate's name, the dials file's name and the git budget the mode gives:
        a hook gives git a clock, a scan and an act none."""
        program = (
            "import json, sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from constitution_layer_kit import identity, repository\n"
            "from constitution_layer_kit.model import Mode\n"
            "who = identity.Identity('x', 'y', Path('.'), 'x.yaml', ('module_prefix',))\n"
            "other = identity.Identity('x', 'z', Path('.'), 'z.yaml', ('module_prefix',))\n"
            "seen = []\n"
            "def read():\n"
            "    clocked = repository.budget() is not None\n"
            "    seen.append([identity.current().gate, identity.dials_file(), clocked])\n"
            "with identity.declared(who, Mode.HOOK):\n"
            "    read()\n"
            "    with identity.declared(who, Mode.HOOK):\n"
            "        read()\n"
            "    with identity.declared(who, Mode.SCAN):\n"
            "        read()\n"
            "    with identity.declared(other, Mode.ACT):\n"
            "        read()\n"
            "    read()\n"
            "print(json.dumps(seen))\n"
        )
        done = subprocess.run(
            [sys.executable, "-c", program, str(SHARED)], capture_output=True, text=True, check=False
        )
        wanted = [  # typed by hand: the gate, the file, whether git has a clock
            ["y", "x.yaml", True],  # the outer scope
            ["y", "x.yaml", True],  # the same identity and mode again
            ["y", "x.yaml", False],  # the same identity in a scan
            ["z", "z.yaml", False],  # another identity, its file and mode
            ["y", "x.yaml", True],  # the outer one holds again
        ]
        seen = json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip()[-200:]
        assert seen == wanted, f"exit {done.returncode}: wanted {wanted}, got {seen}"

    def is_file(self, word: str) -> bool:
        """A word that is an existing file; one the filesystem will not answer for counts as one, since
        a script that cannot be read is held to the rule."""
        try:
            return Path(word).is_file()
        except OSError:
            return True

    def handlers_outlive_git(self, plugin: Path, hook_seconds: float) -> tuple[bool, str]:
        """Every handler of the plugin's hooks file whose script names python3 has a timeout of at least
        `hook_seconds` (the one the gate is declared with) plus `LEFT_FOR_THE_REST` (limit 16): the hook's
        deadline, and so a git that hangs, ends with the gate's own line before the platform cuts the hook,
        which says nothing. The floor implies that the timeout is above `GIT_SECONDS`. A handler's scripts
        are each of its `args` that is no option (`--subagent`), and each word of its `command` that, once
        `${CLAUDE_PLUGIN_ROOT}` (or the unbraced `$CLAUDE_PLUGIN_ROOT`, as a shell expands it) is replaced,
        is a path under the plugin's folder or an existing file: a redirection, an option or any other word
        is no script. A handler whose `command` names python3 as a word is held too, and a script that
        cannot be read, a missing one under the plugin's folder included, counts as one that names
        python3."""
        floor = hook_seconds + identity.LEFT_FOR_THE_REST
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
            words = [re.sub(r"\$\{CLAUDE_PLUGIN_ROOT\}|\$CLAUDE_PLUGIN_ROOT(?!\w)", root, w) for w in words]
            scripts = [
                a.replace("${CLAUDE_PLUGIN_ROOT}", root)
                for a in handler.get("args", [])
                if not a.startswith("-")
            ] + [w for w in words if w.startswith(root + os.sep) or self.is_file(w)]
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
            if not numeric or timeout < floor:
                short.append(f"{event} handler {command!r} {scripts} has timeout {timeout!r}")
        if checked == 0:
            return False, f"{hooks} holds no handler whose script names python3"
        if short:
            return False, (
                f"{'; '.join(short)} — under the {floor:g} s of the hook's budget ({hook_seconds:g} s) and"
                f" LEFT_FOR_THE_REST ({identity.LEFT_FOR_THE_REST:g} s): a hook that spends its deadline"
                " would be cut by the platform before the gate said so"
            )
        return (
            True,
            f"{checked} handler(s) whose script names python3 hold {floor:g} s: the hook's budget"
            f" ({hook_seconds:g} s) and LEFT_FOR_THE_REST ({identity.LEFT_FOR_THE_REST:g} s)",
        )

    def the_tie_catches_a_short_handler(self) -> None:
        """The tie on hooks files made here, for a hook budget of 10 s: a timeout one second under the
        floor, the budget and LEFT_FOR_THE_REST, fails and one at the floor passes, for a handler whose
        script names python3 given as `command: sh` with `args` and given in shell form (`command` alone,
        naming python3 or a script that does), and a handler whose command and scripts name no python3 is
        not held to it."""
        plugin = self.h.scratch_dir()
        (plugin / "hooks").mkdir()
        (plugin / "scripts").mkdir()
        (plugin / "scripts" / "gate.sh").write_text('exec python3 "$0.py"\n', encoding="utf-8")
        (plugin / "scripts" / "print.sh").write_text("cat rule.txt\n", encoding="utf-8")
        root = "${CLAUDE_PLUGIN_ROOT}/scripts/"
        hook_seconds = 10
        enough = hook_seconds + identity.LEFT_FOR_THE_REST  # the floor: held at it, and the test's "above"
        under = enough - 1  # one second under it

        def exec_form(name: str, timeout: float) -> dict[str, object]:
            return {"type": "command", "command": "sh", "args": [root + name], "timeout": timeout}

        def shell_form(command: str, timeout: float) -> dict[str, object]:
            return {"type": "command", "command": command, "timeout": timeout}

        def with_option(name: str, timeout: float) -> dict[str, object]:
            return {
                "type": "command",
                "command": "sh",
                "args": [root + name, "--subagent"],
                "timeout": timeout,
            }

        def holds(*handlers: dict[str, object]) -> tuple[bool, str]:
            spec = {"hooks": {"PreToolUse": [{"matcher": "Write", "hooks": list(handlers)}]}}
            (plugin / "hooks" / "hooks.json").write_text(json.dumps(spec), encoding="utf-8")
            return self.handlers_outlive_git(plugin, hook_seconds)

        cases: list[tuple[str, bool, tuple[dict[str, object], ...]]] = [
            ("exec form, one second under the floor", False, (exec_form("gate.sh", under),)),
            (
                "exec form at the floor, a print handler at 1 s",
                True,
                (exec_form("gate.sh", enough), exec_form("print.sh", 1)),
            ),
            # An option among the `args` is no script that cannot be read: a printer given `--subagent`, at
            # 1 s, beside a held handler at the floor, is not held; the same option after a script that
            # names python3 does not release it.
            (
                "exec form `print.sh --subagent` at 1 s, beside a held handler at the floor",
                True,
                (with_option("print.sh", 1), exec_form("gate.sh", enough)),
            ),
            (
                "exec form `gate.sh --subagent`, one second under the floor",
                False,
                (with_option("gate.sh", under),),
            ),
            # Shell form (N55): no `args`, the handler's `command` alone. A held handler one second under
            # the floor stands beside one at it, so that a handler the tie skips is a green, never the red
            # of a file with no handler to hold.
            (
                "shell form naming python3, one second under the floor",
                False,
                (shell_form(f"python3 {root}x.py", under), exec_form("gate.sh", enough)),
            ),
            ("shell form naming python3, at the floor", True, (shell_form(f'python3 "{root}x.py"', enough),)),
            (
                "shell form naming a script that names python3, one second under the floor",
                False,
                (shell_form(f"sh {root}gate.sh", under), exec_form("gate.sh", enough)),
            ),
            (
                "shell form naming a script that names python3, at the floor",
                True,
                (shell_form(f"sh {root}gate.sh", enough),),
            ),
            # D1: python3 as a word of the command, no path word, no file to be unreadable.
            (
                "shell form `python3 -c pass`, no path word, one second under the floor",
                False,
                (shell_form("python3 -c pass", under), exec_form("gate.sh", enough)),
            ),
            ("shell form `python3 -c pass`, at the floor", True, (shell_form("python3 -c pass", enough),)),
            # An unbalanced quote: the words fall back to whitespace, the script is still found.
            (
                "shell form with an unbalanced quote naming a python3 script, one second under the floor",
                False,
                (shell_form(f"sh {root}gate.sh 'x", under), exec_form("gate.sh", enough)),
            ),
            # A word with a separator that is no script: a redirection, an option, a path outside.
            (
                "shell form `print.sh 2>/dev/null` and `--x=/a`, naming no python3, beside a held handler",
                True,
                (
                    shell_form(f"sh {root}print.sh --x=/a b/c 2>/dev/null", 1),
                    exec_form("gate.sh", enough),
                ),
            ),
            # A script of `args` that does not exist counts as one that names python3, as before B2.
            (
                "exec form whose script is missing, one second under the floor",
                False,
                (exec_form("missing.sh", under), exec_form("gate.sh", enough)),
            ),
            (
                "shell form whose script under the plugin's folder is missing, one second under the floor",
                False,
                (shell_form(f"sh {root}missing.sh", under), exec_form("gate.sh", enough)),
            ),
            (
                "shell form naming no python3 beside a held handler at the floor",
                True,
                (shell_form(f"sh {root}print.sh", 1), exec_form("gate.sh", enough)),
            ),
        ]
        # D-b: the unbraced form a shell expands names the same script.
        cases.append(
            (
                "shell form with `$CLAUDE_PLUGIN_ROOT` unbraced, naming a script, one second under the floor",
                False,
                (
                    shell_form("sh $CLAUDE_PLUGIN_ROOT/scripts/gate.sh", under),
                    exec_form("gate.sh", enough),
                ),
            )
        )
        results = [(label, expected, holds(*handlers)) for label, expected, handlers in cases]
        # D-a: a word outside the plugin, in a folder that cannot be searched. Where the filesystem will
        # not answer, `is_file` raises (Python 3.12) and the word counts as a script that cannot be read:
        # red. Where it answers, as for root or on a newer Python, the word is what the answer says.
        locked = self.h.scratch_dir() / "locked"
        locked.mkdir()
        (locked / "x.sh").write_text("exec python3 x.py\n", encoding="utf-8")
        locked.chmod(0o000)
        try:
            try:
                answer = (locked / "x.sh").is_file()
            except OSError:
                answer = True
            results.append(
                (
                    "shell form naming a file in a folder that cannot be searched, a second under the floor",
                    not answer,
                    holds(shell_form(f"sh {locked}/x.sh", under), exec_form("gate.sh", enough)),
                )
            )
        finally:
            locked.chmod(0o700)
        ok = all(got[0] == expected for _, expected, got in results)
        said = "; ".join(
            f"{label}: {'green' if got[0] else 'red'} (wanted {'green' if expected else 'red'})"
            for label, expected, got in results
        )
        assert ok, said

    def hangs_in_a_folder_to_quote(self) -> None:
        """The folder C12.12 names stands in the fix's two commands quoted for a shell: a repository
        whose folder holds a space and a single quote, a git that hangs at the root's `rev-parse` (the call
        every hook makes first), the line typed with the folder as a shell takes it whole."""
        kept = self.h.scratch
        odd = kept / "a folder it's"
        odd.mkdir()
        self.h.scratch = odd  # every consumer the gate runs on is made under it, for as long as the case runs
        try:
            self.git_failing_at(
                "rev-parse",
                0,
                lambda root: self.silent_git(
                    "rev-parse",
                    self.nearest_folder(root),
                    "rev-parse --show-toplevel",
                    self.quoted_by_hand(self.nearest_folder(root)),
                ),
                hangs=True,
            )
            return
        finally:
            self.h.scratch = kept

    def attempted(self, check: Callable[[], None]) -> tuple[bool, str]:
        """One check of the item that fails or cannot run is a red check with its error, and hides no
        other: its assertion, a `pytest.fail` and any other error alike are gathered, never raised."""
        try:
            check()
        except (Exception, pytest.fail.Exception) as error:  # noqa: BLE001 — any failure of the check is its red
            return False, f"{check.__name__} raised {type(error).__name__}: {error}"
        return True, check.__name__

    # ---------------------------------------------------------------- the one deadline of a hook run

    def spent(self, seconds: str, before: str) -> str:
        """C12.14 as the deadline cases type it, for a hook budget of `seconds` (as `{:g}` writes it)."""
        return (
            f"BROKEN: the hook's budget of {seconds} s is spent before {before} — fix: a hook of many waits,"
            " each within its own limit, would otherwise be cut by the platform with no word of what was"
            " slow: run the scan, which has no clock, to check the same tree; where git itself is slow,"
            " look for a core.fsmonitor hook, set in the repository's or in your own configuration, with"
            " git config --show-origin --get core.fsmonitor (no output means none is set), or for a"
            " stalled file system, and repair it"
        )

    def deadline_by_mode(self) -> None:
        """The rule at its decision point, in a process of its own for each mode, the gate declared with a
        hook budget of 2 s: a hook run has a deadline, so a wait takes the smaller of its cap and what is
        left (a cap of 10 s gets under 2 s, a cap of 0.5 s gets 0.5 s) and a git call gets under 2 s, never
        the 3 s of its own cap; a scan, an act and a scope opened with no mode have none, so a wait takes
        its cap and git no clock. An identity declared without a hook budget has the shared 25 s."""
        program = (
            "import json, sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from constitution_layer_kit import identity, repository\n"
            "from constitution_layer_kit.model import Mode\n"
            "mode = {'hook': Mode.HOOK, 'scan': Mode.SCAN, 'act': Mode.ACT, 'none': None}[sys.argv[2]]\n"
            "who = identity.Identity('x', 'y', Path('.'), 'x.yaml', ('module_prefix',), hook_seconds=2)\n"
            "with identity.declared(who, mode):\n"
            "    asked = [identity.remaining(10, 'x'), identity.remaining(0.5, 'x'), repository.budget()]\n"
            "print(json.dumps(asked))\n"
        )
        seen: dict[str, object] = {}
        for mode in ("hook", "scan", "act", "none"):
            done = subprocess.run(
                [sys.executable, "-c", program, str(SHARED), mode],
                capture_output=True,
                text=True,
                check=False,
            )
            seen[mode] = json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip()
        hook = seen["hook"]
        in_a_hook = (
            isinstance(hook, list)
            and 0 < hook[0] <= 2
            and hook[1] == 0.5
            and hook[2] is not None
            and 0 < hook[2] <= 2
        )
        without = all(seen[mode] == [10, 0.5, None] for mode in ("scan", "act", "none"))
        default = identity.Identity("x", "y", Path("."), "x.yaml", KERNEL_KEYS).hook_seconds == 25
        assert in_a_hook and without and default, (
            f"a wait of cap 10 s, of cap 0.5 s, and a git call, by mode: {seen}; the default budget"
            f" {identity.Identity('x', 'y', Path('.'), 'x.yaml', ('module_prefix',)).hook_seconds:g} s"
        )

    def spent_deadline(self) -> None:
        """A wait asked after the deadline is the shared failure C12.14, typed by hand, before the wait
        begins: in a hook scope whose clock is moved 100 s on after its opening (budget 2 s),
        `identity.remaining` and a shared git call both end in it, and no git process was started."""
        program = (
            "import subprocess, sys, time\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from constitution_layer_kit import identity, repository\n"
            "from constitution_layer_kit.errors import ConfigurationFailure\n"
            "from constitution_layer_kit.model import Mode\n"
            "who = identity.Identity('x', 'y', Path('.'), 'x.yaml', ('module_prefix',), hook_seconds=2)\n"
            "real, started = time.monotonic, []\n"
            "asks = [\n"
            "    lambda: identity.remaining(10, 'the prose linter finished'),\n"
            "    lambda: repository.git(['ls-files', '-z'], Path('.')),\n"
            "]\n"
            "with identity.declared(who, Mode.HOOK):\n"
            "    time.monotonic = lambda: real() + 100\n"
            "    subprocess.run = lambda *args, **kwargs: started.append(args)\n"
            "    for ask in asks:\n"
            "        try:\n"
            "            ask()\n"
            "        except ConfigurationFailure as failure:\n"
            "            print(failure.broken.render())\n"
            "print(len(started))\n"
        )
        done = subprocess.run(
            [sys.executable, "-c", program, str(SHARED)], capture_output=True, text=True, check=False
        )
        wanted = [
            self.spent("2", "the prose linter finished"),
            self.spent("2", "git ls-files answered"),
            "0",
        ]
        lines = done.stdout.splitlines()
        assert done.returncode == 0 and lines == wanted, (
            f"exit {done.returncode}: {lines or done.stderr.strip()[-300:]}"
        )

    def deadline_starts_at_the_opening(self) -> None:
        """In hook mode the opening of the scope starts the run's deadline, `hook_seconds` from that moment
        on a clock the program moves by hand: a wait asked 4 s after the opening of a 10 s scope gets 6 s;
        a hook scope opened inside it starts a deadline of its own, 10 s, which ends with it, and the outer
        deadline holds again; a scan scope opened inside has none, a cap unchanged; a hook scope opened
        7 s later, past the outer deadline, gets its own 10 s; outside every scope a wait gets its cap."""
        program = (
            "import json, sys, time\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from constitution_layer_kit import identity\n"
            "from constitution_layer_kit.model import Mode\n"
            "clock = [1000.0]\n"
            "time.monotonic = lambda: clock[0]\n"
            "who = identity.Identity('x', 'y', Path('.'), 'x.yaml', ('module_prefix',), hook_seconds=10)\n"
            "asked = []\n"
            "def ask():\n"
            "    asked.append(identity.remaining(100, 'x'))\n"
            "with identity.declared(who, Mode.HOOK):\n"
            "    clock[0] = 1004.0\n"
            "    ask()\n"
            "    with identity.declared(who, Mode.HOOK):\n"
            "        ask()\n"
            "    with identity.declared(who, Mode.SCAN):\n"
            "        ask()\n"
            "    ask()\n"
            "    clock[0] = 1011.0\n"
            "    with identity.declared(who, Mode.HOOK):\n"
            "        ask()\n"
            "ask()\n"
            "print(json.dumps(asked))\n"
        )
        done = subprocess.run(
            [sys.executable, "-c", program, str(SHARED)], capture_output=True, text=True, check=False
        )
        wanted = [6, 10, 100, 6, 10, 100]  # typed by hand, in the order the program asks
        asked = json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip()[-300:]
        assert asked == wanted, f"exit {done.returncode}: the waits' seconds, wanted {wanted}, got {asked}"

    def git_call_log(self, log: Path) -> list[tuple[float, list[str]]]:
        """Each git call the log holds: the `timeout=` it was given and its arguments."""
        lines = log.read_text().splitlines() if log.exists() else []
        return [(float(line.split(" ", 1)[0]), ast.literal_eval(line.split(" ", 1)[1])) for line in lines]

    def slow_git_within_the_cap(self) -> None:
        """A git that answers every call 0.15 s late on the patch's clock, in a hook with its own 25 s: the
        cap of 3 s binds every call, and no line of the hook's budget is said."""
        env, log = git_patch(self.h, late=0.15)
        result, _ = self.s.gate_on(self.s.valid, env=env)
        timeouts = git_timeouts(log)
        ok = result.code == 0 and bool(timeouts) and set(timeouts) == {repr(repository.GIT_SECONDS)}
        assert ok and "budget" not in result.stderr, (
            f"exit {result.code}, {len(timeouts)} git calls, each late, timeouts {sorted(set(timeouts))}"
        )

    def slow_git_spends_the_deadline(self) -> None:
        """A hook budget of 1 s, lowered for the run by the patch, and a git that answers late on the patch's
        clock, which nothing else moves: each call is given exactly the smaller of the 3 s and what is left —
        1 s, then 1 s less the lateness of each call before it — and the call the deadline meets ends the
        run in C12.14 as the first stderr line, the count line after it, exit 1, the call naming itself. A
        gate that makes three calls or more meets it at the third (each 0.375 s late: given 1, 0.625 and
        0.25 s), one that makes two at the second (0.625 s late), one that makes one at its first (1.5 s
        late). The numbers are exact in binary, so no rounding moves the cut. The run is bounded at the hang
        cases' 20 s, and no assertion is made on its time."""
        calibrate, counted = git_patch(self.h)
        self.s.gate_on(self.s.valid, env=calibrate)
        calls = len(git_timeouts(counted))
        lowered, meets = 1.0, min(calls, 3)
        late = {1: 1.5, 2: 0.625}.get(meets, 0.375)
        env, log = git_patch(self.h, hook_seconds=lowered, late=late)
        with self.h.bounded(HANG_BOUND):
            result, _ = self.s.gate_on(self.s.valid, env=env)
        made = self.git_call_log(log)
        timeouts = [timeout for timeout, _ in made]
        given = [min(repository.GIT_SECONDS, lowered - late * call) for call in range(meets)]
        sub = repository.subcommand(made[-1][1]) if made else "none"
        self.broken_as_typed(result, self.spent("1", f"git {sub} answered"))
        assert calls > 0 and timeouts == given, (
            f"{len(made)} git calls (the run makes {calls}), timeouts {timeouts}, wanted {given}:"
            f" {result.stderr.strip()[:300]}"
        )

    def unreadable(self, path: Path, run: Callable[[], Result], line: str) -> None:
        """`run` with `path` made unreadable, its mode restored whatever happens: the runner's cleanup
        must be able to remove it."""
        mode = path.stat().st_mode
        path.chmod(0o000)
        try:
            result = run()
        finally:
            path.chmod(mode)
        self.broken_as_typed(result, line)

    def shared_texts_escape_or_cut(self) -> None:
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
            "C16": messages.c16_shared_too_old(self.ns, "1.0.1", "1.0.0", path, VERSION_UNTIL),
            "C17": messages.c17_module_too_old(self.ns, "1.4.2", "2.0.0", path, VERSION_UNTIL),
        }
        wanted = {
            "C4 detail whole": f"BROKEN: {self.file} is not valid YAML (at {'w' * 100}\\\\x) — fix: "
            "repair the YAML at the place the message names; nothing is checked until the file parses",
            "C5.3 dialect": f"BROKEN: {self.file}: territory_dialect 'd\\n" + "e" * 78 + "… [102 characters]'"
            f" is not supported by {self.ns} (supports: gitignore) — fix: set territory_dialect:"
            " gitignore, or remove the key",
            "C5.4 key": f"BROKEN: {self.file}: namespace 'a\\nb' must be a mapping — fix: write it as"
            " a\\nb: {territory: [...]}",
            "C5.6 key": f"BROKEN: {self.file}: {cut}.territory must be a list of non-empty strings"
            f' — fix: write it as {cut}: {{territory: ["<pattern>", ...]}}',
            "C5.7 where": f"BROKEN: {self.file}: {'k' * 80}… [100 characters] holds a pattern git would"
            " not read as one: '#x' — fix: a pattern may not start with '#' (a comment to git) nor contain a"
            " line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes,"
            " and remove a line break",
            "C6": f"BROKEN: {self.file} names root_policy '{esc}' but no such file exists — fix: create"
            " it, or point root_policy at the policy for policies",
            "C7": f"BROKEN: root policy '{esc}' carries no readable id in its envelope — fix: give it the"
            " envelope (id, type, title, status); its id names its namespace",
            "C8": f"BROKEN: root policy '{esc}' claims no territory in {self.file} — fix: write {esc}:"
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
            f" gitignore syntax; check {self.file}",
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
            "C13": f"BROKEN: {self.file}: {self.ns}.log_dir '{esc}' is not ignored by git — fix: a log"
            " inside the working tree must be git-ignored, or every verdict dirties the tree; add the"
            " directory to .gitignore, or remove the key",
            "C16": f"BROKEN: {self.ns} needs constitution-layer-kit 1.0.1 or a later 1.x release, found 1.0.0"
            f" — fix: install one for python3 as {esc} says — until then Markdown writes pass unchecked",
            "C17": f"BROKEN: {self.ns} was written for constitution-layer-kit 1.4.2, a 1.x release, found"
            " 2.0.0 — fix: update the plugin to a release written for 2.x, or install a 1.x release of"
            f" constitution-layer-kit for python3 as {esc} says — until then Markdown writes pass unchecked",
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
                messages.g1_skip_other_tool("T\n" + "t" * 100),
                "tool 'T\\n"
                + "t" * 78
                + "… [102 characters]' is not one this gate judges (it judges Write and Edit)",
            ),
            (
                "G1.1 for an event that names no tool",
                messages.g1_skip_other_tool(""),
                "an event that names no tool is not one this gate judges (it judges Write and Edit)",
            ),
            ("G1.2", messages.g1_skip_not_markdown(path), f"{esc} is not a .md file"),
            (
                "G1.3",
                messages.g1_skip_no_repo(path),
                f"{esc} is not inside a git repository; the constitution is silent there",
            ),
            ("G1.4", messages.g1_skip_no_dials(path), f"no {self.file} in {esc}: nothing is claimed"),
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
        assert not wrong, wrong[0][:600]

    def delimiter_failures_in_writes(self, head: str, body: str) -> list[str]:
        """What the gate does with a write whose delimiters vary: the envelope stays whole in the first
        cases, a form feed before the only closer leaves it open."""
        # an envelope that stays whole in every case: the opener, the closer and the line endings vary
        green = {
            "the opener `--- `": "--- \n" + self.s.valid.text[4:],
            "the closer `--- `": head + "\n--- \n" + body,
            "the closer `---` and a tab": head + "\n---\t\n" + body,
            "CRLF throughout": self.s.valid.text.replace("\n", "\r\n"),
        }
        failed = []
        for what, text in green.items():
            result, _ = self.s.gate_on(Write(self.s.valid.target, text))
            try:
                expect(result, 0, self.s.green, "stdout", label=what)
            except AssertionError as error:  # gathered: one case's red hides no other
                failed.append(str(error)[:300])
        # a form feed before the only closer is no delimiter: the envelope never closes, whatever the
        # reader's `splitlines()` would say
        unclosed = head + "\n\x0c---\n" + body
        result, _ = self.s.gate_on(Write(self.s.valid.target, unclosed))
        if result.code != self.red_code or self.s.green in result.stdout:
            failed.append(f"a form feed before the closer was not blocked: exit {result.code}")
        return failed


# Each item carries its number, so it keeps that number in every module and when the tests are
# reordered; a gate that resolves no policy skips the items about policies, their numbers kept. A new
# item takes the next number after the last, and a removed item leaves its number free: a number
# is never reissued (the handles rule of the shared-code page). The tests below stand in number order;
# the numbers are held unique by acceptance.collected, and rising by a check of the kit that ships them.
about_policies = {
    "root_missing",
    "root_without_id",
    "root_claims_nothing",
    "root_outside_own_territory",
    "no_root_policy",
    "policy_without_id_note",
    "policy_unreadable",
}
# A generator has no event, no verdict and no scan: these items are a gate's alone.
about_events = {
    "unparseable_input",
    "input_not_an_object",
    "malformed_event",
    "edit_without_fields",
    "other_tool",
    "scan_missing_path",
    "scan_outside_repository",
    "scan_forms",
    "not_markdown",
    "relative_path",
    "outside_any_repository",
    "no_dials_file",
    "no_root_policy",
    "edit_unappliable",
    "edit_empty_old_string",
    "severity_warn",
    "stdout_cannot_encode",
    "deeply_nested_envelope",
    "envelope_delimiters",
    "byte_order_mark",
    "negated_pattern",
    "document_unreadable",
    "file_named_md",
}
# A gate wired to Stop examines a repository, never a written file: these items are a tool gate's.
about_files = {
    "other_tool",
    "not_markdown",
    "relative_path",
    "edit_unappliable",
    "edit_empty_old_string",
    "byte_order_mark",
    "negated_pattern",
    "deeply_nested_envelope",
    "envelope_delimiters",
    "file_named_md",
}
# A gate wired to Stop never reaches git's file list, the territory's scratch repository or its
# check-ignore, nor reads a document the scan lists: these items are a tool gate's.
about_listing = {"ls_files_fails", "init_fails", "check_ignore_fails", "document_unreadable"}
# A gate without a hook mode never reads hook input, a written file or the warn channel, and
# takes a file out of its territory with a count, not a skip: these items are a hook gate's.
about_hooks = {
    "unparseable_input",
    "input_not_an_object",
    "malformed_event",
    "edit_without_fields",
    "other_tool",
    "not_markdown",
    "relative_path",
    "outside_any_repository",
    "edit_unappliable",
    "edit_empty_old_string",
    "severity_warn",
    "negated_pattern",
    "file_named_md",
}


def shared(subject: Subject, name: str) -> SharedItems:
    """The items of `subject` for the shared test `name`; skipped, its number kept free, where the
    module's Subject leaves the item out — the reason naming the flag."""
    it = SharedItems(subject)
    for leaves_out, reason in (
        (not subject.resolves_policies and name in about_policies, "Subject.resolves_policies is False"),
        (
            not subject.judges_envelopes and name in ("deeply_nested_envelope", "envelope_delimiters"),
            "Subject.judges_envelopes is False",
        ),
        (not subject.event_driven and name in about_events, "Subject.event_driven is False"),
        (it.no_file and name in about_files, f"Subject.event is {subject.event}"),
        (it.no_file and name in about_listing, f"Subject.event is {subject.event}"),
        (subject.scan_only and name in about_hooks, "Subject.scan_only is True"),
        (subject.long_value is None and name == "long_value_is_cut", "Subject.long_value is None"),
        (
            subject.pattern_dial is None and name == "pattern_in_own_dial_is_one_line",
            "Subject.pattern_dial is None",
        ),
        (subject.noted is None and name == "notes_reach_the_model", "Subject.noted is None"),
        (subject.skill == "" and name == "skill_named_after_red", "Subject.skill is empty"),
    ):
        if leaves_out:
            pytest.skip(f"not this gate's: {reason}")
    return it


@item(101, "exit-code split: a malformed dials file exits 1, never 2, never 0")
def test_malformed_dials(subject: Subject) -> None:
    it = shared(subject, "malformed_dials")
    result, _ = it.s.gate_on(it.s.valid, raw_dials="root-policy: [\n")
    expect(result, 1, f"BROKEN: {it.file} is not valid YAML", "stderr")


@item(102, "C4b: a dials file that is not a mapping")
def test_dials_not_mapping(subject: Subject) -> None:
    it = shared(subject, "dials_not_mapping")
    result, _ = it.s.gate_on(it.s.valid, raw_dials="- a\n- b\n")
    line = (  # typed by hand: the three kernel keys, the dialect said to be needed only off the default
        "BROKEN: constitution.yaml is not a mapping — fix: the file holds top-level keys: module_prefix,"
        " root_policy, and territory_dialect when the dialect is not gitignore, then one namespace per"
        " policy or module"
    )
    if it.layered:  # another layer's file: the identity's own kernel keys, and no policy in it
        line = (
            f"BROKEN: {it.file} is not a mapping — fix: the file holds top-level keys:"
            f" {', '.join(it.kernel_keys)}, then one namespace per module"
        )
    it.broken_as_typed(result, line)


@item(103, "C5: a severity outside block | warn")
def test_dials_bad_severity(subject: Subject) -> None:
    it = shared(subject, "dials_bad_severity")
    line = (  # typed by hand
        f"BROKEN: {it.file}: {it.ns}.severity must be block or warn — fix: under {it.ns},"
        " set severity: block or severity: warn, or remove that line"
    )
    it.broken_as_typed(it.s.gate_on(it.s.valid, dials_patch=it.s.own(severity="loud"))[0], line)


@item(104, "C5: the module's own namespace must be a mapping")
def test_dials_own_namespace(subject: Subject) -> None:
    it = shared(subject, "dials_own_namespace")
    line = (  # typed by hand
        f"BROKEN: {it.file}: namespace '{it.ns}' must be a mapping of this module's dials —"
        " fix: write this module's dials under it as a mapping, or remove the key"
    )
    it.broken_as_typed(it.s.gate_on(it.s.valid, dials_patch={it.ns: "x"})[0], line)


@item(105, "C5: a territory pattern git would read as a comment")
def test_dials_comment_pattern(subject: Subject) -> None:
    it = shared(subject, "dials_comment_pattern")
    result, _ = it.s.gate_on(it.s.valid, dials_patch={"notes-policy": {"territory": ["#docs/notes/**"]}})
    line = (  # typed by hand: the dial's whole path, then the pattern in single quotes
        "BROKEN: constitution.yaml: notes-policy.territory holds a pattern git would not read as one:"
        " '#docs/notes/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a line"
        " break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break"
    )
    it.broken_as_typed(result, line)


@item(106, "C5: an unsupported territory dialect")
def test_dials_unsupported_dialect(subject: Subject) -> None:
    it = shared(subject, "dials_unsupported_dialect")
    result, _ = it.s.gate_on(it.s.valid, dials_patch={"territory_dialect": "regex"})
    it.broken(result, it.of_constitution(lambda: messages.c5_dialect_unsupported("regex")))


@item(107, "C6: the root policy file is missing")
def test_root_missing(subject: Subject) -> None:
    it = shared(subject, "root_missing")
    it.broken(
        it.s.gate_on(it.s.valid, remove=ROOT_POLICY)[0],
        it.of_constitution(lambda: messages.c6_root_missing(ROOT_POLICY)),
    )


@item(108, "C7: the root policy on disk has no readable id")
def test_root_without_id(subject: Subject) -> None:
    it = shared(subject, "root_without_id")
    result, _ = it.s.gate_on(it.s.valid, files={ROOT_POLICY: NO_ENVELOPE})
    it.broken(result, it.of_constitution(lambda: messages.c7_root_without_id(ROOT_POLICY)))


@item(109, "C8: the root policy claims no territory")
def test_root_claims_nothing(subject: Subject) -> None:
    it = shared(subject, "root_claims_nothing")
    result, _ = it.s.gate_on(it.s.valid, dials_patch={"root-policy": {}})
    it.broken(result, it.of_constitution(lambda: messages.c8_root_claims_nothing("root-policy")))


@item(110, "C9: the root policy lies outside its own territory")
def test_root_outside_own_territory(subject: Subject) -> None:
    it = shared(subject, "root_outside_own_territory")
    result, _ = it.s.gate_on(it.s.valid, dials_patch={"root-policy": {"territory": ["docs/elsewhere/**"]}})
    it.broken(
        result,
        it.of_constitution(
            lambda: messages.c9_root_outside_own_territory(ROOT_POLICY, ["docs/elsewhere/**"], "root-policy")
        ),
    )


@item(111, "absence: python3")
def test_python_absent(subject: Subject) -> None:
    it = shared(subject, "python_absent")
    result, _ = it.s.gate_on(it.s.valid, env={"PATH": it.bin_with("dirname")})
    expect(result, 1, f"BROKEN: {it.ns} needs python3", "stderr")


@item(112, "absence: an interpreter below the floor")
def test_python_below_floor(subject: Subject) -> None:
    """The entry file run, under the interpreter at hand, as one a minor below the floor would run it:
    a shim sets `sys.version_info` to that minor, puts the entry's folder first on the path as a real
    run does, and runs the entry as `__main__`. The line is C14's, up to its clause."""
    it = shared(subject, "python_below_floor")
    floor, below = preflight.FLOOR, (preflight.FLOOR[0], preflight.FLOOR[1] - 1)
    line = (
        f"BROKEN: {it.ns} needs Python {floor[0]}.{floor[1]} or newer, found {below[0]}.{below[1]}"
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
    result = it.h.run_gate(
        "{}", command=[sys.executable, "-c", shim, str(it.h.entry), f"{below[0]}.{below[1]}"]
    )
    first = result.stderr.splitlines()[0] if result.stderr else ""
    ok = result.code == 1 and (first == line or first.startswith(line + " — "))
    if ok:
        return
    pytest.fail(
        f"wanted exit 1 under a faked Python {below[0]}.{below[1]} with first stderr line {line!r},"
        f" at its end or followed by ' — ' and a clause; got exit {result.code}, first stderr line"
        f" {first!r}, stderr ends {result.stderr.strip()[-200:]!r},"
        f" stdout {result.stdout.strip()[:200]!r}"
    )


@item(113, "absence: git")
def test_git_absent(subject: Subject) -> None:
    it = shared(subject, "git_absent")
    result, _ = it.s.gate_on(it.s.valid, env={"PATH": it.bin_with("python3", "dirname")})
    it.broken(result, messages.c3_git_missing())


@item(114, "absence: a declared library (PyYAML)")
def test_library_absent(subject: Subject) -> None:
    it = shared(subject, "library_absent")
    shadow = it.h.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    result, _ = it.s.gate_on(it.s.valid, env={"PYTHONPATH": str(shadow)})
    it.broken(result, messages.c2_library_missing("PyYAML", str(preflight.requirements_file())))


@item(115, "absence: the shared code, the Python package that python3 cannot import")
def test_shared_code_absent(subject: Subject) -> None:
    """The package missing for python3 in four ways, each the entry file's `C15`, typed by hand, then the
    closing line: a folder first on PYTHONPATH whose package fails to import; the harness's own shared
    folder left out with nothing else importable (`-S`, so that no release installed for the developer's
    python3 is found); an empty folder of the package's name as the one candidate; and the plugin in a folder
    whose name holds a backslash, a line feed and a carriage return, whose path the line shows escaped on
    one line. The note the line sends to exists."""
    it = shared(subject, "shared_code_absent")
    stdin = it.payload(it.h.fresh_consumer().root, it.s.valid)
    assert it.guide().is_file(), f"the line sends to {it.guide()}, which is no file"
    wanted = it.package_missing(it.guide())
    failing = it.h.scratch_dir()
    (failing / PACKAGE).mkdir()
    (failing / PACKAGE / "__init__.py").write_text(
        "raise ImportError('simulated absence')\n", encoding="utf-8"
    )
    it.broken_as_typed(
        it.h.run_gate(stdin, env={"PYTHONPATH": str(failing)}), wanted, "a package that fails to import"
    )
    alone = [sys.executable, "-S", str(it.h.entry)]
    nothing = {"PYTHONPATH": ""}
    it.broken_as_typed(
        it.h.run_gate(stdin, env=nothing, command=alone, shared=False), wanted, "the shared folder left out"
    )
    empty = it.h.scratch_dir()
    (empty / PACKAGE).mkdir()
    it.broken_as_typed(
        it.h.run_gate(stdin, env={"PYTHONPATH": str(empty)}, command=alone, shared=False),
        wanted,
        "an empty folder of the package's name",
    )
    odd = it.h.scratch_dir() / "a\\b\nc\rd"
    (odd / "scripts").mkdir(parents=True)
    shutil.copy(it.h.entry, odd / "scripts" / it.h.entry.name)
    result = it.h.run_gate(
        stdin,
        env=nothing,
        command=[sys.executable, "-S", str(odd / "scripts" / it.h.entry.name)],
        shared=False,
    )
    it.broken_as_typed(result, it.package_missing(odd / "INSTALL.md"), "a plugin folder with line breaks")


@item(116, "a failing git is a configuration failure, never a green skip")
def test_git_failing(subject: Subject) -> None:
    """A git that fails for any reason other than "not a repository" is never a green skip."""
    it = shared(subject, "git_failing")
    config = it.h.scratch_dir() / "gitconfig"
    config.write_text("[broken\n", encoding="utf-8")
    result, _ = it.s.gate_on(it.s.valid, env={"GIT_CONFIG_GLOBAL": str(config)})
    expect(result, 1, "BROKEN: git could not answer where the repository is", "stderr")


@item(117, "misinvocation exits 1: argparse's exit 2 is overridden")
def test_misinvocation(subject: Subject) -> None:
    it = shared(subject, "misinvocation")
    expect(it.h.run_gate("", args=["--bogus"]), 1, "BROKEN: misinvocation:", "stderr")


@item(118, "--help is a misinvocation like any other: no exit path past the guard and the log")
def test_help_is_not_special(subject: Subject) -> None:
    it = shared(subject, "help_is_not_special")
    expect(it.h.run_gate("", args=["--help"]), 1, "BROKEN: misinvocation:", "stderr")


@item(119, "an abbreviated flag is a misinvocation, not a scan logged as a hook run")
def test_abbreviated_flag(subject: Subject) -> None:
    it = shared(subject, "abbreviated_flag")
    expect(it.h.run_gate("", args=["--sc", "."]), 1, "BROKEN: misinvocation:", "stderr")


@item(120, "unparseable hook input is a configuration failure, not an empty event")
def test_unparseable_input(subject: Subject) -> None:
    it = shared(subject, "unparseable_input")
    expect(it.h.run_gate("not json"), 1, "BROKEN: hook input cannot be used (it is not JSON", "stderr")


@item(121, "hook input that is JSON but no object says so")
def test_input_not_an_object(subject: Subject) -> None:
    it = shared(subject, "input_not_an_object")
    detail = "it is JSON, but the top level is not an object"  # typed by hand
    it.broken(it.h.run_gate("[1, 2]"), messages.c12_input(detail))


@item(122, "a Write event without its documented fields is a configuration failure")
def test_malformed_event(subject: Subject) -> None:
    it = shared(subject, "malformed_event")
    event = json.dumps({"tool_name": "Write", "tool_input": ["not", "an", "object"]})
    it.broken(it.h.run_gate(event), messages.c12_input(messages.detail_tool_input("Write", "file_path")))


@item(123, "an event for a tool the gates do not judge is a visible skip")
def test_other_tool(subject: Subject) -> None:
    """`MultiEdit` carries a `file_path`, and is still no tool this gate judges: the visible skip says so,
    and names the tools it does judge. The whole line is typed by hand."""
    it = shared(subject, "other_tool")
    event = json.dumps({"tool_name": "MultiEdit", "tool_input": {"file_path": "x.md"}})
    skip = (
        f"GREEN: {it.ns}: 0 documents examined — tool 'MultiEdit' is not one this gate judges"
        " (it judges Write and Edit)"
    )
    expect(it.h.run_gate(event), 0, skip, "stdout")


@item(124, "--scan on a path that does not exist is a configuration failure")
def test_scan_missing_path(subject: Subject) -> None:
    it = shared(subject, "scan_missing_path")
    result = it.h.run_gate("", args=["--scan", "no-such-directory"])
    it.broken(result, messages.c12_scan_path("no-such-directory"))


@item(125, "examined count: a non-Markdown file prints 0 and exits 0")
def test_not_markdown(subject: Subject) -> None:
    """Markdown means `.md`: a `.markdown` file is skipped, and the reason names the ending, not
    the format, since the file may well be Markdown."""
    it = shared(subject, "not_markdown")
    target = str(Path(it.s.valid.target).with_suffix(".markdown"))
    result, root = it.s.gate_on(Write(target, "x"))
    skip = messages.g1_green_skip(messages.g1_skip_not_markdown(str(root / target)))
    expect(result, 0, skip, "stdout")
    # a path of over 80 characters with a line break in it: shown whole, the break escaped — typed
    # by hand, since the reader opens that path and the line is read by a later step
    name = "docs/" + "d" * 90 + "\nx.markdown"
    long_result, long_root = it.s.gate_on(Write(name, "x"))
    line = (
        f"GREEN: {it.ns}: 0 documents examined — {long_root}/docs/"
        + "d" * 90
        + "\\nx.markdown is not a .md file"
    )
    expect(long_result, 0, line, "stdout")


@item(126, "a relative file_path is resolved against the event's cwd")
def test_relative_path(subject: Subject) -> None:
    """A relative file_path is resolved against the event's cwd."""
    it = shared(subject, "relative_path")
    _, root = it.s.gate_on(it.s.valid)  # prepares the consumer; the event below is the one judged
    event = json.loads(event_json(root, it.s.red))
    event["tool_input"]["file_path"] = it.s.red.target
    expect(it.h.run_gate(json.dumps(event)), 2, it.s.red_finding.render(), "stderr")


@item(127, "a file outside any git repository is a visible skip")
def test_outside_any_repository(subject: Subject) -> None:
    it = shared(subject, "outside_any_repository")
    directory = it.h.scratch_dir()
    event = it.payload(directory, Write("loose.md", NO_ENVELOPE))
    result = it.h.run_gate(event, env={"GIT_CEILING_DIRECTORIES": str(directory.parent)})
    where = directory if it.no_file else directory / "loose.md"  # no file named: its cwd is the place
    skip = messages.g1_green_skip(messages.g1_skip_no_repo(str(where)))
    expect(result, 0, skip, "stdout")
    if it.no_file:
        return
    # the written file's path with a line break in it and over 80 characters: whole, escaped
    name = "a\n" + "b" * 90 + ".md"
    long_event = it.payload(directory, Write(name, NO_ENVELOPE))
    long_result = it.h.run_gate(long_event, env={"GIT_CEILING_DIRECTORIES": str(directory.parent)})
    line = (
        f"GREEN: {it.ns}: 0 documents examined — {directory}/a\\n" + "b" * 90 + ".md is not inside a git"
        " repository; the constitution is silent there"
    )
    expect(long_result, 0, line, "stdout")


@item(128, "no dials file: a visible skip")
def test_no_dials_file(subject: Subject) -> None:
    it = shared(subject, "no_dials_file")
    consumer = it.h.fresh_consumer()
    (consumer.root / it.file).unlink()  # the gate's own file: a gate of another layer's leaves the other
    if it.s.scan_only:
        consumer.write(it.s.red.target, it.s.red.text)
        result = it.h.run_gate("", args=it.scan_args(consumer.root))
    else:
        result = it.h.run_gate(it.payload(consumer.root, it.s.red))
    skip = messages.g1_green_skip(messages.g1_skip_no_dials(str(consumer.root)))
    expect(result, 0, skip, "stdout")


@item(129, "a dials file with no root_policy: a visible skip")
def test_no_root_policy(subject: Subject) -> None:
    it = shared(subject, "no_root_policy")
    raw = f"module_prefix: {it.constitution_prefix}\nnotes-policy:\n  territory: ['docs/notes/**']\n"
    if it.layered:  # the constitution's file, beside the gate's own, which holds no root_policy anyway
        result, _ = it.s.gate_on(it.s.red, files={CONSTITUTION_FILE: raw})
    else:
        result, _ = it.s.gate_on(it.s.red, raw_dials=raw)
    reason = "constitution.yaml has no root_policy: nothing is claimed"  # typed by hand
    expect(result, 0, messages.g1_green_skip(reason), "stdout")


@item(130, "an Edit whose old_string is absent is a visible skip; the tool reports it")
def test_edit_unappliable(subject: Subject) -> None:
    it = shared(subject, "edit_unappliable")
    action = Edit(it.s.valid.target, "no such text anywhere", "x")
    result, _ = it.s.gate_on(action, files={it.s.valid.target: it.s.valid.text})
    skip = messages.g1_green_skip(messages.g1_skip_edit_unappliable(it.s.valid.target))
    expect(result, 0, skip, "stdout")


@item(131, "severity warn: exit 0 with the whole finding as JSON for the model and the user")
def test_severity_warn(subject: Subject) -> None:
    it = shared(subject, "severity_warn")
    result, _ = it.s.gate_on(it.s.red, dials_patch=it.s.own(severity="warn"))
    if result.code != 0:
        pytest.fail(f"warn must let the write through; exit {result.code}: {result.stderr}")
    answer = json.loads(result.stdout)
    if it.stop:  # the user's notice alone: context handed to the model at a turn's end continues it
        ok = (
            set(answer) == {"systemMessage"}
            and it.s.red_finding.render() in answer["systemMessage"]
            and answer["systemMessage"].startswith(f"{it.ns} (warn):\n")  # typed by hand
        )
        assert ok, f"bad: {answer}"
        return
    context = answer["hookSpecificOutput"]["additionalContext"]
    ok = (
        it.s.red_finding.render() in context
        and f"{it.ns}: severity is warn: the write proceeds, but the finding stands and recurs on every"
        " write until fixed"
        in context  # typed by hand, as the system line below
        and answer["systemMessage"] == f"{it.ns} (warn): {it.s.red_finding.headline}"
    )
    assert ok, f"bad: {answer}"


@item(132, "output log: each print is one record, in the plugin data directory")
def test_log_in_plugin_data(subject: Subject) -> None:
    it = shared(subject, "log_in_plugin_data")
    data = it.h.scratch_dir()
    result, root = it.s.gate_on(it.s.red, env={"CLAUDE_PLUGIN_DATA": str(data)})
    lines = it.log_lines(data / log_name())
    line = lines[0]
    first = ("RED: " if it.s.event_driven else "BROKEN: ") + it.s.red_finding.headline
    said = {
        stream: [each["text"] for each in lines if each["stream"] == stream]
        for stream in ("stdout", "stderr")
    }
    # an asking gate prints its verdict as one JSON object on stdout, the finding inside it; a scan
    # prints its finding and its count line on stdout, one record each
    verdict_stream = "stdout" if (it.s.ask or it.s.scan_only) else "stderr"
    records = (3 if it.s.skill else 2) if it.s.scan_only else 1  # a scan prints F10 as a record of its own
    hooked = it.s.event_driven and not it.s.scan_only
    examined = it.s.red.text if it.shell else str(root / it.s.red.target)
    ok = (
        set(line) == {"ts", "module", "gate", "mode", "session", "path", "transcript", "stream", "text"}
        and (first in line["text"] if it.s.ask else line["text"].startswith(first))
        and line["module"] == it.ns
        and line["stream"] == verdict_stream
        and line["session"] == ("fixture-session" if hooked else "")
        # the event's own names: the transcript, and the file or the shell command the gate examines,
        # which a Stop and a scan do not name
        and line["transcript"] == (TRANSCRIPT if hooked else "")
        and line["path"] == (examined if hooked and not it.stop else "")
        # one record per print: the records rebuild both streams exactly, and a block verdict,
        # printed at once, is one record of several lines
        and "".join(text + "\n" for text in said["stdout"]) == result.stdout
        and "".join(text + "\n" for text in said["stderr"]) == result.stderr
        and (
            not it.s.event_driven
            or (len(said[verdict_stream]) == records and (it.s.ask or "\n" in line["text"]))
        )
    )
    assert ok, f"{len(lines)} log lines; first: {line}"


@item(133, "output log: the log_dir dial routes the whole run to a git-ignored directory")
def test_log_in_ignored_dir(subject: Subject) -> None:
    it = shared(subject, "log_in_ignored_dir")
    data = it.h.scratch_dir()
    result, root = it.s.gate_on(
        it.s.valid,
        files={".gitignore": ".gate-logs/\n"},
        env={"CLAUDE_PLUGIN_DATA": str(data)},
        dials_patch=it.s.own(log_dir="./docs//../.gate-logs//"),  # read as `.gate-logs`
    )
    log = root / ".gate-logs" / log_name()
    ok = (
        result.code == 0
        and log.is_file()
        and it.s.green in it.log_lines(log)[-1]["text"]
        and not (data / log_name()).exists()
    )
    assert ok, f"exit {result.code}; the whole run logged inside the repository, nothing split off"


@item(134, "output log: a log_dir that git does not ignore is a configuration failure")
def test_log_dir_not_ignored(subject: Subject) -> None:
    it = shared(subject, "log_dir_not_ignored")
    result, _ = it.s.gate_on(it.s.valid, dials_patch=it.s.own(log_dir="gate-logs"))
    it.broken(result, messages.c13_log_dir_not_ignored("gate-logs"))


@item(135, "output log: rotation past the size limit")
def test_log_rotates(subject: Subject) -> None:
    it = shared(subject, "log_rotates")
    data = it.h.scratch_dir()
    (data / log_name()).write_text("x" * (ROTATE_AT + 1), encoding="utf-8")
    it.s.gate_on(it.s.valid, env={"CLAUDE_PLUGIN_DATA": str(data)})
    kept = (data / (log_name() + ".1")).stat().st_size > ROTATE_AT
    started = it.log_lines(data / log_name())  # only this run's lines: a gate's one, a generator's few
    assert kept and bool(started) and all(line["module"] == it.ns for line in started), (
        "the old log kept as .1, a new one started"
    )


@item(136, "output log: a logging failure never changes the verdict")
def test_log_failure_keeps_verdict(subject: Subject) -> None:
    it = shared(subject, "log_failure_keeps_verdict")
    blocker = it.h.scratch_dir() / "a-file-not-a-directory"
    blocker.write_text("", encoding="utf-8")
    red, _ = it.s.gate_on(it.s.red, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
    green, _ = it.s.gate_on(it.s.valid, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
    refused = it.red_code if it.s.event_driven else 1  # a gate's finding; a generator's refusal
    ok = red.code == refused and green.code == 0 and (not it.s.ask or ask_reason(red) is not None)
    assert ok, f"log location unwritable: red still exits {red.code}, green still exits {green.code}"


@item(137, "declared dependencies: requirements.txt equals the preflight table")
def test_declared_libraries(subject: Subject) -> None:
    shared(subject, "declared_libraries")
    declared = {
        line.split(">=")[0].split("==")[0].strip()
        for line in preflight.requirements_file().read_text().splitlines()
        if line.strip()
    }
    ok = declared == set(preflight.declared())
    assert ok, f"requirements.txt {sorted(declared)} == preflight table {sorted(preflight.declared())}"


@item(138, "C5: the module's own namespace given as null")
def test_dials_own_namespace_null(subject: Subject) -> None:
    it = shared(subject, "dials_own_namespace_null")
    it.broken(
        it.s.gate_on(it.s.valid, dials_patch={it.ns: None})[0],
        messages.c5_own_namespace_not_mapping(),
    )


@item(
    139,
    "C5: root_policy, an empty dialect, a namespace and a territory of the wrong shape, log_dir;"
    " the dials written the long way, and the dialect written out, read as plain",
)
def test_dials_other_pairs(subject: Subject) -> None:
    it = shared(subject, "dials_other_pairs")
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
        (
            {"notes-policy": "docs/notes/**"},
            it.of_constitution(lambda: messages.c5_namespace_not_mapping("notes-policy")),
        ),
        (
            {"notes-policy": {"territory": "docs/notes/**"}},
            it.of_constitution(lambda: messages.c5_territory_shape("notes-policy")),
        ),
        # a list holding a blank string is no list of non-empty strings
        (
            {"notes-policy": {"territory": ["docs/notes/**", " "]}},
            it.of_constitution(lambda: messages.c5_territory_shape("notes-policy")),
        ),
        (
            it.s.own(log_dir="/absolute/logs"),
            f"BROKEN: {it.file}: {it.ns}.log_dir must be a repository-relative directory — fix:"
            f" under {it.ns}, set log_dir: <a git-ignored directory>, or remove that line",
        ),
        # a path that leaves the repository by `..`, written plain or after a step down
        ({"root_policy": "../root.md"}, it.of_constitution(messages.c5_root_policy_path)),
        ({"root_policy": "docs/../../root.md"}, it.of_constitution(messages.c5_root_policy_path)),
        (it.s.own(log_dir="../logs"), messages.c5_log_dir()),
        (it.s.own(log_dir="logs/../../logs"), messages.c5_log_dir()),
        ({"root_policy": " "}, it.of_constitution(messages.c5_root_policy_path)),
    ]
    failed: list[str] = []
    for patch, failure in pairs:
        try:  # gathered: one pair's red hides no other
            if isinstance(failure, str):
                it.broken_as_typed(it.s.gate_on(it.s.valid, dials_patch=patch)[0], failure)
            else:
                it.broken(it.s.gate_on(it.s.valid, dials_patch=patch)[0], failure)
        except AssertionError as error:
            failed.append(str(error))
    # the same dials written the long way read as written the short way: the verdict is the plain
    # run's, never a refusal — `./` and `//` dropped, a step down and back up undone
    plain = it.s.gate_on(it.s.valid)[0]
    long_way: list[tuple[str, dict[str, object]]] = [
        ("root_policy", {"root_policy": "./docs//../" + ROOT_POLICY}),
        # the kernel's one dialect, written out: a kernel-owned key, never refused as a namespace
        ("territory_dialect", {"territory_dialect": DIALECT}),
    ]
    for name, patch in long_way:
        got = it.s.gate_on(it.s.valid, dials_patch=patch)[0]
        if (got.code, "BROKEN" in got.stderr) != (plain.code, "BROKEN" in plain.stderr):
            failed.append(f"{name}: exit {got.code}, the plain run exit {plain.code}: {got.stderr[:200]}")
    assert not failed, "; ".join(failed) or (
        f"{len(pairs)} dial failures, each exit 1 with its own line; the long way reads as plain"
    )


@item(140, "absence, the other way round: the scripts copied with links followed run")
def test_copy_with_links_followed(subject: Subject) -> None:
    """The plugin's scripts copied the way an install copies them: what the link points at."""
    it = shared(subject, "copy_with_links_followed")
    plugin = it.h.scratch_dir() / "plugin"
    shutil.copytree(it.h.scripts, plugin / "scripts", symlinks=False)
    shutil.copy(preflight.requirements_file(), plugin / "requirements.txt")
    result, green = it.valid_run(command=[it.h.sh, str(plugin / "scripts" / it.h.wrapper.name)])
    expect(result, 0, green, "stdout")


@item(141, "not fail-open: an unexpected exception exits 1, BROKEN first, the traceback after")
def test_unexpected_failure(subject: Subject) -> None:
    """Not fail-open: an exception nobody planned for exits 1, its BROKEN line first, the
    traceback after it."""
    it = shared(subject, "unexpected_failure")
    shadow = it.h.scratch_dir()
    (shadow / "yaml.py").write_text(
        "class YAMLError(Exception): pass\n\n\ndef safe_load(text): raise RuntimeError('simulated defect')\n",
        encoding="utf-8",
    )
    result, _ = it.s.gate_on(it.s.valid, env={"PYTHONPATH": str(shadow)})
    failure = messages.c12_unexpected("RuntimeError: simulated defect")
    it.broken(result, failure)
    assert "Traceback (most recent call last)" in result.stderr, result.stderr.strip()[:600]


@item(142, "an Edit event without its documented fields is a configuration failure")
def test_edit_without_fields(subject: Subject) -> None:
    it = shared(subject, "edit_without_fields")
    event = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "/x/a.md", "old_string": "a"}})
    it.broken(it.h.run_gate(event), messages.c12_input(messages.detail_tool_input("Edit", "new_string")))


@item(143, "a stdout that cannot encode the dash still carries the count line")
def test_stdout_cannot_encode(subject: Subject) -> None:
    """The count line carries a dash; a stream that cannot encode it must not swallow the line."""
    it = shared(subject, "stdout_cannot_encode")
    if it.no_file:
        result, _ = it.s.gate_on(it.s.valid, env={"PYTHONIOENCODING": "ascii"})
        expect(result, 0, it.s.green, "stdout")
        return
    result, _ = it.s.gate_on(Write("README.md", NO_ENVELOPE), env={"PYTHONIOENCODING": "ascii"})
    expect(result, 0, it.s.bare_readme, "stdout")


@item(144, "an envelope nested past the parser's depth is blocked, never a crash that lets it through")
def test_deeply_nested_envelope(subject: Subject) -> None:
    """Brackets nested past the parser's depth are an unreadable envelope, never a crash that
    lets the write through."""
    it = shared(subject, "deeply_nested_envelope")
    text = "---\nid: " + "[" * 600 + "\n---\n"
    result, _ = it.s.gate_on(Write(it.s.valid.target, text))  # a path where the envelope is the only defect
    expect(result, 2, "brackets are nested too deeply to read", "stderr")


@item(145, "--scan outside any repository is a configuration failure")
def test_scan_outside_repository(subject: Subject) -> None:
    it = shared(subject, "scan_outside_repository")
    directory = it.h.scratch_dir()
    result = it.h.run_gate(
        "", args=["--scan", str(directory)], env={"GIT_CEILING_DIRECTORIES": str(directory.parent)}
    )
    it.broken(result, messages.c12_no_repo(str(directory)))


@item(146, "--scan=DIR and a scan from a subdirectory examine the same repository")
def test_scan_forms(subject: Subject) -> None:
    """--scan=DIR, and a scan started from a subdirectory, examine the same repository."""
    it = shared(subject, "scan_forms")
    _, root = it.s.gate_on(it.s.valid, files={it.s.valid.target: it.s.valid.text})
    whole = it.h.run_gate("", args=["--scan", str(root)])
    equals = it.h.run_gate("", args=[f"--scan={root}"])
    below = it.h.run_gate("", args=["--scan", str((root / it.s.valid.target).parent)])
    ok = whole.code == 0 and whole.stdout == equals.stdout == below.stdout
    assert ok, f"{whole}\n{equals}\n{below}"


@item(147, "a byte-order mark before the envelope is not part of it")
def test_byte_order_mark(subject: Subject) -> None:
    it = shared(subject, "byte_order_mark")
    result, _ = it.s.gate_on(Write(it.s.valid.target, "\ufeff" + it.s.valid.text))
    expect(result, 0, it.s.green, "stdout")


@item(148, "a file-level negated pattern takes the file out, and the skip names why")
def test_negated_pattern(subject: Subject) -> None:
    """A file-level negated pattern takes the file out of the territory, and the skip says why."""
    it = shared(subject, "negated_pattern")
    if it.s.outside is None:  # an empty default would make the item pass on any skip at all
        pytest.fail("Subject.outside not given")
    territory = [*it.s.territory, "!" + it.s.red.target]
    result, _ = it.s.gate_on(it.s.red, dials_patch=it.s.claim(territory))
    line = f"GREEN: {it.ns}: 0 documents examined — {it.s.outside}"
    ok = result.code == 0 and line in result.stdout.splitlines()
    assert ok, f"wanted exit 0 printing {line!r}; got exit {result.code}: {result.stdout}"


@item(149, "a document where policies live with no readable id earns a note")
def test_policy_without_id_note(subject: Subject) -> None:
    """A document where policies live with no readable id earns note N1.1. An id written as a YAML
    block scalar ends in a line break, which the kernel schema's pattern does not accept: it is no
    readable id either, and earns the note too — the note typed by hand."""
    it = shared(subject, "policy_without_id_note")
    block = "---\nid: |\n  zz-block\ntype: current-state\ntitle: T\nstatus: active\n---\n"
    files = {"docs/policies/zz-no-id.md": NO_ENVELOPE, "docs/policies/zz-block.md": block}
    result, _ = it.s.gate_on(it.s.valid, files=files)
    said = Result(result.code, it.green_said(result), result.stderr)
    lead = " lies in the root policy's territory but carries no readable id; it claims nothing until it does"
    expect(said, 0, messages.n1_note_policy_without_id("docs/policies/zz-no-id.md"), "stdout")
    block_ok = "note: docs/policies/zz-block.md" + lead in said.stdout
    assert block_ok, f"no note for the block-scalar id: {said.stdout[:300]}"


@item(150, "an Edit with an empty old_string on an existing file is a visible skip")
def test_edit_empty_old_string(subject: Subject) -> None:
    """An empty old_string on a file that exists matches everywhere: the tool refuses it."""
    it = shared(subject, "edit_empty_old_string")
    action = Edit(it.s.valid.target, "", "junk ")
    result, _ = it.s.gate_on(action, files={it.s.valid.target: it.s.valid.text})
    skip = messages.g1_green_skip(messages.g1_skip_edit_unappliable(it.s.valid.target))
    expect(result, 0, skip, "stdout")


@item(151, "an echoed value a page long is cut, and the cut is said: the verdict stays a message")
def test_long_value_is_cut(subject: Subject) -> None:
    """A value a page long is echoed cut, so the whole verdict stays under the platform's cap —
    and the cut is said, not silent."""
    it = shared(subject, "long_value_is_cut")
    if it.s.long_value is None:  # the item is left out then; a direct call must not pass vacuously
        pytest.fail("Subject.long_value not given")
    result, _ = it.s.gate_on(it.s.long_value)
    said = it.red_said(result)
    ok = (
        result.code == it.red_code
        and len(red_lines(said)) == 2  # the one finding and the count line
        and "… [12000 characters]" in said  # the marker, typed by hand
        and "x" * 81 not in said
        and len(said) < 2_000
    )
    assert ok, f"exit {result.code}; {len(said)} characters of verdict: {said[:400]}"


@item(152, "C12.1: git failing to list the files is a configuration failure")
def test_ls_files_fails(subject: Subject) -> None:
    it = shared(subject, "ls_files_fails")
    it.git_failing_at(
        "ls-files",
        1,
        lambda root: (
            f"BROKEN: git could not list the files of {root}: fatal: simulated ls-files failure"
            " — fix: repair what git names in the message, then check by hand: git -C <that directory>"
            " ls-files"
        ),
        through_scan=not it.s.hook_lists_files,
    )


@item(153, "C12.2: git failing to make the scratch repository is a configuration failure")
def test_init_fails(subject: Subject) -> None:
    it = shared(subject, "init_fails")
    it.git_failing_at(
        "init",
        128,
        lambda _: (
            "BROKEN: git init of the scratch repository failed: fatal: simulated init failure — fix:"
            " repair what git names in the message; the scratch repository lives in the system's"
            " temporary directory"
        ),
    )


@item(154, "C12.3: git check-ignore failing, not merely matching nothing, is a configuration failure")
def test_check_ignore_fails(subject: Subject) -> None:
    """Exit 128: check-ignore's exit 1 means no path matched, which is no failure. Git's second
    line of stderr stays out of the message, whose first line is the one that reaches the user."""
    it = shared(subject, "check_ignore_fails")
    it.git_failing_at(
        "--no-index",
        128,
        lambda _: (
            "BROKEN: git check-ignore failed: fatal: simulated --no-index failure — fix: territory"
            " patterns must be gitignore syntax; check constitution.yaml"
        ),
        then="hint: a second line of git's message",
    )


@item(155, "C12.7: a dials file the process cannot read is a configuration failure")
def test_dials_unreadable(subject: Subject) -> None:
    it = shared(subject, "dials_unreadable")
    if os.geteuid() == 0:
        return
    _, root = it.s.gate_on(it.s.valid)
    dials = root / it.file  # the gate's own file

    def again() -> Result:
        if it.s.scan_only:
            return it.h.run_gate("", args=it.scan_args(root))
        if it.s.event_driven:
            return it.h.run_gate(it.payload(root, it.s.valid))
        return it.h.run_gate("", args=list(it.s.act_args), cwd=root)  # refused before the home is looked at

    line = (
        f"BROKEN: {it.file} cannot be read ([Errno 13] Permission denied: '{dials}') — fix: check"
        " the file's permissions"
    )
    it.unreadable(dials, again, line)


@item(156, "C12.10: a document git lists and the scan cannot read is a configuration failure")
def test_document_unreadable(subject: Subject) -> None:
    it = shared(subject, "document_unreadable")
    if os.geteuid() == 0:
        return
    sibling = str(Path(it.s.valid.target).with_name("unreadable.md"))
    _, root = it.s.gate_on(it.s.valid, files={sibling: it.s.valid.text})
    line = (
        f"BROKEN: {sibling} is listed by git but cannot be read — fix: check that the file can be read:"
        " its permissions, or a link that leads nowhere"
    )
    it.unreadable(root / sibling, lambda: it.h.run_gate("", args=["--scan", str(root)]), line)


@item(157, "C4: a dials file that is not UTF-8 is C4, its line and column named, never a defect of the gate")
def test_dials_not_utf8(subject: Subject) -> None:
    """A byte that is not UTF-8 is the file's content: C4 naming its line and column, never C12.11."""
    it = shared(subject, "dials_not_utf8")
    _, root = it.s.gate_on(it.s.valid)
    dials = root / it.file  # the gate's own file
    # "# é", then the byte: two bytes, one character, so the column counts characters, not bytes
    dials.write_bytes(b"# \xc3\xa9\xff\n" + dials.read_bytes())
    if it.s.scan_only:
        result = it.h.run_gate("", args=it.scan_args(root))
    elif it.s.event_driven:
        result = it.h.run_gate(it.payload(root, it.s.valid))
    else:
        result = it.h.run_gate("", args=list(it.s.act_args), cwd=root)  # refused before the home is looked at
    line = (
        f"BROKEN: {it.file} is not valid YAML (byte 0xff at line 1, column 4 is not UTF-8; save"
        " the file as UTF-8) — fix: repair the YAML at the place the message names; nothing is checked"
        " until the file parses"
    )
    it.broken_as_typed(result, line)


@item(
    158,
    "C12.10: a file where policies live that nobody can read is a configuration failure, never a"
    " policy with no id",
)
def test_policy_unreadable(subject: Subject) -> None:
    """A file where policies live is a policy by the kernel's rule: one nobody can read is C12.10
    in a hook run too, never a policy with no id and the green skip that would follow."""
    it = shared(subject, "policy_unreadable")
    if os.geteuid() == 0:
        return
    policy = "docs/policies/zz-unreadable.md"
    _, root = it.s.gate_on(it.s.valid, files={policy: NO_ENVELOPE})
    runs: list[Result] = []

    def again() -> Result:
        if it.s.event_driven:
            runs.append(it.h.run_gate(it.payload(root, it.s.valid)))
        else:
            (root / it.s.valid.target).unlink(missing_ok=True)  # the first run wrote it
            runs.append(it.h.run_gate("", args=list(it.s.act_args), cwd=root))
        return runs[-1]

    line = (
        f"BROKEN: {policy} is listed by git but cannot be read — fix: check that the file can be read:"
        " its permissions, or a link that leads nowhere"
    )
    it.unreadable(root / policy, again, line)
    said = (runs[-1].stdout + runs[-1].stderr).splitlines()
    noted = [each for each in said if "carries no readable id" in each]
    if noted:  # note N1.1, its fragment typed by hand: the file taken for a policy with no id
        pytest.fail(f"note N1.1 printed for a file nobody can read: {noted[0]}")


@item(159, "a green hook run with notes hands them to the model as JSON, one without notes stays plain")
def test_notes_reach_the_model(subject: Subject) -> None:
    """A green hook run with notes answers with one JSON object, the notes and the green line in
    additionalContext: the platform writes a write event's plain stdout to its debug log, where the
    model never reads it. A green run without notes prints its green line alone, as before."""
    it = shared(subject, "notes_reach_the_model")
    if it.s.noted is None:  # the item is left out then; a direct call must not pass vacuously
        pytest.fail("Subject.noted not given")
    result, _ = it.s.gate_on(it.s.noted)
    try:
        answer = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"exit {result.code}; stdout is not one JSON object: {result.stdout.strip()[:400]}")
    output = answer.get("hookSpecificOutput") if isinstance(answer, dict) else None
    lines = str(output.get("additionalContext", "")).split("\n") if isinstance(output, dict) else []
    plain, _ = it.s.gate_on(it.s.valid)
    ok = (
        result.code == 0
        and isinstance(output, dict)
        and set(answer) == {"hookSpecificOutput"}
        and set(output) == {"hookEventName", "additionalContext"}
        and output["hookEventName"] == it.s.event
        and it.s.note in lines
        and lines[-1].startswith(f"GREEN: {it.ns}: ")
        and not any(line.startswith("RED") for line in lines)
        and not result.stderr
        and plain.code == 0
        and plain.stdout.startswith(f"GREEN: {it.ns}: ")
    )
    assert ok, f"exit {result.code}: {result.stdout.strip()[:400]} / no notes: {plain.stdout.strip()[:200]}"


@item(160, "C5: a key with a line break, a page long, in the module's namespace is one line, cut")
def test_unknown_dial_is_one_line(subject: Subject) -> None:
    """A key of the module's namespace that holds a line break and is a page long: C5 on one line,
    the backslash and the line break shown escaped, the key cut — in hook mode only the first stderr
    line reaches the user — and, of two keys, the first in sorted order named."""
    it = shared(subject, "unknown_dial_is_one_line")
    key = "ba\\d\nkey" + "x" * 12_000  # a backslash and a line break, each shown escaped
    # a second key that sorts later, written first: the one named is the first in sorted order
    result, _ = it.s.gate_on(it.s.valid, dials_patch=it.s.own(**{"zz_second": 1, key: 1}))
    first = (  # typed by hand: the key cut at 80 characters, its break escaped; the list that
        # follows is the module's own
        f"BROKEN: {it.file}: {it.ns}.ba\\\\d\\nkey" + "x" * 72 + "… [12008 characters] is no dial of"
        " this module — fix: a misspelt dial would be ignored in silence, so none is: write one of "
    )
    lines = result.stderr.splitlines()
    one_line = len(lines) == 1 + len(it.s.closing.splitlines())  # the failure, then the closing line
    ok = result.code == 1 and one_line and lines[0].startswith(first) and len(result.stderr) < 2_000
    assert ok, f"exit {result.code}; {len(lines)} lines; {result.stderr[:300]}"
    it.shared_texts_escape_or_cut()  # the same two helpers at the other shared texts


@item(161, "C5.7: a pattern git would misread in a dial of the module's own is one line, naming it")
def test_pattern_in_own_dial_is_one_line(subject: Subject) -> None:
    """A pattern git would read as a comment, in a dial of the module's own, a page long: C5.7
    naming the dial as it is written — no policy's `.territory` after it — on one line, the pattern
    cut."""
    it = shared(subject, "pattern_in_own_dial_is_one_line")
    if it.s.pattern_dial is None:  # the item is left out then; a direct call must not pass vacuously
        pytest.fail("Subject.pattern_dial not given")
    dial = it.s.pattern_dial
    result, _ = it.s.gate_on(it.s.valid, dials_patch=dial.patch("#" + "x" * 12_000))
    first = (  # typed by hand
        f"BROKEN: {it.file}: {it.ns}.{dial.path} holds a pattern git would not read as one: '#"
        + "x" * 79
        + "… [12001 characters]' — fix: a pattern may not start with '#' (a comment to git) nor contain"
        " a line break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break"
    )
    lines = result.stderr.splitlines()
    one_line = len(lines) == 1 + len(it.s.closing.splitlines())
    ok = result.code == 1 and one_line and lines[0] == first and len(result.stderr) < 2_000
    if not ok:
        assert ok, f"exit {result.code}; {len(lines)} lines; {result.stderr[:300]}"
        return
    # the escape the message teaches passes: `\#drafts/**`, typed by hand, is a pattern git reads as one,
    # so it is no C5.7 and no configuration failure
    escaped, _ = it.s.gate_on(it.s.valid, dials_patch=dial.patch("\\#drafts/**"))
    refused = "holds a pattern git would not read as one" in escaped.stderr + escaped.stdout
    if escaped.code == 1 or refused:
        pytest.fail(
            f"the taught escape \\#drafts/** was refused: exit {escaped.code}; {escaped.stderr[:300]}"
        )


@item(162, "a file named just .md is Markdown to the hook as to the scan")
def test_file_named_md(subject: Subject) -> None:
    """A file named just `.md` is Markdown to the hook as to the scan, which lists it: the hook
    does not skip it for its ending."""
    it = shared(subject, "file_named_md")
    result, root = it.s.gate_on(Write(".md", NO_ENVELOPE))
    said = result.stdout + result.stderr
    (root / ".md").write_text(NO_ENVELOPE, encoding="utf-8")  # the hook never applied the write
    listed = ".md" in list_markdown(root)  # what the scan examines
    ok = "is not a .md file" not in said and "BROKEN:" not in said and listed
    assert ok, f"listed by the scan: {listed}; the hook said: {said[:400]}"


@item(163, "the findings shown after a write: the first always, then what fits, never more than most")
def test_cap_keeps_the_first(subject: Subject) -> None:
    """The findings a hook shows after one write: the first always, however long; then while the
    text fits 8,000 characters; never more than `most` — each number typed by hand."""
    shared(subject, "cap_keeps_the_first")

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
    assert not failed, "; ".join(failed) or "the first always, then what fits, never more than `most`"


@item(
    164,
    "a `---` line with trailing whitespace opens and closes the envelope, and a line-break character"
    " other than \\n, \\r\\n or \\r makes no delimiter",
)
def test_envelope_delimiters(subject: Subject) -> None:
    """A `---` line with trailing whitespace opens and closes the envelope, and a line ends at
    `\\n`, `\\r\\n` or a lone `\\r` only: a delimiter after any other break character is none. The
    offsets typed by hand, a byte-order mark counted."""
    it = shared(subject, "envelope_delimiters")
    closer = "\n---\n"
    at = it.s.valid.text.find(closer)
    if not it.s.valid.text.startswith("---\n") or at < 0:
        pytest.fail("the module's valid write holds no plain envelope to vary")
    head, body = it.s.valid.text[:at], it.s.valid.text[at + len(closer) :]
    failed = [
        *it.delimiter_failures_in_writes(head, body),
        *reader_delimiter_failures(),
        *envelope_bounds_failures(),
        *envelope_lines_failures(),
    ]
    assert not failed, "; ".join(failed)[:600]


@item(
    165,
    "C12.12, C12.13: a git that gives no answer in a hook ends in a shared line within the budget,"
    " a scan and an act give git no clock, and the hook's handlers hold its budget and the margin",
)
def test_git_has_a_budget_in_a_hook(subject: Subject) -> None:
    """N22: the shared `git` gives a call `GIT_SECONDS` in a hook and no clock in a scan or an act. In a
    hook a git that never answers — at the file list, at the scratch repository, at the repository's
    root — ends in the shared line `C12.12` with the count line after it; a git that answers is
    unchanged; and the plugin's handlers hold the hook's budget and `LEFT_FOR_THE_REST`, so that the
    line is the hook's last word."""
    it = shared(subject, "git_has_a_budget_in_a_hook")
    results: list[tuple[bool, str]] = [
        it.attempted(check)
        for check in (
            it.budget_by_mode,
            it.scopes_shadow,
            it.git_words,
            it.the_tie_catches_a_short_handler,
        )
    ]
    if it.s.event_driven and not it.s.scan_only:  # a gate with a hook run
        lines: dict[str, Callable[[Path], str]] = {
            "rev-parse": lambda root: it.silent_git(
                "rev-parse", it.nearest_folder(root), "rev-parse --show-toplevel"
            ),
            "ls-files": lambda root: it.silent_git(
                "ls-files", str(root), "ls-files --cached --others --exclude-standard"
            ),
            "init": lambda _: it.silent_scratch("init"),
            "check-ignore": lambda _: it.silent_scratch("check-ignore"),
        }
        reached = ["rev-parse"]
        if not it.no_file:
            reached += ["init", "check-ignore"]
            if it.s.hook_lists_files:  # the hook asks git for the file list
                reached.append("ls-files")

        def hangs_at(trigger: str) -> tuple[bool, str]:
            def hang() -> None:
                it.git_failing_at(trigger, 0, lines[trigger], hangs=True)

            hang.__name__ = f"a git that hangs at {trigger}"
            return it.attempted(hang)

        results += [hangs_at(trigger) for trigger in reached]
        results.append(it.attempted(it.hangs_in_a_folder_to_quote))
        env, log = git_patch(it.h)
        it.s.gate_on(it.s.valid, env=env)
        budgeted = git_timeouts(log)
        every_call = set(budgeted) == {repr(repository.GIT_SECONDS)}
        results.append(
            (every_call, f"a hook run's {len(budgeted)} git calls' timeouts: {sorted(set(budgeted))}")
        )
        declared = set(declared_hook_seconds(log))  # the hook budget the gate declared itself with
        results.append(
            it.handlers_outlive_git(preflight.requirements_file().parent, float(declared.pop()))
            if len(declared) == 1
            else (False, f"a hook run declared the gate with {sorted(declared)} hook budgets, not one")
        )
    if it.s.event_driven or it.s.scan_only:  # a scan, on the prepared consumer
        _, scanned = it.s.gate_on(it.s.valid)
        unclocked = it.git_calls(lambda env: it.h.run_gate("", args=it.scan_args(scanned), env=env))
        results.append((bool(unclocked) and set(unclocked) == {"None"}, f"a scan's git calls: {unclocked}"))
    else:  # a generator's act
        acted = it.git_calls(lambda env: it.s.gate_on(it.s.valid, env=env))
        results.append((bool(acted) and set(acted) == {"None"}, f"an act's git calls: {acted}"))
    failed = [evidence for ok, evidence in results if not ok]
    if failed:
        pytest.fail(f"{len(failed)} of {len(results)} checks red: " + " | ".join(failed))


@item(166, "F10: a red names the skill that teaches the rule and its fix, after the count line")
def test_skill_named_after_red(subject: Subject) -> None:
    """A red names the skill that teaches the rule and its fix in one line right after the count
    line, the last line of the block, the asking reason or the scan; the warn context the model
    reads holds the line once, the warn note after it."""
    it = shared(subject, "skill_named_after_red")
    line = (
        f"{it.ns}: load the skill {it.ns}:{it.s.skill} before you fix this — it teaches the rule and the fix"
    )
    result, _ = it.s.gate_on(it.s.red)  # the line typed by hand above
    lines = it.red_said(result).splitlines()
    ok = (
        result.code == it.red_code
        and len(lines) >= 2
        and lines[-1] == line
        and lines[-2].startswith("RED: ")
        and lines.count(line) == 1
    )
    if not ok:
        pytest.fail(f"exit {result.code}, the last lines: {lines[-2:]}")
    if it.s.scan_only or it.stop:  # a scan has no warn; a Stop's warn is the user's notice alone
        return
    warned, _ = it.s.gate_on(it.s.red, dials_patch=it.s.own(severity="warn"))
    context = json.loads(warned.stdout)["hookSpecificOutput"]["additionalContext"].splitlines()
    ok = (  # the count line, then F10, then the warn note, typed by hand, last
        context.count(line) == 1
        and len(context) >= 3
        and context[-2] == line
        and context[-3].startswith("RED: ")
        and context[-1].startswith(f"{it.ns}: severity is warn: the write proceeds")
    )
    assert ok, str(context)


@item(
    167,
    "C12.14: a hook run has one deadline from the opening of its scope, every wait takes the smaller of its"
    " cap and what is left, and a run that spends it ends in a shared line; a scan and an act have none",
)
def test_hook_has_one_deadline(subject: Subject) -> None:
    """N52: a hook run has one deadline, from the opening of its scope, and every wait takes the smaller of
    its own cap and what is left of it; past it the gate says so in the shared line C12.14, non-blocking
    like every configuration failure, the count line after it. A scan, an act and a scope opened with no
    mode have no deadline. Read at the decision point, in a process for each mode, in a process whose
    clock is moved past the deadline, in a process whose clock shows that the opening starts it, and
    through the gate with a git that answers late on a clock of the test's own, which only git's answers
    move."""
    it = shared(subject, "hook_has_one_deadline")
    results: list[tuple[bool, str]] = [
        it.attempted(check)
        for check in (it.deadline_by_mode, it.spent_deadline, it.deadline_starts_at_the_opening)
    ]
    if it.s.event_driven and not it.s.scan_only:  # a gate with a hook run
        results += [
            it.attempted(it.slow_git_within_the_cap),
            it.attempted(it.slow_git_spends_the_deadline),
        ]
    failed = [evidence for ok, evidence in results if not ok]
    if failed:
        pytest.fail(f"{len(failed)} of {len(results)} checks red: " + " | ".join(failed))


# The version check of a module's entry file, `cli.version_failure`: a module of namespace `const-x`, its
# install note at VERSION_GUIDE, its closing clause VERSION_UNTIL. The installed version is set by pytest's
# `monkeypatch` on the `__version__` that `cli` reads, so that every case names it by hand.
VERSION_GUIDE = "/p/plugin/INSTALL.md"
VERSION_UNTIL = "until then Markdown writes pass unchecked"
# The end both lines share, typed by hand: the module's install note and its closing clause.
GUIDE_SAYS = "for python3 as /p/plugin/INSTALL.md says — until then Markdown writes pass unchecked"


def version_asked(
    monkeypatch: pytest.MonkeyPatch,
    installed: str,
    required: str,
    guide: str = VERSION_GUIDE,
    until: str = VERSION_UNTIL,
) -> str | None:
    """What the check says to a module of namespace `const-x` that requires `required`, when the
    installed package is `installed`."""
    monkeypatch.setattr(cli, "__version__", installed)
    return cli.version_failure("const-x", required, guide, until)


@item(
    168,
    "version_failure: an installed version at or above the required one, of the same major, gives no line",
)
def test_version_serves(subject: Subject, monkeypatch: pytest.MonkeyPatch) -> None:
    """The check returns None for the same version, a later minor, a later patch, a later minor with an
    earlier patch, and for numbers read as numbers (10 is above 9), in major 0 and in a later major too."""
    shared(subject, "version_serves")
    cases = [  # (installed, required, why it serves)
        ("1.0.0", "1.0.0", "the same version"),
        ("1.1.0", "1.0.0", "a later minor"),
        ("1.0.1", "1.0.0", "a later patch"),
        ("1.3.0", "1.2.9", "a later minor with an earlier patch"),
        ("1.10.0", "1.9.0", "a minor of 10 is above one of 9"),
        ("1.0.10", "1.0.9", "a patch of 10 is above one of 9"),
        ("12.0.0", "12.0.0", "the same version in major 12"),
        ("2.5.7", "2.5.6", "a later patch in major 2"),
        ("0.4.3", "0.4.2", "a later patch in major 0"),
        ("0.0.0", "0.0.0", "the smallest version, as the largest requirement"),
    ]
    failed = [
        f"installed {installed} for a module that requires {required} ({why}): {said!r}"
        for installed, required, why in cases
        if (said := version_asked(monkeypatch, installed, required)) is not None
    ]
    assert not failed, "; ".join(failed)


@item(169, "C16: an installed version below the required one, a required major above it included, is a line")
def test_version_shared_too_old(subject: Subject, monkeypatch: pytest.MonkeyPatch) -> None:
    """The shared code is too old for the module: below it by a patch, by a minor, by numbers read as
    numbers (9 is below 10), by a major — the line then names the later major — each line typed by hand."""
    shared(subject, "version_shared_too_old")
    cases = [  # (installed, required, the line's headline)
        (
            "1.0.0",
            "1.0.1",
            "const-x needs constitution-layer-kit 1.0.1 or a later 1.x release, found 1.0.0",
        ),
        (
            "1.2.9",
            "1.3.0",
            "const-x needs constitution-layer-kit 1.3.0 or a later 1.x release, found 1.2.9",
        ),
        (
            "1.9.0",
            "1.10.0",
            "const-x needs constitution-layer-kit 1.10.0 or a later 1.x release, found 1.9.0",
        ),
        (
            "1.0.9",
            "1.0.10",
            "const-x needs constitution-layer-kit 1.0.10 or a later 1.x release, found 1.0.9",
        ),
        (
            "1.9.9",
            "2.0.0",
            "const-x needs constitution-layer-kit 2.0.0 or a later 2.x release, found 1.9.9",
        ),
        (
            "2.0.0",
            "3.1.4",
            "const-x needs constitution-layer-kit 3.1.4 or a later 3.x release, found 2.0.0",
        ),
        (
            "0.9.0",
            "1.0.0",
            "const-x needs constitution-layer-kit 1.0.0 or a later 1.x release, found 0.9.0",
        ),
        (
            "9.9.9",
            "10.0.0",
            "const-x needs constitution-layer-kit 10.0.0 or a later 10.x release, found 9.9.9",
        ),
    ]
    failed = []
    for installed, required, headline in cases:
        line = f"BROKEN: {headline} — fix: install one {GUIDE_SAYS}"
        said = version_asked(monkeypatch, installed, required)
        if said != line:
            failed.append(f"installed {installed}, required {required}: wanted {line!r}, got {said!r}")
    assert not failed, "; ".join(failed)


@item(170, "C17: a required major below the installed one is a line naming the version required and found")
def test_version_module_too_old(subject: Subject, monkeypatch: pytest.MonkeyPatch) -> None:
    """The module is too old for the installed major, whatever its minor and patch (a required 1.9.9 is
    below an installed 2.0.0), the majors read as numbers (9 is below 10); the line names the version the
    module requires and its major, the version found, and both ways out, each line typed by hand."""
    shared(subject, "version_module_too_old")
    written = "const-x was written for constitution-layer-kit"
    cases = [  # (installed, required, headline, the major to update the plugin to, the one to install)
        ("2.0.0", "1.4.2", f"{written} 1.4.2, a 1.x release, found 2.0.0", "2.x", "1.x"),
        ("2.0.0", "1.9.9", f"{written} 1.9.9, a 1.x release, found 2.0.0", "2.x", "1.x"),
        ("3.1.4", "1.0.0", f"{written} 1.0.0, a 1.x release, found 3.1.4", "3.x", "1.x"),
        ("1.0.0", "0.9.9", f"{written} 0.9.9, a 0.x release, found 1.0.0", "1.x", "0.x"),
        ("10.2.3", "9.9.9", f"{written} 9.9.9, a 9.x release, found 10.2.3", "10.x", "9.x"),
    ]
    failed = []
    for installed, required, headline, update_to, install in cases:
        line = (
            f"BROKEN: {headline} — fix: update the plugin to a release written for {update_to}, or install a"
            f" {install} release of constitution-layer-kit {GUIDE_SAYS}"
        )
        said = version_asked(monkeypatch, installed, required)
        if said != line:
            failed.append(f"installed {installed}, required {required}: wanted {line!r}, got {said!r}")
    assert not failed, "; ".join(failed)


@item(171, "C16, C17: a generator's empty clause closes the line with none, and a guide path is escaped")
def test_version_clause_and_guide(subject: Subject, monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty closing clause, a generator's, leaves no dash and no text after `says`, in both lines. A
    guide path with a line break, a carriage return and a backslash is shown escaped, never cut, so each
    line stays one line; each line typed by hand."""
    shared(subject, "version_clause_and_guide")
    bare_16 = (  # installed 1.0.0, required 1.0.1, no clause
        "BROKEN: const-x needs constitution-layer-kit 1.0.1 or a later 1.x release, found 1.0.0"
        " — fix: install one for python3 as /p/plugin/INSTALL.md says"
    )
    bare_17 = (  # installed 2.0.0, required 1.4.2, no clause
        "BROKEN: const-x was written for constitution-layer-kit 1.4.2, a 1.x release, found 2.0.0 — fix:"
        " update the plugin to a release written for 2.x, or install a 1.x release of constitution-layer-kit"
        " for python3 as /p/plugin/INSTALL.md says"
    )
    odd = "/p/a\nb\rc\\d/INSTALL.md"  # a line feed, a carriage return and a backslash
    escaped_16 = (
        "BROKEN: const-x needs constitution-layer-kit 1.0.1 or a later 1.x release, found 1.0.0"
        " — fix: install one for python3 as /p/a\\nb\\rc\\\\d/INSTALL.md says"
        " — until then Markdown writes pass unchecked"
    )
    escaped_17 = (
        "BROKEN: const-x was written for constitution-layer-kit 1.4.2, a 1.x release, found 2.0.0 — fix:"
        " update the plugin to a release written for 2.x, or install a 1.x release of constitution-layer-kit"
        " for python3 as /p/a\\nb\\rc\\\\d/INSTALL.md says — until then Markdown writes pass unchecked"
    )
    checks = [  # (installed, required, guide, clause, the line)
        ("1.0.0", "1.0.1", VERSION_GUIDE, "", bare_16),
        ("2.0.0", "1.4.2", VERSION_GUIDE, "", bare_17),
        ("1.0.0", "1.0.1", odd, VERSION_UNTIL, escaped_16),
        ("2.0.0", "1.4.2", odd, VERSION_UNTIL, escaped_17),
    ]
    failed = []
    for installed, required, guide, until, line in checks:
        said = version_asked(monkeypatch, installed, required, guide, until)
        if said != line:
            failed.append(f"installed {installed}, required {required}: wanted {line!r}, got {said!r}")
        elif said is not None and len(said.splitlines()) != 1:
            failed.append(f"installed {installed}, required {required}: the line is not one line: {said!r}")
    assert not failed, "; ".join(failed)


@item(172, "version_failure: a required version that is not major.minor.patch of integers raises ValueError")
def test_version_malformed(subject: Subject, monkeypatch: pytest.MonkeyPatch) -> None:
    """A malformed required version is a defect of the module, not a line: it raises ValueError, whatever
    is installed — fewer or more parts, a leading zero, a prefix, a suffix, a space or line break around
    it, a sign, a digit of another script. The edges of the shape stay accepted. The installed version, if
    it were malformed, would raise too, never serve in silence."""
    shared(subject, "version_malformed")
    malformed = [
        "",
        "1",
        "1.0",
        "1.0.0.0",
        "01.0.0",
        "1.00.0",
        "1.0.00",
        "v1.0.0",
        "1.0.0-rc1",
        "1.0.0+build",
        "1.0.0a1",
        "1.0.x",
        "1..0",
        "1,0,0",
        " 1.0.0",
        "1.0.0 ",
        "1.0.0\n",
        "-1.0.0",
        "+1.0.0",
        "1.-1.0",
        "١.٠.٠",  # Arabic-Indic digits, which int() reads and the shape does not
        "１.０.０",  # full-width digits
        "1٠.0.0",  # an ASCII digit first, an Arabic-Indic one after it: ten, to int()
        "1.1٠.0",
        "1.0.1١",
        "1.0.0.",
        "constitution-layer-kit-v1.0.0",
    ]
    not_raised = []
    for required in malformed:
        try:
            said = version_asked(monkeypatch, "5.0.0", required)
        except ValueError:
            continue
        not_raised.append(f"{required!r} gave {said!r}")
    edges = [("0.0.0", "0.0.0"), ("10.20.30", "10.20.30"), ("100.0.1", "99.99.99")]
    refused = []
    for installed, required in edges:
        try:
            version_asked(monkeypatch, installed, required)
        except ValueError as error:
            refused.append(f"{required!r} with {installed} installed: {error}")
    try:
        said = version_asked(monkeypatch, "1.0", "1.0.0")
    except ValueError:
        said = "ValueError"
    problems = [
        *([f"no ValueError for {len(not_raised)} of them: {'; '.join(not_raised)}"] if not_raised else []),
        *([f"a well-formed version refused: {'; '.join(refused)}"] if refused else []),
        *([f"a malformed installed version gave {said!r}, not ValueError"] if said != "ValueError" else []),
    ]
    assert not problems, " | ".join(problems)


@item(173, "version_failure reads the package's own __version__ and keeps its signature")
def test_version_reads_the_package(subject: Subject) -> None:
    """Unpatched, the check reads the `__version__` of the package: that version serves a module that
    requires it, a patch above it is `C16` naming it, a major below it is `C17` naming it. The parameters
    are `namespace`, `required`, `guide` and `until`, in that order, each a string with no default, and the
    result is a string or None: the signature every module's entry file calls from the first release on."""
    shared(subject, "version_reads_the_package")
    major, minor, patch = (int(part) for part in package_version.split("."))
    above = f"{major}.{minor}.{patch + 1}"
    problems = []
    if cli.__version__ != package_version:
        problems.append(f"cli reads {cli.__version__!r}, the package says {package_version!r}")
    served = cli.version_failure("const-x", package_version, VERSION_GUIDE, VERSION_UNTIL)
    if served is not None:
        problems.append(f"the installed version does not serve a module that requires it: {served!r}")
    shared_old = cli.version_failure("const-x", above, VERSION_GUIDE, VERSION_UNTIL)
    wanted = (
        f"BROKEN: const-x needs constitution-layer-kit {above} or a later {major}.x release,"
        f" found {package_version} — fix: install one {GUIDE_SAYS}"
    )
    if shared_old != wanted:
        problems.append(f"required {above}: wanted {wanted!r}, got {shared_old!r}")
    if major >= 1:
        module_old = cli.version_failure("const-x", f"{major - 1}.0.0", VERSION_GUIDE, VERSION_UNTIL)
        wanted = (
            f"BROKEN: const-x was written for constitution-layer-kit {major - 1}.0.0, a {major - 1}.x"
            f" release, found {package_version} — fix: update the plugin to a release written for"
            f" {major}.x, or install a {major - 1}.x release of constitution-layer-kit {GUIDE_SAYS}"
        )
        if module_old != wanted:
            problems.append(f"required {major - 1}.0.0: wanted {wanted!r}, got {module_old!r}")
    parameters = inspect.signature(cli.version_failure, eval_str=True)
    names = list(parameters.parameters)
    typed = [parameters.parameters[name].annotation for name in names]
    plain = [parameters.parameters[name].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for name in names]
    bare = [parameters.parameters[name].default is inspect.Parameter.empty for name in names]
    if names != ["namespace", "required", "guide", "until"] or typed != [str] * 4 or not all(plain + bare):
        problems.append(f"the signature changed: {parameters}")
    if parameters.return_annotation != (str | None):
        problems.append(f"the result is no longer a string or None: {parameters.return_annotation!r}")
    assert not problems, " | ".join(problems)


# The declaration of a gate — its identity, the name of its dials file included, and the mode of the run — is
# held in a context variable of the shared package with no default, and exists only inside a scope of
# `identity.declared`. The module's conftest opens one scope for the test session, with the identity its test
# file names; an item that needs another declaration opens its own scope inside it, and an item that needs
# none runs in a context of its own, `contextvars.Context().run`, which starts empty and keeps whatever it
# declares to itself. The defects' texts are typed by hand.
UNDECLARED = "the entry point did not declare which gate it is"
EMPTY = "a process reads one dials file: an empty name is no file, a defect of the entry point"
OTHER_FILE = "team.yaml"  # a name no kit of this repository uses
BLANK_FILES = ("", "   ", " \t\n")  # names of no file: empty, and empty once stripped of whitespace


def named(dials_file: str, gate: str = "y", hook_seconds: float = identity.HOOK_SECONDS) -> identity.Identity:
    """An identity for the items that open a scope of their own: namespace `x`, the gate `gate`, the dials
    file `dials_file`."""
    return identity.Identity("x", gate, Path("."), dials_file, KERNEL_KEYS, hook_seconds=hook_seconds)


def refused_with(text: str, body: Callable[[], object]) -> str | None:
    """None when `body`, run in a context of its own, raises the RuntimeError whose text is `text`;
    otherwise what happened instead."""
    try:
        done = contextvars.Context().run(body)
    except RuntimeError as defect:
        return None if str(defect) == text else f"RuntimeError({str(defect)!r})"
    return f"returned {done!r}"


@item(
    174,
    "outside every scope nothing is declared: a read of the identity or of the dials file's name is a defect,"
    " in code and in text, the mode reads as none and no wait has a deadline",
)
def test_dials_file_undeclared(subject: Subject) -> None:
    """In a context of its own, where no scope is open, the identity, the dials file's name, the dials
    reader and five of the shared messages that name the file (`G1.4`, `G1.5`, `C4b`, `C5.8`, `C13`)
    raise `RuntimeError` and never read or print a file of some kit's — the reader even where a file named
    `constitution.yaml` lies in the repository. The mode reads as none, and a wait takes its cap, a wait no
    verdict depends on its cap, and a wait that ran out is its own failure's line, as they did with no
    declaration. And the shared code holds no name of the file at all: its source says `constitution.yaml`
    nowhere, so that no module-level name can hold it."""
    shared(subject, "dials_file_undeclared")
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        valid = {"module_prefix": "const-", "root_policy": "docs/p.md"}
        (root / "constitution.yaml").write_text(json.dumps(valid), encoding="utf-8")
        reads: dict[str, Callable[[], object]] = {
            "identity.current": identity.current,
            "identity.dials_file": identity.dials_file,
            "dials.load_dials": lambda: load_dials(root),
            "G1.4": lambda: messages.g1_skip_no_dials("/r"),
            "G1.5": messages.g1_skip_no_root,
            "C4b": messages.c4b_dials_not_mapping,
            "C5.8": messages.c5_severity,
            "C13": lambda: messages.c13_log_dir_not_ignored("logs"),
        }
        for label, read in reads.items():
            if (refused := refused_with(UNDECLARED, read)) is not None:
                problems.append(f"{label} outside every scope: {refused}")
    own = Broken(SharedKey.C2, "a wait of its own ran out", "wait less")

    def without_a_scope() -> list[object]:
        failure = identity.ran_out(1, 10, "x", own)
        return [identity.declared_mode(), identity.remaining(10, "x"), identity.left_of(10), failure.broken]

    if (got := contextvars.Context().run(without_a_scope)) != [None, 10, 10, own]:
        problems.append(f"the mode, the waits and the failure of a wait outside every scope: {got}")
    source = Path(inspect.getsourcefile(identity) or "").resolve().parent
    files = sorted(source.glob("*.py"))
    if not files:
        problems.append(f"no source of the shared package found beside {source}")
    problems += [
        f"{path.name} names constitution.yaml"
        for path in files
        if "constitution.yaml" in path.read_text(encoding="utf-8")
    ]
    assert not problems, "; ".join(problems)


@item(
    175,
    "an identity whose dials file is empty, or empty once stripped of whitespace, is a defect of the entry"
    " point as its scope opens, and declares nothing",
)
def test_dials_file_empty(subject: Subject) -> None:
    """An empty name is no file, and so is one of only whitespace, which is empty once stripped. Opening a
    scope with such an identity raises `RuntimeError` of its own text, in a context where nothing is
    declared — a read there is still the defect of S174, and a real scope opened after it stands — and
    inside an open scope, which the failed opening leaves as it was."""
    shared(subject, "dials_file_empty")

    def opens_empty_first(empty: str) -> str:
        try:
            with identity.declared(named(empty)):
                return "no error"
        except RuntimeError as defect:
            if str(defect) != EMPTY:
                return f"RuntimeError({str(defect)!r})"
        try:
            read = identity.dials_file()
        except RuntimeError as defect:
            if str(defect) != UNDECLARED:
                return f"after the failed opening, a read raised RuntimeError({str(defect)!r})"
        else:
            return f"after the failed opening, a read gave {read!r}"
        with identity.declared(named(OTHER_FILE)):
            return identity.dials_file()

    def opens_empty_inside(empty: str) -> str:
        with identity.declared(named(OTHER_FILE, "outer")):
            try:
                with identity.declared(named(empty, "inner")):
                    return "no error"
            except RuntimeError as defect:
                if str(defect) != EMPTY:
                    return f"RuntimeError({str(defect)!r})"
            return f"{identity.current().gate} {identity.dials_file()}"

    problems = []
    for empty in BLANK_FILES:
        if (read := contextvars.Context().run(opens_empty_first, empty)) != OTHER_FILE:
            problems.append(f"{empty!r} first, then {OTHER_FILE!r}: {read!r}, wanted {OTHER_FILE!r}")
        if (read := contextvars.Context().run(opens_empty_inside, empty)) != f"outer {OTHER_FILE}":
            problems.append(f"{empty!r} inside {OTHER_FILE!r}: {read!r}, wanted the outer scope's")
    assert not problems, "; ".join(problems)


@item(
    176,
    "a scope declares the gate until it closes, normally or by an exception; one opened inside another"
    " shadows it and the outer one holds again; one made in a context of its own leaves the session's alone",
)
def test_scopes(subject: Subject) -> None:
    """The declaration exists from the opening of a scope to its closing and is reset at the closing,
    whether the body ends or raises — and a body's own exception passes through. A scope opened inside
    another shadows the outer declaration, the gate, the dials file's name and the mode, until it closes,
    and the outer one holds again after it: the same identity and mode twice, another mode, another
    identity and another name of the file are all no defect, and an inner scope that ends by an exception
    leaves the outer one as it was. A scope opened in a context of its own leaves the session's
    declaration as it was."""
    shared(subject, "scopes")
    first, second = named("a.yaml", "first"), named("b.yaml", "second", hook_seconds=7)

    def reads() -> tuple[str, str, Mode | None]:
        return identity.current().gate, identity.dials_file(), identity.declared_mode()

    def lifecycle() -> list[object]:
        seen: list[object] = [refused_with(UNDECLARED, reads)]
        with identity.declared(first, Mode.HOOK):
            seen.append(reads())
        seen.append(refused_with(UNDECLARED, reads))
        try:
            with identity.declared(first):
                seen.append(reads())
                raise KeyError("raised in the body")
        except KeyError as passed:
            seen.append(str(passed))
        seen.append(refused_with(UNDECLARED, reads))
        return seen

    def nested() -> list[object]:
        seen: list[object] = []
        with identity.declared(first, Mode.HOOK):
            with identity.declared(first, Mode.HOOK):
                seen.append(reads())
            seen.append(reads())
            with identity.declared(first, Mode.SCAN):
                seen.append(reads())
            with identity.declared(second):
                seen.append(reads())
                try:
                    with identity.declared(first, Mode.ACT):
                        seen.append(reads())
                        raise KeyError("raised in the inner body")
                except KeyError:
                    seen.append(reads())
            seen.append(reads())
        seen.append(refused_with(UNDECLARED, reads))
        return seen

    wanted_lifecycle: list[object] = [
        None,  # before the scope: a read is the defect
        ("first", "a.yaml", Mode.HOOK),
        None,  # after it: the defect again
        ("first", "a.yaml", None),
        "'raised in the body'",
        None,  # after a body that raised: the defect again
    ]
    wanted_nested: list[object] = [
        ("first", "a.yaml", Mode.HOOK),  # the same identity and mode again
        ("first", "a.yaml", Mode.HOOK),  # the outer scope holds again
        ("first", "a.yaml", Mode.SCAN),  # the same identity in another mode
        ("second", "b.yaml", None),  # another identity, its file and no mode
        ("first", "a.yaml", Mode.ACT),  # a scope inside that one
        ("second", "b.yaml", None),  # which an exception closed: the one around it holds
        ("first", "a.yaml", Mode.HOOK),  # the outermost holds again
        None,  # and after it: the defect
    ]
    problems = []
    for what, run, wanted in (("lifecycle", lifecycle, wanted_lifecycle), ("nesting", nested, wanted_nested)):
        if (got := contextvars.Context().run(run)) != wanted:
            problems.append(f"{what}: wanted {wanted}, got {got}")
    session = (identity.current(), identity.dials_file(), identity.declared_mode())
    contextvars.Context().run(lifecycle)
    contextvars.Context().run(nested)
    if (after := (identity.current(), identity.dials_file(), identity.declared_mode())) != session:
        problems.append(f"scopes made in contexts of their own changed the session's declaration: {after}")
    assert not problems, "; ".join(problems)


@item(177, "every shared message that names the dials file names the declared one, and the reader opens it")
def test_dials_file_name_is_the_declared_one(subject: Subject) -> None:
    """With a scope of the module's own identity, its dials file `team.yaml`, open inside the session's,
    each of the twenty-three shared texts that name the file says `team.yaml` and none says
    `constitution.yaml`, each text typed by hand; `load_dials` opens `team.yaml` and never
    `constitution.yaml`, reads no file where only `constitution.yaml` lies, and its failure on a team.yaml
    that is no YAML names `team.yaml`."""
    it = shared(subject, "dials_file_name_is_the_declared_one")
    ns = it.ns
    team = replace(identity.current(), dials_file=OTHER_FILE, kernel_keys=KERNEL_KEYS)  # a file of this kit's

    def built() -> dict[str, str]:
        return {
            "G1.4": messages.g1_skip_no_dials("/r"),
            "G1.5": messages.g1_skip_no_root(),
            "C4": messages.c4_dials_invalid_yaml("at line 2").render(),
            "C4b": messages.c4b_dials_not_mapping().render(),
            "C5.1": messages.c5_root_policy_path().render(),
            "C5.2": messages.c5_dialect_empty().render(),
            "C5.3": messages.c5_dialect_unsupported("svn").render(),
            "C5.4": messages.c5_namespace_not_mapping("k").render(),
            "C5.5": messages.c5_own_namespace_not_mapping().render(),
            "C5.6": messages.c5_territory_shape("k").render(),
            "C5.7": messages.c5_territory_pattern("k.territory", "#x").render(),
            "C5.8": messages.c5_severity().render(),
            "C5.9": messages.c5_log_dir().render(),
            "C5.10": messages.c5_unknown_dial("zz", ["a", "b"]).render(),
            "C5.11": messages.c5_prefix_invalid().render(),
            "C5.12": messages.c5_namespace_outside_prefix("other-").render(),
            "C5.13": messages.c5_kernel_key_elsewhere("root_policy").render(),
            "C5.14": messages.c5_prefix_invalid_kernel_part().render(),
            "C6": messages.c6_root_missing("docs/p.md").render(),
            "C8": messages.c8_root_claims_nothing("pol").render(),
            "C12.3": messages.c12_check_ignore("boom").render(),
            "C12.7": messages.c12_dials_unreadable("denied").render(),
            "C13": messages.c13_log_dir_not_ignored("logs").render(),
        }

    with identity.declared(team):
        said = built()
    wanted = {  # typed by hand
        "G1.4": "no team.yaml in /r: nothing is claimed",
        "G1.5": "team.yaml has no root_policy: nothing is claimed",
        "C4": "BROKEN: team.yaml is not valid YAML (at line 2) — fix: repair the YAML at the place the"
        " message names; nothing is checked until the file parses",
        "C4b": "BROKEN: team.yaml is not a mapping — fix: the file holds top-level keys: module_prefix,"
        " root_policy, and territory_dialect when the dialect is not gitignore, then one namespace per"
        " policy or module",
        "C5.1": "BROKEN: team.yaml: root_policy must be a repository-relative path — fix: root_policy:"
        " <path of the root policy, relative to the repository root>",
        "C5.2": "BROKEN: team.yaml: territory_dialect must be a non-empty string — fix: remove the key, or"
        " set territory_dialect: gitignore — the one dialect supported",
        "C5.3": f"BROKEN: team.yaml: territory_dialect 'svn' is not supported by {ns} (supports: gitignore)"
        " — fix: set territory_dialect: gitignore, or remove the key",
        "C5.4": "BROKEN: team.yaml: namespace 'k' must be a mapping — fix: write it as k: {territory: [...]}",
        "C5.5": f"BROKEN: team.yaml: namespace '{ns}' must be a mapping of this module's dials — fix: write"
        " this module's dials under it as a mapping, or remove the key",
        "C5.6": "BROKEN: team.yaml: k.territory must be a list of non-empty strings — fix: write it as k:"
        ' {territory: ["<pattern>", ...]}',
        "C5.7": "BROKEN: team.yaml: k.territory holds a pattern git would not read as one: '#x' — fix: a"
        " pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading #"
        " as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",
        "C5.8": f"BROKEN: team.yaml: {ns}.severity must be block or warn — fix: under {ns}, set severity:"
        " block or severity: warn, or remove that line",
        "C5.9": f"BROKEN: team.yaml: {ns}.log_dir must be a repository-relative directory — fix: under"
        f" {ns}, set log_dir: <a git-ignored directory>, or remove that line",
        "C5.10": f"BROKEN: team.yaml: {ns}.zz is no dial of this module — fix: a misspelt dial would be"
        " ignored in silence, so none is: write one of a, b",
        "C5.11": "BROKEN: team.yaml: module_prefix is missing, or is not a kebab-case word that ends in '-'"
        " — fix: a gate tells a module's namespace from a policy's by this prefix, so write module_prefix:"
        f" {it.prefix} as a top-level key, or correct its value to a kebab-case word that ends in '-'",
        "C5.12": f"BROKEN: team.yaml: module_prefix 'other-' is not the start of this module's namespace"
        f" '{ns}' — fix: a gate reads the file of its own modules only, so set module_prefix: {it.prefix} if"
        " this file is for this module, or check it with a module whose namespace starts with 'other-'",
        "C5.13": "BROKEN: team.yaml: root_policy is no key of this file — fix: this module's gates read"
        " root_policy from the dials file that holds the policies, so a copy here would be ignored or"
        " contradict it: remove the line, and set root_policy in that file",
        "C5.14": "BROKEN: team.yaml: module_prefix is missing, or is not a kebab-case word that ends in '-'"
        " — fix: a gate tells a module's namespace from a policy's by this prefix, so write module_prefix:"
        " <the prefix of the modules whose dials this file holds> as a top-level key, or correct its value"
        " to a kebab-case word that ends in '-'",
        "C6": "BROKEN: team.yaml names root_policy 'docs/p.md' but no such file exists — fix: create it, or"
        " point root_policy at the policy for policies",
        "C8": "BROKEN: root policy 'pol' claims no territory in team.yaml — fix: write pol: {territory:"
        " [<where policies live, including the root itself>]} — nothing is governed until then",
        "C12.3": "BROKEN: git check-ignore failed: boom — fix: territory patterns must be gitignore syntax;"
        " check team.yaml",
        "C12.7": "BROKEN: team.yaml cannot be read (denied) — fix: check the file's permissions",
        "C13": f"BROKEN: team.yaml: {ns}.log_dir 'logs' is not ignored by git — fix: a log inside the"
        " working tree must be git-ignored, or every verdict dirties the tree; add the directory to"
        " .gitignore, or remove the key",
    }
    problems = [
        f"{key}: wanted {line!r}, got {said.get(key)!r}"
        for key, line in wanted.items()
        if said.get(key) != line
    ]
    problems += [
        f"{key} still names constitution.yaml: {line!r}"
        for key, line in said.items()
        if "constitution.yaml" in line
    ]
    problems += [f"a text is missing: {key}" for key in said if key not in wanted]

    def reads() -> list[str]:
        seen: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prefixed = {"module_prefix": it.prefix}
            kit = json.dumps({**prefixed, "root_policy": "kit.md"})
            (root / "constitution.yaml").write_text(kit, encoding="utf-8")
            alone = load_dials(root)  # only constitution.yaml lies here: this reader opens team.yaml
            seen.append("no file, nothing claimed" if alone is None else f"read {alone.root_policy!r}")
            (root / OTHER_FILE).write_text(json.dumps({**prefixed, "root_policy": "docs/p.md"}), "utf-8")
            both = load_dials(root)  # JSON is YAML: the file the entry point declared wins
            seen.append("nothing" if both is None else f"read {both.root_policy!r}")
            (root / OTHER_FILE).write_text("[unbalanced", encoding="utf-8")
            try:
                load_dials(root)
            except ConfigurationFailure as failure:
                seen.append(failure.broken.render().split(" (", 1)[0])
        return seen

    wanted_reads = [
        "no file, nothing claimed",
        "read 'docs/p.md'",
        "BROKEN: team.yaml is not valid YAML",
    ]
    with identity.declared(team):
        got = reads()
    if got != wanted_reads:
        problems.append(f"the reader: wanted {wanted_reads}, got {got}")
    assert not problems, "; ".join(problems)


@item(
    178,
    "a module's own messages name the declared dials file: its _file() gives it, its source holds no name",
)
def test_module_messages_name_the_declared_file(subject: Subject) -> None:
    """The module's own `messages.py` asks the package for the dials file's name when it builds a message,
    as the shared texts do: with a scope whose identity names `team.yaml` open inside the session's, its
    `_file()` gives `team.yaml`; and no string constant of that file, a docstring aside, contains
    `constitution.yaml`, so that no message of the module can name the file without asking. The module's
    messages are found in the one package beside its entry files that holds a `messages.py`, and imported as
    its tests do."""
    it = shared(subject, "module_messages_name_the_declared_file")
    packages = sorted(
        folder
        for folder in it.h.scripts.iterdir()
        if folder.name != "constitution_layer_kit"
        and (folder / "__init__.py").is_file()
        and (folder / "messages.py").is_file()
    )
    found = [p.name for p in packages]
    assert len(packages) == 1, (
        f"wanted the one package of the module's own messages in {it.h.scripts}: {found}"
    )
    folder = packages[0]
    own = importlib.import_module(f"{folder.name}.messages")
    problems = []
    file_of = getattr(own, "_file", None)
    if not callable(file_of):
        problems.append(f"{folder.name}.messages has no function _file")
    else:
        with identity.declared(replace(identity.current(), dials_file=OTHER_FILE)):
            read = file_of()
        if read != OTHER_FILE:
            problems.append(f"_file() gave {read!r} with {OTHER_FILE!r} declared")
    tree = ast.parse((folder / "messages.py").read_text(encoding="utf-8"))
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }
    problems += [
        f"line {node.lineno} of {folder.name}/messages.py holds a string with constitution.yaml in it"
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
        and "constitution.yaml" in node.value
    ]
    assert not problems, "; ".join(problems)


# The kernel-owned key `module_prefix`: required in every dials file a gate reads, a kebab-case word that
# ends in '-', and the start of the namespace of the module that reads the file. The line its fix gives is
# the part of the module's namespace up to its first '-', `module_prefix: const-` for every module of this
# kit; the lines are typed by hand, the file and the prefix the gate's own.
def no_prefix(it: SharedItems) -> str:
    return (
        f"BROKEN: {it.file}: module_prefix is missing, or is not a kebab-case word that ends in '-'"
        " — fix: a gate tells a module's namespace from a policy's by this prefix, so write module_prefix:"
        f" {it.prefix} as a top-level key, or correct its value to a kebab-case word that ends in '-'"
    )


def outside_prefix(it: SharedItems, prefix: str) -> str:
    """The line `C5.12` is for the module of `it` reading its own file whose `module_prefix` is `prefix`,
    typed by hand."""
    return (
        f"BROKEN: {it.file}: module_prefix '{prefix}' is not the start of this module's namespace"
        f" '{it.ns}' — fix: a gate reads the file of its own modules only, so set module_prefix:"
        f" {it.prefix} if this file is for this module, or check it with a module whose namespace starts"
        f" with '{prefix}'"
    )


@item(179, "C5.11: a dials file that names no module_prefix is a configuration failure, whatever it holds")
def test_dials_prefix_absent(subject: Subject) -> None:
    """The key is required, as the kernel's schema requires it: a file with other keys, an empty file, a
    file of one comment and a file of `{}` each fail the gate under `C5.11`, the exact line to write in
    the fix, and no gate runs on the file until it is added."""
    it = shared(subject, "dials_prefix_absent")
    files = {
        "other keys": "root_policy: docs/policies/root-policy.md\nroot-policy:\n  territory: ['x/**']\n",
        "an empty file": "",
        "one comment": "# nothing here yet\n",
        "an empty mapping": "{}\n",
        "the prefix only in a comment": f"# module_prefix: {it.prefix}\nroot_policy: docs/policies/root.md\n",
        "the prefix as a namespace's key": f"{it.ns}:\n  module_prefix: {it.prefix}\n",
    }
    failed: list[str] = []
    for what, raw in files.items():
        try:  # gathered: one file's red hides no other
            it.broken_as_typed(it.s.gate_on(it.s.valid, raw_dials=raw)[0], no_prefix(it))
        except AssertionError as error:
            failed.append(f"{what}: {error}")
    assert not failed, "; ".join(failed)


@item(180, "C5.11: a module_prefix that is no kebab-case word ending in '-' is the same failure")
def test_dials_prefix_malformed(subject: Subject) -> None:
    """The kernel schema's pattern `^[a-z][a-z0-9]*(-[a-z0-9]+)*-$` held whole: no trailing '-', an
    upper-case letter, a first digit, an underscore, a space, a doubled or a leading '-', a '-' alone,
    a line break after the '-', an empty string, a number, a boolean, a list, a mapping and a null each
    fail under `C5.11`, the line typed by hand, whatever the module's namespace."""
    it = shared(subject, "dials_prefix_malformed")
    word = it.prefix.removesuffix("-")  # the layer's word: `const` for every module of this kit
    values: dict[str, object] = {
        "no trailing '-'": word,
        "a namespace without its '-'": it.ns,
        "an upper-case letter": word.capitalize() + "-",
        "all upper case": word.upper() + "-",
        "a first digit": "1" + it.prefix,
        "an underscore": word + "_x-",
        "a space inside": word + " -",
        "a space after": it.prefix + " ",
        "a space before": " " + it.prefix,
        "a doubled '-'": it.prefix + "-",
        "a leading '-'": "-" + it.prefix,
        "'-' alone": "-",
        "a line break after the '-'": it.prefix + "\n",
        "an empty string": "",
        "a number": 5,
        "a boolean": True,
        "a list": [it.prefix],
        "a mapping": {it.prefix: 1},
        "a null": None,
    }
    failed: list[str] = []
    for what, value in values.items():
        try:  # gathered: one value's red hides no other
            it.broken_as_typed(
                it.s.gate_on(it.s.valid, dials_patch={"module_prefix": value})[0], no_prefix(it)
            )
        except AssertionError as error:
            failed.append(f"{what}: {error}")
    assert not failed, "; ".join(failed)


@item(181, "C5.12: a file whose module_prefix the reading module's namespace does not start with is refused")
def test_dials_prefix_outside(subject: Subject) -> None:
    """A well-formed prefix that is not the start of the namespace of the module that reads the file — the
    file of another layer, a longer word than the namespace's own first part, a shorter word that is no
    start of it — fails the gate under `C5.12`, the line typed by hand with the prefix as the file gives
    it; a module reads the file of its own modules only."""
    it = shared(subject, "dials_prefix_outside")
    word = it.prefix.removesuffix("-")
    other_layer = "const-" if it.prefix == "know-" else "know-"  # another layer's file
    prefixes = ["other-", other_layer, f"{it.ns}-", "c-", f"{word}-zz-", f"{word[:-1]}-", "a1-b2-"]
    failed: list[str] = []
    for prefix in prefixes:
        try:  # gathered: one prefix's red hides no other
            result = it.s.gate_on(it.s.valid, dials_patch={"module_prefix": prefix})[0]
            it.broken_as_typed(result, outside_prefix(it, prefix))
        except AssertionError as error:
            failed.append(f"{prefix}: {error}")
    assert not failed, "; ".join(failed)


# A kit of another layer reads its own file: one process of a gate named `know-check` or `know-sub-check`
# whose identity names the file `layer.yaml`, in a process of its own as a gate runs. The program prints, as
# one JSON object, what the dials reader gave or the configuration failure it raised.
LAYER_PROGRAM = (
    "import json, sys\n"
    "from pathlib import Path\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from constitution_layer_kit import identity\n"
    "from constitution_layer_kit.dials import load_dials\n"
    "from constitution_layer_kit.errors import ConfigurationFailure\n"
    "from constitution_layer_kit.model import KERNEL_KEYS\n"
    "namespace, text, folder = sys.argv[2:5]\n"
    "who = identity.Identity(namespace, 'check', Path('.'), 'layer.yaml', KERNEL_KEYS)\n"
    "Path(folder, 'layer.yaml').write_text(text, encoding='utf-8')\n"
    "with identity.declared(who):\n"
    "    try:\n"
    "        dials = load_dials(Path(folder))\n"
    "    except ConfigurationFailure as failure:\n"
    "        print(json.dumps({'broken': failure.broken.render()}))\n"
    "    else:\n"
    "        print(json.dumps({'prefix': dials.module_prefix, 'own': dict(dials.own),\n"
    "                          'namespaces': {k: list(v.territory) for k, v in dials.namespaces.items()}}))\n"
)
LAYER_FILE = """\
module_prefix: know-
root_policy: docs/policies/root-policy.md
know-check:
  severity: warn
know-odd: 5
know-loose:
  territory: not a list
know-kept:
  territory: ["a/**"]
notes-policy:
  territory: ["docs/**"]
"""


@item(182, "the prefix is the file's own: the reader names none, and reads a namespace by the one declared")
def test_dials_prefix_is_the_files(subject: Subject) -> None:
    """A gate of another kit, named `know-check`, reads `layer.yaml` with `module_prefix: know-`: the
    prefix is read as the file gives it, a key that starts with it and holds a mapping is a module's, its
    territory kept when well formed and empty otherwise, a key that starts with it and holds no mapping is
    ignored, and a key that starts with `const-` is nothing special there — it must be a mapping, as a
    policy's namespace must. A longer prefix, `know-sub-`, serves a gate named `know-sub-check`. The
    fix of `C5.11` and the line of `C5.12` take the prefix from the reading module's namespace, and the
    source of the shared package says `const-` nowhere, so that no prefix of this kit is built in."""
    it = shared(subject, "dials_prefix_is_the_files")

    def read(namespace: str, text: str) -> object:
        folder = it.h.scratch_dir()
        done = subprocess.run(
            [sys.executable, "-c", LAYER_PROGRAM, str(SHARED), namespace, text, str(folder)],
            capture_output=True,
            text=True,
            check=False,
        )
        return json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip()[-300:]

    def no_prefix(fix_word: str) -> dict[str, str]:
        """`C5.11` for the file `layer.yaml`, the line to write being `module_prefix: {fix_word}`."""
        return {
            "broken": "BROKEN: layer.yaml: module_prefix is missing, or is not a kebab-case word that ends in"
            " '-' — fix: a gate tells a module's namespace from a policy's by this prefix, so write"
            f" module_prefix: {fix_word} as a top-level key, or correct its value to a kebab-case word that"
            " ends in '-'"
        }

    sub_file = (
        "module_prefix: know-sub-\nknow-sub-check:\n  severity: block\nknow-sub-a: 7\n"
        "know-sub-b:\n  territory: [1]\n"
    )
    cases: dict[str, tuple[object, object]] = {
        "know- file, know-check": (
            read("know-check", LAYER_FILE),
            {
                "prefix": "know-",
                "own": {"severity": "warn"},
                "namespaces": {
                    "know-check": [],
                    "know-loose": [],
                    "know-kept": ["a/**"],
                    "notes-policy": ["docs/**"],
                },
            },
        ),
        "const- is nothing special there": (
            read("know-check", LAYER_FILE + "const-x: 5\n"),
            {
                "broken": "BROKEN: layer.yaml: namespace 'const-x' must be a mapping — fix: write it as"
                " const-x: {territory: [...]}"
            },
        ),
        "a policy's territory is held strictly": (
            read("know-check", LAYER_FILE + "plain-policy:\n  territory: 7\n"),
            {
                "broken": "BROKEN: layer.yaml: plain-policy.territory must be a list of non-empty strings"
                ' — fix: write it as plain-policy: {territory: ["<pattern>", ...]}'
            },
        ),
        "a longer prefix": (
            read("know-sub-check", sub_file),
            {
                "prefix": "know-sub-",
                "own": {"severity": "block"},
                "namespaces": {"know-sub-check": [], "know-sub-b": []},
            },
        ),
        "a longer prefix leaves know-x to the policies": (
            read("know-sub-check", sub_file + "know-x: 7\n"),
            {
                "broken": "BROKEN: layer.yaml: namespace 'know-x' must be a mapping — fix: write it as"
                " know-x: {territory: [...]}"
            },
        ),
        "C5.11 names the reader's own prefix": (
            read("know-check", "root_policy: docs/p.md\n"),
            no_prefix("know-"),
        ),
        "C5.11 names the part up to the first '-'": (
            read("know-sub-check", "module_prefix: Know-\n"),
            no_prefix("know-"),
        ),
        "C5.12 for another layer's file": (
            read("know-check", "module_prefix: const-\n"),
            {
                "broken": "BROKEN: layer.yaml: module_prefix 'const-' is not the start of this module's"
                " namespace 'know-check' — fix: a gate reads the file of its own modules only, so set"
                " module_prefix: know- if this file is for this module, or check it with a module whose"
                " namespace starts with 'const-'"
            },
        ),
        "C5.12 for a prefix longer than the namespace's start": (
            read("know-check", "module_prefix: know-sub-\n"),
            {
                "broken": "BROKEN: layer.yaml: module_prefix 'know-sub-' is not the start of this module's"
                " namespace 'know-check' — fix: a gate reads the file of its own modules only, so set"
                " module_prefix: know- if this file is for this module, or check it with a module whose"
                " namespace starts with 'know-sub-'"
            },
        ),
    }
    problems = [
        f"{what}: wanted {wanted!r}, got {got!r}" for what, (got, wanted) in cases.items() if got != wanted
    ]
    source = Path(inspect.getsourcefile(identity) or "").resolve().parent
    files = sorted(source.glob("*.py"))
    if not files:
        problems.append(f"no source of the shared package found beside {source}")
    problems += [
        f"{path.name} names const-" for path in files if "const-" in path.read_text(encoding="utf-8")
    ]
    assert not problems, "; ".join(problems)


@item(
    183, "under the prefix the file declares, a namespace with no mapping is ignored; any other is a policy's"
)
def test_dials_prefix_namespaces(subject: Subject) -> None:
    """With the gate's own prefix — `module_prefix: const-`, as before this key was read from the file, for
    every module of this kit —: a key that starts with it and holds no mapping, or a mapping with a
    territory of the wrong shape, is another module's business and changes no verdict; a key that does not
    start with it must be a mapping with a territory of non-empty strings, as a policy's namespace must,
    and fails under `C5.4` or `C5.6` in the constitution's file, which holds the policies, each line typed
    by hand. For a gate of another layer the prefixed keys stand in its own file and the others in the
    constitution's."""
    it = shared(subject, "dials_prefix_namespaces")
    plain = it.s.gate_on(it.s.valid)[0]
    failed: list[str] = []
    lenient: dict[str, dict[str, object]] = {
        "no mapping": {f"{it.prefix}zz": 5},
        "a null": {f"{it.prefix}zz": None},
        "a territory that is no list": {f"{it.prefix}zz": {"territory": "not a list"}},
        "a territory of a number": {f"{it.prefix}zz": {"territory": [1]}},
        "the prefix alone": {it.prefix: 5},
    }
    for what, patch in lenient.items():
        got = it.s.gate_on(it.s.valid, dials_patch=patch)[0]
        if (got.code, "BROKEN" in got.stderr) != (plain.code, "BROKEN" in plain.stderr):
            failed.append(f"{what}: exit {got.code}, the plain run exit {plain.code}: {got.stderr[:200]}")
    strict: dict[str, tuple[dict[str, object], str]] = {
        "a key outside the prefix that holds no mapping": (
            {"other-zz": 5},
            "BROKEN: constitution.yaml: namespace 'other-zz' must be a mapping — fix: write it as other-zz:"
            " {territory: [...]}",
        ),
        "a key outside the prefix with a territory that is no list": (
            {"other-zz": {"territory": "x"}},
            "BROKEN: constitution.yaml: other-zz.territory must be a list of non-empty strings — fix: write"
            ' it as other-zz: {territory: ["<pattern>", ...]}',
        ),
        "a key that only contains the prefix": (
            {f"zz-{it.prefix}": 5},
            f"BROKEN: constitution.yaml: namespace 'zz-{it.prefix}' must be a mapping — fix: write it as"
            f" zz-{it.prefix}: {{territory: [...]}}",
        ),
    }
    for what, (patch, line) in strict.items():
        try:  # gathered: one key's red hides no other
            it.broken_as_typed(it.s.gate_on(it.s.valid, dials_patch=patch)[0], line)
        except AssertionError as error:
            failed.append(f"{what}: {error}")
    assert not failed, "; ".join(failed)


@item(184, "C16: the installed release is below the one the entry file requires, through the entry point")
def test_shared_code_too_old(subject: Subject) -> None:
    """A copy of the shared package whose `__version__` is `0.9.0`, first on PYTHONPATH, under the module's
    real entry point: `C16`, typed by hand, naming the version the entry file requires and the one found,
    exit 1, the closing line after it. The entry file alone in a folder of its own, with none of the
    module's packages beside it, gives the same line with the path of its own note: the check comes before
    the import of the module's own package."""
    it = shared(subject, "shared_code_too_old")
    found = "0.9.0"
    stdin = it.payload(it.h.fresh_consumer().root, it.s.valid)
    env = it.release_with(found)
    it.broken_as_typed(it.h.run_gate(stdin, env=env), it.package_too_old(found, it.guide()), "in place")
    alone = it.h.scratch_dir() / "plugin"
    (alone / "scripts").mkdir(parents=True)
    shutil.copy(it.h.entry, alone / "scripts" / it.h.entry.name)
    result = it.h.run_gate(stdin, env=env, command=[sys.executable, str(alone / "scripts" / it.h.entry.name)])
    it.broken_as_typed(result, it.package_too_old(found, alone / "INSTALL.md"), "the entry file alone")


@item(185, "C17: the installed release is of a later major than the one the entry file requires")
def test_shared_code_new_major(subject: Subject) -> None:
    """A copy of the shared package whose `__version__` is the next major above the one the entry file
    requires, `<major + 1>.0.0`, under the module's real entry point: `C17`, typed by hand, naming the
    version the entry file requires, its major and the major found, exit 1, the closing line after it. The
    entry file alone in a folder of its own gives the same line with the path of its own note."""
    it = shared(subject, "shared_code_new_major")
    found = f"{int(entry_requires(it.h.entry).split('.')[0]) + 1}.0.0"
    stdin = it.payload(it.h.fresh_consumer().root, it.s.valid)
    env = it.release_with(found)
    it.broken_as_typed(it.h.run_gate(stdin, env=env), it.module_too_old(found, it.guide()), "in place")
    alone = it.h.scratch_dir() / "plugin"
    (alone / "scripts").mkdir(parents=True)
    shutil.copy(it.h.entry, alone / "scripts" / it.h.entry.name)
    result = it.h.run_gate(stdin, env=env, command=[sys.executable, str(alone / "scripts" / it.h.entry.name)])
    it.broken_as_typed(result, it.module_too_old(found, alone / "INSTALL.md"), "the entry file alone")


@item(186, "an installed release of a later minor or patch of the same major serves the entry file")
def test_shared_code_later_release(subject: Subject) -> None:
    """Copies of the shared package above the release the entry file requires, `M.m.p`, in its major: at
    `M.m.p+1`, `M.m+4.0` and `M.m+10.0`, under the module's real entry point, the last read as a number
    above the second: each run passes what it passes with the release at hand, its green line on stdout and
    no `BROKEN` line, each run gathered so that one version's red hides no other."""
    it = shared(subject, "shared_code_later_release")
    failed: list[str] = []
    major, minor, patch = (int(part) for part in entry_requires(it.h.entry).split("."))
    for found in (f"{major}.{minor}.{patch + 1}", f"{major}.{minor + 4}.0", f"{major}.{minor + 10}.0"):
        result, green = it.valid_run(env=it.release_with(found))
        if result.code != 0 or green not in result.stdout or "BROKEN" in result.stderr:
            failed.append(
                f"{found}: exit {result.code}, stdout {result.stdout.strip()}, stderr {result.stderr.strip()}"
            )
    assert not failed, "; ".join(failed)


@item(187, "a release installed where pip puts it stands behind the shared code of the working tree")
def test_installed_release_behind_the_working_tree(subject: Subject) -> None:
    """A copy of the shared package at the working tree's version, which serves every module, in the
    site-packages of a virtual environment whose python3 comes first on PATH, marked so that importing it
    creates a file. Control: with the harness's own folder left out (`shared=False`), that python3 imports
    the copy and the mark is made, so the copy is where an install puts it and the mark works. Then the
    module's gate, run as the harness runs every gate, passes what it passes with no release installed
    and never imports the copy: the harness puts the working tree's shared code on PYTHONPATH, ahead of
    site-packages, since a fixture that ran an installed release would test no change of the shared
    code."""
    it = shared(subject, "installed_release_behind_the_working_tree")
    env, mark, copy = it.installed_release()
    program = "import constitution_layer_kit as m; print(m.__file__)"
    control = it.h.run_gate("", command=["python3", "-c", program], env=env, shared=False)
    imported = Path(control.stdout.strip()).resolve() if control.stdout.strip() else None
    assert control.code == 0 and imported == copy.resolve() and mark.is_file(), (
        f"the control: python3 without the harness's folder imported {imported} (exit {control.code},"
        f" mark made: {mark.is_file()}), not the copy installed at {copy}: {control.stderr.strip()}"
    )
    mark.unlink()
    result, green = it.valid_run(env=env)
    assert result.code == 0 and green in result.stdout and "BROKEN" not in result.stderr, (
        f"with a release installed: exit {result.code}, stdout {result.stdout.strip()},"
        f" stderr {result.stderr.strip()}"
    )
    assert not mark.exists(), (
        "the gate imported the release installed in site-packages, not the shared code of the working tree"
        " the harness puts on PYTHONPATH"
    )


# A gate of another layer: its identity names its own file, `layer.yaml`, and that file's kernel keys, and it
# reads the constitution part of `constitution.yaml` in a scope of `identity.reading`. The items below open
# their scopes inside the session's, as a gate's run would, and type every line by hand.
LAYER_KEYS = ("module_prefix", "layer_dialect", "layer_owner")
OTHER_LAYER = identity.Identity("know-check", "check", Path("."), "layer.yaml", LAYER_KEYS)


def read_in(folder: Path, name: str, text: str | None, reader: Callable[[Path], object]) -> object:
    """What `reader` gives for `folder` holding `name` with `text` (absent where None): the value read, or
    the line of the configuration failure it raised."""
    if text is not None:
        (folder / name).write_text(text, encoding="utf-8")
    try:
        return reader(folder)
    except ConfigurationFailure as failure:
        return failure.broken.render()


@item(188, "kernel_keys is required, every list holds module_prefix, and reading opens only inside a scope")
def test_kernel_keys_required(subject: Subject) -> None:
    """An identity built without `kernel_keys` is a `TypeError`: no gate reads a file as some layer's it did
    not name. `declared` and `reading` refuse a list without `module_prefix` as the scope opens, a
    `RuntimeError` that names the key and declares nothing; `reading` outside every scope is the defect of
    a caller that declared no gate, and an empty file name is no file."""
    shared(subject, "kernel_keys_required")
    problems: list[str] = []
    try:
        identity.Identity("know-check", "check", Path("."), "layer.yaml")  # type: ignore[call-arg]
        problems.append("an identity without kernel_keys was built")
    except TypeError:
        pass
    before = identity.current()
    no_prefix = replace(OTHER_LAYER, kernel_keys=("layer_dialect",))
    openers: dict[str, Callable[[], object]] = {
        "declared": lambda: identity.declared(no_prefix),
        "reading": lambda: identity.reading("constitution.yaml", ("root_policy",)),
        "reading an empty name": lambda: identity.reading(" ", KERNEL_KEYS),
    }
    for what, opener in openers.items():
        try:
            with opener():  # type: ignore[attr-defined]
                problems.append(f"{what}: a scope opened")
        except RuntimeError as error:
            wanted = "empty name" if "empty" in what else "module_prefix"
            if wanted not in str(error):
                problems.append(f"{what}: the defect does not say '{wanted}': {error}")
        if identity.current() != before:
            problems.append(f"{what}: a refused scope declared something")

    def outside() -> str:
        try:
            with identity.reading("constitution.yaml", KERNEL_KEYS):
                return "a scope opened"
        except RuntimeError as error:
            return str(error)

    got = contextvars.Context().run(outside)
    if got != "the entry point did not declare which gate it is":
        problems.append(f"reading outside every scope: {got}")
    assert not problems, "; ".join(problems)


@item(
    189, "a file of another layer: its listed keys are handed on as read, the constitution's refused, C5.13"
)
def test_layer_file_kernel_keys(subject: Subject) -> None:
    """A gate named `know-check` reads `layer.yaml` with the kernel keys `module_prefix`, `layer_dialect`
    and `layer_owner`: the two layer keys reach `Dials.layer` as YAML read them, whatever their shape, an
    absent one left out; `root_policy` is not read; its own namespace and the prefixed and policy-shaped
    keys are read as in any file. `root_policy` or `territory_dialect` written in that file is `C5.13`, an
    unlisted plain value `C5.4`, and a file that is no mapping `C4b` naming the identity's own keys, each
    line typed by hand."""
    shared(subject, "layer_file_kernel_keys")
    base = (
        "module_prefix: know-\nlayer_dialect: plain\nlayer_owner: [a, b]\n"
        "know-check:\n  severity: warn\nnotes-policy:\n  territory: ['docs/**']\n"
    )

    def dials_of(folder: Path) -> object:
        dials = load_dials(folder)
        assert dials is not None
        territories = {k: list(v.territory) for k, v in dials.namespaces.items()}
        return (dials.root_policy, dict(dials.layer), dict(dials.own), territories)

    def elsewhere(key: str) -> str:
        return (
            f"BROKEN: layer.yaml: {key} is no key of this file — fix: this module's gates read {key} from the"
            " dials file that holds the policies, so a copy here would be ignored or contradict it: remove"
            f" the line, and set {key} in that file"
        )

    read_all = (None, {"layer_dialect": "plain", "layer_owner": ["a", "b"]}, {"severity": "warn"})
    cases: dict[str, tuple[str, object]] = {
        "the layer's keys handed on": (
            base,
            (*read_all, {"know-check": [], "notes-policy": ["docs/**"]}),
        ),
        "an absent layer key is left out": (
            "module_prefix: know-\nknow-check:\n  severity: warn\n",
            (None, {}, {"severity": "warn"}, {"know-check": []}),
        ),
        "root_policy in the layer's file": (base + "root_policy: docs/p.md\n", elsewhere("root_policy")),
        "territory_dialect in the layer's file": (
            base + "territory_dialect: gitignore\n",
            elsewhere("territory_dialect"),
        ),
        "an unlisted plain value": (
            base + "layer_other: 1\n",
            "BROKEN: layer.yaml: namespace 'layer_other' must be a mapping — fix: write it as layer_other:"
            " {territory: [...]}",
        ),
        "a file that is no mapping": (
            "- module_prefix\n",
            "BROKEN: layer.yaml is not a mapping — fix: the file holds top-level keys: module_prefix,"
            " layer_dialect, layer_owner, then one namespace per module",
        ),
    }
    problems: list[str] = []
    with identity.declared(OTHER_LAYER):
        for what, (text, wanted) in cases.items():
            got = read_in(it_folder(subject), "layer.yaml", text, dials_of)
            if got != wanted:
                problems.append(f"{what}: wanted {wanted!r}, got {got!r}")
    assert not problems, "; ".join(problems)


def it_folder(subject: Subject) -> Path:
    """A fresh scratch folder of the subject's harness."""
    return subject.harness.scratch_dir()


@item(
    190, "the constitution part of a file read beside the module's own: no C5.12, every line names that file"
)
def test_kernel_part(subject: Subject) -> None:
    """Inside a `know-check` scope that names `layer.yaml`, a scope of `identity.reading` names
    `constitution.yaml` and the constitution's three kernel keys, and `load_kernel_part` reads that file:
    `root_policy`, the file's own `module_prefix`, `const-`, which is no start of `know-check` and is not
    held to be, and the policy namespaces, a prefixed key that holds a mapping kept as a candidate and one
    that holds none passed over, as in any read; no namespace of `know-check` is read. An absent file is
    None. A missing prefix is `C5.14`, whose fix names no prefix of the reader's; a bad `root_policy`, an
    unsupported dialect, a policy key that holds no mapping and a file that is no mapping are `C5.1`,
    `C5.3`, `C5.4` and `C4b` naming `constitution.yaml`, each line typed by hand. When the scope closes the
    gate's own file holds again."""
    shared(subject, "kernel_part")
    base = (
        "module_prefix: const-\nroot_policy: docs/policies/root.md\n"
        "root-policy:\n  territory: ['docs/policies/**']\n"
        "intent-policy:\n  territory: ['docs/product/**']\n"
        "const-questions:\n  severity: block\nconst-odd: 5\n"
    )

    def part_of(folder: Path) -> object:
        part = load_kernel_part(folder)
        if part is None:
            return None
        return (
            part.root_policy,
            part.module_prefix,
            {k: list(v.territory) for k, v in part.namespaces.items()},
        )

    cases: dict[str, tuple[str | None, object]] = {
        "the constitution part": (
            base,
            (
                "docs/policies/root.md",
                "const-",
                {
                    "root-policy": ["docs/policies/**"],
                    "intent-policy": ["docs/product/**"],
                    "const-questions": [],
                },
            ),
        ),
        "an absent file": (None, None),
        "C5.14": (
            "root_policy: docs/policies/root.md\n",
            "BROKEN: constitution.yaml: module_prefix is missing, or is not a kebab-case word that ends in"
            " '-' — fix: a gate tells a module's namespace from a policy's by this prefix, so write"
            " module_prefix: <the prefix of the modules whose dials this file holds> as a top-level key, or"
            " correct its value to a kebab-case word that ends in '-'",
        ),
        "C5.1": (
            "module_prefix: const-\nroot_policy: /etc/root.md\n",
            "BROKEN: constitution.yaml: root_policy must be a repository-relative path — fix: root_policy:"
            " <path of the root policy, relative to the repository root>",
        ),
        "C5.3": (
            "module_prefix: const-\nterritory_dialect: glob\n",
            "BROKEN: constitution.yaml: territory_dialect 'glob' is not supported by know-check (supports:"
            " gitignore) — fix: set territory_dialect: gitignore, or remove the key",
        ),
        "C5.4": (
            "module_prefix: const-\nknow-check: 5\n",
            "BROKEN: constitution.yaml: namespace 'know-check' must be a mapping — fix: write it as"
            " know-check: {territory: [...]}",
        ),
        "C4b": (
            "- module_prefix\n",
            "BROKEN: constitution.yaml is not a mapping — fix: the file holds top-level keys: module_prefix,"
            " root_policy, and territory_dialect when the dialect is not gitignore, then one namespace per"
            " policy or module",
        ),
    }
    problems: list[str] = []
    with identity.declared(OTHER_LAYER):
        for what, (text, wanted) in cases.items():
            with identity.reading("constitution.yaml", KERNEL_KEYS):
                got = read_in(it_folder(subject), "constitution.yaml", text, part_of)
            if got != wanted:
                problems.append(f"{what}: wanted {wanted!r}, got {got!r}")
        if identity.dials_file() != "layer.yaml" or identity.current().kernel_keys != LAYER_KEYS:
            problems.append(f"after the scope: {identity.dials_file()}, {identity.current().kernel_keys}")
    assert not problems, "; ".join(problems)


@item(191, "a scope of reading keeps the run's mode and its one deadline")
def test_reading_keeps_the_deadline(subject: Subject, monkeypatch: pytest.MonkeyPatch) -> None:
    """A hook run of 10 s opened at the monotonic second 1000, read at 1004: 6 s are left outside and the
    same 6 s inside a scope of `reading`, where the mode is still hook; a scope that started a deadline of
    its own would leave 10. At 1011 the budget is spent inside the scope as outside, `C12.14` naming the
    wait. The clock is the test's, so no wait is timed."""
    shared(subject, "reading_keeps_the_deadline")
    now = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: now[0])  # the clock the declaration reads
    problems: list[str] = []
    with identity.declared(replace(OTHER_LAYER, hook_seconds=10), Mode.HOOK):
        now[0] = 1004.0
        outside = identity.remaining(100, "x")
        with identity.reading("constitution.yaml", KERNEL_KEYS):
            inside, mode = identity.remaining(100, "x"), identity.declared_mode()
            now[0] = 1011.0
            try:
                identity.remaining(100, "git ls-files answered")
                problems.append("a spent budget left time inside the scope")
            except ConfigurationFailure as failure:
                line = failure.broken.render()
                if not line.startswith(
                    "BROKEN: the hook's budget of 10 s is spent before git ls-files answered"
                ):
                    problems.append(f"the spent budget inside the scope: {line}")
    if (outside, inside, mode) != (6.0, 6.0, Mode.HOOK):
        problems.append(f"outside {outside} s, inside {inside} s, mode inside {mode}")
    assert not problems, "; ".join(problems)
