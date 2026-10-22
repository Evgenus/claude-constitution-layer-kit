#!/usr/bin/env python3
"""Kit check: the gates' hand-written validation is never more lenient than the kernel's
JSON Schemas — the shared code's mirror of the dials schema (constitution_layer_kit/dials.py, read by
every gate), const-meta-types for the envelope (exactly equal), const-decision-records for
what a decision record adds to the envelope (equal, except where the mirror is stricter on
purpose: a decider of blanks).

A module ships without the kit, so it cannot read kernel/schemas/ at run time; it carries
a mirror of the rules instead. This check runs the real schemas (through the jsonschema
library, a development dependency of the kit only) and the mirror over one corpus and
compares verdicts. The enum and length cases come from the schemas and the mirrors, never from
a list in this script: every value either side holds, plus one value neither may hold, and the
limit of each side with one past it. Each schema is checked against its own draft first and
validated under it. Run from anywhere: python3 scripts/check-schema-mirror.py

An exemption is held too: a case listed as another reader's must still be one the mirror
accepts and the schema rejects, and a case listed as stricter on purpose one the schema
accepts and the mirror rejects — an exemption that stops holding is itself red, with the fix
that removes it or restores the rule it covered.

The dials schema's required key, `module_prefix`, is held on its own: the corpus holds the key absent
and a value of every shape the schema's pattern allows or refuses, and reads each value as the module
whose namespace starts with it, so that the reader's check that its own namespace carries the prefix
(C5.12) never stands in for the pattern; the mirror may be stricter than the schema, never more lenient.

Modes:  no arguments   compare the mirrors with the kit's schemas;
        --self-test    prove the check on mutated copies held in memory: a value added to a
                       schema's enum, a value added to or removed from a mirror's values, a
                       schema limit moved past the mirror's and a schema pattern of the prefix
                       narrowed past the mirror's are each red with the line that names the value
                       and both verdicts; so are a mirror that does not require the prefix and
                       one that holds its pattern loosely; the untouched inputs are green; a schema
                       that breaks its own draft is a BROKEN line.
Exit: 0 green; 2 the mirror and a schema disagree, or an exemption no longer holds; 1 the
check could not run, or a schema breaks its own draft.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import json
import re
import sys
import tempfile
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Any
from unittest import mock

KIT = Path(__file__).resolve().parent.parent
for module in ("const-meta-types", "const-decision-records"):  # kit-side test code only
    sys.path.insert(0, str(KIT / "modules" / module / "plugin" / "scripts"))
sys.path.insert(0, str(KIT / "shared"))  # the shared package: no plugin holds a link to it

try:
    import jsonschema
    import referencing
    import yaml
except ImportError as exc:
    print(f"BROKEN: {exc.name} is not installed — fix: python3 -m pip install jsonschema referencing pyyaml")
    print("BROKEN: the check could not run — 0 cases examined")
    sys.exit(1)

from constitution_layer_kit import dials as dials_reader  # noqa: E402
from constitution_layer_kit import identity  # noqa: E402
from constitution_layer_kit.dials import load_dials  # noqa: E402
from constitution_layer_kit.envelope import parse_envelope  # noqa: E402
from constitution_layer_kit.errors import ConfigurationFailure  # noqa: E402
from constitution_layer_kit.model import MetaType, Status  # noqa: E402
from decision_records_gate import checks as record_checks  # noqa: E402
from decision_records_gate.checks import check_record  # noqa: E402
from decision_records_gate.model import ROUTINE, Stakes  # noqa: E402
from meta_types_gate import checks as meta_checks  # noqa: E402
from meta_types_gate import messages as meta_messages  # noqa: E402
from meta_types_gate import start  # noqa: E402
from meta_types_gate.checks import envelope_errors  # noqa: E402
from meta_types_gate.model import TITLE_MAX  # noqa: E402

EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
OUTSIDE = "zz-not-a-value"  # a value no side may ever hold
GOOD = {"id": "note-a", "type": "non-authoritative", "title": "Note A", "status": "active"}
ENVELOPE_SCHEMA = "kernel/schemas/document-frontmatter.schema.json"
RECORD_SCHEMA = "kernel/schemas/decision-record.schema.json"
DIALS_SCHEMA = "kernel/schemas/constitution.schema.json"
COULD_NOT_RUN = "BROKEN: the check could not run — 0 cases examined"
THIS_FILE = "scripts/check-schema-mirror.py"
WHY_MIRROR = "the module's mirror is the only copy of the kernel schema a consumer has"
WHY_EXEMPTION = "an exemption that no longer holds would hide the next real disagreement on its case"
ALIGN = (
    "align with kernel/schemas/ — dials.py of shared/constitution_layer_kit/,"
    " or checks.py or model.py of the module the line names"
)


@dataclass(frozen=True)
class Disagreement:
    what: str
    why: str
    fix: str


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class EnvelopeCase:
    name: str
    fields: dict[str, object]


@dataclass(frozen=True)
class Mirror:
    """What the hand-written mirrors hold: the values of each closed vocabulary and the title limit."""

    meta_types: frozenset[str]
    statuses: frozenset[str]
    stakes: frozenset[str]  # the recorded levels and ROUTINE, which the mirror names and refuses
    title_max: int


def mirror_values() -> Mirror:
    return Mirror(
        frozenset(t.value for t in MetaType),
        frozenset(s.value for s in Status),
        frozenset(level.value for level in Stakes) | {ROUTINE},
        TITLE_MAX,
    )


def enum_of(schema: dict[str, Any], label: str, key: str) -> set[str]:
    try:
        return {str(value) for value in schema["properties"][key]["enum"]}
    except (KeyError, TypeError) as bad:
        raise Broken(
            f"{label} holds no enum at properties.{key}.enum — fix: restore the enum in {label}"
        ) from bad


def limit_of(schema: dict[str, Any], label: str) -> int:
    try:
        return int(
            schema["properties"]["title"]["maxLength"]
        )  # a draft's own check_schema keeps it an integer
    except (KeyError, TypeError) as bad:
        raise Broken(
            f"{label} holds no maxLength at properties.title.maxLength — fix: restore the limit in {label}"
        ) from bad


def vocabulary_cases(
    base: Mapping[str, object], key: str, schema_values: set[str], held_by_mirror: frozenset[str]
) -> list[EnvelopeCase]:
    """Every value either side holds, and one value neither may: a value only the schema holds, a value only
    the mirror holds and a value dropped from one side each leave a case the two sides judge differently."""
    values = sorted(schema_values | held_by_mirror) + [OUTSIDE]
    return [EnvelopeCase(f"{key} '{value}'", {**base, key: value}) for value in values]


def length_cases(schema_max: int, mirror_max: int) -> list[EnvelopeCase]:
    """The limit of each side and one past it: with equal limits one pair, with unequal limits two, so a
    length one side accepts and the other rejects is always among the cases."""
    limits = sorted({schema_max, mirror_max})
    return [
        EnvelopeCase(f"title {n}", {**GOOD, "title": "x" * n}) for limit in limits for n in (limit, limit + 1)
    ]


def envelope_corpus(schema: dict[str, Any], mirror: Mirror) -> list[EnvelopeCase]:
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
        EnvelopeCase("title empty", {**GOOD, "title": ""}),
        EnvelopeCase("title of spaces", {**GOOD, "title": "   "}),
        EnvelopeCase("title of two lines", {**GOOD, "title": "a\nb"}),
    ]
    cases += vocabulary_cases(GOOD, "type", enum_of(schema, ENVELOPE_SCHEMA, "type"), mirror.meta_types)
    cases += vocabulary_cases(GOOD, "status", enum_of(schema, ENVELOPE_SCHEMA, "status"), mirror.statuses)
    cases += length_cases(limit_of(schema, ENVELOPE_SCHEMA), mirror.title_max)
    return cases


RECORD = {**GOOD, "id": "record-a", "type": "task-record", "stakes": "process", "decider": "the maintainer"}
STRICTER_ON_PURPOSE = {"decider of blanks"}  # the schema's minLength 1 lets blanks through


def record_corpus(schema: dict[str, Any], mirror: Mirror) -> list[EnvelopeCase]:
    """The envelope's own four fields stay valid throughout: only what a record adds varies."""
    cases = [EnvelopeCase("valid record", dict(RECORD))]
    cases += vocabulary_cases(RECORD, "stakes", enum_of(schema, RECORD_SCHEMA, "stakes"), mirror.stakes)
    cases.append(EnvelopeCase("stakes ''", {**RECORD, "stakes": ""}))
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


