---
id: record-references-are-provenance
type: task-record
title: A current-state document states its own rules; its references to records are provenance, never authority
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A current-state document states its own rules; its references to records are provenance, never authority

## Context

On 2026-09-18 the decider observed that the kit's most authoritative documents (policies, `CLAUDE.md`, the module template, [INTENT.md](../../INTENT.md)) link decision records, which are `inactive` task-records and carry no authority ([kernel §1](../../kernel/CONVENTIONS.md#k1), [kernel §2](../../kernel/CONVENTIONS.md#k2)). [Kernel §5](../../kernel/CONVENTIONS.md#k5) already places the ruling in the current-state documents it changed and keeps the record as evidence, so a reference from a standing document into a record is the designed mechanism. What the kernel did not say is the distinction that makes it sound: a reference is either *normative* (the rule is over there) or *provenance* (the rule was decided there; go see why). A survey of every record link in the kit's standing documents found them all provenance except one: [template §4](../../module-template/MODULE.md#t4) read "Rulings that bind this module … Nothing is restated", calling inactive records binding and telling the module document not to state its own rules.

## Options

- **A. Reword [template §4](../../module-template/MODULE.md#t4) only.** Rename the section to provenance; the rule itself is stated where it acts.
  - **Pros:** fixes the one real instance; routine edit, no kernel change.
  - **Cons:** the distinction stays implicit, so the next author can reintroduce a normative cite.
- **B. A plus one sentence in [kernel §5](../../kernel/CONVENTIONS.md#k5).** A current-state document states every rule it binds in its own text; its references to records are provenance, never authority.
  - **Pros:** closes the class, not the instance; one line, derivable from [kernel §1](../../kernel/CONVENTIONS.md#k1) and [kernel §2](../../kernel/CONVENTIONS.md#k2), restating nothing foreign.
  - **Cons:** a kernel change, so a recorded decision before the first module.
- **C. Forbid references from current-state documents to records.**
  - **Pros:** no judgment about which cite is which.
  - **Cons:** reverses [status-encodes-lifecycle](status-encodes-lifecycle.md); unreferenced records must be deleted by the lifecycle rule, so options and reasoning leave the tree; every provenance cite in the policies and `CLAUDE.md` is stripped.

## Recommendation

B. The failure is a class, [template §4](../../module-template/MODULE.md#t4) proves an author can fall into it, and the fix is one kernel sentence naming a consequence [kernel §1](../../kernel/CONVENTIONS.md#k1) and [kernel §2](../../kernel/CONVENTIONS.md#k2) already imply.

## Choice

B, chosen by the decider in chat on 2026-09-18.

## Applied in the same commit

- [Kernel §5](../../kernel/CONVENTIONS.md#k5): the provenance sentence, after the evidence clause.
- [Template §4](../../module-template/MODULE.md#t4): reworded from "rulings that bind this module" to provenance; the rule is stated in [template §5](../../module-template/MODULE.md#t5)–[§9](../../module-template/MODULE.md#t9), the record is cited for where and why.
- The kit's other record cites were checked and left as they are: each states the rule in full and cites the record parenthetically.
