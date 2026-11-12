"""Fixtures of const-locations: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.

The fixture consumer is the shared one: three policies, two of them overlapping, which is
the overlap the generator refuses. This module is only a generator — no hook event, no
verdict, no scan — so the shared items about hook input, paths and skips, the warn channel
and the scan are not its own and are skipped; their numbers stay free. `gate_on` turns the
Write the shared items hand it into the generator's command line, run from inside the consumer.
"""

from __future__ import annotations

import ast
import errno
import json
import os
import re
import resource
import shlex
import shutil
import string
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
import yaml
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import Broken, Finding
from constitution_layer_kit.testing.acceptance import broken_first_line, expect, failure_of, item
from constitution_layer_kit.testing.consumer import ROOT_POLICY, Consumer, document, envelope
from constitution_layer_kit.testing.harness import Edit, Harness, Result, Write
from constitution_layer_kit.testing.items import EntryFile, Subject, fake_claude, tr_line
from locations_gate import filling, messages, start
from locations_gate.dials import KEYS
from locations_gate.model import ActKey

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"

IDENTITY = start.GENERATOR  # declared for the whole session by conftest; the expected messages read it
# — and each is also typed by hand at least once in these fixtures (rule 14 of the gate-script rules)
H = Harness(SCRIPTS, "new-document.sh", "new-document.py", start.GENERATOR.namespace)
NAMESPACE = start.GENERATOR.namespace

# values over 80 characters, with a line break and a backslash where the origin lets one in: a path the
# reader opens or types stays whole; a name that only points is cut at 80 with the cut said
WEIRD_DIR = "w\nx\\y" + "d" * 80  # a folder name, for the directory the run stands in and a root
WEIRD_DIR_SHOWN = "w\\nx\\\\y" + "d" * 80
TPL_ODD = "tpl/w\nx\\y" + "t" * 80 + ".md"  # a template path of the dial
TPL_ODD_SHOWN = "tpl/w\\nx\\\\y" + "t" * 80 + ".md"
LONG_STEM = "s" * 100  # a kebab name over 80 characters: its home is a path over 80 characters
LONG_KIND = "k" * 100  # a policy id over 80 characters

ODD_YAML = (  # the parser's line on a template whose id holds a bad escape: it quotes the backslash
    "while scanning a double-quoted scalar in"
    ' "<unicode string>", line 1, column 5: id: "x\\q" ^ found unknown escape character \'q\' in'
    ' "<unicode string>", line 1, column 8: id: "x\\q" ^'
)

NOTE = "docs/notes/a.md"  # the home of --kind notes-policy --stem a
NOTE_ARGS = ["--kind", "notes-policy", "--stem", "a", "--title", "A note", "--type", "non-authoritative"]
NOTE_TEXT = document("# A note\n", id="a", type="non-authoritative", title="A note", status="active")
NOTE_LINES = [
    messages.l1_home(NOTE, "notes-policy", "docs/notes/**"),
    messages.l2_no_template("notes-policy"),
    messages.l3_created(NOTE),
    messages.l4_count(NOTE),
]
TEMPLATE = "tpl/record.md"
TEMPLATE_TEXT = (
    "---\n"
    "id: <stable id>\n"
    "type: task-record\n"
    "title: >\n"
    "  <one line stating\n"
    "  the ruling>\n"
    "status: <active | inactive>\n"
    "stakes: <process | product | architecture>\n"
    "decider: <who>\n"
    "---\n"
    "\n"
    "# <the title again>\n"
    "\n"
    "## Context\n"
    "\n"
    "<what forced it>\n"
)

# a form feed is no line ending: the closer is the later `---`, and the form feed lies inside the block,
# which YAML refuses; the parser's line, with the position of the form feed
FF_BEFORE_CLOSER = "---\nid: <x>\ntype: current-state\ntitle: T\n\x0c---\nBODY\n---\nTWO\n"
FF_BEFORE_CLOSER_YAML = (
    'unacceptable character #x000c: special characters are not allowed in "<unicode string>", position 37'
)
FF_AFTER_CLOSER = "---\nid: <x>\ntype: current-state\ntitle: T\n---\x0cBODY\n---\nTWO\n"
FF_AFTER_CLOSER_YAML = (
    'unacceptable character #x000c: special characters are not allowed in "<unicode string>", position 40'
)


def own(**dials: object) -> dict[str, object]:
    """A patch of this module's namespace that keeps it working."""
    return {NAMESPACE: dict(dials)}


def claim(territory: Sequence[str]) -> dict[str, object]:
    return {"notes-policy": {"territory": list(territory)}}


def dials_text(patch: dict[str, object] | None = None) -> str:
    return yaml.safe_dump({**Consumer(Path()).dials, **(patch or {})}, sort_keys=False)


def run(consumer: Consumer, *arguments: str, env: dict[str, str] | None = None, cwd: str = "") -> Result:
    return H.run_gate("", args=list(arguments), env=env, cwd=consumer.root / cwd)


def prepared(
    dials_patch: dict[str, object] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> Consumer:
    consumer = H.fresh_consumer()
    consumer.write("constitution.yaml", raw_dials if raw_dials is not None else dials_text(dials_patch))
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    commit_if_changed(consumer)
    return consumer


def commit_if_changed(consumer: Consumer) -> None:
    """The consumer as committed, so that a refusal can be checked to leave git status empty."""
    consumer.git("add", "-A")
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=consumer.root, check=False)
    if staged.returncode != 0:
        consumer.commit()


def args_for(action: Write | Edit) -> list[str]:
    """The shared items hand a Write: its target says which kind and stem; the text is not used."""
    target = Path(action.target)
    kind = {"docs/notes": "notes-policy", "docs/policies": "root-policy"}[target.parent.as_posix()]
    meta_type = "non-authoritative" if kind == "notes-policy" else "current-state"
    return ["--kind", kind, "--stem", target.stem, "--title", "Fixture", "--type", meta_type]


def gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    consumer = prepared(dials_patch, raw_dials, files, remove)
    return run(consumer, *args_for(action), env=env), consumer.root


