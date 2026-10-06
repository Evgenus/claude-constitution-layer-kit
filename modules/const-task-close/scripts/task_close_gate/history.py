"""The one place git is asked about a range — where the base is, which paths the change names,
which declarations its messages carry — and about the working tree. Every answer git refuses
is a configuration failure with git's own first line, never a guess."""

from __future__ import annotations

import os
import re
from pathlib import Path

from const_gate.errors import ConfigurationFailure
from const_gate.repository import first_line, git

from . import messages
from .model import BODY, Declaration, Range

# `<pair> — <reason>`: an em or en dash, spaced or not, or one or two hyphens spaced on both sides
NO_COMMON_ANCESTOR = "the two histories share no commit"
DASH_REF = "a ref cannot begin with a dash"
# a git that does not know a trailer option prints the placeholder itself, with exit 0
UNKNOWN_PLACEHOLDER = "%(trailers"
DASH = re.compile(r"^(.*?)(?:\s*[—–]\s*|\s+--?\s+)(.*)$", re.DOTALL)


def status_lines(root: Path) -> list[str]:
    """What `git status --porcelain` lists: tracked changes and untracked files git does not
    ignore, one line each — a dirty tree is any line."""
    done = git(["status", "--porcelain", "--untracked-files=all"], cwd=root)
    if done.returncode != 0:
        raise ConfigurationFailure(messages.c12_tree(str(root), first_line(done.stderr)))
    return [line for line in os.fsdecode(done.stdout).splitlines() if line.strip()]


def resolve(root: Path, flag: str, ref: str) -> str:
    """The full hash a ref names, or the configuration failure that says it names none."""
    if ref.startswith("-"):  # git would read it as an option; no ref of this repository begins so
        raise ConfigurationFailure(messages.c12_unknown_ref(flag, ref, str(root), DASH_REF))
    done = git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=root)
    if done.returncode != 0:
        detail = first_line(done.stderr) if done.stderr.strip() else "no such ref"
        raise ConfigurationFailure(messages.c12_unknown_ref(flag, ref, str(root), detail))
    return os.fsdecode(done.stdout).strip()


def head(root: Path) -> str | None:
    """HEAD's commit; None on an unborn branch — no commit yet on it, in an empty repository or
    after an orphan checkout. A HEAD git cannot read for any other reason — a ref holding zeros or a
    missing object, a detached HEAD gone — is a configuration failure with git's own line, never a
    green that examined nothing."""
    done = git(["rev-parse", "--verify", "--quiet", "HEAD^{commit}"], cwd=root)
    if done.returncode == 0:
        return os.fsdecode(done.stdout).strip()
    symbolic = git(["symbolic-ref", "--quiet", "HEAD"], cwd=root)
    if symbolic.returncode == 0:
        ref = os.fsdecode(symbolic.stdout).strip()
        probe = git(["show-ref", "--verify", "--quiet", ref], cwd=root)
        if probe.returncode == 1 and not probe.stderr.strip():  # the branch exists in name only: unborn
            return None
        detail = first_line(probe.stderr) if probe.stderr.strip() else _loud_head(root)
    else:
        detail = _loud_head(root)
    raise ConfigurationFailure(messages.c12_range("HEAD", "HEAD", str(root), detail))


def _loud_head(root: Path) -> str:
    """git's own words for a HEAD it cannot resolve, asked without --quiet."""
    return first_line(git(["rev-parse", "--verify", "HEAD^{commit}"], cwd=root).stderr)


def current_branch(root: Path) -> str | None:
    done = git(["symbolic-ref", "--quiet", "--short", "HEAD"], cwd=root)
    return os.fsdecode(done.stdout).strip() if done.returncode == 0 else None


def trunk_tip(root: Path, trunk: str) -> str | None:
    """The trunk as a local branch, else as origin's; None when it is neither."""
    for ref in (f"refs/heads/{trunk}", f"refs/remotes/origin/{trunk}"):
        done = git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=root)
        if done.returncode == 0:
            return os.fsdecode(done.stdout).strip()
    return None


def merge_base(root: Path, a: str, b: str) -> str:
    """Two histories with no common ancestor make git exit 1 in silence; that is said in words."""
    done = git(["merge-base", a, b], cwd=root)
    if done.returncode != 0:
        detail = first_line(done.stderr) if done.stderr.strip() else NO_COMMON_ANCESTOR
        raise ConfigurationFailure(messages.c12_range(short(root, a), short(root, b), str(root), detail))
    return os.fsdecode(done.stdout).strip()


