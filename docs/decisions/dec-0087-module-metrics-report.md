---
id: dec-0087-module-metrics-report
type: task-record
title: The module metrics are a report of scripts/metrics.py, run after the verdict of the CI job gates
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The module metrics are a report of scripts/metrics.py, run after the verdict of the CI job gates

## Context

On 2026-10-13 the decider asked to compare the kit's modules by numbers. A session proposed a list of metrics and measured some of them by hand: lines of code, cyclomatic complexity and test coverage. The decider then asked which of them a script can measure, and asked for that script to run as the last step of the kit's CI.

A number that only reports is advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): it must never look like a check. A new kit script and a new CI step change the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9). The name of the script matters too. `scripts/check-gate-lists.py` holds that every `scripts/check-*.py` is run by an entry of the gate list's gate group, so a report named `check-` would have to become a gate. The rule of [CLAUDE.md](../../CLAUDE.md) against machinery for failures no consumer has hit is not at stake: the report guards against no failure, and the decider asked for it.

The job `gates` of the workflow is the one check the ruleset requires, green only when every other job is, as R7 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r7) ruled. A report step there must not change that verdict either way: its own failure must not turn the job red, and a red verdict must not turn green.

## Options

- **A. A report step in the job `gates`.** A script measures every module, and the job `gates` runs it after its verdict on every pull request and on `main`, the JSON uploaded as an artifact.
  - **Pros:** the numbers of each change stand beside its run, on the same commit; the script takes about 3 seconds; nothing new to schedule.
  - **Cons:** the job `gates` grows from one step to five, and its log mixes a verdict and a report; the slow metrics cannot run here.
- **B. A scheduled workflow of its own.** The same script runs in a workflow of its own, once a day or once a week, on `main`.
  - **Pros:** the job `gates` stays one step; the slow metrics, coverage and mutation score, could join it.
  - **Cons:** a pull request shows no numbers of its own; a second workflow to keep; the numbers trail the changes they measure.
- **C. No script.** The metrics are measured by hand, by a session, when the decider asks.
  - **Pros:** nothing to keep in step with the module documents.
  - **Cons:** each measure costs a session and is done a different way each time; no history of the numbers.

## Recommendation

A, recommended by the session that built it: the cheap metrics belong beside each change, and the slow ones can still get a schedule of their own later (R6).

## Choice

The decider asked for A in chat on 2026-10-13, in the session that measured the modules by hand; the yes is the merge of this change's pull request.

## Ruling

<a id="r1"></a>**R1.** The kit's `scripts/metrics.py` measures every module folder from what the kit holds: the module document's sections, the skills, the hooks file, the code and tests git tracks, and the history of the last 90 days. Its docstring defines each metric and its JSON key. It prints three tables with a totals row, and the same numbers as JSON with `--json <path>` or `--json -`. With `--complexity [<n>]` it lists the `<n>` most complex functions of the modules' own code, 20 by default, each with its place, complexity, length, nesting depth, parameters and the commits of the last 90 days that touch its file; it gives no advice about them. It is kit tooling, never shipped in a module, and advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): no number is a threshold, and no check holds one. It exits 0 whenever it can read its inputs, and 1 with a line that says what failed, why and the fix when it cannot. It is named `metrics`, never `check-`, and it is no entry of the gate list.

<a id="r2"></a>**R2.** The job `gates` keeps its verdict step first. After it come the checkout, Python, the run of `scripts/metrics.py --json metrics.json` and the upload of `metrics.json` as the artifact `metrics`. Each of these steps carries `if: ${{ !cancelled() }}`, `continue-on-error: true` and `timeout-minutes: 5`. The condition runs them after a red verdict too, and not on a cancelled run, which `always()` would; a cancelled run is replaced or stopped, and wants no report. The flag keeps a failed report step from turning the job red. The verdict step carries no such flag, so its red stays the job's red. The timeout bounds a hang at 5 minutes, where the job's own limit is 360 minutes. The table goes to the log and to the run's summary, and so does the report's error line when it exits 1, before the step fails.

<a id="r3"></a>**R3.** The script has no `--self-test`. No list runs it, so a self-test would be a test that nothing runs. The CI step runs the script itself on every change, where only its output shows, and the kit's `lint` and `types` entries hold its code.

<a id="r4"></a>**R4.** The script runs each `SessionStart` command with the smallest `SessionStart` event on stdin, not an empty stdin. With an empty stdin, four modules' hooks print their error line for input that is no JSON and exit 1, and that is not what a session sees.

<a id="r5"></a>**R5.** Test coverage and mutation score are no metric of the script. Each takes minutes per module, so neither belongs in a step that runs on every change.

<a id="r6"></a>**R6.** Test coverage and mutation score are a work item of their own, in a scheduled workflow, when the decider asks for them.

## Applied

The commits before the one that creates this record built the script and the CI step. The commit that creates this record states R1 and R2 in [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI", and the work on coverage and mutation score in step 9 of the [rollout plan](../rollout-plan.md#s9). The record is born `inactive`. The rounds of its carry audit corrected it in place before the yes, as their commits name: among them, R2 gained the reason for its condition, the timeout and the error line in the log; R5 was split into R5, stated in the script's docstring, and R6, pending in the plan; and the Context gained its sentence on the rule against machinery for failures no consumer has hit. R1 was widened in place too, before the yes, by the decider's request in chat on 2026-10-13: the list of the most complex functions.

## Carry list

1. R1 — [`scripts/metrics.py`](../../scripts/metrics.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
2. R2 — [the workflow](../../.github/workflows/gates.yml), the job `gates` and its header; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
3. R3 — [`scripts/metrics.py`](../../scripts/metrics.py), its docstring; [the gate list](../../scripts/gate-list.sh), the entries `lint` and `types`.
4. R4 — [`scripts/metrics.py`](../../scripts/metrics.py), its docstring of `always_on_chars` and `EVENT`.
5. R5 — [`scripts/metrics.py`](../../scripts/metrics.py), its docstring.
6. R6 — pending: [the rollout plan](../rollout-plan.md#s9), step 9, the coverage and the mutation score of each module.
