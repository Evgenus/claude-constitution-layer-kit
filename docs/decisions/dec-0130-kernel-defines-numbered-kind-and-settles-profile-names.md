---
id: dec-0130-kernel-defines-numbered-kind-and-settles-profile-names
type: task-record
title: The kernel defines a numbered kind with no module needed, and settles its names of profiles
status: active
stakes: process
decider: Eugene Chernyshov
---

# The kernel defines a numbered kind with no module needed, and settles its names of profiles

## Context

Item 9.24b of [the rollout plan](../rollout-plan.md#s9-24b) logged that [the kernel](../constitution/CONVENTIONS.md) uses "numbered kind" and never defines it. Item 9.38 of [the plan](../rollout-plan.md#s9-38) logged two findings in the profiles, and one of them is in the kernel too. Both kernel findings land in one change, so this record answers them in one numbered section each. A kernel change is always recorded ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)).

## 1. What a numbered kind is

The term stood once in [kernel §1](../constitution/CONVENTIONS.md#k1), at the start of the three exceptions to the `id` rule. The same paragraph used "catalog" twice, also with no definition. It spoke of "ids that share a prefix and a number", and of a catalog "whose width grows". So the uses relied on four things:

1. a document kind, as [kernel §3](../constitution/CONVENTIONS.md#k3) defines one;
2. a prefix that names the kind, in every item's `id`;
3. a number written with a fixed count of digits, the width;
4. a catalog, all the items of one such kind.

The full form of a name, `<prefix>-<nnnn>-<slug>`, stood only in [requirement A13.1](../requirements.md#a13-1), a row of module [`const-catalogs`](../requirements.md#const-catalogs). The kit's policies state it again for their own kinds. The module's README glosses the term in plain words. [Kernel §3](../constitution/CONVENTIONS.md#k3) also used "catalog" in an older sense. Its sentence "The catalog itself and territory boundaries are module and project concerns" dates from the kernel's first commit. That was before the module existed, and there the word meant the list of policies.

The session first put three options. The decider then set a condition: everything should work without the catalog module as a strict dependency. Read against it, the three exceptions renumber an item "in its file, its `id`". The rule that a file name carries the number stood only in the module's requirement and in each policy. So the session put the options again, each with the file name in the definition.

- **A. One defining clause in the kernel's section 1.** A numbered kind is a document kind whose items each carry a prefix and a number in their `id` and their file name.
  - **Pros:** the smallest edit, and it names no module; "in its file" now leans on a rule the kernel states.
  - **Cons:** "catalog" and "width" stay undefined, and the kernel's section 3 keeps its second sense of "catalog".
- **B. The clause of A, with "catalog" and "width" defined, and a sentence of section 3 reworded.** Two sentences follow the clause, one for the width and one for the catalog. In section 3, "The catalog itself" becomes "Which policies exist".
  - **Pros:** the exceptions read with no catalog module; "catalog" has one sense in the kernel; the exact form stays where the module checks it.
  - **Cons:** it edits two sections and adds about 300 characters; the carry audit reads one more sentence.
- **C. The whole form moves into the kernel.** The kernel states `<prefix>-<nnnn>-<slug>`, the `id` equal to the file name without `.md`, and one sequence per kind. [Requirement A13.1](../requirements.md#a13-1) then cites the kernel.
  - **Pros:** a project without the module gets the exact form from the kernel, and no policy states it again.
  - **Cons:** the largest change; it moves a rule that one module's gate holds into the kernel, and it edits the requirements as well.

The session recommended B. Every term the exceptions use then stands in the kernel, so they work with no catalog module. The project's own policy already gives the exact form, as the kit's policies do. The decider chose B in chat on 2026-11-12.

<a id="r1"></a>**R1.** [Kernel §1](../constitution/CONVENTIONS.md#k1) defines a numbered kind where the term is first used. It is a document kind ([kernel §3](../constitution/CONVENTIONS.md#k3)) whose every item carries a prefix and a number in its `id` and its file name. The prefix names the kind.

<a id="r2"></a>**R2.** The same paragraph defines the width and the catalog. The number of a numbered kind has a fixed count of digits, the kind's width. All the items of one numbered kind are its catalog.

<a id="r3"></a>**R3.** The definitions name no module. So the three exceptions to the `id` rule hold in a project that does not install module [`const-catalogs`](../requirements.md#const-catalogs).

<a id="r4"></a>**R4.** The kernel does not state the exact form of an item's name. That form is `<prefix>-<nnnn>-<slug>`, with the `id` equal to the file name without `.md`. It stays in [requirement A13.1](../requirements.md#a13-1), a row of the module. A project's own policy for the kind states it too, as [rule 3 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r3) does for the kit's records.

<a id="r5"></a>**R5.** "Catalog" has one sense in the kernel. One sentence of [kernel §3](../constitution/CONVENTIONS.md#k3) used it for the list of policies. It now reads: "Which policies exist and where territories end are module and project concerns."

## Carry list

1. R1, R2, R3 — [the kernel](../constitution/CONVENTIONS.md#k1), section 1, the paragraph of the three exceptions to the `id` rule.
2. R4 — [the requirements](../requirements.md#a13-1), its row of the name's form; [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r3), rule 3.
3. R5 — [the kernel](../constitution/CONVENTIONS.md#k3), section 3, its last paragraph.
