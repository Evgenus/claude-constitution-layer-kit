"""How the mover closes a failure: honestly about what had been changed by then. It stands apart
from the acts because the entry needs it before the preflight, and the acts are loaded after."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from constitution_layer_kit.repository import git

from . import messages


@dataclass(slots=True)
class Closing:
    """The line that closes a failure, and the one that closes an interrupt.

    A failure is raised by the act itself, between two of its statements, so its line reads the act's own
    state: before the act has changed anything it can say so; once a folder is made, a file moved or a
    document rewritten it must not. A move undone says so and names the file; a move back that failed says
    where the file is, before the line that the act stopped midway.

    An interrupt can land between any two statements, so its line reads no flag set along the way. It is
    made from what it observes when it is asked for (`interrupted`): where git's index and the disk hold the
    file, by the exact name, and which of the folders the move would make now stand. Whether a document was
    rewritten is the one thing it cannot observe; `rewrote` says it, set before the first write opens."""

    changed: bool = False
    moved_back: str = ""  # the path a move was undone to, when it was
    stranded: str = ""  # the line saying where the file is, when the move back failed
    root: Path | None = None  # the repository, once the act knows it
    move: tuple[str, str] | None = None  # (old, new) of an act that moves, set before the move begins
    planned: tuple[Path, ...] = field(default_factory=tuple)  # the folders it would make, deepest first
    rewrote: bool = False  # set before the first rewrite opens: no look at the tree can tell it

    def __call__(self) -> str:
        if self.stranded:
            return self.stranded + "\n" + messages.v4_stopped_midway()
        if self.changed:
            return messages.v4_stopped_midway()
        if self.moved_back:
            return messages.v4_moved_back(self.moved_back)
        return messages.v4_nothing_changed()

    def interrupted(self) -> str:
        """The line the shared guard prints after an interrupt, made from what the tree shows now. A second
        interrupt while it looks leaves it unable to say, and the line says the file may stand at either
        path."""
        if self.move is None or self.root is None:
            return messages.v4_stopped_midway() if self.rewrote else messages.v4_nothing_changed()
        old, new = self.move
        try:
            at = where(self.root, old, new)
            standing = [folder for folder in self.planned if _stands(folder)]
        except KeyboardInterrupt:
            at, standing = None, []
        if at is None:
            return messages.v4_either(old, new) + "\n" + messages.v4_stopped_midway()
        if at == new:
            return messages.v4_at_new(old, new) + "\n" + messages.v4_stopped_midway()
        if standing:
            shown = [folder.relative_to(self.root).as_posix() for folder in standing]
            line = messages.v4_folders_stand(old, shown)
            return line + "\n" + messages.v4_stopped_midway() if self.rewrote else line
        return messages.v4_stopped_midway() if self.rewrote else messages.v4_nothing_changed()


def where(root: Path, old: str, new: str) -> str | None:
    """`old` or `new` where git's index and the disk both hold the file there and not at the other path;
    None where they do not agree."""
    index = (_indexed(root, old), _indexed(root, new))
    disk = (_on_disk(root / old), _on_disk(root / new))
    if index == disk == (True, False):
        return old
    if index == disk == (False, True):
        return new
    return None


def _indexed(root: Path, rel: str) -> bool:
    """Whether git's index holds the path, by its exact name: where git itself says a file is."""
    return git(["ls-files", "--error-unmatch", "--", rel], cwd=root).returncode == 0


def _on_disk(path: Path) -> bool:
    """Whether the disk holds the path by its exact name: a folder's listing, so that a disk that ignores
    case cannot answer for a name in another case."""
    try:
        return path.name in os.listdir(path.parent)
    except OSError:
        return False


def _stands(folder: Path) -> bool:
    """A folder the move would make stands, by its exact name."""
    return _on_disk(folder) and folder.is_dir()
