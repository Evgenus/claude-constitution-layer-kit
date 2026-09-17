---
id: research-project-tob-anthropic
type: non-authoritative
title: Trail of Bits & Anthropic repos — evidence report (2026-08-28)
status: inactive
---

# Trail of Bits & Anthropic repos — evidence report (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Second-pass per-org research.

## Trail of Bits (trailofbits/skills, 43 plugins)

1. Doc typing/authority — SHIPS. Fixed kind taxonomy per plugin: SKILL.md / references/ / workflows/ (prose) / root workflows/*.js (executable) / evals/ / tests/; AGENTS.md defines each kind's role; CLAUDE.md is just `@AGENTS.md` (single source).
2. Per-kind governance — SHIPS. AGENTS.md prescribes per-kind rules ("Phase 1 / repeat-until prose belongs in a workflow script, not SKILL.md"; security skills must carry a "Rationalizations to Reject" section); validator applies different frontmatter contracts per kind (skills/commands use `allowed-tools`, agents use `tools` — enforced because the loader silently ignores the wrong key).
3. IDs/links — SHIPS. `.github/scripts/validate_plugin_metadata.py`: dangling relative-reference check (code blocks stripped first), namespaced `subagent_type` (`plugin:agent`) resolved repo-wide, README-must-name-every-component check, kebab-case ≤64 chars, no hardcoded home paths.
4. Decision protocol/records — PARTIAL. No ADR register; decisions live as unusually dense rationale comments in CI/Makefile citing PR numbers ("the measurement is in the PR that added this comment"). CODEOWNERS per plugin.
5. Handoff/stop gates — PARTIAL. No session handoff docs; gates are `make check` mirroring CI 1:1 (Makefile states divergence = bug in Makefile) plus pre-commit.
6. Escalation — PARTIAL. AGENTS.md: use claude-code-guide subagent only for what the repo can't answer; warnings-vs-errors doctrine ("blocking on warnings teaches people to ignore the output").
7. Canonical locations — SHIPS. Mandated tree in AGENTS.md; validator errors on sidecar metadata dirs (.codex/, .opencode/) — one canonical metadata source.
8. Styling — SHIPS for code (ruff/shfmt/shellcheck pinned); markdownlint deliberately absent with measured rationale (12,400 violations → would be ignored).
9. Size budgets — SHIPS. SKILL_LINE_LIMIT=500 (WARNING, not error); plugin name ≤64 (error); progressive disclosure + "one level deep, no reference chains" rule.
10. Plain language — PARTIAL. Third-person trigger-rich descriptions required; "explain WHY not just WHAT"; no linter.
11. Answer-shape — PARTIAL. Eval graders per plugin (evals/*/graders/*.md) define acceptable output shapes; resources/ANALYSIS_FORMAT.md in audit-context-building.
12. Deterministic vs advisory — SHIPS, the gold standard. Errors = machine-decidable (metadata sync plugin.json↔marketplace.json, semver + version-increment vs merge-base, frontmatter YAML parseability, entry-point existence); warnings = judgment (length, dangling refs). Validators must pass `--self-test` (96-assertion floor) BEFORE validating; zero-discovery = failure everywhere; real-CLI loadability checks (Claude Code + Codex); LLM review (claude-review.yml) is additive, never the gate.

## Anthropic

- anthropics/skills: (1) PARTIAL — flat skills/ + spec/ (pointer to agentskills.io) + template/SKILL.md (frontmatter only). (2) SHIPS as prior art — skill-creator (scripts/quick_validate.py: allowed frontmatter keys whitelist, kebab ≤64, description ≤1024 no angle brackets; references/schemas.md JSON schemas for evals.json/history.json) and doc-coauthoring/SKILL.md — a document-production protocol (3 stages: context gathering w/ 5–10 numbered clarifying questions, section-by-section refinement, fresh-Claude reader test). (12) NOTHING — no .github, no CI; validation is tooling offered to authors, not enforced on the repo itself.
- anthropics/claude-code: PARTIAL — .claude/commands/ (commit-push-pr, dedupe, triage-issue = process-as-commands); CI is issue-lifecycle automation, no doc validation.
- anthropics/claude-cookbooks: SHIPS — registry.yaml typed by JSON Schema (.github/registry_schema.json), verify-authors.yml, links.yml (lychee), notebook-quality.yml + scripts/validate_notebooks.py (no empty cells/error outputs), claude-model-check.yml (stale IDs), claude-pr-review advisory; CLAUDE.md sets style + never-dated-model-IDs rule.

## Lessons for our design

- CONFIRMS: two-severity split — errors only for machine-decidable facts; judgment stays advisory (ToB doctrine, stated in-code).
- CONFIRMS: creation-time doc validation is real prior art — frontmatter contract per kind, dangling-ref check, registry-with-JSON-Schema (ToB validator; cookbooks registry.yaml).
- CONFIRMS: size budgets ship as numbers (500 lines warn, 64/1024 chars error), enforced, not aspirational.
- CHALLENGES: nobody ships a decision register; ToB puts decisions in PR-linked comments, Anthropic in doc-coauthoring's human-question protocol — our register needs to justify itself over those.
- CHALLENGES: validators themselves must be governed — ToB's `--self-test` + anti-vacuity (zero-found = broken) is table stakes we hadn't specified.
