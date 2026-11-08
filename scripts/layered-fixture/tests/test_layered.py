"""Fixtures of the fixture gate know-check: `python3 -m pytest tests` from the fixture's folder.

The gate is a gate of another layer: its namespace and its layer's keys stand in `layer.yaml`, the policies
in the constitution's file. This file holds what is its own, items 1 on, and hands the shared items its
`SUBJECT`, which they run against: the items every gate shares, from 101, so the run shows that each of them
holds for a gate whose dials file is not the constitution's.
"""

from __future__ import annotations

import datetime
import json
import shlex
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from constitution_layer_kit import identity, ways
from constitution_layer_kit import messages as shared
from constitution_layer_kit.effect import History, Outcome
from constitution_layer_kit.history import read_transcript
from constitution_layer_kit.model import KERNEL_KEYS
from constitution_layer_kit.testing.acceptance import broken_first_line, expect, item
from constitution_layer_kit.testing.consumer import ROOT_POLICY, Consumer, document, dump, envelope
from constitution_layer_kit.testing.harness import Edit, Harness, Result, Write, event_json
from constitution_layer_kit.testing.items import (
    NO_ENVELOPE,
    Subject,
    fake_claude,
    log_record,
    reader_fake,
    tr_blocked,
    tr_call,
    tr_hook,
    tr_line,
    tr_turn,
)
from layered_gate import messages, start

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
NAMESPACE = start.GATE.namespace
H = Harness(
    SCRIPTS,
    "check-layered.sh",
    "check-layered.py",
    NAMESPACE,
    dials_file=start.GATE.dials_file,
    kernel_keys=start.GATE.kernel_keys,
)

NOTE_A = "docs/notes/a.md"
NOTES_POLICY = "docs/policies/notes-policy.md"
PHRASE = "forbidden-word"  # the phrase the notes policy of every consumer of this gate forbids
# the lines the gate prints, typed by hand
L1_LINE = (
    "BROKEN: layer.yaml: layer_dialect is 'fancy', and this layer knows only 'plain' — fix: know-check reads"
    " documents in one dialect, and a dialect it does not know would be judged by rules written for another:"
    " set layer_dialect: plain in layer.yaml, or remove the line"
)
L2_LINE = (
    "BROKEN: layer.yaml: notes-policy is a policy's namespace, and the policies stand in another file"
    " — fix: a policy declared in two files would have two territories, and know-check reads it from one"
    " only: move the 'notes-policy' key, with its territory, to the file of the constitution's policies, and"
    " remove it from this file"
)
L3_FINDING = (
    "RED: docs/notes/a.md: holds 'forbidden-word', which its policy 'notes-policy' forbids\n"
    "  why: a policy lists what its documents must not say, and a document that says it breaks the rule it is"
    " governed by\n"
    "  fix: remove 'forbidden-word' from the document, or remove the line 'FORBIDDEN: forbidden-word' from"
    " the policy 'notes-policy'"
)
NO_ROOT_LINE = (
    "GREEN: know-check: 0 documents examined — constitution.yaml has no root_policy: nothing is claimed"
)


def gate_on(
    action: Write | Edit,
    dials_patch: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    raw_dials: str | None = None,
    files: dict[str, str] | None = None,
    remove: str | None = None,
) -> tuple[Result, Path]:
    """The gate's run on a prepared consumer, whose notes policy forbids `PHRASE`, which `RED` holds."""
    consumer = H.fresh_consumer()
    consumer.write_dials(dials_patch, raw_dials)
    consumer.write(NOTES_POLICY, forbidding("notes-policy"))
    for rel, text in (files or {}).items():
        consumer.write(rel, text)
    if remove is not None:
        (consumer.root / remove).unlink()
    return H.run_gate(event_json(consumer.root, action), env=env), consumer.root


def own(**dials: object) -> dict[str, object]:
    return {NAMESPACE: dials}


def claim(territory: Sequence[str]) -> dict[str, object]:
    """The dials patch that gives the notes policy another territory: it goes to the constitution's file."""
    return {"notes-policy": {"territory": list(territory)}}


def forbidding(policy: str) -> str:
    """The text of a policy that forbids `PHRASE` to its documents, by the line the gate reads."""
    return document(
        body=f"# Policy\n\nFORBIDDEN: {PHRASE}\n",
        id=policy,
        type="current-state",
        title=f"Fixture {policy}",
        status="active",
    )


VALID = Write(NOTE_A, envelope("note-a"))
RED = Write(
    NOTE_A,
    document(f"# Note\n\n{PHRASE}\n", id="note-a", type="non-authoritative", title="Note A", status="active"),
)


def built(raw_constitution: str | None = None, raw: str | None = None) -> Consumer:
    consumer = H.fresh_consumer()
    consumer.write_dials(None, raw, raw_constitution)
    return consumer


def run(consumer: Consumer, action: Write = VALID) -> Result:
    return H.run_gate(event_json(consumer.root, action))


