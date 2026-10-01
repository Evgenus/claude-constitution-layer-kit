---
id: dec-0062-install-guide-governed-kind
type: task-record
title: The install guide is a governed kind of one document, INSTALL.md at the root, under its own policy
status: active
stakes: process
decider: Eugene Chernyshov
---

# The install guide is a governed kind of one document, INSTALL.md at the root, under its own policy

## Context

Until this record, `README.md` was the kit's install guide and nothing else: its title was "Install Guide", and it called itself "the install procedure only". The README is the page GitHub shows a new reader first, so the reader met the prerequisites before learning what the kit is. The decider asked for the README to state the kit's intent as a landing page, with the install guide as a document of its own.

On 2026-09-30 the session checked the README's install path on Claude Code 2.1.282 and found two claims that were wrong. First, a plugin installed from a local marketplace is copied into the plugin cache and does not load in place. Second, `claude plugin update` reports a draft at its version as current after the kit has changed it. The README is in no policy's territory, so no rule asked for its commands to be checked. This is the friction behind the first question below.

The record grows while its change is made: the questions were put in chat one per message, each with lettered options, and the pick was the letter. It is born `active`.

## 1. Whether the install guide is governed

- **A. `INSTALL.md` at the root, ungoverned.** The guide sits beside the README, in no policy's territory, like `CLAUDE.md` and the README.
  - **Pros:** the name and place every GitHub reader knows; a routine change with no record; it keeps R36 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md), that the next policies wait for friction.
  - **Cons:** the same name as each module's own `INSTALL.md`; no policy states what the guide must hold.
- **B. `docs/install.md`, ungoverned.** The same as A, under `docs/`.
  - **Pros:** a tidy root; no name clash with the modules' `INSTALL.md` files; still routine.
  - **Cons:** harder to find from the front page; only the README's link leads to it.
- **C. A governed install-guide kind.** A new policy with its own territory, created by the new-kind procedure of [`const-locations`](../requirements.md#const-locations).
  - **Pros:** the guide carries an envelope and stated rules, for example that every command is checked on a named Claude Code version; the gates read it.
  - **Cons:** a `process` decision with a record, a carry audit and a yes on the merge; ceremony for one document.

The session recommended A: the place a new user looks first, routine, and the policy waiting for friction. C, chosen by the decider in chat on 2026-10-01. The two wrong claims of 2026-09-30 are the friction a policy answers.

**R1.** The install guide is a document kind of its own, governed by its own policy in the root policy's territory, created and changed as [rule 3 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r3) says. The README is no longer the install guide.

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

**R2.** The install guide is one document, `INSTALL.md` at the repository's root, and its policy's territory is `/INSTALL.md`, with the leading slash. A module's own `INSTALL.md` is not of this kind.

## 3. How the guide's commands are kept true

- **A. Review, with a stamp.** The guide states the Claude Code version and the date its commands were last run; review holds that a changed command, or a new Claude Code version, is run again.
  - **Pros:** no new code; the reader sees which version the guide was tested on.
  - **Cons:** judgment only, the protection the README had when it was wrong; the stamp can claim a run that never happened.
- **B. A kit check that runs the guide.** A new `scripts/check-install-guide.py` takes the guide's command blocks marked runnable and runs them in order, in a scratch repository with an empty Claude configuration folder, in CI on every pull request; files the reader writes by hand come from the check's own fixture.
  - **Pros:** deterministic, so a wrong command or a changed platform turns CI red; it covers the update and reinstall path, where the README was wrong; it reuses the CI install route of `scripts/check-bare-install.py`.
  - **Cons:** the largest change: a new check with its `--self-test`, an entry of the gate list, and Claude Code installed in the CI job `kit`, which installed none under R5 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md); a marker for runnable blocks; the steps written by hand stay review.
- **C. The existing install check, plus a stamp.** The policy requires the guide's `marketplace add` and `install` commands to be the ones `scripts/check-bare-install.py` runs for each module in CI; the rest is held as in A.
  - **Pros:** reuses a check that exists; no new code beyond a sentence of policy.
  - **Cons:** it protects only the part that already worked; update, reinstall and the scan loop stay judgment; whether the two command sets match is review too.

The session recommended B: only a run makes the guide's commands trustworthy, and A or C would have let both wrong claims of 2026-09-30 through. B, chosen by the decider in chat on 2026-10-01.
