"""The checks, as functions of typed inputs: is this document a decision record, and does
its envelope carry what a record adds — the type, the stakes, the decider."""

from __future__ import annotations

from collections.abc import Sequence

from . import messages
from .envelope import declared_policy, parse_envelope
from .index import Index
from .model import ROUTINE, Envelope, EnvelopeState, Examination, Finding, MetaType, Stakes


def candidate_policies(index: Index, rel: str, envelope: Envelope) -> list[str]:
    """The policies that may govern the document: by path first; a declaration picks among
    several path matches, or stands in where the path maps to none. Whether the resolution
    is a defect is not judged here: every candidate counts, so a record in an overlap is
    still examined as a record."""
    matched = [match.policy_id for match in index.matches(rel)]
    declared = declared_policy(envelope)
    if not matched:
        return [declared] if declared is not None and declared in index.policies else []
    if declared is not None and len(matched) > 1 and declared in matched:
        return [declared]
    return matched


def record_policy(candidates: Sequence[str], record_policies: Sequence[str]) -> str | None:
    """The first candidate that is a record policy; None: the document is not a record."""
    return next((policy for policy in candidates if policy in record_policies), None)


def check_record(rel: str, envelope: Envelope) -> list[Finding]:
    match envelope.state:
        case EnvelopeState.NONE:
            return [messages.r1_no_readable_envelope(rel, messages.r1_detail_none())]
        case EnvelopeState.UNTERMINATED:
            return [messages.r1_no_readable_envelope(rel, messages.r1_detail_unterminated())]
        case EnvelopeState.INVALID:
            detail = messages.r1_detail_invalid_yaml(envelope.detail)
            return [messages.r1_no_readable_envelope(rel, detail)]
        case EnvelopeState.OK:
            pass
    errors: list[str] = []

    def string(key: str) -> str | None:
        value = envelope.fields.get(key)
        if value is None:
            errors.append(messages.f4_field_missing(key))
            return None
        if value.text is None:
            errors.append(messages.f4_field_not_string(key, value.yaml_type))
        return value.text

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
    envelope = parse_envelope(text)
    policy = record_policy(candidate_policies(index, rel, envelope), record_policies)
    if policy is None:
        return Examination((), None)
    return Examination(tuple(check_record(rel, envelope)), policy)
