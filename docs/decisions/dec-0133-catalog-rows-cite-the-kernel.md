---
id: dec-0133-catalog-rows-cite-the-kernel
type: task-record
title: Two requirement rows cite the kernel for the catalog and its first renumbering
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Two requirement rows cite the kernel for the catalog and its first renumbering

## Context

Item 9.41 of [the rollout plan](../rollout-plan.md#s9-41) logged that the glosses of a catalog say the kernel's terms in other words. [Kernel §1](../constitution/CONVENTIONS.md#k1) defines a numbered kind and its catalog, since [dec-0130-kernel-defines-numbered-kind-and-settles-profile-names](dec-0130-kernel-defines-numbered-kind-and-settles-profile-names.md). It says: "All the items of one numbered kind are its catalog." [Law 1 of CLAUDE.md](../../CLAUDE.md#law-1) bars a second definition. The session read each gloss against the kernel:

1. [Requirement A13.2](../requirements.md#a13-2) said "A catalog is virtual: the set of files carrying its prefix". That set is not the kernel's. A file whose name carries the prefix outside the kind's territory is no item. The module's reading of [requirement A13.1](../requirements.md#a13-1) says an item is a document in the territory. Limit 4 of [the module's §9](../../modules/const-catalogs/MODULE.md#t9) names that gap for the listing.
2. The module's reading of that row in [its §3](../../modules/const-catalogs/MODULE.md#t3), and the opening of the skill `catalog-item`, said the same as the row.
3. [Requirement A5.8](../requirements.md#a5-8) named one renumbering "of a provisional number before its item lands". The kernel's first exception is narrower. It renumbers an item not yet landed only where it meets, at a pull request, an item already on the main branch under its number.
4. The module's README says "A catalog is all the documents of one kind". That agrees with the kernel, in the plain words that R1 of [dec-0077-module-readme-pages](dec-0077-module-readme-pages.md#r1) asks for.
5. The form of a name stays in [requirement A13.1](../requirements.md#a13-1), by R4 of [dec-0130-kernel-defines-numbered-kind-and-settles-profile-names](dec-0130-kernel-defines-numbered-kind-and-settles-profile-names.md#r4).

The amendment of a row is a `process` decision ([rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2)).

## Options

- **A. One record amends both rows.** The catalog row cites the kernel's catalog and keeps its own rule, and the row on moves cites the kernel's first exception. The module's reading and the skill follow the rows.
  - **Pros:** [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) holds, with one sense of "catalog" in the kit; the gap of limit 4 stays stated.
  - **Cons:** a new record and a yes at the merge; the skill's edit makes the module's eval receipt stale.
- **B. No change, justified in a commit.** The catalog row is read as how the module finds a catalog. The row on moves is read with [requirement A13.4](../requirements.md#a13-4).
  - **Pros:** no record and no row change.
  - **Cons:** two rows keep a sense the kernel does not give, the defect [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) names.
- **C. A plan item after the modules reach `0.1.0`.**
  - **Pros:** a smaller change now.
  - **Cons:** the modules ship `0.1.0` with the conflict.

## Recommendation

A, since the kernel took the definition so that the rows stop carrying their own, and the fix is small. The session recommended it.

## Choice

A, chosen by the decider in chat on 2026-11-12.

## Ruling

<a id="r1"></a>**R1.** [Requirement A13.2](../requirements.md#a13-2) cites the kernel's catalog and defines it in no words of its own. Its rule stays: no index, ledger or register file exists. A listing is made on demand, from the files whose names carry the prefix.

<a id="r2"></a>**R2.** [Requirement A5.8](../requirements.md#a5-8) names the first renumbering as the kernel's first exception does. It renumbers an item not yet landed that meets, at a pull request, a landed item under its number.

<a id="r3"></a>**R3.** The module's reading of [requirement A13.2](../requirements.md#a13-2) says that the catalog is the kernel's and that no file lists it. The skill `catalog-item` states a numbered kind and a catalog in the kernel's sense, in plain words.

## Applied

The commit that creates this record applies every item. The record is born `inactive`.

## Carry list

1. R1 — [requirement A13.2](../requirements.md#a13-2).
2. R2 — [requirement A5.8](../requirements.md#a5-8), its sentences on the two renumberings.
3. R3 — [the module's §3](../../modules/const-catalogs/MODULE.md#t3), the row of [requirement A13.2](../requirements.md#a13-2); [the skill `catalog-item`](../../modules/const-catalogs/plugin/skills/catalog-item/SKILL.md), its opening paragraph.
