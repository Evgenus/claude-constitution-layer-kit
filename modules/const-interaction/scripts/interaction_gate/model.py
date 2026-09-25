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
        "a hard reset discards every uncommitted change in the working tree and the index; nothing"
        " brings them back",
        "run git stash first, or reset with --keep, which stops when a change would be lost",
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
