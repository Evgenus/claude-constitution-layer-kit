#!/usr/bin/env python3
"""Fixtures of const-decision-records: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one — three policies, none of them for records — so
every item adds the records policy and names it in this module's dial: through the
case's setup for the red→green cases, through `gate_on` for the assertions.
"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.envelope import yaml_error_line  # noqa: E402
from const_gate.model import EnvelopeState, Finding  # noqa: E402
from consumer import Consumer, envelope  # noqa: E402
from decision_records_gate import messages, start  # noqa: E402
from harness import (  # noqa: E402
    Assertion,
    Case,
    Edit,
    Harness,
    Result,
    Write,
    broken_first_line,
    event_json,
    expect,
)
from shared_items import NO_ENVELOPE, Subject, shared_assertions  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-decision-record.sh", "check-decision-record.py", start.GATE.namespace)

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
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.INVALID, yaml_error("stakes: [unclosed")),
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
        SETUP,
    ),
    Case(
        6,
        "R2: a decider YAML reads as a number is blocked, and the message says to quote it",
        Write(RECORD_A, record(decider=42)),
        VALID,
        messages.r2_invalid_fields(RECORD_A, [shared.field_not_string("decider", "int")]),
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
        messages.r2_invalid_fields(RECORD_A, [shared.field_missing("decider")]),
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
        30,
        "R2: a missing type, and stakes YAML reads as a number, are taught by name",
        Write(RECORD_A, record(stakes=3, drop=("type",))),
        VALID,
        messages.r2_invalid_fields(
            RECORD_A, [shared.field_missing("type"), shared.field_not_string("stakes", "int")]
        ),
        SETUP,
    ),
    Case(
        31,
        "R1: an envelope that is YAML but no mapping of fields is blocked",
        Write(RECORD_A, "---\n- stakes\n- decider\n---\n"),
        VALID,
        messages.r1_no_readable_envelope(RECORD_A, EnvelopeState.INVALID, shared.detail_not_a_mapping()),
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
        SETUP,
    ),
    Case(
        32,
        "an Edit with replace_all is judged on the whole result",
        Edit(RECORD_A, "process", "high", replace_all=True),
        Edit(RECORD_A, "process", "product", replace_all=True),
        messages.r2_invalid_fields(RECORD_A, [messages.r2_stakes_not_allowed("high")]),
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
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_record_policies()), "stdout")


def dial_unset_scan() -> tuple[bool, str]:
    consumer = H.fresh_consumer()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_record_policies()), "stdout")


def not_a_record() -> tuple[bool, str]:
    result, _ = gate_on(Write(NOTE_A, NO_ENVELOPE))
    skip = messages.g1_skip_not_a_record(NOTE_A, [RECORDS_POLICY])
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


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
    return ok and "0 documents examined" in result.stdout, evidence


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
    return broken_first_line(result, messages.c5_record_policy_is_root("root-policy").render())


def policy_named_twice() -> tuple[bool, str]:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text({NAMESPACE: {"record_policies": [RECORDS_POLICY] * 2}}))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, messages.f9_scan_tail(0, 4, 1), "stdout")


def dials_bad_record_policies() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"record_policies": "records-policy"}})
    return broken_first_line(result, messages.c5_record_policies().render())


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
    tail = messages.f9_scan_tail(records=2, scanned=7, record_policies=1)
    return expect(_scan(bad=True), 2, shared.f9_count_scan(1, tail), "stdout")


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
    ok = result.code == 0 and "300 decision record(s) examined" in result.stdout and elapsed < 15
    return ok, f"300 records examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


def scan_with_deleted_file() -> tuple[bool, str]:
    """A tracked record deleted from the working tree, deletion not staged: not a document any more."""
    consumer = H.fresh_consumer((*SETUP, VALID, Write("docs/decisions/b.md", record("record-b"))))
    (consumer.root / RECORD_A).unlink()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 5, 1)), "stdout")


def long_value_is_cut() -> tuple[bool, str]:
    """A value a page long is echoed cut, so the whole verdict stays under the platform's cap."""
    result, _ = gate_on(Write(RECORD_A, record(stakes="x" * 12_000)))
    taught = messages.r2_invalid_fields(RECORD_A, [messages.r2_stakes_not_allowed("x" * 12_000)]).render()
    ok = result.code == 2 and taught in result.stderr and len(result.stderr) < 2_000
    return ok, f"exit {result.code}; {len(result.stderr)} characters on stderr for a 12,000-character value"


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
    Assertion(34, "an echoed value a page long is cut: the verdict stays a message", long_value_is_cut),
    Assertion(29, "message shape: every taught finding has what, why and fix", message_shape),
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
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
