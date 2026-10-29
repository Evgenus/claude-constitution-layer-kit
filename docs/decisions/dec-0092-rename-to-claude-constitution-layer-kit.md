---
id: dec-0092-rename-to-claude-constitution-layer-kit
type: task-record
title: The kit is renamed claude-constitution-layer-kit, its records following under a one-time exception
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit is renamed claude-constitution-layer-kit, its records following under a one-time exception

## Context

The kit was named `constitution-kit`: its GitHub repository, `Evgenus/constitution-kit`; its marketplace, so every module's id ended in `@constitution-kit`; and the folder the install guide writes for the kit's clone, `~/dev/constitution-kit`. On 2026-10-16 the decider asked to rename it `claude-constitution-layer-kit`. The name should say that the kit is made for Claude, and a second layer kit is planned beside it.

At the cut of this change the old name stood 72 times in 15 files git tracks. Eleven of them were in six accepted records. CI takes the repository's name from GitHub at run time, so its workflow names no repository. The kit's checks read the marketplace's name from `.claude-plugin/marketplace.json` and type it nowhere.

The platform refuses a marketplace name that imitates an official one ([marketplace reference, reserved names](https://code.claude.com/docs/en/plugins/marketplace-reference.md#reserved-names)). On 2026-10-16 the session tried the new name in a scratch marketplace: `claude plugin validate` passed on Claude Code 2.1.282 and 2.1.286, and `claude plugin marketplace add` and `claude plugin install` both worked on 2.1.286 in an empty configuration folder.

## 1. How far the rename goes

### Options

- **A. The repository only.** GitHub's name and the five lines that name it; the marketplace keeps `constitution-kit`.
  - **Pros:** the smallest change; no module id changes; no exposure to the platform's rule on imitated names.
  - **Cons:** the name a user types, `const-x@constitution-kit`, still lacks the word Claude; the second kit's marketplace would follow no common pattern.
- **B. The repository and the marketplace.** A, the marketplace's name and the clone's folder in the install guide; the variables `CONSTITUTION_KIT_*` and the prose name "constitution kit" stay.
  - **Pros:** the name a user types matches the repository; the second kit can follow the pattern; the repository is private and has no consumer, so changing the ids breaks nothing.
  - **Cons:** about sixty edits and a record; the platform's rule on imitated names is not written as an exact test, so a later version could refuse a name that starts with `claude-`.
- **C. Everything.** B, the 89 uses of the variables `CONSTITUTION_KIT_*` and the 17 uses of the prose name, in either case.
  - **Pros:** one name everywhere.
  - **Cons:** about twice the size of B, for names no user sees.

### Recommendation

B, recommended by the session. The marketplace's name is what a user types and sees, and it can change for free only while no consumer has installed the kit.

### Choice

B, chosen by the decider in chat on 2026-10-16.

### Ruling

<a id="r1"></a>**R1.** The kit's GitHub repository is `Evgenus/claude-constitution-layer-kit`.

<a id="r2"></a>**R2.** The kit's marketplace is named `claude-constitution-layer-kit`, so every module's id is `<module>@claude-constitution-layer-kit`, in the kit's own settings and in a project's alike.

<a id="r3"></a>**R3.** The install guide writes the kit's clone as `~/dev/claude-constitution-layer-kit`.

<a id="r4"></a>**R4.** These keep their names: the module prefix `const-`, the variables `CONSTITUTION_KIT_*`, the prose name "constitution kit", and the folder of a clone that already exists.

## 2. The old name in accepted records

The session first proposed to keep the eleven mentions in the six accepted records as they were accepted. [Kernel §5](../constitution/CONVENTIONS.md#k5) lets a record's body be edited in place only by a typo fix, a reference-form migration or a wording edit of a listed kind. Rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) says a wording edit changes no fact and no code span. A repository's or a marketplace's name in a code span is none of these. Six of the mentions are in rulings, and five state dated facts, such as the day the repository was created. The decider overruled the session: the records follow the new name. The question left was how the kit allows that edit.

### Options

- **A. A one-time exception in this record.** This record orders the edit, names the rules it breaks, and sets no precedent.
  - **Pros:** the smallest change; no rule changes; the usual carry audit.
  - **Cons:** the kit breaks its own kernel on purpose, against [law 1 of CLAUDE.md](../../CLAUDE.md#law-1); the next rename needs a record of its own.
- **B. A new migration kind in the kernel and in rule 14.** A renamed repository, marketplace or plugin id is followed in records, as a moved document already is; [kernel §5](../constitution/CONVENTIONS.md#k5) and rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) both change.
  - **Pros:** the edit follows the rules; the second kit's rename is ruled in advance; it matches how the kit treats a moved document.
  - **Cons:** a kernel change, so the carry audit reads every record; the new wording must pass its own audit.
- **C. The new kind in rule 14 alone.** A renamed repository is read as a moved document under the kernel's present words.
  - **Pros:** no kernel change; a smaller audit than B.
  - **Cons:** it rests on a reading, not on a rule; a module's id is no citation of a document, so the reading is weak for most of the mentions.

### Recommendation

B, recommended by the session. The decider had overruled the rule, so the rule should change rather than be broken once, and the second kit will meet the same question.

### Choice

A, chosen by the decider in chat on 2026-10-16, over the recommendation. The session's objection stands: this record breaks [kernel §5](../constitution/CONVENTIONS.md#k5) and rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) on purpose.

### Ruling

<a id="r5"></a>**R5.** This change rewrites, in place, the eleven mentions of the old repository's or marketplace's name in [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md), [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md), [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md), [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md), [dec-0060-ci-installs-from-the-github-remote](dec-0060-ci-installs-from-the-github-remote.md) and [dec-0071-projects-install-from-github](dec-0071-projects-install-from-github.md). Each now names `claude-constitution-layer-kit`, the five dated facts included, though the repository had the old name on those dates; git keeps each record as it was accepted. No other word of those records changes.

<a id="r6"></a>**R6.** The edit of R5 is an exception to [kernel §5](../constitution/CONVENTIONS.md#k5) and to rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), which stand unchanged. It sets no precedent: a later rename of a repository, a marketplace or a plugin id leaves accepted records as they stand, save the mechanical edits [kernel §5](../constitution/CONVENTIONS.md#k5) allows.

## Applied

The change renames the marketplace in `.claude-plugin/marketplace.json`, the marketplace and the module ids in `.claude/settings.json`, and the name in [CLAUDE.md](../../CLAUDE.md), [the install guide](../../INSTALL.md), `NOTICE`, rule 4 of [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r4), `scripts/check-install-guide.py` and [step 10 of the rollout plan](../rollout-plan.md#s10). A self-test case of `scripts/check-bare-install.py` that needs the name of some other marketplace now uses `other-mp`. The GitHub repository is renamed before the merge.

## Carry list

1. R1 — item 2 of [the install guide's prerequisites](../../INSTALL.md#s1), and step 2 of [its bootstrap](../../INSTALL.md#s2).
2. R2 — [CLAUDE.md](../../CLAUDE.md), "Session conduct"; step 3 of [the install guide's bootstrap](../../INSTALL.md#s2), and [its install of one module](../../INSTALL.md#s3).
3. R3 — rule 4 of [plc-0011-install-guide](../policies/plc-0011-install-guide.md#r4).
4. R4 — history only: the scope of this change.
5. R5 — history only: a one-time edit.
6. R6 — [kernel §5](../constitution/CONVENTIONS.md#k5) and rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), unchanged; the exception itself is history.
