"""The regions of a Markdown document no check reads and no repair rewrites: the YAML block
that opens the file, fenced and indented code, HTML comments, code spans.

Masking keeps every offset: a masked character becomes a space and a line break stays, so a
position found in the masked text is the same position in the document. It is line-based and
knows no more Markdown than that — an unclosed fence masks to the end of the file, as it
renders.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
_LIST_ITEM = re.compile(r" {0,3}(?:[-*+]|\d{1,9}[.)])(?: |$)")
_INDENTED = re.compile(r"(?: {4}|\t)")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TICKS = re.compile(r"`+")
_BLANK_LINE = re.compile(r"\n[ \t]*\n")


@dataclass(frozen=True, slots=True)
class Span:
    start: int
    end: int

    def holds(self, position: int) -> bool:
        return self.start <= position < self.end


@dataclass(frozen=True, slots=True)
class Masked:
    """`body`: the text with only the YAML block that opens the file blanked — what a check
    reads that judges code too. `blocks`: the block-level regions blanked as well, code spans
    still readable. `text`: code spans blanked too. `spans`: where the code spans are, ticks
    included."""

    body: str
    blocks: str
    text: str
    spans: tuple[Span, ...]


def mask(document: str) -> Masked:
    regions = _block_regions(document)
    opens_with_envelope = document.lstrip("\ufeff").startswith("---")
    body = _blank(document, regions[:1] if opens_with_envelope and regions and regions[0].start == 0 else [])
    blocks = _blank(document, regions)
    blocks = _blank(blocks, [Span(m.start(), m.end()) for m in _COMMENT.finditer(blocks)])
    spans = tuple(_code_spans(blocks))
    return Masked(body, blocks, _blank(blocks, spans), spans)


def content(document: str, span: Span) -> str:
    """What a code span shows: the text between its ticks, without the padding spaces."""
    ticks = len(document[span.start : span.end]) - len(document[span.start : span.end].lstrip("`"))
    return document[span.start + ticks : span.end - ticks].strip()


def line_of(document: str, position: int) -> int:
    return document.count("\n", 0, position) + 1


def _blank(text: str, regions: list[Span] | tuple[Span, ...]) -> str:
    chars = list(text)
    for region in regions:
        for i in range(region.start, region.end):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def _block_regions(document: str) -> list[Span]:
    regions: list[Span] = []
    lines = document.splitlines(keepends=True)
    offset = 0
    fence: str | None = None  # the run that opened the fence being read
    block_start = 0
    in_envelope = bool(lines) and lines[0].lstrip("\ufeff").rstrip() == "---"  # a byte order mark may lead
    in_list = False  # the last unindented line was a list item: indented text continues it
    after_blank = True
    in_indented = False
    for number, line in enumerate(lines):
        end = offset + len(line)
        bare = line.rstrip("\r\n")
        if in_envelope:
            if number > 0 and bare.rstrip() == "---":
                regions.append(Span(0, end))
                in_envelope = False
        elif fence is not None:
            closing = _FENCE.match(bare)
            if (
                closing
                and closing[1][0] == fence[0]
                and len(closing[1]) >= len(fence)
                and not bare.strip(" `~")
            ):
                regions.append(Span(block_start, end))
                fence = None
        elif opening := _FENCE.match(bare):
            fence, block_start, in_indented = opening[1], offset, False
        elif not bare.strip():
            after_blank = True
            offset = end
            continue
        elif _INDENTED.match(bare) and not in_list and (after_blank or in_indented):
            regions.append(Span(offset, end))
            in_indented = True
        else:
            in_indented = False
            if not _INDENTED.match(bare):
                in_list = bool(_LIST_ITEM.match(bare))
        after_blank = False
        offset = end
    if in_envelope or fence is not None:  # never closed: it renders as one block to the end
        regions.append(Span(0 if in_envelope else block_start, len(document)))
    return regions


def _code_spans(text: str) -> list[Span]:
    """A run of n ticks opens a span that the next run of exactly n ticks closes, inside one
    paragraph."""
    spans: list[Span] = []
    position = 0
    while opening := _TICKS.search(text, position):
        paragraph_end = _BLANK_LINE.search(text, opening.end())
        limit = paragraph_end.start() if paragraph_end else len(text)
        position = opening.end()
        for closing in _TICKS.finditer(text, opening.end(), limit):
            if len(closing[0]) == len(opening[0]):
                spans.append(Span(opening.start(), closing.end()))
                position = closing.end()
                break
    return spans
