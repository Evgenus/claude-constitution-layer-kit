"""The links of a document, with the positions a repair needs.

Found by regular expressions over masked text, not by a Markdown parser: no parser surveyed
gives the source position of an inline link, and a repair must rewrite a destination where
it stands, leaving every other character of the document as it was.
"""

from __future__ import annotations

import re

from .masking import Masked, Span, holder
from .model import Link, LinkKind

# text: no unescaped bracket but balanced pairs one level deep; destination: <in angle brackets>
# or a run without spaces, balanced parentheses one level deep; an optional title.
# Every run is bounded: an opener that never closes must not be searched to the end of the file
# each time. A footnote — [^1] — is no link and its definition names no destination.
_TEXT = r"(?:[^\[\]\\]|\\.|\[(?:[^\[\]\\]|\\.){0,500}\])"
_INLINE = re.compile(
    rf"\[(?!\^)(?P<text>{_TEXT}{{0,1000}})\]"
    r"\(\s*(?P<dest><[^<>\n]{0,2000}>|(?:[^\s()\\]|\\.|\((?:[^\s()\\]|\\.){0,500}\)){0,2000})"
    r"(?:\s+(?:\"[^\"]{0,1000}\"|'[^']{0,1000}'))?\s*\)"
)
_DEFINITION = re.compile(
    r"^ {0,3}\[(?!\^)(?P<text>[^\]\n]{1,1000})\]:[ \t]*(?P<dest><[^<>\n]{0,2000}>|\S{1,2000})", re.MULTILINE
)
# [text][label], [label][] and [label] — told from an inline link by what follows the bracket
_USAGE = re.compile(rf"\[(?!\^)(?P<text>{_TEXT}{{1,1000}})\](?:\[(?P<label>[^\[\]\n]{{0,1000}})\])?(?![\[(])")
_HREF = re.compile(
    r"<a\b[^<>]{0,2000}?\bhref\s*=\s*(?P<quote>[\"'])(?P<dest>[^\"'<>\n]{0,2000})(?P=quote)", re.IGNORECASE
)


def find_links(document: str, masked: Masked) -> list[Link]:
    """Links are looked for where code spans are still readable — a link's text may hold one —
    and one that starts inside a code span is no link. A usage of a reference definition is a
    link too: it opens what its definition names, and has no destination of its own to rewrite."""
    found: list[Link] = []
    for kind, pattern in (
        (LinkKind.INLINE, _INLINE),
        (LinkKind.DEFINITION, _DEFINITION),
        (LinkKind.HREF, _HREF),
    ):
        for match in pattern.finditer(masked.blocks):
            if holder(masked.spans, match.start()) is not None:
                continue
            at, until = match.span("dest")
            if document[at:until].startswith("<"):
                at, until = at + 1, until - 1
            text = match["text"] if kind is not LinkKind.HREF else ""
            found.append(Link(kind, text, document[at:until], match.start(), match.end(), at, until))
    defined = {_label(link.text): link.destination for link in found if link.kind is LinkKind.DEFINITION}
    taken = sorted(Span(link.start, link.end) for link in found)
    for match in _USAGE.finditer(masked.blocks) if defined else ():
        destination = defined.get(_label(match["label"] or match["text"]))
        inside = holder(masked.spans, match.start()) or holder(taken, match.start())
        if destination is not None and inside is None:
            found.append(Link(LinkKind.USAGE, match["text"], destination, match.start(), match.end(), 0, 0))
    return sorted(found, key=lambda link: link.start)


def _label(text: str) -> str:
    """Labels match without regard to case, and with runs of white space as one space."""
    return " ".join(text.split()).casefold()


def without_links(masked: Masked, links: list[Link]) -> str:
    """The masked text with every link blanked whole, so a handle is left only where it is bare."""
    chars = list(masked.text)
    for link in links:
        for i in range(link.start, link.end):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)
