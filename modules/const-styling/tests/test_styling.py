"""Fixtures of const-styling: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.

One entry point is driven, the scan, through the shared items and its own. The gate has no
hook mode, so the shared items run with the subject's `scan_only` flag: the items about hook
input, a written file, the warn channel and a negated pattern's skip are skipped with their
numbers kept free, and the rest run the scan on the prepared consumer; the twelve red→green
cases run through the harness's scan-only shape, each half a document written and scanned. The
fixture consumer is the shared one; this module resolves no policy and judges no envelope, so
the shared items about the root policy and about an unreadable envelope are skipped too.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Sequence
from functools import partial
from pathlib import Path

import pytest
import yaml
from constitution_layer_kit.testing.acceptance import broken_first_line, check_case, expect, failure_of, item
from constitution_layer_kit.testing.consumer import BASE_MARKDOWN, Consumer
from constitution_layer_kit.testing.harness import Case, Harness, Result, Write, bash_json, red_lines
from constitution_layer_kit.testing.items import PatternDial, Subject, fake_claude, tr_line
from styling_gate import messages, start
from styling_gate.model import Hit, Signature

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"
PLUGIN_ROOT = SCRIPTS.parent
MODULE_ROOT = PLUGIN_ROOT.parent

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
# — and each is also typed by hand at least once in these fixtures (rule 14 of the gate-script rules)
H = Harness(SCRIPTS, "check-style.sh", "check-style.py", start.GATE.namespace, scan_only=True)
NAMESPACE = start.GATE.namespace
SIGNATURES = len(Signature)
GUIDE = PLUGIN_ROOT / "skills" / "style-defaults" / "style-guide.md"
SKILL = PLUGIN_ROOT / "skills" / "style-defaults" / "SKILL.md"


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


def headlines(result: Result) -> list[str]:
    """The RED lines but the count line: the findings' headlines."""
    return red_lines(result.stdout)[:-1]


def one_finding(files: dict[str, str], headline: str, dials_patch: dict[str, object] | None = None) -> None:
    result = scan(files, dials_patch)
    lines = headlines(result)
    ok = result.code == 2 and lines == [f"RED: {headline}"]
    assert ok, f"exit {result.code}: {result.stdout.strip()}"


def no_finding(
    files: dict[str, str], dials_patch: dict[str, object] | None = None, departures: int = 0
) -> None:
    result = scan(files, dials_patch)
    expect(result, 0, green(BASE_MARKDOWN + len(files), departures), "stdout")


# ---------------------------------------------------------------- the twelve signatures

PLANTUML_FENCE = "# T\n\n```plantuml\n@startuml\nA -> B\n@enduml\n```\n"
PLANTUML_BARE = "# T\n\n```text\n@startuml\nA -> B\n@enduml\n```\n"
MERMAID = "# T\n\n```mermaid\nflowchart LR\n  A --> B\n```\n"


@item(1, "PlantUML is red with Y1 typed whole, Mermaid green, a departure by path allows it")
def test_t1() -> None:
    """Y1 typed whole for a `plantuml` fence, for a `puml` fence, for `@startuml` inside a `text`
    fence and for `@startuml` outside any fence; a Mermaid fence green; a departure by path makes
    the same document green and the count says one departure"""
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
    one_finding(
        {"docs/notes/d.md": PLANTUML_BARE},
        "docs/notes/d.md:4: PlantUML, where the shipped default is Mermaid — @startuml",
    )
    one_finding(
        {"docs/notes/d.md": "# T\n\n@startuml\nA -> B\n@enduml\n"},
        "docs/notes/d.md:3: PlantUML, where the shipped default is Mermaid — @startuml",
    )
    one_finding(
        {"docs/notes/d.md": "# T\n\n```puml\nA -> B\n```\n"},
        "docs/notes/d.md:3: PlantUML, where the shipped default is Mermaid — ```puml",
    )
    no_finding({"docs/notes/d.md": MERMAID})
    departure = [{"paths": ["/docs/notes/d.md"], "allow": ["plantuml"], "reason": "a timing diagram"}]
    allowed = scan({"docs/notes/d.md": PLANTUML_FENCE}, own(departures=departure))
    expect(allowed, 0, green(4, 1), "stdout")
    assert red_ok, f"differs (exit {result.code}):\n{result.stdout}"


