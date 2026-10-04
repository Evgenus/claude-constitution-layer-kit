"""The envelope: the YAML block between a first line '---' and the next line '---'. Every
field is kept as YAML read it; which fields matter, and what is valid, is the module's."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

import yaml

from . import messages
from .model import DECLARATION, Envelope, EnvelopeState, FieldValue

# The kernel schema's pattern, end to end: `$` would let one trailing line break through, and an id
# is echoed in messages and used as a name; `\Z` ends the match at the string's end whoever calls it.
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\Z")

# Where a line ends: Markdown's line endings, as every renderer and the prose linter read them. Not
# `str.splitlines()`, which also breaks at \x0b, \x0c, \x1c-\x1e, \x85 and U+2028/U+2029.
_LINE_END = re.compile(r"\r\n|\r|\n")
_BOM = "\ufeff"


@dataclass(frozen=True, slots=True)
class Bounds:
    """Character offsets into the text as given, a byte-order mark included."""

    yaml_start: int  # first character after the opening line and its line ending
    yaml_end: int | None  # first character of the closing line; None when no line closes
    end: int | None  # first character after the closing line and its line ending; None when none closes


def envelope_lines(text: str, start: int, stop: int) -> Iterator[tuple[int, str, int]]:
    """The lines of text[start:stop] as (offset, content without its line ending, offset of the next):
    the one place a line ends, at `\\n`, `\\r\\n` or a lone `\\r` and nowhere else."""
    pos = start
    while pos < stop:
        found = _LINE_END.search(text, pos, stop)
        content_end, next_pos = (found.start(), found.end()) if found else (stop, stop)
        yield pos, text[pos:content_end], next_pos
        pos = next_pos


def envelope_bounds(text: str) -> Bounds | None:
    """Where the envelope stands. None when the first line, byte-order marks aside, is not `---`; a
    line is `---` with its trailing whitespace ignored. The closing line is the first later line that
    is `---` the same way. A line ends at `\\n`, `\\r\\n` or a lone `\\r`, and nowhere else."""
    start = len(text) - len(text.lstrip(_BOM))
    lines = envelope_lines(text, start, len(text))
    opening = next(lines, None)
    if opening is None or opening[1].rstrip() != "---":
        return None
    yaml_start = opening[2]
    for offset, content, next_pos in lines:
        if content.rstrip() == "---":
            return Bounds(yaml_start, offset, next_pos)
    return Bounds(yaml_start, None, None)


def parse_envelope(text: str) -> Envelope:
    bounds = envelope_bounds(text)
    if bounds is None:
        return Envelope(EnvelopeState.NONE)
    if bounds.yaml_end is None:
        return Envelope(EnvelopeState.UNTERMINATED)
    block = "\n".join(content for _, content, _ in envelope_lines(text, bounds.yaml_start, bounds.yaml_end))
    try:
        loaded: object = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return Envelope(EnvelopeState.INVALID, detail=yaml_error_line(exc))
    except RecursionError:  # brackets nested past the parser's depth: unreadable, never a crash
        return Envelope(EnvelopeState.INVALID, detail=messages.detail_nested_too_deeply())
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        return Envelope(EnvelopeState.INVALID, detail=messages.detail_not_a_mapping())
    fields = {str(key): _field(value) for key, value in loaded.items() if value is not None}
    return Envelope(EnvelopeState.OK, fields=fields)


def yaml_error_line(exc: yaml.YAMLError) -> str:
    """The parser's whole message on one line: what it met, and the line and column."""
    return " ".join(str(exc).split())


def _field(value: object) -> FieldValue:
    return FieldValue(
        text=value if isinstance(value, str) else None, yaml_type=type(value).__name__, shown=str(value)
    )


def string_field(envelope: Envelope, key: str, errors: list[str]) -> str | None:
    """The field's text. A missing field, or one YAML read as something other than a string,
    is appended to `errors` in the shared wording."""
    value = envelope.fields.get(key)
    if value is None:
        errors.append(messages.field_missing(key))
        return None
    if value.text is None:
        errors.append(messages.field_not_string(key, value.yaml_type))
    return value.text


def document_id(envelope: Envelope) -> str | None:
    """The id, when the envelope is readable and the id well-formed."""
    doc_id = envelope.text("id")
    return doc_id if doc_id is not None and ID_RE.fullmatch(doc_id) else None


def declared_policy(envelope: Envelope) -> str | None:
    """The declaration, when well-formed; a malformed one is an envelope field error."""
    declared = envelope.text(DECLARATION)
    return declared if declared is not None and ID_RE.fullmatch(declared) else None


def id_of_text(text: str | None) -> str | None:
    return document_id(parse_envelope(text or ""))
