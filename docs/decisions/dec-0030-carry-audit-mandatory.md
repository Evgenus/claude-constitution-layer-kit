---
id: dec-0030-carry-audit-mandatory
type: task-record
title: The carry audit is mandatory before a yes; the shape of the carry list and the receipt of the audit are gated, the audit itself stays judgment
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The carry audit is mandatory before a yes

## Context

Two audits on 2026-09-19 and 2026-09-20 asked of every decision record whether it could be deleted without anyone losing a rule. The first found eleven ruling items that lived only in a record; after the repairs the second, by readers who knew nothing of the first, found none of those and six new ones — four of them in the repairs themselves. [dec-0027-record-citations-optional](dec-0027-record-citations-optional.md) had made a carry list and a carry check part of a record, both advisory. One day later the three records written under that rule close in two different shapes, and the third spreads its rulings over six sections where the others have one list.

The decider asked for the audit to be mandatory at the end of a module's development, and for a proposal of how to gate it. The difficulty is [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): whether a sentence states a rule is judgment, and nothing judgment-based may be dressed as a check.

## Options

- **A. Procedure only.** The audit becomes a mandatory step, run through a saved procedure with a computed scope; no script.
  - **Pros:** cheapest; nothing pretends to be a check.
  - **Cons:** rests on the author remembering; the drift in record shape continues, and a drifting shape is what makes the next audit dear.
- **B. Procedure plus a gate on the carry list.** A script holds what is deterministic: every ruling item has a handle, every handle a declared home, every home a kind of document that can hold a rule.
  - **Pros:** cheap to run; fixes one record shape; blocks the four places rulings were found hiding; says what it cannot see.
  - **Cons:** one more kit script; handles on ruling items cost the author a little; an item that was given no handle is invisible to it.
- **C. B plus a gate on a receipt.** The commit that names the yes carries a trailer naming the audit, and the script checks it.
  - **Pros:** whether an audit was declared becomes machine-visible; trivial in CI once there is a pull-request flow.
  - **Cons:** it verifies a claim the author writes about their own work, so it can be green over an audit that never ran.
