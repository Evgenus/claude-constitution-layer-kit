---
id: dec-0076-hooks-give-each-shared-git-call-a-budget
type: task-record
title: A hook gives each shared git call a budget of 3 s and names the hang it ends; the scan and the acts give git no clock
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A hook gives each shared git call a budget of 3 s and names the hang it ends; the scan and the acts give git no clock

## Context

Every gate of the kit runs its git commands through one function of the shared code, `git` in `shared/const_gate/repository.py`: the repository's root, the file list, the check that the log folder is ignored, and the matcher's scratch repository, its `init` and its `check-ignore --no-index` ([kit-shared-gate-code](../../shared/GATE.md)). The modules' own git calls go through it too. None had a timeout. Each hook's handler has a timeout in its `hooks.json`, and the budgets the modules tie to it hold only their own tools, the link checker and the prose linter. A git that hangs was therefore cut by the platform at the handler's timeout: the write proceeds, as for every hook past its timeout, and the user sees the platform's notice, never a line that says what failed and how to fix it.

The session probed it on the trunk on 2026-10-08, with git 2.54.0. A `core.fsmonitor` hook, set in a repository's configuration or the person's own, runs on every call that reads the index: twice on the file list, twice on the repository's `check-ignore`, twice on `status`. It never runs on the root's `rev-parse`, nor on the matcher's two calls. So a hung fsmonitor hook hangs every gate at its file list, and a stalled file system can hang any call. A timeout on the call returned on time, at 1.01 s for a budget of 1 s, on Python 3.12.4 and 3.14.8, while the hook still ran.

