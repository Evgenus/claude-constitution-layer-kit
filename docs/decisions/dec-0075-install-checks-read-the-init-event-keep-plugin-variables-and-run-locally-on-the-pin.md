---
id: dec-0075-install-checks-read-the-init-event-keep-plugin-variables-and-run-locally-on-the-pin
type: task-record
title: The install checks fail to run on an init event they cannot read, keep four plugin variables from claude, and run locally on a pinned Claude Code the gate list puts first
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The install checks fail to run on an init event they cannot read, keep four plugin variables from claude, and run locally on a pinned Claude Code the gate list puts first

## Context

[dec-0074-install-checks-run-on-the-pinned-claude-code-and-read-its-documented-json](dec-0074-install-checks-run-on-the-pinned-claude-code-and-read-its-documented-json.md) made the kit's two install checks, `scripts/check-bare-install.py` and `scripts/check-install-guide.py`, run on one pinned Claude Code version and read the platform through its documented JSON commands. Its validation logged five leftovers, and one cost it moved onto local runs. The decider asked for them as one follow-up on 2026-10-08, and the session probed each on the trunk that day:

- **The init event.** The guide's check read the headless session's `system/init` event as before: a `plugins` that was no list, or an entry without a `name` or a `path`, read as "a session loads no module" or "runs it from None", a finding against the install guide, where dec-0074 reads a fault in a platform reply as a failure to run.
- **The person's environment.** The checks removed one variable from the environment of every `claude` command, the plugins root. Claude Code's documentation names more that steer where it finds or loads plugins: a seed folder, and plugin folders loaded as `--plugin-dir` loads them; the binary holds an undocumented one that caches an install as a zip file.
- **Local runs.** Since dec-0074 the install entries of the gate list fail to run on any other `claude` than the pinned one unless an opt-out is set, and no document said where a pinned copy lives.
- **A requirement row.** [Requirement A3.3](../requirements.md#a3-3) still said "by convention until a PR flow exists", while the PR flow and the ruleset on the trunk exist since [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md).
- **Two lines of the bare-install check.** A hook of another type than `command`, or a `timeout` that is no number, ended the check in a traceback; a failing `git commit` in its bare repository read "git -c failed", with the fix "install git" for a git that had run.

At the decider's yes in chat that day, the session installed Claude Code 2.1.282, the pinned version, in a scratch folder beside the machine's own, and probed each plugin variable there with an empty configuration: the zip cache made the install's `installPath` a file; the plugin folders made the session load a same-named plugin from them instead of the install; a seed made a session load a plugin from the seed's cache and list the seed's marketplace. Two other undocumented names changed no reply, and four are set by Claude Code for a helper command, not read. Three questions were put to the decider in chat that day, one per message, each with lettered options and one recommendation, the pick a letter; sections 1, 3 and 4 hold them. Sections 2 and 5 put no choice: each applies a ruling the kit already holds to a place it did not yet reach.

The hooks file's shapes and the git line of the bare repository are routine, noted in their commits. No module changes, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## 1. One pull request and one record

The requirement row is `process` by [rule 2 of plc-0007](../policies/plc-0007-requirements.md#r2), and the init event extends R4 of dec-0074; the two lines of the bare-install check alone would be routine. The question was how the change reaches the trunk.

- **A. One pull request, one `process` record** for the row, the init event, the variables and the local runs, the two routine fixes noted in their commits.
  - **Pros:** one carry audit, one independent verification, one yes; the three scripts and their docstrings are written and audited once; the two routine fixes are about an hour of work and nobody waits for them.
  - **Cons:** the two routine fixes wait for the whole change, about one working day; the record carries a row unrelated to the install checks.
- **B. Two pull requests**, the two routine fixes first with no record, then the rest with the record.
  - **Pros:** the traceback and the wording fixes reach the trunk a few hours sooner; the first pull request needs no audit.
  - **Cons:** both edit the bare-install check and its self-test, so the second audit reads code the first just changed; two gate-list runs, two CI runs and two merges, about two to three more hours; nobody waits for the first half.
- **C. One pull request, only the row recorded**, the init event and the variables priced routine as applying R4 of dec-0074.
  - **Pros:** a smaller record that holds only the row's change.
  - **Cons:** R4 names the replies it covers and the init event is not among them, so a silent extension is the call dressed as routine that the kit's stakes triage forbids; the carry audit runs anyway because of the row, so C saves almost nothing.

The session recommended A: the audit runs anyway because of the row, so a split saves no work, and B's head start helps no one. The decider chose A in chat on 2026-10-08.

**R1.** One pull request and one record for the rulings below; the hooks file's shapes and the git line of the bare repository are routine, noted in their commits.

## 2. The headless session's init event

R4 of dec-0074 reads a reply of the documented `--json` commands that the check cannot read as a failure to run, never as a finding against a module or the guide. The guide's check also reads the `system/init` event of a headless session in the project, which Claude Code's headless page documents: `plugins`, the plugins that loaded, each with a `name` and a `path`. R4 does not name that event, and the check read a fault in it as a finding against the guide. No choice was put: the session applied R4's reading to the event, and the decider priced it `process` with section 1.

**R2.** check-install-guide reads the headless session's `system/init` event as the headless page documents it: `plugins`, a list of objects, each with a `name` and a `path` that are non-empty strings. A `plugins` that is absent or no list, an entry that is no object, a `name` or a `path` that is absent, no string or empty, and two entries of one name are a failure to run, never a finding against the guide, with R4's two-state fix naming the reader `session_paths`. The first init event of the stream is the one read. A list read whole that lacks a module, a path that is not the plugin cache's copy, and a session that prints no init event stay findings against the guide. This adds the init event to the replies R4 of dec-0074 covers.

## 3. The variables kept from claude

Both checks removed one variable from the environment of every `claude` command they run, the plugins root, so that the configuration folder each makes is where Claude Code keeps the run's plugins. The probe found three more that steer where Claude Code finds, keeps or loads plugins. The kit's CI itself sets a fourth plugin variable, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`, so that the install jobs clone the private repository over HTTPS with the job's token: a rule that removes it breaks CI. The question was which variables the checks remove.

- **A. A named list**: the four that steer where plugins are found, kept or loaded, each proven removed by a self-test case, the docstrings naming all four.
  - **Pros:** each name rests on the documentation or a probe of the pinned version; every other variable still reaches `claude`, so nothing CI or a person needs is taken away; the rule is easy to state and to test.
  - **Cons:** a new variable of the kind in a later version gets through until someone checks; the guard is the move of the pin, which must probe the list again, held by review alone.
- **B. Remove by name prefix**, the plugin families, with a kept list of the transport and timeout variables.
  - **Pros:** a future variable of those families is removed by default, with no review at the pin's move.
  - **Cons:** the kept list needs the same judgment, variable by variable, as A; a future transport or timeout variable is dropped unseen, and on a slow network an install could then fail and be blamed on the module; two lists to maintain.
- **C. An allow-list**: `claude` gets only named variables (`PATH`, the sign-in, proxy and git-credential ones, the temporary folder, the locale).
  - **Pros:** the strictest; no setting of a person's reaches the checks unless it is listed.
  - **Cons:** sign-in and proxy variables are many and change between versions; a missing one breaks CI or a person's run with an error far from its cause; the biggest change, much of it unprobed.

The session recommended A: every name is proven on the pin, it keeps what CI needs, and its one gap belongs to the pin's move, which already proves every read again. The decider chose A in chat on 2026-10-08.

**R3.** Both install checks run every `claude` command in the environment they were given less four variables, each whether set to a value or to nothing: `CLAUDE_CODE_PLUGIN_CACHE_DIR`, `CLAUDE_CODE_PLUGIN_SEED_DIR`, `CLAUDE_CODE_PLUGIN_DIRS` and `CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE`, the variables that, by Claude Code's documentation and a probe of 2.1.282, steer where it finds, keeps or loads plugins. Every other variable reaches `claude`, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` among them, save those the checks set themselves. So the configuration folder a check makes is the platform's whole plugin home for the run. A later version's new variable of the kind is found by the probe that the move of the pin asks, held by review.

## 4. A pinned Claude Code for local runs

Since dec-0074 the install entries and the guide of the gate list fail to run on any other `claude` than the pinned one, unless `CONSTITUTION_KIT_ANY_CLAUDE=1` lets them run with a note. The machine the kit is developed on had a newer version, and each change so far installed the pinned one into a scratch folder at the decider's yes and removed it at the merge. The question was where a pinned copy lives for local runs.

- **A. A fixed folder in the clone, ignored by git, filled by a kit script**, which the gate list puts first on `PATH` for the install entries and the guide; the fix of a run off the pin names the script.
  - **Pros:** one command per clone, and again when the pin moves; then every local run is on the pin with no variable to remember; the fix is one command to follow; the worktrees of a clone share the copy.
  - **Cons:** about 220 MB inside the clone; a new kit script, an ignore line and a change to the gate list, each held by checks or review; the gate list must not shadow the global install CI uses.
- **B. A folder of one's own choosing, named by a variable** the gate list puts first on `PATH`, filled by hand with the command the fix already prints.
  - **Pros:** one copy can serve every clone and project; nothing is added to the tree but a few lines in the gate list.
  - **Cons:** a second variable to set in every shell and for every runner agent, forgotten as the opt-out is; the install stays a manual step.
- **C. Nothing new**: the gate list's header and the runner agent say that local runs use the opt-out and CI is the proof on the pin.
  - **Pros:** no new machinery; nothing more to audit.
  - **Cons:** every local green is off the pin; each change still needs a scratch install and the decider's yes to prove its merge on the pinned version.

The session recommended A: the cost recurs with every change, and A removes it with one command per clone, while B moves it to a variable that gets forgotten. The decider chose A in chat on 2026-10-08.

**R4.** A clone runs the install entries and the guide of the gate list on the pinned Claude Code through `sh scripts/setup-claude.sh`, which installs the version `scripts/claude-code.version` names into `.claude-code-pinned/` beside git's common directory — one copy for every worktree of the clone, ignored by git, replaced whole at each install — and whose `--check` tells whether that copy answers the pin. When that copy's `claude` is there and can be run, `scripts/gate-list.sh --run` puts it first on `PATH` for the `install-<module>` entries and `guide` alone; CI never has it and runs as before. The fix both checks print for a run off the pin names the script first, and a hand install beside one's own second.

## 5. The requirement row on immutability

The enforcement cell of [requirement A3.3](../requirements.md#a3-3) named the kit's immutability "by convention until a PR flow exists". Since dec-0057 every change reaches the shared trunk through a pull request, under a ruleset with no force push, no deletion and no one on its bypass list. No choice was put: the session wrote the cell to state what holds, and the decider priced it `process` with section 1, as [rule 2 of plc-0007](../policies/plc-0007-requirements.md#r2) asks of an amended row. The same old words stand in the accepted [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md), which is not touched.

**R5.** The enforcement cell of [requirement A3.3](../requirements.md#a3-3) keeps its general rule — a protected trunk holds immutability, by convention until a repository has a pull-request flow — and states the kit's own flow beside it. The kit's shared trunk is held by its repository's ruleset: every change through a pull request, no force push, no deletion, no one on its bypass list. A local trunk is unheld save for the local commit gate, which `sh scripts/setup-clone.sh` sets up once per clone and which refuses a commit, an amend, a cherry-pick and a revert there; whatever else moves a local trunk reaches the shared one only through a pull request's merge. A commit's naming stays review judgment.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests and the documents; the commits after it correct the code, the documents and this record before its yes, on the findings of its validation and of its carry audit. The message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [check-install-guide](../../scripts/check-install-guide.py), its docstring.
3. R3 — [the reader](../../scripts/kit_module_doc.py), its docstring of `claude_env` and its module docstring; [check-bare-install](../../scripts/check-bare-install.py) and [check-install-guide](../../scripts/check-install-guide.py), their docstrings.
4. R4 — [the setup script](../../scripts/setup-claude.sh), its header; [the gate list](../../scripts/gate-list.sh), its header; [the reader](../../scripts/kit_module_doc.py), its docstring of `put_first`; [CLAUDE.md](../../CLAUDE.md), "The gate list and CI".
5. R5 — [requirement A3.3](../requirements.md#a3-3), its enforcement cell.
