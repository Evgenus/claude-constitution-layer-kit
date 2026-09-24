#!/usr/bin/env python3
"""Kit check: the gates' hand-written validation is never more lenient than the kernel's
JSON Schemas — const-meta-types for the envelope (exactly equal) and the dials file,
const-decision-records for what a decision record adds to the envelope (equal, except
where the mirror is stricter on purpose: a decider of blanks).

A module ships without the kit, so it cannot read kernel/schemas/ at run time; it carries
a mirror of the rules instead. This check runs the real schemas (through the jsonschema
library, a development dependency of the kit only) and the mirror over one corpus and
compares verdicts. Run from anywhere: python3 scripts/check-schema-mirror.py

An exemption is held too: a case listed as another reader's must still be one the mirror
accepts and the schema rejects, and a case listed as stricter on purpose one the schema
accepts and the mirror rejects — an exemption that stops holding is itself red, with the fix
that removes it or restores the rule it covered.

Exit: 0 green; 2 the mirror and a schema disagree, or an exemption no longer holds; 1 the
check could not run.
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
for module in ("const-meta-types", "const-decision-records"):  # kit-side test code only
    sys.path.insert(0, str(KIT / "modules" / module / "scripts"))

try:
    import jsonschema
    import referencing
    import yaml
except ImportError as exc:
    print(f"BROKEN: {exc.name} is not installed — fix: python3 -m pip install jsonschema referencing pyyaml")
    print("BROKEN: the check could not run — 0 cases examined")
    sys.exit(1)

from const_gate import identity  # noqa: E402
from const_gate.dials import load_dials  # noqa: E402
from const_gate.envelope import parse_envelope  # noqa: E402
from const_gate.errors import ConfigurationFailure  # noqa: E402
from decision_records_gate.checks import check_record  # noqa: E402
from meta_types_gate import start  # noqa: E402
from meta_types_gate.checks import envelope_errors  # noqa: E402

GOOD = {"id": "note-a", "type": "non-authoritative", "title": "Note A", "status": "active"}
THIS_FILE = "scripts/check-schema-mirror.py"
WHY_MIRROR = "the module's mirror is the only copy of the kernel schema a consumer has"
WHY_EXEMPTION = "an exemption that no longer holds would hide the next real disagreement on its case"
ALIGN = (
    "align with kernel/schemas/ — dials.py of shared/const_gate/, or checks.py of the module the line names"
)


@dataclass(frozen=True)
class Disagreement:
    what: str
    why: str
    fix: str


@dataclass(frozen=True)
class EnvelopeCase:
    name: str
    fields: dict[str, object]


def envelope_corpus() -> list[EnvelopeCase]:
    cases = [
        EnvelopeCase("valid", dict(GOOD)),
        EnvelopeCase("extra field allowed", {**GOOD, "stakes": "process"}),
    ]
    for key in GOOD:
        cases.append(EnvelopeCase(f"{key} missing", {k: v for k, v in GOOD.items() if k != key}))
        cases.append(EnvelopeCase(f"{key} not a string", {**GOOD, key: True}))
    cases += [
        EnvelopeCase("id not kebab", {**GOOD, "id": "Note_A"}),
        EnvelopeCase("id trailing dash", {**GOOD, "id": "a-"}),
        EnvelopeCase("type outside enum", {**GOOD, "type": "spec"}),
        EnvelopeCase("status outside enum", {**GOOD, "status": "open"}),
        EnvelopeCase("title empty", {**GOOD, "title": ""}),
        EnvelopeCase("title of spaces", {**GOOD, "title": "   "}),
        EnvelopeCase("title of two lines", {**GOOD, "title": "a\nb"}),
        EnvelopeCase("title 200", {**GOOD, "title": "x" * 200}),
        EnvelopeCase("title 201", {**GOOD, "title": "x" * 201}),
    ]
    for meta_type in ("current-state", "task-record"):
        cases.append(EnvelopeCase(f"type {meta_type}", {**GOOD, "type": meta_type}))
    return cases


RECORD = {**GOOD, "id": "record-a", "type": "task-record", "stakes": "process", "decider": "the maintainer"}
STRICTER_ON_PURPOSE = {"decider of blanks"}  # the schema's minLength 1 lets blanks through


def record_corpus() -> list[EnvelopeCase]:
    """The envelope's own four fields stay valid throughout: only what a record adds varies."""
    cases = [EnvelopeCase("valid record", dict(RECORD))]
    for stakes in ("product", "architecture", "routine", "high", ""):
        cases.append(EnvelopeCase(f"stakes '{stakes}'", {**RECORD, "stakes": stakes}))
    for key in ("stakes", "decider"):
        cases.append(EnvelopeCase(f"{key} missing", {k: v for k, v in RECORD.items() if k != key}))
        cases.append(EnvelopeCase(f"{key} not a string", {**RECORD, key: 7}))
        cases.append(EnvelopeCase(f"{key} a list", {**RECORD, key: ["a", "b"]}))
    cases += [
        EnvelopeCase("decider empty", {**RECORD, "decider": ""}),
        EnvelopeCase("decider of blanks", {**RECORD, "decider": "   "}),
        EnvelopeCase("type current-state", {**RECORD, "type": "current-state"}),
        EnvelopeCase("type non-authoritative", {**RECORD, "type": "non-authoritative"}),
        EnvelopeCase("extra field allowed", {**RECORD, "policy": "records-policy"}),
    ]
    return cases


