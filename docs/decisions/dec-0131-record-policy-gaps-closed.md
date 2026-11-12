---
id: dec-0131-record-policy-gaps-closed
type: task-record
title: Commit hashes in a record's body follow the reference row, and a lost acceptance after an id change is mended like a wrong receipt
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Commit hashes in a record's body follow the reference row, and a lost acceptance after an id change is mended like a wrong receipt

This record answers questions on [plc-0004-decision-records](../policies/plc-0004-decision-records.md) that [item 9.38 of the rollout plan](../rollout-plan.md#s9-38) logged. Each has a section of its own.

## 1. A commit hash in a record's body

[Requirement A5.6](../requirements.md#a5-6) lets a commit hash stand in a record's body, and in any dated statement of evidence or of done work. It never stands in a sentence that states how things are. [Rule 12 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12) was narrower. It let a hash in a record's body name an audit's pin, or where git holds a deleted file that is no record. It added "and nowhere else". That phrase read two ways: nowhere else in the body, or nowhere else in the kit.

R5 of [dec-0123-commit-hash-stands-in-dated-text](dec-0123-commit-hash-stands-in-dated-text.md#r5) kept the narrow rule on 2026-11-11. Yet accepted records hold hashes for other dated facts. For example, [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md) names the commit its experiments ran on. [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md) names the commits two records landed in. Those records are frozen.

- **A. Rule 12 follows the row.** A record's body may hold a hash wherever the row allows one.
  - **Pros:** one rule for hashes in the kit; the records that already do so follow it; no reading is left open.
  - **Cons:** it reverses in part a ruling of the day before; one more home for the carry audit.
- **B. Rule 12 stays narrow, its wording made plain.** It says "in a record's body" and keeps the two uses.
  - **Pros:** no new ruling; the ruling of the day before stands.
  - **Cons:** frozen records stay in breach of a rule they cannot be edited to fit; the policy stays narrower than the row it cites.

The session recommended A: the kit's own records follow the row, and a rule its frozen records break is no rule. <a id="r1"></a>**R1.** A, chosen by the decider in chat on 2026-11-12. A commit hash may stand in a record's body as [requirement A5.6](../requirements.md#a5-6) allows, and never in a sentence that states how things are. An audit's pin, where git holds a deleted file that is no record, and a dated fact are such uses. A deleted record is still named by its title.

<a id="r2"></a>**R2.** R1 reverses R5 of [dec-0123-commit-hash-stands-in-dated-text](dec-0123-commit-hash-stands-in-dated-text.md#r5) for rule 12 of the policy only. The rest of that ruling, on rule 3 of plc-0005-research, stands. That record is not touched.

## 2. A renumbering or rename merged without its new acceptance

[Rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5) says that a renumbered or renamed record is accepted again under its new id. That happens in the merge commit of the change that gives the new id. It says how a wrong receipt is mended: by accepting again in the merge commit of a new pull request. It said nothing of a merge that lacks the new acceptance. The check then reports only that the record awaits its yes, as a note, so nothing turns red.

- **A. Mended as a wrong receipt is.** A new pull request's merge commit accepts the record under its new id. Its receipt is for a carry audit that reads the record in full.
  - **Pros:** the path rule 5 gives a wrong receipt; it keeps the full read that dec-0124 ruled; no new code.
  - **Cons:** a full audit for a record whose rulings did not change.
- **B. Mended by a light acceptance.** The new pull request's audit reads only the new id, the file name and the links to it.
  - **Pros:** cheap, since only the id changed.
  - **Cons:** a lighter audit for a mend than for the change itself, against the full read that dec-0124 ruled; two rules for one act.

The session recommended A: it is the path rule 5 already gives a wrong receipt, and it keeps dec-0124 as ruled. <a id="r3"></a>**R3.** A, chosen by the decider in chat on 2026-11-12. A renumbering or a rename that merged without the acceptance under the new id is mended as a wrong receipt is. The merge commit of a new pull request accepts the record under its new id. Its receipt is for a carry audit that reads the record in full.

<a id="r4"></a>**R4.** The receipt of R3 names a commit at which the record already stood under its new id. R6 of [dec-0124-renamed-record-accepted-again](dec-0124-renamed-record-accepted-again.md#r6) asks the same.

## Applied

The commit that creates this record rewords the sentence on hashes in rule 12 of the policy. A later commit of the same branch adds section 2, its sentences in rule 5 and in step 8 of the carry-audit skill. The record is born `inactive`.

## Carry list

1. R1 — [rule 12 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12), its sentences on a commit hash.
2. R2 — history only: the reversal in part of an earlier ruling, which binds nothing once R1 is carried.
3. R3, R4 — [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), its sentences on a lost acceptance after an id change. Also [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md), step 8.
