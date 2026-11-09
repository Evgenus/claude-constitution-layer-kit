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

## 2. How the module runs ccusage

The npm package of ccusage is a Node launcher and one native binary per platform. In the comparison's experiment E1 the native binary counted correctly with no Node on the `PATH`. Node and npm are needed anyway to install the pinned package, since Claude Code runs npm from the person's `PATH` when it copies a plugin, and [R13](dec-0115-tokens-per-commit-counted-by-ccusage.md#r13) already makes Node a need of the first day.

- **A. Through the launcher.** The module runs `ccusage` from the pinned package's `.bin` folder, as ccusage documents.
  - **Pros:** ccusage's own entry point; it picks the right binary for the platform; it survives a change in the package's layout.
  - **Cons:** Node must be present at every count, not only at the install.
- **B. The native binary directly.** The module finds the platform's binary inside the pinned package and runs it.
  - **Pros:** no Node at the count; one process fewer.
  - **Cons:** the binary's place inside `node_modules` is ccusage's own layout, not a promise, so a release can move it; the module must choose among six platform packages itself.

The session recommended A: Node is present wherever the package can be installed, so B saves nothing and leans on a layout ccusage never promised. The decider chose A in chat on 2026-11-09.

<a id="r3"></a>**R3.** The module runs ccusage through the launcher of its pinned package, from that package's `.bin` folder, and never calls a platform binary by its path.

## 3. Where the counts are kept

A count exists only after its commit's window closes, as [R5](dec-0115-tokens-per-commit-counted-by-ccusage.md#r5) says, so no commit can carry its own count. In the comparison's experiment E14, git notes were seen from a linked worktree; a plain push sent no notes, and a rebase lost them unless `notes.rewriteRef` named their ref. A squash or rebase merge on a forge makes new commits that no count names, though a report per pull request can still sum the branch's own commits. A commit trailer changes the commit's SHA, and a file in the tree would ride a later commit that must be counted too.

- **A. A local file in the clone's git common directory.** One JSON line per counted commit, beside the start log and the commit log.
  - **Pros:** shared by every worktree of the clone; never published; no ref that a person must remember not to push; kept when the module is uninstalled.
  - **Cons:** lost with the clone; other clones and other people never see it.
- **B. Git notes on each commit, under a ref of the module's own.**
  - **Pros:** git's own place for facts about a commit; `git log` can show them; a team can share them by pushing the ref.
  - **Cons:** a rebase loses them unless `notes.rewriteRef` is set in every clone; pushing the ref publishes every count and cost, and the kit's repository is public; a forge's squash merge leaves them on commits that never land.
- **C. Both: the local file by default, and git notes as an export.** The counts are kept as in A, and a command writes them as notes only when a person runs it.
  - **Pros:** A's safety by default, and a way to share when someone chooses to.
  - **Cons:** a second output to build and test; the exported notes still carry B's rebase and publishing limits.

The session recommended A: the comparison's recommendation, private costs, and no requirement yet asks for sharing; an export can come later by a new record. The decider chose A in chat on 2026-11-09.

<a id="r4"></a>**R4.** The counts are kept in one file of JSON lines in the clone's git common directory, beside the start log and the commit log, one line per counted commit. The module writes no git note, no trailer and no file in the working tree.

## Carry list

1. R1, R2, R3, R4 — pending: [item 9.34 of the rollout plan](../rollout-plan.md#s9-34).
