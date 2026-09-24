---
id: plc-0002-kernel
type: current-state
title: Kernel policy — the semantic kernel of the kit
status: active
---

# Kernel policy

Governs the document kind *kernel*: the conventions page that is authoritative for all vocabulary of the kit, with the schemas beside it. Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**Type.** `current-state`, superseded in place ([kernel §1](../../kernel/CONVENTIONS.md#k1)).
2. <a id="r2"></a>**Authority.** The kernel is never restated: every other document references its definitions by link ([law 1 of CLAUDE.md](../../CLAUDE.md#law-1)).
3. <a id="r3"></a>**Change.** Every kernel change is a recorded decision ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)), whatever its size, and runs the carry audit in full ([rule 2 of plc-0004-decision-records](plc-0004-decision-records.md#r2)). A change to a section the shared gate code implements — its parts of class K in [kit-shared-gate-code §1](../../shared/GATE.md#g1) — changes that code and bumps the version of every module that links it, as step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md) says.
4. <a id="r4"></a>**Anchors.** Every section carries an explicit anchor of the form `k<n>` (decision [dec-0005-reference-forms](../decisions/dec-0005-reference-forms.md)). A new section takes the next number; a section removed leaves its number unused; an anchor is never renumbered.
5. <a id="r5"></a>**Admission.** A concept enters the page only when two or more modules need it, nothing the repository derives is duplicated, and no machinery is described; the page's own preamble states the test, and this rule points at it rather than restating it.
6. <a id="r6"></a>**Schemas.** The JSON schemas beside the page are its machine half — code, with no envelope. A change to a schema and to the text it encodes lands in one change, held by the pair `kernel-schemas` of the kit's coverage map; the shared code's hand-written mirror of the dials schema is held no more lenient than the schema by `scripts/check-schema-mirror.py`.
7. <a id="r7"></a>**Samples.** Every example in the page obeys the page's own rules and names no path or id of the kit (decision [dec-0021-kernel-sample-territories](../decisions/dec-0021-kernel-sample-territories.md)).
8. <a id="r8"></a>**Enforcement.** The envelope by module `const-meta-types`; links, anchors and the kernel-section lane by module `const-referencing`; the schema pairing by module `const-task-close`. Rules 2, 5 and 7 are review.
