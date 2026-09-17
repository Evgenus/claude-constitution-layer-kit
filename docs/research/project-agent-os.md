---
id: research-project-agent-os
type: non-authoritative
title: Agent OS — evidence report (2026-08-28)
status: inactive
---

# Agent OS — evidence report (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Second-pass per-project research. Repo: buildermethods/agent-os, main @ v3.0 (2026-01-20), plus tags v1.2.0–v2.1.1 for lineage. v3 deliberately shrank the system: spec-writing/task-orchestration retired ("plan mode handles it"); what ships is 5 command prompts, 3 bash scripts, 1 profile. Old three-layer (standards/instructions/product) is now standards + product + specs; "instructions" became `.claude/commands/agent-os/*.md`.

1. **Doc typing/authority — PARTIAL.** Kinds exist only as folders: `agent-os/standards/` (durable rules), `agent-os/product/` (current-state: mission/roadmap/tech-stack; `commands/agent-os/plan-product.md`), `agent-os/specs/YYYY-MM-DD-HHMM-slug/` (task records; `shape-spec.md`). No authority labels in v3; v1's decisions.md carried "Override Priority: Highest" header (v1.2.0 `instructions/plan-product.md` step 7).
2. **Policy-based governance — NOTHING** as per-kind policy docs. Closest prior art: `commands/agent-os/discover-standards.md` is effectively the policy for the "standard" kind — creation procedure (ask-why loop, confirm, file), placement rules, writing rules, good/bad examples. But hardcoded in a command, not a self-describing doc; no root policy, no path-pattern governance.
3. **Referenceability — PARTIAL.** Canonical `folder/file` names via `standards/index.yml`; `@agent-os/standards/...` reference lines injected into plans/skills (`inject-standards.md`); reserved keyword `root`. No anchors or stable IDs. v1 had DEC-XXX decision IDs — gone.
4. **Decision protocol — VERIFIED, then REMOVED.** v1.2.0 shipped `.agent-os/product/decisions.md` with schema (DEC-XXX, status proposed/accepted/superseded, alternatives, consequences) and highest override priority. v1.4.1 CHANGELOG: "rarely used and didn't help future development" — deleted. v3 keeps only a "Decisions" bullet list inside each spec's shape.md. Human-in-loop is strong everywhere: every command mandates AskUserQuestion per step.
5. **Session→repo handoff — SHIPS.** `shape-spec.md`: Task 1 of every plan is always "Save spec documentation" (plan.md/shape.md/standards.md/references.md/visuals/) before any implementation; explicit gate — refuses to run outside plan mode. v2.1.1 also shipped per-task implementation docs + `verifications/final-verification` report.
6. **Escalation — PARTIAL.** Only local rules: "Always ask when uncertain — don't assume" (inject-standards scenario detection). No general uncovered-situation procedure.
7. **Canonical locations — SHIPS** (fixed tree above). New-kind procedure — NOTHING; new standards *folders* are freeform, auto-indexed.
8. **Inheritance/overrides — SHIPS, install-time, whole-file.** `config.yml` `profiles: x: inherits_from: y`; `scripts/common-functions.sh` builds chain (cycle + missing detection); `scripts/project-install.sh` copies base-first, later profile's same-path file clobbers earlier — file-level replacement only, zero merge/section semantics. Divergence handled by reverse `sync-to-profile.sh` (conflict prompt, backups). v2 additionally compiled `{{standards/*}}`, `{{workflows/*}}`, `{{IF}}` tags into commands and could emit standards as Claude Skills.
9. **Size budgets — PARTIAL.** Advisory only: "every word costs tokens", one-line index descriptions; no numbers, no enforcement.
10. **Plain language — PARTIAL.** Writing rules in discover-standards.md: lead with the rule, bullets over paragraphs, skip the obvious, good/bad exemplars.
11. **Answer-shape — PARTIAL.** Every command hard-templates its prompts/outputs (numbered-option questions, fixed injection blocks).
12. **Enforcement — advisory-dominant.** Deterministic machinery exists only at install/sync time (bash: chain resolution, index.yml regeneration, tag compilation). No hooks, no CI, no runtime validation of any doc.

## Lessons for our design

- CHALLENGES: copy-based inheritance (later file clobbers earlier, whole-file) forced them to build a reverse-sync script — resolve overrides at reference time, not by materializing copies.
- CHALLENGES: a formal decision register with IDs/statuses was shipped and abandoned as unused — decisions survived only embedded in per-task shaping notes.
- CONFIRMS: universal defaults overridden by more specific layer works, but only with dead-simple precedence (chain order, file-path identity).
- CONFIRMS: tiny routing index (one-line descriptions, deterministically rebuilt) + explicit stop-gate "persist artifacts as Task 1 / must be in plan mode".
- CHALLENGES: v3's retreat shows constitution layers rot where native tools improve — keep ours to what tools won't natively do (governance, authority, records).
