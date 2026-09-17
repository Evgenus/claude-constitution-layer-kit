---
id: kit-documents
type: current-state
title: Kit documents policy — the kernel, the intent page, decision records, module documents
status: active
---

# Kit documents policy

Governs the kit's own governed documents, as claimed under this policy's id in `constitution.yaml`: the kernel, the intent page, the decision records, the research inputs, and every module's `MODULE.md`. The kit is consumer zero of its document-shaped modules (decision [accumulating-set-first](../decisions/accumulating-set-first.md)); this policy is what those modules enforce here.

## Rules

1. **Envelope.** Every document in this territory carries the kernel envelope ([kernel §1](../../kernel/CONVENTIONS.md#k1)) and is one of the kernel's meta-types ([kernel §2](../../kernel/CONVENTIONS.md#k2)). Enforced by module `const-meta-types` once authored; by review until then.
2. **Decision records.** A record in `docs/decisions/` follows [kernel §5](../../kernel/CONVENTIONS.md#k5) and the kernel's record schema; it is written for every `process`, `product`, or `architecture` ruling of the kit ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)). Enforced by module `const-decision-records` once authored.
3. **Module documents.** A `MODULE.md` fills every section of `module-template/MODULE.md`, cites exactly its matrix rows ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)), and carries no project reference ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)).
4. **References.** Cross-document cites are links to explicit anchors (decision [reference-forms](../decisions/reference-forms.md)); `scripts/check-references.sh` is the gate until module `const-referencing` ships its lint.
5. **Supersession.** The kernel and the intent page are superseded in place; records never are ([kernel §1](../../kernel/CONVENTIONS.md#k1), [kernel §5](../../kernel/CONVENTIONS.md#k5)).
6. **Research inputs.** A document in `docs/research/` is `non-authoritative`: a dated comparison of candidate mechanisms ending in one recommendation, never a rule. Imported comparisons carry a provenance line; a new one is written before a module adopts a mechanism no comparison covers (decision [module-routine-validation-and-inputs](../decisions/module-routine-validation-and-inputs.md)). The index [README](../research/README.md) is the one `active` document there.
