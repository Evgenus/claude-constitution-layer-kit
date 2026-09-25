"""The texts of this module's own findings, green lines, count lines, session-start lines and
dial failures, as functions with typed parameters; the texts every gate shares live in the
shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (d1_, l1_, g1_, f9_, s1_, c5_, c12_), so a
text can be cited, reviewed and asserted by key. A reader must be able to act on a message
without holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Sequence

from const_gate import identity
from const_gate.messages import shown
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import COMMAND_FLAG, Entry, Key, Subcommand


def _ns() -> str:
    return identity.current().namespace


# ---------------------------------------------------------------- the findings


def d1_destructive(entry: Entry, subcommand: Subcommand, matched: str) -> Finding:
    what = f"'{shown(subcommand.text)}' matches the entry {' '.join(entry.command)}"
    if matched:
        what += f" with {matched}"
    return Finding(
        Key.D1,
        f"destructive command: {what}",
        entry.teach,
        f"{entry.alternative}; to run it as written, confirm at the prompt — where no prompt can be"
        " shown, get the user's yes in chat and run it again, one yes per command; to stop gating it,"
        f" remove the entry from {_ns()}.destructive in {DIALS_FILE}",
    )


def l1_list_item(rel: str, line: int, text: str) -> Finding:
    return Finding(
        Key.L1,
        f"{rel}:{line}: list item without a handle — {shown(text)}",
        "an item with no stable handle cannot be cited without quoting it, so a reader cannot point at one",
        "open the item with a handle — a number, a letter or a short key such as R1 or Q-a — or add the"
        f" form the document uses to {_ns()}.handles in {DIALS_FILE}, or take the document out of"
        f" {_ns()}.territories by a negated pattern",
    )


# ---------------------------------------------------------------- green, skip, count


def g1_command_passed(entries: int, subcommands: int) -> str:
    """The whole green line of the shell gate: what it examined and against what."""
    return f"1 command examined: {subcommands} subcommand(s) against {entries} entries, none matched"


def g1_nothing_gated() -> str:
    return f"1 command examined against 0 entries — {_ns()}.destructive is empty, nothing is gated"


def g1_skip_no_command() -> str:
    return f"no command given: run the scan with {COMMAND_FLAG} '<text>' to see what the dial does to it"


def g1_skip_not_covered(rel: str) -> str:
    return f"{rel} is not covered ({_ns()}.territories)"


def f9_count_command(findings: int, subcommands: int) -> str:
    return f"RED: {findings} finding(s) — 1 command examined ({subcommands} subcommand(s))"


def f9_command_tail(entries: int, subcommands: int) -> str:
    return f"1 command examined: {subcommands} subcommand(s) against {entries} entries"


def f9_lists_tail(documents: int, handles: int, scanned: int) -> str:
    return f"{documents} document(s) examined for lists with {handles} handle form(s), {scanned} Markdown file(s) scanned"


# ---------------------------------------------------------------- session start: the visible zero (S1)


def s1_empty() -> str:
    return f"{_ns()}: no command is gated — {_ns()}.destructive is an empty list in {DIALS_FILE}"


def s1_no_dials(root: str) -> str:
    return (
        f"{_ns()}: no {DIALS_FILE} in {root} — the destructive-command gate examines nothing there until"
        " the file exists (an empty mapping, {}, is enough for the default list)"
    )


def s1_no_repo(cwd: str) -> str:
    return f"{_ns()}: {cwd} is not inside a git repository — the destructive-command gate examines nothing there"


def s1_prefix() -> str:
    return _ns()


def s1_could_not_run() -> str:
    return "BROKEN: the session-start line could not be printed — the gate's state is unknown"


def s1_pairs_heading() -> str:
    return f"Boundary examples of this project ({_ns()}.boundary_examples), each violates / complies:"


# ---------------------------------------------------------------- this module's dial failures (C5)


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_unknown_key(key: str, known: Sequence[str]) -> Broken:
    return _c5(
        f"{_ns()}.{key} is no dial of this module",
        "a misspelt dial would be ignored in silence, so none is: write one of " + ", ".join(known),
    )


def c5_territories() -> Broken:
    return _c5(
        f"{_ns()}.territories must be a non-empty list of path patterns",
        'write the patterns of the documents to scan for lists, one per line under "- ", or leave the key'
        " out to cover every Markdown file; an empty list would examine nothing in silence",
    )


def c5_handles() -> Broken:
    return _c5(
        f"{_ns()}.handles must be a non-empty list of regular expressions",
        "write the handle forms a list item may open with, one per line under \"- \" in single quotes, or"
        " leave the key out for the defaults; an empty list would find every list red",
    )


def c5_handle_pattern(pattern: str, error: str) -> Broken:
    return _c5(
        f"{_ns()}.handles holds '{pattern}', which is not a regular expression ({error})",
        "repair the pattern; Python's re syntax, matched at the start of the item's text",
    )


def c5_destructive() -> Broken:
    return _c5(
        f"{_ns()}.destructive must be a list of entries",
        'write one entry per "- " item with the fields command (a list of words), flags (a list, optional),'
        " teach and alternative (texts); leave the key out for the default list; an empty list gates"
        " nothing and says so at session start",
    )


def c5_entry(index: int, detail: str) -> Broken:
    return _c5(
        f"{_ns()}.destructive entry {index}: {detail}",
        "write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard to"
        " reverse>, alternative: <the reversible way>",
    )


def c5_boundary_examples() -> Broken:
    return _c5(
        f"{_ns()}.boundary_examples must be a list of pairs {{violates: <text>, complies: <text>}}",
        'write one pair per "- " item with exactly those two fields, or leave the key out',
    )


# ---------------------------------------------------------------- this module's own C12


def c12_event(name: str, tool: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"hook input names the event '{name}' on tool '{tool}', which this gate is not wired to",
        "wire the gate to PreToolUse with the matcher Bash, as the plugin's hooks file does; to see what"
        f" the dial does to a command by hand run it with --scan {COMMAND_FLAG} '<text>'",
    )


def c12_lists_hook() -> Broken:
    return Broken(
        SharedKey.C12,
        "this check has no hook mode: it scans a tree and judges no single write",
        "run it with --scan [<dir>]; the plugin wires it to no event",
    )
