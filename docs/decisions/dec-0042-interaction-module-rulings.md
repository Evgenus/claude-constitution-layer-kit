---
id: dec-0042-interaction-module-rulings
type: task-record
title: Rulings of the const-interaction authoring — answer in the shape of the question, assumptions and lists addressable, a gate on destructive commands and a scan of list handles
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-interaction authoring

## Context

The module [`const-interaction`](../requirements.md#const-interaction) is authored from 2026-09-25 in the kit, ahead of its Phase C slot in the rollout plan, as the decider chose in chat that day: the kit is consumer zero of its own session conduct — the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md) carries by hand five of the module's rules, "Lead with the answer", "Restate before acting", "Assumptions are always explicit", "Every list item is addressable" and "Honesty over agreement", and the "Refuse destructive moves without a spoken confirmation" bullet is the class the module's one gate holds. Its rows are [requirement A7.1](../requirements.md#a7-1) to [requirement A7.5](../requirements.md#a7-5), [requirement A8.1](../requirements.md#a8-1) to [requirement A8.3](../requirements.md#a8-3) and [requirement A10.2](../requirements.md#a10-2); its research comparison is [res-0008-const-interaction](../research/res-0008-const-interaction.md). Two parked process items of the audit of 2026-09-22 touch the module's always-on carrier and are ruled here with it: the visible zero of an off-by-default module, and the kit loading its own plugins per clone. The questions below were put to the decider in chat, one per message, each with lettered options; the record grows while the module is built and is `active` until the commit that names its yes.

## 1. Which work is next, and where the module is authored

The handoff of the previous session left the next work unchosen: the module, or the parked items of the audit plan first, beginning with the name of the first consumer.

- **A. [`const-interaction`](../requirements.md#const-interaction), with the two carrier items folded in.** The answer-shape rules on an always-on carrier, the escalation rows after `const-questions` took the asking side, and a `PreToolUse` gate on enumerated destructive commands; the visible-zero and the marketplace items ruled as its first decisions.
  - **Pros:** the daggered rows are cheaper now that the asking side has a home; the assumptions and addressable-lists rules cut from the sibling's skill have a home waiting; the two carrier items are settled where they bite.
  - **Cons:** the module carries the kit's first gate on the shell tool, whose hook surface changed since it was last surveyed; the marketplace item inside the module widens its record.
- **B. The parked items first**, beginning with the name of the first consumer and the date of Phase B, one per message, before any new module.
  - **Pros:** a consumer name unblocks the consumer-live proofs seven modules defer to the bootstrap; the parked items stop accumulating.
  - **Cons:** nothing ships; most parked items are process and several depend on this module's carrier, so they would be ruled without the module that exercises them.

The session recommended A. **R1.** A, chosen by the decider in chat on 2026-09-25: [`const-interaction`](../requirements.md#const-interaction) is authored in the kit as consumer zero, like the seven modules before it, ahead of its Phase C slot — the kit having passed the module's entry trigger with five guide bullets on one theme; its consumer-live proof is a step of the consumer's bootstrap, and a finding there is a fix with a version bump, as [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) rules for the four. The consumer's name stays a parked item, put to the decider in one message at any point.

## 2. The always-on carrier of the advisory rules

Nine rules that govern every reply, with no trigger — unlike the sibling's asking rules, which a decision triggers. The comparison ran a control and three carriers headless (section 1 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)): the control led with the word but listed no assumption and used unhandled bullets; the hook and the forced style each produced the assumption block and the handles.

- **A. A `SessionStart` hook, no matcher, printing the rules** in about 1,200 characters, declared advisory; the output style not shipped.
  - **Pros:** reaches the model on startup, resume, clear and compaction; stacks with a sibling's line and overrides nothing; the platform's documented always-on carrier for a plugin; measured live under the 10,000-character cap.
  - **Cons:** the rules cost their characters every session; the text is invisible in the transcript, so the user never sees it.
- **B. A plugin output style with `force-for-plugin: true`,** the same rules in the system prompt.
  - **Pros:** a cached system-prompt slot; the same live shape as A.
  - **Cons:** one slot for the whole session: it overrides the user's own style and the first forced plugin wins silently.
- **C. A plus an unforced output style** shipped beside it, selectable under the plugin's name.
  - **Pros:** costs nothing while unselected.
  - **Cons:** two copies of the rules kept in step on every bump; nothing measured says a consumer needs it.
- **D. No carrier: the install note instructs copying the rules into the consumer's guide.**
  - **Pros:** zero runtime; the user sees the rules.
  - **Cons:** the manual, version-drifting path the specification names only as the fallback; what the kit does today, the friction the module absorbs.

The session recommended A. **R2.** A, chosen by the decider in chat on 2026-09-25: the module's advisory rules ride on one `SessionStart` hook with no matcher, printed to stdout as plain text, declared advisory, sized in characters in the module document; the install note offers the copy-into-guide fallback labelled manual and version-drifting; an unforced output style is deferred with its signal.

## 3. The visible zero of a gate whose dial leaves it examining nothing

Item D3 of the audit of 2026-09-22: two shipped gates examine nothing by default — `catalogs` of module `const-catalogs` and `record_policies` of module `const-decision-records` are empty lists — and say so nowhere a session sees. This module's gate ships a non-empty default, so its zero arises only when a consumer writes an empty list to switch the gate off while keeping the carrier. The comparison verified that a `SessionStart` line reaches the model and not the transcript, the reverse of a `systemMessage`, and measured two plugins' lines stacking at about sixty characters for the zero (p1, p3 and a4 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)).

- **A. The rule kit-wide, applied here now, the siblings in follow-up routine changes.** A gate whose own dial leaves it examining nothing prints one line at `SessionStart` naming the dial, while it stays so; this module adds the line to its hook; the two siblings each gain a `SessionStart` hook in a routine change naming this record, held pending in the rollout plan.
  - **Pros:** one rule for every module, stated once; no state file, no shared-code change, no manifest bump before publication.
  - **Cons:** two follow-up changes with a fixture each; a pending item until they land.
- **B. This module only.** The siblings wait for their own records.
  - **Pros:** the smallest change.
  - **Cons:** the two silent modules stay silent; the same ruling made three times.
- **C. Refuse an empty list,** so this module never has a zero; the item stays parked for the siblings.
  - **Pros:** nothing to print.
  - **Cons:** a consumer who wants the carrier without the gate has no way but a pattern that matches nothing.
- **D. A `systemMessage` on the first matched write of a session,** with a marker file, the audit's original.
  - **Pros:** appears where the gate would have acted.
  - **Cons:** reaches the user and never the model; needs state.

The session recommended A. **R3.** A, chosen by the decider in chat on 2026-09-25: a gate whose own dial leaves it examining nothing prints one line at `SessionStart`, naming the module and the dial, for as long as the dial stays so — a line to the model, sized in characters in the module's document; this module's hook prints it while `destructive` is an empty list; the two modules that examine nothing by default each gain the line in a routine change naming this record, after this module lands.

## 4. How the kit's own sessions load its plugins

Item D7 of the audit of 2026-09-22: the kit's sessions load no plugin unless started with one `--plugin-dir` flag per module, so the kit runs ungated by its own gates. Verified on 2026-09-25 against the settings reference and the marketplace page: a marketplace's plugin entries take relative paths from the marketplace root and load in place; a `directory` marketplace source in a settings file needs an absolute path, so a committed settings file cannot point at its own clone; enabling a plugin in project settings installs it for nobody else, so each clone installs once; the comparison's experiment E8 ran the whole path offline (p13 and p14 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)).

- **A. A marketplace file at the kit root, project settings enabling every module, one setup step per clone.** `.claude-plugin/marketplace.json` with a relative entry per module; `.claude/settings.json` with `enabledPlugins` only; the clone setup script registers the clone as a marketplace and installs each plugin at project scope, idempotently, its `--check` reporting; implemented on its own branch after this module lands, then the session-conduct block of the kit's guide trims to what no module carries, the routine edit [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md) R2 names.
  - **Pros:** every kit session runs under its own gates without flags; plugins load in place so the links survive; verified headless; the marketplace file is what Phase D publishes.
  - **Cons:** one more per-clone step, the registration in the user's settings; the kit's gates then fire in every kit session.
- **B. Keep `--plugin-dir` by hand,** the guide listing the flags.
  - **Pros:** nothing new to maintain.
  - **Cons:** sessions run ungated unless someone types eight flags; the trim never triggers.
- **C. A, with the registration written by the setup script into `.claude/settings.local.json`** instead of the user's settings.
  - **Pros:** nothing of the kit touches the user's global settings.
  - **Cons:** the `directory` source in a local settings file is documented for development only and its in-place loading is unverified by any run.

The session recommended A, with C tried during the implementation. **R4.** A, chosen by the decider in chat on 2026-09-25: the kit loads its own plugins per clone through a marketplace file at its root, relative entries, one per module; the project's settings file enables each; the clone setup script registers the marketplace and installs the plugins once per clone; the work is a routine change on its own branch after this module lands, held by step 10 of the rollout plan, and the local-settings form of C replaces the user-settings write there if one headless run proves it loads in place; the marketplace is named `constitution-kit`.

## 5. Whether the addressable-lists scan ships

The row's optional gate-lite, "a script flagging unnumbered multi-item lists in governed documents". The comparison measured the kit's tree (section 2 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)): of 215 bullet lists, 150 open every item with a handle of the kit's forms, 65 do not, and of those 13 are plain — the rest open with a bold label, a link or a code span that is the item's key, or are pro/con pairs under a lettered option; the kit's own session-conduct block, the rule's home, is among the hits. A scan can decide that an item opens with a token of a handle grammar, not that a bold label or a file name is a stable key, which the rule allows.

- **A. Not shipped; the rule stays on the carrier,** the scan's shape recorded with its signal.
  - **Pros:** no false-positive rate to tune; the module stays one hook and one gate; no consumer has cited an item it could not name.
  - **Cons:** the row's optional half unbuilt.
- **B. Ship a scan-only check** on the shared code, over an own `territories` dial and a `handles` dial of regular expressions defaulting to the six forms measured, one finding per list, fences never counted.
  - **Pros:** the module's second deterministic slice from day one; the grammar is the consumer's to widen.
  - **Cons:** red on 13 to 65 of the kit's own lists depending on what counts as a key; the claim "every item has a handle" is not what the scan can prove.
- **C. Ship it as a hook and a scan,** the standard shape, on `Write` and `Edit` of a Markdown file.
  - **Pros:** catches the list at the keystroke.
  - **Cons:** blocks every draft list mid-work on a heuristic.

The session recommended A. **R5.** B, chosen by the decider in chat on 2026-09-25: the check ships in this version as a `gate` with a scan mode only — a second entry point of the module beside the shell gate, its hook mode never wired and answering that it is not, so the shared code is not widened — over the dials `territories` and `handles` of the module's own namespace, a finding per list naming the first item without a handle, a list inside a fenced block never counted, the message claiming no more than that an item opens with no token of the grammar; the kit's own exemptions are ruled after the first scan on the kit's tree, never before, as [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md) R4 learned. The session's objection stands: the measurement found no consumer friction, and the rule allows keys the grammar cannot see, so the scan is red on prose the rule permits until the grammar or the territory is tuned.

## 6. The pattern language of the destructive-command dial

The comparison bypassed the hook's `if` field live with `git -C . push --force`, so the gate runs on every `Bash` call and reads the command itself, with the platform's own split — separators, substitutions, `bash -c` strings, wrappers stripped, a program path reduced to its base name, git's global options before the verb skipped (d2, d3, d10 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)); its own probe regex missed the `-C .` form.

- **A. Structured entries on the tokens.** `command` words, a `flags` set, `teach` and `alternative` texts; a flag matched anywhere after the verb, inside a cluster too, a long flag by equality; an entry with no `flags` matches the words alone.
  - **Pros:** readable and addressable in the dials file; the alternative beside the pattern; no regular expression to get wrong.
  - **Cons:** an argument value cannot be named at this version; a second shape beside the lists scan's grammar.
- **B. A regular expression per entry** over the normalised subcommand.
  - **Pros:** the most expressive; what three of the four community guards use.
  - **Cons:** opaque; the survey's probe caught the alternative it recommended; a typo silently matches nothing.
- **C. The platform's `Bash(...)` glob.**
  - **Pros:** one grammar a consumer knows.
  - **Cons:** prefix-shaped; `--force-with-lease` cannot be excluded; the grammar whose blind spots the live run showed.

The session recommended A. **R6.** A, chosen by the decider in chat on 2026-09-25: the dial `destructive` is a list of entries `{command: [<words>], flags: [<flags>], teach: <why>, alternative: <the reversible way>}`, matched on the tokens of every subcommand of the `Bash` command after the platform's own split — separators, `$()` and backticks, the string after `bash -c` or `sh -c`, a leading assignment and the wrappers stripped, a program path reduced to its base name, git's global options before the verb skipped; a short flag matched inside a cluster, a long flag by equality; an entry with no `flags` matched on its words alone; an argument-value form deferred with its signal; the scan mode explains a command given as `--scan --command <text>`.

## 7. The confirmation mechanism

The live runs (d4 to d6, E4, E5, E11 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)): a hook answering `permissionDecision: "ask"` makes the platform prompt the user with the reason, labelled with the plugin, forced even in auto mode since 2.1.211; headless, the same answer is a denial whose reason the model sees, and the model reported the block and waited, under every permission mode tried. A hook exiting 2 is a denial the model sees as an error, and the model rerouted to the alternative on its own.

