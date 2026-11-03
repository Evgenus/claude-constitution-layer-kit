"""This module's own structures: its dials, the shell command as read, and the keys of its
findings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

DEFAULT_TERRITORIES = ("*.md",)
# The handle forms a list item may open with, after an optional anchor and an optional bold
# marker: `1.`, `A.`, `a.`, `a1.`, `R1` / `S137` / `L1b`, `Q-a`.
DEFAULT_HANDLES = (
    r"[0-9]+\.",
    r"[A-Z]\.",
    r"[a-z]\.",
    r"[a-z][0-9]+\.",
    r"[A-Z]+[0-9]+[a-z]?\b",
    r"[A-Z]-[a-z]\b",
)
COMMAND_FLAG = "--command"


class Verbosity(StrEnum):
    """The one value the verbosity dial takes today: the assumption block and the restatement
    appear only when triggered, never as an empty ritual."""

    TRIGGERED = "triggered"


class Key(StrEnum):
    """Stable handles of this module's findings."""

    D1 = "D1"  # a subcommand of the shell command matches an entry of the destructive dial
    L1 = "L1"  # a list of a covered document has an item that opens with no handle


@dataclass(frozen=True, slots=True)
class Entry:
    """One entry of the destructive dial: the command words, the flags any one of which
    matches (none: the words alone match), why the act is hard to reverse, and the reversible
    way."""

    command: tuple[str, ...]
    flags: tuple[str, ...]
    teach: str
    alternative: str

    def shown(self) -> str:
        words = " ".join(self.command)
        return words if not self.flags else f"{words} with {' or '.join(self.flags)}"


@dataclass(frozen=True, slots=True)
class Pair:
    """A boundary example of the project's own, printed after the rules."""

    violates: str
    complies: str


@dataclass(frozen=True, slots=True)
class InteractionDials:
    destructive: tuple[Entry, ...]
    territories: tuple[str, ...]
    handles: tuple[str, ...]
    boundary_examples: tuple[Pair, ...]
    verbosity: Verbosity
    reader: ReaderLists  # the default wrappers and shells, merged with those of the dials of that name
    changed: tuple[Dropped | Replaced, ...]  # the defaults those dials removed or replaced, as they stand


@dataclass(frozen=True, slots=True)
class Subcommand:
    """One simple command of the shell command, as the gate reads it: its words after the
    wrappers, assignments and the program's directory are stripped, and the text it came from."""

    words: tuple[str, ...]
    text: str


@dataclass(frozen=True, slots=True)
class Hit:
    entry: Entry
    subcommand: Subcommand
    matched: str  # the flag that matched, or empty when the words alone did


@dataclass(frozen=True, slots=True)
class ListHit:
    """The first item of a list that opens with no handle: where, and its text."""

    line: int
    text: str


def _entry(command: str, flags: tuple[str, ...], teach: str, alternative: str) -> Entry:
    return Entry(tuple(command.split()), flags, teach, alternative)


