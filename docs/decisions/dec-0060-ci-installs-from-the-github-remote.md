---
id: dec-0060-ci-installs-from-the-github-remote
type: task-record
title: CI installs each module from the kit's GitHub remote at the change's branch, pinned to the commit under test, in place of the local-directory install
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# CI installs each module from the kit's GitHub remote at the change's branch, pinned to the commit under test, in place of the local-directory install

## Context

[dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md) installed each module in CI from the kit's working folder, added as a local-directory marketplace. A session runs such an entry from its source, so the cache copy that install writes is one no session runs. [Rollout step 10](../rollout-plan.md#s10) also asked for the install from the marketplace's git remote, the route a consumer takes, which must leave the link to the shared gate code a real directory. On 2026-10-01 the decider asked to wire it. The platform's [hosting page](https://code.claude.com/docs/en/plugins/host-marketplace) says a branch or tag is pinned with `owner/repo#<ref>`, that Claude Code has no git token of its own and clones with the credentials the machine holds, and that `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` makes it clone over HTTPS. The session installed `const-meta-types` from `Evgenus/constitution-kit#main` with an empty configuration folder and no login: the install came from commit `77d5e28`, left no link, and the module's hook and scan exited green on a bare repository. The question below was put in chat with lettered options; the pick was the letter.

## Options

- **A. Eleven more jobs, one per module, from the GitHub remote, beside the local-directory ones.**
  - **Pros:** both installs of step 10 held for each module.
  - **Cons:** about eleven more billed minutes per run; the local-directory copy it keeps is one no session runs.
- **B. One more job installing every module from the GitHub remote.**
  - **Pros:** about two more billed minutes per run.
  - **Cons:** one check for eleven modules.
- **C. The eleven install jobs switch to the GitHub remote in CI; a local run keeps the working folder.**
  - **Pros:** no extra cost; CI tests the copy a consumer runs; one module per check.
  - **Cons:** CI no longer holds the local-directory copy; each job depends on cloning from GitHub; a pull request from a fork would have no branch to clone.

## Recommendation

C, recommended by the session: it holds the install consumers will use, at no extra cost, and drops a copy nothing runs.

## Choice

C, chosen by the decider in chat on 2026-10-01.

## Ruling

**R1.** In the kit's CI, each `install-<module>` job installs the module from the kit's GitHub remote at the change's branch, `<repository>#<branch>` — the pull request's head branch, or `main` on a push to it — over HTTPS, with git credentials set from the job's own token. Run by hand, the check installs from the working folder. `scripts/check-bare-install.py` takes the source from `--from`, else from `CONSTITUTION_KIT_INSTALL_FROM`, else the working folder.

**R2.** The install must come from the commit under test: the job checks out the change's head commit, and the check, given that commit by `--commit` or `CONSTITUTION_KIT_INSTALL_COMMIT`, is a configuration failure when the install record names another — the branch moved during the run, and the job is run again.

**R3.** R1 replaces the local-directory marketplace of R1 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md) in CI, and so its R4's "R1 holds that copy on every run": the local-directory copy was observed on 2026-10-01 and is not held since. The first install of the two-install proof of rollout step 10, from the git remote, is held by R1 on every run.

**R4.** The session's loading in place of a local-directory entry, the rest of that proof, stays pending.

## Applied

The change that adds this record applies every item that binds: the script and the workflow in the commit before the record's, the rest in the record's own. So the record is born `inactive`.

## Carry list

1. R1, R2 — [the install check](../../scripts/check-bare-install.py); [the workflow](../../.github/workflows/gates.yml); [requirement A12.1](../requirements.md#a12-1).
2. R3 — limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4); the narrowing of dec-0059's R1 and R4 is history.
3. R4 — pending: [rollout step 10](../rollout-plan.md#s10).
