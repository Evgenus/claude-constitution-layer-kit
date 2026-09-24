---
id: dec-0039-policies-state-their-kinds
type: task-record
title: Every policy states the shape of its kind — an enforcement rule, anchored rules that keep their numbers, a change rule, and the conventions its documents already keep
status: active
stakes: process
decider: Eugene Chernyshov
---

# Every policy states the shape of its kind — an enforcement rule, anchored rules that keep their numbers, a change rule, and the conventions its documents already keep

## Context

On 2026-09-24 the decider asked for every policy of the kit to be checked against the documents it governs, and for what each policy should also state. The nine policies were read, with the kernel, the intent page, the requirements document, the rollout plan and the shared-code page; the thirty-eight records, the six module documents and the six research comparisons were read by fresh readers, one kind each. The documents comply with their policies almost everywhere; the policies are thin. Eight of nine skip the Enforcement rule the policy template asks for. No policy anchors its rules, though rules are cited by number in seventeen places, and a renumbered rule would silently break accepted records, which are not edited. Most policies say far less about a kind's shape than its documents already practise: the records keep a section order, a handle form and a way of naming the decider that the decision-record policy does not state; the module documents share an envelope, handle prefixes, an evidence form and a way of importing the shared texts that the module-document policy does not state; the research policy's provenance rule admits public sources only, while every comparison rests on its own experiments and on the kit's tree.

