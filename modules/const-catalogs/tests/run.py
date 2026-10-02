#!/usr/bin/env python3
"""Fixtures of const-catalogs: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one, with its three policies. None of them matters here:
a catalog is declared in this module's own dial, with a territory no policy claims, so every
item writes that dial — through the case's setup for the red→green cases, through `gate_on`
for the assertions. The shared items about the root policy and the policies' documents are
not this gate's, and are left out; their numbers stay free. The session-start printer is the
second entry point, driven through its own items (T74–T77).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MODULE_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from catalogs_gate import messages, start  # noqa: E402
from catalogs_gate.model import Advice, Catalog, NameToTake, Reach, Read  # noqa: E402
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
from shared_items import NO_ENVELOPE, PatternDial, Subject, shared_assertions  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-catalog-item.sh", "check-catalog-item.py", start.GATE.namespace)
SESSION = Harness(SCRIPTS, "session-start.sh", "session-start.py", start.GATE.namespace)

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


NOTES = Catalog("note", 4, ("docs/notes/**",))


def reach(in_tree: int | None, in_history: int | None = None, catalog: Catalog = CATALOG) -> Reach:
    return Reach(catalog, in_tree, in_history)


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


def take_next(number: int, history_read: bool = True) -> NameToTake:
    """What a new file is taught: the catalog's next number."""
    return NameToTake(Advice.NEXT, number, history_read)


IN_WORDS = NameToTake(Advice.WORDS)  # what a file that exists, and shows no number, is taught


def k1(stem: str, catalog: Catalog = CATALOG, take: NameToTake | None = None) -> Finding:
    """By default the finding a new file earns in a catalog with no item yet: number 1 is named."""
    return messages.k1_name_without_form(at(stem), stem, catalog, take or take_next(1))


def k2(detail: str, stem: str = STEM_A) -> Finding:
    return messages.k2_id_is_not_the_name(at(stem), stem, detail)


# ------------------------------------------------------------------ red → green cases

GREEN_WHAT = "an item of catalog 'itm'"  # what every green half's line says its document is, typed by hand

CASES = [
    Case(
        1,
        "K1: a file name with no number is blocked; a name of the catalog's form passes",
        Write(at("first"), item("first")),
        VALID,
        k1("first"),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        2,
        "K1: a number of the wrong width is blocked",
        Write(at("itm-001-first"), item("itm-001-first")),
        VALID,
        k1("itm-001-first"),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        3,
        "K1: an uppercase prefix is tolerated in prose, never in a file name",
        Write(at("ITM-0001-first"), item("ITM-0001-first")),
        VALID,
        k1("ITM-0001-first"),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        4,
        "K1: a number with no slug after it is blocked",
        Write(at("itm-0001"), item("itm-0001")),
        VALID,
        k1("itm-0001"),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        5,
        "K1: a slug that is not kebab-case is blocked",
        Write(at("itm-0001-First_item"), item("itm-0001-First_item")),
        VALID,
        k1("itm-0001-First_item"),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        6,
        "K2: an id that differs from the file name is blocked",
        Write(ITEM_A, item(id="itm-0001-other")),
        VALID,
        k2(messages.k2_differs("itm-0001-other", STEM_A)),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        7,
        "K2: a missing id is blocked here too — the module works with no other installed",
        Write(ITEM_A, item(drop=("id",))),
        VALID,
        k2(shared.field_missing("id")),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        8,
        "K2: an id YAML reads as a number is blocked",
        Write(ITEM_A, item(id=7)),
        VALID,
        k2(shared.field_not_string("id", "int")),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        9,
        "K2: an item with no envelope is blocked",
        Write(ITEM_A, NO_ENVELOPE),
        VALID,
        messages.k2_no_envelope(ITEM_A, STEM_A, EnvelopeState.NONE),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        10,
        "K2: an envelope opened and never closed is blocked",
        Write(ITEM_A, f"---\nid: {STEM_A}\n\n# Item\n"),
        VALID,
        messages.k2_no_envelope(ITEM_A, STEM_A, EnvelopeState.UNTERMINATED),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        11,
        "K2: an envelope that is not valid YAML is blocked",
        Write(ITEM_A, "---\nid: [unclosed\n---\n"),
        VALID,
        messages.k2_no_envelope(ITEM_A, STEM_A, EnvelopeState.INVALID, yaml_error("id: [unclosed")),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        12,
        "K2: an Edit that changes the id away from the file name is blocked; one that keeps it passes",
        Edit(ITEM_A, f"id: {STEM_A}", "id: itm-0001-renamed"),
        Edit(ITEM_A, "# Fixture", "# Fixture, edited"),
        k2(messages.k2_differs("itm-0001-renamed", STEM_A)),
        GREEN_WHAT,
        (*SETUP, VALID),
    ),
    Case(
        13,
        "K1: the width the entry declares is the width required",
        Write(at("itm-0001-first"), item()),
        Write(at("itm-000001-first"), item("itm-000001-first")),
        k1("itm-0001-first", Catalog("itm", 6, tuple(TERRITORY))),
        GREEN_WHAT,
        (Write("constitution.yaml", dials_text(catalogs(entry(width=6)))),),
    ),
    Case(
        42,
        "K4: a new item under a number another item carries is blocked; the next free number passes",
        Write(SECOND_TAKEN, item("itm-0001-second")),
        Write(at("itm-0002-second"), item("itm-0002-second")),
        messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, take_next(2)),
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
    return broken_typed(result, failure.render())


def broken_typed(result: Result, line: str) -> tuple[bool, str]:
    """The failure's line, typed by hand where the item types it, first; then the count line."""
    ok, evidence = broken_first_line(result, line)
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
    taught = messages.k1_name_without_form("docs/notes/a.md", "a", NOTES, take_next(1))
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


def a_misspelt_dial() -> tuple[bool, str]:
    """A key of the namespace that is none of the three is refused, never a setting ignored in
    silence — `catalog:` for `catalogs:` would otherwise read as no catalog listed."""
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"catalog": [entry()]}})
    return broken_typed(
        result,
        "BROKEN: constitution.yaml: const-catalogs.catalog is no dial of this module — fix: a misspelt dial"
        " would be ignored in silence, so none is: write one of severity, log_dir, catalogs",
    )


