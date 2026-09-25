---
id: module-const-interaction
type: current-state
title: const-interaction — answer in the shape the question has, assumptions and lists addressable, and stop before a hard-to-reverse act
status: active
---

# MODULE.md — `const-interaction`

*Draft at manifest version `0.0.1`, with open slots. This document is the module's description ([template](../../module-template/MODULE.md)). Every list and table row carries a handle.*


<a id="t1"></a>
## 1. Purpose

A short, vague request is answered by a page: a yes/no question opens with three paragraphs of context and the word arrives at the end, if at all; a request for a value comes back as an explanation; the assumption that made the answer possible is never said, so the user cannot correct it; a list of findings has no handles, so the user quotes a sentence to point at one; a request that is wrong is carried out with a softened note, or a failure is reported as done because it was not verified. Observed in the kit's own sessions: the "Restate before acting", "Assumptions are always explicit", "Every list item is addressable" and "Honesty over agreement" bullets of the kit's session guide were each written after such a session, and "Lead with the answer" was there from the first day — five rules carried by hand in a guide the module exists to replace. On the escalation side, the same sessions produced the "Refuse destructive moves without a spoken confirmation" bullet after an unasked history rewrite, and `git reset`, `git checkout -- .` and `rm -rf` on a scratch tree remain one keystroke from a session that never learned the rule. This module states the answer shape as rules a session carries always, and puts one deterministic gate in front of the enumerated destructive commands.

<a id="t2"></a>
## 2. Failure class

`self-limiting`: a long answer, a missing assumption line, an unnumbered list are each felt by the reader at once and corrected in the session — nothing compounds in the repository. The one exception is the destructive act, whose damage is immediate and sometimes final; that slice is the gate, and it is still self-limiting in the sense that each event is one, never a growing debt. **Entry trigger:** the same correction on the shape of a reply recurs across sessions — a session-guide edit or a commit note on answer length, a silent assumption, an unaddressable list or a softened finding, made twice or more; the kit passed it with five guide bullets on one theme. A single unconfirmed destructive command is trigger enough for the gate alone.

<a id="t3"></a>
## 3. Rows

