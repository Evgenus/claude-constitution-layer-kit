#!/usr/bin/env python3
"""Fixtures of const-referencing: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one. Its three policies matter here only as documents
that carry ids: this gate resolves no policy, and covers every Markdown file by default, so
the shared items about the root policy are not its own and are left out; their numbers
stay free.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.model import Broken, Finding  # noqa: E402
from consumer import Consumer, document  # noqa: E402
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
from referencing_gate import messages, start  # noqa: E402
from shared_items import Subject, shared_assertions  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-references.sh", "check-references.py", start.GATE.namespace)

NAMESPACE = start.GATE.namespace
DOC = "docs/notes/a.md"
OWNER_ID = "notes-policy"  # a document of the shared consumer, carrying this id
OWNER = "docs/policies/notes-policy.md"
TO_OWNER = "../policies/notes-policy.md"
LANE = {
    "pattern": r"\bREQ-[0-9]+\b",
    "names": "a requirement",
    "fix": "[REQ-7](<path to>/docs/reqs.md#req-7)",
    "home": ["docs/reqs.md"],
}


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps it working."""
    return {NAMESPACE: dict(dials)}


def claim(territory: Sequence[str]) -> dict[str, object]:
    return own(territories=list(territory))


LANES = own(lanes=[LANE])


def dials_text(patch: dict[str, object] | None = None) -> str:
    return yaml.safe_dump({**Consumer(Path()).dials, **(patch or {})}, sort_keys=False)


def note(body: str, doc_id: str = "note-a") -> str:
    return document(body, id=doc_id, type="non-authoritative", title="Fixture", status="active")


def wrote(body: str, target: str = DOC) -> Write:
    return Write(target, note(body))


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


def passes(body: str, patch: dict[str, object] | None = LANES, target: str = DOC) -> tuple[bool, str]:
    return expect(gate_on(wrote(body, target), dials_patch=patch)[0], 0, messages.g1_covered(), "stdout")


def blocks(body: str, finding: Finding, patch: dict[str, object] | None = LANES) -> tuple[bool, str]:
    return expect(gate_on(wrote(body), dials_patch=patch)[0], 2, finding.render(), "stderr")


# ------------------------------------------------------------------ the findings, as the gate builds them

LINE = 9  # the line after the heading in `note`: six lines of envelope, a blank one, the heading


def r1(match: str = "REQ-7", line: int = LINE) -> Finding:
    return messages.r1_bare_form(DOC, line, match, str(LANE["names"]), str(LANE["fix"]))


R2 = messages.r2_bare_id(DOC, LINE, OWNER_ID, OWNER, TO_OWNER)
R3 = messages.r3_id_link_astray(DOC, LINE, OWNER_ID, "../policies/root-policy.md", OWNER, TO_OWNER)
R4_PATH = messages.r4_one_machine(DOC, LINE, "/Users/someone/notes.md")
R4_FILE = messages.r4_one_machine(DOC, LINE, "file:///srv/notes.md")

SETUP = (Write("constitution.yaml", dials_text(LANES)),)
LINKED = f"See [{OWNER_ID}]({TO_OWNER}) and [REQ-7](../policies/root-policy.md).\n"
VALID = wrote("# Fixture\n" + LINKED)


def body(line: str) -> str:
    return "# Fixture\n" + line + "\n"


# ------------------------------------------------------------------ red → green cases

CASES = [
    Case(
        1,
        "R1: a lane's bare form is blocked; the same handle as a link's text passes",
        wrote(body("See REQ-7.")),
        VALID,
        r1(),
        SETUP,
    ),
    Case(
        2,
        "R2: a covered document's id in backticks is blocked; the id as a link passes",
        wrote(body(f"See `{OWNER_ID}`.")),
        VALID,
        R2,
        SETUP,
    ),
    Case(
        3,
        "R3: a link showing one document's id and opening another is blocked",
        wrote(body(f"See [{OWNER_ID}](../policies/root-policy.md).")),
        VALID,
        R3,
        SETUP,
    ),
    Case(
        4,
        "R4: a path under a home directory is blocked",
        wrote(body("Notes: /Users/someone/notes.md")),
        VALID,
        R4_PATH,
        SETUP,
    ),
    Case(
        5,
        "R4: a file: link is blocked",
        wrote(body("Notes: [n](file:///srv/notes.md)")),
        VALID,
        R4_FILE,
        SETUP,
    ),
]

# ------------------------------------------------------------------ assertions


