---
id: dec-0102-bootstrap-recommends-and-copies-the-kernel-first
type: task-record
title: The bootstrap recommends yes to its two questions, copies the kernel before the policies, and claims each further territory after its policy
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The bootstrap recommends yes to its two questions, copies the kernel before the policies, and claims each further territory after its policy

## Context

On 2026-10-23 a second session bootstrapped the first consumer project by section 2 of [the install guide](../../INSTALL.md#s2) as merged by the change of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md), which had just rewritten it. All ten scans ended green, and the session reported ten findings, G1 to G10 in its report. On 2026-10-24 the session sorted them in chat. Six were wording, fixed in this change as routine edits: G1, G6, G9 and G10 in the install guide, and G4 and G7 in module [`const-styling`](../requirements.md#const-styling). G5 and G8 are the modules' design: G5 is finding F9 in the Context of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md), and G8 is the silence that R6 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r6) rules. Two changed accepted rulings, and the session put them one per message in chat on 2026-10-24; the carry audit of this change found a third, put the same way:

1. **G2.** R4 and R5 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r4) had the guide ask both questions with no default. [Kernel §5](../constitution/CONVENTIONS.md#k5) asks a record of a real choice for one recommendation with its reasoning, and so does the skill of [`const-questions`](../requirements.md#const-questions). So the project's record #1 read "Recommendation: None".
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
- **D. The guide itself recommends an answer to each question, and the user's answer decides.** The decider proposed it in answer to options A to C.
  - **Pros:** no kernel change; record #1 carries a real recommendation, as the kernel's section on records asks; every project sees the same reasons.
  - **Cons:** it reverses the "no default" of the decider's own earlier ruling.

The session recommended A, as the one option of the three it put that kept both the ruling of no default and the kernel's words, at the price of the full audit. The decider answered "or we can recommend", and the session read it as option D: the guide itself recommends an answer to each question, and the user's answer still decides. The session proposed yes to both, with its reasons, and the decider confirmed in chat on 2026-10-24.

<a id="r1"></a>**R1.** The install guide recommends yes to each of the two questions of its bootstrap, with its reason, and the user's answer decides. Yes to "Is the list of policies a catalog?", since the catalog gate checks every policy's name from the first one and the later rename never comes. Yes to "Does this project keep a style guide?", since at install few policies need a style rule, the shipped guide passes the defaults of [`const-language`](../requirements.md#const-language) as written, and a guide added later edits every policy. Record #1 carries the guide's recommendation beside the answers. This replaces "proposes no default" in R4 and R5 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r4); the rest of R4 stands, and of R5 all but the moment of the style skill, which R3 replaces.

## 2. The kernel copy before the policies

- **A. The kernel is copied before the policies: step 5 copies it, step 6 writes the policies, record #1 stays last.**
  - **Pros:** a policy links the kernel from its first write, and the gate checks the link as it is written; no project edits its policies twice.
  - **Cons:** an accepted ruling changes; steps 5 and 6 swap numbers, so the carry entries that name them follow by a migration.
- **B. The order stays; step 5 cites the kernel in words, and step 7 turns the words into links.**
  - **Pros:** no ruling changes, no new step numbers.
  - **Cons:** every project edits its policies twice, and their first commit lacks the links the gate would check.

The session recommended A: the friction returns in every project, and the reason R2 gave for its order no longer depends on that order. The decider chose A in chat on 2026-10-24.

<a id="r2"></a>**R2.** The bootstrap copies the kernel in its step 5, before the policies of step 6, and commits the copy on its own. Record #1 is written last, in step 7, and is born `inactive`, since by the commit that creates it the dials file, the kernel copy and the policies are applied on the branch. This replaces R2 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r2).

## 3. Each further territory after its policy

The carry audit of this change, at e43ff0b, found the guide's step 4 claiming the territories of the kernel copy and of decision records before their policies existed, while module [`const-locations`](../requirements.md#const-locations) orders every new kind as its policy, then its territory, then its first document, and the guide's own sentence said a territory is claimed once its kind has a policy. The kernel copy cannot follow that order: every policy links it.

- **A. Follow the policy-first order.** Step 4 writes only the root's lines; step 6 writes each policy and then its territory, and names the record policy and its catalog once that policy exists; the kernel copy is the one document made before its policy.
  - **Pros:** the guide and the module agree; one stated exception in place of a contradiction; the gates' repeated note that a named policy has no document goes away.
  - **Cons:** step 6 grows, each policy bringing its line of the dials file; the example block needs a sentence on the file's final form.
- **B. Keep claiming all three territories in step 4, and state it as the bootstrap's exception.**
  - **Pros:** the smallest edit.
  - **Cons:** an exception to the module's "the order is the rule"; the repeated note stays.

The session recommended A: it removes the contradiction and leaves only the exception nothing can avoid. The decider chose A in chat on 2026-10-24. A confirming read at 33d1949 found the root's territory named before its policy, and the fix of that read moved the root's lines out of step 4, on the premise that the gates fail while `root_policy` names a file not yet written. The read at 03cba1c found the premise false for the guide's own steps and the move harmful, since the root policy's write went unchecked; the read at 3dea93e found that A as chosen works. So R3 states A as chosen, and names the root's territory as the one territory claimed before its policy.

<a id="r3"></a>**R3.** The bootstrap claims each further territory only once its kind has a policy. Step 4 writes the dials file's first lines alone, the root's and the others, which need no policy: `root_policy`, `module_prefix`, the root policy's territory, the namespace of `const-task-close`, and the `plc` catalog when the policies are a catalog. The root's territory is therefore the one claimed before its policy, since the creation command and the checks of the root policy need it. Step 6 writes the root policy first, by hand; then each further policy and its territory; and, after the policy for decision records, `record_policies` and the `dec` catalog, before the `plc` entry. With a style guide, the skill of `const-styling` comes after those three policies, which replaces "before the first policy" in R5 of [dec-0101-bootstrap-on-a-branch-with-two-questions](dec-0101-bootstrap-on-a-branch-with-two-questions.md#r5). Since every policy links the kernel, the kernel copy of step 5 is the one document made before its policy; it stays outside claimed territory until step 6 claims it.

## Applied

The record was born `active`, and the change that creates it applies its rulings in the install guide's section 2, its steps 4, 5, 6 and 7, and in step 5 of the rollout plan. Steps 5 and 6 of the guide swap: the kernel copy, step 6 before this change, is step 5, and the policies, step 5 before, are step 6. The change migrates the carry entries of accepted records that named those steps, by case (i) of rule 14 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14). The last commit of the branch sets the record `inactive`.

## Carry list

1. R1 — [the install guide](../../INSTALL.md#s2), step 4 of section 2, and step 7 for the record. What it replaces is history.
2. R2 — [the install guide](../../INSTALL.md#s2), the opening of section 2 and its steps 5, 6 and 7. What it replaces is history.
3. R3 — [the install guide](../../INSTALL.md#s2), steps 4, 5 and 6 of section 2. What it replaces is history.
