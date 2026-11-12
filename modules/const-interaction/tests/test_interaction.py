"""Fixtures of const-interaction: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, and the libraries in the plugin's requirements file. Every item
has a stable number: this module's own items from 1, the items every gate shares from 101.

Three entry points are driven: the shell gate through the shared items and its own, the
list-handles scan and the session-start printer through their own. The shell gate's red is
an `ask` verdict — exit 0, one JSON object asking the platform to prompt, the finding in its
reason — so its red→green pairs are written as assertions that read that reason, and the
shared items run with the subject's `ask` flag. The fixture consumer is the shared one; this
module resolves no policy and judges no envelope, so the shared items about the root policy
and about an unreadable envelope are skipped and their numbers stay free.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
import yaml
from constitution_layer_kit import messages as shared
from constitution_layer_kit.effect import History
from constitution_layer_kit.history import read_transcript
from constitution_layer_kit.model import Broken, Finding
from constitution_layer_kit.testing import items as shared_items
from constitution_layer_kit.testing.acceptance import broken_first_line, expect, failure_of, item
from constitution_layer_kit.testing.consumer import Consumer
from constitution_layer_kit.testing.harness import (
    Harness,
    Result,
    Write,
    ask_reason,
    bash_json,
    event_json,
    red_lines,
)
from constitution_layer_kit.testing.items import (
    PatternDial,
    Subject,
    fake_claude,
    git_patch,
    git_timeouts,
    hook_budget,
    reader_fake,
    tr_line,
    tr_turn,
)
from interaction_gate import effect_rules, messages, start, tokens
from interaction_gate.model import (
    DEFAULT_DESTRUCTIVE,
    DEFAULT_READER_LISTS,
    Entry,
    ReaderLists,
    Shell,
    Subcommand,
    Verbosity,
    Wrapper,
)

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"
PLUGIN_ROOT = SCRIPTS.parent
MODULE_ROOT = PLUGIN_ROOT.parent

IDENTITY = start.GATE  # declared for the whole session by conftest; the expected messages read it
# — and each is also typed by hand at least once in these fixtures (rule 14 of the gate-script rules)
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


def d1(text: str, words: str, matched: str, subcommand: str | None = None) -> Finding:
    """The finding of the default entry whose command words are `words`, found by its words and
    never by its place in the list; no such entry, or two, is an error naming the words."""
    found = [entry for entry in DEFAULT_DESTRUCTIVE if entry.command == tuple(words.split())]
    if len(found) != 1:
        raise AssertionError(f"d1: {len(found)} default entries with the command words {words!r}, wanted one")
    entry = found[0]
    return messages.d1_destructive(entry, Subcommand((), subcommand or text), matched)


def asked(text: str, finding: Finding, subcommands: int = 1, **kwargs: object) -> None:
    """The red half of the gate: exit 0, one JSON object asking, the one finding and the count in
    its reason and nothing else."""
    result, _ = gate_on(command(text), **kwargs)  # type: ignore[arg-type]
    reason = ask_reason(result)
    if reason is None:
        pytest.fail(f"no ask verdict; exit {result.code}: {result.stdout[:300]}{result.stderr[:300]}")
    wanted = [f"RED: {finding.headline}", messages.f9_count_command(1, subcommands)]
    ok = finding.render() in reason and red_lines(reason) == wanted and result.stdout.count("\n") == 1
    assert ok, f"asked with a different reason:\n{reason}"


def passed(text: str, subcommands: int = 1, entries: int = ENTRIES, **kwargs: object) -> None:
    result, _ = gate_on(command(text), **kwargs)  # type: ignore[arg-type]
    # typed by hand
    line = shared.g1_green_event(
        f"1 command examined: {subcommands} subcommand(s) against {entries} entries, none matched"
    )
    expect(result, 0, line, "stdout")


def pair(red: Callable[[], None], green: Callable[[], None]) -> Callable[[], None]:
    """A red→green item of the shell gate: red must ask, green must pass."""

    def check() -> None:
        said_red = failure_of(red)
        assert said_red is None, f"red half: {said_red}"
        said_green = failure_of(green)
        assert said_green is None, f"green half: {said_green}"

    return check


def broken(result: Result, failure: Broken, closing: str = shared.c11_broken_count()) -> None:
    broken_first_line(result, failure.render())
    first = f"exit 1, first stderr line: {failure.render()}"
    assert closing in result.stderr, f"no count line after: {first}"


# ---------------------------------------------------------------- the shell gate: red→green pairs

FORCE_PUSH = "git -C . push --force origin main"


@item(1, "red→green: a forced push asks, typed against the entry; --force-with-lease passes")
def test_t1() -> None:
    pair(
        lambda: asked(FORCE_PUSH, d1(FORCE_PUSH, "git push", "--force")),
        lambda: passed("git push --force-with-lease origin main"),
    )()


@item(2, "red→green: rm -rf inside a chain asks on that subcommand; rm of a file passes")
def test_t2() -> None:
    text = "cd build && rm -rf dist; ls"
    pair(
        lambda: asked(text, d1(text, "rm", "-r", "rm -rf dist"), subcommands=3),
        lambda: passed("cd build && rm dist.log; ls", subcommands=3),
    )()


@item(3, "red→green: a hard reset inside bash -c asks; a soft reset passes")
def test_t3() -> None:
    text = 'bash -c "git reset --hard HEAD~1"'
    finding = d1(text, "git reset", "--hard", "git reset --hard HEAD~1")
    pair(
        lambda: asked(text, finding, subcommands=2),
        lambda: passed('bash -c "git reset --soft HEAD~1"', subcommands=2),
    )()
    # typed by hand: a reset to HEAD~1 also drops a commit, so the why and the fix say so
    why = (
        "a hard reset discards every uncommitted change in the working tree and the index, which nothing"
        " brings back; with a target such as HEAD~1 it also drops the commits after the target from the"
        " branch"
    )
    fix = (
        "run git stash first, or reset with --keep, which stops when a change would be lost; with a"
        " target, also tag the tip first (git tag keep/<name>); to run it as written, confirm"
    )
    assert finding.why == why, f"why: {finding.why}"
    assert finding.fix.startswith(fix), f"fix: {finding.fix}"


@item(4, "red→green: a rebase inside a substitution asks; git log passes")
def test_t4() -> None:
    text = "echo $(git rebase main)"
    pair(
        lambda: asked(text, d1(text, "git rebase", "", "git rebase main"), subcommands=2),
        lambda: passed("echo $(git log -1)", subcommands=2),
    )()


@item(5, "wrappers, assignments, a program path and git's global options hide nothing")
def test_t5() -> None:
    """Wrappers, assignments, a program path, git's global options: none hides the verb.

    The cases, once held by the acceptance table of the module document: wrappers, shells,
    assignments, a program path and the options between a program and its verb hide nothing:
    `sudo /bin/rm -r`, `git -c k=v push -f`, `FOO=1 timeout 5 git stash drop`, `nohup git
    filter-repo`, `git gc --prune=now`, `env -i`, `sudo -k`, `sudo --user root`, `/usr/bin/env`,
    `bash -lc`, `exec`, `exec -a x rm -r y`, `if ...; then`, a redirection `2>&1`.

    Git's options are stepped over by the entry's matching: `-C .`, `-c k=v`, `--no-pager -C .`,
    `--git-dir .git` and `--git-dir=.git`, `--work-tree w`, `--namespace n`, and `--exec-path`,
    whose value git's page gives as optional.

    Each wrapper added on 2026-10-05 in the forms of its page: `busybox`, `setsid -f`, `ionice -c3`
    and `-c 3`, `taskset 0x3` and `-c 0,1`, `caffeinate -t 5`, `flock /tmp/l` and `-w 5 /tmp/l`,
    `chrt 10` and `-f 10`, and `flock /tmp/l -c '...'`. Each added shell with `-c`, fish's
    `--command=`, yash's `--cmdline`, mksh's `-T`, and fish's `-C` and `-c` in both orders, both
    strings read.
    """
    asked("sudo /bin/rm -r /tmp/x", d1("", "rm", "-r", "sudo /bin/rm -r /tmp/x"))
    asked(
        "git -c push.default=current push -f",
        d1("", "git push", "-f", "git -c push.default=current push -f"),
    )
    asked("FOO=1 timeout 5 git stash drop", d1("", "git stash drop", "", "FOO=1 timeout 5 git stash drop"))
    asked("nohup git filter-repo --path x", d1("", "git filter-repo", "", "nohup git filter-repo --path x"))
    asked("git gc --prune=now", d1("git gc --prune=now", "git gc", "--prune=now"))
    asked("env -i git push -f", d1("", "git push", "-f", "env -i git push -f"))
    asked("sudo -k git push -f", d1("", "git push", "-f", "sudo -k git push -f"))
    asked("sudo --user root git push -f", d1("", "git push", "-f", "sudo --user root git push -f"))
    asked("/usr/bin/env git push -f", d1("", "git push", "-f", "/usr/bin/env git push -f"))
    asked('bash -lc "git push -f"', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("exec git push -f", d1("", "git push", "-f", "exec git push -f"))
    # exec is a wrapper whose own option -a takes a value, bash's manual: it stood in front of the verb
    asked("exec -a x rm -r y", d1("", "rm", "-r", "exec -a x rm -r y"))
    asked("if true; then git push -f; fi", d1("", "git push", "-f", "then git push -f"), subcommands=2)
    asked("git push -f 2>&1", d1("", "git push", "-f", "git push -f 2>&1"))
    # git's options before the verb are skipped by the entry's matching, as for every program
    asked("git -C . push -f", d1("", "git push", "-f", "git -C . push -f"))
    asked("git -c k=v push -f", d1("", "git push", "-f", "git -c k=v push -f"))
    asked("git --no-pager -C . push -f", d1("", "git push", "-f", "git --no-pager -C . push -f"))
    asked(
        "git --git-dir .git push --force",
        d1("", "git push", "--force", "git --git-dir .git push --force"),
    )
    asked("git --git-dir=.git push -f", d1("", "git push", "-f", "git --git-dir=.git push -f"))
    asked("git --work-tree w reset --hard", d1("", "git reset", "--hard", "git --work-tree w reset --hard"))
    asked("git --namespace n push -f", d1("", "git push", "-f", "git --namespace n push -f"))
    # git's page gives the value of --exec-path as optional: the verb stands right after it
    asked("git --exec-path push -f", d1("", "git push", "-f", "git --exec-path push -f"))
    # the wrappers of the defaults whose pages the kit read on 2026-10-05, each in the forms of its page
    for form in (
        "busybox",
        "setsid -f",
        "ionice -c3",
        "ionice -c 3",
        "taskset 0x3",
        "taskset -c 0,1",
        "caffeinate -t 5",
        "flock /tmp/l",
        "flock -w 5 /tmp/l",
        "chrt 10",
        "chrt -f 10",
    ):
        asked(f"{form} rm -rf build", d1("", "rm", "-r", f"{form} rm -rf build"))
    # flock's `-c` after the lock file: the string it names is the command, read again
    asked("flock /tmp/l -c 'rm -rf build'", d1("", "rm", "-r", "rm -rf build"))
    # the shells of the defaults, `-c` and the forms of their pages: the string is read as commands
    for shell in ("fish", "ash", "mksh", "yash", "posh", "csh", "tcsh"):
        asked(f"{shell} -c 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("fish --command='git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("yash --cmdline 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("mksh -T /dev/tty2 -c 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    # fish runs `-C` and `-c` strings alike: every command flag met yields a string, both are read
    asked("fish -C 'set x 1' -c 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=3)
    asked("fish -c 'git push -f' -C 'set x 1'", d1("", "git push", "-f", "git push -f"), subcommands=3)


@item(6, "outside the list passes: a heredoc body, checkout -- ., an amend, a plain push, a flag after --")
def test_t6() -> None:
    """What the list leaves out passes and is said so in the install note: a heredoc body, the
    argument form, an amend, a plain push, a flag after `--`, one file removed.

    The cases, once held by the acceptance table of the module document. Outside the list, passes:
    a heredoc body, `git checkout -- .`, an amend, a plain push, a flag after `--`, `rm` of one
    file, `git branch -d`.

    A heredoc marker inside quotes, with or without its terminator line, hides nothing, and the
    commit forms `-F - <<'EOF'` and `-m "$(cat <<'EOF' ... )"` pass with a listed command in
    their body. A `$(` inside single quotes is text and a `)` restores an interrupted quote.

    `env -S` as a token, attached, in a cluster, long and with an unbalanced quote in its value,
    and `bash -o pipefail -c`, `-eo`, `+o posix` and `-O extglob` too, ask. `env -uSHELL` names a
    variable, not a split, and the command after it asks.

    A cluster whose last letter takes a value, `env -iu SHELL` and `sudo -iu root`, takes the next
    word, and so does a valued flag of a wrapper, short or long: `env -P`, `-L`, `-U`, `sudo -T`,
    `-R`, `--command-timeout`, `--chroot`, `doas -a`, `xargs -J`, `-R`, `-S`, `--max-chars`,
    `--process-slot-var`, `stdbuf --output`. The command after it asks, while a GNU flag whose
    value is optional, `xargs --max-lines` and `--eof`, takes no word when given bare. `sudo -c`,
    `-a`, `--login-class` and `--auth-type` are valued, while `sudo --login` and a bare `--` take
    no word.

    `bash --rcfile f -c`, `--init-file f -c`, `bash -c --` and a quoted `)` inside `$(...)`, the
    substitution itself inside a string or nested twice, hide nothing. `env -iu SHELL -S '...'`
    reads the split value after the cluster and its value.

    A word after a shell's strings is an argument and passes: `bash -c 'git status' git push -f`,
    and the same after fish's `-C` and `-c`. `bash -ce` asks.

    With a consumer entry `[kubectl, delete]`, a word that is neither an option nor an option's
    value between the entry's words, or a `--`, is no match: `kubectl get pods delete`,
    `kubectl -n prod get pods` and `kubectl -n prod -- delete pod x` pass. So do `git help
    restore`, `git - restore` and `git -C . help restore` for the default entry `git restore`.
    """
    entry = {"command": ["kubectl", "delete"], "teach": "a deleted resource is gone", "alternative": "scale"}
    kubectl = own(destructive=[entry])
    passed("cat <<EOF\nrm -rf /\nEOF\n")
    passed("git checkout -- .")
    passed("git commit --amend --no-edit")
    passed("git push origin main")
    passed("git push -- --force")
    passed("rm build.log")
    passed("git branch -d old")
    # a word after a shell's string is an argument: only the strings of its command flags are read
    passed("fish -C 'set x 1' -c 'git status' git push -f", subcommands=3)
    passed("bash -c 'git status' git push -f", subcommands=2)
    # a word that is neither an option nor an option's value ends the walk between an entry's words,
    # and so does `--`; the entry is one consumer entry, `kubectl delete`
    passed("kubectl get pods delete", entries=1, dials_patch=kubectl)
    passed("kubectl -n prod get pods", entries=1, dials_patch=kubectl)
    passed("kubectl -n prod -- delete pod x", entries=1, dials_patch=kubectl)
    # an option written with `=` takes no value after it: `get` ends the walk, `delete` is no verb here
    passed("kubectl --context=prod get delete", entries=1, dials_patch=kubectl)
    # the same of a default entry: a plain word first, a lone `-`, a plain word after an option's value
    passed("git help restore")
    passed("git - restore")
    passed("git -C . help restore")
    asked('echo "a<<EOF"\ngit push -f', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked('echo "a<<EOF"\ngit push -f\nEOF', d1("", "git push", "-f", "git push -f"), subcommands=3)
    asked("cat <<EOF\ngit push -f", d1("", "git push", "-f", "git push -f"), subcommands=2)
    passed(
        "git commit -q -F - <<'EOF'\nthe branch fix; git branch -f gated\nEOF",
        subcommands=1,
    )
    passed(
        "git commit -m \"$(cat <<'EOF'\nthe branch fix; git branch -f gated\nEOF\n)\"",
        subcommands=2,
    )
    asked('env -S "git push -f"', d1("", "git push", "-f", "git push -f"))
    asked('env -i -S "git push -f"', d1("", "git push", "-f", "git push -f"))
    asked('env --split-string="git push -f"', d1("", "git push", "-f", "git push -f"))
    asked('env --split-string "git push -f"', d1("", "git push", "-f", "git push -f"))
    asked('env -S "git push" -f', d1("", "git push", "-f", "git push -f"))
    asked("env -S'git push -f'", d1("", "git push", "-f", "git push -f"))
    asked("env -iS 'git push -f'", d1("", "git push", "-f", "git push -f"))
    asked("env -uSHELL git push -f", d1("", "git push", "-f", "env -uSHELL git push -f"))
    asked("env -iu SHELL git push -f", d1("", "git push", "-f", "env -iu SHELL git push -f"))
    asked("env -P /usr/bin git push -f", d1("", "git push", "-f", "env -P /usr/bin git push -f"))
    asked("sudo -iu root git push -f", d1("", "git push", "-f", "sudo -iu root git push -f"))
    asked("env -iu SHELL -S 'git push -f'", d1("", "git push", "-f", "git push -f"))
    asked("sudo -T 5 git push -f", d1("", "git push", "-f", "sudo -T 5 git push -f"))
    asked("sudo -R /tmp git push -f", d1("", "git push", "-f", "sudo -R /tmp git push -f"))
    asked("doas -a x git push -f", d1("", "git push", "-f", "doas -a x git push -f"))
    asked("xargs -J % git push -f", d1("", "git push", "-f", "xargs -J % git push -f"))
    asked("env -L user git push -f", d1("", "git push", "-f", "env -L user git push -f"))
    asked("env -U user git push -f", d1("", "git push", "-f", "env -U user git push -f"))
    asked(
        "sudo --command-timeout 5 git push -f",
        d1("", "git push", "-f", "sudo --command-timeout 5 git push -f"),
    )
    asked("sudo --chroot /tmp git push -f", d1("", "git push", "-f", "sudo --chroot /tmp git push -f"))
    asked("xargs --max-chars 10 git push -f", d1("", "git push", "-f", "xargs --max-chars 10 git push -f"))
    asked("xargs -R 2 git push -f", d1("", "git push", "-f", "xargs -R 2 git push -f"))
    asked("xargs -S 512 git push -f", d1("", "git push", "-f", "xargs -S 512 git push -f"))
    asked("xargs --max-lines git push -f", d1("", "git push", "-f", "xargs --max-lines git push -f"))
    asked("xargs --eof git push -f", d1("", "git push", "-f", "xargs --eof git push -f"))
    asked(
        "xargs --process-slot-var N git push -f",
        d1("", "git push", "-f", "xargs --process-slot-var N git push -f"),
    )
    asked("stdbuf --output L git push -f", d1("", "git push", "-f", "stdbuf --output L git push -f"))
    asked("sudo --login git push -f", d1("", "git push", "-f", "sudo --login git push -f"))
    asked("nice -- git push -f", d1("", "git push", "-f", "nice -- git push -f"))
    asked(
        "sudo --login-class staff git push -f",
        d1("", "git push", "-f", "sudo --login-class staff git push -f"),
    )
    asked("sudo --auth-type pam git push -f", d1("", "git push", "-f", "sudo --auth-type pam git push -f"))
    asked('bash --rcfile /dev/null -c "git push -f"', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked('bash -c -- "git push -f"', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("bash -ce 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked('echo $(echo ")"; git push -f)', d1("", "git push", "-f", "git push -f"), subcommands=3)
    asked('echo "$(echo ")"; git push -f)"', d1("", "git push", "-f", "git push -f"), subcommands=3)
    asked(
        'echo "$(echo "$(echo ")")"; git push -f)"',
        d1("", "git push", "-f", "git push -f"),
        subcommands=4,
    )
    asked(
        'bash --init-file /dev/null -c "git push -f"',
        d1("", "git push", "-f", "git push -f"),
        subcommands=2,
    )
    asked("echo $(echo $(date)) $(git push -f)", d1("", "git push", "-f", "git push -f"), subcommands=4)
    asked("sudo -c staff git push -f", d1("", "git push", "-f", "sudo -c staff git push -f"))
    asked("sudo -a pam git push -f", d1("", "git push", "-f", "sudo -a pam git push -f"))
    asked('env -S "git push -f \'x"', d1("", "git push", "-f", "git push -f ''\"'\"'x'"))
    asked("bash -O extglob -c 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked('env -S "echo \'x" ; git push -f', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("bash +o posix -c 'git push -f'", d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked('bash -o pipefail -c "git push -f"', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked('bash -eo pipefail -c "git push -f"', d1("", "git push", "-f", "git push -f"), subcommands=2)
    asked("echo '$(<<EOF'\ngit push -f\nEOF", d1("", "git push", "-f", "git push -f"), subcommands=4)
    asked('echo "$(date) a<<EOF"\ngit push -f\nEOF', d1("", "git push", "-f", "git push -f"), subcommands=4)


@item(
    7,
    "the dial: empty gates nothing; an own entry; options between an entry's words; the reader's"
    " two dials merged with the defaults",
)
def test_t7() -> None:
    """The dial: an empty list gates nothing and says so; an own entry with words alone; a short
    flag inside a cluster; a long flag by equality only; an entry's words apart by options; the
    reader's dials `wrappers` and `shells`, merged with the defaults by command.

    The cases, once held by the acceptance table of the module document. The dial: an empty list
    gates nothing and says so; an own entry with words alone; a short flag inside a cluster
    (`-xdf`); a long flag by equality (`--force-with-lease=main` passes); two entries matching
    one piece give one hit, the first. An entry written as a base name matches the program by any
    path, and `[git, -C]` loads.

    Options and their values stand between an entry's words and hide none: `kubectl -n prod
    delete`, `--context=prod`, `docker --context prod rm`, `terraform -chdir=infra destroy`,
    `helm -n prod uninstall`, `npx -y prisma migrate reset`, `uv run --with x rm -rf` with the
    flag `-r`; the false prompt `kubectl -n delete get pods` is pinned as asking. A wrapper's
    option `-X` loads and takes its value.

    The reader's dials: a wrapper added reads through (`uv run --with x`); a default dropped is
    read as a program, and an entry may name it; a default given again takes the fields as
    written; a shell added has its string read; a shell dropped passes; empty lists leave the
    defaults; a collision of a wrapper and a shell is judged on the merged lists; a later word
    with a `/` loads and reads; a wrapper with a command flag, `nix develop -c`, reads its
    string.
    """
    result, _ = gate_on(command(FORCE_PUSH), dials_patch=own(destructive=[]))
    nothing_gated = (  # typed by hand
        f"1 command examined against 0 entries — {NAMESPACE}.destructive is empty, nothing is gated"
    )
    expect(result, 0, shared.g1_green_event(nothing_gated), "stdout")
    teach, alternative = "a dropped database is gone", "dump it first"
    with_own = own(destructive=[{"command": ["dropdb"], "teach": teach, "alternative": alternative}])
    asked(
        "dropdb prod",
        messages.d1_destructive(
            Entry(("dropdb",), (), teach, alternative), Subcommand((), "dropdb prod"), ""
        ),
        dials_patch=with_own,
    )
    passed(FORCE_PUSH, entries=1, dials_patch=with_own)
    asked("git clean -xdf", d1("", "git clean", "-f", "git clean -xdf"))
    passed("git push --force-with-lease=main origin main")
    two = own(
        destructive=[
            {"command": ["dropdb"], "teach": "first", "alternative": "a"},
            {"command": ["dropdb"], "teach": "second", "alternative": "b"},
        ]
    )
    asked(
        "dropdb prod",
        messages.d1_destructive(Entry(("dropdb",), (), "first", "a"), Subcommand((), "dropdb prod"), ""),
        dials_patch=two,
    )
    # an entry written as a base name matches the program by any path (the reduction stays); an entry
    # with an option in it reads as itself and loads
    deploy = own(destructive=[{"command": ["deploy.sh"], "teach": teach, "alternative": alternative}])
    deploy_entry = Entry(("deploy.sh",), (), teach, alternative)
    for text in ("./scripts/deploy.sh prod", "/abs/scripts/deploy.sh prod", "deploy.sh prod"):
        asked(
            text,
            messages.d1_destructive(deploy_entry, Subcommand((), text), ""),
            dials_patch=deploy,
        )
    optioned = own(destructive=[{"command": ["git", "-C"], "teach": teach, "alternative": alternative}])
    passed("ls", entries=1, dials_patch=optioned)
    # an option and its value, or a runner the entry names, stand between an entry's words and hide none
    entries = [
        {"command": ["kubectl", "delete"]},
        {"command": ["docker", "rm"]},
        {"command": ["terraform", "destroy"]},
        {"command": ["helm", "uninstall"]},
        {"command": ["npx", "prisma", "migrate", "reset"]},
        {"command": ["uv", "run", "rm"], "flags": ["-r"]},
    ]
    shaped = own(destructive=[{**e, "teach": teach, "alternative": alternative} for e in entries])

    def between(text: str, words: str, matched: str = "") -> None:
        """The consumer entry with these words asks for the text."""
        entry = next(e for e in entries if " ".join(e["command"]) == words)
        flags = tuple(entry.get("flags", ()))
        wanted = Entry(tuple(entry["command"]), flags, teach, alternative)
        finding = messages.d1_destructive(wanted, Subcommand((), text), matched)
        asked(text, finding, dials_patch=shaped)

    # The reader's lists are dials, merged with the defaults by command. A wrapper added by its words
    # reads through to the command; a default dropped is read as a program, so an entry may name it; a
    # default given again replaces the default whole, a field it omits taking its empty value, not the
    # default's; a shell added has its command string read; an empty list leaves the defaults.
    uv_run = own(wrappers=[{"command": ["uv", "run"], "with_value": ["--with"]}])
    no_sudo = own(wrappers=[{"command": ["sudo"], "drop": True}])
    bare_sudo = own(wrappers=[{"command": ["sudo"]}])
    elvish = own(shells=[{"command": ["elvish"], "command_flags": ["-c"]}])
    sudo_own = own(
        wrappers=[{"command": ["sudo"], "drop": True}],
        destructive=[{"command": ["sudo"], "teach": teach, "alternative": alternative}],
    )
    sudo_entry = Entry(("sudo",), (), teach, alternative)
    rm_of = d1("", "rm", "-r", "uv run --with x rm -rf b")
    git_push = d1("", "git push", "-f", "git push -f")
    passed("uv run --with x rm -rf b")  # no dial: the default wrappers do not know uv
    asked("uv run --with x rm -rf b", rm_of, dials_patch=uv_run)
    passed("uv run pytest -k rm", dials_patch=uv_run)
    asked("nohup rm -rf b", d1("", "rm", "-r", "nohup rm -rf b"), dials_patch=uv_run)  # defaults stay
    passed("sudo rm -rf b", dials_patch=no_sudo)  # a dropped wrapper is read as a program
    asked(
        "sudo rm -rf b",
        messages.d1_destructive(sudo_entry, Subcommand((), "sudo rm -rf b"), ""),
        dials_patch=sudo_own,
    )
    passed("sudo -u root rm -rf b", dials_patch=bare_sudo)  # `-u` takes no value now: `root` is the program
    asked("sudo rm -rf b", d1("", "rm", "-r", "sudo rm -rf b"), dials_patch=bare_sudo)
    asked("sudo -u root rm -rf b", d1("", "rm", "-r", "sudo -u root rm -rf b"))  # the default's `-u`
    passed("elvish -c 'git push -f'")  # no dial: elvish is no default shell
    asked("elvish -c 'git push -f'", git_push, subcommands=2, dials_patch=elvish)
    passed(  # a replacing entry takes its fields as given: `-c` is no command flag now
        "bash -c 'git push -f'", dials_patch=own(shells=[{"command": ["bash"], "command_flags": ["-x"]}])
    )
    asked(  # a later word of a wrapper is compared as written, a '/' in it loads and can match
        "uv ./run rm -rf b",
        d1("", "rm", "-r", "uv ./run rm -rf b"),
        dials_patch=own(wrappers=[{"command": ["uv", "./run"]}]),
    )
    asked(  # a wrapper with a command flag reads the string after it
        "nix develop -c 'rm -rf b'",
        d1("", "rm", "-r", "rm -rf b"),
        dials_patch=own(wrappers=[{"command": ["nix", "develop"], "command_flags": ["-c"]}]),
    )
    passed("sh -c 'git push -f'", dials_patch=own(shells=[{"command": ["sh"], "drop": True}]))
    asked("sh -c 'git push -f'", git_push, subcommands=2, dials_patch=own(shells=[]))
    asked("sudo rm -rf b", d1("", "rm", "-r", "sudo rm -rf b"), dials_patch=own(wrappers=[], shells=[]))
    passed(  # a collision is judged on the merged lists: bash a wrapper, the default shell dropped
        "ls",
        dials_patch=own(wrappers=[{"command": ["bash"]}], shells=[{"command": ["bash"], "drop": True}]),
    )
    passed("ls", dials_patch=own(wrappers=[{"command": ["uv"], "with_value": [], "command_flags": []}]))
    asked(  # an option of the dash and one letter, X included, loads and takes its value
        "uv -X v rm -rf b",
        d1("", "rm", "-r", "uv -X v rm -rf b"),
        dials_patch=own(wrappers=[{"command": ["uv"], "with_value": ["-X"]}]),
    )
    between("kubectl -n prod delete pod x", "kubectl delete")
    between("kubectl --context=prod delete pod x", "kubectl delete")
    between("kubectl --namespace prod delete pod x", "kubectl delete")
    between("docker --context prod rm x", "docker rm")
    between("terraform -chdir=infra destroy", "terraform destroy")
    between("helm -n prod uninstall r", "helm uninstall")
    between("npx -y prisma migrate reset", "npx prisma migrate reset")
    between("uv run --with x rm -rf b", "uv run rm", "-r")
    # a value that equals the wanted word is read as that word: the known false prompt, by design
    between("kubectl -n delete get pods", "kubectl delete")


@item(8, "severity warn: the finding as context, the command let through")
def test_t8() -> None:
    """Severity warn: the finding reported as context and the command let through."""
    result, _ = gate_on(command(FORCE_PUSH), dials_patch=own(severity="warn"))
    if result.code != 0:
        pytest.fail(f"warn must let the command through; exit {result.code}: {result.stderr}")
    try:
        answer = json.loads(result.stdout)
        context = answer["hookSpecificOutput"]["additionalContext"]
    except (ValueError, KeyError, TypeError):
        pytest.fail(f"warn must answer with one JSON object; got: {result.stdout[:300]}")
    finding = d1(FORCE_PUSH, "git push", "--force")
    ok = (
        "permissionDecision" not in answer["hookSpecificOutput"]
        and finding.render() in context
        and shared.w1_warn_note() in context
        and answer["systemMessage"] == shared.w1_warn_system(finding.headline)
    )
    assert ok, f"bad: {answer}"


@item(9, "the scan explains a command; no command is a visible skip; --command needs --scan")
def test_t9() -> None:
    """The scan explains a command: the finding and the tail typed by hand, exit 2, with the lists
    the dials give; no command is a visible skip; --command without --scan is a misinvocation."""
    root = prepared()
    red = H.run_gate("", args=["--scan", str(root), "--command", "rm -rf build"])
    tail = "RED: 1 finding(s) — 1 command examined: 1 subcommand(s) against 14 entries"
    red_ok = red.code == 2 and red_lines(red.stdout) == [
        "RED: destructive command: 'rm -rf build' matches the entry rm with -r",
        tail,
    ]
    green = H.run_gate("", args=["--scan", str(root), "--command", "ls -la"])
    expect(
        green, 0, "GREEN: const-interaction: 1 command examined: 1 subcommand(s) against 14 entries", "stdout"
    )
    skip = H.run_gate("", args=["--scan", str(root)])
    expect(
        skip,
        0,
        "GREEN: const-interaction: 0 documents examined — no command given: run the scan with --command"
        " '<text>' to see what the dial does to it",
        "stdout",
    )
    mis = H.run_gate("", args=["--command", "ls"])
    mis_wanted = (  # typed by hand, the whole stderr
        "BROKEN: misinvocation: --command applies to --scan — fix: run with no arguments (hook) or --scan"
        " [<dir>] [--command <text>]\n"
        "BROKEN: the check could not run — 0 documents examined\n"
    )
    mis_ok = mis.code == 1 and mis.stdout == "" and mis.stderr == mis_wanted
    assert mis_ok, f"misinvocation: exit {mis.code}: {mis.stderr}"
    # the split of the scan reads the wrappers the dials give: `uv` is no default wrapper, so the command
    # behind `uv run --with x` is examined only when the scan splits with the loaded lists
    uv_root = prepared(own(wrappers=[{"command": ["uv", "run"], "with_value": ["--with"]}]))
    uv_text = "uv run --with x rm -rf b"
    through = H.run_gate("", args=["--scan", str(uv_root), "--command", uv_text])
    through_ok = through.code == 2 and red_lines(through.stdout) == [
        f"RED: destructive command: '{uv_text}' matches the entry rm with -r",
        tail,
    ]
    through_said = f"scan through a wrapper dial: exit {through.code}: {through.stdout.strip()[:160]}"
    assert red_ok, f"scan red: {red.stdout.strip()[:120]}"
    assert through_ok, through_said


def unread(words: list[str]) -> dict[str, object]:
    """One entry of `destructive` with these command words, well formed in every other field."""
    return own(destructive=[{"command": words, "teach": "t", "alternative": "a"}])


def reader_dial_cases(prefix: str) -> list[tuple[dict[str, object], str]]:
    """The C5 lines of the dials `wrappers` and `shells`, each typed by hand: the shape of a list and
    of an entry, a field the entry does not have, a bad command, a bad option, a bad count, `drop` in
    each of its three misuses, one command twice, a word both a wrapper and a shell, and `destructive`
    read through the lists given."""
    wrapper_shape = (
        "command: [<words>] and, all optional, with_value: [<options>], positionals: <count>, numbers:"
        " <count>, command_flags: [<options>]; or as command: [<words>] with drop: true to remove a default"
    )
    shell_shape = (
        "command: [<word>] and, all optional, with_value: [<options>], command_flags: [<options>]; or as"
        " command: [<word>] with drop: true to remove a default"
    )
    keep = "; leave the key out for the defaults, an empty list leaves them as they are"
    each = 'write one entry per "- " item as '
    w, s = prefix + "const-interaction.wrappers ", prefix + "const-interaction.shells "
    command_why = (
        "; a program is read by its base name, so a first word with a '/' can never match, and a word with"
        " white space is two words"
    )
    wrapper_command = (
        w + "entry 1: command must be a non-empty list of words, none empty, none holding white space, the"
        " first with no '/' — fix: write the words of the program as list items, such as command: [uv, run]"
        + command_why
    )
    shell_command = (
        s + "entry 1: command must be a list of one word, not empty, holding no white space and no '/' —"
        " fix: write the shell's name as the one item, such as command: [fish]" + command_why
    )
    unknown = "a misspelt field would be ignored in silence, so none is: write "
    never = "which the reader never matches, since it "
    sign = (
        "entry 1: {field} holds '{option}', which is no option, a lone sign naming nothing — fix: remove it;"
    )
    sign += " the reader already ends a program's options at '--'"
    cases: list[tuple[dict[str, object], str]] = [
        (own(wrappers="sudo"), w + "must be a list of entries — fix: " + each + wrapper_shape + keep),
        (own(shells="bash"), s + "must be a list of entries — fix: " + each + shell_shape + keep),
        (
            own(wrappers=["sudo"]),
            w + "entry 1: it is not a mapping — fix: write the entry as " + wrapper_shape,
        ),
        (own(shells=[["bash"]]), s + "entry 1: it is not a mapping — fix: write the entry as " + shell_shape),
        (
            own(wrappers=[{"command": ["uv"], "flags": ["-x"]}]),
            w + "entry 1: 'flags' is no field of a wrapper entry — fix: " + unknown + "command, with_value,"
            " positionals, numbers, command_flags or drop",
        ),
        (  # a wrapper's fields are not a shell's
            own(shells=[{"command": ["elvish"], "positionals": 1}]),
            s + "entry 1: 'positionals' is no field of a shell entry — fix: " + unknown + "command,"
            " with_value, command_flags or drop",
        ),
        (  # a line break in the key is shown escaped: the line stays one line
            own(wrappers=[{"command": ["uv"], "a\nb": 1}]),
            w + "entry 1: 'a\\nb' is no field of a wrapper entry — fix: " + unknown + "command, with_value,"
            " positionals, numbers, command_flags or drop",
        ),
        *((own(wrappers=[entry]), wrapper_command) for entry in unread_commands(["uv run"], ["/usr/bin/uv"])),
        *((own(shells=[entry]), shell_command) for entry in unread_commands(["a b"], ["/bin/elvish"])),
        (
            own(shells=[{"command": ["elvish", "x"]}]),
            s + "entry 1: command [elvish, x] has more than one word, and a shell is one word — fix: write"
            " one entry for each shell, command: [<word>]",
        ),
        *(  # the reader takes a shell word or an assignment off before it looks for a wrapper
            (
                own(wrappers=[{"command": [word]}]),
                w + f"entry 1: command starts with '{word}', which is a shell word or an assignment, and the"
                " reader takes both off before it looks for a wrapper, so the entry can never match — fix:"
                " remove the entry; a wrapper is named by the program that runs the command",
            )
            for word in ("if", "FOO=1", "{")
        ),
        *(  # and before it looks for a shell: a shell entry of such a word never matches either
            (
                own(shells=[{"command": [word]}]),  # no command_flags either: this refusal comes first
                s + f"entry 1: command starts with '{word}', which is a shell word or an assignment, and the"
                " reader takes both off before it looks for a shell, so the entry can never match — fix:"
                " remove the entry; a shell is named by the program that runs the string",
            )
            for word in ("if", "FOO=1")
        ),
        (
            own(wrappers=[{"command": ["uv"], "with_value": ["--with"], "command_flags": ["--with"]}]),
            w + "entry 1: with_value and command_flags both hold '--with', and the reader tries command_flags"
            " first, so its place in with_value is never used — fix: keep it in one of the two, in"
            " command_flags if its value is a command to read, in with_value if not",
        ),
        (
            own(shells=[{"command": ["elvish"], "with_value": ["-o"], "command_flags": ["-o"]}]),
            s + "entry 1: with_value and command_flags both hold '-o', and the reader tries command_flags"
            " first, so its place in with_value is never used — fix: keep it in one of the two, in"
            " command_flags if its value is a command to read, in with_value if not",
        ),
        *(  # a shell with no command flag reads no string: only a command flag yields one
            (
                own(shells=[entry]),
                s + f"entry 1: the shell '{word}' has no command_flags, so it reads no string, since only a"
                " command flag tells the reader that the first operand is one — fix: give the shell its"
                " command flag, such as command_flags: [-c], or remove the entry; a default shell is removed"
                f" by an entry with command: [{word}] and drop: true",
            )
            for word, entry in (("elvish", {"command": ["elvish"]}), ("bash", {"command": ["bash"]}))
        ),
        (
            own(wrappers=[{"command": ["uv"], "with_value": "-u"}]),
            w + "entry 1: with_value must be a list of options — fix: write the options as list items, each"
            " as the command line has it, such as -u or --user; to take none, leave the field out",
        ),
        (
            own(shells=[{"command": ["elvish"], "command_flags": "-c"}]),
            s + "entry 1: command_flags must be a list of options — fix: write the options as list items,"
            " each as the command line has it, such as -o, +o or --rcfile; to take none, leave the field out",
        ),
        (
            own(wrappers=[{"command": ["uv"], "with_value": [""]}]),
            w + "entry 1: with_value must be a list of options — fix: write the options as list items, each"
            " as the command line has it, such as -u or --user; to take none, leave the field out",
        ),
        (
            own(wrappers=[{"command": ["uv"], "with_value": ["-a b"]}]),
            w + "entry 1: with_value holds '-a b', which holds white space, and an option is one word of the"
            " command line — fix: write each option as an item of its own, such as -u or --user",
        ),
        (  # an option is echoed on one line, a break escaped
            own(wrappers=[{"command": ["uv"], "with_value": ["-a\nb"]}]),
            w + "entry 1: with_value holds '-a\\nb', which holds white space, and an option is one word of"
            " the command line — fix: write each option as an item of its own, such as -u or --user",
        ),
        *(  # a word that starts with a letter, a capital X too, is no option of a wrapper
            (
                own(wrappers=[{"command": ["uv"], "with_value": [option]}]),
                w
                + f"entry 1: with_value holds '{option}', which does not start with '-', so it is no option —"
                " fix: write it as the command line has it, with its dash, such as -u or --user",
            )
            for option in ("u", "Xu")
        ),
        (  # a wrapper's options are the words that start with '-': a '+' never matches
            own(wrappers=[{"command": ["uv"], "command_flags": ["+c"]}]),
            w + "entry 1: command_flags holds '+c', which does not start with '-', so it is no option — fix:"
            " write it as the command line has it, with its dash, such as -u or --user",
        ),
        *(  # a word that starts with a letter, a capital X too, is no option of a shell
            (
                own(shells=[{"command": ["elvish"], "with_value": [option]}]),
                s + f"entry 1: with_value holds '{option}', which starts with neither '-' nor '+', so it is"
                " no option — fix: write it as the command line has it, with its sign, such as -o, +o or"
                " --rcfile",
            )
            for option in ("o", "Xo")
        ),
        *(
            (
                own(wrappers=[{"command": ["uv"], field: [option]}]),
                w + sign.format(field=field, option=option),
            )
            for field, option in (("command_flags", "--"), ("with_value", "-"))
        ),
        (
            own(shells=[{"command": ["elvish"], "with_value": ["+"]}]),
            s + sign.format(field="with_value", option="+"),
        ),
        (
            own(wrappers=[{"command": ["uv"], "with_value": ["-cx"]}]),
            w
            + "entry 1: with_value holds '-cx', a short option of more than one letter, "
            + never
            + "reads a short cluster one letter at a time — fix: write as an option of its own, as"
            " '-<letter>', each letter that takes a value; a letter that takes none needs no entry; a long"
            " option is written --name",
        ),
        (
            own(wrappers=[{"command": ["uv"], "with_value": ["-abc"]}]),
            w
            + "entry 1: with_value holds '-abc', a short option of more than one letter, "
            + never
            + "reads a short cluster one letter at a time — fix: write as an option of its own, as"
            " '-<letter>', each letter that takes a value; a letter that takes none needs no entry; a long"
            " option is written --name",
        ),
        (  # a shell's command flag is read the same way
            own(shells=[{"command": ["elvish"], "command_flags": ["+ab"]}]),
            s
            + "entry 1: command_flags holds '+ab', a short option of more than one letter, "
            + never
            + "reads a short cluster one letter at a time — fix: write as an option of its own, as"
            " '+<letter>', each letter that is a command flag; any other letter needs no entry; a long option"
            " is written --name",
        ),
        (
            own(wrappers=[{"command": ["uv"], "command_flags": ["--c=x"]}]),
            w + "entry 1: command_flags holds '--c=x', " + never + "compares a long option by its name"
            " before the '=' — fix: write '--c'",
        ),
        (  # the option is cut at 80 characters in the headline, whole in the fix
            own(wrappers=[{"command": ["uv"], "with_value": ["--" + "x" * 100 + "=1"]}]),
            w
            + "entry 1: with_value holds '--"
            + "x" * 78
            + "… [104 characters]', "
            + never
            + "compares a long option by its name before the '=' — fix: write '--"
            + "x" * 100
            + "'",
        ),
        *(
            (
                own(wrappers=[{"command": ["uv"], field: value}]),
                w + f"entry 1: {field} must be a whole number of words, 0 or more, and true and false are no"
                f" number — fix: write {field}: 1, or another whole number, or leave the field out for 0",
            )
            for field, value in (("positionals", -1), ("numbers", True), ("positionals", "1"))
        ),
        (
            own(wrappers=[{"command": ["sudo"], "drop": False}]),
            w + "entry 1: drop must be true, its one value — fix: write drop: true beside command to remove"
            " the default of that command, or leave the field out",
        ),
        (
            own(shells=[{"command": ["sh"], "drop": "yes"}]),
            s + "entry 1: drop must be true, its one value — fix: write drop: true beside command to remove"
            " the default of that command, or leave the field out",
        ),
        (  # the first field beside it, in sorted order
            own(wrappers=[{"command": ["sudo"], "drop": True, "with_value": ["-u"], "positionals": 1}]),
            w + "entry 1: drop: true stands with command alone, and positionals stands beside it, which"
            " would be ignored in silence — fix: remove positionals to drop the default, or remove drop to"
            " replace the default with the fields",
        ),
        (  # it comes before the check of the field's own value
            own(shells=[{"command": ["sh"], "drop": True, "with_value": ["o"]}]),
            s + "entry 1: drop: true stands with command alone, and with_value stands beside it, which would"
            " be ignored in silence — fix: remove with_value to drop the default, or remove drop to replace"
            " the default with the fields",
        ),
        (
            own(wrappers=[{"command": ["suod"], "drop": True}]),
            w + "entry 1: drop names [suod], which is no default wrapper, and a misspelt name would drop"
            " nothing in silence — fix: write the command of a default wrapper (time, nohup, command,"
            " builtin, noglob, exec, xargs, sudo, doas, env, nice, stdbuf, timeout, busybox, setsid, ionice,"
            " taskset, caffeinate, flock, chrt) or remove the entry",
        ),
        (
            own(shells=[{"command": ["elvish"], "drop": True}]),
            s + "entry 1: drop names [elvish], which is no default shell, and a misspelt name would drop"
            " nothing in silence — fix: write the command of a default shell (bash, sh, zsh, dash, ksh, fish,"
            " ash, mksh, yash, posh, csh, tcsh) or remove the entry",
        ),
        (  # the word is echoed cut at 80 characters, its backslash doubled
            own(wrappers=[{"command": ["x\\y" + "z" * 100], "drop": True}]),
            w + "entry 1: drop names [x\\\\y" + "z" * 77 + "… [103 characters]], which is no default wrapper,"
            " and a misspelt name would drop nothing in silence — fix: write the command of a default"
            " wrapper (time, nohup, command, builtin, noglob, exec, xargs, sudo, doas, env, nice, stdbuf,"
            " timeout, busybox, setsid, ionice, taskset, caffeinate, flock, chrt) or remove the entry",
        ),
        (
            own(wrappers=[{"command": ["uv"]}, {"command": ["uv"], "with_value": ["-p"]}]),
            w + "entry 2: command [uv] stands in entry 1 already, and two entries of one command would leave"
            " one of them unread in silence — fix: keep one entry per command, with every field it needs;"
            " entries of one command are never merged",
        ),
        (  # a drop and a replacement of one command are two entries of it
            own(wrappers=[{"command": ["sudo"], "drop": True}, {"command": ["sudo"], "with_value": ["-u"]}]),
            w + "entry 2: command [sudo] stands in entry 1 already, and two entries of one command would"
            " leave one of them unread in silence — fix: keep one entry per command, with every field it"
            " needs; entries of one command are never merged",
        ),
        (
            own(shells=[{"command": ["elvish"]}, {"command": ["elvish"]}]),
            s + "entry 2: command [elvish] stands in entry 1 already, and two entries of one command would"
            " leave one of them unread in silence — fix: keep one entry per command, with every field it"
            " needs; entries of one command are never merged",
        ),
        (
            own(
                wrappers=[{"command": ["elvish"]}],
                shells=[{"command": ["elvish"], "command_flags": ["-c"]}],
            ),
            prefix + "const-interaction.wrappers and const-interaction.shells both name 'elvish', and a word"
            " is a wrapper or a shell, never both: the reader strips a wrapper before it reads a shell — fix:"
            " give it to one of the two dials: remove its entry from the other, where a default is removed"
            " by an entry with command: [elvish] and drop: true",
        ),
        (  # judged on the merged lists: bash is a default shell
            own(wrappers=[{"command": ["bash"]}]),
            prefix + "const-interaction.wrappers and const-interaction.shells both name 'bash', and a word is"
            " a wrapper or a shell, never both: the reader strips a wrapper before it reads a shell — fix:"
            " give it to one of the two dials: remove its entry from the other, where a default is removed"
            " by an entry with command: [bash] and drop: true",
        ),
        (  # judged on a wrapper's first word: `bash -c` strips both words, the shell's string is never read
            own(wrappers=[{"command": ["bash", "-c"]}]),
            prefix + "const-interaction.wrappers and const-interaction.shells both name 'bash', and a word is"
            " a wrapper or a shell, never both: the reader strips a wrapper before it reads a shell — fix:"
            " give it to one of the two dials: remove its entry from the other, where a default is removed"
            " by an entry with command: [bash] and drop: true",
        ),
        *(  # the default entries are read through the lists too, the key being absent: one that a wrapper
            # takes the first word of is refused, what is left of it or nothing named as its reading
            (
                own(wrappers=[{"command": wrapper}]),
                prefix + f"const-interaction.destructive is absent, so its default entry, command [{entry}],"
                f" is read by the gate as {reading}, which the lists of const-interaction.wrappers and"
                " const-interaction.shells cause — fix: remove or change the entry of"
                " const-interaction.wrappers or const-interaction.shells whose command starts with"
                f" '{first}', or write const-interaction.destructive out with commands the gate reads as"
                " written; the gate compares the reading, so the default entry would never match",
            )
            for wrapper, entry, reading, first in (
                (["git"], "git, push", "[push]", "git"),
                (["git", "push"], "git, push", "nothing", "git"),
                (["rm"], "rm", "nothing", "rm"),
                (["git", "stash"], "git, stash, drop", "[drop]", "git"),
            )
        ),
        (  # `destructive` is read through the lists given: a wrapper added hides its words
            own(
                wrappers=[{"command": ["uv", "run"], "with_value": ["--with"]}],
                destructive=[
                    {"command": ["uv", "run", "rm"], "flags": ["-r"], "teach": "t", "alternative": "a"}
                ],
            ),
            prefix + "const-interaction.destructive entry 1: command [uv, run, rm] is read by the gate as"
            " [rm] — fix: write command: [rm]; the gate compares the reading, so this entry can never match",
        ),
        (  # a shell added hands its string on
            own(
                shells=[{"command": ["elvish"], "command_flags": ["-c"]}],
                destructive=[{"command": ["elvish", "-c", "x"], "teach": "t", "alternative": "a"}],
            ),
            prefix + "const-interaction.destructive entry 1: command [elvish, -c, x] has no reading, since it"
            " hands a string on to be split again — fix: write the command the shell runs instead, such as"
            " command: [rm]; the gate compares the reading, so this entry can never match",
        ),
        (  # the reader's dials are read before `destructive`
            own(wrappers="sudo", destructive="rm"),
            w + "must be a list of entries — fix: " + each + wrapper_shape + keep,
        ),
    ]
    return cases


def unread_commands(*words: list[str]) -> list[dict[str, object]]:
    """Entries whose `command` is no usable list: missing, empty, not a list, a blank word, and each of
    the given word lists."""
    entries: list[dict[str, object]] = [{}, {"command": []}, {"command": "uv"}, {"command": ["uv", ""]}]
    entries.extend({"command": listed} for listed in words)
    return entries


@item(10, "this module's C5 lines typed by hand, an unread entry, the reader's dials, each exit 1")
def test_t10() -> None:
    """This module's C5 lines typed by hand, each exit 1.

    The cases, once held by the acceptance table of the module document: a key that is no dial,
    `destructive` not a list, an entry not a mapping, an unknown field, a command with a space,
    flags without `-`, `teach` missing, `handles` empty, a handle that does not compile,
    `territories` empty, a malformed pair, a `verbosity` outside its one value. Also an
    `alternative` missing or blank, a flag holding a space, a pair with a field that is no text, an
    option of either reader dial that starts with a capital X. The list in its
    headline is built from the `Verbosity` members, and the fix's "the one value today" is tied
    to there being one.

    The handle pattern of 102 characters with a backslash is cut at 80 with the compiler's words
    after it. The pattern of 105 characters with a group name of 100 gives the compiler's words
    over 80 characters, which stand whole after the cut pattern.

    Entries the reader does not read as themselves: a path, a wrapper, an assignment, `exec`, a
    wrapper alone, `x/`, `/`, `bash -c x`, and words that need echoing.

    The lines of the dials `wrappers` and `shells`: a wrong shape of the list or of an entry, an
    unknown field, a bad `command` in each dial, a first word that is a shell word or an
    assignment in each, an option in both fields, a shell with no command flag, each fault of an
    option, a count, `drop` in each of its three misuses and for no default, one command twice, a
    word in both dials judged on the merged lists, a wrapper by its first word, `destructive`
    read through the lists given, the reader's dials read before `destructive`.

    The default entries read through the lists, with the key absent, are refused where a wrapper
    takes the first word of one. A bad `wrappers` list is refused with one first line at every
    entry point: the hook, the command scan, the list scan and the session start.
    """
    prefix = "BROKEN: constitution.yaml: "
    try:  # the compiler's own words come from `re` itself, never from the code under test
        re.compile("(?P=" + "a" * 100 + ")")
    except re.error as compiler:
        long_words = str(compiler)
    else:
        pytest.fail("the pattern (?P=aaa...) compiled; the fixture needs one the compiler refuses")
    if len(long_words) <= 80:
        pytest.fail(f"the compiler's words are {len(long_words)} characters; the fixture needs more than 80")
    cases: list[tuple[dict[str, object], str]] = [
        (
            own(marker="x"),
            prefix + "const-interaction.marker is no dial of this module — fix: a misspelt dial would be"
            " ignored in silence, so none is: write one of severity, log_dir, destructive, wrappers, shells,"
            " territories, handles, boundary_examples, verbosity",
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
        *(  # an alternative missing, or blank
            (
                own(destructive=[entry]),
                prefix + "const-interaction.destructive entry 1: alternative must be a non-empty text — fix:"
                " write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is"
                " hard to reverse>, alternative: <the reversible way>",
            )
            for entry in (
                {"command": ["rm"], "teach": "t"},
                {"command": ["rm"], "teach": "t", "alternative": "  "},
            )
        ),
        (  # a flag holding a space is two words, never one flag
            own(destructive=[{"command": ["rm"], "flags": ["-r f"], "teach": "t", "alternative": "a"}]),
            prefix
            + "const-interaction.destructive entry 1: flags must be a list of flags, each starting with"
            " '-' — fix: write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the"
            " act is hard to reverse>, alternative: <the reversible way>",
        ),
        (  # a program's path is dropped by the reading: the base name is the entry to write
            unread(["./scripts/deploy.sh"]),
            prefix + "const-interaction.destructive entry 1: command [./scripts/deploy.sh] is read by the"
            " gate as [deploy.sh] — fix: write command: [deploy.sh]; the gate compares the reading, so this"
            " entry can never match",
        ),
        (
            unread(["/usr/bin/rm"]),
            prefix + "const-interaction.destructive entry 1: command [/usr/bin/rm] is read by the gate as"
            " [rm] — fix: write command: [rm]; the gate compares the reading, so this entry can never match",
        ),
        (  # a wrapper, an assignment and a shell word are dropped
            unread(["sudo", "rm"]),
            prefix + "const-interaction.destructive entry 1: command [sudo, rm] is read by the gate as [rm]"
            " — fix: write command: [rm]; the gate compares the reading, so this entry can never match",
        ),
        (
            unread(["FOO=1", "x"]),
            prefix + "const-interaction.destructive entry 1: command [FOO=1, x] is read by the gate as [x]"
            " — fix: write command: [x]; the gate compares the reading, so this entry can never match",
        ),
        (
            unread(["exec", "x"]),
            prefix + "const-interaction.destructive entry 1: command [exec, x] is read by the gate as [x]"
            " — fix: write command: [x]; the gate compares the reading, so this entry can never match",
        ),
        (  # nothing is left of a wrapper alone: the fix names what to write instead
            unread(["sudo"]),
            prefix + "const-interaction.destructive entry 1: command [sudo] is read by the gate as nothing"
            " — fix: write the command the wrapper or shell runs instead, such as command: [rm]; the gate"
            " compares the reading, so this entry can never match",
        ),
        (  # a word ending in a slash reads as an empty word, no command: the empty reading's fix
            unread(["x/"]),
            prefix + "const-interaction.destructive entry 1: command [x/] is read by the gate as nothing"
            " — fix: write the command the wrapper or shell runs instead, such as command: [rm]; the gate"
            " compares the reading, so this entry can never match",
        ),
        (
            unread(["/"]),
            prefix + "const-interaction.destructive entry 1: command [/] is read by the gate as nothing"
            " — fix: write the command the wrapper or shell runs instead, such as command: [rm]; the gate"
            " compares the reading, so this entry can never match",
        ),
        (  # a shell told to run a string hands it on: there is no reading of these words
            unread(["bash", "-c", "x"]),
            prefix + "const-interaction.destructive entry 1: command [bash, -c, x] has no reading, since it"
            " hands a string on to be split again — fix: write the command the shell runs instead, such as"
            " command: [rm]; the gate compares the reading, so this entry can never match",
        ),
        (  # the earlier checks come first: a malformed entry is refused as malformed
            own(destructive=[{"command": ["sudo rm"], "teach": "t", "alternative": "a"}]),
            prefix + "const-interaction.destructive entry 1: command must be a non-empty list of words — fix:"
            " write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard"
            " to reverse>, alternative: <the reversible way>",
        ),
        (  # an entry's words stand echoed, a line break escaped and a long word cut
            unread(["x\ny/" + "z" * 100]),
            prefix
            + "const-interaction.destructive entry 1: command [x\\ny/"
            + "z" * 76
            + "… [104 characters]] is read by the gate as ["
            + "z" * 80
            + "… [100 characters]] — fix: write command: ["
            + "z" * 100
            + "]; the gate compares the reading, so this entry can never match",
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
        (  # the compiler's words can pass 80 characters, a group name having no limit, and stand whole,
            # never cut, though the pattern before them is cut: 105 characters, cut at 80
            own(handles=["(?P=" + "a" * 100 + ")"]),
            prefix
            + "const-interaction.handles holds '(?P="
            + "a" * 76
            + "… [105 characters]', which is not a regular expression ("
            + long_words
            + ") — fix: repair the pattern; Python's re syntax, matched at the start of the item's text",
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
        *(  # a pair with a field missing, or a field that is no text
            (
                own(boundary_examples=[pair]),
                prefix
                + "const-interaction.boundary_examples must be a list of pairs {violates: <text>, complies:"
                ' <text>} — fix: write one pair per "- " item with exactly those two fields, or leave the key'
                " out",
            )
            for pair in ({"violates": "x"}, {"violates": 5, "complies": "c"})
        ),
    ]
    cases.extend(reader_dial_cases(prefix))
    for patch, line in cases:
        result, _ = gate_on(command("ls"), dials_patch=patch)
        broken_first_line(result, line)
        counted = shared.c11_broken_count() in result.stderr
        assert counted, f"no count line after: exit 1, first stderr line: {line}"
    # every entry point refuses a bad reader dial, with the same line first: the scan of a command, the
    # scan of the lists and the session start, besides the hook above
    bad_reader = own(wrappers="sudo")
    bad_line = (
        prefix + 'const-interaction.wrappers must be a list of entries — fix: write one entry per "- " item'
        " as command: [<words>] and, all optional, with_value: [<options>], positionals: <count>, numbers:"
        " <count>, command_flags: [<options>]; or as command: [<words>] with drop: true to remove a default;"
        " leave the key out for the defaults, an empty list leaves them as they are"
    )
    bad_root = prepared(bad_reader)
    for entry_point, run in (
        ("the command scan", H.run_gate("", args=["--scan", str(bad_root), "--command", "ls"])),
        ("the list scan", LISTS.run_gate("", args=["--scan", str(bad_root)])),
        ("the session start", SESSION.run_gate(session_json(bad_root))),
    ):
        broken_first_line(run, bad_line, label=entry_point)
    # the verbosity fix is prose that says "the one value today": a second value fails here, and
    # points at that prose
    one_value = len(Verbosity) == 1 and f"write verbosity: {Verbosity.TRIGGERED.value} — the one value" in (
        messages.c5_verbosity().fix
    )
    assert one_value, "a second value"


@item(11, "an event the gate is not wired to, and a shell event without a command")
def test_t11() -> None:
    """An event the gate is not wired to, and a shell event without a command, typed by hand."""
    root = prepared()
    write = H.run_gate(event_json(root, Write("docs/notes/a.md", "x")))
    broken_first_line(
        write,
        "BROKEN: hook input names the event 'PreToolUse' on tool 'Write', which this gate is not wired to"
        " — fix: wire the gate to PreToolUse with the matcher Bash, as the plugin's hooks file does; to see"
        " what the dial does to a command by hand run it with --scan --command '<text>'",
    )
    payload = json.dumps(
        {"hook_event_name": "PreToolUse", "cwd": str(root), "tool_name": "Bash", "tool_input": {}}
    )
    no_command = H.run_gate(payload)
    broken_first_line(
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
    broken_first_line(  # names only point: cut at 80 characters with the cut said, then escaped
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
    broken_first_line(  # the event name only points: cut at 80, the cut said, then escaped
        odd_event,
        "BROKEN: hook input names the event 'N\\nx\\\\y" + "e" * 75 + "… [95 characters]' on tool 'Bash',"
        " which this gate is not wired to — fix: wire the gate to PreToolUse with the matcher Bash, as the"
        " plugin's hooks file does; to see what the dial does to a command by hand run it with --scan"
        " --command '<text>'",
    )


@item(12, "golden lines: D1 typed whole")
def test_t12() -> None:
    """Golden lines: D1 for the force push typed whole against a fresh run, so a why emptied or a
    word lost inside the message function is red. Every default entry in each of its flags, 21
    subcommands of one command, asks with its own why and fix, the reason typed whole."""
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
    assert ok, f"differs:\n{reason}"
    # the command, words and flag only point: cut at 80, then escaped; teach and alternative whole
    assert odd_ok, f"differs:\n{odd_reason}"
    # Every default entry asks, in each of its flags, with its own why and fix: one command chains them all,
    # and the reason is typed whole from this table, never from the defaults it pins. A row is the
    # subcommand, the entry's words with the flag that matched, the why and the fix before the tail.
    tail = (
        "; to run it as written, confirm at the prompt — where no prompt can be shown, get the user's yes in"
        " chat and run it again, one yes per command; to stop gating it, remove the entry from"
        " const-interaction.destructive in constitution.yaml"
    )
    checkout = (
        "a forced checkout throws away local changes to the files it switches; nothing brings them back",
        "run git stash first, then check out; or commit the changes on a branch",
    )
    clean = (
        "git clean deletes untracked files, which no commit holds; nothing brings them back",
        "run git clean -n first to see what would go, then move what matters out of the tree",
    )
    branch = (
        "-D deletes a branch whether or not it is merged, and -f moves one to another commit: the commits"
        " left behind become unreachable",
        "delete with -d, which refuses an unmerged branch, or tag the tip first (git tag keep/<name>)",
    )
    recursive = (
        "a recursive rm deletes a directory tree outside git; nothing brings it back",
        "use git rm for tracked files, or move the directory to a scratch location first",
    )
    rewrite = (
        "rewrites history across every commit it touches",
        "clone the repository first, and rewrite the clone",
    )
    defaults = (
        ("git push -f", "git push with -f", *push_texts()),
        ("git push --force", "git push with --force", *push_texts()),
        (
            "git reset --hard",
            "git reset with --hard",
            "a hard reset discards every uncommitted change in the working tree and the index, which nothing"
            " brings back; with a target such as HEAD~1 it also drops the commits after the target from the"
            " branch",
            "run git stash first, or reset with --keep, which stops when a change would be lost; with a"
            " target, also tag the tip first (git tag keep/<name>)",
        ),
        ("git checkout -f x", "git checkout with -f", *checkout),
        ("git checkout --force x", "git checkout with --force", *checkout),
        (
            "git restore a",
            "git restore",
            "git restore discards the working-tree changes of the paths it names; nothing brings them back",
            "run git stash first, or git diff to see what would be lost, then restore one path at a time",
        ),
        ("git clean -f", "git clean with -f", *clean),
        ("git clean --force", "git clean with --force", *clean),
        ("git branch -D b", "git branch with -D", *branch),
        ("git branch -f b", "git branch with -f", *branch),
        ("git branch --force b", "git branch with --force", *branch),
        (
            "git stash drop",
            "git stash drop",
            "a dropped stash is unreachable; nothing lists it again",
            "apply it with git stash branch <name>, or leave it in the list",
        ),
        (
            "git stash clear",
            "git stash clear",
            "clear drops every stash at once; nothing lists them again",
            "drop one at a time after applying it with git stash branch <name>",
        ),
        (
            "git rebase main",
            "git rebase",
            "a rebase rewrites the commits of the branch: their hashes change, and a branch others hold"
            " diverges from theirs",
            "tag the tip first (git tag keep/<name>), or make the change on a new branch and merge",
        ),
        ("git filter-branch", "git filter-branch", "filter-branch " + rewrite[0], rewrite[1]),
        ("git filter-repo", "git filter-repo", "filter-repo " + rewrite[0], rewrite[1]),
        (
            "git reflog expire",
            "git reflog expire",
            "expiring the reflog removes the record that lets a lost commit be found again",
            "leave the reflog; disk is cheaper than a lost commit",
        ),
        (
            "git gc --prune=now",
            "git gc with --prune=now",
            "pruning now deletes every unreachable object at once, including those the reflog would have let"
            " you recover",
            "run git gc without --prune=now, which keeps recent unreachable objects",
        ),
        ("rm -r d", "rm with -r", *recursive),
        ("rm -R d", "rm with -R", *recursive),
        ("rm --recursive d", "rm with --recursive", *recursive),
    )
    chain = "; ".join(row[0] for row in defaults)
    every, _ = gate_on(command(chain))
    every_reason = ask_reason(every) or ""
    every_wanted = (
        "".join(
            f"RED: destructive command: '{text}' matches the entry {matched}\n"
            f"  why: {why}\n  fix: {fix}{tail}\n"
            for text, matched, why, fix in defaults
        )
        + "RED: 21 finding(s) — 1 command examined (21 subcommand(s))"
    )
    assert every_reason == every_wanted, f"differs:\n{every_reason}"


def push_texts() -> tuple[str, str]:
    """The why and the fix of the default entry `git push`, typed by hand."""
    return (
        "a forced push rewrites the branch on the remote: every other clone of it diverges, and the"
        " commits it replaced are unreachable there",
        "push with --force-with-lease, which refuses when the remote moved, or push a new branch and"
        " open a pull request",
    )


@item(13, "the readings typed by hand: every default wrapper, flag and shell, an entry's own")
def test_t13() -> None:
    """The tokeniser's readings, each typed by hand.

    The cases, once held by the acceptance table of the module document: every operator, a quoted
    operator, backticks, `env -i FOO=1 nice -n 5`, a quoted verb, `--git-dir=`, `sh -c` and what
    follows it, an unbalanced quote, a bare subshell, `sudo -u`, a continuation line, `&>`, a
    brace group, an assignment alone.

    117 readings in all, among them git's options kept in the words, `exec -a x`, each wrapper
    added on 2026-10-05 read to its command, `flock -c` before and after the lock file, each
    added shell with its string, a shell's strings (`-ce`, `-cl`, `-ec`, `-oc posix`,
    `-oe pipefail -c` in bash, `-oerrexit -c` in zsh and `-opipefail -c` in ksh, `-c -e`,
    `-c --`, arguments after the string, a script file with `-c` after it), fish's `-C` and `-c`
    in both orders and with a flag that waits, and `--` ending the options of a wrapper and of a
    shell. Since 2026-11-12 also: each two-letter operator before a redirection, each shell word,
    `<&` and `>&`, a heredoc whose terminator is the next line and two operators on one line, a
    heredoc marker in quotes, an escape outside quotes, a substitution at the text's start, a `(`
    and a quote inside `$(…)`, two backtick pairs, chrt's one number, a string two shell walks
    find, flock's `-c` with `--`.

    Ten texts a slip could turn into an endless loop run through the gate within the harness's
    bound: a lone backtick, backtick pairs empty or side by side, and an escape in double quotes
    or outside quotes, at the top level, before a heredoc operator and inside `$(…)`.

    A table typed by hand, never derived from the code, pins 151 readings: every default wrapper
    name, every valued flag of every wrapper, every default shell and every option of a shell
    that takes a value, each read to `rm -rf b`.

    14 readings on lists of their own hold the fields no default uses: a wrapper of two words,
    `numbers`, a command flag after a positional word, a shell's long command flag.

    11 readings of an entry's own words: `[git, -C]` and `[deploy.sh]` read as themselves, while a
    path, a wrapper, an assignment, `exec`, a wrapper alone, `x/` and a string handed on do not.
    Each of the fourteen default entries reads as itself.
    """
    readings = {
        "git -C . push --force origin main": [("git", "-C", ".", "push", "--force", "origin", "main")],
        "a && b || c; d | e |& f & g\nh": [("a",), ("b",), ("c",), ("d",), ("e",), ("f",), ("g",), ("h",)],
        'echo "a && b"': [("echo", "a && b")],
        "echo `git rebase x`": [("git", "rebase", "x"), ("echo", "`git", "rebase", "x`")],
        "env -i FOO=1 nice -n 5 rm -r x": [("rm", "-r", "x")],
        "git 'push' --force": [("git", "push", "--force")],
        # git's options stay in the words: the entry's matching skips them, the reader does not
        "git --git-dir=.git push -f": [("git", "--git-dir=.git", "push", "-f")],
        "git --git-dir .git --no-pager push -f": [("git", "--git-dir", ".git", "--no-pager", "push", "-f")],
        'sh -c "rm -r x" && echo done': [("sh", "-c", "rm -r x"), ("rm", "-r", "x"), ("echo", "done")],
        "echo 'unbalanced && rm -r x": [("echo", "'unbalanced", "&&", "rm", "-r", "x")],
        "(cd x && rm -r y)": [("cd", "x"), ("rm", "-r", "y")],
        "sudo -u root rm -r x": [("rm", "-r", "x")],
        "exec -a x rm -r y": [("rm", "-r", "y")],
        # the wrappers added on 2026-10-05, each to the command: busybox has no option of its own, taskset
        # and flock one word before it, chrt an optional number, ionice two valued options in two forms
        "busybox rm -rf b": [("rm", "-rf", "b")],
        "setsid -f rm -rf b": [("rm", "-rf", "b")],
        "ionice -c3 rm -rf b": [("rm", "-rf", "b")],
        "ionice -c 3 rm -rf b": [("rm", "-rf", "b")],
        "ionice --class 3 --classdata 7 rm -rf b": [("rm", "-rf", "b")],
        "taskset 0x3 rm -rf b": [("rm", "-rf", "b")],
        "taskset -c 0,1 rm -rf b": [("rm", "-rf", "b")],
        "caffeinate -t 5 rm -rf b": [("rm", "-rf", "b")],
        "caffeinate -dimsu rm -rf b": [("rm", "-rf", "b")],
        "flock /tmp/l rm -rf b": [("rm", "-rf", "b")],
        "flock -w 5 /tmp/l rm -rf b": [("rm", "-rf", "b")],
        "flock -n -E 9 /tmp/l rm -rf b": [("rm", "-rf", "b")],
        "chrt 10 rm -rf b": [("rm", "-rf", "b")],
        "chrt -f 10 rm -rf b": [("rm", "-rf", "b")],
        "chrt -i rm -rf b": [("rm", "-rf", "b")],
        "chrt --sched-period 100 -d 0 rm -rf b": [("rm", "-rf", "b")],
        # flock's `-c` (`--command`) names a string a shell runs: read again, before the lock file or after it
        "flock /tmp/l -c 'rm -rf b'": [("rm", "-rf", "b")],
        "flock -c 'rm -rf b' /tmp/l": [("rm", "-rf", "b", "/tmp/l")],
        "flock --command 'rm -rf b' /tmp/l": [("rm", "-rf", "b", "/tmp/l")],
        # the shells added on 2026-10-05: `-c` and its string; fish's `-C` and its long forms too, yash's
        # `--cmdline`, mksh's `-T` takes the next word, fish's `-d` too
        "fish -c 'rm -rf b'": [("fish", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "fish --command='rm -rf b'": [("fish", "--command=rm -rf b"), ("rm", "-rf", "b")],
        "fish -C 'rm -rf b'": [("fish", "-C", "rm -rf b"), ("rm", "-rf", "b")],
        "fish --init-command='rm -rf b'": [("fish", "--init-command=rm -rf b"), ("rm", "-rf", "b")],
        "fish -d x -c 'rm -rf b'": [("fish", "-d", "x", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "ash -c 'rm -rf b'": [("ash", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "mksh -T /dev/tty2 -c 'rm -rf b'": [
            ("mksh", "-T", "/dev/tty2", "-c", "rm -rf b"),
            ("rm", "-rf", "b"),
        ],
        "yash --cmdline 'rm -rf b'": [("yash", "--cmdline", "rm -rf b"), ("rm", "-rf", "b")],
        "posh -c 'rm -rf b'": [("posh", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "csh -c 'rm -rf b'": [("csh", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "tcsh -c 'rm -rf b'": [("tcsh", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        # a shell's command flag yields its string, whatever letters share the cluster: the next word when
        # that is no option, else the first operand after the options, each read once; the words after the
        # string are arguments, not read; with no command flag the first operand is a script file
        "bash -ce 'rm -rf b'": [("bash", "-ce", "rm -rf b"), ("rm", "-rf", "b")],
        "bash -cl 'rm -rf b'": [("bash", "-cl", "rm -rf b"), ("rm", "-rf", "b")],
        "sh -ec 'rm -rf b'": [("sh", "-ec", "rm -rf b"), ("rm", "-rf", "b")],
        "bash -oc posix 'rm -rf b'": [("bash", "-oc", "posix", "rm -rf b"), ("rm", "-rf", "b")],
        "bash -c -e 'rm -rf b'": [("bash", "-c", "-e", "rm -rf b"), ("rm", "-rf", "b")],
        "bash -c 'rm -rf b' arg0 arg1": [("bash", "-c", "rm -rf b", "arg0", "arg1"), ("rm", "-rf", "b")],
        "bash script.sh -c x": [("bash", "script.sh", "-c", "x")],
        "bash -c -- 'rm -rf b'": [("bash", "-c", "--", "rm -rf b"), ("rm", "-rf", "b")],
        # a shell's valued letters each take the next word, whatever their place in the cluster; a word that
        # starts with `+` is an option too, so it is no string
        "bash -oe pipefail -c 'rm -rf b'": [
            ("bash", "-oe", "pipefail", "-c", "rm -rf b"),
            ("rm", "-rf", "b"),
        ],
        "bash -oO pipefail extglob -c 'rm -rf b'": [
            ("bash", "-oO", "pipefail", "extglob", "-c", "rm -rf b"),
            ("rm", "-rf", "b"),
        ],
        "bash -c +x 'rm -rf b'": [("bash", "-c", "+x", "rm -rf b"), ("rm", "-rf", "b")],
        # zsh and ksh take a valued letter's value attached when the cluster goes on (`-oerrexit`), bash
        # takes the next word; a cluster with a valued letter not last is read both ways, and the strings
        # of either reading are read, each once, in the order they stand
        "zsh -oerrexit -c 'rm -rf b'": [("zsh", "-oerrexit", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "ksh -opipefail -c 'rm -rf b'": [("ksh", "-opipefail", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "zsh -c -oerrexit 'rm -rf b'": [("zsh", "-c", "-oerrexit", "rm -rf b"), ("rm", "-rf", "b")],
        "zsh -eoerrexit -c 'rm -rf b'": [("zsh", "-eoerrexit", "-c", "rm -rf b"), ("rm", "-rf", "b")],
        "zsh -oerrexit -c 'rm -rf b' arg0": [
            ("zsh", "-oerrexit", "-c", "rm -rf b", "arg0"),
            ("rm", "-rf", "b"),
        ],
        "bash -co pipefail 'rm -rf b'": [("bash", "-co", "pipefail", "rm -rf b"), ("rm", "-rf", "b")],
        "bash -ce -x 'rm -rf b'": [("bash", "-ce", "-x", "rm -rf b"), ("rm", "-rf", "b")],
        "bash -oc 'rm -rf b'": [("bash", "-oc", "rm -rf b")],
        # every command flag met yields a string, each read in the order it stands: its attached value, else
        # the next word when that is no option and no other option's value, else the first operand after the
        # options; a word taken as a string is no operand, so a POSIX shell's one string is read once
        "fish -C 'set x 1' -c 'rm -rf b'": [
            ("fish", "-C", "set x 1", "-c", "rm -rf b"),
            ("set", "x", "1"),
            ("rm", "-rf", "b"),
        ],
        "fish -c 'rm -rf b' -C 'set x 1'": [
            ("fish", "-c", "rm -rf b", "-C", "set x 1"),
            ("rm", "-rf", "b"),
            ("set", "x", "1"),
        ],
        "fish --init-command='set x 1' -c 'rm -rf b'": [
            ("fish", "--init-command=set x 1", "-c", "rm -rf b"),
            ("set", "x", "1"),
            ("rm", "-rf", "b"),
        ],
        "fish -C -c 'set x 1' 'rm -rf b'": [
            ("fish", "-C", "-c", "set x 1", "rm -rf b"),
            ("set", "x", "1"),
            ("rm", "-rf", "b"),
        ],
        "fish -c -C 'rm -rf b'": [("fish", "-c", "-C", "rm -rf b"), ("rm", "-rf", "b")],
        "fish -d x -C 'set x 1' --command 'rm -rf b'": [
            ("fish", "-d", "x", "-C", "set x 1", "--command", "rm -rf b"),
            ("set", "x", "1"),
            ("rm", "-rf", "b"),
        ],
        "bash -c -- -x": [("bash", "-c", "--", "-x"), ("-x",)],
        # `--` ends the options of a wrapper and of a shell: what follows it is the command, or a file
        "nice -- -n 5 rm -rf b": [("-n", "5", "rm", "-rf", "b")],
        "sh -- -lc 'rm -rf b'": [("sh", "--", "-lc", "rm -rf b")],
        "git push \\\n -f": [("git", "push", "-f")],
        "ls &> /dev/null; rm -r x": [("ls", "&>", "/dev/null"), ("rm", "-r", "x")],
        "{ git push -f; }": [("git", "push", "-f")],
        "FOO=1": [],
        # a two-letter operator is read before its one-letter prefix: `&&`, `||` and `|&` each cut once,
        # and the redirection after them keeps its own `&`
        "a &&> b": [("a",), (">", "b")],
        "a ||&> b": [("a",), ("&>", "b")],
        "a |&> b": [("a",), (">", "b")],
        # each shell word is stripped, by name or by path, so the program after it is read
        "! git push -f": [("git", "push", "-f")],
        "if x; then :; else git push -f; fi": [("x",), (":",), ("git", "push", "-f")],
        "if x; then :; elif git push -f; then :; fi": [("x",), (":",), ("git", "push", "-f"), (":",)],
        "while git push -f; do :; done": [("git", "push", "-f"), (":",)],
        "until git push -f; do :; done": [("git", "push", "-f"), (":",)],
        "while x; do git push -f; done": [("x",), ("git", "push", "-f")],
        "/bin/do git push -f": [("git", "push", "-f")],
        # `<&` and `>&` redirect and cut nothing, at the text's start too; a `&` that opens the text cuts
        "cat <&3 & git push -f": [("cat", "<&3"), ("git", "push", "-f")],
        "ls >& x; git push -f": [("ls", ">&", "x"), ("git", "push", "-f")],
        "& ls >": [("ls", ">")],
        ">& x": [(">&", "x")],
        # a heredoc whose terminator is the next line drops nothing but the operator's body, and the lines
        # after it are read; of two operators on one line, the first one's body alone is dropped, so the
        # second body is read as commands, which examines more
        "cat <<EOF\nEOF\nls": [("cat", "<<EOF"), ("ls",)],
        "cat <<A <<B\nx\nA\ny\nB\nls": [("cat", "<<A", "<<B"), ("y",), ("B",), ("ls",)],
        # an operator inside quotes at the line's first character drops nothing; one after a closed quote
        # inside `$(…)` drops its body
        '"<<EOF"\ngit push -f\nEOF': [("<<EOF",), ("git", "push", "-f"), ("EOF",)],
        'x $("a" <<EOF\nb\nEOF\n)': [("a", "<<EOF"), ("x", "$(a", "<<EOF", ")")],
        # a backtick opens a quote at the top-level split, so its `;` cuts nothing there; an escape outside
        # quotes takes one character with it, at the text's end too
        "echo `a; git push -f`": [("a",), ("git", "push", "-f"), ("echo", "`a;", "git", "push", "-f`")],
        "echo \\;": [("echo", ";")],
        "echo \\a; git push -f": [("echo", "a"), ("git", "push", "-f")],
        # a substitution at the text's start is read; a quoted `)` ends none; two pairs of backticks apart
        # are both read
        "$(git push -f)": [("git", "push", "-f"), ("$(git", "push", "-f)")],
        'echo $("a)" b) x': [("a)", "b"), ("echo", "$(a)", "b)", "x")],
        "echo `a` `b`": [("a",), ("b",), ("echo", "`a`", "`b`")],
        # a `(` inside `$(…)` opens a level that its `)` closes, at the top-level split and in the contents
        "echo $( (cd x) ; git push -f)": [
            ("cd", "x"),
            ("git", "push", "-f"),
            ("echo", "$(", "(cd", "x)", ";", "git", "push", "-f)"),
        ],
        'echo "$( (a) )"; git push -f': [("a",), ("echo", "$( (a) )"), ("git", "push", "-f")],
        'echo $( "$( (x) )" ) $(git push -f)': [
            ("x",),
            ("$( (x) )",),
            ("git", "push", "-f"),
            ("echo", "$(", "$( (x) )", ")", "$(git", "push", "-f)"),
        ],
        # inside `$(…)`: a `$(` in single quotes is text, a quote that a nested `$(` interrupted is restored
        # at its `)`, a single-quoted `)` closes nothing
        "echo $(echo '$(') $(git push -f)": [
            ("echo", "$("),
            ("git", "push", "-f"),
            ("echo", "$(echo", "$()", "$(git", "push", "-f)"),
        ],
        'echo $( "$(a)" ) $(git push -f)': [
            ("a",),
            ("$(a)",),
            ("git", "push", "-f"),
            ("echo", "$(", "$(a)", ")", "$(git", "push", "-f)"),
        ],
        "echo $(echo ')' ) $(git push -f)": [
            ("echo", ")"),
            ("git", "push", "-f"),
            ("echo", "$(echo", ")", ")", "$(git", "push", "-f)"),
        ],
        "elif $( push &> 5 $(": [("push", "&>", "5", "$"), ("$(", "push", "&>", "5", "$(")],
        # a wrapper's numbers: one word only and no number leaves it the program; no wrapper but chrt
        # skips a number, and chrt one at most
        "chrt x": [("x",)],
        "nohup 5 rm -rf b": [("5", "rm", "-rf", "b")],
        "chrt 10 5 rm -rf b": [("5", "rm", "-rf", "b")],
        # a shell's strings: one both walks find is read once, in the order of their places; the zsh walk
        # sees a command flag in a cluster of three letters; a long option no list knows takes no word
        "zsh -coX 'git push -f' -coX 'git push -f'": [
            ("zsh", "-coX", "git push -f", "-coX", "git push -f"),
            ("git", "push", "-f"),
        ],
        "zsh -coerrexit 'git push -f'": [("zsh", "-coerrexit", "git push -f"), ("git", "push", "-f")],
        "fish -coX -cXo -- --command=A": [
            ("fish", "-coX", "-cXo", "--", "--command=A"),
            ("--command=A",),
            ("A",),
        ],
        "bash --norc deploy.sh": [("bash", "--norc", "deploy.sh")],
        # flock's `-c`: a `--` before its string is skipped when a word follows it, else it is the string;
        # a `--` after the string belongs to the command; no word after `-c` reads nothing
        "flock -c -- 'git push -f'": [("git", "push", "-f")],
        "flock -c 'git push -f' -- y": [("git", "push", "-f", "--", "y")],
        "flock -c --": [("--",)],
        "flock -c": [],
    }
    # the reading of an entry's own words, the dials loader's test: every default entry reads as
    # itself; a path, a wrapper, an assignment, a shell word and a wrapper alone do not; a shell told
    # to run a string, or `env -S`, has no reading; an option in an entry stays
    unread = [
        [entry.command, tokens.reading(entry.command, DEFAULT_READER_LISTS)]
        for entry in DEFAULT_DESTRUCTIVE
        if tokens.reading(entry.command, DEFAULT_READER_LISTS) != list(entry.command)
    ]
    entry_readings = {
        ("git", "-C"): ["git", "-C"],
        ("deploy.sh",): ["deploy.sh"],
        ("./scripts/deploy.sh",): ["deploy.sh"],
        ("/usr/bin/rm",): ["rm"],
        ("sudo", "rm"): ["rm"],
        ("FOO=1", "x"): ["x"],
        ("exec", "x"): ["x"],
        ("sudo",): [],
        ("x/",): [""],
        ("bash", "-c", "x"): None,
        ("env", "-S", "x"): None,
    }
    off = {
        words: tokens.reading(words, DEFAULT_READER_LISTS)
        for words, reading in entry_readings.items()
        if tokens.reading(words, DEFAULT_READER_LISTS) != reading
    }
    if unread or off:
        pytest.fail(f"defaults not read as themselves: {unread}; entry readings wrong: {off}")
    # The reader's default wrappers and shells, as they stood before their lists moved into dials and the
    # ones added since, typed by hand and never derived from tokens.py: a table derived from the code
    # would move with it and guard nothing. Every wrapper name, every valued flag of every wrapper (a flag
    # takes the next word `v`), every shell, and every option of a shell that takes a value, each read to
    # `rm -rf b`.
    wrapper_names = (
        "time",
        "nohup",
        "command",
        "builtin",
        "noglob",
        "xargs",
        "sudo",
        "doas",
        "env",
        "nice",
        "stdbuf",
        "timeout",
        "exec",
        # added on 2026-10-05, from the pages their entries cite
        "busybox",
        "setsid",
        "ionice",
        "taskset",
        "caffeinate",
        "flock",
        "chrt",
    )
    # env's `-S` and `--split-string` are no flags of this table: item 6 holds the string they name
    valued_flags = {
        "xargs": "-I -J -d -P -s -n -L -a -E -R -S --max-args --max-procs --max-chars --arg-file"
        " --delimiter --process-slot-var",
        "sudo": "-u -g -C -p -h -U -r -t -D -R -T -a -c --user --group --close-from --prompt --host"
        " --other-user --role --type --chdir --chroot --command-timeout --auth-type --login-class",
        "doas": "-u -C -a",
        "env": "-C -u -P -L -U --chdir --unset",
        "nice": "-n --adjustment",
        "stdbuf": "-i -o -e --input --output --error",
        "timeout": "-s -k --signal --kill-after",
        "exec": "-a",  # added with its move to a wrapper: bash's manual, `exec [-cl] [-a name] [command]`
        # added on 2026-10-05; flock's `-c` and `--command` are command flags, held by their own readings
        "ionice": "-c -n --class --classdata",
        "caffeinate": "-t -w",
        "flock": "-E -w --conflict-exit-code --wait --timeout --start --length",
        "chrt": "-T -P -D -U -X --sched-runtime --sched-period --sched-deadline --clamp-min --clamp-max",
    }
    # `timeout <duration> <command>`, `taskset <mask> <command>`, `flock <file> <command>`: one word before it
    positional = {"timeout": " 5", "taskset": " 0x3", "flock": " /tmp/l"}
    shells = ("bash", "sh", "zsh", "dash", "ksh", "fish", "ash", "mksh", "yash", "posh", "csh", "tcsh")
    shell_options = (  # (shell, the options before `-c`)
        ("bash", "-o pipefail "),
        ("bash", "-O extglob "),
        ("bash", "+O extglob "),
        ("bash", "-eO extglob "),
        ("bash", "+o posix "),
        ("bash", "-eo pipefail "),
        ("bash", "--rcfile f "),
        ("bash", "--init-file f "),
        ("zsh", "--rcfile f "),
        ("ksh", "--init-file f "),
        # added on 2026-10-05: the options of each page that take the next word
        ("fish", "-d x "),
        ("fish", "-o x "),
        ("fish", "-p x "),
        ("fish", "-f x "),
        ("fish", "--debug x "),
        ("fish", "--debug-output x "),
        ("fish", "--profile x "),
        ("fish", "--profile-startup x "),
        ("fish", "--features x "),
        ("ash", "-o pipefail "),
        ("ash", "+o posix "),
        ("mksh", "-o posix "),
        ("mksh", "+o posix "),
        ("mksh", "-T /dev/tty2 "),
        ("yash", "-o posix "),
        ("yash", "+o posix "),
        ("posh", "-o posix "),
        ("posh", "+o posix "),
    )
    rm = ("rm", "-rf", "b")
    wrapper_texts = {f"{name}{positional.get(name, '')} rm -rf b": [rm] for name in wrapper_names}
    wrapper_texts["/usr/bin/sudo rm -rf b"] = [rm]
    wrapper_texts["timeout -s KILL 5 rm -rf b"] = [rm]
    flag_texts = {
        f"{name} {flag} v{positional.get(name, '')} rm -rf b": [rm]
        for name, flags in valued_flags.items()
        for flag in flags.split()
    }
    shell_texts = {
        f"{shell} {options}-c 'rm -rf b'": [(shell, *options.split(), "-c", "rm -rf b"), rm]
        for shell, options in (*((name, "") for name in shells), *shell_options)
    }
    pinned = {**wrapper_texts, **flag_texts, **shell_texts}
    wrong = {
        text: [s.words for s in tokens.split(text, DEFAULT_READER_LISTS)]
        for text, words in {**readings, **pinned}.items()
        if [s.words for s in tokens.split(text, DEFAULT_READER_LISTS)] != words
    }
    # The fields no default uses, on lists of their own: a wrapper of two words, the longest match
    # winning over its first word alone; `numbers`, skipped only when a number; a command option after
    # a positional word and before it; a shell's long command option, its value attached or the next word.
    own_lists = ReaderLists(
        (
            Wrapper(("uv",)),
            Wrapper(("uv", "run"), with_value=("--with", "-p")),
            Wrapper(("chrt",), with_value=("-T",), numbers=1),
            Wrapper(("flock",), positionals=1, command_flags=("-c", "--command")),
        ),
        (Shell("yash", command_flags=("--cmdline",)),),
    )
    rm_read = [rm]
    own_readings = {
        "uv run --with x rm -rf b": rm_read,
        "/bin/uv run -p 3.12 rm -rf b": rm_read,
        "uv run rm -rf b": rm_read,
        "uv tool rm -rf b": [("tool", "rm", "-rf", "b")],
        "chrt 10 rm -rf b": rm_read,
        "chrt -T 5 10 rm -rf b": rm_read,
        "chrt rm -rf b": rm_read,
        "chrt 10 20 rm -rf b": [("20", "rm", "-rf", "b")],
        "flock /tmp/l rm -rf b": rm_read,
        "flock /tmp/l -c 'rm -rf b'": rm_read,
        "flock -c 'rm -rf b'": rm_read,
        "flock /tmp/l --command 'rm -rf b' x": [("rm", "-rf", "b", "x")],
        "yash --cmdline 'rm -rf b'": [("yash", "--cmdline", "rm -rf b"), rm],
        "yash --cmdline='rm -rf b'": [("yash", "--cmdline=rm -rf b"), rm],
    }
    own_wrong = {
        text: [s.words for s in tokens.split(text, own_lists)]
        for text, words in own_readings.items()
        if [s.words for s in tokens.split(text, own_lists)] != words
    }
    wrong.update(own_wrong)
    assert not wrong, f"wrong: {wrong}"
    # The texts whose reading a slip could turn into an endless loop: a lone backtick, backtick pairs empty
    # or side by side, an escape in double quotes at the top level, before a heredoc operator and inside
    # `$(…)`, an escape outside quotes before one. Each runs through the gate within a bound, so a loop is
    # a red item, not a hang. An escaped quote closes nothing and opens nothing, a backslash before a
    # letter stays, and an operator inside the quote the escape leaves open drops no body.
    git_push = d1("", "git push", "-f", "git push -f")
    with H.bounded(shared_items.HANG_BOUND):
        passed("echo `x")
        passed("echo `a``b`", subcommands=3)
        asked("echo `` `git push -f`", git_push, subcommands=2)
        asked('echo "x\\"" ; git push -f', git_push, subcommands=2)
        asked('echo "a\\b"; git push -f', git_push, subcommands=2)
        passed('x "\\""<<EOF\nb\nEOF')
        passed("x \\' <<EOF\nb\nEOF")
        asked('x \\"" <<EOF\n"\ngit push -f\nEOF', git_push, subcommands=3)
        asked('x $(echo "\\"" ) $(git push -f)', git_push, subcommands=3)


