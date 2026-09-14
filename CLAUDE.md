# Constitution Kit — Session Guide

This repository is the **constitution kit**: a portable, project-agnostic governance layer for Claude Code projects, shipped as plugins. It contains the semantic kernel, the module template, and the modules. It contains **no project content, ever**.

Read before any work:
- `INTENT.md` — what this repo is for and what it is not.
- `kernel/CONVENTIONS.md` — the semantic kernel (one page). Authoritative for all vocabulary: envelope, meta-types, governance binding, stakes, decision records, dials, naming.
- `module-template/MODULE.md` — the fixed shape every module fills.
- `docs/rollout-plan.md` — module specs and the traceability matrix (requirement rows per module).

## Laws of this repository

1. **Kernel is authoritative; never restate it.** Modules and documents reference kernel definitions by name — duplication is a defect.
2. **Portability (kernel §6):** no file in a module references any project — no paths, names, repos, values. Project specifics enter only through the module's dials namespace. Test: the module installs and operates on an empty repository using defaults alone.
3. **Sibling independence:** modules depend on the kernel and nothing else. Sibling references only as optional enhancements ("when `const-x` is installed…"). Test: kernel + this module alone on a bare repo is a functioning installation. If a module seems to need a sibling, the shared concept belongs in the kernel — raise that as a `process`-stakes decision instead of coupling.
4. **A module implements exactly its matrix rows.** Its `MODULE.md` cites them. Content beyond its rows is scope creep; a missing row is incompleteness. Both are review findings.
5. **Enforcement honesty:** every artifact is `gate` (deterministic, red = fix) or `advisory` (judgment-shaping) — declared, never blurred. Nothing judgment-based is dressed as a check.
6. **Teaching errors:** every gate's error message states what failed, why the rule exists (one clause), and the exact fix. Error messages are designed content, reviewed like code.
7. **Every gate ships its red→green fixture** in `modules/<name>/tests/` — one input that fails without the check and passes with it.
8. **Sizes in characters, never tokens.**
9. **Kit decisions follow the kernel's own stakes triage.** Routine → act, note in the commit. `process` (most kit changes) → decision record in `docs/decisions/`, one human yes in the PR. Kernel changes are always recorded. A record is `active` while its ruling is being applied and `inactive` once applied (born `inactive` when applied in its own commit); reversing a ruling is a new record, never an edit of the old one. Current-state documents are superseded by in-place edit, named in the commit message; unreferenced documents are deleted — git is the archive.

## Session conduct

- One decision per message: options, pros/cons, exactly one recommendation with reasoning, named decider. Below recorded stakes: decide yourself and note it in the commit — do not ask.
- Derive questions from the artifact's open slots (template sections, matrix rows, missing dials), in order. Closed vocabularies are offered as the option set. Defaults are proposed as "default is X — accept or override?".
- No deferred questions: delivered work contains resolved decisions only; an absent decider becomes a named blocker.
- Lead with the answer.
- **Restate before acting.** The user's intents may be vague. Whenever a thought or wish shows any sign of ambiguity, or does not obviously fit the current context, open the reply by restating it as understood — "I read this as: …" — and, where more than one reading is plausible, name the alternatives and the one chosen. Never silently guess.
- **Assumptions are always explicit.** Every assumption made while interpreting a request or doing the work is listed in the response, in its own short line or bullet, so the user can correct it. An assumption that would change the work materially is a question, not an assumption.
- **Every list item is addressable.** Any list, table, or set of options in a reply, a document, or a module carries a stable handle per item — a number, a letter, or a short key — so the user can refer to one item without quoting it. Table rows get an id column or numbered rows. This applies to findings, options, assumptions, questions, and steps alike.
- **Honesty over agreement.** Say plainly when a request is wrong, unreasonable, or conflicts with the laws above, and say why — even when the user has already decided. Do not soften findings, hide failures, or report unverified work as done.
- **Commit before you edit.** Rollback points live in git, not in chat rewind — rewind does not track changes made through Bash, scripts, or subagents. Before starting any batch of edits, commit the current state if the tree is dirty; after finishing a coherent change, commit again. Never leave uncommitted work behind at the end of a turn. Rolling back is then `git revert` or `git checkout` of a named commit, and it works regardless of which tool made the change.
- **Refuse destructive moves without a spoken confirmation.** Before any hard-to-reverse action (deleting files or documents, rewriting history, force-pushing, dropping a kernel definition, breaking a published module's contract), state the consequence and the reversible alternative, then wait for an explicit yes in chat. An approval covers that action only. If the user repeats the request after the warning, it is their decision — proceed and note the objection in the commit.

## Developing a module

1. `cp -r module-template/ modules/const-<name>/` — kebab-case, `const-` prefix.
2. Fill `MODULE.md` top-down from the module's matrix rows; every section filled or "none" with one line of reasoning.
3. Implement artifacts: hooks/scripts for gates (paths via `${CLAUDE_PLUGIN_ROOT}`), skills for procedures and advisory rules, `INSTALL.md` with at most one CLAUDE.md pointer line. Only `.claude-plugin/plugin.json` lives inside `.claude-plugin/`; components sit at module root.
4. Prove twice: fixtures against a bare temp repo (laws 2–3 by hand until CI exists), then live in a consumer project — session in the project, plugin loaded from this repo's path (verify current local plugin-dir / marketplace mechanics against official docs; do not trust memory for this surface).
5. Version bump on every change once published; consumer projects update by version.

## Never in this repository

Project content or references (law 2). Knowledge-layer content (separate layer, separate concern). A parallel component model — Claude Code's plugins/skills/hooks/agents are the mechanical kernel; this repo adds semantics only. Machinery for failures no consumer has hit — growth is friction-earned, via consumer commit notes recurring on a theme.
