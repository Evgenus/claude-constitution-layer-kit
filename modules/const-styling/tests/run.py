#!/usr/bin/env python3
"""Fixtures of const-styling: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

One entry point is driven, the scan, through the shared items and its own. The gate has no
hook mode, so the shared items run with the subject's `scan_only` flag: the items about hook
input, a written file, the warn channel and a negated pattern's skip are left out with their
numbers kept free, and the rest run the scan on the prepared consumer; the twelve red→green
cases run through the harness's scan-only shape, each half a document written and scanned. The
fixture consumer is the shared one; this module resolves no policy and judges no envelope, so
the shared items about the root policy and about an unreadable envelope are left out too.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Callable, Sequence
from pathlib import Path

import yaml
from const_gate import identity
from consumer import BASE_MARKDOWN, Consumer
from harness import (
    Assertion,
    Case,
    Harness,
    Result,
    Write,
    bash_json,
    broken_first_line,
    expect,
    red_lines,
)
from shared_items import PatternDial, Subject, shared_assertions
from styling_gate import messages, start
from styling_gate.model import Hit, Signature

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MODULE_ROOT = SCRIPTS.parent

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
H = Harness(SCRIPTS, "check-style.sh", "check-style.py", start.GATE.namespace, scan_only=True)
NAMESPACE = start.GATE.namespace
SIGNATURES = len(Signature)
GUIDE = MODULE_ROOT / "skills" / "style-defaults" / "style-guide.md"
SKILL = MODULE_ROOT / "skills" / "style-defaults" / "SKILL.md"


# the line a red ends with (F10), typed by hand
F10 = (
    "const-styling: load the skill const-styling:style-defaults before you fix this"
    " — it teaches the rule and the fix\n"
)

# the pointer line printed at session start and at each subagent's start, typed by hand
POINTER = (
    "const-styling (advisory): before writing a table, a diagram, a list, a formula, a heading below level"
    " three, a callout or a fenced block in a document, load the skill const-styling:style-defaults."
)

# a file name of over 80 characters holding a line break and a backslash: the real name, and the text the
# scan shows for it, typed by hand — the whole name, since a path is what the reader opens
WEIRD = "docs/notes/w\nx\\y" + "z" * 80 + ".md"
WEIRD_SHOWN = "docs/notes/w\\nx\\\\y" + "z" * 80 + ".md"


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
    return expect(result, 0, green(BASE_MARKDOWN + len(files), departures), "stdout")


# ---------------------------------------------------------------- the twelve signatures

PLANTUML_FENCE = "# T\n\n```plantuml\n@startuml\nA -> B\n@enduml\n```\n"
PLANTUML_BARE = "# T\n\n```text\n@startuml\nA -> B\n@enduml\n```\n"
MERMAID = "# T\n\n```mermaid\nflowchart LR\n  A --> B\n```\n"


def t1() -> tuple[bool, str]:
    """red and green: a PlantUML fence is red with Y1 typed whole; a Mermaid fence is green; a departure
    entry naming the file makes the same document green and the count says one departure."""
    result = scan({"docs/notes/d.md": PLANTUML_FENCE})
    wanted = (
        "RED: docs/notes/d.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml\n"
        "  why: Mermaid renders on GitHub, GitLab and in editor previews with no server; PlantUML needs one\n"
        "  fix: draw the diagram in a ```mermaid fence, or declare the departure with its reason: add to"
        " const-styling.departures in constitution.yaml an entry {paths: [<the file, or a pattern of the"
        " documents that depart>], allow: [plantuml], reason: <the capability Mermaid lacks, in one line>};"
        " where your guide changed this default,"
        " the pattern is your whole tree, '*.md' in the default territory, and the reason names the"
        " guide's entry\n"
        "RED: 1 finding(s) — 4 document(s) examined for 12 signature(s) under 0 departure(s), 4 Markdown"
        " file(s) scanned"
    )
    red_ok = result.code == 2 and result.stdout == wanted + "\n" + F10
    bare = one_finding(
        {"docs/notes/d.md": PLANTUML_BARE},
        "docs/notes/d.md:4: PlantUML, where the shipped default is Mermaid — @startuml",
    )
    loose = one_finding(
        {"docs/notes/d.md": "# T\n\n@startuml\nA -> B\n@enduml\n"},
        "docs/notes/d.md:3: PlantUML, where the shipped default is Mermaid — @startuml",
    )
    puml = one_finding(
        {"docs/notes/d.md": "# T\n\n```puml\nA -> B\n```\n"},
        "docs/notes/d.md:3: PlantUML, where the shipped default is Mermaid — ```puml",
    )
    mermaid = no_finding({"docs/notes/d.md": MERMAID})
    departure = [{"paths": ["/docs/notes/d.md"], "allow": ["plantuml"], "reason": "a timing diagram"}]
    allowed = scan({"docs/notes/d.md": PLANTUML_FENCE}, own(departures=departure))
    allowed_ok = expect(allowed, 0, green(4, 1), "stdout")
    return all_of(
        (red_ok, "Y1 typed whole matches" if red_ok else f"differs (exit {result.code}):\n{result.stdout}"),
        bare,
        loose,
        puml,
        mermaid,
        allowed_ok,
    )


def t2() -> tuple[bool, str]:
    """red and green: a math fence and a $$ line are red (Y2); a pseudocode fence is green; $$ inside a
    fence of another language is code."""
    fence = one_finding(
        {"docs/notes/f.md": "# T\n\n```math\nE = mc^2\n```\n"},
        "docs/notes/f.md:3: a formula, where the shipped default is pseudocode — ```math",
    )
    line = one_finding(
        {"docs/notes/f.md": "# T\n\n$$ E = mc^2 $$\n"},
        "docs/notes/f.md:3: a formula, where the shipped default is pseudocode — $$ E = mc^2 $$",
    )
    pseudo = no_finding(
        {"docs/notes/f.md": "# T\n\n```text\nenergy = mass * c * c\n```\n\n```bash\necho $$\n```\n"}
    )
    return all_of(fence, line, pseudo)


def t3() -> tuple[bool, str]:
    """red and green: an alert line is red (Y3); a plain blockquote is green."""
    alert = one_finding(
        {"docs/notes/c.md": "# T\n\n> [!NOTE]\n> Careful.\n"},
        "docs/notes/c.md:3: a callout, where the shipped default is none — > [!NOTE]",
    )
    quote = no_finding({"docs/notes/c.md": "# T\n\n> A quoted reply, as it was written.\n"})
    return all_of(alert, quote)


def t4() -> tuple[bool, str]:
    """red and green: a level-four heading is red (Y4), and one that also skips a level is two findings;
    three levels in order are green; a closing sequence of hashes and a heading in a fence are not; a
    departure over the whole tree turns the signature off, level six included (the limit of section 9)."""
    deep = one_finding(
        {"docs/notes/h.md": "# T\n\n## A\n\n### B\n\n#### C\n"},
        "docs/notes/h.md:7: a heading of level 4, deeper than the shipped default of three",
    )
    both = scan({"docs/notes/h.md": "# T\n\n## A\n\n#### C\n"})
    both_ok = headlines(both) == [
        "RED: docs/notes/h.md:5: a heading of level 4, deeper than the shipped default of three",
        "RED: docs/notes/h.md:5: a heading of level 4, skipping a level",
    ]
    fine = no_finding(
        {
            "docs/notes/h.md": "# T\n\n## A ##\n\n### B\n\n```text\n#### not a heading\n```\n\n"
            "    #### nor this\n"
        }
    )
    whole_tree = [
        {"paths": ["*.md"], "allow": ["deep-heading"], "reason": "our guide allows four levels (entry 7)"}
    ]
    limit = no_finding(
        {"docs/notes/h.md": "# T\n\n## A\n\n### B\n\n#### C\n\n##### D\n\n###### E\n"},
        own(departures=whole_tree),
        departures=1,
    )
    return all_of(deep, (both_ok, "deep and skipped on one line" if both_ok else both.stdout), fine, limit)


def t5() -> tuple[bool, str]:
    """red and green: a skipped level (Y5) and a second level-one heading (Y6) are red; a level that
    steps back up by any number is green."""
    skipped = one_finding(
        {"docs/notes/s.md": "# T\n\n### B\n"}, "docs/notes/s.md:3: a heading of level 3, skipping a level"
    )
    second = one_finding(
        {"docs/notes/s.md": "# T\n\n## A\n\n# Another title\n"},
        "docs/notes/s.md:5: a second level-one heading — Another title",
    )
    up = no_finding({"docs/notes/s.md": "# T\n\n## A\n\n### B\n\n## C\n"})
    bom = one_finding(
        {"docs/notes/s.md": "\ufeff# T\n\n# U\n"}, "docs/notes/s.md:3: a second level-one heading — U"
    )
    after_fence = one_finding(
        {"docs/notes/s.md": "# T\n\n```text\nx\n```\n# U\n"},
        "docs/notes/s.md:6: a second level-one heading — U",
    )
    return all_of(skipped, second, up, bom, after_fence)


def t6() -> tuple[bool, str]:
    """red and green: a fence with no language is red (Y7), a tilde fence too; `text` is green; a fence
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
            "```python {.numberLines}\nx = 1\n```\n\n- item\n\n   ```bash\n   ls\n   ```\n\n"
            "```text\n```bash\n* not an item\n```\n\n- one\n  - two\n\n      ```text\n      * nor this\n"
            "      ```\n"
        }
    )
    return all_of(bare, tilde, fine)


