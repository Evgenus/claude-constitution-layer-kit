---
id: research-aspect-03-decision-protocol
type: non-authoritative
title: Aspect 3: Decision-question protocol — comparison (2026-08-28)
status: inactive
---

# Aspect 3: Decision-question protocol — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Candidate approaches:

1. **CLAUDE.md protocol lines only.** ~10 always-on lines: "when a human decision is needed, present options + pros/cons + one recommendation, use AskUserQuestion, one decision per message, record it." Native, zero infrastructure. Maturity: universal pattern. Cost: burns root-file budget; instruction-following on multi-step protocols degrades in long sessions; no template co-located.

2. **Dedicated skill (.claude/skills/decision/SKILL.md) + AskUserQuestion + one-file-per-decision records.** Skill body carries the full protocol and a MADR-lite record template (MADR 4.0, 2024, is the de-facto community standard: NNNN-slug.md, one decision per file, Considered Options with pros/cons — matches the ONE FILE PER ENTRY finding exactly). Body loads lazily on auto-trigger or /decision; CLAUDE.md keeps 2-3 pointer lines. The ask surface is native AskUserQuestion: 1-4 questions per call (protocol says: use 1), 2-4 options each, "Other" always offered, and the tool's own convention is recommended-option-first labeled "(Recommended)" — the protocol maps onto it natively. Reasoning + named decider go in prose before the tool call and into the record after. Native mechanism, high maturity, cost ≈ one skill file + template.

3. **Hook + script enforcement layer.** PostToolUse hook on AskUserQuestion appends a reminder to write the record; Stop hook or small repo script validates decisions/*.md frontmatter (id, date, decider, status, supersedes). Repo-script class, consistent with settled "frontmatter validation = small repo script." Cost: script maintenance; enforces existence, not quality.

4. **Third-party ADR tooling (adr-tools, log4brains, marketplace ADR skills).** Mature templates/tooling but protocol-unaware, adds dependencies, and marketplace skills duplicate what a 50-line local skill does.

**Recommended: approach 2, with approach 3's validator as an optional add-on.** Reasoning: it is the only design where the interaction protocol and the record format live in one lazily-loaded unit, uses the native surface built for exactly this (AskUserQuestion's recommended-first convention), and satisfies one-file-per-entry via MADR. Known native constraints the design must encode: AskUserQuestion is unavailable inside subagents (GH #12890/#18721) — so the protocol rule "subagents never talk to the decider" is partly self-enforcing; subagents must instead return a "decision needed" package to the main session, which asks. ExitPlanMode is binary plan-approval only — use it as a gate, not a decision menu. Headless runs auto-resolve AskUserQuestion empty — protocol needs a fallback (write record as "proposed", stop).

**Open questions for the human:** (a) Should decisions/ records be repo-committed or a gitignored operator log? (b) Is the frontmatter validator wanted at v1 or deferred?
