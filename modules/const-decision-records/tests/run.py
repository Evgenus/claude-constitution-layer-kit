#!/usr/bin/env python3
"""Fixtures of const-decision-records: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number. Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one — three policies, none of them for records — so
every item adds the records policy and names it in this module's dial: through the
case's setup for the red→green cases, through `_gate_on` for the assertions.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml
from harness import (
    ENTRY,
    HERE,
    Assertion,
    Case,
    Edit,
    Result,
    Write,
    event_json,
    fresh_consumer,
    run_all,
    run_gate,
    scratch_dir,
)

# isort: split
# the harness comes first: it, and only it, puts the scripts directory on the import path
from consumer import Consumer, envelope
from decision_records_gate import messages, preflight
from decision_records_gate.model import Broken, EnvelopeState, Finding
from decision_records_gate.output import LOG_NAME, ROTATE_AT

NAMESPACE = "const-decision-records"
RECORDS_POLICY = "records-policy"
RECORD_A = "docs/decisions/a.md"
NOTE_A = "docs/notes/a.md"
NO_ENVELOPE = "# Fixture\n\nNo envelope at all.\n"
RECORD_DIALS: dict[str, object] = {
    RECORDS_POLICY: {"territory": ["docs/decisions/**"]},
    NAMESPACE: {"record_policies": [RECORDS_POLICY]},
}


def record(doc_id: str = "record-a", drop: tuple[str, ...] = (), **changes: object) -> str:
    """A valid decision record, rendered by the YAML dumper, with the named envelope fields
    replaced, added, or dropped. A value may be any YAML type: a number where a string is
    due is a fixture, not a typing accident."""
    fields: dict[str, object] = {
        "id": doc_id,
        "type": "task-record",
        "title": f"Fixture {doc_id}",
        "status": "active",
        "stakes": "process",
        "decider": "the maintainer",
    }
    fields.update(changes)
    kept = {key: value for key, value in fields.items() if key not in drop}
    return "---\n" + yaml.safe_dump(kept, sort_keys=False, allow_unicode=True) + "---\n\n# Fixture\n"


def dials_text(patch: dict[str, object] | None = None) -> str:
    dials = {**Consumer(Path()).dials, **RECORD_DIALS, **(patch or {})}
    return yaml.safe_dump(dials, sort_keys=False)


POLICY_DOCUMENT = Write(f"docs/policies/{RECORDS_POLICY}.md", envelope(RECORDS_POLICY, "current-state"))
SETUP = (Write("constitution.yaml", dials_text()), POLICY_DOCUMENT)
OVERLAP = (
    Write("constitution.yaml", dials_text({"shared-policy": {"territory": ["docs/decisions/shared/**"]}})),
    POLICY_DOCUMENT,
)
VALID = Write(RECORD_A, record())

# ------------------------------------------------------------------ red → green cases

CASES = [
    Case(
        1,
        "R1: a record with no envelope is blocked; a valid record passes",
        Write(RECORD_A, NO_ENVELOPE),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.NONE),
        SETUP,
    ),
    Case(
        2,
        "R1: an envelope opened and never closed is blocked",
        Write(RECORD_A, "---\nid: record-a\nstakes: process\n\n# Record A\n"),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.UNTERMINATED),
        SETUP,
    ),
    Case(
        3,
        "R1: an envelope that is not valid YAML is blocked",
        Write(RECORD_A, "---\nstakes: [unclosed\n---\n"),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.INVALID, "while parsing a flow sequence"),
        SETUP,
    ),
    Case(
        4,
        "R2: a wrong type, stakes outside the enum and a missing decider are blocked in one message",
        Write(RECORD_A, record(type="current-state", stakes="high", drop=("decider",))),
        VALID,
        messages.r2_invalid_fields(
            RECORD_A,
            [
                messages.r2_type_not_task_record("current-state"),
                messages.r2_stakes_not_allowed("high"),
                messages.f4_field_missing("decider"),
            ],
        ),
        SETUP,
    ),
    Case(
        5,
        "R2: a free-form record — a valid envelope with neither stakes nor decider — is blocked",
        Write(RECORD_A, envelope("record-a", "task-record")),
        VALID,
        messages.r2_invalid_fields(
            RECORD_A, [messages.f4_field_missing("stakes"), messages.f4_field_missing("decider")]
        ),
        SETUP,
    ),
    Case(
        6,
        "R2: a decider YAML reads as a number is blocked, and the message says to quote it",
        Write(RECORD_A, record(decider=42)),
        VALID,
        messages.r2_invalid_fields(RECORD_A, [messages.f4_field_not_string("decider", "int")]),
        SETUP,
    ),
    Case(
        7,
        "R2: a decider of blanks only is blocked",
        Write(RECORD_A, record(decider="  ")),
        VALID,
        messages.r2_invalid_fields(RECORD_A, [messages.r2_decider_empty()]),
        SETUP,
    ),
    Case(
        8,
        "R3: stakes routine is its own finding — a routine call is a commit note, never a record",
        Write(RECORD_A, record(stakes="routine")),
        VALID,
        messages.r3_routine_record(RECORD_A),
        SETUP,
    ),
    Case(
        9,
        "an Edit removing the decider is blocked on the reconstructed result; an Edit in the body passes",
        Edit(RECORD_A, "decider: the maintainer\n", ""),
        Edit(RECORD_A, "# Fixture", "# Fixture, edited"),
        messages.r2_invalid_fields(RECORD_A, [messages.f4_field_missing("decider")]),
        (*SETUP, VALID),
    ),
    Case(
        10,
        "a record by declaration, path mapping absent, is examined like one in record territory",
        Write("loose.md", envelope("loose", "task-record", policy=RECORDS_POLICY)),
        Write("loose.md", record("loose", policy=RECORDS_POLICY)),
        messages.r2_invalid_fields(
            "loose.md", [messages.f4_field_missing("stakes"), messages.f4_field_missing("decider")]
        ),
        SETUP,
    ),
    Case(
        11,
        "a record where two territories overlap is still examined as a record",
        Write("docs/decisions/shared/s.md", record("record-s", stakes="high")),
        Write("docs/decisions/shared/s.md", record("record-s")),
        messages.r2_invalid_fields("docs/decisions/shared/s.md", [messages.r2_stakes_not_allowed("high")]),
        OVERLAP,
    ),
    Case(
        55,
        "R2: a missing type, and stakes YAML reads as a number, are taught by name",
        Write(RECORD_A, record(stakes=3, drop=("type",))),
        VALID,
        messages.r2_invalid_fields(
            RECORD_A, [messages.f4_field_missing("type"), messages.f4_field_not_string("stakes", "int")]
        ),
        SETUP,
    ),
    Case(
        56,
        "R1: an envelope that is YAML but no mapping of fields is blocked",
        Write(RECORD_A, "---\n- stakes\n- decider\n---\n"),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.INVALID, messages.detail_not_a_mapping()),
        SETUP,
    ),
    Case(
        58,
        "an Edit that creates a file — no file yet, an empty old_string — is judged on what it creates",
        Edit(RECORD_A, "", record(drop=("stakes", "decider"))),
        Edit(RECORD_A, "", record()),
        messages.r2_invalid_fields(
            RECORD_A, [messages.f4_field_missing("stakes"), messages.f4_field_missing("decider")]
        ),
        SETUP,
    ),
]

# ------------------------------------------------------------------ assertions


def _gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    consumer = fresh_consumer()
    consumer.write("constitution.yaml", raw_dials if raw_dials is not None else dials_text(dials_patch))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return run_gate(event_json(consumer.root, action), env=env), consumer.root


def _own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps the record policy named."""
    return {NAMESPACE: {"record_policies": [RECORDS_POLICY], **dials}}


