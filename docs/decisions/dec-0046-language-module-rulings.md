---
id: dec-0046-language-module-rulings
type: task-record
title: Rulings of the const-language authoring — Vale under the dials, grade 10 and 25 words by default, a hook after the write and a scan, the chat row settled, frozen documents out by territory
status: active
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-language authoring — Vale under the dials, grade 10 and 25 words by default, a hook after the write and a scan, the chat row settled, frozen documents out by territory

## Context

The module [`const-language`](../requirements.md#const-language) is authored from 2026-09-26 in the kit, ahead of its friction signal, as the decider chose in chat that day against the session's recommendation. Its rows are [requirement A10.1](../requirements.md#a10-1) and [requirement A10.2](../requirements.md#a10-2), and it takes the mechanism of [requirement A9.4](../requirements.md#a9-4), module `const-styling`'s row; its research comparison is [res-0010-const-language](../research/res-0010-const-language.md), a survey of the enforcement instruments the decider asked for in those words — Vale and its packages, textlint, proselint, write-good, alex, LanguageTool, Harper, Hemingway, the readability formulas and their libraries, an LLM as judge — with experiments over the kit's own tree. The questions below were put to the decider in chat, one per message, each with lettered options; the pick was the letter, as the kit's preferences ask. Every ruling is stated in the module's document and the kit's documents the carry list names; this record holds the options and the reasoning.

## 1. Which work is next, and which module

The handoff of the previous session left the next work unchosen.

- **A. The parked item D9 first,** the consumer's name and the date of Phase B, then the other parked items one per message.
  - **Pros:** D9 unblocks the deferred consumer-live proofs of all nine modules; the items are argued and need only a yes.
  - **Cons:** a session of process rulings produces no module.
- **B. A week of the kit under its own gates,** the prompts logged as friction.
  - **Pros:** answers two open questions with evidence.
  - **Cons:** a mode to hold while doing other work, not a plan.
- **C. The next module,** `const-language` or `const-doc-budgets`.
  - **Pros:** the routine is proven nine times and the tooling is in place.
  - **Cons:** neither module has a friction signal, the condition [CLAUDE.md](../../CLAUDE.md) names for growth.

The session recommended A with B beside it. C was chosen; then, between the two modules, the session recommended `const-doc-budgets` — deterministic, Python only, its measuring pass the data its own row asks for — over `const-language`, whose binary is a new dependency class and whose thresholds had no data behind them. **R1.** `const-language`, chosen by the decider in chat on 2026-09-26 with the words "perform proper research of enforcement instruments in internet"; the session's objection stands: no self-limiting module had a friction signal, and the module was started without one.

## 2. The instrument and the home of its thresholds

The comparison found Vale the one runnable instrument with a configurable grade ceiling, a per-sentence word limit, code-aware Markdown reading, machine-readable output and byte-identical repeat runs; the question was where its thresholds live.

- **A. Vale, the rules shipped in the plugin, the configuration generated from the dials on each run.** The consumer installs the binary; the gate refuses below 3.23.0 with the install command, writes a temporary configuration from the module's namespace before every run and passes `--config` and `--no-global`.
  - **Pros:** one calibration surface, the dials file; zero configuration on an empty repository; nothing pinned or synced inside the module; a developer's home configuration never changes what CI sees.
  - **Cons:** a generator inside the gate; the first external binary in a kit module.
- **B. Vale with a consumer-maintained `.vale.ini` and rule files in the consumer's tree,** the module's dial naming the territories alone.
  - **Pros:** cheaper; the layout every editor integration knows.
  - **Cons:** the thresholds live outside the dials file, against the row's "thresholds → binding"; two surfaces; a consumer with no file gets nothing.
- **C. No binary: a Python gate computing the grade and the sentence length on text it strips itself.**
  - **Pros:** every kit gate stays at Python and PyYAML.
  - **Cons:** the module owns Markdown stripping, where the comparison measured gaps of twenty grades between raw and stripped text; the row says "pass Vale".

The session recommended A. **R2.** A, chosen by the decider in chat on 2026-09-26: the gate generates Vale's configuration and one style from the dials into a temporary directory per run, reads it with `--config` and `--no-global`, ships its two founding lists and its passive pattern in the plugin, syncs and pins nothing, and refuses a `vale` that is missing or below 3.23.0 with the install command, as the shared failure shape for a missing dependency; the specification's "pin packages by release URL" becomes the consumer's route for packages of its own, outside the module. **R3.** The rules are five, each with a level in the dial `levels` — `error` a finding, `warning` a note, `off` unwritten — and every rule off is refused, since a gate that checks nothing would report green as if it had checked; the founding lists are extended by the dials `forbidden` and `simpler` and trimmed by `exceptions`, which refuses a phrase no list holds. **R4.** The envelope is blanked before Vale reads, so a title or an id is not prose and the envelope stays the sibling gate's; a Vale comment outside code is blanked and reported as a finding, since a departure is declared in the dials file and never marked in the document, and one inside a fence or a code span is a mention Vale does not honour and is left as it stands.

## 3. The default grade ceiling and the kit's own value

On the kit's tree at the survey, 38 of 109 documents read above grade 10 by Vale's Flesch–Kincaid, 12 above 12, 4 above 13; 13 of the 38 are frozen records and comparisons that no rule allows editing.

- **A. Module default 10; the kit's own dial 10.**
  - **Pros:** one number everywhere; the kit lives under the rule it ships from day one.
  - **Cons:** 25 current-state documents rewritten inside this module's work, the kernel among them, and a kernel edit is a recorded change with the full carry audit.
- **B. Module default 10; the kit's dial 13 now, lowered in steps as a follow-up.**
  - **Pros:** the consumer default is the strict one; the kit-live proof rewrites the three worst documents, real proof of the loop; the rest wait for a work item of their own.
  - **Cons:** the kit ships a module whose default it does not yet meet, said openly.
- **C. Module default 12.**
  - **Pros:** the kit nearly meets it.
  - **Cons:** 12 is where the kernel and the policies read, the documents a non-native reader finds hardest; a consumer with no calibration would get a ceiling that flags almost nothing.

The session recommended B. **R5.** B, chosen by the decider in chat on 2026-09-26: the module's default `grade_ceiling` is 10, exclusive as Vale computes it; the kit's own is 13, and its descent — 12, then 10 — is a work item after this module, one step per change with its audit, named in the rollout plan.

## 4. The default sentence limit and the kit's own value

On the kit's current-state documents at the survey, frozen ones out: 1,365 sentences over 25 words in 58 documents, 621 over 40, 235 over 60, 42 over 100 in 17 documents, the longest 261.

- **A. Module default 25; the kit sets the rule's level to `warning` until its rewrite.**
  - **Pros:** 25 is the one published number; the kit sees every finding from day one.
  - **Cons:** a warning that is never red is a list nobody fixes.
- **B. Module default 25; the kit's own limit 100 now, lowered in steps as a follow-up.**
  - **Pros:** the same ladder as the grade; a red the kit can meet today; each later step its own rewrite.
  - **Cons:** the kit's value stands far from the default for a while, said openly.
- **C. Module default 40.**
  - **Pros:** an eighth of the kit's sentences instead of a third.
  - **Cons:** no public guidance names 40.

The session recommended B. **R6.** B, chosen by the decider in chat on 2026-09-26: the module's default `sentence_words` is 25, exclusive, a heading being a sentence; the kit's own is 100, and its descent — 60, then 40, then 25 — is the same work item as R5's. **R7.** Two routine calls the decider did not object to: the consumer extends the two lists through the dials, since the gate generates the rules from them; a consumer's own Vale style admitted by path waits for a consumer's signal, deferred in the module's document.

## 5. The enforcement moment

- **A. Both at founding: the `--scan` over the territories and a `PostToolUse` hook on `Write` and `Edit`,** the findings handed back after the write, exit 2 under `severity: block` and `additionalContext` under `warn`, no write refused.
  - **Pros:** the teaching loop a linter exists for, at 0.24 s per document; the shared pipeline already reads a file after a write; every other document gate of the kit ships a hook and a scan.
  - **Cons:** the block and warn shapes of the post-write channel get their own fixtures; a document with dozens of findings exceeds the platform's cap, so the hook shows the first twenty and the count line says so.
- **B. The scan alone at founding; the hook when a consumer session asks.**
  - **Pros:** the scan satisfies the row as written; a smaller module.
  - **Cons:** a red found at the commit gate is the slow loop; a post-write hook is the one thing Vale's own plugin ships.

The session recommended A. **R8.** A, chosen by the decider in chat on 2026-09-26: the plugin wires `PostToolUse` on `Write|Edit` and ships the scan; there is no `PreToolUse` entry, since a document-wide rule before the write refuses every partial fix, and the gate judges a `PreToolUse` payload the same way only where a consumer wires it; after a write the hook shows at most twenty findings, or fewer than fill 8,000 characters, and its count line names the total and the scan.

## 6. Where the plain-chat row lives

The matrix held [requirement A10.2](../requirements.md#a10-2) under module `const-interaction` with a dagger and a note asking whether it moves to [`const-language`](../requirements.md#const-language). The comparison applied the three boundary tests — the same invariant; no shared enforcement moment, a reply being no file; no shared lifecycle trigger — and rejected the one measurement possible, Vale over the last reply at `Stop`, as judgment dressed as a check.

- **A. Settle it now: the row is `const-interaction`'s.** The dagger and the question leave the matrix; this module's document names the chat half as the other half of one aspect.
  - **Pros:** the question has an answer from the tests the matrix names; a flag left standing is a deferred question.
  - **Cons:** a consumer may one day find the split confusing, and the row would move back by a record.
- **B. Leave the flag until a consumer reports the split as confusing.**
  - **Pros:** no matrix edit inside this module's work.
  - **Cons:** every reader of the matrix re-asks a closed question.

The session recommended A. **R9.** A, chosen by the decider in chat on 2026-09-26: the row's destination is module `const-interaction`, the boundary note settled, and this module ships nothing for chat.

## 7. Sentence-case headings as this module's first rule

The comparison overturned the graduation of the twelve markup signatures of module `const-styling` — all expressible in Vale, five only as scripts, but the departures dial with its reason has no Vale form and a second home per rule crosses [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) and [law 3 of CLAUDE.md](../../CLAUDE.md#law-3) — and kept the path for rules about words, sentence-case headings first.

- **A. Not at founding.** The module ships the rules of its own rows; its document records the shape and the path.
  - **Pros:** a heading-case rule is no row of the module's aspect, so shipping it is scope creep; the styling guide holds sentence case as a default already, but no consumer has asked for the rule; the rule needs an exception list with no signal behind it.
  - **Cons:** the graduation path stays a described shape with no rule proving it.
- **B. Ship it at founding.**
  - **Pros:** one word rule proves the path end to end.
  - **Cons:** the same two laws, and a rule before its default puts the gate ahead of the guide.

The session recommended A. **R10.** A, chosen by the decider in chat on 2026-09-26: no heading-case rule at founding; the twelve signatures stay the styling scan's, and the graduation path is read as the path for rules about words, deferred in the module's document with its signal.

## 8. The kit's own calibration

No option was put: the kit's dial follows the rulings above and the precedent of module `const-interaction`'s dial, and the session made the calls below as the kit-live proof showed the numbers. **R11.** The kit's accepted records and frozen comparisons leave this gate's territory by negated patterns over their number ranges, since an accepted record is never edited and this gate has no per-document declaration — the route [dec-0045-frozen-documents-stay-in-the-style-scan](dec-0045-frozen-documents-stay-in-the-style-scan.md) closed for the style scan is open here, that record ruling the style scan alone; the ranges grow with each acceptance, this record's own number among them. **R12.** The kit's passive rule is `off`, not `warning`: the day-one scan printed 1,224 passive notes over 64 documents, every sampled one a passive chosen — the register of the kit's documents — and a note nobody reads on every scan is noise, not a warning; a consumer's default stays `warning`. **R13.** Every policy's enforcement rule names this gate among the guards of its kind, after a write and in its scan, as it names the style scan; no policy carries a language rule of its own, since the thresholds live in the dials file and not in a policy.

## Carry list

1. R1 — history only: the choice of the day, the objection noted in the commit that started the branch.
2. R2 — [§3](../../modules/const-language/MODULE.md#t3) of the module's document, the reading of its row; [§6](../../modules/const-language/MODULE.md#t6), the package, binary and dependencies rows; [§7](../../modules/const-language/MODULE.md#t7), what the gate hands to Vale.
3. R3 — [§7](../../modules/const-language/MODULE.md#t7) of the module's document, the dials `levels`, `forbidden`, `simpler` and `exceptions`; [§5](../../modules/const-language/MODULE.md#t5), the invariant's reading of a level.
4. R4 — [§7](../../modules/const-language/MODULE.md#t7) of the module's document, what the gate hands to Vale; [§6](../../modules/const-language/MODULE.md#t6), the message L6; [§9](../../modules/const-language/MODULE.md#t9), limit 6.
5. R5 — [§7](../../modules/const-language/MODULE.md#t7) of the module's document, the dial `grade_ceiling`; [the kit's dials file](../../constitution.yaml), its `const-language.grade_ceiling` and the comment beside it; the descent is planned in step 9 of the rollout plan.
6. R6 — [§7](../../modules/const-language/MODULE.md#t7) of the module's document, the dial `sentence_words`; [the kit's dials file](../../constitution.yaml), its `const-language.sentence_words` and the comment beside it; the descent is planned in step 9 of the rollout plan.
7. R7 — [§7](../../modules/const-language/MODULE.md#t7) of the module's document, the dials `forbidden` and `simpler`; [§12](../../modules/const-language/MODULE.md#t12), item 3.
8. R8 — [§6](../../modules/const-language/MODULE.md#t6) of the module's document, the hook row; [§9](../../modules/const-language/MODULE.md#t9), rows E1 and E2 and limit 4; [§12](../../modules/const-language/MODULE.md#t12), item 5.
9. R9 — [requirement A10.2](../requirements.md#a10-2), its destination, and the boundary note of the requirements document; [§3](../../modules/const-language/MODULE.md#t3) of the module's document, the row's reading; [§11](../../modules/const-language/MODULE.md#t11).
10. R10 — [§3](../../modules/const-language/MODULE.md#t3) of the module's document, the reading of [requirement A9.4](../requirements.md#a9-4); [§12](../../modules/const-language/MODULE.md#t12), item 1.
11. R11 — [the kit's dials file](../../constitution.yaml), its `const-language.territories` and the comment beside them; [§8](../../modules/const-language/MODULE.md#t8) of the module's document, pair 6; [rule 6 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6) and [rule 10 of plc-0005-research](../policies/plc-0005-research.md#r10), the clause on their frozen documents.
12. R12 — [the kit's dials file](../../constitution.yaml), its `const-language.levels.passive` and the comment beside it.
13. R13 — [rule 8 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r8) and the enforcement rule of every other policy under `docs/policies/`, each naming the gate.
