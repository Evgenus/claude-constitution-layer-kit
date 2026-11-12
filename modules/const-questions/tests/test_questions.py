"""Fixtures of const-questions: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.

The fixture consumer is the shared one. Its three policies matter here only as Markdown files
the default territory covers: this gate resolves no policy and judges no envelope, so the
shared items about the root policy and about an unreadable envelope are not its own and are
skipped; their numbers stay free.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
import yaml
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import Broken, Finding
from constitution_layer_kit.testing.acceptance import broken_first_line, check_case, expect, item
from constitution_layer_kit.testing.consumer import Consumer, document
from constitution_layer_kit.testing.harness import (
    Case,
    Edit,
    Harness,
    Result,
    Write,
    event_json,
    red_lines,
)
from constitution_layer_kit.testing.items import (
    PatternDial,
    Subject,
    fake_claude,
    tr_call,
    tr_hook,
    tr_line,
    tr_turn,
)
from questions_gate import messages, start

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
# — and each is also typed by hand at least once in these fixtures (rule 14 of the gate-script rules)
H = Harness(SCRIPTS, "check-open-questions.sh", "check-open-questions.py", start.GATE.namespace)

NAMESPACE = start.GATE.namespace
DOC = "docs/notes/a.md"
OTHER = "docs/notes/b.md"


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps it working."""
    return {NAMESPACE: dict(dials)}


def claim(territory: Sequence[str]) -> dict[str, object]:
    return own(territories=list(territory))


def dials_text(patch: dict[str, object] | None = None) -> str:
    return yaml.safe_dump({**Consumer(Path()).dials, **(patch or {})}, sort_keys=False)


def note(body: str, doc_id: str = "note-a", title: str = "Fixture") -> str:
    return document(body, id=doc_id, type="non-authoritative", title=title, status="active")


def wrote(body: str, target: str = DOC) -> Write:
    return Write(target, note(body))


def line_of(text: str, needle: str) -> int:
    """The 1-based line that carries `needle` — so a case never hardcodes the envelope's height. A line
    ends at `\\n` alone, as the gate counts: a form feed or U+2028 inside a line does not end it."""
    for number, line in enumerate(text.split("\n"), start=1):
        if needle in line:
            return number
    raise AssertionError(needle)


def q1(action: Write, marker: str, needle: str, tail: str | None = None) -> Finding:
    """The finding the gate must teach for `action`: `needle` locates the line, `tail` is the
    line from the marker on (the needle itself when not given)."""
    return messages.q1_marker(action.target, line_of(action.text, needle), marker, tail or needle)


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


def broken(result: Result, failure: Broken) -> None:
    broken_first_line(result, failure.render())
    assert shared.c11_broken_count() in result.stderr, f"no count line after: {result.stderr.strip()}"


def passes(action: Write | Edit, **kwargs: object) -> None:
    result, _ = gate_on(action, **kwargs)  # type: ignore[arg-type]
    # typed by hand: what the green line says the document is
    expect(result, 0, shared.g1_green_hook("a covered document"), "stdout")


def blocked(action: Write | Edit, finding: Finding, **kwargs: object) -> None:
    result, _ = gate_on(action, **kwargs)  # type: ignore[arg-type]
    wanted = [f"RED: {finding.headline}", f"RED: 1 finding(s) — 1 document examined ({action.target})"]
    ok = result.code == 2 and finding.render() in result.stderr and red_lines(result.stderr) == wanted
    assert ok, f"exit {result.code}: {result.stderr[:500]}"


# ---------------------------------------------------------------- the module's own items

VALID = wrote("Nothing is open here.\n")
TBD = wrote("Owner: TBD: who owns this\n")
DECIDE = wrote("Shape: [decide: the dial's shape — default a list of `{a: [b]}` entries — decider <name>]\n")
FIXME = wrote("The count line is wrong, FIXME before the merge.\n")
TITLED = Write(DOC, note("Body.\n", title="TBD"))

CASES = [
    Case(1, "Q1: a TBD in the body", TBD, VALID, q1(TBD, "TBD", "TBD: who owns this"), messages.g1_covered()),
    Case(
        2,
        "Q1: a [decide: marker, holding a ] inside",
        DECIDE,
        VALID,
        q1(
            DECIDE,
            "[decide:",
            "[decide:",
            "[decide: the dial's shape — default a list of `{a: [b]}` entries — decider <name>]",
        ),
        messages.g1_covered(),
    ),
    Case(
        3,
        "Q1: a FIXME mid-sentence",
        FIXME,
        VALID,
        q1(FIXME, "FIXME", "FIXME before the merge."),
        messages.g1_covered(),
    ),
    Case(
        4,
        "Q1: an Edit that writes a TODO into an existing document is judged on the result",
        Edit(DOC, "Nothing is open here.", "Nothing is open here. TODO: check."),
        Edit(DOC, "Nothing is open here.", "Nothing is open here. Checked."),
        messages.q1_marker(DOC, line_of(VALID.text, "Nothing"), "TODO", "TODO: check."),
        messages.g1_covered(),
        setup=[VALID],
    ),
    Case(
        5,
        "Q1: a marker in the envelope is a marker",
        TITLED,
        VALID,
        messages.q1_marker(DOC, line_of(TITLED.text, "title:"), "TBD", "TBD"),
        messages.g1_covered(),
    ),
]


@pytest.mark.parametrize(
    "case", [pytest.param(case, id=f"T{case.number}", marks=item(case.number, case.title)) for case in CASES]
)
def test_case(case: Case) -> None:
    check_case(H, case)