def masked_regions() -> tuple[bool, str]:
    """Every region no check reads, each holding all four forms."""
    forms = f"REQ-7 `{OWNER_ID}` /Users/someone/x.md"
    bodies = {
        "a fence": f"# F\n\n```text\n{forms}\n```\n",
        "a tilde fence left open": f"# F\n\n~~~\n{forms}\n",
        "an indented block": f"# F\n\npara\n\n    {forms}\n",
        "a comment": f"# F\n\n<!-- {forms} -->\n",
        "a code span": "# F\n\nThe form ``REQ-7`` and `/Users/someone/x.md` are shown, not used.\n",
        "a link's text": "# F\n\n[REQ-7](../reqs.md#req-7)\n",
    }
    return all_of(
        [passes(text) for text in bodies.values()], f"{len(bodies)} masked regions pass: {', '.join(bodies)}"
    )


def envelope_is_masked() -> tuple[bool, str]:
    text = document("# F\n", id="note-a", type="non-authoritative", title="About REQ-7", status="active")
    return expect(gate_on(Write(DOC, text), dials_patch=LANES)[0], 0, messages.g1_covered(), "stdout")


def list_continuation_is_no_code() -> tuple[bool, str]:
    return blocks("# F\n\n- item\n\n    continued: REQ-7\n", r1(line=12))


def lane_is_silent_at_home() -> tuple[bool, str]:
    return all_of(
        [passes(body("REQ-7 is defined here."), target="docs/reqs.md"), blocks(body("See REQ-7."), r1())],
        "silent in docs/reqs.md, red elsewhere",
    )


def no_lanes_no_bare_forms() -> tuple[bool, str]:
    return passes(body("See REQ-7."), patch=None)


def bare_ids_allowed() -> tuple[bool, str]:
    return all_of(
        [
            passes(body(f"See `{OWNER_ID}`."), patch=own(bare_ids="allow")),
            blocks(body(f"See `{OWNER_ID}`."), R2, patch=None),
        ],
        "allow passes, the default blocks",
    )


def own_id_and_unknown_ids_pass() -> tuple[bool, str]:
    return passes(body("This is `note-a`; `not-a-document` is no id of a covered document."))


def id_links_that_pass() -> tuple[bool, str]:
    lines = [
        f"[`{OWNER_ID}`]({TO_OWNER}#rules) with ticks and a fragment",
        "[note-a](#top) a fragment alone opens this document",
        f"[{OWNER_ID}](https://example.invalid/x) an address with a scheme is not judged",
        f"[{OWNER_ID}](<{TO_OWNER}>) in angle brackets",
    ]
    return passes("# F\n\n" + "\n".join(lines) + "\n")


def ticks_in_link_text_are_judged() -> tuple[bool, str]:
    finding = messages.r3_id_link_astray(DOC, LINE, OWNER_ID, "b.md", OWNER, TO_OWNER)
    return blocks(body(f"See [`{OWNER_ID}`](b.md)."), finding)


def pending_document_carries_its_id() -> tuple[bool, str]:
    """The id of the document being written is known before the file exists."""
    other = messages.r2_bare_id("docs/notes/b.md", LINE, "note-a", DOC, "a.md")
    result, _ = gate_on(
        Write("docs/notes/b.md", note(body("See `note-a`."), "note-b")), files={DOC: note("# F\n")}
    )
    return expect(result, 2, other.render(), "stderr")


def edit_is_judged_as_written() -> tuple[bool, str]:
    files = {DOC: VALID.text}
    red, _ = gate_on(
        Edit(DOC, "and [REQ-7](../policies/root-policy.md)", "and REQ-7"), dials_patch=LANES, files=files
    )
    green, _ = gate_on(Edit(DOC, "# Fixture", "# Renamed"), dials_patch=LANES, files=files)
    finding = messages.r1_bare_form(DOC, LINE, "REQ-7", str(LANE["names"]), str(LANE["fix"]))
    return all_of(
        [expect(red, 2, finding.headline, "stderr"), expect(green, 0, messages.g1_covered(), "stdout")],
        "an Edit that bares a handle is blocked, another passes",
    )


def findings_in_reading_order() -> tuple[bool, str]:
    result, _ = gate_on(wrote(f"# F\n/Users/someone/x.md then `{OWNER_ID}`\nthen REQ-7\n"), dials_patch=LANES)
    keys = [
        line.split(":")[2].strip()[:12] for line in result.stderr.splitlines() if line.startswith("RED: docs")
    ]
    order = [result.stderr.index(text) for text in ("/Users/someone", f"id '{OWNER_ID}'", "'REQ-7'")]
    ok = result.code == 2 and order == sorted(order) and "3 finding(s)" in result.stderr
    return ok, "three findings, by position" if ok else f"exit {result.code}, {keys}: {result.stderr}"


def not_covered() -> tuple[bool, str]:
    result, _ = gate_on(
        wrote(body("See REQ-7.")),
        dials_patch={NAMESPACE: {"lanes": [LANE], "territories": ["docs/policies/**"]}},
    )
    return expect(result, 0, shared.g1_green_skip(messages.g1_skip_not_covered(DOC)), "stdout")


