"""Fixtures of const-doc-budgets: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest and the libraries in the plugin's requirements file; the runner installs
nothing. Every item has a stable number: this module's own items from 1, the items every gate shares
from 101.

Two entry points are driven: the gate, through the shared items and its own, with real hook events —
the platform's PreToolUse payload, which the harness sends and the gate judges on the content it
carries, and PostToolUse payloads, which the plugin wires and the gate judges on the file on disk —
with `--scan`, and with `--scan --since`, the history report; and the session-start printer. The
fixture consumer is the shared one; this module resolves no policy and judges no envelope, so the
shared items about the root policy and about an unreadable envelope are skipped, and it echoes no
value from a document, so the item about a value cut short is skipped too. Every expected line is
typed by hand.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml
from acceptance import broken_first_line, check_case, item
from budgets_gate import messages, start
from budgets_gate.model import Key, characters, rule_of_thumb
from constitution_layer_kit import identity
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import Finding
from consumer import Consumer
from harness import Case, Edit, Harness, Result, Write, event_json
from test_shared_items import PatternDial, Subject, git_patch, git_timeouts, hook_budget

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"
PLUGIN_ROOT = SCRIPTS.parent
MODULE_ROOT = PLUGIN_ROOT.parent

identity.declare(start.GATE)  # the shared texts the items compare are built for this gate's name
H = Harness(SCRIPTS, "check-budgets.sh", "check-budgets.py", start.GATE.namespace)
SESSION = Harness(SCRIPTS, "session-start.sh", "session-start.py", start.GATE.namespace)
NAMESPACE = start.GATE.namespace
SKILL = PLUGIN_ROOT / "skills" / "set-ceilings" / "SKILL.md"
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
HOOKS = PLUGIN_ROOT / "hooks" / "hooks.json"

NOTES: dict[str, object] = {  # the fixtures' one ceiling: 100 characters over docs/notes, 31 days of data
    "name": "notes",
    "paths": ["docs/notes/**"],
    "max": 100,
    "level": "error",
    "window": {"from": "2026-08-01", "to": "2026-09-01"},
}
WHY = (
    "a document longer than its kind was observed to need makes every reader, and every session that loads"
    " it, pay for text the kind did not need"
)


def b1(rel: str, length: str, excess: str, most: str = "100", name: str = "notes") -> Finding:
    """B1, typed by hand once, its numbers and names filled in as the gate prints them."""
    return Finding(
        Key.B1,
        f"{rel}: {length} characters, over the ceiling '{name}' of {most} by {excess}",
        WHY,
        f"shorten it by {excess} characters or more, or split it into documents that each stay at or"
        f" under {most}; the ceiling for this repository is the entry '{name}' of const-doc-budgets.ceilings"
        " in constitution.yaml; for a document that must stand as written, declare the departure with its"
        " reason: add to const-doc-budgets.departures an entry {paths: [<the file, or a pattern of the"
        f" documents that stand>], allow: [{name}], reason: <why they stand, in one line>}}",
    )


# a file name of over 80 characters holding a line break and a backslash: the real name, and the line the
# gate shows for it, typed by hand — the whole name, since a path is what the reader opens
WEIRD = "docs/notes/w\nx\\y" + "z" * 80 + ".md"
WEIRD_SHOWN = "docs/notes/w\\nx\\\\y" + "z" * 80 + ".md"
WEIRD_OTHER = "docs/other/w\nx\\y" + "z" * 80 + ".md"
WEIRD_OTHER_SHOWN = "docs/other/w\\nx\\\\y" + "z" * 80 + ".md"
WEIRD_DIR = "w\nx\\y" + "d" * 80  # a folder name, for a root and a clone
WEIRD_DIR_SHOWN = "w\\nx\\\\y" + "d" * 80


def doc(length: int, letter: str = "a") -> str:
    """A document of `length` characters, counted as the project's conventions count: a heading line,
    a blank line, one line of the letter. The expected numbers beside it are typed by hand."""
    return "# T\n\n" + letter * (length - 6) + "\n"


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps it working: the one ceiling, unless replaced."""
    return {NAMESPACE: {"ceilings": [NOTES], **dials}}


def claim(territory: Sequence[str]) -> dict[str, object]:
    return own(ceilings=[{**NOTES, "paths": list(territory)}])


def dials_text(patch: dict[str, object] | None = None) -> str:
    return yaml.safe_dump({**Consumer(Path()).dials, **own(), **(patch or {})}, sort_keys=False)


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


def scan(root: Path, *args: str) -> Result:
    return H.run_gate("", args=["--scan", str(root), *args])


def context(result: Result) -> Result:
    """A green hook run with notes answers with one JSON object: what it hands the model, as stdout;
    any other run as it is. The object's shape is the shared item's to prove."""
    try:
        answer = json.loads(result.stdout)
    except json.JSONDecodeError:
        return result
    said = answer.get("hookSpecificOutput", {}).get("additionalContext") if isinstance(answer, dict) else None
    return Result(result.code, said, result.stderr) if isinstance(said, str) else result


def broken(result: Result, line: str) -> None:
    broken_first_line(result, line)
    first = f"exit 1, first stderr line: {line}"
    assert shared.c11_broken_count() in result.stderr, f"no count line after: {first}"


def exactly(result: Result, code: int, stdout: str, stderr: str = "") -> None:
    ok = result.code == code and result.stdout == stdout and result.stderr == stderr
    assert ok, f"wanted exit {code} and\n{stdout}{stderr}\ngot {result.code}:\n{result.stdout}{result.stderr}"


def green(what: str) -> str:
    return f"GREEN: const-doc-budgets: 1 document examined, {what}\n"


# the line after every red, naming the skill that teaches the rule and its fix (F10), typed by hand
POINTER = (
    "const-doc-budgets: load the skill const-doc-budgets:set-ceilings before you fix this — it teaches the"
    " rule and the fix\n"
)


def block(finding: Finding, rel: str) -> str:
    return f"{finding.render()}\nRED: 1 finding(s) — 1 document examined ({rel})\n{POINTER}"


# ---------------------------------------------------------------- red→green cases

SETUP = [Write("constitution.yaml", dials_text())]
EDITED = "docs/notes/e.md"
CRLF_GREEN = "# T\r\n\r\n" + "a" * 94 + "\r\n"  # 103 code points, three of them CR: 100 characters
CRLF_RED = "# T\r\n\r\n" + "a" * 95 + "\r\n"  # 101 characters

CASES = [
    Case(
        1,
        "B1: over the ceiling at level error is red; at exactly the ceiling, green",
        Write("docs/notes/c.md", doc(101)),
        Write("docs/notes/c.md", doc(100)),
        b1("docs/notes/c.md", "101", "1"),
        "100 characters against the ceiling 'notes' of 100",
        SETUP,
    ),
    Case(
        2,
        "a CRLF is one character: 100 with three CRLFs is green, 101 red",
        Write("docs/notes/c.md", CRLF_RED),
        Write("docs/notes/c.md", CRLF_GREEN),
        b1("docs/notes/c.md", "101", "1"),
        "100 characters against the ceiling 'notes' of 100",
        SETUP,
    ),
    Case(
        3,
        "a character is a code point, not a byte: 100 Cyrillic characters, 195 bytes, green",
        Write("docs/notes/c.md", doc(101, "я")),
        Write("docs/notes/c.md", doc(100, "я")),
        b1("docs/notes/c.md", "101", "1"),
        "100 characters against the ceiling 'notes' of 100",
        SETUP,
    ),
    Case(
        4,
        "an Edit is judged on the document it produces",
        Edit(EDITED, "# T", "# T" + "b" * 11),
        Edit(EDITED, "# T", "# T" + "b" * 10),
        b1(EDITED, "101", "1"),
        "100 characters against the ceiling 'notes' of 100",
        [*SETUP, Write(EDITED, doc(90))],
    ),
]


