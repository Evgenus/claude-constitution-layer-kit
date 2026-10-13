---
id: dec-0089-module-coverage-report
type: task-record
title: The fixture coverage of each module is a report of scripts/module-coverage.py, in a weekly workflow of its own
status: active
stakes: process
decider: Eugene Chernyshov
---

# The fixture coverage of each module is a report of scripts/module-coverage.py, in a weekly workflow of its own

## Context

R6 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r6) left the test coverage and the mutation score of each module to a work item of their own, in a scheduled workflow, when the decider asks for them. On 2026-10-13 the decider asked for the coverage, and in chat the same day chose to leave the mutation score pending.

The fixtures of a module run its gates as child processes: a runner calls an `sh` entry point, which calls `python3`. A coverage tool that measures only the runner's own process would miss the gates. coverage.py measures the children too, with `patch = subprocess` in its `[run]` section, from version 7.10 on; an earlier session of the same day measured the modules by hand that way. A new kit script and a new workflow change the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9). A number that only reports is advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5), and must never look like a check. R5 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r5) keeps the slow metrics out of the job `gates`, so the question here is only when the report runs.

## Options

- **A. Once a week, on request, and on a change to the report.** A workflow of its own runs on a schedule each Monday, from the Actions page or `gh workflow run`, and on a pull request that changes the script or the workflow.
  - **Pros:** a cheap, steady series of numbers on `main`; a change to the report proves itself on its own pull request; no pull request waits for it.
  - **Cons:** the numbers trail the changes of up to a week; a second workflow to keep.
- **B. Once a day, on request, and on a change to the report.** As A, with a daily schedule.
  - **Pros:** the numbers trail the changes by a day at most.
  - **Cons:** seven times the runner minutes of A, in a private repository whose minutes are counted; coverage moves slowly, so most daily runs repeat the last one.
- **C. On request, and on a change to the report, alone.** No schedule.
  - **Pros:** no minutes spent unless someone asks; nothing runs unseen.
  - **Cons:** no series of numbers over time; the report runs only when someone remembers it, so a broken report goes unseen until then.

## Recommendation

A, recommended by the session that built it: coverage changes slowly, a week is short enough to see a trend, and it costs a seventh of B.

## Choice

## Ruling

<a id="r1"></a>**R1.** The kit's `scripts/module-coverage.py` runs the runner of each module, `modules/<module>/tests/run.py`, once, from the kit root, under `python3 -m coverage run`, with branch coverage and `patch = subprocess`. A folder holding a `python3` that calls the report's own interpreter goes first on the runner's `PATH`, so that the gates' `python3` is the measured one. It measures the module's own Python under `modules/<module>/scripts` and the shared `const_gate` that module links, read at `shared/const_gate`. Per module it gives the lines and branches of each, with those the fixtures reached, the runner's exit and the run's time. A totals row sums the module's own numbers; its shared numbers are the union of every module's runs. It prints one table, and the same numbers as JSON with `--json <path>` or `--json -`; `--module <name>` narrows the run. Its docstring defines each JSON key.

<a id="r2"></a>**R2.** The report is kit tooling, never shipped in a module, and advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): no number is a threshold, and no check holds one. It exits 0 whenever the runs could be made, a red runner included, which it names in a note; and 1 with a line that says what failed, why and the fix when they cannot. It has no `--self-test`, for the reason R3 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r3) gives. It is named `module-coverage`: never `check-`, since it is no check, and never `coverage`, which would shadow the package it runs.

<a id="r3"></a>**R3.** The workflow `.github/workflows/coverage.yml` runs the report each Monday at 04:17 UTC on `main`, on request through `workflow_dispatch`, and on a pull request that changes the script or the workflow. It is no job of the workflow `gates`, so the ruleset never requires it and no verdict waits for it. It installs coverage.py at a pinned version, and the fixtures' other tools at the pins of `gates.yml`. It writes the table and the notes to the log and the run's summary, and uploads the JSON as the artifact `coverage`. Its job's timeout is 120 minutes.

<a id="r4"></a>**R4.** The mutation score of each module stays a work item of its own, when the decider asks for it.

## Applied

The commits before the one that creates this record built the script, the workflow and the `just coverage` recipe. The commit that creates this record states R1 to R3 in [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI", and R4 in step 9 of the [rollout plan](../rollout-plan.md#s9).

## Carry list

1. R1 — [`scripts/module-coverage.py`](../../scripts/module-coverage.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
2. R2 — [`scripts/module-coverage.py`](../../scripts/module-coverage.py), its docstring.
3. R3 — [the workflow](../../.github/workflows/coverage.yml), its header and its triggers; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
4. R4 — pending: [the rollout plan](../rollout-plan.md#s9), step 9, the mutation score of each module.
