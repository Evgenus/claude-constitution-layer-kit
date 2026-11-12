---
id: dec-0070-runners-import-through-links-in-tests
type: task-record
title: Fixture runners import the shared and their own packages through links in tests/, no module file edits its own import path, and the install keeps the runner's link to its own package
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Fixture runners import the shared and their own packages through links in tests/, no module file edits its own import path, and the install keeps the runner's link to its own package

## Context

Each module's fixture runner, `tests/run.py`, imports two packages that live in the module's `scripts/`: the shared gate package `const_gate`, reached there through the link `scripts/const_gate`, and the module's own package, such as `interaction_gate`. Until this change every runner put its `scripts/` folder first on the import path by one line, `sys.path.insert(0, str(SCRIPTS))`, and marked each import after that line `# noqa: E402`, since an import below a statement breaks the rule of imports at the top ([template §6](../../module-template/gate-script-rules.md#r16), rule 16). The line was a routine call made under [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md), and item 8 of [kit-shared-gate-code §2](../../shared/GATE.md#g2) stated it.

Every module is a draft at `0.0.x`, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). Two questions were put to the decider in chat; sections 1 and 2 hold them.

## 1. How the runner reaches the packages

The runner already imported `harness.py`, `consumer.py` and `shared_items.py` with no such line: they are relative links in its own `tests/` folder, and Python puts the folder of the script it runs first on the import path ([sys.path initialization](https://docs.python.org/3/library/sys_path_init.html)). The decider asked in chat on 2026-10-05 whether the path line could go, with the two packages reached the same way.

Two facts were checked before the change. Every `__file__` the module packages read goes through `Path.resolve()`, so a package imported through a link in `tests/` still finds the module's root; `const_gate` reads no `__file__`. The constant `SCRIPTS`, and `MODULE_ROOT` in the six runners that have it, cannot go: the runners hand `SCRIPTS` to `Harness` and read the module's own files from `MODULE_ROOT`.

- **A. Keep the path line.** The runner goes on putting `scripts/` on the import path.
  - **Pros:** no change; no new link to hold.
  - **Cons:**
    - **the one place where a module's runner edits its own import path** stays, with six to ten `noqa` markers in each runner;
    - **the type check of `tests/` needs `MYPYPATH=../scripts`** to find the packages.
- **B. Links in `tests/`, held by the shared-links check.** `tests/const_gate` and `tests/<package>` for each of the module's own packages, relative links; `scripts/check-shared-links.py` derives both from the folders and turns red on a missing, copied or misdirected one.
  - **Pros:**
    - **no module file edits its own import path**;
    - **the imports stand at the top** with no marker;
    - **the runner reaches the code** exactly as it reaches the shared test files;
    - **mypy needs no path**;
    - **a copy of a package left in `tests/`** cannot drift from what the gate runs unnoticed.
  - **Cons:** 22 more links in the tree, and the shared-links check now also holds a link that is no shared code.
- **C. Links in `tests/`, held by no check.** As B, but a broken link is found only when the runner fails to import.
  - **Pros:** the check stays about shared code alone.
  - **Cons:** a missing link fails the runner loudly, but a plain copy of the package in `tests/` passes in silence and tests code the gate no longer runs.

Recommendation: B, since it removes the runner's path edit and only a check turns a copy red; the session recommended it.

The decider chose the links in chat on 2026-10-07 ("apply that change for all modules"). The check of R3 and the target of R4 are defaults the session took in applying it, left open to override at the yes. The kit's own tooling outside the modules, `scripts/check-schema-mirror.py` and a runner `scripts/check-aspects.py` generates in its self-test, still edits a path; R2 does not reach it.

<a id="r1"></a>**R1.** Each module that uses the shared code has, in `tests/`, the relative link `const_gate` → `shared/const_gate`, and for each folder at the top of its `scripts/`, itself no link, that holds an `__init__.py`, whose name starts with neither `.` nor `_`, save `const_gate`, the relative link `tests/<package>` → `../scripts/<package>`. These links widen the list of item 2 of dec-0025-shared-gate-code-linked, whose ruling otherwise stands.

<a id="r2"></a>**R2.** The runner imports the shared package, the module's own packages and the shared test files through those links, from its own folder. No Python file a module ships edits the import path of its own process, the runner included. The runner's imports stand at the top with no `E402` marker. The rule binds that process alone: any child process the runner starts may be given a path of its own. Two do so today: shared item 112's shim puts the entry's folder first as Python does for a script, and a case may set `PYTHONPATH` to hide or replace a library for the gate.

<a id="r3"></a>**R3.** `scripts/check-shared-links.py` holds the links of R1, derived from the folders: a missing link, a copy, a plain file, a dangling, absolute or misdirected link, and one that reaches its source through another link, is red. A finding on a link to the module's own package says why in its own words: the runner must import the code the gate runs.

<a id="r4"></a>**R4.** `tests/const_gate` points straight at `shared/const_gate`, like the shared test files, and not through `scripts/const_gate`; R3's red for a link through another link holds it.

<a id="r5"></a>**R5.** The gate list's type check of a module's `tests/` runs with no `MYPYPATH`.

## 2. The runner's link in an installed copy

R2 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r2) makes the install check, `scripts/check-bare-install.py`, red when a link of a module's source leads inside the module, so that an installed copy carries all it runs as real files. The link `tests/<package>` → `../scripts/<package>` of R1 is such a link. On the pull request's first CI run, on 2026-10-07, the check was red for every module with one finding each, such as "the link tests/questions_gate is left a link in the installed copy"; its hooks and scans passed. The platform's install copies a link that leads elsewhere in the marketplace as the files it points at, and keeps one that stays inside the plugin as a link, as its documentation says ([kit-shared-gate-code §4](../../shared/GATE.md#g4), limit 3). The kept link leads to a real folder of the same copy.

- **A. Narrow R2 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r2) for the runner's links only.** The one inside link of R1 is allowed. The install check holds that it arrives leading to the module's own package in the copy; every other inside link stays red.
  - **Pros:** keeps the runner free of a path edit; matches what the platform does and documents; the exception is narrow and checked.
  - **Cons:**
    - **it narrows an accepted ruling**;
    - **an installed copy is no longer free of links**, though the one link left serves the fixtures alone, never a hook or a scan.