- **D. The audit report as a governed document kind,** gated for existence and freshness.
  - **Pros:** findings survive outside commit messages and chat.
  - **Cons:** a new document kind and policy for one use; reports are history, which [kernel §1](../../kernel/CONVENTIONS.md#k1) wants in git; the pinned commit such a report needs is barred from documents by [requirement A5.6](../requirements.md#a5-6).

## Recommendation

B, by the session: the failure that earned this was rulings with no declared home, and B turns exactly that red while the part that needs a mind stays with a reader. The session argued against C that a check of a self-written receipt cannot fail honestly.

## Choice

C, by Eugene Chernyshov in chat on 2026-09-20, with both proposed defaults accepted — the computed scope and the threshold — and the instruction to implement. The session's objection to the receipt stands as recorded above and was answered in the build, not dropped: the receipt is made as hard to satisfy falsely as a receipt can be, and the policy, the session guide, the skill and the script each say what it does not show.

## Ruling

1. **R1.** The carry audit is mandatory before the yes on any decision record, and is the second pass of the fresh-context validation at the end of a module's development. It is run through the kit's `carry-audit` skill, which fixes the pin of each round to one commit, the reader prompts, the partition, the blind pass, and the rule that a reader's finding is verified against the tree before it is acted on.
2. **R2.** The scope is computed, never chosen. Read in full: the records the change adds or edits, and those the module's decisions section cites. Read for regression: every other record that cites a file the change touched, asked only whether that file still states what the record ruled — the narrow question is what keeps the wide list affordable. `scripts/check-carry-lists.py --scope` computes both.
3. **R3.** The audit is run in full, over every record, on any change to the kernel and once before publication.
4. **R4.** The shape of a record is fixed: the last section is titled "Carry list"; every ruling item opens with a bold handle; the list pairs each handle, once, with links, with "history only", or with "pending" and a link.
5. **R5.** A link in the list may lead only where a rule can live: an `active` `current-state` document, `CLAUDE.md`, a skill of the kit, a module's or the template's own file, a file that is not markdown — a file, never a folder. The rollout plan, a research comparison, another record and the README cannot hold a rule.
6. **R6.** "pending" is for intent that is not yet real; its link leads to the task-record that holds the work to come — a plan, never a decision record — where [kernel §2](../../kernel/CONVENTIONS.md#k2) says such intent rides. The entry is never rewritten: when that task-record closes, its close carries the intent into the current-state documents, the gate says so in a note, and the next audit in full checks it.
7. **R7.** The commit that names the yes carries two trailers: `Accepted:` with the record's id, and `Carry-Audit:` with the commit the readers were pinned to, the number of records read, and the findings, fixed and justified. The pinned commit is an ancestor at which the record already existed, the records are above zero, fixed and justified add up to the findings. The newest acceptance of a record is the one that counts, so a wrong receipt is mended by accepting again, never by rewriting history.
8. **R8.** A record that no commit accepts yet awaits its yes: the gate reports a note, never a finding — a gate is not red for waiting on a person.
9. **R9.** The gate is `scripts/check-carry-lists.py`, with its red→green proof in `--self-test`, for records numbered `0030` and above. Records `0027` to `0029` keep the earlier form of their lists — another title, or items without handles: an accepted record is not edited to fit a later rule.
10. **R10.** Enforcement is declared, never blurred: the list's shape and the receipt are a gate; whether a ruling is carried is judgment, held by the audit's readers and by review. The gate cannot see an item that was given no handle, whether the linked text states the rule, or whether the audit a receipt names was run.
11. **R11.** In Phase D the gate joins the kit's CI, which fetches the full history for it, and one audit in full is run before the modules are published.
12. **R12.** The yes is named in the message of the commit that lands the change, as [kernel §4](../../kernel/CONVENTIONS.md#k4) says. The kernel does not say which commit of a change made of several lands it; the kit reads it as the one that completes the change: a change is complete when it is accepted with a receipt the gate reads as right. For an audited record that commit comes after the audit, since readers are pinned to a commit that already holds the record; the decision-record policy had said "the commit that lands the record", which is narrower than the kernel and unreachable for a gated record.
13. **R13.** From Phase D, when the yes is PR approval, the two trailers stand in the commit that merges the pull request.
14. **R14.** This reverses two words of [dec-0027-record-citations-optional](dec-0027-record-citations-optional.md): its items 5 and 6 called the carry list and the carry check advisory. The list's shape is now gated and the audit mandatory; what that record called judgment stays judgment. It also widens its item 5: beside carried and "history only" there is "pending".
15. **R15.** Built on the day: the script and the skill in commit `cb1e910`; the "pending" form and the kit skills as a home were added when this record's own item R11 could not otherwise be listed; the audit of this change, pinned to `f87bc5a`, then found the rest — among it a fix text that could never turn the gate green, a receipt that accepted a pin older than the record, and a rule 5 that contradicted the kernel; a confirming reader pinned to `449eaa2` found nine more defects in those fixes, among them a kernel term stretched to cover the rewriting of a pending entry, which is why R6 now says the entry is never rewritten.

16. **R16.** Until its yes the fixes of its audit may amend a record in place, and the commit says so. The third round of this record's audit found that no text allowed it; the decider made it the kernel's rule in [dec-0031-record-amended-until-its-yes](dec-0031-record-amended-until-its-yes.md). This record was so amended by each round of its audit.
17. **R17.** A finding is fixed, or justified in a commit message of the change. When fixes follow an audit, a confirming reader is pinned to the commit that holds them and asked only what the fixes broke, repeated while a pass finds a defect; the receipt names the last pin and counts the findings of every round.

## Carry list

1. R1 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 2; step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); the procedure in [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md).
2. R2 — step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); steps 2 and 3 and prompt B of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md); [the script](../../scripts/check-carry-lists.py).
3. R3 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 2.
4. R4, R5, R6 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 2; [the script](../../scripts/check-carry-lists.py).
5. R7, R8 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 5; step 8 of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md); [the script](../../scripts/check-carry-lists.py).
6. R9, R10 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 2; the docstring of [the script](../../scripts/check-carry-lists.py).
7. R11, R13 — pending: [the rollout plan](../rollout-plan.md), step 10.
8. R12 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 5.
9. R14 — history only: what it says of the earlier record is a fact of this day; the rules themselves are R1, R4, R6 and R10.
10. R15 — history only: what was built on the day.
11. R16 — [kernel §5](../../kernel/CONVENTIONS.md#k5); [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 5.
12. R17 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rules 2 and 5; steps 6 to 8 and prompt D of [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md).
