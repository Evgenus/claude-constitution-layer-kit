"""Fixtures of const-catalogs: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.

The fixture consumer is the shared one, with its three policies. None of them matters here:
a catalog is declared in this module's own dial, with a territory no policy claims, so every
item writes that dial — through the case's setup for the red→green cases, through `gate_on`
for the assertions. The shared items about the root policy and the policies' documents are
not this gate's, and are skipped; their numbers stay free. The session-start printer is the
second entry point, driven through its own items (T74–T77); the skill pointer, a third, is T78.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import pytest
import yaml
from catalogs_gate import messages, start
from catalogs_gate.history import HOOK_SECONDS
from catalogs_gate.model import Advice, Catalog, NameToTake, Reach, Read
from constitution_layer_kit import messages as shared
from constitution_layer_kit.envelope import yaml_error_line
from constitution_layer_kit.model import Broken, EnvelopeState, Finding
from constitution_layer_kit.testing.acceptance import broken_first_line, check_case, expect
from constitution_layer_kit.testing.acceptance import item as acceptance_item
from constitution_layer_kit.testing.consumer import BASE_MARKDOWN, ROOT_POLICY, Consumer
from constitution_layer_kit.testing.harness import (
    Case,
    Edit,
    Harness,
    Result,
    Write,
    event_json,
    fake_program,
)
from constitution_layer_kit.testing.items import (
    NO_ENVELOPE,
    PatternDial,
    Subject,
    fake_claude,
    git_patch,
    git_timeouts,
    hook_budget,
    tr_call,
    tr_hook,
    tr_line,
    tr_turn,
)

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"
PLUGIN_ROOT = SCRIPTS.parent
MODULE_ROOT = PLUGIN_ROOT.parent

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
# — and each is also typed by hand at least once in these fixtures (rule 14 of the gate-script rules)
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


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(case, id=f"T{case.number}", marks=acceptance_item(case.number, case.title))
        for case in CASES
    ],
)
def test_case(case: Case) -> None:
    check_case(H, case)


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


def broken(result: Result, failure: Broken) -> None:
    broken_typed(result, failure.render())


def broken_typed(result: Result, line: str) -> None:
    """The failure's line, typed by hand where the item types it, first; then the count line."""
    broken_first_line(result, line)
    first = f"exit 1, first stderr line: {line}"
    assert shared.c11_broken_count() in result.stderr, f"no count line after: {first}"


@acceptance_item(14, "no catalog listed: nothing is examined, and the count line teaches the dial")
def test_no_catalog_listed() -> None:
    """With no catalog listed, any name passes — and the count line says why."""
    result, _ = gate_on(Write(at("first"), NO_ENVELOPE), dials_patch={NAMESPACE: {}})
    skip = (  # typed by hand
        "const-catalogs.catalogs lists no catalog, so no document is known to be numbered — to declare"
        f" one, write {DECLARATION} in constitution.yaml"
    )
    expect(result, 0, shared.g1_green_skip(skip), "stdout")


@acceptance_item(15, "no catalog listed, scan: the same visible zero")
def test_no_catalog_listed_scan() -> None:
    result = H.run_gate("", args=["--scan", str(H.fresh_consumer().root)])
    expect(result, 0, shared.g1_green_skip(messages.g1_skip_no_catalog()), "stdout")


@acceptance_item(16, "a document in no catalog's territory is a visible skip")
def test_not_an_item() -> None:
    result, _ = gate_on(Write(ELSEWHERE, NO_ENVELOPE))
    skip = messages.g1_skip_not_an_item(ELSEWHERE, [CATALOG])
    expect(result, 0, shared.g1_green_skip(skip), "stdout")
    # a path over 80 characters holding a line break: the skip line stays whole, the break escaped
    long_path = "docs/elsewhere/a\n" + "b" * 100 + ".md"
    long_result, _ = gate_on(Write(long_path, NO_ENVELOPE))
    line = (
        "GREEN: const-catalogs: 0 documents examined — docs/elsewhere/a\\n"
        + "b" * 100
        + ".md lies in no catalog's territory (itm)"
    )
    expect(long_result, 0, line, "stdout")


NO_POLICIES = yaml.safe_dump(  # a dials file with no root_policy at all
    {"module_prefix": "const-", **catalogs(entry())}, sort_keys=False
)


@acceptance_item(17, "no policies at all, red half: the dial alone numbers a project's documents")
def test_no_policies_red() -> None:
    """A project without policies numbers its documents: the dial is all the gate reads."""
    result, _ = gate_on(Write(at("first"), item("first")), raw_dials=NO_POLICIES)
    expect(result, 2, k1("first").render(), "stderr")


@acceptance_item(18, "no policies at all, green half")
def test_no_policies_green() -> None:
    result, _ = gate_on(VALID, raw_dials=NO_POLICIES)
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


@acceptance_item(19, "a root policy named and missing is not this gate's failure")
def test_broken_governance_is_not_this_gates() -> None:
    """A root policy that is named and missing breaks the gates that resolve policies, not this one."""
    result, _ = gate_on(VALID, remove=ROOT_POLICY)
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


@acceptance_item(20, "a catalog inside a policy's territory: numbering and governance do not meet")
def test_inside_a_policys_territory() -> None:
    """A catalog's territory may lie inside a policy's: numbering and governance do not meet."""
    patch = catalogs(entry("note", ["docs/notes/**"]))
    result, _ = gate_on(Write("docs/notes/a.md", item("a")), dials_patch=patch)
    taught = messages.k1_name_without_form("docs/notes/a.md", "a", NOTES, take_next(1))
    expect(result, 2, taught.render(), "stderr")


@acceptance_item(21, "one territory, written once, used by a policy and a catalog through a YAML alias")
def test_territory_by_alias() -> None:
    """One territory written once and used twice, by YAML's own alias: the policy's and the catalog's."""
    raw = (
        f"module_prefix: const-\nroot_policy: {ROOT_POLICY}\n"
        "root-policy: {territory: ['docs/policies/**']}\n"
        "notes-policy:\n  territory: &notes ['docs/notes/**']\n"
        f"{NAMESPACE}:\n  catalogs:\n    - {{prefix: note, territory: *notes}}\n"
    )
    result, _ = gate_on(Write("docs/notes/note-0001-first.md", item("note-0001-first")), raw_dials=raw)
    green = messages.g1_item_of(Catalog("note", 4, ("docs/notes/**",)))
    expect(result, 0, shared.g1_green_hook(green), "stdout")


@acceptance_item(22, "the rest of the envelope is not judged here: a bad type and status pass")
def test_rest_of_envelope_not_judged() -> None:
    result, _ = gate_on(Write(ITEM_A, item(type="memo", status="draft", drop=("title",))))
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


@acceptance_item(23, "width defaults to four")
def test_width_defaults_to_four() -> None:
    result, _ = gate_on(VALID, dials_patch=catalogs(entry()))
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


@acceptance_item(73, "C5: a key of the namespace that is no dial is refused, never ignored")
def test_a_misspelt_dial() -> None:
    """A key of the namespace that is none of the three is refused, never a setting ignored in
    silence — `catalog:` for `catalogs:` would otherwise read as no catalog listed."""
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"catalog": [entry()]}})
    broken_typed(
        result,
        "BROKEN: constitution.yaml: const-catalogs.catalog is no dial of this module — fix: a misspelt dial"
        " would be ignored in silence, so none is: write one of severity, log_dir, catalogs",
    )


# the declaration two lines teach, the skip and the C5: its frame and the entry's form, typed once
DECLARATION = (
    "const-catalogs: {catalogs: [{prefix: <lowercase letters and digits>, territory: [<patterns of the"
    " paths where the numbered documents live>], width: 4}]}"
)


@acceptance_item(24, "C5: catalogs that is not a list")
def test_catalogs_not_a_list() -> None:
    result, _ = gate_on(VALID, dials_patch={NAMESPACE: {"catalogs": entry()}})
    broken_typed(  # typed by hand
        result,
        "BROKEN: constitution.yaml: const-catalogs.catalogs must be a list of catalogs — fix: write it as"
        f" {DECLARATION}, or remove the key",
    )


