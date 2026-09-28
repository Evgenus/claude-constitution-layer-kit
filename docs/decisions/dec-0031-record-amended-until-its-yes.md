---
id: dec-0031-record-amended-until-its-yes
type: task-record
title: Kernel §5 — until the yes or the review its stakes ask for, whatever examines a record may still correct it in place
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Until its yes, a record may be amended in place

## Context

[dec-0030-carry-audit-mandatory](dec-0030-carry-audit-mandatory.md) put an audit between a record's first commit and its yes: the readers are pinned to a commit that already holds the record, so whatever they find is fixed afterwards. Some of what they find is wrong in the record itself — a ruling item that contradicts the kernel, an item nobody gave a handle, a carry list that overstates a home. That record was amended in place by each of the three rounds of its audit, and [dec-0029-catalogs-module-rulings](dec-0029-catalogs-module-rulings.md) had been amended twice the same way before any rule spoke of it.

[Kernel §5](../../kernel/CONVENTIONS.md#k5) said a decision is operative when committed, that reversing a ruling is a new record and never an in-place edit, and named one edit applied in place: the reference-form migration. The second round of that audit wrote into the decision-record policy that "until its yes a record is a proposal"; the third round's reader called it what it was — a carve-out from the kernel, written into a policy, on a record whose status already said applied.

## Options

- **A. A record under audit is `active`.** It lands `active`, the audit's fixes amend it while active, the commit that names the yes sets it `inactive`.
  - **Pros:** no kernel change — the kernel already calls a record `active` while its ruling is being applied; the status becomes truthful; an open yes shows in the envelope.
  - **Cons:** no audited record can be born `inactive` any more; the kernel still names only one in-place edit, so the amendment rests on a reading.
- **B. Change the kernel.** The kernel's section on decision records names a second edit applied in place: amendment by the findings of the review, until the yes.
  - **Pros:** says outright what both authoring sessions already do; nothing rests on a reading.
  - **Cons:** a kernel change for what began as a kit habit; it needs its own record and, by the rule the earlier record made, a carry audit in full.
- **C. No amendment.** A record is immutable from its first commit; a finding against the record is fixed by a superseding record.
  - **Pros:** the strictest reading; nothing to interpret.
  - **Cons:** every audited record would bring a second one; two records are already in breach and would each need one.

## Recommendation

A, by the session: it is the kernel's own word for the state the record is in, and it costs a status flip.

## Choice

B, by Eugene Chernyshov in chat on 2026-09-21.

## Ruling

1. **R1.** [Kernel §5](../../kernel/CONVENTIONS.md#k5) names the two cases in which a record's body is edited in place, each named by its commit; a status change is no such edit. The new case, before acceptance: until the ceremony that [kernel §4](../../kernel/CONVENTIONS.md#k4) asks of its stakes is complete, whatever examines the record may still correct it — a ruling item tightened, added or withdrawn.
2. **R2.** The window is the ceremony's: a `process` record has it until its yes, an `architecture` record until its review, and a `product` record, asked for neither, has none. What completes a review is the project's to say.
3. **R3.** A correction changes the current-state documents in the same commit, so that the record's status stays true: an item added to a record that says its ruling is applied is applied there and then.
4. **R4.** The other case, at any time, is the mechanical edit, which leaves every ruling untouched: a typo, or a reference-form migration. The typo is new to the kernel's text and old in practice — the consumers' procedure has allowed it since [dec-0024-decision-records-module-rulings](dec-0024-decision-records-module-rulings.md), which believed the kernel already did.
5. **R5.** Past the window, reversing or changing a ruling is a new record, never an in-place edit. This narrows two earlier rulings without reversing them: "records are never edited in place" of [dec-0002-status-encodes-lifecycle](dec-0002-status-encodes-lifecycle.md), and the single in-place edit of [dec-0005-reference-forms](dec-0005-reference-forms.md), sub-decision 3.
6. **R6.** The kernel gives no reason clause and no second clock: the first wording said a decision "is not whole" before its yes and that the record is "evidence of its moment" from then on, which read against "operative when committed" and against the lifecycle rule of [kernel §1](../../kernel/CONVENTIONS.md#k1). Both clauses are gone.
7. **R7.** What follows in the kit:
   - **the comment on `status` in the kernel's frontmatter schema** no longer says records are never edited in place;
   - [requirement A5.6](../requirements.md#a5-6) no longer limits a reference-form migration to an inactive record;
   - **rule 4 of the decision-record policy** speaks of a ruling past its yes, and rule 5 points at the kernel, names the validation and the carry audit as what may correct a kit record, and says records below `0030` are accepted;
   - **step 7 of the carry-audit skill** points at the kernel;
   - **item R16 of [dec-0030-carry-audit-mandatory](dec-0030-carry-audit-mandatory.md)** says where the rule lives.
8. **R8.** The consumers' procedure says the same: in module [`const-decision-records`](../requirements.md#const-decision-records), section 4 of the skill `record-decision` tells an author what may be corrected before a record is accepted and what after; the module's document states it as advisory rule R-e, as boundary pair 11, and says "accepted record" where it had said "closed", a word the kernel keeps for a task set `inactive`. The module is unpublished at `0.0.1`, so no version changes.
9. **R9.** A change to the kernel: the carry audit was run in full over every record before this record's yes, and its findings rewrote items R1 to R8.

## Carry list

1. R1, R2, R3, R4, R5 — [kernel §5](../../kernel/CONVENTIONS.md#k5), read with the ceremony table of [kernel §4](../../kernel/CONVENTIONS.md#k4).
2. R6 — history only: what the kernel no longer says.
3. R7 — [the frontmatter schema](../../kernel/schemas/document-frontmatter.schema.json); [requirement A5.6](../requirements.md#a5-6); [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rules 4 and 5; step 7 of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md).
4. R8 — [the record-decision skill](../../modules/const-decision-records/skills/record-decision/SKILL.md), section 4; [the module's document](../../modules/const-decision-records/MODULE.md), sections 5 and 8.
5. R9 — history only: the audit of this change; the rule that asks for it is rule 2 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r2).
