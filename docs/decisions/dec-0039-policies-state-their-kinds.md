---
id: dec-0039-policies-state-their-kinds
type: task-record
title: Every policy states the shape of its kind — an enforcement rule, anchored rules that keep their numbers, a change rule, and the conventions its documents already keep
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Every policy states the shape of its kind — an enforcement rule, anchored rules that keep their numbers, a change rule, and the conventions its documents already keep

## Context

On 2026-09-24 the decider asked for every policy of the kit to be checked against the documents it governs, and for what each policy should also state. The nine policies were read, with the kernel, the intent page, the requirements document, the rollout plan and the shared-code page; the thirty-eight records, the six module documents and the six research comparisons were read by fresh readers, one kind each. The documents comply with their policies almost everywhere; the policies are thin. Eight of nine skip the Enforcement rule the policy template asks for. No policy anchors its rules, though rules are cited by number in seventeen places, and a renumbered rule would silently break accepted records, which are not edited. Most policies say far less about a kind's shape than its documents already practise: the records keep a section order, a handle form and a way of naming the decider that the decision-record policy does not state; the module documents share an envelope, handle prefixes, an evidence form and a way of importing the shared texts that the module-document policy does not state; the research policy's provenance rule admits public sources only, while every comparison rests on its own experiments and on the kit's tree.

Defects found on the day, beside the thin policies:

