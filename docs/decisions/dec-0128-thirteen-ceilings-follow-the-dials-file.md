---
id: dec-0128-thirteen-ceilings-follow-the-dials-file
type: task-record
title: Thirteen founding ceilings stand as the dials file sets them, and a later re-set by the rule of the dial is routine
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Thirteen founding ceilings stand as the dials file sets them, and a later re-set by the rule of the dial is routine

## Context

[The dials file](../../constitution.yaml) holds the character ceilings of module [`const-doc-budgets`](../requirements.md#const-doc-budgets) under the dial `ceilings`. R14 of [dec-0052-doc-budgets-module-rulings](dec-0052-doc-budgets-module-rulings.md#r14) set its eighteen founding ceilings. Each stood at warning, with the window 2026-09-14 to 2026-09-29. Each number came from the rule of R13 of that record.

All eighteen stand at error today. Four routine changes of 2026-11-08 and 2026-11-09 made the moves, by the decider's picks of 2026-11-08 in chat. R10 of [dec-0115-long-documents-split-and-carry-entries-follow-moved-text](dec-0115-long-documents-split-and-carry-entries-follow-moved-text.md#r10) rules five of them: `guide`, `shared-code`, `policies`, `module-template` and `records`. No record named the move of the other thirteen:

- **eleven re-set by the dial's rule** on 2026-11-08, from the window that ends that day: `comparisons`, `kernel`, `intent`, `requirements`, the one of the style guide, `readme`, `module-skills`, `install-notes`, `kit-agents`, `kit-skills` and `templates`;
- **`rollout-plan`**, kept at 48,000 once the plan's done items were trimmed, by the pick D16 of that day;
- **`module-documents`**, set from the documents shortened by the picks D5 to D11 of that day.

So the founding ruling still gave the old level and window of the thirteen, and the old numbers of most. The gap was logged in [item 9.38 of the rollout plan](../rollout-plan.md#s9-38). Its count was checked against the history of the dials file on 2026-11-12. [Rule 4 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r4) lets only a new record reverse a ruling past its yes. R1 to R5 of [dec-0118-two-ceilings-follow-the-dials-file](dec-0118-two-ceilings-follow-the-dials-file.md#r1) ruled the same gap for two later ceilings on 2026-11-11. The open point was how much this record rules.

## Options

- **A. As dec-0118 ruled for its two ceilings, for the thirteen.** The record reverses the founding ruling for the thirteen in their number, level and window. Then those stand in the dials file, and a later re-set by the dial's rule is routine.
  - **Pros:** the rule picked for dec-0118; the gap cannot open again for these thirteen; it leaves the five of dec-0115 alone.
  - **Cons:** three groups of ceilings follow three records, dec-0115, dec-0118 and this one.
- **B. The moves only.** The record states the number, the level and the window of the thirteen as they stand, and rules nothing for later.
  - **Pros:** the smallest ruling.
  - **Cons:** the next routine re-set of any of the thirteen opens the same gap again.
- **C. One rule for every ceiling of the dial.** A re-set of any ceiling by the dial's rule is routine, and the numbers leave every record.
  - **Pros:** one rule in one place.
  - **Cons:** wider than the plan item; it reverses parts of dec-0115 and dec-0118, and was turned down for the latter.

## Recommendation

A, recommended by the session. It closes the gap of the plan item as the decider picked for dec-0118, and leaves dec-0115 alone.

## Choice

A, by the decider in chat on 2026-11-12.

## Ruling

<a id="r1"></a>**R1.** The thirteen ceilings that the Context names no longer take their number, level or window from R14 of [dec-0052-doc-budgets-module-rulings](dec-0052-doc-budgets-module-rulings.md#r14). This record reverses that ruling in those three points, for those thirteen. Their names and the documents they hold stay as that ruling gave them.

<a id="r2"></a>**R2.** The routine changes of 2026-11-08 that moved the thirteen to error stand, with the numbers and the window they set.

<a id="r3"></a>**R3.** The number, the level and the window of each of the thirteen are those of its entry under `const-doc-budgets.ceilings` in the dials file.

<a id="r4"></a>**R4.** A later re-set of any of the thirteen by the dial's rule is routine. It takes a new window, the number the rule gives from it, and the level. The dial's rule is what the dials file states at the key `ceilings` for a ceiling's number and its level. The change that makes the re-set writes its day and its reason in a comment at that entry. A change of such an entry by another measure is priced by its stakes like any other change. A number set from a shortened document is one.

<a id="r5"></a>**R5.** This record does not rule the re-set of `requirements` and `module-documents` on 2026-11-12. The record of that change rules it.

## Applied

The thirteen stand in the dials file as R2 says since 2026-11-08, save the two that R5 names. The commit that creates this record adds the comment of R3 and R4 at the key `ceilings`, naming the thirteen and this record. It changes no number, level or window. The record is born `inactive`.

## Carry list

1. R1 — history only: the reversal, which binds nothing once R3 is carried.
2. R2 — history only: the changes of 2026-11-08, a one-time act.
3. R3, R4 — [the dials file](../../constitution.yaml), the comment at the key `ceilings` of `const-doc-budgets` that names this record.
4. R5 — history only: a bound of this record's scope, which binds nothing.
