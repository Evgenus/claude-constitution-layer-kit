---
id: dec-0083-handle-forms-held-by-a-kit-check
type: task-record
title: 'Kit checks hold the forms of handles: a ruling citation, a module key, a record order and table key'
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Kit checks hold the forms of handles: a ruling citation, a module key, a record order and table key


## Context

A handle audit on 2026-10-11 found handles that collide or name nothing, and the pull requests of that day fixed them by hand. Four classes had no check, so the same slips could come back.

- **A citation of a ruling.** [Rule 2 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r2) asks a citation of a ruling from another document to link the ruling's anchor. Its rule 6 left that to review, as R3 of [dec-0081-rulings-carry-anchors](dec-0081-rulings-carry-anchors.md#r3) ruled. Twelve such citations were missed by hand in two rounds.
- **A module's message keys.** Modules reused keys of the shared message table of [§3 of the shared gate code](../../shared/GATE.md#g3) with a meaning of their own: F10, N1, H1 and S1.
- **One prefix per kind.** [Rule 8 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r8) asks one prefix per kind of handle in a module document; a message key L1 stood beside a live item L1. Its rule 12 left handles to review.
- **A record's order and its table keys.** [Rule 10 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r10) asks handles in order, contiguous and unique, tables included, from [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md) on, as R1 of [dec-0082-handle-migration-in-records](dec-0082-handle-migration-in-records.md#r1) set. `scripts/check-carry-lists.py` held only that no bold ruling handle opens two items.

Each check changes what a policy says is review, so each is a `process` change. No check finds anything in the tree today: each guards against the next slip.

## 1. How the four checks land

- **A. One record and one pull request.** One record rules on the four checks, and one branch holds one commit and one self-test per check.
  - **Pros:** one carry audit instead of four; rule 6 of plc-0004 and rule 12 of plc-0006 change once; one yes.
  - **Cons:** a larger pull request; a problem in one check holds back the other three.
- **B. One record, four pull requests,** the later checks carried "pending" until they land.
  - **Pros:** each check gets its own small pull request.
  - **Cons:** "pending" needs a task-record to hold the work; the policies change in several steps, each audited again.
- **C. Four records, four pull requests.**
  - **Pros:** each ruling stands alone.
  - **Cons:** four carry audits; four yeses; the same rules edited four times.

The session recommended A: the four checks share the same two enforcement rules, and the cost is in the audit, not in the code. The decider chose A in chat on 2026-10-11.

<a id="r1"></a>**R1.** The four checks land as one change, under this record.

## 2. Rulings taken by the session

What each check reads and holds followed from the rule it serves; no real choice was left. The session ruled the details below, and the decider sees them at the yes. The list of R6 grew from six keys to nine while the check was built: three modules state their own closing clause under C1, C14 and C15, a part the shared rows name.

<a id="r2"></a>**R2.** The kit's `scripts/check-handle-forms.py` holds that a citation of a ruling from another document links the ruling's anchor, a list or a range of rulings linking the first. It reads every Markdown file git lists, save a research comparison under `docs/research/`, frozen or not, a section titled "Carry list", fenced and indented code, code spans and HTML comments. A frozen comparison keeps the form it was frozen with; in one not yet frozen, review holds the anchor. It reads three forms: rulings followed by " of " and a link to a record; a link to a record followed by a ruling; a ruling followed by " of " and a record's bare id. A handle after the word "key", "message" or "row", singular or plural, is a qualified key of another kind and no ruling. A handle with a suffix letter, a record's own ruling and a citation that names its record indirectly, "that record's R3", are review.

