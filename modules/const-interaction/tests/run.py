#!/usr/bin/env python3
"""Fixtures of const-interaction: `python3 tests/run.py` from anywhere.

Needs git, Python 3.12+, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.
Exit 0 when every item is green, 2 otherwise.

Three entry points are driven: the shell gate through the shared items and its own, the
list-handles scan and the session-start printer through their own. The shell gate's red is
an `ask` verdict — exit 0, one JSON object asking the platform to prompt, the finding in its
reason — so its red→green pairs are written as assertions that read that reason, and the
shared items run with the subject's `ask` flag. The fixture consumer is the shared one; this
module resolves no policy and judges no envelope, so the shared items about the root policy
and about an unreadable envelope are left out and their numbers stay free.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MODULE_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))  # the runner only: no gate code ever edits the path

from const_gate import identity  # noqa: E402
from const_gate import messages as shared  # noqa: E402
from const_gate.model import Broken, Finding  # noqa: E402
from consumer import Consumer  # noqa: E402
from harness import (  # noqa: E402
    Assertion,
    Harness,
    Result,
    Write,
    ask_reason,
    bash_json,
    broken_first_line,
    event_json,
    expect,
    red_lines,
)
from interaction_gate import messages, start, tokens  # noqa: E402
from interaction_gate.model import DEFAULT_DESTRUCTIVE, Entry, Subcommand, Verbosity  # noqa: E402
from shared_items import PatternDial, Subject, shared_assertions  # noqa: E402

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
H = Harness(SCRIPTS, "check-destructive.sh", "check-destructive.py", start.GATE.namespace)
LISTS = Harness(SCRIPTS, "check-list-handles.sh", "check-list-handles.py", start.GATE.namespace)
SESSION = Harness(SCRIPTS, "session-start.sh", "session-start.py", start.GATE.namespace)

NAMESPACE = start.GATE.namespace
ENTRIES = len(DEFAULT_DESTRUCTIVE)
RULES = (SCRIPTS / "rules.txt").read_text(encoding="utf-8")


# a file name and a folder name of over 80 characters holding a line break and a backslash: the real names,
# and the text the gate shows for them, typed by hand — the whole name, since a path is what the reader opens
WEIRD = "docs/notes/w\nx\\y" + "z" * 80 + ".md"
WEIRD_SHOWN = "docs/notes/w\\nx\\\\y" + "z" * 80 + ".md"
WEIRD_DIR = "w\nx\\y" + "d" * 80
WEIRD_DIR_SHOWN = "w\\nx\\\\y" + "d" * 80


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
    if files:
        consumer.commit()
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
    """The shell gate on a prepared consumer: the action's text is the command."""
    assert isinstance(action, Write)
    root = prepared(dials_patch, raw_dials, files, remove)
    return H.run_gate(bash_json(root, action.text), env=env), root


def command(text: str) -> Write:
    """A shell command as the subject's action: the text is the command; the target matters only to
    the shared items that write a file beside it."""
    return Write("docs/notes/command.md", text)


def d1(text: str, entry_index: int, matched: str, subcommand: str | None = None) -> Finding:
    entry = DEFAULT_DESTRUCTIVE[entry_index]
    return messages.d1_destructive(entry, Subcommand((), subcommand or text), matched)


def asked(text: str, finding: Finding, subcommands: int = 1, **kwargs: object) -> tuple[bool, str]:
    """The red half of the gate: exit 0, one JSON object asking, the one finding and the count in
    its reason and nothing else."""
    result, _ = gate_on(command(text), **kwargs)  # type: ignore[arg-type]
    reason = ask_reason(result)
    if reason is None:
        return False, f"no ask verdict; exit {result.code}: {result.stdout[:300]}{result.stderr[:300]}"
    wanted = [f"RED: {finding.headline}", messages.f9_count_command(1, subcommands)]
    ok = finding.render() in reason and red_lines(reason) == wanted and result.stdout.count("\n") == 1
    return ok, f"asked: {finding.headline}" if ok else f"asked with a different reason:\n{reason}"


def passed(text: str, subcommands: int = 1, entries: int = ENTRIES, **kwargs: object) -> tuple[bool, str]:
    result, _ = gate_on(command(text), **kwargs)  # type: ignore[arg-type]
    line = shared.g1_green_event(messages.g1_command_passed(entries, subcommands))
    return expect(result, 0, line, "stdout")


def pair(
    red: Callable[[], tuple[bool, str]], green: Callable[[], tuple[bool, str]]
) -> Callable[[], tuple[bool, str]]:
    """A red→green item of the shell gate: red must ask, green must pass."""

    def check() -> tuple[bool, str]:
        ok_red, said_red = red()
        if not ok_red:
            return False, f"red half: {said_red}"
        ok_green, said_green = green()
        if not ok_green:
            return False, f"green half: {said_green}"
        return True, f"{said_red}; green: {said_green}"

    return check


def broken(result: Result, failure: Broken, closing: str = shared.c11_broken_count()) -> tuple[bool, str]:
    ok, evidence = broken_first_line(result, failure.render())
    counted = closing in result.stderr
    return ok and counted, evidence if counted else f"no count line after: {evidence}"


def all_of(*checks: tuple[bool, str]) -> tuple[bool, str]:
    failed = [said for ok, said in checks if not ok]
    return (not failed), "; ".join(said for _, said in checks) if not failed else " | ".join(failed)


# ---------------------------------------------------------------- the shell gate: red→green pairs

FORCE_PUSH = "git -C . push --force origin main"


def t1() -> tuple[bool, str]:
    return pair(
        lambda: asked(FORCE_PUSH, d1(FORCE_PUSH, 0, "--force")),
        lambda: passed("git push --force-with-lease origin main"),
    )()


def t2() -> tuple[bool, str]:
    text = "cd build && rm -rf dist; ls"
    return pair(
        lambda: asked(text, d1(text, 13, "-r", "rm -rf dist"), subcommands=3),
        lambda: passed("cd build && rm dist.log; ls", subcommands=3),
    )()


def t3() -> tuple[bool, str]:
    text = 'bash -c "git reset --hard HEAD~1"'
    return pair(
        lambda: asked(text, d1(text, 1, "--hard", "git reset --hard HEAD~1"), subcommands=2),
        lambda: passed('bash -c "git reset --soft HEAD~1"', subcommands=2),
    )()


