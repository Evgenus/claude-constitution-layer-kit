#!/usr/bin/env python3
"""Fixtures of const-styling: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

One entry point is driven, the scan, through the shared items and its own. The gate has no
hook mode, so the shared items run with the subject's `scan_only` flag: the items about hook
input, a written file and the warn channel are left out with their numbers kept free, and the
rest run the scan on the prepared consumer. The fixture consumer is the shared one; this module
resolves no policy and judges no envelope, so the shared items about the root policy and about
an unreadable envelope are left out too.
"""

from __future__ import annotations

import json
import re
import sys
import textwrap
from collections.abc import Callable, Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MODULE_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from consumer import Consumer  # noqa: E402
from harness import (  # noqa: E402
    Assertion,
    Harness,
    Result,
    Write,
    bash_json,
    broken_first_line,
    expect,
    red_lines,
)
from shared_items import Subject, shared_assertions  # noqa: E402
from styling_gate import messages, start  # noqa: E402
from styling_gate.model import Signature  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-style.sh", "check-style.py", start.GATE.namespace)
NAMESPACE = start.GATE.namespace
SIGNATURES = len(Signature)
GUIDE = MODULE_ROOT / "skills" / "style-defaults" / "style-guide.md"
SKILL = MODULE_ROOT / "skills" / "style-defaults" / "SKILL.md"


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
    action: Write | object,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    """The scan on a prepared consumer holding the action's document."""
    assert isinstance(action, Write)
    root = prepared(dials_patch, raw_dials, {**(files or {}), action.target: action.text}, remove)
    return H.run_gate("", args=["--scan", str(root)], env=env), root


def scan(files: dict[str, str], dials_patch: dict[str, object] | None = None) -> Result:
    root = prepared(dials_patch, files=files)
    return H.run_gate("", args=["--scan", str(root)])


def tail(documents: int, departures: int = 0, scanned: int | None = None) -> str:
    return messages.f9_tail(documents, SIGNATURES, departures, documents if scanned is None else scanned)


def green(documents: int, departures: int = 0, scanned: int | None = None) -> str:
    return f"GREEN: {NAMESPACE}: {tail(documents, departures, scanned)}"


def red(findings: int, documents: int, departures: int = 0) -> str:
    return f"RED: {findings} finding(s) — {tail(documents, departures)}"


def all_of(*checks: tuple[bool, str]) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in checks if not ok]
    return not failed, "; ".join(failed) if failed else "; ".join(evidence for _, evidence in checks)


def headlines(result: Result) -> list[str]:
    """The RED lines but the count line: the findings' headlines."""
    return red_lines(result.stdout)[:-1]


def one_finding(
    files: dict[str, str], headline: str, dials_patch: dict[str, object] | None = None
) -> tuple[bool, str]:
    result = scan(files, dials_patch)
    lines = headlines(result)
    ok = result.code == 2 and lines == [f"RED: {headline}"]
    return ok, headline if ok else f"exit {result.code}: {result.stdout.strip()}"


def no_finding(
    files: dict[str, str], dials_patch: dict[str, object] | None = None, departures: int = 0
) -> tuple[bool, str]:
    result = scan(files, dials_patch)
    return expect(result, 0, green(3 + len(files), departures), "stdout")


def finding_keys(files: dict[str, str]) -> list[str]:
    """The signatures found, in order, read from the headlines back through the message functions."""
    result = scan(files)
    found: list[str] = []
    for line in headlines(result):
        for signature in Signature:
            key = messages.finding("x", type("H", (), {"signature": signature, "line": 1, "text": "t"})()).key
            if key.value in _key_of_headline(line):
                found.append(signature.value)
                break
    return found


def _key_of_headline(line: str) -> str:
    """Which message a headline came from, by its fixed words."""
    words = {
        "PlantUML where Mermaid": "Y1",
        "a formula where pseudocode": "Y2",
        "a callout where none": "Y3",
        "where three is the deepest": "Y4",
        "skipping a level": "Y5",
        "a second level-one heading": "Y6",
        "names no language": "Y7",
        "a marker other than a dash": "Y8",
        "an ordered item numbered": "Y9",
        "emphasis by underscores": "Y10",
        "a table row with": "Y11",
        "an empty cell in column": "Y12",
    }
    return next((key for text, key in words.items() if text in line), "")


