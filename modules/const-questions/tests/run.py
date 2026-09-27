#!/usr/bin/env python3
"""Fixtures of const-questions: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one. Its three policies matter here only as Markdown files
the default territory covers: this gate resolves no policy and judges no envelope, so the
shared items about the root policy and about an unreadable envelope are not its own and are
left out; their numbers stay free.
"""

from __future__ import annotations

import json
import re
import subprocess
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
    red_lines,
)
from questions_gate import messages, start  # noqa: E402
from shared_items import Subject, shared_assertions  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
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
    """The 1-based line that carries `needle` — so a case never hardcodes the envelope's height."""
    for number, line in enumerate(text.splitlines(), start=1):
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


def broken(result: Result, failure: Broken) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, failure.render())
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def passes(action: Write | Edit, **kwargs: object) -> tuple[bool, str]:
    result, _ = gate_on(action, **kwargs)  # type: ignore[arg-type]
    return expect(result, 0, shared.g1_green_hook(messages.g1_covered()), "stdout")


def blocked(action: Write | Edit, finding: Finding, **kwargs: object) -> tuple[bool, str]:
    result, _ = gate_on(action, **kwargs)  # type: ignore[arg-type]
    wanted = [f"RED: {finding.headline}", f"RED: 1 finding(s) — 1 document examined ({action.target})"]
    ok = result.code == 2 and finding.render() in result.stderr and red_lines(result.stderr) == wanted
    return ok, f"exit 2: {finding.headline}" if ok else f"exit {result.code}: {result.stderr[:500]}"


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


def quotations_pass() -> tuple[bool, str]:
    """A marker inside a code span or a fenced block is a quotation; a marker that is part of a
    word is none; the match is case-sensitive."""
    body = (
        "A `TODO` in a span, and ``a TBD in a double span``.\n"
        "```\nTODO inside a fence\n[decide: fenced]\n```\n"
        "~~~text\nFIXME in a tilde fence\n~~~\n"
        "TODOs, TODO_LIST, todo, fixme, tbd and Tbd are none.\n"
        "   ```\n   TODO in an indented fence\n   ```\n"
    )
    return passes(wrote(body))


def boundaries_hold() -> tuple[bool, str]:
    """Punctuation beside a marker keeps it a marker; a letter or a digit glued to it does not."""
    for text, marker in (
        ("(TODO)", "TODO"),
        ("#TBD.", "TBD"),
        ("x FIXME", "FIXME"),
        ("a [decide:]", "[decide:"),
    ):
        ok, evidence = blocked(
            wrote(text + "\n"), q1(wrote(text + "\n"), marker, text, text[text.index(marker) :])
        )
        if not ok:
            return False, f"{text!r}: {evidence}"
    for text in ("TODO1", "1TODO", "xTBDx", "FIXMEs"):
        ok, evidence = passes(wrote(text + "\n"))
        if not ok:
            return False, f"{text!r} must pass: {evidence}"
    return True, "four marked lines blocked, four glued words passed"


def open_fence_masks_to_the_end() -> tuple[bool, str]:
    """An unclosed fence hides everything after it (a limit the module document states); a closer
    of the other character, or a shorter one, does not close it; a backtick opener whose info
    string holds a backtick is no opener; a closer with any text after it closes."""
    ok, evidence = passes(wrote("```\nTODO\n~~~\nTBD\n``\nFIXME\n"))
    if not ok:
        return False, evidence
    action = wrote("````\nTODO\n```\nTBD\n````\nFIXME here\n")
    ok, evidence = blocked(action, q1(action, "FIXME", "FIXME here"))
    if not ok:
        return False, evidence
    spans = wrote("```foo`bar\nTODO after a span line, not a fence\n")  # a backtick in the info string
    ok, evidence = blocked(spans, q1(spans, "TODO", "TODO after a span line, not a fence"))
    if not ok:
        return False, evidence
    closer = wrote("```\nTODO\n``` x`y\nTBD here\n")  # a closer with any text after it closes
    return blocked(closer, q1(closer, "TBD", "TBD here"))


def one_hit_per_line_in_order() -> tuple[bool, str]:
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
    ok = result.code == 2 and red_lines(result.stderr) == wanted
    return ok, "two findings in line order, counted two" if ok else result.stderr[:600]


