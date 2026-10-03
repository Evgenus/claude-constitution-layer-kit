"""The acceptance items of what every gate shares — the exit-code split, the absence of each
external tool, hook input, paths, the warn channel, the output log — written once and run by
each module's runner through that module's real entry point.

A module hands over a Subject: its harness, a function that runs its gate on a prepared
consumer, one write it passes and one it blocks. Items are numbered from the number the
module gives, so a module's own items and the shared ones never collide.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from const_gate import messages, pipeline, preflight
from const_gate.model import DIALECT, Broken, Finding, SharedKey
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
        return broken(s.gate_on(s.valid, dials_patch=s.own(severity="loud"))[0], messages.c5_severity())

    def dials_own_namespace() -> tuple[bool, str]:
        return broken(s.gate_on(s.valid, dials_patch={ns: "x"})[0], messages.c5_own_namespace_not_mapping())

    def dials_comment_pattern() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"notes-policy": {"territory": ["#docs/notes/**"]}})
        line = (  # typed by hand: the dial's whole path, then the pattern in single quotes
            "BROKEN: constitution.yaml: notes-policy.territory holds a pattern git would not read as one:"
            " '#docs/notes/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a line"
            " break; escape or remove it"
        )
        return broken_as_typed(result, line)

    def dials_unsupported_dialect() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"territory_dialect": "regex"})
        return broken(result, messages.c5_dialect_unsupported("regex"))

    def dials_own_namespace_null() -> tuple[bool, str]:
        return broken(s.gate_on(s.valid, dials_patch={ns: None})[0], messages.c5_own_namespace_not_mapping())

    def dials_other_pairs() -> tuple[bool, str]:
        pairs: list[tuple[dict[str, object], Broken]] = [
            ({"root_policy": "/absolute/root.md"}, messages.c5_root_policy_path()),
            ({"territory_dialect": ""}, messages.c5_dialect_empty()),
            ({"notes-policy": "docs/notes/**"}, messages.c5_namespace_not_mapping("notes-policy")),
            ({"notes-policy": {"territory": "docs/notes/**"}}, messages.c5_territory_shape("notes-policy")),
            # a list holding a blank string is no list of non-empty strings
            (
                {"notes-policy": {"territory": ["docs/notes/**", " "]}},
                messages.c5_territory_shape("notes-policy"),
            ),
            (s.own(log_dir="/absolute/logs"), messages.c5_log_dir()),
            # a path that leaves the repository by `..`, written plain or after a step down
            ({"root_policy": "../root.md"}, messages.c5_root_policy_path()),
            ({"root_policy": "docs/../../root.md"}, messages.c5_root_policy_path()),
            (s.own(log_dir="../logs"), messages.c5_log_dir()),
            (s.own(log_dir="logs/../../logs"), messages.c5_log_dir()),
            ({"root_policy": " "}, messages.c5_root_policy_path()),
        ]
        results = [broken(s.gate_on(s.valid, dials_patch=patch)[0], failure) for patch, failure in pairs]
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
        search = os.pathsep.join([os.environ.get("PATH", ""), os.defpath])
        for name in ("python3", "python3.11", "python3.10", "python3.9"):
            for directory in search.split(os.pathsep):
                found = shutil.which(name, path=directory)
                if not found:
                    continue
                old = subprocess.run(
                    [found, "-c", "import sys; print(sys.version_info < (3, 12))"],
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.strip()
                if old == "True":
                    result = h.run_gate("{}", command=[found, str(h.entry)])
                    return expect(result, 1, f"BROKEN: {ns} needs Python 3.12 or newer", "stderr")
        return True, "NOT EXERCISED: no interpreter below 3.12 on this machine — 0 interpreters examined"

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
        return broken(h.run_gate("[1, 2]"), messages.c12_input(messages.detail_not_an_object()))

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
        return expect(result, 2, messages.detail_nested_too_deeply(), "stderr")

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
        return expect(result, 0, skip, "stdout")

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
        return expect(result, 0, skip, "stdout")

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
        return expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_root()), "stdout")

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
        result, _ = s.gate_on(s.valid, files={"docs/policies/zz-no-id.md": NO_ENVELOPE})
        said = Result(result.code, green_said(result), result.stderr)
        return expect(said, 0, messages.n1_note_policy_without_id("docs/policies/zz-no-id.md"), "stdout")

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
                and answer["systemMessage"].startswith(messages.w1_warn_stop("").rstrip())
            )
            return (
                ok,
                "exit 0, the whole finding in systemMessage and nothing else" if ok else f"bad: {answer}",
            )
        context = answer["hookSpecificOutput"]["additionalContext"]
        ok = (
            s.red_finding.render() in context
            and messages.w1_warn_note() in context
            and answer["systemMessage"] == messages.w1_warn_system(s.red_finding.headline)
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
        trigger: str, code: int, line: Callable[[Path], str], through_scan: bool = False
    ) -> tuple[bool, str]:
        """A git first on PATH that exits `code` when one of its arguments is `trigger`, and hands every
        other call to the real git — so the gate gets as far as that one call. `through_scan`: the
        failing git is met by the scan on the prepared consumer, for a gate whose hook never makes
        the call."""
        real = shutil.which("git")
        if real is None:
            return False, "no git on PATH: the failing git hands every other call to the real one"
        directory = h.scratch_dir()
        fake = directory / "git"
        fake.write_text(
            "#!/bin/sh\n"
            'for a in "$@"; do\n'
            f'  if [ "$a" = {shlex.quote(trigger)} ]; then\n'
            f"    echo {shlex.quote(f'fatal: simulated {trigger} failure')} >&2\n"
            f"    exit {code}\n"
            "  fi\n"
            "done\n"
            f'exec {shlex.quote(real)} "$@"\n',
            encoding="utf-8",
        )
        fake.chmod(0o755)
        env = {"PATH": str(directory) + os.pathsep + os.environ.get("PATH", os.defpath)}
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
        """Exit 128: check-ignore's exit 1 means no path matched, which is no failure."""
        return git_failing_at(
            "--no-index",
            128,
            lambda _: (
                "BROKEN: git check-ignore failed: fatal: simulated --no-index failure — fix: territory"
                " patterns must be gitignore syntax; check constitution.yaml"
            ),
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
        return ok, (
            f"exit 1; the failure on one line, {len(result.stderr)} characters in all"
            if ok
            else f"exit {result.code}; {len(lines)} lines; {result.stderr[:300]}"
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
            " a line break; escape or remove it"
        )
        lines = result.stderr.splitlines()
        one_line = len(lines) == 1 + len(s.closing.splitlines())
        ok = result.code == 1 and one_line and lines[0] == first and len(result.stderr) < 2_000
        return ok, (
            f"exit 1; {ns}.{dial.path} named whole, on one line, {len(result.stderr)} characters in all"
            if ok
            else f"exit {result.code}; {len(lines)} lines; {result.stderr[:300]}"
        )

    items: list[tuple[str, Callable[[], tuple[bool, str]]]] = [
        ("exit-code split: a malformed dials file exits 1, never 2, never 0", malformed_dials),
        ("C4b: a dials file that is not a mapping", dials_not_mapping),
        ("C5: a severity outside block | warn", dials_bad_severity),
        ("C5: the module's own namespace must be a mapping", dials_own_namespace),
        ("C5: a territory pattern git would read as a comment", dials_comment_pattern),
        ("C5: an unsupported territory dialect", dials_unsupported_dialect),
        ("C6: the root policy file is missing", root_missing),
        ("C7: the root policy on disk has no readable id", root_without_id),
        ("C8: the root policy claims no territory", root_claims_nothing),
        ("C9: the root policy lies outside its own territory", root_outside_own_territory),
        ("absence: python3", python_absent),
        ("absence: an interpreter below the floor", python_below_floor),
        ("absence: git", git_absent),
        ("absence: a declared library (PyYAML)", library_absent),
        (
            "absence: the shared code, as an install that dropped its link would leave the plugin",
            shared_code_absent,
        ),
        ("a failing git is a configuration failure, never a green skip", git_failing),
        ("misinvocation exits 1: argparse's exit 2 is overridden", misinvocation),
        (
            "--help is a misinvocation like any other: no exit path past the guard and the log",
            help_is_not_special,
        ),
        ("an abbreviated flag is a misinvocation, not a scan logged as a hook run", abbreviated_flag),
        ("unparseable hook input is a configuration failure, not an empty event", unparseable_input),
        ("hook input that is JSON but no object says so", input_not_an_object),
        ("a Write event without its documented fields is a configuration failure", malformed_event),
        ("an event for a tool the gates do not judge is a visible skip", other_tool),
        ("--scan on a path that does not exist is a configuration failure", scan_missing_path),
        ("examined count: a non-Markdown file prints 0 and exits 0", not_markdown),
        ("a relative file_path is resolved against the event's cwd", relative_path),
        ("a file outside any git repository is a visible skip", outside_any_repository),
        ("no dials file: a visible skip", no_dials_file),
        ("a dials file with no root_policy: a visible skip", no_root_policy),
        ("an Edit whose old_string is absent is a visible skip; the tool reports it", edit_unappliable),
        ("severity warn: exit 0 with the whole finding as JSON for the model and the user", severity_warn),
        ("output log: each print is one record, in the plugin data directory", log_in_plugin_data),
        ("output log: the log_dir dial routes the whole run to a git-ignored directory", log_in_ignored_dir),
        ("output log: a log_dir that git does not ignore is a configuration failure", log_dir_not_ignored),
        ("output log: rotation past the size limit", log_rotates),
        ("output log: a logging failure never changes the verdict", log_failure_keeps_verdict),
        ("declared dependencies: requirements.txt equals the preflight table", declared_libraries),
        ("C5: the module's own namespace given as null", dials_own_namespace_null),
        (
            "C5: root_policy, an empty dialect, a namespace and a territory of the wrong shape, log_dir;"
            " the dials written the long way, and the dialect written out, read as plain",
            dials_other_pairs,
        ),
        (
            "absence, the other way round: the scripts copied with links followed run",
            copy_with_links_followed,
        ),
        (
            "not fail-open: an unexpected exception exits 1, BROKEN first, the traceback after",
            unexpected_failure,
        ),
        ("an Edit event without its documented fields is a configuration failure", edit_without_fields),
        ("a stdout that cannot encode the dash still carries the count line", stdout_cannot_encode),
        (
            "an envelope nested past the parser's depth is blocked, never a crash that lets it through",
            deeply_nested_envelope,
        ),
        ("--scan outside any repository is a configuration failure", scan_outside_repository),
        ("--scan=DIR and a scan from a subdirectory examine the same repository", scan_forms),
        ("a byte-order mark before the envelope is not part of it", byte_order_mark),
        ("a file-level negated pattern takes the file out, and the skip names why", negated_pattern),
        ("a document where policies live with no readable id earns a note", policy_without_id_note),
        ("an Edit with an empty old_string on an existing file is a visible skip", edit_empty_old_string),
        (
            "an echoed value a page long is cut, and the cut is said: the verdict stays a message",
            long_value_is_cut,
        ),
        ("C12.1: git failing to list the files is a configuration failure", ls_files_fails),
        ("C12.2: git failing to make the scratch repository is a configuration failure", init_fails),
        (
            "C12.3: git check-ignore failing, not merely matching nothing, is a configuration failure",
            check_ignore_fails,
        ),
        ("C12.7: a dials file the process cannot read is a configuration failure", dials_unreadable),
        (
            "C12.10: a document git lists and the scan cannot read is a configuration failure",
            document_unreadable,
        ),
        (
            "C4: a dials file that is not UTF-8 is C4, its line and column named, never a defect of the gate",
            dials_not_utf8,
        ),
        (
            "C12.10: a file where policies live that nobody can read is a configuration failure, never a"
            " policy with no id",
            policy_unreadable,
        ),
        (
            "a green hook run with notes hands them to the model as JSON, one without notes stays plain",
            notes_reach_the_model,
        ),
        (
            "C5: a key with a line break, a page long, in the module's namespace is one line, cut",
            unknown_dial_is_one_line,
        ),
        (
            "C5.7: a pattern git would misread in a dial of the module's own is one line, naming it",
            pattern_in_own_dial_is_one_line,
        ),
        ("a file named just .md is Markdown to the hook as to the scan", file_named_md),
        (
            "the findings shown after a write: the first always, then what fits, never more than most",
            cap_keeps_the_first,
        ),
    ]
    # Numbers are positions in the whole list, so an item keeps its number in every module; a gate
    # that resolves no policy leaves gaps where the items about policies stand.
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
    return [
        Assertion(first + n, title, check)
        for n, (title, check) in enumerate(items)
        if (s.resolves_policies or check not in about_policies)
        and (s.judges_envelopes or check is not deeply_nested_envelope)
        and (s.event_driven or check not in about_events)
        and (not no_file or check not in about_files)
        and (not no_file or check not in about_listing)
        and (not s.scan_only or check not in about_hooks)
        and (s.long_value is not None or check is not long_value_is_cut)
        and (s.pattern_dial is not None or check is not pattern_in_own_dial_is_one_line)
        and (s.noted is not None or check is not notes_reach_the_model)
    ]
