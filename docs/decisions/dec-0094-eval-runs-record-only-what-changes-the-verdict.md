---
id: dec-0094-eval-runs-record-only-what-changes-the-verdict
type: task-record
title: An eval run records an attempt only when it changes what the receipt says
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# An eval run records an attempt only when it changes what the receipt says

## Context

On 2026-10-18 the decider asked why every eval run is recorded in `scripts/eval-receipts.json` and committed, since that makes many commits and a file that keeps growing.

The facts, from the kit's texts that day:

1. R6 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r6) has a module's entry name "every attempt made for that hash", failures included, and has a later hash start a new entry. So the file does not grow without bound: a module's entry holds the attempts made since its files, the Claude Code pin or the model last changed.
2. The kit sees no eval run; a receipt is a run declared. The guide's bullet "The gate list and CI" in [CLAUDE.md](../guide/gate-list-and-ci.md) keeps the failed attempts beside the passing one, so that a review sees each rerun and does not trust it away.
3. A new passing receipt is owed before the merge of a change that makes a receipt stale (R11 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r11)). A rerun of a module whose receipt is current owes nothing. Yet `scripts/run-evals.py` recorded every run, so such a rerun dirtied the tree, and the turn-end hook of module [`const-task-close`](../requirements.md#const-task-close) then asked for a commit. On 2026-10-17, by UTC, an optional run of every module and two single-module runs added passing attempts to current, passing receipts, each with commits of its own.

## Options

- **A. Record only what changes the verdict.** The runner records an attempt when the receipt is missing or stale, when its last attempt failed, or when this run fails; a passing rerun of a current, passing receipt is printed and not recorded.
  - **Pros:** a run made to watch leaves the tree clean, so it owes no commit; a failure is still recorded, which turns the receipt red and shows a flaky case; an entry holds one passing attempt per hash, plus any failures and the pass that followed them.
  - **Cons:** repeated passes leave no trace, so the file no longer shows how many times a case has passed.
- **B. A flag for runs that record nothing.** Runs made to watch, a `--no-record` flag and a recipe of their own, record nothing; every other run records as before.
  - **Pros:** explicit; nothing changes for the runs that record.
  - **Cons:** a failure seen in a run that records nothing leaves no trace; it rests on choosing the right recipe; the runs that record still pile up attempts.
- **C. Keep it as it is.** Every attempt is recorded, and the person commits or discards an optional rerun's attempts.
  - **Pros:** no change; the fullest record.
  - **Cons:** a dirty file and the hook's request after every optional run; discarding attempts by hand quietly defeats R6 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r6).

## Recommendation

A, recommended by the session: it keeps what R6 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r6) is for, that no failure goes unrecorded, and drops only the passes that add nothing; unlike B, a flaky failure seen while watching still turns the receipt red.

## Choice

A, by the decider in chat on 2026-10-18.

## Ruling

<a id="r1"></a>**R1.** `scripts/run-evals.py` records a run's attempt in the module's entry unless the entry names the run's eval hash, Claude Code version and model, the entry's last attempt passed, and the run passed too; then it records nothing, and its verdict line says that the receipt stands. So an entry holds the attempts that changed its verdict: the first one for its hash, Claude Code version and model, every failure since, and each pass that follows a failure; a run on another hash, version or model starts a new entry, as before. An attempt the runner records is committed, a failure as much as a pass, so that the receipt CI reads turns red when a case fails. This narrows R6 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r6), "every attempt made for that hash", and R7 of [dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md#r7), "writes each attempt into the receipts file", to those attempts; the rest of those rulings stands.

## Carry list

1. R1 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring, `recorded` and the verdict line of `main`; [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstring of the receipts file; [CLAUDE.md](../guide/gate-list-and-ci.md), the bullet "The gate list and CI"; [the justfile](../../justfile), its recipe `evals`. That it narrows R6 and R7 of dec-0093-module-evals-with-local-receipts is history.
