---
id: dec-0007-territory-declaration
type: task-record
title: Territories are declared under a kernel-owned top-level key of the dials file
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Territories are declared under a kernel-owned top-level key of the dials file

## Context

[Kernel §3](../constitution/CONVENTIONS.md#k3) said territories are "declared in the project's dials file". [kernel §6](../constitution/CONVENTIONS.md#k6) said each module reads only its own namespace and showed no shared key. Three modules read the territory map — [`const-meta-types`](../requirements.md#const-meta-types), [`const-locations`](../requirements.md#const-locations), [`const-catalogs`](../requirements.md#const-catalogs) — so its shape is kernel, and the first module's hook cannot be written without it. The README had already used a top-level `territories` key without a ruling.

## Options

- **A. A top-level `territories` key, path pattern to policy id, owned by the kernel.** [Kernel §6](../constitution/CONVENTIONS.md#k6) states that one key beside the module namespaces.
  - **Pros:**
    - **one map at one path** for every module;
    - **exactly the glob-to-id semantics** [kernel §3](../constitution/CONVENTIONS.md#k3) already defines;
    - **module names are `const-*`**, so no namespace can collide with it.
  - **Cons:** [kernel §6](../constitution/CONVENTIONS.md#k6) needs one stated exception to "only its own namespace".
- **B. A reserved `kernel` namespace holding `territories`.**
  - **Pros:** the exception is visible as a namespace; room for other project-binding values.
  - **Cons:**
    - **one more nesting level** on the most-read key;
    - **`kernel` is not a plugin name**, so the namespace rule is broken anyway;
    - **invites kernel-level dials**, which the kernel does not have.
- **C. Inside the `const-locations` namespace; other modules read it as an optional enhancement.**
  - **Pros:** no kernel change.
  - **Cons:** breaks [law 3 of CLAUDE.md](../../CLAUDE.md#law-3); kernel plus [`const-meta-types`](../requirements.md#const-meta-types) alone would claim nothing.
- **D. Each policy claims its paths in its own frontmatter; no map in the dials file.**
  - **Pros:** a policy and its territory travel together.
  - **Cons:**
    - **rewrites [kernel §3](../constitution/CONVENTIONS.md#k3) twice**;
    - **[kernel §6](../constitution/CONVENTIONS.md#k6) loses "one file"**;
    - **the kernel file**, as the kit's own policy, would carry kit paths that every consumer copies and edits;
    - **a hook must discover every policy** before judging one file.

## Recommendation

A. It is the shape [kernel §3](../constitution/CONVENTIONS.md#k3) already describes in words, and the cost is one sentence in [kernel §6](../constitution/CONVENTIONS.md#k6).

## Choice

A, chosen by the decider in chat on 2026-09-17. The decider first chose D; the session stated D's consequences under the irreversibility rule ([A8.3](../requirements.md#a8-3)), and the decider moved to A.

## Rulings carried

1. `constitution.yaml` has one kernel-owned key, `territories`: a map from path pattern to the governing policy's id. Every module may read it; it is the sole exception to "a module reads only its own namespace".
2. The pattern dialect and the handling of overlapping patterns are authoring choices of the first modules that read the map, not kernel.
3. Deferred, no consumer yet: the name of a policy's own dials namespace. The proposed default is the policy's id; it is ruled when the first policy needs calibration in the dials file.

## Applied in the same commit

- [Kernel §3](../constitution/CONVENTIONS.md#k3) names the key; [kernel §6](../constitution/CONVENTIONS.md#k6) shows it in the example and states the exception.
- `constitution.yaml` at the kit root claims the kit's own governed documents with the kernel as their policy (decision [dec-0006-accumulating-set-first](dec-0006-accumulating-set-first.md), ruling 3).
