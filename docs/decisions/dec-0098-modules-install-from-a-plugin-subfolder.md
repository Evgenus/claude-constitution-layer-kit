---
id: dec-0098-modules-install-from-a-plugin-subfolder
type: task-record
title: Each module installs from its plugin/ subfolder, and a project's fixtures are optional, run from a kit clone
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Each module installs from its plugin/ subfolder, and a project's fixtures are optional, run from a kit clone

## Context

A project installs a module by copying a folder into the platform's plugin cache. The platform's documentation names no list of files to leave out: a plugin given by a relative path is copied whole. Until this record, the folder a project installed was the whole module folder, `modules/<m>/`. So each project installed the module's tests, its eval cases, its `MODULE.md` and its `README.md`, which no session uses. On a scratch install of every module on 2026-10-20, the cache held 670 files, 7.4 MB, and more than half of them were tests, eval cases and copies of the shared code. The marketplace clone beside it held about 10 MB.

One rule kept the tests inside the installed folder. The second sentence of R11 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r11) had a project verify an install by running pytest on `<plugin root>/tests`. So no slimmer install was possible while that sentence stood. The session measured the options on scratch installs on 2026-10-19 and 2026-10-20 and put them to the decider on 2026-10-20, in two questions.

## 1. What a project installs

- **A. Keep it as it is.** Each module folder installs whole, fixtures included, from a full marketplace clone.
  - **Pros:** no work; the consumer's verification in R11 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r11) stands; the kit's CI already proves it.
  - **Cons:** every machine keeps 670 cached files and a 10 MB clone, more than half of them repeated shared code, tests and eval cases that no session uses.
- **B. A sparse marketplace clone only.** The install guide adds `--sparse .claude-plugin modules shared` to the command that adds the marketplace.
  - **Pros:** a routine edit in one pull request, already tried; it halves the clone.
  - **Cons:** the cache stays at 670 files, tests and eval cases included.
- **C. A slim release branch.** The kit's CI writes a built `release` branch without tests and eval cases, and projects add the marketplace at `#release`.
  - **Pros:** 399 cached files; the kit's module layout stays as it is.
  - **Cons:**
    - **a branch written by a machine**, a new workflow and ruleset, and a built form to install and test on every pull request;
    - **a `process` record**.
- **D. Link mode.** Each marketplace entry becomes a `command` source that links into the platform's marketplace clone.
  - **Pros:** no copies at all.
  - **Cons:**
    - **not the standard use of that source**;
    - **the code changes under a fixed version**;
    - **each person accepts the command by hand**, and in the session's test `--yes` did not accept it without a terminal, which blocks the kit's CI.
- **E. The plugin as a subfolder.** Only `modules/<m>/plugin/` installs, and tests, eval cases, `MODULE.md` and `README.md` stay beside it.
  - **Pros:**
    - 377 cached files;
    - **a standard install from the main branch**, a plugin in a subfolder being the platform's own example;
    - **no branch written by a machine**;
    - **the kit's install checks keep testing exactly what installs**;
    - **an eval case outside its plugin was tried and works**.
  - **Cons:**
    - **a one-time move that touches every module**, at least six of the kit's checks and the module template;
    - **an install from GitHub with the shared-code link one level deeper had not been run**;
    - **a `process` record**.

The session recommended E. It gives the same slim install as C without a branch written by a machine and without a second form to test: its cost comes once, while C's comes back with every change. B stays open beside any option; its stakes would be priced when it is proposed. The decider chose E in chat on 2026-10-21.

<a id="r1"></a>**R1.** Each module's installed parts stand in the folder `modules/<m>/plugin/`, the plugin root and the only folder a project installs: `.claude-plugin/`, `hooks/`, `skills/`, `scripts/`, `requirements.txt` and `INSTALL.md`, and `commands/` and `agents/`, for those the module has. `MODULE.md`, `README.md`, `tests/` and `evals/` stand at the top of `modules/<m>/` and are never installed. Each module's entry in the kit's marketplace file has the source `./modules/<m>/plugin`. The module template takes the same split: `module-template/plugin/` holds the parts that install.

