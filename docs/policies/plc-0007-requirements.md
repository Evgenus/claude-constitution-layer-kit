---
id: plc-0007-requirements
type: current-state
title: Requirements policy — the traceability matrix and module specifications of the kit
status: active
---

# Requirements policy

Governs the document kind *requirements document*: the traceability matrix, one row per requirement part with its destination and recommended enforcement, and the module specifications beside it. Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**Type.** `current-state`, superseded in place ([kernel §1](../../kernel/CONVENTIONS.md#k1)); it holds what a module must implement and nothing about when — phases belong to the rollout plan; a module's entry trigger in its heading, "enters when" (decision [dec-0006-accumulating-set-first](../decisions/dec-0006-accumulating-set-first.md)), and a condition inside a rule, "until the kit's CI runs it", name no phase.
2. <a id="r2"></a>**Change.** Adding, amending, or re-homing a row or a module specification is a `process`-stakes decision ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)). The row states its rule in full; citing a record beside it is optional provenance.
3. <a id="r3"></a>**Anchors.** Every aspect, row, and module specification carries an explicit anchor — `a<n>`, `a<n>-<m>`, the plugin name (decision [dec-0005-reference-forms](../decisions/dec-0005-reference-forms.md)).
4. <a id="r4"></a>**Aliases.** `M<n>` is a local alias inside this document only; everywhere else a module is cited by a link to its specification anchor with the plugin name as text.
5. <a id="r5"></a>**Descriptions.** A module's description moves into its `MODULE.md` when authoring begins; the heading keeps its anchor with a one-line stub linking there (decision [dec-0015-pre-module-audit-rulings](../decisions/dec-0015-pre-module-audit-rulings.md)).
6. <a id="r6"></a>**Rows.** A row keeps its number for life; a new row takes the next number in its aspect and stands in number order; a removed row leaves its number unused. A row's text is its rule in full, whatever its length. The `†` flag marks a row whose destination is under a boundary test, resolved when the module is authored.
7. <a id="r7"></a>**Vocabulary.** The destination classes and the enforcement classes — `gate`, `gate-lite`, `advisory`, `definitional`, `config`, `git-native`, `review` — are closed sets, each defined once in the preamble; a class may carry a qualifier before or after it — "advisory procedure", "review judgment", an assist named — and a row waiting for another module says so in words. A row may name the template as its destination or beside another, the template being authoring law. A row's recommended enforcement stays the recommendation: the module's comparison confirms or overturns it, the module document's enforcement section states what shipped, and the row is amended only under rule 2 — when its rule changes, or when the vocabulary it is written in does.
8. <a id="r8"></a>**Structure.** One heading of the first level; the matrix first, the module specifications after it, each under its anchor, a moved description leaving the stub "Description moved into the module's document: …; this anchor stays the module's handle". Nothing that is neither a requirement nor a specification.
9. <a id="r9"></a>**Enforcement.** The envelope by module `const-meta-types`; links, anchors and the row and module lanes by module `const-referencing`. Content, vocabulary and structure are review.
10. <a id="r10"></a>**Style.** Documents of this kind follow the style guides in the territory of [plc-0010-style-guide](plc-0010-style-guide.md), and depart from a default only where the dial `departures` of module `const-styling` in `constitution.yaml` names a departure for their territory, with its reason ([rule 9 of plc-0001-root-policy](plc-0001-root-policy.md#r9)); the traces of the defaults are held by that module's scan, the rest is review.
