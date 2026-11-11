---
id: dec-0123-commit-hash-stands-in-dated-text
type: task-record
title: A commit hash stands only in dated text, never in a sentence that states how things are
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A commit hash stands only in dated text, never in a sentence that states how things are

## Context

[Requirement A5.6](../requirements.md#a5-6) let a commit hash stand in three places only: commit messages, record bodies and chat. [Rule 3 of plc-0005-research](../policies/plc-0005-research.md#r3) asks a comparison to name what verified each fact, and one of its three sources is "the kit's own tree at a named commit". The two texts did not agree. The gap was logged on 2026-10-12 in [item 9.24 of the rollout plan](../rollout-plan.md#s9-24), to wait for a signal. The decider's ask of 2026-11-11, to finish the plan with its waiting items, started it without one.

The session counted the commit hashes of the tree on 2026-11-11, outside commit messages and decision records:

- **Comparisons.** Twelve of the sixteen comparisons of `docs/research/` name a commit, as rule 3 asks.
- **Module documents.** Three module documents name one, each in a live proof that carries its date: those of [`const-questions`](../requirements.md#const-questions), [`const-doc-budgets`](../requirements.md#const-doc-budgets) and [`const-change-cost`](../requirements.md#const-change-cost).
- **The rollout plan.** Two done items name the merge commit that a release tag was made on, each with its date.

Every one of these stands in text that belongs to one day. None stands in a sentence that says how the kit is. The module document of [`const-referencing`](../requirements.md#const-referencing) also shows hashes inside quoted examples of its own rule; an example of a form is no reference, and this record does not touch them.

## Options

- **A. Widen the row for comparisons only.** The row gains the provenance of a research comparison, and nothing else.
  - **Pros:** it closes exactly the logged gap; it is the smallest change to the row.
  - **Cons:** the hashes of the three module documents and of the plan stay against the row, and need a ruling of their own.
- **B. Widen the row by principle.** A hash may stand in any dated text: a commit message, a record's body, a dated comparison, a dated statement of evidence or of done work, chat. It never stands in a sentence that states how things are.
  - **Pros:** one rule covers every hash the tree holds today; nothing is left over.
  - **Cons:** the policies of module documents and of the rollout plan say it for their kinds; the advisory rule and the skill of the module change with the row; whether a statement carries its date is judgment, which no gate holds.
- **C. Narrow the research policy instead.** Rule 3 stops naming a commit, and a comparison names the tree by its date.
  - **Pros:** the row and the module stay as they are.
  - **Cons:** a date does not name one tree, so a reader cannot repeat the check; the frozen comparisons keep their hashes and would stand against the row for good.

## Recommendation

A, by the session: it is the amendment the plan's item names, and it states what the comparisons already do.

## Choice

B, by the decider, in chat on 2026-11-11. The decider gave the letter and no reason. The session keeps no objection: B leaves no hash of the tree against the row, which A did not.

## Ruling

<a id="r1"></a>**R1.** A commit hash stands only in these places: a commit message, a record's body, a dated comparison, a statement of evidence or of done work that carries its date, and chat. It never stands in a sentence that states how things are. This amends the requirement, which named the first, the second and the last of these places only.

<a id="r2"></a>**R2.** In a module document, a live proof or a platform fact carries its date, and may name the commit it was run or seen at.

<a id="r3"></a>**R3.** In the rollout plan, a done item that says its date may name a commit, such as the one a tag was made on.

<a id="r4"></a>**R4.** Module [`const-referencing`](../requirements.md#const-referencing) carries R1 as advice, in its own words and with no name of a kit document: in its advisory rule on hashes, in the examples of that rule, and in the skill it ships. The rule stays advisory, since a pattern cannot tell a commit hash from other hexadecimal text.

<a id="r5"></a>**R5.** Two narrower rules stand as they are. [Rule 12 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12) lets a hash stand in the body of one of the kit's decision records for two uses only. Rule 3 of plc-0005-research asks a comparison to name the commit of the kit's tree that verified a fact.

## Applied

The commit that creates this record amends the row and adds the sentences of R2 and R3 to the two policies. A second commit of the same branch changes the module's document and skill for R4 and sets this record `inactive`. A third holds the new receipt of the module's eval cases, which the skill's edit made stale.

## Carry list

1. R1 — [requirement A5.6](../requirements.md#a5-6), its sentence on commit hashes.
2. R2 — [rule 10 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r10), its last sentence.
3. R3 — [rule 5 of plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), the sentence after the form of a done item.
4. R4 — [the module's document, its rows](../../modules/const-referencing/MODULE.md#t3), the row of that requirement; [its invariant](../../modules/const-referencing/MODULE.md#t5), rule F-d; [its boundary examples](../../modules/const-referencing/MODULE.md#t8), the examples of F-d; [the module's skill](../../modules/const-referencing/plugin/skills/referencing/SKILL.md), item 6 of its section 1.
5. R5 — [rule 12 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12) and [rule 3 of plc-0005-research](../policies/plc-0005-research.md#r3), each as it stood.
