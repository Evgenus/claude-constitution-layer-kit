---
id: kit-rollout-plan
type: current-state
title: Rollout-plan policy — the kit's own write-head
status: active
---

# Rollout-plan policy

Governs the document kind *rollout plan*: the phases of the kit's rollout and their sequence, the kit's own task-record. Territory under this policy's id in `constitution.yaml`.

## Rules

1. **Type.** `task-record`, `active` while a phase remains, `inactive` when the last phase is reached ([kernel §2](../../kernel/CONVENTIONS.md#k2)); a stretch with no commits in its scope is stalled drift.
2. **Content.** Phases, steps, and sequence only. A requirement belongs to the requirements document, a ruling to a decision record; neither is stated here.
3. **Change.** Reordering or rewriting phases is a `process`-stakes decision ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)); ticking a step done is routine.
