---
id: dec-0068-enforcement-tables-destination-classes-and-kit-checks-held
type: task-record
title: Kit checks read an enforcement table whatever a row's indent, a mode that is no tree scan marked in its cell, hold the destination classes against the preamble and every kit check in the gate group
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Kit checks read an enforcement table whatever a row's indent, a mode that is no tree scan marked in its cell, hold the destination classes against the preamble and every kit check in the gate group

## Context

An audit of the kit's hardcoded logic on 2026-10-02 found that several of the kit's own checks read documents in ways one ordinary edit could turn into a silent green. Each case was probed again on the trunk on 2026-10-06:

- **The enforcement table.** `scripts/check-gate-lists.py` and `scripts/check-bare-install.py` found a module's declared scans only in rows that start `| E` and only in spans of the exact form `<entry> --scan`. An indented row, a bold handle, or a scan written `sh scripts/x.sh --scan` dropped out with no word: the gate list could lose the scan and both checks stayed green, and the bare-install proof ran no scan. The two rows of the kit that hold another mode — const-interaction's explain and const-doc-budgets' history report — were left out only because something follows the flag; no rule said so.
- **The destination classes.** `scripts/check-aspects.py` treated a matrix row as a module's only when its Destination cell opened `M<n>`. A cell worded another way, such as "module `const-x`", took its row out of that check silently. [Rule 7 of plc-0007-requirements](../policies/plc-0007-requirements.md#r7) already makes the destination classes a closed set defined once in the preamble of the requirements document; no check held it.
- **The kit checks themselves.** The kit checks are listed by hand in `scripts/gate-list.sh`. A new `scripts/check-*.py` left off that list would be linted and typed, and never run in CI.

The same audit found more such cases that change no rule: a decisions section found by its number; the carry-list check's own copy of the records' folder and width; the matrix's rows, anchors and module folders read without a guard; the shared-links check's list of shared test files typed by hand; the type-check entries typed by hand. The change fixes them too, at routine stakes, each noted in its commit: one kit reader, `scripts/kit_module_doc.py`, finds a module document's section by its anchor and fails loud on a missing or doubled one; the carry-list check reads the `dec` catalog of `constitution.yaml`; the shared-links check derives its list from `shared/tests/`; the type-check entries use globs.

The change is on one branch. No module's code changes, and the two module documents it edits belong to drafts, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). The decider kept the audit's recommended fixes when reading the change's plan on 2026-10-06. Eight questions were put to the decider in chat that day, one per message, each with lettered options and one recommendation, the pick a letter; sections 1 to 7 hold them, the last raised by the change's own carry audit.

## 1. One pull request and one record

The rulings on the table's form, the destination classes and the kit checks have `process` stakes; the rest of the change is routine. Before that, the decider priced the carry-list check reading `constitution.yaml` routine: [rule 3 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r3) already names the `dec` catalog entry as the declared source, and the catalog gate already holds the naming rule the check's new failure repeats. The question was how the change reaches the trunk.

- **A. One pull request, one record** for the `process` rulings, the routine pieces noted in their commits.
  - **Pros:** the least work, one audit and one yes; the table's reader extends the section reader, so both are reviewed in order on one branch; no consumer is hit today, so nothing waits.
  - **Cons:** the routine fixes wait for the whole change, about one working day; the audit reads every file of the branch; the audit's scope is computed by a script the same branch changes.
- **B. The routine pieces first**, as their own pull request with no record, then the `process` ones with this record.
  - **Pros:** four silent greens leave the trunk within hours; the second change is small.
  - **Cons:** two verifications, two runs of the gate list and two yeses, about two to three more hours.
- **C. The `process` part left out** and logged.
  - **Pros:** the smallest change, with no record and no audit.
  - **Cons:** the silent cases of the table and of the destination cells stay open.

The session recommended A: no consumer exists and the kit trips none of these cases today, so B's speed buys nothing anyone uses. The decider chose A in chat on 2026-10-06.

**R1.** One pull request and one record for the rulings of sections 2 to 4 and 7; the rest of the change routine, noted in its commits.

## 2. A mode that is no tree scan

Two rows of the kit hold a `--scan` span that is no tree scan for CI to run: const-interaction's explain, `check-destructive --scan --command <text>`, and const-doc-budgets' history report, `check-budgets --scan --since <date>`. The question was how the check tells a declared scan from another mode.

- **A. By form**: `<entry> --scan` alone declares; `<entry> --scan --<flag> …` is another mode; any other span with `--scan` in the table is a finding.
  - **Pros:** no module document changes; one clause in the template; it describes how the documents are already written.
  - **Cons:** a real tree scan written with a flag after it is read as another mode and never held; the reading is implicit, by form alone.
- **B. By an explicit mark**: a row whose span has a flag after `--scan` also holds the words `not a tree scan`, or the span is a finding; the two rows gain the words.
  - **Pros:** closes A's silent case; each mode that is no tree scan is declared on purpose and visible; an outright rule, not a reading.
  - **Cons:** two module documents change; a few more records in the audit's scope; a fixed phrase authors must type exactly.
