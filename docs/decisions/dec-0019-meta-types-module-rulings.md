---
id: dec-0019-meta-types-module-rulings
type: task-record
title: Rulings of the const-meta-types authoring — id uniqueness, the declaration field, territories with no policy behind them
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-meta-types authoring

## Context

The first module, [`const-meta-types`](../requirements.md#const-meta-types), was authored on 2026-09-18 from its research comparison ([res-0001-const-meta-types](../research/res-0001-const-meta-types.md)) and its rows [A1.4](../requirements.md#a1-4), [A1.5](../requirements.md#a1-5), [A2.3](../requirements.md#a2-3). Three slots could not be settled from the kernel or earlier rulings and were left as markers in the module document; the fresh-context validation of the draft argued against two of them. Each was decided in chat, one per message. The record is born `inactive`: every ruling is applied in the commit that creates it ([kernel §5](../constitution/CONVENTIONS.md#k5)).

## 1. Duplicate-id check at write time

The [A1.4](../requirements.md#a1-4) row read "declares a valid type"; the module's invariant says an id is "never reused". The draft blocked a write whose id is already carried by another governed document in the present tree. The validator called this beyond the row.

- **A. Keep it, present tree only, and amend the row text** to "declares a valid envelope (id unique in the tree, type, title, status)".
  - **Pros:**
    - **catches the copy-paste of an old envelope** at the moment it happens, the accumulating failure;
    - **one frontmatter read** per governed document per write;
    - **the module's invariant named it**.
  - **Cons:** the kernel schema has no uniqueness rule; machinery before a consumer hit it; a per-write cost growing with the repository.
- **B. Drop it to the module's deferred list** with the signal "a consumer commit note on a duplicated id".
  - **Pros:** exactly the row as written; less code; the kernel-literal reading.
  - **Cons:** references break silently until then, and a later catalogs module depends on unique ids; the repair after the fact is a renumbering.
- **C. Scan mode only.**
  - **Pros:** no per-write cost; CI still audits.
  - **Cons:** the write is where the teaching message lands; a mixed posture for one rule.

Recommendation A. Chosen A by the decider in chat on 2026-09-18. Applied: the [A1.4](../requirements.md#a1-4) row text; the module document's rows section.

## 2. The declaration field name

[Kernel §3](../constitution/CONVENTIONS.md#k3) names the secondary binding but not the envelope key. Consumers write it into documents mid-move.

- **A. `policy`.**
  - **Pros:** the shortest name for what it says; the kernel's own word.
  - **Cons:** a generic word a consumer's own envelope extension could want.
- **B. `governed-by`.**
  - **Pros:** states the relation; unlikely to collide.
  - **Cons:** longer; hyphenated beside four one-word kernel keys.
- **C. `policy-id`.**
  - **Pros:** says the value is an id.
  - **Cons:** every kernel reference to a policy is already by id.

Recommendation A. Chosen A by the decider in chat on 2026-09-18. Applied: the module's script, skill, and document.

## 3. A territory under a namespace with no policy behind it

[Kernel §3](../constitution/CONVENTIONS.md#k3) says such a namespace "is not a policy's, whatever keys it carries". The draft reported a configuration failure instead, and its two modes disagreed on when.

- **A. Follow the kernel letter: silence, plus a note.** A write there is a visible skip naming the namespace; the scan prints a note per such namespace and stays green.
  - **Pros:** no module-only ruling; both modes agree; a consumer mid-setup is not blocked on every write.
  - **Cons:** the evident intent to govern goes unmet quietly; the signal is a note, easy to miss.
- **B. Configuration failure in both modes whenever the namespace exists.**
  - **Pros:** loud at the first write and in CI; a one-document fix, named.
  - **Cons:**
    - **a module rules what the kernel ruled otherwise** ([law 1 of CLAUDE.md](../../CLAUDE.md#law-1));
    - **every write reports it**;
    - **a `territory` key in a non-policy namespace** is legal per the schema.
- **C. Amend the kernel** to call such a namespace a defect, then B.
  - **Pros:** the loud posture with the kernel's authority.
  - **Cons:** a kernel change before any consumer hit the failure; delays the module's yes.

Recommendation A. Chosen A by the decider in chat on 2026-09-18. Applied: the module's script (skip reason and scan note), fixture, and document.
