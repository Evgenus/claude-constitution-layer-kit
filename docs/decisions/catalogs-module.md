---
id: catalogs-module
type: task-record
title: Add the const-catalogs module (numbered kinds) to the rollout plan
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Add the [`const-catalogs`](../rollout-plan.md#const-catalogs) module to the rollout plan

## Context

Projects cite decisions, tasks, and similar records by number. The kit had no home for numbering: the kernel gives every document a stable kebab id and leaves "the catalog itself" to modules ([kernel §3](../../kernel/CONVENTIONS.md#k3)). The failure was observed in the design-phase decisions register of the kit's predecessor: a flat numbered file whose migration left 74 dangling `D<n>` references. Five sub-decisions shaped the module; each was asked in chat on 2026-09-15 with lettered options.

## Decisions

1. **Catalog form.** A: virtual — the set of files carrying a prefix, no index file. B: generated index per kind. C: hand-maintained register file. Chosen: A. The kernel makes git the append-only layer, so a derived index drifts for no gain, and C is the shape that failed.
2. **Id form.** A: the number inside the kernel id, `<prefix>-<nnnn>-<slug>` lowercase, uppercase tolerated in prose. B: separate `number` field beside a free slug. C: kernel change to allow an uppercase prefix. Chosen: A. One identifier per document, kernel untouched, one glob resolves either form.
3. **Allocation.** A: free minting on branches, highest + 1, uniqueness gate at PR, younger branch renumbers on collision, frozen once on main. B: counter file per kind. C: timestamp or hash ids. Chosen: A. Git already orders merges; a counter file conflicts on every parallel branch; non-sequential ids lose order and readability.
4. **Gaps.** A: uniqueness only, gaps legitimate, git remembers. B: continuity check for record kinds with placeholder repair. C: continuity as a dial, default off. Chosen: A. B contradicts the kernel's deletion rule ([kernel §1](../../kernel/CONVENTIONS.md#k1)) and guards a failure no consumer has hit.
5. **Declaration of numbered kinds.** A: catalog list in the module's dials. B: the kind's policy declares its prefix. C: inferred from filenames. Chosen by the decider: B as the default path, A as the fallback when no policy exists. The policy's declaration is read through the kernel's territory map, so kernel plus this module remains a working install; a prefix declared in both places is a defect (routine ruling by the session, no shadowing).

## Recommendation

A on every question; on question 5 the decider chose B-with-A-fallback, which the session accepted because the territory map that resolves a policy is kernel, not a sibling.

## Choice

As listed under Decisions, by the decider in chat on 2026-09-15.

## Rulings carried

- [aspect A13](../rollout-plan.md#a13) rows [requirements [A13.1](../rollout-plan.md#a13-1)–[requirement A13.7](../rollout-plan.md#a13-7)](../rollout-plan.md#a13) and module description [`const-catalogs`](../rollout-plan.md#const-catalogs) in `docs/rollout-plan.md`.
- [`const-catalogs`](../rollout-plan.md#const-catalogs) is accumulating: renumbering after items exist is retrofit debt. Entry: the first numbered kind, typically the first decision record.
