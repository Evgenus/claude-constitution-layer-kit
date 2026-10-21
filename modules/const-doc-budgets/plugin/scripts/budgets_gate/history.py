"""The history report: for every ceiling the dials set now, the longest document it would have
held on each day since a date, read from every commit of the first-parent line of HEAD — the data a
ceiling's number is set from. It judges nothing and exits 0; a shallow clone, whose history would
report days it cannot see as empty, is a configuration failure. The documents of a day are counted
at its last commit; its longest is the longest version any commit of that day held. The state in
force on the first day is read from the last commit before it, when there is one; otherwise the
window starts on the first day a commit was made, so it never claims days no data stand behind. A
departure lifts nothing here: the data are every document's, the frozen ones included, since a
ceiling set from them must sit above them. A symbolic link is measured as the scan measures it: a link
whose path is Markdown and that leads, within the commit's tree, to a file counts as that file at the
link's own path, and a link to a folder, out of the tree, to nothing, or through more than `MAX_LINKS`
links is left out."""

from __future__ import annotations

import datetime
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import EXIT_GREEN
from constitution_layer_kit.output import Output
from constitution_layer_kit.repository import first_line, git, is_markdown
from constitution_layer_kit.territory import Matcher

from . import messages
from .model import BudgetDials, Ceiling, characters, longer, longest, rule_of_thumb

# The links one resolution may pass before it gives up, as Linux's own path resolution does.
MAX_LINKS = 40
_LINK = "120000"  # the mode git gives a symbolic link


@dataclass
class Day:
    documents: dict[str, int] = field(default_factory=dict)  # ceiling name -> documents at the last commit
    longest: dict[str, tuple[str, int]] = field(default_factory=dict)  # ceiling name -> (path, length)


def report(output: Output, root: Path, dials: BudgetDials, since: datetime.date) -> int:
    shallow = _git(["rev-parse", "--is-shallow-repository"], root).strip()
    if shallow == "true":
        raise ConfigurationFailure(messages.c12_shallow(str(root)))
    if git(["rev-parse", "--verify", "-q", "HEAD"], cwd=root).returncode != 0:
        output.out(messages.b2_no_commit(since))
        return EXIT_GREEN
    commits = _commits(root, since)
    if not commits:
        output.out(messages.b2_no_commit(since))
        return EXIT_GREEN
    links: dict[str, str] = {}  # a link's blob -> its target, read once for every commit
    trees = {sha: _markdown_blobs(root, sha, links) for sha, _ in commits}
    every_path = sorted({path for blobs in trees.values() for path in blobs})
    with Matcher() as matcher:
        held = {c.name: set(matcher.match(c.paths, every_path)) for c in dials.ceilings}
    lengths = _lengths(root, sorted({blob for blobs in trees.values() for blob in blobs.values()}))
    days = _days(commits, trees, held, lengths, dials.ceilings)
    ordered = sorted(days)
    for day in ordered:
        for ceiling in dials.ceilings:
            record = days[day]
            output.out(
                messages.b2_day(
                    day, ceiling, record.documents[ceiling.name], record.longest.get(ceiling.name)
                )
            )
    first, last = ordered[0], ordered[-1]
    for ceiling in dials.ceilings:
        top = longest([t for d in days.values() if (t := d.longest.get(ceiling.name)) is not None])
        thumb = rule_of_thumb(top[1]) if top is not None else 0
        output.out(messages.b2_window(ceiling, first, last, top, thumb))
    output.out(messages.b2_closing(since, len(commits), len(ordered), len(dials.ceilings)))
    return EXIT_GREEN


def _days(
    commits: Sequence[tuple[str, datetime.date]],
    trees: dict[str, dict[str, str]],
    held: dict[str, set[str]],
    lengths: dict[str, int],
    ceilings: Sequence[Ceiling],
) -> dict[datetime.date, Day]:
    """Each day's record: for every ceiling, the documents it held at the day's last commit and the
    longest of them any commit of the day held."""
    days: dict[datetime.date, Day] = {}
    for sha, day in commits:  # newest first: the first commit of a day met is its last
        record = days.get(day)
        first_of_day = record is None
        record = days.setdefault(day, Day())
        for ceiling in ceilings:
            mine = [(path, lengths[blob]) for path, blob in trees[sha].items() if path in held[ceiling.name]]
            if first_of_day:
                record.documents[ceiling.name] = len(mine)
            top = longest(mine)
            if top is not None and longer(top, record.longest.get(ceiling.name)):
                record.longest[ceiling.name] = top
    return days


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
    # log.showSignature=true would print a signature check before each formatted line
    listing = _git(
        ["-c", "log.showSignature=false", "log", "--first-parent", "--format=%H %cs", "HEAD"], root
    )
    for line in listing.splitlines():
        sha, _, stamp = line.partition(" ")
        day = datetime.date.fromisoformat(stamp)
        if day >= since:
            found.append((sha, day))
        else:
            found.append((sha, since))
            break
    return found


