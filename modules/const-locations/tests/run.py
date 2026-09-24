#!/usr/bin/env python3
"""Fixtures of const-locations: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one: three policies, two of them overlapping, which is
the overlap the generator refuses. This module is only a generator — no hook event, no
verdict, no scan — so the shared items about hook input, paths and skips, the warn channel
and the scan are not its own and are left out; their numbers stay free. `gate_on` turns the
Write the shared items hand it into the generator's command line, run from inside the consumer.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.model import Broken, Finding  # noqa: E402
from consumer import ROOT_POLICY, Consumer, document  # noqa: E402
from harness import Assertion, Edit, Harness, Result, Write, broken_first_line, expect  # noqa: E402
from locations_gate import messages, start  # noqa: E402
from locations_gate.dials import KEYS  # noqa: E402
from locations_gate.model import ActKey  # noqa: E402
from shared_items import Subject, shared_assertions  # noqa: E402

identity.declare(start.GENERATOR)  # the expected messages are built by the same functions the generator uses
H = Harness(SCRIPTS, "new-document.sh", "new-document.py", start.GENERATOR.namespace)
NAMESPACE = start.GENERATOR.namespace

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
    "L5.2": f"BROKEN: {AT} is not inside a git repository — fix: run it from inside the repository the"
    " document belongs to",
    "L5.3": f"BROKEN: no constitution.yaml in {AT}: no kind is declared — fix: a document is created into a"
    " policy's territory; declare the root policy and the kind's policy first — the new-kind procedure",
    "L5.4": "BROKEN: constitution.yaml names no root_policy: no policy claims anything — fix: set"
    " root_policy: <path of the policy for policies>",
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
    "L5.8": "BROKEN: notes-policy's territory 'packages/*/README.md' has a free segment, and --segment was"
    " not given: the pattern fixes the file name and leaves that one segment to be named — fix: run it"
    " with --segment <the segment>; the file name is the pattern's, so --stem is not taken",
    "L5.9": "BROKEN: --stem was given, but notes-policy's territory 'packages/*/README.md' fixes the file"
    " name 'README' — fix: drop --stem and give --segment",
    "L5.10 stem": "BROKEN: 'Bad_Stem' is not a kebab-case name for the stem" + KEBAB,
    "L5.10 id": "BROKEN: 'x--y' is not a kebab-case name for the id" + KEBAB,
    "L5.10 segment": "BROKEN: 'Bad_Name' is not a kebab-case name for the segment" + KEBAB,
    "L5.11": "BROKEN: docs/notes/a.md already exists: creating never overwrites, so the document that is"
    " there stays as it is — fix: choose another stem, or edit the document that is there",
    "L5.12": "BROKEN: docs/notes/shared/b.md would also lie in notes-policy's territory ('docs/notes/**'):"
    " two policies would govern it — fix: territories never overlap; narrow one of them in"
    " constitution.yaml before creating documents there",
    "L5.13": "BROKEN: notes-policy has no template, and --type was not given: without a template nothing but"
    " the policy's prose says which meta-type the kind is — fix: run it with --type current-state,"
    " task-record or non-authoritative — docs/policies/notes-policy.md says which its kind is",
    "L5.14": "BROKEN: --type current-state was given, but the template tpl/record.md fixes type:"
    " task-record, and a kind has one meta-type — fix: drop --type; the template decides",
    "L5.15 missing": "BROKEN: the template of notes-policy, tpl/record.md, does not exist — fix: point"
    " const-locations.templates at a Markdown file of this repository, or remove the entry",
    "L5.15 unreadable": "BROKEN: the template of notes-policy, tpl/record.md, cannot be read ('utf-8' codec"
    " can't decode byte 0xff in position 222: invalid start byte) — fix: point const-locations.templates"
    " at a Markdown file of this repository, or remove the entry",
    "L5.16": "BROKEN: the template tpl/record.md opens with no readable envelope (none) — fix: a template"
    " opens with the YAML block a document of its kind carries — id, type, title, status — with"
    " placeholders where the writer fills",
    "L5.17": "BROKEN: the template tpl/record.md carries type 'ruling', which is no meta-type — fix: set"
    " type: current-state, task-record or non-authoritative in the template",
    "L5.18": "BROKEN: --title was not given, and the envelope is written with the title as a value — fix:"
    " run it with --title '<the document's title>'; a dry run needs none",
    "L5.19": "BROKEN: id 'a' is already carried by docs/notes/other.md — fix: ids are unique in the tree:"
    " choose another stem, or give --id",
    "L5.20": "BROKEN: docs/notes/a.md could not be written ([Errno 13] Permission denied:"
    f" '{AT}/docs/notes'): the write is the last act, so the refusal leaves nothing behind — fix: check"
    " the directory's permissions; nothing else was changed",
    "L5.21": "BROKEN: --segment was given, but notes-policy's territory 'docs/notes/**' has no free segment:"
    " the home is the directory and the stem — fix: drop --segment and give --stem",
    "L5.22": "BROKEN: --title is empty (or only whitespace), and the title is the envelope's one non-empty"
    " line — fix: run it with --title '<the document's title>'",
    "L5.23": "BROKEN: --title holds a line break, and a title is one line — fix: give the title on one line",
    "L5.24": "BROKEN: notes-policy claims no territory: its namespace in constitution.yaml has no territory,"
    " so no home follows — fix: under notes-policy: in constitution.yaml write territory: ['<dir>/**'],"
    " <dir> being the directory its documents live in",
    "C5.a": "BROKEN: constitution.yaml: const-locations.bogus is not a dial of this module (known: log_dir,"
    " templates); a misspelt dial is never a setting ignored in silence — fix: remove or rename the key",
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
    "C5.d repeated": "BROKEN: constitution.yaml: const-locations.templates[1] names policy 'notes-policy' a"
    " second time" + ENTRY,
    "C5.d outside": "BROKEN: constitution.yaml: const-locations.templates[0] names a template outside the"
    " repository" + ENTRY,
}
COMPARED: set[str] = set()  # the handles the items passed to `broken`; the last item compares it with GOLDEN


def broken(result: Result, failure: Broken, handle: str, at: str = "") -> tuple[bool, str]:
    """The refusal's line first, as the function builds it and as GOLDEN types it — `at` filling the
    directory a line names — then the closing line."""
    COMPARED.add(handle)
    typed = GOLDEN.get(handle)
    if typed is None:
        return False, f"{handle}: no line typed in GOLDEN"
    ok, evidence = broken_first_line(result, failure.render())
    golden = typed.replace(AT, at)
    first = result.stderr.splitlines()[0] if result.stderr else ""
    if ok and first != golden:
        ok, evidence = False, f"{handle}: the first line is not the one typed here, {golden!r}: {first}"
    closed = messages.l4_nothing_written() in result.stderr
    return ok and closed, evidence if closed else f"no closing line after: {evidence}"


def all_of(results: list[tuple[bool, str]], summary: str) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, "; ".join(failed) or summary


def tree_state(consumer: Consumer) -> str:
    done = subprocess.run(
        ["git", "status", "--porcelain"], cwd=consumer.root, capture_output=True, text=True, check=True
    )
    return done.stdout


def created(
    consumer: Consumer, rel: str, expected: str, result: Result, lines: Sequence[str]
) -> tuple[bool, str]:
    path = consumer.root / rel
    if result.code != 0:
        return False, f"exit {result.code}: {result.stdout}{result.stderr}".strip()
    if not path.is_file():
        return False, f"{rel} was not created"
    text = path.read_text(encoding="utf-8")
    if text != expected:
        return False, f"{rel} holds:\n{text}\nexpected:\n{expected}"
    missing = [line for line in lines if line not in result.stdout]
    return (
        not missing,
        f"created {rel}, {len(lines)} lines as designed" if not missing else f"missing: {missing}",
    )


# ---------------------------------------------------------------- the module's own items


def directory_prefix() -> tuple[bool, str]:
    consumer = prepared()
    return created(consumer, NOTE, NOTE_TEXT, run(consumer, *NOTE_ARGS), NOTE_LINES)


def prefix_forms() -> tuple[bool, str]:
    """<dir>/**/*.md is a prefix too; a leading slash anchors and is no part of the home."""
    results = []
    for pattern in ("docs/notes/**/*.md", "/docs/notes/**"):
        consumer = prepared(claim([pattern]))
        result = run(consumer, *NOTE_ARGS)
        lines = [messages.l1_home(NOTE, "notes-policy", pattern), messages.l3_created(NOTE)]
        results.append(created(consumer, NOTE, NOTE_TEXT, result, lines))
    return all_of(results, "both forms give docs/notes/a.md")


def free_segment() -> tuple[bool, str]:
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
    made = created(consumer, home, expected, result, [messages.l1_home(home, "notes-policy", pattern)])
    stem = broken(
        run(prepared(patch), "--kind", "notes-policy", "--stem", "z", "--title", "T"),
        messages.l5_stem_not_taken("notes-policy", pattern, "README"),
        "L5.9",
    )
    none = broken(
        run(prepared(patch), "--kind", "notes-policy", "--title", "T"),
        messages.l5_segment_needed("notes-policy", pattern),
        "L5.8",
    )
    mirror = broken(
        run(prepared(), "--kind", "notes-policy", "--stem", "a", "--segment", "x", "--title", "T"),
        messages.l5_segment_not_taken("notes-policy", "docs/notes/**"),
        "L5.21",
    )
    return all_of(
        [made, stem, none, mirror],
        "the segment fills the home, the id is NAME-<segment> lowered, --stem refused there, --segment"
        " refused on a directory kind, --segment required",
    )


def no_home() -> tuple[bool, str]:
    single = broken(
        run(prepared(claim(["docs/one.md"])), *NOTE_ARGS),
        messages.l5_single_path("notes-policy", "docs/one.md"),
        "L5.6",
    )
    results = [single]
    for territory, handle in (
        (["docs/notes/**", "docs/more/**"], "L5.7 two"),
        (["docs/notes/**", "!docs/notes/x.md"], "L5.7 negation"),
        (["docs/notes/*-note.md"], "L5.7 glob"),
        (["docs/notes/"], "L5.7 directory"),
    ):
        result = run(prepared(claim(territory)), *NOTE_ARGS)
        results.append(broken(result, messages.l5_no_home("notes-policy", territory), handle))
    namespaces: list[dict[str, object]] = [{"notes-policy": {}}, claim([])]  # no territory line; an empty one
    for namespace in namespaces:
        result = run(prepared(namespace), *NOTE_ARGS)
        results.append(broken(result, messages.l5_no_territory("notes-policy"), "L5.24"))
    return all_of(
        results,
        "a single path, two patterns, a negation, a glob in the name, a bare directory, no territory: each"
        " refused",
    )


def from_template() -> tuple[bool, str]:
    consumer = prepared(
        own(templates=[{"policy": "notes-policy", "template": TEMPLATE}]), files={TEMPLATE: TEMPLATE_TEXT}
    )
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
    return created(consumer, NOTE, expected, result, [messages.l2_template(TEMPLATE)])


def template_refusals() -> tuple[bool, str]:
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
    return all_of(
        [
            *(broken(r, f, h) for r, f, h in pairs),
            (tree_state(not_utf8) == "", "a template that is not UTF-8 changed the tree"),
        ],
        "no type, a conflicting type, a bad type, no envelope, a missing template, a template that is not"
        " UTF-8: each refused",
    )


def proof_refusals() -> tuple[bool, str]:
    overlap = run(
        prepared(), "--kind", "shared-policy", "--stem", "b", "--title", "B", "--type", "non-authoritative"
    )
    exists = run(prepared(files={NOTE: NOTE_TEXT}), *NOTE_ARGS)
    other = document("# Other\n", id="a", type="non-authoritative", title="Other", status="active")
    in_use = run(prepared(files={"docs/notes/other.md": other}), *NOTE_ARGS)
    return all_of(
        [
            broken(
                overlap,
                messages.l5_two_policies("docs/notes/shared/b.md", "notes-policy", "docs/notes/**"),
                "L5.12",
            ),
            broken(exists, messages.l5_exists(NOTE), "L5.11"),
            broken(in_use, messages.l5_id_in_use("a", "docs/notes/other.md"), "L5.19"),
        ],
        "an overlap, an existing file and an id in use: each refused",
    )


def dry_run() -> tuple[bool, str]:
    consumer = prepared()
    result = run(consumer, "--kind", "notes-policy", "--stem", "a", "--dry-run")
    lines = [
        messages.l1_home(NOTE, "notes-policy", "docs/notes/**"),
        messages.l2_no_template("notes-policy"),
        messages.l4_dry_run(),
    ]
    ok = (
        result.code == 0
        and all(line in result.stdout for line in lines)
        and not (consumer.root / NOTE).exists()
        and tree_state(consumer) == ""
    )
    return (
        ok,
        "exit 0, the three lines, nothing written" if ok else f"{result}; tree: {tree_state(consumer)!r}",
    )


def repository_refusals() -> tuple[bool, str]:
    not_policy = run(prepared(), "--kind", "const-locations", "--stem", "a", "--title", "T")
    consumer = prepared()
    (consumer.root / "constitution.yaml").unlink()
    no_dials = run(consumer, *NOTE_ARGS)
    no_root = run(prepared(raw_dials="notes-policy:\n  territory: ['docs/notes/**']\n"), *NOTE_ARGS)
    outside = H.scratch_dir()
    loose = H.run_gate("", args=NOTE_ARGS, cwd=outside, env={"GIT_CEILING_DIRECTORIES": str(outside.parent)})
    return all_of(
        [
            broken(
                not_policy,
                messages.l5_not_a_policy("const-locations", ["notes-policy", "root-policy", "shared-policy"]),
                "L5.5",
            ),
            broken(no_dials, messages.l5_no_dials(str(consumer.root)), "L5.3", at=str(consumer.root)),
            broken(no_root, messages.l5_no_root_policy(), "L5.4"),
            broken(loose, messages.l5_no_repository(str(outside)), "L5.2", at=str(outside)),
        ],
        "not a policy, no dials file, no root policy, outside any repository: each refused",
    )


def argument_refusals() -> tuple[bool, str]:
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
    return all_of(
        [
            *(broken(r, f, h) for r, f, h in pairs),
            (tree_state(titles) == "", "a refused title changed the tree"),
        ],
        "a bad stem, a bad id, a bad segment, no title, an empty, a blank and a two-line title, no stem: each"
        " refused",
    )


def dial_failures() -> tuple[bool, str]:
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
            [{"policy": "notes-policy", "template": "t.md"}, {"policy": "notes-policy", "template": "u.md"}],
            messages.c5_template_entry(1, messages.entry_repeated("notes-policy")),
            "C5.d repeated",
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
    triples.append((run(prepared(own(bogus=1)), *NOTE_ARGS), messages.c5_unknown_key("bogus", KEYS), "C5.a"))
    triples.append((run(prepared(own(severity="block")), *NOTE_ARGS), messages.c5_severity_here(), "C5.b"))
    return all_of(
        [broken(r, f, h) for r, f, h in triples],
        f"{len(triples)} dial failures, each exit 1 with its own line",
    )


def refusals_leave_the_tree() -> tuple[bool, str]:
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
    return ok, "four refusals, git status empty, no directory made" if ok else f"tree: {state!r}"


def golden_lines() -> tuple[bool, str]:
    """The texts of the module's document, character for character, against what was printed."""
    consumer = prepared()
    out = run(consumer, *NOTE_ARGS).stdout
    refused = run(consumer, *NOTE_ARGS).stderr
    expected_out = "\n".join(NOTE_LINES) + "\n"
    expected_err = GOLDEN["L5.11"] + "\nBROKEN: the document could not be created — nothing was written\n"
    ok = out == expected_out and refused == expected_err
    return ok, "stdout and stderr as designed" if ok else f"stdout:\n{out}\nstderr:\n{refused}"


