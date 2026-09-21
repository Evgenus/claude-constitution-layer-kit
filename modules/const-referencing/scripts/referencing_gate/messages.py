"""The texts of this module's own findings, skips and dial failures, as functions with typed
parameters; the texts every gate shares live in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (r1_, g1_, c5_, ...), so a text can be
cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from const_gate import identity
from const_gate.messages import shown
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import Key

_LANE = "{pattern: <regular expression>, names: <what the form cites>, fix: <the link form to write>}"


def _ns() -> str:
    return identity.current().namespace


# ---------------------------------------------------------------- findings: the forms of a reference

_WHY_BARE = (
    "a bare handle resolves only inside its home document: elsewhere no reader can follow it, no"
    " check can test it, and a move cannot find it"
)


def r1_bare_form(rel: str, line: int, match: str, names: str, fix: str) -> Finding:
    """`names` and `fix` are the project's words, from its lane; the reason is never theirs."""
    return Finding(
        Key.R1,
        f"{rel}:{line}: '{shown(match)}' cites {names} by a bare handle",
        _WHY_BARE,
        f"write it as a link: {fix}",
    )


def r2_bare_id(rel: str, line: int, doc_id: str, owner: str, path_to_owner: str) -> Finding:
    return Finding(
        Key.R2,
        f"{rel}:{line}: document id '{doc_id}' stands in backticks and is no link",
        "an id names a document that can move: only a link lets a reader reach it and lets a move repair it",
        f"write [{doc_id}]({path_to_owner}) — the path from this document to {owner}",
    )


def r3_id_link_astray(
    rel: str, line: int, doc_id: str, target: str, owner: str, path_to_owner: str
) -> Finding:
    return Finding(
        Key.R3,
        f"{rel}:{line}: the link's text is document id '{doc_id}', and its target {shown(target)} is not"
        f" that document ({owner})",
        "a link that shows one document's id and opens another misleads every reader who trusts the text",
        f"point it at {path_to_owner}",
    )


def r4_one_machine(rel: str, line: int, match: str) -> Finding:
    return Finding(
        Key.R4,
        f"{rel}:{line}: '{shown(match)}' is a path on one machine",
        "it resolves on the machine it was written on and nowhere else",
        "link a file of this repository by its relative path, or cite the public address the fact was"
        " verified at, or drop the reference",
    )


# ---------------------------------------------------------------- green, skip and count lines


def g1_covered() -> str:
    return "a covered document"


def g1_skip_not_covered(rel: str) -> str:
    return f"{rel} is not covered ({_ns()}.territories)"


def f9_scan_tail(documents: int, links: int, scanned: int, lanes: int) -> str:
    return (
        f"{documents} document(s) and {links} link(s) examined, {scanned} Markdown file(s) scanned,"
        f" {lanes} lane(s)"
    )


# ---------------------------------------------------------------- this module's dial failures


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_territories() -> Broken:
    return _c5(
        f"{_ns()}.territories must be a non-empty list of path patterns",
        f"write it as {_ns()}: {{territories: ['*.md']}}, or remove the key:"
        " every Markdown file is then covered",
    )


def c5_switch(dial: str) -> Broken:
    return _c5(
        f"{_ns()}.{dial} must be refuse or allow",
        f"write {dial}: allow, or remove the key: refuse is the default",
    )


def c5_lanes_not_a_list() -> Broken:
    return _c5(
        f"{_ns()}.lanes must be a list of lanes",
        f"write it as {_ns()}: {{lanes: [{_LANE}]}}, or remove the key",
    )


def c5_lane(position: int, what: str) -> Broken:
    return _c5(
        f"entry {position} of {_ns()}.lanes {what}",
        f"write the entry as {_LANE}; home: [<patterns>] is optional",
    )


def lane_not_a_mapping() -> str:
    return "is not a mapping of pattern, names, fix and home"


def lane_unknown_key(key: str) -> str:
    return f"carries the key '{shown(key)}'; a lane holds pattern, names, fix and home, and nothing else"


def lane_needs(field: str) -> str:
    return f"needs {field}: a non-empty string"


def lane_home() -> str:
    return "has a home that is not a list of path patterns"


def lane_pattern(error: str) -> str:
    return (
        f"has a pattern that is no regular expression ({shown(error)}) — in YAML write it in single"
        " quotes, where a backslash stands for itself"
    )
