"""The texts of this module's own findings, skips and dial failures, as functions with typed
parameters; the texts every gate shares live in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (r1_, g1_, c5_, ...), so a text can be
cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

import shlex

from constitution_layer_kit import identity
from constitution_layer_kit.messages import echoed, escaped
from constitution_layer_kit.model import Broken, Finding, SharedKey

from .model import ActKey, Key, ToolKey

_MENTION = "{pattern: <regular expression whose whole match is a document's id>}"
_LANE = "{pattern: <regular expression>, names: <what the form cites>, fix: <the link form to write>}"


def _ns() -> str:
    return identity.current().namespace


def _file() -> str:
    return identity.dials_file()


# ---------------------------------------------------------------- findings: the forms of a reference

_WHY_BARE = (
    "a bare handle resolves only inside its home document: elsewhere no reader can follow it, no"
    " check can test it, and a move cannot find it"
)


def r1_bare_form(rel: str, line: int, match: str, names: str, fix: str) -> Finding:
    """`names` and `fix` are the project's words, from its lane; the reason is never theirs."""
    return Finding(
        Key.R1,
        f"{escaped(rel)}:{line}: '{echoed(match)}' cites {echoed(names)} by a bare handle",
        _WHY_BARE,
        f"write it as a link: {escaped(fix)}",
    )


def r2_bare_id(rel: str, line: int, doc_id: str, owner: str, path_to_owner: str) -> Finding:
    return Finding(
        Key.R2,
        f"{escaped(rel)}:{line}: document id '{escaped(doc_id)}' stands in backticks and is no link",
        "an id names a document that can move: only a link lets a reader reach it and lets a move repair it",
        f"write [{escaped(doc_id)}]({escaped(path_to_owner)}) — the path from this document to"
        f" {escaped(owner)}",
    )


def r3_id_link_astray(
    rel: str, line: int, doc_id: str, target: str, owner: str, path_to_owner: str
) -> Finding:
    return Finding(
        Key.R3,
        f"{escaped(rel)}:{line}: the link's text is document id '{echoed(doc_id)}', and its target"
        f" {echoed(target)} is not that document ({escaped(owner)})",
        "a link that shows one document's id and opens another misleads every reader who trusts the text",
        f"point it at {escaped(path_to_owner)}; after a move, every such link is repaired at once by:"
        f" {mover_command('--ids')}",
    )


def r4_one_machine(rel: str, line: int, match: str) -> Finding:
    return Finding(
        Key.R4,
        f"{escaped(rel)}:{line}: '{echoed(match)}' is a path on one machine",
        "it resolves on the machine it was written on and nowhere else",
        "link a file of this repository by its relative path, or cite the public address the fact was"
        " verified at, or drop the reference",
    )


# ---------------------------------------------------------------- findings: the whole tree

_WHY_BROKEN = (
    "a reference that does not resolve fails the reader exactly when they need it, and nobody else sees it"
)


def r5_no_target(rel: str, line: int, destination: str) -> Finding:
    return Finding(
        Key.R5,
        f"{escaped(rel)}:{line}: link target {echoed(destination)} does not exist",
        _WHY_BROKEN,
        "correct the path; if the target was moved by hand, repair every link to it by:"
        f" {mover_command('--moved', '<old path>', '<new path>')}; if it was deleted, remove the link and"
        " state here what it was cited for",
    )


def r5_unresolved(rel: str, line: int, destination: str, words: str) -> Finding:
    """A break the link checker reports in words this module has no text of its own for."""
    return Finding(
        Key.R5,
        f"{escaped(rel)}:{line}: link target {echoed(destination)} does not resolve: {echoed(words)}",
        _WHY_BROKEN,
        "correct the link so that it names a file of this repository by its relative path",
    )


def r6_no_anchor(
    rel: str, line: int, destination: str, fragment: str, target: str, other_case: str | None
) -> Finding:
    hint = f" (it has '{escaped(other_case)}': an anchor's case counts)" if other_case is not None else ""
    fix = (
        f"cite '{escaped(other_case)}' as it is written"
        if other_case is not None
        else f'cite an anchor the target carries, or add <a id="{escaped(fragment)}"></a> on its own line'
        f" before the cited place in {escaped(target)}"
    )
    return Finding(
        Key.R6,
        f"{escaped(rel)}:{line}: {echoed(destination)} has no anchor '{escaped(fragment)}'{hint}",
        _WHY_BROKEN,
        fix,
    )


