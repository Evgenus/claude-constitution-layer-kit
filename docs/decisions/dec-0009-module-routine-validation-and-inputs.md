---
id: dec-0009-module-routine-validation-and-inputs
type: task-record
title: Module routine gains fresh-context validation, cited research inputs, and the trial-earned check rules
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Module routine gains fresh-context validation, cited research inputs, and the trial-earned check rules

## Context

The constitution design phase ran a fixed per-aspect routine: research with a dated comparison per aspect, gap resolution one decision per message, selection by failure class, a native-first mechanism choice with a rule-to-artifact map, a plan with acceptance evidence and a checkpoint, and a fresh-context validation of every output before it was presented. The kit's per-module routine ([CLAUDE.md, "Developing a module"](../../CLAUDE.md), [module-template/MODULE.md](../../module-template/MODULE.md), the `[decide:]` markers of decision [dec-0003-module-spec-kind](dec-0003-module-spec-kind.md)) was compared step by step against it on 2026-09-18. Covered: gap resolution, selection, the mechanism slots, acceptance, the checkpoint. Missing: any research step or pointer to the existing comparisons; a moment where the session confirms or overturns the matrix's recommended enforcement before filling the artifacts table; a fresh-context validation before the human yes; and the rules earned by executing the design plan once in a trial (every check lane reports its examined-item count, checker-broken and repository-wrong are distinct exit codes, built artifacts never reference the plan that produced them), none of which the template states.

## Options

- **A. Nothing.** Keep the five steps; rely on the template and the human yes.
  - **Pros:** no template change, no record, authoring starts now.
  - **Cons:** the one check that demonstrably caught defects in the design phase is absent; trial lessons stay in another repository.
- **B. Validation, carried lessons, research inputs.** A fresh-context validation step before the human yes; the trial-earned rules added to the template's enforcement-honesty and acceptance sections; the design-phase research copied into the kit and cited from the artifacts section; a decide-how confirmation line in step 2 of the routine.
  - **Pros:** closes every gap found with one template amendment and one routine edit; research stays a cited input, conditional on a mechanism no comparison covers, so no per-module survey tax.
  - **Cons:** one record and a template bump before the first module; eighteen research files to carry under the kit's own territory.
- **C. Full mirror of the six design phases per module.** Research, gap resolution, selection, mechanism, plan, each with its own validation pass.
  - **Pros:** identical rigour to the design phase.
  - **Cons:** the design phase already ran once for all aspects; repeating it per module is the machinery-before-facts failure [INTENT.md](../../INTENT.md) names.

## Recommendation

B: it adds the two steps that produced measurable value in the design phase, validation and folded-back lessons, and makes research a cited input instead of a repeated activity.

## Choice

B, chosen by the decider in chat on 2026-09-18.

## Rulings carried

1. The design-phase research lives in `docs/research/`, each file carrying the kernel envelope as `non-authoritative`, `inactive`, with a provenance line; an index at `docs/research/README.md` maps the design-phase aspect numbers onto the kit's aspects and lists the settled findings the design prompt carried. (Reversed the same day by decision [dec-0010-module-research-per-module](dec-0010-module-research-per-module.md); the files are deleted and this cite is plain text.) The territory is claimed by the kit-documents policy.
2. [Template §6](../../module-template/MODULE.md#t6) gains a **research inputs** slot. Every mechanism names the comparison it rests on, or a comparison is written first, in the same shape. It also gains the portability rule for installed components: a skill, hook, script, command, agent, error text, or install note references nothing in the kit repository, because consumers install the module without the kit. Reasoning lives in the module document and its records.
3. [Template §9](../../module-template/MODULE.md#t9) gains the exit-code contract. A check distinguishes a finding (the repository is wrong) from a configuration failure (the checker is broken, a pinned tool is missing) by exit code and message. A missing tool is loud, never a silent pass.
4. [Template §10](../../module-template/MODULE.md#t10) gains the examined-count rule. Every check reports how many items it examined; zero is a visible count and never a silent green; each gate's fixtures include the exit-code split.
5. Step 2 of the routine confirms or overturns the matrix's recommended enforcement per row before the artifacts table is filled, naming on each step down what the native option cannot do.
6. A new routine step before the human yes: a fresh-context validation by a subagent holding only the module's files, the template, the laws, and the module's matrix rows, never the authoring reasoning. Every finding is fixed or justified in the pull request. The kit's own `scripts/check-references.sh`, which already failed loudly without lychee and printed its counts on green, is amended in the same commit to print its counts on every exit and to exit 2 on findings and 1 on a configuration failure: the first instance of rulings 3 and 4.
