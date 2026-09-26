---
id: dec-0045-frozen-documents-stay-in-the-style-scan
type: task-record
title: Frozen documents stay in the style scan — a trace in one is declared by a departure over a number range that holds it, or its path, never taken out of the territory
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Frozen documents stay in the style scan — a trace in one is declared by a departure over a number range that holds it, or its path, never taken out of the territory

## Context

Module [`const-styling`](../requirements.md#const-styling) landed on 2026-09-26 with three negated patterns in its `territories` dial, taking the 43 records accepted before [dec-0044-styling-module-rulings](dec-0044-styling-module-rulings.md) and the 8 comparisons frozen before its own out of the scan: an accepted record is never edited to fit a later rule ([rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14)) and a comparison is frozen at its module's yes ([rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7)), so a finding in one could never be fixed by an edit. The style rules of the two policies said the ranges were out, and rule 9 of the root policy granted every kind's policy that permission; R7 of the module's record named the two uses. The decider asked the same day why the territory carried so many exclusions. The answer: they protected nothing — the scan was green on every one of the 51 documents before they were added — and they hid every signature in those documents where the module's own dial can hide one. The scan examined 63 of 114 Markdown files.

## Options

- **A. Keep the negated patterns.** The frozen documents stay out of the scan's territory by number range, as the sibling `const-interaction` keeps them out of its list-handles scan.
  - **Pros:** no change; consistent with the sibling; the excluded documents are immutable, so a finding in them could only ever be declared away.
  - **Cons:** 51 documents are examined for nothing, though they carry no signature today; a signature added later would go unseen in them rather than be declared with its reason; the exclusion hides twelve signatures where one would do.
- **B. Drop the patterns; declare a departure over a range or a path when a signature bites.** The scan covers every Markdown file; a trace of a default in a document a rule of its policy freezes is declared by an entry of the `departures` dial over a number range that holds it, or its path, allowing that one signature with the reason that the document stands as written.
  - **Pros:** the scan examines everything it can; the hiding is one signature wide and carries its reason; the module's own mechanism serves the case it was built for.
  - **Cons:** three rules amended an hour after their yes, a record and a carry audit; a future signature that bites an old document costs one dial entry instead of nothing.

## Recommendation

B, though not at once: the shape hides less and the departure is the right home, and the change would earn its record when a signature actually bit a frozen document. The session recommended it.

## Choice

B, chosen by the decider in chat on 2026-09-26, with the record written now rather than at the first bite.

## Ruling

**R1.** A document a rule of its policy freezes — an accepted record, a frozen comparison — stands as written, and a trace of a default in it is declared by a departure over a number range that holds it, or its path, never by an edit and never by taking it out of the scan's territory; rule 9 of the root policy says so for every kind, and the style rules of the records and research policies say so for theirs.

**R2.** The kit's `const-styling.territories` covers every Markdown file, the frozen documents included; no departure is declared for them until a signature bites one, since none of them carries a signature today.

**R3.** The clause of R7 of [dec-0044-styling-module-rulings](dec-0044-styling-module-rulings.md) that named the two number-range exclusions as uses of the root policy's permission is reversed, with the permission itself; the rest of R7 stands.

## Applied

The commit that creates this record amends the three rules, drops the three patterns from the dial and reworks the live item L1 of the module's document; the record is born `inactive`, every item having its home, and awaits its yes.

## Carry list

1. R1 — [rule 9 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r9); [rule 16 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r16); [rule 11 of plc-0005-research](../policies/plc-0005-research.md#r11).
2. R2 — the `territories` of `const-styling` in `constitution.yaml`; [§10](../../modules/const-styling/MODULE.md#t10) of the module's document, item L1.
3. R3 — history only: the reversal of a clause of an accepted record, which is not touched.
