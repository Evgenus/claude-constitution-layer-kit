---
id: dec-0057-pr-flow-merge-names-the-yes
type: task-record
title: The kit has a PR flow — a private GitHub remote, main held by a ruleset, and the yes named in the merge commit, which is the decider's own merge where no second human approves
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit has a PR flow — a private GitHub remote, main held by a ruleset, and the yes named in the merge commit, which is the decider's own merge where no second human approves

## Context

On 2026-09-30 the decider asked to publish the kit to GitHub. The kit had no remote. [Rollout step 10](../rollout-plan.md#s10) planned a remote with a protected main and a PR flow, with the yes moving from the commit message to PR approval ([dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md)). Three facts stood in the way. On GitHub, a pull request's author cannot approve it: the docs on [approving a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews) say "Pull request authors cannot approve their own pull requests." The kit has one human, the decider, who is also the author of every pull request. And no consumer project has run its live proof yet ([rollout step 5](../rollout-plan.md#s5)). The three questions below were put in chat, one per message, each with lettered options; the pick was the letter.

## 1. Who can see the repository

- **A. Public now.**
  - **Pros:** others can install the kit; branch protection is free on a public repository.
  - **Cons:** draft modules with no consumer-live proof are public; the author's email in every commit is public; a license must be chosen first.
- **B. Private now.**
  - **Pros:** nothing is exposed.
  - **Cons:** no one else can install the kit.
- **C. Private now, public after the first consumer-live proof.**
  - **Pros:** the public version is proven in a real project; it follows the rollout order.
  - **Cons:** a second step later.

The session recommended A, since it took the decider's plan to be GitHub Free, where a private repository has no branch protection. <a id="r1"></a>**R1.** C, chosen by the decider in chat on 2026-09-30: the repository is private and is made public after the first consumer project's live proof. The license and whether the author's email stays in the history are decided at that step. The decider holds GitHub Pro, so a private repository can be protected.

<a id="r2"></a>**R2.** The repository `Evgenus/claude-constitution-layer-kit` was created on 2026-09-30 as the clone's `origin`, and `main` and all 77 local branches were pushed, at the decider's word in chat.

## 2. When to protect main

- **A. No protection until the repository is public.**
  - **Pros:** no settings and no rule change now.
  - **Cons:** a force push or a deletion on the remote can remove history.
- **B. The full PR flow now.** A ruleset asks for a pull request; every change goes through one.
  - **Pros:** rollout step 10's PR flow done early; the shared main fully held.
  - **Cons:** the yes must move to the pull request, where the author cannot approve, so the rule must change first; a pull request for every change.
- **C. Protection only.** Force push and deletion blocked; merges pushed directly.
  - **Pros:** it guards against losing history, in minutes, with no rule change.
  - **Cons:** a bad merge can still be pushed; step 10 stays open.

The session recommended C. <a id="r3"></a>**R3.** B, chosen by the decider in chat on 2026-09-30: the shared `main` on GitHub is held by a repository ruleset — a pull request before every merge, with no approval required, since the only human is the author; no force push; no deletion; no one on its bypass list. The repository allows merge commits only, squash and rebase off, and does not delete a head branch after its merge.

<a id="r4"></a>**R4.** A work reaches `main` as a pull request from its branch `work/<name>`, merged with a merge commit whose subject is `Work: <name>`: `gh pr merge <n> --merge --subject "Work: <name>"`. The branch is pushed, and it is kept on the remote after the merge as it is in the clone. A local `main` follows the remote only by fast-forward.

<a id="r5"></a>**R5.** `scripts/setup-clone.sh` sets a third setting, `pull.ff` = `only`, and its check asks for it. With `merge.ff` = `false` alone, a plain `git pull` onto `main` makes a merge commit of its own, tried on git 2.54 on 2026-09-30.

<a id="r6"></a>**R6.** The deferred item R7 of [dec-0032-work-starts-on-a-branch](dec-0032-work-starts-on-a-branch.md#r7) is now real: whatever was done to a local `main` by the ways its R6 names reaches the shared one only through a pull request's merge. A local `main` stays unheld, and the hook stays as the fast local check.

## 3. How the yes is given when the decider is the pull request's only human

- **A. The merge is the yes.** The decider merges; the merge commit names the yes and carries the trailers.
  - **Pros:** it works for one person; the yes stays in git, where the carry-lists gate reads it; a solo consumer can follow the same rule.
  - **Cons:** GitHub shows no approval; the ruleset cannot force a yes, so the rule and the trailer's gate hold it.
- **B. The yes as a comment on the pull request.**
  - **Pros:** it is visible on the pull request.
  - **Cons:** it lives on GitHub only, where no gate reads it and a clone loses it; the kernel changes anyway.
- **C. A second account or a bot approves.**
  - **Pros:** a real approval shows; the kernel text stays.
  - **Cons:** one person acting as two reviewers is an approval with nothing behind it, against [law 5 of CLAUDE.md](../../CLAUDE.md#law-5).
- **D. The yes stays in a commit on the branch.**
  - **Pros:** the smallest rule change.
  - **Cons:** the yes comes before the pull request's checks; the kernel wording changes anyway.

The session recommended A. <a id="r7"></a>**R7.** A, chosen by the decider in chat on 2026-09-30. The `process` row of [kernel §4](../constitution/CONVENTIONS.md#k4) now reads: one human yes on the change, named in the commit that lands it — where a PR flow exists, the commit that merges the pull request, the yes being its approval or, where no second human reviews it, the decider's own merge.

<a id="r8"></a>**R8.** In the kit, the decider gives the yes by merging the pull request, or by saying it in chat and having the session merge in the decider's name. The merge commit names the yes and carries the `Accepted:` and `Carry-Audit:` trailers in its last paragraph, written with `--body`. It is the commit that lands the change and completes it in the sense of rule 5 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5): a yes given in chat is complete with it, and the window for corrections closes there. A decider who merges on the forge's page writes the yes and the trailers into the merge message there. From the merge of the kit's first pull request on, every `Accepted:` and `Carry-Audit:` trailer stands on a merge commit, never on a branch commit: a wrong receipt is mended by accepting again in the merge commit of a new pull request, and a `product` record's lone `Carry-Audit:` trailer stands on the merge commit too.

<a id="r9"></a>**R9.** An audit finding is justified in a commit message of the change, the merge commit included — never only in the pull request's description, which git does not keep.

<a id="r10"></a>**R10.** The review of an `architecture` record is complete with the merge that accepts the record, once the decider has said so, in chat or by that merge.

<a id="r11"></a>**R11.** R7 and R8 narrow the sunset of [dec-0016-yes-on-the-change](dec-0016-yes-on-the-change.md) — PR approval on a protected main from rollout Phase D — and the clause of R2 of [dec-0032-work-starts-on-a-branch](dec-0032-work-starts-on-a-branch.md#r2) that puts the yes on a branch commit until the kit has a PR flow. R4 replaces that R2's merge command, `git merge --no-ff work/<name>`, and R5 adds a third setting to the two of [dec-0032-work-starts-on-a-branch](dec-0032-work-starts-on-a-branch.md#r5)'s R5. R6 withdraws the clause of [dec-0032-work-starts-on-a-branch](dec-0032-work-starts-on-a-branch.md#r7)'s R7 that a pull request's review sees the content of a merge concluded by hand: no approval is required, so no review is promised. The acceptances made until the merge of the kit's first pull request, each on the branch commit that named the yes, stand.

<a id="r12"></a>**R12.** A record born `active` because it grows while its change is made is `inactive` by the last commit of its branch, which the merge that names its yes or ends its review lands: a pull request's merge edits no file. This replaces the moment R10 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r10) set, the commit that names its yes or ends its review.

## Applied

The change that adds this record applies every item that binds — R5 and the hook's text in the commit before the record's, the rest in the record's own — so the record is born `inactive`. The fixes of its carry audit corrected the record and the current-state documents together, before its yes. The ruleset and the repository settings of R3 are set on GitHub before the pull request that carries this change is merged; that merge is the flow's first use.

## Carry list

1. R1 — pending: [rollout step 10](../rollout-plan.md#s10).
2. R2 — history only: the creation and the first push.
3. R3, R4, R6 — the rule "Work starts on a branch" in session conduct of [CLAUDE.md](../../CLAUDE.md); R4 also [the hook](../../scripts/git-hooks/prepare-commit-msg).
4. R5 — [the setup script](../../scripts/setup-clone.sh); [its fixture](../../scripts/git-hooks/tests/run.sh); the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md).
5. R7 — [kernel §4](../constitution/CONVENTIONS.md#k4); [law 9 of CLAUDE.md](../../CLAUDE.md#law-9); [the record skill](../../modules/const-decision-records/plugin/skills/record-decision/SKILL.md).
6. R8 — [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), and for a `product` record [its rule 15](../policies/plc-0004-decision-records.md#r15); the rule "Work starts on a branch" in [CLAUDE.md](../../CLAUDE.md); step 8 of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md).
7. R9 — [rule 2 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r2); step 6 of "Developing a module" in [CLAUDE.md](../guide/developing-a-module.md#s6); step 6 of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md).
8. R10 — [rule 15 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r15).
9. R11 — [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5), the acceptances that stand; the narrowing and the withdrawal are history, stated where R4 to R8 are carried.
10. R12 — [rule 11 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r11), which the status slot of `templates/decision-record.md` follows; the replacement of the moment R10 of dec-0039 set is history.
