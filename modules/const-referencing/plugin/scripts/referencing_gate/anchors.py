"""The anchors a document carries because somebody wrote them: an `id` attribute on any HTML
element, a `name` on an `a`. A heading's generated name is none — it changes with the
heading's words — and neither is a `{#key}` after a heading, which a forge shows as text."""

from __future__ import annotations

import re

from .masking import Masked

_TAG = re.compile(r"<(?P<tag>[A-Za-z][\w-]*)\b(?P<attributes>[^<>]*)>")
_ATTRIBUTE = re.compile(r"\b(?P<name>id|name)\s*=\s*(?P<quote>[\"'])(?P<value>.*?)(?P=quote)", re.IGNORECASE)


def explicit_anchors(masked: Masked) -> frozenset[str]:
    """Read from the masked text: an anchor shown inside code is an example, not an anchor."""
    found: set[str] = set()
    for tag in _TAG.finditer(masked.text):
        for attribute in _ATTRIBUTE.finditer(tag["attributes"]):
            if attribute["name"].lower() == "id" or tag["tag"].lower() == "a":
                found.add(attribute["value"])
    return frozenset(found)
