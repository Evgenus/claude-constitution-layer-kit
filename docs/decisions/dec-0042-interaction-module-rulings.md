---
id: dec-0042-interaction-module-rulings
type: task-record
title: Rulings of the const-interaction authoring — answer in the shape of the question, assumptions and lists addressable, one gate on destructive commands
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

## Carry list

1. R1 — the "not a project" bullet of [INTENT.md](../../INTENT.md), which names the kit consumer zero of the session conduct its own guide states, and [§2](../../modules/const-interaction/MODULE.md#t2) of the module's document, which states the entry trigger; the done sentence of step 9 of the rollout plan is written when the module lands; the sentence on the parked consumer item is history only, a scheduling call of the day.
2. R2 — the hook row and the always-on slot of [§6](../../modules/const-interaction/MODULE.md#t6) of the module's document, its [§12](../../modules/const-interaction/MODULE.md#t12) item 1 for the deferred style, and the fallback step of its install note.
3. R3 — the hook row and the always-on slot of [§6](../../modules/const-interaction/MODULE.md#t6) of the module's document, which states the line; the two siblings' lines are work to come, held by step 9 of the rollout plan until each lands.
4. R4 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10).
