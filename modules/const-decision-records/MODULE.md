---
id: module-const-decision-records
type: current-state
title: const-decision-records — write-time gate on decision records, and the procedures around a recorded ruling
status: active
---

# MODULE.md — `const-decision-records`

*Draft at manifest version `0.0.1`, no open slots; published at `0.1.0` in rollout Phase D. This document is the module's description ([template](../../module-template/MODULE.md)). Every list and table row carries a handle.*

<a id="t1"></a>
## 1. Purpose

A session and its user argue a ruling through — options, objections, a pick — and the ruling stays in the chat: the next session finds the code changed and no reason why, and re-opens the question. Elsewhere a naming nit is written up with the same ritual as a structural choice, until nobody writes anything up; and a fix to the harness waits behind the very gate it fixes. The first failure compounds: every unrecorded ruling is reasoning that must be reconstructed later, and a document that calls itself a decision record without saying what was at stake or who decided is no better than the chat it came from. This module makes a decision record *valid at the moment it is written* — its stakes and its decider are declared, or the write is blocked with a message that teaches the fix — and ships the two procedures around it: pricing and recording a decision, and promoting routine calls that keep recurring.

<a id="t2"></a>
## 2. Failure class

Split. **Accumulating:** records without stakes or decider, and rulings never recorded — each one is a piece of reasoning a later session reconstructs by archaeology, and the cost grows with every such ruling. **Self-limiting:** mispriced ceremony — a team that ritualizes nits feels the drag and stops by itself; the triage guidance addresses it and no gate does. **Entry trigger:** day-one install set of every project that records decisions; the first real decision is the moment the gate and the creation skill must already be there.

<a id="t3"></a>
## 3. Rows

