---
id: dec-0084-one-deadline-per-hook-run
type: task-record
title: A hook run has one deadline from a budget each module declares, and every wait takes the smaller of its own cap and what is left
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A hook run has one deadline from a budget each module declares, and every wait takes the smaller of its own cap and what is left

## Context

Since [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md), every git call the shared code makes in a hook has a budget of its own, `GIT_SECONDS`, 3 s, and the modules' own tools have budgets of their own: the history read of [`const-catalogs`](../requirements.md#const-catalogs), 5 s; the version probe and the run of the prose linter of [`const-language`](../requirements.md#const-language), 5 s and 10 s; the version probe and the run of the link checker of [`const-referencing`](../requirements.md#const-referencing), 5 s and 20 s. Nothing bounded a hook run as a whole. Limit 16 of [kit-shared-gate-code](../../shared/GATE.md#g4) said so: a hook of many calls, each within its own budget, was bounded only by its handler's timeout, which the platform enforces with no line of the gate's. An inventory of every wait a hook makes today, read on 2026-10-11, summed the bounds against the 30 s of the handlers: the check after a write of [`const-referencing`](../requirements.md#const-referencing) added to 40 s on any tree, that of [`const-language`](../requirements.md#const-language) passed 30 s from two departures, and that of [`const-catalogs`](../requirements.md#const-catalogs) from three catalogs. The tie items of the three modules counted only their own waits plus 5 s and no git call.

The closing group of the kit's hardcode audit took the item up. Two questions were put to the decider in chat on 2026-10-11, one per message, each with lettered options and one recommendation, the pick a letter; sections 1 and 2 hold them. Two further rulings came from the group's verification of the change, with no real choice; sections 3 and 4 hold them. Every module is a draft, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## 1. The shared clock joins the closing group

The group was to be two groups of routine pieces, by the decider's earlier pick that day. One clock for a whole hook run had been option B of the second question of dec-0076 and was left out of that change as the larger design, logged for a signal: a hook cut at its handler's timeout with every git call under its 3 s. The question was whether it stays out or joins.

- **A. Stays out.** The item stays on the rollout plan's pending list until the signal fires.
  - **Pros:** the group stays routine; a design the decider declined once is not reopened without the signal that would justify it.
  - **Cons:** a hook of many slow git calls is still bounded only by the platform's cut, with no line of the gate's.
- **B. Joins the group.** A shared clock in the gate code, priced under [rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2).
  - **Pros:** the one hole dec-0076 left is closed in the same pass, with the inventory already in hand.
  - **Cons:** the group becomes a `process` group with a record and the carry audit in full; no consumer has hit the case.

The session recommended A: the signal was named and had not fired. The decider chose B in chat on 2026-10-11, with the cost known.

<a id="r1"></a>**R1.** One pull request and one record for the shared clock; every other piece of the group is routine, each commit noting its call.

## 2. The shape of the deadline

The inventory listed every wait with its number, where each number is tied, and the one point every hook run passes before its first git call: the shared guard, right after the identity is declared. The question was what happens to the existing numbers once one deadline bounds the run.

- **A. Floors under one deadline.** `GIT_SECONDS` and the module constants stay as caps; each wait takes the smaller of its cap and what is left of the deadline; the ties become "the module's own waits fit the budget" and "the budget and a margin fit the handler's timeout".
  - **Pros:** a hung git still names itself at 3 s with the two lines of dec-0076 unchanged, so that record is superseded only in its limit; a slow link checker is still capped at 20 s, so a healthy run keeps the shape it has; the smallest diff: one read site for the git budget, four module wait sites, one declaration per module, one new line, one shared item.
  - **Cons:** two numbers per module, the cap and the budget, and the limit text must explain both; a run of many slow calls ends at the deadline with the new line, not at a git line, so the user reads that the budget is spent rather than which call was slow.
- **B. One deadline replaces them.** `GIT_SECONDS` and the module constants go; each module declares one number and every git call and module wait takes what is left of it.
  - **Pros:** one number per module and one tie; the limit reads in one sentence; no cap to keep in step with the budget.
  - **Cons:** a hung git on the first call eats the whole budget before any line, so the 3 s teaching line of dec-0076 is lost and its R2 and R4 are reversed too; the golden lines of three items are rewritten; several times the diff of A, in every module's runner.

The session recommended A: it closes the hole limit 16 named while keeping every line and test the earlier groups proved, and it is the smaller change by far. The decider chose A in chat on 2026-10-11.

<a id="r2"></a>**R2.** Every module declares a hook budget: `hook_seconds` on its identity, whose default is the shared `HOOK_SECONDS`, 25 s. The shared guard starts one deadline per hook run when the identity is declared, in hook mode only. A scan, an act and a process declared with no mode have none. The budget is part of the one declaration, so a second declaration that differs in it is a defect, as R3 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r3) says of the identity and the mode.

<a id="r3"></a>**R3.** In hook mode every shared git call and every wait a module makes takes the smaller of its own cap and what is left of the deadline. The caps stay: `GIT_SECONDS`, 3 s, for each git call, and the modules' own numbers for their tools. This narrows R2 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r2), which gave each call its 3 s on its own: the cap stays, and what is left of the deadline bounds the call too. A call that runs past its own 3 s still gives the two lines of R4 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r4), unchanged. A scan and an act have no deadline and give git no clock, as R2 of that record says; the version probes of the tools keep their cap in every mode.

