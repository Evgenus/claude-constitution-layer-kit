---
id: kit-module-documents
type: current-state
title: Module-document policy — the description at the root of every module
status: active
---

# Module-document policy

Governs the document kind *module document*: the `MODULE.md` at the root of a module, which is the module's description from its first draft on (decision [dec-0003-module-spec-kind](../decisions/dec-0003-module-spec-kind.md)). Territory under this policy's id in `constitution.yaml`.

## Rules

1. **Shape.** Every section of `module-template/MODULE.md` filled, or "none" with one line of reasoning.
2. **Scope.** Cites exactly its matrix rows ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)).
3. **Portability.** Carries no project reference ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)).
4. **Draft state.** Open slots are inline `[decide: …]` markers while the manifest version is `0.0.x`; a published module carries none. A `0.0.x` module is a draft and is not offered for installation; loading it from the kit's path for its live proofs is the one exception.
