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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from const_gate import identity
from const_gate import messages as shared
from const_gate.model import Broken, Finding
from consumer import Consumer, document
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
from referencing_gate import lychee, messages, start
from shared_items import (
    NO_ENVELOPE,
    PatternDial,
    Subject,
    git_patch,
    git_timeouts,
    no_clock,
    shared_assertions,
)

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
H = Harness(SCRIPTS, "check-references.sh", "check-references.py", start.GATE.namespace)

NAMESPACE = start.GATE.namespace
DOC = "docs/notes/a.md"
OWNER_ID = "notes-policy"  # a document of the shared consumer, carrying this id
OWNER = "docs/policies/notes-policy.md"
TO_OWNER = "../policies/notes-policy.md"
# Values over 80 characters, the echo rule's cases: a path the reader opens or types stays whole, with a
# break and a backslash shown escaped; a word that only points is cut at 80 with the cut said.
HOOK_RAW = (
    "docs/notes/w\nx\\y" + "z" * 80 + ".md"
)  # the hook reads no file: a line break may stand in the path
HOOK_SHOWN = "docs/notes/w\\nx\\\\y" + "z" * 80 + ".md"
BS_RAW = "docs/notes/w\\x" + "z" * 80 + ".md"  # a backslash only: lychee is handed its paths one to a line
BS_SHOWN = "docs/notes/w\\\\x" + "z" * 80 + ".md"
WEIRD_DIR = "w\nx\\y" + "d" * 80  # a folder name, for a root and a directory the run stands in
WEIRD_DIR_SHOWN = "w\\nx\\\\y" + "d" * 80
BS_DIR = "w\\x" + "d" * 80  # a folder with a backslash only: git quotes its path in one line
BS_DIR_SHOWN = "w\\\\x" + "d" * 80
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


def broken(result: Result, failure: Broken | str) -> tuple[bool, str]:
    """The failure as the module builds it, or, given a string, as the item typed it by hand."""
    return broken_typed(result, failure if isinstance(failure, str) else failure.render())


def broken_typed(result: Result, line: str) -> tuple[bool, str]:
    """The failure's line, typed by hand where the item types it, first; then the count line."""
    ok, evidence = broken_first_line(result, line)
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
    # A document with no YAML block has no region the checks skip: its first block, a fence, is read like the
    # rest. This case lives here, not in item 11, since what it holds is the path rule; it has no envelope, so
    # it is written whole and not through `note`. The fence opens on line 1, the path stands on line 2.
    bare = f"```sh\ncat {path}\n```\n"
    wanted = [f"RED: {DOC}:2: '{path}' is a path on one machine"]
    no_block, _ = gate_on(Write(DOC, bare), dials_patch=LANES)
    got = [line for line in red_lines(no_block.stderr) if line.startswith(f"RED: {DOC}:")]
    no_envelope = (
        got == wanted and no_block.code == 2,
        f"no YAML block: wanted exit 2 with {wanted}; got exit {no_block.code}: {got}",
    )
    return all_of(
        [*results, green, no_envelope],
        f"red in {', '.join(reds)}, and in a fence with no YAML block; not read in the YAML block",
    )