def scan_reports_all() -> tuple[bool, str]:
    files = {DOC: note(body("See REQ-7.")), "docs/notes/b.md": note(body(f"See `{OWNER_ID}`."), "note-b")}
    red = scan_of(files, LANES)
    second = messages.r2_bare_id("docs/notes/b.md", LINE, OWNER_ID, OWNER, "../policies/notes-policy.md")
    tail = messages.f9_scan_tail(5, 0, 5, 1, 0, 0)
    green = scan_of({DOC: VALID.text}, LANES)
    return all_of(
        [
            expect(red, 2, r1().render(), "stdout"),
            expect(red, 2, second.render(), "stdout"),
            expect(red, 2, shared.f9_count_scan(2, tail), "stdout"),
            expect(green, 0, shared.g1_green_scan(messages.f9_scan_tail(4, 2, 4, 1, 0, 0)), "stdout"),
        ],
        "two documents red with the count tail; green names documents, links and lanes",
    )


def scan_ignores_severity() -> tuple[bool, str]:
    patch = own(lanes=[LANE], severity="warn")
    return expect(scan_of({DOC: note(body("See REQ-7."))}, patch), 2, r1().headline, "stdout")


def dial_failures() -> tuple[bool, str]:
    def lane(**changes: object) -> dict[str, object]:
        return own(lanes=[{**LANE, **changes}])

    dropped = {key: value for key, value in LANE.items() if key != "fix"}
    wrong: list[tuple[dict[str, object], Broken]] = [
        (own(territories="*.md"), messages.c5_territories()),
        (own(territories=[]), messages.c5_territories()),
        (own(territories=["*.md", 3]), messages.c5_territories()),
        (own(bare_ids="maybe"), messages.c5_switch("bare_ids")),
        (own(bare_ids=True), messages.c5_switch("bare_ids")),
        (own(lanes={"pattern": "x"}), messages.c5_lanes_not_a_list()),
        (own(lanes=["REQ"]), messages.c5_lane(1, messages.lane_not_a_mapping())),
        (own(lanes=[LANE, {**LANE, "why": "mine"}]), messages.c5_lane(2, messages.lane_unknown_key("why"))),
        (own(lanes=[dropped]), messages.c5_lane(1, messages.lane_needs("fix"))),
        (lane(names="  "), messages.c5_lane(1, messages.lane_needs("names"))),
        (lane(pattern=7), messages.c5_lane(1, messages.lane_needs("pattern"))),
        (lane(home="docs/reqs.md"), messages.c5_lane(1, messages.lane_home())),
        (
            lane(pattern="REQ-(["),
            messages.c5_lane(1, messages.lane_pattern("unterminated character set at position 5")),
        ),
    ]
    results = [broken(gate_on(VALID, dials_patch=patch)[0], failure) for patch, failure in wrong]
    in_scan = H.run_gate("", args=["--scan", str(gate_on(VALID, dials_patch=own(bare_ids="maybe"))[1])])
    return all_of(
        [*results, broken(in_scan, messages.c5_switch("bare_ids"))],
        f"{len(wrong)} malformed dials, each exit 1, and one in the scan",
    )


def lane_home_pattern_git_would_misread() -> tuple[bool, str]:
    result, _ = gate_on(VALID, dials_patch=own(lanes=[{**LANE, "home": ["#docs"]}]))
    return broken(result, shared.c5_territory_pattern(f"{NAMESPACE}.lanes[1].home", "#docs"))


def unreadable_envelope_is_no_crash() -> tuple[bool, str]:
    """Brackets nested past the parser's depth: the document carries no id here, and the write is
    judged on its references all the same."""
    text = "---\nid: " + "[" * 600 + "\n---\n"
    green, _ = gate_on(Write(DOC, text + "# F\n"), dials_patch=LANES)
    red, _ = gate_on(Write(DOC, text + "# F\nSee REQ-7.\n"), dials_patch=LANES)
    finding = messages.r1_bare_form(DOC, 5, "REQ-7", str(LANE["names"]), str(LANE["fix"]))
    return all_of(
        [expect(green, 0, messages.g1_covered(), "stdout"), expect(red, 2, finding.render(), "stderr")],
        "green without a reference, red on a bare form after it",
    )


GOLDEN = {
    "R1": f"RED: {DOC}:9: 'REQ-7' cites a requirement by a bare handle",
    "R1 why": "  why: a bare handle resolves only inside its home document: elsewhere no reader can"
    " follow it, no check can test it, and a move cannot find it",
    "R1 fix": "  fix: write it as a link: [REQ-7](<path to>/docs/reqs.md#req-7)",
    "R2": f"RED: {DOC}:9: document id 'notes-policy' stands in backticks and is no link",
    "R2 fix": "  fix: write [notes-policy](../policies/notes-policy.md) — the path from this document to"
    " docs/policies/notes-policy.md",
    "R3": f"RED: {DOC}:9: the link's text is document id 'notes-policy', and its target"
    " ../policies/root-policy.md is not that document (docs/policies/notes-policy.md)",
    "R3 fix": "  fix: point it at ../policies/notes-policy.md",
    "R4": f"RED: {DOC}:9: '/Users/someone/notes.md' is a path on one machine",
    "R4 fix": "  fix: link a file of this repository by its relative path, or cite the public address",
}