- **C. Strict form**: only `<entry> --scan`; any other span with `--scan` a finding, so the two rows are rewritten without one.
  - **Pros:** the narrowest reading, with no exception and no mark.
  - **Cons:** the two documents would stop showing the command a user types; it fights the documents instead of reading them.

The session recommended A: today's documents follow it, and the clause makes the reading a written rule. It named B as the right pick for an outright rule at a small cost. The decider chose B in chat on 2026-10-06.

**R2.** A module's enforcement table ([template §9](../../module-template/MODULE.md#t9)) is read row by row, whatever a row's indent: a row opens with `E<n>`, bold or not, and any other first cell is a finding. A code span in a row that holds `--scan` reads `<entry> --scan`, a declared scan, held in the gate list and CI; or `<entry> --scan --<flag> …` in a row whose cell holding the span also holds the words `not a tree scan` outside a code span, a mode that is no tree scan and not declared. Any other span holding `--scan` in a row is a finding, and so is a span in the declared form in the prose of the section. A declared span stays declared when the mark stands beside it, since the mark only licenses the form with a flag. This amends in part R2 of [dec-0056-portability-grep-and-gate-lists](dec-0056-portability-grep-and-gate-lists.md), whose declared form is unchanged; dec-0056 is not touched.

**R3.** const-interaction's row of its explain and const-doc-budgets' row of its history report carry the mark.

## 3. Where the destination classes live

The four classes — **kernel §n**, **Mx**, **binding**, **template** — stand in the preamble of the requirements document, and all 69 cells open with one of them. The question was where the check gets the set.

- **A. Typed in the check, tied to the preamble**: the four classes and their patterns a constant; the plain run reads the preamble's bold class names and fails to run when they are not exactly the four.
  - **Pros:** an outright list in the code, tested over the whole set; the tie turns any change of the preamble red until both agree; the patterns written once, where they are used.
  - **Cons:** two places to edit when a class is added, held together by the tie; one more read of prose.
- **B. Read from the preamble at each run.**
  - **Pros:** one source, the one rule 7 names; a new class is one edit.
  - **Cons:** the preamble writes placeholders, not patterns, so a typed map is needed anyway; it parses a prose sentence; a reworded preamble changes what the check accepts unless that parse is guarded too.
- **C. The check left out** and logged.
  - **Pros:** one piece less; no new read of prose.
  - **Cons:** a destination worded another way still takes its row out of the check with no word; the closed set stays held by review alone.

The session recommended A: the patterns must be typed somewhere in any case, and the tie keeps the typed list from drifting without a red. The decider chose A in chat on 2026-10-06. The change built the tie into every run of the check, `--run` included, where the option as put named the plain run; R4 states what was built.

**R4.** `scripts/check-aspects.py` types the closed set of destination classes — `kernel §n`, `Mx`, `binding`, `template` — with their patterns, matched at the start of a Destination cell, a link read for its text. A cell that opens with none is red, beside the reds R7 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md) lists; dec-0054 is not touched. Every run reads the bold names of the preamble's sentence "Destination classes: …" and fails to run when the sentence is missing or its names are not exactly the four.

## 4. Every kit check in the gate group

The type-check entries now take every kit script by glob, so a new kit check is typed; nothing held that it is run. All eleven kit checks run today. The question was whether to hold it.

- **A. Leave it logged**, its signal a kit check found missing from CI.
  - **Pros:** no growth; the kit's rule against machinery for failures no consumer has hit; CLAUDE.md untouched, so the audit does not grow.
  - **Cons:** the hand list of kit checks stays unguarded; a forgotten check would look shipped and run nowhere.
- **B. Fold it in**: check-gate-lists red when a tracked kit check is run by no entry of the gate group; CLAUDE.md's sentence on what it holds gains the clause.
  - **Pros:** every kit check held in CI by a check, not by care; it closes the last hand list the audit found; the fix can teach the exact line to add.
  - **Cons:** one more piece; CLAUDE.md touched, which adds the records that cite it to the audit's scope.

The session recommended A: a new kit check is added rarely and on purpose, in a reviewed pull request. The decider chose B in chat on 2026-10-06.

**R5.** `scripts/check-gate-lists.py` is red when a `scripts/check-*.py` that git tracks at the top of `scripts/` is run by no entry of the list's gate group: no command line of a gate entry runs `python3 scripts/check-<x>.py`. A library beside the checks, such as `scripts/kit_module_doc.py`, is no check.

## 5. The shared-links check's list

`scripts/check-shared-links.py` named the shared test files a module owes by hand; a fourth file in `shared/tests/` was owed by no module and the check stayed green.

- **A. Derive the list from the folder**, with a floor of the three files GATE.md names.
  - **Pros:** one source, the folder; a new shared file owed by every linking module from the commit that adds it; no list in the code to drift.
  - **Cons:** the list no longer readable in one place in the code; a stray file there turns every module red until removed; the floor is still a short list typed by hand.
- **B. Keep the hand list, add a guard** that is red on a shared file the list does not name.
  - **Pros:** the list explicit in the code, matching GATE.md word for word; code, GATE.md and links forced to change together.
  - **Cons:** three steps where one would do; still a copy of the folder, now guarded.