AT = "{at}"  # the run's temporary directory, in the three lines that name one: `broken` fills it in
KEBAB = (
    " — fix: lower-case letters, digits and single hyphens between them: a-z, 0-9, no leading, trailing"
    " or double hyphen"
)
NO_HOME = (
    " — fix: a home follows from one pattern <dir>/** or <dir>/**/*.md, or from one with a single free"
    " segment, <dir>/*/NAME.md; write the document by hand inside the territory, or simplify the territory"
)
ENTRY = (
    "; an entry the command cannot read names no template — fix: write the entry as {policy: <id>,"
    " template: <repository-relative path>}"
)
# Every refusal and dial failure the runner reaches, keyed by its handle in the table of §6, the
# whole first line typed here by hand: the items compare with what the message functions return
# too, so a slip inside a function is red only here.
GOLDEN: dict[str, str] = {
    "L5.1": "BROKEN: misinvocation: --stem was not given — fix: run it with --kind <policy id> --stem <stem>"
    " --title <text> [--type <meta-type>] [--segment <segment>] [--id <id>] [--dry-run]",
    "L5.2 odd": f"BROKEN: {AT}/l" + WEIRD_DIR_SHOWN + " is not inside a git repository — fix: run it from"
    " inside the repository the document belongs to",
    "L5.2": f"BROKEN: {AT} is not inside a git repository — fix: run it from inside the repository the"
    " document belongs to",
    "L5.3 odd": f"BROKEN: no constitution.yaml in {AT}/" + WEIRD_DIR_SHOWN + ": no kind is declared — fix: a"
    " document is created into a policy's territory; declare the root policy and the kind's policy first —"
    " the new-kind procedure",
    "L5.3": f"BROKEN: no constitution.yaml in {AT}: no kind is declared — fix: a document is created into a"
    " policy's territory; declare the root policy and the kind's policy first — the new-kind procedure",
    "L5.4": "BROKEN: constitution.yaml names no root_policy: no policy claims anything — fix: set"
    " root_policy: <path of the policy for policies>",
    "L5.5 long": "BROKEN: 'const-locations' is not a policy: no document in the root policy's territory"
    " carries that id — fix: name one of: "
    + LONG_KIND
    + ", notes-policy, root-policy, shared-policy; for a new"
    " kind, create its policy first — the new-kind procedure",
    "L5.5": "BROKEN: 'const-locations' is not a policy: no document in the root policy's territory carries"
    " that id — fix: name one of: notes-policy, root-policy, shared-policy; for a new kind, create its"
    " policy first — the new-kind procedure",
    "L5.6": "BROKEN: notes-policy's territory is the single path 'docs/one.md': nothing new is born there —"
    " fix: that document is created by hand at exactly that path, once; a kind that holds many documents"
    " claims a directory: <dir>/**",
    "L5.7 two": "BROKEN: no home follows from notes-policy's territory ['docs/notes/**', 'docs/more/**']"
    + NO_HOME,
    "L5.7 negation": "BROKEN: no home follows from notes-policy's territory ['docs/notes/**',"
    " '!docs/notes/x.md']" + NO_HOME,
    "L5.7 glob": "BROKEN: no home follows from notes-policy's territory ['docs/notes/*-note.md']" + NO_HOME,
    "L5.7 directory": "BROKEN: no home follows from notes-policy's territory ['docs/notes/']" + NO_HOME,
    "L5.7 git": "BROKEN: no home follows from notes-policy's territory ['./docs/notes/**']" + NO_HOME,
    "L5.8": "BROKEN: notes-policy's territory 'packages/*/README.md' has a free segment, and --segment was"
    " not given: the pattern fixes the file name and leaves that one segment to be named — fix: run it"
    " with --segment <the segment>; the file name is the pattern's, so --stem is not taken",
    "L5.9": "BROKEN: --stem was given, but notes-policy's territory 'packages/*/README.md' fixes the file"
    " name 'README' — fix: drop --stem and give --segment",
    "L5.10 stem": "BROKEN: 'Bad_Stem' is not a kebab-case name for the stem" + KEBAB,
    "L5.10 id": "BROKEN: 'x--y' is not a kebab-case name for the id" + KEBAB,
    "L5.10 segment": "BROKEN: 'Bad_Name' is not a kebab-case name for the segment" + KEBAB,
    "L5.10 stem break": "BROKEN: 'abc\\n' is not a kebab-case name for the stem" + KEBAB,
    "L5.10 stem cr": "BROKEN: 'abc\\r' is not a kebab-case name for the stem" + KEBAB,
    "L5.10 id break": "BROKEN: 'x\\ny' is not a kebab-case name for the id" + KEBAB,
    "L5.10 stem odd": "BROKEN: 'a\\nb\\\\c"
    + "d" * 75
    + "… [95 characters]' is not a kebab-case name for the stem"
    + KEBAB,
    "L5.11": "BROKEN: docs/notes/a.md already exists: creating never overwrites, so the document that is"
    " there stays as it is — fix: choose another stem, or edit the document that is there",
    "L5.11 long": "BROKEN: docs/notes/" + LONG_STEM + ".md already exists: creating never overwrites, so the"
    " document that is there stays as it is — fix: choose another stem, or edit the document that is there",
    "L5.12 long": "BROKEN: docs/notes/shared/" + LONG_STEM + ".md would also lie in notes-policy's territory"
    " ('docs/notes/**'): two policies would govern it — fix: territories never overlap; narrow one of them"
    " in constitution.yaml before creating documents there",
    "L5.12": "BROKEN: docs/notes/shared/b.md would also lie in notes-policy's territory ('docs/notes/**'):"
    " two policies would govern it — fix: territories never overlap; narrow one of them in"
    " constitution.yaml before creating documents there",
    "L5.13": "BROKEN: notes-policy has no template, and --type was not given: without a template nothing but"
    " the policy's prose says which meta-type the kind is — fix: run it with --type current-state,"
    " task-record or non-authoritative — docs/policies/notes-policy.md says which its kind is",
    "L5.13 long": "BROKEN: "
    + "k" * 80
    + "… [100 characters] has no template, and --type was not given: without a"
    " template nothing but the policy's prose says which meta-type the kind is — fix: run it with --type"
    " current-state, task-record or non-authoritative — docs/policies/" + LONG_KIND + ".md says which its"
    " kind is",
    "L5.14 odd": "BROKEN: --type current-state was given, but the template " + TPL_ODD_SHOWN + " fixes type:"
    " task-record, and a kind has one meta-type — fix: drop --type; the template decides",
    "L5.14": "BROKEN: --type current-state was given, but the template tpl/record.md fixes type:"
    " task-record, and a kind has one meta-type — fix: drop --type; the template decides",
    "L5.15 missing": "BROKEN: the template of notes-policy, tpl/record.md, does not exist — fix: point"
    " const-locations.templates at a Markdown file of this repository, or remove the entry",
    "L5.15 unreadable": "BROKEN: the template of notes-policy, tpl/record.md, cannot be read ('utf-8' codec"
    " can't decode byte 0xff in position 222: invalid start byte) — fix: point const-locations.templates"
    " at a Markdown file of this repository, or remove the entry",
    "L5.15 missing odd": "BROKEN: the template of notes-policy, " + TPL_ODD_SHOWN + ", does not exist — fix:"
    " point const-locations.templates at a Markdown file of this repository, or remove the entry",
    "L5.15 unreadable odd": "BROKEN: the template of notes-policy, " + TPL_ODD_SHOWN + ", cannot be read"
    " ('utf-8' codec can't decode byte 0xff in position 222: invalid start byte) — fix: point"
    " const-locations.templates at a Markdown file of this repository, or remove the entry",
    "L5.16 odd": "BROKEN: the template " + TPL_ODD_SHOWN + " opens with no readable envelope (while"
    ' scanning a double-quoted scalar in "<unicode string>",'
    ' line 1, column 5: id: "x\\\\q" ^ found unknown escape character \'q\' in "<unicode string>", line 1,'
    ' column 8: id: "x\\\\q" ^) — fix: a template opens with the YAML block a document of its kind carries'
    " — id, type, title, status — with placeholders where the writer fills",
    "L5.16 ff closer": "BROKEN: the template tpl/record.md opens with no readable envelope (unacceptable"
    ' character #x000c: special characters are not allowed in "<unicode string>", position 37) — fix: a'
    " template opens with the YAML block a document of its kind carries — id, type, title, status — with"
    " placeholders where the writer fills",
    "L5.16 ff after": "BROKEN: the template tpl/record.md opens with no readable envelope (unacceptable"
    ' character #x000c: special characters are not allowed in "<unicode string>", position 40) — fix: a'
    " template opens with the YAML block a document of its kind carries — id, type, title, status — with"
    " placeholders where the writer fills",
    "L5.16": "BROKEN: the template tpl/record.md opens with no readable envelope (none) — fix: a template"
    " opens with the YAML block a document of its kind carries — id, type, title, status — with"
    " placeholders where the writer fills",
    "L5.17 odd": "BROKEN: the template " + TPL_ODD_SHOWN + " carries type 'x\\ny" + "v" * 77 + "… [93"
    " characters]', which is no meta-type — fix: set type: current-state, task-record or non-authoritative"
    " in the template",
    "L5.17": "BROKEN: the template tpl/record.md carries type 'ruling', which is no meta-type — fix: set"
    " type: current-state, task-record or non-authoritative in the template",
    "L5.18": "BROKEN: --title was not given, and the envelope is written with the title as a value — fix:"
    " run it with --title '<the document's title>'; a dry run needs none",
    "L5.19 long": "BROKEN: id '"
    + "s" * 80
    + "… [100 characters]' is already carried by docs/notes/"
    + "o" * 100
    + ".md — fix: ids are unique in the tree: choose another stem, or give --id",
    "L5.19": "BROKEN: id 'a' is already carried by docs/notes/other.md — fix: ids are unique in the tree:"
    " choose another stem, or give --id",
    "L5.20 link long": "BROKEN: docs/notes/" + LONG_STEM + ".md could not be written ([Errno 17] File exists:"
    f" '{AT}/docs/notes/" + LONG_STEM + ".md'): the write is the last act, so the refusal leaves nothing"
    " behind — fix: remove what the system's error names — a denied permission, a file or link in the way"
    " at the home or a directory above it, a full or read-only disk — and run it again; nothing else was"
    " changed",
    "L5.20": "BROKEN: docs/notes/a.md could not be written ([Errno 13] Permission denied:"
    f" '{AT}/docs/notes'): the write is the last act, so the refusal leaves nothing behind — fix:"
    " remove what the system's error names — a denied permission, a file or link in the way at the home"
    " or a directory above it, a full or read-only disk — and run it again; nothing else was changed",
    "L5.20 link": "BROKEN: docs/notes/a.md could not be written ([Errno 17] File exists:"
    f" '{AT}/docs/notes/a.md'): the write is the last act, so the refusal leaves nothing behind — fix:"
    " remove what the system's error names — a denied permission, a file or link in the way at the home"
    " or a directory above it, a full or read-only disk — and run it again; nothing else was changed",
    "L5.20 part-way": "BROKEN: docs/notes/a.md could not be written ([Errno 27] File too large): the write"
    " is the last act, so the refusal leaves nothing behind — fix: remove what the system's error names — a"
    " denied permission, a file or link in the way at the home or a directory above it, a full or read-only"
    " disk — and run it again; nothing else was changed",
    "L5.21": "BROKEN: --segment was given, but notes-policy's territory 'docs/notes/**' has no free segment:"
    " the home is the directory and the stem — fix: drop --segment and give --stem",
    "L5.22": "BROKEN: --title is empty (or only whitespace), and the title is the envelope's one non-empty"
    " line — fix: run it with --title '<the document's title>'",
    "L5.23": "BROKEN: --title holds a line break, and a title is one line — fix: give the title on one line",
    "L5.24 long": "BROKEN: " + LONG_KIND + " claims no territory: its namespace in constitution.yaml has no"
    " territory, so no home follows — fix: under " + LONG_KIND + ": in constitution.yaml write territory:"
    " ['<dir>/**'], <dir> being the directory its documents live in",
    "L5.24": "BROKEN: notes-policy claims no territory: its namespace in constitution.yaml has no territory,"
    " so no home follows — fix: under notes-policy: in constitution.yaml write territory: ['<dir>/**'],"
    " <dir> being the directory its documents live in",
    "C5.a": "BROKEN: constitution.yaml: const-locations.bogus is no dial of this module — fix: a misspelt"
    " dial would be ignored in silence, so none is: write one of log_dir, templates",
    "C5.b": "BROKEN: constitution.yaml: const-locations.severity has no meaning: this module blocks"
    " nothing, and a line that sets nothing misleads the next reader — fix: remove the line",
    "C5.c": "BROKEN: constitution.yaml: const-locations.templates must be a list of {policy: <id>, template:"
    " <repository-relative path>}: one entry names one kind's template — fix: write it as templates:"
    " [{policy: <id>, template: <path>}, ...], or remove the key",
    "C5.d not a mapping": "BROKEN: constitution.yaml: const-locations.templates[0] is not a mapping" + ENTRY,
    "C5.d no policy": "BROKEN: constitution.yaml: const-locations.templates[0] has no policy" + ENTRY,
    "C5.d no template": "BROKEN: constitution.yaml: const-locations.templates[0] has no template" + ENTRY,
    "C5.d unknown key": "BROKEN: constitution.yaml: const-locations.templates[0] carries an unknown key"
    " 'type'" + ENTRY,
    "C5.d odd key": "BROKEN: constitution.yaml: const-locations.templates[0] carries an unknown key"
    " 'a\\nb'" + ENTRY,
    "C5.d repeated": "BROKEN: constitution.yaml: const-locations.templates[1] names policy 'notes-policy' a"
    " second time" + ENTRY,
    "C5.d odd repeated": "BROKEN: constitution.yaml: const-locations.templates[1] names policy 'a\\nb' a"
    " second time" + ENTRY,
    "C5.d outside": "BROKEN: constitution.yaml: const-locations.templates[0] names a template outside the"
    " repository" + ENTRY,
}