def _expect(result: Result, code: int, text: str, where: str = "both") -> tuple[bool, str]:
    haystack = {"stdout": result.stdout, "stderr": result.stderr, "both": result.stdout + result.stderr}[
        where
    ]
    ok = result.code == code and text in haystack
    return ok, (
        f"exit {result.code}: {text}"
        if ok
        else f"wanted exit {code} teaching {text!r}; got exit {result.code}: {haystack.strip()}"
    )


def _broken(result: Result, broken: Broken) -> tuple[bool, str]:
    """A configuration failure: exit 1 — never 2, never 0 — and its line is the FIRST stderr line."""
    first = result.stderr.splitlines()[0] if result.stderr else ""
    ok = result.code == 1 and first == broken.render()
    return ok, (
        f"exit 1, first stderr line: {first}"
        if ok
        else f"wanted exit 1 with first line {broken.render()!r};"
        f" got exit {result.code}: {result.stderr.strip()}"
    )


def _bin_with(*tools: str) -> str:
    """A PATH directory holding only the named tools, to simulate the absence of the rest."""
    directory = scratch_dir()
    for tool in tools:
        source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert source, tool
        os.symlink(source, directory / tool)
    return str(directory)


def dial_unset() -> tuple[bool, str]:
    """With no record policy named, a free-form record passes — and the count line says why."""
    result, _ = _gate_on(Write(RECORD_A, NO_ENVELOPE), dials_patch={NAMESPACE: {}})
    return _expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_record_policies()), "stdout")