@acceptance_item(25, "C5: an entry of the wrong shape, fifteen ways, named by position and field")
def test_entry_shapes() -> None:
    """Each malformed entry is named by its position and by what is wrong with it: fifteen shapes,
    a prefix ending in a line break and a width of 10 among them. Each is exit 1, never 2, never 0."""
    shapes: list[tuple[object, str]] = [
        ("itm", "is not a mapping of prefix, territory and width"),  # typed by hand
        (entry(start=1), messages.entry_unknown_key("start")),
        (
            {"territory": TERRITORY},
            # typed by hand
            "needs a prefix of lowercase letters and digits — in quotes when it is all digits",
        ),
        (entry("ITM"), messages.entry_prefix()),
        (entry("it-m"), messages.entry_prefix()),
        (entry("itm\n"), messages.entry_prefix()),
        ({"prefix": 7, "territory": TERRITORY}, messages.entry_prefix()),
        ({"prefix": "itm"}, "needs a territory: a non-empty list of path patterns"),  # typed by hand
        (entry(territory=[]), messages.entry_territory()),
        (entry(territory=[""]), messages.entry_territory()),
        ({"prefix": "itm", "territory": "docs/items/**"}, messages.entry_territory()),
        (entry(width=0), "has a width that is not a whole number from 1 to 9"),  # typed by hand
        (entry(width=10), messages.entry_width()),
        (entry(width="4"), messages.entry_width()),
        (entry(width=True), messages.entry_width()),
    ]
    for shape, what in shapes:
        broken(
            gate_on(VALID, dials_patch=catalogs(entry("ok"), shape))[0], messages.c5_catalog_entry(2, what)
        )
    # a key with a line break is shown escaped: one line, typed by hand
    broken_typed(
        gate_on(VALID, dials_patch=catalogs(entry("ok"), {**entry(), "a\nb": 1}))[0],
        "BROKEN: constitution.yaml: entry 2 of const-catalogs.catalogs carries the key 'a\\nb'; an entry"
        " holds prefix, territory and width, and nothing else — fix: write the entry as {prefix: <lowercase"
        " letters and digits>, territory: [<patterns of the paths where the numbered documents live>],"
        " width: 4}",
    )


@acceptance_item(26, "C5: a territory pattern git would read as a comment, in an entry")
def test_entry_pattern_git_would_misread() -> None:
    result, _ = gate_on(VALID, dials_patch=catalogs(entry(territory=["#docs/items/**"])))
    broken_typed(
        result,
        "BROKEN: constitution.yaml: const-catalogs.catalogs[itm] holds a pattern git would not read as"
        " one: '#docs/items/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a"
        " line break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break",
    )


TWICE = catalogs(entry(), entry(territory=["docs/more/**"], width=3))


@acceptance_item(27, "C5: one prefix listed twice fails the load")
def test_prefix_listed_twice() -> None:
    broken_typed(  # typed by hand
        gate_on(VALID, dials_patch=TWICE)[0],
        "BROKEN: constitution.yaml: const-catalogs.catalogs lists prefix 'itm' twice — fix: one prefix names"
        " one catalog, or a number would cite two kinds: join the two entries' territories in one entry, or"
        " give one of them another prefix — before it has items, since an id never changes",
    )


@acceptance_item(28, "C5: the same in a scan: exit 1, so CI turns red")
def test_prefix_listed_twice_scan() -> None:
    broken(scan_of({}, TWICE), messages.c5_prefix_listed_twice("itm"))


@acceptance_item(29, "two catalogs: one sequence each, the same number in both is no collision")
def test_two_catalogs() -> None:
    """Two kinds, two prefixes, one sequence each: the same number in both is no collision."""
    patch = catalogs(entry(), entry("note", ["docs/notes/**"]))
    files = {ITEM_A: item(), "docs/notes/note-0001-first.md": item("note-0001-first")}
    expect(
        scan_of(files, patch),
        0,
        shared.g1_green_scan(
            messages.f9_scan_tail(2, 2 + BASE_MARKDOWN, [reach(1), reach(1, catalog=NOTES)])
        ),
        "stdout",
    )


@acceptance_item(30, "two territories over one file: the catalog whose prefix the name carries judges")
def test_overlap_takes_the_prefix_carried() -> None:
    """Where two territories hold one file, the catalog whose prefix the name carries judges it."""
    patch = catalogs(entry(), entry("shr", ["docs/items/shared/**"]))
    result, _ = gate_on(
        Write("docs/items/shared/shr-0001-first.md", item("shr-0001-first")), dials_patch=patch
    )
    green = messages.g1_item_of(Catalog("shr", 4, ("docs/items/shared/**",)))
    expect(result, 0, shared.g1_green_hook(green), "stdout")


@acceptance_item(31, "two territories over one file, no prefix carried: the first listed judges")
def test_overlap_without_a_prefix() -> None:
    """A name that carries neither prefix is judged by the first catalog listed."""
    patch = catalogs(entry(), entry("shr", ["docs/items/shared/**"]))
    result, _ = gate_on(Write("docs/items/shared/first.md", item("first")), dials_patch=patch)
    taught = messages.k1_name_without_form("docs/items/shared/first.md", "first", CATALOG, take_next(1))
    expect(result, 2, taught.render(), "stderr")


@acceptance_item(32, "severity warn: the finding travels in the JSON and the write proceeds")
def test_severity_warn() -> None:
    result, _ = gate_on(Write(at("first"), item("first")), dials_patch=own(severity="warn"))
    ok = result.code == 0 and not result.stderr and k1("first").headline in result.stdout
    assert ok, f"exit {result.code}; the finding travels in the JSON on stdout"


COLLIDING = {
    ITEM_A: item(),
    at("itm-0001-second"): item("itm-0001-second"),
    at("itm-0002-third"): item("itm-0002-third"),
}
K3 = messages.k3_number_shared(CATALOG, 1, [ITEM_A, at("itm-0001-second")])


@acceptance_item(33, "K3, red half: two items under one number fail the scan, exit 2, both files named")
def test_scan_collision() -> None:
    """The red half of the uniqueness gate: two items under one number."""
    result = scan_of(COLLIDING)
    count = shared.f9_count_scan(1, messages.f9_scan_tail(3, 3 + BASE_MARKDOWN, [reach(2)]))
    ok = result.code == 2 and K3.render() in result.stdout and count in result.stdout
    assert ok, f"exit {result.code}: {result.stdout}{result.stderr}"


@acceptance_item(34, "K3, green half: the renumbered pair passes")
def test_scan_renumbered() -> None:
    """The green half: the younger item renumbered, the pair passes."""
    files = {
        ITEM_A: item(),
        at("itm-0003-second"): item("itm-0003-second"),
        at("itm-0002-third"): item("itm-0002-third"),
    }
    expect(
        scan_of(files),
        0,
        shared.g1_green_scan(messages.f9_scan_tail(3, 3 + BASE_MARKDOWN, [reach(3)])),
        "stdout",
    )


@acceptance_item(35, "a gap is legitimate: numbers 1 and 9 alone are green")
def test_scan_gap_is_legitimate() -> None:
    files = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
    expect(
        scan_of(files),
        0,
        shared.g1_green_scan(messages.f9_scan_tail(2, 2 + BASE_MARKDOWN, [reach(9)])),
        "stdout",
    )


@acceptance_item(49, "scan: a listed catalog with no item yet is named, with a zero count")
def test_scan_empty_catalog() -> None:
    """A listed catalog with no item yet is named as such: a visible zero, and the first number is 1."""
    expect(
        scan_of({}), 0, shared.g1_green_scan(messages.f9_scan_tail(0, BASE_MARKDOWN, [reach(None)])), "stdout"
    )


@acceptance_item(36, "scan: a finding with counts, exit 2, ignoring severity warn")
def test_scan_ignores_warn() -> None:
    result = scan_of({at("first"): item("first")}, own(severity="warn"))
    expect(result, 2, k1("first", take=IN_WORDS).render(), "stdout")


@acceptance_item(37, "scan: a name with no number is one finding and no part of a collision")
def test_scan_name_and_number() -> None:
    """An item whose name carries no number is one finding and takes no part in the collision check."""
    result = scan_of({**COLLIDING, at("first"): item("first")})
    count = shared.f9_count_scan(2, messages.f9_scan_tail(4, 4 + BASE_MARKDOWN, [reach(2)]))
    taught = (k1("first", take=IN_WORDS).render(), K3.render(), count)
    ok = result.code == 2 and all(text in result.stdout for text in taught)
    assert ok, f"exit {result.code}: two findings, four items"


@acceptance_item(38, "scan: a tracked file deleted from the working tree is left out, not a failure")
def test_scan_with_deleted_file() -> None:
    """A tracked item deleted from the working tree, deletion not staged: not a document any more."""
    consumer = H.fresh_consumer((*SETUP, VALID, Write(at("itm-0002-second"), item("itm-0002-second"))))
    (consumer.root / ITEM_A).unlink()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    expect(result, 0, shared.g1_green_scan(messages.f9_scan_tail(1, 1 + BASE_MARKDOWN, [reach(2)])), "stdout")


@acceptance_item(39, "scan: 300 items in seconds (each item read once)")
def test_scan_scales() -> None:
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
    assert ok, f"300 items examined in {elapsed:.1f} s (bound 15 s); exit {result.code}"


ONE_AND_NINE = {ITEM_A: item(), at("itm-0009-ninth"): item("itm-0009-ninth")}
K4 = messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, take_next(2))


