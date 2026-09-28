---
id: dec-0051-module-citation-rule-in-the-guide
type: task-record
title: The rule for citing a module lives in the kit guide, not in the requirements policy
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The rule for citing a module lives in the kit guide, not in the requirements policy

## Context

The blind reader of the carry audit of [dec-0049-module-links-held-by-a-kit-check](dec-0049-module-links-held-by-a-kit-check.md), on 2026-09-28, found that [rule 4 of plc-0007-requirements](../policies/plc-0007-requirements.md#r4) bound every kit document: how a module is cited outside module prose, the two exceptions, and the check that holds the link. That policy governs the requirements document alone, and [rule 5 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r5) has a policy govern exactly one kind. The rule had stood there before dec-0049, which made it longer. The finding was justified in that audit as older than the change and put to the decider afterwards, in chat on 2026-09-28.

## Options

- **A. Move it to CLAUDE.md.** Rule 4 keeps the `M<n>` alias of its own document; the kit-wide rule, its exceptions and its check move into the reference bullet of the kit guide, which already lists the kit's reference forms.
  - **Pros:** each policy governs its own kind again; the kit's reference forms stay together in one text that governs every kit document.
  - **Cons:** a record, an audit and a yes; the guide grows by a few lines.
- **B. Keep it in plc-0007, and say why.** Rule 4 states that it binds every kit document, because the module anchors live in the requirements document.
  - **Pros:** one sentence; no rule moves.
  - **Cons:** a policy still governs more than its kind; the exception is explained, not removed.
- **C. Move it to the root policy.**
  - **Pros:** the root policy sets rules every policy follows.
  - **Cons:** it governs the policies, not every kit document, so the mismatch moves with the rule.

## Recommendation

A, by the session: the kit guide is the one text that governs every kit document, and its reference bullet already lists the kit's other forms.

## Choice

A, chosen by the decider in chat on 2026-09-28.

## Ruling

**R1.** How a kit document cites a module outside module prose — the link to the specification anchor, the two exceptions for a template and a frozen comparison, and the kit check that holds the link, with what it reads and when it runs — is stated in the reference bullet of the kit guide, whose anchor is `references`. Rule 4 of plc-0007-requirements keeps only the `M<n>` alias of the requirements document and points to that bullet; rule 9 of the same policy, the enforcement cell of [requirement A5.6](../requirements.md#a5-6) and the check's own texts point to it too. The rulings of dec-0049 stand unchanged; only their home moves.

## Applied

The commit that creates this record gives the reference bullet of [CLAUDE.md](../../CLAUDE.md#references) its anchor and the full rule; cuts [rule 4 of plc-0007-requirements](../policies/plc-0007-requirements.md#r4) to the alias and a pointer; points [rule 9](../policies/plc-0007-requirements.md#r9) of the same policy and the enforcement cell of [requirement A5.6](../requirements.md#a5-6) at the bullet; and names the bullet in the docstring, the message and the self-test of [the kit check](../../scripts/check-module-links.py). The record is born `inactive`.

## Carry list

1. R1 — [the reference bullet of CLAUDE.md](../../CLAUDE.md#references); [rule 4](../policies/plc-0007-requirements.md#r4) and [rule 9 of plc-0007-requirements](../policies/plc-0007-requirements.md#r9); the enforcement cell of [requirement A5.6](../requirements.md#a5-6); [the kit check](../../scripts/check-module-links.py), its docstring and its message.