def golden_lines() -> tuple[bool, str]:
    """The texts as literals, typed here by hand: the cases above compare with what the message
    functions return, so a slip inside a function would pass them all."""
    runs = {str(case.expect.key): gate_on(case.red, dials_patch=LANES)[0].stderr for case in CASES[:4]}
    missing = [key for key, line in GOLDEN.items() if line not in runs[key.split()[0]]]
    skip = gate_on(wrote("# F\n"), dials_patch=claim(["docs/policies/**"]))[0].stdout
    if f"{DOC} is not covered (const-referencing.territories)" not in skip:
        missing.append("skip")
    return not missing, f"{len(GOLDEN) + 1} literal lines found" if not missing else f"not found: {missing}"


# ------------------------------------------------------------------ the whole tree, in the scan

TARGET = "docs/notes/t.md"
SOURCE = "docs/notes/s.md"
TARGET_TEXT = note('# Target\n\n<a id="k1"></a>\n## First Section\n\n## Second {#custom}\n', "note-t")


def source(line: str) -> str:
    return note(body(line), "note-s")


def tree_scan(
    line: str, patch: dict[str, object] | None = None, more: dict[str, str] | None = None
) -> Result:
    return scan_of({TARGET: TARGET_TEXT, SOURCE: source(line), **(more or {})}, patch)


def red_green(red: Result, finding: Finding, green: Result) -> tuple[bool, str]:
    return all_of(
        [expect(red, 2, finding.render(), "stdout"), expect(green, 0, "GREEN: ", "stdout")],
        f"red → {finding.key}: {finding.headline}; green after the fix",
    )


def broken_reference() -> tuple[bool, str]:
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    return red_green(tree_scan("See [x](gone.md)."), finding, tree_scan("See [x](t.md)."))


def moved_anchor() -> tuple[bool, str]:
    """The anchor a link cites is taken out of the target: red; put back: green."""
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#k1", "k1", TARGET, None)
    moved = {TARGET: TARGET_TEXT.replace('<a id="k1"></a>\n', ""), SOURCE: source("See [x](t.md#k1).")}
    return red_green(scan_of(moved), finding, tree_scan("See [x](t.md#k1)."))


def heading_anchors() -> tuple[bool, str]:
    by_name = messages.r7_heading_anchor(SOURCE, LINE, "t.md#first-section", TARGET)
    by_key = messages.r7_heading_anchor(SOURCE, LINE, "t.md#custom", TARGET)
    own_heading = messages.r7_heading_anchor(SOURCE, LINE, "#fixture", SOURCE)
    allowed = own(heading_anchors="allow")
    return all_of(
        [
            red_green(tree_scan("See [x](t.md#first-section)."), by_name, tree_scan("See [x](t.md#k1).")),
            expect(tree_scan("See [x](t.md#custom)."), 2, by_key.render(), "stdout"),
            expect(tree_scan("See [x](#fixture)."), 2, own_heading.render(), "stdout"),
            expect(
                tree_scan("See [x](t.md#first-section) and [y](t.md#custom).", allowed),
                0,
                "GREEN: ",
                "stdout",
            ),
        ],
        "a generated name, a {#key} and the own heading are red; an explicit anchor and allow pass",
    )


def anchor_shown_in_code_is_none() -> tuple[bool, str]:
    """An anchor inside a fence is an example: the link beside it still goes through the heading."""
    shown = note('# Target\n\n## Shown\n\n```html\n<a id="shown"></a>\n```\n', "note-t")
    finding = messages.r7_heading_anchor(SOURCE, LINE, "t.md#shown", TARGET)
    return expect(
        scan_of({TARGET: shown, SOURCE: source("See [x](t.md#shown).")}), 2, finding.render(), "stdout"
    )


def anchor_case_counts() -> tuple[bool, str]:
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#K1", "K1", TARGET, "k1")
    allowed = tree_scan("See [x](t.md#K1).", own(heading_anchors="allow"))
    return all_of(
        [
            expect(tree_scan("See [x](t.md#K1)."), 2, finding.render(), "stdout"),
            expect(allowed, 2, finding.headline, "stdout"),
        ],
        "the link checker passes it, a forge does not: red, and not switched off by heading_anchors",
    )