@acceptance_item(
    43, "an item that exists is never judged on its number: of two that collide, either can be edited"
)
def test_existing_item_is_not_judged_on_its_number() -> None:
    """Of two items that already collide, either may still be written: which one renumbers is a
    question of branches, answered by the scan's finding, not by blocking the frozen one's edits."""
    files = {ITEM_A: item(), SECOND_TAKEN: item("itm-0001-second")}
    result, _ = gate_on(Write(SECOND_TAKEN, item("itm-0001-second")), files=files)
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


@acceptance_item(44, "K4: an untracked item, not ignored, holds its number")
def test_untracked_item_holds_its_number() -> None:
    """An item nobody committed yet is in the working tree all the same, and its number is taken."""
    result, _ = gate_on(Write(SECOND_TAKEN, item("itm-0001-second")), files={ITEM_A: item()})
    expect(result, 2, K4.render(), "stderr")


@acceptance_item(45, "K4: an Edit that creates a file is a new item")
def test_edit_that_creates_is_new() -> None:
    result, _ = gate_on(Edit(SECOND_TAKEN, "", item("itm-0001-second")), files={ITEM_A: item()})
    expect(result, 2, K4.render(), "stderr")


@acceptance_item(46, "a free number below the highest passes: the gate asks for free, not for next")
def test_free_number_below_the_highest() -> None:
    """The gate asks for a free number, not for the next one: allocation is advice, a gap is legitimate."""
    result, _ = gate_on(Write(at("itm-0005-fifth"), item("itm-0005-fifth")), files=ONE_AND_NINE)
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


@acceptance_item(47, "K1 for a new file names the next free number: 10 after 1 and 9")
def test_next_free_number_is_named() -> None:
    result, _ = gate_on(Write(at("tenth"), item("tenth")), files=ONE_AND_NINE)
    expect(result, 2, k1("tenth", take=take_next(10)).render(), "stderr")


@acceptance_item(48, "the width exhausted: the fix is in words, no name is invented")
def test_width_exhausted() -> None:
    """Past the last number the width can write, the fix falls back to words: no name is invented."""
    files = {at("itm-9-ninth"): item("itm-9-ninth")}
    result, _ = gate_on(Write(at("tenth"), item("tenth")), dials_patch=catalogs(entry(width=1)), files=files)
    expect(
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


@acceptance_item(50, "a deleted top number is not suggested again: K1 names 3 after 1 and a deleted 2")
def test_deleted_top_number_is_not_suggested() -> None:
    result = H.run_gate(event_json(top_deleted().root, Write(at("third"), item("third"))))
    expect(result, 2, k1("third", take=take_next(3)).render(), "stderr")


@acceptance_item(51, "the same in K4's fix")
def test_deleted_top_number_in_k4() -> None:
    result = H.run_gate(event_json(top_deleted().root, Write(SECOND_TAKEN, item("itm-0001-second"))))
    expect(
        result, 2, messages.k4_number_taken(SECOND_TAKEN, CATALOG, 1, ITEM_A, take_next(3)).render(), "stderr"
    )


@acceptance_item(52, "history moves the advice, never the verdict: the deleted number itself still passes")
def test_deleted_number_is_not_refused() -> None:
    """History moves the advice only: a number free in the working tree passes in every clone."""
    again = Write(at("itm-0002-again"), item("itm-0002-again"))
    result = H.run_gate(event_json(top_deleted().root, again))
    expect(result, 0, shared.g1_green_hook(messages.g1_item_of(CATALOG)), "stdout")


def fake_gpg(root: Path) -> None:
    """Signs every later commit of the repository through a fake `gpg.program` and turns
    `log.showSignature` on; the fake logs each call to a file and, to verify, says its human text on
    stderr as gpg does, which git log prints before the formatted line."""
    folder = H.scratch_dir()
    log = folder / "gpg.log"
    program = folder / "gpg"
    program.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {shlex.quote(str(log))}\n"
        "cat > /dev/null\n"
        'case "$*" in\n'
        "  *--verify*)\n"
        "    printf 'gpg: Good signature from \"fake signer\"\\n' >&2\n"
        "    printf '[GNUPG:] GOODSIG 0123456789ABCDEF fake signer\\n'\n"
        "    printf '[GNUPG:] VALIDSIG 0123456789ABCDEF 2026-10-06 1 0 4 0 1 8 00 0123456789ABCDEF\\n';;\n"
        "  *)\n"
        "    printf '[GNUPG:] SIG_CREATED D 1 8 00 1 0123456789ABCDEF 1\\n' >&2\n"
        "    printf -- '-----BEGIN PGP SIGNATURE-----\\n\\nZmFrZQ==\\n-----END PGP SIGNATURE-----\\n';;\n"
        "esac\n",
        encoding="utf-8",
    )
    program.chmod(0o755)
    for key, value in (
        ("gpg.format", "openpgp"),
        ("gpg.program", str(program)),
        ("user.signingkey", "FIXTURE"),
        ("commit.gpgsign", "true"),
        ("log.showSignature", "true"),
    ):
        subprocess.run(["git", "config", key, value], cwd=root, check=True)


TOP_LEVEL = Catalog("itm", 4, ("itm-*.md",))  # a catalog whose items stand in the repository's top folder


def top_level_deleted(signed: bool) -> Consumer:
    """Items 1 and 2 of a catalog whose items stand in the top folder, committed, then item 2 deleted
    and the deletion committed. `signed`: every commit after the first is signed through a fake
    `gpg.program`, with `log.showSignature` on, so the repository's own `git log` prints the check."""
    consumer = Consumer(H.scratch_dir()).build()
    if signed:
        fake_gpg(consumer.root)
    consumer.write("constitution.yaml", dials_text(catalogs(entry(territory=list(TOP_LEVEL.territory)))))
    consumer.write("itm-0001-first.md", item("itm-0001-first"))
    consumer.commit()
    consumer.write("itm-0002-second.md", item("itm-0002-second"))
    consumer.commit()
    consumer.git("rm", "-q", "itm-0002-second.md")
    consumer.commit()
    return consumer


@acceptance_item(53, "scan: the line names history where it went further than the tree")
def test_scan_names_history() -> None:
    """The scan names history where it went further than the tree. A signed history, read with
    `log.showSignature` on, gives the same: the signature check git prints before a commit's names
    would stand in front of the name of the first file the commit added, and a name without a folder
    — an item in the top folder — would carry it as part of its stem and lose its number."""
    result = H.run_gate("", args=["--scan", str(top_deleted().root)])
    wanted = shared.g1_green_scan(messages.f9_scan_tail(1, 1 + BASE_MARKDOWN, [reach(1, 2)]))
    top = shared.g1_green_scan(messages.f9_scan_tail(1, 1 + BASE_MARKDOWN, [reach(1, 2, TOP_LEVEL)]))
    signed = top_level_deleted(signed=True)
    shown = subprocess.run(
        ["git", "log", "-1", "--format=%h"], cwd=signed.root, capture_output=True, text=True, check=False
    )
    if "fake signer" not in shown.stdout + shown.stderr:  # the case cannot pass for want of a check
        pytest.fail(f"git log did not print the check: {shown.stdout}{shown.stderr}")
    plain = H.run_gate("", args=["--scan", str(top_level_deleted(signed=False).root)])
    after = H.run_gate("", args=["--scan", str(signed.root)])
    expect(result, 0, wanted, "stdout")
    expect(plain, 0, top, "stdout")
    expect(after, 0, top, "stdout")


@acceptance_item(54, "a name an item was renamed to counts as added: rename detection is off")
def test_renamed_name_is_history() -> None:
    """An item renamed to a higher number and then deleted: git would report the rename as such, not
    as an addition, so rename detection is off and the new name counts as added."""
    consumer = H.fresh_consumer((*SETUP, VALID))
    consumer.git("mv", ITEM_A, at("itm-0007-first"))
    consumer.commit()
    consumer.git("rm", "-q", at("itm-0007-first"))
    consumer.commit()
    result = H.run_gate("", args=["--scan", str(consumer.root)])
    expect(
        result, 0, shared.g1_green_scan(messages.f9_scan_tail(0, BASE_MARKDOWN, [reach(None, 7)])), "stdout"
    )


@acceptance_item(55, "scan: a shallow clone has no history, and the line says so")
def test_shallow_clone_says_so() -> None:
    clone = H.scratch_dir() / "shallow"
    source = top_deleted().root.as_uri()
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", source, str(clone)], check=True, capture_output=True
    )
    result = H.run_gate("", args=["--scan", str(clone)])
    tail = messages.f9_scan_tail(1, 1 + BASE_MARKDOWN, [reach(1)], Read.SHALLOW)
    expect(result, 0, shared.g1_green_scan(tail), "stdout")


