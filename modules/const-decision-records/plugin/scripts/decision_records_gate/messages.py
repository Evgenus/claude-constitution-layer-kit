"""The texts of this module's own findings, skips, notes and dial failures, as functions
with typed parameters; the texts every gate shares live in the shared package's messages
module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (r1_, g1_, n2_, c5_, ...), so a text can
be cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Sequence

from constitution_layer_kit import identity
from constitution_layer_kit.messages import echoed, escaped
from constitution_layer_kit.model import DIALS_FILE, Broken, EnvelopeState, Finding, SharedKey, Status

from .model import Key, Stakes

_STATUSES = " | ".join(s.value for s in Status)


def _ns() -> str:
    return identity.current().namespace


# ---------------------------------------------------------------- findings: the decision record

_STAKES = " | ".join(level.value for level in Stakes)


def r1_no_readable_envelope(rel: str, state: EnvelopeState, yaml_detail: str = "") -> Finding:
    """state is NONE, UNTERMINATED or INVALID; yaml_detail says what YAML could not read."""
    carries = (
        f"id: <kebab-id>, type: task-record, title: <one line>, status: {_STATUSES}, stakes: {_STAKES},"
        " decider: <person or role>"
    )
    match state:
        case EnvelopeState.UNTERMINATED:
            detail = "opened with '---' but never closed"
            fix = f"close the YAML block with a line holding only '---'; the block carries {carries}"
        case EnvelopeState.INVALID:
            detail = f"the block between the '---' lines cannot be read: {escaped(yaml_detail)}"
            fix = f"repair the YAML between the '---' lines; the block carries {carries}"
        case _:
            detail = "the file does not start with a '---' line"
            fix = f"start the file with a YAML block between two '---' lines carrying {carries}"
    return Finding(
        Key.R1,
        f"{escaped(rel)}: a decision record with no readable envelope ({detail})",
        "a record declares its stakes and its decider in the envelope: without them the ruling has no"
        " price and nobody accountable",
        fix,
    )


def r2_invalid_fields(rel: str, errors: Sequence[str]) -> Finding:
    return Finding(
        Key.R2,
        f"{escaped(rel)}: decision-record field(s) invalid: {'; '.join(errors)}",
        "a decision record is a task-record whose envelope adds the stakes, which set the ceremony the"
        " ruling gets, and the decider, who is accountable for it; git can derive neither",
        "set each named field: type = task-record (a record is a change delta); stakes = process"
        " (harness, policy or procedure) | product (user-visible behaviour) | architecture (structural,"
        " hard to reverse); decider = the person or role who made the choice, a non-empty string",
    )


def r3_routine_record(rel: str) -> Finding:
    return Finding(
        Key.R3,
        f"{escaped(rel)}: stakes 'routine' — a routine call never produces a record",
        "ceremony scales with stakes: a call that is cheap to revert is noted in the commit message,"
        " and a record for it is ritual",
        "write no record: put the note in the commit message, and delete this file if it already"
        f" exists; or, if the ruling is not cheap to revert, set stakes: {_STAKES}",
    )


# field-level parts of R2, beside the two every gate shares


def r2_type_not_task_record(value: str) -> str:
    return f"type '{echoed(value)}' is not task-record"


def r2_stakes_not_allowed(value: str) -> str:
    return f"stakes '{echoed(value)}' not one of {_STAKES}"


def r2_decider_empty() -> str:
    return "decider empty"


# ---------------------------------------------------------------- count line, skips, note


def f9_scan_tail(records: int, scanned: int, record_policies: int) -> str:
    return (
        f"{records} decision record(s) examined, {scanned} Markdown file(s) scanned,"
        f" {record_policies} record policy(ies)"
    )


def g1_skip_no_record_policies() -> str:
    return (
        f"{_ns()}.record_policies names no policy, so no document is known to be a decision"
        f" record — to switch the check on, write {_ns()}: {{record_policies: [<id of the policy"
        f" that governs decision records>]}} in {DIALS_FILE}"
    )


def g1_skip_not_a_record(rel: str, record_policies: Sequence[str]) -> str:
    policies = ", ".join(echoed(p) for p in record_policies)
    return f"{escaped(rel)} is not governed by a record policy ({policies})"


def n2_note_dangling_record_policy(policy_id: str) -> str:
    return (
        f"note: {_ns()}.record_policies names '{echoed(policy_id)}', but no policy with that id lies in the"
        " root policy's territory; it claims nothing until that policy exists"
    )


def n3_note_record_policy_claims_nothing(policy_id: str, path: str) -> str:
    return (
        f"note: {_ns()}.record_policies names '{escaped(policy_id)}' ({escaped(path)}), whose namespace"
        f" declares no territory — it governs no document until {DIALS_FILE} holds {escaped(policy_id)}:"
        " {territory: [<patterns of the paths where decision records live>]}"
    )


# ---------------------------------------------------------------- session start: the visible zero (Z1)


def z1_empty() -> str:
    return f"{_ns()}: no document is examined — {_ns()}.record_policies is an empty list in {DIALS_FILE}"


def z1_no_dials(root: str) -> str:
    return (
        f"{_ns()}: no {DIALS_FILE} in {escaped(root)} — the record gate examines nothing there until the file"
        f" names a record policy in {_ns()}.record_policies"
    )


def z1_no_repo(cwd: str) -> str:
    return f"{_ns()}: {escaped(cwd)} is not inside a git repository — the record gate examines nothing there"


def z1_prefix() -> str:
    return _ns()


def z1_could_not_run() -> str:
    return "BROKEN: the session-start line could not be printed — the gate's state is unknown"


# ---------------------------------------------------------------- this module's dial failures


def c5_record_policies() -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.record_policies must be a list of kebab-case policy ids",
        f"write {_ns()}: {{record_policies: [<id of the policy that governs decision records>]}},"
        " or remove the key",
    )


def c5_record_policy_is_root(root_id: str) -> Broken:
    return Broken(
        SharedKey.C5,
        f"{DIALS_FILE}: {_ns()}.record_policies names the root policy '{echoed(root_id)}', which governs"
        " policies, never decision records",
        "name the policy that governs decision records instead; if there is none yet, write that"
        " policy first",
    )
