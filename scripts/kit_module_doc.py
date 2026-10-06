"""Kit tooling, never shipped in a module: where a kit check reads a section of a module document.

A module document (template `MODULE.md`) puts the anchor `<a id="tN"></a>` alone on the line above
the heading of its section N. `section` reads one section by that anchor, so that a heading's number,
its wording or its place never decides what is read, and it fails loud where a read would otherwise
go quietly wrong: an anchor gone, an anchor twice, or an anchor with text on its line.

Only a line whose stripped form is exactly the anchor counts; the same anchor written inside other
text, as in prose that shows it, is plain text and no anchor. The section ends at the next such
anchor, whatever its number, or at the end of the file. There is no runner of its own: each check
that reads through it proves it in its own `--self-test`.
"""

from __future__ import annotations

import re

ANCHOR = re.compile(r'^<a id="(t\d+)"></a>$')


class DocumentError(Exception):
    """A section of a module document cannot be read; the message says why and how to fix it."""


def section(text: str, anchor: str, path: str) -> list[tuple[int, str]]:
    """The lines (1-based number, text) after the line of `anchor` up to, not including, the next
    section anchor of any number, or to the end of the text; `path` names the document in a message."""
    lines = text.splitlines()
    stands: dict[str, list[int]] = {}
    for number, line in enumerate(lines, start=1):
        if (found := ANCHOR.match(line.strip())) is not None:
            stands.setdefault(found[1], []).append(number)
    if anchor not in stands:
        raise DocumentError(
            f'{path} has no anchor <a id="{anchor}"></a> on a line of its own'
            " — fix: restore the template's anchor, alone on its line"
        )
    for name, numbers in stands.items():
        if len(numbers) > 1:
            raise DocumentError(
                f'{path} holds the anchor <a id="{name}"></a> twice, lines {numbers[0]} and {numbers[1]}'
                " — fix: keep the one before its section's heading"
            )
    start = stands[anchor][0]
    later = sorted(number for numbers in stands.values() for number in numbers if number > start)
    end = later[0] if later else len(lines) + 1
    return [(number, lines[number - 1]) for number in range(start + 1, end)]