# ---------------------------------------------------------------- the twelve signatures

PLANTUML_FENCE = "# T\n\n```plantuml\n@startuml\nA -> B\n@enduml\n```\n"
PLANTUML_BARE = "# T\n\n```text\n@startuml\nA -> B\n@enduml\n```\n"
MERMAID = "# T\n\n```mermaid\nflowchart LR\n  A --> B\n```\n"


def t1() -> tuple[bool, str]:
    """red→green: a PlantUML fence is red with Y1 typed whole; a Mermaid fence is green; a departure
    entry naming the file makes the same document green and the count says one departure."""
    result = scan({"docs/notes/d.md": PLANTUML_FENCE})
    wanted = (
        "RED: docs/notes/d.md:3: PlantUML where Mermaid is the default — ```plantuml\n"
        "  why: Mermaid renders on GitHub, GitLab and in editor previews with no server; PlantUML needs one\n"
        "  fix: draw the diagram in a ```mermaid fence, or declare the departure with its reason: add to"
        " const-styling.departures in constitution.yaml an entry {paths: [<the file, or a pattern of the"
        " documents that depart>], allow: [plantuml], reason: <the capability Mermaid lacks, in one line>}\n"
        "RED: 1 finding(s) — 4 document(s) examined for 12 signature(s) under 0 departure(s), 4 Markdown"
        " file(s) scanned"
    )
    red_ok = result.code == 2 and result.stdout.strip() == wanted
    bare = one_finding(
        {"docs/notes/d.md": PLANTUML_BARE},
        "docs/notes/d.md:4: PlantUML where Mermaid is the default — @startuml",
    )
    mermaid = no_finding({"docs/notes/d.md": MERMAID})
    departure = [{"paths": ["/docs/notes/d.md"], "allow": ["plantuml"], "reason": "a timing diagram"}]
    allowed = scan({"docs/notes/d.md": PLANTUML_FENCE}, own(departures=departure))
    allowed_ok = expect(allowed, 0, green(4, 1), "stdout")
    return all_of(
        (red_ok, "Y1 typed whole matches" if red_ok else f"differs (exit {result.code}):\n{result.stdout}"),
        bare,
        mermaid,
        allowed_ok,
    )


def t2() -> tuple[bool, str]:
    """red→green: a math fence and a $$ line are red (Y2); a pseudocode fence is green; $$ inside a
    fence of another language is code."""
    fence = one_finding(
        {"docs/notes/f.md": "# T\n\n```math\nE = mc^2\n```\n"},
        "docs/notes/f.md:3: a formula where pseudocode is the default — ```math",
    )
    line = one_finding(
        {"docs/notes/f.md": "# T\n\n$$ E = mc^2 $$\n"},
        "docs/notes/f.md:3: a formula where pseudocode is the default — $$ E = mc^2 $$",
    )
    pseudo = no_finding(
        {"docs/notes/f.md": "# T\n\n```text\nenergy = mass * c * c\n```\n\n```bash\necho $$\n```\n"}
    )
    return all_of(fence, line, pseudo)


def t3() -> tuple[bool, str]:
    """red→green: an alert line is red (Y3); a plain blockquote is green."""
    alert = one_finding(
        {"docs/notes/c.md": "# T\n\n> [!NOTE]\n> Careful.\n"},
        "docs/notes/c.md:3: a callout where none is the default — > [!NOTE]",
    )
    quote = no_finding({"docs/notes/c.md": "# T\n\n> A quoted reply, as it was written.\n"})
    return all_of(alert, quote)