def t4() -> tuple[bool, str]:
    text = "echo $(git rebase main)"
    return pair(
        lambda: asked(text, d1(text, 8, "", "git rebase main"), subcommands=2),
        lambda: passed("echo $(git log -1)", subcommands=2),
    )()


def t5() -> tuple[bool, str]:
    """Wrappers, assignments, a program path, git's global options: none hides the verb."""
    return all_of(
        asked("sudo /bin/rm -r /tmp/x", d1("", 13, "-r", "sudo /bin/rm -r /tmp/x")),
        asked("git -c push.default=current push -f", d1("", 0, "-f", "git -c push.default=current push -f")),
        asked("FOO=1 timeout 5 git stash drop", d1("", 6, "", "FOO=1 timeout 5 git stash drop")),
        asked("nohup git filter-repo --path x", d1("", 10, "", "nohup git filter-repo --path x")),
        asked("git gc --prune=now", d1("git gc --prune=now", 12, "--prune=now")),
        asked("env -i git push -f", d1("", 0, "-f", "env -i git push -f")),
        asked("sudo -k git push -f", d1("", 0, "-f", "sudo -k git push -f")),
        asked("sudo --user root git push -f", d1("", 0, "-f", "sudo --user root git push -f")),
        asked("/usr/bin/env git push -f", d1("", 0, "-f", "/usr/bin/env git push -f")),
        asked('bash -lc "git push -f"', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked("exec git push -f", d1("", 0, "-f", "exec git push -f")),
        asked("if true; then git push -f; fi", d1("", 0, "-f", "then git push -f"), subcommands=2),
        asked("git push -f 2>&1", d1("", 0, "-f", "git push -f 2>&1")),
    )


def t6() -> tuple[bool, str]:
    """What the list leaves out passes and is said so in the install note: a heredoc body, the
    argument form, an amend, a plain push, a flag after `--`, one file removed."""
    return all_of(
        passed("cat <<EOF\nrm -rf /\nEOF\n"),
        passed("git checkout -- ."),
        passed("git commit --amend --no-edit"),
        passed("git push origin main"),
        passed("git push -- --force"),
        passed("rm build.log"),
        passed("git branch -d old"),
        asked('echo "a<<EOF"\ngit push -f', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked('echo "a<<EOF"\ngit push -f\nEOF', d1("", 0, "-f", "git push -f"), subcommands=3),
        asked("cat <<EOF\ngit push -f", d1("", 0, "-f", "git push -f"), subcommands=2),
        passed(
            "git commit -q -F - <<'EOF'\nthe branch fix; git branch -f gated\nEOF",
            subcommands=1,
        ),
        passed(
            "git commit -m \"$(cat <<'EOF'\nthe branch fix; git branch -f gated\nEOF\n)\"",
            subcommands=2,
        ),
        asked('env -S "git push -f"', d1("", 0, "-f", "git push -f")),
        asked('env -i -S "git push -f"', d1("", 0, "-f", "git push -f")),
        asked('env --split-string="git push -f"', d1("", 0, "-f", "git push -f")),
        asked('env -S "git push" -f', d1("", 0, "-f", "git push -f")),
        asked("env -S'git push -f'", d1("", 0, "-f", "git push -f")),
        asked("env -iS 'git push -f'", d1("", 0, "-f", "git push -f")),
        asked("env -uSHELL git push -f", d1("", 0, "-f", "env -uSHELL git push -f")),
        asked("env -iu SHELL git push -f", d1("", 0, "-f", "env -iu SHELL git push -f")),
        asked("env -P /usr/bin git push -f", d1("", 0, "-f", "env -P /usr/bin git push -f")),
        asked("sudo -iu root git push -f", d1("", 0, "-f", "sudo -iu root git push -f")),
        asked("env -iu SHELL -S 'git push -f'", d1("", 0, "-f", "git push -f")),
        asked("sudo -T 5 git push -f", d1("", 0, "-f", "sudo -T 5 git push -f")),
        asked("sudo -R /tmp git push -f", d1("", 0, "-f", "sudo -R /tmp git push -f")),
        asked("doas -a x git push -f", d1("", 0, "-f", "doas -a x git push -f")),
        asked("xargs -J % git push -f", d1("", 0, "-f", "xargs -J % git push -f")),
        asked("env -L user git push -f", d1("", 0, "-f", "env -L user git push -f")),
        asked("env -U user git push -f", d1("", 0, "-f", "env -U user git push -f")),
        asked(
            "sudo --command-timeout 5 git push -f", d1("", 0, "-f", "sudo --command-timeout 5 git push -f")
        ),
        asked("sudo --chroot /tmp git push -f", d1("", 0, "-f", "sudo --chroot /tmp git push -f")),
        asked("xargs --max-chars 10 git push -f", d1("", 0, "-f", "xargs --max-chars 10 git push -f")),
        asked("xargs -R 2 git push -f", d1("", 0, "-f", "xargs -R 2 git push -f")),
        asked("xargs -S 512 git push -f", d1("", 0, "-f", "xargs -S 512 git push -f")),
        asked("xargs --max-lines git push -f", d1("", 0, "-f", "xargs --max-lines git push -f")),
        asked("xargs --eof git push -f", d1("", 0, "-f", "xargs --eof git push -f")),
        asked(
            "xargs --process-slot-var N git push -f",
            d1("", 0, "-f", "xargs --process-slot-var N git push -f"),
        ),
        asked("stdbuf --output L git push -f", d1("", 0, "-f", "stdbuf --output L git push -f")),
        asked("sudo --login git push -f", d1("", 0, "-f", "sudo --login git push -f")),
        asked("nice -- git push -f", d1("", 0, "-f", "nice -- git push -f")),
        asked(
            "sudo --login-class staff git push -f", d1("", 0, "-f", "sudo --login-class staff git push -f")
        ),
        asked("sudo --auth-type pam git push -f", d1("", 0, "-f", "sudo --auth-type pam git push -f")),
        asked('bash --rcfile /dev/null -c "git push -f"', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked('bash -c -- "git push -f"', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked('echo $(echo ")"; git push -f)', d1("", 0, "-f", "git push -f"), subcommands=3),
        asked('echo "$(echo ")"; git push -f)"', d1("", 0, "-f", "git push -f"), subcommands=3),
        asked('echo "$(echo "$(echo ")")"; git push -f)"', d1("", 0, "-f", "git push -f"), subcommands=4),
        asked('bash --init-file /dev/null -c "git push -f"', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked("echo $(echo $(date)) $(git push -f)", d1("", 0, "-f", "git push -f"), subcommands=4),
        asked("sudo -c staff git push -f", d1("", 0, "-f", "sudo -c staff git push -f")),
        asked("sudo -a pam git push -f", d1("", 0, "-f", "sudo -a pam git push -f")),
        asked('env -S "git push -f \'x"', d1("", 0, "-f", "git push -f ''\"'\"'x'")),
        asked("bash -O extglob -c 'git push -f'", d1("", 0, "-f", "git push -f"), subcommands=2),
        asked('env -S "echo \'x" ; git push -f', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked("bash +o posix -c 'git push -f'", d1("", 0, "-f", "git push -f"), subcommands=2),
        asked('bash -o pipefail -c "git push -f"', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked('bash -eo pipefail -c "git push -f"', d1("", 0, "-f", "git push -f"), subcommands=2),
        asked("echo '$(<<EOF'\ngit push -f\nEOF", d1("", 0, "-f", "git push -f"), subcommands=4),
        asked('echo "$(date) a<<EOF"\ngit push -f\nEOF', d1("", 0, "-f", "git push -f"), subcommands=4),
    )


def t7() -> tuple[bool, str]:
    """The dial: an empty list gates nothing and says so; an own entry with words alone; a short
    flag inside a cluster; a long flag by equality only."""
    result, _ = gate_on(command(FORCE_PUSH), dials_patch=own(destructive=[]))
    empty = expect(result, 0, shared.g1_green_event(messages.g1_nothing_gated()), "stdout")
    teach, alternative = "a dropped database is gone", "dump it first"
    with_own = own(destructive=[{"command": ["dropdb"], "teach": teach, "alternative": alternative}])
    own_hit = asked(
        "dropdb prod",
        messages.d1_destructive(
            Entry(("dropdb",), (), teach, alternative), Subcommand((), "dropdb prod"), ""
        ),
        dials_patch=with_own,
    )
    own_miss = passed(FORCE_PUSH, entries=1, dials_patch=with_own)
    cluster = asked("git clean -xdf", d1("", 4, "-f", "git clean -xdf"))
    equality = passed("git push --force-with-lease=main origin main")
    two = own(
        destructive=[
            {"command": ["dropdb"], "teach": "first", "alternative": "a"},
            {"command": ["dropdb"], "teach": "second", "alternative": "b"},
        ]
    )
    first_only = asked(
        "dropdb prod",
        messages.d1_destructive(Entry(("dropdb",), (), "first", "a"), Subcommand((), "dropdb prod"), ""),
        dials_patch=two,
    )
    return all_of(empty, own_hit, own_miss, cluster, equality, first_only)


def t8() -> tuple[bool, str]:
    """Severity warn: the finding reported as context and the command let through."""
    result, _ = gate_on(command(FORCE_PUSH), dials_patch=own(severity="warn"))
    if result.code != 0:
        return False, f"warn must let the command through; exit {result.code}: {result.stderr}"
    try:
        answer = json.loads(result.stdout)
        context = answer["hookSpecificOutput"]["additionalContext"]
    except (ValueError, KeyError, TypeError):
        return False, f"warn must answer with one JSON object; got: {result.stdout[:300]}"
    finding = d1(FORCE_PUSH, 0, "--force")
    ok = (
        "permissionDecision" not in answer["hookSpecificOutput"]
        and finding.render() in context
        and shared.w1_warn_note() in context
        and answer["systemMessage"] == shared.w1_warn_system(finding.headline)
    )
    return (
        ok,
        "exit 0, no decision, finding in additionalContext and systemMessage" if ok else f"bad: {answer}",
    )


def t9() -> tuple[bool, str]:
    """The scan explains a command: the finding and the tail typed by hand; no command is a
    visible skip; --command without --scan is a misinvocation."""
    root = prepared()
    red = H.run_gate("", args=["--scan", str(root), "--command", "rm -rf build"])
    tail = "RED: 1 finding(s) — 1 command examined: 1 subcommand(s) against 14 entries"
    red_ok = red.code == 2 and red_lines(red.stdout) == [
        "RED: destructive command: 'rm -rf build' matches the entry rm with -r",
        tail,
    ]
    green = H.run_gate("", args=["--scan", str(root), "--command", "ls -la"])
    green_ok = expect(
        green, 0, "GREEN: const-interaction: 1 command examined: 1 subcommand(s) against 14 entries", "stdout"
    )
    skip = H.run_gate("", args=["--scan", str(root)])
    skip_ok = expect(
        skip,
        0,
        "GREEN: const-interaction: 0 documents examined — no command given: run the scan with --command"
        " '<text>' to see what the dial does to it",
        "stdout",
    )
    mis = H.run_gate("", args=["--command", "ls"])
    mis_ok = expect(mis, 1, "BROKEN: misinvocation: --command applies to --scan", "stderr")
    return all_of((red_ok, f"scan red: {red.stdout.strip()[:120]}"), green_ok, skip_ok, mis_ok)


def t10() -> tuple[bool, str]:
    """This module's C5 lines typed by hand, each exit 1."""
    prefix = "BROKEN: constitution.yaml: "
    cases: list[tuple[dict[str, object], str]] = [
        (
            own(marker="x"),
            prefix + "const-interaction.marker is no dial of this module — fix: a misspelt dial would be"
            " ignored in silence, so none is: write one of severity, log_dir, destructive, territories,"
            " handles, boundary_examples, verbosity",
        ),
        (
            own(destructive="rm"),
            prefix + "const-interaction.destructive must be a list of entries — fix: write one entry per"
            ' "- " item with the fields command (a list of words), flags (a list, optional), teach and'
            " alternative (texts); leave the key out for the default list; an empty list gates nothing and"
            " says so at session start",
        ),
        (
            own(destructive=["rm -rf"]),
            prefix + "const-interaction.destructive entry 1: it is not a mapping — fix: write the entry as"
            " command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard to reverse>,"
            " alternative: <the reversible way>",
        ),
        (
            own(destructive=[{"command": ["rm"], "teach": "t", "alternative": "a", "why": "x"}]),
            prefix + "const-interaction.destructive entry 1: 'why' is no field of an entry — fix: write the"
            " entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard to"
            " reverse>, alternative: <the reversible way>",
        ),
        (  # a line break in the key is shown escaped: the line stays one line
            own(destructive=[{"command": ["rm"], "teach": "t", "alternative": "a", "a\nb": "x"}]),
            prefix + "const-interaction.destructive entry 1: 'a\\nb' is no field of an entry — fix: write the"
            " entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard to"
            " reverse>, alternative: <the reversible way>",
        ),
        (
            own(destructive=[{"command": ["git push"], "teach": "t", "alternative": "a"}]),
            prefix + "const-interaction.destructive entry 1: command must be a non-empty list of words — fix:"
            " write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard"
            " to reverse>, alternative: <the reversible way>",
        ),
        (
            own(destructive=[{"command": ["rm"], "flags": ["rf"], "teach": "t", "alternative": "a"}]),
            prefix
            + "const-interaction.destructive entry 1: flags must be a list of flags, each starting with"
            " '-' — fix: write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the"
            " act is hard to reverse>, alternative: <the reversible way>",
        ),
        (
            own(destructive=[{"command": ["rm"], "alternative": "a"}]),
            prefix + "const-interaction.destructive entry 1: teach must be a non-empty text — fix: write the"
            " entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard to"
            " reverse>, alternative: <the reversible way>",
        ),
        (
            own(handles=[]),
            prefix + "const-interaction.handles must be a non-empty list of regular expressions — fix: write"
            ' the handle forms a list item may open with, one per line under "- " in single quotes, or leave'
            " the key out for the defaults; an empty list would find every list red",
        ),
        (
            own(handles=["("]),
            prefix + "const-interaction.handles holds '(', which is not a regular expression (missing ),"
            " unterminated subpattern at position 0) — fix: repair the pattern; Python's re syntax, matched"
            " at the start of the item's text",
        ),
        (  # a pattern only points: 102 characters, cut at 80 with the cut said, its backslash doubled; the
            # compiler's words quote a character of it and keep their own backslash, doubled
            own(handles=["\\q" + "x" * 100]),
            prefix
            + "const-interaction.handles holds '\\\\q"
            + "x" * 78
            + "… [102 characters]', which is not a"
            " regular expression (bad escape \\\\q at position 0) — fix: repair the pattern; Python's re"
            " syntax, matched at the start of the item's text",
        ),
        (
            own(territories=[]),
            prefix + "const-interaction.territories must be a non-empty list of path patterns — fix: write"
            ' the patterns of the documents to scan for lists, one per line under "- ", or leave the key out'
            " to cover every Markdown file; an empty list would examine nothing in silence",
        ),
        (
            own(verbosity="terse"),
            prefix
            + "const-interaction.verbosity must be one of: triggered — fix: write verbosity: triggered — the"
            " one value today: assumption and restatement lines appear only when triggered — or leave the key"
            " out for it",
        ),
        (
            own(boundary_examples=[{"violates": "x"}]),
            prefix
            + "const-interaction.boundary_examples must be a list of pairs {violates: <text>, complies:"
            ' <text>} — fix: write one pair per "- " item with exactly those two fields, or leave the key'
            " out",
        ),
    ]
    checks = []
    for patch, line in cases:
        result, _ = gate_on(command("ls"), dials_patch=patch)
        ok, evidence = broken_first_line(result, line)
        checks.append((ok and shared.c11_broken_count() in result.stderr, evidence))
    # the verbosity fix is prose that says "the one value today": a second value fails here, and
    # points at that prose
    one_value = len(Verbosity) == 1 and f"write verbosity: {Verbosity.TRIGGERED.value} — the one value" in (
        messages.c5_verbosity().fix
    )
    checks.append((one_value, "one verbosity value, and its fix says so" if one_value else "a second value"))
    return all_of(*checks)


def t11() -> tuple[bool, str]:
    """An event the gate is not wired to, and a shell event without a command, typed by hand."""
    root = prepared()
    write = H.run_gate(event_json(root, Write("docs/notes/a.md", "x")))
    write_ok = broken_first_line(
        write,
        "BROKEN: hook input names the event 'PreToolUse' on tool 'Write', which this gate is not wired to"
        " — fix: wire the gate to PreToolUse with the matcher Bash, as the plugin's hooks file does; to see"
        " what the dial does to a command by hand run it with --scan --command '<text>'",
    )
    payload = json.dumps(
        {"hook_event_name": "PreToolUse", "cwd": str(root), "tool_name": "Bash", "tool_input": {}}
    )
    no_command = H.run_gate(payload)
    no_command_ok = broken_first_line(
        no_command,
        "BROKEN: hook input cannot be used (a Bash event must carry a string tool_input.command) — fix: as a"
        " hook this script reads one tool event, a JSON object, on stdin; to check a repository by hand run"
        " it with --scan [<dir>]",
    )
    odd = H.run_gate(
        json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(root),
                "tool_name": "N\nx\\y" + "e" * 90,
                "tool_input": {},
            }
        )
    )
    odd_ok = broken_first_line(  # names only point: cut at 80 characters with the cut said, then escaped
        odd,
        "BROKEN: hook input names the event 'PreToolUse' on tool 'N\\nx\\\\y"
        + "e" * 75
        + "… [95 characters]',"
        " which this gate is not wired to — fix: wire the gate to PreToolUse with the matcher Bash, as the"
        " plugin's hooks file does; to see what the dial does to a command by hand run it with --scan"
        " --command '<text>'",
    )
    odd_event = H.run_gate(
        json.dumps(
            {
                "hook_event_name": "N\nx\\y" + "e" * 90,
                "cwd": str(root),
                "tool_name": "Bash",
                "tool_input": {"command": "ls"},
            }
        )
    )
    odd_event_ok = broken_first_line(  # the event name only points: cut at 80, the cut said, then escaped
        odd_event,
        "BROKEN: hook input names the event 'N\\nx\\\\y" + "e" * 75 + "… [95 characters]' on tool 'Bash',"
        " which this gate is not wired to — fix: wire the gate to PreToolUse with the matcher Bash, as the"
        " plugin's hooks file does; to see what the dial does to a command by hand run it with --scan"
        " --command '<text>'",
    )
    return all_of(write_ok, no_command_ok, odd_ok, odd_event_ok)


def t12() -> tuple[bool, str]:
    """Golden lines: D1 for the force push typed whole against a fresh run, so a why emptied or a
    word lost inside the message function is red."""
    result, _ = gate_on(command(FORCE_PUSH))
    reason = ask_reason(result) or ""
    wanted = (
        "RED: destructive command: 'git -C . push --force origin main' matches the entry git push with"
        " --force\n"
        "  why: a forced push rewrites the branch on the remote: every other clone of it diverges, and the"
        " commits it replaced are unreachable there\n"
        "  fix: push with --force-with-lease, which refuses when the remote moved, or push a new branch and"
        " open a pull request; to run it as written, confirm at the prompt — where no prompt can be shown,"
        " get the user's yes in chat and run it again, one yes per command; to stop gating it, remove the"
        " entry from const-interaction.destructive in constitution.yaml\n"
        "RED: 1 finding(s) — 1 command examined (1 subcommand(s))"
    )
    ok = reason == wanted
    teach = (
        "line one\nline two \\ " + "t" * 100
    )  # the entry's teaching text and alternative: lines, a backslash,
    alternative = (
        "alt one\nalt \\ " + "a" * 100
    )  # over 80 characters — a reader acts on them, so they stand whole
    word = "wipe\\x" + "k" * 90  # a command word of 96 characters and a flag of 95, each with a backslash
    flag = "--f\\g" + "m" * 90
    entry = {"command": [word], "flags": [flag], "teach": teach, "alternative": alternative}
    odd, _ = gate_on(
        command("'" + word + "' '" + flag + "' " + "q" * 100), dials_patch=own(destructive=[entry])
    )
    odd_reason = ask_reason(odd) or ""
    odd_wanted = (
        "RED: destructive command: ''wipe\\\\x" + "k" * 73 + "… [297 characters]' matches the entry"
        " wipe\\\\x" + "k" * 74 + "… [96 characters] with --f\\\\g" + "m" * 75 + "… [95 characters]\n"
        "  why: line one\\nline two \\\\ " + "t" * 100 + "\n"
        "  fix: alt one\\nalt \\\\ " + "a" * 100 + "; to run it as written, confirm at the prompt — where no"
        " prompt can be shown, get the user's yes in chat and run it again, one yes per command; to stop"
        " gating it, remove the entry from const-interaction.destructive in constitution.yaml\n"
        "RED: 1 finding(s) — 1 command examined (1 subcommand(s))"
    )
    odd_ok = odd_reason == odd_wanted
    return all_of(
        (ok, "D1 typed whole matches" if ok else f"differs:\n{reason}"),
        (  # the command, words and flag only point: cut at 80, then escaped; teach and alternative whole
            odd_ok,
            "D1 with a backslash, a break and long texts" if odd_ok else f"differs:\n{odd_reason}",
        ),
    )


def t13() -> tuple[bool, str]:
    """The tokeniser's readings, each typed by hand."""
    readings = {
        "git -C . push --force origin main": [("git", "push", "--force", "origin", "main")],
        "a && b || c; d | e |& f & g\nh": [("a",), ("b",), ("c",), ("d",), ("e",), ("f",), ("g",), ("h",)],
        'echo "a && b"': [("echo", "a && b")],
        "echo `git rebase x`": [("git", "rebase", "x"), ("echo", "`git", "rebase", "x`")],
        "env -i FOO=1 nice -n 5 rm -r x": [("rm", "-r", "x")],
        "git 'push' --force": [("git", "push", "--force")],
        "git --git-dir=.git push -f": [("git", "push", "-f")],
        "git --git-dir .git --no-pager push -f": [("git", "push", "-f")],
        'sh -c "rm -r x" && echo done': [("sh", "-c", "rm -r x"), ("rm", "-r", "x"), ("echo", "done")],
        "echo 'unbalanced && rm -r x": [("echo", "'unbalanced", "&&", "rm", "-r", "x")],
        "(cd x && rm -r y)": [("cd", "x"), ("rm", "-r", "y")],
        "sudo -u root rm -r x": [("rm", "-r", "x")],
        "git push \\\n -f": [("git", "push", "-f")],
        "ls &> /dev/null; rm -r x": [("ls", "&>", "/dev/null"), ("rm", "-r", "x")],
        "{ git push -f; }": [("git", "push", "-f")],
        "FOO=1": [],
    }
    wrong = {
        text: [s.words for s in tokens.split(text)]
        for text, words in readings.items()
        if [s.words for s in tokens.split(text)] != words
    }
    return (not wrong), f"{len(readings)} readings hold" if not wrong else f"wrong: {wrong}"


# ---------------------------------------------------------------- the list-handles scan

PLAIN = "# T\n\n- one item\n- two items\n"
HANDLED = "# T\n\n- 1. one\n- 2. two\n\n- R1 a\n- R2 b\n\n- **Label:** a\n- `code` b\n- [link](x) c\n"


def lists_scan(files: dict[str, str], dials_patch: dict[str, object] | None = None) -> Result:
    root = prepared(dials_patch, files=files)
    return LISTS.run_gate("", args=["--scan", str(root)])


def t20() -> tuple[bool, str]:
    """red→green: a plain list is red with L1 typed whole; the same document with handles is green."""
    red = lists_scan({"docs/notes/a.md": PLAIN})
    wanted = (
        "RED: docs/notes/a.md:3: list item without a handle — one item\n"
        "  why: an item with no stable handle cannot be cited without quoting it, so a reader cannot point"
        " at one\n"
        "  fix: open the item with a handle — a number, a letter or a short key such as R1 or Q-a — or add"
        " the form the document uses to const-interaction.handles in constitution.yaml, or take the document"
        " out of const-interaction.territories by a negated pattern\n"
        "RED: 1 finding(s) — 4 document(s) examined for lists with 6 handle form(s), 4 Markdown file(s)"
        " scanned"
    )
    red_ok = red.code == 2 and red.stdout.strip() == wanted
    handles = [r"[0-9]+\.", r"[A-Z]+[0-9]+\b", r"\*\*[^*]+\*\*", r"`[^`]+`", r"\[[^\]]+\]\("]
    green = lists_scan({"docs/notes/a.md": HANDLED}, dials_patch=own(handles=handles))
    green_ok = expect(
        green,
        0,
        "GREEN: const-interaction: 4 document(s) examined for lists with 5 handle form(s), 4 Markdown"
        " file(s) scanned",
        "stdout",
    )
    odd = lists_scan({WEIRD: "# T\n\n- one\\two " + "y" * 100 + "\n- two\n"})
    odd_ok = (  # the path whole, escaped, and the item cut at 80 characters with the cut said, then escaped
        odd.code == 2
        and red_lines(odd.stdout)[0]
        == "RED: "
        + WEIRD_SHOWN
        + ":3: list item without a handle — one\\\\two "
        + "y" * 72
        + "… [108 characters]"
    )
    return all_of(
        (red_ok, "L1 typed whole matches" if red_ok else f"differs (exit {red.code}):\n{red.stdout}"),
        green_ok,
        (
            odd_ok,
            "a long path whole, a long item cut" if odd_ok else f"differs (exit {odd.code}):\n{odd.stdout}",
        ),
    )


def t21() -> tuple[bool, str]:
    """What is not a finding: a list in a fence, a one-item list, a nested list under a handled
    item, an anchor before the handle, a numbered list, a fence closed by a shorter one; and what
    is: the first item only, and a loose list — blank lines between items — as one list."""
    text = (
        "# T\n\n```\n- x\n- y\n```\n\n- only one\n\nA paragraph ends the list.\n\n"
        "- 1. a\n  - nested\n  - nested\n- 2. b\n\n"
        '- <a id="p1"></a>**1.** a\n- **2.** b\n\n'
        "1. a\n2. b\n\n"
        "- plain one\n- plain two\n- 3. handled\n"
    )
    result = lists_scan({"docs/notes/a.md": text})
    ok = (
        result.code == 2
        and red_lines(result.stdout)[0] == ("RED: docs/notes/a.md:23: list item without a handle — plain one")
        and len(red_lines(result.stdout)) == 2
    )
    loose = lists_scan({"docs/notes/b.md": "# T\n\n- loose one\n\n- loose two\n"})
    loose_ok = expect(loose, 2, "RED: docs/notes/b.md:3: list item without a handle — loose one", "stdout")
    fence = lists_scan({"docs/notes/c.md": "# T\n\n````\n- x\n- y\n```\n- z\n- w\n````\n"})
    fence_ok = expect(fence, 0, "GREEN: const-interaction: 4 document(s) examined", "stdout")
    return all_of(
        (ok, "one finding, the first plain item" if ok else f"exit {result.code}: {result.stdout}"),
        loose_ok,
        fence_ok,
    )


def t22() -> tuple[bool, str]:
    """Territories: a negated pattern takes a document out; the default covers every Markdown file."""
    out = lists_scan({"docs/notes/a.md": PLAIN}, dials_patch=own(territories=["*.md", "!docs/notes/**"]))
    out_ok = expect(
        out,
        0,
        "GREEN: const-interaction: 3 document(s) examined for lists with 6 handle form(s), 4 Markdown"
        " file(s) scanned",
        "stdout",
    )
    top = lists_scan({"README.md": PLAIN})
    top_ok = expect(top, 2, "RED: README.md:3: list item without a handle — one item", "stdout")
    return all_of(out_ok, top_ok)


def t23() -> tuple[bool, str]:
    """The scan's entry point as a hook is its own C12, typed by hand; a misinvocation exits 1."""
    root = prepared()
    hook = LISTS.run_gate(bash_json(root, "ls"))
    hook_ok = broken_first_line(
        hook,
        "BROKEN: this check has no hook mode: it scans a tree and judges no single write — fix: run it with"
        " --scan [<dir>]; the plugin wires it to no event",
    )
    mis = LISTS.run_gate("", args=["--bogus"])
    return all_of(hook_ok, expect(mis, 1, "BROKEN: misinvocation:", "stderr"))


# ---------------------------------------------------------------- the session-start printer


def session_json(root: Path) -> str:
    return json.dumps(
        {
            "hook_event_name": "SessionStart",
            "session_id": "fixture-session",
            "cwd": str(root),
            "source": "startup",
        }
    )


def t30() -> tuple[bool, str]:
    """The rules first, whole; then nothing when the default list gates; the zero line when the
    dial is empty; the project's pairs numbered."""
    root = prepared()
    plain = SESSION.run_gate(session_json(root))
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    verbosity = (
        "const-interaction: verbosity is triggered — the assumption block and the restatement appear only"
        " when triggered, never as an empty ritual\n"
    )
    stated_verbosity = re.search(r"one line of ([0-9,]+) characters naming the value", module_doc)
    plain_ok = (
        plain.code == 0
        and plain.stdout == RULES + verbosity
        and plain.stderr == ""
        and stated_verbosity is not None
        and int(stated_verbosity.group(1).replace(",", "")) == len(verbosity) - 1
    )
    empty_root = prepared(own(destructive=[]))
    empty = SESSION.run_gate(session_json(empty_root))
    zero = (
        "const-interaction: no command is gated — const-interaction.destructive is an empty list in"
        " constitution.yaml"
    )
    match = re.search(r"one line of ([0-9,]+) characters saying that no command is gated", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    empty_ok = empty.code == 0 and empty.stdout == RULES + verbosity + zero + "\n" and stated == len(zero)
    pairs_root = prepared(own(boundary_examples=[{"violates": "an essay", "complies": "the word"}]))
    pairs = SESSION.run_gate(session_json(pairs_root))
    pairs_ok = pairs.stdout == RULES + verbosity + (
        "Boundary examples of this project (const-interaction.boundary_examples), each violates / complies:\n"
        "1. an essay / the word\n"
    )
    long_pair = {"violates": "a\nb \\ " + "v" * 100, "complies": "c\\d\r\n" + "w" * 100}
    long_root = prepared(own(boundary_examples=[long_pair]))
    long_pairs = SESSION.run_gate(session_json(long_root))
    long_ok = (
        long_pairs.stdout
        == RULES
        + verbosity
        + (  # the example is the content: whole, escaped, one line
            "Boundary examples of this project (const-interaction.boundary_examples), each violates /"
            " complies:\n"
            "1. a\\nb \\\\ " + "v" * 100 + " / c\\\\d\\r\\n" + "w" * 100 + "\n"
        )
    )
    return all_of(
        (
            long_ok,
            "a pair with breaks, a backslash and 100 characters, whole"
            if long_ok
            else f"got: {long_pairs.stdout[-400:]}",
        ),
        (
            plain_ok,
            f"rules and the verbosity line, {len(RULES)} rule characters"
            if plain_ok
            else f"got: {plain.stdout[-200:]}{plain.stderr}",
        ),
        (empty_ok, "zero line after the rules" if empty_ok else f"got: {empty.stdout[-300:]}"),
        (pairs_ok, "pairs numbered" if pairs_ok else f"got: {pairs.stdout[-300:]}"),
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


def t31() -> tuple[bool, str]:
    """No dials file and no repository (roots and folders whose names hold `:` too), the first also from a
    subfolder of the root: the shared skips said in the module's words; malformed dials:
    exit 1 with the shared C4 first on stderr and the rules still on stdout; an argument: exit 1."""
    root = colon_root()
    no_dials = SESSION.run_gate(session_json(root))
    no_dials_line = (
        f"const-interaction: no constitution.yaml in {root} — the destructive-command gate examines nothing"
        " there until the file exists (an empty mapping, {} is enough for the default list)"
    ).replace("{} is", "{}, is")
    verbosity = (
        "const-interaction: verbosity is triggered — the assumption block and the restatement appear only"
        " when triggered, never as an empty ritual\n"
    )
    no_dials_ok = no_dials.code == 0 and no_dials.stdout == RULES + verbosity + no_dials_line + "\n"
    (root / "sub").mkdir()
    from_sub = SESSION.run_gate(session_json(root / "sub"))
    from_sub_ok = from_sub.code == 0 and from_sub.stdout == RULES + verbosity + no_dials_line + "\n"
    loose = colon_dir()
    no_repo = SESSION.run_gate(session_json(loose), env={"GIT_CEILING_DIRECTORIES": str(loose.parent)})
    no_repo_line = (
        f"const-interaction: {loose} is not inside a git repository — the destructive-command gate examines"
        " nothing there"
    )
    no_repo_ok = no_repo.code == 0 and no_repo.stdout == RULES + verbosity + no_repo_line + "\n"
    bad_root = prepared(raw_dials="root-policy: [\n")
    bad = SESSION.run_gate(session_json(bad_root))
    bad_ok = (
        bad.code == 1
        and bad.stdout == RULES
        and bad.stderr.startswith("BROKEN: constitution.yaml is not valid YAML")
        and "BROKEN: the session-start line could not be printed — the gate's state is unknown" in bad.stderr
    )
    arg = SESSION.run_gate(session_json(root), args=["--scan"])
    arg_ok = arg.code == 1 and "BROKEN: misinvocation: unexpected argument --scan" in arg.stderr
    weird_parent = H.scratch_dir()
    weird_root = Consumer(weird_parent / WEIRD_DIR).build().root  # over 80 characters, a break, a backslash
    (weird_root / "constitution.yaml").unlink()
    weird_no_dials = SESSION.run_gate(session_json(weird_root))
    weird_loose = weird_parent / ("l" + WEIRD_DIR)
    weird_loose.mkdir()
    weird_no_repo = SESSION.run_gate(
        session_json(weird_loose), env={"GIT_CEILING_DIRECTORIES": str(weird_parent)}
    )
    weird_dials_ok = weird_no_dials.stdout == RULES + verbosity + (
        f"const-interaction: no constitution.yaml in {weird_parent}/" + WEIRD_DIR_SHOWN + " — the"
        " destructive-command gate examines nothing there until the file exists (an empty mapping, {}, is"
        " enough for the default list)\n"
    )
    weird_repo_ok = weird_no_repo.stdout == RULES + verbosity + (
        f"const-interaction: {weird_parent}/l" + WEIRD_DIR_SHOWN + " is not inside a git repository — the"
        " destructive-command gate examines nothing there\n"
    )
    return all_of(
        (  # the folder is what the reader opens: whole, escaped, over 80 characters
            weird_dials_ok,
            "a folder with a break, whole, no dials"
            if weird_dials_ok
            else f"got: {weird_no_dials.stdout[-400:]}",
        ),
        (
            weird_repo_ok,
            "a folder with a break, whole, no repository"
            if weird_repo_ok
            else f"got: {weird_no_repo.stdout[-400:]}",
        ),
        (no_dials_ok, "no dials said" if no_dials_ok else f"got: {no_dials.stdout[-300:]}"),
        (from_sub_ok, "no dials said from a subfolder" if from_sub_ok else f"got: {from_sub.stdout[-300:]}"),
        (no_repo_ok, "no repository said" if no_repo_ok else f"got: {no_repo.stdout[-300:]}"),
        (bad_ok, "malformed dials: exit 1, rules kept" if bad_ok else f"got {bad.code}: {bad.stderr[:300]}"),
        (arg_ok, "an argument is a misinvocation" if arg_ok else f"got {arg.code}: {arg.stderr[:200]}"),
    )


def t32() -> tuple[bool, str]:
    """The rules text: under the platform's cap, of the size the module document states, every rule
    lettered, and the hook prints it before python3 is looked for."""
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"prints the rules text of ([0-9,]+) characters", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    letters = re.findall(r"^([a-z])\. ", RULES, re.M)
    ok = len(RULES) < 10_000 and stated == len(RULES) and letters == list("abcdefghi")
    return ok, (
        f"{len(RULES)} characters, as stated; rules a–i"
        if ok
        else f"{len(RULES)} characters, document states {stated}; letters {letters}"
    )


def t33() -> tuple[bool, str]:
    """The printer's absence paths: PyYAML missing is C2 first on stderr with the printer's closing
    line, the rules still on stdout; python3 missing is C1, the rules still printed first."""
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    root = prepared()
    no_yaml = SESSION.run_gate(session_json(root), env={"PYTHONPATH": str(shadow)})
    c2 = (
        "BROKEN: const-interaction needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{MODULE_ROOT / 'requirements.txt'}' — until then the gate's state is not said at session start"
    )
    yaml_ok, yaml_said = broken_first_line(no_yaml, c2)
    yaml_ok = yaml_ok and messages.s1_could_not_run() in no_yaml.stderr and no_yaml.stdout == RULES
    bin_dir = H.scratch_dir()
    (bin_dir / "sh").symlink_to(H.sh)
    for tool in ("cat", "dirname"):
        (bin_dir / tool).symlink_to(shutil.which(tool) or tool)
    no_python = SESSION.run_gate(session_json(root), env={"PATH": str(bin_dir)})
    c1 = (
        "BROKEN: const-interaction needs python3 — fix: install Python 3.12 or newer"
        " (https://www.python.org/downloads/) — until then the gate's state is not said at session start"
    )
    py_ok, py_said = broken_first_line(no_python, c1)
    py_ok = py_ok and no_python.stdout == RULES
    return all_of((yaml_ok, yaml_said), (py_ok, py_said))


# ---------------------------------------------------------------- the plugin's files


def t40() -> tuple[bool, str]:
    """The hooks file's shape: a SessionStart handler with no matcher and a PreToolUse handler on
    Bash, exec form, the placeholder in args, timeouts."""
    hooks = json.loads((MODULE_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    start_hook = hooks["SessionStart"][0]
    bash_hook = hooks["PreToolUse"][0]
    ok = (
        "matcher" not in start_hook
        and start_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"]
        and bash_hook["matcher"] == "Bash"
        and bash_hook["hooks"][0]["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/check-destructive.sh"]
        and all(
            h["hooks"][0]["command"] == "sh" and isinstance(h["hooks"][0]["timeout"], int)
            for h in (start_hook, bash_hook)
        )
    )
    return (
        ok,
        "SessionStart without matcher, PreToolUse on Bash, exec form, timeouts" if ok else f"bad: {hooks}",
    )


def t41() -> tuple[bool, str]:
    """The install note names no kit document; the manifest names the plugin; the install note's
    calibration example is accepted as it stands."""
    install = (MODULE_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    kit_words = ("MODULE.md", "requirements.md", "rollout-plan", "dec-00", "res-00", "CONVENTIONS.md")
    named = [word for word in kit_words if word in install]
    manifest = json.loads((MODULE_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    example = re.search(r"```yaml\n(.*?)```", install, re.S)
    accepted = False
    if example:
        loaded = yaml.safe_load(example.group(1))
        result, _ = gate_on(command("ls"), dials_patch=loaded)
        accepted = result.code == 0
    ok = not named and manifest["name"] == NAMESPACE and accepted
    return (
        ok,
        "no kit document named; manifest; example accepted" if ok else f"named {named}; accepted {accepted}",
    )


# ---------------------------------------------------------------- the runner

RED_LONG = "git push --force " + "x" * (12_000 - len("git push --force "))
SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=command("git status"),
    red=command("git push --force origin main"),
    red_finding=d1("git push --force origin main", 0, "--force"),
    green=shared.g1_green_event(messages.g1_command_passed(ENTRIES, 1)),
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=False,
    judges_envelopes=False,
    event="Bash",
    ask=True,
    long_value=command(RED_LONG),
    pattern_dial=PatternDial("territories", lambda pattern: own(territories=[pattern])),
)

ITEMS: list[tuple[int, str, Callable[[], tuple[bool, str]]]] = [
    (1, "red→green: a forced push asks, typed against the entry; --force-with-lease passes", t1),
    (2, "red→green: rm -rf inside a chain asks on that subcommand; rm of a file passes", t2),
    (3, "red→green: a hard reset inside bash -c asks; a soft reset passes", t3),
    (4, "red→green: a rebase inside a substitution asks; git log passes", t4),
    (5, "wrappers, assignments, a program path and git's global options hide nothing", t5),
    (
        6,
        "outside the list passes: a heredoc body, checkout -- ., an amend, a plain push, a flag after --",
        t6,
    ),
    (
        7,
        "the dial: empty gates nothing and says so; an own entry; a cluster; equality; one hit per piece",
        t7,
    ),
    (8, "severity warn: the finding as context, the command let through", t8),
    (9, "the scan explains a command; no command is a visible skip; --command needs --scan", t9),
    (10, "this module's C5 lines typed by hand, each exit 1", t10),
    (11, "an event the gate is not wired to, and a shell event without a command", t11),
    (12, "golden lines: D1 typed whole", t12),
    (13, "the tokeniser's readings typed by hand", t13),
    (20, "red→green: a plain list is red with L1 typed whole; handled lists are green", t20),
    (
        21,
        "not a finding: fence, one item, nested, anchor, numbered list; the first plain item; a loose list",
        t21,
    ),
    (22, "territories: a negated pattern takes a document out; a README at the top is covered", t22),
    (23, "the list scan as a hook is its own C12; a misinvocation exits 1", t23),
    (30, "session start: the rules first, the verbosity line, the zero line, the pairs numbered", t30),
    (31, "session start: no dials file, no repository, malformed dials, an argument", t31),
    (32, "the rules text: under the cap, of the stated size, lettered a–i", t32),
    (33, "the printer's absence paths: PyYAML missing is C2, python3 missing is C1, the rules kept", t33),
    (40, "the hooks file's shape", t40),
    (41, "the install note names no kit document; the manifest; the example accepted", t41),
]


def main() -> int:
    assertions = [Assertion(number, title, check) for number, title, check in ITEMS]
    return H.run_all([], [*assertions, *shared_assertions(SUBJECT, 101)])


if __name__ == "__main__":
    sys.exit(main())
