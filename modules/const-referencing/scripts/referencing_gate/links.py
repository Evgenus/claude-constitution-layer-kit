"""The links of a document, with the positions a repair needs.

Found by regular expressions over masked text, not by a Markdown parser: no parser surveyed
gives the source position of an inline link, and a repair must rewrite a destination where
it stands, leaving every other character of the document as it was.
"""

from __future__ import annotations

import re

from .masking import Masked
from .model import Link, LinkKind

# text: no unescaped bracket but balanced pairs one level deep; destination: <in angle brackets>
# or a run without spaces, balanced parentheses one level deep; an optional title.
_INLINE = re.compile(
    r"\[(?P<text>(?:[^\[\]\\]|\\.|\[(?:[^\[\]\\]|\\.)*\])*)\]"
    r"\(\s*(?P<dest><[^<>\n]*>|(?:[^\s()\\]|\\.|\((?:[^\s()\\]|\\.)*\))*)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
_DEFINITION = re.compile(r"^ {0,3}\[(?P<text>[^\]\n]+)\]:[ \t]*(?P<dest><[^<>\n]*>|\S+)", re.MULTILINE)
_HREF = re.compile(
    r"<a\b[^>]*?\bhref\s*=\s*(?P<quote>[\"'])(?P<dest>.*?)(?P=quote)", re.IGNORECASE | re.DOTALL
)


def find_links(document: str, masked: Masked) -> list[Link]:
    """Links are looked for where code spans are still readable — a link's text may hold one —
    and one that starts inside a code span is no link."""
    found: list[Link] = []
    for kind, pattern in (
        (LinkKind.INLINE, _INLINE),
        (LinkKind.DEFINITION, _DEFINITION),
        (LinkKind.HREF, _HREF),
    ):
        for match in pattern.finditer(masked.blocks):
            if any(span.holds(match.start()) for span in masked.spans):
                continue
            at, until = match.span("dest")
            if document[at:until].startswith("<"):
                at, until = at + 1, until - 1
            text = match["text"] if kind is not LinkKind.HREF else ""
            found.append(Link(kind, text, document[at:until], match.start(), match.end(), at, until))
    return sorted(found, key=lambda link: link.start)


def without_links(masked: Masked, links: list[Link]) -> str:
    """The masked text with every link blanked whole, so a handle is left only where it is bare."""
    chars = list(masked.text)
    for link in links:
        for i in range(link.start, link.end):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)