@item(
    1,
    "L3: a document that holds a phrase its policy forbids is blocked; with the line gone, it passes",
)
def test_forbidden_policy() -> None:
    red, _ = gate_on(RED)
    expect(red, 2, L3_FINDING, "stderr")
    assert [line for line in red.stderr.splitlines() if line.startswith("RED:")] == [
        "RED: docs/notes/a.md: holds 'forbidden-word', which its policy 'notes-policy' forbids",
        "RED: 1 finding(s) — 1 document examined (docs/notes/a.md)",
    ]
    assert L3_FINDING == messages.l3_forbidden(NOTE_A, "notes-policy", PHRASE).render()
    green, _ = gate_on(VALID)
    expect(green, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")
    plain = {
        NOTES_POLICY: envelope("notes-policy", "current-state")
    }  # the same document, a policy without the line
    unforbidden, _ = gate_on(RED, files=plain)
    expect(unforbidden, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")


@item(
    2,
    "L1: a layer_dialect other than plain is a configuration failure of the layer's file, plain passes",
)
def test_layer_dialect() -> None:
    result, _ = gate_on(VALID, dials_patch={"layer_dialect": "fancy"})
    broken_first_line(result, L1_LINE)
    assert L1_LINE == messages.l1_dialect("fancy").render()
    listed, _ = gate_on(VALID, dials_patch={"layer_dialect": ["plain"]})
    assert listed.code == 1 and "layer_dialect is '['plain']'" in listed.stderr, listed.stderr
    plain, _ = gate_on(VALID, dials_patch={"layer_dialect": "plain"})
    expect(plain, 0, "governed by notes-policy", "stdout")


@item(
    3,
    "L2: a policy's namespace in the layer's file is refused; the policies stand in the constitution's",
)
def test_policy_namespace_in_layer_file() -> None:
    raw = "module_prefix: know-\nnotes-policy:\n  territory:\n    - 'docs/notes/**'\n"
    result, _ = gate_on(VALID, raw_dials=raw)
    broken_first_line(result, L2_LINE)
    assert L2_LINE == messages.l2_policy_namespace("notes-policy").render()


@item(4, "a constitution file with no root_policy, or none at all, is a skip that names that file")
def test_no_root_policy() -> None:
    without = dump({"module_prefix": "const-", "notes-policy": {"territory": ["docs/notes/**"]}})
    result = run(built(raw_constitution=without))
    expect(result, 0, NO_ROOT_LINE, "stdout")
    consumer = built()
    (consumer.root / "constitution.yaml").unlink()
    expect(run(consumer), 0, NO_ROOT_LINE, "stdout")


@item(5, "a failure of the policies names the constitution's file, and a failure of the layer's keys its own")
def test_failures_name_their_file() -> None:
    gone = dump({"root_policy": "docs/policies/gone.md", "module_prefix": "const-"})
    result = run(built(raw_constitution=gone))
    with identity.reading("constitution.yaml", KERNEL_KEYS):
        wanted = shared.c6_root_missing("docs/policies/gone.md").render()
    broken_first_line(result, wanted)
    assert wanted.startswith("BROKEN: constitution.yaml names root_policy"), wanted
    bad = dump({"root_policy": ROOT_POLICY, "module_prefix": "const-", "territory_dialect": "regex"})
    result = run(built(raw_constitution=bad))
    with identity.reading("constitution.yaml", KERNEL_KEYS):
        wanted = shared.c5_dialect_unsupported("regex").render()
    broken_first_line(result, wanted)
    assert wanted.startswith("BROKEN: constitution.yaml: territory_dialect"), wanted
    alone = "module_prefix: know-\nroot_policy: docs/policies/root-policy.md\n"
    result = run(built(raw=alone))
    with identity.reading("layer.yaml", start.GATE.kernel_keys):
        wanted = shared.c5_kernel_key_elsewhere("root_policy").render()
    broken_first_line(result, wanted)
    assert wanted.startswith("BROKEN: layer.yaml: root_policy is no key of this file"), wanted


@item(6, "the policies are the constitution's alone: a territory written in the layer's file moves nothing")
def test_territory_comes_from_the_constitution() -> None:
    outside, _ = gate_on(Write("docs/other/a.md", NO_ENVELOPE), dials_patch=own(severity="warn"))
    expect(outside, 0, "docs/other/a.md is outside claimed territory", "stdout")
    moved, _ = gate_on(Write("docs/other/a.md", NO_ENVELOPE), dials_patch=claim(["docs/other/**"]))
    expect(moved, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")


@item(7, "the scan reads both files: the finding of a forbidden phrase, and the green line of a clean tree")
def test_scan() -> None:
    consumer = H.fresh_consumer()
    consumer.write(NOTES_POLICY, forbidding("notes-policy"))
    consumer.write(NOTE_A, VALID.text)
    green = H.run_gate("", args=["--scan", str(consumer.root)])
    expect(
        green,
        0,
        "GREEN: know-check: 4 governed document(s) examined, 4 Markdown file(s) scanned, 3 policies",
        "stdout",
    )
    consumer.write(NOTE_A, RED.text)
    red = H.run_gate("", args=["--scan", str(consumer.root)])
    expect(red, 2, L3_FINDING, "stdout")
    assert (
        "RED: 1 finding(s) — 4 governed document(s) examined, 4 Markdown file(s) scanned, 3 policies"
        in red.stdout
    )


@item(
    8, "an envelope nobody can read is no finding of this gate and no crash: the path mapping decides alone"
)
def test_unreadable_envelope_is_no_crash() -> None:
    for text in ("---\nid: [unclosed\n---\n", "---\nid: a\n", "---\n" + "[" * 5000 + "\n---\n"):
        result, _ = gate_on(Write(NOTE_A, text))
        expect(result, 0, "GREEN: know-check: 1 document examined, governed by notes-policy", "stdout")


@item(
    9,
    "W1: a Markdown write is applied when a run of the hook script examined it, else bypassed by B1",
)
def test_effect_pattern_rule() -> None:
    """A hand-made transcript: a Write examined by a run of `check-layered.sh`, an Edit likewise, and a Write
    whose call that script blocked are applied; a Write with no run, and one whose only run is of another
    script, are bypassed by way B1; a write of a file that is no Markdown is no moment. The line is typed by
    hand."""
    root = H.fresh_consumer().root
    folder = H.scratch_dir()
    sid, at = "s9", "2026-11-03T10:00:00.000Z"
    lines = [
        tr_call(sid, root, at, "t1", "Write", root / "a.md"),
        tr_hook(sid, root, at, "t1", "check-layered.sh"),
        tr_call(sid, root, at, "t2", "Write", root / "b.md"),
        tr_call(sid, root, at, "t3", "Write", root / "c.md"),
        tr_hook(sid, root, at, "t3", "other.sh"),
        tr_call(sid, root, at, "t4", "Write", root / "d.txt"),
        tr_call(sid, root, at, "t5", "Edit", root / "e.md"),
        tr_hook(sid, root, at, "t5", "check-layered.sh"),
        tr_call(sid, root, at, "t6", "Write", root / "f.md"),
        tr_blocked(sid, root, at, "t6", "check-layered.sh"),
    ]
    (folder / "s9.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder)],
        env={"CLAUDE_PLUGIN_DATA": str(H.scratch_dir())},
        command=[H.sh, str(SCRIPTS / "effect-report.sh")],
        cwd=root,
    )
    wanted = "  W1 (pattern): 5 moment(s): 3 applied, 2 bypassed, 0 missed — B1 2"
    assert result.code == 0 and wanted in result.stdout.splitlines(), result.stdout + result.stderr


@item(10, "a run of the hook script that blocked its call is read as that script's run, and as blocked")
def test_blocked_hook_run() -> None:
    """The transcript line of a hook that blocked has no `command`: its text opens with the command in
    brackets. The reader takes the script from there and marks the run blocked; a run that let the call
    through is not blocked."""
    root = H.fresh_consumer().root
    path = H.scratch_dir() / "s10.jsonl"
    lines = [
        tr_call("s10", root, "2026-11-03T10:00:00.000Z", "t1", "Write", root / "a.md"),
        tr_blocked("s10", root, "2026-11-03T10:00:00.000Z", "t1", "check-layered.sh"),
        tr_call("s10", root, "2026-11-03T10:00:00.000Z", "t2", "Write", root / "b.md"),
        tr_hook("s10", root, "2026-11-03T10:00:00.000Z", "t2", "check-layered.sh"),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    session = read_transcript(path)
    assert session is not None
    seen = [(run.tool_use_id, run.script, run.blocked) for run in session.hook_runs()]
    assert seen == [("t1", "check-layered.sh", True), ("t2", "check-layered.sh", False)], seen


@item(11, "W3: a hook record of the log counts only where no transcript holds its session")
def test_effect_log_only() -> None:
    """The log holds a hook record of session `held`, whose transcript is read, and one of `unheld`, whose
    transcript is not; only the second is a moment of W3, applied. A scan record counts for none."""
    root = H.fresh_consumer().root
    folder, data = H.scratch_dir(), H.scratch_dir()
    at = "2026-11-03T10:00:00.000Z"
    (folder / "held.jsonl").write_text(tr_turn("held", root, at, "hello") + "\n", encoding="utf-8")
    records = [
        log_record(NAMESPACE, at, "hook", "held", str(root / "a.md")),
        log_record(NAMESPACE, at, "hook", "unheld", str(root / "b.md")),
        log_record(NAMESPACE, at, "scan", "unheld", ""),
    ]
    (data / f"{NAMESPACE}.jsonl").write_text("\n".join(records) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder)],
        env={"CLAUDE_PLUGIN_DATA": str(data)},
        command=[H.sh, str(SCRIPTS / "effect-report.sh")],
        cwd=root,
    )
    wanted = "  W3 (pattern): 1 moment(s): 1 applied, 0 bypassed, 0 missed"
    assert result.code == 0 and wanted in result.stdout.splitlines(), result.stdout + result.stderr


# ---------------------------------------------------------------- the helpers of `ways` (items 12 on)
# The fixture's rules W4 to W11 are each built by one helper of `constitution_layer_kit.ways`; the items
# below run the report over hand-made transcripts and over git histories made in a scratch repository, and
# call a helper directly for a parameter the fixture's rule does not set.

WAY_AT = "2026-11-03T10:00:00.000Z"
NOTES_DIR = "docs/notes"


def tr_tool(sid: str, cwd: Path, call_id: str, name: str, **given: object) -> str:
    """A tool call of any tool, with its input as given."""
    block = {"type": "tool_use", "id": call_id, "name": name, "input": given}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def tr_say(sid: str, cwd: Path, text: str) -> str:
    block = {"type": "text", "text": text}
    return tr_line("assistant", sid, cwd, WAY_AT, message={"role": "assistant", "content": [block]})


def tr_red(sid: str, cwd: Path, call_id: str, text: str) -> str:
    """A run of the fixture's hook script that blocked its call, with the text it printed."""
    done = {
        "type": "hook_blocking_error",
        "hookName": "PreToolUse:Write",
        "toolUseID": call_id,
        "hookEvent": "PreToolUse",
        "blockingError": {"blockingError": f"[sh /x/plugin/scripts/check-layered.sh]: {text}"},
    }
    return tr_line("attachment", sid, cwd, WAY_AT, attachment=done)


def tr_ask(sid: str, cwd: Path, call_id: str) -> str:
    """A run of the fixture's hook script that let its call through with the verdict `ask`."""
    done = {
        "hookName": "PreToolUse:Write",
        "toolUseID": call_id,
        "hookEvent": "PreToolUse",
        "command": "sh /x/plugin/scripts/check-layered.sh",
        "exitCode": 0,
        "stdout": '{"hookSpecificOutput": {"permissionDecision": "ask"}}',
    }
    return tr_line("attachment", sid, cwd, WAY_AT, attachment=done)


def effect_lines(
    root: Path, sessions: Mapping[str, Sequence[str]], env: Mapping[str, str] | None = None, *flags: str
) -> list[str]:
    """The lines of the report over the sessions, one transcript each; the report must exit 0."""
    folder = H.scratch_dir()
    for name, lines in sessions.items():
        (folder / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder), *flags],
        env={"CLAUDE_PLUGIN_DATA": str(H.scratch_dir()), **(env or {})},
        command=[H.sh, str(SCRIPTS / "effect-report.sh")],
        cwd=root,
    )
    assert result.code == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def no_plugins(listed: str = "[]") -> dict[str, str]:
    """The environment of a fake `claude` that lists `listed` as its plugins."""
    return fake_claude(H.scratch_dir(), f"echo {shlex.quote(listed)}\n")


