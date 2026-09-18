#!/usr/bin/env python3
"""Fixtures of const-meta-types: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Items are
numbered as in the module document's acceptance section. Exit 0 when every item is green,
2 otherwise.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from harness import (ENTRY, HERE, Assertion, Case, Edit, Result, Write, event_json, fresh_consumer, run_all,
                     run_gate)

from consumer import ROOT_POLICY, document, envelope
from meta_types_gate import messages, preflight
from meta_types_gate.model import Finding, Match

NOTE_A = "docs/notes/a.md"
SHARED = "docs/notes/shared/x.md"
ROOT_TERRITORY = ["docs/policies/**"]

# ------------------------------------------------------------------ red → green cases

CASES = [
    Case(1, "a document with no envelope is blocked; with one it passes",
         Write(NOTE_A, "# Note A\n\nNo envelope at all.\n"), Write(NOTE_A, envelope("note-a")),
         messages.f1_no_envelope(NOTE_A)),
    Case(2, "an envelope opened and never closed is blocked",
         Write(NOTE_A, "---\nid: note-a\n\n# Note A\n"), Write(NOTE_A, envelope("note-a")),
         messages.f2_unterminated(NOTE_A)),
    Case(3, "invalid id, type and status are blocked in one message",
         Write(NOTE_A, document(id="Note_A", type="spec", title="Note A", status="open")),
         Write(NOTE_A, envelope("note-a")),
         messages.f4_invalid_fields(NOTE_A, [messages.id_not_kebab("Note_A"), messages.type_not_allowed("spec"),
                                             messages.status_not_allowed("open")])),
    Case(4, "an id already carried by another governed document is blocked",
         Write("docs/notes/b.md", envelope("notes-policy")), Write("docs/notes/b.md", envelope("note-b")),
         messages.f5_duplicate_id("docs/notes/b.md", "notes-policy", "docs/policies/notes-policy.md")),
    Case(5, "no policy: a declaration naming no policy is blocked; naming one, path mapping absent, passes",
         Write("loose.md", envelope("loose", policy="ghost-policy")),
         Write("loose.md", envelope("loose", policy="notes-policy")),
         messages.f6_no_such_policy("loose.md", "ghost-policy", ROOT_TERRITORY)),
    Case(6, "multi-policy: two territories and no declaration is blocked; declaring one of them passes",
         Write(SHARED, envelope("shared-x")), Write(SHARED, envelope("shared-x", policy="shared-policy")),
         messages.f7_multi_policy(SHARED, [Match("notes-policy", "docs/notes/**"),
                                           Match("shared-policy", "docs/notes/shared/**")])),
    Case(7, "contradiction: a declaration against the path mapping is blocked; without it passes",
         Write(NOTE_A, envelope("note-a", policy="root-policy")), Write(NOTE_A, envelope("note-a")),
         messages.f8_contradiction(NOTE_A, "root-policy", Match("notes-policy", "docs/notes/**"), ROOT_TERRITORY)),
    Case(8, "contradiction in an overlap: a declaration naming neither claimant is blocked",
         Write(SHARED, envelope("shared-x", policy="root-policy")),
         Write(SHARED, envelope("shared-x", policy="notes-policy")),
         messages.f8b_contradiction_in_overlap(SHARED, "root-policy",
                                               [Match("notes-policy", "docs/notes/**"),
                                                Match("shared-policy", "docs/notes/shared/**")])),
    Case(9, "a document where policies live must be current-state",
         Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "task-record")),
         Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "current-state")),
         messages.f10_policy_type("docs/policies/drafts-policy.md", "task-record", ROOT_TERRITORY)),
    Case(10, "the root policy losing its envelope is a blocked write, never a non-blocking failure",
         Write(ROOT_POLICY, "# Root policy\n\nEnvelope deleted by mistake.\n"),
         Write(ROOT_POLICY, envelope("root-policy", "current-state")),
         messages.f11_root_unreadable(ROOT_POLICY, "none")),
    Case(11, "an Edit is judged on the document as it will be after the edit",
         Edit(NOTE_A, "type: non-authoritative\n", ""), Edit(NOTE_A, "# Fixture", "# Fixture, edited"),
         messages.f4_invalid_fields(NOTE_A, [messages.field_missing("type")]),
         setup=[Write(NOTE_A, envelope("note-a"))]),
]

# ------------------------------------------------------------------ assertions


def _gate_on(action: Write | Edit, dials_patch: dict[str, object] | None = None,
             env: dict[str, str] | None = None, raw_dials: str | None = None,
             ignore: str | None = None) -> tuple[Result, Path]:
    tmp = tempfile.mkdtemp()
    consumer = fresh_consumer(tmp)
    if dials_patch is not None:
        consumer.dials.update(dials_patch)
        consumer.build()
    if raw_dials is not None:
        consumer.write("constitution.yaml", raw_dials)
    if ignore is not None:
        consumer.write(".gitignore", ignore)
    return run_gate(event_json(consumer.root, action), env=env), consumer.root


def _expect(result: Result, code: int, text: str, where: str = "both") -> tuple[bool, str]:
    haystack = {"stdout": result.stdout, "stderr": result.stderr, "both": result.stdout + result.stderr}[where]
    ok = result.code == code and text in haystack
    return ok, (f"exit {result.code}: {text}" if ok else
                f"wanted exit {code} teaching {text!r}; got exit {result.code}: {haystack.strip()}")


def _bin_with(*tools: str) -> str:
    """A PATH directory holding only the named tools, to simulate the absence of the rest."""
    directory = tempfile.mkdtemp()
    for tool in tools:
        source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert source, tool
        os.symlink(source, os.path.join(directory, tool))
    return directory


def malformed_dials() -> tuple[bool, str]:
    result, _ = _gate_on(Write(NOTE_A, envelope("note-a")), raw_dials="root-policy: [\n")
    return _expect(result, 1, "BROKEN: constitution.yaml is not valid YAML", "stderr")


def python_absent() -> tuple[bool, str]:
    result, _ = _gate_on(Write(NOTE_A, "x"), env={"PATH": _bin_with("dirname")})
    return _expect(result, 1, "BROKEN: const-meta-types needs python3", "stderr")


def python_below_floor() -> tuple[bool, str]:
    for candidate in ("/usr/bin/python3", "python3.11", "python3.10", "python3.9"):
        found = shutil.which(candidate)
        if not found:
            continue
        version = subprocess.run([found, "-c", "import sys; print(sys.version_info >= (3, 12))"],
                                 capture_output=True, text=True, check=False).stdout.strip()
        if version == "False":
            result = run_gate("{}", command=[found, str(ENTRY)])
            return _expect(result, 1, "BROKEN: const-meta-types needs Python 3.12 or newer", "stderr")
    return True, "NOT EXERCISED: no interpreter below 3.12 on this machine — 0 interpreters examined"


def git_absent() -> tuple[bool, str]:
    result, _ = _gate_on(Write(NOTE_A, envelope("note-a")), env={"PATH": _bin_with("python3", "dirname")})
    return _expect(result, 1, messages.c3_git_missing().render(), "stderr")


def library_absent() -> tuple[bool, str]:
    shadow = tempfile.mkdtemp()
    Path(shadow, "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    result, _ = _gate_on(Write(NOTE_A, envelope("note-a")), env={"PYTHONPATH": shadow})
    expected = messages.c2_library_missing("PyYAML", str(preflight.requirements_file())).render()
    return _expect(result, 1, expected, "stderr")


def misinvocation() -> tuple[bool, str]:
    return _expect(run_gate("", args=["--bogus"]), 1, "BROKEN: misinvocation:", "stderr")


def unparseable_input() -> tuple[bool, str]:
    return _expect(run_gate("not json"), 1, "BROKEN: hook input is not a JSON object", "stderr")


def outside_territory() -> tuple[bool, str]:
    result, _ = _gate_on(Write("README.md", "# no envelope\n"))
    return _expect(result, 0, messages.green_skip(messages.skip_outside_territory("README.md")), "stdout")


def not_markdown() -> tuple[bool, str]:
    result, _ = _gate_on(Write("docs/notes/a.txt", "x"))
    return _expect(result, 0, "0 documents examined", "stdout")


def void_territory() -> tuple[bool, str]:
    result, _ = _gate_on(Write("docs/ghost/g.md", "# no envelope\n"),
                         dials_patch={"ghost": {"territory": ["docs/ghost/**"]}})
    return _expect(result, 0, messages.skip_void_territory("docs/ghost/g.md", ["ghost"]), "stdout")


def negation() -> tuple[bool, str]:
    result, _ = _gate_on(Write("docs/notes/secret.md", "# no envelope\n"),
                         dials_patch={"notes-policy": {"territory": ["docs/notes/**", "!docs/notes/secret.md"]}})
    return _expect(result, 0, messages.skip_outside_territory("docs/notes/secret.md"), "stdout")


def severity_warn() -> tuple[bool, str]:
    result, _ = _gate_on(Write(NOTE_A, "# no envelope\n"), dials_patch={"const-meta-types": {"severity": "warn"}})
    if result.code != 0:
        return False, f"warn must let the write through; exit {result.code}: {result.stderr}"
    payload = json.loads(result.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    ok = (messages.f1_no_envelope(NOTE_A).headline in context and messages.warn_note() in context
          and payload["systemMessage"] == messages.warn_system(messages.f1_no_envelope(NOTE_A).headline))
    return ok, "exit 0, finding in additionalContext and systemMessage" if ok else f"bad payload: {payload}"


def _scan(bad: bool) -> Result:
    consumer = fresh_consumer(tempfile.mkdtemp())
    consumer.dials.update({"const-meta-types": {"severity": "warn"}, "ghost": {"territory": ["nowhere/**"]}})
    consumer.build()
    consumer.write(NOTE_A, "# no envelope\n" if bad else envelope("note-a"))
    return run_gate("", args=["--scan", str(consumer.root)])


def scan_red() -> tuple[bool, str]:
    tail = messages.scan_tail(examined=4, scanned=4, policies=3)
    return _expect(_scan(bad=True), 2, messages.count_scan(1, tail), "stdout")


def scan_green() -> tuple[bool, str]:
    result = _scan(bad=False)
    ok, evidence = _expect(result, 0, messages.green_scan(messages.scan_tail(4, 4, 3)), "stdout")
    return ok and messages.note_void_namespace("ghost") in result.stdout, evidence + " + void-namespace note"


def _log_lines(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def log_in_plugin_data() -> tuple[bool, str]:
    data = tempfile.mkdtemp()
    _gate_on(Write(NOTE_A, "# no envelope\n"), env={"CLAUDE_PLUGIN_DATA": data})
    lines = _log_lines(Path(data) / "const-meta-types.jsonl")
    first = lines[0]
    ok = (set(first) == {"ts", "module", "gate", "mode", "session", "stream", "text"}
          and first["text"] == "RED: " + messages.f1_no_envelope(NOTE_A).headline
          and first["stream"] == "stderr" and first["session"] == "fixture-session")
    return ok, f"{len(lines)} log lines; first: {first}"


def log_in_ignored_dir() -> tuple[bool, str]:
    result, root = _gate_on(Write(NOTE_A, envelope("note-a")), ignore=".gate-logs/\n",
                            dials_patch={"const-meta-types": {"log_dir": ".gate-logs"}})
    log = root / ".gate-logs" / "const-meta-types.jsonl"
    ok = result.code == 0 and log.is_file() and "governed by notes-policy" in _log_lines(log)[-1]["text"]
    return ok, f"exit {result.code}; log written inside the repository, git-ignored"


def log_dir_not_ignored() -> tuple[bool, str]:
    result, _ = _gate_on(Write(NOTE_A, envelope("note-a")),
                         dials_patch={"const-meta-types": {"log_dir": "gate-logs"}})
    return _expect(result, 1, messages.c13_log_dir_not_ignored("gate-logs").render(), "stderr")


def declared_libraries() -> tuple[bool, str]:
    declared = {line.split(">=")[0].split("==")[0].strip()
                for line in (HERE.parent / "requirements.txt").read_text().splitlines() if line.strip()}
    ok = declared == set(preflight.DECLARED)
    return ok, f"requirements.txt {sorted(declared)} == preflight table {sorted(preflight.DECLARED)}"


def message_shape() -> tuple[bool, str]:
    """Every finding carries its three parts; every case above names the key it teaches."""
    built = [case.expect for case in CASES]
    ok = all(isinstance(f, Finding) and f.key and f.headline and f.why and f.fix for f in built)
    return ok, f"{len(built)} findings examined, each with what / why / fix"


ASSERTIONS = [
    Assertion(12, "exit-code split: a malformed dials file exits 1, never 2, never 0", malformed_dials),
    Assertion(13, "absence: python3", python_absent),
    Assertion(14, "absence: an interpreter below the floor", python_below_floor),
    Assertion(15, "absence: git", git_absent),
    Assertion(16, "absence: a declared library (PyYAML)", library_absent),
    Assertion(17, "misinvocation exits 1: argparse's exit 2 is overridden", misinvocation),
    Assertion(18, "unparseable hook input is a configuration failure, not an empty event", unparseable_input),
    Assertion(19, "examined count: outside claimed territory prints 0 and exits 0", outside_territory),
    Assertion(20, "examined count: a non-Markdown file prints 0 and exits 0", not_markdown),
    Assertion(21, "a territory with no policy behind it claims nothing: a visible skip", void_territory),
    Assertion(22, "a file-level negated pattern excludes the file from the territory", negation),
    Assertion(23, "severity warn: exit 0 with the finding as JSON for the model and the user", severity_warn),
    Assertion(24, "scan: the finding with counts, exit 2, ignoring severity warn", scan_red),
    Assertion(25, "scan: green with counts, and a note per void namespace", scan_green),
    Assertion(26, "output log: every printed line lands in the plugin data directory", log_in_plugin_data),
    Assertion(27, "output log: the log_dir dial routes it to a git-ignored directory", log_in_ignored_dir),
    Assertion(28, "output log: a log_dir that git does not ignore is a configuration failure", log_dir_not_ignored),
    Assertion(29, "declared dependencies: requirements.txt equals the preflight table", declared_libraries),
    Assertion(30, "message shape: every taught finding has what, why and fix", message_shape),
]

if __name__ == "__main__":
    sys.exit(run_all(CASES, ASSERTIONS))
