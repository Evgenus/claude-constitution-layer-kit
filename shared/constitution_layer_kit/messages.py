"""Every user-facing text the gates share, in one place, as functions with typed parameters:
verdict and count lines, skip reasons, notes about policies, configuration failures. A
module's own findings live in the module's own messages module, written the same way.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (f1_, c4_, g1_, ...), so a text can be
cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

import shlex
from collections.abc import Sequence

from . import identity
from .model import DIALECT, DIALECT_KEY, DIALS_FILE, ROOT_POLICY_KEY, Broken, FileTool, SharedKey


def _ns() -> str:
    return identity.current().namespace


SHOWN_MAX = 80


def shown(value: str) -> str:
    """A value echoed from a document, cut to a length that keeps a message a message: hook
    output is capped by the platform, and a value a page long teaches nothing."""
    return value if len(value) <= SHOWN_MAX else value[:SHOWN_MAX] + f"… [{len(value)} characters]"


def escaped(value: str) -> str:
    """A value on one line, never cut: a backslash and the line breaks shown escaped, since in hook
    mode only a failure's first line reaches the user. For a value the reader opens, copies or types
    into a fix, or that a later step reads — a path, an id typed into a fix, the text of a dial that
    teaches, a tool's one-line diagnosis; a cut one is no path and no word."""
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")


def echoed(value: str) -> str:
    """A value echoed in a message: cut as `shown` cuts, then escaped. For a value that only points
    at something the reader can see elsewhere — a dial key, a pattern, a phrase, a command word."""
    return escaped(shown(value))


def patterns(territory: Sequence[str]) -> str:
    return "[" + ", ".join(f"'{echoed(p)}'" for p in territory) + "]"


# ---------------------------------------------------------------- field-level parts every gate shares


def field_missing(key: str) -> str:
    return f"{key} missing"


def field_not_string(key: str, yaml_type: str) -> str:
    return f"{key} must be a quoted string (YAML read it as {yaml_type})"


# ---------------------------------------------------------------- verdict and count lines (F9, F10, G1, W1)


def f9_count_hook(findings: int, rel: str) -> str:
    return f"RED: {findings} finding(s) — 1 document examined ({escaped(rel)})"


def f9_count_scan(findings: int, tail: str) -> str:
    return f"RED: {findings} finding(s) — {tail}"


def f10_skill(skill: str) -> str:
    return f"{_ns()}: load the skill {_ns()}:{skill} before you fix this — it teaches the rule and the fix"


def g1_green_hook(what: str) -> str:
    return f"GREEN: {_ns()}: 1 document examined, {what}"


def governed_by(policy: str) -> str:
    return f"governed by {echoed(policy)}"


def g1_green_scan(tail: str) -> str:
    return f"GREEN: {_ns()}: {tail}"


def g1_green_event(line: str) -> str:
    """The green of a hook wired to an event that names no document: the module's whole line."""
    return f"GREEN: {_ns()}: {line}"


def g1_green_skip(reason: str) -> str:
    return f"GREEN: {_ns()}: 0 documents examined — {reason}"


def w1_warn_note() -> str:
    return (
        f"{_ns()}: severity is warn: the write proceeds, but the finding stands and recurs on"
        " every write until fixed"
    )


def w1_warn_system(headline: str) -> str:
    return f"{_ns()} (warn): {headline}"


def w1_warn_stop(body: str) -> str:
    """On Stop the user's notice is the whole verdict: nothing else reaches anyone, since context
    handed to the model there would continue the turn."""
    return f"{_ns()} (warn):\n{body}"


# skip reasons (the {reason} of G1)


def g1_skip_other_tool(tool: str) -> str:
    """G1.1: the event is for a tool this gate does not judge, however it came to the gate. The tools it
    does judge are the members of `FileTool`, so text and enum stay in step. A `Stop` and a session start
    name no tool: the line then says the event names none."""
    judged = " and ".join(t.value for t in FileTool)
    if not tool:
        return f"an event that names no tool is not one this gate judges (it judges {judged})"
    return f"tool '{echoed(tool)}' is not one this gate judges (it judges {judged})"


def g1_skip_not_markdown(path: str) -> str:
    return f"{escaped(path)} is not a .md file"


def g1_skip_no_repo(path: str) -> str:
    return f"{escaped(path)} is not inside a git repository; the constitution is silent there"


