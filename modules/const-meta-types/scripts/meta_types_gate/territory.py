"""Territory patterns in the gitignore dialect, evaluated by git itself.

`git check-ignore` runs against a fresh null repository with an empty work tree whose
only ignore rules are one policy's patterns: paths need not exist yet, and the consumer's
own .gitignore never interferes. `-v` reports one deciding pattern per path, so each
policy is one run; a deciding pattern that starts with '!' means "not in the territory".
"""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType

from . import messages
from .errors import ConfigurationFailure
from .model import NAMESPACE
from .repository import git


class Matcher:
    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix=NAMESPACE + "-"))
        self.git_dir = self.tmp / "null" / ".git"
        self.tree = self.tmp / "tree"
        template = self.tmp / "template"
        self.tree.mkdir()
        template.mkdir()
        if git(["init", "-q", f"--template={template}", str(self.tmp / "null")], cwd=self.tmp).returncode != 0:
            raise ConfigurationFailure(messages.c12_init())
        self.runs = 0

    def __enter__(self) -> Matcher:
        return self

    def __exit__(self, kind: type[BaseException] | None, value: BaseException | None,
                 trace: TracebackType | None) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def match(self, patterns: Sequence[str], paths: Sequence[str]) -> dict[str, str]:
        """{path: deciding pattern} for the paths inside the territory; others are absent."""
        if not patterns or not paths:
            return {}
        self.runs += 1
        excludes = self.tmp / f"territory-{self.runs}"
        excludes.write_text("\n".join(patterns) + "\n", encoding="utf-8")
        result = git([f"--git-dir={self.git_dir}", f"--work-tree={self.tree}",
                      "-c", f"core.excludesfile={excludes}", "-c", "core.ignorecase=false",
                      "check-ignore", "--no-index", "-v", "-n", "-z", "--stdin"],
                     cwd=self.tree, stdin=("\0".join(paths) + "\0").encode("utf-8"))
        if result.returncode not in (0, 1):
            raise ConfigurationFailure(messages.c12_check_ignore(result.stderr.decode("utf-8", "replace").strip()))
        fields = result.stdout.decode("utf-8", "replace").split("\0")
        found: dict[str, str] = {}
        for i in range(0, len(fields) - 3, 4):
            source, _line, pattern, path = fields[i:i + 4]
            if source and not pattern.startswith("!"):
                found[path] = pattern
        return found
