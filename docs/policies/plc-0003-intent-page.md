---
id: plc-0003-intent-page
type: current-state
title: Intent policy — the frame of the kit
status: active
---

# Intent policy

Governs the document kind *intent page*: the frame every design and edit of the kit is checked against. Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**Type.** `current-state`, superseded in place ([kernel §1](../../kernel/CONVENTIONS.md#k1)).
2. <a id="r2"></a>**Change.** A change to the frame is an explicit `process`-stakes decision, never a side effect of other work ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)).
3. <a id="r3"></a>**Content.** States what the kit is, the problem it solves, its architecture in three layers, its design principles, what it is not, and its success criteria; adding a section is a change under rule 2. It holds no rule that belongs to the kernel and no procedure that belongs to a module.
4. <a id="r4"></a>**Present tense.** The page states what the kit is. A mechanism not yet built is named as planned, with a link to the step of the rollout plan that builds it, or left out: intent that is not yet real rides in the plan ([kernel §2](../../kernel/CONVENTIONS.md#k2)).
5. <a id="r5"></a>**Principles are earned.** A principle added after the founding set cites the record that earned it, beside it, as provenance ([kernel §5](../../kernel/CONVENTIONS.md#k5)).
6. <a id="r6"></a>**Anchors.** Every section carries an explicit anchor `i<n>` and every principle `p<n>`, never renumbered ([requirement A5.5](../requirements.md#a5-5)).
7. <a id="r7"></a>**Enforcement.** The envelope by module `const-meta-types`; links and anchors by module `const-referencing`. The content is review.
