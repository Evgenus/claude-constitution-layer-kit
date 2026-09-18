"""The repository as this gate sees it: git for the root and the file list, plain reads
for the text."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from . import messages
from .errors import ConfigurationFailure


def git(args: list[str], cwd: Path, stdin: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(["git", *args], cwd=cwd, input=stdin, capture_output=True, check=False)
    except FileNotFoundError as exc:
        raise ConfigurationFailure(messages.c3_git_missing()) from exc


def repo_root(path: Path) -> Path | None:
    """The real path of the repository containing `path` (which need not exist), or None."""
    probe = path if path.is_dir() else path.parent
    while not probe.is_dir():
        if probe.parent == probe:
            return None
        probe = probe.parent
    result = git(["rev-parse", "--show-toplevel"], cwd=probe)
    if result.returncode != 0:
        return None
    return Path(os.path.realpath(result.stdout.decode("utf-8", "replace").strip()))


def list_markdown(root: Path) -> list[str]:
    """Tracked and untracked non-ignored Markdown files, repository-relative."""
    result = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if result.returncode != 0:
        raise ConfigurationFailure(messages.c12_ls_files(str(root)))
    paths = result.stdout.decode("utf-8", "replace").split("\0")
    return sorted({p for p in paths if p and p.lower().endswith(".md")})


def is_ignored(root: Path, rel: str) -> bool:
    """Whether the consumer's own ignore rules cover `rel` (used for the log directory)."""
    return git(["check-ignore", "-q", "--", rel], cwd=root).returncode == 0


def read_text(root: Path, rel: str) -> str | None:
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
