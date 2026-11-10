"""The count: every complete window of a commit not yet in the file of counts gets one kept line.

It runs under the lock on the file of counts, so two counts at once keep each commit once. Per session it
finds the earliest start its start log holds, orders the session's commits by time, and surveys the session's
transcript and everything under the folder named after it. A window is complete once any of those files holds
a record dated after the commit; a commit whose window is not complete waits for a later pass. A complete
window is copied into a throwaway folder, counted by ccusage, and the folder removed. The kept line is
appended whole after the count, so a count that is killed first leaves none. A commit whose session has no
logged start, or that was made before the session's first logged start, is never counted: no start is made up
from other sessions' transcripts."""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from constitution_layer_kit import identity
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.output import Output

from . import counter as counters
from . import git as gitpart
from . import logs, messages, model, windows
from .model import (
    CommitLine,
    Counted,
    Kept,
    ModelTokens,
    NotCounted,
    Reason,
    Report,
    StartLine,
)

# Finds the pinned ccusage, installing it where the plugin loads in place; asked at the first window to count.
Locate = Callable[[], counters.Ccusage]


@dataclass(slots=True)
class Tally:
    """What one pass did, for the closing line, and the commits that have no kept line."""

    counted: int = 0
    before: int = 0
    not_counted: list[NotCounted] = field(default_factory=list)

    @property
    def waiting(self) -> int:
        return sum(1 for held in self.not_counted if held.reason is Reason.WAITING)

    @property
    def never(self) -> int:
        return len(self.not_counted) - self.waiting


@dataclass(frozen=True, slots=True)
class Scope:
    """Which sessions a pass counts: one, or every session in the logs."""

    session: str | None


def commits_of(commits: Sequence[CommitLine]) -> dict[str, list[CommitLine]]:
    """The logged commits by session, in the order of their time; a SHA logged twice is the first line's."""
    seen: set[str] = set()
    by_session: dict[str, list[CommitLine]] = {}
    for line in commits:
        if line.sha in seen:
            continue
        seen.add(line.sha)
        by_session.setdefault(line.session, []).append(line)
    for held in by_session.values():
        held.sort(key=lambda line: line.ms)
    return by_session


def to_kept(commit: CommitLine, counted: Counted, compactions: int, version: str, counted_ms: int) -> Kept:
    report: Report = counted.report
    tokens: Counter[str] = Counter()
    for entry in report.entries:
        tokens[entry.model] += entry.input + entry.output + entry.cache_write + entry.cache_read
    ordered = sorted(tokens.items(), key=lambda held: (-held[1], held[0]))
    return Kept(
        sha=commit.sha,
        session=commit.session,
        input=sum(entry.input for entry in report.entries),
        output=sum(entry.output for entry in report.entries),
        cache_write=sum(entry.cache_write for entry in report.entries),
        cache_read=sum(entry.cache_read for entry in report.entries),
        total=report.total_tokens,
        cost=report.total_cost,
        replies=len(report.entries),
        models=tuple(ModelTokens(name, held) for name, held in ordered),
        compactions=compactions,
        unpriced=tuple(name for name in counted.unpriced if name in tokens),
        ccusage=version,
        counted_ms=counted_ms,
    )


