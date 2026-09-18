"""The checks, as functions of typed inputs: resolution (which policy governs a document)
and the envelope (is the document governable)."""

from __future__ import annotations

from . import messages
from .envelope import declared_policy, envelope_errors, parse_envelope
from .index import Index
from .model import Dials, Envelope, EnvelopeState, Examination, Finding, MetaType


def resolve(index: Index, rel: str, envelope: Envelope) -> tuple[str | None, list[Finding]]:
    """Path first; a declaration only where the path mapping is absent or ambiguous.
    Returns the governing policy id (None when unresolved or outside) and the findings."""
    matches = index.matches(rel)
    declared = declared_policy(envelope)
    if len(matches) == 1:
        match = matches[0]
        if declared is None or declared == match.policy_id:
            return match.policy_id, []
        territory = index.policies[declared].territory if declared in index.policies else None
        return None, [messages.f8_contradiction(rel, declared, match, territory)]
    if len(matches) > 1:
        if declared is None:
            return None, [messages.f7_multi_policy(rel, matches)]
        if declared in {m.policy_id for m in matches}:
            return declared, []
        return None, [messages.f8b_contradiction_in_overlap(rel, declared, matches)]
    if declared is None:
        return None, []                                     # outside claimed territory: silence
    if declared in index.policies:
        return declared, []
    return None, [messages.f6_no_such_policy(rel, declared, index.root_territory)]


def check_envelope(index: Index, rel: str, envelope: Envelope) -> list[Finding]:
    """Shape, fields, the policy-type rule, and id uniqueness in the present tree."""
    match envelope.state:
        case EnvelopeState.NONE:
            return [messages.f1_no_envelope(rel)]
        case EnvelopeState.UNTERMINATED:
            return [messages.f2_unterminated(rel)]
        case EnvelopeState.INVALID:
            return [messages.f3_invalid_yaml(rel, envelope.detail)]
        case EnvelopeState.OK:
            pass
    errors = envelope_errors(envelope)
    if errors:
        return [messages.f4_invalid_fields(rel, errors)]
    findings: list[Finding] = []
    meta_type, doc_id = envelope.text("type") or "", envelope.text("id") or ""
    if rel in index.in_root and meta_type != MetaType.CURRENT_STATE:
        findings.append(messages.f10_policy_type(rel, meta_type, index.root_territory))
    others = [path for path in index.id_owners().get(doc_id, []) if path != rel]
    if others:
        findings.append(messages.f5_duplicate_id(rel, doc_id, others[0]))
    return findings


def examine(index: Index, rel: str, text: str) -> Examination:
    envelope = parse_envelope(text)
    policy, findings = resolve(index, rel, envelope)
    if policy is None and not findings:
        return Examination((), None)
    return Examination(tuple(findings + check_envelope(index, rel, envelope)), policy)


def check_root_policy(dials: Dials, rel: str, text: str) -> list[Finding]:
    """The root policy about to be written. A damaged root is a finding on this write, never
    a configuration failure, which would be non-blocking and let the damage land."""
    envelope = parse_envelope(text)
    if envelope.state is not EnvelopeState.OK:
        return [messages.f11_root_unreadable(rel, envelope.detail or envelope.state.value)]
    errors = envelope_errors(envelope)
    if errors:
        return [messages.f4_invalid_fields(rel, errors)]
    findings: list[Finding] = []
    meta_type, doc_id = envelope.text("type") or "", envelope.text("id") or ""
    if meta_type != MetaType.CURRENT_STATE:
        findings.append(messages.f12_root_type(rel, meta_type))
    if not dials.territory_of(doc_id):
        findings.append(messages.f13_root_id_orphaned(rel, doc_id))
    return findings