def broken(result: Result, failure: Broken, handle: str, at: str = "") -> None:
    """The refusal's line first, as the function builds it and as GOLDEN types it — `at` filling the
    directory a line names — then the closing line."""
    typed = GOLDEN.get(handle)
    if typed is None:
        pytest.fail(f"{handle}: no line typed in GOLDEN")
    broken_first_line(result, failure.render(), label=handle)
    golden = typed.replace(AT, at)
    first = result.stderr.splitlines()[0] if result.stderr else ""
    assert first == golden, f"{handle}: the first line is not the one typed here, {golden!r}: {first}"
    closed = messages.l4_nothing_written() in result.stderr
    assert closed, f"no closing line after: {result.stderr.strip()}"


def tree_state(consumer: Consumer) -> str:
    done = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=consumer.root,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def created(consumer: Consumer, rel: str, expected: str, result: Result, lines: Sequence[str]) -> None:
    path = consumer.root / rel
    if result.code != 0:
        pytest.fail(f"exit {result.code}: {result.stdout}{result.stderr}".strip())
    if not path.is_file():
        pytest.fail(f"{rel} was not created")
    text = path.read_text(encoding="utf-8")
    if text != expected:
        pytest.fail(f"{rel} holds:\n{text}\nexpected:\n{expected}")
    missing = [line for line in lines if line not in result.stdout]
    assert not missing, f"missing: {missing}"


# ---------------------------------------------------------------- the module's own items


@item(1, "a directory-prefix territory: the four-field envelope, the heading body, lines L1–L4")
def test_directory_prefix() -> None:
    """A directory-prefix territory: `--kind notes-policy --stem a --title 'A note' --type non-authoritative`
    creates `docs/notes/a.md` with exactly the four-field envelope and the heading body, and prints L1, L2
    (none), L3 and L4 word for word."""
    consumer = prepared()
    created(consumer, NOTE, NOTE_TEXT, run(consumer, *NOTE_ARGS), NOTE_LINES)
    # A home over 80 characters is a path the next step opens, so its lines show it whole — never cut
    stem = "a" * 90
    long_home = f"docs/notes/{stem}.md"
    long_consumer = prepared()
    long_args = ["--kind", "notes-policy", "--stem", stem, "--title", "A note", "--type", "non-authoritative"]
    long_text = document("# A note\n", id=stem, type="non-authoritative", title="A note", status="active")
    long_lines = [  # typed by hand: the home whole on the HOME, CREATED and count lines
        f"HOME: {long_home} — governed by notes-policy (territory 'docs/notes/**')",
        f"CREATED: {long_home}",
        f"1 document created ({long_home}) — fill the body where the template says, then commit",
    ]
    created(long_consumer, long_home, long_text, run(long_consumer, *long_args), long_lines)
    assert shared.escaped("a\\b\nc\r" + stem) == "a\\\\b\\nc\\r" + stem, (
        "a backslash and the line breaks of a path are escaped, the path never cut"
    )


@item(2, "<dir>/**/*.md and a leading slash are prefixes too")
def test_prefix_forms() -> None:
    """<dir>/**/*.md is a prefix too; a leading slash anchors and is no part of the home."""
    for pattern in ("docs/notes/**/*.md", "/docs/notes/**"):
        consumer = prepared(claim([pattern]))
        result = run(consumer, *NOTE_ARGS)
        lines = [messages.l1_home(NOTE, "notes-policy", pattern), messages.l3_created(NOTE)]
        created(consumer, NOTE, NOTE_TEXT, result, lines)
    pass


@item(3, "one free segment: the home filled, the id derived, --stem and --segment refused where not taken")
def test_free_segment() -> None:
    """One free segment: `packages/*/README.md` with `--segment alpha` creates `packages/alpha/README.md`
    with id `readme-alpha`; `--stem` given there is L5.9; `--segment` missing is L5.8; `--segment` given
    on a directory-prefix kind is L5.21."""
    pattern = "packages/*/README.md"
    patch = claim([pattern])
    consumer = prepared(patch)
    result = run(
        consumer,
        "--kind",
        "notes-policy",
        "--segment",
        "alpha",
        "--title",
        "Alpha",
        "--type",
        "current-state",
    )
    expected = document("# Alpha\n", id="readme-alpha", type="current-state", title="Alpha", status="active")
    home = "packages/alpha/README.md"
    created(consumer, home, expected, result, [messages.l1_home(home, "notes-policy", pattern)])
    broken(
        run(prepared(patch), "--kind", "notes-policy", "--stem", "z", "--title", "T"),
        messages.l5_stem_not_taken("notes-policy", pattern, "README"),
        "L5.9",
    )
    broken(
        run(prepared(patch), "--kind", "notes-policy", "--title", "T"),
        messages.l5_segment_needed("notes-policy", pattern),
        "L5.8",
    )
    broken(
        run(prepared(), "--kind", "notes-policy", "--stem", "a", "--segment", "x", "--title", "T"),
        messages.l5_segment_not_taken("notes-policy", "docs/notes/**"),
        "L5.21",
    )
    pass


@item(4, "a single path and every fourth-class territory: no home, refused and taught")
def test_no_home() -> None:
    """A single-path territory is L5.6; two patterns, a negated pattern, a `*` inside a file name, a bare
    directory `<dir>/` and `./<dir>/**`, whose derived home git does not claim, are each L5.7; a namespace
    with no `territory` line, and one with an empty list, are each L5.24."""
    broken(
        run(prepared(claim(["docs/one.md"])), *NOTE_ARGS),
        messages.l5_single_path("notes-policy", "docs/one.md"),
        "L5.6",
    )
    for territory, handle in (
        (["docs/notes/**", "docs/more/**"], "L5.7 two"),
        (["docs/notes/**", "!docs/notes/x.md"], "L5.7 negation"),
        (["docs/notes/*-note.md"], "L5.7 glob"),
        (["docs/notes/"], "L5.7 directory"),
        (["./docs/notes/**"], "L5.7 git"),  # a home derives, but git reads no ./ and claims none
    ):
        result = run(prepared(claim(territory)), *NOTE_ARGS)
        broken(result, messages.l5_no_home("notes-policy", territory), handle)
    namespaces: list[dict[str, object]] = [{"notes-policy": {}}, claim([])]  # no territory line; an empty one
    for namespace in namespaces:
        result = run(prepared(namespace), *NOTE_ARGS)
        broken(result, messages.l5_no_territory("notes-policy"), "L5.24")
    long_policy = {f"docs/policies/{LONG_KIND}.md": envelope(LONG_KIND, "current-state")}
    long_run = run(prepared(files=long_policy), "--kind", LONG_KIND, "--stem", "a", "--title", "T")
    broken(long_run, messages.l5_no_territory(LONG_KIND), "L5.24 long")  # typed into the dials


@item(
    5,
    "a template: the command's id, title and status, the template's type, the rest verbatim; a closer"
    " `--- ` and every line ending of Markdown read",
)
def test_from_template() -> None:
    """The created document carries the command's `id`, `title` and `status`, the template's `type` and
    every other envelope field verbatim, and the template's body byte for byte after the block; the same
    with a closer `--- `; and for a template given as text, each line ending of Markdown (LF, CRLF, a lone
    carriage return) and two byte-order marks, the rewritten block with LF endings and the body as written,
    a closing line with no ending at the text's end left so, each expected file typed by hand. The command
    itself reads a template with `read_text`, which turns CRLF and a lone carriage return into LF, so those
    two endings reach the generator in this item only."""
    dials = own(templates=[{"policy": "notes-policy", "template": TEMPLATE}])
    consumer = prepared(dials, files={TEMPLATE: TEMPLATE_TEXT})
    result = run(consumer, "--kind", "notes-policy", "--stem", "a", "--title", 'A ruling: "quoted"')
    expected = (
        "---\n"
        "id: a\n"
        "type: task-record\n"
        "title: 'A ruling: \"quoted\"'\n"
        "status: active\n"
        "stakes: <process | product | architecture>\n"
        "decider: <who>\n"
        "---\n"
        "\n"
        "# <the title again>\n"
        "\n"
        "## Context\n"
        "\n"
        "<what forced it>\n"
    )
    # the same template with a space after its closing line: the same file
    spaced = TEMPLATE_TEXT.replace("\n---\n\n#", "\n--- \n\n#")
    spaced_consumer = prepared(dials, files={TEMPLATE: spaced})
    spaced_result = run(
        spaced_consumer, "--kind", "notes-policy", "--stem", "a", "--title", 'A ruling: "quoted"'
    )
    created(consumer, NOTE, expected, result, [messages.l2_template(TEMPLATE)])
    assert spaced != TEMPLATE_TEXT, "the closer with a trailing space was not made"
    created(spaced_consumer, NOTE, expected, spaced_result, [messages.l2_template(TEMPLATE)])
    failed = [evidence for ok, evidence in from_text_in_process() if not ok]
    assert not failed, "; ".join(failed)


# `read_text` turns a CRLF and a lone CR in a template file into LF before the generator sees it, so
# those endings reach `from_template` only as text: it is called here with the text, each expected file typed
FROM_TEXT: list[tuple[str, str, str]] = [
    (
        "a lone CR ends each line",
        "---\rid: <x>\rtype: current-state\rtitle: T\r---\rBODY\r",
        "---\nid: a\ntype: current-state\ntitle: N\nstatus: active\n---\nBODY\r",
    ),
    (
        "CRLF, a folded title of two continuation lines, a status missing",
        "---\r\nid: <x>\r\ntype: current-state\r\ntitle: >\r\n  one\r\n  two\r\nstakes: process\r\n"
        "---\r\nBODY\r\n",
        "---\nid: a\ntype: current-state\ntitle: N\nstakes: process\nstatus: active\n---\nBODY\r\n",
    ),
    (
        "the closing line ends the text, with no line ending after it",
        "---\nid: <x>\ntype: current-state\ntitle: T\n---",
        "---\nid: a\ntype: current-state\ntitle: N\nstatus: active\n---",
    ),
    (
        "a closer `--- ` with its space, and a later thematic break in the body",
        "---\nid: <x>\ntype: current-state\ntitle: T\n--- \nBODY\n---\nTWO\n",
        "---\nid: a\ntype: current-state\ntitle: N\nstatus: active\n---\nBODY\n---\nTWO\n",
    ),
    (
        "two byte-order marks before the opener, and an opener `--- `",
        "\ufeff\ufeff--- \nid: <x>\ntype: current-state\ntitle: T\n---\nBODY\n",
        "---\nid: a\ntype: current-state\ntitle: N\nstatus: active\n---\nBODY\n",
    ),
]


