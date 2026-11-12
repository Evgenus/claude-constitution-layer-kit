---
id: dec-0115-long-documents-split-and-carry-entries-follow-moved-text
type: task-record
title: Three long documents split along their seams, and a record's citation follows text moved to another document
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Three long documents split along their seams, and a record's citation follows text moved to another document

## Context

On 2026-11-08 the scan of module [`const-doc-budgets`](../requirements.md#const-doc-budgets) found 17 documents over their character ceilings, at warning, about 192,000 characters over in all. The ceilings had 30 days of data behind them, so they could move to error. The decider asked to decide each document on its own, one question per message. The picks that are routine changes landed in two pull requests of that day: twelve ceilings re-set by the dial's rule and moved to error, the rollout plan's done items trimmed, and the install guide and seven module documents shortened as far as their rulings allow. This record holds the picks that change a policy, add a document kind or change what the kit's checks read: sections 1 to 6. Section 7 holds the ceilings they bring under, and section 8 a question the audit of this change raised.

Three of the documents are long because they hold text that only some readers need at some moments. The session guide, `CLAUDE.md`, loads in every session. The page of the shared code, `shared/GATE.md`, holds two long tables. The module template holds the rules for a module's Python code beside the slots a module document fills. Moving such text into a page of its own meets a constraint the decider did not have at the first picks: 67 of the kit's 114 records name one of the moved places in their carry lists, and those records are frozen. Sections 6 and 8 rule how they follow.

## 1. The session guide

`CLAUDE.md` stood at 45,037 characters against its `guide` ceiling of 24,000. Most of the size is in the bullet "The gate list and CI", about 10,150 characters, and the section "Developing a module", about 15,400. An agent needs the first only when it changes the kit's tooling, and the second only when it writes a module.

- **A. Split into two linked pages.** Move the two blocks each into a page of its own, a new document kind with its policy, the guide keeping one line per page that says when to read it.
  - **Pros:** every session loads less than half of the text; each rule keeps one current-state home and stays whole.
  - **Cons:**
    - **a new kind needs a policy first**;
    - **every record whose rulings live in those blocks must point to the new page**;
    - **a page read only on demand can be skipped**, like a skill.
- **B. Move "Developing a module" into a kit skill, and "The gate list and CI" into a page.**
  - **Pros:** the module procedure loads at its moment.
  - **Cons:** a rule that lives only in a skill drifts when the skill is not loaded, as [dec-0047-decision-shape-printed-at-session-start](dec-0047-decision-shape-printed-at-session-start.md) found.
- **C. Shorten in place.**
  - **Pros:** no new document.
  - **Cons:** about 21,000 characters must go from text that carries rulings.
- **D. Raise the ceiling by the rule to 50,000.**
  - **Pros:** no work.
  - **Cons:** every session keeps loading 45,000 characters.

The session recommended A, since this file costs every session and the two blocks are seams it already has. The decider chose A in chat on 2026-11-08.

<a id="r1"></a>**R1.** The bullet "The gate list and CI" of `CLAUDE.md` and its section "Developing a module" move whole into two pages, [the gate-list page](../guide/gate-list-and-ci.md) and [the module-development page](../guide/developing-a-module.md). In their place `CLAUDE.md` keeps one line each that says when the page is read and links it.

<a id="r2"></a>**R2.** The two pages are a document kind of their own, the kit's guide pages, under a new policy, [plc-0012-guide-pages](../policies/plc-0012-guide-pages.md), whose territory is `docs/guide/**`. They are `current-state`. A change to a rule they state is a `process` decision, as one to a rule of `CLAUDE.md` is ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)). A wording edit of them is routine.

## 2. The page of the shared code

`shared/GATE.md` stood at 125,148 characters against its `shared-code` ceiling of 75,000. Its [§3](../../shared/GATE.md#g3), the shared messages, is 28,469 characters, and its [§5](../../shared/GATE.md#g5), the shared acceptance items, 25,945. [Rule 1 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r1) wrote every shared message out "in this document".

- **A. Split the two tables into two pages of their own, beside `GATE.md`.**
  - **Pros:**
    - **a long table into a document of its own is the seam the length module's skill names first**;
    - **every message and item stays word for word**.
  - **Cons:** rule 1 and the policy's territory change; three kit checks that read the tables read them elsewhere; links into moved rows are repaired.
- **B. Shorten in place.**
  - **Pros:** one page, no policy change.
  - **Cons:** the page was cut to its rulings on 2026-10-12; another 50,000 characters cannot go without cutting rulings.
- **C. Raise the ceiling by the rule to 138,000.**
  - **Pros:** no work.
  - **Cons:** the page stays at 125,000.

The session recommended A, since the tables are a seam the page already has and B cannot reach the number without cutting rulings. The decider chose A in chat on 2026-11-08.

<a id="r3"></a>**R3.** The table of shared messages of [§3 of kit-shared-gate-code](../../shared/GATE.md#g3), with the paragraphs that lead it, moves to [the page of shared messages](../../shared/MESSAGES.md), and the table of shared acceptance items of [its §5](../../shared/GATE.md#g5), with its lead, to [the page of shared items](../../shared/ITEMS.md). The two sections keep their headings and anchors, each with one line that links its page.

<a id="r4"></a>**R4.** Every message the shared code prints is written out, word for word, on the page of shared messages. The territory of [plc-0009-shared-code](../policies/plc-0009-shared-code.md) holds the three pages. The kit's checks that read those tables — `scripts/check-copies.py`, `scripts/check-aspects.py` and `scripts/check-handle-forms.py` — read them on the new pages.

## 3. The module template

`module-template/MODULE.md` stood at 46,389 characters against its `module-template` ceiling of 23,000. Of its [§6](../../module-template/MODULE.md#t6), 11,144 characters are the sixteen gate-script rules: rules for the Python code a module ships, not slots its document fills, and no module document copies them.

- **A. Move the gate-script rules into a page of their own, and raise the ceiling to fit what is left.**
  - **Pros:** a seam the document already has; every rule stays word for word.
  - **Cons:** the ceiling still rises from 23,000.
- **B. A, then cut the slot guidance until the template fits 23,000.**
  - **Pros:** the number stays; every new module document starts from a shorter template.
  - **Cons:** the slot texts carry the rulings of many records, so the cuts risk losing one.
- **C. Raise the ceiling by the rule to 52,000.**
  - **Pros:** no work.
  - **Cons:** the template stays at 46,000.
- **D. Shorten in place to 23,000.**
  - **Pros:** one file.
  - **Cons:** half the file must go, nearly all of it rulings.

The session recommended A, since the code rules are a clean seam and a cut of the slot guidance puts rulings at risk. The decider chose B in chat on 2026-11-08.

<a id="r5"></a>**R5.** The sixteen gate-script rules move whole from [§6 of the module template](../../module-template/MODULE.md#t6) to [the page of gate-script rules](../../module-template/gate-script-rules.md), each keeping its number. That section keeps one line that links the page and says that every Python script a module ships follows all sixteen.

<a id="r6"></a>**R6.** The template's slot guidance is cut until the template fits its ceiling of 23,000. A cut takes only text that no record carries and that repeats another home. A carried text the template cannot keep moves to a page of the template folder that the slot links, and keeps its words.

## 4. The decision-record policy

[plc-0004-decision-records](../policies/plc-0004-decision-records.md) stood at 27,017 characters against the `policies` ceiling of 22,000, while every other policy is under 14,000. Rules 14, 6 and 2 hold over half of it.

- **A. Shorten its wording as far as every rule allows, then set the ceiling from it.**
  - **Pros:** the rule of the other picks of the day; the policy every record follows gets easier to read.
  - **Cons:** a policy rewording is a `process` change with its own audit.
- **B. Raise the `policies` ceiling by the rule to 30,000.**
  - **Pros:** no policy change.
  - **Cons:** ten policies that do not need it get the room.
- **C. A departure for this policy alone.**
  - **Pros:** the other policies keep a tight number.
  - **Cons:** a departure is for a document that must stand, and a policy can be rewritten.

The session recommended A, since it follows the rule of the other picks of the day and B gives room to policies that do not need it. The decider chose A in chat on 2026-11-08.

<a id="r7"></a>**R7.** The policy's wording is shortened as far as every rule allows: no rule is dropped or changed in what it binds, and what repeats the kernel, a module document or the template gives way to a link to that home.

## 5. The two frozen records over their ceiling

[dec-0093-module-evals-with-local-receipts](dec-0093-module-evals-with-local-receipts.md) stood at 35,810 characters and [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md) at 34,030, against the `records` ceiling of 34,000. [Rule 6 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6) brings an accepted record under its ceiling by the wording edits of rule 14 where they reach. It declares a departure for what they do not.

- **A. The edits rule 14 allows, then a departure for what they do not reach.**
  - **Pros:** the policy's own procedure; the other records keep 34,000.
  - **Cons:** those edits free a few characters each, so dec-0093 keeps nearly its size.
- **B. Raise the `records` ceiling by the rule to 40,000.**
  - **Pros:** no work.
  - **Cons:** every record gets 6,000 more room.
- **C. A departure at once.**
  - **Pros:** the least work.
  - **Cons:** it skips the step rule 6 asks for first.

The session recommended A for each, since it is the policy's own procedure and keeps the ceiling tight for every new record. The decider chose A for each in chat on 2026-11-08.

<a id="r8"></a>**R8.** Each of the two records takes the wording edits of [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) that are due in it, in this change, which has the carry audit those edits need. A record those edits do not bring under 34,000 is declared under `departures` of `const-doc-budgets` in `constitution.yaml`, by its path, allowed the ceiling `records`, with its reason.

## 6. A record's citation of text moved to another document

Sections 1 to 3 move text that records name as the home of their rulings: 41 records name a block of `CLAUDE.md` that section 1 moves, 22 a table of `shared/GATE.md`, 39 the section of the template that section 3 changes. Those records are accepted and frozen. The kernel allows a reference-form migration at any time ([kernel §5](../constitution/CONVENTIONS.md#k5)). Rule 14 of the decision-record policy listed the migrations a record may take, and a section moved into another document was not among them.

- **A. A new migration kind in rule 14, applied in the change that moves the text.**
  - **Pros:**
    - **every home stays true**, and a reader goes to the text in one step;
    - **it is the form the kernel already allows for a moved file**.
  - **Cons:** many frozen records are edited in one change, so the carry audit is large.
- **B. A forwarding home: the old place keeps a heading that links the page, and no record is edited.**
  - **Pros:** no frozen record is touched.
  - **Cons:** a home that does not state its ruling goes against [kernel §5](../constitution/CONVENTIONS.md#k5), and every reader takes two steps.
- **C. Split only `CLAUDE.md`, and raise the other two ceilings.**
  - **Pros:** fewer records edited.
  - **Cons:** it reverses the picks of sections 2 and 3.
- **D. Drop the three splits, and raise the three ceilings.**
  - **Pros:** no record edited.
  - **Cons:** it reverses the picks of sections 1 to 3.

The session recommended A, since it keeps every home true, in one step, by the form the kernel already allows for a moved file. The decider chose A in chat on 2026-11-08.

<a id="r9"></a>**R9.** Where a change moves the whole text of a place into another document, a record's link to that place takes, in the same change, the document and the anchor the text moved to, and only the link's target changes, with the link's text where it is the id of the document the text left, which takes the id of the document the text moved to: the record's other words keep the old name as history, as after a moved file. The commit names it a migration and names the move. [Rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) lists it among the migrations a record may take, which widens the closed list of those migrations that R4 of [dec-0082-handle-migration-in-records](dec-0082-handle-migration-in-records.md#r4) set.

## 7. The ceilings these sections bring under

<a id="r10"></a>**R10.** The ceilings `guide`, `shared-code` and `policies` each move to error in this change, over the window 2026-10-09 to 2026-11-08, each set to the longest of its documents as this change leaves them plus 10 %, rounded up to 1,000: not the window's longest, which is the size before this change. The ceilings `module-template` and `records` keep the numbers the picks of sections 3 and 5 kept, 23,000 and 34,000. They move to error over the same window. The guide pages stand under a ceiling of their own, `guide-pages`, set by the same rule, at warning until 30 days of data stand behind it.

## 8. A link to text that moved only in part

R9 says where a link goes when the text of the place it names moved whole. It said nothing of a link that names several places, or of one place whose text moved only in part. The audit of this change found such links placed two ways, and four wordings of a rule for them, written into R9 and rule 14 before acceptance, each read two ways by the next confirming reader. The decider was asked on 2026-11-09.

- **A. Keep the old target while any of the cited text still stands there.** A link moves only when nothing it cites is left at its old place. It then takes the place where the first text it cites now stands.
  - **Pros:**
    - **one yes or no question per link**, which a reader checks without reading what a ruling's first part is;
    - **it matches the rule for a moved file**, and it edits the fewest frozen records.
  - **Cons:** some links lead to a place that states only part of their ruling, so a reader takes a second step through that place's link.
- **B. Take the place that states most of what the link cites, a judgment the audit's readers hold.**
  - **Pros:** each link leads where most of its text is.
  - **Cons:** "most" is still a reading, so the readers may keep disagreeing.
- **C. Keep tuning the wording of the time.**
  - **Pros:** no link placed by the earlier rounds moves again.
  - **Cons:** four wordings had each been read two ways.

The session recommended A, since it turns each link into one yes or no question a reader can check. The decider chose A in chat on 2026-11-09.

<a id="r11"></a>**R11.** A link that names several places, or one place whose text moved only in part, keeps its target while any text it cites still stands there. When none does, it takes the place where the first text it cites now stands. A heading, or a line that only links where the text moved, is no text of a place and no text a link cites, save where that heading or line itself states a ruling the link cites. In a carry list, the text a link cites is the text that states a ruling of its entry. [Rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) states it beside the moved-place migration.

## Carry list

1. R1 — [CLAUDE.md](../../CLAUDE.md), its pointer lines in "Session conduct" and in "Developing a module"; [the gate-list page](../guide/gate-list-and-ci.md); [the module-development page](../guide/developing-a-module.md).
2. R2 — [plc-0012-guide-pages](../policies/plc-0012-guide-pages.md); [the dials file](../../constitution.yaml), the territory of that policy.
3. R3 — [kit-shared-gate-code](../../shared/GATE.md), [its §3](../../shared/GATE.md#g3) and [its §5](../../shared/GATE.md#g5); [the page of shared messages](../../shared/MESSAGES.md); [the page of shared items](../../shared/ITEMS.md).
4. R4 — [rule 1 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r1); [the dials file](../../constitution.yaml), the territory of that policy; [`scripts/check-copies.py`](../../scripts/check-copies.py), [`scripts/check-aspects.py`](../../scripts/check-aspects.py) and [`scripts/check-handle-forms.py`](../../scripts/check-handle-forms.py), their docstrings.
5. R5 — [template §6](../../module-template/MODULE.md#t6); [the page of gate-script rules](../../module-template/gate-script-rules.md).
6. R6 — [the module template](../../module-template/MODULE.md), its slots; [the slot-guidance page](../../module-template/slot-guidance.md), its opening; the cut of this change itself is history.
7. R7 — history only: the rewording of this change.
8. R8 — [rule 6 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6); [the dials file](../../constitution.yaml), `const-doc-budgets.departures`.
9. R9 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14); that it widens the list of R4 of dec-0082 is history.
10. R10 — [the dials file](../../constitution.yaml), `const-doc-budgets.ceilings`.
11. R11 — [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14).