- **A. `ask`, with the three-part teaching text as the reason.** The human's yes is the platform's own prompt; unattended, a denial the model reports and waits on; exit 0 with the JSON, exit 0 plainly for an unlisted command.
  - **Pros:** the only option that puts the yes in a human hand; one yes covers one act by construction; the prompt is the platform's, labelled with the plugin.
  - **Cons:** headless, the ask is a block; the prompt itself is proven live only; the shared report path needs an `ask` verdict beside block and warn.
- **B. Exit 2 with the teaching text, the user re-runs by hand.**
  - **Pros:** the block every kit gate uses; the usual red→green fixture.
  - **Cons:** the model re-runs, as the live run showed, and the second run is blocked again unless the hook remembers, which needs a marker file.
- **C. A confirmation word or an environment marker.**
  - **Pros:** works headless.
  - **Cons:** the model can add it alone; the yes is not in a human hand.

The session recommended A. **R7.** A, chosen by the decider in chat on 2026-09-25: a `Bash` command matching an entry is answered with `permissionDecision: "ask"` and the entry's three-part teaching text as the reason — what matched, why the act is hard to reverse, the reversible alternative — at exit 0; an unlisted command passes at exit 0 with nothing printed but the green line; under `severity: warn` the match is reported in the JSON form the sibling gates use and the command runs, the adoption path; no `updatedInput` at this version, a rewrite deferred with its signal; the shared report path gains the `ask` verdict as a widening that defaults to what the other modules pass.

