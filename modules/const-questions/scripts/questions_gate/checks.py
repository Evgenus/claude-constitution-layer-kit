"""The check: which lines of a document carry a marker, outside code."""

from __future__ import annotations

import re
from collections.abc import Sequence

from .model import Hit

_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_SPAN = re.compile(r"(`+)(?:.+?)\1")


def examine(text: str, markers: Sequence[str]) -> list[Hit]:
    """One hit per line at most: the marker that stands first on it, with the line from there on.
    A fenced block, from its opener to its closer or to the end of the text, and a code span on a
    line are not read: a marker there is a quotation. The match is case-sensitive, and a marker
    that begins or ends with a word character must stand at a word boundary on that side."""
    patterns = [_pattern(marker) for marker in markers]
    hits: list[Hit] = []
    fence: str | None = None
    # a line ends at "\n" alone, as the other gates count: a form feed or U+2028 stays inside its line
    for number, line in enumerate(text.split("\n"), start=1):
        opener = _FENCE.match(line)
        if fence is None and opener and opener.group(1)[0] == "`" and "`" in opener.group(2):
            opener = None  # a backtick fence's info string holds no backtick: this is a code span line
        if fence is None and opener:
            fence = opener.group(1)
            continue
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence):
                fence = None
            continue
        readable = _SPAN.sub(lambda m: " " * len(m.group(0)), line)
        first: tuple[int, str] | None = None
        for marker, pattern in zip(markers, patterns, strict=True):
            found = pattern.search(readable)
            if found and (first is None or found.start() < first[0]):
                first = (found.start(), marker)
        if first is not None:
            hits.append(Hit(number, first[1], line[first[0] :].rstrip()))
    return hits


def _pattern(marker: str) -> re.Pattern[str]:
    before = r"(?<!\w)" if re.match(r"\w", marker) else ""
    after = r"(?!\w)" if re.search(r"\w$", marker) else ""
    return re.compile(before + re.escape(marker) + after)
