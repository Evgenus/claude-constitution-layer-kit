---
id: dec-0027-record-citations-optional
type: task-record
title: Citing a record is optional provenance; records stay as evidence, each deletable once its ruling is carried, and a new record closes with a carry list
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Citing a record is optional provenance; records stay as evidence

## Context

[Kernel §5](../../kernel/CONVENTIONS.md#k5) says an applied ruling lives in the current-state documents it changed and a record is provenance, never authority. On 2026-09-19 and 2026-09-20 the decider asked whether that holds in fact — whether every record could be removed without anyone losing a rule. All twenty-six records were audited by readers who checked each ruling item against the current-state text.

What the audit found:

1. No current-state document relies on a record. Every citation reads as provenance: the sentence is complete without its link.
2. Eleven ruling items lived only in a record. Most were of one shape: a deferred trigger, a fallback, an exception — items that change no file on the day they are ruled, so the record's list of applied files never shows them missing. They are carried now, in commits `83d5c2f`, `cd04c14`, `251df8b`, `053a0f6`, `138d142` and `11a8593`.
3. Three places made citing a record mandatory, so no record could go even when fully carried: [template §4](../../module-template/MODULE.md#t4) defined a module's decisions list as record ids; [plc-0007-requirements](../policies/plc-0007-requirements.md) rule 2 said "the row cites its record", which the matrix had never followed; and six error texts of `scripts/check-references.sh` named records by path, where no link checker reads.
4. Most records are linked from other records, and the kernel lets a record be edited in place only as a reference-form migration. Whether unlinking a deleted record is one was not said anywhere.

A choice was needed on what the records are for once everything is carried.

## Options

- **A. Keep the records as evidence; make citing them optional.** Carry what is missing, reword the rules that require a citation, delete nothing now.
  - **Pros:** no kernel change; the options and reasoning stay one click away; a later deletion costs only the removal of links.
  - **Cons:** the folder of records keeps growing, in mild tension with the kernel's "the working tree holds only current truth".
- **B. Delete every record in one act after the repairs.** Amend the kernel's evidence clause, the template's decisions section and the intent page; provenance becomes the commit.
  - **Pros:** the tree holds current truth only; the question of editing surviving records never arises.
  - **Cons:** a kernel change; reasoning reachable only through git; [requirement A5.6](../requirements.md#a5-6) allows commit hashes only in commit messages, record bodies and chat, so it would change too; module `const-decision-records` would govern an empty territory in the kit, which weakens its live proof.
- **C. Drain gradually.** A record is deleted once nothing links to it, as [kernel §1](../../kernel/CONVENTIONS.md#k1) already says; links are stripped when someone passes by.
  - **Pros:** uses the rule as written; no single large change.
  - **Cons:** one record links ten others, so almost nothing drains until that one does; a permanent half-state.

## Recommendation

A, by the session. The decider's test — no need to rely on any decision directly — is a property of the current-state documents, and A delivers that property in full without spending a kernel change on it. B buys tidiness at the price of the kit's own traceability and of the second module's live proof, and nothing has yet hurt enough to earn that.

As first argued in chat, A said a deleted record's place in a module's decisions list is taken by "its record, or the commit". That was wrong — it would put commit hashes into documents against [requirement A5.6](../requirements.md#a5-6) — and was corrected before the choice was applied: nothing takes the place.

## Choice

A, by Eugene Chernyshov in chat on 2026-09-20; then, the same day, "lift read-only, apply fixes, keep decision files".

## Ruling

1. **[Template §4](../../module-template/MODULE.md#t4).** A module's decisions list cites a record while the record exists. When a record is deleted its entry goes with it and nothing replaces it; a ruling below recorded stakes has no entry. The clause "or, below recorded stakes, the commit that noted it" is gone.
2. **Requirements policy, rule 2.** A row states its rule in full; citing a record beside it is optional provenance.
3. **No record is deleted by this ruling, and none has to be.** A carried, `inactive` record binds nothing and is kept as evidence; whether anything should still reference it, in the words of [kernel §1](../../kernel/CONVENTIONS.md#k1), is the decider's judgment, not a count of links. Deleting one later is routine and one commit: its links removed, the record removed, the commit naming the record and calling the change a deletion. An `active` record is never deleted.
4. **Unlinking inside a surviving record is a reference-form migration** in the sense of [kernel §5](../../kernel/CONVENTIONS.md#k5): the link becomes the deleted record's title in plain words, never its id, so nothing in the tree points at what is gone; the citation changes form, the ruling does not. The kernel's text already covers it — "rewriting how a record cites other documents, its ruling untouched" — so the kernel is not changed; the decision-record policy says it.
5. **Carry list.** A record's last section pairs every ruling item, deferred triggers and fallbacks included, with the current-state text that states it. An item that binds is always carried; "history only" is for an item that binds nothing — a one-time act, a finding of the day. Advisory. Records numbered below `0027` carry no list.
6. **Carry check.** Before the yes, the author puts each item as a question and a reader holding the current-state documents and not the record answers it; what that reader cannot answer is carried, or justified in the commit message. Advisory; for a module it is a second pass of the fresh-context validation.
7. **The matrix amendments made ahead of this record are under it.** Rows [A5.5](../requirements.md#a5-5) and [A5.6](../requirements.md#a5-6) and the specification of [`const-referencing`](../requirements.md#const-referencing) were amended in commits `83d5c2f`, `251df8b` and `11a8593` as repairs. Amending a row is `process` stakes under the requirements policy, so this record and its yes cover them; each restates a ruling of [dec-0005-reference-forms](dec-0005-reference-forms.md) and adds none, except the sentence describing the gate's new lane.

## Carry list

1. Item 1 — [template §4](../../module-template/MODULE.md#t4), first paragraph.
2. Item 2 — [plc-0007-requirements](../policies/plc-0007-requirements.md), rule 2.
3. Items 3 and 4 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 7.
4. Item 5 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 2.
5. Item 6 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 2, and step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md).
6. Item 7 — history only: the rows state their rules; that they were amended under this record is provenance.
