"""The report and its three exports, each made from the file of counts and started by a person, never by a
hook: the plain report, `--trailer`, `--pr` and `--notes`.

The report reads the file of counts, and the commit log and the start log to name the reason a commit has no
kept line; it reads no transcript and runs no ccusage. With no range it shows every kept line. With a range
it shows each commit of the range, counted or not, in the range's order, and the total. The cost is the list
price of ccusage's table, and every line says so. `--pr` writes its block through `gh` where `gh` finds the
pull request of the range's head, the branch the range ends at, and prints it with the reason otherwise;
`--notes` writes under the module's notes ref. The module never pushes."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.output import Output
from constitution_layer_kit.repository import repo_root

from . import git as gitpart
from . import logs, messages, windows
from .model import (
    GH_SECONDS,
    MARK_CLOSE,
    MARK_OPEN,
    PIN,
    CommitLine,
    Figures,
    Kept,
    ModelTokens,
    NotCounted,
    Reason,
    StartLine,
)

Shown = Kept | NotCounted
NO_PULL_REQUEST = "no pull requests found"  # gh's own words, in lower case, when a branch has no pull request


@dataclass(frozen=True, slots=True)
class Selection:
    """What a report shows: the commits in order, each with its kept line or its reason."""

    range_text: str | None
    shown: list[Shown]

    @property
    def counted(self) -> list[Kept]:
        return [held for held in self.shown if isinstance(held, Kept)]

    @property
    def not_counted(self) -> list[NotCounted]:
        return [held for held in self.shown if isinstance(held, NotCounted)]

    @property
    def versions(self) -> list[str]:
        """Every ccusage version the shown lines carry; the pin where none is shown."""
        return sorted({held.ccusage for held in self.counted}) or [PIN]


def figures_of(kept: Kept) -> Figures:
    return Figures(
        kept.input,
        kept.output,
        kept.cache_write,
        kept.cache_read,
        kept.total,
        kept.cost,
        kept.replies,
        kept.models,
        kept.compactions,
        kept.unpriced,
    )


def total_of(counted: Sequence[Kept]) -> Figures:
    """The sums of the counted lines. The cost is the sum of the windows' costs; the models add by name."""
    tokens: Counter[str] = Counter()
    for kept in counted:
        for held in kept.models:
            tokens[held.model] += held.tokens
    ordered = sorted(tokens.items(), key=lambda held: (-held[1], held[0]))
    return Figures(
        input=sum(kept.input for kept in counted),
        output=sum(kept.output for kept in counted),
        cache_write=sum(kept.cache_write for kept in counted),
        cache_read=sum(kept.cache_read for kept in counted),
        total=sum(kept.total for kept in counted),
        cost=sum(kept.cost for kept in counted),
        replies=sum(kept.replies for kept in counted),
        models=tuple(ModelTokens(name, held) for name, held in ordered),
        compactions=sum(kept.compactions for kept in counted),
        unpriced=tuple(sorted({name for kept in counted for name in kept.unpriced})),
    )


def reason_of(sha: str, commits: dict[str, CommitLine], starts_of: dict[str, list[StartLine]]) -> NotCounted:
    """Why a commit has no kept line, from the two logs and from whether the session's transcript stands. The
    transcript is not read: only whether a file stands, as the count looks. A commit the count has not yet
    reached is waiting."""
    line = commits.get(sha)
    if line is None:
        return NotCounted(sha, Reason.NO_LOG)
    if not line.session:
        return NotCounted(sha, Reason.NO_SESSION)
    starts = starts_of.get(line.session, [])
    if not starts:
        return NotCounted(sha, Reason.NO_START, line.session)
    earliest = min(starts, key=lambda held: held.ms)
    if line.ms < earliest.ms:
        return NotCounted(sha, Reason.NO_START, line.session)
    first = earliest.transcript_path
    if not any(
        windows.transcripts_of(Path(path))
        for path in dict.fromkeys(s.transcript_path for s in starts if s.transcript_path)
    ):
        return NotCounted(sha, Reason.NO_TRANSCRIPT, line.session, first)
    return NotCounted(sha, Reason.WAITING, line.session)


def select(output: Output, directory: Path, range_text: str | None) -> Selection:
    """The commits to show. The unreadable lines of the logs are named on stderr, leaving stdout to the
    report, which a trailer's caller may read as a message."""
    folder = logs.folder_of(gitpart.common_directory(directory))
    counts, notes = logs.read_counts(folder)
    by_sha: dict[str, Kept] = {}
    for kept in counts:
        by_sha.setdefault(kept.sha, kept)
    if range_text is None:
        for note in notes:
            output.err(note)
        return Selection(None, list(by_sha.values()))
    root = repo_root(directory) or directory
    shas = gitpart.range_commits(directory, root, range_text)
    commits, commit_notes = logs.read_commits(folder)
    starts, start_notes = logs.read_starts(folder)
    for note in (*notes, *commit_notes, *start_notes):
        output.err(note)
    commit_of: dict[str, CommitLine] = {}
    for line in commits:
        commit_of.setdefault(line.sha, line)
    starts_of: dict[str, list[StartLine]] = {}
    for start_line in starts:
        starts_of.setdefault(start_line.session, []).append(start_line)
    shown: list[Shown] = [
        by_sha[sha] if sha in by_sha else reason_of(sha, commit_of, starts_of) for sha in shas
    ]
    return Selection(range_text, shown)