def t4() -> tuple[bool, str]:
    """red→green: a level-four heading is red (Y4), and one that also skips a level is two findings;
    three levels in order are green; a closing sequence of hashes and a heading in a fence are not."""
    deep = one_finding(
        {"docs/notes/h.md": "# T\n\n## A\n\n### B\n\n#### C\n"},
        "docs/notes/h.md:7: a heading of level 4 where three is the deepest",
    )
    both = scan({"docs/notes/h.md": "# T\n\n## A\n\n#### C\n"})
    both_ok = headlines(both) == [
        "RED: docs/notes/h.md:5: a heading of level 4 where three is the deepest",
        "RED: docs/notes/h.md:5: a heading of level 4, skipping a level",
    ]
    fine = no_finding({"docs/notes/h.md": "# T\n\n## A ##\n\n### B\n\n```text\n#### not a heading\n```\n"})
    return all_of(deep, (both_ok, "deep and skipped on one line" if both_ok else both.stdout), fine)


def t5() -> tuple[bool, str]:
    """red→green: a skipped level (Y5) and a second level-one heading (Y6) are red; a level that
    steps back up by any number is green."""
    skipped = one_finding(
        {"docs/notes/s.md": "# T\n\n### B\n"}, "docs/notes/s.md:3: a heading of level 3, skipping a level"
    )
    second = one_finding(
        {"docs/notes/s.md": "# T\n\n## A\n\n# Another title\n"},
        "docs/notes/s.md:5: a second level-one heading — Another title",
    )
    up = no_finding({"docs/notes/s.md": "# T\n\n## A\n\n### B\n\n## C\n"})
    return all_of(skipped, second, up)


def t6() -> tuple[bool, str]:
    """red→green: a fence with no language is red (Y7), a tilde fence too; `text` is green; a fence
    closed by a longer one, an info string with attributes, and an indented fence in a list item."""
    bare = one_finding(
        {"docs/notes/k.md": "# T\n\n```\nls\n```\n"},
        "docs/notes/k.md:3: a fenced block that names no language",
    )
    tilde = one_finding(
        {"docs/notes/k.md": "# T\n\n~~~\nls\n~~~\n"},
        "docs/notes/k.md:3: a fenced block that names no language",
    )
    fine = no_finding(
        {
            "docs/notes/k.md": "# T\n\n```text\ntree\n```\n\n````markdown\n```\nnested\n```\n````\n\n"
            "```python {.numberLines}\nx = 1\n```\n\n- item\n\n   ```bash\n   ls\n   ```\n"
        }
    )
    return all_of(bare, tilde, fine)


def t7() -> tuple[bool, str]:
    """red→green: a star item and a plus item are red (Y8); dashes are green; a bold line and a
    horizontal rule are no items."""
    star = one_finding(
        {"docs/notes/l.md": "# T\n\n* one\n- two\n"},
        "docs/notes/l.md:3: a bullet item opening with a marker other than a dash — one",
    )
    plus = one_finding(
        {"docs/notes/l.md": "# T\n\n- one\n  + nested\n"},
        "docs/notes/l.md:4: a bullet item opening with a marker other than a dash — nested",
    )
    fine = no_finding({"docs/notes/l.md": "# T\n\n- one\n- two\n\n**bold** at the start\n\n***\n"})
    return all_of(star, plus, fine)


def t8() -> tuple[bool, str]:
    """red→green: all-ones numbering and a jump are red (Y9); a list starting anywhere and counting
    on is green, a paragraph ends a list so the next may start over, and a nested ordered list
    counts on its own."""
    ones = one_finding(
        {"docs/notes/n.md": "# T\n\n1. a\n1. b\n2. c\n"},
        "docs/notes/n.md:4: an ordered item numbered 1 after 1",
    )
    jump = one_finding(
        {"docs/notes/n.md": "# T\n\n1. a\n3. b\n"}, "docs/notes/n.md:4: an ordered item numbered 3 after 1"
    )
    fine = no_finding(
        {
            "docs/notes/n.md": "# T\n\n101. a\n102. b\n\nA paragraph.\n\n1. a\n   1. nested\n"
            "   2. nested\n2. b\n   - bullet\n3. c\n\n1) a\n2) b\n"
        }
    )
    return all_of(ones, jump, fine)


