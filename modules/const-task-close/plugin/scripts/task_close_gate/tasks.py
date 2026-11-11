"""The Stop event's task list, parsed once into typed entries. The shared reader takes the event
and carries no task list, so this module reads `background_tasks` from the event's text itself.
The field is the platform's to send: an event without it, a list that is no list and an entry
whose `type` or `status` is no text give no entry here, and nothing raises."""

from __future__ import annotations

import json

from .model import Task


def in_flight(payload: str) -> tuple[Task, ...]:
    """The entries of `background_tasks` that carry a `type` and a `status` as text, in order."""
    try:
        event: object = json.loads(payload)
    except ValueError:  # the shared reader has refused such an event before this is asked
        return ()
    listed = event.get("background_tasks") if isinstance(event, dict) else None
    if not isinstance(listed, list):
        return ()
    return tuple(task for entry in listed if (task := _task(entry)) is not None)


def _task(entry: object) -> Task | None:
    if not isinstance(entry, dict):
        return None
    kind, status = entry.get("type"), entry.get("status")
    return Task(kind, status) if isinstance(kind, str) and isinstance(status, str) else None
