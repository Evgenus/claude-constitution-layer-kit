---
id: res-0001-const-meta-types
type: non-authoritative
title: Research comparison — const-meta-types (2026-09-18)
status: active
---

# Research comparison — const-meta-types (2026-09-18)

Surveyed 2026-09-18; local `claude --version` prints `2.1.251 (Claude Code)`. Experiments ran with git 2.54.0, Python 3.12.4, PyYAML 6.0.2, jsonschema 4.26.0, pathspec 0.12.1 on macOS.

Scope: the rows of [`const-meta-types`](../requirements.md#const-meta-types) — [requirement A1.4](../requirements.md#a1-4), [requirement A1.5](../requirements.md#a1-5), [requirement A2.3](../requirements.md#a2-3) — under [dec-0015-pre-module-audit-rulings](../decisions/dec-0015-pre-module-audit-rulings.md) (Python 3 with PyYAML; one write-time script for envelope and resolution with a scan mode; `severity` block | warn). Vocabulary: envelope ([kernel §1](../constitution/CONVENTIONS.md#k1)), territory and policy ([kernel §3](../constitution/CONVENTIONS.md#k3)), dials file ([kernel §6](../constitution/CONVENTIONS.md#k6)). Sources by authority: official Claude Code documentation, community harnesses, tool documentation, experiments reported here.

## 1. Write-time envelope gate ([requirement A1.4](../requirements.md#a1-4))

- **A. `PreToolUse` command hook, matcher `Write|Edit`, exit 2 on a defect.** Class: platform hook, deterministic. Maturity:
  - **documented** — exit 2 "Blocks the tool call" and Claude sees stderr as the reason;
  - **the input carries** `tool_input.file_path` (always absolute) and, for `Write`, the full `content` ([hooks reference](https://code.claude.com/docs/en/hooks)).

  Cost: one Python process per matched write via `"${CLAUDE_PLUGIN_ROOT}"/scripts/...` ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). Cannot see `Bash` writes (heredocs, `sed -i`); an `Edit` shows only `old_string`/`new_string`, so the script reads the file and applies the replacement itself. Precedent: [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) (Python, `sys.exit(2)`); [@constellos/claude-code-kit](https://registry.npmjs.org/@constellos%2Fclaude-code-kit) (Zod frontmatter schema on `Write|Edit`, TypeScript under `bun`).
- **B. `PostToolUse` hook.** Exit 2 "Shows stderr to Claude; the tool already ran" ([hooks reference](https://code.claude.com/docs/en/hooks)). Cannot block; the row says blocked.
- **C. git `pre-commit` validator.** [check-jsonschema](https://check-jsonschema.readthedocs.io/en/latest/precommit_usage.html) validates JSON/YAML/JSON5; Markdown front matter is not an input ([usage](https://check-jsonschema.readthedocs.io/en/latest/usage.html)). [remark-lint-frontmatter-schema](https://github.com/JulianCataldo/remark-lint-frontmatter-schema) validates front matter against a JSON schema ("Must have required property"), Node runtime, schema by in-file `$schema` key or glob map. Cost: Node or pip on every machine plus a per-clone install a plugin cannot perform. Cannot fire at write time; `--no-verify` bypasses it.
- **D. CI on pull request.** Cannot teach mid-session — the backstop role (section 3), not the gate.
- **E. Prose linter.** [Vale](https://docs.vale.sh/llms-full.txt) scopes each *present* front-matter field (`text.frontmatter.title`); a missing field yields no scope, so absence is undetectable. [markdownlint](https://github.com/DavidAnson/markdownlint/blob/main/README.md) skips front matter by regex, no rule on its contents. Cannot detect a missing key, an out-of-enum `type`, or a policy.
- **F. Prompt or agent hook** ([hooks guide](https://code.claude.com/docs/en/hooks-guide)). Judgment dressed as a check; rejected under [template §6](../../module-template/MODULE.md#t6).

**Recommendation: A.** Only this moment blocks and teaches; B and E cannot block, C and D are late, F is not a gate. Bash writes fall to scan mode, never to a Bash matcher: the `if` field's Bash matching is "best-effort" and the documentation says to use permissions, not hooks, for a hard deny ([hooks reference](https://code.claude.com/docs/en/hooks)). `NotebookEdit` needs no matcher: its path field is `notebook_path` ([permissions](https://code.claude.com/docs/en/permissions)) and a notebook is never a governed document.

## 2. Resolution gate ([requirement A2.3](../requirements.md#a2-3))

Same moments, same verdicts. Specific to resolution:

- **No existing tool resolves "path → exactly one policy".** Checked: [remark-lint-frontmatter-schema](https://github.com/JulianCataldo/remark-lint-frontmatter-schema) (glob → schema, silent when two match), [runlist, formerly dotmd](https://github.com/reowens/dotmd) (type by frontmatter key — declaration, the kernel's secondary route), [@constellos/claude-code-kit](https://registry.npmjs.org/@constellos%2Fclaude-code-kit) (`files` patterns, no multi-match rule), [Vale](https://docs.vale.sh/llms-full.txt) (scopes rules, not documents), [check-jsonschema](https://check-jsonschema.readthedocs.io/en/latest/precommit_usage.html) (one schema per `files` regex). The three defect classes exist in none.
- **Root discovery.** `cwd` "follows Claude" into worktrees and after `cd` ([hooks reference](https://code.claude.com/docs/en/hooks)), so the repository root comes from the written file's directory (`git -C <dir> rev-parse --show-toplevel`), never from `cwd` or `CLAUDE_PROJECT_DIR`.

**Recommendation: A, in the same script and invocation as section 1**, as ruled: two hooks would parse one write twice and could disagree.

## 3. Repository-scan backstop

- **A. On-demand script mode** (`--scan` over `git ls-files` plus untracked non-ignored Markdown). Cost: one process per run, paths batched through `--stdin`; zero always-on characters. Cannot run itself.
- **B. `SessionStart` hook.** Fires on `startup`, `resume`, `clear`, `compact`, `fork`; stdout enters context; exit 2 "Shows stderr to user only" ([hooks reference](https://code.claude.com/docs/en/hooks)). Cost: a full scan on every compaction, findings in context when nothing changed; cannot block.
- **C. git `pre-commit`.** Per-clone install the plugin cannot do; `--no-verify` bypass.
- **D. CI on pull request.** One consumer workflow line calling A; absent before the consumer has CI.

**Recommendation: A, with D as the consumer's wiring** — the row's own "same script as CI backstop on PR". B is cost without a gate. A skill may tell the agent to run A after a Bash-made edit in territory (advisory).

## 4. Territory matching in the gitignore dialect

- **A. `git check-ignore`.** Documented:
  - **exit 0 on a match**, 1 on none, 128 fatal;
  - `-v` prints the deciding pattern;
  - `-n` adds non-matches;
  - `-z` NUL-separates;
  - `--no-index` skips the index ([git-check-ignore](https://git-scm.com/docs/git-check-ignore)).

  Sources by precedence: command line, `.gitignore` in the path's directory and parents, `$GIT_DIR/info/exclude`, `core.excludesFile`; last match wins within a level; no re-inclusion under an excluded directory ([gitignore](https://git-scm.com/docs/gitignore)). Experiment in a scratch directory — `git init nullrepo`, `mkdir empty`, territory file `terr.txt` holding `docs/policies/**` and `docs/*.md`, a repository `ci-exp` whose `.gitignore` holds `*.md`:
  - E1. In `ci-exp`, `git -c core.excludesfile=terr.txt check-ignore -v --no-index README.md` → `.gitignore:1:*.md`, exit 0; the same with `--git-dir=nullrepo/.git --work-tree=ci-exp`. The work tree's ignore files outrank `core.excludesFile`; neither that key nor a foreign git dir isolates the territory list.
  - E2. `git --git-dir=nullrepo/.git --work-tree=empty -c core.excludesfile=terr.txt check-ignore --no-index -v docs/policies/new.md`, cwd `empty` → `terr.txt:1:docs/policies/**`, exit 0; `README.md` → exit 1. **An empty work tree isolates the territory list.** A pattern put in `nullrepo/.git/info/exclude` still matched, so the null repository must be fresh.
  - E3. Paths need not exist: `docs/policies/a/b/c/new.md` matched in the empty tree — a file about to be written is evaluable. A trailing-slash pattern (`docs/policies/`) matched a not-yet-existing file beneath it.
  - E4. `docs/*.md` matched `docs/x.md`, not `docs/sub/x.md` (single star stops at a slash); slash-less patterns (`CLAUDE.md`, `notes`) matched at any depth.
  - E5. `-v -n -z --stdin` over three paths → four NUL-separated fields per path, empty source/line/pattern on a non-match; one process per batch.
  - E6. `/etc/hosts` → `fatal: ... is outside repository`, exit 128; an absolute path inside the tree and a `./` path both work. Pass repository-relative paths only.
  - E7. `git init` on macOS set `core.ignorecase=true`, and `Docs/Policies/new.md` matched; with `-c core.ignorecase=false` it did not. Pin it.
  - E8. A non-existent `core.excludesfile` path is silently ignored (exit 1, no error): check the territory file exists first.
  - E9. Negation: `docs/**` then `!docs/keep.md` → `-v` printed `terr.txt:2:!docs/keep.md` for `docs/keep.md` **with exit 0**; `docs/sub/keep.md` matched `docs/**`. Parse the `-v` fields and read a `!` pattern as "not in territory", never the exit code alone.
  - E10. Two patterns matching one path (`docs/**`, `docs/policies/**`) → `-v` reported only `docs/**`. **One deciding pattern per path, not all matches**: the multi-policy defect needs one run per policy, each policy's territory as its own excludes file, all paths batched via `--stdin`.
  - E11. Without `--no-index` a tracked matching file reported exit 1; with it, matched. Mandatory in scan mode.
  Cost: `git init` of a temporary null repository per run (milliseconds) plus one `git` process per policy.
- **B. Python `pathspec` (`GitIgnoreSpec`).** `pip install pathspec`, MPL-2.0, no dependencies ([pathspec docs](https://python-path-specification.readthedocs.io/en/stable/readme.html)). Experiment: verdicts identical to A on `**`, `*`, negation, case; returns all matches, so multi-policy is one call. Cannot be assumed present — a second pip dependency, with `gitwildmatch` renamed across major versions ([pathspec changes](https://python-path-specification.readthedocs.io/en/stable/changes.html)).
- **C. `fnmatch`.** `fnmatchcase("docs/sub/x.md", "docs/*.md")` → `True`: `*` crosses slashes, `**` is a plain `*`. Wrong dialect.

**Recommendation: A**, as ruled and as E2 verifies: `git --git-dir=<fresh-null-repo>/.git --work-tree=<empty-dir> -c core.excludesfile=<one-policy-territory-file> -c core.ignorecase=false check-ignore --no-index -v -n -z --stdin`, one run per policy, verdicts from the `-v` fields with `!` as non-match, repository-relative paths, territory file existence checked first. B is the fallback if a consumer reports a git discrepancy; C never.

## 5. Schema validation of the envelope and the dials file

Readers validate against the kernel's two schema files ([kernel §6](../constitution/CONVENTIONS.md#k6)). Those live in the kit, and a consumer installs the module without it ([template §6](../../module-template/MODULE.md#t6)), so the schema can only come from inside the plugin:

- **A. Python `jsonschema` against a schema copy in the plugin.** `pip install jsonschema`, Draft 2020-12 ([jsonschema docs](https://python-jsonschema.readthedocs.io/en/stable/)); 4.26.0, Python ≥ 3.10 ([PyPI](https://pypi.org/project/jsonschema/)); local `pip show` lists `attrs`, `jsonschema-specifications`, `referencing`, `rpds-py` (compiled). Cost: a second install command in every teaching error, a platform wheel, a copy that can drift. Absent on a bare interpreter locally.
- **B. Hand-coded checks with PyYAML only, mirroring the schema field by field.** Envelope: four required keys, two enums, one id pattern, one title length; dials: two kernel keys plus the `territory` and `catalog` shapes. Cost: ~40 lines kept equal to the schema, proven in the kit by running the real schema through `jsonschema` over the module's fixtures (kit developer dependency only). Cannot absorb a kernel extension without a module bump — required anyway.
- **C. Vendor a validator.** Rejected: [dec-0015-pre-module-audit-rulings](../decisions/dec-0015-pre-module-audit-rulings.md) admits vendored code only for literal kernel-section functions needed by two modules.

**Recommendation: B.** One dependency in the install message, no compiled wheel; the module document states "validates a mirror of the kernel schema, proven equal by kit fixtures". `yaml.safe_load` only ([PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)).

## 6. Advisory type-selection guidance ([requirement A1.5](../requirements.md#a1-5))

- **A. Plugin skill.** Always-on cost:
  - `description` plus `when_to_use`, capped at 1,536 characters in the listing;
  - **the body loads** on invocation and "stays there across later turns";
  - `paths` limits auto-activation to matching files ([skills](https://code.claude.com/docs/en/skills)) — territory is a runtime dial, so at most `**/*.md`.

  Invoked as `/<plugin>:<skill>` ([plugins](https://code.claude.com/docs/en/plugins)).
- **B. `SessionStart` hook printing the rules.** The full text on every `startup`, `resume`, `clear`, `compact`, `fork` ([hooks reference](https://code.claude.com/docs/en/hooks)); the contrastive pairs are hundreds of characters most sessions never need.
- **C. CLAUDE.md pointer line.** Consumer-maintained, version-drifting; permitted as the single pointer of `INSTALL.md` ([template §6](../../module-template/MODULE.md#t6)).
- **D. `.claude/rules/` with `paths:`.** Loads when Claude reads matching files ([memory](https://code.claude.com/docs/en/memory)); but the plugin component list — skills, commands, agents, hooks, MCP, LSP, monitors, `bin/`, `settings.json` — has no rules directory ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). Not shippable.
- **E. Plugin-root `CLAUDE.md`.** "not loaded as project context" ([plugins reference](https://code.claude.com/docs/en/plugins-reference)).

**Recommendation: A**, `paths: "**/*.md"`, the one-line rule in the description, the pairs in the body. Always-on characters: the description only.

## 7. Hook mechanics and plugin loading — discrepancies found

The verified facts are the numbered list below; this section records only where the task's claims and the documentation diverge.

- a. `MultiEdit` is absent from the tools list ([tools reference](https://code.claude.com/docs/en/tools-reference)) and called "the legacy `MultiEdit` tool" ([permissions](https://code.claude.com/docs/en/permissions)) — retired. Matchers of letters, digits, `_`, `-`, spaces, `,`, `|` are exact strings or lists (`Edit|Write` matches "either tool exactly"). Any other character makes an unanchored JavaScript regex, `Edit.*` also matching `NotebookEdit` ([hooks reference](https://code.claude.com/docs/en/hooks)).
- b. `permissionDecision` has a fourth value, `defer`. Exit codes other than 0 and 2 are non-blocking and the transcript shows only the first stderr line, prefixed `Failed with non-blocking status code:`; stderr on exit 0 "goes to the debug log only" ([hooks reference](https://code.claude.com/docs/en/hooks)). So `severity: warn` is exit 0 with `additionalContext` or `systemMessage`, not a non-zero exit.
- d. A `PostToolUse` `tool_response.bashEditDiff` listing files a Bash command changed exists but "Requires Claude Code v2.1.269 or later", is "best effort and in public beta", and is "not to enforce a policy" ([hooks reference](https://code.claude.com/docs/en/hooks)) — unfit for a gate.
- e. A folder of plugins under `--plugin-dir` "requires Claude Code v2.1.265 or later" ([CLI reference](https://code.claude.com/docs/en/cli-reference)). Local 2.1.251 predates it, its `--help` showing no folder form. A local-directory marketplace loads a plugin in place with `CLAUDE_PLUGIN_ROOT` at the source; `claude plugin validate <dir>` checks manifest, hooks and frontmatter ([plugins reference](https://code.claude.com/docs/en/plugins-reference)).
- f. Default command timeout is 600 seconds, not 60; hooks run "in the current directory", not the project root ([hooks reference](https://code.claude.com/docs/en/hooks)).
- g. `updatedInput` replaces the whole tool input before execution ([hooks reference](https://code.claude.com/docs/en/hooks)); silently rewriting an envelope is the opposite of a teaching error — rejected.

## Recommendations summary

1. [Requirement A1.4](../requirements.md#a1-4) — **CONFIRMED**: gate, `PreToolUse` on `Write|Edit`, exit 2 with the teaching error on stderr; Bash writes fall to scan mode.
2. [Requirement A1.5](../requirements.md#a1-5) — **CONFIRMED**:
   - **advisory skill**, `paths: "**/*.md"`;
   - **always-on cost** is the description;
   - **rules files** are not a plugin component, a plugin-root CLAUDE.md is not loaded.
3. [Requirement A2.3](../requirements.md#a2-3) — **CONFIRMED**: same script and invocation, plus on-demand scan mode wired into consumer CI; no `SessionStart` scan. Territory via `git check-ignore` against a fresh null repository with an empty work tree, one run per policy, `core.ignorecase=false`, `--no-index`, verdicts from `-v`. Schema checks are a PyYAML-only mirror proven equal by kit fixtures.

Platform facts for the module document's slot (all verified 2026-09-18):

1. `PreToolUse` exit 2 blocks the call; Claude sees stderr — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: the gate stops blocking.
2. `Write` = `file_path` + `content`; `Edit` = `file_path`, `old_string`, `new_string`, `replace_all`; `file_path` always absolute, `~` and relative spellings expanded, backslashes on Windows — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: locating or reconstructing the document.
3. `Write|Edit` is an exact-string list, not a regex — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: tool matching.
4. `NotebookEdit` uses `notebook_path`; `MultiEdit` is legacy and unlisted — [permissions](https://code.claude.com/docs/en/permissions), [tools reference](https://code.claude.com/docs/en/tools-reference). Breaks: a Markdown write through an unmatched tool.
5. `permissionDecision` ∈ allow | deny | ask | defer with `permissionDecisionReason` (for deny, shown to Claude); stderr on exit 0 never reaches the transcript — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: the `warn` channel.
6. Input carries `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `permission_mode`, `tool_name`, `tool_input`, `tool_use_id`; hooks run in the current directory; `cwd` follows worktrees; `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_DATA` exported — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: root discovery and script path.
7. Default command-hook timeout 600 s, per-hook `timeout` in seconds; matching hooks run in parallel — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: a slow scan inside a hook.
8. `hooks/hooks.json` under a top-level `hooks` key or inline in `plugin.json`; `name` the only required manifest field; skills as `/<plugin>:<skill>`; plugin-root CLAUDE.md not loaded; no `rules/` component — [plugins reference](https://code.claude.com/docs/en/plugins-reference), [plugins](https://code.claude.com/docs/en/plugins). Breaks: plugin load or the advisory carrier.
9. `--plugin-dir` one path per flag, repeatable; folder form needs v2.1.265+ (local 2.1.251 lacks it); `/reload-plugins` applies changes — [CLI reference](https://code.claude.com/docs/en/cli-reference), [plugins](https://code.claude.com/docs/en/plugins). Breaks: the live-proof procedure.
10. `SessionStart` matchers `startup`, `resume`, `clear`, `compact`, `fork`; stdout enters context; cannot block — [hooks reference](https://code.claude.com/docs/en/hooks). Breaks: nothing shipped here.
11. Skill description capped at 1,536 characters; body loads on invocation; `paths` limits auto-activation — [skills](https://code.claude.com/docs/en/skills). Breaks: the always-on budget claim.
12. `git check-ignore`: exit 0/1/128; `-v` prints one deciding pattern; work-tree ignore files and `info/exclude` outrank `core.excludesFile`; non-existent paths evaluable — [git-check-ignore](https://git-scm.com/docs/git-check-ignore), [gitignore](https://git-scm.com/docs/gitignore), experiments E1–E11. Breaks: territory verdicts.
