---
id: dec-0101-bootstrap-on-a-branch-with-two-questions
type: task-record
title: The bootstrap runs on a branch, its yes named in the merge, and asks whether policies are a catalog and whether a style guide is kept
status: active
stakes: process
decider: Eugene Chernyshov
---

# The bootstrap runs on a branch, its yes named in the merge, and asks whether policies are a catalog and whether a style guide is kept

## Context

On 2026-10-23 a session bootstrapped the first consumer project by section 2 of [the install guide](../../INSTALL.md#s2), at kit commit 6b63527, with the modules loaded in live mode. It was each module's consumer-live proof ([step 5 of the rollout plan](../rollout-plan.md#s5)). All ten scans ended green, and the session reported eleven findings. The decider then had the project reset to its empty first commit, to be bootstrapped again once the kit had addressed them:

1. **F1.** The guide said "Commit after each step", but its step 7 put record #1 in the same commit as the kernel copy.
2. **F2.** The guide wrote the policies before `constitution.yaml`. The creation command of [`const-locations`](../requirements.md#const-locations) refuses to run without that file, and the skill `new-kind` writes it first.
3. **F3.** Step 7 said to create the record through the creation command alone. The command wrote `status: active` and no `stakes` or `decider`, through the shell, so no hook saw it, and the record scan was red. Module [`const-locations`](../requirements.md#const-locations) names that very act a violation in its section 8.
4. **F4.** The guide said no document is written without its guard, "the kernel copy included". The copy is made through the shell and passes no hook; only the scans check it.
5. **F5.** The skill of [`const-styling`](../requirements.md#const-styling) asks a repository with no style guide to create one, with a policy of its own and a style rule in every policy. The guide named none of this, and the style scan stays green without a guide.
6. **F6.** Step 8 asked for `/plugin list` and the Errors tab of `/plugin`, which a session in the desktop app cannot open.
7. **F7.** The kernel's language departure allowed `grade` and `sentence` only, so every scan printed passive-voice notes on a copy nobody may edit.
8. **F8.** After a write, some gates printed a green line and others printed nothing, so the session could not tell whether the record gate had run.
9. **F9.** With no template, the creation command writes the whole title as the heading.
10. **F10.** The turn-end hook of [`const-task-close`](../requirements.md#const-task-close), at `severity: block`, asked for a commit while step 9 waited for the yes that [kernel §4](../../kernel/CONVENTIONS.md#k4) asks of a `process` record. Following it would have landed the record before its yes.
11. **F11.** The guide used plain policy ids without asking. The decider ruled in chat on 2026-10-23 that whether policies are a catalog is a question the install asks before the first policy, since a later change renames each policy, its dials key and every citation of it.

Six of them are fixes of the guide's text, routine by [rule 6 of plc-0011-install-guide](../policies/plc-0011-install-guide.md#r6): F1, F2, F3, F4, F6 and F7. F9 is no fault: the heading equal to the title is the module's design, which its messages say. Four questions remained, F10, F11, F5 and F8, and the session put them one per message in chat on 2026-10-23, in that order. The decider chose one change for all eleven, with this one record. Sections 1 to 4 hold the questions.

## 1. Where the yes of a bootstrap lands

[Kernel §4](../../kernel/CONVENTIONS.md#k4) names the yes "in the commit that lands it". The guide's step 9 committed straight onto `main`, so the dirty-tree hook asked for the very commit that would land the record before its yes. Every later `process` record of a project meets the same clash.

- **A. The bootstrap runs on a branch, and the yes is named in the merge.** The guide cuts `work/adopt-kernel`; each step commits on it; the kernel copy moves to just before the record, so the two share one commit; the merge onto `main` names the yes. The skill `commit-before-edit` gains one sentence: work that waits for its yes is committed on its branch.
  - **Pros:** it matches [kernel §4](../../kernel/CONVENTIONS.md#k4) and the kit's own practice; the hook stays at `block` and is right every time; "commit after each step" becomes true; later records of the project follow the same path.
  - **Cons:** a new project starts with a branch and a merge; the guide and one skill both change.
- **B. `severity: warn` during the bootstrap, switched to `block` in the final commit.**
  - **Pros:** no branch; a small change to the guide.
  - **Cons:** the dirty-tree guard is off during the riskiest stretch; the switch back is a step someone can forget; it does nothing for later records.
- **C. Ask for the yes before the record is written, then commit at once.**
  - **Pros:** no branch and no dial change.
  - **Cons:** the yes comes before the change exists, while [kernel §4](../../kernel/CONVENTIONS.md#k4) asks for it on the change; if the session ends mid-way, the yes covers work nobody saw.

The session recommended A: it is the one option that fixes the clash for every later record and not only for the bootstrap, and it follows the kernel's own words. The decider chose A in chat on 2026-10-23.

<a id="r1"></a>**R1.** The bootstrap of the install guide runs on a branch of its own, `work/adopt-kernel`, cut right after the repository's first commit on `main`. Each step commits on that branch. The last step merges it onto `main` with `--no-ff`, after the decider's yes, and the merge commit names the yes: it is the commit that lands record #1.

<a id="r2"></a>**R2.** The kernel copy is made just before record #1, and the two land in one commit, so the record is born `inactive`.

<a id="r3"></a>**R3.** A change that waits for a human yes is committed on its own branch at the end of a turn, its yes named in the merge that lands it; it is never left uncommitted to wait. The skill `commit-before-edit` of module [`const-task-close`](../requirements.md#const-task-close) says so, and its hook is unchanged.

## 2. Whether the list of policies is a catalog

The decider had ruled that the install asks this before step 5. What was left was the default the question proposes, since [`const-questions`](../requirements.md#const-questions) asks a question with a sensible default as "default X: accept or override?".

- **A. Default: numbered.** Each policy is named `plc-<nnnn>-<slug>`, with a `plc` catalog of [`const-catalogs`](../requirements.md#const-catalogs) in the dials; plain ids are the override.
  - **Pros:** the kit's own practice ([dec-0034-research-and-policies-numbered](dec-0034-research-and-policies-numbered.md)); a number never collides when two people add policies at once; the catalog gate checks every policy's name from the first one.
  - **Cons:** longer ids in the dials keys and in every citation; one more catalog for a new user to learn on the first day.
- **B. Default: plain ids,** as the guide showed; numbered is the override.
  - **Pros:** short, readable keys; nothing new to learn at install; the guide's block stays the default.
  - **Cons:** it differs from the kit's own practice; two policies added at once can take one name; nothing checks policy names.
- **C. No default: the guide shows both forms, and the user chooses.**
  - **Pros:** neither form is favoured, so the choice is fully deliberate.
  - **Cons:** it goes against the default-with-override rule of `const-questions`; one more choice with nothing to lean on, for a reader new to the kit.

The session recommended A, the form the kit has tried on itself. The decider chose C in chat on 2026-10-23, and said what the question is: whether the list of policies is a catalog. That is a yes or a no about the project's documents, which the user answers, not a form the guide should lean either way.

<a id="r4"></a>**R4.** Before the dials file and before any policy, the install guide asks "Is the list of policies a catalog?" and proposes no default. On yes, each policy is named `plc-<nnnn>-<slug>`, and `const-catalogs.catalogs` gains a `plc` entry after `dec` over the policies' territory. On no, each policy has a plain kebab-case id. The answer is written in record #1.

## 3. Whether the project keeps a style guide

The skill of `const-styling` creates a guide only when it is first loaded, and a guide made after the bootstrap means a style rule added to every policy written before it. The style scan never says a guide is missing.

- **A. The install asks, with no default: "Does this project keep a style guide?"** On yes, the bootstrap adds the guide, its policy, the `const-styling.guides` dial, and a style rule in the root policy and in each policy.
  - **Pros:** the same kind of question as section 2, asked while there are only three policies to change; nothing is created that the user did not choose.
  - **Cons:** one more question at install; with yes, two more documents in the first change.
- **B. The bootstrap always creates the guide and its policy.**
  - **Pros:** every project follows the module's procedure from the first commit; no question to answer.
  - **Cons:** a project that does not want the defaults gets a guide it must remove; the first change grows for everyone.
- **C. The install only says the guide comes later, when the skill first needs it.**
  - **Pros:** the smallest change to the guide.
  - **Cons:** every policy written by then needs a style rule added later; the scan never reminds anyone, so the guide may never come.

The session recommended A: it follows the ruling of section 2, a choice made at install, when it costs least, and only by the user. The decider chose A in chat on 2026-10-23.

<a id="r5"></a>**R5.** Beside the question of R4, the install guide asks "Does this project keep a style guide?" and proposes no default. On yes, the skill `style-defaults` of `const-styling` is loaded before the first policy and creates the guide, its policy and the `guides` dial, and every policy carries a style rule. On no, no guide is written. The answer is written in record #1.

## 4. Whether a green write reaches the model

A gate that passes a write with nothing to note prints its green line on plain standard output, which the platform writes to its debug log; a run with notes hands the line on as context ([kit-shared-gate-code §3](../../shared/GATE.md#g3), the row of `G2`).

- **A. No: keep the silence, and the install guide says what it means,** and names the scans as the way to see every verdict.
  - **Pros:** no context spent on writes that pass cleanly, which are most of them; no change to code, so no new release of the shared package and no new eval runs.
  - **Cons:** after one write, the model still cannot see which gates ran; it learns that only from a scan.
- **B. Yes: every green write hands its line on as context.**
  - **Pros:** each write shows which gates ran; a gate that failed to load shows as a missing line.
  - **Cons:** up to eight more lines of context on every write; a change to the shared code, so a new release, a raised `REQUIRES` in every module and new eval receipts for every module.
- **C. Only the gates that guard a record hand their green line on.**
  - **Pros:** the gates the bootstrap missed become visible; less noise than B.
  - **Cons:** two rules for one event; the same release and eval costs for the modules it touches; which gates count becomes a judgment.

The session recommended A: the silence is a decision the kit made to save context, and it was proved live; what failed was the explanation. The decider chose A in chat on 2026-10-23.

<a id="r6"></a>**R6.** A gate that passes a write with nothing to note stays silent to the model. The install guide's step 8 says so, and names the scans as the place where every gate's verdict shows.

## Applied

The record was born `active`, and the change that creates it applies its rulings: the install guide's section 2 is rewritten, and the skill `commit-before-edit` of `const-task-close` gains its sentence, with boundary example 14 in that module's section 8. In the guide, the dials file and the kernel copy swap places: the dials file, step 6 before this change, is step 4, and the kernel copy, step 4 before, is step 6. A record accepted earlier that names step 4 or step 6 of the bootstrap means the other one now; the other steps keep their numbers. The commit that fixes what the carry audit finds sets the record `inactive`.

## Carry list

1. R1 — [the install guide](../../INSTALL.md#s2), the opening of section 2 and its steps 1 and 9.
2. R2 — [the install guide](../../INSTALL.md#s2), steps 6 and 7 of section 2.
3. R3 — [the skill commit-before-edit](../../modules/const-task-close/plugin/skills/commit-before-edit/SKILL.md), its third moment; [const-task-close §8](../../modules/const-task-close/MODULE.md#t8), example 14.
4. R4 — [the install guide](../../INSTALL.md#s2), step 4 of section 2, and step 7 for the answer.
5. R5 — [the install guide](../../INSTALL.md#s2), steps 4, 5 and 7 of section 2.
6. R6 — [the install guide](../../INSTALL.md#s2), step 8 of section 2.
