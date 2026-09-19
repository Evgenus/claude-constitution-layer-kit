"""The parts of a run every gate shares: from the hook event, or the scan's directory, to the
repository and its dials; and from findings to the verdict the platform understands. What
lies between — which documents the module examines, and how — is the module's own code,
which calls these and is called by nothing here."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from . import messages
from .dials import load_dials
from .errors import ConfigurationFailure
from .events import document_after_write, read_event
from .model import EXIT_GREEN, EXIT_RED, Dials, Finding, Severity
from .output import Output, log_name
from .repository import is_ignored, repo_root


@dataclass(frozen=True, slots=True)
class Skip:
    """Nothing to examine, and the reason the count line gives."""

    reason: str


@dataclass(frozen=True, slots=True)
class WriteTarget:
    """A Markdown document about to be written into a repository whose dials name a root policy."""

    root: Path
    rel: str
    text: str  # the document as it will be after the write
    dials: Dials
    root_policy: str


@dataclass(frozen=True, slots=True)
class ScanTarget:
    root: Path
    dials: Dials
    root_policy: str


def locate_write(output: Output, stdin: TextIO) -> WriteTarget | Skip:
    event = read_event(stdin)
    output.session = event.session_id
    if event.tool is None:
        return Skip(messages.g1_skip_no_file(event.tool_name))
    path = Path(os.path.expanduser(event.file_path))
    if not path.is_absolute():
        path = Path(event.cwd or os.getcwd()) / path
    path = Path(os.path.realpath(path))
    if path.suffix.lower() != ".md":
        return Skip(messages.g1_skip_not_markdown(str(path)))
    root = repo_root(path)
    if root is None:
        return Skip(messages.g1_skip_no_repo(str(path)))
    rel = path.relative_to(root).as_posix()
    dials = load_dials(root)
    if dials is None:
        return Skip(messages.g1_skip_no_dials(str(root)))
    _route_log(output, root, dials)
    if dials.root_policy is None:
        return Skip(messages.g1_skip_no_root())
    text = document_after_write(event, root, rel)
    if text is None:
        return Skip(messages.g1_skip_edit_unappliable(rel))
    return WriteTarget(root, rel, text, dials, dials.root_policy)


def locate_scan(output: Output, start: Path) -> ScanTarget | Skip:
    if not start.exists():
        raise ConfigurationFailure(messages.c12_scan_path(str(start)))
    root = repo_root(start.resolve())
    if root is None:
        raise ConfigurationFailure(messages.c12_no_repo(str(start)))
    dials = load_dials(root)
    if dials is None:
        return Skip(messages.g1_skip_no_dials(str(root)))
    _route_log(output, root, dials)
    if dials.root_policy is None:
        return Skip(messages.g1_skip_no_root())
    return ScanTarget(root, dials, dials.root_policy)


def skip(output: Output, reason: str, notes: Sequence[str] = ()) -> int:
    for note in notes:
        output.out(note)
    output.out(messages.g1_green_skip(reason))
    return EXIT_GREEN


def green_hook(output: Output, policy: str, notes: Sequence[str] = ()) -> int:
    for note in notes:
        output.out(note)
    output.out(messages.g1_green_hook(policy))
    return EXIT_GREEN


def report_hook(
    output: Output, findings: Sequence[Finding], notes: Sequence[str], rel: str, severity: Severity
) -> int:
    """Hook verdict on findings. Block: exit 2, stderr reaches the model. Warn: exit 0 with
    nothing on stdout but one JSON object — additionalContext reaches the model,
    systemMessage the user — so the notes travel inside it, never before it."""
    body = "\n".join([*notes, *(f.render() for f in findings), messages.f9_count_hook(len(findings), rel)])
    if severity is Severity.WARN:
        output.out(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "additionalContext": body + "\n" + messages.w1_warn_note(),
                    },
                    "systemMessage": messages.w1_warn_system(findings[0].headline),
                }
            )
        )
        return EXIT_GREEN
    output.err(body)
    return EXIT_RED


def report_scan(output: Output, findings: Sequence[Finding], notes: Sequence[str], tail: str) -> int:
    """Scan verdict. The scan ignores the severity dial and always reports."""
    for note in notes:
        output.out(note)
    if findings:
        for finding in findings:
            output.out(finding.render())
        output.out(messages.f9_count_scan(len(findings), tail))
        return EXIT_RED
    output.out(messages.g1_green_scan(tail))
    return EXIT_GREEN


def _route_log(output: Output, root: Path, dials: Dials) -> None:
    """Send the log to the dial's directory, once git confirms the directory is ignored."""
    if dials.log_dir is None:
        return
    if not is_ignored(root, f"{dials.log_dir}/{log_name()}"):
        raise ConfigurationFailure(messages.c13_log_dir_not_ignored(dials.log_dir))
    output.use_log_dir(root / dials.log_dir)
