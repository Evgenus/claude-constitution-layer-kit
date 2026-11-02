---
id: dec-0109-mature-project-proofs-after-the-switch
type: task-record
title: Budget ceilings stay before the switch; the lane, departure and coverage-pair proofs follow it
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Budget ceilings stay before the switch; the lane, departure and coverage-pair proofs follow it

## Context

On 2026-11-01 a session started item 5.2 of [the rollout plan](../rollout-plan.md#s5-2) in the first consumer project. Every scan of a module was green there, and every module's runner was green on the throwaway repository it builds. Four parts of the live items still needed state the project did not have:

- L4 of [`const-doc-budgets`](../requirements.md#const-doc-budgets) asks for ceilings set at warning from the history report. The project had no ceilings. Its history began on 2026-10-23, enough for a ceiling at warning.
- L4 of [`const-referencing`](../requirements.md#const-referencing) asks for a write with a bare form of a declared lane to be blocked. The project declared no lane.
- L4 of [`const-styling`](../requirements.md#const-styling) asks for a departure declared in the project. It had none.
- L4 of [`const-task-close`](../requirements.md#const-task-close) proves the range check, which needs a coverage pair. The project had no code for a pair to describe. Its plan brings its first scripts at its step W9.

By [rule 5 of plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), step 5a waits for item 5.2. No item of either plan made the lane or the departure, and only a real need of the project would bring them. So the switch of [dec-0104-public-before-the-ci-bound-proofs](dec-0104-public-before-the-ci-bound-proofs.md) could wait without end, and with it the consumer project's own CI, which waits for the kit to be public. The session put the question in chat on 2026-11-01.

## Options

- **A. All four parts move to waiting items after the switch.** Item 5.2 closes with the session proofs; each part waits for its own signal.
  - **Pros:** the switch waits only for the session proofs, the decisions and the access check; nothing is invented in the project; it is the move [dec-0104-public-before-the-ci-bound-proofs](dec-0104-public-before-the-ci-bound-proofs.md) made for the CI parts.
  - **Cons:** the kit goes public with four live items partly unproven; the lane and the departure may wait forever.
- **B. As A, but the ceilings stay in item 5.2, set now as a real change in the project.**
  - **Pros:** one more part is proven in the project itself before the switch; the project gains ceilings it can use.
  - **Cons:** the kit's plan asks for content in the project outside the project's own plan; the change touches the project's dials file while another of its branches is open; the move to error still waits for 30 days of data.
- **C. Item 5.2 stays whole, and the missing items are added to both plans.**
  - **Pros:** every item is proven as written before the switch.
  - **Cons:** the switch waits for the project's steps up to its first code, and for two needs that may never come.
- **D. The lane and the departure leave the consumer proof; the ceilings and the coverage pair move after the switch.**
  - **Pros:** nothing can wait without end.
  - **Cons:** two modules no longer claim a consumer proof for a rule; it changes what is proven, not only when.

## Recommendation

The session recommended A: it is the only option in which the switch waits neither for the project's own work nor for needs that may never come, and it invents no content in the project.

## Choice

The decider chose B in chat on 2026-11-01.

## Ruling

<a id="r1"></a>**R1.** The ceilings of L4 of [`const-doc-budgets`](../requirements.md#const-doc-budgets) stay in item 5.2, before the switch: the consumer project sets its ceilings at warning from the history report, in a change of its own. Their move to error is no part of the proof.

<a id="r2"></a>**R2.** Three parts of live items follow the switch, each in an item of its own, waiting for its own signal, and none is made in the project only to pass the proof. The blocked write with a bare form of a declared lane, of L4 of [`const-referencing`](../requirements.md#const-referencing), waits for the first lane the project declares. The declared departure, of L4 of [`const-styling`](../requirements.md#const-styling), waits for the first departure the project declares with a reason of its own. The range check over a coverage pair, of L4 of [`const-task-close`](../requirements.md#const-task-close), waits for the first pair the project writes. For these three parts, this replaces "the parts of the live items that need no CI still come before the switch" in R1 of [dec-0104-public-before-the-ci-bound-proofs](dec-0104-public-before-the-ci-bound-proofs.md#r1), and "Item 5.2 keeps … the parts of the live items that need no CI" in R2 of [dec-0104-public-before-the-ci-bound-proofs](dec-0104-public-before-the-ci-bound-proofs.md#r2); step 5a holds these three items after the six that R2 lists. The rest of those rulings stands.

## Applied

The change adds items 5a.6, 5a.7 and 5a.8 to the plan, each waiting, with the row of step 5a and the row `all` of the status matrix; and item 5.2 names the parts that are theirs. Every item has its home in the commit that creates this record, so the record is born `inactive`.

## Carry list

1. R1 — pending: [item 5.2 of the rollout plan](../rollout-plan.md#s5-2).
2. R2 — pending: [items 5a.6](../rollout-plan.md#s5a-6), [5a.7](../rollout-plan.md#s5a-7) and [5a.8](../rollout-plan.md#s5a-8) of the rollout plan, and [item 5.2](../rollout-plan.md#s5-2) for the parts that stay before the switch. What it replaces in R1 and R2 of dec-0104 is history.