@item(2, "a math fence and a $$ line are red; pseudocode is green; $$ in code is code")
def test_t2() -> None:
    """red and green: a math fence and a $$ line are red (Y2); a pseudocode fence is green; $$ inside a
    fence of another language is code."""
    one_finding(
        {"docs/notes/f.md": "# T\n\n```math\nE = mc^2\n```\n"},
        "docs/notes/f.md:3: a formula, where the shipped default is pseudocode — ```math",
    )
    one_finding(
        {"docs/notes/f.md": "# T\n\n$$ E = mc^2 $$\n"},
        "docs/notes/f.md:3: a formula, where the shipped default is pseudocode — $$ E = mc^2 $$",
    )
    no_finding({"docs/notes/f.md": "# T\n\n```text\nenergy = mass * c * c\n```\n\n```bash\necho $$\n```\n"})


@item(3, "an alert line is red; a plain blockquote is green")
def test_t3() -> None:
    """red and green: an alert line is red (Y3); a plain blockquote is green."""
    one_finding(
        {"docs/notes/c.md": "# T\n\n> [!NOTE]\n> Careful.\n"},
        "docs/notes/c.md:3: a callout, where the shipped default is none — > [!NOTE]",
    )
    no_finding({"docs/notes/c.md": "# T\n\n> A quoted reply, as it was written.\n"})


@item(4, "a fourth heading level is red, twice when it also skips; three levels are green")
def test_t4() -> None:
    """Y4 for a level-four heading; one that also skips a level is Y4 and Y5 on one line; three
    levels in order, a closing hash sequence, a heading inside a fence and a heading indented four
    spaces green; one departure for `deep-heading` over the whole tree makes a level-six heading
    green, the limit 9 of [§9](#t9)"""
    one_finding(
        {"docs/notes/h.md": "# T\n\n## A\n\n### B\n\n#### C\n"},
        "docs/notes/h.md:7: a heading of level 4, deeper than the shipped default of three",
    )
    both = scan({"docs/notes/h.md": "# T\n\n## A\n\n#### C\n"})
    both_ok = headlines(both) == [
        "RED: docs/notes/h.md:5: a heading of level 4, deeper than the shipped default of three",
        "RED: docs/notes/h.md:5: a heading of level 4, skipping a level",
    ]
    no_finding(
        {
            "docs/notes/h.md": "# T\n\n## A ##\n\n### B\n\n```text\n#### not a heading\n```\n\n"
            "    #### nor this\n"
        }
    )
    whole_tree = [
        {"paths": ["*.md"], "allow": ["deep-heading"], "reason": "our guide allows four levels (entry 7)"}
    ]
    no_finding(
        {"docs/notes/h.md": "# T\n\n## A\n\n### B\n\n#### C\n\n##### D\n\n###### E\n"},
        own(departures=whole_tree),
        departures=1,
    )
    assert both_ok, both.stdout


@item(5, "a skipped level and a second H1 are red; stepping back up is green")
def test_t5() -> None:
    """Y5 for a level-three heading under the title; Y6 for a second level-one heading, after a
    byte-order mark before the title, and right after a fence closes; stepping back up by any number
    green"""
    one_finding(
        {"docs/notes/s.md": "# T\n\n### B\n"}, "docs/notes/s.md:3: a heading of level 3, skipping a level"
    )
    one_finding(
        {"docs/notes/s.md": "# T\n\n## A\n\n# Another title\n"},
        "docs/notes/s.md:5: a second level-one heading — Another title",
    )
    no_finding({"docs/notes/s.md": "# T\n\n## A\n\n### B\n\n## C\n"})
    one_finding(
        {"docs/notes/s.md": "\ufeff# T\n\n# U\n"}, "docs/notes/s.md:3: a second level-one heading — U"
    )
    one_finding(
        {"docs/notes/s.md": "# T\n\n```text\nx\n```\n# U\n"},
        "docs/notes/s.md:6: a second level-one heading — U",
    )


