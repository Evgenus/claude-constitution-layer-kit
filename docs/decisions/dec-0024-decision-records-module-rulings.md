---
id: dec-0024-decision-records-module-rulings
type: task-record
title: Rulings of the const-decision-records authoring — a record is what a named record policy governs; the gate judges the record's own fields; routine is its own finding
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-decision-records authoring

## Context

The second module, [`const-decision-records`](../requirements.md#const-decision-records), was authored on 2026-09-18 and 2026-09-19 from its research comparison ([research-const-decision-records](../research/res-0002-const-decision-records.md)) and its rows [A3.4](../requirements.md#a3-4) and [A3.6](../requirements.md#a3-6). The row says "record validity enforced" and leaves three things open: how a gate knows that a document is a decision record at all, how much of the kernel's record schema "valid" covers when the first module already guards the envelope and both hooks fire on one write, and which of the lifecycle rules of [kernel §5](../../kernel/CONVENTIONS.md#k5) have a deterministic slice worth a gate.

## 1. How the gate knows a document is a decision record

- **A. By location, through a module dial.** `record_policies` lists the ids of the policies that govern decision records; a document is a record when it resolves to one of them.
  - **Pros:** one meaning of "record", the kernel's own — a kind is one policy's territory; it catches the free-form record with neither field, or with misspelt keys; with the dial unset the result is a loud zero naming the dial.
  - **Cons:** enforces nothing until one line is written; blind to a record written outside record territory; the dial repeats a policy id, so a dangling id needs a defined behaviour.
- **B. By content.** Any governed document carrying `stakes` or `decider` is a record.
  - **Pros:** no dial; reserves the two kernel words across every kind.
  - **Cons:** blind to the record that lacks both keys — the one defect a validity gate exists for — while its green count says otherwise.
- **C. Both.** Territory says "must be a record", either key anywhere in claimed territory says "is a record". The comparison's recommendation.
  - **Pros:** detects the union; with the dial unset it still checks what carries the keys.
  - **Cons:** two meanings of "record"; with the dial unset it prints a healthy examined count while a free-form record passes unseen — a vacuous green in a subtler form.
- **D. By location, through a key in the policy's own namespace,** beside `territory`, as `catalog` is.
  - **Pros:** the declaration lives with the policy; nothing can dangle.
  - **Cons:** a kernel change, and the kernel admits a concept only when two or more modules need it; today one does.

Recommendation A, by the authoring session, against the comparison's C: C's default-on enforcement is partial in the worst place, and A's unset state is an honest zero whose message teaches the one-line fix. All four options satisfy [law 3 of CLAUDE.md](../../CLAUDE.md#law-3); what selects A is [kernel §3](../../kernel/CONVENTIONS.md#k3): a document kind is one policy's territory, so the consumer's own record policy is the only project-blind definition of "this is a record". Chosen A by the decider in chat on 2026-09-18.

**Ruling.** A document is a decision record when a policy named in `const-decision-records.record_policies` governs it — by path, or by declaration where the path maps to no policy; in an overlap a declaration naming one claimant picks it, and otherwise every claimant counts. With the dial empty nothing is examined, visibly. An id in the dial with no policy behind it claims nothing and earns a note, never a failure — the shape of item 3 of [dec-0019-meta-types-module-rulings](dec-0019-meta-types-module-rulings.md). Content detection and option D are deferred with their signals.

## 2. What "valid" covers

- **A. The record's own fields only:** `type: task-record`, `stakes` in the recorded enum, `decider` a non-empty string; an envelope that cannot be read at all is one finding; `id`, `title`, `status` are not examined.
  - **Pros:** one invariant per module and no rule implemented twice; with both modules installed a defect in `id` or `status` is taught once; alone, the module still blocks a free-form record.
  - **Cons:** alone, a record with a bad `id` or `status` passes; an unreadable envelope is still reported by both modules.
- **B. The whole schema,** the envelope's fields included.
  - **Pros:** "valid per schema" read literally; complete alone.
  - **Cons:** with both installed every envelope defect is reported twice, in wordings that will drift; the envelope rule lives in two modules; it contradicts ruling (a) of section 2 of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md).
- **C. The whole schema, silent on the envelope's fields when the first module is present.**
  - **Pros:** complete alone, no duplicates together.
  - **Cons:** a hook process has no documented way to learn which other plugins are loaded; the verdict would depend on what else is installed.

Recommendation A. Chosen A by the decider in chat on 2026-09-19.

**Ruling.** The gate judges what a record adds to the envelope and nothing else; the module's honest limits and its install note say that the rest of the envelope has its owner in the first module.

## 3. Lifecycle slices

No real choice was put to the decider; the authoring session took the default and the decider may override it before the yes. `stakes: routine` is already red by the enum and gets its own finding, because its fix differs — delete the record, write the commit note. Born-`inactive` is judgment: "applied" is semantic. An in-place change of a closed record's body is indistinguishable, by its diff, from a typo fix or a reference-form migration, which [kernel §5](../../kernel/CONVENTIONS.md#k5) permits. The one deterministic slice — a write that changes `stakes`, `decider`, `id` or `type` of a record that is `inactive` on disk — is deferred to its friction signal: the row says "gate on schema" ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)), and the kit grows by friction.

## Applied

In the commit that creates this record: sections 3, 5, 7, 9 and 12 of the module's [MODULE.md](../../modules/const-decision-records/MODULE.md), its scripts, fixtures, skills and install note; `const-decision-records.record_policies` in the kit's `constitution.yaml`. The record is born `inactive`.
