"""The regions of a Markdown document no check reads and no repair rewrites: the YAML block
that opens the file, fenced and indented code, HTML comments, code spans.

Masking keeps every offset: a masked character becomes a space and a line break stays, so a
position found in the masked text is the same position in the document. It is line-based and
knows no more Markdown than that — an unclosed fence masks to the end of the file, as it
renders.
"""

from __future__ import annotations

import bisect
import re
from collections.abc import Sequence
from dataclasses import dataclass

from const_gate.envelope import Bounds, envelope_bounds

_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
_FENCE_IN_LIST = re.compile(r"[ \t]*(`{3,}|~{3,})")  # a list item's content is indented with it
_TAB = 4  # columns a tab counts for where indentation is compared
_LIST_ITEM = re.compile(r" {0,3}(?:[-*+]|\d{1,9}[.)])(?: |$)")
_INDENTED = re.compile(r"(?: {4}|\t)")
_TICKS = re.compile(r"`+")
_BLANK_LINE = re.compile(r"\n[ \t]*\n")


@dataclass(frozen=True, slots=True, order=True)
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
    bounds = envelope_bounds(document)  # the one reading of where the YAML block stands
    regions = _block_regions(document, bounds)
    body = _blank(document, regions[:1] if bounds is not None else [])  # then the block is the first region
    blocks = _blank(document, regions)
    blocks = _blank(blocks, _comments(blocks))
    spans = tuple(_code_spans(blocks))
    return Masked(body, blocks, _blank(blocks, spans), spans)


def holder(spans: Sequence[Span], position: int) -> Span | None:
    """The span that holds the position, of spans in reading order that do not overlap."""
    index = bisect.bisect_right(spans, position, key=lambda span: span.start) - 1
    return spans[index] if index >= 0 and spans[index].holds(position) else None


def _comments(text: str) -> list[Span]:
    """HTML comments, found by plain search: an opener that is never closed costs one look to the
    end of the text, not one per opener."""
    found: list[Span] = []
    start = text.find("<!--")
    while start != -1:
        end = text.find("-->", start + 4)
        if end == -1:
            break
        found.append(Span(start, end + 3))
        start = text.find("<!--", end + 3)
    return found


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


def _block_regions(document: str, bounds: Bounds | None) -> list[Span]:
    """The block-level regions in reading order. Where the YAML block stands is the helper's `bounds`: a
    block that opens the file is the first region, from offset 0 to the end of its closing line. A block
    no line closes is this module's own rule, not the helper's: it masks to the end of the file. The
    rest — fences, indented code — is read line by line here; the block's end falls on a line break
    that `splitlines` also breaks at, so the loop resumes at the line after the block."""
    regions: list[Span] = []
    lines = document.splitlines(keepends=True)
    offset = 0
    fence: str | None = None  # the run that opened the fence being read
    fence_depth = 0  # the columns its opener was indented by
    block_start = 0
    in_envelope = bounds is not None
    in_list = False  # the last unindented line was a list item: indented text continues it
    after_blank = True
    in_indented = False
    for line in lines:
        end = offset + len(line)
        bare = line.rstrip("\r\n")
        if in_envelope:
            if bounds is not None and bounds.end is not None and end >= bounds.end:
                regions.append(Span(0, bounds.end))
                in_envelope = False
        elif fence is not None:
            closing = _FENCE_IN_LIST.match(bare)
            if (
                closing
                and closing[1][0] == fence[0]
                and len(closing[1]) >= len(fence)
                and not bare.strip(" \t`~")
                # at its opener's depth, give or take what a fence may be indented by: a deeper
                # fence inside this one is shown, not closed
                and _depth(bare) <= (3 if fence_depth <= 3 else fence_depth + 3)
            ):
                regions.append(Span(block_start, end))
                fence = None
        elif opening := (_FENCE_IN_LIST if in_list else _FENCE).match(bare):
            fence, fence_depth, block_start, in_indented = opening[1], _depth(bare), offset, False
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


def _depth(line: str) -> int:
    indent = line[: len(line) - len(line.lstrip(" \t"))]
    return len(indent.expandtabs(_TAB))


def _code_spans(text: str) -> list[Span]:
    """A run of n ticks opens a span that the next run of exactly n ticks closes, inside one
    paragraph. Where paragraphs end is found once, not once per tick."""
    spans: list[Span] = []
    ends = [match.start() for match in _BLANK_LINE.finditer(text)]
    position = 0
    while opening := _TICKS.search(text, position):
        following = bisect.bisect_left(ends, opening.end())
        limit = ends[following] if following < len(ends) else len(text)
        position = opening.end()
        for closing in _TICKS.finditer(text, opening.end(), limit):
            if len(closing[0]) == len(opening[0]):
                spans.append(Span(opening.start(), closing.end()))
                position = closing.end()
                break
    return spans
