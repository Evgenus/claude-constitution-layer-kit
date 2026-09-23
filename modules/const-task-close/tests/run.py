#!/usr/bin/env python3
"""Fixtures of const-task-close: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

The fixture consumer is the shared one, its branch renamed to main so that the trunk dial's
default applies; its three policies matter to nothing here, since this gate reads only its own
dials. The gate is driven by Stop, which names no file: `gate_on` turns the Write the shared
items hand it into the tree the hook passes — everything committed — or blocks — one untracked
file — and the items about a written file are left out, their numbers kept free. The scan's
cases make their own commits, branches and merges with git.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.model import Broken, Finding  # noqa: E402
from consumer import Consumer  # noqa: E402
from harness import (  # noqa: E402
    Assertion,
    Edit,
    Harness,
    Result,
    Write,
    broken_first_line,
    expect,
    stop_json,
)
from shared_items import Subject, shared_assertions  # noqa: E402
from task_close_gate import messages, start  # noqa: E402
from task_close_gate.model import BODY, Declaration, Pair  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-task-close.sh", "check-task-close.py", start.GATE.namespace)
NS = start.GATE.namespace
KEY = "No-Doc-Impact"
CORE = {"name": "core", "code": ["src/**"], "docs": ["docs/core.md"]}
PAIR = Pair("core", ("src/**",), ("docs/core.md",))
GIT_ENV = {
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "LC_ALL": "C",
}
VALID = Write("docs/notes/kept.md", "# kept\n")  # committed by gate_on: a clean tree
RED = Write("scratch.txt", "scratch\n")  # left untracked by gate_on: a dirty tree
RED_LINES = ["?? scratch.txt"]


# ------------------------------------------------------------------ helpers


def git(root: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, **GIT_ENV},
    )


def dials_text(patch: Mapping[str, object] | None = None) -> str:
    dials: dict[str, object] = {**Consumer(Path()).dials, NS: {}, **(patch or {})}
    return yaml.safe_dump(dials, sort_keys=False, allow_unicode=True)


def own(**dials: object) -> dict[str, object]:
    return {NS: {**dials}}


def with_map(*pairs: object, **more: object) -> dict[str, object]:
    return own(coverage=list(pairs) if pairs else [CORE], **more)


def repo(
    patch: Mapping[str, object] | None = None,
    raw: str | None = None,
    files: Mapping[str, str] | None = None,
) -> Consumer:
    """A consumer on branch main with the dials and the map's documents committed."""
    consumer = H.fresh_consumer()
    git(consumer.root, "branch", "-M", "main")
    consumer.write("constitution.yaml", raw if raw is not None else dials_text(patch))
    for rel, text in {"docs/core.md": "# core\n", "src/a.py": "x = 1\n", **(files or {})}.items():
        consumer.write(rel, text)
    commit(consumer.root, "setup")
    return consumer


def commit(
    root: Path, message: str, files: Mapping[str, str] | None = None, remove: Sequence[str] = ()
) -> str:
    """Writes, removes, stages everything and commits with the message as given — trailers and
    all; returns the short hash."""
    for rel, text in (files or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for rel in remove:
        (root / rel).unlink()
    git(root, "add", "-A")
    done = git(root, "commit", "-q", "--allow-empty", "-F", "-", stdin=message)
    assert done.returncode == 0, done.stderr
    return git(root, "rev-parse", "--short", "HEAD").stdout.strip()


def branch(root: Path, name: str = "work/x") -> None:
    assert git(root, "checkout", "-q", "-b", name).returncode == 0


def checkout(root: Path, name: str) -> None:
    assert git(root, "checkout", "-q", name).returncode == 0


def merge(root: Path, name: str = "work/x", into: str = "main") -> str:
    checkout(root, into)
    done = git(root, "merge", "-q", "--no-ff", name, "-m", f"Work: {name}")
    assert done.returncode == 0, done.stderr
    return git(root, "rev-parse", "--short", "HEAD").stdout.strip()


def short(root: Path, ref: str = "HEAD") -> str:
    return git(root, "rev-parse", "--short", ref).stdout.strip()


def scan(root: Path, *args: str, env: Mapping[str, str] | None = None) -> Result:
    return H.run_gate("", args=["--scan", str(root), *args], env=dict(env) if env else None)


def hook(root: Path, active: bool = False, env: Mapping[str, str] | None = None) -> Result:
    return H.run_gate(stop_json(root, active), env=dict(env) if env else None)


def trailer(pair: str = "core", reason: str = "a helper only, the page describes the interface") -> str:
    return f"{KEY}: {pair} — {reason}"


def t2(touched: Sequence[str] = ("src/a.py",), pair: Pair = PAIR) -> Finding:
    return messages.t2_not_updated(pair, list(touched), KEY)


def declared(where: str, pair: str, reason: str) -> Declaration:
    return Declaration(where, f"{pair} — {reason}", pair, reason)


def broken(result: Result, failure: Broken) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, failure.render())
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def all_of(results: list[tuple[bool, str]], summary: str) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, failed[0] if failed else summary


