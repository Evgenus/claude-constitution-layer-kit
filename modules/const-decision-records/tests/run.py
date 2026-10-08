#!/usr/bin/env python3
"""Fixtures of const-decision-records: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one — three policies, none of them for records — so
every item adds the records policy and names it in this module's dial: through the
case's setup for the red→green cases, through `gate_on` for the assertions. The session-start
printer is the second entry point, driven through its own items (T38–T41).
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import yaml
from const_gate import identity
from const_gate import messages as shared
from const_gate.envelope import yaml_error_line
from const_gate.model import EnvelopeState
from consumer import Consumer, envelope
from decision_records_gate import messages, start
from decision_records_gate.model import Stakes
from harness import (
    Assertion,
    Case,
    Edit,
    Harness,
    Result,
    Write,
    broken_first_line,
    event_json,
    expect,
    red_lines,
)
from shared_items import (
    NO_ENVELOPE,
    Subject,
    git_patch,
    git_timeouts,
    hook_budget,
    shared_assertions,
)

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MODULE_ROOT = SCRIPTS.parent

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
H = Harness(SCRIPTS, "check-decision-record.sh", "check-decision-record.py", start.GATE.namespace)
SESSION = Harness(SCRIPTS, "session-start.sh", "session-start.py", start.GATE.namespace)

NAMESPACE = start.GATE.namespace
RECORDS_POLICY = "records-policy"
RECORD_A = "docs/decisions/a.md"
NOTE_A = "docs/notes/a.md"
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


def yaml_error(block: str) -> str:
    """What the gate will report for a YAML block that does not parse: the parser's own words."""
    try:
        yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return yaml_error_line(exc)
    raise AssertionError("the fixture block parses")


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
# typed by hand, as the gate prints it for a free-form record at RECORD_A
R2_HEADLINE = "RED: docs/decisions/a.md: decision-record field(s) invalid: stakes missing; decider missing"

# ------------------------------------------------------------------ red → green cases

GREEN_WHAT = "governed by records-policy"  # what every green half's line says its document is, typed by hand

CASES = [
    Case(
        1,
        "R1: a record with no envelope is blocked; a valid record passes",
        Write(RECORD_A, NO_ENVELOPE),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.NONE),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        2,
        "R1: an envelope opened and never closed is blocked",
        Write(RECORD_A, "---\nid: record-a\nstakes: process\n\n# Record A\n"),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.UNTERMINATED),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        3,
        "R1: an envelope that is not valid YAML is blocked",
        Write(RECORD_A, "---\nstakes: [unclosed\n---\n"),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.INVALID, yaml_error("stakes: [unclosed")),
        GREEN_WHAT,
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
                shared.field_missing("decider"),
            ],
        ),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        5,
        "R2: a free-form record — a valid envelope with neither stakes nor decider — is blocked",
        Write(RECORD_A, envelope("record-a", "task-record")),
        VALID,
        messages.r2_invalid_fields(
            RECORD_A, [shared.field_missing("stakes"), shared.field_missing("decider")]
        ),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        6,
        "R2: a decider YAML reads as a number is blocked, and the message says to quote it",
        Write(RECORD_A, record(decider=42)),
        VALID,
        messages.r2_invalid_fields(RECORD_A, [shared.field_not_string("decider", "int")]),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        7,
        "R2: a decider of blanks only is blocked",
        Write(RECORD_A, record(decider="  ")),
        VALID,
        messages.r2_invalid_fields(RECORD_A, ["decider empty"]),  # typed by hand
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        8,
        "R3: stakes routine is its own finding — a routine call is a commit note, never a record",
        Write(RECORD_A, record(stakes="routine")),
        VALID,
        messages.r3_routine_record(RECORD_A),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        9,
        "an Edit removing the decider is blocked on the reconstructed result; an Edit in the body passes",
        Edit(RECORD_A, "decider: the maintainer\n", ""),
        Edit(RECORD_A, "# Fixture", "# Fixture, edited"),
        messages.r2_invalid_fields(RECORD_A, [shared.field_missing("decider")]),
        GREEN_WHAT,
        (*SETUP, VALID),
    ),
    Case(
        10,
        "a record by declaration, path mapping absent, is examined like one in record territory",
        Write("loose.md", envelope("loose", "task-record", policy=RECORDS_POLICY)),
        Write("loose.md", record("loose", policy=RECORDS_POLICY)),
        messages.r2_invalid_fields(
            "loose.md", [shared.field_missing("stakes"), shared.field_missing("decider")]
        ),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        11,
        "a record where two territories overlap is still examined as a record",
        Write("docs/decisions/shared/s.md", record("record-s", stakes="high")),
        Write("docs/decisions/shared/s.md", record("record-s")),
        messages.r2_invalid_fields("docs/decisions/shared/s.md", [messages.r2_stakes_not_allowed("high")]),
        GREEN_WHAT,
        OVERLAP,
    ),
    Case(
        30,
        "R2: a missing type, and stakes YAML reads as a number, are taught by name",
        Write(RECORD_A, record(stakes=3, drop=("type",))),
        VALID,
        messages.r2_invalid_fields(
            RECORD_A, [shared.field_missing("type"), shared.field_not_string("stakes", "int")]
        ),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        31,
        "R1: an envelope that is YAML but no mapping of fields is blocked",
        Write(RECORD_A, "---\n- stakes\n- decider\n---\n"),
        VALID,
        messages.r1_no_readable_envelope(
            RECORD_A, EnvelopeState.INVALID, "the block is not a mapping of field: value"
        ),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        33,
        "an Edit that creates a file — no file yet, an empty old_string — is judged on what it creates",
        Edit(RECORD_A, "", record(drop=("stakes", "decider"))),
        Edit(RECORD_A, "", record()),
        messages.r2_invalid_fields(
            RECORD_A, [shared.field_missing("stakes"), shared.field_missing("decider")]
        ),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        32,
        "an Edit with replace_all is judged on the whole result",
        Edit(RECORD_A, "process", "high", replace_all=True),
        Edit(RECORD_A, "process", "product", replace_all=True),
        messages.r2_invalid_fields(RECORD_A, [messages.r2_stakes_not_allowed("high")]),
        GREEN_WHAT,
        (*SETUP, VALID),
    ),
]

