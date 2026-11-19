---
id: dec-0141-scratch-calls-drop-repository-variables
type: task-record
title: The shared code's scratch git calls drop the caller's repository variables, and its pages say so
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shared code's scratch git calls drop the caller's repository variables, and its pages say so

## Context

A read-only audit of the kit on 2026-11-18 found a defect in the shared package. `Matcher` in `territory.py` makes a scratch repository, the "null" repository, with `git init` in the system's temporary folder. It makes the call through `git` in `repository.py`, which passes the caller's whole environment to git. When `GIT_DIR` is in that environment, git ignores the folder the call names. It initialises the repository `GIT_DIR` names instead.

Git sets `GIT_DIR` for a commit hook and for `git rebase -x` in a linked worktree. In the main checkout it does not. So a module's scan run from such a hook set `core.bare` to `true` in the main checkout. After that, `git status` there said `fatal: this operation must be run in a work tree`. The scan itself ended with the shared message `C12.3`. Its fix text blamed the territory patterns, which had nothing to do with it. The session that started this change reproduced it, and this one did again, on release 2.6.0.

Calls on the consumer's repository must keep honouring `GIT_DIR`. The kit chose that on purpose: `ask_passed_over` in `repository.py` leaves git's answer standing wherever the environment names the repository. An older shared item, 145, runs scans with `GIT_DIR` set. It passed with the defect present, since it checks only that one text is absent.

[Rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11) sets the size. A change to the shared code that also changes `shared/GATE.md` or `shared/MESSAGES.md` raises the release every module requires. [Rule 7](../policies/plc-0009-shared-code.md#r7) then bumps every published module.

## Options

- **A. Code only.** Fix `git`, add the test, update `shared/ITEMS.md`, raise `__version__` to 2.6.1.
  - **Pros:** about five files; no module's version changes; no consumer's gates stop until pip installs the new release.
  - **Cons:** the install pages keep naming 2.6.0, so a new install still gets the defect; the fix text of `C12.3` still blames the patterns.
- **B. Pages too.** Do A, state the behaviour in `shared/GATE.md`, and correct the fix text of `C12.3`.
  - **Pros:** every install moves to the fixed release; the pages say what the code does; the wrong fix text is gone.
  - **Cons:** about ninety files; every module requires 2.6.1 and takes a new version; every consumer's gates stop until pip installs 2.6.1.

## Recommendation

The audit session recommended A. The harm is the damaged checkout, and A removes it for everyone who installs 2.6.1. The raise of the required release could ride with the next change that must edit `shared/GATE.md` anyway.

## Choice

The decider picked B in the audit session's chat on 2026-11-19.

## Ruling

<a id="r1"></a>**R1.** A git call the shared code makes in a scratch repository of its own, which `git` takes as `scratch=True`, runs with none of the variables that `git rev-parse --local-env-vars` names. `GIT_DIR` is one of them. The code holds the list git 2.56 gives.

<a id="r2"></a>**R2.** Every other git call keeps the caller's whole environment, as before. So `GIT_DIR` and `GIT_WORK_TREE` still name the consumer's repository for a scan and a hook.

<a id="r3"></a>**R3.** The fix text of `C12.3` no longer blames the territory patterns for every failure of `git check-ignore`. It sends the reader to git's own line. The message keeps its key and its parameter.

<a id="r4"></a>**R4.** Shared item 205 holds R1 and R2. A scan in a linked worktree, run with `GIT_DIR` naming that worktree's git folder, leaves `core.bare` of the repository as it was. It gives the verdict the same scan gives without `GIT_DIR`. The list in the code holds every variable the running git names. The item is red on release 2.6.0.

<a id="r5"></a>**R5.** The change raises `__version__` to 2.6.1 and the release every module requires to 2.6.1. It bumps each published module to `0.1.2`, and the install pages name the new tag. Rules 7 and 11 of plc-0009-shared-code ask for both.

## Applied

The commits of this record's branch apply every item. The record was born `active`, and the commit that applied the last item set it `inactive`.

## Carry list

1. R1 — [the shared code's parts](../../shared/GATE.md#g1), row `repository`, `territory`; [the git call in the code](../../shared/constitution_layer_kit/repository.py), `git`, `_environment` and `_REPOSITORY_VARIABLES`.
2. R2 — [the shared code's parts](../../shared/GATE.md#g1), row `repository`, `territory`; [the git call in the code](../../shared/constitution_layer_kit/repository.py), `git` and `_environment`.
3. R3 — [the shared messages](../../shared/MESSAGES.md#g3), row C12.3; [the message in the code](../../shared/constitution_layer_kit/messages.py), `c12_check_ignore`.
4. R4 — [the shared items](../../shared/ITEMS.md#g5), row S205; [the item in the code](../../shared/constitution_layer_kit/testing/items.py), `test_scratch_repository_under_git_dir`.
5. R5 — history only: the raise and the bumps of this change, which rules 7 and 11 of plc-0009-shared-code ask for.
