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
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            input=stdin,
            capture_output=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
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
        detail = result.stderr.decode("utf-8", "replace").strip()
        if "not a git repository" in detail:
            return None
        raise ConfigurationFailure(
            messages.c12_git_failed(detail.splitlines()[0] if detail else "no message")
        )
    return Path(os.path.realpath(result.stdout.decode("utf-8", "replace").strip()))


def first_line(stderr: bytes) -> str:
    lines = stderr.decode("utf-8", "replace").strip().splitlines()
    return lines[0] if lines else "no message"


def list_markdown(root: Path) -> list[str]:
    """Tracked and untracked non-ignored Markdown files, repository-relative. A tracked file
    deleted from the working tree is still listed by git until the deletion is staged; it is
    not a document any more, so it is left out."""
    result = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if result.returncode != 0:
        raise ConfigurationFailure(messages.c12_ls_files(str(root), first_line(result.stderr)))
    paths = os.fsdecode(result.stdout).split("\0")  # bytes git cannot decode survive as they are
    return sorted({p for p in paths if p and p.lower().endswith(".md") and (root / p).is_file()})


def is_ignored(root: Path, rel: str) -> bool:
    """Whether the consumer's own ignore rules cover `rel` (used for the log directory)."""
    return git(["check-ignore", "-q", "--", rel], cwd=root).returncode == 0


def read_text(root: Path, rel: str) -> str | None:
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
