---
id: dec-0131-record-policy-gaps-closed
type: task-record
title: A record's body holds a commit hash as the row on reference forms allows
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A record's body holds a commit hash as the row on reference forms allows

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

## Applied

The commit that creates this record rewords the sentence on hashes in rule 12 of the policy. The record is born `inactive`.

## Carry list

1. R1 — [rule 12 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12), its sentences on a commit hash.
2. R2 — history only: the reversal in part of an earlier ruling, which binds nothing once R1 is carried.