def g1_skip_no_dials(root: str) -> str:
    return f"no {DIALS_FILE} in {escaped(root)}: nothing is claimed"


def g1_skip_no_root() -> str:
    return f"{DIALS_FILE} has no root_policy: nothing is claimed"


def g1_skip_edit_unappliable(rel: str) -> str:
    return f"the Edit cannot be applied to {escaped(rel)}; the tool will report it"


def g1_skip_gone(rel: str) -> str:
    return f"{escaped(rel)} is not there after the write"


# ---------------------------------------------------------------- notes (N1)


def n1_note_policy_without_id(rel: str) -> str:
    return (
        f"note: {escaped(rel)} lies in the root policy's territory but carries no readable id; it claims"
        " nothing until it does"
    )


def n1_note_policy_id_shared(first: str, second: str, doc_id: str) -> str:
    return (
        f"note: {escaped(first)} and {escaped(second)} both carry id '{echoed(doc_id)}';"
        " the first claims, the second is ignored"
    )


# ---------------------------------------------------------------- configuration failures
# C1 (python3 missing) and C14 (interpreter below the floor) are printed by the POSIX entry
# point and by the Python entry file, which must run on interpreters this package cannot.


def c2_library_missing(distribution: str, requirements_file: str) -> Broken:
    return Broken(
        SharedKey.C2,
        f"{_ns()} needs {distribution}",
        f"run: python3 -m pip install -r '{requirements_file}' — {identity.current().until_installed}",
    )


def c3_git_missing() -> Broken:
    return Broken(SharedKey.C3, f"{_ns()} needs git on PATH", "install git (https://git-scm.com/downloads)")


def c4_dials_invalid_yaml(detail: str) -> Broken:
    return Broken(
        SharedKey.C4,
        f"{DIALS_FILE} is not valid YAML ({escaped(detail)})",
        "repair the YAML at the place the message names; nothing is checked until the file parses",
    )


def c4b_dials_not_mapping() -> Broken:
    return Broken(
        SharedKey.C4B,
        f"{DIALS_FILE} is not a mapping",
        f"the file holds top-level keys: {ROOT_POLICY_KEY}, and {DIALECT_KEY} when the dialect is not"
        f" {DIALECT}, then one namespace per policy or module",
    )


def c5_root_policy_path() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: root_policy must be a repository-relative path",
        "root_policy: <path of the root policy, relative to the repository root>",
    )


def c5_dialect_empty() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: territory_dialect must be a non-empty string",
        f"remove the key, or set territory_dialect: {DIALECT} — the one dialect supported",
    )


def c5_dialect_unsupported(dialect: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: territory_dialect '{echoed(dialect)}' is not supported by {_ns()}"
        f" (supports: {DIALECT})",
        f"set territory_dialect: {DIALECT}, or remove the key",
    )


def c5_namespace_not_mapping(key: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: namespace '{echoed(key)}' must be a mapping",
        f"write it as {echoed(key)}: {{territory: [...]}}",
    )


def c5_own_namespace_not_mapping() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: namespace '{_ns()}' must be a mapping of this module's dials",
        "write this module's dials under it as a mapping, or remove the key",
    )


def c5_territory_pattern(where: str, pattern: str) -> Broken:
    """`where` is the dial's whole path: `{policy id}.territory`, or a module's own dial."""
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {echoed(where)} holds a pattern git would not read as one: '{echoed(pattern)}'",
        "a pattern may not start with '#' (a comment to git) nor contain a line break; "
        "escape a leading # as \\# bare or in single quotes, "
        "as \\\\# in double quotes, and remove a line break",
    )


def c5_unknown_dial(key: str, known: Sequence[str]) -> Broken:
    """`key` is the name given, `known` the names this module reads, in the order it lists them."""
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.{echoed(key)} is no dial of this module",
        "a misspelt dial would be ignored in silence, so none is: write one of " + ", ".join(known),
    )


def c5_territory_shape(key: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {echoed(key)}.territory must be a list of non-empty strings",
        f'write it as {echoed(key)}: {{territory: ["<pattern>", ...]}}',
    )


def c5_severity() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.severity must be block or warn",
        f"under {_ns()}, set severity: block or severity: warn, or remove that line",
    )


def c5_log_dir() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.log_dir must be a repository-relative directory",
        f"under {_ns()}, set log_dir: <a git-ignored directory>, or remove that line",
    )


