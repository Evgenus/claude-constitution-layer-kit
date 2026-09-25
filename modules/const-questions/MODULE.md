---
id: module-const-questions
type: current-state
title: const-questions — ask at recorded stakes or a blocker, one decision per message in the fixed shape, and no open question left in a delivered document
status: active
---

# MODULE.md — `const-questions`

*Draft at manifest version `0.0.1`, with open slots. This document is the module's description ([template](../../module-template/MODULE.md)). Every list and table row carries a handle.*

<a id="t1"></a>
## 1. Purpose

A session asks what it should have decided, and decides what it should have asked. Observed, both poles: four questions bundled in one message, each with no options and no recommendation; a question about where a scratch file goes, blocking until answered; a request with two plausible readings answered on one of them in silence; a delivered plan carrying `TBD: who owns this` inside; and, once corrected, the inverse — every small uncertainty escalated as a fixed-price ceremony until the person asked stops reading the ceremony. In the kit's own authoring sessions the shape of one decision message took six commits in two days before it held (the kit's tree, commits 1534dd8 to f73393a), and twice the argument was written where the user never saw it. Each such correction is made in a session and lost with it; the next session asks the same way again.

<a id="t2"></a>
## 2. Failure class

`self-limiting`: the drag of a badly shaped question is felt at once by the person asked, who corrects it in the session — nothing compounds in the repository, and a delivered document with an open question inside is caught by its reader. **Entry trigger:** the same correction on how the agent asks, or fails to ask, recurs across sessions — a session-guide edit or a commit note on the question format, the threshold, a silent reading or a deferred question, made twice or more; the kit passed it with six commits on one theme in two days.

<a id="t3"></a>
## 3. Rows

