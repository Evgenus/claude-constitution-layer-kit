"""The evidence the effect report reads: the session transcripts and a module's output log, each read into
typed records.

A transcript is the platform's own file, one JSON object per line, whose format Claude Code does not
document (limit 17 of §4 of kit-shared-gate-code). The reader takes the fields it knows and skips every
other line, and it counts the lines it could not read, so that a changed format shows as unread lines in
the report and never as a quiet count of nothing. What it knows, observed on Claude Code 2.1.286 on
2026-11-07:

- a line of type ``user`` whose ``message.content`` is a string, or a list of text blocks, and which is
  no tool result and not marked ``isMeta``, is a human turn;
- a line of type ``assistant`` carries blocks: ``tool_use`` (``id``, ``name``, ``input``) and ``text``;
- a line of type ``attachment`` whose ``attachment`` has a ``hookName`` is a hook run: ``toolUseID`` names
  the tool call it examined, ``hookEvent`` the event; ``command``, ``exitCode`` and ``stdout`` stand on a
  run that let the call through, ``blockingError`` on a run that blocked it, whose text opens with the
  command in brackets, ``[sh <script>]:``.

Every line carries ``timestamp``, ``sessionId`` and ``cwd``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from . import repository

SCRIPT = re.compile(r"scripts/([A-Za-z0-9_.-]+\.(?:sh|py))\b")  # a hook's script, by its file name
BLOCKED_COMMAND = re.compile(r"\A\[([^\]]*)\]:")  # the command a blocking run's text opens with


@dataclass(frozen=True, slots=True)
class HumanTurn:
    at: str
    text: str


@dataclass(frozen=True, slots=True)
class ToolCall:
    at: str
    id: str
    name: str
    input: Mapping[str, object]

    def names(self) -> str:
        """What the call acts on, as a hook's event names it: the file, or the shell tool's command."""
        for key in ("file_path", "command"):
            value = self.input.get(key)
            if isinstance(value, str):
                return value
        return ""


@dataclass(frozen=True, slots=True)
class HookRun:
    at: str
    tool_use_id: str  # the call it examined; empty for a run on an event without a call
    hook: str  # the platform's name for it, `PreToolUse:Write`
    script: str  # the file name of the script it ran, `check-references.sh`; empty when unknown
    exit_code: int | None
    blocked: bool
    text: str  # what it printed: its standard output, or the blocking text


@dataclass(frozen=True, slots=True)
class AssistantText:
    at: str
    text: str


Event = HumanTurn | ToolCall | HookRun | AssistantText


@dataclass(frozen=True, slots=True)
class Session:
    id: str
    transcript: str
    events: tuple[Event, ...]
    cwds: frozenset[str]
    unread: int  # lines that are no JSON object

    def calls(self) -> Iterator[ToolCall]:
        return (e for e in self.events if isinstance(e, ToolCall))

    def hook_runs(self) -> Iterator[HookRun]:
        return (e for e in self.events if isinstance(e, HookRun))


@dataclass(frozen=True, slots=True)
class LogRecord:
    at: str
    gate: str
    mode: str
    session: str
    path: str
    transcript: str
    stream: str
    text: str


@dataclass(slots=True)
class _Reading:
    session: str = ""
    events: list[Event] = field(default_factory=list)
    cwds: set[str] = field(default_factory=set)
    unread: int = 0


def script_of(command: str) -> str:
    found = SCRIPT.search(command)
    return found[1] if found else ""


def read_transcript(path: Path) -> Session | None:
    """The session one transcript holds; None when the file cannot be read at all."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    reading = _Reading()
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            loaded: object = json.loads(line)
        except ValueError:
            reading.unread += 1
            continue
        if not isinstance(loaded, dict):
            reading.unread += 1
            continue
        _take(reading, loaded)
    return Session(
        reading.session or path.stem,
        str(path),
        tuple(reading.events),
        frozenset(reading.cwds),
        reading.unread,
    )


def _take(reading: _Reading, line: Mapping[str, object]) -> None:
    at = _text(line.get("timestamp"))
    reading.session = reading.session or _text(line.get("sessionId"))
    cwd = _text(line.get("cwd"))
    if cwd:
        reading.cwds.add(cwd)
    kind = line.get("type")
    message = line.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if kind == "user" and not line.get("isMeta"):
        human = _human_text(content)
        if human is not None:
            reading.events.append(HumanTurn(at, human))
    elif kind == "assistant" and isinstance(content, list):
        reading.events.extend(_assistant_events(at, content))
    elif kind == "attachment":
        run = _hook_run(at, line.get("attachment"))
        if run is not None:
            reading.events.append(run)


def _human_text(content: object) -> str | None:
    if isinstance(content, str):
        return content
    if not isinstance(content, list) or not content:
        return None
    if not all(isinstance(block, dict) and block.get("type") == "text" for block in content):
        return None  # a tool result, an image, or a block of a kind not known
    return "\n".join(_text(block.get("text")) for block in content if isinstance(block, dict))


def _assistant_events(at: str, content: Sequence[object]) -> Iterator[Event]:
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            given = block.get("input")
            yield ToolCall(
                at, _text(block.get("id")), _text(block.get("name")), given if isinstance(given, dict) else {}
            )
        elif block.get("type") == "text":
            yield AssistantText(at, _text(block.get("text")))


def _hook_run(at: str, attachment: object) -> HookRun | None:
    if not isinstance(attachment, dict) or not isinstance(attachment.get("hookName"), str):
        return None
    blocking = attachment.get("blockingError")
    if isinstance(blocking, dict):
        blocking = blocking.get("blockingError")
    if isinstance(blocking, str):
        opened = BLOCKED_COMMAND.match(blocking)
        command = opened[1] if opened else ""
        printed = blocking
    else:
        command = _text(attachment.get("command"))
        printed = _text(attachment.get("stdout")) or _text(attachment.get("content"))
    code = attachment.get("exitCode")
    exit_code = int(code) if isinstance(code, int | str) and str(code).lstrip("-").isdigit() else None
    return HookRun(
        at,
        _text(attachment.get("toolUseID")),
        _text(attachment.get("hookName")),
        script_of(command),
        exit_code,
        isinstance(blocking, str),
        printed,
    )


def read_log(directory: Path, namespace: str) -> list[LogRecord]:
    """A module's output log, the rotated file first, as records; a line that is no record is skipped."""
    records: list[LogRecord] = []
    for name in (f"{namespace}.jsonl.1", f"{namespace}.jsonl"):
        text = repository.read_text(directory, name)
        for line in (text or "").splitlines():
            try:
                loaded: object = json.loads(line)
            except ValueError:
                continue
            if isinstance(loaded, dict):
                records.append(
                    LogRecord(
                        *(_text(loaded.get(key)) for key in ("ts", "gate", "mode", "session")),
                        *(_text(loaded.get(key)) for key in ("path", "transcript", "stream", "text")),
                    )
                )
    return records


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""
