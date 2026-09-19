"""The envelope: the YAML block between a first line '---' and the next line '---'."""

from __future__ import annotations

import re

import yaml

from . import messages
from .model import DECLARATION, RECORD_FIELDS, Envelope, EnvelopeState, FieldValue, MetaType, Status

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
READ_FIELDS = ("id", "type", "title", "status", DECLARATION, *RECORD_FIELDS)
TITLE_MAX = 200


def parse_envelope(text: str) -> Envelope:
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return Envelope(EnvelopeState.NONE)
    for i in range(1, len(lines)):
        if lines[i].rstrip() != "---":
            continue
        try:
            loaded: object = yaml.safe_load("\n".join(lines[1:i]))
        except yaml.YAMLError as exc:
            return Envelope(EnvelopeState.INVALID, detail=str(exc).splitlines()[0])
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            return Envelope(EnvelopeState.INVALID, detail=messages.detail_not_a_mapping())
        fields = {key: _field(loaded[key]) for key in READ_FIELDS if loaded.get(key) is not None}
        return Envelope(EnvelopeState.OK, fields=fields)
    return Envelope(EnvelopeState.UNTERMINATED)


def _field(value: object) -> FieldValue:
    return FieldValue(
        text=value if isinstance(value, str) else None, yaml_type=type(value).__name__, shown=str(value)
    )


def envelope_errors(envelope: Envelope) -> list[str]:
    """Field-level violations of the kernel's frontmatter schema, in reading order."""
    errors: list[str] = []

    def string(key: str) -> str | None:
        value = envelope.fields.get(key)
        if value is None:
            errors.append(messages.f4_field_missing(key))
            return None
        if value.text is None:
            errors.append(messages.f4_field_not_string(key, value.yaml_type))
        return value.text

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


def document_id(envelope: Envelope) -> str | None:
    """The id, when the envelope is readable and the id well-formed."""
    doc_id = envelope.text("id")
    return doc_id if doc_id is not None and ID_RE.match(doc_id) else None


def declared_policy(envelope: Envelope) -> str | None:
    """The declaration, when well-formed; a malformed one is an envelope field error."""
    declared = envelope.text(DECLARATION)
    return declared if declared is not None and ID_RE.match(declared) else None


def id_of_text(text: str | None) -> str | None:
    return document_id(parse_envelope(text or ""))