@pytest.mark.parametrize(
    "case", [pytest.param(case, id=f"T{case.number}", marks=item(case.number, case.title)) for case in CASES]
)
def test_case(case: Case) -> None:
    check_case(H, case)


# ---------------------------------------------------------------- this module's own items

GUIDE: dict[str, object] = {
    "name": "guide",
    "paths": ["/docs/guide.md"],
    "max": 50,
    "level": "warning",
    "window": {"from": "2026-09-01", "to": "2026-09-02"},
}


@item(5, "a ceiling at warning: the excess is a note handed to the model with the green line")
def test_t5() -> None:
    """A ceiling at warning: an excess is a note that reaches the model with the green line, exit 0;
    under the ceiling, the green line alone."""
    two = own(ceilings=[NOTES, GUIDE])
    over, _ = gate_on(Write("docs/guide.md", doc(60)), two)
    under, _ = gate_on(Write("docs/guide.md", doc(50)), two)
    note = (
        "note: docs/guide.md: 60 characters, over the ceiling 'guide' of 50 by 10 — reported, not red, while"
        " the ceiling's level is warning; shorten it or split it before the ceiling blocks"
    )
    long_over, _ = gate_on(Write(WEIRD, doc(160)), own(ceilings=[{**NOTES, "level": "warning"}]))
    long_note = (  # the path whole, its break and backslash escaped, though it is over 80 characters
        "note: " + WEIRD_SHOWN + ": 160 characters, over the ceiling 'notes' of 100 by 60 — reported, not"
        " red, while the ceiling's level is warning; shorten it or split it before the ceiling blocks"
    )
    exactly(context(over), 0, note + "\n" + green("60 characters against the ceiling 'guide' of 50").rstrip())
    exactly(under, 0, green("50 characters against the ceiling 'guide' of 50"))
    exactly(
        context(long_over),
        0,
        long_note + "\n" + green("160 characters against the ceiling 'notes' of 100").rstrip(),
    )


@item(6, "PostToolUse, the plugin's wiring: the file on disk is measured")
def test_t6() -> None:
    """PostToolUse, the plugin's wiring: the file on disk is measured, CRLF and all."""
    red_root = prepared(files={"docs/notes/c.md": doc(120)})
    green_root = prepared(files={"docs/notes/c.md": CRLF_GREEN})
    finding = b1("docs/notes/c.md", "120", "20")
    weird_root = prepared(files={WEIRD: doc(120)})
    weird = b1(WEIRD_SHOWN, "120", "20")  # the path whole and escaped, in the headline and the count line
    exactly(after_write(red_root, "docs/notes/c.md"), 2, "", block(finding, "docs/notes/c.md"))
    exactly(after_write(weird_root, WEIRD), 2, "", block(weird, WEIRD_SHOWN))
    exactly(
        after_write(green_root, "docs/notes/c.md"),
        0,
        green("100 characters against the ceiling 'notes' of 100"),
    )


@item(7, "departures: a lifted document passes and the entry is named; only named ceilings lift; C5")
def test_t7() -> None:
    """Departures: a document lifted from its ceiling is measured and passes, the entry named; a
    departure lifts only the ceilings it names; an entry naming no ceiling is a configuration failure."""
    lift = {"paths": ["docs/notes/frozen-*.md"], "allow": ["notes"], "reason": "accepted before the ceiling"}
    lifted, _ = gate_on(Write("docs/notes/frozen-1.md", doc(300)), own(departures=[lift]))
    other = {**lift, "allow": ["guide"]}
    held, _ = gate_on(
        Write("docs/notes/frozen-1.md", doc(300)), own(ceilings=[NOTES, GUIDE], departures=[other])
    )
    unknown, _ = gate_on(Write("docs/notes/a.md", doc(10)), own(departures=[{**lift, "allow": ["nowhere"]}]))
    exactly(
        lifted,
        0,
        green("300 characters; the ceiling 'notes' is lifted by const-doc-budgets.departures entry 1"),
    )
    exactly(held, 2, "", block(b1("docs/notes/frozen-1.md", "300", "200"), "docs/notes/frozen-1.md"))
    broken(
        unknown,
        "BROKEN: constitution.yaml: const-doc-budgets.departures entry 1: 'nowhere' names no ceiling —"
        " fix: write the entry as paths: [<patterns>], allow: [<ceiling names>], reason: <one line"
        " saying why these documents stand as written>; the ceilings are named in"
        " const-doc-budgets.ceilings: notes",
    )


OVERLAP_HEAD = "BROKEN: constitution.yaml: const-doc-budgets.ceilings 'notes' and 'wide' both hold "
OVERLAP_FIX = (
    " — fix: a document is held to one ceiling at most, so that its number never depends on the order of the"
    " list: narrow one entry's paths, or take the file out of one with a negated pattern; a document that"
    " must stand over its ceiling takes a departure"
)
OVERLAP = OVERLAP_HEAD + "docs/notes/a.md" + OVERLAP_FIX


@item(8, "two ceilings holding one document: C5 in the hook and in the scan; a negated pattern parts them")
def test_t8() -> None:
    """Two ceilings holding one document: a configuration failure in the hook for the written file and
    in the scan for the first such file; one taken out by a negated pattern holds nothing twice."""
    wide = {**NOTES, "name": "wide", "paths": ["docs/**"], "max": 500}
    both = own(ceilings=[NOTES, wide])
    hook, _ = gate_on(Write("docs/notes/a.md", doc(10)), both)
    root = prepared(both, files={"docs/notes/a.md": doc(10), "docs/notes/b.md": doc(10)})
    carved = {
        **wide,
        "paths": ["docs/**/*.md", "!docs/notes/*.md"],
    }  # file patterns, so the negation takes the files out
    fine, _ = gate_on(Write("docs/notes/a.md", doc(10)), own(ceilings=[NOTES, carved]))
    outside, _ = gate_on(Write("docs/policies/x.md", doc(10)), both)  # held by `wide` alone
    weird, _ = gate_on(Write(WEIRD, doc(10)), both)
    broken(hook, OVERLAP)
    # the path whole, escaped, not cut at 80
    broken(weird, OVERLAP_HEAD + WEIRD_SHOWN + OVERLAP_FIX)
    broken(scan(root), OVERLAP)
    exactly(fine, 0, green("10 characters against the ceiling 'notes' of 100"))
    exactly(outside, 0, green("10 characters against the ceiling 'wide' of 500"))


@item(9, "the month rule: error on 29 days is C5, on 30 days green; warning on any window")
def test_t9() -> None:
    """The month rule, a check of the dials alone: level error on a window of 29 days is a
    configuration failure; 30 days is enough; level warning takes any window."""
    short = {**NOTES, "window": {"from": "2026-08-01", "to": "2026-08-30"}}
    thirty = {**NOTES, "window": {"from": "2026-08-01", "to": "2026-08-31"}}
    one_day = {**NOTES, "level": "warning", "window": {"from": "2026-08-01", "to": "2026-08-01"}}
    refused, _ = gate_on(Write("docs/notes/a.md", doc(10)), own(ceilings=[short]))
    root = prepared(own(ceilings=[short]))
    at_thirty, _ = gate_on(Write("docs/notes/a.md", doc(10)), own(ceilings=[thirty]))
    warned, _ = gate_on(Write("docs/notes/a.md", doc(10)), own(ceilings=[one_day]))
    line = (
        "BROKEN: constitution.yaml: const-doc-budgets.ceilings 'notes' is at level error on a window whose"
        " span"
        " is 29 day(s), 2026-08-01 to 2026-08-30 — fix: a ceiling blocks only on 30 days of observed data"
        " or more:"
        " set its level to warning until window.to is 30 days or more after window.from — the report --scan"
        " --since <YYYY-MM-DD> prints the data of those days"
    )
    broken(refused, line)
    broken(scan(root), line)
    exactly(at_thirty, 0, green("10 characters against the ceiling 'notes' of 100"))
    exactly(warned, 0, green("10 characters against the ceiling 'notes' of 100"))


