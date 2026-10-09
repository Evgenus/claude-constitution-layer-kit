"""The check of the whole tree: every link of a covered document resolves, and where it cites a
place inside a covered document, it cites an anchor somebody wrote there.

The link checker answers whether a link resolves. Which kind of anchor resolved it, it
cannot say — it accepts a heading's generated name, a `{#key}` after a heading, and any
case — so that half is read here, from the documents themselves."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from urllib.parse import unquote

from const_gate.model import Finding

from . import lychee, messages
from .anchors import explicit_anchors
from .links import find_links
from .lint import target_of
from .lychee import Break, BreakKind
from .masking import Masked, line_of, mask
from .model import Link, LinkKind, Switch


def examine(
    root: Path,
    texts: Mapping[str, str],
    heading_anchors: Switch,
    budget: lychee.Budget | None,
    binary: str | None,
    about: str | None = None,
) -> tuple[dict[str, list[tuple[int, Finding]]], int]:
    """The findings of each covered document, in reading order, and the links examined. `texts`
    holds the covered documents as they stand on disk. With `about`, only the findings that involve
    that document: its own links, and other documents' links into it. `budget` is the check's one
    deadline, begun by the caller before it read the texts, None for no limit: the clock is read after
    each document is masked, and the checker's run is given what is left. `binary` is the checker
    the caller found and probed before it began the budget, None to find and probe it here (the scan)."""
    masked: dict[str, Masked] = {}
    links: dict[str, list[Link]] = {}
    anchors: dict[str, frozenset[str]] = {}
    for rel, text in texts.items():
        masked[rel] = mask(text)  # once per document: it is the costly step
        links[rel] = find_links(text, masked[rel])
        anchors[rel] = explicit_anchors(masked[rel])
        if budget is not None:
            budget.check()
    found: dict[str, list[tuple[int, Finding]]] = {rel: [] for rel in texts}
    broken: set[tuple[str, str, str | None]] = set()
    for b in lychee.find_breaks(root, sorted(texts), budget, binary):
        broken.add((b.source, b.target, b.fragment))
        if about is not None and about not in (b.source, b.target):
            continue
        found.setdefault(b.source, []).append((b.line, _of_break(b, links.get(b.source, []), texts)))
    for rel, text in texts.items():
        for link in links[rel]:
            if link.kind is LinkKind.USAGE:
                continue  # its definition is the link that is resolved
            target, fragment = target_of(rel, link.destination), _fragment(link)
            if target is None or not fragment or target not in anchors or fragment in anchors[target]:
                continue
            if (rel, target, fragment) in broken:
                continue  # already reported as it is: no such anchor of any kind
            if about is not None and about not in (rel, target):
                continue
            line = line_of(text, link.start)
            other_case = next((a for a in sorted(anchors[target]) if a.lower() == fragment.lower()), None)
            if other_case is not None:
                found[rel].append(
                    (line, messages.r6_no_anchor(rel, line, link.destination, fragment, target, other_case))
                )
            elif heading_anchors is Switch.REFUSE:
                found[rel].append((line, messages.r7_heading_anchor(rel, line, link.destination, target)))
    # two links alike on one line make one finding: said twice it teaches nothing more
    in_order = {
        rel: sorted(dict.fromkeys(pairs), key=lambda pair: pair[0]) for rel, pairs in found.items() if pairs
    }
    return in_order, sum(len(found_links) for found_links in links.values())


def _fragment(link: Link) -> str:
    return unquote(link.destination.split("#", 1)[1]) if "#" in link.destination else ""


def _of_break(b: Break, links: list[Link], texts: Mapping[str, str]) -> Finding:
    """The finding names the destination as the document wrote it, where the link can be told."""
    text = texts.get(b.source, "")
    written = next(
        (
            link.destination
            for link in links
            if line_of(text, link.start) <= b.line <= line_of(text, link.end)
            and target_of(b.source, link.destination) == b.target
            and (_fragment(link) or None) == b.fragment
        ),
        b.target + (f"#{b.fragment}" if b.fragment else ""),
    )
    match b.kind:
        case BreakKind.NO_FILE:
            return messages.r5_no_target(b.source, b.line, written)
        case BreakKind.NO_FRAGMENT:
            return messages.r6_no_anchor(b.source, b.line, written, b.fragment or "", b.target, None)
        case BreakKind.OTHER:
            return messages.r5_unresolved(b.source, b.line, written, b.words)
