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
from .model import EXIT_GREEN, EXIT_RED, POST_WRITE, PRE_WRITE, STOP, Dials, Finding, Severity, SkipKind
from .output import Output, log_name
from .repository import is_ignored, is_markdown, read_text, repo_root


@dataclass(frozen=True, slots=True)
class Skip:
    """Nothing to examine, and the reason the count line gives. `kind` and `where` are the same
    facts typed, for a module that says the skip in its own words: never parse `reason`."""

    reason: str
    kind: SkipKind
    where: str  # the path, root, file or tool the reason names, whole


@dataclass(frozen=True, slots=True)
class WriteTarget:
    """A Markdown document about to be written into a repository that has a dials file. Whether
    the dials name a root policy is the module's question: a gate that resolves policies skips
    without one, a gate that reads only its own dials does not care."""

    root: Path
    rel: str
    text: str  # the document as it will be after the write — or as it is, for an event after it
    dials: Dials
    event_name: str = PRE_WRITE


@dataclass(frozen=True, slots=True)
class ScanTarget:
    root: Path
    dials: Dials


@dataclass(frozen=True, slots=True)
class EventTarget:
    """An event that names no file — a Stop — in a repository that has a dials file: the
    repository is the one the event's cwd lies in, and what the module examines there is its own."""

    root: Path
    dials: Dials
    event_name: str
    stop_hook_active: bool | None
    tool_name: str = ""  # the tool of a tool event without a file — the shell — or empty for a Stop
    command: str | None = None  # the shell tool's command; None for every other event


def locate_write(output: Output, stdin: TextIO) -> WriteTarget | Skip:
    event = read_event(stdin)
    output.session = event.session_id
    if event.tool is None:
        return Skip(messages.g1_skip_no_file(event.tool_name), SkipKind.NO_FILE, event.tool_name)
    path = Path(os.path.expanduser(event.file_path))
    if not path.is_absolute():
        path = Path(event.cwd or os.getcwd()) / path
    path = Path(os.path.realpath(path))
    if not is_markdown(path.name):
        return Skip(messages.g1_skip_not_markdown(str(path)), SkipKind.NOT_MARKDOWN, str(path))
    root = repo_root(path)
    if root is None:
        return Skip(messages.g1_skip_no_repo(str(path)), SkipKind.NO_REPO, str(path))
    rel = path.relative_to(root).as_posix()
    dials = load_dials(root)
    if dials is None:
        return Skip(messages.g1_skip_no_dials(str(root)), SkipKind.NO_DIALS, str(root))
    route_log(output, root, dials)
    if event.event_name == POST_WRITE:  # the document is the file on disk: nothing to reconstruct
        text = read_text(root, rel)
        if text is None:
            return Skip(messages.g1_skip_gone(rel), SkipKind.GONE, rel)
    else:
        text = document_after_write(event, root, rel)
        if text is None:
            return Skip(messages.g1_skip_edit_unappliable(rel), SkipKind.EDIT_UNAPPLIABLE, rel)
    return WriteTarget(root, rel, text, dials, event.event_name or PRE_WRITE)


def locate_event(output: Output, stdin: TextIO) -> EventTarget | Skip:
    """For a gate wired to an event without a file. The event is read by the one reader, so a
    tool event's fields are still validated; a cwd outside any repository is a visible skip."""
    event = read_event(stdin)
    output.session = event.session_id
    cwd = Path(os.path.realpath(event.cwd or os.getcwd()))
    root = repo_root(cwd)
    if root is None:
        return Skip(messages.g1_skip_no_repo(str(cwd)), SkipKind.NO_REPO, str(cwd))
    dials = load_dials(root)
    if dials is None:
        return Skip(messages.g1_skip_no_dials(str(root)), SkipKind.NO_DIALS, str(root))
    route_log(output, root, dials)
    return EventTarget(root, dials, event.event_name, event.stop_hook_active, event.tool_name, event.command)


def locate_scan(output: Output, start: Path) -> ScanTarget | Skip:
    if not start.exists():
        raise ConfigurationFailure(messages.c12_scan_path(str(start)))
    root = repo_root(start.resolve())
    if root is None:
        raise ConfigurationFailure(messages.c12_no_repo(str(start)))
    dials = load_dials(root)
    if dials is None:
        return Skip(messages.g1_skip_no_dials(str(root)), SkipKind.NO_DIALS, str(root))
    route_log(output, root, dials)
    return ScanTarget(root, dials)