# The default list: each entry with the reversible alternative it teaches. What it leaves out is
# said in the module's document and in the install note.
DEFAULT_DESTRUCTIVE: tuple[Entry, ...] = (
    _entry(
        "git push",
        ("--force", "-f"),
        "a forced push rewrites the branch on the remote: every other clone of it diverges, and the"
        " commits it replaced are unreachable there",
        "push with --force-with-lease, which refuses when the remote moved, or push a new branch and"
        " open a pull request",
    ),
    _entry(
        "git reset",
        ("--hard",),
        "a hard reset discards every uncommitted change in the working tree and the index, which nothing"
        " brings back; with a target such as HEAD~1 it also drops the commits after the target from the"
        " branch",
        "run git stash first, or reset with --keep, which stops when a change would be lost; with a"
        " target, also tag the tip first (git tag keep/<name>)",
    ),
    _entry(
        "git checkout",
        ("-f", "--force"),
        "a forced checkout throws away local changes to the files it switches; nothing brings them back",
        "run git stash first, then check out; or commit the changes on a branch",
    ),
    _entry(
        "git restore",
        (),
        "git restore discards the working-tree changes of the paths it names; nothing brings them back",
        "run git stash first, or git diff to see what would be lost, then restore one path at a time",
    ),
    _entry(
        "git clean",
        ("-f", "--force"),
        "git clean deletes untracked files, which no commit holds; nothing brings them back",
        "run git clean -n first to see what would go, then move what matters out of the tree",
    ),
    _entry(
        "git branch",
        ("-D", "-f", "--force"),
        "-D deletes a branch whether or not it is merged, and -f moves one to another commit: the"
        " commits left behind become unreachable",
        "delete with -d, which refuses an unmerged branch, or tag the tip first (git tag keep/<name>)",
    ),
    _entry(
        "git stash drop",
        (),
        "a dropped stash is unreachable; nothing lists it again",
        "apply it with git stash branch <name>, or leave it in the list",
    ),
    _entry(
        "git stash clear",
        (),
        "clear drops every stash at once; nothing lists them again",
        "drop one at a time after applying it with git stash branch <name>",
    ),
    _entry(
        "git rebase",
        (),
        "a rebase rewrites the commits of the branch: their hashes change, and a branch others hold"
        " diverges from theirs",
        "tag the tip first (git tag keep/<name>), or make the change on a new branch and merge",
    ),
    _entry(
        "git filter-branch",
        (),
        "filter-branch rewrites history across every commit it touches",
        "clone the repository first, and rewrite the clone",
    ),
    _entry(
        "git filter-repo",
        (),
        "filter-repo rewrites history across every commit it touches",
        "clone the repository first, and rewrite the clone",
    ),
    _entry(
        "git reflog expire",
        (),
        "expiring the reflog removes the record that lets a lost commit be found again",
        "leave the reflog; disk is cheaper than a lost commit",
    ),
    _entry(
        "git gc",
        ("--prune=now",),
        "pruning now deletes every unreachable object at once, including those the reflog would have"
        " let you recover",
        "run git gc without --prune=now, which keeps recent unreachable objects",
    ),
    _entry(
        "rm",
        ("-r", "-R", "--recursive"),
        "a recursive rm deletes a directory tree outside git; nothing brings it back",
        "use git rm for tracked files, or move the directory to a scratch location first",
    ),
)


@dataclass(frozen=True, slots=True)
class Wrapper:
    """A program that runs another program, stripped from the front of a command with its own
    options. `command` is its words, the first read by its base name. `with_value` are the options
    whose value is the next word; `positionals` the plain words always skipped before the command
    (`timeout 5`); `numbers` how many more words are skipped, each only when it is a number;
    `command_flags` the options whose value is a command string, read again, the words after that
    value appended to it (`env -S`)."""

    command: tuple[str, ...]
    with_value: tuple[str, ...] = ()
    positionals: int = 0
    numbers: int = 0
    command_flags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Shell:
    """A program whose option reads a command string: `command` is its one word, `with_value` the
    options whose value is the next word, `command_flags` the options whose string is read: every one
    met yields a string, its attached value, else the next word when that is no option and no other
    option's value, else the first operand after the options. The words after a string are the
    program's arguments and are not read."""

    command: str
    with_value: tuple[str, ...] = ()
    command_flags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReaderLists:
    """The wrappers and the shells the shell reader knows."""

    wrappers: tuple[Wrapper, ...]
    shells: tuple[Shell, ...]


class ReaderDial(StrEnum):
    """The two dials that hold the reader's lists, each named by the key it is written under."""

    WRAPPERS = "wrappers"
    SHELLS = "shells"


class ReaderField(StrEnum):
    """The fields of an entry of a reader dial, each named by the key it is written under."""

    COMMAND = "command"
    WITH_VALUE = "with_value"
    POSITIONALS = "positionals"
    NUMBERS = "numbers"
    COMMAND_FLAGS = "command_flags"
    DROP = "drop"


@dataclass(frozen=True, slots=True)
class Dropped:
    """A default the dials removed: the dial it stood in (`wrappers` or `shells`) and its command."""

    dial: ReaderDial
    command: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Replaced:
    """A default the dials replaced whole by an entry of its command: the dial it stood in and its
    command. The entry's fields are the ones written, none of the default's kept."""

    dial: ReaderDial
    command: tuple[str, ...]


class OptionFault(StrEnum):
    """Why an option of a wrapper or a shell, as the dials give it, can never be matched by the
    reader."""

    NOT_A_LIST = "not a list"  # the field is no non-empty list of non-blank texts
    WHITE_SPACE = "white space"  # an option is one word of the command line
    NO_SIGN = "no sign"  # it does not start as the reader's options do: `-`, for a shell also `+`
    LONE_SIGN = "lone sign"  # `-`, `--`, `+`: it names nothing
    LETTERS = "letters"  # a short option of more than one letter: a cluster is read a letter at a time
    EQUALS = "equals"  # a long option holding `=`: it is compared by the name before it