# ------------------------------------------------------------------ assertions


def gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", raw_dials if raw_dials is not None else dials_text(dials_patch))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return H.run_gate(event_json(consumer.root, action), env=env), consumer.root


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps the record policy named."""
    return {NAMESPACE: {"record_policies": [RECORDS_POLICY], **dials}}


def dial_unset() -> tuple[bool, str]:
    """With no record policy named, a free-form record passes — and the count line says why."""
    result, _ = gate_on(Write(RECORD_A, NO_ENVELOPE), dials_patch={NAMESPACE: {}})
    skip = (  # typed by hand
        f"{NAMESPACE}.record_policies names no policy, so no document is known to be a decision record"
        f" — to switch the check on, write {NAMESPACE}: {{record_policies: [<id of the policy that governs"
        " decision records>]} in constitution.yaml"
    )
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


def dial_unset_scan() -> tuple[bool, str]:
    consumer = H.fresh_consumer()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_record_policies()), "stdout")


def as_context(result: Result) -> Result:
    """A hook run that carries notes hands them, with the verdict, to the model as one JSON object."""
    answer = json.loads(result.stdout)
    return Result(result.code, answer["hookSpecificOutput"]["additionalContext"], result.stderr)


def not_a_record() -> tuple[bool, str]:
    result, _ = gate_on(Write(NOTE_A, NO_ENVELOPE))
    skip = messages.g1_skip_not_a_record(NOTE_A, [RECORDS_POLICY])
    plain = expect(result, 0, shared.g1_green_skip(skip), "stdout")
    # a path over 80 characters with a line break stands whole, the break escaped; a policy id of 100
    # characters in the dial only points, so it is cut — every expected line typed by hand
    long_note = "docs/notes/a\n" + "b" * 100 + ".md"
    wide, _ = gate_on(
        Write(long_note, NO_ENVELOPE),
        dials_patch={NAMESPACE: {"record_policies": [RECORDS_POLICY, "g" * 100]}},
    )
    line = (
        "GREEN: const-decision-records: 0 documents examined — docs/notes/a\\n"
        + "b" * 100
        + ".md is not governed by a record policy (records-policy, "
        + "g" * 80
        + "… [100 characters])"
    )
    return all_of(
        [plain, expect(as_context(wide), 0, line, "stdout")], "a path whole on one line, a long id cut"
    )


def declared_elsewhere() -> tuple[bool, str]:
    """In an overlap, a declaration naming the other claimant makes the document not a record."""
    target = "docs/decisions/shared/s.md"
    result, _ = gate_on(
        Write(target, envelope("shared-s", policy="shared-policy")),
        dials_patch={"shared-policy": {"territory": ["docs/decisions/shared/**"]}},
    )
    skip = messages.g1_skip_not_a_record(target, [RECORDS_POLICY])
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


def dangling_record_policy() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": ["ghost-policy"]}})
    ok, evidence = expect(result, 0, messages.n2_note_dangling_record_policy("ghost-policy"), "stdout")
    # an id of 100 characters only points: the note cuts it at 80 and says so, typed by hand
    long_id = "g" * 100
    wide, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": [long_id]}})
    cut = (
        "note: const-decision-records.record_policies names '"
        + "g" * 80
        + "… [100 characters]', but no policy"
        " with that id lies in the root policy's territory; it claims nothing until that policy exists"
    )
    wide_ok, wide_evidence = expect(as_context(wide), 0, cut, "stdout")
    return all_of(
        [(ok and "0 documents examined" in result.stdout, evidence), (wide_ok, wide_evidence)],
        "a dangling policy id is named; a long one is cut",
    )


def record_policy_claims_nothing() -> tuple[bool, str]:
    """A record policy that exists, whose namespace declares no territory: a note naming the line
    to write, never a failure, and nothing examined."""
    result, _ = gate_on(VALID, dials_patch={RECORDS_POLICY: {"territory": []}})
    note = messages.n3_note_record_policy_claims_nothing(RECORDS_POLICY, POLICY_DOCUMENT.target)
    answer = json.loads(result.stdout)  # a hook run with notes hands them to the model as one JSON object
    said = Result(result.code, answer["hookSpecificOutput"]["additionalContext"], result.stderr)
    ok, evidence = expect(said, 0, note, "stdout")
    # the policy file's path, over 80 characters with a line break, and its id of 100 characters are
    # typed whole into the note — the reader opens the one and writes the other: escaped, never cut
    long_id = "p" * 100
    long_path = "docs/policies/q\n" + "x" * 100 + ".md"
    wide, _ = gate_on(
        VALID,
        dials_patch={NAMESPACE: {"record_policies": [long_id]}, long_id: {"territory": []}},
        files={long_path: envelope(long_id, "current-state")},
    )
    wide_note = (
        f"note: const-decision-records.record_policies names '{long_id}' (docs/policies/q\\n"
        + "x" * 100
        + ".md),"
        " whose namespace declares no territory — it governs no document until constitution.yaml holds"
        f" {long_id}: {{territory: [<patterns of the paths where decision records live>]}}"
    )
    wide_ok, wide_evidence = expect(as_context(wide), 0, wide_note, "stdout")
    return all_of(
        [(ok and "0 documents examined" in said.stdout, evidence), (wide_ok, wide_evidence)],
        "the policy's path and id whole, on one line",
    )


def a_misspelt_dial() -> tuple[bool, str]:
    """A key of the namespace that is none of the six is refused, never a setting ignored in
    silence — `record_policy:` for `record_policies:` would otherwise read as the dial unset."""
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policy": [RECORDS_POLICY]}})
    return broken_first_line(
        result,
        "BROKEN: constitution.yaml: const-decision-records.record_policy is no dial of this module — fix: a"
        " misspelt dial would be ignored in silence, so none is: write one of severity, log_dir,"
        " record_policies, boundary_examples, deciders, note_trailer",
    )


def rest_of_envelope_not_judged() -> tuple[bool, str]:
    """An id that is not kebab-case and a status outside the enum are another check's business."""
    result, _ = gate_on(Write(RECORD_A, record("Record_A", status="open")))
    return expect(result, 0, shared.g1_green_hook(shared.governed_by(RECORDS_POLICY)), "stdout")


