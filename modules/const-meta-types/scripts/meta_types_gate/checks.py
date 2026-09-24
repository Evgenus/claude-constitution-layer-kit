"""The checks, as functions of typed inputs: the resolution's defects turned into findings,
and the envelope (is the document governable)."""

from __future__ import annotations

from collections.abc import Callable

from const_gate.dials import MODULE_PREFIX
from const_gate.envelope import ID_RE, declared_policy, document_id, parse_envelope, string_field
from const_gate.index import Index
from const_gate.model import (
    DECLARATION,
    Defect,
    Dials,
    Envelope,
    EnvelopeState,
    Examination,
    Finding,
    MetaType,
    Resolution,
    Status,
)
from const_gate.resolution import resolve
from const_gate.territory import Matcher

from . import messages

TITLE_MAX = 200


def resolution_findings(index: Index, rel: str, resolution: Resolution) -> list[Finding]:
    declared, matches = resolution.declared or "", resolution.matches
    match resolution.defect:
        case None:
            return []
        case Defect.NO_SUCH_POLICY:
            return [messages.f6_no_such_policy(rel, declared, index.root_territory)]
        case Defect.MULTI_POLICY:
            return [messages.f7_multi_policy(rel, matches)]
        case Defect.CONTRADICTION:
            territory = index.policies[declared].territory if declared in index.policies else None
            return [messages.f8_contradiction(rel, declared, matches[0], territory)]
        case Defect.CONTRADICTION_IN_OVERLAP:
            return [messages.f8b_contradiction_in_overlap(rel, declared, matches)]


def envelope_errors(envelope: Envelope) -> list[str]:
    """Field-level violations of the kernel's frontmatter schema, in reading order."""
    errors: list[str] = []

    def string(key: str) -> str | None:
        return string_field(envelope, key, errors)

    doc_id = string("id")
    if doc_id is not None and not ID_RE.match(doc_id):
        errors.append(messages.f4_id_not_kebab(doc_id))
    meta_type = string("type")
    if meta_type is not None and meta_type not in {t.value for t in MetaType}:
        errors.append(messages.f4_type_not_allowed(meta_type))
    title = string("title")
    if title is not None and not title:
        errors.append(messages.f4_title_empty())
    elif title is not None and len(title) > TITLE_MAX:
        errors.append(messages.f4_title_too_long())
    status = string("status")
    if status is not None and status not in {s.value for s in Status}:
        errors.append(messages.f4_status_not_allowed(status))
    declaration = envelope.fields.get(DECLARATION)
    if declaration is not None and (declaration.text is None or not ID_RE.match(declaration.text)):
        errors.append(messages.f4_declaration_not_kebab(declaration.shown))
    return errors


def id_owners(index: Index) -> dict[str, list[str]]:
    """id -> the governed documents carrying it (claimed by path, or bound by a declaration
    naming a policy). Built at most once per run, in one pass that reads each Markdown file once,
    and one nobody can read is the shared configuration failure, in a scan or in a write some
    policy governs: an id not read is a uniqueness not checked, and a green line would claim it
    was."""
    claimed = {rel for policy in index.policies.values() for rel in policy.claims}
    owners: dict[str, list[str]] = {}
    for rel, text in index.documents():
        envelope = parse_envelope(text)
        doc_id = document_id(envelope)
        if doc_id is not None and (rel in claimed or declared_policy(envelope) in index.policies):
            owners.setdefault(doc_id, []).append(rel)
    return owners


def void_claims(index: Index, dials: Dials, matcher: Matcher) -> dict[str, dict[str, str]]:
    """namespace -> what its territory would claim, for every namespace that declares a
    territory and has no policy document behind it. One git run per such namespace."""
    return {
        name: matcher.match(namespace.territory, index.paths)
        for name, namespace in dials.namespaces.items()
        if name not in index.policies and not name.startswith(MODULE_PREFIX) and namespace.territory
    }


def check_envelope(index: Index, owners: dict[str, list[str]], rel: str, envelope: Envelope) -> list[Finding]:
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
    others = [path for path in owners.get(doc_id, []) if path != rel]
    if others:
        findings.append(messages.f5_duplicate_id(rel, doc_id, others[0]))
    return findings


def examine(index: Index, owners: Callable[[], dict[str, list[str]]], rel: str, text: str) -> Examination:
    """``owners`` is called only for a document some policy governs, so a write outside every
    territory is skipped without reading the others."""
    envelope = parse_envelope(text)
    resolution = resolve(index, rel, envelope)
    if resolution.outside:
        return Examination((), None)
    findings = resolution_findings(index, rel, resolution) + check_envelope(index, owners(), rel, envelope)
    return Examination(tuple(findings), resolution.policy)


def check_root_policy(dials: Dials, rel: str, text: str) -> list[Finding]:
    """The root policy about to be written. A damaged root is a finding on this write, never
    a configuration failure, which would be non-blocking and let the damage land."""
    envelope = parse_envelope(text)
    if envelope.state is not EnvelopeState.OK:
        detail = {
            EnvelopeState.NONE: messages.f11_detail_no_envelope(),
            EnvelopeState.UNTERMINATED: messages.f11_detail_unterminated(),
        }.get(envelope.state, envelope.detail)
        return [messages.f11_root_unreadable(rel, detail)]
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