<a id="r3"></a>**R3.** R2 reverses the part of R3 of [dec-0081-rulings-carry-anchors](dec-0081-rulings-carry-anchors.md#r3) that left a citation's anchor to review.

<a id="r4"></a>**R4.** From dec-0039 on, `scripts/check-carry-lists.py` holds that the bold ruling handles run R1, R2, … in document order with no gap, outside fenced blocks and before the carry list. `scripts/check-handle-forms.py` holds that no table row of such a record has a first cell whose first handle has the form of a ruling handle, `R<n>`: alone, bold, in a code span, in a range or a list, or followed by other words. A handle qualified as another document's key, "R1 of the module" or after "message", "key" or "row", is no ruling. The order, the contiguity and the uniqueness of other handles, and the order and the contiguity of the handles of an earlier record, stay review.

<a id="r5"></a>**R5.** R4 narrows what R1 of [dec-0082-handle-migration-in-records](dec-0082-handle-migration-in-records.md#r1) left to review: the order and the contiguity of the bold ruling handles, and a table key of the form of a ruling handle.

<a id="r6"></a>**R6.** A module's own message table takes a key of the shared table only to state its part of that message: G1, F9, F10, C1, C2, C5, C12, C14 and C15. The family of a key is its letters and its first number. `scripts/check-handle-forms.py` holds that no key of the module's table has a family of the shared table outside that list, sub-keys included. Whether a module's row under an allowed key states its part of the message is review.

<a id="r7"></a>**R7.** `scripts/check-handle-forms.py` holds rule 8 of plc-0006 over three kinds of a module document: the message keys of its message table ([template §6](../../module-template/MODULE.md#t6)), the rows of its enforcement table ([template §9](../../module-template/MODULE.md#t9)) and its acceptance items ([template §10](../../module-template/MODULE.md#t10)). A prefix, the capital letters before a handle's number, used by two of these kinds is a finding. The acceptance items are one kind, since a live, review or kit-check item may continue the module's own numbering. The advisory rules, `X-a`, are another prefix and are not read. Rule 8 fixes `E<n>` for the enforcement rows and T, S, L or V for the items, and leaves the message keys to the module. So the fix line moves the kind that uses a prefix rule 8 gives another kind, and a fixed kind that uses a prefix no kind owns. Where the message keys use L, the live, review and kit-check items take V, as rule 8 says, and the message keys keep L.

<a id="r8"></a>**R8.** `scripts/check-handle-forms.py` is the entry `handle-forms` of the gate group, in the job `kit`, with `--self-test` as its fixture. It is kit tooling, never shipped in a module.

<a id="r9"></a>**R9.** R2 narrows R3 of [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md#r3), that a frozen document is never taken out of any gate's territory, and R2 of [dec-0051-module-citation-rule-in-the-guide](dec-0051-module-citation-rule-in-the-guide.md#r2), which named `scripts/check-module-links.py` the one check that reads no comparison: `scripts/check-handle-forms.py` is a second.

## Applied

The commits before the one that creates this record built the checks: R4's order in `scripts/check-carry-lists.py`, then `scripts/check-handle-forms.py` with R2, R6 and its paragraph in [§3 of the shared gate code](../../shared/GATE.md#g3a), then R7 and R4's table keys, each followed by the fixes of its verifier. The commit that creates this record states R2, R4 and R8 in rule 6 of plc-0004, R6 and R7 in rule 12 of plc-0006, and R2 and R8 in CLAUDE.md. The record is born `inactive`. The rounds of its carry audit corrected the record and the documents in place before the yes, among them: R2 stated in rule 10 of plc-0005 too, R9 added, the fix line of R7 brought to the V clause of rule 8 of plc-0006, and the scope of R2 and R4 stated in rule 6 of plc-0004 as the scripts hold it.

## Carry list

1. R1 — history only: how the change landed.
2. R2 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6), rule 6; [plc-0005-research](../policies/plc-0005-research.md#r10), rule 10; [`scripts/check-handle-forms.py`](../../scripts/check-handle-forms.py), `ruling_citations`; [CLAUDE.md](../../CLAUDE.md#references), the reference rule.
3. R3 — history only: the reversal of part of an earlier ruling.
4. R4 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6), rule 6; [`scripts/check-carry-lists.py`](../../scripts/check-carry-lists.py), `check_order`; [`scripts/check-handle-forms.py`](../../scripts/check-handle-forms.py), `record_table_keys`.
5. R5 — history only: the narrowing of an earlier ruling.
6. R6 — [the shared gate code](../../shared/GATE.md#g3a), the paragraph on a module's keys; [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12), rule 12; [`scripts/check-handle-forms.py`](../../scripts/check-handle-forms.py), `module_message_keys`.
7. R7 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12), rule 12; [`scripts/check-handle-forms.py`](../../scripts/check-handle-forms.py), `module_handle_prefixes`.
8. R8 — [`scripts/gate-list.sh`](../../scripts/gate-list.sh), the gate group; [CLAUDE.md](../../CLAUDE.md#references), the reference rule.
9. R9 — history only: the narrowing of two earlier rulings.
