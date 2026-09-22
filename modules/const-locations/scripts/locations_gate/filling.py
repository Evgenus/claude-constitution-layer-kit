"""The text of the new document: the envelope's id, title and status as the command's values,
type as the template's, every other line of the template as it stands."""

from __future__ import annotations

import re

import yaml
from const_gate.envelope import parse_envelope
from const_gate.errors import ConfigurationFailure
from const_gate.model import EnvelopeState, MetaType, Status

from . import messages

OWN_FIELDS = ("id", "title", "status")
FIELD_LINE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:")


def _line(key: str, value: str) -> str:
    """One `key: value` line, quoted as YAML needs it."""
    return yaml.safe_dump({key: value}, allow_unicode=True, width=10_000).rstrip("\n")


def from_envelope_alone(doc_id: str, meta_type: MetaType, title: str) -> str:
    block = yaml.safe_dump(
        {"id": doc_id, "type": meta_type.value, "title": title, "status": Status.ACTIVE.value},
        sort_keys=False,
        allow_unicode=True,
        width=10_000,
    )
    return f"---\n{block}---\n\n# {title}\n"


def from_template(template: str, path: str, doc_id: str, title: str, given_type: MetaType | None) -> str:
    """The template with its envelope's id, title and status replaced by values; the body verbatim."""
    envelope = parse_envelope(template)
    if envelope.state is not EnvelopeState.OK:
        detail = envelope.detail or envelope.state.value
        raise ConfigurationFailure(messages.l5_template_no_envelope(path, detail))
    fixed = envelope.text("type")
    if fixed is None or fixed not in {t.value for t in MetaType}:
        raise ConfigurationFailure(
            messages.l5_template_bad_type(
                path, envelope.fields["type"].shown if "type" in envelope.fields else "missing"
            )
        )
    if given_type is not None and given_type.value != fixed:
        raise ConfigurationFailure(messages.l5_type_conflict(given_type.value, path, fixed))
    values = {"id": doc_id, "title": title, "status": Status.ACTIVE.value}
    lines = template.lstrip("﻿").split("\n")
    close = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    block: list[str] = []
    written: set[str] = set()
    skipping = False
    for line in lines[1:close]:
        if skipping and (line.startswith((" ", "\t")) or not line.strip()):
            continue  # a continuation line of the value just replaced
        skipping = False
        found = FIELD_LINE.match(line)
        key = found.group("key") if found else None
        if key in values:
            if key not in written:
                block.append(_line(key, values[key]))
                written.add(key)
            skipping = True
            continue
        block.append(line)
    for key in OWN_FIELDS:
        if key not in written:
            block.append(_line(key, values[key]))
    return "\n".join(["---", *block, "---", *lines[close + 1 :]])