def t7() -> tuple[bool, str]:
    """red and green: a star item and a plus item are red (Y8); dashes are green; a bold line and a
    horizontal rule are no items."""
    star = one_finding(
        {"docs/notes/l.md": "# T\n\n* one\n- two\n"},
        "docs/notes/l.md:3: a bullet item whose marker is not the shipped default, a dash — one",
    )
    plus = one_finding(
        {"docs/notes/l.md": "# T\n\n- one\n  + nested\n"},
        "docs/notes/l.md:4: a bullet item whose marker is not the shipped default, a dash — nested",
    )
    fine = no_finding({"docs/notes/l.md": "# T\n\n- one\n- two\n\n**bold** at the start\n\n***\n"})
    no_fence = one_finding(
        {"docs/notes/l.md": "# T\n\n``` x`y\n* star\n"},
        "docs/notes/l.md:4: a bullet item whose marker is not the shipped default, a dash — star",
    )
    odd = (
        one_finding(  # the echoed text holds backslashes and runs to 105 characters: cut at 80, then escaped
            {"docs/notes/l.md": "# T\n\n* a\\b\\c" + "x" * 100 + "\n"},
            "docs/notes/l.md:3: a bullet item whose marker is not the shipped default, a dash — a\\\\b\\\\c"
            + "x" * 75
            + "… [105 characters]",
        )
    )
    long_path = (
        one_finding(  # the path whole in the headline, over 80 characters, its break and backslash escaped
            {WEIRD: "# T\n\n* one\n"},
            WEIRD_SHOWN + ":3: a bullet item whose marker is not the shipped default, a dash — one",
        )
    )
    return all_of(star, plus, fine, no_fence, odd, long_path)