def envelope_is_masked() -> tuple[bool, str]:
    """The YAML block is where the shared helper says it stands: its first line is `---` with trailing
    whitespace aside, its closer the next such line, a line ends at a line feed, a carriage return or
    both and nowhere else, and a block no line closes runs to the end of the file. Every text holds
    `REQ-7` in the block, which no check may read, and, but for the unclosed block, once in the text
    after it, which the check must find, on the line typed here. Every line is typed by hand."""
    block = "id: note-a\ntype: non-authoritative\ntitle: About REQ-7\nstatus: active\n"  # lines 2 to 5
    tail = "\n# F\nSee REQ-7.\n"  # the blank line is 7, the reference stands on line 9 after a closer on 6
    found = f"RED: {DOC}:9: 'REQ-7' cites a requirement by a bare handle"
    unmasked = [  # no opener: nothing is masked, the title stands on line 3 and the text after the `---` on 8
        f"RED: {DOC}:3: 'REQ-7' cites a requirement by a bare handle",
        f"RED: {DOC}:8: 'REQ-7' cites a requirement by a bare handle",
    ]
    texts = {
        "exact": ("---\n" + block + "---\n" + tail, [found]),
        "an opener with a trailing space": ("--- \n" + block + "---\n" + tail, [found]),
        "a closer with a trailing space": ("---\n" + block + "--- \n" + tail, [found]),
        "a closer with a trailing tab": ("---\n" + block + "---\t\n" + tail, [found]),
        "CRLF": (("---\n" + block + "---\n" + tail).replace("\n", "\r\n"), [found]),
        "a byte order mark": ("﻿---\n" + block + "---\n" + tail, [found]),
        # The closer's line ends the block and the next line opens a fence: the fence is masked as a block,
        # the text after it is not. The fence opens on line 7, `See REQ-7.` stands in it, the reference on 10.
        "a fence on the line after the closer": (
            "---\n" + block + "---\n```\nSee REQ-7.\n```\nAfter REQ-7.\n",
            [f"RED: {DOC}:10: 'REQ-7' cites a requirement by a bare handle"],
        ),
        "no closer": ("---\n" + block + tail, []),
        "no block": (block + "---\n" + tail, unmasked),
        # A form feed breaks a line for `str.splitlines()` and for no Markdown reader: it closes nothing.
        "a form feed before the only closer": ("---\n" + block + "\x0c---\n" + tail, []),
        "a form feed before a closer, and a later one": (
            "---\n" + block + "\x0c---\n\n# F\nSee REQ-7.\n---\n\nSee REQ-7.\n",
            [f"RED: {DOC}:12: 'REQ-7' cites a requirement by a bare handle"],
        ),
    }
    for name, (text, wanted) in texts.items():
        result, _ = gate_on(Write(DOC, text), dials_patch=LANES)
        got = [line for line in red_lines(result.stderr) if line.startswith(f"RED: {DOC}:")]  # not the count
        code = 2 if wanted else 0
        if got != wanted or result.code != code:
            return False, f"{name}: wanted exit {code} with {wanted}; got exit {result.code}: {got}"
    return True, f"{len(texts)} texts: the block is masked as far as the helper says, and no further"


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
    try:  # the compiler's own words come from `re` itself, so a Python version cannot break the golden
        re.compile("REQ-([")
    except re.error as compiler:
        compiler_words = str(compiler)
    else:
        return False, "the pattern 'REQ-([' compiled; the fixture needs one the compiler refuses"
    lane_fix = (  # the fix every lane failure ends in, typed by hand
        "write the entry as {pattern: <regular expression>, names: <what the form cites>, fix: <the link"
        " form to write>}; home: [<patterns>] is optional"
    )
    wrong: list[tuple[dict[str, object], Broken | str]] = [
        (  # typed by hand
            own(territories="*.md"),
            "BROKEN: constitution.yaml: const-referencing.territories must be a non-empty list of path"
            " patterns — fix: write it as const-referencing: {territories: ['*.md']}, or remove the key:"
            " every Markdown file is then covered",
        ),
        (own(territories=[]), messages.c5_territories()),
        (own(territories=["*.md", 3]), messages.c5_territories()),
        (own(bare_ids="maybe"), messages.c5_switch("bare_ids")),
        (own(bare_ids=True), messages.c5_switch("bare_ids")),
        (own(local_paths="off"), messages.c5_switch("local_paths")),
        (  # typed by hand
            own(lanes={"pattern": "x"}),
            "BROKEN: constitution.yaml: const-referencing.lanes must be a list of lanes — fix: write it as"
            " const-referencing: {lanes: [{pattern: <regular expression>, names: <what the form cites>,"
            " fix: <the link form to write>}]}, or remove the key",
        ),
        (  # typed by hand
            own(lanes=["REQ"]),
            "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes is not a mapping of pattern,"
            f" names, fix and home — fix: {lane_fix}",
        ),
        (own(lanes=[LANE, {**LANE, "why": "mine"}]), messages.c5_lane(2, messages.lane_unknown_key("why"))),
        (  # typed by hand
            own(lanes=[dropped]),
            "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes needs fix: a non-empty string"
            f" — fix: {lane_fix}",
        ),
        (lane(names="  "), messages.c5_lane(1, messages.lane_needs("names"))),
        (lane(pattern=7), messages.c5_lane(1, messages.lane_needs("pattern"))),
        (  # typed by hand
            lane(home="docs/reqs.md"),
            "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes has a home that is not a list"
            f" of path patterns — fix: {lane_fix}",
        ),
        (
            lane(pattern="REQ-(["),
            messages.c5_lane(1, messages.lane_pattern(compiler_words)),
        ),
    ]
    results = [broken(gate_on(VALID, dials_patch=patch)[0], failure) for patch, failure in wrong]
    in_scan = H.run_gate("", args=["--scan", str(gate_on(VALID, dials_patch=own(bare_ids="maybe"))[1])])
    odd_key = broken_typed(  # a key with a line break is shown escaped: one line, typed by hand
        gate_on(VALID, dials_patch=own(lanes=[{**LANE, "a\nb": 1}]))[0],
        "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes carries the key 'a\\nb'; a lane holds"
        " pattern, names, fix and home, and nothing else — fix: write the entry as {pattern: <regular"
        " expression>, names: <what the form cites>, fix: <the link form to write>}; home: [<patterns>] is"
        " optional",
    )
    # the compiler's own words come from `re` again, for the pattern under test; they echo the pattern's
    # backslash, which the message shows escaped in turn, so the doubling is typed by hand
    odd = r"(?P<a\b>x)"
    try:
        re.compile(odd)
    except re.error as odd_compiler:
        odd_words = str(odd_compiler).replace("\\", "\\\\")
    else:
        return False, "the pattern (?P<a\\b>x) compiled; the fixture needs one the compiler refuses"
    odd_pattern = broken_typed(
        gate_on(VALID, dials_patch=lane(pattern=odd))[0],
        "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes has a pattern that is no regular"
        f" expression ({odd_words}) — in YAML write it in single"
        " quotes, where a backslash stands for itself — fix: write the entry as {pattern: <regular"
        " expression>, names: <what the form cites>, fix: <the link form to write>}; home: [<patterns>] is"
        " optional",
    )
    # the compiler's words can pass 80 characters, a group name having no limit; the diagnosis stands in
    # the line whole, never cut, so the words come from `re` again and the line around them is typed
    long_name = "a" * 100
    long = "(?P=" + long_name + ")"
    try:
        re.compile(long)
    except re.error as long_compiler:
        long_words = str(long_compiler)
    else:
        return False, "the pattern (?P=aaa...) compiled; the fixture needs one the compiler refuses"
    if len(long_words) <= 80 or long_name not in long_words:
        return False, f"the compiler's words are {len(long_words)} characters; the fixture needs more than 80"
    long_pattern = broken_typed(
        gate_on(VALID, dials_patch=lane(pattern=long))[0],
        "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes has a pattern that is no regular"
        f" expression ({long_words}) — in YAML write it in single"
        " quotes, where a backslash stands for itself — fix: write the entry as {pattern: <regular"
        " expression>, names: <what the form cites>, fix: <the link form to write>}; home: [<patterns>] is"
        " optional",
    )
    return all_of(
        [*results, broken(in_scan, messages.c5_switch("bare_ids")), odd_key, odd_pattern, long_pattern],
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
    return broken_typed(
        result,
        "BROKEN: constitution.yaml: const-referencing.lanes[1].home holds a pattern git would not read as"
        " one: '#docs' — fix: a pattern may not start with '#' (a comment to git) nor contain a line"
        " break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break",
    )


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
    odd = own(lanes=[{**LANE, "names": "a\nrequirement", "fix": "[REQ-7]\n(x\\y)"}])
    broken_lines = gate_on(CASES[0].red, dials_patch=odd)[0].stderr
    for hand_typed in (  # the lane's own words with a line break: shown escaped, the finding stays lines
        f"RED: {DOC}:9: 'REQ-7' cites a\\nrequirement by a bare handle",
        "  fix: write it as a link: [REQ-7]\\n(x\\\\y)",
    ):
        if hand_typed not in broken_lines:
            missing.append(hand_typed)
    # the document's path is the reader's to open, and the lane's fix the text the reader copies: both whole,
    # a break and a backslash escaped, over 80 characters; the lane's `names` and the match only point: cut
    wide_lanes = own(
        lanes=[
            {**LANE, "names": "a\nrequirement" + "n" * 90, "fix": "[REQ-7]\n(x\\y" + "z" * 130 + ")"},
            {**LANE, "pattern": r"\bLONG-[0-9]+\b", "names": "a long one"},
        ]
    )
    wide = gate_on(wrote(body("See REQ-7 and LONG-" + "7" * 100 + "."), HOOK_RAW), dials_patch=wide_lanes)[0]
    for hand_typed in (
        f"RED: {HOOK_SHOWN}:9: 'REQ-7' cites a\\nrequirement"
        + "n" * 67
        + "… [103 characters] by a bare handle",
        "  fix: write it as a link: [REQ-7]\\n(x\\\\y" + "z" * 130 + ")",
        f"RED: {HOOK_SHOWN}:9: 'LONG-" + "7" * 75 + "… [105 characters]' cites a long one by a bare handle",
    ):
        if hand_typed not in wide.stderr.splitlines():
            missing.append(hand_typed)
    outside = gate_on(Write(HOOK_RAW, note("# F\n")), dials_patch=claim(["docs/policies/**"]))[0].stdout
    if f"{HOOK_SHOWN} is not covered (const-referencing.territories)" not in outside:
        missing.append("skip of a path over 80 characters")
    return not missing, f"{len(GOLDEN) + 7} literal lines found" if not missing else f"not found: {missing}"


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


def path_with_unstartable_lychee() -> dict[str, str]:
    """An executable lychee whose interpreter line names no program: found on PATH, raises OSError."""
    env = path_with(None)
    (Path(env["PATH"]) / "lychee").write_text("#!/no/such/interpreter\n")
    (Path(env["PATH"]) / "lychee").chmod(0o755)
    return env


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
            broken(scan_with(path_with_unstartable_lychee()), messages.x2_lychee_too_old("0.24.2", "")),
            broken(
                scan_with(path_with(usage)), messages.x3_no_report("exit 2", "error: unexpected argument")
            ),
            # lychee's version output is several lines with a backslash: it only points, cut at 80, escaped
            broken_typed(
                scan_with(path_with("printf 'lychee 0.23.0\\nline\\\\two " + "w" * 90 + "\\n'\n")),
                "BROKEN: const-referencing needs lychee 0.24.2 or newer, found 'lychee 0.23.0\\nline\\\\two "
                + "w" * 57
                + "… [113 characters]' — fix: install a current one (https://lychee.cli.rs/installation/),"
                " then run the scan — until then no reference is checked for resolving",
            ),
            # its first line of stderr is the diagnosis the fix asks to be reported: whole, escaped
            broken_typed(
                scan_with(
                    path_with(
                        'case "$1" in --version) echo "lychee 0.24.2";;'
                        " *) printf '%s\\n' 'error: a\\b " + "e" * 90 + "' >&2; exit 2;; esac\n"
                    )
                ),
                "BROKEN: lychee gave no report: exit 2 (error: a\\\\b "
                + "e" * 90
                + ") — fix: this is a defect"
                " of the gate's invocation or of the installed lychee, not of the repository; run lychee"
                " --version and report both to whoever maintains the plugin — until then no reference is"
                " checked for resolving",
            ),
        ],
        "below the floor, a version nobody can read, a binary that cannot be started, and exit 2 with no"
        " report: each exit 1, never a finding",
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


