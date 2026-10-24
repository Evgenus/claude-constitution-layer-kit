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

Three rules stood in the way of a plain rewrite. [Rule 3 of plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r3) priced a rewrite of the phases at `process` stakes. [Rule 5](../policies/plc-0008-rollout-plan.md#r5) fixed how a done step is marked, in one sentence, with the evidence never in the plan. No rule defined a percent. A count typed by hand also drifts: step 9 of the plan itself logged hand-kept sums in two kit checks, and a hand-typed count of the kernel's sections that nothing held. The dated sizes of step 9 had drifted too: the page of [kit-shared-gate-code](../../shared/GATE.md) stood at 94,415 characters on 2026-10-22 and at 98,628 on 2026-10-24.

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

<a id="r1"></a>**R1.** Every piece of work the plan names is an item of its step, and every item opens, after its handle, with one mark: ✅ done; ⏳ open, to be done in the plan's order; 💤 waiting, started only when the signal, the condition or the ask its text names comes. A piece whose parts carry different marks is split into items, one mark each. A step with no items is its own one item, its mark right after its anchor; a step with items carries no mark of its own. The plan states its steps' items and their status beside its phases, steps and sequence.

<a id="r2"></a>**R2.** Every item carries an explicit anchor `s<n>-<m>` and opens with the bold handle `<n>.<m>`, numbered once within its step from 1, keeping its number. An item added later at the end of its step takes the next number; one added between two items stands after the one it follows as `<n>.<m>a`. This widens R31 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r31) from the steps to their items; the rest of R31 stands.

<a id="r3"></a>**R3.** An item done says, in one sentence, its date and its record — the record's title in plain words once the record is deleted — and "the yes given", or its date and "a routine change". It links the record, or the document or the module a routine change concerns, or, once the record is deleted, the current-state document that carries its ruling: that link is its proof, and the evidence stays in the record and the module document. This widens R32 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r32) from a done step to a done item, and adds the routine change and the link; the rest of R32 stands.

<a id="r4"></a>**R4.** The plan opens with a status matrix, before its first phase: one row per step in the plan's order, whose cells are the step's handle linked to its anchor, a title of a few words, its phase's letter, its status, the counts of its done, open and waiting items, and its percent done; and a last row, `all`, of the sums. The percent is `done * 100 // (done + open)`, rounded down, a waiting item counting in neither part, and `n/a` where done and open are both 0. A step's status is ✅ when no item is open or waiting, ⏳ when an item is open and none is done, 🔄 when an item is done and another is open, and 💤 when no item is open and one is waiting.

<a id="r5"></a>**R5.** The kit's `scripts/check-rollout-status.py`, an entry of the gate list with `--self-test` as its fixture, holds the matrix against the items: one row per step and none for another, in order; each row's phase, counts, percent and status, and the `all` row, as R4 derives them; each item's one mark, and its handle and anchor, matching its step and numbered on as R2 says; and a link in every done item. Whether a mark matches its item's words, whether a link is its proof, and a row's title stay with review.

<a id="r6"></a>**R6.** Ticking an item done changes its mark, its sentence and its step's row in the same change, at routine stakes.

<a id="r7"></a>**R7.** The rewrite of this change is one of form: every sentence of the plan is kept, split into items where a step held several pieces of work, each item marked by its own words; a sentence is changed only where a split needs a subject or a joining word, and the reading of the old text against the new one reads each such change. A status the proof pass of this change found stale is changed only as the decider chooses.

## Applied

<Filled as the change is made.>

## Carry list

1. R1 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5, and [its rule 2](../policies/plc-0008-rollout-plan.md#r2).
2. R2 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r4), rule 4.
3. R3 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5.
4. R4 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r10), rule 10.
5. R5 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r8), rule 8, and [the check's docstring](../../scripts/check-rollout-status.py).
6. R6 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r3), rule 3.
7. R7 — history only: the form of this change's rewrite, and the stale statuses of its proof pass.
