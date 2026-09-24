#!/usr/bin/env python3
"""Fixtures of const-meta-types: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.
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
from const_gate.model import Finding, Match  # noqa: E402
from consumer import ROOT_POLICY, document, envelope  # noqa: E402
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
    red_lines,
)
from meta_types_gate import messages, start  # noqa: E402
from shared_items import NO_ENVELOPE, Subject, shared_assertions  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-governed-document.sh", "check-governed-document.py", start.GATE.namespace)
NAMESPACE = start.GATE.namespace

NOTE_A = "docs/notes/a.md"
SHARED = "docs/notes/shared/x.md"
ROOT_TERRITORY = ["docs/policies/**"]
NOTES = Match("notes-policy", "docs/notes/**")
SHARED_POLICY = Match("shared-policy", "docs/notes/shared/**")
F1_HEADLINE = "RED: docs/notes/a.md: no frontmatter envelope"  # typed by hand, as the gate prints it


def yaml_error(block: str) -> str:
    """What the gate will report for a YAML block that does not parse: the parser's own words."""
    try:
        yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return yaml_error_line(exc)
    raise AssertionError("the fixture block parses")


# ------------------------------------------------------------------ red → green cases

CASES = [
    Case(
        1,
        "F1: a document with no envelope is blocked; with one it passes",
        Write(NOTE_A, NO_ENVELOPE),
        Write(NOTE_A, envelope("note-a")),
        messages.f1_no_envelope(NOTE_A),
        "governed by notes-policy",
    ),
    Case(
        2,
        "F2: an envelope opened and never closed is blocked",
        Write(NOTE_A, "---\nid: note-a\n\n# Note A\n"),
        Write(NOTE_A, envelope("note-a")),
        messages.f2_unterminated(NOTE_A),
        "governed by notes-policy",
    ),
    Case(
        3,
        "F3: an envelope that is not valid YAML is blocked",
        Write(NOTE_A, "---\nid: [unclosed\n---\n"),
        Write(NOTE_A, envelope("note-a")),
        messages.f3_invalid_yaml(NOTE_A, yaml_error("id: [unclosed")),
        "governed by notes-policy",
    ),
    Case(
        4,
        "F4: invalid id, type and status are blocked in one message",
        Write(NOTE_A, document(id="Note_A", type="spec", title="Note A", status="open")),
        Write(NOTE_A, envelope("note-a")),
        messages.f4_invalid_fields(
            NOTE_A,
            [
                messages.f4_id_not_kebab("Note_A"),
                messages.f4_type_not_allowed("spec"),
                messages.f4_status_not_allowed("open"),
            ],
        ),
        "governed by notes-policy",
    ),
    Case(
        5,
        "F5: an id already carried by another governed document is blocked",
        Write("docs/notes/b.md", envelope("notes-policy")),
        Write("docs/notes/b.md", envelope("note-b")),
        messages.f5_duplicate_id("docs/notes/b.md", "notes-policy", "docs/policies/notes-policy.md"),
        "governed by notes-policy",
    ),
    Case(
        6,
        "F6 no policy: a declaration naming no policy is blocked; naming one, path mapping absent, passes",
        Write("loose.md", envelope("loose", policy="ghost-policy")),
        Write("loose.md", envelope("loose", policy="notes-policy")),
        messages.f6_no_such_policy("loose.md", "ghost-policy", ROOT_TERRITORY),
        "governed by notes-policy",
    ),
    Case(
        7,
        "F7 multi-policy: two territories and no declaration is blocked; declaring one of them passes",
        Write(SHARED, envelope("shared-x")),
        Write(SHARED, envelope("shared-x", policy="shared-policy")),
        messages.f7_multi_policy(SHARED, [NOTES, SHARED_POLICY]),
        "governed by shared-policy",
    ),
    Case(
        8,
        "F8 contradiction: a declaration against the path mapping is blocked; without it passes",
        Write(NOTE_A, envelope("note-a", policy="root-policy")),
        Write(NOTE_A, envelope("note-a")),
        messages.f8_contradiction(NOTE_A, "root-policy", NOTES, ROOT_TERRITORY),
        "governed by notes-policy",
    ),
    Case(
        9,
        "F8 contradiction naming no policy at all: the fix says so instead of pointing nowhere",
        Write(NOTE_A, envelope("note-a", policy="ghost-policy")),
        Write(NOTE_A, envelope("note-a")),
        messages.f8_contradiction(NOTE_A, "ghost-policy", NOTES, None),
        "governed by notes-policy",
    ),
    Case(
        10,
        "F8b contradiction in an overlap: a declaration naming neither claimant is blocked",
        Write(SHARED, envelope("shared-x", policy="root-policy")),
        Write(SHARED, envelope("shared-x", policy="notes-policy")),
        messages.f8b_contradiction_in_overlap(SHARED, "root-policy", [NOTES, SHARED_POLICY]),
        "governed by notes-policy",
    ),
    Case(
        11,
        "F10: a document where policies live must be current-state",
        Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "task-record")),
        Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "current-state")),
        messages.f10_policy_type("docs/policies/drafts-policy.md", "task-record", ROOT_TERRITORY),
        "governed by root-policy",
    ),
    Case(
        12,
        "F11: the root policy losing its envelope is a blocked write, never a non-blocking failure",
        Write(ROOT_POLICY, NO_ENVELOPE),
        Write(ROOT_POLICY, envelope("root-policy", "current-state")),
        messages.f11_root_unreadable(ROOT_POLICY, messages.f11_detail_no_envelope()),
        "governed by root-policy",
    ),
    Case(
        13,
        "F12: the root policy must stay current-state",
        Write(ROOT_POLICY, envelope("root-policy", "task-record")),
        Write(ROOT_POLICY, envelope("root-policy", "current-state")),
        messages.f12_root_type(ROOT_POLICY, "task-record"),
        "governed by root-policy",
    ),
    Case(
        14,
        "F13: the root policy renamed to an id with no namespace is blocked",
        Write(ROOT_POLICY, envelope("renamed-root", "current-state")),
        Write(ROOT_POLICY, envelope("root-policy", "current-state")),
        messages.f13_root_id_orphaned(ROOT_POLICY, "renamed-root"),
        "governed by root-policy",
    ),
    Case(
        15,
        "F14: the root policy renamed to a namespace that does not contain it is blocked, not let through",
        Write(ROOT_POLICY, envelope("notes-policy", "current-state")),
        Write(ROOT_POLICY, envelope("root-policy", "current-state")),
        messages.f14_root_breaks_governance(
            ROOT_POLICY,
            shared.c9_root_outside_own_territory(ROOT_POLICY, ["docs/notes/**"], "notes-policy"),
        ),
        "governed by root-policy",
    ),
    Case(
        16,
        "an Edit is judged on the document as it will be after the edit",
        Edit(NOTE_A, "type: non-authoritative\n", ""),
        Edit(NOTE_A, "# Fixture", "# Fixture, edited"),
        messages.f4_invalid_fields(NOTE_A, [shared.field_missing("type")]),
        "governed by notes-policy",
        setup=[Write(NOTE_A, envelope("note-a"))],
    ),
    Case(
        17,
        "an Edit that creates a file — no file yet, an empty old_string — is judged on what it creates",
        Edit(NOTE_A, "", NO_ENVELOPE),
        Edit(NOTE_A, "", envelope("note-a")),
        messages.f1_no_envelope(NOTE_A),
        "governed by notes-policy",
    ),
]