def green_scan(result: Result, tail: str) -> tuple[bool, str]:
    return expect(result, 0, shared.g1_green_scan(tail), "stdout")


def red_scan(result: Result, *findings: Finding) -> tuple[bool, str]:
    missing = [f.key for f in findings if f.render() not in result.stdout]
    ok = result.code == 2 and not missing
    return ok, f"exit 2 teaching {[f.key.value for f in findings]}" if ok else (
        f"wanted exit 2 with {missing or 'the findings'}; got exit {result.code}:"
        f" {result.stdout}{result.stderr}"
    )


# ------------------------------------------------------------------ the specification's four


def spec_update() -> tuple[bool, str]:
    """A code-touching change without a document update or a declaration is red; with the
    update, green."""
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "code only", {"src/a.py": "x = 2\n"})
    red = red_scan(scan(r.root), t2())
    commit(r.root, "the page", {"docs/core.md": "# core, updated\n"})
    green = green_scan(scan(r.root), messages.f9_scan_tail(1, 2, short(r.root, "main"), short(r.root), False))
    return all_of([red, green], "red→green: T2, then the document updated")


def spec_trailer() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "code only", {"src/a.py": "x = 2\n"})
    red = red_scan(scan(r.root), t2())
    where = "commit " + commit(r.root, "declare\n\n" + trailer())
    result = scan(r.root)
    note = messages.n1_declared(
        declared(where, "core", "a helper only, the page describes the interface"), True
    )
    green = green_scan(result, messages.f9_scan_tail(1, 2, short(r.root, "main"), short(r.root), False))
    noted = (note in result.stdout, f"the note: {note}" if note in result.stdout else result.stdout)
    return all_of([red, green, noted], "red→green: T2, then a trailer on a later commit of the range")


def spec_body() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "code only", {"src/a.py": "x = 2\n"})
    red = red_scan(scan(r.root), t2())
    body = H.scratch_dir() / "body.txt"
    body.write_text(
        "Title\n\nSome text.\n\n" + trailer(reason="via the description") + "\n", encoding="utf-8"
    )
    result = scan(r.root, "--body", str(body))
    note = messages.n1_declared(declared(BODY, "core", "via the description"), True)
    green = green_scan(result, messages.f9_scan_tail(1, 1, short(r.root, "main"), short(r.root), False))
    noted = (note in result.stdout, f"the note: {note}" if note in result.stdout else result.stdout)
    return all_of([red, green, noted], "red→green: T2, then the same line in the body given as a file")


def spec_tree() -> tuple[bool, str]:
    r = repo(own())
    r.write("scratch.txt", "x\n")
    red = expect(hook(r.root), 2, messages.t1_dirty_tree(RED_LINES).render(), "stderr")
    counted = expect(hook(r.root), 2, messages.f9_count_hook(1), "stderr")
    (r.root / "scratch.txt").unlink()
    green = expect(hook(r.root), 0, shared.g1_green_event(messages.g1_clean()), "stdout")
    return all_of([red, counted, green], "red→green: T1 on an untracked file, silent once it is gone")


# ------------------------------------------------------------------ the hook


def second_stop() -> tuple[bool, str]:
    r = repo(own())
    r.write("scratch.txt", "x\n")
    line = shared.g1_green_event(messages.g1_second_stop(1))
    return expect(hook(r.root, active=True), 0, line, "stdout")


def warn_is_notice_alone() -> tuple[bool, str]:
    r = repo(own(severity="warn"))
    r.write("scratch.txt", "x\n")
    result = hook(r.root)
    if result.code != 0:
        return False, f"exit {result.code}: {result.stderr}"
    answer = json.loads(result.stdout)
    body = "\n".join([messages.t1_dirty_tree(RED_LINES).render(), messages.f9_count_hook(1)])
    ok = answer == {"systemMessage": shared.w1_warn_stop(body)}
    return ok, "systemMessage alone, carrying the finding and the count" if ok else f"bad: {answer}"


