---
id: dec-0041-questions-module-rulings
type: task-record
title: Rulings of the const-questions authoring — ask at recorded stakes or a blocker, one decision per message in the fixed shape, no open question in a deliverable
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-questions authoring

## Context

The module [`const-questions`](../requirements.md#const-questions) is authored from 2026-09-25 in the kit, ahead of its Phase C slot in the rollout plan, as the decider chose in chat that day: the kit is consumer zero of its own session conduct — the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md) is the interim carrier of the module's rules, and the kit's history holds the friction signal the specification asked for, six commits on the shape of one decision message in two days (commits 1534dd8, 064da57, 1df97d1, cffa57f, ff06c3f, f73393a). Its rows are [requirement A6.1](../requirements.md#a6-1) to [requirement A6.9](../requirements.md#a6-9); its research comparison is [res-0007-const-questions](../research/res-0007-const-questions.md). The questions below were put to the decider in chat, one per message, each with lettered options; the record grows while the module is built and is `active` until the commit that names its yes.

## 1. Which module, and where it is authored

The handoff of the previous session left the next module unchosen: two self-limiting modules had their friction signal observed, and the plan lists the consumer's bootstrap before either.

- **A. [`const-questions`](../requirements.md#const-questions).** The ask-vs-decide skill with its contrastive pairs, the per-decider preferences dial, and the optional gate-lite scan of delivered documents for open-question markers.
  - **Pros:** its signal is the best documented in the repository, six commits on the decision format alone; a skill plus one deterministic scan keeps the record small; the boundary rows of [`const-interaction`](../requirements.md#const-interaction) are easier to rule once this module exists.
  - **Cons:** almost entirely advisory, so its live proof is a headless-run reading rather than a red→green fixture; the scan's territory is a design decision the kernel does not settle.
- **B. [`const-interaction`](../requirements.md#const-interaction).** The answer-shape and assumptions skill on the `SessionStart` carrier, plus a `PreToolUse` gate on destructive commands.
  - **Pros:** a genuine hook gate with a red→green fixture; part of its research already exists; the visible zero of an off-by-default module gets settled there.
  - **Cons:** three parked items of the audit plan must be ruled before or inside it, so the record is larger and slower; its signal is observed but less counted.
- **C. No module yet.** Name the first consumer and the date of Phase B, and take the parked process items first.
  - **Pros:** the plan lists Phase B before Phase C, and one parked item changes how a module is proven live in the kit.
  - **Cons:** the accumulating set is complete and every consumer-live proof already sits at step 5 of the plan, so nothing blocks a module; the parked items are each short and can be taken when they bite.

The session recommended A. **R1.** A, chosen by the decider in chat on 2026-09-25: [`const-questions`](../requirements.md#const-questions) is authored in the kit as consumer zero, like the six modules before it, ahead of its Phase C slot — the kit being consumer zero of the session conduct its own guide states, and having passed the module's entry trigger; its consumer-live proof is a step of the consumer's bootstrap, and a finding there is a fix with a version bump, as [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) rules for the four. The parked items of the audit plan stay parked and come to the decider one per message when one blocks a step.

## 2. The session-conduct block of CLAUDE.md once the skill exists

The block carries today, by hand, the rules this module ships as a skill. The kit's own sessions load no plugin unless started with `--plugin-dir`, one flag per module.

- **A. The block stays whole; the skill is proven beside it.** The record states that the block is the kit's own copy of the rules, kept until the kit loads its plugins per clone.
  - **Pros:** no kit session loses the rules; the block also carries the branch, commit and reference rules, which are owed to no module; the trim is earned by the parked item on how the kit loads its own plugins.
  - **Cons:** the same rules stand in two places for a while, and a change to the format is made in both.
- **B. Trim the block now to what the module does not carry, with one pointer line to the module.**
  - **Pros:** one home for the asking rules from the day the module lands; the kit dogfoods its carrier at once.
  - **Cons:** a kit session started without the flag has no asking rules at all — the state that earned the module; a pointer line is the drifting install path the template discourages.
- **C. Replace the block's question lines with the copy-into-CLAUDE.md fallback the install note offers,** labelled manual and version-drifting.
  - **Pros:** proves the fallback path on the kit, which no consumer has yet.
  - **Cons:** a lower-fidelity carrier chosen over the skill just built; the label invites the drift it warns of.

The session recommended A. **R2.** A, chosen by the decider in chat on 2026-09-25, with the decider's addition: the kit's harness — the session-conduct block and the rest of what [CLAUDE.md](../../CLAUDE.md) carries by hand — is replaced by the made modules later, once the kit loads its own plugins per clone; until then the block stays whole and carries the rules itself, and what a module carries leaves the block at that replacement, as a routine edit that names this record.

## Carry list

1. R1 — the "not a project" bullet of [INTENT.md](../../INTENT.md), which names the kit consumer zero of the session conduct its own guide states, and [§2](../../modules/const-questions/MODULE.md#t2) of the module's document, which states the entry trigger; the done sentence of step 9 of the rollout plan is written when the module lands.
2. R2 — the opening sentence of the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md), which states that the block carries the rules itself until the made modules replace the kit's harness.
