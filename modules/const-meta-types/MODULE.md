---
id: module-const-meta-types
type: current-state
title: const-meta-types — write-time guard of claimed territory
status: active
---

# MODULE.md — `const-meta-types`

*Draft at manifest version `0.0.1`. This document is the module's description ([template](../../module-template/MODULE.md)); open slots are inline `[decide: …]` markers and are resolved before publication. Every list and table row carries a handle.*

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
| [A1.4](../../docs/requirements.md#a1-4) | "Valid type" is read as the whole envelope of [kernel §1](../../kernel/CONVENTIONS.md#k1): `id` (kebab-case), `type` (one of three), `title` (one non-empty line), `status` (one of two), checked against a mirror of the kernel's frontmatter schema. "In territory" is decided by [A2.3](../../docs/requirements.md#a2-3)'s resolution: a document is examined only when it resolves to a policy. An id already carried by another governed document is an invalid envelope, because a shared id is not a stable identifier — the kernel's "never reused", checked for the present tree, not for history. [decide: duplicate-id check at write time — default on (the present tree only) — stakes process — decider Eugene Chernyshov] |
| [A1.5](../../docs/requirements.md#a1-5) | Advisory only: the skill carries the founding contrastive pairs and the split rule; the gate cannot tell a wrong choice from a right one and does not pretend to. |
| [A2.3](../../docs/requirements.md#a2-3) | Path first, declaration second, per [kernel §3](../../kernel/CONVENTIONS.md#k3). The declaration field is `policy: <id>` in the envelope — a module-defined extension field, since the kernel names the mechanism and not the key. [decide: declaration field name — default `policy` — stakes process — decider Eugene Chernyshov] Blocked defects: no policy (a declaration naming an id that is not a policy), multi-policy (two or more territories match and no declaration picks one of them), contradicting declaration (the path maps to a policy the declaration does not name). A declaration that names one of the matching policies resolves an ambiguous mapping and is permitted; whether an active task-record covers the move is not deterministic and is not checked. A document outside every territory that carries a declaration is examined by that declaration — this is the path-absent case, and a declaration naming a non-policy is the no-policy defect; one that declares nothing is left alone: outside claimed territory the module is silent. A territory claimed under a namespace with no policy document behind it is a configuration failure, not silence, because the writer's evident intent was to govern it; module namespaces (`const-*`) are exempt, since the kernel says a `territory` key outside a policy's namespace claims nothing. [decide: territory under a non-module namespace with no policy — default configuration failure — stakes process — decider Eugene Chernyshov] |

<a id="t4"></a>
## 4. Decisions

1. [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) — section 1 fixes the runtime (Python 3 with PyYAML, POSIX shell for the entry point, a missing runtime exits 1 with the install command); section 2 homes [A2.3](../../docs/requirements.md#a2-3) here, one script for envelope and resolution with a repository-scan mode as backstop; section 7 adds the `severity` dial.
2. [dec-0014-territory-dialect](../../docs/decisions/dec-0014-territory-dialect.md) — territory patterns are gitignore syntax by default, `territory_dialect` names another; this module supports `gitignore` only and reports any other as a configuration failure.
3. [dec-0018-dials-schema](../../docs/decisions/dec-0018-dials-schema.md) — every read of `constitution.yaml` validates the keys read; a malformed file is a configuration failure.
4. [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md) — the mechanism choices of [§6](#t6) rest on this module's own dated comparison.

<a id="t5"></a>
## 5. Invariant

**Every Markdown document in claimed territory carries a valid envelope and resolves, path first, to exactly one governing policy at the moment it is written through the platform's file tools.** Claimed territory, envelope, policy, and resolution are the kernel's ([§1](../../kernel/CONVENTIONS.md#k1), [§3](../../kernel/CONVENTIONS.md#k3), [§6](../../kernel/CONVENTIONS.md#k6)); "valid" is the kernel's frontmatter schema plus id uniqueness in the present tree; "written through the platform's file tools" is the honest boundary of [§9](#t9).

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

| component | path | carries |
|---|---|---|
| hook | `hooks/hooks.json` | `PreToolUse`, matcher `Write\|Edit` (an exact-string list on the platform), command `sh "${CLAUDE_PLUGIN_ROOT}/scripts/check-governed-document.sh"`, timeout 30 s. The gate. |
| script | `scripts/check-governed-document.sh` | POSIX entry point: finds `python3` and PyYAML, exits 1 with the install command when either is missing, otherwise hands stdin and arguments to the Python script. Reads no YAML. |
| script | `scripts/check-governed-document.py` | The check, in two modes: hook mode (reconstructs the document as it will be after the `Write` or `Edit`, examines it) and `--scan [<dir>]` (examines every Markdown document in claimed territory of the repository). Step down from a platform component: no platform component evaluates a document against a schema or resolves a path to a policy. Step down from a pure-shell script: legal YAML outside a hand-rolled subset would yield a wrong answer, not an error. Territory matching is delegated to `git check-ignore` rather than reimplemented: the dialect is git's, so git's verdict is the reference. |
| skill | `skills/choose-meta-type/SKILL.md` | The type-selection procedure ([A1.5](../../docs/requirements.md#a1-5)): the contrastive pairs of [§8](#t8), the split rule, envelope reminders, and the advice to run the scan after a shell edit. `paths: "**/*.md"`. Advisory. |
| install note | `INSTALL.md` | Requirements, the dial, the scan command for CI, no CLAUDE.md pointer. |
| tests | `tests/run.sh`, `tests/fixtures/` | The fixtures of [§10](#t10). |
| command | none | no act here is one a human deliberately initiates; the scan is a shell command, documented in the install note. |
| agent | none | no delegation boundary. |

- **Always-on content:** the skill's `description`, 450 characters, in the skill listing. No `SessionStart` hook: the pairs are needed at creation time, not in every session.
- **Platform facts relied on** (all verified 2026-09-18 against the official documentation; sources in the research comparison):
  1. A `PreToolUse` command hook exiting 2 blocks the tool call and Claude sees stderr as the reason. Breaks: the gate stops blocking.
  2. `Write` input is `file_path` + `content`; `Edit` input is `file_path`, `old_string`, `new_string`, `replace_all`; `file_path` is absolute for the file tools. Breaks: locating or reconstructing the document.
  3. A matcher made of letters, `|` and friends is an exact-string list: `Write|Edit` matches those two tools and nothing else. `MultiEdit` is legacy and unlisted; `NotebookEdit` writes notebooks, never Markdown. Breaks: a Markdown write through an unmatched tool.
  4. On exit 0, JSON on stdout is parsed: `hookSpecificOutput.additionalContext` reaches Claude, top-level `systemMessage` reaches the user; stderr on exit 0 goes to the debug log only. On any exit other than 0 and 2, the hook is non-blocking and the transcript shows only the first stderr line. Breaks: the `warn` channel; the visibility of a configuration failure.
  5. Hook input carries `cwd`, `tool_name`, `tool_input`; hooks run in the current directory, which follows worktrees and `cd`. The repository root is therefore derived from the written file's path (`git rev-parse --show-toplevel`), never from `cwd`. Breaks: root discovery.
  6. `${CLAUDE_PLUGIN_ROOT}` is the plugin's root in hook commands; `hooks/hooks.json` uses a top-level `hooks` key; `name` is the only required manifest field; only `plugin.json` lives in `.claude-plugin/`; skills are `/<plugin>:<skill>`. Breaks: plugin load.
  7. Default command-hook timeout is 600 s; per-hook `timeout` is in seconds. Breaks: nothing at 30 s unless a repository holds tens of thousands of Markdown files.
  8. `git check-ignore --no-index -v -n -z --stdin` against a fresh null repository with an empty work tree and `core.excludesfile` set to one policy's patterns evaluates paths that do not exist yet, reports one deciding pattern per path (a `!` pattern means not in territory), and is unaffected by the consumer's own `.gitignore`; `core.ignorecase` must be pinned false. Breaks: territory verdicts.
  9. A skill's `paths` limits automatic activation; `description` plus `when_to_use` are capped at 1,536 characters in the listing. Breaks: the always-on budget.
- **Research:** [docs/research/const-meta-types.md](../../docs/research/const-meta-types.md) (2026-09-18). Per row: [A1.4](../../docs/requirements.md#a1-4) gate at `PreToolUse` — **confirmed**; [A1.5](../../docs/requirements.md#a1-5) advisory skill — **confirmed**; [A2.3](../../docs/requirements.md#a2-3) same script at write time plus scan backstop — **confirmed** (no `SessionStart` scan: cost on every compaction without a gate). Schema validation is a PyYAML-only mirror of the kernel schemas rather than the `jsonschema` library (four more dependencies, one compiled), proven equal by the kit's fixtures; the module ships without the kit's schema files, so the mirror is the only copy a consumer has.

**Error messages.** Copied verbatim into the script; `{…}` are the values filled in. Findings are `RED`, three lines each (what failed / why the rule exists / the exact fix), followed by a count line; configuration failures are `BROKEN`, one self-sufficient line (only the first stderr line reaches the user in hook mode), followed by a count line.

| key | first line | why | fix |
|---|---|---|---|
| F1 | `RED: {path}: no frontmatter envelope` | a governed document declares its authority in its envelope, or sessions guess it | start the file with a YAML block between two '---' lines carrying id: <kebab-id>, type: current-state \| task-record \| non-authoritative, title: <one line>, status: active \| inactive |
| F2 | `RED: {path}: frontmatter opened with '---' but never closed` | an unclosed envelope is unreadable by machines and by the next session | close the YAML block with a line holding only '---' |
| F3 | `RED: {path}: frontmatter is not valid YAML ({error})` | the envelope is read by machines, so it must parse | repair the YAML between the '---' lines; keep the four fields id, type, title, status |
| F4 | `RED: {path}: envelope field(s) invalid: {list}` — items such as `type missing`, `type 'spec' not one of current-state \| task-record \| non-authoritative`, `id 'Note_A' is not kebab-case`, `title empty`, `title longer than 200 characters`, `status 'open' not one of active \| inactive`, `policy 'X' is not a kebab-case policy id` | the envelope is the one place a document's authority is declared, and it is read by machines | set each named field: id = stable kebab-case (never changed, never reused); type = current-state (reconciled truth) \| task-record (change delta) \| non-authoritative (explanation); title = one line; status = active \| inactive |
| F5 | `RED: {path}: id '{id}' is already carried by {other path}` | an id is a stable identifier: two documents sharing one break every reference to it | give this document its own id, never a retired one; if this is a move, delete the old file in the same change |
| F6 | `RED: {path}: declares policy '{id}' but no policy with that id lies in the root policy's territory {patterns}` | a governed document resolves to exactly one governing policy, or its rules are undefined | declare the id of a policy that exists there, or drop the declaration and place the file in a claimed territory |
| F7 | `RED: {path}: matched by {n} policy territories: {id} ({pattern}), {id} ({pattern})` | a document resolves to exactly one governing policy, or two rule sets compete | narrow one territory in constitution.yaml so the patterns no longer overlap; during a move, declare the intended one with 'policy: <id>' in the envelope while an active task-record covers it |
| F8 | `RED: {path}: declares policy '{id}' but its path is claimed by '{id}' ({pattern})` | the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it | remove 'policy: {id}' from the envelope, or move the file into the territory of '{id}': {patterns} |
| F9 | count: `RED: {n} finding(s) — 1 document examined ({path})` (hook) / `RED: {n} finding(s) — {g} governed document(s) examined, {m} Markdown file(s) scanned, {p} policies` (scan) | — | — |
| G1 | `GREEN: const-meta-types: 1 document examined, governed by {policy id}` / `GREEN: const-meta-types: 0 documents examined — {reason}` (not Markdown, outside the repository, no dials file, no `root_policy`, outside claimed territory, an `Edit` the tool will reject) / scan: `GREEN: const-meta-types: {g} governed document(s) examined, {m} Markdown file(s) scanned, {p} policies` | — | — |
| W1 | `severity: warn`: exit 0 with JSON — `additionalContext` = the `RED` lines plus `const-meta-types: severity is warn: the write proceeds, but the finding stands and recurs on every write until fixed`; `systemMessage` = `const-meta-types (warn): {first line}` | — | — |
| C1 | `BROKEN: const-meta-types needs python3 — install Python 3 (https://www.python.org/downloads/) — until then Markdown writes pass unchecked` | — | — |
| C2 | `BROKEN: const-meta-types needs PyYAML — run: python3 -m pip install pyyaml — until then Markdown writes pass unchecked` | — | — |
| C3 | `BROKEN: const-meta-types needs git on PATH — fix: install git (https://git-scm.com/downloads)` | — | — |
| C4 | `BROKEN: constitution.yaml is not valid YAML ({error}) — fix: fix the file; nothing is checked until it parses` | — | — |
| C5 | `BROKEN: constitution.yaml: {detail} — fix: {fix}` for each schema rule read: `root_policy must be a non-empty string`; `territory_dialect '{d}' is not supported by const-meta-types (supports: gitignore)`; `namespace '{k}' must be a mapping`; `{k}.territory must be a list of non-empty strings`; `{k}.catalog must be {prefix: <a-z0-9>, width: <integer >= 1>}`; `const-meta-types.severity must be block or warn` | — | — |
| C6 | `BROKEN: constitution.yaml names root_policy '{path}' but no such file exists — fix: create it, or point root_policy at the policy for policies` | — | — |
| C7 | `BROKEN: root policy '{path}' carries no readable id in its envelope — fix: give it the envelope (id, type, title, status); its id names its namespace` | — | — |
| C8 | `BROKEN: root policy '{id}' claims no territory in constitution.yaml — fix: write {id}: {territory: [<where policies live, including the root itself>]} — nothing is governed until then` | — | — |
| C9 | `BROKEN: root policy '{path}' lies outside its own territory {patterns} — fix: every chain of governance ends at the root; widen {id}.territory to include it` | — | — |
| C10 | `BROKEN: constitution.yaml: namespace '{ns}' claims territory but no policy with id '{ns}' lies in the root policy's territory — fix: create the policy document there first, or remove the namespace — a claim without a policy behind it governs nothing` | — | — |
| C11 | count: `BROKEN: the check could not run — 0 documents examined` | — | — |

**Installed components reference nothing in the kit.** The skill, hook, scripts, error text, fixtures, and install note name no kit document; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

| dial | default | meaning |
|---|---|---|
| `severity` | `block` | `block`: a finding exits 2 and the write is blocked. `warn`: the finding is reported to Claude and to the user and the write proceeds — the adoption path onto a repository with legacy documents. The scan ignores it. |

Territory, the root policy, and the dialect are the kernel-owned keys and the policy namespaces of [kernel §6](../../kernel/CONVENTIONS.md#k6), not dials of this module.

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

**Honest limits**, each with its backstop:

1. **Shell writes.** A heredoc, `sed -i`, `mv`, or any Bash command is not a `Write` or `Edit`; the hook never sees it. Backstop: the scan, on demand and in CI; the skill tells the agent to run it after a shell edit.
2. **Writes by other actors.** Humans, other tools, merges, and rebases bypass the hook. Backstop: the scan in CI.
3. **Configuration failure is non-blocking in hook mode.** Exit 1 is what the runtime ruling fixes, and the platform treats it as a non-blocking error: the user sees the first stderr line, Claude sees nothing, the write proceeds. The message is designed to be complete on that one line. Backstop: the scan exits 1 with the same message, so CI turns red until the configuration is repaired.
4. **`Edit` is reconstructed, not observed.** The script applies `old_string` → `new_string` to the file on disk to judge the result; an edit the tool itself would reject (file missing, string absent) is skipped with a visible zero count.
5. **The declaration's condition is not checked.** Whether "an active task-record covers the move" holds is judgment; the gate accepts any declaration that names a matching or existing policy.
6. **Markdown means `.md`.** Other extensions are outside the module.
7. **Timeout.** At 30 s the platform abandons the hook as a non-blocking error; repositories large enough to hit it are the friction signal of [§12](#t12).
8. **Duplicate ids across history** ("never reused") are not checked; only the present tree is.

**Exit-code contract** (both modes): `0` green or nothing examined (the count line says which); `2` finding — the repository is wrong; `1` configuration failure — the checker could not run (missing runtime or library, malformed or contradictory dials file, missing root policy, git absent). A missing tool is loud, never a silent pass.

<a id="t10"></a>
## 10. Acceptance

Runner: `tests/run.sh` (bash; needs git, Python 3, PyYAML) builds `tests/fixtures/repo/` — a three-policy consumer with a deliberate overlap — in a temporary git repository and drives the gate with real `PreToolUse` events. Each item names its verification kind.

| item | kind | what it proves |
|---|---|---|
| T1 `tests/fixtures/cases/01-envelope-missing/` (each case: `target`, `red.txt`, `green.txt` — inputs the runner writes as Markdown into the temporary consumer) | fixture | frontmatter-less file blocked (F1); corrected file passes |
| T2 `tests/fixtures/cases/02-envelope-invalid/` | fixture | invalid `id`, `type`, `status` blocked (F4); corrected file passes |
| T3 `tests/fixtures/cases/03-no-policy/` | fixture | declaration naming a non-policy blocked (F6); declaration naming a policy, path mapping absent, passes |
| T4 `tests/fixtures/cases/04-multi-policy/` | fixture | two territories, no declaration, blocked (F7); declaration naming one of them passes |
| T5 `tests/fixtures/cases/05-contradicting-declaration/` | fixture | declaration contradicting the path blocked (F8); without it passes |
| T6 `tests/fixtures/cases/06-duplicate-id/` | fixture | id carried by another governed document blocked (F5); own id passes |
| T7 (runner, case 7) | fixture | an `Edit` removing `type` is blocked on the reconstructed result; an `Edit` in the body passes |
| T8–T10 (runner, cases 8–10) | fixture | exit-code split: malformed dials file, territory without a policy, missing `python3` each exit 1 with `BROKEN`, never 2, never 0 |
| T11–T12 (runner, cases 11–12) | fixture | examined count on a skip: outside territory and non-Markdown both print `0 documents examined` and exit 0 |
| T13 (runner, case 13) | fixture | `severity: warn`: exit 0, JSON with `additionalContext` carrying the `RED` lines |
| T14–T15 (runner, cases 14–15) | fixture | scan mode reports the finding with counts and exits 2 under `warn`; green prints counts |
| T16 | live | the scan over this repository (consumer zero): every governed kit document green, counts printed |
| T17 | live | the plugin loaded in a session in this repository via `--plugin-dir`; a frontmatter-less write into claimed territory is blocked with F1, the corrected write passes |
| T18 | review | the pairs of [§8](#t8) and the error texts of [§6](#t6), at the one yes |
| T19 | live, deferred to the consumer's bootstrap | the consumer-live proof (decision [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) section 3) |

**Examined count.** Every exit prints it: hook mode `1 document examined, governed by …` or `0 documents examined — <reason>`; scan mode governed documents, Markdown files scanned, and policies; `BROKEN` prints `0 documents examined`.

<a id="t11"></a>
## 11. Siblings

**Depends on:** [kernel §1](../../kernel/CONVENTIONS.md#k1) (envelope), [§2](../../kernel/CONVENTIONS.md#k2) (the type enum), [§3](../../kernel/CONVENTIONS.md#k3) (territory, policy, resolution, the three defects), [§6](../../kernel/CONVENTIONS.md#k6) (dials file, kernel-owned keys, dialect, portability), [§7](../../kernel/CONVENTIONS.md#k7) (naming). Nothing else.

**Kernel alone:** on a bare repository with no `constitution.yaml`, every write passes with a visible zero count; with a dials file naming a root policy, every Markdown write into claimed territory is checked and the scan runs. Policies are the consumer's documents; the module ships none.

**Optional enhancements:** when module `const-locations` is installed, documents are born in their canonical home from the policy's template, so this gate sees fewer findings — it stays the guard either way. When module `const-catalogs` is installed, the `catalog` shape of a numbered kind (`<prefix>-<nnnn>-<slug>` ids and stems) is checked there; this module validates only that the key is well-formed. When module `const-decision-records` is installed, the body shape of a decision record is its concern; this module checks the envelope only.

<a id="t12"></a>
## 12. Deferred

1. **A `Bash` matcher inspecting commands for Markdown writes.** Signal: consumer commit notes recurring on shell edits that escaped the hook and were caught late by the scan. The platform calls Bash matching best-effort and points to permissions for a hard deny, so the scan is the honest backstop until then.
2. **`pathspec` as a fallback matcher.** Signal: a consumer reports a territory verdict where git and the kernel's dialect description disagree.
3. **Other Markdown extensions** (`.markdown`, `.mdx`). Signal: a consumer's governed documents use one.
4. **Id reuse across history.** Signal: a retired id resurfacing in a consumer and breaking references; the check needs git history and a definition of "retired".
5. **Checking the declaration's condition** (an active task-record covering the move). Signal: declarations left in place after moves complete; the check needs the record catalog of module `const-decision-records`, which would be a kernel candidate.
6. **Windows without a POSIX shell.** Signal: a consumer on Windows; the entry point would become a `.cmd` beside the `.sh`.
7. **Performance on very large repositories.** Signal: the 30 s hook timeout hit; the fix is a cached index, not a bigger timeout.
