"""The checks, as functions of typed inputs: is this document a decision record, and does
its envelope carry what a record adds — the type, the stakes, the decider."""

from __future__ import annotations

from collections.abc import Sequence

from constitution_layer_kit.envelope import parse_envelope, string_field
from constitution_layer_kit.index import Index
from constitution_layer_kit.model import Envelope, EnvelopeState, Examination, Finding, MetaType, Resolution
from constitution_layer_kit.resolution import resolve

from . import messages
from .model import ROUTINE, Stakes


def record_policy(resolution: Resolution, record_policies: Sequence[str]) -> str | None:
    """The record policy that governs the document, or None: not a record. Where the
    resolution is a defect — an overlap nobody resolved, a declaration against the path —
    every policy whose territory matches still counts: the defect is another check's, and a
    record in an overlap is examined as a record."""
    candidates = (
        [resolution.policy] if resolution.policy is not None else [m.policy_id for m in resolution.matches]
    )
    return next((policy for policy in candidates if policy in record_policies), None)


def check_record(rel: str, envelope: Envelope) -> list[Finding]:
    if envelope.state is not EnvelopeState.OK:
        return [messages.r1_no_readable_envelope(rel, envelope.state, envelope.detail)]
    errors: list[str] = []

    def string(key: str) -> str | None:
        return string_field(envelope, key, errors)

    meta_type = string("type")
    if meta_type is not None and meta_type != MetaType.TASK_RECORD:
        errors.append(messages.r2_type_not_task_record(meta_type))
    stakes = string("stakes")
    routine = stakes == ROUTINE
    if stakes is not None and not routine and stakes not in {level.value for level in Stakes}:
        errors.append(messages.r2_stakes_not_allowed(stakes))
    decider = string("decider")
    if decider is not None and not decider.strip():
        errors.append(messages.r2_decider_empty())
    findings = [messages.r3_routine_record(rel)] if routine else []
    if errors:
        findings.append(messages.r2_invalid_fields(rel, errors))
    return findings


def examine(index: Index, record_policies: Sequence[str], rel: str, text: str) -> Examination:
    if rel in index.in_root:  # where policies live: a policy, whatever else claims the path
        return Examination((), None)
    envelope = parse_envelope(text)
    policy = record_policy(resolve(index, rel, envelope), record_policies)
    if policy is None:
        return Examination((), None)
    return Examination(tuple(check_record(rel, envelope)), policy)
