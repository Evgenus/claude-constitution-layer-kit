---
id: research-index
type: non-authoritative
title: Research inputs — the dated comparisons the modules' mechanisms rest on
status: active
---

# Research inputs

Dated comparisons from the constitution design phase, imported so that a module can cite the comparison its mechanism rests on ([template §6](../../module-template/MODULE.md#t6), decision [module-routine-validation-and-inputs](../decisions/module-routine-validation-and-inputs.md)). They are `non-authoritative`: the kernel and the [traceability matrix](../rollout-plan.md#a1) hold what was decided; a comparison explains why a mechanism was preferred at its date. A mechanism no comparison covers gets its own comparison here first, in the same shape: candidate approaches, mechanism class, maturity, cost, one recommendation with reasoning, dated.

## Aspect comparisons

The design phase numbered aspects 1–10; the kit's matrix regroups them as A1–A13. Mapping:

| key | comparison | kit aspect(s) |
|---|---|---|
| R1 | [Document meta-types](aspect-01-meta-types.md) | [A1](../rollout-plan.md#a1) |
| R2 | [Document referenceability](aspect-02-referenceability.md) | [A5](../rollout-plan.md#a5), [A13](../rollout-plan.md#a13) |
| R3 | [Decision-question protocol](aspect-03-decision-protocol.md) | [A3](../rollout-plan.md#a3), [A6](../rollout-plan.md#a6) |
| R4 | [Session→repo handoff contract](aspect-04-handoff-contract.md) | [A4](../rollout-plan.md#a4) |
| R5 | [Escalation default](aspect-05-escalation.md) | [A8](../rollout-plan.md#a8) |
| R6 | [Canonical location](aspect-06-canonical-location.md) | [A2](../rollout-plan.md#a2) |
| R7 | [Documentation styling defaults](aspect-07-styling-defaults.md) | [A9](../rollout-plan.md#a9) |
| R8 | [Document budgets](aspect-08-doc-budgets.md) | [A11](../rollout-plan.md#a11) |
| R9 | [Language complexity](aspect-09-language-complexity.md) | [A10](../rollout-plan.md#a10) |
| R10 | [Answer-shape matching](aspect-10-answer-shape.md) | [A7](../rollout-plan.md#a7) |

## Surface and prior art

| key | document | use |
|---|---|---|
| R11 | [Native surface map](native-surface-map.md) | which platform mechanism carries what, with loading and enforcement semantics, as verified on its date. A module's "platform facts relied on" slot re-verifies each fact it uses against the official documentation on its own date; this map is the starting list, never the evidence |
| R12 | [Second-pass consolidated findings](second-pass-consolidated.md) | what the prior-art survey confirmed, challenged, or refined |
| R13 | [Agent OS](project-agent-os.md), [community harnesses](project-community-harnesses.md), [OpenSpec](project-openspec.md), [spec-kit](project-spec-kit.md), [SuperClaude and claude-flow](project-superclaude-claude-flow.md), [Trail of Bits and Anthropic repos](project-tob-anthropic.md) | per-project evidence reports behind R12 |

## Settled findings carried from the design prompt (2026-08-25)

Stated in the design prompt as settled and not re-researched; listed here so a module can cite them.

1. MCP servers cannot arbitrate: assist-only by construction.
2. Frontmatter validation is a small repository script; no viable third-party tool (Vale is capability-disqualified: its scopes match only present content, so it cannot see a missing field).
3. Reference checking: `lychee` ≥ 0.24.2, offline, with fragments.
4. Prose linting: Vale (organisation now `vale-cli`; pin packages by release URL).
5. Staleness detection: custom script only.
6. Sizes are measured in characters, never tokens.
7. Any ledger-like file is one file per entry.