C5 = "BROKEN: constitution.yaml: const-doc-budgets."
LIFT: dict[str, object] = {"paths": ["docs/notes/**"], "allow": ["notes"], "reason": "stands"}
DEP_FIX = (
    " — fix: write the entry as paths: [<patterns>], allow: [<ceiling names>], reason: <one line saying why"
    " these documents stand as written>; the ceilings are named in const-doc-budgets.ceilings: notes"
)
ENTRY_FIX = (
    " — fix: write the entry as name: <kebab-case>, paths: [<patterns>], max: <characters>, level: warning or"
    " error, window: {from: <YYYY-MM-DD>, to: <YYYY-MM-DD>}, the days of data the number was set from"
)


@item(10, "this module's C5 lines typed by hand, each exit 1 with the count line")
def test_t10() -> None:
    """This module's dial failures typed by hand, each exit 1 with the count line after it."""
    pairs: list[tuple[dict[str, object], str]] = [
        (
            own(budget=1),
            C5 + "budget is no dial of this module — fix: a misspelt dial would be ignored in silence, so"
            " none is: write one of severity, log_dir, ceilings, departures",
        ),
        (
            own(**{"bad\nkey": 1}),
            C5 + "bad\\nkey is no dial of this module — fix: a misspelt dial would be ignored in silence, so"
            " none is: write one of severity, log_dir, ceilings, departures",
        ),
        (
            own(ceilings=[{**NOTES, "a\nb": 3}]),
            C5 + "ceilings entry 1: 'a\\nb' is no field of an entry" + ENTRY_FIX,
        ),
        (
            own(departures=[{**LIFT, "a\nb": 3}]),
            C5 + "departures entry 1: 'a\\nb' is no field of an entry" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "allow": ["x\ny"]}]),
            C5 + "departures entry 1: 'x\\ny' names no ceiling" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "reason": "one\ntwo\n"}]),
            C5 + "departures entry 1: reason must be one non-empty line saying why" + DEP_FIX,
        ),
        (
            own(ceilings={"notes": 1}),
            C5 + 'ceilings must be a list of entries — fix: write one entry per "- " item with the fields'
            " name, paths, max, level and window; leave the key out, or write [], for no ceiling",
        ),
        (own(ceilings=["notes"]), C5 + "ceilings entry 1: it is not a mapping" + ENTRY_FIX),
        (
            own(ceilings=[{**NOTES, "limit": 3}]),
            C5 + "ceilings entry 1: 'limit' is no field of an entry" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "name": "Notes"}]),
            C5 + "ceilings entry 1: name must be a kebab-case name, such as records" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "paths": []}]),
            C5 + "ceilings entry 1: paths must be a non-empty list of path patterns" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "paths": ["#docs/**"]}]),
            C5 + "ceilings entry 1 paths holds a pattern git would not read as one: '#docs/**' — fix: a"
            " pattern may not start with '#' (a comment to git) nor contain a line break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break",
        ),
        (
            own(ceilings=[{**NOTES, "max": 0}]),
            C5 + "ceilings entry 1: max must be a whole number of characters, 1 or more" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "max": True}]),
            C5 + "ceilings entry 1: max must be a whole number of characters, 1 or more" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "max": "100"}]),
            C5 + "ceilings entry 1: max must be a whole number of characters, 1 or more" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "level": "off"}]),
            C5 + "ceilings entry 1: level must be warning or error" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "window": {"from": "2026-08-01"}}]),
            C5 + "ceilings entry 1: window must be a mapping of exactly from and to, each a date written"
            " YYYY-MM-DD" + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "window": {"from": "2026-8-1", "to": "2026-09-01"}}]),
            C5
            + "ceilings entry 1: window.from and window.to must each be a date written YYYY-MM-DD"
            + ENTRY_FIX,
        ),
        (
            own(ceilings=[{**NOTES, "window": {"from": "2026-09-02", "to": "2026-09-01"}}]),
            C5 + "ceilings entry 1: window.to 2026-09-01 is before window.from 2026-09-02" + ENTRY_FIX,
        ),
        (
            own(ceilings=[NOTES, NOTES]),
            C5 + "ceilings names 'notes' twice — fix: a departure lifts a ceiling by its name, so each name"
            " is one entry's: rename one of the two",
        ),
        (
            own(departures={"paths": 1}),
            C5 + 'departures must be a list of entries — fix: write one entry per "- " item with the fields'
            " paths (a list of patterns), allow (a list of ceiling names) and reason (one line); leave the"
            " key out, or write [], for no departure",
        ),
        (
            own(departures=["docs/notes/**"]),
            C5 + "departures entry 1: it is not a mapping" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "why": "x"}]),
            C5 + "departures entry 1: 'why' is no field of an entry" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "paths": []}]),
            C5 + "departures entry 1: paths must be a non-empty list of path patterns" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "allow": []}]),
            C5 + "departures entry 1: allow must be a non-empty list of ceiling names" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "reason": "one\ntwo"}]),
            C5 + "departures entry 1: reason must be one non-empty line saying why" + DEP_FIX,
        ),
        (
            own(departures=[{**LIFT, "paths": ["#docs/**"]}]),
            C5 + "departures entry 1 paths holds a pattern git would not read as one: '#docs/**' — fix: a"
            " pattern may not start with '#' (a comment to git) nor contain a line break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break",
        ),
        (
            own(departures=[{"paths": ["docs/notes/**"], "allow": ["notes"], "reason": ""}]),
            C5 + "departures entry 1: reason must be one non-empty line saying why — fix: write the entry as"
            " paths: [<patterns>], allow: [<ceiling names>], reason: <one line saying why these documents"
            " stand as written>; the ceilings are named in const-doc-budgets.ceilings: notes",
        ),
    ]
    for patch, line in pairs:
        broken(gate_on(Write("docs/notes/a.md", doc(10)), patch)[0], line)
    block_scalar = own(departures=[{**LIFT, "reason": "stands\n"}])  # what `reason: |` gives: trimmed, taken
    trimmed, _ = gate_on(Write("docs/notes/a.md", doc(10)), block_scalar)
    exactly(
        trimmed,
        0,
        green("10 characters; the ceiling 'notes' is lifted by const-doc-budgets.departures entry 1"),
    )


@item(11, "window dates unquoted and quoted are taken; a timestamp is refused")
def test_t11() -> None:
    """Dates as YAML reads them unquoted, date objects, and quoted, strings, are both taken; a
    timestamp is no date."""
    base = yaml.safe_dump({**Consumer(Path()).dials}, sort_keys=False)

    def raw(start: str, end: str) -> str:
        return base + (
            'const-doc-budgets:\n  ceilings:\n    - name: notes\n      paths:\n        - "docs/notes/**"\n'
            f"      max: 100\n      level: error\n      window:\n        from: {start}\n        to: {end}\n"
        )

    unquoted, _ = gate_on(Write("docs/notes/a.md", doc(10)), raw_dials=raw("2026-08-01", "2026-09-01"))
    quoted, _ = gate_on(Write("docs/notes/a.md", doc(10)), raw_dials=raw("'2026-08-01'", "'2026-09-01'"))
    stamp, _ = gate_on(Write("docs/notes/a.md", doc(10)), raw_dials=raw("2026-08-01 10:00:00", "2026-09-01"))
    ok = green("10 characters against the ceiling 'notes' of 100")
    exactly(unquoted, 0, ok)
    exactly(quoted, 0, ok)
    broken(
        stamp,
        C5 + "ceilings entry 1: window.from and window.to must each be a date written YYYY-MM-DD" + ENTRY_FIX,
    )


