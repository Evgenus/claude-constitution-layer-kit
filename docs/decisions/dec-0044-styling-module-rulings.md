---
id: dec-0044-styling-module-rulings
type: task-record
title: Rulings of the const-styling authoring — ten founding defaults in a style guide of its own kind, departures declared in the dials file, a scan of twelve signatures
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-styling authoring — ten founding defaults in a style guide of its own kind, departures declared in the dials file, a scan of twelve signatures

## Context

The module [`const-styling`](../requirements.md#const-styling) is authored from 2026-09-26 in the kit, ahead of its friction signal, as the decider chose in chat that day against the session's recommendation. Its rows are [requirement A9.1](../requirements.md#a9-1) to [requirement A9.4](../requirements.md#a9-4); its research comparison is [res-0009-const-styling](../research/res-0009-const-styling.md), which the decider widened with one question: beyond diagrams, which styling aspects should a defaults page rule on at founding — structure against narrative, list format, tables. The questions below were put to the decider in chat, one per message, each with lettered options; two of the decider's own questions in between — what the new policy would govern, and whether a departure in the dial makes a second statement of the defaults unnecessary — moved the design, and the answers are recorded where they bit. The record grows while the module is built and is `active` until the commit that names its yes. The kit's tree at the survey commit showed what the module absorbs: five fenced blocks with no language, three second level-one headings from one template, thirty-nine empty cells in one matrix, and uniformity elsewhere by habit alone.

## 1. Which work is next

The handoff of the previous session left the next work unchosen: the parked items of the audit plan, beginning with the name of the first consumer; a module; or a week under the kit's own gates.

- **A. The parked item D9 first,** the consumer's name and the date of Phase B, then the other parked items one per message.
  - **Pros:** D9 unblocks the deferred consumer-live proofs of all eight modules; the parked items are already argued and need only a yes.
  - **Cons:** it needs a fact only the decider holds, so the session halts until given; a day of process rulings produces no module.
- **B. The next module,** one of the three self-limiting modules waiting for a signal.
  - **Pros:** the routine is proven eight times and the tooling is in place.
  - **Cons:** none of the three has a friction signal in the commit notes, the condition the kit's guide names for growth; the module's consumer-live proof waits on D9 like the others.
- **C. A week of the kit under its own gates,** no new work, the prompts logged as friction.
  - **Pros:** answers the `warn` against `block` calibration with evidence.
  - **Cons:** a wait, not a task.

The session recommended A with C beside it. **R1.** B, chosen by the decider in chat on 2026-09-26; the session's objection stands: no self-limiting module had a friction signal in the commit notes, the condition [CLAUDE.md](../../CLAUDE.md) names for growth, and the module was started without one.

## 2. Which module

- **A. [`const-styling`](../requirements.md#const-styling).** One style-defaults document, founding entries, deviation reasons.
  - **Pros:** the smallest module, almost all advisory; no dial at founding by the specification; the kit's templates its consumer-zero objects.
  - **Cons:** the mechanics of a deviation and its detection had to be invented, a recorded ruling each; the kit holds almost no diagrams.
- **B. [`const-language`](../requirements.md#const-language).** Governed documents pass Vale with a pinned ruleset.
  - **Pros:** the strongest gate of the three; Vale installed on the authoring machine.
  - **Cons:** a third-party binary and package pins; a matrix row that says "in CI" before the kit has CI; nearly every kit document red on day one.
- **C. [`const-doc-budgets`](../requirements.md#const-doc-budgets).** A character-length gate per document kind.
  - **Pros:** the eight-times-proven shape on the shared code; the default examines nothing, as the two silent modules do; the kit's records its data.
  - **Cons:** a month of data before a ceiling binds, and the kit is twelve days old.

The session recommended C. **R2.** A, chosen by the decider in chat on 2026-09-26: [`const-styling`](../requirements.md#const-styling) is authored in the kit as consumer zero of its own documents, ahead of its slot in the rollout plan and of its signal; its consumer-live proof is a step of the consumer's bootstrap, and a finding there is a fix with a version bump, as [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) rules for the modules before it.

## 3. The founding set

The matrix row said exactly three founding entries and lazy accretion for the rest ([requirement A9.3](../requirements.md#a9-3)). The comparison's widened survey (section 6 of [res-0009-const-styling](../research/res-0009-const-styling.md)) found the kit's tree uniform on every aspect a linter checks, without a rule, and one judgment rule the guides converge on that no linter reaches.

- **A. The three as the matrix stands.**
  - **Pros:** no matrix edit; lazy accretion kept whole.
  - **Cons:** the aspect the guides agree on most, prose against list against table, stays unruled at the cost of one line.
- **B. Four: the three and structure against narrative.**
  - **Pros:** a judgment rule, so advisory with no gate; the kit's tree already keeps it; it decides the "when" of lists and tables.
  - **Cons:** one matrix edit; the "how" of lists and tables waits.
- **C. Six: B and the format of lists and of tables.**
  - **Pros:** the three aspects the decider named all founded; checkable by a linter later.
  - **Cons:** two entries born without a consumer's need.
- **D. Ten: C and headings, code blocks, emphasis and callouts** — every aspect the kit's tree is already uniform on.
  - **Pros:** a complete style page on day one; a linter configuration derivable from it; explicit over inferred.
  - **Cons:** the lazy-accretion rule hollowed at the module's own founding; seven entries with no consumer behind them.

The session recommended B. **R3.** D, chosen by the decider in chat on 2026-09-26, the session's objection noted: seven of the ten entries are born without a consumer's need, against [requirement A9.3](../requirements.md#a9-3). The founding entries are ten — Mermaid first with PlantUML only under a departure naming the missing capability; character drawings for trivial cases only, by pairs; pseudocode over formulas; prose against lists against tables; list format; table format; heading levels; code font and fence languages; emphasis; no callouts — each one sentence with its pairs in the guide; the matrix row [requirement A9.2](../requirements.md#a9-2) is edited to say so, its destination reading the guide in place of a policy, under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2). The aspects the comparison priced as lazy and the decider did not found — numbers and units, link text, source line length — enter under [requirement A9.3](../requirements.md#a9-3) when a document needs them.

## 4. The carrier

The defaults must reach a session at the moment of choice and have a home the consumer can accrete into.

- **A. A skill plus the guide's text shipped as a file.** The skill's description phrased by the activities before a departure — a diagram, prose against list against table, a formula, a fourth heading level or a callout, a template — its body the procedure; the text the consumer's guide is born from.
  - **Pros:** works on a bare repository with no configuration; the consumer's guide is the home of accretion; the pattern is shipped twice, the record template of module `const-decision-records` and the templates dial of module `const-locations`.
  - **Cons:** the entries exist in the shipped text and in the consumer's guide, which drifts by accretion — the relation of every template to its documents; the skill fires only when the model judges a choice is at hand.
- **B. The skill alone.**
  - **Pros:** one copy.
  - **Cons:** no home for accretion; the kit itself would have no guide.
- **C. A `SessionStart` line beside the skill.**
  - **Pros:** reaches every session.
  - **Cons:** ten entries with examples, about 1,500 characters, paid every session and compaction for rules that have a trigger, which the sibling comparisons placed in a skill's description.
- **D. The guide alone, no skill.**
  - **Pros:** one binding copy.
  - **Cons:** nothing brings it to the model at the moment of writing.

The session recommended A. **R4.** A, taken with the ruling of section 5 in chat on 2026-09-26 — the decider's questions moved the discussion to the home before a letter was given, and the home chosen there is A's shipped text as a document of its own kind: the module ships one skill, `style-defaults`, whose description names the moments before a departure and whose body is the procedure, and the guide's text as `skills/style-defaults/style-guide.md`, the file the consumer's guide is born from and the floor on a bare repository; no `SessionStart` line; the skill restates no default — it points at the guides the dial `guides` names and at the shipped file where none exists.

## 5. The home of the defaults

The comparison proposed a policy that claims nothing, a document in the root policy's territory with no namespace, which [kernel §3](../../kernel/CONVENTIONS.md#k3) names; the decider asked what such a policy would govern and whether one document under two policies breaks the kernel's rule. It governs nothing by resolution, and the rule holds; the honest description is a rules document homed among policies for want of another home, and the root policy's rule 5, "one kind", contradicts it.

- **A. A policy that claims nothing.**
  - **Pros:** one document; the kernel names the case.
  - **Cons:** a policy only by its address; rule 5 of the root policy to be amended or read around.
- **B. Rules of the root policy,** the defaults stated there and reaching every kind by governance.
  - **Pros:** no new document or kind; a kind born without a template is covered.
  - **Cons:** the policy for policies carries content rules that every consumer edits at `process` stakes; a module cannot write into a consumer's root policy, so the install is a paste.
- **C. A style guide, a document kind of its own with its own policy,** one document in a territory of one path, as the kit's intent page is; the module ships the guide's text.
  - **Pros:** every object is what the kernel says it is, nothing read around and nothing amended; the kit holds five kinds of one document already ([dec-0011-one-policy-per-kind](dec-0011-one-policy-per-kind.md)); the guide's policy states who guards what; accretion is an edit of a current-state document at the stakes its policy sets.
  - **Cons:** two documents in the consumer, the policy and the guide; the matrix row's word "policy" becomes "guide".
- **D. A kernel section.**
  - **Pros:** reaches everything.
  - **Cons:** the kernel is semantics, and the consumer cannot accrete into a page the kit ships.

The session recommended C. **R5.** C, chosen by the decider in chat on 2026-09-26: the style guide is a document kind of its own, one document in a territory of one path, governed by its own policy — in the kit [plc-0010-style-guide](../policies/plc-0010-style-guide.md) governing `docs/style-guide.md`, the guide created by hand from the module's shipped text; the matrix row [requirement A9.1](../requirements.md#a9-1) is edited to say so, and the destination of [requirement A9.3](../requirements.md#a9-3) and [requirement A9.4](../requirements.md#a9-4) reads the guide in place of a policy, under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2); a style guide never claims a territory beyond its own path, since a document resolving to two policies is the kernel's defect. **R6.** The binding is by governance, the session's proposal adopted with the ruling of section 6: the root policy asks every policy to carry a rule named "Style", saying that its kind's documents follow the style guides in the territory of the policy that governs the style guide and depart from a default only where the module's dial names a departure for their territory, with its reason; policies follow the guides as documents of their own kind; the guides are found through the module's dial `guides`, which the kit aliases to the style-guide policy's territory, and are never enumerated, so the root policy relies on no other policy; each policy's enforcement rule names the module's scan among its guards, and the style rule names no departure; a template carries no inheritance sentence — it complies with the guide or shows the departure its kind's entry allows.

## 6. Where a departure is declared

The decider rejected the comparison's marker — an HTML comment or a visible line before the deviating element — and every other inline form, and asked for approaches that mark nothing in the document; the connection of section 5 makes a departure a rule of the kind's policy, so the question became how the scan learns it and what a one-off document does.

- **A. Per kind only.** The kind policy's style rule is the declaration; the module's dial mirrors it for the scan; a one-off is a defect or an amendment of the kind's rule.
  - **Pros:** the reason lives where rules live; no document carries markup.
  - **Cons:** a real one-off has no path but amending the whole kind's rule.
- **B. Per kind, and one-offs by path in the dial.** An entry naming one document, its signatures and its reason.
  - **Pros:** the one-off has a machine-read home with its reason; a second entry for the same signature is the signal that promotes it, the path of [requirement A9.3](../requirements.md#a9-3).
  - **Cons:** the dials file names a document; a stale entry survives its document until the scan reports it.
- **C. Per kind, and one-offs as commit notes.** The scan reports a signature outside its dial as a note, never red; the reason is the routine line in the commit.
  - **Pros:** zero markup, zero dial entries.
  - **Cons:** the gate-lite becomes advisory in fact; the reason is in history, and the tree holds current truth.

The session recommended B. **R7.** B, chosen by the decider in chat on 2026-09-26, with the decider's own finding that nothing then needs to be stated twice: every departure is an entry of the dial `departures` of module `const-styling` — `paths` a pattern for a kind or one document by its path, `allow` the signature keys, `reason` one required line, never two — and nothing in a document marks it; a kind's policy may keep the documents of its kind finished before its style rule out of the scan's territory by number range, saying so — in the kit the records accepted before this one and the comparisons frozen before this module's, which stand as written; a kind policy's style rule is one fixed sentence that restates no departure, the guide lists none, and the skill restates no default; an entry with an empty reason, an unknown key or a malformed shape is a configuration failure naming it; an entry matching no covered document is a note on every scan, never a finding.

## 7. The signatures the scan knows

The scan is `--scan` only, over an own `territories` dial, red on a trace in a territory where no entry allows it — the mechanism the comparison recommended (b5 of [res-0009-const-styling](../research/res-0009-const-styling.md)) — and with ten founding entries several defaults have a mechanical trace.

- **A. Diagrams and formulas only.** A `plantuml` or `puml` fence, `@startuml`, a `math` fence, a `$$` line: four signatures.
  - **Pros:** the two rows' own gate-lite; the kit green on day one.
  - **Cons:** seven founding entries with a trace go unchecked.
- **B. Every line-shaped signature of the ten entries.** A and: an alert line, a heading of level four or deeper, a fence without a language, a bullet marker other than a dash, emphasis by underscores: nine.
  - **Pros:** every entry with a one-line trace held; each a fixed string or one expression with a fixture; the kit's own tree the proof, five fences and one heading to fix.
  - **Cons:** nine fixtures; the marker and emphasis checks flag forms some consumers prefer.
- **C. B and the multi-line shapes.** A skipped heading level, a second level-one heading, a table row with the wrong number of cells or an empty cell, an ordered list out of sequence.
  - **Pros:** the fullest coverage the entries allow.
  - **Cons:** parser state across lines, the class the reviewers probe for rounds; a third-party linter's territory.

The session recommended B. **R8.** C, chosen by the decider in chat on 2026-09-26, the session's objection noted: the scan knows twelve signatures — `plantuml`, `formula`, `callout`, `deep-heading`, `skipped-level`, `second-h1`, `fence-language`, `list-marker`, `list-numbering`, `underscore-emphasis`, `table-columns`, `table-empty-cell` — the closed vocabulary of the dial's `allow`, each defined by its line shape or its multi-line state in the module's document, and claims nothing beyond them. **R9.** The scan has no hook mode and no `severity` dial, and the module ships no hook: run as a hook it is its own configuration failure; the shared fixture subject is widened with `scan_only`, defaulting to what the other modules pass, so that the shared items run through a gate without a hook mode.

## Carry list

1. R1 — history only: the choice of the day, the objection noted in the commit that started the branch.
2. R2 — [§2](../../modules/const-styling/MODULE.md#t2) of the module's document, the entry trigger the kit started ahead of by the decider's choice, and [§10](../../modules/const-styling/MODULE.md#t10), item L4, the deferred consumer-live proof; the choice itself history only.
3. R3 — [requirement A9.2](../requirements.md#a9-2), the ten entries; [the style guide](../style-guide.md#d1), entries d1 to d10; [§3](../../modules/const-styling/MODULE.md#t3) of the module's document, the reading of that row; [§12](../../modules/const-styling/MODULE.md#t12), item 5, the aspects left lazy.
4. R4 — [§6](../../modules/const-styling/MODULE.md#t6) of the module's document, the skill and text rows and the always-on slot; [the skill](../../modules/const-styling/skills/style-defaults/SKILL.md), its first section.
5. R5 — [requirement A9.1](../requirements.md#a9-1), [requirement A9.3](../requirements.md#a9-3) and [requirement A9.4](../requirements.md#a9-4), their destination; [rule 1 of plc-0010-style-guide](../policies/plc-0010-style-guide.md#r1) and [rule 4](../policies/plc-0010-style-guide.md#r4); [§3](../../modules/const-styling/MODULE.md#t3) of the module's document, the reading of that row, and [§11](../../modules/const-styling/MODULE.md#t11), the kernel section relied on.
6. R6 — [rule 9 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r9) and its [rule 8](../policies/plc-0001-root-policy.md#r8), which names the scan among the guards of policies, as the enforcement rule of every kind policy does; [the policy template](../../templates/policy.md), whose style slot every new policy fills; the style rule of every kind policy, [rule 9 of plc-0002-kernel](../policies/plc-0002-kernel.md#r9), [rule 8 of plc-0003-intent-page](../policies/plc-0003-intent-page.md#r8), [rule 16 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r16), [rule 11 of plc-0005-research](../policies/plc-0005-research.md#r11), [rule 13 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r13), [rule 10 of plc-0007-requirements](../policies/plc-0007-requirements.md#r10), [rule 9 of plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r9), [rule 10 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r10), [rule 6 of plc-0010-style-guide](../policies/plc-0010-style-guide.md#r6); [§3](../../modules/const-styling/MODULE.md#t3) of the module's document, the reading of [requirement A9.1](../requirements.md#a9-1).
7. R7 — [§7](../../modules/const-styling/MODULE.md#t7) of the module's document, the dial `departures`; [rule 4 of plc-0010-style-guide](../policies/plc-0010-style-guide.md#r4); [the style guide](../style-guide.md), its closing section; [the skill](../../modules/const-styling/skills/style-defaults/SKILL.md), its first and third sections; the kit's own entry and its `territories` in `constitution.yaml`; the number ranges in [rule 16 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r16), [rule 11 of plc-0005-research](../policies/plc-0005-research.md#r11) and [rule 9 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r9).
8. R8 — [§7](../../modules/const-styling/MODULE.md#t7) of the module's document, the twelve signatures, and [§9](../../modules/const-styling/MODULE.md#t9), row E1 and the limits.
9. R9 — [§6](../../modules/const-styling/MODULE.md#t6) of the module's document, the hook row, the entry-file rows and the shared-code row, and [§7](../../modules/const-styling/MODULE.md#t7), its opening line; [kit-shared-gate-code §2](../../shared/GATE.md#g2), items 1, 6, 7 and 8, and [§5](../../shared/GATE.md#g5), the items a gate without a hook mode leaves out.