@acceptance_item(56, "a repository with no commit yet: no history, no failure")
def test_repository_without_a_commit() -> None:
    """No commit yet: nothing was ever added, so the history is complete, and nothing fails."""
    consumer = Consumer(H.scratch_dir())
    consumer.write("constitution.yaml", dials_text())
    consumer.git("init", "-q")
    result = H.run_gate(event_json(consumer.root, Write(at("first"), item("first"))))
    expect(result, 2, k1("first").render(), "stderr")


@acceptance_item(57, "a shallow clone, hook: the fix does not claim to know deleted items")
def test_shallow_clone_hook_says_so() -> None:
    """In a shallow clone the fix does not claim what it cannot know: deleted items are out of sight."""
    clone = H.scratch_dir() / "shallow"
    source = top_deleted().root.as_uri()
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", source, str(clone)], check=True, capture_output=True
    )
    result = H.run_gate(event_json(clone, Write(at("third"), item("third"))))
    expect(result, 2, k1("third", take=take_next(2, history_read=False)).render(), "stderr")


def fake_git(on_log: str = ":", on_verify: str = ":") -> tuple[dict[str, str], Path]:
    """A PATH that holds python3, dirname and a git that notes every `log` call in a file, does
    `on_log` then, does `on_verify` when asked whether HEAD exists, and is the real git otherwise.
    Returns the environment and the file of calls — a file, because the gate captures what its
    git prints, so nothing a fake writes to stderr would ever reach this runner. The fake is started
    once before it is used (`fake_program`): its first start inside a hook, slow on a loaded machine,
    took more than the 3 s the hook gives git."""
    directory = H.scratch_dir()
    calls = directory / "calls"
    for tool in ("python3", "dirname"):
        source = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert source, tool
        os.symlink(source, directory / tool)
    script = (
        'for a in "$@"; do\n'
        f'  if [ "$a" = log ]; then echo log >> "{calls}"; {on_log}; fi\n'
        f'  if [ "$a" = --verify ]; then {on_verify}; fi\n'
        "done\n"
        f'exec "{shutil.which("git")}" "$@"\n'
    )
    fake_program(directory / "git", script)
    return {"PATH": str(directory)}, calls


NOT_READ = take_next(1, history_read=False)
BLOCKED = Write(at("first"), item("first"))


@acceptance_item(58, "history is read only once a fix will name a number: a green write never calls it")
def test_history_is_read_only_for_a_fix() -> None:
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
    assert ok, (
        f"green exit {green.code}, log called: {called_for_green}; red exit {red.code}, log called once"
    )


# A process whose clock jumps 100 s forward once it has made the number of git calls the environment names:
# the hook's budget of 25 s is then spent from that call on. The gate's own clock is the only one it moves.
CLOCK_JUMP = """\
import os
import subprocess
import time

after, made, jumped = int(os.environ["CLOCK_JUMP_AFTER"]), [0], [0.0]
run, real = subprocess.run, time.monotonic


def spy(command, *args, **kwargs):
    if command[0] == "git":
        with open(os.environ["CLOCK_JUMP_LOG"], "a") as out:
            out.write(repr(command[1:]) + "\\n")
    done = run(command, *args, **kwargs)
    if command[0] == "git":
        made[0] += 1
        if made[0] == after:
            jumped[0] = 100.0
    return done


subprocess.run = spy
time.monotonic = lambda: real() + jumped[0]
"""


def clock_jump_after_git(calls_before_history: int) -> tuple[dict[str, str], Path]:
    """The environment that moves the gate's clock 100 s on after that many git calls, and the file that
    notes the arguments of every git call the process starts."""
    folder = H.scratch_dir()
    (folder / "sitecustomize.py").write_text(CLOCK_JUMP, encoding="utf-8")
    path = os.pathsep.join(filter(None, [str(folder), os.environ.get("PYTHONPATH")]))
    log = folder / "git-calls"
    after, kept = str(calls_before_history), str(log)
    return {"PYTHONPATH": path, "CLOCK_JUMP_AFTER": after, "CLOCK_JUMP_LOG": kept}, log


def calls_before_history(log: Path) -> int:
    """How many git calls the log holds before the history's first, `rev-parse --verify`."""
    asked = [ast.literal_eval(line.split(" ", 1)[1]) for line in log.read_text().splitlines()]
    return next(number for number, args in enumerate(asked) if "--verify" in args)


@acceptance_item(66, "a history twenty seconds slow costs no verdict: the block comes in time")
def test_slow_history_costs_no_verdict() -> None:
    """A history that takes twenty seconds to list: the block still comes, within the hook's patience. The
    history is given its own 5 s, or what the hook's deadline has left where that is less: with the gate
    declared with 2 s, no git call, the history's included, is given more than that. With the deadline
    already spent when the history is asked, the history is not read and starts no git, and the block stands,
    exit 2, never the shared C12.14 (exit 1): no verdict waits for advice or falls with it."""
    consumer = H.fresh_consumer(SETUP)
    env, _ = fake_git(on_log="exec /bin/sleep 20")
    patch, log = git_patch(H)
    started = time.monotonic()
    red = H.run_gate(event_json(consumer.root, BLOCKED), env={**env, **patch})
    elapsed = time.monotonic() - started
    own = [float(timeout) for timeout in git_timeouts(log)]
    short_patch, short_log = git_patch(H, hook_seconds=2.0)
    short = H.run_gate(event_json(consumer.root, BLOCKED), env={**env, **short_patch})
    left = [float(timeout) for timeout in git_timeouts(short_log)]
    quick_env, _ = fake_git()
    before_history = calls_before_history(log)
    jump_env, jump_log = clock_jump_after_git(before_history)
    spent = H.run_gate(event_json(consumer.root, BLOCKED), env={**quick_env, **jump_env})
    asked = len(jump_log.read_text().splitlines()) if jump_log.exists() else 0
    block = k1("first", take=NOT_READ).render()
    ok = (
        red.code == 2
        and block in red.stderr
        and elapsed < 9
        and bool(own)
        and max(own) > HOOK_SECONDS - 0.5  # the history read has its own 5 s
        and short.code == 2
        and block in short.stderr
        and bool(left)
        and max(left) <= 2.0  # no call is given more than the hook's 2 s
        and spent.code == 2  # the deadline was spent when the history was asked: the block stands
        and block in spent.stderr
        and "budget" not in spent.stderr
        and asked == before_history  # a read asked with nothing left starts no git
    )
    assert ok, (
        f"exit {red.code} in {elapsed:.1f} s (bound 9 s), saying history was not read; the most any git call"
        f" was given: {max(own, default=0):.2f} s, and {max(left, default=0):.2f} s under a hook of 2 s;"
        f" with the deadline spent when the history is asked: exit {spent.code}, {asked} git calls of"
        f" {before_history} before the history"
        f" ({spent.stderr.splitlines()[0][:90] if spent.stderr else spent.stdout[:90]})"
    )


@acceptance_item(67, "git gone after the verdict stood: still a block, saying history was not read")
def test_vanished_git_costs_no_verdict() -> None:
    """Git gone after the verdict stood — removed between two of history's questions: still a block."""
    consumer = H.fresh_consumer(SETUP)
    env, _ = fake_git(on_verify='/bin/rm -f "$0"')
    red = H.run_gate(event_json(consumer.root, BLOCKED), env=env)
    ok = red.code == 2 and k1("first", take=NOT_READ).render() in red.stderr
    assert ok, f"exit {red.code}: {red.stderr.splitlines()[0] if red.stderr else red.stdout}"


@acceptance_item(68, "scan: a history git would not list is named in the count line")
def test_unread_history_in_the_scan() -> None:
    consumer = H.fresh_consumer((*SETUP, VALID))
    env, _ = fake_git(on_log="exit 97")
    result = H.run_gate("", args=["--scan", str(consumer.root)], env=env)
    expect(
        result,
        0,
        shared.g1_green_scan(messages.f9_scan_tail(1, 1 + BASE_MARKDOWN, [reach(1)], Read.NOT)),
        "stdout",
    )


LEGACY = at("ITM-06-upper")


@acceptance_item(59, "adoption: an item that exists under a malformed name keeps the number it shows")
def test_legacy_item_keeps_its_number() -> None:
    """An item that exists under a malformed name is told to keep the number it is cited by — by
    the scan, and by the hook when the file is written again."""
    taught = k1("ITM-06-upper", take=NameToTake(Advice.KEEP, 6)).render()
    scanned = scan_of({LEGACY: item("ITM-06-upper")})
    written, _ = gate_on(Write(LEGACY, item("ITM-06-upper")), files={LEGACY: item("ITM-06-upper")})
    ok = scanned.code == 2 and taught in scanned.stdout and written.code == 2 and taught in written.stderr
    assert ok, f"scan exit {scanned.code}, hook exit {written.code}: both teach itm-0006"


