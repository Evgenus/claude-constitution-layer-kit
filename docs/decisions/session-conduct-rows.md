---
id: session-conduct-rows
type: task-record
title: Add the session-conduct rules to the traceability matrix
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Add the session-conduct rules to the traceability matrix

## Context

Six session-conduct rules entered this repository's `CLAUDE.md` on 2026-09-14 after one working session: restate before acting, explicit assumptions, honesty over agreement, commit before you edit, refuse destructive moves without confirmation, addressable list items. They apply to every consumer session, not only to kit work, so they belong in the matrix (`docs/rollout-plan.md`) or they are lost at module authoring time.

## Options

1. **Add now, as rows in the existing aspects.** Amend [A6.6](../requirements.md#a6-6) and [A7.2](../requirements.md#a7-2), which partly covered two rules; add [A4.7](../requirements.md#a4-7), [A7.4](../requirements.md#a7-4), [A7.5](../requirements.md#a7-5), [A8.3](../requirements.md#a8-3) for the rest.
   - Pro: every rule has a home before [`const-task-close`](../requirements.md#const-task-close)/[`const-questions`](../requirements.md#const-questions)/[`const-interaction`](../requirements.md#const-interaction) are authored; [law 4 of CLAUDE.md](../../CLAUDE.md#law-4) (a module implements exactly its rows) can then be applied.
   - Pro: no new aspect or module; the rules land where the failure pattern already lives.
   - Con: one session is thin evidence for chat-behavior rules; the plan's Phase D doctrine prefers recurring signals.
2. **Wait for recurrence, log as commit notes.** Keep the rules in `CLAUDE.md` only; promote when they recur across sessions.
   - Pro: follows the friction-earned doctrine literally.
   - Con: for [`const-questions`](../requirements.md#const-questions)/[`const-interaction`](../requirements.md#const-interaction) the evidence is lived sessions, not consumer commit notes; the doctrine's instrument does not fit chat behavior. Rules absent from the matrix are silently dropped when a module is authored from its rows.
3. **New aspect "A13 — Session conduct" with its own module.** Group all six as one aspect.
   - Pro: one place to look.
   - Con: fails the three boundary tests (three enforcement moments: reply shaping, turn end, pre-action); duplicates [`const-questions`](../requirements.md#const-questions)/[`const-interaction`](../requirements.md#const-interaction)'s failure patterns.

## Recommendation

Option 1. The decider judged the rules necessary after direct experience, the evidence instrument for chat rules is the session itself, and the rows are cheap to remove if a later authoring session finds one unearned.

## Choice

Option 1, chosen by the decider in chat on 2026-09-14.

## Rulings carried in the rows

- [requirement A4.7](../requirements.md#a4-7) is gate-lite: a `Stop` hook may warn on a dirty tree; blocking is a dial.
- [requirement A8.3](../requirements.md#a8-3) is a second escalation trigger beside stakes (irreversibility). Only the enumerated destructive command patterns are a gate; the class stays advisory and says so ([law 5 of CLAUDE.md](../../CLAUDE.md#law-5)).
- [requirement A6.6](../requirements.md#a6-6)'s restatement proceeds on the stated reading below the [requirement A6.1](../requirements.md#a6-1) threshold; it does not add a question.
- [requirement A7.2](../requirements.md#a7-2) lists no assumptions when none were made. The verbosity dial in [`const-interaction`](../requirements.md#const-interaction) carries this as its first concrete value.
