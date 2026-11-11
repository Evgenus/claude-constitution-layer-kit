---
id: dec-0122-module-mutation-report
type: task-record
title: CI measures a sample of each module's mutants on every change, in jobs the verdict does not wait for, and scripts/module-mutation.py reports the score
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# CI measures a sample of each module's mutants on every change, in jobs the verdict does not wait for, and scripts/module-mutation.py reports the score

## Context

R6 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r6) left the mutation score of each module to a work item of its own, in a scheduled workflow, when the decider asks for it. R2 of [dec-0089-module-coverage-report](dec-0089-module-coverage-report.md#r2) built the coverage half and kept the mutation score open. On 2026-11-11 the decider asked for the work item.

A mutant is a module's code with one small change. A test run kills it when a test fails, and it survives when every test passes. The mutation score is the share of mutants killed.

The survey behind this record is the comparison [res-0016-mutation-score](../research/res-0016-mutation-score.md), cited here as provenance. Its facts that settle the mechanism:

1. Four in five statements of [`const-questions`](../requirements.md#const-questions) run only in a child `python3` process that a test starts. A tool whose mutant does not reach such a child measures one fifth of the code.
2. Of seven outside tools, only cosmic-ray 8.7.0 ran whole on the kit's layout. It runs one fixed command for every mutant, so it cannot choose tests for a mutant.
3. One whole pass of a module's tests for each mutant costs 16 to 25 seconds a mutant. The twelve modules hold 9,848 mutants by the kit's operators.
4. A prototype of a kit script ran, for each mutant, only the tests whose coverage reaches the mutant's lines. It measured `const-questions` whole in 3.8 minutes with eight copies side by side: 329 mutants, 246 killed, 53 survived, 30 that no test reaches. Every kill was run again alone and stayed a kill. Every survivor was run again against the whole module and survived.
5. Of those 53 survivors, 13 change no behaviour and can never be killed, and 36 point at something no test holds.
6. For the largest modules a whole run is two and a half to five hours of one process, by samples.

A new kit script, new jobs of the workflow and a new entry of the gate list change the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9). A number that only reports is advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5), and must never look like a check.

The record answers two questions, in the order the decider was asked them.

## 1. How the score is measured and reported

### Options

- **A. The kit's own script, a weekly workflow of its own, whole runs, report only.** A new script and a new workflow run each Monday and on request, one job per module; the table goes to the run's summary and the survivors to an artifact.
  - **Pros:** measured whole on one module with no false kill and no missed kill; nothing new to pin; no pull request waits for it.
  - **Cons:** the kit owns the script and the list of mutation operators, which shapes the score; the score trails a change by up to a week; it narrows R9 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r9), since the report runs chosen tests itself.
- **B. cosmic-ray, pinned at 8.7.0, in the same weekly workflow, on a sample.** The outside tool runs the whole module for each mutant, so each run measures a seeded sample of each module's mutants.
  - **Pros:** a maintained tool whose operators are not the kit's to keep.
  - **Cons:** 13 packages behind one pin; the score is an estimate; it makes no mutant of a message text; the survivors' list is partial.
- **C. The kit's script, in the workflow `gates` on every change, on a sample.** Each module's job spends a fixed few minutes on a seeded sample, and the table stands beside the coverage report.
  - **Pros:** every change shows its own score, beside its coverage.
  - **Cons:** it reverses R5 and R6 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r5) for the mutation score; every pull request pays some minutes more in each module's job; a small sample moves by several points with no change in the code.
- **D. A and C together.** The whole score weekly, and a rough one on every change.
  - **Pros:** both the exact score and a rough one for each change.
  - **Cons:** both costs; two numbers that differ by sampling noise alone.
- **E. A, with a floor for each module that turns the weekly job red.** A declared gate: the floor is set from each module's first run.
  - **Pros:** a drop is seen without anyone reading the report.
  - **Cons:** mutants that cannot be killed, a change of the operators and load each move the score with no change in the tests; a red on a schedule belongs to no pull request.

### Recommendation

A, recommended by the session that built it: the only option measured whole and checked both ways, and a run of hours cannot stand on every pull request without a sample, whose number invites reading noise as change.

### Choice

C, by the decider in chat on 2026-11-11, over the session's recommendation. The session read the choice, and stated it back in chat, as: the kit's own script, in the workflow `gates` on every pull request and on `main`, a seeded sample in each module's job under a fixed time, the table beside the coverage report, no weekly workflow and no threshold. The cons of C stand as the price chosen. The numbers of the sample — the time, the copies, the seed — were set by the session, each cheap to change in the workflow.

## 2. Where the sample runs

