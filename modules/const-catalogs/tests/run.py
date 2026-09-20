#!/usr/bin/env python3
"""Fixtures of const-catalogs: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one, with its three policies. None of them matters here:
a catalog is declared in this module's own dial, with a territory no policy claims, so every
item writes that dial — through the case's setup for the red→green cases, through `gate_on`
for the assertions. The shared items about the root policy and the policies' documents are
not this gate's, and are left out; their numbers stay free.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Sequence
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
from consumer import ROOT_POLICY, Consumer  # noqa: E402
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
TERRITORY = ["docs/items/**"]
CATALOG = Catalog("itm", 4, tuple(TERRITORY))
STEM_A = "itm-0001-first"
ITEM_A = f"docs/items/{STEM_A}.md"
ELSEWHERE = "docs/elsewhere/a.md"


def entry(prefix: str = "itm", territory: list[str] | None = None, **more: object) -> dict[str, object]:
    return {"prefix": prefix, "territory": TERRITORY if territory is None else territory, **more}


def catalogs(*entries: object) -> dict[str, object]:
    """A patch of the dials file that lists these catalogs."""
    return {NAMESPACE: {"catalogs": list(entries)}}


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
    dials = {**Consumer(Path()).dials, **catalogs(entry(width=4)), **(patch or {})}
    return yaml.safe_dump(dials, sort_keys=False)


SETUP = (Write("constitution.yaml", dials_text()),)
VALID = Write(ITEM_A, item())
SECOND_TAKEN = at("itm-0001-second")


def k1(stem: str, catalog: Catalog = CATALOG, free: int | None = 1) -> Finding:
    """`free` is the next free number a new file is taught; None for a file that exists, as in a scan."""
    return messages.k1_name_without_form(at(stem), stem, catalog, free)


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
        "K1: the width the entry declares is the width required",
        Write(at("itm-0001-first"), item()),
        Write(at("itm-000001-first"), item("itm-000001-first")),
        k1("itm-0001-first", Catalog("itm", 6, tuple(TERRITORY))),
        (Write("constitution.yaml", dials_text(catalogs(entry(width=6)))),),
    ),
    Case(
        42,
        "K4: a new item under a number another item carries is blocked; the next free number passes",
        Write(SECOND_TAKEN, item("itm-0001-second")),
        Write(at("itm-0002-second"), item("itm-0002-second")),
        messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, 2),
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
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return H.run_gate(event_json(consumer.root, action), env=env), consumer.root


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps the catalog listed."""
    return {NAMESPACE: {"catalogs": [entry(width=4)], **dials}}


def scan_of(files: dict[str, str], dials_patch: dict[str, object] | None = None) -> Result:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text(dials_patch))
    for rel, text in files.items():
        consumer.write(rel, text)
    return H.run_gate("", args=["--scan", str(consumer.root)])


def broken(result: Result, failure: Broken) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, failure.render())
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def all_of(results: list[tuple[bool, str]], summary: str) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, failed[0] if failed else summary


def no_catalog_listed() -> tuple[bool, str]:
    """With no catalog listed, any name passes — and the count line says why."""
    result, _ = gate_on(Write(at("first"), NO_ENVELOPE), dials_patch={NAMESPACE: {}})
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_catalog()), "stdout")


def no_catalog_listed_scan() -> tuple[bool, str]:
    result = H.run_gate("", args=["--scan", str(H.fresh_consumer().root)])
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_catalog()), "stdout")


def not_an_item() -> tuple[bool, str]:
    result, _ = gate_on(Write(ELSEWHERE, NO_ENVELOPE))
    skip = messages.g1_skip_not_an_item(ELSEWHERE, [CATALOG])
    return expect(result, 0, shared.g1_green_skip(skip), "stdout")


NO_POLICIES = yaml.safe_dump(catalogs(entry()), sort_keys=False)  # a dials file with no root_policy at all


def no_policies_red() -> tuple[bool, str]:
    """A project without policies numbers its documents: the dial is all the gate reads."""
    result, _ = gate_on(Write(at("first"), item("first")), raw_dials=NO_POLICIES)
    return expect(result, 2, k1("first").render(), "stderr")