DIALS_CORPUS: list[tuple[str, object]] = [
    ("empty file", {}),
    ("root only", {"root_policy": "docs/policies/root.md"}),
    ("root empty string", {"root_policy": ""}),
    ("root not a string", {"root_policy": 3}),
    ("dialect empty", {"territory_dialect": ""}),
    ("dialect not a string", {"territory_dialect": 1}),
    ("namespace not a mapping", {"notes-policy": "docs/**"}),
    ("territory not a list", {"notes-policy": {"territory": "docs/**"}}),
    ("territory with empty item", {"notes-policy": {"territory": [""]}}),
    ("territory with non-string item", {"notes-policy": {"territory": [1]}}),
    ("valid policy namespace", {"notes-policy": {"territory": ["docs/notes/**"], "anything": 1}}),
    ("policy namespace null", {"notes-policy": None}),
    ("own namespace null", {"const-meta-types": None}),
    ("own namespace not a mapping", {"const-meta-types": "x"}),
    ("another module's namespace not a mapping", {"const-other": 5}),
    ("another module's territory not a list", {"const-other": {"territory": "x"}}),
    ("own territory with a non-string item", {"const-meta-types": {"territory": [1]}}),
]
# Kernel §6: a reader reads its own namespace and the policy namespaces, no other module's. A
# namespace named like a module is a policy's only when a policy document carries that id, so
# its territory is read leniently, and what another module's namespace holds is that module's
# to validate. On these cases the schema is stricter than this reader, on purpose.
NOT_THIS_READERS = {
    "another module's namespace not a mapping",
    "another module's territory not a list",
    "own territory with a non-string item",
}


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


def record_validator(
    record_schema: dict[str, object], envelope_schema: dict[str, object]
) -> jsonschema.Draft202012Validator:
    """The record schema extends the envelope schema by reference; resolve it from the kit's files."""
    resource = referencing.Resource.from_contents(envelope_schema)
    registry = referencing.Registry().with_resource(str(envelope_schema["$id"]), resource)
    return jsonschema.Draft202012Validator(record_schema, registry=registry)


def dials_disagreement(name: str, mirror: bool, schema: bool) -> Disagreement | None:
    """Stricter is fine, looser is not; a case listed as another reader's must stay one the
    mirror accepts and the schema rejects."""
    if name not in NOT_THIS_READERS:
        if mirror and not schema:
            return Disagreement(
                f"dials '{name}': the schema rejects it but the mirror accepts it", WHY_MIRROR, ALIGN
            )
        return None
    if mirror and not schema:
        return None
    remove = f"remove '{name}' from NOT_THIS_READERS in {THIS_FILE}"
    if mirror:
        return Disagreement(
            f"dials '{name}': listed as another reader's, but the schema accepts it too",
            WHY_EXEMPTION,
            remove,
        )
    return Disagreement(
        f"dials '{name}': listed as another reader's, but the mirror rejects it",
        WHY_EXEMPTION,
        f"{remove}, or, where kernel §6 keeps the key another reader's, stop dials.py of shared/const_gate/"
        " from judging it",
    )