def r7_heading_anchor(rel: str, line: int, destination: str, target: str) -> Finding:
    return Finding(
        Key.R7,
        f"{escaped(rel)}:{line}: {echoed(destination)} resolves only through a heading — its generated name,"
        f" or a {{#key}} written after it — not through an anchor written in {escaped(target)}",
        "a generated name changes when the heading is reworded, and every link through it breaks unseen",
        f'add <a id="<short fixed key>"></a> on its own line before that heading in {escaped(target)} and'
        f" cite the key; a repository whose links go through headings sets {_ns()}:"
        f" {{heading_anchors: allow}} in"
        f" {_file()} until they are converted",
    )


def r8_unknown_mention(rel: str, line: int, match: str) -> Finding:
    return Finding(
        Key.R8,
        f"{escaped(rel)}:{line}: '{echoed(match)}' names a document no covered document carries as its id",
        "outside Markdown no link checker follows a name, so it dangles unseen once the document is"
        " renamed or deleted",
        "correct the name, or drop the mention and state the rule in words",
    )


# ---------------------------------------------------------------- the link checker cannot be used

_INSTALL = "https://lychee.cli.rs/installation/"


def x1_no_lychee(floor: str) -> Broken:
    return Broken(
        ToolKey.X1,
        f"{_ns()} needs lychee {floor} or newer and found none on PATH",
        f"install it ({_INSTALL}), then run the scan — until then no reference is checked for resolving",
    )


def x2_lychee_too_old(floor: str, said: str) -> Broken:
    found = f"found '{echoed(said)}'" if said else "its version could not be read"
    return Broken(
        ToolKey.X2,
        f"{_ns()} needs lychee {floor} or newer, {found}",
        f"install a current one ({_INSTALL}), then run the scan — until then no reference is checked for"
        " resolving",
    )


def x3_no_report(what: str, first_line: str) -> Broken:
    said = f" ({escaped(first_line)})" if first_line else ""
    return Broken(
        ToolKey.X3,
        f"lychee gave no report: {what}{said}",
        "this is a defect of the gate's invocation or of the installed lychee, not of the repository; run"
        " lychee --version and report both to whoever maintains the plugin — until then no reference is"
        " checked for resolving",
    )


def x3_too_slow(seconds: float) -> Broken:
    """The budget of a check after a write ran out inside lychee's run: lychee is not at fault, the tree
    is large. `seconds` is the whole budget, not what was left for the run when it began."""
    return Broken(
        ToolKey.X3,
        f"lychee gave no report within the {seconds:g} s a check after a write waits, the tree's reading"
        " and masking counted",
        "a large tree can take lychee longer than that; run the scan, which waits for lychee as long as it"
        " takes — until then no reference is checked for resolving",
    )


def x3_out_of_time(seconds: float, before_write: bool) -> Broken:
    """The budget of a hook's check ran out before the check was done: the module's own reading, and after a
    write the masking too, of a large tree took all of it, so lychee, which after a write was not yet run,
    is not blamed. Before a write there is no lychee at all: the line names the reading alone."""
    if before_write:
        return Broken(
            ToolKey.X3,
            f"the check before a write used its {seconds:g} s reading the covered documents",
            "a large tree takes longer than that to read; run the scan, which waits as long as it takes"
            " — until then the references of this write are not checked",
        )
    return Broken(
        ToolKey.X3,
        f"the check after a write used its {seconds:g} s reading and masking the tree before lychee could"
        " run",
        "a large tree takes longer than that to read; run the scan, which waits as long as it takes — until"
        " then no reference is checked for resolving",
    )


# ---------------------------------------------------------------- green, skip and count lines


def g1_covered() -> str:
    return "a covered document"


def g1_skip_not_covered(rel: str) -> str:
    return f"{escaped(rel)} is not covered ({_ns()}.territories)"


def f9_after_write(rel: str, links: int, findings: int, shown_first: int | None) -> str:
    """The count line of the check after a write: the whole tree is examined, and the findings
    that involve the written document are reported — all, or the first so many."""
    cut = f" — the first {shown_first} shown" if shown_first is not None else ""  # by count or by size
    return f"{links} link(s) of the whole tree examined, {findings} finding(s) involve {escaped(rel)}{cut}"


def c12_event(name: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"hook input names the event '{echoed(name)}', which this gate is not wired to",
        "wire the gate to PreToolUse and PostToolUse on Write|Edit, as the plugin's hooks file does; to"
        " check a repository by hand run it with --scan [<dir>]",
    )


def f9_scan_tail(documents: int, links: int, scanned: int, lanes: int, mentions: int, files: int) -> str:
    tail = (
        f"{documents} document(s) and {links} link(s) examined, {scanned} Markdown file(s) scanned,"
        f" {lanes} lane(s)"
    )
    return tail + (f", {mentions} mention pattern(s) over {files} other file(s)" if mentions else "")