def uncovered_targets() -> tuple[bool, str]:
    """Coverage decides whose links are judged: a link into an uncovered file must resolve, and
    which kind of anchor resolved it there is not this gate's to say."""
    only_source = own(territories=["*.md", "!" + TARGET])
    gone = messages.r5_no_target(SOURCE, LINE, "gone.md")
    return all_of(
        [
            expect(
                tree_scan("See [x](t.md#first-section).", only_source),
                0,
                "4 document(s) and 1 link(s) examined, 5 Markdown",
                "stdout",
            ),
            expect(tree_scan("See [x](gone.md).", only_source), 2, gone.render(), "stdout"),
        ],
        "a heading link into an uncovered target passes; a missing target is red all the same",
    )


def owned_invocation() -> tuple[bool, str]:
    """Files by which a repository steers its own lychee change nothing here."""
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    stray = {"lychee.toml": 'exclude_path = ["docs"]\n', ".lycheeignore": "gone.md\n"}
    steered = tree_scan("See [x](gone.md).", more=stray)
    return expect(steered, 2, finding.render(), "stdout")


def links_in_code_are_not_checked() -> tuple[bool, str]:
    return expect(tree_scan("Shown: `[x](gone.md)`.\n\n```md\n[y](gone.md#a)\n```"), 0, "GREEN: ", "stdout")


def path_with(lychee_script: str | None) -> dict[str, str]:
    """A PATH holding python3, git and dirname, and the given script as lychee — or none at all."""
    directory = H.scratch_dir()
    for tool in ("python3", "git", "dirname"):
        found = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert found, tool
        os.symlink(found, directory / tool)
    if lychee_script is not None:
        (directory / "lychee").write_text("#!/bin/sh\n" + lychee_script)
        (directory / "lychee").chmod(0o755)
    return {"PATH": str(directory)}


def scan_with(env: dict[str, str]) -> Result:
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    return H.run_gate("", args=["--scan", str(consumer.root)], env=env)


def link_checker_absent() -> tuple[bool, str]:
    return broken(scan_with(path_with(None)), messages.x1_no_lychee("0.24.2"))


def link_checker_unusable() -> tuple[bool, str]:
    usage = (
        'case "$1" in --version) echo "lychee 0.24.2";;'
        ' *) echo "error: unexpected argument" >&2; exit 2;; esac\n'
    )
    return all_of(
        [
            broken(
                scan_with(path_with('echo "lychee 0.23.0"\n')),
                messages.x2_lychee_too_old("0.24.2", "lychee 0.23.0"),
            ),
            broken(scan_with(path_with("exit 0\n")), messages.x2_lychee_too_old("0.24.2", "")),
            broken(
                scan_with(path_with(usage)), messages.x3_no_report("exit 2", "error: unexpected argument")
            ),
        ],
        "below the floor, a version nobody can read, and exit 2 with no report: each exit 1, never a finding",
    )


# ------------------------------------------------------------------ coverage, and names outside Markdown

MENTION = {"pattern": r"\bnote-[a-z]+\b"}
LOOSE = "docs/loose/l.md"  # no policy of the shared consumer governs docs/loose/


def governed_only() -> tuple[bool, str]:
    """Under governed_only a document no policy governs is not covered."""
    files = {LOOSE: note(body("See [x](gone.md)."), "note-l"), SOURCE: source("See [x](gone.md).")}
    only = own(governed_only=True)
    governed = scan_of(files, only)
    loose_write = gate_on(Write(LOOSE, note(body(f"See `{OWNER_ID}`."), "note-l")), only)[0]
    skipped = shared.g1_green_skip(messages.g1_skip_not_covered(LOOSE))
    return all_of(
        [
            expect(governed, 2, messages.r5_no_target(SOURCE, LINE, "gone.md").headline, "stdout"),
            expect(governed, 2, "1 finding(s)", "stdout"),
            expect(scan_of(files), 2, "2 finding(s)", "stdout"),
            expect(loose_write, 0, skipped, "stdout"),
            expect(gate_on(wrote(body(f"See `{OWNER_ID}`.")), only)[0], 2, R2.render(), "stderr"),
        ],
        "the ungoverned document is left out of the scan and skipped at the write; the governed is judged",
    )


def governed_only_without_root() -> tuple[bool, str]:
    result, _ = gate_on(VALID, raw_dials=yaml.safe_dump({NAMESPACE: {"governed_only": True}}))
    default, _ = gate_on(VALID, raw_dials="{}\n")
    return all_of(
        [
            expect(result, 0, shared.g1_green_skip(shared.g1_skip_no_root()), "stdout"),
            expect(default, 0, messages.g1_covered(), "stdout"),
        ],
        "governed_only with no root policy is the shared visible skip; by default none is needed",
    )


