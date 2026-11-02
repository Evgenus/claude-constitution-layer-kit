"""The grant: the one command line this plugin answers `allow` for, and nothing else.

A skill that a rule lets the model load does not carry its own pre-approval to the command it names,
so the command is granted here, on the shell tool's event, before the platform's permission check.
The match is an allowlist: the command is exactly `sh <plugin root>/scripts/new-document.sh`, then
arguments each written plain or in single quotes, one space before each. Anything else — a second
command, a redirection, a substitution, a variable, a glob, a double quote, another path, two spaces —
is not matched, and the hook says nothing, so that the platform's own permission flow decides it. An
answer of `allow` skips the platform's split of a compound command, so a looser match would grant
what follows a separator; that is why nothing is matched that the allowlist does not name.
"""

from __future__ import annotations

import json
import re
from typing import TextIO

from constitution_layer_kit import preflight
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.events import read_event
from constitution_layer_kit.model import EXIT_GREEN, SHELL, Broken
from constitution_layer_kit.output import Output

from . import messages

PRE_TOOL_USE = "PreToolUse"
COMMAND = "scripts/new-document.sh"  # the command's path below the plugin root
# A plugin root the grant names in its pattern: an absolute path of characters no shell reads as syntax,
# so that the text before the arguments cannot hold a separator, a quote or an expansion.
ROOT = re.compile(r"/[A-Za-z0-9_./@+-]*")
# One argument: plain characters no shell reads as syntax — no `=`, which zsh expands at a word's start —
# or a single-quoted string, in which a POSIX shell expands nothing; neither a quote nor a line break in it.
ARGUMENT = r"(?:[A-Za-z0-9_./:,@+-]+|'[^'\n\r\x00]*')"
ARGUMENTS = re.compile(rf"(?: {ARGUMENT})*")


def granted(command: str, root: str) -> bool:
    """Whether `command` is exactly this plugin's create command, with plain or single-quoted
    arguments, for the plugin installed at `root`."""
    if ROOT.fullmatch(root) is None:
        return False
    head = f"sh {root.rstrip('/')}/{COMMAND}"
    if not command.startswith(head):
        return False
    return ARGUMENTS.fullmatch(command[len(head) :]) is not None


def answer() -> str:
    """The one JSON object that grants the call: the platform skips its prompt, and still applies
    the deny and ask rules the consumer wrote."""
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": PRE_TOOL_USE,
                "permissionDecision": "allow",
                "permissionDecisionReason": messages.g1_granted(),
            }
        }
    )


def grant(output: Output, stdin: TextIO, root: str) -> int:
    """Reads one event; answers `allow` for the plugin's own command and prints nothing for any
    other call. Exit 0 either way: the grant judges nothing, so it has no finding."""
    try:
        event = read_event(stdin)
    except ConfigurationFailure as failure:  # the shared fix names a scan, which the grant has not
        raise ConfigurationFailure(
            Broken(failure.broken.key, failure.broken.headline, messages.g4_input())
        ) from None
    output.session = event.session_id
    if event.event_name != PRE_TOOL_USE or event.tool_name != SHELL or event.command is None:
        return EXIT_GREEN
    if granted(event.command, root):
        preflight.check()  # before the answer, as before any verdict; a call that is no match needs none
        output.out(answer())
    return EXIT_GREEN