def direct_history(root: Path, plugin: Path | None = None, scripts: frozenset[str] = frozenset()) -> History:
    """The history a rule reads, made by hand: no session, no log."""
    return History(root, scripts, (), (), "", NAMESPACE, start.GATE.dials_file, plugin)


def git_in(root: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)
    return done.stdout


@item(
    12,
    "H1: the Markdown paths a shell command changes, by pattern: redirect, tee, sed -i, mv, cp, rm, Python",
)
def test_shell_changes() -> None:
    """Each command is read for the Markdown paths it seems to change and no others; a read, a pattern in a
    quote that is no command, and a path that is no Markdown are none. The lists are typed by hand."""
    table: list[tuple[str, list[str]]] = [
        ("echo hi > docs/a.md", ["docs/a.md"]),
        ('echo hi >> "docs/b.md"', ["docs/b.md"]),
        ("echo hi >docs/q.md", ["docs/q.md"]),
        ("cat x | tee -a docs/c.md docs/d.txt", ["docs/c.md"]),
        ("sed -i '' 's/a/b/' docs/e.md", ["docs/e.md"]),
        ("sed -n 's/a/b/p' docs/f.md", []),
        ("perl -pi -e 's/a/b/' docs/g.md", ["docs/g.md"]),
        ("git mv docs/h.md docs/i.md", ["docs/h.md", "docs/i.md"]),
        ("git rm -f docs/j.md", ["docs/j.md"]),
        ("git log docs/j.md", []),
        ("mv a.md b.md && cp c.md d.md", ["a.md", "b.md", "d.md"]),
        ("rm -rf docs/k.md docs/l", ["docs/k.md"]),
        ("ENV=1 rm docs/s.md", ["docs/s.md"]),
        ('python3 -c \'from pathlib import Path; Path("docs/m.md").write_text("x")\'', ["docs/m.md"]),
        ('python3 -c \'open("docs/n.md", "w").write("x")\'', ["docs/n.md"]),
        ('python3 -c \'open("docs/r.md", "r").read()\'', []),
        ("ls docs/o.md; cat docs/p.md 2>/dev/null", []),
        ("grep -r x . > out.txt", []),
    ]
    wrong = [(c, ways.shell_changes(c), want) for c, want in table if ways.shell_changes(c) != want]
    assert not wrong, wrong