def count_session(
    session: str,
    commits: list[CommitLine],
    starts: list[StartLine],
    kept: set[str],
    locate: Locate | None,
    folder: Path,
    tally: Tally,
) -> None:
    """Counts what can be counted of one session's commits; with no `locate`, nothing is counted and a
    commit that could be waits. ccusage is asked for only when a window is ready to count."""
    pending = [commit for commit in commits if commit.sha not in kept]
    tally.before += len(commits) - len(pending)
    if not pending:
        return
    if not session:
        tally.not_counted += [NotCounted(commit.sha, Reason.NO_SESSION) for commit in pending]
        return
    if not starts:
        tally.not_counted += [NotCounted(commit.sha, Reason.NO_START, session) for commit in pending]
        return
    first_start = min(starts, key=lambda line: line.ms)
    # a commit made before the session's first logged start has a window that holds no record of the session:
    # a count of it would be 0 tokens made up, so it is named and never counted
    early = {commit.sha for commit in pending if commit.ms < first_start.ms}
    tally.not_counted += [
        NotCounted(commit.sha, Reason.NO_START, session) for commit in pending if commit.sha in early
    ]
    pending = [commit for commit in pending if commit.sha not in early]
    if not pending:
        return
    files: list[windows.Transcript] = []
    for path in dict.fromkeys(line.transcript_path for line in starts):
        files += windows.transcripts_of(Path(path))
    if not files:
        tally.not_counted += [
            NotCounted(commit.sha, Reason.NO_TRANSCRIPT, session, first_start.transcript_path)
            for commit in pending
        ]
        return
    found = windows.survey(files, session, first_start.ms)
    times = [commit.ms for commit in commits]
    countable = {commit.sha for commit in pending}
    ready = {
        index: commit
        for index, commit in enumerate(commits)
        if commit.sha in countable and found.newest_ms is not None and found.newest_ms > commit.ms
    }
    tally.not_counted += [
        NotCounted(commit.sha, Reason.WAITING, session)
        for index, commit in enumerate(commits)
        if commit.sha in countable and (index not in ready or locate is None)
    ]
    if locate is None or not ready:
        return
    counter = locate()
    compactions = windows.compactions_in(found, times)
    try:
        root = Path(tempfile.mkdtemp(prefix=f"{identity.current().namespace}-"))
    except OSError as exc:
        raise ConfigurationFailure(messages.j6_9_no_folder(session, str(exc))) from exc
    try:
        folders = windows.cut(files, session, first_start.ms, found, times, set(ready), root)
        for index, commit in ready.items():
            window = folders.get(index)
            counted = (
                counters.count(counter, window, session)
                if window is not None
                else Counted(Report((), 0, 0.0), ())
            )
            line = to_kept(
                commit, counted, compactions.get(index, 0), counter.version, int(time.time() * 1000)
            )
            logs.append_kept(folder, line)
            kept.add(commit.sha)
            tally.counted += 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def count_all(output: Output, scope: Scope, folder: Path, locate: Locate | None) -> Tally:
    starts, start_notes = logs.read_starts(folder)
    commits, commit_notes = logs.read_commits(folder)
    counts, count_notes = logs.read_counts(folder)
    for note in (*start_notes, *commit_notes, *count_notes):
        output.out(note)
    kept = {line.sha for line in counts}
    tally = Tally()
    starts_of: dict[str, list[StartLine]] = {}
    for line in starts:
        starts_of.setdefault(line.session, []).append(line)
    for session, held in commits_of(commits).items():
        if scope.session is None or session == scope.session:
            count_session(session, held, starts_of.get(session, []), kept, locate, folder, tally)
    return tally


def run(output: Output, scope: Scope, directory: Path) -> int:
    """One pass over the clone's logs; exit 0, the closing line saying what it did."""
    folder = logs.folder_of(gitpart.common_directory(directory))
    named = os.environ.get("CLAUDE_PLUGIN_DATA")
    if named:  # in a hook: keep the folder for a run by hand, whose shell has no such variable
        logs.record_plugin_data(folder, named)
    data = Path(named) if named else logs.recorded_plugin_data(folder)
    with logs.locked(folder, model.LOCK_SECONDS) as held:
        if held:
            found: list[counters.Ccusage] = []

            def locate() -> counters.Ccusage:
                """The first window to count asks; a later one has the answer."""
                if not found:
                    root = identity.current().plugin_root
                    found.append(counters.locate(root, data, output))
                return found[0]

            tally = count_all(output, scope, folder, locate)
        else:
            output.out(messages.j5_2_lock_held())
            tally = count_all(output, scope, folder, None)
    output.out(messages.j3_counted(tally.counted, tally.before, tally.waiting, tally.never))
    return 0
