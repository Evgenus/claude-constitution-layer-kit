#!/usr/bin/env python3
"""Fixtures of const-language: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, the libraries in the plugin's requirements file, and vale 3.23.0 or
newer on PATH — the runner installs nothing: without the binary the absence items pass and the
rest fail with the install command. Every item has a stable number: this module's own items
from 1, the items every gate shares from 101. Exit 0 when every item is green, 2 otherwise.

One entry point is driven through the shared items and its own, with real hook events — the
platform's PreToolUse payload, which the harness sends and the gate judges on the content it
carries, and PostToolUse payloads, which the plugin wires and the gate judges on the file on
disk — and with `--scan`. The fixture consumer is the shared one; this module resolves no
policy and judges no envelope, so the shared items about the root policy and about an
unreadable envelope are left out.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from const_gate import identity
from const_gate import messages as shared
from const_gate.model import Finding
from const_gate.repository import list_markdown
from consumer import Consumer
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
    stop_json,
)
from language_gate import dials as own_dials
from language_gate import messages, rules, start, vale
from language_gate.model import Departure, Rule
from shared_items import PatternDial, Subject, git_patch, shared_assertions

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MODULE_ROOT = SCRIPTS.parent

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
H = Harness(SCRIPTS, "check-language.sh", "check-language.py", start.GATE.namespace)
NAMESPACE = start.GATE.namespace
SKILL = MODULE_ROOT / "skills" / "plain-language" / "SKILL.md"
INSTALL = MODULE_ROOT / "INSTALL.md"
MANIFEST = MODULE_ROOT / ".claude-plugin" / "plugin.json"
HOOKS = MODULE_ROOT / "hooks" / "hooks.json"
DOC = "docs/notes/c.md"
# the line after the count line of every red (F10 of the shared gate code), typed by hand once
F10 = "const-language: load the skill const-language:plain-language before you fix this — it teaches the rule and the fix"  # noqa: E501 — a golden line is typed whole
# the line printed at session start and at each subagent's start, typed by hand once
POINTER = "const-language (advisory): before writing or editing prose in a document the language check covers, and when the check reports a finding, load the skill const-language:plain-language."  # noqa: E501 — a golden line is typed whole

# Documents the items share. Vale 3.23.0 counts these as the numbers below (E1 of the comparison);
# a later Vale that counts syllables differently changes the grade and this fixture says so.
GRADE_RED = (
    "# T\n\nOrganizational responsibilities necessitate comprehensive documentation. Institutional"
    " accountability presupposes systematic verification. Methodological considerations determine"
    " implementation.\n"
)
GRADE_RED_VALUE = 43.54
PLAIN = "# T\n\nThe cat sat on the mat. It was warm. We went home.\n"
LONG_SENTENCE = (
    "The cat sat on the mat and the dog ran to the door and the bird flew up to the roof and the fish"
    " swam in the pond and the sun set."
)
SENTENCE_RED = f"# T\n\n{LONG_SENTENCE}\n"
SENTENCE_GREEN = "# T\n\n" + " ".join(["cat"] * 24) + " sat.\n"  # exactly 25 words: at the limit, not over
IDIOM_RED = "# T\n\nWe will hit the ground running.\n"
IDIOM_GREEN = "# T\n\nWe will start at once.\n"
SIMPLER_RED = "# T\n\nDo it prior to noon.\n"
SIMPLER_GREEN = "# T\n\nDo it before noon.\n"
PASSIVE = "# T\n\nThe report was written yesterday.\n"
COMMENT_RED = "# T\n\n<!-- vale Language.Simpler = NO -->\nDo it prior to noon.\n"
COMMENT_GREEN = "# T\n\nDo it before noon.\n"


# a file name of over 80 characters holding a line break and a backslash: the real name, and the text the
# gate shows for it, typed by hand — the whole name, since a path is what the reader opens
WEIRD = "docs/notes/w\nx\\y" + "z" * 80 + ".md"
WEIRD_SHOWN = "docs/notes/w\\nx\\\\y" + "z" * 80 + ".md"
WEIRD_OTHER = "docs/other/w\nx\\y" + "z" * 80 + ".md"
WEIRD_OTHER_SHOWN = "docs/other/w\\nx\\\\y" + "z" * 80 + ".md"


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps it working."""
    return {NAMESPACE: dict(dials)}


def claim(territory: Sequence[str]) -> dict[str, object]:
    return own(territories=list(territory))


def dials_text(patch: dict[str, object] | None = None) -> str:
    return yaml.safe_dump({**Consumer(Path()).dials, **(patch or {})}, sort_keys=False)


def prepared(
    dials_patch: dict[str, object] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> Path:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", raw_dials if raw_dials is not None else dials_text(dials_patch))
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return consumer.root


def gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    """The gate on a prepared consumer, driven by the platform's pre-write event for the action."""
    root = prepared(dials_patch, raw_dials, files, remove)
    return H.run_gate(event_json(root, action), env=env), root


def after_write(root: Path, target: str) -> Result:
    """The event the plugin wires: PostToolUse, the document being the file on disk."""
    return H.run_gate(event_json(root, Write(target, "unused"), event="PostToolUse"))


def scan(files: dict[str, str], dials_patch: dict[str, object] | None = None) -> Result:
    root = prepared(dials_patch, files=files)
    return H.run_gate("", args=["--scan", str(root)])


def tail(
    documents: int, scanned: int | None = None, ceiling: float = 10.0, words: int = 25, departures: int = 0
) -> str:
    return messages.f9_tail(documents, ceiling, words, departures, documents if scanned is None else scanned)


def green_scan(
    documents: int, scanned: int | None = None, ceiling: float = 10.0, words: int = 25, departures: int = 0
) -> str:
    return f"GREEN: {NAMESPACE}: {tail(documents, scanned, ceiling, words, departures)}"


def green_hook() -> str:
    # typed by hand: the covered line is not built by the message function
    return f"GREEN: {NAMESPACE}: 1 document examined, covered by {NAMESPACE}.territories"


def context(result: Result) -> Result:
    """A green hook run with notes answers with one JSON object: what it hands the model, as stdout;
    any other run as it is. The object's shape is the shared item's to prove."""
    try:
        answer = json.loads(result.stdout)
    except json.JSONDecodeError:
        return result
    said = answer.get("hookSpecificOutput", {}).get("additionalContext") if isinstance(answer, dict) else None
    return Result(result.code, said, result.stderr) if isinstance(said, str) else result


def all_of(*checks: tuple[bool, str]) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in checks if not ok]
    return not failed, "; ".join(failed) if failed else "; ".join(evidence for _, evidence in checks)


def headlines(result: Result, where: str = "stderr") -> list[str]:
    """The RED lines but the count line: the findings' headlines."""
    return red_lines(result.stderr if where == "stderr" else result.stdout)[:-1]


def one_finding(
    text: str, headline: str, dials_patch: dict[str, object] | None = None, target: str = DOC
) -> tuple[bool, str]:
    result, _ = gate_on(Write(target, text), dials_patch)
    lines = headlines(result)
    ok = result.code == 2 and lines == [f"RED: {headline}"]
    return ok, headline if ok else f"exit {result.code}: {result.stderr.strip()}{result.stdout.strip()}"


def no_finding(text: str, dials_patch: dict[str, object] | None = None) -> tuple[bool, str]:
    result, _ = gate_on(Write(DOC, text), dials_patch)
    return expect(result, 0, green_hook(), "stdout")


def allow_typed(key: str) -> str:
    """The closing clause of every fix but L6, typed by hand once, the rule key filled in."""
    return (
        "; for a document that must stand as written, declare the departure with its reason: add to"
        " const-language.departures in constitution.yaml an entry {paths: [<the file, or a pattern of the"
        f" documents that stand>], allow: [{key}], reason: <why they stand, in one line>}}"
    )


ALLOW_GRADE = allow_typed("grade")
ALLOW_SENTENCE = allow_typed("sentence")
ALLOW_FORBIDDEN = allow_typed("forbidden")
ALLOW_SIMPLER = allow_typed("simpler")


def sentence_headline(words: int, text: str, limit: int = 25) -> str:
    return messages.l2_sentence(DOC, 3, words, limit, text).headline


# ---------------------------------------------------------------- this module's own items


def t1() -> tuple[bool, str]:
    """L1 typed whole for a document of long words; a plain document is green; the ceiling is
    exclusive and a dial; a headline of a grade-only document at line 1."""
    found = messages.l1_grade(DOC, GRADE_RED_VALUE, 10.0)
    result, _ = gate_on(Write(DOC, GRADE_RED))
    typed = (
        f"RED: {DOC}:1: the document reads at grade 43.54 by Flesch–Kincaid, above the ceiling of 10\n"
        "  why: a reader whose first language is not English pays for every year of schooling the prose"
        " assumes, and the grade rises with words per sentence and syllables per word\n"
        "  fix: split the long sentences and prefer short words in the prose outside headings, code and"
        " tables until the grade is at or under 10; the ceiling for this repository is"
        " const-language.grade_ceiling in constitution.yaml" + allow_typed("grade")
    )
    return all_of(
        (found.render() == typed, "L1 typed whole equals the function's text"),
        one_finding(GRADE_RED, found.headline),
        no_finding(PLAIN),
        no_finding(GRADE_RED, own(grade_ceiling=43.6)),  # over the grade: not a finding
        one_finding(
            GRADE_RED, messages.l1_grade(DOC, GRADE_RED_VALUE, 43.5).headline, own(grade_ceiling=43.5)
        ),
        expect(result, 2, f"RED: 1 finding(s) — 1 document examined ({DOC})", "stderr"),
    )