def mentions_outside_markdown() -> tuple[bool, str]:
    files = {
        SOURCE: source("x"),
        "tools/check.sh": "# see note-s and note-gone\necho note-s\n",
        "tools/blob.bin": "note-zz\0",
    }
    finding = messages.r8_unknown_mention("tools/check.sh", 1, "note-gone")
    red = scan_of(files, own(mentions=[MENTION]))
    fixed = scan_of({**files, "tools/check.sh": "# see note-s\n"}, own(mentions=[MENTION]))
    elsewhere = scan_of(files, own(mentions=[{**MENTION, "files": ["src/**"]}]))
    return all_of(
        [
            expect(red, 2, finding.render(), "stdout"),
            expect(red, 2, "1 finding(s)", "stdout"),
            expect(fixed, 0, "1 mention pattern(s) over ", "stdout"),
            expect(scan_of(files), 0, "GREEN: ", "stdout"),
            expect(elsewhere, 0, "GREEN: ", "stdout"),
        ],
        "an unknown name is red, a known one and a binary file pass; off by default; files narrows it",
    )


def mention_dial_failures() -> tuple[bool, str]:
    unclosed = messages.lane_pattern("missing ), unterminated subpattern at position 5")
    wrong: list[tuple[dict[str, object], Broken]] = [
        (own(governed_only="yes"), messages.c5_governed_only()),
        (own(heading_anchors="sometimes"), messages.c5_switch("heading_anchors")),
        (own(mentions={"pattern": "x"}), messages.c5_mentions_not_a_list()),
        (own(mentions=["note"]), messages.c5_mention(1, messages.mention_not_a_mapping())),
        (
            own(mentions=[{**MENTION, "names": "x"}]),
            messages.c5_mention(1, messages.mention_unknown_key("names")),
        ),
        (own(mentions=[{"files": ["src/**"]}]), messages.c5_mention(1, messages.lane_needs("pattern"))),
        (own(mentions=[{**MENTION, "files": "src"}]), messages.c5_mention(1, messages.mention_files())),
        (own(mentions=[{"pattern": "note-("}]), messages.c5_mention(1, unclosed)),
    ]
    results = [broken(gate_on(VALID, dials_patch=patch)[0], failure) for patch, failure in wrong]
    return all_of(results, f"{len(wrong)} malformed dials, each exit 1")


# ------------------------------------------------------------------ after the write

AFTER = "PostToolUse"


def after_write(
    written: str, files: dict[str, str], patch: dict[str, object] | None = None, event: str = AFTER
) -> Result:
    """The files are on disk, `written` among them, and the event says it was just written."""
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text(patch))
    for rel, text in files.items():
        consumer.write(rel, text)
    return H.run_gate(event_json(consumer.root, Write(written, files[written]), event=event))


def after_count(rel: str, links: int, findings: int, cut: int | None = None) -> str:
    return "RED: " + messages.f9_after_write(rel, links, findings, cut)


def own_links_after_write() -> tuple[bool, str]:
    files = {TARGET: TARGET_TEXT, SOURCE: source("See [x](gone.md).")}
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    fixed = {TARGET: TARGET_TEXT, SOURCE: source("See [x](t.md#k1).")}
    return all_of(
        [
            expect(after_write(SOURCE, files), 2, finding.render(), "stderr"),
            expect(after_write(SOURCE, files), 2, after_count(SOURCE, 1, 1), "stderr"),
            expect(after_write(SOURCE, fixed), 0, messages.g1_covered(), "stdout"),
        ],
        "the written document's broken link is reported on stderr with exit 2; repaired, green",
    )


def inbound_break_after_write() -> tuple[bool, str]:
    """The target is written without the anchor another document cites: the break is in the
    other file, and it is reported in the turn that causes it."""
    files = {TARGET: TARGET_TEXT.replace('<a id="k1"></a>\n', ""), SOURCE: source("See [x](t.md#k1).")}
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#k1", "k1", TARGET, None)
    return expect(after_write(TARGET, files), 2, finding.render(), "stderr")


def older_break_elsewhere_is_not_repeated() -> tuple[bool, str]:
    files = {
        TARGET: TARGET_TEXT,
        SOURCE: source("See [x](gone.md)."),
        "docs/notes/u.md": note("# U\n", "note-u"),
    }
    return all_of(
        [
            expect(after_write("docs/notes/u.md", files), 0, messages.g1_covered(), "stdout"),
            expect(scan_of(files), 2, messages.r5_no_target(SOURCE, LINE, "gone.md").headline, "stdout"),
        ],
        "a write that touches neither end of an older break is green; the scan still reports it",
    )


def heading_anchor_after_write() -> tuple[bool, str]:
    files = {TARGET: TARGET_TEXT, SOURCE: source("See [x](t.md#first-section).")}
    finding = messages.r7_heading_anchor(SOURCE, LINE, "t.md#first-section", TARGET)
    return expect(after_write(SOURCE, files), 2, finding.render(), "stderr")


