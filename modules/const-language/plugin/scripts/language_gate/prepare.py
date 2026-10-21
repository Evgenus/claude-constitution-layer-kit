"""A document as the gate hands it to Vale. The envelope, the block the shared reader finds, is
blanked, so a title or an id is not prose; an envelope never closed is prose; every Vale comment
outside code is blanked, so nothing in a document can switch a rule off — a departure is declared
in the dials file, never marked in the document — and reported; one inside a fence or a code span
is a mention, which Vale does not honour, and is left as it stands. Line numbers are kept: a
blanked line is an empty line, a blanked comment is spaces."""

from __future__ import annotations

import re

from constitution_layer_kit.envelope import envelope_bounds

from .model import Prepared

VALE_COMMENT = re.compile(r"<!--\s*vale\b.*?-->", re.DOTALL)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")


def prepare(text: str) -> Prepared:
    bounds = envelope_bounds(text)
    blanked = text
    if bounds is not None and bounds.end is not None:
        # exactly the shared reader's block: only its `\n` stay, one per line Vale counts; whatever else
        # stood there (a byte-order mark, a `\r`) goes, so no line break is left for Vale but its own
        blanked = "\n" * text.count("\n", 0, bounds.end) + text[bounds.end :]
    code = _code_ranges(blanked)
    comments: list[tuple[int, str]] = []

    def blank(match: re.Match[str]) -> str:
        if any(start <= match.start() < end for start, end in code):
            return match.group(0)  # a mention: Vale does not honour it, and a span of spaces would misread
        comments.append((blanked.count("\n", 0, match.start()) + 1, match.group(0)))
        return "".join("\n" if c == "\n" else " " for c in match.group(0))

    return Prepared(VALE_COMMENT.sub(blank, blanked), tuple(comments))


def _code_ranges(text: str) -> list[tuple[int, int]]:
    """The character ranges of fenced blocks and, outside them, of code spans."""
    ranges: list[tuple[int, int]] = []
    offset = 0
    fence: str | None = None
    fence_start = 0
    prose: list[tuple[int, str]] = []
    for line in text.split("\n"):
        opener = FENCE.match(line)
        if fence is None and opener:
            fence, fence_start = opener.group(1), offset
        elif (
            fence is not None
            and opener
            and opener.group(1)[0] == fence[0]
            and len(opener.group(1)) >= len(fence)
        ):
            ranges.append((fence_start, offset + len(line)))
            fence = None
        elif fence is None:
            prose.append((offset, line))
        offset += len(line) + 1
    if fence is not None:
        ranges.append((fence_start, len(text)))
    for start, line in prose:
        for span in CODE_SPAN.finditer(line):
            ranges.append((start + span.start(), start + span.end()))
    return ranges