def routine_and_more() -> tuple[bool, str]:
    """Stakes routine with a missing decider: both findings are taught, and the count says two."""
    result, _ = gate_on(Write(RECORD_A, record(stakes="routine", drop=("decider",))))
    wanted = [
        messages.r3_routine_record(RECORD_A).render(),
        messages.r2_invalid_fields(RECORD_A, [shared.field_missing("decider")]).render(),
        shared.f9_count_hook(2, RECORD_A),
    ]
    ok = result.code == 2 and all(text in result.stderr for text in wanted)
    return ok, f"exit {result.code}; R3, R2 and a count of 2" if ok else result.stderr


def policy_in_record_territory() -> tuple[bool, str]:
    """A document where policies live is a policy, whatever else claims its path."""
    target = "docs/policies/extra-policy.md"
    result, _ = gate_on(
        Write(target, envelope("extra-policy", "current-state")),
        dials_patch={RECORDS_POLICY: {"territory": ["docs/**"]}},
    )
    skip = messages.g1_skip_not_a_record(target, [RECORDS_POLICY])
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


def root_named_as_record_policy() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": ["root-policy"]}})
    plain = broken_first_line(result, messages.c5_record_policy_is_root("root-policy").render())
    if not plain[0]:
        return plain
    # a root policy whose id is 100 characters only points: the line cuts it at 80 and says so
    root = "docs/policies/long-root.md"
    long_id = "r" * 100
    wide, _ = gate_on(
        VALID,
        dials_patch={
            "root_policy": root,
            long_id: {"territory": ["docs/policies/**"]},
            NAMESPACE: {"record_policies": [long_id]},
        },
        files={root: envelope(long_id, "current-state")},
    )
    cut = (
        "BROKEN: constitution.yaml: const-decision-records.record_policies names the root policy '"
        + "r" * 80
        + "… [100 characters]', which governs policies, never decision records — fix: name the policy that"
        " governs decision records instead; if there is none yet, write that policy first"
    )
    return broken_first_line(wide, cut)


