---
id: research-aspect-02-referenceability
type: non-authoritative
title: Aspect 2: Document referenceability — comparison (2026-08-28)
status: inactive
---

# Aspect 2: Document referenceability — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. Path-only references (relative repo paths, whole-file granularity).** Mechanism: native convention — Grep/Glob/Read resolve paths in one tool call, zero infrastructure. Maturity: universal. Cost: free, but no sub-file precision; file renames rot references silently unless a checker runs; sections referenced by heading text rot on any rewording.

**B. Canonical document IDs in filenames (ADR-style).** Each referenceable doc gets a monotonic, never-reused ID baked into its filename (`DEC-0042-runtime-choice.md`) and frontmatter. References are the bare ID (`DEC-0042`), resolvable by one Glob (`*DEC-0042*`) or Grep — cheapest possible for a session, and the reference survives directory moves and title edits. Mechanism: convention + the already-settled small frontmatter script (add ID-uniqueness check). Maturity: very high (Nygard ADR practice; supersede-don't-edit semantics are standard). Cost: near zero; applies naturally to the settled one-file-per-entry ledger docs.

**C. Explicit HTML anchors + lychee fragment checking.** For sub-file targets in living docs: `<a id="stable-name"></a>` above the section (renders everywhere GitHub-flavored; `{#id}` does not render on GitHub), referenced as `path#stable-name`, validated by the already-settled lychee ≥0.24.2 with `--include-fragments` (checks anchors offline in Markdown/HTML). Mechanism: convention + third-party tool already in the stack. Maturity: solid; lychee fragment checking is proven. Cost: small authoring discipline; anchors must never be renamed once referenced.

**D. Wiki-links (`[[doc]]`).** Requires a resolver (Obsidian-style tooling); Grep can find the link text but not resolve it to a path natively. Rejected fit for Claude Code semantics.

**Recommendation: B + A + C layered, tied to volatility class.** Immutable ledger entries (decisions, goals) get canonical IDs in filenames (B) and are the only cross-doc reference targets encouraged in prose — one Glob resolves them, and immutability means references never rot. Living docs are referenced at file level by path (A); when sub-file precision is genuinely needed, add an explicit `<a id>` anchor (C), never a heading-text slug. Volatility rule stated in the constitution: an anchor or ID, once referenced, is frozen — content changes, identifiers don't; superseding replaces referencing. Lychee with `--include-fragments` in the existing check catches the rest. Reasoning: this matches Claude Code's cheap primitives (Glob/Grep favor filenames over rendered slugs), reuses two already-settled tools, and puts the stability burden on identifiers rather than on discipline about heading wording.

**Open questions for the human:**
- ID namespace scheme: one global sequence or per-type prefixes (DEC-, GOAL-, …)?
- Should code→doc references (IDs in code comments) be checked by the same script, or left unchecked?
- Run lychee in a hook (PostToolUse/Stop) or only in CI/manual script?
