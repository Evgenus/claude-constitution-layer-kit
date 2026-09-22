---
id: dec-0013-non-authoritative-status
type: task-record
title: status on a non-authoritative document means current or superseded
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# `status` on a `non-authoritative` document means current or superseded

## Context

The lifecycle rule of [kernel §1](../../kernel/CONVENTIONS.md#k1) claimed one meaning of `status` for every meta-type but spelled it out for two: `active` for a binding current-state document or a task-record being applied, `inactive` for historical evidence. A `non-authoritative` document binds nothing and is never applied, so neither reading fit. The gap was found in the pre-module audit of 2026-09-18: the module routine's first artifact, the research comparison under `docs/research/`, lands in claimed territory and must carry a status on day one. [plc-0005-research](../policies/plc-0005-research.md) was silent; the reversed ruling 1 of [dec-0009-module-routine-validation-and-inputs](dec-0009-module-routine-validation-and-inputs.md) had said `inactive`.

## Options

- **A. `active` means current for non-authoritative documents.** One clause in [kernel §1](../../kernel/CONVENTIONS.md#k1): `active` = the current account of its subject, the version a reader consults; `inactive` = superseded, kept while referenced.
  - **Pros:** keeps "one meaning for every meta-type" honest; a stale comparison can be marked without deletion; envelope checks stay type-blind on the field.
  - **Cons:** "active" on a document without authority reads oddly until the clause is known; a kernel edit and a record.
- **B. Always `active` while in the tree; stale means delete.**
  - **Pros:** nothing to manage; staleness is git-derivable from the date in the comparison.
  - **Cons:** a field with a value but no meaning, which the git-derivability razor forbids; a superseded comparison that is still cited must go, breaking the cite.
- **C. Born `inactive`, as the reversed ruling had it.**
  - **Pros:** matches the "kept as evidence" wording; consistent with records.
  - **Cons:** `inactive` means historical and "kept only while referenced", so a fresh, unreferenced comparison is due for deletion the day it is written; current and superseded are indistinguishable.
- **D. Make `status` optional for non-authoritative documents.**
  - **Pros:** no meaningless value.
  - **Cons:** breaks the four-field envelope; the envelope check branches by type; the schema needs a conditional.

## Recommendation

A: the smallest change that gives the field a real meaning for the third type, and every check that reads the envelope stays uniform.

## Choice

A, chosen by the decider in chat on 2026-09-18.

## Applied in the same commit

- [Kernel §1](../../kernel/CONVENTIONS.md#k1): the lifecycle rule names the non-authoritative reading of both values.
- `kernel/schemas/document-frontmatter.schema.json`: the `status` comment says the same.
- [plc-0005-research](../policies/plc-0005-research.md): rule 2, status of a comparison; later rules renumbered.
