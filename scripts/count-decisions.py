#!/usr/bin/env python3
"""Kit report, never a gate: count the kit's decision records by the `status` of their envelopes.

Advisory in the sense of law 5 of CLAUDE.md: it judges nothing and blocks nothing; no count is a threshold.
It reads every docs/decisions/dec-*.md, takes the YAML envelope between the first two `---` lines, and
counts its `status`. A record with no envelope, an envelope that does not load, or a `status` outside the
kernel's two values, `active` and `inactive`, is counted apart and named, for a person to look at.

Modes:  no arguments   one line per status, its count and, for `active` and the odd ones, the records;
        --json         the same as one JSON object: {"total": n, "counts": {...}, "records": {...}}.
Exit:   0 always, save 1, with a BROKEN line and its fix, when PyYAML is missing, the arguments are misused,
        or the records' folder or a record cannot be read.
Its name is count-, never check-: the kit's check-gate-lists holds every scripts/check-*.py to the gate
group, and this script is no check.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
RECORDS = "docs/decisions"
OK, BROKEN = 0, 1
STATUSES = ("active", "inactive")  # the kernel's lifecycle values, printed first and always
NO_ENVELOPE = "(no envelope)"
NO_STATUS = "(no status)"


class Parser(argparse.ArgumentParser):
    """argparse with misuse a BROKEN exit 1, never its default 2."""

    def error(self, message: str) -> NoReturn:
        print(f"BROKEN: {message} — fix: python3 scripts/count-decisions.py [--json]")
        sys.exit(BROKEN)


class Broken(Exception):
    """A record cannot be read: the message is its BROKEN line."""


def status_of(text: str) -> str:
    """The envelope's `status` as text, or NO_ENVELOPE / NO_STATUS when there is none to read."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return NO_ENVELOPE
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return NO_ENVELOPE
    try:
        envelope = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return NO_ENVELOPE
    if not isinstance(envelope, dict) or envelope.get("status") is None:
        return NO_STATUS
    return str(envelope["status"])


def tally(folder: Path) -> dict[str, list[str]]:
    """Each status mapped to the file names that carry it, the kernel's values present even when empty."""
    found: dict[str, list[str]] = {status: [] for status in STATUSES}
    for path in sorted(folder.glob("dec-*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as bad:
            raise Broken(f"{path.relative_to(KIT)} cannot be read ({bad}) — fix: restore the file") from None
        found.setdefault(status_of(text), []).append(path.name)
    return found


def report(found: dict[str, list[str]], as_json: bool) -> str:
    """The text to print: one line per status, or one JSON object."""
    total = sum(len(names) for names in found.values())
    if as_json:
        counts = {status: len(names) for status, names in found.items()}
        return json.dumps({"total": total, "counts": counts, "records": found}, indent=2)
    lines = []
    for status, names in found.items():
        line = f"{status}: {len(names)}"
        if names and status != "inactive":
            line += " — " + ", ".join(names)
        lines.append(line)
    lines.append(f"total: {total}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = Parser(description="Count the kit's decision records by status.")
    parser.add_argument("--json", action="store_true", help="print one JSON object")
    args = parser.parse_args(argv)
    folder = KIT / RECORDS
    if not folder.is_dir():
        print(f"BROKEN: {RECORDS} is missing — fix: run the script from a clone of the kit")
        return BROKEN
    try:
        found = tally(folder)
    except Broken as bad:
        print(f"BROKEN: {bad}")
        return BROKEN
    print(report(found, args.json))
    return OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