def own_markers() -> tuple[bool, str]:
    """The markers dial replaces the defaults: a project's own text is found, a default no more;
    a marker made of punctuation needs no boundary."""
    patch = own(markers=["OPEN QUESTION", "??"])
    action = wrote("TODO is fine now; OPEN QUESTION: who?\n")
    ok, evidence = blocked(
        action, q1(action, "OPEN QUESTION", "OPEN QUESTION", "OPEN QUESTION: who?"), dials_patch=patch
    )
    if not ok:
        return False, evidence
    glued = wrote("Really??\n")
    ok, evidence = blocked(glued, q1(glued, "??", "Really", "??"), dials_patch=patch)
    if not ok:
        return False, evidence
    return passes(wrote("TODO and TBD pass under the project's own markers.\n"), dials_patch=patch)


def territories_decide_coverage() -> tuple[bool, str]:
    """A document outside the territories is a visible skip naming the dial; a README at the top
    is covered by the default and examined."""
    result, _ = gate_on(TBD, dials_patch=claim(["docs/other/**"]))
    skip = shared.g1_green_skip(messages.g1_skip_not_covered(DOC))
    ok, evidence = expect(result, 0, skip, "stdout")
    if not ok:
        return False, evidence
    readme = Write("README.md", "# Top\n\nTBD\n")
    return blocked(readme, messages.q1_marker("README.md", 3, "TBD", "TBD"))


def dial_failures() -> tuple[bool, str]:
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
        ok, evidence = broken_first_line(result, line)
        if not ok or shared.c11_broken_count() not in result.stderr:
            return False, f"{patch}: {evidence}"
    ok, evidence = passes(
        VALID, dials_patch=own(preferences=[{"decider": "x"}], boundary_examples=[{"ask": "a"}])
    )
    return ok, "seven refusals exit 1 with their lines; the skill's two dials pass unread" if ok else evidence


def scan_reports_in_order() -> tuple[bool, str]:
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
    wanted = [
        f"RED: {messages.q1_marker(DOC, line_of(a, 'TBD one'), 'TBD', 'TBD one').headline}",
        f"RED: {messages.q1_marker(DOC, line_of(a, 'TBD two'), 'TBD', 'TBD two').headline}",
        f"RED: {messages.q1_marker('docs/notes/c.md', line_of(a, 'TBD one'), 'FIXME', 'FIXME').headline}",
        "RED: 3 finding(s) — 6 document(s) examined for 4 marker(s), 7 Markdown file(s) scanned",
    ]
    if result.code != 2 or red_lines(result.stdout) != wanted:
        return False, f"exit {result.code}: {result.stdout[:800]}"
    green = scan_of({DOC: note("Fine.\n")})
    line = "GREEN: const-questions: 4 document(s) examined for 4 marker(s), 4 Markdown file(s) scanned"
    return expect(green, 0, line, "stdout")


def golden_lines() -> tuple[bool, str]:
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
    if "\n".join(lines) not in result.stderr:
        return False, f"expected:\n{chr(10).join(lines)}\ngot:\n{result.stderr[:900]}"
    long = wrote("TODO " + "y" * 200 + "\n")
    result, _ = gate_on(long)
    head = (
        f"RED: {DOC}:{line_of(long.text, 'TODO')}: open question marker 'TODO' — TODO "
        + "y" * 75
        + "… [205 characters]"
    )
    ok = head in result.stderr and "y" * 76 not in result.stderr
    return ok, "three lines and the cut as typed" if ok else result.stderr[:400]


SHAPE = (
    "const-questions (advisory): a choice put to the user takes one shape, in the chat message, one decision"
    " per message. Options lettered A, B, C…, each a bullet: the bold letter and title with a one-sentence"
    " description on the first line; beneath it two indented sub-bullets, **Pros:** and **Cons:**, one prose"
    " line each — never inline in the description, never a table. Then exactly one recommendation with its"
    " reasoning, and the decider named. A one-fact clarification is a plain line and takes none of this."
    " Whether to ask at all, the tool or the letter, and the project's preferences are the skill"
    " ask-or-decide: load it before putting any choice.\n"
)


def hooks_file() -> tuple[bool, str]:
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
    return (
        not problems,
        "a PreToolUse handler on Write|Edit and a SessionStart handler without matcher, exec form, timeouts,"
        " scripts present"
        if not problems
        else str(problems),
    )


def decision_shape_printed() -> tuple[bool, str]:
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
    if done.returncode != 0 or done.stdout != SHAPE or done.stderr != "":
        return False, repr(done)
    size = len(SHAPE) - 1
    stated = re.search(
        r"printed by the `SessionStart` hook, (\d+) characters",
        (SCRIPTS.parent / "MODULE.md").read_text(encoding="utf-8"),
    )
    if not stated or int(stated.group(1)) != size:
        return False, f"the module document states another size than {size}"
    install = " ".join((SCRIPTS.parent / "INSTALL.md").read_text(encoding="utf-8").split())
    if f"{size} characters, advisory" not in install:
        return False, f"the install note states another size than {size}"
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
    if missing:
        return False, f"phrases not in both carriers: {missing}"
    return (
        True,
        f"exit 0, the text as typed, {size} characters as both documents state, eight phrases in the skill",
    )


