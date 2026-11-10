"""What the module asks of git: the common directory, git's version and the two hooks of the commit log in
git's configuration. Every call goes through the shared `git` function, so that a hook gives each its clock.
The range and the notes are the report's too."""

from __future__ import annotations

import os
import re
from collections.abc import Sequence
from pathlib import Path

from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.repository import git

from . import messages
from .model import GIT_MINIMUM, HOOK_COMMIT, HOOK_MERGE, NOTES_REF

# the hook keys with the git event each runs on, in the order the messages name them
HOOKS: tuple[tuple[str, str], ...] = ((HOOK_COMMIT, "post-commit"), (HOOK_MERGE, "post-merge"))
_VERSION = re.compile(r"git version (\d+)\.(\d+)")


def common_or_none(directory: Path) -> Path | None:
    """Git's common directory, the same from the main checkout and from every linked worktree; None outside
    a git repository."""
    if not directory.is_dir():
        return None
    done = git(["rev-parse", "--git-common-dir"], directory)
    if done.returncode != 0:
        return None
    return Path(os.path.realpath(directory / done.stdout.decode("utf-8", "replace").strip()))


def common_directory(directory: Path) -> Path:
    """The common directory, or the configuration failure J6.7 outside a git repository."""
    found = common_or_none(directory)
    if found is None:
        raise ConfigurationFailure(messages.j6_7_no_repository(str(directory)))
    return found


def version_of(directory: Path) -> tuple[int, int] | None:
    """git's major and minor, None where its answer is not of the form `git version 2.56.0`."""
    done = git(["--version"], directory)
    found = _VERSION.match(done.stdout.decode("utf-8", "replace"))
    return (int(found[1]), int(found[2])) if found else None


def version_text(directory: Path) -> str:
    """git's version as it names itself, such as 2.53.1; its whole answer where that has no such form."""
    done = git(["--version"], directory)
    text = done.stdout.decode("utf-8", "replace").strip()
    found = re.match(r"git version (\S+)", text)
    return found[1] if found else text or "no answer"


def is_old(directory: Path) -> bool:
    found = version_of(directory)
    return found is None or found < GIT_MINIMUM


def stands(directory: Path, key: str, event: str) -> bool:
    """Whether the hook `key` stands in git's configuration: a command, and the event it runs on."""
    done = git(["config", "--get-regexp", f"^{re.escape(key)}\\.(command|event)$"], directory)
    if done.returncode != 0:
        return False
    command = False
    on_event = False
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        name, _, value = line.partition(" ")
        if name.lower() == f"{key}.command".lower() and value.strip():
            command = True
        if name.lower() == f"{key}.event".lower() and value.strip() == event:
            on_event = True
    return command and on_event


def missing_hooks(directory: Path) -> list[str]:
    """The keys of the commit log's hooks that git's configuration lacks, in the order of `HOOKS`."""
    return [key for key, event in HOOKS if not stands(directory, key, event)]


def config_file(common: Path) -> Path:
    return common / "config"


def set_config(directory: Path, common: Path, key: str, values: Sequence[str]) -> None:
    """Writes `key` into the clone's own configuration file, replacing what it held; J6.15 if git cannot."""
    for position, value in enumerate(values):
        args = ["config", "--file", str(config_file(common))]
        args += ["--replace-all" if position == 0 else "--add", key, value]
        done = git(args, directory)
        if done.returncode != 0:
            detail = done.stderr.decode("utf-8", "replace").strip().splitlines()
            raise ConfigurationFailure(
                messages.j6_15_no_write(key, str(config_file(common)), detail[0] if detail else "no message")
            )


def remove_section(directory: Path, common: Path, section: str) -> None:
    """Removes the section `hook.<name>` from the clone's own configuration file; a section that is not
    there is as good as removed."""
    done = git(["config", "--file", str(config_file(common)), "--remove-section", section], directory)
    detail = done.stderr.decode("utf-8", "replace").strip().splitlines()
    if done.returncode != 0 and not (detail and "no such section" in detail[0]):
        raise ConfigurationFailure(
            messages.j6_15_no_write(section, str(config_file(common)), detail[0] if detail else "no message")
        )


def range_commits(directory: Path, root: Path, range_text: str) -> list[str]:
    """The SHAs of the commits of `range_text`, oldest first, parents before children; J6.12 where git cannot
    read the range. The range follows `--end-of-options`, so that no range is taken for an option."""
    done = git(["rev-list", "--reverse", "--topo-order", "--end-of-options", range_text, "--"], directory)
    if done.returncode != 0:
        raise ConfigurationFailure(messages.j6_12_bad_range(range_text, str(root), first_line(done.stderr)))
    return done.stdout.decode("utf-8", "replace").split()


def first_line(stderr: bytes) -> str:
    lines = stderr.decode("utf-8", "replace").strip().splitlines()
    return lines[0] if lines else "no message"


def write_note(directory: Path, sha: str, text: str) -> None:
    """Writes `text` as the note on `sha` under the module's notes ref, replacing an earlier one; J6.14 where
    git cannot. It writes the local ref alone: nothing is pushed."""
    done = git(["notes", "--ref", NOTES_REF, "add", "--force", "--message", text, sha], directory)
    if done.returncode != 0:
        raise ConfigurationFailure(messages.j6_14_no_note(sha, first_line(done.stderr)))
