---
id: dec-0089-module-coverage-report
type: task-record
title: Each module's fixtures entry runs under coverage.py in CI, and scripts/module-coverage.py reports it after the verdict of the job gates
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Each module's fixtures entry runs under coverage.py in CI, and scripts/module-coverage.py reports it after the verdict of the job gates

## Context

R6 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r6) left the test coverage and the mutation score of each module to a work item of their own, in a scheduled workflow, when the decider asks for them. R5 of that record gave the reason: each takes minutes per module, too slow for a step that runs on every change. On 2026-10-13 the decider asked for the work item.

The fixtures of a module run its gates as child processes: a runner calls an `sh` entry point, which calls `python3`. A coverage tool that measures only the runner's own process would miss the gates. coverage.py measures the children too, with `patch = subprocess` in its `[run]` section, from version 7.10 on. A new kit script and a change to a kit check and to CI change the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9). A number that only reports is advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5), and must never look like a check.

The record answers three questions, in the order the decider was asked them.

## 1. What the work item measures

### Options

- **A. Coverage only.** The line and branch coverage of each module; the mutation score stays pending.
  - **Pros:** a small scope, and coverage.py with `patch = subprocess` was already tried by hand; one new tool to pin.
  - **Cons:** R6 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r6) is carried only in part.
- **B. Coverage and mutation score together.** A mutation tool runs over each module's own code as well.
  - **Pros:** R6 is carried whole.
  - **Cons:** a mutation run reruns the fixtures once per mutant, which may take hours per module; the tool needs research first.
- **C. Coverage, with the mutation score named as the next step in this record.** As A, with a ruling that keeps the mutation score open.
  - **Pros:** the record says plainly what is still open.
  - **Cons:** nearly the same as A, since the plan already holds the work.

### Recommendation

A, recommended by the session that built it: the brief scoped the work to coverage, and the mutation score needs research of its own.

### Choice

A, by the decider in chat on 2026-10-13.

## 2. When the report runs

### Options

- **A. Once a week.** A workflow of its own runs on a schedule each Monday, on request, and on a pull request that changes the report.
  - **Pros:** a cheap, steady series of numbers on `main`; no pull request waits for it.
  - **Cons:** the numbers trail the changes by up to a week; a second workflow to keep.
- **B. Once a day.** As A, with a daily schedule.
  - **Pros:** the numbers trail the changes by a day at most.
  - **Cons:** seven times the runner minutes of A; most daily runs repeat the last.
- **C. On request alone.** No schedule.
  - **Pros:** no minutes spent unless someone asks.
  - **Cons:** no series of numbers; a broken report goes unseen until someone runs it.
- **D. On every change, in the workflow `gates`.** The report runs on every pull request and on `main`.
  - **Pros:** each change shows its own numbers; the module jobs already run the fixtures, so the cost is coverage.py's own slowdown, about 40%: the fixtures of [`const-questions`](../requirements.md#const-questions) took 49 seconds alone and 68 under coverage.py, on the session's machine.
  - **Cons:** it reverses R6 and narrows R5 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r5), accepted the same day; every pull request pays the slowdown.

### Recommendation

The session first recommended A, on the premise of R5 that coverage takes minutes per module. The decider asked why the report was a scheduled run and not part of the testing. The session then found the premise weak, as D's pros say, and offered D.

### Choice

D, by the decider in chat on 2026-10-13: "put it in the PR gates", read by the session, and stated back in chat, as a report on every pull request and on `main`, with no threshold.

## 3. How the run is wired

### Options

- **A. One run: the fixtures entry itself runs under coverage.py in CI.** `scripts/check-aspects.py --run` starts the runner under coverage.py when CI asks for it.
  - **Pros:** the cheapest, about 40% on each fixtures run and no second run; the numbers are those of the very run that gave the verdict.
  - **Cons:** a failure of coverage.py turns the fixtures entry red, so a report can change a verdict, which R2 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r2) kept from the metrics; a kit check gains a coverage mode.
- **B. A second run in each module's job, after its verdict.** A report step after the entries, as the metrics steps run.
  - **Pros:** the verdict is untouched; the pattern of R2 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r2).
  - **Cons:** each module's job runs its fixtures twice, and the required check comes about 1.5 to 2.5 minutes later.
- **C. Separate coverage jobs, one per module, that the job `gates` does not wait for.** A summary job merges them.
  - **Pros:** the verdict is untouched, in what it says and in when it comes.
  - **Cons:** about twice the fixtures' runner minutes; 25 jobs at once may wait for a free runner.

### Recommendation

C, recommended by the session: the only option in which coverage changes neither the verdict nor its time.

### Choice