def first_parent(root: Path, commit: str) -> str | None:
    done = git(["rev-list", "--parents", "-n", "1", commit], cwd=root)
    if done.returncode != 0:
        raise ConfigurationFailure(
            messages.c12_range(short(root, commit), short(root, commit), str(root), first_line(done.stderr))
        )
    parts = os.fsdecode(done.stdout).split()
    return parts[1] if len(parts) > 1 else None


def short(root: Path, commit: str) -> str:
    done = git(["rev-parse", "--short", commit], cwd=root)
    return os.fsdecode(done.stdout).strip() if done.returncode == 0 else commit[:7]


def make_range(root: Path, base: str | None, tip: str) -> Range:
    """The commits after `base` up to `tip` and the paths their diff names; renames are not
    folded, so a renamed path appears under both its names."""
    tip_short = short(root, tip)
    if base is None:
        listing = git(
            ["diff-tree", "--root", "-r", "--no-commit-id", "--name-only", "--no-renames", "-z", tip],
            cwd=root,
        )
        base_short = tip_short
        commits = 1
    else:
        listing = git(["diff", "--name-only", "--no-renames", "-z", base, tip], cwd=root)
        base_short = short(root, base)
        counted = git(["rev-list", "--count", f"{base}..{tip}"], cwd=root)
        if counted.returncode != 0:
            raise ConfigurationFailure(
                messages.c12_range(base_short, tip_short, str(root), first_line(counted.stderr))
            )
        commits = int(os.fsdecode(counted.stdout).strip() or "0")
    if listing.returncode != 0:
        raise ConfigurationFailure(
            messages.c12_range(base_short, tip_short, str(root), first_line(listing.stderr))
        )
    paths = tuple(sorted({p for p in os.fsdecode(listing.stdout).split("\0") if p}))
    return Range(base, tip, base_short, tip_short, commits, paths)


def trailers(root: Path, rng: Range, key: str) -> list[Declaration]:
    """Every value of the key among the range's commit messages, newest commit first, as git
    reads trailers: the message's last paragraph, every line `Key: value`."""
    where = [f"{rng.base}..{rng.tip}"] if rng.base is not None else ["-1", rng.tip]
    done = git(  # log.showSignature=true would print a signature check before each formatted line
        [
            "-c",
            "log.showSignature=false",
            "log",
            f"--format=%h%x00%(trailers:key={key},valueonly,unfold,separator=%x1f)%x01",
            *where,
        ],
        cwd=root,
    )
    if done.returncode != 0:
        raise ConfigurationFailure(
            messages.c12_range(rng.base_short, rng.tip_short, str(root), first_line(done.stderr))
        )
    found: list[Declaration] = []
    for record in os.fsdecode(done.stdout).split("\x01"):
        if "\x00" not in record:
            continue
        commit, values = record.strip("\n").split("\x00", 1)
        if values.startswith(UNKNOWN_PLACEHOLDER):  # a trailer's own text may quote it, not begin so
            raise ConfigurationFailure(messages.c12_old_git(_version_line(root)))
        for value in values.split("\x1f"):
            if value.strip():
                found.append(declaration(f"commit {commit.strip()}", value.strip()))
    return found


def _version_line(root: Path) -> str:
    """git's own first line of `git version`, or the way it failed to say it."""
    done = git(["version"], cwd=root)
    if done.returncode != 0:
        return f"git version failed: {first_line(done.stderr)}"
    lines = os.fsdecode(done.stdout).strip().splitlines()
    return lines[0] if lines else "git version printed nothing"


def body_declarations(text: str, key: str) -> list[Declaration]:
    """The same line, read from a pull request's description: `Key: value` on a line of its own."""
    line = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", re.IGNORECASE)
    found: list[Declaration] = []
    for raw in text.splitlines():
        match = line.match(raw)
        if match and match.group(1):
            found.append(declaration(BODY, match.group(1)))
    return found


def declaration(where: str, value: str) -> Declaration:
    split = DASH.match(value)
    if split:
        return Declaration(where, value, split.group(1).strip(), split.group(2).strip())
    return Declaration(where, value, value.strip(), "")


def kind_at(root: Path, tip: str, path: str) -> str | None:
    """What the path is in that commit, as git types it — `blob` for a file, `tree` for a
    directory, `commit` for a submodule — or None when the commit holds no such path."""
    done = git(["cat-file", "-t", f"{tip}:{path}"], cwd=root)
    return os.fsdecode(done.stdout).strip() if done.returncode == 0 else None


def tracked(root: Path) -> list[str]:
    done = git(["ls-files", "-z", "--cached"], cwd=root)
    if done.returncode != 0:
        raise ConfigurationFailure(messages.c12_tree(str(root), first_line(done.stderr)))
    return sorted({p for p in os.fsdecode(done.stdout).split("\0") if p})
