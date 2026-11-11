---
id: dec-0101-bootstrap-on-a-branch-with-two-questions
type: task-record
title: The bootstrap runs on a branch, its yes named in the merge, and asks whether policies are a catalog and whether a style guide is kept
status: inactive
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
10. **F10.** The turn-end hook of [`const-task-close`](../requirements.md#const-task-close), at `severity: block`, asked for a commit while step 9 waited for the yes that [kernel §4](../constitution/CONVENTIONS.md#k4) asks of a `process` record. Following it would have landed the record before its yes.
11. **F11.** The guide used plain policy ids without asking. The decider ruled in chat on 2026-10-23 that whether policies are a catalog is a question the install asks before the first policy, since a later change renames each policy, its dials key and every citation of it.

Five of them are fixes of the guide's text, routine by [rule 6 of plc-0011-install-guide](../policies/plc-0011-install-guide.md#r6): F1, F2, F3, F4 and F6. F9 is no fault: the heading equal to the title is the module's design, which its messages say. Four questions remained, F10, F11, F5 and F8, and the session put them one per message in chat on 2026-10-23, in that order. The decider chose one change for all eleven, with this one record. The session first fixed F7 as a routine edit too. The carry audit found that it changed an accepted ruling, and it became a fifth question. Sections 1 to 5 hold the questions.

## 1. Where the yes of a bootstrap lands

[Kernel §4](../constitution/CONVENTIONS.md#k4) names the yes "in the commit that lands it". The guide's step 9 committed straight onto `main`, so the dirty-tree hook asked for the very commit that would land the record before its yes. Every later `process` record of a project meets the same clash.

- **A. The bootstrap runs on a branch, and the yes is named in the merge.**
  - **The guide cuts `work/adopt-kernel`**;
  - **each step commits on it**;
  - **the kernel copy moves to just before the record**, so the two share one commit;
  - **the merge onto `main` names the yes**.

  The skill `commit-before-edit` gains one sentence: work that waits for its yes is committed on its branch.
  - **Pros:**
    - **it matches [kernel §4](../constitution/CONVENTIONS.md#k4) and the kit's own practice**;
    - **the hook stays at `block` and is right every time**;
    - **"commit after each step" becomes true**;
    - **later records of the project follow the same path**.
  - **Cons:** a new project starts with a branch and a merge; the guide and one skill both change.
- **B. `severity: warn` during the bootstrap, switched to `block` in the final commit.**
  - **Pros:** no branch; a small change to the guide.
  - **Cons:**
    - **the dirty-tree guard is off during the riskiest stretch**;
    - **the switch back is a step someone can forget**;
    - **it does nothing for later records**.
- **C. Ask for the yes before the record is written, then commit at once.**
  - **Pros:** no branch and no dial change.
  - **Cons:**
    - **the yes comes before the change exists**, while [kernel §4](../constitution/CONVENTIONS.md#k4) asks for it on the change;
    - **if the session ends mid-way**, the yes covers work nobody saw.

The session recommended A: it is the one option that fixes the clash for every later record and not only for the bootstrap, and it follows the kernel's own words. The decider chose A in chat on 2026-10-23.

<a id="r1"></a>**R1.** The bootstrap of the install guide runs on a branch of its own, `work/adopt-kernel`, cut right after the repository's first commit on `main`. Each step commits on that branch. The last step merges it onto `main` with `--no-ff`, after the decider's yes. The merge commit names the yes: it is the commit that lands record #1.

<a id="r2"></a>**R2.** The kernel copy is made just before record #1, in the same turn, so that the two land in one commit. If a turn ends between them, the copy is committed on the branch first. Record #1 is born `inactive`: by the commit that creates it, everything it rules is applied on the branch — the dials file and the policies by earlier commits, the kernel copy beside it or just before it — and it lands with them in the merge.

<a id="r3"></a>**R3.** A change that waits for a human yes is committed on its own branch at the end of a turn, its yes named in the merge that lands it. It is never left uncommitted to wait. The skill `commit-before-edit` of module [`const-task-close`](../requirements.md#const-task-close) says so, and its hook is unchanged.

## 2. Whether the list of policies is a catalog

The decider had ruled that the install asks this before step 5. What was left was the default the question proposes, since [`const-questions`](../requirements.md#const-questions) asks a question with a sensible default as "default X: accept or override?".

- **A. Default: numbered.** Each policy is named `plc-<nnnn>-<slug>`, with a `plc` catalog of [`const-catalogs`](../requirements.md#const-catalogs) in the dials; plain ids are the override.
  - **Pros:**
    - **the kit's own practice** ([dec-0034-research-and-policies-numbered](dec-0034-research-and-policies-numbered.md));
    - **a number never collides when two people add policies at once**;
    - **the catalog gate checks every policy's name from the first one**.
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

The skill of `const-styling` creates a guide only when it is first loaded. A guide made after the bootstrap means a style rule added to every policy written before it. The style scan never says a guide is missing.

- **A. The install asks, with no default: "Does this project keep a style guide?"** On yes, the bootstrap adds the guide, its policy, the `const-styling.guides` dial, and a style rule in the root policy and in each policy.
  - **Pros:**
    - **the same kind of question as section 2**, asked while there are only three policies to change;
    - **nothing is created that the user did not choose**.
  - **Cons:** one more question at install; with yes, two more documents in the first change.
- **B. The bootstrap always creates the guide and its policy.**
  - **Pros:** every project follows the module's procedure from the first commit; no question to answer.
  - **Cons:** a project that does not want the defaults gets a guide it must remove; the first change grows for everyone.
- **C. The install only says the guide comes later, when the skill first needs it.**
  - **Pros:** the smallest change to the guide.
  - **Cons:** every policy written by then needs a style rule added later; the scan never reminds anyone, so the guide may never come.

The session recommended A: it follows the ruling of section 2, a choice made at install, when it costs least, and only by the user. The decider chose A in chat on 2026-10-23.

<a id="r5"></a>**R5.** Beside the question of R4, the install guide asks "Does this project keep a style guide?" and proposes no default. On yes, the skill `style-defaults` of `const-styling` is loaded before the first policy and creates the guide, its policy and the `guides` dial, and every policy carries a style rule. On no, no guide is written, and the skill `style-defaults` follows its shipped text as the guide and creates none; record #1 says so, and the policies carry no style rule. The answer is written in record #1. This narrows R5 and R6 of [dec-0044-styling-module-rulings](dec-0044-styling-module-rulings.md#r5) and R6 of [dec-0055-promise-audit-fixes](dec-0055-promise-audit-fixes.md#r6), which bound every policy-governed project to a guide, and [requirement A9.1](../requirements.md#a9-1) with them.

## 4. Whether a green write reaches the model

A gate that passes a write with nothing to note prints its green line on plain standard output, which the platform writes to its debug log. A run with notes hands the line on as context ([kit-shared-gate-code §3](../../shared/MESSAGES.md#g3), the row of `G2`).

- **A. No: keep the silence, and the install guide says what it means,** and names the scans as the way to see every verdict.
  - **Pros:**
    - **no context spent on writes that pass cleanly**, which are most of them;
    - **no change to code**, so no new release of the shared package and no new eval runs.
  - **Cons:** after one write, the model still cannot see which gates ran; it learns that only from a scan.
- **B. Yes: every green write hands its line on as context.**
  - **Pros:** each write shows which gates ran; a gate that failed to load shows as a missing line.
  - **Cons:**
    - **up to eight more lines of context on every write**;
    - **a change to the shared code**, so a new release, a raised `REQUIRES` in every module and new eval receipts for every module.
- **C. Only the gates that guard a record hand their green line on.**
  - **Pros:** the gates the bootstrap missed become visible; less noise than B.
  - **Cons:** two rules for one event; the same release and eval costs for the modules it touches; which gates count becomes a judgment.

The session recommended A: the silence is a decision the kit made to save context, and it was proved live; what failed was the explanation. The decider chose A in chat on 2026-10-23.

<a id="r6"></a>**R6.** A gate that passes a write with nothing to note stays silent to the model. The install guide's step 8 says so, and names the scans as the place where every gate's verdict shows.

## 5. The language of the kernel copy

R10 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r10) ruled that the guide's dials example departs from [`const-language`](../requirements.md#const-language) for `docs/constitution/**`, allowing `grade` and `sentence`, since the kernel met only the kit's own looser thresholds. The bootstrap still saw passive-voice notes on the kernel copy, which a project never edits (F7). The session widened the departure to `passive` as a routine edit, and the carry audit at 387f0f5 found that this changed R10 without a ruling. Measured on 2026-10-23 at the module's defaults, the kernel read at grade 12.17 against a ceiling of 10, held 24 sentences over 25 words, and gave 20 passive-voice notes. The kit keeps `passive: off` for its own text by [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md). The planned descent of its thresholds covers grade and sentence length, not passive voice.

- **A. Allow `passive` too, a ruling here that widens R10.**
  - **Pros:** a project's scans stay quiet about text it cannot change; the project's own documents keep the check; this change stays small.
  - **Cons:** it changes an accepted ruling; the departure grows, and its passive part stays as long as the kit writes in the passive.
- **B. Undo the widening, R10 as it stands.**
  - **Pros:** no accepted ruling changes.
  - **Cons:** about twenty notes on every scan of every new project, real notes lost among them; F7 stays open.
- **C. `const-language.passive: off` in the guide's example.**
  - **Pros:** the setting the kit uses for itself.
  - **Cons:** it silences passive voice on the project's own documents, a check the module keeps on by default; it still needs a ruling.
- **D. Rewrite the kernel in this change to meet the module's defaults, and drop the departure.**
  - **Pros:** no departure at all; the kernel copy is checked at full strictness like every other document; the guide's example loses an entry.
  - **Cons:**
    - **a kernel change**, so the carry audit runs in full over every record ([rule 3 of plc-0002-kernel](../policies/plc-0002-kernel.md#r3));
    - **every rewritten sentence must keep its meaning**;
    - **the recreate of the first project waits for it**.

The session recommended A, to keep this change small and leave the rewrite to a change of its own. The decider asked to fix the language of that one file instead, and chose D in chat on 2026-10-23.

<a id="r7"></a>**R7.** The kernel meets the default thresholds of `const-language` as written: its grade, its sentence length, its two lists of phrases, and no passive-voice note. The guide's dials example carries no departure for the kernel copy. The guide's check holds what that module reports as an error at its defaults — such as the grade, the sentence limit and the lists — since its scan block runs that module's scan on the copy. The passive voice, a warning there and off in the kit's own dials, is held by review. The kernel policy states the rule. The rewrite that makes it so changes wording only. This replaces R10 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r10).

## Applied

The record was born `active`, and the change that creates it applies its rulings. The install guide's section 2 is rewritten. Its check holds what the blocks `new-repo` and `commit` now do, as [rule 4 of plc-0011-install-guide](../policies/plc-0011-install-guide.md#r4) asks. The skill `commit-before-edit` of `const-task-close` gains its sentence, with boundary example 14 in that module's section 8. The skill `style-defaults` of `const-styling`, its install note and its module document say what a project that keeps no guide does. The kernel is rewritten. Its policy gains the language rule. [requirement A9.1](../requirements.md#a9-1) and its reading in the module document of `const-styling` admit a project that keeps no guide. Step 5 of the rollout plan follows the guide's order. In the guide, the dials file and the kernel copy swap places: the dials file, step 6 before this change, is step 4, and the kernel copy, step 4 before, is step 6. The change migrates the three carry entries of accepted records that named those steps, by case (i) of rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14). The last commit of the branch sets the record `inactive`.

## Carry list

1. R1 — [the install guide](../../INSTALL.md#s2), the opening of section 2 and its steps 1 and 9; [the guide's check](../../scripts/check-install-guide.py), its docstring at the names `new-repo` and `commit`.
2. R2 — [the install guide](../../INSTALL.md#s2), the opening of section 2 and its steps 5 and 7.
3. R3 — [the skill commit-before-edit](../../modules/const-task-close/plugin/skills/commit-before-edit/SKILL.md), its third moment; [const-task-close §8](../../modules/const-task-close/MODULE.md#t8), example 14.
4. R4 — [the install guide](../../INSTALL.md#s2), step 4 of section 2, and step 7 for the answer.
5. R5 — [the install guide](../../INSTALL.md#s2), steps 4, 6 and 7 of section 2; [the skill style-defaults](../../modules/const-styling/plugin/skills/style-defaults/SKILL.md), its first section; [the install note of const-styling](../../modules/const-styling/plugin/INSTALL.md), step 2; [requirement A9.1](../requirements.md#a9-1); [const-styling §3](../../modules/const-styling/MODULE.md#t3), the row of [requirement A9.1](../requirements.md#a9-1). What it narrows is history.
6. R6 — [the install guide](../../INSTALL.md#s2), step 8 of section 2.
7. R7 — [the kernel](../constitution/CONVENTIONS.md), its prose as written; [rule 10 of plc-0002-kernel](../policies/plc-0002-kernel.md#r10) and its [rule 8](../policies/plc-0002-kernel.md#r8); [the install guide](../../INSTALL.md#s2), step 4 of section 2; [the guide's check](../../scripts/check-install-guide.py), its docstring at the name `scan`. What it replaces is history.
