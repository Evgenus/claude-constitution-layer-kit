"""The envelope: the YAML block between a first line '---' and the next line '---'. Every
field is kept as YAML read it; which fields matter, and what is valid, is the module's."""

from __future__ import annotations

import re

import yaml

from . import messages
from .model import DECLARATION, Envelope, EnvelopeState, FieldValue

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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
            return Envelope(EnvelopeState.INVALID, detail=yaml_error_line(exc))
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            return Envelope(EnvelopeState.INVALID, detail=messages.detail_not_a_mapping())
        fields = {str(key): _field(value) for key, value in loaded.items() if value is not None}
        return Envelope(EnvelopeState.OK, fields=fields)
    return Envelope(EnvelopeState.UNTERMINATED)


def yaml_error_line(exc: yaml.YAMLError) -> str:
    """The parser's whole message on one line: what it met, and the line and column."""
    return " ".join(str(exc).split())


def _field(value: object) -> FieldValue:
    return FieldValue(
        text=value if isinstance(value, str) else None, yaml_type=type(value).__name__, shown=str(value)
    )


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
