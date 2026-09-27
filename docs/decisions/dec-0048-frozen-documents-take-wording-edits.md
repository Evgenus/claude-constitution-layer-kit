---
id: dec-0048-frozen-documents-take-wording-edits
type: task-record
title: An accepted record and a frozen comparison take wording edits from a closed list, so every scan covers them with no exclusion and no departure
status: active
stakes: process
decider: Eugene Chernyshov
---

# An accepted record and a frozen comparison take wording edits from a closed list, so every scan covers them with no exclusion and no departure

## 1. What "frozen" means for an accepted record and a frozen comparison

### Context

An accepted record was never edited to fit a later rule ([rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14)), and a comparison was frozen at its module's yes, with three named edits and no other ([rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7)). Each scan that reached those documents therefore had to hide them. The list-handles scan of module [`const-interaction`](../requirements.md#const-interaction) took them out of its territory by three number ranges. The language gate of module [`const-language`](../requirements.md#const-language) declared one departure over them, allowing its four content rules, as R11 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md) ruled. The marker scan of module [`const-questions`](../requirements.md#const-questions) took the templates out, as R4 of [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md) ruled. The decider asked on 2026-09-27 whether these exclusions were needed and whether they could go.

Measured on a scratch clone of the trunk with every exclusion removed, under the kit's calibration of the day (grade 13, 100 words): the marker scan was green over 121 documents, so the template patterns protected nothing. The list scan reported nine plain list items in accepted records and frozen comparisons. The language gate reported 26 findings in them: 24 sentences of 101 to 162 words, one record at grade 13.4 and one formal word. At the next step of the kit's descent, grade 12 and 60 words, the same gate reported 243 findings in 41 frozen documents; at the module's defaults, 1,794 in 68. None of these findings could be fixed by an edit that changes a ruling or a fact.

One claim of the session's first reading did not hold. Rule 9 of the root policy says a frozen document is never taken out of "the scan's territory", but that rule is the style rule and speaks of the style scan of module [`const-styling`](../requirements.md#const-styling). The list scan's exclusions broke no rule; they were a choice.

### Options

- **A. The same meaning: a closed list of wording edits is allowed, and every exclusion and departure for frozen documents goes.** An accepted record or a frozen comparison may take an edit that changes no ruling, fact or number and no link, anchor, handle, code span or quotation — a sentence split, a bold lead, a plain word, a code span around a quoted phrase — as a routine act, read by the readers of the change's audit.
  - **Pros:** no exclusion and no departure for frozen documents is left; the frozen documents follow every rule at every step of the descent, as the current-state documents do; the meaning of the freeze is stated in one place per kind.
  - **Cons:** the bytes of an accepted record may move after its yes, so review holds the freeze and git no longer does; three policies change and the audit is wide; [dec-0045-frozen-documents-stay-in-the-style-scan](dec-0045-frozen-documents-stay-in-the-style-scan.md), two days old, is reversed in part.
- **B. The same bytes: the list scan gets a departures dial like its two siblings.** The three exclusions become one departure entry; the template patterns go.
  - **Pros:** no accepted text moves; the smallest change; the three scans declare frozen documents in one way.
  - **Cons:** the exclusions only change their name; the nine items stay without a handle; the language departure grows with every acceptance and every step of the descent; a module gains a dial mostly for the kit's own use.
- **C. The same bytes, but the freeze starts later: the oldest records and comparisons are edited once, then frozen again.**
  - **Pros:** the nine list items are fixed with no standing permission.
  - **Cons:** moving the threshold by hand is the edit to fit a later rule that rule 14 forbids; the 26 language findings stand in later records and gain nothing.

### Recommendation

A: the byte-exact reading costs one exclusion or departure per scan, each growing with every acceptance, for edits that cannot change a ruling, and the reader who checks such edits already exists. The session recommended it, saying the cost plainly: the freeze becomes a promise about meaning, held by review.

### Choice

A, chosen by the decider in chat on 2026-09-28.

### Ruling

**R1.** An accepted record and a frozen comparison stay frozen in meaning, not in bytes. Each may take a wording edit, which changes no ruling, no fact and no number, removes or alters no link, anchor, handle, code span or quotation, and is one of four kinds and no other. (a) A sentence split where a clause ends: the dash, semicolon, colon or comma there becomes a full stop, and the next word takes a capital unless it is code. A joining word there — *and*, *but*, *so*, *while*, *which*, *where* — is dropped or becomes a pronoun or a noun the sentence already holds, and a clause with no subject of its own takes the subject it shared. (b) A list item that opens with no handle has its opening words set in bold, no word added, dropped or moved. (c) A word the `simpler` list of module `const-language` pairs with a plain word is replaced by that plain word, an article before it made to agree. (d) A quotation, or a word mentioned as a word, that holds a phrase of that module's `forbidden` or `simpler` list is put whole in a code span, its words unchanged.

**R2.** A wording edit is routine and may be made at any time. The commit names it a wording edit and names the documents it edits. Whether an edit stays inside the four kinds is review, by the readers of the change's carry audit where the change has one.

**R3.** A finding of a later threshold or list, or a trace of a style default, in a frozen document is removed by a wording edit where one removes it. Where none does, it is declared as a departure of that gate's dial over the document's path or a number range that holds it, with its reason. A frozen document is never taken out of a scan's territory.

**R4.** The kit's calibration follows. The list-handles scan, the marker scan and the language gate cover every Markdown file git lists: the three number-range patterns of `const-interaction.territories`, the two template patterns of `const-questions.territories` and the one entry of `const-language.departures` go. A draft module document is still taken out of the marker scan by its own path while it carries open slots.

