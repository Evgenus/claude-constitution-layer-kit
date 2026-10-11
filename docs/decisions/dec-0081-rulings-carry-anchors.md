---
id: dec-0081-rulings-carry-anchors
type: task-record
title: Every ruling of a decision record carries an anchor, and a citation from another document links it
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Every ruling of a decision record carries an anchor, and a citation from another document links it

## Context

[Requirement A5.5](../requirements.md#a5-5) asks every citable unit of a kit document for an explicit anchor with a short fixed key, and [requirement A5.6](../requirements.md#a5-6) asks a reference across documents to be a link to the target's anchor. A policy's rules meet both: each stands after its anchor, `r<n>`, and a citation reads "rule 5 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5)". A record's rulings met neither. A handle audit on 2026-10-11 found 51 records numbering 443 rulings, none with an anchor, and about 125 citations of a ruling from another document, each of which could open only the record's file. Only [dec-0005-reference-forms](dec-0005-reference-forms.md) anchored its items, as `r1` to `r20`.

`scripts/check-carry-lists.py` reads a ruling's handle wherever it stands on its line, so an anchor before the handle changes nothing it reads.

## Options

- **A. Anchor every ruling, old and new, and link every citation.**
  - **Pros:** every ruling becomes linkable and [requirement A5.5](../requirements.md#a5-5) holds everywhere; one form in the kit, held by a gate; the citation rewrites are reference-form migrations, which [kernel §5](../../kernel/CONVENTIONS.md#k5) allows.
  - **Cons:** it adds an anchor to 51 accepted records, against rule 14 of plc-0004; the largest of the three changes, with a full carry audit.
- **B. Anchors only from the next record on,** the rule and its gate starting at that number.
  - **Pros:** no accepted record is touched; small.
  - **Cons:** two forms in the kit for good; the existing citations still open only the file.
- **C. No anchors:** [requirement A5.5](../requirements.md#a5-5) narrowed, a ruling cited by a link to its record and its handle.
  - **Pros:** one requirement row changes and nothing else.
  - **Cons:** it weakens a requirement to fit current practice; a reader still searches the file for the ruling.

## Recommendation

The session recommended A: the decider had chosen the explicit and stricter rule before, even at a cost, a gate keeps the form from drifting again, and the citation rewrites are edits the kernel already allows.

## Choice

The decider chose A in chat on 2026-10-11, the session noting that an anchor added to an accepted record was none of the wording edits rule 14 of plc-0004 then allowed, and that rule 14 keeps an accepted record from being edited to fit a later rule beyond those edits. The carry audit of this record found that the kernel allows the edit once the policy lists it: [kernel §5](../../kernel/CONVENTIONS.md#k5) admits a wording edit of any kind the records' policy lists in a closed set, and the anchor changes no meaning, fact, number or reference. R4 lists it; with it, the objection no longer stands.

## Ruling

<a id="r1"></a>**R1.** Every ruling handle of a decision record stands right after the explicit anchor of its own key — `<a id="r1"></a>` before the handle R1 — in every record whatever its number.

<a id="r2"></a>**R2.** A citation of a ruling from another document links that anchor, its record's id the link's text, as `R7 of [dec-…](…#r7)`; several rulings named at once link the first. A carry list cites no ruling of another record by a link, since its links lead to no record, and a frozen research comparison keeps the form it was frozen with.

<a id="r3"></a>**R3.** `scripts/check-carry-lists.py` holds R1 in every record, before every bold ruling handle outside fenced blocks: a ruling with no anchor, or after the anchor of another key, is a finding. Whether a citation links its anchor is review.

<a id="r4"></a>**R4.** The anchor of R1, set right before an existing bold ruling handle of the same number with no other character changed, is a wording edit of the closed set of rule 14 of plc-0004, its kind (f); the commit that makes it names it a wording edit and names the records it edits.

<a id="r5"></a>**R5.** An anchor may stand right before the bold handle or name that opens a numbered rule or ruling — a policy's rule, a record's ruling — beside its own line and a table row's first cell, the two places [requirement A5.5](../requirements.md#a5-5) named.

## Applied

The commits before the one that creates this record apply every item. The first gave the 443 rulings of 51 records their anchors, and turned the citations of a ruling in records and in current-state documents into links to them; a short id became the record's full id as the link text. It restored the carry lists that pass had rewritten, and left the research comparisons as they were frozen. The second stated the rule in plc-0004, gave the record template the anchor, and taught `scripts/check-carry-lists.py` to hold it. The fixes of the carry audit stated R4 and R5, linked the citations the first pass had missed, and narrowed the check to handles with no suffix letter, which no record uses. A citation of a record whose items carry no bold handle, such as R4 of dec-0001, stays as written, having no anchor to link. The record is born `inactive`.

## Carry list

1. R1 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r2), rule 2, and its rule 6 for every record whatever its number.
2. R2 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r2), rule 2; [CLAUDE.md](../../CLAUDE.md#references), the reference rule, where a frozen comparison keeps its form.
3. R3 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6), rule 6; [`scripts/check-carry-lists.py`](../../scripts/check-carry-lists.py), `check_anchors`; [CLAUDE.md](../../CLAUDE.md), step 6 of "Developing a module".
4. R4 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), rule 14, kind (f).
5. R5 — [requirement A5.5](../requirements.md#a5-5); [the skill `referencing`](../../modules/const-referencing/skills/referencing/SKILL.md), section 2.
