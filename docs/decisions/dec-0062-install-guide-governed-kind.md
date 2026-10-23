---
id: dec-0062-install-guide-governed-kind
type: task-record
title: The install guide is a governed kind of one document, INSTALL.md at the root, under its own policy
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The install guide is a governed kind of one document, INSTALL.md at the root, under its own policy

## Context

Until this record, `README.md` was the kit's install guide and nothing else: its title was "Install Guide", and it called itself "the install procedure only". The README is the page GitHub shows a new reader first, so the reader met the prerequisites before learning what the kit is. The decider asked for the README to state the kit's intent as a landing page, with the install guide as a document of its own.

On 2026-09-30 the session checked the README's install path on Claude Code 2.1.282 and found two claims that were wrong. First, a plugin installed from a local marketplace is copied into the plugin cache and does not load in place. Second, `claude plugin update` reports a draft at its version as current after the kit has changed it. The README is in no policy's territory, so no rule asked for its commands to be checked. This is the friction behind the first question below.

The record grew while its change was made: the questions were put in chat one per message, each with lettered options, and the pick was the letter. It was born `active` and is `inactive` by the last commit of its branch.

## 1. Whether the install guide is governed

- **A. `INSTALL.md` at the root, ungoverned.** The guide sits beside the README, in no policy's territory, like `CLAUDE.md` and the README.
  - **Pros:** the name and place every GitHub reader knows; a routine change with no record; it keeps R36 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r36), that the next policies wait for friction.
  - **Cons:** the same name as each module's own `INSTALL.md`; no policy states what the guide must hold.
- **B. `docs/install.md`, ungoverned.** The same as A, under `docs/`.
  - **Pros:** a tidy root; no name clash with the modules' `INSTALL.md` files; still routine.
  - **Cons:** harder to find from the front page; only the README's link leads to it.
