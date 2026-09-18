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
from .model import ToolEvent
from .repository import read_text


def read_event(stream: TextIO) -> ToolEvent:
    """Unparseable input is a configuration failure, never an empty event: a gate that
    cannot read its input has produced no verdict."""
    try:
        loaded: object = json.load(stream)
    except ValueError as exc:
        raise ConfigurationFailure(messages.c12_input(str(exc))) from exc
    if not isinstance(loaded, dict):
        raise ConfigurationFailure(messages.c12_input("the top level is not an object"))
    tool_input = loaded.get("tool_input")
    fields: dict[object, object] = tool_input if isinstance(tool_input, dict) else {}
    return ToolEvent(
        tool_name=_text(loaded.get("tool_name")) or "",
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
    """None when the tool itself will fail (no content, missing file, absent old_string):
    there is nothing to judge, and the tool reports its own error."""
    if event.tool_name == "Write":
        return event.content
    current = read_text(root, rel)
    if current is None or event.old_string is None or event.new_string is None:
        return None
    if event.old_string not in current:
        return None
    if event.replace_all:
        return current.replace(event.old_string, event.new_string)
    return current.replace(event.old_string, event.new_string, 1)