Defects found on the day, beside the thin policies: the record template the `templates` dial pointed at carries no carry list and no handles, so a record written from it fails `scripts/check-carry-lists.py`; [dec-0037-dials-file-block-style](dec-0037-dials-file-block-style.md) was born `active` though applied in its creating commit; [dec-0009-module-routine-validation-and-inputs](dec-0009-module-routine-validation-and-inputs.md) received a pointer to its reversing record after its yes, called a migration; three records are `inactive` with pending entries while two older ones stayed `active` in the same situation; the requirements document had two headings of the first level, a column named "one line" over rows of six hundred characters, row [A6.9](../requirements.md#a6-9) between [A6.2](../requirements.md#a6-2) and [A6.3](../requirements.md#a6-3), and a horizon paragraph of intent not yet real; the intent page claimed enforcement by a CI that does not exist; the rollout plan's done lines had grown into narratives.

## Options

- **A. One record, nine sections.** One `process` record with a section per policy and handles across all, one carry audit, one yes.
  - **Pros:** one ceremony for one theme; the cross-cutting rules are ruled once; the audit reads every policy either way.
  - **Cons:** a long record, and an open question on one policy holds the other eight.
- **B. One record per policy**, landed in sequence, the cross-cutting rules in the root policy's record first.
  - **Pros:** each record short and reversible on its own; the root's rules bind the rest before they are written.
  - **Cons:** nine audits and nine yeses over the same fortnight; repeated context in each.
- **C. Fix the defects only** and defer the new rules until friction recurs.
  - **Pros:** cheapest; obeys "growth is friction-earned".
  - **Cons:** most of the rules are conventions already practised, so the friction has occurred; the policies stay thinner than their documents.

## Recommendation

A, by the session: the proposals are one theme — the written-down shape of nine kinds — and the carry audit reads every policy in either case.

## Choice

A, chosen by the decider in chat on 2026-09-24. Two slots were left open in the proposal and put to the decider one per message before the yes, each answered A on 2026-09-24: how a reversal treats the reversed record (R14), and what completes an `architecture` review in the kit (R16).

## Ruling

### 1. The root policy, [plc-0001-root-policy](../policies/plc-0001-root-policy.md)

**R1.** Every policy carries an Enforcement rule, stating which module guards which field of its kind at write time and in its scan, and what stays judgment.

**R2.** Every rule of every policy carries an explicit anchor `r<n>` inside its item, before the bold name; from another document a rule is cited as a link to its anchor with "rule n of <policy id>" as the text; a rule keeps its number and anchor for life, a withdrawn rule keeps its number and says so, and a new rule takes the next number. The seventeen citations of a policy's rule in the tree were migrated to the anchored form in this change, the records among them under the reference-form migration of [kernel §5](../../kernel/CONVENTIONS.md#k5).

**R3.** Amending a rule of a policy is a `process` decision; carrying an already-ruled item is routine; a mechanical edit is routine. The policy template, `templates/policy.md`, is the shape, and a rule that changes the shape changes the template in the same change.

**R4.** A policy's body opens with the sentence the template writes, its title is "<Kind> policy — <clause>", and every rule opens with a bold name.

### 2. The kernel policy, [plc-0002-kernel](../policies/plc-0002-kernel.md)

**R5.** A kernel change runs the carry audit in full, and a change to a section the shared gate code implements changes that code and bumps every module that links it. Sections keep their `k` numbers; a new one takes the next. The admission test of the kernel's own preamble is pointed at, not restated. The schemas are the page's machine half, held with the text by the coverage pair `kernel-schemas` and with the shared mirror by `scripts/check-schema-mirror.py`. Every example in the page obeys the page's rules and names no path or id of the kit.

### 3. The intent policy, [plc-0003-intent-page](../policies/plc-0003-intent-page.md)

**R6.** The page's content is the six sections it holds, adding one being a change under its change rule; the page speaks in the present tense, a mechanism not yet built named as planned with a link to the plan's step; a principle added after the founding set cites the record that earned it; sections carry `i<n>` and principles `p<n>`. The claim of enforcement by CI is rewritten as a link to step 10 of the plan.

### 4. The decision-record policy, [plc-0004-decision-records](../policies/plc-0004-decision-records.md)

**R7.** A record is written from the kit's own template, `templates/decision-record.md`, named for the kind in `const-locations.templates`: the shape the record skill of module `const-decision-records` ships to every consumer, with the carry list and the handles added, which are the kit's rules and no module's — so the module's template stays within its rows. A change to the shape rules changes the template in the same change.

**R8.** The sections and their order are fixed for both shapes; a record answering several questions has one numbered section per question with a recommendation and its reasoning each; the title states the ruling and the H1 repeats it.

**R9.** A ruling item is any sentence that binds after the yes, wherever it stands, a default left open to override included — the test being the blind reader; handles run in order, contiguous and unique in the record, tables included, a key of another document written qualified; one home per handle, with the split or the after-link history for a mixed item.

**R10.** A record is `inactive` once every item has a home, "pending" being a home, and `active` only while an item has none; a record grown through an authoring is set `inactive` in the commit that names its yes. This settles the two readings the records took, in favour of the newer.

**R11.** The body says "the decider"; the Choice names where and when; a commit hash appears for a pin or a deleted file only.

**R12.** An accepted record is never edited to fit a later rule, whatever the rule; a rule that applies from a number on names the threshold.

**R13.** The defects of the day are not repaired in the records: [dec-0037-dials-file-block-style](dec-0037-dials-file-block-style.md) keeps its history of a wrong birth status, and the sentence added to [dec-0009-module-routine-validation-and-inputs](dec-0009-module-routine-validation-and-inputs.md) stays — an accepted record is not edited, and both are provenance only.

**R14.** A reversing record names the reversed item by record and handle, the reversal itself is carried "history only", and the reversed record is not touched: a pointer added to an accepted record is new content, not the mechanical edit of [kernel §5](../../kernel/CONVENTIONS.md#k5). Chosen A over a kernel change admitting a supersession pointer as a third mechanical edit, by the decider in chat on 2026-09-24: the reversal is found through the reversing record and the audit's provenance sort, and the kernel stays as it is.

**R15.** Every record of the kit so far is `process`; a `product` record is complete when committed.

**R16.** An `architecture` record's review is the two passes of step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md) — a fresh-context reader of the record and the carry audit — with every finding fixed or justified, and its yes named as a `process` record's is. Chosen A by the decider in chat on 2026-09-24, over a second human reviewer, whom the kit does not have, and over leaving the slot open, which would make the first such record improvise a recorded-stakes procedure; a second reviewer replaces this by a routine amendment once one exists.

### 5. The research policy, [plc-0005-research](../policies/plc-0005-research.md)

**R17.** Provenance is a public source, a numbered experiment of the document that a reader could repeat, or the kit's tree at a named commit; a tool read and not run is marked so; an earlier comparison is never a source; nothing cites an input outside the repository.

**R18.** The shape is the template's, `templates/research-comparison.md`, section by section, with the verdicts of the summary a closed set: CONFIRMED, OVERTURNED, build, not needed.

**R19.** A comparison is frozen when the record that accepts its module is accepted: a fact found wrong is annotated inline with the date, a finding on the module as built goes into the module document, and a platform change, a module revision or the decider's request earns a new survey under a new number, the older set `inactive` in the same commit.

**R20.** No rule lives in a comparison and no document relies on one; modules, comparisons and records are named by name or id, never by ordinal; "the specification" is the module's stub, linked; a comparison is written by a subagent from the template.

**R21.** The six comparisons written before these rules stand as written, under R19.

### 6. The module-document policy, [plc-0006-module-documents](../policies/plc-0006-module-documents.md)

**R22.** The envelope is `current-state`, `active`, id `module-<plugin name>`, title `const-<name> — <one clause>`; the three documents whose title was the bare name gained their clause in this change.

**R23.** The document changes with its code under the coverage map; a change to a rule it states is `process`; a version bump edits the preamble's version line, which after publication states the version alone. Anchors `t1` to `t12` are the template's; a section is added to the template, never to one document.

**R24.** One prefix per kind of handle in a document — message keys, `E<n>`, `T<n>`, `S<n>` from 101, `L<n>` for live items or `V<n>` where `L` is the message prefix — never reused, a key of another document written qualified. Three enforcement tables gained their `E` column, two sibling lists their numbers, and the live items of `const-locations` became `V1` to `V3` in this change.

**R25.** The shared texts enter by link to [kit-shared-gate-code](../../shared/GATE.md), its sections 3 to 5; the module's own messages are written out word for word.

**R26.** A live proof carries its date, environment and platform version; a deferred one is labelled `live, deferred` and links the plan's step; a platform fact carries its date and what breaks. Kit-live counts are such evidence, and links to kit documents are the description's own: the kit is no project, and the portability grep holds the installed components.

**R27.** The files are listed once, in the artifacts section; the plugin skeleton is not copied into the document — removed from the two that carried it.

### 7. The requirements policy, [plc-0007-requirements](../policies/plc-0007-requirements.md)

**R28.** A row keeps its number for life, stands in number order, states its rule in full at any length; the `†` flag is defined. Row [A6.9](../requirements.md#a6-9) was moved after [A6.8](../requirements.md#a6-8) and the column renamed in this change.

**R29.** The destination and enforcement classes are closed sets defined once in the preamble — the enforcement classes were written out there in this change; a row's recommended enforcement stays the recommendation, confirmed or overturned by the comparison, what shipped stated in the module document's enforcement section.

**R30.** One heading of the first level, the matrix first, the specifications after it under their anchors, nothing that is neither a requirement nor a specification: the second first-level heading was lowered and the horizon paragraph moved to the plan in this change.

### 8. The rollout-plan policy, [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md)

**R31.** Phases carry `phase-<letter>` and steps `s<n>`; steps are numbered once across phases and keep their number, a later one standing as `<n>a`.

**R32.** A step done is marked in one sentence with the date, the record and "the yes given"; evidence lives in the record and the module document. The done lines of Phase A and Phase C were cut to this form in this change.

**R33.** The plan is the home a "pending" entry points at, and a step so named closes with its intent carried; the plan is `inactive` when step 11 is done; the last phase holds no rule and points at the intent page and the policies.

### 9. The shared-code policy, [plc-0009-shared-code](../policies/plc-0009-shared-code.md)

**R34.** Sections carry `g<n>`; an acceptance item's number is never reissued; an observed platform fact names version, date, backstop and fallback; a change to the code updates the page in the same change and bumps every linking module; a part not built is listed with its signal.

**R35.** A module may be pointed at by its ordinal in the order of authoring, which the plan resolves and which never changes; the equality of the messages table with the code is review until a friction earns a check.

### 10. Across the nine

**R36.** Twenty-four Markdown files lie in no territory — `CLAUDE.md`, the README, the templates, the skills, the install notes. The constitution is silent there, so this is no defect, and no policy is written for them by this record; a session-guide kind and a templates kind are the next policies the kit will want, when friction says so.

## Carry list

1. R1 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r8), rule 8, and [templates/policy.md](../../templates/policy.md), rule 3.
2. R2 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r7), rule 7, and [templates/policy.md](../../templates/policy.md), rule 1.
3. R3 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r3), rule 3.
4. R4 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r4), rule 4.
5. R5 — [plc-0002-kernel](../policies/plc-0002-kernel.md#r3), rules 3 to 7.
6. R6 — [plc-0003-intent-page](../policies/plc-0003-intent-page.md#r3), rules 3 to 6, and [INTENT.md](../../INTENT.md#i5), the sentence on the A12 gates.
7. R7 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r8), rule 8, and the `templates` dial of [constitution.yaml](../../constitution.yaml).
8. R8 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r9), rule 9.
9. R9 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r10), rule 10.
10. R10 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r11), rule 11.
11. R11 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12), rule 12.
12. R12 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), rule 14.
13. R13 — history only: a finding of the day, left as it is.
14. R14 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r13), rule 13.
15. R15, R16 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r15), rule 15.
16. R17 — [plc-0005-research](../policies/plc-0005-research.md#r3), rule 3.
17. R18 — [plc-0005-research](../policies/plc-0005-research.md#r5), rule 5.
18. R19 — [plc-0005-research](../policies/plc-0005-research.md#r7), rule 7.
19. R20 — [plc-0005-research](../policies/plc-0005-research.md#r4), rules 4, 8 and 9.
20. R21 — [plc-0005-research](../policies/plc-0005-research.md#r10), rule 10.
21. R22 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r5), rule 5.
22. R23 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r6), rules 6 and 7.
23. R24 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r8), rule 8.
24. R25 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r9), rule 9.
25. R26 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r10), rule 10, and rule 3.
26. R27 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r11), rule 11.
27. R28 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r6), rule 6.
28. R29 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r7), rule 7, and the preamble of [constitution-requirements](../requirements.md).
29. R30 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r8), rule 8.
30. R31 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r4), rule 4.
31. R32 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5.
32. R33 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r6), rules 6 and 7.
33. R34 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r4), rules 4 to 8.
34. R35 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r3), rules 3 and 9.
35. R36 — history only: an observation of the day; the next policies wait for friction.