**R5.** The edits of the day, named in the commit that makes them: ten plain list items reported in seven accepted records and two frozen comparisons, with their sibling items, took a bold lead; the 26 language findings were removed by sentence splits and one quotation put in a code span.

**R6.** Reversed or narrowed, the reversed records untouched: R12 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md), "never edited to fit a later rule", now holds beyond the wording edits; R37 of the same record, the edits a frozen comparison allows, gains the wording edit; R1 of [dec-0045-frozen-documents-stay-in-the-style-scan](dec-0045-frozen-documents-stay-in-the-style-scan.md), in its clauses "stands as written" and "never by an edit"; R11 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md), in its kit departure and in the policies' clause beside the style scan; R4 of [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md), in its two template patterns.

## 2. Where the wording edit of a record is allowed

### Context

After the pick of section 1, the session read [kernel §5](../../kernel/CONVENTIONS.md#k5) and found that the kernel allowed a record's body to be edited in place in two cases only. One is a correction before acceptance. The other is a mechanical edit, and the kernel named two: a typo and a reference-form migration. A sentence split or a bold lead is neither. So a policy of the kit could not allow the wording edits of R1 in an accepted record; only a kernel change could. The kernel says nothing of comparisons, whose freeze is the research policy's alone. In the kit, 15 of the 26 language findings and seven of the ten list items stood in records.

### Options

- **A. Change the kernel's section on records: a wording edit of a kind the project's records policy lists in a closed set becomes a third mechanical edit.** The kernel stays free of project detail; rule 14 of the records policy gives the list.
  - **Pros:** the result the decider picked in section 1; the rule is stated in the kernel, not read into the word "typo"; the kernel already allowed one wording edit, the typo.
  - **Cons:** a kernel change is always recorded, and its carry audit runs over every record; every consumer inherits the new kind of edit.
- **B. Apply section 1 to comparisons only; records keep their bytes, their exclusions and their departure.**
  - **Pros:** no kernel change; a smaller audit.
  - **Cons:** two routes again; the record ranges of the exclusion and of the departure keep growing.
- **C. Drop section 1's pick and take its option B.**
  - **Pros:** no freeze text changes anywhere.
  - **Cons:** the exclusions only change their name, and the language departure grows at every step.

### Recommendation

A: only a kernel change gives the result picked in section 1, and the typo already admits a wording edit that leaves the ruling. The session recommended it, the cost being a full carry audit.

### Choice

A, chosen by the decider in chat on 2026-09-28.

### Ruling

**R7.** [Kernel §5](../../kernel/CONVENTIONS.md#k5) names a third mechanical edit: a wording edit — a change to how a sentence or a list item is written that leaves its meaning, and every fact, number and reference in it, as they stand — of a kind the policy governing the project's records lists in a closed set, which the commit names a wording edit. R4 of [dec-0031-record-amended-until-its-yes](dec-0031-record-amended-until-its-yes.md), which named the typo and the migration as the mechanical edits, is widened, not reversed.

**R8.** The skills that state the mechanical edits or the freeze to consumers follow the kernel: `record-decision` of module `const-decision-records`, `plain-language` of module `const-language` and `style-defaults` of module `const-styling`. Their manifest version is `0.0.2`.

## Applied

The commit that creates this record changes the kernel's section on records, the three policies, the dials file, the module documents and skills of R4 and R8 and the three manifests, and makes the wording edits of R5. The record is born `active`, since the audit's findings may still add to it, and is set `inactive` in the commit that names its yes.

## Carry list

1. R1 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14); [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7).
2. R2 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14); [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7).
3. R3 — [rule 9 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r9); [rule 6](../policies/plc-0004-decision-records.md#r6) and [rule 16 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r16); [rule 10](../policies/plc-0005-research.md#r10) and [rule 11 of plc-0005-research](../policies/plc-0005-research.md#r11).
4. R4 — [the kit's dials file](../../constitution.yaml), the `territories` of `const-interaction`, `const-questions` and `const-language`, its `const-language.departures` and the comments beside them; [§7](../../modules/const-interaction/MODULE.md#t7) of the document of module `const-interaction`, the row `territories`; [§3](../../modules/const-questions/MODULE.md#t3) of the document of module `const-questions`, the row [A6.7](../requirements.md#a6-7); [§7](../../modules/const-language/MODULE.md#t7) of the document of module `const-language`, the row `departures`.
5. R5 — history only: the edits of the day; item L1 of [§10](../../modules/const-interaction/MODULE.md#t10) of the document of module `const-interaction` and item L1 of [§10](../../modules/const-language/MODULE.md#t10) of the document of module `const-language` tell them.
6. R6 — history only: the reversal and narrowing of items of accepted records, which are not touched.
7. R7 — [kernel §5](../../kernel/CONVENTIONS.md#k5); the widening of R4 of dec-0031, history only.
8. R8 — [the skill `record-decision`](../../modules/const-decision-records/skills/record-decision/SKILL.md) of module `const-decision-records`, section 4; [the skill `plain-language`](../../modules/const-language/skills/plain-language/SKILL.md) of module `const-language`, sections 3 and 4; [the skill `style-defaults`](../../modules/const-styling/skills/style-defaults/SKILL.md) of module `const-styling`, section 3; the manifests of [`const-decision-records`](../../modules/const-decision-records/.claude-plugin/plugin.json), [`const-language`](../../modules/const-language/.claude-plugin/plugin.json) and [`const-styling`](../../modules/const-styling/.claude-plugin/plugin.json), and the version line of the three module documents, [`const-decision-records`](../../modules/const-decision-records/MODULE.md), [`const-language`](../../modules/const-language/MODULE.md) and [`const-styling`](../../modules/const-styling/MODULE.md).
