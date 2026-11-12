---
id: dec-0118-two-ceilings-follow-the-dials-file
type: task-record
title: The ceilings install-guide and module-readmes stand as the dials file sets them, and a later re-set by the rule of the dial is routine
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The ceilings install-guide and module-readmes stand as the dials file sets them, and a later re-set by the rule of the dial is routine

## Context

[The dials file](../../constitution.yaml) holds the character ceilings of module [`const-doc-budgets`](../requirements.md#const-doc-budgets) under the dial `ceilings`. It states the dial's rule at that key: a ceiling's number is the longest document of its window plus 10 %, rounded up to 1,000, and a ceiling stays at warning until its window holds 30 days of data.

Two accepted records ruled on two of those ceilings:

1. R12 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r12) set the ceiling `install-guide` at 15,000 characters at warning, with the guide's first day as its window.
2. R4 of [dec-0077-module-readme-pages](dec-0077-module-readme-pages.md#r4) set the ceiling `module-readmes` at warning, by the dial's rule, with the pages' own first days as its window.

On 2026-11-08 the ceilings had 30 days of data behind them. The decider picked in chat, one document per message, what each document over its ceiling takes. Two of those picks reach these two ceilings. By the first, the install guide is shortened as far as its rulings allow, and its ceiling is set from the shortened guide. By the second, each ceiling moves to error in the change that brings its group under its number.

Two routine changes of that day applied the picks. The ceiling `install-guide` went from 15,000 at warning to 29,000 at error: the shortened guide, 25,543 characters, plus 10 %, rounded up to 1,000. The ceiling `module-readmes` went from 8,000 at warning to 9,000 at error, by the dial's rule. Both took the window 2026-10-09 to 2026-11-08.

Neither change named a record. So the two rulings still gave the old level, and the first the old number. On 2026-11-10 the carry audit of [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md) and [dec-0117-change-cost-module-rulings](dec-0117-change-cost-module-rulings.md) found the gap: the dials file no longer stated what the two records ruled, and no record named the move ([item 9.37 of the rollout plan](../rollout-plan.md#s9-37)). [Rule 4 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r4) lets only a new record reverse a ruling past its yes. The open point was how much the new record rules.

## Options

- **A. The two moves only.** The record rules the number, the level and the window of the two ceilings as they stand today, and names the two rulings it replaces.
  - **Pros:** it says exactly what the picks of 2026-11-08 decided; it is the smallest ruling.
  - **Cons:** a record again sets two numbers, so the next routine re-set of either ceiling opens the same gap and needs another record.
- **B. The two moves, and a rule for later moves of these two ceilings.** Today's numbers are history. What binds is that the number, the level and the window of the two ceilings stand in the dials file, and that a later re-set by the dial's rule is routine, with its reason in a comment at the entry.
  - **Pros:** the gap cannot open again for these two; they then move as the other ceilings moved on 2026-11-08, by a routine change.
  - **Cons:** a new rule beyond the picks of 2026-11-08; two more comments in the dials file.
- **C. As B, for every ceiling of the dial.** One rule at the key `ceilings` of the dials file says that a re-set of any ceiling by the dial's rule is routine.
  - **Pros:** one rule for all ceilings; it matches how twelve ceilings moved on 2026-11-08.
  - **Cons:**
    - **wider than the plan item asks**;
    - **other records set other ceilings**, such as R6 of [dec-0115-long-documents-split-and-carry-entries-follow-moved-text](dec-0115-long-documents-split-and-carry-entries-follow-moved-text.md#r6) for the template's 23,000, and a general rule may collide with them.

## Recommendation

B, recommended by the session: it closes the gap for the two ceilings the plan item names, and it stays clear of the records that set other ceilings.

## Choice

B, by the decider in chat on 2026-11-11.

## Ruling

<a id="r1"></a>**R1.** The ceiling `install-guide` no longer takes its number, its level or its window from R12 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r12). This record reverses that ruling in those three points. The ceiling's name and the document it holds stay as that ruling gave them.

<a id="r2"></a>**R2.** The ceiling `module-readmes` no longer takes the way its number is set, its level or its window from R4 of [dec-0077-module-readme-pages](dec-0077-module-readme-pages.md#r4). This record reverses that ruling in those three points. The ceiling's name and its paths stay as that ruling gave them.

<a id="r3"></a>**R3.** The two routine changes of 2026-11-08 stand. They set `install-guide` to 29,000 at error and `module-readmes` to 9,000 at error, each over the window 2026-10-09 to 2026-11-08, by the decider's picks of that day.

<a id="r4"></a>**R4.** The number, the level and the window of the two ceilings are those of their entries under `const-doc-budgets.ceilings` in the dials file, and of no record.

<a id="r5"></a>**R5.** A later re-set of either entry by the dial's rule is routine: a new window, the number that the rule gives from it, and the level. The dial's rule is what the dials file states at the key `ceilings` for a ceiling's number and its level:

- **the window's longest document plus 10 %**, rounded up to 1,000;
- **warning until 30 days of data**;
- **error in the change that brings the group under its number**.

The change that makes the re-set writes its day and its reason in the comment at that entry. A change of either entry by another measure, such as a number set from a shortened document, is priced by its stakes like any other change.

## Applied

The two ceilings stand in the dials file as R3 says since 2026-11-08. This change adds the comment of R4 and R5 at each of the two entries. It also names the window's longest in the comment of `install-guide`, and folds the inline comment of `module-readmes` into its block. It changes no number, level or window. The record is born `inactive`.

## Carry list

1. R1, R2 — history only: the two reversals, which bind nothing once R4 is carried.
2. R3 — history only: the changes of 2026-11-08, a one-time act.
3. R4, R5 — [the dials file](../../constitution.yaml), the comments at the entries `install-guide` and `module-readmes` of `const-doc-budgets.ceilings`.