The first run of the kit's CI with the sample in each module's job was run 43003257222, on 2026-11-11. It measured 898 of 9,884 mutants and scored 80.3%, with a standard error of 1.9 points. The sample step took 233 to 316 seconds in ten modules. It took 437 seconds in [`const-referencing`](../requirements.md#const-referencing) and 668 in [`const-interaction`](../requirements.md#const-interaction), whose tests are slow: a mutant that survives runs every test that reaches it. The check `gates` waits for the slowest job, so the verdict came after about 15 minutes, where it had come after about 5. The session had told the decider of 3 to 5 minutes more in each module's job.

### Options

- **A. Keep the sample in each module's job.** The verdict waits for the sample, and the step's time limit rises from 15 to 25 minutes, so that a slow module is never cut off.
  - **Pros:** nothing more to build; one job holds everything about a module.
  - **Cons:** every pull request waits about 15 minutes for its verdict, three times the old wait.
- **B. Jobs of its own, which the verdict does not wait for.** One sample job for each module and one job that prints the table; the check `gates` needs none of them.
  - **Pros:** the verdict comes after about 5 minutes again; the table still stands on the same run's page, on every change.
  - **Cons:** twelve more jobs in each run, each with its own setup; more jobs than the plan runs at once, so some wait for a runner; the table comes after the verdict.
- **C. Keep the sample in the module's job and shorten it.** The budget drops from 150 to 60 seconds.
  - **Pros:** no new jobs.
  - **Cons:** it saves little where it matters, since the slow modules spend their time on the line map and on the last survivors; the fast modules lose more than half of their sample.

### Recommendation

B, recommended by the session: the verdict is what a pull request waits for, and a report should not hold it back.

### Choice

B, by the decider in chat on 2026-11-11. The session chose that the sample jobs start once the check jobs have ended, so that no check job waits for a runner behind a sample.

## Ruling

<a id="r1"></a>**R1.** For each module, the kit measures a mutation score: the share of the mutants of the module's own Python, under `modules/<module>/plugin/scripts`, that the module's tests kill. The shared `constitution_layer_kit` is not mutated. Each mutant is written over its file in a copy of the kit, never in the kit's tree, so that a child process meets it too. The outcomes are killed, timeout, survived, not covered, unsure and error. The score counts the killed and the timeouts against those two, the survivors and the mutants no test reaches. No number is a threshold, and no check holds one.

<a id="r2"></a>**R2.** The mutants are made by the kit's own script, `scripts/kit_mutation.py`, from each file's syntax tree, with the operators its docstring lists. No outside mutation tool is pinned. The operators are the kit's own choice: a change of that list moves every score with no change in any test.

<a id="r3"></a>**R3.** A mutant runs against the tests whose coverage reaches one of its lines, the quickest first, stopped at the first failure. When one of those lines also runs outside any test, every other test follows. A mutant that no test reaches is counted as not covered, with no run. The reach comes from a line map: one run of the module's unmutated tests under coverage.py, in which a child process takes its context from the environment variable `PYTEST_CURRENT_TEST`. The unmutated tests must be green in that run, or no score is made.

<a id="r4"></a>**R4.** Copies of the kit may run mutants side by side. With more than one copy, the test that failed with a mutant is run again at once on the unmutated file in the same copy. When it fails there too, the mutant is unsure and left out of the score, since the load and not the mutant may have failed the test. A kill at collection, where no test ran, and a timeout are not run again. R10 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r10) is of the fixtures entry, which still runs a module's tests one by one: the sample's copies run in jobs of their own, where their load reaches no verdict.

<a id="r5"></a>**R5.** With a budget in seconds, no new mutant starts once the budget is spent, and the mutants run in an order that a seed shuffles. The score is then an estimate from a sample. The report gives one standard error beside it, and two runs are never compared as a change. The list of survivors is the part a person acts on.

