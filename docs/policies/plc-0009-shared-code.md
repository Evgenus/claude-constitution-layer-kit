---
id: plc-0009-shared-code
type: current-state
title: Shared-code policy — the description of the code every gate shares
status: active
---

# Shared-code policy

Governs the document kind *shared-code description*: the page beside the kit's shared gate code that states what the code is for, the interface a module fills, every shared message, the shared limits and the shared acceptance items (decision [dec-0025-shared-gate-code-linked](../decisions/dec-0025-shared-gate-code-linked.md)). Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**One home for shared texts.** Every message the shared code prints is written out in this document, word for word as the code returns it; a module's document writes out its own messages and links here for the rest ([law 6 of CLAUDE.md](../../CLAUDE.md#law-6)).
2. <a id="r2"></a>**Admission.** Code is shared only when it implements a kernel section literally or a gate-script rule of [template §6](../../module-template/MODULE.md#t6), and two or more modules need it; the document names the class of each part. A part already shared may be widened for one module where the widening keeps a rule the part carries for all — one guard, one pipeline, one fixture subject — and defaults to what the other modules pass, so they change nothing.
3. <a id="r3"></a>**Portability.** The document and the code carry no project reference ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)) and no module's name: a module is `{module}` in every text, or, where the document must point at one module's fixture or code, its ordinal in the order of authoring — "the third module" — which the rollout plan resolves and which never changes. A shared message about a module's namespace names the key and never shows an example of that module's dials — an example that replaces the namespace drops the module's own keys; the example is the module's to give.
4. <a id="r4"></a>**Handles.** Every list and table row carries a handle. An acceptance item's number is never reissued: an item a subject leaves out keeps its number free, and a new item takes the next.
5. <a id="r5"></a>**Anchors.** Every section carries an explicit anchor `g<n>`; a new section takes the next number; an anchor is never renumbered.
6. <a id="r6"></a>**Platform facts.** An observed fact about the platform names the platform's version and the date it was observed, its backstop and, where one exists, its fallback; a re-read is dated inline.
7. <a id="r7"></a>**Change.** A change to the shared code updates this page in the same change — the pair `shared-gate-code` of the kit's coverage map — and bumps the version of every module that links the code (step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md)).
8. <a id="r8"></a>**Deferred.** A part not built is listed with the signal that would build it, as [template §12](../../module-template/MODULE.md#t12) asks of a module.
9. <a id="r9"></a>**Enforcement.** The envelope by module `const-meta-types`; links and anchors by module `const-referencing`; the pairing with the code by module `const-task-close` in its scan alone — the range check, run before the merge. That the messages table equals the code word for word, and rules 2 and 3, are review — a check on the equality waits for a friction that earns it.
