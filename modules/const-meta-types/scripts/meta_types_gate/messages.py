"""The texts of this module's own findings, skips, notes and dial failure, as functions with
typed parameters; the texts every gate shares live in the shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (f1_, g1_, n2_, c5_, ...), so a text can
be cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Sequence

from const_gate import identity
from const_gate.messages import echoed, escaped, patterns
from const_gate.model import DECLARATION, DIALS_FILE, Broken, Finding, Match, MetaType, Status

from .model import TITLE_MAX, Key

_ENVELOPE_WHY = "the envelope is the one place a document's authority is declared, and it is read by machines"
_DECLARATION_WHY = (
    "the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it"
)
_TYPES = " | ".join(t.value for t in MetaType)
_STATUSES = " | ".join(s.value for s in Status)


def _ns() -> str:
    return identity.current().namespace


# The fix of F4 names only the fields its list names: each fragment under the key that opens
# every field-level part below and in the shared messages, in the envelope's reading order.
_FIELD_FIXES = {
    "id": "id = stable kebab-case (never changed, never reused)",
    "type": (
        "type = current-state (reconciled truth) | task-record (change delta) | non-authoritative"
        " (explanation)"
    ),
    "title": f"title = one line of at most {TITLE_MAX} characters",
    "status": f"status = {_STATUSES}",
    DECLARATION: f"{DECLARATION} = the kebab-case id of the governing policy, or no such line",
}


def _matches(matches: Sequence[Match]) -> str:
    return ", ".join(f"{echoed(m.policy_id)} ({echoed(m.pattern)})" for m in matches)


# ---------------------------------------------------------------- findings: the envelope


def f1_no_envelope(rel: str) -> Finding:
    return Finding(
        Key.F1,
        f"{escaped(rel)}: no frontmatter envelope",
        "a governed document declares its authority in its envelope, or sessions guess it",
        "start the file with a YAML block between two '---' lines carrying at least id: <kebab-id>,"
        f" type: {_TYPES}, title: <one line>, status: {_STATUSES} — the fields every governed"
        " document carries; its kind may add fields of its own",
    )


def f2_unterminated(rel: str) -> Finding:
    return Finding(
        Key.F2,
        f"{escaped(rel)}: frontmatter opened with '---' but never closed",
        "an unclosed envelope is unreadable by machines and by the next session",
        "close the YAML block with a line holding only '---'",
    )


def f3_invalid_yaml(rel: str, detail: str) -> Finding:
    return Finding(
        Key.F3,
        f"{escaped(rel)}: frontmatter is not valid YAML ({escaped(detail)})",
        "the envelope is read by machines, so it must parse",
        "repair the YAML between the '---' lines; keep at least the four fields id, type, title, status",
    )


def f4_invalid_fields(rel: str, errors: Sequence[str]) -> Finding:
    """Each error opens with its field's key; the fix names those fields and no other."""
    named = {error.split(" ", 1)[0] for error in errors}
    fragments = [fix for key, fix in _FIELD_FIXES.items() if key in named] or list(_FIELD_FIXES.values())
    return Finding(
        Key.F4,
        f"{escaped(rel)}: envelope field(s) invalid: {'; '.join(errors)}",
        _ENVELOPE_WHY,
        f"set {'each named field' if len(fragments) > 1 else 'the named field'}: {'; '.join(fragments)}",
    )


def f5_duplicate_id(rel: str, doc_id: str, other: str) -> Finding:
    return Finding(
        Key.F5,
        f"{escaped(rel)}: id '{echoed(doc_id)}' is already carried by {escaped(other)}",
        "an id is a stable identifier: two documents sharing one break every reference to it",
        "give this document its own id, never a retired one; if this is a move, delete or git mv the"
        " old file first, then write",
    )


def f15_policy_type(rel: str, found_type: str, root_territory: Sequence[str]) -> Finding:
    return Finding(
        Key.F15,
        f"{escaped(rel)}: lies in the root policy's territory but has type '{found_type}'",
        "a policy is a current-state document, and only policies lie where policies live",
        f"set type: current-state, or move the file out of {patterns(root_territory)}",
    )


# ---------------------------------------------------------------- findings: resolution


def f6_no_such_policy(rel: str, declared: str, root_territory: Sequence[str]) -> Finding:
    return Finding(
        Key.F6,
        f"{escaped(rel)}: declares policy '{echoed(declared)}' but no policy with that id lies in the root"
        f" policy's territory {patterns(root_territory)}",
        "a governed document resolves to exactly one governing policy, or its rules are undefined",
        "declare the id of a policy that exists there, or drop the declaration and place the file"
        " in a claimed territory",
    )


