"""Documents named outside Markdown: in a script, a configuration file, a comment. No link
checker follows such a name, so where a project declares how its ids look there, every match
must be the id of a covered document. Scan only: these files pass no Markdown hook."""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit import messages as shared
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import Finding
from constitution_layer_kit.repository import first_line, git, is_markdown
from constitution_layer_kit.territory import Matcher

from . import messages
from .model import Ids, Mention

_SNIFF = 8000  # bytes read to tell a binary file, as git does: one holding a NUL is none of ours


def other_files(root: Path) -> list[str]:
    """The files git lists that are no Markdown, no link and not binary, repository-relative."""
    result = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if result.returncode != 0:
        raise ConfigurationFailure(shared.c12_ls_files(str(root), first_line(result.stderr)))
    paths = sorted({p for p in os.fsdecode(result.stdout).split("\0") if p and not is_markdown(p)})
    return [
        p
        for p in paths
        # a link first, never followed: os.path.islink answers on every interpreter, and is not read
        if not os.path.islink(root / p) and _listed_file(root, p) and not _binary(root / p)
    ]


# The errors that say a path is no file, as Path.is_file reads them on every Python: gone, a folder on the
# way that is a file, a link that leads nowhere or round in a loop.
_ABSENT = frozenset({errno.ENOENT, errno.ENOTDIR, errno.EBADF, errno.ELOOP})


def _listed_file(root: Path, rel: str) -> bool:
    """Whether a path git lists is a file, through any link; one the gate cannot reach — a folder above it
    nobody may search — is the shared C12.10 on every Python. `Path.is_file` raises there before 3.14 and
    returns False from 3.14 on; `os.stat` raises on every version. The module's own copy of the shared
    `listed_file`, so that it needs no later release of the package than it requires."""
    try:
        mode = os.stat(root / rel).st_mode
    except OSError as exc:
        if exc.errno in _ABSENT:
            return False
        raise ConfigurationFailure(shared.c12_unreadable(rel)) from exc
    return stat.S_ISREG(mode)


def examine(
    root: Path, files: Sequence[str], mentions: Sequence[Mention], ids: Ids, matcher: Matcher
) -> tuple[list[Finding], int]:
    """The findings, and how many files were read for them."""
    found: list[Finding] = []
    read_at_all: set[str] = set()
    for mention in mentions:
        read = sorted(matcher.match(mention.files, files)) if mention.files else list(files)
        read_at_all.update(read)
        for rel in read:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
            # a line ends at "\n" alone, as `line_of` counts: a form feed or U+2028 stays inside its line
            for number, line in enumerate(text.split("\n"), start=1):
                found += [
                    messages.r8_unknown_mention(rel, number, m[0])
                    for m in mention.pattern.finditer(line)
                    if m[0] and not ids.owners_of(m[0])
                ]
    return found, len(read_at_all)


def _binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\0" in handle.read(_SNIFF)
    except OSError:
        return True