@item(13, "W4: a Markdown write in the territory is applied when a hook run examined it, else bypassed by B1")
def test_path_bypass() -> None:
    """A write examined by a run of the hook script is applied. A write no run examined, a shell redirect, a
    write through a worktree of the project (below `.claude/worktrees/<name>/`) are bypassed by B1, and the
    worktree's is read as the path in the root. A file outside the territory, one that is no Markdown, and a
    path outside the project are no moment. The line is typed by hand."""
    root = H.fresh_consumer().root
    sid = "s13"
    inside = root / "docs" / "notes"
    worktree = root / ".claude" / "worktrees" / "w" / "docs" / "notes" / "w.md"
    lines = [
        tr_call(sid, root, WAY_AT, "t1", "Write", inside / "a.md"),
        tr_hook(sid, root, WAY_AT, "t1", "check-layered.sh"),
        tr_call(sid, root, WAY_AT, "t2", "Write", inside / "b.md"),
        tr_tool(sid, root, "t3", "Bash", command="echo x > docs/notes/c.md"),
        tr_tool(sid, root, "t4", "Bash", command="echo x > README.md"),
        tr_call(sid, root, WAY_AT, "t5", "Write", worktree),
        tr_call(sid, root, WAY_AT, "t6", "Write", root / "docs" / "other" / "d.md"),
        tr_call(sid, root, WAY_AT, "t7", "Write", inside / "e.txt"),
        tr_call(sid, root, WAY_AT, "t8", "Write", Path("/elsewhere/docs/notes/f.md")),
    ]
    found = effect_lines(root, {sid: lines}, no_plugins())
    wanted = "  W4 (pattern): 4 moment(s): 1 applied, 3 bypassed, 0 missed — B1 3"
    assert wanted in found, found


@item(14, "H2: a path is read as the project's root sees it, a worktree's and another checkout's too")
def test_relative_paths() -> None:
    """A path below the root is relative to it; below `.claude/worktrees/<name>/` of the root, relative to
    that worktree; in another checkout of the project, made by `git worktree add`, relative to that
    checkout's top, found by git from the call's folder; in another repository or nowhere, none."""
    consumer = H.fresh_consumer()
    root = consumer.root
    history = direct_history(root)
    other = H.scratch_dir() / "other"
    git_in(root, "worktree", "add", "-q", "-b", "elsewhere", str(other))
    stranger = H.fresh_consumer().root
    table = [
        (str(root / "docs" / "a.md"), "", "docs/a.md"),
        ("docs/b.md", str(root), "docs/b.md"),
        (str(root / ".claude" / "worktrees" / "w" / "docs" / "c.md"), "", "docs/c.md"),
        (str(other / "docs" / "d.md"), str(other / "docs"), "docs/d.md"),
        (str(other / "docs" / "d.md"), "", None),
        (str(stranger / "docs" / "e.md"), str(stranger), None),
        ("/elsewhere/f.md", "", None),
        ("", "", None),
    ]
    got = [ways.relative(history, path, cwd) for path, cwd, _ in table]
    assert got == [want for _, _, want in table], got


@item(15, "W5: the plugin enabled for this project is applied, listed and disabled is bypassed by B2")
def test_switch_off_plugin() -> None:
    """A fake `claude plugin list --json` lists the gate for this project three times, enabled twice (one
    with no project path) and disabled once, and once for another project, and another plugin: the three
    for this project are moments. A list with no entry for the gate, one that is no JSON and one that
    fails are notes and no moment. The lines are typed by hand."""
    root = H.fresh_consumer().root
    here, elsewhere = str(root), str(H.scratch_dir())
    entries = [
        {"id": f"{NAMESPACE}@a", "enabled": True, "projectPath": here},
        {"id": f"{NAMESPACE}@b", "enabled": False, "projectPath": here},
        {"id": f"{NAMESPACE}@d", "enabled": True},
        {"id": f"{NAMESPACE}@c", "enabled": False, "projectPath": elsewhere},
        {"id": "another@a", "enabled": False, "projectPath": here},
    ]
    found = effect_lines(root, {}, no_plugins(json.dumps(entries)))
    assert "  W5 (pattern): 3 moment(s): 2 applied, 1 bypassed, 0 missed — B2 1" in found, found
    unlisted = effect_lines(root, {}, no_plugins(json.dumps(entries[3:])))
    assert "  W5 (pattern): 0 moment(s): 0 applied, 0 bypassed, 0 missed" in unlisted, unlisted
    note_unlisted = (
        "note: know-check: W5: the plugin list names this plugin for no scope of this project —"
        " whether it is enabled is not counted"
    )
    assert note_unlisted in unlisted, unlisted
    note_failed = (
        "note: know-check: W5: the plugin list could not be read (exit 3, no JSON list) —"
        " whether the plugin is enabled is not counted"
    )
    failing = effect_lines(root, {}, fake_claude(H.scratch_dir(), "exit 3\n"))
    assert (
        note_failed in failing and "  W5 (pattern): 0 moment(s): 0 applied, 0 bypassed, 0 missed" in failing
    ), failing
    note_json = note_failed.replace("exit 3", "exit 0")
    garbage = effect_lines(root, {}, fake_claude(H.scratch_dir(), "echo no list\n"))
    assert note_json in garbage, garbage


@item(
    16,
    "W5: a change of the gate's dials is applied, or bypassed by B2 when severity falls or a dial loosens",
)
def test_switch_off_dials() -> None:
    """Five commits of the dials file: the gate's namespace added with `severity: block` (applied), severity
    turned to `warn` (bypassed), back to `block` with `lenient: true`, the module's own loosened dial
    (bypassed), a dial added that loosens nothing (applied), and another namespace changed (no moment). A
    commit whose YAML cannot be read is a note. The lines are typed by hand."""
    consumer = H.fresh_consumer()
    root = consumer.root
    steps = [
        own(severity="block"),
        own(severity="warn"),
        own(severity="block", lenient=True),
        own(severity="block", lenient=True, other=1),
    ]
    for step in steps:
        consumer.write_dials(step)
        consumer.commit()
    text = (root / start.GATE.dials_file).read_text(encoding="utf-8")
    consumer.write(start.GATE.dials_file, text + "another-gate:\n  severity: warn\n")
    consumer.commit()
    found = effect_lines(root, {}, no_plugins())
    assert "  W5 (pattern): 4 moment(s): 2 applied, 2 bypassed, 0 missed — B2 2" in found, found
    other = H.fresh_consumer()
    other.write(start.GATE.dials_file, "know-check: [unclosed\n")
    other.commit()
    other.write_dials(own(severity="block"))
    other.commit()
    broken = effect_lines(other.root, {}, no_plugins())
    note = (
        "note: know-check: W5: the history of layer.yaml could not be read in full (2 commit(s) with"
        " ParserError) — the changes it failed on are not counted"
    )
    assert "  W5 (pattern): 0 moment(s): 0 applied, 0 bypassed, 0 missed" in broken, broken
    assert note in broken, broken