def governed_only_policy_unreadable() -> tuple[bool, str]:
    """Under governed_only the gate reads the policies: a file where they live that nobody can read
    is C12.10 at the write, never a policy with no id and a verdict computed without it."""
    if os.geteuid() == 0:
        return (
            True,
            "NOT EXERCISED: running as root, where a mode bit does not deny a read — 0 files examined",
        )
    policy = "docs/policies/zz-unreadable.md"
    # a document no readable policy governs: the one verdict a policy with no id would leave standing
    loose = Write(LOOSE, note(body("No links."), "note-l"))
    _, root = gate_on(loose, own(governed_only=True), files={policy: NO_ENVELOPE})
    mode = (root / policy).stat().st_mode
    (root / policy).chmod(0o000)
    try:
        result = H.run_gate(event_json(root, loose))
    finally:
        (root / policy).chmod(mode)
    line = (
        f"BROKEN: {policy} is listed by git but cannot be read — fix: check that the file can be read: its"
        " permissions, or a link that leads nowhere"
    )
    ok, evidence = broken_first_line(result, line)
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


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
    failure = (  # typed by hand
        "BROKEN: constitution.yaml: const-referencing.governed_only is set and no root_policy is named, so"
        " nobody can say which documents a policy governs — fix: name the root policy, or remove"
        " governed_only"
    )
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
    mention_fix = (  # the fix every mention failure ends in, typed by hand
        "write the entry as {pattern: <regular expression whose whole match is a document's id>};"
        " files: [<patterns>] is optional"
    )
    wrong: list[tuple[dict[str, object], Broken | str]] = [
        (  # typed by hand
            own(governed_only="yes"),
            "BROKEN: constitution.yaml: const-referencing.governed_only must be true or false — fix: write"
            " governed_only: true to cover only documents a policy governs, or remove the key",
        ),
        (own(heading_anchors="sometimes"), messages.c5_switch("heading_anchors")),
        (  # typed by hand
            own(mentions={"pattern": "x"}),
            "BROKEN: constitution.yaml: const-referencing.mentions must be a list of mention patterns —"
            " fix: write it as const-referencing: {mentions: [{pattern: <regular expression whose whole"
            " match is a document's id>}]}, or remove the key",
        ),
        (  # typed by hand
            own(mentions=["note"]),
            "BROKEN: constitution.yaml: entry 1 of const-referencing.mentions is not a mapping of pattern"
            f" and files — fix: {mention_fix}",
        ),
        (
            own(mentions=[{**MENTION, "names": "x"}]),
            messages.c5_mention(1, messages.mention_unknown_key("names")),
        ),
        (own(mentions=[{"files": ["src/**"]}]), messages.c5_mention(1, messages.lane_needs("pattern"))),
        (  # typed by hand
            own(mentions=[{**MENTION, "files": "src"}]),
            "BROKEN: constitution.yaml: entry 1 of const-referencing.mentions has files that is not a list"
            f" of path patterns — fix: {mention_fix}",
        ),
        (own(mentions=[{"pattern": "note-("}]), messages.c5_mention(1, unclosed)),
    ]
    results = [broken(gate_on(VALID, dials_patch=patch)[0], failure) for patch, failure in wrong]
    odd_key = broken_typed(  # a key with a line break is shown escaped: one line, typed by hand
        gate_on(VALID, dials_patch=own(mentions=[{**MENTION, "a\nb": 1}]))[0],
        "BROKEN: constitution.yaml: entry 1 of const-referencing.mentions carries the key 'a\\nb'; a mention"
        " holds pattern and files, and nothing else — fix: write the entry as {pattern: <regular expression"
        " whose whole match is a document's id>}; files: [<patterns>] is optional",
    )
    return all_of([*results, odd_key], f"{len(wrong)} malformed dials, each exit 1")


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
            # the count line is what a later step reads: the path whole, escaped, over 80 characters
            expect(
                after_write(BS_RAW, {TARGET: TARGET_TEXT, BS_RAW: source("See [x](gone.md).")}),
                2,
                f"RED: 1 link(s) of the whole tree examined, 1 finding(s) involve {BS_SHOWN}",
                "stderr",
            ),
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
    odd = broken_typed(  # a name holding a line break stays on one line, the break shown escaped
        after_write(SOURCE, files, event="Notif\nication"),
        "BROKEN: hook input names the event 'Notif\\nication', which this gate is not wired to — fix: wire"
        " the gate to PreToolUse and PostToolUse on Write|Edit, as the plugin's hooks file does; to check a"
        " repository by hand run it with --scan [<dir>]",
    )
    return all_of(
        [
            broken(after_write(SOURCE, files, event="Notification"), messages.c12_event("Notification")),
            odd,
        ],
        "an event the gate is not wired to is a configuration failure, a line break in its name escaped",
    )


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


def mover(consumer: Consumer, *arguments: str, cwd: str = "", env: dict[str, str] | None = None) -> Result:
    merged = {key: value for key, value in os.environ.items() if key != "CLAUDE_PLUGIN_DATA"}
    merged.update(env or {})
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
    patch, log = git_patch(H)  # the mover is an act: none of its git calls carries a clock
    done = mover(acted, "notes/one.md", "moved/deep/first.md", cwd="docs", env=patch)
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
        no_clock(git_timeouts(log)),
    ]
    return all_of(
        checks,
        "git mv alone leaves the scan red; the act leaves it green, fragments and code untouched, and no"
        " git call of the mover has a clock",
    )


