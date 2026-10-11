"""Documents named outside Markdown: in a script, a configuration file, a comment. No link
checker follows such a name, so where a project declares how its ids look there, every match
must be the id of a covered document. Scan only: these files pass no Markdown hook."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from const_gate import messages as shared
from const_gate.errors import ConfigurationFailure
from const_gate.model import Finding
from const_gate.repository import first_line, git, is_markdown
from const_gate.territory import Matcher

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
        p for p in paths if (root / p).is_file() and not (root / p).is_symlink() and not _binary(root / p)
    ]


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
