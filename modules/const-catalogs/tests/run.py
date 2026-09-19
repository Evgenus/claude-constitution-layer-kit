#!/usr/bin/env python3
"""Fixtures of const-catalogs: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one — three policies, none of them for a numbered kind —
so every item adds the items policy, whose namespace declares the catalog: through the
case's setup for the red→green cases, through `gate_on` for the assertions.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from catalogs_gate import messages, start  # noqa: E402
from catalogs_gate.model import Catalog  # noqa: E402
from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.envelope import yaml_error_line  # noqa: E402
from const_gate.model import Broken, EnvelopeState, Finding  # noqa: E402
from consumer import Consumer, envelope  # noqa: E402
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
H = Harness(SCRIPTS, "check-catalog-item.sh", "check-catalog-item.py", start.GATE.namespace)

NAMESPACE = start.GATE.namespace
ITEMS_POLICY = "items-policy"
CATALOG = Catalog("itm", 4, ITEMS_POLICY)
STEM_A = "itm-0001-first"
ITEM_A = f"docs/items/{STEM_A}.md"
NOTE_A = "docs/notes/a.md"
ITEMS_DIALS: dict[str, object] = {
    ITEMS_POLICY: {"territory": ["docs/items/**"], "catalog": {"prefix": "itm", "width": 4}},
}


def item(stem: str = STEM_A, drop: tuple[str, ...] = (), **changes: object) -> str:
    """A valid item, rendered by the YAML dumper, with the named envelope fields replaced,
    added, or dropped. A value may be any YAML type: a number where a string is due is a
    fixture, not a typing accident."""
    fields: dict[str, object] = {
        "id": stem,
        "type": "non-authoritative",
        "title": f"Fixture {stem}",
        "status": "active",
    }
    fields.update(changes)
    kept = {key: value for key, value in fields.items() if key not in drop}
    return "---\n" + yaml.safe_dump(kept, sort_keys=False, allow_unicode=True) + "---\n\n# Fixture\n"


def at(stem: str) -> str:
    return f"docs/items/{stem}.md"


def yaml_error(block: str) -> str:
    """What the gate will report for a YAML block that does not parse: the parser's own words."""
    try:
        yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return yaml_error_line(exc)
    raise AssertionError("the fixture block parses")


def dials_text(patch: dict[str, object] | None = None) -> str:
    dials = {**Consumer(Path()).dials, **ITEMS_DIALS, **(patch or {})}
    return yaml.safe_dump(dials, sort_keys=False)


def policy_document(policy_id: str) -> Write:
    return Write(f"docs/policies/{policy_id}.md", envelope(policy_id, "current-state"))


POLICY_DOCUMENT = policy_document(ITEMS_POLICY)
SETUP = (Write("constitution.yaml", dials_text()), POLICY_DOCUMENT)
VALID = Write(ITEM_A, item())


def k1(stem: str, catalog: Catalog = CATALOG) -> Finding:
    return messages.k1_name_without_form(at(stem), stem, catalog)


def k2(detail: str, stem: str = STEM_A) -> Finding:
    return messages.k2_id_is_not_the_name(at(stem), stem, detail)


# ------------------------------------------------------------------ red → green cases

