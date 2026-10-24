---
id: dec-0102-bootstrap-recommends-and-copies-the-kernel-first
type: task-record
title: The bootstrap recommends yes to its two questions and copies the kernel before the policies
status: active
stakes: process
decider: Eugene Chernyshov
---

# The bootstrap recommends yes to its two questions and copies the kernel before the policies

## Context

On 2026-10-23 a second session bootstrapped the first consumer project by section 2 of [the install guide](../../INSTALL.md#s2), at kit commit cbc486f, the guide that [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md) had just rewritten. All ten scans ended green, and the session reported ten findings, G1 to G10 in its report. On 2026-10-24 the session sorted them in chat. Six were wording, fixed in this change as routine edits: G1, G6, G9 and G10 in the install guide, and G4 and G7 in module [`const-styling`](../requirements.md#const-styling). G5 and G8 are the modules' design: G5 is F9 of dec-0101, and G8 is the silence that R6 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r6) rules. Two changed accepted rulings, and the session put them one per message in chat on 2026-10-24:

1. **G2.** R4 and R5 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r4) had the guide ask both questions with no default. [Kernel §5](../../kernel/CONVENTIONS.md#k5) asks a record of a real choice for one recommendation with its reasoning, and so does the skill of [`const-questions`](../requirements.md#const-questions). So the project's record #1 read "Recommendation: None".
2. **G3.** R2 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r2) made the kernel copy just before record #1, after the policies. A policy's link to a kernel section then pointed at a file not yet there, and the referencing gate refused the write. The session cited the kernel in words first and linked it in the record's commit.

## 1. A recommendation for the two questions

- **A. The kernel's section on records admits a record with no recommendation, when its question was put without one by rule, the record saying why.**
  - **Pros:** it matches the ruling of no default; record #1 as written would comply.
  - **Cons:** a kernel change, so the carry audit runs in full over every record; a kernel rule widens for one case.
- **B. The session recommends, while the guide proposes no default.**
  - **Pros:** no kernel change.
  - **Cons:** a session's recommendation is close to a default, which the decider had ruled against; sessions would lean differently.
- **C. Record #1 states the answers in the kernel's shape for no real choice: ruling and reasons, no options.**
  - **Pros:** no kernel change; a small edit of the guide.
  - **Cons:** the record loses the options as weighed; a real choice is called none.

The session recommended A. The decider answered "or we can recommend", and the session read it as a fourth option: the guide itself recommends an answer to each question, and the user's answer still decides. The session proposed yes to both, with its reasons, and the decider confirmed in chat on 2026-10-24.

<a id="r1"></a>**R1.** The install guide recommends yes to each of the two questions of its bootstrap, with its reason, and the user's answer decides. Yes to "Is the list of policies a catalog?", since the catalog gate checks every policy's name from the first one and the later rename never comes. Yes to "Does this project keep a style guide?", since at install few policies need a style rule, the shipped guide passes the defaults of [`const-language`](../requirements.md#const-language) as written, and a guide added later edits every policy. Record #1 carries the guide's recommendation beside the answers. This replaces "proposes no default" in R4 and R5 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r4); the rest of R4 and R5 stands.

## 2. The kernel copy before the policies

- **A. The kernel is copied before the policies: step 5 copies it, step 6 writes the policies, record #1 stays last.**
  - **Pros:** a policy links the kernel from its first write, and the gate checks the link as it is written; no project edits its policies twice.
  - **Cons:** an accepted ruling changes; steps 5 and 6 swap numbers, so the carry entries that name them follow by a migration.
- **B. The order stays; step 5 cites the kernel in words, and step 7 turns the words into links.**
  - **Pros:** no ruling changes, no new step numbers.
  - **Cons:** every project edits its policies twice, and their first commit lacks the links the gate would check.

The session recommended A: the friction returns in every project, and the reason R2 gave for its order no longer depends on that order. The decider chose A in chat on 2026-10-24.

<a id="r2"></a>**R2.** The bootstrap copies the kernel in its step 5, before the policies of step 6, and commits the copy on its own. Record #1 is written last, in step 7, and is born `inactive`, since by the commit that creates it the dials file, the kernel copy and the policies are applied on the branch. This replaces R2 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r2).

## Applied

The record was born `active`, and the change that creates it applies its rulings in the install guide's section 2 and in step 5 of the rollout plan. Steps 5 and 6 of the guide swap: the kernel copy, step 6 before this change, is step 5, and the policies, step 5 before, are step 6. The change migrates the carry entries of accepted records that named those steps, by case (i) of rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14). The last commit of the branch sets the record `inactive`.

## Carry list

1. R1 — [the install guide](../../INSTALL.md#s2), step 4 of section 2, and step 7 for the record. What it replaces is history.
2. R2 — [the install guide](../../INSTALL.md#s2), the opening of section 2 and its steps 5, 6 and 7. What it replaces is history.
