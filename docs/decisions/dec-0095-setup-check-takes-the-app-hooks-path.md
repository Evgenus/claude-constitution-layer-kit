---
id: dec-0095-setup-check-takes-the-app-hooks-path
type: task-record
title: The clone's setup check takes an absolute hooks path into a checkout of the same repository
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The clone's setup check takes an absolute hooks path into a checkout of the same repository

## Context

On 2026-10-18 `sh scripts/setup-clone.sh --check` was red in every worktree the Claude desktop app had made, and in the main clone. R5 of [dec-0032-work-starts-on-a-branch](dec-0032-work-starts-on-a-branch.md#r5) has the setup write `core.hooksPath` = `scripts/git-hooks`, and the check compared that literal text. The facts that day:

1. Each worktree the app made held a `config.worktree` with `core.hookspath` set to the absolute path of the main checkout's `scripts/git-hooks`, beside `core.untrackedcache=true`, which the kit never sets; three of three app worktrees had it, the two worktrees made another way had none. The main clone's `.git/config` held the same absolute path; who wrote it there was not found.
2. The hook ran in all of them: git ran the main checkout's `prepare-commit-msg`, and `merge.ff` and `pull.ff` were set. Only the check was red.
3. A worktree's own configuration wins over the clone's, so running the setup again would not turn an app worktree green, and each worktree the app makes later would be red again.

## Options

- **A. Reset the settings once.** Run the setup in the main checkout and `git config --worktree core.hooksPath scripts/git-hooks` in each app worktree.
  - **Pros:** no kit change; the check is green that day.
  - **Cons:** each worktree the app makes later is red again; it changes the settings of worktrees other sessions may be using.
- **B. The check takes the app's form.** `--check` also takes an absolute path to `scripts/git-hooks` in the top folder of a checkout of the same repository, with that folder's hook executable.
  - **Pros:** a lasting fix for every worktree the app makes; no one's settings change.
  - **Cons:** a change to the setup check of the branch-first gate; with the absolute form a worktree runs the main checkout's copy of the hook, not its own branch's.
- **C. Leave it and record it.**
  - **Pros:** no work; the hook already runs.
  - **Cons:** a check that stays red in every app worktree teaches its readers to ignore it.

## Recommendation

B, recommended by the session: the app keeps writing absolute paths, so only B ends the red without turning it on again at the next worktree, and it changes nobody's settings.

## Choice

B, by the decider in chat on 2026-10-18.

## Ruling

<a id="r1"></a>**R1.** `sh scripts/setup-clone.sh` still writes `core.hooksPath` = `scripts/git-hooks`. Its `--check` takes that value, or an absolute path ending in `/scripts/git-hooks` whose folder above is the top folder of a checkout with the same git common directory as the clone checked; with either, the `prepare-commit-msg` in the folder the value names must be executable, and the red's fixes for a hook that is not executable or missing name, by absolute path, that hook and the checkout it is in. Any other value is red, and its message says that the value names no `scripts/git-hooks` of this repository and gives `git config --worktree` as the fix for a worktree whose own configuration names another path; its fixes for the hook then name the hook of the checkout that runs the check. This widens R5 of [dec-0032-work-starts-on-a-branch](dec-0032-work-starts-on-a-branch.md#r5), "`--check` exits 0 when both are set", to that second value; the rest of that ruling stands.

## Carry list

1. R1 — [the setup script](../../scripts/setup-clone.sh), its header and `--check`; [its fixture](../../scripts/git-hooks/tests/run.sh), the cases of the absolute path; [CLAUDE.md](../../CLAUDE.md), the bullet "The local gate". That it widens R5 of dec-0032-work-starts-on-a-branch is history.
