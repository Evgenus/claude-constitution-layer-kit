---
id: dec-0053-drafts-keep-their-versions
type: task-record
title: A module's version is bumped once it is published — a draft need not be bumped for a change of its own, a change to the shared code or a consumer-live finding
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A module's version is bumped once it is published — a draft need not be bumped for a change of its own, a change to the shared code or a consumer-live finding

## Context

The carry audit of [dec-0052-doc-budgets-module-rulings](dec-0052-doc-budgets-module-rulings.md) found three texts that disagreed on versions. Step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md) said "a fix in shared code bumps the version of every module that links it", and rule 7 of [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r7) said a change to the shared code bumps the version of every module that links the code, neither with a condition; step 7 said "Version bump on every change once published". Three changes to the shared code had bumped nothing, every module being a draft at `0.0.x`. The audit justified the tension and left it to the decider, who asked for it as a decision on 2026-09-29. The two questions below were put in chat, one per message, each with lettered options; the pick was the letter.

## 1. When a fix to shared code bumps a module's version

- **A. Drafts are exempt: the bump applies once a module is published.**
  - **Pros:** it matches what the kit did three times; a draft has no consumer who installs by version; the texts then agree.
  - **Cons:** a policy and guide change, recorded and audited; a draft's version does not say which shared code it carries.
- **B. Always bump, drafts included.**
  - **Pros:** no rule text changes; a version always marks a change in what the plugin runs.
  - **Cons:** step 7 still disagrees; eleven manifests and their documents bumped on every shared fix; the three earlier fixes stay un-bumped.
- **C. Leave the texts, read step 7 as governing.**
  - **Pros:** no work now.
  - **Cons:** a reading the rule's own words contradict; the next audit finds the tension again.

The session recommended A. <a id="r1"></a>**R1.** A, chosen by the decider in chat on 2026-09-29: a change to the shared code bumps the version of every published module that links it, and a draft's need not be bumped. The same holds for a change to a kernel section the shared code implements, which rule 3 of [plc-0002-kernel](../policies/plc-0002-kernel.md#r3) ties to the same bump.

## 2. Whether the exemption covers a consumer-live finding

Step 5 of "Developing a module" said a finding in the consumer-live proof "is a fix with a version bump", a clause of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) that seven module documents repeat in their deferred live item. That proof runs in the rollout plan's Phase B, while every module is a draft loaded from the kit's path, where a version selects nothing.

- **A. Yes: every version bump applies once a module is published;** this record narrows that clause of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md), its section 3.
  - **Pros:** one rule for every bump; it fits the path load of Phase B.
  - **Cons:** a wider change and audit.
- **B. No: only the shared-code bump gains "published".**
  - **Pros:** a smaller change; dec-0015 unchanged.
  - **Cons:** two bump rules with different conditions.

The session recommended A. <a id="r2"></a>**R2.** A, chosen by the decider in chat on 2026-09-29: a consumer-live finding is a fix, with a version bump once the module is published; step 7 states the whole rule — a draft, at `0.0.x`, need not be bumped, for a change of its own, a change to the shared code or a consumer-live finding alike. "Need not": a draft may still be bumped within `0.0.x`, as four were before this record.

## 3. What this record narrows

<a id="r3"></a>**R3.** R1 narrows the unconditional bump of R5 and R34 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r5), carried into [rule 3 of plc-0002-kernel](../policies/plc-0002-kernel.md#r3) and [rule 7 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r7). R2 narrows the clause "a finding there is a fix with a version bump" of section 3 of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) and the same clause as R4 of [dec-0035-locations-module-rulings](dec-0035-locations-module-rulings.md#r4), R6 of [dec-0036-task-close-module-rulings](dec-0036-task-close-module-rulings.md#r6), R1 of [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md#r1), R1 of [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md#r1) and R2 of [dec-0044-styling-module-rulings](dec-0044-styling-module-rulings.md#r2). Each such bump now applies once the module is published; the rest of those rulings stands.

## Carry list

1. R1 — [CLAUDE.md](../../CLAUDE.md), steps 4 and 7 of "Developing a module"; [rule 7 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r7); [rule 3 of plc-0002-kernel](../policies/plc-0002-kernel.md#r3).
2. R2 — [CLAUDE.md](../../CLAUDE.md), steps 5 and 7 of "Developing a module", step 7 also saying a draft may still be bumped; the deferred live item of seven module documents: [`const-doc-budgets`](../../modules/const-doc-budgets/MODULE.md#t10), [`const-interaction`](../../modules/const-interaction/MODULE.md#t10), [`const-language`](../../modules/const-language/MODULE.md#t10), [`const-locations`](../../modules/const-locations/MODULE.md#t10), [`const-questions`](../../modules/const-questions/MODULE.md#t10), [`const-styling`](../../modules/const-styling/MODULE.md#t10), [`const-task-close`](../../modules/const-task-close/MODULE.md#t10). The rollout plan's step 5 names the narrowed clause for the consumer-live proof.
3. R3 — history only: the narrowing is stated where R1 and R2 are carried.