PREFIX = {"module_prefix": "const-"}  # the required key, as the kit writes it
DIALS_CORPUS: list[tuple[str, object]] = [
    ("empty file", {}),
    ("prefix only", dict(PREFIX)),
    ("prefix absent", {"root_policy": "docs/policies/root.md"}),
    ("prefix of another layer", {"module_prefix": "other-"}),
    ("root only", {**PREFIX, "root_policy": "docs/policies/root.md"}),
    ("root empty string", {**PREFIX, "root_policy": ""}),
    ("root not a string", {**PREFIX, "root_policy": 3}),
    ("dialect empty", {**PREFIX, "territory_dialect": ""}),
    ("dialect not a string", {**PREFIX, "territory_dialect": 1}),
    ("namespace not a mapping", {**PREFIX, "notes-policy": "docs/**"}),
    ("territory not a list", {**PREFIX, "notes-policy": {"territory": "docs/**"}}),
    ("territory with empty item", {**PREFIX, "notes-policy": {"territory": [""]}}),
    ("territory with non-string item", {**PREFIX, "notes-policy": {"territory": [1]}}),
    ("valid policy namespace", {**PREFIX, "notes-policy": {"territory": ["docs/notes/**"], "anything": 1}}),
    ("policy namespace null", {**PREFIX, "notes-policy": None}),
    ("own namespace null", {**PREFIX, "const-meta-types": None}),
    ("own namespace not a mapping", {**PREFIX, "const-meta-types": "x"}),
    ("another module's namespace not a mapping", {**PREFIX, "const-other": 5}),
    ("another module's territory not a list", {**PREFIX, "const-other": {"territory": "x"}}),
    ("own territory with a non-string item", {**PREFIX, "const-meta-types": {"territory": [1]}}),
]
# The values of `module_prefix` the schema's pattern allows or refuses, each read by a module whose
# namespace starts with the value (`READER_SUFFIX` after it), so that the pattern is all that judges it. The
# schema is the Python `re` of the validator: it takes a trailing line feed after the '-', which the
# pattern's `$` allows there; the mirror, which holds the whole value, is stricter on that one.
READER_SUFFIX = "x"
# The case that the self-test's loose-pattern mirror must fail on: a value that the kit's own namespace does
# not start with. A reader left at the kit's own namespace, `const-…`, would pass the value `const` on the
# strength of that namespace whatever the pattern says, so a case on `const` cannot show the reader is the
# case's own.
UPPER_CASE_PREFIX = "prefix with an upper-case letter"
PREFIX_SHAPES: list[tuple[str, object]] = [
    ("prefix of one word", "const-"),
    ("prefix of two words", "const-meta-"),
    ("prefix of three words", "ab-cd-ef-"),
    ("prefix with digits", "a1-b2-"),
    ("prefix with a digit-only word", "a-1-"),
    ("prefix of one letter", "a-"),
    ("prefix without a trailing dash", "const"),
    ("prefix with a doubled dash", "const--"),
    ("prefix with a leading dash", "-const-"),
    ("prefix of a dash alone", "-"),
    (UPPER_CASE_PREFIX, "Const-"),
    ("prefix in upper case", "CONST-"),
    ("prefix with a first digit", "1const-"),
    ("prefix with an underscore", "const_x-"),
    ("prefix with a space inside", "const -"),
    ("prefix with a trailing space", "const- "),
    ("prefix with a leading space", " const-"),
    ("prefix with a line feed after the dash", "const-\n"),
    ("prefix with a letter beyond ASCII", "çonst-"),
    ("prefix with a digit beyond ASCII", "a\u0663-"),
    ("prefix empty", ""),
    ("prefix a number", 3),
    ("prefix a boolean", True),
    ("prefix null", None),
    ("prefix a list", ["const-"]),
    ("prefix a mapping", {"const-": 1}),
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


def validator_of(schema: dict[str, Any], label: str, **options: Any) -> jsonschema.Validator:
    """The validator of the draft the schema declares, after the schema is checked against that draft."""
    draft = jsonschema.validators.validator_for(schema)
    try:
        draft.check_schema(schema)
    except jsonschema.SchemaError as bad:
        raise Broken(f"{label} breaks its own draft ({bad.message}) — fix: repair the schema") from bad
    return draft(schema, **options)


def schema_accepts(validator: jsonschema.Validator, instance: Any) -> bool:
    return not list(validator.iter_errors(instance))


def dials_cases() -> list[tuple[str, object, str | None]]:
    """Every dials case with the namespace of the module that reads it: None for the kit's own reader of
    this check, a name that starts with the prefix for a value of `module_prefix` that is a string, so that
    the reader's check of its own namespace against the prefix never judges the pattern."""
    cases: list[tuple[str, object, str | None]] = [(name, instance, None) for name, instance in DIALS_CORPUS]
    for name, value in PREFIX_SHAPES:
        reader = value + READER_SUFFIX if isinstance(value, str) else None
        cases.append((name, {"module_prefix": value}, reader))
    return cases


@contextlib.contextmanager
def reading_as(namespace: str | None) -> Iterator[None]:
    """The shared reader asks which module reads the file. The identity is declared once per process, so for
    the span of the block it is declared afresh under another namespace, and the first is restored after."""
    if namespace is None:
        yield
        return
    with mock.patch.object(identity, "_declared", None):
        identity.declare(replace(start.GATE, namespace=namespace))
        yield


def mirror_accepts_dials(instance: object, reader: str | None = None) -> bool:
    with tempfile.TemporaryDirectory() as tmp, reading_as(reader):
        Path(tmp, "constitution.yaml").write_text(yaml.safe_dump(instance), encoding="utf-8")
        try:
            load_dials(Path(tmp))
        except ConfigurationFailure:
            return False
        return True


def record_validator(record_schema: dict[str, Any], envelope_schema: dict[str, Any]) -> jsonschema.Validator:
    """The record schema extends the envelope schema by reference; resolve it from the kit's files."""
    resource = referencing.Resource.from_contents(envelope_schema)
    registry = referencing.Registry().with_resource(str(envelope_schema["$id"]), resource)
    return validator_of(record_schema, RECORD_SCHEMA, registry=registry)


def values_of(name: str, values: set[str] | frozenset[str]) -> Any:
    """An enum class of exactly these values, the stand-in the mirror code reads in place of its own."""
    return StrEnum(name, {value: value for value in sorted(values)})


@contextlib.contextmanager
def applied(mirror: Mirror) -> Iterator[None]:
    """Let the mirror code read these values where they differ from its own, for the span of the block,
    so a mirror that gains or loses a value can be tried without editing the enums it reads."""
    real = mirror_values()
    with contextlib.ExitStack() as stack:
        if mirror.meta_types != real.meta_types:
            stack.enter_context(
                mock.patch.object(meta_checks, "MetaType", values_of("MetaType", mirror.meta_types))
            )
        if mirror.statuses != real.statuses:
            stack.enter_context(
                mock.patch.object(meta_checks, "Status", values_of("Status", mirror.statuses))
            )
        if mirror.title_max != real.title_max:
            stack.enter_context(mock.patch.object(meta_checks, "TITLE_MAX", mirror.title_max))
        if mirror.stakes != real.stakes:
            stack.enter_context(
                mock.patch.object(record_checks, "Stakes", values_of("Stakes", mirror.stakes - {ROUTINE}))
            )
        yield


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
        f"{remove}, or, where kernel §6 keeps the key another reader's, stop dials.py of"
        " shared/constitution_layer_kit/"
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


@dataclass(frozen=True)
class Comparison:
    disagreements: list[Disagreement]
    counts: str


def frontmatter(fields: dict[str, object]) -> str:
    return "---\n" + yaml.safe_dump(fields, sort_keys=False) + "---\n"


def compare(
    envelope_schema: dict[str, Any],
    record_schema: dict[str, Any],
    dials_schema: dict[str, Any],
    mirror: Mirror,
) -> Comparison:
    """Run the schemas and the mirror over one corpus, drawn from both; the inputs are passed in, so a
    caller can hand over altered copies. A schema that breaks its own draft raises Broken."""
    envelope_validator = validator_of(envelope_schema, ENVELOPE_SCHEMA)
    record_check = record_validator(record_schema, envelope_schema)
    dials_validator = validator_of(dials_schema, DIALS_SCHEMA)
    corpus = envelope_corpus(envelope_schema, mirror)
    records = record_corpus(record_schema, mirror)
    disagreements: list[Disagreement] = []
    with applied(mirror):
        for case in corpus:
            mirror_says = not envelope_errors(parse_envelope(frontmatter(case.fields)))
            schema_says = schema_accepts(envelope_validator, case.fields)
            if mirror_says != schema_says:
                disagreements.append(
                    Disagreement(
                        f"envelope '{case.name}': schema accepts={schema_says}, mirror accepts={mirror_says}",
                        WHY_MIRROR,
                        ALIGN,
                    )
                )
        for name, instance, reader in dials_cases():
            mirror_says, schema_says = (
                mirror_accepts_dials(instance, reader),
                schema_accepts(dials_validator, instance),
            )
            found = dials_disagreement(name, mirror_says, schema_says)
            disagreements += [found] if found else []
        for case in records:
            mirror_says = not check_record("record.md", parse_envelope(frontmatter(case.fields)))
            schema_says = schema_accepts(record_check, case.fields)
            found = record_disagreement(case.name, mirror_says, schema_says)
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
        f"{len(corpus)} envelope cases (equality), {len(dials_cases())} dials cases (never more lenient on"
        f" the keys a gate reads; {len(NOT_THIS_READERS)} are another reader's),"
        f" {len(records)} record cases (equality but {len(STRICTER_ON_PURPOSE)} stricter on purpose) examined"
    )
    return Comparison(disagreements, counts)