def catalogs_not_a_list() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"catalogs": entry()}})
    return broken(result, messages.c5_catalogs_not_a_list())


def entry_shapes() -> tuple[bool, str]:
    """Each malformed entry is named by its position and by what is wrong with it."""
    shapes: list[tuple[object, str]] = [
        ("itm", messages.entry_not_a_mapping()),
        (entry(start=1), messages.entry_unknown_key("start")),
        ({"territory": TERRITORY}, messages.entry_prefix()),
        (entry("ITM"), messages.entry_prefix()),
        (entry("it-m"), messages.entry_prefix()),
        (entry("itm\n"), messages.entry_prefix()),
        ({"prefix": 7, "territory": TERRITORY}, messages.entry_prefix()),
        ({"prefix": "itm"}, messages.entry_territory()),
        (entry(territory=[]), messages.entry_territory()),
        (entry(territory=[""]), messages.entry_territory()),
        ({"prefix": "itm", "territory": "docs/items/**"}, messages.entry_territory()),
        (entry(width=0), messages.entry_width()),
        (entry(width=10), messages.entry_width()),
        (entry(width="4"), messages.entry_width()),
        (entry(width=True), messages.entry_width()),
    ]
    results = [
        broken(
            gate_on(VALID, dials_patch=catalogs(entry("ok"), shape))[0], messages.c5_catalog_entry(2, what)
        )
        for shape, what in shapes
    ]
    # a key with a line break is shown escaped: one line, typed by hand
    odd_key = broken_typed(
        gate_on(VALID, dials_patch=catalogs(entry("ok"), {**entry(), "a\nb": 1}))[0],
        "BROKEN: constitution.yaml: entry 2 of const-catalogs.catalogs carries the key 'a\\nb'; an entry"
        " holds prefix, territory and width, and nothing else — fix: write the entry as {prefix: <lowercase"
        " letters and digits>, territory: [<patterns of the paths where the numbered documents live>],"
        " width: 4}",
    )
    return all_of(
        [*results, odd_key],
        f"{len(shapes)} malformed entries, each exit 1 with C5 naming entry 2 and the field",
    )


def entry_pattern_git_would_misread() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch=catalogs(entry(territory=["#docs/items/**"])))
    return broken_typed(
        result,
        "BROKEN: constitution.yaml: const-catalogs.catalogs[itm] holds a pattern git would not read as"
        " one: '#docs/items/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a"
        " line break; escape or remove it",
    )


TWICE = catalogs(entry(), entry(territory=["docs/more/**"], width=3))


def prefix_listed_twice() -> tuple[bool, str]:
    return broken(gate_on(VALID, dials_patch=TWICE)[0], messages.c5_prefix_listed_twice("itm"))


def prefix_listed_twice_scan() -> tuple[bool, str]:
    return broken(scan_of({}, TWICE), messages.c5_prefix_listed_twice("itm"))


