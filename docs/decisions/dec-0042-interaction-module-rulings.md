---
id: dec-0042-interaction-module-rulings
type: task-record
title: Rulings of the const-interaction authoring — answer in the shape of the question, assumptions and lists addressable, one gate on destructive commands
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-interaction authoring

## Context

The module [`const-interaction`](../requirements.md#const-interaction) is authored from 2026-09-25 in the kit, ahead of its Phase C slot in the rollout plan, as the decider chose in chat that day: the kit is consumer zero of its own session conduct — the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md) carries by hand five of the module's rules, "Lead with the answer", "Restate before acting", "Assumptions are always explicit", "Every list item is addressable" and "Honesty over agreement", and the "Refuse destructive moves without a spoken confirmation" bullet is the class the module's one gate holds. Its rows are [requirement A7.1](../requirements.md#a7-1) to [requirement A7.5](../requirements.md#a7-5), [requirement A8.1](../requirements.md#a8-1) to [requirement A8.3](../requirements.md#a8-3) and [requirement A10.2](../requirements.md#a10-2); its research comparison is [res-0008-const-interaction](../research/res-0008-const-interaction.md). Two parked process items of the audit of 2026-09-22 touch the module's always-on carrier and are ruled here with it: the visible zero of an off-by-default module, and the kit loading its own plugins per clone. The questions below were put to the decider in chat, one per message, each with lettered options; the record grows while the module is built and is `active` until the commit that names its yes.

## 1. Which work is next, and where the module is authored

The handoff of the previous session left the next work unchosen: the module, or the parked items of the audit plan first, beginning with the name of the first consumer.

- **A. [`const-interaction`](../requirements.md#const-interaction), with the two carrier items folded in.** The answer-shape rules on an always-on carrier, the escalation rows after `const-questions` took the asking side, and a `PreToolUse` gate on enumerated destructive commands; the visible-zero and the marketplace items ruled as its first decisions.
  - **Pros:** the daggered rows are cheaper now that the asking side has a home; the assumptions and addressable-lists rules cut from the sibling's skill have a home waiting; the two carrier items are settled where they bite.
  - **Cons:** the module carries the kit's first gate on the shell tool, whose hook surface changed since it was last surveyed; the marketplace item inside the module widens its record.
- **B. The parked items first**, beginning with the name of the first consumer and the date of Phase B, one per message, before any new module.
  - **Pros:** a consumer name unblocks the consumer-live proofs seven modules defer to the bootstrap; the parked items stop accumulating.
  - **Cons:** nothing ships; most parked items are process and several depend on this module's carrier, so they would be ruled without the module that exercises them.

The session recommended A. **R1.** A, chosen by the decider in chat on 2026-09-25: [`const-interaction`](../requirements.md#const-interaction) is authored in the kit as consumer zero, like the seven modules before it, ahead of its Phase C slot — the kit having passed the module's entry trigger with five guide bullets on one theme; its consumer-live proof is a step of the consumer's bootstrap, and a finding there is a fix with a version bump, as [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) rules for the four. The consumer's name stays a parked item, put to the decider in one message at any point.

## Carry list

1. R1 — the "not a project" bullet of [INTENT.md](../../INTENT.md), which names the kit consumer zero of the session conduct its own guide states, and [§2](../../modules/const-interaction/MODULE.md#t2) of the module's document, which states the entry trigger; the done sentence of step 9 of the rollout plan is written when the module lands; the sentence on the parked consumer item is history only, a scheduling call of the day.
