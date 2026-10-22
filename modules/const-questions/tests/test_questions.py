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
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
import yaml
from acceptance import broken_first_line, check_case, expect, item
from constitution_layer_kit import identity
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import Broken, Finding
from consumer import Consumer, document
from harness import (
    Case,
    Edit,
    Harness,
    Result,
    Write,
    event_json,
    red_lines,
)
from questions_gate import messages, start
from test_shared_items import PatternDial, Subject

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
identity.declare_dials_file("constitution.yaml")  # the expected messages name the file the gate reads
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
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
)
