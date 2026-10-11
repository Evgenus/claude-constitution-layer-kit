---
id: module-const-<aspect>
type: current-state
title: const-<aspect> — <one clause saying what the module guards or does>
status: active
---

# MODULE.md — `const-<aspect>`

*Template. Every constitution module is a Claude Code plugin with this document at its root, and this document is the module's **description** from the first draft on — there is no separate specification kind (decision [dec-0003-module-spec-kind](../docs/decisions/dec-0003-module-spec-kind.md)). A draft module carries manifest version `0.0.x`; it is published at `0.1.0` or higher, once every gate has its fixture and no open marker is left. Open slots in a draft are written inline as `[decide: <slot> — default <X> — stakes <level> — decider <who>]`; an authoring session derives its questions from these markers in document order, and a published module carries none.*

*Fill every section; a section that does not apply says "none" with one line of reasoning. The module depends on the kernel (`CONVENTIONS.md` + schemas) and on nothing else — if it seems to need a sibling module, the shared concept belongs in the kernel; raise that instead of coupling. **No file in the module references a project directly** (paths, names, values): project specifics arrive only through the dials namespace, and the module must install and operate on an empty repository using its defaults ([kernel §6](../kernel/CONVENTIONS.md#k6), portability rule). References to sibling modules are permitted **only as optional enhancements** ("when module `const-x` is installed, ..."); every rule must be executable with the kernel alone — the test: **kernel + this module on an empty repository is a functioning installation.** Every list and table row carries a handle so one item can be cited without quoting it.*

<a id="t1"></a>
## 1. Purpose

One paragraph: the failure pattern this module prevents, stated concretely — in terms someone has observed, not a category name. If the failure pattern cannot be named, the module is not ready to exist.

<a id="t2"></a>
## 2. Failure class

`accumulating` or `self-limiting`, with one line of reasoning; a module may be split honestly — name the accumulating slice and the self-limiting remainder. Then the **entry trigger**: accumulating modules belong in every project's day-one install set; a self-limiting module names the observed friction signal that earns its installation, stated so a consumer can recognize it.

<a id="t3"></a>
## 3. Rows

The requirement set, and nothing else ([law 4 of CLAUDE.md](../CLAUDE.md#law-4)): every matrix row homed in this module, by handle. The row's text lives in the matrix and is not repeated; the table carries the *reading* the row needs beyond its text — interpretation, boundary rulings, the part of a shared row this module owns. A row under a boundary test (marked † in the matrix) states which of the three tests is open — *one invariant? one enforcement moment? one lifecycle trigger?* — and which sibling takes the row if the boundary moves.

| row | this module's reading |
|---|---|
| A<n>.<m> | … |

<a id="t4"></a>
## 4. Decisions

Provenance of this module's rules: the records whose rulings it applies, each cited by its record id while the record exists. When a record is deleted its entry goes with it and nothing replaces it; a ruling below recorded stakes has no entry. The rule itself is stated in the section where it acts ([§5](#t5)–[§9](#t9)); a record is cited for where and why it was decided, never in place of the rule ([kernel §5](../kernel/CONVENTIONS.md#k5)). The record holds the options and reasoning, which are not restated here.

1. `<record-id>` — one line naming what it fixes here.

<a id="t5"></a>
## 5. Invariant

The one rule the module guarantees, stated in a single testable sentence built only from kernel vocabulary and this module's own definitions. An advisory-only module claims no invariant; in its place stands the numbered rule list, each rule labeled `advisory` in its own text.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

What this plugin ships and what each part carries — only components the module actually uses exist. Native-first: platform component > repo script > third-party tool > new infrastructure; every step down from a platform component names, in one clause, what the native option cannot do.

| component | path | carries |
|---|---|---|
| skill | `skills/<name>/SKILL.md` | the procedure, loaded when the activity occurs. The model loads a skill when something sends it there. Its description, which the skill listing carries, opens with an order — `Load this skill first, before <the moment> — every time, …` — and then says what the skill does, after `Use when` its other moments, and last its `Advisory:` line, which says what the skill shapes and what a gate holds; a description that opens with what the skill does was found to bring no load at the moment of writing. A skill is also named at its moment by the module's other parts, where they meet it. A gate whose rule the skill teaches names it in the line after every red, the shared `F10` of [kit-shared-gate-code §3](../shared/GATE.md#g3), through the identity's `skills`. A skill that applies before a write, or at a moment no gate meets, and that sessions were found not to load at that moment, is named in one pointer line, which every session and every subagent pays for in characters: `<module> (advisory): before <the moment>, load the skill <module>:<skill>.`, printed by the `SessionStart` hook of the hook row and given to every subagent by a `SubagentStart` hook; a skill outside that case ships no pointer line (decision [dec-0079-skills-named-at-their-moment](../docs/decisions/dec-0079-skills-named-at-their-moment.md)) |
| hook | `hooks/hooks.json` + `scripts/` | deterministic enforcement of the invariant; or, as a `SessionStart` hook printing rules to stdout, the always-on carrier for advisory content — declared `advisory`, never `gate`. Text printed at session start does not reach a subagent, which starts with a context of its own; a pointer line of the skill row is also printed by a `SubagentStart` hook, as the event's `additionalContext` in one JSON object, since that event adds no plain stdout to the context; one script prints both forms, the subagent's on an argument. A gate whose own dial leaves it examining nothing — an empty list, an absent binding — prints one `SessionStart` line naming the module and the dial, for as long as the dial stays so, sized in characters in [§6](#t6): a silent zero read as coverage is the failure this rule exists for (decision [dec-0042-interaction-module-rulings](../docs/decisions/dec-0042-interaction-module-rulings.md#r3), R3) |
| command | `commands/<name>.md` | only for acts a human deliberately initiates — name the scenario where a human actually types it, or delete this row |
| agent | `agents/<name>.md` | only for a genuine delegation boundary |
| script | `scripts/<name>` | checks and generators; all paths via `${CLAUDE_PLUGIN_ROOT}`; Python 3 with PyYAML when the script reads YAML, POSIX shell otherwise; a missing runtime or library is a configuration failure ([§9](#t9)); Python scripts follow the gate-script rules below |
| install note | `INSTALL.md` | at most one pointer line for the project's own `CLAUDE.md`, for discoverability only. Always-on rules ship via a `SessionStart` hook (see hook row), never via a pointer or a plugin-root `CLAUDE.md` (not loaded); a copy-into-CLAUDE.md fallback may be offered, labeled as manual and version-drifting |

Three fixed sub-slots follow the table:

- **Always-on content:** the exact lines the `SessionStart` hook prints and their size in characters; or "none". This is the module's whole always-on budget. A pointer line given to subagents too is counted again here, as the cost of each subagent's start.
- **Platform facts relied on:** each fact, the date it was verified against the official documentation, and what breaks if it changes. Nothing in this slot comes from memory.
- **Research:** a link to this module's own dated comparison in `docs/research/` — written at authoring, in kit vocabulary, from a survey of the official documentation, community harnesses, and applicable tools for exactly this module's rows — and, per row, whether the matrix's recommended enforcement was confirmed or overturned by it (decision [dec-0010-module-research-per-module](../docs/decisions/dec-0010-module-research-per-module.md)). Nothing from earlier design work enters unverified.

**Gate-script rules** (decision [dec-0020-gate-script-rules](../docs/decisions/dec-0020-gate-script-rules.md)) — every Python script a module ships follows all sixteen; the fresh-context validation checks them:

1. **Shape.** The entry point is a thin file. Past about 300 lines of logic, or with a second entry point, the code is a package directory beside it, imported with no path manipulation — Python puts the script's directory on the import path. What every gate shares is not written again: `scripts/const_gate` is a relative symbolic link to the kit's one source, the module fills the interface of [kit-shared-gate-code §2](../shared/GATE.md#g2), and the entry file turns a missing shared package into its designed configuration failure (decision [dec-0025-shared-gate-code-linked](../docs/decisions/dec-0025-shared-gate-code-linked.md)). Never a sibling-script import and never a `sys.path` edit of the script's own process, the fixture runner included: the runner imports the shared package and the module's own packages through links in `tests/` (item 7 of [kit-shared-gate-code §2](../shared/GATE.md#g2)), and a child process it starts may be given its own path (item 8 there). A package or shared test file the runner imports this way uses `__file__` only as `Path(__file__).resolve()` and derives every path from that, since through a link `__file__` is the link's path, not the file's; the kit's `scripts/check-resolved-paths.py` holds it. Package and module names are snake_case because the language requires identifiers; entry-point files stay kebab-case.
2. **Messages.** One messages module per package: the shared package's, and the module's own for its findings, skip reasons, notes and dial failures. Each message is a function with typed parameters returning its three parts — what failed, why the rule exists, the exact fix — under the key it carries in this section's error-message table.
3. **One exit.** `main(argv) -> int`, a single `sys.exit`, and one guard that maps the configuration exception to exit 1. The entry file's exits before any package can be imported — the interpreter floor, the missing shared package — are the only others, each printing its designed line and the count line; a generator's entry file prints its own closing line in the count line's place, and its variants of those lines drop the clause about unchecked writes.
4. **Exit codes.** Named constants: 0 green, 2 finding, 1 configuration failure. Parameters are parsed with `argparse`, whose exit-2 default on bad usage is overridden to 1.
5. **Separation.** Parsing, checking, and reporting are separate functions; a check is a function of typed inputs.
6. **Runtime.** Plain `python3` through the POSIX entry point, never `uv run`. Floor: Python 3.12, the value of `FLOOR` in the shared preflight. The interpreter version and every declared library are preflighted on each invocation, before any verdict is printed.
7. **Dependencies.** Unrestricted, but declared in `requirements.txt` at the plugin root; the configuration-failure message prints the one install command for that file. `yaml.safe_load` only.
8. **No fail-open.** An unexpected exception exits 1 with its traceback; unparseable hook input is a configuration failure; nothing exits 0 on error. An advisory script may fail open and says so in its docstring.
9. **Types.** Every parameter and return is annotated. Untyped data — JSON, YAML — is parsed once into dataclasses; no bare `dict`, `list` or `Any` crosses a function boundary; closed vocabularies are enums. `mypy --strict` is clean.
10. **Docstring contract.** The entry point's docstring states the hook events, the modes, the input fields read, the exit codes, the output channels, and the dial keys read.
11. **Hook wiring.** `hooks.json` uses the exec form (`command` plus `args`) wherever a path placeholder appears, with an explicit `timeout`.
12. **Output log.** Everything a gate prints is also appended to a log, one JSON line per print: timestamp, module, gate, mode, session, stream, text — a text of several lines, a verdict or a traceback, stays one record, never a line apiece, its newlines escaped by JSON. The records of a run whose log is written, each text followed by a newline, rebuild what was printed on each stream exactly, save a character the stream could not encode, which the stream shows escaped and the record keeps (decision [dec-0038-log-record-per-print](../docs/decisions/dec-0038-log-record-per-print.md)). Location: the fixed dial `log_dir` ([§7](#t7)) when set — repository-relative and verified git-ignored, otherwise a configuration failure; else `${CLAUDE_PLUGIN_DATA}`; else nowhere, and stdout is the record. The log rotates at a fixed size, holds only what was printed, and a logging failure never changes the verdict — the one error a gate swallows, and the code says so. It is built on the standard library's `logging`, not a hand-made tee (decision [dec-0022-output-log-through-logging](../docs/decisions/dec-0022-output-log-through-logging.md)): a `RotatingFileHandler` behind a `MemoryHandler` that holds records until the location is known, with three cautions — the logger is named and does not propagate, so no other library's line reaches stdout or stderr, which in hook mode are a protocol; the stream is the caller's choice and the level only carries it; `logging.raiseExceptions` is switched off, because its default prints a traceback to stderr, whose first line is what the user sees.
13. **Paths.** The target path comes from the tool input, resolved against the event's `cwd`; a path escaping the repository is a visible skip.
14. **Fixtures.** Case records — number, title, red, green, the message red must teach — numbered as in [§10](#t10), the module's own from 1 and the shared acceptance items, linked into `tests/` and run through the module's own entry point, from 101. The runner refuses a number that two items carry, before any item runs. It drives the real entry point with real hook events and fails a case when red does not fire, when red does not teach the expected message, or when green still fails. A property with no failing half is a separate assertion item. Every message the module's code can print stands, in the fixtures that run it, at least once as a line typed by hand — its fixed text written out, a value the test computes filled in — since an expectation built by the message's own function cannot catch a defect in that function's text; a shared message stands so in the shared items or in the fixtures of a module that runs it. The fresh-context review holds this, with the kit's `scripts/list-message-literals.py`, never shipped in a module, as its aid: it reads the messages modules, where rule 2 puts every message, lists each message function with no piece of its fixed text, 15 characters or more, typed in a fixture that runs it — for a shared message, the shared harness included — and lists apart those whose text is too short to find — a list for the review to judge and never a verdict. YAML fixture documents are rendered by the dumper, never typed as strings, unless malformed text is the point.
15. **Absence fixtures.** Every external tool or library the gate needs has a fixture simulating its absence; the shared items cover the interpreter, git, PyYAML and the shared package itself, and a module adds one for anything more it needs.
16. **Imports at the top.** Every import stands at the top of its module, where a reader, the type checker and the preflight see the dependency; none inside a function or a method, unless it is explicitly necessary — and then the reason is written at the import, beside the marker that silences the check, `# noqa: PLC0415`. Today there are three such cases, of one kind: a module's two modes, a generator's acts, and a session-start printer's pipeline and dials, are imported after the preflight, because only then does a missing library become its designed message instead of a traceback. A call of `importlib.import_module` made on purpose — the preflight's own — is one the tool does not see; review holds it. The kit's tooling holds the rule: `ruff` rule `PLC0415` (decision [dec-0026-imports-at-the-top](../docs/decisions/dec-0026-imports-at-the-top.md)).

Every check's **error message** is written here as part of the design — the module's own; the shared texts are written out once, in [kit-shared-gate-code §3](../shared/GATE.md#g3), and the module's table links there — it is the highest-bandwidth channel for teaching an agent mid-session: state what failed, why the rule exists (one clause), and the exact fix. Reviewed like code; copied verbatim into the script.

**Installed components reference nothing in the kit.** A skill, hook, script, command, agent, error text, or install note never cites the requirements document, the rollout plan, a matrix row, a decision record, a research comparison, or this document: consumers install the module without the kit, so every such reference dangles there. Rules are stated in those components in plain words; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

The module's calibration surface. Namespace = plugin name in the project's `constitution.yaml`; every dial has a default; the module works with zero configuration. A module with a hook gate — at write time, at a turn's end, or on a shell call — carries the fixed dial `severity` — `block` (default) or `warn` — as its first row; its repository-scan mode ignores the dial and always reports. Every gate also carries the fixed dial `log_dir` — absent by default — naming a repository-relative, git-ignored directory for its output log ([§6](#t6), gate-script rule 12).

| dial | default | meaning |
|---|---|---|
| `<dial>` | `<value>` | one line |

<a id="t8"></a>
## 8. Boundary examples

For every judgment-based boundary the module introduces (including its slice of the routine/product stakes line, if any): 3–4 contrastive pairs (violates / complies), numbered. The examples are the definition; no abstract criteria. The project's own pairs arrive through dials.

<a id="t9"></a>
## 9. Enforcement honesty

For each artifact: `gate` (deterministic — hook or script, red means fix) or `advisory` (judgment-shaping — skill prose, suggestions in review). Nothing advisory is dressed as a gate. A scan over the tree is written in its row as a code span that reads exactly `<entry> --scan`, or `<entry>.py --scan` for an entry named by its Python file, nothing after the flag, so that the kit's `scripts/check-gate-lists.py` finds it and holds it in the kit's gate list, its CI list and the install guide's scan block. That check reads the table row by row, whatever a row's indent, each row opening `E<n>`, bold or not. A mode that is no tree scan is written `<entry> --scan --<flag> …` with the words `not a tree scan` in the same cell, outside a code span, and declares no scan. Any other code span in a row that holds `--scan`, and a span in the declared form in this section's prose, is a finding of that check. A deterministic check whose blocking is a dial is a `gate` with its severity dial named — the check is still deterministic. For a hook gate that dial is `severity` ([§7](#t7)): `warn` reports the finding and lets the write, or the turn's end, through — the adoption path onto a repository with legacy documents, or the path for a session that must not be asked to commit; the default `block` keeps the gate a gate. Then the **honest limits**: every path the gate does not see (a tool that bypasses the hook's event, a moment outside its trigger), each with its backstop.

**Exit-code contract** for every check: a finding (the repository is wrong) and a configuration failure (the checker is broken, a pinned tool is missing, the invocation is malformed) are distinct exit codes with distinct messages, so a reader never mistakes one for the other. A missing tool is loud, never a silent pass; a check that could not run reports that it could not run.

<a id="t10"></a>
## 10. Acceptance

For each gate: the red→green fixture proving it (a fixture that fails without the check, passes with it) and its path under `tests/` ([law 7 of CLAUDE.md](../CLAUDE.md#law-7)), plus one fixture showing the exit-code split of [§9](#t9) (a missing tool or malformed invocation exits differently from a finding). For each advisory rule: the boundary examples above stand as its acceptance. Each item labeled by verification kind: `fixture` (bare temp repo), `live` (the kit as consumer zero, or a consumer project, the plugin loaded from this repository), `review` (the human, at the one yes), `kit check` (a check the kit runs on the module from outside it, never shipped).

**Handles.** One prefix per kind of handle in a document, never reused for another kind in the same document. A prefix is a letter or a word followed by a number, `T1`; a letter followed by a hyphen and a lowercase letter, `R-a`, is another prefix, the advisory rules'; a bare number is local to the list it stands in and is cited with its section, "limit 4 of the enforcement section"; an item added beside another takes that item's number with a letter, `L1b`; the rows of the artifacts table are keyed by their component and path. The kinds: the message keys as the module's `messages.py` names them; `E<n>` for the enforcement rows of [§9](#t9); the acceptance items numbered from 1 for the module's own and from 101 for the shared items, bare or under `T<n>` and `S<n>`; the live, review and kit-check items continuing the module's own numbering or under `L<n>` — `V<n>` where `L` is the module's message prefix. A key of another document is written qualified ([rule 8 of plc-0006-module-documents](../docs/policies/plc-0006-module-documents.md#r8)).

**Rows.** The acceptance table is `| item | kind | rows | what it proves |`. The `rows` cell links every matrix row the item proves, each to its anchor in the requirements document, or says `none` for an item that proves no row of the module — the hooks file's shape, the manifest, the install note. An item names a row only where it proves what the module's reading of that row in [§3](#t3) says the module ships; the judgment of an advisory row is proved by its boundary examples at the review item, never by a fixture. The line of the shared items carries every row that a fixture item of the module, run through the same entry point — the script its hook or its scan calls — names, and no other row. Every row [§3](#t3) holds is named by at least one item. The item cell is handles and closed ranges, `T1–T4, T7`, a fixture item's handle being its runner number, bare or under `T` or `S`; the kind opens with `fixture`, `kit check`, `live`, `live, deferred` or `review`. The kit's `scripts/check-aspects.py` holds this as a line of the gate list; with `--run` it runs the runner and gives each row the result of its items, a row's status derived on each run and stored nowhere (decision [dec-0054-acceptance-items-name-their-rows](../docs/decisions/dec-0054-acceptance-items-name-their-rows.md)).

**Examined count.** Every check reports how many items it examined in its green and red output alike. Zero is a visible count, never a failure and never a silent green: a check that inspected nothing must say so, because a vacuous green read as permission is the failure this rule exists for.

<a id="t11"></a>
## 11. Siblings

**Depends on:** the kernel sections used — nothing else. Then the kernel-alone statement: what the module does on a bare repository with the kernel only. Then each optional enhancement as "when module `const-<x>` is installed, …". A concept this module needs from a sibling is a kernel candidate, raised as a `process` decision, never coupled.

<a id="t12"></a>
## 12. Deferred

What this module deliberately does not ship yet, each with the friction signal that would earn it. Nothing here is a hidden requirement: a deferred item has no matrix row, or its row is marked deferred there.

---

## Plugin skeleton

```text
const-<aspect-name>/
├── .claude-plugin/
│   └── plugin.json          # manifest — the ONLY file inside .claude-plugin/; version 0.0.x while draft
├── MODULE.md                # this document, filled in
├── INSTALL.md               # install/uninstall notes; the one CLAUDE.md pointer line if any
├── README.md                # the landing page for a reader, from the template's README.md; of the root README's kind, binds nothing
├── skills/
│   └── <name>/SKILL.md      # optional
├── commands/<name>.md       # optional
├── agents/<name>.md         # optional
├── hooks/hooks.json         # optional
├── scripts/                 # optional; reference via ${CLAUDE_PLUGIN_ROOT}
│   ├── const_gate -> ../../../shared/const_gate   # a gate only: the shared code, by relative link
│   └── <module>_gate/       # the module's own package: model, messages, checks, modes, start
└── tests/                   # const_gate and harness.py, consumer.py, shared_items.py linked from shared/; <module>_gate linked from ../scripts/; one red→green fixture per gate ([law 7 of CLAUDE.md](../CLAUDE.md#law-7))
```

Kebab-case everywhere. Only plugin.json lives inside `.claude-plugin/`; every component directory sits at plugin root. Verify the manifest fields against the current plugin reference at authoring time. A module carries no license file: its manifest names the license, and the kit's `LICENSE` and `NOTICE` stand at the kit root alone. Linking both into each module is reopened as a decision once a module is mirrored or vendored outside the kit's marketplace.