def render(comparison: Comparison) -> tuple[int, list[str]]:
    if comparison.disagreements:
        lines = [f"RED: {d.what}\n  why: {d.why}\n  fix: {d.fix}" for d in comparison.disagreements]
        lines.append(f"RED: {len(comparison.disagreements)} disagreement(s) — {comparison.counts}")
        return EXIT_RED, lines
    return EXIT_GREEN, [f"GREEN: the mirrors agree with the kernel schemas — {comparison.counts}"]


def broken_lines(broken: Broken) -> tuple[int, list[str]]:
    return EXIT_BROKEN, [f"BROKEN: {broken}", COULD_NOT_RUN]


def outcome(
    envelope_schema: dict[str, Any],
    record_schema: dict[str, Any],
    dials_schema: dict[str, Any],
    mirror: Mirror,
) -> tuple[int, list[str]]:
    try:
        return render(compare(envelope_schema, record_schema, dials_schema, mirror))
    except Broken as broken:
        return broken_lines(broken)


def load_schema(name: str) -> dict[str, Any]:
    try:
        schema = json.loads((KIT / name).read_text(encoding="utf-8"))
    except (OSError, ValueError) as bad:
        raise Broken(f"{name} cannot be read as JSON ({bad}) — fix: restore the schema") from bad
    if not isinstance(schema, dict):
        raise Broken(f"{name} is not a JSON object — fix: restore the schema")
    return schema


