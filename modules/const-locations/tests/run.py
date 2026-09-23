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


def broken(result: Result, failure: Broken) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, failure.render())
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
    )
    none = broken(
        run(prepared(patch), "--kind", "notes-policy", "--title", "T"),
        messages.l5_segment_needed("notes-policy", pattern),
    )
    mirror = broken(
        run(prepared(), "--kind", "notes-policy", "--stem", "a", "--segment", "x", "--title", "T"),
        messages.l5_segment_not_taken("notes-policy", "docs/notes/**"),
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
    )
    results = [single]
    for territory in (
        ["docs/notes/**", "docs/more/**"],
        ["docs/notes/**", "!docs/notes/x.md"],
        ["docs/notes/*-note.md"],
        ["docs/notes/"],
    ):
        result = run(prepared(claim(territory)), *NOTE_ARGS)
        results.append(broken(result, messages.l5_no_home("notes-policy", territory)))
    namespaces: list[dict[str, object]] = [{"notes-policy": {}}, claim([])]  # no territory line; an empty one
    for namespace in namespaces:
        result = run(prepared(namespace), *NOTE_ARGS)
        results.append(broken(result, messages.l5_no_territory("notes-policy")))
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
    pairs = [
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "a", "--title", "T"),
            messages.l5_type_needed("notes-policy", "docs/policies/notes-policy.md"),
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
        ),
        (
            run(prepared(with_template), "--kind", "notes-policy", "--stem", "a", "--title", "T"),
            messages.l5_template_missing("notes-policy", TEMPLATE),
        ),
    ]
    return all_of(
        [broken(r, f) for r, f in pairs],
        "no type, a conflicting type, a bad type, no envelope, a missing template: each refused",
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
                overlap, messages.l5_two_policies("docs/notes/shared/b.md", "notes-policy", "docs/notes/**")
            ),
            broken(exists, messages.l5_exists(NOTE)),
            broken(in_use, messages.l5_id_in_use("a", "docs/notes/other.md")),
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
            ),
            broken(no_dials, messages.l5_no_dials(str(consumer.root))),
            broken(no_root, messages.l5_no_root_policy()),
            broken(loose, messages.l5_no_repository(str(outside))),
        ],
        "not a policy, no dials file, no root policy, outside any repository: each refused",
    )


def argument_refusals() -> tuple[bool, str]:
    pairs = [
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "Bad_Stem", "--title", "T"),
            messages.l5_not_kebab("Bad_Stem", "the stem"),
        ),
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "a", "--title", "T", "--id", "x--y"),
            messages.l5_not_kebab("x--y", "the id"),
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
        ),
        (
            run(prepared(), "--kind", "notes-policy", "--stem", "a", "--type", "non-authoritative"),
            messages.l5_title_needed(),
        ),
        (
            run(prepared(), "--kind", "notes-policy", "--title", "T"),
            messages.l5_usage("--stem was not given"),
        ),
    ]
    titles = prepared()  # an empty title, one of whitespace — in a dry run too — and one of two lines
    for title, failure in (
        ("", messages.l5_title_empty()),
        ("  ", messages.l5_title_empty()),
        ("a\nb", messages.l5_title_multiline()),
    ):
        pairs.append((run(titles, "--kind", "notes-policy", "--stem", "a", "--title", title), failure))
    pairs.append(
        (
            run(titles, "--kind", "notes-policy", "--stem", "a", "--title", "", "--dry-run"),
            messages.l5_title_empty(),
        )
    )
    return all_of(
        [*(broken(r, f) for r, f in pairs), (tree_state(titles) == "", "a refused title changed the tree")],
        "a bad stem, a bad id, a bad segment, no title, an empty, a blank and a two-line title, no stem: each"
        " refused",
    )


def dial_failures() -> tuple[bool, str]:
    entries: list[tuple[object, Broken]] = [
        ("x", messages.c5_templates_shape()),
        (["x"], messages.c5_template_entry(0, messages.entry_not_a_mapping())),
        ([{"template": "t.md"}], messages.c5_template_entry(0, messages.entry_missing("policy"))),
        ([{"policy": "notes-policy"}], messages.c5_template_entry(0, messages.entry_missing("template"))),
        (
            [{"policy": "notes-policy", "template": "t.md", "type": "x"}],
            messages.c5_template_entry(0, messages.entry_unknown_key("type")),
        ),
        (
            [{"policy": "notes-policy", "template": "t.md"}, {"policy": "notes-policy", "template": "u.md"}],
            messages.c5_template_entry(1, messages.entry_repeated("notes-policy")),
        ),
        (
            [{"policy": "notes-policy", "template": "../t.md"}],
            messages.c5_template_entry(0, messages.entry_outside()),
        ),
    ]
    pairs = [(run(prepared(own(templates=value)), *NOTE_ARGS), failure) for value, failure in entries]
    pairs.append((run(prepared(own(bogus=1)), *NOTE_ARGS), messages.c5_unknown_key("bogus", KEYS)))
    pairs.append((run(prepared(own(severity="block")), *NOTE_ARGS), messages.c5_severity_here()))
    return all_of(
        [broken(r, f) for r, f in pairs], f"{len(pairs)} dial failures, each exit 1 with its own line"
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
    expected_err = (
        "BROKEN: docs/notes/a.md already exists: creating never overwrites, so the document that is there"
        " stays as it is — fix: choose another stem, or edit the document that is there\n"
        "BROKEN: the document could not be created — nothing was written\n"
    )
    ok = out == expected_out and refused == expected_err
    return ok, "stdout and stderr as designed" if ok else f"stdout:\n{out}\nstderr:\n{refused}"


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
    ("no type, a conflicting type, a bad type, no envelope, a missing template", template_refusals),
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
