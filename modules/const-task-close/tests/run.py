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
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.model import Finding  # noqa: E402
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
from shared_items import PatternDial, Subject, shared_assertions  # noqa: E402
from task_close_gate import messages, start  # noqa: E402
from task_close_gate.model import BODY, Declaration, Pair  # noqa: E402

identity.declare(start.GATE)  # the messages not typed by hand are built by the functions the gate uses
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
    parent: Path | None = None,
    ref_format: str | None = None,
) -> Consumer:
    """A consumer on branch main with the dials and the map's documents committed; with a parent, the
    repository lives in the folder WEIRD_DIR below it; with a ref_format, "files" or "reftable", the
    repository is created with that ref store named, whatever git defaults to."""
    named = {"GIT_DEFAULT_REF_FORMAT": ref_format} if ref_format else {}
    os.environ.update(named)  # the one `git init` of Consumer.build reads it; git before 2.45 ignores it
    try:
        consumer = H.fresh_consumer() if parent is None else Consumer(parent / WEIRD_DIR).build()
    finally:
        for key in named:
            del os.environ[key]
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


def broken(result: Result, line: str) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, line)
    counted = shared.c11_broken_count() in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def all_of(results: list[tuple[bool, str]], summary: str) -> tuple[bool, str]:
    failed = [evidence for ok, evidence in results if not ok]
    return not failed, failed[0] if failed else summary


# the module's own configuration failures, typed by hand: the dials' C5 lines, one pair's fix whole

DIAL = "BROKEN: constitution.yaml: const-task-close."
PAIR_FIX = (
    " — fix: write the pair as {name: <kebab>, code: [<gitignore patterns of the code it describes>],"
    " docs: [<paths of the documents that describe it>]}"
)
UNKNOWN_DIAL_FIX = (
    " is no dial of this module — fix: a misspelt dial would be ignored in silence, so none is: write"
    " one of severity, log_dir, coverage, trunk, declaration_key, working_files"
)
SHALLOW = "a shallow clone may need its history fetched (git fetch --unshallow)"
# a path or a folder name over 80 characters with a line break and a backslash: the echo rule's value
WEIRD_DIR = "w\nx\\y" + "d" * 80  # a folder name, for a root
WEIRD_DIR_SHOWN = "w\\nx\\\\y" + "d" * 80
WEIRD_DOC = "docs/w\nx\\y" + "m" * 80 + ".md"
WEIRD_DOC_SHOWN = "docs/w\\nx\\\\y" + "m" * 80 + ".md"
WEIRD_CODE = "src/w\nx\\y" + "c" * 80 + ".py"
WEIRD_CODE_SHOWN = "src/w\\nx\\\\y" + "c" * 80 + ".py"


def pair_line(position: int, detail: str) -> str:
    return f"{DIAL}coverage[{position}] {detail}{PAIR_FIX}"


# the scan's count tails, typed by hand: built by the message functions, a wrong word would pass


def tail(pairs: int, commits: int, base: str, tip: str) -> str:
    return f"{pairs} pair(s) examined over {commits} commit(s), {base}..{tip}"


def rooted(pairs: int, tip: str) -> str:
    return f"{pairs} pair(s) examined over 0 commit(s) — nothing landed before {tip}"


EMPTY = "0 pair(s) examined — coverage is empty"


def green_scan(result: Result, line: str) -> tuple[bool, str]:
    return expect(result, 0, "GREEN: const-task-close: " + line, "stdout")