def f7_multi_policy(rel: str, matches: Sequence[Match]) -> Finding:
    return Finding(
        Key.F7,
        f"{escaped(rel)}: matched by {len(matches)} policy territories: {_matches(matches)}",
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
        f"{escaped(rel)}: declares policy '{echoed(declared)}' but its path is claimed by"
        f" '{echoed(match.policy_id)}' ({echoed(match.pattern)})"
    )
    if declared_territory is None:
        fix = f"remove '{DECLARATION}: {echoed(declared)}' from the envelope — no policy with that id exists"
    else:
        fix = (
            f"remove '{DECLARATION}: {echoed(declared)}' from the envelope, or move the file into the"
            f" territory of '{echoed(declared)}': {patterns(declared_territory)}"
        )
    return Finding(Key.F8, headline, _DECLARATION_WHY, fix)


def f8b_contradiction_in_overlap(rel: str, declared: str, matches: Sequence[Match]) -> Finding:
    return Finding(
        Key.F8B,
        f"{escaped(rel)}: declares policy '{echoed(declared)}' but its path is claimed by"
        f" {_matches(matches)}",
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
        f"{escaped(rel)}: as written, {broken.headline}",
        "every chain of governance ends at the root policy; a write that breaks it ungoverns the repository",
        broken.fix,
    )


def f11_root_unreadable(rel: str, detail: str) -> Finding:
    return Finding(
        Key.F11,
        f"{escaped(rel)}: the root policy has no readable envelope ({escaped(detail)})",
        "the root policy's id names the namespace where policies live; without it nothing is governed",
        "keep the YAML block between two '---' lines with id, type: current-state, title, status: active",
    )


def f11_detail_no_envelope() -> str:
    return "the file does not start with a '---' line"


def f11_detail_unterminated() -> str:
    return "opened with '---' but never closed"


def f12_root_type(rel: str, found_type: str) -> Finding:
    return Finding(
        Key.F12,
        f"{escaped(rel)}: the root policy has type '{found_type}'",
        "a policy is a current-state document, and the root is the policy for policies",
        "set type: current-state",
    )


def f13_root_id_orphaned(rel: str, doc_id: str) -> Finding:
    return Finding(
        Key.F13,
        f"{escaped(rel)}: the root policy's id '{echoed(doc_id)}' has no territory under that id in"
        f" {DIALS_FILE}",
        "the root's namespace is where policies live; changing the id orphans every policy",
        f"keep the id that has the namespace, or rename the namespace in {DIALS_FILE} in the same change",
    )


def f9_scan_tail(examined: int, scanned: int, policies: int) -> str:
    return (
        f"{examined} governed document(s) examined, {scanned} Markdown file(s) scanned, {policies} policies"
    )


def g1_skip_outside_territory(rel: str) -> str:
    return f"{escaped(rel)} is outside claimed territory"


def g1_skip_void_territory(rel: str, namespaces: Sequence[str]) -> str:
    listed = ", ".join(f"'{echoed(n)}'" for n in namespaces)
    if len(namespaces) == 1:
        return (
            f"{escaped(rel)} lies only in the territory of namespace {listed}, which has no policy document"
            " behind it and so claims nothing"
        )
    return (
        f"{escaped(rel)} lies only in the territories of namespaces {listed}, none of which has a policy"
        " document behind it, so nothing is claimed"
    )


def n2_note_void_namespace(name: str) -> str:
    return (
        f"note: namespace '{echoed(name)}' declares a territory but no policy with id '{echoed(name)}'"
        " lies in the root policy's territory; it claims nothing until that policy exists"
    )


# ---------------------------------------------------------------- the pointer to the governing policy (N3)


def n3_policy_pointer(policy_path: str, anchor: str | None) -> str:
    """Advisory, on a green write in claimed territory, once per session for the policy: the policy's
    document to read, and the rule that says what review holds. `anchor` is the explicit anchor of
    the policy's rule named Enforcement, whose shape the pattern that found it fixed; None where the
    policy has no such rule, and the line names the document alone."""
    line = (
        f"{_ns()} (advisory): this document is governed by {escaped(policy_path)} — read its rules"
        " before further edits"
    )
    if anchor is None:
        return line
    return f"{line}; what review holds is its Enforcement rule (#{anchor})"


# ---------------------------------------------------------------- this module's dial failure


# field-level parts of F4, beside the two every gate shares, in reading order


def f4_id_not_kebab(value: str) -> str:
    return f"id '{echoed(value)}' is not kebab-case"


def f4_type_not_allowed(value: str) -> str:
    return f"type '{echoed(value)}' not one of {_TYPES}"


def f4_status_not_allowed(value: str) -> str:
    return f"status '{echoed(value)}' not one of {_STATUSES}"


def f4_title_empty() -> str:
    return "title empty"


def f4_title_too_long() -> str:
    return f"title longer than {TITLE_MAX} characters"


def f4_declaration_not_kebab(value: str) -> str:
    return f"{DECLARATION} '{echoed(value)}' is not a kebab-case policy id"