| row | this module's reading |
|---|---|
| [A6.1](../../docs/requirements.md#a6-1) | The threshold is the kernel's stakes triage ([kernel §4](../../kernel/CONVENTIONS.md#k4)): a question is asked at recorded stakes — `process`, `product`, `architecture` — or at a genuine blocker, a fact the session cannot find and cannot proceed without; below it the session makes the reasonable call and notes it in the commit. The line is drawn by contrastive pairs ([§8](#t8)), the project's own arriving through a dial. A question that should not have been asked is the first defect class; a call that should have been asked is the second, and the pairs cover both. |
| [A6.2](../../docs/requirements.md#a6-2) | One decision per message, in the fixed shape the row states; the shape is carried by the skill word for word, so a session never improvises it. Simple factual clarifications — one fact, no options — are exempt from the full shape. The platform's question tool follows the message only under five options and carries the pick alone. The weighted-analysis policy for complex trade-offs is deferred ([§12](#t12)). |
| [A6.3](../../docs/requirements.md#a6-3) | Questions come from the artifact's open slots, in document order: template placeholders, `[decide: …]` markers, missing dials, unfilled matrix rows — never from free association. The skill names the slot each question answers. |
| [A6.4](../../docs/requirements.md#a6-4) | Where the slot's vocabulary is closed — a kernel enum, a dial's listed values, a policy's list — the options are exactly that set and nothing is invented beside it; free text only for a genuinely open value. |
| [A6.5](../../docs/requirements.md#a6-5) | A slot with a sensible default is asked as "default is X — accept or override?"; the answer that overrides carries a one-line reason, which the record or the commit note keeps. |
| [A6.6](../../docs/requirements.md#a6-6) | Vague or context-foreign input opens the reply with the restatement "I read this as: …"; several plausible readings are named with the one chosen; the choice is a question only above the threshold of [A6.1](../../docs/requirements.md#a6-1), otherwise the session proceeds on the stated reading. Assumptions made on the way are listed, one line each, addressable. |
| [A6.7](../../docs/requirements.md#a6-7) | A delivered plan or document holds resolved decisions only; where the decider is absent, the affected part halts behind an explicit blocker naming who must answer, never behind an open question inside the deliverable. The advisory rule is the skill's. The gate-lite ships as a `gate`: a `PreToolUse` hook on `Write` and `Edit` and a `--scan`, over the documents the dial `territories` names, reporting every line that carries a marker of the dial `markers` — claiming no more than that no marker was left; a deferred question written as prose is invisible to it ([§9](#t9)). The kit as consumer zero exempts its draft module documents and the documents that quote the marker's syntax by negated patterns (decision [dec-0041-questions-module-rulings](../../docs/decisions/dec-0041-questions-module-rulings.md), R3 and R4). |
| [A6.8](../../docs/requirements.md#a6-8) | The consumer's binding: who wants to be asked about what, and who wants a call made and noted instead. The module gives the binding two dials of its own namespace ([§7](#t7)), `preferences` and `boundary_examples`, both empty by default and read by the skill as prose; with both empty, the threshold of [A6.1](../../docs/requirements.md#a6-1) and the seed pairs of [§8](#t8) alone apply, and the skill asks who decides at the first choice at recorded stakes. |
| [A6.9](../../docs/requirements.md#a6-9) | The argument must reach the user. The skill states the fallback: once the user reports an argument missing, every later decision in that session ends the turn on the chat message and the pick is collected by letter, without the tool. A decider's standing preference for the letter path is the `pick` field of their `preferences` entry, `tool` by default; a session where the platform offers no question tool takes the letter path on its own. |

<a id="t4"></a>
## 4. Decisions

1. [dec-0041-questions-module-rulings](../../docs/decisions/dec-0041-questions-module-rulings.md) — the rulings of this module's authoring: the module authored in the kit as consumer zero of its own session conduct; the session-conduct block of the kit's guide kept until the made modules replace the kit's harness; the open-question check shipped as a `gate` with its territories and markers as dials, against the session's recommendation; its shape a hook and a scan, the standard one, with quotations in code never reported; the preferences and boundary-example dials, the `pick` field settling the fallback of [A6.9](../../docs/requirements.md#a6-9).
2. [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) — the runtime, the `severity` dial, the order of the two proofs.
3. [dec-0014-territory-dialect](../../docs/decisions/dec-0014-territory-dialect.md) and [dec-0018-dials-schema](../../docs/decisions/dec-0018-dials-schema.md) — `territories` is gitignore syntax; every read of the dials file validates the keys read.
4. [dec-0020-gate-script-rules](../../docs/decisions/dec-0020-gate-script-rules.md), [dec-0022-output-log-through-logging](../../docs/decisions/dec-0022-output-log-through-logging.md), [dec-0026-imports-at-the-top](../../docs/decisions/dec-0026-imports-at-the-top.md), [dec-0025-shared-gate-code-linked](../../docs/decisions/dec-0025-shared-gate-code-linked.md) and [dec-0038-log-record-per-print](../../docs/decisions/dec-0038-log-record-per-print.md) — the gate-script rules, the linked shared code and the output log.
5. [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md) — the mechanism choices of [§6](#t6) rest on this module's own dated comparison.

<a id="t5"></a>
## 5. Invariant

**A covered document written through the platform's file tools, and every covered document of a scanned tree, carries on no line outside code a text the `markers` dial lists.** "Covered" is the `territories` dial of [§7](#t7) over the Markdown files git lists; "outside code" is outside a fenced block and outside a code span; a marker that begins or ends with a word character counts only at a word boundary there, and the match is case-sensitive.

The advisory rules beside it, each `advisory` in its own text and carried by the skill:

- **Q-a.** A question is asked at recorded stakes or at a genuine blocker — a fact only the user holds, without which the work cannot proceed; below that line the session makes the reasonable call and notes it in the commit. The line is the pairs of [§8](#t8) and the project's own through `boundary_examples`; a decider's `preferences` entry overrides them on its topics. *Advisory.*
- **Q-b.** One decision per message, never bundled, in the fixed shape: options lettered `A`, `B`, `C`…, each a bullet with a one-sentence description and indented **Pros:** and **Cons:** sub-bullets of one prose line each, never inline and never a table; exactly one recommendation with reasoning; the decider named. A simple factual clarification is a plain one-line question. Under five options, and where the decider's `pick` is `tool`, the platform's question tool follows and carries the pick alone — letter plus short label, at most one clause; five or more options, a `pick` of `letter`, or a session where the tool is not offered: chat only, the pick by letter. *Advisory.*
- **Q-c.** Questions come from the artifact's open slots, in document order — the next unfilled template section, `[decide: …]` marker, missing dial or unresolved row — and name the slot; "while we are at it" is noted as deferred with its signal, never asked. *Advisory.*
- **Q-d.** Where the slot's vocabulary is closed the options are exactly that set; free text only for a genuinely open value, with the default proposed. *Advisory.*
- **Q-e.** A slot with a sensible default is asked as "default is X — accept or override?"; an override carries a one-line reason, kept in the record or the commit note. *Advisory.*
- **Q-f.** Vague or context-foreign input opens the reply with the reading taken; several plausible readings are named with the one chosen; the choice is a question only above Q-a's line; every assumption made is listed, one line each, addressable. *Advisory.*
- **Q-g.** A delivered plan or document holds resolved decisions only; an open decision whose decider is absent halts the affected part behind an explicit named blocker, never an open question inside the deliverable. The gate holds the marker half of this rule; the prose half is judgment. *Advisory.*
- **Q-h.** The argument must reach the user: once the user reports an argument missing, every later decision in the session ends the turn on the chat message and the pick is collected by letter, without the tool; a decider's standing `pick: letter` makes that the path from the first decision. *Advisory.*
- **Q-i.** A recorded-stakes answer is written down as argued, in a decision record with `stakes` and `decider` — through the record skill of module `const-decision-records` when installed, free-form after the kernel's shape otherwise; a routine answer is one line in the commit message. *Advisory.*

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

| component | path | carries |
|---|---|---|
| hook | `hooks/hooks.json` | One handler, exec form, explicit timeout: `PreToolUse`, matcher `Write\|Edit`, `sh` with `["${CLAUDE_PLUGIN_ROOT}/scripts/check-open-questions.sh"]` — the gate on markers, at the keystroke where a question is deferred into a document. |
| script (sh) | `scripts/check-open-questions.sh` | POSIX entry point: finds `python3`, exits 1 with the fix when it is missing, otherwise hands stdin and arguments on. Reads no YAML. |
| script (py) | `scripts/check-open-questions.py` | Thin entry point, parseable by any Python 3: the interpreter floor, the shared package, then the module's `start`. Hook mode and `--scan [DIR]`. Its docstring is the contract. |
| package | `scripts/questions_gate/` | The module's own code: `model` (the dials, a hit, the key Q1), `messages` (every text below), `dials` (the six keys, two of them the skill's, refused by name only), `checks` (fences, spans, boundaries, one hit per line), `modes` (the hook and the scan over the shared pipeline), `start` (the identity). |
| shared code | `scripts/const_gate` → the kit's `shared/const_gate/` | A relative symbolic link to what every gate shares ([kit-shared-gate-code](../../shared/GATE.md)). This gate resolves no policy: it matches its own territories with the shared matcher and builds no index. |
| dependencies | `requirements.txt` | PyYAML. |
| skill | `skills/ask-or-decide/SKILL.md` | Rules Q-a to Q-i in plain words: the threshold with the seed pairs and the two dials, derivation, enum-first, defaults, restatement, the message shape, the tool and the fallback, the named blocker, the record. Model-invocable and user-invocable, the default; no `paths`, no `context: fork`: the decision lives in the dialog that raised it. Advisory. |
| install note | `INSTALL.md` | Requirements, zero-configuration behaviour, the six dials with a worked example, adoption through `severity: warn`, the scan for CI, the output log, what the module does not check, no CLAUDE.md pointer. |
| manifest | `.claude-plugin/plugin.json` | The plugin's name, version and description — the only file inside `.claude-plugin/`; `0.0.x` marks a draft. |
| tests | `tests/run.py`; `harness.py`, `consumer.py`, `shared_items.py` linked from the kit's `shared/tests/` | The fixtures of [§10](#t10). |
| command | none | no act here is one a human deliberately types: a question arises in the dialog, and the scan is a line of CI. |
| agent | none | a question is one step of the dialog that raised it, not a delegation. |

- **Always-on content:** none printed; the skill's description stands in the skill listing, 566 characters. No `SessionStart` hook: the comparison's live runs show the description reaching the model at the moment a choice arises and not before (a5, a6 of [res-0007-const-questions](../../docs/research/res-0007-const-questions.md)), and the hooks page itself sends static context to `CLAUDE.md`.
- **Platform facts relied on** (each verified 2026-09-25 against the official documentation in its Markdown form; sources in the research comparison, sections 1, 2 and 7, and the pages named here):
  1. A `PreToolUse` command hook exiting 2 blocks the tool call and Claude sees stderr as the reason; on exit 0, JSON on stdout is parsed and `hookSpecificOutput.additionalContext` reaches Claude, `systemMessage` the user; `additionalContext`, `systemMessage` and plain stdout are capped at 10,000 characters, the overflow written to a file with a preview ([hooks](https://code.claude.com/docs/en/hooks)). Breaks: the block; the `warn` channel.
  2. All matching hooks run in parallel and the most restrictive answer applies; a plugin's copy of a handler stays separate from a settings file's ([hooks](https://code.claude.com/docs/en/hooks)). Breaks: behaviour beside sibling gates.
  3. `${CLAUDE_PLUGIN_ROOT}` is substituted in a hook's `command` and `args`; `hooks.json` uses the exec form, `command` plus `args`; only `plugin.json` lives in `.claude-plugin/`; `--plugin-dir` takes one path per flag ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). Breaks: plugin load; the hook's path.
  4. A skill's `description` stands in the skill listing in every turn and its body loads on invocation; `description` plus `when_to_use` is cut at 1,536 characters there, the listing at 1% of the context window; on compaction the most recent invocation of each skill is re-attached, its first 5,000 tokens, 25,000 shared ([skills](https://code.claude.com/docs/en/skills), [settings reference](https://code.claude.com/docs/en/settings-reference)). Breaks: the carrier; the size stated above.
  5. `AskUserQuestion` asks one to four multiple-choice questions, each `question`, `header`, `options[].label`, `multiSelect`; an option's `description` is accepted, observed on Claude Code 2.1.251 and documented on no page read; the dialog offers an `Other` row and a notes field; the dialog waits without limit by default (`askUserQuestionTimeout`, `never`); in a `-p` session the tool is offered only with a permission host, and it is denied under `dontAsk` ([hooks](https://code.claude.com/docs/en/hooks), [tools reference](https://code.claude.com/docs/en/tools-reference), [headless](https://code.claude.com/docs/en/headless), [settings reference](https://code.claude.com/docs/en/settings-reference)). Breaks: the option shape Q-b states; the letter path being the only headless one.
  6. Whether chat text written in the same turn as a tool call is shown before the dialog in the desktop app is stated on no page read and in neither changelog; the CLI on 2.1.251 showed it. The rule Q-h stands on the field observation of 2026-09-15, not on the documentation. Breaks: nothing — a platform that always shows the text makes the fallback unnecessary, never wrong.
- **Research:** [res-0007-const-questions](../../docs/research/res-0007-const-questions.md) (2026-09-25). Per row: [A6.1](../../docs/requirements.md#a6-1) to [A6.6](../../docs/requirements.md#a6-6) and [A6.9](../../docs/requirements.md#a6-9) advisory — **confirmed**, the skill alone having carried the shape in three of three live runs while the control reproduced the failure; [A6.7](../../docs/requirements.md#a6-7) advisory — **confirmed**, and its optional gate-lite, which the comparison found **not needed** at this version, shipped as a `gate` by the decider's choice (decision [dec-0041-questions-module-rulings](../../docs/decisions/dec-0041-questions-module-rulings.md), R3), as a hook and a scan rather than the scan alone the comparison recommended (R4); [A6.8](../../docs/requirements.md#a6-8) — **build**, the `preferences` and `boundary_examples` dials as the comparison shaped them.

**Error messages.** Each row is one function of this module's `messages.py`, under the same key; `{path}` is the document's repository-relative path and `{line}` a line number. A finding is `RED`, three lines (what failed / why the rule exists / the exact fix), followed by the count line. The texts every gate shares are written out once, in [kit-shared-gate-code §3](../../shared/GATE.md#g3), and are not restated here.

| key | first line | why | fix |
|---|---|---|---|
| Q1 | `RED: {path}:{line}: open question marker '{marker}' — {the line from the marker on}` — the echoed text cut at 80 characters, the cut said | a delivered document holds resolved decisions only: a marker left in it defers the question to a reader who may never see it, and a deferred question is the first thing a deliverable must not carry | `resolve the question in the text; if the decider is absent, replace the marker by a named blocker — 'blocked: <who> must decide <what>' — and halt that part; a draft whose own convention keeps markers until delivery is taken out of const-questions.territories by a negated pattern in constitution.yaml` |
| G1 | the green line's words for an examined document: `a covered document`. This module's skip reason: `{path} is not covered (const-questions.territories)` | — | — |
| F9 | the count tail of the scan: `{d} document(s) examined for {m} marker(s), {n} Markdown file(s) scanned` | — | — |
| C5 | this module's dial failures, `BROKEN: constitution.yaml: {detail} — fix: {fix}`: `const-questions.{key} is no dial of this module` — `a misspelt dial would be ignored in silence, so none is: write one of` the six keys; `const-questions.territories must be a non-empty list of path patterns` — `write the patterns of the documents to cover, one per line under "- ", or leave the key out to cover every Markdown file; an empty list would examine nothing in silence`; `const-questions.markers must be a non-empty list of non-empty texts` — `write the marker texts to look for, one per line under "- ", in single quotes, or leave the key out for the defaults '[decide:', 'TODO', 'TBD', 'FIXME'; an empty list would examine nothing in silence` | — | — |
| C12 | this module's own: `BROKEN: hook input names the event '{name}', which this gate is not wired to — fix: wire the gate to PreToolUse on Write\|Edit, as the plugin's hooks file does; to check a repository by hand run it with --scan [<dir>]` | — | — |

**Installed components reference nothing in the kit.** The skill, hook, scripts, error texts, fixtures and install note name no kit document; where the skill needs the kernel's definitions it points at "the constitution's conventions page the project adopted". The reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

| dial | default | read by | meaning |
|---|---|---|---|
| `severity` | `block` | gate, hook mode | `block`: a finding exits 2 and the write is blocked. `warn`: the finding is reported to the model and the user in one JSON object and the write proceeds — the adoption path onto a repository whose documents carry markers. The scan ignores it. |
| `log_dir` | absent | gate | As every gate's ([template §7](../../module-template/MODULE.md#t7)). |
| `territories` | `["*.md"]` | gate | The delivered documents: path patterns in the dials file's dialect over the Markdown files git lists, tracked and untracked, ignored ones excepted; a negated pattern takes files out — a template, a working draft whose own convention keeps inline markers until it is delivered. Empty: refused, since it would examine nothing in silence. |
| `markers` | `['[decide:', 'TODO', 'TBD', 'FIXME']` | gate | The texts that mark an open question, matched case-sensitively outside code; one that begins or ends with a word character counts only at a word boundary there. Empty: refused. |
| `boundary_examples` | `[]` | skill | The project's own ask / decide pairs: a list of `{ask: …, decide: …}`. Absent or empty: the seed pairs of [§8](#t8). |
| `preferences` | `[]` | skill | Per decider, what they want: a list of `{decider, ask: [<topics>], decide: [<topics>], pick: tool \| letter}` — `ask` the topics put to them even below the line, `decide` the topics decided and noted even above it, `pick` how they take a pick, `tool` when omitted. Absent or empty: the line alone, and the skill asks who decides at the first choice at recorded stakes. |

The gate validates the two dials it reads at each read, and a key of this namespace that is none of the six above is a configuration failure: a misspelt `marker:` would otherwise read as the dial unset. The two skill-read dials are refused by name only — a key that is not theirs — and read by the agent as written; nothing validates their shape ([§9](#t9), limit 4).

<a id="t8"></a>
## 8. Boundary examples

**Ask or decide** (this module's slice of the routine/recorded line of [kernel §4](../../kernel/CONVENTIONS.md#k4), aligned with the pairs of module `const-decision-records` where installed: the two modules share the triage, this one asking the question and that one writing the answer). The test behind every pair: is the call the user's to make — recorded stakes, or a fact only the user holds that the work cannot proceed without? The pairs are the definition and are carried by the skill; the project's own arrive through the preferences dial ([§7](#t7)). Each pair reads *decide and note / ask*.

1. Which of two directory names holds a scratch file → decide, one line in the commit / where the project's decision records live and how they are numbered → ask (`process`).
2. The wording of a commit message, the name of a helper nobody else calls → decide / the name of a dial, a trailer key or a command-line flag that others will type → ask.
3. A fact the session can find by reading the tree, the documents or the history → find it, never ask / a fact only the user holds — who decides, which consumer, a date — without which the work cannot proceed → ask, and if the user is absent, halt that part behind a named blocker.
4. A request with two readings that lead to the same work → proceed on the stated reading, restated first / two readings that lead to materially different work → ask: a material assumption is a question, not an assumption.

**The full shape or a plain question** ([A6.2](../../docs/requirements.md#a6-2), the exemption):

5. "The pasted file or the one in the repository?" — one fact, answered in a word → a plain question, one line / three mechanisms compared, one to be chosen → the full shape: lettered options, pros and cons, one recommendation, the decider named.
6. Every uncertainty put as a lettered ceremony — the spelling of a variable, the order of two paragraphs → *not* the shape, and not a question: decide and note / a choice that binds a policy, a procedure or a contract → the shape, every time.

**One decision per message:**

7. Two open slots, both at recorded stakes → two messages, the second put after the first is answered / two facts of one slot — a value and its unit → one message.

**Derived, not improvised** ([A6.3](../../docs/requirements.md#a6-3)–[A6.5](../../docs/requirements.md#a6-5)):

8. The next unfilled template section, the next `[decide: …]` marker, the next missing dial → the next question, in that order / "while we are at it, should we also…" → not asked; noted as a deferred item with its signal.
9. A slot whose values are a kernel enum or a dial's listed values → those values are the options, nothing beside them / a genuinely open value — a title, a path the project owns → free text, with the default proposed.
10. A slot with a sensible default → "default is X — accept or override?", the override carrying its one-line reason / a slot with no defensible default → options with one recommendation.

**Resolved, not deferred** ([A6.7](../../docs/requirements.md#a6-7)):

11. `TBD: who owns this` inside a delivered plan → *not* delivered; the part halts behind "blocked: <who> must name the owner" / a draft module document at manifest `0.0.x` carrying `[decide: …]` markers → the draft's own open slots, legitimate until publication.

<a id="t9"></a>
## 9. Enforcement honesty

| # | artifact | kind |
|---|---|---|
| E1 | `PreToolUse` hook + `check-open-questions` (hook mode): Q1 | `gate`, severity dial `severity` (`block` default; `warn` reports and lets the write through) |
| E2 | `check-open-questions --scan`: Q1 | `gate`, always exit 2 on a finding, ignores `severity` |
| E3 | skill `ask-or-decide`: Q-a to Q-i | `advisory` |

**Honest limits**, each with its backstop. The shared code's limits — [kit-shared-gate-code §4](../../shared/GATE.md#g4) — apply. This module's own:

1. **A deferred question written in prose is invisible.** "We can settle the numbering later", a heading with nothing under it, a decider named nowhere: no marker, no finding. The gate proves that nobody left a marker, and its message claims no more. Backstop: Q-g in the skill; review of the deliverable.
2. **A marker inside code is a quotation and is never reported** — a code span, a fenced block from its opener to its closer or to the end of the file. An unclosed fence therefore hides everything after it, and an indented code block is not code to this check, so a marker there is reported. Backstop: the scan lists what it examined; a fence is closed by its author.
3. **Whether a question should have been asked, and the shape of the message, are judgment.** A choice decided in silence, a bundle of four decisions, an argument written where the user never saw it: no file shows any of them. Backstop: the skill; the consumer's own pairs and preferences; the friction signal of [§12](#t12), item 4.
4. **The skill-read dials are not validated.** A malformed `preferences` entry is read by the agent as it stands; the gate refuses a key that is none of the six, which is not validating the shape of what stands under a known one. Backstop: none deterministic; [§12](#t12), item 2.
5. **A draft is a deliverable to the gate.** A document with legitimate inline slots is blocked at every write unless its path is taken out by a negated pattern or `severity` is `warn` — the cost of catching the marker at the keystroke. Backstop: the fix line names the pattern; the kit's own dials file shows the shape.
6. **One finding per line.** Two markers on one line report the first; a line fixed and re-written reports the second then. Backstop: the count line says how many lines, and the scan re-reads the whole document.
7. **Coverage is by path only.** A document a policy governs is no more covered than any other Markdown file; a file git does not list — ignored, or outside the repository — is never examined. Backstop: `territories` is the consumer's; the scan says how many files it scanned.

**Exit-code contract** (both modes): `0` green or nothing examined (the count line says which); `2` finding — the document, or the tree, carries a marker; `1` configuration failure — the checker could not run: the shared failures, this module's C5 and C12. Nothing exits 0 on error.

<a id="t10"></a>
## 10. Acceptance

Runner: `python3 tests/run.py` (needs git, Python 3.12, the declared libraries), 68 items green. It builds the shared three-policy consumer in a temporary git repository, fresh for every half of every case, and drives the real entry point — POSIX wrapper, stdin, exit code — with real `PreToolUse` events. A red→green case fails when its red half does not exit 2, when red does not teach the expected message — all three lines, compared with what the `messages` function returns — or prints any `RED` line but that finding's headline and the count line, or when green still fails. Verification kinds: `fixture` (the shared consumer in a temp repository), `live` (the kit as consumer zero, or a consumer project), `review` (the human, at the one yes).

| item | kind | what it proves |
|---|---|---|
| T1–T3 | fixture, red→green | Q1: a `TBD` in the body; a `[decide:` marker holding a `]` inside, echoed whole; a `FIXME` mid-sentence |
| T4 | fixture, red→green | an `Edit` that writes a `TODO` into an existing document is judged on the result |
| T5 | fixture, red→green | a marker in the envelope is a marker |
| T6 | fixture, assertion | quotations pass: a code span, a double-backtick span, a backtick fence, a tilde fence, an indented fence; glued words pass (`TODOs`, `TODO_LIST`); the match is case-sensitive |
| T7 | fixture, assertion | word boundaries: punctuation beside a marker keeps it a marker, a letter or a digit glued to it does not |
| T8 | fixture, assertion | an open fence masks to the end; a closer of the other character, or a shorter one, does not close it |
| T9 | fixture, assertion | one finding per line, the first marker by position; two lines give two findings in line order, counted two |
| T10 | fixture, assertion | the `markers` dial replaces the defaults; a marker made of punctuation needs no boundary |
| T11 | fixture, assertion | a document outside `territories` is a visible skip naming the dial; a README at the top is covered by the default |
| T12 | fixture, assertion | this module's C5 lines typed by hand — a key that is no dial, `territories` empty or not a list, `markers` empty, holding an empty text or a non-string — each exit 1; the skill's two dials pass unread |
| T13 | fixture, assertion | the scan: every finding in path and line order, the count tail typed by hand, exit 2 under `warn` too; the green tail typed by hand; a document outside the territories not examined |
| T14 | fixture, assertion | golden lines: Q1's headline, why and fix as literals typed by hand against a fresh run, so a why emptied or a word lost inside the message function is red; a line of 205 characters echoed cut at 80 with the cut said |
| T15 | fixture, assertion | the hooks file's shape: one `PreToolUse` handler on `Write\|Edit`, exec form, the placeholder in `args`, a timeout |
| T16 | fixture, assertion | the skill description under the listing's 1,536 characters, of the size [§6](#t6) states — counted as YAML loads it — carrying its `Use when` trigger and its `Advisory:` line; the install note names no module document; the install note's calibration example accepted as it stands, its negated pattern taking a draft out |
| T17 | fixture, assertion | an event the gate is not wired to is this module's C12, its line typed by hand |
| T18 | fixture, assertion | an `Edit` is judged on the result: one that takes every marker out passes, one that leaves another marker is blocked on that one |
| S101–S106, S111–S128, S130–S148, S150–S157 | fixture, shared | the shared acceptance items of [kit-shared-gate-code §5](../../shared/GATE.md#g5) that apply to a gate resolving no policy and judging no envelope, run through this module's entry point: the exit-code split, absence of each tool and of the shared code, invocation and input, paths and skips, `warn`, the output log, declared dependencies, a value a page long cut and said (S151, a `[decide:` line of 12,000 characters) |
| L1 | live | done 2026-09-25, Claude Code 2.1.251, in this repository (consumer zero): the scan over the kit's tree with the namespace of `constitution.yaml` calibrated — 90 documents examined for 4 markers, 96 Markdown files scanned, green; before the quotations of the marker words were put in code spans it reported eight lines, five of them quotations in prose and three the draft's own open slots, and no document needed an exemption |
| L2 | live, pending | the plugin loaded with `--plugin-dir` in a headless session in this repository: a `Write` carrying a marker blocked with Q1 and the file not created, the corrected write landed, the log written; the skill reachable under the plugin's name and invoked first on a decision prompt — to be run before the yes |
| L3 | review | the pairs of [§8](#t8), the rules Q-a to Q-i, the skill and the error texts of [§6](#t6), at the one yes |
| L4 | live, deferred | the consumer-live proof, [step 5 of the rollout plan](../../docs/rollout-plan.md#s5) (decision [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) section 3): this runner against the project, the scan wired into its CI, a write with a marker blocked in the project, and a decision put in the ruled shape from an install that carries the shared code; a finding there is a fix with a version bump |

**Examined count.** F9 in every green and red line; hook mode `1 document examined, a covered document` or `0 documents examined — <reason>`; zero is said as zero.

<a id="t11"></a>
## 11. Siblings

**Depends on:** [kernel §4](../../kernel/CONVENTIONS.md#k4) — the stakes enum, which is the threshold's vocabulary, and the standing signal of recurring commit notes; [kernel §5](../../kernel/CONVENTIONS.md#k5) — the body shape of a record, which the decision message mirrors so that a recorded answer can be written down as argued; [kernel §6](../../kernel/CONVENTIONS.md#k6) — the dials file, where the project's own pairs and preferences arrive. Nothing else.

**Kernel alone:** on a bare repository with no `constitution.yaml`, the skill carries the threshold, the message shape, the derivation order and the no-deferred-questions rule with its seed pairs; a recorded-stakes answer is written free-form after the kernel's record shape, with `stakes` and `decider` in its envelope, at the place the user names. A repository with no `constitution.yaml` is the shared visible skip naming the file, in the hook and in the scan alike.

**When module `const-decision-records` is installed,** a recorded-stakes answer is written through its record skill, which prices the stakes with the same triage and knows where records live; the two modules share the routine/recorded line, this one asking the question and that one writing the answer. **When module `const-locations` is installed,** a document the answer creates is born at its home through the command. **When module `const-catalogs` is installed,** the record's number comes from its allocation. Each is an optional enhancement; every rule here runs with the kernel alone.

<a id="t12"></a>
## 12. Deferred

1. **The weighted-analysis policy** for trade-offs too complex for the lettered shape — the matrix names it "added at first concrete need" ([A6.2](../../docs/requirements.md#a6-2)). Signal: a decision message in a consumer whose options need a scored table to be compared, reported twice.
2. **Validation of the preferences dial's shape.** The skill reads it as prose; nothing checks its shape ([§9](#t9)). Signal: a malformed entry read wrongly by the skill, reported once.
3. **A deferred question written as prose.** The scan, where it ships, sees markers; "to be agreed with the team" in a sentence is invisible to it. Signal: a delivered document found to carry such a sentence past review, twice.
4. **An always-on carrier.** The rules load with the skill when a question is about to be asked; no `SessionStart` hook prints them in every session. Signal: a session that asked in the wrong shape without ever loading the skill, observed in a consumer twice.
