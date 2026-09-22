---
id: dec-0017-records-numbered-now
type: task-record
title: The kit's decision records enter the catalog form now, by one hand-made migration, before const-catalogs exists
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit's decision records enter the catalog form now, by one hand-made migration, before `const-catalogs` exists

## Context

[Requirement A13.1](../requirements.md#a13-1) makes a catalogued item's id equal its stem, `<prefix>-<nnnn>-<slug>`, and [kernel §1](../../kernel/CONVENTIONS.md#k1) says an id never changes after creation. Sixteen records existed on 2026-09-18 with plain slug ids, and each new one deepened the debt that [`const-catalogs`](../requirements.md#const-catalogs), third in the authoring order, would repay by changing ids. [dec-0006-accumulating-set-first](dec-0006-accumulating-set-first.md) had already named this debt.

## Options

- **A. Reserve the catalog now, number new records only, leave the sixteen.**
  - **Pros:** no id ever changes.
  - **Cons:** the module's write-time hook blocks any nonconforming id in catalog territory, so the sixteen become permanent findings or a permanent exemption; two regimes in one directory forever.
- **B. Wait for `const-catalogs` and renumber then.**
  - **Pros:** the module's own skill does the work.
  - **Cons:** the change happens anyway, later and larger; the module is authored against a directory it must first repair.
- **C. Renumber every record now, by hand, in one recorded migration.** Prefix and width in the policy's dials namespace; numbers by first-commit order from git; ids change once; links migrate in the same commit; every later record is born numbered.
  - **Pros:** one regime from today; `const-catalogs` is authored against a real conforming catalog; the debt stops growing.
  - **Cons:** a deliberate one-time breach of "never changes"; sixteen renames and their links; the prefix is sticky.
- **D. Renumber the stems, keep the old ids.**
  - **Pros:** [kernel §1](../../kernel/CONVENTIONS.md#k1) untouched.
  - **Cons:** contradicts [A13.1](../requirements.md#a13-1); two identifiers per record.

## Recommendation

C, with prefix `dec` and width 4.

## Choice

C, chosen by the decider in chat on 2026-09-18; prefix `dec`, width 4, accepted as proposed.

## Rulings carried

1. The kit's decision records are a numbered kind: prefix `dec`, width 4, declared as `catalog: {prefix: dec, width: 4}` under the policy's id in `constitution.yaml`, in the form [A13.7](../requirements.md#a13-7) states. The policy [plc-0004-decision-records](../policies/plc-0004-decision-records.md) carries the numbering rule.
2. Numbers 1 to 16 were allocated by first-commit order of the existing records. Their ids changed once, in this migration, which is the one deliberate breach of the kernel's "never changes" rule: entering the regime the kernel already requires, before any consumer references exist. Nothing outside this repository referenced the old ids.
3. Link targets and link texts were rewritten to the new stems across records, policies, `CLAUDE.md`, `INTENT.md`, `README.md`, the template, and `scripts/check-references.sh`, a reference-form migration under [kernel §5](../../kernel/CONVENTIONS.md#k5). Prose mentions of a record by its old slug are left as written.
4. From this record on, a new record takes the highest number on the branch plus one, provisional until it lands on main ([A13.3](../requirements.md#a13-3)); this record is `dec-0017`.
