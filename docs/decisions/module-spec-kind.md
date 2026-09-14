---
id: module-spec-kind
type: task-record
title: Module descriptions live in draft MODULE.md files, not in a separate spec kind
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Module descriptions live in draft `MODULE.md` files, not in a separate spec kind

## Context

The module descriptions M1–M10 sit in `docs/rollout-plan.md` beside the traceability matrix. To start authoring modules, each description is to move into its own file. The question was which document kind holds a description and how that kind relates to the module's own `MODULE.md`. A template for a separate kind was drafted first, at `docs/modules/TEMPLATE.md` (commit 64495e7), written for option A.

## Options

- **A. Task-record write-head.** A spec file per module, `type: task-record`, `active` until `MODULE.md` ships, then `inactive` and deleted; its content is applied into `MODULE.md`, the matrix, and decision records at close.
  - **Pros:** matches kernel §2 literally, since intent not yet real rides in a task delta; no second current-state document about one module, so no drift surface; amendments reuse the template scoped to a delta.
  - **Cons:** design reasoning leaves the tree at close and survives only in git and in decision records; a stalled spec is visible only as an active record with no commits.
- **B. Durable requirements document.** A spec file per module, `type: current-state`, kept beside `MODULE.md` and restricted after authoring to what and why; mechanism, dials, and error texts move out.
  - **Pros:** a standing per-module requirements page; the matrix could later be generated from the specs.
  - **Cons:** two current-state documents per module with a hand-maintained no-overlap rule, the doc-to-doc drift the kernel calls a defect; the post-authoring trimming is ceremony nobody asked for.
- **C. No spec kind.** Each plan description moves straight into a draft `modules/const-<aspect>/MODULE.md`; open slots are inline markers there; `module-template/MODULE.md` gains the homes the descriptions need.
  - **Pros:** one document kind fewer; no transfer step at close; the description and the shipped document are the same file from the first draft.
  - **Cons:** `MODULE.md` had no home for rows, decisions, or deferred items and must grow them; half-designed modules sit under `modules/` looking published unless a draft marker exists.

## Recommendation

A — the kernel already places intent that is not yet real in a task delta, and it avoids a second document about the same module.

## Choice

C, chosen by the decider in chat on 2026-09-14, against the recommendation. The objection is recorded above as C's cons and is answered by rulings 2 and 3 below.

## Rulings carried

1. `module-template/MODULE.md` is the one description format. It gains the slots the plan's descriptions need: rows, decisions, always-on content, platform facts, honest limits, siblings, deferred. Sections are numbered so any one can be cited.
2. A draft module is marked by its manifest version: `0.0.x` means draft, not for consumer installation; publication starts at `0.1.0`, once every gate has its fixture and no open marker remains. Proposed by the session as the default; override is a routine edit.
3. Open slots in a draft are inline `[decide: <slot> — default <X> — stakes <level> — decider <who>]` markers. An authoring session derives its questions from them in document order; a published module carries none.
4. `docs/modules/TEMPLATE.md` is removed in the commit that applies this record; git holds it at 64495e7.
