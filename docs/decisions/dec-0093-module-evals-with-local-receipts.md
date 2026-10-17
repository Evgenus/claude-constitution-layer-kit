---
id: dec-0093-module-evals-with-local-receipts
type: task-record
title: Every module ships eval cases, run locally on the pinned model, with a receipt CI checks; a load check runs in CI
status: active
stakes: process
decider: Eugene Chernyshov
---

# Every module ships eval cases, run locally on the pinned model, with a receipt CI checks; a load check runs in CI

## Context

On 2026-10-16 the decider asked how the kit makes sure that every tool of a module really works: its skills load, its start rules reach the model and are used, and the commands a rule makes mandatory are run. The kit's checks answered only part of it.

1. Each module's fixtures run its gate and hook scripts directly, on bare temporary repositories. They prove what a script decides, not that Claude Code runs it.
2. `scripts/check-bare-install.py` installs each module through `claude plugin install` and runs every hook of the copy by hand, on a sample event. It starts no session, so it proves neither that the platform registers a hook nor that it loads a skill.
3. `scripts/check-install-guide.py` starts one headless session and reads only the plugins' paths from its `init` event.
4. The `live` items of each module document's acceptance table prove the session behaviour, the "pointer leads to a load" among them. Each was run once by hand and is never run again; some date from Claude Code 2.1.251, and the kit's pin is 2.1.282.

The kit has met the failure these leave open. In its own sessions of 2026-09-26, a rule whose only home was a skill drifted while the skill was not loaded, as the context of [dec-0047-decision-shape-printed-at-session-start](dec-0047-decision-shape-printed-at-session-start.md) tells. Nothing in the repository had changed, and nothing re-ran its one live proof.

Facts that settle the mechanism, from experiments on 2026-10-16 on Claude Code 2.1.282, the pinned version, and from the official documentation read that day:

1. A headless session with no login still runs its `SessionStart` hooks and reports them, with `--include-hook-events`, as `hook_response` events carrying each hook's output. Its `init` event lists the plugin's skills under `skills`. Both come before the model is called, which then fails for want of a login.
2. Claude Code ships `claude plugin eval`, which runs a plugin's eval cases, each a folder holding a `case.yaml` or a `prompt.md` and its graders ([Test plugins with evals](https://code.claude.com/docs/en/plugin-evals.md)). The graders are `regex`, `tool_used`, `tool_order` and `file_exists`, which the page calls deterministic and free, and `llm` and `baseline`, which call a judge. The cases sit below the plugin's folder: `--eval-dir` and the manifest's `experimental.evals` take a folder name there, never an absolute path or one with `..`.
3. Each run starts in an empty temporary folder with its own home and configuration, the plugin alone loaded; no project file loads. A workspace is seeded only by a case's `scaffold_script`, which runs only under `--scaffold`.
4. Runs use the login of the person's normal sessions and count against that plan's limits. One case against a copy of module [`const-styling`](../requirements.md#const-styling), one run, no baseline, on the decider's subscription login and with no API key, scored 1: the model called `Skill` with `style-defaults` before `Write`, in 6 turns and 12 s, at a cost of $0.12 at list price.
5. In a run with a no-plugin baseline, a `tool_used` grader on `Skill` is shown but not scored; under `--ablation none`, or marked `arm: both`, it is scored.
6. The run's result JSON names the Claude Code version, the plugin's name and version, and per case its score and pass rate. It names the model only when one is passed with `--model`, as `suite.modelOverride`.

A change to the kit's checks, its CI and its module documents changes the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9). A model's behaviour can never be a deterministic gate under [law 5 of CLAUDE.md](../../CLAUDE.md#law-5). So the decider was asked, in chat on 2026-10-16, how to enforce it without a credential in CI. The options were a run on the decider's own login with a receipt that CI checks, a subscription token kept as a secret of the repository, or a local hook alone. The decider chose the receipt. Asked then whether the change owes a research comparison, the decider chose none, in chat on 2026-10-16, as the session recommended: the facts above, from the platform's own documentation and two probes, settle every question below. The record answers eight questions, in the order the decider was asked them; the eighth came from the first runs.

## 1. Where the eval cases live

### Options

- **A. In the kit, not shipped.** The cases sit at `evals/<module>/` in the kit; the runner puts them into a copy of the module in the scratch folder.
  - **Pros:** the plugins ship nothing new; the template, the portability check and the coverage map stay as they are; a case may name kit details, since it is kit tooling.
  - **Cons:** a consumer cannot run the cases on their own setup; the runner must build the copy first.
- **B. In each module, shipped.** The cases sit at `modules/<module>/evals/`, the platform's own layout.
  - **Pros:** `claude plugin eval` runs on the module's folder as it is; a consumer can run the same proof in their project.
  - **Cons:** a new component in every plugin, so the template, the portability check, `scripts/check-gate-lists.py` and the coverage map change; the results are written inside the plugin's folder; the guide's rule against machinery for failures no consumer has hit must be answered.

### Recommendation

A, recommended by the session: the smaller change, all of it kit tooling, with a move into the modules left for the day a consumer asks.

### Choice

B, by the decider in chat on 2026-10-16, over the recommendation. The failure that earns the machinery is the kit's own, as consumer zero, told in the context above.

## 2. What the receipt binds, and where it is kept

### Options

In every option the receipt binds a hash of the module's files, the pinned Claude Code version, the model and the run's scores.

- **A. One file per module, in its `evals/` folder, shipped.**
  - **Pros:** the proof sits beside its cases; a consumer sees the version and model the kit's run passed on.
  - **Cons:** each new receipt changes the module's files, so once a module is published every eval run forces a version bump; the plugin carries kit state.
- **B. One file in the kit, not shipped.** One entry per module.
  - **Pros:** a receipt never touches a module, so no version bump and nothing kit-specific ships; one file for CI to read and one diff to review.
  - **Cons:** the proof sits away from its cases; two branches that each renew a different module conflict on the one file.
- **C. A commit trailer**, `Eval-Receipt: <module> <hash> <score>`, on a commit of the branch.
  - **Pros:** no file at all; it follows a receipt the kit already has.
  - **Cons:** CI must find which modules a range changed and the newest trailer of each; a push to `main` has no range to read.

### Recommendation

B, recommended by the session: no version bump on an eval run, and CI stays one comparison of each module's hash against one file.

### Choice

B, by the decider in chat on 2026-10-16.

## 3. Runs per case, and the pass threshold

### Options

- **A. The tool's default: 3 runs, threshold 1.0.** A case passes only when all 3 runs pass.
  - **Pros:** strict and plain; a rule that reaches the model 2 times in 3 is a finding about its wording, fixed at its cause; no number of the kit's own to defend.
  - **Cons:** the model's variance can block a receipt for a rule that mostly works; a receipt alone cannot show the runs before it.
- **B. 3 runs, a case passing at 2 of 3.**
  - **Pros:** one noisy run is absorbed.
  - **Cons:** it accepts a rule that fails one time in three, the drift the evals exist to catch; the kit must defend its 0.67.
- **C. 5 runs, threshold 0.8.**
  - **Pros:** a better estimate of the true rate.
  - **Cons:** five thirds of the cost and time of A on every renewal; it still accepts one failure in five.

### Recommendation

A, recommended by the session, the receipt keeping every attempt so that a review sees a rerun and does not trust it away.

### Choice

A, by the decider in chat on 2026-10-16.

## 4. Which files make a receipt stale

### Options

- **A. Every file of the module** git tracks.
  - **Pros:** the simplest rule and code; nothing slips through a list.
  - **Cons:** an edit to a document or a test that no session loads forces a full rerun.
- **B. What a session loads.** Every tracked file save the module's documents and tests.
  - **Pros:** a receipt goes stale only when something that could change the model's behaviour changed; the most common change, a document's, costs no run.
  - **Cons:** a list to keep current.
- **C. Only what the model reads:** the skills, the hooks file, the manifest and the cases.
  - **Pros:** the fewest reruns.
  - **Cons:** it misses `scripts/`, where the start rules and every block message are written.

### Recommendation

B, recommended by the session, written as what it leaves out, so that a component folder a later module adds counts by default.

### Choice

B, by the decider in chat on 2026-10-16, in the form recommended.

## 5. Which cases each module has, and how they stand in its document

### Options

The first part asked which cases each module must have.

- **A. One case per skill, and one per mandatory command.**
  - **Pros:** all deterministic and cheap; it tests the path the start pointers exist for.
  - **Cons:** module [`const-interaction`](../requirements.md#const-interaction), which has no skill, gets no case, and no start rule that carries a rule of its own is tested.
- **B. As A, and one case per start rule that carries a rule of its own**, graded by `regex` where a pattern can see the rule and by `llm` only where none can.
  - **Pros:** every module gets a case; every kind of rule a module sends to the model is checked at least once.
  - **Cons:** an `llm` grader is paid and votes 2 of 3, which adds variance under the threshold of section 3.
- **C. One case per `live` item of the module's acceptance table.**
  - **Pros:** reviewed scenarios reused.
  - **Cons:** the cases follow history, not the module's parts; some live items prove scans, not sessions.

The second part asked how a case stands in the acceptance table.

- **A. A new kind, `eval`, beside the `live` items.**
  - **Pros:** each case names its rows; the `live` items stay as they are.
  - **Cons:** a `live` item and an `eval` item often prove one thing twice.
- **B. No new kind:** the cases stand outside the table, in the artifacts table alone.
  - **Pros:** the smallest change.
  - **Cons:** nothing ties a case to a row, so a missing or an extra case goes unseen.
- **C. As A, and each `live` item a case covers becomes an `eval` item.**
  - **Pros:** one item per proof; the proofs that had gone stale are run again on every change that could break them.
  - **Cons:** the largest edit, in every module document; a rewritten item's date and version live on in git alone.

### Recommendation

B for the first part and C for the second, recommended by the session: every tool a module has gets a case, and each proof is stated once.

### Choice

B and C, by the decider in chat on 2026-10-16.

## 6. Which model the runs use

### Options

The result names no model unless one is passed, so in every option the runner passes `--model` from one kit file.

- **A. One pinned model, `claude-opus-5-5`**, the model of the kit's own sessions.
  - **Pros:** the rules are proven on the model that works in the kit; a failure points at a rule's wording, not at a smaller model's limits.
  - **Cons:** the costliest model per run; a consumer on a smaller model gets no proof for it.
- **B. One pinned model, `claude-haiku-5-5`**, the smallest.
  - **Pros:** the cheapest and fastest.
  - **Cons:** a miss may come from the model's limits and not the rule's wording; no kit session uses it.
- **C. Both**, every case run on each.
  - **Pros:** the range a consumer may use.
  - **Cons:** twice the runs on every renewal, and the chase of B.

### Recommendation

A, recommended by the session: the receipt shows that a module works where it is used, and today that is the kit, on Opus 5.5.

### Choice

A, by the decider in chat on 2026-10-16.

## 7. The load check

### Options

- **A. A step added to `scripts/check-bare-install.py`.**
  - **Pros:** it reuses the install, the empty configuration and the pin the check already sets up.
  - **Cons:** a longer check, in a script already over 3,000 lines.
- **B. A new kit check of its own**, with its own `--self-test`.
  - **Pros:** a smaller script that fails on its own line.
  - **Cons:** it must install the module again or share that code; one more entry for `scripts/check-gate-lists.py` to hold.
- **C. Not now.**
  - **Pros:** a smaller change.
  - **Cons:** a skill or start rule that breaks only in the installed copy is caught by nothing.

### Recommendation

A, recommended by the session: the new hold is a short step on work CI already pays for.

### Choice

B, by the decider in chat on 2026-10-16, over the recommendation; the cost of a second install stands as the price chosen.

## 8. How the cases that need Bash run on the decider's machine

On 2026-10-17 the first runs showed that `claude plugin eval` 2.1.282 refuses any run that grants `Bash` on a machine whose Docker credential store, `~/.docker`, holds a symbolic link, since its sandbox "cannot reliably exclude" the store. Docker Desktop keeps its own plugin links there, on the decider's machine too. Twelve cases need no `Bash` and lost it; four need it, the three command cases and one that reads the history.

### Options

- **A. An opt-in flag of the runner** that points `DOCKER_CONFIG` at an empty folder for the runs that grant `Bash`, and says so.
  - **Pros:** the four cases run on the decider's machine; nothing there changes; the decider chooses it per run.
  - **Cons:** in those runs the sandbox guards the empty folder, not the real store, so a `Bash` command of the run could read the decider's Docker credentials.
- **B. Run the four cases on another machine** with the decider's login and no Docker Desktop.
  - **Pros:** the safeguard stays whole.
  - **Cons:** a second machine to keep on the pinned Claude Code, for every change that makes those receipts stale.
- **C. Replace Docker Desktop's links** in `cli-plugins/` with copies of their targets.
  - **Pros:** every run works, with the safeguard whole.
  - **Cons:** it edits Docker Desktop's own install, which its updates may break or undo.

### Recommendation

A, recommended by the session: opt-in, limited to the runs asked for, and the commands those runs execute are the kit's own scripts and the cases' scaffolds.

### Choice

A, by the decider in chat on 2026-10-17.

## Ruling

<a id="r1"></a>**R1.** Every module ships its eval cases in `evals/` at its root, one folder per case holding a `case.yaml`, in the form `claude plugin eval` reads. The results a run writes under `evals/results/` are ignored by git and never committed.

<a id="r2"></a>**R2.** A module has one case per skill, which holds by `tool_used` that the model calls `Skill` with the skill's name and by `tool_order` that it does so before the tool the skill's moment names. It has one case per command a rule of the module makes mandatory, which holds by `tool_used` on `Bash` that the command runs; where a skill makes the command mandatory at the skill's own moment, one case holds both, the skill before the command. It has one case per start rule that carries a rule of its own, not a pointer to a skill, graded by `regex` where a pattern can see the rule and by `llm` only where none can. A case that needs files seeds them by its `scaffold_script`.

<a id="r3"></a>**R3.** Every case runs 3 times, the tool's default, which no case overrides. A case passes when every grader passes in every run, the threshold 1.0. The runs take `--ablation none`, so that a grader on `Skill` is scored.

<a id="r4"></a>**R4.** The runs use the model the kit's file `scripts/eval-model` names, passed as `--model`; it names `claude-opus-5-5`.

<a id="r5"></a>**R5.** A module's eval hash is taken over every file git tracks in the module's folder, links followed, save `MODULE.md`, `README.md`, `INSTALL.md`, the folder `tests/` and the folder `evals/results/`.

<a id="r6"></a>**R6.** The receipts stand in one kit file, `scripts/eval-receipts.json`, never shipped, one entry per module. An entry names the module's eval hash, the Claude Code version of `scripts/claude-code.version`, the model of `scripts/eval-model`, and every attempt made for that hash, each with its time and its scores; a later hash starts a new entry.

<a id="r7"></a>**R7.** The kit's `scripts/run-evals.py` runs the evals of one module, or of every module, on the login of the person who runs it. It runs them on a link-followed copy of the module in a temporary folder, on the pinned Claude Code, and writes each attempt into the receipts file. It is kit tooling, never shipped, and no check.

<a id="r8"></a>**R8.** The kit's `scripts/check-eval-receipts.py`, an entry of the gate group with `--self-test` as its fixture, turns red for a module whose entry is missing; whose hash differs from the module's current eval hash; whose version or model differs from the pinned ones; or whose last attempt did not pass. It holds that a passing run was declared for the current files, not that it was run, as the receipt of [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5) does for an audit.

<a id="r9"></a>**R9.** A module document's acceptance table gains the kind `eval`: one item per case, naming the rows it proves, its status derived by `scripts/check-aspects.py` from the receipt. Each `live` item that a case covers becomes an `eval` item. A `live` item that proves a scan over the kit's tree, and a deferred consumer-live item, stay `live`.

<a id="r10"></a>**R10.** The kit's `scripts/check-session-load.py`, an entry of the gate group in each module's job with `--self-test` as its fixture, installs the module as `scripts/check-bare-install.py` does, the shared steps in one place. It then starts one headless session with no login in the bare repository and holds two things. The `init` event lists every skill under the module's `skills/`. Every `SessionStart` hook of the module has a `hook_response` with exit 0 and output that is not empty.

<a id="r11"></a>**R11.** A change that makes a module's receipt stale is merged only with a new passing receipt, made by a local run before the merge; this narrows the guide's "No local run is required" to the gate list.

<a id="r12"></a>**R12.** A case grants `Bash` only where it needs it, and the runner grants the eval only the tools of `Bash`, `Write` and `Edit` that a module's cases list. With its flag `--docker-config-empty`, and only then, the runner points `DOCKER_CONFIG` at an empty folder for the runs of a module whose cases grant `Bash`, and prints a note saying so.

## Carry list

1. R1 — the eval case row of [template §6](../../module-template/MODULE.md#t6); [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [the kit's ignore file](../../.gitignore).
2. R2 — the eval case row of [template §6](../../module-template/MODULE.md#t6); [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
3. R3 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
4. R4 — [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstring of `eval_model`; [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring.
5. R5 — [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstring of `eval_files`.
6. R6 — [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstring of the receipts file.
7. R7 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring.
8. R8 — [`scripts/check-eval-receipts.py`](../../scripts/check-eval-receipts.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
9. R9 — [template §10](../../module-template/MODULE.md#t10); [rule 8 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r8); [`scripts/check-aspects.py`](../../scripts/check-aspects.py), its docstring. Which live items became eval items is history.
10. R10 — [`scripts/check-session-load.py`](../../scripts/check-session-load.py), its docstring; [`scripts/kit_install.py`](../../scripts/kit_install.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
11. R11 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
12. R12 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring.