def load_schemas() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_schema(ENVELOPE_SCHEMA), load_schema(RECORD_SCHEMA), load_schema(DIALS_SCHEMA)


def with_enum_value(schema: dict[str, Any], key: str, value: str) -> dict[str, Any]:
    changed = copy.deepcopy(schema)
    changed["properties"][key]["enum"].append(value)
    return changed


def with_title_limit(schema: dict[str, Any], limit: int) -> dict[str, Any]:
    changed = copy.deepcopy(schema)
    changed["properties"]["title"]["maxLength"] = limit
    return changed


def with_broken_property(schema: dict[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(schema)
    changed["properties"]["zz-broken"] = {"type": 7}  # no draft allows a type that is a number
    return changed


@contextlib.contextmanager
def mirror_accepting_any_status() -> Iterator[None]:
    """A mirror whose status check lets every value through: the error it gives for the value no side
    holds, `OUTSIDE`, is dropped. Neither side lists that value, so only the case `vocabulary_cases` adds
    for it can show the mirror to be looser than the schema."""
    real = envelope_errors
    refusal = meta_messages.f4_status_not_allowed(OUTSIDE)

    def lenient(envelope: Any) -> list[str]:
        return [error for error in real(envelope) if error != refusal]

    with mock.patch.dict(globals(), {"envelope_errors": lenient}):
        yield


def with_prefix_pattern(schema: dict[str, Any], pattern: str) -> dict[str, Any]:
    changed = copy.deepcopy(schema)
    changed["properties"]["module_prefix"]["pattern"] = pattern
    return changed


@contextlib.contextmanager
def mirror_defaulting_the_prefix() -> Iterator[None]:
    """A mirror that reads a file with no `module_prefix`, or a null one, as if it named `const-`: the key
    is no longer required, though the schema requires it."""
    real = dials_reader._module_prefix

    def lenient(value: object) -> str:
        return real(value) if value is not None else "const-"

    with mock.patch.object(dials_reader, "_module_prefix", lenient):
        yield


@contextlib.contextmanager
def mirror_with_a_loose_prefix_pattern() -> Iterator[None]:
    """A mirror whose pattern of the prefix takes any string: a value the schema's pattern refuses, such as
    one with no '-' at its end, is then read."""
    with mock.patch.object(dials_reader, "_PREFIX_SHAPE", re.compile(".*")):
        yield


def self_test() -> int:
    """Red→green on mutated copies held in memory: each mutation is red with the line that names the
    value and both verdicts, the untouched inputs are green, a schema that breaks its draft is BROKEN."""
    envelope, record, dials = load_schemas()
    real = mirror_values()
    drafted = "breaks its own draft ("
    cases: list[
        tuple[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any], Mirror], int, tuple[str, ...]]
    ] = [
        (
            "a meta-type added to the schema's enum is red",
            (with_enum_value(envelope, "type", "draft"), record, dials, real),
            EXIT_RED,
            ("RED: envelope 'type 'draft'': schema accepts=True, mirror accepts=False",),
        ),
        (
            "a status added to the schema's enum is red",
            (with_enum_value(envelope, "status", "archived"), record, dials, real),
            EXIT_RED,
            ("RED: envelope 'status 'archived'': schema accepts=True, mirror accepts=False",),
        ),
        (
            "a stakes level added to the schema's enum is red",
            (envelope, with_enum_value(record, "stakes", "security"), dials, real),
            EXIT_RED,
            ("RED: record 'stakes 'security'': schema accepts=True, mirror accepts=False",),
        ),
        (
            "a status added to the mirror's values is red",
            (envelope, record, dials, replace(real, statuses=real.statuses | {"archived"})),
            EXIT_RED,
            ("RED: envelope 'status 'archived'': schema accepts=False, mirror accepts=True",),
        ),
        (
            "a stakes level added to the mirror's values is red",
            (envelope, record, dials, replace(real, stakes=real.stakes | {"security"})),
            EXIT_RED,
            ("RED: record 'stakes 'security'': schema accepts=False, mirror accepts=True",),
        ),
        (
            "a status removed from the mirror's values is red",
            (envelope, record, dials, replace(real, statuses=real.statuses - {"inactive"})),
            EXIT_RED,
            ("RED: envelope 'status 'inactive'': schema accepts=True, mirror accepts=False",),
        ),
        (
            "a schema title limit moved past the mirror's is red",
            (with_title_limit(envelope, real.title_max + 100), record, dials, real),
            EXIT_RED,
            (f"RED: envelope 'title {real.title_max + 1}': schema accepts=True, mirror accepts=False",),
        ),
        (
            "a mirror that accepts a status neither side lists is red",
            (envelope, record, dials, real),
            EXIT_RED,
            (f"RED: envelope 'status '{OUTSIDE}'': schema accepts=False, mirror accepts=True",),
        ),
        (
            "a schema pattern of the prefix narrowed past the mirror's is red",
            (envelope, record, with_prefix_pattern(dials, "^[a-z]+-$"), real),
            EXIT_RED,
            ("RED: dials 'prefix of two words': the schema rejects it but the mirror accepts it",),
        ),
        (
            "a mirror that does not require the prefix is red",
            (envelope, record, dials, real),
            EXIT_RED,
            ("RED: dials 'prefix absent': the schema rejects it but the mirror accepts it",),
        ),
        (
            "a mirror that holds the prefix's pattern loosely is red",
            (envelope, record, dials, real),
            EXIT_RED,
            (f"RED: dials '{UPPER_CASE_PREFIX}': the schema rejects it but the mirror accepts it",),
        ),
        (
            "the untouched inputs are green",
            (envelope, record, dials, real),
            EXIT_GREEN,
            ("GREEN: the mirrors agree with the kernel schemas — ",),
        ),
        (
            "a schema that breaks its own draft is a teaching BROKEN line",
            (with_broken_property(envelope), record, dials, real),
            EXIT_BROKEN,
            (f"BROKEN: {ENVELOPE_SCHEMA} {drafted}", ") — fix: repair the schema"),
        ),
    ]
    under: dict[str, Callable[[], contextlib.AbstractContextManager[None]]] = {
        "a mirror that accepts a status neither side lists is red": mirror_accepting_any_status,
        "a mirror that does not require the prefix is red": mirror_defaulting_the_prefix,
        "a mirror that holds the prefix's pattern loosely is red": mirror_with_a_loose_prefix_pattern,
    }
    failed = 0
    for name, inputs, wanted_code, wanted in cases:
        with under.get(name, contextlib.nullcontext)():
            code, lines = outcome(*inputs)
        said = [line for line in "\n".join(lines).splitlines() if all(part in line for part in wanted)]
        ok = code == wanted_code and bool(said)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        exit {code}, wanted {wanted_code} with a line holding {wanted}")
            print("        " + "\n        ".join("\n".join(lines).splitlines()))
    print(f"{len(cases) - failed}/{len(cases)} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-schema-mirror", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print(COULD_NOT_RUN)
        return EXIT_BROKEN
    identity.declare(start.GATE)  # the shared reader asks which gate it serves
    identity.declare_dials_file("constitution.yaml")  # ... and which file it opens
    try:
        if args.self_test:
            return self_test()
        code, lines = outcome(*load_schemas(), mirror_values())
    except Broken as broken:
        code, lines = broken_lines(broken)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