# ---------------------------------------------------------------- the list-handles scan

PLAIN = "# T\n\n- one item\n- two items\n"
HANDLED = "# T\n\n- 1. one\n- 2. two\n\n- R1 a\n- R2 b\n\n- **Label:** a\n- `code` b\n- [link](x) c\n"


def lists_scan(files: dict[str, str], dials_patch: dict[str, object] | None = None) -> Result:
    root = prepared(dials_patch, files=files)
    return LISTS.run_gate("", args=["--scan", str(root)])


@item(20, "red→green: a plain list is red with L1 typed whole; handled lists are green")
def test_t20() -> None:
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
    expect(
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
    assert red_ok, f"differs (exit {red.code}):\n{red.stdout}"
    assert odd_ok, f"differs (exit {odd.code}):\n{odd.stdout}"


@item(21, "not a finding: fence, one item, nested, anchor, numbered list; the first plain item; a loose list")
def test_t21() -> None:
    """What is not a finding: a list in a fence, a one-item list, a nested list under a handled
    item, an anchor before the handle, a numbered list, a fence closed by a shorter one; and what
    is: the first item only, and a loose list — blank lines between items — as one list. Not a
    finding either: three items in a fence, a tilde fence with a backtick in its info string, a
    fence that ends the list before it, a bold handle, the default forms `A.`, `a.`, `a1.` and
    `Q-a`. A finding: the list after a backtick fence line with a backtick in its info string, and
    a list continued by a line indented with spaces or with a tab."""
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
    expect(loose, 2, "RED: docs/notes/b.md:3: list item without a handle — loose one", "stdout")
    fence = lists_scan({"docs/notes/c.md": "# T\n\n````\n- x\n- y\n```\n- z\n- w\n````\n"})
    expect(fence, 0, "GREEN: const-interaction: 4 document(s) examined", "stdout")
    # Not a finding: three plain items in a fence; a tilde fence whose info string holds a backtick; a fence
    # that closes the list before it; a bold handle; each default form of a letter, of a letter and digits
    # and of a key with a dash.
    green_text = (
        "# T\n\n```\n- a\n- b\n- c\n```\n\nText.\n\n~~~ a`b\n- x\n- y\n~~~\n\nText.\n\n"
        "- solo\n```\nx\n```\n- other\n\nText.\n\n- **a.** x\n- **b.** y\n\nText.\n\n"
        "- A. one\n- B. two\n\nText.\n\n- a. one\n- b. two\n\nText.\n\n- a1. one\n- a2. two\n\nText.\n\n"
        "- Q-a one\n- Q-b two\n"
    )
    expect(
        lists_scan({"docs/notes/d.md": green_text}),
        0,
        "GREEN: const-interaction: 4 document(s) examined for lists with 6 handle form(s), 4 Markdown file(s)"
        " scanned",
        "stdout",
    )
    # A finding: a backtick fence whose info string holds a backtick opens none, so the list after it counts;
    # a line indented by spaces or by a tab continues the list, so its second item joins the first.
    red_text = (
        "# T\n\n``` a`b\n- p\n- q\n\nText.\n\n- plain a\n  more\n- plain b\n\nText.\n\n"
        "- tab a\n\tmore\n- tab b\n"
    )
    red = lists_scan({"docs/notes/e.md": red_text})
    red_wanted = [
        "RED: docs/notes/e.md:4: list item without a handle — p",
        "RED: docs/notes/e.md:9: list item without a handle — plain a",
        "RED: docs/notes/e.md:15: list item without a handle — tab a",
        "RED: 3 finding(s) — 4 document(s) examined for lists with 6 handle form(s), 4 Markdown file(s)"
        " scanned",
    ]
    red_ok = red.code == 2 and red_lines(red.stdout) == red_wanted
    assert red_ok, f"exit {red.code}: {red.stdout}"
    assert ok, f"exit {result.code}: {result.stdout}"


@item(22, "territories: a negated pattern takes a document out; a README at the top is covered")
def test_t22() -> None:
    """Territories: a negated pattern takes a document out; the default covers every Markdown file. A
    repository with no dials file claims nothing, said by the scan's skip line."""
    out = lists_scan({"docs/notes/a.md": PLAIN}, dials_patch=own(territories=["*.md", "!docs/notes/**"]))
    expect(
        out,
        0,
        "GREEN: const-interaction: 3 document(s) examined for lists with 6 handle form(s), 4 Markdown"
        " file(s) scanned",
        "stdout",
    )
    top = lists_scan({"README.md": PLAIN})
    expect(top, 2, "RED: README.md:3: list item without a handle — one item", "stdout")
    # a repository with no dials file claims nothing: the scan's skip line, typed by hand
    bare = H.fresh_consumer()
    (bare.root / "constitution.yaml").unlink()
    bare.commit()
    skipped = LISTS.run_gate("", args=["--scan", str(bare.root)])
    skip_line = (
        f"GREEN: const-interaction: 0 documents examined — no constitution.yaml in {bare.root}: nothing is"
        " claimed\n"
    )
    skip_ok = skipped.code == 0 and skipped.stdout == skip_line and skipped.stderr == ""
    assert skip_ok, f"no dials file: exit {skipped.code}: {skipped.stdout}{skipped.stderr}"


@item(23, "the list scan as a hook is its own C12; a misinvocation exits 1")
def test_t23() -> None:
    """The scan's entry point as a hook is its own C12, typed by hand; a misinvocation exits 1."""
    root = prepared()
    hook = LISTS.run_gate(bash_json(root, "ls"))
    broken_first_line(
        hook,
        "BROKEN: this check has no hook mode: it scans a tree and judges no single write — fix: run it with"
        " --scan [<dir>]; the plugin wires it to no event",
    )
    mis = LISTS.run_gate("", args=["--bogus"])
    expect(mis, 1, "BROKEN: misinvocation:", "stderr")


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


@item(30, "session start: rules, verbosity line, zero line, a default dropped or replaced, the pairs")
def test_t30() -> None:
    """The rules first, whole; then nothing when the default list gates; the zero line when the
    dial is empty; the project's pairs numbered.

    The cases, once held by the acceptance table of the module document: the carrier of the rules,
    shipped and reading as written, never that a rule is followed (V3). The rules first and whole,
    the verbosity line after them, nothing more when the default list gates, each line whose size
    §6 of the module document states typed whole; the zero line typed by hand when the dial is
    empty; one line for each default dropped or replaced, none for an added entry; the pairs
    numbered and escaped. In the run that prints the rules and nothing more, every git call
    carries the git cap of the cost sub-slot of §6. The verbosity written out prints the same."""
    root = prepared()
    # the printer is a hook: each of its git calls has the hook's budget, logged before the call is made
    # with no clock, so that a slow git on a loaded machine cuts none of them
    patch, log = git_patch(SESSION, unclocked=True)
    plain = SESSION.run_gate(session_json(root), env=patch)
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
    # the one value written out says the same line as the key left out
    written = SESSION.run_gate(session_json(prepared(own(verbosity="triggered"))))
    written_ok = written.code == 0 and written.stdout == RULES + verbosity and written.stderr == ""
    assert written_ok, f"verbosity written out: exit {written.code}: {written.stdout[-200:]}{written.stderr}"
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
    # a dropped default and a replaced one are each named by one line, in the dials' order, the wrappers'
    # dial first; an added one, an empty list and no dial name nothing
    sudo_line = (
        "const-interaction: the wrapper sudo is dropped, so a command behind it is no longer examined —"
        " const-interaction.wrappers in constitution.yaml drops it\n"
    )
    nohup_line = (
        "const-interaction: the wrapper nohup is dropped, so a command behind it is no longer examined —"
        " const-interaction.wrappers in constitution.yaml drops it\n"
    )
    dash_line = (
        "const-interaction: the shell dash is dropped, so a command it is told to run is no longer examined"
        " — const-interaction.shells in constitution.yaml drops it\n"
    )
    sudo_replaced = (
        "const-interaction: the wrapper sudo is replaced, so its options are those written for it, not the"
        " defaults — const-interaction.wrappers in constitution.yaml replaces it\n"
    )
    bash_replaced = (
        "const-interaction: the shell bash is replaced, so its options are those written for it, not the"
        " defaults — const-interaction.shells in constitution.yaml replaces it\n"
    )
    drops = SESSION.run_gate(
        session_json(
            prepared(
                own(
                    wrappers=[
                        {"command": ["sudo"], "drop": True},
                        {"command": ["uv"], "with_value": ["-p"]},
                        {"command": ["nohup"], "drop": True},
                    ],
                    shells=[
                        {"command": ["dash"], "drop": True},
                        {"command": ["elvish"], "command_flags": ["-c"]},
                    ],
                )
            )
        )
    )
    drops_ok = drops.code == 0 and drops.stdout == RULES + verbosity + sudo_line + nohup_line + dash_line
    zero_drop = SESSION.run_gate(
        session_json(prepared(own(destructive=[], wrappers=[{"command": ["sudo"], "drop": True}])))
    )
    zero_drop_ok = zero_drop.stdout == RULES + verbosity + zero + "\n" + sudo_line
    # the drop and replace lines stand before the pairs
    ordered = SESSION.run_gate(
        session_json(
            prepared(
                own(
                    wrappers=[{"command": ["sudo"], "drop": True}],
                    boundary_examples=[{"violates": "an essay", "complies": "the word"}],
                )
            )
        )
    )
    ordered_ok = ordered.stdout == RULES + verbosity + sudo_line + (
        "Boundary examples of this project (const-interaction.boundary_examples), each violates / complies:\n"
        "1. an essay / the word\n"
    )
    replaced = SESSION.run_gate(
        session_json(
            prepared(
                own(
                    wrappers=[{"command": ["sudo"]}],
                    shells=[{"command": ["bash"], "command_flags": ["-c"]}],
                )
            )
        )
    )
    replaced_ok = replaced.code == 0 and replaced.stdout == RULES + verbosity + sudo_replaced + bash_replaced
    # drops and replacements together, each as its entry stands in its list, the added entries silent
    mixed = SESSION.run_gate(
        session_json(
            prepared(
                own(
                    wrappers=[
                        {"command": ["nohup"], "drop": True},
                        {"command": ["uv"], "with_value": ["-p"]},
                        {"command": ["sudo"], "with_value": ["-u"]},
                    ],
                    shells=[
                        {"command": ["elvish"], "command_flags": ["-c"]},
                        {"command": ["bash"], "command_flags": ["-c"]},
                        {"command": ["dash"], "drop": True},
                    ],
                )
            )
        )
    )
    mixed_ok = mixed.stdout == RULES + verbosity + nohup_line + sudo_replaced + bash_replaced + dash_line
    quiet = SESSION.run_gate(
        session_json(
            prepared(
                own(
                    wrappers=[{"command": ["uv"]}],
                    shells=[{"command": ["elvish"], "command_flags": ["-c"]}],
                )
            )
        )
    )
    empty_lists = SESSION.run_gate(session_json(prepared(own(wrappers=[], shells=[]))))
    quiet_ok = quiet.stdout == RULES + verbosity and empty_lists.stdout == RULES + verbosity
    assert drops_ok, f"got: {drops.stdout[-500:]}"
    assert zero_drop_ok, f"got: {zero_drop.stdout[-400:]}"
    assert ordered_ok, f"got: {ordered.stdout[-500:]}"
    assert replaced_ok, f"got: {replaced.stdout[-500:]}"
    assert mixed_ok, f"got: {mixed.stdout[-700:]}"
    assert quiet_ok, f"got: {quiet.stdout[-300:]}"
    assert long_ok, f"got: {long_pairs.stdout[-400:]}"
    assert plain_ok, f"got: {plain.stdout[-200:]}{plain.stderr}"
    hook_budget(git_timeouts(log))
    assert empty_ok, f"got: {empty.stdout[-300:]}"
    assert pairs_ok, f"got: {pairs.stdout[-300:]}"


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


@item(31, "session start: no dials file, no repository, malformed dials, an argument")
def test_t31() -> None:
    """No dials file and no repository (roots and folders whose names hold `:` too), the first also from a
    subfolder of the root: the shared skips said in the module's words; malformed dials:
    exit 1 with the shared C4 first on stderr and the rules still on stdout; an argument: exit 1."""
    root = colon_root()
    no_dials = SESSION.run_gate(session_json(root))
    no_dials_line = (
        f"const-interaction: no constitution.yaml in {root} — the destructive-command gate examines nothing"
        " there until the file exists (a file that holds only module_prefix: const- is enough for the"
        " default list)"
    )
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
    arg_wanted = (  # typed by hand, the whole stderr
        "BROKEN: misinvocation: unexpected argument --scan — fix: session-start takes no arguments; it reads"
        " one SessionStart event on stdin\n"
        "BROKEN: the session-start line could not be printed — the gate's state is unknown\n"
    )
    arg_ok = arg.code == 1 and arg.stderr == arg_wanted
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
        " destructive-command gate examines nothing there until the file exists (a file that holds only"
        " module_prefix: const- is enough for the default list)\n"
    )
    weird_repo_ok = weird_no_repo.stdout == RULES + verbosity + (
        f"const-interaction: {weird_parent}/l" + WEIRD_DIR_SHOWN + " is not inside a git repository — the"
        " destructive-command gate examines nothing there\n"
    )
    # the folder is what the reader opens: whole, escaped, over 80 characters
    assert weird_dials_ok, f"got: {weird_no_dials.stdout[-400:]}"
    assert weird_repo_ok, f"got: {weird_no_repo.stdout[-400:]}"
    assert no_dials_ok, f"got: {no_dials.stdout[-300:]}"
    assert from_sub_ok, f"got: {from_sub.stdout[-300:]}"
    assert no_repo_ok, f"got: {no_repo.stdout[-300:]}"
    assert bad_ok, f"got {bad.code}: {bad.stderr[:300]}"
    assert arg_ok, f"got {arg.code}: {arg.stderr[:200]}"