def two_catalogs() -> tuple[bool, str]:
    """Two kinds, two prefixes, one sequence each: the same number in both is no collision."""
    patch = catalogs(entry(), entry("note", ["docs/notes/**"]))
    files = {ITEM_A: item(), "docs/notes/note-0001-first.md": item("note-0001-first")}
    return expect(
        scan_of(files, patch),
        0,
        shared.g1_green_scan(messages.f9_scan_tail(2, 5, [reach(1), reach(1, catalog=NOTES)])),
        "stdout",
    )


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
    taught = messages.k1_name_without_form("docs/items/shared/first.md", "first", CATALOG, take_next(1))
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
    count = shared.f9_count_scan(1, messages.f9_scan_tail(3, 6, [reach(2)]))
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
    return expect(scan_of(files), 0, shared.g1_green_scan(messages.f9_scan_tail(3, 6, [reach(3)])), "stdout")


def scan_gap_is_legitimate() -> tuple[bool, str]:
    files = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
    return expect(scan_of(files), 0, shared.g1_green_scan(messages.f9_scan_tail(2, 5, [reach(9)])), "stdout")


def scan_empty_catalog() -> tuple[bool, str]:
    """A listed catalog with no item yet is named as such: a visible zero, and the first number is 1."""
    return expect(scan_of({}), 0, shared.g1_green_scan(messages.f9_scan_tail(0, 3, [reach(None)])), "stdout")


def scan_ignores_warn() -> tuple[bool, str]:
    result = scan_of({at("first"): item("first")}, own(severity="warn"))
    return expect(result, 2, k1("first", take=IN_WORDS).render(), "stdout")


def scan_name_and_number() -> tuple[bool, str]:
    """An item whose name carries no number is one finding and takes no part in the collision check."""
    result = scan_of({**COLLIDING, at("first"): item("first")})
    count = shared.f9_count_scan(2, messages.f9_scan_tail(4, 7, [reach(2)]))
    taught = (k1("first", take=IN_WORDS).render(), K3.render(), count)
    ok = result.code == 2 and all(text in result.stdout for text in taught)
    return ok, f"exit {result.code}: two findings, four items"


def scan_with_deleted_file() -> tuple[bool, str]:
    """A tracked item deleted from the working tree, deletion not staged: not a document any more."""
    consumer = H.fresh_consumer((*SETUP, VALID, Write(at("itm-0002-second"), item("itm-0002-second"))))
    (consumer.root / ITEM_A).unlink()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 4, [reach(2)])), "stdout")


def scan_scales() -> tuple[bool, str]:
    """The scan reads each item once: a few hundred items take seconds, not minutes."""
    files = {at(f"itm-{n:04d}-item"): item(f"itm-{n:04d}-item") for n in range(1, 301)}
    started = time.monotonic()
    result = scan_of(files)
    elapsed = time.monotonic() - started
    line = (
        "GREEN: const-catalogs: 300 catalogued item(s) examined, 303 Markdown file(s) scanned,"
        " 1 catalog(s): itm up to itm-0300"
    )
    ok = result.code == 0 and line in result.stdout.splitlines() and elapsed < 15
    return ok, f"300 items examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


ONE_AND_NINE = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
K4 = messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, take_next(2))


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
    return expect(result, 2, k1("tenth", take=take_next(10)).render(), "stderr")


def width_exhausted() -> tuple[bool, str]:
    """Past the last number the width can write, the fix falls back to words: no name is invented."""
    files = {at("itm-9-ninth"): item("itm-9-ninth")}
    result, _ = gate_on(Write(at("tenth"), item("tenth")), dials_patch=catalogs(entry(width=1)), files=files)
    return expect(
        result,
        2,
        k1("tenth", Catalog("itm", 1, tuple(TERRITORY)), NameToTake(Advice.FULL)).render(),
        "stderr",
    )


def top_deleted() -> Consumer:
    """Items 1 and 2 committed, then item 2 deleted and the deletion committed: the tree holds 1,
    history held 2."""
    second = Write(at("itm-0002-second"), item("itm-0002-second"))
    consumer = H.fresh_consumer((*SETUP, VALID, second))
    consumer.git("rm", "-q", second.target)
    consumer.commit()
    return consumer


def deleted_top_number_is_not_suggested() -> tuple[bool, str]:
    result = H.run_gate(event_json(top_deleted().root, Write(at("third"), item("third"))))
    return expect(result, 2, k1("third", take=take_next(3)).render(), "stderr")


def deleted_top_number_in_k4() -> tuple[bool, str]:
    result = H.run_gate(event_json(top_deleted().root, Write(SECOND_TAKEN, item("itm-0001-second"))))
    return expect(
        result, 2, messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, take_next(3)).render(), "stderr"
    )


def deleted_number_is_not_refused() -> tuple[bool, str]:
    """History moves the advice only: a number free in the working tree passes in every clone."""
    again = Write(at("itm-0002-again"), item("itm-0002-again"))
    result = H.run_gate(event_json(top_deleted().root, again))
    return expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def scan_names_history() -> tuple[bool, str]:
    result = H.run_gate("", args=["--scan", str(top_deleted().root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 4, [reach(1, 2)])), "stdout")


