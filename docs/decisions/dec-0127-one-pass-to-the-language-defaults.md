---
id: dec-0127-one-pass-to-the-language-defaults
type: task-record
title: The kit comes down to the language defaults in one pass, in one change closed by the audit before publication
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit comes down to the language defaults in one pass, in one change closed by the audit before publication

## Context

Module [`const-language`](../requirements.md#const-language) holds two numbers for the kit's prose. One is the grade ceiling and the other is the words a sentence may hold. The module's defaults are grade 10 and 25 words. The kit started at 13 and 100 words.

R5 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md#r5) set the grade's descent: 12, then 10. R6 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md#r6) set the sentence's descent: 60, then 40, then 25. Both asked one step per change, each with its audit. [Item 9.6 of the rollout plan](../rollout-plan.md#s9-6) holds those five steps.

On 2026-11-11 the decider asked to finish the rollout plan. The same day the decider asked for fewer pull requests, one per wave of work. Each pull request costs runs of CI.

The session measured the tree on 2026-11-12 at the target numbers. It found 6,752 findings in 237 documents. The counts of the five steps overlap. So five steps would rewrite many sentences up to three times. [Item 10.13 of the rollout plan](../rollout-plan.md#s10-13) also owes one carry audit in full before publication.

The session put three questions in chat on 2026-11-12, one per message.

## 1. How the descent lands

- **A. Five changes, as the plan words it.** Five pull requests, each with its own carry audit.
  - **Pros:** each step is small enough to review and to revert alone; the plan's wording stands.
  - **Cons:**
    - **five rounds of CI and five audits** over nearly every record;
    - **many sentences rewritten** two or three times.
- **B. One change for the descent alone.** One pass straight to grade 10 and 25 words, with its own carry audit. Item 10.13 is a separate audit later.
  - **Pros:** each sentence is rewritten once; one round of CI.
  - **Cons:** two audits of nearly the whole tree in a row; the change is too large to review by eye.
- **C. One change for every text edit before publication.** It holds the descent in one pass, the logged findings of item 9.38 and the kernel piece of item 9.24b. The one carry audit in full closes it, and that audit is item 10.13.
  - **Pros:**
    - **one audit in full** instead of two or more;
    - **one round of CI**;
    - **nothing is audited and then edited again**.
  - **Cons:**
    - **the largest single change**;
    - **one red blocks all of it**;
    - **it rests on the gates and the audit**, not on review by eye.

The session recommended C. It asks one audit in full where the plan already owes one. The decider chose C in chat on 2026-11-12.

<a id="r1"></a>**R1.** The kit's descent to the defaults of module [`const-language`](../requirements.md#const-language) is one pass. It goes straight to a grade ceiling of 10 and 25 words per sentence. This reverses the five steps of R5 and R6 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md#r5). The rest of those two rulings stands.

<a id="r2"></a>**R2.** The descent, the findings of item 9.38 of the rollout plan and the kernel piece of its item 9.24b land as one change. The carry audit in full that closes it is the audit that item 10.13 of the plan asks before publication.

## 2. How frozen documents meet the defaults

An accepted record or a frozen comparison takes only the wording edits its policy lists. [Rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) lists them for records. The question was whether the frozen documents should take them at all.

The session first ran a pilot on the records 1 to 30. The wording edits fixed 131 of 264 findings, and 133 stood. Of 29 records, 28 still needed a departure. Pros and cons on one line became nested bullets with bold leads.

- **A. Edit them, as the earlier ruling says.** Every frozen document takes the allowed edits, and a departure covers the rest.
  - **Pros:** the ruling stands; about half of the long sentences get shorter.
  - **Cons:**
    - **nearly every record needs the departure anyway**;
    - **records change their look**;
    - **the heaviest part of the audit**.
- **B. They stand as written under one departure by path.** No frozen document is edited, and a new record narrows the earlier ruling.
  - **Pros:** 56 % of the work and the riskiest part of the audit fall away; records keep their text.
  - **Cons:**
    - **it changes a ruling**;
    - **old records stay hard to read**;
    - **the pilot's work is thrown away**.
- **C. Keep the pilot's 28 records, and the rest stand as written.**
  - **Pros:** no work is thrown away.
  - **Cons:** two kinds of frozen record, with no reason a reader can see.

The session recommended B, for the work and the audit it saves. The decider chose A in chat on 2026-11-12.

So [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md) stands unchanged. This section rules nothing new. It records that the edits were made and where the departures stand.

## 3. Three documents over their ceilings

The splits of the descent took three documents over their character ceilings. The requirements document stood at 46,607 characters against 46,000. The document of module [`const-change-cost`](../requirements.md#const-change-cost) stood at 90,261 against 90,000. One accepted record stood at 34,500 against the records' 34,000.

That record is [dec-0117-change-cost-module-rulings](dec-0117-change-cost-module-rulings.md). Two records already stand over that ceiling under a departure.

- **A. Raise by the dial's rule.** The ceilings `requirements` and `module-documents` are re-set by the rule. The rule takes the longest document, adds 10 % and rounds up to 1,000. That gives 52,000 and 100,000. The record stands under a departure beside the other two.
  - **Pros:**
    - **the rule already in use decides the numbers**;
    - **no text is cut for size alone**;
    - **the records' ceiling keeps its number**.
  - **Cons:** two ceilings rise by about 10 %; a third long record stands over the records' ceiling.
- **B. Shorten the two living documents.** The record takes a form with splits only.
  - **Pros:** every ceiling stays.
  - **Cons:**
    - **a second rewrite for size alone**;
    - **the record would keep 68 long sentences**, not 49;
    - **more to audit**.
- **C. Departures for all three.**
  - **Pros:** no ceiling moves, and no text changes.
  - **Cons:** a departure lets a living document grow without limit.

The session recommended A, since the rule the kit already uses decides the numbers. The decider chose A in chat on 2026-11-12.

<a id="r3"></a>**R3.** The ceilings `requirements` and `module-documents` were re-set by the dial's rule on 2026-11-12. Their number, level and window are those of their entries in the dials file, and of no record. A later re-set of either by the dial's rule is routine. It is a new window, the number the rule gives from it, and the level. The change that makes it writes its day and its reason in the comment at the entry. A change of either entry by another measure is priced by its stakes, like any other change.

<a id="r4"></a>**R4.** [dec-0117-change-cost-module-rulings](dec-0117-change-cost-module-rulings.md) stands over the records' ceiling under a departure. The dials file gives the reason in that entry.

## Applied

The change this record belongs to did the following on its branch, and the record states only what that branch shows.

- **The two dials.** `grade_ceiling` stands at 10 and `sentence_words` at 25 in the dials file.
- **The documents.** Eleven groups of documents were rewritten on 2026-11-12, and the language scan is green.
- **The departures.** The language module's `departures` hold four entries. The first is the entry that stood before. The second allows long sentences in 133 frozen documents. The third allows long sentences and the grade in one record, the tenth. The fourth allows long sentences in five module pages.
- **The ceilings.** `requirements` stands at 52,000 and `module-documents` at 100,000, and the third long record stands under a departure.

The commit that creates this record adds the clause of R3 to the comments at the two ceilings. It names this record at the two dials and at the departure of R4. It also brings one sentence of the language module's document to the one pass. Every item has its home there, or is pending in the plan, so the record is born `inactive`.

Another record of the same change rules the thirteen founding ceilings. It leaves the two re-sets of 2026-11-12 to this record.

## Carry list

1. R1 — [the dials file](../../constitution.yaml), the comments at `grade_ceiling` and `sentence_words` of `const-language`; [§4 of the module's document](../../modules/const-language/MODULE.md#t4), its first item. History: the reversal of the five steps of two earlier rulings, an act of this record.
2. R2 — pending: [item 10.13 of the rollout plan](../rollout-plan.md#s10-13), the carry audit in full that closes this change.
3. R3 — [the dials file](../../constitution.yaml), the comments at the entries `requirements` and `module-documents` of `const-doc-budgets.ceilings`. History: the re-sets of 2026-11-12, a one-time act.
4. R4 — [the dials file](../../constitution.yaml), the comment at the ceiling `records` and the second entry of `const-doc-budgets.departures`.
