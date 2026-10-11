#!/usr/bin/env python3
"""Fixtures of const-meta-types: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import yaml
from const_gate import identity
from const_gate import messages as shared
from const_gate.envelope import parse_envelope, yaml_error_line
from const_gate.model import Match, MetaType
from consumer import ROOT_POLICY, document, envelope
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
from meta_types_gate import messages, start
from meta_types_gate.checks import envelope_errors
from shared_items import NO_ENVELOPE, Subject, shared_assertions

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
H = Harness(SCRIPTS, "check-governed-document.sh", "check-governed-document.py", start.GATE.namespace)
NAMESPACE = start.GATE.namespace

NOTE_A = "docs/notes/a.md"
SHARED = "docs/notes/shared/x.md"
ROOT_TERRITORY = ["docs/policies/**"]
NOTES = Match("notes-policy", "docs/notes/**")
SHARED_POLICY = Match("shared-policy", "docs/notes/shared/**")
F1_HEADLINE = "RED: docs/notes/a.md: no frontmatter envelope"  # typed by hand, as the gate prints it
# the line after the count line of every red verdict (F10), typed by hand
F10_LINE = (
    "const-meta-types: load the skill const-meta-types:choose-meta-type before you fix this — it teaches"
    " the rule and the fix"
)
# the pointer line the module prints at session start and at every subagent's start, typed by hand
POINTER = (
    "const-meta-types (advisory): before creating a governed document or changing its type, and when a"
    " write is blocked for its envelope, load the skill const-meta-types:choose-meta-type."
)


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
        "F15: a document where policies live must be current-state",
        Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "task-record")),
        Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "current-state")),
        messages.f15_policy_type("docs/policies/drafts-policy.md", "task-record", ROOT_TERRITORY),
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
    Case(
        34,
        "F11: the root policy with an envelope opened and never closed is a blocked write",
        Write(ROOT_POLICY, "---\nid: root-policy\ntype: current-state\n\n# Root\n"),
        Write(ROOT_POLICY, envelope("root-policy", "current-state")),
        # typed by hand: the detail is not built by the message function
        messages.f11_root_unreadable(ROOT_POLICY, "opened with '---' but never closed"),
        "governed by root-policy",
    ),
    Case(
        35,
        "F4 carrying two errors: an id YAML reads as a bool and an empty title, in one finding",
        Write(
            NOTE_A, "---\nid: true\ntype: non-authoritative\ntitle: ''\nstatus: active\n---\n\n# Fixture\n"
        ),
        Write(NOTE_A, envelope("note-a")),
        messages.f4_invalid_fields(
            NOTE_A, [shared.field_not_string("id", "bool"), messages.f4_title_empty()]
        ),
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
    return broken_first_line(
        result,
        "BROKEN: constitution.yaml: const-meta-types.severty is no dial of this module — fix: a misspelt"
        " dial would be ignored in silence, so none is: write one of severity, log_dir",
    )


def outside_territory() -> tuple[bool, str]:
    result, _ = gate_on(Write("README.md", NO_ENVELOPE))
    plain = expect(result, 0, shared.g1_green_skip(messages.g1_skip_outside_territory("README.md")), "stdout")
    # a path of over 80 characters with a line break is said whole on one line, the break escaped
    wide, _ = gate_on(Write("a\n" + "b" * 100 + ".md", NO_ENVELOPE))
    line = (
        "GREEN: const-meta-types: 0 documents examined — a\\n"
        + "b" * 100
        + ".md is outside claimed territory"
    )
    wide_ok, wide_evidence = expect(wide, 0, line, "stdout")
    return (plain[0] and wide_ok, wide_evidence if plain[0] else plain[1])


VOID_KEY = "g\nh" + "o" * 100  # a namespace key with a line break, 103 characters
VOID_SHOWN = "g\\nh" + "o" * 77 + "… [103 characters]"  # the message's form of it, typed by hand


def void_territory() -> tuple[bool, str]:
    result, _ = gate_on(
        Write("docs/ghost/g.md", NO_ENVELOPE), dials_patch={"ghost": {"territory": ["docs/ghost/**"]}}
    )
    plain = expect(result, 0, messages.g1_skip_void_territory("docs/ghost/g.md", ["ghost"]), "stdout")
    # a namespace key holding a line break, over 80 characters, only points: cut, then escaped
    # and the path stands whole, its break escaped, over 80 characters
    wide, _ = gate_on(
        Write("docs/ghost/g\n" + "h" * 100 + ".md", NO_ENVELOPE),
        dials_patch={VOID_KEY: {"territory": ["docs/ghost/**"]}},
    )
    line = (
        "GREEN: const-meta-types: 0 documents examined — docs/ghost/g\\n" + "h" * 100 + ".md lies only in"
        f" the territory of namespace '{VOID_SHOWN}', which has no policy document behind it and so claims"
        " nothing"
    )
    wide_ok, wide_evidence = expect(wide, 0, line, "stdout")
    # two such namespaces: the plural line, the same path whole and the keys cut
    two, _ = gate_on(
        Write("docs/ghost/g\n" + "h" * 100 + ".md", NO_ENVELOPE),
        dials_patch={VOID_KEY: {"territory": ["docs/ghost/**"]}, "ghost": {"territory": ["docs/ghost/**"]}},
    )
    plural = (
        "GREEN: const-meta-types: 0 documents examined — docs/ghost/g\\n" + "h" * 100 + ".md lies only in"
        f" the territories of namespaces '{VOID_SHOWN}', 'ghost', none of which has a policy document behind"
        " it, so nothing is claimed"
    )
    two_ok, two_evidence = expect(two, 0, plural, "stdout")
    ok = plain[0] and wide_ok and two_ok
    return ok, plain[1] if not plain[0] else (wide_evidence if not wide_ok else two_evidence)


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


def _scan(bad: bool, void_key: str = "ghost") -> Result:
    consumer = H.fresh_consumer()
    consumer.dials.update({**own(severity="warn"), void_key: {"territory": ["nowhere/**"]}})
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
    # F10 closes the output, after the count line
    ok = result.code == 2 and red_lines(result.stdout) == wanted
    ok = ok and result.stdout.rstrip("\n").endswith(wanted[1] + "\n" + F10_LINE)
    return (
        ok,
        f"exit 2: {wanted[1]}"
        if ok
        else f"wanted exit 2 and {wanted}; got exit {result.code}: {result.stdout}",
    )


def scan_green() -> tuple[bool, str]:
    result = _scan(bad=False)
    ok, evidence = expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(4, 4, 3)), "stdout")
    note = messages.n2_note_void_namespace("ghost")
    # a namespace key with a line break and 103 characters: the note names it cut at 80 and escaped,
    # each time on the one line — typed by hand
    wide = _scan(bad=False, void_key=VOID_KEY)
    wide_note = (
        f"note: namespace '{VOID_SHOWN}' declares a territory but no policy with id '{VOID_SHOWN}' lies in"
        " the root policy's territory; it claims nothing until that policy exists"
    )
    return ok and note in result.stdout and wide_note in wide.stdout, evidence + " + void-namespace note"


def scan_scales() -> tuple[bool, str]:
    """A few hundred documents take seconds, not minutes: the bound is the wall time, 15 s."""
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
    long_title, _ = gate_on(
        Write(NOTE_A, document(id="note-a", type="non-authoritative", title="x" * 201, status="active"))
    )
    title_only = (  # typed by hand: the limit is named in the headline and taught in the fix
        "RED: docs/notes/a.md: envelope field(s) invalid: title longer than 200 characters\n"
        "  why: the envelope is the one place a document's authority is declared, and it is read by"
        " machines\n"
        "  fix: set the named field: title = one line of at most 200 characters\n"
    )
    edge, _ = gate_on(
        Write(NOTE_A, document(id="note-a", type="non-authoritative", title="x" * 200, status="active"))
    )
    # the hand-written fragments stay tied to the closed sets they gloss: a type added to the
    # enum is glossed, and each fragment's key is a field the checks report
    all_wrong = parse_envelope(document(id="X_", type="x", title="", status="x", policy="X_"))
    reported = {error.split(" ", 1)[0] for error in envelope_errors(all_wrong)}
    tied = all(
        meta_type.value in messages._FIELD_FIXES["type"] for meta_type in MetaType
    ) and reported == set(messages._FIELD_FIXES)
    ok = (
        result.code == 2
        and status_only in result.stderr
        and "id = " not in result.stderr
        and declared.code == 2
        and policy_only in declared.stderr
        and long_title.code == 2
        and title_only in long_title.stderr
        and edge.code == 0
        and tied
    )
    return ok, (
        "status alone: the status fragment; policy alone: the policy fragment; a title of 201 characters:"
        " the limit taught, of 200: green; the fragments tied to the enum and the fields"
        if ok
        else f"{result.stderr}\n{declared.stderr}\n{long_title.stderr}\n{edge.stderr}\n{reported}"
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


# The lines each case's red half prints, keyed by the case's number, typed here by hand: the cases
# compare with what the message functions return, so a slip inside a function — a why emptied, a
# word lost from a fix — would pass them all. F1's fix is item 29's, F4's why and one-field fix
# item 32's; F3's headline stops where the parser's own words begin; case 34's why and fix are
# case 12's, typed once.
GOLDEN: dict[int, Sequence[str]] = {
    1: [
        F1_HEADLINE,
        "  why: a governed document declares its authority in its envelope, or sessions guess it",
    ],
    2: [
        "RED: docs/notes/a.md: frontmatter opened with '---' but never closed",
        "  why: an unclosed envelope is unreadable by machines and by the next session",
        "  fix: close the YAML block with a line holding only '---'",
    ],
    3: [
        "RED: docs/notes/a.md: frontmatter is not valid YAML (",
        "  why: the envelope is read by machines, so it must parse",
        "  fix: repair the YAML between the '---' lines; keep at least the four fields id, type, title,"
        " status",
    ],
    4: [
        "RED: docs/notes/a.md: envelope field(s) invalid: id 'Note_A' is not kebab-case; type 'spec' not one"
        " of current-state | task-record | non-authoritative; status 'open' not one of active | inactive",
        "  fix: set each named field: id = stable kebab-case (never changed, never reused); type ="
        " current-state (reconciled truth) | task-record (change delta) | non-authoritative (explanation);"
        " status = active | inactive",
    ],
    5: [
        "RED: docs/notes/b.md: id 'notes-policy' is already carried by docs/policies/notes-policy.md",
        "  why: an id is a stable identifier: two documents sharing one break every reference to it",
        "  fix: give this document its own id, never a retired one; if this is a move, delete or git mv the"
        " old file first, then write",
    ],
    6: [
        "RED: loose.md: declares policy 'ghost-policy' but no policy with that id lies in the root policy's"
        " territory ['docs/policies/**']",
        "  why: a governed document resolves to exactly one governing policy, or its rules are undefined",
        "  fix: declare the id of a policy that exists there, or drop the declaration and place the file in"
        " a claimed territory",
    ],
    7: [
        "RED: docs/notes/shared/x.md: matched by 2 policy territories: notes-policy (docs/notes/**),"
        " shared-policy (docs/notes/shared/**)",
        "  why: a document resolves to exactly one governing policy, or two rule sets compete",
        "  fix: narrow one territory in constitution.yaml so the patterns no longer overlap; during a move,"
        " declare the intended one with 'policy: <id>' in the envelope while an active task-record covers it",
    ],
    8: [
        "RED: docs/notes/a.md: declares policy 'root-policy' but its path is claimed by 'notes-policy'"
        " (docs/notes/**)",
        "  why: the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never"
        " override it",
        "  fix: remove 'policy: root-policy' from the envelope, or move the file into the territory of"
        " 'root-policy': ['docs/policies/**']",
    ],
    9: ["  fix: remove 'policy: ghost-policy' from the envelope — no policy with that id exists"],
    10: [
        "RED: docs/notes/shared/x.md: declares policy 'root-policy' but its path is claimed by notes-policy"
        " (docs/notes/**), shared-policy (docs/notes/shared/**)",
        "  why: the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never"
        " override it",
        "  fix: declare one of the policies that claim the path, or remove the declaration and narrow the"
        " territories in constitution.yaml",
    ],
    11: [
        "RED: docs/policies/drafts-policy.md: lies in the root policy's territory but has type 'task-record'",
        "  why: a policy is a current-state document, and only policies lie where policies live",
        "  fix: set type: current-state, or move the file out of ['docs/policies/**']",
    ],
    12: [
        "RED: docs/policies/root-policy.md: the root policy has no readable envelope (the file does not"
        " start with a '---' line)",
        "  why: the root policy's id names the namespace where policies live; without it nothing is governed",
        "  fix: keep the YAML block between two '---' lines with id, type: current-state, title, status:"
        " active",
    ],
    13: [
        "RED: docs/policies/root-policy.md: the root policy has type 'task-record'",
        "  why: a policy is a current-state document, and the root is the policy for policies",
        "  fix: set type: current-state",
    ],
    14: [
        "RED: docs/policies/root-policy.md: the root policy's id 'renamed-root' has no territory under that"
        " id in constitution.yaml",
        "  why: the root's namespace is where policies live; changing the id orphans every policy",
        "  fix: keep the id that has the namespace, or rename the namespace in constitution.yaml in the same"
        " change",
    ],
    15: [
        "RED: docs/policies/root-policy.md: as written, root policy 'docs/policies/root-policy.md' lies"
        " outside its own territory ['docs/notes/**']",
        "  why: every chain of governance ends at the root policy; a write that breaks it ungoverns the"
        " repository",
        "  fix: every chain of governance ends at the root; widen notes-policy.territory to include it",
    ],
    34: [
        "RED: docs/policies/root-policy.md: the root policy has no readable envelope (opened with '---' but"
        " never closed)",
    ],
    35: [
        "RED: docs/notes/a.md: envelope field(s) invalid: id must be a quoted string (YAML read it as bool);"
        " title empty",
        "  fix: set each named field: id = stable kebab-case (never changed, never reused); title = one"
        " line of at most 200 characters",
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
        if not stderr.endswith("\n" + F10_LINE + "\n"):
            missing.append(f"case {number}: the stderr does not end with F10: {F10_LINE}")
    # an id, a type, a status and a declared policy holding a line break stay on one line, each break
    # shown escaped, typed by hand
    breaks = H.run_gate(
        event_json(
            H.fresh_consumer().root,
            Write(
                NOTE_A,
                document(id="a\nb", type="c\nd", title="A", status="e\nf", policy="g\nh"),
            ),
        )
    ).stderr
    escaped = (
        "RED: docs/notes/a.md: envelope field(s) invalid: id 'a\\nb' is not kebab-case; type 'c\\nd' not"
        " one of current-state | task-record | non-authoritative; status 'e\\nf' not one of active |"
        " inactive; policy 'g\\nh' is not a kebab-case policy id"
    )
    if escaped not in breaks:
        missing.append(f"escaped values: {escaped}")
    # the same four values at 100 characters only point: each cut at 80, the cut said
    long_values = H.run_gate(
        event_json(
            H.fresh_consumer().root,
            Write(
                NOTE_A, document(id="I" * 100, type="t" * 100, title="A", status="s" * 100, policy="P" * 100)
            ),
        )
    ).stderr
    cut_head = "… [100 characters]'"
    cut = (
        f"RED: docs/notes/a.md: envelope field(s) invalid: id '{'I' * 80}{cut_head} is not kebab-case;"
        f" type '{'t' * 80}{cut_head} not one of current-state | task-record | non-authoritative;"
        f" status '{'s' * 80}{cut_head} not one of active | inactive;"
        f" policy '{'P' * 80}{cut_head} is not a kebab-case policy id"
    )
    if cut not in long_values:
        missing.append(f"cut values: {cut}")
    # a written file's path stands whole, over 80 characters, its break escaped; a YAML error keeps its
    # text and shows its backslash doubled; an id or a declared policy that only points is cut at 80
    weird = "docs/notes/a\n" + "b" * 100 + ".md"
    shown = "docs/notes/a\\n" + "b" * 100 + ".md"
    other = "docs/notes/o\n" + "x" * 100 + ".md"
    shown_other = "docs/notes/o\\n" + "x" * 100 + ".md"
    long_id = "d" * 100
    cut_id = "d" * 80 + "… [100 characters]"
    ghost = "g" * 100
    cut_ghost = "g" * 80 + "… [100 characters]"
    runs: list[tuple[str, Write, str, list[Write]]] = [
        ("F1 path", Write(weird, NO_ENVELOPE), f"RED: {shown}: no frontmatter envelope", []),
        (
            "F3 yaml",
            Write(NOTE_A, '---\nid: "x\\q"\n---\n'),
            "RED: docs/notes/a.md: frontmatter is not valid YAML (while scanning a double-quoted scalar in"
            ' "<unicode string>", line 1, column 5: id: "x\\\\q" ^ found unknown escape character \'q\' in'
            ' "<unicode string>", line 1, column 8: id: "x\\\\q" ^)',
            [],
        ),
        (
            "F5 id and path",
            Write(NOTE_A, envelope(long_id)),
            f"RED: docs/notes/a.md: id '{cut_id}' is already carried by {shown_other}",
            [Write(other, envelope(long_id))],
        ),
        (
            "F6 declared",
            Write("loose.md", envelope("loose", policy=ghost)),
            f"RED: loose.md: declares policy '{cut_ghost}' but no policy with that id lies in the root"
            " policy's territory ['docs/policies/**']",
            [],
        ),
        (
            "F8 declared, headline",
            Write(NOTE_A, envelope("note-a", policy=ghost)),
            f"RED: docs/notes/a.md: declares policy '{cut_ghost}' but its path is claimed by 'notes-policy'"
            " (docs/notes/**)",
            [],
        ),
        (
            "F8 declared, fix",
            Write(NOTE_A, envelope("note-a", policy=ghost)),
            f"  fix: remove 'policy: {cut_ghost}' from the envelope — no policy with that id exists",
            [],
        ),
        (
            "F13 root id",
            Write(ROOT_POLICY, envelope("r" * 100, "current-state")),
            "RED: docs/policies/root-policy.md: the root policy's id '"
            + "r" * 80
            + "… [100 characters]' has no territory under that id in constitution.yaml",
            [],
        ),
    ]
    runs.append(
        (
            "F11 yaml",
            Write(ROOT_POLICY, '---\nid: "x\\q"\n---\n'),
            "RED: docs/policies/root-policy.md: the root policy has no readable envelope (while scanning a"
            ' double-quoted scalar in "<unicode string>", line 1, column 5: id: "x\\\\q" ^ found unknown'
            ' escape character \'q\' in "<unicode string>", line 1, column 8: id: "x\\\\q" ^)',
            [],
        )
    )
    for label, action, wanted, setup in runs:
        said = H.run_gate(event_json(H.fresh_consumer(setup).root, action)).stderr
        if wanted not in said:
            missing.append(f"{label}: {wanted}")
    # every finding about a written file opens with its path whole, however long, the break escaped: the
    # red half of each case, its target renamed to a name of 106 characters holding a line break
    cases_by_number = {case.number: case for case in CASES}
    found_paths = 0
    for number in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 35):
        case = cases_by_number[number]
        assert isinstance(case.red, Write)
        folder, _, _ = case.red.target.rpartition("/")
        renamed = (folder + "/" if folder else "") + "a\n" + "b" * 100 + ".md"
        said = H.run_gate(event_json(H.fresh_consumer(case.setup).root, Write(renamed, case.red.text))).stderr
        head = "RED: " + renamed.replace("\n", "\\n") + ": "
        found_paths += 1
        if not said.startswith(head):
            missing.append(f"case {number} with a long path: {head} — got {said[:300]}")
    # the same for the root policy's own findings: the root policy dial points at a file of that kind
    shown_root = "docs/policies/r\\n" + "s" * 100 + ".md"
    root = "docs/policies/r\n" + "s" * 100 + ".md"
    for number in (12, 13, 14, 15, 34):
        case = cases_by_number[number]
        assert isinstance(case.red, Write)
        result, _ = gate_on(
            Write(root, case.red.text),
            dials_patch={"root_policy": root},
            files={root: envelope("root-policy", "current-state")},
            remove=ROOT_POLICY,
        )
        found_paths += 1
        if not result.stderr.startswith(f"RED: {shown_root}: "):
            missing.append(f"case {number} with a long root path: {result.stderr[:300]}")
    # a policy id and a territory pattern of 100 characters or more only point: cut at 80, the cut said
    long_id = "p" * 100
    pattern = "docs/notes/" + "a" * 100 + ".md"
    cut_policy = "p" * 80 + "… [100 characters]"
    cut_pattern = "docs/notes/" + "a" * 69 + "… [114 characters]"
    twin = {f"docs/policies/{long_id}.md": envelope(long_id, "current-state")}
    overlap: dict[str, object] = {long_id: {"territory": [pattern]}}
    mark = f"{cut_policy} ({cut_pattern})"
    for label, doc, wanted in (
        ("F7", envelope("note-a"), f"matched by 2 policy territories: notes-policy (docs/notes/**), {mark}"),
        (
            "F8b",
            envelope("note-a", policy="root-policy"),
            f"declares policy 'root-policy' but its path is claimed by notes-policy (docs/notes/**), {mark}",
        ),
    ):
        said = gate_on(Write(pattern, doc), dials_patch=overlap, files=twin)[0].stderr
        found_paths += 1
        if wanted not in said:
            missing.append(f"{label} long policy and pattern: {wanted} — got {said[:400]}")
    single = "docs/other/" + "c" * 100 + ".md"
    alone: dict[str, object] = {long_id: {"territory": [single]}}
    said = gate_on(Write(single, envelope("note-a", policy="root-policy")), dials_patch=alone, files=twin)[
        0
    ].stderr
    wanted = (
        f"declares policy 'root-policy' but its path is claimed by '{cut_policy}' ("
        + "docs/other/"
        + "c" * 69
        + "… [114 characters])"
    )
    found_paths += 1
    if wanted not in said:
        missing.append(f"F8 long policy and pattern: {wanted} — got {said[:400]}")
    # a declared policy of 100 characters that exists and claims elsewhere: cut in the headline, in the
    # fix's removal line and in the fix's pointer to its territory
    declared = "q" * 100
    cut_declared = "q" * 80 + "… [100 characters]"
    elsewhere: dict[str, object] = {declared: {"territory": ["docs/other/**"]}}
    home = {f"docs/policies/{declared}.md": envelope(declared, "current-state")}
    said = gate_on(Write(NOTE_A, envelope("note-a", policy=declared)), dials_patch=elsewhere, files=home)[
        0
    ].stderr
    for label, wanted in (
        (
            "F8 headline",
            f"RED: docs/notes/a.md: declares policy '{cut_declared}' but its path is claimed by"
            " 'notes-policy' (docs/notes/**)",
        ),
        (
            "F8 fix",
            f"  fix: remove 'policy: {cut_declared}' from the envelope, or move the file into the territory"
            f" of '{cut_declared}': ['docs/other/**']",
        ),
    ):
        found_paths += 1
        if wanted not in said:
            missing.append(f"{label} with a declared policy of 100 characters: {wanted} — got {said[:400]}")
    said = gate_on(Write(pattern, envelope("note-a", policy=declared)), dials_patch=overlap, files=twin)[
        0
    ].stderr
    wanted = (
        f"declares policy '{cut_declared}' but its path is claimed by notes-policy (docs/notes/**), {mark}"
    )
    found_paths += 1
    if wanted not in said:
        missing.append(f"F8b with a declared policy of 100 characters: {wanted} — got {said[:400]}")
    found = sum(len(lines) for lines in GOLDEN.values()) + len(runs) + found_paths
    return not missing, f"{found} literal lines found" if not missing else "not found:\n" + "\n".join(missing)


def unreadable_twin_is_broken() -> tuple[bool, str]:
    """Any Markdown file git lists and nobody can read may carry the written id — its declaration
    cannot be known — so a governed write is the shared configuration failure, never a green that
    compared the id with nothing. A write outside every territory, with the same file unreadable,
    is still the plain skip: the others are read only for a governed document. Lines typed by hand."""
    as_root = (
        "NOT EXERCISED: running as root, where a mode bit does not deny a read — 0 unreadable files examined"
    )
    if os.geteuid() == 0:
        return True, as_root
    twin = "docs/notes/twin.md"
    consumer = H.fresh_consumer([Write(twin, envelope("note-a"))])
    path = consumer.root / twin
    mode = path.stat().st_mode
    path.chmod(0o000)
    try:
        governed = H.run_gate(event_json(consumer.root, VALID))
        outside = H.run_gate(event_json(consumer.root, Write("README.md", NO_ENVELOPE)))
    finally:
        path.chmod(mode)
    first = (
        "BROKEN: docs/notes/twin.md is listed by git but cannot be read — fix: check that the file can be"
        " read: its permissions, or a link that leads nowhere"
    )
    count = "BROKEN: the check could not run — 0 documents examined"
    ok, detail = broken_first_line(governed, first)
    if ok and count not in governed.stderr.splitlines():
        return False, f"no count line in stderr: {governed.stderr}"
    if not ok:
        return ok, detail
    skip = "GREEN: const-meta-types: 0 documents examined — README.md is outside claimed territory"
    skipped, skip_detail = expect(outside, 0, skip, "stdout")
    return skipped, f"{detail}; README.md: {skip_detail}"


def hooks_file_shape() -> tuple[bool, str]:
    """The hooks file: the gate on Write and Edit, kept as it was, and the two handlers of the
    pointer — one at session start, one at a subagent's start — each in exec form `sh`, with no
    matcher, an integer timeout and a script that is there."""
    spec = json.loads((SCRIPTS.parent / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    if sorted(spec) != ["PreToolUse", "SessionStart", "SubagentStart"]:
        return False, f"events: {sorted(spec)}"
    wanted: dict[str, tuple[str | None, list[str], int | None]] = {
        "PreToolUse": ("Write|Edit", ["${CLAUDE_PLUGIN_ROOT}/scripts/check-governed-document.sh"], 30),
        "SessionStart": (None, ["${CLAUDE_PLUGIN_ROOT}/scripts/print-skill-pointer.sh"], None),
        "SubagentStart": (
            None,
            ["${CLAUDE_PLUGIN_ROOT}/scripts/print-skill-pointer.sh", "--subagent"],
            None,
        ),
    }
    for event, (matcher, args, timeout) in wanted.items():
        groups = spec[event]
        if len(groups) != 1 or groups[0].get("matcher") != matcher or len(groups[0]["hooks"]) != 1:
            return False, f"{event}: {groups}"
        handler = groups[0]["hooks"][0]
        timeout_ok = (
            handler["timeout"] == timeout
            if timeout is not None
            else isinstance(handler["timeout"], int) and not isinstance(handler["timeout"], bool)
        )
        script = SCRIPTS / Path(args[0]).name
        if (
            handler["type"] != "command"
            or handler["command"] != "sh"
            or handler["args"] != args
            or not timeout_ok
            or not script.is_file()
        ):
            return False, f"{event}: {handler}"
    return (
        True,
        "PreToolUse kept; SessionStart and SubagentStart: sh, no matcher, integer timeout, script present",
    )


def skill_pointer_printed() -> tuple[bool, str]:
    """The pointer, run through sh: exit 0, the line as typed here and nothing on stderr; with
    `--subagent` one JSON object whose `hookSpecificOutput` is the event's name and the line; the
    size the module document states; and the skill it names a folder of this plugin."""
    script = str(SCRIPTS / "print-skill-pointer.sh")
    plain = subprocess.run([H.sh, script], capture_output=True, text=True, check=False)
    if plain.returncode != 0 or plain.stdout != POINTER + "\n" or plain.stderr != "":
        return False, repr(plain)
    nested = subprocess.run([H.sh, script, "--subagent"], capture_output=True, text=True, check=False)
    if nested.returncode != 0 or nested.stderr != "":
        return False, repr(nested)
    payload = json.loads(nested.stdout)
    wanted = {"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": POINTER}}
    if payload != wanted or nested.stdout.count("\n") != 1:
        return False, f"the subagent form is {nested.stdout!r}"
    size = len(POINTER)
    stated = re.search(
        r"pointer line, (\d+) characters", (SCRIPTS.parent / "MODULE.md").read_text(encoding="utf-8")
    )
    if not stated or int(stated.group(1)) != size:
        return False, f"the module document states another size than {size}"
    named = re.search(r"load the skill const-meta-types:([a-z-]+)\.$", POINTER)
    if not named or not (SCRIPTS.parent / "skills" / named.group(1) / "SKILL.md").is_file():
        return False, "the line names no skill of this plugin"
    return (
        True,
        f"exit 0, the line as typed, {size} characters as the module document states, one JSON object",
    )


# the pointer to the governing policy (N3), typed by hand: with the Enforcement anchor, and without it
POINTED = (
    "const-meta-types (advisory): this document is governed by docs/policies/notes-policy.md — read its"
    " rules before further edits; what review holds is its Enforcement rule (#r6)"
)
POINTED_PLAIN = (
    "const-meta-types (advisory): this document is governed by docs/policies/root-policy.md — read its"
    " rules before further edits"
)
ENFORCEMENT_RULE = (
    '6. <a id="r6"></a>**Enforcement.** The envelope by the write-time guard; the rest is review.\n'
)


def policy_pointer_once_per_session() -> tuple[bool, str]:
    """The green of a write in claimed territory points the session at the governing policy once:
    the first such write of a session prints one JSON object whose context holds the pointer, with
    the anchor of the policy's rule named Enforcement, then the green line; the next write of the
    same session for the same policy prints the green line plain; another session, another policy,
    the same session in another repository, an Edit each earn their own; with two Enforcement rules
    the first is named; a write outside territory, a red, a warn and a scan earn none; an index note
    stands before the pointer; the memo beside the output log holds the session, the repository and
    the policy, keeps its last lines, and with no home — no log_dir, no data directory — or no
    session nothing is pointed; a memo that cannot be written or read is said again, the verdict
    green, the unreadable one reported not exercised as root. Every line typed by hand."""
    data = H.scratch_dir()
    env = {"CLAUDE_PLUGIN_DATA": str(data)}
    consumer = H.fresh_consumer()
    consumer.write(
        "docs/policies/notes-policy.md", envelope("notes-policy", "current-state") + "\n" + ENFORCEMENT_RULE
    )
    root = consumer.root
    green = "GREEN: const-meta-types: 1 document examined, governed by notes-policy"

    def run(action: Write | Edit, session: str, env: dict[str, str] = env) -> Result:
        return H.run_gate(event_json(root, action, session=session), env=env)

    def context(result: Result) -> str | None:
        """The additionalContext of one JSON object on stdout, or None for anything else."""
        try:
            payload = json.loads(result.stdout)
        except ValueError:
            return None
        specific = payload.get("hookSpecificOutput", {}) if isinstance(payload, dict) else {}
        if (
            result.code != 0
            or specific.get("hookEventName") != "PreToolUse"
            or result.stdout.count("\n") != 1
        ):
            return None
        found = specific.get("additionalContext")
        return found if isinstance(found, str) else None

    checks: list[tuple[str, bool]] = []
    first = run(VALID, "s1")
    checks.append(
        (
            "first write of s1: the pointer with the anchor, then the green line",
            context(first) == f"{POINTED}\n{green}",
        )
    )
    second = run(VALID, "s1")
    checks.append(
        (
            "second write of s1: the green line plain, no JSON",
            second.code == 0 and second.stdout == green + "\n",
        )
    )
    # the same session in another repository is pointed again: the memo keys on the repository too
    other_root = H.fresh_consumer().root
    elsewhere = H.run_gate(event_json(other_root, VALID, session="s1"), env=env)
    checks.append(("the same session, another repository: pointed again", context(elsewhere) is not None))
    other_session = run(VALID, "s2")
    checks.append(("first write of s2: pointed again", context(other_session) == f"{POINTED}\n{green}"))
    consumer.write(NOTE_A, envelope("note-a"))  # an Edit is applied to the file on disk
    edited = run(Edit(NOTE_A, "# Fixture", "# Fixture, edited"), "s3")
    checks.append(("an Edit is pointed too", context(edited) == f"{POINTED}\n{green}"))
    plain_policy = run(
        Write("docs/policies/drafts-policy.md", envelope("drafts-policy", "current-state")), "s1"
    )
    root_green = "GREEN: const-meta-types: 1 document examined, governed by root-policy"
    checks.append(
        (
            "a policy with no Enforcement rule: the path alone",
            context(plain_policy) == f"{POINTED_PLAIN}\n{root_green}",
        )
    )
    outside = run(Write("README.md", NO_ENVELOPE), "s4")
    checks.append(
        (
            "outside territory: the skip line plain",
            outside.code == 0
            and outside.stdout
            == "GREEN: const-meta-types: 0 documents examined — README.md is outside claimed territory\n",
        )
    )
    red = run(Write(NOTE_A, NO_ENVELOPE), "s4")
    checks.append(("a red earns no pointer", red.code == 2 and "advisory" not in red.stdout + red.stderr))
    memo = data / "const-meta-types.pointed"
    lines = memo.read_text(encoding="utf-8").splitlines() if memo.is_file() else []
    wanted = [
        f"s1\t{root}\tdocs/policies/notes-policy.md",
        f"s1\t{other_root}\tdocs/policies/notes-policy.md",
        f"s2\t{root}\tdocs/policies/notes-policy.md",
        f"s3\t{root}\tdocs/policies/notes-policy.md",
        f"s1\t{root}\tdocs/policies/root-policy.md",
    ]
    checks.append(
        ("the memo holds session, repository and policy, tab-separated, one line each", lines == wanted)
    )
    # the memo keeps its last 200 lines: 300 lines of other sessions, then one pointer, leaves 200
    memo.write_text("".join(f"old-{n}\tx\ty\n" for n in range(300)), encoding="utf-8")
    capped = run(VALID, "s5")
    kept = memo.read_text(encoding="utf-8").splitlines()
    checks.append(
        (
            "the memo keeps its last 200 lines",
            context(capped) is not None
            and len(kept) == 200
            and kept[-1] == f"s5\t{root}\tdocs/policies/notes-policy.md"
            and kept[0] == "old-101\tx\ty",
        )
    )
    # no session in the event: nothing pointed, the green line plain
    nameless = run(VALID, "")
    checks.append(
        (
            "an event with no session: the green line plain",
            nameless.code == 0 and nameless.stdout == green + "\n",
        )
    )
    # no home for the memo: nothing pointed
    homeless = H.run_gate(event_json(root, VALID, session="s6"))
    checks.append(
        (
            "no log_dir and no data directory: the green line plain, nothing pointed",
            homeless.code == 0 and homeless.stdout == green + "\n",
        )
    )
    # log_dir set: the memo lives beside the log inside the repository
    logged = H.fresh_consumer()
    logged.dials.update(own(log_dir=".gate-logs"))
    logged.build()
    logged.write(".gitignore", ".gate-logs/\n")
    in_repo = H.run_gate(event_json(logged.root, VALID, session="s7"))
    beside = logged.root / ".gate-logs" / "const-meta-types.pointed"
    checks.append(
        (
            "log_dir: the memo beside the log, and the pointer said",
            context(in_repo) is not None
            and beside.is_file()
            and beside.read_text(encoding="utf-8") == f"s7\t{logged.root}\tdocs/policies/notes-policy.md\n",
        )
    )
    # with a note of the index — a second policy document carrying the notes policy's id — the note
    # stands first, the pointer after it, the green line last, typed by hand
    noted = H.fresh_consumer()
    noted.write("docs/policies/zz-twin.md", envelope("notes-policy", "current-state"))
    with_note = H.run_gate(event_json(noted.root, VALID, session="s8"), env=env)
    note = (
        "note: docs/policies/notes-policy.md and docs/policies/zz-twin.md both carry id 'notes-policy'; the"
        " first claims, the second is ignored"
    )
    pointed_notes = POINTED_PLAIN.replace(
        "root-policy", "notes-policy"
    )  # no Enforcement rule in this consumer
    checks.append(
        (
            "the pointer after the index's note, before the green line",
            context(with_note) == f"{note}\n{pointed_notes}\n{green}",
        )
    )
    # a warn carries no pointer: the finding's context, the warn note last; a scan carries none
    warned = H.fresh_consumer()
    warned.dials.update(own(severity="warn"))
    warned.build()
    at_warn = H.run_gate(event_json(warned.root, Write(NOTE_A, NO_ENVELOPE), session="s9"), env=env)
    warn_context = json.loads(at_warn.stdout)["hookSpecificOutput"]["additionalContext"]
    checks.append(("a warn carries no pointer", at_warn.code == 0 and "advisory" not in warn_context))
    scanned = H.run_gate("", args=["--scan", str(root)], env=env)
    checks.append(("a scan carries no pointer", scanned.code == 0 and "advisory" not in scanned.stdout))
    # two rules named Enforcement: the first is named
    twice = H.fresh_consumer()
    twice.write(
        "docs/policies/notes-policy.md",
        envelope("notes-policy", "current-state")
        + '\n3. <a id="r3"></a>**Enforcement** review.\n'
        + ENFORCEMENT_RULE,
    )
    first_rule = H.run_gate(event_json(twice.root, VALID, session="s10"), env=env)
    checks.append(
        (
            "two Enforcement rules: the first is named",
            context(first_rule) == f"{POINTED.replace('#r6', '#r3')}\n{green}",
        )
    )
    # a memo that cannot be written: the line said on every write, the verdict unchanged
    blocked = H.scratch_dir()
    (blocked / "const-meta-types.pointed").mkdir()  # a directory where the memo file should be
    blocked_env = {"CLAUDE_PLUGIN_DATA": str(blocked)}
    once = run(VALID, "s11", blocked_env)
    again = run(VALID, "s11", blocked_env)
    checks.append(
        (
            "a memo that cannot be written: said again, the verdict green",
            context(once) == f"{POINTED}\n{green}" and context(again) == f"{POINTED}\n{green}",
        )
    )
    # a memo that cannot be read: the line said on every write, the verdict green; a mode bit does not
    # stop root, so there the case is reported not exercised
    not_exercised = ""
    if os.geteuid() == 0:
        not_exercised = (
            "; NOT EXERCISED: a memo that cannot be read, running as root — 0 unreadable memos examined"
        )
    else:
        sealed = H.scratch_dir()
        sealed_memo = sealed / "const-meta-types.pointed"
        sealed_memo.write_text(f"s12\t{root}\tdocs/policies/notes-policy.md\n", encoding="utf-8")
        sealed_memo.chmod(0o000)
        try:
            unread = run(VALID, "s12", {"CLAUDE_PLUGIN_DATA": str(sealed)})
        finally:
            sealed_memo.chmod(0o644)
        checks.append(
            (
                "a memo that cannot be read: said again, the verdict green",
                context(unread) == f"{POINTED}\n{green}",
            )
        )
    failed = [title for title, ok in checks if not ok]
    return not failed, f"{len(checks)} checks{not_exercised}" if not failed else "failed: " + "; ".join(
        failed
    ) + f"\nfirst run: {first.stdout}{first.stderr}"


ASSERTIONS = [
    Assertion(
        39,
        "the pointer to the governing policy: on a green write, once per session, repository and policy",
        policy_pointer_once_per_session,
    ),
    Assertion(18, "examined count: outside claimed territory prints 0 and exits 0", outside_territory),
    Assertion(19, "a territory with no policy behind it claims nothing: a visible skip", void_territory),
    Assertion(
        20, "a policy whose id looks like a module's name still governs its territory", module_named_policy
    ),
    Assertion(22, "severity warn with a note: stdout stays one JSON object", severity_warn_with_note),
    Assertion(23, "scan: the finding with counts, exit 2, ignoring severity warn", scan_red),
    Assertion(24, "scan: green with counts, and a note per void namespace", scan_green),
    Assertion(25, "scan: 300 documents in under 15 s, the green line whole", scan_scales),
    Assertion(
        26,
        "scan: a tracked file deleted from the working tree is left out, not a failure",
        scan_with_deleted_file,
    ),
    Assertion(29, "golden line: the F1 fix as a literal, not as the function returns it", golden_f1_fix),
    Assertion(
        30, "an ungoverned twin id is not seen: the governed write is green", ungoverned_twin_is_not_seen
    ),
    Assertion(31, "C5: a key of the namespace that is no dial is refused, never ignored", a_misspelt_dial),
    Assertion(32, "the fix of F4 names only the field that failed", fix_names_the_failing_field),
    Assertion(33, "golden lines: each finding's headline, why and fix as literals", golden_lines),
    Assertion(
        36,
        "hook: a listed Markdown file nobody can read is C12.10 for a governed write, never a green;"
        " a write outside every territory is still skipped",
        unreadable_twin_is_broken,
    ),
    Assertion(
        37,
        "the hooks file: the gate, and the pointer at session start and at a subagent's start",
        hooks_file_shape,
    ),
    Assertion(
        38,
        "the pointer: the line as typed, its JSON form for a subagent, its size, its skill",
        skill_pointer_printed,
    ),
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
    skill="choose-meta-type",  # the skill a red names (F10), typed by hand
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
