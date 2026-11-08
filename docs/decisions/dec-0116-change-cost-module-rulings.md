---
id: dec-0116-change-cost-module-rulings
type: task-record
title: Rulings of the const-change-cost authoring — the start hook warns and a command writes the commit log into the git configuration of each clone
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-change-cost authoring — the start hook warns and a command writes the commit log into the git configuration of each clone

## Context

Record [dec-0115-tokens-per-commit-counted-by-ccusage](dec-0115-tokens-per-commit-counted-by-ccusage.md) rules what the module counts and how, and its [R10](dec-0115-tokens-per-commit-counted-by-ccusage.md#r10) leaves the rest to this record, after the module's research round. That round is [res-0015-const-change-cost](../research/res-0015-const-change-cost.md). It confirmed rows [A15.1](../requirements.md#a15-1) to [A15.6](../requirements.md#a15-6) of the requirements matrix and left some choices to the decider. The session puts them in chat from 2026-11-09, one per message, and each adds a section here.

## 1. How the commit log reaches each clone

The comparison recommends git's `post-commit` and `post-merge` hooks set in git's configuration, from git 2.54 on, reading the variable `CLAUDE_CODE_SESSION_ID`. It is the only route it found that names each commit's session with no guess when two sessions share a checkout. A plugin cannot install a git hook, and a git hook cannot find the plugin's folder, which moves with each version, so each hook is a whole command of its own. Someone must write the two keys into each clone's `.git/config`.

- **A. A step per clone.** The module ships a command, and its install note says to run it once in each clone, as the kit runs `sh scripts/setup-clone.sh`.
  - **Pros:** nothing changes a project's git configuration unless a person runs the command; easy to undo.
  - **Cons:** a clone that skips the step logs no commits, which are lost for good, the loss R11 of [dec-0115-tokens-per-commit-counted-by-ccusage](dec-0115-tokens-per-commit-counted-by-ccusage.md#r11) names; every contributor's clone must remember it.
- **B. The start hook writes the keys itself.** At each session start the module's `SessionStart` hook writes the two keys into the clone's own `.git/config` when they are missing, says so in its output, and names the command that removes them.
  - **Pros:** no step for anyone; every clone logs from its first session, as the day-one install of [R13](dec-0115-tokens-per-commit-counted-by-ccusage.md#r13) asks; the write is announced, not hidden.
  - **Cons:** a plugin changes the project's git configuration without a person typing it; after an uninstall the keys stay until removed and keep appending to the log.
- **C. The start hook warns, a command writes.** At each session start the hook names the missing keys and the one command that writes them; it writes nothing itself.
  - **Pros:** only a person changes git's configuration, and no clone goes unnoticed, since the warning comes at the first session.
  - **Cons:** commits made before someone runs the command are lost; a headless or automated session shows the warning to nobody; the warning repeats in every session until the command runs.

The session recommended B, the only option that loses no commit. The decider chose C in chat on 2026-11-09 and gave no other reason. The session keeps its objection in view: a clone's commits before the command runs are not logged, and a session that no person watches warns no one.

<a id="r1"></a>**R1.** The commit log is git's `post-commit` and `post-merge` hooks, set in the clone's git configuration. Each is a whole command that appends the commit's SHA, the time in milliseconds and the value of `CLAUDE_CODE_SESSION_ID` to the log in the clone's git common directory, which every worktree of the clone shares.

<a id="r2"></a>**R2.** The module ships a command that writes the two keys into the clone's `.git/config`, and removes them when asked; it writes nothing else there. While either key is missing, the module's `SessionStart` hook names the missing keys and that command in its output at each session start. No hook of the module writes the keys.

## Carry list

1. R1, R2 — pending: [item 9.34 of the rollout plan](../rollout-plan.md#s9-34).
