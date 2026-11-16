"""The repository as this gate sees it: git for the root and the file list, plain reads
for the text."""

from __future__ import annotations

import errno
import os
import shlex
import stat
import subprocess
import tempfile
from pathlib import Path

from . import identity, messages
from .errors import ConfigurationFailure
from .model import Mode

# The most seconds one git call may take in a hook; a scan and an act give git as long as it takes. A cap:
# the call takes the smaller of it and what is left of the hook's one deadline (`identity.remaining`).
GIT_SECONDS: float = 3
_TAKES_A_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"})


def budget(before: str = "a git call") -> float | None:
    """The clock of one git call: in a run declared a hook the smaller of `GIT_SECONDS` and what is left of
    the hook's deadline, and a configuration failure, C12.14, where nothing is left (`before` names the call
    it ended); none in a scan, in an act, or where no mode was declared."""
    return identity.remaining(GIT_SECONDS, before) if identity.declared_mode() is Mode.HOOK else None


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
    """One git call. In a hook it has the smaller of `GIT_SECONDS` and what is left of the hook's deadline to
    answer. Past `GIT_SECONDS` it is a configuration failure naming the hang, C12.12 or C12.13; cut short
    by the deadline, which the earlier waits of the run had spent, it is C12.14, the hook's budget, and a
    call asked after the deadline is that failure before git is started. In a scan or an act it has no
    clock.
    `scratch`: the call runs in a null repository the caller made in the system's temporary directory,
    which a person cannot run it in by hand; the failure then names that directory and the git
    configuration outside any repository, not `cwd` and the call."""
    asked = f"git {subcommand(args)} answered"
    timeout = budget(asked)
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            input=stdin,
            capture_output=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ConfigurationFailure(messages.c3_git_missing()) from exc
    except subprocess.TimeoutExpired as exc:
        if exc.timeout is not None and exc.timeout < GIT_SECONDS:  # the deadline cut it, not the call's cap
            raise ConfigurationFailure(
                messages.c12_hook_budget(identity.current().hook_seconds, asked)
            ) from exc
        if scratch:
            failure = messages.c12_git_silent_scratch(GIT_SECONDS, subcommand(args), tempfile.gettempdir())
        else:
            failure = messages.c12_git_silent(GIT_SECONDS, subcommand(args), str(cwd), by_hand(args, stdin))
        raise ConfigurationFailure(failure) from exc


def stand_in(folder: Path, shown: str) -> bool:
    """Whether `folder` is a folder a process can stand in: one that stands and may be searched. A path that
    is absent, or no folder, is not. A folder that stands and may not be searched, or one behind such a
    folder, is the shared C12.16 naming `shown`, on every Python. `folder/.` is asked, whose lookup needs the
    search right, so the system itself says which."""
    try:
        os.stat(os.path.join(folder, "."))
    except OSError as exc:
        if exc.errno in _ABSENT:
            return False
        raise ConfigurationFailure(
            messages.c12_unreachable(shown, exc.strerror or type(exc).__name__)
        ) from exc
    return True


def working_folder() -> Path:
    """The process's working folder, asked of the system in this one place. Where the system will not say
    where the process stands, as macOS does when a folder above it may not be searched, the shared C12.16
    names the working folder: there is no path to name, since that path is what the system withheld."""
    try:
        return Path(os.getcwd())
    except OSError as exc:
        raise ConfigurationFailure(
            messages.c12_unreachable("the working folder", exc.strerror or type(exc).__name__)
        ) from exc


