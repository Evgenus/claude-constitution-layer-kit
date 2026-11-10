"""The two logs of the module, its file of counts and the lock on that file.

They stand in the folder FOLDER of git's common directory, which every worktree of a clone shares, and are
never committed or pushed; beside them stands one small file, the plugin's data folder as a hook saw it. A log
is appended one whole JSON line at a time, in one write; a line that cannot be read is left out of the reading
and named in a note, and never stops it. The module writes no file in the working tree."""

from __future__ import annotations

import fcntl
import json
import os
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path

from . import messages
from .model import (
    COMMITS,
    COUNTS,
    FOLDER,
    LOCK,
    PLUGIN_DATA,
    STARTS,
    CommitLine,
    Kept,
    ModelTokens,
    StartLine,
)

JSON_LINE = (",", ":")


class Unreadable(Exception):
    """A log line that cannot be read; `detail` says why, in the words of the note."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def folder_of(common: Path) -> Path:
    return common / FOLDER


def _text(line: Mapping[str, object], name: str) -> str:
    value = line.get(name)
    if not isinstance(value, str):
        raise Unreadable(messages.detail_field(name))
    return value


def _whole(line: Mapping[str, object], name: str) -> int:
    value = line.get(name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise Unreadable(messages.detail_field(name))
    return value


def _number(line: Mapping[str, object], name: str) -> float:
    value = line.get(name)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise Unreadable(messages.detail_field(name))
    return float(value)


def _object(raw: str) -> Mapping[str, object]:
    try:
        parsed: object = json.loads(raw)
    except ValueError as exc:
        raise Unreadable(messages.detail_not_json()) from exc
    if not isinstance(parsed, dict):
        raise Unreadable(messages.detail_not_an_object())
    return {str(key): value for key, value in parsed.items()}


def parse_start(line: Mapping[str, object]) -> StartLine:
    return StartLine(
        _text(line, "session"), _whole(line, "ms"), _text(line, "source"), _text(line, "transcript_path")
    )


def parse_commit(line: Mapping[str, object]) -> CommitLine:
    return CommitLine(_text(line, "sha"), _whole(line, "ms"), _text(line, "session"), _text(line, "event"))


def _models(line: Mapping[str, object]) -> tuple[ModelTokens, ...]:
    models = line.get("models")
    if not isinstance(models, dict):
        raise Unreadable(messages.detail_field("models"))
    held = []
    for name, tokens in models.items():
        if isinstance(tokens, bool) or not isinstance(tokens, int):
            raise Unreadable(messages.detail_field("models"))
        held.append(ModelTokens(str(name), tokens))
    return tuple(held)


def _unpriced(line: Mapping[str, object]) -> tuple[str, ...]:
    names = line.get("unpriced")
    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise Unreadable(messages.detail_field("unpriced"))
    return tuple(str(name) for name in names)


def parse_kept(line: Mapping[str, object]) -> Kept:
    return Kept(
        sha=_text(line, "sha"),
        session=_text(line, "session"),
        input=_whole(line, "input"),
        output=_whole(line, "output"),
        cache_write=_whole(line, "cache_write"),
        cache_read=_whole(line, "cache_read"),
        total=_whole(line, "total"),
        cost=_number(line, "cost"),
        replies=_whole(line, "replies"),
        models=_models(line),
        compactions=_whole(line, "compactions"),
        unpriced=_unpriced(line),
        ccusage=_text(line, "ccusage"),
        counted_ms=_whole(line, "counted_ms"),
    )


def kept_object(kept: Kept) -> dict[str, object]:
    """The kept line as the JSON object written to the file of counts, in the order of its fields."""
    return {
        "sha": kept.sha,
        "session": kept.session,
        "input": kept.input,
        "output": kept.output,
        "cache_write": kept.cache_write,
        "cache_read": kept.cache_read,
        "total": kept.total,
        "cost": kept.cost,
        "replies": kept.replies,
        "models": {held.model: held.tokens for held in kept.models},
        "compactions": kept.compactions,
        "unpriced": list(kept.unpriced),
        "ccusage": kept.ccusage,
        "counted_ms": kept.counted_ms,
    }


def _each(path: Path) -> Iterator[tuple[int, str]]:
    """The numbered lines of the log that hold anything; a missing file is an empty log."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return
    for number, raw in enumerate(text.splitlines(), start=1):
        if raw.strip():
            yield number, raw


def read_starts(folder: Path) -> tuple[list[StartLine], list[str]]:
    """Every line of the start log that can be read, and a note for each that cannot."""
    path = folder / STARTS
    items: list[StartLine] = []
    notes: list[str] = []
    for number, raw in _each(path):
        try:
            items.append(parse_start(_object(raw)))
        except Unreadable as exc:
            notes.append(messages.j5_1_unreadable_line(str(path), number, exc.detail))
    return items, notes


def read_commits(folder: Path) -> tuple[list[CommitLine], list[str]]:
    """Every line of the commit log that can be read, and a note for each that cannot."""
    path = folder / COMMITS
    items: list[CommitLine] = []
    notes: list[str] = []
    for number, raw in _each(path):
        try:
            items.append(parse_commit(_object(raw)))
        except Unreadable as exc:
            notes.append(messages.j5_1_unreadable_line(str(path), number, exc.detail))
    return items, notes


def read_counts(folder: Path) -> tuple[list[Kept], list[str]]:
    """Every line of the file of counts that can be read, and a note for each that cannot."""
    path = folder / COUNTS
    items: list[Kept] = []
    notes: list[str] = []
    for number, raw in _each(path):
        try:
            items.append(parse_kept(_object(raw)))
        except Unreadable as exc:
            notes.append(messages.j5_1_unreadable_line(str(path), number, exc.detail))
    return items, notes


def append_line(path: Path, line: Mapping[str, object]) -> None:
    """One whole line in one write on a descriptor opened for appending: a reader sees all of it or none."""
    data = (json.dumps(line, separators=JSON_LINE, ensure_ascii=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(descriptor, data)
    finally:
        os.close(descriptor)


def append_kept(folder: Path, kept: Kept) -> None:
    append_line(folder / COUNTS, kept_object(kept))


def record_plugin_data(folder: Path, data: str) -> None:
    """Keeps the plugin's data folder, as a hook saw it in `CLAUDE_PLUGIN_DATA`, for the run by hand that has
    no such variable. One line, written whole and swapped in by a rename, and only when it differs."""
    path = folder / PLUGIN_DATA
    try:
        if path.read_text(encoding="utf-8") == data:
            return
    except OSError:
        pass
    folder.mkdir(parents=True, exist_ok=True)
    temporary = folder / f"{PLUGIN_DATA}.{os.getpid()}"
    temporary.write_text(data, encoding="utf-8")
    os.replace(temporary, path)


def recorded_plugin_data(folder: Path) -> Path | None:
    """The data folder a hook recorded, when none is recorded or the folder is gone, None."""
    try:
        text = (folder / PLUGIN_DATA).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return Path(text) if text and Path(text).is_dir() else None


@contextmanager
def locked(folder: Path, seconds: float) -> Iterator[bool]:
    """The lock on the file of counts: True once held, False when another count kept it for `seconds`. The
    lock is the operating system's, so it falls with a process that is killed."""
    folder.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(folder / LOCK, os.O_RDWR | os.O_CREAT, 0o644)
    held = False
    try:
        deadline = time.monotonic() + seconds
        while not held:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                held = True
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.05)
        yield held
    finally:
        if held:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)
