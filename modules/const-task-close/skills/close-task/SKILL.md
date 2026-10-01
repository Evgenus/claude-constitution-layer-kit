---
name: close-task
description: >
  Close a task as one act: merge the deltas into the current-state documents that describe
  the changed code, run the range check, delete the working files, set the task's record
  inactive, commit as one change. Use when a task, story, branch or pull request is being
  finished, merged or handed off, when a change touched code and the question is which
  documents it owes, when writing a no-impact declaration, or when the range check is red.
  Advisory: it shapes the close; the check judges only the range.
---

# Close a task

A task that ends with its code merged and its documents untouched leaves two truths in the
repository, and the next reader has to guess which one holds. Task close is one act, defined by
the constitution's conventions page the project adopted: the code and the current-state documents
that describe it change together; then the task's record is set `inactive` and its working files
are deleted, git remembering both. Nothing here redefines that; this is the order of work.

What is checked and what is not: this plugin's range check reads the project's coverage map —
`coverage` under `const-task-close` in `constitution.yaml`, named pairs of code patterns and the
documents that describe that code — and turns red when a change touches a pair's code and neither
updates one of its documents nor declares no impact for that pair. Whether an update is right,
whether a declaration is honest, whether a file is a working file: judgment, and yours.

## 1. Name what the change owes

Run the check on the change as it stands, from the repository:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/check-task-close.sh" --scan
```

On a branch it examines the commits since the trunk (`trunk` under `const-task-close`, `main` by
default); `--since <ref>` names another base; `--change <commit>` examines one landed change, a
merge by its first-parent diff. Read the verdict: each `RED` line names a pair, the code paths the
change touched, and the documents that did not move. Exit 0 with a count of pairs is green; exit 2
is a finding — fix the pair each `RED` names, or declare no impact for it; exit 1 is a
configuration failure to repair first — the message says what.

## 2. Merge the deltas

For each pair named: open its documents and change what the code change made false or
incomplete — a rule, a message, a dial, a path, a limit. Write the state as it now is; never a
changelog, never "as of this task". Intent that is not yet real belongs in the task's record, not
in a current-state page.

## 3. Declare no impact — only when true

When the code change leaves a pair's documents true — comments reworded, a formatter pass, a
helper the page never describes — say so where the check reads it, one line per pair:

- **As a trailer** on a commit of the change, in the message's **last paragraph, where every line is
  `Key: value`** — one line without a colon hides the whole paragraph from git:
  `No-Doc-Impact: <pair name> — <why the documents are unaffected>`
- **Or in the description:** the same line on its own in the pull request's description, read
  only where the description is given to the check with `--body <file>`; where it is not, the
  trailer is the only form.

The reason is for the reviewer: write what a reviewer needs to agree. Never declare what an update
would have fixed. The key is `declaration_key` under `const-task-close` when the project changed it.

## 4. Delete the working files

Scratch scripts, notes that became the record's reasoning, trial outputs: delete them. Git
remembers. A deleted file leaves its links dangling: find each one and remove it, or redirect it
to where the content went — the record, the document — in the same change; when a module that
checks references is installed, its scan lists every link left dangling after the deletion, so
run it before the commit of step 6. The project may name their patterns in `working_files` under
`const-task-close`; the check then lists tracked files that match as a note. A file kept is kept
with a reason in the commit message. A fixture the check runs, a template, a script the project
keeps: code, not working files.

## 5. Set the record inactive

If the task has a record — a decision record, a plan — set its `status` to `inactive` in the same
change: its ruling now lives in the documents it changed, and the record is evidence. It is kept
while something should still reference it; once nothing should, it is deleted, and git history is
its archive — whether anything should is judgment, never a count of links. When a
module that guards records is installed, its own skill defines when a record is `inactive`; this
step performs it. An active record whose scope sees no commits is stalled drift: commit it back
or roll it back, never leave the halfway state as the truth.

## 6. Commit as one change, and check again

Commit the documents, the deletions and the status change together, the message naming the close.
Run the check once more; merge, or open the pull request, on green. In a project's CI on a pull
request, the same check can run with the base from the event as `--since`, and with the
description as `--body` where that CI writes it to a file:

```bash
sh <plugin root>/scripts/check-task-close.sh --scan --since <base commit> --body <description file>
```

where `<plugin root>` is the plugin's path on the runner: the placeholder above is filled only in a session.
Drop `--body` where the CI writes no description, and the trailers alone are read.
