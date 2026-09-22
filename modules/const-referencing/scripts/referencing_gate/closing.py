"""How the mover closes a failure: honestly about what had been changed by then. It stands apart
from the acts because the entry needs it before the preflight, and the acts are loaded after."""

from __future__ import annotations

from dataclasses import dataclass

from . import messages


@dataclass(slots=True)
class Closing:
    """The line that closes a failure. Before the act has changed anything it can say so; once a
    file has moved or been rewritten it must not."""

    changed: bool = False

    def __call__(self) -> str:
        return messages.v4_stopped_midway() if self.changed else messages.v4_nothing_changed()
