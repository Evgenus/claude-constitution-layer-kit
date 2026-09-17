---
id: research-aspect-05-escalation
type: non-authoritative
title: Aspect 5: Escalation default — comparison (2026-08-28)
status: inactive
---

# Aspect 5: Escalation default — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Honest framing first: the trigger condition ("no covering procedure exists") is pure model judgment. No hook can detect it. What IS deterministically enforceable: the shape of the stop (record exists, well-formed) once the model has declared one, and blanket denials of risky actions that force the model into a stop.

**A. Root CLAUDE.md prime directive (native, advisory, mature, ~free).** State the rule imperatively in the first ~40 lines of root CLAUDE.md — empirical work (arXiv 2509.14744, 2605.10039; community consensus) shows top-of-file rules get the most consistent adherence and compliance attenuates within-session, so it must be short, absolute, and paired with a runnable action ("write an escalation file, then stop"), not a description. This is the only always-on, compaction-surviving surface — the rule belongs here, not in an output style (output styles are for tone/format and apply to the main conversation only — subagents would not see the rule) and not only in a skill (skill bodies are lazy — the model must already know to invoke it).

**B. Escalation skill carrying the record template (native, advisory, mature, one skill file).** An `escalate` skill whose description ("invoke when no documented procedure covers the situation") is always in context, body loads on use: template for one file per entry in `escalations/` (timestamp, situation, why no procedure covers it, options considered, what was NOT done), then instruct: stop, do nothing further. Interactive sessions can also use AskUserQuestion; the file is the durable record either way.

**C. Hook reinforcement (native + repo script, medium maturity, ~50 lines).** (1) UserPromptSubmit hook injecting a one-line reminder of the rule each turn — counters within-session attenuation, the documented failure mode. (2) Stop hook script: if the final message signals a stop/blocked state (keyword sentinel the constitution mandates, e.g. "ESCALATION:"), exit 2 unless a matching well-formed escalations/ file exists — deterministically enforces record-before-stop, not the judgment itself. (3) settings deny/ask rules make the agent hit hard walls that naturally convert improvisation into escalation.

**D. Third-party guardrail classifiers** — immature for this niche, conflicts with settled MCP-assist-only stance; skip.

**Recommendation: A + B + C combined.** A is the norm (placement matters most), B makes the correct behavior cheap and gives the one-file-per-entry record, C is the only deterministic backstop available. Accept openly that the trigger stays advisory.

**Open questions for the human:** Should the Stop-hook sentinel check be mandatory or optional per project? Should escalation files be git-committed by the agent before stopping?

Sources: Claude Code hooks reference; Anthropic auto-mode engineering post; arXiv 2509.14744; community rule-enforcement pattern posts.