# ------------------------------------------------------------------ assertions


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
    if dials_patch is not None:
        consumer.dials.update(dials_patch)
        consumer.build()
    if raw_dials is not None:
        consumer.write("constitution.yaml", raw_dials)
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return H.run_gate(event_json(consumer.root, action), env=env), consumer.root


def own(**dials: object) -> dict[str, object]:
    return {NAMESPACE: dials}


VALID = Write(NOTE_A, envelope("note-a"))


def a_misspelt_dial() -> tuple[bool, str]:
    """A key of the namespace that is neither of the two is refused, never a setting ignored in
    silence — `severty:` for `severity:` would otherwise leave the default in force unseen."""
    result, _ = gate_on(VALID, dials_patch=own(severty="warn"))
    return broken_first_line(result, messages.c5_unknown_dial("severty").render())


def outside_territory() -> tuple[bool, str]:
    result, _ = gate_on(Write("README.md", NO_ENVELOPE))
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_outside_territory("README.md")), "stdout")


def void_territory() -> tuple[bool, str]:
    result, _ = gate_on(
        Write("docs/ghost/g.md", NO_ENVELOPE), dials_patch={"ghost": {"territory": ["docs/ghost/**"]}}
    )
    return expect(result, 0, messages.g1_skip_void_territory("docs/ghost/g.md", ["ghost"]), "stdout")