def warn_after_write() -> tuple[bool, str]:
    files = {TARGET: TARGET_TEXT, SOURCE: source("See [x](gone.md).")}
    result = after_write(SOURCE, files, own(severity="warn"))
    try:
        loaded = json.loads(result.stdout)
    except ValueError:
        return False, f"stdout is not one JSON object: {result.stdout!r}"
    specific = loaded.get("hookSpecificOutput", {})
    ok = (
        result.code == 0
        and result.stderr == ""
        and specific.get("hookEventName") == AFTER
        and messages.r5_no_target(SOURCE, LINE, "gone.md").render() in specific.get("additionalContext", "")
        and after_count(SOURCE, 1, 1) in specific.get("additionalContext", "")
    )
    return ok, "exit 0, one JSON object naming PostToolUse, the finding and the count inside" if ok else str(
        result
    )


def lint_is_not_run_after_write() -> tuple[bool, str]:
    """A bare form is the pre-write handler's to block; after the write only the tree is read."""
    files = {SOURCE: source("See REQ-7.")}
    before = H.run_gate(event_json(H.fresh_consumer(SETUP).root, Write(SOURCE, files[SOURCE])))
    return all_of(
        [
            expect(after_write(SOURCE, files, LANES), 0, messages.g1_covered(), "stdout"),
            expect(before, 2, "REQ-7", "stderr"),
        ],
        "green after the write, blocked before it",
    )


def many_findings_are_cut() -> tuple[bool, str]:
    lines = " ".join(f"[x{n}](gone-{n}.md)" for n in range(25))
    result = after_write(SOURCE, {SOURCE: source(lines)})
    ok = (
        result.code == 2
        and result.stderr.count("RED: docs/") == 20
        and after_count(SOURCE, 25, 25, 20) in result.stderr
    )
    return ok, "25 findings, 20 printed, the count line says both" if ok else result.stderr[-400:]


def file_gone_after_write() -> tuple[bool, str]:
    consumer = H.fresh_consumer()
    result = H.run_gate(event_json(consumer.root, Write(SOURCE, source("x")), event=AFTER))
    return expect(result, 0, shared.g1_green_skip(shared.g1_skip_gone(SOURCE)), "stdout")


def unknown_event() -> tuple[bool, str]:
    files = {SOURCE: source("See [x](gone.md).")}
    return broken(after_write(SOURCE, files, event="Notification"), messages.c12_event("Notification"))


def lychee_absent_after_write() -> tuple[bool, str]:
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    event = event_json(consumer.root, Write(SOURCE, source("See [x](gone.md).")), event=AFTER)
    return broken(H.run_gate(event, env=path_with(None)), messages.x1_no_lychee("0.24.2"))


GOLDEN_TREE = {
    "R5": f"RED: {SOURCE}:9: link target gone.md does not exist",
    "R5 fix": "  fix: correct the path; if the target was deleted, remove the link and state here what it"
    " was cited for",
    "R6": f"RED: {SOURCE}:9: t.md#nope has no anchor 'nope'",
    "R6 fix": f'  fix: cite an anchor the target carries, or add <a id="nope"></a> on its own line before the'
    f" cited place in {TARGET}",
    "R6 case": f"RED: {SOURCE}:9: t.md#K1 has no anchor 'K1' (it has 'k1': an anchor's case counts)",
    "R6 case fix": "  fix: cite 'k1' as it is written",
    "R7": f"RED: {SOURCE}:9: t.md#first-section resolves only through a heading — its generated name, or a"
    f" {{#key}} written after it — not through an anchor written in {TARGET}",
    "R7 fix": '  fix: add <a id="<short fixed key>"></a> on its own line before that heading in'
    f" {TARGET} and cite the key; a repository whose links go through headings sets const-referencing:"
    " {heading_anchors: allow} in constitution.yaml until they are converted",
}


def golden_tree_lines() -> tuple[bool, str]:
    out = tree_scan("See [a](gone.md), [b](t.md#nope), [c](t.md#K1) and [d](t.md#first-section).").stdout
    missing = [key for key, line in GOLDEN_TREE.items() if line not in out]
    absent = scan_with(path_with(None)).stderr
    x1 = (
        "BROKEN: const-referencing needs lychee 0.24.2 or newer and found none on PATH — fix: install it"
        " (https://lychee.cli.rs/installation/), then run the scan"
    )
    if x1 not in absent:
        missing.append("X1")
    return (
        not missing,
        f"{len(GOLDEN_TREE) + 1} literal lines found" if not missing else f"not found: {missing}",
    )


