"""How the mover closes a failure: honestly about what had been changed by then. It stands apart
from the acts because the entry needs it before the preflight, and the acts are loaded after."""

from __future__ import annotations

from dataclasses import dataclass

from . import messages


@dataclass(slots=True)
class Closing:
    """The line that closes a failure. Before the act has changed anything it can say so; once a
    file has moved or been rewritten it must not. A move undone says so and names the file; a move back
    that failed says where the file is, before the line that the act stopped midway."""

    changed: bool = False
    moved_back: str = ""  # the path a move was undone to, when it was
    stranded: str = ""  # the line saying where the file is, when the move back failed

    def __call__(self) -> str:
        if self.stranded:
            return self.stranded + "\n" + messages.v4_stopped_midway()
        if self.changed:
            return messages.v4_stopped_midway()
        if self.moved_back:
            return messages.v4_moved_back(self.moved_back)
        return messages.v4_nothing_changed()
