"""The two modes. Each wires parsing to checking to reporting and returns an exit code;
the checks themselves live in ``checks``."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TextIO

from . import messages
from .checks import check_root_policy, examine
from .dials import load_dials
from .errors import ConfigurationFailure
from .events import document_after_write, read_event
from .index import build_index
from .model import (EXIT_GREEN, EXIT_RED, Dials, Finding, PendingDocument, Severity)
from .output import LOG_NAME, Output
from .repository import is_ignored, repo_root
from .territory import Matcher

FILE_TOOLS = ("Write", "Edit")


def hook_mode(output: Output, stdin: TextIO) -> int:
    event = read_event(stdin)
    output.session = event.session_id
    if event.tool_name not in FILE_TOOLS or not event.file_path:
        return _skip(output, messages.skip_no_file(event.tool_name))
    path = Path(os.path.expanduser(event.file_path))
    if not path.is_absolute():
        path = Path(event.cwd or os.getcwd()) / path
    path = Path(os.path.realpath(path))
    if path.suffix.lower() != ".md":
        return _skip(output, messages.skip_not_markdown(str(path)))
    root = repo_root(path)
    if root is None:
        return _skip(output, messages.skip_no_repo(str(path)))
    if not path.is_relative_to(root):
        return _skip(output, messages.skip_outside_repo(str(path)))
    rel = path.relative_to(root).as_posix()
    dials = load_dials(root)
    if dials is None:
        return _skip(output, messages.skip_no_dials(str(root)))
    _route_log(output, root, dials)
    if dials.root_policy is None:
        return _skip(output, messages.skip_no_root())
    text = document_after_write(event, root, rel)
    if text is None:
        reason = messages.skip_no_content() if event.tool_name == "Write" else messages.skip_edit_unappliable(rel)
        return _skip(output, reason)
    if rel == dials.root_policy:
        root_findings = check_root_policy(dials, rel, text)
        if root_findings:
            return _report(output, root_findings, rel, dials.severity)
    with Matcher() as matcher:
        index = build_index(root, dials, dials.root_policy, matcher, PendingDocument(rel, text))
        examination = examine(index, rel, text)
    if examination.outside:
        void = index.void_namespaces_claiming(rel)
        reason = messages.skip_void_territory(rel, void) if void else messages.skip_outside_territory(rel)
        return _skip(output, reason)
    for note in index.notes:
        output.out(note)
    if not examination.findings:
        output.out(messages.green_hook(examination.policy or ""))
        return EXIT_GREEN
    return _report(output, list(examination.findings), rel, dials.severity)


def scan_mode(output: Output, start: Path) -> int:
    root = repo_root(start.resolve())
    if root is None:
        raise ConfigurationFailure(messages.c12_no_repo(str(start)))
    dials = load_dials(root)
    if dials is None:
        return _skip(output, messages.skip_no_dials(str(root)))
    _route_log(output, root, dials)
    if dials.root_policy is None:
        return _skip(output, messages.skip_no_root())
    findings: list[Finding] = []
    examined = 0
    with Matcher() as matcher:
        index = build_index(root, dials, dials.root_policy, matcher)
        for rel in index.paths:
            text = index.text(rel)
            if text is None:
                raise ConfigurationFailure(messages.c12_unreadable(rel))
            examination = examine(index, rel, text)
            if examination.outside:
                continue
            examined += 1
            findings.extend(examination.findings)
    for note in index.notes + [messages.note_void_namespace(name) for name in sorted(index.void)]:
        output.out(note)
    tail = messages.scan_tail(examined, len(index.paths), len(index.policies))
    if findings:                         # the scan ignores the severity dial and always reports
        for finding in findings:
            output.out(finding.render())
        output.out(messages.count_scan(len(findings), tail))
        return EXIT_RED
    output.out(messages.green_scan(tail))
    return EXIT_GREEN


def _skip(output: Output, reason: str) -> int:
    output.out(messages.green_skip(reason))
    return EXIT_GREEN


def _route_log(output: Output, root: Path, dials: Dials) -> None:
    """Send the log to the dial's directory, once git confirms the directory is ignored."""
    if dials.log_dir is None:
        return
    if not is_ignored(root, f"{dials.log_dir}/{LOG_NAME}"):
        raise ConfigurationFailure(messages.c13_log_dir_not_ignored(dials.log_dir))
    output.use_log_dir(root / dials.log_dir)


def _report(output: Output, findings: list[Finding], rel: str, severity: Severity) -> int:
    """Hook verdict on findings: block (exit 2, stderr reaches the model) or warn (exit 0
    with JSON: additionalContext reaches the model, systemMessage the user)."""
    body = "\n".join([f.render() for f in findings] + [messages.count_hook(len(findings), rel)])
    if severity is Severity.WARN:
        output.out(json.dumps({
            "hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "additionalContext": body + "\n" + messages.warn_note()},
            "systemMessage": messages.warn_system(findings[0].headline),
        }))
        return EXIT_GREEN
    output.err(body)
    return EXIT_RED
