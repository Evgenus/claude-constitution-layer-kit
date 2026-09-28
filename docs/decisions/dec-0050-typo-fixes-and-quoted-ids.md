---
id: dec-0050-typo-fixes-and-quoted-ids
type: task-record
title: A typo fix is named in its commit and allowed in a frozen comparison; a deleted record quoted in a code span stays as written
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A typo fix is named in its commit and allowed in a frozen comparison; a deleted record quoted in a code span stays as written

## Context

The full carry audit of [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md), pinned at `0670486` on 2026-09-28, found three gaps older than that change and justified them there as out of its scope. Each concerns what may still change in a document that is otherwise fixed: an accepted record, or a comparison frozen under [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7). The three were put to the decider in chat on 2026-09-28, one per message, each with lettered options. They are recorded here together, since they amend the same rules. The change touches the kernel, so it is recorded whatever its size and is audited over every record ([rule 3 of plc-0002-kernel](../policies/plc-0002-kernel.md#r3)).

## 1. A deleted record's id or path in a code span

[Rule 7 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r7) turned every link to a deleted record into its title in plain words, "so nothing in the tree points at what is gone" — a promise from item 4 of [dec-0027-record-citations-optional](dec-0027-record-citations-optional.md). It spoke of links alone. Records and comparisons also quote ids and paths inside code spans: [dec-0005-reference-forms](dec-0005-reference-forms.md) shows the link syntax with a record's id as its example, and [res-0007-const-questions](../research/res-0007-const-questions.md) lists records by path as the data of a measurement. No edit the rules allow reaches a code span, so the promise could not be kept.

- **A. Narrow the promise to links.** No link points at what is gone; an id or a path quoted in a code span stays as written, as quoted evidence.
  - **Pros:** it promises what the rule's mechanism delivers; no quotation or measurement is falsified; one sentence and no new kind of edit.
  - **Cons:** a reader may meet a path to a file that no longer exists; the promise is weaker.
- **B. A deletion edit for code spans.** The code span becomes the deleted record's title in plain words, a new kind named in both policies.
  - **Pros:** the promise holds in full.
  - **Cons:** it rewrites quotations and measurement data; a syntax example loses its point; one more kind in two closed lists.
- **C. Keep such records.** A record quoted in a code span of an accepted record or a frozen comparison is not deleted.
  - **Pros:** no evidence is edited, and the promise holds.
  - **Cons:** records become undeletable for reasons that have nothing to do with them; every deletion first needs a search of every code span by hand.

**Recommendation:** A, by the session: a code span in a record or a comparison is a quotation or a measurement, and rewriting it changes evidence, which the freeze forbids; deletion is optional and has never happened.

**Choice:** A, chosen by the decider in chat on 2026-09-28.

**R1.** When a record is deleted, no link points at what is gone. An id or a path of the deleted record quoted in code — a code span or a fenced block — of a record or a frozen comparison stays as written: it is quoted evidence, and no edit reaches it. Anywhere else the deletion commit removes it, a comment or an entry of the dials file included. The deletion commit names the deletion and, where a record was edited, the migration.

## 2. A typo in a frozen comparison

The kernel lets a record's body take a typo fix at any time ([kernel §5](../../kernel/CONVENTIONS.md#k5)). A frozen comparison allowed four kinds of edit and no other, and a typo fix was none of them: a wording edit changes no word beyond the plain-word replacements of module [`const-language`](../requirements.md#const-language), and the dated inline note is for a fact found wrong.

- **A. A fifth kind: the typo fix.** It corrects a misspelt word, a doubled word or a wrong punctuation mark, and changes no fact, number, link, anchor, code span, handle or word of a quotation; the commit names it.
  - **Pros:** the same treatment as a record; the narrow definition keeps it near mechanical; a small fix stays small.
  - **Cons:** whether something is a typo is judgment, held by review; one more kind in a closed list; it widens a freeze [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md) set with care.
- **B. No typo kind.** A frozen comparison keeps its typos, and the rule says so.
  - **Pros:** the strictest freeze; nothing to judge.
  - **Cons:** misspellings stay in evidence for good; records and comparisons are treated differently for no reason.
- **C. A dated inline note.** The original stays and a note gives the right form.
  - **Pros:** the original is kept exactly; the freeze already has the mechanism.
  - **Cons:** heavy for a slip; notes clutter the text; a slip is treated as a wrong fact.

**Recommendation:** A, by the session: a comparison is evidence as a record is, and the kernel already trusts a typo fix in a record.

**Choice:** A, chosen by the decider in chat on 2026-09-28.

**R2.** A comparison frozen under rule 7 of plc-0005-research takes a fifth kind of edit, the typo fix. It corrects a misspelt word, a doubled word or a wrong punctuation mark, and changes no fact, number, link, anchor, code span, handle or word of a quotation. The commit names it a typo fix and names the comparisons it edits.

## 3. The commit word for a typo fix

Kernel section 5 listed three mechanical edits of a record's body and named the commit word for two: a reference-form migration and a wording edit. A typo carried none, so a claimed typo fix in an accepted record could not be told from an edit the rules do not allow, and a reader of the history had nothing to check it against.

- **A. Name it in the kernel.** Kernel section 5 says the commit names a typo fix, and the kit's policies refer to it.
  - **Pros:** the kernel's list becomes whole; every consumer gets the rule with the kernel.
  - **Cons:** a kernel change needs the carry audit over every record, the largest cost of the three.
- **B. Name it in the kit's policies only.**
  - **Pros:** the audit covers this change alone.
  - **Cons:** the kernel's list stays uneven, and a consumer's records get no word.
- **C. No word.** A typo fix shows in its diff.
  - **Pros:** nothing to write.
  - **Cons:** a claimed typo fix cannot be told from an edit that is not allowed without judging it, which is why the other two are named.

**Recommendation:** A, by the session: the gap is in the kernel's own list, which consumers adopt, and the audit in full is due before `0.1.0` in any case.

**Choice:** A, chosen by the decider in chat on 2026-09-28.

**R3.** A typo fix in a record's body is named a typo fix in its commit, as a reference-form migration and a wording edit are named, and the commit names the records it edits. For a record it is the same narrow kind R2 defines for a comparison, and it changes no ruling either.

## Applied

The commit that creates this record states R1 in rule 7 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r7), R2 in rule 7 of [plc-0005-research](../policies/plc-0005-research.md#r7), and R3 in [kernel §5](../../kernel/CONVENTIONS.md#k5) and in boundary example 9 of the module document of [`const-decision-records`](../requirements.md#const-decision-records). The first fix round of its carry audit corrected it in place before its yes: R1 reaches only quoted code in a record or a frozen comparison and names what is removed everywhere else, as the `mentions` scan of module [`const-referencing`](../requirements.md#const-referencing) already asked; R3 gives a record's typo fix the definition R2 gives a comparison's, stated once in rule 14 of plc-0004 and cited by rule 7 of plc-0005; the record-decision skill names the three commit words. The record is born `inactive`.

## Carry list

1. R1 — [rule 7 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r7).
2. R2 — [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7), with the definition in [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14).
3. R3 — [kernel §5](../../kernel/CONVENTIONS.md#k5); [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14); boundary example 9 in section 8 of [the module document of `const-decision-records`](../../modules/const-decision-records/MODULE.md#t8); section 4 of [the record-decision skill](../../modules/const-decision-records/skills/record-decision/SKILL.md).