def t2() -> tuple[bool, str]:
    """L2 typed whole for a sentence of 32 words, its start echoed; 25 words exactly pass; the
    limit is a dial; a heading is a sentence to the rule."""
    found = messages.l2_sentence(DOC, 3, 32, 25, LONG_SENTENCE)
    typed = (
        f"RED: {DOC}:3: a sentence of 32 words, over the limit of 25 — The cat sat on the mat and the"
        " dog ran to the door and the bird flew up to the r… [130 characters]\n"
        "  why: a sentence longer than the limit carries more than one idea, and a non-native reader"
        " loses the first before reaching the last\n"
        "  fix: split it at a clause into sentences of at most 25 words; the limit for this repository"
        " is const-language.sentence_words in constitution.yaml" + allow_typed("sentence")
    )
    heading = "# " + " ".join(["word"] * 26) + "\n\nShort.\n"
    return all_of(
        (found.render() == typed, "L2 typed whole equals the function's text"),
        one_finding(SENTENCE_RED, found.headline),
        no_finding(SENTENCE_GREEN),
        no_finding(SENTENCE_RED, own(sentence_words=32)),
        one_finding(SENTENCE_RED, sentence_headline(32, LONG_SENTENCE, 31), own(sentence_words=31)),
        one_finding(heading, messages.l2_sentence(DOC, 1, 26, 25, heading.split("\n")[0][2:]).headline),
    )


def t3() -> tuple[bool, str]:
    """L3 typed whole for an idiom, case-insensitive; the same phrase in a code span or a fence is
    code; an exception takes it out; a phrase of the repository's own is added."""
    found = messages.l3_forbidden(DOC, 3, "hit the ground running")
    typed = (
        f"RED: {DOC}:3: 'hit the ground running' is a construction plain language avoids\n"
        "  why: an idiom or a formal phrase says nothing a plain sentence does not, and a non-native"
        " reader must translate it before reading on\n"
        "  fix: say it in plain words, or drop it; a phrase this repository keeps on purpose is named"
        " in const-language.exceptions in constitution.yaml" + allow_typed("forbidden")
    )
    return all_of(
        (found.render() == typed, "L3 typed whole equals the function's text"),
        one_finding(IDIOM_RED, found.headline),
        one_finding(
            "# T\n\nWe will Hit The Ground Running.\n",
            messages.l3_forbidden(DOC, 3, "Hit The Ground Running").headline,
        ),
        no_finding(IDIOM_GREEN),
        no_finding("# T\n\nThe phrase `hit the ground running` is quoted here.\n"),
        no_finding("# T\n\n```text\nhit the ground running\n```\n"),
        no_finding(IDIOM_RED, own(exceptions=["hit the ground running"])),
        no_finding(
            IDIOM_RED, own(exceptions=["Hit The Ground Running"])
        ),  # an exception, like the lists, in any case
        one_finding(
            "# T\n\nWe ship a synergy.\n",
            messages.l3_forbidden(DOC, 3, "synergy").headline,
            own(forbidden=["synergy"]),
        ),
    )


def t4() -> tuple[bool, str]:
    """L4 typed whole with the plain word, in any case; an exception keeps the phrase; a pair of the
    repository's own; the pair's plain word arrives from the rule, not from the document."""
    found = messages.l4_simpler(DOC, 3, "prior to", "before")
    odd, _ = (
        gate_on(  # the plain word holds a backslash and 103 characters: the headline points, the fix is typed
            Write(DOC, "# T\n\nWe will ascertain it.\n"), own(simpler={"ascertain": "a\\b" + "x" * 100})
        )
    )
    long_plain = (
        odd.stderr.splitlines()[0:3:2]
        == [
            "RED: docs/notes/c.md:3: 'ascertain' where the plain word is 'a\\\\b"
            + "x" * 77
            + "… [103 characters]'",
            "  fix: write 'a\\\\b" + "x" * 100 + "'; a word this repository keeps on purpose is named in"
            " const-language.exceptions in constitution.yaml" + ALLOW_SIMPLER,
        ],
        "the plain word cut in the headline and whole in the fix, its backslash doubled: " + odd.stderr[:600],
    )
    weird, _ = gate_on(Write(WEIRD, SIMPLER_RED))
    long_path = (  # the path whole in the headline and in the count line, though over 80 characters
        weird.stderr.splitlines()[0]
        == "RED: " + WEIRD_SHOWN + ":3: 'prior to' where the plain word is 'before'"
        and weird.stderr.splitlines()[-2:]
        == ["RED: 1 finding(s) — 1 document examined (" + WEIRD_SHOWN + ")", F10],
        "the path whole and escaped: " + weird.stderr[:400],
    )
    typed = (
        f"RED: {DOC}:3: 'prior to' where the plain word is 'before'\n"
        "  why: a long or formal word costs a non-native reader a dictionary where the plain one does"
        " not\n"
        "  fix: write 'before'; a word this repository keeps on purpose is named in"
        " const-language.exceptions in constitution.yaml" + allow_typed("simpler")
    )
    return all_of(
        (found.render() == typed, "L4 typed whole equals the function's text"),
        one_finding(SIMPLER_RED, found.headline),
        no_finding(SIMPLER_GREEN),
        one_finding(
            "# T\n\nDo it Prior To noon.\n", messages.l4_simpler(DOC, 3, "Prior To", "before").headline
        ),
        no_finding(SIMPLER_RED, own(exceptions=["prior to"])),
        one_finding(
            "# T\n\nWe will ascertain it.\n",
            messages.l4_simpler(DOC, 3, "ascertain", "x" * 12000).headline,
            own(simpler={"ascertain": "x" * 12000}),
        ),
        (
            messages.l4_simpler(DOC, 3, "ascertain", "x" * 12000).headline.endswith(
                "'ascertain' where the plain word is '" + "x" * 80 + "… [12000 characters]'"
            )
            and "x" * 12000 + "'; a word this repository"
            in messages.l4_simpler(DOC, 3, "ascertain", "x" * 12000).render(),
            "a plain word of 12,000 characters is cut in the headline, which only points, and whole in the"
            " fix, which the reader types",
        ),
        one_finding(
            "# T\n\nWe will ascertain it.\n",
            messages.l4_simpler(DOC, 3, "ascertain", "find out").headline,
            own(simpler={"ascertain": "find out"}),
        ),
        long_plain,
        long_path,
    )


def t5() -> tuple[bool, str]:
    """L5: a note by default, green; red under levels.passive error, typed whole; nothing under off,
    bare or quoted; a rule at warning keeps its note on a red run too; a form of be inside a word
    is no passive."""
    found = messages.l5_passive(DOC, 3, "was written")
    typed = (
        f"RED: {DOC}:3: passive voice — 'was written'\n"
        "  why: the passive hides who acts, and a non-native reader must supply the actor to follow the"
        " sentence\n"
        "  fix: name who acts and put them first; a passive kept on purpose is a register the repository"
        " sets by const-language.levels.passive in constitution.yaml" + allow_typed("passive")
    )
    note = messages.n2_warning(DOC, Rule.PASSIVE, found)
    result, _ = gate_on(Write(DOC, PASSIVE))
    off, _ = gate_on(Write(DOC, PASSIVE), own(levels={"passive": "off"}))
    bare, _ = gate_on(
        Write(DOC, PASSIVE), raw_dials=dials_text() + "const-language:\n  levels:\n    passive: off\n"
    )
    both, _ = gate_on(Write(DOC, PASSIVE + "\nDo it prior to noon.\n"))
    inside, _ = gate_on(Write(DOC, "# T\n\nThis used car is fine.\n"))  # "is" inside "This": no passive
    return all_of(
        (found.render() == typed, "L5 typed whole equals the function's text"),
        # a form of be and its participle on two lines: Vale's match holds the line break, shown escaped
        one_finding(
            "# T\n\nThe report was\nwritten yesterday.\n",
            f"{DOC}:3: passive voice — 'was\\nwritten'",
            own(levels={"passive": "error"}),
        ),
        expect(context(result), 0, note, "stdout"),
        expect(context(result), 0, green_hook(), "stdout"),
        (
            note == f"note: {DOC}:3: passive voice — 'was written' — reported, not red, while"
            " const-language.levels.passive is warning",
            "the note typed whole",
        ),
        one_finding(PASSIVE, found.headline, own(levels={"passive": "error"})),
        (off.code == 0 and "note:" not in off.stdout, f"off: exit {off.code}, no note"),
        (
            bare.code == 0 and "note:" not in bare.stdout,
            f"a bare off, false to YAML: exit {bare.code}, no note",
        ),
        expect(both, 2, note, "stderr"),  # the note travels with the block verdict
        (
            inside.code == 0 and "note:" not in inside.stdout,
            f"a form of be inside a word: exit {inside.code}, no note",
        ),
    )


def t6() -> tuple[bool, str]:
    """L6 typed whole: a Vale comment is a finding, and the rule it would switch off still fires."""
    comment = "<!-- vale Language.Simpler = NO -->"
    found = messages.l6_vale_comment(DOC, 3, comment)
    typed = (
        f"RED: {DOC}:3: a Vale comment in the document — {comment}\n"
        "  why: a comment that switches a rule off is a mark in the document, which the gate blanks"
        " before it reads; what departs from a rule is declared in the dials file, where every reader"
        " sees it\n"
        "  fix: remove the comment; to change a rule for this repository set its level or threshold"
        " under const-language in constitution.yaml, or, for a document that must stand as written,"
        " declare the departure with its reason in const-language.departures there"
    )
    result, _ = gate_on(Write(DOC, COMMENT_RED))
    wanted = [f"RED: {found.headline}", f"RED: {messages.l4_simpler(DOC, 4, 'prior to', 'before').headline}"]
    multi = "# T\n\n<!-- vale off\n-->\nDo it prior to noon.\n"
    mentioned = "# T\n\n```text\n<!-- vale Language.Simpler = NO -->\n```\n\nDo it prior to noon.\n"
    in_span = "# T\n\nA `<!-- vale Language.Simpler = NO -->` span; do it prior to noon.\n"
    across, _ = gate_on(Write(DOC, multi))
    # a lone carriage return reaches the message only by a PreToolUse payload, whose content is not read
    # through universal newlines; the comment stays on line 3 and its headline shows the return escaped
    carriage, _ = gate_on(Write(DOC, "# T\n\n<!-- vale\roff -->\nShort.\n"))
    return all_of(
        (found.render() == typed, "L6 typed whole equals the function's text"),
        (
            headlines(carriage) == [f"RED: {DOC}:3: a Vale comment in the document — <!-- vale\\roff -->"],
            f"a lone carriage return in a Vale comment is shown escaped: {headlines(carriage)}",
        ),
        (headlines(result) == wanted, f"both findings, in line order: {headlines(result)}"),
        (
            headlines(across)
            == [
                f"RED: {messages.l6_vale_comment(DOC, 3, '<!-- vale off -->').headline}",
                f"RED: {messages.l4_simpler(DOC, 5, 'prior to', 'before').headline}",
            ],
            f"a comment across lines is blanked with its line numbers kept: {headlines(across)}",
        ),
        no_finding(COMMENT_GREEN),
        one_finding(mentioned, messages.l4_simpler(DOC, 7, "prior to", "before").headline),
        one_finding(in_span, messages.l4_simpler(DOC, 3, "prior to", "before").headline),
    )


