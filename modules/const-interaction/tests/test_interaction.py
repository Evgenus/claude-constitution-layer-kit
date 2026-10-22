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
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
import yaml
from acceptance import broken_first_line, expect, failure_of, item
from constitution_layer_kit import identity
from constitution_layer_kit import messages as shared
from constitution_layer_kit.model import Broken, Finding
from consumer import Consumer
from harness import Harness, Result, Write, ask_reason, bash_json, event_json, red_lines
from interaction_gate import messages, start, tokens
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
from test_shared_items import PatternDial, Subject, git_patch, git_timeouts, hook_budget

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"
PLUGIN_ROOT = SCRIPTS.parent
MODULE_ROOT = PLUGIN_ROOT.parent

identity.declare(start.GATE)  # the expected messages are built by the same functions the gate uses
identity.declare_dials_file("constitution.yaml")  # the expected messages name the file the gate reads
# — and each is also typed by hand at least once in these fixtures (rule 14 of the template's §6)
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
    pair(
        lambda: asked(text, d1(text, "git reset", "--hard", "git reset --hard HEAD~1"), subcommands=2),
        lambda: passed('bash -c "git reset --soft HEAD~1"', subcommands=2),
    )()


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
    `kubectl -n prod get pods` and `kubectl -n prod -- delete pod x` pass.
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
    flag `-r`; the false prompt `kubectl -n delete get pods` is pinned as asking.

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
    expect(mis, 1, "BROKEN: misinvocation: --command applies to --scan", "stderr")
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
        (
            own(wrappers=[{"command": ["uv"], "with_value": ["u"]}]),
            w + "entry 1: with_value holds 'u', which does not start with '-', so it is no option — fix:"
            " write it as the command line has it, with its dash, such as -u or --user",
        ),
        (  # a wrapper's options are the words that start with '-': a '+' never matches
            own(wrappers=[{"command": ["uv"], "command_flags": ["+c"]}]),
            w + "entry 1: command_flags holds '+c', which does not start with '-', so it is no option — fix:"
            " write it as the command line has it, with its dash, such as -u or --user",
        ),
        (
            own(shells=[{"command": ["elvish"], "with_value": ["o"]}]),
            s + "entry 1: with_value holds 'o', which starts with neither '-' nor '+', so it is no option —"
            " fix: write it as the command line has it, with its sign, such as -o, +o or --rcfile",
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
    `territories` empty, a malformed pair, a `verbosity` outside its one value. The list in its
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
        (
            own(boundary_examples=[{"violates": "x"}]),
            prefix
            + "const-interaction.boundary_examples must be a list of pairs {violates: <text>, complies:"
            ' <text>} — fix: write one pair per "- " item with exactly those two fields, or leave the key'
            " out",
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
    assert ok, f"differs:\n{reason}"
    # the command, words and flag only point: cut at 80, then escaped; teach and alternative whole
    assert odd_ok, f"differs:\n{odd_reason}"


@item(13, "the readings typed by hand: every default wrapper, flag and shell, an entry's own")
def test_t13() -> None:
    """The tokeniser's readings, each typed by hand.

    The cases, once held by the acceptance table of the module document: every operator, a quoted
    operator, backticks, `env -i FOO=1 nice -n 5`, a quoted verb, `--git-dir=`, `sh -c` and what
    follows it, an unbalanced quote, a bare subshell, `sudo -u`, a continuation line, `&>`, a
    brace group, an assignment alone.

    75 readings in all, among them git's options kept in the words, `exec -a x`, each wrapper
    added on 2026-10-05 read to its command, `flock -c` before and after the lock file, each
    added shell with its string, a shell's strings (`-ce`, `-cl`, `-ec`, `-oc posix`,
    `-oe pipefail -c` in bash, `-oerrexit -c` in zsh and `-opipefail -c` in ksh, `-c -e`,
    `-c --`, arguments after the string, a script file with `-c` after it), fish's `-C` and `-c`
    in both orders and with a flag that waits, and `--` ending the options of a wrapper and of a
    shell.

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
    expect(loose, 2, "RED: docs/notes/b.md:3: list item without a handle — loose one", "stdout")
    fence = lists_scan({"docs/notes/c.md": "# T\n\n````\n- x\n- y\n```\n- z\n- w\n````\n"})
    expect(fence, 0, "GREEN: const-interaction: 4 document(s) examined", "stdout")
    assert ok, f"exit {result.code}: {result.stdout}"


@item(22, "territories: a negated pattern takes a document out; a README at the top is covered")
def test_t22() -> None:
    """Territories: a negated pattern takes a document out; the default covers every Markdown file."""
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
    dial is empty; the project's pairs numbered."""
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
    lettered, and the hook prints it before python3 is looked for."""
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
    yaml_ok = messages.z1_could_not_run() in no_yaml.stderr and no_yaml.stdout == RULES
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
    a version it is told it has) and C15 (a copy without the shared code), each first line typed whole;
    and each gate's two entry files hold its clause exactly three times, once per entry text (C1, C14,
    C15), and "Markdown writes" nowhere."""
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
    plugin = H.scratch_dir() / "plugin"  # an install that dropped the link to the shared code
    shutil.copytree(
        SCRIPTS, plugin / "scripts", symlinks=True, ignore=shutil.ignore_patterns("constitution_layer_kit")
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
            harness.run_gate(
                stdin, args, command=[harness.sh, str(plugin / "scripts" / harness.wrapper.name)]
            ),
            "BROKEN: const-interaction is installed without its shared code (scripts/constitution_layer_kit"
            " is missing"
            " or is not a directory) — fix: install the plugin from its marketplace, or load it from a full"
            " checkout of the repository it comes from; a copy of the plugin's folder must be made with"
            f" links followed (cp -RL) — {clause}",
        )
        sources = "".join(
            (SCRIPTS / entry).read_text(encoding="utf-8")
            for entry in (harness.wrapper.name, harness.entry.name)
        )
        if sources.count(clause) != 3 or "Markdown writes" in sources:
            problems.append(
                f"{name} entry files: the clause {sources.count(clause)} times, wanted 3; or Markdown writes"
            )
    assert not problems, "; ".join(problems)


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
)