def ignored_is_clean() -> tuple[bool, str]:
    r = repo(own(), files={".gitignore": "scratch/\n"})
    r.write("scratch/x.txt", "x\n")
    clean = expect(hook(r.root), 0, shared.g1_green_event(messages.g1_clean()), "stdout")
    commit(r.root, "tracked", {"kept.txt": "1\n"})
    (r.root / "kept.txt").write_text("2\n", encoding="utf-8")
    dirty = expect(hook(r.root), 2, messages.t1_dirty_tree([" M kept.txt"]).render(), "stderr")
    return all_of([clean, dirty], "an ignored file is not dirty; a modified tracked one is")


def cwd_below_root() -> tuple[bool, str]:
    r = repo(own())
    r.write("scratch.txt", "x\n")
    result = H.run_gate(stop_json(r.root / "docs"))
    return expect(result, 2, messages.t1_dirty_tree(RED_LINES).render(), "stderr")


def tool_event_is_not_wired() -> tuple[bool, str]:
    r = repo(own())
    event = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "x.md"},
            "cwd": str(r.root),
        }
    )
    return broken(H.run_gate(event), messages.c12_not_wired("PreToolUse"))


def hook_validates_dials() -> tuple[bool, str]:
    r = repo(own(coverag=[]))
    return broken(hook(r.root), messages.c5_unknown_dial("coverag"))


# ------------------------------------------------------------------ the scan's range


def trunk_dial() -> tuple[bool, str]:
    r = repo(with_map(trunk="trunk"))
    git(r.root, "branch", "-M", "trunk")
    branch(r.root)
    commit(r.root, "code only", {"src/a.py": "x = 2\n"})
    named = red_scan(scan(r.root), t2())
    r2 = repo(with_map(trunk="nowhere"))
    branch(r2.root)
    missing = broken(scan(r2.root), messages.c12_no_trunk("nowhere", str(r2.root)))
    return all_of(
        [named, missing], "the trunk dial names the base; an unknown trunk is a configuration failure"
    )


def since_ref() -> tuple[bool, str]:
    r = repo(with_map())
    git(r.root, "tag", "start")
    commit(r.root, "the page", {"docs/core.md": "# core 2\n"})
    commit(r.root, "code", {"src/a.py": "x = 2\n"})
    since_tag = green_scan(
        scan(r.root, "--since", "start"),
        messages.f9_scan_tail(1, 2, short(r.root, "start"), short(r.root), False),
    )
    since_last = red_scan(scan(r.root, "--since", "HEAD~1"), t2())
    return all_of([since_tag, since_last], "--since names the base: a tag, a relative ref")


def change_merge_and_commit() -> tuple[bool, str]:
    """The kit's own form: the declaration on a branch commit, a later commit of the range without
    it, the range examined by the trailer-less merge."""
    r = repo(with_map())
    branch(r.root)
    where = "commit " + commit(r.root, "code\n\n" + trailer(), {"src/a.py": "x = 2\n"})
    commit(r.root, "more code", {"src/b.py": "y\n"})
    merged = merge(r.root)
    result = scan(r.root, "--change", merged)
    note = messages.n1_declared(
        declared(where, "core", "a helper only, the page describes the interface"), True
    )
    whole = green_scan(result, messages.f9_scan_tail(1, 3, short(r.root, "main^1"), merged, False))
    noted = (
        note in result.stdout,
        "the branch commit's trailer read through the merge" if note in result.stdout else result.stdout,
    )
    plain = red_scan(scan(r.root, "--change", "main^2"), t2(["src/b.py"]))
    return all_of(
        [whole, noted, plain],
        "--change: a merge by its first-parent diff, every commit read; a plain commit alone",
    )


def head_on_trunk() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "code", {"src/a.py": "x = 2\n"})
    merge(r.root)
    bare = scan(r.root)
    explicit = scan(r.root, "--change", "HEAD")
    same = bare.code == 2 and bare.stdout == explicit.stdout
    checkout(r.root, "work/x")
    on_branch = green_scan(  # the merge-base is the branch's own tip
        scan(r.root), messages.f9_scan_tail(1, 0, short(r.root), short(r.root), False)
    )
    return all_of(
        [(same, "on the trunk the bare scan is --change HEAD" if same else f"{bare}\n{explicit}"), on_branch],
        "on the trunk: the last landed change; on a merged branch: an empty range, said so",
    )


def nothing_landed_before() -> tuple[bool, str]:
    r = H.fresh_consumer()
    git(r.root, "branch", "-M", "main")
    r.write("constitution.yaml", dials_text(with_map()))
    r.write("docs/core.md", "# core\n")
    git(r.root, "add", "-A")
    git(r.root, "commit", "-q", "--amend", "--no-edit")  # one commit, the root, holding the map
    rooted = green_scan(scan(r.root), messages.f9_scan_tail(1, 0, "", short(r.root), True))
    empty = H.scratch_dir()
    git(empty, "init", "-q")
    (empty / "constitution.yaml").write_text(dials_text(with_map()), encoding="utf-8")
    none = green_scan(scan(empty), messages.f9_scan_tail(1, 0, "HEAD", "HEAD", True))
    return all_of([rooted, none], "a root commit on the trunk, and a repository with no commit yet")