def t8() -> tuple[bool, str]:
    """red and green: all-ones numbering and a jump are red (Y9); a list starting anywhere and counting
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
            "   2. nested\n2. b\n   - bullet\n3. c\n\n1) a\n2) b\n\n## H\n\n1) again\n"
        }
    )
    return all_of(ones, jump, fine)


def t9() -> tuple[bool, str]:
    """red and green: _italic_ and __bold__ are red (Y10); a name with underscores, an underscore inside
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
        {
            "docs/notes/e.md": "# T\n\nsnake_case_name, `__init__`, a_b_c and *fine* and **fine**, x_ y_z.\n"
            "[text](https://e.com/_p_/y) and [x](docs/_p_.md) and https://e.com/_p_/y and <https://e.com/_p_/>"
            " <!-- _c_ -->\n<!--\n_hidden_\n```\n-->\n```markdown\n<!-- opens in a fence\n```\n\n"
            "The opener `<!--` in a code span.\n"
        }
    )
    link = one_finding(
        {"docs/notes/e.md": "# T\n\n[_text_](https://e.com/_p_/y)\n"},
        "docs/notes/e.md:3: emphasis by underscores — text",
    )
    after_fence = one_finding(
        {"docs/notes/e.md": "# T\n\n```markdown\n<!-- x\n```\n\n__after__\n"},
        "docs/notes/e.md:7: emphasis by underscores — after",
    )
    after_span = one_finding(
        {"docs/notes/e.md": "# T\n\nThe opener `<!--` starts a comment.\n\n__after__\n"},
        "docs/notes/e.md:5: emphasis by underscores — after",
    )
    closing = one_finding(
        {"docs/notes/e.md": "# T\n\n<!--\n_hidden_\n--> _raw_\n__shown__\n"},
        "docs/notes/e.md:6: emphasis by underscores — shown",
    )
    closer_in_span = one_finding(
        {"docs/notes/e.md": "# T\n\n<!-- _a_ `-->` b\n__after__\n"},
        "docs/notes/e.md:4: emphasis by underscores — after",
    )
    two_openers = one_finding(
        {"docs/notes/e.md": "# T\n\nt <!-- a --> _x_ <!-- b\n_hidden_\n-->\n"},
        "docs/notes/e.md:3: emphasis by underscores — x",
    )
    return all_of(italic, bold, fine, link, after_fence, after_span, closing, closer_in_span, two_openers)


