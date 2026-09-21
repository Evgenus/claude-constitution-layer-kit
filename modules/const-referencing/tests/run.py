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
LINKED = f"See [{OWNER_ID}]({TO_OWNER}) and [REQ-7](../reqs.md#req-7).\n"
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
    red, _ = gate_on(Edit(DOC, "and [REQ-7](../reqs.md#req-7)", "and REQ-7"), dials_patch=LANES, files=files)
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
    tail = messages.f9_scan_tail(5, 0, 5, 1)
    green = scan_of({DOC: VALID.text}, LANES)
    return all_of(
        [
            expect(red, 2, r1().render(), "stdout"),
            expect(red, 2, second.render(), "stdout"),
            expect(red, 2, shared.f9_count_scan(2, tail), "stdout"),
            expect(green, 0, shared.g1_green_scan(messages.f9_scan_tail(4, 2, 4, 1)), "stdout"),
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
