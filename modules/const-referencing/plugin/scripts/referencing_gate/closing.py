"""How the mover closes a failure: honestly about what had been changed by then. It stands apart
from the acts because the entry needs it before the preflight, and the acts are loaded after."""

from __future__ import annotations

import errno
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from constitution_layer_kit.repository import git

from . import messages


@dataclass(slots=True)
class Closing:
    """The line that closes a failure, and the one that closes an interrupt.

    Both are made from what the tree shows when the line is asked for, so no failure path keeps its own
    account of what it changed: where git's index and the disk hold the file, by the exact name, and which
    of the folders the move would make now stand. Whether a document was rewritten is the one thing it
    cannot observe; `rewrote` says it, set before the first write opens, and `writing` names the document
    whose open emptied it until its text is written. A failure adds what the act knows of its own move back
    where the tree agrees with it: one git made, its folders gone, says the file was moved back; one git
    refused gives git's words."""

    moved_back: str = ""  # the path git moved the file back to, when it did
    stranded: str = ""  # the line giving git's words, when git refused the move back
    root: Path | None = None  # the repository, once the act knows it
    move: tuple[str, str] | None = None  # (old, new) of an act that moves, set before the move begins
    planned: tuple[Path, ...] = field(default_factory=tuple)  # the folders it would make, deepest first
    rewrote: bool = False  # set before the first rewrite opens: no look at the tree can tell it
    writing: str = ""  # the document being rewritten, from before its open until its text is written
    unmade: dict[Path, str] = field(default_factory=dict)  # a folder the move made that stayed: the reason

    def __call__(self) -> str:
        """The line that closes a failure, made as an interrupt's is."""
        return self._observed(failure=True)

    def interrupted(self) -> str:
        """The line the shared guard prints after an interrupt, made from what the tree shows now: where the
        file stands, the folders the move made that stand, the document being written, if one was, and the
        midway line wherever the file moved, its place is unknown, or a document was rewritten. A second
        interrupt while it looks leaves it unable to say, and the line says the file may stand at either
        path."""
        return self._observed(failure=False)

    def _observed(self, failure: bool) -> str:
        place, midway = self._place(failure)
        lines = [place] if place else []
        if self.writing:  # opened, so perhaps emptied, and its text perhaps not written
            lines.append(messages.v4_cut_short(self.writing, self._held(self.writing)))
        if midway or self.rewrote:
            lines.append(messages.v4_stopped_midway())
        return "\n".join(lines) if lines else messages.v4_nothing_changed()

    def _place(self, failure: bool) -> tuple[str, bool]:
        """The line of where the file stands, as observed now, and whether the midway line follows it. An act
        that moves nothing, and a file at its old path with no folder of the move standing, give no line,
        save for a failure whose move back was made."""
        if self.move is None or self.root is None:
            return "", False
        old, new = self.move
        try:
            at = where(self.root, old, new)
            standing = [folder for folder in self.planned if _stands(folder)]
        # a second interrupt, or a look the system refuses or git cannot answer: nobody can say
        except (KeyboardInterrupt, Exception):
            at, standing = None, []
        if at is None:
            return messages.v4_either(old, new), True
        if at == new:
            return (self.stranded if failure and self.stranded else messages.v4_at_new(old, new)), True
        if standing:
            shown = [
                (folder.relative_to(self.root).as_posix(), self.unmade.get(folder, "")) for folder in standing
            ]
            return messages.v4_folders_stand(old, shown), False
        if failure and self.moved_back == old:
            return messages.v4_moved_back(old), False
        return "", False

    def _held(self, rel: str) -> bool | None:
        """Whether git's index holds the document being written, so that git restore can bring its text back:
        None where it cannot say."""
        if self.root is None:
            return None
        try:
            return _indexed(self.root, rel)
        except (KeyboardInterrupt, Exception):
            return None


def where(root: Path, old: str, new: str) -> str | None:
    """`old` or `new` where git's index and the disk both hold the file there and not at the other path;
    None where they do not agree."""
    index = (_indexed(root, old), _indexed(root, new))
    disk = (_on_disk(root / old), _on_disk(root / new))
    if None in index:  # git gave no answer of either kind: nobody can say
        return None
    if index == disk == (True, False):
        return old
    if index == disk == (False, True):
        return new
    return None


def _indexed(root: Path, rel: str) -> bool | None:
    """Whether git's index holds the path, by its exact name: where git itself says a file is. git exits 0
    where it holds it and 1 where it does not; any other answer is None, nobody can say."""
    code = git(["ls-files", "--error-unmatch", "--", rel], cwd=root).returncode
    return True if code == 0 else False if code == 1 else None


def _on_disk(path: Path) -> bool:
    """Whether the disk holds the path by its exact name: a folder's listing, so that a disk that ignores
    case cannot answer for a name in another case."""
    try:
        return path.name in os.listdir(path.parent)
    except OSError as exc:
        # its folder is gone, or no file can stand at a name the system refuses for its length
        if exc.errno in (errno.ENOENT, errno.ENOTDIR, errno.ENAMETOOLONG):
            return False
        raise  # any other answer: nobody can say, and the line says so


def _stands(folder: Path) -> bool:
    """A folder the move would make stands, by its exact name, asked of the system the same way on every
    Python: os.stat, whose error the line reads as nobody can say."""
    return _on_disk(folder) and stat.S_ISDIR(os.stat(folder).st_mode)