def t10() -> tuple[bool, str]:
    """red and green: a row with a cell too few (Y11) and an empty cell (Y12) are red, the delimiter row
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
            "a | b\nc | d\n\ncell | text\n---\n\n| one |\n"
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
        "RED: docs/other/c.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml"
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
            "RED: docs/notes/b.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml",
            "RED: docs/other/c.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml",
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
    outside = scan(
        {"docs/notes/a.md": MERMAID, "docs/other/b.md": MERMAID},
        own(
            territories=["*.md", "!docs/other/**"],
            departures=[{"paths": ["docs/other/**"], "allow": ["plantuml"], "reason": "was"}],
        ),
    )
    outside_note = (
        "note: const-styling.departures entry 1 (docs/other/**) matches no covered document; the documents it"
        " allowed were deleted or moved, or the pattern is wrong"
    )
    outside_ok = outside.code == 0 and outside.stdout.splitlines()[0] == outside_note
    note = (
        "note: const-styling.departures entry 1 (docs/gone/**) matches no covered document; the documents it"
        " allowed were deleted or moved, or the pattern is wrong"
    )
    stale_ok = stale.code == 0 and stale.stdout.splitlines()[0] == note and green(4, 1) in stale.stdout
    long_pattern = "docs\\gone/" + "p" * 100  # 110 characters with a backslash: a pattern only points
    cut = scan(
        {"docs/notes/a.md": MERMAID},
        own(departures=[{"paths": [long_pattern], "allow": ["plantuml"], "reason": "was"}]),
    )
    cut_note = (
        "note: const-styling.departures entry 1 (docs\\\\gone/" + "p" * 70 + "… [110 characters]) matches no"
        " covered document; the documents it allowed were deleted or moved, or the pattern is wrong"
    )
    cut_ok = cut.code == 0 and cut.stdout.splitlines()[0] == cut_note
    return all_of(
        (territory_ok, "territory entry" if territory_ok else by_territory.stdout),
        (path_ok, "path entry" if path_ok else by_path.stdout),
        other_ok,
        (stale_ok, "stale entry noted, typed by hand" if stale_ok else f"{stale.code}: {stale.stdout}"),
        (outside_ok, "an entry over uncovered documents is stale" if outside_ok else outside.stdout),
        (cut_ok, "a pattern of 110 characters cut at 80, said, then escaped" if cut_ok else cut.stdout),
    )


def t12() -> tuple[bool, str]:
    """Territories: a negated pattern takes a document out and the count drops; the default covers a
    README at the top; the guides dial is validated and changes no verdict."""
    out = scan({"docs/notes/a.md": PLANTUML_FENCE}, own(territories=["*.md", "!docs/notes/**"]))
    out_ok = expect(out, 0, green(3, scanned=4), "stdout")
    top = one_finding(
        {"README.md": PLANTUML_FENCE},
        "README.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml",
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
            own(**{"bad\nkey": 1}),
            "BROKEN: constitution.yaml: const-styling.bad\\nkey is no dial of this module — fix: a misspelt"
            " dial would be ignored in silence, so none is: write one of log_dir, territories, guides,"
            " departures",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["plantuml"], "reason": "r", "a\nb": "w"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: 'a\\nb' is no field of an entry"
            f" — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["plant\numl"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: 'plant\\numl' is no signature this"
            f" scan knows — fix: {entry_fix}",
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
            own(territories=["#docs/**"]),
            "BROKEN: constitution.yaml: const-styling.territories holds a pattern git would not read as one:"
            " '#docs/**' — fix: a pattern may not start with '#' (a comment to git) nor contain a line"
            " break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break",
        ),
        (
            own(guides=["a\nb"]),
            "BROKEN: constitution.yaml: const-styling.guides holds a pattern git would not read as one:"
            " 'a\\nb' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["plantuml"], "reason": "one\rtwo"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: reason must be one non-empty line"
            f" saying why — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["a.md"], "allow": ["plantuml"], "reason": "one\ntwo"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1: reason must be one non-empty line"
            f" saying why — fix: {entry_fix}",
        ),
        (
            own(departures=[{"paths": ["#a.md"], "allow": ["plantuml"], "reason": "r"}]),
            "BROKEN: constitution.yaml: const-styling.departures entry 1 paths holds a pattern git would not"
            " read as one: '#a.md' — fix: a pattern may not start with '#' (a comment to git) nor contain a"
            " line break; "
            "escape a leading # as \\# bare or in single quotes, "
            "as \\\\# in double quotes, and remove a line break",
        ),
    ]
    results = [broken_first_line(scan({"docs/notes/a.md": MERMAID}, patch), line) for patch, line in cases]
    # what `reason: |` gives, a line break at the end: trimmed and taken, as in the other two gates
    block_scalar = own(departures=[{"paths": ["docs/gone/**"], "allow": ["plantuml"], "reason": "why\n"}])
    results.append(no_finding({"docs/notes/a.md": MERMAID}, block_scalar, departures=1))
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


GOLDEN = (
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


def t15() -> tuple[bool, str]:
    """Golden lines: the twelve headlines typed whole, one document carrying every signature once, in
    line order; and a document with none is green."""
    result = scan({"docs/notes/g.md": GOLDEN})
    wanted = [
        "RED: docs/notes/g.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml",
        "RED: docs/notes/g.md:7: a formula, where the shipped default is pseudocode — $$ x $$",
        "RED: docs/notes/g.md:9: a callout, where the shipped default is none — > [!TIP]",
        "RED: docs/notes/g.md:11: a heading of level 4, deeper than the shipped default of three",
        "RED: docs/notes/g.md:11: a heading of level 4, skipping a level",
        "RED: docs/notes/g.md:13: a second level-one heading — Second",
        "RED: docs/notes/g.md:15: a fenced block that names no language",
        "RED: docs/notes/g.md:19: a bullet item whose marker is not the shipped default, a dash — star",
        "RED: docs/notes/g.md:22: an ordered item numbered 1 after 1",
        "RED: docs/notes/g.md:24: emphasis by underscores — under",
        "RED: docs/notes/g.md:28: a table row with 1 cell(s) under a header of 2",
        "RED: docs/notes/g.md:29: an empty cell in column 2",
    ]
    ok = result.code == 2 and headlines(result) == wanted and red_lines(result.stdout)[-1] == red(12, 4)
    clean = no_finding({"docs/notes/g.md": MERMAID})
    long_path = scan(
        {WEIRD: GOLDEN}
    )  # the path of over 80 characters, whole and escaped, in all twelve headlines
    long_ok = (
        long_path.code == 2
        and len(headlines(long_path)) == 12
        and all(line.startswith("RED: " + WEIRD_SHOWN + ":") for line in headlines(long_path))
    )
    return all_of(
        (ok, "twelve headlines in order" if ok else result.stdout),
        clean,
        (long_ok, "the path whole in every headline" if long_ok else long_path.stdout[:600]),
    )


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
    odd = scan(  # six signatures echo a line: each holds a backslash and runs over 80 characters
        {
            "docs/notes/o.md": "# T\n\n"  # 1-2
            "```plantuml a\\b" + "p" * 100 + "\nA -> B\n```\n\n"  # 3-6
            "$$ a\\b " + "f" * 100 + " $$\n\n"  # 7-8
            "> [!TIP] a\\b" + "c" * 100 + "\n\n"  # 9-10
            "# Second a\\b" + "h" * 100 + "\n\n"  # 11-12
            "* a\\b" + "l" * 100 + "\n\n"  # 13-14
            "_a\\b" + "u" * 100 + "_\n"  # 15
        }
    )
    odd_wanted = [
        "RED: docs/notes/o.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml a\\\\b"
        + "p" * 65
        + "… [115 characters]",
        "RED: docs/notes/o.md:7: a formula, where the shipped default is pseudocode — $$ a\\\\b "
        + "f" * 73
        + "… [110 characters]",
        "RED: docs/notes/o.md:9: a callout, where the shipped default is none — > [!TIP] a\\\\b"
        + "c" * 68
        + "… [112 characters]",
        "RED: docs/notes/o.md:11: a second level-one heading — Second a\\\\b"
        + "h" * 70
        + "… [110 characters]",
        "RED: docs/notes/o.md:13: a bullet item whose marker is not the shipped default, a dash — a\\\\b"
        + "l" * 77
        + "… [103 characters]",
        "RED: docs/notes/o.md:15: emphasis by underscores — a\\\\b" + "u" * 77 + "… [103 characters]",
    ]
    odd_ok = odd.code == 2 and headlines(odd) == odd_wanted
    return all_of(
        (ok, f"{len(result.stdout)} characters of verdict" if ok else result.stdout[:300]),
        (odd_ok, "six echoed lines, backslash doubled, cut at 80" if odd_ok else odd.stdout[:1500]),
    )


# ---------------------------------------------------------------- golden lines


def t19() -> tuple[bool, str]:
    """Golden lines: the why and the fix of every finding typed by hand — a fixture built from the
    message functions cannot see a changed word — against the document of T15."""
    allow = (
        "or declare the departure with its reason: add to const-styling.departures in constitution.yaml an"
        " entry {paths: [<the file, or a pattern of the documents that depart>], allow: [{key}],"
        " reason: <{what}>}"
    )

    amended_tail = (
        "; where your guide changed this default, the pattern is your whole tree, '*.md' in the default"
        " territory, and the reason names the guide's entry"
    )

    def fix(head: str, key: str, what: str, amended: bool = False) -> str:
        tail = amended_tail if amended else ""
        return "  fix: " + head + allow.replace("{key}", key).replace("{what}", what) + tail

    wanted = [
        "  why: Mermaid renders on GitHub, GitLab and in editor previews with no server; PlantUML needs one",
        fix(
            "draw the diagram in a ```mermaid fence, ",
            "plantuml",
            "the capability Mermaid lacks, in one line",
            amended=True,
        ),
        "  why: a formula renders only in a web view and is invisible to a prose reader and a linter;"
        " pseudocode reads everywhere",
        fix(
            "write the computation as pseudocode in a fenced block, ",
            "formula",
            "why this must be a formula, in one line",
            amended=True,
        ),
        "  why: a callout pulls a sentence out of its argument; an aside is a clause, and a warning about an"
        " act is a sentence where the act is described",
        fix(
            "write the sentence in the paragraph it belongs to, ",
            "callout",
            "why the reader must see this apart from the text, in one line",
            amended=True,
        ),
        "  why: a fourth level is a section too small to stand on its own, and most renderers stop showing"
        " levels below three in a page's outline",
        fix(
            "make it a bold run-in label at the start of a paragraph, or split the document, ",
            "deep-heading",
            "why this document needs the level, in one line",
            amended=True,
        ),
        "  why: a skipped level makes a section look nested in one that does not exist, and an outline built"
        " from the headings mis-nests it",
        fix(
            "use the next level down from the heading before it, ",
            "skipped-level",
            "why the levels are read this way here, in one line",
        ),
        "  why: a document has one title; a second level-one heading is a second document or a section",
        fix(
            "make it a level-two heading, or move what follows it into a document of its own, ",
            "second-h1",
            "why this document carries two titles, in one line",
        ),
        "  why: the language after the fence tells a renderer how to highlight the block and a reader what it"
        " is looking at; without it every viewer guesses",
        fix(
            "name the language after the opening fence — ```bash, ```yaml, ```text for a directory tree or"
            " plain output, ",
            "fence-language",
            "why no language fits this block, in one line",
        ),
        "  why: one marker for every bullet list keeps the source uniform, so a diff shows a change of"
        " content and never a change of marker",
        fix(
            "open the item with the shipped default, '- ', ",
            "list-marker",
            "why this list keeps its marker, in one line",
            amended=True,
        ),
        "  why: an item is cited by the number written in the source, so the numbers must be the ones a"
        " reader sees: each the one before it plus one, never all ones and never a jump",
        fix(
            "renumber the list so that each item is the one before it plus one, or start a new list after a"
            " paragraph, ",
            "list-numbering",
            "why this list is numbered so, in one line",
        ),
        "  why: one emphasis marker keeps the source uniform, and an underscore inside a word or a name is"
        " text, which a second marker makes ambiguous",
        fix(
            "use the shipped default, *italic* and **bold**; put a name that carries underscores in a"
            " code span, ",
            "underscore-emphasis",
            "why this document marks emphasis so, in one line",
            amended=True,
        ),
        "  why: a row with more or fewer cells than the header puts values under the wrong heads, or drops"
        " them in silence, in every renderer",
        fix(
            "give the row exactly one cell per column of the header, a backslash before a pipe that belongs"
            " inside a cell, ",
            "table-columns",
            "why this table's rows differ, in one line",
        ),
        "  why: an empty cell does not say whether the value is none, unknown or forgotten",
        fix(
            "write none, or the value, in the cell, ",
            "table-empty-cell",
            "what an empty cell means in this table, in one line",
        ),
    ]
    result = scan({"docs/notes/g.md": GOLDEN})
    got = [
        line
        for line in result.stdout.splitlines()
        if line.startswith("  why: ") or line.startswith("  fix: ")
    ]
    ok = result.code == 2 and got == wanted
    return ok, "twelve why and fix lines typed whole" if ok else "\n".join(
        f"{a}\n{b}" for a, b in zip(got, wanted, strict=False) if a != b
    )[:1500]


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
    """The manifest names the plugin; the install note's calibration example is accepted as it stands and
    describes the twelve keys."""
    texts = {"INSTALL.md": (MODULE_ROOT / "INSTALL.md").read_text(encoding="utf-8")}
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
        (manifest_ok, "manifest names the plugin, a draft version"),
        (
            example_ok,
            "the install note's example accepted" if example_ok else "the example is refused or missing",
        ),
        (keys_ok, "the twelve keys named in the install note"),
    )


CLOSING = "until then no document is scanned for style"


def t20() -> tuple[bool, str]:
    """Every install-failure line closes with this gate's own clause, never the write gates' "until then
    Markdown writes pass unchecked": C1 (no python3, the POSIX entry), C2 (PyYAML missing, in the scan),
    C14 (an interpreter below the floor, run by a version it is told it has) and C15 (a copy without the
    shared code), each first line typed whole; and the entry files' source holds the clause exactly three
    times, once per entry text (C1, C14, C15), and "Markdown writes" nowhere."""
    root = prepared()
    args = ["--scan", str(root)]
    problems: list[str] = []

    def line_of(label: str, result: Result, whole: str) -> None:
        first = result.stderr.splitlines()[0] if result.stderr else ""
        if result.code != 1 or first != whole or "Markdown writes" in result.stdout + result.stderr:
            problems.append(f"{label}: exit {result.code}: {result.stderr.strip()[:400]}")

    tools = H.scratch_dir()  # a PATH holding only sh and dirname: no python3
    for tool in ("sh", "dirname"):
        found = shutil.which(tool)
        assert found, tool
        (tools / tool).symlink_to(found)
    line_of(
        "C1",
        H.run_gate("", args, env={"PATH": str(tools)}),
        "BROKEN: const-styling needs python3 — fix: install Python 3.12 or newer"
        f" (https://www.python.org/downloads/) — {CLOSING}",
    )
    shadow = H.scratch_dir()  # PyYAML hidden: the shared C2, its closing clause the identity's
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    line_of(
        "C2",
        H.run_gate("", args, env={"PYTHONPATH": str(shadow)}),
        "BROKEN: const-styling needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{MODULE_ROOT / 'requirements.txt'}' — {CLOSING}",
    )
    lowered = (  # the entry file run as an interpreter of 3.11 would run it
        "import sys; sys.version_info = (3, 11, 0); path = sys.argv[1]; "
        "exec(compile(open(path).read(), path, 'exec'), {'__name__': '__main__', '__file__': path})"
    )
    line_of(
        "C14",
        H.run_gate("", args, command=[sys.executable, "-c", lowered, str(H.entry)]),
        "BROKEN: const-styling needs Python 3.12 or newer, found 3.11 — fix: install a current Python 3"
        f" (https://www.python.org/downloads/) and put it first on PATH — {CLOSING}",
    )
    plugin = H.scratch_dir() / "plugin"  # an install that dropped the link to the shared code
    shutil.copytree(SCRIPTS, plugin / "scripts", symlinks=True, ignore=shutil.ignore_patterns("const_gate"))
    line_of(
        "C15",
        H.run_gate("", args, command=[H.sh, str(plugin / "scripts" / H.wrapper.name)]),
        "BROKEN: const-styling is installed without its shared code (scripts/const_gate is missing or is"
        " not a directory) — fix: install the plugin from its marketplace, or load it from a full checkout"
        " of the repository it comes from; a copy of the plugin's folder must be made with links followed"
        f" (cp -RL) — {CLOSING}",
    )
    sources = "".join((SCRIPTS / name).read_text(encoding="utf-8") for name in (H.wrapper.name, H.entry.name))
    if sources.count(CLOSING) != 3 or "Markdown writes" in sources:
        problems.append(
            f"entry files: the clause {sources.count(CLOSING)} times, wanted 3; or Markdown writes"
        )
    return not problems, "; ".join(problems) or "C1, C2, C14 and C15 close with the gate's own clause"


def skill_pointer() -> tuple[bool, str]:
    """The pointer, run through sh: exit 0, the line as typed here and a newline, nothing on stderr; with
    --subagent one JSON object whose hookSpecificOutput is the event name and the line, nothing else; the
    size in characters is the one the module document states; the qualified name names a skill folder."""
    script = str(SCRIPTS / "print-skill-pointer.sh")
    session = subprocess.run([H.sh, script], capture_output=True, text=True, check=False)
    if session.returncode != 0 or session.stdout != POINTER + "\n" or session.stderr != "":
        return False, repr(session)
    subagent = subprocess.run([H.sh, script, "--subagent"], capture_output=True, text=True, check=False)
    if subagent.returncode != 0 or subagent.stderr != "" or not subagent.stdout.endswith("\n"):
        return False, repr(subagent)
    printed = json.loads(subagent.stdout)
    wanted = {"hookEventName": "SubagentStart", "additionalContext": POINTER}
    if list(printed) != ["hookSpecificOutput"] or printed["hookSpecificOutput"] != wanted:
        return False, f"the subagent form differs: {subagent.stdout}"
    size = len(POINTER)
    stated = re.search(
        r"pointer line, (\d+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    if not stated or int(stated.group(1)) != size:
        return False, f"the module document states another size than {size}"
    named = re.search(r"load the skill (const-styling):([a-z-]+)\.$", POINTER)
    if not named or not (MODULE_ROOT / "skills" / named.group(2) / "SKILL.md").is_file():
        return False, "the qualified skill name in the line names no folder under skills/"
    return (
        True,
        f"exit 0, the line as typed, {size} characters as the module document states, JSON form exact",
    )


def hooks_file() -> tuple[bool, str]:
    """The hooks file holds the two advisory handlers and nothing else: SessionStart and SubagentStart,
    each without a matcher, exec form sh, the script in args (the second with --subagent), an integer
    timeout, the script present."""
    hooks = json.loads((MODULE_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    pointer = "${CLAUDE_PLUGIN_ROOT}/scripts/print-skill-pointer.sh"
    wanted = {"SessionStart": [pointer], "SubagentStart": [pointer, "--subagent"]}
    problems = [name for name in wanted if name not in hooks] + [name for name in hooks if name not in wanted]
    for name, args in wanted.items():
        groups = hooks.get(name, [])
        if len(groups) != 1:
            problems.append(f"{name}: {len(groups)} handler(s)")
        for group in groups:
            handler = group["hooks"][0]
            right = (
                "matcher" not in group
                and len(group["hooks"]) == 1
                and handler.get("type") == "command"
                and handler.get("command") == "sh"
                and handler.get("args") == args
                and isinstance(handler.get("timeout"), int)
                and (SCRIPTS / Path(args[0]).name).is_file()
            )
            if not right:
                problems.append(f"{name}: {group}")
    return (
        not problems,
        "SessionStart and SubagentStart, no matcher, exec form, integer timeouts, the script present"
        if not problems
        else str(problems),
    )


# ---------------------------------------------------------------- the twelve red→green cases


def case(number: int, signature: Signature, red_text: str, line: int, echo: str, green_text: str) -> Case:
    """One signature: a document carrying it once is red with the finding whole and the count line
    typed by hand; a document without it is green with the whole tail."""
    hit = Hit(signature, line, echo)
    return Case(
        number,
        f"red→green: {signature.value}",
        Write("docs/notes/c.md", red_text),
        Write("docs/notes/c.md", green_text),
        messages.finding("docs/notes/c.md", hit),
        tail(4),
        count=f"RED: 1 finding(s) — {tail(4)}",
    )


CASES = [
    case(21, Signature.PLANTUML, PLANTUML_FENCE, 3, "```plantuml", MERMAID),
    case(22, Signature.FORMULA, "# T\n\n$$ x $$\n", 3, "$$ x $$", "# T\n\n```text\nx = y\n```\n"),
    case(23, Signature.CALLOUT, "# T\n\n> [!NOTE]\n", 3, "> [!NOTE]", "# T\n\n> quoted\n"),
    case(24, Signature.DEEP_HEADING, "# T\n\n## A\n\n### B\n\n#### C\n", 7, "4", "# T\n\n## A\n\n### B\n"),
    case(25, Signature.SKIPPED_LEVEL, "# T\n\n### B\n", 3, "3", "# T\n\n## B\n"),
    case(26, Signature.SECOND_H1, "# T\n\n# U\n", 3, "U", "# T\n\n## U\n"),
    case(27, Signature.FENCE_LANGUAGE, "# T\n\n```\nx\n```\n", 3, "", "# T\n\n```text\nx\n```\n"),
    case(28, Signature.LIST_MARKER, "# T\n\n* a\n", 3, "a", "# T\n\n- a\n"),
    case(29, Signature.LIST_NUMBERING, "# T\n\n1. a\n3. b\n", 4, "3 after 1", "# T\n\n1. a\n2. b\n"),
    case(30, Signature.UNDERSCORE_EMPHASIS, "# T\n\n_a_\n", 3, "a", "# T\n\n*a*\n"),
    case(
        31,
        Signature.TABLE_COLUMNS,
        "# T\n\n| k | v |\n|---|---|\n| a |\n",
        5,
        "1 cell(s) under a header of 2",
        "# T\n\n| k | v |\n|---|---|\n| a | b |\n",
    ),
    case(
        32,
        Signature.TABLE_EMPTY_CELL,
        "# T\n\n| k | v |\n|---|---|\n| a | |\n",
        5,
        "2",
        "# T\n\n| k | v |\n|---|---|\n| a | none |\n",
    ),
]


# ---------------------------------------------------------------- the list

ITEMS: list[tuple[int, str, Callable[[], tuple[bool, str]]]] = [
    (1, "PlantUML is red with Y1 typed whole, Mermaid green, a departure by path allows it", t1),
    (2, "a math fence and a $$ line are red; pseudocode is green; $$ in code is code", t2),
    (3, "an alert line is red; a plain blockquote is green", t3),
    (4, "a fourth heading level is red, twice when it also skips; three levels are green", t4),
    (5, "a skipped level and a second H1 are red; stepping back up is green", t5),
    (
        6,
        "a fence without a language is red; text, nested, attributed and indented fences green",
        t6,
    ),
    (7, "star and plus items are red; dashes, a bold line and a rule are green", t7),
    (8, "all-ones and a jump are red; counting on from anywhere, a new list, nesting green", t8),
    (9, "underscore emphasis is red; names, words, code spans and stars are green", t9),
    (10, "a short row, an empty cell and a short delimiter row are red; a keyed table green", t10),
    (11, "departures: by territory, by path, one signature at a time; a stale entry is a note", t11),
    (12, "territories: a negated pattern drops the count; a README at the top; guides validated", t12),
    (13, "this module's C5 lines typed by hand, each exit 1", t13),
    (14, "the scan as a hook is its own C12; a misinvocation exits 1", t14),
    (15, "golden lines: the twelve headlines typed whole, in line order; a clean document green", t15),
    (16, "an echoed item of 12,000 characters is cut, and the cut is said", t16),
    (17, "the shipped guide passes its own scan with ten entries; the skill's description size", t17),
    (18, "the manifest names the plugin; the install note's example accepted and describes the keys", t18),
    (19, "golden lines: the why and the fix of every finding typed whole", t19),
    (20, "C1, C2, C14 and C15 close with the gate's own clause, and the entry files carry it", t20),
    (
        33,
        "the session-start and subagent pointer as typed, its size stated, the skill it names present",
        skill_pointer,
    ),
    (
        34,
        "the hooks file holds the two advisory handlers: SessionStart and SubagentStart, exec form",
        hooks_file,
    ),
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
    pattern_dial=PatternDial("territories", lambda pattern: own(territories=[pattern])),
    skill="style-defaults",  # the skill a red names (F10), typed by hand
)


def main() -> int:
    assertions = [Assertion(number, title, check) for number, title, check in ITEMS]
    return H.run_all(CASES, [*assertions, *shared_assertions(SUBJECT, 101)])


if __name__ == "__main__":
    sys.exit(main())