def ask_git_entry(folder: Path) -> None:
    """Asks the system of `.git` in `folder` and in each folder above it, until one is found, before git's
    own discovery may go on upward past one it cannot read. A `.git` folder must let its `HEAD` be asked; a
    gitfile, as a worktree's or a submodule's `.git` is, must be readable. Either refused is the shared
    C12.16 naming that `.git`, on every Python: never the verdict of a repository above it. The walk stops
    where git's would: at the first `.git`, or below a folder of GIT_CEILING_DIRECTORIES, and not at all
    where GIT_DIR names the repository."""
    if os.environ.get("GIT_DIR"):
        return
    ceilings = {
        os.path.realpath(part)
        for part in os.environ.get("GIT_CEILING_DIRECTORIES", "").split(os.pathsep)
        if part
    }
    while True:
        entry = folder / ".git"
        found = reached(entry, str(entry))
        if found is not None:
            try:
                if stat.S_ISDIR(found.st_mode):
                    os.stat(entry / "HEAD")
                else:
                    with open(entry, "rb") as handle:
                        handle.read(1)
            except OSError as exc:
                if exc.errno not in _ABSENT:  # a .git with no HEAD is git's to judge
                    raise ConfigurationFailure(
                        messages.c12_unreachable(str(entry), exc.strerror or type(exc).__name__)
                    ) from exc
            return
        if folder.parent == folder or os.path.realpath(folder.parent) in ceilings:
            return
        folder = folder.parent


def repo_root(path: Path) -> Path | None:
    """The real path of the repository containing `path` (which need not exist), or None. The walk goes up
    only past what is absent or no folder. A folder it cannot search, the path itself or one on the way
    up, is the shared C12.16 naming the path asked about, on every Python: the walk never passes it to stand
    in a repository above, whose verdict is not this tree's. Nor does git's own discovery: the `.git` of
    the folder found, and of each above it up to the first, is asked first (`ask_git_entry`)."""
    probe = path
    while not stand_in(probe, str(probe)):
        if probe.parent == probe:
            return None
        probe = probe.parent
    ask_git_entry(probe)  # a .git nobody can read is said here: git's discovery would go on upward past it
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
    return sorted({p for p in paths if p and is_markdown(p) and listed_file(root, p)})


# The errors that say a path is absent, as Path.is_file reads them on every Python: gone, a folder on the
# way that is a file, a link that leads nowhere or round in a loop.
_ABSENT = frozenset({errno.ENOENT, errno.ENOTDIR, errno.EBADF, errno.ELOOP})


def stat_or_none(path: Path) -> os.stat_result | None:
    """What the system says of a path, through any link: None where it is absent — gone, behind a file, a
    link that leads nowhere or loops. Any other error is raised, on every Python: `Path.is_file`,
    `exists` and `is_dir` raise there before 3.14 and return False from 3.14 on, which would read a path
    nobody can reach as absent and pass it over without a word. So the answer is asked of `os.stat`,
    which raises on every version."""
    try:
        return os.stat(path)
    except OSError as exc:
        if exc.errno in _ABSENT:
            return None
        raise


def reached(path: Path, shown: str) -> os.stat_result | None:
    """What the system says of `path` (`stat_or_none`): None where it is absent. Any other error is the
    shared C12.16, naming the path as `shown`, on every Python: a path behind a folder nobody may search is
    never read as absent."""
    try:
        return stat_or_none(path)
    except OSError as exc:
        raise ConfigurationFailure(
            messages.c12_unreachable(shown, exc.strerror or type(exc).__name__)
        ) from exc


def listed_file(root: Path, rel: str) -> bool:
    """Whether a path git lists is a file, through any link (`stat_or_none`). A path the gate cannot reach
    — a folder above it nobody may search, a name too long for the system — is a configuration failure,
    C12.10."""
    try:
        found = stat_or_none(root / rel)
    except OSError as exc:
        raise ConfigurationFailure(messages.c12_unreadable(rel, exc.strerror or type(exc).__name__)) from exc
    return found is not None and stat.S_ISREG(found.st_mode)


def is_ignored(root: Path, rel: str) -> bool:
    """Whether the consumer's own ignore rules cover `rel` (used for the log directory)."""
    return git(["check-ignore", "-q", "--", rel], cwd=root).returncode == 0


def read_text(root: Path, rel: str) -> str | None:
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