def red_scan(result: Result, *findings: Finding) -> tuple[bool, str]:
    """Every expected finding whole, and nothing else red: no other finding, no other count."""
    missing = [f.key for f in findings if f.render() not in result.stdout]
    count = f"RED: {len(findings)} finding(s) — "
    expected = {"RED: " + f.headline for f in findings}
    reds = [line for line in result.stdout.splitlines() if line.startswith("RED: ")]
    stray = [line for line in reds if line not in expected and not line.startswith(count)]
    counted = sum(line.startswith(count) for line in reds) == 1
    ok = result.code == 2 and not missing and not stray and counted
    return ok, f"exit 2 teaching {[f.key.value for f in findings]}" if ok else (
        f"wanted exit 2 with {missing or 'the findings'}, nothing else red, and the line {count!r} once"
        f"; got exit {result.code}: {result.stdout}{result.stderr}"
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
    green = green_scan(scan(r.root), tail(1, 2, short(r.root, "main"), short(r.root)))
    # the same pair written with a leading './' and a doubled slash is the same document: the shared
    # normalisation reads it as 'docs/core.md', so the update counts (read as written, it never did)
    spelt = repo(with_map({**CORE, "docs": ["./docs//core.md"]}))
    branch(spelt.root)
    commit(spelt.root, "code only", {"src/a.py": "x = 2\n"})
    commit(spelt.root, "the page", {"docs/core.md": "# core, updated\n"})
    normalised = green_scan(scan(spelt.root), tail(1, 2, short(spelt.root, "main"), short(spelt.root)))
    # the paths a finding names are the reader's to open and to update: whole, never cut, one line
    odd = repo(with_map({**CORE, "docs": [WEIRD_DOC]}), files={WEIRD_DOC: "# core\n"})
    branch(odd.root)
    commit(odd.root, "code only", {WEIRD_CODE: "x = 2\n"})
    odd_lines = scan(odd.root).stdout.splitlines()
    odd_head = (
        "RED: core: the change touches 1 path(s) this pair describes ("
        + WEIRD_CODE_SHOWN
        + ") and none of its document(s): "
        + WEIRD_DOC_SHOWN
    )
    odd_fix = "  fix: update " + WEIRD_DOC_SHOWN + " in this change, or declare no impact: add the trailer"
    whole = (
        odd_head in odd_lines and any(line.startswith(odd_fix) for line in odd_lines),
        f"T2 names the changed path and the document whole: {odd_lines}",
    )
    return all_of(
        [red, green, normalised, whole], "red→green: T2, then the document updated, however it is spelt"
    )


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
    green = green_scan(result, tail(1, 2, short(r.root, "main"), short(r.root)))
    noted = (note in result.stdout, f"the note: {note}" if note in result.stdout else result.stdout)
    # the reason only points at the commit the note names: cut at 80 characters with the cut said, then
    # escaped, a backslash shown doubled; typed by hand, never built with the function under test
    odd = repo(with_map())
    branch(odd.root)
    commit(odd.root, "code only", {"src/a.py": "x = 2\n"})
    odd_where = "commit " + commit(odd.root, "declare\n\n" + trailer(reason="a\\b " + "r" * 100))
    odd_note = f"note: core: no impact declared in {odd_where}: a\\\\b " + "r" * 76 + "… [104 characters]"
    odd_result = scan(odd.root)
    odd_ok = (
        odd_note in odd_result.stdout.splitlines(),
        f"the note cuts the reason at 80 characters and escapes it: {odd_result.stdout}",
    )
    return all_of([red, green, noted, odd_ok], "red→green: T2, then a trailer on a later commit of the range")


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
    green = green_scan(result, tail(1, 1, short(r.root, "main"), short(r.root)))
    noted = (note in result.stdout, f"the note: {note}" if note in result.stdout else result.stdout)
    return all_of([red, green, noted], "red→green: T2, then the same line in the body given as a file")


def spec_tree() -> tuple[bool, str]:
    r = repo(own())
    r.write("scratch.txt", "x\n")
    red = expect(hook(r.root), 2, messages.t1_dirty_tree(RED_LINES).render(), "stderr")
    counted = expect(hook(r.root), 2, messages.f9_count_hook(1), "stderr")
    (r.root / "scratch.txt").unlink()
    green = expect(hook(r.root), 0, shared.g1_green_event(messages.g1_clean()), "stdout")
    # git quotes a path with a line break and doubles its backslash; the line is cut at 80 characters with
    # the cut said, and escaped again: it only points at what `git status` shows
    odd = repo(own())
    odd.write("w\nx\\y" + "z" * 90 + ".txt", "x\n")
    cut = expect(
        hook(odd.root),
        2,
        'RED: the working tree is dirty at turn end — 1 path(s): ?? "w\\\\nx\\\\\\\\y'
        + "z" * 69
        + "… [106 characters]\n",
        "stderr",
    )
    return all_of([red, counted, green, cut], "red→green: T1 on an untracked file, silent once it is gone")


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
    fix = (
        " — fix: wire the gate to Stop, as the plugin's hooks file does; to check a change by hand run it"
        " with --scan [<dir>] [--since <ref> | --change <commit>] [--body <file>]"
    )
    # a name holding a line break stays on one line, the break shown escaped, typed by hand
    odd = event.replace("PreToolUse", "Pre\\nTool")
    return all_of(
        [
            broken(
                H.run_gate(event),
                "BROKEN: hook input names the event 'PreToolUse', which this gate is not wired to" + fix,
            ),
            broken(
                H.run_gate(odd),
                "BROKEN: hook input names the event 'Pre\\nTool', which this gate is not wired to" + fix,
            ),
        ],
        "an event the gate is not wired to is a configuration failure, a line break in its name escaped",
    )


def hook_validates_dials() -> tuple[bool, str]:
    r = repo(own(coverag=[]))
    return broken(hook(r.root), DIAL + "coverag" + UNKNOWN_DIAL_FIX)


# ------------------------------------------------------------------ the scan's range


def trunk_dial() -> tuple[bool, str]:
    r = repo(with_map(trunk="trunk"))
    git(r.root, "branch", "-M", "trunk")
    branch(r.root)
    commit(r.root, "code only", {"src/a.py": "x = 2\n"})
    named = red_scan(scan(r.root), t2())
    r2 = repo(with_map(trunk="nowhere"))
    branch(r2.root)
    missing = broken(
        scan(r2.root),
        f"BROKEN: the trunk 'nowhere' is neither a local branch nor origin/nowhere in {r2.root} — fix:"
        " set const-task-close.trunk to the branch changes land on, or run the scan with --since <ref>",
    )
    r3 = repo(with_map(trunk="no\nwhere"))
    branch(r3.root)
    odd = broken(  # a line break in the dial's value stays on one line, shown escaped, typed by hand
        scan(r3.root),
        f"BROKEN: the trunk 'no\\nwhere' is neither a local branch nor origin/no\\nwhere in {r3.root} — fix:"
        " set const-task-close.trunk to the branch changes land on, or run the scan with --since <ref>",
    )
    parent = H.scratch_dir()  # a root of over 80 characters, a break and a backslash: whole
    r4 = repo(with_map(trunk="nowhere"), parent=parent)
    branch(r4.root)
    whole = broken(
        scan(r4.root),
        f"BROKEN: the trunk 'nowhere' is neither a local branch nor origin/nowhere in {parent}/"
        + WEIRD_DIR_SHOWN
        + " — fix: set const-task-close.trunk to the branch changes land on, or run the scan with --since"
        " <ref>",
    )
    return all_of(
        [named, missing, odd, whole, *fresher_trunk()],
        "the trunk dial names the base, the fresher of a local and a tracked trunk; an unknown trunk is a"
        " configuration failure",
    )


def clone_of(upstream: Path) -> Path:
    """A clone of the repository, its remote the default `origin`, in a fresh folder."""
    clone = H.scratch_dir() / "clone"
    done = git(upstream, "clone", "-q", str(upstream), str(clone))
    assert done.returncode == 0, done.stderr
    return clone


def landed_upstream() -> Path:
    """A clone whose local main is stale: the upstream repository has two more commits, fetched and not
    merged — `landed code` touches code alone, `landed readme` a README alone. The clone's main has
    `older code` at its tip, a code-only commit too, pushed before the clone was made."""
    up = repo(with_map())
    commit(up.root, "older code", {"src/a.py": "x = 2\n"})
    clone = clone_of(up.root)
    commit(up.root, "landed code", {"src/a.py": "x = 9\n"})
    commit(up.root, "landed readme", {"README": "hi\n"})
    done = git(clone, "fetch", "-q", "origin")
    assert done.returncode == 0, done.stderr
    return clone


def red_over(result: Result, line: str) -> tuple[bool, str]:
    """T2 for `src/a.py`, and the count line of the red whole."""
    ok, evidence = red_scan(result, t2())
    counted = f"RED: 1 finding(s) — {line}" in result.stdout.splitlines()
    return ok and counted, evidence if counted else f"wanted the count line {line!r}: {result.stdout}"


def fresher_trunk() -> list[tuple[bool, str]]:
    """Where the base is when the trunk is a local branch, the remote's tracking branch, or both: the
    one ahead when one is behind the other, the local one otherwise; and what is on the trunk."""
    real = shutil.which("git")
    if real is None:
        return [(False, "no git on PATH for the fake git to hand its other calls to")]
    results: list[tuple[bool, str]] = []

    def case(label: str, outcome: tuple[bool, str]) -> None:
        results.append((outcome[0], f"{label}: {outcome[1]}"))

    # 1: no local trunk, origin's only — the path of a CI checkout of a pull request
    c = clone_of(repo(with_map()).root)
    branch(c)
    git(c, "branch", "-D", "main")
    commit(c, "code only", {"src/a.py": "x = 2\n"})
    case("1 origin only", red_over(scan(c), tail(1, 1, short(c, "origin/main"), short(c))))
    # 2: a stale local main behind origin/main, a branch cut from origin/main: only its own commit
    c = landed_upstream()
    git(c, "checkout", "-q", "-b", "work/z", "origin/main")
    commit(c, "readme only", {"README": "hello\n"})
    case("2 stale local", green_scan(scan(c), tail(1, 1, short(c, "origin/main"), short(c))))
    # 3: local main ahead of origin/main by an unpushed trunk commit, the branch cut from it
    c = clone_of(repo(with_map()).root)
    commit(c, "unpushed trunk code", {"src/a.py": "x = 2\n"})
    branch(c)
    commit(c, "readme only", {"README": "hello\n"})
    case("3 local ahead", green_scan(scan(c), tail(1, 1, short(c, "main"), short(c))))
    # 4: split, each with a commit of its own: the local one, since it may hold what is not pushed yet
    c = landed_upstream()
    commit(c, "unpushed trunk code", {"src/b.py": "y = 1\n"})
    branch(c)
    commit(c, "readme only", {"README": "hello\n"})
    case("4 split", green_scan(scan(c), tail(1, 1, short(c, "main"), short(c))))
    # 5: detached at the stale local tip is on the trunk — the last landed change, never an empty range
    c = landed_upstream()
    git(c, "checkout", "-q", "--detach", "main")
    case(
        "5 detached at the stale local tip",
        red_over(scan(c), tail(1, 1, short(c, "main~1"), short(c, "main"))),
    )
    # 6: detached at the tracked tip is on the trunk too, whatever the local one says
    c = landed_upstream()
    git(c, "checkout", "-q", "--detach", "origin/main")
    case(
        "6 detached at the tracked tip",
        green_scan(scan(c), tail(1, 1, short(c, "origin/main~1"), short(c, "origin/main"))),
    )
    # 7: detached elsewhere: the base is the merge-base with the fresher trunk
    c = landed_upstream()
    git(c, "checkout", "-q", "-b", "work/z", "origin/main")
    commit(c, "readme only", {"README": "hello\n"})
    git(c, "checkout", "-q", "--detach")
    case(
        "7a detached, cut from the tracked tip",
        green_scan(scan(c), tail(1, 1, short(c, "origin/main"), short(c))),
    )
    c = landed_upstream()
    git(c, "checkout", "-q", "-b", "work/z", "main")
    commit(c, "readme only", {"README": "hello\n"})
    git(c, "checkout", "-q", "--detach")
    case("7b detached, cut from the stale tip", green_scan(scan(c), tail(1, 1, short(c, "main"), short(c))))
    # 8: on the branch named like the trunk: the last landed change, stale or not
    c = landed_upstream()
    case("8 on main", red_over(scan(c), tail(1, 1, short(c, "main~1"), short(c, "main"))))
    # 9: the two equal: either is the trunk
    c = clone_of(repo(with_map()).root)
    branch(c)
    commit(c, "code only", {"src/a.py": "x = 2\n"})
    case("9 equal", red_over(scan(c), tail(1, 1, short(c, "main"), short(c))))
    # 10: git cannot say whether the local trunk is an ancestor: the local one, as before, no failure
    c = landed_upstream()
    git(c, "checkout", "-q", "-b", "work/z", "origin/main")
    commit(c, "readme only", {"README": "hello\n"})
    unsaid = fake_git(real, "merge-base", when="--is-ancestor")
    case("10 ancestry unanswered", red_over(scan(c, env=unsaid), tail(1, 3, short(c, "main"), short(c))))
    return results


def since_ref() -> tuple[bool, str]:
    r = repo(with_map())
    git(r.root, "tag", "start")
    commit(r.root, "the page", {"docs/core.md": "# core 2\n"})
    commit(r.root, "code", {"src/a.py": "x = 2\n"})
    since_tag = green_scan(
        scan(r.root, "--since", "start"),
        tail(1, 2, short(r.root, "start"), short(r.root)),
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
    whole = green_scan(result, tail(1, 3, short(r.root, "main^1"), merged))
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
        scan(r.root), tail(1, 0, short(r.root), short(r.root))
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
    root_commit = green_scan(scan(r.root), rooted(1, short(r.root)))
    empty = H.scratch_dir()
    git(empty, "init", "-q")
    (empty / "constitution.yaml").write_text(dials_text(with_map()), encoding="utf-8")
    none = green_scan(scan(empty), rooted(1, "HEAD"))
    return all_of([root_commit, none], "a root commit on the trunk, and a repository with no commit yet")


def since_and_change() -> tuple[bool, str]:
    r = repo(with_map())
    return broken(
        scan(r.root, "--since", "main", "--change", "HEAD"),
        "BROKEN: --since and --change exclude each other — fix: give one: --since <ref> examines the"
        " changes since that base, --change <commit> examines one landed change",
    )


def unknown_ref() -> tuple[bool, str]:
    r = repo(with_map())
    unknown = (
        f"'nope', which git cannot resolve in {r.root}: no such ref — fix: name a commit, branch or tag"
        f" this repository has; {SHALLOW}"
    )
    since = broken(scan(r.root, "--since", "nope"), f"BROKEN: --since names {unknown}")
    change = broken(scan(r.root, "--change", "nope"), f"BROKEN: --change names {unknown}")
    # the ref only points: cut at 80, the cut said, then escaped; the root is a path: whole
    parent = H.scratch_dir()
    odd_root = repo(with_map(), parent=parent).root
    odd_unknown = (
        "'n\\nx\\\\y" + "r" * 75 + f"… [95 characters]', which git cannot resolve in {parent}/"
        f"{WEIRD_DIR_SHOWN}: no such ref — fix: name a commit, branch or tag this repository has; {SHALLOW}"
    )
    odd = broken(scan(odd_root, "--since", "n\nx\\y" + "r" * 90), f"BROKEN: --since names {odd_unknown}")
    # git's own line is the diagnosis the reader acts on: whole, escaped, over 80 characters
    real = shutil.which("git")
    if real is None:
        return False, "no git on PATH for the fake git to hand its other calls to"
    said = "fatal: a\\b " + "w" * 90
    diagnosed = broken(
        scan(r.root, "--since", "nope", env=fake_git(real, "rev-parse", said, "nope")),
        f"BROKEN: --since names 'nope', which git cannot resolve in {r.root}: fatal: a\\\\b "
        + "w" * 90
        + f" — fix: name a commit, branch or tag this repository has; {SHALLOW}",
    )
    return all_of(
        [since, change, odd, diagnosed, dash_refs(r.root, real), refs_that_resolve()],
        "an unknown ref is a configuration failure for both flags; a ref that begins with a dash is one"
        " before git is asked, and the refs git resolves still resolve",
    )


def logging_git(
    real: str, old: bool = False, version_fails: str | None = None, version_says: str | None = None
) -> tuple[dict[str, str], Path]:
    """A git first on PATH that logs each call's arguments, as it hands them on, to the returned file
    and execs the real one by its path. As an old git, it gives every `%(trailers:` the scan asks an
    option no git knows, as a git of before the options does not know its own; with `version_fails`,
    `git version` fails with that line, and with `version_says` it prints that line and succeeds."""
    folder = H.scratch_dir()
    log = folder / "git.log"
    script = folder / "git"
    rewrite = (
        "    *'%(trailers:'*) a=$(printf '%s' \"$a\" | sed 's/%(trailers:/%(trailers:nosuchopt,/');;\n"
        if old
        else ""
    )
    failing = (
        f"if [ \"$1\" = version ]; then printf '%s\\n' {shlex.quote(version_fails)} >&2; exit 128; fi\n"
        if version_fails is not None
        else ""
    )
    if version_says is not None:
        failing += f"if [ \"$1\" = version ]; then printf '%s\\n' {shlex.quote(version_says)}; exit 0; fi\n"
    script.write_text(
        "#!/bin/sh\n"
        f"{failing}"
        'for a in "$@"; do\n'
        "  shift\n"
        '  case "$a" in\n'
        f"{rewrite}"
        "  esac\n"
        '  set -- "$@" "$a"\n'
        "done\n"
        f"printf '%s\\n' \"$*\" >> {shlex.quote(str(log))}\n"
        f'exec {shlex.quote(real)} "$@"\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    log.write_text("", encoding="utf-8")
    return {"PATH": f"{script.parent}{os.pathsep}{os.environ['PATH']}"}, log


def dash_refs(root: Path, real: str) -> tuple[bool, str]:
    """A ref that begins with a dash is refused with its reason before git is asked, in both flags and
    in each form that reaches the gate (`--since=-x`; `--since -1`, which the parser reads as a value);
    a fake git logs every call, and a control run proves the log holds the ref git is asked about."""
    env, log = logging_git(real)
    scan(root, "--since", "nope", env=env)
    if "nope^{commit}" not in log.read_text(encoding="utf-8"):
        return False, f"the fake git's log does not hold the call that resolves a ref: {log.read_text()!r}"
    for flag, ref, args in (
        ("--since", "--all", ["--since=--all"]),
        ("--since", "-x", ["--since=-x"]),
        ("--change", "-1", ["--change=-1"]),
        ("--since", "-1", ["--since", "-1"]),
        ("--change", "-", ["--change", "-"]),
    ):
        log.write_text("", encoding="utf-8")
        verdict = broken(
            scan(root, *args, env=env),
            f"BROKEN: {flag} names '{ref}', which git cannot resolve in {root}: a ref cannot begin with a"
            f" dash — fix: name a commit, branch or tag this repository has; {SHALLOW}",
        )
        if not verdict[0]:
            return verdict
        asked = log.read_text(encoding="utf-8")
        if f"{ref}^{{commit}}" in asked:
            return False, f"git was asked to resolve {ref!r}: {asked!r}"
    return True, "a ref that begins with a dash is refused with its reason, git never asked"


def refs_that_resolve() -> tuple[bool, str]:
    """The refs git resolves are resolved as ever: a branch, a tag, a relative ref, the reflog's
    previous branch, a full hash, and --change HEAD; each examines the one code-only commit."""
    r = repo(with_map())
    git(r.root, "tag", "start")
    base = git(r.root, "rev-parse", "HEAD").stdout.strip()
    branch(r.root)
    commit(r.root, "code only", {"src/a.py": "x = 2\n"})
    checkout(r.root, "main")
    checkout(r.root, "work/x")  # @{-1} is now main
    for args in (
        ("--since", "main"),
        ("--since", "start"),
        ("--since", "HEAD~1"),
        ("--since", "HEAD^"),
        ("--since", "@{-1}"),
        ("--since", base),
        ("--change", "HEAD"),
    ):
        verdict = red_scan(scan(r.root, *args), t2())
        if not verdict[0]:
            return False, f"{' '.join(args)}: {verdict[1]}"
    return True, "a branch, a tag, HEAD~1, HEAD^, @{-1}, a full hash and --change HEAD resolve"


# ------------------------------------------------------------------ declarations


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
        assert git(root, "config", key, value).returncode == 0
    return log


def signed_gate(root: Path, result: Result, log: Path) -> str:
    """What is wrong with a scan of a signed range, or "": the repository's own git log verifies the
    signature through the fake and prints its text, so the case cannot pass for want of a signature
    check, and no text of the check reached the scan's output."""
    shown = git(root, "log", "-1", "--format=%h")
    calls = log.read_text(encoding="utf-8") if log.exists() else ""
    if "--verify" not in calls:
        return f"git never called the fake to verify: {calls!r}"
    if "fake signer" not in shown.stdout + shown.stderr:
        return f"git log did not print the check: {shown.stdout}{shown.stderr}"
    if "fake signer" in result.stdout + result.stderr:
        return f"the signature check reached the output: {result.stdout}{result.stderr}"
    return ""


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
    if not ok:
        return False, result.stdout + result.stderr
    return all_of(
        [signed_note(), old_git_is_a_failure_of_git()],
        "both trailers read beside Co-Authored-By, one note each; a signed commit's note on one line;"
        " a git that does not know the trailer options is a configuration failure naming it",
    )


def signed_note() -> tuple[bool, str]:
    """A signed commit under log.showSignature=true: the note's label is `commit <short>` on one line,
    as for an unsigned commit, and the scan prints that note and the count line, nothing more."""
    r = repo(with_map())
    branch(r.root)
    log = fake_gpg(r.root)
    where = "commit " + commit(r.root, "renamed\n\n" + trailer("core", "a rename only"), {"src/a.py": "2\n"})
    result = scan(r.root)
    note = messages.n1_declared(declared(where, "core", "a rename only"), True)
    count = "GREEN: const-task-close: " + tail(1, 1, short(r.root, "main"), short(r.root))
    wrong = signed_gate(r.root, result, log)
    ok = result.code == 0 and not wrong and result.stdout.splitlines() == [*note.splitlines(), count]
    if ok:
        return (
            True,
            "both trailers read beside Co-Authored-By, one note each; a signed commit's note on one line",
        )
    return (
        False,
        wrong or f"exit {result.code}, wanted {note!r} then {count!r}: {result.stdout}{result.stderr}",
    )


def old_git_is_a_failure_of_git() -> tuple[bool, str]:
    """A git that prints the trailer placeholder as text, as one that does not know the options does,
    makes the scan a configuration failure naming git's version line — never a red for a declaration
    nobody wrote; when `git version` itself fails, the failure says so in the version's place; its
    line, said or failed, is cut at 80 characters and its backslashes escaped like any echoed value. A
    declaration that merely quotes the placeholder is read as ever."""
    real = shutil.which("git")
    if real is None:
        return False, "no git on PATH for the fake git to hand its calls to"
    r = repo(with_map())
    branch(r.root)
    commit(r.root, "renamed\n\n" + trailer("core", "a rename only"), {"src/a.py": "2\n"})
    env, log = logging_git(real, old=True)
    result = scan(r.root, env=env)
    version = subprocess.run([real, "version"], capture_output=True, text=True, check=False)
    fix = "install a newer git (https://git-scm.com/downloads)"
    options = "git does not know the trailer options this check reads (key, valueonly, unfold, separator)"
    old = broken(result, f"BROKEN: {options}: {version.stdout.splitlines()[0]} — fix: {fix}")
    if not old[0]:
        return old
    if "nosuchopt" not in log.read_text(encoding="utf-8"):
        return False, f"the fake git never gave the placeholder its unknown option: {log.read_text()!r}"
    if "names no pair" in result.stdout + result.stderr or "RED" in result.stdout + result.stderr:
        return False, f"a red beside the failure: {result.stdout}{result.stderr}"
    env, _ = logging_git(real, old=True, version_fails="fatal: planted version failure")
    silent = broken(
        scan(r.root, env=env),
        f"BROKEN: {options}: git version failed: fatal: planted version failure — fix: {fix}",
    )
    if not silent[0]:
        return silent
    # a version line of over 80 characters holding backslashes reaches the failure cut and escaped,
    # said or failed alike: the cut at 80 characters with the count, each backslash doubled
    said = r"git version 1.8.3.1 built at C:\tools\git on a host with a rather long name,"
    said += " 2014-01-01 (the 1.8 line)"
    env, _ = logging_git(real, old=True, version_says=said)
    echoed_said = broken(
        scan(r.root, env=env),
        rf"BROKEN: {options}: git version 1.8.3.1 built at C:\\tools\\git on a host with a rather long name,"
        f" 201… [102 characters] — fix: {fix}",
    )
    if not echoed_said[0]:
        return echoed_said
    lost = r"fatal: cannot exec C:\tools\git\git.exe on a host with a rather long name,"
    lost += " so the version is unknown"
    env, _ = logging_git(real, old=True, version_fails=lost)
    echoed_lost = broken(
        scan(r.root, env=env),
        rf"BROKEN: {options}: git version failed: fatal: cannot exec C:\\tools\\git\\git.exe on a host"
        f" with a rat… [120 characters] — fix: {fix}",
    )
    if not echoed_lost[0]:
        return echoed_lost
    q = repo(with_map())
    branch(q.root)
    reason = "the %(trailers placeholder, quoted"
    where = "commit " + commit(q.root, "quoted\n\n" + trailer("core", reason), {"src/a.py": "2\n"})
    quoted = scan(q.root)
    note = messages.n1_declared(declared(where, "core", reason), True)
    count = "GREEN: const-task-close: " + tail(1, 1, short(q.root, "main"), short(q.root))
    if quoted.code != 0 or quoted.stdout.splitlines() != [*note.splitlines(), count]:
        return (
            False,
            f"a declaration quoting the placeholder: exit {quoted.code}: {quoted.stdout}{quoted.stderr}",
        )
    return True, "the placeholder as text is a failure naming git, its line echoed; quoted it is read"


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
        tail(1, 1, short(r.root, "main"), short(r.root)),
    )
    gone = H.scratch_dir() / "gone.txt"
    unreadable = broken(
        scan(r.root, "--body", str(gone)),
        f"BROKEN: --body names {gone}, which cannot be read ([Errno 2] No such file or directory: '{gone}')"
        " — fix: give the pull request's description as a readable file",
    )
    odd_dir = H.scratch_dir()  # a path of over 80 characters with a break and a backslash: whole
    odd_name = "w\nx\\y" + "b" * 80 + ".txt"
    odd = broken(
        scan(r.root, "--body", str(odd_dir / odd_name)),
        f"BROKEN: --body names {odd_dir}/w\\nx\\\\y"
        + "b" * 80
        + ".txt, which cannot be read ([Errno 2] No such"
        f" file or directory: '{odd_dir}/w\\nx\\\\y" + "b" * 80 + ".txt') — fix: give the pull request's"
        " description as a readable file",
    )
    return all_of([read, unreadable, odd], "the body's line, any case, any dash; an unreadable body")


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
    unsigned = red_scan(result, no_pair, no_reason, t2())
    if not unsigned[0]:
        return unsigned
    return signed_red()


def signed_red() -> tuple[bool, str]:
    """The same declarations in a signed commit under log.showSignature=true: the red names
    `commit <short>` on one line."""
    r = repo(with_map())
    branch(r.root)
    log = fake_gpg(r.root)
    where = "commit " + commit(
        r.root, "wrong\n\n" + f"{KEY}: nosuch — reason\n{KEY}: core\n", {"src/a.py": "2\n"}
    )
    result = scan(r.root)
    no_pair = messages.t3_names_no_pair(
        Declaration(where, "nosuch — reason", "nosuch", "reason"), KEY, ["core"]
    )
    no_reason = messages.t4_no_reason(Declaration(where, "core", "core", ""), KEY)
    wrong = signed_gate(r.root, result, log)
    ok, evidence = red_scan(result, no_pair, no_reason, t2())
    return ok and not wrong, evidence if ok and not wrong else wrong or evidence


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
    green = expect(scan(r.root), 0, "GREEN: const-task-close: 2 pair(s) examined over ", "stdout")
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
    doc_moved = expect(scan(r3.root), 0, "GREEN: const-task-close: 1 pair(s) examined over ", "stdout")
    return all_of([deleted, renamed, doc_moved], "a deleted or renamed path counts as touched, on both sides")


def missing_document() -> tuple[bool, str]:
    r = repo(with_map({"name": "core", "code": ["src/**"], "docs": ["docs/none.md"]}))
    missing = broken(
        scan(r.root), messages.x1_document_missing("core", "docs/none.md", short(r.root)).render()
    )
    tree = repo(with_map({"name": "core", "code": ["src/**"], "docs": ["docs"]}))  # docs/ holds core.md
    directory = broken(
        scan(tree.root), messages.x2_document_is_directory("core", "docs", short(tree.root)).render()
    )
    gone = repo(with_map({**CORE, "docs": [WEIRD_DOC]}))  # a document path over 80 characters: whole
    dir_doc = repo(with_map({**CORE, "docs": [WEIRD_DOC]}), files={WEIRD_DOC + "/a.md": "x\n"})
    odd = all_of(
        [
            broken(
                scan(gone.root),
                "BROKEN: constitution.yaml: const-task-close.coverage[core] names the document "
                + WEIRD_DOC_SHOWN
                + f", which does not exist at HEAD ({short(gone.root)}) — fix: correct the path, or create"
                " the document; a pair whose document is gone describes nothing",
            ),
            broken(
                scan(dir_doc.root),
                "BROKEN: constitution.yaml: const-task-close.coverage[core] names "
                + WEIRD_DOC_SHOWN
                + f", which is a directory at HEAD ({short(dir_doc.root)}) — fix: name the document file; a"
                " change names files, so a directory can never count as updated",
            ),
        ],
        "X1 and X2 name the path whole",
    )
    r2 = repo(with_map())
    branch(r2.root)
    commit(r2.root, "drop the page", remove=["docs/core.md"])
    deleted = expect(scan(r2.root), 0, "GREEN: const-task-close: 1 pair(s) examined over ", "stdout")
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
        [missing, directory, odd, deleted, older],
        "X1 for a document that never was; X2 for a directory at HEAD; not for one the range deleted;"
        " an older change judged by today's map is a finding, never X1",
    )


def empty_map() -> tuple[bool, str]:
    r = repo(own())
    branch(r.root)
    commit(r.root, "code", {"src/a.py": "2\n"})
    return green_scan(scan(r.root), EMPTY)


# ------------------------------------------------------------------ dials


TRUNK = (
    DIAL + "trunk must be a non-empty string — fix: set trunk: <the branch changes land on>, or remove the"
    " line for main"
)


def dial_failures() -> tuple[bool, str]:
    cases: list[tuple[dict[str, object], str]] = [
        (
            own(coverage="x"),
            DIAL + "coverage must be a list of pairs — fix: write it as coverage: [{name: <kebab>, code:"
            " [<patterns>], docs: [<paths>]}]",
        ),
        (own(coverage=["x"]), pair_line(1, "is not a mapping")),
        (
            own(coverage=[{**CORE, "extra": 1}]),
            pair_line(1, "carries the key 'extra', which no pair has (name, code, docs)"),
        ),
        (  # a line break in the key is shown escaped: the line stays one line
            own(coverage=[{**CORE, "a\nb": 1}]),
            pair_line(1, "carries the key 'a\\nb', which no pair has (name, code, docs)"),
        ),
        (
            own(coverage=[{"code": ["src/**"], "docs": ["docs/core.md"]}]),
            pair_line(1, "has no name, or one that is not kebab-case"),
        ),
        (
            own(coverage=[{**CORE, "name": "Core Bad"}]),
            pair_line(1, "has no name, or one that is not kebab-case"),
        ),
        (own(coverage=[CORE, CORE]), pair_line(2, "repeats the name 'core'")),
        (
            own(coverage=[{"name": "core", "docs": ["docs/core.md"]}]),
            pair_line(1, "has no code, or code is not a non-empty list of patterns"),
        ),
        (
            own(coverage=[{"name": "core", "code": [], "docs": ["docs/core.md"]}]),
            pair_line(1, "has no code, or code is not a non-empty list of patterns"),
        ),
        (
            own(coverage=[{"name": "core", "code": ["src/**"]}]),
            pair_line(1, "has no docs, or docs is not a non-empty list of repository-relative paths"),
        ),
        (
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": ["/abs.md"]}]),
            pair_line(1, "has no docs, or docs is not a non-empty list of repository-relative paths"),
        ),
        (
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": ["../x.md"]}]),
            pair_line(1, "has no docs, or docs is not a non-empty list of repository-relative paths"),
        ),
        (
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": ["docs/../../x.md"]}]),
            pair_line(1, "has no docs, or docs is not a non-empty list of repository-relative paths"),
        ),
        (
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": ["docs/"]}]),
            pair_line(1, "names 'docs/', a directory — a pair's documents are files"),
        ),
        (  # a line break in the path stays on one line, shown escaped
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": ["a\nb/"]}]),
            pair_line(1, "names 'a\\nb/', a directory — a pair's documents are files"),
        ),
        (  # a path of over 80 characters stays whole: the reader corrects it
            own(coverage=[{"name": "core", "code": ["src/**"], "docs": [WEIRD_DOC[:-3] + "/"]}]),
            pair_line(1, "names '" + WEIRD_DOC_SHOWN[:-3] + "/', a directory — a pair's documents are files"),
        ),
        (own(trunk=""), TRUNK),
        (own(trunk=3), TRUNK),
        (
            own(declaration_key="No Doc"),
            DIAL + "declaration_key must be a trailer key: letters, digits and hyphens — fix: set"
            " declaration_key: No-Doc-Impact, or remove the line",
        ),
        (
            own(working_files="x"),
            DIAL + "working_files must be a list of patterns — fix: write it as working_files:"
            " [<gitignore patterns>], or remove the line",
        ),
    ]
    results = [broken(scan(repo(patch).root), failure) for patch, failure in cases]
    # a backslash is a separator only where the platform says so: there `..\x.md` leaves the repository,
    # elsewhere it is one file name and stays inside (it was refused everywhere before)
    escaping = scan(repo(own(coverage=[{**CORE, "docs": ["..\\x.md"]}])).root)
    if os.sep == "\\":
        results.append(
            broken(
                escaping,
                pair_line(1, "has no docs, or docs is not a non-empty list of repository-relative paths"),
            )
        )
    else:
        first = escaping.stderr.splitlines()[0] if escaping.stderr else ""
        named = (  # past the dials, the one thing wrong is that no such document is at HEAD
            "BROKEN: constitution.yaml: const-task-close.coverage[core] names the document ..\\\\x.md, which"
            " does not exist at HEAD ("
        )
        results.append((escaping.code == 1 and first.startswith(named), first[:200]))
    return all_of(results, f"{len(cases)} dial failures, each exit 1 with its own line")


def unreadable_patterns() -> tuple[bool, str]:
    fix = (
        " — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break"
    )
    code = broken(
        scan(repo(with_map({**CORE, "code": ["#src/**"]})).root),
        DIAL + "coverage[core].code holds a pattern git would not read as one: '#src/**'" + fix,
    )
    working = broken(
        scan(repo(own(working_files=["#x"])).root),
        DIAL + "working_files holds a pattern git would not read as one: '#x'" + fix,
    )
    return all_of([code, working], "a pattern git would misread, in a pair's code and in working_files")


def working_files_note() -> tuple[bool, str]:
    r = repo(own(working_files=["notes/**"]), files={"notes/todo.md": "x\n"})
    r.write("notes/untracked.md", "y\n")
    result = scan(r.root)
    note = messages.n2_working_files(["notes/todo.md"])
    odd = "notes/w\nx\\y" + "p" * 80 + ".md"  # a path over 80 characters: whole, escaped
    odd_run = scan(repo(own(working_files=["notes/**"]), files={odd: "x\n"}).root)
    odd_note = (
        "note: 1 tracked file(s) match working_files (notes/w\\nx\\\\y" + "p" * 80 + ".md) — a task's"
        " working files are deleted at its close; keep one only with a reason"
    )
    return all_of([expect(result, 0, note, "stdout"), expect(odd_run, 0, odd_note, "stdout")], "the note")


def misspelt_dial() -> tuple[bool, str]:
    return broken(scan(repo(own(covrage=[])).root), DIAL + "covrage" + UNKNOWN_DIAL_FIX)


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
    spelt = repo(with_map())
    branch(spelt.root)
    odd_where = "commit " + commit(  # a line break inside a declaration's value stays on one line
        spelt.root, "wrong\n\n" + f"{KEY}: nosuch — a\rb\n", {"src/a.py": "2\n"}
    )
    odd = scan(spelt.root).stdout
    cut = repo(with_map())
    branch(cut.root)
    cut_where = "commit " + commit(  # a value of 95 characters with a backslash points only: cut at 80
        cut.root, "wrong\n\n" + f"{KEY}: nosuch — q\\" + "z" * 84 + "\n", {"src/a.py": "2\n"}
    )
    cut_out = scan(cut.root).stdout
    x1 = scan(repo(with_map({**CORE, "docs": ["docs/none.md"]})).root).stderr
    x2 = scan(repo(with_map({**CORE, "docs": ["docs"]})).root).stderr
    slash = scan(repo(with_map({**CORE, "docs": ["docs/"]})).root).stderr
    many = repo(own())
    for n in range(1, 7):
        many.write(f"s{n}.txt", "x\n")
    six = hook(many.root).stderr  # one more path than T1 lists
    wide = repo(with_map())
    branch(wide.root)
    commit(wide.root, "four", {"src/a.py": "2\n", "src/b.py": "b\n", "src/c.py": "c\n", "src/d.py": "d\n"})
    four = scan(wide.root).stdout  # one more path than T2 lists
    literals = [
        (
            f'RED: {odd_where}: "No-Doc-Impact: nosuch — a\\rb" names no pair of the coverage map'
            " (pairs: core)",
            odd,
        ),
        (
            f'RED: {cut_where}: "No-Doc-Impact: nosuch — q\\\\'
            + "z" * 69
            + '… [95 characters]" names no pair'
            " of the coverage map (pairs: core)",
            cut_out,
        ),
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
        (
            "BROKEN: constitution.yaml: const-task-close.coverage[core] names docs, which is a directory at HEAD (",  # noqa: E501 — a golden line is typed whole
            x2,
        ),
        (
            " — fix: name the document file; a change names files, so a directory can never count as updated",  # noqa: E501 — a golden line is typed whole
            x2,
        ),
        (
            "BROKEN: constitution.yaml: const-task-close.coverage[1] names 'docs/', a directory — a pair's documents are files — fix: write the pair as ",  # noqa: E501 — a golden line is typed whole
            slash,
        ),
        (
            "RED: the working tree is dirty at turn end — 6 path(s): ?? s1.txt, ?? s2.txt, ?? s3.txt, ?? s4.txt, ?? s5.txt, …",  # noqa: E501 — a golden line is typed whole
            six,
        ),
        (
            "RED: core: the change touches 4 path(s) this pair describes (src/a.py, src/b.py, src/c.py, …) and none of its document(s): docs/core.md",  # noqa: E501 — a golden line is typed whole
            four,
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
        if "Use when " not in front["description"] or "Advisory:" not in front["description"]:
            return False, f"{name}: the description carries no 'Use when ' trigger or no 'Advisory:' line"
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
    accepted = expect(scan(r.root), 0, "GREEN: const-task-close: 2 pair(s) examined over ", "stdout")
    return accepted[0], (
        f"{sizes}, as the module document states; the install note's example accepted as it stands"
        if accepted[0]
        else accepted[1]
    )


def wrong_store(root: Path, wanted: str) -> tuple[bool, str] | None:
    """None when the repository is in the wanted ref store; else the red of the half that needed it —
    a git before 2.45 knows neither the option nor the variable, and the half is red, never a crash."""
    found = git(root, "rev-parse", "--show-ref-format")
    store = found.stdout.strip() if found.returncode == 0 else f"unreadable ({found.stderr.strip()})"
    if store == wanted:
        return None
    return (
        False,
        f"this half needs the {wanted} ref store, found: {store} — git 2.45 or newer is needed for this half",
    )


def zeroed_ref_half(failure: str) -> tuple[bool, str]:
    """A ref file of forty zeros, written by hand, in a repository of the files store."""
    zero = repo(with_map(), ref_format="files")
    if (red := wrong_store(zero.root, "files")) is not None:
        return red
    (zero.root / ".git" / "refs" / "heads" / "main").write_text("0" * 40 + "\n", encoding="utf-8")
    result = scan(zero.root)
    ok = result.code == 1 and result.stderr.startswith(failure)
    return (
        ok,
        "exit 1, the range failure" if ok else f"files store, zeroed ref: {result.code}: {result.stderr}",
    )


def missing_object_half(failure: str) -> tuple[bool, str]:
    """A ref to a commit whose object is gone, made through git alone, in a repository of the
    reftable store."""
    gone = repo(with_map(), ref_format="reftable")
    if (red := wrong_store(gone.root, "reftable")) is not None:
        return red
    tree = git(gone.root, "write-tree")
    dangling = git(gone.root, "commit-tree", "-m", "gone", tree.stdout.strip())
    sha = dangling.stdout.strip()
    update = git(gone.root, "update-ref", "refs/heads/main", sha)
    if tree.returncode or dangling.returncode or update.returncode:
        return (
            False,
            "reftable store, the missing object could not be made: "
            f"{tree.stderr}{dangling.stderr}{update.stderr}",
        )
    loose = gone.root / ".git" / "objects" / sha[:2] / sha[2:]
    if not loose.exists():
        return False, f"reftable store, the commit {sha} is not a loose object to delete"
    loose.unlink()
    result = scan(gone.root)
    ok = result.code == 1 and result.stderr.startswith(failure)
    return (
        ok,
        "exit 1, the range failure"
        if ok
        else f"reftable store, missing object: {result.code}: {result.stderr}",
    )


def broken_head() -> tuple[bool, str]:
    """A HEAD git cannot read is a configuration failure, never 'nothing landed'; an orphan branch
    in a repository with commits is unborn, and nothing landed on it. Two broken HEADs, each in a
    repository whose ref store the item chose: a zeroed ref file, written by hand, in the files store; a
    ref to a commit whose object is gone, made through git alone, in the reftable store."""
    r = repo(with_map())
    git(r.root, "checkout", "-q", "--orphan", "fresh")
    orphan = green_scan(scan(r.root), rooted(1, "HEAD"))
    failure = "BROKEN: git could not read the range HEAD..HEAD in "

    zeroed = zeroed_ref_half(failure)
    missing = missing_object_half(failure)
    return all_of(
        [orphan, zeroed, missing],
        "an orphan branch is unborn; a zeroed ref file in the files store and a ref to a missing object"
        " in the reftable store are each a configuration failure, exit 1 with git's own line",
    )


def directory_named_as_document() -> tuple[bool, str]:
    """A pair naming a directory could never be updated — a change names files — so it is refused
    before any range is judged: a trailing slash at the read, a tree at HEAD by the scan. The file
    named, the same change is examined."""
    r = repo(with_map({**CORE, "docs": ["docs/"]}))
    branch(r.root)
    commit(r.root, "code", {"src/a.py": "2\n"})
    slash = broken(scan(r.root), pair_line(1, "names 'docs/', a directory — a pair's documents are files"))
    commit(r.root, "the tree", {"constitution.yaml": dials_text(with_map({**CORE, "docs": ["docs"]}))})
    tree = broken(scan(r.root), messages.x2_document_is_directory("core", "docs", short(r.root)).render())
    commit(r.root, "the file", {"constitution.yaml": dials_text(with_map()), "docs/core.md": "# 2\n"})
    green = green_scan(scan(r.root), tail(1, 3, short(r.root, "main"), short(r.root)))
    return all_of(
        [slash, tree, green], "red→green: C5 for docs/, X2 for the tree, green once the file is named"
    )


def unrelated_histories() -> tuple[bool, str]:
    """git merge-base exits 1 in silence for two histories with no common commit; the failure says so."""
    r = repo(with_map())
    git(r.root, "checkout", "-q", "--orphan", "other")
    commit(r.root, "another root", {"z.txt": "z\n"})
    other = short(r.root)
    checkout(r.root, "main")
    result = scan(r.root, "--since", "other")
    return broken(
        result,
        f"BROKEN: git could not read the range {other}..{short(r.root)} in {r.root}: the two histories"
        f" share no commit — fix: repair what git names in the message; {SHALLOW}",
    )


def fake_git(real: str, failing: str, said: str | None = None, when: str = "") -> dict[str, str]:
    """A git first on PATH that fails one subcommand as git does, with the line it says, and hands every
    other to the real one; with `when`, only a call whose arguments hold that text."""
    line = f"fatal: planted {failing} failure" if said is None else said
    script = H.scratch_dir() / "git"
    script.write_text(
        f'#!/bin/sh\nif [ "$1" = "{failing}" ]; then\n  case "$*" in *{when}*)\n'
        f"  printf '%s\\n' {shlex.quote(line)} >&2; exit 128;;\n  esac\nfi\n"
        f'exec {shlex.quote(real)} "$@"\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    return {"PATH": f"{script.parent}{os.pathsep}{os.environ['PATH']}"}


def unreadable_tree() -> tuple[bool, str]:
    """git failing on the working tree is a configuration failure in both modes, never a clean tree:
    the hook's git status, the scan's git ls-files."""
    real = shutil.which("git")
    if real is None:
        return False, "no git on PATH for the fake git to hand its other calls to"
    r = repo(own())
    r.write("scratch.txt", "x\n")
    hooked = broken(
        hook(r.root, env=fake_git(real, "status")),
        f"BROKEN: git could not read the working tree in {r.root}: fatal: planted status failure — fix:"
        " repair what git names in the message, then check by hand: git -C <that directory> status",
    )
    r2 = repo(with_map())
    branch(r2.root)
    commit(r2.root, "code", {"src/a.py": "2\n"})
    scanned = broken(
        scan(r2.root, env=fake_git(real, "ls-files")),
        f"BROKEN: git could not read the working tree in {r2.root}: fatal: planted ls-files failure — fix:"
        " repair what git names in the message, then check by hand: git -C <that directory> status",
    )
    # git's line is the diagnosis the fix says to repair, and the root a path: both whole, escaped
    parent = H.scratch_dir()
    said = "fatal: a\\b " + "w" * 90
    odd = repo(own(), parent=parent)
    odd.write("scratch.txt", "x\n")
    odd_hooked = broken(
        hook(odd.root, env=fake_git(real, "status", said)),
        f"BROKEN: git could not read the working tree in {parent}/"
        + WEIRD_DIR_SHOWN
        + ": fatal: a\\\\b "
        + "w" * 90
        + " — fix: repair what git names in the message, then check by hand:"
        " git -C <that directory> status",
    )
    r3 = repo(with_map(), parent=H.scratch_dir())
    branch(r3.root)
    commit(r3.root, "code", {"src/a.py": "2\n"})
    odd_range = broken(
        scan(r3.root, env=fake_git(real, "merge-base", said)),
        f"BROKEN: git could not read the range {short(r3.root, 'main')}..{short(r3.root)} in"
        f" {r3.root.parent}/"
        + WEIRD_DIR_SHOWN
        + ": fatal: a\\\\b "
        + "w" * 90
        + " — fix: repair what git names in the message; "
        + SHALLOW,
    )
    return all_of(
        [hooked, scanned, odd_hooked, odd_range],
        "git status failing in the hook, git ls-files in the scan: exit 1 each",
    )


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
    pattern_dial=PatternDial("working_files", lambda pattern: own(working_files=[pattern])),
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
    (
        10,
        "the trunk dial names the base, the fresher of a local and a tracked trunk; an unknown trunk is a"
        " configuration failure",
        trunk_dial,
    ),
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
    (
        16,
        "an unknown ref is a configuration failure, never a skip; a ref that begins with a dash is one,"
        " before git is asked",
        unknown_ref,
    ),
    (
        17,
        "trailers read beside Co-Authored-By, a repeated key, one note each; a signed commit's note on one"
        " line; a git too old for the trailer options is a configuration failure naming git",
        trailer_among_others,
    ),
    (
        18,
        "a colon-less line hides the paragraph: red, and the fix teaches the rule",
        colonless_line_hides_paragraph,
    ),
    (19, "the body's line in any case with any dash; an unreadable body", body_forms),
    (
        20,
        "T3 for a declaration naming no pair, T4 for one without a reason, beside T2; the same in a signed"
        " commit",
        t3_and_t4,
    ),
    (21, "a declaration for a pair the change does not touch earns its note", untouched_pair_note),
    (22, "declaration_key: the dial's key is read and the default is not", declaration_key_dial),
    (23, "overlapping pairs both apply, each satisfied its own way", overlapping_pairs),
    (24, "a document inside its own pair's code is not its own trigger", document_is_no_trigger),
    (25, "a deleted or renamed path counts as touched, on both sides", deleted_and_renamed_are_touched),
    (
        26,
        "X1 for a document that never was, X2 for a directory; not for a deleted one; an older change"
        " under today's map",
        missing_document,
    ),
    (27, "an empty map examines zero pairs and says so", empty_map),
    (28, "dial failures: each C5 text, a docs path with a trailing slash among them, exit 1", dial_failures),
    (29, "a pattern git would misread, in code and in working_files", unreadable_patterns),
    (30, "working_files: tracked matches are a note, untracked ones are not", working_files_note),
    (31, "a misspelt dial is a configuration failure", misspelt_dial),
    (
        32,
        "golden lines of T1–T4, X1, X2, the trailing-slash C5, the count forms and the ellipsis of T1 and"
        " T2, typed by hand",
        golden_lines,
    ),
    (33, "the hooks file's shape", hooks_file_shape),
    (
        34,
        "the skill descriptions' sizes, each with its trigger and its advisory line; the install note's"
        " example accepted as it stands",
        skills_and_install_note,
    ),
    (35, "the hook validates the dials too", hook_validates_dials),
    (36, "an orphan branch is unborn; a HEAD git cannot read is a configuration failure", broken_head),
    (37, "two histories with no common commit: the range failure says so in words", unrelated_histories),
    (
        38,
        "red→green: a docs path naming a directory is refused, a trailing slash at the read and a tree at"
        " HEAD by the scan; the file named, the change is examined",
        directory_named_as_document,
    ),
    (
        39,
        "git failing on the working tree is a configuration failure, in the hook and in the scan",
        unreadable_tree,
    ),
]

ASSERTIONS = [Assertion(number, title, check) for number, title, check in ITEMS]

if __name__ == "__main__":
    sys.exit(H.run_all([], [*ASSERTIONS, *shared_assertions(SUBJECT, first=101)]))
