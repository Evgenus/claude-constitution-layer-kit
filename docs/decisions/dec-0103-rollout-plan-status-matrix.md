---
id: dec-0103-rollout-plan-status-matrix
type: task-record
title: The rollout plan opens with a status matrix that a kit check holds, and every item carries one status mark
status: active
stakes: process
decider: Eugene Chernyshov
---

# The rollout plan opens with a status matrix that a kit check holds, and every item carries one status mark

## Context

On 2026-10-24 the decider asked that [the rollout plan](../rollout-plan.md) make it easier to see what is done and what is pending, more like a traceability matrix, with status marks and percents of completion. Each status and percent was to be verified with its proof, the meaning kept identical, and the old and new texts read against each other.

The plan's state was hard to read. Step 9 held about forty pieces of work in one paragraph and one list, done and open mixed. Step 10 held seventeen in one paragraph. A done piece and an open piece often shared a sentence. No line said how much of a step was done.

Three rules stood in the way of a plain rewrite. [Rule 3 of plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r3) priced a rewrite of the phases at `process` stakes. [Rule 5](../policies/plc-0008-rollout-plan.md#r5) fixed how a done step is marked, in one sentence, with the evidence never in the plan. No rule defined a percent. A count typed by hand also drifts: step 9 of the plan itself logged hand-kept sums in two kit checks, and a hand-typed count of the kernel's sections that nothing held. The dated sizes of step 9 had drifted too: the page of [kit-shared-gate-code](../../shared/GATE.md) stood at 94,415 characters on 2026-10-22 and at 98,145 on 2026-10-24.

## Options

- **A. A full matrix.** One table per phase, one row per step and per piece of work, with the item's text, its status mark, a percent and its proof in the cells.
  - **Pros:** it is the shape asked for; every piece gets a handle; a phase reads at a glance.
  - **Cons:** long prose in table cells is hard to read and to compare in raw Markdown; an argument is never a table by [default d4 of the style guide](../style-guide.md#d4), and steps 5 and 9 hold procedure and reasons; the percents are typed by hand and held by review alone.
- **B. A summary matrix on top, the steps split into items below.** One row per step at the top, with its phase, status, counts and percent; each long step split into items, each opening with its handle and its mark, the text kept almost word for word.
  - **Pros:** the old and new texts compare sentence by sentence, so the meaning is least likely to drift; the summary gives the view at a glance; the prose stays readable.
  - **Cons:** a status is stated twice, in its row and in its items, and the two can disagree; the percents are still typed by hand.
- **C. B, with a kit check.** The shape of B, and a script of the kit that counts the items' marks, derives each row's counts, percent and status, and turns red on a mismatch or on a done item with no link.
  - **Pros:** a status or a percent cannot drift without a red; the check is a gate in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5); every later tick is held, not this rewrite alone.
  - **Cons:** new kit tooling, a script with its self-test and an entry of the gate list, so the change is larger and takes longer to review.
- **D. Only the open work.** The plan keeps its open pieces and a short table of the done steps; the history stays in the records and in git.
  - **Pros:** the shortest and clearest plan; rule 2 of the policy already sends rulings elsewhere.
  - **Cons:** it removes text, against the decider's "meaning should be identical"; the carry audit would have to prove that every removed sentence has its home elsewhere.

## Recommendation

C, recommended by the session: B gives the clearest view with the least risk to the meaning, and the check keeps the percents from drifting the way the sizes of step 9 did.

## Choice

C, by the decider in chat on 2026-10-24: "C: summary matrix on top, split items below, and a kit check that holds the counts and percents."

## Ruling

<a id="r1"></a>**R1.** Every piece of work the plan names, or group of pieces it names together, is an item of its step, and every item opens, after its handle, with one mark. ✅ is done. ⏳ is open: to be done in the plan's order, which is the order of its steps and, within a step, only the order its items' own words set, and not before a date its text sets for the work to start. 💤 is waiting: started only when the signal, the condition or the ask its text names comes, which may never come; a date is no such condition. A piece or a group whose parts would carry different marks is split into items, one mark each. A step with no items is its own one item, its mark, a space and its words right after its anchor; a step with items carries no mark of its own. The plan states its steps' items and their status beside its phases, steps and sequence.

<a id="r2"></a>**R2.** A step's line opens `<n>. <a id="s<n>"></a>`, and the step stands under a phase line. Every list line from a step's line to the next step or phase line, outside a fenced block, is one of its items, and a list line under a phase line and above its first step stands in no step. An item is one line, `- <a id="s<n>-<m>"></a>**<n>.<m>** <mark> <words>`: its anchor, then its bold handle, its number written without a leading zero. A line right under an item, or under a step with no items, that is no blank line, list line, step line, phase line or fence line is part of it, so a heading or a paragraph of the step that follows an item stands after a blank line. Every fenced block of the plan closes. Items are numbered within their step in ascending order, from 1, and keep their number; a number once used is not used again, so an item removed leaves a gap. An item added later at the end of its step takes the next whole number above the highest yet used; one added between two items stands after the one it follows as `<n>.<m>a`. This widens R31 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r31) from the steps to their items, and adds the step line's form and its place under a phase line; the rest of R31 stands.

