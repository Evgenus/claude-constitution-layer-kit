---
id: research-aspect-01-meta-types
type: non-authoritative
title: Aspect 1: Document meta-types — comparison (2026-08-28)
status: inactive
---

# Aspect 1: Document meta-types — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. In-file frontmatter declaration + always-on precedence rule.** Every repo .md carries YAML frontmatter `meta-type: current-state | task-record | non-authoritative`; the vocabulary and a ~5-line precedence rule live in root CLAUDE.md. Mechanism: native (CLAUDE.md) + convention. Maturity: high — frontmatter-as-schema is the settled docs-as-code pattern (MADR ADRs use YAML frontmatter for status; Front Matter CMS "content types"; 2025-26 "frontmatter-first" agent-context writing). Cost: ~5 CLAUDE.md lines + 3 frontmatter lines/doc. Covers declaration + reading-time arbitration; advisory only.

**B. Directory-encoded types with lazy-loaded semantics.** Type = subtree (Diátaxis quadrant-dirs, ADR/spec-kit archive-vs-active layout; OpenSpec's active-delta vs archived-spec split is exactly current-state vs task-record). Bind behavior via `.claude/rules/*.md` with `paths:` globs (e.g. `docs/archive/**` → "evidence only, never cite as current") so type semantics load only when a session touches that subtree. Mechanism: native. Maturity: high in docs-as-code and SDD tools. Cost: near zero ongoing. Weakness: type dies on file move; can't type files outside the tree; no per-file granularity.

**C. Hook-enforced declaration.** PreToolUse hook (matcher `Write|Edit`) runs the repo frontmatter-validation script (per settled finding); exit 2 blocks writing any .md with missing/invalid `meta-type`, message tells the session the vocabulary. Optional CI re-check. Mechanism: native hook + repo script. Maturity: PreToolUse blocking is a well-established 2025-26 enforcement pattern. Cost: ~50-line script + one hook entry. Covers declaration compliance only — cannot enforce that a session *respects* precedence when reading.

**Recommended: A + B + C combined, with distinct roles.** Frontmatter (A) is the declaration of record — it travels with the file into any context window, survives moves, and is machine-checkable. The precedence rule is a reading rule so it must be always-on: root CLAUDE.md only. Rules-with-paths (B) add subtree-level behavioral reinforcement for the archive/exhaust areas at zero always-on cost. The hook (C) makes the declaration invariant self-maintaining, since instruction-only conventions demonstrably drift. No third-party tool fits (consistent with settled findings).

**Open questions for the human:**
1. Is untyped = `non-authoritative` by default, or a validation error? (Fail-closed vs fail-safe.)
2. Precedence tiebreak within `current-state`: does anything (dates?) arbitrate two conflicting current-state docs?
3. Should directories mirror types (redundant encoding, drift risk) or stay orthogonal?
4. Are harness files (CLAUDE.md, skills, rules) themselves typed, or exempt from the vocabulary?