@acceptance_item(69, "adoption: a number two names show is kept by neither unseen")
def test_contested_number_is_not_kept_twice() -> None:
    """Two names show one number: neither is told it keeps it, each is told of the other."""
    formed = at("itm-0006-new")
    result = scan_of({LEGACY: item("ITM-06-upper"), formed: item("itm-0006-new")})
    taught = k1("ITM-06-upper", take=NameToTake(Advice.CONTESTED, 6, other=formed)).render()
    expect(result, 2, taught, "stdout")


@acceptance_item(72, "adoption: under width 4 a date-shaped name is an item numbered by its year")
def test_dated_name_is_an_item() -> None:
    """Under width 4 a date-shaped legacy name has the form — number 2026, slug the rest — so the
    scan's line counts it, and a formed item beside it passes (limit 14)."""
    dated = "itm-2026-09-22-x"
    result = scan_of({at(dated): item(dated), ITEM_A: item()})
    expect(
        result, 0, shared.g1_green_scan(messages.f9_scan_tail(2, 2 + BASE_MARKDOWN, [reach(2026)])), "stdout"
    )


@acceptance_item(70, "adoption: a number the width cannot write is named as such")
def test_number_the_width_cannot_write() -> None:
    stem = "itm-123456-big"
    result = scan_of({at(stem): item(stem)})
    expect(result, 2, k1(stem, take=NameToTake(Advice.WIDE, 123456)).render(), "stdout")


@acceptance_item(71, "scan: a catalog whose width is used up is named full")
def test_full_catalog_is_named() -> None:
    files = {at("itm-9-ninth"): item("itm-9-ninth")}
    result = scan_of(files, catalogs(entry(width=1)))
    tail = (  # typed by hand
        "1 catalogued item(s) examined, 4 Markdown file(s) scanned, 1 catalog(s): itm up to itm-9"
        " (full: the width can write no higher number)"
    )
    ok = result.code == 0 and tail in result.stdout
    assert ok, f"exit {result.code}: {tail}"


@acceptance_item(60, "adoption: the next number goes above a number a malformed name shows")
def test_legacy_number_is_not_given_away() -> None:
    """During adoption the next number goes above every number a name shows, formed or not."""
    result, _ = gate_on(Write(at("third"), item("third")), files={LEGACY: item("ITM-06-upper")})
    expect(result, 2, k1("third", take=take_next(7)).render(), "stderr")


@acceptance_item(61, "K1: digits of another script are no number")
def test_other_scripts_digits() -> None:
    """Digits are ASCII: a number the listing's glob cannot see is no number."""
    stem = "itm-\u0966\u0966\u0966\u0967-first"
    result, _ = gate_on(Write(at(stem), item(stem)))
    expect(result, 2, k1(stem).render(), "stderr")


@acceptance_item(62, "K1: an uppercase .MD is not the form")
def test_uppercase_extension() -> None:
    """`.MD` is no part of the form: the listing's glob would not find the file."""
    target = "docs/items/itm-0001-first.MD"
    result, _ = gate_on(Write(target, item()))
    taught = messages.k1_name_without_form(target, "itm-0001-first.MD", CATALOG, take_next(1))
    expect(result, 2, taught.render(), "stderr")


NESTED_README = "docs/items/sub/README.md"


@acceptance_item(63, "a nested file leaves a territory of file patterns, not one of directory patterns")
def test_nested_file_taken_out() -> None:
    """A file below the territory's top directory leaves it only when the patterns match files,
    not directories: git re-includes nothing under a directory a pattern excluded."""
    by_files = catalogs(entry(territory=["docs/items/**/*.md", "!" + NESTED_README]))
    by_directory = catalogs(entry(territory=["docs/items/**", "!" + NESTED_README]))
    out, _ = gate_on(Write(NESTED_README, NO_ENVELOPE), dials_patch=by_files)
    still_in, _ = gate_on(Write(NESTED_README, NO_ENVELOPE), dials_patch=by_directory)
    ok = out.code == 0 and "0 documents examined" in out.stdout and still_in.code == 2
    assert ok, (
        f"file patterns: exit {out.code}, out of the territory; a directory pattern: exit {still_in.code}"
    )


@acceptance_item(64, "K4: of two holders the first by path is named")
def test_holder_is_the_first_by_path() -> None:
    files = {at("itm-0001-b"): item("itm-0001-b"), at("itm-0001-a"): item("itm-0001-a")}
    result, _ = gate_on(Write(at("itm-0001-c"), item("itm-0001-c")), files=files)
    taught = messages.k4_number_taken(at("itm-0001-c"), CATALOG, 1, at("itm-0001-a"), take_next(2))
    expect(result, 2, taught.render(), "stderr")


# a directory whose name holds a line break and is a page long: a path through it is shown whole, escaped
WEIRD_DIR = "docs/items/w\n" + "w" * 90
WEIRD = "docs/items/w\\n" + "w" * 90  # the same as the message shows it, typed by hand

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
    # a value echoed from a document stays on one line: the break shown escaped, typed by hand
    "K2 id with a break": f"RED: {ITEM_A}: id 'itm-0001-a\\nb' differs from the file name '{STEM_A}'",
    # the written file's path is shown whole, its break escaped, however long; the name cut at 80
    "K1 name with a break": "RED: docs/items/a\\nb.md: file name 'a\\nb' is not itm-<4 digits>-<kebab-slug>,"
    " the form of catalog 'itm', whose territory holds this file",
    "K1 long path": "RED: docs/items/a\\n"
    + "b" * 100
    + ".md: file name 'a\\n"
    + "b" * 78
    + "… [102 characters]' is not itm-<4 digits>-<kebab-slug>, the form of catalog 'itm',"
    " whose territory holds this file",
    # a path through a directory with a break, in the headline of each K2 shape; an id over 80 characters cut
    "K2 missing path": f"RED: {WEIRD}/{STEM_A}.md: id missing",
    "K2 differs path": f"RED: {WEIRD}/{STEM_A}.md: id 'itm-0001-other' differs from the file name '{STEM_A}'",
    "K2 differs long": f"RED: {ITEM_A}: id 'i"
    + "j" * 79
    + f"… [100 characters]' differs from the file name '{STEM_A}'",
    "K2 no envelope path": f"RED: {WEIRD}/{STEM_A}.md: id cannot be read: the file does not start with a"
    " '---' line",
    "K2 yaml detail": f"RED: {ITEM_A}: id cannot be read: the block between the '---' lines is not readable"
    ' YAML: while scanning a double-quoted scalar in "<unicode string>", line 1, column 5: id: "x\\\\q" ^'
    ' found unknown escape character \'q\' in "<unicode string>", line 1, column 8: id: "x\\\\q" ^',
    "K4 paths": f"RED: {WEIRD}/itm-0001-second.md: number itm-0001 is already carried by"
    f" {WEIRD}/itm-0001-a.md",
    "K4 holder fix": f"  fix: {WEIRD}/itm-0001-a.md keeps its number; name the file itm-0002-<slug>.md:",
    "K4": f"RED: {SECOND_TAKEN}: number itm-0001 is already carried by {ITEM_A}",
    "K4 why": "  why: a number cites one item; two items under one number make every reference to it"
    " ambiguous",
    "K4 fix": f"  fix: {ITEM_A} keeps its number; name the file itm-0002-<slug>.md:",
    "keep": "  fix: rename the file with git mv to itm-0006-<slug>.md: it keeps its number,",
    "contested": f"  fix: the name shows number 6, and so does {at('itm-0006-new')}: only one of the two",
    "contested path": f"  fix: the name shows number 6, and so does {WEIRD}/itm-0006-new.md: only one of"
    " the two",
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
    " and rewrite the references to it made on its own branch; of two items both on the main branch,"
    " the one that landed second renumbers the same way, and every reference to it in the tree is"
    " rewritten",
]


