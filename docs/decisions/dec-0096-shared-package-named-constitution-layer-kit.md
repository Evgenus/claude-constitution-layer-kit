---
id: dec-0096-shared-package-named-constitution-layer-kit
type: task-record
title: The shared gate package is named constitution_layer_kit, and the records keep its old name in their prose
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shared gate package is named constitution_layer_kit, and the records keep its old name in their prose

## Context

The code every gate shares has one source, [kit-shared-gate-code](../../shared/GATE.md). Until this record its Python package was `const_gate`. Items 1 and 2 of the Ruling of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) put it at `shared/const_gate/` and had each module reach it through links of that name. Three facts made the name a problem:

1. **It reads like a module's package.** Each module has its own package, named `<aspect>_gate`, such as `catalogs_gate`. Beside them, `const_gate` looked like one more module's package, not the kit's shared code.
2. **"const" is unclear.** It is short for "constitution", but a reader can take it for "constant".
3. **The package may be published.** A second kit is planned on the same kernel, for knowledge documents. It may take this package from a package index for its own modules, and a name there must be unique.

The repository was named `claude-constitution-layer-kit` by [dec-0092-rename-to-claude-constitution-layer-kit](dec-0092-rename-to-claude-constitution-layer-kit.md). The decider asked for a package name close to it. A first set of names, `gate_runtime`, `gatewright`, `teachgate` and `constitution_gates`, was turned down as too far from the repository's name.

A rename also meets the history. Accepted records and frozen research comparisons name `const_gate` in their prose and link into its folder. Their policies allow few edits to them.

## Options

- **A. `constitution_layer_kit`.** The repository's name without "claude-".
  - **Pros:** it names the kit, not a module, so no reader takes it for a module's package; it is free as `constitution-layer-kit` on the Python package index, checked on 2026-10-20; it does not name the platform, which the knowledge kit's code need not carry.
  - **Cons:** 22 characters against 10, so 42 lines of code grew past the 110 columns of the kit's lint and had to be wrapped.
- **B. `constitution_kit`.** The kit's short name.
  - **Pros:** short; it reads well in an import.
  - **Cons:** generic, so a package of that name on an index may belong to anyone; it no longer matches the repository's name.
- **C. `claude_constitution_layer_kit`.** The repository's whole name.
  - **Pros:** an exact match with the repository.
  - **Cons:** the longest of the four, so more lines to wrap; it names the platform in every import.
- **D. `constitution_kit_gates`.** The kit's short name with what the code serves.
  - **Pros:** it says the code serves the gates.
  - **Cons:** "gates" is narrower than what the package holds, and narrower still for a second kit; the generic prefix of B stays.

## Recommendation

A, recommended by the session: it is the only name that matches the repository, stays clear of the platform's name and is free to publish.

## Choice

A, by the decider in chat on 2026-10-20.

## Ruling

<a id="r1"></a>**R1.** The kit's shared gate package is `constitution_layer_kit`. Its source is the folder `shared/constitution_layer_kit/`. A module reaches it through relative symbolic links named `scripts/constitution_layer_kit` and `tests/constitution_layer_kit`. Code imports it as `from constitution_layer_kit import …`. If it is ever published to a package index, its name there is `constitution-layer-kit`. Each module's own package keeps its name `<aspect>_gate`.

<a id="r2"></a>**R2.** Accepted records and frozen research comparisons keep the old name `const_gate` in their prose, as history. Only their links into the moved folder follow the move, as a link repaired after a move.

## Applied

The commit before this record's own made the rename: the folder, the 22 links, the name in code and in the current-state documents, and the link repairs in four history files. The commit that creates this record adds the published name to the deferred line of section 1 of [kit-shared-gate-code](../../shared/GATE.md#g1). The record is born `inactive`.

That R1 renames the path that items 1 and 2 of the Ruling of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) ruled is history. The rest of that ruling stands.

## Carry list

1. R1 — [kit-shared-gate-code](../../shared/GATE.md), its opening paragraph; [its section 1](../../shared/GATE.md#g1), the deferred line under the table; [its section 2](../../shared/GATE.md#g2), items 6 and 7; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
2. R2 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14); [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7).
