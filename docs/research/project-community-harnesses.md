---
id: research-project-community-harnesses
type: non-authoritative
title: Community harnesses — evidence report (2026-08-28)
status: inactive
---

# Community harnesses — evidence report (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Second-pass discovery research. Scanned: hesreallyhim/awesome-claude-code (full README) + GitHub repo searches ("documentation framework", "ADR decision", "session handoff", "governance"). Shortlist considered: automazeio/ccpm (per-kind doc schemas + scripts); superbasicstudio/claude-conductor (pure doc framework); GWUDCAP/cc-sessions (hook-enforced DAIC gates, 1.5k★ but dormant since 12/2025); OthmanAdi/planning-with-files (26k★, plan-docs only, not doc governance); rvdbreemen/adr-kit (deterministic ADR CI enforcement, 5★); EvolveHQ/docflow (ADR lifecycle skills, 10★); me2resh/agent-decision-record (AgDR standard, 43★); codenamev/ai-software-architect (ADRs+reviews, 76★); alexeykrol/claude-code-starter (meta-doc framework, 193★); jjanczur/tyran (hook gates, 87★).

## 1) automazeio/ccpm — 8,353★, active (pushed 2026-03), now a Claude Code skill

- Doc typing/authority: SHIPS — 4 typed kinds (PRD/epic/task/progress), strict traceability chain PRD→epic→tasks (`skill/ccpm/references/conventions.md`).
- Per-kind policy docs: PARTIAL — one policy file per lifecycle phase (`references/plan.md`, `structure.md`, `sync.md`, `execute.md`, `track.md`) each defining triggers, preflight checks, templates, postflight; `SKILL.md` is a self-describing root routing to them. No path-pattern governance; kinds hardcoded, no new-kind procedure.
- IDs/anchors/links: PARTIAL — kebab-case names = filenames; task files renamed to GitHub issue numbers after sync; explicit rule "don't hardcode deps by filename, use `depends_on` array"; frontmatter `prd:`/`github:` fields as links. No in-doc anchors.
- Decision protocol/records: PARTIAL — mandatory brainstorming interview before PRD; confirm-before-overwrite gates. No decision-record artifact.
- Handoff/stop gates: SHIPS — every phase ends with explicit confirmation + suggested next command; `execution-status.md`, per-stream `updates/<N>/stream-A.md` for parallel-agent handoff.
- Escalation: PARTIAL — confirm on overwrite/completed-epic warnings only.
- Canonical locations: SHIPS — full tree spec in `conventions.md` (`.claude/prds/`, `.claude/epics/<name>/`, `archived/`).
- Styling: NOTHING. Size budgets: PARTIAL (≤10 tasks/epic). Plain language: NOTHING. Answer shapes: PARTIAL (scripted outputs = fixed shapes).
- Deterministic enforcement: SHIPS — "Script-First Rule" (`SKILL.md`): 12 bash scripts for all read/report ops; `references/scripts/validate.sh` checks tree, orphans, broken `depends_on` refs, missing frontmatter; repo-safety + no-force-push guards. Advisory otherwise (no hooks).

## 2) superbasicstudio/claude-conductor — 380★, npm CLI, pushed 2026-05

- Doc typing: SHIPS — 13 fixed doc kinds, each with Purpose + Required Elements (`templates/CONDUCTOR.md`, `templates/*.md`).
- Per-kind policy: PARTIAL — closest prior art found: `CONDUCTOR.md` is a self-describing root ("Read me first") that defines, per kind, purpose/required sections/ID formats/maintenance cadence, plus 10 "Documentation Optimization Rules". But it's one monolithic meta-doc, not per-kind policy files; no path patterns.
- IDs/anchors/links: SHIPS — `ERR-YYYY-MM-DD-NNN`, `TASK-YYYY-MM-DD-NNN`, `FINDING/DECISION/BLOCKER-NNN`; HTML anchors `<!-- #name -->`; `|TASK:ID|`/`|ERROR:ID|` tags making JOURNAL↔ERRORS↔TASKS bidirectionally greppable; relative-path cross-link rule.
- Decision protocol/records: PARTIAL — DECISION-NNN entries in TASKS.md linked to ARCHITECTURE.md; journal "Design decisions" category; no human-approval protocol ("GOLDEN RULE": user decides all priority, `templates/CLAUDE.md`).
- Handoff/stop gates: SHIPS — Session Startup Checklist (check TASKS.md, last 2-3 journal entries); one-active-task rule; capture-context-before-switching; completion trigger archives to `TASKS_ARCHIVE/`.
- Escalation: PARTIAL — BLOCKED task state; never-deprioritize rule.
- Canonical locations: SHIPS (fixed root-level set); new-kind procedure: NOTHING.
- Styling: NOTHING. Size budgets: SHIPS — 500-line JOURNAL compaction rule, "move & summarize, never delete". Plain language: NOTHING.
- Answer shapes: SHIPS — `RESPONSE_STYLE_CONFIG.md`: confidence bars, tone control, celebration thresholds as CLAUDE.md settings.
- Deterministic enforcement: NOTHING — init CLI only; all rules advisory prose.

## Lessons for our design

- CONFIRMS: per-kind policy (purpose/template/criteria/procedure) exists only embryonically — conductor's monolithic meta-doc, ccpm's per-phase files; a modular self-describing policy system with path-pattern governance has no direct prior art. Genuine gap.
- CONFIRMS: canonical ID grammars + tag-based bidirectional linking (conductor) demonstrably work for greppable cross-artifact traceability.
- CONFIRMS: deterministic validation as plain bash over frontmatter/tree (ccpm's validate.sh) is cheap and adopted at 8k★ scale — enforce structure mechanically, reserve LLM for content.
- CHALLENGES: neither ships decision *records* as first-class governed documents with human sign-off protocol — community treats decisions as journal entries or interviews; our stronger protocol needs its own justification.
- CHALLENGES: size budgets appear as compaction/archival rules (500-line + summarize-don't-delete), not authoring caps — consider governing growth via lifecycle rules, not just budgets.