CASES = [
    Case(
        1,
        "K1: a file name with no number is blocked; a name of the catalog's form passes",
        Write(at("first"), item("first")),
        VALID,
        k1("first"),
        SETUP,
    ),
    Case(
        2,
        "K1: a number of the wrong width is blocked",
        Write(at("itm-001-first"), item("itm-001-first")),
        VALID,
        k1("itm-001-first"),
        SETUP,
    ),
    Case(
        3,
        "K1: an uppercase prefix is tolerated in prose, never in a file name",
        Write(at("ITM-0001-first"), item("ITM-0001-first")),
        VALID,
        k1("ITM-0001-first"),
        SETUP,
    ),
    Case(
        4,
        "K1: a number with no slug after it is blocked",
        Write(at("itm-0001"), item("itm-0001")),
        VALID,
        k1("itm-0001"),
        SETUP,
    ),
    Case(
        5,
        "K1: a slug that is not kebab-case is blocked",
        Write(at("itm-0001-First_item"), item("itm-0001-First_item")),
        VALID,
        k1("itm-0001-First_item"),
        SETUP,
    ),
    Case(
        6,
        "K2: an id that differs from the file name is blocked",
        Write(ITEM_A, item(id="itm-0001-other")),
        VALID,
        k2(messages.k2_differs("itm-0001-other", STEM_A)),
        SETUP,
    ),
    Case(
        7,
        "K2: a missing id is blocked here too — the module works with no other installed",
        Write(ITEM_A, item(drop=("id",))),
        VALID,
        k2(shared.field_missing("id")),
        SETUP,
    ),
    Case(
        8,
        "K2: an id YAML reads as a number is blocked",
        Write(ITEM_A, item(id=7)),
        VALID,
        k2(shared.field_not_string("id", "int")),
        SETUP,
    ),
    Case(
        9,
        "K2: an item with no envelope is blocked",
        Write(ITEM_A, NO_ENVELOPE),
        VALID,
        k2(messages.k2_no_envelope(EnvelopeState.NONE)),
        SETUP,
    ),
    Case(
        10,
        "K2: an envelope opened and never closed is blocked",
        Write(ITEM_A, f"---\nid: {STEM_A}\n\n# Item\n"),
        VALID,
        k2(messages.k2_no_envelope(EnvelopeState.UNTERMINATED)),
        SETUP,
    ),
    Case(
        11,
        "K2: an envelope that is not valid YAML is blocked",
        Write(ITEM_A, "---\nid: [unclosed\n---\n"),
        VALID,
        k2(messages.k2_no_envelope(EnvelopeState.INVALID, yaml_error("id: [unclosed"))),
        SETUP,
    ),
    Case(
        12,
        "K2: an Edit that changes the id away from the file name is blocked; one that keeps it passes",
        Edit(ITEM_A, f"id: {STEM_A}", "id: itm-0001-renamed"),
        Edit(ITEM_A, "# Fixture", "# Fixture, edited"),
        k2(messages.k2_differs("itm-0001-renamed", STEM_A)),
        (*SETUP, VALID),
    ),
    Case(
        13,
        "K1: a width the policy declares is the width required",
        Write(at("itm-0001-first"), item()),
        Write(at("itm-000001-first"), item("itm-000001-first")),
        k1("itm-0001-first", Catalog("itm", 6, ITEMS_POLICY)),
        (
            Write(
                "constitution.yaml",
                dials_text(
                    {ITEMS_POLICY: {"territory": ["docs/items/**"], "catalog": {"prefix": "itm", "width": 6}}}
                ),
            ),
            POLICY_DOCUMENT,
        ),
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
    """A patch of this module's namespace; the catalog is declared in the policy's, so any keeps it."""
    return {NAMESPACE: dials}


def scan_of(files: dict[str, str], dials_patch: dict[str, object] | None = None) -> Result:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text(dials_patch))
    consumer.write(POLICY_DOCUMENT.target, POLICY_DOCUMENT.text)
    for rel, text in files.items():
        consumer.write(rel, text)
    return H.run_gate("", args=["--scan", str(consumer.root)])


def broken(result: Result, failure: Broken) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, failure.render())
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def no_catalog_declared() -> tuple[bool, str]:
    """With no catalog declared, any name passes — and the count line says why."""
    result, _ = gate_on(
        Write(at("first"), NO_ENVELOPE), dials_patch={ITEMS_POLICY: {"territory": ["docs/items/**"]}}
    )
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_catalog()), "stdout")


def no_catalog_declared_scan() -> tuple[bool, str]:
    result = H.run_gate("", args=["--scan", str(H.fresh_consumer().root)])
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_catalog()), "stdout")


def not_an_item() -> tuple[bool, str]:
    result, _ = gate_on(Write(NOTE_A, NO_ENVELOPE))
    skip = messages.g1_skip_not_an_item(NOTE_A, [CATALOG])
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


def declaration_without_policy() -> tuple[bool, str]:
    """A namespace with a catalog key and no policy document behind it is not a policy's: it
    may be another reader's, and declares nothing."""
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text())  # the items policy's document is never written
    result = H.run_gate(event_json(consumer.root, Write(at("first"), NO_ENVELOPE)))
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_catalog()), "stdout")


def rest_of_envelope_not_judged() -> tuple[bool, str]:
    result, _ = gate_on(Write(ITEM_A, item(type="memo", status="draft", drop=("title",))))
    return expect(result, 0, f"governed by {ITEMS_POLICY}", "stdout")


def policy_is_never_an_item() -> tuple[bool, str]:
    """A catalog territory that reaches where policies live does not number the policies."""
    patch: dict[str, object] = {ITEMS_POLICY: {"territory": ["docs/**"], "catalog": {"prefix": "itm"}}}
    result, _ = gate_on(policy_document("another-policy"), dials_patch=patch)
    skip = messages.g1_skip_not_an_item("docs/policies/another-policy.md", [CATALOG])
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


