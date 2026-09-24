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
import re
import shutil
import subprocess
import sys
import time
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
from referencing_gate.dials import KEYS  # noqa: E402
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

GREEN_WHAT = "a covered document"  # what every green half's line says its document is, typed by hand

CASES = [
    Case(
        1,
        "R1: a lane's bare form is blocked; the same handle as a link's text passes",
        wrote(body("See REQ-7.")),
        VALID,
        r1(),
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        2,
        "R2: a covered document's id in backticks is blocked; the id as a link passes",
        wrote(body(f"See `{OWNER_ID}`.")),
        VALID,
        R2,
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        3,
        "R3: a link showing one document's id and opening another is blocked",
        wrote(body(f"See [{OWNER_ID}](../policies/root-policy.md).")),
        VALID,
        R3,
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        4,
        "R4: a path under a home directory is blocked",
        wrote(body("Notes: /Users/someone/notes.md")),
        VALID,
        R4_PATH,
        GREEN_WHAT,
        SETUP,
    ),
    Case(
        5,
        "R4: a file: link is blocked",
        wrote(body("Notes: [n](file:///srv/notes.md)")),
        VALID,
        R4_FILE,
        GREEN_WHAT,
        SETUP,
    ),
]

# ------------------------------------------------------------------ assertions


def masked_regions() -> tuple[bool, str]:
    """Every region the checks of form do not read, each holding a bare form and an id. A path
    on one machine is another matter: item 46."""
    forms = f"REQ-7 `{OWNER_ID}`"
    bodies = {
        "a fence": f"# F\n\n```text\n{forms}\n```\n",
        "a tilde fence left open": f"# F\n\n~~~\n{forms}\n",
        "an indented block": f"# F\n\npara\n\n    {forms}\n",
        "a comment": f"# F\n\n<!-- {forms} -->\n",
        "a code span": "# F\n\nThe form ``REQ-7`` is shown, not used.\n",
        "a link's text": "# F\n\n[REQ-7](../reqs.md#req-7)\n",
    }
    return all_of(
        [passes(text) for text in bodies.values()], f"{len(bodies)} masked regions pass: {', '.join(bodies)}"
    )


def a_path_on_one_machine_is_read_in_code_too() -> tuple[bool, str]:
    """A bare form inside code is an illustration; a local path inside code still leaks a machine
    and resolves nowhere else. Only the YAML block that opens the file is not read."""
    path = "/Users/someone/x.md"
    reds = {
        "a code span": (f"# F\n\nIt lies in `{path}`.\n", 10),
        "a fence": (f"# F\n\n```sh\ncat {path}\n```\n", 11),
        "an indented block": (f"# F\n\npara\n\n    cat {path}\n", 12),
        "a comment": (f"# F\n\n<!-- {path} -->\n", 10),
    }
    results = [blocks(text, messages.r4_one_machine(DOC, line, path)) for text, line in reds.values()]
    in_envelope = document(
        "# F\n", id="note-a", type="non-authoritative", title=f"About {path}", status="active"
    )
    green = expect(gate_on(Write(DOC, in_envelope))[0], 0, messages.g1_covered(), "stdout")
    return all_of([*results, green], f"red in {', '.join(reds)}; not read in the YAML block")


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