def _markdown_blobs(root: Path, sha: str, links: dict[str, str]) -> dict[str, str]:
    """{path: blob} of every Markdown file the commit's tree holds, a link at its own path standing for
    the blob of the file it leads to, as the module docstring says. `links` caches each link's target
    by its blob, across the commits of one report."""
    files: dict[str, str] = {}
    symlinks: dict[str, str] = {}
    listing = git(["ls-tree", "-r", "-z", sha], cwd=root)
    if listing.returncode != 0:
        raise ConfigurationFailure(messages.c12_git_history(first_line(listing.stderr)))
    for entry in os.fsdecode(listing.stdout).split("\0"):
        head, _, path = entry.partition("\t")
        parts = head.split()
        if len(parts) == 3 and parts[1] == "blob":
            (symlinks if parts[0] == _LINK else files)[path] = parts[2]
    blobs = {path: blob for path, blob in files.items() if is_markdown(path)}
    named = [path for path in symlinks if is_markdown(path)]
    if named:
        unread = sorted(set(symlinks.values()) - links.keys())
        links.update({blob: os.fsdecode(text) for blob, text in _contents(root, unread).items()})
        targets = {path: links[blob] for path, blob in symlinks.items()}
        folders = {
            "/".join(path.split("/")[:n])
            for path in [*files, *symlinks]
            for n in range(1, path.count("/") + 1)
        }
        for path in named:
            blob = _resolve(path, files, targets, folders)
            if blob is not None:
                blobs[path] = blob
    return blobs


def _resolve(link: str, files: dict[str, str], targets: dict[str, str], folders: set[str]) -> str | None:
    """The blob of the file the link at `link` leads to within the tree, or None: component by
    component, as a system resolves a path — a link's target read from the link's own folder, `..` from
    where the path stands once its links are followed. None for a folder, a target that leaves the tree
    or is absolute, a name the tree does not hold, a file with more path after it, and a resolution that
    passes more than `MAX_LINKS` links."""
    *done, name = link.split("/")
    pending = [name]  # the components still to walk, the next one last
    passed = 0
    while pending:
        part = pending.pop()
        if part in ("", "."):
            continue
        if part == "..":
            if not done:
                return None
            done.pop()
            continue
        here = "/".join([*done, part])
        if here in targets:
            passed += 1
            if passed > MAX_LINKS or targets[here].startswith("/"):
                return None
            pending.extend(reversed(targets[here].split("/")))
        elif here in files:
            return None if pending else files[here]
        elif here in folders:
            done.append(part)
        else:
            return None
    return None


def _contents(root: Path, blobs: Sequence[str]) -> dict[str, bytes]:
    """{blob: bytes} — each blob read once, through one git process."""
    if not blobs:
        return {}
    done = git(["cat-file", "--batch"], cwd=root, stdin=("\n".join(blobs) + "\n").encode("ascii"))
    if done.returncode != 0:
        raise ConfigurationFailure(messages.c12_git_history(first_line(done.stderr)))
    data, at = done.stdout, 0
    contents: dict[str, bytes] = {}
    for _ in blobs:
        end = data.index(b"\n", at)
        sha, kind, size = data[at:end].decode("ascii").split(" ")
        if kind != "blob":
            raise ConfigurationFailure(messages.c12_git_history(f"{sha} is a {kind}, not a blob"))
        start = end + 1
        contents[sha] = data[start : start + int(size)]
        at = start + int(size) + 1
    return contents


def _lengths(root: Path, blobs: Sequence[str]) -> dict[str, int]:
    """{blob: characters} — each blob read once, through one git process."""
    return {sha: characters(text.decode("utf-8", "replace")) for sha, text in _contents(root, blobs).items()}
