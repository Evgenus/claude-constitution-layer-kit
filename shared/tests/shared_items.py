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
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from const_gate import messages, preflight
from const_gate.model import Broken, Finding
from const_gate.output import ROTATE_AT, log_name
from consumer import ROOT_POLICY
from harness import Assertion, Edit, Harness, Result, Write, broken_first_line, event_json, expect

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


@dataclass(frozen=True)
class Subject:
    harness: Harness
    gate_on: GateOn
    own: OwnPatch  # a patch of the module's namespace that keeps it working
    valid: Write  # a write the gate passes, green with `governed by <governed_by>`
    red: Write  # a write the gate blocks
    red_finding: Finding
    governed_by: str
    territory: Sequence[str]  # the patterns of the policy that governs `valid` and `red`


def shared_assertions(s: Subject, first: int) -> list[Assertion]:  # noqa: C901 — a flat list of small items
    h, ns = s.harness, s.harness.namespace

    def broken(result: Result, failure: Broken) -> tuple[bool, str]:
        ok, evidence = broken_first_line(result, failure.render())
        counted = messages.c11_broken_count() in result.stderr  # a run that examined nothing says so
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
        return broken(s.gate_on(s.valid, raw_dials="- a\n- b\n")[0], messages.c4b_dials_not_mapping())

    def dials_bad_severity() -> tuple[bool, str]:
        return broken(s.gate_on(s.valid, dials_patch=s.own(severity="loud"))[0], messages.c5_severity())

    def dials_own_namespace() -> tuple[bool, str]:
        return broken(s.gate_on(s.valid, dials_patch={ns: "x"})[0], messages.c5_own_namespace_not_mapping())

    def dials_comment_pattern() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, dials_patch={"notes-policy": {"territory": ["#docs/notes/**"]}})
        return broken(result, messages.c5_territory_pattern("notes-policy", "#docs/notes/**"))

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
            (s.own(log_dir="/absolute/logs"), messages.c5_log_dir()),
        ]
        results = [broken(s.gate_on(s.valid, dials_patch=patch)[0], failure) for patch, failure in pairs]
        failed = [evidence for ok, evidence in results if not ok]
        return not failed, "; ".join(failed) or f"{len(pairs)} dial failures, each exit 1 with its own line"

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
            event_json(consumer.root, s.valid), command=[h.sh, str(plugin / "scripts" / h.wrapper.name)]
        )
        first = expect(result, 1, f"BROKEN: {ns} is installed without its shared code", "stderr")
        shared.mkdir()  # an install that left an empty directory behind: importable, and still no code
        result = h.run_gate(
            event_json(consumer.root, s.valid), command=[h.sh, str(plugin / "scripts" / h.wrapper.name)]
        )
        second = expect(result, 1, f"BROKEN: {ns} is installed without its shared code", "stderr")
        return first[0] and second[0], f"link removed: {first[1][:60]}…; empty directory: {second[1][:60]}…"

    def copy_with_links_followed() -> tuple[bool, str]:
        """The plugin's scripts copied the way an install copies them: what the link points at."""
        plugin = h.scratch_dir() / "plugin"
        shutil.copytree(h.scripts, plugin / "scripts", symlinks=False)
        shutil.copy(preflight.requirements_file(), plugin / "requirements.txt")
        result = h.run_gate(
            event_json(h.fresh_consumer().root, Write("README.md", NO_ENVELOPE)),
            command=[h.sh, str(plugin / "scripts" / h.wrapper.name)],
        )
        return expect(result, 0, "0 documents examined", "stdout")

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
        result, _ = s.gate_on(Write("README.md", NO_ENVELOPE), env={"PYTHONIOENCODING": "ascii"})
        return expect(result, 0, "0 documents examined", "stdout")

    def deeply_nested_envelope() -> tuple[bool, str]:
        """Brackets nested past the parser's depth are an unreadable envelope, never a crash that
        lets the write through."""
        text = "---\nid: " + "[" * 600 + "\n---\n"
        result, _ = s.gate_on(Write(s.red.target, text))
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
        target = str(Path(s.valid.target).with_suffix(".txt"))
        return expect(s.gate_on(Write(target, "x"))[0], 0, "0 documents examined", "stdout")

    def relative_path() -> tuple[bool, str]:
        """A relative file_path is resolved against the event's cwd."""
        _, root = s.gate_on(s.valid)  # prepares the consumer; the event below is the one judged
        event = json.loads(event_json(root, s.red))
        event["tool_input"]["file_path"] = s.red.target
        return expect(h.run_gate(json.dumps(event)), 2, s.red_finding.render(), "stderr")

    def outside_any_repository() -> tuple[bool, str]:
        directory = h.scratch_dir()
        event = event_json(directory, Write("loose.md", NO_ENVELOPE))
        result = h.run_gate(event, env={"GIT_CEILING_DIRECTORIES": str(directory.parent)})
        skip = messages.g1_green_skip(messages.g1_skip_no_repo(str(directory / "loose.md")))
        return expect(result, 0, skip, "stdout")

    def no_dials_file() -> tuple[bool, str]:
        consumer = h.fresh_consumer()
        (consumer.root / "constitution.yaml").unlink()
        result = h.run_gate(event_json(consumer.root, s.red))
        skip = messages.g1_green_skip(messages.g1_skip_no_dials(str(consumer.root)))
        return expect(result, 0, skip, "stdout")

    def no_root_policy() -> tuple[bool, str]:
        result, _ = s.gate_on(s.red, raw_dials="notes-policy:\n  territory: ['docs/notes/**']\n")
        return expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_root()), "stdout")

    def byte_order_mark() -> tuple[bool, str]:
        result, _ = s.gate_on(Write(s.valid.target, "\ufeff" + s.valid.text))
        return expect(result, 0, f"governed by {s.governed_by}", "stdout")

    def negated_pattern() -> tuple[bool, str]:
        """A file-level negated pattern takes the file out of the territory."""
        territory = [*s.territory, "!" + s.red.target]
        result, _ = s.gate_on(s.red, dials_patch={s.governed_by: {"territory": territory}})
        return expect(result, 0, "0 documents examined", "stdout")

    def policy_without_id_note() -> tuple[bool, str]:
        result, _ = s.gate_on(s.valid, files={"docs/policies/zz-no-id.md": NO_ENVELOPE})
        return expect(result, 0, messages.n1_note_policy_without_id("docs/policies/zz-no-id.md"), "stdout")

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

    # ---------------------------------------------------------------- the warn channel

    def severity_warn() -> tuple[bool, str]:
        result, _ = s.gate_on(s.red, dials_patch=s.own(severity="warn"))
        if result.code != 0:
            return False, f"warn must let the write through; exit {result.code}: {result.stderr}"
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        ok = (
            s.red_finding.render() in context
            and messages.w1_warn_note() in context
            and payload["systemMessage"] == messages.w1_warn_system(s.red_finding.headline)
        )
        return ok, "exit 0, finding in additionalContext and systemMessage" if ok else f"bad: {payload}"

    # ---------------------------------------------------------------- the output log

    def log_lines(path: Path) -> list[dict[str, str]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def log_in_plugin_data() -> tuple[bool, str]:
        data = h.scratch_dir()
        s.gate_on(s.red, env={"CLAUDE_PLUGIN_DATA": str(data)})
        lines = log_lines(data / log_name())
        line = lines[0]
        ok = (
            set(line) == {"ts", "module", "gate", "mode", "session", "stream", "text"}
            and line["text"] == "RED: " + s.red_finding.headline
            and line["module"] == ns
            and line["stream"] == "stderr"
            and line["session"] == "fixture-session"
        )
        return ok, f"{len(lines)} log lines; first: {line}"

    def log_in_ignored_dir() -> tuple[bool, str]:
        data = h.scratch_dir()
        result, root = s.gate_on(
            s.valid,
            files={".gitignore": ".gate-logs/\n"},
            env={"CLAUDE_PLUGIN_DATA": str(data)},
            dials_patch=s.own(log_dir=".gate-logs"),
        )
        log = root / ".gate-logs" / log_name()
        ok = (
            result.code == 0
            and log.is_file()
            and f"governed by {s.governed_by}" in log_lines(log)[-1]["text"]
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
        return kept and len(log_lines(data / log_name())) == 1, "the old log kept as .1, a new one started"

    def log_failure_keeps_verdict() -> tuple[bool, str]:
        blocker = h.scratch_dir() / "a-file-not-a-directory"
        blocker.write_text("", encoding="utf-8")
        red, _ = s.gate_on(s.red, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
        green, _ = s.gate_on(s.valid, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
        ok = red.code == 2 and green.code == 0
        return ok, f"log location unwritable: red still exits {red.code}, green still exits {green.code}"

    def declared_libraries() -> tuple[bool, str]:
        declared = {
            line.split(">=")[0].split("==")[0].strip()
            for line in preflight.requirements_file().read_text().splitlines()
            if line.strip()
        }
        ok = declared == set(preflight.declared())
        return ok, f"requirements.txt {sorted(declared)} == preflight table {sorted(preflight.declared())}"

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
        ("output log: every printed line lands in the plugin data directory", log_in_plugin_data),
        ("output log: the log_dir dial routes the whole run to a git-ignored directory", log_in_ignored_dir),
        ("output log: a log_dir that git does not ignore is a configuration failure", log_dir_not_ignored),
        ("output log: rotation past the size limit", log_rotates),
        ("output log: a logging failure never changes the verdict", log_failure_keeps_verdict),
        ("declared dependencies: requirements.txt equals the preflight table", declared_libraries),
        ("C5: the module's own namespace given as null", dials_own_namespace_null),
        (
            "C5: root_policy, an empty dialect, a namespace and a territory of the wrong shape, log_dir",
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
        ("a file-level negated pattern takes the file out of the territory", negated_pattern),
        ("a document where policies live with no readable id earns a note", policy_without_id_note),
        ("an Edit with an empty old_string on an existing file is a visible skip", edit_empty_old_string),
    ]
    return [Assertion(first + n, title, check) for n, (title, check) in enumerate(items)]