<a id="r6"></a>**R6.** The kit's CI measures a sample of each module's mutants in the workflow `gates`, on every pull request and on `main`, in jobs of its own. One job for each module, `mutation <module>`, starts once the check jobs have ended, whatever their verdict, save on a cancelled run or where the job that lists the modules failed. It runs `scripts/module-mutation.py --module <module> --budget 150 --copies 3 --seed <commit> --out <folder>`, the commit being the one the run checks out, on a pull request its merge with the base. It uploads the module's mutation file as the artifact `mutation-<module>`, kept 5 days. The job `mutation` then downloads every such artifact, runs `scripts/module-mutation.py --from` over the files, writes the table, the survivors and the notes to the log and the run's summary, and uploads the JSON as the artifact `mutation`. The job `gates` needs none of these jobs, so the verdict never waits for the score: R7 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r7) is of the jobs of the gate list, and the job `gates` is green only when each of those is. Each step of the mutation jobs carries `continue-on-error: true`, so that a report that cannot be made turns no job red, and a timeout: 25 minutes for the sample, 5 for the others. Each job's own limit stands above the sum of its steps' limits. This reverses R6 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r6) and R2 of [dec-0089-module-coverage-report](dec-0089-module-coverage-report.md#r2) for the mutation score: no workflow runs on a schedule for it. It narrows R5 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r5): the metrics script still holds no mutation score, and a sample of it runs on every change.

<a id="r7"></a>**R7.** No workflow measures every mutant of a module. A whole measure is a run by hand, `python3 scripts/module-mutation.py --module <module> --copies <n>`, which takes from minutes to hours.

<a id="r8"></a>**R8.** The kit's `scripts/module-mutation.py` is the report: it makes the files or reads them, prints one table with a totals row and the list of survivors, and gives the same numbers as JSON with `--json <path>` or `--json -`. It is kit tooling, never shipped in a module, and advisory. It exits 0 whenever the files could be read or made, whatever they measure. It exits 1, with a line on stdout that says what failed, why and the fix, when they cannot, as when a module's unmutated tests are not green. It is named `module-mutation`, never `check-`, since it is no check. Its docstring defines each JSON key.

<a id="r9"></a>**R9.** The report has a `--self-test`, and the entry `module-mutation` of the gate group runs it, in the job `kit`. The self-test holds the report's code on a small kit of its own and judges no module. It needs coverage.py and pytest at the versions the workflow pins. R3 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r3) gave the metrics script no self-test because no list would run it; here a list runs it.

<a id="r10"></a>**R10.** R9 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r9) is of the runs that give a verdict: the gate list and CI still take a module's verdict only from `scripts/check-aspects.py --run --module`. The mutation report gives no verdict, is no entry of the list, and runs chosen tests itself, through the pytest command that `scripts/kit_mutation.py` builds. No code line of the gate list or of the workflow names pytest for it.

## Applied

The commits before the one that creates this record wrote the comparison and built `scripts/kit_mutation.py`, `scripts/kit_mutation_plugin.py` and `scripts/module-mutation.py` with its self-test, 17 cases at the branch's end. The commit that creates this record adds the sample to the workflow, as steps of each module's job, and the entry to the gate list. A later commit of the branch moves the sample into jobs of its own, as the second question chose. The branch states the rulings in [the gate-list page](../guide/gate-list-and-ci.md#g2) and in the docstrings of `scripts/metrics.py`, `scripts/module-coverage.py` and `scripts/check-gate-lists.py`. The record is born `inactive`.

On the session's machine, a sample of `const-questions` with the workflow's shape, three copies and a budget of 60 seconds, ran 44 mutants in 71 seconds after a line map of 69 seconds: 29 killed, 8 survived, 7 not covered.

Item 9.27 of the [rollout plan](../rollout-plan.md#s9-27) still calls the score pending, in a scheduled workflow. The session that holds the plan marks it done after this change lands, since parallel changes must not meet on the plan's status matrix.

## Carry list

1. R1 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring; [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its docstring; [the gate-list page](../guide/gate-list-and-ci.md#g2), the paragraph on the mutation sample.
2. R2 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring.
3. R3 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring; [`scripts/kit_mutation_plugin.py`](../../scripts/kit_mutation_plugin.py), its docstring.
4. R4 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the outcome `unsure`; [the gate-list page](../guide/gate-list-and-ci.md#g2), the paragraph on the mutation sample; [the workflow](../../.github/workflows/gates.yml), the comment on `CONSTITUTION_KIT_JOBS` in the check jobs' environment. That R10 of dec-0091 is of the fixtures entry is history.
5. R5 — [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its docstring; [the gate-list page](../guide/gate-list-and-ci.md#g2), the paragraph on the mutation sample.
6. R6 — [the workflow](../../.github/workflows/gates.yml), its header and the jobs `mutation-sample` and `mutation`; [`scripts/metrics.py`](../../scripts/metrics.py), its docstring; [`scripts/module-coverage.py`](../../scripts/module-coverage.py), its docstring; [the gate-list page](../guide/gate-list-and-ci.md#g2), the paragraph on the mutation sample, and [its paragraph on the kit's CI](../guide/gate-list-and-ci.md#g1), which says when the job `gates` is green. The reversal of R6 of dec-0087 and of R2 of dec-0089 for the mutation score, the narrowing of R5 of dec-0087, and that R7 of dec-0061 is of the jobs of the gate list, are history.
7. R7 — [the gate-list page](../guide/gate-list-and-ci.md#g2), the paragraph on the mutation sample; [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its docstring of the modes.
8. R8 — [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its docstring.
9. R9 — [the gate list](../../scripts/gate-list.sh), the entry `module-mutation`; [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its docstring; [the gate-list page](../guide/gate-list-and-ci.md#g1), the paragraph on the gate group, and [its paragraph on the mutation sample](../guide/gate-list-and-ci.md#g2). That R3 of dec-0087 gave the metrics script no self-test is history.
10. R10 — [`scripts/check-gate-lists.py`](../../scripts/check-gate-lists.py), its docstring; [the gate-list page](../guide/gate-list-and-ci.md#g2), the paragraph on the mutation sample. That R9 of dec-0091 is of the runs that give a verdict is history.
