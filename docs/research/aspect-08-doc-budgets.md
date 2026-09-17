---
id: research-aspect-08-doc-budgets
type: non-authoritative
title: Aspect 8: Document budgets — comparison (2026-08-28)
status: inactive
---

# Aspect 8: Document budgets — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. Central registry + PostToolUse hook (native hook + repo script).** One small registry file (e.g. `.claude/doc-budgets.json`: glob → char ceiling per doc kind). A PostToolUse hook on Write|Edit matches the touched path, counts characters (Python `len()` on decoded text, not `wc -c` bytes), exits 2 on overshoot — stderr goes to the model as feedback after the write lands, which is exactly the settled post-hoc semantics (file exists; model trims next). Advisory side: the same registry is rendered into one line in the relevant .claude/rules/*.md (paths-matched, lazy) so the ceiling reaches the authoring session before writing; single source, no drift. Maturity: hooks-for-enforcement is the dominant 2025-26 community pattern ("hooks fire every time; CLAUDE.md instructions don't"). Cost: ~40-line script + registry.

**B. Per-document frontmatter `budget:` field + same hook.** Self-describing, ceiling visible on read. But it scatters budgets, needs a default anyway, and lets a document raise its own ceiling — the budget authority sits inside the thing being budgeted, which an agent can (and will) edit to pass the check. Fits the settled frontmatter-validation script only as a declared-vs-registry consistency check, not as the source of truth. Cost: low, hazard: self-exemption.

**C. Stop-hook / CI / pre-commit sweep (repo script).** Whole-tree scan against the registry; catches files created outside Write|Edit and drift from ceiling changes. Feedback is late (end of turn or post-session), so as the *only* mechanism it teaches nothing at authoring time. Cheap: reuse the same script with a `--all` flag.

**D. Third-party linters (claudelint claude-md-size etc.).** Real but narrow: CLAUDE.md-only, bytes not per-kind characters, default 40KB. Doesn't cover arbitrary doc kinds; another dependency. Precedent value only (confirms size-ceiling discipline is mainstream; skills ecosystem already hard-caps description at 1,024 chars).

**Recommended: A, with C as backstop** — one script, two entry points: PostToolUse Write|Edit hook (exit 2, per-file) and --all sweep in CI/pre-commit. Registry is the single source; rules-file advisory line is generated or hand-kept from it. Reasoning: registry keeps budget authority outside the budgeted file (B's flaw), PostToolUse gives deterministic same-turn teaching (C alone can't), and D can't express per-kind character ceilings. Error message as teaching surface: `docs/decisions/x.md: 9,412 chars; ceiling for kind 'decision' is 8,000 (over by 18%). Trim, split into a referenced file, or ask the human to raise the ceiling in .claude/doc-budgets.json.`

**Open questions for the human:** (1) Warn-band before hard fail (e.g. advisory at 90%)? (2) Should ceilings count frontmatter/code blocks or prose only? (3) Exempt paths (vendored/generated docs)?
