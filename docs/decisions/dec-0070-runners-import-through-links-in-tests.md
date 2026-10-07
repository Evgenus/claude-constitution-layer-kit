---
id: dec-0070-runners-import-through-links-in-tests
type: task-record
title: Fixture runners import the shared and their own packages through links in tests/, and no code edits the import path
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Fixture runners import the shared and their own packages through links in tests/, and no code edits the import path

## Context

Each module's fixture runner, `tests/run.py`, imports two packages that live in the module's `scripts/`: the shared gate package `const_gate`, reached there through the link `scripts/const_gate`, and the module's own package, such as `interaction_gate`. Until this change every runner put its `scripts/` folder first on the import path by one line, `sys.path.insert(0, str(SCRIPTS))`, and marked each import after that line `# noqa: E402`, since an import below a statement breaks the rule of imports at the top ([template §6](../../module-template/MODULE.md#t6), rule 16). The line was a routine call made under [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md), and item 8 of [kit-shared-gate-code §2](../../shared/GATE.md#g2) stated it.

The runner already imported `harness.py`, `consumer.py` and `shared_items.py` with no such line: they are relative links in its own `tests/` folder, and Python puts the folder of the script it runs first on the import path ([sys.path initialization](https://docs.python.org/3/library/sys_path_init.html)). The decider asked in chat on 2026-10-05 whether the path line could go, with the two packages reached the same way.

Two facts were checked before the change. Every `__file__` the module packages read goes through `Path.resolve()`, so a package imported through a link in `tests/` still finds the module's root. `const_gate` reads no `__file__`. The constants `SCRIPTS` and `MODULE_ROOT` cannot go: the runners hand `SCRIPTS` to `Harness` and read the module's own files from `MODULE_ROOT`. Every module is a draft at `0.0.x`, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## Options

- **A. Keep the path line.** The runner goes on putting `scripts/` on the import path.
  - **Pros:** no change; no new link to hold.
  - **Cons:** the one place where kit code edits the import path stays, with six to ten `noqa` markers in each runner; the type check of `tests/` needs `MYPYPATH=../scripts` to find the packages.
- **B. Links in `tests/`, held by the shared-links check.** `tests/const_gate` and `tests/<package>` for each of the module's own packages, relative links; `scripts/check-shared-links.py` derives both from the folders and turns red on a missing, copied or misdirected one.
  - **Pros:** no code edits the import path; the imports stand at the top with no marker; the runner reaches the code exactly as it reaches the shared test files; mypy needs no path; a copy of a package left in `tests/` cannot drift from what the gate runs unnoticed.
  - **Cons:** 22 more links in the tree, and the shared-links check now also holds a link that is no shared code.
- **C. Links in `tests/`, held by no check.** As B, but a broken link is found only when the runner fails to import.
  - **Pros:** the check stays about shared code alone.
  - **Cons:** a missing link fails the runner loudly, but a plain copy of the package in `tests/` passes in silence and tests code the gate no longer runs.

## Recommendation

B: it removes the last path edit, and only a check turns a copy red; the session recommended it.

## Choice

The decider chose the links in chat on 2026-10-07 ("apply that change for all modules"). The check of R3 and the target of R4 are defaults the session took in applying it, left open to override at the yes.

## Ruling

**R1.** Each module that uses the shared code has, in `tests/`, the relative link `const_gate` → `shared/const_gate`, and for each folder at the top of its `scripts/` that holds an `__init__.py`, whose name starts with neither `.` nor `_`, save `const_gate`, the relative link `tests/<package>` → `../scripts/<package>`. These links widen the list of item 2 of dec-0025-shared-gate-code-linked, whose ruling otherwise stands.

**R2.** The runner imports the shared package, the module's own packages and the shared test files through those links, from its own folder; no code edits the import path, the runner included, and its imports stand at the top with no `E402` marker.

**R3.** `scripts/check-shared-links.py` holds the links of R1, derived from the folders: a missing link, a copy, a plain file, a dangling, absolute or misdirected link is red. A finding on a link to the module's own package says why in its own words: the runner must import the code the gate runs.

**R4.** `tests/const_gate` points straight at `shared/const_gate`, like the shared test files, and not through `scripts/const_gate`.

**R5.** The gate list's type check of a module's `tests/` runs with no `MYPYPATH`.

## Applied

The commits of this branch apply every item: the first adds the links and edits the 11 runners, the second widens the shared-links check and its self-test, the third changes the documents and the gate list and adds this record. The record is born `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7, and its opening paragraph; [template §6](../../module-template/MODULE.md#t6), rule 1, and the `tests/` line of the section "Plugin skeleton" of the [template](../../module-template/MODULE.md); [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; each module's `MODULE.md`, the row `tests` of its artifacts table, and its `INSTALL.md`, the sentence on copying the plugin's folder. The widening of item 2 of dec-0025-shared-gate-code-linked is history.
2. R2 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 8; [template §6](../../module-template/MODULE.md#t6), rule 1; [the harness](../../shared/tests/harness.py), its docstring.
3. R3 — [check-shared-links](../../scripts/check-shared-links.py), its docstring; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7.
4. R4 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7.
5. R5 — [the gate list](../../scripts/gate-list.sh), its entry `types-<module>`; [pyproject.toml](../../pyproject.toml), its list of commands.
