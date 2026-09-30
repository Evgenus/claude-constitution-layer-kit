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

[Requirements A12.1 to A12.3](../requirements.md#a12) name a gate in the kit's CI: a module installs on a bare repository and operates there with its defaults alone, the kernel and that one module forming a working install. After [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md) the kit had CI, but [rollout step 10](../rollout-plan.md#s10) still listed the install as unwired, and no text said what the install run does. On 2026-10-01 the decider asked to wire it. The session tried the platform's install on Claude Code 2.1.282, in a scratch folder with an empty configuration folder. `claude plugin marketplace add <kit>` and `claude plugin install <module>@constitution-kit` worked with no login. The install copied the module into the configuration's plugin cache, the link to the shared gate code arriving as a real directory, and the module's hook and scan exited green on a bare repository holding only the kernel. The CLI installs from npm as `@anthropic-ai/claude-code`, which needs Node 22. The question below was put in chat with lettered options; the pick was the letter.

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

**R1.** `scripts/check-bare-install.py --module <name>` is the install gate of [requirements A12.1 to A12.3](../requirements.md#a12). In throwaway folders it makes a bare repository — `git init`, the kit's kernel copied to `docs/constitution/` and committed, no `constitution.yaml` — and an empty Claude configuration folder, then runs `claude plugin marketplace add <kit>` and `claude plugin install <module>@constitution-kit`.

**R2.** In the installed copy the check is red when a symbolic link is left, when a hook of `hooks/hooks.json`, run in exec form on a sample event of its kind with `CLAUDE_PLUGIN_ROOT` set to the copy, exits other than 0 on the bare repository, and when a scan the module declares in its enforcement section exits other than 0 there. A missing `claude` or `git`, or an install the CLI refuses, is a configuration failure, exit 1. Its `--self-test` proves the checks of the installed copy on throwaway plugin folders.

**R3.** The list's gate group holds `bare-install`, the self-test, and one entry `install-<module>` per module, so CI runs each module's install as its own job. Only those jobs install Node 22 and Claude Code, pinned at 2.1.282 from npm.

**R4.** On Claude Code 2.1.282 a relative-path entry of a marketplace added from a local directory is installed by copy into the plugin cache, not loaded in place: the link to the shared gate code, which leads outside the plugin, arrives as a real directory, and a link leading within the plugin stays a link. Observed 2026-10-01; limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4) states it, and every CI run holds it.

**R5.** The local-directory half of the two-install proof of rollout step 10 is done by R1 on every run; the install from the git remote stays pending there.

## Applied

The change that adds this record applies every item that binds: the script, the list's entries and the workflow in the commit before the record's, the rest in the record's own. So the record is born `inactive`.

## Carry list

1. R1, R2 — [the install check](../../scripts/check-bare-install.py); [requirement A12.1](../requirements.md#a12-1) and [A12.2](../requirements.md#a12-2); step 5 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the intent page](../../INTENT.md).
2. R3 — [the list script](../../scripts/gate-list.sh); [the workflow](../../.github/workflows/gates.yml).
3. R4 — limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4); [the install check](../../scripts/check-bare-install.py).
4. R5 — pending: [rollout step 10](../rollout-plan.md#s10).