def dial_unset_scan() -> tuple[bool, str]:
    consumer = fresh_consumer()
    result = run_gate("", args=["--scan", str(consumer.root)])
    return _expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_record_policies()), "stdout")


def not_a_record() -> tuple[bool, str]:
    result, _ = _gate_on(Write(NOTE_A, NO_ENVELOPE))
    skip = messages.g1_skip_not_a_record(NOTE_A, [RECORDS_POLICY])
    return _expect(result, 0, messages.g1_green_skip(skip), "stdout")


def declared_elsewhere() -> tuple[bool, str]:
    """In an overlap, a declaration naming the other claimant makes the document not a record."""
    target = "docs/decisions/shared/s.md"
    result, _ = _gate_on(
        Write(target, envelope("shared-s", policy="shared-policy")),
        dials_patch={"shared-policy": {"territory": ["docs/decisions/shared/**"]}},
    )
    skip = messages.g1_skip_not_a_record(target, [RECORDS_POLICY])
    return _expect(result, 0, messages.g1_green_skip(skip), "stdout")


def dangling_record_policy() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": ["ghost-policy"]}})
    ok, evidence = _expect(result, 0, messages.n2_note_dangling_record_policy("ghost-policy"), "stdout")
    return ok and "0 documents examined" in result.stdout, evidence


def rest_of_envelope_not_judged() -> tuple[bool, str]:
    """An id that is not kebab-case and a status outside the enum are another check's business."""
    result, _ = _gate_on(Write(RECORD_A, record("Record_A", status="open")))
    return _expect(result, 0, messages.g1_green_hook(RECORDS_POLICY), "stdout")


def routine_and_more() -> tuple[bool, str]:
    """Stakes routine with a missing decider: both findings are taught, and the count says two."""
    result, _ = _gate_on(Write(RECORD_A, record(stakes="routine", drop=("decider",))))
    wanted = [
        messages.r3_routine_record(RECORD_A).render(),
        messages.r2_invalid_fields(RECORD_A, [messages.f4_field_missing("decider")]).render(),
        messages.f9_count_hook(2, RECORD_A),
    ]
    ok = result.code == 2 and all(text in result.stderr for text in wanted)
    return ok, f"exit {result.code}; R3, R2 and a count of 2" if ok else result.stderr


def policy_in_record_territory() -> tuple[bool, str]:
    """A document where policies live is a policy, whatever else claims its path."""
    target = "docs/policies/extra-policy.md"
    result, _ = _gate_on(
        Write(target, envelope("extra-policy", "current-state")),
        dials_patch={RECORDS_POLICY: {"territory": ["docs/**"]}},
    )
    skip = messages.g1_skip_not_a_record(target, [RECORDS_POLICY])
    return _expect(result, 0, messages.g1_green_skip(skip), "stdout")


