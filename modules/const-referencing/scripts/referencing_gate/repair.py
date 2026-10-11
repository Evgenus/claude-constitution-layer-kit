"""The rewrites of a move, as functions of text: a destination is replaced where it stands,
and every other character of the document stays as it was. Links inside the regions masking
blanks — code, comments, the YAML block — are no links here, so they are never rewritten."""

from __future__ import annotations

import posixpath
import re
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import quote

from .links import find_links
from .lint import path_between, target_of
from .masking import Span, holder, line_of, mask
from .model import Ids, Link, LinkKind


@dataclass(frozen=True, slots=True)
class Rewritten:
    text: str
    links: int


@dataclass(frozen=True, slots=True)
class Mentioned:
    line: int
    text: str


def inbound(rel: str, document: str, old: str, new: str) -> Rewritten:
    """Every link of the document at `rel` that opens `old` opens `new` instead."""
    return _rewrite(rel, document, lambda link: new if target_of(rel, link.destination) == old else None)


def own_links(old: str, new: str, document: str) -> Rewritten:
    """The links of the moved document itself, written when it lay at `old`, reach from `new`
    what they reached before; a link to the document by its old name reaches its new one."""

    def aim(link: Link) -> str | None:
        if not link.destination.split("#", 1)[0].split("?", 1)[0]:
            return None  # a fragment alone stays inside the document, wherever it lies
        target = target_of(old, link.destination)
        return new if target == old else target

    return _rewrite(new, document, aim)


def id_links(rel: str, document: str, ids: Ids) -> Rewritten:
    """A link whose text is a document's id opens the document that carries the id — where
    exactly one does. This needs no knowledge of what moved: the envelope says where it is."""

    def aim(link: Link) -> str | None:
        owners = ids.owners_of(link.text.strip().strip("`").strip()) if link.kind is LinkKind.INLINE else ()
        return owners[0] if len(owners) == 1 else None

    return _rewrite(rel, document, aim)


def mentions(document: str, names: tuple[str, ...]) -> list[Mentioned]:
    """Where the document names the old place outside a link's destination — in prose, in code.
    Nothing here is rewritten: a sentence may mean the old place on purpose."""
    links = find_links(document, mask(document))
    spans = sorted(Span(link.at, link.until) for link in links if link.kind is not LinkKind.USAGE)
    found: dict[int, Mentioned] = {}
    lines = document.split("\n")  # a line ends at "\n" alone, as `line_of` counts
    for name in names:  # the name itself: `a.md` is not named by `data.md`
        for match in re.finditer(rf"(?<![\w./-]){re.escape(name)}(?![\w-])", document):
            if holder(spans, match.start()) is None:
                line = line_of(document, match.start())
                found.setdefault(line, Mentioned(line, lines[line - 1].strip()))
    return [found[line] for line in sorted(found)]


def _rewrite(rel: str, document: str, aim: Callable[[Link], str | None]) -> Rewritten:
    """`aim` names the repository-relative path a link should open, or None to leave it. The
    destination keeps its form: what follows the path — a fragment, a query — a leading slash,
    and angle brackets, inside which a space needs no escaping."""
    text, count = document, 0
    for link in reversed(find_links(document, mask(document))):
        wanted = aim(link) if link.kind is not LinkKind.USAGE else None  # its definition is the link
        if wanted is None or target_of(rel, link.destination) in (None, wanted):
            continue
        path_end = min(
            (i for i in (link.destination.find("#"), link.destination.find("?")) if i != -1),
            default=len(link.destination),
        )
        path = "/" + wanted if link.destination.startswith("/") else path_between(rel, wanted)
        in_brackets = document[link.at - 1 : link.at] == "<"
        written = (path if in_brackets else quote(path, safe="/@:+,=~!$&'*;")) + link.destination[path_end:]
        text = text[: link.at] + written + text[link.until :]
        count += 1
    return Rewritten(text, count)


def names_of(rel: str, old: str) -> tuple[str, ...]:
    """How the document at `rel` may name the old place: by its repository path, and by the
    path from the document itself."""
    return tuple(dict.fromkeys((old, posixpath.relpath(old, posixpath.dirname(rel) or "."))))
