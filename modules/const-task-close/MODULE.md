---
id: module-const-task-close
type: current-state
title: const-task-close
status: active
---

# MODULE.md — `const-task-close`

*Draft at manifest version `0.0.1`, no open slots; published at `0.1.0` in rollout Phase D. This document is the module's description ([template](../../module-template/MODULE.md)). Every list and table row carries a handle.*

<a id="t1"></a>
## 1. Purpose

A change lands in the code and the page that describes the code stays as it was. Nobody notices at the commit, because the page is in another file and still reads well; it is found later by a reader who follows the page into code that no longer does what it says, or by the author of the next change, who now has to work out which of the two is true. The kit observed this on itself while authoring five modules: each module's scripts and its own document, the shared gate code and its page, the git hooks and the session rules, were kept in step by hand, and its history shows the cost — nineteen of fifty accepted commits touched a module's scripts without its document, and one landed change, a linter pass over two script trees, touched no document at all and declared nothing. Beside it stands the smaller failure of the same shape inside one session: work done through the shell, a script or a subagent, left uncommitted at the end of a turn, where the chat's rewind cannot see it and a later edit cannot be rolled back to it — the kit's rule "commit before you edit" exists because that loss happened. This module makes task close a single, checkable act: a change that touches code a current-state document describes also changes that document, or says in a searchable line why not; a task's working files are deleted and its record set `inactive` at its close; and a turn never ends with a dirty tree unremarked.

<a id="t2"></a>
## 2. Failure class

**Accumulating.** Every undocumented change is one more page a reader cannot trust, and the divergence compounds silently until the page is rewritten from the code — the retrofit the kernel's defect rule exists to forbid. **Entry trigger:** the first change that touches code described by a current-state document — in practice the first commit after a project writes its first design page, so the module belongs in the day-one install set; the kit passed the trigger at its first module.

<a id="t3"></a>
## 3. Rows