def c6_root_missing(path: str) -> Broken:
    return Broken(
        SharedKey.C6,
        f"{DIALS_FILE} names root_policy '{escaped(path)}' but no such file exists",
        "create it, or point root_policy at the policy for policies",
    )


def c7_root_without_id(path: str) -> Broken:
    return Broken(
        SharedKey.C7,
        f"root policy '{escaped(path)}' carries no readable id in its envelope",
        "give it the envelope (id, type, title, status); its id names its namespace",
    )


def c8_root_claims_nothing(root_id: str) -> Broken:
    return Broken(
        SharedKey.C8,
        f"root policy '{escaped(root_id)}' claims no territory in {DIALS_FILE}",
        f"write {escaped(root_id)}: {{territory: [<where policies live, including the root itself>]}}"
        " — nothing is governed until then",
    )


def c9_root_outside_own_territory(path: str, territory: Sequence[str], root_id: str) -> Broken:
    return Broken(
        SharedKey.C9,
        f"root policy '{escaped(path)}' lies outside its own territory {patterns(territory)}",
        f"every chain of governance ends at the root; widen {escaped(root_id)}.territory to include it",
    )


def c12_ls_files(root: str, detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not list the files of {escaped(root)}: {escaped(detail)}",
        "repair what git names in the message, then check by hand: git -C <that directory> ls-files",
    )


def c12_init(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git init of the scratch repository failed: {escaped(detail)}",
        "repair what git names in the message; the scratch repository lives in the system's"
        " temporary directory",
    )


def c12_check_ignore(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git check-ignore failed: {escaped(detail)}",
        f"territory patterns must be gitignore syntax; check {DIALS_FILE}",
    )


def c12_input(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"hook input cannot be used ({detail})",
        "as a hook this script reads one tool event, a JSON object, on stdin; to check a repository by"
        " hand run it with --scan [<dir>]",
    )


def c12_no_repo(path: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{escaped(path)} is not inside a git repository",
        "run --scan from a repository, or pass its path",
    )


USAGE = "run with no arguments (hook) or --scan [<dir>]"


def c12_invocation(detail: str, usage: str = USAGE) -> Broken:
    return Broken(SharedKey.C12, f"misinvocation: {echoed(detail)}", usage)


def c12_unreadable(rel: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{escaped(rel)} is listed by git but cannot be read",
        "check that the file can be read: its permissions, or a link that leads nowhere",
    )


def c12_unexpected(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"unexpected failure inside the checker: {echoed(detail)}",
        "this is a defect of the gate, not of the repository; report it, with the traceback below, to"
        f" whoever maintains the plugin — {identity.current().until_fixed}",
    )


def c12_git_failed(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not answer where the repository is: {escaped(detail)}",
        "repair the git setup named in the message (configuration, ownership, installation)",
    )


def c12_git_silent(seconds: float, subcommand: str, directory: str, call: str) -> Broken:
    """A git call in the person's repository gave no answer. `call` is the call as a person runs it
    (`repository.by_hand`); the hung call may be one that reads the index, which a core.fsmonitor hook
    stalls, or any call on a stalled file system."""
    where = shlex.quote(directory)
    return Broken(
        SharedKey.C12,
        f"git gave no answer in {seconds:g} s to git {echoed(subcommand)} in {escaped(directory)}",
        "a git that hangs is a stalled file system or, for a call that reads the index, a core.fsmonitor"
        " hook, set in the repository's or in your own configuration: find the setting with"
        f" git -C {escaped(where)} config --show-origin --get core.fsmonitor (no output means none is set),"
        f" repair or unset it or the file system, and run git -C {escaped(where)} {escaped(call)} by hand"
        " until it answers; the scan, which gives git as long as it takes, checks the same tree",
    )


def c12_git_silent_scratch(seconds: float, subcommand: str, temporary: str) -> Broken:
    """A git call in the scratch repository the gate makes in the system's temporary directory gave no
    answer: nothing there can be run by hand, and no core.fsmonitor hook runs in it."""
    return Broken(
        SharedKey.C12,
        f"git gave no answer in {seconds:g} s to git {echoed(subcommand)} in a scratch folder under"
        f" {escaped(temporary)}",
        f"the system's temporary directory ({escaped(temporary)}; TMPDIR names it) may sit on a stalled"
        " file system, or your git configuration outside any repository may hang git: read it with"
        " git config --global --list --show-origin and git config --system --list --show-origin, repair"
        " the setting, or free that file system or set TMPDIR to a folder on a working one, then run"
        " again; the scan, which gives git as long as it takes, checks the same tree",
    )