Its sibling in one module, a check after a write of [`const-referencing`](../requirements.md#const-referencing) that read and masked the whole tree before its link checker's clock started, is fixed in the same change, together with a clause of that module's limit 15 on the mover's closing scan; both are routine, noted in their commits. Every module is a draft, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). Two questions were put to the decider in chat on 2026-10-08, one per message, each with lettered options and one recommendation, the pick a letter; sections 1 and 2 hold them.

## 1. One pull request and one record

The module's own budget and its limit are routine, as the kit's earlier budgets of one module were. The shared budget gives every gate's hook a new failure the user sees and a new shared line. It reverses no record, and it admits no new part under [rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2): the repository part is shared already, of class K, and every module uses it. The question was its stakes and how the change reaches the trunk.

- **A. All routine:** one pull request, no record, each commit noting its call.
  - **Pros:** it follows the earlier budgets of one module, where a timeout with a teaching line was routine; no carry audit; the shortest path to the merge.
  - **Cons:** a new failure line in every gate's hook lands with no record of why; the reason stands only in commit messages and in the shared code's document.
- **B. `process` for the shared budget alone:** one pull request with one record, the module's budget and its limit noted as routine in their commits.
  - **Pros:** a behaviour shared by all eleven gates gets its reasoning recorded, as earlier changes to shared behaviour did; it matches the kit's rule that most kit changes are `process`.
  - **Cons:** a record, a carry audit and its receipt; about one to two more hours.
- **C. Two pull requests:** the module's budget and its limit first, as routine, then the shared budget with a record.
  - **Pros:** the routine half merges fast; the audit covers only the shared change.
  - **Cons:** two pull requests, two gate-list and CI runs; the two budgets share the one margin of the module's handler, and are best reviewed together.

The session recommended B: the shared change sets behaviour that all eleven gates show the user, and one pull request keeps the two budgets reviewed side by side. The decider chose B in chat on 2026-10-08.

<a id="r1"></a>**R1.** One pull request and one record for the shared git budget; the module's budget for its check after a write and the clause of its limit 15 are routine, noted in their commits.

## 2. The budget of the shared git

The question was how the shared git calls get a budget.

- **A. A budget for each git call, in hook mode only:** `git` gets a timeout of about 3 s when the gate runs as a hook; past it a new shared line names the hang and its fix; the scan and the acts keep no clock.
  - **Pros:** a hang ends in about 3 s with a teaching line in every module at once; one function, one shared message, one shared item with a fake git that hangs; the slow, legitimate scans — a module's history report, a file list of a huge tree — are untouched.
  - **Cons:** the shared code must know the mode; a healthy but slow git over 3 s in a hook gives a configuration failure instead of a late verdict; a budget per call does not bound a hook that makes many slow calls.
- **B. One clock for the whole hook run:** the shared pipeline starts a deadline from a hook budget each module declares, and every git call and every module wait takes what is left.
  - **Pros:** one true bound for every hook, whatever it calls; each module's tie between its waits and its handler's timeout becomes one number.
  - **Cons:** it touches the identity and the waits of all eleven modules and every tie test; several times the size of A; it grows the change beyond the git calls.
- **C. A shared limit only, no code:** the shared code's document states that its git calls have no budget, and that the platform cuts a hung git with no teaching line.
  - **Pros:** no code; one paragraph.
  - **Cons:** the silent hang stays in every hook; the scan in CI waits until the job's limit.

The session recommended A: it closes the hang that has a known cause, the file list under a stalled fsmonitor hook, in every hook, at the cost of one function and one line; B is the larger design, left out of this change; the value of 3 s was the session's to tune, open to the decider's override, and leaves room inside the handlers' margins for the interpreter's start. The decider chose A in chat on 2026-10-08.

<a id="r2"></a>**R2.** In hook mode every call of the shared `git` has a budget of 3 s, `GIT_SECONDS`, its own for each call: the shared code's own calls and every call a module makes through it. In scan mode and in act mode the function gives git no clock, so a slow scan or a slow move is waited for as long as it takes. A module's own clock for git calls it makes outside the shared function stays its own.

<a id="r3"></a>**R3.** The mode is part of the one declaration the shared guard makes for the process: the identity and the mode together, still the package's one global of its own. A second declaration that differs in either is a defect.

<a id="r4"></a>**R4.** A call past its budget is a configuration failure, non-blocking in hook mode like every configuration failure, with one of two shared lines. Each names the seconds and git's subcommand, and each gives a fix a person can follow to green and that harms nothing. C12.12, for a call in the repository, names where git ran and what can stall git there: a stalled file system or, for a call that reads the index, a `core.fsmonitor` hook, with the command that shows the hook. It then gives the call that hung, to run by hand as the gate made it, the argument `-z` dropped and a standard input replaced by `/dev/null`. C12.13, for a call in the matcher's scratch repository, names the system's temporary directory and `TMPDIR`, and git's configuration outside any repository, with the commands that list it; it asks for no git command run there by hand. Both say that the scan, which gives git as long as it takes, checks the same tree.

<a id="r5"></a>**R5.** Every handler of a module's `hooks.json` whose script names `python3`, a gate's or a session-start printer's, has a timeout above `GIT_SECONDS`, so a hung git ends with the line before the platform cuts the hook; a shared acceptance item holds it, beside the hangs.

<a id="r6"></a>**R6.** What the budget does not hold: a hook that makes many slow calls, each under 3 s, is bounded by no budget of git's; a healthy git slower than 3 s in a hook gives the C12.12 line instead of a late verdict; a process git started, a `core.fsmonitor` hook, may outlive the git the timeout kills.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests and the documents; the commits after it correct the code, the documents and this record before its yes, on the findings of its validation and of its carry audit. The message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `repository` row of section 1, and [its limit 16](../../shared/GATE.md#g4); [the repository module](../../shared/constitution_layer_kit/repository.py), the docstrings of `git` and `budget`.
3. R3 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `identity` row of section 1, and [item 1 of its section 2](../../shared/GATE.md#g2); [the identity module](../../shared/constitution_layer_kit/identity.py), its docstrings.
4. R4 — [kit-shared-gate-code](../../shared/GATE.md#g3), rows C12.12 and C12.13 of section 3.
5. R5 — [kit-shared-gate-code](../../shared/GATE.md#g5), row S165 of section 5, and [its limit 16](../../shared/GATE.md#g4).
6. R6 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 16.