def module_named_policy() -> tuple[bool, str]:
    """A policy is a policy by where it lies, even when its id looks like a module's name."""
    result, _ = gate_on(
        Write("style/s.md", NO_ENVELOPE),
        dials_patch={"const-style": {"territory": ["style/**"]}},
        files={"docs/policies/const-style.md": envelope("const-style", "current-state")},
    )
    return expect(result, 2, messages.f1_no_envelope("style/s.md").render(), "stderr")


def ungoverned_twin_is_not_seen() -> tuple[bool, str]:
    """A file outside every territory that declares no policy is never consulted: the governed
    document's id standing in it is no duplicate (limit 4)."""
    result, _ = gate_on(VALID, files={"README.md": envelope("note-a")})
    return expect(result, 0, shared.g1_green_hook(shared.governed_by("notes-policy")), "stdout")


def _warn(files: dict[str, str] | None = None) -> tuple[Result, str]:
    result, _ = gate_on(Write(NOTE_A, NO_ENVELOPE), dials_patch=own(severity="warn"), files=files)
    return result, messages.f1_no_envelope(NOTE_A).headline


def severity_warn_with_note() -> tuple[bool, str]:
    """Under warn, stdout must be one JSON object and nothing else, or the finding reaches nobody."""
    twin = envelope("notes-policy", "current-state")
    result, _ = _warn(files={"docs/policies/zz-twin.md": twin})
    payload = json.loads(result.stdout)  # raises, and so fails, if a note precedes the JSON
    note = shared.n1_note_policy_id_shared(
        "docs/policies/notes-policy.md", "docs/policies/zz-twin.md", "notes-policy"
    )
    ok = result.code == 0 and note in payload["hookSpecificOutput"]["additionalContext"]
    return ok, "stdout parses as one JSON object; the note travels inside additionalContext"


def _scan(bad: bool) -> Result:
    consumer = H.fresh_consumer()
    consumer.dials.update({**own(severity="warn"), "ghost": {"territory": ["nowhere/**"]}})
    consumer.build()
    consumer.write(NOTE_A, NO_ENVELOPE if bad else envelope("note-a"))
    return H.run_gate("", args=["--scan", str(consumer.root)])


def scan_red() -> tuple[bool, str]:
    """Exactly the one finding and the count line, typed by hand: a finding of another kind, or one
    more, is red."""
    result = _scan(bad=True)
    wanted = [
        F1_HEADLINE,
        "RED: 1 finding(s) — 4 governed document(s) examined, 4 Markdown file(s) scanned, 3 policies",
    ]
    ok = result.code == 2 and red_lines(result.stdout) == wanted
    return (
        ok,
        f"exit 2: {wanted[1]}"
        if ok
        else f"wanted exit 2 and {wanted}; got exit {result.code}: {result.stdout}",
    )


def scan_green() -> tuple[bool, str]:
    result = _scan(bad=False)
    ok, evidence = expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(4, 4, 3)), "stdout")
    return ok and messages.n1_note_void_namespace(
        "ghost"
    ) in result.stdout, evidence + " + void-namespace note"


def scan_scales() -> tuple[bool, str]:
    """The scan reads each document once: a few hundred documents take seconds, not minutes."""
    consumer = H.fresh_consumer()
    for n in range(300):
        consumer.write(f"docs/notes/n{n}.md", envelope(f"note-{n}"))
    started = time.monotonic()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    elapsed = time.monotonic() - started
    line = (
        "GREEN: const-meta-types: 303 governed document(s) examined, 303 Markdown file(s) scanned, 3 policies"
    )
    ok = result.code == 0 and line in result.stdout.splitlines() and elapsed < 15
    return ok, f"303 documents examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