@item(12, "no ceiling, the default: a visible skip in the hook, a zero in the scan; a file under none")
def test_t12() -> None:
    """No ceiling — the dial empty or absent, the default: the hook skips and says why, the scan
    measures nothing and says so; a document under no ceiling is a visible skip."""
    empty, _ = gate_on(Write("docs/notes/a.md", doc(500)), {NAMESPACE: {"ceilings": []}})
    absent, _ = gate_on(Write("docs/notes/a.md", doc(500)), {NAMESPACE: {}})
    outside, _ = gate_on(Write("README.md", doc(500)))
    root = prepared({NAMESPACE: {}}, files={"docs/notes/a.md": doc(500)})
    skip = "GREEN: const-doc-budgets: 0 documents examined — no ceiling is set (const-doc-budgets.ceilings)\n"
    weird_outside, _ = gate_on(Write(WEIRD_OTHER, doc(500)))
    exactly(
        weird_outside,
        0,
        "GREEN: const-doc-budgets: 0 documents examined — " + WEIRD_OTHER_SHOWN + " is under no ceiling"
        " (const-doc-budgets.ceilings)\n",
    )
    exactly(empty, 0, skip)
    exactly(absent, 0, skip)
    exactly(
        outside,
        0,
        "GREEN: const-doc-budgets: 0 documents examined — README.md is under no ceiling"
        " (const-doc-budgets.ceilings)\n",
    )
    exactly(
        scan(root),
        0,
        "GREEN: const-doc-budgets: 0 document(s) measured under 0 ceiling(s) and 0 departure(s), 4"
        " Markdown file(s) scanned\n",
    )


@item(13, "golden scan: stale departure, one note per ceiling, a warning, a finding, the count line")
def test_t13() -> None:
    """The scan, golden: a stale departure, one note per ceiling — a departure lifting one document, a
    ceiling holding nothing — a warning, a finding, the count line, each typed whole."""
    empty = {**GUIDE, "name": "empty", "paths": ["/docs/none/**"]}
    lift = {"paths": ["docs/notes/frozen-*.md"], "allow": ["notes"], "reason": "accepted before the ceiling"}
    stale = {"paths": ["docs/gone/**"], "allow": ["guide"], "reason": "moved away"}
    elsewhere = {"paths": ["/docs/guide.md"], "allow": ["notes"], "reason": "names the wrong ceiling"}
    root = prepared(
        own(ceilings=[NOTES, GUIDE, empty], departures=[lift, stale, elsewhere]),
        files={
            "docs/notes/a.md": doc(90),
            "docs/notes/b.md": doc(120),
            "docs/notes/frozen-1.md": doc(300),
            "docs/guide.md": doc(60),
            "README.md": doc(1000),
        },
    )
    finding = b1("docs/notes/b.md", "120", "20")
    wanted = (
        "note: const-doc-budgets.departures entry 2 (docs/gone/**) lifts nothing: it matches no document a"
        " ceiling it names holds; the documents were deleted or moved, or the pattern or the names are"
        " wrong\n"
        "note: const-doc-budgets.departures entry 3 (/docs/guide.md) lifts nothing: it matches no document a"
        " ceiling it names holds; the documents were deleted or moved, or the pattern or the names are"
        " wrong\n"
        "note: ceiling 'notes' — 100 characters, error, window 2026-08-01 to 2026-09-01: 3 document(s), 1"
        " lifted by a departure, the longest of the others docs/notes/b.md at 120, over by 20\n"
        "note: ceiling 'guide' — 50 characters, warning, window 2026-09-01 to 2026-09-02: 1 document(s), the"
        " longest docs/guide.md at 60, over by 10\n"
        "note: ceiling 'empty' — 50 characters, warning, window 2026-09-01 to 2026-09-02: no document\n"
        "note: docs/guide.md: 60 characters, over the ceiling 'guide' of 50 by 10 — reported, not red, while"
        " the ceiling's level is warning; shorten it or split it before the ceiling blocks\n"
        f"{finding.render()}\n"
        "RED: 1 finding(s) — 4 document(s) measured under 3 ceiling(s) and 3 departure(s), 8 Markdown file(s)"
        " scanned\n"
        f"{POINTER}"
    )
    long_pattern = "docs\\gone/" + "p" * 100  # 110 characters with a backslash: a pattern only points
    cut = prepared(
        own(departures=[{"paths": [long_pattern], "allow": ["notes"], "reason": "moved away"}]),
    )
    cut_wanted = (
        "note: const-doc-budgets.departures entry 1 (docs\\\\gone/" + "p" * 70 + "… [110 characters]) lifts"
        " nothing: it matches no document a ceiling it names holds; the documents were deleted or moved, or"
        " the pattern or the names are wrong\n"
        "note: ceiling 'notes' — 100 characters, error, window 2026-08-01 to 2026-09-01: no document\n"
        "GREEN: const-doc-budgets: 0 document(s) measured under 1 ceiling(s) and 1 departure(s), 3 Markdown"
        " file(s) scanned\n"
    )
    exactly(scan(root), 2, wanted)
    exactly(scan(cut), 0, cut_wanted)


@dataclass(frozen=True)
class Link:
    """A symbolic link a commit holds, its target written as git stores it."""

    target: str


def fake_gpg(root: Path) -> Path:
    """Signs every later commit of the repository through a fake `gpg.program` and turns
    `log.showSignature` on; the fake logs each call to the returned file and, to verify, says its
    human text on stderr as gpg does, which git log prints before the formatted line."""
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
    return log


