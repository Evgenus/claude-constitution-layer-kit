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

from collections.abc import Sequence

from . import identity
from .model import DIALECT, DIALS_FILE, Broken, SharedKey


def _ns() -> str:
    return identity.current().namespace


SHOWN_MAX = 80


def shown(value: str) -> str:
    """A value echoed from a document, cut to a length that keeps a message a message: hook
    output is capped by the platform, and a value a page long teaches nothing."""
    return value if len(value) <= SHOWN_MAX else value[:SHOWN_MAX] + f"… [{len(value)} characters]"


def patterns(territory: Sequence[str]) -> str:
    return "[" + ", ".join(f"'{p}'" for p in territory) + "]"


# ---------------------------------------------------------------- field-level parts every gate shares


def field_missing(key: str) -> str:
    return f"{key} missing"


def field_not_string(key: str, yaml_type: str) -> str:
    return f"{key} must be a quoted string (YAML read it as {yaml_type})"


# ---------------------------------------------------------------- verdict and count lines (F9, G1, W1)


def f9_count_hook(findings: int, rel: str) -> str:
    return f"RED: {findings} finding(s) — 1 document examined ({rel})"


def f9_count_scan(findings: int, tail: str) -> str:
    return f"RED: {findings} finding(s) — {tail}"


def g1_green_hook(what: str) -> str:
    return f"GREEN: {_ns()}: 1 document examined, {what}"


def governed_by(policy: str) -> str:
    return f"governed by {policy}"


def g1_green_scan(tail: str) -> str:
    return f"GREEN: {_ns()}: {tail}"


def g1_green_skip(reason: str) -> str:
    return f"GREEN: {_ns()}: 0 documents examined — {reason}"


def w1_warn_note() -> str:
    return (
        f"{_ns()}: severity is warn: the write proceeds, but the finding stands and recurs on"
        " every write until fixed"
    )


def w1_warn_system(headline: str) -> str:
    return f"{_ns()} (warn): {headline}"


# skip reasons (the {reason} of G1)


def g1_skip_no_file(tool: str) -> str:
    return f"tool '{tool}' carries no file to examine"


def g1_skip_not_markdown(path: str) -> str:
    return f"{path} is not a Markdown document"


def g1_skip_no_repo(path: str) -> str:
    return f"{path} is not inside a git repository; the constitution is silent there"


def g1_skip_no_dials(root: str) -> str:
    return f"no {DIALS_FILE} in {root}: nothing is claimed"


def g1_skip_no_root() -> str:
    return f"{DIALS_FILE} has no root_policy: nothing is claimed"


def g1_skip_edit_unappliable(rel: str) -> str:
    return f"the Edit cannot be applied to {rel}; the tool will report it"


def g1_skip_gone(rel: str) -> str:
    return f"{rel} is not there after the write"


# ---------------------------------------------------------------- notes (N1)


def n1_note_policy_without_id(rel: str) -> str:
    return (
        f"note: {rel} lies in the root policy's territory but carries no readable id; it claims"
        " nothing until it does"
    )


def n1_note_policy_id_shared(first: str, second: str, doc_id: str) -> str:
    return f"note: {first} and {second} both carry id '{doc_id}'; the first claims, the second is ignored"


# ---------------------------------------------------------------- configuration failures
# C1 (python3 missing) and C14 (interpreter below the floor) are printed by the POSIX entry
# point and by the Python entry file, which must run on interpreters this package cannot.


def c2_library_missing(distribution: str, requirements_file: str) -> Broken:
    return Broken(
        SharedKey.C2,
        f"{_ns()} needs {distribution}",
        f"run: python3 -m pip install -r '{requirements_file}' — until then Markdown writes pass unchecked",
    )


def c3_git_missing() -> Broken:
    return Broken(SharedKey.C3, f"{_ns()} needs git on PATH", "install git (https://git-scm.com/downloads)")


def c4_dials_invalid_yaml(detail: str) -> Broken:
    return Broken(
        SharedKey.C4,
        f"{DIALS_FILE} is not valid YAML ({detail})",
        "repair the YAML at the place the message names; nothing is checked until the file parses",
    )


