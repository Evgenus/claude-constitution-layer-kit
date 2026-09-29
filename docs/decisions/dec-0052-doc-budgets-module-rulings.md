---
id: dec-0052-doc-budgets-module-rulings
type: task-record
title: Rulings of the const-doc-budgets authoring — ceilings per group of paths, warning below 30 days of data, a character defined in the kernel, a green hook's notes handed to the model
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-doc-budgets authoring — ceilings per group of paths, warning below 30 days of data, a character defined in the kernel, a green hook's notes handed to the model

## Context

The module [`const-doc-budgets`](../requirements.md#const-doc-budgets) is authored from 2026-09-28 in the kit, the eleventh and last module of the set. The decider asked for it in the handoff of that day. Its rows are [requirement A11.1](../requirements.md#a11-1), [requirement A11.2](../requirements.md#a11-2) and [requirement A11.3](../requirements.md#a11-3); its research comparison is [res-0011-const-doc-budgets](../research/res-0011-const-doc-budgets.md). The questions below were put to the decider in chat, one per message, each with lettered options; the pick was the letter, as the kit's preferences ask. Sections 1 to 3 were decided on 2026-09-28, the rest on 2026-09-29. Every ruling is stated in the documents the carry list names; this record holds the options and the reasoning.

## 1. Start without the signal

The specification says the module enters "when bloat is observed, with data", and the row asked for a month of data; the kit had two weeks, and no commit note had named length as a problem.

- **A. Start now, measure and report only,** no ceiling until a month of data.
  - **Pros:** breaks no row; the report builds the data the row needs.
  - **Cons:** still machinery before a signal; the gate row is not met until a second step.
- **B. Start now, with ceilings from two weeks of data,** at warning, blocking later.
  - **Pros:** the module is complete against its rows in one round.
  - **Cons:** breaks the month the row asked for; ceilings from a tree still growing fast may soon be wrong.
- **C. Wait for the signal** and a month of data.
  - **Pros:** follows the growth rule of [CLAUDE.md](../../CLAUDE.md) exactly.
  - **Cons:** the set stays incomplete; the growth of the session guide stays unmeasured.

The session recommended A. **R1.** B, chosen by the decider in chat on 2026-09-28; the session's objection stands: no friction signal on document length existed, the condition the guide names for growth.

## 2. How B meets the month of the row

B set ceilings from less data than the row asked for, while the specification's "Ships" line allowed a ceiling before a month so long as it did not block.

- **A. Amend the row in writing:** a ceiling from less than the data asked warns, and blocks only on that much data.
  - **Pros:** explicit; the row and the specification agree.
  - **Cons:** a row change to audit; the data rule weakens for warnings.
- **B. Keep the words, read them as covering blocking ceilings only.**
  - **Pros:** no edit of the requirements.
  - **Cons:** a reading the row's own words contradict.
- **C. Keep the row, record the two-week ceilings as an exception.**
  - **Pros:** the row keeps its strength.
  - **Cons:** the module breaks its own row at its first yes.

The session recommended A. **R2.** A, chosen by the decider in chat on 2026-09-28: [requirement A11.3](../requirements.md#a11-3) now says that a ceiling set from fewer than 30 days of data only warns, and blocks only on 30 days or more.

## 3. What a ceiling is keyed by

Forty of the kit's 128 Markdown files lay in no policy's territory, the session guide and every skill among them.

- **A. Path patterns in the module's own namespace,** a kind's territory reached by a YAML alias.
  - **Pros:** reads only its own dials; reaches every file; the pattern of four shipped gates.
  - **Cons:** a consumer without anchors writes a kind's patterns twice.
- **B. The document kind, resolved through the policies.**
  - **Pros:** matches the row's word "kind".
  - **Cons:** reads keys outside its namespace; misses the 40 files; meets the resolution defects a sibling reports.
- **C. The meta-type, from the envelope.**
  - **Pros:** the row's literal "one per meta-type".
  - **Cons:** loose for small kinds, the kernel allowed 5.4 times its length; files without a type get nothing.
- **D. Path patterns with an optional filter on the meta-type.**
  - **Pros:** covers A and a meta-type where wanted.
  - **Cons:** a feature nothing asks for yet.

The session recommended A. **R3.** A, chosen by the decider in chat on 2026-09-28: a ceiling is an entry of the dial `ceilings` whose `paths` name its documents in the dials file's dialect; the module reads no policy and no envelope, and [requirement A11.2](../requirements.md#a11-2) now names a group of documents by path patterns, a document kind or any other group.

## 4. The phrase "one per meta-type at most"

Under path keys the phrase capped the number of ceilings, and the kit's data proposed ten groups.

- **A. Replace it in writing,** in the same amendment as section 2: each ceiling covers a named group and is set from that group's data; how many there are is review.
  - **Pros:** explicit; fits the key of section 3.
  - **Cons:** drops a limit on how many ceilings exist.
- **B. Keep the cap of three,** one per meta-type.
  - **Pros:** the row's words stand.
  - **Cons:** small kinds nearly unbounded; the files with no meta-type break the cap.
- **C. Keep the words, read them as covering the first calibration.**
  - **Pros:** no edit.
  - **Cons:** a reading; the day-one set breaks the words.

The session recommended A. **R4.** A, chosen by the decider in chat on 2026-09-29: [requirement A11.3](../requirements.md#a11-3) says each ceiling is set from observed data of the group it covers, and the cap is gone.

## 5. When the check runs

The check reads one number per file; the kit's whole scan took about 0.2 s.

- **A. A scan only.**
  - **Pros:** the least code.
  - **Cons:** the model learns of an excess only when someone scans.
- **B. A `PostToolUse` hook on `Write|Edit` and the scan.**
  - **Pros:** the model is told at the moment it makes a document longer; the kit's pattern.
  - **Cons:** more code; a warning after a write must travel as `additionalContext`; a document already over is reported after every write.

A gate before the write was rejected in the comparison, since it would refuse every partial cut. The session recommended B. **R5.** B, chosen by the decider in chat on 2026-09-29: the hook measures the written document after the write and never refuses it; the scan measures every held document; every policy's enforcement rule names the gate, after a write and in its scan.

## 6. How the warn-then-block steps are held

The shared `severity` says how a finding travels after a write, and the scan ignores it; a scan red in the first month would block before the data the amended row asks for.

- **A. A level per ceiling, set by hand;** review holds the month.
  - **Pros:** the simplest dial.
  - **Cons:** no check holds the amended row.
- **B. A level per ceiling and the window of data as two dates;** the gate refuses `error` on a short window.
  - **Pros:** the rule is a check of the dials alone, one verdict for one tree on any day.
  - **Cons:** the dates are declared, not proven.
- **C. A date per ceiling from which it blocks, read against the clock.**
  - **Pros:** the step to blocking is automatic.
  - **Cons:** a verdict that changes with no commit.
- **D. The window worked out from git history.**
  - **Pros:** nothing declared falsely.
  - **Cons:** a shallow clone changes the verdict; a walk of history at every write.

The session recommended B. **R6.** B, chosen by the decider in chat on 2026-09-29: each ceiling has a `level`, `warning` a note that is never red, `error` a finding, and a `window` of two dates; a ceiling at `error` on a window shorter than 30 days is a configuration failure at every read; the shared `severity` keeps its one meaning.

## 7. What a month is

- **A. A calendar month,** a rule for the days that do not exist.
  - **Pros:** matches the word.
  - **Cons:** an edge rule and its fixture.
- **B. 30 days,** `to` minus `from`.
  - **Pros:** one subtraction, no edge case; the row and the check say the same.
  - **Cons:** one more word of the row changes.
- **C. 31 days.**
  - **Pros:** never shorter than a calendar month.
  - **Cons:** an odd number needing its reason.

The session recommended B. **R7.** B, chosen by the decider in chat on 2026-09-29: the row says 30 days, and the gate checks `window.to` minus `window.from` against 30.

## 8. Two ceilings over one document

- **A. Every matching ceiling applies,** the lowest deciding.
  - **Pros:** no order; each finding names its ceiling.
  - **Cons:** a broad entry cannot be relaxed by a narrower one.
- **B. The first entry wins.**
  - **Pros:** a narrow entry first gives a sub-group more room.
  - **Cons:** the verdict hangs on the list's order; the higher number carries no reason.
- **C. An overlap is a configuration failure.**
  - **Pros:** one ceiling per file, nothing unclear.
  - **Cons:** the hook sees the written file alone; useful set-ups are ruled out.

The session recommended A. **R8.** C, chosen by the decider in chat on 2026-09-29: a document two ceilings hold is a configuration failure — in the hook for the written file, in the scan, the history report excepted, for the first such file in path order — and [requirement A11.2](../requirements.md#a11-2) says one ceiling per document at most.

## 9. A file that is not valid UTF-8

- **A. Count it,** each replacement character the decoder puts in one.
  - **Pros:** every sibling gate reads files so; no rule beyond the rows.
  - **Cons:** a damaged file gets a length and no warning.
- **B. Refuse it** with a finding naming the offset.
  - **Pros:** no damaged file passes quietly.
  - **Cons:** a rule no row asks for; a second way of reading files.

The session recommended A. **R9.** A, chosen by the decider in chat on 2026-09-29: bytes that are not valid UTF-8 count one per replacement character that a decoder following the Unicode standard's recommended practice puts in their place — one for each maximal subpart of an ill-formed subsequence, as the shared code already reads them.

## 10. Where the definition of a character lives

The kernel said sizes are characters and never said what one is, while the template's always-on budget and the shared code's cut count characters too.

- **A. In this module's document only.**
  - **Pros:** no kernel change.
  - **Cons:** the other counts keep an undefined unit; a concept two modules need is the kernel's.
- **B. In [kernel §7](../../kernel/CONVENTIONS.md#k7),** one sentence; the module cites it.
  - **Pros:** the kernel's own word defined where it is used.
  - **Cons:** a kernel change, always recorded, and a larger audit.

The session recommended B. **R10.** B, chosen by the decider in chat on 2026-09-29: a character is one Unicode code point of the file read as UTF-8, a CRLF line ending counts as one, nothing is normalized or left out, with the clause of R9; [requirement A11.1](../requirements.md#a11-1) points there.

## 11. How one document is let over a ceiling

An accepted record or a frozen comparison takes only the edits its policy lists; the kit's pattern keeps such a document in a gate's territory with a reason ([dec-0045-frozen-documents-stay-in-the-style-scan](dec-0045-frozen-documents-stay-in-the-style-scan.md), [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md)).

- **A. A `departures` dial in the siblings' shape,** `paths`, `allow`, `reason`.
  - **Pros:** the kit's shipped pattern; one wording across three gates.
  - **Cons:** a lifted document has no limit; the parser is written a third time.
- **B. No departures: an exception is a ceiling of its own,** the broad entry negating its paths, a reason on every entry.
  - **Pros:** every document keeps a limit; no third parser.
  - **Cons:** a shape unlike the siblings'.

The session recommended B. **R11.** A, chosen by the decider in chat on 2026-09-29: an entry of the dial `departures` lifts the ceilings it names for the documents it matches, with a one-line reason; it names only ceilings that exist; an entry that lifts nothing — it matches no document a ceiling it names holds — is a note on every scan; the kit's dial holds none, every ceiling sitting above its frozen documents. The two policies with frozen documents say that such a document over its ceiling is brought under it by the wording edits its policy allows where they reach it, and otherwise stays as it is and is declared so, as R3 of [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md) rules for every later threshold.

## 12. How the observed data is shown

- **A. A note per ceiling on every scan.**
  - **Pros:** almost no code.
  - **Cons:** today only, no growth over the window.
- **B. The notes and a history report,** `--scan --since <date>`, over git history, judging nothing, refusing a shallow clone.
  - **Pros:** the 30 days the row asks for, counted as the gate counts.
  - **Cons:** the most code; a mode that judges nothing.
- **C. The notes and a git command in the skill.**
  - **Pros:** no history code.
  - **Cons:** its count can drift from the gate's, `wc -m` counting bytes under some locales.

The session recommended B. **R12.** B, chosen by the decider in chat on 2026-09-29: every scan prints one note per ceiling — what it holds, how many a departure lifts, the longest of the others and its margin — and the report prints per day and per ceiling the longest document on the first-parent line of HEAD, then each ceiling's window with the rule of R13, and exits 0.

## 13. How a ceiling's number is derived

A number some documents break on its first day is a target for the rest; wording edits had lengthened frozen documents by up to 1.5 %.

- **A. The window's longest plus 10 %, rounded up to 1,000.**
  - **Pros:** no document over on the first day; the backtest's rule.
  - **Cons:** soon used up by a kind still growing.
- **B. The same with 5 %.**
  - **Pros:** tighter.
  - **Cons:** uneven after rounding; more warnings.
- **C. A percentile.**
  - **Pros:** one outlier does not set the number.
  - **Cons:** documents over it on day one.
- **D. No rule.**
  - **Pros:** freedom.
  - **Cons:** numbers nobody can repeat.

The session recommended A. **R13.** A, chosen by the decider in chat on 2026-09-29: the rule of thumb is the window's longest document plus 10 %, rounded up to a multiple of 1,000; the number is review, the module teaching the rule and the report printing it. The window's longest is read as its longest committed version, a stated assumption of the session.

## 14. The kit's own ceilings

- **A. The ten groups of the comparison,** fourteen files left without a ceiling.
  - **Pros:** measured and backtested.
  - **Cons:** the requirements, the rollout plan and the intent page unbounded.
- **B. The ten groups and groups for the other files,** every Markdown file under one ceiling.
  - **Pros:** no gap in coverage.
  - **Cons:** more entries.
- **C. The session guide only.**
  - **Pros:** the smallest set.
  - **Cons:** the kit tests one entry.

The session recommended B. **R14.** B, chosen by the decider in chat on 2026-09-29: eighteen ceilings, at `warning` with the window 2026-09-14 to 2026-09-29, each number the rule of R13 applied to the report over that window, hold all 129 Markdown files of the tree, one each; kinds with an anchored territory are reached by alias, and six policy territories gained an anchor for it.

## 15. How a warning note after a write reaches the model

The hooks page says the plain stdout of most events goes to the debug log; headless runs on 2026-09-29 confirmed it for `PostToolUse` and `PreToolUse`, and confirmed that `additionalContext` arrives. The shared `green_hook` printed its notes plain, so the warning notes of module [`const-language`](../requirements.md#const-language) never reached the model; the shared warn channel would label a note as a finding.

- **A. Widen the shared green** to hand notes over as JSON after a write, for every gate.
  - **Pros:** the protocol stays shared; one fix for both modules.
  - **Cons:** a larger change and audit, touching siblings.
- **B. This module writes its own JSON.**
  - **Pros:** a smaller change.
  - **Cons:** protocol code in a module, written twice.
- **C. The shared warn channel for a warning.**
  - **Pros:** no new code.
  - **Cons:** a false text; a note counted as a finding.

The session recommended A. **R15.** A, chosen by the decider in chat on 2026-09-29: a green hook run on a write event with notes — `green_hook`, or `skip` given the event's name — prints one JSON object whose `additionalContext` holds the notes and the green line; a run without notes, and a scan, print as before; the shared item S159 proves it.

## 16. The dial names

The names others will type were put as a default to accept or override: `ceilings` of `name`, `paths`, `max`, `level`, `window.from` and `window.to`, and `departures` of `paths`, `allow`, `reason`. **R16.** The default, accepted by the decider in chat on 2026-09-29.

## 17. How far the fix of section 15 reaches

Two more gates handed notes to `green_hook` before a write, [`const-meta-types`](../requirements.md#const-meta-types) and [`const-decision-records`](../requirements.md#const-decision-records).

- **A. Every write event,** JSON only where there are notes.
  - **Pros:** one cause, one fix.
  - **Cons:** two more modules' documents and fixtures change.
- **B. `PostToolUse` only.**
  - **Pros:** a smaller change.
  - **Cons:** a known loss left in place; a second change to the same lines.

The session recommended A. **R17.** A, chosen by the decider in chat on 2026-09-29: R15 holds for `PreToolUse` and `PostToolUse` alike, and the three gates with notes pass the event's name.

## Carry list

1. R1 — history only: the choice of the day, the objection noted in the commit that started the branch and in [§2](../../modules/const-doc-budgets/MODULE.md#t2) of the module's document.
2. R2 — [requirement A11.3](../requirements.md#a11-3); [§3](../../modules/const-doc-budgets/MODULE.md#t3) of the module's document, the row's reading.
3. R3 — [requirement A11.2](../requirements.md#a11-2); [§3](../../modules/const-doc-budgets/MODULE.md#t3) and [§7](../../modules/const-doc-budgets/MODULE.md#t7) of the module's document, the dial `ceilings`.
4. R4 — [requirement A11.3](../requirements.md#a11-3); [§3](../../modules/const-doc-budgets/MODULE.md#t3) of the module's document.
5. R5 — [§6](../../modules/const-doc-budgets/MODULE.md#t6) of the module's document, the hook row; [§9](../../modules/const-doc-budgets/MODULE.md#t9), rows E1 and E2; [rule 8 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r8) and the enforcement rule of every other policy under `docs/policies/`; [the policy template](../../templates/policy.md), its enforcement and style slots.
6. R6 — [§7](../../modules/const-doc-budgets/MODULE.md#t7) of the module's document, the dials `severity` and `ceilings`; [§5](../../modules/const-doc-budgets/MODULE.md#t5), the invariant; [requirement A11.2](../requirements.md#a11-2), its enforcement cell.
7. R7 — [requirement A11.3](../requirements.md#a11-3); [§7](../../modules/const-doc-budgets/MODULE.md#t7) of the module's document, the dial `ceilings`.
8. R8 — [requirement A11.2](../requirements.md#a11-2); [§5](../../modules/const-doc-budgets/MODULE.md#t5) and [§7](../../modules/const-doc-budgets/MODULE.md#t7) of the module's document; [§6](../../modules/const-doc-budgets/MODULE.md#t6), the C5 text of an overlap.
9. R9 — [kernel §7](../../kernel/CONVENTIONS.md#k7).
10. R10 — [kernel §7](../../kernel/CONVENTIONS.md#k7); [requirement A11.1](../requirements.md#a11-1); [§3](../../modules/const-doc-budgets/MODULE.md#t3) of the module's document.
11. R11 — [§7](../../modules/const-doc-budgets/MODULE.md#t7) of the module's document, the dial `departures`; [the kit's dials file](../../constitution.yaml), its `const-doc-budgets.departures` and the comment beside it; [rule 6 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6) and [rule 10 of plc-0005-research](../policies/plc-0005-research.md#r10), the sentence on their frozen documents.
12. R12 — [§6](../../modules/const-doc-budgets/MODULE.md#t6) of the module's document, the package row and the messages N4 and H1; [§9](../../modules/const-doc-budgets/MODULE.md#t9), row E3 and limits 4 and 5.
13. R13 — [§5](../../modules/const-doc-budgets/MODULE.md#t5) of the module's document, rule B-a; [§3](../../modules/const-doc-budgets/MODULE.md#t3), the reading of [requirement A11.3](../requirements.md#a11-3).
14. R14 — [the kit's dials file](../../constitution.yaml), its `const-doc-budgets.ceilings`, the comment beside it and the six anchors of policy territories; [§10](../../modules/const-doc-budgets/MODULE.md#t10) of the module's document, item L1, the calibration as it was set.
15. R15 — [kit-shared-gate-code §3](../../shared/GATE.md#g3), the row G2; [its §2](../../shared/GATE.md#g2), item 3; [its §5](../../shared/GATE.md#g5), the item S159; [§6](../../modules/const-language/MODULE.md#t6) of the language module's document, the message N2.
16. R16 — [§7](../../modules/const-doc-budgets/MODULE.md#t7) of the module's document.
17. R17 — [kit-shared-gate-code §3](../../shared/GATE.md#g3), the row G2; [§6](../../modules/const-meta-types/MODULE.md#t6) of the meta-types module's document and [§6](../../modules/const-decision-records/MODULE.md#t6) of the decision-records module's document, the platform fact on stdout.
