---
id: dec-0011-one-policy-per-kind
type: task-record
title: One policy per document kind; the root policy lists nothing; no policy enumerates its documents
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# One policy per document kind; the root policy lists nothing; no policy enumerates its documents

## Context

Decision [dec-0008-policies-by-location](dec-0008-policies-by-location.md), ruling 6, gave the kit two policies: a root policy and one kit-documents policy claiming the kernel, the intent page, the decision records, and the module documents; research comparisons joined it on 2026-09-18. The root policy's body ended with a list of the kit's policies, although [kernel §3](../constitution/CONVENTIONS.md#k3) already said nothing enumerates them. On 2026-09-18 the decider ruled in chat:

- **only documents of the same kind share a policy**;
- **the root policy does not list the other policies**;
- **no policy enumerates its documents**, since the territory under its id in `constitution.yaml` already does.

The kernel had no definition of *kind*. One slot was open: how many kinds the kit has.

## Options

- **A. Six policies, one per document class.** Root, kernel, intent page, decision records, research comparisons, module documents.
  - **Pros:** the literal reading of "same kind"; every policy states one homogeneous rule set; no catch-all; six real cases for `const-locations` to prove against.
  - **Cons:** two policies govern a single document each; a consumer likewise needs one policy per kind from the first commit.
- **B. Five policies, kernel and intent page as one kind.** A standing-pages policy covers both, since they share type, lifecycle, in-place supersession, and change by recorded decision.
  - **Pros:** no single-document policy; one rule set stated once.
  - **Cons:**
    - **the two differ in shape**, so the kind would be defined by rules alone;
    - **a standing-pages policy** invites the next unrelated page in, the failure being corrected.
- **C. Four policies, research folded under module documents.**
  - **Pros:** fewest files.
  - **Cons:** different meta-type and lifecycle; not one kind by any reading.

## Recommendation

A: a kind is shape plus rules, and the kernel and the intent page share only the rules. A single-document kind is legitimate; the root policy already governs a kind with few members.

## Choice

A, chosen by the decider in chat on 2026-09-18.

## Rulings carried

1. [Kernel §3](../constitution/CONVENTIONS.md#k3) defines a document kind as documents sharing one shape and one rule set. A policy governs exactly one kind. Documents of different kinds never share a policy, and a policy never enumerates its documents: its territory is the enumeration. Supersedes ruling 6 of [dec-0008-policies-by-location](dec-0008-policies-by-location.md).
2. The kit's policies are the root policy and one policy per kind: kernel, intent page, decision records, research comparisons, module documents, each with its territory under its id in `constitution.yaml`. The merged kit-documents policy is deleted; git holds it.
3. The root policy's list of policies is removed. It gains the one-kind rule for the kit's policies.
4. Rules that belong to the kernel rather than to a kind, the envelope and the reference forms, are not restated in any policy ([law 1 of CLAUDE.md](../../CLAUDE.md#law-1)). The interim reference gate is described in the rollout plan, not in a policy.
5. A consumer bootstraps with one policy per kind as well: at least a root policy, a policy for its kernel copy, and a policy for its decision records. The README and Phase B of the rollout plan say so.
