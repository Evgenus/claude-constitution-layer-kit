---
id: dec-0006-accumulating-set-first
type: task-record
title: Accumulating modules are authored before the consumer that needs them; the kit is consumer zero
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Accumulating modules are authored before the consumer that needs them; the kit is consumer zero

## Context

The rollout plan authored the first module inside an existing consumer project and read every module's "enters when" line as its authoring moment. Two facts broke that reading on 2026-09-17. First, the intended first consumer is a greenfield project, which has no documents to author against on its first day. Second, for an accumulating failure the entry moment is by definition too late: every artifact written before the gate exists is retrofit debt, and [INTENT.md](../../INTENT.md) already places the guards against accumulating failures in the day-one install set, as does [template §2](../../module-template/MODULE.md#t2). This repository shows the debt in miniature: five decision records written before [`const-catalogs`](../requirements.md#const-catalogs) exists, all unnumbered.

The plan also held that the kit is never a consumer, while its [`const-referencing`](../requirements.md#const-referencing) spec already makes the kit adopt that module's lint and [aspect A12](../requirements.md#a12) puts kit CI on kernel gates. The kit's own records, intent page, and module documents carry the kernel envelope and are governed by nobody.

## Options

- **A. Interleaved, project-led.** Start the consumer project with the kernel only; author each module when the project's trigger fires, against the project's documents.
  - **Pros:** no imagined content; the project is never blocked, since kernel-only is a working install.
  - **Cons:** for accumulating modules the trigger is the moment the debt begins; the kit's own records stay ungoverned.
- **B. Kit-first, kit as its own consumer, all six accumulating modules.** Author them against the kit's documents and fixtures, then start the project.
  - **Pros:** the project starts fully gated; the kit's records are governed.
  - **Cons:** the kit has no code and no tasks closing against code, so [`const-locations`](../requirements.md#const-locations) and [`const-task-close`](../requirements.md#const-task-close) would be designed against imagined content; the project waits.
- **C. Kit-first against a synthetic consumer.** A throwaway repository seeded with fake documents.
  - **Pros:** fast and isolated.
  - **Cons:** the plan's working rule names this as the failure; the `tests/` fixtures already cover the synthetic case.
- **D. A plus the kit as consumer zero for document-shaped modules.** The kit claims its own documents; the modules whose objects exist here are proven here first; the rest wait for the project's trigger.
  - **Pros:** the first module has a live test with no project dependency; the project starts now.
  - **Cons:** still reads "enters when" as "wait" for the two modules that need the project, which is the accumulating failure again.
- **E. Accumulating set first, kit as consumer zero, project born governed.** As D for the four document-shaped modules; the remaining two are authored in the project's first week, before their objects multiply; self-limiting modules wait for friction, with a copy of the kit's session-conduct block in the project's `CLAUDE.md` as the interim carrier.
  - **Pros:** no accumulating failure is ever unguarded in the project; nothing is designed against imagined content; the kit's own records stop rotting.
  - **Cons:** one to two weeks of kit work before the project's first feature; the plan's phase text and "enters when" wording must be corrected; two consumers to keep green; a hook loaded in the repository that develops it can block its own fix, mitigated by per-session `--plugin-dir` and the `process` fast lane.

## Recommendation

E. The circularity dissolves once the two needs are separated: a module needs a few real governed documents in a claimed territory, which the kit already has, and a project needs only the kernel to be born. The accumulating set must exist before the project's first week, because every one of its entry moments falls inside that week for a greenfield consumer. The session first recommended D and revised to E after the decider pointed out that a trigger-driven schedule for accumulating modules arrives after the failure.

## Choice

E, chosen by the decider in chat on 2026-09-17.

## Rulings carried

1. **"Enters when" means two different things.** For an accumulating module it names the first moment an object for the module exists; the module is authored before that moment, and for a greenfield consumer the whole accumulating set is the day-one install set. For a self-limiting module it names the friction signal that earns authoring. Stated in the matrix introduction of `docs/rollout-plan.md`.
2. **Modules are authored up front; dials follow the project.** Every module installs with zero configuration ([kernel §6](../../kernel/CONVENTIONS.md#k6)); territory and coverage maps grow with the consumer. A module never waits for calibration.
3. **The kit is consumer zero for document-shaped modules.** A `constitution.yaml` at the kit root claims the kit's own governed documents, with the kernel as their policy; `kernel/CONVENTIONS.md` carries its own envelope. This is calibration of the kit, not project content: [law 2 of CLAUDE.md](../../CLAUDE.md#law-2) governs files inside modules, and the dials file is outside every module. [`const-meta-types`](../requirements.md#const-meta-types), [`const-decision-records`](../requirements.md#const-decision-records), [`const-catalogs`](../requirements.md#const-catalogs), and [`const-referencing`](../requirements.md#const-referencing) are authored and proven live here first.
4. **Sequence.** Kernel ruling on the territory declaration shape (its own record) → the four modules here → consumer bootstrap with the four loaded from the first commit → [`const-locations`](../requirements.md#const-locations) and [`const-task-close`](../requirements.md#const-task-close) in the consumer's first week → publication → self-limiting modules on friction.
5. **Interim carrier for advisory rules.** Until [`const-interaction`](../requirements.md#const-interaction) ships, a consumer's `CLAUDE.md` may carry a copy of the kit's session-conduct block, labeled manual and version-drifting, as that module's spec already allows.

## Applied in the same commit

- `docs/rollout-plan.md`: phases rewritten as A (kit as consumer zero), B (consumer bootstrap), C (consumer's first week), D (publish), E (steady state); the "enters when" definition added to the matrix introduction; phase references in the [`const-meta-types`](../requirements.md#const-meta-types) and [`const-questions`](../requirements.md#const-questions) headings updated.
- `kernel/CONVENTIONS.md`: envelope frontmatter added; no semantic change.
- [INTENT.md](../../INTENT.md): the "not a project" bullet names the kit as consumer zero.
- `CLAUDE.md`: module step 4 proves document-shaped modules live in this repository as well.
- `README.md`: the kernel ships with its envelope; phase reference updated; the accumulating modules are installed before the first governed document.
- The kit-root `constitution.yaml` is not created here: its shape depends on the territory-declaration ruling.
