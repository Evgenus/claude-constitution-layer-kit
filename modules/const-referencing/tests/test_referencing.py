"""Fixtures of const-referencing: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.

The fixture consumer is the shared one. Its three policies matter here only as documents
that carry ids: this gate resolves no policy, and covers every Markdown file by default, so
the shared items about the root policy are not its own and are skipped; their numbers
stay free.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import yaml
from acceptance import broken_first_line, check_case, expect, item
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import Broken, Finding
from consumer import Consumer, document
from harness import Case, Edit, Harness, Result, Write, event_json, fake_program, red_lines
from referencing_gate import lychee, messages, start
from test_shared_items import NO_ENVELOPE, PatternDial, Subject, git_patch, git_timeouts, no_clock

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
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


def broken(result: Result, failure: Broken | str) -> None:
    """The failure as the module builds it, or, given a string, as the item typed it by hand."""
    broken_typed(result, failure if isinstance(failure, str) else failure.render())


def broken_typed(result: Result, line: str) -> None:
    """The failure's line, typed by hand where the item types it, first; then the count line."""
    broken_first_line(result, line)
    first = f"exit 1, first stderr line: {line}"
    assert shared.c11_broken_count() in result.stderr, f"no count line after: {first}"


def passes(body: str, patch: dict[str, object] | None = LANES, target: str = DOC) -> None:
    expect(gate_on(wrote(body, target), dials_patch=patch)[0], 0, messages.g1_covered(), "stdout")


def blocks(body: str, finding: Finding, patch: dict[str, object] | None = LANES) -> None:
    expect(gate_on(wrote(body), dials_patch=patch)[0], 2, finding.render(), "stderr")


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


@pytest.mark.parametrize(
    "case", [pytest.param(case, id=f"T{case.number}", marks=item(case.number, case.title)) for case in CASES]
)
def test_case(case: Case) -> None:
    check_case(H, case)


# ------------------------------------------------------------------ assertions


@item(10, "masked: a fence, an open fence, an indented block, a comment, a code span, a link's text")
def test_masked_regions() -> None:
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
    for text in bodies.values():
        passes(text)


@item(46, "R4 reads code and comments too; only the YAML block that opens the file is not read")
def test_a_path_on_one_machine_is_read_in_code_too() -> None:
    """A bare form inside code is an illustration; a local path inside code still leaks a machine
    and resolves nowhere else. Only the YAML block that opens the file is not read."""
    path = "/Users/someone/x.md"
    reds = {
        "a code span": (f"# F\n\nIt lies in `{path}`.\n", 10),
        "a fence": (f"# F\n\n```sh\ncat {path}\n```\n", 11),
        "an indented block": (f"# F\n\npara\n\n    cat {path}\n", 12),
        "a comment": (f"# F\n\n<!-- {path} -->\n", 10),
    }
    for text, line in reds.values():
        blocks(text, messages.r4_one_machine(DOC, line, path))
    in_envelope = document(
        "# F\n", id="note-a", type="non-authoritative", title=f"About {path}", status="active"
    )
    expect(gate_on(Write(DOC, in_envelope))[0], 0, messages.g1_covered(), "stdout")
    # A document with no YAML block has no region the checks skip: its first block, a fence, is read like the
    # rest. This case lives here, not in item 11, since what it holds is the path rule; it has no envelope, so
    # it is written whole and not through `note`. The fence opens on line 1, the path stands on line 2.
    bare = f"```sh\ncat {path}\n```\n"
    wanted = [f"RED: {DOC}:2: '{path}' is a path on one machine"]
    no_block, _ = gate_on(Write(DOC, bare), dials_patch=LANES)
    got = [line for line in red_lines(no_block.stderr) if line.startswith(f"RED: {DOC}:")]
    assert got == wanted and no_block.code == 2, (
        f"no YAML block: wanted exit 2 with {wanted}; got exit {no_block.code}: {got}"
    )


@item(11, "masked: the YAML block that opens the file")
def test_envelope_is_masked() -> None:
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
            pytest.fail(f"{name}: wanted exit {code} with {wanted}; got exit {result.code}: {got}")


@item(12, "an indented paragraph continuing a list item is no code: a bare form there is red")
def test_list_continuation_is_no_code() -> None:
    blocks("# F\n\n- item\n\n    continued: REQ-7\n", r1(line=12))


@item(13, "a lane is silent in its home documents")
def test_lane_is_silent_at_home() -> None:
    passes(body("REQ-7 is defined here."), target="docs/reqs.md")
    blocks(body("See REQ-7."), r1())


@item(14, "with no lane declared no bare form is known")
def test_no_lanes_no_bare_forms() -> None:
    passes(body("See REQ-7."), patch=None)


@item(15, "bare_ids: allow switches R2 off")
def test_bare_ids_allowed() -> None:
    passes(body(f"See `{OWNER_ID}`."), patch=own(bare_ids="allow"))
    blocks(body(f"See `{OWNER_ID}`."), R2, patch=None)


@item(48, "local_paths: allow switches R4 off")
def test_local_paths_allowed() -> None:
    """The switch for a document that must show a container's home directory."""
    fence = body("```dockerfile\nWORKDIR /home/node/app\n```")
    blocks(fence, messages.r4_one_machine(DOC, 10, "/home/node/app"), patch=None)
    passes(fence, patch=own(local_paths="allow"))
    passes(body("Notes: /Users/someone/notes.md"), patch=own(local_paths="allow"))


@item(16, "the document's own id, and a name no covered document carries, pass in backticks")
def test_own_id_and_unknown_ids_pass() -> None:
    passes(body("This is `note-a`; `not-a-document` is no id of a covered document."))


@item(17, "R3 passes: ticks and a fragment, a fragment alone, an address with a scheme, angle brackets")
def test_id_links_that_pass() -> None:
    lines = [
        f"[`{OWNER_ID}`]({TO_OWNER}#rules) with ticks and a fragment",
        "[note-a](#top) a fragment alone opens this document",
        f"[{OWNER_ID}](https://example.invalid/x) an address with a scheme is not judged",
        f"[{OWNER_ID}](<{TO_OWNER}>) in angle brackets",
    ]
    passes("# F\n\n" + "\n".join(lines) + "\n")


@item(18, "R3 judges an id written in ticks inside the link's text")
def test_ticks_in_link_text_are_judged() -> None:
    finding = messages.r3_id_link_astray(DOC, LINE, OWNER_ID, "b.md", OWNER, TO_OWNER)
    blocks(body(f"See [`{OWNER_ID}`](b.md)."), finding)


@item(19, "the id of a document that exists is known to the write of another")
def test_pending_document_carries_its_id() -> None:
    """The id of the document being written is known before the file exists."""
    other = messages.r2_bare_id("docs/notes/b.md", LINE, "note-a", DOC, "a.md")
    result, _ = gate_on(
        Write("docs/notes/b.md", note(body("See `note-a`."), "note-b")), files={DOC: note("# F\n")}
    )
    expect(result, 2, other.render(), "stderr")


@item(20, "an Edit is judged on the document it produces")
def test_edit_is_judged_as_written() -> None:
    files = {DOC: VALID.text}
    red, _ = gate_on(
        Edit(DOC, "and [REQ-7](../policies/root-policy.md)", "and REQ-7"), dials_patch=LANES, files=files
    )
    green, _ = gate_on(Edit(DOC, "# Fixture", "# Renamed"), dials_patch=LANES, files=files)
    finding = messages.r1_bare_form(DOC, LINE, "REQ-7", str(LANE["names"]), str(LANE["fix"]))
    expect(red, 2, finding.headline, "stderr")
    expect(green, 0, messages.g1_covered(), "stdout")


@item(21, "several findings come in reading order, with their count")
def test_findings_in_reading_order() -> None:
    result, _ = gate_on(wrote(f"# F\n/Users/someone/x.md then `{OWNER_ID}`\nthen REQ-7\n"), dials_patch=LANES)
    keys = [
        line.split(":")[2].strip()[:12] for line in result.stderr.splitlines() if line.startswith("RED: docs")
    ]
    order = [result.stderr.index(text) for text in ("/Users/someone", f"id '{OWNER_ID}'", "'REQ-7'")]
    ok = result.code == 2 and order == sorted(order) and "3 finding(s)" in result.stderr
    assert ok, f"exit {result.code}, {keys}: {result.stderr}"


@item(29, "R4 names the path, not the full stop after it")
def test_a_path_ends_before_the_sentence_does() -> None:
    blocks(body("Notes are in /Users/someone/notes.md."), R4_PATH)


@item(22, "a document outside const-referencing.territories, or a new one git ignores, is a visible skip")
def test_not_covered() -> None:
    result, _ = gate_on(
        wrote(body("See REQ-7.")),
        dials_patch={NAMESPACE: {"lanes": [LANE], "territories": ["docs/policies/**"]}},
    )
    expect(result, 0, shared.g1_green_skip(messages.g1_skip_not_covered(DOC)), "stdout")
    _ignored_by_git()


IGNORED_DIR = "docs/notes/ignored/"
IGNORED = IGNORED_DIR + "new.md"


def _ignored_by_git() -> None:
    """The dial covers the Markdown files git lists, ignored ones excepted: before a write as after it.
    A new file under an ignored folder is a skip, and the same line either way; a new file git does not
    ignore is covered; a tracked file the ignore rules match is still listed by git, so still covered."""
    ignore = {".gitignore": IGNORED_DIR + "\n"}
    skip = shared.g1_green_skip(messages.g1_skip_not_covered(IGNORED))
    before, _ = gate_on(wrote("# F\n", IGNORED), files=ignore)
    after = after_write(IGNORED, {**ignore, IGNORED: note("# F\n")})
    new, _ = gate_on(wrote("# F\n"), files=ignore)
    tracked = H.fresh_consumer(setup=(Write(IGNORED, note("# F\n", "note-t")),))
    tracked.write(".gitignore", ignore[".gitignore"])  # after the commit: the file stays tracked, now matched
    kept = H.run_gate(event_json(tracked.root, wrote("# F\n", IGNORED)))
    # The calls: a file git lists costs no `check-ignore` in the repository, a new file the territories hold
    # one (the matcher's own calls carry `--no-index`; the fixture sets no log_dir, so none is the log's)
    listed_calls = _repository_check_ignores(event_json(tracked.root, wrote("# F\n", IGNORED)))
    new_root = H.fresh_consumer().root
    new_root.joinpath(".gitignore").write_text(ignore[".gitignore"], encoding="utf-8")
    new_calls = _repository_check_ignores(event_json(new_root, wrote("# F\n", IGNORED)))
    assert listed_calls == 0 and new_calls == 1, (
        f"repository check-ignore calls: {listed_calls} for a listed file, {new_calls} for a new one"
    )
    expect(before, 0, skip, "stdout")
    expect(after, 0, skip, "stdout")
    expect(new, 0, messages.g1_covered(), "stdout")
    expect(kept, 0, messages.g1_covered(), "stdout")