# ---------------------------------------------------------------- this module's dial failures


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{_file()}: {detail}", fix)


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


def c5_governed_only() -> Broken:
    return _c5(
        f"{_ns()}.governed_only must be true or false",
        "write governed_only: true to cover only documents a policy governs, or remove the key",
    )


_GOVERNED_ONLY_NEEDS_ROOT = "name the root policy, or remove governed_only"


def c5_governed_only_without_root() -> Broken:
    """The gate's twin of the mover's V5: a skip would let a write through with nothing examined."""
    return _c5(
        f"{_ns()}.governed_only is set and no root_policy is named, so nobody can say which documents a"
        " policy governs",
        _GOVERNED_ONLY_NEEDS_ROOT,
    )


def c5_mentions_not_a_list() -> Broken:
    return _c5(
        f"{_ns()}.mentions must be a list of mention patterns",
        f"write it as {_ns()}: {{mentions: [{_MENTION}]}}, or remove the key",
    )


def c5_mention(position: int, what: str) -> Broken:
    return _c5(
        f"entry {position} of {_ns()}.mentions {what}",
        f"write the entry as {_MENTION}; files: [<patterns>] is optional",
    )


def mention_not_a_mapping() -> str:
    return "is not a mapping of pattern and files"


def mention_unknown_key(key: str) -> str:
    return f"carries the key '{echoed(key)}'; a mention holds pattern and files, and nothing else"


def mention_files() -> str:
    return "has files that is not a list of path patterns"


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
    return f"carries the key '{echoed(key)}'; a lane holds pattern, names, fix and home, and nothing else"


def lane_needs(field: str) -> str:
    return f"needs {field}: a non-empty string"


def lane_home() -> str:
    return "has a home that is not a list of path patterns"


def lane_pattern(error: str) -> str:
    return (
        f"has a pattern that is no regular expression ({escaped(error)}) — in YAML write it in single"
        " quotes, where a backslash stands for itself"
    )


def lane_pattern_control(char: str) -> str:
    """A lane's or a mention's pattern holding a control character — what YAML's double quotes make
    of `\\b` — is refused before it is compiled, since it would match nothing and pass in silence."""
    return (
        f"has a pattern holding the control character {char!r} — YAML's double quotes turn a backslash"
        " escape into one, so the pattern would match nothing and pass in silence; write it in single"
        " quotes, where a backslash stands for itself"
    )


# ---------------------------------------------------------------- the mover: a generator, never a gate


def mover_command(*arguments: str) -> str:
    """The mover as a command a reader can paste: the plugin's own path, resolved."""
    script = identity.current().plugin_root / "scripts" / "move-document.sh"
    return " ".join(["sh", f'"{script}"', *arguments])


def v1_moved(old: str, new: str) -> str:
    return f"MOVED: {escaped(old)} → {escaped(new)}"


def v2_rewrote(rel: str, links: int) -> str:
    return f"REWROTE: {escaped(rel)}: {links} link(s)"


def v3_mention(rel: str, line: int, text: str) -> str:
    return (
        f"MENTION: {escaped(rel)}:{line}: '{echoed(text)}' names the old path outside a link — read it"
        " and decide; nothing was changed"
    )


def v4_count(files: int, links: int, mentions: int) -> str:
    return (
        f"{files} file(s) rewritten, {links} link(s), {mentions} mention(s) listed; the whole tree is"
        " checked next"
    )


def v4_nothing_changed() -> str:
    return "BROKEN: the move could not run — nothing was changed"


def v4_moved_back(old: str) -> str:
    return (
        f"BROKEN: the move could not run — the file was moved back to {escaped(old)}, and nothing was changed"
    )


def v4_move_back_failed(old: str, new: str, detail: str) -> str:
    return (
        f"BROKEN: the move could not be undone — git mv refused to move {escaped(new)} back to"
        f" {escaped(old)}: {escaped(detail)}; the file is at {escaped(new)}"
    )


def v4_folder_left(old: str, folder: str, reason: str) -> str:
    return (
        f"BROKEN: the move was undone, the file back at {escaped(old)}, but the folder {escaped(folder)} it"
        f" made could not be removed ({echoed(reason)})"
    )


def v4_stopped_midway() -> str:
    return (
        "BROKEN: the act stopped midway — what the lines above name was moved or rewritten, and the"
        " check of the whole tree has not run: look at git status, repair the cause, then run the scan"
    )


def v2_left_alone(rel: str) -> str:
    return f"LEFT ALONE: {escaped(rel)} is not UTF-8 text — its links, if any, were not repaired"