@item(6, "quotations in code, glued words and other cases pass")
def test_quotations_pass() -> None:
    """A marker inside a code span or a fenced block is a quotation; a marker that is part of a
    word is none; the match is case-sensitive."""
    body = (
        "A `TODO` in a span, and ``a TBD in a double span``.\n"
        "```\nTODO inside a fence\n[decide: fenced]\n```\n"
        "~~~text\nFIXME in a tilde fence\n~~~\n"
        "TODOs, TODO_LIST, todo, fixme, tbd and Tbd are none.\n"
        "   ```\n   TODO in an indented fence\n   ```\n"
    )
    passes(wrote(body))
    # a form feed or U+2028 is no line end: a fence is closed by a line of its own, and a fence line
    # that holds the closer's characters after one is still inside the block
    odd = "```\nTODO a\x0c```\nTODO b ```\nTBD c\n```\nA `TBD`\x0c and ``a FIXME``  in spans.\n"
    passes(wrote(odd))


@item(7, "word boundaries: punctuation keeps a marker, a glued letter or digit unmakes it")
def test_boundaries_hold() -> None:
    """Punctuation beside a marker keeps it a marker; a letter or a digit glued to it does not."""
    for text, marker in (
        ("(TODO)", "TODO"),
        ("#TBD.", "TBD"),
        ("x FIXME", "FIXME"),
        ("a [decide:]", "[decide:"),
    ):
        blocked(wrote(text + "\n"), q1(wrote(text + "\n"), marker, text, text[text.index(marker) :]))
    for text in ("TODO1", "1TODO", "xTBDx", "FIXMEs"):
        passes(wrote(text + "\n"))


@item(8, "an open fence masks to the end; a closer must match")
def test_open_fence_masks_to_the_end() -> None:
    """An unclosed fence hides everything after it (a limit the module document states); a closer
    of the other character, or a shorter one, does not close it; a backtick opener whose info
    string holds a backtick is no opener; a closer with any text after it closes."""
    passes(wrote("```\nTODO\n~~~\nTBD\n``\nFIXME\n"))
    action = wrote("````\nTODO\n```\nTBD\n````\nFIXME here\n")
    blocked(action, q1(action, "FIXME", "FIXME here"))
    spans = wrote("```foo`bar\nTODO after a span line, not a fence\n")  # a backtick in the info string
    blocked(spans, q1(spans, "TODO", "TODO after a span line, not a fence"))
    closer = wrote("```\nTODO\n``` x`y\nTBD here\n")  # a closer with any text after it closes
    blocked(closer, q1(closer, "TBD", "TBD here"))


@item(9, "one finding per line, in line order, counted")
def test_one_hit_per_line_in_order() -> None:
    """Two markers on one line: one finding, the one that stands first; two lines: two findings
    in line order, and the count says two."""
    action = wrote("First TBD then TODO.\nThen [decide: x] after.\n")
    result, _ = gate_on(action)
    first = messages.q1_marker(DOC, line_of(action.text, "First"), "TBD", "TBD then TODO.")
    second = messages.q1_marker(DOC, line_of(action.text, "Then"), "[decide:", "[decide: x] after.")
    wanted = [
        f"RED: {first.headline}",
        f"RED: {second.headline}",
        f"RED: 2 finding(s) — 1 document examined ({DOC})",
    ]
    assert result.code == 2 and red_lines(result.stderr) == wanted, result.stderr[:600]
    # a form feed or U+2028 inside a line before the marker moves no line number: lines end at "\n" alone
    odd = wrote("Page\x0cbreak.\nNext para, then TBD here.\n\x0c\nLast\x0cline [decide: y] end.\n")
    result, _ = gate_on(odd)
    wanted = [
        f"RED: {q1(odd, 'TBD', 'Next', 'TBD here.').headline}",
        f"RED: {q1(odd, '[decide:', 'Last', '[decide: y] end.').headline}",
        f"RED: 2 finding(s) — 1 document examined ({DOC})",
    ]
    assert result.code == 2 and red_lines(result.stderr) == wanted, result.stderr[:600]
    # a code span before the marker is blanked at its own length: the finding quotes from the marker on
    spanned = wrote("Use `x` then TODO here.\n")
    result, _ = gate_on(spanned)
    at = line_of(spanned.text, "Use")
    wanted = [
        f"RED: docs/notes/a.md:{at}: open question marker 'TODO' — TODO here.",
        "RED: 1 finding(s) — 1 document examined (docs/notes/a.md)",
    ]
    assert result.code == 2 and red_lines(result.stderr) == wanted, result.stderr[:600]


@item(10, "the markers dial replaces the defaults")
def test_own_markers() -> None:
    """The markers dial replaces the defaults: a project's own text is found, a default no more;
    a marker made of punctuation needs no boundary."""
    patch = own(markers=["OPEN QUESTION", "??"])
    action = wrote("TODO is fine now; OPEN QUESTION: who?\n")
    blocked(action, q1(action, "OPEN QUESTION", "OPEN QUESTION", "OPEN QUESTION: who?"), dials_patch=patch)
    glued = wrote("Really??\n")
    blocked(glued, q1(glued, "??", "Really", "??"), dials_patch=patch)
    passes(wrote("TODO and TBD pass under the project's own markers.\n"), dials_patch=patch)
    # two markers that start at the same column: the one listed first is named
    tied = wrote("TODO: x\n")
    result, _ = gate_on(tied, dials_patch=own(markers=["TODO", "TODO:"]))
    wanted = [
        f"RED: docs/notes/a.md:{line_of(tied.text, 'TODO')}: open question marker 'TODO' — TODO: x",
        "RED: 1 finding(s) — 1 document examined (docs/notes/a.md)",
    ]
    assert result.code == 2 and red_lines(result.stderr) == wanted, result.stderr[:600]