def t9() -> tuple[bool, str]:
    """red→green: _italic_ and __bold__ are red (Y10); a name with underscores, an underscore inside
    a word, a code span and a star are green."""
    italic = one_finding(
        {"docs/notes/e.md": "# T\n\nSome _quiet_ words.\n"},
        "docs/notes/e.md:3: emphasis by underscores — quiet",
    )
    bold = one_finding(
        {"docs/notes/e.md": "# T\n\nSome __loud__ words.\n"},
        "docs/notes/e.md:3: emphasis by underscores — loud",
    )
    fine = no_finding(
        {"docs/notes/e.md": "# T\n\nsnake_case_name, `__init__`, a_b_c and *fine* and **fine**, x_ y_z.\n"}
    )
    return all_of(italic, bold, fine)


def t10() -> tuple[bool, str]:
    """red→green: a row with a cell too few (Y11) and an empty cell (Y12) are red, the delimiter row
    is counted too; a table with a key column and an escaped pipe is green; lines with pipes and no
    delimiter row are no table."""
    short = one_finding(
        {"docs/notes/t.md": "# T\n\n| key | value |\n|---|---|\n| a |\n"},
        "docs/notes/t.md:5: a table row with 1 cell(s) under a header of 2",
    )
    empty = one_finding(
        {"docs/notes/t.md": "# T\n\n| key | value |\n|---|---|\n| a | |\n"},
        "docs/notes/t.md:5: an empty cell in column 2",
    )
    delimiter = one_finding(
        {"docs/notes/t.md": "# T\n\n| key | value |\n|---|\n| a | b |\n"},
        "docs/notes/t.md:4: a table row with 1 cell(s) under a header of 2",
    )
    fine = no_finding(
        {
            "docs/notes/t.md": "# T\n\n| key | value |\n|:---|---:|\n| a | x \\| y |\n| b | none |\n\n"
            "a | b\nc | d\n"
        }
    )
    return all_of(short, empty, delimiter, fine)


# ---------------------------------------------------------------- departures and territories


def t11() -> tuple[bool, str]:
    """Departures: an entry over a territory allows every document there; one by path allows that
    document alone; an entry allowing one signature does not allow another; an entry matching no
    covered document is a note, typed by hand, and never a finding."""
    files = {
        "docs/notes/a.md": PLANTUML_FENCE,
        "docs/notes/b.md": PLANTUML_FENCE,
        "docs/other/c.md": PLANTUML_FENCE,
    }
    territory = own(departures=[{"paths": ["docs/notes/**"], "allow": ["plantuml"], "reason": "timing"}])
    by_territory = scan(files, territory)
    territory_ok = headlines(by_territory) == [
        "RED: docs/other/c.md:3: PlantUML where Mermaid is the default — ```plantuml"
    ]
    by_path = scan(
        files, own(departures=[{"paths": ["/docs/notes/a.md"], "allow": ["plantuml"], "reason": "timing"}])
    )
    path_ok = [line.split(":")[1] for line in headlines(by_path)] == [
        " docs/notes/b.md",
        " docs/other/c.md",
    ] or (
        headlines(by_path)
        == [
            "RED: docs/notes/b.md:3: PlantUML where Mermaid is the default — ```plantuml",
            "RED: docs/other/c.md:3: PlantUML where Mermaid is the default — ```plantuml",
        ]
    )
    other = scan(
        {"docs/notes/a.md": PLANTUML_FENCE},
        own(departures=[{"paths": ["docs/notes/**"], "allow": ["formula"], "reason": "none"}]),
    )
    other_ok = expect(other, 2, red(1, 4, 1), "stdout")
    stale = scan(
        {"docs/notes/a.md": MERMAID},
        own(departures=[{"paths": ["docs/gone/**"], "allow": ["plantuml"], "reason": "was"}]),
    )
    note = (
        "note: const-styling.departures entry 1 (docs/gone/**) matches no covered document; the documents it"
        " allowed were deleted or moved, or the pattern is wrong"
    )
    stale_ok = stale.code == 0 and stale.stdout.splitlines()[0] == note and green(4, 1) in stale.stdout
    return all_of(
        (territory_ok, "territory entry" if territory_ok else by_territory.stdout),
        (path_ok, "path entry" if path_ok else by_path.stdout),
        other_ok,
        (stale_ok, "stale entry noted, typed by hand" if stale_ok else f"{stale.code}: {stale.stdout}"),
    )