def _flags(text: str) -> tuple[str, ...]:
    return tuple(text.split())


# The default wrappers. Per wrapper, the options that take the next word as a value: `nice -n 5`,
# `sudo -u root`, `xargs -I {}`; a `--flag=value` is one word and needs no entry.
# Sources, read 2026-09-25: sudo's upstream man page (sudo.ws; -r, -t and their long forms are
# SELinux-only and absent from the macOS page); the xargs pages of macOS 26 (BSD) and of GNU
# findutils; env of macOS 26 and GNU coreutils, with FreeBSD's -L and -U; doas of OpenBSD; nice,
# stdbuf and timeout of GNU coreutils. A long flag whose value is the next word is listed as the
# page spells it — an abbreviation of it, which GNU getopt_long accepts, is not read as it, since
# telling one apart needs every flag of the program; `--flag=value` is one word and needs no
# entry; a GNU flag whose value is optional (`--max-lines[=N]`, `--eof[=STR]`) takes it attached
# only and is left out on purpose, since given bare it takes no word. env's -S and --split-string
# hold a command, so they are its `command_flags`, not `with_value`. `timeout` is told its duration
# before the command: one positional word. `time`, `nohup`, `command`, `builtin` and `noglob` take
# no option that has a value. `exec`, read 2026-10-05 in bash(1), the shell builtins, as shipped
# with macOS 26 (bash 3.2.57), synopsis `exec [-cl] [-a name] [command [arguments]]`: -c and -l take
# no value, -a takes the name, so only `-a` is listed; it was a shell word before, which left
# `exec -a x rm -r y` read as `-a x rm -r y`.
DEFAULT_WRAPPERS: tuple[Wrapper, ...] = (
    Wrapper(("time",)),
    Wrapper(("nohup",)),
    Wrapper(("command",)),
    Wrapper(("builtin",)),
    Wrapper(("noglob",)),
    Wrapper(("exec",), with_value=("-a",)),
    Wrapper(
        ("xargs",),
        with_value=_flags(
            "-I -J -d -P -s -n -L -a -E -R -S --max-args --max-procs --max-chars --arg-file --delimiter"
            " --process-slot-var"
        ),
    ),
    Wrapper(
        ("sudo",),
        with_value=_flags(
            "-u -g -C -p -h -U -r -t -D -R -T -a -c --user --group --close-from --prompt --host"
            " --other-user --role --type --chdir --chroot --command-timeout --auth-type --login-class"
        ),
    ),
    Wrapper(("doas",), with_value=_flags("-u -C -a")),
    Wrapper(
        ("env",),
        with_value=_flags("-C -u -P -L -U --chdir --unset"),
        command_flags=_flags("-S --split-string"),
    ),
    Wrapper(("nice",), with_value=_flags("-n --adjustment")),
    Wrapper(("stdbuf",), with_value=_flags("-i -o -e --input --output --error")),
    Wrapper(("timeout",), with_value=_flags("-s -k --signal --kill-after"), positionals=1),
    # The wrappers below, read 2026-10-05, each from the page it names; a long flag whose value is the next
    # word is listed as its page spells it, as above. The util-linux pages are man7.org's, man-pages/man1/
    # <name>.1.html, of util-linux 2.43.devel, each dated in its footer.
    # busybox: BusyBox's page (https://busybox.net/downloads/BusyBox.html, served with a date of 2009-10-02),
    # `busybox <applet> [arguments...]`: no option of its own, the applet follows.
    Wrapper(("busybox",)),
    # setsid: page of 2026-05-24, `setsid [options] program [arguments]`; -c, -f, -w take no value.
    Wrapper(("setsid",)),
    # ionice: page of 2026-05-24; -c/--class and -n/--classdata take a value, -t takes none; -p, -P and -u
    # take ids and run no command, so they are not listed.
    Wrapper(("ionice",), with_value=_flags("-c -n --class --classdata")),
    # taskset: page of 2026-05-24, `taskset [options] mask command [argument...]`: one positional word, the
    # mask, or with -c the CPU list; -a, -c, -p take no value.
    Wrapper(("taskset",), positionals=1),
    # caffeinate: macOS 26's own `man caffeinate`, dated 2012-11-09, `caffeinate [-disu] [-t timeout] [-w pid]
    # [utility arguments...]`: -t and -w take a value.
    Wrapper(("caffeinate",), with_value=_flags("-t -w")),
    # flock: page of 2026-05-24, `flock [options] file|directory command [arguments]` or `-c command`: -E
    # (--conflict-exit-code), -w (--wait, --timeout), --start and --length take a value; one positional
    # word, the lock file; -c/--command is read after it too, as `env -S`'s string is.
    Wrapper(
        ("flock",),
        with_value=_flags("-E -w --conflict-exit-code --wait --timeout --start --length"),
        positionals=1,
        command_flags=_flags("-c --command"),
    ),
    # chrt: page of 2026-08-03, `chrt [options] [priority] command [argument...]`: -T, -P, -D, -U, -X with
    # --sched-runtime, --sched-period, --sched-deadline, --clamp-min, --clamp-max take a value; the priority
    # is optional since util-linux 2.42, so one number is skipped when there is one.
    Wrapper(
        ("chrt",),
        with_value=_flags(
            "-T -P -D -U -X --sched-runtime --sched-period --sched-deadline --clamp-min --clamp-max"
        ),
        numbers=1,
    ),
)

