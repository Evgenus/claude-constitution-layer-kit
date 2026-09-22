---
id: plc-0005-research
type: current-state
title: Research policy — a module's dated comparison of candidate mechanisms
status: active
---

# Research policy

Governs the document kind *research comparison*: one module's dated survey of how its matrix rows are addressed today, ending in one recommendation per mechanism (decision [dec-0010-module-research-per-module](../decisions/dec-0010-module-research-per-module.md)). Territory under this policy's id in `constitution.yaml`.

## Rules

1. **Type.** `non-authoritative`: a comparison informs a mechanism choice and binds nothing.
2. **Status.** `active` while it is the module's current comparison; `inactive` once a later survey supersedes it, kept while cited ([kernel §1](../../kernel/CONVENTIONS.md#k1)).
3. **Provenance.** Every fact names the public source that verified it; nothing is copied from earlier design work.
4. **Vocabulary.** Written in kit vocabulary: kernel terms, matrix rows, module names.
5. **Shape.** Candidate approaches, mechanism class, maturity, cost, one recommendation per mechanism with reasoning, and the date of the survey.
6. **Number.** Comparisons are a numbered kind: id and filename stem are one name, `res-<nnnn>-<slug>`, the slug naming the module surveyed; prefix, width and territory are an entry of `const-catalogs.catalogs` in `constitution.yaml`, its territory this policy's own by a YAML alias. A new comparison takes one more than the highest number the catalog has held, deleted comparisons included, provisional until it lands on main ([requirement A13.1](../requirements.md#a13-1), [A13.3](../requirements.md#a13-3)) — which is how a later survey of the same module gets a name of its own beside the one it supersedes (rule 2). A `res-` name written outside Markdown matches a pattern of the `mentions` dial of module `const-referencing`, whose scan reports one that is not an id a document the scan covers carries.
