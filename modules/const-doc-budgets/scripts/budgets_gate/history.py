"""The history report: for every ceiling the dials set now, the longest document it would have
held on each day since a date, read from every commit of the first-parent line of HEAD — the data a
ceiling's number is set from. It judges nothing and exits 0; a shallow clone, whose history would
report days it cannot see as empty, is a configuration failure. The documents of a day are counted
at its last commit; its longest is the longest version any commit of that day held. The state in
force on the first day is read from the last commit before it, when there is one; otherwise the
window starts on the first day a commit was made, so it never claims days no data stand behind. A
departure lifts nothing here: the data are every document's, the frozen ones included, since a
ceiling set from them must sit above them."""

from __future__ import annotations

import datetime
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from const_gate.errors import ConfigurationFailure
from const_gate.model import EXIT_GREEN
from const_gate.output import Output
from const_gate.repository import first_line, git
from const_gate.territory import Matcher

from . import messages
from .model import BudgetDials, characters, longer, longest, rule_of_thumb


@dataclass
class Day:
    documents: dict[str, int] = field(default_factory=dict)  # ceiling name -> documents at the last commit
    longest: dict[str, tuple[str, int]] = field(default_factory=dict)  # ceiling name -> (path, length)


def report(output: Output, root: Path, dials: BudgetDials, since: datetime.date) -> int:
    shallow = _git(["rev-parse", "--is-shallow-repository"], root).strip()
    if shallow == "true":
        raise ConfigurationFailure(messages.c12_shallow(str(root)))
    if git(["rev-parse", "--verify", "-q", "HEAD"], cwd=root).returncode != 0:
        output.out(messages.h1_no_commit(since))
        return EXIT_GREEN
    commits = _commits(root, since)
    if not commits:
        output.out(messages.h1_no_commit(since))
        return EXIT_GREEN
    trees = {sha: _markdown_blobs(root, sha) for sha, _ in commits}
    every_path = sorted({path for blobs in trees.values() for path in blobs})
    with Matcher() as matcher:
        held = {c.name: set(matcher.match(c.paths, every_path)) for c in dials.ceilings}
    lengths = _lengths(root, sorted({blob for blobs in trees.values() for blob in blobs.values()}))
    days: dict[datetime.date, Day] = {}
    for sha, day in commits:  # newest first: the first commit of a day met is its last
        record = days.get(day)
        first_of_day = record is None
        record = days.setdefault(day, Day())
        for ceiling in dials.ceilings:
            mine = [(path, lengths[blob]) for path, blob in trees[sha].items() if path in held[ceiling.name]]
            if first_of_day:
                record.documents[ceiling.name] = len(mine)
            top = longest(mine)
            if top is not None and longer(top, record.longest.get(ceiling.name)):
                record.longest[ceiling.name] = top
    ordered = sorted(days)
    for day in ordered:
        for ceiling in dials.ceilings:
            record = days[day]
            output.out(
                messages.h1_day(
                    day, ceiling, record.documents[ceiling.name], record.longest.get(ceiling.name)
                )
            )
    first, last = ordered[0], ordered[-1]
    for ceiling in dials.ceilings:
        top = longest([t for d in days.values() if (t := d.longest.get(ceiling.name)) is not None])
        thumb = rule_of_thumb(top[1]) if top is not None else 0
        output.out(messages.h1_window(ceiling, first, last, top, thumb))
    output.out(messages.h1_closing(since, len(commits), len(ordered), len(dials.ceilings)))
    return EXIT_GREEN


def _git(args: list[str], root: Path) -> str:
    done = git(args, cwd=root)
    if done.returncode != 0:
        raise ConfigurationFailure(messages.c12_git_history(first_line(done.stderr)))
    return done.stdout.decode("utf-8", "replace")


def _commits(root: Path, since: datetime.date) -> list[tuple[str, datetime.date]]:
    """The commits of the first-parent line of HEAD committed on or after `since`, newest first, each
    with its committer date as the committer's clock wrote it; then, when one exists, the last commit
    before `since`, standing for `since` itself — the state in force when the window opens."""
    found: list[tuple[str, datetime.date]] = []
    for line in _git(["log", "--first-parent", "--format=%H %cs", "HEAD"], root).splitlines():
        sha, _, stamp = line.partition(" ")
        day = datetime.date.fromisoformat(stamp)
        if day >= since:
            found.append((sha, day))
        else:
            found.append((sha, since))
            break
    return found


def _markdown_blobs(root: Path, sha: str) -> dict[str, str]:
    """{path: blob} of every Markdown file the commit's tree holds."""
    blobs: dict[str, str] = {}
    listing = git(["ls-tree", "-r", "-z", sha], cwd=root)
    if listing.returncode != 0:
        raise ConfigurationFailure(messages.c12_git_history(first_line(listing.stderr)))
    for entry in os.fsdecode(listing.stdout).split("\0"):
        head, _, path = entry.partition("\t")
        parts = head.split()
        if len(parts) == 3 and parts[1] == "blob" and path.lower().endswith(".md"):
            blobs[path] = parts[2]
    return blobs


def _lengths(root: Path, blobs: Sequence[str]) -> dict[str, int]:
    """{blob: characters} — each blob read once, through one git process."""
    if not blobs:
        return {}
    done = git(["cat-file", "--batch"], cwd=root, stdin=("\n".join(blobs) + "\n").encode("ascii"))
    if done.returncode != 0:
        raise ConfigurationFailure(messages.c12_git_history(first_line(done.stderr)))
    data, at = done.stdout, 0
    lengths: dict[str, int] = {}
    for _ in blobs:
        end = data.index(b"\n", at)
        sha, kind, size = data[at:end].decode("ascii").split(" ")
        if kind != "blob":
            raise ConfigurationFailure(messages.c12_git_history(f"{sha} is a {kind}, not a blob"))
        start = end + 1
        lengths[sha] = characters(data[start : start + int(size)].decode("utf-8", "replace"))
        at = start + int(size) + 1
    return lengths
