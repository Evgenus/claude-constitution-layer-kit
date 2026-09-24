---
id: module-const-meta-types
type: current-state
title: const-meta-types — write-time guard of claimed territory
status: active
---

# MODULE.md — `const-meta-types`

*Draft at manifest version `0.0.1`, no open slots; published at `0.1.0` in rollout Phase D. This document is the module's description ([template](../../module-template/MODULE.md)). Every list and table row carries a handle.*

<a id="t1"></a>
## 1. Purpose

A session opens a research note, a stale structure description, or a half-migrated remnant and treats it as binding truth because nothing on the document says otherwise — the retroactive-canonization problem. In the same repository, a document sits in a folder two policies claim, or in one that none claims, and the rules that apply to it are whatever the reader assumes. Both compound silently: every unguarded document raises the cost of the eventual repair. This module makes a Markdown document in claimed territory *governable* at the moment it is written: its authority is declared in its envelope and exactly one policy governs it, or the write is blocked with a message that teaches the fix.

<a id="t2"></a>
## 2. Failure class

`accumulating`: each document written without a valid envelope, or into ambiguous territory, is one more file whose authority a later session must reconstruct by archaeology, and the reconstruction cost grows with every such file. **Entry trigger:** day-one install set of every project that claims territory; the first document written into a territory is the moment the guard must already be there.

<a id="t3"></a>
## 3. Rows

