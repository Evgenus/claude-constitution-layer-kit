---
name: choose-meta-type
description: >
  Choose the meta-type of a governed Markdown document (current-state, task-record,
  non-authoritative) before creating or reclassifying one, and split a document that
  mixes how things are with where they should go. Use when creating a document in
  claimed territory, when unsure whether a document binds, or when a write was blocked
  for an invalid type. Advisory: it shapes the choice; the write-time gate checks only
  that the type is one of the three.
paths: "**/*.md"
---

# Choose the meta-type

Every governed document declares exactly one meta-type in its envelope. The kernel
defines the three and their authority; this skill only helps you pick the right one.
The choice is judgment, so it is defined by the contrastive pairs below, not by a rule.
The gate (this plugin's hook) checks only that `type` is one of the three values and
that the document resolves to one policy; it cannot tell a wrong choice from a right
one. That is your job.

## The one question

**Does this document state what the system is and must remain, what a bounded change
will make it, or merely explain something?**

- *What the system is and must remain*, as of all completed work → `current-state`.
  It binds. It is edited in place when reality changes; git keeps the history.
- *What a bounded change will make it*, agreed for a point in time → `task-record`.
  It is the write-head while `active`; it outranks the current-state documents it is
  changing within its scope, and becomes evidence once `inactive`.
- *Explanation, investigation, research, an as-is snapshot* → `non-authoritative`.
  It obliges nothing. Date it. Prefer generating it over hand-maintaining it.

## Contrastive pairs (the definition)

1. **Architecture of what should be, written mid-task.** A design for the target shape
   of a subsystem, produced while the change is under way → `task-record`: it rides
   with the task's delta and closes with it. *Not* `current-state`: intent that is not
   yet real never sits in a standing document.
2. **The standing specification.** The reconciled description of a subsystem as it is
   and must stay — its invariants and why → `current-state`. *Not* `task-record`: it has
   no close, it is kept aligned with code at every task close.
3. **A description of how the code is organised today.** A module map, a dependency
   listing, a walkthrough of the current structure → `non-authoritative`, dated, ideally
   generated from the code. *Not* `current-state`: it carries no obligation, and a stale
   copy of it read as truth is exactly the failure this vocabulary prevents.
4. **A document that mixes as-is with direction.** Half of it describes the present
   structure, half says where it should go → split it: the normative half becomes
   `current-state` (or a `task-record` if the direction is a bounded change), the
   descriptive half `non-authoritative`. If splitting is not worth it, classify by the
   normative content and cut the rest to a dated pointer.
5. **Notes from an investigation** (a spike, a comparison of options, a postmortem
   narrative) → `non-authoritative`. *Not* `task-record`: a task-record carries a ruling
   or a delta, not an account.

## Envelope reminders

- `status: active` at birth for a current-state document and for a task-record whose
  delta is being applied; a task-record applied in the same commit that creates it is
  born `inactive`.
- A `non-authoritative` document that is superseded by a later account becomes
  `inactive`, or is deleted when nothing references it.
- Put the document where its policy's territory says; the path binds it. Add a
  `policy: <id>` declaration only when the path mapping is absent or ambiguous —
  typically mid-move, while an active task-record covers the move — never to
  override where the file sits.
- If you edited a governed document through the shell (heredoc, `sed`), the hook did
  not see it: run the plugin's scan mode over the repository before you finish.
