---
id: dec-0131-record-policy-gaps-closed
type: task-record
title: The record policy closes four gaps, on hashes, a lost acceptance after an id change, a link to rewritten text and an old id's note
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The record policy closes four gaps, on hashes, a lost acceptance after an id change, a link to rewritten text and an old id's note

This record answers questions on [plc-0004-decision-records](../policies/plc-0004-decision-records.md) that [item 9.38 of the rollout plan](../rollout-plan.md#s9-38) logged, in sections 1 to 3. Section 4 answers a finding of the carry audit of the change that holds this record. Each question has a section of its own.

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

## 3. A link to text that a later change rewrote elsewhere

This section is on [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md). Entry 2 of its carry list homes its R2 in the docstring of `run_all`, in the shared harness file. The move to pytest on 2026-10-15 removed `run_all`. R3 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r3) replaced part of that ruling. Its carry list names `collected` in the shared file `acceptance.py` as the home. [Rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) let a link follow a place's whole text moved to another document, in the same change. This text was rewritten, not moved, a month before.

- **A. Move the link.** Only the link's target in dec-0078 changes, to `acceptance.py`.
  - **Pros:** a reader of the record lands on the code that holds the ruling now.
  - **Cons:** it edits a frozen record past what rule 14 allowed; the record's words still name `run_all`.
- **B. Leave dec-0078 as it stands.** The newer record already names the ruling's current home.
  - **Pros:** no edit of a frozen record; rule 14 stays as it is.
  - **Cons:** the link leads to a file where the named docstring is gone.

The session recommended B: rule 14 let a link follow only a whole text moved in the same change. <a id="r5"></a>**R5.** A, chosen by the decider in chat on 2026-11-12. The session's objection stands as history: the pick moves a link past what rule 14 allowed. So rule 14 is widened, and the move is a migration under it. A later change may have rewritten a link's cited text into another document. Then, if a later record's carry list names that place for the same ruling, the link may take it at any later time. Only the link's target changes. The commit names it a migration and names that record.

<a id="r6"></a>**R6.** Under R5, the link of entry 2 of dec-0078's carry list to the shared harness takes `acceptance.py`, as dec-0091 names it. The link's text and the words "the docstring of `run_all`" stay as history.

## 4. The note for the old id of a record accepted again

[Rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5) says that an `Accepted:` id that names no record is a note. Such an id was deleted since, renumbered, renamed or misspelt. R3 of [dec-0124-renamed-record-accepted-again](dec-0124-renamed-record-accepted-again.md#r3) says the same of the old id of a renamed record. R8 of [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md#r8) says it of a renumbered one.

A commit of this change, `2e3e8ff5`, stopped that note once the record is accepted again under its new id. The note had printed on every run for the old id of the module-readme-pages record, though a merge had accepted the record rightly. The commit called the change routine. The change's carry audit in full found that it adds a condition to those rulings. [Rule 1 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r1) prices that as a ruling.

- **A. Rule it here, before the yes.** The note stops once the record is accepted again under its new id, and rule 5 says so.
  - **Pros:** it keeps the fix of a note that taught nothing; the code and its self-test already stand; it stays in this one change.
  - **Cons:** one more ruling late in the audit, and one more confirming round; the note's end leans on git's rename detection.
- **B. Revert the commit.** Rule 5 and the two records stand as written.
  - **Pros:** no new ruling, and nothing more to audit.
  - **Cons:** the note for that old id prints again on every run.
- **C. Keep the code and justify it as routine.** No text changes.
  - **Pros:** no edit and no record.
  - **Cons:** rule 1 prices an added condition as a ruling, so the gate would contradict rule 5.

The session recommended A: the note's end removes a note that taught nothing, and this record already closes the record policy's gaps on renames. <a id="r7"></a>**R7.** A, chosen by the decider in chat on 2026-11-12. Once a renumbered or renamed record is accepted again under its new id, the note for its old id stops. It stops where git's rename detection follows the old id's file to a record that stands. It stops only if a commit that holds the last rename accepts that record. A deleted or misspelt id keeps its note. So does the old id of a rename that git does not detect. So does the old id of a record never accepted again, or accepted only before its last rename.

<a id="r8"></a>**R8.** R7 narrows R3 of [dec-0124-renamed-record-accepted-again](dec-0124-renamed-record-accepted-again.md#r3) in that one point. It narrows R8 of [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md#r8) the same way. Those records are not touched.

## Applied

The commit that creates this record rewords the sentence on hashes in rule 12 of the policy. A later commit of the same branch adds section 2, its sentences in rule 5 and in step 8 of the carry-audit skill. Another adds section 3, its sentences in rule 14, and the migration of R6. A last one adds section 4 and its sentences in rule 5; the code it rules came in `2e3e8ff5`. The record is born `inactive`.

## Carry list

1. R1 — [rule 12 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12), its sentences on a commit hash.
2. R2 — history only: the reversal in part of an earlier ruling, which binds nothing once R1 is carried.
3. R3, R4 — [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), its sentences on a lost acceptance after an id change. Also [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md), step 8.
4. R5 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), its sentences on a text a later change rewrote into another document.
5. R6 — history only: one migration under R5, a one-time act.
6. R7 — [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), its sentences on the note for an old id; [`scripts/check-carry-lists.py`](../../scripts/check-carry-lists.py), its docstring.
7. R8 — history only: the narrowing in part of two earlier rulings, which binds nothing once R7 is carried.
