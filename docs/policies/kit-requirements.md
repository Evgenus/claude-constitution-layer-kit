---
id: kit-requirements
type: current-state
title: Requirements policy — the traceability matrix and module specifications of the kit
status: active
---

# Requirements policy

Governs the document kind *requirements document*: the traceability matrix, one row per requirement part with its destination and recommended enforcement, and the module specifications beside it. Territory under this policy's id in `constitution.yaml`.

## Rules

1. **Type.** `current-state`, superseded in place ([kernel §1](../../kernel/CONVENTIONS.md#k1)); it holds what a module must implement and nothing about when — phases belong to the rollout plan.
2. **Change.** Adding, amending, or re-homing a row or a module specification is a `process`-stakes decision ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)); the row cites its record.
3. **Anchors.** Every aspect, row, and module specification carries an explicit anchor — `a<n>`, `a<n>-<m>`, the plugin name (decision [dec-0005-reference-forms](../decisions/dec-0005-reference-forms.md)).
4. **Aliases.** `M<n>` is a local alias inside this document only; everywhere else a module is cited by a link to its specification anchor with the plugin name as text.
5. **Descriptions.** A module's description moves into its `MODULE.md` when authoring begins; the heading keeps its anchor with a one-line stub linking there (decision [dec-0015-pre-module-audit-rulings](../decisions/dec-0015-pre-module-audit-rulings.md)).
