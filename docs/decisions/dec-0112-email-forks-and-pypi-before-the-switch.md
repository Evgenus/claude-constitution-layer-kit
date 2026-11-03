---
id: dec-0112-email-forks-and-pypi-before-the-switch
type: task-record
title: Before the switch, the email stays in the history, fork pull requests run the same CI, and the shared package stays off PyPI
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Before the switch, the email stays in the history, fork pull requests run the same CI, and the shared package stays off PyPI

## Context

Step 5a of [the rollout plan](../rollout-plan.md#s5a) makes the repository public. Its first three items are decisions made before the switch: whether the author's email stays in the history (5a.1), how a pull request from a fork is checked (5a.2), and whether the shared package is also published on PyPI (5a.3). Item 5.2 closed on 2026-11-03, so the three came due. The session put them in chat on 2026-11-03, one per message.

## 1. The author's email in the history

The author's address stood 3,323 times as author or committer in the 1,711 commits on 2026-11-03, and in no tracked file. It was already the public email of the author's GitHub profile. A rewrite of the history changes every commit hash: those of the two tags of the shared package, which every consumer's install pins, the pins of the carry audits' receipts, the commits the records and the plan cite, and those the first consumer project's records cite. GitHub keeps a read-only ref for each pull request, which may keep the old commits readable after a rewrite; the session did not verify that.

- **A. Keep everything as it is.**
  - **Pros:** no work; every hash, tag and pin stays valid; the address is public already.
  - **Cons:** the address stands in every commit of a public repository, for good.
- **B. Keep the history, and commit with the GitHub noreply address from now on.**
  - **Pros:** no rewrite; no new commit adds the address.
  - **Cons:** the old entries keep it; hiding it on GitHub also hides it on the profile.
- **C. Rewrite the history to the noreply address before the switch.**
  - **Pros:** a new clone shows no address.
  - **Cons:** every cited hash, both tags and every audit pin break; the ruleset must be lifted for a force push; the pull requests' refs may still hold the old commits.
- **D. Publish a fresh repository with a rewritten history, and keep this one private.**
  - **Pros:** the public copy holds no address.
  - **Cons:** the public hashes match none of the cited ones; the install address and the marketplace move; the public copy has no pull-request history.

The session recommended B: it stops new exposure at no cost to any hash. The decider chose A in chat on 2026-11-03.

<a id="r1"></a>**R1.** The author's email stays in the history: the history is not rewritten, and commits go on carrying the author's address. This is the decision that R5 of [dec-0063-apache-license-with-notice](dec-0063-apache-license-with-notice.md#r5) left to this step.

## 2. A pull request from a fork

The CI workflow runs on `pull_request`, never `pull_request_target`, with `permissions: contents: read`, and uses no secret, only the job's read-only token. The module jobs and the job `install-guide` install from the pull request's head repository and branch. While the repository is private, a fork is private too and that token cannot read it. Once it is public, a fork is public too, so the install should work without a token; that can be proven only after the switch. A fork pull request that changes a module also needs a new eval receipt, made with a Claude subscription in the kit's eval container. GitHub's setting that asks the owner's approval before workflows run for outside contributors exists only for public repositories. On public repositories, standard GitHub-hosted runners cost nothing, and a fork's run takes the owner's concurrent job slots.

- **A. Nothing changes now; the first fork pull request is the signal.** At the switch, GitHub asks approval for all outside collaborators.
  - **Pros:** no machinery for a failure nobody has hit; the workflow is already safe for forks.
  - **Cons:** the first such pull request may wait on a decision; the install from a fork stays unproven until then.
- **B. As A, and the decider makes the receipt of a fork pull request that changes a module.**
  - **Pros:** a contributor knows the path; every receipt comes from one environment.
  - **Cons:** the decider's time and eval runs per such pull request, for a case that has not happened.
- **C. As B, and a throwaway fork proves the install right after the switch.**
  - **Pros:** the one unproven fact is tested first.
  - **Cons:** one more item in step 5a, and a fork and a pull request to clean up.
- **D. No pull requests from forks.**
  - **Pros:** CI only ever runs in this repository's context.
  - **Cons:** it shuts out outside contributions.

The session recommended A: the workflow is safe for forks as it stands, and machinery is earned by friction. The decider chose A in chat on 2026-11-03, after asking who pays for its CI.

<a id="r2"></a>**R2.** A pull request from a fork runs the same CI as any other, and nothing in the workflow changes for it. The change that makes the repository public also sets GitHub to ask the owner's approval before workflows run for all outside collaborators.

<a id="r3"></a>**R3.** Deferred: how the eval receipt of a fork pull request that changes a module is made. Signal: the first such pull request.

## 3. The shared package on PyPI

Every consumer installs the shared package from a git tag, by the line the install guide and each module's install note give, which `scripts/check-copies.py` holds. Once the repository is public, that install needs no credentials. R20 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r20) deferred PyPI to this step. On 2026-11-03 the names `constitution-layer-kit` and `knowledge-layer-kit` were free on PyPI. A version published there can never be reused.

- **A. No PyPI; the git tag stays the one source, until a signal.**
  - **Pros:** no release process to add or keep in step; the install line names its source exactly.
  - **Cons:** the name stays free for anyone.
- **B. Reserve the names with an empty release.**
  - **Pros:** no one else takes them.
  - **Cons:** a package that does nothing; PyPI's naming policy may give the name away on request.
- **C. Publish every release on PyPI from CI, and install from there.**
  - **Pros:** the usual install; the name owned with real content.
  - **Cons:** two sources to keep in step; a new workflow, and every install line and its check change.
- **D. Publish release 2.0.0 by hand once.**
  - **Pros:** the name owned; no workflow.
  - **Cons:** later releases do not reach PyPI, which soon shows a stale version.

The session recommended A: the install line already names its source, and nothing has asked for a release process. The decider chose A in chat on 2026-11-03.

<a id="r4"></a>**R4.** Deferred: publication of the shared package on PyPI; the git tag stays its one source. Signal: a consumer asks for it, or the name `constitution-layer-kit` is taken there. This answers R20 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r20) at this step.

## Applied

The change ticks items 5a.1, 5a.2 and 5a.3 of the plan, adds the approval setting to item 5a.4, adds the waiting item 5a.9 for R3, and gives the PyPI deferral of [kit-shared-gate-code](../../shared/GATE.md#g1) its new signal, with the status matrix's rows. Every item has its home in the commit that creates this record, so the record is born `inactive`.

## Carry list

1. R1 — history only: a decision that changes no file.
2. R2 — pending: [item 5a.4 of the rollout plan](../rollout-plan.md#s5a-4).
3. R3 — pending: [item 5a.9 of the rollout plan](../rollout-plan.md#s5a-9).
4. R4 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts.
