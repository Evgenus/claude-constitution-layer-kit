"""The reader judge of the effect report: a fresh reader, a language model, given one rule and an excerpt of a
session, answers whether the rule was applied, bypassed or missed there (R5 of dec-0114-module-effect-report-
design).

It runs `claude -p` with no tools, in an empty folder, on the person's own login, and never billed by usage:
before the first question it asks `claude auth status`, and it refuses unless the login is a subscription's.
The variables Claude Code prefers over a login, each billing by usage, are removed from the reader's
environment, so the login it checked is the one the reader uses. Its verdict is the first word of the answer;
an answer that opens with no outcome is no verdict, and the report counts it as such.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile

from . import messages
from .errors import ConfigurationFailure

SUBSCRIPTION = (
    "oauth_token",
    "claude.ai",
)  # the `authMethod` values of `claude auth status` that bill a plan
USAGE_BILLED = (  # the variables Claude Code prefers over a subscription login, each billing by usage
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
)
ASK_SECONDS = 60.0  # `claude --version` and `claude auth status`
VERDICT_SECONDS = 300.0  # one question to the reader
PROMPT = """You judge one rule of a software project at one moment of a working session.

The rule:
{rule}

The moment, an excerpt of the session's transcript, one event per line:
{excerpt}

Answer on the first line with one word: APPLIED if the rule was followed at this moment, BYPASSED if the
work went around the rule, or MISSED if the rule was not followed. Give one line of reason after it."""


def _environment() -> dict[str, str]:
    return {name: value for name, value in os.environ.items() if name not in USAGE_BILLED}


def _ask(argv: list[str], seconds: float) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=seconds, env=_environment())
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConfigurationFailure(messages.e5_no_claude(f"{type(exc).__name__}: {exc}")) from exc


def ready() -> tuple[str, str]:
    """The Claude Code version the reader runs on, once the login is a subscription's, and no model yet."""
    version = _ask(["claude", "--version"], ASK_SECONDS)
    if version.returncode != 0 or not version.stdout.strip():
        raise ConfigurationFailure(messages.e5_no_claude(f"claude --version exited {version.returncode}"))
    status = _ask(["claude", "auth", "status"], ASK_SECONDS)
    try:
        loaded: object = json.loads(status.stdout)
    except ValueError:
        loaded = {}
    method = loaded.get("authMethod") if isinstance(loaded, dict) else None
    if method not in SUBSCRIPTION:
        raise ConfigurationFailure(messages.e5_not_subscription(str(method or "no login")))
    return version.stdout.split()[0], ""


def verdict(rule: str, excerpt: str, model: str) -> tuple[str | None, str]:
    """The reader's outcome, `applied`, `bypassed` or `missed`, or None; and the model that answered."""
    prompt = PROMPT.format(rule=rule, excerpt=excerpt)
    with tempfile.TemporaryDirectory() as empty:
        argv = ["claude", "-p", prompt, "--output-format", "json", "--tools", ""]
        try:
            done = subprocess.run(
                argv, capture_output=True, text=True, timeout=VERDICT_SECONDS, env=_environment(), cwd=empty
            )
        except (OSError, subprocess.TimeoutExpired):
            return None, model
    try:
        answer: object = json.loads(done.stdout)
    except ValueError:
        return None, model
    if not isinstance(answer, dict):
        return None, model
    used = answer.get("modelUsage")
    if isinstance(used, dict) and used:
        model = ", ".join(sorted(str(name) for name in used))
    text = answer.get("result")
    words = text.split() if isinstance(text, str) else []
    first = words[0].strip(".:*").lower() if words else ""
    return (first if first in ("applied", "bypassed", "missed") else None), model
