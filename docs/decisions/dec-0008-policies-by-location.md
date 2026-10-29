---
id: dec-0008-policies-by-location
type: task-record
title: A policy is a document in the root policy's territory; territories are declared in the dials file under the policy's id
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A policy is a document in the root policy's territory; territories are declared in the dials file under the policy's id

## Context

[dec-0007-territory-declaration](dec-0007-territory-declaration.md) ruled, earlier on 2026-09-17, that the dials file holds a kernel-owned `territories` map from path pattern to policy id. The decider then worked through what a policy *is*: a document cannot proclaim itself a policy from an arbitrary location, so policy-ness must be external judgment, and the judgment must have a root that governs itself. The map made the dials file that judge and left the root implicit. This record reverses ruling 1 of [dec-0007-territory-declaration](dec-0007-territory-declaration.md); a record is never edited in place ([kernel §5](../constitution/CONVENTIONS.md#k5)). Its ruling 3, the policy namespace default, is settled here in passing.

## Options

- **A. Keep the map.** A `territories` key in the dials file, glob to id; the root is whichever policy governs its own territory.
  - **Pros:** one key to read; already committed.
  - **Cons:** every new policy is an edit to an unenveloped map; nothing says which policy is the root; mutual governance cycles are not excluded.
- **B. The root policy names the other policies by id.** The dials file points at the root; the root enumerates.
  - **Pros:** explicit policy set.
  - **Cons:** every gate depends on the id index before it can answer anything; adding a policy edits the root. Rejected by the decider outright.
- **C. Each policy declares its territory in its own frontmatter; the root's territory is where policies live.**
  - **Pros:** no enumeration; policy-ness by location.
  - **Cons:** machine-readable calibration leaves the dials file, against [kernel §6](../constitution/CONVENTIONS.md#k6). Corrected by the decider to D.
- **D. Policy-ness by location; territory in the dials file under the policy's id.** The dials file holds one bootstrap path, `root_policy`. The root's namespace, keyed by its id, declares where policies live; the root's file lies inside. Every policy's territory and calibration live in its namespace, keyed by its id.
  - **Pros:** nothing declares itself a policy and nothing enumerates them; calibration stays in one file; a policy's dials namespace is its id, so no field names it; the chain of governance ends at one self-governing root.
  - **Cons:** a namespace carrying a `territory` key proves nothing by itself, so classifying a namespace needs a lookup of its id among the documents in the root's territory; [kernel §3](../constitution/CONVENTIONS.md#k3) and [kernel §6](../constitution/CONVENTIONS.md#k6) are rewritten; the kernel can no longer serve as the kit's own policy, so the kit needs a root policy and a kit-documents policy.
- **E. D plus a reserved `policies:` section in the dials file**, so classification needs no lookup.
  - **Pros:** the dials file alone says which namespaces are policies'.
  - **Cons:** a second assertion of policy-ness beside location; the two can disagree, a new defect class; the existence lookup is needed anyway to catch a dangling namespace.

## Recommendation

D. The lookup it needs is bounded to the root's territory, a handful of files, and no gate depends on a repository-wide index. The session first recommended A, then B once enumeration was raised, and moved to D after the decider rejected enumeration and moved calibration back into the dials file.

## Choice

D, chosen by the decider in chat on 2026-09-17.

## Rulings carried

1. The dials file has one kernel-owned key, `root_policy`: the path of the root policy. It replaces the `territories` map.
2. A document is a policy because it lies in the root policy's territory. Nothing declares itself a policy; nothing enumerates policies. The root's own file lies in its territory, so it governs itself and every chain of governance ends there.
3. A policy's dials namespace is its id. Its territory and all other machine-readable calibration live there. No field names the namespace.
4. Classification: a namespace whose id has a document in the root's territory is a policy's, and its `territory` claims paths. A namespace with no such document belongs to a module or something else, and its `territory`, if any, claims nothing. A document in the root's territory with no namespace is a policy that claims nothing; silent, not a defect. A path matched by two policies' territories is the kernel's multi-policy defect.
5. The lookup that classifies a namespace scans only the root's territory. An id index over the whole repository remains a `const-referencing` concern for repairing links and is never a gate dependency.
6. The kit is consumer zero with two policies under `docs/policies/`: a root policy and a kit-documents policy claiming the kernel, the intent page, the records, and the module documents. A consumer bootstraps with the same two documents.

## Applied in the same commit

- `docs/rollout-plan.md`: "territory map" wording in rows [A2.6](../requirements.md#a2-6) and [A13.7](../requirements.md#a13-7) and in the [`const-locations`](../requirements.md#const-locations) and [`const-catalogs`](../requirements.md#const-catalogs) specs replaced by "territory declarations"; Phase A steps 1 and 2 updated.
- **Following commits:** [kernel §3](../constitution/CONVENTIONS.md#k3) and [kernel §6](../constitution/CONVENTIONS.md#k6); the kit's two policies and its dials file; Phase B and the README.