_USAGE = (
    "<old path> <new path> to move a file and repair the links; --moved <old path> <new path> after a"
    " move made by hand; --ids to point every link whose text is a document's id at that document"
)


def v5_usage(detail: str) -> Broken:
    return Broken(ActKey.V5, f"misinvocation: {echoed(detail)}", f"run it with {_USAGE}")


def v5_refused(what: str, fix: str) -> Broken:
    return Broken(ActKey.V5, what, fix)


def v5_not_listed(old: str) -> Broken:
    return v5_refused(
        f"{escaped(old)} is not a file git lists",
        "name a file of this repository, by its path from where you stand",
    )


def v5_target_exists(new: str) -> Broken:
    return v5_refused(
        f"{escaped(new)} already exists", "choose a path that is free, or move what lies there first"
    )


def v5_same(old: str) -> Broken:
    return v5_refused(f"{escaped(old)} would move onto itself", "name two different paths")


def v5_not_moved(old: str, new: str) -> Broken:
    return v5_refused(
        f"--moved says the move was made by hand, yet {escaped(old)} still exists or {escaped(new)} does not",
        "to make the move and repair the links in one act, run it without --moved",
    )


def v5_outside(path: str) -> Broken:
    return v5_refused(f"{echoed(path)} lies outside the repository", "name a path inside it")


def v5_git_mv(first_line: str) -> Broken:
    return v5_refused(
        f"git mv refused: {escaped(first_line)}", "repair what git names, then run the move again"
    )


def v5_no_repository(where: str) -> Broken:
    return v5_refused(
        f"{escaped(where)} is not inside a git repository", "run the mover from inside the repository"
    )


def v5_names_a_directory(new: str) -> Broken:
    return v5_refused(
        f"{echoed(new)} names a directory, not the file's new path",
        "give the new path in full, file name included — a document is never moved 'into' a directory",
    )


def v5_is_a_link(old: str) -> Broken:
    return v5_refused(
        f"{escaped(old)} is a symbolic link, not a document",
        "move the document it points at; move the link itself with git mv, its target being relative to it",
    )


def v5_leaves_markdown(old: str, new: str) -> Broken:
    return v5_refused(
        f"{escaped(old)} is a Markdown document and {escaped(new)} is not named as one",
        "keep the .md ending: a document that loses it is no longer checked, and its own links are"
        " never repaired",
    )


def v5_parent_is_a_file(path: str) -> Broken:
    return v5_refused(
        f"{escaped(path)} is a file, so nothing can lie inside it",
        "name a new path whose directories exist or can be made",
    )


def v5_unreadable(path: str, reason: str) -> Broken:
    return v5_refused(
        f"{escaped(path)} is a document the mover must read, and it cannot be read ({echoed(reason)}),"
        " so nobody can say which of its links need repair",
        "make it readable — its permissions — then run the mover again",
    )


def v5_unwritable(path: str, reason: str) -> Broken:
    return v5_refused(
        f"{escaped(path)} holds links the mover must rewrite, and it cannot be written ({echoed(reason)})",
        "make it writable — its permissions, a lock on the file, a file system mounted read-only — then"
        " run the mover again",
    )


def _shell(path: str) -> str:
    """A path in a command to paste: quoted for a POSIX shell, then shown by the echo rule."""
    return escaped(shlex.quote(path))


def v5_takes_the_root_policy(old: str, new: str, folder: str) -> Broken:
    """`folder`: the new path's folder, which the move had to make and the move by hand must make first;
    empty when it exists."""
    made = f"mkdir -p {_shell(folder)} && " if folder else ""
    return v5_refused(
        f"moving {escaped(old)} takes away the root policy {_file()} names, so the dials would name a file"
        " that is gone",
        f"move it by hand with {made}git mv -- {_shell(old)} {_shell(new)}, set root_policy to {escaped(new)}"
        f" in {_file()}, then run {mover_command('--moved', _shell(old), _shell(new))}; outside the root"
        " policy's own territory, --moved then meets C9, whose fix follows",
    )


def v5_no_root_policy() -> Broken:
    return v5_refused(
        f"{_ns()}.governed_only is set and {_file()} names no root_policy, so nobody can say which"
        " documents a move must repair",
        _GOVERNED_ONLY_NEEDS_ROOT,
    )


def v5_no_dials(root: str) -> Broken:
    return v5_refused(
        f"no {_file()} in {escaped(root)}: the check that proves a move cannot run",
        f"create {_file()} at the repository's top — a file that holds only module_prefix: const- is enough",
    )