def from_text_in_process() -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []
    for name, template, expected in FROM_TEXT:
        try:
            got = filling.from_template(template, TEMPLATE, "a", "N", None)
        except Exception as error:  # the old reader met a lone CR as no closing line at all
            results.append((False, f"{name}: {type(error).__name__} {error}"))
            continue
        results.append((got == expected, f"{name}: gave {got!r}, expected {expected!r}"))
    return results


@item(
    6,
    "no type, a conflicting type, a bad type, no envelope, a form feed at the closer, a missing"
    " template, one not UTF-8",
)
def test_template_refusals() -> None:
    """No template and no `--type` is L5.13; a template and `--type` is L5.14; a template whose `type` is no
    meta-type is L5.17; a template without an envelope is L5.16, and so is one with a form feed before its
    closer or one followed by text on the closer's line, since a line ends at a line break and nowhere else
    and YAML refuses the character; a missing template is L5.15, and a template that is not UTF-8 is
    L5.15's second form, `cannot be read`, the tree left as it was."""
    with_template = own(templates=[{"policy": "notes-policy", "template": TEMPLATE}])
    bad_type = TEMPLATE_TEXT.replace("type: task-record", "type: ruling")
    not_utf8 = prepared(with_template, files={TEMPLATE: TEMPLATE_TEXT})
    (not_utf8.root / TEMPLATE).write_bytes(TEMPLATE_TEXT.encode() + b"\xff\n")  # a byte UTF-8 never opens
    commit_if_changed(not_utf8)
    pairs = [
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "a", "--title", "T"),
            messages.l5_type_needed("notes-policy", "docs/policies/notes-policy.md"),
            "L5.13",
        ),
        (
            run(
                prepared(with_template, files={TEMPLATE: TEMPLATE_TEXT}),
                "--kind",
                "notes-policy",
                "--stem",
                "a",
                "--title",
                "T",
                "--type",
                "current-state",
            ),
            messages.l5_type_conflict("current-state", TEMPLATE, "task-record"),
            "L5.14",
        ),
        (
            run(
                prepared(with_template, files={TEMPLATE: bad_type}),
                "--kind",
                "notes-policy",
                "--stem",
                "a",
                "--title",
                "T",
            ),
            messages.l5_template_bad_type(TEMPLATE, "ruling"),
            "L5.17",
        ),
        (
            run(
                prepared(with_template, files={TEMPLATE: "# No envelope\n"}),
                "--kind",
                "notes-policy",
                "--stem",
                "a",
                "--title",
                "T",
            ),
            messages.l5_template_no_envelope(TEMPLATE, "none"),
            "L5.16",
        ),
        (
            run(
                prepared(with_template, files={TEMPLATE: FF_BEFORE_CLOSER}),
                "--kind",
                "notes-policy",
                "--stem",
                "a",
                "--title",
                "T",
            ),
            messages.l5_template_no_envelope(TEMPLATE, FF_BEFORE_CLOSER_YAML),
            "L5.16 ff closer",
        ),
        (
            run(
                prepared(with_template, files={TEMPLATE: FF_AFTER_CLOSER}),
                "--kind",
                "notes-policy",
                "--stem",
                "a",
                "--title",
                "T",
            ),
            messages.l5_template_no_envelope(TEMPLATE, FF_AFTER_CLOSER_YAML),
            "L5.16 ff after",
        ),
        (
            run(prepared(with_template), "--kind", "notes-policy", "--stem", "a", "--title", "T"),
            messages.l5_template_missing("notes-policy", TEMPLATE),
            "L5.15 missing",
        ),
        (
            run(not_utf8, "--kind", "notes-policy", "--stem", "a", "--title", "T"),
            messages.l5_template_unreadable(
                "notes-policy",
                TEMPLATE,
                f"'utf-8' codec can't decode byte 0xff in position {len(TEMPLATE_TEXT.encode())}: invalid"
                " start byte",
            ),
            "L5.15 unreadable",
        ),
    ]
    # the template's path, as the dial gives it, is the reader's to point at a real file: whole, escaped
    odd_dials = own(templates=[{"policy": "notes-policy", "template": TPL_ODD}])
    odd_args = ("--kind", "notes-policy", "--stem", "a", "--title", "T")
    odd_not_utf8 = prepared(odd_dials, files={TPL_ODD: TEMPLATE_TEXT})
    (odd_not_utf8.root / TPL_ODD).write_bytes(TEMPLATE_TEXT.encode() + b"\xff\n")
    commit_if_changed(odd_not_utf8)
    odd_type = TEMPLATE_TEXT.replace("type: task-record", 'type: "x\\ny' + "v" * 90 + '"')
    pairs += [
        (
            run(prepared(odd_dials), *odd_args),
            messages.l5_template_missing("notes-policy", TPL_ODD),
            "L5.15 missing odd",
        ),
        (
            run(odd_not_utf8, *odd_args),
            messages.l5_template_unreadable(
                "notes-policy",
                TPL_ODD,
                f"'utf-8' codec can't decode byte 0xff in position {len(TEMPLATE_TEXT.encode())}: invalid"
                " start byte",
            ),
            "L5.15 unreadable odd",
        ),
        (
            run(prepared(odd_dials, files={TPL_ODD: TEMPLATE_TEXT}), *odd_args, "--type", "current-state"),
            messages.l5_type_conflict("current-state", TPL_ODD, "task-record"),
            "L5.14 odd",
        ),
        (
            run(prepared(odd_dials, files={TPL_ODD: odd_type}), *odd_args),
            messages.l5_template_bad_type(TPL_ODD, "x\ny" + "v" * 90),
            "L5.17 odd",
        ),
        (
            run(prepared(odd_dials, files={TPL_ODD: '---\nid: "x\\q"\n---\n\n# T\n'}), *odd_args),
            messages.l5_template_no_envelope(TPL_ODD, ODD_YAML),
            "L5.16 odd",
        ),
        (
            run(
                prepared(
                    {LONG_KIND: {"territory": ["docs/long/**"]}},
                    files={f"docs/policies/{LONG_KIND}.md": envelope(LONG_KIND, "current-state")},
                ),
                "--kind",
                LONG_KIND,
                "--stem",
                "a",
                "--title",
                "T",
            ),
            messages.l5_type_needed(LONG_KIND, f"docs/policies/{LONG_KIND}.md"),
            "L5.13 long",
        ),
    ]
    for r, f, h in pairs:
        broken(r, f, h)
    assert tree_state(not_utf8) == "", "a template that is not UTF-8 changed the tree"


@item(7, "an overlap, an existing file, an id in use")
def test_proof_refusals() -> None:
    """A home another policy also claims is L5.12 (the shared consumer's overlap); a home that exists is
    L5.11; an id another document carries is L5.19."""
    overlap = run(
        prepared(), "--kind", "shared-policy", "--stem", "b", "--title", "B", "--type", "non-authoritative"
    )
    exists = run(prepared(files={NOTE: NOTE_TEXT}), *NOTE_ARGS)
    other = document("# Other\n", id="a", type="non-authoritative", title="Other", status="active")
    in_use = run(prepared(files={"docs/notes/other.md": other}), *NOTE_ARGS)
    # a stem of 100 characters makes every home a path over 80 characters: whole, never cut
    long_home = f"docs/notes/{LONG_STEM}.md"
    long_args = ["--kind", "notes-policy", "--stem", LONG_STEM, "--title", "T", "--type", "non-authoritative"]
    long_overlap = run(
        prepared(),
        "--kind",
        "shared-policy",
        "--stem",
        LONG_STEM,
        "--title",
        "T",
        "--type",
        "non-authoritative",
    )
    long_exists = run(prepared(files={long_home: NOTE_TEXT}), *long_args)
    long_other = f"docs/notes/{'o' * 100}.md"  # a holder whose path is over 80 characters, and an id too
    long_in_use = run(prepared(files={long_other: envelope(LONG_STEM, "non-authoritative")}), *long_args)
    broken(
        overlap,
        messages.l5_two_policies("docs/notes/shared/b.md", "notes-policy", "docs/notes/**"),
        "L5.12",
    )
    broken(exists, messages.l5_exists(NOTE), "L5.11")
    broken(in_use, messages.l5_id_in_use("a", "docs/notes/other.md"), "L5.19")
    broken(
        long_overlap,
        messages.l5_two_policies(f"docs/notes/shared/{LONG_STEM}.md", "notes-policy", "docs/notes/**"),
        "L5.12 long",
    )
    broken(long_exists, messages.l5_exists(long_home), "L5.11 long")
    broken(long_in_use, messages.l5_id_in_use(LONG_STEM, long_other), "L5.19 long")


@item(8, "--dry-run prints the home and the template and writes nothing")
def test_dry_run() -> None:
    consumer = prepared()
    result = run(consumer, "--kind", "notes-policy", "--stem", "a", "--dry-run")
    lines = [
        messages.l1_home(NOTE, "notes-policy", "docs/notes/**"),
        # typed by hand
        f"TEMPLATE: none — notes-policy names no template in {NAMESPACE}.templates; the envelope alone is"
        " written, and the body is the title's heading",
        "0 documents created — dry run: the lines above are what a write would use",
    ]
    # a template path of over 80 characters with a break and a backslash: the TEMPLATE line shows it whole
    odd = prepared(
        own(templates=[{"policy": "notes-policy", "template": TPL_ODD}]), files={TPL_ODD: TEMPLATE_TEXT}
    )
    odd_result = run(odd, "--kind", "notes-policy", "--stem", "a", "--dry-run")
    odd_line = "TEMPLATE: tpl/w\\nx\\\\y" + "t" * 80 + ".md"
    ok = (
        result.code == 0
        and all(line in result.stdout for line in lines)
        and not (consumer.root / NOTE).exists()
        and tree_state(consumer) == ""
        and odd_result.code == 0
        and odd_line in odd_result.stdout.splitlines()
        and tree_state(odd) == ""
    )
    assert ok, f"{result}; tree: {tree_state(consumer)!r}; odd: {odd_result}"