@item(11, "territories decide coverage; a top-level README is covered")
def test_territories_decide_coverage() -> None:
    """A document outside the territories is a visible skip naming the dial; a README at the top
    is covered by the default and examined."""
    result, _ = gate_on(TBD, dials_patch=claim(["docs/other/**"]))
    skip = shared.g1_green_skip(messages.g1_skip_not_covered(DOC))
    expect(result, 0, skip, "stdout")
    readme = Write("README.md", "# Top\n\nTBD\n")
    blocked(readme, messages.q1_marker("README.md", 3, "TBD", "TBD"))
    # an uncovered path over 80 characters with a line break is said whole, the break escaped
    weird = "docs/notes/a\n" + "b" * 100 + ".md"
    wide, _ = gate_on(wrote("TBD\n", target=weird), dials_patch=claim(["docs/other/**"]))
    line = (
        "GREEN: const-questions: 0 documents examined — docs/notes/a\\n"
        + "b" * 100
        + ".md is not covered (const-questions.territories)"
    )
    expect(wide, 0, line, "stdout")


@item(12, "this module's dial failures, exit 1, lines typed by hand")
def test_dial_failures() -> None:
    """This module's own C5 lines, typed by hand, each exit 1 — never 2, never 0."""
    pairs: list[tuple[dict[str, object], str]] = [
        (
            own(marker=["x"]),
            "BROKEN: constitution.yaml: const-questions.marker is no dial of this module — fix: a misspelt"
            " dial would be ignored in silence, so none is: write one of severity, log_dir, territories,"
            " markers, preferences, boundary_examples",
        ),
        (
            own(territories=[]),
            "BROKEN: constitution.yaml: const-questions.territories must be a non-empty list of path patterns"
            ' — fix: write the patterns of the documents to cover, one per line under "- ", or leave the key'
            " out to cover every Markdown file; an empty list would examine nothing in silence",
        ),
        (
            own(territories="*.md"),
            "BROKEN: constitution.yaml: const-questions.territories must be a non-empty list of path patterns"
            ' — fix: write the patterns of the documents to cover, one per line under "- ", or leave the key'
            " out to cover every Markdown file; an empty list would examine nothing in silence",
        ),
        (
            own(markers=[]),
            "BROKEN: constitution.yaml: const-questions.markers must be a non-empty list of non-empty"
            " one-line texts"
            ' — fix: write the marker texts to look for, one per line under "- ", in single quotes, or'
            " leave the key out for the defaults '[decide:', 'TODO', 'TBD', 'FIXME'; an empty list would"
            " examine nothing in silence",
        ),
        (
            own(markers=["TODO", ""]),
            "BROKEN: constitution.yaml: const-questions.markers must be a non-empty list of non-empty"
            " one-line texts"
            ' — fix: write the marker texts to look for, one per line under "- ", in single quotes, or'
            " leave the key out for the defaults '[decide:', 'TODO', 'TBD', 'FIXME'; an empty list would"
            " examine nothing in silence",
        ),
        (
            own(markers=["TO\nDO"]),
            "BROKEN: constitution.yaml: const-questions.markers must be a non-empty list of non-empty"
            " one-line texts"
            ' — fix: write the marker texts to look for, one per line under "- ", in single quotes, or'
            " leave the key out for the defaults '[decide:', 'TODO', 'TBD', 'FIXME'; an empty list would"
            " examine nothing in silence",
        ),
        (
            own(markers=["TO\rDO"]),
            "BROKEN: constitution.yaml: const-questions.markers must be a non-empty list of non-empty"
            " one-line texts"
            ' — fix: write the marker texts to look for, one per line under "- ", in single quotes, or'
            " leave the key out for the defaults '[decide:', 'TODO', 'TBD', 'FIXME'; an empty list would"
            " examine nothing in silence",
        ),
        (
            own(markers=[1]),
            "BROKEN: constitution.yaml: const-questions.markers must be a non-empty list of non-empty"
            " one-line texts"
            ' — fix: write the marker texts to look for, one per line under "- ", in single quotes, or'
            " leave the key out for the defaults '[decide:', 'TODO', 'TBD', 'FIXME'; an empty list would"
            " examine nothing in silence",
        ),
    ]
    for patch, line in pairs:
        result, _ = gate_on(VALID, dials_patch=patch)
        broken_first_line(result, line)
        assert shared.c11_broken_count() in result.stderr, f"{patch}: no count line: {result.stderr.strip()}"
    passes(VALID, dials_patch=own(preferences=[{"decider": "x"}], boundary_examples=[{"ask": "a"}]))


@item(13, "the scan: order, count tail, warn ignored, green tail")
def test_scan_reports_in_order() -> None:
    """The scan: every finding in path and line order, the count tail typed by hand, exit 2 under
    warn too; green with the tail typed by hand; a document outside the territories not examined."""
    files = {
        DOC: note("TBD one\n\nTBD two\n"),
        OTHER: note("Fine.\n", doc_id="note-b"),
        "docs/notes/c.md": note("FIXME\n", doc_id="note-c"),
        "out/d.md": "# Out\n\nTODO\n",
    }
    result = scan_of(
        files, dials_patch={**claim(["docs/**"]), **own(severity="warn", territories=["docs/**"])}
    )
    a = note("TBD one\n\nTBD two\n")
    c = files["docs/notes/c.md"]
    wanted = [
        f"RED: {messages.q1_marker(DOC, line_of(a, 'TBD one'), 'TBD', 'TBD one').headline}",
        f"RED: {messages.q1_marker(DOC, line_of(a, 'TBD two'), 'TBD', 'TBD two').headline}",
        f"RED: {messages.q1_marker('docs/notes/c.md', line_of(c, 'FIXME'), 'FIXME', 'FIXME').headline}",
        "RED: 3 finding(s) — 6 document(s) examined for 4 marker(s), 7 Markdown file(s) scanned",
    ]
    assert result.code == 2 and red_lines(result.stdout) == wanted, (
        f"exit {result.code}: {result.stdout[:800]}"
    )
    green = scan_of({DOC: note("Fine.\n")})
    line = "GREEN: const-questions: 4 document(s) examined for 4 marker(s), 4 Markdown file(s) scanned"
    expect(green, 0, line, "stdout")


