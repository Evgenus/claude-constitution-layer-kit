#!/usr/bin/env python3
"""Fixtures of const-meta-types: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number. Exit 0 when every item is green, 2 otherwise.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from harness import (ENTRY, HERE, Assertion, Case, Edit, Result, Write, event_json, fresh_consumer, run_all,
                     run_gate, scratch_dir)

from consumer import ROOT_POLICY, document, envelope
from meta_types_gate import messages, preflight
from meta_types_gate.model import Broken, Finding, Match
from meta_types_gate.output import LOG_NAME, ROTATE_AT

NOTE_A = "docs/notes/a.md"
SHARED = "docs/notes/shared/x.md"
ROOT_TERRITORY = ["docs/policies/**"]
NOTES = Match("notes-policy", "docs/notes/**")
SHARED_POLICY = Match("shared-policy", "docs/notes/shared/**")
NO_ENVELOPE = "# Fixture\n\nNo envelope at all.\n"

# ------------------------------------------------------------------ red → green cases

CASES = [
    Case(1, "F1: a document with no envelope is blocked; with one it passes",
         Write(NOTE_A, NO_ENVELOPE), Write(NOTE_A, envelope("note-a")), messages.f1_no_envelope(NOTE_A)),
    Case(2, "F2: an envelope opened and never closed is blocked",
         Write(NOTE_A, "---\nid: note-a\n\n# Note A\n"), Write(NOTE_A, envelope("note-a")),
         messages.f2_unterminated(NOTE_A)),
    Case(3, "F3: an envelope that is not valid YAML is blocked",
         Write(NOTE_A, "---\nid: [unclosed\n---\n"), Write(NOTE_A, envelope("note-a")),
         messages.f3_invalid_yaml(NOTE_A, "while parsing a flow sequence")),
    Case(4, "F4: invalid id, type and status are blocked in one message",
         Write(NOTE_A, document(id="Note_A", type="spec", title="Note A", status="open")),
         Write(NOTE_A, envelope("note-a")),
         messages.f4_invalid_fields(NOTE_A, [messages.f4_id_not_kebab("Note_A"), messages.f4_type_not_allowed("spec"),
                                             messages.f4_status_not_allowed("open")])),
    Case(5, "F5: an id already carried by another governed document is blocked",
         Write("docs/notes/b.md", envelope("notes-policy")), Write("docs/notes/b.md", envelope("note-b")),
         messages.f5_duplicate_id("docs/notes/b.md", "notes-policy", "docs/policies/notes-policy.md")),
    Case(6, "F6 no policy: a declaration naming no policy is blocked; naming one, path mapping absent, passes",
         Write("loose.md", envelope("loose", policy="ghost-policy")),
         Write("loose.md", envelope("loose", policy="notes-policy")),
         messages.f6_no_such_policy("loose.md", "ghost-policy", ROOT_TERRITORY)),
    Case(7, "F7 multi-policy: two territories and no declaration is blocked; declaring one of them passes",
         Write(SHARED, envelope("shared-x")), Write(SHARED, envelope("shared-x", policy="shared-policy")),
         messages.f7_multi_policy(SHARED, [NOTES, SHARED_POLICY])),
    Case(8, "F8 contradiction: a declaration against the path mapping is blocked; without it passes",
         Write(NOTE_A, envelope("note-a", policy="root-policy")), Write(NOTE_A, envelope("note-a")),
         messages.f8_contradiction(NOTE_A, "root-policy", NOTES, ROOT_TERRITORY)),
    Case(9, "F8 contradiction naming no policy at all: the fix says so instead of pointing nowhere",
         Write(NOTE_A, envelope("note-a", policy="ghost-policy")), Write(NOTE_A, envelope("note-a")),
         messages.f8_contradiction(NOTE_A, "ghost-policy", NOTES, None)),
    Case(10, "F8b contradiction in an overlap: a declaration naming neither claimant is blocked",
         Write(SHARED, envelope("shared-x", policy="root-policy")),
         Write(SHARED, envelope("shared-x", policy="notes-policy")),
         messages.f8b_contradiction_in_overlap(SHARED, "root-policy", [NOTES, SHARED_POLICY])),
    Case(11, "F10: a document where policies live must be current-state",
         Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "task-record")),
         Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "current-state")),
         messages.f10_policy_type("docs/policies/drafts-policy.md", "task-record", ROOT_TERRITORY)),
    Case(12, "F11: the root policy losing its envelope is a blocked write, never a non-blocking failure",
         Write(ROOT_POLICY, NO_ENVELOPE), Write(ROOT_POLICY, envelope("root-policy", "current-state")),
         messages.f11_root_unreadable(ROOT_POLICY, "none")),
    Case(13, "F12: the root policy must stay current-state",
         Write(ROOT_POLICY, envelope("root-policy", "task-record")),
         Write(ROOT_POLICY, envelope("root-policy", "current-state")),
         messages.f12_root_type(ROOT_POLICY, "task-record")),
    Case(14, "F13: the root policy renamed to an id with no namespace is blocked",
         Write(ROOT_POLICY, envelope("renamed-root", "current-state")),
         Write(ROOT_POLICY, envelope("root-policy", "current-state")),
         messages.f13_root_id_orphaned(ROOT_POLICY, "renamed-root")),
    Case(15, "F14: the root policy renamed to a namespace that does not contain it is blocked, not let through",
         Write(ROOT_POLICY, envelope("notes-policy", "current-state")),
         Write(ROOT_POLICY, envelope("root-policy", "current-state")),
         messages.f14_root_breaks_governance(
             ROOT_POLICY, messages.c9_root_outside_own_territory(ROOT_POLICY, ["docs/notes/**"], "notes-policy"))),
    Case(16, "an Edit is judged on the document as it will be after the edit",
         Edit(NOTE_A, "type: non-authoritative\n", ""), Edit(NOTE_A, "# Fixture", "# Fixture, edited"),
         messages.f4_invalid_fields(NOTE_A, [messages.f4_field_missing("type")]),
         setup=[Write(NOTE_A, envelope("note-a"))]),
]

# ------------------------------------------------------------------ assertions


def _gate_on(action: Write | Edit, dials_patch: dict[str, object] | None = None,
             env: dict[str, str] | None = None, raw_dials: str | None = None,
             files: dict[str, str] | None = None, remove: str | None = None) -> tuple[Result, Path]:
    consumer = fresh_consumer()
    if dials_patch is not None:
        consumer.dials.update(dials_patch)
        consumer.build()
    if raw_dials is not None:
        consumer.write("constitution.yaml", raw_dials)
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return run_gate(event_json(consumer.root, action), env=env), consumer.root


def _expect(result: Result, code: int, text: str, where: str = "both") -> tuple[bool, str]:
    haystack = {"stdout": result.stdout, "stderr": result.stderr, "both": result.stdout + result.stderr}[where]
    ok = result.code == code and text in haystack
    return ok, (f"exit {result.code}: {text}" if ok else
                f"wanted exit {code} teaching {text!r}; got exit {result.code}: {haystack.strip()}")


def _broken(result: Result, broken: Broken) -> tuple[bool, str]:
    """A configuration failure: exit 1 — never 2, never 0 — and its line is the FIRST stderr line."""
    first = result.stderr.splitlines()[0] if result.stderr else ""
    ok = result.code == 1 and first == broken.render()
    return ok, (f"exit 1, first stderr line: {first}" if ok else
                f"wanted exit 1 with first line {broken.render()!r}; got exit {result.code}: {result.stderr.strip()}")


def _bin_with(*tools: str) -> str:
    """A PATH directory holding only the named tools, to simulate the absence of the rest."""
    directory = scratch_dir()
    for tool in tools:
        source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert source, tool
        os.symlink(source, directory / tool)
    return str(directory)


VALID = Write(NOTE_A, envelope("note-a"))


def malformed_dials() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, raw_dials="root-policy: [\n")
    return _expect(result, 1, "BROKEN: constitution.yaml is not valid YAML", "stderr")


def dials_not_mapping() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, raw_dials="- a\n- b\n")[0], messages.c4b_dials_not_mapping())


def dials_bad_severity() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, dials_patch={"const-meta-types": {"severity": "loud"}})[0], messages.c5_severity())


def dials_own_namespace() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, dials_patch={"const-meta-types": "x"})[0], messages.c5_own_namespace_not_mapping())


def dials_comment_pattern() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={"notes-policy": {"territory": ["#docs/notes/**"]}})
    return _broken(result, messages.c5_territory_pattern("notes-policy", "#docs/notes/**"))


def dials_unsupported_dialect() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, dials_patch={"territory_dialect": "regex"})[0], messages.c5_dialect_unsupported("regex"))


def root_missing() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, remove=ROOT_POLICY)[0], messages.c6_root_missing(ROOT_POLICY))


def root_without_id() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, files={ROOT_POLICY: NO_ENVELOPE})[0], messages.c7_root_without_id(ROOT_POLICY))


def root_claims_nothing() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, dials_patch={"root-policy": {}})[0], messages.c8_root_claims_nothing("root-policy"))


def root_outside_own_territory() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={"root-policy": {"territory": ["docs/elsewhere/**"]}})
    return _broken(result, messages.c9_root_outside_own_territory(ROOT_POLICY, ["docs/elsewhere/**"], "root-policy"))


def python_absent() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, env={"PATH": _bin_with("dirname")})
    return _expect(result, 1, "BROKEN: const-meta-types needs python3", "stderr")


def python_below_floor() -> tuple[bool, str]:
    search = os.pathsep.join([os.environ.get("PATH", ""), os.defpath])
    for name in ("python3", "python3.11", "python3.10", "python3.9"):
        for directory in search.split(os.pathsep):
            found = shutil.which(name, path=directory)
            if not found:
                continue
            old = subprocess.run([found, "-c", "import sys; print(sys.version_info < (3, 12))"],
                                 capture_output=True, text=True, check=False).stdout.strip()
            if old == "True":
                result = run_gate("{}", command=[found, str(ENTRY)])
                return _expect(result, 1, "BROKEN: const-meta-types needs Python 3.12 or newer", "stderr")
    return True, "NOT EXERCISED: no interpreter below 3.12 on this machine — 0 interpreters examined"


def git_absent() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, env={"PATH": _bin_with("python3", "dirname")})[0], messages.c3_git_missing())


def git_failing() -> tuple[bool, str]:
    """A git that fails for any reason other than "not a repository" is never a green skip."""
    config = scratch_dir() / "gitconfig"
    config.write_text("[broken\n", encoding="utf-8")
    result, _ = _gate_on(VALID, env={"GIT_CONFIG_GLOBAL": str(config)})
    return _expect(result, 1, "BROKEN: git could not answer where the repository is", "stderr")


def library_absent() -> tuple[bool, str]:
    shadow = scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    result, _ = _gate_on(VALID, env={"PYTHONPATH": str(shadow)})
    return _broken(result, messages.c2_library_missing("PyYAML", str(preflight.requirements_file())))


def misinvocation() -> tuple[bool, str]:
    return _expect(run_gate("", args=["--bogus"]), 1, "BROKEN: misinvocation:", "stderr")


def help_is_not_special() -> tuple[bool, str]:
    return _expect(run_gate("", args=["--help"]), 1, "BROKEN: misinvocation:", "stderr")


def unparseable_input() -> tuple[bool, str]:
    return _expect(run_gate("not json"), 1, "BROKEN: hook input is not a JSON object", "stderr")


def malformed_event() -> tuple[bool, str]:
    event = json.dumps({"tool_name": "Write", "tool_input": ["not", "an", "object"]})
    return _broken(run_gate(event), messages.c12_input(messages.detail_tool_input("Write", "file_path")))


def other_tool() -> tuple[bool, str]:
    event = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x.md"}})
    return _expect(run_gate(event), 0, messages.g1_green_skip(messages.g1_skip_no_file("Read")), "stdout")


def scan_missing_path() -> tuple[bool, str]:
    return _broken(run_gate("", args=["--scan", "no-such-directory"]), messages.c12_scan_path("no-such-directory"))


def outside_territory() -> tuple[bool, str]:
    result, _ = _gate_on(Write("README.md", NO_ENVELOPE))
    return _expect(result, 0, messages.g1_green_skip(messages.g1_skip_outside_territory("README.md")), "stdout")


def not_markdown() -> tuple[bool, str]:
    return _expect(_gate_on(Write("docs/notes/a.txt", "x"))[0], 0, "0 documents examined", "stdout")


def void_territory() -> tuple[bool, str]:
    result, _ = _gate_on(Write("docs/ghost/g.md", NO_ENVELOPE), dials_patch={"ghost": {"territory": ["docs/ghost/**"]}})
    return _expect(result, 0, messages.g1_skip_void_territory("docs/ghost/g.md", ["ghost"]), "stdout")


def module_named_policy() -> tuple[bool, str]:
    """A policy is a policy by where it lies, even when its id looks like a module's name."""
    result, _ = _gate_on(Write("style/s.md", NO_ENVELOPE),
                         dials_patch={"const-style": {"territory": ["style/**"]}},
                         files={"docs/policies/const-style.md": envelope("const-style", "current-state")})
    return _expect(result, 2, messages.f1_no_envelope("style/s.md").render(), "stderr")


