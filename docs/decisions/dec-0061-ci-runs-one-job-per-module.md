---
id: dec-0061-ci-runs-one-job-per-module
type: task-record
title: CI runs one job per module and one job kit, each holding its entries of the list, every red entry named in an annotation
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# CI runs one job per module and one job kit, each holding its entries of the list, every red entry named in an annotation

## Context

R1 of [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md#r1) made every entry of the kit's list its own CI job, and R3 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r3) added one install job per module. By 2026-10-01 a run had 47 jobs: the list job, 45 entries and `gates`. In the run of the merge "Work: in-place-proof" most jobs spent about 10 s on setup and 0 to 2 s on their check; the module fixtures took 12 to 42 s each, and `types` 32 s. GitHub rounds each job up to a whole minute, as the [runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing) dec-0058 cites says, so one run was billed about 47 minutes, and a change, run on its pull request and on `main`, about 94. The decider found the checks too many on the pull request and asked how to group them. The two questions below were put in chat, one per message, each with lettered options; the pick was the letter.

## 1. How the entries are grouped

- **A. Five groups by kind: module scans, kit checks, installs, fixtures, lint and types.**
  - **Pros:** about 11 billed minutes per run; only the install job sets up Node and Claude Code; simple serial code.
  - **Cons:** a run takes about 5 minutes, the fixtures running one after another; a red shows its group on the check line and its entry only in the annotation.
- **B. The same five groups, the fixtures run four at a time inside their job.**
  - **Pros:** about 1.5 minutes per run and about 8 billed minutes.
  - **Cons:** parallel shell code with each entry's output held back, in a script with no fixture of its own.
- **C. Two jobs: the list's gate group and its extra group.**
  - **Pros:** no new grouping, the split exists already; the fewest jobs.
  - **Cons:** the gate job installs everything; a red names only "gate" or "extra"; about 5 minutes per run.
- **D. One job per module, holding its scan, fixtures and install, and one job for the kit.**
  - **Pros:** a red check line names the plugin a consumer installs, the unit the kit versions; each job is the module alone, as [law 3 of CLAUDE.md](../../CLAUDE.md#law-3) asks a module to stand; about 1.5 minutes per run, the slow fixtures spread over eleven jobs.
  - **Cons:** 14 jobs and about 15 billed minutes, one more job with each new module; every module job installs Node and Claude Code; a whole-tree scan's red lands on a module's line; more code to change than A.

The session first recommended A, for the fewest billed minutes with the simplest code. Asked to discuss D in depth, it recommended D: for about four more billed minutes per run, D brings the wait from about 5 minutes to about 1.5, and a red names a module. D, chosen by the decider in chat on 2026-10-01.

<a id="r1"></a>**R1.** `.github/workflows/gates.yml` runs one job per module and one job `kit`, in parallel, none cancelled by another's red. A module's job holds every entry of that module: its scan where it declares one, its install, its fixtures, its lint and its types. `kit` holds every other entry. This reverses R1 of [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md#r1), one job per entry, and narrows R3 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r3) and the job named in R1 of [dec-0060-ci-installs-from-the-github-remote](dec-0060-ci-installs-from-the-github-remote.md#r1): each module's install is now an entry of the module's own job, as [requirement A12.1](../requirements.md#a12-1) says, no longer a job of its own.

<a id="r2"></a>**R2.** The jobs are written once, in `scripts/gate-list.sh`, and read from the entries: each entry is mapped to exactly one job, and an entry no line maps falls into `kit`, so none is left out of CI. `--json` prints the jobs; `--names <job>` lists a job's entries; `--run <job>` runs every entry of the job in turn, after a red one too, and exits as `--run <entry>` does, 0 when every command did, else 2 when every failing command exited 2, else 1. An entry with no commands is a BROKEN line and exit 1, never a pass. This narrows R2 of [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md#r2), where `--json` printed the entries and each job ran one.

<a id="r3"></a>**R3.** A job's run in GitHub Actions folds each entry's log under the entry's name, writes for each entry that did not exit 0 an error annotation naming the entry and the command that reruns it alone, and writes one line per entry with its exit to the job's summary.

<a id="r4"></a>**R4.** Lint and types are split like the rest: each module has its own entries `lint-<module>` and `types-<module>` in the extra group, the kit's own `lint` covers `scripts/` and `shared/`, and its `types` the kit's checks under `scripts/` and the shared package `shared/const_gate`, the shared tests being typed through each module's links.

<a id="r5"></a>**R5.** Every module's job installs Node 22 and Claude Code, pinned as R3 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r3) says, for its install entry. The job's run carries the token and the install source that entry needs, for every entry of the job, though only the install reads the source; the job `kit` installs neither and carries neither, its install self-test needing no `claude`.

<a id="r6"></a>**R6.** Every job runs on every run. None is skipped for the paths a change touched: the scans read the whole tree or, for the range check, the change's whole range, and the shared gate code sits in every module.

<a id="r7"></a>**R7.** The job `gates` stays the one check the ruleset requires, green only when every other job is, so the ruleset does not change.

## 2. Where the whole-tree scans run

- **A. Each scan stays in its module's job.**
  - **Pros:** a module's job holds everything the module declares, the pairing `scripts/check-gate-lists.py` already holds; a red names whose rule the tree broke.
  - **Cons:** a broken link in a document turns a module's line red though its code is fine; the annotation must tell the two apart.
- **B. Every scan moves to the job `kit`.**
  - **Pros:** a red module line always means the module's code.
  - **Cons:** `kit` grows to about 20 entries and its red names no module; it must install Vale and lychee too; the scan map is still needed.

The session recommended A: a scan is a module's rule applied to the tree, so its red belongs on that module's line. A, chosen by the decider in chat on 2026-10-01.

<a id="r8"></a>**R8.** A module's scan runs in that module's job. A red scan on a module's line means the tree, or for the range check the change, breaks that module's rule, not that the module's code is broken; the annotation of R3 names the scan's entry.

## Applied

The change that adds this record applies every item, in the commit before the record's, the record's own and the fix rounds of its carry audit. So the record is born `inactive`.

## Carry list

1. R1 — [the workflow](../../.github/workflows/gates.yml); [the list script](../../scripts/gate-list.sh); the rule "Work starts on a branch" in [CLAUDE.md](../guide/gate-list-and-ci.md); [requirement A12.1](../requirements.md#a12-1). The reversal of dec-0058's R1 and the narrowing of dec-0059's R3 and of dec-0060's R1 are history.
2. R2 — [the list script](../../scripts/gate-list.sh), its header; [the gate-list check](../../scripts/check-gate-lists.py), its docstring and its fix line. The narrowing of dec-0058's R2 is history.
3. R3 — [the list script](../../scripts/gate-list.sh), its header and its `--run`.
4. R4 — [the list script](../../scripts/gate-list.sh), its header and its commands; the rule "Work starts on a branch" in [CLAUDE.md](../guide/gate-list-and-ci.md), the extra group's sentence.
5. R5 — [the workflow](../../.github/workflows/gates.yml), its install steps and their comment.
6. R6 — [the workflow](../../.github/workflows/gates.yml), its header.
7. R7 — [the workflow](../../.github/workflows/gates.yml); the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md), the ruleset's sentence.
8. R8 — [the list script](../../scripts/gate-list.sh), its job mapping and its header.
