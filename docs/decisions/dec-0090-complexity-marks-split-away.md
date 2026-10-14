---
id: dec-0090-complexity-marks-split-away
type: task-record
title: The functions marked over the complexity limit when it came in are split below it and lost their marks
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The functions marked over the complexity limit when it came in are split below it and lost their marks

## Context

R1 of [dec-0088-ruff-complexity-limit](dec-0088-ruff-complexity-limit.md#r1) holds ruff's C901 at a complexity of 15. R2 of [dec-0088-ruff-complexity-limit](dec-0088-ruff-complexity-limit.md#r2), the marking ruling below, ruled that each function above 15 when the rule came in carries a `# noqa: C901` mark: 22 functions, 3 of module code, 2 of the shared tests and 17 of the kit's scripts. The carry list of dec-0088 homes the marking ruling in step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md), and in the marks themselves.

On 2026-10-13 the change `work/simplify-complexity` split the functions of the modules' gate code above a complexity of 10. Two of them carried a mark, `examine` of const-styling and `act` of const-locations; both fell far below 15, and their marks went with the split. That change read the marking ruling as a fact of the day the rule came in, and it did not say so.

On 2026-10-14 the decider asked to remove every mark. This change splits the other 20 marked functions. Each of them, and each function the split adds, scores 15 or below, and each split keeps the behaviour. The question is what that does to the marking ruling. Its carriers are the marks, which are now gone, and a sentence of CLAUDE.md, which would now be false.

## Options

- **A. A record that reverses the marking ruling.** This record states that the marked functions are split and lost their marks, and CLAUDE.md is reworded to match.
  - **Pros:** the ruling and the code agree without a reading of the marking ruling; the record also covers the two marks of `work/simplify-complexity`; it follows the decider's habit of picking the explicit rule.
  - **Cons:** a carry audit and a record for a change that keeps the rule in force — the limit of 15, a mark with its reason held by review — as it is.
- **B. Routine: the marking ruling read as a fact of its day.** No record; CLAUDE.md gets a one-line change, and the commit says how the marking ruling was read.
  - **Pros:** fast; R1, R3 and R4 of [dec-0088-ruff-complexity-limit](dec-0088-ruff-complexity-limit.md#r1) stay as they are; the words "when the rule came in" allow the reading.
  - **Cons:** it rests on a reading of an accepted ruling; a later carry audit may find the marking ruling without its home; the decider has picked the explicit rule over a reading before.

## Recommendation

A, recommended by the session: the carry list of dec-0088 names the marks as a home of the marking ruling, so removing them takes away a carrier of the ruling, not a dated count, and a record says so in the open.

## Choice

The decider chose A in chat on 2026-10-14.

## Ruling

<a id="r1"></a>**R1.** R2 of [dec-0088-ruff-complexity-limit](dec-0088-ruff-complexity-limit.md#r2) is reversed, save its last sentence. None of the 22 functions it names kept its `# noqa: C901` mark. Each was split to a complexity of 15 or below, two by the change `work/simplify-complexity` and 20 by this one, with its behaviour kept.

<a id="r2"></a>**R2.** The last sentence of R2 of [dec-0088-ruff-complexity-limit](dec-0088-ruff-complexity-limit.md#r2) stands: a reason in a module's files or in the shared code names no record.

<a id="r3"></a>**R3.** Any function above the limit, one of the 22 included, carries `# noqa: C901` only where a change marks it under R3 of [dec-0088-ruff-complexity-limit](dec-0088-ruff-complexity-limit.md#r3); no mark stands from the day the rule came in, 2026-10-13.

## Applied

The commits before the one that creates this record split the 20 functions and removed their marks. The commit that creates this record states R2 and R3 in [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module". The rounds of its carry audit corrected R1 and R3 and that step in place before the yes, as their commits name. The record is born `inactive`.

## Carry list

1. R1 — history only: the reversal of R2 of dec-0088-ruff-complexity-limit, and the splits that removed the marks.
2. R2 — [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
3. R3 — [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