def negation() -> tuple[bool, str]:
    result, _ = _gate_on(Write("docs/notes/secret.md", NO_ENVELOPE),
                         dials_patch={"notes-policy": {"territory": ["docs/notes/**", "!docs/notes/secret.md"]}})
    return _expect(result, 0, messages.g1_skip_outside_territory("docs/notes/secret.md"), "stdout")


def _warn(files: dict[str, str] | None = None) -> tuple[Result, str]:
    result, _ = _gate_on(Write(NOTE_A, NO_ENVELOPE), dials_patch={"const-meta-types": {"severity": "warn"}}, files=files)
    return result, messages.f1_no_envelope(NOTE_A).headline


def severity_warn() -> tuple[bool, str]:
    result, headline = _warn()
    if result.code != 0:
        return False, f"warn must let the write through; exit {result.code}: {result.stderr}"
    payload = json.loads(result.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    ok = (messages.f1_no_envelope(NOTE_A).render() in context and messages.w1_warn_note() in context
          and payload["systemMessage"] == messages.w1_warn_system(headline))
    return ok, "exit 0, finding in additionalContext and systemMessage" if ok else f"bad payload: {payload}"


def severity_warn_with_note() -> tuple[bool, str]:
    """Under warn, stdout must be one JSON object and nothing else, or the finding reaches nobody."""
    twin = envelope("notes-policy", "current-state")
    result, _ = _warn(files={"docs/policies/zz-twin.md": twin})
    payload = json.loads(result.stdout)             # raises, and so fails, if a note precedes the JSON
    note = messages.n1_note_policy_id_shared("docs/policies/notes-policy.md", "docs/policies/zz-twin.md", "notes-policy")
    ok = result.code == 0 and note in payload["hookSpecificOutput"]["additionalContext"]
    return ok, "stdout parses as one JSON object; the note travels inside additionalContext"


def _scan(bad: bool) -> Result:
    consumer = fresh_consumer()
    consumer.dials.update({"const-meta-types": {"severity": "warn"}, "ghost": {"territory": ["nowhere/**"]}})
    consumer.build()
    consumer.write(NOTE_A, NO_ENVELOPE if bad else envelope("note-a"))
    return run_gate("", args=["--scan", str(consumer.root)])


def scan_red() -> tuple[bool, str]:
    tail = messages.f9_scan_tail(examined=4, scanned=4, policies=3)
    return _expect(_scan(bad=True), 2, messages.f9_count_scan(1, tail), "stdout")


def scan_green() -> tuple[bool, str]:
    result = _scan(bad=False)
    ok, evidence = _expect(result, 0, messages.g1_green_scan(messages.f9_scan_tail(4, 4, 3)), "stdout")
    return ok and messages.n1_note_void_namespace("ghost") in result.stdout, evidence + " + void-namespace note"


def scan_scales() -> tuple[bool, str]:
    """The scan reads each document once: a few hundred documents take seconds, not minutes."""
    consumer = fresh_consumer()
    for n in range(300):
        consumer.write(f"docs/notes/n{n}.md", envelope(f"note-{n}"))
    started = time.monotonic()
    result = run_gate("", args=["--scan", str(consumer.root)])
    elapsed = time.monotonic() - started
    ok = result.code == 0 and "303 governed document(s) examined" in result.stdout and elapsed < 15
    return ok, f"303 documents examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


def _log_lines(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def log_in_plugin_data() -> tuple[bool, str]:
    data = scratch_dir()
    _gate_on(Write(NOTE_A, NO_ENVELOPE), env={"CLAUDE_PLUGIN_DATA": str(data)})
    lines = _log_lines(data / LOG_NAME)
    first = lines[0]
    ok = (set(first) == {"ts", "module", "gate", "mode", "session", "stream", "text"}
          and first["text"] == "RED: " + messages.f1_no_envelope(NOTE_A).headline
          and first["stream"] == "stderr" and first["session"] == "fixture-session")
    return ok, f"{len(lines)} log lines; first: {first}"


def log_in_ignored_dir() -> tuple[bool, str]:
    data = scratch_dir()
    result, root = _gate_on(VALID, files={".gitignore": ".gate-logs/\n"}, env={"CLAUDE_PLUGIN_DATA": str(data)},
                            dials_patch={"const-meta-types": {"log_dir": ".gate-logs"}})
    log = root / ".gate-logs" / LOG_NAME
    ok = (result.code == 0 and log.is_file() and "governed by notes-policy" in _log_lines(log)[-1]["text"]
          and not (data / LOG_NAME).exists())
    return ok, f"exit {result.code}; the whole run logged inside the repository, nothing split off to the data directory"


def log_dir_not_ignored() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={"const-meta-types": {"log_dir": "gate-logs"}})
    return _broken(result, messages.c13_log_dir_not_ignored("gate-logs"))


def log_rotates() -> tuple[bool, str]:
    data = scratch_dir()
    (data / LOG_NAME).write_text("x" * (ROTATE_AT + 1), encoding="utf-8")
    _gate_on(VALID, env={"CLAUDE_PLUGIN_DATA": str(data)})
    ok = (data / (LOG_NAME + ".1")).stat().st_size > ROTATE_AT and len(_log_lines(data / LOG_NAME)) == 1
    return ok, "a log past the size limit is kept as .1 and a new one started"


def log_failure_keeps_verdict() -> tuple[bool, str]:
    blocker = scratch_dir() / "a-file-not-a-directory"
    blocker.write_text("", encoding="utf-8")
    red, _ = _gate_on(Write(NOTE_A, NO_ENVELOPE), env={"CLAUDE_PLUGIN_DATA": str(blocker)})
    green, _ = _gate_on(VALID, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
    ok = red.code == 2 and green.code == 0
    return ok, f"log location unwritable: red still exits {red.code}, green still exits {green.code}"


def declared_libraries() -> tuple[bool, str]:
    declared = {line.split(">=")[0].split("==")[0].strip()
                for line in (HERE.parent / "requirements.txt").read_text().splitlines() if line.strip()}
    ok = declared == set(preflight.DECLARED)
    return ok, f"requirements.txt {sorted(declared)} == preflight table {sorted(preflight.DECLARED)}"


def message_shape() -> tuple[bool, str]:
    built = [case.expect for case in CASES]
    ok = all(isinstance(f, Finding) and f.key and f.headline and f.why and f.fix for f in built)
    return ok, f"{len(built)} findings examined, each with what / why / fix"


ASSERTIONS = [
    Assertion(17, "exit-code split: a malformed dials file exits 1, never 2, never 0", malformed_dials),
    Assertion(18, "C4b: a dials file that is not a mapping", dials_not_mapping),
    Assertion(19, "C5: a severity outside block | warn", dials_bad_severity),
    Assertion(20, "C5: this module's own namespace must be a mapping, and the fix teaches its dials", dials_own_namespace),
    Assertion(21, "C5: a territory pattern git would read as a comment", dials_comment_pattern),
    Assertion(22, "C5: an unsupported territory dialect", dials_unsupported_dialect),
    Assertion(23, "C6: the root policy file is missing", root_missing),
    Assertion(24, "C7: the root policy on disk has no readable id", root_without_id),
    Assertion(25, "C8: the root policy claims no territory", root_claims_nothing),
    Assertion(26, "C9: the root policy lies outside its own territory", root_outside_own_territory),
    Assertion(27, "absence: python3", python_absent),
    Assertion(28, "absence: an interpreter below the floor", python_below_floor),
    Assertion(29, "absence: git", git_absent),
    Assertion(30, "absence: a declared library (PyYAML)", library_absent),
    Assertion(31, "a failing git is a configuration failure, never a green skip", git_failing),
    Assertion(32, "misinvocation exits 1: argparse's exit 2 is overridden", misinvocation),
    Assertion(33, "--help is a misinvocation like any other: no exit path past the guard and the log", help_is_not_special),
    Assertion(34, "unparseable hook input is a configuration failure, not an empty event", unparseable_input),
    Assertion(35, "a Write event without its documented fields is a configuration failure", malformed_event),
    Assertion(36, "an event for a tool this gate does not judge is a visible skip", other_tool),
    Assertion(37, "--scan on a path that does not exist is a configuration failure", scan_missing_path),
    Assertion(38, "examined count: outside claimed territory prints 0 and exits 0", outside_territory),
    Assertion(39, "examined count: a non-Markdown file prints 0 and exits 0", not_markdown),
    Assertion(40, "a territory with no policy behind it claims nothing: a visible skip", void_territory),
    Assertion(41, "a policy whose id looks like a module's name still governs its territory", module_named_policy),
    Assertion(42, "a file-level negated pattern excludes the file from the territory", negation),
    Assertion(43, "severity warn: exit 0 with the whole finding as JSON for the model and the user", severity_warn),
    Assertion(44, "severity warn with a note: stdout stays one JSON object", severity_warn_with_note),
    Assertion(45, "scan: the finding with counts, exit 2, ignoring severity warn", scan_red),
    Assertion(46, "scan: green with counts, and a note per void namespace", scan_green),
    Assertion(47, "scan: 300 documents in seconds (each document read once)", scan_scales),
    Assertion(48, "output log: every printed line lands in the plugin data directory", log_in_plugin_data),
    Assertion(49, "output log: the log_dir dial routes the whole run to a git-ignored directory", log_in_ignored_dir),
    Assertion(50, "output log: a log_dir that git does not ignore is a configuration failure", log_dir_not_ignored),
    Assertion(51, "output log: rotation past the size limit", log_rotates),
    Assertion(52, "output log: a logging failure never changes the verdict", log_failure_keeps_verdict),
    Assertion(53, "declared dependencies: requirements.txt equals the preflight table", declared_libraries),
    Assertion(54, "message shape: every taught finding has what, why and fix", message_shape),
]

if __name__ == "__main__":
    sys.exit(run_all(CASES, ASSERTIONS))