ASSERTIONS = [
    Assertion(
        10,
        "masked: a fence, an open fence, an indented block, a comment, a code span, a link's text",
        masked_regions,
    ),
    Assertion(11, "masked: the YAML block that opens the file", envelope_is_masked),
    Assertion(
        12,
        "an indented paragraph continuing a list item is no code: a bare form there is red",
        list_continuation_is_no_code,
    ),
    Assertion(13, "a lane is silent in its home documents", lane_is_silent_at_home),
    Assertion(14, "with no lane declared no bare form is known", no_lanes_no_bare_forms),
    Assertion(15, "bare_ids: allow switches R2 off", bare_ids_allowed),
    Assertion(
        16,
        "the document's own id, and a name no covered document carries, pass in backticks",
        own_id_and_unknown_ids_pass,
    ),
    Assertion(
        17,
        "R3 passes: ticks and a fragment, a fragment alone, an address with a scheme, angle brackets",
        id_links_that_pass,
    ),
    Assertion(18, "R3 judges an id written in ticks inside the link's text", ticks_in_link_text_are_judged),
    Assertion(
        19,
        "the id of a document that exists is known to the write of another",
        pending_document_carries_its_id,
    ),
    Assertion(20, "an Edit is judged on the document it produces", edit_is_judged_as_written),
    Assertion(21, "several findings come in reading order, with their count", findings_in_reading_order),
    Assertion(22, "a document outside const-referencing.territories is a visible skip", not_covered),
    Assertion(
        23, "the scan reports every document, names documents, links and lanes in its tail", scan_reports_all
    ),
    Assertion(24, "the scan ignores severity", scan_ignores_severity),
    Assertion(25, "this module's dial failures are exit 1, never 2, never 0", dial_failures),
    Assertion(
        26,
        "a lane's home pattern git would misread is the shared configuration failure",
        lane_home_pattern_git_would_misread,
    ),
    Assertion(
        28,
        "an envelope nobody can read is no crash and no finding: references are still judged",
        unreadable_envelope_is_no_crash,
    ),
    Assertion(
        27, "golden lines: the taught texts as literals, not as the functions return them", golden_lines
    ),
    Assertion(
        30, "R5, the specification's first: a broken reference is red, repaired it is green", broken_reference
    ),
    Assertion(
        31, "R6, the specification's second: a moved anchor is red, put back it is green", moved_anchor
    ),
    Assertion(
        32, "R7: a generated name, a {#key}, the own heading; an explicit anchor; allow", heading_anchors
    ),
    Assertion(
        33, "R6: an anchor cited in another case is red, whatever heading_anchors says", anchor_case_counts
    ),
    Assertion(34, "coverage decides whose links are judged, not which targets must exist", uncovered_targets),
    Assertion(35, "a lychee.toml and a .lycheeignore in the repository change nothing", owned_invocation),
    Assertion(36, "links inside code are not checked", links_in_code_are_not_checked),
    Assertion(
        37,
        "absence: no lychee on PATH is a configuration failure with the install address",
        link_checker_absent,
    ),
    Assertion(
        38,
        "a lychee below the floor, one with no version, one that exits 2 with no report",
        link_checker_unusable,
    ),
    Assertion(39, "golden lines of the whole-tree findings, typed by hand", golden_tree_lines),
    Assertion(40, "an anchor shown inside code is no anchor", anchor_shown_in_code_is_none),
    Assertion(
        50,
        "after the write: the written document's own broken link, exit 2 on stderr; repaired, green",
        own_links_after_write,
    ),
    Assertion(
        51,
        "after the write: a break the write causes in another document is reported",
        inbound_break_after_write,
    ),
    Assertion(
        52,
        "after the write: an older break elsewhere is not repeated; the scan reports it",
        older_break_elsewhere_is_not_repeated,
    ),
    Assertion(53, "after the write: a heading-derived anchor is reported", heading_anchor_after_write),
    Assertion(54, "after the write, severity warn: one JSON object naming the event", warn_after_write),
    Assertion(55, "the lint is the pre-write handler's alone", lint_is_not_run_after_write),
    Assertion(56, "after the write: findings past the cap are counted, not printed", many_findings_are_cut),
    Assertion(57, "after the write: a file that is not there is a visible skip", file_gone_after_write),
    Assertion(58, "an event the gate is not wired to is a configuration failure", unknown_event),
    Assertion(
        59, "absence after the write: no lychee is exit 1 with the install address", lychee_absent_after_write
    ),
    Assertion(41, "governed_only: a document no policy governs is not covered", governed_only),
    Assertion(42, "governed_only needs a root policy; the default needs none", governed_only_without_root),
    Assertion(
        43,
        "R8: a name outside Markdown no covered document carries; off by default",
        mentions_outside_markdown,
    ),
    Assertion(
        44,
        "the dial failures of governed_only, heading_anchors and mentions are exit 1",
        mention_dial_failures,
    ),
]

SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=wrote(body(f"See `{OWNER_ID}`.")),
    red_finding=R2,
    green=messages.g1_covered(),
    territory=["*.md"],
    claim=claim,
    resolves_policies=False,
    bare_readme="1 document examined",
    judges_envelopes=False,
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