def run_report(output: Output, directory: Path, range_text: str | None) -> int:
    chosen = select(output, directory, range_text)
    counted = chosen.counted
    if range_text is None:
        output.out(messages.j9_head_all(len(counted), chosen.versions))
    else:
        output.out(messages.j9_head(len(chosen.shown), len(counted), range_text, chosen.versions))
    for held in chosen.shown:
        if isinstance(held, Kept):
            output.out(messages.j10_counted(held.sha, figures_of(held)))
        else:
            output.out(messages.j11_not_counted(held))
    if range_text is not None:
        output.out(messages.j12_total(len(counted), total_of(counted)))
    return 0


def run_trailer(output: Output, directory: Path, range_text: str) -> int:
    chosen = select(output, directory, range_text)
    counted = chosen.counted
    for held in counted:
        output.out(messages.j13_commit(held.sha, figures_of(held)))
    output.out(messages.j13_total(len(counted), len(chosen.shown), total_of(counted)))
    return 0


def block_of(chosen: Selection) -> str:
    counted = chosen.counted
    return messages.j14_block(
        [(held.sha, figures_of(held)) for held in counted],
        total_of(counted),
        len(chosen.shown),
        chosen.not_counted,
        chosen.versions,
    )


def with_block(body: str, block: str) -> str:
    """The description with the block between its markers: an earlier block replaced and the rest kept, or the
    block added after the description."""
    earlier = re.compile(re.escape(MARK_OPEN) + ".*?" + re.escape(MARK_CLOSE), re.DOTALL)
    if earlier.search(body):
        return earlier.sub(lambda _: block, body, count=1)
    return (body.rstrip("\n") + "\n\n" if body.strip() else "") + block + "\n"


def _gh(directory: Path, args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str] | str:
    """One gh call within `GH_SECONDS`; the detail of the failure, in words, where gh cannot be started or
    does not answer in time."""
    try:
        return subprocess.run(
            ["gh", *args],
            cwd=directory,
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
            timeout=GH_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return messages.detail_gh_silent()
    except OSError as exc:
        return str(exc)


@dataclass(frozen=True, slots=True)
class PullRequest:
    """A pull request as `gh pr view` gives it: its number and its description."""

    number: int
    body: str


def head_of(range_text: str) -> str:
    """The end of the range that names the work: the side after `..` or `...`, `HEAD` where that is left
    empty, and the text as it is where the range is a single revision."""
    for separator in ("...", ".."):
        if separator in range_text:
            return range_text.partition(separator)[2] or "HEAD"
    return range_text


def pull_request(directory: Path, head: str) -> PullRequest | str:
    """The pull request of the branch `head`, or the note, J15.2 to J15.4, that says why there is none: no gh,
    a gh that failed or gave no answer in time, or a gh that found no pull request of that branch."""
    if shutil.which("gh") is None:
        return messages.j15_2_no_gh()
    done = _gh(directory, ["pr", "view", head, "--json", "number,body"])
    if isinstance(done, str):
        return messages.j15_3_gh_failed(head, done)
    if done.returncode != 0:
        if NO_PULL_REQUEST in done.stderr.lower():
            return messages.j15_4_no_pull_request(head)
        return messages.j15_3_gh_failed(head, _first(done.stderr))
    try:
        found = json.loads(done.stdout)
    except ValueError:
        found = None
    number = found.get("number") if isinstance(found, dict) else None
    if isinstance(number, bool) or not isinstance(number, int):
        return messages.j15_3_gh_failed(head, messages.detail_gh_answer())
    body = found.get("body")
    return PullRequest(number, body if isinstance(body, str) else "")


def run_pr(output: Output, directory: Path, range_text: str) -> int:
    block = block_of(select(output, directory, range_text))
    found = pull_request(directory, gitpart.branch_of(directory, head_of(range_text)))
    if isinstance(found, str):
        output.out(block)
        output.out(found)
        return 0
    done = _gh(
        directory, ["pr", "edit", str(found.number), "--body-file", "-"], with_block(found.body, block)
    )
    if isinstance(done, str) or done.returncode != 0:
        output.out(block)
        detail = done if isinstance(done, str) else _first(done.stderr)
        raise ConfigurationFailure(messages.j6_13_gh_failed(found.number, detail))
    output.out(messages.j15_1_written(found.number))
    return 0


def _first(text: str) -> str:
    lines = text.strip().splitlines()
    return lines[0] if lines else "no message"


def run_notes(output: Output, directory: Path, range_text: str) -> int:
    counted = select(output, directory, range_text).counted
    for held in counted:
        gitpart.write_note(directory, held.sha, messages.j10_counted(held.sha, figures_of(held)))
    output.out(messages.j16_notes(len(counted)))
    return 0