def _repository_check_ignores(event: str) -> int:
    """The `git check-ignore` calls without `--no-index` one hook run makes: a fake git first on PATH logs
    the arguments of each call to a file and hands the call to the real git; it is started once before
    the run (`fake_program`), so its slow first start cuts no git call of the hook."""
    real = shutil.which("git")
    assert real is not None
    directory = H.scratch_dir()
    log = directory / "git.log"
    fake_program(directory / "git", f'echo "$*" >> {shlex.quote(str(log))}\nexec {shlex.quote(real)} "$@"\n')
    H.run_gate(event, env={"PATH": str(directory) + os.pathsep + os.environ.get("PATH", os.defpath)})
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return sum("check-ignore" in line and "--no-index" not in line for line in lines)


@item(23, "the scan reports every document, names documents, links and lanes in its tail")
def test_scan_reports_all() -> None:
    files = {DOC: note(body("See REQ-7.")), "docs/notes/b.md": note(body(f"See `{OWNER_ID}`."), "note-b")}
    red = scan_of(files, LANES)
    second = messages.r2_bare_id("docs/notes/b.md", LINE, OWNER_ID, OWNER, "../policies/notes-policy.md")
    tail = messages.f9_scan_tail(5, 0, 5, 1, 0, 0)
    green = scan_of({DOC: VALID.text}, LANES)
    expect(red, 2, r1().render(), "stdout")
    expect(red, 2, second.render(), "stdout")
    expect(red, 2, shared.f9_count_scan(2, tail), "stdout")
    expect(green, 0, shared.g1_green_scan(messages.f9_scan_tail(4, 2, 4, 1, 0, 0)), "stdout")


@item(24, "the scan ignores severity")
def test_scan_ignores_severity() -> None:
    patch = own(lanes=[LANE], severity="warn")
    expect(scan_of({DOC: note(body("See REQ-7."))}, patch), 2, r1().headline, "stdout")