def no_policies_green() -> tuple[bool, str]:
    result, _ = gate_on(VALID, raw_dials=NO_POLICIES)
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def broken_governance_is_not_this_gates() -> tuple[bool, str]:
    """A root policy that is named and missing breaks the gates that resolve policies, not this one."""
    result, _ = gate_on(VALID, remove=ROOT_POLICY)
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def inside_a_policys_territory() -> tuple[bool, str]:
    """A catalog's territory may lie inside a policy's: numbering and governance do not meet."""
    patch = catalogs(entry("note", ["docs/notes/**"]))
    result, _ = gate_on(Write("docs/notes/a.md", item("a")), dials_patch=patch)
    taught = messages.k1_name_without_form("docs/notes/a.md", "a", Catalog("note", 4, ("docs/notes/**",)), 1)
    return expect(result, 2, taught.render(), "stderr")


def territory_by_alias() -> tuple[bool, str]:
    """One territory written once and used twice, by YAML's own alias: the policy's and the catalog's."""
    raw = (
        f"root_policy: {ROOT_POLICY}\n"
        "root-policy: {territory: ['docs/policies/**']}\n"
        "notes-policy:\n  territory: &notes ['docs/notes/**']\n"
        f"{NAMESPACE}:\n  catalogs:\n    - {{prefix: note, territory: *notes}}\n"
    )
    result, _ = gate_on(Write("docs/notes/note-0001-first.md", item("note-0001-first")), raw_dials=raw)
    green = messages.g1_item_of(Catalog("note", 4, ("docs/notes/**",)))
    return expect(result, 0, shared.g1_green_hook(green), "stdout")


def rest_of_envelope_not_judged() -> tuple[bool, str]:
    result, _ = gate_on(Write(ITEM_A, item(type="memo", status="draft", drop=("title",))))
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def width_defaults_to_four() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch=catalogs(entry()))
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def catalogs_not_a_list() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"catalogs": entry()}})
    return broken(result, messages.c5_catalogs_not_a_list())


def entry_shapes() -> tuple[bool, str]:
    shapes: list[object] = [
        "itm",
        {"territory": TERRITORY},
        {"prefix": "itm"},
        entry("ITM"),
        entry("it-m"),
        entry(7),  # type: ignore[arg-type]  # the fixture is the wrong type on purpose
        entry(territory=[]),
        entry(territory=[""]),
        {"prefix": "itm", "territory": "docs/items/**"},
        entry(width=0),
        entry(width="4"),
        entry(width=True),
        entry(start=1),
    ]
    results = [
        broken(gate_on(VALID, dials_patch=catalogs(entry("ok"), shape))[0], messages.c5_catalog_entry(2))
        for shape in shapes
    ]
    return all_of(results, f"{len(shapes)} malformed entries, each exit 1 with C5 naming entry 2")


def entry_pattern_git_would_misread() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch=catalogs(entry(territory=["#docs/items/**"])))
    return broken(result, shared.c5_territory_pattern(f"{NAMESPACE}.catalogs[itm]", "#docs/items/**"))


TWICE = catalogs(entry(), entry(territory=["docs/more/**"], width=3))


def prefix_listed_twice() -> tuple[bool, str]:
    return broken(gate_on(VALID, dials_patch=TWICE)[0], messages.c5_prefix_listed_twice("itm"))


def prefix_listed_twice_scan() -> tuple[bool, str]:
    return broken(scan_of({}, TWICE), messages.c5_prefix_listed_twice("itm"))


def two_catalogs() -> tuple[bool, str]:
    """Two kinds, two prefixes, one sequence each: the same number in both is no collision."""
    patch = catalogs(entry(), entry("note", ["docs/notes/**"]))
    files = {ITEM_A: item(), "docs/notes/note-0001-first.md": item("note-0001-first")}
    return expect(scan_of(files, patch), 0, shared.g1_green_scan(messages.f9_scan_tail(2, 5, 2)), "stdout")


def overlap_takes_the_prefix_carried() -> tuple[bool, str]:
    """Where two territories hold one file, the catalog whose prefix the name carries judges it."""
    patch = catalogs(entry(), entry("shr", ["docs/items/shared/**"]))
    result, _ = gate_on(
        Write("docs/items/shared/shr-0001-first.md", item("shr-0001-first")), dials_patch=patch
    )
    green = messages.g1_item_of(Catalog("shr", 4, ("docs/items/shared/**",)))
    return expect(result, 0, shared.g1_green_hook(green), "stdout")


