---
id: dec-0127-mutation-line-map-blind-spots
type: task-record
title: The line map of the mutation report sees copies of the plugin, children under python3 -S and the continuation lines of folded constants
status: active
stakes: process
decider: Eugene Chernyshov
---

# The line map of the mutation report sees copies of the plugin, children under python3 -S and the continuation lines of folded constants

## Context

The mutation report runs each mutant only against the tests that reach its lines. A mutant is the module's own Python with one small change. The reach comes from a line map: one run of the module's tests under coverage.py (R3 of [dec-0122-module-mutation-report](dec-0122-module-mutation-report.md#r3)). A mutant that no test reaches is counted as not covered, and no test runs on it.

On 2026-11-12 a session measured every mutant of all twelve modules, for [item 9.38 of the rollout plan](../rollout-plan.md#s9-38). Readers then sorted each survivor and each mutant that was not covered. They found 129 mutants that a test does run and would kill, in a process the line map cannot see. So those mutants were never run, and every score was a little too low. The map was blind in four places:

1. A test that copies the plugin with `shutil.copytree` and runs the copy: coverage.py records the copy's paths, outside the module's folder, and the map keeps only that folder. 48 mutants, all in module [`const-change-cost`](../requirements.md#const-change-cost).
2. A child that a test starts as `python3 -S <file>`: under `-S` Python reads no `.pth` file, and coverage.py starts in a child through one. 33 mutants in four modules.
3. A child under a limit on the size of the files it may write, `RLIMIT_FSIZE`: it cannot write coverage.py's data file. 5 mutants, all in module [`const-locations`](../requirements.md#const-locations).
4. The continuation lines of a constant that the compiler folds into one: no bytecode stands on them, so coverage.py sees no line run there. 43 mutants in three modules, most in [`const-language`](../requirements.md#const-language).

<!-- MEASURE: the whole runs of const-change-cost and const-language on the branch go here. -->

## Options

- **A. Fix the first, second and fourth places; leave the third, and say so.** The map measures copies and maps them back, starts coverage.py in a `-S` child, and looks up a line with no bytecode at the line that runs it. The docstring names the size limit as a child the map does not measure.
  - **Pros:** 124 of the 129 mutants are run, by kit code that uses only coverage.py's public interface; each fix has a self-test case that is red without it.
  - **Cons:** five mutants stay not covered; the map's run differs from a plain test run in one way, the tests' `sys.executable`.
- **B. Fix all four places.** As A, and the size limit too: the map's run would keep the limit's hard value, and patch coverage.py so that a child raises its soft limit before coverage.py saves.
  - **Pros:** all 129 mutants are run.
  - **Cons:** it patches a test's own call of `resource.setrlimit` and a private method of coverage.py, `Coverage._atexit`; a new release of coverage.py can break it in silence, for five mutants of one module.
- **C. Leave the map as it is.** The docstring already says the count of mutants not covered can be too high.
  - **Pros:** no work, no new code.
  - **Cons:** 129 mutants are never run, the scores stay low, and a survivor list can never show those mutants.

## Recommendation

Option A, recommended by the session. It runs almost every hidden mutant with public interfaces only, and the five it leaves are named where a reader looks.

## Choice

<!-- CHOICE: the decider's answer goes here. -->

## Ruling

<a id="r1"></a>**R1.** The run of the line map measures every file whose path holds a folder named `scripts`, not only the module's own folder. A file measured outside the copy of the kit stands for a file of the module. That file is the one below `plugin/scripts` that the part of the path after its last folder named `scripts` names, when the module has it. A file the module does not have is left out, and so is a path that holds a line break, which coverage.py does not match.

<a id="r2"></a>**R2.** In the run of the line map alone, the report's pytest plugin makes a file the report writes the tests' `sys.executable`. That file runs `-S <file>` through `scripts/kit_mutation_boot.py`, and hands every other call to the real interpreter unchanged. The boot file starts coverage.py from a folder that holds coverage.py alone, put last on the path, then runs the file as Python would under `-S`. No mutant's run uses it. A child started under `-S` in another way stays unmeasured.

<a id="r3"></a>**R3.** A mutant is looked up in the line map at those of its lines that hold bytecode. Where none of them does, it is looked up at the first line of the nearest node around it, up to its statement, that holds bytecode. Where there is no such line either, the mutant is not covered.

<a id="r4"></a>**R4.** A child under a limit on the size of the files it writes stays unmeasured. The report's docstring names it, beside a child started with an environment of its own, as a reason the count of mutants not covered can be too high.

<a id="r5"></a>**R5.** The score, the outcomes and every key of the JSON keep their meaning. Only the tests chosen for a mutant can change, so a mutant may move from not covered to killed or to survived. A kill still means that a test failed on the mutated file.

<a id="r6"></a>**R6.** The self-test of the report holds each of R1, R2 and R3 with a case of its own, on its fixture kit. Each case is red when its fix is taken out.

<a id="r7"></a>**R7.** This record widens R3 of [dec-0122-module-mutation-report](dec-0122-module-mutation-report.md#r3): the line map holds what R1 to R3 add. The rest of that ruling stands as written.

## Applied

The commits of the branch before this record change `scripts/kit_mutation.py`, `scripts/kit_mutation_plugin.py` and `scripts/module-mutation.py`, and add `scripts/kit_mutation_boot.py`. Each item is applied there, so the record is born `inactive`.

## Carry list

1. R1 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map.
2. R2 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map; [`scripts/kit_mutation_plugin.py`](../../scripts/kit_mutation_plugin.py), its docstring; [`scripts/kit_mutation_boot.py`](../../scripts/kit_mutation_boot.py), its docstring.
3. R3 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map.
4. R4 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the outcome `not covered`.
5. R5 — history only: a finding of the day, that no key changes its meaning.
6. R6 — [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its self-test, the cases on a copy, on `-S` and on a folded constant.
7. R7 — history only: the widening of one ruling of an earlier record, an act of this record.
