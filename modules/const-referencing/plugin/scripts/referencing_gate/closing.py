"""How the mover closes a failure: honestly about what had been changed by then. It stands apart
from the acts because the entry needs it before the preflight, and the acts are loaded after."""

from __future__ import annotations

import errno
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from constitution_layer_kit.repository import git, stat_or_none

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
    scanned: bool = False  # set just before the closing scan prints its verdict, which may then stand above

    def __call__(self) -> str:
        """The line that closes a failure, made as an interrupt's is. An interrupt while it is made goes on to
        the shared guard, which then closes the run as for any interrupt; an error says nobody can say."""
        try:
            return self._observed(failure=True)
        except Exception:
            return self._unknown(failure=True)

    def interrupted(self) -> str:
        """The line the shared guard prints after an interrupt, made from what the tree shows now: where the
        file stands, the folders the move made that stand, the document being written, if one was, and the
        midway line wherever the file moved, its place is unknown, or a document was rewritten. A second
        interrupt anywhere in the making of the line leaves it unable to say, and the line says the file may
        stand at either path."""
        try:
            return self._observed(failure=False)
        except (KeyboardInterrupt, Exception):
            return self._unknown(failure=False)

    def _unknown(self, failure: bool) -> str:
        """The line where its making was cut short: nothing looked at, so nothing claimed but what may be."""
        if self.move is None:
            return messages.v4_stopped_midway()
        return messages.v4_either(*self.move, interrupted=not failure) + "\n" + messages.v4_stopped_midway()

    def _observed(self, failure: bool) -> str:
        if self.scanned:  # the scan has begun to print its verdict, which may stand above
            return messages.v4_verdict_may()
        place, midway = self._place(failure)
        lines = [place] if place else []
        if (
            self.writing and self.root is not None
        ):  # perhaps opened, so emptied, and its text perhaps not written
            here = from_here(self.root, self.writing)
            lines.append(messages.v4_cut_short(self.writing, self._held(self.writing), here))
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
        except Exception:  # a look the system refuses, or git cannot answer: nobody can say
            at, standing = None, []
        if at is None:
            return messages.v4_either(old, new, interrupted=not failure), True
        if at == new:
            if failure and self.stranded:
                return self.stranded, True
            # a rewrite may have begun: --moved would rewrite the moved document's own links once more
            if self.rewrote:
                return messages.v4_at_new(old, new, None), True
            folders = [from_here(self.root, rel) for rel in self._standing_rel(standing)]
            here = (from_here(self.root, old), from_here(self.root, new), folders)
            return messages.v4_at_new(old, new, here), True
        if standing:
            shown = [
                (folder.relative_to(self.root).as_posix(), self.unmade.get(folder, "")) for folder in standing
            ]
            return messages.v4_folders_stand(old, shown), False
        if failure and self.moved_back == old:
            return messages.v4_moved_back(old), False
        return "", False

    def _standing_rel(self, standing: list[Path]) -> list[str]:
        assert self.root is not None
        return [folder.relative_to(self.root).as_posix() for folder in standing]

    def _held(self, rel: str) -> bool | None:
        """Whether git's index holds the document being written, so that git restore can bring its text back:
        None where it cannot say."""
        if self.root is None:
            return None
        try:
            return _indexed(self.root, rel)
        except Exception:
            return None


def from_here(root: Path, rel: str) -> str:
    """A path from the repository's top as the user types it where they stand: from the working folder."""
    return os.path.relpath(os.path.realpath(root / rel), os.path.realpath(Path.cwd()))


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


_GONE = (errno.ENOENT, errno.ENOTDIR, errno.ELOOP, errno.ENAMETOOLONG)  # no file can stand there


def _on_disk(path: Path) -> bool:
    """Whether the disk holds the path by its exact name: a folder's listing, so that a disk that ignores
    case cannot answer for a name in another case. Where the listing is refused, as in a folder that can be
    searched and not listed, the name itself is asked (`os.lstat`), which needs only the search right: no
    such file is "not there" on any disk, since no name in any case answers. A name that answers there
    cannot be told by its case, and nobody can say."""
    try:
        return path.name in os.listdir(path.parent)
    except OSError as exc:
        # its folder is gone, a link on the way loops, or no file can stand at a name too long
        if exc.errno in _GONE:
            return False
        if exc.errno not in (errno.EACCES, errno.EPERM):
            raise  # any other answer: nobody can say, and the line says so
    try:
        os.lstat(path)
    except OSError as exc:
        if exc.errno in _GONE:
            return False
        raise
    raise PermissionError(
        errno.EACCES, "the folder cannot be listed, so the name's case cannot be told", str(path)
    )


def _stands(folder: Path) -> bool:
    """A folder the move would make stands, by its exact name, asked of the system the same way on every
    Python (`stat_or_none`): what is absent by its rule is no folder, and any other error the line reads as
    nobody can say."""
    if not _on_disk(folder):
        return False
    found = stat_or_none(folder)
    return found is not None and stat.S_ISDIR(found.st_mode)