def since_and_change() -> tuple[bool, str]:
    r = repo(with_map())
    return broken(scan(r.root, "--since", "main", "--change", "HEAD"), messages.c12_since_and_change())


def unknown_ref() -> tuple[bool, str]:
    r = repo(with_map())
    since = broken(
        scan(r.root, "--since", "nope"),
        messages.c12_unknown_ref("--since", "nope", str(r.root), "no such ref"),
    )
    change = broken(
        scan(r.root, "--change", "nope"),
        messages.c12_unknown_ref("--change", "nope", str(r.root), "no such ref"),
    )
    return all_of([since, change], "an unknown ref is a configuration failure for both flags")


# ------------------------------------------------------------------ declarations


def trailer_among_others() -> tuple[bool, str]:
    r = repo(
        with_map(
            {"name": "core", "code": ["src/**"], "docs": ["docs/core.md"]},
            {"name": "cli", "code": ["cli/**"], "docs": ["docs/cli.md"]},
        ),
        files={"docs/cli.md": "# cli\n", "cli/m.py": "\n"},
    )
    branch(r.root)
    where = "commit " + commit(
        r.root,
        "both\n\n"
        + trailer("core", "one")
        + "\nCo-Authored-By: Someone <s@example.invalid>\n"
        + trailer("cli", "two")
        + "\n",
        {"src/a.py": "2\n", "cli/m.py": "2\n"},
    )
    result = scan(r.root)
    notes = [
        messages.n1_declared(declared(where, "core", "one"), True),
        messages.n1_declared(declared(where, "cli", "two"), True),
    ]
    ok = result.code == 0 and all(note in result.stdout for note in notes)
    return (
        ok,
        "both trailers read beside Co-Authored-By, one note each" if ok else result.stdout + result.stderr,
    )


def colonless_line_hides_paragraph() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "hidden\n\n" + trailer() + "\nsee the page above\n", {"src/a.py": "2\n"})
    result = scan(r.root)
    return red_scan(result, t2())


def body_forms() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "code", {"src/a.py": "2\n"})
    lower = H.scratch_dir() / "lower.txt"
    lower.write_text("  no-doc-impact: core - lower case, a hyphen\n", encoding="utf-8")
    read = green_scan(
        scan(r.root, "--body", str(lower)),
        messages.f9_scan_tail(1, 1, short(r.root, "main"), short(r.root), False),
    )
    gone = H.scratch_dir() / "gone.txt"
    result = scan(r.root, "--body", str(gone))
    unreadable = result.code == 1 and result.stderr.startswith(
        f"BROKEN: --body names {gone}, which cannot be read ("
    )
    return all_of(
        [
            read,
            (unreadable, "an unreadable body is a configuration failure" if unreadable else result.stderr),
        ],
        "the body's line, any case, any dash; an unreadable body",
    )


def t3_and_t4() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    where = "commit " + commit(
        r.root, "wrong\n\n" + f"{KEY}: nosuch — reason\n{KEY}: core\n", {"src/a.py": "2\n"}
    )
    result = scan(r.root)
    no_pair = messages.t3_names_no_pair(
        Declaration(where, "nosuch — reason", "nosuch", "reason"), KEY, ["core"]
    )
    no_reason = messages.t4_no_reason(Declaration(where, "core", "core", ""), KEY)
    return red_scan(result, no_pair, no_reason, t2())


def untouched_pair_note() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    where = "commit " + commit(r.root, "docs only\n\n" + trailer(reason="nothing"), {"README.md": "x\n"})
    result = scan(r.root)
    note = messages.n1_declared(declared(where, "core", "nothing"), False)
    return expect(result, 0, note, "stdout")


def declaration_key_dial() -> tuple[bool, str]:
    r = repo(with_map(declaration_key="Docs-Stand"))
    branch(r.root)
    commit(r.root, "old key\n\n" + trailer(), {"src/a.py": "2\n"})
    old_ignored = red_scan(scan(r.root), messages.t2_not_updated(PAIR, ["src/a.py"], "Docs-Stand"))
    commit(r.root, "new key\n\nDocs-Stand: core — the new key\n")
    new_read = expect(scan(r.root), 0, "no impact declared in commit", "stdout")
    return all_of([old_ignored, new_read], "the key is the dial's: the default key is then not read")