def t7() -> tuple[bool, str]:
    """The envelope is blanked: a title holding a phrase is not prose, and a byte-order mark before
    it changes nothing; a document of no prose is green; an unterminated envelope is prose. The
    envelope is the block the shared reader finds: a closer `--- ` with trailing whitespace closes
    it and a thematic break below does not stand in for it; a whole file in CRLF is blanked; a
    form feed before `---` makes no closer, since a line ends at a line break and nowhere else; an
    envelope ended by lone carriage returns is deleted, not turned to spaces, so the prose after
    it on the same line is read, never taken for an indented code block."""
    with_title = "---\nid: c\ntitle: Do it prior to noon\nstatus: active\n---\n\n# T\n\nShort.\n"
    unterminated = "---\nid: c\n\nDo it prior to noon.\n"
    # the closer's trailing space, a thematic break further down: the first section is prose
    spaced_closer = "---\nid: c\ntitle: Plain\n--- \n\n# T\n\nDo it prior to noon.\n\n---\n\nMore.\n"
    # a form feed starts the only closer line: no line is `---`, nothing is blanked, the prose is read
    form_feed = "---\nid: c\n\x0c---\n\n# T\n\nDo it prior to noon.\n"
    # lone carriage returns end the envelope's lines: the prose shares line 1 with it
    lone_cr = "---\rid: c\rtitle: Plain\r---\rDo it prior to noon.\n\n# T\n\nShort.\n"
    return all_of(
        no_finding(with_title),
        no_finding("﻿" + with_title),
        no_finding(""),
        one_finding(unterminated, messages.l4_simpler(DOC, 4, "prior to", "before").headline),
        no_finding(
            "---\nid: " + "[" * 600 + "\n---\n\nShort.\n"
        ),  # nested past the parser's depth: blanked, no crash
        no_finding(with_title.replace("status: active\n---\n", "status: active\n--- \n")),
        no_finding(with_title.replace("\n", "\r\n")),
        one_finding(spaced_closer, messages.l4_simpler(DOC, 8, "prior to", "before").headline),
        one_finding(form_feed, messages.l4_simpler(DOC, 7, "prior to", "before").headline),
        one_finding(lone_cr, messages.l4_simpler(DOC, 1, "prior to", "before").headline),
    )


def t8() -> tuple[bool, str]:
    """The event the plugin wires: after the write the file on disk is judged, a missing file is the
    shared skip, a covered file is green; before the write the content is judged; a Stop event is
    this module's C12, typed by hand."""
    root = prepared(files={DOC: SIMPLER_RED, "docs/notes/ok.md": PLAIN})
    red = after_write(root, DOC)
    green = after_write(root, "docs/notes/ok.md")
    gone = after_write(root, "docs/notes/gone.md")
    stop = H.run_gate(stop_json(root))
    other = json.loads(event_json(root, Write(DOC, "x")))
    other["hook_event_name"] = "UserPromptSubmit"
    elsewhere = H.run_gate(json.dumps(other))
    other["hook_event_name"] = "N\nx\\y" + "e" * 90
    odd_event = H.run_gate(json.dumps(other))
    c12 = "BROKEN: this check is wired to a tool event before or after a write, not to 'UserPromptSubmit' — fix: in hooks.json wire it to PostToolUse on Write|Edit, or run it with --scan [<dir>]"  # noqa: E501 — a golden line is typed whole  # noqa: E501 — a golden line is typed whole
    return all_of(
        expect(red, 2, messages.l4_simpler(DOC, 3, "prior to", "before").render(), "stderr"),
        expect(red, 2, f"RED: 1 finding(s) — 1 document examined ({DOC})", "stderr"),
        expect(green, 0, green_hook(), "stdout"),
        expect(gone, 0, shared.g1_green_skip(shared.g1_skip_gone("docs/notes/gone.md")), "stdout"),
        (messages.c12_event("UserPromptSubmit").render() == c12, "C12 typed whole"),
        broken_first_line(elsewhere, c12),
        broken_first_line(  # an event name only points: cut at 80 characters, the cut said, then escaped
            odd_event,
            "BROKEN: this check is wired to a tool event before or after a write, not to 'N\\nx\\\\y"
            + "e" * 75
            + "… [95 characters]' — fix: in hooks.json wire it to PostToolUse on Write|Edit, or run it with"
            " --scan [<dir>]",
        ),
        expect(stop, 0, shared.g1_green_skip(shared.g1_skip_other_tool("")), "stdout"),
    )


def t9() -> tuple[bool, str]:
    """Levels: grade at warning is a note and the write is green; every rule off is refused; an
    unknown rule, a level that is none of the three, and a mapping that is not one, each C5."""
    found = messages.l1_grade(DOC, GRADE_RED_VALUE, 10.0)
    warned, _ = gate_on(Write(DOC, GRADE_RED), own(levels={"grade": "warning"}))
    all_off = own(levels={r.value: "off" for r in Rule})
    return all_of(
        expect(context(warned), 0, messages.n2_warning(DOC, Rule.GRADE, found), "stdout"),
        expect(context(warned), 0, green_hook(), "stdout"),
        broken(gate_on(Write(DOC, PLAIN), all_off)[0], messages.c5_all_off()),
        broken(
            gate_on(Write(DOC, PLAIN), own(levels={"tone": "error"}))[0],
            shared.c5_unknown_dial("levels.tone", [f"levels.{r.value}" for r in Rule]),
        ),
        broken(
            gate_on(Write(DOC, PLAIN), own(levels={"grade": "loud"}))[0], messages.c5_level("grade", "loud")
        ),
        broken(gate_on(Write(DOC, PLAIN), own(levels=["grade"]))[0], messages.c5_levels()),
    )


