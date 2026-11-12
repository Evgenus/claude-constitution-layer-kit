---
id: dec-0071-projects-install-from-github
type: task-record
title: Projects install the kit from its GitHub repository, a registered clone is live mode, and the install guide check holds the cache copy a session runs
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Projects install the kit from its GitHub repository, a registered clone is live mode, and the install guide check holds the cache copy a session runs

## Context

The install guide told a project to register a local clone of the kit as its marketplace and to install each module at project scope. It said each install copies the module into the plugin cache, and that a later edit in the kit reaches the project only through an update. Limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4) said the opposite for the kit's own sessions: a relative-path entry of a marketplace added from a local folder runs from its source. The two could not both hold for a project, and the guide's check, `scripts/check-install-guide.py`, looked only at the cache, never at what a session runs.

On 2026-10-07, on Claude Code 2.1.286, the session ran both forms in throwaway configurations, a marked file in each place a session might read:

- **A local clone.** A project that registered a local clone ran the clone's working files: its session reported the clone's module folder as the plugin's path, and the hook printed the clone's marker;
- **GitHub.** A project that registered `Evgenus/claude-constitution-layer-kit` ran the copy in the plugin cache: its session reported the cache path, and the hook printed the cache copy's marker, never the marketplace clone's.

Two questions followed, put to the decider in chat that day, one per message.

## 1. Which form the guide gives a project

- **A. GitHub first, the local clone a named live mode.** The bootstrap installs from the repository; a short passage says a registered clone runs live.
  - **Pros:**
    - **a project runs the frozen, versioned copy** the modules' design assumes;
    - **the update section becomes true**;
    - **the live form stays available** with its risk stated.
  - **Cons:**
    - **a project needs read access to the repository**, private today;
    - **a fix found in a draft's live proof** reaches the project only after a reinstall.
- **B. Keep the local clone, state that it runs live.**
  - **Pros:** matches the guide's purpose while modules are drafts; a kit fix is live at once.
  - **Cons:** a project's behaviour changes with every checkout and pull in the clone, unfinished branches included; no version is pinned.
- **C. Both, as equal choices.**
  - **Pros:** each project picks.
  - **Cons:** two paths for the check to keep true; the reader chooses before knowing the trade-off.

Recommendation: A, since only the GitHub form gives a project a frozen copy per version; the session recommended it. The decider chose A in chat on 2026-10-07.

<a id="r1"></a>**R1.** A project installs the kit's modules from its GitHub repository: the install guide's bootstrap registers `Evgenus/claude-constitution-layer-kit` as the marketplace, and its prerequisites name read access to the repository beside the local clone, from which the guide's commands take the module names, the kernel copy, the scans and the fixtures. A draft's live proof still loads the modules from the kit's path, as rule 4 of [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r4) says. Every project, the proof's included, installs from GitHub once the modules are published, at `0.1.0` as [step 10 of the rollout plan](../rollout-plan.md#s10) says, the switch being [its step 11](../rollout-plan.md#s11).

<a id="r2"></a>**R2.** Registering a local clone as the marketplace is live mode: a session runs each module from the clone's working files in place, so every edit and every branch checked out there reaches the project, a hook script at its next run and the rest at the next session or reload. It serves the kit's own development and a module's live proof — a project that is a draft's proof loads the modules so, and switches to the GitHub install once the modules are published — never a project's working install.

## 2. What the guide's check holds of the GitHub form

Building the check showed one claim it could no longer run. It had held that an update leaves a draft's change at an unchanged version untaken, and a reinstall takes it, by committing a probe into the local clone the marketplace read. With a GitHub source the platform fetches from GitHub alone: on 2026-10-07 `claude plugin marketplace update` ignored the `origin` of its own clone and dropped a local commit there, and a static git server on localhost failed the platform's clone, which read only the server's refs and `HEAD`. A CI job cannot push a probe to GitHub.

- **A. The GitHub form, the update claim narrowed and stated.** The check installs from the change's GitHub branch and holds marketplace, install, a session running the cache copy, kernel, scan, commit and uninstall. For update and reinstall it holds what a run can show, and the guide states the draft behaviour as a platform fact seen that day.
  - **Pros:** the check runs the form the guide gives; the new session claim guards the defect found.
  - **Cons:** one claim moves from a probe to a dated observation; CI's job needs git credentials, and a run by hand needs the branch pushed.
- **B. The GitHub form for the bootstrap, a local marketplace for update and reinstall.**
  - **Pros:** keeps a real probe.
  - **Cons:** checks the update commands against a form the guide no longer gives, which runs in place.
- **C. A local git server standing in for GitHub.**
  - **Pros:** full control of the probe; no credentials in CI.
  - **Cons:** the most code; tests a source the guide never uses; the platform's clone against it unproven.

Recommendation: A, since it tests the form projects use and adds the claim that matters most; the session recommended it. The decider chose A in chat on 2026-10-07.

<a id="r3"></a>**R3.** The install guide's check points the guide's `claude plugin marketplace add` at the change: the environment's `CONSTITUTION_KIT_INSTALL_FROM`, `<owner>/<repo>#<branch>`, else the kit's origin on GitHub at the branch checked out, which must be at HEAD; a source it cannot point is a configuration failure with its fix. The kit's CI gives its `install-guide` job the change's repository and branch and the git credentials the module jobs have. This replaces, in R6 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r6), that the job needs no git credentials because the check installs from a clone of the working folder.

<a id="r4"></a>**R4.** The check holds that the marketplace is registered from a GitHub source naming the source's repository, that the platform's clone of it holds the same modules at the same versions as the kit's clone — in CI the clone is the job's checkout of the change and the source its head branch — and that a headless session in the trusted project reports each module's path in the plugin cache. The path is reported before the model is called, so the run needs no login.

<a id="r5"></a>**R5.** For update the check holds that every module stays in the plugin cache at its manifest version and enabled; for reinstall, that a module's cached copy holds the same files as the module in the platform's clone of the marketplace, read through its links, byte for byte. That an update leaves a draft's change at an unchanged version untaken is a platform fact the guide states with the version and the date it was seen. No run of the check exercises it. This replaces, in R4 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r4), the probe the check committed into its clone of the kit to show that the update leaves the cached draft as it was and the reinstall takes the change.

## Applied

The commits of this branch apply every item: the check and the workflow, the guide, then this record with the sentence of limit 3. The record is born `inactive`.

## Carry list

1. R1 — [the install guide](../../INSTALL.md), its opening, its prerequisites and step 2 of [§2](../../INSTALL.md#s2); [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r4), rule 4, for the live proof's load from the kit's path.
2. R2 — [the install guide](../../INSTALL.md), its opening, step 2 of [§2](../../INSTALL.md#s2) and the live mode of [§3](../../INSTALL.md#s3); [kit-shared-gate-code §4](../../shared/GATE.md#g4), limit 3.
3. R3 — [the install guide's check](../../scripts/check-install-guide.py), its docstring; [the CI workflow](../../.github/workflows/gates.yml), the steps of the `install-guide` job; [the gate list](../../scripts/gate-list.sh), its header. The narrowing of R6 of dec-0062-install-guide-governed-kind is history.
4. R4 — [the install guide's check](../../scripts/check-install-guide.py), its docstring; [kit-shared-gate-code §4](../../shared/GATE.md#g4), limit 3.
5. R5 — [the install guide's check](../../scripts/check-install-guide.py), its docstring; [the install guide](../../INSTALL.md), [§4](../../INSTALL.md#s4). The narrowing of R4 of dec-0062-install-guide-governed-kind is history.