def skill_and_install_note() -> tuple[bool, str]:
    root = SCRIPTS.parent
    text = (root / "skills" / "ask-or-decide" / "SKILL.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---")[1])
    if front["name"] != "ask-or-decide" or not (0 < len(front["description"]) <= 1536):
        return False, "name or description size"
    if "Use when " not in front["description"] or "Advisory:" not in front["description"]:
        return False, "the description carries no 'Use when ' trigger or no 'Advisory:' line"
    if "Load this skill first" not in front["description"]:
        return False, "the description does not ask to be loaded first"
    size = len(front["description"])
    stated = re.search(r"skill listing, (\d+) characters", (root / "MODULE.md").read_text(encoding="utf-8"))
    if not stated or int(stated.group(1)) != size:
        return False, f"the module document states another size than {size}"
    install = (root / "INSTALL.md").read_text(encoding="utf-8")
    if "MODULE.md" in install:
        return False, "the install note names the module document, which a consumer does not hold"
    block = install.split("```yaml", 1)[1].split("```", 1)[0]
    example = yaml.safe_load(block)
    result = scan_of({DOC: note("Fine.\n"), "drafts/x.md": "TODO\n"}, dials_patch=example)
    ok, evidence = expect(
        result, 0, "GREEN: const-questions: 4 document(s) examined for 4 marker(s), 5 Markdown", "stdout"
    )
    return (
        ok,
        f"description {size} characters, as the module document states; the install note's example accepted"
        if ok
        else evidence,
    )


def other_event_refused() -> tuple[bool, str]:
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
    return broken_first_line(result, line)


def deep_envelope_is_no_crash() -> tuple[bool, str]:
    """An envelope nested past the parser's depth is judged for markers like any text and is no
    crash: this gate reads no envelope, so the shared item about one is not its own."""
    ok, evidence = passes(Write(DOC, "---\nid: " + "[" * 5000 + "]" * 5000 + "\n---\n\nFine.\n"))
    if not ok:
        return False, evidence
    deep = Write(DOC, "---\nid: " + "[" * 5000 + "\n---\n\nTBD here\n")
    return blocked(deep, q1(deep, "TBD", "TBD here"))


def edit_removing_a_marker_passes() -> tuple[bool, str]:
    """The document judged is the one after the write: an Edit that takes the marker out passes,
    and one that leaves another marker in place is blocked on that one."""
    two = note("TBD one\n\nTBD two\n")
    ok, evidence = passes(Edit(DOC, "TBD", "Done", replace_all=True), files={DOC: two})
    if not ok:
        return False, evidence
    action = Edit(DOC, "TBD one", "Done one")
    return blocked(
        action, messages.q1_marker(DOC, line_of(two, "TBD two"), "TBD", "TBD two"), files={DOC: two}
    )


ASSERTIONS = [
    Assertion(6, "quotations in code, glued words and other cases pass", quotations_pass),
    Assertion(
        7, "word boundaries: punctuation keeps a marker, a glued letter or digit unmakes it", boundaries_hold
    ),
    Assertion(8, "an open fence masks to the end; a closer must match", open_fence_masks_to_the_end),
    Assertion(9, "one finding per line, in line order, counted", one_hit_per_line_in_order),
    Assertion(10, "the markers dial replaces the defaults", own_markers),
    Assertion(11, "territories decide coverage; a top-level README is covered", territories_decide_coverage),
    Assertion(12, "this module's dial failures, exit 1, lines typed by hand", dial_failures),
    Assertion(13, "the scan: order, count tail, warn ignored, green tail", scan_reports_in_order),
    Assertion(14, "golden lines of Q1 and the cut of a long line", golden_lines),
    Assertion(15, "the hooks file's shape", hooks_file),
    Assertion(
        16, "the skill description's size and lines; the install note's example", skill_and_install_note
    ),
    Assertion(17, "an event the gate is not wired to is C12", other_event_refused),
    Assertion(18, "an Edit is judged on the result", edit_removing_a_marker_passes),
    Assertion(
        19, "an envelope nested past the parser's depth is no crash, and is judged", deep_envelope_is_no_crash
    ),
    Assertion(
        20,
        "the session-start text as typed, its size stated, its phrases in the skill",
        decision_shape_printed,
    ),
]

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
)

if __name__ == "__main__":
    sys.exit(H.run_all(CASES, [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
