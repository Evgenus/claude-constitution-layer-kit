# Constitution Kit — Session Guide

This repository is the **constitution kit**: a portable, project-agnostic governance layer for Claude Code projects, shipped as plugins. It contains the semantic kernel, the module template, and the modules. It contains **no project content, ever**.

Read before any work:
- `INTENT.md` — what this repo is for and what it is not.
- `kernel/CONVENTIONS.md` — the semantic kernel (one page). Authoritative for all vocabulary: envelope, meta-types, governance binding, stakes, decision records, dials, naming.
- `module-template/MODULE.md` — the fixed shape every module fills.
- `docs/rollout-plan.md` — module specs and the traceability matrix (requirement rows per module).

## Laws of this repository

1. <a id="law-1"></a>**Kernel is authoritative; never restate it.** Modules and documents reference kernel definitions by name — duplication is a defect.
2. <a id="law-2"></a>**Portability ([kernel §6](kernel/CONVENTIONS.md#k6)):** no file in a module references any project — no paths, names, repos, values. Project specifics enter only through the module's dials namespace. Test: the module installs and operates on an empty repository using defaults alone.
3. <a id="law-3"></a>**Sibling independence:** modules depend on the kernel and nothing else. Sibling references only as optional enhancements ("when `const-x` is installed…"). Test: kernel + this module alone on a bare repo is a functioning installation. If a module seems to need a sibling, the shared concept belongs in the kernel — raise that as a `process`-stakes decision instead of coupling.
4. <a id="law-4"></a>**A module implements exactly its matrix rows.** Its `MODULE.md` cites them. Content beyond its rows is scope creep; a missing row is incompleteness. Both are review findings.
5. <a id="law-5"></a>**Enforcement honesty:** every artifact is `gate` (deterministic, red = fix) or `advisory` (judgment-shaping) — declared, never blurred. Nothing judgment-based is dressed as a check.
6. <a id="law-6"></a>**Teaching errors:** every gate's error message states what failed, why the rule exists (one clause), and the exact fix. Error messages are designed content, reviewed like code.
7. <a id="law-7"></a>**Every gate ships its red→green fixture** in `modules/<name>/tests/` — one input that fails without the check and passes with it.
8. <a id="law-8"></a>**Sizes in characters, never tokens.**
9. <a id="law-9"></a>**Kit decisions follow the kernel's own stakes triage.** Routine → act, note in the commit. `process` (most kit changes) → decision record in `docs/decisions/`, one human yes in the PR. Kernel changes are always recorded. Record lifecycle, supersession, and deletion: [kernel §1](kernel/CONVENTIONS.md#k1) and [kernel §5](kernel/CONVENTIONS.md#k5) — not restated here.

## Session conduct

- One decision per message: options, pros/cons, exactly one recommendation with reasoning, named decider. Below recorded stakes: decide yourself and note it in the commit — do not ask.
- **Decision format.** Options are lettered A, B, C… (never numbered — numbers are for every other list item, so an option is never confused with a finding or a step). The full argument is written in the chat message, in this shape: each option is a bullet whose first line is the bold letter and title plus a one-sentence description; beneath it, two indented sub-bullets labeled **Pros:** and **Cons:**, each a short prose line — never inline in the description paragraph, never a table; then exactly one recommendation with reasoning, and the named decider. When there are fewer than five options, the `AskUserQuestion` tool is then used only to collect the pick: the question restates the decision in one line, each option is its letter plus a short label, and the tool's descriptions carry at most one clause each — never the pros, cons, or recommendation. Five or more options: chat only, the user answers with a letter. The argument must reach the user: chat text written between tool calls in one turn is not always rendered, so if the user reports an argument missing, every later decision in that session ends the turn on the chat message and the pick is collected by letter, without the tool.
- Derive questions from the artifact's open slots (template sections, matrix rows, missing dials), in order. Closed vocabularies are offered as the option set. Defaults are proposed as "default is X — accept or override?".
- No deferred questions: delivered work contains resolved decisions only; an absent decider becomes a named blocker.
- Lead with the answer.
- **Restate before acting.** The user's intents may be vague. Whenever a thought or wish shows any sign of ambiguity, or does not obviously fit the current context, open the reply by restating it as understood — "I read this as: …" — and, where more than one reading is plausible, name the alternatives and the one chosen. Never silently guess.
- **Assumptions are always explicit.** Every assumption made while interpreting a request or doing the work is listed in the response, in its own short line or bullet, so the user can correct it. An assumption that would change the work materially is a question, not an assumption.
- **Every list item is addressable.** Any list, table, or set of options in a reply, a document, or a module carries a stable handle per item — a number, a letter, or a short key — so the user can refer to one item without quoting it. Table rows get an id column or numbered rows. This applies to findings, options, assumptions, questions, and steps alike.
- **Honesty over agreement.** Say plainly when a request is wrong, unreasonable, or conflicts with the laws above, and say why — even when the user has already decided. Do not soften findings, hide failures, or report unverified work as done.
- **Commit before you edit.** Rollback points live in git, not in chat rewind — rewind does not track changes made through Bash, scripts, or subagents. Before starting any batch of edits, commit the current state if the tree is dirty; after finishing a coherent change, commit again. Never leave uncommitted work behind at the end of a turn. Rolling back is then `git revert` or `git checkout` of a named commit, and it works regardless of which tool made the change.
- **References are clickable; handles are scoped.** In chat, every reference to a file, section, requirement, law, or record is a markdown link. A numbered item resolves within its message, a lettered option within its decision, a table key within the session; across that boundary, name the message or decision. Verbose handles: "law 3 of CLAUDE.md", "dial `ns.key`", "requirement [A5.3](docs/rollout-plan.md#a5-3)" or "[aspect A5](docs/rollout-plan.md#a5)", "module `const-x`". In documents a bare handle is local to its own document; across documents it is a link to the target's anchor ([requirements A5.5–A5.7](docs/rollout-plan.md#a5)); `scripts/check-references.sh` is the gate.
- **Refuse destructive moves without a spoken confirmation.** Before any hard-to-reverse action (deleting files or documents, rewriting history, force-pushing, dropping a kernel definition, breaking a published module's contract), state the consequence and the reversible alternative, then wait for an explicit yes in chat. An approval covers that action only. If the user repeats the request after the warning, it is their decision — proceed and note the objection in the commit.

## Developing a module

1. `cp -r module-template/ modules/const-<name>/` — kebab-case, `const-` prefix. The template's relative links gain one `../` level in the copy; `scripts/check-references.sh` turns red until they are fixed.
2. Fill `MODULE.md` top-down from the module's matrix rows; every section filled or "none" with one line of reasoning.
3. Implement artifacts: hooks/scripts for gates (paths via `${CLAUDE_PLUGIN_ROOT}`), skills for procedures and advisory rules, `INSTALL.md` with at most one CLAUDE.md pointer line. Only `.claude-plugin/plugin.json` lives inside `.claude-plugin/`; components sit at module root.
4. Prove twice: fixtures against a bare temp repo (laws 2–3 by hand until CI exists), then live in a consumer project — session in the project, plugin loaded from this repo's path (verify current local plugin-dir / marketplace mechanics against official docs; do not trust memory for this surface).
5. Version bump on every change once published; consumer projects update by version.

## Never in this repository

Project content or references (law 2). Knowledge-layer content (separate layer, separate concern). A parallel component model — Claude Code's plugins/skills/hooks/agents are the mechanical kernel; this repo adds semantics only. Machinery for failures no consumer has hit — growth is friction-earned, via consumer commit notes recurring on a theme.