def renamed_name_is_history() -> tuple[bool, str]:
    """An item renamed to a higher number and then deleted: git would report the rename as such, not
    as an addition, so rename detection is off and the new name counts as added."""
    consumer = H.fresh_consumer((*SETUP, VALID))
    consumer.git("mv", ITEM_A, at("itm-0007-first"))
    consumer.commit()
    consumer.git("rm", "-q", at("itm-0007-first"))
    consumer.commit()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(0, 3, [reach(None, 7)])), "stdout")


def shallow_clone_says_so() -> tuple[bool, str]:
    clone = H.scratch_dir() / "shallow"
    source = top_deleted().root.as_uri()
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", source, str(clone)], check=True, capture_output=True
    )
    result = H.run_gate("", args=["--scan", str(clone)])
    tail = messages.f9_scan_tail(1, 4, [reach(1)], Read.SHALLOW)
    return expect(result, 0, shared.g1_green_scan(tail), "stdout")


def repository_without_a_commit() -> tuple[bool, str]:
    """No commit yet: nothing was ever added, so the history is complete, and nothing fails."""
    consumer = Consumer(H.scratch_dir())
    consumer.write("constitution.yaml", dials_text())
    consumer.git("init", "-q")
    result = H.run_gate(event_json(consumer.root, Write(at("first"), item("first"))))
    return expect(result, 2, k1("first").render(), "stderr")


def shallow_clone_hook_says_so() -> tuple[bool, str]:
    """In a shallow clone the fix does not claim what it cannot know: deleted items are out of sight."""
    clone = H.scratch_dir() / "shallow"
    source = top_deleted().root.as_uri()
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", source, str(clone)], check=True, capture_output=True
    )
    result = H.run_gate(event_json(clone, Write(at("third"), item("third"))))
    return expect(result, 2, k1("third", take=take_next(2, history_read=False)).render(), "stderr")


def fake_git(on_log: str = ":", on_verify: str = ":") -> tuple[dict[str, str], Path]:
    """A PATH that holds python3, dirname and a git that notes every `log` call in a file, does
    `on_log` then, does `on_verify` when asked whether HEAD exists, and is the real git otherwise.
    Returns the environment and the file of calls — a file, because the gate captures what its
    git prints, so nothing a fake writes to stderr would ever reach this runner."""
    directory = H.scratch_dir()
    calls = directory / "calls"
    for tool in ("python3", "dirname"):
        source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert source, tool
        os.symlink(source, directory / tool)
    script = (
        "#!/bin/sh\n"
        'for a in "$@"; do\n'
        f'  if [ "$a" = log ]; then echo log >> "{calls}"; {on_log}; fi\n'
        f'  if [ "$a" = --verify ]; then {on_verify}; fi\n'
        "done\n"
        f'exec "{shutil.which("git")}" "$@"\n'
    )
    (directory / "git").write_text(script)
    (directory / "git").chmod(0o755)
    return {"PATH": str(directory)}, calls


NOT_READ = take_next(1, history_read=False)
BLOCKED = Write(at("first"), item("first"))


def history_is_read_only_for_a_fix() -> tuple[bool, str]:
    """A green write never reads history; a blocked one reads it once, and says so when git fails."""
    consumer = H.fresh_consumer(SETUP)
    env, calls = fake_git(on_log="exit 97")
    green = H.run_gate(event_json(consumer.root, VALID), env=env)
    called_for_green = calls.exists()
    red = H.run_gate(event_json(consumer.root, BLOCKED), env=env)
    ok = (
        green.code == 0
        and not called_for_green
        and red.code == 2
        and calls.read_text().count("log") == 1
        and k1("first", take=NOT_READ).render() in red.stderr
    )
    return (
        ok,
        f"green exit {green.code}, log called: {called_for_green}; red exit {red.code}, log called once",
    )


def slow_history_costs_no_verdict() -> tuple[bool, str]:
    """A history that takes twenty seconds to list: the block still comes, within the hook's patience."""
    consumer = H.fresh_consumer(SETUP)
    env, _ = fake_git(on_log="exec /bin/sleep 20")
    started = time.monotonic()
    red = H.run_gate(event_json(consumer.root, BLOCKED), env=env)
    elapsed = time.monotonic() - started
    ok = red.code == 2 and k1("first", take=NOT_READ).render() in red.stderr and elapsed < 9
    return ok, f"exit {red.code} in {elapsed:.1f} s (bound 9 s), saying history was not read"


