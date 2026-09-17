---
id: research-aspect-10-answer-shape
type: non-authoritative
title: Aspect 10: Answer-shape matching — comparison (2026-08-28)
status: inactive
---

# Aspect 10: Answer-shape matching — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Context: this behavior class is fully judgment-based — no hook or script can deterministically check "reply shape matched request shape." Label it as unverifiable norms. Claude Code's default system prompt already pushes concision and direct answers; anything added should reinforce, not fight, that.

**Candidate A — Built-in "Concise" output style (native, official, v2.1.237+; `"outputStyle": "Concise"`).** Covers answer-first/short-by-default only; not assumption-stating or vague-request restatement; not customizable. Mature, zero maintenance, zero authored text. Main conversation only.

**Candidate B — Custom project output style (native).** `.claude/output-styles/answer-shape.md` with `keep-coding-instructions: true` (keeps default engineering behavior), containing the three norms: match reply shape to request shape (yes/no first, question→answer not essay); state assumptions explicitly; on vague requests, restate the request back and confirm before acting (optionally via AskUserQuestion). Strongest placement: modifies the system prompt directly, and Claude Code re-reminds the model of a non-Default style mid-conversation — better adherence than CLAUDE.md's after-system-prompt user message. This is exactly the class of behavior output styles were built for, per official docs ("different role, tone, or default response format every turn"). Cost: one small file + `outputStyle` in checked-in .claude/settings.json. Limit: main conversation only (subagents unaffected — acceptable, since answer shape is a user-facing concern). Mature (official surface).

**Candidate C — 3–5 lines in root CLAUDE.md (native).** Always-on, survives compaction, but weakest placement for tone/format discipline, and spends the ~200-line budget on something output styles handle better.

**Candidate D — Clarification skill (third-party: Trail of Bits `ask-questions-if-underspecified` plugin, or home-grown).** Covers only the vague-request half, well (numbered questions, defaults fast-path, "state assumptions and confirm" fallback). Weakness: lazy skill triggering means the model must already recognize vagueness to invoke it — unreliable at exactly the needed moment. Mature (ToB-maintained).

**Recommended: B** — a single custom output style carrying all three norms, honestly labeled judgment-based/unverifiable in the constitution. A is the zero-cost fallback if the project won't ship a style; D is an optional add-on for heavyweight clarification flows.

**Open questions for the human:** (1) Is it acceptable for shared .claude/settings.json to force `outputStyle` over users' personal style choice? (2) Should vague-request clarification use AskUserQuestion or prose restatement?