def every_golden_line_compared() -> tuple[bool, str]:
    """No line of GOLDEN typed and left unused: each was compared by an item before this one."""
    unused = sorted(set(GOLDEN) - COMPARED)
    return not unused, (
        f"{len(GOLDEN)} refusal lines, each compared by items 3, 4, 6, 7, 9–11 and 16"
        if not unused
        else f"typed in GOLDEN, compared by no item: {unused}"
    )


def closing_is_the_generators() -> tuple[bool, str]:
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
    return (
        own_line and "pass unchecked" not in sources and library_clause,
        "closing line the generator's; entry files without the gate's clause; C2 closed by the generator's",
    )


def write_refused() -> tuple[bool, str]:
    """A write the system refuses is L5.20, and leaves nothing: no file, no directory made for it."""
    if os.geteuid() == 0:
        return (
            True,
            "NOT EXERCISED: running as root, where a mode bit does not deny a write — 0 writes examined",
        )
    consumer = prepared()
    docs = consumer.root / "docs"
    os.chmod(docs, 0o500)  # docs/notes cannot be made
    try:
        result = run(consumer, *NOTE_ARGS)
    finally:
        os.chmod(docs, 0o755)  # the runner's cleanup cannot remove what it may not write into
    error = f"[Errno 13] Permission denied: '{docs}/notes'"
    ok, evidence = broken(result, messages.l5_could_not_write(NOTE, error), "L5.20", at=str(consumer.root))
    state = tree_state(consumer)
    problems = [
        *([] if ok else [evidence]),
        *([] if state == "" else [f"tree: {state!r}"]),
        *(["docs/notes was left behind"] if (docs / "notes").exists() else []),
    ]
    return not problems, "; ".join(problems) or f"{evidence}; git status empty, no directory made"


