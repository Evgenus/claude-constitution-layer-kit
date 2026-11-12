"""A document as the gate hands it to Vale. The envelope, the block the shared reader finds, is
blanked, so a title or an id is not prose; an envelope never closed is prose; every Vale comment
outside code is blanked, so nothing in a document can switch a rule off — a departure is declared
in the dials file, never marked in the document — and reported; one inside a fence or a code span
is a mention, which Vale does not honour, and is left as it stands. A code span that holds a run
of three backticks or more is rewritten so that it holds none (`_unfenced`), since Vale reads such a
run as a fence's opening and loses its place in the source after it. Line numbers and columns are
kept: a blanked line is an empty line, a blanked comment is spaces, a rewritten span keeps its
length."""

from __future__ import annotations

import re

from constitution_layer_kit.envelope import envelope_bounds

from .model import Prepared

VALE_COMMENT = re.compile(r"<!--\s*vale\b.*?-->", re.DOTALL)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")
FENCE_RUN = "```"  # the run Vale's own pass takes for a fence's opening, wherever it stands in a line


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

    return Prepared(_unfenced(VALE_COMMENT.sub(blank, blanked)), tuple(comments))


def _unfenced(text: str) -> str:
    """Each code span outside a fence that holds a run of three backticks or more, its delimiters
    included, rewritten at the same length: one backtick on each side, and a space for every other
    backtick. Vale 3.23.0 masks such a run and the rest of its line wherever it stands, as if it opened
    a fence (`prepMarkdown` in its Markdown lint source). The text after it is then not where Vale
    looks for it, so it places each later sentence of the block by guess. A guess can name the wrong
    line, and two guesses on one place are one finding to Vale. Vale reads no word inside a code span,
    so the rewrite moves no count."""
    spans = [(a, b) for a, b in _code_parts(text)[1] if FENCE_RUN in text[a:b]]
    for start, end in spans:
        span = text[start:end]
        width = len(span) - len(span.lstrip("`"))
        inner = span[width : len(span) - width].replace("`", " ")
        pad = " " * (width - 1)
        text = text[:start] + "`" + pad + inner + pad + "`" + text[end:]
    return text


def _code_ranges(text: str) -> list[tuple[int, int]]:
    """The character ranges of fenced blocks and, outside them, of code spans."""
    fences, spans = _code_parts(text)
    return fences + spans


def _code_parts(text: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """The character ranges of fenced blocks, and apart, of the code spans outside them."""
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
    spans = [(start + m.start(), start + m.end()) for start, line in prose for m in CODE_SPAN.finditer(line)]
    return ranges, spans
