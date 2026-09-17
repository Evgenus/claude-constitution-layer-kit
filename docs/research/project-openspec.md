---
id: research-project-openspec
type: non-authoritative
title: OpenSpec — evidence report (2026-08-28)
status: inactive
---

# OpenSpec — evidence report (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Second-pass per-project research (repo: Fission-AI/OpenSpec, main).

1. **Doc typing/authority — SHIPS.** Hard three-tier split codified in `openspec/specs/openspec-conventions/spec.md` (Project Structure req): `openspec/specs/` = current deployed truth; `openspec/changes/<name>/` = active task records (proposal/specs-deltas/design/tasks); `changes/archive/YYYY-MM-DD-<name>/` = closed evidence. Non-authoritative notes (`openspec/explorations/`) exist but untooled.

2. **Policy-based governance — SHIPS, strongest prior art.** `schemas/spec-driven/schema.yaml`: per-kind entries {id, `generates` path glob, template, `instruction` (creation procedure + acceptance rules), `requires` dep-DAG}. Loaded with Zod + duplicate/ref/cycle validation (`src/core/artifact-graph/schema.ts`). Projects fork schemas into `openspec/schemas/<name>/` via `openspec schema fork` (`docs/customization.md`). Self-describing root: `openspec-conventions` spec is a meta-spec governing OpenSpec's own conventions in its own format. Path-pattern governance of frontmatter-less files: all docs are plain markdown, kind determined purely by path + heading structure; only per-change flags live in sidecar `.openspec.yaml` (skip_specs, schema).

3. **Referenceability — PARTIAL.** Requirement headers ARE canonical IDs: `### Requirement: <name>`, normalized case-sensitive matching, explicit RENAMED FROM/TO protocol, duplicate headers = validation error (conventions spec). Spec id = dir path. Cross-repo reference index with fetch recipes (`src/core/references.ts`). No intra-doc anchor/link convention.

4. **Decision protocol — PARTIAL.** design.md Decisions section (choice+rationale+alternatives) and Open Questions rule: "if a question would change specs/approach/tasks, ask the user — don't guess" (schema.yaml). No standalone decision-record kind; they dogfood `openspec/initiatives/*/decisions.md` untooled.

5. **Session→repo handoff — SHIPS.** Work exists only as change artifacts. Explicit planning-boundary stop gate: "authorizes planning only… stop, wait for a new user request" (`src/core/templates/workflows/propose.ts`). Apply pauses on ambiguity, "never silently narrow scope" (`workflows/apply-change.ts`). Archive-on-close: `openspec archive` merges deltas into main specs by header match, conflict-detects, then moves to dated archive (`src/core/archive.ts`).

6. **Escalation — PARTIAL.** Materiality threshold for asking vs assuming; stop-on-lookup-failure rules in archive workflow. No general "no procedure covers this" channel.

7. **Canonical locations — SHIPS.** Fixed tree in conventions spec; `generates` paths per kind. New kind = add artifact entry to forked schema.yaml (cycle-validated).

8. **Styling/inheritance — SHIPS.** `openspec/config.yaml`: `context` injected into all artifacts, `rules` per kind, `operations.*.guidance` per operation; resolution CLI flag > change metadata > project config > built-in; advisory guidance explicitly cannot override controlling workflow (`docs/customization.md`).

9. **Size budgets — PARTIAL.** Numeric: Why 50–1000 chars, Purpose ≥50, requirement >500 warn, >10 deltas warn, 50KB context/index caps (`src/core/validation/constants.ts`). Page budgets advisory only.

10. **Plain language — PARTIAL.** SHALL/MUST enforced (strict-gated); behavior-vs-implementation boundary advisory. Superb internal style guide (`.agents/skills/write-openspec-docs/writing.md`: retrievability test, "dumb sentences, smart structure") — not shipped to users.

11. **Answer shapes — SHIPS (machine).** `docs/agent-contract.md`: one JSON doc/invocation, shared diagnostic envelope {severity, code, message, target?, fix?}, exit-code + null-shape contract. Doc shapes fixed by templates (WHEN/THEN scenarios, `- [ ] X.Y` checkboxes parsed for progress).

12. **Enforcement — SHIPS.** Deterministic `openspec validate` (ERROR/WARNING/INFO, `--strict` promotes, line/col) + archive conflict detection; advisory layer = instructions/rules. Error design: every message pairs detection with remediation + example (`GUIDE_*` snippets); placeholder text defined once and shared between writer and checker so validation can't drift (`constants.ts` comment).

## Lessons for our design

- **CONFIRMS** current-state/task-record split: closing a task *programmatically updates* current-state docs (delta merge), not just archives — archive is a state transition, not a move.
- **CONFIRMS** per-kind policy docs: schema.yaml = {path pattern, template, creation procedure, deps} per kind, project-forkable; validated as a DAG.
- **CONFIRMS** teach-through-errors: every validator message carries a fix + example; strict mode separates blocking from advisory.
- **CHALLENGES** frontmatter: OpenSpec governs frontmatter-less markdown entirely by path pattern + heading grammar (headers as IDs); sidecar yaml only for flags.
- **CHALLENGES** decision records: even this governance-heavy tool never tooled standalone decisions (buried in design.md; register only dogfooded) — a real gap our design can fill, but evidence that decision capture resists schema enforcement.