def broken(result: Result, failure: object) -> tuple[bool, str]:
    line = failure.render() if hasattr(failure, "render") else str(failure)
    ok, evidence = broken_first_line(result, line)
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def t10() -> tuple[bool, str]:
    """This module's C5 lines typed by hand, each exit 1 with the count line after it."""
    pairs: list[tuple[dict[str, object], str]] = [
        (
            own(tone="plain"),
            "BROKEN: constitution.yaml: const-language.tone is no dial of this module — fix: a misspelt dial would be ignored in silence, so none is: write one of severity, log_dir, territories, grade_ceiling, sentence_words, levels, forbidden, simpler, exceptions, departures",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(territories=[]),
            'BROKEN: constitution.yaml: const-language.territories must be a non-empty list of path patterns — fix: write the patterns of the documents to check, one per line under "- ", or leave the key out to cover every Markdown file; an empty list would examine nothing in silence',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(territories=["#docs/**"]),
            "BROKEN: constitution.yaml: const-language.territories holds a pattern git would not read as one: '#docs/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(territories=["a\nb"]),
            "BROKEN: constitution.yaml: const-language.territories holds a pattern git would not read as one: 'a\\nb' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(grade_ceiling=-1),
            "BROKEN: constitution.yaml: const-language.grade_ceiling must be a finite number of 0 or more — fix: write the Flesch–Kincaid grade a document may reach, such as 10, or leave the key out for the default",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(grade_ceiling=float("nan")),
            "BROKEN: constitution.yaml: const-language.grade_ceiling must be a finite number of 0 or more — fix: write the Flesch–Kincaid grade a document may reach, such as 10, or leave the key out for the default",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(grade_ceiling="ten"),
            "BROKEN: constitution.yaml: const-language.grade_ceiling must be a finite number of 0 or more — fix: write the Flesch–Kincaid grade a document may reach, such as 10, or leave the key out for the default",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(sentence_words=0),
            "BROKEN: constitution.yaml: const-language.sentence_words must be a whole number of 1 or more — fix: write the words a sentence may hold, such as 25, or leave the key out for the default",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(sentence_words=25.5),
            "BROKEN: constitution.yaml: const-language.sentence_words must be a whole number of 1 or more — fix: write the words a sentence may hold, such as 25, or leave the key out for the default",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels="error"),
            "BROKEN: constitution.yaml: const-language.levels must be a mapping of rule to level — fix: write it as levels: {grade: error, sentence: error, forbidden: error, simpler: error, passive: warning}, any subset; the levels are error, warning, off",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels={"grade": "loud"}),
            "BROKEN: constitution.yaml: const-language.levels.grade is 'loud', and the levels are error, warning, off — fix: set it to error (a finding, red), warning (reported, not red) or off, or remove the line; the rules are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels={r.value: "off" for r in Rule}),
            "BROKEN: constitution.yaml: const-language.levels switches every rule off — fix: a gate that checks nothing would report green as if it had checked: set at least one rule to error or warning, or remove the plugin",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(forbidden="synergy"),
            'BROKEN: constitution.yaml: const-language.forbidden must be a list of phrases, each one non-empty line — fix: write one phrase per line under "- ", or leave the key out',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(forbidden=[""]),
            'BROKEN: constitution.yaml: const-language.forbidden must be a list of phrases, each one non-empty line — fix: write one phrase per line under "- ", or leave the key out',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(exceptions=[3]),
            'BROKEN: constitution.yaml: const-language.exceptions must be a list of phrases, each one non-empty line — fix: write one phrase per line under "- ", or leave the key out',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(simpler=["prior to"]),
            'BROKEN: constitution.yaml: const-language.simpler must be a mapping of phrase to plain word, each one non-empty line — fix: write one line per pair, the phrase as the key and the plain word as the value, such as "prior to: before", or leave the key out',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(simpler={"prior to": ""}),
            'BROKEN: constitution.yaml: const-language.simpler must be a mapping of phrase to plain word, each one non-empty line — fix: write one line per pair, the phrase as the key and the plain word as the value, such as "prior to: before", or leave the key out',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures="none"),
            'BROKEN: constitution.yaml: const-language.departures must be a list of entries — fix: write one entry per "- " item with the fields paths (a list of patterns), allow (a list of rule keys) and reason (one line); leave the key out, or write [], for no departure',  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=["x"]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: it is not a mapping — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["grade"], "reason": "r", "why": "x"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: 'why' is no field of an entry — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": [], "allow": ["grade"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: paths must be a non-empty list of path patterns — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["#a.md"], "allow": ["grade"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1 paths holds a pattern git would not read as one: '#a.md' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["#" + "x" * 100], "allow": ["grade"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1 paths holds a pattern git would not read as one: '#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx… [101 characters]' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": [], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: allow must be a non-empty list of rule keys — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["tone"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: 'tone' is no rule this gate knows — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["grade"], "reason": "a\rb"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: reason must be one non-empty line saying why — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(
                departures=[
                    {
                        "paths": ["a.md"],
                        "allow": ["grade"],
                        "reason": "r",
                        "x" * 100 + "\ny": 1,
                    }
                ]
            ),
            "BROKEN: constitution.yaml: const-language.departures entry 1: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx… [102 characters]' is no field of an entry — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            {NAMESPACE: {"x" * 70 + "\n" + "y" * 20: 1}},
            "BROKEN: constitution.yaml: const-language.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\\nyyyyyyyyy… [91 characters] is no dial of this module — fix: a misspelt dial would be ignored in silence, so none is: write one of severity, log_dir, territories, grade_ceiling, sentence_words, levels, forbidden, simpler, exceptions, departures",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels={"x" * 70 + "\n" + "y" * 20: "error"}),
            "BROKEN: constitution.yaml: const-language.levels.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\\nyy… [98 characters] is no dial of this module — fix: a misspelt dial would be ignored in silence, so none is: write one of levels.grade, levels.sentence, levels.forbidden, levels.simpler, levels.passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels={"grade": "x" * 70 + "\n" + "y" * 20}),
            "BROKEN: constitution.yaml: const-language.levels.grade is 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\\nyyyyyyyyy… [91 characters]', and the levels are error, warning, off — fix: set it to error (a finding, red), warning (reported, not red) or off, or remove the line; the rules are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(territories=["#" + "x" * 69 + "\n" + "y" * 20]),
            "BROKEN: constitution.yaml: const-language.territories holds a pattern git would not read as one: '#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\\nyyyyyyyyy… [91 characters]' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["x" * 70 + "\n" + "y" * 20], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\\nyyyyyyyyy… [91 characters]' is no rule this gate knows — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels={"grade": "a\nb"}),
            "BROKEN: constitution.yaml: const-language.levels.grade is 'a\\nb', and the levels are error, warning, off — fix: set it to error (a finding, red), warning (reported, not red) or off, or remove the line; the rules are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(
                departures=[
                    {"paths": ["a.md"], "allow": ["grade"], "reason": "r", "x" * 70 + "\n" + "y" * 20: 1}
                ]
            ),
            "BROKEN: constitution.yaml: const-language.departures entry 1: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\\nyyyyyyyyy… [91 characters]' is no field of an entry — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(territories=["#" + "x" * 100]),
            "BROKEN: constitution.yaml: const-language.territories holds a pattern git would not read as one: '#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx… [101 characters]' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape a leading # as \\# bare or in single quotes, as \\\\# in double quotes, and remove a line break",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(levels={"a\nb": "error"}),
            "BROKEN: constitution.yaml: const-language.levels.a\\nb is no dial of this module — fix: a misspelt dial would be ignored in silence, so none is: write one of levels.grade, levels.sentence, levels.forbidden, levels.simpler, levels.passive",  # noqa: E501 — a golden line is typed whole
        ),
        (  # two unknown rules, the later one written first: the first in sorted order is named, as C5.10 does
            own(levels={"zeta": "error", "alpha": "error"}),
            "BROKEN: constitution.yaml: const-language.levels.alpha is no dial of this module — fix: a misspelt dial would be ignored in silence, so none is: write one of levels.grade, levels.sentence, levels.forbidden, levels.simpler, levels.passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["grade"], "reason": "a\nb"}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: reason must be one non-empty line saying why — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["grade"], "reason": " "}]),
            "BROKEN: constitution.yaml: const-language.departures entry 1: reason must be one non-empty line saying why — fix: write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these documents stand as written>; the keys are grade, sentence, forbidden, simpler, passive",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(exceptions=["z" * 100]),
            "BROKEN: constitution.yaml: const-language.exceptions names 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz… [100 characters]', which no forbidden phrase and no simpler pair holds — fix: an exception removes a phrase the rules know; check its spelling against the rules' lists, or remove it",  # noqa: E501 — a golden line is typed whole
        ),
        (
            own(exceptions=["hit the road"]),
            "BROKEN: constitution.yaml: const-language.exceptions names 'hit the road', which no forbidden phrase and no simpler pair holds — fix: an exception removes a phrase the rules know; check its spelling against the rules' lists, or remove it",  # noqa: E501 — a golden line is typed whole
        ),
        (  # a phrase is one line by the dial's own rule; its backslash is shown escaped
            own(exceptions=["a\\b"]),
            "BROKEN: constitution.yaml: const-language.exceptions names 'a\\\\b', which no forbidden phrase and no simpler pair holds — fix: an exception removes a phrase the rules know; check its spelling against the rules' lists, or remove it",  # noqa: E501 — a golden line is typed whole
        ),
    ]
    block_scalar = own(departures=[{"paths": ["a.md"], "allow": ["grade"], "reason": "why\n"}])
    return all_of(
        *(broken(gate_on(Write(DOC, PLAIN), patch)[0], line) for patch, line in pairs),
        # what `reason: |` gives, a line break at the end: trimmed and taken, as in the other two gates
        expect(gate_on(Write(DOC, PLAIN), block_scalar)[0], 0, green_hook(), "stdout"),
    )