def policy_named_twice() -> tuple[bool, str]:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text({NAMESPACE: {"record_policies": [RECORDS_POLICY] * 2}}))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, messages.f9_scan_tail(0, 4, 1), "stdout")


def dials_bad_record_policies() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": "records-policy"}})
    line = (  # typed by hand
        f"BROKEN: constitution.yaml: {NAMESPACE}.record_policies must be a list of kebab-case policy ids"
        f" — fix: write {NAMESPACE}: {{record_policies: [<id of the policy that governs decision"
        " records>]}, or remove the key"
    )
    return broken_first_line(result, line)


def dials_record_policy_not_kebab() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": ["Records Policy"]}})
    return broken_first_line(result, messages.c5_record_policies().render())


def severity_warn_with_note() -> tuple[bool, str]:
    """Under warn, stdout must be one JSON object and nothing else, or the finding reaches nobody."""
    result, _ = gate_on(
        Write(RECORD_A, NO_ENVELOPE),
        dials_patch={NAMESPACE: {"record_policies": [RECORDS_POLICY, "ghost-policy"], "severity": "warn"}},
    )
    payload = json.loads(result.stdout)  # raises, and so fails, if a note precedes the JSON
    note = messages.n2_note_dangling_record_policy("ghost-policy")
    ok = result.code == 0 and note in payload["hookSpecificOutput"]["additionalContext"]
    return ok, "stdout parses as one JSON object; the note travels inside additionalContext"


def _scan(bad: bool) -> Result:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text(own(severity="warn")))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    consumer.write(RECORD_A, envelope("record-a", "task-record") if bad else record())
    consumer.write("docs/decisions/b.md", record("record-b", stakes="architecture"))
    consumer.write(NOTE_A, NO_ENVELOPE)  # not a record: never examined here
    return H.run_gate("", args=["--scan", str(consumer.root)])


def scan_red() -> tuple[bool, str]:
    """Exactly the one finding and the count line, typed by hand: a finding of another kind, or one
    more, is red."""
    result = _scan(bad=True)
    wanted = [
        R2_HEADLINE,
        "RED: 1 finding(s) — 2 decision record(s) examined, 7 Markdown file(s) scanned, 1 record policy(ies)",
    ]
    ok = result.code == 2 and red_lines(result.stdout) == wanted
    return (
        ok,
        f"exit 2: {wanted[1]}"
        if ok
        else f"wanted exit 2 and {wanted}; got exit {result.code}: {result.stdout}",
    )


def scan_green() -> tuple[bool, str]:
    tail = messages.f9_scan_tail(records=2, scanned=7, record_policies=1)
    return expect(_scan(bad=False), 0, shared.g1_green_scan(tail), "stdout")


def scan_scales() -> tuple[bool, str]:
    """The scan reads each document once: a few hundred records take seconds, not minutes."""
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text())
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    for n in range(300):
        consumer.write(f"docs/decisions/r{n}.md", record(f"record-{n}"))
    started = time.monotonic()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    elapsed = time.monotonic() - started
    line = (
        "GREEN: const-decision-records: 300 decision record(s) examined, 304 Markdown file(s) scanned,"
        " 1 record policy(ies)"
    )
    ok = result.code == 0 and line in result.stdout.splitlines() and elapsed < 15
    return ok, f"300 records examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