def c12_hook_budget(seconds: float, before: str) -> Broken:
    """The hook's one deadline passed while the run still had a wait to make: `before` names the wait it
    ended (`identity.remaining`). A run of many waits, each within its own limit, is bounded by this
    alone; the platform's cut at the handler's timeout says nothing."""
    return Broken(
        SharedKey.C12,
        f"the hook's budget of {seconds:g} s is spent before {echoed(before)}",
        "a hook of many waits, each within its own limit, would otherwise be cut by the platform with no word"
        " of what was slow: run the scan, which has no clock, to check the same tree; where git itself is"
        " slow, look for a core.fsmonitor hook, set in the repository's or in your own configuration, with"
        " git config --show-origin --get core.fsmonitor (no output means none is set), or for a stalled"
        " file system, and repair it",
    )


def c12_scan_path(path: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{escaped(path)} does not exist",
        "pass --scan an existing directory, or none for the current one",
    )


def c12_dials_unreadable(detail: str) -> Broken:
    return Broken(SharedKey.C12, f"{DIALS_FILE} cannot be read ({detail})", "check the file's permissions")


def detail_not_json(error: str) -> str:
    return f"it is not JSON: {error}"


def detail_not_an_object() -> str:
    return "it is JSON, but the top level is not an object"


def detail_tool_input(tool: str, field: str) -> str:
    return f"a {tool} event must carry a string tool_input.{field}"


def detail_nested_too_deeply() -> str:
    return "brackets are nested too deeply to read"


def detail_not_utf8(exc: UnicodeDecodeError) -> str:
    """Where the first byte that is not UTF-8 stands, as a person finds it: line and column, from 1."""
    data = bytes(exc.object)  # bytes or bytearray, as the decoder was handed it
    line = data.count(b"\n", 0, exc.start) + 1
    start = data.rfind(b"\n", 0, exc.start) + 1
    column = len(data[start : exc.start].decode("utf-8")) + 1  # characters, as an editor counts; all valid
    where = f"line {line}, column {column}"
    return f"byte 0x{data[exc.start]:02x} at {where} is not UTF-8; save the file as UTF-8"


def detail_not_a_mapping() -> str:
    return "the block is not a mapping of field: value"


def c13_log_dir_not_ignored(log_dir: str) -> Broken:
    return Broken(
        SharedKey.C13,
        f"{DIALS_FILE}: {_ns()}.log_dir '{escaped(log_dir)}' is not ignored by git",
        "a log inside the working tree must be git-ignored, or every verdict dirties the tree;"
        " add the directory to .gitignore, or remove the key",
    )


def c11_broken_count() -> str:
    return "BROKEN: the check could not run — 0 documents examined"


# ---------------------------------------------------------------- the release of the shared code (C16, C17)
# A module's entry file asks for these before it declares its identity, so they take the namespace and the
# closing clause as parameters and read no identity. The versions are strict major.minor.patch, checked by
# the caller; the namespace is the module's literal; the guide, a path, is escaped.


def _major(version: str) -> str:
    return version.partition(".")[0]


def _clause(until: str) -> str:
    """The module's closing clause behind a fix; a generator's is empty and closes with nothing."""
    return f" — {until}" if until else ""


def c16_shared_too_old(namespace: str, required: str, found: str, guide: str, until: str) -> Broken:
    """The installed release is below the one the module requires: the shared code is too old. A required
    major above the installed one is this too."""
    return Broken(
        SharedKey.C16,
        f"{namespace} needs constitution-layer-kit {required} or a later {_major(required)}.x release,"
        f" found {found}",
        f"install one for python3 as {escaped(guide)} says" + _clause(until),
    )


def c17_module_too_old(namespace: str, required: str, found: str, guide: str, until: str) -> Broken:
    """The module requires a major below the installed one: the module is too old for that major."""
    return Broken(
        SharedKey.C17,
        f"{namespace} was written for constitution-layer-kit {_major(required)}.x, found {found}",
        f"update the plugin to a release written for {_major(found)}.x, or install a {_major(required)}.x"
        f" release of constitution-layer-kit for python3 as {escaped(guide)} says" + _clause(until),
    )
