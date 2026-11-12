---
id: dec-0018-dials-schema
type: task-record
title: The dials file has a kernel schema, validated by every reader at each read
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The dials file has a kernel schema, validated by every reader at each read

## Context

[Requirements A2.6](../requirements.md#a2-6), [A4.6](../requirements.md#a4-6) and [A13.7](../requirements.md#a13-7) said the declarations in `constitution.yaml` are "schema-validated at module load". The pre-module audit of 2026-09-18 found no such schema, and no load moment: a plugin has `SessionStart` and nothing earlier. [Kernel §6](../constitution/CONVENTIONS.md#k6) described the file's shape in prose and one example.

## Options

- **A. Kernel schema, validated at each read.**
  - **`kernel/schemas/constitution.schema.json` states** the kernel-owned keys and the policy-namespace keys, module namespaces open;
  - **every reader checks the keys it reads by hand**, so no validator library enters a module;
  - **a malformed file is a configuration failure**;
  - **the kit's CI validates the kit's own file** with a real validator.
  - **Pros:** one authoritative shape beside the envelope schema; a consumer can validate in the editor; the moment named exists.
  - **Cons:** documentation plus discipline until CI runs it; a kernel sentence and a record.
- **B. No schema; readers validate by hand; rows say so.**
  - **Pros:** no artifact.
  - **Cons:** the shape lives only in prose; three readers re-derive it; nothing for a consumer to validate against.
- **C. Schema plus a `SessionStart` validation hook per module.**
  - **Pros:** errors before any write.
  - **Cons:** one hook per module for one check; the file changes mid-session; a validator library everywhere.
- **D. Schema validated only in the kit's CI.**
  - **Pros:** one validator.
  - **Cons:** a consumer's malformed file is never checked where it matters.

## Recommendation

A: the dials file is the other machine-read artifact the kernel defines, and "at each read" is the only honest moment.

## Choice

A, chosen by the decider in chat on 2026-09-18.

## Applied in the same commit

- `kernel/schemas/constitution.schema.json`, new; [kernel §6](../constitution/CONVENTIONS.md#k6) names it and the read-time rule.
- [A2.6](../requirements.md#a2-6), [A4.6](../requirements.md#a4-6), [A13.7](../requirements.md#a13-7): "at module load" replaced by "at each read".
- **Rollout plan, Phase D:** the kit's CI validates the kit's own dials file.
