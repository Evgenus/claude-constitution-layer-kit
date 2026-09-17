---
id: research-project-superclaude-claude-flow
type: non-authoritative
title: SuperClaude & claude-flow — evidence report (2026-08-28)
status: inactive
---

# SuperClaude & claude-flow — evidence report (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Second-pass per-project research.

## SuperClaude (SuperClaude-Org/SuperClaude_Framework, master; active, pushed 2026-08-21, ~24k stars; v4→plugin migration)

Everything is advisory markdown injected into context; only ONE hook ships (`src/superclaude/hooks/hooks.json`: SessionStart→session-init.sh).

1. Doc typing/authority: NOTHING. 2. Per-kind doc governance: PARTIAL — pm-agent (`plugins/superclaude/agents/pm-agent.md`) does post-implementation learning capture + "monthly documentation health reviews"; purely advisory, no criteria per doc kind. 3. IDs/anchors: NOTHING. 4. Human decision protocol: NOTHING shipped (memory key `decisions` in MODE_Task_Management.md is the only trace). 5. Handoff/stop gates: PARTIAL — `/sc:save`,`/sc:load` (commands/save.md) persist session state into Serena MCP *memory*, not repo files; 30-min checkpoint pattern in RULES.md "Session Lifecycle"; no deterministic stop gate. 6. Escalation default: NOTHING. 7. Canonical locations: SHIPS (advisory) — RULES.md "File Organization": reports→`claudedocs/`, tests→`tests/`, scripts→`scripts/`. 8. Styling: PARTIAL — MODE_Token_Efficiency + BUSINESS_SYMBOLS.md symbol system, flag-overridable (FLAGS.md). 9. Size budgets: PARTIAL — only context-usage trigger (>75%→--token-efficient); no doc budgets. 10. Plain language: SHIPS — RULES.md "Professional Honesty" (🟡): no marketing superlatives, state "untested/MVP". 11. Answer shape: PARTIAL — per-mode markers, ✅Right/❌Wrong example pairs throughout RULES.md. 12. Enforcement: ADVISORY-ONLY. Tiers confirmed current: 🔴/🟡/🟢 + conflict hierarchy (Safety>Scope>Quality>Context) in `src/superclaude/core/RULES.md`. No evidence tiering works: their own `docs/research/pm-mode-performance-analysis.md` admits claims are "simulation-based", hallucination-detection/error-recurrence unmeasured.

## claude-flow (renamed ruvnet/ruflo, main; very active, pushed 2026-08-28, ~70k stars; sprawling — v3 rewrite in-repo, some surfaces self-labeled "partly design")

The gem is `v3/@claude-flow/guidance/` ("Guidance Control Plane", ADR-G001–G026): direct constitution-layer prior art.

1. Typing/authority: SHIPS — ADR-G021: typed authority levels agent<human<institutional<regulatory; irreversibility classes (reversible/costly/irreversible→proof levels). 2. Per-kind/meta governance: SHIPS — `docs/reports/claude-md-analysis.md`: an analyzer that *scores CLAUDE.md itself* (6 weighted dimensions: structure/coverage/enforceability/compilability/clarity/completeness, grades A–F, auto-optimizer) — self-describing meta-level exists; plus ADR-G012 manifest validator, ADR-G011 artifact ledger. 3. IDs/anchors: SHIPS — shard `compactText` = `[RULE-ID] text @tags` (ADR-G002); truth anchors (ADR-G018); dense ADR numbering (`v3/docs/adr/`). 4. Decision records: SHIPS — 26 guidance ADRs + ~350 project ADRs; HMAC-signed human-intervention records (ADR-G021). 5. Handoff: SHIPS — `.claude/settings.json` hooks on SessionEnd/Stop/PreCompact (auto-memory sync, checkpoint), `.claude/helpers/checkpoint-manager.sh`; root CLAUDE.md loop ends "…receipt → handoff → separately authorized publish". 6. Escalation: SHIPS — `checkAuthority()` returns `escalationRequired`; destructive ops→`require-confirmation` (ADR-G004). 7. Locations: SHIPS (advisory) — root CLAUDE.md "NEVER save to root" + directory map. 8–10. Styling/plain-language: PARTIAL — analyzer penalizes vague language; demands imperative list-form rules over prose. 9. Budgets: SHIPS — constitution capped 60 lines/~500 tokens (+100 priority boost), sections <50 lines, diff gate 300 lines. 11. Answer shape: NOTHING notable. 12. Deterministic enforcement: SHIPS — 4 hook-layer gates (destructive/allowlist/diff-size/secrets, block>confirm>warn>allow), real CI verification (Ed25519 witness manifests, monotone baselines; `.claude/skills/verification-quality/SKILL.md` honestly separates shipped vs aspirational).

## Lessons for our design

- CHALLENGES rule-priority tiers: SuperClaude's 🔴🟡🟢 is unvalidated self-report; claude-flow ADR-G004 states context rules are "probabilistic… model can and does ignore them" — tiers only matter if the top tier is deterministically enforced.
- CONFIRMS two-tier loading: tiny always-on constitution (≤60 lines, hashed) + retrieved-on-demand rest (ADR-G002) — instruction volume dilutes compliance ("models skip rules beyond first 100 lines").
- CONFIRMS deterministic-vs-advisory split: block/confirm/warn/allow hierarchy, hooks outside model control; keep style rules out of gates.
- CONFIRMS meta-governance: a rules-file that scores/validates itself (claude-md analyzer) is proven prior art; imperative list-form rules beat prose for machine-checkability.
- CONFIRMS typed human authority + irreversibility classes + explicit escalation ("requires human approval") as first-class records — nobody ships "stop when no procedure" as a blanket default; it must be designed in.
