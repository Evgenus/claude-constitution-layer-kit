---
id: dec-0040-rules-fit-their-documents
type: task-record
title: Rules of dec-0039 that read stricter than the documents keep are widened to what the documents do, and a comparison gets its change stakes
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rules of dec-0039 that read stricter than the documents keep are widened to what the documents do, and a comparison gets its change stakes

## Context

On the day [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md) landed, the decider asked whether the governed documents now needed adjusting. Three fresh readers checked every governed document against its policy's final rules. Most gaps were the documents' — undated live proofs, deferred proofs not linking the plan's step, a manifest never listed — and were repaired as routine edits under dec-0039 in the repair commit of this branch, two commits before this record's. Five gaps were the rules': rule 8 of the module-document policy counted an advisory rule `R-a` as a reuse of the message prefix `R` and bare-numbered lists in different sections as one prefix, which all six module documents break. Rule 4 of the root policy demanded the full kind in a policy's title where four policies use a short name; rule 8 of the root policy asked every Enforcement rule to split write time from scan, which seven do not. Rule 7 of the requirements policy closed the enforcement vocabulary against the qualifiers the rows carry, and its rule 1 read against the module headings' entry triggers, which [dec-0006-accumulating-set-first](dec-0006-accumulating-set-first.md) defines and are no phase; rule 2 of the rollout-plan policy forbade stating a ruling in the plan while its rule 6 makes the plan the home of pending intent. Amending a row of the matrix is `process` under rule 2 of the requirements policy, so even the two rows whose enforcement word lay outside the set could not be touched without a record. A sixth gap was a missing rule: the research policy gave a comparison no change stakes before its freeze, which the policy template asks every policy to give. Before the yes the decider found a seventh: the root policy's rule 3 cited a rule of the decision-record policy for what counts as a routine repair, so the policy where every chain of governance ends depended on a policy it governs.

## Options

- **A. Widen the rules to what the documents keep, and give a comparison its change stakes, in one record.** With it, the two rows and two headings the readers flagged, and two sentences of the plan that restate rules carried elsewhere.
  - **Pros:** the readers never confused the prefixes or the titles; the rules were the audit's own drafting error; one small record and audit.
  - **Cons:** a record following dec-0039 the same day.
- **B. Repairs only; the rules wait for friction.**
  - **Pros:** no record.
  - **Cons:** six module documents and four policies in breach of rules accepted the same day, and the rows untouchable without a record anyway.
- **C. Bring the documents to the strict rules.** Rename the advisory-rule handles in six documents, retitle four policies, rewrite the rows.
  - **Pros:** no rule changes.
  - **Cons:** churn for a distinction no reader needed, and the row rewrites still need a record.

## Recommendation

A, by the session: a rule stricter than its documents' practice, with no reader confused, is the rule's defect.

## Choice

A, chosen by the decider in chat on 2026-09-24; R8, found by the decider before the yes: the rule was chosen over a routine fix of the citation alone and over leaving it, in chat on 2026-09-25; two audit rounds then reworded it, from "relies on no rule of a policy it governs", which caught the root's own rules, to what stands.

## Ruling

**R1.** In a module document a handle prefix is a letter or a word followed by a number; a letter, a hyphen and a lowercase letter is another prefix, the advisory rules'; a bare number is local to its list and cited with its section; an item added beside another takes its number with a letter; the artifacts table's rows are keyed by component and path. The kinds and their prefixes stay as dec-0039 R24 gave them.

**R2.** A policy's title names its kind in full or by its short name — "Intent policy" for the intent page — and the root's is "Root policy — <clause>".

**R3.** A policy's Enforcement rule says which module guards which field, at write time, in its scan, or both; the split is named where the two differ — the mentions outside Markdown and a collision between items that exist, which only a scan reads, while a new item's number is checked at write time too; and the code pairing, which the range check alone holds, run before a merge and on the trunk after it.

**R4.** The requirements document's enforcement classes may carry a qualifier before or after the class — "advisory procedure", "review judgment", an assist named — and a row may name the template as its destination or beside another; a row's cell is amended under rule 2 of the policy when its rule or its vocabulary changes; a module's entry trigger and a condition inside a rule name no phase. Row [A4.2](../requirements.md#a4-2) reads `gate-lite` for what it called "gate as flag"; row [A13.7](../requirements.md#a13-7) reads `config` for a check validated at each read; the headings of `const-meta-types` and `const-questions` drop their phase, and the first reads "enters with the first governed document" for "authored first", which was sequence.

**R5.** The rollout plan states no ruling already made, and states the intent not yet real that a pending carry entry points at, in its step, until the step closes. Two sentences of the plan restating the ceremony of a module and of a change, carried in steps 5 and 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md) and in [rule 4 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r4), are removed; the plan's preamble states its lifecycle by a link to the policy.

**R6.** A research comparison is written as a routine act of a module's development; an edit before its freeze is routine, from the freeze rule 7 of the research policy holds.

**R7.** The document repairs made under dec-0039 in the repair commit, two before this record's — dates and the platform's version on every live item, the `live, deferred` label and the plan's step on every deferred one, dates and breaks on five platform statements, the manifest row, the count tail under F9, two shared keys qualified, one title made one clause, rule 6 of the decision-record policy completed, six facts of the shared page sourced, their dates the audit's later fix, the plan's step 3 given its done line and its Phase E its stakes clause dropped — are routine under the rules dec-0039 accepted.

**R8.** A policy states its own rules itself; a citation of another policy points at where a rule about the other's kind lives, and a clause the citing policy also states is its own, the link being provenance; the root policy, which governs every policy including itself, relies on no rule of any other policy and cites none. Rule 3 of the root policy states the repair rule in its own words and cites the record that made it as provenance.

## Applied

In the commit before the one that creates this record, which holds only this file: the seven rules of R1 to R6, the two rows, the two headings, the two sentences of the plan; the repairs of R7 in the commit before that; the audit's fixes, and R8 with the two rules of the root policy it changes, in the commits after. The record is born `inactive`.

## Carry list

1. R1 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r8), rule 8, and the handles paragraph of [template §10](../../module-template/MODULE.md#t10).
2. R2 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r4), rule 4, and the title line of [templates/policy.md](../../templates/policy.md).
3. R3 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r8), rule 8, rule 3 of [templates/policy.md](../../templates/policy.md), and the Enforcement rules that name a split — [plc-0002-kernel](../policies/plc-0002-kernel.md#r8) rule 8, [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6) rule 6, [plc-0005-research](../policies/plc-0005-research.md#r10) rule 10, [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12) rule 12, [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r9) rule 9.
4. R4 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r1), rule 1, [rule 7](../policies/plc-0007-requirements.md#r7), and rows [A4.2](../requirements.md#a4-2) and [A13.7](../requirements.md#a13-7) of [constitution-requirements](../requirements.md); the two headings' change is history.
5. R5 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r2), rule 2; the two sentences removed and the preamble's link are history.
6. R6 — [plc-0005-research](../policies/plc-0005-research.md#r9), rule 9.
7. R7 — history only: repairs of the day under rules already accepted.
8. R8 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r4), rule 4, and [rule 3](../policies/plc-0001-root-policy.md#r3); that rule 3 once cited the decision-record policy is history.
