---
id: research-aspect-06-canonical-location
type: non-authoritative
title: Aspect 6: Canonical location — comparison (2026-08-28)
status: inactive
---

# Aspect 6: Canonical location — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. Prose location table in root CLAUDE.md (native, guidance-only).** A "where documents live" table (kind → home dir) plus a "new kind: ask/define first" rule. Mechanism: native memory. Maturity: universal community practice (CLAUDE.md best-practice guides all carry a repo-layout section). Cost: ~10-15 lines of the 200-line budget. Weakness: probabilistic — placement drifts under long sessions and subagents, and the table itself becomes a second source of truth once a knowledge layer adds kinds.

**B. Machine-readable registry + PreToolUse hook (native hook + repo script).** One registry file (e.g. docs/registry.md or .yaml: kind → home glob → filename pattern → one-line purpose) as the single source of truth; a small PreToolUse hook matched on Write|Edit validates any created doc-extension file against the registry and exits 2 with stderr naming the correct home ("kind X lives in docs/decisions/; unregistered kinds require a registry entry first"). CLAUDE.md shrinks to a 2-line pointer + the new-kind procedure. Maturity: PreToolUse path-gating is a documented, widely blogged production pattern in 2026; the registry file is bespoke but trivial. Cost: ~60-100 lines of script, one registry file. Extensible by design: the knowledge layer adds kinds by appending registry entries — hook and guidance both update automatically.

**C. settings.json permission deny/ask path patterns (native).** Deterministic, zero code. Weakness: denylist-shaped — can block known-bad locations but cannot express "kind→dir mapping" or give the model a corrective message; unsuitable as the primary mechanism.

**D. Post-hoc placement lint (repo script in CI or Stop hook).** Catches drift after the fact; useful backstop, but the file already exists in the wrong place — corrections cost a round-trip.

**Recommended: B**, with a thin A on top (the CLAUDE.md pointer + procedure) and D as an optional CI backstop. Reasoning: canonical location is exactly the class of rule where deterministic enforcement beats instruction-following — violations are cheap to detect syntactically (path vs registry) and the exit-2 stderr channel converts each block into in-context teaching. The registry satisfies the extensibility requirement (later layers append entries, no prose edits), matches settled findings (small repo script, single-source ledger-style file), and keeps CLAUDE.md budget spend minimal.

**Open questions for the human:**
1. Should the hook gate only *new* file creation, or also flag edits/moves of misplaced existing docs?
2. May an agent add a registry entry autonomously (defining a new kind), or is that human-approval-only?
3. Registry format: YAML (script-friendly) vs Markdown table (human/model-friendly)?
