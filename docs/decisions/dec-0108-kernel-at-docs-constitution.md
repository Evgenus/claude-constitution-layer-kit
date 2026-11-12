---
id: dec-0108-kernel-at-docs-constitution
type: task-record
title: The kit keeps its kernel at docs/constitution/, where every consumer keeps its copy
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit keeps its kernel at docs/constitution/, where every consumer keeps its copy

## Context

The kit kept its kernel, the conventions page and its three schemas, in a folder `kernel/` at its root. Every consumer keeps its copy at `docs/constitution/`, where step 5 of the [install guide](../../INSTALL.md) puts it. The knowledge kit, a second kit of plugins built on this kernel, keeps a copy of this kernel at `docs/constitution/` and its own kernel at `docs/knowledge/`. Once a repository holds two kernels, a folder named `kernel/` does not say which kernel it holds. A script copied from this kit that reads `kernel/` could then read the wrong kernel and still pass green. The knowledge kit will copy this kit's tooling at a pinned commit later, so a clean path here first makes that copy cleaner.

## 1. Where the kit keeps its kernel

- **A. Keep `kernel/` at the kit's root.**
  - **Pros:** nothing moves; no link, script or record changes.
  - **Cons:**
    - **the kit and its consumers keep the kernel at two paths**;
    - **a script copied into a repository with two kernels names a folder that says nothing of which one it reads**.
- **B. Move it to `docs/constitution/`, the path every consumer uses.**
  - **Pros:**
    - **one path for the kernel in the kit and in every project**;
    - **the install step copies a folder to the same path**;
    - **the name says which kernel it is**.
  - **Cons:** about 430 links in about 100 documents and about twelve scripts change in one move.

The session recommended B, since the cost is paid once and the mover of module [`const-referencing`](../requirements.md#const-referencing) repairs the links. The decider chose B in chat on 2026-10-29, when the knowledge kit took `docs/knowledge/` for its own kernel. The decider asked that both kits keep their kernels where a consumer keeps them.

<a id="r1"></a>**R1.** The kit's kernel, `CONVENTIONS.md` and its schemas under `schemas/`, lives at `docs/constitution/`, the territory of [plc-0002-kernel](../policies/plc-0002-kernel.md), the home of the lane of kernel sections and the code of the pair `kernel-schemas` in `constitution.yaml`.

<a id="r2"></a>**R2.** The install guide copies the kernel as git holds it at the kit's `docs/constitution/` to the same path in the project. Its check holds that copy against the files git tracks there.

<a id="r3"></a>**R3.** The kit's tooling reads the kernel at `docs/constitution/`: the schema checks, the bare repository that the install and session checks build, and the toy kits of their self-tests.

The move itself, made by the mover with one call per file, is a one-time act, and it left no folder `kernel/` in the kit. In accepted records and frozen comparisons only the targets of links changed, as [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) and [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) allow. Their texts, code spans and prose keep the old path as history.

## 2. What the portability check holds of the kernel's folder

The check that holds [law 2 of CLAUDE.md](../../CLAUDE.md#law-2) by grep, `scripts/check-portability.py`, refuses a fixed name of the kit in every installed file of a module and in the shared code. `kernel/` was one of those names. After the move, no folder of that name exists here, and the kernel's folder is `docs/constitution/`. No installed file of a module and no file of the shared package names either path.

- **A. Replace `kernel/` with `docs/constitution/`.** The hold follows the kernel's folder to its new name.
  - **Pros:**
    - **the check refuses `docs/constitution/`**, where the kernel copy lives, in every installed file of a module and in the shared code, as it refused `kernel/`;
    - **nothing names the path today**, so nothing turns red.
  - **Cons:**
    - `docs/constitution/` is also every consumer's own path, so the shared test files can no longer name it;
    - **a bare `docs/constitution` with no slash still passes**, as `kernel` did before.
- **B. Drop `kernel/` and add nothing.** The list keeps only the names of the kit's own documents, and no folder a project holds.
  - **Pros:** the list names no folder, and `CONVENTIONS.md` on it still catches the kernel page.
  - **Cons:** a module that names `docs/constitution/schemas/` passes unseen, held by review alone.
- **C. Keep `kernel/` and add `docs/constitution/`.**
  - **Pros:** it also catches a stale copy of the old path, such as a script copied from an older commit of the kit.
  - **Cons:** `kernel/` names no folder anywhere now, so it is a rule kept for history; two names to keep in step.

The session recommended A, since it keeps the hold the kit had on the folder that holds the kernel today, and costs nothing now. The decider chose A in chat on 2026-10-29.

<a id="r4"></a>**R4.** The fixed names of the kit that the portability check refuses hold `docs/constitution/` in place of `kernel/`. This replaces the fixed name `kernel/` in R9 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r9). The check's reason for the refusal now says that a module takes every place in a project from the dials file, since the kernel's copy does exist in every project.

## Applied

The rulings were applied by the commits of the branch `work/kernel-to-docs-constitution` before this record, so it is born `inactive`.

## Carry list

1. R1 — [plc-0002-kernel](../policies/plc-0002-kernel.md), its territory in [the dials file](../../constitution.yaml), with the lane of kernel sections and the pair `kernel-schemas`; [CLAUDE.md](../../CLAUDE.md), the list read before any work; [the intent page](../../INTENT.md), layer 2.
2. R2 — [step 5 of the install guide](../../INSTALL.md); [the install guide's check](../../scripts/check-install-guide.py), its claim `kernel` and the constant `KERNEL`.
3. R3 — [the schema mirror check](../../scripts/check-schema-mirror.py) and [the dials schema check](../../scripts/check-dials-schema.py), their constants; [the shared install steps](../../scripts/kit_install.py), `bare_repository`; the toy kits of the self-tests of [the bare-install check](../../scripts/check-bare-install.py), [the session-load check](../../scripts/check-session-load.py) and [the install guide's check](../../scripts/check-install-guide.py).
4. R4 — [requirement A12.1](../requirements.md#a12-1); [the portability check](../../scripts/check-portability.py), `FIXED_NAMES`, `WHY_KIT` and its docstring. The replacement in R9 of dec-0069 is history only.
