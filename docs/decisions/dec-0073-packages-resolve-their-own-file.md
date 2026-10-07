---
id: dec-0073-packages-resolve-their-own-file
type: task-record
title: A package reads its own file only through Path.resolve(), held by a kit check
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A package reads its own file only through Path.resolve(), held by a kit check

## Context

Since [dec-0070-runners-import-through-links-in-tests](dec-0070-runners-import-through-links-in-tests.md), a module's fixture runner imports the shared package and the module's own packages through relative links in its `tests/`. Python sets `__file__` of a module imported so to the path through the link, not to the file's own place. A package that derives a path from `__file__` without resolving it finds one place under its fixtures and another in a hook run: `Path(__file__).parent.parent / "lychee.toml"` names `tests/lychee.toml` under the runner and `scripts/lychee.toml` in a hook. A fixture shows the defect only where it reaches that path.

On 2026-10-08 all 13 uses of `__file__` in the module packages read it as `Path(__file__).resolve()`, and the shared code reads it nowhere; no text of the kit asks for that. The point was justified, not fixed, at dec-0070's merge. The decider was asked in chat on 2026-10-08 whether to state it.

## Options

- **A. A clause in the template, held by review.** Rule 1 of [template §6](../../module-template/MODULE.md#t6) says a package reads its own place only as `Path(__file__).resolve()`, and why.
  - **Pros:** the rule stands where module authors read; one sentence; the 13 uses already follow it.
  - **Cons:** a new rule, with a record and its audit; review can miss a case; the template grows while over its ceiling.
- **B. The clause, and a kit check.** As A, and a kit script reads every package a runner imports through a link and turns red on any other use of `__file__`.
  - **Pros:** the rule is held by a gate, not by memory; the check is mechanical, since the allowed form is one shape of the syntax tree.
  - **Cons:** machinery for a failure no consumer has hit, which the guide's "Never in this repository" names; a script, its self-test and a gate-list entry to keep.
- **C. Leave it unstated.**
  - **Pros:** no new rule and no audit.
  - **Cons:** a new module can break it unseen, and a fixture shows it only where it uses the wrong path.

## Recommendation

A, since one sentence closes a real but rare failure and a gate costs more than one unhit failure earns; the session recommended it.

## Choice

The decider chose B in chat on 2026-10-08. The session keeps its objection: the check is machinery for a failure no consumer has hit. It costs little, though, since the allowed form is one exact shape and the check needs no judgment.

## Ruling

**R1.** A package that the fixture runner imports through a link in `tests/` — a module's own package, the shared package, the shared test files — reads its own place only as `Path(__file__).resolve()`, the name `Path` or `pathlib.Path`, and derives every path from that. Any other use of `__file__` is a defect. Entry files and the runner, run by path, are not bound.

**R2.** The kit's `scripts/check-resolved-paths.py`, kit tooling never shipped in a module, holds R1: it reads every `.py` file of each module's own packages, of `shared/const_gate/` and at the top of `shared/tests/`, and turns red, with why and fix, on each use of `__file__` not of that form. It is an entry of the gate list's gate group, in the job `kit`, with its `--self-test` as its fixture.

**R3.** A module's own packages have one derivation in Python, `own_packages` of `scripts/kit_module_doc.py`, which `scripts/check-shared-links.py`, `scripts/check-bare-install.py`, `scripts/check-resolved-paths.py` and `scripts/list-message-literals.py` read; the gate list's entry `types-<module>` derives the same set in shell.

## Applied

The commit that creates this record applies every item: the clause in rule 1 of the template's section 6, the check with its self-test and its entry in the gate list and the routine's list, and the shared derivation. The record is born `inactive`.

## Carry list

1. R1 — [template §6](../../module-template/MODULE.md#t6), rule 1; [the check](../../scripts/check-resolved-paths.py), its docstring.
2. R2 — [the check](../../scripts/check-resolved-paths.py), its docstring; [the gate list](../../scripts/gate-list.sh), its entry `resolved-paths`; [pyproject.toml](../../pyproject.toml), its list of commands; [template §6](../../module-template/MODULE.md#t6), rule 1.
3. R3 — [kit_module_doc](../../scripts/kit_module_doc.py), its docstring and `own_packages`; [the gate list](../../scripts/gate-list.sh), the comment of its entry `types-<module>`.
