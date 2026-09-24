---
id: plc-0006-module-documents
type: current-state
title: Module-document policy — the description at the root of every module
status: active
---

# Module-document policy

Governs the document kind *module document*: the `MODULE.md` at the root of a module, which is the module's description from its first draft on (decision [dec-0003-module-spec-kind](../decisions/dec-0003-module-spec-kind.md)). Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**Shape.** Every section of `module-template/MODULE.md` filled, or "none" with one line of reasoning.
2. <a id="r2"></a>**Scope.** Cites exactly its matrix rows ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)).
3. <a id="r3"></a>**Portability.** Carries no project reference ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)). The kit is no project: the document ships with the plugin and is read in the kit, so its links to kit documents are the description's own, and a count observed in the kit-live proof is evidence under rule 10; the portability grep of [requirement A12.1](../requirements.md#a12-1) holds the installed components, which reference nothing in the kit.
4. <a id="r4"></a>**Draft state.** Open slots are inline `[decide: …]` markers while the manifest version is `0.0.x`; a published module carries none. A `0.0.x` module is a draft and is not offered for installation; loading it from the kit's path for its live proofs is the one exception.
5. <a id="r5"></a>**Envelope.** `current-state`, `active`, superseded in place ([kernel §1](../../kernel/CONVENTIONS.md#k1)); the id is `module-<plugin name>`, the form the territory `modules/*/MODULE.md` yields; the title is `const-<name> — <one clause saying what the module guards or does>`; the preamble's first sentence states the manifest version.
6. <a id="r6"></a>**Change.** The document changes with its code: a change under the module's pair of the kit's coverage map updates it or declares no impact, held by module `const-task-close`; a change to a rule the document states is `process` stakes ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)), and any other edit is routine; a version bump edits the version sentence of the preamble, which after publication reads "Published at manifest version `x.y.z`."
7. <a id="r7"></a>**Anchors.** `t1` to `t12`, as the template numbers its sections; a section is added by a change to the template, never to one document.
8. <a id="r8"></a>**Handles.** One prefix per kind of handle in a document, never reused for another kind in the same document: the message keys as the module's `messages.py` names them; `E<n>` for the enforcement rows; the acceptance items numbered from 1 for the module's own and from 101 for the shared items, bare or under `T<n>` and `S<n>`; the live, review and kit-check items continuing the module's own numbering or under `L<n>` — `V<n>` where `L` is the module's message prefix; a key of another document is written qualified.
9. <a id="r9"></a>**Shared content.** What the shared gate code carries — its messages, its limits, its acceptance items — enters by link to [kit-shared-gate-code](../../shared/GATE.md), its sections 3 to 5, never restated; the module's own messages are written out word for word ([rule 1 of plc-0009-shared-code](plc-0009-shared-code.md#r1)).
10. <a id="r10"></a>**Evidence.** A live proof carries its date, its environment and the platform's version; a proof deferred to the consumer's bootstrap is labelled `live, deferred` and links the step of the rollout plan that holds it; a platform fact carries the date it was verified and what breaks if it changes.
11. <a id="r11"></a>**Files.** The document lists the module's files once, in its artifacts section; the template's plugin skeleton is not copied into it.
12. <a id="r12"></a>**Enforcement.** The envelope by module `const-meta-types`; links and anchors by module `const-referencing`; the pairing with the code by module `const-task-close`. Rows, shape, portability and handles are review — the fresh-context validation of step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md).