@item(14, "golden lines of Q1 and the cut of a long line")
def test_golden_lines() -> None:
    """Q1's three lines typed by hand, character for character, against a fresh run — so a why
    emptied or a word lost inside the message function is red; and a long line cut, the cut said."""
    result, _ = gate_on(TBD)
    lines = [
        f"RED: {DOC}:{line_of(TBD.text, 'Owner')}: open question marker 'TBD' — TBD: who owns this",
        "  why: a delivered document holds resolved decisions only: a marker left in it defers the question"
        " to a reader who may never see it",
        "  fix: resolve the question in the text; if the decider is absent, replace the marker by a named"
        " blocker — 'blocked: <who> must decide <what>' — and halt that part; a draft whose own convention"
        " keeps markers until delivery is taken out of const-questions.territories by a negated pattern in"
        " constitution.yaml",
    ]
    assert "\n".join(lines) in result.stderr, f"expected:\n{chr(10).join(lines)}\ngot:\n{result.stderr[:900]}"
    # the echoed line has a backslash and 209 characters: cut at 80, the cut said, then escaped
    long = wrote("TODO a\\b " + "y" * 200 + "\n")
    result, _ = gate_on(long)
    head = (
        f"RED: {DOC}:{line_of(long.text, 'TODO')}: open question marker 'TODO' — TODO a\\\\b "
        + "y" * 71
        + "… [209 characters]"
    )
    assert head in result.stderr and "y" * 72 not in result.stderr, result.stderr[:400]
    # a marker of the project's own holding a backslash only points: shown escaped
    own_marker = wrote("X\\Y: who decides\n")
    result, _ = gate_on(own_marker, dials_patch=own(markers=["X\\Y"]))
    marked = (
        f"RED: {DOC}:{line_of(own_marker.text, 'X')}: open question marker 'X\\\\Y' — X\\\\Y: who decides"
    )
    assert marked in result.stderr, result.stderr[:400]
    # a marker of 103 characters, with the backslash, is cut at 80 and the cut said, in its own place
    # and again in the echoed line, which runs on to 116 characters
    long_marker = "X\\Y" + "Z" * 100
    long_doc = wrote(long_marker + ": who decides\n")
    result, _ = gate_on(long_doc, dials_patch=own(markers=[long_marker]))
    cut = "X\\\\Y" + "Z" * 77
    cut_both = (
        f"RED: {DOC}:{line_of(long_doc.text, 'X')}: open question marker '{cut}… [103 characters]' — "
        f"{cut}… [116 characters]"
    )
    assert cut_both in result.stderr, result.stderr[:400]
    # the written file's path, over 80 characters with a line break, is shown whole, the break escaped,
    # in the headline and in the count line
    weird = "docs/notes/a\n" + "b" * 100 + ".md"
    shown_path = "docs/notes/a\\n" + "b" * 100 + ".md"
    result, _ = gate_on(wrote("TBD: who owns this\n", target=weird))
    at_line = line_of(note("TBD: who owns this"), "TBD")
    path_lines = [
        f"RED: {shown_path}:{at_line}: open question marker 'TBD' — TBD: who owns this",
        f"RED: 1 finding(s) — 1 document examined ({shown_path})",
    ]
    assert result.code == 2 and red_lines(result.stderr) == path_lines, result.stderr[:600]


SHAPE = (
    "const-questions (advisory): a choice put to the user takes one shape, in the chat message, one decision"
    " per message. Options lettered A, B, C…, each a bullet: the bold letter and title with a one-sentence"
    " description on the first line; beneath it two indented sub-bullets, **Pros:** and **Cons:**, one prose"
    " line each — never inline in the description, never a table. Then exactly one recommendation with its"
    " reasoning, and the decider named. A one-fact clarification is a plain line and takes none of this."
    " Whether to ask at all, the tool or the letter, and the project's preferences are the skill"
    " ask-or-decide: load it before putting any choice.\n"
)