@item(32, "the rules text: under the cap, of the stated size, lettered a–i")
def test_t32() -> None:
    """The rules text: under the platform's cap, of the size the module document states, every rule
    lettered, and the hook prints it before python3 is looked for.

    The size is read from the document's sentence "prints the rules text of N characters"."""
    module_doc = (MODULE_ROOT / "MODULE.md").read_text(encoding="utf-8")
    match = re.search(r"prints the rules text of ([0-9,]+) characters", module_doc)
    stated = int(match.group(1).replace(",", "")) if match else -1
    letters = re.findall(r"^([a-z])\. ", RULES, re.M)
    ok = len(RULES) < 10_000 and stated == len(RULES) and letters == list("abcdefghi")
    assert ok, f"{len(RULES)} characters, document states {stated}; letters {letters}"


@item(33, "the printer's absence paths: PyYAML missing is C2, python3 missing is C1, the rules kept")
def test_t33() -> None:
    """The printer's absence paths: PyYAML missing is C2 first on stderr with the printer's closing
    line, the rules still on stdout; python3 missing is C1, the rules still printed first."""
    shadow = H.scratch_dir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    root = prepared()
    no_yaml = SESSION.run_gate(session_json(root), env={"PYTHONPATH": str(shadow)})
    c2 = (
        "BROKEN: const-interaction needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{PLUGIN_ROOT / 'requirements.txt'}' — until then the gate's state is not said at session start"
    )
    broken_first_line(no_yaml, c2)
    # typed by hand: the printer's closing line, the whole stderr after C2
    closing = "BROKEN: the session-start line could not be printed — the gate's state is unknown"
    yaml_ok = no_yaml.stderr == f"{c2}\n{closing}\n" and no_yaml.stdout == RULES
    assert yaml_ok, f"exit {no_yaml.code}, stdout {no_yaml.stdout[:80]!r}: {no_yaml.stderr}"
    bin_dir = H.scratch_dir()
    (bin_dir / "sh").symlink_to(H.sh)
    for tool in ("cat", "dirname"):
        (bin_dir / tool).symlink_to(shutil.which(tool) or tool)
    no_python = SESSION.run_gate(session_json(root), env={"PATH": str(bin_dir)})
    c1 = (
        "BROKEN: const-interaction needs python3 — fix: install Python 3.12 or newer"
        " (https://www.python.org/downloads/) — until then the gate's state is not said at session start"
    )
    broken_first_line(no_python, c1)
    py_ok = no_python.stdout == RULES
    assert py_ok, f"exit {no_python.code}, stdout {no_python.stdout[:80]!r}: {no_python.stderr}"


