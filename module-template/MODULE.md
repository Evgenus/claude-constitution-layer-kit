---
id: module-const-<aspect>
type: current-state
title: const-<aspect> — <one clause saying what the module guards or does>
status: active
---

# MODULE.md — `const-<aspect>`

*Template. Every constitution module is a folder whose `plugin/` subfolder is a Claude Code plugin, with this document at the folder's top beside it. This document is the module's **description** from the first draft on: there is no separate specification kind (decision [dec-0003-module-spec-kind](../docs/decisions/dec-0003-module-spec-kind.md)). A draft module carries manifest version `0.0.x`; it is published at `0.1.0` or higher, once every gate has its fixture and no open marker is left. Open slots in a draft are written inline as `[decide: <slot> — default <X> — stakes <level> — decider <who>]`; an authoring session derives its questions from these markers in document order. A published module carries none.*

*Fill every section; a section that does not apply says "none" with one line of reasoning. The module depends on the kernel (`CONVENTIONS.md` + schemas) and on nothing else. If it seems to need a sibling module, the shared concept belongs in the kernel; raise that instead of coupling. **No file in the module references a project directly** (paths, names, values): project specifics arrive only through the dials namespace. The module must install and operate on an empty repository using its defaults ([kernel §6](../docs/constitution/CONVENTIONS.md#k6), portability rule). References to sibling modules are permitted **only as optional enhancements** ("when module `const-x` is installed, ..."); every rule must be executable with the kernel alone — the test: **kernel + this module on an empty repository is a functioning installation.** Every list and table row carries a handle so one item can be cited without quoting it.*

*In a module's copy, the two paragraphs above give way to one status line in italics, three sentences: "Draft at manifest version `0.0.x`, no open slots.", then "This document is the module's description", with the word *template* linked to this file, then "Every list and table row carries a handle.". Once the module is published, its first sentence reads "Published at manifest version `x.y.z`."; a draft names its open `[decide:]` markers in place of "no open slots". It names no phase of the rollout plan, a task-record whose state changes apart from this document. A bold label in this template is followed by one of two marks: *(slot)*, where the module writes its own text, and *(template rule)*. A label marked *(template rule)* binds the module and is not copied into it.*

<a id="t1"></a>
## 1. Purpose

One paragraph: the failure pattern this module prevents, stated concretely — in terms someone has observed, not a category name. If the failure pattern cannot be named, the module is not ready to exist.

<a id="t2"></a>
## 2. Failure class

`accumulating` or `self-limiting`, with one line of reasoning; a module may be split honestly — name the accumulating slice and the self-limiting remainder. Then the **entry trigger** *(slot)*: accumulating modules belong in every project's day-one install set. A self-limiting module names the observed friction signal that earns its installation, stated so a consumer can recognize it.

<a id="t3"></a>
## 3. Rows

The requirement set, and nothing else ([law 4 of CLAUDE.md](../CLAUDE.md#law-4)): every matrix row homed in this module, by handle. Each is linked to its anchor in the requirements document in the form the placeholder shows. The row's text lives in the matrix and is not repeated. The table carries the *reading* the row needs beyond its text: interpretation, boundary rulings, the part of a shared row this module owns. A row under a boundary test (marked † in the matrix) states which of the three tests is open — *one invariant? one enforcement moment? one lifecycle trigger?* — and which sibling takes the row if the boundary moves.

| row | this module's reading |
|---|---|
| `[A<n>.<m>](../../docs/requirements.md#a<n>-<m>)` | … |

Optional, one line after the table: each row of the module's aspect that another place homes, with that home and how this module meets it. This may be the kernel's, a definition enforced through one of this module's rows, or a binding row this module only gives dials to.

<a id="t4"></a>
## 4. Decisions

Provenance of this module's rules: the records whose rulings it applies, each cited by its record id while the record exists. When a record is deleted its entry goes with it and nothing replaces it; a ruling below recorded stakes has no entry. The rule itself is stated in the section where it acts ([§5](#t5)–[§9](#t9)). A record is cited for where and why it was decided, never in place of the rule ([kernel §5](../docs/constitution/CONVENTIONS.md#k5)). The record holds the options and reasoning, which are not restated here.

One record per entry, one line each, the record linked in the form the placeholder shows. A line may name another record it relates to, which has its own entry:

1. `[<record-id>](../../docs/decisions/<record-id>.md)` — one line naming what it fixes here.

<a id="t5"></a>
## 5. Invariant

The one rule the module guarantees, stated in a single testable sentence built only from kernel vocabulary and this module's own definitions. An advisory-only module claims no invariant; in its place stands its rule list. A module with an invariant and advisory rules states the invariant, then its advisory rules. Each list's items carry the handles `<L>-a`, `<L>-b` and so on in bold, each rule labeled `advisory` in its own text. The form `<L>-a` is a prefix apart from a message key's `<L><n>` ([rule 8 of plc-0006-module-documents](../docs/policies/plc-0006-module-documents.md#r8)). So a module keeps the letter its rules have.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

What this plugin ships and what each part carries. Every row stays: a component the module does not use reads `none` in its path cell, with its reason in one line. Native-first: platform component > repo script > third-party tool > new infrastructure. Every step down from a platform component names, in one clause, what the native option cannot do.

| component | path | carries |
|---|---|---|
| skill | `plugin/skills/<name>/SKILL.md`, and each file beside it that the skill names; one row per skill | the procedure, loaded when the activity occurs. The model loads a skill when something sends it there. Its description, which the skill listing carries, opens with an order — `Load this skill first, before <the moment> — every time, …` — and then says what the skill does. After `Use when` it names its other moments, and last comes its `Advisory:` line, which says what the skill shapes and what a gate holds. A description that opens with what the skill does was found to bring no load at the moment of writing. The skills `plain-language` of module `const-language` and `style-defaults` of module `const-styling` alone keep the words the live proof ran, which have no `Use when` segment. A skill is also named at its moment by the module's other parts, where they meet it. A gate whose rule the skill teaches names it after every red in the shared line `F10` of [kit-shared-gate-code §3](../shared/MESSAGES.md#g3), through the identity's `skills`. A skill may apply before a write, or at a moment no gate meets, and sessions were found not to load it at that moment. Such a skill is named in one pointer line, which every session and every subagent pays for in characters: `<module> (advisory): before <the moment>, load the skill <module>:<skill>.`. It is printed by the `SessionStart` hook of the hook row and given to every subagent by a `SubagentStart` hook. A skill outside that case ships no pointer line (decision [dec-0079-skills-named-at-their-moment](../docs/decisions/dec-0079-skills-named-at-their-moment.md)) |
| hook | `plugin/hooks/hooks.json` + `plugin/scripts/` | deterministic enforcement of the invariant. Or, as a `SessionStart` hook printing rules to stdout, the always-on carrier for advisory content, declared `advisory`, never `gate`. Or a grant, a `PreToolUse` hook that answers `allow` for a command the module itself ships, declared `grant`, its row in [§9](#t9) naming what it allows. The match of a grant, the subagent's start and the visible zero stand in [the hook row](slot-guidance.md#s9) |
| eval case | `evals/<case>/case.yaml`, with `scaffold.sh` where the run needs a project; each case names its plugin, `plugins:` listing `../../plugin` | a prompt at one moment of the module and the graders that hold what a session must do there, which `claude plugin eval` runs on the pinned model. Every module has at least one. The cases, their graders and their tools stand in [the eval case row](slot-guidance.md#s7) |
| command | `plugin/commands/<name>.md` | only for acts a human deliberately initiates — name the scenario where a human actually types it |
| agent | `plugin/agents/<name>.md` | only for a genuine delegation boundary |
| script (sh) | `plugin/scripts/<name>.sh` | a POSIX shell entry point, all paths via `${CLAUDE_PLUGIN_ROOT}`. It is the wrapper each hook and the scan call. It finds `python3`, prints its own two lines when there is none, and hands over to the Python entry file with `exec`. Or it is a printer that reads nothing, such as the pointer line's |
| script (py) | `plugin/scripts/<entry>.py` | a Python entry file. It has the interpreter floor, `REQUIRES`, the shared package's import with `C15`, the version call, then the module's own package ([rule 1 of kit-gate-script-rules](gate-script-rules.md#r1)). Python 3, with PyYAML when the script reads YAML. A script that reads no YAML may instead be POSIX shell, the row above. A missing runtime or library is a configuration failure ([§9](#t9)). Python scripts follow [kit-gate-script-rules](gate-script-rules.md) |
| package | `plugin/scripts/<module>_gate/` | the module's own code: model, messages, checks, modes, start, and the dials and session parts its printers need |
| effect entry | `plugin/scripts/effect-report.sh` + `plugin/scripts/effect-report.py`, and the rules in the module's package | the report of [§13](#t13): the code that finds each rule's moments and their outcomes, handed to the shared runner. `none` while the module counts no rule, with its reason |
| shared code | none in the plugin | the Python package `constitution-layer-kit`, which pip installs for the `python3` the hooks run; the plugin never carries it |
| dependencies | `plugin/requirements.txt` | the libraries the scripts need beyond the shared package, installed by one command ([rule 7 of kit-gate-script-rules](gate-script-rules.md#r7)) |
| configuration | `plugin/<file>`, `plugin/scripts/<file>` or `plugin/<tool>/<file>` | a pinned third-party tool's own files: its configuration, which the code that runs the tool reads or hands to it, and its pin. The pin is the files that name the exact version an install takes. Where each file stands, and what the coverage pair lists, stand in [the configuration row](slot-guidance.md#s13) |
| manifest | `plugin/.claude-plugin/plugin.json` | name, version, description, author and license `Apache-2.0` |
| tests | `tests/` | the fixtures of [§10](#t10), run from a clone of the kit; never installed |
| install note | `plugin/INSTALL.md` | for a module with a Python entry file, the command that installs the shared package at the tag of `REQUIRES`. The entry files' lines `C15` to `C17` point at it (R15 of [dec-0099-shared-code-installed-as-a-pip-package](../docs/decisions/dec-0099-shared-code-installed-as-a-pip-package.md#r15)). At most one line for the project's own `CLAUDE.md`, the *CLAUDE.md line*, for discoverability only, or `CLAUDE.md line: none`. Its steps and the way always-on rules ship stand in [the install note row](slot-guidance.md#s10) |

Four fixed sub-slots follow the table:

- **Always-on content** *(slot)*: the exact lines the module's `SessionStart` and `SubagentStart` hooks print, and each skill's `description`, with its `when_to_use` if any, as the skill listing carries it. Each states its size in characters; or "none". This is the module's whole always-on budget, since the platform loads the skill listing into every session. A line that holds a value, such as a path, is written with the value's placeholder, `{root}`, and sized as its fixed text, the placeholder named. A pointer line given to subagents too is counted again here, as the cost of each subagent's start. Then the pointer line of the skill row, or `Pointer line: none` with one line of reasoning. Its reason: no skill applies before a write or at a moment no gate meets. Or sessions were found to load it at its moment, or no session has been found to skip it.
- **Platform facts relied on** *(slot)*: each fact with its source, the date it was verified, one date per fact, and what breaks if it changes. A source is a link to the page of the official documentation, or `observed on Claude Code <version>` with what was run. It may also be this module's research comparison with the fact's handle there, or its section and item where the comparison gives none. Nothing in this slot comes from memory.
- **Cost and budget** *(slot)*: the hook budget each hook run declares, each wait's cap and each handler's `timeout`. It also gives each cost measured, with its date and the platform's version; or "none". [§9](#t9) and [§10](#t10) cite this slot by its name and never restate its figures. A figure that an accepted record cites in another numbered place stays there, and this slot cites that place.
- **Research** *(slot)*: a link to this module's own dated comparison in `docs/research/`. It is written at authoring, in kit vocabulary, from a survey of the official documentation, community harnesses, and applicable tools for exactly this module's rows. And, per row, whether the matrix's recommended enforcement was confirmed or overturned by it (decision [dec-0010-module-research-per-module](../docs/decisions/dec-0010-module-research-per-module.md)). Nothing from earlier design work enters unverified. Where a later survey covered some mechanisms only, the line names which comparison each mechanism cites ([rule 2 of plc-0005-research](../docs/policies/plc-0005-research.md#r2)).

**Gate-script rules** *(template rule)*: every Python script a module ships follows all sixteen rules of [kit-gate-script-rules](gate-script-rules.md). The fresh-context validation checks them.

**Error messages** *(slot)*. Every check's error message is written here as part of the design — the module's own. The shared texts are written out once, in [kit-shared-gate-code §3](../shared/MESSAGES.md#g3), and the module's table links there. It is the highest-bandwidth channel for teaching an agent mid-session: state what failed, why the rule exists (one clause), and the exact fix. Reviewed like code; copied verbatim into the script. The table is `| key | first line | why | fix |`, one row per key of the module's messages module. Some texts are no finding: a skip reason, the count line's tail, a session-start line, a note, a dial failure. Such a text fills the cells it has and writes `—` in the others.

**Installed components reference nothing in the kit** *(template rule)*. See [the rule](slot-guidance.md#s11).

<a id="t7"></a>
## 7. Dials

The module's calibration surface. Namespace = plugin name in the project's `constitution.yaml`; every dial has a default; the module works with zero configuration. A module with a hook gate — at write time, at a turn's end, or on a shell call — carries the fixed dial `severity`. The dial is its first row, `block` (default) or `warn`. Its repository-scan mode ignores the dial and always reports. Every gate also carries the fixed dial `log_dir`, absent by default. It names a repository-relative, git-ignored directory for its output log ([rule 12 of kit-gate-script-rules](gate-script-rules.md#r12)).

| dial | default | read by | meaning |
|---|---|---|---|
| `<dial>` | `<value>` | the gate, the scan, a printer or a skill | one line |

The `read by` cell names each part that reads the dial: only a dial a script reads is validated.

<a id="t8"></a>
## 8. Boundary examples

For every judgment-based boundary the module introduces (including its slice of the routine/product stakes line, if any): at least three contrastive pairs. Each keeps the number it was given. A number once used is never used again, as the handles of [§10](#t10) say. The numbers, the groups and the form of a pair stand in [the boundary examples](slot-guidance.md#s8). The examples are the definition; no abstract criteria. The project's own pairs arrive through dials.

<a id="t9"></a>
## 9. Enforcement honesty

Each artifact of [§6](#t6) that runs or prints, the session-start printers included, has a row of its own. Its kind is `gate` (deterministic — hook or script, red means fix) or `advisory` (judgment-shaping — skill prose, a line printed at session start, suggestions in review). Or it is `grant`: a hook's deterministic answer of `allow` for a command the module itself ships (the hook row of [§6](#t6)). A grant judges nothing, blocks nothing and is never red. Nothing advisory is dressed as a gate. The form of a declared scan, and of a gate whose blocking is a dial, stands in [the enforcement section](slot-guidance.md#s6). The table:

| # | artifact | kind |
|---|---|---|
| E1 | the hook on `<event>` and `<entry>.sh`: what it checks | `gate`, its dial `severity` |
| E2 | the scan: the code span of its `--scan` form | `gate` |
| E3 | the skill `<name>` | `advisory` |
| E4 | the hook on `SessionStart` and `<printer>.sh`: the line it prints | `advisory` |
| E5 | the hook on `PreToolUse` and `<grant>.sh`: the command it answers `allow` for, and that it says nothing for any other call | `grant` |
| E6 | the effect entry `effect-report.sh`: it informs judgment, gives no finding, never exits 2 and is never red | `advisory` |

Then the **honest limits** *(slot)*: first one line that cites the limits every gate shares, [kit-shared-gate-code §4](../shared/GATE.md#g4), and restates none. Then the module's own, numbered. Each is a path the gate does not see (a tool that bypasses the hook's event, a moment outside its trigger). It has its backstop, or `none — accepted` with the reason the gap is accepted.

**Exit-code contract** *(template rule)*. See [the rule](slot-guidance.md#s12).

<a id="t10"></a>
## 10. Acceptance

For each gate: the red→green fixture proving it (a fixture that fails without the check, passes with it), under `tests/` ([law 7 of CLAUDE.md](../CLAUDE.md#law-7)). Each gate also has one fixture showing the exit-code split of [§9](#t9) (a missing tool or malformed invocation exits differently from a finding). The proof of a grant, of an advisory rule, and the kinds that label an item (`fixture`, `live`, `eval`, `review`, `kit check`) stand in [the acceptance section](slot-guidance.md#s2).

**Runner line** *(slot)*. A line at column 0 that opens `Runner:`, outside code fences, names three things. The command that runs the fixtures from the module's folder, `python3 -m pytest tests`; the kit's run of them, `scripts/check-aspects.py --run --module <name>`; and the ranges of the fixture items the table holds. It may hold `<digits> items green`, a count that the kit's `scripts/check-aspects.py` holds against the runner's total under `--run`.

**Handles** *(template rule)*. As [rule 8 of plc-0006-module-documents](../docs/policies/plc-0006-module-documents.md#r8) states them, one prefix per kind. The rule on a number once used, and on a number a record cites, stands in [the handles paragraph](slot-guidance.md#s4).

**Rows** *(template rule)*. The acceptance table is `| item | kind | rows | what it proves |`. The reading of the columns, and what the kit's `scripts/check-aspects.py` holds of them, stand in [the rows paragraph](slot-guidance.md#s3).

**Examined count** *(template rule)*. Every check reports how many items it examined in its green and red output alike. Zero is a visible count, never a failure and never a silent green. A check that inspected nothing must say so. A vacuous green read as permission is the failure this rule exists for. A grant is no check: it examines nothing and prints no count line, only its answer.

<a id="t11"></a>
## 11. Siblings

**Depends on** *(slot)*: the kernel sections used, each external tool a gate preflights, such as git or a pinned third-party tool. It also lists the Python distribution `constitution-layer-kit`, which pip installs as it installs PyYAML for a module that reads YAML, and nothing else. The kit's shared gate code is no sibling ([law 3 of CLAUDE.md](../CLAUDE.md#law-3)). Then the kernel-alone statement, with that package installed: what the module does on a bare repository with the kernel only. It also says what runs without each external tool. Then each optional enhancement as "when module `const-<x>` is installed, …". A concept this module needs from a sibling is a kernel candidate, raised as a `process` decision, never coupled.

<a id="t12"></a>
## 12. Deferred

What this module deliberately does not ship yet, each with the friction signal that would earn it. The deferrals every gate shares stand once in [kit-shared-gate-code §1](../shared/GATE.md#g1), the deferred parts, and are cited, never restated. This list holds the module's own. Nothing here is a hidden requirement: a deferred item has no matrix row, or its row is marked deferred there.

<a id="t13"></a>
## 13. Effect

What the module counts of its own effect in a project that installs it, [aspect A14](../docs/requirements.md#a14). At each moment where one of its rules applies, whether the rule was applied, bypassed or missed. The records are [dec-0113-module-effect-is-rules-applied-not-bypassed](../docs/decisions/dec-0113-module-effect-is-rules-applied-not-bypassed.md) and [dec-0114-module-effect-report-design](../docs/decisions/dec-0114-module-effect-report-design.md). One row per rule the module's effect code counts, its key the key of the code's `Rule`:

| # | rule | moment | judge | ways |
|---|---|---|---|---|
| W1 | the rule in the module's words, the text the reader is given | where the rule applies: the act, the event or the turn | `pattern` | the ways it can fail, of the six below |

The paragraphs **Judge**, **Ways** and **Code** *(template rule)* stand in [the effect section](slot-guidance.md#s5); a module that counts no rule yet writes `none` here, with its reason.

---

## Plugin skeleton

The folder of a module, the template's own split and the rule on a license file stand in [the plugin skeleton](slot-guidance.md#s1).