@acceptance_item(65, "golden lines: the taught texts as literals, not as the functions return them")
def test_golden_lines() -> None:
    """The texts as literals, typed here by hand: the cases above compare with what the message
    functions return, so a slip inside a function would pass them all. They are the headlines and the
    why lines of K1 to K4, the fixes of K2 (the id to set, the envelope to start) and of K3, the opening
    of K4's fix, and the opening of every advice text: next, keep, contested, words, full, wide, not
    read. Seen to fail with the keep text broken, and with one word of the K1 why changed. A path of over
    80 characters with a line break stands whole and escaped in K1, K3, K4 and the contested fix; a long
    file name is cut; a YAML error with a backslash stands whole, its backslash doubled."""
    runs = {
        "K1": gate_on(Write(at("first"), item("first")))[0],
        "K2 missing": gate_on(Write(ITEM_A, item(drop=("id",))))[0],
        "K2 differs": gate_on(Write(ITEM_A, item(id="itm-0001-other")))[0],
        "K2 no envelope": gate_on(Write(ITEM_A, NO_ENVELOPE))[0],
        "K2 id with a break": gate_on(Write(ITEM_A, item(id="itm-0001-a\nb")))[0],
        "K1 name with a break": gate_on(Write(at("a\nb"), item("a\nb")))[0],
        "K1 long path": gate_on(Write(at("a\n" + "b" * 100), item("a\n" + "b" * 100)))[0],
        "K2 missing path": gate_on(Write(f"{WEIRD_DIR}/{STEM_A}.md", item(drop=("id",))))[0],
        "K2 differs path": gate_on(Write(f"{WEIRD_DIR}/{STEM_A}.md", item(id="itm-0001-other")))[0],
        "K2 differs long": gate_on(Write(ITEM_A, item(id="i" + "j" * 99)))[0],
        "K2 no envelope path": gate_on(Write(f"{WEIRD_DIR}/{STEM_A}.md", NO_ENVELOPE))[0],
        "K2 yaml detail": gate_on(Write(ITEM_A, '---\nid: "x\\q"\n---\n'))[0],
        "K4": gate_on(Write(SECOND_TAKEN, item("itm-0001-second")), files={ITEM_A: item()})[0],
    }
    runs["K1 fix"] = runs["K1 why"] = runs["K1"]
    runs["K2 why"] = runs["K2 fix"] = runs["K2 missing"]
    runs["K2 no envelope fix"] = runs["K2 no envelope"]
    runs["K4 why"] = runs["K4 fix"] = runs["K4"]
    holder = {f"{WEIRD_DIR}/itm-0001-a.md": item("itm-0001-a")}
    runs["K4 paths"] = runs["K4 holder fix"] = gate_on(
        Write(f"{WEIRD_DIR}/itm-0001-second.md", item("itm-0001-second")), files=holder
    )[0]
    legacy = {LEGACY: item("ITM-06-upper")}
    runs["keep"] = gate_on(Write(LEGACY, item("ITM-06-upper")), files=legacy)[0]
    both = {**legacy, at("itm-0006-new"): item("itm-0006-new")}
    runs["contested"] = gate_on(Write(LEGACY, item("ITM-06-upper")), files=both)[0]
    weird_new = {f"{WEIRD_DIR}/itm-0006-new.md": item("itm-0006-new")}
    runs["contested path"] = gate_on(Write(LEGACY, item("ITM-06-upper")), files={**legacy, **weird_new})[0]
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
    two = {f"{WEIRD_DIR}/itm-0001-a.md": item("itm-0001-a"), f"{WEIRD_DIR}/itm-0001-b.md": item("itm-0001-b")}
    k3_paths = (
        f"RED: catalog 'itm': 2 items carry number itm-0001: {WEIRD}/itm-0001-a.md, {WEIRD}/itm-0001-b.md"
    )
    if k3_paths not in scan_of(two).stdout:  # the paths whole, each on the one line, breaks escaped
        missing.append(k3_paths)
    assert not missing, f"not found: {missing}"


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


@acceptance_item(74, "session start: nothing when listed; the zero line when the dial is empty or absent")
def test_session_start_zero_line() -> None:
    """Nothing while a catalog is listed; the zero line typed by hand when the dial is an empty list
    and when it is absent, of the size the module document states. While a catalog is listed, every git
    call of the run carries the 3 s cap of limit 16 of kit-shared-gate-code section 4, read from a spy
    on `subprocess.run`."""
    # the printer is a hook: each of its git calls has the hook's budget, logged before the call is made
    # with no clock, so that a slow git on a loaded machine cuts none of them
    patch, log = git_patch(SESSION, unclocked=True)
    listed = SESSION.run_gate(session_json(session_root()), env=patch)
    listed_ok = listed.code == 0 and listed.stdout == "" and listed.stderr == ""
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"one line of ([0-9,]+) characters saying that no document is examined", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    empty = SESSION.run_gate(session_json(session_root({NAMESPACE: {"catalogs": []}})))
    empty_ok = empty.code == 0 and empty.stdout == ZERO_LINE + "\n" and empty.stderr == ""
    absent = SESSION.run_gate(session_json(session_root({NAMESPACE: {}})))
    absent_ok = absent.code == 0 and absent.stdout == ZERO_LINE + "\n"
    assert listed_ok, f"a listed catalog printed: {listed.stdout!r} {listed.stderr!r}"
    hook_budget(git_timeouts(log))
    assert empty_ok, f"an empty list got: {empty.stdout!r} {empty.stderr!r}"
    assert absent_ok, f"an absent dial got: {absent.stdout!r} {absent.stderr!r}"
    assert stated == len(ZERO_LINE), f"the document states {stated} characters, the line has {len(ZERO_LINE)}"


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


@acceptance_item(75, "session start: no dials file, no repository, malformed dials, an argument")
def test_session_start_skips_and_failures() -> None:
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
        and COULD_NOT_RUN in bad.stderr
    )
    broken_name = "d\n" + "e" * 100  # a folder name holding a line break, over 80 characters
    wide_dir = H.scratch_dir() / broken_name
    wide_dir.mkdir()
    wide_root = Consumer(wide_dir).build().root
    (wide_root / "constitution.yaml").unlink()
    wide = SESSION.run_gate(session_json(wide_root))
    wide_head = "const-catalogs: no constitution.yaml in "
    wide_tail = (
        "d\\n" + "e" * 100 + " — the catalog gate examines nothing there until the file lists a catalog"
    )
    wide_ok = wide.code == 0 and wide.stdout.startswith(wide_head) and wide_tail in wide.stdout
    wide_ok = wide_ok and wide.stdout.count("\n") == 1  # one line: the break is shown escaped
    wide_loose = H.scratch_dir() / broken_name
    wide_loose.mkdir()
    wide_no_repo = SESSION.run_gate(
        session_json(wide_loose), env={"GIT_CEILING_DIRECTORIES": str(wide_loose.parent)}
    )
    wide_no_repo_ok = (
        wide_no_repo.code == 0
        and wide_no_repo.stdout.count("\n") == 1
        and f"{wide_tail.split(' — ')[0]} is not inside a git repository" in wide_no_repo.stdout
    )
    arg = SESSION.run_gate(session_json(session_root()), args=["--scan"])
    arg_ok = arg.code == 1 and "BROKEN: misinvocation: unexpected argument --scan" in arg.stderr
    assert no_dials_ok, f"no dials got: {no_dials.stdout!r} {no_dials.stderr[:200]!r}"
    assert from_sub_ok, f"no dials from a subfolder got: {from_sub.stdout!r} {from_sub.stderr[:200]!r}"
    assert no_repo_ok, f"no repository got: {no_repo.stdout!r} {no_repo.stderr[:200]!r}"
    assert wide_ok, f"a long folder name with a break, no dials, got: {wide.stdout!r}"
    assert wide_no_repo_ok, f"a long folder name with a break, no repository, got: {wide_no_repo.stdout!r}"
    assert bad_ok, f"malformed dials got {bad.code}: {bad.stdout!r} {bad.stderr[:300]!r}"
    assert arg_ok, f"an argument got {arg.code}: {arg.stderr[:200]!r}"


COULD_NOT_RUN = (
    "BROKEN: the session-start line could not be printed — the gate's state is unknown"  # typed by hand
)


@acceptance_item(76, "the printer's absence paths: PyYAML missing is C2, python3 missing is C1")
def test_session_start_absence_paths() -> None:
    """PyYAML missing is C2 first on stderr with the printer's closing line; python3 missing is C1;
    stdout stays empty in both."""
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_yaml = SESSION.run_gate(session_json(session_root()), env={"PYTHONPATH": str(shadow)})
    c2 = (
        "BROKEN: const-catalogs needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{PLUGIN_ROOT / 'requirements.txt'}' — until then the gate's state is not said at session start"
    )
    broken_first_line(no_yaml, c2)
    yaml_ok = messages.z1_could_not_run() in no_yaml.stderr and no_yaml.stdout == ""
    assert yaml_ok, f"PyYAML missing: stderr {no_yaml.stderr.strip()!r}, stdout {no_yaml.stdout!r}"
    bin_dir = H.scratch_dir()
    (bin_dir / "sh").symlink_to(H.sh)
    (bin_dir / "dirname").symlink_to(shutil.which("dirname") or "dirname")
    no_python = SESSION.run_gate(session_json(session_root()), env={"PATH": str(bin_dir)})
    c1 = (
        "BROKEN: const-catalogs needs python3 — fix: install Python 3.12 or newer"
        " (https://www.python.org/downloads/) — until then the gate's state is not said at session start"
    )
    broken_first_line(no_python, c1)
    py_ok = messages.z1_could_not_run() in no_python.stderr and no_python.stdout == ""
    assert py_ok, f"python3 missing: stderr {no_python.stderr.strip()!r}, stdout {no_python.stdout!r}"