# ---------------------------------------------------------------- the plugin's files


@item(40, "the hooks file's shape")
def test_t40() -> None:
    """The hooks file's shape: a SessionStart handler with no matcher and a PreToolUse handler on
    Bash, exec form, the placeholder in args, timeouts."""
    hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
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
    assert ok, f"bad: {hooks}"


@item(41, "the manifest names the plugin; the install note's example accepted")
def test_t41() -> None:
    """The manifest names the plugin; the install note's calibration example is accepted as it stands."""
    install = (PLUGIN_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    example = re.search(r"```yaml\n(.*?)```", install, re.S)
    accepted = False
    if example:
        loaded = yaml.safe_load(example.group(1))
        result, _ = gate_on(command("ls"), dials_patch=loaded)
        accepted = result.code == 0
    ok = manifest["name"] == NAMESPACE and accepted
    assert ok, f"manifest {manifest['name']!r}; accepted {accepted}"


SHELL_CLOSING = "until then shell commands pass unchecked"
LISTS_CLOSING = "until then no list is scanned"


@item(42, "C1, C2, C14 and C15 of the shell gate and of the list check close with each gate's own clause")
def test_t42() -> None:
    """Each gate's install-failure lines close with its own clause, never the write gates' "until then
    Markdown writes pass unchecked" — the shell gate's `until then shell commands pass unchecked`, the list
    check's `until then no list is scanned`: C1 (no python3, the POSIX entry), C2 (PyYAML missing, the
    shell gate in its hook mode, the list check in its scan), C14 (an interpreter below the floor, run by
    a version it is told it has) and C15 (the shared package missing for python3), each first line typed
    whole; and each gate's two entry files hold its clause exactly four times, once per entry text (C1, C14,
    C15) and once as the clause the Python entry file hands to the version check of the shared package (C16,
    C17), and "Markdown writes" nowhere."""
    root = prepared()
    problems: list[str] = []
    tools = H.scratch_dir()  # a PATH holding only sh and dirname: no python3
    for tool in ("sh", "dirname"):
        found = shutil.which(tool)
        assert found, tool
        (tools / tool).symlink_to(found)
    shadow = H.scratch_dir()  # PyYAML hidden: the shared C2, its closing clause the identity's
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    lowered = (  # an entry file run as an interpreter of 3.11 would run it
        "import sys; sys.version_info = (3, 11, 0); path = sys.argv[1]; "
        "exec(compile(open(path).read(), path, 'exec'), {'__name__': '__main__', '__file__': path})"
    )
    gates: tuple[tuple[str, Harness, str, str, list[str]], ...] = (
        ("shell gate", H, SHELL_CLOSING, bash_json(root, "ls"), []),
        ("list check", LISTS, LISTS_CLOSING, "", ["--scan", str(root)]),
    )
    for name, harness, clause, stdin, args in gates:

        def line_of(label: str, result: Result, whole: str, name: str = name) -> None:
            first = result.stderr.splitlines()[0] if result.stderr else ""
            if result.code != 1 or first != whole or "Markdown writes" in result.stdout + result.stderr:
                problems.append(f"{name} {label}: exit {result.code}: {result.stderr.strip()[:400]}")

        line_of(
            "C1",
            harness.run_gate(stdin, args, env={"PATH": str(tools)}),
            "BROKEN: const-interaction needs python3 — fix: install Python 3.12 or newer"
            f" (https://www.python.org/downloads/) — {clause}",
        )
        line_of(
            "C2",
            harness.run_gate(stdin, args, env={"PYTHONPATH": str(shadow)}),
            "BROKEN: const-interaction needs PyYAML — fix: run: python3 -m pip install -r"
            f" '{PLUGIN_ROOT / 'requirements.txt'}' — {clause}",
        )
        line_of(
            "C14",
            harness.run_gate(stdin, args, command=[sys.executable, "-c", lowered, str(harness.entry)]),
            "BROKEN: const-interaction needs Python 3.12 or newer, found 3.11 — fix: install a current"
            f" Python 3 (https://www.python.org/downloads/) and put it first on PATH — {clause}",
        )
        line_of(
            "C15",
            harness.run_gate(  # the harness's shared folder left out, and no site-packages
                stdin,
                args,
                env={"PYTHONPATH": ""},
                command=[sys.executable, "-S", str(harness.entry)],
                shared=False,
            ),
            "BROKEN: const-interaction needs the Python package constitution-layer-kit 2.0.0 or a later 2.x"
            " release, and python3 cannot import it — fix: install it for python3 as"
            f" {PLUGIN_ROOT / 'INSTALL.md'} says — {clause}",
        )
        sources = "".join(
            (SCRIPTS / entry).read_text(encoding="utf-8")
            for entry in (harness.wrapper.name, harness.entry.name)
        )
        if sources.count(clause) != 4 or "Markdown writes" in sources:
            problems.append(
                f"{name} entry files: the clause {sources.count(clause)} times, wanted 4; or Markdown writes"
            )
    assert not problems, "; ".join(problems)


# ------------------------------------------------------------------ the effect report (items 43 on)
# The rules W1 to W4 of the module's section 13, each run through `effect-report.sh` over transcripts made
# by hand and, for W1 and W3, over a git history made in a scratch repository. The lines are typed by hand.

EFFECT_AT = "2026-11-03T10:00:00.000Z"
EFFECT = SCRIPTS / "effect-report.sh"
GATE_COMMAND = "sh ${CLAUDE_PLUGIN_ROOT}/scripts/check-destructive.sh"
ASK_WHY = (
    "RED: destructive command: '{command}' matches the entry {entry}\n"
    "  why: it cannot be undone\n  fix: use the reversible way\nRED: 1 finding(s) — 1 command examined"
)


def tr_tool(sid: str, cwd: Path, call_id: str, name: str, **given: object) -> str:
    block = {"type": "tool_use", "id": call_id, "name": name, "input": given}
    return tr_line("assistant", sid, cwd, EFFECT_AT, message={"role": "assistant", "content": [block]})


def tr_say(sid: str, cwd: Path, text: str) -> str:
    block = {"type": "text", "text": text}
    return tr_line("assistant", sid, cwd, EFFECT_AT, message={"role": "assistant", "content": [block]})


def tr_ask(
    sid: str, cwd: Path, call_id: str, command: str, entry: str, script: str = "check-destructive.sh"
) -> str:
    """The run of the shell gate that asked, as Claude Code 2.1.295 records it: a `hook_success` attachment
    whose standard output holds the verdict."""
    reason = ASK_WHY.format(command=command, entry=entry)
    answer = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }
    done = {
        "type": "hook_success",
        "hookName": "PreToolUse:Bash",
        "toolUseID": call_id,
        "hookEvent": "PreToolUse",
        "stdout": json.dumps(answer) + "\n",
        "exitCode": 0,
        "command": GATE_COMMAND.replace("check-destructive.sh", script),
    }
    return tr_line("attachment", sid, cwd, EFFECT_AT, attachment=done)


