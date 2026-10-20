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

The code every gate shares has one source, [kit-shared-gate-code](../../shared/GATE.md). Until this record its Python package was `const_gate`. Items 1 and 2 of the Ruling of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) put it at `shared/const_gate/` and had each module reach it through links of that name. This record answers two questions: what the package is named, and what accepted records and frozen research comparisons, which name the package and link into its folder, take of the rename.

## 1. The name of the package

Three facts made the old name a problem:

1. **It reads like a module's package.** Each module has its own package, with a name that ends in `_gate`, such as `catalogs_gate`. Beside them, `const_gate` looked like one more module's package, not the kit's shared code.
2. **"const" is unclear.** It is short for "constitution", but a reader can take it for "constant".
3. **The package may be published.** A second kit is planned on the same kernel, for knowledge documents. It may take this package from a package index for its own modules, and a name there must be unique.

The repository was named `claude-constitution-layer-kit` by [dec-0092-rename-to-claude-constitution-layer-kit](dec-0092-rename-to-claude-constitution-layer-kit.md). The decider asked for a package name close to it. A first set of names, `gate_runtime`, `gatewright`, `teachgate` and `constitution_gates`, was turned down as too far from the repository's name.

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

The session recommended A: it is the only name that matches the repository, stays clear of the platform's name and is free to publish. The decider chose A in chat on 2026-10-20.

<a id="r1"></a>**R1.** The kit's shared gate package is `constitution_layer_kit`. Its source is the folder `shared/constitution_layer_kit/`. A module reaches it through relative symbolic links named `scripts/constitution_layer_kit` and `tests/constitution_layer_kit`. Code imports it as `from constitution_layer_kit import …`. If it is ever published to a package index, its name there is `constitution-layer-kit`. Each module's own package, such as `catalogs_gate`, keeps its name.

<a id="r2"></a>**R2.** R1 replaces the path that items 1 and 2 of the Ruling of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) ruled. The rest of that ruling stands.

## 2. What the history takes of the rename

Accepted records and frozen research comparisons name `const_gate` in their prose and link into its folder: 8 links in dec-0038, dec-0076, dec-0084 and res-0012. Their policies allow few edits to them. A link to a moved file must lead to the file's new place, or the link check of module [`const-referencing`](../requirements.md#const-referencing) turns red. But [kernel §5](../../kernel/CONVENTIONS.md#k5) allows an accepted record three kinds of mechanical edit, and the one for links is "a reference-form migration — rewriting how a record cites other documents". A Python file is no document in the kernel's sense. The kit already rewrites links to code files in records, and 39 records link to a Python or shell file, but no text said so. The carry audit of this change found the gap.

- **A. The record policy states the reading.** Rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) says that, for this migration, the documents a record cites include every file and folder it links to.
  - **Pros:** explicit, and it covers what the kit already does; a small policy edit inside this change; no kernel change.
  - **Cons:** a policy reads a kernel word more widely than the kernel defines it; a reader of the kernel alone does not see it.
- **B. The kernel is amended.** The migration of [kernel §5](../../kernel/CONVENTIONS.md#k5) becomes "rewriting how a record cites another file or folder".
  - **Pros:** the rule stands in the kernel itself, with no reading needed.
  - **Cons:** a kernel change needs a carry audit over every record, so this change grows a lot.
- **C. The link repairs in the four files are undone.**
  - **Pros:** no rule changes.
  - **Cons:** the link check turns red on 8 dead links, so another rule would be needed anyway.

The session recommended A: it states the kit's practice at the cost of one sentence and keeps the rename its size. The decider chose A in chat on 2026-10-21.

<a id="r3"></a>**R3.** In an accepted record or a frozen research comparison, a link to a file or a folder that moved or was renamed takes the new path, whether it leads to a document, to another file or to a folder. Only the link's target changes: the link's text, a code span and the prose keep the old name or path as written, as history. A document whose id changes, by a renumbering or a rename that [kernel §1](../../kernel/CONVENTIONS.md#k1) allows, is outside this ruling: what its references take is said by that section of the kernel and by the two policies. So after this rename those documents still say `const_gate`, and only their links lead to `shared/constitution_layer_kit/`.

<a id="r4"></a>**R4.** For a record, the documents it cites, in the words of [kernel §5](../../kernel/CONVENTIONS.md#k5) for a reference-form migration, include every file and folder the record links to, whether it is a document or not.

## Applied

The commit before this record's own made the rename: the folder, the 22 links, the name in code and in the current-state documents, and the link repairs in four history files. The commit that creates this record adds the published name to the deferred line of section 1 of [kit-shared-gate-code](../../shared/GATE.md#g1). Later commits of the same change, after the carry audit, state R3 in rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) and in rule 7 of [plc-0005-research](../policies/plc-0005-research.md#r7), and R4 in rule 14 of plc-0004-decision-records. The record is `inactive`: by the last commit of its branch every item has its home.

## Carry list

1. R1 — [kit-shared-gate-code](../../shared/GATE.md), its opening paragraph; [its section 1](../../shared/GATE.md#g1), the deferred line under the table; [its section 2](../../shared/GATE.md#g2), items 6 and 7; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
2. R2 — history only: the path of items 1 and 2 of the Ruling of dec-0025-shared-gate-code-linked renamed, the rest of that ruling unchanged.
3. R3 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14); [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7).
4. R4 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14).