def overlap_without_a_prefix() -> tuple[bool, str]:
    """A name that carries neither prefix is judged by the first catalog listed."""
    patch = catalogs(entry(), entry("shr", ["docs/items/shared/**"]))
    result, _ = gate_on(Write("docs/items/shared/first.md", item("first")), dials_patch=patch)
    taught = messages.k1_name_without_form("docs/items/shared/first.md", "first", CATALOG, 1)
    return expect(result, 2, taught.render(), "stderr")


def severity_warn() -> tuple[bool, str]:
    result, _ = gate_on(Write(at("first"), item("first")), dials_patch=own(severity="warn"))
    ok = result.code == 0 and not result.stderr and k1("first").headline in result.stdout
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
    count = shared.f9_count_scan(1, messages.f9_scan_tail(3, 6, 1))
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
    return expect(scan_of(files), 0, shared.g1_green_scan(messages.f9_scan_tail(3, 6, 1)), "stdout")


def scan_gap_is_legitimate() -> tuple[bool, str]:
    files = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
    return expect(scan_of(files), 0, shared.g1_green_scan(messages.f9_scan_tail(2, 5, 1)), "stdout")


def scan_ignores_warn() -> tuple[bool, str]:
    result = scan_of({at("first"): item("first")}, own(severity="warn"))
    return expect(result, 2, k1("first", free=None).render(), "stdout")


def scan_name_and_number() -> tuple[bool, str]:
    """An item whose name carries no number is one finding and takes no part in the collision check."""
    result = scan_of({**COLLIDING, at("first"): item("first")})
    count = shared.f9_count_scan(2, messages.f9_scan_tail(4, 7, 1))
    taught = (k1("first", free=None).render(), K3.render(), count)
    ok = result.code == 2 and all(text in result.stdout for text in taught)
    return ok, f"exit {result.code}: two findings, four items"


def scan_with_deleted_file() -> tuple[bool, str]:
    """A tracked item deleted from the working tree, deletion not staged: not a document any more."""
    consumer = H.fresh_consumer((*SETUP, VALID, Write(at("itm-0002-second"), item("itm-0002-second"))))
    (consumer.root / ITEM_A).unlink()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 4, 1)), "stdout")


def scan_scales() -> tuple[bool, str]:
    """The scan reads each item once: a few hundred items take seconds, not minutes."""
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


ONE_AND_NINE = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
K4 = messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, 2)


def existing_item_is_not_judged_on_its_number() -> tuple[bool, str]:
    """Of two items that already collide, either may still be written: which one renumbers is a
    question of branches, answered by the scan's finding, not by blocking the frozen one's edits."""
    files = {ITEM_A: item(), SECOND_TAKEN: item("itm-0001-second")}
    result, _ = gate_on(Write(SECOND_TAKEN, item("itm-0001-second")), files=files)
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def untracked_item_holds_its_number() -> tuple[bool, str]:
    """An item nobody committed yet is in the working tree all the same, and its number is taken."""
    result, _ = gate_on(Write(SECOND_TAKEN, item("itm-0001-second")), files={ITEM_A: item()})
    return expect(result, 2, K4.render(), "stderr")


def edit_that_creates_is_new() -> tuple[bool, str]:
    result, _ = gate_on(Edit(SECOND_TAKEN, "", item("itm-0001-second")), files={ITEM_A: item()})
    return expect(result, 2, K4.render(), "stderr")


def free_number_below_the_highest() -> tuple[bool, str]:
    """The gate asks for a free number, not for the next one: allocation is advice, a gap is legitimate."""
    result, _ = gate_on(Write(at("itm-0005-fifth"), item("itm-0005-fifth")), files=ONE_AND_NINE)
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def next_free_number_is_named() -> tuple[bool, str]:
    result, _ = gate_on(Write(at("tenth"), item("tenth")), files=ONE_AND_NINE)
    return expect(result, 2, k1("tenth", free=10).render(), "stderr")


def width_exhausted() -> tuple[bool, str]:
    """Past the last number the width can write, the fix falls back to words: no name is invented."""
    files = {at("itm-9-ninth"): item("itm-9-ninth")}
    result, _ = gate_on(Write(at("tenth"), item("tenth")), dials_patch=catalogs(entry(width=1)), files=files)
    return expect(result, 2, k1("tenth", Catalog("itm", 1, tuple(TERRITORY)), free=None).render(), "stderr")