def vanished_git_costs_no_verdict() -> tuple[bool, str]:
    """Git gone after the verdict stood — removed between two of history's questions: still a block."""
    consumer = H.fresh_consumer(SETUP)
    env, _ = fake_git(on_verify='/bin/rm -f "$0"')
    red = H.run_gate(event_json(consumer.root, BLOCKED), env=env)
    ok = red.code == 2 and k1("first", take=NOT_READ).render() in red.stderr
    return ok, f"exit {red.code}: {red.stderr.splitlines()[0] if red.stderr else red.stdout}"


def unread_history_in_the_scan() -> tuple[bool, str]:
    consumer = H.fresh_consumer((*SETUP, VALID))
    env, _ = fake_git(on_log="exit 97")
    result = H.run_gate("", args=["--scan", str(consumer.root)], env=env)
    return expect(
        result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 4, [reach(1)], Read.NOT)), "stdout"
    )


LEGACY = at("ITM-06-upper")


def legacy_item_keeps_its_number() -> tuple[bool, str]:
    """An item that exists under a malformed name is told to keep the number it is cited by — by
    the scan, and by the hook when the file is written again."""
    taught = k1("ITM-06-upper", take=NameToTake(Advice.KEEP, 6)).render()
    scanned = scan_of({LEGACY: item("ITM-06-upper")})
    written, _ = gate_on(Write(LEGACY, item("ITM-06-upper")), files={LEGACY: item("ITM-06-upper")})
    ok = scanned.code == 2 and taught in scanned.stdout and written.code == 2 and taught in written.stderr
    return ok, f"scan exit {scanned.code}, hook exit {written.code}: both teach itm-0006"


def contested_number_is_not_kept_twice() -> tuple[bool, str]:
    """Two names show one number: neither is told it keeps it, each is told of the other."""
    formed = at("itm-0006-new")
    result = scan_of({LEGACY: item("ITM-06-upper"), formed: item("itm-0006-new")})
    taught = k1("ITM-06-upper", take=NameToTake(Advice.CONTESTED, 6, other=formed)).render()
    return expect(result, 2, taught, "stdout")


def dated_name_is_an_item() -> tuple[bool, str]:
    """Under width 4 a date-shaped legacy name has the form — number 2026, slug the rest — so the
    scan's line counts it, and a formed item beside it passes (limit 14)."""
    dated = "itm-2026-09-22-x"
    result = scan_of({at(dated): item(dated), ITEM_A: item()})
    return expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(2, 5, [reach(2026)])), "stdout")


def number_the_width_cannot_write() -> tuple[bool, str]:
    stem = "itm-123456-big"
    result = scan_of({at(stem): item(stem)})
    return expect(result, 2, k1(stem, take=NameToTake(Advice.WIDE, 123456)).render(), "stdout")


def full_catalog_is_named() -> tuple[bool, str]:
    files = {at("itm-9-ninth"): item("itm-9-ninth")}
    result = scan_of(files, catalogs(entry(width=1)))
    tail = messages.f9_scan_tail(1, 4, [reach(9, catalog=Catalog("itm", 1, tuple(TERRITORY)))])
    ok = result.code == 0 and tail in result.stdout and "(full:" in tail
    return ok, f"exit {result.code}: {tail}"


def legacy_number_is_not_given_away() -> tuple[bool, str]:
    """During adoption the next number goes above every number a name shows, formed or not."""
    result, _ = gate_on(Write(at("third"), item("third")), files={LEGACY: item("ITM-06-upper")})
    return expect(result, 2, k1("third", take=take_next(7)).render(), "stderr")


def other_scripts_digits() -> tuple[bool, str]:
    """Digits are ASCII: a number the listing's glob cannot see is no number."""
    stem = "itm-\u0966\u0966\u0966\u0967-first"
    result, _ = gate_on(Write(at(stem), item(stem)))
    return expect(result, 2, k1(stem).render(), "stderr")


def uppercase_extension() -> tuple[bool, str]:
    """`.MD` is no part of the form: the listing's glob would not find the file."""
    target = "docs/items/itm-0001-first.MD"
    result, _ = gate_on(Write(target, item()))
    taught = messages.k1_name_without_form(target, "itm-0001-first.MD", CATALOG, take_next(1))
    return expect(result, 2, taught.render(), "stderr")


NESTED_README = "docs/items/sub/README.md"


def nested_file_taken_out() -> tuple[bool, str]:
    """A file below the territory's top directory leaves it only when the patterns match files,
    not directories: git re-includes nothing under a directory a pattern excluded."""
    by_files = catalogs(entry(territory=["docs/items/**/*.md", "!" + NESTED_README]))
    by_directory = catalogs(entry(territory=["docs/items/**", "!" + NESTED_README]))
    out, _ = gate_on(Write(NESTED_README, NO_ENVELOPE), dials_patch=by_files)
    still_in, _ = gate_on(Write(NESTED_README, NO_ENVELOPE), dials_patch=by_directory)
    ok = out.code == 0 and "0 documents examined" in out.stdout and still_in.code == 2
    return (
        ok,
        f"file patterns: exit {out.code}, out of the territory; a directory pattern: exit {still_in.code}",
    )


