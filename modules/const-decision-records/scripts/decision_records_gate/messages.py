"""Every user-facing text this gate emits, in one place, as functions with typed parameters.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (f1_, c4_, g1_, ...), so a text can be
cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Sequence

from .model import DECLARATION, DIALECT, DIALS_FILE, NAMESPACE, Broken, Finding, Key, Match, MetaType, Status

_ENVELOPE_WHY = "the envelope is the one place a document's authority is declared, and it is read by machines"
_DECLARATION_WHY = (
    "the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it"
)
_FIELD_FIX = (
    "set each named field: id = stable kebab-case (never changed, never reused);"
    " type = current-state (reconciled truth) | task-record (change delta) | non-authoritative (explanation);"
    " title = one line; status = active | inactive"
)
_TYPES = " | ".join(t.value for t in MetaType)
_STATUSES = " | ".join(s.value for s in Status)


def _patterns(patterns: Sequence[str]) -> str:
    return "[" + ", ".join(f"'{p}'" for p in patterns) + "]"


def _matches(matches: Sequence[Match]) -> str:
    return ", ".join(f"{m.policy_id} ({m.pattern})" for m in matches)


# ---------------------------------------------------------------- findings: the envelope


def f1_no_envelope(rel: str) -> Finding:
    return Finding(
        Key.F1,
        f"{rel}: no frontmatter envelope",
        "a governed document declares its authority in its envelope, or sessions guess it",
        "start the file with a YAML block between two '---' lines carrying id: <kebab-id>,"
        f" type: {_TYPES}, title: <one line>, status: {_STATUSES}",
    )


def f2_unterminated(rel: str) -> Finding:
    return Finding(
        Key.F2,
        f"{rel}: frontmatter opened with '---' but never closed",
        "an unclosed envelope is unreadable by machines and by the next session",
        "close the YAML block with a line holding only '---'",
    )


def f3_invalid_yaml(rel: str, detail: str) -> Finding:
    return Finding(
        Key.F3,
        f"{rel}: frontmatter is not valid YAML ({detail})",
        "the envelope is read by machines, so it must parse",
        "repair the YAML between the '---' lines; keep the four fields id, type, title, status",
    )


def f4_invalid_fields(rel: str, errors: Sequence[str]) -> Finding:
    return Finding(
        Key.F4, f"{rel}: envelope field(s) invalid: {'; '.join(errors)}", _ENVELOPE_WHY, _FIELD_FIX
    )


def f5_duplicate_id(rel: str, doc_id: str, other: str) -> Finding:
    return Finding(
        Key.F5,
        f"{rel}: id '{doc_id}' is already carried by {other}",
        "an id is a stable identifier: two documents sharing one break every reference to it",
        "give this document its own id, never a retired one; if this is a move, delete or git mv the"
        " old file first, then write",
    )


def f10_policy_type(rel: str, found_type: str, root_territory: Sequence[str]) -> Finding:
    return Finding(
        Key.F10,
        f"{rel}: lies in the root policy's territory but has type '{found_type}'",
        "a policy is a current-state document, and only policies lie where policies live",
        f"set type: current-state, or move the file out of {_patterns(root_territory)}",
    )


# field-level parts of F4, in reading order


def f4_field_missing(key: str) -> str:
    return f"{key} missing"


def f4_field_not_string(key: str, yaml_type: str) -> str:
    return f"{key} must be a quoted string (YAML read it as {yaml_type})"


def f4_id_not_kebab(shown: str) -> str:
    return f"id '{shown}' is not kebab-case"


def f4_type_not_allowed(shown: str) -> str:
    return f"type '{shown}' not one of {_TYPES}"


def f4_status_not_allowed(shown: str) -> str:
    return f"status '{shown}' not one of {_STATUSES}"


def f4_title_empty() -> str:
    return "title empty"


def f4_title_too_long() -> str:
    return "title longer than 200 characters"


def f4_declaration_not_kebab(shown: str) -> str:
    return f"{DECLARATION} '{shown}' is not a kebab-case policy id"


# ---------------------------------------------------------------- findings: resolution


def f6_no_such_policy(rel: str, declared: str, root_territory: Sequence[str]) -> Finding:
    return Finding(
        Key.F6,
        f"{rel}: declares policy '{declared}' but no policy with that id lies in the root"
        f" policy's territory {_patterns(root_territory)}",
        "a governed document resolves to exactly one governing policy, or its rules are undefined",
        "declare the id of a policy that exists there, or drop the declaration and place the file"
        " in a claimed territory",
    )


def f7_multi_policy(rel: str, matches: Sequence[Match]) -> Finding:
    return Finding(
        Key.F7,
        f"{rel}: matched by {len(matches)} policy territories: {_matches(matches)}",
        "a document resolves to exactly one governing policy, or two rule sets compete",
        f"narrow one territory in {DIALS_FILE} so the patterns no longer overlap; during a move,"
        f" declare the intended one with '{DECLARATION}: <id>' in the envelope while an active"
        " task-record covers it",
    )


def f8_contradiction(
    rel: str, declared: str, match: Match, declared_territory: Sequence[str] | None
) -> Finding:
    """declared_territory is None when the declared id is no policy at all."""
    headline = (
        f"{rel}: declares policy '{declared}' but its path is claimed by"
        f" '{match.policy_id}' ({match.pattern})"
    )
    if declared_territory is None:
        fix = f"remove '{DECLARATION}: {declared}' from the envelope — no policy with that id exists"
    else:
        fix = (
            f"remove '{DECLARATION}: {declared}' from the envelope, or move the file into the territory"
            f" of '{declared}': {_patterns(declared_territory)}"
        )
    return Finding(Key.F8, headline, _DECLARATION_WHY, fix)


def f8b_contradiction_in_overlap(rel: str, declared: str, matches: Sequence[Match]) -> Finding:
    return Finding(
        Key.F8B,
        f"{rel}: declares policy '{declared}' but its path is claimed by {_matches(matches)}",
        _DECLARATION_WHY,
        "declare one of the policies that claim the path, or remove the declaration and narrow"
        f" the territories in {DIALS_FILE}",
    )


# ---------------------------------------------------------------- findings: the root policy itself


def f14_root_breaks_governance(rel: str, broken: Broken) -> Finding:
    """A write to the root policy that would leave the repository ungovernable is blocked
    as a finding: as a configuration failure it would be non-blocking and the damage would land."""
    return Finding(
        Key.F14,
        f"{rel}: as written, {broken.headline}",
        "every chain of governance ends at the root policy; a write that breaks it ungoverns the repository",
        broken.fix,
    )


def f11_root_unreadable(rel: str, detail: str) -> Finding:
    return Finding(
        Key.F11,
        f"{rel}: the root policy has no readable envelope ({detail})",
        "the root policy's id names the namespace where policies live; without it nothing is governed",
        "keep the YAML block between two '---' lines with id, type: current-state, title, status: active",
    )


def f12_root_type(rel: str, found_type: str) -> Finding:
    return Finding(
        Key.F12,
        f"{rel}: the root policy has type '{found_type}'",
        "a policy is a current-state document, and the root is the policy for policies",
        "set type: current-state",
    )


def f13_root_id_orphaned(rel: str, doc_id: str) -> Finding:
    return Finding(
        Key.F13,
        f"{rel}: the root policy's id '{doc_id}' has no territory under that id in {DIALS_FILE}",
        "the root's namespace is where policies live; changing the id orphans every policy",
        f"keep the id that has the namespace, or rename the namespace in {DIALS_FILE} in the same change",
    )


# ---------------------------------------------------------------- verdict and count lines (F9, G1, W1)


def f9_count_hook(findings: int, rel: str) -> str:
    return f"RED: {findings} finding(s) — 1 document examined ({rel})"


def f9_scan_tail(examined: int, scanned: int, policies: int) -> str:
    return (
        f"{examined} governed document(s) examined, {scanned} Markdown file(s) scanned, {policies} policies"
    )


def f9_count_scan(findings: int, tail: str) -> str:
    return f"RED: {findings} finding(s) — {tail}"


def g1_green_hook(policy: str) -> str:
    return f"GREEN: {NAMESPACE}: 1 document examined, governed by {policy}"


def g1_green_scan(tail: str) -> str:
    return f"GREEN: {NAMESPACE}: {tail}"


def g1_green_skip(reason: str) -> str:
    return f"GREEN: {NAMESPACE}: 0 documents examined — {reason}"


def w1_warn_note() -> str:
    return (
        f"{NAMESPACE}: severity is warn: the write proceeds, but the finding stands and recurs on"
        " every write until fixed"
    )


def w1_warn_system(headline: str) -> str:
    return f"{NAMESPACE} (warn): {headline}"


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


def g1_skip_outside_territory(rel: str) -> str:
    return f"{rel} is outside claimed territory"


def g1_skip_void_territory(rel: str, namespaces: Sequence[str]) -> str:
    listed = ", ".join(f"'{n}'" for n in namespaces)
    if len(namespaces) == 1:
        return (
            f"{rel} lies only in the territory of namespace {listed}, which has no policy document"
            " behind it and so claims nothing"
        )
    return (
        f"{rel} lies only in the territories of namespaces {listed}, none of which has a policy"
        " document behind it, so nothing is claimed"
    )


# ---------------------------------------------------------------- notes (N1)


def n1_note_policy_without_id(rel: str) -> str:
    return (
        f"note: {rel} lies in the root policy's territory but carries no readable id; it claims"
        " nothing until it does"
    )


def n1_note_policy_id_shared(first: str, second: str, doc_id: str) -> str:
    return f"note: {first} and {second} both carry id '{doc_id}'; the first claims, the second is ignored"


def n1_note_void_namespace(name: str) -> str:
    return (
        f"note: namespace '{name}' declares a territory but no policy with id '{name}' lies in the root"
        " policy's territory; it claims nothing until that policy exists"
    )


# ---------------------------------------------------------------- configuration failures
# C1 (python3 missing) and C14 (interpreter below the floor) are printed by the POSIX entry
# point and by the Python entry file, which must run on interpreters this package cannot.


def c2_library_missing(distribution: str, requirements_file: str) -> Broken:
    return Broken(
        Key.C2,
        f"{NAMESPACE} needs {distribution}",
        f"run: python3 -m pip install -r {requirements_file} — until then Markdown writes pass unchecked",
    )


def c3_git_missing() -> Broken:
    return Broken(Key.C3, f"{NAMESPACE} needs git on PATH", "install git (https://git-scm.com/downloads)")


def c4_dials_invalid_yaml(detail: str) -> Broken:
    return Broken(
        Key.C4,
        f"{DIALS_FILE} is not valid YAML ({detail})",
        "fix the file; nothing is checked until it parses",
    )


def c4b_dials_not_mapping() -> Broken:
    return Broken(
        Key.C4B,
        f"{DIALS_FILE} is not a mapping",
        "the file holds top-level keys: root_policy, then one namespace per policy or module",
    )


def c5_root_policy_path() -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: root_policy must be a repository-relative path",
        "root_policy: <path of the root policy, relative to the repository root>",
    )


def c5_dialect_empty() -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: territory_dialect must be a non-empty string",
        "remove the key (default gitignore) or name a dialect",
    )


def c5_dialect_unsupported(dialect: str) -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: territory_dialect '{dialect}' is not supported by {NAMESPACE} (supports: {DIALECT})",
        f"set territory_dialect: {DIALECT}, or remove the key",
    )


def c5_namespace_not_mapping(key: str) -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: namespace '{key}' must be a mapping",
        f"write it as {key}: {{territory: [...]}}",
    )


def c5_own_namespace_not_mapping() -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: namespace '{NAMESPACE}' must be a mapping of this module's dials",
        f"write {NAMESPACE}: {{severity: block}}, or remove the key",
    )


def c5_territory_pattern(key: str, pattern: str) -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: {key}.territory holds a pattern git would not read as one: {pattern!r}",
        "a pattern may not start with '#' (a comment to git) nor contain a line break; escape or remove it",
    )


def c5_territory_shape(key: str) -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: {key}.territory must be a list of non-empty strings",
        f'write it as {key}: {{territory: ["<pattern>", ...]}}',
    )


def c5_severity() -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: {NAMESPACE}.severity must be block or warn",
        f"write {NAMESPACE}: {{severity: block}} or {{severity: warn}}",
    )


def c5_log_dir() -> Broken:
    return Broken(
        Key.C5,
        f"{DIALS_FILE}: {NAMESPACE}.log_dir must be a repository-relative directory",
        f"write {NAMESPACE}: {{log_dir: <a git-ignored directory>}}, or remove the key",
    )


def c6_root_missing(path: str) -> Broken:
    return Broken(
        Key.C6,
        f"{DIALS_FILE} names root_policy '{path}' but no such file exists",
        "create it, or point root_policy at the policy for policies",
    )


def c7_root_without_id(path: str) -> Broken:
    return Broken(
        Key.C7,
        f"root policy '{path}' carries no readable id in its envelope",
        "give it the envelope (id, type, title, status); its id names its namespace",
    )


def c8_root_claims_nothing(root_id: str) -> Broken:
    return Broken(
        Key.C8,
        f"root policy '{root_id}' claims no territory in {DIALS_FILE}",
        f"write {root_id}: {{territory: [<where policies live, including the root itself>]}}"
        " — nothing is governed until then",
    )


def c9_root_outside_own_territory(path: str, territory: Sequence[str], root_id: str) -> Broken:
    return Broken(
        Key.C9,
        f"root policy '{path}' lies outside its own territory {_patterns(territory)}",
        f"every chain of governance ends at the root; widen {root_id}.territory to include it",
    )


def c12_ls_files(root: str) -> Broken:
    return Broken(Key.C12, f"git ls-files failed in {root}", "run the check from inside a git repository")


def c12_init() -> Broken:
    return Broken(Key.C12, "git init of the scratch repository failed", "check that git works: git --version")


def c12_check_ignore(detail: str) -> Broken:
    return Broken(
        Key.C12,
        f"git check-ignore failed: {detail}",
        f"territory patterns must be gitignore syntax; check {DIALS_FILE}",
    )


def c12_input(detail: str) -> Broken:
    return Broken(
        Key.C12,
        f"hook input is not a JSON object ({detail})",
        "this script reads a PreToolUse event on stdin",
    )


def c12_no_repo(path: str) -> Broken:
    return Broken(
        Key.C12, f"{path} is not inside a git repository", "run --scan from a repository, or pass its path"
    )


def c12_invocation(detail: str) -> Broken:
    return Broken(Key.C12, f"misinvocation: {detail}", "run with no arguments (hook) or --scan [<dir>]")


def c12_unreadable(rel: str) -> Broken:
    return Broken(
        Key.C12, f"{rel} is listed by git but cannot be read", "check the file's permissions and encoding"
    )


def c12_unexpected(detail: str) -> Broken:
    return Broken(
        Key.C12,
        f"unexpected failure inside the checker: {detail}",
        "this is a defect of the gate, not of the repository; report it with the traceback below",
    )


def c12_git_failed(detail: str) -> Broken:
    return Broken(
        Key.C12,
        f"git could not answer where the repository is: {detail}",
        "repair the git setup named in the message (configuration, ownership, installation)",
    )


def c12_scan_path(path: str) -> Broken:
    return Broken(
        Key.C12, f"{path} does not exist", "pass --scan an existing directory, or none for the current one"
    )


def c12_dials_unreadable(detail: str) -> Broken:
    return Broken(Key.C12, f"{DIALS_FILE} cannot be read ({detail})", "check the file's permissions")


def detail_not_an_object() -> str:
    return "the top level is not an object"


def detail_tool_input(tool: str, field: str) -> str:
    return f"a {tool} event must carry a string tool_input.{field}"


def detail_not_a_mapping() -> str:
    return "the block is not a mapping of field: value"


def c13_log_dir_not_ignored(log_dir: str) -> Broken:
    return Broken(
        Key.C13,
        f"{DIALS_FILE}: {NAMESPACE}.log_dir '{log_dir}' is not ignored by git",
        "a log inside the working tree must be git-ignored, or every verdict dirties the tree;"
        " add the directory to .gitignore, or remove the key",
    )


def c11_broken_count() -> str:
    return "BROKEN: the check could not run — 0 documents examined"