def tr_result(sid: str, cwd: Path, call_id: str, text: str, error: bool) -> str:
    """The result of a call: an error where the user refused it at the prompt or the platform refused it."""
    block = {"type": "tool_result", "tool_use_id": call_id, "content": text, "is_error": error}
    return tr_line("user", sid, cwd, EFFECT_AT, message={"role": "user", "content": [block]})


NO_PROMPT = "The user doesn't want to proceed with this tool use. The tool use was rejected."


def effect_lines(
    root: Path, sessions: dict[str, list[str]], env: dict[str, str] | None = None, *flags: str
) -> list[str]:
    """The lines of the report over the sessions, one transcript each; the report must exit 0."""
    folder = H.scratch_dir()
    for name, lines in sessions.items():
        (folder / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = H.run_gate(
        "",
        args=["--transcripts", str(folder), *flags],
        env={
            "CLAUDE_PLUGIN_DATA": str(H.scratch_dir()),
            **(env or fake_claude(H.scratch_dir(), "echo '[]'\n")),
        },
        command=[H.sh, str(EFFECT)],
        cwd=root,
    )
    assert result.code == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def w2_moments(
    root: Path, sessions: dict[str, list[str]], gone: Sequence[str] = (), raw: dict[str, bytes] | None = None
) -> list[tuple[str, str, str]]:
    """W2's moments over the sessions, one transcript each, as (session, outcome, way): the rule's own code
    run in this process on the sessions as the report reads them. Each moment is told apart, so outcomes
    that trade places between sessions cannot keep a total. The transcripts named in `gone` are deleted
    once read; `raw` adds bytes to the end of a transcript."""
    folder = H.scratch_dir()
    read = []
    for name, lines in sorted(sessions.items()):
        path = folder / f"{name}.jsonl"
        path.write_bytes(("\n".join(lines) + "\n").encode("utf-8") + (raw or {}).get(name, b""))
        session = read_transcript(path)
        assert session is not None, name
        read.append(session)
    for name in gone:
        (folder / f"{name}.jsonl").unlink()
    history = History(
        root, frozenset({"check-destructive.sh"}), tuple(read), (), "", NAMESPACE, "constitution.yaml"
    )
    return [(m.session, str(m.outcome), str(m.way) if m.way else "") for m in effect_rules.after_ask(history)]


@item(
    43, "W1: a change of the module's dials is applied, or bypassed by B2 when a gate or a territory loosens"
)
def test_effect_switch_off() -> None:
    """Seven commits of the dials file, each changing this module's namespace: severity block (applied);
    the destructive list cut to one entry, the defaults gone (bypassed); an entry added (applied); severity
    warn (bypassed); severity back to block, with the territories narrowed to one folder, a pattern of the
    default gone (bypassed); a negated pattern added (bypassed); a handle form added (applied). The plugin
    list names no plugin. Then seven changes judged alone by the module's predicate: an entry replaced by a
    flagless entry of another command, narrowed to other flags, or a flagless one narrowed to a flag,
    loosens; a namespace the reader refuses before, after or on both sides, or a negated pattern removed,
    does not."""
    consumer = H.fresh_consumer()
    rm = {"command": ["rm"], "flags": ["-r"], "teach": "t", "alternative": "a"}
    reset = {"command": ["git", "reset"], "flags": ["--hard"], "teach": "t", "alternative": "a"}
    steps = [
        own(severity="block"),
        own(destructive=[rm]),
        own(destructive=[rm, reset]),
        own(destructive=[rm, reset], severity="warn"),
        own(destructive=[rm, reset], territories=["docs/**"]),
        own(destructive=[rm, reset], territories=["docs/**", "!docs/drafts/**"]),
        own(destructive=[rm, reset], territories=["docs/**", "!docs/drafts/**"], handles=["^[0-9]+\\."]),
    ]
    for step in steps:
        consumer.write("constitution.yaml", dials_text(step))
        consumer.commit()
    found = effect_lines(consumer.root, {})
    assert "  W1 (pattern): 7 moment(s): 3 applied, 4 bypassed, 0 missed — B2 4" in found, found
    # Each change judged alone, by the module's own predicate of a loosened dial: an entry replaced by a
    # flagless entry of another command, narrowed to other flags, or a flagless one narrowed to a flag,
    # loosens; a namespace the reader refuses on either side, or a negated pattern removed, does not.
    dropdb = {"command": ["dropdb"], "teach": "t", "alternative": "a"}
    rm_f = {**rm, "flags": ["-f"]}
    refused: dict[str, object] = {"marker": "x"}
    changes: tuple[tuple[str, dict[str, object], dict[str, object], bool], ...] = (
        ("rm replaced by a flagless dropdb", {"destructive": [rm]}, {"destructive": [dropdb]}, True),
        ("rm -r narrowed to rm -f", {"destructive": [rm]}, {"destructive": [rm_f]}, True),
        (
            "dropdb narrowed to -x",
            {"destructive": [dropdb]},
            {"destructive": [{**dropdb, "flags": ["-x"]}]},
            True,
        ),
        ("refused before", refused, {"destructive": [rm]}, False),
        ("refused after", {"destructive": [rm]}, refused, False),
        ("refused on both sides", refused, refused, False),
        (
            "a negated pattern removed",
            {"territories": ["*.md", "!docs/**"]},
            {"territories": ["*.md"]},
            False,
        ),
    )
    wrong = [name for name, old, new, loose in changes if effect_rules.loosened(old, new) is not loose]
    assert not wrong, f"judged wrongly: {wrong}"


@item(
    44,
    "W2: after an ask the same command again is applied, another route to the same target is bypassed by B3",
)
def test_effect_after_ask() -> None:
    """Each session holds an ask of the shell gate, as the platform records it: the ask is recorded as a
    `hook_success` attachment or as a refusal in the tool result alike, and a second ask is no moment. The ask
    refused at the prompt,
    then the same command again: applied. Refused, then `find build -delete`, which the gate did not ask for:
    bypassed by B3, as is a refused `git push --force origin main`, a refusal recorded as a hook error, then
    `git push -f origin main`. No moment: a human turn first; an ask the user accepted, whose next command
    names the same target; a refused ask followed by commands that name nothing of it; an ask of another
    plugin's script; a command that the gate asked for and that is another command.

    Each moment is then told apart, by the rule's own code run in this process, so two outcomes that
    trade places keep no total. Twenty more sessions: the target from a quoted string, from the first of
    two commands, of two words, of two letters; `..`, `--`, an option and one letter are no target; the
    entry's words with the asked option, at the end of the words too; a Read call between ends nothing;
    an ask with no call, or no result; an accepted ask found ran past a line that is no JSON, a bad
    byte and another call's result in the same line; a later ask after an accepted one; an accepted
    ask whose transcript is gone."""
    root = H.fresh_consumer().root
    rm = ("rm -rf build", "rm with -r")
    push = ("git push --force origin main", "git push with --force")

    def asked(sid: str, command: str, entry: tuple[str, str], accepted: bool = False) -> list[str]:
        return [
            tr_tool(sid, root, "a", "Bash", command=command),
            tr_ask(sid, root, "a", entry[0], entry[1]),
            tr_result(sid, root, "a", "done" if accepted else NO_PROMPT, not accepted),
        ]

    refused_text = (
        "PreToolUse:Bash hook error: [sh /x/plugin/scripts/check-destructive.sh]: RED: destructive command:"
        " 'git push --force origin main' matches the entry git push with --force\\n  why: w\\n  fix: f"
        "\n\nThis hook comes from the const-interaction@fixture-marketplace plugin."
    )
    sessions = {
        "a": [*asked("a", rm[0], rm), tr_tool("a", root, "b", "Bash", command="rm -rf build")],
        "b": [*asked("b", rm[0], rm), tr_tool("b", root, "b", "Bash", command="find build -delete")],
        "c": [
            tr_tool("c", root, "a", "Bash", command=push[0]),
            tr_result("c", root, "a", refused_text, True),
            tr_tool("c", root, "b", "Bash", command="git push -f origin main"),
        ],
        "d": [
            *asked("d", rm[0], rm),
            tr_turn("d", root, EFFECT_AT, "yes"),
            tr_tool("d", root, "b", "Bash", command="find build -delete"),
        ],
        "e": [*asked("e", rm[0], rm, accepted=True), tr_tool("e", root, "b", "Bash", command="ls build")],
        "f": [
            *asked("f", rm[0], rm),
            tr_tool("f", root, "b", "Bash", command="git status"),
            tr_tool("f", root, "c", "Read", file_path="build/x"),
            tr_tool("f", root, "d", "Bash", command="ls dist"),
        ],
        "g": [
            tr_tool("g", root, "a", "Bash", command=rm[0]),
            tr_ask("g", root, "a", rm[0], rm[1], script="check-other.sh"),
            tr_result("g", root, "a", NO_PROMPT, True),
            tr_tool("g", root, "b", "Bash", command="find build -delete"),
        ],
        "h": [
            *asked("h", rm[0], rm),
            tr_tool("h", root, "b", "Bash", command="rm -rf dist"),
            tr_ask("h", root, "b", "rm -rf dist", rm[1]),
            tr_result("h", root, "b", NO_PROMPT, True),
        ],
    }
    found = effect_lines(root, sessions)
    assert "  W2 (pattern): 3 moment(s): 1 applied, 2 bypassed, 0 missed — B3 2" in found, found
    applied, bypassed = ("applied", ""), ("bypassed", "B3")
    each = w2_moments(root, sessions)
    assert each == [("a", *applied), ("b", *bypassed), ("c", *bypassed)], each

    def later(sid: str, asked_command: str, entry: tuple[str, str], *commands: str) -> list[str]:
        """A refused ask, then the later commands, each its own call."""
        calls = [tr_tool(sid, root, f"l{n}", "Bash", command=one) for n, one in enumerate(commands)]
        return [*asked(sid, asked_command, entry), *calls]

    def ran_twice(sid: str, *between: str) -> list[str]:
        """An ask the user accepted, the lines given after its call, then the same command again."""
        return [
            tr_tool(sid, root, "a", "Bash", command=rm[0]),
            tr_ask(sid, root, "a", rm[0], rm[1]),
            *between,
            tr_tool(sid, root, "b", "Bash", command=rm[0]),
        ]

    other = {"type": "tool_result", "tool_use_id": "o", "content": NO_PROMPT, "is_error": True}
    ours = {"type": "tool_result", "tool_use_id": "a", "content": "done", "is_error": False}
    both = tr_line("user", "pair", root, EFFECT_AT, message={"role": "user", "content": [other, ours]})
    more = {
        # the target: a quoted string is split into words; the words after the entry's words in the first
        # command that holds them; `..`, `--`, options and one letter are no target, two letters are one
        "dots": later("dots", "rm -rf ..", rm, "cd .."),
        "quoted": later("quoted", "bash -c 'rm -rf build'", rm, "find build -delete"),
        "two": later("two", "rm -rf build dist", rm, "find build -delete"),
        "segs": later("segs", "rm -rf build; rm -rf dist", rm, "find build -delete"),
        "dashes": later("dashes", "rm -r -- build", rm, "rm -- other"),
        "copy": later("copy", "rm -rf build", rm, "cp -rf a b"),
        "short": later("short", "rm -rf a", rm, "ls a"),
        "db": later("db", "rm -rf db", rm, "find db -delete"),
        # no target: the entry's words with an option the asked command had, at the end of the words too;
        # without the entry's words, or without the option, it names nothing
        "form": later("form", "git push --force", push, "git push origin main --force"),
        "end": later("end", "git push --force", push, "echo --force; git push"),
        "other": later("other", "git push --force", push, "ls --force"),
        "plain": later("plain", "git push --force", push, "git push origin main"),
        # a call that is no shell command, between, ends nothing
        "read": [
            *asked("read", rm[0], rm),
            tr_tool("read", root, "r", "Read", file_path="build/x"),
            tr_tool("read", root, "b", "Bash", command="find build -delete"),
        ],
        # an ask with no call is no moment; an ask with no result did not run, and the same command again
        # is applied; an accepted ask is found ran past a line that is no JSON, a bad byte in the file, and
        # another call's result in the same line; a later ask is examined after an accepted one
        "noc": [tr_ask("noc", root, "z", rm[0], rm[1])],
        "nores": ran_twice("nores"),
        "nojson": ran_twice(
            "nojson", "a tool_result line that is no JSON", tr_result("nojson", root, "a", "done", False)
        ),
        "bad": ran_twice("bad", tr_result("bad", root, "a", "done", False)),
        "pair": ran_twice("pair", both),
        "after": [
            *asked("after", rm[0], rm, accepted=True),
            tr_tool("after", root, "c", "Bash", command="rm -rf dist"),
            tr_ask("after", root, "c", "rm -rf dist", rm[1]),
            tr_result("after", root, "c", NO_PROMPT, True),
            tr_tool("after", root, "d", "Bash", command="rm -rf dist"),
        ],
        # an accepted ask whose transcript cannot be read again is taken as not run
        "gone": ran_twice("gone", tr_result("gone", root, "a", "done", False)),
    }
    found_more = w2_moments(root, more, gone=["gone"], raw={"bad": b"\xff\n"})
    wanted_more = [
        ("after", *applied),
        ("db", *bypassed),
        ("end", *bypassed),
        ("form", *bypassed),
        ("gone", *applied),
        ("nores", *applied),
        ("quoted", *bypassed),
        ("read", *bypassed),
        ("segs", *bypassed),
        ("two", *bypassed),
    ]
    assert found_more == wanted_more, found_more


@item(45, "W3: the list scan on each commit of main in a throwaway clone: green applied, red bypassed by B4")
def test_effect_escape() -> None:
    """Three commits of the main branch: the fixture, one that adds a document with a list of two plain
    items (red, bypassed), and one that gives the items handles (green, applied). The scan of the current
    plugin runs on a shared clone at each commit, outside the project, which stays as it was."""
    consumer = H.fresh_consumer()
    consumer.write("docs/notes/list.md", "# List\n\n- first thing\n- second thing\n")
    consumer.commit()
    consumer.write("docs/notes/list.md", "# List\n\n- A1 first thing\n- A2 second thing\n")
    consumer.commit()
    root = consumer.root
    before = subprocess.run(
        ["git", "status", "--porcelain", "--ignored"], cwd=root, capture_output=True, text=True
    )
    names = sorted(p.name for p in root.iterdir())
    found = effect_lines(root, {})
    assert "  W3 (pattern): 3 moment(s): 2 applied, 1 bypassed, 0 missed — B4 1" in found, found
    after = subprocess.run(
        ["git", "status", "--porcelain", "--ignored"], cwd=root, capture_output=True, text=True
    )
    assert (after.stdout, sorted(p.name for p in root.iterdir())) == (before.stdout, names)


@item(46, "W4: the last reply before each human turn is a moment for the reader, who judges it with --reader")
def test_effect_reader_rule() -> None:
    """A session of three human turns holds two replies before the first, one before the second, a call and
    no reply before the third, and a reply after the third. The moments are the second text before the first
    turn and the one before the second turn: two. Without `--reader` they are counted and not judged; a fake
    reader that answers APPLIED judges them, and is given the rules a to i of the start text, taken from the
    module's `rules.txt`, after the sentence of W4 typed by hand. Without `rules.txt` the sentence alone
    is given. The lines are typed by hand."""
    root = H.fresh_consumer().root
    sid = "s46"
    lines = [
        tr_turn(sid, root, EFFECT_AT, "one"),
        tr_say(sid, root, "A first reply."),
        tr_say(sid, root, "The last reply of the first turn."),
        tr_turn(sid, root, EFFECT_AT, "two"),
        tr_say(sid, root, "The reply of the second turn."),
        tr_turn(sid, root, EFFECT_AT, "three"),
        tr_tool(sid, root, "t", "Bash", command="ls"),
        tr_say(sid, root, "A reply after the last turn."),
    ]
    plain = effect_lines(root, {sid: lines})
    assert "  W4 (reader): 2 moment(s), not judged — run again with --reader to judge them" in plain, plain
    env, calls = reader_fake(H.scratch_dir(), "claude.ai", json.dumps({"result": "APPLIED"}))
    judged = effect_lines(root, {sid: lines}, env, "--reader")
    assert "  W4 (reader): 2 moment(s): 2 applied, 0 bypassed, 0 missed" in judged, judged
    asked = H.scratch_dir()
    spy = fake_claude(
        asked,
        f'echo "$*" >> {asked}/prompts\ncase "$1" in\n  --version) echo "9.9.9 (Claude Code)" ;;\n'
        '  auth) echo \'{"authMethod": "claude.ai"}\' ;;\n  -p) echo \'{"result": "APPLIED"}\' ;;\nesac\n',
    )
    effect_lines(root, {sid: lines}, spy, "--reader")
    prompts = (asked / "prompts").read_text(encoding="utf-8") if (asked / "prompts").exists() else ""
    # typed by hand: the sentence of W4, then the rules a to i, each a line of `rules.txt` after its first
    sentence = (
        "The last reply before each message of the user follows the rules a to i of the start text, the"
        " answer shape and the assumptions among them"
    )
    rules_text = sentence + ":\n" + "\n".join(RULES.splitlines()[1:])
    assert (
        "a. Classify the shape the question asks for" in prompts
        and "i. Write chat in plain language" in prompts
        and rules_text in prompts
    ), prompts
    # without `rules.txt` the reader is given the sentence alone, closed by a full stop
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(effect_rules, "RULES_FILE", H.scratch_dir() / "rules.txt")
        alone = effect_rules._reader_text()  # noqa: SLF001
    assert alone == sentence + ".", alone


# ---------------------------------------------------------------- the runner

RED_LONG = "git push --force " + "x" * (12_000 - len("git push --force "))
SUBJECT = Subject(
    harness=H,
    gate_on=gate_on,
    own=own,
    valid=command("git status"),
    red=command("git push --force origin main"),
    red_finding=d1("git push --force origin main", "git push", "--force"),
    green=shared.g1_green_event(messages.g1_command_passed(ENTRIES, 1)),
    territory=["docs/notes/**"],
    claim=claim,
    resolves_policies=False,
    judges_envelopes=False,
    event="Bash",
    ask=True,
    long_value=command(RED_LONG),
    pattern_dial=PatternDial("territories", lambda pattern: own(territories=[pattern])),
    effect="effect-report.sh",  # no `effect_reader`: its reader rule W4 has a moment for the last reply
    # before each human turn, and the shared items about a reader rule need a moment for each human turn
)
