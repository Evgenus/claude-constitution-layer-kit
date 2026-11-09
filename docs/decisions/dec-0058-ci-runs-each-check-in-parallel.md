---
id: dec-0058-ci-runs-each-check-in-parallel
type: task-record
title: CI runs every entry of the kit's one list as its own job in parallel, one required check gates holds the merge, and the local gate-list runs become optional
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# CI runs every entry of the kit's one list as its own job in parallel, one required check gates holds the merge, and the local gate-list runs become optional

## Context

After [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md) gave the kit a PR flow on 2026-09-30, the decider asked for CI. [Rollout step 10](../rollout-plan.md#s10) planned CI for the gate list and more. The gate list was written out twice: as the numbered list of the `gate-list-runner` agent and as the CI sentence of step 10, which `scripts/check-gate-lists.py` read. Every gate ran by hand, through the agent, before a commit that touches a document, before a merge and on `main` after it, and several texts said a check runs by hand "until the kit's CI runs it". GitHub's [runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing) says it "rounds the minutes and partial minutes each job uses up to the nearest whole minute", and GitHub Pro includes 3,000 minutes a month for private repositories. The two questions below were put in chat, one per message, each with lettered options; the pick was the letter.

## 1. How CI runs the checks

- **A. One job runs the whole list.**
  - **Pros:** the tools are installed once; few minutes billed; one required check.
  - **Cons:** a red shows as one check, and its log names the gate; slower than parallel.
- **B. One job per check, in parallel.**
  - **Pros:** each check is its own line on the pull request; the wait is the slowest check.
  - **Cons:** the tools are installed once per job; each job is billed at least a minute; many checks to require; a second copy of the list.
- **C. A few grouped jobs in parallel.**
  - **Pros:** a red points to its group; a few minutes billed.
  - **Cons:** more setup than A.

The session recommended A. <a id="r1"></a>**R1.** B, chosen by the decider in chat on 2026-09-30, for visibility and speed, the tools to install being few: `.github/workflows/gates.yml` runs every entry of the kit's list as its own job, in parallel, none cancelled by another's red, each a check of its own on the pull request.

<a id="r2"></a>**R2.** The session answered B's cons without leaving B. The list is written once, in `scripts/gate-list.sh`: its gate group is the gate list, and its extra group holds the branch gate's fixture, each module's fixture runner, the lint and the types. A first job reads `--json` and the matrix is built from it; each job runs `--run <entry>`; the `gate-list-runner` agent runs the same entries locally.

<a id="r3"></a>**R3.** One job, `gates`, waits for every other and is green only when every other is. It is the one check the ruleset requires on `main`, so a new entry never changes the ruleset.

<a id="r4"></a>**R4.** Every kit check's entry runs its `--self-test` after its plain run where it has one, and `scripts/check-schema-mirror.py`, the kit check the kernel policy names for the mirror of the dials schema, is an entry of the gate group.

<a id="r5"></a>**R5.** The workflow runs on every pull request and on every push to `main`, with the whole history fetched, since the carry-lists and range checks read it. Each job installs pinned versions: Python 3.12, PyYAML 6.0.2, ruff 0.16.8, mypy 1.8.0 with the type stubs of PyYAML and jsonschema, jsonschema 4.26.0, referencing 0.37.0, Vale 3.23.0 and lychee 0.24.2. On a pull request a newer push cancels the run still going; on `main` each merge has a run of its own, never cancelled or replaced by the next merge's, so every merge gets its range check.

<a id="r6"></a>**R6.** `scripts/check-gate-lists.py` reads the gate list from `sh scripts/gate-list.sh --names gate` and `--show`, and holds the CI list as that script, when the workflow builds its jobs from `--json` and runs them with `--run`. The workflow's comments, whole lines or trailing, do not count. That the matrix is built from the one and runs the other is the workflow's own text, held by review and by its run. This replaces where R2 of [dec-0056-portability-grep-and-gate-lists](dec-0056-portability-grep-and-gate-lists.md#r2) read the two lists: the agent's numbered list and the CI sentence of rollout step 10.

## 2. What happens to the local runs

- **A. CI takes the runs before and after the merge; the run before a document commit stays.**
  - **Pros:** a red is still caught before a push.
  - **Cons:** minutes of session time per commit; the "until CI runs it" texts need rewording.
- **B. CI takes all three; the local run becomes optional.**
  - **Pros:** what the "until the kit's CI runs it" texts already said; faster sessions; a required check holds the merge, where the local run was a convention; the write-time hooks still catch most findings.
  - **Cons:** a red the hooks miss is seen only after a push; fix rounds cost CI minutes.
- **C. Keep all local runs and add CI.**
  - **Pros:** the strictest.
  - **Cons:** every check runs twice; the "until" texts must lose their condition.

The session recommended B. <a id="r7"></a>**R7.** B, chosen by the decider in chat on 2026-09-30: CI takes the runs before the merge and on `main` after it, and no local run of the gate list is required. The `gate-list-runner` agent runs its gate group locally, and its extra group on request, when a red is wanted before a push.

<a id="r8"></a>**R8.** The texts that said a check runs by hand "until the kit's CI runs it" now say CI runs it: the dials-file style check, the references scan, the module-links check and the portability grep of step 5 in [CLAUDE.md](../../CLAUDE.md), the dials-file style check in the header comment of `constitution.yaml` too, the reference-forms cell of [requirement A5.6](../requirements.md#a5-6), and the project-reference grep among the [aspect A12](../requirements.md#a12) gates of [the intent page](../../INTENT.md).

<a id="r9"></a>**R9.** Not wired by this record, and left to rollout step 10: the bare-repo install and the kernel-plus-one-module run of [aspect A12](../requirements.md#a12), and the validation of the kit's `constitution.yaml` against the kernel's dials schema by a real validator.

<a id="r10"></a>**R10.** Items other records left pending on CI are now real: R4 of [dec-0056-portability-grep-and-gate-lists](dec-0056-portability-grep-and-gate-lists.md#r4), R8 of [dec-0055-promise-audit-fixes](dec-0055-promise-audit-fixes.md#r8), R8 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r8), R3 of [dec-0049-module-links-held-by-a-kit-check](dec-0049-module-links-held-by-a-kit-check.md#r3), the CI half of R2 of [dec-0037-dials-file-block-style](dec-0037-dials-file-block-style.md#r2), and the whole history R11 of [dec-0030-carry-audit-mandatory](dec-0030-carry-audit-mandatory.md#r11) asks CI to fetch.

<a id="r11"></a>**R11.** R7 ends the local runs two accepted records set: the run of the dials-file style check before every commit that touches the file, R2 of [dec-0037-dials-file-block-style](dec-0037-dials-file-block-style.md#r2), whose condition, until the kit's CI runs it, is now met; and the run of the module-links check before every commit that touches a document, R2 of [dec-0049-module-links-held-by-a-kit-check](dec-0049-module-links-held-by-a-kit-check.md#r2), whose hand run had that condition and whose timing R7 reverses.

## Applied

The change that adds this record applies every item that binds: the script, the workflow, the check and the agent in the commit before the record's, the rest in the record's own. The ruleset's required check `gates` is set before this change is merged, so that its own merge already needs `gates` green; an open pull request cut from `main` before this merge gets the check with its next push, since its merge ref takes the workflow from `main`. So the record is born `inactive`.

## Carry list

1. R1, R5 — [the workflow](../../.github/workflows/gates.yml); the rule "Work starts on a branch" in [CLAUDE.md](../guide/gate-list-and-ci.md).
2. R2, R4 — [the list script](../../scripts/gate-list.sh); [the workflow](../../.github/workflows/gates.yml); the rule "Work starts on a branch" in [CLAUDE.md](../guide/gate-list-and-ci.md).
3. R3 — [the workflow](../../.github/workflows/gates.yml); the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md), the ruleset's sentence.
4. R6 — [the gate-list check](../../scripts/check-gate-lists.py); the rule "Work starts on a branch" in [CLAUDE.md](../guide/gate-list-and-ci.md); the narrowing of dec-0056's R2 is history.
5. R7 — the rule "Work starts on a branch" in [CLAUDE.md](../guide/gate-list-and-ci.md).
6. R8 — [CLAUDE.md](../../CLAUDE.md), the reading-list item on `constitution.yaml`, the rule "References are clickable; handles are scoped" and step 5 of "Developing a module"; [requirement A5.6](../requirements.md#a5-6); [the intent page](../../INTENT.md); the header comment of [constitution.yaml](../../constitution.yaml).
7. R9 — pending: [rollout step 10](../rollout-plan.md#s10).
8. R10 — history only: the items are stated where their own records carry them, and CI now runs them.
9. R11 — history only: the local runs end, as R7 states in the rule "Work starts on a branch" of [CLAUDE.md](../guide/gate-list-and-ci.md).
