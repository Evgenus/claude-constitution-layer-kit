"""The repository as this gate sees it: git for the root and the file list, plain reads
for the text."""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from pathlib import Path

from . import identity, messages
from .errors import ConfigurationFailure
from .model import Mode

# The seconds one git call may take in a hook; a scan and an act give git as long as it takes.
GIT_SECONDS: float = 3
_TAKES_A_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"})


def budget() -> float | None:
    """The clock of one git call: `GIT_SECONDS` where the run was declared a hook, none in a scan, in an
    act, or where no mode was declared."""
    return GIT_SECONDS if identity.declared_mode() is Mode.HOOK else None


def subcommand(args: list[str]) -> str:
    """Git's own subcommand: the first argument that is no option and no option's value (`-C <v>`,
    `-c <v>`, `--git-dir <v>`, `--work-tree <v>`, … — the forms with `=` are one argument)."""
    skip = False
    for argument in args:
        if skip:
            skip = False
        elif argument in _TAKES_A_VALUE:
            skip = True
        elif not argument.startswith("-"):
            return argument
    return " ".join(args)  # no subcommand: say what was asked


def by_hand(args: list[str], stdin: bytes | None = None) -> str:
    """The call as a person can run it to see it hang or answer: the arguments as the gate passed them,
    each quoted for a shell, the NUL-output flag `-z` dropped (it only changes how paths are written),
    and `< /dev/null` where the gate fed the call a standard input, so that it never waits on a
    terminal."""
    shown = " ".join(shlex.quote(a) for a in args if a != "-z")
    return shown + (" < /dev/null" if stdin is not None else "")


def git(
    args: list[str], cwd: Path, stdin: bytes | None = None, scratch: bool = False
) -> subprocess.CompletedProcess[bytes]:
    """One git call. In a hook it has `GIT_SECONDS` to answer; past them it is a configuration failure.
    `scratch`: the call runs in a null repository the caller made in the system's temporary directory,
    which a person cannot run it in by hand; the failure then names that directory and the git
    configuration outside any repository, not `cwd` and the call."""
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            input=stdin,
            capture_output=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
            timeout=budget(),
        )
    except FileNotFoundError as exc:
        raise ConfigurationFailure(messages.c3_git_missing()) from exc
    except subprocess.TimeoutExpired as exc:
        if scratch:
            failure = messages.c12_git_silent_scratch(GIT_SECONDS, subcommand(args), tempfile.gettempdir())
        else:
            failure = messages.c12_git_silent(GIT_SECONDS, subcommand(args), str(cwd), by_hand(args, stdin))
        raise ConfigurationFailure(failure) from exc


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


def is_markdown(rel: str) -> bool:
    """Markdown means `.md`: the name's ending, in any case — a file named just `.md` too — wherever
    the hook or the scan asks (limit 7 of the shared limits)."""
    return rel.lower().endswith(".md")


def list_markdown(root: Path) -> list[str]:
    """Tracked and untracked non-ignored Markdown files, repository-relative. A tracked file
    deleted from the working tree is still listed by git until the deletion is staged; it is
    not a document any more, so it is left out."""
    result = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if result.returncode != 0:
        raise ConfigurationFailure(messages.c12_ls_files(str(root), first_line(result.stderr)))
    paths = os.fsdecode(result.stdout).split("\0")  # bytes git cannot decode survive as they are
    return sorted({p for p in paths if p and is_markdown(p) and (root / p).is_file()})


def is_ignored(root: Path, rel: str) -> bool:
    """Whether the consumer's own ignore rules cover `rel` (used for the log directory)."""
    return git(["check-ignore", "-q", "--", rel], cwd=root).returncode == 0


def read_text(root: Path, rel: str) -> str | None:
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