def fake_vale(directory: Path, script: str) -> Path:
    """A PATH directory with the real python3, git, sh and dirname, and a `vale` that runs `script`
    (a shell body) and logs every invocation to `calls` beside it."""
    for tool in ("python3", "git", "sh", "dirname"):
        source = (
            os.path.realpath(sys.executable)
            if tool == "python3"
            else os.popen(f"command -v {tool}").read().strip()
        )
        os.symlink(source, directory / tool)
    fake = directory / "vale"
    fake.write_text(f'#!/bin/sh\necho "$@" >> "{directory / "calls"}"\n{script}\n', encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return directory


def t11() -> tuple[bool, str]:
    """Absence of the binary, each line typed by hand: no vale on PATH is C2 with the install
    command; an old vale is C2 with its version; a vale that cannot run is C12 with its own first
    line; a vale with no version line, or one whose --version exits 1, is C12; a vale whose run
    outlasts the hook's budget is C12 in the check after a write, and in one before a write where a
    consumer wires it, naming the budget and the scan, while the scan waits and is green; a vale
    whose --version outlasts its own budget is C12 in both modes, the check after a write and the
    scan — the five runs side by side, so the item costs the budget plus a second or so; under a hook
    whose declared budget is lower than a wait's cap, the same slow run and a probe that answers after 4 s
    are cut at what the deadline has left, and the line is the deadline's, C12.14, naming the wait and
    the budget — and every fake was asked what the gate says."""
    none = H.scratch_dir()
    for tool in ("python3", "git", "sh", "dirname"):
        source = (
            os.path.realpath(sys.executable)
            if tool == "python3"
            else os.popen(f"command -v {tool}").read().strip()
        )
        os.symlink(source, none / tool)
    old = fake_vale(H.scratch_dir(), 'echo "vale version 3.19.0"')
    failing = fake_vale(
        H.scratch_dir(),
        'case "$1" in --version) echo "vale version 3.23.0";; *) echo \'{"Line":1,"Path":"x","Text":"E201 something broke","Code":"E201","Span":1}\'; exit 2;; esac',  # noqa: E501 — a golden line is typed whole
    )
    mute = fake_vale(H.scratch_dir(), "echo hello")
    odd_version = fake_vale(
        H.scratch_dir(), "printf '%s\\n' 'a\\b " + "w" * 90 + "'"
    )  # a backslash, 93 characters
    odd_exit = fake_vale(H.scratch_dir(), "printf '%s\\n' 'a\\b " + "w" * 90 + "'; exit 1")
    odd_failed = fake_vale(
        H.scratch_dir(),
        'case "$1" in --version) echo "vale version 3.23.0";; *) printf \'%s\\n\' \'{"Text":"E201 a\\\\b '
        + "w" * 90
        + "\"}'; exit 2;; esac",
    )
    failing_version = fake_vale(H.scratch_dir(), 'echo "vale version 3.23.0"; exit 1')
    missing = "BROKEN: const-language needs vale 3.23.0 or newer on PATH — fix: brew install vale (macOS, Linuxbrew), or the other routes at https://vale.sh/docs/install — until then Markdown writes pass unchecked"  # noqa: E501 — a golden line is typed whole
    too_old = "BROKEN: const-language needs vale 3.23.0 or newer, found 3.19.0 — fix: upgrade it: brew install vale (macOS, Linuxbrew), or the other routes at https://vale.sh/docs/install — until then Markdown writes pass unchecked"  # noqa: E501 — a golden line is typed whole
    failed = "BROKEN: vale could not run: E201 something broke — fix: repair what the message names — the binary, its permissions, the temporary directory — then run the check again"  # noqa: E501 — a golden line is typed whole
    no_version = "BROKEN: vale did not report its version (hello) — fix: run vale --version by hand and repair the installation — until then Markdown writes pass unchecked"  # noqa: E501 — a golden line is typed whole
    results = [
        gate_on(Write(DOC, PLAIN), env={"PATH": str(directory)})[0]
        for directory in (none, old, failing, mute, failing_version)
    ]
    exit_one = "BROKEN: vale --version failed (exit 1: vale version 3.23.0) — fix: run vale --version by hand and repair the installation — until then Markdown writes pass unchecked"  # noqa: E501 — a golden line is typed whole
    scan_old = H.run_gate("", args=["--scan", str(prepared(files={DOC: PLAIN}))], env={"PATH": str(old)})
    odd = [
        gate_on(Write(DOC, PLAIN), env={"PATH": str(directory)})[0]
        for directory in (odd_version, odd_exit, odd_failed)
    ]
    repair = (
        "run vale --version by hand and repair the installation — until then Markdown writes pass unchecked"
    )
    # answers --version at once, with the floor; its run is a second past the hook's budget, then `{}`
    sleep = shutil.which("sleep") or "/bin/sleep"  # the fake's PATH holds no sleep
    past = int(vale.HOOK_SECONDS) + 1
    slow_run = fake_vale(
        H.scratch_dir(),
        f'case "$1" in --version) echo "vale version 3.23.0";; *) {sleep} {past}; echo \'{{}}\';; esac',
    )
    in_the_hook = prepared(files={DOC: PLAIN})
    in_the_scan = prepared(files={DOC: PLAIN})
    on_path = {"PATH": str(slow_run)}

    def timed_hook() -> tuple[Result, float]:
        began = time.monotonic()
        event = event_json(in_the_hook, Write(DOC, "unused"), event="PostToolUse")
        return H.run_gate(event, env=on_path), time.monotonic() - began

    def timed_scan() -> tuple[Result, float]:
        began = time.monotonic()
        return H.run_gate("", args=["--scan", str(in_the_scan)], env=on_path), time.monotonic() - began

    # answers --version a second past its budget, then with the floor; its run would be quick
    slow_version = fake_vale(
        H.scratch_dir(),
        f'case "$1" in --version) {sleep} {vale.VERSION_SECONDS + 1}; echo "vale version 3.23.0";;'
        " *) echo '{}';; esac",
    )
    on_slow_version = {"PATH": str(slow_version)}
    version_hook_root = prepared(files={DOC: PLAIN})
    version_scan_root = prepared(files={DOC: PLAIN})

    def timed_version_hook() -> tuple[Result, float]:
        began = time.monotonic()
        event = event_json(version_hook_root, Write(DOC, "unused"), event="PostToolUse")
        return H.run_gate(event, env=on_slow_version), time.monotonic() - began

    def timed_version_scan() -> tuple[Result, float]:
        began = time.monotonic()
        result = H.run_gate("", args=["--scan", str(version_scan_root)], env=on_slow_version)
        return result, time.monotonic() - began

    # the same slow run before a write, where a consumer wires it: the budget is the hook's in both events
    before_root = prepared(files={DOC: PLAIN})

    def timed_before_hook() -> tuple[Result, float]:
        began = time.monotonic()
        result = H.run_gate(event_json(before_root, Write(DOC, PLAIN)), env=on_path)
        return result, time.monotonic() - began

    # the hook's own deadline, declared as 3 s, is shorter than the run's cap of 10 s: the same slow run is
    # cut at what that deadline has left, a little under 3 s, not at 10
    lowered_env, _ = git_patch(H, hook_seconds=3.0)
    lowered_root = prepared(files={DOC: PLAIN})

    def timed_lowered() -> tuple[Result, float]:
        began = time.monotonic()
        event = event_json(lowered_root, Write(DOC, "unused"), event="PostToolUse")
        return H.run_gate(event, env={**on_path, **lowered_env}), time.monotonic() - began

    # the same hook budget, lowered to 2 s, and a probe that answers after 4 s, under its cap of 5: the probe
    # is given what the deadline has left, so it is cut and the deadline's line says so; given its cap it
    # would answer, and the next wait, the run, would find the deadline spent and name itself instead
    probe_lowered_env, _ = git_patch(H, hook_seconds=2.0)
    slow_answer = fake_vale(
        H.scratch_dir(),
        f'case "$1" in --version) {sleep} {vale.VERSION_SECONDS - 1}; echo "vale version 3.23.0";;'
        " *) echo '{}';; esac",
    )
    probe_lowered_root = prepared(files={DOC: PLAIN})

    def timed_probe_lowered() -> tuple[Result, float]:
        began = time.monotonic()
        event = event_json(probe_lowered_root, Write(DOC, "unused"), event="PostToolUse")
        result = H.run_gate(event, env={"PATH": str(slow_answer), **probe_lowered_env})
        return result, time.monotonic() - began

    with ThreadPoolExecutor(max_workers=7) as pool:
        probe_lowered_hooked = pool.submit(timed_probe_lowered)
        lowered_hooked = pool.submit(timed_lowered)
        hooked = pool.submit(timed_hook)
        before_hooked = pool.submit(timed_before_hook)
        scanned = pool.submit(timed_scan)
        version_hooked = pool.submit(timed_version_hook)
        version_scanned = pool.submit(timed_version_scan)
    lowered_hook, lowered_took = lowered_hooked.result()
    probe_lowered_hook, probe_lowered_took = probe_lowered_hooked.result()
    hook, hook_took = hooked.result()
    before_hook, before_took = before_hooked.result()
    scan_slow, scan_took = scanned.result()
    version_hook, version_hook_took = version_hooked.result()
    version_scan, version_scan_took = version_scanned.result()
    no_answer = "BROKEN: vale did not report its version (no answer in 5 s) — fix: run vale --version by hand and repair the installation — until then Markdown writes pass unchecked"  # noqa: E501 — a golden line is typed whole
    too_slow = "BROKEN: vale gave no answer in 10 s, the most a check after a write waits — fix: a document of normal size takes vale well under a second, so the likely cause is a vale that hangs; run vale by hand to repair it, and the scan waits for vale as long as it takes — until then Markdown writes pass unchecked"  # noqa: E501 — a golden line is typed whole
    # a wait the hook's deadline cut short, then out of time, is the deadline's shared line naming the wait
    # and the whole budget the gate declares, never this module's line with the shortened number
    cut_run = shared.c12_hook_budget(3, "vale finished its run")
    cut_probe = shared.c12_hook_budget(2, "vale reported its version")
    return all_of(
        broken(hook, too_slow),
        (hook_took > 9, f"the check after a write gave up after {hook_took:.1f} s"),
        (
            broken(lowered_hook, cut_run)[0],
            f"under a hook that declares 3 s the run ended after {lowered_took:.1f} s:"
            f" {lowered_hook.stderr[:160]}",
        ),
        (
            broken(probe_lowered_hook, cut_probe)[0],
            f"under a hook that declares 2 s the probe, which answers after 4 s, ended after"
            f" {probe_lowered_took:.1f} s: {probe_lowered_hook.stderr[:160]}",
        ),
        broken(before_hook, too_slow),  # the same budget in the event the plugin does not wire
        (
            before_took > vale.HOOK_SECONDS - 1,
            f"the check before a write gave up after {before_took:.1f} s",
        ),
        expect(scan_slow, 0, green_scan(4), "stdout"),
        (
            scan_took > vale.HOOK_SECONDS,
            f"the scan stopped after {scan_took:.1f} s, within the hook's budget",
        ),
        broken(version_hook, no_answer),  # the probe's bound holds in a check after a write ...
        broken(version_scan, no_answer),  # ... and in the scan, which waits on the run but not on this
        (
            vale.VERSION_SECONDS - 1 < min(version_hook_took, version_scan_took),
            f"the probe gave up after {version_hook_took:.1f} s (hook), {version_scan_took:.1f} s (scan)",
        ),
        broken(  # a diagnosis is what the reader acts on: whole, its backslash doubled, 90 letters uncut
            odd[0],
            ("BROKEN: vale did not report its version (a\\\\b " + "w" * 90 + ") — fix: " + repair),
        ),
        broken(
            odd[1],
            ("BROKEN: vale --version failed (exit 1: a\\\\b " + "w" * 90 + ") — fix: " + repair),
        ),
        broken(
            odd[2],
            (
                "BROKEN: vale could not run: E201 a\\\\b "
                + "w" * 90
                + " — fix: repair what the message names"
                " — the binary, its permissions, the temporary directory — then run the check again"
            ),
        ),
        broken(results[0], missing),
        broken(results[1], too_old),
        broken(results[2], failed),
        broken(results[3], no_version),
        broken(results[4], exit_one),  # a version line with a failing exit is a failure, not a pass
        broken(scan_old, too_old),
        (
            set((old / "calls").read_text().split("\n")) <= {"--version", ""},
            "the old vale was asked its version and nothing else",
        ),
        (
            "--no-global" in (failing / "calls").read_text(),
            "the failing vale was run with the generated configuration",
        ),
    )


def t12() -> tuple[bool, str]:
    """The cap: sixty findings in one document show the first that fit in 8,000 characters after a
    write, the count line saying how many, the verdict staying under the platform's cap; the same
    with a finding of another length; the scan lists all sixty."""

    def fit_of(render: Callable[[int], str]) -> int:
        fit, size = 0, 0
        for line in range(3, 3 + 2 * 60, 2):
            size += len(render(line)) + 1
            if size > 8000:
                break
            fit += 1
        return fit

    text = "# T\n\n" + "\n\n".join(["Do it prior to noon."] * 60) + "\n"
    result, root = gate_on(Write(DOC, text), files={DOC: text})
    scanned = H.run_gate("", args=["--scan", str(root)])
    fit = fit_of(lambda line: messages.l4_simpler(DOC, line, "prior to", "before").render())
    count = (
        f"RED: 60 finding(s), the first {fit} shown — the scan lists them all — 1 document examined ({DOC})"
    )
    wide_text = "# T\n\n" + "\n\n".join(["<!-- vale off -->"] * 60) + "\n"
    wide, _ = gate_on(Write(DOC, wide_text))
    wide_fit = fit_of(lambda line: messages.l6_vale_comment(DOC, line, "<!-- vale off -->").render())
    wide_count = f"RED: 60 finding(s), the first {wide_fit} shown — the scan lists them all — 1 document examined ({DOC})"  # noqa: E501 — a golden line is typed whole
    weird_fit = fit_of(lambda line: messages.l4_simpler(WEIRD, line, "prior to", "before").render())
    weird, _ = gate_on(Write(WEIRD, text))
    weird_count = (  # the cut count line keeps the path whole, over 80 characters, escaped
        f"RED: 60 finding(s), the first {weird_fit} shown — the scan lists them all — 1 document examined ("
        + WEIRD_SHOWN
        + ")"
    )
    weird_tail = red_lines(weird.stderr)[-1] if red_lines(weird.stderr) else "no RED line"
    tail_of = red_lines(result.stderr)[-1] if red_lines(result.stderr) else "no RED line"
    wide_tail = red_lines(wide.stderr)[-1] if red_lines(wide.stderr) else "no RED line"
    return all_of(
        (
            result.code == 2 and 0 < fit < 60 and len(headlines(result)) == fit,
            f"exit {result.code}, {len(headlines(result))} shown of a fit of {fit}",
        ),
        (tail_of == count, f"count line: {tail_of}"),
        (weird_tail == weird_count, f"count line of a long path: {weird_tail}"),
        (len(result.stderr) < 10_000, f"{len(result.stderr)} characters of verdict"),
        (
            0 < wide_fit < 60 and len(headlines(wide)) == wide_fit,
            f"wide: {len(headlines(wide))} shown of {wide_fit}",
        ),
        (wide_tail == wide_count, f"wide count line: {wide_tail}"),
        (
            scanned.code == 2 and len(headlines(scanned, "stdout")) == 60,
            f"the scan shows {len(headlines(scanned, 'stdout'))}",
        ),
    )


def t13() -> tuple[bool, str]:
    """Territories: the scan counts examined against scanned; a negated pattern drops a file; a
    README at the top is covered by the default; the tail carries the dials' numbers; a covered
    document with an upper-case ending or a name starting with a dash is read as Markdown."""
    files = {DOC: SIMPLER_RED, "README.md": PLAIN, "docs/other/x.md": SIMPLER_RED}
    default = scan(files)
    narrowed = scan(files, own(territories=["docs/**/*.md", "!docs/other/**"]))
    dialled = scan({DOC: PLAIN}, own(grade_ceiling=12.5, sentence_words=40))
    outside, _ = gate_on(Write(WEIRD_OTHER, PLAIN), own(territories=["docs/notes/**"]))
    long_pattern = "docs\\gone/" + "p" * 100  # 110 characters with a backslash: a pattern only points
    stale = scan(
        {DOC: PLAIN}, own(departures=[{"paths": [long_pattern], "allow": ["simpler"], "reason": "moved"}])
    )
    return all_of(
        expect(  # the skip names the path whole and escaped, over 80 characters
            outside,
            0,
            "GREEN: const-language: 0 documents examined — " + WEIRD_OTHER_SHOWN + " is not covered"
            " (const-language.territories)",
            "stdout",
        ),
        (
            "note: const-language.departures entry 1 (docs\\\\gone/"
            + "p" * 70
            + "… [110 characters]) matches no"
            " covered document; the documents it allowed were deleted or moved, or the pattern is wrong"
            in stale.stdout.splitlines(),
            "the pattern cut at 80, said, then escaped: " + stale.stdout[:400],
        ),
        expect(default, 2, f"RED: 2 finding(s) — {tail(6)}", "stdout"),
        expect(narrowed, 2, f"RED: 1 finding(s) — {tail(4, 6)}", "stdout"),
        expect(dialled, 0, green_scan(4, ceiling=12.5, words=40), "stdout"),
        (
            "12.5 and 40 words" in dialled.stdout,
            f"the tail names the dials: {dialled.stdout.strip()}",
        ),
        *names_vale_cannot_read(),
    )


def names_vale_cannot_read() -> list[tuple[bool, str]]:
    """A covered document whose ending is in upper or mixed case is read as Markdown, by the scan and
    by the hook: a phrase in prose is found at its real path, a phrase only in code is not. One whose
    name starts with a dash is read too, not taken by Vale for a flag. Vale's keys are mapped back to
    the paths by name, not by position, and across the runs of `vale.CHUNK` documents: a scan of more
    than one run, plain documents sorting before each red one, finds each at its own path and line."""
    wide = own(territories=["*"])
    dash_found = messages.l4_simpler("-dash.md", 3, "prior to", "before").headline
    dash_scan = scan({"-dash.md": SIMPLER_RED})
    dash_root = prepared(files={"-dash.md": SIMPLER_RED})
    dash_written = after_write(dash_root, "-dash.md")
    prose_found = messages.l4_simpler("NOTES.MD", 3, "prior to", "before").headline
    in_code = "# T\n\nDo it before noon. A `prior to` span.\n\n```text\nprior to\n```\n"
    guide_found = messages.l4_simpler("docs/Guide.Md", 3, "prior to", "before").headline
    in_prose = scan({"NOTES.MD": SIMPLER_RED}, wide)
    in_a_span = scan({"NOTES.MD": in_code}, wide)
    root = prepared(wide, files={"docs/Guide.Md": SIMPLER_RED})
    written = after_write(root, "docs/Guide.Md")
    # CHUNK + 30 documents named so that their order is their number: the first red one stands in
    # the first run, the second in the second; plain ones sort before both, so that a map by position
    # or an index per run names another path, and each red one has its own line
    many = vale.CHUNK + 30
    first_red = "docs/many/n0007.md"
    second_red = f"docs/many/n{vale.CHUNK + 12:04d}.md"
    later_red = "# T\n\nIt is warm.\n\nDo it prior to noon.\n"  # the phrase on line 5
    crowd = {f"docs/many/n{index:04d}.md": PLAIN for index in range(many)}
    crowd[first_red] = SIMPLER_RED
    crowd[second_red] = later_red
    crowd_root = prepared(files=crowd)
    present = len(list_markdown(crowd_root))  # the consumer's own files beside the crowd, all covered
    across = H.run_gate("", args=["--scan", str(crowd_root)])
    across_found = [
        f"RED: {messages.l4_simpler(first_red, 3, 'prior to', 'before').headline}",
        f"RED: {messages.l4_simpler(second_red, 5, 'prior to', 'before').headline}",
    ]
    return [
        (
            in_prose.code == 2
            and headlines(in_prose, "stdout") == [f"RED: {prose_found}"]
            and f"RED: 1 finding(s) — {tail(4)}" in in_prose.stdout,
            f"NOTES.MD under '*' found by the scan, counted as examined: {in_prose.stdout.strip()}"
            f"{in_prose.stderr.strip()}",
        ),
        expect(in_a_span, 0, green_scan(4), "stdout"),
        (
            written.code == 2 and headlines(written) == [f"RED: {guide_found}"],
            f"docs/Guide.Md found by the hook after a write: exit {written.code}: {written.stderr.strip()}",
        ),
        (
            dash_scan.code == 2
            and headlines(dash_scan, "stdout") == [f"RED: {dash_found}"]
            and f"RED: 1 finding(s) — {tail(4)}" in dash_scan.stdout,
            f"-dash.md found by the default scan, counted as examined: exit {dash_scan.code}:"
            f" {dash_scan.stdout.strip()}{dash_scan.stderr.strip()}",
        ),
        (
            dash_written.code == 2 and headlines(dash_written) == [f"RED: {dash_found}"],
            f"-dash.md found by the hook after a write: exit {dash_written.code}:"
            f" {dash_written.stderr.strip()}",
        ),
        (
            present > vale.CHUNK + 30
            and across.code == 2
            and headlines(across, "stdout") == across_found
            and f"RED: 2 finding(s) — {tail(present)}" in across.stdout,
            f"{many} documents over two runs, one red in each, found at their own paths and lines,"
            f" every one counted: exit {across.code}: {across.stdout.strip()}{across.stderr.strip()}",
        ),
    ]


def t14() -> tuple[bool, str]:
    """A value of 12,000 characters echoed by L3 is cut and the cut is said; the verdict stays a
    message."""
    phrase = "x" * 12000
    result, _ = gate_on(Write(DOC, f"# T\n\nThe {phrase} word.\n"), own(forbidden=[phrase]))
    said = result.stderr
    ok = (
        result.code == 2
        and len(red_lines(said)) == 2
        and "… [12000 characters]" in said
        and "x" * 81 not in said
        and len(said) < 2_000
    )
    return ok, f"exit {result.code}, {len(said)} characters" if ok else f"exit {result.code}: {said[:300]}"


def t15() -> tuple[bool, str]:
    """Golden lines: one document carrying every rule once, its whole scan output typed by hand —
    headlines, whys, fixes, the note and the count line — since a fixture built from the message
    functions cannot see a changed word."""
    text = (
        "# T\n\n<!-- vale Language.Forbidden = NO -->\n"
        f"{GRADE_RED.split(chr(10))[2]}\n\n"
        f"{LONG_SENTENCE}\n\nWe will hit the ground running. Do it prior to noon. The report was written.\n"
    )
    result = scan({DOC: text})
    typed = "\n".join(
        [
            f"note: {DOC}:8: passive voice — 'was written' — reported, not red, while const-language.levels.passive is warning",  # noqa: E501 — a golden line is typed whole
            f"RED: {DOC}:1: the document reads at grade 10.83 by Flesch–Kincaid, above the ceiling of 10",  # noqa: E501 — a golden line is typed whole
            "  why: a reader whose first language is not English pays for every year of schooling the prose assumes, and the grade rises with words per sentence and syllables per word",  # noqa: E501 — a golden line is typed whole
            f"  fix: split the long sentences and prefer short words in the prose outside headings, code and tables until the grade is at or under 10; the ceiling for this repository is const-language.grade_ceiling in constitution.yaml{ALLOW_GRADE}",  # noqa: E501 — a golden line is typed whole
            f"RED: {DOC}:3: a Vale comment in the document — <!-- vale Language.Forbidden = NO -->",  # noqa: E501 — a golden line is typed whole
            "  why: a comment that switches a rule off is a mark in the document, which the gate blanks before it reads; what departs from a rule is declared in the dials file, where every reader sees it",  # noqa: E501 — a golden line is typed whole
            "  fix: remove the comment; to change a rule for this repository set its level or threshold under const-language in constitution.yaml, or, for a document that must stand as written, declare the departure with its reason in const-language.departures there",  # noqa: E501 — a golden line is typed whole
            f"RED: {DOC}:6: a sentence of 32 words, over the limit of 25 — The cat sat on the mat and the dog ran to the door and the bird flew up to the r… [130 characters]",  # noqa: E501 — a golden line is typed whole
            "  why: a sentence longer than the limit carries more than one idea, and a non-native reader loses the first before reaching the last",  # noqa: E501 — a golden line is typed whole
            f"  fix: split it at a clause into sentences of at most 25 words; the limit for this repository is const-language.sentence_words in constitution.yaml{ALLOW_SENTENCE}",  # noqa: E501 — a golden line is typed whole
            f"RED: {DOC}:8: 'hit the ground running' is a construction plain language avoids",  # noqa: E501 — a golden line is typed whole
            "  why: an idiom or a formal phrase says nothing a plain sentence does not, and a non-native reader must translate it before reading on",  # noqa: E501 — a golden line is typed whole
            f"  fix: say it in plain words, or drop it; a phrase this repository keeps on purpose is named in const-language.exceptions in constitution.yaml{ALLOW_FORBIDDEN}",  # noqa: E501 — a golden line is typed whole
            f"RED: {DOC}:8: 'prior to' where the plain word is 'before'",  # noqa: E501 — a golden line is typed whole
            "  why: a long or formal word costs a non-native reader a dictionary where the plain one does not",  # noqa: E501 — a golden line is typed whole
            f"  fix: write 'before'; a word this repository keeps on purpose is named in const-language.exceptions in constitution.yaml{ALLOW_SIMPLER}",  # noqa: E501 — a golden line is typed whole
            "RED: 5 finding(s) — 4 document(s) examined under a grade ceiling of 10 and 25 words per sentence and 0 departure(s), 4 Markdown file(s) scanned",  # noqa: E501 — a golden line is typed whole
            F10,
            "",
        ]
    )
    ok = result.code == 2 and result.stdout == typed
    long_path = scan(
        {WEIRD: text}
    )  # every finding and the note name the path whole, escaped, over 80 characters
    long_lines = long_path.stdout.splitlines()
    long_ok = (
        long_path.code == 2
        and len(headlines(long_path, "stdout")) == 5
        and all(line.startswith("RED: " + WEIRD_SHOWN + ":") for line in headlines(long_path, "stdout"))
        and long_lines[0].startswith("note: " + WEIRD_SHOWN + ":8: passive voice")
    )
    return all_of(
        (ok, "the whole output typed by hand" if ok else f"exit {result.code}:\n{result.stdout}"),
        (
            long_ok,
            "the path whole in every headline"
            if long_ok
            else f"exit {long_path.code}:\n{long_path.stdout[:600]}",
        ),
    )


def pointer_wiring(hooks: dict[str, list[dict[str, object]]]) -> tuple[bool, str]:
    """SessionStart and SubagentStart: one handler each, no matcher, exec form sh, an integer timeout,
    the script there."""
    wanted = {
        "SessionStart": ["${CLAUDE_PLUGIN_ROOT}/scripts/print-skill-pointer.sh"],
        "SubagentStart": ["${CLAUDE_PLUGIN_ROOT}/scripts/print-skill-pointer.sh", "--subagent"],
    }
    for event, args in wanted.items():
        entries = hooks.get(event, [])
        handlers = entries[0].get("hooks") if len(entries) == 1 else None
        if (
            not isinstance(handlers, list)
            or len(handlers) != 1
            or "matcher" in entries[0]
            or handlers[0].get("type") != "command"
            or handlers[0].get("command") != "sh"
            or handlers[0].get("args") != args
            or not isinstance(handlers[0].get("timeout"), int)
        ):
            return False, f"{event} is not one handler, no matcher, exec form sh, integer timeout: {entries}"
    if not (SCRIPTS / "print-skill-pointer.sh").is_file():
        return False, "scripts/print-skill-pointer.sh is missing"
    return True, "SessionStart and SubagentStart: one handler each, no matcher, sh, integer timeout"


def t16() -> tuple[bool, str]:
    """The skill's description is under the platform's cap; the hook is wired after the write, and
    besides it only the two pointer events (the pointer's own item proves what they print), with an
    integer timeout; the version probe and then the run, both read from the module's own code, fit the
    hook's budget the gate declares (`GATE.hook_seconds`), which the handler's timeout holds with
    `LEFT_FOR_THE_REST` (the shared item S165); the manifest names the plugin at a draft version; the
    install note's calibration example is accepted."""
    texts = {p.name: p.read_text(encoding="utf-8") for p in (SKILL, INSTALL, MANIFEST)}
    front = yaml.safe_load(texts["SKILL.md"].split("---")[1])
    description = str(front["description"])
    hooks = json.loads(HOOKS.read_text(encoding="utf-8"))["hooks"]
    entry = hooks["PostToolUse"][0]
    manifest = json.loads(texts["plugin.json"])
    example = re.search(r"```yaml\n(.*?)```", texts["INSTALL.md"], re.DOTALL)
    assert example
    patch = yaml.safe_load(example.group(1))
    accepted, _ = gate_on(Write(DOC, PLAIN), patch)
    stated = re.search(
        r"a description of (\d+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    timeout = entry["hooks"][0].get("timeout")
    needed = vale.VERSION_SECONDS + vale.HOOK_SECONDS
    budget = start.GATE.hook_seconds
    return all_of(
        (len(description) < 1536, f"description of {len(description)} characters"),
        (
            stated is not None and int(stated.group(1)) == len(description),
            f"the module document states the size: {stated.group(1) if stated else 'none'}",
        ),
        (
            list(hooks) == ["PostToolUse", "SessionStart", "SubagentStart"]
            and entry["matcher"] == "Write|Edit"
            and entry["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/check-language.sh"],
            "PostToolUse on Write|Edit through the plugin root, and the two pointer events, no other",
        ),
        pointer_wiring(hooks),
        (
            isinstance(timeout, int) and needed <= budget,
            f"the version probe's {vale.VERSION_SECONDS} s and the run's {vale.HOOK_SECONDS} s, {needed} s in"
            f" all, fit the hook's budget of {budget:g} s"
            if isinstance(timeout, int) and needed <= budget
            else f"timeout {timeout!r} is no integer"
            if not isinstance(timeout, int)
            else f"the version probe's {vale.VERSION_SECONDS} s and the run's {vale.HOOK_SECONDS} s,"
            f" {needed} s in all, are over the hook's budget of {budget:g} s",
        ),
        (
            manifest["name"] == NAMESPACE and manifest["version"].startswith("0.0."),
            f"manifest {manifest['version']}",
        ),
        expect(accepted, 0, green_hook(), "stdout"),
    )


# The founding lists, typed whole: a phrase deleted, respelt or given another plain word turns T17 red.
FORBIDDEN_TYPED = (
    "hit the ground running",
    "low-hanging fruit",
    "move the needle",
    "boil the ocean",
    "touch base",
    "circle back",
    "on the same page",
    "up to speed",
    "silver bullet",
    "at the end of the day",
    "needless to say",
    "it goes without saying",
    "as a matter of fact",
    "in the grand scheme of things",
    "when all is said and done",
    "a level playing field",
    "think outside the box",
    "the ball is in your court",
    "back to the drawing board",
    "bite the bullet",
    "cut corners",
    "get the ball rolling",
    "last but not least",
    "notwithstanding",
    "aforementioned",
    "heretofore",
    "hereinafter",
    "it should be noted that",
    "it is worth noting that",
    "it is important to note that",
)
SIMPLER_TYPED = {
    "prior to": "before",
    "subsequent to": "after",
    "in order to": "to",
    "utilize": "use",
    "utilise": "use",
    "leverage": "use",
    "commence": "begin",
    "terminate": "end",
    "endeavour": "try",
    "endeavor": "try",
    "facilitate": "help",
    "in the event that": "if",
    "with regard to": "about",
    "with respect to": "about",
    "in regard to": "about",
    "a number of": "some",
    "in excess of": "more than",
    "in the near future": "soon",
    "at this point in time": "now",
    "on a daily basis": "daily",
    "with the exception of": "except",
    "take into consideration": "consider",
    "in spite of the fact that": "although",
    "due to the fact that": "because",
    "in light of the fact that": "because",
    "for the purpose of": "to",
    "is able to": "can",
    "whilst": "while",
    "amongst": "among",
    "numerous": "many",
    "sufficient": "enough",
    "approximately": "about",
    "subsequently": "later",
}


def t17() -> tuple[bool, str]:
    """Determinism: two runs on the same input print the same verdict; the founding lists equal the
    lists typed here, hold no duplicate and no phrase that is both forbidden and simpler; a document
    that uses every phrase once gets one finding per phrase, in order, each echoing its own phrase."""
    files = {DOC: SIMPLER_RED + LONG_SENTENCE + "\n", "docs/notes/d.md": GRADE_RED}
    first = scan(files)
    second = scan(files)
    overlap = sorted(set(FORBIDDEN_TYPED) & set(SIMPLER_TYPED))
    phrases = [*FORBIDDEN_TYPED, *SIMPLER_TYPED]
    every = "# T\n\n" + "\n\n".join(f"We {phrase} today." for phrase in phrases) + "\n"
    fired = scan({DOC: every})
    echoed = [line.split("'")[1] if "'" in line else "" for line in headlines(fired, "stdout")]
    return all_of(
        (first.stdout == second.stdout and first.code == second.code == 2, "two scans, one output"),
        (
            tuple(rules.FORBIDDEN) == FORBIDDEN_TYPED and dict(rules.SIMPLER) == SIMPLER_TYPED,
            "the founding lists equal the lists typed here",
        ),
        (
            len(set(FORBIDDEN_TYPED)) == len(FORBIDDEN_TYPED) and not overlap,
            f"lists disjoint, no duplicate: {overlap}",
        ),
        (
            fired.code == 2 and echoed == phrases,
            f"one finding per phrase, in order, each echoing its own: {len(echoed)} of {len(phrases)}",
        ),
    )


def t18() -> tuple[bool, str]:
    """An Edit before the write is judged on the document it produces; the sentence echo comes from
    the document's own line; a finding's line survives a fence above it."""
    edit = Edit(DOC, "before noon", "prior to noon")
    result, _ = gate_on(edit, files={DOC: SIMPLER_GREEN})
    fenced = "# T\n\n```text\nprior to\n```\n\nDo it prior to noon.\n"
    return all_of(
        expect(result, 2, messages.l4_simpler(DOC, 3, "prior to", "before").headline, "stderr"),
        one_finding(fenced, messages.l4_simpler(DOC, 7, "prior to", "before").headline),
    )


def t19() -> tuple[bool, str]:
    """Departures: an entry by pattern allows a rule in every document it matches; one by path allows
    that document alone; an entry allowing one rule does not allow another; a stale entry is a note,
    typed by hand, first on stdout, and the scan green; the hook honours a departure too; the count
    line names the departures."""
    by_pattern = own(
        departures=[{"paths": ["docs/notes/**"], "allow": ["simpler"], "reason": "frozen notes"}]
    )
    by_path = own(
        departures=[{"paths": ["/docs/notes/c.md"], "allow": ["simpler"], "reason": "one frozen note"}]
    )
    stale = own(departures=[{"paths": ["docs/gone/**"], "allow": ["grade"], "reason": "gone"}])
    two = {DOC: SIMPLER_RED, "docs/notes/d.md": SIMPLER_RED}
    pattern_run = scan(two, by_pattern)
    path_run = scan(two, by_path)
    other_rule = scan({DOC: GRADE_RED + "\nDo it prior to noon.\n"}, by_pattern)
    stale_run = scan({DOC: PLAIN}, stale)
    note = "note: const-language.departures entry 1 (docs/gone/**) matches no covered document; the documents it allowed were deleted or moved, or the pattern is wrong"  # noqa: E501 — a golden line is typed whole
    hooked, _ = gate_on(Write(DOC, SIMPLER_RED), by_path)
    return all_of(
        expect(pattern_run, 0, green_scan(5, departures=1), "stdout"),
        expect(path_run, 2, f"RED: 1 finding(s) — {tail(5, departures=1)}", "stdout"),
        (
            headlines(path_run, "stdout")
            == [f"RED: {messages.l4_simpler('docs/notes/d.md', 3, 'prior to', 'before').headline}"],
            "the entry by path leaves the other document red",
        ),
        (
            len(headlines(other_rule, "stdout")) == 1
            and headlines(other_rule, "stdout")[0].startswith(f"RED: {DOC}:1: the document reads at grade"),
            f"an entry allowing simpler leaves the grade red: {headlines(other_rule, 'stdout')}",
        ),
        (
            stale_run.code == 0 and stale_run.stdout.splitlines()[0] == note,
            f"a stale entry is the note first, the scan green: {stale_run.stdout.splitlines()[:1]}",
        ),
        (
            (entry := own_dials_entry(stale)) is not None and messages.n3_stale_departure(1, entry) == note,
            "the note typed whole",
        ),
        expect(hooked, 0, green_hook(), "stdout"),
    )


def own_dials_entry(patch: dict[str, object]) -> Departure | None:
    """The one departure of a patch, as the gate's own parser reads it; None where the parser reads
    none, so that a mutant there fails the item instead of crashing the runner."""
    namespace = patch[NAMESPACE]
    assert isinstance(namespace, dict)
    departures = own_dials.parse(namespace).departures
    return departures[0] if departures else None


# ---------------------------------------------------------------- the red→green cases


def case(number: int, title: str, red: str, expect_finding: Finding, green: str) -> Case:
    return Case(
        number,
        f"red→green: {title}",
        Write(DOC, red),
        Write(DOC, green),
        expect_finding,
        messages.g1_covered(),
    )


CASES = [
    case(21, "the grade ceiling", GRADE_RED, messages.l1_grade(DOC, GRADE_RED_VALUE, 10.0), PLAIN),
    case(
        22,
        "the sentence limit",
        SENTENCE_RED,
        messages.l2_sentence(DOC, 3, 32, 25, LONG_SENTENCE),
        SENTENCE_GREEN,
    ),
    case(
        23,
        "a forbidden construction",
        IDIOM_RED,
        messages.l3_forbidden(DOC, 3, "hit the ground running"),
        IDIOM_GREEN,
    ),
    case(
        24,
        "a word with a plain replacement",
        SIMPLER_RED,
        messages.l4_simpler(DOC, 3, "prior to", "before"),
        SIMPLER_GREEN,
    ),
    case(
        25,
        "a Vale comment",
        "# T\n\n<!-- vale off -->\nShort.\n",
        messages.l6_vale_comment(DOC, 3, "<!-- vale off -->"),
        COMMENT_GREEN,
    ),
]


def ran_pointer(*args: str) -> Result:
    done = subprocess.run(
        [H.sh, str(SCRIPTS / "print-skill-pointer.sh"), *args],
        input="{}",
        capture_output=True,
        text=True,
        check=False,
    )
    return Result(done.returncode, done.stdout, done.stderr)


def t20() -> tuple[bool, str]:
    """The pointer, run through sh: exit 0, the line typed here and nothing on stderr; with --subagent
    one JSON object that adds the same line to the subagent's context and nothing else; the line is of
    the size the module document states and names a skill folder."""
    plain = ran_pointer()
    sub = ran_pointer("--subagent")
    if (plain.code, plain.stdout, plain.stderr) != (0, POINTER + "\n", ""):
        return False, f"session start: {plain}"
    if sub.code != 0 or sub.stderr != "":
        return False, f"subagent start: {sub}"
    try:
        answer = json.loads(sub.stdout)
    except json.JSONDecodeError:
        return False, f"subagent start is not JSON: {sub.stdout!r}"
    shown = {"hookEventName": "SubagentStart", "additionalContext": POINTER}
    if answer != {"hookSpecificOutput": shown} or sub.stdout.count("\n") != 1:
        return False, f"subagent start: {sub.stdout!r}"
    stated = re.search(
        r"pointer line, (\d+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    if not stated or int(stated.group(1)) != len(POINTER):
        return False, f"the module document states another size than {len(POINTER)}"
    named = re.search(r"load the skill const-language:([a-z-]+)", POINTER)
    if not named or not (MODULE_ROOT / "skills" / named.group(1) / "SKILL.md").is_file():
        return False, "the line names no folder under skills/"
    return (
        True,
        f"exit 0, the line as typed, {len(POINTER)} characters as the module document states, plain and JSON",
    )


# ---------------------------------------------------------------- the list

ITEMS: list[tuple[int, str, Callable[[], tuple[bool, str]]]] = [
    (1, "L1 typed whole; a plain document green; the ceiling exclusive and a dial", t1),
    (2, "L2 typed whole with the sentence echoed; 25 words pass; the limit a dial; a heading counts", t2),
    (3, "L3 typed whole, case-insensitive; code is code; an exception; a phrase of the repository's", t3),
    (4, "L4 typed whole with the plain word, in any case; an exception; a pair of the repository's", t4),
    (
        5,
        "L5 a note by default, red at error, none at off; the note travels with a block; be in a word none",
        t5,
    ),
    (6, "L6 a Vale comment is red and the rule it names still fires; across lines; code is a mention", t6),
    (
        7,
        "the envelope is blanked; a byte-order mark; no prose; an unterminated envelope is prose;"
        " a closer with trailing whitespace; CRLF; a form feed makes no closer; lone carriage returns",
        t7,
    ),
    (8, "after the write the file on disk is judged; a missing file skips; a Stop event is C12", t8),
    (9, "levels: a rule at warning notes; all off refused; unknown rule and level are C5", t9),
    (10, "this module's C5 lines typed by hand, each exit 1", t10),
    (
        11,
        "vale absent, old, failing, mute, slow or exiting 1: C2 and C12 typed by hand; the fakes asked",
        t11,
    ),
    (
        12,
        "the cap after a write: the first findings that fit in 8,000 characters; the scan lists all",
        t12,
    ),
    (13, "territories: examined against scanned; a negated pattern; a README; the tail's numbers", t13),
    (14, "a value of 12,000 characters echoed by L3 is cut, and the cut is said", t14),
    (15, "golden lines: one document carrying every rule, the whole scan output typed by hand", t15),
    (16, "wiring; description size; manifest; the install note's example accepted", t16),
    (
        17,
        "two runs, one verdict; the founding lists typed whole, disjoint; one finding per phrase, in order",
        t17,
    ),
    (18, "an Edit is judged on what it produces; a line number survives a fence above it", t18),
    (
        19,
        "departures: by pattern, by path, one rule at a time; a stale entry is a note; the hook honours one",
        t19,
    ),
    (
        20,
        "the skill pointer: the line typed whole at session start and as a subagent's context; its size"
        " stated; its skill a folder",
        t20,
    ),
]

SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=Write("docs/notes/ok.md", PLAIN),
    red=Write("docs/notes/bad.md", SIMPLER_RED),
    red_finding=messages.l4_simpler("docs/notes/bad.md", 3, "prior to", "before"),
    green=messages.g1_covered(),
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=False,
    bare_readme=green_hook(),
    judges_envelopes=False,
    outside=messages.g1_skip_not_covered("docs/notes/bad.md"),
    hook_lists_files=False,  # the hook matches the written file by pattern and never lists the tree
    long_value=None,  # L3's echo is the phrase and not the sentence: the cut is proven by item 14
    noted=Write(DOC, PASSIVE),
    note=f"note: {DOC}:3: passive voice — 'was written' — reported, not red, while"
    " const-language.levels.passive is warning",
    pattern_dial=PatternDial("territories", lambda pattern: own(territories=[pattern])),
    skill="plain-language",  # the skill a red names (F10), typed by hand
)


def main() -> int:
    assertions = [Assertion(number, title, check) for number, title, check in ITEMS]
    return H.run_all(CASES, [*assertions, *shared_assertions(SUBJECT, 101)])


if __name__ == "__main__":
    sys.exit(main())
