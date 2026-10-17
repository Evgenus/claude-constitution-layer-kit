---
id: dec-0093-module-evals-with-local-receipts
type: task-record
title: Every module ships eval cases, run locally on the pinned model, with a receipt CI checks; a load check runs in CI
status: inactive
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

A change to the kit's checks, its CI and its module documents changes the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9). A model's behaviour can never be a deterministic gate under [law 5 of CLAUDE.md](../../CLAUDE.md#law-5). So the decider was asked, in chat on 2026-10-16, how to enforce it without a credential in CI. The options were a run on the decider's own login with a receipt that CI checks, a subscription token kept as a secret of the repository, or a local hook alone. The decider chose the receipt. Asked then whether the change owes a research comparison, the decider chose none, in chat on 2026-10-16, as the session recommended: the facts above, from the platform's own documentation and two probes, settle questions 1 to 7 below. The record answers twelve questions, in the order the decider was asked them; questions 8 to 11 came from the first runs, and question 12 from a case that failed and the carry audit that followed.

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

On 2026-10-17 the first runs showed that `claude plugin eval` 2.1.282 refuses any run that grants `Bash` on a machine whose Docker credential store, `~/.docker`, holds a symbolic link, since its sandbox "cannot reliably exclude" the store. Docker Desktop keeps its own plugin links there, on the decider's machine too. Twelve cases need no `Bash`: eight of them lost it, and four never had it, the three start-rule cases and `ask-or-decide`; four need it, the three command cases and one that reads the history.

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

A, by the decider in chat on 2026-10-17. Tried that day, A did not work: the eval checks `~/.docker` itself as well as the folder `DOCKER_CONFIG` names, and refused the runs as before. The flag was removed in the same change. The same runs showed that one case's `Bash` grant refuses every case of a module run as a whole. So the runner now runs each case on its own.

The decider then chose C in chat: the session moved the plugin links out of `~/.docker` and pointed Docker at the app's own folder by its documented key `cliPluginsExtraDirs`. The eval still refused, for 16 more links in `~/.docker/bin/lib/`, and the session undid both edits. The decider then chose B, a cloud session. It never started, and its request was withdrawn once question 9 was answered.

## 9. How a case that needs Bash is isolated

The cases that need `Bash` prove what a module's rules make mandatory, so they cannot lose it; and a run with `Bash` needs a sandbox that keeps the person's secrets out of reach. The decider set one more rule that day: no run is billed by usage, never an API key.

### Options

- **A. A narrowed grant**, `Bash(sh *<script>*)`, so the model may run the module's own scripts alone.
  - **Pros:** it would run on the decider's machine with the least power given.
  - **Cons:** unverified whether the eval counts a narrowed grant as a `Bash` grant.
- **B. A throwaway container** holding nothing secret, logged in with a subscription token from `claude setup-token`.
  - **Pros:** even a gap in the eval's sandbox finds no secret to read; the token bills the plan, not usage.
  - **Cons:** unverified whether the token reaches the eval's runs; Docker is needed; the token is a long-lived credential of the decider's, kept in a file.
- **C. A cloud session** of the repository.
  - **Pros:** clean infrastructure.
  - **Cons:** nothing tells the session that asked when it ends; every stale receipt of those modules needs another.
- **D. CI with a token.**
  - **Pros:** the most reliable sandbox, each runner thrown away.
  - **Cons:** a long-lived credential of the decider's account kept on GitHub, which section 2 turned away from.

### Recommendation

A first, since a refusal costs nothing, then B, recommended by the session.

### Choice

The decider chose to probe A, in chat on 2026-10-17: the eval refused a narrowed grant as it refuses a full one. The decider then chose to probe B. In a container of the official `node:22-bookworm` image, logged in with a token the decider made with `claude setup-token`, Claude Code reported `oauth_token` on `firstParty`, a subscription login. The case `move-document` passed every grader. The decider then chose B as a mode of the runner, that day.

## 10. Where the evals run

After question 9, seven modules had receipts made on the decider's Mac and four made in the container, and the receipt does not say which. The decider asked, in chat on 2026-10-17, what running every module in the container would change.

### Options

- **A. The container for every module, the host mode removed.**
  - **Pros:** one environment and full isolation for every receipt; one rule to remember, for every machine.
  - **Cons:** no eval run without Docker and a subscription token in a file; the seven host-made receipts made again; a change to the record before its yes, with one more audit round.
- **B. The container as the default, the host mode kept behind a flag.**
  - **Pros:** the same default; a machine without Docker can still run.
  - **Cons:** two modes to keep working and tested; receipts may again come from different environments.
- **C. As it was:** the host by default, the container where `Bash` needs it.
  - **Pros:** no change; the pull request merges as audited.
  - **Cons:** receipts from two environments; a rule that depends on the machine.

### Recommendation

A, recommended by the session: the decider already had Docker and the token file, one environment makes a receipt mean the same every time, and every case gets the container's isolation.

### Choice

A, by the decider in chat on 2026-10-17. With every case in the container, the reason section 8 gave for taking `Bash` from eight cases was gone, and two of them failed there for want of the command their skill names; so R12 gives every skill or command case the tools a session at its moment would have.

## 11. How a case's Bash runs in the container

The traces the runner kept showed that, under Docker's default settings, every `Bash` command of a case failed before it ran: the eval's own sandbox, bwrap, could not create its namespace. The command cases had passed only because their grader counted the call, not what it did. Probes on 2026-10-17 showed bwrap starts with Docker's seccomp filter and its `/proc` mask lifted, and with nothing less.

### Options

- **A. Lift the seccomp filter and the `/proc` mask of each case's container,** and grade each command case by what its command did.
  - **Pros:** commands run, under the eval's own sandbox, in a container that holds nothing of the decider's but the token; the command proofs become real.
  - **Cons:** the container's own system-call filter is off and `/proc` unmasked, so a process in it reaches more of the kernel of Docker Desktop's Linux machine, which still separates it from the host.
- **B. Keep Docker's defaults, and drop the command proofs** to `live` items run by hand.
  - **Pros:** the container keeps Docker's default hardening.
  - **Cons:** the mandatory commands lose their repeatable proof; a skill whose procedure needs a command is tested without it.
- **C. As it was,** a counted call the proof.
  - **Pros:** no change.
  - **Cons:** receipts that claim proofs which never ran.

### Recommendation

A, recommended by the session: the container exists to keep the decider's files and credentials out of reach, which A keeps; what it turns off is an inner layer of Docker's hardening, in exchange for the eval's own sandbox, the layer made for exactly this.

### Choice

A, by the decider in chat on 2026-10-17. Every module's receipt is made again after it, since no `Bash` command of an earlier container run had run.

## 12. The moment of rule T-c, and its requirement row

On the image with Vale and lychee, the case `commit-before-edit` of module [`const-task-close`](../requirements.md#const-task-close) failed one run in three. Asked to rename a function across two folders, the model loaded the skill only after its edits. The start rule named the moment "before a batch of edits", and a rename that starts with one edit is not seen as a batch. On 2026-10-17 the decider chose to fix the cause in the module. Its start rule and the skill's description now name the moment "before the first edit of any change, such as a rename, a refactor or an edit of more than one file", and its rule T-c "before the first edit of any change"; the case passed every run after it. [Requirement A4.7](../requirements.md#a4-7) still said "dirty tree committed before a batch of edits". A fix of the carry audit's regression pass then amended the row with no record, and a confirming reader found it; this question records that amendment. Amending a row is a `process` decision under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2).

### Options

- **A. Amend the row in this record,** to "dirty tree committed before the first edit of any change", so that the merge that accepts this record accepts the row too.
  - **Pros:** the row and the module's rule say the same words, so that whether the module implements exactly its row, as [law 4 of CLAUDE.md](../../CLAUDE.md#law-4) asks, needs no reading; the change is reviewed at the one yes already due; nothing rests on reading a single edit as a batch.
  - **Cons:** a record about evals gains a ruling on another module's row; one more confirming round before the merge.
- **B. Keep the row,** and read a change's first edit as the start of its batch.
  - **Pros:** no row is amended, so no record is needed.
  - **Cons:** the row and the rule differ in wording; their agreement rests on the fuzzy moment that made the case fail.
- **C. Keep the row now, and amend it later** in a record and pull request of its own.
  - **Pros:** each record stays on its own topic; the row ends up matching the rule.
  - **Cons:** a second pull request and record for one row; until then the row and the rule differ.

### Recommendation

A, recommended by the session: the merge's yes is already the ceremony a `process` decision needs, and an explicit row is better than a reading.

### Choice

A, by the decider in chat on 2026-10-18.

## Ruling

<a id="r1"></a>**R1.** Every module ships its eval cases in `evals/` at its root, one folder per case holding a `case.yaml`, in the form `claude plugin eval` reads. The results a run writes under `evals/results/` are ignored by git and never committed.

<a id="r2"></a>**R2.** Every module ships at least one case. A module has one case per skill, which holds by `tool_used` that the model calls `Skill` with the skill's name, by a `regex` on the run's trace that no `Write` or `Edit` comes before the call that names this skill, and by a grader on the work's result where the work leaves one, a file made or a line written; a `tool_order` on one tool would miss the same change made through `Bash`, and the `regex` does not see a change made through `Bash` before the call either, which the result grader covers where the work leaves one. A case whose moment is a command also holds by `tool_order` that the skill comes before that command. It has one case per command a rule of the module makes mandatory, a script the module ships, which holds by `tool_used` on `Bash` that the command is called and by a grader on what it did, a file it made or the line it printed, that it ran; where a skill makes the command mandatory at the skill's own moment, one case holds both, the skill before the command. It has one case per start rule that carries a rule of its own, not a pointer to a skill, graded by `regex` where a pattern can see the rule and by `llm` only where none can. A case that needs files seeds them by its `scaffold_script`.

<a id="r3"></a>**R3.** Every case runs 3 times, the tool's default; the runner passes the count and the threshold, so they hold whatever a case sets. A case passes when every grader passes in every run, the threshold 1.0. The runs take `--ablation none`, so that a grader on `Skill` is scored.

<a id="r4"></a>**R4.** The runs use the model the kit's file `scripts/eval-model` names, passed as `--model`; it names `claude-opus-5-5`.

<a id="r5"></a>**R5.** A module's eval hash is taken over every file git tracks in the module's folder, links followed, save `MODULE.md`, `README.md`, `INSTALL.md`, the folder `tests/` and the folder `evals/results/`; and over the kit's `scripts/eval-container/Dockerfile`, so that a change to the image every case runs in makes every receipt stale.

<a id="r6"></a>**R6.** The receipts stand in one kit file, `scripts/eval-receipts.json`, never shipped, one entry per module. An entry names the module's eval hash, the Claude Code version of `scripts/claude-code.version`, the model of `scripts/eval-model`, and every attempt made for that hash, each with its time and its scores; a later hash starts a new entry.

<a id="r7"></a>**R7.** The kit's `scripts/run-evals.py` runs the evals of one module, or of every module, on the subscription of the person who runs it, never billed by usage: every variable Claude Code would prefer over a subscription login, an API key, an auth token and the cloud providers' switches, is dropped from the environment of its `docker` commands and unset in each container, and each container refuses to run its case unless `claude auth status` reports a subscription login. It runs them on a link-followed copy of the module, on the pinned Claude Code, and writes each attempt into the receipts file. It is kit tooling, never shipped, and no check.

<a id="r8"></a>**R8.** The kit's `scripts/check-eval-receipts.py`, an entry of the gate group with `--self-test` as its fixture, turns red for a module whose entry is missing; whose hash differs from the module's current eval hash; whose version or model differs from the pinned ones; or whose last attempt did not pass. It holds that a passing run was declared for the current files, not that it was run, as the receipt of [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5) does for an audit.

<a id="r9"></a>**R9.** A module document's acceptance table gains the kind `eval`: one item per case, naming the rows it proves, its status derived by `scripts/check-aspects.py` from the receipt. An `eval` item counts as run when its module's receipt is current, green when its last attempt passes and red when it does not, a run declared and not one the kit sees; this narrows R1 and R10 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r1). Its date, platform version and model are its receipt's, which widens [rule 10 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r10). Each `live` item run in this repository that proves a session's behaviour alone, and that a case covers whole, becomes an `eval` item, which replaces it, so that the proof that item asks for is owed no more. A `live` item that proves a scan over the kit's tree, and every deferred consumer-live item, stay `live` whatever a case covers, and the proofs they ask for stay owed: an eval proves a session's behaviour in the folder a run starts in, which a scaffold seeds where a case needs a project, never the module's live proof in the kit or in a consumer.

<a id="r10"></a>**R10.** The kit's `scripts/check-session-load.py`, an entry of the gate group in each module's job with `--self-test` as its fixture, installs the module as `scripts/check-bare-install.py` does, the shared steps in one place. It then starts one headless session with no login in the bare repository and holds two things. The `init` event lists every skill under the module's `skills/`. Every `SessionStart` hook of the module has a `hook_response` with exit 0 and output that is not empty.

<a id="r11"></a>**R11.** A change that makes a module's receipt stale is merged only with a new passing receipt, made by a local run before the merge; this narrows the guide's "No local run is required" to the gate list.

<a id="r12"></a>**R12.** A case lists the tools a session at its moment would have, so that the model can follow the module's skill as written: a skill or command case `Read`, `Glob`, `Grep`, `Write`, `Edit`, `Skill` and `Bash`; a start-rule case only what its rule needs. The runner runs each case on its own and grants it only the tools of `Bash`, `Write` and `Edit` that the case lists.

<a id="r13"></a>**R13.** Every case runs in a throwaway container of the image `scripts/eval-container/Dockerfile` defines, one container per case. The image holds the Claude Code version the kit pins, a Python at or above the kit's floor, and the Vale and lychee the kit's CI installs, which the modules' scripts call. The image's tag names the pinned Claude Code version and the Dockerfile's hash, so that a changed file is built again; no case runs on the host, so every receipt comes from one environment. The runner takes `--token-file <file>`: a subscription token from `claude setup-token`, which the runner never opens, refuses unless its owner alone can read it, judges before it asks docker for the image, and hands the container as Docker's `--env-file`. The module's copy is mounted read-only, and a results folder of the run's own writable. The container runs with Docker's seccomp filter and its `/proc` mask lifted, `--security-opt seccomp=unconfined --security-opt systempaths=unconfined`, which the eval's own sandbox needs to start. Inside, the usage-billing variables of R7 are unset, and the case runs only when `claude --version` is the pinned version and `claude auth status` reports a subscription login.

<a id="r14"></a>**R14.** The session-load check of R10 runs on the pinned Claude Code like the install check, and reads the same install source. So the gate list puts the pinned version first on `PATH` for the `session-<module>` entries too, which widens R4 of [dec-0075-install-checks-read-the-init-event-keep-plugin-variables-and-run-locally-on-the-pin](dec-0075-install-checks-read-the-init-event-keep-plugin-variables-and-run-locally-on-the-pin.md#r4); and a module's job carries the install source for its session entry too, which widens R5 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r5).

<a id="r15"></a>**R15.** [Requirement A4.7](../requirements.md#a4-7) has a dirty tree committed before the first edit of any change, not before a batch of edits. Rule T-c of module [`const-task-close`](../requirements.md#const-task-close), the description of its skill `commit-before-edit` and its start rule name the same moment; the description and the start rule give a rename, a refactor and an edit of more than one file as its examples.

## Carry list

1. R1 — the eval case row of [template §6](../../module-template/MODULE.md#t6); [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [the kit's ignore file](../../.gitignore).
2. R2 — the eval case row of [template §6](../../module-template/MODULE.md#t6); [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
3. R3 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring; the eval case row of [template §6](../../module-template/MODULE.md#t6); [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
4. R4 — [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstring of `eval_model`; [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring.
5. R5 — [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstrings of `eval_files` and `eval_hash`.
6. R6 — [`scripts/kit_evals.py`](../../scripts/kit_evals.py), its docstring of the receipts file.
7. R7 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
8. R8 — [`scripts/check-eval-receipts.py`](../../scripts/check-eval-receipts.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
9. R9 — [template §10](../../module-template/MODULE.md#t10); [rule 8 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r8) and [its rule 10](../policies/plc-0006-module-documents.md#r10); [`scripts/check-aspects.py`](../../scripts/check-aspects.py), its docstring; [CLAUDE.md](../../CLAUDE.md), step 5 of "Developing a module". Which live items became eval items, and that the narrowing and the widening are this record's, is history.
10. R10 — [`scripts/check-session-load.py`](../../scripts/check-session-load.py), its docstring; [`scripts/kit_install.py`](../../scripts/kit_install.py), its docstring; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
11. R11 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
12. R12 — the eval case row of [template §6](../../module-template/MODULE.md#t6); [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring. That eight cases lost `Bash` for a day, and got it back, is history.
13. R13 — [`scripts/run-evals.py`](../../scripts/run-evals.py), its docstring; [the image](../../scripts/eval-container/Dockerfile), its header and its comment on the tools it installs; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI".
14. R14 — [`scripts/gate-list.sh`](../../scripts/gate-list.sh), its header and `run_entry`; [`scripts/setup-claude.sh`](../../scripts/setup-claude.sh), its header; [the workflow](../../.github/workflows/gates.yml), its header, its step that installs Claude Code and the comment on the install source; [`scripts/kit_module_doc.py`](../../scripts/kit_module_doc.py), the fix `put_first` words; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI". That it widens R4 of dec-0075 and R5 of dec-0061 is history.
15. R15 — [requirement A4.7](../requirements.md#a4-7); [the module document of `const-task-close`](../../modules/const-task-close/MODULE.md), rule T-c; [its skill `commit-before-edit`](../../modules/const-task-close/skills/commit-before-edit/SKILL.md), its description; [its start rule](../../modules/const-task-close/scripts/print-skill-pointer.sh).
