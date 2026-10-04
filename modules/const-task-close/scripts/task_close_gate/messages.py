"""The texts of this module's own findings, notes, green and count lines, dial failures and
configuration failures, as functions with typed parameters; the texts every gate shares live
in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (t1_, n1_, g1_, c5_, ...), so a text can
be cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from const_gate import identity
from const_gate.messages import echoed, escaped
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import DEFAULT_KEY, DEFAULT_TRUNK, SHOWN_LINES, SHOWN_PATHS, Declaration, Key, Pair

_PAIR = "{name: <kebab>, code: [<patterns>], docs: [<paths>]}"
_PAIR_FULL = (
    "{name: <kebab>, code: [<gitignore patterns of the code it describes>], docs: [<paths of the"
    " documents that describe it>]}"
)


def _ns() -> str:
    return identity.current().namespace


def _some(items: Sequence[str], limit: int, show: Callable[[str], str] = escaped) -> str:
    """The first few of a list, each shown by `show` — `escaped` for a path, `echoed` for a line that only
    points — then an ellipsis."""
    head = ", ".join(show(item) for item in items[:limit])
    return head + (", …" if len(items) > limit else "")


# ---------------------------------------------------------------- findings


def t1_dirty_tree(lines: Sequence[str]) -> Finding:
    return Finding(
        Key.T1,
        f"the working tree is dirty at turn end — {len(lines)} path(s): {_some(lines, SHOWN_LINES, echoed)}",
        "rollback points live in git, not in the chat's rewind, which does not see edits made through"
        " the shell, a script or a subagent — work not committed did not happen",
        "commit what is finished: git add -A && git commit -m '<what changed and why>' — stash or discard"
        " what is not; this is asked once per turn, and the rule is the skill commit-before-edit",
    )


def t2_not_updated(pair: Pair, touched: Sequence[str], key: str) -> Finding:
    docs = ", ".join(escaped(doc) for doc in pair.docs)
    return Finding(
        Key.T2,
        f"{pair.name}: the change touches {len(touched)} path(s) this pair describes"
        f" ({_some(touched, SHOWN_PATHS)}) and none of its document(s): {docs}",
        "task close is a single act: code and the current-state documents that describe it change"
        " together, or the change says why the documents stand",
        f'update {docs} in this change, or declare no impact: add the trailer "{key}: {pair.name} — <why'
        ' the documents are unaffected>" to a commit of the range, in its last paragraph, where every'
        " line is Key: value — or the same line on its own in the pull request's description, given"
        " to the scan with --body <file>",
    )


def t3_names_no_pair(declaration: Declaration, key: str, names: Sequence[str]) -> Finding:
    return Finding(
        Key.T3,
        f'{declaration.where}: "{key}: {echoed(declaration.value)}" names no pair of the coverage map'
        f" (pairs: {', '.join(names)})",
        "a declaration must name what it declares unaffected, or it declares nothing",
        "name one of the pairs before the dash, or remove the line",
    )


def t4_no_reason(declaration: Declaration, key: str) -> Finding:
    return Finding(
        Key.T4,
        f'{declaration.where}: "{key}: {declaration.pair}" carries no reason',
        "a declaration is a judgment; the reason is what a reviewer reads",
        f"write it as {key}: {declaration.pair} — <why the documents are unaffected>",
    )


# ---------------------------------------------------------------- notes


def n1_declared(declaration: Declaration, covered: bool) -> str:
    if covered:
        return (
            f"note: {declaration.pair}: no impact declared in {declaration.where}:"
            f" {escaped(declaration.reason)}"
        )
    return (
        f"note: {declaration.pair}: no impact declared in {declaration.where}, and the change touches"
        " nothing this pair describes"
    )


def n2_working_files(paths: Sequence[str]) -> str:
    return (
        f"note: {len(paths)} tracked file(s) match working_files ({_some(paths, SHOWN_PATHS)}) — a task's"
        " working files are deleted at its close; keep one only with a reason"
    )


# ---------------------------------------------------------------- green and count lines


def g1_clean() -> str:
    return "the working tree examined, clean"


def g1_second_stop(dirty: int) -> str:
    return (
        f"the working tree examined — {dirty} path(s) dirty; a stop hook already continued this turn"
        " once, so it is not asked again and the turn ends"
    )


def f9_count_hook(dirty: int) -> str:
    return f"RED: 1 finding — the working tree examined ({dirty} path(s) dirty)"


def f9_scan_tail(pairs: int, commits: int, base_short: str, tip_short: str, rooted: bool) -> str:
    if rooted:
        return f"{pairs} pair(s) examined over 0 commit(s) — nothing landed before {tip_short}"
    return f"{pairs} pair(s) examined over {commits} commit(s), {base_short}..{tip_short}"


def f9_scan_tail_empty() -> str:
    return "0 pair(s) examined — coverage is empty"


# ---------------------------------------------------------------- this module's own failures


def x1_document_missing(pair: str, path: str, head_short: str) -> Broken:
    return Broken(
        Key.X1,
        f"{DIALS_FILE}: {_ns()}.coverage[{pair}] names the document {escaped(path)}, which does not exist at"
        f" HEAD ({head_short})",
        "correct the path, or create the document; a pair whose document is gone describes nothing",
    )


def x2_document_is_directory(pair: str, path: str, head_short: str) -> Broken:
    return Broken(
        Key.X2,
        f"{DIALS_FILE}: {_ns()}.coverage[{pair}] names {escaped(path)}, which is a directory at HEAD"
        f" ({head_short})",
        "name the document file; a change names files, so a directory can never count as updated",
    )


def c5_coverage_not_a_list() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.coverage must be a list of pairs",
        f"write it as coverage: [{_PAIR}]",
    )


def c5_pair(position: int, detail: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.coverage[{position}] {detail}",
        f"write the pair as {_PAIR_FULL}",
    )


# what is wrong with a pair: the parts of the C5 line above


def pair_not_a_mapping() -> str:
    return "is not a mapping"


def pair_unknown_key(key: str) -> str:
    return f"carries the key '{echoed(key)}', which no pair has (name, code, docs)"


def pair_name() -> str:
    return "has no name, or one that is not kebab-case"


def pair_name_repeated(name: str) -> str:
    return f"repeats the name '{name}'"


def pair_code() -> str:
    return "has no code, or code is not a non-empty list of patterns"


def pair_docs() -> str:
    return "has no docs, or docs is not a non-empty list of repository-relative paths"


def pair_docs_directory(path: str) -> str:
    return f"names '{escaped(path)}', a directory — a pair's documents are files"


def c5_trunk() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.trunk must be a non-empty string",
        f"set trunk: <the branch changes land on>, or remove the line for {DEFAULT_TRUNK}",
    )


def c5_declaration_key() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.declaration_key must be a trailer key: letters, digits and hyphens",
        f"set declaration_key: {DEFAULT_KEY}, or remove the line",
    )


def c5_working_files() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.working_files must be a list of patterns",
        "write it as working_files: [<gitignore patterns>], or remove the line",
    )


SCAN_USAGE = "--scan [<dir>] [--since <ref> | --change <commit>] [--body <file>]"


def c12_not_wired(event: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"hook input names the event '{echoed(event)}', which this gate is not wired to",
        f"wire the gate to Stop, as the plugin's hooks file does; to check a change by hand run it with"
        f" {SCAN_USAGE}",
    )


def c12_unknown_ref(flag: str, ref: str, root: str, detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{flag} names '{echoed(ref)}', which git cannot resolve in {escaped(root)}: {escaped(detail)}",
        "name a commit, branch or tag this repository has; a shallow clone may need its history fetched"
        " (git fetch --unshallow)",
    )


def c12_no_trunk(trunk: str, root: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"the trunk '{echoed(trunk)}' is neither a local branch nor origin/{echoed(trunk)} in"
        f" {escaped(root)}",
        f"set {_ns()}.trunk to the branch changes land on, or run the scan with --since <ref>",
    )


def c12_since_and_change() -> Broken:
    return Broken(
        SharedKey.C12,
        "--since and --change exclude each other",
        "give one: --since <ref> examines the changes since that base, --change <commit> examines one"
        " landed change",
    )


def c12_body_unreadable(path: str, error: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"--body names {escaped(path)}, which cannot be read ({error})",
        "give the pull request's description as a readable file",
    )


def c12_range(base_short: str, tip_short: str, root: str, detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not read the range {base_short}..{tip_short} in {escaped(root)}: {escaped(detail)}",
        "repair what git names in the message; a shallow clone may need its history fetched"
        " (git fetch --unshallow)",
    )


def c12_tree(root: str, detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not read the working tree in {escaped(root)}: {escaped(detail)}",
        "repair what git names in the message, then check by hand: git -C <that directory> status",
    )