<a id="r3"></a>**R3.** An item ticked done says, in one of its sentences, its date and its record — the record's title in plain words once the record is deleted — and "the yes given", or its date and "a routine change". An item already done when the status matrix came into the main branch, by the merge of this record's change, need not take this form, nor shed what it holds. Every done item holds an inline link, `[text](target)`, to its record, or the document or the module a routine change concerns, or, once the record is deleted, the current-state document that carries its ruling, which the change that deletes the record links: that link is its proof. The evidence stays in the record, the module document or, for a routine change, its commit. This widens R32 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r32) from a done step to a done item, adds the routine change, the commit and the link, and narrows it in one point: a step or an item already done when the matrix came into the main branch keeps its words, though they break R32's one-sentence form or hold evidence. The rest of R32 stands.

<a id="r4"></a>**R4.** The plan holds a status matrix before its first phase: one row per step in the plan's order, under the header row `| Step | Title | Phase | Status | Done | Open | Waiting | % done |`, whose cells are the step's handle linked to its anchor, `[s<n>](#s<n>)`, a short title, its phase's capital letter, its status, the counts of its done, open and waiting items, and its percent done; and a last row, `all` in its handle and phase cells, of the sums, its percent and status derived by the same rules. The counts are of items, whatever each holds, so the percent measures items, not effort. The percent is `done * 100 // (done + open)`, rounded down and written with `%`, a waiting item counting in neither part, and `n/a` where done and open are both 0. A step's status is ✅ when no item is open or waiting, ⏳ when an item is open and none is done, 🔄 when an item is done and another is open, and 💤 when no item is open and one is waiting.

<a id="r5"></a>**R5.** The kit's `scripts/check-rollout-status.py`, an entry of the gate list with `--self-test` as its fixture, reads the plan by line patterns, not as a Markdown parser does. It holds what its docstring lists: the matrix against the steps and their items, its rows, cells and the values R4 derives, read once no finding of the steps, the items or a fenced block stands; the lines of the steps and the items in the forms of R1 to R3, with their marks, the words after them, their numbers and their links, and that no list line stands in no step; and the fenced blocks closed. Its docstring also names known limits of that reading; where the check misreads a line, review holds it. Whether a mark matches its item's words, whether a link is its proof, a done item's words, a row's title and the history R2 asks of numbers stay with review.

<a id="r6"></a>**R6.** Ticking an item done changes its mark, its sentence, its step's row and the row `all` in the same change, at routine stakes.

<a id="r7"></a>**R7.** The rewrite of this change is one of form: every sentence of the plan is kept, split into items where a step held several pieces of work, each item marked by its own words. A sentence is changed only where a split needs it: a subject named where a pronoun would point across an item, a sentence joined by semicolons cut where its parts carry different marks, a parenthesis that names open work made an item of its own, and a sentence about a whole step moved to the step's lead. Steps 4, 5, 8, 9 and 10, whose items hold their text, open with their titles from the matrix. The reading of the old text against the new one reads each such change. The decider chose, in chat on 2026-10-24, that the statuses and dated facts the proof pass of this change found stale are corrected in this change, and the open item it found missing added; the commit that corrects them names the proof of each.

## Applied

The change amended rules 2, 3, 4, 5 and 8 of [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md) and added its rule 10; rewrote [the rollout plan](../rollout-plan.md) into the matrix and its items; and added the kit's `scripts/check-rollout-status.py` to the gate group of `scripts/gate-list.sh`. A proof pass checked every claim of the old plan against the repository, and four fresh readers read the old text against the new one; the claims the proof pass found stale were then corrected, as the decider chose.

## Carry list

1. R1 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5, and [its rule 2](../policies/plc-0008-rollout-plan.md#r2).
2. R2 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r4), rule 4.
3. R3 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5.
4. R4 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r10), rule 10.
5. R5 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r8), rule 8, and [the check's docstring](../../scripts/check-rollout-status.py).
6. R6 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r3), rule 3.
7. R7 — history only: the form of this change's rewrite, and the correction of the stale claims its proof pass found.
