---
id: research-second-pass-consolidated
type: non-authoritative
title: Second-pass research — consolidated findings (2026-08-28)
status: inactive
---

# Second-pass research — consolidated findings (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Input: six per-project evidence reports (spec-kit, OpenSpec, Agent OS, ccpm + claude-conductor, SuperClaude + claude-flow, Trail of Bits + Anthropic). This document states only what changes or hardens relative to the first-pass per-aspect comparisons. Sources: the six sibling `2026-08-28-project-*.md` files.

## Verdicts on our standing choices

1. **Policy model (D20) — CONFIRMED with real prior art.** OpenSpec's `schema.yaml` is a working per-kind policy system: {id, path glob, template, creation instruction, dependency DAG}, project-forkable, cycle-validated, with a self-describing meta-spec governing its own conventions. Weaker echoes: ccpm's per-phase reference files, conductor's monolithic self-describing meta-doc, spec-kit's command-files-as-policies. Our modular per-kind policy *documents* + path-pattern governance remain the fullest form, but the shape is proven, not invented.
2. **Frontmatter as primary mapping — CHALLENGED, not overturned.** OpenSpec governs frontmatter-less markdown entirely by path pattern + heading grammar. Evidence that path-first is viable; our reasons for frontmatter-first (type travels with the file on move; machine-checkable in isolation) still stand, but J1's scope ruling should weigh path-pattern governance as a first-class mode, not a fallback. Note: ruling that way would loosen D20's parenthetical ("for formats that cannot carry frontmatter") and therefore requires a recorded D20 amendment, not just a J1 answer.
3. **Decision register — CHALLENGED by three independent data points.** Agent OS shipped a DEC-XXX register and deleted it ("rarely used"); OpenSpec never tooled decisions; ToB keeps decisions in PR-linked comments. Counter-evidence: claude-flow ships ~350 ADRs actively, and our own design process is already running on a register. Lesson: registers die of friction, not concept — records must be cheap (short template, written by the agent at ask-time, zero ceremony) and read (loaded at relevant moments), or they rot.
4. **Deterministic-vs-advisory split (D17) — STRONGLY CONFIRMED; one refinement.** ToB doctrine: errors only for machine-decidable facts; judgment-based findings are warnings ("blocking on warnings teaches people to ignore the output"); LLM review additive, never the gate. claude-flow states context rules are "probabilistic — the model can and does ignore them." Refinement: rule-priority *tiers* in prose (SuperClaude 🔴🟡🟢) have zero validation evidence — the only meaningful tier boundary is enforced-vs-advisory.
5. **Tiny always-on core — CONFIRMED with numbers.** claude-flow caps its always-on constitution at ~60 lines and cites compliance decay past ~100 lines; ToB's CLAUDE.md is one `@AGENTS.md` line. Our ~200-line ceiling should be treated as an upper bound, with the constitution aiming far lower.
6. **Teach-through-errors — CONFIRMED as mature practice.** OpenSpec pairs every validator message with fix + example and shares constants between writer and checker so they cannot drift; spec-kit pairs every error with the next command to run.
7. **Greppable plain-text IDs — CONFIRMED** (spec-kit ships FR-###/T### stable IDs, and declares its roadmap R# ids "immutable once referenced"; conductor's ID grammar + tag-based bidirectional links). OpenSpec's headers-as-IDs with a RENAMED FROM/TO protocol is an alternative for sub-file anchors worth noting against our `<a id>` choice.
8. **Escalation-by-default — NOVEL, stands.** Nobody ships blanket "no procedure → stop, record, escalate." claude-flow's typed authority levels + `escalationRequired` is the nearest machinery. Our design fills a real gap; no prior art to copy, none to defer to.
9. **Budgets — nuance found.** ToB ships numeric budgets with a split: hard caps as errors (name ≤64, description ≤1024), length as WARNING (500 lines). Conductor governs growth by lifecycle (500-line compaction, "move & summarize, never delete") rather than authoring caps. Feeds A3 (warn-band question) with real evidence on both sides.
10. **Inheritance/overrides (D22) — CONFIRMED, with a named anti-pattern.** Agent OS's copy-based whole-file inheritance forced a reverse-sync tool; resolve overrides at reference time, never by materializing copies. OpenSpec's layered config (CLI > change > project > built-in) is the working pattern.

## New obligations surfaced (added to phase2-open-questions as J12–J13)

- **Validator self-governance (ToB):** check scripts must pass a `--self-test` before validating, and zero-files-discovered must be a failure, not a pass (anti-vacuity). We had red→green fixtures; self-test + anti-vacuity were missing.
- **Sync Impact discipline (spec-kit):** amendments to the root policy (and possibly any policy) carry a short "dependent documents reviewed" note — cheap propagation discipline for policy changes.

## Two lessons without a question slot (design-shaping, no decision needed now)

- **Archive as state transition (OpenSpec):** closing a task record programmatically updates current-state documents, then archives. Constitution-level note for the handoff contract; full mechanics belong to the knowledge layer (D9/D2).
- **Rot warning (Agent OS v3):** constitution layers rot where native tooling improves — keep ours to what the platform will not natively do (governance, authority, records), which is where every surveyed project is thinnest.