def holder_is_the_first_by_path() -> tuple[bool, str]:
    files = {at("itm-0001-b"): item("itm-0001-b"), at("itm-0001-a"): item("itm-0001-a")}
    result, _ = gate_on(Write(at("itm-0001-c"), item("itm-0001-c")), files=files)
    taught = messages.k4_number_taken(at("itm-0001-c"), CATALOG, 1, at("itm-0001-a"), take_next(2))
    return expect(result, 2, taught.render(), "stderr")


GOLDEN = {
    "K1": "RED: docs/items/first.md: file name 'first' is not itm-<4 digits>-<kebab-slug>, the form of"
    " catalog 'itm', whose territory holds this file",
    "K1 fix": "  fix: name the file itm-0001-<slug>.md: itm-0001 is the catalog's next number, one more"
    " than the highest it has held, deleted items included;",
    "K1 why": "  why: an item of a numbered kind is cited by its number, and a citation resolves only when"
    " the number stands in the file's name, in one form for the whole catalog",
    "K2 why": "  why: a catalogued document has one identifier: its id is its file name without .md, so a"
    " reference by id and a search by file name find the same document",
    "K2 fix": f"  fix: set id: {STEM_A} in the YAML block between the two '---' lines that open the file;"
    " if other documents already cite the id as it stands, rename the file to match the id instead",
    "K2 no envelope fix": "  fix: start the file with a YAML block between two '---' lines carrying at least"
    f" id: {STEM_A}",
    "K2 missing": f"RED: {ITEM_A}: id missing",
    "K2 differs": f"RED: {ITEM_A}: id 'itm-0001-other' differs from the file name '{STEM_A}'",
    "K2 no envelope": f"RED: {ITEM_A}: id cannot be read: the file does not start with a '---' line",
    "K4": f"RED: {SECOND_TAKEN}: number itm-0001 is already carried by {ITEM_A}",
    "K4 why": "  why: a number cites one item; two items under one number make every reference to it"
    " ambiguous",
    "K4 fix": f"  fix: {ITEM_A} keeps its number; name the file itm-0002-<slug>.md:",
    "keep": "  fix: rename the file with git mv to itm-0006-<slug>.md: it keeps its number,",
    "contested": f"  fix: the name shows number 6, and so does {at('itm-0006-new')}: only one of the two",
    "words": "  fix: rename the file to itm-<number>-<slug>.md: the number it is already cited by,",
    "full": "  fix: no name can be given: catalog 'itm' has used every number 1 digit(s) can write.",
    "wide": "  fix: no name can be given: the name shows number 123456, which 4 digit(s) cannot write.",
    "not read": "itm-0001 is one more than the highest number seen — this clone's history is incomplete or"
    " could not be read",
}

# K3 is the scan's, on stdout
K3_GOLDEN = [
    f"RED: catalog 'itm': 2 items carry number itm-0001: {ITEM_A}, {SECOND_TAKEN}",
    "  why: a number cites one item; two items under one number make every reference to it ambiguous",
    "  fix: the item already on the main branch keeps its number; every other one takes a number of its"
    " own, one more than the highest the catalog has held: rename its file, set its id to the new name,"
    " and rewrite the references to it made on its own branch",
]