- **B. Keep the path edit for the module's own package only.** `tests/const_gate` stays, the runner keeps one `sys.path` line for its own `scripts/`, and the `tests/<package>` links go.
  - **Pros:** dec-0059 stays as it is; no link is left in an installed copy.
  - **Cons:** half of what the decider asked; the path edit and its markers stay in every runner.
- **C. Drop the change.**
  - **Pros:** no ruling changes.
  - **Cons:** the path edit stays; the work is lost.

Recommendation: A, since the kept link leads to a real folder of the same copy, so the copy still carries all it runs; the session recommended it.

The decider answered in chat on 2026-10-07 that the shared files serve only the kit's own development, and that in another project the kernel holds no code and each module ships the common files within itself. The session read that as A: a link from `tests/` to the module's own `scripts/` stays within the module. That the exception covers the runner's links alone, and no other link inside a module, is a default the session took, left open to override at the yes.

<a id="r6"></a>**R6.** R2 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r2) is narrowed: a link of the source that leads inside the module is allowed in one shape only, the runner's link `tests/<package>` → `../scripts/<package>` to a package of the module's own as R1 derives it. The install check holds that it arrives in the installed copy as a link leading to that package in the copy, and is red otherwise. Every other link inside the module stays red as R2 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r2) rules.

## Applied

The commits of this branch apply every item. The first adds the links and edits the 11 runners. The second widens the shared-links check. The third changes the documents and the gate list and adds this record. The commits after the carry audit's first round hold its fixes, the red for a link through another link and the install check's exception among them, each message naming what it changed. The record is born `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7, and its opening paragraph; [template §6](../../module-template/gate-script-rules.md#r1), rule 1, and the `tests/` line of the section "Plugin skeleton" of the [template](../../module-template/slot-guidance.md#s1); [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module"; each module's `MODULE.md`, the row `tests` of its artifacts table, and its `INSTALL.md`, the sentence on copying the plugin's folder. The widening of item 2 of dec-0025-shared-gate-code-linked is history.
2. R2 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 8; [template §6](../../module-template/gate-script-rules.md#r1), rule 1; [the harness](../../shared/constitution_layer_kit/testing/harness.py), its docstring.
3. R3 — [check-shared-links](../../scripts/check-shared-links.py), its docstring; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7, and row K1 of [§5](../../shared/ITEMS.md#g5).
4. R4 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7; [check-shared-links](../../scripts/check-shared-links.py), its docstring.
5. R5 — [the gate list](../../scripts/gate-list.sh), its entry `types-<module>`; [pyproject.toml](../../pyproject.toml), its list of commands.
6. R6 — [the install check](../../scripts/check-bare-install.py), its docstring; [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [kit-shared-gate-code §4](../../shared/GATE.md#g4), limit 3; each module's `INSTALL.md`, the sentence on copying the plugin's folder. The narrowing of R2 of dec-0059-bare-repo-install-in-ci is history.