| row | this module's reading |
|---|---|
| [A1.4](../../docs/requirements.md#a1-4) | "Valid type" is read as the whole envelope of [kernel §1](../../kernel/CONVENTIONS.md#k1): `id` (kebab-case), `type` (one of three), `title` (a non-empty string of at most 200 characters), `status` (one of two), checked against a mirror of the kernel's frontmatter schema; in the root policy's territory a valid `type` is `current-state` only, since a policy is a current-state document. A scalar YAML read as a non-string (`status: yes`) is reported as needing quotes. "In territory" is decided by [A2.3](../../docs/requirements.md#a2-3)'s resolution: a document is examined only when it resolves to a policy. An id already carried by another governed document is an invalid envelope, because a shared id is not a stable identifier — the kernel's "never reused", checked for the present tree, not for history (decision [dec-0019-meta-types-module-rulings](../../docs/decisions/dec-0019-meta-types-module-rulings.md) item 1, which amended the row text). The row's "tree" is the governed tree: outside claimed territory the constitution is silent ([kernel §3](../../kernel/CONVENTIONS.md#k3)), so a Markdown file no policy claims, and that carries no declaration, may carry the same id unseen ([§9](#t9), limit 4). |
| [A1.5](../../docs/requirements.md#a1-5) | Advisory only: the skill carries the founding contrastive pairs and the split rule; the gate cannot tell a wrong choice from a right one and does not pretend to. |
| [A2.3](../../docs/requirements.md#a2-3) | Path first, declaration second, per [kernel §3](../../kernel/CONVENTIONS.md#k3). The declaration field is `policy: <id>` in the envelope — a module-defined extension field, since the kernel names the mechanism and not the key (decision [dec-0019-meta-types-module-rulings](../../docs/decisions/dec-0019-meta-types-module-rulings.md) item 2). Blocked defects: no policy (a declaration naming an id that is not a policy), multi-policy (two or more territories match and no declaration picks one of them), contradicting declaration (the path maps to a policy the declaration does not name). A declaration that names one of the matching policies resolves an ambiguous mapping and is permitted; a declaration naming the single policy the path already maps to is redundant and accepted silently, since it contradicts nothing; whether an active task-record covers the move is not deterministic and is not checked. A document outside every territory that carries a declaration is examined by that declaration — this is the path-absent case, and a declaration naming a non-policy is the no-policy defect; one that declares nothing is left alone: outside claimed territory the module is silent. A `territory` under a namespace with no policy document behind it claims nothing, as the kernel says: a write there is a visible skip naming the namespace, and the scan prints a note per such namespace and stays green (decision [dec-0019-meta-types-module-rulings](../../docs/decisions/dec-0019-meta-types-module-rulings.md) item 3). |

<a id="t4"></a>
## 4. Decisions

1. [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) — section 1 fixes the runtime (Python 3 with PyYAML, POSIX shell for the entry point, a missing runtime exits 1 with the install command); section 2 homes [A2.3](../../docs/requirements.md#a2-3) here, one script for envelope and resolution with a repository-scan mode as backstop; section 7 adds the `severity` dial.
2. [dec-0014-territory-dialect](../../docs/decisions/dec-0014-territory-dialect.md) — territory patterns are gitignore syntax by default, `territory_dialect` names another; this module supports `gitignore` only and reports any other as a configuration failure.
3. [dec-0018-dials-schema](../../docs/decisions/dec-0018-dials-schema.md) — every read of `constitution.yaml` validates the keys read; a malformed file is a configuration failure.
4. [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md) — the mechanism choices of [§6](#t6) rest on this module's own dated comparison.
5. [dec-0019-meta-types-module-rulings](../../docs/decisions/dec-0019-meta-types-module-rulings.md) — the three rulings of this module's authoring: id uniqueness in the present tree is part of a valid envelope; the declaration field is `policy`; a territory with no policy behind it claims nothing.
6. [dec-0020-gate-script-rules](../../docs/decisions/dec-0020-gate-script-rules.md) — the gate-script rules this module's scripts follow: package shape, typed message functions, exit codes, floor 3.12, declared dependencies, no fail-open, strict typing, the output log and its `log_dir` dial, case-record fixtures, absence fixtures; and [dec-0026-imports-at-the-top](../../docs/decisions/dec-0026-imports-at-the-top.md) — imports at the top, the one exception being the modes loaded after the preflight.
7. [dec-0022-output-log-through-logging](../../docs/decisions/dec-0022-output-log-through-logging.md) — the output log is built on the standard library's `logging`, with its three cautions.
8. [dec-0025-shared-gate-code-linked](../../docs/decisions/dec-0025-shared-gate-code-linked.md) — what every gate shares has one source under `shared/`; this module links to it and keeps its own model, messages, checks and modes.

<a id="t5"></a>
## 5. Invariant

**Every Markdown document in claimed territory carries a valid envelope and resolves, path first, to exactly one governing policy at the moment it is written through the platform's file tools.** Claimed territory, envelope, policy, and resolution are the kernel's ([§1](../../kernel/CONVENTIONS.md#k1), [§3](../../kernel/CONVENTIONS.md#k3), [§6](../../kernel/CONVENTIONS.md#k6)); "valid" is the kernel's frontmatter schema plus id uniqueness in the present tree; "written through the platform's file tools" is the honest boundary of [§9](#t9).

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

| component | path | carries |
|---|---|---|
| hook | `hooks/hooks.json` | `PreToolUse`, matcher `Write\|Edit` (an exact-string list on the platform), exec form: `command` `sh`, `args` `["${CLAUDE_PLUGIN_ROOT}/scripts/check-governed-document.sh"]`, timeout 30 s. The gate. |
| script (sh) | `scripts/check-governed-document.sh` | POSIX entry point: finds `python3`, exits 1 with the fix when it is missing, otherwise hands stdin and arguments to the Python entry point. Reads no YAML. |
| script (py) | `scripts/check-governed-document.py` | Thin Python entry point, parseable by any Python 3: checks the interpreter floor (3.12) and that the shared package is there, then runs the module's `start`. Its docstring is the contract: events, modes, input read, exit codes, output channels, dials read. |
| package | `scripts/meta_types_gate/` | The module's own code, beside its entry point, imported with no path manipulation: `model` (the keys of its findings), `messages` (its own texts, as typed functions keyed as in the table below), `dials` (the module has no dial of its own beyond the two every gate has; the parse refuses any other key of its namespace), `checks` (the resolution's defects turned into findings, the envelope's fields, id uniqueness, the root policy), `modes` (hook, `--scan [DIR]`), `start` (which gate this is). Step down from a platform component: no platform component evaluates a document against a schema or resolves a path to a policy. Step down from a pure-shell script: legal YAML outside a hand-rolled subset would yield a wrong answer, not an error. `mypy --strict` clean. |
| shared code | `scripts/const_gate` → the kit's `shared/const_gate/` | A relative symbolic link to what every gate shares — the hook event, the dials file, territories through `git check-ignore`, the index of policies, resolution, the output log on the standard library's `logging`, the pipeline, `argparse` and the single guard, the shared messages — described in [kit-shared-gate-code](../../shared/GATE.md). The platform copies what the link points at into an installed plugin; the entry file turns a missing package into the designed failure C15. |
| dependencies | `requirements.txt` | The declared libraries (PyYAML); the preflight imports each on every invocation, and the configuration-failure message prints the one install command for this file. |
| skill | `skills/choose-meta-type/SKILL.md` | The type-selection procedure ([A1.5](../../docs/requirements.md#a1-5)): the contrastive pairs of [§8](#t8), the split rule, envelope reminders, and the advice to run the scan after a shell edit. `paths: "**/*.md"`. Advisory. |
| install note | `INSTALL.md` | Requirements, the two dials, the scan command for CI, where the output log goes, no CLAUDE.md pointer. |
| tests | `tests/run.py`; `harness.py`, `consumer.py`, `shared_items.py` linked from the kit's `shared/tests/` | The fixtures of [§10](#t10): this module's numbered case records and assertions, and the shared acceptance items, all driving the real entry point with real hook events. |
| command | none | no act here is one a human deliberately initiates; the scan is a shell command, documented in the install note. |
| agent | none | no delegation boundary. |

- **Always-on content:** the skill's `description`, 449 characters, in the skill listing. No `SessionStart` hook: the pairs are needed at creation time, not in every session.
- **Platform facts relied on** (all verified 2026-09-18 against the official documentation; sources in the research comparison):
  1. A `PreToolUse` command hook exiting 2 blocks the tool call and Claude sees stderr as the reason. Breaks: the gate stops blocking.
  2. `Write` input is `file_path` + `content`; `Edit` input is `file_path`, `old_string`, `new_string`, `replace_all`; `file_path` is absolute for the file tools. `Edit` can create a new file, so an `Edit` of a missing file with an empty `old_string` is judged on its `new_string` (re-verified 2026-09-19). Breaks: locating or reconstructing the document.
  3. A matcher made of letters, `|` and friends is an exact-string list: `Write|Edit` matches those two tools and nothing else. `MultiEdit` is legacy and unlisted; `NotebookEdit` writes notebooks, never Markdown. Breaks: a Markdown write through an unmatched tool.
  4. On exit 0, JSON on stdout is parsed: `hookSpecificOutput.additionalContext` reaches Claude, top-level `systemMessage` reaches the user; stderr on exit 0 goes to the debug log only. On any exit other than 0 and 2, with no schema-valid JSON on stdout, the hook is non-blocking and the transcript shows only the first stderr line; with such JSON on stdout the JSON alone decides and the exit code is ignored, so a configuration failure keeps stdout free of JSON (made precise 2026-09-18 by the second module's research round). Breaks: the `warn` channel; the visibility of a configuration failure.
  5. Hook input carries `cwd`, `tool_name`, `tool_input`; hooks run in the current directory, which follows worktrees and `cd`. The repository root is therefore derived from the written file's path (`git rev-parse --show-toplevel`), never from `cwd`. Breaks: root discovery.
  6. `${CLAUDE_PLUGIN_ROOT}` is the plugin's root in hook commands; `hooks/hooks.json` uses a top-level `hooks` key; when a manifest is present `name` is its only required field; only `plugin.json` lives in `.claude-plugin/`; skills are `/<plugin>:<skill>`. Breaks: plugin load.
  7. Default command-hook timeout is 600 s; per-hook `timeout` is in seconds. A timed-out command hook does not block the tool call, and neither does a hook that cannot start; hook output strings are capped at 10,000 characters; all matching hooks run in parallel, a second plugin's hook on the same matcher is a separate process, and any one exit 2 blocks (added 2026-09-18 from the second module's research round). Breaks: nothing at 30 s unless a repository holds tens of thousands of Markdown files.
  8. `git check-ignore --no-index -v -n -z --stdin` against a fresh null repository with an empty work tree and `core.excludesfile` set to one policy's patterns evaluates paths that do not exist yet, reports one deciding pattern per path (a `!` pattern means not in territory), and is unaffected by the consumer's own `.gitignore`; `core.ignorecase` must be pinned false. Breaks: territory verdicts.
  9. A skill's `paths` limits automatic activation; `description` plus `when_to_use` are capped at 1,536 characters in the listing. Breaks: the always-on budget.
  10. `hooks.json` has an exec form — `command` plus `args`, no shell, each element one argument — which the documentation says to use whenever a path placeholder appears. Breaks: hook wiring.
  11. `${CLAUDE_PLUGIN_DATA}` is a persistent per-plugin directory outside the repository, exported to hook processes as an environment variable, removed on uninstall unless kept. Breaks: the default log location (the gate then logs nowhere, silently — stdout remains).
  12. `${CLAUDE_PLUGIN_ROOT}` is substituted in a plugin skill's Markdown, so the skill can name the scan command exactly. Breaks: the skill's backstop advice.
  13. A symbolic link inside a plugin that leads elsewhere within the same marketplace is dereferenced when a marketplace install copies the plugin into the plugin cache — the target's content is copied into the cache in its place — and one leading outside the marketplace is skipped; a plugin loaded in place — `--plugin-dir`, or a relative-path entry of a marketplace added from a local directory — is not copied, its hook processes receive a plugin root pointing at the source directory, and the documentation's skip of such a link under `--plugin-dir` is read by the kit as its component-path rule (limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4)); on Claude Code 2.1.251 a plugin loaded with `--plugin-dir` resolves the link (verified and observed 2026-09-19; re-read 2026-09-23 against the documentation). Breaks: the shared code is missing from the install — C15, loud, exit 1.
- **Research:** [res-0001-const-meta-types](../../docs/research/res-0001-const-meta-types.md) (2026-09-18). Per row: [A1.4](../../docs/requirements.md#a1-4) gate at `PreToolUse` — **confirmed**; [A1.5](../../docs/requirements.md#a1-5) advisory skill — **confirmed**; [A2.3](../../docs/requirements.md#a2-3) same script at write time plus scan backstop — **confirmed** (no `SessionStart` scan: cost on every compaction without a gate). Schema validation is a PyYAML-only mirror of the kernel schemas rather than the `jsonschema` library (four more dependencies, one compiled); the module ships without the kit's schema files, so the mirror is the only copy a consumer has. The kit proves the mirror with `scripts/check-schema-mirror.py`, which runs the real schemas through `jsonschema` (a development dependency of the kit only) over one corpus: the same verdict on every envelope case, never more lenient on the keys of the dials file a gate reads, where the mirror is deliberately stricter (repository-relative paths, patterns git can read); what another module's namespace holds is that module's to validate ([kernel §6](../../kernel/CONVENTIONS.md#k6)), and the check names those cases.

**Error messages.** Each row is one function of this module's `messages.py`, under the same key; `{…}` are its parameters. The texts every gate shares — the other reasons of `G1`, `W1`, the two notes about policies, the field-level parts `… missing` and `… must be a quoted string`, and every configuration failure `C1`–`C15` — are written out once, in [kit-shared-gate-code §3](../../shared/GATE.md#g3), with `{module}` standing for `const-meta-types`. Findings are `RED`, three lines each (what failed / why the rule exists / the exact fix), followed by a count line; configuration failures are `BROKEN`, one self-sufficient line (only the first stderr line reaches the user in hook mode), followed by a count line.

| key | first line | why | fix |
|---|---|---|---|
| F1 | `RED: {path}: no frontmatter envelope` | a governed document declares its authority in its envelope, or sessions guess it | start the file with a YAML block between two '---' lines carrying at least id: <kebab-id>, type: current-state \| task-record \| non-authoritative, title: <one line>, status: active \| inactive — the fields every governed document carries; its kind may add fields of its own |
| F2 | `RED: {path}: frontmatter opened with '---' but never closed` | an unclosed envelope is unreadable by machines and by the next session | close the YAML block with a line holding only '---' |
| F3 | `RED: {path}: frontmatter is not valid YAML ({error})` | the envelope is read by machines, so it must parse | repair the YAML between the '---' lines; keep at least the four fields id, type, title, status |
| F4 | `RED: {path}: envelope field(s) invalid: {list}` — items such as `type missing`, `type 'spec' not one of current-state \| task-record \| non-authoritative`, `id 'Note_A' is not kebab-case`, `title empty`, `title longer than 200 characters`, `status 'open' not one of active \| inactive`, `policy 'X' is not a kebab-case policy id`, `status must be a quoted string (YAML read it as bool)` | the envelope is the one place a document's authority is declared, and it is read by machines | `set each named field: {fragments}` — `set the named field: {fragment}` for one — the fragments being those of the fields the list names, in reading order, out of: `id = stable kebab-case (never changed, never reused)`; `type = current-state (reconciled truth) \| task-record (change delta) \| non-authoritative (explanation)`; `title = one line`; `status = active \| inactive`; `policy = the kebab-case id of the governing policy, or no such line` |
| F5 | `RED: {path}: id '{id}' is already carried by {other path}` | an id is a stable identifier: two documents sharing one break every reference to it | give this document its own id, never a retired one; if this is a move, delete or git mv the old file first, then write |
| F6 | `RED: {path}: declares policy '{id}' but no policy with that id lies in the root policy's territory {patterns}` | a governed document resolves to exactly one governing policy, or its rules are undefined | declare the id of a policy that exists there, or drop the declaration and place the file in a claimed territory |
| F7 | `RED: {path}: matched by {n} policy territories: {id} ({pattern}), {id} ({pattern})` | a document resolves to exactly one governing policy, or two rule sets compete | narrow one territory in constitution.yaml so the patterns no longer overlap; during a move, declare the intended one with 'policy: <id>' in the envelope while an active task-record covers it |
| F8 | `RED: {path}: declares policy '{id}' but its path is claimed by '{id}' ({pattern})` | the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it | remove 'policy: {id}' from the envelope, or move the file into the territory of '{id}': {patterns} — or, when the declared id is no policy: remove 'policy: {id}' from the envelope — no policy with that id exists |
| F8b | `RED: {path}: declares policy '{id}' but its path is claimed by {id} ({pattern}), {id} ({pattern})` (overlap, declaration naming none of them) | the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it | declare one of the policies that claim the path, or remove the declaration and narrow the territories in constitution.yaml |
| F10 | `RED: {path}: lies in the root policy's territory but has type '{type}'` | a policy is a current-state document, and only policies lie where policies live | set type: current-state, or move the file out of {root territory} |
| F11 | `RED: {path}: the root policy has no readable envelope ({detail})` — detail one of `the file does not start with a '---' line`, `opened with '---' but never closed`, the YAML parser's message (a `Write` or `Edit` of the root policy itself) | the root policy's id names the namespace where policies live; without it nothing is governed | keep the YAML block between two '---' lines with id, type: current-state, title, status: active |
| F12 | `RED: {path}: the root policy has type '{type}'` | a policy is a current-state document, and the root is the policy for policies | set type: current-state |
| F13 | `RED: {path}: the root policy's id '{id}' has no territory under that id in constitution.yaml` | the root's namespace is where policies live; changing the id orphans every policy | keep the id that has the namespace, or rename the namespace in constitution.yaml in the same change |
| F14 | `RED: {path}: as written, {the headline of C6, C7, C8 or C9}` (a write to the root policy that would itself cause that configuration failure) | every chain of governance ends at the root policy; a write that breaks it ungoverns the repository | {the fix of that configuration failure} |
| G1 | this module's reasons of the shared skip line `GREEN: const-meta-types: 0 documents examined — {reason}`: `{path} is outside claimed territory`; `{path} lies only in the territory of namespace '{ns}', which has no policy document behind it and so claims nothing`, or for several: `{path} lies only in the territories of namespaces '{ns}', '{ns}', none of which has a policy document behind it, so nothing is claimed`. Its count tail, in the scan's green and red lines: `{g} governed document(s) examined, {m} Markdown file(s) scanned, {p} policies` | — | — |
| N1 | this module's note, scan only, printed before the verdict: `note: namespace '{ns}' declares a territory but no policy with id '{ns}' lies in the root policy's territory; it claims nothing until that policy exists` | — | — |
| C5 | this module's dial failure, `BROKEN: constitution.yaml: {detail} — fix: {fix}`: `const-meta-types.{key} is no dial of this module` — `a misspelt dial would be ignored in silence, so none is: write one of severity, log_dir` | — | — |

**Installed components reference nothing in the kit.** The skill, hook, scripts, error text, fixtures, and install note name no kit document; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

| dial | default | meaning |
|---|---|---|
| `severity` | `block` | `block`: a finding exits 2 and the write is blocked. `warn`: the finding is reported to Claude and to the user and the write proceeds — the adoption path onto a repository with legacy documents. The scan ignores it. |
| `log_dir` | absent | A repository-relative directory for the output log. The gate verifies with git that the directory is ignored and reports a configuration failure otherwise. Absent: the log goes to the platform's per-plugin data directory; where that is absent too (CI), nowhere, and stdout is the record. |

The shared code validates the two at each read, and a key of this namespace that is neither is a configuration failure: a misspelt `severty: warn` would otherwise leave the default in force unseen. Territory, the root policy, and the dialect are the kernel-owned keys and the policy namespaces of [kernel §6](../../kernel/CONVENTIONS.md#k6), not dials of this module. The one read of another `const-*` namespace — its `territory`, read leniently, for a policy whose id looks like a module's name — is the shared dials reader's, stated in the `dials` row of [kit-shared-gate-code §1](../../shared/GATE.md#g1).

<a id="t8"></a>
## 8. Boundary examples

The one judgment boundary is the meta-type choice ([A1.5](../../docs/requirements.md#a1-5)). The pairs are the definition and are carried verbatim by the skill:

1. **Architecture of what should be, written mid-task** → `task-record` (rides with the delta, closes with it) / *not* `current-state` (unrealized intent never sits in a standing document).
2. **The standing specification** — what a subsystem is and must stay, invariants and why → `current-state` / *not* `task-record` (it has no close).
3. **How the code is organised today** — a module map, a dependency listing → `non-authoritative`, dated, generated-preferred / *not* `current-state` (no obligation; a stale copy read as truth is the failure).
4. **A document mixing as-is with direction** → split: normative half `current-state` (or `task-record` if a bounded change), descriptive half `non-authoritative`; or classify by the normative content and cut the rest to a dated pointer / *not* left mixed.
5. **Notes from an investigation** → `non-authoritative` / *not* `task-record` (a record carries a ruling or a delta, not an account).

The resolution and envelope boundaries are deterministic and need no examples; the fixtures of [§10](#t10) are their contrastive pairs.

<a id="t9"></a>
## 9. Enforcement honesty

| artifact | kind |
|---|---|
| hook + `check-governed-document.sh` + `check-governed-document.py` (hook mode) | `gate`, severity dial `severity` (`block` default; `warn` reports and lets the write through) |
| `check-governed-document.py --scan` | `gate`, always blocking (exit 2), ignores `severity` |
| skill `choose-meta-type` | `advisory` |

**Honest limits**, each with its backstop. The limits of the shared code — shell writes and other actors, non-blocking configuration failures and timeouts, a dropped link to the shared code, the reconstructed `Edit`, symbolic links, a key given twice, `.md` only and git-ignored files, where the envelope ends, case-sensitive patterns, the best-effort log, no `--help`, one block message at a time, a negated pattern under an excluded directory — are [kit-shared-gate-code §4](../../shared/GATE.md#g4), items 1–13, and apply here; the skill tells the agent to run the scan after a shell edit. This module's own:

1. **The declaration's condition is not checked.** Whether "an active task-record covers the move" holds is judgment; the gate accepts any declaration that names a matching or existing policy. Backstop: review.
2. **Duplicate ids across history** ("never reused") are not checked; only the present tree is. Backstop: review; the friction signal of [§12](#t12), item 4.
3. **Negation cannot carve a subtree out of a `**` territory.** Under gitignore's rule that a file below an excluded directory cannot be re-included, `["docs/notes/**", "!docs/notes/private/**"]` still claims `docs/notes/private/p.md`; a file-level negation such as `"!docs/notes/secret.md"` against `"docs/notes/*.md"` does exclude. This is the dialect's semantics, not the module's. Backstop: write the territory without the parent match instead.
4. **An ungoverned twin id is not seen.** A file outside every territory that carries no declaration is never consulted, at write time or in the scan, so a governed document's id may stand in it unseen; a file outside every territory that carries a declaration is bound by it and is consulted like any governed document. Backstop: the generator of module `const-locations`, when installed, refuses such a twin before writing; review otherwise.

**Exit-code contract** (both modes): `0` green or nothing examined (the count line says which); `2` finding — the repository is wrong; `1` configuration failure — the checker could not run (missing or too-old interpreter, missing library, malformed or contradictory dials file, missing root policy, the shared code missing from the install, git absent, a log directory git does not ignore, unparseable hook input, a bad argument, or an unexpected exception, whose traceback is printed). Nothing exits 0 on error. A territory with no policy behind it is none of these: it claims nothing, and the skip says so. A missing tool is loud, never a silent pass.

<a id="t10"></a>
## 10. Acceptance

Runner: `python3 tests/run.py` (needs git, Python 3.12, the declared libraries). It builds a three-policy consumer with a deliberate overlap in a temporary git repository, fresh for every half of every case, and drives the real entry point — POSIX wrapper, stdin, exit code — with real `PreToolUse` events. A red→green case fails when its red half does not exit 2, when red does not teach the expected message — all three lines, compared with what the `messages` function returns — or prints any `RED` line but that finding's headline and the count line, or when its green half does not print the whole green line, whose words the case types by hand. A configuration-failure assertion requires exit 1 and the `BROKEN` line as the first stderr line. Items T1–T33 and S101–S151 carry the numbers the runner prints; envelope documents are rendered through the YAML dumper, malformed ones typed on purpose. The runner, and only the runner, puts the package on the import path; no gate code edits the path.

| item | kind | what it proves |
|---|---|---|
| T1–T5 | fixture, red→green | the envelope: none (F1), unclosed (F2), not YAML (F3, with the parser's whole message), invalid `id`, `type`, `status` in one message (F4), an id carried by another governed document (F5) |
| T6–T10 | fixture, red→green | resolution: no policy (F6; a declaration naming a policy, path mapping absent, passes), multi-policy (F7; declaring one claimant passes), contradiction (F8), contradiction naming no policy at all (F8, its other fix), contradiction in an overlap (F8b) |
| T11 | fixture, red→green | a document in the root's territory with `type: task-record` (F10) |
| T12–T15 | fixture, red→green | the root policy itself: written without its envelope (F11), with another type (F12), renamed to an id with no namespace (F13), renamed to a namespace that does not contain it (F14) — each a blocked write, never a non-blocking configuration failure |
| T16–T17 | fixture, red→green | an `Edit` removing `type` is blocked on the reconstructed result, an `Edit` in the body passes; an `Edit` that creates a file is judged on what it creates |
| T18–T20 | fixture, assertion | territory: outside territory prints `0 documents examined`; a territory with no policy behind it is a visible skip; a policy whose id looks like a module's name still governs. A file-level negation excluding the file, the skip line whole, is the shared item S148 |
| T22 | fixture, assertion | `severity: warn` with a note present: stdout is still one JSON object |
| T23–T26 | fixture, assertion | scan: exactly the finding and the count line, typed by hand, and exit 2 under `warn`; green with counts and a note per void namespace; 300 documents in seconds (each read once), the green line typed whole; a tracked file deleted from the working tree is left out, not a failure |
| T29 | fixture, assertion | the F1 fix line as a literal typed by hand, since a case compares with what the message function returns; seen to fail with the text broken |
| T30 | fixture, assertion | an ungoverned twin id is green: a file outside every territory, declaring no policy, carries a governed document's id, and the governed write passes ([§9](#t9), limit 4) |
| T31 | fixture, assertion | this module's dial failure: a key of the namespace that is no dial exits 1, never 2, never 0 |
| T32 | fixture, assertion | the fix of F4 names only the field that failed: a bad `status` alone earns the `status` fragment and no other, as a literal; a bad `policy` earns its own |
| T33 | fixture, assertion | golden lines: the headline, why and fix of every finding, F1 to F14, as literals typed by hand, checked against a fresh run of each case's red half — F1's fix is T29's, F4's why and one-field fix T32's, F3's headline up to the parser's own words, both fixes of F8 — so a why emptied or a word lost inside a message function is red; seen to fail with one word of the F2 why changed. A value a page long echoed cut, the cut said, is the shared item S151 |
| S101–S151 | fixture, assertion | the shared acceptance items of [kit-shared-gate-code §5](../../shared/GATE.md#g5), run through this module's entry point: the exit-code split, absence of each tool and of the shared code, invocation and input, paths and skips — S148 the file-level negation, its skip line typed here — `warn`, the output log, declared dependencies |
| T50 | kit check | `scripts/check-schema-mirror.py` in the kit: the mirror gives the kernel envelope schema's verdict on every case and is never more lenient than the dials schema; a case exempted as another reader's is red once the exemption stops holding |
| T51 | live | the scan over this repository (consumer zero): every governed kit document green, counts printed |
| T52 | live | the plugin loaded in a headless session in this repository via `--plugin-dir`: a frontmatter-less write into claimed territory blocked with F1 and the file not created; the corrected write landed; the log written to the plugin data directory; the skill reachable as `/const-meta-types:choose-meta-type`; repeated after the shared code was linked, with both modules loaded |
| T53 | review | the pairs of [§8](#t8) and the error texts of [§6](#t6), at the one yes |
| T54 | live, deferred to the consumer's bootstrap | the consumer-live proof (decision [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) section 3), which also proves that the install carries the shared code |

**Examined count.** Every exit prints it: hook mode `1 document examined, governed by …` or `0 documents examined — <reason>`; scan mode governed documents, Markdown files scanned, and policies; `BROKEN` prints `0 documents examined`.

<a id="t11"></a>
## 11. Siblings

**Depends on:** [kernel §1](../../kernel/CONVENTIONS.md#k1) (envelope), [§2](../../kernel/CONVENTIONS.md#k2) (the type enum), [§3](../../kernel/CONVENTIONS.md#k3) (territory, policy, resolution, the three defects), [§6](../../kernel/CONVENTIONS.md#k6) (dials file, kernel-owned keys, dialect, portability), [§7](../../kernel/CONVENTIONS.md#k7) (naming). Nothing else.

**Kernel alone:** on a bare repository with no `constitution.yaml`, every write passes with a visible zero count; with a dials file naming a root policy, every Markdown write into claimed territory is checked and the scan runs. Policies are the consumer's documents; the module ships none.

**Optional enhancements:** when module `const-locations` is installed, documents are born in their canonical home from the policy's template, so this gate sees fewer findings — it stays the guard either way. When module `const-catalogs` is installed, the name and id form of a numbered kind (`<prefix>-<nnnn>-<slug>`) is checked there, from that module's own dial; this module reads nothing of it. When module `const-decision-records` is installed, the body shape of a decision record is its concern; this module checks the envelope only.

<a id="t12"></a>
## 12. Deferred

1. **A `Bash` matcher inspecting commands for Markdown writes.** Signal: consumer commit notes recurring on shell edits that escaped the hook and were caught late by the scan. The platform calls Bash matching best-effort and points to permissions for a hard deny, so the scan is the honest backstop until then.
2. **`pathspec` as a fallback matcher.** Signal: a consumer reports a territory verdict where git and the kernel's dialect description disagree.
3. **Other Markdown extensions** (`.markdown`, `.mdx`). Signal: a consumer's governed documents use one.
4. **Id reuse across history.** Signal: a retired id resurfacing in a consumer and breaking references; the check needs git history and a definition of "retired".
5. **Checking the declaration's condition** (an active task-record covering the move). Signal: declarations left in place after moves complete; the check needs the record catalog of module `const-decision-records`, which would be a kernel candidate.
6. **Windows without a POSIX shell, or a checkout without symlink support.** Signal: a consumer on Windows; the entry point would become a `.cmd` beside the `.sh`, and the links to the shared code need `core.symlinks` or the fallback to copies.
7. **Performance on very large repositories.** Signal: the 30 s hook timeout hit; the fix is a cached index, not a bigger timeout.
