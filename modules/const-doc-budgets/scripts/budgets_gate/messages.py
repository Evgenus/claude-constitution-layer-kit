"""The texts of this module's own finding, notes, count lines, skip reasons, report lines and
configuration failures, as functions with typed parameters; the texts every gate shares live in the
shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists (one
clause), and the exact fix; a configuration failure is one self-sufficient line. Every function
name starts with the stable key of its text (b1, n2 to n4, f9, g1, h1, s1, c5, c12), so a text can
be cited, reviewed and asserted by key. A reader must be able to act on a message without holding
any other document: no text here cites one.
"""

from __future__ import annotations

import datetime
from collections.abc import Sequence

from const_gate import identity
from const_gate.messages import shown
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import MARGIN, ROUND_TO, WINDOW_DAYS, Ceiling, Departure, Key, Level


def _ns() -> str:
    return identity.current().namespace


def one_line(value: str) -> str:
    """A value echoed in a message stays on one line: its line breaks are shown escaped."""
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")


def _over(rel: str, length: int, ceiling: Ceiling) -> str:
    return (
        f"{rel}: {length:,} characters, over the ceiling '{ceiling.name}' of {ceiling.max:,}"
        f" by {length - ceiling.max:,}"
    )


# ---------------------------------------------------------------- the finding


def b1_over(rel: str, length: int, ceiling: Ceiling) -> Finding:
    return Finding(
        Key.B1,
        _over(rel, length, ceiling),
        "a document longer than its kind was observed to need makes every reader, and every session that"
        " loads it, pay for text the kind did not need",
        f"shorten it by {length - ceiling.max:,} characters or more, or split it into documents that"
        f" each stay at or under {ceiling.max:,}; the ceiling for this repository is the entry"
        f" '{ceiling.name}' of {_ns()}.ceilings in {DIALS_FILE}; for a document that must stand as"
        f" written, declare the departure with its reason: add to {_ns()}.departures an entry"
        f" {{paths: [<the file, or a pattern of the documents that stand>], allow: [{ceiling.name}],"
        " reason: <why they stand, in one line>}",
    )


# ---------------------------------------------------------------- notes


def n2_warning(rel: str, length: int, ceiling: Ceiling) -> str:
    """An excess over a ceiling at level warning: reported, never a finding."""
    return (
        f"note: {_over(rel, length, ceiling)} — reported, not red, while the ceiling's level is"
        f" {Level.WARNING.value}; shorten it or split it before the ceiling blocks"
    )


def n3_stale_departure(index: int, departure: Departure) -> str:
    return (
        f"note: {_ns()}.departures entry {index} ({', '.join(departure.paths)}) matches no measured"
        " document; the documents it allowed were deleted or moved, or the pattern is wrong"
    )


def n4_ceiling(ceiling: Ceiling, held: int, lifted: int, longest: tuple[str, int] | None) -> str:
    """The data of one ceiling, on every scan: how many documents it holds, how many a departure
    lifts, and how close the longest of the others is."""
    head = (
        f"note: ceiling '{ceiling.name}' — {ceiling.max:,} characters, {ceiling.level.value}, window"
        f" {ceiling.window.start.isoformat()} to {ceiling.window.end.isoformat()}"
    )
    if held == 0:
        return f"{head}: no document"
    if longest is None:
        return f"{head}: {held} document(s), all lifted by a departure"
    rel, length = longest
    margin = (
        f"{ceiling.max - length:,} to spare" if length <= ceiling.max else f"over by {length - ceiling.max:,}"
    )
    if lifted:
        return (
            f"{head}: {held} document(s), {lifted} lifted by a departure, the longest of the others {rel}"
            f" at {length:,}, {margin}"
        )
    return f"{head}: {held} document(s), the longest {rel} at {length:,}, {margin}"


# ---------------------------------------------------------------- green, count lines and skips


def g1_measured(length: int, ceiling: Ceiling) -> str:
    return f"{length:,} characters against the ceiling '{ceiling.name}' of {ceiling.max:,}"


def g1_lifted(length: int, ceiling: Ceiling, index: int) -> str:
    return (
        f"{length:,} characters; the ceiling '{ceiling.name}' is lifted by {_ns()}.departures entry {index}"
    )


def g1_skip_no_ceiling() -> str:
    return f"no ceiling is set ({_ns()}.ceilings)"


def g1_skip_not_covered(rel: str) -> str:
    return f"{rel} is under no ceiling ({_ns()}.ceilings)"


def f9_tail(documents: int, ceilings: int, departures: int, scanned: int) -> str:
    return (
        f"{documents} document(s) measured under {ceilings} ceiling(s) and {departures} departure(s),"
        f" {scanned} Markdown file(s) scanned"
    )


# ---------------------------------------------------------------- the history report


def h1_day(day: datetime.date, ceiling: Ceiling, documents: int, longest: tuple[str, int] | None) -> str:
    if longest is None:
        return f"{day.isoformat()} {ceiling.name}: no document"
    rel, length = longest
    return f"{day.isoformat()} {ceiling.name}: {documents} document(s), the longest {rel} at {length:,}"


def h1_window(
    ceiling: Ceiling, since: datetime.date, last: datetime.date, longest: tuple[str, int] | None, thumb: int
) -> str:
    if longest is None:
        return f"window {ceiling.name}: no document from {since.isoformat()} to {last.isoformat()}"
    rel, length = longest
    return (
        f"window {ceiling.name}: {since.isoformat()} to {last.isoformat()}, {(last - since).days} day(s),"
        f" the longest {rel} at {length:,}; plus {round(MARGIN * 100)} % rounded up to {ROUND_TO:,}:"
        f" {thumb:,}; set now: {ceiling.max:,}"
    )