def history_repo(dates: Sequence[tuple[str, dict[str, str | Link | None]]], signed: bool = False) -> Path:
    """A repository whose first-parent line is the given commits, each at its date: {path: text}, a
    `Link` making the path a symbolic link, None deleting the file. No other commit, so the report's
    numbers depend on nothing else. `signed`: every commit is signed through a fake `gpg.program`, and
    the repository's own `git log` prints the signature check with `log.showSignature` on."""
    root = H.scratch_dir()
    consumer = Consumer(root)
    consumer.write("constitution.yaml", dials_text())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    if signed:
        fake_gpg(root)
    for stamp, files in dates:
        for rel, text in files.items():
            if text is None:
                (root / rel).unlink()
            elif isinstance(text, Link):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                os.symlink(text.target, root / rel)
            else:
                consumer.write(rel, text)
        env = {**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
        subprocess.run(
            ["git", "-c", "user.name=f", "-c", "user.email=f@example.invalid", "commit", "-qm", "c"],
            cwd=root,
            check=True,
            env=env,
        )
    return root


HISTORY: list[tuple[str, dict[str, str | Link | None]]] = [
    ("2026-08-10T10:00:00+0000", {"docs/notes/a.md": doc(50)}),
    ("2026-08-11T09:00:00+0000", {"docs/notes/a.md": doc(80)}),
    ("2026-08-11T17:00:00+0000", {"docs/notes/a.md": doc(60), "docs/notes/b.md": doc(70)}),
    ("2026-08-12T10:00:00+0000", {"docs/notes/b.md": None}),
]


@item(14, "golden history report: per day, the window, the rule of thumb; a date with no commit")
def test_t14() -> None:
    """The history report, golden: per day the documents at its last commit and the longest version any
    commit of the day held, the state before the window read from the last commit before it; the window
    from the first day with data, its longest and the rule of thumb; exit 0, nothing judged."""
    root = history_repo(HISTORY)
    wanted = (
        "2026-08-11 notes: 2 document(s) at the day's last commit, the longest of the day docs/notes/a.md at"
        " 80\n"
        "2026-08-12 notes: 1 document(s) at the day's last commit, the longest of the day docs/notes/a.md at"
        " 60\n"
        "window notes: 2026-08-11 to 2026-08-12, a span of 1 day(s), the longest docs/notes/a.md at 80; plus"
        " 10 % rounded up to 1,000: 1,000; set now: 100\n"
        "const-doc-budgets: history since 2026-08-11 — 4 commit(s) of the first-parent line read, 2 day(s)"
        " with data, 1 ceiling(s); a report, nothing judged\n"
    )
    before = (  # --since before the first commit: the window opens on the first day with data
        "2026-08-10 notes: 1 document(s) at the day's last commit, the longest of the day docs/notes/a.md at"
        " 50\n"
        "2026-08-11 notes: 2 document(s) at the day's last commit, the longest of the day docs/notes/a.md at"
        " 80\n"
        "2026-08-12 notes: 1 document(s) at the day's last commit, the longest of the day docs/notes/a.md at"
        " 60\n"
        "window notes: 2026-08-10 to 2026-08-12, a span of 2 day(s), the longest docs/notes/a.md at 80; plus"
        " 10 % rounded up to 1,000: 1,000; set now: 100\n"
        "const-doc-budgets: history since 2026-08-01 — 4 commit(s) of the first-parent line read, 3 day(s)"
        " with data, 1 ceiling(s); a report, nothing judged\n"
    )
    after = (  # --since after the last commit: the state in force, from the last commit before it
        "2026-08-13 notes: 1 document(s) at the day's last commit, the longest of the day docs/notes/a.md at"
        " 60\n"
        "window notes: 2026-08-13 to 2026-08-13, a span of 0 day(s), the longest docs/notes/a.md at 60; plus"
        " 10 % rounded up to 1,000: 1,000; set now: 100\n"
        "const-doc-budgets: history since 2026-08-13 — 1 commit(s) of the first-parent line read, 1 day(s)"
        " with data, 1 ceiling(s); a report, nothing judged\n"
    )
    weird = history_repo([("2026-08-20T09:00:00+0000", {WEIRD: doc(50)})])
    weird_wanted = (  # the longest document's path whole, escaped, in the day line and the window line
        "2026-08-20 notes: 1 document(s) at the day's last commit, the longest of the day "
        + WEIRD_SHOWN
        + " at"
        " 50\n"
        "window notes: 2026-08-20 to 2026-08-20, a span of 0 day(s), the longest " + WEIRD_SHOWN + " at 50;"
        " plus 10 % rounded up to 1,000: 1,000; set now: 100\n"
        "const-doc-budgets: history since 2026-08-20 — 1 commit(s) of the first-parent line read, 1 day(s)"
        " with data, 1 ceiling(s); a report, nothing judged\n"
    )
    signed = history_repo(HISTORY, signed=True)  # the same history, signed, `log.showSignature` on
    shown = subprocess.run(
        ["git", "log", "-1", "--format=%h"], cwd=signed, capture_output=True, text=True, check=False
    )
    printed = "fake signer" in shown.stdout + shown.stderr  # so the case cannot pass for want of a check
    assert printed, f"git log did not print the check: {shown.stdout}{shown.stderr}"
    exactly(scan(signed, "--since", "2026-08-11"), 0, wanted)
    exactly(scan(weird, "--since", "2026-08-20"), 0, weird_wanted)
    exactly(scan(root, "--since", "2026-08-11"), 0, wanted)
    exactly(scan(root, "--since", "2026-08-01"), 0, before)
    exactly(scan(root, "--since", "2026-08-13"), 0, after)


@item(22, "report: a day whose last commit holds none, no document at all, no commit, git failing")
def test_t22() -> None:
    """The report's other lines: a day whose last commit holds no document while an earlier commit did;
    a day and a window with no document at all; a repository with no commit; git failing inside it."""
    gone = history_repo(
        [
            ("2026-08-20T09:00:00+0000", {"docs/notes/x.md": doc(50)}),
            ("2026-08-20T17:00:00+0000", {"docs/notes/x.md": None}),
        ]
    )
    empty = history_repo([("2026-08-20T09:00:00+0000", {"docs/other.md": doc(50)})])
    fresh = H.scratch_dir()
    Consumer(fresh).write("constitution.yaml", dials_text())
    subprocess.run(["git", "init", "-q"], cwd=fresh, check=True)
    fake = H.scratch_dir()
    real = shutil.which("git") or "git"
    (fake / "git").write_text(
        "#!/bin/sh\n"
        'for a in "$@"; do if [ "$a" = log ]; then echo "fatal: simulated failure" >&2; exit 128; fi; done\n'
        f"exec '{real}' \"$@\"\n",
        encoding="utf-8",
    )
    (fake / "git").chmod(0o755)
    failing = H.run_gate(
        "", args=["--scan", str(gone), "--since", "2026-08-20"], env={"PATH": f"{fake}:{os.environ['PATH']}"}
    )
    odd = H.scratch_dir()  # git's diagnosis holds a backslash and runs over 80 characters
    (odd / "git").write_text(
        "#!/bin/sh\n"
        'for a in "$@"; do if [ "$a" = log ]; then printf \'%s\\n\' "fatal: a\\b '
        + "w"
        * 90
        + '" >&2; exit 128; fi;'
        " done\n"
        f"exec '{real}' \"$@\"\n",
        encoding="utf-8",
    )
    (odd / "git").chmod(0o755)
    failing_odd = H.run_gate(
        "", args=["--scan", str(gone), "--since", "2026-08-20"], env={"PATH": f"{odd}:{os.environ['PATH']}"}
    )
    exactly(
        scan(gone, "--since", "2026-08-20"),
        0,
        "2026-08-20 notes: 0 document(s) at the day's last commit, the longest of the day docs/notes/x.md"
        " at 50\n"
        "window notes: 2026-08-20 to 2026-08-20, a span of 0 day(s), the longest docs/notes/x.md at 50;"
        " plus"
        " 10 % rounded up to 1,000: 1,000; set now: 100\n"
        "const-doc-budgets: history since 2026-08-20 — 2 commit(s) of the first-parent line read, 1"
        " day(s)"
        " with data, 1 ceiling(s); a report, nothing judged\n",
    )
    exactly(
        scan(empty, "--since", "2026-08-20"),
        0,
        "2026-08-20 notes: no document\n"
        "window notes: 2026-08-20 to 2026-08-20, a span of 0 day(s), no document\n"
        "const-doc-budgets: history since 2026-08-20 — 1 commit(s) of the first-parent line read, 1"
        " day(s)"
        " with data, 1 ceiling(s); a report, nothing judged\n",
    )
    exactly(
        scan(fresh, "--since", "2026-08-20"),
        0,
        "const-doc-budgets: history since 2026-08-20 — no commit on the first-parent line; a report,"
        " nothing judged\n",
    )
    broken(
        failing,
        "BROKEN: git could not read the history: fatal: simulated failure — fix: repair what git names in"
        " the message, then check by hand: git log --first-parent -1",
    )
    broken(  # the diagnosis whole: its backslash doubled, none of its 90 letters cut
        failing_odd,
        "BROKEN: git could not read the history: fatal: a\\\\b " + "w" * 90 + " — fix: repair what git"
        " names in the message, then check by hand: git log --first-parent -1",
    )


@item(23, "scan margins: at the ceiling, all lifted, a tie named in path order, two departures on one file")
def test_t23() -> None:
    """The scan's other margins: a document at exactly its ceiling is green with nothing to spare; a
    ceiling whose documents are all lifted says so; two documents of one length name the first in path
    order, in the scan and in the report alike; two departures lifting one document name the first."""
    frozen = {**GUIDE, "name": "frozen", "paths": ["/docs/frozen/**"]}
    lift_frozen = {"paths": ["docs/frozen/**"], "allow": ["frozen"], "reason": "stands"}
    root = prepared(
        own(ceilings=[NOTES, frozen], departures=[lift_frozen]),
        files={"docs/notes/b.md": doc(100), "docs/notes/a.md": doc(100), "docs/frozen/x.md": doc(900)},
    )
    wanted = (
        "note: ceiling 'notes' — 100 characters, error, window 2026-08-01 to 2026-09-01: 2 document(s), the"
        " longest docs/notes/a.md at 100, 0 to spare\n"
        "note: ceiling 'frozen' — 50 characters, warning, window 2026-09-01 to 2026-09-02: 1 document(s), all"
        " lifted by a departure\n"
        "GREEN: const-doc-budgets: 3 document(s) measured under 2 ceiling(s) and 1 departure(s), 6 Markdown"
        " file(s) scanned\n"
    )
    tie = history_repo(
        [("2026-08-20T09:00:00+0000", {"docs/notes/b.md": doc(70), "docs/notes/a.md": doc(70)})]
    )
    second = {"paths": ["docs/notes/frozen-*.md"], "allow": ["notes"], "reason": "the second entry"}
    first = {**second, "paths": ["docs/notes/*.md"], "reason": "the first entry"}
    twice, _ = gate_on(Write("docs/notes/frozen-1.md", doc(300)), own(departures=[first, second]))
    longest = prepared(files={WEIRD: doc(90)})
    lifted = prepared(
        own(departures=[{"paths": ["docs/notes/frozen-*.md"], "allow": ["notes"], "reason": "stands"}]),
        files={WEIRD: doc(90), "docs/notes/frozen-1.md": doc(300)},
    )
    exactly(  # with a document lifted, the longest of the others is named whole and escaped too
        scan(lifted),
        0,
        "note: ceiling 'notes' — 100 characters, error, window 2026-08-01 to 2026-09-01: 2 document(s),"
        " 1 lifted by a departure, the longest of the others " + WEIRD_SHOWN + " at 90, 10 to spare\n"
        "GREEN: const-doc-budgets: 2 document(s) measured under 1 ceiling(s) and 1 departure(s), 5"
        " Markdown file(s) scanned\n",
    )
    exactly(  # the longest document's path whole in the ceiling's note, escaped, over 80 characters
        scan(longest),
        0,
        "note: ceiling 'notes' — 100 characters, error, window 2026-08-01 to 2026-09-01: 1 document(s),"
        " the longest " + WEIRD_SHOWN + " at 90, 10 to spare\n"
        "GREEN: const-doc-budgets: 1 document(s) measured under 1 ceiling(s) and 0 departure(s), 4"
        " Markdown file(s) scanned\n",
    )
    exactly(scan(root), 0, wanted)
    assert "the longest of the day docs/notes/a.md at 70" in scan(tie, "--since", "2026-08-20").stdout, (
        "the report names the first of two equal documents in path order"
    )
    exactly(
        twice,
        0,
        green("300 characters; the ceiling 'notes' is lifted by const-doc-budgets.departures entry 1"),
    )


@item(24, "report: a link to a file measured as that file, as the scan does; other links left out")
def test_t24() -> None:
    """The report measures a symbolic link as the scan does: a link to a file in the tree is that file
    at the link's own path, through a chain and a linked folder too; a link to a folder, out of the
    tree, absolute, to a file with a slash after it, to nothing or through a missing folder, or in a
    loop is left out."""
    root = history_repo(
        [
            (
                "2026-08-20T09:00:00+0000",
                {
                    "docs/notes/a.md": doc(50),
                    "docs/long.md": doc(90),
                    "docs/other/x.md": doc(30),
                    "docs/hop": Link("notes/a.md"),
                    "docs/dir": Link("notes"),
                    "docs/notes/link.md": Link("../long.md"),
                    "docs/notes/chain.md": Link("../hop"),
                    "docs/notes/via.md": Link("../dir/a.md"),
                    "docs/notes/folder.md": Link("../other"),
                    "docs/notes/out.md": Link("../../../docs/long.md"),
                    "docs/notes/abs.md": Link("/../long.md"),
                    "docs/notes/slash.md": Link("../long.md/"),
                    "docs/notes/gone.md": Link("missing.md"),
                    "docs/notes/ghost.md": Link("../nothere/../long.md"),
                    "docs/notes/loop.md": Link("loop.md"),
                },
            )
        ]
    )
    exactly(
        scan(root, "--since", "2026-08-20"),
        0,
        "2026-08-20 notes: 4 document(s) at the day's last commit, the longest of the day"
        " docs/notes/link.md at 90\n"
        "window notes: 2026-08-20 to 2026-08-20, a span of 0 day(s), the longest docs/notes/link.md at"
        " 90; plus 10 % rounded up to 1,000: 1,000; set now: 100\n"
        "const-doc-budgets: history since 2026-08-20 — 1 commit(s) of the first-parent line read, 1"
        " day(s) with data, 1 ceiling(s); a report, nothing judged\n",
    )
    exactly(  # the scan of the same tree holds the same four documents and names the same longest
        scan(root),
        0,
        "note: ceiling 'notes' — 100 characters, error, window 2026-08-01 to 2026-09-01: 4 document(s),"
        " the longest docs/notes/link.md at 90, 10 to spare\n"
        "GREEN: const-doc-budgets: 4 document(s) measured under 1 ceiling(s) and 0 departure(s), 6"
        " Markdown file(s) scanned\n",
    )


@item(15, "the report refuses a shallow clone, another date form, and --since without --scan")
def test_t15() -> None:
    """The report refuses what it cannot answer: a shallow clone, a date of another form, --since
    without --scan; each typed whole, exit 1 with the count line after it."""
    source = history_repo(HISTORY)
    clone = H.scratch_dir() / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{source}", str(clone)],
        check=True,
        capture_output=True,
    )
    shallow = scan(clone, "--since", "2026-08-11")
    weird_parent = H.scratch_dir()
    weird_clone = weird_parent / WEIRD_DIR
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{source}", str(weird_clone)],
        check=True,
        capture_output=True,
    )
    weird_shallow = scan(weird_clone, "--since", "2026-08-11")
    bad_date = scan(source, "--since", "2026-8-11")
    week = scan(source, "--since", "2026-W33-2")  # a form the standard library would take
    broken_up = scan(source, "--since", "2026\n" + "x" * 90)  # 95 characters, a break inside the first 80
    slashed = scan(source, "--since", "2026\\x")  # a backslash, shown escaped
    alone = H.run_gate("", args=["--since", "2026-08-11"])
    date_line = (
        "BROKEN: misinvocation: --since takes a date written YYYY-MM-DD, not '{v}' — fix: run --scan [<dir>]"
        " --since <YYYY-MM-DD>, the first day of the window to report"
    )
    shallow_fix = (
        " is a shallow clone, so its history holds only the last commits — fix: a report on days it cannot"
        " see would say they held nothing: run git fetch --unshallow, or in CI check out with the whole"
        " history (fetch-depth: 0), then run the report again"
    )
    broken(shallow, f"BROKEN: {os.path.realpath(clone)}" + shallow_fix)
    broken(  # the folder's path whole, over 80 characters, its break and backslash escaped
        weird_shallow, f"BROKEN: {os.path.realpath(weird_parent)}/" + WEIRD_DIR_SHOWN + shallow_fix
    )
    broken(bad_date, date_line.format(v="2026-8-11"))
    broken(week, date_line.format(v="2026-W33-2"))
    # the value only points: cut at 80 characters with the cut said, its break and backslash escaped,
    # the expected text typed by hand, not built by the shared function the message calls
    broken(broken_up, date_line.format(v="2026\\n" + "x" * 75 + "… [95 characters]"))
    broken(slashed, date_line.format(v="2026\\\\x"))
    broken(
        alone,
        "BROKEN: misinvocation: --since applies to --scan — fix: run with no arguments (hook) or --scan"
        " [<dir>] [--since <date>]",
    )


