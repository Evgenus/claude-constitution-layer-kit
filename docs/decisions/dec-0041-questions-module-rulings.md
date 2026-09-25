---
id: dec-0041-questions-module-rulings
type: task-record
title: Rulings of the const-questions authoring — ask at recorded stakes or a blocker, one decision per message in the fixed shape, no open question in a deliverable
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-questions authoring

## Context

The module [`const-questions`](../requirements.md#const-questions) is authored from 2026-09-25 in the kit, ahead of its Phase C slot in the rollout plan, as the decider chose in chat that day: the kit is consumer zero of its own session conduct — the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md) is the interim carrier of the module's rules, and the kit's history holds the friction signal the specification asked for, six commits on the shape of one decision message in two days (commits 1534dd8, 064da57, 1df97d1, cffa57f, ff06c3f, f73393a). Its rows are [requirement A6.1](../requirements.md#a6-1) to [requirement A6.9](../requirements.md#a6-9); its research comparison is [res-0007-const-questions](../research/res-0007-const-questions.md). The questions below were put to the decider in chat, one per message, each with lettered options; the record grows while the module is built and is `active` until the commit that names its yes.

## 1. Which module, and where it is authored

The handoff of the previous session left the next module unchosen: two self-limiting modules had their friction signal observed, and the plan lists the consumer's bootstrap before either.

- **A. [`const-questions`](../requirements.md#const-questions).** The ask-vs-decide skill with its contrastive pairs, the per-decider preferences dial, and the optional gate-lite scan of delivered documents for open-question markers.
  - **Pros:** its signal is the best documented in the repository, six commits on the decision format alone; a skill plus one deterministic scan keeps the record small; the boundary rows of [`const-interaction`](../requirements.md#const-interaction) are easier to rule once this module exists.
  - **Cons:** almost entirely advisory, so its live proof is a headless-run reading rather than a red→green fixture; the scan's territory is a design decision the kernel does not settle.
- **B. [`const-interaction`](../requirements.md#const-interaction).** The answer-shape and assumptions skill on the `SessionStart` carrier, plus a `PreToolUse` gate on destructive commands.
  - **Pros:** a genuine hook gate with a red→green fixture; part of its research already exists; the visible zero of an off-by-default module gets settled there.
  - **Cons:** three parked items of the audit plan must be ruled before or inside it, so the record is larger and slower; its signal is observed but less counted.
- **C. No module yet.** Name the first consumer and the date of Phase B, and take the parked process items first.
  - **Pros:** the plan lists Phase B before Phase C, and one parked item changes how a module is proven live in the kit.
  - **Cons:** the accumulating set is complete and every consumer-live proof already sits at step 5 of the plan, so nothing blocks a module; the parked items are each short and can be taken when they bite.

The session recommended A. **R1.** A, chosen by the decider in chat on 2026-09-25: [`const-questions`](../requirements.md#const-questions) is authored in the kit as consumer zero, like the six modules before it, ahead of its Phase C slot — the kit being consumer zero of the session conduct its own guide states, and having passed the module's entry trigger; its consumer-live proof is a step of the consumer's bootstrap, and a finding there is a fix with a version bump, as [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) rules for the four. The parked items of the audit plan stay parked and come to the decider one per message when one blocks a step.

## 2. The session-conduct block of CLAUDE.md once the skill exists

The block carries today, by hand, the rules this module ships as a skill. The kit's own sessions load no plugin unless started with `--plugin-dir`, one flag per module.

- **A. The block stays whole; the skill is proven beside it.** The record states that the block is the kit's own copy of the rules, kept until the kit loads its plugins per clone.
  - **Pros:** no kit session loses the rules; the block also carries the branch, commit and reference rules, which are owed to no module; the trim is earned by the parked item on how the kit loads its own plugins.
  - **Cons:** the same rules stand in two places for a while, and a change to the format is made in both.
- **B. Trim the block now to what the module does not carry, with one pointer line to the module.**
  - **Pros:** one home for the asking rules from the day the module lands; the kit dogfoods its carrier at once.
  - **Cons:** a kit session started without the flag has no asking rules at all — the state that earned the module; a pointer line is the drifting install path the template discourages.
- **C. Replace the block's question lines with the copy-into-CLAUDE.md fallback the install note offers,** labelled manual and version-drifting.
  - **Pros:** proves the fallback path on the kit, which no consumer has yet.
  - **Cons:** a lower-fidelity carrier chosen over the skill just built; the label invites the drift it warns of.

The session recommended A. **R2.** A, chosen by the decider in chat on 2026-09-25, with the decider's addition: the kit's harness — the session-conduct block and the rest of what [CLAUDE.md](../../CLAUDE.md) carries by hand — is replaced by the made modules later, once the kit loads its own plugins per clone; until then the block stays whole and carries the rules itself, and what a module carries leaves the block at that replacement, as a routine edit that names this record.

## 3. Whether the open-question scan ships

The row's optional gate-lite, "a script scanning deliverables for open-question markers". The comparison measured the kit's tree: zero code markers on 94 Markdown files, and of eight `[decide:` hits three are the draft module's own legitimate markers and five the documents that define the marker's syntax (section 5 of [res-0007-const-questions](../research/res-0007-const-questions.md)).

- **A. Record and wait.** The rule advisory in the skill; the scan's shape recorded, its signal a consumer's commit note about a marker in a delivered document.
  - **Pros:** no consumer has hit it and the kit's own hits are false positives; no script, no fixture wave; the module stays the pure prose the live runs proved.
  - **Cons:** the row's optional half unbuilt; a marker in a delivered document is caught by its reader alone until the signal.
- **B. Ship the scan now.** A deterministic check on the shared code, own territory and marker dials, reporting file and line and claiming only "no marker left".
  - **Pros:** the module's one deterministic slice exists from day one; the kit runs it as consumer zero.
  - **Cons:** on the kit it is green by construction after the exemptions; the message must disclaim in every run that a prose deferral is invisible.
- **C. A named command in the skill, no script.** The skill's delivery step names one git-native command over the deliverable's files with the marker set.
  - **Pros:** a self-check at the cost of one line; nothing claimed as a gate.
  - **Cons:** the model may skip the command and nothing shows it did; the marker set fixed in prose.

The session recommended C. **R3.** B, chosen by the decider in chat on 2026-09-25: the check ships in this version, a `gate` with its territory and its marker set as dials of the module's own namespace, its message claiming no more than that no marker was left. The session's objection stands: the measurement found no consumer friction, and the kit's own corpus turns the check red only in its fixtures.

## 4. The shape of the check

Whether the check is a hook and a scan, the standard shape of every kit gate, or a scan alone, which the comparison recommended and which needs the shared code widened for a gate with no event.

- **A. Hook and scan, the standard shape.** A `PreToolUse` hook on `Write` and `Edit` judges the written document when it lies in the `territories` dial; `--scan` walks the tree; `severity` as every hook gate; the kit exempts its drafts and the documents that quote the syntax by negated patterns.
  - **Pros:** no shared change, every shared item runs as for the six modules; the marker is caught at the keystroke, where the model writes `TBD` instead of asking; `warn` is the adoption path; the red→green fixture is the natural one.
  - **Cons:** the kit exempts `modules/*/MODULE.md` while any module is a draft, so its module documents are unseen until publication; a working draft inside the territory is blocked mid-work unless the consumer sets `warn` or excludes it.
- **B. Scan only, the shared code widened.** The hook mode optional in the shared command line, a run without `--scan` a misinvocation, the fixture subject widened for a gate with no event, no `severity`.
  - **Pros:** matches the row's words and the comparison's recommendation; no write is ever blocked.
  - **Cons:** widens four shared parts and the shared page for one module; a red arrives only when the scan is run; the drafts need the same exemptions, since the scan sees them too.

The session recommended A. **R4.** A, chosen by the decider in chat on 2026-09-25, with the session's defaults accepted: the marker set is `[decide:`, `TODO`, `TBD` and `FIXME`, matched case-sensitively and, where a marker begins or ends with a word character, at a word boundary there; `???` and `[open]` left out for having matched nothing but a quoted glob; a marker inside a code span or a fenced block is a quotation the check never reports; exemptions are negated patterns inside the `territories` dial and no second dial, the shape of `const-referencing`; the kit's own territory is every Markdown file git lists, minus `templates/**` and `module-template/**`, which are no deliverables, and minus a draft module document by its own path while it carries open slots — the first scan on the kit found the documents that quote the marker's syntax need no exemption once the quotations stand in code, and found no reason to hide six finished module documents behind a wildcard, which corrected the session's two defaults before the yes. A document with no dials file, in either mode, is the shared visible skip naming the file.

## Carry list

1. R1 — the "not a project" bullet of [INTENT.md](../../INTENT.md), which names the kit consumer zero of the session conduct its own guide states, and [§2](../../modules/const-questions/MODULE.md#t2) of the module's document, which states the entry trigger; the done sentence of step 9 of the rollout plan is written when the module lands.
2. R2 — the opening sentence of the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md), which states that the block carries the rules itself until the made modules replace the kit's harness.
3. R3 — the row of [requirement A6.7](../requirements.md#a6-7) in [§3](../../modules/const-questions/MODULE.md#t3) of the module's document, and the rows E1 and E2 of its [§9](../../modules/const-questions/MODULE.md#t9); the session's objection, history only.
4. R4 — the rows `territories`, `markers` and `severity` of [§7](../../modules/const-questions/MODULE.md#t7) of the module's document, and the `const-questions` namespace of the kit's `constitution.yaml`, which carries the kit's territory.
