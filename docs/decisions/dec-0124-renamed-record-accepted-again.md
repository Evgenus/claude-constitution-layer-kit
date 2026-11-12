---
id: dec-0124-renamed-record-accepted-again
type: task-record
title: A renamed record is accepted again under its new id, as a renumbered one is
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A renamed record is accepted again under its new id, as a renumbered one is

## Context

[Rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5) said that a renumbered record is accepted again under its new id. It said nothing of a renamed one. [Kernel §1](../constitution/CONVENTIONS.md#k1) lets an item's `id` change in three cases. The third is a rename: a catalog whose form changes, as when its width grows, renames each of its items once. After such a rename, every earlier `Accepted:` trailer names an id that no record carries. The gap was logged on 2026-10-12 in [item 9.24 of the rollout plan](../rollout-plan.md#s9-24), to wait for a signal. The decider's ask of 2026-11-11, to finish the plan with its waiting items, started it without one. No catalog of the kit has changed its form yet.

The kit's `scripts/check-carry-lists.py` already treats a renamed record as it treats a renumbered one. It reads a file under a new name as a record the change adds: its audit scope lists the record in full under that name, and it refuses a receipt pinned to a commit where the record stood under its old id. Its docstring and its note said "renumbered" alone.

## Options

- **A. A renamed record is accepted again, as a renumbered one is.** Rule 5 names both cases; the carry audit of the renaming change reads the record in full under its new name.
  - **Pros:** it states what the check already does, with no new code path; one rule covers every id change the kernel allows.
  - **Cons:** a rename of a whole catalog means every record is read in full and accepted again in one merge, which is a large audit.
- **B. Accepted again, but the audit reads only the rename.** The readers check the new id and the file name, not the record's body.
  - **Pros:** a rename of many records stays cheap; rule 14 of the same policy says a rename is no edit of a record's body.
  - **Cons:**
    - **the check's scope must tell a renamed record from an added one**, which is new code for a case nobody has met;
    - **two rules for two kinds of id change**.
- **C. A renamed record keeps its acceptance.** The check follows the old id to the new one, and no second yes is asked.
  - **Pros:** no second yes for a record whose rulings did not change.
  - **Cons:**
    - **the check must read renames from the history**, which is new machinery for a failure nobody has hit;
    - **an old trailer would count for an id it never named**.

## Recommendation

A, by the session: it writes down what the check does today, so the policy and the check agree.

## Choice

A, by the decider, in chat on 2026-11-11. The decider gave the letter and no reason. The pick did not name R6 and R7. The session added them in the fixes of the first round of the carry audit: R7 where the new sentence of rule 5 read two ways, R6 where the rule did not say under which id the record must stand at the commit the receipt names. Both state what the check already does.

## Ruling

<a id="r1"></a>**R1.** A record renamed as [kernel §1](../constitution/CONVENTIONS.md#k1) allows, when its catalog's form changes, is accepted again under its new id, in the merge commit of the change that renames it.

<a id="r2"></a>**R2.** That acceptance carries the receipt of the carry audit of the renaming change. The audit's readers read the renamed record in full: the audit's scope lists it under its new name, as a record the change adds.

<a id="r3"></a>**R3.** An earlier `Accepted:` trailer that names the old id of a renamed record names no record. The check reports it as a note and never as a finding, as it does for a record deleted since, renumbered or misspelt.

<a id="r4"></a>**R4.** The docstring and the note of `scripts/check-carry-lists.py` name the renamed record beside the renumbered one.

<a id="r5"></a>**R5.** R1, R2 and R3 widen R8 of [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md#r8), which ruled the same for a renumbered record. R6 adds to that ruling which commit the receipt names. That record is not touched.

<a id="r6"></a>**R6.** For a renumbered record and for a renamed one, the commit the receipt names is one at which the record already stood under its new id.

<a id="r7"></a>**R7.** A record numbered below `0030` stays accepted with no trailer after its rename.

## Applied

The commit that creates this record adds the sentence of R1 and R2 to rule 5 of the policy, and the word "renamed" to its list of the ids that name no record. It changes three texts of the check: the receipt paragraph of its docstring, its note, and the typed line of that note in its self-test. What the check judges does not change, and the sentence of rule 5 on a renumbered record stands as it was. The record is born `inactive`. The corrections of the carry audit, among them the sentences of R6 and R7 in rule 5, follow in the same branch, before the yes.

## Carry list

1. R1, R2, R3, R6, R7 — [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), its sentences on an `Accepted:` id that names no record, on a renamed record, on the commit the receipt names, and on a record numbered below `0030`.
2. R4 — [the check](../../scripts/check-carry-lists.py), the receipt paragraph of its docstring and the note of an accepted id that is no record.
3. R5 — history only: the widening of an earlier ruling, which binds nothing once R1, R2, R3 and R6 are carried.