# The default shells: the programs whose command strings are read as commands. Every command flag met
# yields a string: its attached value, else the next word when that is no option and no other option's
# value, else the first operand after the options, so `bash -ce 'x'` and `bash -c -e 'x'` read `x` once
# and fish's `-C` and `-c` both read theirs. Bash's own options that take a value stand for the first
# five alike: `-o` and `-O` with their `+` forms (`bash -o pipefail -c …`, `-eo pipefail`, `+o posix`,
# `-O extglob`) and the long `--rcfile` and `--init-file`.
DEFAULT_SHELLS: tuple[Shell, ...] = (
    *(
        Shell(name, with_value=_flags("-o -O +o +O --rcfile --init-file"), command_flags=("-c",))
        for name in ("bash", "sh", "zsh", "dash", "ksh")
    ),
    # The shells below, read 2026-10-05, each from the page it names. fish:
    # https://fishshell.com/docs/current/cmds/fish.html, fish 4.9.3 (the page marks itself as an old version
    # and links the same address as the latest release; 4.9.3 is the latest on GitHub): -c/--command and
    # -C/--init-command run a string; -d/--debug, -o/--debug-output, -p/--profile, --profile-startup and
    # -f/--features take a value, the page spelling the long ones with `=`, its examples with a space.
    Shell(
        "fish",
        with_value=_flags("-d -o -p -f --debug --debug-output --profile --profile-startup --features"),
        command_flags=_flags("-c --command -C --init-command"),
    ),
    # ash: BusyBox's page lists it as an applet and gives no usage; its usage line is in
    # https://github.com/mirror/busybox/blob/master/shell/ash.c (the file last changed 2024-07-13):
    # `[-il] [-|+Cabefmnuvx] [-|+o OPT]... [-c 'SCRIPT' [ARG0 ARGS] | FILE ARGS | -s ARGS]`.
    Shell("ash", with_value=_flags("-o +o"), command_flags=("-c",)),
    # mksh: https://www.mirbsd.org/htman/i386/man1/mksh.htm, page of 2026-01-25,
    # `mksh [-+abCefhiklmnprUuvXx] [-+o option] [-T [!]tty|-] -c cmd [arg0 ...]`: -o, +o and -T take a value.
    Shell("mksh", with_value=_flags("-o +o -T"), command_flags=("-c",)),
    # yash: https://magicant.github.io/yash/doc/invoke.html (updated 2025-04-21) and _set.html (updated
    # 2025-11-29): -c (--cmdline) runs its first operand; -o and +o take a name, the options of `set`.
    Shell("yash", with_value=_flags("-o +o"), command_flags=_flags("-c --cmdline")),
    # posh: https://manpages.debian.org/trixie/posh/posh.1.en.html, posh 0.14.1, `posh [+-aCefilnuvx] [+-o
    # option] [[-c command-string [command-name] | -s | file] [argument...]]`: -o and +o take a value.
    Shell("posh", with_value=_flags("-o +o"), command_flags=("-c",)),
    # csh and tcsh: https://manpages.debian.org/trixie/tcsh/tcsh.1.en.html, tcsh 6.24.13, `tcsh
    # [-bcdefFimnqstvVxX] [-Dname[=value]] [arg] ...`; FreeBSD 15.1's csh(1), man.freebsd.org, is the same
    # text. No option takes the next word as its value (`-D` is attached); -c reads the following argument as
    # the commands.
    Shell("csh", command_flags=("-c",)),
    Shell("tcsh", command_flags=("-c",)),
)

DEFAULT_READER_LISTS = ReaderLists(DEFAULT_WRAPPERS, DEFAULT_SHELLS)
