---
id: module-const-questions
type: current-state
title: const-questions — <one clause saying what the module guards or does>
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

Provenance of this module's rules: the records whose rulings it applies, each cited by its record id while the record exists. When a record is deleted its entry goes with it and nothing replaces it; a ruling below recorded stakes has no entry. The rule itself is stated in the section where it acts ([§5](#t5)–[§9](#t9)); a record is cited for where and why it was decided, never in place of the rule ([kernel §5](../../kernel/CONVENTIONS.md#k5)). The record holds the options and reasoning, which are not restated here.

1. `<record-id>` — one line naming what it fixes here.

<a id="t5"></a>
## 5. Invariant

The one rule the module guarantees, stated in a single testable sentence built only from kernel vocabulary and this module's own definitions. An advisory-only module claims no invariant; in its place stands the numbered rule list, each rule labeled `advisory` in its own text.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

What this plugin ships and what each part carries — only components the module actually uses exist. Native-first: platform component > repo script > third-party tool > new infrastructure; every step down from a platform component names, in one clause, what the native option cannot do.

| component | path | carries |
|---|---|---|
| skill | `skills/<name>/SKILL.md` | the procedure, loaded when the activity occurs |
| hook | `hooks/hooks.json` + `scripts/` | deterministic enforcement of the invariant; or, as a `SessionStart` hook printing rules to stdout, the always-on carrier for advisory content — declared `advisory`, never `gate` |
| command | `commands/<name>.md` | only for acts a human deliberately initiates — name the scenario where a human actually types it, or delete this row |
| agent | `agents/<name>.md` | only for a genuine delegation boundary |
| script | `scripts/<name>` | checks and generators; all paths via `${CLAUDE_PLUGIN_ROOT}`; Python 3 with PyYAML when the script reads YAML, POSIX shell otherwise; a missing runtime or library is a configuration failure ([§9](#t9)); Python scripts follow the gate-script rules below |
| install note | `INSTALL.md` | at most one pointer line for the project's own `CLAUDE.md`, for discoverability only. Always-on rules ship via a `SessionStart` hook (see hook row), never via a pointer or a plugin-root `CLAUDE.md` (not loaded); a copy-into-CLAUDE.md fallback may be offered, labeled as manual and version-drifting |

Three fixed sub-slots follow the table:

- **Always-on content:** the exact lines the `SessionStart` hook prints and their size in characters; or "none". This is the module's whole always-on budget.
- **Platform facts relied on:** each fact, the date it was verified against the official documentation, and what breaks if it changes. Nothing in this slot comes from memory.
- **Research:** a link to this module's own dated comparison in `docs/research/` — written at authoring, in kit vocabulary, from a survey of the official documentation, community harnesses, and applicable tools for exactly this module's rows — and, per row, whether the matrix's recommended enforcement was confirmed or overturned by it (decision [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md)). Nothing from earlier design work enters unverified.

**Gate-script rules** (decision [dec-0020-gate-script-rules](../../docs/decisions/dec-0020-gate-script-rules.md)) — every Python script a module ships follows all sixteen; the fresh-context validation checks them:

1. **Shape.** The entry point is a thin file. Past about 300 lines of logic, or with a second entry point, the code is a package directory beside it, imported with no path manipulation — Python puts the script's directory on the import path. What every gate shares is not written again: `scripts/const_gate` is a relative symbolic link to the kit's one source, the module fills the interface of [kit-shared-gate-code §2](../../shared/GATE.md#g2), and the entry file turns a missing shared package into its designed configuration failure (decision [dec-0025-shared-gate-code-linked](../../docs/decisions/dec-0025-shared-gate-code-linked.md)). Never a sibling-script import and never a `sys.path` edit in gate code; the fixture runner alone puts the module's `scripts/` directory on the path, and says so. Package and module names are snake_case because the language requires identifiers; entry-point files stay kebab-case.
2. **Messages.** One messages module per package: the shared package's, and the module's own for its findings, skip reasons, notes and dial failures. Each message is a function with typed parameters returning its three parts — what failed, why the rule exists, the exact fix — under the key it carries in this section's error-message table.
3. **One exit.** `main(argv) -> int`, a single `sys.exit`, and one guard that maps the configuration exception to exit 1. The entry file's exits before any package can be imported — the interpreter floor, the missing shared package — are the only others, each printing its designed line and the count line; a generator's entry file prints its own closing line in the count line's place, and its variants of those lines drop the clause about unchecked writes.
4. **Exit codes.** Named constants: 0 green, 2 finding, 1 configuration failure. Parameters are parsed with `argparse`, whose exit-2 default on bad usage is overridden to 1.
5. **Separation.** Parsing, checking, and reporting are separate functions; a check is a function of typed inputs.
6. **Runtime.** Plain `python3` through the POSIX entry point, never `uv run`. Floor: Python 3.12. The interpreter version and every declared library are preflighted on each invocation, before any verdict is printed.
7. **Dependencies.** Unrestricted, but declared in `requirements.txt` at the plugin root; the configuration-failure message prints the one install command for that file. `yaml.safe_load` only.
8. **No fail-open.** An unexpected exception exits 1 with its traceback; unparseable hook input is a configuration failure; nothing exits 0 on error. An advisory script may fail open and says so in its docstring.
9. **Types.** Every parameter and return is annotated. Untyped data — JSON, YAML — is parsed once into dataclasses; no bare `dict`, `list` or `Any` crosses a function boundary; closed vocabularies are enums. `mypy --strict` is clean.
10. **Docstring contract.** The entry point's docstring states the hook events, the modes, the input fields read, the exit codes, the output channels, and the dial keys read.
11. **Hook wiring.** `hooks.json` uses the exec form (`command` plus `args`) wherever a path placeholder appears, with an explicit `timeout`.
12. **Output log.** Everything a gate prints is also appended to a log, one JSON line per print: timestamp, module, gate, mode, session, stream, text — a text of several lines, a verdict or a traceback, stays one record, never a line apiece, its newlines escaped by JSON. The records of a run whose log is written, each text followed by a newline, rebuild what was printed on each stream exactly, save a character the stream could not encode, which the stream shows escaped and the record keeps (decision [dec-0038-log-record-per-print](../../docs/decisions/dec-0038-log-record-per-print.md)). Location: the fixed dial `log_dir` ([§7](#t7)) when set — repository-relative and verified git-ignored, otherwise a configuration failure; else `${CLAUDE_PLUGIN_DATA}`; else nowhere, and stdout is the record. The log rotates at a fixed size, holds only what was printed, and a logging failure never changes the verdict — the one error a gate swallows, and the code says so. It is built on the standard library's `logging`, not a hand-made tee (decision [dec-0022-output-log-through-logging](../../docs/decisions/dec-0022-output-log-through-logging.md)): a `RotatingFileHandler` behind a `MemoryHandler` that holds records until the location is known, with three cautions — the logger is named and does not propagate, so no other library's line reaches stdout or stderr, which in hook mode are a protocol; the stream is the caller's choice and the level only carries it; `logging.raiseExceptions` is switched off, because its default prints a traceback to stderr, whose first line is what the user sees.
13. **Paths.** The target path comes from the tool input, resolved against the event's `cwd`; a path escaping the repository is a visible skip.
14. **Fixtures.** Case records — number, title, red, green, the message red must teach — numbered as in [§10](#t10), the module's own from 1 and the shared acceptance items, linked into `tests/` and run through the module's own entry point, from 101. The runner drives the real entry point with real hook events and fails a case when red does not fire, when red does not teach the expected message, or when green still fails. A property with no failing half is a separate assertion item. YAML fixture documents are rendered by the dumper, never typed as strings, unless malformed text is the point.
15. **Absence fixtures.** Every external tool or library the gate needs has a fixture simulating its absence; the shared items cover the interpreter, git, PyYAML and the shared package itself, and a module adds one for anything more it needs.
16. **Imports at the top.** Every import stands at the top of its module, where a reader, the type checker and the preflight see the dependency; none inside a function or a method, unless it is explicitly necessary — and then the reason is written at the import, beside the marker that silences the check. Today there are two such cases, of one kind: a module's two modes, and a generator's acts, are imported after the preflight, because only then does a missing library become its designed message instead of a traceback. A call of `importlib.import_module` made on purpose — the preflight's own — is one the tool does not see; review holds it. The kit's tooling holds the rule: `ruff` rule `PLC0415` (decision [dec-0026-imports-at-the-top](../../docs/decisions/dec-0026-imports-at-the-top.md)).

Every check's **error message** is written here as part of the design — the module's own; the shared texts are written out once, in [kit-shared-gate-code §3](../../shared/GATE.md#g3), and the module's table links there — it is the highest-bandwidth channel for teaching an agent mid-session: state what failed, why the rule exists (one clause), and the exact fix. Reviewed like code; copied verbatim into the script.

**Installed components reference nothing in the kit.** A skill, hook, script, command, agent, error text, or install note never cites the requirements document, the rollout plan, a matrix row, a decision record, a research comparison, or this document: consumers install the module without the kit, so every such reference dangles there. Rules are stated in those components in plain words; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

The module's calibration surface. Namespace = plugin name in the project's `constitution.yaml`; every dial has a default; the module works with zero configuration. A module with a hook gate — at write time, or at a turn's end — carries the fixed dial `severity` — `block` (default) or `warn` — as its first row; its repository-scan mode ignores the dial and always reports. Every gate also carries the fixed dial `log_dir` — absent by default — naming a repository-relative, git-ignored directory for its output log ([§6](#t6), gate-script rule 12).

| dial | default | meaning |
|---|---|---|
| `<dial>` | `<value>` | one line |

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

For each artifact: `gate` (deterministic — hook or script, red means fix) or `advisory` (judgment-shaping — skill prose, suggestions in review). Nothing advisory is dressed as a gate. A deterministic check whose blocking is a dial is a `gate` with its severity dial named — the check is still deterministic. For a hook gate that dial is `severity` ([§7](#t7)): `warn` reports the finding and lets the write, or the turn's end, through — the adoption path onto a repository with legacy documents, or the path for a session that must not be asked to commit; the default `block` keeps the gate a gate. Then the **honest limits**: every path the gate does not see (a tool that bypasses the hook's event, a moment outside its trigger), each with its backstop.

**Exit-code contract** for every check: a finding (the repository is wrong) and a configuration failure (the checker is broken, a pinned tool is missing, the invocation is malformed) are distinct exit codes with distinct messages, so a reader never mistakes one for the other. A missing tool is loud, never a silent pass; a check that could not run reports that it could not run.

<a id="t10"></a>
## 10. Acceptance

For each gate: the red→green fixture proving it (a fixture that fails without the check, passes with it) and its path under `tests/` ([law 7 of CLAUDE.md](../../CLAUDE.md#law-7)), plus one fixture showing the exit-code split of [§9](#t9) (a missing tool or malformed invocation exits differently from a finding). For each advisory rule: the boundary examples above stand as its acceptance. Each item labeled by verification kind: `fixture` (bare temp repo), `live` (the kit as consumer zero, or a consumer project, the plugin loaded from this repository), `review` (the human, at the one yes), `kit check` (a check the kit runs on the module from outside it, never shipped).

**Handles.** One prefix per kind of handle in a document, never reused for another kind in the same document. A prefix is a letter or a word followed by a number, `T1`; a letter followed by a hyphen and a lowercase letter, `R-a`, is another prefix, the advisory rules'; a bare number is local to the list it stands in and is cited with its section, "limit 4 of the enforcement section"; an item added beside another takes that item's number with a letter, `L1b`; the rows of the artifacts table are keyed by their component and path. The kinds: the message keys as the module's `messages.py` names them; `E<n>` for the enforcement rows of [§9](#t9); the acceptance items numbered from 1 for the module's own and from 101 for the shared items, bare or under `T<n>` and `S<n>`; the live, review and kit-check items continuing the module's own numbering or under `L<n>` — `V<n>` where `L` is the module's message prefix. A key of another document is written qualified ([rule 8 of plc-0006-module-documents](../../docs/policies/plc-0006-module-documents.md#r8)).

**Examined count.** Every check reports how many items it examined in its green and red output alike. Zero is a visible count, never a failure and never a silent green: a check that inspected nothing must say so, because a vacuous green read as permission is the failure this rule exists for.

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
