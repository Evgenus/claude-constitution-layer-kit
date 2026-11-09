---
id: kit-template-slot-guidance
type: current-state
title: The slot guidance of the module template — the texts moved out of its sections
status: active
---

# The slot guidance of the module template

Each text below stands word for word as it stood in [the module template](MODULE.md), in the section its heading names, so "this document" and "here" in a text mean the module's document, as they did in the template. The slot of the template links to it. Like the template, this page stands in no policy's territory, and a module's document does not copy it.

<a id="s1"></a>
## The plugin skeleton

The text of the section "Plugin skeleton" of the template.

```text
const-<aspect-name>/
├── MODULE.md                # this document, filled in; never installed
├── README.md                # the landing page for a reader, from the template's README.md; of the root README's kind, binds nothing; never installed
├── plugin/                  # the plugin root, the only folder a project installs; its marketplace source ./modules/const-<aspect-name>/plugin
│   ├── .claude-plugin/
│   │   └── plugin.json      # manifest — the ONLY file inside .claude-plugin/; version 0.0.x while draft
│   ├── INSTALL.md           # install/uninstall notes; the pip command of the shared package at the tag of REQUIRES; the one CLAUDE.md pointer line if any
│   ├── requirements.txt     # optional; the libraries its scripts need, installed by one command
│   ├── skills/
│   │   └── <name>/          # optional; SKILL.md, and any file it names through ${CLAUDE_SKILL_DIR}
│   ├── commands/<name>.md   # optional
│   ├── agents/<name>.md     # optional
│   ├── hooks/hooks.json     # optional
│   └── scripts/             # optional; reference via ${CLAUDE_PLUGIN_ROOT}
│       ├── <entry>.sh       # the POSIX entry point each hook and the scan call; finds python3, then exec
│       ├── <entry>.py       # a Python entry file: FLOOR and REQUIRES, then C14, C15 and the version call, then its own package
│       ├── session-start.sh # optional, with session-start.py: the line of a gate whose dial leaves it examining nothing
│       ├── <grant>.sh       # optional, with <grant>.py: a grant's entry, the hook that answers allow for the module's own command
│       ├── print-skill-pointer.sh  # optional: the pointer line, at session start and, with --subagent, at a subagent's start
│       ├── effect-report.sh # optional, with effect-report.py: the effect report of §13, which hands the module's rules to the shared runner
│       └── <module>_gate/   # the module's own package: model, messages, checks, modes, start, dials, session
├── evals/<case>/case.yaml   # the eval cases, each naming its plugin (plugins: ../../plugin), scaffold.sh beside one that needs a project; evals/results/ ignored by git; never installed
└── tests/                   # conftest.py, test_<name>.py, test_shared_items.py; constitution_layer_kit linked from shared/, its testing/ the shared test files; <module>_gate from ../plugin/scripts/; one red→green fixture per gate ([law 7 of CLAUDE.md](../CLAUDE.md#law-7)); never installed
```

The template takes the same split: `module-template/plugin/` holds its parts that install, and `MODULE.md` and `README.md` stand beside it; it has no `tests/` and no `evals/`, which a module adds with its first gate and its first case. Kebab-case everywhere. Only plugin.json lives inside `.claude-plugin/`; every component directory sits at plugin root. Verify the manifest fields against the current plugin reference at authoring time. A module carries no license file: its manifest names the license, and the kit's `LICENSE` and `NOTICE` stand at the kit root alone. Linking both into each module is reopened as a decision once a module is mirrored or vendored outside the kit's marketplace.

<a id="s2"></a>
## The acceptance section, after its first sentence

