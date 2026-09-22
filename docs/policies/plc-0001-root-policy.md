---
id: kit-root-policy
type: current-state
title: Root policy of the constitution kit — the policy for policies
status: active
---

# Root policy — the policy for policies

This document is the root of governance in this repository, per [kernel §3](../../kernel/CONVENTIONS.md#k3): its territory, declared under its id in the kit's `constitution.yaml`, is where policies live, and this file lies inside it. A document is a policy because it sits here. Nothing declares itself one.

## Rules

1. **Home.** Every policy of the kit is a Markdown document in this policy's territory, carrying the kernel envelope ([kernel §1](../../kernel/CONVENTIONS.md#k1)) with `type: current-state`.
2. **Territory.** A policy claims paths only through its dials namespace, keyed by its id, in `constitution.yaml`. A policy with no namespace claims nothing.
3. **Creation and change.** Adding, removing, or re-scoping a policy is a `process`-stakes decision ([kernel §4](../../kernel/CONVENTIONS.md#k4)): a record in `docs/decisions/` and one human yes. When module `const-locations` is installed, its creation command writes the document here from the policy template; until then, by hand from this document's shape.
4. **Body.** A policy's body is prose: what kind it governs, its rules as numbered items, and the kernel sections it relies on by link. It never restates the kernel ([law 1 of CLAUDE.md](../../CLAUDE.md#law-1)) and never lists the documents it governs — the territory under its id is the enumeration.
5. **One kind.** A policy governs exactly one document kind ([kernel §3](../../kernel/CONVENTIONS.md#k3)). A document of a kind no policy governs gets its policy first, by rule 3.