The session recommended A: the folder is the only source that cannot be wrong about itself, and the floor keeps a derived list from shrinking silently. The decider chose A in chat on 2026-10-06.

**R6.** `scripts/check-shared-links.py` takes the links a module owes from `shared/tests/` itself — each `.py` file at its top whose name starts with neither `.` nor `_` — and fails to run when `shared/const_gate/` or one of the three files GATE.md names is gone. Kit tooling at routine stakes.

## 6. Cases the inventory found

The inventory of every place a kit check reads a document found three more cases, all in check-aspects: an indented acceptance item dropped from the plain run; a matrix row written twice, the second hiding the first; and a module listing that skipped no `.` or `_` folder, unlike its siblings, and skipped a folder with no module document silently.

- **A. Leave all three logged.**
  - **Pros:** no growth.
  - **Cons:** the pieces rewrite those reads yet leave a silent green standing in them.
- **B. Fold in the two silent greens**; the module listing stays for a later change.
  - **Pros:** both in lines the pieces already change, one test case each.
  - **Cons:** the change's scope moves again.
- **C. Fold in all three.**
  - **Pros:** check-aspects agrees with check-gate-lists on module folders.
  - **Cons:** it answers one part of the question "which folders are modules" in one script while the other answers stay apart; a loud inconsistency, not a silent green.

The session recommended B: both silent greens sit in functions the change already rewrites and cost one test case each, while the module listing is loud and belongs with a single answer to "which folders are modules" in a later change. The decider chose C in chat on 2026-10-06.

**R7.** `scripts/check-aspects.py` reads the rows of a module's rows section and acceptance table whatever their indent, fails to run when two lines of the matrix open with the same row or aspect anchor, skips a folder of `modules/` whose name starts with `.` or `_`, and fails to run on one that holds no module document. Kit tooling at routine stakes.

## 7. A qualifier before a destination class

[Rule 7 of plc-0007-requirements](../policies/plc-0007-requirements.md#r7) said a class may carry a qualifier before or after it. Its examples are enforcement classes, but the sentence covered both closed sets. The check of R4 classes a Destination cell at its start, so a cell with a qualifier before its class would be red against the policy's words. All 69 cells put the class first, and the module check R7 of dec-0054 rules also reads a module's number at the cell's start.

- **A. Narrow rule 7 for destinations**: a destination class opens its cell, its qualifiers after it; the check unchanged.
  - **Pros:** it matches all 69 cells and both checks that read the cell, so neither can go quiet; one clause in a policy the change already edits; no code change.
  - **Cons:** it narrows a policy's allowance; a writer who wants a qualifier first must reorder the cell.
- **B. Read the class anywhere in the cell**, as rule 7 allowed.
  - **Pros:** the policy stays as written; the check follows its words.
  - **Cons:** the module check of dec-0054 still reads at the start, so a cell with a qualifier first would be classed and still missed by it, a silent narrowing; fixing that check too is one more piece and touches dec-0054's ruling.
- **C. Justify, change nothing**, reading "qualifier before" as the enforcement classes' alone.
  - **Pros:** no work.
  - **Cons:** it rests on a reading, not the rule's words; a future cell with a qualifier first meets a red that contradicts the policy.

The session recommended A: it is the only option that keeps both checks of the cell loud and in agreement at no code cost, and it writes down what all 69 cells do. The decider chose A in chat on 2026-10-06.

**R8.** A Destination cell opens with a destination class, its qualifiers after it, the template still free to stand beside another class as the rest of rule 7 says; an enforcement class may carry a qualifier before or after it. This narrows rule 7 of plc-0007-requirements for destinations, in the same change.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests and the documents; the message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The commit that adds this record adds a row for it in section 4 of const-interaction's and const-doc-budgets' module documents, and corrects three docstrings its review found loose. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [the module template](../../module-template/MODULE.md#t9), section 9, its sentences on the form of a declared scan; [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI", on what `scripts/check-gate-lists.py` holds; [the reader](../../scripts/kit_module_doc.py), its docstring of `enforcement`; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring; [rule 12 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12), what holds the table's form. The amendment in part of R2 of dec-0056-portability-grep-and-gate-lists is history.
3. R3 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t9), its row E2 of section 9; [`const-doc-budgets`](../../modules/const-doc-budgets/MODULE.md#t9), its row E3 of section 9.
4. R4 — [check-aspects](../../scripts/check-aspects.py), its docstring, its red list and its modes; [rule 9 of plc-0007-requirements](../policies/plc-0007-requirements.md#r9), its exceptions to review. The red added beside R7 of dec-0054-acceptance-items-name-their-rows is history.
5. R5 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring.
6. R6 — [GATE.md §2](../../shared/GATE.md#g2), item 7; [check-shared-links](../../scripts/check-shared-links.py), its docstring.
7. R7 — [check-aspects](../../scripts/check-aspects.py), its docstring; [rule 9 of plc-0007-requirements](../policies/plc-0007-requirements.md#r9), for the matrix's lines and anchors.
8. R8 — [rule 7 of plc-0007-requirements](../policies/plc-0007-requirements.md#r7), its clause on a destination class.