def scan_with_deleted_file() -> tuple[bool, str]:
    """A tracked document deleted from the working tree, deletion not staged: not a document any more."""
    consumer = H.fresh_consumer([Write(NOTE_A, envelope("note-a"))])
    (consumer.root / NOTE_A).unlink()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(3, 3, 3)), "stdout")


def fix_names_the_failing_field() -> tuple[bool, str]:
    """The fix of F4 names the field that failed and no other; the line is typed as printed."""
    result, _ = gate_on(
        Write(NOTE_A, document(id="note-a", type="non-authoritative", title="A", status="open"))
    )
    status_only = (
        "RED: docs/notes/a.md: envelope field(s) invalid: status 'open' not one of active | inactive\n"
        "  why: the envelope is the one place a document's authority is declared, and it is read by"
        " machines\n"
        "  fix: set the named field: status = active | inactive\n"
    )
    declared, _ = gate_on(Write(NOTE_A, envelope("note-a", policy="Not_Kebab")))
    policy_only = (
        "  fix: set the named field: policy = the kebab-case id of the governing policy, or no such line\n"
    )
    ok = (
        result.code == 2
        and status_only in result.stderr
        and "id = " not in result.stderr
        and declared.code == 2
        and policy_only in declared.stderr
    )
    return ok, "status alone: the status fragment; policy alone: the policy fragment" if ok else (
        f"{result.stderr}\n{declared.stderr}"
    )


def golden_f1_fix() -> tuple[bool, str]:
    """The F1 fix as a literal, typed here by hand: case 1 compares with what the message function
    returns, so a slip inside the function would pass it."""
    result, _ = gate_on(Write(NOTE_A, NO_ENVELOPE))
    literal = (
        "  fix: start the file with a YAML block between two '---' lines carrying at least id: <kebab-id>,"
        " type: current-state | task-record | non-authoritative, title: <one line>, status: active |"
        " inactive — the fields every governed document carries; its kind may add fields of its own"
    )
    return expect(result, 2, literal, "stderr")


def message_shape() -> tuple[bool, str]:
    built = [case.expect for case in CASES]
    ok = all(isinstance(f, Finding) and f.key and f.headline and f.why and f.fix for f in built)
    return ok, f"{len(built)} findings examined, each with what / why / fix"


ASSERTIONS = [
    Assertion(18, "examined count: outside claimed territory prints 0 and exits 0", outside_territory),
    Assertion(19, "a territory with no policy behind it claims nothing: a visible skip", void_territory),
    Assertion(
        20, "a policy whose id looks like a module's name still governs its territory", module_named_policy
    ),
    Assertion(22, "severity warn with a note: stdout stays one JSON object", severity_warn_with_note),
    Assertion(23, "scan: the finding with counts, exit 2, ignoring severity warn", scan_red),
    Assertion(24, "scan: green with counts, and a note per void namespace", scan_green),
    Assertion(25, "scan: 300 documents in seconds (each document read once)", scan_scales),
    Assertion(
        26,
        "scan: a tracked file deleted from the working tree is left out, not a failure",
        scan_with_deleted_file,
    ),
    Assertion(29, "golden line: the F1 fix as a literal, not as the function returns it", golden_f1_fix),
    Assertion(27, "message shape: every taught finding has what, why and fix", message_shape),
    Assertion(
        30, "an ungoverned twin id is not seen: the governed write is green", ungoverned_twin_is_not_seen
    ),
    Assertion(31, "C5: a key of the namespace that is no dial is refused, never ignored", a_misspelt_dial),
    Assertion(32, "the fix of F4 names only the field that failed", fix_names_the_failing_field),
]


def claim(territory: Sequence[str]) -> dict[str, object]:
    """The dials patch that gives the notes policy another territory."""
    return {"notes-policy": {"territory": list(territory)}}


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=Write(NOTE_A, NO_ENVELOPE),
    red_finding=messages.f1_no_envelope(NOTE_A),
    territory=["docs/notes/**"],
    green=shared.governed_by("notes-policy"),
    claim=claim,
    long_value=Write(NOTE_A, document(id="note-a", type="x" * 12_000, title="Note A", status="active")),
    # the skip reason once a negated pattern takes `red` out of the territory, typed by hand
    outside="docs/notes/a.md is outside claimed territory",
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
