---
id: plc-0008-rollout-plan
type: current-state
title: Rollout-plan policy — the kit's own write-head
status: active
---

# Rollout-plan policy

Governs the document kind *rollout plan*: the phases of the kit's rollout and their sequence, the kit's own task-record. Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**Type.** `task-record`, `active` while a phase remains, `inactive` when the last phase is reached — step 11 done, rule 7 ([kernel §2](../../kernel/CONVENTIONS.md#k2)); a stretch with no commits in its scope is stalled drift.
2. <a id="r2"></a>**Content.** Phases, steps, and sequence only. A requirement belongs to the requirements document, a ruling already made to its record and to the current-state text that carries it; neither is stated here. Intent not yet real that a "pending" carry entry points at is stated in its step until the step closes (rule 6).
3. <a id="r3"></a>**Change.** Reordering or rewriting phases is a `process`-stakes decision ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)); ticking a step done is routine.
4. <a id="r4"></a>**Anchors and numbers.** Every phase carries an explicit anchor `phase-<letter>` and every step `s<n>`. Steps are numbered once across the phases and keep their number; a step added later stands after the one it follows as `<n>a`, `<n>b`, with the anchor to match.
5. <a id="r5"></a>**Done.** A step done is marked in its own line with the date, the record — its title in plain words once the record is deleted ([rule 7 of plc-0004-decision-records](plc-0004-decision-records.md#r7)) — and "the yes given", in one sentence; the evidence lives in the record and the module document, never here.
6. <a id="r6"></a>**Pending home.** This is the document a carry list's "pending" entry points at ([rule 2 of plc-0004-decision-records](plc-0004-decision-records.md#r2)): a step so named closes only with its intent carried into the current-state documents, in the same change, and the note the carry-lists gate prints for it is answered by the next audit in full.
7. <a id="r7"></a>**Close.** The plan is `inactive` when step 11 is done. The last phase describes the steady state and holds no rule: what it points at lives in the intent page and the policies.
8. <a id="r8"></a>**Enforcement.** The envelope by module `const-meta-types`; links and anchors by module `const-referencing`; `scripts/check-carry-lists.py` refuses this document as a home, so a ruling stated only here is found by the carry audit. Content is review.