def scan_with_deleted_file() -> tuple[bool, str]:
    """A tracked record deleted from the working tree, deletion not staged: not a document any more."""
    consumer = H.fresh_consumer((*SETUP, VALID, Write("docs/decisions/b.md", record("record-b"))))
    (consumer.root / RECORD_A).unlink()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 5, 1)), "stdout")


# What every R1 fix says the block carries, typed by hand once for its three shapes.
CARRIES = (
    "id: <kebab-id>, type: task-record, title: <one line>, status: active | inactive, stakes: process |"
    " product | architecture, decider: <person or role>"
)
# The lines each case's red half prints, keyed by the case's number, typed here by hand: the cases
# compare with what the message functions return, so a slip inside a function — a why emptied, a
# word lost from a fix — would pass them all. R1's INVALID headline stops where the parser's own
# words begin; case 5's headline is the scan's R2_HEADLINE.
GOLDEN: dict[int, Sequence[str]] = {
    1: [
        "RED: docs/decisions/a.md: a decision record with no readable envelope (the file does not start"
        " with a '---' line)",
        "  why: a record declares its stakes and its decider in the envelope: without them the ruling has"
        " no price and nobody accountable",
        f"  fix: start the file with a YAML block between two '---' lines carrying {CARRIES}",
    ],
    2: [
        "RED: docs/decisions/a.md: a decision record with no readable envelope (opened with '---' but"
        " never closed)",
        f"  fix: close the YAML block with a line holding only '---'; the block carries {CARRIES}",
    ],
    3: [
        "RED: docs/decisions/a.md: a decision record with no readable envelope (the block between the"
        " '---' lines cannot be read: ",
        f"  fix: repair the YAML between the '---' lines; the block carries {CARRIES}",
    ],
    4: [
        "RED: docs/decisions/a.md: decision-record field(s) invalid: type 'current-state' is not"
        " task-record; stakes 'high' not one of process | product | architecture; decider missing",
        "  why: a decision record is a task-record whose envelope adds the stakes, which set the ceremony"
        " the ruling gets, and the decider, who is accountable for it; git can derive neither",
        "  fix: set each named field: type = task-record (a record is a change delta); stakes = process"
        " (harness, policy or procedure) | product (user-visible behaviour) | architecture (structural,"
        " hard to reverse); decider = the person or role who made the choice, a non-empty string",
    ],
    5: [R2_HEADLINE],
    8: [
        "RED: docs/decisions/a.md: stakes 'routine' — a routine call never produces a record",
        "  why: ceremony scales with stakes: a call that is cheap to revert is noted in the commit message,"
        " and a record for it is ritual",
        "  fix: write no record: put the note in the commit message, and delete this file if it already"
        " exists; or, if the ruling is not cheap to revert, set stakes: process | product | architecture",
    ],
}


