---
id: dec-0130-kernel-defines-numbered-kind-and-settles-profile-names
type: task-record
title: The kernel defines a numbered kind with no module needed and settles its names of profiles, and two requirement rows take its words
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kernel defines a numbered kind with no module needed and settles its names of profiles, and two requirement rows take its words

## Context

Item 9.24b of [the rollout plan](../rollout-plan.md#s9-24b) logged that [the kernel](../constitution/CONVENTIONS.md) uses "numbered kind" and never defines it. Item 9.38 of [the plan](../rollout-plan.md#s9-38) logged two findings in the profiles, and one of them is in the kernel too. Both kernel findings land in one change, so this record answers them in one numbered section each. Section 3 answers a finding of the change's carry audit. A kernel change is always recorded ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)).

## 1. What a numbered kind is

The term stood once in [kernel §1](../constitution/CONVENTIONS.md#k1), at the start of the three exceptions to the `id` rule. The same paragraph used "catalog" four times, also with no definition. It spoke of "ids that share a prefix and a number", and of "a catalog whose form changes, as when its width grows". So the uses relied on four things:

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

<a id="r5"></a>**R5.** "Catalog" has one sense in the kernel. One sentence of [kernel §3](../constitution/CONVENTIONS.md#k3) used it for the list of policies. It now reads: "Which policies exist and where territories end are module and project concerns." In [kernel §1](../constitution/CONVENTIONS.md#k1), the third exception spoke of a kind that "becomes a catalog, or a catalog whose form changes". It now reads "becomes numbered, or a numbered kind whose form changes".

## 2. Which profiles the kernel names

[Kernel §6](../constitution/CONVENTIONS.md#k6) named three profiles as examples: `solo-agents`, `small-team` and `regulated`. The kit ships two others, `new-project.yaml` and `existing-repository.yaml`, by R1 of [dec-0120-two-profiles-taken-in-the-guides-order](dec-0120-two-profiles-taken-in-the-guides-order.md#r1). That record weighed the three names as its option C and turned them down. The dials that tell a team's shape name people, and no profile can hold them. Its R5 left the kernel as it was, and it binds nothing. Every project copies the kernel in step 5 of [the install guide](../../INSTALL.md#s2), so a name in the kernel reaches every project.

- **A. The kernel names the two profiles the kit ships.**
  - **Pros:** the names match what ships; a reader of the kernel finds the files.
  - **Cons:** a new or renamed profile changes the kernel, which asks the carry audit in full; each project's copy names files only the kit has.
- **B. The kernel names no profile.** Step 4 of [the install guide](../../INSTALL.md#s2) already names the two.
  - **Pros:** the smallest edit; the kernel can never drift from the folder again; the names stay in the guide that says how to take them.
  - **Cons:** a reader of the kernel sees no example, and must open the install guide to learn which profiles exist.
- **C. The kernel keeps its three names as examples.**
  - **Pros:** no kernel text changes.
  - **Cons:** the finding stays, since those files do not exist; the names suggest profiles of a team's shape, which dec-0120 turned down.

The session recommended B. The kernel holds vocabulary and shape, and a list of the kit's files is the install guide's. The decider chose B in chat on 2026-11-12.

<a id="r6"></a>**R6.** [Kernel §6](../constitution/CONVENTIONS.md#k6) names no profile. Its sentence reads: "Profiles are nothing but prewritten `constitution.yaml` files shipped with the kit." The install guide names the profiles the kit ships, in step 4 of its section 2.

## 3. Two requirement rows in the kernel's words

The carry audit in full of the change that holds this record found two rows of [the requirements](../requirements.md) at odds with R1, R2 and R5. [Requirement A13.7](../requirements.md#a13-7) said that "a numbered kind is an entry of the module's dials". That is a second definition, which [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) bars. [Requirement A5.8](../requirements.md#a5-8) spoke of "a kind that becomes a catalog" and of "a catalog whose form changes". Both wordings stood on the main branch before this change. [Rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2) makes the amendment of a row a `process` decision.

- **A. Rule it here, before the yes.** The two rows take the kernel's words.
  - **Pros:** [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) holds when the change lands; the amendment has its record in the same change; two cells change.
  - **Cons:** one more ruling and one more confirming round late in the audit.
- **B. Leave the rows, and log a plan item for after this change.**
  - **Pros:** no more edits or rounds now.
  - **Cons:** the change lands with a kernel term stated twice, a known defect of [law 1 of CLAUDE.md](../../CLAUDE.md#law-1).
- **C. Justify the rows as written.** They say where the module declares a kind.
  - **Pros:** no edit and no record.
  - **Cons:** "is an entry" says what a numbered kind is, not where it is declared.

The session recommended A: the kernel change that made the rows wrong is this record's. <a id="r7"></a>**R7.** A, chosen by the decider in chat on 2026-11-12. [Requirement A13.7](../requirements.md#a13-7) says that a numbered kind is declared by an entry of the module's dials, and cites the kernel's definition. [Requirement A5.8](../requirements.md#a5-8) speaks of a kind that becomes numbered and of a numbered kind whose form changes.

## Carry list

1. R1, R2, R3 — [the kernel](../constitution/CONVENTIONS.md#k1), section 1, the paragraph of the three exceptions to the `id` rule.
2. R4 — [the requirements](../requirements.md#a13-1), its row of the name's form; [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r3), rule 3.
3. R5 — [the kernel](../constitution/CONVENTIONS.md#k3), section 3, its last paragraph; [the kernel](../constitution/CONVENTIONS.md#k1), section 1, the third exception to the `id` rule.
4. R6 — [the kernel](../constitution/CONVENTIONS.md#k6), section 6; [the install guide](../../INSTALL.md#s2), step 4 of section 2.
5. R7 — [requirement A13.7](../requirements.md#a13-7), its first sentence; [requirement A5.8](../requirements.md#a5-8), its sentences on the third change of an id.
