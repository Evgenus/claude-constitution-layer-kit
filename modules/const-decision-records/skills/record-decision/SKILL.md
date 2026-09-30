---
name: record-decision
description: >
  Price a decision by its stakes and, when it is a recorded one, write the decision record:
  envelope with stakes and decider, body with the options, pros and cons, one recommendation
  and the choice. Use when a ruling is being made or has just been made in the dialog — a
  policy, procedure or harness ruling, a user-visible behaviour, a structural choice — when
  unsure whether a call deserves a record or only a commit note, when reversing an earlier
  ruling, or when a write was blocked for a record's stakes or decider. Advisory: it shapes
  the triage and the body; the write-time gate checks only type, stakes and decider.
---

# Record a decision

A ruling that lives only in the chat is gone with the session. A ruling recorded with more
ceremony than it deserves teaches everyone to skip the ceremony. This procedure prices the
decision first and writes a record only when the price says so. Stakes, the ceremony each
level gets, and the shape of a decision record are defined by the constitution's conventions
page that the project adopted; nothing here redefines them.

What is checked and what is not: once the project has named its record policy (step 3,
item 1), this plugin's hook blocks a decision record whose envelope lacks
`type: task-record`, a `stakes` of `process | product | architecture`, or a non-empty
`decider` — or, where the project set `severity: warn`, reports it and lets the write
through. Until a record policy is named the hook examines nothing and says so. Everything else on this page is judgment, and it is yours: whether a record was
due, what its stakes are, whether the body is honest.

## 1. Price it: which stakes?

Ask one question: **is the call cheap to revert?**

- **Yes → `routine`.** Act. Put one line in the commit message saying what was chosen and
  why. Write no record — a record for a routine call is ritual, and the gate refuses
  `stakes: routine`.
- **No, and it rules on the harness, a policy or a procedure → `process`.** A record, and one
  human yes on the change, named in the commit that lands it: where a PR flow exists, the
  commit that merges the pull request, the yes being its approval or, where no second human
  reviews it, the decider's own merge. This is the fast lane: a
  process fix needs that one yes and nothing more — it never waits behind a heavier gate,
  least of all the gate it is fixing.
- **No, and it changes what a user sees → `product`.** A record.
- **No, and it is structural and hard to reverse → `architecture`.** A record, and review.

The line between routine and recorded is drawn by examples, not by criteria. The project's
own pairs come first: read `boundary_examples` under `const-decision-records` in
`constitution.yaml`. When the project has none — the key absent or an empty list — use these:

1. Where a worktree or a scratch directory lives → routine. / Which kinds of document exist
   and what authority each carries → recorded (`process`).
2. Where in a pull-request description a review note goes → routine. / Whether a change may
   land without a review → recorded (`process`).
3. How a test stub fakes a dependency → routine. / How the product treats untrusted input →
   recorded (`product` or `architecture`).
4. Renaming a helper nobody else calls → routine. / Renaming an identifier, a setting or a
   contract that others already depend on → recorded.

When two readings stay plausible, take the higher one: an unneeded record costs minutes, an
unrecorded structural call costs the next session its reasoning.

## 2. Name the decider

`decider` is the person or role who made the choice — not who typed the commit; git already
knows that, and it is often not the same. If the project says who may decide at each level
(`deciders` under `const-decision-records` in `constitution.yaml`, a list per stakes level),
the decider comes from that list; if the project names nobody — the key absent or empty, as a whole or at that level — ask who decides. If the person who should decide is absent, do not decide
for them at recorded stakes: stop, put the question with its options, and name them as the
blocker.

## 3. Write the record

1. **Where.** Decision records live in the territory of the project's record policy: in
   `constitution.yaml`, `const-decision-records.record_policies` names the policy, and the
   territory sits under that policy's id. Read the policy document itself for the project's
   own rules — naming, numbering, anything else. When a module that allocates numbers is
   installed and the project numbers its decision records, take the number from it.
   When a module that creates documents at their home is installed, its command's dry run
   names the path for the record's stem; take the home from there rather than deriving it.
   If the project has no `constitution.yaml`, or names no record policy, ask the user where
   decision records live and write the record there; say once that the write-time check is
   off until `record_policies` names the policy for that place.
2. **From the template,** never from a blank page or from another record:
   [record-template.md](record-template.md) in this skill's directory
   (`${CLAUDE_SKILL_DIR}/record-template.md`). It holds both body shapes; delete the one
   that does not apply.
3. **Envelope.** `id` stable kebab-case, never changed afterwards; `type: task-record`;
   `title` one line stating the ruling, not the topic; `stakes`; `decider`; `status` as in
   item 5. No date: the commit is the decision moment and the ordering.
4. **Body, when a real choice existed:** the options considered; pros and cons per option;
   exactly **one** recommendation with its reasoning; the choice made and by whom — which
   may differ from the recommendation, and then the record says why.
   **Body, when no real choice existed:** the ruling and the reasoning. Never manufacture
   options to fill the shape.
5. **Status.** `active` while the ruling is still being applied to the documents and code
   it changes; `inactive` once it is applied. A record whose ruling is applied in the same
   commit that creates it is born `inactive`. Once applied, the rule must stand in the text
   of the current-state document it changed: the record is provenance — where and why —
   never the place a rule lives.

## 4. Reversing or changing an earlier ruling

A record is **accepted** once the ceremony its stakes ask for is complete: the yes of a
`process` record, the review of an `architecture` record. A `product` record is asked for
neither and is accepted when committed.

- **Before it is accepted,** whatever examines the record — a validation, a review, the
  decider reading it again — may still correct it in place: a ruling item tightened, added or
  withdrawn. Correct the documents it changed in the same commit, and say so in the commit
  message.
- **Once it is accepted,** write a **new** record that names the old one and says what
  replaces it. Never edit the old record's ruling, stakes or decider in place. The only
  in-place edit left is mechanical — a typo, rewriting how it cites other documents, or a
  wording edit of a kind the project's policy for records lists in a closed set, such as a long
  sentence split — with the commit message naming it a typo fix, a migration or a wording edit.

## 5. Before you finish

If a record was written or edited through the shell (heredoc, `sed`), the hook did not see
it. Run the scan: `sh "${CLAUDE_PLUGIN_ROOT}/scripts/check-decision-record.sh" --scan` —
exit 2 lists the findings with the same messages the hook gives.
