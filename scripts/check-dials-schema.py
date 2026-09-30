#!/usr/bin/env python3
"""Kit check: the kit's own constitution.yaml is valid against the kernel's dials schema,
kernel/schemas/constitution.schema.json, checked by a real validator — the jsonschema library,
a development dependency of the kit only, never of a module (decision dec-0018-dials-schema).

Every gate reads its own keys by hand at each read; this check reads the whole file against the
whole schema once, so a key no gate reads is held too. The schema itself is checked against its
draft first. The file is read with PyYAML's safe loader, anchors and aliases resolved.

Modes:  no arguments   check the kit's constitution.yaml;
        --self-test    prove the check on throwaway files: a valid file green; an empty
                       root_policy, a territory that is not a list and a namespace that is not a
                       mapping each a finding; the report of one finding as literal lines with
                       exit 2; a file that is not YAML, an absent file and a schema that breaks
                       its draft each a BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import jsonschema
    import yaml
except ImportError as missing:
    print(f"BROKEN: {missing.name} is not installed — fix: python3 -m pip install jsonschema pyyaml")
    print("BROKEN: the check could not run — 0 keys examined")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
DIALS = "constitution.yaml"
SCHEMA = "kernel/schemas/constitution.schema.json"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
ALIGN = "allows, or change the schema with the kernel text it encodes"
WHY = "the kit's dials file is the kernel's first consumer, and a key no gate reads is held by nothing else"


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    where: str
    what: str

    def render(self) -> str:
        return (
            f"RED: {DIALS}: {self.where}: {self.what}\n"
            f"  why: {WHY}\n"
            f"  fix: change {self.where} to what {SCHEMA} {ALIGN}"
        )


def load(dials: Path, schema: Path) -> tuple[Any, dict[str, Any]]:
    if not dials.is_file():
        raise Broken(f"no {DIALS} at {dials.parent} — fix: run the check from a clone of the kit")
    try:
        data = yaml.safe_load(dials.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as bad:
        raise Broken(f"{DIALS} is not YAML ({str(bad).splitlines()[0]}) — fix: repair the file") from bad
    try:
        rules = json.loads(schema.read_text(encoding="utf-8"))
    except (OSError, ValueError) as bad:
        raise Broken(f"{SCHEMA} cannot be read as JSON ({bad}) — fix: restore the schema") from bad
    if not isinstance(rules, dict):
        raise Broken(f"{SCHEMA} is not a JSON object — fix: restore the schema")
    try:
        jsonschema.validators.validator_for(rules).check_schema(rules)
    except jsonschema.SchemaError as bad:
        raise Broken(f"{SCHEMA} breaks its own draft ({bad.message}) — fix: repair the schema") from bad
    return data, rules


def check(dials: Path, schema: Path) -> tuple[list[Finding], int]:
    data, rules = load(dials, schema)
    validator = jsonschema.validators.validator_for(rules)(rules)
    findings = [
        Finding("/".join(str(p) for p in error.absolute_path) or "the file", error.message)
        for error in sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    ]
    keys = len(data) if isinstance(data, dict) else 0
    return findings, keys


def report(findings: list[Finding], keys: int) -> int:
    counts = f"{keys} top-level key(s) examined against {SCHEMA}"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: {DIALS} is valid against the kernel's dials schema — {counts}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on throwaway files against the kit's own schema: a valid file is green; an empty
    root_policy, a territory that is not a list and a namespace that is not a mapping are one finding
    each; the report of one finding is its literal text, exit 2; a file that is not YAML, an absent
    file and a schema that breaks its draft are each a teaching BROKEN line."""
    schema = KIT / SCHEMA
    valid = (
        "root_policy: docs/policies/root.md\nroot:\n  territory:\n    - docs/policies/**\nconst-x:\n  a: 1\n"
    )
    cases = {
        "a valid file is green": (valid, []),
        "an empty root_policy is a finding": (valid.replace("docs/policies/root.md", "''"), ["root_policy"]),
        "a territory that is not a list is a finding": (
            valid.replace("  territory:\n    - docs/policies/**\n", "  territory: docs/policies/**\n"),
            ["root/territory"],
        ),
        "a namespace that is not a mapping is a finding": (
            valid.replace("const-x:\n  a: 1\n", "const-x: 3\n"),
            ["const-x"],
        ),
    }
    failed = 0
    for name, (text, wanted) in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            dials = Path(tmp) / DIALS
            dials.write_text(text, encoding="utf-8")
            got = [f.where for f in check(dials, schema)[0]]
        ok = got == wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        got {got}")
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: constitution.yaml: root_policy: '' should be non-empty",
        f"  why: {WHY}",
        f"  fix: change root_policy to what {SCHEMA} {ALIGN}",
        f"RED: 1 finding(s) — 3 top-level key(s) examined against {SCHEMA}",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        dials = Path(tmp) / DIALS
        dials.write_text(valid.replace("docs/policies/root.md", "''"), encoding="utf-8")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check(dials, schema))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    broken_cases: list[tuple[str, str | None, bool, str]] = [
        ("a file that is not YAML", "a: [1, 2\n", False, "is not YAML"),
        ("an absent file", None, False, "no constitution.yaml"),
        ("a schema that breaks its draft", valid, True, "breaks its own draft"),
    ]
    for name, body, broken_schema, said in broken_cases:
        with tempfile.TemporaryDirectory() as tmp:
            dials, bad = Path(tmp) / DIALS, Path(tmp) / "schema.json"
            if body is not None:
                dials.write_text(body, encoding="utf-8")
            bad.write_text(json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": 3}))
            try:
                check(dials, bad if broken_schema else schema)
                ok = False
            except Broken as broken:
                ok = said in str(broken) and "fix:" in str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line")
    total = len(cases) + 4
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-dials-schema", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 keys examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check(KIT / DIALS, KIT / SCHEMA))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 keys examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