@acceptance_item(77, "the hooks file's shape, with integer timeouts; the history read fits the hook's budget")
def test_hooks_file_shape() -> None:
    """Two SessionStart handlers (the printer of the dial's state, the skill pointer) and a SubagentStart
    handler, each with no matcher, and a PreToolUse handler on Write|Edit, exec form, the placeholder in
    args, integer timeouts, every script present. The module's own wait in one hook run, the history read,
    fits the hook's budget the gate declares (`GATE.hook_seconds`); the handlers' timeouts hold that budget
    and `LEFT_FOR_THE_REST`, which the shared item S165 ties; the two printers read no history."""
    hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    root = "${CLAUDE_PLUGIN_ROOT}/scripts/"
    wanted: dict[str, list[list[str]]] = {
        "SessionStart": [[root + "session-start.sh"], [root + "print-skill-pointer.sh"]],
        "SubagentStart": [[root + "print-skill-pointer.sh", "--subagent"]],
        "PreToolUse": [[root + "check-catalog-item.sh"]],
    }
    if set(hooks) != set(wanted):
        pytest.fail(f"events {sorted(hooks)}, wanted {sorted(wanted)}")
    for event, args_lists in wanted.items():
        groups = hooks[event]
        if [[handler["args"] for handler in group["hooks"]] for group in groups] != [
            [args] for args in args_lists
        ]:
            pytest.fail(f"{event}: handlers {groups}")
        for group in groups:
            handler = group["hooks"][0]
            if handler["type"] != "command" or handler["command"] != "sh":
                pytest.fail(f"{event}: not exec form `sh`: {handler}")
            if not isinstance(handler["timeout"], int) or isinstance(handler["timeout"], bool):
                pytest.fail(f"{event}: timeout is no integer: {handler}")
            if not (PLUGIN_ROOT / "scripts" / Path(handler["args"][0]).name).is_file():
                pytest.fail(f"{event}: no script {handler['args'][0]}")
            if ("matcher" in group) != (event == "PreToolUse"):
                pytest.fail(f"{event}: matcher wrong: {group}")
    write_hook = hooks["PreToolUse"][0]
    if write_hook["matcher"] != "Write|Edit":
        pytest.fail(f"PreToolUse matcher {write_hook['matcher']}")
    budget = start.GATE.hook_seconds
    if HOOK_SECONDS > budget:
        pytest.fail(f"the history read waits {HOOK_SECONDS:g} s, over the hook's budget of {budget:g} s")
    pass


# The pointer to the module's skill, typed by hand: printed at session start and as the context a
# subagent starts with.
POINTER = (
    "const-catalogs (advisory): before creating a document of a kind the project numbers — a decision"
    " record, a task, an RFC — and when a write is blocked for its file name, id or number, load the skill"
    " const-catalogs:catalog-item."
)


@acceptance_item(
    78, "the skill pointer: the line as typed, its SubagentStart form, its size stated, its skill present"
)
def test_skill_pointer_printed() -> None:
    """The pointer line: exit 0, the line as typed here and a line break, nothing on stderr; with
    --subagent one JSON object whose hookSpecificOutput is exactly the SubagentStart event name and the
    line; the line's size is the one the module document states, and the skill it names is a folder
    under skills/."""
    script = str(SCRIPTS / "print-skill-pointer.sh")
    plain = subprocess.run([H.sh, script], capture_output=True, text=True, encoding="utf-8", check=False)
    if plain.returncode != 0 or plain.stdout != POINTER + "\n" or plain.stderr != "":
        pytest.fail(repr(plain))
    sub = subprocess.run(
        [H.sh, script, "--subagent"], capture_output=True, text=True, encoding="utf-8", check=False
    )
    if sub.returncode != 0 or sub.stderr != "" or not sub.stdout.endswith("\n"):
        pytest.fail(repr(sub))
    try:
        event = json.loads(sub.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"--subagent printed no JSON: {sub.stdout!r}")
    expected = {"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": POINTER}}
    if event != expected or sub.stdout.count("\n") != 1:
        pytest.fail(f"--subagent printed {sub.stdout!r}")
    size = len(POINTER)
    stated = re.search(
        r"pointer line, (\d+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    if not stated or int(stated.group(1)) != size:
        pytest.fail(f"the module document states another size than {size}")
    named = re.search(rf"load the skill ({re.escape(NAMESPACE)}):([a-z0-9-]+)\.$", POINTER)
    if not named or not (PLUGIN_ROOT / "skills" / named.group(2) / "SKILL.md").is_file():
        pytest.fail("the line names no skill folder of this module")
    pass


# ---------------------------------------------------------------- the effect report (items 79 to 84)
# Each rule of the module's section "Effect" runs through the real entry `effect-report.sh` over transcripts
# made by hand and, for the history rules, a scratch git repository. The lines asserted are typed by hand.

EFFECT = SCRIPTS / "effect-report.sh"
WAY_AT = "2026-11-03T10:00:00.000Z"
SKILL_NAME = "const-catalogs:catalog-item"
TAIL = f"\n\nThis hook comes from the {NAMESPACE}@fixture-marketplace plugin."


def tr_tool(sid: str, cwd: Path, call_id: str, name: str, **given: object) -> str:
    """A tool call of any tool, with its input as given."""
    block = {"type": "tool_use", "id": call_id, "name": name, "input": given}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def tr_red(sid: str, cwd: Path, call_id: str, text: str) -> str:
    """A run of the module's hook script that blocked its call, as an attachment, with the text it printed."""
    done = {
        "type": "hook_blocking_error",
        "hookName": "PreToolUse:Write",
        "toolUseID": call_id,
        "hookEvent": "PreToolUse",
        "blockingError": {"blockingError": f"[sh /x/plugin/scripts/check-catalog-item.sh]: {text}"},
    }
    return tr_line("attachment", sid, cwd, WAY_AT, attachment=done)


def tr_refused(sid: str, cwd: Path, call_id: str, text: str) -> str:
    """The same block as Claude Code records a call a PreToolUse hook refused: only in the call's tool result,
    its command naming no script, and the plugin it comes from at the end."""
    refusal = {
        "type": "tool_result",
        "tool_use_id": call_id,
        "is_error": True,
        "content": f"PreToolUse:Write hook error: [command hook 3]: {text}{TAIL}",
    }
    return tr_line("user", sid, cwd, WAY_AT, message={"role": "user", "content": [refusal]})


def effect_lines(
    root: Path, sessions: dict[str, list[str]], env: dict[str, str] | None = None, *flags: str
) -> list[str]:
    """The lines of the report over the sessions, one transcript each; the report must exit 0."""
    folder = H.scratch_dir()
    for name, lines in sessions.items():
        (folder / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder), *flags],
        env={"CLAUDE_PLUGIN_DATA": str(H.scratch_dir()), **(env or {})},
        command=[H.sh, str(EFFECT)],
        cwd=root,
    )
    assert result.code == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def no_plugins(listed: str = "[]") -> dict[str, str]:
    """The environment of a fake `claude` that lists `listed` as its plugins."""
    return fake_claude(H.scratch_dir(), f"echo {shlex.quote(listed)}\n")


def listing(**more: object) -> dict[str, object]:
    """A patch of the dials file that lists the `itm` catalog, with the keys of the namespace `more`."""
    return {NAMESPACE: {"catalogs": [entry()], **more}}


@acceptance_item(79, "W1: a Markdown write in a catalog's territory is applied when a hook run examined it")
def test_effect_path_bypass() -> None:
    """A write examined by a run of the gate's hook is applied; a write no run examined, two shell commands
    that change an item and a write through a worktree of the project are bypassed by B1, the worktree's read
    as the path in the root. A file outside every territory, one that is no Markdown and a path outside the
    project are no moment."""
    consumer = H.fresh_consumer()
    consumer.write_dials(listing())
    root, sid = consumer.root, "s79"
    worktree = root / ".claude" / "worktrees" / "w" / "docs" / "items" / "itm-0005-w.md"
    lines = [
        tr_call(sid, root, WAY_AT, "t1", "Write", root / "docs" / "items" / "itm-0001-a.md"),
        tr_hook(sid, root, WAY_AT, "t1", "check-catalog-item.sh"),
        tr_call(sid, root, WAY_AT, "t2", "Write", root / "docs" / "items" / "itm-0002-b.md"),
        tr_tool(sid, root, "t3", "Bash", command="echo x > docs/items/itm-0003-c.md"),
        tr_tool(sid, root, "t4", "Bash", command="git mv docs/items/old.md docs/items/itm-0004-d.md"),
        tr_call(sid, root, WAY_AT, "t5", "Write", worktree),
        tr_call(sid, root, WAY_AT, "t6", "Write", root / "docs" / "elsewhere" / "e.md"),
        tr_call(sid, root, WAY_AT, "t7", "Write", root / "docs" / "items" / "f.txt"),
        tr_call(sid, root, WAY_AT, "t8", "Write", Path("/elsewhere/docs/items/g.md")),
    ]
    found = effect_lines(root, {sid: lines}, no_plugins())
    wanted = "  W1 (pattern): 6 moment(s): 1 applied, 5 bypassed, 0 missed — B1 5"
    assert wanted in found, found