def message_shape() -> tuple[bool, str]:
    built = [*(case.expect for case in CASES), K3, K4]
    ok = all(isinstance(f, Finding) and f.key and f.headline and f.why and f.fix for f in built)
    return ok, f"{len(built)} findings examined, each with what / why / fix"


ASSERTIONS = [
    Assertion(
        14, "no catalog listed: nothing is examined, and the count line teaches the dial", no_catalog_listed
    ),
    Assertion(15, "no catalog listed, scan: the same visible zero", no_catalog_listed_scan),
    Assertion(16, "a document in no catalog's territory is a visible skip", not_an_item),
    Assertion(
        17, "no policies at all, red half: the dial alone numbers a project's documents", no_policies_red
    ),
    Assertion(18, "no policies at all, green half", no_policies_green),
    Assertion(
        19, "a root policy named and missing is not this gate's failure", broken_governance_is_not_this_gates
    ),
    Assertion(
        20,
        "a catalog inside a policy's territory: numbering and governance do not meet",
        inside_a_policys_territory,
    ),
    Assertion(
        21,
        "one territory, written once, used by a policy and a catalog through a YAML alias",
        territory_by_alias,
    ),
    Assertion(
        22,
        "the rest of the envelope is not judged here: a bad type and status pass",
        rest_of_envelope_not_judged,
    ),
    Assertion(23, "width defaults to four", width_defaults_to_four),
    Assertion(24, "C5: catalogs that is not a list", catalogs_not_a_list),
    Assertion(25, "C5: an entry of the wrong shape, thirteen ways, named by its position", entry_shapes),
    Assertion(
        26,
        "C5: a territory pattern git would read as a comment, in an entry",
        entry_pattern_git_would_misread,
    ),
    Assertion(27, "C5: one prefix listed twice fails the load", prefix_listed_twice),
    Assertion(28, "C5: the same in a scan: exit 1, so CI turns red", prefix_listed_twice_scan),
    Assertion(29, "two catalogs: one sequence each, the same number in both is no collision", two_catalogs),
    Assertion(
        30,
        "two territories over one file: the catalog whose prefix the name carries judges",
        overlap_takes_the_prefix_carried,
    ),
    Assertion(
        31,
        "two territories over one file, no prefix carried: the first listed judges",
        overlap_without_a_prefix,
    ),
    Assertion(32, "severity warn: the finding travels in the JSON and the write proceeds", severity_warn),
    Assertion(
        33, "K3, red half: two items under one number fail the scan, exit 2, both files named", scan_collision
    ),
    Assertion(34, "K3, green half: the renumbered pair passes", scan_renumbered),
    Assertion(35, "a gap is legitimate: numbers 1 and 9 alone are green", scan_gap_is_legitimate),
    Assertion(36, "scan: a finding with counts, exit 2, ignoring severity warn", scan_ignores_warn),
    Assertion(
        37, "scan: a name with no number is one finding and no part of a collision", scan_name_and_number
    ),
    Assertion(
        38,
        "scan: a tracked file deleted from the working tree is left out, not a failure",
        scan_with_deleted_file,
    ),
    Assertion(39, "scan: 300 items in seconds (each item read once)", scan_scales),
    Assertion(40, "an echoed value a page long is cut: the verdict stays a message", long_value_is_cut),
    Assertion(41, "message shape: every taught finding has what, why and fix", message_shape),
    Assertion(
        43,
        "an item that exists is never judged on its number: of two that collide, either can be edited",
        existing_item_is_not_judged_on_its_number,
    ),
    Assertion(44, "K4: an untracked item, not ignored, holds its number", untracked_item_holds_its_number),
    Assertion(45, "K4: an Edit that creates a file is a new item", edit_that_creates_is_new),
    Assertion(
        46,
        "a free number below the highest passes: the gate asks for free, not for next",
        free_number_below_the_highest,
    ),
    Assertion(
        47, "K1 for a new file names the next free number: 10 after 1 and 9", next_free_number_is_named
    ),
    Assertion(48, "the width exhausted: the fix is in words, no name is invented", width_exhausted),
]


def claim(territory: Sequence[str]) -> dict[str, object]:
    """The dials patch that gives the catalog another territory."""
    return catalogs(entry(territory=list(territory)))


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=Write(at("first"), item("first")),
    red_finding=k1("first"),
    green=messages.g1_item_of(CATALOG),
    territory=TERRITORY,
    claim=claim,
    resolves_policies=False,
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