def record_disagreement(name: str, mirror: bool, schema: bool) -> Disagreement | None:
    """Equality; a case listed as stricter on purpose must stay one the schema accepts and the
    mirror rejects."""
    listed = name in STRICTER_ON_PURPOSE
    if listed and schema and not mirror:
        return None
    if mirror != schema:
        return Disagreement(
            f"record '{name}': schema accepts={schema}, mirror accepts={mirror}", WHY_MIRROR, ALIGN
        )
    if not listed:
        return None
    if not schema:
        return Disagreement(
            f"record '{name}': listed as stricter on purpose, but the schema rejects it too: the schema"
            " caught up",
            WHY_EXEMPTION,
            f"remove '{name}' from STRICTER_ON_PURPOSE in {THIS_FILE}",
        )
    return Disagreement(
        f"record '{name}': listed as stricter on purpose, but the mirror accepts it:"
        " the stricter rule is gone",
        "the rule was kept stricter than the schema on purpose, and its loss lets the case through unseen",
        "restore the rule in checks.py of const-decision-records, or, where its end is decided, remove"
        f" '{name}' from STRICTER_ON_PURPOSE in {THIS_FILE}",
    )


def main() -> int:
    identity.declare(start.GATE)  # the shared reader asks which gate it serves
    schemas = KIT / "kernel" / "schemas"
    envelope_schema = json.loads((schemas / "document-frontmatter.schema.json").read_text(encoding="utf-8"))
    record_schema = json.loads((schemas / "decision-record.schema.json").read_text(encoding="utf-8"))
    dials_schema = json.loads((schemas / "constitution.schema.json").read_text(encoding="utf-8"))
    disagreements: list[Disagreement] = []
    corpus = envelope_corpus()
    for case in corpus:
        text = "---\n" + yaml.safe_dump(case.fields, sort_keys=False) + "---\n"
        mirror = not envelope_errors(parse_envelope(text))
        schema = schema_accepts(envelope_schema, case.fields)
        if mirror != schema:
            disagreements.append(
                Disagreement(
                    f"envelope '{case.name}': schema accepts={schema}, mirror accepts={mirror}",
                    WHY_MIRROR,
                    ALIGN,
                )
            )
    for name, instance in DIALS_CORPUS:
        mirror, schema = mirror_accepts_dials(instance), schema_accepts(dials_schema, instance)
        found = dials_disagreement(name, mirror, schema)
        disagreements += [found] if found else []
    records = record_corpus()
    validator = record_validator(record_schema, envelope_schema)
    for case in records:
        text = "---\n" + yaml.safe_dump(case.fields, sort_keys=False) + "---\n"
        mirror = not check_record("record.md", parse_envelope(text))
        schema = not list(validator.iter_errors(case.fields))
        found = record_disagreement(case.name, mirror, schema)
        disagreements += [found] if found else []
    for listed, names, corpus_names in (
        ("NOT_THIS_READERS", NOT_THIS_READERS, {name for name, _ in DIALS_CORPUS}),
        ("STRICTER_ON_PURPOSE", STRICTER_ON_PURPOSE, {case.name for case in records}),
    ):
        for name in sorted(names - corpus_names):
            disagreements.append(
                Disagreement(
                    f"{listed} lists '{name}', but no corpus case carries it",
                    WHY_EXEMPTION,
                    f"remove '{name}' from {listed} in {THIS_FILE}",
                )
            )
    counts = (
        f"{len(corpus)} envelope cases (equality), {len(DIALS_CORPUS)} dials cases (never more lenient on"
        f" the keys a gate reads; {len(NOT_THIS_READERS)} are another reader's),"
        f" {len(records)} record cases (equality but {len(STRICTER_ON_PURPOSE)} stricter on purpose) examined"
    )
    if disagreements:
        for found in disagreements:
            print(f"RED: {found.what}\n  why: {found.why}\n  fix: {found.fix}")
        print(f"RED: {len(disagreements)} disagreement(s) — {counts}")
        return 2
    print(f"GREEN: the mirrors agree with the kernel schemas — {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