def golden_lines() -> tuple[bool, str]:
    """Each case's red input run afresh on its setup; every literal of GOLDEN must stand in its stderr."""
    cases = {case.number: case for case in CASES}
    missing: list[str] = []
    for number, lines in GOLDEN.items():
        case = cases[number]
        stderr = H.run_gate(event_json(H.fresh_consumer(case.setup).root, case.red)).stderr
        missing += [f"case {number}: {line}" for line in lines if line not in stderr]
    # a type and a stakes value holding a line break stay on one line, the break shown escaped
    broken_values = H.run_gate(
        event_json(
            H.fresh_consumer(SETUP).root, Write(RECORD_A, record(type="task\nrecord", stakes="high\nlow"))
        )
    ).stderr
    escaped = (
        "RED: docs/decisions/a.md: decision-record field(s) invalid: type 'task\\nrecord' is not"
        " task-record; stakes 'high\\nlow' not one of process | product | architecture"
    )
    if escaped not in broken_values:
        missing.append(f"escaped values: {escaped}")
    # a type and a stakes value of 100 characters only point: cut at 80, the cut said
    cut_values = H.run_gate(
        event_json(H.fresh_consumer(SETUP).root, Write(RECORD_A, record(type="t" * 100, stakes="s" * 100)))
    ).stderr
    cut = (
        "RED: docs/decisions/a.md: decision-record field(s) invalid: type '"
        + "t" * 80
        + "… [100 characters]' is not task-record; stakes '"
        + "s" * 80
        + "… [100 characters]' not one of process | product | architecture"
    )
    if cut not in cut_values:
        missing.append(f"cut values: {cut}")
    # the R2 fix glosses each stakes level in prose: exactly the enum's members, in its order
    fix = messages.r2_invalid_fields("x", []).fix
    glossed = re.findall(r"(\w+) \(", fix.split("stakes = ")[1].split("; decider")[0])
    if glossed != [level.value for level in Stakes]:
        missing.append(f"the R2 fix glosses {glossed}, the enum holds {[level.value for level in Stakes]}")
    # the written file's path stands whole, over 80 characters, its break escaped, in every headline;
    # a YAML error's backslash is shown doubled and its whole text kept
    weird = "docs/decisions/a\n" + "b" * 100 + ".md"
    shown_path = "docs/decisions/a\\n" + "b" * 100 + ".md"
    runs = {
        "R1 path": (
            Write(weird, NO_ENVELOPE),
            f"RED: {shown_path}: a decision record with no readable envelope (",
        ),
        "R2 path": (
            Write(weird, record(stakes="high")),
            f"RED: {shown_path}: decision-record field(s) invalid: ",
        ),
        "R3 path": (
            Write(weird, record(stakes="routine")),
            f"RED: {shown_path}: stakes 'routine' — a routine",
        ),
        "R1 yaml": (
            Write(RECORD_A, '---\nid: "x\\q"\n---\n'),
            "RED: docs/decisions/a.md: a decision record with no readable envelope (the block between the"
            " '---' lines cannot be read: while scanning a double-quoted scalar in"
            ' "<unicode string>", line 1, column 5:'
            ' id: "x\\\\q" ^ found unknown escape character \'q\' in "<unicode string>", line 1, column 8:'
            ' id: "x\\\\q" ^)',
        ),
    }
    for label, (action, wanted) in runs.items():
        said = H.run_gate(event_json(H.fresh_consumer(SETUP).root, action)).stderr
        if wanted not in said:
            missing.append(f"{label}: {wanted}")
    found = sum(len(lines) for lines in GOLDEN.values()) + len(runs)
    return not missing, f"{found} literal lines found" if not missing else "not found:\n" + "\n".join(missing)


# ---------------------------------------------------------------- the session-start printer


def all_of(results: list[tuple[bool, str]], summary: str) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, failed[0] if failed else summary


def session_json(root: Path) -> str:
    return json.dumps(
        {
            "hook_event_name": "SessionStart",
            "session_id": "fixture-session",
            "cwd": str(root),
            "source": "startup",
        }
    )


def session_root(
    dials_patch: dict[str, object] | None = None, raw_dials: str | None = None, remove: str | None = None
) -> Path:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", raw_dials if raw_dials is not None else dials_text(dials_patch))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return consumer.root


ZERO_LINE = (
    "const-decision-records: no document is examined — const-decision-records.record_policies is an empty"
    " list in constitution.yaml"
)


def session_start_zero_line() -> tuple[bool, str]:
    """Nothing while a record policy is named; the zero line typed by hand when the dial is an empty
    list and when it is absent, of the size the module document states."""
    patch, log = git_patch(SESSION)  # the printer is a hook: each of its git calls has the hook's budget
    named = SESSION.run_gate(session_json(session_root()), env=patch)
    named_ok = named.code == 0 and named.stdout == "" and named.stderr == ""
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"one line of ([0-9,]+) characters saying that no document is examined", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    empty = SESSION.run_gate(session_json(session_root({NAMESPACE: {"record_policies": []}})))
    empty_ok = empty.code == 0 and empty.stdout == ZERO_LINE + "\n" and empty.stderr == ""
    absent = SESSION.run_gate(session_json(session_root({NAMESPACE: {}})))
    absent_ok = absent.code == 0 and absent.stdout == ZERO_LINE + "\n"
    return all_of(
        [
            (named_ok, f"a named policy printed: {named.stdout!r} {named.stderr!r}"),
            hook_budget(git_timeouts(log)),
            (empty_ok, f"an empty list got: {empty.stdout!r} {empty.stderr!r}"),
            (absent_ok, f"an absent dial got: {absent.stdout!r} {absent.stderr!r}"),
            (
                stated == len(ZERO_LINE),
                f"the document states {stated} characters, the line has {len(ZERO_LINE)}",
            ),
        ],
        f"nothing when named; the zero line of {len(ZERO_LINE)} characters when empty or absent, as stated",
    )


def colon_dir() -> Path:
    """A fresh directory named `a:b`: a path holding ':' must be said whole by the session printer."""
    path = H.scratch_dir() / "a:b"
    path.mkdir()
    return path


def colon_root() -> Path:
    """A repository root whose own name holds ':', its dials file removed."""
    consumer = Consumer(colon_dir()).build()
    (consumer.root / "constitution.yaml").unlink()
    return consumer.root