def golden_lines() -> tuple[bool, str]:
    """The texts as literals, typed here by hand: the cases above compare with what the message
    functions return, so a slip inside a function would pass them all."""
    runs = {
        "K1": gate_on(Write(at("first"), item("first")))[0],
        "K2 missing": gate_on(Write(ITEM_A, item(drop=("id",))))[0],
        "K2 differs": gate_on(Write(ITEM_A, item(id="itm-0001-other")))[0],
        "K2 no envelope": gate_on(Write(ITEM_A, NO_ENVELOPE))[0],
        "K4": gate_on(Write(SECOND_TAKEN, item("itm-0001-second")), files={ITEM_A: item()})[0],
    }
    runs["K1 fix"] = runs["K1 why"] = runs["K1"]
    runs["K2 why"] = runs["K2 fix"] = runs["K2 missing"]
    runs["K2 no envelope fix"] = runs["K2 no envelope"]
    runs["K4 why"] = runs["K4 fix"] = runs["K4"]
    legacy = {LEGACY: item("ITM-06-upper")}
    runs["keep"] = gate_on(Write(LEGACY, item("ITM-06-upper")), files=legacy)[0]
    both = {**legacy, at("itm-0006-new"): item("itm-0006-new")}
    runs["contested"] = gate_on(Write(LEGACY, item("ITM-06-upper")), files=both)[0]
    runs["words"] = gate_on(Write(at("old"), item("old")), files={at("old"): item("old")})[0]
    nine = {at("itm-9-ninth"): item("itm-9-ninth")}
    runs["full"] = gate_on(
        Write(at("tenth"), item("tenth")), dials_patch=catalogs(entry(width=1)), files=nine
    )[0]
    big = {at("itm-123456-big"): item("itm-123456-big")}
    runs["wide"] = gate_on(Write(at("itm-123456-big"), item("itm-123456-big")), files=big)[0]
    runs["not read"] = H.run_gate(
        event_json(H.fresh_consumer(SETUP).root, BLOCKED), env=fake_git(on_log="exit 97")[0]
    )
    missing = [key for key, line in GOLDEN.items() if line not in runs[key].stderr]
    k3 = scan_of(COLLIDING).stdout
    missing += [line for line in K3_GOLDEN if line not in k3]
    found = len(GOLDEN) + len(K3_GOLDEN)
    return not missing, f"{found} literal lines found" if not missing else f"not found: {missing}"


# ---------------------------------------------------------------- the session-start printer


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
    if remove is not None:
        (consumer.root / remove).unlink()
    return consumer.root


ZERO_LINE = (
    "const-catalogs: no document is examined — const-catalogs.catalogs is an empty list in constitution.yaml"
)