# ------------------------------------------------------------------ the map


def overlapping_pairs() -> tuple[bool, str]:
    second = {"name": "guide", "code": ["src/**"], "docs": ["docs/guide.md"]}
    r = repo(with_map(CORE, second), files={"docs/guide.md": "# guide\n"})
    branch(r.root)
    commit(r.root, "code", {"src/a.py": "2\n"})
    both = red_scan(scan(r.root), t2(), t2(pair=Pair("guide", ("src/**",), ("docs/guide.md",))))
    commit(
        r.root,
        "one updated, one declared\n\n" + trailer("guide", "the guide is about usage"),
        {"docs/core.md": "# 2\n"},
    )
    green = expect(scan(r.root), 0, "2 pair(s) examined", "stdout")
    return all_of([both, green], "two pairs over one path both apply; each satisfied its own way")


def document_is_no_trigger() -> tuple[bool, str]:
    docs = Pair("docs", ("docs/**",), ("docs/core.md",))
    r = repo(with_map({"name": "docs", "code": ["docs/**"], "docs": ["docs/core.md"]}))
    branch(r.root)
    where = "commit " + commit(
        r.root, "the page alone\n\n" + trailer("docs", "nothing"), {"docs/core.md": "# 2\n"}
    )
    result = scan(r.root)
    note = messages.n1_declared(
        declared(where, "docs", "nothing"), False
    )  # the pair is not covered by its own page
    silent = expect(result, 0, note, "stdout")
    commit(r.root, "another page", {"docs/other.md": "x\n"})
    covered = red_scan(  # since the last commit: the range no longer holds the page's own update
        scan(r.root, "--since", "HEAD~1"), messages.t2_not_updated(docs, ["docs/other.md"], KEY)
    )
    return all_of([silent, covered], "a document inside its own pair's code is not its own trigger")


def deleted_and_renamed_are_touched() -> tuple[bool, str]:
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "delete code", remove=["src/a.py"])
    deleted = red_scan(scan(r.root), t2())
    r2 = repo(with_map())
    branch(r2.root)
    git(r2.root, "mv", "src/a.py", "src/b.py")
    commit(r2.root, "rename code")
    renamed = red_scan(scan(r2.root), t2(["src/a.py", "src/b.py"]))
    r3 = repo(with_map())
    branch(r3.root)
    git(r3.root, "mv", "docs/core.md", "docs/core-2.md")
    commit(r3.root, "rename the page", {"src/a.py": "2\n"})
    doc_moved = expect(scan(r3.root), 0, "1 pair(s) examined", "stdout")
    return all_of([deleted, renamed, doc_moved], "a deleted or renamed path counts as touched, on both sides")


def missing_document() -> tuple[bool, str]:
    r = repo(with_map({"name": "core", "code": ["src/**"], "docs": ["docs/none.md"]}))
    missing = broken(scan(r.root), messages.x1_document_missing("core", "docs/none.md", short(r.root)))
    r2 = repo(with_map())
    branch(r2.root)
    commit(r2.root, "drop the page", remove=["docs/core.md"])
    deleted = expect(scan(r2.root), 0, "1 pair(s) examined", "stdout")
    r3 = repo(with_map())
    first = short(r3.root)
    branch(r3.root)
    commit(r3.root, "the page arrives later", {"docs/later.md": "x\n", "src/a.py": "2\n"})
    merge(r3.root)
    r3.write(
        "constitution.yaml",
        dials_text(with_map({"name": "core", "code": ["src/**"], "docs": ["docs/later.md"]})),
    )
    commit(r3.root, "map grows")
    later = Pair("core", ("src/**",), ("docs/later.md",))
    older = red_scan(scan(r3.root, "--change", first), messages.t2_not_updated(later, ["src/a.py"], KEY))
    return all_of(
        [missing, deleted, older],
        "X1 for a document that never was; not for one the range deleted; an older change judged by"
        " today's map is a finding, never X1",
    )


def empty_map() -> tuple[bool, str]:
    r = repo(own())
    branch(r.root)
    commit(r.root, "code", {"src/a.py": "2\n"})
    return green_scan(scan(r.root), messages.f9_scan_tail_empty())


# ------------------------------------------------------------------ dials


