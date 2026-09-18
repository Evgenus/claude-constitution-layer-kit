#!/usr/bin/env python3
"""Kit check: the const-meta-types gate's hand-written validation is never more lenient
than the kernel's JSON Schemas, and for the envelope it is exactly equal.

The module ships without the kit, so it cannot read kernel/schemas/ at run time; it carries
a mirror of the rules instead. This check runs the real schemas (through the jsonschema
library, a development dependency of the kit only) and the mirror over one corpus and
compares verdicts. Run from anywhere: python3 scripts/check-schema-mirror.py

Exit: 0 green; 2 the mirror and a schema disagree; 1 the check could not run.
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "modules" / "const-meta-types" / "scripts"))   # kit-side test code only

try:
    import jsonschema
    import yaml
except ImportError as exc:
    print(f"BROKEN: {exc.name} is not installed — fix: python3 -m pip install jsonschema pyyaml")
    print("BROKEN: the check could not run — 0 cases examined")
    sys.exit(1)

from meta_types_gate.dials import load_dials  # noqa: E402
from meta_types_gate.envelope import envelope_errors, parse_envelope  # noqa: E402
from meta_types_gate.errors import ConfigurationFailure  # noqa: E402

GOOD = {"id": "note-a", "type": "non-authoritative", "title": "Note A", "status": "active"}


@dataclass(frozen=True)
class EnvelopeCase:
    name: str
    fields: dict[str, object]


def envelope_corpus() -> list[EnvelopeCase]:
    cases = [EnvelopeCase("valid", dict(GOOD)), EnvelopeCase("extra field allowed", {**GOOD, "stakes": "process"})]
    for key in GOOD:
        cases.append(EnvelopeCase(f"{key} missing", {k: v for k, v in GOOD.items() if k != key}))
        cases.append(EnvelopeCase(f"{key} not a string", {**GOOD, key: True}))
    cases += [EnvelopeCase("id not kebab", {**GOOD, "id": "Note_A"}), EnvelopeCase("id trailing dash", {**GOOD, "id": "a-"}),
              EnvelopeCase("type outside enum", {**GOOD, "type": "spec"}),
              EnvelopeCase("status outside enum", {**GOOD, "status": "open"}),
              EnvelopeCase("title empty", {**GOOD, "title": ""}), EnvelopeCase("title of spaces", {**GOOD, "title": "   "}),
              EnvelopeCase("title of two lines", {**GOOD, "title": "a\nb"}), EnvelopeCase("title 200", {**GOOD, "title": "x" * 200}),
              EnvelopeCase("title 201", {**GOOD, "title": "x" * 201})]
    for meta_type in ("current-state", "task-record"):
        cases.append(EnvelopeCase(f"type {meta_type}", {**GOOD, "type": meta_type}))
    return cases


DIALS_CORPUS: list[tuple[str, object]] = [
    ("empty file", {}), ("root only", {"root_policy": "docs/policies/root.md"}),
    ("root empty string", {"root_policy": ""}), ("root not a string", {"root_policy": 3}),
    ("dialect empty", {"territory_dialect": ""}), ("dialect not a string", {"territory_dialect": 1}),
    ("namespace not a mapping", {"notes-policy": "docs/**"}),
    ("territory not a list", {"notes-policy": {"territory": "docs/**"}}),
    ("territory with empty item", {"notes-policy": {"territory": [""]}}),
    ("territory with non-string item", {"notes-policy": {"territory": [1]}}),
    ("valid policy namespace", {"notes-policy": {"territory": ["docs/notes/**"], "anything": 1}}),
]


def schema_accepts(schema: dict[str, object], instance: object) -> bool:
    return not list(jsonschema.Draft202012Validator(schema).iter_errors(instance))


def mirror_accepts_dials(instance: object) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "constitution.yaml").write_text(yaml.safe_dump(instance), encoding="utf-8")
        try:
            load_dials(Path(tmp))
        except ConfigurationFailure:
            return False
        return True


def main() -> int:
    schemas = KIT / "kernel" / "schemas"
    envelope_schema = json.loads((schemas / "document-frontmatter.schema.json").read_text(encoding="utf-8"))
    dials_schema = json.loads((schemas / "constitution.schema.json").read_text(encoding="utf-8"))
    disagreements: list[str] = []
    corpus = envelope_corpus()
    for case in corpus:
        text = "---\n" + yaml.safe_dump(case.fields, sort_keys=False) + "---\n"
        mirror = not envelope_errors(parse_envelope(text))
        schema = schema_accepts(envelope_schema, case.fields)
        if mirror != schema:
            disagreements.append(f"envelope '{case.name}': schema accepts={schema}, mirror accepts={mirror}")
    for name, instance in DIALS_CORPUS:
        mirror, schema = mirror_accepts_dials(instance), schema_accepts(dials_schema, instance)
        if mirror and not schema:          # the mirror may be stricter (repository-relative paths), never looser
            disagreements.append(f"dials '{name}': the schema rejects it but the mirror accepts it")
    counts = f"{len(corpus)} envelope cases (equality), {len(DIALS_CORPUS)} dials cases (never more lenient) examined"
    if disagreements:
        for line in disagreements:
            print(f"RED: {line}\n  why: the module's mirror is the only copy of the kernel schema a consumer has\n"
                  "  fix: align modules/const-meta-types/scripts/meta_types_gate/envelope.py or dials.py with kernel/schemas/")
        print(f"RED: {len(disagreements)} disagreement(s) — {counts}")
        return 2
    print(f"GREEN: the const-meta-types mirror agrees with the kernel schemas — {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