def local_paths_allowed() -> tuple[bool, str]:
    """The switch for a document that must show a container's home directory."""
    fence = body("```dockerfile\nWORKDIR /home/node/app\n```")
    return all_of(
        [
            blocks(fence, messages.r4_one_machine(DOC, 10, "/home/node/app"), patch=None),
            passes(fence, patch=own(local_paths="allow")),
            passes(body("Notes: /Users/someone/notes.md"), patch=own(local_paths="allow")),
        ],
        "a Dockerfile fence is red by default and passes under allow; so does prose",
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


def a_path_ends_before_the_sentence_does() -> tuple[bool, str]:
    return blocks(body("Notes are in /Users/someone/notes.md."), R4_PATH)


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
        (own(local_paths="off"), messages.c5_switch("local_paths")),
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


def control_character_in_a_pattern() -> tuple[bool, str]:
    """Red→green of the dials file itself: a pattern in YAML's double quotes, where `\\b` is a
    backspace, is refused before it is compiled — it would match nothing and pass in silence; the
    same pattern in single quotes finds the bare form. The golden line is typed by hand."""
    quoted = dials_text(own(lanes=[{**LANE, "pattern": "<P>"}]))
    red, _ = gate_on(wrote(body("See REQ-7.")), raw_dials=quoted.replace("<P>", '"\\bREQ-[0-9]+\\b"'))
    green, _ = gate_on(wrote(body("See REQ-7.")), raw_dials=quoted.replace("<P>", "'\\bREQ-[0-9]+\\b'"))
    mention, _ = gate_on(VALID, dials_patch=own(mentions=[{"pattern": "\x08note-[a-z]+"}]))
    literal = (
        "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes has a pattern holding the control"
        " character '\\x08' — YAML's double quotes turn a backslash escape into one, so the pattern would"
        " match nothing and pass in silence; write it in single quotes, where a backslash stands for"
        " itself — fix: write the entry as {pattern: <regular expression>, names: <what the form cites>,"
        " fix: <the link form to write>}; home: [<patterns>] is optional"
    )
    return all_of(
        [
            broken(red, messages.c5_lane(1, messages.lane_pattern_control("\x08"))),
            (literal in red.stderr, f"the golden line is not in: {red.stderr.strip()}"),
            expect(green, 2, r1().render(), "stderr"),
            broken(mention, messages.c5_mention(1, messages.lane_pattern_control("\x08"))),
        ],
        "double-quoted: exit 1 with the golden line; single-quoted: the form is found; a mention too",
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


def a_tree_taken_out() -> tuple[bool, str]:
    """`!dir/**` after `*.md` leaves a tree uncovered; `!dir/` names the directory alone, and
    the files inside it still match — as the install note says."""
    files = {"vendor/deep/v.md": "[x](gone.md)\n", SOURCE: source("See [x](gone.md).")}
    return all_of(
        [
            expect(scan_of(files, claim(["*.md", "!vendor/**"])), 2, "1 finding(s)", "stdout"),
            expect(scan_of(files, claim(["*.md", "!vendor/"])), 2, "2 finding(s)", "stdout"),
        ],
        "one finding with the tree taken out, two with the directory alone negated",
    )


def governed_only_without_root() -> tuple[bool, str]:
    """governed_only with no root policy is a configuration failure in every mode — as the mover
    refuses — never a skip that lets a write through with nothing examined; by default none is needed."""
    rootless = yaml.safe_dump({NAMESPACE: {"governed_only": True}})
    failure = messages.c5_governed_only_without_root()
    before, root = gate_on(VALID, raw_dials=rootless)
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", rootless)
    consumer.write(VALID.target, VALID.text)
    after = H.run_gate(event_json(consumer.root, VALID, event=AFTER))
    scan = H.run_gate("", args=["--scan", str(root)])
    default, _ = gate_on(VALID, raw_dials="{}\n")
    return all_of(
        [
            broken(before, failure),
            broken(after, failure),
            broken(scan, failure),
            expect(default, 0, messages.g1_covered(), "stdout"),
        ],
        "governed_only with no root policy is C5, exit 1, before the write, after it and in the scan; by"
        " default none is needed",
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
    """Two caps: twenty findings, and no more characters than leave the count line inside what the
    platform passes on. Short findings meet the first, long ones the second."""
    short = " ".join(f"[x{n}](t.md#nope-{n})" for n in range(25))
    by_count = after_write(SOURCE, {TARGET: TARGET_TEXT, SOURCE: source(short)})
    long_ones = " ".join(f"[x{n}](gone-{n}-{'y' * 150}.md)" for n in range(25))
    by_size = after_write(SOURCE, {SOURCE: source(long_ones)})
    printed = by_size.stderr.count("RED: docs/")
    checks = [
        (
            by_count.code == 2 and by_count.stderr.count("RED: docs/") == 20,
            "short findings: not twenty printed",
        ),
        (after_count(SOURCE, 25, 25, 20) in by_count.stderr, "short findings: the count line"),
        (by_size.code == 2 and 0 < printed < 20, f"long findings: {printed} printed"),
        (after_count(SOURCE, 25, 25, printed) in by_size.stderr, "long findings: the count line"),
        (len(by_size.stderr) < 10000, f"long findings: {len(by_size.stderr)} characters"),
    ]
    return all_of(
        checks, f"25 findings: 20 short ones printed, {printed} long ones, all inside 10,000 characters"
    )


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


# ------------------------------------------------------------------ the mover

MOVER = SCRIPTS / "move-document.sh"
OLD, NEW = "docs/notes/one.md", "docs/moved/deep/first.md"
ONE = note(
    '# One\n\n<a id="k1"></a>\n'
    "See [sib](two.md#k2), [self](one.md#k1), [here](#k1) and [up](../../constitution.yaml).\n",
    "note-one",
)
TWO = note(
    '# Two\n\n<a id="k2"></a>\n'
    "Back to [note-one](one.md#k1), [r] and `[shown](one.md)`. Once docs/notes/one.md.\n\n[r]: one.md\n",
    "note-two",
)
ONE_MOVED = (
    "See [sib](../../notes/two.md#k2), [self](first.md#k1), [here](#k1) and [up](../../../constitution.yaml)."
)
TWO_REPAIRED = (
    "Back to [note-one](../moved/deep/first.md#k1), [r] and `[shown](one.md)`. Once docs/notes/one.md."
)


def moving_consumer() -> Consumer:
    consumer = H.fresh_consumer(
        (Write(OLD, ONE), Write("docs/notes/two.md", TWO), Write("tools/x.sh", f"# see {OLD}\n"))
    )
    return consumer


def mover(consumer: Consumer, *arguments: str, cwd: str = "") -> Result:
    merged = {key: value for key, value in os.environ.items() if key != "CLAUDE_PLUGIN_DATA"}
    done = subprocess.run(
        [H.sh, str(MOVER), *arguments],
        cwd=consumer.root / cwd,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    return Result(done.returncode, done.stdout, done.stderr)


def scan(consumer: Consumer) -> Result:
    return H.run_gate("", args=["--scan", str(consumer.root)])


def tree_state(consumer: Consumer) -> str:
    done = subprocess.run(
        ["git", "status", "--porcelain"], cwd=consumer.root, capture_output=True, text=True, check=True
    )
    return done.stdout


def move_red_green() -> tuple[bool, str]:
    """Red is the tree after git mv alone; green is the tree after the act."""
    by_git = moving_consumer()
    (by_git.root / NEW).parent.mkdir(parents=True)
    by_git.git("mv", OLD, NEW)
    red = scan(by_git)
    acted = moving_consumer()
    done = mover(acted, "notes/one.md", "moved/deep/first.md", cwd="docs")
    first, two = (acted.root / NEW).read_text(), (acted.root / "docs/notes/two.md").read_text()
    checks = [
        expect(red, 2, messages.r5_no_target("docs/notes/two.md", 11, "one.md#k1").headline, "stdout"),
        expect(done, 0, messages.v1_moved(OLD, NEW), "stdout"),
        expect(done, 0, messages.v2_rewrote("docs/notes/two.md", 2), "stdout"),
        expect(done, 0, messages.v2_rewrote(NEW, 3), "stdout"),
        expect(done, 0, messages.v4_count(2, 5, 2), "stdout"),
        expect(done, 0, "GREEN: const-referencing: ", "stdout"),
        (ONE_MOVED in first, f"the moved document's own links: {first}"),
        (TWO_REPAIRED in two and "[r]: ../moved/deep/first.md" in two, f"inbound links: {two}"),
        expect(scan(acted), 0, "GREEN: ", "stdout"),
    ]
    return all_of(
        checks, "git mv alone leaves the scan red; the act leaves it green, fragments and code untouched"
    )


def mentions_are_listed_not_changed() -> tuple[bool, str]:
    acted = moving_consumer()
    done = mover(acted, OLD, NEW)
    script = (acted.root / "tools/x.sh").read_text()
    return all_of(
        [
            expect(done, 0, "MENTION: docs/notes/two.md:11: ", "stdout"),
            expect(
                done, 0, f"MENTION: tools/x.sh:1: '# see {OLD}' names the old path outside a link", "stdout"
            ),
            (script == f"# see {OLD}\n", "the script was not rewritten"),
        ],
        "a sentence, a code span and a script naming the old path are listed; none is changed",
    )


def repair_after_a_hand_move() -> tuple[bool, str]:
    """The fix R5 teaches is followed as printed, with the two paths filled in."""
    consumer = moving_consumer()
    (consumer.root / NEW).parent.mkdir(parents=True)
    consumer.git("mv", OLD, NEW)
    taught = scan(consumer).stdout
    command = messages.mover_command("--moved", "<old path>", "<new path>")
    if command not in taught:
        return False, f"the scan did not teach {command!r}: {taught}"
    typed = command.replace("<old path>", OLD).replace("<new path>", NEW)
    done = subprocess.run(typed, shell=True, cwd=consumer.root, capture_output=True, text=True, check=False)  # noqa: S602 — the point is to run the line as a reader would paste it
    return all_of(
        [
            (
                done.returncode == 0 and "GREEN: " in done.stdout,
                f"exit {done.returncode}: {done.stdout}{done.stderr}",
            ),
            expect(scan(consumer), 0, "GREEN: ", "stdout"),
        ],
        "the command the finding prints, pasted with the two paths, leaves the scan green",
    )


def repair_by_ids() -> tuple[bool, str]:
    """The fix R3 teaches is followed as printed: no path is given, the envelopes say where."""
    consumer = moving_consumer()
    (consumer.root / NEW).parent.mkdir(parents=True)
    consumer.git("mv", OLD, NEW)
    consumer.write("docs/notes/two.md", TWO.replace(", [r]", "").replace("[r]: one.md\n", ""))
    blocked, _ = gate_on(Write(DOC, note(body(f"See [{OWNER_ID}](../policies/root-policy.md)."))))
    command = messages.mover_command("--ids")
    if command not in blocked.stderr:
        return False, f"R3 did not teach {command!r}: {blocked.stderr}"
    done = subprocess.run(command, shell=True, cwd=consumer.root, capture_output=True, text=True, check=False)  # noqa: S602 — as above
    two = (consumer.root / "docs/notes/two.md").read_text()
    return all_of(
        [
            ("[note-one](../moved/deep/first.md#k1)" in two, f"the id link: {two}"),
            (messages.v2_rewrote("docs/notes/two.md", 1) in done.stdout, done.stdout + done.stderr),
        ],
        "an id link follows its document with no path given; the fragment is kept",
    )


def id_repair_leaves_an_ambiguous_id_alone() -> tuple[bool, str]:
    """Two documents under one id: the envelopes do not say which is meant, so nothing is guessed."""
    consumer = H.fresh_consumer(
        (
            Write("docs/notes/p.md", note("# P\n", "note-twin")),
            Write("docs/notes/q.md", note("# Q\n", "note-twin")),
            Write(SOURCE, source("See [note-twin](t.md).")),
            Write(TARGET, TARGET_TEXT),
        )
    )
    done = mover(consumer, "--ids")
    kept = "See [note-twin](t.md)." in (consumer.root / SOURCE).read_text()
    return kept and messages.v4_count(0, 0, 0) in done.stdout, done.stdout + done.stderr


def refusals_change_nothing() -> tuple[bool, str]:
    consumer = moving_consumer()
    before = tree_state(consumer)
    refused = [
        (mover(consumer, "docs/notes/none.md", NEW), messages.v5_not_listed("docs/notes/none.md")),
        (mover(consumer, OLD, "docs/notes/two.md"), messages.v5_target_exists("docs/notes/two.md")),
        (mover(consumer, OLD, OLD), messages.v5_same(OLD)),
        (mover(consumer, "--moved", OLD, NEW), messages.v5_not_moved(OLD, NEW)),
        (mover(consumer, OLD, "../outside.md"), messages.v5_outside("../outside.md")),
        (mover(consumer, OLD), messages.v5_usage("1 path(s) given")),
        (mover(consumer, "--ids", OLD, NEW), messages.v5_usage("2 path(s) given")),
        (mover(consumer, "--help"), messages.v5_usage("unrecognized arguments: --help")),
    ]
    results = [broken_first_line(result, failure.render()) for result, failure in refused]
    closing = [(messages.v4_nothing_changed() in result.stderr, "no closing line") for result, _ in refused]
    unchanged = (tree_state(consumer) == before, "a refusal changed the tree")
    return all_of(
        [*results, *closing, unchanged], f"{len(refused)} refusals, each exit 1, the tree as it was"
    )


def mover_without_dials() -> tuple[bool, str]:
    consumer = moving_consumer()
    (consumer.root / "constitution.yaml").unlink()
    result = mover(consumer, OLD, NEW)
    ok, evidence = broken_first_line(result, messages.v5_no_dials(str(consumer.root)).render())
    return ok and (consumer.root / OLD).exists(), evidence


def mover_ends_red_when_the_tree_is() -> tuple[bool, str]:
    consumer = moving_consumer()
    consumer.write("docs/notes/three.md", note(body("See [x](gone.md)."), "note-three"))
    return expect(
        mover(consumer, OLD, NEW),
        2,
        messages.r5_no_target("docs/notes/three.md", LINE, "gone.md").headline,
        "stdout",
    )


GOLDEN_MOVER = [
    f"MOVED: {OLD} → {NEW}",
    "REWROTE: docs/notes/two.md: 2 link(s)",
    "names the old path outside a link — read it and decide; nothing was changed",
    "2 file(s) rewritten, 5 link(s), 2 mention(s) listed; the whole tree is checked next",
]


def golden_mover_lines() -> tuple[bool, str]:
    out = mover(moving_consumer(), OLD, NEW).stdout
    refused = mover(moving_consumer(), OLD, "docs/notes/two.md").stderr
    missing = [line for line in GOLDEN_MOVER if line not in out]
    wanted = (
        "BROKEN: docs/notes/two.md already exists — fix: choose a path that is free, or move what lies"
        " there first\nBROKEN: the move could not run — nothing was changed"
    )
    if wanted not in refused:
        missing.append(wanted)
    return (
        not missing,
        f"{len(GOLDEN_MOVER) + 2} literal lines found" if not missing else f"not found: {missing}",
    )


# ------------------------------------------------------------------ the plugin's other parts

PLUGIN = SCRIPTS.parent
CHAT_RULE = (
    "const-referencing (advisory): in chat, write every reference to a file, a section or a document as a"
    " markdown link wherever the file exists. A number, letter or key is a handle local to its message,"
    " decision or session: when a cite crosses that boundary, name the message or decision it came from.\n"
)


def hooks_file() -> tuple[bool, str]:
    """Three handlers, each in the exec form with an explicit timeout; both tool events run the
    gate's one entry point, which tells them apart by the event's name."""
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
    gate = ["${CLAUDE_PLUGIN_ROOT}/scripts/check-references.sh"]
    wanted = {
        "PreToolUse": ("Write|Edit", gate),
        "PostToolUse": ("Write|Edit", gate),
        "SessionStart": (None, ["${CLAUDE_PLUGIN_ROOT}/scripts/print-chat-rule.sh"]),
    }
    problems = [name for name in wanted if name not in hooks] + [name for name in hooks if name not in wanted]
    for name, (matcher, args) in wanted.items():
        for group in hooks.get(name, []):
            handler = group["hooks"][0]
            right = (
                group.get("matcher") == matcher
                and handler.get("type") == "command"
                and handler.get("command") == "sh"
                and handler.get("args") == args
                and isinstance(handler.get("timeout"), int)
                and all((SCRIPTS / Path(arg).name).is_file() for arg in args)
            )
            if not right:
                problems.append(f"{name}: {group}")
    return not problems, "three handlers, exec form, timeouts, scripts present" if not problems else str(
        problems
    )


def chat_rule() -> tuple[bool, str]:
    done = subprocess.run(
        [H.sh, str(SCRIPTS / "print-chat-rule.sh")], input="{}", capture_output=True, text=True, check=False
    )
    ok = done.returncode == 0 and done.stdout == CHAT_RULE and done.stderr == ""
    return ok, f"exit 0, the rule as typed here, {len(CHAT_RULE) - 1} characters" if ok else repr(done)


def skill_description_fits() -> tuple[bool, str]:
    """The description as the listing loads it — the folded scalar's final line break counted, as
    MODULE.md counts it — under the listing's 1,536 characters, of the size MODULE.md states, and
    carrying when to use the skill and that it is advisory."""
    text = (PLUGIN / "skills" / "referencing" / "SKILL.md").read_text()
    front = yaml.safe_load(text.split("---\n")[1])
    description = str(front["description"])
    size = len(description)
    found = re.search(r"skill listing, ([\d,]+) characters", (PLUGIN / "MODULE.md").read_text())
    stated = int(found.group(1).replace(",", "")) if found else None
    problems = [
        *([] if front["name"] == "referencing" else [f"name {front['name']!r}"]),
        *([] if size <= 1536 else [f"{size} characters, over the listing's 1,536"]),
        *(
            []
            if stated == size
            else ["no 'skill listing, N characters' line in MODULE.md"]
            if stated is None
            else [f"MODULE.md states {stated}, the description holds {size}"]
        ),
        *([] if "Use when " in description else ["no 'Use when ' clause"]),
        *([] if "Advisory:" in description else ["no 'Advisory:' line"]),
    ]
    return not problems, "; ".join(problems) or (
        f"description of {size} characters, as MODULE.md states, under the listing's 1,536; its trigger"
        " and its advisory line present"
    )


def install_note_example_is_accepted() -> tuple[bool, str]:
    """The calibration block of the install note, handed to the gate as it stands: it parses, and its
    lane fires on the form it declares. That double quotes make a backslash escape a control
    character is item 6's, run through the gate."""
    note_text = (PLUGIN / "INSTALL.md").read_text()
    block = note_text.split("```yaml\n")[1].split("```")[0]
    dials = yaml.safe_load("\n".join(line[3:] for line in block.splitlines()))
    lane = dials[NAMESPACE]["lanes"][0]
    finding = messages.r1_bare_form(DOC, LINE, "REQ-7", lane["names"], lane["fix"])
    raw = yaml.safe_dump({**Consumer(Path()).dials, **dials}, sort_keys=False)
    result, _ = gate_on(wrote(body("See REQ-7.")), raw_dials=raw)
    return all_of(
        [expect(result, 2, finding.render(), "stderr")], "the note's example is accepted and its lane fires"
    )


# ------------------------------------------------------------------ found by the first validation


def porcelain(consumer: Consumer) -> str:
    return tree_state(consumer)


def mover_asks_before_it_moves() -> tuple[bool, str]:
    """Whatever the closing scan would fail on is asked before the file moves: no lychee, and
    governed_only with no root policy, are refusals that find the tree as it was."""
    no_lychee = moving_consumer()
    before = porcelain(no_lychee)
    merged = {**{k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}, **path_with(None)}
    done = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=no_lychee.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    first = broken_first_line(
        Result(done.returncode, done.stdout, done.stderr), messages.x1_no_lychee("0.24.2").render()
    )
    rootless = H.fresh_consumer((Write(OLD, ONE), Write("docs/notes/two.md", TWO)))
    rootless.write("constitution.yaml", yaml.safe_dump({NAMESPACE: {"governed_only": True}}))
    rootless.commit()
    state = porcelain(rootless)
    refused = mover(rootless, OLD, NEW)
    return all_of(
        [
            first,
            (
                messages.v4_nothing_changed() in done.stderr and porcelain(no_lychee) == before,
                "no lychee: the tree changed",
            ),
            broken_first_line(refused, messages.v5_no_root_policy().render()),
            (
                porcelain(rootless) == state and (rootless.root / OLD).exists(),
                "no root policy: the tree changed",
            ),
        ],
        "no lychee, and governed_only with no root policy: refused before the move, the tree as it was",
    )


def mover_says_when_it_stopped_midway() -> tuple[bool, str]:
    """A failure after the move must not claim that nothing was changed."""
    consumer = moving_consumer()
    dying = 'case "$1" in --version) echo "lychee 0.24.2";; *) echo "error: gone wrong" >&2; exit 3;; esac\n'
    merged = {**{k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}, **path_with(dying)}
    done = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    ok = (
        done.returncode == 1
        and messages.v4_stopped_midway() in done.stderr
        and messages.v4_nothing_changed() not in done.stderr
        and (consumer.root / NEW).exists()
    )
    return ok, "exit 1, the closing line says the act stopped midway" if ok else done.stdout + done.stderr


def mover_keeps_every_other_character() -> tuple[bool, str]:
    """CRLF line endings and a byte order mark survive a rewrite; a file that is not UTF-8 is
    left alone, and the mover says so."""
    consumer = H.fresh_consumer((Write(OLD, ONE),))
    crlf = "\ufeff# Two\r\n\r\nSee [one](one.md).\r\n"
    (consumer.root / "docs/notes/crlf.md").write_bytes(crlf.encode("utf-8"))
    (consumer.root / "docs/notes/latin.md").write_bytes("# Caf\xe9\n\nSee [one](one.md).\n".encode("latin-1"))
    consumer.commit()
    done = mover(consumer, OLD, NEW)
    after = (consumer.root / "docs/notes/crlf.md").read_bytes().decode("utf-8")
    latin = (consumer.root / "docs/notes/latin.md").read_bytes()
    return all_of(
        [
            (after == crlf.replace("one.md", "../moved/deep/first.md"), f"CRLF document: {after!r}"),
            (b"Caf\xe9" in latin and b"(one.md)" in latin, "the latin-1 file was rewritten"),
            (messages.v2_left_alone("docs/notes/latin.md") in done.stdout, done.stdout),
        ],
        "one link rewritten, line endings and the byte order mark kept; the latin-1 file left alone, named",
    )


def mover_refuses_cleanly() -> tuple[bool, str]:
    consumer = moving_consumer()
    before = porcelain(consumer)
    under_a_file = mover(consumer, OLD, "docs/notes/two.md/inside.md")
    (consumer.root / ".git" / "index.lock").write_text("")
    locked = mover(consumer, OLD, "brand/new/dir/first.md")
    (consumer.root / ".git" / "index.lock").unlink()
    return all_of(
        [
            broken_first_line(under_a_file, messages.v5_parent_is_a_file("docs/notes/two.md").render()),
            (locked.code == 1 and "BROKEN: git mv refused: " in locked.stderr, locked.stderr),
            (messages.v4_nothing_changed() in locked.stderr, "no closing line"),
            (
                not (consumer.root / "brand").exists(),
                "directories made for a move git refused were left behind",
            ),
            (porcelain(consumer) == before, "the tree changed"),
        ],
        "a new path under a file, and a git mv git refuses: exit 1, no directory left, the tree as it was",
    )


def mover_quotes_and_bounds() -> tuple[bool, str]:
    """A new name with a space is escaped in the link, so it stays a link; a longer name that ends
    in the old one is no mention of it."""
    consumer = H.fresh_consumer(
        (
            Write("docs/notes/a.md", note("# A\n", "note-a")),
            Write("docs/notes/b.md", note(body("See [a](a.md). The file data.md is another."), "note-b")),
            Write("docs/notes/data.md", note("# D\n", "note-d")),
        )
    )
    done = mover(consumer, "docs/notes/a.md", "docs/notes/new name.md")
    b = (consumer.root / "docs/notes/b.md").read_text()
    return all_of(
        [
            ("See [a](new%20name.md)." in b, f"the link: {b}"),
            expect(done, 0, messages.v4_count(1, 1, 0), "stdout"),
            expect(scan(consumer), 0, "and 1 link(s) examined", "stdout"),
        ],
        "the space is escaped and the link still counted as one; data.md is not a mention of a.md",
    )


def reference_style_links() -> tuple[bool, str]:
    definitions = f"\n\n[o]: {TO_OWNER}\n[r]: ../policies/root-policy.md\n"
    astray = messages.r3_id_link_astray(DOC, LINE, OWNER_ID, "../policies/root-policy.md", OWNER, TO_OWNER)
    return all_of(
        [
            passes(f"# Fixture\nSee [`{OWNER_ID}`][o], [{OWNER_ID}][O] and [o].{definitions}"),
            blocks(f"# Fixture\nSee [{OWNER_ID}][r].{definitions}", astray),
            passes(f"# Fixture\nSee [REQ-7][r].{definitions}"),
        ],
        "an id in ticks used through a label is a link; a label that opens another document is R3",
    )


def a_fence_under_a_list_item() -> tuple[bool, str]:
    shown = "# F\n\n1. Configure:\n\n    ```yaml\n    # implements REQ-7\n\n    key: value\n    ```\n"
    deeper = "# F\n\n- a\n  - b\n\n      ~~~\n      REQ-7\n\n      more\n      ~~~\n"
    return all_of(
        [passes(shown), passes(deeper)],
        "a fence indented with its list item is code, a blank line inside it or not",
    )


def what_is_no_path_on_one_machine() -> tuple[bool, str]:
    lines = [
        "The route `/home/feed` and the page https://example.invalid/home/ann/page are no machines.",
        "Neither is ~/Users/x, nor docs/home/ann/x.md, nor a bare /home/ or /Users/.",
    ]
    return passes("# F\n\n" + "\n".join(lines) + "\n")


def owned_invocation_from_inside() -> tuple[bool, str]:
    """The gate started with the repository as its working directory — as a hook is — still takes
    nothing from the repository's own lychee files."""
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    consumer.write(".lycheeignore", "gone.md\n")
    consumer.write("lychee.toml", 'exclude_path = ["docs"]\n')
    merged = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
    done = subprocess.run(
        [H.sh, str(SCRIPTS / "check-references.sh"), "--scan"],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    return expect(Result(done.returncode, done.stdout, done.stderr), 2, finding.render(), "stdout")


def one_large_document() -> tuple[bool, str]:
    """A table of 4,000 rows and 8,000 links, and two openers that are never closed, repeated:
    each judged in seconds, far inside the hook's timeout."""
    table = "".join(f"| [r{n}](t.md#k1) | `code{n}` | [s{n}](t.md) |\n" for n in range(4000))
    timings: list[str] = []
    shapes = {
        "table": table,
        "<a": "<a " * 20000,
        "<!--": "<!-- " * 20000,
        "[": "[" * 20000,
        "ticks": "`x` " * 30000,
    }
    for name, text in shapes.items():
        began = time.monotonic()
        result, _ = gate_on(Write(SOURCE, source("x") + text), files={TARGET: TARGET_TEXT})
        took = time.monotonic() - began
        timings.append(f"{name} {took:.1f} s")
        if result.code != 0 or took > 5:
            return False, f"{name}: exit {result.code} after {took:.1f} s: {result.stderr[:200]}"
    return True, ", ".join(timings)


def uncovered_write_that_breaks_a_covered_link() -> tuple[bool, str]:
    only_source = own(territories=["*.md", "!" + TARGET])
    broken_target = TARGET_TEXT.replace('<a id="k1"></a>\n', "")
    files = {TARGET: broken_target, SOURCE: source("See [x](t.md#k1).")}
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#k1", "k1", TARGET, None)
    harmless = {TARGET: TARGET_TEXT, SOURCE: source("See [x](t.md#k1).")}
    return all_of(
        [
            expect(after_write(TARGET, files, only_source), 2, finding.render(), "stderr"),
            expect(
                after_write(TARGET, harmless, only_source),
                0,
                shared.g1_green_skip(messages.g1_skip_not_covered(TARGET)),
                "stdout",
            ),
        ],
        "an uncovered document written without a cited anchor is reported; a harmless write is a skip",
    )


def a_misspelt_dial() -> tuple[bool, str]:
    known = sorted(KEYS)
    result, _ = gate_on(VALID, dials_patch=own(heading_anchor="allow"))
    return broken(result, messages.c5_unknown_key("heading_anchor", known))


def one_break_one_finding() -> tuple[bool, str]:
    """A missing anchor is R6 and not R7 as well; two links alike on one line are one finding."""
    out = tree_scan("See [a](t.md#nope) and [b](t.md#nope).")
    ok = out.code == 2 and "RED: 1 finding(s)" in out.stdout and "resolves only through" not in out.stdout
    return ok, "one R6, no R7, said once" if ok else out.stdout


def anchors_by_name_and_encoded_paths() -> tuple[bool, str]:
    named = note('# N\n\n<a name="old-style"></a>\n## Section Here\n', "note-n")
    spaced = "docs/notes/my dir/t.md"
    finding = messages.r7_heading_anchor(SOURCE, LINE, "my%20dir/t.md#first-section", spaced)
    return all_of(
        [
            expect(
                scan_of({"docs/notes/n.md": named, SOURCE: source("See [x](n.md#old-style).")}),
                0,
                "GREEN: ",
                "stdout",
            ),
            expect(
                scan_of({spaced: TARGET_TEXT, SOURCE: source("See [x](my%20dir/t.md#first-section).")}),
                2,
                finding.render(),
                "stdout",
            ),
        ],
        "an `a name` is an anchor somebody wrote; a path with an escaped space is still read for R7",
    )


def byte_order_mark_before_the_block() -> tuple[bool, str]:
    text = "\ufeff" + document(
        "# F\n", id="note-a", type="non-authoritative", title="In /Users/ann/x.md", status="active"
    )
    return expect(gate_on(Write(DOC, text))[0], 0, messages.g1_covered(), "stdout")


def scan_findings_in_line_order() -> tuple[bool, str]:
    out = scan_of(
        {TARGET: TARGET_TEXT, SOURCE: note("# S\nSee [x](gone.md).\nThen `note-t` bare.\n", "note-s")}
    ).stdout
    order = [out.find("link target gone.md"), out.find("document id 'note-t'")]
    return -1 not in order and order == sorted(
        order
    ), "line 9 before line 10, whichever check found it" if order == sorted(order) else out


def a_break_in_words_of_lychee() -> tuple[bool, str]:
    """A kind of break this module has no text of its own for is reported in the checker's words."""
    report = json.dumps(
        {
            "error_map": {
                "SRC": [
                    {
                        "url": "file:///nowhere/x.md",
                        "status": {"text": "Some new failure"},
                        "span": {"line": 9, "column": 5},
                    }
                ]
            }
        }
    )
    # the fake's PATH holds no cat: the shell's own read and printf do
    script = (
        'case "$1" in --version) echo "lychee 0.24.2";; *) while read -r _; do :; done;'
        ' while IFS= read -r line; do printf "%s\\n" "$line"; done < "$0.json"; exit 2;; esac\n'
    )
    env = path_with(script)
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    Path(env["PATH"], "lychee.json").write_text(
        report.replace("SRC", str(consumer.root / SOURCE)) + "\n"
    )  # read needs the line closed
    result = H.run_gate("", args=["--scan", str(consumer.root)], env=env)
    finding = messages.r5_unresolved(SOURCE, LINE, "/nowhere/x.md", "Some new failure")
    return expect(result, 2, finding.render(), "stdout")


def mover_entry_absences() -> tuple[bool, str]:
    """The mover's own exits before the guard — no python3, an install without the shared code — and
    the shared C2 inside it, closed by the mover's clause."""
    consumer = moving_consumer()
    env = {
        **{k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"},
        "PATH": path_with(None)["PATH"],
    }
    bare = H.scratch_dir()
    os.symlink(shutil.which("dirname") or "/usr/bin/dirname", bare / "dirname")
    no_python = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env={**env, "PATH": str(bare)},
        check=False,
    )
    plugin = H.scratch_dir() / "plugin"
    shutil.copytree(SCRIPTS, plugin / "scripts", symlinks=True)
    shared_code = plugin / "scripts" / "const_gate"  # a link in a checkout, a directory in an install
    shared_code.unlink() if shared_code.is_symlink() else shutil.rmtree(shared_code)
    no_shared = subprocess.run(
        [H.sh, str(plugin / "scripts" / "move-document.sh"), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    shadow = H.scratch_dir()  # the shared C2, printed by the preflight, closes with the mover's own clause
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_library = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env={**env, "PYTHONPATH": str(shadow)},
        check=False,
    )
    library_first = no_library.stderr.splitlines()[0] if no_library.stderr else ""
    closing = "BROKEN: the move could not run — nothing was changed"
    return all_of(
        [
            (
                no_python.returncode == 1
                and "BROKEN: const-referencing needs python3" in no_python.stderr
                and closing in no_python.stderr,
                no_python.stderr,
            ),
            (
                no_shared.returncode == 1
                and "is installed without its shared code" in no_shared.stderr
                and closing in no_shared.stderr,
                no_shared.stderr,
            ),
            (
                no_library.returncode == 1
                and library_first.endswith(" — until then nothing is moved")
                and "pass unchecked" not in no_library.stderr
                and closing in no_library.stderr,
                no_library.stderr,
            ),
            ((consumer.root / OLD).exists(), "the file moved"),
        ],
        "each exit 1 with its designed line and the mover's closing line; nothing moved",
    )


WHYS = {
    "R2": "  why: an id names a document that can move: only a link lets a reader reach it and lets a move"
    " repair it",
    "R3": "  why: a link that shows one document's id and opens another misleads every reader who trusts"
    " the text",
    "R4": "  why: it resolves on the machine it was written on and nowhere else",
    "R5": "  why: a reference that does not resolve fails the reader exactly when they need it, and nobody"
    " else sees it",
    "R6": "  why: a reference that does not resolve fails the reader exactly when they need it, and nobody"
    " else sees it",
    "R7": "  why: a generated name changes when the heading is reworded, and every link through it breaks"
    " unseen",
    "R8": "  why: outside Markdown no link checker follows a name, so it dangles unseen once the document"
    " is renamed or deleted",
}


def golden_why_lines() -> tuple[bool, str]:
    """The reason of every finding, typed by hand: R1's is in the first golden item."""
    lint_runs = {str(case.expect.key): gate_on(case.red, dials_patch=LANES)[0].stderr for case in CASES[:4]}
    tree_out = tree_scan("See [a](gone.md), [b](t.md#nope) and [d](t.md#first-section).").stdout
    named = scan_of({SOURCE: source("x"), "tools/x.sh": "# note-gone\n"}, own(mentions=[MENTION])).stdout
    outputs = {**lint_runs, "R5": tree_out, "R6": tree_out, "R7": tree_out, "R8": named}
    missing = [key for key, line in WHYS.items() if line not in outputs[key]]
    return not missing, f"{len(WHYS)} reasons found as typed" if not missing else f"not found: {missing}"


# ------------------------------------------------------------------ found by the second validation

DYING = 'case "$1" in --version) echo "lychee 0.24.2";; *) echo "error: gone wrong" >&2; exit 3;; esac\n'


def mover_with(consumer: Consumer, lychee_script: str | None, *arguments: str) -> Result:
    merged = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
    merged.update(path_with(lychee_script))
    done = subprocess.run(
        [H.sh, str(MOVER), *arguments],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    return Result(done.returncode, done.stdout, done.stderr)


def midway_after_the_move_alone() -> tuple[bool, str]:
    """A lone document, nothing to rewrite: the move alone is a change, and the closing line
    must say so when the check dies after it."""
    alone = H.fresh_consumer((Write(OLD, note("# One\n", "note-one")),))
    done = mover_with(alone, DYING, OLD, NEW)
    by_hand = moving_consumer()
    (by_hand.root / NEW).parent.mkdir(parents=True)
    by_hand.git("mv", OLD, NEW)
    repaired = mover_with(by_hand, DYING, "--moved", OLD, NEW)
    return all_of(
        [
            (done.code == 1 and messages.v4_stopped_midway() in done.stderr, f"move alone: {done.stderr}"),
            (
                repaired.code == 1 and messages.v4_stopped_midway() in repaired.stderr,
                f"--moved: {repaired.stderr}",
            ),
            ("REWROTE: docs/notes/two.md" in repaired.stdout, "--moved rewrote nothing"),
        ],
        "after the move alone, and after a rewrite with no move: the act stopped midway",
    )


def fences_close_at_their_depth() -> tuple[bool, str]:
    """A fence closes at its opener's depth: a deeper fence shown inside it is content, not its
    end; a fence under a list item closes when indented like it, a tab counting."""
    inner = "1. Configure:\n\n    ```yaml\n    key: v\n    ```\n"
    shows_a_fence = "# F\n\nHow to:\n\n```\n" + inner + "```\n\nAfter it, REQ-7 is bare.\n"
    tabbed = "# F\n\n- item\n\n\t```\n\tcode REQ-9\n\t```\n\nAfter REQ-7.\n"
    unclosed_in_list = "# F\n\n- item\n\n    ```\n    REQ-9\n\nAfter REQ-7.\n"
    return all_of(
        [
            blocks(shows_a_fence, r1(line=20)),
            blocks(tabbed, r1(line=16)),
            passes(unclosed_in_list),
        ],
        "red after a fence that shows a fence, red after a tab-indented fence, green inside one never closed",
    )


def footnotes_are_no_links() -> tuple[bool, str]:
    named = messages.r1_bare_form(DOC, 12, "REQ-9", str(LANE["names"]), str(LANE["fix"]))
    with_footnote = "# F\n\nA claim.[^1]\n\n[^1]: REQ-9 says so, see [x](../policies/root-policy.md).\n"
    consumer = H.fresh_consumer(
        (
            Write("docs/notes/a.md", note("# A\n", "note-a")),
            Write(
                "docs/notes/b.md", note("# B\n\nA claim.[^1]\n\n[^1]: a.md was the first note.\n", "note-b")
            ),
        )
    )
    moved = mover(consumer, "docs/notes/a.md", "docs/notes/h/a.md")
    prose = (consumer.root / "docs/notes/b.md").read_text()
    return all_of(
        [
            blocks(with_footnote, named),
            expect(
                tree_scan("A claim.[^note]\n\n[^note]: t.md#first-section is named."), 0, "GREEN: ", "stdout"
            ),
            (
                "[^1]: a.md was the first note." in prose and messages.v4_count(0, 0, 1) in moved.stdout,
                f"footnote prose rewritten: {prose}",
            ),
        ],
        "a bare form in a footnote is red; a path in one is neither resolved nor rewritten, only listed",
    )


def labels_fold_case_and_nest() -> tuple[bool, str]:
    folded = passes(f"# Fixture\nSee [`{OWNER_ID}`][O].\n\n[o]: {TO_OWNER}\n")
    nested = expect(tree_scan("See [x [o] y](t.md#k1).\n\n[o]: t.md\n"), 0, "and 2 link(s)", "stdout")
    colon = passes("# Fixture\nSee [REQ-7]: and more.\n\n[REQ-7]: ../policies/root-policy.md\n")
    via_label = messages.r7_heading_anchor(SOURCE, 11, "t.md#first-section", TARGET)
    once = tree_scan("See [via][h] and [again][h].\n\n[h]: t.md#first-section\n")
    return all_of(
        [
            folded,
            nested,
            colon,
            expect(once, 2, via_label.render(), "stdout"),
            expect(once, 2, "1 finding(s)", "stdout"),
        ],
        "a label matches in any case; a usage inside a link's text is none; a colon after one is prose;"
        " one R7 per definition",
    )


def r4_more_shapes() -> tuple[bool, str]:
    reds = [
        ("PATH: `PATH=/usr/bin:/home/ann/bin`", "/home/ann/bin"),
        ("Windows: `C:/Users/ann/x`", "C:/Users/ann/x"),
    ]
    results = [blocks(body(text), messages.r4_one_machine(DOC, LINE, path)) for text, path in reds]
    return all_of(
        [*results, passes(body("Mine: ~/Users/x/y and ~/home/ann/z."))],
        "a PATH entry and C:/Users are red; tilde paths of any depth are not",
    )


def a_mention_ends_where_the_name_does() -> tuple[bool, str]:
    consumer = H.fresh_consumer(
        (
            Write("docs/notes/a.md", note("# A\n", "note-a")),
            Write(
                "docs/notes/b.md", note('# B\n\nThe a.mdx-notes tool, and <a href="a.md">it</a>.\n', "note-b")
            ),
        )
    )
    done = mover(consumer, "docs/notes/a.md", "docs/notes/h/a.md")
    b = (consumer.root / "docs/notes/b.md").read_text()
    return all_of(
        [
            (messages.v4_count(1, 1, 0) in done.stdout, done.stdout),
            ('<a href="h/a.md">' in b, f"the href: {b}"),
        ],
        "a.mdx-notes is no mention of a.md; an href is a link, rewritten and not listed",
    )


def older_heading_link_not_repeated() -> tuple[bool, str]:
    files = {
        TARGET: TARGET_TEXT,
        SOURCE: source("See [x](t.md#first-section)."),
        "docs/notes/u.md": note("# U\n", "note-u"),
    }
    return expect(after_write("docs/notes/u.md", files), 0, messages.g1_covered(), "stdout")


def a_link_checker_that_hangs() -> tuple[bool, str]:
    """A checker that never answers is a configuration failure inside the hook's timeout, never
    a hook the platform gives up on: the version probe and the run have a budget each."""
    sleep = shutil.which("sleep") or "/bin/sleep"  # the fake's PATH holds no sleep
    slow_version = f'case "$1" in --version) {sleep} 8; echo "lychee 0.24.2";; *) exit 0;; esac\n'
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    began = time.monotonic()
    result = H.run_gate("", args=["--scan", str(consumer.root)], env=path_with(slow_version))
    took = time.monotonic() - began
    ok = result.code == 1 and "BROKEN: " in result.stderr and 4 < took < 8
    return ok, f"exit {result.code} after {took:.1f} s: {result.stderr[:160]}"


def mover_refuses_what_would_leave_coverage() -> tuple[bool, str]:
    consumer = moving_consumer()
    (consumer.root / "docs/notes/link.md").symlink_to("one.md")
    consumer.commit()
    before = tree_state(consumer)
    refused = [
        (mover(consumer, OLD, "docs/newdir/"), messages.v5_names_a_directory("docs/newdir/")),
        (mover(consumer, OLD, "docs/notes/one.txt"), messages.v5_leaves_markdown(OLD, "docs/notes/one.txt")),
        (mover(consumer, "docs/notes/link.md", NEW), messages.v5_is_a_link("docs/notes/link.md")),
    ]
    results = [broken_first_line(result, failure.render()) for result, failure in refused]
    outside = H.scratch_dir()
    merged = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
    nowhere = subprocess.run(
        [H.sh, str(MOVER), "a.md", "b.md"],
        cwd=outside,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    return all_of(
        [
            *results,
            (tree_state(consumer) == before, "the tree changed"),
            (nowhere.returncode == 1 and "is not inside a git repository" in nowhere.stderr, nowhere.stderr),
        ],
        "a directory, a name that is no Markdown, a link, no repository: each refused, the tree as it was",
    )


def case_only_rename_and_uncovered_destination() -> tuple[bool, str]:
    """A rename in case alone is a move; a document moved out of coverage still has its own
    links repaired, and the links to it."""
    consumer = moving_consumer()
    renamed = mover(consumer, OLD, "docs/notes/One.md")
    two = (consumer.root / "docs/notes/two.md").read_text()
    out = moving_consumer()
    out.write("constitution.yaml", dials_text(own(territories=["docs/notes/**"])))
    out.commit()
    moved_out = mover(out, OLD, "docs/elsewhere/one.md")
    own_links = (out.root / "docs/elsewhere/one.md").read_text()
    return all_of(
        [
            expect(renamed, 0, messages.v1_moved(OLD, "docs/notes/One.md"), "stdout"),
            expect(
                moved_out, 0, messages.v2_rewrote("docs/elsewhere/one.md", 1), "stdout"
            ),  # the others still reach
            ("[note-one](One.md#k1)" in two, f"inbound after the case rename: {two}"),
            ("[sib](../notes/two.md#k2)" in own_links, f"own links of the document moved out: {own_links}"),
            (
                "[note-one](../elsewhere/one.md#k1)" in (out.root / "docs/notes/two.md").read_text(),
                "inbound to the document moved out",
            ),
        ],
        "One.md is a move; a document moved outside the territory keeps working links both ways",
    )


def mover_routes_its_log() -> tuple[bool, str]:
    """The earliest refusal after the log is routed — a malformed namespace — lands in the log the
    dial names: the routing stands before every refusal that follows it."""
    consumer = moving_consumer()
    consumer.write("constitution.yaml", dials_text(own(log_dir=".gate-logs", bare_ids="maybe")))
    consumer.write(".gitignore", ".gate-logs/\n")
    consumer.commit()
    refused = mover(consumer, OLD, "docs/notes/two.md")
    log = consumer.root / ".gate-logs" / "const-referencing.jsonl"
    lines = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    ok = refused.code == 1 and any(
        "bare_ids must be refuse or allow" in entry.get("text", "") for entry in lines
    )
    return (
        ok,
        f"{len(lines)} log line(s) under log_dir, the refusal among them" if ok else f"log: {lines[-2:]}",
    )


GOLDEN_TREE = {
    "R5": f"RED: {SOURCE}:9: link target gone.md does not exist",
    "R5 fix": '  fix: correct the path; if the target was moved by hand, repair every link to it by: sh "',
    "R5 fix, the rest": 'scripts/move-document.sh" --moved <old path> <new path>; if it was deleted,'
    " remove the link and state here what it was cited for",
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
        6,
        "a pattern holding a control character — YAML's double-quoted \\b — is exit 1, never a silent pass",
        control_character_in_a_pattern,
    ),
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
    Assertion(
        42,
        "governed_only without a root policy is C5 in every mode; the default needs none",
        governed_only_without_root,
    ),
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
    Assertion(
        60, "the move's red→green: git mv alone leaves the scan red, the act leaves it green", move_red_green
    ),
    Assertion(
        61, "the mover lists what names the old path and changes none of it", mentions_are_listed_not_changed
    ),
    Assertion(
        62, "the fix R5 teaches, pasted as printed, repairs a move made by hand", repair_after_a_hand_move
    ),
    Assertion(
        63, "the fix R3 teaches, pasted as printed, repairs id links from the envelopes", repair_by_ids
    ),
    Assertion(64, "every refusal of the mover is exit 1 and changes nothing", refusals_change_nothing),
    Assertion(65, "with no dials file the mover refuses before it moves", mover_without_dials),
    Assertion(66, "the mover exits with the scan's verdict", mover_ends_red_when_the_tree_is),
    Assertion(67, "golden lines of the mover, typed by hand", golden_mover_lines),
    Assertion(
        68, "the id repair leaves alone an id two documents carry", id_repair_leaves_an_ambiguous_id_alone
    ),
    Assertion(
        45, "a negated pattern takes a tree out of the territory: !dir/**, not !dir/", a_tree_taken_out
    ),
    Assertion(
        70, "hooks.json: three handlers in the exec form, explicit timeouts, scripts present", hooks_file
    ),
    Assertion(71, "the always-on rule is printed as typed here, and nothing else", chat_rule),
    Assertion(
        72,
        "the skill's description fits the listing, matches the size MODULE.md states, and carries its"
        " trigger and its advisory line",
        skill_description_fits,
    ),
    Assertion(
        73,
        "the install note's calibration example is accepted by the gate as it stands",
        install_note_example_is_accepted,
    ),
    Assertion(29, "R4 names the path, not the full stop after it", a_path_ends_before_the_sentence_does),
    Assertion(
        46,
        "R4 reads code and comments too; only the YAML block that opens the file is not read",
        a_path_on_one_machine_is_read_in_code_too,
    ),
    Assertion(
        80,
        "the mover asks everything that can refuse before it moves: no lychee, no root policy",
        mover_asks_before_it_moves,
    ),
    Assertion(
        81,
        "a failure after the move says the act stopped midway, never that nothing changed",
        mover_says_when_it_stopped_midway,
    ),
    Assertion(
        82,
        "the mover keeps CRLF and a byte order mark, and leaves a file that is not UTF-8 alone",
        mover_keeps_every_other_character,
    ),
    Assertion(
        83,
        "a new path under a file, and a git mv that git refuses: refused, no directory left behind",
        mover_refuses_cleanly,
    ),
    Assertion(
        84,
        "the mover escapes a space in a link; a longer name is no mention of a shorter one",
        mover_quotes_and_bounds,
    ),
    Assertion(
        85,
        "reference-style links: a usage is a link, and is judged by what its label opens",
        reference_style_links,
    ),
    Assertion(86, "a fence indented under a list item is code", a_fence_under_a_list_item),
    Assertion(
        87,
        "R4 leaves alone a route, an address, a tilde path and a bare home directory",
        what_is_no_path_on_one_machine,
    ),
    Assertion(
        88,
        "started inside the repository, the gate still takes nothing from its lychee files",
        owned_invocation_from_inside,
    ),
    Assertion(89, "one large document, and openers never closed, are judged in seconds", one_large_document),
    Assertion(
        90,
        "after the write of an uncovered document, the covered links it broke are reported",
        uncovered_write_that_breaks_a_covered_link,
    ),
    Assertion(
        91, "a misspelt dial is a configuration failure, never a setting ignored in silence", a_misspelt_dial
    ),
    Assertion(
        92,
        "one break is one finding: R6 without R7, and said once for links alike on a line",
        one_break_one_finding,
    ),
    Assertion(
        93,
        "an `a name` is an explicit anchor; an escaped path is read for R7",
        anchors_by_name_and_encoded_paths,
    ),
    Assertion(94, "a byte order mark does not open the YAML block to R4", byte_order_mark_before_the_block),
    Assertion(95, "the scan's findings inside one document come in line order", scan_findings_in_line_order),
    Assertion(
        96,
        "a break of a kind the module has no text for is reported in the checker's words",
        a_break_in_words_of_lychee,
    ),
    Assertion(
        97,
        "the mover's absences: no python3 and no shared code before the guard, no PyYAML inside it",
        mover_entry_absences,
    ),
    Assertion(98, "golden reasons: the why-line of every finding, typed by hand", golden_why_lines),
    Assertion(
        99,
        "the act stopped midway: after the move alone, and after a rewrite with no move",
        midway_after_the_move_alone,
    ),
    Assertion(
        100,
        "a fence closes at its opener's depth; a tab counts; one never closed masks to the end",
        fences_close_at_their_depth,
    ),
    Assertion(
        74,
        "a footnote is no link: a bare form in it is red, a path in it is left alone",
        footnotes_are_no_links,
    ),
    Assertion(
        75,
        "labels fold case; a usage inside a link's text is none; one R7 per definition",
        labels_fold_case_and_nest,
    ),
    Assertion(76, "R4: a PATH entry and C:/Users are red; tilde paths are not", r4_more_shapes),
    Assertion(
        77,
        "a mention ends where the name does; an href is rewritten, not listed",
        a_mention_ends_where_the_name_does,
    ),
    Assertion(
        78, "after a write, an older heading link elsewhere is not repeated", older_heading_link_not_repeated
    ),
    Assertion(
        79,
        "a link checker that hangs is a configuration failure inside the hook's timeout",
        a_link_checker_that_hangs,
    ),
    Assertion(
        69,
        "the mover refuses a directory, a name that is no Markdown, a link, and no repository",
        mover_refuses_what_would_leave_coverage,
    ),
    Assertion(
        47,
        "a case-only rename is a move; a document moved out of coverage keeps its links",
        case_only_rename_and_uncovered_destination,
    ),
    Assertion(48, "local_paths: allow switches R4 off", local_paths_allowed),
    Assertion(49, "the mover routes its log to log_dir before any refusal", mover_routes_its_log),
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
    # the skip reason once a negated pattern takes `red` out of the territory, typed by hand
    outside="docs/notes/a.md is not covered (const-referencing.territories)",
    resolves_policies=False,
    bare_readme="1 document examined",
    judges_envelopes=False,
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
