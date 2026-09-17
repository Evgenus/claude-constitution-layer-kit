---
id: research-aspect-04-handoff-contract
type: non-authoritative
title: Aspect 4: Session→repo handoff contract — comparison (2026-08-28)
status: inactive
---

# Aspect 4: Session→repo handoff contract — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. Instruction-only "land the plane" protocol** — CLAUDE.md rule + a session-end skill (/handoff, /land) that tells Claude to commit/write defined artifact kinds (decision entry, handoff note, plan update) before finishing. Covers the full contract semantically, including content quality. Mechanism: native (memory + skill). Maturity: very common (HANDOVER.md/progress.md conventions widespread in 2025-26 community guides). Cost: ~10 CLAUDE.md lines + one skill. Weakness: purely probabilistic; skipped exactly when context is degraded at session end.

**B. Stop-hook deterministic gate** — repo script on the Stop event; exit code 2 (verified: blocks Claude from stopping and feeds stderr back as "you're not done") when checkable invariants fail: dirty working tree, no file created/modified this session under artifact directories, invalid artifact frontmatter (reuses the settled frontmatter-validation script; one-file-per-entry makes "artifact written this session" a trivial existence check). Mechanism: native hook + repo script. Maturity: pattern well documented; official docs confirm blocking semantics; known hazard is the infinite-loop case — hook must be conditional and respect the stop_hook_active input flag / a same-diff-hash bailout. Cost: one ~50-line script. Weakness: can only check form (files exist, tree clean), never content adequacy.

**C. SessionEnd capture hook** — fire-and-forget script that snapshots exhaust (transcript path, git stash/scratch-ref commit of uncommitted work). Mechanism: native hook + repo script. Maturity: works but verified non-blocking (exit codes ignored, session ends regardless) and has a known reliability gap (doesn't fire on all exit paths, e.g. anthropics/claude-code#35892). Cost: trivial. Weakness: safety net only — cannot enforce anything.

**D. External orchestrator harness** — third-party control planes that git-track sessions and gate phase transitions. Mature-ish but heavyweight, violates Claude-Code-native premise.

**Recommended: B as the enforcement spine, A as the semantic layer, C as optional safety net.** Reasoning: the contract's core claim — "work not in an artifact did not happen" — is exactly the class of invariant hooks exist for; Stop is the only event that both fires reliably and can block, so put the deterministic checks (clean tree, artifact-of-kind touched, frontmatter valid) there, and leave what's only instructable (what to write, which kind) to the instruction protocol. Never rely on SessionEnd for enforcement.

**Open questions for the human:** (1) Should a dirty tree hard-block (exit 2) or merely warn in interactive sessions? (2) Is every session required to produce an artifact, or is an explicit "no-artifact session" marker an allowed escape hatch? (3) Which artifact kinds are mandatory per session type?