- **the record template the `templates` dial pointed at** carries no carry list and no handles, so a record written from it fails `scripts/check-carry-lists.py`;
- [dec-0037-dials-file-block-style](dec-0037-dials-file-block-style.md) was born `active` though applied in its creating commit;
- [dec-0009-module-routine-validation-and-inputs](dec-0009-module-routine-validation-and-inputs.md) received a pointer to its reversing record after its yes, called a migration;
- **three records** are `inactive` with pending entries while two older ones stayed `active` in the same situation;
- **the requirements document** had two headings of the first level, a column named "one line" over rows of six hundred characters, row [A6.9](../requirements.md#a6-9) between [A6.2](../requirements.md#a6-2) and [A6.3](../requirements.md#a6-3), and a horizon paragraph of intent not yet real;
- **the intent page** claimed enforcement by a CI that does not exist;
- **the rollout plan's done lines** had grown into narratives.

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

<a id="r1"></a>**R1.** Every policy carries an Enforcement rule, stating which module guards which field of its kind at write time and in its scan, and what stays judgment.

<a id="r2"></a>**R2.** Every rule of every policy carries an explicit anchor `r<n>` inside its item, before the bold name; from another document a rule is cited as a link to its anchor, "rule n of <policy id>" being the link's text or the words that carry it; a rule keeps its number and anchor for life, a withdrawn rule keeps its number and says so, and a new rule takes the next number. The seventeen citations of a policy's rule in the tree were migrated to the anchored form in this change, the records among them under the reference-form migration of [kernel §5](../constitution/CONVENTIONS.md#k5).

<a id="r3"></a>**R3.** Amending a rule of a policy is a `process` decision; carrying an already-ruled item is routine; a mechanical edit is routine. The policy template, `templates/policy.md`, is the shape, and a rule that changes the shape changes the template in the same change.

<a id="r4"></a>**R4.** A policy's body opens with the sentence the template writes, its title is "<Kind> policy — <clause>" — the root's, whose kind is *policy*, "Root policy — <clause>" — and every rule opens with a bold name; the root policy and the decision-record policy, which broke the form, were brought into it in this change.

### 2. The kernel policy, [plc-0002-kernel](../policies/plc-0002-kernel.md)

<a id="r5"></a>**R5.** A kernel change is `process` stakes at the least, runs the carry audit in full, and where it touches a section the shared gate code implements changes that code and bumps every module that links it. Sections keep their `k` numbers; a new one takes the next. The admission test is the kernel's own preamble, with the git-derivability razor of the intent page beside it. The schemas are the page's machine half, held with the text by the coverage pair `kernel-schemas` and with the shared mirror by `scripts/check-schema-mirror.py`. Every example in the page obeys the page's rules and names no id of the kit and no path that resolves only here — a conventional path a consumer would use as well is no reference to the kit.

### 3. The intent policy, [plc-0003-intent-page](../policies/plc-0003-intent-page.md)

<a id="r6"></a>**R6.** The page's content is the six sections it holds, adding one being a change under its change rule; the page speaks in the present tense, a mechanism not yet built named as planned with a link to the plan's step; a principle added after the founding set cites the record that earned it; sections carry `i<n>` and principles `p<n>`. The claim of enforcement by CI is rewritten as a link to step 10 of the plan.

### 4. The decision-record policy, [plc-0004-decision-records](../policies/plc-0004-decision-records.md)

<a id="r7"></a>**R7.** A record is written from the kit's own template, `templates/decision-record.md`, named for the kind in `const-locations.templates`: the shape the record skill of module [`const-decision-records`](../requirements.md#const-decision-records) ships to every consumer, with what the policy's rules 2, 9, 11 and 12 add, which are the kit's rules and no module's — so the module's template stays within its rows. A change to the shape rules changes the template in the same change.

<a id="r8"></a>**R8.** The sections and their order are fixed for both shapes; a record answering several questions has one numbered section per question, with its context, options, recommendation, choice and handled ruling; the title states the ruling and the top-level heading repeats it.

<a id="r9"></a>**R9.** A ruling item is any sentence that binds after the yes, wherever it stands, a default left open to override included — the test being the blind reader; handles run in order, contiguous and unique in the record, tables included, a key of another document written qualified; one kind of home per handle, with the split or the after-link history for a mixed item.

<a id="r10"></a>**R10.** A record is `inactive` once every item has its home in the sense of rule 2 — current-state text, "history only", or "pending" in the plan, the write-head that holds unreal intent, which is how the kit reads the kernel's "applied" — and `active` only while an item has none — a `product` record, having no window, cannot grow and follows this alone; a record not applied in its creating commit because it grows while its change is made is born `active` and set `inactive` in the commit that names its yes or ends its review. This settles the two readings the records took, in favour of the newer, and this record, grown through its two slots, follows it.

<a id="r11"></a>**R11.** The body says "the decider"; the Choice names where and when; a commit hash appears for a pin or for a deleted file that is no record only.

<a id="r12"></a>**R12.** An accepted record is never edited to fit a later rule, whatever the rule; a rule that applies from a number on names the threshold.

<a id="r13"></a>**R13.** The defects of the day are not repaired in the records: [dec-0037-dials-file-block-style](dec-0037-dials-file-block-style.md) keeps its history of a wrong birth status, and the sentence added to [dec-0009-module-routine-validation-and-inputs](dec-0009-module-routine-validation-and-inputs.md) stays — an accepted record is not edited, and both are provenance only.

<a id="r14"></a>**R14.** A reversing record names the reversed item by record and handle, the reversal itself is carried "history only", and the reversed record is not touched: a pointer added to an accepted record is new content, not the mechanical edit of [kernel §5](../constitution/CONVENTIONS.md#k5). The slot was put to the decider with two options — A, the reversed record untouched; B, a kernel change admitting a supersession pointer as a third mechanical edit — the session recommending A, since the reversal is found through the reversing record and the audit's provenance sort and the kernel stays as it is; A chosen by the decider in chat on 2026-09-24.

<a id="r15"></a>**R15.** Every record of the kit so far is `process`.

<a id="r16"></a>**R16.** An `architecture` record's review is the two passes of step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md), every finding fixed or justified:

- **a fresh reader** holding the record, the current-state documents it changes and the policy, never the authoring reasoning, then the carry audit;
- **the review** is complete when the decider says so, in chat or from rollout Phase D in the pull request, the commit that names it carrying the trailers of [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5) as the receipt, so the correction window closes at the review's end as the kernel has it;
- **a reviewer other than the decider** replaces the first pass once the kit has a second human, by an amendment under [rule 3 of plc-0001-root-policy](../policies/plc-0001-root-policy.md#r3).

A `product` record, which the kernel gives neither a yes nor a review, is complete when committed and has no window: the audit runs on the commit that holds it, a finding is fixed in the documents or by a further record and never by editing it beyond the kernel's mechanical edits; the commit with the fixes carries the `Carry-Audit:` trailer alone, and the gate's note that it awaits a yes is the honest limit of a gate that does not read stakes. The slot was put to the decider with three options — A, the two passes plus the yes; B, a second human reviewer; C, the slot left open — the session recommending A, since it is the kit's existing review made mandatory at the higher stakes, B naming a blocker no record could pass today and C a deferred question inside a policy; A chosen by the decider in chat on 2026-09-24. The audit's rounds corrected the draft before the yes: its "routine amendment" against rule 3 of the root policy, its ceremony for a `product` record against the kernel's, the first pass without inputs for a record that is no module's, and the review fixed in chat past Phase D.

### 5. The research policy, [plc-0005-research](../policies/plc-0005-research.md)

<a id="r17"></a>**R17.** Provenance is a public source, a numbered experiment of the document that a reader could repeat, or the kit's tree at a named commit; a tool read and not run is marked so; an earlier comparison is never a source; nothing cites an input outside the repository.

<a id="r18"></a>**R18.** The shape is the template's, `templates/research-comparison.md`, section by section, with the verdicts of the summary a closed set: CONFIRMED, OVERTURNED, build, not needed.

<a id="r19"></a>**R19.** A comparison is frozen when the record that accepts its module is accepted: a fact found wrong is annotated inline with the date, a finding on the module as built goes into the module document, and a platform change, a module revision or the decider's request earns a new survey under a new number, the older set `inactive` in the same commit.

<a id="r20"></a>**R20.** No rule lives in a comparison and no document relies on one; modules, comparisons and records are named by name or id, never by ordinal; "the specification" is the module's stub, linked; a comparison is written by a subagent from the template.

<a id="r21"></a>**R21.** The six comparisons written before these rules stand as written, under R19.

### 6. The module-document policy, [plc-0006-module-documents](../policies/plc-0006-module-documents.md)

<a id="r22"></a>**R22.** The envelope is `current-state`, `active`, id `module-<plugin name>`, title `const-<name> — <one clause>`, and the preamble's first sentence states the manifest version; the three documents whose title was the bare name gained their clause in this change.

<a id="r23"></a>**R23.** The document changes with its code under the coverage map; a change to a rule it states is `process`, any other edit routine; a version bump edits the preamble's version sentence, which after publication reads "Published at manifest version `x.y.z`." Anchors `t1` to `t12` are the template's; a section is added to the template, never to one document.

<a id="r24"></a>**R24.** One prefix per kind of handle in a document, never reused for another kind: the message keys as `messages.py` names them; `E<n>` for the enforcement rows; the acceptance items numbered from 1 for the module's own and from 101 for the shared, bare or under `T<n>` and `S<n>`; the live, review and kit-check items continuing the module's own numbering or under `L<n>`, `V<n>` where `L` is the message prefix; a key of another document written qualified. Three enforcement tables gained their `E` column, two sibling lists their numbers, and the live and review items of `const-locations` became `V1` to `V4` in this change; the first audit found the draft's stricter prefixes broken by four of the six documents and the rule was widened to what they keep.

<a id="r25"></a>**R25.** The shared texts enter by link to [kit-shared-gate-code](../../shared/GATE.md), its sections 3 to 5; the module's own messages are written out word for word.

<a id="r26"></a>**R26.** A live proof carries its date, environment and platform version; a deferred one is labelled `live, deferred` and links the plan's step; a platform fact carries its date and what breaks. Kit-live counts are such evidence, and links to kit documents are the description's own: the kit is no project, and the portability grep holds the installed components.

<a id="r27"></a>**R27.** The files are listed once, in the artifacts section; the plugin skeleton is not copied into the document — removed from the two that carried it.

### 7. The requirements policy, [plc-0007-requirements](../policies/plc-0007-requirements.md)

<a id="r28"></a>**R28.** A row keeps its number for life, stands in number order, states its rule in full at any length; the `†` flag is defined. Row [A6.9](../requirements.md#a6-9) was moved after [A6.8](../requirements.md#a6-8) and the column renamed in this change.

<a id="r29"></a>**R29.** The destination and enforcement classes are closed sets defined once in the preamble — the enforcement classes were written out there in this change; a row's recommended enforcement stays the recommendation, confirmed or overturned by the comparison, what shipped stated in the module document's enforcement section.

<a id="r30"></a>**R30.** One heading of the first level, the matrix first, the specifications after it under their anchors, nothing that is neither a requirement nor a specification: the second first-level heading was lowered in this change, and the horizon paragraph on the knowledge layer was removed — the intent page already frames that layer as not this repository's, and the plan holds steps, which the paragraph was not; the policy names no home for a layer to come.

### 8. The rollout-plan policy, [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md)

<a id="r31"></a>**R31.** Phases carry `phase-<letter>` and steps `s<n>`; steps are numbered once across phases and keep their number, a later one standing as `<n>a`.

<a id="r32"></a>**R32.** A step done is marked in one sentence with the date, the record — its title in plain words once the record is deleted — and "the yes given"; evidence lives in the record and the module document. The done lines of Phase A and Phase C were cut to this form in this change.

<a id="r33"></a>**R33.** The plan is the home a "pending" entry points at, and a step so named closes with its intent carried; the plan is `inactive` when step 11 is done; the last phase holds no rule and points at the intent page and the policies.

### 9. The shared-code policy, [plc-0009-shared-code](../policies/plc-0009-shared-code.md)

<a id="r34"></a>**R34.** Sections carry `g<n>`; an acceptance item's number is never reissued; an observed platform fact names version, date, backstop and fallback; a change to the code updates the page in the same change and bumps every linking module; a part not built is listed with its signal.

<a id="r35"></a>**R35.** A module may be pointed at by its ordinal in the order of authoring, which the plan resolves and which never changes; the equality of the messages table with the code is review until a friction earns a check.

### 10. Across the nine

<a id="r36"></a>**R36.** Twenty-five Markdown files lie in no territory, the kit's record template now among them — `CLAUDE.md`, the README, the templates, the skills, the install notes. The constitution is silent there, so this is no defect, and no policy is written for them by this record; a session-guide kind and a templates kind are the next policies the kit will want, when friction says so.

<a id="r37"></a>**R37.** Found by the audit and ruled here: the link to a deleted record becomes its title in plain words inside a frozen research comparison, an edit the freeze allows by name beside a dated annotation, a later survey's `inactive` and a link repaired by the mover after a move, made by it or by hand; and in a done line of the plan, a routine edit — not only inside another record; this widens items 3 and 4 of [dec-0027-record-citations-optional](dec-0027-record-citations-optional.md) without reversing them.

## Carry list

1. R1 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r8), rule 8, and [templates/policy.md](../../templates/policy.md), rule 3.
2. R2 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r7), rule 7, and [templates/policy.md](../../templates/policy.md), rule 1; the migration of the seventeen citations is history.
3. R3 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r3), rule 3.
4. R4 — [plc-0001-root-policy](../policies/plc-0001-root-policy.md#r4), rule 4; the two policies brought into the form is history.
5. R5 — [plc-0002-kernel](../policies/plc-0002-kernel.md#r3), rules 3 to 7.
6. R6 — [plc-0003-intent-page](../policies/plc-0003-intent-page.md#r3), rules 3 to 6, and [INTENT.md](../../INTENT.md#i5), the sentence on the [aspect A12](../requirements.md#a12) gates; the rewriting of that sentence is history.
7. R7 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r8), rule 8, and the `templates` dial of [constitution.yaml](../../constitution.yaml).
8. R8 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r9), rule 9.
9. R9 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r10), rule 10.
10. R10 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r11), rule 11; which reading the older records took is history.
11. R11 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r12), rule 12.
12. R12 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), rule 14.
13. R13 — history only: a finding of the day, left as it is.
14. R14 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r13), rule 13; the options put and the pick are history.
15. R15, R16 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r15), rule 15; the options put, the pick and the audit's corrections are history.
16. R17 — [plc-0005-research](../policies/plc-0005-research.md#r3), rule 3.
17. R18 — [plc-0005-research](../policies/plc-0005-research.md#r5), rule 5.
18. R19 — [plc-0005-research](../policies/plc-0005-research.md#r7), rule 7.
19. R20 — [plc-0005-research](../policies/plc-0005-research.md#r4), rules 4, 8 and 9.
20. R21 — [plc-0005-research](../policies/plc-0005-research.md#r10), rule 10.
21. R22 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r5), rule 5; the three titles given their clause is history.
22. R23 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r6), rules 6 and 7.
23. R24 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r8), rule 8, and the handles paragraph of [template §10](../../module-template/MODULE.md#t10); the columns, numbers and renamed items of the day, and the audit's finding that widened the rule, are history.
24. R25 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r9), rule 9.
25. R26 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r10), rule 10, and rule 3.
26. R27 — [plc-0006-module-documents](../policies/plc-0006-module-documents.md#r11), rule 11; the two removals are history.
27. R28 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r6), rule 6; the move of a row and the renamed column are history.
28. R29 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r7), rule 7, and the preamble of [constitution-requirements](../requirements.md); that the classes were written out on the day is history.
29. R30 — [plc-0007-requirements](../policies/plc-0007-requirements.md#r8), rule 8; the lowered heading and the removed paragraph are history.
30. R31 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r4), rule 4.
31. R32 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5; the cut done lines are history.
32. R33 — [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r6), rules 6 and 7.
33. R34 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r4), rules 4 to 8.
34. R35 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r3), rules 3 and 9.
35. R36 — history only: an observation of the day; the next policies wait for friction.
36. R37 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r7), rule 7, [plc-0005-research](../policies/plc-0005-research.md#r7), rule 7, and [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md#r5), rule 5; what it widens of an older record is history.