@item(9, "not a policy, no dials file, no root policy, outside any repository")
def test_repository_refusals() -> None:
    not_policy = run(prepared(), "--kind", "const-locations", "--stem", "a", "--title", "T")
    consumer = prepared()
    (consumer.root / "constitution.yaml").unlink()
    no_dials = run(consumer, *NOTE_ARGS)
    no_root = run(
        prepared(raw_dials="module_prefix: const-\nnotes-policy:\n  territory: ['docs/notes/**']\n"),
        *NOTE_ARGS,
    )
    outside = H.scratch_dir()
    loose = H.run_gate("", args=NOTE_ARGS, cwd=outside, env={"GIT_CEILING_DIRECTORIES": str(outside.parent)})
    # the directory the run stands in and the repository root are paths: whole, a break and a backslash shown
    parent = H.scratch_dir()
    odd = Consumer(parent / WEIRD_DIR).build()
    (odd.root / "constitution.yaml").unlink()
    odd_no_dials = run(odd, *NOTE_ARGS)
    odd_loose_dir = parent / ("l" + WEIRD_DIR)
    odd_loose_dir.mkdir()
    odd_loose = H.run_gate(
        "", args=NOTE_ARGS, cwd=odd_loose_dir, env={"GIT_CEILING_DIRECTORIES": str(parent)}
    )
    long_policy = {f"docs/policies/{LONG_KIND}.md": envelope(LONG_KIND, "current-state")}
    long_not_policy = run(
        prepared(files=long_policy), "--kind", "const-locations", "--stem", "a", "--title", "T"
    )
    broken(
        not_policy,
        messages.l5_not_a_policy("const-locations", ["notes-policy", "root-policy", "shared-policy"]),
        "L5.5",
    )
    broken(no_dials, messages.l5_no_dials(str(consumer.root)), "L5.3", at=str(consumer.root))
    broken(no_root, messages.l5_no_root_policy(), "L5.4")
    broken(loose, messages.l5_no_repository(str(outside)), "L5.2", at=str(outside))
    broken(odd_no_dials, messages.l5_no_dials(str(odd.root)), "L5.3 odd", at=str(parent))
    broken(odd_loose, messages.l5_no_repository(str(odd_loose_dir)), "L5.2 odd", at=str(parent))
    broken(
        long_not_policy,
        messages.l5_not_a_policy(
            "const-locations", [LONG_KIND, "notes-policy", "root-policy", "shared-policy"]
        ),
        "L5.5 long",
    )


@item(10, "a stem, an id, a segment, a title, a missing stem")
def test_argument_refusals() -> None:
    """A stem, a segment and an id that are no kebab-case names are each L5.10, a stem or an id holding a
    line break or a carriage return too, shown escaped and cut at 80 characters, the tree untouched; no
    `--title` is L5.18; an empty title and one of whitespace are L5.22, in a dry run too, and one holding a
    line break is L5.23, each leaving the tree as it was; no `--stem` on a directory-prefix kind is L5.1."""
    pairs = [
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "Bad_Stem", "--title", "T"),
            messages.l5_not_kebab("Bad_Stem", "the stem"),
            "L5.10 stem",
        ),
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "a", "--title", "T", "--id", "x--y"),
            messages.l5_not_kebab("x--y", "the id"),
            "L5.10 id",
        ),
        (
            run(
                prepared(claim(["packages/*/README.md"])),
                "--kind",
                "notes-policy",
                "--segment",
                "Bad_Name",
                "--title",
                "T",
            ),
            messages.l5_not_kebab("Bad_Name", "the segment"),
            "L5.10 segment",
        ),
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "a", "--type", "non-authoritative"),
            messages.l5_title_needed(),
            "L5.18",
        ),
        (
            run(prepared(), "--kind", "notes-policy", "--title", "T"),
            messages.l5_usage("--stem was not given"),
            "L5.1",
        ),
    ]
    broke = prepared()
    for stem, handle in (("abc\n", "L5.10 stem break"), ("abc\r", "L5.10 stem cr")):
        pairs.append(
            (
                run(broke, "--kind", "notes-policy", "--stem", stem, "--title", "T"),
                messages.l5_not_kebab(stem, "the stem"),
                handle,
            )
        )
    pairs.append(  # a line break in the id; then a value over 80 characters with a backslash, cut
        (
            run(broke, "--kind", "notes-policy", "--stem", "a", "--title", "T", "--id", "x\ny"),
            messages.l5_not_kebab("x\ny", "the id"),
            "L5.10 id break",
        )
    )
    odd_stem = "a\nb\\c" + "d" * 90
    pairs.append(
        (
            run(broke, "--kind", "notes-policy", "--stem", odd_stem, "--title", "T"),
            messages.l5_not_kebab(odd_stem, "the stem"),
            "L5.10 stem odd",
        )
    )
    titles = prepared()  # an empty title, one of whitespace — in a dry run too — and one of two lines
    for title, failure, handle in (
        ("", messages.l5_title_empty(), "L5.22"),
        ("  ", messages.l5_title_empty(), "L5.22"),
        ("a\nb", messages.l5_title_multiline(), "L5.23"),
    ):
        pairs.append(
            (run(titles, "--kind", "notes-policy", "--stem", "a", "--title", title), failure, handle)
        )
    pairs.append(
        (
            run(titles, "--kind", "notes-policy", "--stem", "a", "--title", "", "--dry-run"),
            messages.l5_title_empty(),
            "L5.22",
        )
    )
    for r, f, h in pairs:
        broken(r, f, h)
    assert tree_state(titles) == "", "a refused title changed the tree"
    assert tree_state(broke) == "" and not (broke.root / "docs" / "notes").exists(), (
        "a refused stem or id with a line break wrote a file"
    )


@item(11, "the dials: an unknown key, severity, and every shape of a bad templates entry")
def test_dial_failures() -> None:
    """An unknown key is C5.a; `severity` present is C5.b; `templates` not a list is C5.c; an entry that is
    no mapping, lacks a key, carries an unknown key, repeats a policy (one named with a line break too,
    shown escaped on one line) or leaves the repository is C5.d with that clause."""
    entries: list[tuple[object, Broken, str]] = [
        ("x", messages.c5_templates_shape(), "C5.c"),
        (["x"], messages.c5_template_entry(0, messages.entry_not_a_mapping()), "C5.d not a mapping"),
        (
            [{"template": "t.md"}],
            messages.c5_template_entry(0, messages.entry_missing("policy")),
            "C5.d no policy",
        ),
        (
            [{"policy": "notes-policy"}],
            messages.c5_template_entry(0, messages.entry_missing("template")),
            "C5.d no template",
        ),
        (
            [{"policy": "notes-policy", "template": "t.md", "type": "x"}],
            messages.c5_template_entry(0, messages.entry_unknown_key("type")),
            "C5.d unknown key",
        ),
        (
            [{"policy": "notes-policy", "template": "t.md", "a\nb": "x"}],
            messages.c5_template_entry(0, messages.entry_unknown_key("a\nb")),
            "C5.d odd key",  # a line break in the key is shown escaped: the line stays one line
        ),
        (
            [{"policy": "notes-policy", "template": "t.md"}, {"policy": "notes-policy", "template": "u.md"}],
            messages.c5_template_entry(1, messages.entry_repeated("notes-policy")),
            "C5.d repeated",
        ),
        (
            [{"policy": "a\nb", "template": "t.md"}, {"policy": "a\nb", "template": "u.md"}],
            messages.c5_template_entry(1, messages.entry_repeated("a\nb")),
            "C5.d odd repeated",  # a policy name with a line break is shown escaped, like the key's
        ),
        (
            [{"policy": "notes-policy", "template": "../t.md"}],
            messages.c5_template_entry(0, messages.entry_outside()),
            "C5.d outside",
        ),
    ]
    triples = [
        (run(prepared(own(templates=value)), *NOTE_ARGS), failure, handle)
        for value, failure, handle in entries
    ]
    triples.append((run(prepared(own(bogus=1)), *NOTE_ARGS), shared.c5_unknown_dial("bogus", KEYS), "C5.a"))
    triples.append((run(prepared(own(severity="block")), *NOTE_ARGS), messages.c5_severity_here(), "C5.b"))
    for r, f, h in triples:
        broken(r, f, h)


@item(12, "every refusal leaves the tree as it was")
def test_refusals_leave_the_tree() -> None:
    """After four refusals of different classes (an overlap, a missing template, an unknown kind, a bad
    stem) `git status` is empty and no directory was made."""
    consumer = prepared(own(templates=[{"policy": "notes-policy", "template": TEMPLATE}]))
    runs = [
        run(
            consumer, "--kind", "shared-policy", "--stem", "b", "--title", "B", "--type", "non-authoritative"
        ),
        run(consumer, "--kind", "notes-policy", "--stem", "a", "--title", "T"),  # the template is missing
        run(consumer, "--kind", "nobody", "--stem", "a", "--title", "T"),
        run(consumer, "--kind", "notes-policy", "--stem", "Bad", "--title", "T"),
    ]
    state = tree_state(consumer)
    ok = all(r.code == 1 for r in runs) and state == "" and not (consumer.root / "docs/notes/shared").exists()
    assert ok, f"tree: {state!r}"


@item(13, "golden lines: stdout and stderr character for character")
def test_golden_lines() -> None:
    """The texts of the module's document, character for character, against what was printed: L1-L4,
    the refusal L5.11 and the closing line as literals. Every L5 and C5 line the runner reaches is typed as
    a literal keyed by its handle, the three that name the run's directory (L5.2, L5.3, L5.20) with that
    directory filled in. T3, T4, T6, T7, T9-T11 and T16-T18 require the first stderr line to be that
    literal as well as what the message function returns; a handle with no literal is red, never a crash
    of the runner. Seen to fail with one word of the L5.9 fix changed. The table of the module document's
    section 6 and the code agree where review compared them (V4)."""
    consumer = prepared()
    out = run(consumer, *NOTE_ARGS).stdout
    refused = run(consumer, *NOTE_ARGS).stderr
    expected_out = "\n".join(NOTE_LINES) + "\n"
    expected_err = GOLDEN["L5.11"] + "\nBROKEN: the document could not be created — nothing was written\n"
    ok = out == expected_out and refused == expected_err
    assert ok, f"stdout:\n{out}\nstderr:\n{refused}"