def notes_are_printed() -> tuple[bool, str]:
    """A policy document without a readable id earns the shared note, on stdout, before the lines."""
    consumer = prepared(files={"docs/policies/zz-no-id.md": "# no envelope\n"})
    result = run(consumer, *NOTE_ARGS)
    note = shared.n1_note_policy_without_id("docs/policies/zz-no-id.md")
    return expect(result, 0, note, "stdout")


OWN: list[tuple[str, Callable[[], tuple[bool, str]]]] = [
    (
        "a directory-prefix territory: the four-field envelope, the heading body, lines L1–L4",
        directory_prefix,
    ),
    ("<dir>/**/*.md and a leading slash are prefixes too", prefix_forms),
    (
        "one free segment: the home filled, the id derived, --stem and --segment refused where not taken",
        free_segment,
    ),
    ("a single path and every fourth-class territory: no home, refused and taught", no_home),
    ("a template: the command's id, title and status, the template's type, the rest verbatim", from_template),
    (
        "no type, a conflicting type, a bad type, no envelope, a missing template, one not UTF-8",
        template_refusals,
    ),
    ("an overlap, an existing file, an id in use", proof_refusals),
    ("--dry-run prints the home and the template and writes nothing", dry_run),
    ("not a policy, no dials file, no root policy, outside any repository", repository_refusals),
    ("a stem, an id, a segment, a title, a missing stem", argument_refusals),
    ("the dials: an unknown key, severity, and every shape of a bad templates entry", dial_failures),
    ("every refusal leaves the tree as it was", refusals_leave_the_tree),
    ("golden lines: stdout and stderr character for character", golden_lines),
    (
        "the closing line is the generator's own; the entry files drop the gate's clause",
        closing_is_the_generators,
    ),
    ("a note of the policy index is printed before the lines", notes_are_printed),
    ("a write the system refuses is refused in turn, and leaves nothing behind", write_refused),
    # stays the last entry: it reads what every item before it compared; new items go above it
    (
        "golden lines: every refusal line typed here was compared by an earlier item",
        every_golden_line_compared,
    ),
]

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
)


def main() -> int:
    assertions = [Assertion(n + 1, title, check) for n, (title, check) in enumerate(OWN)]
    assertions += shared_assertions(SUBJECT, 101)
    return H.run_all([], assertions)


if __name__ == "__main__":
    sys.exit(main())
