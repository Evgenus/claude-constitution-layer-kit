"""The hook payload, parsed once into a typed event, and the document a write would produce.

A pre-write gate judges the document that will exist, not the one that does: for a Write
that is the content field; for an Edit it is the edit applied to the file on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from . import messages
from .errors import ConfigurationFailure
from .model import FileTool, ToolEvent
from .repository import read_text


def read_event(stream: TextIO) -> ToolEvent:
    """Unparseable input is a configuration failure, never an empty event, and so is an
    event for a judged tool that lacks the fields the platform documents: a gate that
    cannot read its input has produced no verdict."""
    try:
        loaded: object = json.load(stream)
    except ValueError as exc:
        raise ConfigurationFailure(messages.c12_input(str(exc))) from exc
    if not isinstance(loaded, dict):
        raise ConfigurationFailure(messages.c12_input(messages.detail_not_an_object()))
    tool_name = _text(loaded.get("tool_name")) or ""
    tool = FileTool(tool_name) if tool_name in {t.value for t in FileTool} else None
    tool_input = loaded.get("tool_input")
    fields: dict[object, object] = tool_input if isinstance(tool_input, dict) else {}
    if tool is not None:
        required = (
            ("file_path", "content") if tool is FileTool.WRITE else ("file_path", "old_string", "new_string")
        )
        for name in required:
            if not isinstance(fields.get(name), str) or (name == "file_path" and not fields.get(name)):
                raise ConfigurationFailure(messages.c12_input(messages.detail_tool_input(tool.value, name)))
    return ToolEvent(
        tool=tool,
        tool_name=tool_name,
        file_path=_text(fields.get("file_path")) or "",
        cwd=_text(loaded.get("cwd")) or "",
        session_id=_text(loaded.get("session_id")) or "",
        content=_text(fields.get("content")),
        old_string=_text(fields.get("old_string")),
        new_string=_text(fields.get("new_string")),
        replace_all=fields.get("replace_all") is True,
    )


def _text(value: object) -> str | None:
    return value if isinstance(value, str) else None


def document_after_write(event: ToolEvent, root: Path, rel: str) -> str | None:
    """None when the Edit cannot be applied (missing file, absent old_string): there is
    nothing to judge, and the tool reports its own error. An Edit of a missing file with an
    empty old_string creates the file from new_string, so that is what is judged."""
    if event.tool is FileTool.WRITE:
        return event.content
    current = read_text(root, rel)
    if current is None and event.old_string == "" and event.new_string is not None:
        return event.new_string
    if current is None or event.old_string is None or event.new_string is None:
        return None
    if event.old_string not in current:
        return None
    if event.replace_all:
        return current.replace(event.old_string, event.new_string)
    return current.replace(event.old_string, event.new_string, 1)