A, by the decider in chat on 2026-10-13, over the session's recommendation; the cons of A stand as the price chosen.

## Ruling

<a id="r1"></a>**R1.** Per module, the kit measures the line and branch coverage its fixtures reach, in two parts: the module's own Python under `modules/<module>/scripts`, and the shared `const_gate` it links, read at `shared/const_gate`. A file there that no run imports counts with all its lines missed. coverage.py measures Python alone, so a module's `.sh` files are not in the numbers. A child process started with an environment of its own, without coverage.py's variable, is not measured. No number is a threshold, and no check holds one.

<a id="r2"></a>**R2.** The mutation score of each module stays a work item of its own, in a scheduled workflow, when the decider asks for it.

<a id="r3"></a>**R3.** When the environment variable `CONSTITUTION_KIT_COVERAGE` names a folder, `scripts/check-aspects.py --run` runs each runner under `python3 -m coverage run`, with branch coverage and `patch = subprocess`. A folder holding a `python3` that calls the check's own interpreter goes first on the runner's `PATH`, so that a gate's `python3` is the measured one. After the run, a red one too, and before it reads the runner's lines, the check writes `<folder>/<module>.json`: the runner's exit, the run's time, and coverage.py's lists of executed and missing lines and branches per measured file. coverage.py not installed, or a step of it that fails, is a BROKEN line of the check. Empty or absent, the variable changes nothing. The code that does this is the kit's `scripts/kit_coverage.py`, whose docstring defines the file.

<a id="r4"></a>**R4.** The kit's CI installs coverage.py at a pinned version in every job of its matrix, the jobs of the gate list, and sets the variable in each module's job, where the fixtures entry writes the module's file. The folder is uploaded as the artifact `coverage-<module>`, kept 5 days. After its verdict, the job `gates` downloads every such artifact, runs `scripts/module-coverage.py --from` over the files, writes the table and the notes to the log and the run's summary, and uploads the JSON as the artifact `coverage`. Those steps carry `if: ${{ !cancelled() }}`, `continue-on-error: true` and `timeout-minutes: 5`, as R2 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r2) gives the metrics steps. This reverses R6 of that record for the coverage, and narrows its R5 to the mutation score.

<a id="r5"></a>**R5.** The kit's `scripts/module-coverage.py` reads the files, one per module, and prints one table: per module the four ratios with their counts, the runner's exit and the run's time; a totals row whose own numbers join every module and whose shared numbers are the union of every module's runs. It gives the same numbers as JSON with `--json <path>` or `--json -`. Without `--from` it makes the files first, running the fixtures entry of each module, or of those `--module` names, with the variable set. It is kit tooling, never shipped in a module, and advisory. It exits 0 whenever the files could be read or made, and 1 with a line that says what failed, why and the fix when they cannot. It has no `--self-test`, for the reason R3 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r3) gives. It is named `module-coverage`: never `check-`, since it is no check, and never `coverage`, which would shadow the package it runs. Its docstring defines each JSON key.

<a id="r6"></a>**R6.** The self-test of `scripts/check-aspects.py` holds the coverage mode: a green run and a red one each write the module's file, with a gate that a child process ran counted as executed and a file that no run imports counted as missed; with the variable unset, no file is written. It needs coverage.py installed.

## Applied

The commits before the one that creates this record built the report as a weekly workflow of its own, the answer to the second question as first recommended. The commit that rewrites this record moves it into the workflow `gates`, as the decider chose. It adds the coverage mode, removes the workflow `coverage.yml`, and states R1, R3 and R4 in [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI". It states R2 in step 9 of the [rollout plan](../rollout-plan.md#s9). It also states R4's change to R5 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r5) in the docstring of `scripts/metrics.py`, where that ruling is carried.

## Carry list

1. R1 — [`scripts/kit_coverage.py`](../../scripts/kit_coverage.py), its docstring; [`scripts/module-coverage.py`](../../scripts/module-coverage.py), its docstring.
2. R2 — pending: [the rollout plan](../rollout-plan.md#s9), step 9, the mutation score of each module.
3. R3 — [`scripts/kit_coverage.py`](../../scripts/kit_coverage.py), its docstring; [`scripts/check-aspects.py`](../../scripts/check-aspects.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
4. R4 — [the workflow](../../.github/workflows/gates.yml), its header and the steps of the module jobs and of the job `gates`; [`scripts/metrics.py`](../../scripts/metrics.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
5. R5 — [`scripts/module-coverage.py`](../../scripts/module-coverage.py), its docstring.
6. R6 — [`scripts/check-aspects.py`](../../scripts/check-aspects.py), its docstring of `--self-test`.