## 8. The default destructive-command list

The comparison proposed a list (d13 of [res-0008-const-interaction](../research/res-0008-const-interaction.md)); two of its entries do not fit the token entries of R6 — a SQL statement stands inside a quoted argument, one token after the split, and `git checkout -- .` needs the argument form deferred there.

- **A. The comparison's list whole,** SQL included, matched by a special case inside quoted arguments.
  - **Pros:** the widest net on day one.
  - **Cons:** a second matching mechanism for two entries; a database command belongs to the tool that runs it, not to the shell tokens.
- **B. The token-expressible list, each entry with its alternative:** `git push` with `--force`/`-f`; `git reset` with `--hard`; `git checkout` with `-f`/`--force`; `git restore` whole; `git clean` with `-f`/`--force`; `git branch` with `-D`; `git stash drop` and `git stash clear`; `git rebase` whole; `git filter-branch`, `git filter-repo`, `git reflog expire`, `git gc` with `--prune=now`; `rm` with `-r`/`-R`/`--recursive`. Outside the list and said so: `git commit --amend`, a plain push, `rm` of one file, `git checkout -- .`, deletion through a file tool, SQL through any client.
  - **Pros:** every entry the grammar states exactly; the alternative beside each.
  - **Cons:** `git rebase` and `git restore` prompt on common, recoverable acts; a consumer who rebases work branches daily tunes the list on day one.