@item(16, "the count and the rule of thumb on values typed by hand")
def test_t16() -> None:
    """The count and the rule of thumb on values typed by hand: code points, a CRLF as one, a byte-order
    mark as one; the longest plus 10 %, rounded up to 1,000."""
    family = "\U0001f468‍\U0001f469‍\U0001f467"  # three people and two joiners: 5 code points
    counts = [
        (characters("a\r\nb"), 3),
        (characters("a\rb\nc"), 5),
        (characters("café"), 5),
        (characters(family), 5),
        (characters("﻿x"), 2),
    ]
    thumbs = [(rule_of_thumb(30126), 34000), (rule_of_thumb(71590), 79000), (rule_of_thumb(12313), 14000)]
    thumbs += [(rule_of_thumb(1000), 2000), (rule_of_thumb(909), 1000)]
    ok = all(got == want for got, want in [*counts, *thumbs])
    assert ok, f"counts {counts}; thumbs {thumbs}"


@item(17, "a file that is not valid UTF-8 is measured, a bad byte one character")
def test_t17() -> None:
    """A file that is not valid UTF-8 is measured, each replacement character the decoder puts in one:
    a lone 0xff byte is one, and so is a three-byte sequence cut after two bytes, which a count per byte
    makes two."""
    root = prepared()
    (root / "docs/notes").mkdir(parents=True, exist_ok=True)
    bad = (
        b"\xff" * 45 + b"\xe2\x82" * 50
    )  # 45 lone bytes and 50 truncated sequences: 95 characters, 145 bytes
    (root / "docs/notes/bin.md").write_bytes(b"# T\n\n" + bad + b"\n")  # 101 characters
    finding = b1("docs/notes/bin.md", "101", "1")
    exactly(after_write(root, "docs/notes/bin.md"), 2, "", block(finding, "docs/notes/bin.md"))


