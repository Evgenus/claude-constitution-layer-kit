"""The texts of this module's own finding, skip, count and dial failures, as functions with
typed parameters; the texts every gate shares live in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (q1_, g1_, f9_, c5_, c12_), so a text can
be cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from const_gate import identity
from const_gate.messages import echoed, escaped
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import DEFAULT_MARKERS, Key

_DEFAULT_MARKERS = ", ".join(f"'{marker}'" for marker in DEFAULT_MARKERS)


def _ns() -> str:
    return identity.current().namespace


# ---------------------------------------------------------------- the finding

_WHY = (
    "a delivered document holds resolved decisions only: a marker left in it defers the question to a"
    " reader who may never see it"
)


def q1_marker(rel: str, line: int, marker: str, text: str) -> Finding:
    return Finding(
        Key.Q1,
        f"{escaped(rel)}:{line}: open question marker '{echoed(marker)}' — {echoed(text)}",
        _WHY,
        "resolve the question in the text; if the decider is absent, replace the marker by a named blocker"
        " — 'blocked: <who> must decide <what>' — and halt that part; a draft whose own convention keeps"
        f" markers until delivery is taken out of {_ns()}.territories by a negated pattern in {DIALS_FILE}",
    )


# ---------------------------------------------------------------- green, skip, count


def g1_covered() -> str:
    """What the green line says the examined document is."""
    return "a covered document"


def g1_skip_not_covered(rel: str) -> str:
    return f"{escaped(rel)} is not covered ({_ns()}.territories)"


def f9_scan_tail(documents: int, markers: int, scanned: int) -> str:
    return f"{documents} document(s) examined for {markers} marker(s), {scanned} Markdown file(s) scanned"


# ---------------------------------------------------------------- this module's dial failures (C5)


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_territories() -> Broken:
    return _c5(
        f"{_ns()}.territories must be a non-empty list of path patterns",
        'write the patterns of the documents to cover, one per line under "- ", or leave the key out to'
        " cover every Markdown file; an empty list would examine nothing in silence",
    )


def c5_markers() -> Broken:
    return _c5(
        f"{_ns()}.markers must be a non-empty list of non-empty one-line texts",
        'write the marker texts to look for, one per line under "- ", in single quotes, or leave the key'
        f" out for the defaults {_DEFAULT_MARKERS}; an empty list would"
        " examine nothing in silence",
    )


# ---------------------------------------------------------------- this module's own C12


def c12_event(name: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"hook input names the event '{echoed(name)}', which this gate is not wired to",
        "wire the gate to PreToolUse on Write|Edit, as the plugin's hooks file does; to check a repository"
        " by hand run it with --scan [<dir>]",
    )
