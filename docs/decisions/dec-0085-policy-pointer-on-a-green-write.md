---
id: dec-0085-policy-pointer-on-a-green-write
type: task-record
title: The write-time guard points a session at the governing policy once per session
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The write-time guard points a session at the governing policy once per session

## Context

Each policy in `docs/policies/` governs one document kind and claims its territory through its namespace in `constitution.yaml` ([kernel §3](../constitution/CONVENTIONS.md#k3)). The gates read the root policy, the dialect and the territory lines, and no gate reads a policy's prose. Every policy's Enforcement rule says that its content rules are review. The one carrier that sends a session to a policy's body is the new-document skill of module [`const-locations`](../requirements.md#const-locations), at a document's creation. When a session edits a document that exists, nothing names the policy that governs it. The guide's line "open a policy only when working in its territory" is unenforced, and a session that edits a record or a module document does not know which rules review will hold. The write-time gate of module [`const-meta-types`](../requirements.md#const-meta-types) already resolves the governing policy on every write in claimed territory, so it holds the one fact the session lacks at the moment it lacks it. The skills study behind [dec-0079-skills-named-at-their-moment](dec-0079-skills-named-at-their-moment.md) showed that a pointer given at the moment it applies brings the load that a listing alone does not, and that a rule carried by a skill alone drifts (R5 of [dec-0047-decision-shape-printed-at-session-start](dec-0047-decision-shape-printed-at-session-start.md#r5)).

## Options

- **A. The gate's green carries a pointer.** On a green verdict for a `Write` or an `Edit` in claimed territory, the write-time gate adds one advisory line to the model's context: the governing policy's path and the anchor of its rule named Enforcement, once per session for that policy.
  - **Pros:** the gate already knows the policy and runs on every write; the line reaches the model as added context, which plain output does not; one line per session and policy costs about 170 characters; the pointer is a fact, so a fixture proves it.
  - **Cons:** the gate gains a memo of what it said, kept beside its output log; a pointer is advice, and whether the policy is read stays judgment.
- **B. A new skill alone.** A skill of the module says: before editing a governed document, read its policy.
  - **Pros:** no code, no memo, no fixture.
  - **Cons:** a skill-only rule drifts when the skill is not loaded, the finding of R5 of [dec-0047-decision-shape-printed-at-session-start](dec-0047-decision-shape-printed-at-session-start.md#r5); nothing names the policy's path, so the session still has to resolve it.
- **C. Review-side reading only.** The reviewer reads the policy at the merge and holds the document to it.
  - **Pros:** nothing to ship; the policies already say content is review.
  - **Cons:** it catches a defect at the merge, after the work, and only in the kit, whose one reviewer is the author; a consumer has no such reviewer.
- **D. Make the policies' rules mechanical one by one.** Each content rule of each policy becomes a check.
  - **Pros:** a check is deterministic and teaches its fix.
  - **Cons:** machinery for failures no consumer has hit, against the guide's rule that growth is friction-earned; most content rules are judgment and cannot become checks.

## Recommendation

The session recommended A: it uses the fact the gate already holds, at the moment it applies, through the one channel that reaches the model, at a cost the session pays once per policy.

## Choice

The decider chose A in chat on 2026-10-11.

## Ruling

<a id="r1"></a>**R1.** On a green verdict for a `Write` or an `Edit` in claimed territory, the write-time gate of module [`const-meta-types`](../requirements.md#const-meta-types) adds one advisory line to the context the platform hands the model, before the green line: the module's name, the word `advisory`, the governing policy's repository-relative path, and the words `read its rules before further edits`. The line is the module's message `N3`, written out in the module's document, and it reaches the model as the `additionalContext` of the green, never as plain output, which the model never reads. A red, a warn, a skip and a scan carry no pointer: a red already teaches, and a scan has no session.

<a id="r2"></a>**R2.** Where the policy's body holds a rule named Enforcement — an explicit anchor followed by the bold name, with or without a full stop inside the bold, as the kit's policies write their numbered rules — the line names that rule's anchor after the path, since that rule says what review holds; the first such rule is the one named. Where the policy has no such rule, the line names the path alone.

<a id="r3"></a>**R3.** The line is said once per session, per repository and per policy, so that a session edits many documents of one kind and pays once. What was said is remembered in a memo beside the module's output log, under the same name as the log with the suffix `.pointed`: one line per pointer, the session's id, the repository root and the policy's path, tab-separated; the memo keeps its last 200 lines. The memo has a home where the log has one: `log_dir` when set, else the platform's per-plugin data directory. Where neither exists, or where the event names no session, nothing is pointed. A memo that cannot be read or written counts as holding nothing, so the line is said again rather than lost, and no verdict waits on it: the memo's read and its write each swallow an `OSError`, said so at their place, which the gate-script rule on the output log allows for an advisory memo kept beside the log, as the template now says.

<a id="r4"></a>**R4.** The pointer is a new requirement row, [A2.7](../requirements.md#a2-7), homed in module [`const-meta-types`](../requirements.md#const-meta-types) as advisory: the hook's green carries the line, and whether the policy is read is judgment. The module's manifest version moves to `0.0.2`, within its draft range ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## Applied

The commits of this branch apply every item: the code and its fixture, then the requirement row, the module's document, its install note and landing page, and this record, corrected before its yes on the findings of its validation and of its carry audit. The record was created `active` and set `inactive` by a fix commit of its validation, once every item was applied.

## Carry list

1. R1 — [`const-meta-types`](../../modules/const-meta-types/MODULE.md#t3), the row of section 3 for [requirement A2.7](../requirements.md#a2-7), [its section 6](../../modules/const-meta-types/MODULE.md#t6), the row `N3` of the message table, and [its section 9](../../modules/const-meta-types/MODULE.md#t9), row `E5`; [requirement A2.7](../requirements.md#a2-7).
2. R2 — [`const-meta-types`](../../modules/const-meta-types/MODULE.md#t6), the row `N3` of the message table of section 6; [requirement A2.7](../requirements.md#a2-7).
3. R3 — [`const-meta-types`](../../modules/const-meta-types/MODULE.md#t6), the `package` row of section 6, and [its section 9](../../modules/const-meta-types/MODULE.md#t9), limit 5; [the module template](../../module-template/gate-script-rules.md#r12), gate-script rule 12 of section 6, the clause on an advisory memo; [kit-shared-gate-code](../../shared/GATE.md#g4), limit 10; [requirement A2.7](../requirements.md#a2-7).
4. R4 — [requirement A2.7](../requirements.md#a2-7), and [`const-meta-types`](../../modules/const-meta-types/MODULE.md#t3), the row of section 3 for that requirement; the version is history only.
