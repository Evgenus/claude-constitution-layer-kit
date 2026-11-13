---
id: dec-0135-mover-refuses-an-unwritable-document
type: task-record
title: The mover refuses before the move a document it cannot read or rewrite
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The mover refuses before the move a document it cannot read or rewrite

## Context

The mover of [`const-referencing`](../requirements.md#const-referencing) moves a document and rewrites the links to it. Before the change, a covered document that could not be written stopped the act after the move. The user saw the defect line of the shared code, C12.11, with a traceback, and then the line that the act stopped midway. The file had moved, and some links were rewritten. A covered document that could not be read was passed over at the rewrite. The closing scan then failed on it, also after the move. Item 81 of the module's tests held the first case as it was. The test session of wave 4 found it and put the right behaviour to the decider.

## Options

- **A. A refusal before the move.** The mover asks whether each document it would rewrite can be written, and refuses with a teaching line and nothing changed.
  - **Pros:** it fits the mover's other refusals, which all change nothing; no traceback reaches the user.
  - **Cons:** plugin code and a message change, so the eval receipt goes stale; a file can still change between the check and the write.
- **B. Keep the defect line.** The C12.11 line, then the line that the act stopped midway.
  - **Pros:** no change; the closing line already says what to do.
  - **Cons:** a common state of the user's own tree is reported as a defect of the plugin, with a traceback.
- **C. A designed line after the fact.** The write's failure is caught, the file named, and the act closes with the midway line.
  - **Pros:** a smaller change than A; no traceback.
  - **Cons:** the move has still happened, and the user repairs the tree by hand.

## Recommendation

A, as a later rollout item and not inside wave 4. The session recommended it because it keeps the mover's rule that a refusal changes nothing.

## Choice

The decider picked A in chat on 2026-11-13. On the same day the decider placed it in wave 5, as item 9.42 of the rollout plan, before the release.

## Ruling

<a id="r1"></a>**R1.** Before anything moves or is written, the mover reads every document the act will read. These are the covered documents and the moved one, wherever coverage holds it. A document it cannot read is a V5 refusal that names it and the system's reason.

<a id="r2"></a>**R2.** Each document whose rewrite would change a link is opened for writing and closed again, with nothing written. A document the system will not open so is a V5 refusal that names it and the system's reason. A read-only document the act would not rewrite is no refusal.

<a id="r3"></a>**R3.** The check runs in all three acts: the move, `--moved` and `--ids`. Each refusal closes with the line that nothing was changed, and the tree stays as it was.

<a id="r4"></a>**R4.** The check cannot hold what changes after it. That covers a file's permissions or text changing before the write, a disk that fills, and a link checker that dies after the move. Under `governed_only` a moved policy can change which documents are covered after the move, and a document covered only then is not asked. As root a mode bit denies nothing. Each such case still closes with the midway line.

## Applied

The commit that brings this record also states its rulings in the module's document and its code. The commit before it on the same branch changed the code and the tests. So the record is born `inactive`.

## Carry list

1. R1, R2, R3 — [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the check in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `_refuse_what_cannot_be_rewritten`.
2. R4 — [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12.