| row | this module's reading |
|---|---|
| [A7.1](../../docs/requirements.md#a7-1) | The expected shape of an answer is one of a closed set — yes/no, a value, a short list, an explanation, a deliverable — and the reply matches it: a yes/no question is answered with the word first and the qualification after; a value with the value; a "why" with the explanation. A shape is classified from the question, never from what the session would like to say. Judgment; the pairs of [§8](#t8) are the definition. |
| [A7.2](../../docs/requirements.md#a7-2) | Every assumption made while reading the request or doing the work is listed, one line each, in the reply that delivers the work; when none was made, no assumption block appears — the line is never an empty ritual; an assumption that would change the work materially is a question, priced by the threshold module `const-questions` carries where installed and by the kernel's stakes triage otherwise. The restatement that opens a reply to a vague request is the sibling's rule ([requirement A6.6](../../docs/requirements.md#a6-6)); this row owns what is listed after the reading is taken. |
| [A7.3](../../docs/requirements.md#a7-3) | The answer stands first; the elaboration follows only when asked for or when the answer cannot be trusted without it — a one-line "why" beside a "no" is the answer, three paragraphs of preamble before it are the failure. |
| [A7.4](../../docs/requirements.md#a7-4) | A request that is wrong, unreasonable or in conflict with the governing rules is said to be so, with the reason, even after the user has decided and the work proceeds; a finding is never softened, a failure never hidden, unverified work never reported as done — "the tests were not run" is the sentence, not "should pass". Judgment; honestly ungateable, and the module says so. |
| [A7.5](../../docs/requirements.md#a7-5) | Every list, table and option set in a reply or a document carries a stable per-item handle — a number, a letter or a short key — so one item can be cited without quoting it; table rows get a key column or numbered rows; handles are scoped to their message, decision or document. The rule is the skill's. [decide: the optional gate-lite of the matrix, a script flagging unnumbered multi-item lists in governed documents — default not shipped, the comparison to price it — stakes process — decider Eugene Chernyshov] |
| [A8.1](../../docs/requirements.md#a8-1) | The answer side of the stakes-triaged escalation, after module `const-questions` took the asking side: a procedural gap met at routine stakes is closed by a reasonable call and a line in the commit note; one met at recorded stakes stops the work, is put to the decider and is recorded as the kernel asks — the record itself being what module `const-decision-records` writes where installed. † Open test: one enforcement moment — the ask is the sibling's moment, the call-and-note is this module's; if the boundary moves, the row goes whole to `const-questions`. |
| [A8.2](../../docs/requirements.md#a8-2) | A procedure at recorded stakes that the project has not written is never invented on the spot — not a numbering scheme, not a review flow, not a merge rule; the session stops and asks for it, or proposes it as a decision. † Open test: one invariant — "never improvise" is the negative of the previous row's "stop and ask"; the two rows stay together, in whichever module holds the previous row. |
| [A8.3](../../docs/requirements.md#a8-3) | The second escalation trigger, orthogonal to stakes: before any hard-to-reverse act — a deletion, a history rewrite, a force push, dropping a kernel definition, breaking a published contract — the consequence and the reversible alternative are stated and an explicit yes in chat is waited for; one yes covers one act; a repeated request after the warning is the user's decision, executed with the objection noted in the commit. The class is advisory. The enumerated command patterns are a `gate`: a `PreToolUse` hook on `Bash` refuses a command matching a pattern of the dial with a teaching error until the user confirms, and says of everything outside the list that it is not seen. [decide: the pattern language of the dial and the tokenising of the command — default the comparison's recommendation — stakes process — decider Eugene Chernyshov] [decide: the confirmation mechanism — a permission prompt carrying the teaching text, a block the user lifts by re-asking, or a marker — default the comparison's recommendation — stakes process — decider Eugene Chernyshov] [decide: the default pattern list — default the comparison's proposed list — stakes process — decider Eugene Chernyshov] |
| [A10.2](../../docs/requirements.md#a10-2) | Plain chat language for a reader whose first language is not English: short sentences, common words, no idiom, a term defined at first use — the chat half of the language aspect; the document half is module `const-language`. † Open test: one lifecycle trigger — this module enters on reply-shape friction, `const-language` on prose-complexity complaints in documents; the row stays here while it is about chat. |



<a id="t4"></a>
## 4. Decisions

Provenance of this module's rules: the records whose rulings it applies, each cited by its record id while the record exists. When a record is deleted its entry goes with it and nothing replaces it; a ruling below recorded stakes has no entry. The rule itself is stated in the section where it acts ([§5](#t5)–[§9](#t9)); a record is cited for where and why it was decided, never in place of the rule ([kernel §5](../../kernel/CONVENTIONS.md#k5)). The record holds the options and reasoning, which are not restated here.

1. `<record-id>` — one line naming what it fixes here.

<a id="t5"></a>
## 5. Invariant

**No `Bash` command run through the platform's shell tool matches a pattern of the `destructive` dial without the user having confirmed that command.** [decide: the exact wording of "matches" and "confirmed" follows the pattern-language and confirmation decisions of [§3](#t3) — default the comparison's recommendation — stakes process — decider Eugene Chernyshov]

The advisory rules beside it, each `advisory` in its own text and carried always-on:

- **I-a.** The expected shape of the answer is classified from the question — yes/no, a value, a short list, an explanation, a deliverable — and the reply matches it: a yes/no question is answered with the word first, the qualification after; a value with the value; a "why" with the reason; a deliverable with the thing itself. *Advisory.*
- **I-b.** The answer stands first. Elaboration follows only when asked for, or when the answer cannot be trusted without one clause of it. *Advisory.*
- **I-c.** Every assumption made while reading the request or doing the work is listed in the reply that delivers the work, one line each, under a heading of its own; when none was made, no such block appears. An assumption that would change the work materially is a question, priced by the stakes triage of the constitution's conventions page the project adopted. *Advisory.*
- **I-d.** A request that is wrong, unreasonable or in conflict with the governing rules is said to be so, with the reason, even after the user has decided and the work proceeds. A finding is never softened, a failure never hidden, and work that was not verified is never reported as done: the reply says what was run and what was not. *Advisory.*
- **I-e.** Every list, table and option set carries a stable per-item handle — a number, a letter or a short key — so that one item can be cited without quoting it; table rows carry a key column or numbers; a handle is scoped to its message, decision or document, and is named with that scope across the boundary. *Advisory.*
- **I-f.** A procedural gap met at routine stakes is closed by a reasonable call and one line in the commit note; one met at recorded stakes stops the work and is put to the decider, and the answer is recorded as the conventions page asks. *Advisory.*
- **I-g.** A procedure at recorded stakes that the project has not written — a numbering scheme, a review flow, a merge rule — is never invented on the spot: the gap is named and the procedure proposed as a decision. *Advisory.*
- **I-h.** Before any hard-to-reverse act — a deletion, a history rewrite, a force push, dropping a definition others rely on, breaking a published contract — the consequence and the reversible alternative are stated and an explicit yes in chat is waited for; one yes covers one act; a request repeated after the warning is the user's decision, done with the objection noted in the commit. The gate holds the enumerated command patterns; everything else in the class is this rule. *Advisory.*
- **I-i.** Chat is written in plain language for a reader whose first language is not English: short sentences, common words, no idiom, a term defined at its first use. *Advisory.*

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

Each pair reads *violates / complies*; the pairs are the definition and are carried by the skill; the project's own arrive through the dial `boundary_examples` ([§7](#t7)).

**Answer shape** ([A7.1](../../docs/requirements.md#a7-1), [A7.3](../../docs/requirements.md#a7-3)):

1. "Is the branch merged?" → three paragraphs on the branch's history ending in "so, not yet" / "No. The range check is still red on one commit; the fix is one trailer."
2. "Which version is on main?" → the release process explained, the number in the last line / "0.0.1 — every module, until Phase D."
3. "Why does the hook refuse the commit?" → "It refuses it." / the one reason, then the fix — an explanation was asked for, and one is the shape.
4. A deliverable asked for — a plan, a document — → a summary of what it would contain / the deliverable itself, its notes after it.

**Assumptions** ([A7.2](../../docs/requirements.md#a7-2)):

5. A request with no ambiguity answered with "Assumptions: none" every time → the empty ritual / no assumption line at all when none was made.
6. "Use the usual layout" done on the layout the last module used, unsaid → a silent assumption / the same work with one line: "assumed the layout of the previous module".
7. A reading that changes which files are written listed as an assumption after the fact → a material assumption taken instead of asked / the choice put as a question before the work, priced by the stakes triage.

**Honesty over agreement** ([A7.4](../../docs/requirements.md#a7-4)):

8. The tests were not run and the reply says "should pass" → unverified work reported as done / "the tests were not run: the runner needs a library this machine lacks".
9. A request that breaks a published contract carried out with "note: this may affect consumers" in the last line → a softened finding / "this breaks the contract of version 0.1.0 for every consumer; the reversible alternative is a new key beside the old one" first, then, on a repeated request, the work with the objection noted in the commit.
10. A finding the user will not like left out of the review → hidden / stated, with its severity, whatever the reception.

**Addressable lists** ([A7.5](../../docs/requirements.md#a7-5)):

11. Findings as bullets with no handle → the user quotes a sentence to point at one / findings numbered, and the number cited in the fix commit.
12. A table of dials with no key column → unaddressable rows / the dial's name in the first column, the handle.
13. Options numbered 1, 2, 3 beside numbered findings → the two confused / options lettered, findings numbered, steps numbered in their own list.

**Escalation, stakes-triaged** ([A8.1](../../docs/requirements.md#a8-1), [A8.2](../../docs/requirements.md#a8-2)):

14. No rule says where a scratch file goes → the session stops to ask / a reasonable call, one line in the commit note.
15. No rule says how a record is numbered → a scheme invented on the spot and used / the work stops there; the scheme is put as a decision at process stakes, and recorded once chosen.
16. A review flow the project has not written → the session performs one it made up and reports the change reviewed / "the project has no review flow; this change is unreviewed until one is decided" — the gap named, never filled by improvisation.

**Irreversibility** ([A8.3](../../docs/requirements.md#a8-3)):

17. `git push --force` to a shared branch on the user's "just push it" → done / the consequence — every collaborator's clone diverges — and the alternative — `--force-with-lease`, or a new branch — stated, then the wait for a yes.
18. Deleting a directory of generated files that one command rebuilds → a warning ceremony / done and noted: it is reversible, the class does not apply.
19. One yes given for a history rewrite, then a second rewrite done under it → an approval stretched over two acts / the second asked for on its own.
20. The user repeats "delete it" after the warning → refused again / done, the objection in the commit note: the decision is theirs.

**Plain language** ([A10.2](../../docs/requirements.md#a10-2)):

21. "We'll circle back once the dust settles on the upstream churn" → idiom on idiom / "We return to this after the upstream changes stop."
22. A term of the kit used without definition in a reply to a newcomer → undefined jargon / the term defined at its first use in that reply.

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

**Depends on:** [kernel §4](../../kernel/CONVENTIONS.md#k4) — the stakes triage, which prices a material assumption and a procedural gap; [kernel §5](../../kernel/CONVENTIONS.md#k5) — what a recorded answer is written as, whoever writes it; [kernel §6](../../kernel/CONVENTIONS.md#k6) — the dials file, where the project's own pairs and its pattern list arrive. Nothing else.

**Kernel alone:** on a bare repository the always-on carrier states the answer-shape rules, the assumption rule, the addressable-lists rule, the honesty rule, the two escalation rules and the irreversibility rule with their seed pairs; a recorded-stakes gap is put to the decider and recorded as the kernel asks, by whatever the project has for it; the gate holds the default pattern list over every `Bash` call, with a `constitution.yaml` that holds no key of this namespace, and with no `constitution.yaml` at all [decide: whether the gate skips or applies its defaults without a dials file — default the shared visible skip, as every gate — stakes process — decider Eugene Chernyshov].

**When module `const-questions` is installed,** a material assumption becomes a question in that module's shape, priced by its threshold and pairs, and the restatement of a vague request is its rule; this module's assumption line lists what was taken after the reading. **When module `const-decision-records` is installed,** a recorded-stakes gap is written down through its record skill, which knows where records live and prices the stakes with the same triage. **When module `const-task-close` is installed,** the objection noted in a commit after a repeated request stands in the commit message its turn-end hook asks for. Each is an optional enhancement; every rule here runs with the kernel alone.

<a id="t12"></a>
## 12. Deferred

1. **An output style as a second carrier**, unforced, selectable under the plugin's name. The specification names it as optional; the comparison priced it and found the forced form a single slot that overrides the user (decision [dec-0042-interaction-module-rulings](../../docs/decisions/dec-0042-interaction-module-rulings.md), R2). Signal: a consumer whose sessions lose the rules after compaction with the chosen carrier, reported twice.
2. **A checker for plain chat language.** No tool reads chat; the rule is judgment ([A10.2](../../docs/requirements.md#a10-2)). Signal: none foreseen; the document half is module `const-language`.
3. **The class beyond the pattern list.** A destructive act the list does not name — an API call that deletes, a tool other than the shell — is advisory. Signal: a destructive act through another tool reported once in a consumer; it enters the list or earns a matcher of its own.
4. **The gate-lite on unnumbered lists in documents**, where it is not shipped ([§3](#t3), row [A7.5](../../docs/requirements.md#a7-5)). Signal: a delivered document with an unaddressable list past review, twice.

---

# Plugin skeleton

```
const-<aspect-name>/
├── .claude-plugin/
│   └── plugin.json          # manifest — the ONLY file inside .claude-plugin/; version 0.0.x while draft
├── MODULE.md                # this document, filled in
├── INSTALL.md               # install/uninstall notes; the one CLAUDE.md pointer line if any
├── skills/
│   └── <name>/SKILL.md      # optional
├── commands/<name>.md       # optional
├── agents/<name>.md         # optional
├── hooks/hooks.json         # optional
├── scripts/                 # optional; reference via ${CLAUDE_PLUGIN_ROOT}
│   ├── const_gate -> ../../../shared/const_gate   # a gate only: the shared code, by relative link
│   └── <module>_gate/       # the module's own package: model, messages, checks, modes, start
└── tests/                   # harness.py, consumer.py, shared_items.py linked from shared/tests/; one red→green fixture per gate ([law 7 of CLAUDE.md](../../CLAUDE.md#law-7))
```

Kebab-case everywhere. Only plugin.json lives inside `.claude-plugin/`; every component directory sits at plugin root. Verify the manifest fields against the current plugin reference at authoring time.
