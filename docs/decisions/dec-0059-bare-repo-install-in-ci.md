---
id: dec-0059-bare-repo-install-in-ci
type: task-record
title: CI installs each module alone through Claude Code on a bare repository, one job per module, and holds that its hooks and scans pass there with no link left
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# CI installs each module alone through Claude Code on a bare repository, one job per module, and holds that its hooks and scans pass there with no link left

## Context

[Requirements A12.1 to A12.3](../requirements.md#a12) name a gate in the kit's CI: a module installs on a bare repository and operates there with its defaults alone, the kernel and that one module forming a working install. After [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md) the kit had CI, but [rollout step 10](../rollout-plan.md#s10) still listed the install as unwired, and no text said what the install run does. On 2026-10-01 the decider asked to wire it. The session tried the platform's install on Claude Code 2.1.282, in a scratch folder with an empty configuration folder. `claude plugin marketplace add <kit>` and `claude plugin install <module>@claude-constitution-layer-kit` worked with no login. The install wrote a copy of the module into the configuration's plugin cache, the link to the shared gate code arriving as a real directory. The copy's hook and scan exited green on a bare repository holding only the kernel. The CLI installs from npm as `@anthropic-ai/claude-code`, which needs Node 22. The question below was put in chat with lettered options; the pick was the letter.

## Options

- **A. A real install, one job per module.**
  - **Pros:** what the rows name, kernel plus one module on defaults; each module its own check; a red names its module.
  - **Cons:** eleven more billed minutes per run; Claude Code installed eleven times.
- **B. A real install, one job for all modules.**
  - **Pros:** about one more billed minute per run.
  - **Cons:** one check for eleven modules; slower.
- **C. A simulated install, no Claude Code.**
  - **Pros:** no external tool; fast.
  - **Cons:** it proves the kit's idea of an install, not the platform's; the link fact stays untested.

## Recommendation

A, recommended by the session: the faithful reading of the rows, and the visibility the decider chose for the rest of CI.

## Choice

A, chosen by the decider in chat on 2026-10-01.

## Ruling

<a id="r1"></a>**R1.** `scripts/check-bare-install.py --module <name>` is the install gate of [requirements A12.1 to A12.3](../requirements.md#a12). In throwaway folders it makes a bare repository — `git init`, the kit's kernel copied to `docs/constitution/` and committed, no `constitution.yaml` — and an empty Claude configuration folder, then runs `claude plugin marketplace add <kit>` and `claude plugin install <module>@claude-constitution-layer-kit`.

<a id="r2"></a>**R2.** What the kit's source of the module declares is held in its installed copy. The check is red when a link of the source leads inside the module, or is left a link, is missing or arrives with other files or bytes than its target in the copy, and when the copy holds a link the source lacks. It is red when the copy lacks the source's hooks file; when a hook of the source's `hooks/hooks.json`, run from the copy in exec form on a sample event of its kind with `CLAUDE_PLUGIN_ROOT` set to the copy, exits other than 0 on the bare repository, or exits 0 while the JSON on its standard output blocks, denies, asks or stops; when a scan the source declares in its enforcement section exits other than 0 there; and when Claude Code refuses to install the module. A missing `claude` or `git`, or a marketplace the CLI cannot add, is a configuration failure, exit 1. The run holds the case of an absent dials file; a module with neither hook nor scan is held on its links alone. Its `--self-test` proves the checks of an installed copy on throwaway source and copy folders.

<a id="r3"></a>**R3.** The list's gate group holds `bare-install`, the self-test, and one entry `install-<module>` per module, so CI runs each module's install as its own job. Only those jobs install Node 22 and Claude Code, pinned at 2.1.282 from npm.

<a id="r4"></a>**R4.** Installing a relative-path entry of a marketplace added from a local directory writes a copy into the plugin cache, which a session loading that entry in place does not run, as research [res-0008-const-interaction](../research/res-0008-const-interaction.md) p14 recorded. In that copy, on Claude Code 2.1.282, the link to the shared gate code arrives as a real directory, observed 2026-10-01, as p14 had recorded file links dereferenced on 2026-09-25; R1 holds that copy on every run. This replaces the reading of limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4), re-read 2026-09-23, that such an entry "is not copied". This widens its fallback to a link the kit's install check shows skipped, kept as a link, or arrived with other files or bytes than its target.

<a id="r5"></a>**R5.** The two-install proof of rollout step 10 stays pending: the install from the git remote, and the session's loading in place of a local-directory entry.

<a id="r6"></a>**R6.** R3 narrows R4 of [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md#r4), that a kit check's entry runs its `--self-test` after its plain run: the install check's plain run is one entry per module, so its self-test is an entry of its own, `bare-install`.

## Applied

The change that adds this record applies every item that binds: the script, the list's entries and the workflow in the commit before the record's, the rest in the record's own. So the record is born `inactive`.

## Carry list

1. R1, R2 — [the install check](../../scripts/check-bare-install.py); [requirement A12.1](../requirements.md#a12-1) and [A12.2](../requirements.md#a12-2); step 5 of "Developing a module" in [CLAUDE.md](../guide/developing-a-module.md#s5); [the intent page](../../INTENT.md).
2. R3 — [the list script](../../scripts/gate-list.sh); [the workflow](../../.github/workflows/gates.yml).
3. R4 — limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4); the platform-fact items of four module documents, [`const-catalogs`](../../modules/const-catalogs/MODULE.md#t6), [`const-decision-records`](../../modules/const-decision-records/MODULE.md#t6), [`const-meta-types`](../../modules/const-meta-types/MODULE.md#t6) and [`const-locations`](../../modules/const-locations/MODULE.md#t6); the replaced reading is history.
4. R5 — pending: [rollout step 10](../rollout-plan.md#s10).
5. R6 — [the list script](../../scripts/gate-list.sh); the narrowing of dec-0058's R4 is history.
