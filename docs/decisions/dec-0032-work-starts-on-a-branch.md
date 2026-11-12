---
id: dec-0032-work-starts-on-a-branch
type: task-record
title: Work starts on a branch — nothing is committed on main; a tracked git hook refuses it
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Work starts on a branch

## Context

Until 2026-09-21 every change of the kit was committed on `main`, one line of 109 commits in which the works — a module, an audit, a decision with its application — ran into each other. On that day the history was rebuilt into one side branch per work, each closed by a merge commit, so that the first-parent view of `main` reads one line per work. Nothing in the repository kept the next commit from landing on `main` again: no hook was active, `core.hooksPath` was unset, and the rollout plan's protected main belongs to Phase D, which needs a remote the kit does not have yet. [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md) had weighed local branches merged `--no-ff` as its option D and turned it down because nothing stopped a direct commit. Its ruling on where the yes is given stands untouched here. The question was how to hold the rule until Phase D.

## Options

- **A. A conduct rule only.** One line in `CLAUDE.md`.
  - **Pros:** no cost; every session reads it.
  - **Cons:** advisory — it enforces nothing, and [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) forbids calling it a gate.
- **B. A tracked git hook, enabled per clone, and the conduct rule.** The hook refuses a commit while `main` is checked out; one setup command sets the two settings git keeps per clone.
  - **Pros:** deterministic for every committer — a person, a session, a script, a subagent; versioned; has a red→green fixture.
  - **Cons:** the settings are per clone, so a fresh clone is unguarded until the command has run; a `main` moved without a commit is not seen.
- **C. A Claude Code hook** on the Bash tool that blocks `git commit` while the session is on `main`.
  - **Pros:** versioned; active in every session without setup.
  - **Cons:**
    - **it matches a command string**, so `git -C`, a script or an alias passes — judgment dressed as a check;
    - **and it holds sessions only**, never a person at a terminal.
- **D. Nothing until Phase D.**
  - **Pros:** a protected main is the only complete enforcement; nothing to build now.
  - **Cons:** until then commits keep landing on `main`, which is how the history that had to be rebuilt came about.

## Recommendation and choice

The session recommended B: the only option that is deterministic today and honest about its limits. **Chosen: B, strict,** by Eugene Chernyshov in chat on 2026-09-21. Strict was offered as the default — nothing lands directly on `main`, a single routine commit included, since a hook cannot tell routine from work — and was not overridden.

## Ruling

<a id="r1"></a>**R1.** Every change — one commit or many, routine or recorded — is made on its own branch `work/<name>`, a short kebab-case name of the work, cut from `main`. Nothing is committed on `main` itself.

<a id="r2"></a>**R2.** A work reaches `main` as one merge commit, never a fast-forward: `git merge --no-ff work/<name> -m "Work: <name>"`. Where the change needs a yes, the merge comes after it, and the commit that names the yes stands on the branch: until the kit has a PR flow that commit is the one that lands the change in the sense of [kernel §4](../constitution/CONVENTIONS.md#k4) and completes it in the sense of rule 5 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), the one [law 9 of CLAUDE.md](../../CLAUDE.md#law-9) asks the yes to be named in, and carries the `Accepted:` and `Carry-Audit:` trailers; the merge commit names no yes and carries no trailer.

From rollout Phase D the yes is PR approval and the trailers move to the commit that merges the pull request.

<a id="r3"></a>**R3.** The branch is kept after the merge, with no limit of time, so a work stays addressable by name. The decider chose named work branches over unnamed merged lines when the history was rebuilt, in chat on 2026-09-21.

<a id="r4"></a>**R4.** The gate is `scripts/git-hooks/prepare-commit-msg`, POSIX shell. While `main` is checked out it refuses a commit, an amend, a cherry-pick and a revert, with a message that states what failed, why, and the fix; it lets a merge pass whole, and a detached HEAD is not `main`. The fix it teaches follows what git leaves behind:

- **a refused cherry-pick is still in progress**, and so is a revert of several commits or one being concluded after a conflict, and git will not switch branches in the middle of either, so it is aborted first and repeated on the branch;
- **a refused commit and a refused revert of one commit** leave their changes staged, and the switch takes them along;
- **an amend is told to leave the commit**, which is on `main` already.

It is this hook and not `pre-commit` because git runs it for a commit, an amend, a cherry-pick and a revert alike and does not skip it on `--no-verify`; `pre-commit` is skipped by a cherry-pick, a revert and `--no-verify` — each tried on git 2.54 on 2026-09-21. Its fixture is `scripts/git-hooks/tests/run.sh`, which counts its own cases, runs in a throwaway repository with the user's global git configuration kept out, and holds among them the same commit red on `main` and green on a branch, and the taught fix carried out for a cherry-pick, for a revert of one commit and of several. The amend's is matched in the message only.

<a id="r5"></a>**R5.** Git keeps the two settings the gate needs per clone and never versions them: `core.hooksPath` = `scripts/git-hooks`, and `merge.ff` = `false`, which makes a merge that could fast-forward a merge commit — a fast-forward makes no commit, so no hook would see it. `sh scripts/setup-clone.sh` sets both, once per clone; `--check` exits 0 when both are set and the hook file is executable, and 2 when not. Both commands stand in the routine's list in `pyproject.toml`.

<a id="r6"></a>**R6.** Declared limit:

- **the gate sees nothing** that moves `main` without passing that hook — `git am`, a rebase of `main`, a fast-forward asked for on the command line (`--ff`, `--ff-only`), which overrides the setting of R5, a push into `main`, `git reset`, `git update-ref`, `git branch -f` — each of the first four tried on git 2.54 on 2026-09-21;
- **and a merge passes whole**, so one concluded by hand can carry any content.

For all of those the rule of R1 is advisory and held by session conduct.

<a id="r7"></a>**R7.** Deferred: from rollout Phase D a protected main on the remote holds the shared `main` — whatever was done to a local `main` by the ways R6 names reaches it only through a pull request's merge, whose review also sees the content of a merge concluded by hand; a local `main` itself stays as R6 leaves it.

The hook stays as the fast local check.

<a id="r8"></a>**R8.** The rebuild of 2026-09-21 that preceded this record:

- **109 commits copied** with tree, author, committer and dates byte for byte onto twelve work branches;
- **the hashes cited** in commit messages and in five records rewritten to the new ones, the record edits named a migration in their commit;
- **the two earlier histories deleted** by the decider after a verified bundle held them.

## Applied

In the commit that creates this record:

- **the rule in session conduct** of [CLAUDE.md](../../CLAUDE.md);
- **the hook, its fixture and the setup script** under `scripts/`;
- **the two commands** in `pyproject.toml`;
- **the clause in item 10** of the rollout plan.

This work is itself made on `work/branch-first`. The record is born `inactive`.

## Carry list

1. R1, R2, R3 — the rule "Work starts on a branch" in session conduct of [CLAUDE.md](../../CLAUDE.md).
2. R4 — [the hook](../../scripts/git-hooks/prepare-commit-msg); [its fixture](../../scripts/git-hooks/tests/run.sh); the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md).
3. R5 — [the setup script](../../scripts/setup-clone.sh); [the routine's command list](../../pyproject.toml); the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md).
4. R6 — the last sentence of the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md).
5. R7 — pending: item 10 of [the rollout plan](../rollout-plan.md).
6. R8 — history only: what was done to the history on the day.