| row | this module's reading |
|---|---|
| [A4.1](../../docs/requirements.md#a4-1) | Definitional; this module makes the act checkable and executable rather than restating it. "Together" means *in one change*: the unit is the commit range that lands as one — a `work/*` branch merged with `--no-ff` in the kit, a pull request elsewhere — never a single commit, since the kit's own history writes the document in the commit after the code as a matter of course. "Then task files deleted" is a step of the close skill and a note of the scan ([§5](#t5), rules T-a and T-e). |
| [A4.2](../../docs/requirements.md#a4-2) | The defect rule made detectable **as a finding of a change, never of a timestamp**: the scan is the range check with its base derived — on a branch the change since the trunk, on the trunk the last landed change — so a divergence is always attributed to the range that made it and has an author to teach and a fix to name. A comparison of last-commit dates per pair was surveyed and deferred ([§12](#t12), item 2): it compares commits, not content. "Blocking is a dial" is the shared `severity` in hook mode; the scan, as every scan, always reports. |
| [A4.3](../../docs/requirements.md#a4-3) | Advisory: the lifecycle doctrine is the kernel's ([kernel §1](../../kernel/CONVENTIONS.md#k1), [§2](../../kernel/CONVENTIONS.md#k2)) and the skills carry it in plain words (rules T-b and T-e). The stalled-drift assist — an `active` task-record whose file saw no commit in *n* days — is **deferred** with its signal and its shape ([§12](#t12), item 3): the kit's records are born `inactive`, its one active task-record is its plan, and no consumer exists to hear the alarm. |
| [A4.4](../../docs/requirements.md#a4-4) | The gate: the range check of [§6](#t6), `--scan` with `--since <ref>` or `--change <commit>`, run before a merge, on demand and in CI on a pull request. "PR check" names one place it runs, not its shape. No `PreToolUse` hook on `Bash` — it sees a command string, never a diff — and no git hook — a plugin cannot install one, and a check that reads YAML would stand in front of every commit. Per change, never per commit ([A4.1](../../docs/requirements.md#a4-1)). |
| [A4.5](../../docs/requirements.md#a4-5) | The skill `close-task`: merge the deltas into the documents the coverage map names, run the range check, delete the working files, set the record `inactive`, commit as one change. The record skill of `const-decision-records` *defines* when a record is `inactive`; this skill *performs* it at close, and works with the kernel alone, since `status` is the kernel's. "Active-without-progress flagged" is rule T-b, advisory, with the assist deferred. The leftover-files check is a **note** of the scan under the `working_files` dial, not a finding: whether a file is leftover is the closer's judgment. |
| [A4.6](../../docs/requirements.md#a4-6) | Binding, validated at each read: `coverage`, a list of named pairs of gitignore `code` patterns and exact `docs` paths; `declaration_key`, the trailer key of the no-impact declaration, `No-Doc-Impact` by default; the active-age alarm deferred with [A4.3](../../docs/requirements.md#a4-3). All in this module's own namespace ([§7](#t7)). |
| [A4.7](../../docs/requirements.md#a4-7) | The skill `commit-before-edit` carries the rule and its reason; the `Stop` hook is the gate-lite: at every turn end it runs `git status --porcelain` from the session's directory and reports a dirty tree once — under `block` the model receives the three-part message and the turn continues once; under `warn` the user sees a notice and the model nothing. The second firing of a turn always lets it end. `warn` is `systemMessage` alone: the shared warn channel's `additionalContext` continues a `Stop` up to the platform's cap, which the research showed live. |

<a id="t4"></a>
## 4. Decisions

1. [dec-0036-task-close-module-rulings](../../docs/decisions/dec-0036-task-close-module-rulings.md) — the rulings of this module's authoring: the no-impact declaration as a commit trailer *and* a pull-request body line, either satisfying the gate, the body given as text; the coverage map as named pairs in this module's own namespace; the `Stop` hook's `severity` with `block` as its default; the base of the range check from a `trunk` dial; the module authored in the kit as consumer zero ahead of its Phase C slot.
2. [dec-0032-work-starts-on-a-branch](../../docs/decisions/dec-0032-work-starts-on-a-branch.md) — what a change is in the kit: a `work/*` branch merged with `--no-ff`, whose merge is the unit the range check examines with `--change`.
3. [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) — the runtime, the `severity` dial, the order of the two live proofs.
4. [dec-0014-territory-dialect](../../docs/decisions/dec-0014-territory-dialect.md) and [dec-0018-dials-schema](../../docs/decisions/dec-0018-dials-schema.md) — a pair's `code` and the `working_files` are gitignore patterns matched by `git check-ignore`; every read of the dials file validates the keys read.
5. [dec-0020-gate-script-rules](../../docs/decisions/dec-0020-gate-script-rules.md), [dec-0022-output-log-through-logging](../../docs/decisions/dec-0022-output-log-through-logging.md), [dec-0025-shared-gate-code-linked](../../docs/decisions/dec-0025-shared-gate-code-linked.md) and [dec-0026-imports-at-the-top](../../docs/decisions/dec-0026-imports-at-the-top.md) — the gate-script rules and the linked shared code; this module is its sixth consumer, the first wired to an event that names no file.
6. [dec-0006-accumulating-set-first](../../docs/decisions/dec-0006-accumulating-set-first.md) — the kit as consumer zero; the reorder that brings this module here is item 4 of the first record above.
7. [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md) — the mechanism choices of [§6](#t6) rest on this module's own dated comparison.

<a id="t5"></a>
## 5. Invariant

**In an examined range, every coverage pair whose code the range touches is either updated — one of the pair's documents is among the range's paths — or declared, by a no-impact line naming the pair in a commit of the range or in the body given to the check; and at the end of a turn in a session that loads the plugin, a dirty working tree is reported once before the turn ends.** "Range", "pair", "declared" and "dirty" are this module's definitions ([§6](#t6), [§7](#t7)); task close, the defect rule and the lifecycle are the kernel's ([kernel §1](../../kernel/CONVENTIONS.md#k1), [§2](../../kernel/CONVENTIONS.md#k2)); "examined" and "a session that loads the plugin" are the honest boundaries of [§9](#t9).

The advisory rules beside it, each `advisory` in its own text: (T-a) close a task as one act — merge the deltas into the documents the map names, run the range check, delete the working files, set the record `inactive`, commit as one change whose message names the close; (T-b) an active task-record whose scope sees no commits is stalled drift: commit it back or roll it back, never leave the halfway state as truth; (T-c) commit a dirty tree before a batch of edits, commit again after each coherent change, never end a turn dirty — git is the rollback layer, the chat's rewind is not; (T-d) a no-impact declaration is a judgment written for the reviewer: name the pair and say why its documents stand, and never declare what an update would have fixed; (T-e) a task's working files are deleted at its close and git remembers them; a file kept is kept with a reason.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

| component | path | carries |
|---|---|---|
| hook | `hooks/hooks.json` | One handler, exec form, explicit timeout. `Stop`, no matcher — the event has none: `sh` with `["${CLAUDE_PLUGIN_ROOT}/scripts/check-task-close.sh"]` — the turn-end check, the gate-lite. Step down from a platform component: no native option reads the working tree; the platform's own guide names a `Stop` hook that "scans the working tree once per turn" as the remedy for edits made through the shell. |
| script (sh) | `scripts/check-task-close.sh` | POSIX entry point: find `python3`, exit 1 with the fix when it is missing, otherwise hand stdin and arguments on. Reads no YAML. |
| script (py) | `scripts/check-task-close.py` | Thin entry point, parseable by any Python 3: the interpreter floor, the shared package, then the module's `start`. Hook mode (`Stop`) and `--scan [DIR] [--since <ref> \| --change <commit>] [--body <file>]`. Its docstring is the contract. |
| package | `scripts/task_close_gate/` | The module's own code: `model`, `messages`, `dials` (`coverage`, `trunk`, `declaration_key`, `working_files`), `history` (the one place git is asked about a range — the base, the paths, the messages' trailers — and about the working tree), `checks` (the range against the map, the declarations against the pairs, the tree), `modes` (hook, scan), `start`. Step down to a repository script: no platform component diffs a range or reads a trailer; git does both, and the module owns the questions. `mypy --strict` clean. |
| shared code | `scripts/const_gate` → the kit's `shared/const_gate/` | A relative symbolic link to what every gate shares ([kit-shared-gate-code](../../shared/GATE.md)). This gate reads only its own dials, resolves no policy and builds no index; it matches the pairs' `code` and the `working_files` with the shared matcher. |
| dependencies | `requirements.txt` | PyYAML. |
| skill | `skills/close-task/SKILL.md` | Rules T-a, T-b, T-d and T-e: the close sequence, the range check and how to read its verdict, the declaration's form and when it is honest, the working files, the record's status at close. Model-invocable. Advisory. |
| skill | `skills/commit-before-edit/SKILL.md` | Rule T-c: commit before a batch of edits, after each coherent change, never end a turn dirty; the reason; the commands; what the turn-end hook does. Model-invocable. Advisory. |
| install note | `INSTALL.md` | Requirements, the hook's behaviour under both severities, the map with a worked example, the declaration's two forms and the trailer paragraph's rule, the scan for CI with the base from the pull request's event, adoption through `warn`, what the module does not check, no CLAUDE.md pointer. |
| tests | `tests/run.py`; `harness.py`, `consumer.py`, `shared_items.py` linked from the kit's `shared/tests/` | The fixtures of [§10](#t10). |
| command | none | closing a task is asked for in words, and the skill carries it; the scan is a command line, not a slash command. |
| agent | none | a close is one step of the dialog that did the work, not a delegation. |

- **Always-on content:** none printed; the two skills' descriptions stand in the skill listing, 502 and 367 characters. No `SessionStart` hook: the rule of T-c reaches the model through the hook's message at the first dirty turn end, and the close rule through the skill when a task ends.
- **Platform facts relied on** (all verified 2026-09-23 against the official documentation; sources and experiments in the research comparison, sections 1, 2 and 9):
  1. A `Stop` hook fires when the main agent finishes responding, not on a user interrupt; its payload carries `session_id`, `cwd`, `hook_event_name`, `stop_hook_active` and `last_assistant_message`, and names no file; `cwd` is the session's directory. Breaks: where the tree is looked for; the loop guard.
  2. A `Stop` hook exiting 2 continues the conversation with its stderr as the model's instruction; `stop_hook_active` is `true` on every firing after the first of a turn; the platform ends the turn after eight consecutive blocks. Observed 2026-09-23 on Claude Code 2.1.251: the model read the message and committed. Breaks: `block`.
  3. On exit 0 a `systemMessage` is shown to the user and the model sees nothing; `hookSpecificOutput.additionalContext` on `Stop` continues the conversation through the same loop protections as a block. Observed: nine firings under the shared warn channel, one under `systemMessage` alone. Breaks: `warn`.
  4. `Stop` has no matcher and the handler's `if` field never runs off tool events; `SessionEnd` has no decision control and discards `systemMessage`. Breaks: nothing — neither is used.
  5. Exit 1 is a non-blocking error whose first stderr line the user sees; the default timeout is 600 s; `args` is set whenever the command carries a path placeholder. Breaks: the exit-code split; rule 11's wiring.
  6. Git: a trailer paragraph is the message's last, separated by a blank line, every line `Key: value`; one line without a colon makes git read no trailer in it; `%(trailers:key=…,valueonly)` returns every value of a repeated key, matched case-insensitively; a merge made with `-m` carries none, so the kit's declarations stand on the branch's commits; `A...B` diffs from the merge-base; a shallow clone cannot name the history it lacks. Breaks: the declaration's reader; the range.
  7. GitHub: a pull request's body and its base commit are in the workflow's event payload; a squash merge keeps a commit's trailer only when that message lands last. Breaks: the body's route into `--body`; a squashing consumer's declarations.
  8. Cost on the kit's tree: `git status --porcelain` 24 ms, the range's paths 22 ms, the trailers 21 ms, the interpreter's start about 52 ms. Breaks: nothing under the hook's 30 s.
- **Research:** [res-0006-const-task-close](../../docs/research/res-0006-const-task-close.md) (2026-09-23). Per row: [A4.1](../../docs/requirements.md#a4-1) definitional — **confirmed**, the unit being the change. [A4.2](../../docs/requirements.md#a4-2) gate as flag — **confirmed**, the flag a finding of a change, the timestamp heuristic deferred. [A4.3](../../docs/requirements.md#a4-3) advisory — **confirmed**, the assist deferred. [A4.4](../../docs/requirements.md#a4-4) gate — **confirmed**, built as a range check rather than a forge-bound check. [A4.5](../../docs/requirements.md#a4-5) advisory with a scriptable leftover check — **confirmed**, the check a note of the scan. [A4.6](../../docs/requirements.md#a4-6) binding — **confirmed**; the declaration's mechanism decided as both forms, the comparison having recommended the trailer alone. [A4.7](../../docs/requirements.md#a4-7) gate-lite — **confirmed** in shape, its warn channel corrected to `systemMessage` alone, and its default **overturned** from warn to `block` by the decider, since a block is now known to let go after one continuation.

**Gate-script rules** ([template §6](../../module-template/MODULE.md#t6)): every Python script here follows all sixteen; the entry file, the package, the messages module, the one exit, the preflight, the declared dependency, the typed model, the docstring contract, the exec-form wiring, the output log, the fixtures from 1 and the shared items from 101, the absence fixtures, and the imports at the top with the two marked exceptions of the shared interface. The kit's tooling holds them: `ruff` and `mypy --strict` from `pyproject.toml`.

**Error messages.** Each row is one function of this module's `messages.py`, under the same key. Findings are `RED`, three lines each (what failed / why the rule exists / the exact fix), followed by the count line. The texts every gate shares are written out once, in [kit-shared-gate-code §3](../../shared/GATE.md#g3), with `{module}` standing for `const-task-close`; `{key}` is the `declaration_key` dial, `{pair}` a pair's name, `{where}` `commit {short hash}` or `the body`.

| key | first line | why | fix |
|---|---|---|---|
| T1 | hook: `RED: the working tree is dirty at turn end — {n} path(s): {up to five lines of git status --porcelain, then …}` | `rollback points live in git, not in the chat's rewind, which does not see edits made through the shell, a script or a subagent — work not committed did not happen` | `commit what is finished: git add -A && git commit -m '<what changed and why>' — stash or discard what is not; this is asked once per turn, and the rule is the skill commit-before-edit` |
| T2 | scan: `RED: {pair}: the change touches {n} path(s) this pair describes ({up to three paths, then …}) and none of its document(s): {docs}` | `task close is a single act: code and the current-state documents that describe it change together, or the change says why the documents stand` | `update {docs} in this change, or declare no impact: add the trailer "{key}: {pair} — <why the documents are unaffected>" to a commit of the range, in its last paragraph, where every line is Key: value — or the same line on its own in the pull request's description, given to the scan with --body <file>` |
| T3 | scan: `RED: {where}: "{key}: {value}" names no pair of the coverage map (pairs: {names})` | `a declaration must name what it declares unaffected, or it declares nothing` | `name one of the pairs before the dash, or remove the line` |
| T4 | scan: `RED: {where}: "{key}: {pair}" carries no reason` | `a declaration is a judgment; the reason is what a reviewer reads` | `write it as {key}: {pair} — <why the documents are unaffected>` |
| N1 | scan notes, stdout, before the verdict: `note: {pair}: no impact declared in {where}: {reason}`; and, for a declaration of a pair the change does not touch, `note: {pair}: no impact declared in {where}, and the change touches nothing this pair describes` | — | — |
| N2 | scan note: `note: {n} tracked file(s) match working_files ({up to three, then …}) — a task's working files are deleted at its close; keep one only with a reason` | — | — |
| G1 | hook, clean: `GREEN: {module}: the working tree examined, clean`; hook, second firing of a turn: `GREEN: {module}: the working tree examined — {n} path(s) dirty, reported at this turn's first stop; the turn ends`; hook, no repository: the shared `G1.3` with the event's `cwd`; no dials file: the shared `G1.4`. Scan: the shared form with the tail of F9 | — | — |
| F9 | hook count: `RED: 1 finding — the working tree examined ({n} path(s) dirty)`. Scan tail: `{p} pair(s) examined over {c} commit(s), {base}..{tip}` — short hashes; with an empty map `0 pair(s) examined — coverage is empty`; on a trunk whose tip has no parent `{p} pair(s) examined over 0 commit(s) — nothing landed before {tip}` | — | — |
| X1 | `BROKEN: constitution.yaml: {module}.coverage[{pair}] names the document {path}, which does not exist at HEAD ({short hash}) — fix: correct the path, or create the document; a pair whose document is gone describes nothing` — the map describes the tree as it is, so existence is asked of HEAD, and an older change is judged by today's map; a path the range itself deletes or renames is touched, not missing | — | — |
| C5 | this module's dial failures, `BROKEN: constitution.yaml: {detail} — fix: {fix}`: `{module}.{k} is no dial of this module` — `a misspelt dial would be ignored in silence, so none is: write one of severity, log_dir, coverage, trunk, declaration_key, working_files`; `{module}.coverage must be a list of pairs` — `write it as coverage: [{name: <kebab>, code: [<patterns>], docs: [<paths>]}]`; `{module}.coverage[{n}] {detail}` with detail one of `is not a mapping`, `carries the key '{k}', which no pair has (name, code, docs)`, `has no name, or one that is not kebab-case`, `repeats the name '{name}'`, `has no code, or code is not a non-empty list of patterns`, `has no docs, or docs is not a non-empty list of repository-relative paths` — `write the pair as {name: <kebab>, code: [<gitignore patterns of the code it describes>], docs: [<paths of the documents that describe it>]}`; `{module}.trunk must be a non-empty string` — `set trunk: <the branch changes land on>, or remove the line for main`; `{module}.declaration_key must be a trailer key: letters, digits and hyphens` — `set declaration_key: No-Doc-Impact, or remove the line`; `{module}.working_files must be a list of patterns` — `write it as working_files: [<gitignore patterns>], or remove the line`. A pattern git would misread, in a pair's `code` or in `working_files`, is the shared `C5.7` under `{module}.coverage[{pair}].code` or `{module}.working_files` | — | — |
| C12 | this module's own configuration failures, each `BROKEN: {what} — fix: {fix}`: `hook input names the event '{name}', which this gate is not wired to` — `wire the gate to Stop, as the plugin's hooks file does; to check a change by hand run it with --scan [<dir>] [--since <ref> \| --change <commit>] [--body <file>]`; `{flag} names '{ref}', which git cannot resolve in {root}: {git's first line}` — `name a commit, branch or tag this repository has; a shallow clone may need its history fetched (git fetch --unshallow)`; `the trunk '{trunk}' is neither a local branch nor origin/{trunk} in {root}` — `set {module}.trunk to the branch changes land on, or run the scan with --since <ref>`; `--since and --change exclude each other` — `give one: --since <ref> examines the changes since that base, --change <commit> examines one landed change`; `--body names {path}, which cannot be read ({error})` — `give the pull request's description as a readable file`; `git could not read the range {base}..{tip} in {root}: {git's first line}` — `repair what git names in the message; a shallow clone may need its history fetched (git fetch --unshallow)`. A module flag given without `--scan` is the shared `C12.9`, whose usage line is this module's | — | — |

**Installed components reference nothing in the kit.** The skills, hook, scripts, error texts, fixtures and install note name no kit document; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

| dial | default | read by | meaning |
|---|---|---|---|
| `severity` | `block` | hook | How loud a dirty tree at turn end is. `block`: exit 2 on the turn's first stop — the model receives T1 and the turn continues once; `warn`: exit 0 with T1 in a `systemMessage`, shown to the user, unseen by the model. The second stop of a turn is exit 0 under both. The scan ignores it. |
| `log_dir` | absent | hook, scan | As every gate's ([template §7](../../module-template/MODULE.md#t7)). |
| `coverage` | `[]` | scan | The map: a list of pairs `{name, code, docs}` — a kebab-case name, unique in the list; `code`, gitignore patterns of the code the documents describe, matched against the range's paths whether or not they still exist; `docs`, repository-relative paths of the current-state documents, each existing at HEAD unless the range itself deleted or renamed it. A `docs` path that also matches the pair's `code` is left out of the pair's code side. Pairs may overlap; order carries no meaning. Empty: zero pairs examined, said so. |
| `trunk` | `main` | scan | The branch changes land on: the base of a scan given neither `--since` nor `--change` is the merge-base of the trunk and the head, the trunk found as a local branch or as `origin/<trunk>`; a head that *is* the trunk examines its last landed change, as `--change HEAD` would. |
| `declaration_key` | `No-Doc-Impact` | scan | The trailer key of the no-impact declaration, matched case-insensitively as git matches it; the same line is read from a `--body` file. |
| `working_files` | `[]` | scan | Gitignore patterns of a task's working files; a tracked file that matches earns note N2. Empty: no note. |

The gate validates every key it reads at each read, and a key of this namespace that is none of the six above is a configuration failure: a misspelt `coverage:` would otherwise be an empty map in silence.

<a id="t8"></a>
## 8. Boundary examples

The range check and the tree check are deterministic; the fixtures are their pairs. The judgment is the skills'.

**Declare, or update (T-d):**

1. A gate's message text changes → its module document's error-message table is updated / *not* declared: the document states the text.
2. A comment reworded in a script, no behaviour changed → `No-Doc-Impact: <pair> — comments only, no rule or message changed` / *not* an edit to the document to make the gate green.
3. A dial's default changes → the document's dial table / *not* `No-Doc-Impact: … — small change`.
4. A file moved inside the code territory, the document naming it by path → the document / *not* a declaration: the path in the page is now wrong.
4a. A formatter pass over a script tree → a declaration naming the pass / *not* silence: the change is real and the reviewer should see it was judged.

**What is a working file (T-e):**

5. A scratch script written to try a fixture → deleted at close / *not* kept "in case".
6. A note that became the record's reasoning → the record / *not* the note beside it.
7. A fixture the gate runs → code, not a working file / *not* deleted because it was written during the task.

**Stalled or paused (T-b):**

8. A task-record `active` for a month, its files untouched, its author gone → commit back what is real and set it `inactive`, or roll it back / *not* left as the write-head.
9. A plan whose next step waits on a decision named as the blocker → paused, the blocker written in the record / *not* rolled back.

**Commit before you edit (T-c):**

10. A batch of edits is about to start on a dirty tree → commit first, then edit / *not* "the rewind will cover it": it covers nothing done through the shell.
11. A turn ends with one coherent change done → commit / *not* "next turn".
12. A turn ends mid-change, a test still red → commit as work in progress, the message saying so / *not* a clean-looking silence; or stash, and say so.
13. The hook blocks a turn that was a question with no edits → impossible: a clean tree is silent; a dirty one was left by earlier work, and that is what it names.

<a id="t9"></a>
## 9. Enforcement honesty

| # | artifact | kind |
|---|---|---|
| E1 | `Stop` hook + `check-task-close` (hook mode): T1 | `gate`, severity dial `severity` — deterministic; under `block` red means commit, and the turn continues once |
| E2 | `check-task-close --scan`: T2–T4, with notes N1–N2 | `gate`, always exit 2 on a finding, ignores `severity` |
| E3 | skills `close-task`, `commit-before-edit` | `advisory` |

**Honest limits**, each with its backstop. The shared code's limits — [kit-shared-gate-code §4](../../shared/GATE.md#g4) — apply, shared limit 1 in its own way: a commit made through the shell is exactly what the scan examines. This module's own:

1. **A block on `Stop` is a request the model weighs, not a wall.** The model may refuse, as it did in the research when its prompt told it not to commit; the second firing lets the turn end either way, and a committed tree can carry a poor message. Backstop: the message teaches the commit's shape; the user sees the notice; the scan judges the commits.
2. **The hook does not fire on a user interrupt,** nor in a session that has not loaded the plugin, nor for a subagent's own stop. Backstop: the scan; the session rule in the consumer's own instructions.
3. **A declaration's truth is review.** The gate holds its presence, shape and target, never whether the documents really stand. Backstop: N1 prints every declaration used, so the reviewer reads each; rule T-d.
4. **The unit is the change.** A commit inside the range may touch code without its document, and the range is green when a later commit of the same range updates it — by design; and a change merged by hand into the trunk without the scan is examined only by the next scan of the trunk. Backstop: the scan on the trunk, `--change HEAD`, in CI.
5. **Git's trailer rules are unforgiving:** one colon-less line in a message's last paragraph hides every trailer there, and a squash merge keeps a trailer only when its message lands last. Backstop: T2's fix states the paragraph's rule; the body line is the second form.
6. **The body is trusted text.** Whatever file `--body` names is read as the description; nothing checks that it came from the forge. Backstop: CI writes it from the event payload; a local run has no body and reads the trailers.
7. **A shallow clone cannot see the range.** Backstop: the configuration failure names the fetch.
8. **The map covers what it lists.** Code no pair names is never a finding, and a document no pair names is never asked to move. Backstop: the map grows with the project; N2 and the close skill.
9. **Dirty means what `git status --porcelain` lists** — tracked changes and untracked files git does not ignore; an ignored scratch directory is invisible, which is where working files should live until close. Backstop: `working_files` for tracked ones.
10. **The scan compares commits,** so an update sitting uncommitted in the working tree does not count. Backstop: the hook; T2's fix says "in this change".

**Exit-code contract**: `0` green, or nothing to examine (the count line says so); `2` a finding; `1` configuration failure: the shared ones, X1, C5, C12. Nothing exits 0 on error.

<a id="t10"></a>
## 10. Acceptance

Runner: `python3 tests/run.py` (needs git, Python 3.12 and the declared library). It builds the shared consumer in a temporary git repository, fresh for every half of every case, and drives the real entry points — POSIX wrapper, stdin, exit codes — with real `Stop` payloads and with `--scan` over commits it makes. A red→green case fails when its red half does not exit 2, when red does not teach the expected message — all three lines — or when its green half does not pass. The shared harness's case record drives one tool event, so this module's cases carry both halves inside one assertion item each, named red→green in its title, as the fourth module's scan cases do. Texts are also typed by hand as literals, since a case that compares with what a message function returns cannot catch a wrong text. Every group is probed with mutants on a copy made with links followed before the second validation.

| item | kind | what it proves |
|---|---|---|
| 1–4 | fixture, red→green | **the specification's four:** a code-touching change without a document update or a declaration is red (T2), with the update green, with a trailer green; a dirty tree at turn end is red (T1) and a clean tree silent |
| 5–9, 35 | fixture, assertion | the hook: `stop_hook_active` lets the turn end with the second-firing line; `warn` is a `systemMessage` alone, no `additionalContext`; an untracked file is dirty, an ignored one is not, a modified tracked one is; a `cwd` below the root finds the repository (a `cwd` outside any repository is the shared skip); a tool event is C12; the hook validates the dials too (35) |
| 10–16 | fixture, assertion | the scan: the base from `trunk` on a branch, and an unknown trunk; `--since`; `--change` on a merge — its first-parent diff, the merge itself counted among the commits — and on a plain commit; the head on the trunk examines the last landed change, a merged branch an empty range; a root commit on the trunk, and a repository with no commit, examine nothing and say so; `--since` and `--change` together; an unknown ref |
| 17–22 | fixture, assertion | declarations: the trailer read among `Co-Authored-By`; a repeated key; a colon-less line hiding the paragraph (red, the fix teaching the rule); the body line; a declaration naming no pair (T3); one without a reason (T4); N1 for a used and for an untouched pair; the key matched case-insensitively; `declaration_key` changed |
| 23–27 | fixture, assertion | the map: overlapping pairs both apply; a `docs` path inside `code` is not its own trigger; a deleted and a renamed path count as touched; a missing document is X1, a deleted one is not, and an older change is judged by today's map without X1; an empty map is zero pairs examined |
| 28–31 | fixture, assertion | dial failures, exit 1, one per C5 text; a pattern git would misread; `working_files` and N2; a misspelt dial |
| 32–34 | fixture, assertion | golden lines of T1–T4, X1 and the count forms, typed by hand; the hooks file's shape; the skill descriptions' sizes |
| 101– | fixture, shared | the shared acceptance items that apply to a gate that resolves no policy, judges no envelope and is driven by `Stop`: the exit-code split, absence, invocation and input, the log, the declared library, the install copy, not fail-open, the scan's forms |
| L1 | live | **in this repository:** the kit's own map declared in its `constitution.yaml`; `--change` of the locations merge green — code and document in one range; `--change` of the tooling merge red with three findings under the kit's nine pairs, the one landed change the research found undocumented; a scratch commit on a branch touching the shared code without its page red, then green with a trailer |
| L2 | live | **headless, Claude Code 2.1.251,** the plugin loaded with `--plugin-dir` in a scratch repository: a dirty tree at turn end blocked once, the model committing on the message; a clean tree silent; `warn` shown as a notice |
| L3 | review | the designed texts of [§6](#t6), the skills, the install note, at the one yes |

**Examined count.** F9 in every green and red line; zero is said as zero.

<a id="t11"></a>
## 11. Siblings

**Depends on:** [kernel §1](../../kernel/CONVENTIONS.md#k1) (the lifecycle rule; `status`), [§2](../../kernel/CONVENTIONS.md#k2) (task close as a single act, the defect rule, stalled drift), [§6](../../kernel/CONVENTIONS.md#k6) (the dials file, the dialect, portability). Nothing else. **Kernel alone:** on a bare repository with no `constitution.yaml` the hook is a visible skip and the scan too; with an empty dials file the hook judges the tree and the scan examines zero pairs and says so; with a map, the scan judges every change. No policy is read, no envelope is judged: a task-record's `status` is set by the skill, in words.

- When module `const-decision-records` is installed, its record skill defines when a record is `inactive` and this module's close skill performs it at close; neither reads the other's dial.
- When module `const-locations` is installed, a document a pair names that does not exist yet is created through its command, at the home its policy implies.
- When module `const-referencing` is installed, its scan runs beside this one before a merge, and the two verdicts are read together.
- When module `const-meta-types` is installed, the documents the map names carry valid envelopes; this module never reads one.

<a id="t12"></a>
## 12. Deferred

1. **The pull-request body read from the forge** by the module itself, through a client and the network. Today the body is text given with `--body`. Signal: a consumer whose closers cannot get the body into a file.
2. **Drift by timestamp** — the newest commit of a pair's code newer than the newest of its documents with no declaration since. It compares commits, not content, resets on a typo fix, and blames nobody. Signal: a consumer commit note reporting drift no range had shown.
3. **The active-age assist** of [A4.3](../../docs/requirements.md#a4-3): a note of the scan, `<record> is active and its file saw no commit in <n> days`, its scope the commits touching the record's file, under a dial `active_age_days` absent by default, skipped in a shallow clone. Signal: a consumer commit note about a task-record left active, or a stretch of the kit's own plan with no commits.
4. **`--history <n>`**, auditing the last *n* landed changes of the trunk in one run. Signal: a consumer adopting the module over a history it wants judged.
5. **A pair with no documents,** meaning "this code is described nowhere and every change to it is a finding". Signal: a consumer asking for the sharper form.
6. **`SubagentStop`.** Signal: subagents leaving dirty trees the main agent's turn end does not reach.
7. **Per-commit strictness as a dial.** The kit's history rejected it; a consumer with one-commit changes may want it. Signal: that consumer.

---

# Plugin skeleton

```
const-task-close/
├── .claude-plugin/
│   └── plugin.json
├── MODULE.md
├── INSTALL.md
├── requirements.txt
├── hooks/hooks.json                 # Stop
├── skills/
│   ├── close-task/SKILL.md
│   └── commit-before-edit/SKILL.md
├── scripts/
│   ├── check-task-close.sh
│   ├── check-task-close.py
│   ├── const_gate -> ../../../shared/const_gate
│   └── task_close_gate/             # model, messages, dials, history, checks, modes, start
└── tests/                           # run.py; harness.py, consumer.py, shared_items.py linked from shared/tests/
```