<a id="r2"></a>**R2.** A module's `README.md` stays at the top of the module's folder, while its `INSTALL.md` ships inside `plugin/`, so the page links `plugin/INSTALL.md`. This replaces "beside `INSTALL.md`" in R1 of [dec-0077-module-readme-pages](dec-0077-module-readme-pages.md#r1); the rest of that ruling stands.

<a id="r3"></a>**R3.** Each eval case names its plugin, `plugins:` listing `../../plugin`, since the case sits outside the plugin it tests. `claude plugin eval modules/<m>` runs a module's cases with the plugin loaded from `plugin/`. This adds to R1 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r1), whose `evals/` stays at the top of the module's folder.

<a id="r4"></a>**R4.** Where an earlier ruling names one of the installed parts of R1 by its place in a module's folder, it reads that part under `plugin/`, and the rest of the ruling stands:
1. the gate list runs `modules/<module>/plugin/scripts/<entry>.sh --scan` or `….py --scan` in R2 of [dec-0056-portability-grep-and-gate-lists](dec-0056-portability-grep-and-gate-lists.md#r2);
2. the source whose installed copy the install check holds, in R2 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r2), is the module's `plugin/` folder, its hooks file `plugin/hooks/hooks.json`; the scans it runs are still those the module's document declares, read from `modules/<m>/MODULE.md`; and a link of the source that "leads inside the module", in that ruling, is one that stays inside the plugin folder;
3. the marketplace source in R2 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r2) is `./modules/<name>/plugin`;
4. the runner's links of R1 of [dec-0070-runners-import-through-links-in-tests](dec-0070-runners-import-through-links-in-tests.md#r1) are derived from the folders at the top of `plugin/scripts/` and lead `tests/<package>` → `../plugin/scripts/<package>`;
5. the install check keeps the allowance of R6 of [dec-0070-runners-import-through-links-in-tests](dec-0070-runners-import-through-links-in-tests.md#r6) for such a link inside the source; since the runner's links stand in `tests/`, outside the plugin folder, no module's source holds one now;
6. the tests' link to the shared code in R4 of [dec-0070-runners-import-through-links-in-tests](dec-0070-runners-import-through-links-in-tests.md#r4) leads straight to `shared/constitution_layer_kit`, never through `plugin/scripts/constitution_layer_kit`;
7. the reinstall claim of R5 of [dec-0071-projects-install-from-github](dec-0071-projects-install-from-github.md#r5) compares a module's cached copy with the module's `plugin/` folder in the platform's clone of the marketplace;
8. the guide's scan path in R4 of [dec-0086-three-id-exceptions-partial-surveys-and-three-kit-holds](dec-0086-three-id-exceptions-partial-surveys-and-three-kit-holds.md#r4) is `<module>/plugin/scripts/<name>.sh`, and the coverage pair of R5 of [dec-0086-three-id-exceptions-partial-surveys-and-three-kit-holds](dec-0086-three-id-exceptions-partial-surveys-and-three-kit-holds.md#r5) holds `modules/<module>/<path>/**` for each of `plugin/scripts`, `plugin/hooks`, `plugin/skills`, `tests` and `evals` that the module has;
9. the module's own Python in R1 of [dec-0089-module-coverage-report](dec-0089-module-coverage-report.md#r1) is under `modules/<module>/plugin/scripts`;
10. the eval hash of R5 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r5) leaves out `plugin/INSTALL.md` where it left out `INSTALL.md`, and the skills of R10 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r10) are those under `plugin/skills/`;
11. the link to the shared code in R1 of [dec-0096-shared-package-named-constitution-layer-kit](dec-0096-shared-package-named-constitution-layer-kit.md#r1) is `plugin/scripts/constitution_layer_kit`, which climbs four levels to `shared/constitution_layer_kit`; `tests/constitution_layer_kit` keeps its place.

## 2. A project's fixtures

C and E drop the tests from the install. Each needs an answer to the consumer's verification in R11 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r11). The fixtures catch one thing that nothing else catches: a difference on the project's machine, another OS or another version of git, Python or Vale, that breaks a gate's logic while the gate still starts. Everything else is covered without them. The kit's CI runs every module's fixtures on every pull request, and the decider runs them on macOS. Each gate stops with exit 1, never with a silent pass, when a tool it needs or its shared code is missing. Step 8 of the install guide's bootstrap runs every scan on the project itself.

- **A. Optional, from a kit clone.** The install guide keeps one step: a project that wants the fixtures runs them from its kit clone, checked out at the commit its install records, and pytest becomes an optional prerequisite.
  - **Pros:**
    - **the one check that catches a break on the project's machine stays within reach**;
    - **the platform records the installed commit**, so the tests match the installed code exactly.
  - **Cons:** the guide keeps a step that most projects will skip.
- **B. Gone.** That step goes too, and a project checks its install with the plugin list, the skills and the scans alone.
  - **Pros:** the shortest guide.
  - **Cons:** a project loses its only way to run the kit's tests on its own machine.

The session recommended A: it costs one step and keeps the check within reach. The decider chose it with E in chat on 2026-10-21, whose text named the fixtures optional from a kit clone.

<a id="r5"></a>**R5.** A project need not run a module's fixtures, which its install no longer holds. A project that wants to runs them from a clone of the kit, checked out at the commit its install records, `gitCommitSha` in the platform's `installed_plugins.json`, with pytest installed; for a project that loads the modules from its clone, that clone as it is. This replaces the consumer's verification in the second sentence of R11 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r11). Its pins, and its clause that a module's `requirements.txt` names neither pytest nor pytest-xdist, stand.

## Applied

The commits of this change before the one that creates this record apply every ruling. The first moved the parts of R1 with `git mv`. It pointed the 22 links at their old targets again. It repaired the links into the moved parts. It rewrote the path texts outside records and comparisons. It gave each eval case its `plugins:` line. It pointed the marketplace's sources at `plugin/`. The next ones taught each kit check, report and fixture the layout, one commit per check. The last before the record edited the current-state documents: the kit guide, the install guide, the shared-code page, the module template and its page, and each module's document, install note and page. The record is born `inactive`. The carry audit's first round corrected R1, R4 and R5 in place before the yes, with the documents they name.

## Carry list

1. R1 — [CLAUDE.md](../guide/developing-a-module.md#s1), steps 1 and 4 of "Developing a module" and the bullet "The gate list and CI"; [the template](../../module-template/MODULE.md), its opening note, the path column of [its §6](../../module-template/MODULE.md#t6) and the section "Plugin skeleton"; [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r3), rule 3; [plc-0010-style-guide](../policies/plc-0010-style-guide.md#r1), rule 1; [the marketplace file](../../.claude-plugin/marketplace.json), its sources; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring; each module's `MODULE.md`, the path column of its artifacts table.
2. R2 — [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module"; [the template](../../module-template/slot-guidance.md#s1), the section "Plugin skeleton"; [the template's page](../../module-template/README.md), its note and its fifth section.
3. R3 — [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module"; [the template](../../module-template/MODULE.md), the row `eval case` of the table of [its §6](../../module-template/MODULE.md#t6) and the section "Plugin skeleton"; [kit_evals](../../scripts/kit_evals.py), its docstring; each module's eval cases, their `plugins:` line.
4. R4 — [check-gate-lists](../../scripts/check-gate-lists.py), its docstring; [CLAUDE.md](../guide/gate-list-and-ci.md), the bullet "The gate list and CI"; [check-bare-install](../../scripts/check-bare-install.py), its docstring; [check-session-load](../../scripts/check-session-load.py), its docstring; [check-install-guide](../../scripts/check-install-guide.py), its docstring; [check-shared-links](../../scripts/check-shared-links.py), its docstring; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7, and limit 3 of [its §4](../../shared/GATE.md#g4); [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [kit_coverage](../../scripts/kit_coverage.py), its docstring; [kit_evals](../../scripts/kit_evals.py), its docstring and `LEFT_OUT_FILES`.
5. R5 — [the install guide](../../INSTALL.md), item 3 of [its §1](../../INSTALL.md#s1), step 8 of [its §2](../../INSTALL.md#s2) and step 4 of [its §3](../../INSTALL.md#s3); [CLAUDE.md](../guide/developing-a-module.md#s5), step 5 of "Developing a module"; each module's `INSTALL.md`, its step on the fixtures. The clause of R11 on `requirements.txt` stands in that same item 3. That the pins of R11 of dec-0091-module-fixtures-run-as-pytest stand is history.
