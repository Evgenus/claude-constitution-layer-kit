"""Fixtures of the fixture gate know-check: `python3 -m pytest tests` from the fixture's folder.

The gate is a gate of another layer: its namespace and its layer's keys stand in `layer.yaml`, the policies
in the constitution's file. This file holds what is its own, items 1 on, and hands the shared items its
`SUBJECT`, which they run against: the items every gate shares, from 101, so the run shows that each of them
holds for a gate whose dials file is not the constitution's.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit import identity
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import KERNEL_KEYS
from constitution_layer_kit.testing.acceptance import broken_first_line, expect, item
from constitution_layer_kit.testing.consumer import ROOT_POLICY, Consumer, document, dump, envelope
from constitution_layer_kit.testing.harness import Edit, Harness, Result, Write, event_json
from constitution_layer_kit.testing.items import NO_ENVELOPE, Subject
from layered_gate import messages, start

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
NAMESPACE = start.GATE.namespace
H = Harness(
    SCRIPTS,
    "check-layered.sh",
    "check-layered.py",
    NAMESPACE,
    dials_file=start.GATE.dials_file,
    kernel_keys=start.GATE.kernel_keys,
)

NOTE_A = "docs/notes/a.md"
NOTES_POLICY = "docs/policies/notes-policy.md"
PHRASE = "forbidden-word"  # the phrase the notes policy of every consumer of this gate forbids
# the lines the gate prints, typed by hand
L1_LINE = (
    "BROKEN: layer.yaml: layer_dialect is 'fancy', and this layer knows only 'plain' — fix: know-check reads"
    " documents in one dialect, and a dialect it does not know would be judged by rules written for another:"
    " set layer_dialect: plain in layer.yaml, or remove the line"
)
L2_LINE = (
    "BROKEN: layer.yaml: notes-policy is a policy's namespace, and the policies stand in another file"
    " — fix: a policy declared in two files would have two territories, and know-check reads it from one"
    " only: move the 'notes-policy' key, with its territory, to the file of the constitution's policies, and"
    " remove it from this file"
)
L3_FINDING = (
    "RED: docs/notes/a.md: holds 'forbidden-word', which its policy 'notes-policy' forbids\n"
    "  why: a policy lists what its documents must not say, and a document that says it breaks the rule it is"
    " governed by\n"
    "  fix: remove 'forbidden-word' from the document, or remove the line 'FORBIDDEN: forbidden-word' from"
    " the policy 'notes-policy'"
)
NO_ROOT_LINE = (
    "GREEN: know-check: 0 documents examined — constitution.yaml has no root_policy: nothing is claimed"
)


def gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    """The gate's run on a prepared consumer, whose notes policy forbids `PHRASE`, which `RED` holds."""
    consumer = H.fresh_consumer()
    consumer.write_dials(dials_patch, raw_dials)
    consumer.write(NOTES_POLICY, forbidding("notes-policy"))
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return H.run_gate(event_json(consumer.root, action), env=env), consumer.root


def own(**dials: object) -> dict[str, object]:
    return {NAMESPACE: dials}


def claim(territory: Sequence[str]) -> dict[str, object]:
    """The dials patch that gives the notes policy another territory: it goes to the constitution's file."""
    return {"notes-policy": {"territory": list(territory)}}


def forbidding(policy: str) -> str:
    """The text of a policy that forbids `PHRASE` to its documents, by the line the gate reads."""
    return document(
        body=f"# Policy\n\nFORBIDDEN: {PHRASE}\n",
        id=policy,
        type="current-state",
        title=f"Fixture {policy}",
        status="active",
    )


VALID = Write(NOTE_A, envelope("note-a"))
RED = Write(
    NOTE_A,
    document(f"# Note\n\n{PHRASE}\n", id="note-a", type="non-authoritative", title="Note A", status="active"),
)


def built(raw_constitution: str | None = None, raw: str | None = None) -> Consumer:
    consumer = H.fresh_consumer()
    consumer.write_dials(None, raw, raw_constitution)
    return consumer


def run(consumer: Consumer, action: Write = VALID) -> Result:
    return H.run_gate(event_json(consumer.root, action))


