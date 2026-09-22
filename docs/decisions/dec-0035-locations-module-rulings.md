---
id: dec-0035-locations-module-rulings
type: task-record
title: Rulings of the const-locations authoring — a generator with a dry run creates a document at the home its territory implies, from a template the module's own dial names
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-locations authoring

## Context

The fifth module, [`const-locations`](../requirements.md#const-locations), is authored from 2026-09-22 in the kit, ahead of its Phase C slot in the rollout plan: the kit is consumer zero for exactly the kinds it creates — policies, module documents, records, comparisons — and passed the module's entry trigger, the second territory, long ago. Its research comparison is [res-0005-const-locations](../research/res-0005-const-locations.md); its rows are [requirement A2.4](../requirements.md#a2-4) and [requirement A2.5](../requirements.md#a2-5), both advisory in the matrix and confirmed so by the comparison. The questions below were put to the decider in chat, one per message, each with lettered options. What the session derived without a choice — the three classes of territory a home follows from, the dials file edited by hand, no hook and no always-on line, the specification's optional default-policy dial dropped — follows the comparison's recommendations and the laws of [CLAUDE.md](../../CLAUDE.md), and is stated in the module's document with its reasoning.

## 1. How a document is created "by command"

[Requirement A2.4](../requirements.md#a2-4) says documents are "created by command from the policy's template into the canonical home". The comparison's live runs showed the model, with a skill alone, deriving the home correctly on a two-namespace dials file — and writing every file through a shell heredoc, with the same three envelope defects whenever it wrote blind. The kit's own dials file carries anchors, aliases and a free-segment pattern.

- **A. Generator plus skill.** A Python script derives the home from the policy's territory, proves through `git check-ignore` that the home resolves to exactly that policy, and writes the file from the kind's template with a valid envelope; the skill carries the procedure and names the script.
  - **Pros:** the row's words made literal; the envelope and the home are proven before the write, not judged after; the dials file is read by code; a `HOME:` line gives the record and catalog skills a handoff that keeps every module executable alone.
  - **Cons:** a script in a module with no gate strains the shared code in two places — no `severity` dial, a second entry point with no first — both widenings the shared-code policy allows but that must be argued and fixtured; more to build than prose.
- **B. Skill prose only.** The skill tells the model to read the dials file, find the policy, take the pattern's prefix, copy the template and write.
  - **Pros:** nothing to build beyond a skill; no shared links; the smallest module; correct in the live runs on a simple dials file.
  - **Cons:** the derivation becomes judgment exactly where a gate later judges it; nothing proves the path before the write; on the kit's own file the model must read anchors and a `modules/*/MODULE.md` pattern as prose; the row says "by command" and this ships none.
- **C. Locator script, the model writes.** The script derives and proves the home and prints it with the template's path; the model writes the file.
  - **Pros:** the proof is deterministic and the script never touches a file; the handoff line is the whole interface.
  - **Cons:** the envelope is left to the model, whose blind envelopes carried the same three defects in every run; the template becomes an exemplar to imitate, which the row's own wording forbids.

**R1.** A, with C kept as the `--dry-run` mode of the same script. Chosen by the decider in chat on 2026-09-22, "as recommended". The generator is `new-document`, a second entry point on the pattern of the fourth module's mover, under the shared guard with a closing line of its own; the skill `new-document` names it and carries the procedure; the dry run prints the home and the template and writes nothing, and is what another kind's procedure calls when it writes the file itself.

## 2. Where a kind's template is declared, and where its `type` comes from

The generator needs two things per kind: the template file and the meta-type. The kernel gives a policy no internal format and lets a module read a policy's namespace only for its territory ([kernel §6](../../kernel/CONVENTIONS.md#k6)).

- **A. A `templates` list in this module's own namespace; `type` from the template's envelope, or from a `--type` argument where the kind has no template.** Entries `{policy: <id>, template: <path>}`.
  - **Pros:** reads only its own namespace, absent by default, so the kernel-alone test holds with zero configuration; one source for the type where a template exists; the kit's three templates are three lines.
  - **Cons:** a kind without a template makes the caller name the type, and a wrong `--type` is caught only by the meta-types gate where installed.
- **B. The same list, each entry also carrying `type`.**
  - **Pros:** the command never needs `--type`; a kind with no template is still fully declared.
  - **Cons:** the type is stated twice where a template exists and the two can disagree; the dial grows for a case the kit does not have.
- **C. A `template` key in each policy's namespace.**
  - **Pros:** the natural reading — a policy declares its template; no list to maintain.
  - **Cons:** a module would read a policy-namespace key beyond `territory`: a kernel change to its section 6 and the dials schema, recorded and audited.

**R2.** A, with the principle the decider stated in choosing it: the module stays independent of every other module — it reads its own namespace and the kernel-owned keys, and a sibling enters only as an optional enhancement whose handoff is a stem given to the command and a `HOME:` line read from it. Chosen by the decider in chat on 2026-09-22.

## Carry list

1. R1 — the row of [requirement A2.4](../requirements.md#a2-4) in [§3](../../modules/const-locations/MODULE.md#t3) of the module's document, rule L-a of its [§5](../../modules/const-locations/MODULE.md#t5), the two `script` rows and the `skill` row of `new-document` in its [§6](../../modules/const-locations/MODULE.md#t6). That the choice was "as recommended": history only.
2. R2 — the row `templates` of [§7](../../modules/const-locations/MODULE.md#t7) of the module's document, rule L-e of its [§5](../../modules/const-locations/MODULE.md#t5), rows L5.13 and L5.14 of the error-message table in its [§6](../../modules/const-locations/MODULE.md#t6), and the "Depends on" and enhancements of its [§11](../../modules/const-locations/MODULE.md#t11).
