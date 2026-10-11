---
id: dec-0082-handle-migration-in-records
type: task-record
title: A handle cited in an accepted record follows its rename by a migration; a pronoun fix is a typo fix; a commit message names the source of every handle
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A handle cited in an accepted record follows its rename by a migration; a pronoun fix is a typo fix; a commit message names the source of every handle

## Context

A handle audit on 2026-10-11 found handles that collide or name nothing, and the pull requests of that day fixed them. Some fixes edited accepted records. [Rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) allows an accepted record only a typo fix, a reference-form migration in the sense of [kernel §5](../../kernel/CONVENTIONS.md#k5), and the wording edits of its closed set, and a wording edit "alters no … existing handle". So those fixes stand outside the rule. Four questions followed from them, each put to the decider in chat on 2026-10-11, one per message. The audit also left one known gap, ruled on in section 5.

## 1. The order of the rulings of dec-0033

The rulings of [dec-0033-referencing-module-rulings](dec-0033-referencing-module-rulings.md) run R1 to R17, then R21, R22, R23, R26, R25, R24, R27, and its section 12 holds R18 to R20. No other record breaks the order. [Rule 10 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r10) says handles run in order. That sentence came with [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md) on 2026-09-24; dec-0033 was accepted on 2026-09-22, and rule 14 of plc-0004 never edits an accepted record to fit a later rule. No document in the tree cites R18 to R27 of [dec-0033-referencing-module-rulings](dec-0033-referencing-module-rulings.md#r18), but seven commit subjects on `main` do.

- **A. Renumber R18 to R27 to the order of the file,** and migrate every citation.
  - **Pros:** the record reads in order; a check of the order needs no exception.
  - **Cons:** no edit of rule 14 of plc-0004 allows it; it rewrites the carry list, which rule 2 of plc-0004 forbids; the seven commit subjects would then name the wrong rulings.
- **B. Leave dec-0033 as it is, and say why;** the order holds from dec-0039 on.
  - **Pros:** no handle moves, so the commit subjects stay true; it follows rule 14 as written; a check of the order gets a clear first number.
  - **Cons:** dec-0033 stays out of order for its readers; the check does not reach every record.
- **C. Move only R24 to R26 inside section 11.**
  - **Pros:** no handle changes, so every citation stays true.
  - **Cons:** moving paragraphs is no edit of rule 14 of plc-0004 either; R18 to R20 still stand after R27; it fixes only part of the order.

The session recommended B: the order rule came after the record, rule 14 keeps such a record as it is, and B alone needs no exception. The decider chose B.

<a id="r1"></a>**R1.** The sentence of rule 10 of plc-0004 that handles run in order, contiguous and unique in the record, tables included, holds from dec-0039 on, the record that brought it. An earlier record keeps the handles it was accepted with, though from record 30 on no ruling handle opens two ruling items, as `scripts/check-carry-lists.py` already held. The order and the contiguity of handles are review, and so is the uniqueness of handles other than the bold ruling handles.

<a id="r2"></a>**R2.** R1 narrows R9 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r9), which ruled that sentence for every record, to the records from dec-0039 on, save the uniqueness of ruling handles, held from record 30 on. R4 narrows R12 of the same record, that an accepted record is never edited to fit a later rule: case (ii) may bring a citation in an earlier record to the qualified form that rule 10 of plc-0004 asks.

<a id="r3"></a>**R3.** dec-0033 stays as it is: no ruling of it is renumbered or moved.

## 2. How a cited handle follows a rename

The fixes of 2026-10-11 edited handles in accepted records in three ways.

- **Renamed in another document.** A citation followed a rename made there: item L1 of the live items of two modules to V1 in [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md), message H1 to B2 in [dec-0052-doc-budgets-module-rulings](dec-0052-doc-budgets-module-rulings.md), message S1 to Z1 in [dec-0066-interaction-reader-dials-and-entry-matching](dec-0066-interaction-reader-dials-and-entry-matching.md), some of them in carry lists.
- **Bare, or of a document outside the repository.** A citation was qualified or set in plain words:
  - The bare "R4" of a message key in dec-0033 to "message key R4".
  - The bare `A12` in [dec-0005-reference-forms](dec-0005-reference-forms.md), [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md) and [dec-0058-ci-runs-each-check-in-parallel](dec-0058-ci-runs-each-check-in-parallel.md) to a link to the aspect.
  - D3, D7 and D9 of an audit report the repository does not hold to plain words in [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md), [dec-0044-styling-module-rulings](dec-0044-styling-module-rulings.md) and [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md).
  - The names C0, DEL and C1 to code point ranges in [dec-0067-task-close-trunk-remote-and-own-closing-clauses](dec-0067-task-close-trunk-remote-and-own-closing-clauses.md).
- **The record's own keys.** The table keys R1 to R4 of [dec-0034-research-and-policies-numbered](dec-0034-research-and-policies-numbered.md) became C1 to C4, and H1 in dec-0039 became "top-level heading".

Options:

- **A. A handle migration, as a named case of the kernel's reference-form migration.** Rule 14 of plc-0004 names three cases in which a citation of another document's handle is rewritten. The edits of the record's own keys stay departures.
  - **Pros:** no kernel change, since it fits a class the kernel already allows; narrow and explicit; it also covers a citation of a handle that names nothing.
  - **Cons:** the two edits of the record's own keys stay departures; a future clash of a record's own keys needs a record of its own.
- **B. A new wording kind (g),** covering citations of other documents and the record's own keys that are no ruling handles.
  - **Pros:** every edit of the day is covered; one kind for every handle fix.
  - **Cons:** wider; renaming a record's own keys is close to rewriting the record; dec-0034 is older than the sentence of rule 10 of plc-0004 its keys broke, so it was never at fault.
- **C. No new kind.** Every edit of the day is a departure, and each future handle fix in an accepted record needs a record of its own.
  - **Pros:** rule 14 of plc-0004 stays as it is; each such edit is examined in full.
  - **Cons:** heavy for a citation that only follows a rename; renames elsewhere leave stale citations behind.

The session recommended A: it uses a class of edit the kernel already allows, it is the narrow form, and the edits of the record's own keys are better recorded than allowed. The decider chose A.

<a id="r4"></a>**R4.** A handle migration is a reference-form migration in the sense of [kernel §5](../../kernel/CONVENTIONS.md#k5), the ruling untouched. Where a record cites a handle of another document, its carry list included, the citation of the handle changes in three cases and no other. A migration of the citation's link stands as its own rule says: to a renumbered record, as rule 14 of plc-0004 says; to a deleted record's title, as rule 7 of plc-0004 says, the handle kept; to the anchor of a ruling, in the form rule 2 of plc-0004 gives. (i) That document renamed the handle: the citation takes the new one, and a link's fragment that holds the handle follows it. (ii) The handle stands bare, and a reader could take it for a key of the record or of the kit: it is qualified by its document's name or by a link to that document, in a carry list only where the link leads to no record, as rule 2 of plc-0004 says. (iii) Its document lies outside the repository and was never in it, or holds no item under that handle: the handle becomes the plain words it stood for. In each of the three cases the new words stand where the grammar of the sentence needs them, and nothing else in the sentence changes. The first sentence of rule 14 of plc-0004 names, as a closed list, the edits by which an accepted record may meet a later rule: a typo fix, a wording edit of a kind rule 14 lists, the module link of rule 6 of plc-0004, and the qualified handle, the plain words and the ruling's anchor of rule 14. A migration that follows a document moved, renumbered or deleted, or a handle renamed, as case (i), is the kernel's, at any time. A link that only qualifies a handle in a carry list is no home, as rule 2 of plc-0004 says. The commit names it a migration, and names the rename in case (i) and the case in (ii) and (iii).

<a id="r5"></a>**R5.** The edits of the first two groups above were handle migrations, made before R4 named them, save three. "Message key R4" in dec-0033 is qualified by its kind, not by its document, and its list item gained a bold lead. In dec-0044 and dec-0046 the word "first" moved and the bold lead grew. These three, and the two edits of the record's own keys in dec-0034 and dec-0039, were no edit that rule 14 of plc-0004 allows. Nor was the edit of the frozen comparison [res-0008-const-interaction](../research/res-0008-const-interaction.md), where D3 and D7 became plain words, leaving a capital after a semicolon: [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) allows no handle migration. The six stand as departures, since undoing them would be a second such edit.

## 3. A gendered pronoun in an accepted record

The fixes of 2026-10-11 changed "his" and "he" to "their" and "they" in R1 and R21 of [dec-0033-referencing-module-rulings](dec-0033-referencing-module-rulings.md#r1) and in the choice of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md). No gendered pronoun is left in the tree. A pronoun is no handle, so R4 does not reach it.

- **A. A new wording kind (g) for a gendered pronoun,** the verb made to agree, a quotation never changed.
  - **Pros:** the three edits become allowed; a later slip is fixed without a record.
  - **Cons:** a new kind with no case left today; rule 14 of plc-0004 grows; making the verb agree is a small judgment a reader must check.
- **B. No kind:** the three edits stand as departures.
  - **Pros:** rule 14 of plc-0004 does not grow; the tree is already clean.
  - **Cons:** three departures that no one disputes; a later slip in an accepted record costs a record.
- **C. A case of the typo fix.**
  - **Pros:** light, with no carry audit, as any typo fix; it covers the three edits and a later slip.
  - **Cons:** it stretches the word "typo", since a pronoun is not misspelt; a verb that must agree changes a second word.

The session recommended A, as an explicit kind that a reader checks. The decider chose C. The session noted that [kernel §5](../../kernel/CONVENTIONS.md#k5) names a typo without defining it, so C widens the word, and that the carry audit's readers may question it. The question named an accepted record. Since [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) makes the typo fix of a frozen comparison the one kind rule 14 of plc-0004 defines, the session took the case for both, so that one kind stays one.

<a id="r6"></a>**R6.** A typo fix of rule 14 of plc-0004 also corrects a gendered pronoun that stands for a person: he, him, his, himself, she, her, hers or herself becomes the form of they that the grammar asks, they, them, their, theirs or themselves, and the verb of its clause is made to agree. It changes no word of a quotation, as every typo fix. The typo fix stays one kind for a record and for a frozen comparison, so [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) takes the same case.

<a id="r7"></a>**R7.** R6 widens the kind that R2 of [dec-0050-typo-fixes-and-quoted-ids](dec-0050-typo-fixes-and-quoted-ids.md#r2) defined for a comparison and that its R3 made the same for a record. It also widens the reading of the kernel's word "typo" that R4 of [dec-0031-record-amended-until-its-yes](dec-0031-record-amended-until-its-yes.md#r4) brought into the kernel's text.

<a id="r8"></a>**R8.** The three edits of the day in dec-0033 and dec-0020 were typo fixes, made before R6 named them.

## 4. Handles in commit messages

Many commit subjects on `main` — 49 by the count of the handle audit of 2026-10-11 — cite handles of the report of an audit of hard-coded values, such as G4 B1, S2 part 3, P5 and N22. That report is not in the repository, so the handles read as keys of the kit. The chat rule of [CLAUDE.md](../../CLAUDE.md#references) has a handle name its source when a citation crosses the boundary of its message, decision or session, and says nothing of commit messages. History is never rewritten.

- **A. In CLAUDE.md, for documents outside the repository only.**
  - **Pros:** it targets exactly the failure seen; small.
  - **Cons:** a handle local to a session can still stand bare in a commit, and a later reader cannot find its source either.
- **B. In CLAUDE.md, for every handle,** each naming its source unless it is a key of a tracked document named in the same message.
  - **Pros:** it closes the whole class; it carries the boundary test of the chat rule to commits.
  - **Cons:** a little longer to write; review alone holds it, and "named in the same message" takes judgment.
- **C. In the chat rule of module [`const-referencing`](../requirements.md#const-referencing),** for every consumer.
  - **Pros:** every consumer gets the rule.
  - **Cons:** it changes a module for a failure no consumer has hit, which the kit's growth rule forbids; a module change and its version.

The session recommended B: a handle local to a session fails a later reader as one of an outside document does, and B stops both. The decider chose B.

<a id="r9"></a>**R9.** Every handle in a commit message names its source. A key of a tracked document names that document in the same message. A handle of a document outside the repository names that document. A handle local to a session or a chat names the work or the decision it came from. The chat rule of the referencing module carries this for a handle local to a message, a decision or a session; the rest is the kit's own. Review holds it.

<a id="r10"></a>**R10.** The commit subjects that cite handles of the audit report stay as they are.

## 5. A reversal that names no handle

[Rule 13 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r13) asks a reversing record to name the reversed item by record and handle. R10 of [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md#r10) replaces part of the second item of R16 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r16) — that the review is complete "from rollout Phase D in the pull request" — without naming R16. Both records are accepted: rule 13 leaves the reversed record untouched, and no mechanical edit adds a pointer to the reversing one. No choice existed.

<a id="r11"></a>**R11.** The gap stays as it is, known and recorded here.

## Applied

The change that creates this record states R1 in rules 10 and 6 of plc-0004, R4 in its rules 14 and 2, R6 in its rule 14, R6 in rule 7 of plc-0005 too, and R9 in the reference rule of CLAUDE.md. By case (iii) of R4, it rewrites two citations that named an "R4" of dec-0001, whose ruling list has no handles, as "the fourth item of the ruling list" of that record: one in section 9 of dec-0042, one in the section "Applied" of [dec-0081-rulings-carry-anchors](dec-0081-rulings-carry-anchors.md). The record is born `inactive`.

## Carry list

1. R1 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r10), rule 10, and its [rule 6](../policies/plc-0004-decision-records.md#r6), what is left to review.
2. R2 — history only: the narrowing of two earlier rulings.
3. R3 — history only: dec-0033 is left as it was accepted.
4. R4 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), rule 14, the handle migration and the closed list of its first sentence; its [rule 2](../policies/plc-0004-decision-records.md#r2), the link that is no home.
5. R5 — history only: the edits of 2026-10-11 and the six departures.
6. R6 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), rule 14, the typo fix; [plc-0005-research](../policies/plc-0005-research.md#r7), rule 7.
7. R7 — history only: the widening of three earlier rulings.
8. R8 — history only: the pronoun edits of 2026-10-11.
9. R9 — [CLAUDE.md](../../CLAUDE.md#references), the reference rule.
10. R10 — history only: the commit subjects of the audit of hard-coded values.
11. R11 — history only: a finding of the day.