@item(
    1,
    "L3: a document that holds a phrase its policy forbids is blocked; with the line gone, it passes",
)
def test_forbidden_policy() -> None:
    red, _ = gate_on(RED)
    expect(red, 2, L3_FINDING, "stderr")
    assert [line for line in red.stderr.splitlines() if line.startswith("RED:")] == [
        "RED: docs/notes/a.md: holds 'forbidden-word', which its policy 'notes-policy' forbids",
        "RED: 1 finding(s) — 1 document examined (docs/notes/a.md)",
    ]
    assert L3_FINDING == messages.l3_forbidden(NOTE_A, "notes-policy", PHRASE).render()
    green, _ = gate_on(VALID)
    expect(green, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")
    plain = {
        NOTES_POLICY: envelope("notes-policy", "current-state")
    }  # the same document, a policy without the line
    unforbidden, _ = gate_on(RED, files=plain)
    expect(unforbidden, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")


@item(
    2,
    "L1: a layer_dialect other than plain is a configuration failure of the layer's file, plain passes",
)
def test_layer_dialect() -> None:
    result, _ = gate_on(VALID, dials_patch={"layer_dialect": "fancy"})
    broken_first_line(result, L1_LINE)
    assert L1_LINE == messages.l1_dialect("fancy").render()
    listed, _ = gate_on(VALID, dials_patch={"layer_dialect": ["plain"]})
    assert listed.code == 1 and "layer_dialect is '['plain']'" in listed.stderr, listed.stderr
    plain, _ = gate_on(VALID, dials_patch={"layer_dialect": "plain"})
    expect(plain, 0, "governed by notes-policy", "stdout")


@item(
    3,
    "L2: a policy's namespace in the layer's file is refused; the policies stand in the constitution's",
)
def test_policy_namespace_in_layer_file() -> None:
    raw = "module_prefix: know-\nnotes-policy:\n  territory:\n    - 'docs/notes/**'\n"
    result, _ = gate_on(VALID, raw_dials=raw)
    broken_first_line(result, L2_LINE)
    assert L2_LINE == messages.l2_policy_namespace("notes-policy").render()


@item(4, "a constitution file with no root_policy, or none at all, is a skip that names that file")
def test_no_root_policy() -> None:
    without = dump({"module_prefix": "const-", "notes-policy": {"territory": ["docs/notes/**"]}})
    result = run(built(raw_constitution=without))
    expect(result, 0, NO_ROOT_LINE, "stdout")
    consumer = built()
    (consumer.root / "constitution.yaml").unlink()
    expect(run(consumer), 0, NO_ROOT_LINE, "stdout")


@item(5, "a failure of the policies names the constitution's file, and a failure of the layer's keys its own")
def test_failures_name_their_file() -> None:
    gone = dump({"root_policy": "docs/policies/gone.md", "module_prefix": "const-"})
    result = run(built(raw_constitution=gone))
    with identity.reading("constitution.yaml", KERNEL_KEYS):
        wanted = shared.c6_root_missing("docs/policies/gone.md").render()
    broken_first_line(result, wanted)
    assert wanted.startswith("BROKEN: constitution.yaml names root_policy"), wanted
    bad = dump({"root_policy": ROOT_POLICY, "module_prefix": "const-", "territory_dialect": "regex"})
    result = run(built(raw_constitution=bad))
    with identity.reading("constitution.yaml", KERNEL_KEYS):
        wanted = shared.c5_dialect_unsupported("regex").render()
    broken_first_line(result, wanted)
    assert wanted.startswith("BROKEN: constitution.yaml: territory_dialect"), wanted
    alone = "module_prefix: know-\nroot_policy: docs/policies/root-policy.md\n"
    result = run(built(raw=alone))
    with identity.reading("layer.yaml", start.GATE.kernel_keys):
        wanted = shared.c5_kernel_key_elsewhere("root_policy").render()
    broken_first_line(result, wanted)
    assert wanted.startswith("BROKEN: layer.yaml: root_policy is no key of this file"), wanted


@item(6, "the policies are the constitution's alone: a territory written in the layer's file moves nothing")
def test_territory_comes_from_the_constitution() -> None:
    outside, _ = gate_on(Write("docs/other/a.md", NO_ENVELOPE), dials_patch=own(severity="warn"))
    expect(outside, 0, "docs/other/a.md is outside claimed territory", "stdout")
    moved, _ = gate_on(Write("docs/other/a.md", NO_ENVELOPE), dials_patch=claim(["docs/other/**"]))
    expect(moved, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")


@item(7, "the scan reads both files: the finding of a forbidden phrase, and the green line of a clean tree")
def test_scan() -> None:
    consumer = H.fresh_consumer()
    consumer.write(NOTES_POLICY, forbidding("notes-policy"))
    consumer.write(NOTE_A, VALID.text)
    green = H.run_gate("", args=["--scan", str(consumer.root)])
    expect(
        green,
        0,
        "GREEN: know-check: 4 governed document(s) examined, 4 Markdown file(s) scanned, 3 policies",
        "stdout",
    )
    consumer.write(NOTE_A, RED.text)
    red = H.run_gate("", args=["--scan", str(consumer.root)])
    expect(red, 2, L3_FINDING, "stdout")
    assert (
        "RED: 1 finding(s) — 4 governed document(s) examined, 4 Markdown file(s) scanned, 3 policies"
        in red.stdout
    )


@item(
    8, "an envelope nobody can read is no finding of this gate and no crash: the path mapping decides alone"
)
def test_unreadable_envelope_is_no_crash() -> None:
    for text in ("---\nid: [unclosed\n---\n", "---\nid: a\n", "---\n" + "[" * 5000 + "\n---\n"):
        result, _ = gate_on(Write(NOTE_A, text))
        expect(result, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=RED,
    red_finding=messages.l3_forbidden(NOTE_A, "notes-policy", PHRASE),
    territory=["docs/notes/**"],
    green=shared.governed_by("notes-policy"),
    claim=claim,
    judges_envelopes=False,
    noted=Write("docs/policies/loose-policy.md", NO_ENVELOPE),  # a policy with no id: the shared note N1.1
    note=(  # typed by hand
        "note: docs/policies/loose-policy.md lies in the root policy's territory but carries no readable id;"
        " it claims nothing until it does"
    ),
    outside="docs/notes/a.md is outside claimed territory",
)
