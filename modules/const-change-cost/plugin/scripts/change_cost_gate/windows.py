"""The cutter: one session's records into the windows of its commits, copied into a throwaway folder.

Of a record it reads its time, its session id, its message id, its request id and its type, and nothing
else: no token count is read here, every figure of a count comes from ccusage's output. A session owns the
records dated at or after its earliest start and carrying its id, so the history a fork copies in stays with
the session that made it. All the records of one reply, one message id and one request id, go into the
window of the reply's first record. A window runs from the session's previous commit, or its start, up to
the commit's time. The copy is made of plain files in the layout ccusage walks, `projects/<project>/...`,
each line byte for byte as it was read."""

from __future__ import annotations

import json
import os
from bisect import bisect_left
from contextlib import ExitStack
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import BinaryIO

from .model import COMPACTION, ReplyKey

EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
MILLISECOND = timedelta(milliseconds=1)


@dataclass(frozen=True, slots=True)
class Record:
    """The five things read of one line of a transcript."""

    ms: int
    key: ReplyKey | None  # message id and request id; None for a record that is no reply
    compaction: bool


@dataclass(frozen=True, slots=True)
class Transcript:
    """One file of a session's copy: where it stands, and where its copy goes under `projects/`."""

    path: Path
    destination: Path  # relative to the folder `projects/`: the project's folder, then the file's place in it


@dataclass(slots=True)
class Survey:
    """What one pass over a session's files finds: the first record of each reply, the newest record of any
    kind, and the time of each compaction; records before the start are not in it, bar the newest."""

    first: dict[ReplyKey, int] = field(default_factory=dict)
    newest_ms: int | None = None
    compactions: list[int] = field(default_factory=list)


def milliseconds(stamp: str) -> int | None:
    """An ISO 8601 time as whole milliseconds since the epoch, or None when it is none."""
    try:
        moment = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return (moment - EPOCH) // MILLISECOND


def read_record(raw: bytes, session: str) -> Record | None:
    """The record a line holds, or None for a line that is no record of the session: it cannot be read, it has
    no time, or it names another session."""
    try:
        parsed: object = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(parsed, dict):
        return None
    stamp = parsed.get("timestamp")
    ms = milliseconds(stamp) if isinstance(stamp, str) else None
    owner = parsed.get("sessionId")
    if ms is None or (isinstance(owner, str) and owner and owner != session):
        return None
    message = parsed.get("message")
    identifier = message.get("id") if isinstance(message, dict) else None
    request = parsed.get("requestId")
    key: ReplyKey | None = None
    if isinstance(identifier, str) and identifier:
        key = (identifier, request if isinstance(request, str) else None)
    compaction = COMPACTION in (parsed.get("type"), parsed.get("subtype"))
    return Record(ms, key, compaction)


def transcripts_of(path: Path) -> list[Transcript]:
    """The session's transcript and every `.jsonl` under the folder named after it, plain files only: a
    symbolic link is left out, as ccusage's own walk leaves it out."""
    base = path.parent.parent
    found: list[Path] = []
    if path.is_file() and not path.is_symlink():
        found.append(path)
    folder = path.with_suffix("")
    for top, _, names in os.walk(folder, followlinks=False):
        for name in sorted(names):
            candidate = Path(top) / name
            if name.endswith(".jsonl") and candidate.is_file() and not candidate.is_symlink():
                found.append(candidate)
    return [Transcript(candidate, candidate.relative_to(base)) for candidate in found]


def survey(files: list[Transcript], session: str, start_ms: int) -> Survey:
    """One pass over every line of the session's files."""
    found = Survey()
    for transcript in files:
        with transcript.path.open("rb") as handle:
            for raw in handle:
                record = read_record(raw, session)
                if record is None:
                    continue
                if found.newest_ms is None or record.ms > found.newest_ms:
                    found.newest_ms = record.ms
                if record.ms < start_ms:
                    continue
                if record.key is not None and (
                    record.key not in found.first or record.ms < found.first[record.key]
                ):
                    found.first[record.key] = record.ms
                if record.compaction:
                    found.compactions.append(record.ms)
    return found


def window_of(ms: int, commit_times: list[int]) -> int:
    """The index of the first commit at or after `ms`; the list's length when `ms` falls after the last."""
    return bisect_left(commit_times, ms)


def compactions_in(found: Survey, commit_times: list[int]) -> dict[int, int]:
    """How many compactions fall in each window."""
    counted: dict[int, int] = {}
    for ms in found.compactions:
        index = window_of(ms, commit_times)
        counted[index] = counted.get(index, 0) + 1
    return counted


def cut(
    files: list[Transcript],
    session: str,
    start_ms: int,
    found: Survey,
    commit_times: list[int],
    wanted: set[int],
    root: Path,
) -> dict[int, Path]:
    """Copies the lines of each wanted window into `root/w<index>/projects/...` and returns the folders of the
    windows that hold any line; a wanted window with none has no folder."""
    folders: dict[int, Path] = {}
    for transcript in files:
        with ExitStack() as stack, transcript.path.open("rb") as handle:
            opened: dict[int, BinaryIO] = {}
            for raw in handle:
                record = read_record(raw, session)
                if record is None or record.ms < start_ms:
                    continue
                at = found.first.get(record.key, record.ms) if record.key is not None else record.ms
                index = window_of(at, commit_times)
                if index not in wanted:
                    continue
                if index not in opened:
                    folder = root / f"w{index}"
                    target = folder / "projects" / transcript.destination
                    target.parent.mkdir(parents=True, exist_ok=True)
                    opened[index] = stack.enter_context(target.open("ab"))
                    folders[index] = folder
                opened[index].write(raw if raw.endswith(b"\n") else raw + b"\n")
    return folders