def root_named_as_record_policy() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": ["root-policy"]}})
    return _broken(result, messages.c5_record_policy_is_root("root-policy"))


def policy_named_twice() -> tuple[bool, str]:
    consumer = fresh_consumer()
    consumer.write("constitution.yaml", dials_text({NAMESPACE: {"record_policies": [RECORDS_POLICY] * 2}}))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    result = run_gate("", args=["--scan", str(consumer.root)])
    return _expect(result, 0, messages.f9_scan_tail(0, 4, 1), "stdout")


def edit_unappliable() -> tuple[bool, str]:
    result, _ = _gate_on(Edit(RECORD_A, "no such text", "x"), files={RECORD_A: record()})
    skip = messages.g1_skip_edit_unappliable(RECORD_A)
    return _expect(result, 0, messages.g1_green_skip(skip), "stdout")


def edit_replace_all() -> tuple[bool, str]:
    """replace_all is judged on the whole result. The harness's Edit has no such field, so the
    events are built here."""

    def run(new: str) -> Result:
        consumer = fresh_consumer((*SETUP, VALID))
        event = json.loads(event_json(consumer.root, Edit(RECORD_A, "process", new)))
        event["tool_input"]["replace_all"] = True
        return run_gate(json.dumps(event))

    red, green = run("high"), run("product")
    taught = messages.r2_invalid_fields(RECORD_A, [messages.r2_stakes_not_allowed("high")]).render()
    ok = red.code == 2 and taught in red.stderr and green.code == 0
    return ok, f"red exit {red.code} teaching R2, green exit {green.code}"


def relative_path() -> tuple[bool, str]:
    """A relative file_path is resolved against the event's cwd."""
    consumer = fresh_consumer(SETUP)
    event = json.loads(event_json(consumer.root, Write(RECORD_A, NO_ENVELOPE)))
    event["tool_input"]["file_path"] = RECORD_A
    result = run_gate(json.dumps(event))
    return _expect(
        result, 2, messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.NONE).render(), "stderr"
    )


def outside_any_repository() -> tuple[bool, str]:
    target = scratch_dir() / "loose.md"
    event = json.loads(event_json(target.parent, Write("loose.md", NO_ENVELOPE)))
    result = run_gate(json.dumps(event), env={"GIT_CEILING_DIRECTORIES": str(target.parent.parent)})
    return _expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_repo(str(target))), "stdout")


def no_dials_file() -> tuple[bool, str]:
    consumer = fresh_consumer()
    (consumer.root / "constitution.yaml").unlink()
    result = run_gate(event_json(consumer.root, Write(RECORD_A, NO_ENVELOPE)))
    return _expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_dials(str(consumer.root))), "stdout")


def no_root_policy() -> tuple[bool, str]:
    result, _ = _gate_on(Write(RECORD_A, NO_ENVELOPE), raw_dials=yaml.safe_dump(RECORD_DIALS))
    return _expect(result, 0, messages.g1_green_skip(messages.g1_skip_no_root()), "stdout")


def scan_with_deleted_file() -> tuple[bool, str]:
    """A tracked record deleted from the working tree, deletion not staged: not a document any more."""
    consumer = fresh_consumer((*SETUP, VALID, Write("docs/decisions/b.md", record("record-b"))))
    (consumer.root / RECORD_A).unlink()
    result = run_gate("", args=["--scan", str(consumer.root)])
    return _expect(result, 0, messages.g1_green_scan(messages.f9_scan_tail(1, 5, 1)), "stdout")


def abbreviated_flag() -> tuple[bool, str]:
    return _expect(run_gate("", args=["--sc", "."]), 1, "BROKEN: misinvocation:", "stderr")


def malformed_dials() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, raw_dials="root-policy: [\n")
    return _expect(result, 1, "BROKEN: constitution.yaml is not valid YAML", "stderr")


def dials_not_mapping() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, raw_dials="- a\n- b\n")[0], messages.c4b_dials_not_mapping())