@item(18, "an event other than a write is a configuration failure")
def test_t18() -> None:
    """An event of another name carrying a write's input is a configuration failure typed whole; an
    event that carries no file — a session start sent to the gate — is the shared visible skip."""
    root = prepared()
    result = H.run_gate(event_json(root, Write("docs/notes/a.md", doc(10)), event="Notification"))
    odd = H.run_gate(event_json(root, Write("docs/notes/a.md", doc(10)), event="N\nx\\y" + "e" * 90))
    start = H.run_gate(
        json.dumps(
            {"hook_event_name": "SessionStart", "session_id": "s", "cwd": str(root), "source": "startup"}
        )
    )
    broken(
        result,
        "BROKEN: this check is wired to a tool event before or after a write, not to 'Notification' —"
        " fix:"
        " in hooks.json wire it to PostToolUse on Write|Edit, or run it with --scan [<dir>]",
    )
    broken(  # an event name only points: cut at 80 characters with the cut said, then escaped
        odd,
        "BROKEN: this check is wired to a tool event before or after a write, not to"
        " 'N\\nx\\\\y" + "e" * 75 + "… [95 characters]' — fix: in hooks.json wire it to PostToolUse on"
        " Write|Edit, or run it with --scan [<dir>]",
    )
    exactly(
        start,
        0,
        "GREEN: const-doc-budgets: 0 documents examined — an event that names no tool is not one this"
        " gate judges (it judges Write and Edit)\n",
    )


# ---------------------------------------------------------------- the session-start printer

ZERO_LINE = (
    "const-doc-budgets: no document is measured — const-doc-budgets.ceilings is empty or absent in"
    " constitution.yaml"
)


def session_json(root: Path) -> str:
    return json.dumps(
        {
            "hook_event_name": "SessionStart",
            "session_id": "fixture-session",
            "cwd": str(root),
            "source": "startup",
        }
    )


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


@item(19, "session start: nothing while a ceiling is set; the zero line as stated; no dials, no repository")
def test_t19() -> None:
    """Nothing while a ceiling is set; the zero line typed by hand when the dial is empty or absent, of
    the size the module document states; no dials file (the first also from a subfolder of the root) and no
    repository said in the module's words, roots and folders whose names hold `:` too."""
    # the printer is a hook: each of its git calls has the hook's budget, logged before the call is made
    # with no clock, so that a slow git on a loaded machine cuts none of them
    patch, log = git_patch(SESSION, unclocked=True)
    set_ = SESSION.run_gate(session_json(prepared()), env=patch)
    empty = SESSION.run_gate(session_json(prepared({NAMESPACE: {"ceilings": []}})))
    absent = SESSION.run_gate(session_json(prepared({NAMESPACE: {}})))
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"one line of ([0-9,]+) characters saying that no document is measured", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    root = colon_root()
    no_dials = SESSION.run_gate(session_json(root))
    (root / "sub").mkdir()
    from_sub = SESSION.run_gate(session_json(root / "sub"))
    no_dials_line = (
        f"const-doc-budgets: no constitution.yaml in {root} — the length gate measures nothing there"
        " until the file sets a ceiling in const-doc-budgets.ceilings\n"
    )
    loose = colon_dir()
    no_repo = SESSION.run_gate(session_json(loose), env={"GIT_CEILING_DIRECTORIES": str(loose.parent)})
    weird_parent = H.scratch_dir()
    weird_root = Consumer(weird_parent / WEIRD_DIR).build().root  # a root of over 80 characters, a break, a \
    (weird_root / "constitution.yaml").unlink()
    weird_no_dials = SESSION.run_gate(session_json(weird_root))
    weird_loose = weird_parent / ("l" + WEIRD_DIR)
    weird_loose.mkdir()
    weird_no_repo = SESSION.run_gate(
        session_json(weird_loose), env={"GIT_CEILING_DIRECTORIES": str(weird_parent)}
    )
    exactly(  # the folder whole: escaped, never cut
        weird_no_dials,
        0,
        f"const-doc-budgets: no constitution.yaml in {weird_parent}/" + WEIRD_DIR_SHOWN + " — the length"
        " gate measures nothing there until the file sets a ceiling in const-doc-budgets.ceilings\n",
    )
    exactly(
        weird_no_repo,
        0,
        f"const-doc-budgets: {weird_parent}/l" + WEIRD_DIR_SHOWN + " is not inside a git repository — the"
        " length gate measures nothing there\n",
    )
    exactly(set_, 0, "")
    hook_budget(git_timeouts(log))
    exactly(empty, 0, ZERO_LINE + "\n")
    exactly(absent, 0, ZERO_LINE + "\n")
    assert stated == 111, f"the document states {stated} characters; 111 typed by hand"
    assert len(ZERO_LINE) == 111, f"the zero line has {len(ZERO_LINE)} characters; 111 typed by hand"
    exactly(no_dials, 0, no_dials_line)
    exactly(from_sub, 0, no_dials_line)
    exactly(
        no_repo,
        0,
        f"const-doc-budgets: {loose} is not inside a git repository — the length gate measures nothing"
        " there\n",
    )