def dial_failures() -> tuple[bool, str]:
    cases: list[tuple[dict[str, object], Broken]] = [
        (own(coverage="x"), messages.c5_coverage_not_a_list()),
        (own(coverage=["x"]), messages.c5_pair(1, messages.pair_not_a_mapping())),
        (own(coverage=[{**CORE, "extra": 1}]), messages.c5_pair(1, messages.pair_unknown_key("extra"))),
        (
            own(coverage=[{"code": ["src/**"], "docs": ["docs/core.md"]}]),
            messages.c5_pair(1, messages.pair_name()),
        ),
        (own(coverage=[{**CORE, "name": "Core Bad"}]), messages.c5_pair(1, messages.pair_name())),
        (own(coverage=[CORE, CORE]), messages.c5_pair(2, messages.pair_name_repeated("core"))),
        (
            own(coverage=[{"name": "core", "docs": ["docs/core.md"]}]),
            messages.c5_pair(1, messages.pair_code()),
        ),
        (
            own(coverage=[{"name": "core", "code": [], "docs": ["docs/core.md"]}]),
            messages.c5_pair(1, messages.pair_code()),
        ),
        (own(coverage=[{"name": "core", "code": ["src/**"]}]), messages.c5_pair(1, messages.pair_docs())),
        (
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": ["/abs.md"]}]),
            messages.c5_pair(1, messages.pair_docs()),
        ),
        (own(trunk=""), messages.c5_trunk()),
        (own(trunk=3), messages.c5_trunk()),
        (own(declaration_key="No Doc"), messages.c5_declaration_key()),
        (own(working_files="x"), messages.c5_working_files()),
    ]
    results = [broken(scan(repo(patch).root), failure) for patch, failure in cases]
    return all_of(results, f"{len(cases)} dial failures, each exit 1 with its own line")


def unreadable_patterns() -> tuple[bool, str]:
    code = broken(
        scan(repo(with_map({**CORE, "code": ["#src/**"]})).root),
        shared.c5_territory_pattern(f"{NS}.coverage[core].code", "#src/**"),
    )
    working = broken(
        scan(repo(own(working_files=["#x"])).root), shared.c5_territory_pattern(f"{NS}.working_files", "#x")
    )
    return all_of([code, working], "a pattern git would misread, in a pair's code and in working_files")


def working_files_note() -> tuple[bool, str]:
    r = repo(own(working_files=["notes/**"]), files={"notes/todo.md": "x\n"})
    r.write("notes/untracked.md", "y\n")
    result = scan(r.root)
    note = messages.n2_working_files(["notes/todo.md"])
    return expect(result, 0, note, "stdout")


def misspelt_dial() -> tuple[bool, str]:
    return broken(scan(repo(own(covrage=[])).root), messages.c5_unknown_dial("covrage"))


# ------------------------------------------------------------------ texts and shape


def golden_lines() -> tuple[bool, str]:
    """Typed by hand: a case that compares with what a message function returns cannot catch a
    wrong text."""
    r = repo(with_map())
    r.write("scratch.txt", "x\n")
    tree = hook(r.root).stderr
    second = hook(r.root, active=True).stdout
    (r.root / "scratch.txt").unlink()
    branch(r.root)
    where = "commit " + commit(
        r.root, "wrong\n\n" + f"{KEY}: nosuch — reason\n{KEY}: core\n", {"src/a.py": "2\n"}
    )
    out = scan(r.root).stdout
    x1 = scan(repo(with_map({**CORE, "docs": ["docs/none.md"]})).root).stderr
    literals = [
        ("RED: the working tree is dirty at turn end — 1 path(s): ?? scratch.txt", tree),
        (
            "  why: rollback points live in git, not in the chat's rewind, which does not see edits made through the shell, a script or a subagent — work not committed did not happen",  # noqa: E501 — a golden line is typed whole
            tree,
        ),
        (
            "  fix: commit what is finished: git add -A && git commit -m '<what changed and why>' — stash or discard what is not; this is asked once per turn, and the rule is the skill commit-before-edit",  # noqa: E501 — a golden line is typed whole
            tree,
        ),
        ("RED: 1 finding — the working tree examined (1 path(s) dirty)", tree),
        (
            "GREEN: const-task-close: the working tree examined — 1 path(s) dirty; a stop hook already continued this turn once, so it is not asked again and the turn ends",  # noqa: E501 — a golden line is typed whole
            second,
        ),
        (
            "RED: core: the change touches 1 path(s) this pair describes (src/a.py) and none of its document(s): docs/core.md",  # noqa: E501 — a golden line is typed whole
            out,
        ),
        (
            "  why: task close is a single act: code and the current-state documents that describe it change together, or the change says why the documents stand",  # noqa: E501 — a golden line is typed whole
            out,
        ),
        (
            '  fix: update docs/core.md in this change, or declare no impact: add the trailer "No-Doc-Impact: core — <why the documents are unaffected>" to a commit of the range, in its last paragraph, where every line is Key: value — or the same line on its own in the pull request\'s description, given to the scan with --body <file>',  # noqa: E501 — a golden line is typed whole
            out,
        ),
        (
            f'RED: {where}: "No-Doc-Impact: nosuch — reason" names no pair of the coverage map (pairs: core)',
            out,
        ),
        ("  why: a declaration must name what it declares unaffected, or it declares nothing", out),
        ("  fix: name one of the pairs before the dash, or remove the line", out),
        (f'RED: {where}: "No-Doc-Impact: core" carries no reason', out),
        ("  why: a declaration is a judgment; the reason is what a reviewer reads", out),
        ("  fix: write it as No-Doc-Impact: core — <why the documents are unaffected>", out),
        ("RED: 3 finding(s) — 1 pair(s) examined over 1 commit(s), ", out),
        (
            "BROKEN: constitution.yaml: const-task-close.coverage[core] names the document docs/none.md, which does not exist at HEAD (",  # noqa: E501 — a golden line is typed whole
            x1,
        ),
        (
            " — fix: correct the path, or create the document; a pair whose document is gone describes nothing",  # noqa: E501 — a golden line is typed whole
            x1,
        ),
    ]
    missing = [text for text, haystack in literals if text not in haystack]
    return not missing, f"{len(literals)} literal lines found" if not missing else f"missing: {missing[0]!r}"