def dials_bad_record_policies() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": "records-policy"}})
    return _broken(result, messages.c5_record_policies())


def dials_record_policy_not_kebab() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": ["Records Policy"]}})
    return _broken(result, messages.c5_record_policies())


def dials_bad_severity() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, dials_patch=_own(severity="loud"))[0], messages.c5_severity())


def dials_own_namespace() -> tuple[bool, str]:
    return _broken(_gate_on(VALID, dials_patch={NAMESPACE: "x"})[0], messages.c5_own_namespace_not_mapping())


def root_missing() -> tuple[bool, str]:
    root_policy = str(Consumer(Path()).dials["root_policy"])
    return _broken(_gate_on(VALID, remove=root_policy)[0], messages.c6_root_missing(root_policy))


def python_absent() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, env={"PATH": _bin_with("dirname")})
    return _expect(result, 1, f"BROKEN: {NAMESPACE} needs python3", "stderr")


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
                result = run_gate("{}", command=[found, str(ENTRY)])
                return _expect(result, 1, f"BROKEN: {NAMESPACE} needs Python 3.12 or newer", "stderr")
    return True, "NOT EXERCISED: no interpreter below 3.12 on this machine — 0 interpreters examined"


def git_absent() -> tuple[bool, str]:
    return _broken(
        _gate_on(VALID, env={"PATH": _bin_with("python3", "dirname")})[0], messages.c3_git_missing()
    )


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
    return _broken(
        run_gate("", args=["--scan", "no-such-directory"]), messages.c12_scan_path("no-such-directory")
    )


def not_markdown() -> tuple[bool, str]:
    return _expect(_gate_on(Write("docs/decisions/a.txt", "x"))[0], 0, "0 documents examined", "stdout")


def _warn(files: dict[str, str] | None = None) -> tuple[Result, Finding]:
    result, _ = _gate_on(Write(RECORD_A, NO_ENVELOPE), dials_patch=_own(severity="warn"), files=files)
    return result, messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.NONE)


