---
id: dec-0126-each-handler-holds-its-own-hook-budget
type: task-record
title: The tie of the hooks file holds each handler at the hook budget its own entry point declares
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The tie of the hooks file holds each handler at the hook budget its own entry point declares

## Context

A hook run has one deadline, the `hook_seconds` of the identity its entry point declares. A handler's timeout in the hooks file must stand above that deadline by a margin, `LEFT_FOR_THE_REST`. Then a run that spends its deadline ends with its own line before the platform cuts the hook. R5 of [dec-0084-one-deadline-per-hook-run](dec-0084-one-deadline-per-hook-run.md#r5) ruled this tie and said how the shared item S165 holds it: by reading the budget the gate declares.

A module has more entry points than its gate. A session-start printer builds an identity of its own, and so does a grant and a hook that counts. Each names its own `hook_seconds`. The tie read one budget, the gate's, and held every handler at it. So the budget of a printer was held by no tie. [Item 9.24 of the rollout plan](../rollout-plan.md#s9-24) logged this on 2026-10-12, and the decider asked on 2026-11-11 to finish the plan with its waiting items.

The session probed it on 2026-11-11. It gave the printer of module [`const-catalogs`](../requirements.md#const-catalogs) a budget of 40 s under its handler of 30 s. Every test of the module stayed green.

Two more facts framed the choice. The tie ran only beside a gate's hook run, so it did not run at all in three modules: [`const-styling`](../requirements.md#const-styling), whose gate is a scan alone, and [`const-locations`](../requirements.md#const-locations) and [`const-change-cost`](../requirements.md#const-change-cost), which have no gate on an event. Two of them have handlers that name `python3`. And today every such handler of every module declares the default budget of 25 s under a timeout of 30 s or more, so no hooks file is wrong; only the hold was missing.

## Options

- **A. The shared item reads each handler's own budget.** S165 starts every handler that names `python3` as far as its declaration, reads the budget it declares, and holds its timeout at that budget and the margin.
  - **Pros:** one place holds every handler of every module, a new module's and another kit's included; the budget is read from the run, never typed a second time; the three modules the tie skipped are held too.
  - **Cons:** it changes one clause of an accepted ruling, so it needs this record and its audit; the item starts each handler once more, a fraction of a second each.
- **B. Each module holds its printer in an item of its own.** The module's item on the hooks file's shape compares the printer's identity with its handler's timeout.
  - **Pros:** no shared code changes and no ruling changes; no receipt goes stale.
  - **Cons:** five modules gain the same lines; a new module's printer is held only if its author writes the item; a grant and a counting hook stay outside.
- **C. Leave it.** The gate's budget stands for all handlers.
  - **Pros:** no work.
  - **Cons:** a printer whose budget is raised above its handler's timeout is cut by the platform in silence, and no test is red.

## Recommendation

Option A, recommended by the session. It is the only option that holds a handler nobody thought of, and it reads what the run declares.

## Choice

Option A, chosen by the decider in chat on 2026-11-11. The session had asked how the pieces of the shared test code land, and the decider picked a way that builds the tie in the shared item. Later that day the decider asked that this change share one pull request with the change before it, the hang case of S165.

## Ruling

<a id="r1"></a>**R1.** Every handler of a module's hooks file whose `command` names `python3`, or whose script names it, has a timeout of at least the `hook_seconds` its own entry point declares plus `LEFT_FOR_THE_REST`. This holds for every kind of entry point a handler starts — a gate, a printer, a grant, a hook that counts — and whatever mode its scope opens in: an entry point whose run has no deadline, an act, is held to the number it declares all the same. The shared item S165 holds it. What counts as a handler's script stays as it was.

<a id="r2"></a>**R2.** S165 reads that budget from a run. It starts the handler as the platform does, on empty input, in a fresh consumer. A patch of the test logs the `hook_seconds` the entry point declares itself with and ends the process there, before the scope opens. So nothing of the run happens.

<a id="r3"></a>**R3.** A handler that names `python3` and whose entry point never declares itself, opening no scope of `identity.declared`, is red: the tie has no number to hold it to. So is one that cannot be started, or that does not reach its declaration within the 20 s the item gives it. An identity that names no `hook_seconds` declares the default, and is held to it.

<a id="r4"></a>**R4.** The tie runs in every module, whatever kind its gate is. A gate with a hook run must have at least one handler to hold, so there a hooks file that is missing, or that holds no handler that names `python3`, is red. Any other module owes none: with no hooks file, or with handlers that all name no `python3`, it is green.

<a id="r5"></a>**R5.** The tie has its fixture of [law 7 of CLAUDE.md](../../CLAUDE.md#law-7) inside S165, on a plugin made for the purpose. Its gate declares 10 s and its printer 40 s. Both at their own floor are green. The printer one second under its floor is red. The printer at 30 s is red, though the gate's budget alone would let it pass. A handler that never declares itself is red. No handler runs past its declaration. The earlier negative control, on hooks files made for the purpose, stays, with the budget given to it.

<a id="r6"></a>**R6.** No hooks file and no identity changes with this record. Every handler that names `python3` holds the tie as it stands on 2026-11-11.

<a id="r7"></a>**R7.** This record reverses one clause of R5 of [dec-0084-one-deadline-per-hook-run](dec-0084-one-deadline-per-hook-run.md#r5): that S165 holds the tie "reading the budget the gate declares". R1 and R2 stand in its place. The rest of that ruling stands as written: the floor, the margin of 5 s, the second tie on a module's own waits, and that it replaced the tie of an earlier record.

## Applied

The commit that creates this record changes the shared item and its patch, limit 16 of the shared gate page and row S165 of the shared items page. Every item is applied there, so the record is born `inactive`. The shared package keeps its version, which already stands above the last tag ([rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11)).

## Carry list

1. R1, R3, R4 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 16, and [row S165 of kit-shared-items](../../shared/ITEMS.md#g5).
2. R2 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 16; [row S165 of kit-shared-items](../../shared/ITEMS.md#g5); [the shared items](../../shared/constitution_layer_kit/testing/items.py), the docstrings of `git_patch` and `declared_budget`.
3. R5 — [row S165 of kit-shared-items](../../shared/ITEMS.md#g5).
4. R6 — history only: a finding of the day, that no hooks file had to change.
5. R7 — history only: the reversal of one clause of an earlier ruling, an act of this record.