@item(6, "a fence without a language is red; text, nested, attributed and indented fences green")
def test_t6() -> None:
    """Y7 for a backtick fence and for a tilde fence with no language; `text`, a nested fence closed
    by a longer one, an info string with attributes, a fence indented inside a list item and under a
    nested item, and a fence that a fence with an info string does not close, green"""
    one_finding(
        {"docs/notes/k.md": "# T\n\n```\nls\n```\n"},
        "docs/notes/k.md:3: a fenced block that names no language",
    )
    one_finding(
        {"docs/notes/k.md": "# T\n\n~~~\nls\n~~~\n"},
        "docs/notes/k.md:3: a fenced block that names no language",
    )
    no_finding(
        {
            "docs/notes/k.md": "# T\n\n```text\ntree\n```\n\n````markdown\n```\nnested\n```\n````\n\n"
            "```python {.numberLines}\nx = 1\n```\n\n- item\n\n   ```bash\n   ls\n   ```\n\n"
            "```text\n```bash\n* not an item\n```\n\n- one\n  - two\n\n      ```text\n      * nor this\n"
            "      ```\n"
        }
    )


@item(7, "star and plus items are red; dashes, a bold line and a rule are green")
def test_t7() -> None:
    """Y8 for a star item, a nested plus item, and a star item after a line that looks like a fence
    but carries a backtick in its info string; dashes, a bold line and a horizontal rule green; an
    item of 105 characters holding backslashes, cut at 80 with the cut said, then escaped; a path of
    over 80 characters with a line break, whole and escaped in the headline"""
    one_finding(
        {"docs/notes/l.md": "# T\n\n* one\n- two\n"},
        "docs/notes/l.md:3: a bullet item whose marker is not the shipped default, a dash — one",
    )
    one_finding(
        {"docs/notes/l.md": "# T\n\n- one\n  + nested\n"},
        "docs/notes/l.md:4: a bullet item whose marker is not the shipped default, a dash — nested",
    )
    no_finding({"docs/notes/l.md": "# T\n\n- one\n- two\n\n**bold** at the start\n\n***\n"})
    one_finding(
        {"docs/notes/l.md": "# T\n\n``` x`y\n* star\n"},
        "docs/notes/l.md:4: a bullet item whose marker is not the shipped default, a dash — star",
    )
    one_finding(  # the echoed text holds backslashes and runs to 105 characters: cut at 80, then escaped
        {"docs/notes/l.md": "# T\n\n* a\\b\\c" + "x" * 100 + "\n"},
        "docs/notes/l.md:3: a bullet item whose marker is not the shipped default, a dash — a\\\\b\\\\c"
        + "x" * 75
        + "… [105 characters]",
    )
    one_finding(  # the path whole in the headline, over 80 characters, its break and backslash escaped
        {WEIRD: "# T\n\n* one\n"},
        WEIRD_SHOWN + ":3: a bullet item whose marker is not the shipped default, a dash — one",
    )


@item(8, "all-ones and a jump are red; counting on from anywhere, a new list, nesting green")
def test_t8() -> None:
    """Y9 for all-ones numbering and for a jump; a list starting at 101, a new list after a
    paragraph, a nested ordered list counting on its own, a bullet inside an ordered list, a change
    of delimiter, a list restarting under the same delimiter after a heading, and one starting
    anywhere after a fence green"""
    one_finding(
        {"docs/notes/n.md": "# T\n\n1. a\n1. b\n2. c\n"},
        "docs/notes/n.md:4: an ordered item numbered 1 after 1",
    )
    one_finding(
        {"docs/notes/n.md": "# T\n\n1. a\n3. b\n"}, "docs/notes/n.md:4: an ordered item numbered 3 after 1"
    )
    no_finding(
        {
            "docs/notes/n.md": "# T\n\n101. a\n102. b\n\nA paragraph.\n\n1. a\n   1. nested\n"
            "   2. nested\n2. b\n   - bullet\n3. c\n\n1) a\n2) b\n\n## H\n\n1) again\n"
        }
    )
    no_finding({"docs/notes/n.md": "# T\n\n1. one\n```text\nx\n```\n5. five\n"})