def severity_warn() -> tuple[bool, str]:
    result, finding = _warn()
    if result.code != 0:
        return False, f"warn must let the write through; exit {result.code}: {result.stderr}"
    payload = json.loads(result.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    ok = (
        finding.render() in context
        and messages.w1_warn_note() in context
        and payload["systemMessage"] == messages.w1_warn_system(finding.headline)
    )
    return ok, "exit 0, finding in additionalContext and systemMessage" if ok else f"bad payload: {payload}"


def severity_warn_with_note() -> tuple[bool, str]:
    """Under warn, stdout must be one JSON object and nothing else, or the finding reaches nobody."""
    result, _ = _gate_on(
        Write(RECORD_A, NO_ENVELOPE),
        dials_patch={NAMESPACE: {"record_policies": [RECORDS_POLICY, "ghost-policy"], "severity": "warn"}},
    )
    payload = json.loads(result.stdout)  # raises, and so fails, if a note precedes the JSON
    note = messages.n2_note_dangling_record_policy("ghost-policy")
    ok = result.code == 0 and note in payload["hookSpecificOutput"]["additionalContext"]
    return ok, "stdout parses as one JSON object; the note travels inside additionalContext"


def _scan(bad: bool) -> Result:
    consumer = fresh_consumer()
    consumer.write("constitution.yaml", dials_text(_own(severity="warn")))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    consumer.write(RECORD_A, envelope("record-a", "task-record") if bad else record())
    consumer.write("docs/decisions/b.md", record("record-b", stakes="architecture"))
    consumer.write(NOTE_A, NO_ENVELOPE)  # not a record: never examined here
    return run_gate("", args=["--scan", str(consumer.root)])


def scan_red() -> tuple[bool, str]:
    tail = messages.f9_scan_tail(records=2, scanned=7, record_policies=1)
    return _expect(_scan(bad=True), 2, messages.f9_count_scan(1, tail), "stdout")


def scan_green() -> tuple[bool, str]:
    tail = messages.f9_scan_tail(records=2, scanned=7, record_policies=1)
    return _expect(_scan(bad=False), 0, messages.g1_green_scan(tail), "stdout")


def scan_scales() -> tuple[bool, str]:
    """The scan reads each document once: a few hundred records take seconds, not minutes."""
    consumer = fresh_consumer()
    consumer.write("constitution.yaml", dials_text())
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    for n in range(300):
        consumer.write(f"docs/decisions/r{n}.md", record(f"record-{n}"))
    started = time.monotonic()
    result = run_gate("", args=["--scan", str(consumer.root)])
    elapsed = time.monotonic() - started
    ok = result.code == 0 and "300 decision record(s) examined" in result.stdout and elapsed < 15
    return ok, f"300 records examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


def _log_lines(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def log_in_plugin_data() -> tuple[bool, str]:
    data = scratch_dir()
    _gate_on(Write(RECORD_A, NO_ENVELOPE), env={"CLAUDE_PLUGIN_DATA": str(data)})
    lines = _log_lines(data / LOG_NAME)
    first = lines[0]
    headline = messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.NONE).headline
    ok = (
        set(first) == {"ts", "module", "gate", "mode", "session", "stream", "text"}
        and first["text"] == "RED: " + headline
        and first["module"] == NAMESPACE
        and first["stream"] == "stderr"
        and first["session"] == "fixture-session"
    )
    return ok, f"{len(lines)} log lines; first: {first}"


def log_in_ignored_dir() -> tuple[bool, str]:
    data = scratch_dir()
    result, root = _gate_on(
        VALID,
        files={".gitignore": ".gate-logs/\n"},
        env={"CLAUDE_PLUGIN_DATA": str(data)},
        dials_patch=_own(log_dir=".gate-logs"),
    )
    log = root / ".gate-logs" / LOG_NAME
    ok = (
        result.code == 0
        and log.is_file()
        and f"governed by {RECORDS_POLICY}" in _log_lines(log)[-1]["text"]
        and not (data / LOG_NAME).exists()
    )
    return (
        ok,
        f"exit {result.code}; the whole run logged inside the repository,"
        " nothing split off to the data directory",
    )


def log_dir_not_ignored() -> tuple[bool, str]:
    result, _ = _gate_on(VALID, dials_patch=_own(log_dir="gate-logs"))
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
    red, _ = _gate_on(Write(RECORD_A, NO_ENVELOPE), env={"CLAUDE_PLUGIN_DATA": str(blocker)})
    green, _ = _gate_on(VALID, env={"CLAUDE_PLUGIN_DATA": str(blocker)})
    ok = red.code == 2 and green.code == 0
    return ok, f"log location unwritable: red still exits {red.code}, green still exits {green.code}"


def declared_libraries() -> tuple[bool, str]:
    declared = {
        line.split(">=")[0].split("==")[0].strip()
        for line in (HERE.parent / "requirements.txt").read_text().splitlines()
        if line.strip()
    }
    ok = declared == set(preflight.DECLARED)
    return ok, f"requirements.txt {sorted(declared)} == preflight table {sorted(preflight.DECLARED)}"


def message_shape() -> tuple[bool, str]:
    built = [case.expect for case in CASES]
    ok = all(isinstance(f, Finding) and f.key and f.headline and f.why and f.fix for f in built)
    return ok, f"{len(built)} findings examined, each with what / why / fix"


ASSERTIONS = [
    Assertion(12, "the dial unset: nothing is examined, and the count line teaches the dial", dial_unset),
    Assertion(13, "the dial unset, scan: the same visible zero", dial_unset_scan),
    Assertion(14, "a governed document that is no record is a visible skip", not_a_record),
    Assertion(15, "in an overlap, a declaration naming the other claimant: not a record", declared_elsewhere),
    Assertion(
        16,
        "a record policy the dial names that is no policy claims nothing: a note, never a failure",
        dangling_record_policy,
    ),
    Assertion(
        17,
        "the rest of the envelope is not judged here: a bad id and status pass",
        rest_of_envelope_not_judged,
    ),
    Assertion(18, "exit-code split: a malformed dials file exits 1, never 2, never 0", malformed_dials),
    Assertion(19, "C4b: a dials file that is not a mapping", dials_not_mapping),
    Assertion(20, "C5: record_policies that is not a list", dials_bad_record_policies),
    Assertion(21, "C5: a record policy id that is not kebab-case", dials_record_policy_not_kebab),
    Assertion(22, "C5: a severity outside block | warn", dials_bad_severity),
    Assertion(23, "C5: this module's own namespace must be a mapping", dials_own_namespace),
    Assertion(24, "C6: the root policy file is missing", root_missing),
    Assertion(25, "absence: python3", python_absent),
    Assertion(26, "absence: an interpreter below the floor", python_below_floor),
    Assertion(27, "absence: git", git_absent),
    Assertion(28, "absence: a declared library (PyYAML)", library_absent),
    Assertion(29, "a failing git is a configuration failure, never a green skip", git_failing),
    Assertion(30, "misinvocation exits 1: argparse's exit 2 is overridden", misinvocation),
    Assertion(
        31,
        "--help is a misinvocation like any other: no exit path past the guard and the log",
        help_is_not_special,
    ),
    Assertion(32, "unparseable hook input is a configuration failure, not an empty event", unparseable_input),
    Assertion(33, "a Write event without its documented fields is a configuration failure", malformed_event),
    Assertion(34, "an event for a tool this gate does not judge is a visible skip", other_tool),
    Assertion(35, "--scan on a path that does not exist is a configuration failure", scan_missing_path),
    Assertion(36, "examined count: a non-Markdown file prints 0 and exits 0", not_markdown),
    Assertion(
        37, "severity warn: exit 0 with the whole finding as JSON for the model and the user", severity_warn
    ),
    Assertion(38, "severity warn with a note: stdout stays one JSON object", severity_warn_with_note),
    Assertion(39, "scan: the finding with counts, exit 2, ignoring severity warn", scan_red),
    Assertion(40, "scan: green with counts; a governed non-record is never examined", scan_green),
    Assertion(41, "scan: 300 records in seconds (each document read once)", scan_scales),
    Assertion(42, "output log: every printed line lands in the plugin data directory", log_in_plugin_data),
    Assertion(
        43, "output log: the log_dir dial routes the whole run to a git-ignored directory", log_in_ignored_dir
    ),
    Assertion(
        44, "output log: a log_dir that git does not ignore is a configuration failure", log_dir_not_ignored
    ),
    Assertion(45, "output log: rotation past the size limit", log_rotates),
    Assertion(46, "output log: a logging failure never changes the verdict", log_failure_keeps_verdict),
    Assertion(47, "declared dependencies: requirements.txt equals the preflight table", declared_libraries),
    Assertion(48, "message shape: every taught finding has what, why and fix", message_shape),
    Assertion(59, "stakes routine and a missing decider: both taught, the count says two", routine_and_more),
    Assertion(60, "a document where policies live is never a record", policy_in_record_territory),
    Assertion(61, "C5: the root policy named as a record policy", root_named_as_record_policy),
    Assertion(62, "a record policy named twice counts once", policy_named_twice),
    Assertion(
        63, "an Edit whose old_string is absent is a visible skip; the tool reports it", edit_unappliable
    ),
    Assertion(57, "an Edit with replace_all is judged on the whole result", edit_replace_all),
    Assertion(64, "a relative file_path is resolved against the event's cwd", relative_path),
    Assertion(65, "a file outside any git repository is a visible skip", outside_any_repository),
    Assertion(66, "no dials file: a visible skip", no_dials_file),
    Assertion(67, "a dials file with no root_policy: a visible skip", no_root_policy),
    Assertion(
        68,
        "scan: a tracked file deleted from the working tree is left out, not a failure",
        scan_with_deleted_file,
    ),
    Assertion(
        69, "an abbreviated flag is a misinvocation, not a scan logged as a hook run", abbreviated_flag
    ),
]

if __name__ == "__main__":
    sys.exit(run_all(CASES, ASSERTIONS))
