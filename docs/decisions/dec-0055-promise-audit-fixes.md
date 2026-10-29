---
id: dec-0055-promise-audit-fixes
type: task-record
title: The promise audit's partly carried rows are carried, the gate and CI lists name every module scan, and a bare aspect handle stays with review
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The promise audit's partly carried rows are carried, the gate and CI lists name every module scan, and a bare aspect handle stays with review

## Context

On 2026-09-30 the decider asked whether every row of the matrix of [constitution-requirements](../requirements.md) was addressed as the plan promised. The per-row report of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md) says whether a row's items pass, not whether what shipped keeps the row's destination and recommended enforcement. The decider chose a one-time audit by fresh readers first, and a mechanical check afterwards only where the audit finds a gap a script could have caught. Six readers read the 69 rows at the commit that landed dec-0054: 45 kept, 17 changed with the change declared and argued as [rule 7 of plc-0007-requirements](../policies/plc-0007-requirements.md#r7) allows, 3 not yet — [aspect A12](../requirements.md#a12), waiting on kit CI — and 4 partly carried. Beside the rows, the readers found gaps a script could have caught: F5, F6 and F8 below. The session checked every partial row and every kit-side point against the tree. They are the findings below, numbered F1 to F11; the questions were put in chat, one per message, and the pick was the letter.

## 1. How the fixes are grouped

- **A. One change, one record, one audit, the fixes and the two mechanical checks together.**
  - **Pros:** one audit, one yes.
  - **Cons:** a large change, and a problem in the new scripts would hold back the simple fixes.
- **B. The fixes first, the mechanical checks after, each with its own record.**
  - **Pros:** the fixes land fast; the checks keep their own design questions; the checks then prove the fixed tree.
  - **Cons:** two audits and two yeses.
- **C. One change per module or topic.**
  - **Pros:** each small.
  - **Cons:** about six audits reading the same records again.

The session recommended B. The decider chose B in chat on 2026-09-30. <a id="r1"></a>**R1.** This record carries the fixes; the check that every module scan stands in the gate list and the CI list, and the grep of [requirement A12.1](../requirements.md#a12-1) as a kit script, come in a change of their own. F8 — that grep, run by hand as the row words it, hits in-plugin relative paths in messages and example dial paths in install notes, though it finds no project reference — moves there, since its fix is the grep's own design.

## 2. The bare aspect handle

[Requirement A5.6](../requirements.md#a5-6) asks for an aspect to be cited by a link, and no lane of the kit held a bare aspect handle (F2). A lane for the letter and a number would collide with message keys — the shared gate code keys its `ask` message A1 — and three accepted records cite aspects bare.

- **A. A lane for the bare aspect handle, the documents with such message keys named as its homes, the three records migrated to links.**
  - **Pros:** the row held as written.
  - **Cons:** every document with an A-keyed message table must be named a home, or it turns red; three accepted records edited.
- **B. The bare aspect handle stays with review, declared.**
  - **Pros:** no false red and no list of exceptions to keep; the limit written where a reader looks.
  - **Cons:** a bare aspect handle in a new document is not caught by a machine.

The session recommended B: bare aspect handles were three in the kit, all in records written before the reference rule was strict, and a list of exceptions would be machinery for a failure no one has hit. <a id="r2"></a>**R2.** B, chosen by the decider in chat on 2026-09-30: a bare aspect handle is held by review and not by a lane, since the letter and a number collide with message keys.

## 3. The fixes without a choice

Each carries a clause a row states, or corrects a text the audit found wrong; none is a new rule.

<a id="r3"></a>**R3.** F1, [requirement A4.3](../requirements.md#a4-3): an `inactive` record is kept while something should still reference it and deleted once nothing should, git history its archive, whether anything should being judgment — carried into rule T-b of module [`const-task-close`](../requirements.md#const-task-close) and its close skill, after [kernel §1](../constitution/CONVENTIONS.md#k1), its "should" read as judgment, as [rule 7 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r7) reads it for the kit's own records.

<a id="r4"></a>**R4.** F2, the rest of the same row: a code location by symbol, a commit hash and a bare `#n` stay advisory, with the reason now stated — a pattern cannot tell a symbol from a word, a hash from other hexadecimal text, or a bare `#n` from prose such as "record #1".

<a id="r5"></a>**R5.** F3, [requirement A7.5](../requirements.md#a7-5): rule e of the rules text of module [`const-interaction`](../requirements.md#const-interaction) says a stable per-item handle, as the row does.

<a id="r6"></a>**R6.** F4, [requirement A9.1](../requirements.md#a9-1): what module [`const-styling`](../requirements.md#const-styling) ships tells a project that governs its documents by policies to have its root policy ask every policy for a style rule, and each kind's policy carry one, binding that kind's documents to the guide.

<a id="r7"></a>**R7.** F5: the list-handles scan of module [`const-interaction`](../requirements.md#const-interaction), the gate of [requirement A7.5](../requirements.md#a7-5), is a line of the kit's gate list.

<a id="r8"></a>**R8.** F6: the CI of rollout step 10 runs the scan of every module that ships one, not only the reference scan and the range check.

<a id="r9"></a>**R9.** F7, [requirement A9.4](../requirements.md#a9-4): the row's text says that, once module [`const-language`](../requirements.md#const-language) is installed, a checkable default about words may graduate to a Vale rule, each at its first need, and that the markup signatures the styling scan detects stay the scan's — the ruling R10 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md#r10), section 7; the row is amended under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2), its rule having changed.

<a id="r10"></a>**R10.** F9 and F10, two readings corrected: in module [`const-interaction`](../requirements.md#const-interaction) the daggers of [requirement A8.1](../requirements.md#a8-1) and [requirement A8.2](../requirements.md#a8-2) are still an open test, as its rows section says; in module [`const-task-close`](../requirements.md#const-task-close) the row's "blocking is a dial" is kept by a stronger hold, the scan exiting 2 on every finding, while the shared `severity` governs only the turn-end hook.

F11 needs no edit: module [`const-catalogs`](../requirements.md#const-catalogs) records the research's verdict against the matrix row as it then stood, and the row was amended afterwards — a history line, not a stale claim.

## Carry list

1. R1 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the two kit checks and F8 settled in the grep's design; how this work is split is history.
2. R2 — the reference bullet of [CLAUDE.md](../../CLAUDE.md#references).
3. R3 — [module `const-task-close`](../../modules/const-task-close/MODULE.md#t5), rule T-b; [its close skill](../../modules/const-task-close/plugin/skills/close-task/SKILL.md), step 5.
4. R4 — [module `const-referencing`](../../modules/const-referencing/MODULE.md#t3), its reading of the row.
5. R5 — [the rules text](../../modules/const-interaction/plugin/scripts/rules.txt), rule e; [module `const-interaction`](../../modules/const-interaction/MODULE.md#t6), the size it states.
6. R6 — [the skill of module `const-styling`](../../modules/const-styling/plugin/skills/style-defaults/SKILL.md); [its install note](../../modules/const-styling/plugin/INSTALL.md).
7. R7 — the bullet "Work starts on a branch" of [CLAUDE.md](../../CLAUDE.md), whose gate list holds "the scans of the modules"; the gate-list agent of `.claude/agents/` runs it as item 9.
8. R8 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the CI wiring.
9. R9 — [requirement A9.4](../requirements.md#a9-4), its text.
10. R10 — [module `const-interaction`](../../modules/const-interaction/MODULE.md#t6), its research line; [module `const-task-close`](../../modules/const-task-close/MODULE.md#t3), its reading of [requirement A4.2](../requirements.md#a4-2).