@acceptance_item(80, "W2: the plugin disabled, or a dial of the gate loosened, is bypassed by B2")
def test_effect_switch_off() -> None:
    """Eight commits of the dials file, the namespace changed at each: a catalog listed (applied); a second
    catalog listed (applied); severity warn where none stood, so from the default block (bypassed); severity
    block again (applied); the first catalog's territory narrowed to another pattern (bypassed); a negated
    pattern added to it (bypassed); its width changed (applied); the second catalog unlisted (bypassed). A
    fake plugin list that lists the gate for this project disabled adds one more, bypassed. The lines are
    typed by hand."""
    consumer = H.fresh_consumer()
    root = consumer.root
    first, second = entry(), entry("note", ["docs/notes/**"])
    narrow = entry(territory=["docs/items/some/**"])
    steps = [
        {"catalogs": [first]},
        {"catalogs": [first, second]},
        {"catalogs": [first, second], "severity": "warn"},
        {"catalogs": [first, second], "severity": "block"},
        {"catalogs": [narrow, second], "severity": "block"},
        {"catalogs": [entry(territory=["docs/items/some/**", "!docs/items/some/x/**"]), second]},
        {"catalogs": [entry(territory=["docs/items/some/**", "!docs/items/some/x/**"], width=5), second]},
        {"catalogs": [entry(territory=["docs/items/some/**", "!docs/items/some/x/**"], width=5)]},
    ]
    for step in steps:
        consumer.write_dials({NAMESPACE: step})
        consumer.commit()
    found = effect_lines(root, {}, no_plugins())
    assert "  W2 (pattern): 8 moment(s): 4 applied, 4 bypassed, 0 missed — B2 4" in found, found
    disabled = json.dumps([{"id": f"{NAMESPACE}@m", "enabled": False, "projectPath": str(root)}])
    again = effect_lines(root, {}, no_plugins(disabled))
    assert "  W2 (pattern): 9 moment(s): 4 applied, 5 bypassed, 0 missed — B2 5" in again, again


@acceptance_item(
    81, "W3: after a block the next act on the file decides: a write applied, a shell command bypassed by B3"
)
def test_effect_after_red() -> None:
    """Six sessions, each a block of the hook on a write of an item, as an attachment or as the refusal of
    the call, which names no script: the next act a write of the same file (applied, in both forms); a `sed
    -i` of it and a `git mv` of it (bypassed); a write of another file and no more (bypassed); a human turn
    first (no moment). The line is typed by hand."""
    root = H.fresh_consumer().root
    doc = root / "docs" / "items" / "first.md"

    def red(sid: str, refused: bool, *after: str) -> list[str]:
        block = tr_refused if refused else tr_red
        return [tr_call(sid, root, WAY_AT, "r", "Write", doc), block(sid, root, "r", "RED: x"), *after]

    sessions = {
        "s81a": red("s81a", False, tr_call("s81a", root, WAY_AT, "n", "Write", doc)),
        "s81b": red("s81b", True, tr_call("s81b", root, WAY_AT, "n", "Write", doc)),
        "s81c": red(
            "s81c", False, tr_tool("s81c", root, "n", "Bash", command="sed -i '' s/a/b/ " + str(doc))
        ),
        "s81d": red("s81d", True, tr_tool("s81d", root, "n", "Bash", command=f"git mv {doc} itm-1.md")),
        "s81e": red("s81e", False, tr_call("s81e", root, WAY_AT, "n", "Write", doc.with_name("other.md"))),
        "s81f": red(
            "s81f",
            True,
            tr_turn("s81f", root, WAY_AT, "stop"),
            tr_call("s81f", root, WAY_AT, "n", "Write", doc),
        ),
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W3 (pattern): 5 moment(s): 2 applied, 3 bypassed, 0 missed — B3 3" in found, found


@acceptance_item(
    82, "W4: the skill a block names is loaded before the next act on the file, or the block is missed by B5"
)
def test_effect_skill_after_red() -> None:
    """A block whose text says `load the skill const-catalogs:catalog-item`, as an attachment or as a refusal:
    a Skill call naming it before the next write of the file is applied, in full or bare; a write first, or
    a Skill call for another skill, is missed; a block whose text names no skill is no moment. The line is
    typed by hand."""
    root = H.fresh_consumer().root
    doc = root / "docs" / "items" / "first.md"
    said = f"RED: x\nconst-catalogs: load the skill {SKILL_NAME} before you fix this"

    def case(sid: str, refused: bool, *after: str, text: str = said) -> list[str]:
        block = tr_refused if refused else tr_red
        return [tr_call(sid, root, WAY_AT, "r", "Write", doc), block(sid, root, "r", text), *after]

    sessions = {
        "s82a": case("s82a", False, tr_tool("s82a", root, "k", "Skill", skill=SKILL_NAME)),
        "s82b": case("s82b", True, tr_tool("s82b", root, "k", "Skill", skill="catalog-item")),
        "s82c": case("s82c", True, tr_call("s82c", root, WAY_AT, "w", "Write", doc)),
        "s82d": case("s82d", False, tr_tool("s82d", root, "k", "Skill", skill="const-catalogs:other")),
        "s82e": case("s82e", False, text="RED: x"),
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W4 (pattern): 4 moment(s): 2 applied, 0 bypassed, 2 missed — B5 2" in found, found


@acceptance_item(
    83, "W5: a skill loaded earlier makes a Write of a numbered document applied, none missed by B5"
)
def test_effect_skill_before_write() -> None:
    """A Write of a Markdown file in a catalog's territory after a Skill call for catalog-item, in full or
    bare, is applied; one with no load before it, one after a load of another skill and one whose load comes
    after the write are missed; an Edit of an item, a Write of a Markdown file outside every territory and a
    Write of a file that is no Markdown are no moment. The line is typed by hand."""
    consumer = H.fresh_consumer()
    consumer.write_dials(listing())
    root = consumer.root
    item_path = root / "docs" / "items" / "itm-0001-a.md"

    def load(sid: str, skill: str) -> str:
        return tr_tool(sid, root, "k", "Skill", skill=skill)

    def write(sid: str, path: Path = item_path, tool: str = "Write") -> str:
        return tr_call(sid, root, WAY_AT, "w", tool, path)

    sessions = {
        "s83a": [load("s83a", SKILL_NAME), write("s83a")],
        "s83b": [load("s83b", "catalog-item"), write("s83b")],
        "s83c": [write("s83c")],
        "s83d": [load("s83d", "const-catalogs:other"), write("s83d")],
        "s83e": [write("s83e"), load("s83e", SKILL_NAME)],
        "s83f": [write("s83f", tool="Edit"), write("s83f", root / "docs" / "elsewhere" / "e.md")],
        "s83g": [write("s83g", root / "docs" / "items" / "f.txt")],
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W5 (pattern): 5 moment(s): 2 applied, 0 bypassed, 3 missed — B5 3" in found, found


@acceptance_item(
    84,
    "W6: the scan on each commit of main in a throwaway clone: green applied, a refused name bypassed by B4",
)
def test_effect_escape() -> None:
    """Four commits of `main`: the fixture with no catalog listed (the scan examines nothing), the catalog
    listed with a valid item, an item whose name has not the form (the scan is red there), and that item
    renamed. The module's own scan runs on a shared clone at each, outside the project, which stays as it
    was. The line is typed by hand."""
    consumer = H.fresh_consumer()
    consumer.git("branch", "-M", "main")
    consumer.write_dials(listing())
    consumer.write(ITEM_A, item())
    consumer.commit()
    consumer.write(at("first"), item("first"))
    consumer.commit()
    consumer.git("mv", at("first"), at("itm-0002-first"))
    consumer.write(at("itm-0002-first"), item("itm-0002-first"))
    consumer.commit()
    root = consumer.root
    before = subprocess.run(
        ["git", "status", "--porcelain", "--ignored"], cwd=root, capture_output=True, text=True, check=False
    )
    found = effect_lines(root, {}, no_plugins())
    assert "  W6 (pattern): 4 moment(s): 3 applied, 1 bypassed, 0 missed — B4 1" in found, found
    after = subprocess.run(
        ["git", "status", "--porcelain", "--ignored"], cwd=root, capture_output=True, text=True, check=False
    )
    assert after.stdout == before.stdout, (before.stdout, after.stdout)


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
    skill="catalog-item",  # the skill a red names (F10), typed by hand
    effect="effect-report.sh",  # no `effect_reader`: the module has no reader rule
)