def skip(output: Output, reason: str, notes: Sequence[str] = (), event_name: str | None = None) -> int:
    """`event_name`: the write event a hook run answers, so that its notes reach the model as
    `green_hook`'s do; None for a scan, whose stdout is its reader's."""
    line = messages.g1_green_skip(reason)
    if event_name is None:
        for note in notes:
            output.out(note)
        output.out(line)
        return EXIT_GREEN
    return _green_write(output, notes, line, event_name)


def no_root_policy(output: Output) -> int:
    """The skip of a gate that resolves policies, in a repository whose dials name no root."""
    return skip(output, messages.g1_skip_no_root())


def green_hook(output: Output, what: str, notes: Sequence[str] = (), event_name: str = PRE_WRITE) -> int:
    """`what` says what the examined document is: `messages.governed_by(policy)`, or the module's
    own words where no policy is involved. `event_name`: the write event the run answers, which a
    run with notes must repeat."""
    return _green_write(output, notes, messages.g1_green_hook(what), event_name)


def _green_write(output: Output, notes: Sequence[str], line: str, event_name: str) -> int:
    """The green of a hook run on a write event. Without notes: the line alone, plain. With notes:
    exit 0 with one JSON object on stdout and nothing else, the notes and the line in
    additionalContext — the platform writes a write event's plain stdout to its debug log, where
    the model never reads it, and passes additionalContext on."""
    if not notes:
        output.out(line)
        return EXIT_GREEN
    context = "\n".join([*notes, line])
    output.out(
        json.dumps({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": context}})
    )
    return EXIT_GREEN


def green_event(output: Output, line: str, notes: Sequence[str] = ()) -> int:
    """The green of a hook wired to an event that names no document: `line` is the module's whole
    account of what it examined."""
    for note in notes:
        output.out(note)
    output.out(messages.g1_green_event(line))
    return EXIT_GREEN


SHOWN_CHARACTERS = 8000  # above 10,000 characters the platform replaces a hook's text with a file path
# and a preview of the first 2,000 (hooks documentation, read 2026-10-03; limit 14 of the shared limits):
# the findings after the first keep the text under the cap, the count line and the closing note standing last


def within_the_cap(findings: Sequence[Finding], most: int | None = None) -> Sequence[Finding]:
    """The first findings that fit: at most `most` of them when it is given, and no more characters
    than SHOWN_CHARACTERS. The first is always shown, however long, so that a verdict with a finding
    never shows none."""
    shown: list[Finding] = []
    size = 0
    for finding in findings[:most]:
        size += len(finding.render()) + 1
        if size > SHOWN_CHARACTERS and shown:
            break
        shown.append(finding)
    return shown


def report_hook(
    output: Output,
    findings: Sequence[Finding],
    notes: Sequence[str],
    rel: str,
    severity: Severity,
    event_name: str = PRE_WRITE,
    count: str | None = None,
    ask: bool = False,
) -> int:
    """Hook verdict on findings. Block: exit 2, stderr reaches the model. Warn: exit 0 with
    nothing on stdout but one JSON object — additionalContext reaches the model,
    systemMessage the user — so the notes travel inside it, never before it. On Stop the warn
    is the systemMessage alone, carrying the whole body: context handed to the model at a
    turn's end continues the turn, up to the platform's cap, and that is a block, not a warning.
    `ask`: a gate whose block is the user's yes — the shell gate — answers, at block severity,
    with exit 0 and one JSON object asking the platform to prompt the user, the body its reason:
    where a prompt cannot be shown the platform denies the call with that reason, and the exit
    code is 0 because the verdict is the platform's prompt, not this process's; warn is unchanged."""
    count = messages.f9_count_hook(len(findings), rel) if count is None else count
    body = "\n".join([*notes, *(f.render() for f in findings), count])
    if ask and severity is Severity.BLOCK:
        output.out(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": event_name,
                        "permissionDecision": "ask",
                        "permissionDecisionReason": body,
                    }
                }
            )
        )
        return EXIT_GREEN
    if severity is Severity.WARN and event_name == STOP:
        output.out(json.dumps({"systemMessage": messages.w1_warn_stop(body)}))
        return EXIT_GREEN
    if severity is Severity.WARN:
        output.out(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": event_name,
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


def route_log(output: Output, root: Path, dials: Dials) -> None:
    """Send the log to the dial's directory, once git confirms the directory is ignored. Public
    for a second entry point, which locates nothing through this module and routes its own log
    as soon as it has read the dials."""
    if dials.log_dir is None:
        return
    if not is_ignored(root, f"{dials.log_dir}/{log_name()}"):
        raise ConfigurationFailure(messages.c13_log_dir_not_ignored(dials.log_dir))
    output.use_log_dir(root / dials.log_dir)
