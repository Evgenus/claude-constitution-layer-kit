---
id: dec-0056-portability-grep-and-gate-lists
type: task-record
title: The portability grep forbids what can name a place in a project and runs as scripts/check-portability.py; scripts/check-gate-lists.py holds every declared module scan in the gate list and the CI list
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The portability grep forbids what can name a place in a project and runs as scripts/check-portability.py; scripts/check-gate-lists.py holds every declared module scan in the gate list and the CI list

## Context

The promise audit of [dec-0055-promise-audit-fixes](dec-0055-promise-audit-fixes.md) left two kit checks to a change of their own, held pending in step 10 of the rollout plan: the grep of [requirement A12.1](../requirements.md#a12-1) as a kit script, its design settling what the grep as worded finds in the modules today (F8 there), and a check that every module's scan stands in the gate list and in the CI list, the gap F5 and F6 there showed. The questions below were put in chat on 2026-09-30, one per message, and the pick was the letter.

## 1. What the grep forbids

The row's grep read: in every file of a module, any absolute path, link with the `file` scheme, `~/`, or repository-relative path literal not prefixed by `${CLAUDE_PLUGIN_ROOT}` and not a public URL is a finding, with no exemption marker. Run as worded, it found no project reference and hit paths inside the plugin, example dial values in install notes and skills, and the module documents' links to kit documents, which [rule 3 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r3) already took out.

- **A. Amend the row: installed components only; a path of the plugin itself and a fenced example allowed; everything else a finding.**
  - **Pros:** red only on what the row is for; no module changes; the exceptions structural.
  - **Cons:** the row's rule changes; a real project path inside an example block passes.
- **B. Change the modules to meet the row as worded.**
  - **Pros:** the row unchanged, the strictest reading.
  - **Cons:** edits across eleven modules, their messages and fixtures; placeholders make install notes harder to use.
- **C. A report, never red.**
  - **Pros:** no row or module change.
  - **Cons:** a list of known hits read on every run hides a new real one.

The session recommended A, and the decider chose A. A prototype of A then left 74 hits, none a project reference: interpreter lines, the reference module's own detection patterns, example paths in inline code, words with a slash. The session put the rule again:

- **A. Refined: only what can name a place in a project.** In the installed components and the shared code, a path under a home directory, `~/`, a link with the `file` scheme, or a relative path with a slash and a file extension or a glob that is no file of the plugin and not `constitution.yaml`; Markdown code, inline and fenced, an example; no marker; the reference module's four hits reworded.
  - **Pros:** measured: no false red after the rewording; each exception structural.
  - **Cons:** system paths and relative paths with neither extension nor glob are no longer findings.
- **B. A as first described.**
  - **Pros:** closest to the row's words.
  - **Cons:** 74 hits, none real; about twenty files to edit before it can be a gate.
- **C. A report.**
  - **Pros:** no row change.
  - **Cons:** the same noise, never red.

The session recommended A, the only form the prototype showed could be a gate. **R1.** A refined, chosen by the decider in chat on 2026-09-30: the grep of [requirement A12.1](../requirements.md#a12-1) reads the installed components of a module — its skills, hooks, scripts, commands, agents, install note and manifest, never its document or its tests — and the shared gate code it installs. There, a path under a home directory — `/Users/`, `/home/`, `~/`, `$HOME`, a Windows user folder — a link with the `file` scheme, or a relative path with a slash that has a file extension or a glob and is no file or directory of the plugin is a finding, outside a public URL and outside Markdown code; an interpreter line is read as any other, and a glob whose folder parts are all wildcards names no particular folder and is none. There is no exemption marker, and `constitution.yaml` is the one repository path a module may name. What the grep does not see — a folder named with neither an extension nor a glob, a system path, a home path in a form not listed — is held by review, and by the bare-repository run on defaults, the gate of record, only where the path acts on a bare repository. The row is amended under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2), its rule having changed.

The session's first script also skipped a file's interpreter line; a mutation probe showed that exception guarded nothing under these forms and would hide a home path written there, so the script reads the interpreter line as any other — one exception fewer than the session's first script had, the rule stricter. The carry audit then widened the home forms to `$HOME` and a Windows user folder, which the row's "a path under a home directory" already meant. It also found the one clause of R1 the decider did not pick: a glob whose folder parts are all wildcards, such as the skill field `paths: "**/*.md"`, names no particular folder, so it is no finding, while `**/docs/decisions/*.md` names a folder and is one. The session puts that clause to the decider by name with its request for the yes.

## 2. Where the check learns a module's scans

- **A. From each module document's enforcement section: a code span in a row of it that reads exactly `<entry> --scan`.**
  - **Pros:** the module's own current-state declaration; one exact form; ten modules declare one today, matching the gate list one to one.
  - **Cons:** a scan written in another form there is missed; the plan's prose is parsed for the CI half.
- **B. From the scripts, run in a scratch repository.**
  - **Pros:** trusts no document.
  - **Cons:** slow; an explain mode taking `--scan` must be told apart by its output.
- **C. From a list declared in `constitution.yaml`.**
  - **Pros:** explicit.
  - **Cons:** a third list that can drift like the two it checks.

The session recommended A. **R2.** A, chosen by the decider in chat on 2026-09-30: a module's scan is a code span in a row of its enforcement section that reads exactly `<entry> --scan` or `<entry>.py --scan`, nothing after the flag; the check is red when the gate list, before its on-request item, runs no `modules/<module>/scripts/<entry>.sh --scan` or `….py --scan`, and when the CI list of rollout step 10 does not link the module's specification.

## 3. The scripts' names

- **A. `scripts/check-portability.py` and `scripts/check-gate-lists.py`.**
  - **Pros:** each names its subject in the kit's words, as `check-aspects.py` does.
  - **Cons:** "portability" is broader than the grep.
- **B. `scripts/check-project-references.py` and `scripts/check-gate-lists.py`.**
  - **Pros:** claims no more than it does.
  - **Cons:** long, and not the kit's word.
- **C. One script for both.**
  - **Pros:** one line in the gate list.
  - **Cons:** two concerns behind one exit.

The session recommended A. **R3.** A, chosen by the decider in chat on 2026-09-30: `scripts/check-portability.py` and `scripts/check-gate-lists.py`, kit tooling never shipped in a module, each a line of the gate list, a plain run the gate and `--self-test` its fixture.

**R4.** Both run in the kit's CI with the other kit checks once CI is wired.

## 4. What this record narrows

**R5.** R1 narrows the grep ruled in section 6 of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md), its choice C: from every file of a module to the installed components; from any absolute path to a path under a home directory; from any relative path not written `${CLAUDE_PLUGIN_ROOT}`-relative to one with an extension or a glob that is no file or directory of the plugin, save a glob whose folder parts are all wildcards; with Markdown code an example. The rest of that ruling stands — no exemption marker, `constitution.yaml` the one repository path, the grep a heuristic, the bare-repository run the gate of record. That record is not touched ([rule 13 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r13)). Its reasoning that such a run cannot catch a path which acts only where it exists holds: that path is review's.

## Applied

The change adds the two scripts, the lines of the gate list and of the routine in `pyproject.toml`, amends the row of [requirement A12.1](../requirements.md#a12-1), names both in steps 5 and "Work starts on a branch" of [CLAUDE.md](../../CLAUDE.md), and marks the two checks done in step 10 of the rollout plan. In module [`const-referencing`](../requirements.md#const-referencing) the comment and regex of the lint's one-machine pattern are respelled so the module names no such path itself; the regex matches what it matched. The record is born `inactive`.

## Carry list

1. R1 — [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [the script](../../scripts/check-portability.py), its docstring; step 5 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md).
2. R2 — [the script](../../scripts/check-gate-lists.py), its docstring; the bullet "Work starts on a branch" of [CLAUDE.md](../../CLAUDE.md); [template §9](../../module-template/MODULE.md#t9), the form of a declared scan.
3. R3 — both scripts; the routine list of [pyproject.toml](../../pyproject.toml); [CLAUDE.md](../../CLAUDE.md), the two places above.
4. R4 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the CI wiring.
5. R5 — history only: the act of narrowing; the narrowed rule itself is R1's, carried in the row of [requirement A12.1](../requirements.md#a12-1).