The text of [section 10](MODULE.md#t10) of the template that follows its first sentence.

For each grant, the red→green fixture is its two halves: the forms its allowlist names, answered `allow`, and forms outside it answered with nothing — one value for each printable ASCII character the allowlist leaves out, a quote joined to a plain word, and another path — so that a character added to the allowlist by mistake turns the fixture red; and its exit-code split is its configuration failure, exit 1 with nothing granted, against its silence on a call outside the allowlist, exit 0. For each advisory rule: the boundary examples above stand as its acceptance. Each item labeled by verification kind: `fixture` (bare temp repo), `live` (the kit as consumer zero, or a consumer project, the plugin loaded from this repository), `eval` (a run of one of the module's eval cases on the pinned model, its result read from the kit's receipt, whose date, platform version and model are its evidence; one item per case, its "what it proves" cell naming the case as `` `evals/<case>/` ``), `review` (the human, at the one yes), `kit check` (a check the kit runs on the module from outside it, never shipped). A `live` item that proves a session's behaviour alone, and whose proof does not run in a consumer project, becomes an `eval` item where a case covers it whole: the `eval` item replaces it, and the proof it asks for is owed no more. Every other `live` item stays `live`, and the proof it asks for stays owed: one that no case covers whole, one that proves a scan over the kit's tree, and one whose proof runs in a consumer project, deferred or not. A scan item and a consumer-project item stay `live` because an eval runs in an empty folder, which a scaffold seeds where a case needs a project: it proves no scan over the kit's tree, and it runs in no consumer project.

<a id="s3"></a>
## The rows paragraph, after its first sentence

The text of the paragraph "Rows" of [section 10](MODULE.md#t10) of the template that follows its first sentence.

The `rows` cell links every matrix row the item proves, each to its anchor in the requirements document, or says `none` for an item that proves no row of the module — the hooks file's shape, the manifest, the install note. An item names a row only where it proves what the module's reading of that row in [§3](MODULE.md#t3) says the module ships. A fixture that checks an advisory row's carrier — a line a hook prints, a skill's description — names the row: it proves that the carrier is shipped and reads as written, never that the rule is followed, whose judgment is proved by the boundary examples at the review item. An `eval` item names each row whose reading names the skill, the pointer line or the start rule its case checks; a reading that ships such a carrier names it. The line of the shared items carries every row that a fixture item of the module, run through the same entry point — the script its hook or its scan calls — names, and no other row. Every row [§3](MODULE.md#t3) holds is named by at least one item. The item cell is handles and closed ranges, `T1–T4, T7`, a fixture item's handle being its test's number, bare or under `T` or `S`; the kind opens with `fixture` — `fixture, red→green` for a case record, `fixture, assertion` for a plain test, `fixture, shared` for the line of the shared items — or `kit check`, `live`, `live, deferred`, `eval` or `review`. An `eval` item is one item for one case: its "what it proves" cell names the case as the code span `` `evals/<case>/` ``, the folder's name of lowercase letters, digits and hyphens, every case folder of the module has an item, and no case has two. The kit's `scripts/check-aspects.py` holds this as a line of the gate list; with `--run` it runs the tests and gives each row the result of its items, a row's status derived on each run and stored nowhere (decision [dec-0054-acceptance-items-name-their-rows](../docs/decisions/dec-0054-acceptance-items-name-their-rows.md)); it reads an `eval` item's result from the module's receipt, and gives none where the receipt is not current; an `eval` item whose receipt is current counts as run, green when its last attempt passes and red when it does not, a run declared and not one the kit sees (decision [dec-0093-module-evals-with-local-receipts](../docs/decisions/dec-0093-module-evals-with-local-receipts.md)).

<a id="s4"></a>
## The handles paragraph, after its first sentence

The text of the paragraph "Handles" of [section 10](MODULE.md#t10) of the template that follows its first sentence.

A number once used is never used again: a removed item leaves a gap, and a shared item the module does not claim is left out of the shared line. A number that an accepted record or a frozen research comparison cites — an entry of [§4](MODULE.md#t4), a platform fact, a limit, a pair, a row of [§9](MODULE.md#t9), a step of the install note — is never moved and keeps the text the record cites: where this template's order, numbering or slots would move it, the module keeps the number and the text there, and the order yields.

<a id="s5"></a>
## The effect section, its three paragraphs

The paragraphs "Judge", "Ways" and "Code" of [section 13](MODULE.md#t13) of the template, which follow its table.

**Judge** *(template rule)*. A rule is judged by a deterministic pattern over what the project already holds — its transcripts, its gate logs and its git history — wherever a pattern can see it: `pattern`. It is judged by a fresh reader, a language model, only where no pattern can see it: `reader`. The report keeps the two judges' counts on lines of their own and never adds them together.

**Ways** *(template rule)*. A gate can be gone around four ways. B1, a path bypass: a file of the gate's territory changed with no hook of the gate examining it, through a shell write, a script, `git mv`, a merge or a checkout. B2, a switch-off: the module switched off for a clone, its severity lowered to warn, or one of its dials loosened. B3, a workaround after a red: after a block, the next act is another path to the same end, not the fix the message teaches; a red followed by the taught fix, with no human turn between them, counts as applied. B4, an escape: the invariant broken on the main branch anyway, as a later scan or the project's CI finds it. An advisory rule can be missed two ways. B5, a skill skipped: the act at the skill's moment with no load of the skill before it. B6, a shape missed: the rule's visible form absent where the rule asks for it.

**Code** *(template rule)*. The rules live in the module's package; the entry `effect-report.sh` and its Python entry file hand them to the shared runner, as item 10 of [kit-shared-gate-code §2](../shared/GATE.md#g2) says, and declare the release that adds it, `2.1.0`, or a later one, in `REQUIRES`. The entry is a row of [§9](MODULE.md#t9), `advisory`, with its reason in the row. The report blocks nothing, sets no threshold, and no check holds its numbers. A module that counts no rule yet writes `none` here, with its reason.

<a id="s6"></a>
## The enforcement section, after its first sentence

The text of [section 9](MODULE.md#t9) of the template between its first sentences and its table.

A scan over the tree is written in its row as a code span that reads exactly `<entry> --scan`, or `<entry>.py --scan` for an entry named by its Python file, nothing after the flag, so that the kit's `scripts/check-gate-lists.py` finds it and holds it in the kit's gate list, its CI list and the install guide's scan block. That check reads the table row by row, whatever a row's indent, each row opening `E<n>`, bold or not. A mode that is no tree scan is written `<entry> --scan --<flag> …` with the words `not a tree scan` in the same cell, outside a code span, and declares no scan. Any other code span in a row that holds `--scan`, and a span in the declared form in this section's prose, is a finding of that check. A deterministic check whose blocking is a dial is a `gate` with its severity dial named — the check is still deterministic. For a hook gate that dial is `severity` ([§7](MODULE.md#t7)): `warn` reports the finding and lets the write, or the turn's end, through — the adoption path onto a repository with legacy documents, or the path for a session that must not be asked to commit; the default `block` keeps the gate a gate.

<a id="s7"></a>
## The eval case row

The text of the row "eval case" of the table of [section 6](MODULE.md#t6) of the template, in its "carries" cell, after the cell's first sentence.

One case per skill: `tool_used` on `Skill`, a `regex` on the run's trace that no `Write` or `Edit` comes before the call that names it, and a grader on the work's result where the work leaves one, since the `regex` does not see a change made through `Bash`; where the skill's moment is a command, also `tool_order` putting the skill before it. One per command a rule makes mandatory, a script the module ships: `tool_used` on `Bash`, and a grader on what it did, a file it made or a line it printed, joined with its skill's case where the skill makes it mandatory at its own moment, the skill before the command; one per start rule that carries a rule of its own, `regex` where a pattern can see it and `llm` only where none can. A case lists the tools a session at its moment would have, so that the model can follow the skill as written: a skill or command case `Read`, `Glob`, `Grep`, `Write`, `Edit`, `Skill` and `Bash`, a start-rule case only what its rule needs. A run starts in an empty folder, which a scaffold seeds. The runner's three runs and threshold of 1 hold for every case, whatever a case sets: a case passes when every grader passes in every run. Each case is an `eval` item of [§10](MODULE.md#t10) (decision [dec-0093-module-evals-with-local-receipts](../docs/decisions/dec-0093-module-evals-with-local-receipts.md))

<a id="s8"></a>
## The boundary examples, the middle of the section

The text of [section 8](MODULE.md#t8) of the template between its first sentence and its last two.

A pair added after another in its group takes that pair's number with a letter, as [rule 8 of plc-0006-module-documents](../docs/policies/plc-0006-module-documents.md#r8) says of an added item; a pair that opens a group of its own takes the next unused number; a removed pair leaves a gap. A group of two pairs or more whose whole numbers run in order is a numbered list. A group of two pairs or more whose pairs carry a letter or skip a number writes each pair as a bullet that opens with its bold number, `- **3a.**`, so that each pair renders as an item of its own and no list's numbers jump, as the style scan asks. A group of one pair is a paragraph that opens with its bold number, since one item is no list. A pair sets one side against the other, each with its verdict: violates / complies, or, where both sides are allowed, the two outcomes, such as → routine / → recorded. Where the module has several advisory rules, the pairs stand in groups headed by the handles of the rules they serve, in bold; one group may serve several rules, and the groups may stand out of number order. Where a text the module ships, such as a skill's guide, already holds a rule's pairs, the section cites that text and does not copy it.

<a id="s9"></a>
## The hook row

The text of the row "hook" of the table of [section 6](MODULE.md#t6) of the template, in its "carries" cell, after the sentence that declares a grant.

A grant matches by an allowlist alone, never by a list of forms to refuse, since an answer of `allow` is given for the call as a whole and the platform does not split a compound command after it; it says nothing for a call outside the allowlist, so that the platform's own permission flow decides it; and when it cannot run it grants nothing: it exits 1 with its configuration failure and a closing line of its own, and the platform asks for the call as for any other (decision [dec-0110-new-document-command-granted-by-a-hook](../docs/decisions/dec-0110-new-document-command-granted-by-a-hook.md)). Text printed at session start does not reach a subagent, which starts with a context of its own; a pointer line of the skill row is also printed by a `SubagentStart` hook, as the event's `additionalContext` in one JSON object, since that event adds no plain stdout to the context; one script prints both forms, the subagent's on an argument. A gate whose own dial leaves it examining nothing — an empty list, an absent binding — prints one `SessionStart` line naming the module and the dial, for as long as the dial stays so, sized in characters in [§6](MODULE.md#t6): a silent zero read as coverage is the failure this rule exists for (decision [dec-0042-interaction-module-rulings](../docs/decisions/dec-0042-interaction-module-rulings.md#r3), R3)

<a id="s10"></a>
## The install note row

The text of the row "install note" of the table of [section 6](MODULE.md#t6) of the template, in its "carries" cell, after the sentence on the `CLAUDE.md` line.

Its steps follow the order of the template's install note: a step the module does not need is deleted and the steps after it are numbered on, and a step the module needs beyond them stands where its subject belongs; a step an accepted record cites keeps its number and its place, and the order yields there ([§10](MODULE.md#t10), the handles). Always-on rules ship via a `SessionStart` hook (see hook row), never via a pointer or a plugin-root `CLAUDE.md` (not loaded); a copy-into-CLAUDE.md fallback may be offered, labeled as manual and version-drifting

<a id="s11"></a>
## The rule on references from installed components

The paragraph of [section 6](MODULE.md#t6) of the template that follows the error-message slot.

**Installed components reference nothing in the kit** *(template rule)*. A skill, hook, script, command, agent, error text, or install note never cites the requirements document, the rollout plan, a matrix row, a decision record, a research comparison, or this document: consumers install the module without the kit, so every such reference dangles there. Rules are stated in those components in plain words; the reasoning lives here and in [§4](MODULE.md#t4).

<a id="s12"></a>
## The exit-code contract

The paragraph of [section 9](MODULE.md#t9) of the template that follows its table and its honest limits.

**Exit-code contract** *(template rule)* for every check: a finding (the repository is wrong) and a configuration failure (the checker is broken, a pinned tool is missing, the invocation is malformed) are distinct exit codes with distinct messages, so a reader never mistakes one for the other. A missing tool is loud, never a silent pass; a check that could not run reports that it could not run.
