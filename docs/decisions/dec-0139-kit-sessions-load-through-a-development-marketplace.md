---
id: dec-0139-kit-sessions-load-through-a-development-marketplace
type: task-record
title: The kit loads its own modules through a development marketplace of another name
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit loads its own modules through a development marketplace of another name

## Context

Step 11 of the rollout plan has the first project switch from path load to the marketplace install. That project's session tested the switch on the Claude Code version the kit pins, in a throwaway configuration. It found a clash.

The platform keeps one entry for each marketplace name, for all the projects of a user. A session that starts in a trusted folder overwrites that entry with the source the folder's settings declare. The kit's own settings declared the published marketplace as its own folder. A project declares the same name from GitHub. So each side overwrote the other. After a session of the project, a session of the kit found its modules not cached, and its gates did not load.

An agent of the orchestrating session then tested ways out, again in throwaway configurations and on throwaway clones.

## Options

- **A. A development manifest beside the published one.** A second file in the same folder carries another name. The kit's settings declare that file and enable the modules under its name.
  - **Pros:** it ends the clash at its cause. The published name then always means the GitHub source. Both files sit in one folder, so the check that keeps them in step is simple.
  - **Cons:** one more manifest to keep in step. The plugin ids of the kit's own sessions change. A branch that still has the old settings brings the clash back while a session runs on it.
- **B. The same manifest inside the modules' folder.**
  - **Pros:** it loaded the same way in the tests.
  - **Cons:** a plugin folder among the module folders, where the checks that walk them may trip on it.
- **C. No change.** The kit keeps the published name for its own sessions.
  - **Pros:** nothing to build.
  - **Cons:** no project on a machine that also develops the kit can declare the marketplace from GitHub, so step 11 cannot close there.

Three other ways failed in the tests. The platform refuses a manifest whose sources lie outside its own folder. A settings key of another name changes nothing, since the name comes from the manifest. A plugin folder named in the environment works for one shell or one user, never for one project.

## Recommendation

The orchestrating session recommended A. It is the only way step 11 can close, and of the two forms that load it is the tidier.

## Choice

The decider picked A in the orchestrating session's chat on 2026-11-17, with the words "A: dev manifest file". The option as put there had live mode move to the development name too.

## Ruling

<a id="r1"></a>**R1.** The kit's own sessions load its modules through a development marketplace. Its manifest is `.claude-plugin/dev-marketplace.json`, beside the published one, and its name is `claude-constitution-layer-kit-dev`. The kit's committed settings declare that file by a relative `file` source. They enable each module as `<module>@claude-constitution-layer-kit-dev`. They never name the published marketplace. The switch that turns a module off for one clone bears the development name too.

<a id="r2"></a>**R2.** The development manifest lists the entries of the published manifest, each as written there, under a name of its own. The gate-list check holds this. It also holds the kit's settings to R1. A new module is added to both manifests.

<a id="r3"></a>**R3.** A repository that develops a marketplace never declares it under the published name. Live mode of the install guide registers a clone's development manifest and installs under its name. So the published name always means the GitHub source, on every machine.

<a id="r4"></a>**R4.** These rulings replace words of five accepted rulings. Those records stay as they were accepted.

1. R1 of [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md#r1): the marketplace's name, and the `directory` source.
2. R4 of [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md#r4): the name in the switch key.
3. R2 of [dec-0092-rename-to-claude-constitution-layer-kit](dec-0092-rename-to-claude-constitution-layer-kit.md#r2): the words "in the kit's own settings". Its words "in a project's alike" now hold for a working install. A project in live mode enables under the development name.
4. R2 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r2): the name the settings enable under.
5. R3 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r3): the `directory` source. Also its words that other marketplaces are not read. The gate-list check now reads the published name there, to refuse it.

<a id="r5"></a>**R5.** A branch cut before this change still declares the published name. A session that starts on such a checkout points the published name at the clone again, for every project on the machine. So `main` is merged into such a branch before a session runs there.

## What the tests showed, and what they could not

A kit session and a project's session were started in turn, in both orders. The kit loaded its clone's files every time, and an edit there reached the next session with no reinstall. The project loaded the published version from GitHub every time. No start overwrote an entry. Live mode through the development manifest ran a clone's files in place. A session in a worktree registered the main checkout's manifest, also where the worktree's session started first. All of this is on the pinned version, 2.1.282, on 2026-11-17.

The tests ran with no login, from the command line. A logged-in session, the desktop app's own start and two sessions open at once were not tried. The first sessions of the kit after this change are that test. This is a finding of the day, and no plan item waits on it.

Two effects follow once, on a machine that already ran the kit. Each plugin's data folder is keyed by the plugin's id, so the kit's sessions start with fresh ones. And a user's old entry of the published name stays a folder until a project declares the name from GitHub.

## Applied

The commits of this record's branch apply every ruling. The development manifest stands, with the twelve modules. The kit's settings declare it and enable the modules under its name. The gate-list check holds both, with new cases in its self-test. The session-conduct paragraph of the guide, the install guide and the two guide pages say what the kit now does. The record is born `inactive`.

## Carry list

1. R1 — [CLAUDE.md](../../CLAUDE.md), the opening paragraph of "Session conduct"; [the kit's settings](../../.claude/settings.json); [the development manifest](../../.claude-plugin/dev-marketplace.json).
2. R2 — [the gate-list page](../guide/gate-list-and-ci.md); [the gate-list check](../../scripts/check-gate-lists.py), its docstring. Also [the module-development page](../guide/developing-a-module.md#s1), step 1.
3. R3 — [§3 of the install guide](../../INSTALL.md#s3), the items "Live mode" and "Team"; [§2 of that guide](../../INSTALL.md#s2), steps 2 and 3.
4. R4 — history only: which words of two accepted records R1 replaces, and those records stay as they were accepted.
5. R5 — [CLAUDE.md](../../CLAUDE.md), the opening paragraph of "Session conduct".