def mentions_are_listed_not_changed() -> tuple[bool, str]:
    acted = moving_consumer()
    done = mover(acted, OLD, NEW)
    script = (acted.root / "tools/x.sh").read_text()
    # a Markdown file outside coverage is a text file git lists: read, by either name, like a script
    outside = moving_consumer()
    outside.write("constitution.yaml", dials_text(own(territories=["docs/**"])))
    outside.write("other/readme.md", f"# Readme\nSee {OLD}.\nOr ../{OLD}.\n")
    outside.write("tools/y.sh", f"cat ../{OLD}\n")
    outside.commit()
    listed = mover(outside, OLD, NEW)
    return all_of(
        [
            expect(done, 0, "MENTION: docs/notes/two.md:11: ", "stdout"),
            expect(
                done, 0, f"MENTION: tools/x.sh:1: '# see {OLD}' names the old path outside a link", "stdout"
            ),
            (script == f"# see {OLD}\n", "the script was not rewritten"),
            expect(listed, 0, f"MENTION: other/readme.md:2: 'See {OLD}.' names the old path", "stdout"),
            expect(listed, 0, f"MENTION: other/readme.md:3: 'Or ../{OLD}.' names the old path", "stdout"),
            expect(listed, 0, f"MENTION: tools/y.sh:1: 'cat ../{OLD}' names the old path", "stdout"),
            (
                (outside.root / "other/readme.md").read_text() == f"# Readme\nSee {OLD}.\nOr ../{OLD}.\n",
                "the uncovered Markdown file was not rewritten",
            ),
        ],
        "a sentence, a code span, a script and a Markdown file outside coverage naming the old path"
        " are listed; none is changed",
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
    # a path the reader opens is whole, escaped; an argument that only says which one is wrong is cut at 80
    odd = moving_consumer()
    odd.write(HOOK_RAW, note("# W\n", "note-w"))
    odd.commit()
    odd_before = tree_state(odd)
    moved_to = "docs/m\\nx\\\\y" + "m" * 80 + ".md"  # the new path, never made: whole
    typed = [
        (
            mover(odd, "docs/notes/n\nx\\y" + "n" * 80 + ".md", NEW),
            "BROKEN: docs/notes/n\\nx\\\\y"
            + "n" * 80
            + ".md is not a file git lists — fix: name a file of this"
            " repository, by its path from where you stand",
        ),
        (
            mover(odd, OLD, HOOK_RAW),
            f"BROKEN: {HOOK_SHOWN} already exists — fix: choose a path that is free, or move what lies there"
            " first",
        ),
        (
            mover(odd, HOOK_RAW, HOOK_RAW),
            f"BROKEN: {HOOK_SHOWN} would move onto itself — fix: name two different paths",
        ),
        (
            mover(odd, "--moved", HOOK_RAW, "docs/m\nx\\y" + "m" * 80 + ".md"),
            f"BROKEN: --moved says the move was made by hand, yet {HOOK_SHOWN} still exists or {moved_to}"
            " does not — fix: to make the move and repair the links in one act, run it without --moved",
        ),
        (
            mover(odd, OLD, "../q\nr\\s" + "o" * 90),
            "BROKEN: ../q\\nr\\\\s" + "o" * 72 + "… [98 characters] lies outside the repository — fix: name a"
            " path inside it",
        ),
        (
            mover(odd, "--zz\nz\\" + "u" * 90),
            "BROKEN: misinvocation: unrecognized arguments: --zz\\nz\\\\"
            + "u" * 49
            + "… [121 characters] — fix:"
            " run it with <old path> <new path> to move a file and repair the links; --moved <old path> <new"
            " path> after a move made by hand; --ids to point every link whose text is a document's id at"
            " that document",
        ),
    ]
    odd_lines = [broken_first_line(result, line) for result, line in typed]
    odd_unchanged = (tree_state(odd) == odd_before, "a refusal of a long path changed the tree")
    return all_of(
        [*results, *closing, unchanged, *odd_lines, odd_unchanged],
        f"{len(refused) + len(typed)} refusals, each exit 1, the tree as it was",
    )


def mover_without_dials() -> tuple[bool, str]:
    consumer = moving_consumer()
    (consumer.root / "constitution.yaml").unlink()
    result = mover(consumer, OLD, NEW)
    ok, evidence = broken_first_line(result, messages.v5_no_dials(str(consumer.root)).render())
    # the root is a path the reader goes to: whole, escaped, over 80 characters
    parent = H.scratch_dir()
    odd = Consumer(parent / WEIRD_DIR).build()
    odd.write(OLD, ONE)
    odd.commit()
    (odd.root / "constitution.yaml").unlink()
    odd_ok, odd_evidence = broken_first_line(
        mover(odd, OLD, NEW),
        f"BROKEN: no constitution.yaml in {parent}/{WEIRD_DIR_SHOWN}: the check that proves a move cannot run"
        " — fix: create constitution.yaml at the repository's top — an empty mapping, {}, is enough",
    )
    return ok and odd_ok and (consumer.root / OLD).exists(), evidence if not ok else odd_evidence


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
    # paths over 80 characters with a backslash: every path whole, escaped; the line that only points at
    # a mention is cut at 80 with the cut said
    odd = moving_consumer()
    odd.write(BS_RAW, note(body("See [o](one.md)."), "note-w"))
    odd_script = "tools/w\\x" + "t" * 80 + ".sh"
    odd.write(odd_script, "# see " + OLD + " a\\b " + "t" * 90 + "\n")
    odd.commit()
    odd_out = mover(odd, BS_RAW, "docs/notes/n\\x" + "n" * 80 + ".md").stdout.splitlines()
    moved = mover(odd, OLD, NEW).stdout.splitlines()
    for hand_typed in (
        f"MOVED: {BS_SHOWN} → docs/notes/n\\\\x" + "n" * 80 + ".md",
        "REWROTE: docs/notes/n\\\\x" + "n" * 80 + ".md: 1 link(s)",
    ):
        if hand_typed not in odd_out + moved:
            missing.append(hand_typed)
    mention = (
        "MENTION: tools/w\\\\x"
        + "t" * 80
        + ".sh:1: '# see docs/notes/one.md a\\\\b "
        + "t" * 52
        + "… [118 characters]' names the old path outside a link — read it and decide; nothing was changed"
    )
    if mention not in moved:
        missing.append(mention)
    return (
        not missing,
        f"{len(GOLDEN_MOVER) + 5} literal lines found" if not missing else f"not found: {missing}",
    )


# ------------------------------------------------------------------ the plugin's other parts

PLUGIN = SCRIPTS.parent
CHAT_RULE = (
    "const-referencing (advisory): in chat, write every reference to a file, a section or a document as a"
    " markdown link wherever the file exists. A number, letter or key is a handle local to its message,"
    " decision or session: when a cite crosses that boundary, name the message or decision it came from.\n"
)


# Seconds a handler keeps beyond its waits, for the interpreter's start and for git while git is quick: no
# bound on git. Several shared git calls, each under their 3 s, can pass them, and under governed_only the
# policy index read (build_index) stands outside both budgets too (limit 16 of shared/GATE.md §4). The
# module's own reading and masking of the tree are inside HOOK_SECONDS, one budget with the run; the
# version probe has VERSION_SECONDS of its own, before it.
LEFT_FOR_THE_REST = 5


def hooks_file() -> tuple[bool, str]:
    """Three handlers, each in the exec form with an explicit timeout; both tool events run the
    gate's one entry point, which tells them apart by the event's name. A tool handler's timeout
    holds what its check after a write waits on, one wait after the other (the version probe, then
    the run), and LEFT_FOR_THE_REST; the session-start printer runs no child process."""
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
    gate = ["${CLAUDE_PLUGIN_ROOT}/scripts/check-references.sh"]
    wanted = {
        "PreToolUse": ("Write|Edit", gate),
        "PostToolUse": ("Write|Edit", gate),
        "SessionStart": (None, ["${CLAUDE_PLUGIN_ROOT}/scripts/print-chat-rule.sh"]),
    }
    waits = {
        "PreToolUse": lychee.VERSION_SECONDS + lychee.HOOK_SECONDS,
        "PostToolUse": lychee.VERSION_SECONDS + lychee.HOOK_SECONDS,
        "SessionStart": 0,
    }
    problems = [name for name in wanted if name not in hooks] + [name for name in hooks if name not in wanted]
    tied: list[str] = []
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
            elif waits[name]:
                needed = waits[name] + LEFT_FOR_THE_REST
                if handler["timeout"] < needed:
                    problems.append(
                        f"{name}: timeout {handler['timeout']} s is under the {needed} s it needs:"
                        f" version probe {lychee.VERSION_SECONDS} s + run {lychee.HOOK_SECONDS} s"
                        f" + {LEFT_FOR_THE_REST} s left"
                    )
                else:
                    tied.append(f"{name} {handler['timeout']} s >= {needed} s")
    return not problems, (
        "three handlers, exec form, scripts present, timeouts that hold the waits: " + ", ".join(tied)
        if not problems
        else str(problems)
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
            broken_first_line(  # typed by hand
                refused,
                "BROKEN: const-referencing.governed_only is set and constitution.yaml names no root_policy,"
                " so nobody can say which documents a move must repair — fix: name the root policy, or"
                " remove governed_only",
            ),
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
    stopped = (  # typed by hand
        "BROKEN: the act stopped midway — what the lines above name was moved or rewritten, and the check"
        " of the whole tree has not run: look at git status, repair the cause, then run the scan"
    )
    ok = (
        done.returncode == 1
        and stopped in done.stderr
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
    odd_latin = (
        "docs/notes/l\\y" + "n" * 80 + ".md"
    )  # a path over 80 characters with a backslash: named whole
    (consumer.root / odd_latin).write_bytes("# Caf\xe9\n\nSee [one](one.md).\n".encode("latin-1"))
    consumer.commit()
    done = mover(consumer, OLD, NEW)
    after = (consumer.root / "docs/notes/crlf.md").read_bytes().decode("utf-8")
    latin = (consumer.root / "docs/notes/latin.md").read_bytes()
    return all_of(
        [
            (after == crlf.replace("one.md", "../moved/deep/first.md"), f"CRLF document: {after!r}"),
            (b"Caf\xe9" in latin and b"(one.md)" in latin, "the latin-1 file was rewritten"),
            (messages.v2_left_alone("docs/notes/latin.md") in done.stdout, done.stdout),
            (
                "LEFT ALONE: docs/notes/l\\\\y"
                + "n" * 80
                + ".md is not UTF-8 text — its links, if any, were not"
                " repaired" in done.stdout.splitlines(),
                done.stdout,
            ),
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
    # the path under a file, and git's own line naming the repository, are whole, escaped, over 80 characters
    odd = moving_consumer()
    odd.write(HOOK_RAW, note("# W\n", "note-w"))
    odd.commit()
    under_odd = mover(odd, OLD, HOOK_RAW + "/inside.md")
    parent = H.scratch_dir()
    in_folder = Consumer(parent / BS_DIR).build()
    in_folder.write(OLD, ONE)
    in_folder.commit()
    (in_folder.root / ".git" / "index.lock").write_text("")
    locked_odd = mover(in_folder, OLD, "brand/new/dir/first.md")
    return all_of(
        [
            broken_first_line(
                under_odd,
                f"BROKEN: {HOOK_SHOWN} is a file, so nothing can lie inside it — fix: name a new path whose"
                " directories exist or can be made",
            ),
            broken_first_line(
                locked_odd,
                f"BROKEN: git mv refused: fatal: Unable to create '{parent}/{BS_DIR_SHOWN}/.git/index.lock':"
                " File exists. — fix: repair what git names, then run the move again",
            ),
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
    result, _ = gate_on(VALID, dials_patch=own(heading_anchor="allow"))
    return broken_typed(
        result,
        "BROKEN: constitution.yaml: const-referencing.heading_anchor is no dial of this module — fix: a"
        " misspelt dial would be ignored in silence, so none is: write one of bare_ids, governed_only,"
        " heading_anchors, lanes, local_paths, log_dir, mentions, severity, territories",
    )


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
    plain = _lychee_words("Some new failure")
    odd = _lychee_words("Some\nnew failure\\ " + "w" * 90, "x\\y" + "n" * 100 + ".md")  # both only point: cut
    return all_of(
        [
            expect(
                plain,
                2,
                messages.r5_unresolved(SOURCE, LINE, "/nowhere/x.md", "Some new failure").render(),
                "stdout",
            ),
            expect(
                odd,
                2,
                f"RED: {SOURCE}:{LINE}: link target /nowhere/x\\\\y"
                + "n" * 68
                + "… [115 characters] does not"
                " resolve: Some\\nnew failure\\\\ " + "w" * 62 + "… [108 characters]",
                "stdout",
            ),
        ],
        "a break in the checker's words, shown as it said, cut when long, on one line",
    )


def _lychee_words(text: str, name: str = "x.md") -> Result:
    report = json.dumps(
        {
            "error_map": {
                "SRC": [
                    {
                        "url": f"file:///nowhere/{name}",
                        "status": {"text": text},
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
    return result


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
        [
            *results,
            passes(body("Mine: ~/Users/x/y and ~/home/ann/z.")),
            passes(body("A user's directory alone is a route: C:/Users/ann and C:\\Users\\ann\\ are one.")),
        ],
        "a PATH entry and C:/Users/ann/x are red; C:/Users/ann alone and tilde paths of any depth are not",
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


# typed by hand: the first line of a check after a write that waited its 20 s for lychee, then the count line
TOO_SLOW_TYPED = (
    "BROKEN: lychee gave no report within the 20 s a check after a write waits, the tree's reading and"
    " masking counted — fix: a large tree can take lychee longer than that; run the scan, which waits"
    " for lychee as long as it takes — until then no reference is checked for resolving"
)
# typed by hand: the first line when lychee is missing, and when it is too old to be used
X1_TYPED = (
    "BROKEN: const-referencing needs lychee 0.24.2 or newer and found none on PATH — fix: install it"
    " (https://lychee.cli.rs/installation/), then run the scan — until then no reference is checked for"
    " resolving"
)
X2_TYPED = (
    "BROKEN: const-referencing needs lychee 0.24.2 or newer, found 'lychee 0.23.0' — fix: install a"
    " current one (https://lychee.cli.rs/installation/), then run the scan — until then no reference is"
    " checked for resolving"
)
# typed by hand: the first line of a check after a write whose 20 s went on the tree before lychee ran
OUT_OF_TIME_TYPED = (
    "BROKEN: the check after a write used its 20 s reading and masking the tree before lychee could run"
    " — fix: a large tree takes longer than that to read; run the scan, which waits as long as it takes"
    " — until then no reference is checked for resolving"
)

# A run of the real entry point, `start.main`, with the budget's clock stood still and moved by hand: it
# advances by the seconds the environment names for the file list, for the territory matching, for each
# document read, each masked, once more at the first masking, and once at the version probe. Nothing waits
# for real. The trace holds one word per read and per masking, and what lychee's run was given as its
# timeout, with the clock then.
BUDGET_DRIVER = """\
import os
import subprocess
import sys

sys.path.insert(0, {scripts!r})
from referencing_gate import lychee, modes, start, tree

now = [0.0]
extra = [float(os.environ.get("MASK_FIRST", "0"))]
trace = open(os.environ["TRACE"], "a")


def note(text):
    trace.write(text + "\\n")
    trace.flush()


def reading(*args):
    now[0] += float(os.environ.get("READ_STEP", "0"))
    note("read")
    return read(*args)


def masking(text):
    now[0] += float(os.environ.get("MASK_STEP", "0")) + extra[0]
    extra[0] = 0.0
    note("mask")
    return mask(text)


def spy(command, *args, **kwargs):
    if os.path.basename(str(command[0])) == "lychee" and command[1] == "--version":
        now[0] += float(os.environ.get("PROBE_STEP", "0"))
    elif os.path.basename(str(command[0])) == "lychee":
        note("run timeout=%r clock=%r" % (kwargs.get("timeout"), now[0]))
    return run(command, *args, **kwargs)


def listing(*args):
    now[0] += float(os.environ.get("LIST_STEP", "0"))
    return listed(*args)


def matching(*args, **kwargs):
    now[0] += float(os.environ.get("MATCH_STEP", "0"))
    return matched(*args, **kwargs)


read, mask, run = modes.read_text, tree.mask, subprocess.run
listed, matched = modes.list_markdown, modes.covered_documents
lychee.monotonic = lambda: now[0]
modes.read_text, tree.mask, subprocess.run = reading, masking, spy
modes.list_markdown, modes.covered_documents = listing, matching
sys.exit(start.main(sys.argv[1:]))
"""
BUDGET_LYCHEE = (  # logs the first argument of each call; says its version, then an empty report or nothing
    'echo "$1" >> "$LYCHEE_LOG"\ncase "$1" in --version) echo \'{version}\';; *) {run};; esac\n'
)


def on_a_patched_clock(
    clock: dict[str, str],
    run: str = "echo '{\"error_map\": {}}'",
    scan: bool = False,
    version: str | None = "lychee 0.24.2",
) -> tuple[Result, list[str], list[str], float, int]:
    """The check after a write (or the scan) of a tree of documents, run through the entry point with
    the clock patched as `clock` says (the seconds, as LIST_STEP, MATCH_STEP, MASK_FIRST, MASK_STEP, READ_STEP
    and PROBE_STEP). `version` is what the fake lychee says to --version, None for no lychee on PATH. Gives
    the result, the trace, the fake lychee's own log of its calls, the real seconds it took, and the
    number of documents the tree holds."""
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text())
    consumer.write(TARGET, TARGET_TEXT)
    consumer.write(SOURCE, source("See [x](t.md)."))
    documents = sum(1 for found in consumer.root.rglob("*.md") if ".git" not in found.parts)
    scratch = H.scratch_dir()
    (scratch / "driver.py").write_text(BUDGET_DRIVER.format(scripts=str(SCRIPTS)))
    env = {
        **path_with(None if version is None else BUDGET_LYCHEE.format(run=run, version=version)),
        "TRACE": str(scratch / "trace"),
        "LYCHEE_LOG": str(scratch / "lychee"),
        **clock,
    }
    stdin = "" if scan else event_json(consumer.root, Write(SOURCE, source("See [x](t.md).")), event=AFTER)
    began = time.monotonic()
    result = H.run_gate(
        stdin,
        args=["--scan", str(consumer.root)] if scan else [],
        env=env,
        command=[sys.executable, str(scratch / "driver.py")],
    )
    took = time.monotonic() - began
    lines = [
        (scratch / name).read_text().splitlines() if (scratch / name).exists() else []
        for name in ("trace", "lychee")
    ]
    return result, lines[0], lines[1], took, documents


def the_budget_is_one() -> list[tuple[bool, str]]:
    """The check after a write has one deadline for the reads, the masking and lychee's run; the scan
    has none. Every case moves a patched clock by the document: the longest real wait is half a second.
    The order of two configuration failures is held here too: with a missing lychee and a document that
    cannot be read, the check after a write says X1 and the scan says C12.10."""
    results: list[tuple[bool, str]] = []
    # masking, document by document, passes the deadline at the last of them: no run, and one probe,
    # made before the budget began
    count = on_a_patched_clock({})[4]
    each = 20 / (count - 0.5)
    late, trace, ran, _, _ = on_a_patched_clock({"MASK_STEP": repr(each)})
    results.append(broken_typed(late, OUT_OF_TIME_TYPED))
    results.append(
        (
            trace.count("mask") == count and trace.count("read") == count and ran == ["--version"],
            f"{count} documents read and masked, lychee called: {ran}; trace {trace}",
        )
    )
    # the first of several documents masked passes it: the clock is read after each document, so the
    # check stops there and the other documents are never masked
    first, trace, ran, _, _ = on_a_patched_clock({"MASK_FIRST": "25"})
    results.append(broken_typed(first, OUT_OF_TIME_TYPED))
    results.append(
        (
            count > 1 and trace.count("mask") == 1 and trace.count("read") == count and ran == ["--version"],
            f"{count} documents read, one masked, lychee probed and never run: trace {trace}, lychee {ran}",
        )
    )
    # a read passes it before any masking starts (reading is counted)
    late, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"})
    results.append(broken_typed(late, OUT_OF_TIME_TYPED))
    results.append(
        (
            trace == ["read"] and ran == ["--version"],
            f"one read and no masking, lychee probed and never run: trace {trace}, lychee {ran}",
        )
    )
    # the run is given what the reads and the masking left, never more than the budget
    spent = 9.0
    done, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": repr(3 / count), "MASK_STEP": repr(6 / count)})
    given = [line for line in trace if line.startswith("run ")]
    timeout, clock = (float(part.split("=")[1]) for part in given[0].split()[1:]) if given else (-1.0, 0.0)
    results.append(
        (
            done.code == 0
            and len(given) == 1
            and abs(clock - spent) < 1e-6
            and timeout == 20.0 - clock
            and 0 < timeout <= 20,
            f"exit {done.code}, the run was given {timeout!r} s with the clock at {clock!r}: {trace}",
        )
    )
    # lychee's run times out with 0.5 s left: the line names the whole budget, not the half second
    hung, trace, ran, took, _ = on_a_patched_clock(
        {"MASK_FIRST": "19.5"}, run=f"exec {shutil.which('sleep') or '/bin/sleep'} 30"
    )
    results.append(broken_typed(hung, TOO_SLOW_TYPED))
    results.append(
        (
            "run timeout=0.5 clock=19.5" in trace and took < 6,
            f"the run was given 0.5 s and ended after {took:.1f} s: {trace}",
        )
    )
    # the reads and the masking leave 0.005 s, the deadline not yet passed: the run is given the floor,
    # 0.01 s, never less; its timeout is the only place the floor shows
    near, trace, ran, _, _ = on_a_patched_clock(
        {"MASK_FIRST": "19.995"}, run=f"exec {shutil.which('sleep') or '/bin/sleep'} 30"
    )
    results.append(broken_typed(near, TOO_SLOW_TYPED))
    results.append(
        (
            "run timeout=0.01 clock=19.995" in trace,  # the fake's own log is a race with the kill
            f"the run was given 0.01 s with 0.005 s left: trace {trace}",
        )
    )
    # the version probe has its own seconds, before the budget begins: a probe that takes 25 s of the
    # patched clock leaves the run what the reads and the masking left of the whole 20 s
    probed, trace, ran, _, _ = on_a_patched_clock(
        {"PROBE_STEP": "25", "READ_STEP": repr(3 / count), "MASK_STEP": repr(6 / count)}
    )
    given = [line for line in trace if line.startswith("run ")]
    timeout, clock = (float(part.split("=")[1]) for part in given[0].split()[1:]) if given else (-1.0, 0.0)
    results.append(
        (
            probed.code == 0
            and ran == ["--version", "--offline"]
            and abs(clock - 34.0) < 1e-6
            and abs(timeout - 11.0) < 1e-6,
            f"exit {probed.code}, one probe, then the run was given {timeout!r} s with the clock at"
            f" {clock!r}: {trace}, lychee {ran}",
        )
    )
    # lychee is missing or too old: whatever the tree's size and however the reads spend the budget,
    # the failure is the checker's own, X1 or X2, found before the first document is read
    no_lychee, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"}, version=None)
    results.append(broken_typed(no_lychee, X1_TYPED))
    results.append((trace == [] and ran == [], f"nothing read, no lychee: trace {trace}, lychee {ran}"))
    old, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"}, version="lychee 0.23.0")
    results.append(broken_typed(old, X2_TYPED))
    results.append(
        (trace == [] and ran == ["--version"], f"nothing read, one probe: trace {trace}, lychee {ran}")
    )
    # a document nobody can read and no lychee together: the check after a write finds the checker before
    # it reads anything and says X1, the scan reads the texts first and says C12.10; the same tree with
    # the document readable says X1 in both, so the missing lychee is real in the scan too
    if os.geteuid() == 0:
        results.append(
            (
                True,
                "NOT EXERCISED: running as root, where a mode bit does not deny a read, so the order of a"
                " missing lychee and an unreadable document is not pinned — 3 results skipped",
            )
        )
    else:
        both = H.fresh_consumer()
        both.write("constitution.yaml", dials_text())
        both.write(TARGET, TARGET_TEXT)
        both.write(SOURCE, source("See [x](t.md)."))
        shut = "docs/notes/zz-unreadable.md"
        both.write(shut, note("# Shut\n", "note-z"))
        both.commit()
        (both.root / shut).chmod(0o000)
        try:
            hooked = H.run_gate(
                event_json(both.root, Write(SOURCE, source("See [x](t.md).")), event=AFTER),
                env=path_with(None),
            )
            scanned = H.run_gate("", args=["--scan", str(both.root)], env=path_with(None))
        finally:
            (both.root / shut).chmod(0o644)
        readable = H.run_gate("", args=["--scan", str(both.root)], env=path_with(None))
        unreadable_typed = (  # typed by hand: a scan's first line for a file git lists and nobody reads
            f"BROKEN: {shut} is listed by git but cannot be read — fix: check that the file can be read: its"
            " permissions, or a link that leads nowhere"
        )
        results.append(broken_typed(hooked, X1_TYPED))
        results.append(broken_typed(scanned, unreadable_typed))
        results.append(broken_typed(readable, X1_TYPED))
    # the file list and the territory matching, which stand before the budget, take 25 s of the clock
    # each: the check still reads, masks and runs, the whole 20 s its own
    for step in ("LIST_STEP", "MATCH_STEP"):
        slow, trace, ran, _, _ = on_a_patched_clock({step: "25"})
        given = [line for line in trace if line.startswith("run ")]
        results.append(
            (
                slow.code == 0
                and trace.count("read") == count
                and trace.count("mask") == count
                and given == ["run timeout=20.0 clock=25.0"],
                f"{step}: exit {slow.code}, {count} documents read and masked, the run: {given}",
            )
        )
    # the scan has no clock: a patched one that runs far away changes nothing, and the run has no timeout
    scanned, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "1000", "MASK_STEP": "1000"}, scan=True)
    far = [line for line in trace if line.startswith("run timeout=None clock=")]
    results.append(
        (
            scanned.code == 0
            and scanned.stderr == ""
            and ran.count("--version") == 1
            and len(far) == 1
            and float(far[0].rsplit("=", 1)[1]) > 20 * count,
            f"exit {scanned.code}: {scanned.stderr[:200]}; trace {trace}",
        )
    )
    return results


def a_link_checker_that_hangs() -> tuple[bool, str]:
    """A checker that never answers is a configuration failure inside the hook's timeout, never
    a hook the platform gives up on: the version probe and the run have a budget each. The run's
    budget belongs to the check after a write, and it is one budget with the reading and the masking
    of the tree (`the_budget_is_one`): the scan waits for a slow checker, as long as it takes.
    The three runs go side by side, the longest about 21 s, and the budget cases follow one after the
    other: the item costs about 30 s."""
    sleep = shutil.which("sleep") or "/bin/sleep"  # the fake's PATH holds no sleep
    slow_version = f'case "$1" in --version) {sleep} 8; echo "lychee 0.24.2";; *) exit 0;; esac\n'
    # answers --version at once; any other call is 1 s past the hook's 20 s, then an empty report
    report = '{"error_map": {}}'
    slow_run = f"case \"$1\" in --version) echo 'lychee 0.24.2';; *) {sleep} 21; echo '{report}';; esac\n"
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    in_the_scan, in_the_hook = H.fresh_consumer(), H.fresh_consumer()
    for tree in (in_the_scan, in_the_hook):
        tree.write("constitution.yaml", dials_text())
        tree.write(TARGET, TARGET_TEXT)
        tree.write(SOURCE, source("See [x](t.md)."))
    event = event_json(in_the_hook.root, Write(SOURCE, source("See [x](t.md).")), event=AFTER)

    def timed(stdin: str, args: list[str], script: str) -> tuple[Result, float]:
        began = time.monotonic()
        return H.run_gate(stdin, args=args, env=path_with(script)), time.monotonic() - began

    with ThreadPoolExecutor(max_workers=3) as pool:
        probe = pool.submit(timed, "", ["--scan", str(consumer.root)], slow_version)
        scanned = pool.submit(timed, "", ["--scan", str(in_the_scan.root)], slow_run)
        hooked = pool.submit(timed, event, [], slow_run)
    result, took = probe.result()
    scan, scan_took = scanned.result()
    hook, hook_took = hooked.result()
    # typed by hand: the first line for a version probe that gave no answer in its 5 s, then the count line
    probe_typed = (
        "BROKEN: lychee gave no report: no answer in 5 s — fix: this is a defect of the gate's invocation"
        " or of the installed lychee, not of the repository; run lychee --version and report both to"
        " whoever maintains the plugin — until then no reference is checked for resolving"
    )
    on_the_version = broken_typed(result, probe_typed)
    hand_typed = TOO_SLOW_TYPED
    return all_of(
        [
            *the_budget_is_one(),
            (
                on_the_version[0] and result.code == 1 and 4 < took < 8,
                f"the version: exit {result.code} after {took:.1f} s: {on_the_version[1]}",
            ),
            expect(scan, 0, shared.g1_green_scan(messages.f9_scan_tail(5, 1, 5, 0, 0, 0)), "stdout"),
            (
                scan_took > 20,
                f"the scan stopped after {scan_took:.1f} s: {scan.stdout[:160]}{scan.stderr[:160]}",
            ),
            broken_typed(hook, hand_typed),
            (hook_took > 19, f"the check after a write gave up after {hook_took:.1f} s"),
        ],
        f"the version probe fails in {took:.1f} s; the scan waits {scan_took:.1f} s for a slow checker and"
        f" is green; the check after a write gives up after {hook_took:.1f} s with its own line",
    )


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
    # a path the reader opens or goes to is whole, escaped; the new path as typed only says which one is wrong
    odd = moving_consumer()
    odd.write(HOOK_RAW, note("# W\n", "note-w"))
    link = "docs/notes/l\nx\\y" + "k" * 80 + ".md"
    (odd.root / link).symlink_to("one.md")
    odd.commit()
    odd_before = tree_state(odd)
    odd_typed = [
        (
            mover(odd, OLD, "docs/n\nx\\y" + "d" * 80 + "/"),
            "BROKEN: docs/n\\nx\\\\y"
            + "d" * 70
            + "… [91 characters] names a directory, not the file's new path"
            " — fix: give the new path in full, file name included — a document is never moved 'into' a"
            " directory",
        ),
        (
            mover(odd, HOOK_RAW, "docs/notes/n\nx\\y" + "k" * 80 + ".txt"),
            f"BROKEN: {HOOK_SHOWN} is a Markdown document and docs/notes/n\\nx\\\\y"
            + "k" * 80
            + ".txt is not"
            " named as one — fix: keep the .md ending: a document that loses it is no longer checked, and its"
            " own links are never repaired",
        ),
        (
            mover(odd, link, NEW),
            "BROKEN: docs/notes/l\\nx\\\\y"
            + "k" * 80
            + ".md is a symbolic link, not a document — fix: move the"
            " document it points at; move the link itself with git mv, its target being relative to it",
        ),
    ]
    parent = H.scratch_dir()
    outside_odd = parent / ("o" + WEIRD_DIR)
    outside_odd.mkdir()
    nowhere_odd = subprocess.run(
        [H.sh, str(MOVER), "a.md", "b.md"],
        cwd=outside_odd,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    odd_results = [broken_first_line(result, line) for result, line in odd_typed]
    return all_of(
        [
            *results,
            (tree_state(consumer) == before, "the tree changed"),
            (nowhere.returncode == 1 and "is not inside a git repository" in nowhere.stderr, nowhere.stderr),
            *odd_results,
            (tree_state(odd) == odd_before, "a refusal of a long path changed the tree"),
            (
                nowhere_odd.returncode == 1
                and nowhere_odd.stderr.startswith(
                    f"BROKEN: {parent}/o{WEIRD_DIR_SHOWN} is not inside a git repository — fix: run the mover"
                    " from inside the repository\n"
                ),
                nowhere_odd.stderr,
            ),
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


def wide_tree_lines() -> list[str]:
    """A scan of a document whose path, ids, targets and anchors run over 80 characters with a backslash:
    every line typed by hand. A path is whole, escaped; an id, a link's target and a match only point:
    cut at 80 with the cut said, then escaped; the anchor the fix tells the reader to write is whole."""
    doc = "docs/notes/w\\x" + "z" * 80 + ".md"
    shown = "docs/notes/w\\\\x" + "z" * 80 + ".md"
    owner = "docs/notes/o\\y" + "q" * 80 + ".md"
    target = "docs/notes/t\\z" + "t" * 80 + ".md"  # lychee reads its backslash as a separator: R7 only
    long_target = "docs/notes/" + "t" * 100 + ".md"
    doc_id = "i" * 100
    lines = (
        f"See `{doc_id}`.\n"
        f"See [{doc_id}]({'l' * 100}.md).\n"
        "See /Users/ann/" + "p" * 100 + " there.\n"
        "See [e](an.md#K\\z" + "x" * 100 + ").\n"
        "See [a](gone-" + "g" * 100 + ".md).\n"
        "See [b](t.md#a%0Ab).\n"
        "See [c](" + "t" * 100 + ".md#" + "f" * 100 + ").\n"
        "See [d](t\\z" + "t" * 80 + ".md#first-section).\n"
        "See [f](t%5Cz" + "t" * 80 + ".md#nope).\n"
    )
    files = {
        TARGET: TARGET_TEXT,
        target: TARGET_TEXT.replace("id: note-t\n", "id: note-tw\n"),
        long_target: TARGET_TEXT.replace("id: note-t\n", "id: note-tl\n"),
        doc: note(body(lines), "note-w"),
        owner: note("# O\n", doc_id),
        "docs/notes/" + "l" * 100 + ".md": note("# L\n", "long-t"),
        "docs/notes/an.md": note('# An\n\n<a id="k\\z' + "x" * 100 + '"></a>\n', "note-an"),
        "tools/w\\x" + "t" * 80 + ".sh": "see note-" + "n" * 100 + "\n",
        "docs/notes/c\rd.md": note(body("See [g](gone-cr.md).\n"), "note-c"),  # a lone carriage return
    }
    out = scan_of(files, own(mentions=[{"pattern": r"\bnote-[a-z]+\b"}])).stdout.splitlines()
    owner_shown = "docs/notes/o\\\\y" + "q" * 80 + ".md"
    owner_rel = "o\\\\y" + "q" * 80 + ".md"
    target_shown = "docs/notes/t\\\\z" + "t" * 80 + ".md"
    cut_target = "t\\\\z" + "t" * 77  # a destination of over 80 characters, cut, its backslash escaped
    wanted = (
        f"RED: {shown}:9: document id '{doc_id}' stands in backticks and is no link",
        f"  fix: write [{doc_id}]({owner_rel}) — the path from this document to {owner_shown}",
        f"RED: {shown}:10: the link's text is document id '"
        + "i" * 80
        + "… [100 characters]', and its target "
        + "l" * 80
        + f"… [103 characters] is not that document ({owner_shown})",
        f"RED: {shown}:11: '/Users/ann/" + "p" * 69 + "… [111 characters]' is a path on one machine",
        f"RED: {shown}:12: an.md#K\\\\z"
        + "x" * 71
        + "… [109 characters] has no anchor 'K\\\\z"
        + "x" * 100
        + "' (it has 'k\\\\z"
        + "x" * 100
        + "': an anchor's case counts)",
        "  fix: cite 'k\\\\z" + "x" * 100 + "' as it is written",
        f"RED: {shown}:13: link target gone-" + "g" * 75 + "… [108 characters] does not exist",
        f"RED: {shown}:14: t.md#a%0Ab has no anchor 'a\\nb'",
        '  fix: cite an anchor the target carries, or add <a id="a\\nb"></a> on its own line before the cited'
        " place in docs/notes/t.md",
        f"RED: {shown}:15: " + "t" * 80 + "… [204 characters] has no anchor '" + "f" * 100 + "'",
        '  fix: cite an anchor the target carries, or add <a id="'
        + "f" * 100
        + '"></a> on its own line before'
        f" the cited place in {long_target}",
        f"RED: {shown}:16: {cut_target}… [100 characters] resolves only through a heading — its generated"
        " name, or a {#key} written after it — not through an anchor written in " + target_shown,
        f"RED: {shown}:17: t%5Cz" + "t" * 75 + "… [93 characters] has no anchor 'nope'",
        '  fix: cite an anchor the target carries, or add <a id="nope"></a> on its own line before the cited'
        " place in " + target_shown,
        "RED: docs/notes/c\\rd.md:9: link target gone-cr.md does not exist",
        "RED: tools/w\\\\x"
        + "t" * 80
        + ".sh:1: 'note-"
        + "n" * 75
        + "… [105 characters]' names a document no covered document carries as its id",
    )
    prefixes = (
        f"  fix: point it at {owner_rel}; after a move, every such link is repaired at once by: ",
        '  fix: add <a id="<short fixed key>"></a> on its own line before that heading in '
        + target_shown
        + " and cite",
    )
    absent = [line for line in wanted if line not in out]
    return absent + [p for p in prefixes if not any(line.startswith(p) for line in out)]


def golden_tree_lines() -> tuple[bool, str]:
    out = tree_scan("See [a](gone.md), [b](t.md#nope), [c](t.md#K1) and [d](t.md#first-section).").stdout
    missing = [key for key, line in GOLDEN_TREE.items() if line not in out]
    missing += wide_tree_lines()
    absent = scan_with(path_with(None)).stderr
    x1 = (
        "BROKEN: const-referencing needs lychee 0.24.2 or newer and found none on PATH — fix: install it"
        " (https://lychee.cli.rs/installation/), then run the scan"
    )
    if x1 not in absent:
        missing.append("X1")
    return (
        not missing,
        f"{len(GOLDEN_TREE) + 16} literal lines found" if not missing else f"not found: {missing}",
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
        7,
        "governed_only: a policy nobody can read is C12.10 at the write, never a policy with no id",
        governed_only_policy_unreadable,
    ),
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
        70,
        "hooks.json: three handlers in the exec form, scripts present, explicit timeouts that hold the"
        " budgets each tool handler waits on",
        hooks_file,
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
    Assertion(
        76,
        "R4: a PATH entry and C:/Users/ann/x are red; C:/Users/ann alone and tilde paths are not",
        r4_more_shapes,
    ),
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
        "a link checker that hangs is a configuration failure inside the hook's timeout; the scan has none;"
        " no lychee and an unreadable document: X1 at the write, C12.10 in the scan",
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
    pattern_dial=PatternDial("territories", lambda pattern: own(territories=[pattern])),
    skill="referencing",  # the skill a red names (F10), typed by hand
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
