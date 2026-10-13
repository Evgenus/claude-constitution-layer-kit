"""The text of the new document: the envelope's id, title and status as the command's values,
type as the template's, every other line of the template as it stands."""

from __future__ import annotations

import re

import yaml
from const_gate.envelope import envelope_bounds, envelope_lines, parse_envelope
from const_gate.errors import ConfigurationFailure
from const_gate.model import Envelope, EnvelopeState, MetaType, Status

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
    _refuse_type(envelope, path, given_type)
    values = {"id": doc_id, "title": title, "status": Status.ACTIVE.value}
    bounds = envelope_bounds(template)
    if bounds is None or bounds.yaml_end is None or bounds.end is None:  # unreachable: read OK above
        raise ConfigurationFailure(messages.l5_template_no_envelope(path, envelope.state.value))
    # the block as lines, cut where the helper cuts them: each without its line ending
    lines = [content for _, content, _ in envelope_lines(template, bounds.yaml_start, bounds.yaml_end)]
    block = _block(lines, values)
    closing = template[bounds.yaml_end : bounds.end]  # the closing line as written: a break ends it, or none
    ending = "\n" if closing.endswith(("\n", "\r")) else ""
    return "".join(f"{line}\n" for line in ["---", *block]) + "---" + ending + template[bounds.end :]


def _refuse_type(envelope: Envelope, path: str, given_type: MetaType | None) -> None:
    """Refuses a template whose type is missing or no meta-type, or not the type the command gave."""
    fixed = envelope.text("type")
    if fixed is None or fixed not in {t.value for t in MetaType}:
        raise ConfigurationFailure(
            messages.l5_template_bad_type(
                path, envelope.fields["type"].shown if "type" in envelope.fields else "missing"
            )
        )
    if given_type is not None and given_type.value != fixed:
        raise ConfigurationFailure(messages.l5_type_conflict(given_type.value, path, fixed))


def _block(lines: list[str], values: dict[str, str]) -> list[str]:
    """The envelope's lines with the first line of each own field replaced by its value, its
    continuation lines and any later line of the same field dropped; a field absent is added last."""
    block: list[str] = []
    written: set[str] = set()
    skipping = False
    for line in lines:
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
    return block