def hooks_file_shape() -> tuple[bool, str]:
    hooks = json.loads((SCRIPTS.parent / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    stop = hooks["hooks"]["Stop"]
    handler = stop[0]["hooks"][0]
    ok = (
        list(hooks["hooks"]) == ["Stop"]
        and "matcher" not in stop[0]
        and handler["type"] == "command"
        and handler["command"] == "sh"
        and handler["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/check-task-close.sh"]
        and isinstance(handler["timeout"], int)
    )
    return ok, "one Stop handler, exec form, the placeholder in args, a timeout" if ok else json.dumps(hooks)


def skills_and_install_note() -> tuple[bool, str]:
    root = SCRIPTS.parent
    sizes: dict[str, int] = {}
    for name in ("close-task", "commit-before-edit"):
        text = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---")[1])
        if front["name"] != name or not (0 < len(front["description"]) <= 1536):
            return False, f"{name}: name or description size"
        sizes[name] = len(front["description"])
    stated = re.search(
        r"skill listing, (\d+) and (\d+) characters", (root / "MODULE.md").read_text(encoding="utf-8")
    )
    if not stated or (int(stated.group(1)), int(stated.group(2))) != tuple(sizes.values()):
        return False, f"the module document states other sizes than {sizes}"
    install = (root / "INSTALL.md").read_text(encoding="utf-8")
    block = install.split("```yaml", 1)[1].split("```", 1)[0]
    example = yaml.safe_load(block)
    r = repo(example, files={"docs/design/api.md": "# api\n", "docs/design/build.md": "# build\n"})
    accepted = expect(scan(r.root), 0, "2 pair(s) examined", "stdout")
    return accepted[0], (
        f"{sizes}, as the module document states; the install note's example accepted as it stands"
        if accepted[0]
        else accepted[1]
    )


def broken_head() -> tuple[bool, str]:
    """A HEAD git cannot read is a configuration failure, never 'nothing landed'; an orphan branch
    in a repository with commits is unborn, and nothing landed on it."""
    r = repo(with_map())
    git(r.root, "checkout", "-q", "--orphan", "fresh")
    orphan = green_scan(scan(r.root), messages.f9_scan_tail(1, 0, "HEAD", "HEAD", True))
    git(r.root, "checkout", "-q", "main")
    (r.root / ".git" / "refs" / "heads" / "main").write_text("0" * 40 + "\n", encoding="utf-8")
    result = scan(r.root)
    ok = result.code == 1 and result.stderr.startswith("BROKEN: git could not read the range HEAD..HEAD in ")
    zeroed = (
        ok,
        "exit 1, the range failure with git's own line" if ok else f"{result.code}: {result.stderr}",
    )
    return all_of([orphan, zeroed], "an orphan branch is unborn; a zeroed ref is a configuration failure")


def unrelated_histories() -> tuple[bool, str]:
    """git merge-base exits 1 in silence for two histories with no common commit; the failure says so."""
    r = repo(with_map())
    git(r.root, "checkout", "-q", "--orphan", "other")
    commit(r.root, "another root", {"z.txt": "z\n"})
    other = short(r.root)
    checkout(r.root, "main")
    result = scan(r.root, "--since", "other")
    expected = messages.c12_range(other, short(r.root), str(r.root), "the two histories share no commit")
    return broken(result, expected)


def gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    """The consumer prepared and committed — a clean tree, which the hook passes — and, for the
    write the gate blocks, one untracked file left behind."""
    consumer = H.fresh_consumer()
    git(consumer.root, "branch", "-M", "main")
    consumer.write("constitution.yaml", raw_dials if raw_dials is not None else dials_text(dials_patch))
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    git(consumer.root, "add", "-A")
    git(consumer.root, "commit", "-q", "--allow-empty", "-m", "prepared")
    if isinstance(action, Write) and action.target == RED.target:
        consumer.write(RED.target, RED.text)
    return H.run_gate(stop_json(consumer.root), env=env), consumer.root


def claim(territory: Sequence[str]) -> dict[str, object]:
    return own()


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=RED,
    red_finding=messages.t1_dirty_tree(RED_LINES),
    green=messages.g1_clean(),
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=False,
    judges_envelopes=False,
    event="Stop",
)

ITEMS: list[tuple[int, str, Callable[[], tuple[bool, str]]]] = [
    (
        1,
        "red→green: a code-touching change without a document update is red; with the update, green",
        spec_update,
    ),
    (
        2,
        "red→green: the same change, green with a no-impact trailer on a later commit of the range",
        spec_trailer,
    ),
    (3, "red→green: the same change, green with the line in the body given as a file", spec_body),
    (4, "red→green: a dirty tree at turn end is red; a clean tree is silent", spec_tree),
    (5, "the second stop of a turn lets it end, saying so", second_stop),
    (6, "severity warn: the user's notice alone, carrying the finding and the count", warn_is_notice_alone),
    (7, "an ignored file is not dirty; a modified tracked file is", ignored_is_clean),
    (8, "a cwd below the root finds the repository", cwd_below_root),
    (9, "a tool event is a configuration failure: the gate is wired to Stop", tool_event_is_not_wired),
    (10, "the trunk dial names the base; an unknown trunk is a configuration failure", trunk_dial),
    (11, "--since names the base: a tag, a relative ref", since_ref),
    (12, "--change: a merge by its first-parent diff, a plain commit alone", change_merge_and_commit),
    (
        13,
        "on the trunk the bare scan examines the last landed change; on a merged branch, nothing",
        head_on_trunk,
    ),
    (
        14,
        "a root commit on the trunk, and a repository with no commit yet, examine nothing and say so",
        nothing_landed_before,
    ),
    (15, "--since and --change together are a misinvocation of the module's own", since_and_change),
    (16, "an unknown ref is a configuration failure, never a skip", unknown_ref),
    (17, "trailers read beside Co-Authored-By, a repeated key, one note each", trailer_among_others),
    (
        18,
        "a colon-less line hides the paragraph: red, and the fix teaches the rule",
        colonless_line_hides_paragraph,
    ),
    (19, "the body's line in any case with any dash; an unreadable body", body_forms),
    (20, "T3 for a declaration naming no pair, T4 for one without a reason, beside T2", t3_and_t4),
    (21, "a declaration for a pair the change does not touch earns its note", untouched_pair_note),
    (22, "declaration_key: the dial's key is read and the default is not", declaration_key_dial),
    (23, "overlapping pairs both apply, each satisfied its own way", overlapping_pairs),
    (24, "a document inside its own pair's code is not its own trigger", document_is_no_trigger),
    (25, "a deleted or renamed path counts as touched, on both sides", deleted_and_renamed_are_touched),
    (
        26,
        "X1 for a document that never was; not for a deleted one; an older change under today's map",
        missing_document,
    ),
    (27, "an empty map examines zero pairs and says so", empty_map),
    (28, "dial failures: each C5 text, exit 1", dial_failures),
    (29, "a pattern git would misread, in code and in working_files", unreadable_patterns),
    (30, "working_files: tracked matches are a note, untracked ones are not", working_files_note),
    (31, "a misspelt dial is a configuration failure", misspelt_dial),
    (32, "golden lines of T1–T4, X1 and the count forms, typed by hand", golden_lines),
    (33, "the hooks file's shape", hooks_file_shape),
    (
        34,
        "the skill descriptions' sizes; the install note's example accepted as it stands",
        skills_and_install_note,
    ),
    (35, "the hook validates the dials too", hook_validates_dials),
    (36, "an orphan branch is unborn; a HEAD git cannot read is a configuration failure", broken_head),
    (37, "two histories with no common commit: the range failure says so in words", unrelated_histories),
]

ASSERTIONS = [Assertion(number, title, check) for number, title, check in ITEMS]

if __name__ == "__main__":
    sys.exit(H.run_all([], [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
