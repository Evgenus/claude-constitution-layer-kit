---
id: dec-0111-worktrees-and-scratch-folders
type: task-record
title: Worktrees live in .claude/worktrees, scratch work outside the repository; a session removes the scratch folders and worktrees it and its agents made, a worktree once its work is in main
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Worktrees live in .claude/worktrees, scratch work outside the repository; a session removes the scratch folders and worktrees it and its agents made, a worktree once its work is in main

## Context

On 2026-11-02 the decider asked whether any rule of the kit governs scratch folders and the folders of worktrees. The session searched the tracked files and found these facts:

1. Four agents of `.claude/agents/` — the implementer, the verifier, the mutation probe runner and the live proof runner — write only in the scratch directory their prompt names. They make a fresh folder there for each run. They delete nothing. Each says that the session removes the folders before the merge. No current-state document says so, and no check holds it.
2. No document says where a worktree lives, how it is named, or when it is removed. CLAUDE.md keeps every branch after its merge and says nothing of worktrees.
3. The clone held six worktrees, all in `.claude/worktrees/`, where the Claude desktop app makes its own. That folder was kept out of the tree only by the clone's own `.git/info/exclude`, which git never versions. None had uncommitted changes. Four stood on commits already in `main`, and two held commits that were not.
4. The record skill's own example pair calls the place of a worktree or a scratch directory a routine call. A duty to remove them, written into the kit's session guide, rules on a procedure, so it is a `process` ruling.

## Options

- **A. Keep it as it is.** No rule; the leftovers are cleaned once, with the decider's yes.
  - **Pros:** follows the kit's rule that machinery is earned by a failure, and none was found; costs nothing.
  - **Cons:** leftovers pile up again; the removal duty stays in four agent files alone.
- **B. One bullet in the session guide.** CLAUDE.md says where worktrees and scratch work live and when a session removes them.
  - **Pros:** one visible place for the habit; the agents' removal duty gets a home in the guide.
  - **Cons:** a record and a carry audit for a few sentences; no check holds it, so review alone does.
- **C. A check.** `scripts/setup-clone.sh --check`, or a new script, warns of a worktree whose commits are already in `main`.
  - **Pros:** a machine finds the leftovers.
  - **Cons:** machinery for a failure no one has hit; a record, fixtures and a self-test; local clutter fits poorly in the clone's setup check.

## Recommendation

A, recommended by the session: the leftovers are clutter, not a defect, and the kit adds rules when a failure earns them.

## Choice

B, by the decider in chat on 2026-11-02. The session's objection stands: no failure has earned the rule yet.

## Ruling

<a id="r1"></a>**R1.** A session's worktree is a folder of `.claude/worktrees/` in the main checkout, the folder where the Claude desktop app makes its own. A session that makes one itself runs `git worktree add .claude/worktrees/<name> -b work/<name> main` at the top of the main checkout.

<a id="r2"></a>**R2.** The kit's `.gitignore` keeps `.claude/worktrees/` out of the tree, in every clone.

<a id="r3"></a>**R3.** Scratch work — a copy, a clone, a message file, an agent's probe folder — goes in the session's scratch directory, outside the repository. What must outlive the session goes in `local/`, which git ignores.

<a id="r4"></a>**R4.** Before the merge, the session removes the scratch folders that it and its agents made.

<a id="r5"></a>**R5.** After the merge, once `git pull` has brought the merge into the local `main`, the session removes each worktree that it or its agents made with `git worktree remove <path>`, never with `--force`, when `git status` there is clean and the worktree's `HEAD` is in the local `main`. The branch stays. A worktree whose commits are not in the local `main` stays too.

<a id="r6"></a>**R6.** A worktree the app made, or one another session made, is removed only with the decider's yes.

<a id="r7"></a>**R7.** Review holds R1 to R6; no check does.

## Applied

The commit that creates this record adds the bullet "Worktrees and scratch folders" to "Session conduct" in CLAUDE.md and the line `.claude/worktrees/` to `.gitignore`, so the record is born `inactive`.

## Carry list

1. R1, R3, R4, R5, R6, R7 — [CLAUDE.md](../../CLAUDE.md), the bullet "Worktrees and scratch folders" under "Work starts on a branch".
2. R2 — [the kit's ignore file](../../.gitignore), the line `.claude/worktrees/`.
