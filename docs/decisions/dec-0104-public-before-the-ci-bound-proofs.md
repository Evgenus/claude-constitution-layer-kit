---
id: dec-0104-public-before-the-ci-bound-proofs
type: task-record
title: The repository goes public in a new step 5a, after the bootstrap and before the consumer-live proofs that need the project's CI
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The repository goes public in a new step 5a, after the bootstrap and before the consumer-live proofs that need the project's CI

## Context

On 2026-10-24 a session reviewed [the rollout plan](../rollout-plan.md) against the two bootstraps of the first consumer project, read-only. The bootstrap itself was done: the project merged its branch on 2026-10-23, its merge naming the decider's yes for its record #1. The eleven live items that item 5.2 of the plan names were not: each still reads "live, deferred" in its module's document.

Seven of those items ask for the module's scan in the project's CI: L5 of [`const-catalogs`](../requirements.md#const-catalogs), L4 of [`const-referencing`](../requirements.md#const-referencing), L4 of [`const-questions`](../requirements.md#const-questions), V4 of [`const-interaction`](../requirements.md#const-interaction), L4 of [`const-styling`](../requirements.md#const-styling), V4 of [`const-language`](../requirements.md#const-language) and L4 of [`const-doc-budgets`](../requirements.md#const-doc-budgets). The project has no remote and no CI. Its scans run from a clone of the kit, and the kit's repository is private, so a CI job of the project needs a token to read the kit. R1 of [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md#r1) makes the repository public only after the first consumer project's live proof. On 2026-10-25 GitHub also refused to start the kit's own CI jobs for a billing reason; on a public repository GitHub runs them free.

The session put two questions, one per message, in chat on 2026-10-26.

## 1. How the seven CI-bound live items are proven

- **A. The project gets a private GitHub remote and a CI job that clones the kit with a read token and runs the scans.**
  - **Pros:** the items are proven as written; the project needs a remote anyway; it tests the access to a private repository while a failure is cheap.
  - **Cons:** a token secret in the project; the install guide has no CI step, so the run would add one to a guide already over its length ceiling.
- **B. The seven items are narrowed to "the scan run against the project", and the CI part moves to a new item after the repository is public.**
  - **Pros:** item 5.2 can finish now; no token.
  - **Cons:** seven acceptance items of seven modules change, and [requirement A10.1](../requirements.md#a10-1) names the CI as the gate; the CI path stays unproven until after publication.
- **C. The repository is made public before the CI-bound parts of item 5.2.**
  - **Pros:** no token; the project's CI reads the kit as any consumer's will.
  - **Cons:** it reorders the phases, at `process` stakes; the kit goes public before its consumer-live proof is complete.

The session recommended A: it proves the items as written and changes no ruling. The decider chose C in chat on 2026-10-26.

<a id="r1"></a>**R1.** The kit's repository is made public before the parts of the consumer-live proof that need the project's CI, and those parts follow the switch: the project's CI reads the public kit with no token. The scans against the project, each module's runner and the parts of the live items that need no CI still come before the switch. This replaces "made public after the first consumer project's live proof" in R1 of [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md#r1); the rest of that ruling stands.

## 2. Where the switch stands in the plan

By [rule 5 of plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), an open item is done in the order of the plan's steps. Item 10.3, which makes the repository public, stood in step 10, so it waited for every open item of steps 4 to 9 as well: the review of 4.1, the language descent of 9.6, and the ceilings of 9.9, 9.13, 9.14 and 9.14a.

- **A. A new step 5a, "Make the repository public", right after step 5.** It takes the email question of 10.3, the forks of 10.4 and the package index of 10.5; item 5.2 keeps the parts that need no CI, and the CI-bound proofs become an item right after the switch.
  - **Pros:** the switch waits only for 4.1 and the parts of 5.2 that need no CI; the seven proofs are unblocked soon; CI runs free; forks and the package index are decided when they start to matter.
  - **Cons:** the open work of step 9 happens in public; three items leave step 10, which leaves gaps in its numbers.
- **B. Item 10.3 stays in step 10, its words changed; the CI-bound proofs become a new item 10.3a.**
  - **Pros:** the smallest edit; no item moves.
  - **Cons:** the switch, and with it the seven proofs, waits for every open item of step 9, the six changes of the language descent among them.
- **C. A new step 5a with 10.3 and the CI-bound proofs only; 10.4 and 10.5 stay in step 10.**
  - **Pros:** a smaller move than A.
  - **Cons:** once public, a pull request from a fork fails until 10.4 is decided; the signal of the package index fires at the switch, but its decision waits.

The session recommended A: only A unblocks the seven proofs without waiting for step 9, and the forks and the package index belong beside the switch. The decider chose A in chat on 2026-10-26.

<a id="r2"></a>**R2.** A new step 5a, "Make the repository public", follows step 5 in phase B. Its items are, in this order: the decision whether the author's email stays in the history; the decision how a pull request from a fork is checked; the decision whether the shared package is also published on PyPI; the switch itself, after those three; and the parts of the live items that need the project's CI, after the switch. Items 10.3, 10.4 and 10.5 leave step 10, and their numbers stay as gaps. Item 5.2 keeps the scans, the runners and the parts of the live items that need no CI.

<a id="r3"></a>**R3.** The decision on the author's email, which R5 of [dec-0063-apache-license-with-notice](dec-0063-apache-license-with-notice.md#r5) left to step 10, is made at step 5a, before the switch.

<a id="r4"></a>**R4.** The signal of R20 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r20), "the repository goes public at step 10 of the rollout plan", is reaching step 5a: the question is decided there, at item 5a.3, before the switch.

<a id="r5"></a>**R5.** Item 10.8, to verify in a session the team access to the private repository, leaves the plan: after the switch no private repository is left to verify. Its number stays as a gap.

<a id="r6"></a>**R6.** The change that makes the repository public also updates every text that calls it private, save the decision records and the done items of the plan, which are history. Among them are the rule "Work starts on a branch" of [CLAUDE.md](../../CLAUDE.md), which names the kit's private GitHub remote; prerequisite 2 of [the install guide](../../INSTALL.md#s1); a step name of the CI workflow; and docstrings, comments and fix texts of the kit's scripts `scripts/check-bare-install.py`, `scripts/check-install-guide.py`, `scripts/gate-list.sh` and `scripts/kit_module_doc.py`.

## Applied

The change adds step 5a and its five items to the plan, with its row in the status matrix; narrows item 5.2; removes items 10.3, 10.4, 10.5 and 10.8; and rewords the package index's signal in [kit-shared-gate-code](../../shared/GATE.md#g1) to name step 5a. Every item has its home in the commit that creates this record, so the record is born `inactive`.

## Carry list

1. R1 — pending: [step 5a of the rollout plan](../rollout-plan.md#s5a), its items 5a.4 and 5a.5. What it replaces in R1 of dec-0057 is history.
2. R2 — pending: [step 5a of the rollout plan](../rollout-plan.md#s5a), and [item 5.2](../rollout-plan.md#s5-2) for the parts that need no CI. The removal of items 10.3, 10.4 and 10.5 is history.
3. R3 — pending: [item 5a.1 of the rollout plan](../rollout-plan.md#s5a-1).
4. R4 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts.
5. R5 — history only: the removal of item 10.8, a one-time act.
6. R6 — pending: [item 5a.4 of the rollout plan](../rollout-plan.md#s5a-4).