| row | this module's reading |
|---|---|
| [A3.4](../../docs/requirements.md#a3-4) | Three readings. **What a record is:** a Markdown document governed by a policy the dial `record_policies` names — a document kind is one policy's territory ([kernel §3](../../kernel/CONVENTIONS.md#k3)), so the consumer's record policy is the only project-blind definition of "this is a record"; carrying a `stakes` key does not make a document a record, and with the dial unset nothing is examined, visibly (decision [dec-0024-decision-records-module-rulings](../../docs/decisions/dec-0024-decision-records-module-rulings.md) item 1). Governed means by path, or by a `policy: <id>` declaration where the path maps to no policy; where several territories claim the path, a declaration naming one of them picks it, and otherwise every claimant counts — the overlap is another check's defect, and the record is examined as a record either way. **What valid covers:** what a record adds to the envelope ([kernel §5](../../kernel/CONVENTIONS.md#k5)) — `type: task-record`, `stakes` one of the three recorded levels, `decider` a non-empty string — checked against a mirror of the kernel's record schema; `id`, `title` and `status` have their owner in module `const-meta-types` and are not judged here, so that with both modules installed a defect is taught once (item 2 of the same record). An envelope that cannot be read at all is one finding here too, since the two fields have nowhere to live: that one defect both modules report. **`stakes: routine`** is red by the enum and gets its own message, because the fix differs: delete the record, write the commit note (item 3). "Records via skill, never free-form" is advisory: nothing in a file tells how it was made, and the gate judges the result. "Routine → commit note" is the skill's first step. |
| [A3.6](../../docs/requirements.md#a3-6) | Advisory procedure, a skill: gather commit notes, cluster by the question they answer, promote a recurring theme to a record or a documented procedure. The row's optional assist script is not shipped: git already counts trailer values (`git shortlog --group=trailer:<key>`), so the assist is one command the skill names, keyed by the dial `note_trailer`. |

Rows enforced through [A3.4](../../docs/requirements.md#a3-4) and not homed here: [A3.1](../../docs/requirements.md#a3-1) (the enum), [A3.2](../../docs/requirements.md#a3-2) (frontmatter by the gate, body shape by the skill's template and review), [A3.3](../../docs/requirements.md#a3-3) (git-native). [A3.5](../../docs/requirements.md#a3-5) and [A3.7](../../docs/requirements.md#a3-7) are the consumer's binding; this module gives them their dials ([§7](#t7)) and reads them in the skill.

<a id="t4"></a>
## 4. Decisions

1. [dec-0024-decision-records-module-rulings](../../docs/decisions/dec-0024-decision-records-module-rulings.md) — the rulings of this module's authoring: a record is a document governed by a named record policy; the gate judges the record's own fields only; `stakes: routine` is its own finding, and the deterministic slice of record immutability is deferred.
2. [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) — section 1 fixes the runtime (Python 3 with PyYAML, POSIX shell for the entry point, a missing runtime exits 1 with the install command); section 2, ruling (a), makes module `const-meta-types` the one write-time guard of the envelope, which is why this gate leaves `id`, `title` and `status` alone; section 7 adds the `severity` dial.
3. [dec-0014-territory-dialect](../../docs/decisions/dec-0014-territory-dialect.md) — territory patterns are gitignore syntax by default; this module supports `gitignore` only and reports any other dialect as a configuration failure.
4. [dec-0018-dials-schema](../../docs/decisions/dec-0018-dials-schema.md) — every read of `constitution.yaml` validates the keys read; a malformed file is a configuration failure.
5. [dec-0020-gate-script-rules](../../docs/decisions/dec-0020-gate-script-rules.md) and [dec-0022-output-log-through-logging](../../docs/decisions/dec-0022-output-log-through-logging.md) — the fifteen gate-script rules and the output log on the standard library's `logging`.
6. [dec-0023-shared-gate-code-at-module-two](../../docs/decisions/dec-0023-shared-gate-code-at-module-two.md) — the generic modules of the package are the first module's, copied; the forced edits are listed under Phase A step 3 of the [rollout plan](../../docs/rollout-plan.md).
7. [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md) — the mechanism choices of [§6](#t6) rest on this module's own dated comparison.
8. [dec-0012-record-references-are-provenance](../../docs/decisions/dec-0012-record-references-are-provenance.md) — the skill's rule that an applied ruling stands in the text of the current-state document it changed.

<a id="t5"></a>
## 5. Invariant

**Every Markdown document governed by a named record policy carries, at the moment it is written through the platform's file tools, what a decision record adds to the envelope: `type: task-record`, `stakes` of `process`, `product` or `architecture`, and a non-empty `decider`.** Policy, governed, envelope, stakes and decision record are the kernel's ([§1](../../kernel/CONVENTIONS.md#k1), [§3](../../kernel/CONVENTIONS.md#k3), [§4](../../kernel/CONVENTIONS.md#k4), [§5](../../kernel/CONVENTIONS.md#k5)); "named" is the dial `record_policies` of [§7](#t7); "written through the platform's file tools" is the honest boundary of [§9](#t9).

The advisory rules beside it, each `advisory` in its own text: (R-a) price a decision by its stakes before acting, routine calls leave a commit note and no record; (R-b) a record is written from the skill's template, in one of the kernel's two body shapes, never with manufactured options; (R-c) `process` takes the fast lane — the record and one human yes; (R-d) a record is `active` while its ruling is being applied, `inactive` once applied, born `inactive` when applied in the creating commit; (R-e) reversing a ruling is a new record; (R-f) recurring commit notes on one theme are promoted to a record or a procedure.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

| component | path | carries |
|---|---|---|
| hook | `hooks/hooks.json` | `PreToolUse`, matcher `Write\|Edit` (an exact-string list on the platform), exec form: `command` `sh`, `args` `["${CLAUDE_PLUGIN_ROOT}/scripts/check-decision-record.sh"]`, timeout 30 s. The gate. |
| script (sh) | `scripts/check-decision-record.sh` | POSIX entry point: finds `python3`, exits 1 with the fix when it is missing, otherwise hands stdin and arguments to the Python entry point. Reads no YAML. |
| script (py) | `scripts/check-decision-record.py` | Thin Python entry point, parseable by any Python 3: checks the interpreter floor (3.12), then runs the package. Its docstring is the contract: events, modes, input read, exit codes, output channels, dials read. |
| package | `scripts/decision_records_gate/` | The check, beside its entry point, imported with no path manipulation. Its own modules: `checks` (the candidate policies of a document, the record fields), `modes` (hook, `--scan [DIR]`). Copied from the first module (decision [dec-0023-shared-gate-code-at-module-two](../../docs/decisions/dec-0023-shared-gate-code-at-module-two.md)): `errors`, `preflight`, `output`, `repository`, `territory`, `events`, `index`, `cli` unedited; `model`, `messages`, `envelope`, `dials` with the listed edits. Step down from a platform component: no platform component evaluates a document's frontmatter against a schema or resolves a path to a policy. Step down from an existing decision-record tool: every validator surveyed checks a status or date vocabulary the kernel excludes, and none knows `stakes` or a single `decider`. `mypy --strict` clean. |
| dependencies | `requirements.txt` | The declared libraries (PyYAML); the preflight imports each on every invocation, and the configuration-failure message prints the one install command for this file. |
| skill | `skills/record-decision/SKILL.md` + `record-template.md` | Rules R-a to R-e: the stakes triage with the seed pairs of [§8](#t8), the decider, where a record goes, the envelope, the two body shapes, status, reversal, and the advice to run the scan after a shell edit. The template sits beside the skill and is named through `${CLAUDE_SKILL_DIR}`. Model-invocable: a recorded-stakes decision surfaces mid-dialog. No `paths`: a territory is a runtime dial, which a static glob cannot carry. Advisory. |
| skill | `skills/promote-recurring-notes/SKILL.md` | Rule R-f: gather, cluster, promote, report. Names the git-native trailer count as the optional assist. Advisory. |
| install note | `INSTALL.md` | Requirements, the one dial that switches the check on, the skill-read dials, the scan command for CI, where the output log goes, what the module does not check, no CLAUDE.md pointer. |
| tests | `tests/run.py`, `tests/harness.py`, `tests/consumer.py` | The fixtures of [§10](#t10): numbered case records and assertions, driving the real entry point with real hook events. |
| command | none | a command file is the legacy form of a skill on the platform and cannot carry the template beside it. |
| agent | none | a record is the residue of a dialog — options argued, the decider's pick — that a subagent in its own context never saw. |
| script for the promotion loop | none | git counts trailer values natively; a script would add nothing to one command. |

- **Always-on content:** the two skill descriptions in the skill listing, 620 and 414 characters. No `SessionStart` hook: the triage is needed when a ruling is made, not in every session.
- **Platform facts relied on** (all verified 2026-09-18 against the official documentation; sources in the research comparison):
  1. A `PreToolUse` command hook exiting 2 blocks the tool call and Claude sees stderr as the reason. Breaks: the gate stops blocking.
  2. `Write` input is `file_path` + `content`; `Edit` input is `file_path`, `old_string`, `new_string`, `replace_all`; `file_path` is absolute for the file tools. Breaks: locating or reconstructing the document.
  3. A matcher made of letters and `|` is an exact-string list: `Write|Edit` matches those two tools and nothing else; `MultiEdit` is retired. Breaks: a Markdown write through an unmatched tool.
  4. On exit 0, JSON on stdout is parsed: `hookSpecificOutput.additionalContext` reaches Claude, top-level `systemMessage` reaches the user. On any exit other than 0 and 2 *with no schema-valid JSON on stdout*, the hook is non-blocking and the transcript shows the first stderr line; with such JSON on stdout, the JSON alone decides and the exit code is ignored — so a configuration failure keeps stdout free of JSON. Breaks: the `warn` channel; the visibility of a configuration failure.
  5. All matching hooks run in parallel; the same handler in two plugins is not deduplicated; every hook runs to completion; the most restrictive decision applies and an exit 2 routes as `deny`; `additionalContext` is kept from every hook. So with module `const-meta-types` installed too, one write starts two processes, either one can block, and neither sees the other. Breaks: the both-installed behaviour of [§9](#t9) and [§11](#t11).
  6. A timed-out command hook does not block the tool call, and neither does a hook that cannot start (a missing script path). Breaks: nothing — it is the limit stated in [§9](#t9).
  7. Hook output strings — `additionalContext`, `systemMessage`, plain stdout — are capped at 10,000 characters, the overflow saved to a file with a preview. Breaks: a `warn` payload past the cap; one record's findings stay far below it.
  8. Hook input carries `cwd`, `tool_name`, `tool_input`, `session_id`; `cwd` follows worktrees and `cd`, so the repository root is derived from the written file's path, never from `cwd`. Breaks: root discovery.
  9. `${CLAUDE_PLUGIN_ROOT}` is the plugin's root in hook commands and is substituted in a plugin skill's Markdown; `${CLAUDE_SKILL_DIR}` is the skill's own directory inside the plugin; supporting files beside `SKILL.md` are loaded when the skill refers to them; `hooks/hooks.json` uses a top-level `hooks` key and an exec form, `command` plus `args`; when a manifest is present `name` is its only required field, and only `plugin.json` lives in `.claude-plugin/`; skills are `/<plugin>:<skill>`. Breaks: plugin load; the skill's template and scan advice.
  10. Default command-hook timeout is 600 s; per-hook `timeout` is in seconds. Breaks: nothing at 30 s unless a repository holds tens of thousands of Markdown files.
  11. `git check-ignore --no-index -v -n -z --stdin` against a fresh null repository with an empty work tree and `core.excludesfile` set to one policy's patterns evaluates paths that do not exist yet and is unaffected by the consumer's own `.gitignore`; `core.ignorecase` must be pinned false. Breaks: territory verdicts.
  12. `${CLAUDE_PLUGIN_DATA}` is a persistent per-plugin directory outside the repository, exported to hook processes. Breaks: the default log location (the gate then logs nowhere — stdout remains).
  13. `description` plus `when_to_use` of a skill are capped at 1,536 characters in the listing. Breaks: the always-on budget.
  14. `git shortlog -ns --group=trailer:<key>` counts commits per trailer value; a trailer block must be the last paragraph of the message; keys match case-insensitively, values do not. Breaks: the assist command the promotion skill names.
- **Research:** [docs/research/const-decision-records.md](../../docs/research/const-decision-records.md) (2026-09-18). Per row: [A3.4](../../docs/requirements.md#a3-4) gate at `PreToolUse` plus scan, creation path advisory — **confirmed**; [A3.6](../../docs/requirements.md#a3-6) advisory procedure, no gate — **confirmed**, with the optional assist script reduced to a git-native command. On how the gate knows a record the comparison recommended location *and* content; the decider chose location alone ([§3](#t3)), because content detection with the dial unset reports a healthy count while the free-form record passes unseen. Schema validation is a PyYAML-only mirror of the kernel's record schema, for the first module's reason: the module ships without the kit's schema files. The kit proves the mirror with `scripts/check-schema-mirror.py`, which runs the real schema through `jsonschema` (a development dependency of the kit only).

**Error messages.** Each row is one function of `messages.py`, under the same key; `{…}` are its parameters. Findings are `RED`, three lines each (what failed / why the rule exists / the exact fix), followed by a count line; configuration failures are `BROKEN`, one self-sufficient line, followed by a count line. Keys `G1`, `W1`, `F9`, `N1` and the `C` series are the shared texts, word for word the first module's under this module's name; the `R` series, `N2`, two skip reasons and one `C5` pair are this module's.

| key | first line | why | fix |
|---|---|---|---|
| R1 | `RED: {path}: a decision record with no readable envelope ({detail})` — detail one of `the file does not start with a '---' line`, `opened with '---' but never closed`, `not valid YAML: {error}` | a record declares its stakes and its decider in the envelope: without them the ruling has no price and nobody accountable | start the file with a YAML block between two '---' lines carrying id: <kebab-id>, type: task-record, title: <one line>, status: active \| inactive, stakes: process \| product \| architecture, decider: <person or role> |
| R2 | `RED: {path}: decision-record field(s) invalid: {list}` — items such as `type 'current-state' is not task-record`, `stakes missing`, `stakes 'high' not one of process \| product \| architecture`, `decider missing`, `decider empty`, `decider must be a quoted string (YAML read it as int)` | stakes set the ceremony a ruling gets and decider names who is accountable for it; git can derive neither | set each named field: type = task-record (a record is a change delta); stakes = process (harness, policy or procedure) \| product (user-visible behaviour) \| architecture (structural, hard to reverse); decider = the person or role who made the choice, a non-empty string |
| R3 | `RED: {path}: stakes 'routine' — a routine call never produces a record` | ceremony scales with stakes: a call that is cheap to revert is noted in the commit message, and a record for it is ritual | delete this file and put the note in the commit message; or, if the ruling is not cheap to revert, set stakes: process \| product \| architecture |
| F9 | count: `RED: {n} finding(s) — 1 document examined ({path})` (hook) / `RED: {n} finding(s) — {r} decision record(s) examined, {m} Markdown file(s) scanned, {p} record policy(ies)` (scan) | — | — |
| G1 | `GREEN: const-decision-records: 1 document examined, governed by {policy id}` / `GREEN: const-decision-records: 0 documents examined — {reason}`; this module's reasons: `const-decision-records.record_policies names no policy, so no document is known to be a decision record — to switch the check on, write const-decision-records: {record_policies: [<id of the policy that governs decision records>]} in constitution.yaml`; `{path} is not governed by a record policy ({ids})`; the shared reasons: no file in the tool's event, not Markdown, not in a git repository, no `constitution.yaml`, no `root_policy`, an `Edit` that cannot be applied / scan: `GREEN: const-decision-records: {r} decision record(s) examined, {m} Markdown file(s) scanned, {p} record policy(ies)` | — | — |
| W1 | `severity: warn`: exit 0 with one JSON object on stdout and nothing else — `additionalContext` = any notes, the `RED` lines, the count line, and `const-decision-records: severity is warn: the write proceeds, but the finding stands and recurs on every write until fixed`; `systemMessage` = `const-decision-records (warn): {headline of the first finding}` | — | — |
| N2 | note, printed before the verdict in both modes (under `warn` inside the JSON): `note: const-decision-records.record_policies names '{id}', but no policy with that id lies in the root policy's territory; it claims nothing until that policy exists` | — | — |
| N1 | the shared notes about policies: a document in the root's territory with no readable id; two policies sharing an id | — | — |
| C5 | this module's pair: `BROKEN: constitution.yaml: const-decision-records.record_policies must be a list of kebab-case policy ids — fix: write const-decision-records: {record_policies: [<id of the policy that governs decision records>]}, or remove the key`; the shared pairs: `root_policy`, `territory_dialect`, a namespace that is no mapping, this module's namespace that is no mapping, a `territory` that is no list or holds a pattern git would not read, `severity`, `log_dir` | — | — |
| C1, C14 | `BROKEN: const-decision-records needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/) — until then Markdown writes pass unchecked` (the POSIX entry point) / `BROKEN: const-decision-records needs Python 3.12 or newer, found {major}.{minor} — fix: …` (the Python entry file, whose text lives there because an old interpreter cannot import `messages.py`) | — | — |
| C2–C4b, C6–C9, C11–C13 | the shared configuration failures, each one line with its fix: a declared library missing (the install command for `requirements.txt`), git missing, the dials file not YAML or not a mapping, the root policy missing, without an id, claiming nothing, or outside its own territory, the count line `BROKEN: the check could not run — 0 documents examined`, the internal failures (git commands, hook input that is no JSON object, a bad argument, an unreadable file, an unexpected exception with its traceback after the line), a `log_dir` git does not ignore | — | — |

**Installed components reference nothing in the kit.** The skills, template, hook, scripts, error text, fixtures, and install note name no kit document; where the skills need the kernel's definitions they point at "the constitution's conventions page that the project adopted". The reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

| dial | default | read by | meaning |
|---|---|---|---|
| `severity` | `block` | gate | `block`: a finding exits 2 and the write is blocked. `warn`: the finding is reported to Claude and to the user and the write proceeds — the adoption path onto a repository with legacy records. The scan ignores it. |
| `log_dir` | absent | gate | A repository-relative directory for the output log. The gate verifies with git that the directory is ignored and reports a configuration failure otherwise. Absent: the log goes to the platform's per-plugin data directory; where that is absent too (CI), nowhere, and stdout is the record. |
| `record_policies` | `[]` | gate | The ids of the policies that govern decision records. Empty: nothing is examined and every run says so. An id with no policy behind it claims nothing and earns a note. |
| `boundary_examples` | absent | skill | The project's own routine / recorded pairs ([A3.5](../../docs/requirements.md#a3-5)): a list of `{routine: …, recorded: …}`. Absent: the skill uses the seed pairs of [§8](#t8). |
| `deciders` | absent | skill | Who may decide at each stakes level ([A3.7](../../docs/requirements.md#a3-7)): `{process: […], product: […], architecture: […]}`. Absent: the skill asks who decides. |
| `note_trailer` | absent | skill | The commit-message trailer key under which routine notes carry a theme, if the project uses one. Absent: the promotion skill reads the log only. |

The gate validates the three dials it reads at each read. The three skill-read dials are read by the agent as written; nothing validates their shape ([§9](#t9), limit 9). Territory, the root policy, and the dialect are the kernel-owned keys and the policy namespaces of [kernel §6](../../kernel/CONVENTIONS.md#k6), not dials of this module.

<a id="t8"></a>
## 8. Boundary examples

**The routine / recorded line** (this module's slice of [kernel §4](../../kernel/CONVENTIONS.md#k4)). The test behind every pair is one question — is the call cheap to revert? The pairs are the definition and are carried verbatim by the skill; the project's own arrive through `boundary_examples`:

1. Where a worktree or a scratch directory lives → routine / which kinds of document exist and what authority each carries → recorded (`process`).
2. Where in a pull-request description a review note goes → routine / whether a change may land without a review → recorded (`process`).
3. How a test stub fakes a dependency → routine / how the product treats untrusted input → recorded (`product` or `architecture`).
4. Renaming a helper nobody else calls → routine / renaming an identifier, a setting or a contract that others already depend on → recorded.

**A real choice or not** (which body shape):

5. Three mechanisms were compared and one picked → options, pros and cons, one recommendation, the choice / a schema gains the key a ruling already requires → ruling and reasoning, *not* two invented alternatives.
6. The decider overruled the recommendation → the record keeps both and says why / *not* a record rewritten so that the recommendation matches the choice.

**In place or a new record:**

7. A link form changes across every record, rulings untouched → in place, the commit names it a migration / the ruling's substance changes → a new record naming the old one.
8. A typo in a closed record → in place / a closed record's `stakes` or `decider` "corrected" after the fact → *not* in place without saying so in the commit; if the ruling's price or owner was genuinely different, that is a new record.

The field checks are deterministic and need no examples; the fixtures of [§10](#t10) are their contrastive pairs.

<a id="t9"></a>
## 9. Enforcement honesty

| artifact | kind |
|---|---|
| hook + `check-decision-record.sh` + `check-decision-record.py` (hook mode) | `gate`, severity dial `severity` (`block` default; `warn` reports and lets the write through) |
| `check-decision-record.py --scan` | `gate`, always blocking (exit 2), ignores `severity` |
| skill `record-decision` with its template | `advisory` |
| skill `promote-recurring-notes` | `advisory` |

**Honest limits**, each with its backstop:

1. **Off until named.** With `record_policies` empty the gate examines nothing. Backstop: every run prints `0 documents examined` with the line to write; a profile can prewrite the dial.
2. **A record outside record territory is invisible.** A document with `stakes` and `decider` in another policy's territory, or outside every territory, is not a record to this gate. Backstop: review; the friction signal of [§12](#t12), item 1.
3. **The rest of the envelope is not judged.** A record with a malformed `id` or `status` passes this gate. Backstop: module `const-meta-types`; alone, this module lets it through, and the install note says so.
4. **Whether a record was due is judgment.** A recorded-stakes ruling left as a commit note, a routine call recorded as `process`, a record made without the skill: no file shows any of them. Backstop: the skill's triage; review at the one yes.
5. **Body shape is not checked.** A heading check would pass manufactured options under an "Options" heading and fail a legal record that names its sections differently. Backstop: the template; review.
6. **Lifecycle is not checked.** Born-`inactive`, `active` while applied, and reversal by a new record are skill prose. An in-place edit of a closed record's ruling is indistinguishable from a typo fix by its diff. Backstop: git history and review; a protected main branch where a PR flow exists.
7. **Shell writes and other actors.** A heredoc, `sed -i`, a human's editor, a merge: none is a `Write` or `Edit`. Backstop: the scan, on demand and in CI; the skill tells the agent to run it after a shell edit.
8. **Configuration failure, timeout, and a hook that cannot start are non-blocking.** Exit 1 shows the user the first stderr line and lets the write proceed; a hook past its 30 s, or whose script path is wrong, does not block either. Backstop: the scan exits 1 with the same message, so CI turns red; the line lands in the output log.
9. **The skill-read dials are not validated.** A malformed `deciders` is read by the agent as it stands. Backstop: none deterministic; the friction signal of [§12](#t12), item 4.
10. **`Edit` is reconstructed, not observed.** The script applies `old_string` → `new_string` to the file on disk; an edit the tool itself would reject is skipped with a visible zero count.
11. **With both modules installed, an unreadable envelope is reported twice** — once by each, in different words, with the same fix. The two processes cannot see each other.
12. **Markdown means `.md`; untracked and git-ignored records are invisible to the scan; the envelope ends at the first line holding only `---`; patterns match case-sensitively on every platform; the output log is best-effort evidence; no `--help`.** The shared code's limits, the same as the first module's.

**Exit-code contract** (both modes): `0` green or nothing examined (the count line says which); `2` finding — the repository is wrong; `1` configuration failure — the checker could not run (missing or too-old interpreter, missing library, malformed dials file, missing root policy, git absent, a log directory git does not ignore, unparseable hook input, a bad argument, or an unexpected exception, whose traceback is printed). Nothing exits 0 on error. A record policy named in the dial with no policy behind it is none of these: it claims nothing, and the note says so.

<a id="t10"></a>
## 10. Acceptance

Runner: `python3 tests/run.py` (needs git, Python 3.12, the declared libraries). It builds the shared three-policy consumer in a temporary git repository, fresh for every half of every case, adds a record policy and names it in the dial, and drives the real entry point — POSIX wrapper, stdin, exit code — with real `PreToolUse` events. A red→green case fails when its red half does not exit 2, when red does not teach the expected message — all three lines, compared with what the `messages` function returns — or when its green half does not pass. A configuration-failure assertion requires exit 1 and the `BROKEN` line as the first stderr line. Items carry the numbers the runner prints; record documents are rendered through the YAML dumper, malformed ones typed on purpose.

| item | kind | what it proves |
|---|---|---|
| T1–T3 | fixture, red→green | R1: no envelope, unclosed, not YAML |
| T4–T7 | fixture, red→green | R2: wrong type, stakes outside the enum and a missing decider in one message; the free-form record — a valid envelope with neither field; a decider YAML reads as a number; a decider of blanks |
| T8 | fixture, red→green | R3: `stakes: routine` teaches the commit note |
| T9 | fixture, red→green | an `Edit` removing `decider` is blocked on the reconstructed result; an `Edit` in the body passes |
| T10–T11 | fixture, red→green | a record by declaration, path mapping absent; a record in an overlap of two territories |
| T12–T17 | fixture, assertion | what is and is not a record: the dial unset (hook and scan) prints the teaching zero; a governed non-record is a visible skip; a declaration naming the other claimant of an overlap; a dangling record policy is a note; a bad `id` and `status` pass — the rest of the envelope is not judged |
| T18–T24 | fixture, assertion | exit-code split: malformed dials file, C4b, `record_policies` not a list, an id not kebab-case, `severity`, own namespace, C6 — each exits 1, never 2, never 0 |
| T25–T29 | fixture, assertion | absence: `python3`, an interpreter below the floor (reported as not exercised, with a zero count, on a machine that has none), git, a declared library; a git that fails for another reason is a configuration failure |
| T30–T36 | fixture, assertion | input: misinvocation and `--help` exit 1, unparseable input and a `Write` event without its fields exit 1, another tool's event is a visible skip, `--scan` on a missing path exits 1, a non-Markdown file prints zero |
| T37–T38 | fixture, assertion | `severity: warn`: exit 0 with the whole finding in `additionalContext` and `systemMessage`; with a note present, stdout is still one JSON object |
| T39–T41 | fixture, assertion | scan: finding with counts and exit 2 under `warn`; green with counts, a governed non-record never examined; 300 records in seconds |
| T42–T46 | fixture, assertion | output log: seven fields per line under this module's name; `log_dir`; a `log_dir` git does not ignore (C13); rotation; a logging failure never changes the verdict |
| T47–T48 | fixture, assertion | `requirements.txt` equals the preflight table; every taught finding carries what, why, fix |
| T49 | kit check | `scripts/check-schema-mirror.py` in the kit: the mirror gives the kernel record schema's verdict on the record fields of every case |
| T50 | live | the scan over this repository (consumer zero): every kit decision record green, counts printed |
| T51 | live | the plugin loaded in a headless session in this repository via `--plugin-dir`: a record without `stakes` and `decider` blocked with R2 and the file not created; the corrected write landed; the log written; both skills reachable under the plugin's name |
| T52 | live | both modules loaded together: a record with no envelope is blocked, and a record with a bad `id` and valid record fields is blocked by the first module alone |
| T53 | review | the pairs of [§8](#t8), the skills, the template and the error texts of [§6](#t6), at the one yes; a walked example of each stakes level |
| T54 | live, deferred to the consumer's bootstrap | the consumer-live proof (decision [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) section 3): decision record number one of the consumer is written through the skill, under the gate |

Territory semantics — negation, a void namespace, a policy named like a module — are the copied `territory` and `index` modules' and are proven by the first module's fixtures; after the extraction of decision [dec-0023-shared-gate-code-at-module-two](../../docs/decisions/dec-0023-shared-gate-code-at-module-two.md) the copy-equality gate carries that proof into this module.

**Examined count.** Every exit prints it: hook mode `1 document examined, governed by …` or `0 documents examined — <reason>`; scan mode decision records, Markdown files scanned, and record policies; `BROKEN` prints `0 documents examined`.

<a id="t11"></a>
## 11. Siblings

**Depends on:** [kernel §1](../../kernel/CONVENTIONS.md#k1) (the envelope and its lifecycle rule), [§3](../../kernel/CONVENTIONS.md#k3) (territory, policy, kind, resolution), [§4](../../kernel/CONVENTIONS.md#k4) (the stakes enum and ceremony), [§5](../../kernel/CONVENTIONS.md#k5) (the decision record), [§6](../../kernel/CONVENTIONS.md#k6) (dials file, kernel-owned keys, dialect, portability), [§7](../../kernel/CONVENTIONS.md#k7) (naming). Nothing else.

**Kernel alone:** on a bare repository with no `constitution.yaml` every write passes with a visible zero count and both skills work from their seed pairs and the template; with a dials file naming a root policy, a record policy and the dial, every Markdown write into record territory is checked for the record fields and the scan runs. The record policy is the consumer's document; the module ships none.

**Optional enhancements:** when module `const-meta-types` is installed, the rest of the envelope and the resolution defects are guarded there, and a record is fully valid per the kernel's record schema only with both. When module `const-catalogs` is installed and the record policy declares a numbered kind, the skill takes the record's number from that module's allocation; this module reads no `catalog` key. When module `const-questions` is installed, a recorded-stakes answer reached in its dialog is written through this module's skill. When module `const-task-close` is installed, setting a record `inactive` at task close is its moment.

<a id="t12"></a>
## 12. Deferred

1. **Content detection** — treating any governed document with a `stakes` or `decider` key as a record. Signal: consumer commit notes about records found outside record territory.
2. **The envelope slice of immutability** — blocking a write that changes `stakes`, `decider`, `id` or `type` of a record that is `inactive` on disk, or flips it back to `active`. Deterministic, about fifteen lines, two rare false positives (a misspelt decider, a record closed too early). Signal: a consumer commit note reporting an in-place reversal.
3. **Checking `decider` against the `deciders` dial.** The matrix gives [A3.7](../../docs/requirements.md#a3-7) to review. Signal: records landing with a decider the project's list does not allow.
4. **Validating the skill-read dials.** Signal: a session misled by a malformed `boundary_examples` or `deciders`.
5. **A marker that the skill ran in the session,** to refuse a free-form record. It proves "the skill ran earlier", not "this record came from it", and is a state machine over three hook events. Signal: free-form records recurring despite the skill.
6. **A record policy declared in the policy's own namespace** rather than in this module's dial. A kernel key, admissible when a second module needs to know which policies govern records.
7. **Windows without a POSIX shell; performance past the 30 s timeout; other Markdown extensions** — the shared code's deferred items, the same as the first module's.
