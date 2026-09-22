---
id: plc-0009-shared-code
type: current-state
title: Shared-code policy — the description of the code every gate shares
status: active
---

# Shared-code policy

Governs the document kind *shared-code description*: the page beside the kit's shared gate code that states what the code is for, the interface a module fills, every shared message, the shared limits and the shared acceptance items (decision [dec-0025-shared-gate-code-linked](../decisions/dec-0025-shared-gate-code-linked.md)). Territory under this policy's id in `constitution.yaml`.

## Rules

1. **One home for shared texts.** Every message the shared code prints is written out in this document, word for word as the code returns it; a module's document writes out its own messages and links here for the rest ([law 6 of CLAUDE.md](../../CLAUDE.md#law-6)).
2. **Admission.** Code is shared only when it implements a kernel section literally or a gate-script rule of [template §6](../../module-template/MODULE.md#t6), and two or more modules need it; the document names the class of each part. A part already shared may be widened for one module where the widening keeps a rule the part carries for all — one guard, one pipeline, one fixture subject — and defaults to what the other modules pass, so they change nothing.
3. **Portability.** The document and the code carry no project reference ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)) and no module's name: a module is `{module}` in every text. A shared message about a module's namespace names the key and never shows an example of that module's dials — an example that replaces the namespace drops the module's own keys; the example is the module's to give.
4. **Handles.** Every list and table row carries a handle.