@item(25, "this module's dial failures are exit 1, never 2, never 0")
def test_dial_failures() -> None:
    def lane(**changes: object) -> dict[str, object]:
        return own(lanes=[{**LANE, **changes}])

    dropped = {key: value for key, value in LANE.items() if key != "fix"}
    try:  # the compiler's own words come from `re` itself, so a Python version cannot break the golden
        re.compile("REQ-([")
    except re.error as compiler:
        compiler_words = str(compiler)
    else:
        pytest.fail("the pattern 'REQ-([' compiled; the fixture needs one the compiler refuses")
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
    for patch, failure in wrong:
        broken(gate_on(VALID, dials_patch=patch)[0], failure)
    in_scan = H.run_gate("", args=["--scan", str(gate_on(VALID, dials_patch=own(bare_ids="maybe"))[1])])
    broken_typed(  # a key with a line break is shown escaped: one line, typed by hand
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
        pytest.fail("the pattern (?P<a\\b>x) compiled; the fixture needs one the compiler refuses")
    broken_typed(
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
        pytest.fail("the pattern (?P=aaa...) compiled; the fixture needs one the compiler refuses")
    if len(long_words) <= 80 or long_name not in long_words:
        pytest.fail(f"the compiler's words are {len(long_words)} characters; the fixture needs more than 80")
    broken_typed(
        gate_on(VALID, dials_patch=lane(pattern=long))[0],
        "BROKEN: constitution.yaml: entry 1 of const-referencing.lanes has a pattern that is no regular"
        f" expression ({long_words}) — in YAML write it in single"
        " quotes, where a backslash stands for itself — fix: write the entry as {pattern: <regular"
        " expression>, names: <what the form cites>, fix: <the link form to write>}; home: [<patterns>] is"
        " optional",
    )
    broken(in_scan, messages.c5_switch("bare_ids"))


@item(6, "a pattern holding a control character — YAML's double-quoted \\b — is exit 1, never a silent pass")
def test_control_character_in_a_pattern() -> None:
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
    broken(red, messages.c5_lane(1, messages.lane_pattern_control("\x08")))
    assert literal in red.stderr, f"the golden line is not in: {red.stderr.strip()}"
    expect(green, 2, r1().render(), "stderr")
    broken(mention, messages.c5_mention(1, messages.lane_pattern_control("\x08")))


@item(26, "a lane's home pattern git would misread is the shared configuration failure")
def test_lane_home_pattern_git_would_misread() -> None:
    result, _ = gate_on(VALID, dials_patch=own(lanes=[{**LANE, "home": ["#docs"]}]))
    broken_typed(
        result,
        "BROKEN: constitution.yaml: const-referencing.lanes[1].home holds a pattern git would not read as"
        " one: '#docs' — fix: a pattern may not start with '#' (a comment to git) nor contain a line"
        " break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break",
    )


@item(28, "an envelope nobody can read is no crash and no finding: references are still judged")
def test_unreadable_envelope_is_no_crash() -> None:
    """Brackets nested past the parser's depth: the document carries no id here, and the write is
    judged on its references all the same."""
    text = "---\nid: " + "[" * 600 + "\n---\n"
    green, _ = gate_on(Write(DOC, text + "# F\n"), dials_patch=LANES)
    red, _ = gate_on(Write(DOC, text + "# F\nSee REQ-7.\n"), dials_patch=LANES)
    finding = messages.r1_bare_form(DOC, 5, "REQ-7", str(LANE["names"]), str(LANE["fix"]))
    expect(green, 0, messages.g1_covered(), "stdout")
    expect(red, 2, finding.render(), "stderr")


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


@item(27, "golden lines: the taught texts as literals, not as the functions return them")
def test_golden_lines() -> None:
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
    assert not missing, f"not found: {missing}"


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


def red_green(red: Result, finding: Finding, green: Result) -> None:
    expect(red, 2, finding.render(), "stdout")
    expect(green, 0, "GREEN: ", "stdout")


@item(30, "R5, the specification's first: a broken reference is red, repaired it is green")
def test_broken_reference() -> None:
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    red_green(tree_scan("See [x](gone.md)."), finding, tree_scan("See [x](t.md)."))


@item(31, "R6, the specification's second: a moved anchor is red, put back it is green")
def test_moved_anchor() -> None:
    """The anchor a link cites is taken out of the target: red; put back: green."""
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#k1", "k1", TARGET, None)
    moved = {TARGET: TARGET_TEXT.replace('<a id="k1"></a>\n', ""), SOURCE: source("See [x](t.md#k1).")}
    red_green(scan_of(moved), finding, tree_scan("See [x](t.md#k1)."))


@item(32, "R7: a generated name, a {#key}, the own heading; an explicit anchor; allow")
def test_heading_anchors() -> None:
    by_name = messages.r7_heading_anchor(SOURCE, LINE, "t.md#first-section", TARGET)
    by_key = messages.r7_heading_anchor(SOURCE, LINE, "t.md#custom", TARGET)
    own_heading = messages.r7_heading_anchor(SOURCE, LINE, "#fixture", SOURCE)
    allowed = own(heading_anchors="allow")
    red_green(tree_scan("See [x](t.md#first-section)."), by_name, tree_scan("See [x](t.md#k1)."))
    expect(tree_scan("See [x](t.md#custom)."), 2, by_key.render(), "stdout")
    expect(tree_scan("See [x](#fixture)."), 2, own_heading.render(), "stdout")
    expect(
        tree_scan("See [x](t.md#first-section) and [y](t.md#custom).", allowed),
        0,
        "GREEN: ",
        "stdout",
    )


@item(40, "an anchor shown inside code is no anchor")
def test_anchor_shown_in_code_is_none() -> None:
    """An anchor inside a fence is an example: the link beside it still goes through the heading."""
    shown = note('# Target\n\n## Shown\n\n```html\n<a id="shown"></a>\n```\n', "note-t")
    finding = messages.r7_heading_anchor(SOURCE, LINE, "t.md#shown", TARGET)
    expect(scan_of({TARGET: shown, SOURCE: source("See [x](t.md#shown).")}), 2, finding.render(), "stdout")


@item(33, "R6: an anchor cited in another case is red, whatever heading_anchors says")
def test_anchor_case_counts() -> None:
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#K1", "K1", TARGET, "k1")
    allowed = tree_scan("See [x](t.md#K1).", own(heading_anchors="allow"))
    expect(tree_scan("See [x](t.md#K1)."), 2, finding.render(), "stdout")
    expect(allowed, 2, finding.headline, "stdout")


@item(34, "coverage decides whose links are judged, not which targets must exist")
def test_uncovered_targets() -> None:
    """Coverage decides whose links are judged: a link into an uncovered file must resolve, and
    which kind of anchor resolved it there is not this gate's to say."""
    only_source = own(territories=["*.md", "!" + TARGET])
    gone = messages.r5_no_target(SOURCE, LINE, "gone.md")
    expect(
        tree_scan("See [x](t.md#first-section).", only_source),
        0,
        "4 document(s) and 1 link(s) examined, 5 Markdown",
        "stdout",
    )
    expect(tree_scan("See [x](gone.md).", only_source), 2, gone.render(), "stdout")


@item(35, "a lychee.toml and a .lycheeignore in the repository change nothing")
def test_owned_invocation() -> None:
    """Files by which a repository steers its own lychee change nothing here."""
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    stray = {"lychee.toml": 'exclude_path = ["docs"]\n', ".lycheeignore": "gone.md\n"}
    steered = tree_scan("See [x](gone.md).", more=stray)
    expect(steered, 2, finding.render(), "stdout")


@item(36, "links inside code are not checked")
def test_links_in_code_are_not_checked() -> None:
    expect(tree_scan("Shown: `[x](gone.md)`.\n\n```md\n[y](gone.md#a)\n```"), 0, "GREEN: ", "stdout")


def path_with(lychee_script: str | None) -> dict[str, str]:
    """A PATH holding python3, git and dirname, and the given script as lychee — or none at all. The fake
    is started once before it is used (`fake_program`), so that its slow first start falls in no clock."""
    directory = H.scratch_dir()
    for tool in ("python3", "git", "dirname"):
        found = os.path.realpath(sys.executable) if tool == "python3" else shutil.which(tool)
        assert found, tool
        os.symlink(found, directory / tool)
    if lychee_script is not None:
        fake_program(directory / "lychee", lychee_script)
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


@item(37, "absence: no lychee on PATH is a configuration failure with the install address")
def test_link_checker_absent() -> None:
    broken(scan_with(path_with(None)), messages.x1_no_lychee("0.24.2"))


@item(38, "a lychee below the floor, one with no version, one that exits 2 with no report")
def test_link_checker_unusable() -> None:
    usage = (
        'case "$1" in --version) echo "lychee 0.24.2";;'
        ' *) echo "error: unexpected argument" >&2; exit 2;; esac\n'
    )
    broken(
        scan_with(path_with('echo "lychee 0.23.0"\n')),
        messages.x2_lychee_too_old("0.24.2", "lychee 0.23.0"),
    )
    broken(scan_with(path_with("exit 0\n")), messages.x2_lychee_too_old("0.24.2", ""))
    broken(scan_with(path_with_unstartable_lychee()), messages.x2_lychee_too_old("0.24.2", ""))
    broken(scan_with(path_with(usage)), messages.x3_no_report("exit 2", "error: unexpected argument"))
    # lychee's version output is several lines with a backslash: it only points, cut at 80, escaped
    broken_typed(
        scan_with(path_with("printf 'lychee 0.23.0\\nline\\\\two " + "w" * 90 + "\\n'\n")),
        "BROKEN: const-referencing needs lychee 0.24.2 or newer, found 'lychee 0.23.0\\nline\\\\two "
        + "w" * 57
        + "… [113 characters]' — fix: install a current one (https://lychee.cli.rs/installation/),"
        " then run the scan — until then no reference is checked for resolving",
    )
    # its first line of stderr is the diagnosis the fix asks to be reported: whole, escaped
    broken_typed(
        scan_with(
            path_with(
                'case "$1" in --version) echo "lychee 0.24.2";;'
                " *) printf '%s\\n' 'error: a\\b " + "e" * 90 + "' >&2; exit 2;; esac\n"
            )
        ),
        "BROKEN: lychee gave no report: exit 2 (error: a\\\\b " + "e" * 90 + ") — fix: this is a defect"
        " of the gate's invocation or of the installed lychee, not of the repository; run lychee"
        " --version and report both to whoever maintains the plugin — until then no reference is"
        " checked for resolving",
    )


# ------------------------------------------------------------------ coverage, and names outside Markdown

MENTION = {"pattern": r"\bnote-[a-z]+\b"}
LOOSE = "docs/loose/l.md"  # no policy of the shared consumer governs docs/loose/


@item(41, "governed_only: a document no policy governs is not covered")
def test_governed_only() -> None:
    """Under governed_only a document no policy governs is not covered."""
    files = {LOOSE: note(body("See [x](gone.md)."), "note-l"), SOURCE: source("See [x](gone.md).")}
    only = own(governed_only=True)
    governed = scan_of(files, only)
    loose_write = gate_on(Write(LOOSE, note(body(f"See `{OWNER_ID}`."), "note-l")), only)[0]
    skipped = shared.g1_green_skip(messages.g1_skip_not_covered(LOOSE))
    expect(governed, 2, messages.r5_no_target(SOURCE, LINE, "gone.md").headline, "stdout")
    expect(governed, 2, "1 finding(s)", "stdout")
    expect(scan_of(files), 2, "2 finding(s)", "stdout")
    expect(loose_write, 0, skipped, "stdout")
    expect(gate_on(wrote(body(f"See `{OWNER_ID}`.")), only)[0], 2, R2.render(), "stderr")


@pytest.mark.skipif(
    os.geteuid() == 0,
    reason="NOT EXERCISED: running as root, where a mode bit does not deny a read — 0 files examined",
)
@item(7, "governed_only: a policy nobody can read is C12.10 at the write, never a policy with no id")
def test_governed_only_policy_unreadable() -> None:
    """Under governed_only the gate reads the policies: a file where they live that nobody can read
    is C12.10 at the write, never a policy with no id and a verdict computed without it."""
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
    broken_first_line(result, line)
    first = f"exit 1, first stderr line: {line}"
    assert shared.c11_broken_count() in result.stderr, f"no count line after: {first}"


@item(45, "a negated pattern takes a tree out of the territory: !dir/**, not !dir/")
def test_a_tree_taken_out() -> None:
    """`!dir/**` after `*.md` leaves a tree uncovered; `!dir/` names the directory alone, and
    the files inside it still match — as the install note says."""
    files = {"vendor/deep/v.md": "[x](gone.md)\n", SOURCE: source("See [x](gone.md).")}
    expect(scan_of(files, claim(["*.md", "!vendor/**"])), 2, "1 finding(s)", "stdout")
    expect(scan_of(files, claim(["*.md", "!vendor/"])), 2, "2 finding(s)", "stdout")


@item(42, "governed_only without a root policy is C5 in every mode; the default needs none")
def test_governed_only_without_root() -> None:
    """governed_only with no root policy is a configuration failure in every mode — as the mover
    refuses — never a skip that lets a write through with nothing examined; by default none is needed."""
    rootless = yaml.safe_dump({"module_prefix": "const-", NAMESPACE: {"governed_only": True}})
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
    default, _ = gate_on(VALID, raw_dials="module_prefix: const-\n")
    broken(before, failure)
    broken(after, failure)
    broken(scan, failure)
    expect(default, 0, messages.g1_covered(), "stdout")


@item(43, "R8: a name outside Markdown no covered document carries; off by default")
def test_mentions_outside_markdown() -> None:
    files = {
        SOURCE: source("x"),
        "tools/check.sh": "# see note-s and note-gone\necho note-s\n",
        "tools/blob.bin": "note-zz\0",
    }
    finding = messages.r8_unknown_mention("tools/check.sh", 1, "note-gone")
    red = scan_of(files, own(mentions=[MENTION]))
    fixed = scan_of({**files, "tools/check.sh": "# see note-s\n"}, own(mentions=[MENTION]))
    elsewhere = scan_of(files, own(mentions=[{**MENTION, "files": ["src/**"]}]))
    # a line ends at "\n" alone: a form feed or U+2028 inside a line moves no line number
    odd = scan_of({**files, "tools/page.sh": "echo one\x0ctwo\n# page  note-lost\n"}, own(mentions=[MENTION]))
    expect(red, 2, finding.render(), "stdout")
    expect(red, 2, "1 finding(s)", "stdout")
    expect(odd, 2, messages.r8_unknown_mention("tools/page.sh", 2, "note-lost").render(), "stdout")
    expect(odd, 2, "2 finding(s)", "stdout")
    expect(fixed, 0, "1 mention pattern(s) over ", "stdout")
    expect(scan_of(files), 0, "GREEN: ", "stdout")
    expect(elsewhere, 0, "GREEN: ", "stdout")


@item(44, "the dial failures of governed_only, heading_anchors and mentions are exit 1")
def test_mention_dial_failures() -> None:
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
    for patch, failure in wrong:
        broken(gate_on(VALID, dials_patch=patch)[0], failure)
    broken_typed(  # a key with a line break is shown escaped: one line, typed by hand
        gate_on(VALID, dials_patch=own(mentions=[{**MENTION, "a\nb": 1}]))[0],
        "BROKEN: constitution.yaml: entry 1 of const-referencing.mentions carries the key 'a\\nb'; a mention"
        " holds pattern and files, and nothing else — fix: write the entry as {pattern: <regular expression"
        " whose whole match is a document's id>}; files: [<patterns>] is optional",
    )


# ------------------------------------------------------------------ after the write

AFTER = "PostToolUse"
BEFORE = "PreToolUse"


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


@item(50, "after the write: the written document's own broken link, exit 2 on stderr; repaired, green")
def test_own_links_after_write() -> None:
    files = {TARGET: TARGET_TEXT, SOURCE: source("See [x](gone.md).")}
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    fixed = {TARGET: TARGET_TEXT, SOURCE: source("See [x](t.md#k1).")}
    expect(after_write(SOURCE, files), 2, finding.render(), "stderr")
    expect(after_write(SOURCE, files), 2, after_count(SOURCE, 1, 1), "stderr")
    expect(after_write(SOURCE, fixed), 0, messages.g1_covered(), "stdout")
    # the count line is what a later step reads: the path whole, escaped, over 80 characters
    expect(
        after_write(BS_RAW, {TARGET: TARGET_TEXT, BS_RAW: source("See [x](gone.md).")}),
        2,
        f"RED: 1 link(s) of the whole tree examined, 1 finding(s) involve {BS_SHOWN}",
        "stderr",
    )


@item(51, "after the write: a break the write causes in another document is reported")
def test_inbound_break_after_write() -> None:
    """The target is written without the anchor another document cites: the break is in the
    other file, and it is reported in the turn that causes it."""
    files = {TARGET: TARGET_TEXT.replace('<a id="k1"></a>\n', ""), SOURCE: source("See [x](t.md#k1).")}
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#k1", "k1", TARGET, None)
    expect(after_write(TARGET, files), 2, finding.render(), "stderr")


@item(52, "after the write: an older break elsewhere is not repeated; the scan reports it")
def test_older_break_elsewhere_is_not_repeated() -> None:
    files = {
        TARGET: TARGET_TEXT,
        SOURCE: source("See [x](gone.md)."),
        "docs/notes/u.md": note("# U\n", "note-u"),
    }
    expect(after_write("docs/notes/u.md", files), 0, messages.g1_covered(), "stdout")
    expect(scan_of(files), 2, messages.r5_no_target(SOURCE, LINE, "gone.md").headline, "stdout")


@item(53, "after the write: a heading-derived anchor is reported")
def test_heading_anchor_after_write() -> None:
    files = {TARGET: TARGET_TEXT, SOURCE: source("See [x](t.md#first-section).")}
    finding = messages.r7_heading_anchor(SOURCE, LINE, "t.md#first-section", TARGET)
    expect(after_write(SOURCE, files), 2, finding.render(), "stderr")


@item(54, "after the write, severity warn: one JSON object naming the event")
def test_warn_after_write() -> None:
    files = {TARGET: TARGET_TEXT, SOURCE: source("See [x](gone.md).")}
    result = after_write(SOURCE, files, own(severity="warn"))
    try:
        loaded = json.loads(result.stdout)
    except ValueError:
        pytest.fail(f"stdout is not one JSON object: {result.stdout!r}")
    specific = loaded.get("hookSpecificOutput", {})
    ok = (
        result.code == 0
        and result.stderr == ""
        and specific.get("hookEventName") == AFTER
        and messages.r5_no_target(SOURCE, LINE, "gone.md").render() in specific.get("additionalContext", "")
        and after_count(SOURCE, 1, 1) in specific.get("additionalContext", "")
    )
    assert ok, str(result)


@item(55, "the lint is the pre-write handler's alone")
def test_lint_is_not_run_after_write() -> None:
    """A bare form is the pre-write handler's to block; after the write only the tree is read."""
    files = {SOURCE: source("See REQ-7.")}
    before = H.run_gate(event_json(H.fresh_consumer(SETUP).root, Write(SOURCE, files[SOURCE])))
    expect(after_write(SOURCE, files, LANES), 0, messages.g1_covered(), "stdout")
    expect(before, 2, "REQ-7", "stderr")


@item(56, "after the write: findings past the cap are counted, not printed")
def test_many_findings_are_cut() -> None:
    """Two caps: twenty findings, and no more characters than leave the count line inside what the
    platform passes on. Short findings meet the first, long ones the second."""
    short = " ".join(f"[x{n}](t.md#nope-{n})" for n in range(25))
    by_count = after_write(SOURCE, {TARGET: TARGET_TEXT, SOURCE: source(short)})
    long_ones = " ".join(f"[x{n}](gone-{n}-{'y' * 150}.md)" for n in range(25))
    by_size = after_write(SOURCE, {SOURCE: source(long_ones)})
    printed = by_size.stderr.count("RED: docs/")
    assert by_count.code == 2 and by_count.stderr.count("RED: docs/") == 20, (
        "short findings: not twenty printed"
    )
    assert after_count(SOURCE, 25, 25, 20) in by_count.stderr, "short findings: the count line"
    assert by_size.code == 2 and 0 < printed < 20, f"long findings: {printed} printed"
    assert after_count(SOURCE, 25, 25, printed) in by_size.stderr, "long findings: the count line"
    assert len(by_size.stderr) < 10000, f"long findings: {len(by_size.stderr)} characters"


@item(57, "after the write: a file that is not there is a visible skip")
def test_file_gone_after_write() -> None:
    consumer = H.fresh_consumer()
    result = H.run_gate(event_json(consumer.root, Write(SOURCE, source("x")), event=AFTER))
    expect(result, 0, shared.g1_green_skip(shared.g1_skip_gone(SOURCE)), "stdout")


@item(58, "an event the gate is not wired to is a configuration failure")
def test_unknown_event() -> None:
    files = {SOURCE: source("See [x](gone.md).")}
    broken_typed(  # a name holding a line break stays on one line, the break shown escaped
        after_write(SOURCE, files, event="Notif\nication"),
        "BROKEN: hook input names the event 'Notif\\nication', which this gate is not wired to — fix: wire"
        " the gate to PreToolUse and PostToolUse on Write|Edit, as the plugin's hooks file does; to check a"
        " repository by hand run it with --scan [<dir>]",
    )
    broken(after_write(SOURCE, files, event="Notification"), messages.c12_event("Notification"))


@item(59, "absence after the write: no lychee is exit 1 with the install address")
def test_lychee_absent_after_write() -> None:
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    event = event_json(consumer.root, Write(SOURCE, source("See [x](gone.md).")), event=AFTER)
    broken(H.run_gate(event, env=path_with(None)), messages.x1_no_lychee("0.24.2"))


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
    done = subprocess.run(
        [H.sh, str(MOVER), *arguments],
        cwd=consumer.root / cwd,
        capture_output=True,
        text=True,
        env=H.environment(env),
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


@item(60, "the move's red→green: git mv alone leaves the scan red, the act leaves it green")
def test_move_red_green() -> None:
    """Red is the tree after git mv alone; green is the tree after the act."""
    by_git = moving_consumer()
    (by_git.root / NEW).parent.mkdir(parents=True)
    by_git.git("mv", OLD, NEW)
    red = scan(by_git)
    acted = moving_consumer()
    patch, log = git_patch(H)  # the mover is an act: none of its git calls carries a clock
    done = mover(acted, "notes/one.md", "moved/deep/first.md", cwd="docs", env=patch)
    first, two = (acted.root / NEW).read_text(), (acted.root / "docs/notes/two.md").read_text()
    expect(red, 2, messages.r5_no_target("docs/notes/two.md", 11, "one.md#k1").headline, "stdout")
    expect(done, 0, messages.v1_moved(OLD, NEW), "stdout")
    expect(done, 0, messages.v2_rewrote("docs/notes/two.md", 2), "stdout")
    expect(done, 0, messages.v2_rewrote(NEW, 3), "stdout")
    expect(done, 0, messages.v4_count(2, 5, 2), "stdout")
    expect(done, 0, "GREEN: const-referencing: ", "stdout")
    assert ONE_MOVED in first, f"the moved document's own links: {first}"
    assert TWO_REPAIRED in two and "[r]: ../moved/deep/first.md" in two, f"inbound links: {two}"
    expect(scan(acted), 0, "GREEN: ", "stdout")
    no_clock(git_timeouts(log))


@item(61, "the mover lists what names the old path and changes none of it")
def test_mentions_are_listed_not_changed() -> None:
    acted = moving_consumer()
    done = mover(acted, OLD, NEW)
    script = (acted.root / "tools/x.sh").read_text()
    # a Markdown file outside coverage is a text file git lists: read, by either name, like a script
    outside = moving_consumer()
    outside.write("constitution.yaml", dials_text(own(territories=["docs/**"])))
    outside.write("other/readme.md", f"# Readme\nSee {OLD}.\nOr ../{OLD}.\n")
    outside.write("tools/y.sh", f"cat ../{OLD}\n")
    # a line ends at "\n" alone: a form feed inside an earlier line, or before the name, moves no number
    outside.write("tools/z.sh", f"echo one\x0ctwo\ncat\x0c ../{OLD}\n")
    outside.commit()
    listed = mover(outside, OLD, NEW)
    expect(done, 0, "MENTION: docs/notes/two.md:11: ", "stdout")
    expect(done, 0, f"MENTION: tools/x.sh:1: '# see {OLD}' names the old path outside a link", "stdout")
    assert script == f"# see {OLD}\n", "the script was not rewritten"
    expect(listed, 0, f"MENTION: other/readme.md:2: 'See {OLD}.' names the old path", "stdout")
    expect(listed, 0, f"MENTION: other/readme.md:3: 'Or ../{OLD}.' names the old path", "stdout")
    expect(listed, 0, f"MENTION: tools/y.sh:1: 'cat ../{OLD}' names the old path", "stdout")
    expect(listed, 0, f"MENTION: tools/z.sh:2: 'cat\x0c ../{OLD}' names the old path", "stdout")
    assert (outside.root / "other/readme.md").read_text() == f"# Readme\nSee {OLD}.\nOr ../{OLD}.\n", (
        "the uncovered Markdown file was not rewritten"
    )


@item(62, "the fix R5 teaches, pasted as printed, repairs a move made by hand")
def test_repair_after_a_hand_move() -> None:
    """The fix R5 teaches is followed as printed, with the two paths filled in."""
    consumer = moving_consumer()
    (consumer.root / NEW).parent.mkdir(parents=True)
    consumer.git("mv", OLD, NEW)
    taught = scan(consumer).stdout
    command = messages.mover_command("--moved", "<old path>", "<new path>")
    if command not in taught:
        pytest.fail(f"the scan did not teach {command!r}: {taught}")
    typed = command.replace("<old path>", OLD).replace("<new path>", NEW)
    done = subprocess.run(  # noqa: S602 — the point is to run the line as a reader would paste it
        typed, shell=True, cwd=consumer.root, capture_output=True, text=True, env=H.environment(), check=False
    )
    assert done.returncode == 0 and "GREEN: " in done.stdout, (
        f"exit {done.returncode}: {done.stdout}{done.stderr}"
    )
    expect(scan(consumer), 0, "GREEN: ", "stdout")


@item(63, "the fix R3 teaches, pasted as printed, repairs id links from the envelopes")
def test_repair_by_ids() -> None:
    """The fix R3 teaches is followed as printed: no path is given, the envelopes say where."""
    consumer = moving_consumer()
    (consumer.root / NEW).parent.mkdir(parents=True)
    consumer.git("mv", OLD, NEW)
    consumer.write("docs/notes/two.md", TWO.replace(", [r]", "").replace("[r]: one.md\n", ""))
    blocked, _ = gate_on(Write(DOC, note(body(f"See [{OWNER_ID}](../policies/root-policy.md)."))))
    command = messages.mover_command("--ids")
    if command not in blocked.stderr:
        pytest.fail(f"R3 did not teach {command!r}: {blocked.stderr}")
    done = subprocess.run(  # noqa: S602 — as above
        command,
        shell=True,
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=H.environment(),
        check=False,
    )
    two = (consumer.root / "docs/notes/two.md").read_text()
    assert "[note-one](../moved/deep/first.md#k1)" in two, f"the id link: {two}"
    assert messages.v2_rewrote("docs/notes/two.md", 1) in done.stdout, done.stdout + done.stderr


@item(68, "the id repair leaves alone an id two documents carry")
def test_id_repair_leaves_an_ambiguous_id_alone() -> None:
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
    assert kept and messages.v4_count(0, 0, 0) in done.stdout, done.stdout + done.stderr


@item(64, "every refusal of the mover is exit 1 and changes nothing")
def test_refusals_change_nothing() -> None:
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
    for result, failure in refused:
        broken_first_line(result, failure.render())
    for result, _ in refused:
        assert messages.v4_nothing_changed() in result.stderr, "no closing line"
    assert tree_state(consumer) == before, "a refusal changed the tree"
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
    for result, line in typed:
        broken_first_line(result, line)
    assert tree_state(odd) == odd_before, "a refusal of a long path changed the tree"


@item(65, "with no dials file the mover refuses before it moves")
def test_mover_without_dials() -> None:
    consumer = moving_consumer()
    (consumer.root / "constitution.yaml").unlink()
    result = mover(consumer, OLD, NEW)
    broken_first_line(result, messages.v5_no_dials(str(consumer.root)).render())
    # the root is a path the reader goes to: whole, escaped, over 80 characters
    parent = H.scratch_dir()
    odd = Consumer(parent / WEIRD_DIR).build()
    odd.write(OLD, ONE)
    odd.commit()
    (odd.root / "constitution.yaml").unlink()
    broken_first_line(
        mover(odd, OLD, NEW),
        f"BROKEN: no constitution.yaml in {parent}/{WEIRD_DIR_SHOWN}: the check that proves a move cannot run"
        " — fix: create constitution.yaml at the repository's top — a file that holds only module_prefix:"
        " const- is enough",
    )
    assert (consumer.root / OLD).exists(), result.stdout + result.stderr


@item(66, "the mover exits with the scan's verdict")
def test_mover_ends_red_when_the_tree_is() -> None:
    consumer = moving_consumer()
    consumer.write("docs/notes/three.md", note(body("See [x](gone.md)."), "note-three"))
    expect(
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


@item(67, "golden lines of the mover, typed by hand")
def test_golden_mover_lines() -> None:
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
    assert not missing, f"not found: {missing}"


# ------------------------------------------------------------------ the plugin's other parts

PLUGIN = SCRIPTS.parent
# the session-start pointer to the skill, and the context a subagent starts with, typed by hand
POINTER = (
    "const-referencing (advisory): before writing a link between documents, adding a section or a row"
    " that others will cite, or moving, renaming or deleting a document, load the skill"
    " const-referencing:referencing.\n"
)
CHAT_RULE = (
    "const-referencing (advisory): in chat, write every reference to a file, a section or a document as a"
    " markdown link wherever the file exists. A number, letter or key is a handle local to its message,"
    " decision or session: when a cite crosses that boundary, name the message or decision it came from.\n"
)


@item(
    70,
    "hooks.json: five handlers in the exec form, scripts present, explicit timeouts; the waits of a"
    " check after a write fit the hook's budget, and a check before a write waits for no link checker",
)
def test_hooks_file() -> None:
    """Five handlers, each in the exec form with an explicit timeout: both tool events run the
    gate's one entry point, which tells them apart by the event's name; the session start has two,
    the chat rule and the pointer to the skill, and the subagent start one, the pointer with
    `--subagent`. The module's own waits in one hook run fit the hook's budget the gate declares
    (`GATE.hook_seconds`): the check after a write waits for the version probe, then for the run, one
    after the other; the check before a write runs no link checker and waits for none of them. The
    handlers' timeouts hold that budget and `LEFT_FOR_THE_REST`, which the shared item S165 ties; the
    printers run no child process."""
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
    gate = ["${CLAUDE_PLUGIN_ROOT}/scripts/check-references.sh"]
    rule = ["${CLAUDE_PLUGIN_ROOT}/scripts/print-chat-rule.sh"]
    pointer = ["${CLAUDE_PLUGIN_ROOT}/scripts/print-skill-pointer.sh"]
    wanted: dict[str, list[tuple[str | None, list[str]]]] = {
        "PreToolUse": [("Write|Edit", gate)],
        "PostToolUse": [("Write|Edit", gate)],
        "SessionStart": [(None, rule), (None, pointer)],
        "SubagentStart": [(None, [*pointer, "--subagent"])],
    }
    problems = [name for name in wanted if name not in hooks] + [name for name in hooks if name not in wanted]
    for name, expected in wanted.items():
        groups = hooks.get(name, [])
        if len(groups) != len(expected):
            problems.append(f"{name}: {len(groups)} groups, {len(expected)} wanted")
            continue
        for group, (matcher, args) in zip(groups, expected, strict=True):
            handler = group["hooks"][0]
            right = (
                len(group["hooks"]) == 1
                and group.get("matcher") == matcher
                and handler.get("type") == "command"
                and handler.get("command") == "sh"
                and handler.get("args") == args
                and isinstance(handler.get("timeout"), int)
                and all((SCRIPTS / Path(arg).name).is_file() for arg in args if not arg.startswith("--"))
            )
            if not right:
                problems.append(f"{name}: {group}")
    own = lychee.VERSION_SECONDS + lychee.HOOK_SECONDS  # the check after a write; before a write: none
    if own > start.GATE.hook_seconds:
        problems.append(
            f"PostToolUse: version probe {lychee.VERSION_SECONDS} s + run {lychee.HOOK_SECONDS} s = {own} s"
            f" is over the hook's budget of {start.GATE.hook_seconds:g} s"
        )
    assert not problems, str(problems)


@item(
    8,
    "the pointer to the skill is printed as typed here at session start and as a subagent's context,"
    " of the size MODULE.md states, naming a skill that exists",
)
def test_skill_pointer() -> None:
    """The pointer to the skill, run through `sh`: exit 0, the line as typed here and nothing on
    stderr; with `--subagent`, one JSON object whose `hookSpecificOutput` is exactly the event's
    name and the line as `additionalContext`. The line's size is the one MODULE.md states, and
    the qualified skill name in it names a folder under `skills/`."""
    plain = subprocess.run(
        [H.sh, str(SCRIPTS / "print-skill-pointer.sh")],
        input="{}",
        capture_output=True,
        text=True,
        check=False,
    )
    if plain.returncode != 0 or plain.stdout != POINTER or plain.stderr != "":
        pytest.fail(repr(plain))
    sub = subprocess.run(
        [H.sh, str(SCRIPTS / "print-skill-pointer.sh"), "--subagent"],
        input="{}",
        capture_output=True,
        text=True,
        check=False,
    )
    if sub.returncode != 0 or sub.stderr != "" or not sub.stdout.endswith("\n"):
        pytest.fail(repr(sub))
    answer = json.loads(sub.stdout)
    wanted = {
        "hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": POINTER.rstrip("\n")}
    }
    if answer != wanted or sub.stdout.count("\n") != 1:
        pytest.fail(f"the subagent's answer is {answer!r}")
    size = len(POINTER) - 1
    stated = re.search(r"pointer line, ([\d,]+) characters", (PLUGIN.parent / "MODULE.md").read_text())
    if not stated or int(stated.group(1).replace(",", "")) != size:
        pytest.fail(f"MODULE.md states another size than {size}")
    named = re.search(r"load the skill (const-referencing):([a-z-]+)\.", POINTER)
    if not named or not (PLUGIN / "skills" / named.group(2) / "SKILL.md").is_file():
        pytest.fail("the skill the line names is no folder under skills/")


@item(71, "the always-on rule is printed as typed here, and nothing else")
def test_chat_rule() -> None:
    done = subprocess.run(
        [H.sh, str(SCRIPTS / "print-chat-rule.sh")], input="{}", capture_output=True, text=True, check=False
    )
    ok = done.returncode == 0 and done.stdout == CHAT_RULE and done.stderr == ""
    assert ok, repr(done)


@item(
    72,
    "the skill's description fits the listing, matches the size MODULE.md states, and carries its"
    " trigger and its advisory line",
)
def test_skill_description_fits() -> None:
    """The description as the listing loads it — the folded scalar's final line break counted, as
    MODULE.md counts it — under the listing's 1,536 characters, of the size MODULE.md states, and
    carrying when to use the skill and that it is advisory."""
    text = (PLUGIN / "skills" / "referencing" / "SKILL.md").read_text()
    front = yaml.safe_load(text.split("---\n")[1])
    description = str(front["description"])
    size = len(description)
    found = re.search(r"skill listing, ([\d,]+) characters", (PLUGIN.parent / "MODULE.md").read_text())
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
    assert not problems, "; ".join(problems)


@item(73, "the install note's calibration example is accepted by the gate as it stands")
def test_install_note_example_is_accepted() -> None:
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
    expect(result, 2, finding.render(), "stderr")


# ------------------------------------------------------------------ found by the first validation


def porcelain(consumer: Consumer) -> str:
    return tree_state(consumer)


@item(80, "the mover asks everything that can refuse before it moves: no lychee, no root policy")
def test_mover_asks_before_it_moves() -> None:
    """Whatever the closing scan would fail on is asked before the file moves: no lychee, and
    governed_only with no root policy, are refusals that find the tree as it was."""
    no_lychee = moving_consumer()
    before = porcelain(no_lychee)
    merged = H.environment(path_with(None))
    done = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=no_lychee.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    broken_first_line(
        Result(done.returncode, done.stdout, done.stderr), messages.x1_no_lychee("0.24.2").render()
    )
    rootless = H.fresh_consumer((Write(OLD, ONE), Write("docs/notes/two.md", TWO)))
    rootless.write(
        "constitution.yaml", yaml.safe_dump({"module_prefix": "const-", NAMESPACE: {"governed_only": True}})
    )
    rootless.commit()
    state = porcelain(rootless)
    refused = mover(rootless, OLD, NEW)
    assert messages.v4_nothing_changed() in done.stderr and porcelain(no_lychee) == before, (
        "no lychee: the tree changed"
    )
    broken_first_line(  # typed by hand
        refused,
        "BROKEN: const-referencing.governed_only is set and constitution.yaml names no root_policy,"
        " so nobody can say which documents a move must repair — fix: name the root policy, or"
        " remove governed_only",
    )
    assert porcelain(rootless) == state and (rootless.root / OLD).exists(), "no root policy: the tree changed"


@item(81, "a failure after the move says the act stopped midway, never that nothing changed")
def test_mover_says_when_it_stopped_midway() -> None:
    """A failure after the move must not claim that nothing was changed."""
    consumer = moving_consumer()
    dying = 'case "$1" in --version) echo "lychee 0.24.2";; *) echo "error: gone wrong" >&2; exit 3;; esac\n'
    merged = H.environment(path_with(dying))
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
    assert ok, done.stdout + done.stderr


@item(82, "the mover keeps CRLF and a byte order mark, and leaves a file that is not UTF-8 alone")
def test_mover_keeps_every_other_character() -> None:
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
    assert after == crlf.replace("one.md", "../moved/deep/first.md"), f"CRLF document: {after!r}"
    assert b"Caf\xe9" in latin and b"(one.md)" in latin, "the latin-1 file was rewritten"
    assert messages.v2_left_alone("docs/notes/latin.md") in done.stdout, done.stdout
    assert (
        "LEFT ALONE: docs/notes/l\\\\y" + "n" * 80 + ".md is not UTF-8 text — its links, if any, were not"
        " repaired" in done.stdout.splitlines()
    ), done.stdout


@item(83, "a new path under a file, and a git mv that git refuses: refused, no directory left behind")
def test_mover_refuses_cleanly() -> None:
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
    broken_first_line(
        under_odd,
        f"BROKEN: {HOOK_SHOWN} is a file, so nothing can lie inside it — fix: name a new path whose"
        " directories exist or can be made",
    )
    broken_first_line(
        locked_odd,
        f"BROKEN: git mv refused: fatal: Unable to create '{parent}/{BS_DIR_SHOWN}/.git/index.lock':"
        " File exists. — fix: repair what git names, then run the move again",
    )
    broken_first_line(under_a_file, messages.v5_parent_is_a_file("docs/notes/two.md").render())
    assert locked.code == 1 and "BROKEN: git mv refused: " in locked.stderr, locked.stderr
    assert messages.v4_nothing_changed() in locked.stderr, "no closing line"
    assert not (consumer.root / "brand").exists(), "directories made for a move git refused were left behind"
    assert porcelain(consumer) == before, "the tree changed"


@item(84, "the mover escapes a space in a link; a longer name is no mention of a shorter one")
def test_mover_quotes_and_bounds() -> None:
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
    assert "See [a](new%20name.md)." in b, f"the link: {b}"
    expect(done, 0, messages.v4_count(1, 1, 0), "stdout")
    expect(scan(consumer), 0, "and 1 link(s) examined", "stdout")


@item(85, "reference-style links: a usage is a link, and is judged by what its label opens")
def test_reference_style_links() -> None:
    definitions = f"\n\n[o]: {TO_OWNER}\n[r]: ../policies/root-policy.md\n"
    astray = messages.r3_id_link_astray(DOC, LINE, OWNER_ID, "../policies/root-policy.md", OWNER, TO_OWNER)
    passes(f"# Fixture\nSee [`{OWNER_ID}`][o], [{OWNER_ID}][O] and [o].{definitions}")
    blocks(f"# Fixture\nSee [{OWNER_ID}][r].{definitions}", astray)
    passes(f"# Fixture\nSee [REQ-7][r].{definitions}")


@item(86, "a fence indented under a list item is code")
def test_a_fence_under_a_list_item() -> None:
    shown = "# F\n\n1. Configure:\n\n    ```yaml\n    # implements REQ-7\n\n    key: value\n    ```\n"
    deeper = "# F\n\n- a\n  - b\n\n      ~~~\n      REQ-7\n\n      more\n      ~~~\n"
    passes(shown)
    passes(deeper)


@item(87, "R4 leaves alone a route, an address, a tilde path and a bare home directory")
def test_what_is_no_path_on_one_machine() -> None:
    lines = [
        "The route `/home/feed` and the page https://example.invalid/home/ann/page are no machines.",
        "Neither is ~/Users/x, nor docs/home/ann/x.md, nor a bare /home/ or /Users/.",
    ]
    passes("# F\n\n" + "\n".join(lines) + "\n")


@item(88, "started inside the repository, the gate still takes nothing from its lychee files")
def test_owned_invocation_from_inside() -> None:
    """The gate started with the repository as its working directory — as a hook is — still takes
    nothing from the repository's own lychee files."""
    consumer = H.fresh_consumer()
    consumer.write(SOURCE, source("See [x](gone.md)."))
    consumer.write(".lycheeignore", "gone.md\n")
    consumer.write("lychee.toml", 'exclude_path = ["docs"]\n')
    merged = H.environment()
    done = subprocess.run(
        [H.sh, str(SCRIPTS / "check-references.sh"), "--scan"],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    finding = messages.r5_no_target(SOURCE, LINE, "gone.md")
    expect(Result(done.returncode, done.stdout, done.stderr), 2, finding.render(), "stdout")


@item(89, "one large document, and openers never closed, are judged in seconds")
def test_one_large_document() -> None:
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
            pytest.fail(f"{name}: exit {result.code} after {took:.1f} s: {result.stderr[:200]}")


@item(90, "after the write of an uncovered document, the covered links it broke are reported")
def test_uncovered_write_that_breaks_a_covered_link() -> None:
    only_source = own(territories=["*.md", "!" + TARGET])
    broken_target = TARGET_TEXT.replace('<a id="k1"></a>\n', "")
    files = {TARGET: broken_target, SOURCE: source("See [x](t.md#k1).")}
    finding = messages.r6_no_anchor(SOURCE, LINE, "t.md#k1", "k1", TARGET, None)
    harmless = {TARGET: TARGET_TEXT, SOURCE: source("See [x](t.md#k1).")}
    expect(after_write(TARGET, files, only_source), 2, finding.render(), "stderr")
    expect(
        after_write(TARGET, harmless, only_source),
        0,
        shared.g1_green_skip(messages.g1_skip_not_covered(TARGET)),
        "stdout",
    )


@item(91, "a misspelt dial is a configuration failure, never a setting ignored in silence")
def test_a_misspelt_dial() -> None:
    result, _ = gate_on(VALID, dials_patch=own(heading_anchor="allow"))
    broken_typed(
        result,
        "BROKEN: constitution.yaml: const-referencing.heading_anchor is no dial of this module — fix: a"
        " misspelt dial would be ignored in silence, so none is: write one of bare_ids, governed_only,"
        " heading_anchors, lanes, local_paths, log_dir, mentions, severity, territories",
    )


@item(92, "one break is one finding: R6 without R7, and said once for links alike on a line")
def test_one_break_one_finding() -> None:
    """A missing anchor is R6 and not R7 as well; two links alike on one line are one finding."""
    out = tree_scan("See [a](t.md#nope) and [b](t.md#nope).")
    ok = out.code == 2 and "RED: 1 finding(s)" in out.stdout and "resolves only through" not in out.stdout
    assert ok, out.stdout


@item(93, "an `a name` is an explicit anchor; an escaped path is read for R7")
def test_anchors_by_name_and_encoded_paths() -> None:
    named = note('# N\n\n<a name="old-style"></a>\n## Section Here\n', "note-n")
    spaced = "docs/notes/my dir/t.md"
    finding = messages.r7_heading_anchor(SOURCE, LINE, "my%20dir/t.md#first-section", spaced)
    expect(
        scan_of({"docs/notes/n.md": named, SOURCE: source("See [x](n.md#old-style).")}),
        0,
        "GREEN: ",
        "stdout",
    )
    expect(
        scan_of({spaced: TARGET_TEXT, SOURCE: source("See [x](my%20dir/t.md#first-section).")}),
        2,
        finding.render(),
        "stdout",
    )


@item(94, "a byte order mark does not open the YAML block to R4")
def test_byte_order_mark_before_the_block() -> None:
    text = "\ufeff" + document(
        "# F\n", id="note-a", type="non-authoritative", title="In /Users/ann/x.md", status="active"
    )
    expect(gate_on(Write(DOC, text))[0], 0, messages.g1_covered(), "stdout")


@item(95, "the scan's findings inside one document come in line order")
def test_scan_findings_in_line_order() -> None:
    out = scan_of(
        {TARGET: TARGET_TEXT, SOURCE: note("# S\nSee [x](gone.md).\nThen `note-t` bare.\n", "note-s")}
    ).stdout
    order = [out.find("link target gone.md"), out.find("document id 'note-t'")]
    assert -1 not in order and order == sorted(order), (
        "line 9 before line 10, whichever check found it" if order == sorted(order) else out
    )


@item(96, "a break of a kind the module has no text for is reported in the checker's words")
def test_a_break_in_words_of_lychee() -> None:
    """A kind of break this module has no text of its own for is reported in the checker's words."""
    plain = _lychee_words("Some new failure")
    odd = _lychee_words("Some\nnew failure\\ " + "w" * 90, "x\\y" + "n" * 100 + ".md")  # both only point: cut
    expect(
        plain,
        2,
        messages.r5_unresolved(SOURCE, LINE, "/nowhere/x.md", "Some new failure").render(),
        "stdout",
    )
    expect(
        odd,
        2,
        f"RED: {SOURCE}:{LINE}: link target /nowhere/x\\\\y" + "n" * 68 + "… [115 characters] does not"
        " resolve: Some\\nnew failure\\\\ " + "w" * 62 + "… [108 characters]",
        "stdout",
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


@item(97, "the mover's absences: no python3 and no shared code before the guard, no PyYAML inside it")
def test_mover_entry_absences() -> None:
    """The mover's own exits before the guard — no python3, an install without the shared code — and
    the shared C2 inside it, closed by the mover's clause."""
    consumer = moving_consumer()
    bare = H.scratch_dir()
    os.symlink(shutil.which("dirname") or "/usr/bin/dirname", bare / "dirname")
    no_python = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=H.environment({"PATH": str(bare)}),
        check=False,
    )
    no_shared = subprocess.run(  # the shared package missing for python3: no site-packages, no shared folder
        [sys.executable, "-S", str(SCRIPTS / "move-document.py"), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=H.environment({"PYTHONPATH": ""}, shared=False),
        check=False,
    )
    shadow = H.scratch_dir()  # the shared C2, printed by the preflight, closes with the mover's own clause
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_library = subprocess.run(
        [H.sh, str(MOVER), OLD, NEW],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=H.environment({"PYTHONPATH": str(shadow)}),
        check=False,
    )
    library_first = no_library.stderr.splitlines()[0] if no_library.stderr else ""
    closing = "BROKEN: the move could not run — nothing was changed"
    assert (
        no_python.returncode == 1
        and "BROKEN: const-referencing needs python3" in no_python.stderr
        and closing in no_python.stderr
    ), no_python.stderr
    assert (
        no_shared.returncode == 1
        and no_shared.stderr.splitlines()[0]
        == "BROKEN: const-referencing needs the Python package constitution-layer-kit 1.0.0 or a later 1.x"
        " release, and python3 cannot import it — fix: install it for python3 as"
        f" {PLUGIN / 'INSTALL.md'} says"
        and closing in no_shared.stderr
    ), no_shared.stderr
    assert (
        no_library.returncode == 1
        and library_first.endswith(" — until then nothing is moved")
        and "pass unchecked" not in no_library.stderr
        and closing in no_library.stderr
    ), no_library.stderr
    assert (consumer.root / OLD).exists(), "the file moved"


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


@item(98, "golden reasons: the why-line of every finding, typed by hand")
def test_golden_why_lines() -> None:
    """The reason of every finding, typed by hand: R1's is in the first golden item."""
    lint_runs = {str(case.expect.key): gate_on(case.red, dials_patch=LANES)[0].stderr for case in CASES[:4]}
    tree_out = tree_scan("See [a](gone.md), [b](t.md#nope) and [d](t.md#first-section).").stdout
    named = scan_of({SOURCE: source("x"), "tools/x.sh": "# note-gone\n"}, own(mentions=[MENTION])).stdout
    outputs = {**lint_runs, "R5": tree_out, "R6": tree_out, "R7": tree_out, "R8": named}
    missing = [key for key, line in WHYS.items() if line not in outputs[key]]
    assert not missing, f"not found: {missing}"


# ------------------------------------------------------------------ found by the second validation

DYING = 'case "$1" in --version) echo "lychee 0.24.2";; *) echo "error: gone wrong" >&2; exit 3;; esac\n'


def mover_with(consumer: Consumer, lychee_script: str | None, *arguments: str) -> Result:
    merged = H.environment(path_with(lychee_script))
    done = subprocess.run(
        [H.sh, str(MOVER), *arguments],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    return Result(done.returncode, done.stdout, done.stderr)


@item(99, "the act stopped midway: after the move alone, and after a rewrite with no move")
def test_midway_after_the_move_alone() -> None:
    """A lone document, nothing to rewrite: the move alone is a change, and the closing line
    must say so when the check dies after it."""
    alone = H.fresh_consumer((Write(OLD, note("# One\n", "note-one")),))
    done = mover_with(alone, DYING, OLD, NEW)
    by_hand = moving_consumer()
    (by_hand.root / NEW).parent.mkdir(parents=True)
    by_hand.git("mv", OLD, NEW)
    repaired = mover_with(by_hand, DYING, "--moved", OLD, NEW)
    assert done.code == 1 and messages.v4_stopped_midway() in done.stderr, f"move alone: {done.stderr}"
    assert repaired.code == 1 and messages.v4_stopped_midway() in repaired.stderr, (
        f"--moved: {repaired.stderr}"
    )
    assert "REWROTE: docs/notes/two.md" in repaired.stdout, "--moved rewrote nothing"


@item(100, "a fence closes at its opener's depth; a tab counts; one never closed masks to the end")
def test_fences_close_at_their_depth() -> None:
    """A fence closes at its opener's depth: a deeper fence shown inside it is content, not its
    end; a fence under a list item closes when indented like it, a tab counting."""
    inner = "1. Configure:\n\n    ```yaml\n    key: v\n    ```\n"
    shows_a_fence = "# F\n\nHow to:\n\n```\n" + inner + "```\n\nAfter it, REQ-7 is bare.\n"
    tabbed = "# F\n\n- item\n\n\t```\n\tcode REQ-9\n\t```\n\nAfter REQ-7.\n"
    unclosed_in_list = "# F\n\n- item\n\n    ```\n    REQ-9\n\nAfter REQ-7.\n"
    blocks(shows_a_fence, r1(line=20))
    blocks(tabbed, r1(line=16))
    passes(unclosed_in_list)


@item(74, "a footnote is no link: a bare form in it is red, a path in it is left alone")
def test_footnotes_are_no_links() -> None:
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
    blocks(with_footnote, named)
    expect(tree_scan("A claim.[^note]\n\n[^note]: t.md#first-section is named."), 0, "GREEN: ", "stdout")
    assert "[^1]: a.md was the first note." in prose and messages.v4_count(0, 0, 1) in moved.stdout, (
        f"footnote prose rewritten: {prose}"
    )


@item(75, "labels fold case; a usage inside a link's text is none; one R7 per definition")
def test_labels_fold_case_and_nest() -> None:
    passes(f"# Fixture\nSee [`{OWNER_ID}`][O].\n\n[o]: {TO_OWNER}\n")
    expect(tree_scan("See [x [o] y](t.md#k1).\n\n[o]: t.md\n"), 0, "and 2 link(s)", "stdout")
    passes("# Fixture\nSee [REQ-7]: and more.\n\n[REQ-7]: ../policies/root-policy.md\n")
    via_label = messages.r7_heading_anchor(SOURCE, 11, "t.md#first-section", TARGET)
    once = tree_scan("See [via][h] and [again][h].\n\n[h]: t.md#first-section\n")
    expect(once, 2, via_label.render(), "stdout")
    expect(once, 2, "1 finding(s)", "stdout")


@item(76, "R4: a PATH entry and C:/Users/ann/x are red; C:/Users/ann alone and tilde paths are not")
def test_r4_more_shapes() -> None:
    reds = [
        ("PATH: `PATH=/usr/bin:/home/ann/bin`", "/home/ann/bin"),
        ("Windows: `C:/Users/ann/x`", "C:/Users/ann/x"),
    ]
    for text, path in reds:
        blocks(body(text), messages.r4_one_machine(DOC, LINE, path))
    passes(body("Mine: ~/Users/x/y and ~/home/ann/z."))
    passes(body("A user's directory alone is a route: C:/Users/ann and C:\\Users\\ann\\ are one."))


@item(77, "a mention ends where the name does; an href is rewritten, not listed")
def test_a_mention_ends_where_the_name_does() -> None:
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
    assert messages.v4_count(1, 1, 0) in done.stdout, done.stdout
    assert '<a href="h/a.md">' in b, f"the href: {b}"


@item(78, "after a write, an older heading link elsewhere is not repeated")
def test_older_heading_link_not_repeated() -> None:
    files = {
        TARGET: TARGET_TEXT,
        SOURCE: source("See [x](t.md#first-section)."),
        "docs/notes/u.md": note("# U\n", "note-u"),
    }
    expect(after_write("docs/notes/u.md", files), 0, messages.g1_covered(), "stdout")


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
# typed by hand: the first line of a check before a write whose 20 s went on reading the tree; no checker
# is run before a write, so the line names the reading alone and does not say the references are unresolved
OUT_OF_TIME_BEFORE_TYPED = (
    "BROKEN: the check before a write used its 20 s reading the covered documents — fix: a large tree"
    " takes longer than that to read; run the scan, which waits as long as it takes — until then the"
    " references of this write are not checked"
)

# A run of the real entry point, `start.main`, with the budget's clock stood still and moved by hand: it
# advances by the seconds the environment names for the file list, for the territory matching, for each
# document read, each masked, once more at the first masking, and once at the version probe. Nothing waits
# for real. The trace holds one word per read and per masking, and what lychee's run was given as its
# timeout, with the clock then. The clock moved by hand is the check's own; the hook's deadline reads a
# clock of the driver's own that stands still, and HOOK_BUDGET declares the gate with that many seconds in
# place of its own.
BUDGET_DRIVER = """\
import dataclasses
import os
import subprocess
import sys
import types

sys.path.insert(0, {scripts!r})
from constitution_layer_kit import identity
from referencing_gate import lychee, modes, start, tree

# the hook's one deadline reads a clock that stands still, so it is the whole of its seconds at every wait:
# the real seconds before the check's budget begins, which a loaded machine stretches, never shorten it
identity.time = types.SimpleNamespace(monotonic=lambda: 0.0)
if os.environ.get("HOOK_BUDGET"):
    start.GATE = dataclasses.replace(start.GATE, hook_seconds=float(os.environ["HOOK_BUDGET"]))

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
        if not os.environ.get("PROBE_WAITS"):  # a probe that answers at once: no clock can cut it
            kwargs.pop("timeout", None)
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


def deadline_line(seconds: int, before: str) -> str:
    """The shared C12.14 line a wait the hook's deadline cut short ends in, for a gate declared with a hook
    budget of `seconds`: the wait is named by `before`, typed by hand in the case that asks for it."""
    return shared.c12_hook_budget(seconds, before).render()


# What a run cut at its timeout may take in all, the gate's start included. It only tells a cut run from one
# that waited out its fake's 30 s, so it stays far above any start a loaded machine takes; the trace's
# timeout and the line prove the cut. It was 6 s and, for the version probe, 8: those measured the machine,
# since the first start of a fake just written has taken 3.1 s on a loaded one.
CUT_BOUND = 20.0
BUDGET_LYCHEE = (  # logs the first argument of each call; says its version, then an empty report or nothing
    'echo "$1" >> "$LYCHEE_LOG"\ncase "$1" in --version) {wait}echo \'{version}\';; *) {run};; esac\n'
)


def on_a_patched_clock(
    clock: dict[str, str],
    run: str = "echo '{\"error_map\": {}}'",
    scan: bool = False,
    version: str | None = "lychee 0.24.2",
    event: str = AFTER,
    probe_seconds: int = 0,
) -> tuple[Result, list[str], list[str], float, int]:
    """The check after a write (or the scan; or, with `event`, the check before a write) of a tree of
    documents, run through the entry point with
    the clock patched as `clock` says (the seconds, as LIST_STEP, MATCH_STEP, MASK_FIRST, MASK_STEP, READ_STEP
    and PROBE_STEP). `version` is what the fake lychee says to --version, None for no lychee on PATH, after
    `probe_seconds` of real waiting where that is not 0. The fake is a file just written, whose first start
    on a loaded machine has taken seconds (0.2 to 3.1 s measured on macOS on 2026-10-16): so `path_with`
    starts the fake once before the run, the hook's deadline stands still on a clock of the driver's own,
    and a probe with no real wait runs with no clock; only the waits a case sets can run out. Gives
    the result, the trace, the fake lychee's own log of its calls, the real seconds it took, and the
    number of documents the tree holds."""
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text())
    consumer.write(TARGET, TARGET_TEXT)
    consumer.write(SOURCE, source("See [x](t.md)."))
    documents = sum(1 for found in consumer.root.rglob("*.md") if ".git" not in found.parts)
    scratch = H.scratch_dir()
    (scratch / "driver.py").write_text(BUDGET_DRIVER.format(scripts=str(SCRIPTS)))
    wait = f"{shutil.which('sleep') or '/bin/sleep'} {probe_seconds}; " if probe_seconds else ""
    waits = {"PROBE_WAITS": "1"} if probe_seconds else {}
    script = None if version is None else BUDGET_LYCHEE.format(run=run, version=version, wait=wait)
    env = {
        **path_with(script),
        "TRACE": str(scratch / "trace"),
        "LYCHEE_LOG": str(scratch / "lychee"),
        **waits,
        **clock,
    }
    stdin = "" if scan else event_json(consumer.root, Write(SOURCE, source("See [x](t.md).")), event=event)
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


def the_budget_is_one() -> None:
    """The check after a write has one deadline for the reads, the masking and lychee's run, and the
    check before a write the same deadline for its reads; the scan has none. Every case moves a patched
    clock by the document: the longest real wait is half a second, bar the probe cut by a hook of 2 s,
    which waits those 2. The hook's deadline stands still, so the seconds it leaves are exact.
    A wait the hook's deadline cut short that runs out ends in the shared C12.14 line, for each of the four
    waits: the probe, the run, the reads and the masking after a write, the reads before one.
    The order of two configuration failures is held here too: with a missing lychee and a document that
    cannot be read, the check after a write says X1 and the scan says C12.10."""
    # masking, document by document, passes the deadline at the last of them: no run, and one probe,
    # made before the budget began
    count = on_a_patched_clock({})[4]
    each = 20 / (count - 0.5)
    late, trace, ran, _, _ = on_a_patched_clock({"MASK_STEP": repr(each)})
    broken_typed(late, OUT_OF_TIME_TYPED)
    assert trace.count("mask") == count and trace.count("read") == count and ran == ["--version"], (
        f"{count} documents read and masked, lychee called: {ran}; trace {trace}"
    )
    # the first of several documents masked passes it: the clock is read after each document, so the
    # check stops there and the other documents are never masked
    first, trace, ran, _, _ = on_a_patched_clock({"MASK_FIRST": "25"})
    broken_typed(first, OUT_OF_TIME_TYPED)
    assert count > 1 and trace.count("mask") == 1 and trace.count("read") == count and ran == ["--version"], (
        f"{count} documents read, one masked, lychee probed and never run: trace {trace}, lychee {ran}"
    )
    # a read passes it before any masking starts (reading is counted)
    late, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"})
    broken_typed(late, OUT_OF_TIME_TYPED)
    assert trace == ["read"] and ran == ["--version"], (
        f"one read and no masking, lychee probed and never run: trace {trace}, lychee {ran}"
    )
    # the run is given what the reads and the masking left, never more than the budget
    spent = 9.0
    done, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": repr(3 / count), "MASK_STEP": repr(6 / count)})
    given = [line for line in trace if line.startswith("run ")]
    timeout, clock = (float(part.split("=")[1]) for part in given[0].split()[1:]) if given else (-1.0, 0.0)
    assert (
        done.code == 0
        and len(given) == 1
        and abs(clock - spent) < 1e-6
        and timeout == 20.0 - clock
        and 0 < timeout <= 20
    ), f"exit {done.code}, the run was given {timeout!r} s with the clock at {clock!r}: {trace}"
    # lychee's run times out with 0.5 s left: the line names the whole budget, not the half second
    hung, trace, ran, took, _ = on_a_patched_clock(
        {"MASK_FIRST": "19.5"}, run=f"exec {shutil.which('sleep') or '/bin/sleep'} 30"
    )
    broken_typed(hung, TOO_SLOW_TYPED)
    assert "run timeout=0.5 clock=19.5" in trace and took < CUT_BOUND, (
        f"the run was given 0.5 s and ended after {took:.1f} s: {trace}"
    )
    # the reads and the masking leave 0.005 s, the deadline not yet passed: the run is given the floor,
    # 0.01 s, never less; its timeout is the only place the floor shows
    near, trace, ran, _, _ = on_a_patched_clock(
        {"MASK_FIRST": "19.995"}, run=f"exec {shutil.which('sleep') or '/bin/sleep'} 30"
    )
    broken_typed(near, TOO_SLOW_TYPED)
    # the fake's own log is a race with the kill
    assert "run timeout=0.01 clock=19.995" in trace, (
        f"the run was given 0.01 s with 0.005 s left: trace {trace}"
    )
    # the version probe has its own seconds, before the budget begins: a probe that takes 25 s of the
    # patched clock leaves the run what the reads and the masking left of the whole 20 s
    probed, trace, ran, _, _ = on_a_patched_clock(
        {"PROBE_STEP": "25", "READ_STEP": repr(3 / count), "MASK_STEP": repr(6 / count)}
    )
    given = [line for line in trace if line.startswith("run ")]
    timeout, clock = (float(part.split("=")[1]) for part in given[0].split()[1:]) if given else (-1.0, 0.0)
    assert (
        probed.code == 0
        and ran == ["--version", "--offline"]
        and abs(clock - 34.0) < 1e-6
        and abs(timeout - 11.0) < 1e-6
    ), (
        f"exit {probed.code}, one probe, then the run was given {timeout!r} s with the clock at"
        f" {clock!r}: {trace}, lychee {ran}"
    )
    # the hook's own deadline, declared as 12 s, is shorter than the check's cap of 20 s: the run is given
    # what that deadline has left, all 12 s on its standing clock, never the cap
    short, trace, ran, _, _ = on_a_patched_clock({"HOOK_BUDGET": "12"})
    given = [line for line in trace if line.startswith("run ")]
    timeout = float(given[0].split()[1].split("=")[1]) if given else -1.0
    assert short.code == 0 and timeout == 12.0, (
        f"exit {short.code}, the run was given {timeout!r} s of a hook that declares 12 s: {trace}"
    )
    # a wait the hook's deadline cut short that then runs out ends in the deadline's shared line, naming the
    # wait and the hook's whole budget, never lychee's or the check's own line with the shortened number.
    # The run: given 0.5 s of a hook that declares 12 s, it hangs
    sleep = shutil.which("sleep") or "/bin/sleep"
    cut_run, trace, ran, took, _ = on_a_patched_clock(
        {"HOOK_BUDGET": "12", "MASK_FIRST": "11.5"}, run=f"exec {sleep} 30"
    )
    broken_typed(cut_run, deadline_line(12, "lychee finished the link check"))
    assert any(line.startswith("run timeout=0.") for line in trace) and took < CUT_BOUND, (
        f"the run was given under a second and ended after {took:.1f} s: {trace}"
    )
    # the reads of a check after a write pass that deadline before any masking
    cut_read, trace, ran, _, _ = on_a_patched_clock({"HOOK_BUDGET": "12", "READ_STEP": "25"})
    broken_typed(cut_read, deadline_line(12, "lychee finished the link check"))
    assert trace == ["read"] and ran == ["--version"], f"one read, lychee probed: {trace}, {ran}"
    # the check before a write: one read moves the clock past what the hook's 12 s leave, 15 s, and no
    # later document is read; with the cap of 20 s, which that budget must not be given, the second read
    # would be the one to pass it, and with the check's own line
    cut_before, trace, ran, _, _ = on_a_patched_clock({"HOOK_BUDGET": "12", "READ_STEP": "15"}, event=BEFORE)
    broken_typed(cut_before, deadline_line(12, "the covered documents were read"))
    assert count > 1 and trace == ["read"] and ran == [], f"{count} documents, one read: {trace}, {ran}"
    # the version probe of a check after a write: a hook that declares 2 s, a lychee that answers after 4 s,
    # under the probe's cap of 5 s; the probe is given what the deadline has left and is cut. Given its cap
    # it would answer, and the budget that follows would find the deadline spent and name itself
    cut_probe, trace, ran, took, _ = on_a_patched_clock(
        {"HOOK_BUDGET": "2"}, probe_seconds=int(lychee.VERSION_SECONDS) - 1
    )
    broken_typed(cut_probe, deadline_line(2, "lychee reported its version"))
    assert trace == [] and ran == ["--version"], (
        f"lychee probed, nothing read, after {took:.1f} s: {trace}, {ran}"
    )
    # lychee is missing or too old: whatever the tree's size and however the reads spend the budget,
    # the failure is the checker's own, X1 or X2, found before the first document is read
    no_lychee, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"}, version=None)
    broken_typed(no_lychee, X1_TYPED)
    assert trace == [] and ran == [], f"nothing read, no lychee: trace {trace}, lychee {ran}"
    old, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"}, version="lychee 0.23.0")
    broken_typed(old, X2_TYPED)
    assert trace == [] and ran == ["--version"], f"nothing read, one probe: trace {trace}, lychee {ran}"
    # a document nobody can read and no lychee together: the check after a write finds the checker before
    # it reads anything and says X1, the scan reads the texts first and says C12.10; the same tree with
    # the document readable says X1 in both, so the missing lychee is real in the scan too
    if os.geteuid() == 0:
        _not_exercised = (
            "NOT EXERCISED: running as root, where a mode bit does not deny a read, so the order of a"
            " missing lychee and an unreadable document is not pinned — 3 results skipped"
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
        broken_typed(hooked, X1_TYPED)
        broken_typed(scanned, unreadable_typed)
        broken_typed(readable, X1_TYPED)
    # the file list and the territory matching, which stand before the budget, take 25 s of the clock
    # each: the check still reads, masks and runs, the whole 20 s its own
    for step in ("LIST_STEP", "MATCH_STEP"):
        slow, trace, ran, _, _ = on_a_patched_clock({step: "25"})
        given = [line for line in trace if line.startswith("run ")]
        assert (
            slow.code == 0
            and trace.count("read") == count
            and trace.count("mask") == count
            and given == ["run timeout=20.0 clock=25.0"]
        ), f"{step}: exit {slow.code}, {count} documents read and masked, the run: {given}"
    # the check before a write has the same budget for its reads, and no checker to run or to find: a read
    # that passes the deadline stops it there with the X3 line in its before-a-write form, no later document
    # read, lychee neither probed nor run, however many it is told of
    before, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "25"}, event=BEFORE)
    broken_typed(before, OUT_OF_TIME_BEFORE_TYPED)
    assert count > 1 and trace == ["read"] and ran == [], (
        f"{count} documents, one read and nothing masked, lychee not called: trace {trace}, lychee {ran}"
    )
    # reads within the budget give the verdict they gave: green, with no lychee on PATH at all, as before
    within, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": repr(3 / count)}, version=None, event=BEFORE)
    assert within.code == 0 and trace.count("read") >= 1 and "mask" not in trace and ran == [], (
        f"exit {within.code}: {within.stderr[:200]}; trace {trace}, lychee {ran}"
    )
    # the file list and the territory matching stand before this budget too: 25 s of the clock each, the
    # reads are still all made
    for step in ("LIST_STEP", "MATCH_STEP"):
        slow, trace, ran, _, _ = on_a_patched_clock({step: "25"}, event=BEFORE)
        assert slow.code == 0 and trace.count("read") >= 1 and ran == [], (
            f"{step} before a write: exit {slow.code}: {slow.stderr[:200]}; trace {trace}"
        )
    # the scan has no clock: a patched one that runs far away changes nothing, and the run has no timeout
    scanned, trace, ran, _, _ = on_a_patched_clock({"READ_STEP": "1000", "MASK_STEP": "1000"}, scan=True)
    far = [line for line in trace if line.startswith("run timeout=None clock=")]
    assert (
        scanned.code == 0
        and scanned.stderr == ""
        and ran.count("--version") == 1
        and len(far) == 1
        and float(far[0].rsplit("=", 1)[1]) > 20 * count
    ), f"exit {scanned.code}: {scanned.stderr[:200]}; trace {trace}"


@item(
    79,
    "a link checker that hangs is a configuration failure inside the hook's timeout; the scan has none;"
    " no lychee and an unreadable document: X1 at the write, C12.10 in the scan",
)
def test_a_link_checker_that_hangs() -> None:
    """A checker that never answers is a configuration failure inside the hook's timeout, never
    a hook the platform gives up on: the version probe and the run have a budget each. The run's
    budget belongs to the check after a write, and it is one budget with the reading and the masking
    of the tree (`the_budget_is_one`): the scan waits for a slow checker, as long as it takes.
    The three runs go side by side, the longest about 21 s, and the budget cases follow one after the
    other: the item costs about 30 s. Each fake is started once before the runs (`path_with`), since the
    first start of a file just written has taken seconds on a loaded machine, and the hook run's deadline
    stands still (`git_patch`, `unclocked`): the start of a slow machine shortens no wait."""
    sleep = shutil.which("sleep") or "/bin/sleep"  # the fake's PATH holds no sleep
    slow_version = f'case "$1" in --version) {sleep} 30; echo "lychee 0.24.2";; *) exit 0;; esac\n'
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
    scan_env = path_with(slow_run)
    hook_env = {**path_with(slow_run), **git_patch(H, unclocked=True)[0]}

    def timed(stdin: str, args: list[str], env: dict[str, str]) -> tuple[Result, float]:
        began = time.monotonic()
        return H.run_gate(stdin, args=args, env=env), time.monotonic() - began

    with ThreadPoolExecutor(max_workers=3) as pool:
        probe = pool.submit(timed, "", ["--scan", str(consumer.root)], path_with(slow_version))
        scanned = pool.submit(timed, "", ["--scan", str(in_the_scan.root)], scan_env)
        hooked = pool.submit(timed, event, [], hook_env)
    result, took = probe.result()
    scan, scan_took = scanned.result()
    hook, hook_took = hooked.result()
    # typed by hand: the first line for a version probe that gave no answer in its 5 s, then the count line
    probe_typed = (
        "BROKEN: lychee gave no report: no answer in 5 s — fix: this is a defect of the gate's invocation"
        " or of the installed lychee, not of the repository; run lychee --version and report both to"
        " whoever maintains the plugin — until then no reference is checked for resolving"
    )
    broken_typed(result, probe_typed)
    hand_typed = TOO_SLOW_TYPED
    the_budget_is_one()
    assert result.code == 1 and 4 < took < CUT_BOUND, (
        f"the version: exit {result.code} after {took:.1f} s: {result.stderr}"
    )
    expect(scan, 0, shared.g1_green_scan(messages.f9_scan_tail(5, 1, 5, 0, 0, 0)), "stdout")
    assert scan_took > 20, f"the scan stopped after {scan_took:.1f} s: {scan.stdout[:160]}{scan.stderr[:160]}"
    broken_typed(hook, hand_typed)
    assert hook_took > 19, f"the check after a write gave up after {hook_took:.1f} s"


@item(69, "the mover refuses a directory, a name that is no Markdown, a link, and no repository")
def test_mover_refuses_what_would_leave_coverage() -> None:
    consumer = moving_consumer()
    (consumer.root / "docs/notes/link.md").symlink_to("one.md")
    consumer.commit()
    before = tree_state(consumer)
    refused = [
        (mover(consumer, OLD, "docs/newdir/"), messages.v5_names_a_directory("docs/newdir/")),
        (mover(consumer, OLD, "docs/notes/one.txt"), messages.v5_leaves_markdown(OLD, "docs/notes/one.txt")),
        (mover(consumer, "docs/notes/link.md", NEW), messages.v5_is_a_link("docs/notes/link.md")),
    ]
    for result, failure in refused:
        broken_first_line(result, failure.render())
    outside = H.scratch_dir()
    merged = H.environment()
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
    assert tree_state(consumer) == before, "the tree changed"
    assert nowhere.returncode == 1 and "is not inside a git repository" in nowhere.stderr, nowhere.stderr
    for result, line in odd_typed:
        broken_first_line(result, line)
    assert tree_state(odd) == odd_before, "a refusal of a long path changed the tree"
    assert nowhere_odd.returncode == 1 and nowhere_odd.stderr.startswith(
        f"BROKEN: {parent}/o{WEIRD_DIR_SHOWN} is not inside a git repository — fix: run the mover"
        " from inside the repository\n"
    ), nowhere_odd.stderr


@item(47, "a case-only rename is a move; a document moved out of coverage keeps its links")
def test_case_only_rename_and_uncovered_destination() -> None:
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
    expect(renamed, 0, messages.v1_moved(OLD, "docs/notes/One.md"), "stdout")
    # the others still reach
    expect(moved_out, 0, messages.v2_rewrote("docs/elsewhere/one.md", 1), "stdout")
    assert "[note-one](One.md#k1)" in two, f"inbound after the case rename: {two}"
    assert "[sib](../notes/two.md#k2)" in own_links, f"own links of the document moved out: {own_links}"
    assert "[note-one](../elsewhere/one.md#k1)" in (out.root / "docs/notes/two.md").read_text(), (
        "inbound to the document moved out"
    )


@item(49, "the mover routes its log to log_dir before any refusal")
def test_mover_routes_its_log() -> None:
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
    assert ok, f"log: {lines[-2:]}"


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


@item(39, "golden lines of the whole-tree findings, typed by hand")
def test_golden_tree_lines() -> None:
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
    assert not missing, f"not found: {missing}"


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