def c4b_dials_not_mapping() -> Broken:
    return Broken(
        SharedKey.C4B,
        f"{DIALS_FILE} is not a mapping",
        "the file holds top-level keys: root_policy, then one namespace per policy or module",
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
        f"{DIALS_FILE}: territory_dialect '{dialect}' is not supported by {_ns()} (supports: {DIALECT})",
        f"set territory_dialect: {DIALECT}, or remove the key",
    )


def c5_namespace_not_mapping(key: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: namespace '{key}' must be a mapping",
        f"write it as {key}: {{territory: [...]}}",
    )


def c5_own_namespace_not_mapping() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: namespace '{_ns()}' must be a mapping of this module's dials",
        "write this module's dials under it as a mapping, or remove the key",
    )


def c5_territory_pattern(key: str, pattern: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {key}.territory holds a pattern git would not read as one: {pattern!r}",
        "a pattern may not start with '#' (a comment to git) nor contain a line break; escape or remove it",
    )


def c5_territory_shape(key: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {key}.territory must be a list of non-empty strings",
        f'write it as {key}: {{territory: ["<pattern>", ...]}}',
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
        f"{DIALS_FILE} names root_policy '{path}' but no such file exists",
        "create it, or point root_policy at the policy for policies",
    )


def c7_root_without_id(path: str) -> Broken:
    return Broken(
        SharedKey.C7,
        f"root policy '{path}' carries no readable id in its envelope",
        "give it the envelope (id, type, title, status); its id names its namespace",
    )


def c8_root_claims_nothing(root_id: str) -> Broken:
    return Broken(
        SharedKey.C8,
        f"root policy '{root_id}' claims no territory in {DIALS_FILE}",
        f"write {root_id}: {{territory: [<where policies live, including the root itself>]}}"
        " — nothing is governed until then",
    )


def c9_root_outside_own_territory(path: str, territory: Sequence[str], root_id: str) -> Broken:
    return Broken(
        SharedKey.C9,
        f"root policy '{path}' lies outside its own territory {patterns(territory)}",
        f"every chain of governance ends at the root; widen {root_id}.territory to include it",
    )


def c12_ls_files(root: str, detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not list the files of {root}: {detail}",
        "repair what git names in the message, then check by hand: git -C <that directory> ls-files",
    )


def c12_init(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git init of the scratch repository failed: {detail}",
        "repair what git names in the message; the scratch repository lives in the system's"
        " temporary directory",
    )


def c12_check_ignore(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git check-ignore failed: {detail}",
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
        f"{path} is not inside a git repository",
        "run --scan from a repository, or pass its path",
    )


def c12_invocation(detail: str) -> Broken:
    return Broken(SharedKey.C12, f"misinvocation: {detail}", "run with no arguments (hook) or --scan [<dir>]")


def c12_unreadable(rel: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{rel} is listed by git but cannot be read",
        "check that the file can be read: its permissions, or a link that leads nowhere",
    )


def c12_unexpected(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"unexpected failure inside the checker: {detail}",
        "this is a defect of the gate, not of the repository; report it, with the traceback below, to"
        " whoever maintains the plugin — until it is fixed this check does not run",
    )


def c12_git_failed(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"git could not answer where the repository is: {detail}",
        "repair the git setup named in the message (configuration, ownership, installation)",
    )


def c12_scan_path(path: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"{path} does not exist",
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


def detail_not_a_mapping() -> str:
    return "the block is not a mapping of field: value"


def c13_log_dir_not_ignored(log_dir: str) -> Broken:
    return Broken(
        SharedKey.C13,
        f"{DIALS_FILE}: {_ns()}.log_dir '{log_dir}' is not ignored by git",
        "a log inside the working tree must be git-ignored, or every verdict dirties the tree;"
        " add the directory to .gitignore, or remove the key",
    )


def c11_broken_count() -> str:
    return "BROKEN: the check could not run — 0 documents examined"