@item(19, "golden lines: every refusal line typed here was compared by an earlier item")
def test_every_golden_line_compared() -> None:
    """No line of GOLDEN typed and left unused: each handle stands as a string in this file outside
    GOLDEN, where an item hands it to `broken` — read by syntax tree, since the items run in no fixed
    order and need not share a process."""
    tree = ast.parse(Path(__file__).resolve().read_text(encoding="utf-8"))
    typed = next(
        node
        for node in tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "GOLDEN"
    )
    inside = {id(node) for node in ast.walk(typed)}
    named = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in inside
    }
    unused = sorted(set(GOLDEN) - named)
    assert not unused, f"typed in GOLDEN, compared by no item: {unused}"


@item(14, "the closing line is the generator's own; the entry files drop the gate's clause")
def test_closing_is_the_generators() -> None:
    """A failure closes with the generator's line, never a gate's count; the entry files' variants
    of C1, C14 and C15 drop the clause about unchecked writes; and the shared C2, printed when a
    library is missing, closes with the generator's own clause, since no write passes here."""
    result = run(prepared(), "--kind", "nobody", "--stem", "a", "--title", "T")
    own_line = (
        messages.l4_nothing_written() in result.stderr and shared.c11_broken_count() not in result.stderr
    )
    sources = "".join(
        (SCRIPTS / name).read_text(encoding="utf-8") for name in ("new-document.sh", "new-document.py")
    )
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_library = run(prepared(), *NOTE_ARGS, env={"PYTHONPATH": str(shadow)})
    first = no_library.stderr.splitlines()[0] if no_library.stderr else ""
    library_clause = (
        no_library.code == 1
        and first.endswith(" — until then nothing is created")
        and "pass unchecked" not in no_library.stderr
    )
    assert own_line and "pass unchecked" not in sources and library_clause, (
        "closing line the generator's; entry files without the gate's clause; C2 closed by the generator's"
    )


@item(16, "a write the system refuses is refused in turn, and leaves nothing behind")
def test_write_refused() -> None:
    """A write the system refuses (`docs` made read-only, so `docs/notes` cannot be made) is L5.20, and
    leaves nothing: no file, no directory made for it. The line is the literal of item 13 with the
    system's error naming the directory, the closing line after it, `git status` empty. Reported as not
    exercised, with a zero count, when the runner runs as root, where a mode bit denies no write."""
    if os.geteuid() == 0:
        return
    consumer = prepared()
    docs = consumer.root / "docs"
    os.chmod(docs, 0o500)  # docs/notes cannot be made
    try:
        result = run(consumer, *NOTE_ARGS)
    finally:
        os.chmod(docs, 0o755)  # the runner's cleanup cannot remove what it may not write into
    error = f"[Errno 13] Permission denied: '{docs}/notes'"
    said = failure_of(
        lambda: broken(result, messages.l5_could_not_write(NOTE, error), "L5.20", at=str(consumer.root))
    )
    state = tree_state(consumer)
    problems = [
        *([] if said is None else [said]),
        *([] if state == "" else [f"tree: {state!r}"]),
        *(["docs/notes was left behind"] if (docs / "notes").exists() else []),
    ]
    assert not problems, "; ".join(problems)


@item(17, "a link that points nowhere at the home is refused at the write, and is left as it was")
def test_write_refused_by_a_link() -> None:
    """A link that points nowhere, standing at the home, passes the existence proof and meets the
    write: L5.20 with the system's own error (`File exists`, naming the home), its fix naming a file or
    link in the way, the closing line after it, the link left as it was."""
    consumer = prepared()
    notes = consumer.root / "docs" / "notes"
    notes.mkdir(parents=True)
    os.symlink("nowhere.md", notes / "a.md")
    os.symlink("nowhere.md", notes / f"{LONG_STEM}.md")  # a home over 80 characters is named whole
    before = tree_state(consumer)
    result = run(consumer, *NOTE_ARGS)
    error = f"[Errno {errno.EEXIST}] {os.strerror(errno.EEXIST)}: '{notes}/a.md'"
    said = failure_of(
        lambda: broken(result, messages.l5_could_not_write(NOTE, error), "L5.20 link", at=str(consumer.root))
    )
    link = notes / "a.md"
    kept = link.is_symlink() and os.readlink(link) == "nowhere.md"
    long_result = run(
        consumer,
        "--kind",
        "notes-policy",
        "--stem",
        LONG_STEM,
        "--title",
        "A note",
        "--type",
        "non-authoritative",
    )
    long_error = f"[Errno {errno.EEXIST}] {os.strerror(errno.EEXIST)}: '{notes}/{LONG_STEM}.md'"
    long_said = failure_of(
        lambda: broken(
            long_result,
            messages.l5_could_not_write(f"docs/notes/{LONG_STEM}.md", long_error),
            "L5.20 link long",
            at=str(consumer.root),
        )
    )
    after = tree_state(consumer)
    problems = [
        *([] if said is None else [said]),
        *([] if long_said is None else [long_said]),
        *([] if after == before else [f"tree: {before!r} became {after!r}"]),
        *([] if kept else ["the link was not left as it was"]),
    ]
    assert not problems, "; ".join(problems)


FILE_LIMIT = 8192  # bytes: room for what git writes on the way, not for the note with LONG_TITLE
LONG_TITLE = "A note " * 2000  # one line of 14000 characters, the envelope and the heading both carry it
LONG_ARGS = ["--kind", "notes-policy", "--stem", "a", "--title", LONG_TITLE, "--type", "non-authoritative"]


def limited_to_file_size() -> None:
    """Run in the child before the generator starts: a file past FILE_LIMIT bytes cannot grow, and
    Python, which ignores SIGXFSZ, sees the write fail with EFBIG."""
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_LIMIT, FILE_LIMIT))


@item(18, "a write that fails part-way leaves neither the file nor the directory made for it")
def test_write_fails_part_way() -> None:
    """A write that fails once the file is open — part of the text written, the rest refused —
    is L5.20, and the file and the directory made for it are removed: the tree as it was. The generator
    runs under a limit on the size of a file it may write, below the length of the document, so the file
    is opened and the write meets `File too large`; the line carries the system's error, the closing line
    follows, `git status` as before."""
    consumer = prepared()
    before = tree_state(consumer)
    done = subprocess.run(
        [H.sh, str(H.wrapper), *LONG_ARGS],
        text=True,
        capture_output=True,
        env=H.environment(),
        check=False,
        cwd=consumer.root,
        preexec_fn=limited_to_file_size,  # the harness's run takes none: the limit is this item's alone
    )
    result = Result(done.returncode, done.stdout, done.stderr)
    error = f"[Errno {errno.EFBIG}] {os.strerror(errno.EFBIG)}"
    said = failure_of(lambda: broken(result, messages.l5_could_not_write(NOTE, error), "L5.20 part-way"))
    after = tree_state(consumer)
    notes = consumer.root / "docs" / "notes"
    problems = [
        *([] if len(LONG_TITLE) > FILE_LIMIT else ["the note fits under the limit"]),
        *([] if result.code == 1 else [f"exit {result.code}, not 1"]),
        *([] if said is None else [said]),
        *([] if after == before else [f"tree: {before!r} became {after!r}"]),
        *([f"{NOTE} was left behind"] if (notes / "a.md").exists() else []),
        *(["docs/notes was left behind"] if notes.exists() else []),
    ]
    assert not problems, "; ".join(problems)


@item(15, "a note of the policy index is printed before the lines")
def test_notes_are_printed() -> None:
    """A policy document without a readable id earns the shared note, on stdout, before the lines."""
    consumer = prepared(files={"docs/policies/zz-no-id.md": "# no envelope\n"})
    result = run(consumer, *NOTE_ARGS)
    note = shared.n1_note_policy_without_id("docs/policies/zz-no-id.md")
    expect(result, 0, note, "stdout")


# The module's other entry files, beside the harness's, each with its clause and closing line typed by hand:
# the shared items about the interpreter's floor and the shared package run each.
ENTRY_FILES = (
    EntryFile("effect-report.py", "", "BROKEN: the report could not run — no rule counted"),
    EntryFile(
        "grant-new-document.py",
        "",
        "BROKEN: the command was not granted — the platform asks for it as for any other command",
    ),
)

SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=Write(NOTE, NOTE_TEXT),
    red=Write(ROOT_POLICY, ""),  # the root policy exists: the run is refused
    red_finding=Finding(ActKey.L5, f"{ROOT_POLICY} already exists", "", ""),
    green=messages.l4_count(NOTE),
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=True,
    judges_envelopes=False,
    event_driven=False,
    closing=messages.l4_nothing_written(),
    act_args=NOTE_ARGS,
    effect="effect-report.sh",
    effect_hook="grant-new-document.sh",  # the hook runs the grant, not the generator the harness wraps
    entries=ENTRY_FILES,
    effect_clause="until then the effect report is not made",  # its C2 clause, typed by hand
)


# ---------------------------------------------------------------- the grant: the hook's own entry point

G = Harness(SCRIPTS, "grant-new-document.sh", "grant-new-document.py", NAMESPACE)
PLUGIN = SCRIPTS.parent  # the plugin root, as CLAUDE_PLUGIN_ROOT names it to the hook
OWN = f"sh {PLUGIN}/scripts/new-document.sh"
# The answer, typed by hand: one JSON object, the reason the platform writes to its debug log.
ALLOW = (
    '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",'
    ' "permissionDecisionReason": "const-locations: the plugin\'s own create command, with plain or'
    ' single-quoted arguments"}}\n'
)
# The release of the shared package the grant's entry file requires, read from that file.
REQUIRES = re.search(r'^REQUIRES = "([0-9.]+)"', (SCRIPTS / "grant-new-document.py").read_text(), re.M)[1]  # type: ignore[index]
NOT_GRANTED = "BROKEN: the command was not granted — the platform asks for it as for any other command"
GRANT_CLAUSE = "until then the command asks for approval as any other command does"


