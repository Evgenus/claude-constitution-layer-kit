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

## 4. When the count runs

A commit is counted once its window is complete, and only once, as [R5](dec-0115-tokens-per-commit-counted-by-ccusage.md#r5) says. The comparison found the transcript written late: at a commit's `PostToolUse` it did not yet hold the call's result, at `Stop` it held 31 of its final 34 lines, at `SessionEnd` all of them (E15). A plugin's `SessionEnd` hook has 1.5 seconds and cannot raise them, while an `async` hook runs in the background with no timeout enforced. A run of ccusage took at most 0.10 seconds (E10). Command-line transcripts are swept after 30 days by default.

- **A. After each turn, at each start, and by hand.** An async `Stop` hook counts every complete window of its session not yet counted, the same pass runs at `SessionStart` over every session in the clone's logs, and a command does it on demand.
  - **Pros:** a window is counted at the turn after its commit, long before any sweep; the start pass catches what a crashed or closed session left; no turn waits.
  - **Cons:** three ways in to build and test; a count in the background can still run when the next turn starts.
- **B. By hand only.** A command counts every complete window it finds.
  - **Pros:** the least machinery; nothing runs unasked.
  - **Cons:** windows wait until someone remembers, and a command-line transcript can be swept first, against the accumulating class of [R13](dec-0115-tokens-per-commit-counted-by-ccusage.md#r13).
- **C. At session end, and a pass at start.** A `SessionEnd` hook counts the session's windows, and the start pass catches the rest.
  - **Pros:** the transcript is complete at `SessionEnd`; one count per session.
  - **Cons:** 1.5 seconds is too short to copy and count a large session; a desktop session that lives for days rarely ends, so its windows wait for the next start.

The session recommended A, the comparison's recommendation and the only one that counts each window soon without making a turn wait. The decider chose A in chat on 2026-11-09.

<a id="r5"></a>**R5.** The count runs three ways, each counting every complete window not yet counted: an `async` `Stop` hook, over its own session, after each turn; a pass at `SessionStart`, over every session in the clone's logs; and a command a person runs. The module keeps no copy of a window's records.

## 5. How the work of parallel agents is split

Each subagent writes its own transcript, whose records carry `agentId` and the parent's session id, and the tool hooks inside a subagent carry `agent_id` (the comparison's E11 and E15). The commit log of R1 knows only the session: `CLAUDE_CODE_SESSION_ID` names the session, not the agent, and no variable names the agent, so a subagent's commit carries the main session's id.

- **A. Time windows over the whole session.** Every reply of the session, of the main thread and of every agent, goes to the session's next commit by time, as [R4](dec-0115-tokens-per-commit-counted-by-ccusage.md#r4) cuts it.
  - **Pros:** time is the one key every reply carries; it uses the commit log of R1 as it is, with no guess.
  - **Cons:** if agent X still works while agent Y commits, X's tokens until then go to Y's commit.
- **B. Windows per agent.** Each agent's replies go to the next commit that agent made, and the main thread's replies, and those of agents that never commit, go by time.
  - **Pros:** a commit made by one agent does not take in a parallel agent's work.
  - **Cons:** the commit log cannot tell which agent made a commit, so it would need a `PostToolUse` lister, which in the comparison's E13 claimed another session's commit in a shared checkout; it still falls back on time for the rest.

The session recommended A, the comparison's recommendation: B trades the commit log's certainty for an agent name and still splits most of the work by time, while the session's total is exact either way. The decider chose A in chat on 2026-11-09.

<a id="r6"></a>**R6.** A session's windows run over the whole session: every reply of its main thread, its subagents and its workflow agents goes to the session's next commit by time. No window is cut per agent.

## Carry list

1. R1, R2, R3, R4, R5, R6 — pending: [item 9.34 of the rollout plan](../rollout-plan.md#s9-34).