def session_start_skips_and_failures() -> tuple[bool, str]:
    """No dials file and no repository (roots and folders whose names hold `:` too), the first also from a
    subfolder of the root: the shared skips said in the module's words, typed by hand; malformed dials:
    exit 1 with the shared C4 first on stderr and nothing on stdout; an argument: exit 1."""
    root = colon_root()
    no_dials = SESSION.run_gate(session_json(root))
    no_dials_line = (
        f"const-decision-records: no constitution.yaml in {root} — the record gate examines nothing there"
        " until the file names a record policy in const-decision-records.record_policies"
    )
    no_dials_ok = no_dials.code == 0 and no_dials.stdout == no_dials_line + "\n"
    (root / "sub").mkdir()
    from_sub = SESSION.run_gate(session_json(root / "sub"))
    from_sub_ok = from_sub.code == 0 and from_sub.stdout == no_dials_line + "\n"
    loose = colon_dir()
    no_repo = SESSION.run_gate(session_json(loose), env={"GIT_CEILING_DIRECTORIES": str(loose.parent)})
    no_repo_line = (
        f"const-decision-records: {loose} is not inside a git repository — the record gate examines nothing"
        " there"
    )
    no_repo_ok = no_repo.code == 0 and no_repo.stdout == no_repo_line + "\n"
    # typed by hand
    could_not_run = "BROKEN: the session-start line could not be printed — the gate's state is unknown"
    bad = SESSION.run_gate(session_json(session_root(raw_dials="root-policy: [\n")))
    bad_ok = (
        bad.code == 1
        and bad.stdout == ""
        and bad.stderr.startswith("BROKEN: constitution.yaml is not valid YAML")
        and could_not_run in bad.stderr
    )
    broken_name = "d\n" + "e" * 100  # a folder name holding a line break, over 80 characters
    wide_dir = H.scratch_dir() / broken_name
    wide_dir.mkdir()
    wide_root = Consumer(wide_dir).build().root
    (wide_root / "constitution.yaml").unlink()
    wide = SESSION.run_gate(session_json(wide_root))
    shown_name = "d\\n" + "e" * 100
    wide_ok = (
        wide.code == 0
        and wide.stdout.count("\n") == 1  # one line: the break is shown escaped
        and wide.stdout.startswith("const-decision-records: no constitution.yaml in ")
        and f"{shown_name} — the record gate examines nothing there" in wide.stdout
    )
    wide_loose = H.scratch_dir() / broken_name
    wide_loose.mkdir()
    wide_no_repo = SESSION.run_gate(
        session_json(wide_loose), env={"GIT_CEILING_DIRECTORIES": str(wide_loose.parent)}
    )
    wide_no_repo_ok = (
        wide_no_repo.code == 0
        and wide_no_repo.stdout.count("\n") == 1
        and f"{shown_name} is not inside a git repository" in wide_no_repo.stdout
    )
    arg = SESSION.run_gate(session_json(session_root()), args=["--scan"])
    arg_ok = arg.code == 1 and "BROKEN: misinvocation: unexpected argument --scan" in arg.stderr
    return all_of(
        [
            (no_dials_ok, f"no dials got: {no_dials.stdout!r} {no_dials.stderr[:200]!r}"),
            (from_sub_ok, f"no dials from a subfolder got: {from_sub.stdout!r} {from_sub.stderr[:200]!r}"),
            (no_repo_ok, f"no repository got: {no_repo.stdout!r} {no_repo.stderr[:200]!r}"),
            (wide_ok, f"a long folder name with a break, no dials, got: {wide.stdout!r}"),
            (
                wide_no_repo_ok,
                f"a long folder name with a break, no repository, got: {wide_no_repo.stdout!r}",
            ),
            (bad_ok, f"malformed dials got {bad.code}: {bad.stdout!r} {bad.stderr[:300]!r}"),
            (arg_ok, f"an argument got {arg.code}: {arg.stderr[:200]!r}"),
        ],
        "no dials and no repository said; malformed dials exit 1 with C4; an argument is a misinvocation",
    )


