---
id: dec-0031-record-amended-until-its-yes
type: task-record
title: Kernel §5 — until the yes or the review its stakes ask for, a record may be amended in place by the findings of that review
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

1. **R1.** [Kernel §5](../../kernel/CONVENTIONS.md#k5) names two edits applied in place, each named by its commit. The new one: until the yes or the review that [kernel §4](../../kernel/CONVENTIONS.md#k4) asks of its stakes is given, a record may be amended by the findings of that review — a ruling item tightened, added or withdrawn — since the decision is not whole before it. From then on the record is evidence of its moment.
2. **R2.** The window is the ceremony's: a `process` record has it until its yes, an `architecture` record until its review; a `product` record, of which the ceremony table asks neither, has none.
3. **R3.** The reference-form migration stays the other edit, applied at any time. Reversing a ruling that has had its yes is a new record, as before.
4. **R4.** The kit's texts that had grown their own version give way to the kernel's: the decision-record policy no longer calls a record a proposal and points at the kernel; the carry-audit skill likewise; item R16 of the earlier record says where the rule now lives.
5. **R5.** The consumers' procedure says the same: the skill `record-decision` of module `const-decision-records`, under "Reversing or changing an earlier ruling", says a record is closed by the yes or the review its stakes ask for, and that until then the findings of that review may amend it. The module is unpublished at `0.0.1`, so no version changes.
6. **R6.** A change to the kernel: the carry audit is run in full over every record before this record's yes.

## Carry list

1. R1, R2, R3 — [kernel §5](../../kernel/CONVENTIONS.md#k5), read with the ceremony table of [kernel §4](../../kernel/CONVENTIONS.md#k4).
2. R4 — [kit-decision-records](../policies/kit-decision-records.md), rule 5; step 7 of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md).
3. R5 — [the record-decision skill](../../modules/const-decision-records/skills/record-decision/SKILL.md), section 4.
4. R6 — history only: the audit of this change; the rule that asks for it is rule 2 of [kit-decision-records](../policies/kit-decision-records.md).