def t12() -> tuple[bool, str]:
    """Territories: a negated pattern takes a document out and the count drops; the default covers a
    README at the top; the guides dial is validated and changes no verdict."""
    out = scan({"docs/notes/a.md": PLANTUML_FENCE}, own(territories=["*.md", "!docs/notes/**"]))
    out_ok = expect(out, 0, green(3, scanned=4), "stdout")
    top = one_finding(
        {"README.md": PLANTUML_FENCE}, "README.md:3: PlantUML where Mermaid is the default — ```plantuml"
    )
    guides = no_finding({"docs/notes/a.md": MERMAID}, own(guides=["docs/style/**"]))
    return all_of(out_ok, top, guides)


def t13() -> tuple[bool, str]:
    """This module's C5 lines typed by hand, each exit 1."""
    entry_fix = (
        "write the entry as paths: [<patterns>], allow: [<signature keys>], reason: <one line saying why"
        " these documents depart>; the keys are plantuml, formula, callout, deep-heading, skipped-level,"
        " second-h1, fence-language, list-marker, list-numbering, underscore-emphasis, table-columns,"
        " table-empty-cell"
    )
    cases: list[tuple[dict[str, object], str]] = [
        (
            own(colour="red"),
            "BROKEN: constitution.yaml: const-styling.colour is no dial of this module — fix: a misspelt dial"
            " would be ignored in silence, so none is: write one of log_dir, territories, guides, departures",
        ),
        (
            own(severity="block"),
            "BROKEN: constitution.yaml: const-styling.severity is no dial of this module — fix: a misspelt"
            " dial would be ignored in silence, so none is: write one of log_dir, territories, guides,"
            " departures",
        ),
        (
            own(territories=[]),
            "BROKEN: constitution.yaml: const-styling.territories must be a non-empty list of path patterns"
            ' — fix: write the patterns of the documents to scan, one per line under "- ", or leave the key'
            " out to cover every Markdown file; an empty list would examine nothing in silence",
        ),
        (
            own(guides="docs/style.md"),
            "BROKEN: constitution.yaml: const-styling.guides must be a list of path patterns — fix: write the"
            ' patterns of the style guides, one per line under "- ", or leave the key out; the scan reads'
            " nothing from them — the skill does",
        ),
        (
            own(departures="none"),
            "BROKEN: constitution.yaml: const-styling.departures must be a list of entries — fix: write one"
            ' entry per "- " item with the fields paths (a list of patterns), allow (a list of signature'
            " keys) and reason (one line); leave the key out, or write [], for no departure",
        ),
        (
            own(departures=["x"]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: it is not a mapping — fix:"
            f" {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["plantuml"], "reason": "r", "why": "w"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: 'why' is no field of an entry"
            f" — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": [], "allow": ["plantuml"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: paths must be a non-empty list of"
            f" path patterns — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["diagram"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: 'diagram' is no signature this scan"
            f" knows — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["plantuml"], "reason": " "}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: reason must be one non-empty line"
            f" saying why — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["#a.md"], "allow": ["plantuml"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: paths holds '#a.md', which git"
            f" would read as a comment or as two lines — fix: {entry_fix}",
        ),
    ]
    results = [broken_first_line(scan({"docs/notes/a.md": MERMAID}, patch), line) for patch, line in cases]
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, "; ".join(
        failed
    ) or f"{len(cases)} dial failures, each exit 1 with its line typed by hand"


def t14() -> tuple[bool, str]:
    """The scan run as a hook is its own C12, typed by hand; a misinvocation exits 1."""
    root = prepared()
    hook = H.run_gate(bash_json(root, "ls"))
    hook_ok = broken_first_line(
        hook,
        "BROKEN: this check has no hook mode: it scans a tree and judges no single write — fix: run it with"
        " --scan [<dir>]; the plugin wires it to no event",
    )
    mis = H.run_gate("", args=["--bogus"])
    return all_of(hook_ok, expect(mis, 1, "BROKEN: misinvocation:", "stderr"))


def t15() -> tuple[bool, str]:
    """Golden lines: the twelve headlines typed whole, one document carrying every signature once, in
    line order; and a document with none is green."""
    text = (
        "# T\n\n"  # 1-2
        "```plantuml\nA -> B\n```\n\n"  # 3-6
        "$$ x $$\n\n"  # 7-8
        "> [!TIP]\n\n"  # 9-10
        "#### Deep\n\n"  # 11-12: deep and skipped
        "# Second\n\n"  # 13-14
        "```\nbare\n```\n\n"  # 15-18
        "* star\n\n"  # 19-20
        "1. a\n1. b\n\n"  # 21-23
        "_under_\n\n"  # 24-25
        "| k | v |\n|---|---|\n| a |\n| b | |\n"  # 26-29
    )
    result = scan({"docs/notes/g.md": text})
    wanted = [
        "RED: docs/notes/g.md:3: PlantUML where Mermaid is the default — ```plantuml",
        "RED: docs/notes/g.md:7: a formula where pseudocode is the default — $$ x $$",
        "RED: docs/notes/g.md:9: a callout where none is the default — > [!TIP]",
        "RED: docs/notes/g.md:11: a heading of level 4 where three is the deepest",
        "RED: docs/notes/g.md:11: a heading of level 4, skipping a level",
        "RED: docs/notes/g.md:13: a second level-one heading — Second",
        "RED: docs/notes/g.md:15: a fenced block that names no language",
        "RED: docs/notes/g.md:19: a bullet item opening with a marker other than a dash — star",
        "RED: docs/notes/g.md:22: an ordered item numbered 1 after 1",
        "RED: docs/notes/g.md:24: emphasis by underscores — under",
        "RED: docs/notes/g.md:28: a table row with 1 cell(s) under a header of 2",
        "RED: docs/notes/g.md:29: an empty cell in column 2",
    ]
    ok = result.code == 2 and headlines(result) == wanted and red_lines(result.stdout)[-1] == red(12, 4)
    clean = no_finding({"docs/notes/g.md": MERMAID})
    return all_of((ok, "twelve headlines in order" if ok else result.stdout), clean)


def t16() -> tuple[bool, str]:
    """A finding echoing a value of 12,000 characters is cut and the cut is said, the verdict a message."""
    result = scan({"docs/notes/x.md": "# T\n\n* " + "x" * 12000 + "\n"})
    ok = (
        result.code == 2
        and len(red_lines(result.stdout)) == 2
        and "… [12000 characters]" in result.stdout
        and "x" * 81 not in result.stdout
        and len(result.stdout) < 2_000
    )
    return ok, f"{len(result.stdout)} characters of verdict" if ok else result.stdout[:300]


# ---------------------------------------------------------------- the shipped files


def t17() -> tuple[bool, str]:
    """The shipped style guide passes the scan it describes, placed in a consumer as its guide, and
    carries the ten defaults as numbered entries; the skill's description is under the platform's
    listing cap and of the size the module's document states."""
    guide = GUIDE.read_text(encoding="utf-8")
    passes = no_finding({"docs/style-guide.md": guide})
    entries = re.findall(r"^\d+\. <a id=\"d(\d+)\"></a>\*\*", guide, flags=re.M)
    entries_ok = entries == [str(n) for n in range(1, 11)]
    front = SKILL.read_text(encoding="utf-8").split("---")[1]
    description = str(yaml.safe_load(front)["description"]).strip()
    stated = re.search(
        r"description of ([0-9,]+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    size_ok = stated is not None and int(stated.group(1).replace(",", "")) == len(description) <= 1536
    return all_of(
        passes,
        (entries_ok, "ten entries d1 to d10" if entries_ok else f"entries {entries}"),
        (
            size_ok,
            f"description of {len(description)} characters, as stated"
            if size_ok
            else f"description {len(description)}, stated {stated and stated.group(1)}",
        ),
    )


def t18() -> tuple[bool, str]:
    """The install note, the skill and the guide name no kit document; the manifest names the plugin;
    the install note's calibration example is accepted as it stands and describes the twelve keys."""
    kit_words = (
        "requirements.md",
        "rollout-plan",
        "dec-00",
        "res-00",
        "MODULE.md",
        "CONVENTIONS.md",
        "GATE.md",
    )
    texts = {
        "INSTALL.md": (MODULE_ROOT / "INSTALL.md").read_text(encoding="utf-8"),
        "SKILL.md": SKILL.read_text(encoding="utf-8"),
        "style-guide.md": GUIDE.read_text(encoding="utf-8"),
    }
    leaks = [f"{name}: {word}" for name, text in texts.items() for word in kit_words if word in text]
    manifest = json.loads((MODULE_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    manifest_ok = manifest["name"] == NAMESPACE and manifest["version"].startswith("0.0.")
    example = re.search(r"```yaml\n((?:.*\n)*?)[ ]*```", texts["INSTALL.md"])
    example_ok = False
    keys_ok = all(s.value in texts["INSTALL.md"] for s in Signature)
    if example:
        patch = yaml.safe_load(textwrap.dedent(example.group(1)))
        result = scan({"docs/notes/a.md": MERMAID, ".gitignore": ""}, patch)
        example_ok = result.code == 0
    return all_of(
        (not leaks, "no kit document named" if not leaks else "; ".join(leaks)),
        (manifest_ok, "manifest names the plugin, a draft version"),
        (
            example_ok,
            "the install note's example accepted" if example_ok else "the example is refused or missing",
        ),
        (keys_ok, "the twelve keys named in the install note"),
    )


# ---------------------------------------------------------------- the list

ITEMS: list[tuple[int, str, Callable[[], tuple[bool, str]]]] = [
    (1, "red→green: PlantUML is red with Y1 typed whole, Mermaid green, a departure by path allows it", t1),
    (2, "red→green: a math fence and a $$ line are red; pseudocode is green; $$ in code is code", t2),
    (3, "red→green: an alert line is red; a plain blockquote is green", t3),
    (4, "red→green: a fourth heading level is red, twice when it also skips; three levels are green", t4),
    (5, "red→green: a skipped level and a second H1 are red; stepping back up is green", t5),
    (
        6,
        "red→green: a fence without a language is red; text, nested, attributed and indented fences green",
        t6,
    ),
    (7, "red→green: star and plus items are red; dashes, a bold line and a rule are green", t7),
    (8, "red→green: all-ones and a jump are red; counting on from anywhere, a new list, nesting green", t8),
    (9, "red→green: underscore emphasis is red; names, words, code spans and stars are green", t9),
    (10, "red→green: a short row, an empty cell and a short delimiter row are red; a keyed table green", t10),
    (11, "departures: by territory, by path, one signature at a time; a stale entry is a note", t11),
    (12, "territories: a negated pattern drops the count; a README at the top; guides validated", t12),
    (13, "this module's C5 lines typed by hand, each exit 1", t13),
    (14, "the scan as a hook is its own C12; a misinvocation exits 1", t14),
    (15, "golden lines: the twelve headlines typed whole, in line order; a clean document green", t15),
    (16, "an echoed item of 12,000 characters is cut, and the cut is said", t16),
    (17, "the shipped guide passes its own scan with ten entries; the skill's description size", t17),
    (18, "the install note, skill and guide name no kit document; manifest; example accepted", t18),
]

SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=Write("docs/notes/ok.md", "# Ok\n\n- a\n- b\n"),
    red=Write("docs/notes/bad.md", PLANTUML_FENCE),
    red_finding=messages.y1_plantuml("docs/notes/bad.md", 3, "```plantuml"),
    green=green(4),
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=False,
    bare_readme=green(4),
    judges_envelopes=False,
    long_value=Write("docs/notes/long.md", "# T\n\n* " + "x" * 12000 + "\n"),
    scan_only=True,
)


def main() -> int:
    assertions = [Assertion(number, title, check) for number, title, check in ITEMS]
    return H.run_all([], [*assertions, *shared_assertions(SUBJECT, 101)])


if __name__ == "__main__":
    sys.exit(main())
