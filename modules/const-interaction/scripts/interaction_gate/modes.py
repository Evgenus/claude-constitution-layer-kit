"""The two modes of the shell gate. The hook judges the command of a Bash event; the scan
explains what the dial does to a command given on the command line."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from constitution_layer_kit import cli, pipeline
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import PRE_WRITE, SHELL, Finding
from constitution_layer_kit.output import Output
from constitution_layer_kit.pipeline import Skip

from . import checks, messages, tokens
from . import dials as own_dials
from .model import COMMAND_FLAG, InteractionDials, Subcommand


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_event(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)  # validated at each read, in every mode
    if target.event_name != PRE_WRITE or target.tool_name != SHELL or target.command is None:
        raise ConfigurationFailure(messages.c12_event(target.event_name, target.tool_name))
    subcommands = tokens.split(target.command, dials.reader)
    if not dials.destructive:
        return pipeline.green_event(output, messages.g1_nothing_gated())
    findings = _findings(dials, subcommands)
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
    subcommands = tokens.split(command, dials.reader)
    tail = messages.f9_command_tail(len(dials.destructive), len(subcommands))
    return pipeline.report_scan(output, _findings(dials, subcommands), (), tail)


def _findings(dials: InteractionDials, subcommands: list[Subcommand]) -> list[Finding]:
    return [
        messages.d1_destructive(hit.entry, hit.subcommand, hit.matched)
        for hit in checks.match(dials.destructive, subcommands)
    ]