- **C. A minimal list:** the force push, the hard reset, the clean, the branch delete and the recursive remove only.
  - **Pros:** prompts only on the acts nearly everyone calls destructive.
  - **Cons:** a rebase and a discarded working tree pass in silence, the two acts the kit's own guide names first.

The session recommended B. **R8.** B, chosen by the decider in chat on 2026-09-25: the default of the dial `destructive` is the entries of B — fourteen, listed there in ten groups — each with its teaching text and its reversible alternative written in the module's document; what the list leaves out is named there and in the gate's own words; SQL is no shell gate's default.

## Carry list

1. R1 — the "not a project" bullet of [INTENT.md](../../INTENT.md), which names the kit consumer zero of the session conduct its own guide states, and [§2](../../modules/const-interaction/MODULE.md#t2) of the module's document, which states the entry trigger; the done sentence of step 9 of the rollout plan is written when the module lands; the sentence on the parked consumer item is history only, a scheduling call of the day.
2. R2 — the hook row and the always-on slot of [§6](../../modules/const-interaction/MODULE.md#t6) of the module's document, its [§12](../../modules/const-interaction/MODULE.md#t12) item 1 for the deferred style, and step 6 of [its install note](../../modules/const-interaction/INSTALL.md), the fallback.
3. R3 — the hook row of [template §6](../../module-template/MODULE.md#t6), which states the rule for every module, and the hook row and the always-on slot of [§6](../../modules/const-interaction/MODULE.md#t6) of the module's document, which states this module's line; the two siblings' lines are work to come, held by step 9 of the rollout plan until each lands.
4. R4 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10).
5. R5 — the row of [requirement A7.5](../requirements.md#a7-5) in [§3](../../modules/const-interaction/MODULE.md#t3) of the module's document, the rows `territories` and `handles` of its [§7](../../modules/const-interaction/MODULE.md#t7), and its scan row in [§9](../../modules/const-interaction/MODULE.md#t9); the session's objection, history only.
6. R6 — the row `destructive` of [§7](../../modules/const-interaction/MODULE.md#t7) of the module's document, its [§5](../../modules/const-interaction/MODULE.md#t5), which states the reading of a command, and its [§12](../../modules/const-interaction/MODULE.md#t12) for the deferred argument form.
7. R7 — the row `severity` of [§7](../../modules/const-interaction/MODULE.md#t7) of the module's document, the row E1 of its [§9](../../modules/const-interaction/MODULE.md#t9), its [§12](../../modules/const-interaction/MODULE.md#t12) for the deferred rewrite, and the verdicts of [kit-shared-gate-code §3](../../shared/GATE.md#g3) for the widening.
8. R8 — the row `destructive` of [§7](../../modules/const-interaction/MODULE.md#t7) of the module's document, which lists the default entries, and the honest limits of its [§9](../../modules/const-interaction/MODULE.md#t9), which name what the list leaves out.