def session_start_zero_line() -> tuple[bool, str]:
    """Nothing while a catalog is listed; the zero line typed by hand when the dial is an empty list
    and when it is absent, of the size the module document states."""
    listed = SESSION.run_gate(session_json(session_root()))
    listed_ok = listed.code == 0 and listed.stdout == "" and listed.stderr == ""
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"one line of ([0-9,]+) characters saying that no document is examined", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    empty = SESSION.run_gate(session_json(session_root({NAMESPACE: {"catalogs": []}})))
    empty_ok = empty.code == 0 and empty.stdout == ZERO_LINE + "\n" and empty.stderr == ""
    absent = SESSION.run_gate(session_json(session_root({NAMESPACE: {}})))
    absent_ok = absent.code == 0 and absent.stdout == ZERO_LINE + "\n"
    return all_of(
        [
            (listed_ok, f"a listed catalog printed: {listed.stdout!r} {listed.stderr!r}"),
            (empty_ok, f"an empty list got: {empty.stdout!r} {empty.stderr!r}"),
            (absent_ok, f"an absent dial got: {absent.stdout!r} {absent.stderr!r}"),
            (
                stated == len(ZERO_LINE),
                f"the document states {stated} characters, the line has {len(ZERO_LINE)}",
            ),
        ],
        f"nothing when listed; the zero line of {len(ZERO_LINE)} characters when empty or absent, as stated",
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
        f"const-catalogs: no constitution.yaml in {root} — the catalog gate examines nothing there until the"
        " file lists a catalog in const-catalogs.catalogs"
    )
    no_dials_ok = no_dials.code == 0 and no_dials.stdout == no_dials_line + "\n"
    (root / "sub").mkdir()
    from_sub = SESSION.run_gate(session_json(root / "sub"))
    from_sub_ok = from_sub.code == 0 and from_sub.stdout == no_dials_line + "\n"
    loose = colon_dir()
    no_repo = SESSION.run_gate(session_json(loose), env={"GIT_CEILING_DIRECTORIES": str(loose.parent)})
    no_repo_line = (
        f"const-catalogs: {loose} is not inside a git repository — the catalog gate examines nothing there"
    )
    no_repo_ok = no_repo.code == 0 and no_repo.stdout == no_repo_line + "\n"
    bad = SESSION.run_gate(session_json(session_root(raw_dials="root-policy: [\n")))
    bad_ok = (
        bad.code == 1
        and bad.stdout == ""
        and bad.stderr.startswith("BROKEN: constitution.yaml is not valid YAML")
        and messages.s1_could_not_run() in bad.stderr
    )
    arg = SESSION.run_gate(session_json(session_root()), args=["--scan"])
    arg_ok = arg.code == 1 and "BROKEN: misinvocation: unexpected argument --scan" in arg.stderr
    return all_of(
        [
            (no_dials_ok, f"no dials got: {no_dials.stdout!r} {no_dials.stderr[:200]!r}"),
            (from_sub_ok, f"no dials from a subfolder got: {from_sub.stdout!r} {from_sub.stderr[:200]!r}"),
            (no_repo_ok, f"no repository got: {no_repo.stdout!r} {no_repo.stderr[:200]!r}"),
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
        "BROKEN: const-catalogs needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{MODULE_ROOT / 'requirements.txt'}' — until then the gate's state is not said at session start"
    )
    yaml_ok, yaml_said = broken_first_line(no_yaml, c2)
    yaml_ok = yaml_ok and messages.s1_could_not_run() in no_yaml.stderr and no_yaml.stdout == ""
    bin_dir = H.scratch_dir()
    (bin_dir / "sh").symlink_to(H.sh)
    (bin_dir / "dirname").symlink_to(shutil.which("dirname") or "dirname")
    no_python = SESSION.run_gate(session_json(session_root()), env={"PATH": str(bin_dir)})
    c1 = (
        "BROKEN: const-catalogs needs python3 — fix: install Python 3.12 or newer"
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
        and write_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/check-catalog-item.sh"]
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
    Assertion(25, "C5: an entry of the wrong shape, fifteen ways, named by position and field", entry_shapes),
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
    Assertion(49, "scan: a listed catalog with no item yet is named, with a zero count", scan_empty_catalog),
    Assertion(
        50,
        "a deleted top number is not suggested again: K1 names 3 after 1 and a deleted 2",
        deleted_top_number_is_not_suggested,
    ),
    Assertion(51, "the same in K4's fix", deleted_top_number_in_k4),
    Assertion(
        52,
        "history moves the advice, never the verdict: the deleted number itself still passes",
        deleted_number_is_not_refused,
    ),
    Assertion(53, "scan: the line names history where it went further than the tree", scan_names_history),
    Assertion(
        54, "a name an item was renamed to counts as added: rename detection is off", renamed_name_is_history
    ),
    Assertion(55, "scan: a shallow clone has no history, and the line says so", shallow_clone_says_so),
    Assertion(56, "a repository with no commit yet: no history, no failure", repository_without_a_commit),
    Assertion(
        57, "a shallow clone, hook: the fix does not claim to know deleted items", shallow_clone_hook_says_so
    ),
    Assertion(
        58,
        "history is read only once a fix will name a number: a green write never calls it",
        history_is_read_only_for_a_fix,
    ),
    Assertion(
        59,
        "adoption: an item that exists under a malformed name keeps the number it shows",
        legacy_item_keeps_its_number,
    ),
    Assertion(
        60,
        "adoption: the next number goes above a number a malformed name shows",
        legacy_number_is_not_given_away,
    ),
    Assertion(61, "K1: digits of another script are no number", other_scripts_digits),
    Assertion(62, "K1: an uppercase .MD is not the form", uppercase_extension),
    Assertion(
        63,
        "a nested file leaves a territory of file patterns, not one of directory patterns",
        nested_file_taken_out,
    ),
    Assertion(64, "K4: of two holders the first by path is named", holder_is_the_first_by_path),
    Assertion(
        65, "golden lines: the taught texts as literals, not as the functions return them", golden_lines
    ),
    Assertion(
        66,
        "a history twenty seconds slow costs no verdict: the block comes in time",
        slow_history_costs_no_verdict,
    ),
    Assertion(
        67,
        "git gone after the verdict stood: still a block, saying history was not read",
        vanished_git_costs_no_verdict,
    ),
    Assertion(
        68, "scan: a history git would not list is named in the count line", unread_history_in_the_scan
    ),
    Assertion(
        69, "adoption: a number two names show is kept by neither unseen", contested_number_is_not_kept_twice
    ),
    Assertion(
        70, "adoption: a number the width cannot write is named as such", number_the_width_cannot_write
    ),
    Assertion(71, "scan: a catalog whose width is used up is named full", full_catalog_is_named),
    Assertion(
        72,
        "adoption: under width 4 a date-shaped name is an item numbered by its year",
        dated_name_is_an_item,
    ),
    Assertion(73, "C5: a key of the namespace that is no dial is refused, never ignored", a_misspelt_dial),
    Assertion(
        74,
        "session start: nothing when listed; the zero line when the dial is empty or absent",
        session_start_zero_line,
    ),
    Assertion(
        75,
        "session start: no dials file, no repository, malformed dials, an argument",
        session_start_skips_and_failures,
    ),
    Assertion(
        76,
        "the printer's absence paths: PyYAML missing is C2, python3 missing is C1",
        session_start_absence_paths,
    ),
    Assertion(77, "the hooks file's shape", hooks_file_shape),
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
    long_value=Write(ITEM_A, item(id="x" * 12_000)),
    # the skip reason once a negated pattern takes `red` out of the territory, typed by hand
    outside="docs/items/first.md lies in no catalog's territory (itm)",
    resolves_policies=False,
    pattern_dial=PatternDial("catalogs[itm]", lambda pattern: catalogs(entry(territory=[pattern]))),
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