@item(15, "the hooks file's shape")
def test_hooks_file() -> None:
    """Two handlers, each in the exec form with an explicit timeout: the gate on Write|Edit, the
    session-start printer without a matcher; both scripts present."""
    hooks = json.loads((SCRIPTS.parent / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    wanted = {
        "PreToolUse": ("Write|Edit", ["${CLAUDE_PLUGIN_ROOT}/scripts/check-open-questions.sh"]),
        "SessionStart": (None, ["${CLAUDE_PLUGIN_ROOT}/scripts/print-decision-shape.sh"]),
    }
    problems = [name for name in wanted if name not in hooks] + [name for name in hooks if name not in wanted]
    for name, (matcher, args) in wanted.items():
        groups = hooks.get(name, [])
        if len(groups) != 1:
            problems.append(f"{name}: {len(groups)} handler(s)")
        for group in groups:
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
    wired = messages.c12_event("x").fix  # the C12 fix names the event and matcher the file wires
    problems += [
        f"{name} on {matcher}: not in the C12 fix"
        for name, (matcher, _) in wanted.items()
        if matcher is not None and f"{name} on {matcher}" not in wired
    ]
    assert not problems, str(problems)


@item(20, "the session-start text as typed, its size stated, its phrases in the skill")
def test_decision_shape_printed() -> None:
    """The session-start text: exit 0, the text as typed here character for character, nothing
    on stderr, of the size the module document and the install note state; and every phrase it
    shares with the skill's shape section stands in the skill too, so the two carriers cannot
    drift apart."""
    done = subprocess.run(
        [H.sh, str(SCRIPTS / "print-decision-shape.sh")],
        input="{}",
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0 and done.stdout == SHAPE and done.stderr == "", repr(done)
    size = len(SHAPE) - 1
    stated = re.search(
        r"printed by the `SessionStart` hook, (\d+) characters",
        (SCRIPTS.parent.parent / "MODULE.md").read_text(encoding="utf-8"),
    )
    assert stated and int(stated.group(1)) == size, f"the module document states another size than {size}"
    install = " ".join((SCRIPTS.parent / "INSTALL.md").read_text(encoding="utf-8").split())
    assert f"{size} characters, advisory" in install, f"the install note states another size than {size}"
    # the skill's prose is wrapped at 100 columns, so a phrase may carry a line break inside it
    skill = " ".join(
        (SCRIPTS.parent / "skills" / "ask-or-decide" / "SKILL.md").read_text(encoding="utf-8").split()
    )
    shared_phrases = (
        "one decision per message",
        "**Pros:**",
        "**Cons:**",
        "one prose line each",
        "never inline in the description",
        "never a table",
        "exactly one recommendation",
        "ask-or-decide",
    )
    missing = [phrase for phrase in shared_phrases if phrase not in SHAPE or phrase not in skill]
    assert not missing, f"phrases not in both carriers: {missing}"


@item(16, "the skill description's size and lines; the install note's example")
def test_skill_and_install_note() -> None:
    root = SCRIPTS.parent
    text = (root / "skills" / "ask-or-decide" / "SKILL.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---")[1])
    assert front["name"] == "ask-or-decide" and 0 < len(front["description"]) <= 1536, (
        "name or description size"
    )
    assert "Use when " in front["description"] and "Advisory:" in front["description"], (
        "the description carries no 'Use when ' trigger or no 'Advisory:' line"
    )
    assert "Load this skill first" in front["description"], "the description does not ask to be loaded first"
    size = len(front["description"])
    stated = re.search(
        r"skill listing, (\d+) characters", (root.parent / "MODULE.md").read_text(encoding="utf-8")
    )
    assert stated and int(stated.group(1)) == size, f"the module document states another size than {size}"
    install = (root / "INSTALL.md").read_text(encoding="utf-8")
    assert "MODULE.md" not in install, (
        "the install note names the module document, which a consumer does not hold"
    )
    block = install.split("```yaml", 1)[1].split("```", 1)[0]
    example = yaml.safe_load(block)
    result = scan_of({DOC: note("Fine.\n"), "drafts/x.md": "TODO\n"}, dials_patch=example)
    expect(result, 0, "GREEN: const-questions: 4 document(s) examined for 4 marker(s), 5 Markdown", "stdout")


@item(17, "an event the gate is not wired to is C12")
def test_other_event_refused() -> None:
    """A PostToolUse event, which this gate is not wired to, is this module's own C12."""
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", dials_text())
    consumer.write(DOC, VALID.text)  # on disk, so that the event reaches the gate's own check
    result = H.run_gate(event_json(consumer.root, VALID, event="PostToolUse"))
    line = (
        "BROKEN: hook input names the event 'PostToolUse', which this gate is not wired to — fix: wire the"
        " gate to PreToolUse on Write|Edit, as the plugin's hooks file does; to check a repository by hand"
        " run it with --scan [<dir>]"
    )
    broken_first_line(result, line)
    # an event name that holds a line break and is 105 characters only points: cut at 80, then escaped
    odd = H.run_gate(event_json(consumer.root, VALID, event="Post\n" + "T" * 100))
    cut = (
        "BROKEN: hook input names the event 'Post\\n"
        + "T" * 75
        + "… [105 characters]', which this gate is not wired to — fix: wire the gate to PreToolUse on"
        " Write|Edit, as the plugin's hooks file does; to check a repository by hand run it with --scan"
        " [<dir>]"
    )
    broken_first_line(odd, cut)


@item(19, "an envelope nested past the parser's depth is no crash, and is judged")
def test_deep_envelope_is_no_crash() -> None:
    """An envelope nested past the parser's depth is judged for markers like any text and is no
    crash: this gate reads no envelope, so the shared item about one is not its own."""
    passes(Write(DOC, "---\nid: " + "[" * 5000 + "]" * 5000 + "\n---\n\nFine.\n"))
    deep = Write(DOC, "---\nid: " + "[" * 5000 + "\n---\n\nTBD here\n")
    blocked(deep, q1(deep, "TBD", "TBD here"))


@item(18, "an Edit is judged on the result")
def test_edit_removing_a_marker_passes() -> None:
    """The document judged is the one after the write: an Edit that takes the marker out passes,
    and one that leaves another marker in place is blocked on that one."""
    two = note("TBD one\n\nTBD two\n")
    passes(Edit(DOC, "TBD", "Done", replace_all=True), files={DOC: two})
    action = Edit(DOC, "TBD one", "Done one")
    blocked(action, messages.q1_marker(DOC, line_of(two, "TBD two"), "TBD", "TBD two"), files={DOC: two})


# ---------------------------------------------------------------- the effect report (items 21 to 28)
# Each rule of the module's section "Effect" runs through the real entry `effect-report.sh` over transcripts
# made by hand and, for the history rules, a scratch git repository. The lines asserted are typed by hand.

EFFECT = SCRIPTS / "effect-report.sh"
WAY_AT = "2026-11-03T10:00:00.000Z"
SKILL_NAME = "const-questions:ask-or-decide"


def tr_tool(sid: str, cwd: Path, call_id: str, name: str, **given: object) -> str:
    """A tool call of any tool, with its input as given."""
    block = {"type": "tool_use", "id": call_id, "name": name, "input": given}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def tr_say(sid: str, cwd: Path, text: str) -> str:
    block = {"type": "text", "text": text}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def tr_red(sid: str, cwd: Path, call_id: str, text: str) -> str:
    """A call the module's PreToolUse hook refused, as Claude Code records it (observed on 2.1.286): only in
    the call's tool result, the command named in brackets as `command hook <n>`, the plugin at the end."""
    refusal = {
        "type": "tool_result",
        "tool_use_id": call_id,
        "is_error": True,
        "content": f"PreToolUse:Write hook error: [command hook 3]: {text}\n\n"
        "This hook comes from the const-questions@fixture-marketplace plugin.",
    }
    return tr_line("user", sid, cwd, WAY_AT, message={"role": "user", "content": [refusal]})


def tr_red_attached(sid: str, cwd: Path, call_id: str, text: str) -> str:
    """A run of the module's hook script that blocked its call, recorded as an attachment with the script."""
    done = {
        "type": "hook_blocking_error",
        "hookName": "PreToolUse:Write",
        "toolUseID": call_id,
        "hookEvent": "PreToolUse",
        "blockingError": {"blockingError": f"[sh /x/plugin/scripts/check-open-questions.sh]: {text}"},
    }
    return tr_line("attachment", sid, cwd, WAY_AT, attachment=done)


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


def options(
    *parts: str, closing: str = "Recommendation: B, because it is the smaller change.\nDecider: you.\n"
) -> str:
    """A message of lettered options: `parts` are the bullets, each already with its sub-bullets."""
    return "Which one do you want?\n\n" + "".join(parts) + "\n" + closing


def option(letter: str, pros: bool = True, cons: bool = True) -> str:
    text = f"- **{letter}. Option {letter}** — one sentence.\n"
    text += "  - **Pros:** a gain.\n" if pros else ""
    return text + ("  - **Cons:** a cost.\n" if cons else "")


@item(21, "W1: a covered Markdown write is applied when a hook run examined it, else bypassed by B1")
def test_effect_path_bypass() -> None:
    """A write examined by a run of the gate's hook is applied; a write no run examined, a shell redirect, a
    shell redirect to a README and a write through a worktree of the project are bypassed by B1, the
    worktree's read as the path in the root. A file taken out of the territories by a negated pattern, one
    that is no Markdown and a path outside the project are no moment."""
    consumer = H.fresh_consumer()
    consumer.write_dials(claim(["*.md", "!drafts/**"]))
    root, sid = consumer.root, "s21"
    worktree = root / ".claude" / "worktrees" / "w" / "docs" / "w.md"
    lines = [
        tr_call(sid, root, WAY_AT, "t1", "Write", root / "docs" / "a.md"),
        tr_hook(sid, root, WAY_AT, "t1", "check-open-questions.sh"),
        tr_call(sid, root, WAY_AT, "t2", "Write", root / "docs" / "b.md"),
        tr_tool(sid, root, "t3", "Bash", command="echo x > docs/c.md"),
        tr_tool(sid, root, "t4", "Bash", command="echo x > README.md"),
        tr_call(sid, root, WAY_AT, "t5", "Write", worktree),
        tr_call(sid, root, WAY_AT, "t6", "Write", root / "drafts" / "d.md"),
        tr_call(sid, root, WAY_AT, "t7", "Write", root / "docs" / "e.txt"),
        tr_call(sid, root, WAY_AT, "t8", "Write", Path("/elsewhere/docs/f.md")),
    ]
    found = effect_lines(root, {sid: lines}, no_plugins())
    wanted = "  W1 (pattern): 5 moment(s): 1 applied, 4 bypassed, 0 missed — B1 4"
    assert wanted in found, found
    # with no dials file the gate skips every file, so no write is a moment
    bare = H.fresh_consumer()
    (bare.root / "constitution.yaml").unlink()
    bare.commit()
    alone = [tr_call("s21b", bare.root, WAY_AT, "t1", "Write", bare.root / "docs" / "a.md")]
    found = effect_lines(bare.root, {"s21b": alone}, no_plugins())
    assert "  W1 (pattern): 0 moment(s): 0 applied, 0 bypassed, 0 missed" in found, found


@item(22, "W2: the plugin disabled, or a dial of the gate loosened, is bypassed by B2")
def test_effect_switch_off() -> None:
    """Eight commits of the dials file, the namespace changed at each: the namespace added at severity warn,
    an adoption that lowers nothing (applied); severity block (applied); the defaults written out with no
    severity (applied); severity warn where none stood, so from the default block (bypassed); the markers cut
    to one (bypassed); a marker added (applied); a negated territory added (bypassed); that negation removed
    (applied). A fake plugin list that lists the gate for this project disabled adds one more, bypassed.
    Then a second project, whose commits tell each loosened dial apart: adopted at block (applied); the
    markers cut to one (bypassed); a territory pattern added (applied); that pattern dropped (bypassed). The
    lines are typed by hand."""
    consumer = H.fresh_consumer()
    root = consumer.root
    defaults = ["[decide:", "TODO", "TBD", "FIXME"]
    steps = [
        own(severity="warn"),
        own(severity="block"),
        own(markers=defaults),
        own(markers=defaults, severity="warn"),
        own(markers=["TODO"]),
        own(markers=["TODO", "XXX"]),
        own(markers=["TODO", "XXX"], territories=["*.md", "!drafts/**"]),
        own(markers=["TODO", "XXX"], territories=["*.md"]),
    ]
    for step in steps:
        consumer.write_dials(step)
        consumer.commit()
    found = effect_lines(root, {}, no_plugins())
    assert "  W2 (pattern): 8 moment(s): 5 applied, 3 bypassed, 0 missed — B2 3" in found, found
    disabled = json.dumps([{"id": f"{NAMESPACE}@m", "enabled": False, "projectPath": str(root)}])
    again = effect_lines(root, {}, no_plugins(disabled))
    assert "  W2 (pattern): 9 moment(s): 5 applied, 4 bypassed, 0 missed — B2 4" in again, again
    other = H.fresh_consumer()
    for step in [
        own(severity="block"),
        own(markers=["TODO"]),
        own(markers=["TODO"], territories=["*.md", "docs/**"]),
        own(markers=["TODO"], territories=["*.md"]),
    ]:
        other.write_dials(step)
        other.commit()
    told = effect_lines(other.root, {}, no_plugins())
    assert "  W2 (pattern): 4 moment(s): 2 applied, 2 bypassed, 0 missed — B2 2" in told, told


@item(
    23,
    "W3: after a block for a marker the next act on the file decides: write applied, shell bypassed by B3",
)
def test_effect_after_red() -> None:
    """Four sessions, each a block of the hook on a write of a document: the next act a write of the same
    file (applied); a `sed -i` of it (bypassed); a write of another file and no more (bypassed); a human turn
    first (no moment). The line is typed by hand."""
    root = H.fresh_consumer().root
    docs = root / "docs"

    def red(sid: str, *after: str, attached: bool = False) -> list[str]:
        made = tr_red_attached if attached else tr_red
        return [
            tr_call(sid, root, WAY_AT, "r", "Write", docs / "a.md"),
            made(sid, root, "r", "RED: x"),
            *after,
        ]

    sessions = {
        "s23a": red("s23a", tr_call("s23a", root, WAY_AT, "n", "Edit", docs / "a.md")),
        "s23b": red("s23b", tr_tool("s23b", root, "n", "Bash", command="sed -i '' s/TBD/x/ docs/a.md")),
        "s23c": red("s23c", tr_call("s23c", root, WAY_AT, "n", "Write", docs / "other.md"), attached=True),
        "s23d": red(
            "s23d",
            tr_turn("s23d", root, WAY_AT, "stop"),
            tr_call("s23d", root, WAY_AT, "n", "Write", docs / "a.md"),
        ),
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W3 (pattern): 3 moment(s): 1 applied, 2 bypassed, 0 missed — B3 2" in found, found


@item(
    24, "W4: the skill a block names is loaded before the next act on the file, or the block is missed by B5"
)
def test_effect_skill_after_red() -> None:
    """A block whose text says `load the skill const-questions:ask-or-decide`: a Skill call naming it before
    the next write of the file is applied, in full or bare; a write first, or a Skill call for another skill,
    is missed; a block whose text names no skill is no moment. The line is typed by hand."""
    root = H.fresh_consumer().root
    doc = root / "docs" / "a.md"
    said = f"RED: x\nconst-questions: load the skill {SKILL_NAME} before you fix this"

    def case(sid: str, *after: str, text: str = said) -> list[str]:
        return [tr_call(sid, root, WAY_AT, "r", "Write", doc), tr_red(sid, root, "r", text), *after]

    sessions = {
        "s24a": case("s24a", tr_tool("s24a", root, "k", "Skill", skill=SKILL_NAME)),
        "s24b": case("s24b", tr_tool("s24b", root, "k", "Skill", skill="ask-or-decide")),
        "s24c": case("s24c", tr_call("s24c", root, WAY_AT, "w", "Write", doc)),
        "s24d": case("s24d", tr_tool("s24d", root, "k", "Skill", skill="const-questions:other")),
        "s24e": case("s24e", text="RED: x"),
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W4 (pattern): 4 moment(s): 2 applied, 0 bypassed, 2 missed — B5 2" in found, found


@item(
    25,
    "W5: a skill loaded earlier makes a message of lettered options applied, none missed by B5",
)
def test_effect_skill_before_options() -> None:
    """A message of lettered options after a Skill call for ask-or-decide, in full or bare, is applied; one
    with no load before it, and one after a load of another skill, are missed; a load after the message
    does not count for it; a message with no lettered options is no moment. One load counts for every later
    message of its session. The line is typed by hand."""
    root = H.fresh_consumer().root
    chosen = options(option("A"), option("B"))
    sessions = {
        "s25a": [tr_tool("s25a", root, "k", "Skill", skill=SKILL_NAME), tr_say("s25a", root, chosen)],
        "s25b": [tr_tool("s25b", root, "k", "Skill", skill="ask-or-decide"), tr_say("s25b", root, chosen)],
        "s25c": [tr_say("s25c", root, chosen), tr_tool("s25c", root, "k", "Skill", skill=SKILL_NAME)],
        "s25d": [
            tr_tool("s25d", root, "k", "Skill", skill="const-questions:other"),
            tr_say("s25d", root, chosen),
        ],
        "s25e": [tr_say("s25e", root, "I did it, and nothing is left to choose.")],
        "s25f": [
            tr_tool("s25f", root, "k", "Skill", skill=SKILL_NAME),
            tr_say("s25f", root, chosen),
            tr_say("s25f", root, chosen),
        ],
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W5 (pattern): 6 moment(s): 4 applied, 0 bypassed, 2 missed — B5 2" in found, found


@item(
    26,
    "W6: lettered options are applied when they show Pros and Cons, a recommendation, the decider",
)
def test_effect_decision_shape() -> None:
    """The whole shape, twice, is applied. Each of these is missed by B6: options with no sub-bullets, one
    option with no Cons, no recommendation, no decider. A plain question with no letters, and one whose bold
    letters are not a run from A, are no moment. The line is typed by hand."""
    root = H.fresh_consumer().root
    whole = options(option("A"), option("B"))
    texts = [
        whole,
        whole,
        options(option("A", pros=False, cons=False), option("B", pros=False, cons=False)),
        options(option("A"), option("B", cons=False)),
        options(option("A"), option("B"), closing="Decider: you.\n"),
        options(option("A"), option("B"), closing="Recommendation: B.\n"),
        "Should the file go in docs or in notes?",
        "- **C. Third** — alone.\n  - **Pros:** x.\n  - **Cons:** y.\n",
    ]
    lines = [tr_say("s26", root, text) for text in texts]
    found = effect_lines(root, {"s26": lines}, no_plugins())
    assert "  W6 (pattern): 6 moment(s): 2 applied, 0 bypassed, 4 missed — B6 4" in found, found


@item(
    27,
    "W7: the scan on each commit of main in a throwaway clone: green applied, a marker bypassed by B4",
)
def test_effect_escape() -> None:
    """Three commits of `main`: the fixture, a document that holds a `TBD` (the scan is red there), and the
    document without it. The module's own scan runs on a shared clone at each, outside the project, which
    stays as it was. The line is typed by hand."""
    consumer = H.fresh_consumer()
    consumer.git("branch", "-M", "main")
    consumer.write(DOC, note("TBD: who owns this\n"))
    consumer.commit()
    consumer.write(DOC, note("Done.\n"))
    consumer.commit()
    root = consumer.root
    before = subprocess.run(
        ["git", "status", "--porcelain", "--ignored"], cwd=root, capture_output=True, text=True
    )
    found = effect_lines(root, {}, no_plugins())
    assert "  W7 (pattern): 3 moment(s): 2 applied, 1 bypassed, 0 missed — B4 1" in found, found
    after = subprocess.run(
        ["git", "status", "--porcelain", "--ignored"], cwd=root, capture_output=True, text=True
    )
    assert after.stdout == before.stdout, (before.stdout, after.stdout)


@item(28, "W8: each message that puts a question is a moment for the reader, who judges it with --reader")
def test_effect_reader_rule() -> None:
    """Five messages put a question: one that ends in a question mark, one of lettered options with none, one
    whose last line is a question inside bold, one with a question after a code block, and one whose question
    mark stands before a code span. Five do not: three statements, a question mark inside a code span, a
    question mark inside a fenced block. Without `--reader` the five are counted and not judged; a fake
    reader that answers APPLIED judges them, each by W8's own text. The lines are typed by hand."""
    root = H.fresh_consumer().root
    sid = "s28"
    texts = [
        "Shall I put the scratch file under docs/?",
        options(option("A"), option("B"), closing=""),
        "I read this as the first. **Is that right?**",
        "```\nwhat?\n```\nWhich do you want?",
        "Shall I run this? `make check`",
        "The change is made.",
        "The tests pass.",
        "The file is saved.",
        "Run `git status ?` to see it.",
        "```\nIs this a question?\n```\nIt is not.",
    ]
    lines = [tr_turn(sid, root, WAY_AT, "start"), *(tr_say(sid, root, text) for text in texts)]
    plain = effect_lines(root, {sid: lines}, no_plugins())
    assert "  W8 (reader): 5 moment(s), not judged — run again with --reader to judge them" in plain, plain
    folder = H.scratch_dir()
    prompts = folder / "prompts"
    body = (
        'case "$1" in\n'
        '  --version) echo "9.9.9 (Claude Code)" ;;\n'
        '  auth) echo \'{"authMethod": "claude.ai"}\' ;;\n'
        f"  -p) printf '%s\\n<end>\\n' \"$2\" >> {shlex.quote(str(prompts))}\n"
        '      echo \'{"result": "APPLIED"}\' ;;\n'
        "esac\n"
    )
    judged = effect_lines(root, {sid: lines}, fake_claude(folder, body), "--reader")
    assert "  W8 (reader): 5 moment(s): 5 applied, 0 bypassed, 0 missed" in judged, judged
    # the reader judges by W8's own text, typed by hand
    rule = (
        "A question is put to the user only at recorded stakes or at a genuine blocker; below that line the"
        " session makes the reasonable call and notes it in the commit message."
    )
    asked = prompts.read_text(encoding="utf-8").split("\n<end>\n")[:-1]
    assert len(asked) == 5, asked
    for prompt in asked:
        assert prompt.split("The rule:\n", 1)[1].split("\n\nThe moment", 1)[0] == rule, prompt


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=TBD,
    red_finding=q1(TBD, "TBD", "TBD: who owns this"),
    green=messages.g1_covered(),
    territory=["*.md"],
    claim=claim,
    # the skip reason once a negated pattern takes `red` out of the territory, typed by hand
    outside="docs/notes/a.md is not covered (const-questions.territories)",
    resolves_policies=False,
    bare_readme="1 document examined",
    judges_envelopes=False,
    long_value=wrote("[decide:" + "x" * 11992 + "\n"),
    pattern_dial=PatternDial("territories", lambda pattern: own(territories=[pattern])),
    skill="ask-or-decide",  # the skill a red names (F10), typed by hand
    effect="effect-report.sh",  # no `effect_reader`: its reader rule W8 has a moment for each question put,
    # and the shared items about a reader rule need one for each human turn
)
