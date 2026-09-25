"""The two modes of the shell gate. The hook judges the command of a Bash event; the scan
explains what the dial does to a command given on the command line."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from const_gate import cli, pipeline
from const_gate.errors import ConfigurationFailure
from const_gate.model import PRE_WRITE, SHELL, Finding
from const_gate.output import Output
from const_gate.pipeline import Skip

from . import checks, messages, tokens
from . import dials as own_dials
from .model import COMMAND_FLAG, InteractionDials


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_event(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)  # validated at each read, in every mode
    if target.event_name != PRE_WRITE or target.tool_name != SHELL or target.command is None:
        raise ConfigurationFailure(messages.c12_event(target.event_name, target.tool_name))
    subcommands = tokens.split(target.command)
    if not dials.destructive:
        return pipeline.green_event(output, messages.g1_nothing_gated())
    findings = _findings(dials, target.command)
    if not findings:
        return pipeline.green_event(
            output, messages.g1_command_passed(len(dials.destructive), len(subcommands))
        )
    return pipeline.report_hook(
        output,
        findings,
        (),
        "",
        target.dials.severity,
        event_name=PRE_WRITE,
        count=messages.f9_count_command(len(findings), len(subcommands)),
        ask=True,
    )


def scan_mode(output: Output, start: Path) -> int:
    return scan_with(output, start, {COMMAND_FLAG: None})


def scan_with(output: Output, start: Path, values: cli.Values) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    command = values.get(COMMAND_FLAG)
    if command is None:
        return pipeline.skip(output, messages.g1_skip_no_command())
    subcommands = tokens.split(command)
    tail = messages.f9_command_tail(len(dials.destructive), len(subcommands))
    return pipeline.report_scan(output, _findings(dials, command), (), tail)


def _findings(dials: InteractionDials, command: str) -> list[Finding]:
    return [
        messages.d1_destructive(hit.entry, hit.subcommand, hit.matched)
        for hit in checks.match(dials.destructive, tokens.split(command))
    ]
