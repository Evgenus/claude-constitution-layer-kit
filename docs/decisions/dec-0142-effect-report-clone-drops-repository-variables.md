---
id: dec-0142-effect-report-clone-drops-repository-variables
type: task-record
title: The effect report clone drops the caller repository variables, and the shared pages say so
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The effect report clone drops the caller repository variables, and the shared pages say so

## Context

[dec-0141-scratch-calls-drop-repository-variables](dec-0141-scratch-calls-drop-repository-variables.md) made the scratch calls of `git` in `repository.py` drop the variables `git rev-parse --local-env-vars` names. Its audit found a second git runner the change left alone: `_run_git` in `ways.py`, which runs the git calls of the effect report. It passed the caller's whole environment. The decider asked on 2026-11-20 for a session to fix it.

The escape rule of the effect report, `escape` in `ways.py`, clones the project with `git clone --shared` into a temporary folder. In that clone it runs `checkout -f --detach` at each commit it scans, then `clean -fdxq`. Git sets `GIT_DIR` for a commit hook and for `git rebase -x` in a linked worktree. Under it, the checkout and the clean act on the repository `GIT_DIR` names, with the clone's folder as the work tree. This session reproduced it on release 2.6.1. The report, run from a linked worktree with `GIT_DIR` naming that worktree's git folder, detached the worktree's branch and reset its index. The same run without `GIT_DIR` left the worktree as it was.

The row `repository`, `territory` of [the shared code's parts](../../shared/GATE.md#g1) also said that one function, `git`, runs each git call of the shared code. `_run_git` made that untrue before release 2.6.1 too.

[Rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11) sets the size. A change to the shared code that also changes `shared/GATE.md` or `shared/MESSAGES.md` raises the release every module requires. [Rule 7](../policies/plc-0009-shared-code.md#r7) then bumps every published module.

## Options

- **A. Code only.** Fix `_run_git`, add the test and its row in `shared/ITEMS.md`, raise `__version__` to 2.6.2.
  - **Pros:** the smallest change; no module's version changes; the tag can wait, since no module requires 2.6.2.
  - **Cons:** `shared/GATE.md` keeps its untrue sentence about one git function; the page says nothing of the clone's calls.
- **B. Pages too.** Do A, and correct the row `repository`, `territory` of `shared/GATE.md`: name the effect report's runner, and say that its calls in its clone drop the variables.
  - **Pros:** the page is true again and states the rule for every scratch call; the same shape as dec-0141.
  - **Cons:** a sweep over all twelve modules; the tag must follow the merge at once; `shared/GATE.md` has 29 characters of room under its ceiling.

## Recommendation

The session recommended B. The page's sentence is wrong today, and this change touches the rule it states. A later fix of the sentence would cost the same twelve-module sweep again.

## Choice

The decider picked B in this session's chat on 2026-11-20.

## Ruling

<a id="r1"></a>**R1.** The git calls of the effect report run in the environment `git` in `repository.py` gives. The clone of the escape rule, its checkout and its clean are scratch calls, so they run with none of the variables that `git rev-parse --local-env-vars` names. The calls on the project keep the caller's whole environment.

<a id="r2"></a>**R2.** The scan the escape rule runs in the clone keeps the caller's environment. This session probed it under `GIT_DIR`, with a red document only on the main branch and with one only in the worktree's index. Its verdict equalled the plain run's each time. A scan reads the files on disk, and the clone shares the caller's objects. A verdict that differs under `GIT_DIR` would reopen it.

<a id="r3"></a>**R3.** Shared item 206 holds R1. The item runs the effect report from a linked worktree, with `GIT_DIR` naming that worktree's git folder. The report leaves the worktree's branch, its index and its untracked file as they were. It also leaves `core.bare` of the repository as it was. Its output equals that of the same report without `GIT_DIR`. The item is red on release 2.6.1 in the ten modules with an escape rule. Every module runs it.

<a id="r4"></a>**R4.** The change raises `__version__` to 2.6.2 and the release every module requires to 2.6.2. It bumps each published module to `0.1.3`, and the install pages name the new tag. Rules 7 and 11 of plc-0009-shared-code ask for both.

## Applied

The commits of this record's branch apply every item. The record was born `active`, and the commit that applied the last item set it `inactive`.

## Carry list

1. R1 — [the shared code's parts](../../shared/GATE.md#g1), row `repository`, `territory`; [the effect report's git runner](../../shared/constitution_layer_kit/ways.py), `_run_git`, `_escape_moments` and `_scan_at`.
2. R2 — [the shared code's parts](../../shared/GATE.md#g1), row `repository`, `territory`; [the effect report's git runner](../../shared/constitution_layer_kit/ways.py), the comment in `_scan_commits`. [The shared items](../../shared/ITEMS.md#g5), row S206, turn red on a verdict that differs under `GIT_DIR`. The probe itself is history.
3. R3 — [the shared items](../../shared/ITEMS.md#g5), row S206; [the item in the code](../../shared/constitution_layer_kit/testing/items.py), `test_effect_escape_clone_under_git_dir`.
4. R4 — history only: the raise and the bumps of this change, which rules 7 and 11 of plc-0009-shared-code ask for.