def root_declares_a_catalog() -> tuple[bool, str]:
    """The root policy may number the policies themselves."""
    patch: dict[str, object] = {
        "root-policy": {"territory": ["docs/policies/**"], "catalog": {"prefix": "pol"}},
        ITEMS_POLICY: {"territory": ["docs/items/**"]},
    }
    result, _ = gate_on(policy_document("another-policy"), dials_patch=patch)
    taught = messages.k1_name_without_form(
        "docs/policies/another-policy.md", "another-policy", Catalog("pol", 4, "root-policy")
    )
    return expect(result, 2, taught.render(), "stderr")


def width_defaults_to_four() -> tuple[bool, str]:
    patch: dict[str, object] = {ITEMS_POLICY: {"territory": ["docs/items/**"], "catalog": {"prefix": "itm"}}}
    result, _ = gate_on(VALID, dials_patch=patch)
    return expect(result, 0, f"governed by {ITEMS_POLICY}", "stdout")


def catalog_shapes() -> tuple[bool, str]:
    shapes: list[object] = [
        "itm",
        {"width": 4},
        {"prefix": "ITM"},
        {"prefix": "it-m"},
        {"prefix": 7},
        {"prefix": "itm", "width": 0},
        {"prefix": "itm", "width": "4"},
        {"prefix": "itm", "width": True},
        {"prefix": "itm", "start": 1},
    ]
    results = [
        broken(
            gate_on(VALID, dials_patch={ITEMS_POLICY: {"territory": ["docs/items/**"], "catalog": shape}})[0],
            messages.c5_catalog_shape(ITEMS_POLICY),
        )
        for shape in shapes
    ]
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, failed[0] if failed else f"{len(shapes)} malformed declarations, each exit 1 with C5"


TWICE: dict[str, object] = {
    "notes-policy": {"territory": ["docs/notes/**"], "catalog": {"prefix": "itm", "width": 3}}
}


def prefix_declared_twice() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch=TWICE)
    return broken(result, messages.c5_prefix_declared_twice("itm", ITEMS_POLICY, "notes-policy"))


def prefix_declared_twice_scan() -> tuple[bool, str]:
    return broken(scan_of({}, TWICE), messages.c5_prefix_declared_twice("itm", ITEMS_POLICY, "notes-policy"))


def two_catalogs() -> tuple[bool, str]:
    """Two kinds, two prefixes, one sequence each: the same number in both is no collision."""
    patch: dict[str, object] = {
        "notes-policy": {"territory": ["docs/notes/**"], "catalog": {"prefix": "note"}}
    }
    files = {ITEM_A: item(), "docs/notes/note-0001-first.md": item("note-0001-first")}
    return expect(scan_of(files, patch), 0, shared.g1_green_scan(messages.f9_scan_tail(2, 6, 2)), "stdout")


def overlap_takes_the_prefix_carried() -> tuple[bool, str]:
    """In an overlap nobody resolved, the item is judged against the catalog whose prefix it carries."""
    patch: dict[str, object] = {
        "shared-policy": {"territory": ["docs/items/shared/**"], "catalog": {"prefix": "shr"}}
    }
    target = "docs/items/shared/shr-0001-first.md"
    result, _ = gate_on(Write(target, item("shr-0001-first")), dials_patch=patch)
    return expect(result, 0, "governed by shared-policy", "stdout")


def severity_warn() -> tuple[bool, str]:
    result, _ = gate_on(Write(at("first"), item("first")), dials_patch=own(severity="warn"))
    ok = result.code == 0 and "K1" not in result.stderr and k1("first").headline in result.stdout
    return ok, f"exit {result.code}; the finding travels in the JSON on stdout"


COLLIDING = {
    ITEM_A: item(),
    at("itm-0001-second"): item("itm-0001-second"),
    at("itm-0002-third"): item("itm-0002-third"),
}
K3 = messages.k3_number_shared(CATALOG, 1, [ITEM_A, at("itm-0001-second")])


def scan_collision() -> tuple[bool, str]:
    """The red half of the uniqueness gate: two items under one number."""
    result = scan_of(COLLIDING)
    count = shared.f9_count_scan(1, messages.f9_scan_tail(3, 7, 1))
    ok = result.code == 2 and K3.render() in result.stdout and count in result.stdout
    return (
        ok,
        f"exit {result.code}: {K3.headline}" if ok else f"exit {result.code}: {result.stdout}{result.stderr}",
    )


def scan_renumbered() -> tuple[bool, str]:
    """The green half: the younger item renumbered, the pair passes."""
    files = {
        ITEM_A: item(),
        at("itm-0003-second"): item("itm-0003-second"),
        at("itm-0002-third"): item("itm-0002-third"),
    }
    return expect(scan_of(files), 0, shared.g1_green_scan(messages.f9_scan_tail(3, 7, 1)), "stdout")


