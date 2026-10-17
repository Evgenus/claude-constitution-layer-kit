"""Kit tooling, never shipped in a module: the story of one eval case, as `scripts/run-evals.py --verbose`
prints it (decision dec-0093-module-evals-with-local-receipts).

  `case_preamble`  before a case runs, from its `case.yaml`: the prompt the model is given, and each grader
                   with the rule it holds: `regex` its target, match and pattern; `tool_used` its tool and
                   input match; `tool_order` its tools in order; `file_exists` its path; `llm` its rubric.
  `case_story`     after it ran, from the result JSON `claude plugin eval --json` wrote and the run traces the
                   runner copied: per run, its verdict, score, turns and time; what the session showed the
                   model before the prompt, each start hook's output; every tool call in order, a tool's
                   failure, and every text the model wrote, its last one its reply; then each grader's
                   verdict and the eval's own explanation. A run's trace is found through the map file the
                   container writes, one line per copied trace, `<n>` and the trace's path in the
                   container, the path the result JSON names for that run.

Long texts are cut to `LINES` lines, a tool's input to one line of `WIDTH` characters. Nothing here is a
check: a file that cannot be read, or a field the eval does not write, prints as a note and never stops a
run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

LINES = 40  # lines of one text before it is cut
WIDTH = 160  # characters of one tool input
INDENT = "    "


def cut(text: str, limit: int = LINES) -> list[str]:
    """The text's lines, at most `limit` of them, the last naming how many were cut."""
    lines = text.rstrip().splitlines() or [""]
    if len(lines) <= limit:
        return lines
    return [*lines[:limit], f"… ({len(lines) - limit} more lines)"]


def one_line(text: str, width: int = WIDTH) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def grader_rule(grader: dict[str, Any]) -> str:
    """One grader as the case states it: its name, its type and the rule it holds."""
    name, kind = grader.get("name", "?"), grader.get("type", "?")
    conf = grader.get("config", grader)
    if kind == "regex":
        target = conf.get("target", "last_message")
        if isinstance(target, dict):
            target = f"file {target.get('path', '?')}"
        match = conf.get("match", "contains")
        flags = f", flags {conf['flags']}" if conf.get("flags") else ""
        rule = f"regex on {target}, {match}{flags}: {conf.get('pattern', '?')}"
    elif kind == "tool_used":
        matching = f" whose input matches {conf['input_match']!r}" if conf.get("input_match") else ""
        rule = f"tool_used: {conf.get('tool', '?')}{matching}"
    elif kind == "tool_order":
        rule = f"tool_order: {' before '.join(str(t) for t in conf.get('tools', conf.get('order', [])))}"
    elif kind == "file_exists":
        rule = f"file_exists: {conf.get('path', conf.get('glob', '?'))}"
    elif kind == "llm":
        rule = f"llm judge: {one_line(str(conf.get('rubric', conf.get('prompt', '?'))))}"
    else:
        rule = f"{kind}: {one_line(json.dumps(conf, sort_keys=True))}"
    return f"{name} — {rule}"


def case_preamble(case_yaml: Path) -> list[str]:
    try:
        data = yaml.safe_load(case_yaml.read_text(encoding="utf-8"))
        prompt = str(data["execution"]["prompt"])
        graders = list(data.get("graders") or [])
    except (OSError, yaml.YAMLError, KeyError, TypeError) as bad:
        return [f"  (the case cannot be read: {bad!r})"]
    lines = ["  we tell the model:"]
    lines += [INDENT + line for line in cut(prompt)]
    lines.append("  we judge by:")
    lines += [f"{INDENT}{grader_rule(g)}" for g in graders if isinstance(g, dict)]
    return lines


def tool_call(name: str, given: dict[str, Any]) -> str:
    """A tool call on one line: the input that says what it does, else the input as JSON."""
    for key in ("skill", "command", "file_path", "path", "pattern", "url", "description"):
        if isinstance(given.get(key), str):
            return f"→ {name} {one_line(given[key])}"
    return f"→ {name} {one_line(json.dumps(given, sort_keys=True))}"


def trace_story(trace: Path) -> list[str]:
    """What the session showed the model before the prompt, then what the model did, in order."""
    try:
        events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, ValueError) as bad:
        return [f"{INDENT}(the trace cannot be read: {bad!r})"]
    lines: list[str] = []
    texts: list[list[str]] = []
    for event in events:
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "hook_response":
            output = str(event.get("output") or event.get("stdout") or "").strip()
            if output:
                lines.append(f"{INDENT}{event.get('hook_name', 'hook')} told the model:")
                lines += [INDENT + "  " + line for line in cut(output, 8)]
            continue
        message = event.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            if kind == "assistant" and part.get("type") == "text" and str(part.get("text", "")).strip():
                block = cut(str(part["text"]))
                texts.append(block)
                lines.append(f"{INDENT}model says:")
                lines += [INDENT + "  " + line for line in block]
            elif kind == "assistant" and part.get("type") == "tool_use":
                given = part.get("input")
                lines.append(
                    INDENT + tool_call(str(part.get("name", "?")), given if isinstance(given, dict) else {})
                )
            elif kind == "user" and part.get("type") == "tool_result" and part.get("is_error"):
                said = part.get("content")
                text = said if isinstance(said, str) else json.dumps(said)
                lines.append(f"{INDENT}  ✗ the tool failed: {one_line(text)}")
    if not texts:
        lines.append(f"{INDENT}(the model wrote no text)")
    return lines


def trace_map(map_file: Path) -> dict[str, Path]:
    """The container's trace path of each run, mapped to the copy the runner kept beside the map."""
    found: dict[str, Path] = {}
    try:
        rows = map_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return found
    for row in rows:
        number, _, path = row.partition(" ")
        if number.isdigit() and path:
            found[path] = map_file.with_name(map_file.name.replace("-traces.txt", f"-trace{number}.jsonl"))
    return found


def case_story(result: Path, map_file: Path) -> list[str]:
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
        case = data["cases"][0]
        runs = [run for arm in case.get("arms", {}).values() for run in arm]
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as bad:
        return [f"  (the result cannot be read: {bad!r})"]
    traces = trace_map(map_file)
    lines: list[str] = []
    for number, run in enumerate(runs, 1):
        verdict = "passed" if run.get("passed") else "FAILED"
        lines.append(
            f"  run {number}: {verdict}, score {float(run.get('score') or 0):.2f},"
            f" {run.get('turns', '?')} turn(s), {run.get('durationSeconds', '?')} s"
        )
        if run.get("error"):
            lines.append(f"{INDENT}✗ the run failed: {one_line(str(run['error']))}")
        trace = traces.get(str(run.get("tracePath", "")))
        lines += trace_story(trace) if trace else [f"{INDENT}(no trace kept for this run)"]
        for grader in run.get("graders") or []:
            mark = "✓" if grader.get("passed") else "✗"
            why = one_line(str(grader.get("explanation") or ""))
            lines.append(f"{INDENT}{mark} {grader.get('name', '?')}: {why}")
    return lines