def event(command: object, name: str = "PreToolUse", tool: str = "Bash") -> str:
    """One hook event of the shell tool, as the platform sends it."""
    return json.dumps(
        {
            "hook_event_name": name,
            "tool_name": tool,
            "tool_input": {"command": command},
            "session_id": "s1",
            "transcript_path": "/t/s1.jsonl",
            "cwd": "/",
        }
    )


def ask_grant(stdin: str, root: str = str(PLUGIN), env: dict[str, str] | None = None) -> Result:
    environment = {"CLAUDE_PLUGIN_ROOT": root} if root else {}
    return G.run_gate(stdin, env={**environment, **(env or {})}, cwd=G.scratch_dir())


GRANTED = [
    OWN,
    f"{OWN} --dry-run --kind notes-policy --stem a",
    f"{OWN} --kind notes-policy --stem a --title 'A note' --type non-authoritative",
    f"{OWN} --kind plc-0005-research --stem comparison-x"
    " --title 'Comparison — const-x (2026-11-02): a; b & c | d $e `f` \"g\" *'",
    f"{OWN} --kind p --segment alpha --id readme-alpha --title ''",
]
NOT_OWN = [
    f"{OWN} --kind p; touch PWNED",
    f"{OWN} --kind p && touch PWNED",
    f"{OWN} --kind p || touch PWNED",
    f"{OWN} --kind p | tee out",
    f"{OWN} --kind p & touch PWNED",
    f"{OWN} --kind p\ntouch PWNED",
    f"{OWN} --kind p > out.txt",
    f"{OWN} --kind p 2>&1",
    f"{OWN} --kind p < in.txt",
    f"{OWN} --title $(touch PWNED)",
    f"{OWN} --title `touch PWNED`",
    f"{OWN} --title $HOME",
    f'{OWN} --title "A note"',
    f"{OWN} --stem *",
    f"{OWN} --stem ~",
    f"{OWN} --stem =ls",
    f"{OWN} --title 'A'\"'\"'s'",
    f"{OWN} --title='A note'",
    f"{OWN} --title 'two\nlines'",
    f"{OWN}  --kind p",
    f"{OWN} --kind p ",
    f"{OWN}.evil --kind p",
    f"sh {PLUGIN}/scripts/other.sh --kind p",
    f"bash {PLUGIN}/scripts/new-document.sh --kind p",
    f"X=1 {OWN} --kind p",
    f"command {OWN} --kind p",
    f"cd /tmp && {OWN} --kind p",
    "sh /elsewhere/const-locations/plugin/scripts/new-document.sh --kind p",
    "ls",
    f"{OWN} --title a' ';touch PWNED;' b'",  # a quote joined to a plain word: the `;` stands outside
    f"{OWN} --title 'a'b",
    f"{OWN} --title a'b'",
    f"{OWN} --title '''",
    f"{OWN} --title 'a\rb'",
    f"{OWN} --title 'a\x00b'",
    f"{OWN} #x",
    f"{OWN} !x",
]
# One form for each character the plain class of an argument does not hold, printable ASCII and a few
# others a shell or a font may read as syntax or space: each alone in a value, so that a character added
# to the class by mistake is answered with `allow` here and the item is red.
PLAIN = set(string.ascii_letters + string.digits + "_./:,@+-")
EXCLUDED = [c for c in string.printable + "  ＆；" if c not in PLAIN and c not in " \n"]
NOT_OWN += [f"{OWN} --stem a{c}b" for c in EXCLUDED]
# The same for the root, whose class holds neither `:` nor `,`.
EXCLUDED_ROOT = [c for c in string.printable + "\u00a0" if c not in PLAIN - {":", ","} and c != " "]


@item(20, "the grant: the plugin's own command, plain or single-quoted, is answered allow, typed by hand")
def test_grant_allows_its_own_command() -> None:
    """Each form the allowlist names gets the one JSON object and exit 0, nothing on stderr — a trailing
    slash on the root changes nothing. GRANTED holds the forms: the module's own command alone, with a dry
    run, with plain values, with single-quoted values holding a space, a dash, a separator, a `$`, a
    backtick, a double quote and a glob, and an empty one."""
    wrong = []
    for command in GRANTED:
        for root in (str(PLUGIN), f"{PLUGIN}/"):
            result = ask_grant(event(command), root)
            if (result.code, result.stdout, result.stderr) != (0, ALLOW, ""):
                wrong.append(f"{command!r} at {root!r}: {result}")
    assert not wrong, "\n".join(wrong)


@item(
    21, "the grant: any other command, a separator, a redirection, an expansion or a quote form, gets nothing"
)
def test_grant_says_nothing_else() -> None:
    """The allowlist's red half: each of these is no match, so the hook prints nothing and exits 0, and
    the platform's own permission flow decides the call. NOT_OWN lists the forms: the command followed by
    `;`, `&&`, `||`, a pipe, `&`, a line break, a redirection of each direction, a substitution of each
    form, a variable, a double-quoted value, a glob, `~`, a word opening `=`, a quote closed and reopened,
    a quote joined to a plain word so that a `;` stands outside it, an unbalanced quote, `--title='...'`, a
    line break, a carriage return or a NUL inside quotes, `#` and `!` as words, two spaces, a trailing
    space, a suffix on the script's name, another script, `bash`, an assignment, the `command` builtin and
    a `cd` before it, another root, and `ls`; one value for each printable character the plain class does
    not hold, and for a no-break space, a line separator and two full-width separators. An `allow` here
    would skip the platform's split of a compound command and grant what follows the separator."""
    wrong = []
    for command in NOT_OWN:
        result = ask_grant(event(command))
        if (result.code, result.stdout, result.stderr) != (0, "", ""):
            wrong.append(f"{command!r}: {result}")
    assert not wrong, "\n".join(wrong)


@item(22, "the grant: a plugin root it cannot name safely, or none, grants nothing")
def test_grant_root() -> None:
    """A root with a space, a separator, a quote, any printable character its class leaves out or a
    no-break space, a root that ends in a line break, or a relative path is matched by nothing, nor is
    an empty or absent CLAUDE_PLUGIN_ROOT — the call then goes to the platform's prompt."""
    wrong = []
    roots = ["/a b/plugin", "/a;b/plugin", "/a'b/plugin", "plugin", ""]
    roots += [f"/a{c}b/plugin" for c in EXCLUDED_ROOT] + [f"{PLUGIN}\n"]
    for root in roots:
        result = ask_grant(event(f"sh {root}/scripts/new-document.sh --kind p"), root)
        if (result.code, result.stdout, result.stderr) != (0, "", ""):
            wrong.append(f"{root!r}: {result}")
    empty = G.run_gate(event(OWN), env={"CLAUDE_PLUGIN_ROOT": ""}, cwd=G.scratch_dir())
    if (empty.code, empty.stdout, empty.stderr) != (0, "", ""):
        wrong.append(f"an empty CLAUDE_PLUGIN_ROOT: {empty}")
    assert not wrong, "\n".join(wrong)


@item(23, "the grant: another event, another tool, judges nothing and says nothing")
def test_grant_other_events() -> None:
    """A PostToolUse of the same command and a PreToolUse of another tool are no call it grants."""
    after = ask_grant(event(OWN, name="PostToolUse"))
    write = ask_grant(
        json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Read", "tool_input": {"file_path": "/x"}})
    )
    assert (after.code, after.stdout, after.stderr) == (0, "", "") and (
        write.code,
        write.stdout,
        write.stderr,
    ) == (0, "", ""), f"{after}\n{write}"


@item(24, "the grant: input it cannot read and an argument given are refused, nothing granted, typed by hand")
def test_grant_refusals() -> None:
    """Unreadable input, a shell event without its command, and an argument on the command line each
    exit 1 with the shared line and the grant's own closing line, and print nothing on stdout."""
    not_json = ask_grant("not json")
    no_command = ask_grant(event(None))
    argument = G.run_gate(event(OWN), args=["--scan"], env={"CLAUDE_PLUGIN_ROOT": str(PLUGIN)})
    expected = {
        "not json": "BROKEN: hook input cannot be used (it is not JSON: Expecting value: line 1 column 1"
        " (char 0)) — fix: this hook reads one PreToolUse event of the shell tool, a JSON object, on stdin;"
        " it has no other mode",
        "no command": "BROKEN: hook input cannot be used (a Bash event must carry a string"
        " tool_input.command) — fix: this hook reads one PreToolUse event of the shell tool, a JSON object,"
        " on stdin; it has no other mode",
        "argument": "BROKEN: misinvocation: --scan — fix: run it with no arguments: it reads one PreToolUse"
        " event of the shell tool on stdin",
    }
    got = {"not json": not_json, "no command": no_command, "argument": argument}
    wrong = [
        f"{name}: {result}"
        for name, result in got.items()
        if (result.code, result.stdout, result.stderr) != (1, "", f"{expected[name]}\n{NOT_GRANTED}\n")
    ]
    assert not wrong, "\n".join(wrong)