@item(9, "underscore emphasis is red; names, words, code spans and stars are green")
def test_t9() -> None:
    """Y10 for `_italic_` and `__bold__`, and inside a link's text; a snake-case name, an underscore
    inside a word, a code span, asterisks, a link's destination absolute or relative, a bare URL, an
    autolink and an HTML comment on one line or across lines green; a comment opener inside a fence
    or a code span hides nothing after it, a closer inside a code span closes and the comment is
    masked, a second opener after a closed comment opens, and a comment's closing line is hidden
    whole"""
    one_finding(
        {"docs/notes/e.md": "# T\n\nSome _quiet_ words.\n"},
        "docs/notes/e.md:3: emphasis by underscores — quiet",
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\nSome __loud__ words.\n"},
        "docs/notes/e.md:3: emphasis by underscores — loud",
    )
    no_finding(
        {
            "docs/notes/e.md": "# T\n\nsnake_case_name, `__init__`, a_b_c and *fine* and **fine**, x_ y_z.\n"
            "[text](https://e.com/_p_/y) and [x](docs/_p_.md) and https://e.com/_p_/y and <https://e.com/_p_/>"
            " <!-- _c_ -->\n<!--\n_hidden_\n```\n-->\n```markdown\n<!-- opens in a fence\n```\n\n"
            "The opener `<!--` in a code span.\n"
        }
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\n[_text_](https://e.com/_p_/y)\n"},
        "docs/notes/e.md:3: emphasis by underscores — text",
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\n```markdown\n<!-- x\n```\n\n__after__\n"},
        "docs/notes/e.md:7: emphasis by underscores — after",
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\nThe opener `<!--` starts a comment.\n\n__after__\n"},
        "docs/notes/e.md:5: emphasis by underscores — after",
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\n<!--\n_hidden_\n--> _raw_\n__shown__\n"},
        "docs/notes/e.md:6: emphasis by underscores — shown",
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\n<!-- _a_ `-->` b\n__after__\n"},
        "docs/notes/e.md:4: emphasis by underscores — after",
    )
    one_finding(
        {"docs/notes/e.md": "# T\n\nt <!-- a --> _x_ <!-- b\n_hidden_\n-->\n"},
        "docs/notes/e.md:3: emphasis by underscores — x",
    )


@item(10, "a short row, an empty cell and a short delimiter row are red; a keyed table green")
def test_t10() -> None:
    """Y11 for a row with a cell too few and for a short delimiter row; Y12 for an empty cell; a
    keyed table with an escaped pipe and `none`, lines with pipes and no delimiter row, a dash line
    without a pipe under a line with one, and a short row after a comment that opens on a row and
    runs on, which ends the table, green"""
    one_finding(
        {"docs/notes/t.md": "# T\n\n| key | value |\n|---|---|\n| a |\n"},
        "docs/notes/t.md:5: a table row with 1 cell(s) under a header of 2",
    )
    one_finding(
        {"docs/notes/t.md": "# T\n\n| key | value |\n|---|---|\n| a | |\n"},
        "docs/notes/t.md:5: an empty cell in column 2",
    )
    one_finding(
        {"docs/notes/t.md": "# T\n\n| key | value |\n|---|\n| a | b |\n"},
        "docs/notes/t.md:4: a table row with 1 cell(s) under a header of 2",
    )
    no_finding(
        {
            "docs/notes/t.md": "# T\n\n| key | value |\n|:---|---:|\n| a | x \\| y |\n| b | none |\n\n"
            "a | b\nc | d\n\ncell | text\n---\n\n| one |\n"
        }
    )
    no_finding({"docs/notes/t.md": "# T\n\n| a | b |\n|---|---|\n| 1 | 2 | <!-- open\nhidden\n-->\n| x |\n"})


# ---------------------------------------------------------------- departures and territories


@item(11, "departures: by territory, by path, one signature at a time; a stale entry is a note")
def test_t11() -> None:
    """Departures: an entry by territory allows every document there; one by path allows that
    document alone; an entry allowing one signature does not allow another; a stale entry is N2,
    typed by hand, first on stdout, and the scan green; an entry over documents a negated pattern
    took out of the territory is stale too; a stale pattern of 110 characters with a backslash is
    cut at 80 with the cut said, then escaped"""
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
    expect(other, 2, red(1, 4, 1), "stdout")
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
    assert territory_ok, by_territory.stdout
    assert path_ok, by_path.stdout
    assert stale_ok, f"{stale.code}: {stale.stdout}"
    assert outside_ok, outside.stdout
    assert cut_ok, cut.stdout


@item(12, "territories: a negated pattern drops the count; a README at the top; guides validated")
def test_t12() -> None:
    """Territories: a negated pattern takes a document out and the count drops; the default covers a
    README at the top; the guides dial is validated and changes no verdict."""
    out = scan({"docs/notes/a.md": PLANTUML_FENCE}, own(territories=["*.md", "!docs/notes/**"]))
    expect(out, 0, green(3, scanned=4), "stdout")
    one_finding(
        {"README.md": PLANTUML_FENCE},
        "README.md:3: PlantUML, where the shipped default is Mermaid — ```plantuml",
    )
    no_finding({"docs/notes/a.md": MERMAID}, own(guides=["docs/style/**"]))


@item(13, "this module's C5 lines typed by hand, each exit 1")
def test_t13() -> None:
    """This module's C5 lines typed by hand — a key that is no dial, `severity`, `territories`
    empty, `guides` not a list, `departures` not a list, an entry not a mapping, an unknown field,
    `paths` empty, a pattern git would misread in `territories`, in `guides` with its line break
    shown escaped, and in `paths`, an unknown signature key, an empty reason, a reason broken by a
    line feed or a carriage return — each exit 1. A reason with a line break at its end is taken,
    trimmed"""
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
    problems = [
        said
        for patch, line in cases
        if (said := failure_of(partial(broken_first_line, scan({"docs/notes/a.md": MERMAID}, patch), line)))
        is not None
    ]
    # what `reason: |` gives, a line break at the end: trimmed and taken, as in the other two gates
    block_scalar = own(departures=[{"paths": ["docs/gone/**"], "allow": ["plantuml"], "reason": "why\n"}])
    block_said = failure_of(lambda: no_finding({"docs/notes/a.md": MERMAID}, block_scalar, departures=1))
    problems.extend([] if block_said is None else [block_said])
    assert not problems, "; ".join(problems)


@item(14, "the scan as a hook is its own C12; a misinvocation exits 1")
def test_t14() -> None:
    """The scan run as a hook is its own C12, typed by hand; a misinvocation exits 1."""
    root = prepared()
    hook = H.run_gate(bash_json(root, "ls"))
    broken_first_line(
        hook,
        "BROKEN: this check has no hook mode: it scans a tree and judges no single write — fix: run it with"
        " --scan [<dir>]; the plugin wires it to no event",
    )
    mis = H.run_gate("", args=["--bogus"])
    expect(mis, 1, "BROKEN: misinvocation:", "stderr")


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


@item(15, "golden lines: the twelve headlines typed whole, in line order; a clean document green")
def test_t15() -> None:
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
    no_finding({"docs/notes/g.md": MERMAID})
    long_path = scan(
        {WEIRD: GOLDEN}
    )  # the path of over 80 characters, whole and escaped, in all twelve headlines
    long_ok = (
        long_path.code == 2
        and len(headlines(long_path)) == 12
        and all(line.startswith("RED: " + WEIRD_SHOWN + ":") for line in headlines(long_path))
    )
    assert ok, result.stdout
    assert long_ok, long_path.stdout[:600]


@item(16, "an echoed item of 12,000 characters is cut, and the cut is said")
def test_t16() -> None:
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
    assert ok, result.stdout[:300]
    assert odd_ok, odd.stdout[:1500]


# ---------------------------------------------------------------- golden lines


@item(19, "golden lines: the why and the fix of every finding typed whole")
def test_t19() -> None:
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
    assert ok, "\n".join(f"{a}\n{b}" for a, b in zip(got, wanted, strict=False) if a != b)[:1500]


# ---------------------------------------------------------------- the shipped files


@item(17, "the shipped guide passes its own scan with ten entries; the skill's description size")
def test_t17() -> None:
    """The shipped guide, placed in a consumer as its guide, passes the scan it describes; it
    carries entries d1 to d10; the skill's description is under the platform's cap and of the size
    [§6](#t6) states — the number read from this document"""
    guide = GUIDE.read_text(encoding="utf-8")
    no_finding({"docs/style-guide.md": guide})
    entries = re.findall(r"^\d+\. <a id=\"d(\d+)\"></a>\*\*", guide, flags=re.M)
    entries_ok = entries == [str(n) for n in range(1, 11)]
    front = SKILL.read_text(encoding="utf-8").split("---")[1]
    description = str(yaml.safe_load(front)["description"]).strip()
    stated = re.search(
        r"description of ([0-9,]+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    size_ok = stated is not None and int(stated.group(1).replace(",", "")) == len(description) <= 1536
    assert entries_ok, f"entries {entries}"
    assert size_ok, f"description {len(description)}, stated {stated and stated.group(1)}"


@item(18, "the manifest names the plugin; the install note's example accepted and describes the keys")
def test_t18() -> None:
    """The manifest names the plugin; the install note's calibration example is accepted as it stands and
    describes the twelve keys."""
    texts = {"INSTALL.md": (PLUGIN_ROOT / "INSTALL.md").read_text(encoding="utf-8")}
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    manifest_ok = manifest["name"] == NAMESPACE and manifest["version"].startswith("0.0.")
    example = re.search(r"```yaml\n((?:.*\n)*?)[ ]*```", texts["INSTALL.md"])
    example_ok = False
    keys_ok = all(s.value in texts["INSTALL.md"] for s in Signature)
    if example:
        patch = yaml.safe_load(textwrap.dedent(example.group(1)))
        result = scan({"docs/notes/a.md": MERMAID, ".gitignore": ""}, patch)
        example_ok = result.code == 0
    assert manifest_ok, "manifest names the plugin, a draft version"
    assert example_ok, "the example is refused or missing"
    assert keys_ok, "the twelve keys named in the install note"


CLOSING = "until then no document is scanned for style"


@item(20, "C1, C2, C14 and C15 close with the gate's own clause, and the entry files carry it")
def test_t20() -> None:
    """The install-failure lines close with this gate's own clause, never the write gates': C1 with
    no `python3` on `PATH`, C2 with PyYAML hidden, C14 with the entry file run as an interpreter of
    3.11, C15 with the entry file run under `python3 -S` and the shared folder left out, the shared
    package missing for python3, each first line typed whole. The entry files hold the clause
    exactly four times, once per entry text (C1, C14, C15) and once as the clause handed to the
    version check of the shared package (C16, C17), and "Markdown writes" nowhere"""
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
        f" '{PLUGIN_ROOT / 'requirements.txt'}' — {CLOSING}",
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
    line_of(
        "C15",
        H.run_gate(  # the harness's shared folder left out, and no site-packages
            "", args, env={"PYTHONPATH": ""}, command=[sys.executable, "-S", str(H.entry)], shared=False
        ),
        "BROKEN: const-styling needs the Python package constitution-layer-kit 2.1.0 or a later 2.x release,"
        " and python3 cannot import it — fix: install it for python3 as"
        f" {PLUGIN_ROOT / 'INSTALL.md'} says — {CLOSING}",
    )
    sources = "".join((SCRIPTS / name).read_text(encoding="utf-8") for name in (H.wrapper.name, H.entry.name))
    if sources.count(CLOSING) != 4 or "Markdown writes" in sources:
        problems.append(
            f"entry files: the clause {sources.count(CLOSING)} times, wanted 4; or Markdown writes"
        )
    assert not problems, "; ".join(problems)


@item(33, "the session-start and subagent pointer as typed, its size stated, the skill it names present")
def test_skill_pointer() -> None:
    """The pointer, run through sh: exit 0, the line as typed here and a newline, nothing on stderr; with
    --subagent one JSON object whose hookSpecificOutput is the event name and the line, nothing else; the
    size in characters is the one the module document states; the qualified name names a skill folder."""
    script = str(SCRIPTS / "print-skill-pointer.sh")
    session = subprocess.run([H.sh, script], capture_output=True, text=True, check=False)
    if session.returncode != 0 or session.stdout != POINTER + "\n" or session.stderr != "":
        pytest.fail(repr(session))
    subagent = subprocess.run([H.sh, script, "--subagent"], capture_output=True, text=True, check=False)
    if subagent.returncode != 0 or subagent.stderr != "" or not subagent.stdout.endswith("\n"):
        pytest.fail(repr(subagent))
    printed = json.loads(subagent.stdout)
    wanted = {"hookEventName": "SubagentStart", "additionalContext": POINTER}
    if list(printed) != ["hookSpecificOutput"] or printed["hookSpecificOutput"] != wanted:
        pytest.fail(f"the subagent form differs: {subagent.stdout}")
    size = len(POINTER)
    stated = re.search(
        r"pointer line, (\d+) characters", (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    )
    if not stated or int(stated.group(1)) != size:
        pytest.fail(f"the module document states another size than {size}")
    named = re.search(r"load the skill (const-styling):([a-z-]+)\.$", POINTER)
    if not named or not (PLUGIN_ROOT / "skills" / named.group(2) / "SKILL.md").is_file():
        pytest.fail("the qualified skill name in the line names no folder under skills/")


@item(34, "the hooks file holds the two advisory handlers: SessionStart and SubagentStart, exec form")
def test_hooks_file() -> None:
    """The hooks file holds the two advisory handlers and nothing else: SessionStart and SubagentStart,
    each without a matcher, exec form sh, the script in args (the second with --subagent), an integer
    timeout, the script present."""
    hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
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
    assert not problems, str(problems)


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


@pytest.mark.parametrize(
    "case", [pytest.param(case, id=f"T{case.number}", marks=item(case.number, case.title)) for case in CASES]
)
def test_case(case: Case) -> None:
    check_case(H, case)


# ---------------------------------------------------------------- the list

# ---------------------------------------------------------------- the effect report (items 35 to 37)
# Each rule of the module's section "Effect" runs through the real entry `effect-report.sh` over transcripts
# made by hand and, for the history rules, a scratch git repository. The lines asserted are typed by hand.

EFFECT = SCRIPTS / "effect-report.sh"
WAY_AT = "2026-11-03T10:00:00.000Z"
SKILL_NAME = "const-styling:style-defaults"


def tr_tool(sid: str, cwd: Path, call_id: str, name: str, **given: object) -> str:
    """A tool call of any tool, with its input as given."""
    block = {"type": "tool_use", "id": call_id, "name": name, "input": given}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def effect_lines(root: Path, sessions: dict[str, list[str]], env: dict[str, str] | None = None) -> list[str]:
    """The lines of the report over the sessions, one transcript each; the report must exit 0."""
    folder = H.scratch_dir()
    for name, lines in sessions.items():
        (folder / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder)],
        env={"CLAUDE_PLUGIN_DATA": str(H.scratch_dir()), **(env or {})},
        command=[H.sh, str(EFFECT)],
        cwd=root,
    )
    assert result.code == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def no_plugins(listed: str = "[]") -> dict[str, str]:
    """The environment of a fake `claude` that lists `listed` as its plugins."""
    return fake_claude(H.scratch_dir(), f"echo {shlex.quote(listed)}\n")


def departure(path: str, *allow: str, reason: str = "the diagram is the point") -> dict[str, object]:
    return {"paths": [path], "allow": list(allow), "reason": reason}


@item(35, "W1: the plugin disabled, or a departure widened or a guide dropped, is bypassed by B2")
def test_effect_switch_off() -> None:
    """Ten commits of the dials file, the namespace changed at each: a territory only (applied); a departure
    added (bypassed); its signatures widened (bypassed); its reason reworded (applied); a second path
    allowed (bypassed); the first departure removed (applied); a guide added (applied); the guide dropped
    (bypassed); the last departure removed (applied); a namespace this module cannot read (applied: read
    as no change). A fake plugin list that lists the gate for this project disabled adds one more,
    bypassed. The lines are typed by hand."""
    consumer = H.fresh_consumer()
    root = consumer.root
    steps = [
        own(territories=["*.md"]),
        own(departures=[departure("docs/a.md", "plantuml")]),
        own(departures=[departure("docs/a.md", "plantuml", "formula")]),
        own(departures=[departure("docs/a.md", "plantuml", "formula", reason="another reason")]),
        own(departures=[departure("docs/a.md", "plantuml", "formula"), departure("docs/b.md", "callout")]),
        own(departures=[departure("docs/b.md", "callout")]),
        own(departures=[departure("docs/b.md", "callout")], guides=["docs/guide.md"]),
        own(departures=[departure("docs/b.md", "callout")]),
        own(departures=[]),
        own(departures="not a list"),
    ]
    for step in steps:
        consumer.write_dials(step)
        consumer.commit()
    found = effect_lines(root, {}, no_plugins())
    assert "  W1 (pattern): 10 moment(s): 6 applied, 4 bypassed, 0 missed — B2 4" in found, found
    disabled = json.dumps([{"id": f"{NAMESPACE}@m", "enabled": False, "projectPath": str(root)}])
    again = effect_lines(root, {}, no_plugins(disabled))
    assert "  W1 (pattern): 11 moment(s): 6 applied, 5 bypassed, 0 missed — B2 5" in again, again


@item(36, "W2: the scan on each commit of main in a throwaway clone: green applied, a trace bypassed by B4")
def test_effect_escape() -> None:
    """Three commits of `main`: the fixture, a document that holds a PlantUML block (the scan is red there),
    and the document without it. The module's own scan runs on a shared clone at each, outside the project,
    which stays as it was. The line is typed by hand."""
    consumer = H.fresh_consumer()
    consumer.git("branch", "-M", "main")
    consumer.write("docs/notes/a.md", PLANTUML_FENCE)
    consumer.commit()
    consumer.write("docs/notes/a.md", "# T\n\n- a\n")
    consumer.commit()
    root = consumer.root
    status = ["git", "status", "--porcelain", "--ignored"]
    before = subprocess.run(status, cwd=root, capture_output=True, text=True)
    found = effect_lines(root, {}, no_plugins())
    assert "  W2 (pattern): 3 moment(s): 2 applied, 1 bypassed, 0 missed — B4 1" in found, found
    after = subprocess.run(status, cwd=root, capture_output=True, text=True)
    assert after.stdout == before.stdout, (before.stdout, after.stdout)


@item(
    37, "W3: a write with a table, a fence, a deep heading or a list is applied after the skill, else missed"
)
def test_effect_skill_before_write() -> None:
    """A Write or an Edit of a Markdown file whose new content holds a table, a fenced block, a heading of
    level four, a bullet or a numbered item is a moment: applied where a Skill call for style-defaults, in
    full or bare, came earlier in the session; missed by B5 with no load, with a load of another skill, or
    with the load after the write. A MultiEdit counts by its edits. Prose, a heading of level three, pipes
    with no delimiter row, a rule, and a list written into a file that is no Markdown are no moment. The
    line is typed by hand."""
    root = H.fresh_consumer().root
    doc = str(root / "docs" / "a.md")
    table = "| k | v |\n|---|---|\n| a | b |\n"
    fence = "```text\nx\n```\n"

    def write(sid: str, call_id: str, content: str, tool: str = "Write", path: str = doc) -> str:
        key = "content" if tool == "Write" else "new_string"
        return tr_tool(sid, root, call_id, tool, file_path=path, **{key: content})

    def skill(sid: str, name: str) -> str:
        return tr_tool(sid, root, "k" + name, "Skill", skill=name)

    sessions = {
        "s37a": [skill("s37a", "style-defaults"), write("s37a", "w1", table), write("s37a", "w2", fence)],
        "s37b": [skill("s37b", SKILL_NAME), write("s37b", "w1", "- a\n")],
        "s37c": [
            write("s37c", "w1", table),
            write("s37c", "w2", fence),
            write("s37c", "w3", "#### Deep\n", "Edit"),
            write("s37c", "w4", "* a\n"),
            write("s37c", "w5", "1. a\n"),
            tr_tool(
                "s37c",
                root,
                "w6",
                "MultiEdit",
                file_path=doc,
                edits=[{"old_string": "a", "new_string": "- b"}],
            ),
        ],
        "s37d": [skill("s37d", "const-styling:other"), write("s37d", "w1", table)],
        "s37e": [write("s37e", "w1", table), skill("s37e", "style-defaults")],
        "s37f": [
            write("s37f", "w1", "Plain prose, nothing more.\n"),
            write("s37f", "w2", "### Level three\n"),
            write("s37f", "w3", "a | b\nc | d\n"),
            write("s37f", "w4", "text\n\n---\n\ntext\n"),
            write("s37f", "w5", "- a\n", path=str(root / "notes.txt")),
        ],
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W3 (pattern): 11 moment(s): 3 applied, 0 bypassed, 8 missed — B5 8" in found, found


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
    effect="effect-report.sh",  # no `effect_reader`: the module has no reader rule
)
