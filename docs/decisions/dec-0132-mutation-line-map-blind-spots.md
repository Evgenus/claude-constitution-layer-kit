---
id: dec-0132-mutation-line-map-blind-spots
type: task-record
title: The line map of the mutation report sees four kinds of test run it missed
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The line map of the mutation report sees four kinds of test run it missed

## Context

The mutation report runs each mutant only against the tests that reach its lines. A mutant is the module's own Python with one small change. The reach comes from a line map: one run of the module's tests under coverage.py (R3 of [dec-0122-module-mutation-report](dec-0122-module-mutation-report.md#r3)). A mutant that no test reaches is counted as not covered, and no test runs on it.

On 2026-11-12 a session measured every mutant of all twelve modules, for [item 9.38 of the rollout plan](../rollout-plan.md#s9-38). Readers then sorted each survivor and each mutant that was not covered. They found 129 mutants that a test does run and would kill, in a process the line map cannot see. So those mutants were never run, and every score was a little too low. The map was blind in four places:

1. A test that copies the plugin with `shutil.copytree` and runs the copy. coverage.py records the copy's paths, outside the module's folder, and the map keeps only that folder. 48 mutants, all in module [`const-change-cost`](../requirements.md#const-change-cost).
2. A child that a test starts as `python3 -S <file>`: under `-S` Python reads no `.pth` file, and coverage.py starts in a child through one. 33 mutants in four modules.
3. A child under a limit on the size of the files it may write, `RLIMIT_FSIZE`: it cannot write coverage.py's data file. 5 mutants, all in module [`const-locations`](../requirements.md#const-locations).
4. The continuation lines of a constant that the compiler folds into one: no bytecode stands on them, so coverage.py sees no line run there. 43 mutants in three modules, most in [`const-language`](../requirements.md#const-language).

The session first fixed the first, second and fourth places on its branch. Then it measured every mutant again in the two modules with the most such mutants. It used eight copies, on 2026-11-12. All 107 mutants that the readers had sorted this way in those two modules were killed: 77 in [`const-change-cost`](../requirements.md#const-change-cost) and 30 in [`const-language`](../requirements.md#const-language). In `const-change-cost`, 113 mutants were no longer not covered: 82 were killed and 31 survived. The 31 sit in the entry files that a copy or a `-S` child runs. The readers had sorted most of them as behaviour no test holds. The score of `const-change-cost` rose from 74.6% to 79.7%, and that of `const-language` from 79.1% to 82.6%. The same four mutants as before ended as an error, none of them reached by these fixes. The session also built the line map of the other ten modules: the unmutated tests of each stayed green. Their count of mutants not covered fell only where the readers had found such mutants. It fell from 64 to 52 in [`const-doc-budgets`](../requirements.md#const-doc-budgets), from 115 to 97 in [`const-interaction`](../requirements.md#const-interaction) and from 60 to 48 in [`const-referencing`](../requirements.md#const-referencing). The other seven kept their counts.

After the choice below, the session fixed the third place too, and measured every mutant of [`const-locations`](../requirements.md#const-locations) again, with eight copies. Its five such mutants were killed, each by the test that runs the child under the limit. Its mutants not covered fell from 45 to 42, and its score rose from 79.6% to 80.3%. The one mutant that ended as an error had ended so before. The line map of each of the twelve modules was then built again, and the unmutated tests of each stayed green. Only `const-locations` changed its count of mutants not covered.

## Options

- **A. Fix the first, second and fourth places; leave the third, and say so.** The map measures copies and maps them back, and starts coverage.py in a `-S` child. It looks up a line with no bytecode at the line that runs it. The docstring names the size limit as a child the map does not measure.
  - **Pros:** 124 of the 129 mutants are run, by kit code that uses only coverage.py's public interface. Each fix has a self-test case that is red without it.
  - **Cons:** five mutants stay not covered; the map's run differs from a plain test run in one way, the tests' `sys.executable`.
- **B. Fix all four places.** As A, and the size limit too. The map's run would keep the limit's hard value, and patch coverage.py so that a child raises its soft limit before coverage.py saves.
  - **Pros:** all 129 mutants are run.
  - **Cons:** it patches a test's own call of `resource.setrlimit` and a private method of coverage.py, `Coverage._atexit`. A new release of coverage.py can break it in silence, for five mutants of one module.
- **C. Leave the map as it is.** The docstring already says the count of mutants not covered can be too high.
  - **Pros:** no work, no new code.
  - **Cons:** 129 mutants are never run, the scores stay low, and a survivor list can never show those mutants.

## Recommendation

Option A, recommended by the session. It runs almost every hidden mutant with public interfaces only, and the five it leaves are named where a reader looks.

## Choice

Option B, chosen by the decider in chat on 2026-11-12, over the recommendation. The decider gave no reason beyond the letter.

Building it, the session found a way that needs no private method of coverage.py at all. Python runs the handlers of a process's exit last registered first. So a handler that the child registers after coverage.py has started runs before the handler of coverage.py, which saves the data. Only the test's call of `resource.setrlimit` is still patched, in the run of the line map alone. The second half of B's cons falls away with the private method: a release of coverage.py that breaks the fix in silence. A change in the rule on exit handlers would break it, but that rule is part of Python's documented `atexit` module.

## Ruling

<a id="r1"></a>**R1.** The run of the line map measures every file whose path holds a folder named `scripts`, not only the module's own folder. A file measured outside the copy of the kit stands for a file of the module. That file is the one below `plugin/scripts` that the part of the path after its last folder named `scripts` names, when the module has it. A file the module does not have is left out. So is a path that holds a line break, which coverage.py does not match.

<a id="r2"></a>**R2.** The report writes a file of its own. In the run of the line map alone, its pytest plugin makes that file the tests' `sys.executable`. In that run, the `python3` the report puts first on PATH hands on to that file too. That file runs `-S <file>` through `scripts/kit_mutation_boot.py`. The boot file puts last on the path a folder that holds coverage.py alone, and starts coverage.py from it. Then it runs the file as Python would under `-S`. No mutant's run uses it. A child started under `-S` in another way stays unmeasured.

<a id="r3"></a>**R3.** A mutant is looked up in the line map at those of its lines that hold bytecode. Where none of them does, it is looked up at the first line of the nearest node around it that holds bytecode. The search stops at the mutant's statement. Where there is no such line either, the mutant is not covered.

<a id="r4"></a>**R4.** In the same run, a test's call of `resource.setrlimit` on the limit on file size sets the soft value alone and keeps the hard one. The soft value is the one a write meets, so the test's child fails its write as before. The file of R2 runs `<file>` under a soft limit below the hard one through the boot file as well. The boot file registers a handler of the process's exit that lifts the soft limit to the hard one. Registered after coverage.py's own, it runs before it, once the file and its own handlers have ended. A `-S <file>` call takes the boot file whatever the limit. Every other call the file of R2 hands to the real interpreter unchanged. A child stays unmeasured when its limit is still too low for coverage.py's data file as it exits. Its hard value may be too low, as when a shell's plain `ulimit -f` sets both values. Or its soft value may be, with no boot file run to lift it. One example is a child started with another option before its file, or by another interpreter.

<a id="r5"></a>**R5.** The score, the outcomes and every key of the JSON keep their meaning. Only the tests chosen for a mutant can change, so a mutant may move from not covered to killed or to survived. A kill still means that a test failed on the mutated file.

<a id="r6"></a>**R6.** The self-test of the report holds each of R1 to R4 with a case of its own, on its fixture kit. Each case is red when its fix is taken out.

<a id="r7"></a>**R7.** This record widens R3 of [dec-0122-module-mutation-report](dec-0122-module-mutation-report.md#r3): the line map holds what R1 to R4 add. The rest of that ruling stands as written.

## Applied

The commits of the branch before this record change `scripts/kit_mutation.py`, `scripts/kit_mutation_plugin.py` and `scripts/module-mutation.py`, and add `scripts/kit_mutation_boot.py`. The commit that creates this record started it `active`, before the choice. Every item is applied by the end of the branch, and its last commit sets the record `inactive`.

## Carry list

1. R1 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map.
2. R2 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map; [`scripts/kit_mutation_plugin.py`](../../scripts/kit_mutation_plugin.py), its docstring; [`scripts/kit_mutation_boot.py`](../../scripts/kit_mutation_boot.py), its docstring.
3. R3 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map.
4. R4 — [`scripts/kit_mutation.py`](../../scripts/kit_mutation.py), its docstring, the paragraph on the line map; [`scripts/kit_mutation_plugin.py`](../../scripts/kit_mutation_plugin.py), its docstring; [`scripts/kit_mutation_boot.py`](../../scripts/kit_mutation_boot.py), its docstring.
5. R5 — history only: a finding of the day, that no key changes its meaning.
6. R6 — [`scripts/module-mutation.py`](../../scripts/module-mutation.py), its self-test, the cases on a copy, on `-S`, on a folded constant and on a limit on file size.
7. R7 — history only: the widening of one ruling of an earlier record, an act of this record.