@item(20, "session start: malformed dials, an argument, PyYAML and python3 missing")
def test_t20() -> None:
    """The printer's failures: the shared code dropped from a copy is C15 and git missing is C3; malformed
    dials exit 1 with C4 first and nothing on stdout; a ceiling at error on 14 days is this module's C5; an
    argument is a misinvocation; PyYAML missing is C2 and python3 missing is C1, each with the printer's
    clause."""
    # typed by hand
    could_not_run = "BROKEN: the session-start line could not be printed — the gate's state is unknown"
    bad = SESSION.run_gate(session_json(prepared(raw_dials="root-policy: [\n")))
    bad_ok = (
        bad.code == 1
        and bad.stdout == ""
        and bad.stderr.startswith("BROKEN: constitution.yaml is not valid YAML")
        and could_not_run in bad.stderr
    )
    short = {**NOTES, "window": {"from": "2026-08-01", "to": "2026-08-15"}}
    refused = SESSION.run_gate(session_json(prepared(own(ceilings=[short]))))
    refused_ok = (
        refused.code == 1
        and refused.stdout == ""
        and refused.stderr.startswith(
            "BROKEN: constitution.yaml: const-doc-budgets.ceilings 'notes' is at level error on a window"
            " whose"
            " span is 14 day(s), 2026-08-01 to 2026-08-15"
        )
    )
    arg = SESSION.run_gate(session_json(prepared()), args=["--scan"])
    arg_ok = arg.code == 1 and "BROKEN: misinvocation: unexpected argument --scan" in arg.stderr
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_yaml = SESSION.run_gate(session_json(prepared()), env={"PYTHONPATH": str(shadow)})
    broken_first_line(
        no_yaml,
        "BROKEN: const-doc-budgets needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{PLUGIN_ROOT / 'requirements.txt'}' — until then the gate's state is not said at session start",
    )
    bin_dir = H.scratch_dir()
    (bin_dir / "sh").symlink_to(H.sh)
    (bin_dir / "dirname").symlink_to(shutil.which("dirname") or "dirname")
    no_python = SESSION.run_gate(session_json(prepared()), env={"PATH": str(bin_dir)})
    broken_first_line(
        no_python,
        "BROKEN: const-doc-budgets needs python3 — fix: install Python 3.12 or newer"
        " (https://www.python.org/downloads/) — until then the gate's state is not said at session start",
    )
    copy = H.scratch_dir() / "scripts"
    shutil.copytree(SCRIPTS, copy, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", ".mypy_cache"))
    (copy / "constitution_layer_kit").unlink()  # an install that dropped the link to the shared code
    no_shared = SESSION.run_gate(
        session_json(prepared()), command=[SESSION.sh, str(copy / "session-start.sh")]
    )
    broken_first_line(
        no_shared,
        "BROKEN: const-doc-budgets is installed without its shared code (scripts/constitution_layer_kit is"
        " missing or is"
        " not a directory) — fix: install the plugin from its marketplace, or load it from a full checkout of"
        " the repository it comes from; a copy of the plugin's folder must be made with links followed"
        " (cp -RL) — until then the gate's state is not said at session start",
    )
    no_git_bin = H.scratch_dir()
    for tool in ("sh", "dirname"):
        (no_git_bin / tool).symlink_to(shutil.which(tool) or tool)
    # the runner's own interpreter, never what `python3` resolves to on the PATH: that can be a launcher
    # script that needs a shell this folder does not hold
    (no_git_bin / "python3").symlink_to(os.path.realpath(sys.executable))
    no_git = SESSION.run_gate(session_json(prepared()), env={"PATH": str(no_git_bin)})
    broken_first_line(
        no_git,
        "BROKEN: const-doc-budgets needs git on PATH — fix: install git (https://git-scm.com/downloads)",
    )
    assert no_shared.stdout == "" and messages.z1_could_not_run() in no_shared.stderr, (
        f"exit {no_shared.code}, stdout {no_shared.stdout[:80]!r}: {no_shared.stderr}"
    )
    assert no_git.stdout == "" and messages.z1_could_not_run() in no_git.stderr, (
        f"exit {no_git.code}, stdout {no_git.stdout[:80]!r}: {no_git.stderr}"
    )
    assert bad_ok, f"malformed dials got {bad.code}: {bad.stdout!r} {bad.stderr[:300]!r}"
    assert arg_ok, f"an argument got {arg.code}: {arg.stderr[:200]!r}"
    assert refused_ok, f"a ceiling at error on 14 days got {refused.code}: {refused.stderr[:300]!r}"
    assert no_yaml.stdout == "", f"exit {no_yaml.code}, stdout {no_yaml.stdout[:80]!r}: {no_yaml.stderr}"
    assert no_python.stdout == "", (
        f"exit {no_python.code}, stdout {no_python.stdout[:80]!r}: {no_python.stderr}"
    )


@item(21, "hooks shape; description size and the stated listing count; manifest name")
def test_t21() -> None:
    """The hooks file's shape; the skill's description fits the platform's listing limit of 1,536
    characters, and the module document states its size; the manifest names the plugin. The kit's names an
    installed text must not carry are the kit check `check-portability`'s."""
    texts = {path.name: path.read_text(encoding="utf-8") for path in (SKILL, MANIFEST)}
    hooks = json.loads(HOOKS.read_text(encoding="utf-8"))["hooks"]
    start_hook, write_hook = hooks["SessionStart"][0], hooks["PostToolUse"][0]
    shape = (
        set(hooks) == {"SessionStart", "PostToolUse"}
        and "matcher" not in start_hook
        and start_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"]
        and write_hook["matcher"] == "Write|Edit"
        and write_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/check-budgets.sh"]
        and all(
            h["hooks"][0]["command"] == "sh" and isinstance(h["hooks"][0]["timeout"], int)
            for h in (start_hook, write_hook)
        )
    )
    front = yaml.safe_load(texts["SKILL.md"].split("---")[1])
    listing = len(str(front["description"])) + len(str(front.get("when_to_use", "")))
    manifest = json.loads(texts["plugin.json"])
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"a listing of ([0-9,]+) characters", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    assert stated == listing, f"the module document states {stated} characters, the listing has {listing}"
    assert shape, "SessionStart without matcher, PostToolUse on Write|Edit, exec form, timeouts"
    assert listing <= 1536, f"the skill's listing text is {listing} characters, within 1,536"
    assert manifest["name"] == NAMESPACE, f"the manifest names {manifest['name']}"


NOTED = Write("docs/notes/ok.md", doc(151))


def subject_gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    """`gate_on` for the shared items, which hand over `noted` with no patch: its ceiling is then at
    level warning, so the excess is a note."""
    if action == NOTED and dials_patch is None and raw_dials is None:
        dials_patch = own(ceilings=[{**NOTES, "level": "warning"}])
    return gate_on(action, dials_patch, env, raw_dials, files, remove)


SUBJECT = Subject(
    harness=H,
    gate_on=subject_gate_on,
    own=own,
    valid=Write("docs/notes/ok.md", doc(40)),
    red=Write("docs/notes/bad.md", doc(151)),
    red_finding=b1("docs/notes/bad.md", "151", "51"),
    green="characters against the ceiling 'notes' of 100",  # the count left out: a byte-order mark is one
    # more character by the project's conventions, and the item about one compares this text
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=False,
    judges_envelopes=False,
    outside="docs/notes/bad.md is under no ceiling (const-doc-budgets.ceilings)",
    hook_lists_files=False,  # the hook matches the written file by pattern and never lists the tree
    long_value=None,  # a finding echoes a path and numbers, never a value from the document
    noted=NOTED,
    note="note: docs/notes/ok.md: 151 characters, over the ceiling 'notes' of 100 by 51 — reported, not red,"
    " while the ceiling's level is warning; shorten it or split it before the ceiling blocks",
    pattern_dial=PatternDial(
        "ceilings entry 1 paths", lambda pattern: own(ceilings=[{**NOTES, "paths": [pattern]}])
    ),
    skill="set-ceilings",  # the skill a red names (F10), typed by hand
)
