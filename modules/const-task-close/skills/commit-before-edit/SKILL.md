---
name: commit-before-edit
description: >
  Commit before you edit: commit a dirty tree before a batch of edits, commit again after each
  coherent change, never end a turn with uncommitted work. Use when about to start a batch of
  edits, when a change is done, when a turn is ending, when the turn-end hook reports a dirty
  tree, or when rolling back to an earlier state. Advisory: the hook only reports the tree.
---

# Commit before you edit

Rollback points live in git, not in the chat's rewind. The rewind restores what the model wrote
through its file tools and nothing else: an edit made through the shell, a script, a heredoc or a
subagent stays, and a rewind past it leaves a tree that matches no message. Work not committed did
not happen: it can be lost by the next edit, the next session, or the next rewind. So git is the
rollback layer, and a commit is the rollback point.

What is checked and what is not: this plugin's turn-end hook runs `git status --porcelain` in the
session's repository when a turn ends and reports a dirty tree — any tracked change or untracked
file git does not ignore — once per turn: under `severity: block` the model is asked to commit and
the turn continues once; under `warn` the user is shown the notice. The second stop of a turn always
lets it end. Whether a commit is coherent, and what its message says: yours.

## The three moments

1. **Before a batch of edits.** If the tree is dirty, commit it first — whatever it holds is
   someone's work, and the batch must be revertible on its own:
   ```bash
   git add -A && git commit -m '<what is here and why>'
   ```
2. **After each coherent change.** One commit per thing that is done: a fix, a section, a fixture.
   The message says what changed and why, in the project's own conventions.
3. **At the end of a turn.** Never leave a dirty tree. A change that is done is committed; a change
   that is half-done is committed as work in progress, its message saying so — or stashed, and the
   reply says so. A clean tree is silent at the hook.

## Rolling back

`git revert <commit>` for a change that landed; `git checkout <commit> -- <path>` or
`git stash` for the working tree. Name the commit you are going back to; the chat's rewind is not a
rollback and is never relied on as one.

## Scratch work

A scratch directory git ignores is invisible to the hook and is where trial files belong until the
task closes; a tracked scratch file is a working file, deleted at close.