@item(
    17, "W6: after a red the next act on the file decides: a write is applied, a shell command bypassed by B3"
)
def test_after_red() -> None:
    """Eight sessions, each a red of the hook on a write of a note. The next act a write of the same file
    (applied); a `sed -i` of it (bypassed); a `git mv` of it (bypassed); a write of another file and then of
    this one (applied); a write of another file and then a shell command naming this one (bypassed); a write
    of another file and no more (bypassed); a human turn first (no moment); an `ask` verdict, then a write of
    the file (applied). The line is typed by hand."""
    root = H.fresh_consumer().root
    notes = root / NOTES_DIR

    def red(sid: str, name: str, *after: str, verdict: str = "red") -> list[str]:
        call = tr_call(sid, root, WAY_AT, "r", "Write", notes / name)
        run = tr_red(sid, root, "r", "RED: a finding") if verdict == "red" else tr_ask(sid, root, "r")
        return [call, run, *after]

    sessions = {
        "s17a": red("s17a", "a.md", tr_call("s17a", root, WAY_AT, "n", "Write", notes / "a.md")),
        "s17b": red(
            "s17b", "b.md", tr_tool("s17b", root, "n", "Bash", command="sed -i '' s/a/b/ docs/notes/b.md")
        ),
        "s17c": red(
            "s17c",
            "c.md",
            tr_tool("s17c", root, "n", "Bash", command="git mv docs/notes/c.md docs/notes/x.md"),
        ),
        "s17d": red(
            "s17d",
            "d.md",
            tr_call("s17d", root, WAY_AT, "n1", "Write", notes / "other.md"),
            tr_call("s17d", root, WAY_AT, "n2", "Edit", notes / "d.md"),
        ),
        "s17e": red(
            "s17e",
            "e.md",
            tr_call("s17e", root, WAY_AT, "n1", "Write", notes / "other.md"),
            tr_tool("s17e", root, "n2", "Bash", command="echo x >> docs/notes/e.md"),
        ),
        "s17f": red("s17f", "f.md", tr_call("s17f", root, WAY_AT, "n", "Write", notes / "other.md")),
        "s17g": red(
            "s17g",
            "g.md",
            tr_turn("s17g", root, WAY_AT, "stop"),
            tr_call("s17g", root, WAY_AT, "n", "Write", notes / "g.md"),
        ),
        "s17h": red(
            "s17h", "h.md", tr_call("s17h", root, WAY_AT, "n", "Write", notes / "h.md"), verdict="ask"
        ),
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W6 (pattern): 7 moment(s): 3 applied, 4 bypassed, 0 missed — B3 4" in found, found
    # a fixed_by of the module's own decides what the fix is: here an Edit alone
    session = read_transcript(_write_transcript(sessions["s17a"]))
    assert session is not None
    history = History(root, frozenset({"check-layered.sh"}), (session,), (), "", NAMESPACE)
    only_edit = ways.after_red("X", "x", lambda _red, act: act.name == "Edit")
    assert [m.outcome for m in list(only_edit.find(history))] == [Outcome.BYPASSED]


def _write_transcript(lines: Sequence[str]) -> Path:
    path = H.scratch_dir() / "direct.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@item(18, "W7: the skill a red names is loaded before the next act on the file, or the red is missed by B5")
def test_skill_after_red() -> None:
    """A red whose text says `load the skill know-check:notes`: a Skill call naming it, in full or bare,
    before the next write of the file is applied; a write first is missed, and a load after that write too; a
    Skill call after a write of another file and before the file's own is applied; a Skill call for another
    skill is missed; a red whose text names no skill is no moment. The line is typed by hand."""
    root = H.fresh_consumer().root
    notes = root / NOTES_DIR
    text = "RED: x\nknow-check: load the skill know-check:notes before you fix this — it teaches the rule"
    skill = tr_tool

    def case(sid: str, *after: str, said: str = text) -> list[str]:
        return [
            tr_call(sid, root, WAY_AT, "r", "Write", notes / "a.md"),
            tr_red(sid, root, "r", said),
            *after,
        ]

    sessions = {
        "s18a": case("s18a", skill("s18a", root, "k", "Skill", skill="know-check:notes")),
        "s18b": case("s18b", skill("s18b", root, "k", "Skill", skill="notes")),
        "s18c": case("s18c", tr_call("s18c", root, WAY_AT, "w", "Write", notes / "a.md")),
        "s18d": case(
            "s18d",
            tr_call("s18d", root, WAY_AT, "w", "Write", notes / "b.md"),
            skill("s18d", root, "k", "Skill", skill="know-check:notes"),
        ),
        "s18e": case("s18e", skill("s18e", root, "k", "Skill", skill="know-check:other")),
        "s18f": case("s18f", said="RED: x"),
        "s18g": case(
            "s18g",
            tr_call("s18g", root, WAY_AT, "w", "Write", notes / "a.md"),
            skill("s18g", root, "k", "Skill", skill="know-check:notes"),
        ),
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W7 (pattern): 6 moment(s): 3 applied, 0 bypassed, 3 missed — B5 3" in found, found


@item(19, "W8: a skill loaded earlier in the session makes the act applied, none makes it missed by B5")
def test_skill_before() -> None:
    """The moment is a write of a note. A Skill call for the skill, in full or bare, earlier in the session
    makes it applied, and stays so for a later write; a write with no load, one after a load of another
    skill, and one in another session are missed; a write that is no note is no moment. The line is typed by
    hand."""
    root = H.fresh_consumer().root
    notes = root / NOTES_DIR
    sessions = {
        "s19a": [
            tr_tool("s19a", root, "k", "Skill", skill="know-check:notes-guide"),
            tr_call("s19a", root, WAY_AT, "w1", "Write", notes / "a.md"),
            tr_call("s19a", root, WAY_AT, "w2", "Edit", notes / "b.md"),
            tr_call("s19a", root, WAY_AT, "w3", "Write", root / "README.md"),
        ],
        "s19b": [
            tr_call("s19b", root, WAY_AT, "w1", "Write", notes / "a.md"),
            tr_tool("s19b", root, "k", "Skill", skill="notes-guide"),
            tr_call("s19b", root, WAY_AT, "w2", "Write", notes / "b.md"),
        ],
        "s19c": [
            tr_tool("s19c", root, "k", "Skill", skill="know-check:other"),
            tr_call("s19c", root, WAY_AT, "w1", "Write", notes / "a.md"),
        ],
    }
    found = effect_lines(root, sessions, no_plugins())
    assert "  W8 (pattern): 5 moment(s): 3 applied, 0 bypassed, 2 missed — B5 2" in found, found


def scratch_main(consumer: Consumer) -> Path:
    """The consumer's repository with its branch named `main`, and its notes policy forbidding the phrase."""
    consumer.git("branch", "-M", "main")
    consumer.write(NOTES_POLICY, forbidding("notes-policy"))
    consumer.commit()
    return consumer.root


@item(
    20,
    "W9: the scan on each commit of the main branch in a throwaway clone: green applied, red bypassed by B4",
)
def test_escape() -> None:
    """Four commits of `main`: the fixture, the policy that forbids the phrase, a note that holds it (the
    scan is red there), and the note without it. The scan of the current plugin runs on a shared clone at
    each, outside the project, which stays as it was. The line is typed by hand."""
    consumer = H.fresh_consumer()
    root = scratch_main(consumer)
    consumer.write(NOTE_A, RED.text)
    consumer.commit()
    consumer.write(NOTE_A, VALID.text)
    consumer.commit()
    before = git_in(root, "status", "--porcelain", "--ignored"), sorted(p.name for p in root.iterdir())
    found = effect_lines(root, {}, no_plugins())
    assert "  W9 (pattern): 4 moment(s): 3 applied, 1 bypassed, 0 missed — B4 1" in found, found
    after = git_in(root, "status", "--porcelain", "--ignored"), sorted(p.name for p in root.iterdir())
    assert after == before, (before, after)


def fake_plugin(body: str) -> Path:
    """A plugin folder whose one script, `check-fake.sh`, is `body`."""
    folder = H.scratch_dir() / "plugin"
    (folder / "scripts").mkdir(parents=True)
    (folder / "scripts" / "check-fake.sh").write_text(body, encoding="utf-8")
    return folder


@item(
    21,
    "H7: the module gives the scan's arguments, other exit codes are notes, the last 50 commits count",
)
def test_escape_parameters() -> None:
    """A fake scan wrapper that logs its folder and arguments and exits as the commit's number says. The
    module's `scan_argv` gives its arguments, which name the commit; the folder is a clone outside the
    project; exit 1 is a note and no moment. With no main branch it is a note. Over 50 commits only the
    last 50 are scanned and a note says so."""
    consumer = H.fresh_consumer()
    root = scratch_main(consumer)
    log = H.scratch_dir() / "log"
    body = f'echo "$PWD $*" >> {shlex.quote(str(log))}\nexit 0\n'
    plugin = fake_plugin(body)
    scripts = frozenset({"check-fake.sh"})
    rule = ways.escape("X", "x", lambda commit: ["--scan", "--change", commit], "check-fake.sh")
    history = direct_history(root, plugin, scripts)
    moments = list(rule.find(history))
    head = git_in(root, "rev-parse", "HEAD").strip()
    calls = log.read_text(encoding="utf-8").splitlines()
    assert [m.outcome for m in moments] == [Outcome.APPLIED] * 2 and len(calls) == 2, (moments, calls)
    assert calls[-1].endswith(f" --scan --change {head}") and not calls[-1].startswith(str(root)), calls
    # an exit that is neither 0 nor 2 gives no verdict
    failing = fake_plugin("exit 1\n")
    noted = direct_history(root, failing, scripts)
    assert list(rule.find(noted)) == []
    oldest = git_in(root, "rev-list", "--max-parents=0", "main").strip()
    assert noted.notes == [
        f"note: know-check: X: the scan gave no verdict at 2 commit(s), the first {oldest[:12]} (exit 1) —"
        " they are not counted"
    ], noted.notes
    # no main branch
    bare = H.scratch_dir()
    git_in(bare, "init", "-q", "-b", "trunk")
    git_in(
        bare,
        "-c",
        "user.name=f",
        "-c",
        "user.email=f@example.invalid",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "x",
    )
    lonely = direct_history(bare, plugin, scripts)
    assert list(rule.find(lonely)) == []
    assert lonely.notes == [
        "note: know-check: X: no commit of the main branch could be scanned (no main branch)"
    ], lonely.notes
    # a cap of 50
    many = H.scratch_dir()
    git_in(many, "init", "-q", "-b", "main")
    for number in range(52):
        git_in(
            many,
            "-c",
            "user.name=f",
            "-c",
            "user.email=f@example.invalid",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            str(number),
        )
    capped = direct_history(many, plugin, scripts)
    found = list(rule.find(capped))
    assert len(found) == 50 and capped.notes == [
        "note: know-check: X: 52 commit(s) of the main branch in the window, only the last 50 are scanned"
    ], capped.notes


@item(22, "W10: a text the rule is owed at is applied when it shows the form, else missed by B6")
def test_shape() -> None:
    """The fixture's owed text names a note; the form shown is a markdown link to it. A text with the link
    is applied, one that names it bare is missed, one that names none is no moment. The line is typed by
    hand."""
    root = H.fresh_consumer().root
    sid = "s22"
    lines = [
        tr_say(sid, root, "I wrote [a](docs/notes/a.md)."),
        tr_say(sid, root, "I changed [b](docs/notes/b.md) too."),
        tr_say(sid, root, "I wrote docs/notes/c.md."),
        tr_say(sid, root, "Nothing to show."),
    ]
    found = effect_lines(root, {sid: lines}, no_plugins())
    assert "  W10 (pattern): 3 moment(s): 2 applied, 0 bypassed, 1 missed — B6 1" in found, found


@item(
    23,
    "W11: a reader rule has one moment for each event the module names, the reader judges them with --reader",
)
def test_reader_rule() -> None:
    """The fixture names each text of the assistant: three moments, not judged without `--reader`, and judged
    by a fake reader that answers APPLIED with it. The moment's excerpt holds the events around it. The lines
    are typed by hand."""
    root = H.fresh_consumer().root
    sid = "s23"
    lines = [
        tr_turn(sid, root, WAY_AT, "first"),
        tr_say(sid, root, "one"),
        tr_say(sid, root, "two"),
        tr_say(sid, root, "three"),
    ]
    plain = effect_lines(root, {sid: lines}, no_plugins())
    assert "  W11 (reader): 3 moment(s), not judged — run again with --reader to judge them" in plain, plain
    env, _ = reader_fake(H.scratch_dir(), "claude.ai", json.dumps({"result": "APPLIED"}))
    judged = effect_lines(root, {sid: lines}, env, "--reader")
    assert "  W11 (reader): 3 moment(s): 3 applied, 0 bypassed, 0 missed" in judged, judged
    session = read_transcript(_write_transcript(lines))
    assert session is not None
    reader = ways.reader_rule("X", "x", lambda _session: [2])
    found = list(reader.find(History(root, frozenset(), (session,), (), "")))
    assert len(found) == 1 and found[0].where == "AssistantText" and found[0].outcome is None
    assert "HumanTurn: first" in found[0].excerpt and "AssistantText: three" in found[0].excerpt, found[0]


@item(
    24,
    "a call a PreToolUse hook refused and a red on a Stop are read as blocked runs of the plugin they name",
)
def test_refusal_and_feedback() -> None:
    """Claude Code records a refusal of a PreToolUse hook only in the call's tool result, and a hook's red
    on a Stop only as a line marked isMeta; each text names its command in brackets — a script, or
    `command hook <n>` — and ends with the plugin it comes from. The texts are those observed on Claude
    Code 2.1.286 on 2026-11-07, typed by hand. A run whose command names no script counts as the module's
    by its plugin."""
    root = H.fresh_consumer().root
    sid = "s24"
    tail = "\n\nThis hook comes from the know-check@fixture-marketplace plugin."
    refusal = {
        "type": "tool_result",
        "tool_use_id": "t1",
        "is_error": True,
        "content": "PreToolUse:Write hook error: [command hook 7]: RED: docs/notes/a.md: forbidden" + tail,
    }
    lines = [
        tr_call(sid, root, WAY_AT, "t1", "Write", root / "docs/notes/a.md"),
        tr_line("user", sid, root, WAY_AT, message={"role": "user", "content": [refusal]}),
        tr_line(
            "user",
            sid,
            root,
            WAY_AT,
            isMeta=True,
            message={"role": "user", "content": "Stop hook feedback:\n[command hook]: RED: dirty" + tail},
        ),
        tr_turn(sid, root, WAY_AT, "a human turn"),
    ]
    session = read_transcript(_write_transcript(lines))
    assert session is not None
    seen = [(r.tool_use_id, r.hook, r.script, r.blocked, r.plugin) for r in session.hook_runs()]
    assert seen == [
        ("t1", "PreToolUse:Write", "", True, "know-check"),
        ("", "Stop", "", True, "know-check"),
    ], seen
    turns = [e for e in session.events if type(e).__name__ == "HumanTurn"]
    assert len(turns) == 1, turns  # the feedback is no human turn
    history = History(root, frozenset(), (session,), (), "", namespace="know-check")
    runs = history.runs(session)
    assert [(call is not None, run.hook) for call, run in runs] == [
        (True, "PreToolUse:Write"),
        (False, "Stop"),
    ]
    assert not History(root, frozenset(), (session,), (), "", namespace="another").runs(session)


@item(25, "B3 and B5 after a red see a refusal whose command names no script, by the plugin its text names")
def test_red_by_plugin() -> None:
    """A PreToolUse refusal of `[command hook 7]` names no script, only the plugin. The workaround and the
    skill helpers count it as the module's red when its plugin is the module's, and as nobody's when it is
    another's. The fix is a Write of the same file after a load of the skill the red names."""
    root = H.fresh_consumer().root
    sid = "s25"

    def refusal(plugin: str) -> dict[str, object]:
        text = (
            "PreToolUse:Write hook error: [command hook 7]: RED: docs/notes/a.md: forbidden\n"
            "know-check: load the skill know-check:notes before you fix this"
            f"\n\nThis hook comes from the {plugin}@fixture-marketplace plugin."
        )
        return {"type": "tool_result", "tool_use_id": "t1", "is_error": True, "content": text}

    def lines(plugin: str) -> list[str]:
        return [
            tr_call(sid, root, WAY_AT, "t1", "Write", root / "docs/notes/a.md"),
            tr_line("user", sid, root, WAY_AT, message={"role": "user", "content": [refusal(plugin)]}),
            tr_tool(sid, root, "t2", "Skill", skill="know-check:notes"),
            tr_call(sid, root, WAY_AT, "t3", "Write", root / "docs/notes/a.md"),
        ]

    for plugin, wanted in (("know-check", 1), ("another", 0)):
        session = read_transcript(_write_transcript(lines(plugin)))
        assert session is not None
        history = History(root, frozenset(), (session,), (), "", namespace="know-check")
        fixed = list(ways.after_red("X", "x").find(history))
        loaded = list(ways.skill_after_red("Y", "y").find(history))
        assert len(fixed) == wanted and len(loaded) == wanted, (plugin, fixed, loaded)
        assert all(m.outcome is Outcome.APPLIED for m in fixed + loaded), (fixed, loaded)


@item(
    26,
    "W5: an absent severity reads as the default, so absent to warn is lowered; adding the namespace is not",
)
def test_switch_off_default() -> None:
    """Two histories of the dials file. In the first the gate's namespace comes in with no severity, which
    reads as `block` (applied), then gains `severity: warn` (bypassed by B2). In the second it comes in at
    `warn`: a project may adopt a module at warn, so that is no lowering (applied). Typed by hand."""
    first = H.fresh_consumer()
    for step in (own(other=1), own(other=1, severity="warn")):
        first.write_dials(step)
        first.commit()
    found = effect_lines(first.root, {}, no_plugins())
    assert "  W5 (pattern): 2 moment(s): 1 applied, 1 bypassed, 0 missed — B2 1" in found, found
    # a module whose default is warn: the same history lowers nothing, since absent already read as warn
    history = History(
        first.root, frozenset(), (), (), "", namespace=NAMESPACE, dials_file=start.GATE.dials_file
    )
    lenient = ways.switch_off("X", "x", default_severity="warn")
    outcomes = [m.outcome for m in lenient.find(history) if m.where.endswith(start.GATE.dials_file)]
    assert outcomes == [Outcome.APPLIED, Outcome.APPLIED], outcomes
    # and there, removing a written `severity: block` lowers the gate to the default, warn
    third = H.fresh_consumer()
    for step in (own(severity="block"), own(other=1)):
        third.write_dials(step)
        third.commit()
    history = History(
        third.root, frozenset(), (), (), "", namespace=NAMESPACE, dials_file=start.GATE.dials_file
    )
    removed = [m.outcome for m in lenient.find(history) if m.where.endswith(start.GATE.dials_file)]
    assert removed == [Outcome.APPLIED, Outcome.BYPASSED], removed
    second = H.fresh_consumer()
    second.write_dials(own(severity="warn"))
    second.commit()
    adopted = effect_lines(second.root, {}, no_plugins())
    assert "  W5 (pattern): 1 moment(s): 1 applied, 0 bypassed, 0 missed" in adopted, adopted


def tr_green(sid: str, cwd: Path, call_id: str, module: str) -> str:
    """A run that let its call through, recorded as Claude Code 2.1.317 records it on 2026-11-07: its command
    `command hook <n>`, naming no script, and only its output naming the module."""
    done = {
        "type": "hook_success",
        "hookName": "PreToolUse:Write",
        "toolUseID": call_id,
        "hookEvent": "PreToolUse",
        "command": "command hook 3",
        "exitCode": "0",
        "stdout": f"GREEN: {module}: 1 document examined, governed by notes-policy\n",
    }
    return tr_line("attachment", sid, cwd, WAY_AT, attachment=done)


def tr_result(sid: str, cwd: Path, call_id: str, text: str, error: bool) -> str:
    block = {"type": "tool_result", "tool_use_id": call_id, "is_error": error, "content": text}
    return tr_line("user", sid, cwd, WAY_AT, message={"role": "user", "content": [block]})


@item(27, "a run recorded as `command hook <n>` is its module's by the green line its output opens")
def test_green_by_module() -> None:
    """The run names no script and no plugin line; its output, `GREEN: <module>: …`, names the module. W4
    counts the write it examined applied, and a run that names another module leaves its write bypassed."""
    root = H.fresh_consumer().root
    sid = "s27"
    inside = root / "docs" / "notes"
    lines = [
        tr_call(sid, root, WAY_AT, "t1", "Write", inside / "a.md"),
        tr_green(sid, root, "t1", "know-check"),
        tr_call(sid, root, WAY_AT, "t2", "Write", inside / "b.md"),
        tr_green(sid, root, "t2", "another-check"),
    ]
    found = effect_lines(root, {sid: lines}, no_plugins())
    assert "  W4 (pattern): 2 moment(s): 1 applied, 1 bypassed, 0 missed — B1 1" in found, found
    session = read_transcript(_write_transcript(lines))
    assert session is not None
    assert [run.plugin for run in session.hook_runs()] == ["know-check", "another-check"]


@item(28, "W4: a write that failed, or that another hook refused, is no moment unless the gate examined it")
def test_failed_writes() -> None:
    """Four writes in the territory, each with its tool result: one that went through with no run of the
    hook (bypassed by B1); one the tool could not do and one another module's hook refused, neither seen
    by the hook (no moment: nothing changed); and one this gate's own hook refused (applied: the gate
    held)."""
    root = H.fresh_consumer().root
    sid = "s28"
    inside = root / "docs" / "notes"
    refused = (
        "PreToolUse:Write hook error: [command hook 7]: RED: docs/notes/d.md: forbidden"
        "\n\nThis hook comes from the {}@fixture-marketplace plugin."
    )
    lines = [
        tr_call(sid, root, WAY_AT, "t1", "Write", inside / "a.md"),
        tr_result(sid, root, "t1", "File created", False),
        tr_call(sid, root, WAY_AT, "t2", "Edit", inside / "b.md"),
        tr_result(sid, root, "t2", "String to replace not found in file.", True),
        tr_call(sid, root, WAY_AT, "t3", "Write", inside / "c.md"),
        tr_result(sid, root, "t3", refused.format("another-check"), True),
        tr_call(sid, root, WAY_AT, "t4", "Write", inside / "d.md"),
        tr_result(sid, root, "t4", refused.format("know-check"), True),
    ]
    found = effect_lines(root, {sid: lines}, no_plugins())
    assert "  W4 (pattern): 2 moment(s): 1 applied, 1 bypassed, 0 missed — B1 1" in found, found
    session = read_transcript(_write_transcript(lines))
    assert session is not None
    assert [call.failed for call in session.calls()] == [False, True, True, True]


@item(29, "--help on a module's entry and on the shared entry prints the usage and each flag, exit 0")
def test_effect_help() -> None:
    """Typed by hand: the usage line and the three flags' lines, on standard output, nothing on stderr."""
    root = H.fresh_consumer().root
    flags = (
        "  --reader       let a fresh reader judge the rules no pattern can see, on a subscription login\n"
        "  --transcripts  a folder of session transcripts, for the sessions whose transcript no log names\n"
        "  --since        count only what stands on that day or later\n"
    )
    usage = "[--reader] [--transcripts <dir>] [--since <YYYY-MM-DD>]\n"
    entry = H.run_gate("", args=["--help"], command=[H.sh, str(SCRIPTS / "effect-report.sh")], cwd=root)
    assert entry.code == 0 and not entry.stderr, entry
    assert entry.stdout == "usage: effect-report.sh " + usage + flags, entry.stdout
    shared_entry = H.run_gate(
        "", args=["-h"], command=[sys.executable, "-m", "constitution_layer_kit.effect"], cwd=root
    )
    assert shared_entry.code == 0 and not shared_entry.stderr, shared_entry
    assert shared_entry.stdout == "usage: python3 -m constitution_layer_kit.effect " + usage + flags


@item(30, "--since names the day from its first second: a commit made earlier that day is in the window")
def test_since_whole_day() -> None:
    """A change of the gate's dials, committed a moment before the run, on the run's own day. Git reads a bare
    date as that day at the run's clock time, which would leave the commit out; W5 counts it."""
    consumer = H.fresh_consumer()
    consumer.write_dials(own(severity="block"))
    consumer.commit()
    today = datetime.date.today().isoformat()
    found = effect_lines(consumer.root, {}, no_plugins(), "--since", today)
    assert "  W5 (pattern): 1 moment(s): 1 applied, 0 bypassed, 0 missed" in found, found


@item(31, "with --since, the headline counts only the sessions with an event in the window")
def test_since_sessions() -> None:
    """Two sessions of the project, one wholly before the window and one in it: the headline says one."""
    root = H.fresh_consumer().root
    before = [tr_turn("s31a", root, "2026-11-01T10:00:00.000Z", "old")]
    within = [tr_turn("s31b", root, "2026-11-03T10:00:00.000Z", "new")]
    found = effect_lines(root, {"s31a": before, "s31b": within}, no_plugins(), "--since", "2026-11-02")
    head = found[0]
    assert head.startswith("EFFECT: know-check: ") and head.endswith(
        " rule(s) over 1 session(s) since 2026-11-02, 0 transcript line(s) unread"
    ), head


SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=VALID,
    red=RED,
    red_finding=messages.l3_forbidden(NOTE_A, "notes-policy", PHRASE),
    territory=["docs/notes/**"],
    green=shared.governed_by("notes-policy"),
    claim=claim,
    judges_envelopes=False,
    noted=Write("docs/policies/loose-policy.md", NO_ENVELOPE),  # a policy with no id: the shared note N1.1
    note=(  # typed by hand
        "note: docs/policies/loose-policy.md lies in the root policy's territory but carries no readable id;"
        " it claims nothing until it does"
    ),
    outside="docs/notes/a.md is outside claimed territory",
    effect="effect-report.sh",
    effect_reader="W2",
)