def session_start_absence_paths() -> tuple[bool, str]:
    """PyYAML missing is C2 first on stderr with the printer's closing line; python3 missing is C1;
    stdout stays empty in both."""
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_yaml = SESSION.run_gate(session_json(session_root()), env={"PYTHONPATH": str(shadow)})
    c2 = (
        "BROKEN: const-decision-records needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{MODULE_ROOT / 'requirements.txt'}' — until then the gate's state is not said at session start"
    )
    yaml_ok, yaml_said = broken_first_line(no_yaml, c2)
    yaml_ok = yaml_ok and messages.s1_could_not_run() in no_yaml.stderr and no_yaml.stdout == ""
    bin_dir = H.scratch_dir()
    (bin_dir / "sh").symlink_to(H.sh)
    (bin_dir / "dirname").symlink_to(shutil.which("dirname") or "dirname")
    no_python = SESSION.run_gate(session_json(session_root()), env={"PATH": str(bin_dir)})
    c1 = (
        "BROKEN: const-decision-records needs python3 — fix: install Python 3.12 or newer"
        " (https://www.python.org/downloads/) — until then the gate's state is not said at session start"
    )
    py_ok, py_said = broken_first_line(no_python, c1)
    py_ok = py_ok and messages.s1_could_not_run() in no_python.stderr and no_python.stdout == ""
    return all_of([(yaml_ok, yaml_said), (py_ok, py_said)], f"{yaml_said}; {py_said}")


def hooks_file_shape() -> tuple[bool, str]:
    """A SessionStart handler with no matcher and a PreToolUse handler on Write|Edit, exec form, the
    placeholder in args, timeouts."""
    hooks = json.loads((MODULE_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    start_hook = hooks["SessionStart"][0]
    write_hook = hooks["PreToolUse"][0]
    ok = (
        "matcher" not in start_hook
        and start_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"]
        and write_hook["matcher"] == "Write|Edit"
        and write_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/check-decision-record.sh"]
        and all(
            h["hooks"][0]["command"] == "sh" and isinstance(h["hooks"][0]["timeout"], int)
            for h in (start_hook, write_hook)
        )
    )
    return (
        ok,
        "SessionStart without matcher, PreToolUse on Write|Edit, exec form, timeouts"
        if ok
        else f"bad: {hooks}",
    )


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
    Assertion(18, "stakes routine and a missing decider: both taught, the count says two", routine_and_more),
    Assertion(19, "a document where policies live is never a record", policy_in_record_territory),
    Assertion(20, "C5: the root policy named as a record policy", root_named_as_record_policy),
    Assertion(21, "a record policy named twice counts once", policy_named_twice),
    Assertion(22, "C5: record_policies that is not a list", dials_bad_record_policies),
    Assertion(23, "C5: a record policy id that is not kebab-case", dials_record_policy_not_kebab),
    Assertion(24, "severity warn with a note: stdout stays one JSON object", severity_warn_with_note),
    Assertion(25, "scan: the finding with counts, exit 2, ignoring severity warn", scan_red),
    Assertion(26, "scan: green with counts; a governed non-record is never examined", scan_green),
    Assertion(27, "scan: 300 records in seconds (each document read once)", scan_scales),
    Assertion(
        28,
        "scan: a tracked file deleted from the working tree is left out, not a failure",
        scan_with_deleted_file,
    ),
    Assertion(
        35,
        "a record policy whose namespace declares no territory claims nothing: a note, never a failure",
        record_policy_claims_nothing,
    ),
    Assertion(36, "C5: a key of the namespace that is no dial is refused, never ignored", a_misspelt_dial),
    Assertion(37, "golden lines: each finding's headline, why and fix as literals", golden_lines),
    Assertion(
        38,
        "session start: nothing when named; the zero line when the dial is empty or absent",
        session_start_zero_line,
    ),
    Assertion(
        39,
        "session start: no dials file, no repository, malformed dials, an argument",
        session_start_skips_and_failures,
    ),
    Assertion(
        40,
        "the printer's absence paths: PyYAML missing is C2, python3 missing is C1",
        session_start_absence_paths,
    ),
    Assertion(41, "the hooks file's shape", hooks_file_shape),
]


def claim(territory: Sequence[str]) -> dict[str, object]:
    """The dials patch that gives the records policy another territory."""
    return {RECORDS_POLICY: {"territory": list(territory)}}


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=Write(RECORD_A, NO_ENVELOPE),
    red_finding=messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.NONE),
    territory=["docs/decisions/**"],
    green=shared.governed_by(RECORDS_POLICY),
    claim=claim,
    long_value=Write(RECORD_A, record(stakes="x" * 12_000)),
    # the skip reason once a negated pattern takes `red` out of the territory, typed by hand
    outside="docs/decisions/a.md is not governed by a record policy (records-policy)",
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
