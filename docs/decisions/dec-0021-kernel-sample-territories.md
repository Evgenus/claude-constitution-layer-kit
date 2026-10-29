---
id: dec-0021-kernel-sample-territories
type: task-record
title: The kernel's sample dials file no longer shows two overlapping territories
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kernel's sample dials file no longer shows two overlapping territories

## Context

The sample `constitution.yaml` in [kernel §6](../constitution/CONVENTIONS.md#k6) gave `some-policy` the territory `docs/**`, which contains the root policy's `docs/policies/**`. The same section rules that two territories matching one path is the multi-policy defect of [kernel §3](../constitution/CONVENTIONS.md#k3). The fresh-context validation of [`const-meta-types`](../requirements.md#const-meta-types) reproduced the consequence on 2026-09-18: a repository built from the sample reports multi-policy on every policy document. The gate follows the rule; the example contradicted it. Every kernel change is recorded, whatever its size ([plc-0002-kernel](../policies/plc-0002-kernel.md)).

## Options

- **A. Narrow the sample** to a pattern that overlaps nothing, with a comment saying why.
  - **Pros:** the kernel's own example passes the kernel's own rule; one line.
  - **Cons:** a record for an example line.
- **B. Leave it** until the next kernel change.
  - **Pros:** no record now.
  - **Cons:** the first consumer who copies the sample meets a multi-policy finding on every policy.

Recommendation A. Chosen A by the decider in chat on 2026-09-18.

## Ruling

The sample's `some-policy` claims `docs/notes/**`, and its comment states that a territory never overlaps another policy's, the root's included. No rule of the kernel changes: the example now obeys the rule that was already there. Applied in the commit that creates this record.
