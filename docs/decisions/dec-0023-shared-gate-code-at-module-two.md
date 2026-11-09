---
id: dec-0023-shared-gate-code-at-module-two
type: task-record
title: Shared gate code is extracted at the end of the second module, from recorded evidence; the admission rule gains a second class
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Shared gate code is extracted at the end of the second module

## Context

[dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) section 2 ruled two things. Ruling (a): [`const-meta-types`](../requirements.md#const-meta-types) is the one write-time guard of claimed territory. Ruling (b): no shared library before a second reader exists; when [`const-catalogs`](../requirements.md#const-catalogs) needs the territory lookup, a kernel reference implementation is extracted, vendored into each module under a kit gate on copy equality, admitted only for functions that implement a kernel section literally and that two or more modules need.

Ruling (b) rested on two assumptions that the first module's authoring overturned on 2026-09-18. The shared piece was pictured as the lookup of [kernel §3](../constitution/CONVENTIONS.md#k3), a couple of hundred lines; after [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md) roughly half of the module — event parsing, dials loading, territory matching, the policy index, the output log, the command line and its guard, the preflight, the configuration-failure messages, the fixture harness — is machinery every gate must have. And the second reader is not the third module: [requirement A3.4](../requirements.md#a3-4) makes [`const-decision-records`](../requirements.md#const-decision-records), the next one, a write-time gate that needs all of it. The admission rule was too narrow as well: the log, the guard, the preflight and the harness implement gate-script rules of [template §6](../../module-template/MODULE.md#t6), not kernel sections. A second defect surfaced on the way: ruling (b) was stated in no current text, only in its record, against [kernel §5](../constitution/CONVENTIONS.md#k5).

Ruling (a) is untouched; the implementation strengthens it, since envelope and resolution share one index in one process.

## Options

- **A. Keep ruling (b).** The second module copies by hand; extraction at the third.
  - **Pros:** no work now; three users' evidence before a seam is drawn.
  - **Cons:** about a thousand lines copied by hand, drifting across a whole module's authoring; two migrations later.
- **B. Extract now, before the second module starts.**
  - **Pros:** the second module starts clean; copies cannot drift.
  - **Cons:** every seam guessed from one example — how a module adds its dials, how its check plugs into the hook pipeline, what it needs from the index; the premature shape the earlier record warned about.
- **C. Extract at the end of the second module, before its yes.** It copies the generic modules verbatim; copies are not edited; every forced edit is written down — those are the seams. Then both modules move to the vendored form together.
  - **Pros:** seams from evidence — the principle of ruling (b), with its timing corrected; one migration per module; drift bounded to one module's authoring and recorded.
  - **Cons:** a short period with two copies; the second module is validated twice.
- **D. A pip package declared in `requirements.txt`.**
  - **Pros:** no copies.
  - **Cons:** the kit would publish a package; two modules pinning different versions conflict in one environment; verdicts depending on machine state were already rejected.

Recommendation C. Chosen C by the decider in chat on 2026-09-18.

## Ruling

1. Ruling (b) of the earlier record is replaced; ruling (a) stands.
2. [`const-decision-records`](../requirements.md#const-decision-records) copies the generic modules of the first module verbatim. A copy is not edited; an edit the second module cannot avoid is listed, with its reason, under Phase A step 3 of the [rollout plan](../rollout-plan.md) — the list is the evidence the seams are drawn from.
3. At the end of the second module's authoring, before its yes, the shared code is extracted: source in the kit, vendored into each module, a kit gate on copy equality, [INTENT.md](../../INTENT.md) amended, and [law 3 of CLAUDE.md](../../CLAUDE.md#law-3) reworded so that a vendored copy is visibly not a sibling dependency — an installed module still carries everything it runs. Both modules move together.
4. Admission has two classes: code that implements a kernel section literally, and code that implements a gate-script rule of the template. In both, two or more modules must need it.
5. Delivery by package index stays what it was: for readers outside plugins, if one appears.

Applied in the commit that creates this record: [CLAUDE.md](../guide/developing-a-module.md#s4) step 4 of "Developing a module" and Phase A step 3 of the rollout plan. The record stays `active` until item 3 is done.
