---
id: dec-0080-fixtures-run-through-check-aspects
type: task-record
title: Each module's fixtures run in CI through check-aspects, which holds the runner's items against the acceptance table
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Each module's fixtures run in CI through check-aspects, which holds the runner's items against the acceptance table

## Context

[dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md) gave `scripts/check-aspects.py` two runs. The plain run is a gate over the module documents and the matrix and runs no runner. The full run, `--run`, also runs each module's runner, and in it two more things are findings: a runner item that no row of the module's acceptance table names, and a fixture item a table names that the runner did not print. The record's R7 chose the plain run as the gate and kept the full run on request, since option C, "the full run a gate", cost minutes on every commit.

So the kit's CI ran the plain run, and each module's job ran its runner alone. Nothing held a runner's items against its table before a merge. A handle audit on 2026-10-11 ran the full run by hand and found one such gap on `main`: the acceptance table of module [`const-referencing`](../requirements.md#const-referencing) did not name shared item 166, which its runner runs. The kit's CI took 137 seconds for its last green run on `main`, its longest job, `const-referencing`, 117 seconds. The full run over all eleven runners, one after another, took several minutes on the session's machine.

## Options

- **A. Each module's job runs its fixtures through `check-aspects --run --module <name>`,** in place of calling the runner directly.
  - **Pros:** the table check rides on a runner run CI already pays for, so it adds almost no time; every pull request holds the gap for every module.
  - **Cons:** it changes the gate list; a red item shows as the check's report unless the check is taught to print the runner's own lines.
- **B. One more entry in the `kit` job runs the full `check-aspects --run`.**
  - **Pros:** one line in the gate list.
  - **Cons:** the eleven runners run a second time, one after another, so the `kit` job grows from about half a minute to several minutes — the cost R7 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r7) turned down.
- **C. R7 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r7) stays, and the full run joins the steps before a merge of a change that touches a module.**
  - **Pros:** no change to CI or to the ruling.
  - **Cons:** a step by hand, the way the gap above went unseen.

## Recommendation

The session recommended A: it closes the gap on every pull request without paying for the runners twice, the cost R7 turned down.

## Choice

The decider chose A in chat on 2026-10-11.

## Ruling

<a id="r1"></a>**R1.** Each module's `fixtures-<module>` entry of the kit's gate list runs `python3 scripts/check-aspects.py --run --module <module>`, never the module's runner alone. So the findings of the full run hold in each module's CI job, on every pull request and on `main` after each merge. The plain run stays the gate of R7 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r7), in the `kit` job.

<a id="r2"></a>**R2.** `scripts/check-aspects.py` prints the whole output of a runner that exits other than 0, its standard output and then its standard error, line for line, under one line naming the runner and its exit, before its report, so that the lines of a red item stand where the run is read.

<a id="r3"></a>**R3.** For each module, R1 replaces the last sentence of R7 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r7): "The full run, with results, is on request, beside the module runners."

## Applied

The commit before the one that creates this record applies R1 and R2, with the self-test of `scripts/check-aspects.py` red without the printing of R2 and green with it. The record is born `inactive`.

## Carry list

1. R1 — [the gate list](../../scripts/gate-list.sh), the `fixtures-*` arm of `commands()` and its header; [CLAUDE.md](../guide/gate-list-and-ci.md), "The gate list and CI".
2. R2 — [`scripts/check-aspects.py`](../../scripts/check-aspects.py), `run_runner` and the paragraph of its docstring on the report.
3. R3 — history only: it names the part of an earlier record's item that R1 replaces.