- **C. A governed install-guide kind.** A new policy with its own territory, created by the new-kind procedure of [`const-locations`](../requirements.md#const-locations).
  - **Pros:** the guide carries an envelope and stated rules, for example that every command is checked on a named Claude Code version; the gates read it.
  - **Cons:** a `process` decision with a record, a carry audit and a yes on the merge; ceremony for one document.

The session recommended A: the place a new user looks first, routine, and the policy waiting for friction. C, chosen by the decider in chat on 2026-10-01. The two wrong claims of 2026-09-30 are the friction a policy answers.

<a id="r1"></a>**R1.** The install guide is a document kind of its own, governed by its own policy in the root policy's territory, created and changed as [rule 3 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r3) says. The README is no longer the install guide.

## 2. Where the install guide lives

- **A. `INSTALL.md` at the root, territory `/INSTALL.md`.** One document beside the README, in the same form as `/INTENT.md`.
  - **Pros:** the name and place a GitHub reader looks for; the leading slash limits the territory to the root file, so the modules' `modules/*/INSTALL.md` stay outside it; the same form as the intent page's policy.
  - **Cons:** the create command of [`const-locations`](../requirements.md#const-locations) refuses a territory of one path, so the guide is first written by hand under its policy, as the intent page was; GitHub shows the front matter as a table at the top of the page.
- **B. `docs/install-guide.md`, territory `/docs/install-guide.md`.** One document beside the other kit documents.
  - **Pros:** a tidy root; no name that resembles the modules' `INSTALL.md` files.
  - **Cons:** harder to find without the README's link; the same one-path and front-matter costs as A.
- **C. A folder, territory `docs/install/**`.** The guide split into a walkthrough that bootstraps a new project and a reference of the install steps for one module.
  - **Pros:** the create command works there, so each document is born with a valid envelope; each part stays short and has one job.
  - **Cons:** a reader opens two files instead of one; no friction yet shows that two documents are needed; a later rename or merge is another `process` change.

The session recommended A: the place new users look, at the cost of writing by hand once and a front-matter table the intent page already shows. A, chosen by the decider in chat on 2026-10-01.

<a id="r2"></a>**R2.** The install guide is one document, `INSTALL.md` at the repository's root, and its policy's territory is `/INSTALL.md`, with the leading slash. A module's own `INSTALL.md` is not of this kind.

## 3. How the guide's commands are kept true

- **A. Review, with a stamp.** The guide states the Claude Code version and the date its commands were last run; review holds that a changed command, or a new Claude Code version, is run again.
  - **Pros:** no new code; the reader sees which version the guide was tested on.
  - **Cons:** judgment only, the protection the README had when it was wrong; the stamp can claim a run that never happened.
- **B. A kit check that runs the guide.** A new `scripts/check-install-guide.py` takes the guide's command blocks marked runnable and runs them in order, in a scratch repository with an empty Claude configuration folder, in CI on every pull request; files the reader writes by hand come from the check's own fixture.
  - **Pros:** deterministic, so a wrong command or a changed platform turns CI red; it covers the update and reinstall path, where the README was wrong; it reuses the CI install route of `scripts/check-bare-install.py`.
  - **Cons:** the largest change: a new check with its `--self-test`, an entry of the gate list, and Claude Code installed in the CI job `kit`, which installed none under R5 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r5); a marker for runnable blocks; the steps written by hand stay review.
- **C. The existing install check, plus a stamp.** The policy requires the guide's `marketplace add` and `install` commands to be the ones `scripts/check-bare-install.py` runs for each module in CI; the rest is held as in A.
  - **Pros:** reuses a check that exists; no new code beyond a sentence of policy.
  - **Cons:** it protects only the part that already worked; update, reinstall and the scan loop stay judgment; whether the two command sets match is review too.

The session recommended B: only a run makes the guide's commands trustworthy, and A or C would have let both wrong claims of 2026-09-30 through. B, chosen by the decider in chat on 2026-10-01.

<a id="r3"></a>**R3.** The commands of the install guide are run by a kit check, `scripts/check-install-guide.py`, never shipped in a module, an entry of the gate list with `--self-test` as its fixture, run by the kit's CI on every pull request and on `main` after each merge. A block the check does not run, a step the reader writes by hand, and whether the guide is whole and clear stay review.

## 4. What the check holds the guide to

- **A. Exit codes only.** Every runnable block runs in order, from a fresh scratch project, and must exit 0.
  - **Pros:** the smallest check; it knows nothing of the guide's content.
  - **Cons:** it misses the error of 2026-09-30, since `claude plugin update` exits 0 while it leaves the old copy in place; a command that runs but does the wrong thing passes.
- **B. Exit codes plus the guide's claims.** As A, and at named points the check tests what the guide says happened: after the install, each module is in the plugin cache and enabled in the project's settings; after a change the check makes in its own copy of the kit, the guide's update path puts the change into the cache; after the bootstrap, every module's scan exits 0 on the new project.
  - **Pros:** it catches the class of error found on 2026-09-30; each claim the guide makes about the platform gets a test.
  - **Cons:** the check knows the guide's sections by name, so a renamed section is red until the check follows; more code and a larger self-test.
- **C. The guide carries its own tests.** The check stays as in A, and the guide holds short verify commands a user also runs.
  - **Pros:** every test is something the guide teaches; the check stays small.
  - **Cons:** the guide fills with test commands a new user does not need; the update test needs a change in the kit between two blocks, which no block a user runs can make.

The session recommended B: A passes the error that justified the check, and C makes the guide harder to read. B, chosen by the decider in chat on 2026-10-01.

<a id="r4"></a>**R4.** Beside the exit of every block it runs, the check tests at named points what the guide says happened. The project is a git repository; the kit is a known marketplace; every module stands in the plugin cache at its manifest version and is enabled in the project's settings; the kernel copy is the kit's kernel, byte for byte; the commit leaves a clean tree; after a change the check commits into its clone of the kit, the update leaves the cached draft as it was and the reinstall takes the change; the uninstall leaves no module enabled or recorded for the project. The run happens in a home folder of its own, the kit cloned from the working folder's HEAD to the guide's placeholder path. What the reader writes by hand comes from the check's fixture: the dials file is the guide's own example, and the fixture writes one policy per namespace that claims a territory and record #1, named and placed by the dials' first catalog. The first finding ends the run.

## 5. How a block is marked for the check

- **A. A word on the fence.** ```` ```bash check=<name> ````: every `bash` block carries it, a name for a block the check runs, or `check=none` for one it cannot run; an unmarked `bash` block is red.
  - **Pros:** the mark sits on the block, so no edit separates the two; GitHub reads only the first word, so a reader sees a plain `bash` block and its copy button copies only the commands; no block slips past untested.
  - **Cons:** the mark shows in the raw Markdown; every new `bash` block needs a mark before CI is green.
- **B. An HTML comment above the block.** `<!-- check: <name> -->` on the line before the fence; a block with no comment is not run.
  - **Pros:** invisible on GitHub and in the reading flow; the fence stays plain.
  - **Cons:** an edit can move the block away from its comment unnoticed; an unmarked block is silently untested.
- **C. No mark; every `bash` block runs.** Each block is named by the anchor of its section, and a command the check cannot run is written in a `text` block.
  - **Pros:** no new syntax; the anchors exist and are fixed for life.
  - **Cons:** a shell command in a `text` block is labelled as what it is not; two runnable blocks in one section cannot be told apart.

The session checked that the style scan of [`const-styling`](../requirements.md#const-styling) accepts words after a fence's language and masks HTML comments, so all three pass it, and recommended A: the mark cannot drift from its block, and a skipped test becomes a written choice. A, chosen by the decider in chat on 2026-10-01.

<a id="r5"></a>**R5.** Every `bash` fence of the install guide names `check=<name>` after its language: a name of the closed set the check knows, each exactly once, or `none`, as often as needed, for a block the check does not run — an interactive session, a system package manager, the module fixtures. The dials example is the one `yaml` fence named `check=dials`. An unmarked `bash` block, an unknown name, a name twice, a name on the wrong fence, a mark where a fence's language should stand and a name of the set missing from the guide are each red. A block runs in a fresh `bash -eu`, in the folder the block before it ended in, so no block relies on a variable another block set: such a variable is unset there, and the block fails. A change that adds, renames or removes a named block, or changes what the guide says one does, changes the check in the same change.

## 6. Which CI job runs the check

- **A. In the job `kit`.** `kit` installs Node and Claude Code from now on.
  - **Pros:** no new kind of job; R1 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r1) stays as it is.
  - **Cons:** reverses R5 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r5), under which `kit` installs no Claude Code; every run of `kit` slows by the install and eleven plugin installs; a red on `kit` names no guide until the annotation is read.
- **B. A job of its own, `install-guide`.** The gate list maps the new entry to its own job, and the workflow installs Node and Claude Code for it as for a module's job.
  - **Pros:** `kit` stays fast and free of Claude Code; the check line says "install-guide", so a red names the guide; it runs in parallel, so the wait does not grow.
  - **Cons:** narrows R1 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r1) with a third kind of job; about one more billed minute per run; one more case in the workflow's step condition.
- **C. Only by hand, not in CI.** The check is in the gate list's extra group, run before a pull request that touches the guide or an install.
  - **Pros:** no CI cost; no change to the workflow.
  - **Cons:** a new Claude Code version or a module change breaks the guide unseen; the weakness of review the decider chose B in question 3 to escape.

The session recommended B: the red names what broke, `kit` keeps its speed, and the cost is about one billed minute. B, chosen by the decider in chat on 2026-10-01.

<a id="r6"></a>**R6.** The check's entry of the gate list, `guide`, runs the check and its `--self-test` in a CI job of its own, `install-guide`, in parallel with the others. The workflow installs Node and Claude Code for it as for a module's job; it needs no git credentials, since the check installs from a clone of the working folder. This narrows R1 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r1), one job per module and one job `kit`, and R5 there, Claude Code installed for the module jobs alone.

## 7. What the session set with these choices

These items carry no options: each follows from the answers above or from the kit's rules, and stands open to the decider's override before the yes.

<a id="r7"></a>**R7.** The policy [plc-0011-install-guide](../policies/plc-0011-install-guide.md) states the kind's rules: the type, `current-state`; the content, the kit's whole install procedure, restating no rule of the kernel and leaving each module's dials, findings and calibration to the module's own `INSTALL.md`; the present tense; anchors `s<n>`; an edit of the guide routine once the check is green on it, a change to a rule `process`; its enforcement and its style.

<a id="r8"></a>**R8.** A command of the install procedure stands in the install guide, where the check runs it; another document of the kit links to the guide instead of copying a command. A module's own `INSTALL.md` is the one exception: it ships inside the plugin, where no link to the kit's root resolves, and gives the commands of its own module — its load, the tools it needs, its scan and its fixtures.

<a id="r9"></a>**R9.** The README is rewritten as the kit's landing page — what the kit is, why it is shaped so, how it works, its modules with their gates and skills, one real gate message, the status, and where to go next — with no install command. The README lies in no territory, so the rewrite is routine.

<a id="r10"></a>**R10.** A bootstrap in a scratch folder on 2026-10-01, at the modules' defaults, found the kernel copy red under [`const-language`](../requirements.md#const-language): 22 findings of grade and sentence length, the kernel meeting the kit's own thresholds and not yet the module's defaults. The guide's dials example declares a departure of that module for `docs/constitution/**`, allowing grade and sentence, with its reason.

<a id="r11"></a>**R11.** That departure leaves the guide's example when the kit's kernel meets the module's default thresholds, in the kit's descent to the defaults.

<a id="r12"></a>**R12.** A length ceiling of [`const-doc-budgets`](../requirements.md#const-doc-budgets), `install-guide`, holds the guide at 15,000 characters at warning: its length on its first day, 12,862 characters, plus 10 %, rounded up to 1,000, with that one day as its window.

## Applied

The change that adds this record applies every item: the policy and its territory, the guide, the check and its wiring in the gate list, the workflow, `CLAUDE.md` and the gate-list agent, the README, the ceiling, and the plan's clause for R11. So the record is `inactive` by the last commit of its branch.

## Carry list

1. R1 — [plc-0011-install-guide](../policies/plc-0011-install-guide.md), its opening paragraph; [the dials file](../../constitution.yaml), the namespace of [plc-0011-install-guide](../policies/plc-0011-install-guide.md); [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r3), rule 3. That the README was the install guide until this record is history.
2. R2 — [the dials file](../../constitution.yaml), the territory of [plc-0011-install-guide](../policies/plc-0011-install-guide.md) and its comment.
3. R3 — [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r7), rules 4 and 7; [the check](../../scripts/check-install-guide.py), its docstring; [the list script](../../scripts/gate-list.sh), the entry `guide`; [the install guide](../../INSTALL.md#s6), its last section, for a check shipped in no module.
4. R4 — [the check](../../scripts/check-install-guide.py), its docstring; [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r4), rule 4.
5. R5 — [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r4), rule 4; [the check](../../scripts/check-install-guide.py), its docstring.
6. R6 — [the list script](../../scripts/gate-list.sh), its header, `job()` and `commands()`; [the workflow](../../.github/workflows/gates.yml), its header and its install steps; the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md). The narrowing of dec-0061's R1 and R5 is history.
7. R7 — [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r1), rules 1 to 8.
8. R8 — [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r2), rule 2.
9. R9 — history only: a routine rewrite of a page in no territory, made by this change.
10. R10 — [the install guide](../../INSTALL.md#s2), step 4 of its bootstrap; the finding itself is history.
11. R11 — pending: [the rollout plan](../rollout-plan.md#s9), step 9, the kit's descent to the defaults of `const-language`.
12. R12 — [the dials file](../../constitution.yaml), the ceiling `install-guide` of `const-doc-budgets`.