@item(
    25, "the grant: no python3, no PyYAML, no shared package — exit 1, nothing granted, its own closing line"
)
def test_grant_absence() -> None:
    """The entry files' C1 and C15 and the shared C2 close with the grant's line; a call that is no match
    runs no preflight, so a missing library costs it nothing."""
    tools = H.scratch_dir()
    for tool in ("sh", "dirname"):
        found = shutil.which(tool)
        assert found, tool
        os.symlink(found, tools / tool)
    no_python = G.run_gate(event(OWN), env={"PATH": str(tools)}, command=[str(tools / "sh"), str(G.wrapper)])
    c1 = (
        "BROKEN: const-locations needs python3 — fix: install Python 3.12 or newer"
        f" (https://www.python.org/downloads/)\n{NOT_GRANTED}\n"
    )
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_library = ask_grant(event(OWN), env={"PYTHONPATH": str(shadow)})
    no_library_other = ask_grant(event("ls"), env={"PYTHONPATH": str(shadow)})
    requirements = PLUGIN / "requirements.txt"
    c2 = (
        "BROKEN: const-locations needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{requirements}' — {GRANT_CLAUSE}\n{NOT_GRANTED}\n"
    )
    hidden = H.scratch_dir()  # a package of the same name first on the path, which cannot be imported
    (hidden / "constitution_layer_kit").mkdir()
    (hidden / "constitution_layer_kit" / "__init__.py").write_text("raise ImportError('simulated absence')\n")
    no_shared = ask_grant(event(OWN), env={"PYTHONPATH": str(hidden)})
    c15 = (
        f"BROKEN: const-locations needs the Python package constitution-layer-kit {REQUIRES} or a later"
        f" {REQUIRES.partition('.')[0]}.x release, and python3 cannot import it — fix: install it for python3"
        f" as {PLUGIN / 'INSTALL.md'} says\n{NOT_GRANTED}\n"
    )
    wrong = [
        f"{name}: {result}"
        for name, result, err in (("C1", no_python, c1), ("C2", no_library, c2), ("C15", no_shared, c15))
        if (result.code, result.stdout, result.stderr) != (1, "", err)
    ]
    if (no_library_other.code, no_library_other.stdout, no_library_other.stderr) != (0, "", ""):
        wrong.append(f"no match, no PyYAML: {no_library_other}")
    assert not wrong, "\n".join(wrong)


@item(26, "the grant: its answer is logged as one record of the grant; a call that is no match leaves none")
def test_grant_log() -> None:
    """Under CLAUDE_PLUGIN_DATA the answer is one JSON line of the log, its gate the grant's, and its
    session, path and transcript the event's; a call the grant does not answer writes no record."""
    data = H.scratch_dir()
    ask_grant(event("ls"), env={"CLAUDE_PLUGIN_DATA": str(data)})
    quiet = not (data / f"{NAMESPACE}.jsonl").exists()
    ask_grant(event(OWN), env={"CLAUDE_PLUGIN_DATA": str(data)})
    records = [
        json.loads(line) for line in (data / f"{NAMESPACE}.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    one = (
        len(records) == 1
        and records[0]["gate"] == "grant-new-document"
        and records[0]["mode"] == "hook"
        and records[0]["session"] == "s1"
        and records[0]["path"] == OWN
        and records[0]["transcript"] == "/t/s1.jsonl"
        and records[0]["stream"] == "stdout"
        and records[0]["text"] + "\n" == ALLOW
    )
    assert quiet and one, f"quiet: {quiet}; records: {records}"


@item(27, "the hooks file wires the grant; neither skill carries allowed-tools")
def test_grant_wiring() -> None:
    """One PreToolUse handler on Bash, filtered to `sh` subcommands, in the exec form with the plugin
    root and an explicit timeout; no other event. Neither skill pre-approves anything, so the model's
    load of a skill asks for no approval."""
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    expected = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "if": "Bash(sh *)",
                            "command": "sh",
                            "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/grant-new-document.sh"],
                            "timeout": 30,
                        }
                    ],
                }
            ]
        }
    }
    fronts = {
        name: yaml.safe_load(
            (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8").split("---\n")[1]
        )
        for name in ("new-document", "new-kind")
    }
    granting_skill = sorted(name for name, front in fronts.items() if "allowed-tools" in front)
    assert hooks == expected and not granting_skill, f"hooks: {hooks}; allowed-tools in {granting_skill}"


# ---------------------------------------------------------------- the effect report (items 28 on)
# The three rules of MODULE.md §13, each run through `effect-report.sh` over hand-made transcripts and a
# fake `claude`. The lines asserted are typed by hand.

WAY_AT = "2026-11-03T10:00:00.000Z"
CREATOR = f"sh {PLUGIN}/scripts/new-document.sh"


def tr_tool(sid: str, cwd: Path, call_id: str, name: str, **given: object) -> str:
    """A tool call of any tool, with its input as given."""
    block = {"type": "tool_use", "id": call_id, "name": name, "input": given}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def plugin_list(*, enabled: bool | None) -> dict[str, str]:
    """The environment of a fake `claude` that lists this plugin enabled or disabled, or lists none."""
    listed = [] if enabled is None else [{"id": "const-locations@m", "enabled": enabled}]
    return fake_claude(H.scratch_dir(), f"echo {shlex.quote(json.dumps(listed))}\n")


def effect_lines(root: Path, sessions: dict[str, list[str]], env: dict[str, str] | None = None) -> list[str]:
    """The lines of the report over the sessions, one transcript each; the report must exit 0."""
    folder = H.scratch_dir()
    for name, lines in sessions.items():
        (folder / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder)],
        env={"CLAUDE_PLUGIN_DATA": str(H.scratch_dir()), **(env or plugin_list(enabled=None))},
        command=[H.sh, str(SCRIPTS / "effect-report.sh")],
        cwd=root,
    )
    assert result.code == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def tr_write(sid: str, root: Path, call_id: str, tool: str, rel: str) -> str:
    block = {"type": "tool_use", "id": call_id, "name": tool, "input": {"file_path": str(root / rel)}}
    return tr_line("assistant", sid, root, WAY_AT, message={"role": "assistant", "content": [block]})


@item(
    28, "W1: a command that runs new-document.sh is applied; a Write that creates a document is missed by B6"
)
def test_effect_w1() -> None:
    """Over a hand-made transcript: a shell command that runs the create command is applied; a `Write`
    that creates a Markdown file in the territory of a policy with a derivable home, with no earlier
    read, write or edit of it, is missed by B6. A dry run, a `Write` after a `Read` of the file, a
    `Write` in a single-path territory, one outside any territory and a file that is no Markdown are no
    moment.

    Notes are a directory territory, so the command derives a home there. Applied: the command. Missed
    by B6: a Write of a new note, and one through a worktree of the project. No moment: a dry run, a Write
    after a Read of the file, a Write after a Write of it, a Write outside any territory and a file that is
    no Markdown. Where a policy claims one path, the command has no home and a Write there is no moment."""
    root = prepared().root
    sid = "s28"
    lines = [
        tr_tool(sid, root, "c1", "Bash", command=f"{CREATOR} --kind notes-policy --stem a --title 'A'"),
        tr_tool(sid, root, "c2", "Bash", command=f"{CREATOR} --kind notes-policy --stem a --dry-run"),
        tr_tool(sid, root, "c3", "Bash", command="cat scripts/new-document.sh"),
        tr_write(sid, root, "w1", "Write", "docs/notes/b.md"),
        tr_write(sid, root, "w2", "Write", ".claude/worktrees/w/docs/notes/c.md"),
        tr_write(sid, root, "r1", "Read", "docs/notes/d.md"),
        tr_write(sid, root, "w3", "Write", "docs/notes/d.md"),
        tr_write(sid, root, "w4", "Write", "docs/notes/e.md"),
        tr_write(sid, root, "w5", "Write", "docs/notes/e.md"),
        tr_write(sid, root, "w6", "Write", "docs/other/f.md"),
        tr_write(sid, root, "w7", "Write", "docs/notes/g.txt"),
    ]
    found = effect_lines(root, {sid: lines})
    assert "  W1 (pattern): 4 moment(s): 1 applied, 0 bypassed, 3 missed — B6 3" in found, found
    single = prepared(claim(["docs/one.md"])).root
    again = [tr_write("s28b", single, "w1", "Write", "docs/one.md")]
    other = effect_lines(single, {"s28b": again})
    assert "  W1 (pattern): 0 moment(s): 0 applied, 0 bypassed, 0 missed" in other, other


@item(29, "W2: a creation after a load of new-document is applied; with none, or another skill, missed by B5")
def test_effect_w2() -> None:
    """The moments of W1. A Skill call for `new-document`, in full or bare, before a command or a Write
    makes it applied; none before, or the load of another skill, makes it missed by B5."""
    root = prepared().root
    new = f"{CREATOR} --kind notes-policy --stem a --title 'A'"
    sessions = {
        "s29a": [
            tr_tool("s29a", root, "k", "Skill", skill="const-locations:new-document"),
            tr_tool("s29a", root, "c", "Bash", command=new),
            tr_write("s29a", root, "w", "Write", "docs/notes/b.md"),
        ],
        "s29b": [
            tr_tool("s29b", root, "k", "Skill", skill="new-document"),
            tr_write("s29b", root, "w", "Write", "docs/notes/b.md"),
        ],
        "s29c": [tr_tool("s29c", root, "c", "Bash", command=new)],
        "s29d": [
            tr_tool("s29d", root, "k", "Skill", skill="const-locations:new-kind"),
            tr_write("s29d", root, "w", "Write", "docs/notes/b.md"),
        ],
    }
    found = effect_lines(root, sessions)
    assert "  W2 (pattern): 5 moment(s): 3 applied, 0 bypassed, 2 missed — B5 2" in found, found


@item(30, "W3: the plugin listed enabled is applied, listed disabled bypassed by B2; the dials add no moment")
def test_effect_w3() -> None:
    """A fake `claude` lists the plugin: enabled, one applied moment; disabled, one bypassed by B2; not
    listed, none. A commit of the dials file that changes the namespace is no moment, since the module has
    no severity to lower."""
    root = prepared(own(templates=[])).root
    consumer_dials = root / "constitution.yaml"
    consumer_dials.write_text(dials_text(own(templates=[{"policy": "notes-policy", "template": TEMPLATE}])))
    subprocess.run(["git", "commit", "-qam", "dials"], cwd=root, check=True)
    counts = {
        True: "  W3 (pattern): 1 moment(s): 1 applied, 0 bypassed, 0 missed",
        False: "  W3 (pattern): 1 moment(s): 0 applied, 1 bypassed, 0 missed — B2 1",
        None: "  W3 (pattern): 0 moment(s): 0 applied, 0 bypassed, 0 missed",
    }
    wrong = []
    for enabled, line in counts.items():
        found = effect_lines(root, {}, plugin_list(enabled=enabled))
        if line not in found:
            wrong.append(f"{enabled}: {found}")
    assert not wrong, "\n".join(wrong)
