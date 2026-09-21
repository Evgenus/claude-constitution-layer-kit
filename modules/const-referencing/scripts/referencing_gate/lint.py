"""The forms a reference may not take, judged on one document's text: a project's bare forms
(its lanes), a governed id in backticks, an id link that opens another document, a path on
one machine. Each check is a function of typed inputs and reads no file."""

from __future__ import annotations

import posixpath
import re
from collections.abc import Sequence
from urllib.parse import unquote

from const_gate.model import Finding

from . import messages
from .links import find_links, without_links
from .masking import Masked, content, line_of, mask
from .model import Ids, Lane, Link, LinkKind

# A home directory is an operating system's fact, not a project's.
_ONE_MACHINE = re.compile(
    r"file:/+[^\s)>\"']*|(?<![\w.:/-])(?:/Users/|/home/)[^\s)>\"'`]+|\b[A-Za-z]:\\Users\\[^\s)>\"'`]+"
)
_CLOSES_A_SENTENCE = ".,;:!?"  # punctuation after a path is the sentence's, not the path's
_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


def examine(
    rel: str, document: str, own_id: str | None, ids: Ids, lanes: Sequence[Lane], bare_ids: bool
) -> tuple[list[Finding], int]:
    """The findings of one document, by position, and the number of links it holds. `lanes` are
    those not at home in this document; `bare_ids` says whether an id in backticks is judged."""
    masked = mask(document)
    links = find_links(document, masked)
    found: list[tuple[int, Finding]] = [
        *_bare_forms(rel, document, without_links(masked, links), lanes),
        *(_bare_ids(rel, document, masked, links, own_id, ids) if bare_ids else []),
        *_id_links_astray(rel, document, links, ids),
        *_one_machine(rel, document, masked),
    ]
    return [finding for _, finding in sorted(found, key=lambda pair: pair[0])], len(links)


def target_of(rel: str, destination: str) -> str | None:
    """The repository-relative path a destination names, from the document at `rel`; None for
    an address with a scheme. A destination that is only a fragment names the document itself."""
    if _SCHEME.match(destination):
        return None
    path = unquote(destination.split("#", 1)[0].split("?", 1)[0])
    if not path:
        return rel
    if path.startswith("/"):
        return posixpath.normpath(path.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))


def path_between(rel: str, target: str) -> str:
    """The destination to write in the document at `rel` to reach `target`."""
    return posixpath.relpath(target, posixpath.dirname(rel) or ".")


def _bare_forms(rel: str, document: str, bare: str, lanes: Sequence[Lane]) -> list[tuple[int, Finding]]:
    return [
        (m.start(), messages.r1_bare_form(rel, line_of(document, m.start()), m[0], lane.names, lane.fix))
        for lane in lanes
        for m in lane.pattern.finditer(bare)
        if m[0]
    ]


def _bare_ids(
    rel: str, document: str, masked: Masked, links: Sequence[Link], own_id: str | None, ids: Ids
) -> list[tuple[int, Finding]]:
    found: list[tuple[int, Finding]] = []
    for span in masked.spans:
        doc_id = content(document, span)
        owners = ids.owners_of(doc_id)
        if not owners or doc_id == own_id or any(link.start <= span.start < link.end for link in links):
            continue
        line = line_of(document, span.start)
        found.append(
            (span.start, messages.r2_bare_id(rel, line, doc_id, owners[0], path_between(rel, owners[0])))
        )
    return found


def _id_links_astray(rel: str, document: str, links: Sequence[Link], ids: Ids) -> list[tuple[int, Finding]]:
    found: list[tuple[int, Finding]] = []
    for link in links:
        if link.kind is not LinkKind.INLINE:
            continue
        doc_id = link.text.strip().strip("`").strip()
        owners = ids.owners_of(doc_id)
        target = target_of(rel, link.destination)
        if not owners or target is None or target in owners:
            continue
        line = line_of(document, link.start)
        found.append(
            (
                link.start,
                messages.r3_id_link_astray(
                    rel, line, doc_id, link.destination, owners[0], path_between(rel, owners[0])
                ),
            )
        )
    return found


def _one_machine(rel: str, document: str, masked: Masked) -> list[tuple[int, Finding]]:
    return [
        (
            m.start(),
            messages.r4_one_machine(rel, line_of(document, m.start()), m[0].rstrip(_CLOSES_A_SENTENCE)),
        )
        for m in _ONE_MACHINE.finditer(masked.body)  # code too: a path leaks a machine however it is set
    ]
