---
id: research-aspect-07-styling-defaults
type: non-authoritative
title: Aspect 7: Documentation styling defaults — comparison (2026-08-28)
status: inactive
---

# Aspect 7: Documentation styling defaults — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. Rules file with paths globs (native).** One .claude/rules/doc-style.md with `paths: ["docs/**/*.md", "*.md"]` frontmatter; lazy-loads exactly when a session touches a matching doc file. Covers the whole defaults sheet (Mermaid-first, pseudocode over formulas, founding entries + lazy additions appended in place). Mechanism: native. Maturity: stable, verified surface. Cost: near-zero — pays context only in doc-touching sessions; sole gap is a session that hasn't yet created the file (rule fires on first write, arguably late for pre-write decisions).

**B. Lines in root CLAUDE.md (native).** Defaults inlined always-on. Covers same content; guaranteed visibility incl. pre-write. Cost: burns the ~200-line ceiling in every session, doc-related or not; scales badly as defaults accrete lazily. Maturity: stable.

**C. Doc-authoring skill (native).** Defaults as skill body, loaded on invocation. Suits procedural workflows (scaffold-a-doc), but auto-relevance triggering is unreliable for "am I writing prose right now," and a short defaults sheet doesn't need a body/description split. Cost: description slot at startup, invocation flakiness. Maturity: stable mechanism, wrong shape here.

**D. Checkable-subset enforcement (repo script / third-party).** Honest scope: styling is ~90% advisory. Checkable: (1) Mermaid fences actually parse — `maid` (probelabs) or `@mermaid-lint/cli` are 2025-era linters built for AI-generated diagrams; a tiny repo script grepping for forbidden patterns (e.g. LaTeX $$ blocks where pseudocode is mandated) also works; (2) markdownlint for mechanical Markdown hygiene; (3) Vale only if prose-term rules ever get founded (settled finding). GitHub renders Mermaid natively since 2022 and still does in 2026 (minor limits: no layout control, some chars/links break), so Mermaid-first remains the right portable default. Maturity: markdownlint mature; Mermaid linters young but functional. Cost: dev-dep or one script; CI seconds.

**Recommended:** A as the carrier, with one pointer line in root CLAUDE.md ("doc styling defaults: .claude/rules/doc-style.md — read before authoring any document") to close the pre-first-write gap cheaply, plus D's Mermaid-parse check as the only founded enforcement (repo script or `maid`, added lazily at first broken diagram, per settled repo-script preference). Everything else stays explicitly advisory in the rule text itself.

**Open questions for the human:** (1) Glob scope — all **/*.md or only designated doc dirs (affects whether CLAUDE.md/rules files self-apply)? (2) Add Mermaid parse-check now or at first breakage? (3) Is the CLAUDE.md pointer line worth one ceiling line?