def h1_closing(since: datetime.date, commits: int, days: int, ceilings: int) -> str:
    return (
        f"{_ns()}: history since {since.isoformat()} — {commits} commit(s) of the first-parent line on"
        f" {days} day(s), {ceilings} ceiling(s); a report, nothing judged"
    )


def h1_no_commit(since: datetime.date) -> str:
    return (
        f"{_ns()}: history since {since.isoformat()} — no commit on the first-parent line; a report,"
        " nothing judged"
    )


# ---------------------------------------------------------------- the session-start line


def s1_empty() -> str:
    return f"{_ns()}: no document is measured — {_ns()}.ceilings is empty or absent in {DIALS_FILE}"


def s1_no_dials(root: str) -> str:
    return (
        f"{_ns()}: no {DIALS_FILE} in {root} — the length gate measures nothing there until the file"
        f" sets a ceiling in {_ns()}.ceilings"
    )


def s1_no_repo(cwd: str) -> str:
    return f"{_ns()}: {cwd} is not inside a git repository — the length gate measures nothing there"


def s1_prefix() -> str:
    return _ns()


def s1_could_not_run() -> str:
    return "BROKEN: the session-start line could not be printed — the gate's state is unknown"


# ---------------------------------------------------------------- this module's own failures (C12)


def c12_event(event: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"this check is wired to a tool event before or after a write, not to '{event}'",
        "in hooks.json wire it to PostToolUse on Write|Edit, or run it with --scan [<dir>]",
    )


def c12_since(value: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"misinvocation: --since takes a date written YYYY-MM-DD, not '{one_line(shown(value))}'",
        "run --scan [<dir>] --since <YYYY-MM-DD>, the first day of the window to report",
    )


def c12_shallow(root: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{root} is a shallow clone, so its history holds only the last commits",
        "a report on days it cannot see would say they held nothing: run git fetch --unshallow, or in"
        " CI check out with the whole history (fetch-depth: 0), then run the report again",
    )


def c12_git_history(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not read the history: {detail}",
        "repair what git names in the message, then check by hand: git log --first-parent -1",
    )


# ---------------------------------------------------------------- this module's dial failures (C5)


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_unknown_key(key: str, known: Sequence[str]) -> Broken:
    return _c5(
        f"{_ns()}.{key} is no dial of this module",
        "a misspelt dial would be ignored in silence, so none is: write one of " + ", ".join(known),
    )


def c5_ceilings() -> Broken:
    return _c5(
        f"{_ns()}.ceilings must be a list of entries",
        'write one entry per "- " item with the fields name, paths, max, level and window; leave the key'
        " out, or write [], for no ceiling",
    )


def c5_ceiling(index: int, detail: str) -> Broken:
    return _c5(
        f"{_ns()}.ceilings entry {index}: {detail}",
        "write the entry as name: <kebab-case>, paths: [<patterns>], max: <characters>, level: warning"
        " or error, window: {from: <YYYY-MM-DD>, to: <YYYY-MM-DD>}, the days of data the number was set"
        " from",
    )


def c5_pattern(where: str, pattern: str) -> Broken:
    """`where` names the entry's paths holding the pattern."""
    return _c5(
        f"{_ns()}.{where} holds '{one_line(shown(pattern))}', which git would read as a comment or as two"
        " lines",
        "patterns are gitignore syntax: escape a leading # as \\# bare or in single quotes, as \\\\# in"
        " double quotes, and remove a line break",
    )


def c5_duplicate_name(name: str) -> Broken:
    return _c5(
        f"{_ns()}.ceilings names '{one_line(shown(name))}' twice",
        "a departure lifts a ceiling by its name, so each name is one entry's: rename one of the two",
    )


def c5_window(name: str, window_days: int, start: datetime.date, end: datetime.date) -> Broken:
    return _c5(
        f"{_ns()}.ceilings '{name}' is at level error on a window of {window_days} day(s),"
        f" {start.isoformat()} to {end.isoformat()}",
        f"a ceiling blocks only on {WINDOW_DAYS} days of observed data or more: set its level to warning"
        f" until window.to is {WINDOW_DAYS} days or more after window.from — the report --scan --since"
        " <YYYY-MM-DD> prints the data of those days",
    )


def c5_overlap(first: str, second: str, rel: str) -> Broken:
    return _c5(
        f"{_ns()}.ceilings '{first}' and '{second}' both hold {one_line(shown(rel))}",
        "a document is held to one ceiling at most, so that its number never depends on the order of the"
        " list: narrow one entry's paths, or take the file out of one with a negated pattern; a document"
        " that must stand over its ceiling takes a departure",
    )


def c5_departures() -> Broken:
    return _c5(
        f"{_ns()}.departures must be a list of entries",
        'write one entry per "- " item with the fields paths (a list of patterns), allow (a list of ceiling'
        " names) and reason (one line); leave the key out, or write [], for no departure",
    )


def c5_departure(index: int, detail: str, names: Sequence[str]) -> Broken:
    known = ", ".join(names) if names else "none is set"
    return _c5(
        f"{_ns()}.departures entry {index}: {detail}",
        "write the entry as paths: [<patterns>], allow: [<ceiling names>], reason: <one line saying why"
        f" these documents stand as written>; the ceilings are named in {_ns()}.ceilings: {known}",
    )
