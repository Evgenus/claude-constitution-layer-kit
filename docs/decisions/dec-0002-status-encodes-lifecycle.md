---
id: dec-0002-status-encodes-lifecycle
type: task-record
title: status encodes lifecycle; inactive is the historical end state
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# `status` encodes lifecycle; `inactive` is the historical end state

## Context

The kernel said two incompatible things about a decision record once applied: [kernel §2](../../kernel/CONVENTIONS.md#k2) deleted a closed task-record, [kernel §5](../../kernel/CONVENTIONS.md#k5) kept records for in-place supersession. The first record in this repository ([dec-0001-session-conduct-rows](dec-0001-session-conduct-rows.md)) was applied in the commit that created it and sat `active` with no meaning attached. Meanwhile "in-progress vs done" was encoded by existence in the tree, not by any field, so a persisting record had no way to say it was done.

## Options

1. **Records persist as an exception; `active` = ruling in force.** Amend [kernel §5](../../kernel/CONVENTIONS.md#k5) only.
   - Pro: smallest edit; `inactive` keeps its transition-only meaning.
   - Con: records stay a special case of task-record; "done" remains unexpressed; the [kernel §2](../../kernel/CONVENTIONS.md#k2)/[kernel §5](../../kernel/CONVENTIONS.md#k5) contradiction is patched, not removed.
2. **Records deleted at close; commit message is the archive.**
   - Pro: [kernel §2](../../kernel/CONVENTIONS.md#k2) stays pure.
   - Con: rejected options and reasoning vanish from the tree; [`const-decision-records`](../requirements.md#const-decision-records)'s promotion loop and [`const-referencing`](../requirements.md#const-referencing)'s reference stability lose their object.
3. **`status` encodes lifecycle for every meta-type.** `active` = in force (binding current-state; a task-record being applied, the write-head); `inactive` = historical evidence, no authority, kept while referenced, deleted when unreferenced. Authority = meta-type × status, which [kernel §2](../../kernel/CONVENTIONS.md#k2) already claimed. Records are never edited in place; reversing a ruling is a new record. The stalled-migration signal inverts: an active task-record with no commits in scope.
   - Pro: one rule for all types; removes the contradiction; "done" is expressed without duplicating git (no commit links a record to its application).
   - Con: redefines `inactive`, which was a transition-only marker; [`const-task-close`](../requirements.md#const-task-close)'s inactive-age alarm becomes an active-age alarm; [kernel §3](../../kernel/CONVENTIONS.md#k3)'s "declaration pairs with inactive" is reworded.

## Recommendation

Option 3 — it is the model [kernel §2](../../kernel/CONVENTIONS.md#k2) already described, made explicit in the field instead of in file existence.

## Choice

Option 3, proposed by the decider and confirmed in chat on 2026-09-14. Applied in the same commit as this record, which is therefore born `inactive`.

## Edits made

- [kernel §1](../../kernel/CONVENTIONS.md#k1): lifecycle rule rewritten; supersession-in-place narrowed to current-state documents.
- [kernel §2](../../kernel/CONVENTIONS.md#k2): precedence items 2 and 3; close sets the record `inactive`; stalled = active without commits.
- [kernel §3](../../kernel/CONVENTIONS.md#k3): declaration pairs with an active task-record, not with `inactive`.
- [kernel §5](../../kernel/CONVENTIONS.md#k5): record lifecycle stated; "append-only" clause dropped (git holds it).
- **Schema comment** on `status` updated.
- **Plan:** rows [A4.3](../requirements.md#a4-3), [A4.5](../requirements.md#a4-5), [A4.6](../requirements.md#a4-6); [`const-locations`](../requirements.md#const-locations), [`const-decision-records`](../requirements.md#const-decision-records), [`const-task-close`](../requirements.md#const-task-close) spec text; [dec-0001-session-conduct-rows](dec-0001-session-conduct-rows.md) set `inactive`.