def scan_gap_is_legitimate() -> tuple[bool, str]:
    files = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
    return expect(scan_of(files), 0, shared.g1_green_scan(messages.f9_scan_tail(2, 6, 1)), "stdout")


def scan_ignores_warn() -> tuple[bool, str]:
    result = scan_of({at("first"): item("first")}, own(severity="warn"))
    return expect(result, 2, k1("first").render(), "stdout")


def scan_name_and_number() -> tuple[bool, str]:
    """An item whose name carries no number is one finding and takes no part in the collision check."""
    result = scan_of({**COLLIDING, at("first"): item("first")})
    count = shared.f9_count_scan(2, messages.f9_scan_tail(4, 8, 1))
    ok = result.code == 2 and all(
        text in result.stdout for text in (k1("first").render(), K3.render(), count)
    )
    return ok, f"exit {result.code}: two findings, four items"


def scan_scales() -> tuple[bool, str]:
    """The scan reads each document once: a few hundred items take seconds, not minutes."""
    files = {at(f"itm-{n:04d}-item"): item(f"itm-{n:04d}-item") for n in range(1, 301)}
    started = time.monotonic()
    result = scan_of(files)
    elapsed = time.monotonic() - started
    ok = result.code == 0 and "300 catalogued item(s) examined" in result.stdout and elapsed < 15
    return ok, f"300 items examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


def long_value_is_cut() -> tuple[bool, str]:
    """A value a page long is echoed cut, so the whole verdict stays under the platform's cap."""
    result, _ = gate_on(Write(ITEM_A, item(id="x" * 12_000)))
    taught = k2(messages.k2_differs("x" * 12_000, STEM_A)).render()
    ok = result.code == 2 and taught in result.stderr and len(result.stderr) < 2_000
    return ok, f"exit {result.code}; {len(result.stderr)} characters on stderr for a 12,000-character value"


def message_shape() -> tuple[bool, str]:
    built = [*(case.expect for case in CASES), K3]
    ok = all(isinstance(f, Finding) and f.key and f.headline and f.why and f.fix for f in built)
    return ok, f"{len(built)} findings examined, each with what / why / fix"


ASSERTIONS = [
    Assertion(
        14,
        "no catalog declared: nothing is examined, and the count line teaches the key",
        no_catalog_declared,
    ),
    Assertion(15, "no catalog declared, scan: the same visible zero", no_catalog_declared_scan),
    Assertion(16, "a document no catalog policy governs is a visible skip", not_an_item),
    Assertion(
        17,
        "a catalog key in a namespace with no policy behind it declares nothing",
        declaration_without_policy,
    ),
    Assertion(
        18,
        "the rest of the envelope is not judged here: a bad type and status pass",
        rest_of_envelope_not_judged,
    ),
    Assertion(19, "a document where policies live is never another catalog's item", policy_is_never_an_item),
    Assertion(
        20, "the root policy may declare a catalog: the policies are then its items", root_declares_a_catalog
    ),
    Assertion(21, "width defaults to four", width_defaults_to_four),
    Assertion(22, "C5: a catalog declaration of the wrong shape, nine ways", catalog_shapes),
    Assertion(23, "C5: one prefix declared by two policies fails the load", prefix_declared_twice),
    Assertion(24, "C5: the same in a scan: exit 1, so CI turns red", prefix_declared_twice_scan),
    Assertion(25, "two catalogs: one sequence each, the same number in both is no collision", two_catalogs),
    Assertion(
        26,
        "in an unresolved overlap the catalog whose prefix the name carries judges",
        overlap_takes_the_prefix_carried,
    ),
    Assertion(27, "severity warn: the finding travels in the JSON and the write proceeds", severity_warn),
    Assertion(
        28, "K3, red half: two items under one number fail the scan, exit 2, both files named", scan_collision
    ),
    Assertion(29, "K3, green half: the renumbered pair passes", scan_renumbered),
    Assertion(30, "a gap is legitimate: numbers 1 and 9 alone are green", scan_gap_is_legitimate),
    Assertion(31, "scan: a finding with counts, exit 2, ignoring severity warn", scan_ignores_warn),
    Assertion(
        32, "scan: a name with no number is one finding and no part of a collision", scan_name_and_number
    ),
    Assertion(33, "scan: 300 items in seconds (each document read once)", scan_scales),
    Assertion(34, "an echoed value a page long is cut: the verdict stays a message", long_value_is_cut),
    Assertion(35, "message shape: every taught finding has what, why and fix", message_shape),
]

SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=Write(at("first"), item("first")),
    red_finding=k1("first"),
    territory=["docs/items/**"],
    governed_by=ITEMS_POLICY,
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
