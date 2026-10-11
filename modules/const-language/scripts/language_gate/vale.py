"""The binary: found on PATH, its version checked against the floor, run over prepared copies of
the documents with the generated configuration alone, its JSON read into hits. Vale's own exit 1
on an error-level alert is silenced with --no-exit, so an exit code from it means it could not
run — a configuration failure with its first line."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from const_gate.errors import ConfigurationFailure

from . import messages
from .model import STYLE, VALE_FLOOR, VALE_RULE_NAME, Hit, Rule, Version

# In a hook these are caps: each wait takes the smaller of its cap and what is left of the hook's one
# deadline, which together they fit (`identity.hook_seconds`; the gate's tie holds it).
HOOK_SECONDS = 10  # the run's cap in a check after a write, the scan has none
VERSION_SECONDS = 5  # the probe's cap, in every mode
CHUNK = 200  # files per run, so an argument list stays far under any platform's limit
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")
RULE_OF = {f"{STYLE}.{name}": rule for rule, name in VALE_RULE_NAME.items()}


@dataclass(frozen=True, slots=True)
class Waits:
    """The seconds each of Vale's waits may take, asked when the wait begins, since what a hook has left of
    its deadline shrinks with the wait before it: the version probe's, and each run's, None for no limit.
    The caller chooses, there is no default: a hook asks the deadline, the scan asks for no limit."""

    probe: Callable[[], float]
    run: Callable[[], float | None]


def preflight(seconds: float = VERSION_SECONDS) -> Path:
    """The binary's path, once it exists and is new enough; a configuration failure otherwise. `seconds` is
    how long the version probe may take, the cap unless a hook has less of its deadline left."""
    found = shutil.which("vale")
    if found is None:
        raise ConfigurationFailure(messages.c2_vale_missing())
    try:
        done = subprocess.run(
            [found, "--version"], capture_output=True, text=True, timeout=seconds, check=False
        )
    except subprocess.TimeoutExpired as late:
        raise ConfigurationFailure(messages.c12_vale_version(f"no answer in {seconds:g} s")) from late
    except OSError as exc:
        raise ConfigurationFailure(messages.c12_vale_version(str(exc))) from exc
    match = VERSION.search(done.stdout)
    detail = (done.stderr or done.stdout).strip().splitlines()
    first = detail[0] if detail else "no output"
    if done.returncode != 0:
        raise ConfigurationFailure(messages.c12_vale_version_exit(done.returncode, first))
    if match is None:
        raise ConfigurationFailure(messages.c12_vale_version(first))
    version = Version(*(int(n) for n in match.groups()))
    if not version.at_least(VALE_FLOOR):
        raise ConfigurationFailure(messages.c2_vale_too_old(str(version)))
    return Path(found)


def run(
    binary: Path, config: Path, tree: Path, rels: Sequence[str], seconds: Callable[[], float | None]
) -> dict[str, list[Hit]]:
    """Vale over the named files under `tree`, in chunks; {rel: hits} for the files with any. `seconds`
    is asked before each run for its budget, None for no limit: the caller chooses, there is no default."""
    hits: dict[str, list[Hit]] = {}
    for start in range(0, len(rels), CHUNK):
        chunk = rels[start : start + CHUNK]
        budget = seconds()
        try:
            done = subprocess.run(
                [str(binary), f"--config={config}", "--no-global", "--output=JSON", "--no-exit", *chunk],
                cwd=tree,
                capture_output=True,
                text=True,
                timeout=budget,
                check=False,
            )
        except subprocess.TimeoutExpired as late:
            raise ConfigurationFailure(messages.c12_vale_too_slow(late.timeout)) from late
        if done.returncode != 0:
            raise ConfigurationFailure(messages.c12_vale_failed(_failure(done)))
        try:
            loaded: object = json.loads(done.stdout or "{}")
        except ValueError as exc:
            raise ConfigurationFailure(messages.c12_vale_failed(f"its output is not JSON: {exc}")) from exc
        if not isinstance(loaded, dict):
            raise ConfigurationFailure(messages.c12_vale_failed("its output is not a JSON object"))
        for rel, alerts in loaded.items():
            if isinstance(alerts, list):
                hits[str(rel)] = [hit for hit in (_hit(a) for a in alerts) if hit is not None]
    return hits


def _hit(alert: object) -> Hit | None:
    if not isinstance(alert, dict):
        return None
    rule = RULE_OF.get(str(alert.get("Check", "")))
    if rule is None:
        return None
    line = alert.get("Line")
    span = alert.get("Span")
    column = span[0] if isinstance(span, list) and span and isinstance(span[0], int) else 1
    return Hit(
        rule=rule,
        line=line if isinstance(line, int) and line > 0 else 1,
        column=column,
        match=str(alert.get("Match", "")),
        message=str(alert.get("Message", "")),
    )


def _failure(done: subprocess.CompletedProcess[str]) -> str:
    """Vale's own words for a run that failed: the Text of its JSON error, or the first line."""
    try:
        loaded: object = json.loads(done.stdout)
    except ValueError:
        loaded = None
    if isinstance(loaded, dict) and isinstance(loaded.get("Text"), str):
        text = str(loaded["Text"]).strip().splitlines()
        return text[0] if text else f"exit {done.returncode}"
    lines = (done.stderr or done.stdout).strip().splitlines()
    return lines[0] if lines else f"exit {done.returncode}"


def first_rule_of(rule: Rule) -> str:
    return f"{STYLE}.{VALE_RULE_NAME[rule]}"
