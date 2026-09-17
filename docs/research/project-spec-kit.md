---
id: research-project-spec-kit
type: non-authoritative
title: spec-kit — evidence report (2026-08-28)
status: inactive
---

# spec-kit — evidence report (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Second-pass per-project research (repo read at main, pushed 2026-08-28).

1. **Document typing/authority — PARTIAL.** Fixed pipeline kinds (spec/plan/tasks/checklist per feature dir; `templates/plan-template.md` names research.md, data-model.md, quickstart.md, contracts/). Authority is ordered ad hoc: constitution "non-negotiable", conflicts auto-CRITICAL (`templates/commands/analyze.md` "Constitution Authority"). Current-state vs task-record is NOT typed — it's a team convention doc: `docs/concepts/spec-persistence.md` names flow-back / flow-forward (immutable historical dirs) / living-spec models, explicitly "none is the default", record your choice in the constitution.

2. **Policy-based governance — PARTIAL, different shape.** No per-kind policy docs. Closest: (a) each `/speckit.*` command file IS the creation-procedure+acceptance policy for its kind (`templates/commands/*.md`); (b) constitution is quasi-self-describing — carries its own amendment procedure, SemVer policy, and a "Sync Impact Report" HTML comment listing dependent templates reviewed for alignment (`.specify/memory/constitution.md` lines 1–32, `templates/commands/constitution.md` step 4). No path-pattern governance of frontmatter-less files.

3. **Referenceability — SHIPS.** Stable IDs everywhere: FR-###/SC-### (`templates/spec-template.md`), T### + [P]/[US1] tags (`templates/tasks-template.md`), CHK### (`templates/checklist-template.md`), roadmap R# ids declared "immutable once referenced" with bidirectional plain-text links, deliberately "greppable, no metadata schema" (`docs/concepts/spec-of-specs.md`).

4. **Decision protocol — SHIPS.** `/speckit.clarify`: ≤5 questions, one at a time, MC table A–E or ≤5-word answer, recommended option stated first, answers logged as `## Clarifications / ### Session YYYY-MM-DD / - Q:…→A:…` then propagated into sections (`templates/commands/clarify.md`). Decision records: `extensions/assess/commands/speckit.assess.decide.md` writes go/kill/needs-clarification verdicts to `.specify/assessments/<slug>/decision.md`, refuses silent overwrite. No repo-wide ADR system.

5. **Session→repo handoff — SHIPS.** Every command's output is a file at a scripted path; `scripts/bash/check-prerequisites.sh` hard-fails (exit 1) if upstream artifacts missing, with "Run /speckit.plan first" messages. Stop gates: `/speckit.implement` STOPs on unchecked checklist items and asks yes/no (`templates/commands/implement.md:81`); plan's Constitution Check "GATE: must pass before Phase 0".

6. **Escalation — PARTIAL.** Only local rules ("if unclear whether input is constitution content, ask before changing", constitution.md:33; TODO(FIELD) markers for unknowns). No general no-procedure-covers-this escalation channel.

7. **Canonical locations — SHIPS** (fixed kinds): `specs/NNN-slug/` with sequential numbering computed by `scripts/bash/create-new-feature.sh`; memory at `.specify/memory/constitution.md`; assessments under `.specify/assessments/`. **NOTHING** for new-kind procedure — new kinds require writing an extension (`extensions/EXTENSION-DEVELOPMENT-GUIDE.md`).

8. **Styling inheritance — SHIPS (for templates, not prose).** 4-layer resolution: `.specify/templates/overrides/` → presets (priority-sorted `.registry`) → extensions → core (`scripts/bash/common.sh` resolve_template, ~l.497). Prose style only as inline command rules (constitution.md "Formatting & Style Requirements").

9. **Size budgets — PARTIAL.** Interaction budgets (≤5 clarify Qs, ≤3 NEEDS CLARIFICATION markers, 50-finding cap in analyze), all advisory prompt text. No document-size limits, no enforcement.

10. **Plain language — PARTIAL.** Pointed but narrow: clarify.md:146-147 ("everyday wording; jargon only if defined in same sentence; a reader who doesn't know Spec Kit must answer from the Question line alone"); analyze flags vague adjectives; constitution step 5 bans vague "should".

11. **Answer shapes — SHIPS.** Highly prescriptive per command: exact MC table format, `**Recommended:** Option X`, fixed report tables with severity/coverage/metrics (analyze.md section 6), Given/When/Then scenarios.

12. **Enforcement — mostly advisory.** Deterministic: prerequisite/feature-creation/template-resolution scripts (tri-implemented bash/ps/python), path-safety checks, CI (ruff/markdownlint/pytest) — but CI governs spec-kit's own repo, not user artifacts. Everything about generated-document quality (constitution gates, analyze severities, checklist validation) is LLM instruction, read-only-by-convention. Error messages consistently pair error + next command.

## Lessons for our design

- **CONFIRMS** per-kind creation procedure + acceptance criteria living in one doc per kind — spec-kit does exactly this via command files; steal the "instructions and template resolved as one unit" coupling.
- **CONFIRMS** plain-text greppable IDs/links over metadata schema (roadmap R#, FR-###) — works with zero tooling.
- **STEAL** from constitution: Sync Impact Report (amendment must list dependent docs reviewed) and governance SemVer — cheap propagation discipline for a root policy.
- **CHALLENGES** advisory-only enforcement: spec-kit's only deterministic checks are existence/ordering scripts; doc-quality gates are pure prompt text — our design should push more into hooks/CI than spec-kit does.
- **AVOID** spec-kit's gap: no document typing beyond the pipeline, no path-pattern governance, no new-kind procedure short of writing an extension — our per-kind policy registry fills real holes, not reinvention.
