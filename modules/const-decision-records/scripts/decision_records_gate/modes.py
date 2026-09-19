"""The two modes. Each wires parsing to checking to reporting and returns an exit code;
the checks themselves live in ``checks``."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from . import messages
from .checks import examine
from .dials import load_dials
from .errors import ConfigurationFailure
from .events import document_after_write, read_event
from .index import Index, build_index
from .model import EXIT_GREEN, EXIT_RED, Dials, Finding, PendingDocument, Severity
from .output import LOG_NAME, Output
from .repository import is_ignored, repo_root
from .territory import Matcher


def hook_mode(output: Output, stdin: TextIO) -> int:
    event = read_event(stdin)
    output.session = event.session_id
    if event.tool is None:
        return _skip(output, messages.g1_skip_no_file(event.tool_name))
    path = Path(os.path.expanduser(event.file_path))
    if not path.is_absolute():
        path = Path(event.cwd or os.getcwd()) / path
    path = Path(os.path.realpath(path))
    if path.suffix.lower() != ".md":
        return _skip(output, messages.g1_skip_not_markdown(str(path)))
    root = repo_root(path)
    if root is None:
        return _skip(output, messages.g1_skip_no_repo(str(path)))
    rel = path.relative_to(root).as_posix()
    dials = load_dials(root)
    if dials is None:
        return _skip(output, messages.g1_skip_no_dials(str(root)))
    _route_log(output, root, dials)
    if dials.root_policy is None:
        return _skip(output, messages.g1_skip_no_root())
    if not dials.record_policies:
        return _skip(output, messages.g1_skip_no_record_policies())
    text = document_after_write(event, root, rel)
    if text is None:
        return _skip(output, messages.g1_skip_edit_unappliable(rel))
    with Matcher() as matcher:
        index = build_index(root, dials, dials.root_policy, matcher, PendingDocument(rel, text))
        examination = examine(index, dials.record_policies, rel, text)
    notes = _notes(index, dials)
    if examination.outside:
        for note in notes:
            output.out(note)
        return _skip(output, messages.g1_skip_not_a_record(rel, dials.record_policies))
    if examination.findings:
        return _report(output, list(examination.findings), notes, rel, dials.severity)
    for note in notes:
        output.out(note)
    output.out(messages.g1_green_hook(examination.policy or ""))
    return EXIT_GREEN


def scan_mode(output: Output, start: Path) -> int:
    if not start.exists():
        raise ConfigurationFailure(messages.c12_scan_path(str(start)))
    root = repo_root(start.resolve())
    if root is None:
        raise ConfigurationFailure(messages.c12_no_repo(str(start)))
    dials = load_dials(root)
    if dials is None:
        return _skip(output, messages.g1_skip_no_dials(str(root)))
    _route_log(output, root, dials)
    if dials.root_policy is None:
        return _skip(output, messages.g1_skip_no_root())
    if not dials.record_policies:
        return _skip(output, messages.g1_skip_no_record_policies())
    findings: list[Finding] = []
    examined = 0
    with Matcher() as matcher:
        index = build_index(root, dials, dials.root_policy, matcher)
        for rel in index.paths:
            text = index.text(rel)
            if text is None:
                raise ConfigurationFailure(messages.c12_unreadable(rel))
            examination = examine(index, dials.record_policies, rel, text)
            if examination.outside:
                continue
            examined += 1
            findings.extend(examination.findings)
    for note in _notes(index, dials):
        output.out(note)
    known = sum(1 for policy in dials.record_policies if policy in index.policies)
    tail = messages.f9_scan_tail(examined, len(index.paths), known)
    if findings:  # the scan ignores the severity dial and always reports
        for finding in findings:
            output.out(finding.render())
        output.out(messages.f9_count_scan(len(findings), tail))
        return EXIT_RED
    output.out(messages.g1_green_scan(tail))
    return EXIT_GREEN


def _notes(index: Index, dials: Dials) -> list[str]:
    """The index's notes, then one per record policy the dial names that is no policy."""
    dangling = [policy for policy in dials.record_policies if policy not in index.policies]
    return [*index.notes, *(messages.n2_note_dangling_record_policy(policy) for policy in dangling)]


def _skip(output: Output, reason: str) -> int:
    output.out(messages.g1_green_skip(reason))
    return EXIT_GREEN


def _route_log(output: Output, root: Path, dials: Dials) -> None:
    """Send the log to the dial's directory, once git confirms the directory is ignored."""
    if dials.log_dir is None:
        return
    if not is_ignored(root, f"{dials.log_dir}/{LOG_NAME}"):
        raise ConfigurationFailure(messages.c13_log_dir_not_ignored(dials.log_dir))
    output.use_log_dir(root / dials.log_dir)


def _report(
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