<a id="r4"></a>**R4.** Nothing left before a wait is a configuration failure, non-blocking in hook mode like every configuration failure, with one shared line, `C12.14`: it names the budget and the wait it ended, says in one clause why the rule exists, and gives the fix, the scan, which has no clock, and where git itself is slow the setting and the file system that `C12.12` names. The count line follows it.

<a id="r5"></a>**R5.** Two ties hold the numbers. Every handler of a module's hooks file whose script names `python3` has a timeout of at least the declared `hook_seconds` plus `LEFT_FOR_THE_REST`, 5 s, the margin for the interpreter's start and the reads; the shared item S165 holds it, reading the budget the gate declares, and it replaces the tie of R5 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r5), which it implies. Each module's own waits in one hook run fit its `hook_seconds`, held by the module's own tie item. No hooks file changes: every handler that names `python3` keeps 30 s.

<a id="r6"></a>**R6.** What the deadline does not hold: the interpreter's start and the reads before the declaration, the reading of the event on standard input, and a wait that takes no number from the clock, of which there is none in hook mode today. This replaces the first clause of R6 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r6), which named a hook of many calls bounded only by its handler's timeout: that case is now bounded by the deadline. Its other two clauses stand: a healthy git slower than 3 s in a hook gives the `C12.12` line in place of a late verdict, and a process git started, a `core.fsmonitor` hook, may outlive the git the timeout kills.

## 3. A tool wait the deadline shortened

Under R3 a tool wait near the end of the budget is given less than its cap. The verifier of the change found that such a wait, when it then ran out, printed the tool's own line with the shortened number: "vale gave no answer in 2 s, the most a check after a write waits", when the most is 10 s. The line was false, and the user could not tell that the hook's budget, not the tool's cap, ended the wait. No real choice existed: [law 6 of CLAUDE.md](../../CLAUDE.md#law-6) asks a gate's line to say what failed.

<a id="r7"></a>**R7.** A wait that the deadline shortened and that then runs out — a shared git call, the version probe and the run of the prose linter, the version probe, the reads and the run of the link checker — is reported by the shared line `C12.14`, naming the wait, never by the tool's own line. The tool's own line stands only for a wait that had its whole cap. The shared code decides by comparing the seconds a wait was given with its cap. The one exception is the history read of [`const-catalogs`](../requirements.md#const-catalogs): a git call outside the shared function and an advisory wait, asked only after a verdict, with a clock of its own inside the number the deadline gives it. A read that clock cuts, and one asked when nothing is left, end in the working tree's answer, not in a failure, so that no verdict falls with its advice.

## 4. The handler tie reads a script, not an option

The tie of R5 read every entry of a handler's `args` as a script, and a script that cannot be read counted as one that names `python3`. So the option `--subagent` of the pointer printers, which hold no `python3` and have 5 s, counted as naming it, and the new floor turned the tie red in three modules. No real choice existed: an option is no script, and raising the printers' timeouts would hold them to a rule they do not fall under.

<a id="r8"></a>**R8.** A handler's script is each `args` entry that is no option, an entry starting with `-` being an option, and each word of its `command` that lies under the plugin's folder or is an existing file. A script that cannot be read still counts as one that names `python3`, as limit 16 of [kit-shared-gate-code](../../shared/GATE.md#g4) said before this change.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the shared code, the modules' waits, the tie items and the fixtures; the commits after it write the documents and correct the code, the documents and this record before its yes, on the findings of its validation and of its carry audit. The message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `identity` row of section 1, and [item 1 of its section 2](../../shared/GATE.md#g2); [its limit 16](../../shared/GATE.md#g4); [the identity module](../../shared/constitution_layer_kit/identity.py), the docstrings of `declare` and `remaining`.
3. R3 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `repository` row of section 1, and [its limit 16](../../shared/GATE.md#g4); [the repository module](../../shared/constitution_layer_kit/repository.py), the docstrings of `budget` and `git`; the limits of [const-language](../../modules/const-language/MODULE.md#t9) and [const-referencing](../../modules/const-referencing/MODULE.md#t9); [const-catalogs](../../modules/const-catalogs/MODULE.md#t9), its limit 7, and [its platform fact 5](../../modules/const-catalogs/MODULE.md#t6).
4. R4 — [kit-shared-gate-code](../../shared/GATE.md#g3), row C12.14 of section 3, and [its limit 16](../../shared/GATE.md#g4).
5. R5 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 16, and [row S165 of its section 5](../../shared/ITEMS.md#g5); the acceptance rows of items 77, 16 and 70 of [const-catalogs](../../modules/const-catalogs/MODULE.md#t10), [const-language](../../modules/const-language/MODULE.md#t10) and [const-referencing](../../modules/const-referencing/MODULE.md#t10).
6. R6 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 16.
7. R7 — [kit-shared-gate-code](../../shared/GATE.md#g3), row C12.14 of section 3, and [its limit 16](../../shared/GATE.md#g4); the limits of [const-language](../../modules/const-language/MODULE.md#t9) and [const-referencing](../../modules/const-referencing/MODULE.md#t9); [const-catalogs](../../modules/const-catalogs/MODULE.md#t9), its limit 7, and [its platform fact 5](../../modules/const-catalogs/MODULE.md#t6); [the identity module](../../shared/constitution_layer_kit/identity.py), the docstrings of `ran_out` and `left_of`.
8. R8 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 16, and [row S165 of its section 5](../../shared/ITEMS.md#g5).
