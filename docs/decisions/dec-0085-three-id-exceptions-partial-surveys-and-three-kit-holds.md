---
id: dec-0085-three-id-exceptions-partial-surveys-and-three-kit-holds
type: task-record
title: The id rule has three named exceptions, a survey may supersede a comparison in part, and kit checks hold the runner count, the guide scan block and the coverage pairs
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The id rule has three named exceptions, a survey may supersede a comparison in part, and kit checks hold the runner count, the guide scan block and the coverage pairs

## Context

The kit's hardcode audit of 2026-10-02 closed its findings in change groups. The closing group of 2026-10-11 took the items that rule: the kernel's `id` line, a gap in the research policy, three texts held by review alone, and the two lanes of the kit's own dials. The kernel's `id` line said an id "never changes after creation; never reused", with one exception, the landed collision of R7 of [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md#r7). Two other texts of the kit change an id: a number is provisional until its item lands, so a collision at a pull request renumbers the item not yet landed ([requirement A13.3](../requirements.md#a13-3), [A13.4](../requirements.md#a13-4)); and a kind that already has documents and enters catalog form renames each of them once, the procedure of [`const-catalogs`](../requirements.md#const-catalogs), which [dec-0017-records-numbered-now](dec-0017-records-numbered-now.md) and [dec-0034-research-and-policies-numbered](dec-0034-research-and-policies-numbered.md) had called a breach. The carry audit of this record found a fourth change, the widening of a full catalog, which the module offers and the kernel's cases did not name; section 5 rules it. [Rule 2 of plc-0005-research](../policies/plc-0005-research.md#r2) kept a comparison `active` while it was the module's current comparison and `inactive` once a later survey superseded it, and said nothing of a survey that covers some mechanisms only, which the kit has had since R2 of [dec-0066-interaction-reader-dials-and-entry-matching](dec-0066-interaction-reader-dials-and-entry-matching.md#r2). Three texts drifted with no check: the count a module document types on the Runner line of its section 10, which no check tied to the runner, so that all six documents carrying one were stale on the day; the count words "eleven" in the install guide and the README and the guide's hand list of scans; and the coverage pair of `const-task-close.coverage` that a new module owes, which nothing named and no check held, so that one module's hooks folder had stood outside its pair since the change that added it.

Five questions were put to the decider in chat on 2026-10-11, one per message, each with lettered options and one recommendation, the pick a letter; the numbered sections below hold them, two options having been corrected before the yes, on the audit's findings, and reading now as corrected. The two lanes of the kit's dials — the bare-law lane's fix naming the law that was cited, the kernel-section lane taking an end boundary and sections 1 to 7 — are routine changes of the kit as consumer zero, noted in their commits. Every module is a draft, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

<a id="r1"></a>**R1.** One pull request and one record for the closing group; the two lanes of the kit's dials and the two shortenings of over-ceiling documents are routine, each commit noting its call; the three holds are priced `process`, as the holds of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md) and [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md) were.

## 1. What the kernel's `id` line says of the changes an id takes

- **A. Creation is the landing.** The comment reads "never changes after it lands on the main branch; never reused"; the exception paragraph keeps the landed collision and adds adoption as a second exception.
  - **Pros:** a provisional number is no exception but the rule itself, which [requirement A13.3](../requirements.md#a13-3) already says; two exceptions, not three; the old migrations become the adoption case, named.
  - **Cons:** the comment the catalogs skill, the meta-types module and the frontmatter schema echo changes, so every echo is rewritten; "lands on the main branch" assumes a trunk, which the exception already does.
- **B. The comment stays; every change is a named exception.** "Never changes after creation; never reused" stands, and the exception paragraph lists three cases: the provisional number renumbered at a pull request before it lands, the landed collision, and adoption, each with "the id it leaves is never reused".
  - **Pros:** the rule's words stay as every citing text knows them; every change an id takes is stated where the rule is, none derived from a reading of "creation"; [requirement A13.3](../requirements.md#a13-3), [A13.4](../requirements.md#a13-4) and the catalogs texts then agree with the kernel word for word.
  - **Cons:** three exceptions to a five-word rule, the longest paragraph of the kernel's first section; the first exception restates [requirement A13.3](../requirements.md#a13-3) in the kernel, which [kernel §3](../../kernel/CONVENTIONS.md#k3) calls a module concern.
- **C. The kernel names the procedure, not the cases.** The comment stays; the exception paragraph says an id of a numbered kind changes only by the catalog procedure of the requirements document.
  - **Pros:** the kernel stays one short paragraph and points at the one place the procedure lives.
  - **Cons:** the kernel then relies on a requirements document for the content of its own rule, against [law 1 of CLAUDE.md](../../CLAUDE.md#law-1); the three cases are still listed in brief, so little is saved.

The session recommended B: the rule's words are cited in four places and stay true; each change an id takes becomes an explicit case where the rule is; the landed-collision paragraph already has the shape, so B extends it. The decider chose B in chat on 2026-10-11.

<a id="r2"></a>**R2.** The `id` rule of [kernel §1](../../kernel/CONVENTIONS.md#k1) keeps its comment and has three named exceptions, each for the items of a numbered kind and each leaving an id that is never reused. First, a number is provisional until its item lands on the main branch: where an item not yet landed meets, at a pull request, an item already landed under its number, the one not yet landed is renumbered — its file, its `id` and its references on its own branch — while the landed one keeps its number. Second, where two items of one catalog have both landed under one number, the one landed second is renumbered, its file and its `id` taking a number the catalog has not held and every reference to it in the tree rewritten. Third, where a kind that already has documents becomes a catalog, or a catalog's form changes, as when its width is widened, each of its documents not yet in that form is renamed once. Its file and its `id` take the catalog's form, and every reference to it in the tree is rewritten. The second case is the one R7 of [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md#r7) named; this record names the two beside it, and the "breach" of [dec-0017-records-numbered-now](dec-0017-records-numbered-now.md) and [dec-0034-research-and-policies-numbered](dec-0034-research-and-policies-numbered.md) is the third case.

## 2. A survey that supersedes a comparison in part

- **A. Partial supersession, named.** Rule 2 says a later survey may cover some mechanisms only; the module's current comparison is the newest, and the older is `inactive`, kept as the evidence for each mechanism the newer did not survey, the module's research line naming which comparison each mechanism cites; rule 7's "earns a new survey" names the reopened mechanisms as the new survey's scope.
  - **Pros:** it writes down what the kit already did, so no document changes status and R2 of [dec-0066-interaction-reader-dials-and-entry-matching](dec-0066-interaction-reader-dials-and-entry-matching.md#r2) stands; two sentences in the policy; a new survey costs only the mechanisms that reopened.
  - **Cons:** an `inactive` document is still consulted for the rest, which reads against the kernel's "inactive = no authority" until one recalls that a comparison never had any; the research line must carry the split.
- **B. Both active while each is current for something.** A partial survey leaves the older `active` for the mechanisms it still covers; `inactive` only once every mechanism has a later survey.
  - **Pros:** the kernel's lifecycle rule reads literally, the current account of a subject is `active`.
  - **Cons:** two active comparisons per module and rule 2's "the module's current comparison" becomes plural; the status flip is a sixth edit kind for a frozen document in rule 7; it reverses R2 of [dec-0066-interaction-reader-dials-and-entry-matching](dec-0066-interaction-reader-dials-and-entry-matching.md#r2).
- **C. No partial survey.** A later survey covers every mechanism, re-verifying from public sources what it does not reopen.
  - **Pros:** one comparison per module at a time; rule 2 stands unchanged.
  - **Cons:** the kit's own partial survey is frozen and would be in breach until a new full survey; every reopened mechanism then costs a re-survey of all the others.

The session recommended A: it states the rule the tree already follows, costs no status change and no reversal, and keeps a new survey priced by what reopened. The decider chose A in chat on 2026-10-11.

<a id="r3"></a>**R3.** Under [rule 2 of plc-0005-research](../policies/plc-0005-research.md#r2) a later survey may cover some of a module's mechanisms only: it supersedes the older comparison for those; the module's current comparison is the newest; the older, `inactive`, stays kept, as the evidence for each mechanism the later survey did not cover; and the research line of the module document names which comparison each mechanism cites. Under [rule 7 of that policy](../policies/plc-0005-research.md#r7) a new survey's scope is the mechanisms reopened or asked for. R2 of [dec-0066-interaction-reader-dials-and-entry-matching](dec-0066-interaction-reader-dials-and-entry-matching.md#r2) stands as an instance.

## 3. Three texts held by review: a kit check or text made true by hand

- **A. Hold the pair; drop the counts.** `scripts/check-gate-lists.py` holds that every module folder has one coverage pair whose code patterns name its folder and whose docs name its module document, and step 1 of "Developing a module" names the pair; the four count words are rewritten without a number; the scan list stays with the install-guide job and review.
  - **Pros:** the one silent drift that makes the range check skip a module gets a check; a count that no longer exists cannot drift; one hold, one case.
  - **Cons:** the guide's scan block stays unheld, so a new module's scan can be left out of the guide unseen; the README loses its headline number.
- **B. Hold the pair and the scan list; drop the counts.** As A, plus the check holds that the guide's `check=scan` block names every scan the module documents declare.
  - **Pros:** every list a new module must join is held by the one check that already holds the other lists; the guide cannot drift from the enforcement tables.
  - **Cons:** the check gains a reader of a fenced block of the guide, a file two kit checks then parse; two ruling items and two cases; a scan added later must edit the guide in the same change, a red met only in CI.
- **C. Text by hand only.** The four counts made true or dropped, the pair named in step 1, the scan list by review.
  - **Pros:** no new code; the pieces stay routine wording.
  - **Cons:** the pair's absence stays silent, which is the defect: a module with no pair is never asked for its document by the range check; the guide's scan list stays by review.

The session recommended B: both are lists a new module must join and both drift without a sound; the check that holds the other lists of step 1 is the natural home; the counts are dropped under every option, since a number in prose drifts without a sound. The decider chose B in chat on 2026-10-11.

<a id="r4"></a>**R4.** `scripts/check-gate-lists.py` holds the one fenced block of the install guide whose info string is `bash check=scan` to list, between `for s in` and `; do` on its first line, exactly the scans the module documents declare, each as `<module>/scripts/<name>.sh` with `<name>` the declared scan's name without `.py`; a module that declares no scan owes no path; a declared scan not listed and a listed path no module declares are each one finding naming the path to add or remove; the guide absent, the block absent or doubled, or its first line not of that form is a configuration failure. This narrows R3 of [dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md#r3), which left whether the guide is whole and clear to review: that the scan block lists the declared scans is now held, and a block the install-guide check does not run, the steps the reader writes by hand and whether the guide is otherwise whole and clear stay review.

<a id="r5"></a>**R5.** `scripts/check-gate-lists.py` holds every module folder to have its one pair in `const-task-close.coverage` of the kit's dials file: exactly one entry named after the folder; `docs` its module document alone; every `code` pattern under the module's folder; and, for each of the folders `scripts`, `hooks`, `skills` and `tests` the module has, the pattern `modules/<module>/<folder>/**` among them, a pattern for a folder the module does not have allowed; entries named for no module folder are not judged; the map absent, or not a list of entries each with a `name`, a `code` list and a `docs` list of strings, is a configuration failure. Step 1 of "Developing a module" names the pair and the guide's scan block among the places a new module is named.

<a id="r6"></a>**R6.** The install guide and the README name the modules without a count, since a number word drifts without a sound when a module is added. The lists a new module joins that `scripts/check-gate-lists.py` holds are the ones step 1 of "Developing a module" in CLAUDE.md names; the module table of the root README is held by review.

## 4. Where the hold on the hand-typed runner count lives

- **A. Inside `scripts/check-aspects.py --run`.** Where section 10's Runner line carries "N items green", the run compares N with the runner's last-line total and reds a mismatch with the fix naming both numbers; a Runner line without a count is not a finding.
  - **Pros:** the comparison sits where the total is already read, so no new script, no new gate-list entry, one case in the self-test; the per-module CI job runs it on every pull request.
  - **Cons:** the hold runs only under `--run`, the extra group, never in the gate group's quick scan; a document that drops its count escapes it, so the count stays optional.
- **B. A check of its own.** A new kit script with a self-test, an entry of the gate group, reading each runner's item list without running it.
  - **Pros:** held in the gate group, quick, on every run.
  - **Cons:** the harness has no way to list items without running them, so the check would parse the runners' source by regular expression; a new script, entry and self-test for one number.
- **C. Drop the six counts; hold nothing.** The Runner line states the command and its needs, no number, as the four other documents that carry a Runner line do; a fifth carries no Runner line.
  - **Pros:** no code; nothing to drift; the acceptance table already lists every item.
  - **Cons:** the audit's item asked for the check; a reader of a module document loses the one line that says how big its runner is.

The session recommended A: the total is already in hand under `--run`, so the comparison is one line and one case, run by CI on every pull request; B parses source for the same number at many times the cost, and C removes the sentence rather than holding it. The decider chose A in chat on 2026-10-11.

<a id="r7"></a>**R7.** `scripts/check-aspects.py --run`, with or without `--module`, holds, for each module whose runner ran, a count typed on the Runner line of the module document's section 10 — the first line outside code fences that opens with `Runner:` and holds `<digits> items green` — equal to the runner's total, a mismatch one finding naming both numbers and the exact edit; a Runner line without that form, or none, is no finding; the gate mode, which runs no runner, compares nothing.

## 5. A catalog's width widened

The carry audit's readers found on 2026-10-11 that the catalogs module offers to widen the `width` of a full catalog. Its limit 8 says "widening a catalog renames every item", and the fix texts of its `messages.py` and its catalog-item skill say the same. The kernel's three cases named only a kind that becomes a catalog, so the kernel forbade what the module offers. No catalog has been widened: width 4 holds 9,999 items.

- **A. Fold it into the third case.** The third case reads "where a kind that already has documents becomes a catalog, or a catalog's form changes, as when its width is widened, each of its documents not yet in that form is renamed once"; [requirement A5.8](../requirements.md#a5-8), the schema's description of `id` and the module texts stay.
  - **Pros:** every change an id takes stays named, as the choice in section 1 asked; one clause; widening is the act of adoption, a rename to the catalog's form, so it is no fourth case.
  - **Cons:** the kernel names a dial of one module by its effect.
- **B. A fourth named case.** The paragraph lists widening beside the other three.
  - **Pros:** the most explicit list.
  - **Cons:** a fourth sentence in the longest paragraph of the kernel for an act never performed; every text that counts "three" is rewritten.
- **C. The width fixed for a catalog's life.** Limit 8, the two fix texts and the skill stop offering a widening.
  - **Pros:** the kernel stays as chosen in section 1.
  - **Cons:** a full catalog has no path; four module texts and their golden lines change in this change's audit.

The session recommended A: it keeps the list complete without a new case, since widening is the act of adoption, and it leaves the module untouched. The decider chose A in chat on 2026-10-11.

<a id="r8"></a>**R8.** The third exception of [kernel §1](../../kernel/CONVENTIONS.md#k1) covers a catalog whose form changes, as when its width is widened, as it covers a kind that becomes a catalog: each of its documents not yet in that form is renamed once, every reference rewritten, the id left never reused; the catalogs module's limit on a full catalog and its fix texts stand.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the kernel and its schema, the policy, the two lanes, the two kit checks with their self-tests, the install guide, the README and step 1 of "Developing a module" in CLAUDE.md, and wrote the documents once after the code and tests had settled, every count made true; the commits after it correct the documents and this record before its yes, on the findings of its verification and of its carry audit. The message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [kernel §1](../../kernel/CONVENTIONS.md#k1), the paragraph of the three exceptions to the `id` rule, and [the frontmatter schema](../../kernel/schemas/document-frontmatter.schema.json), the description of `id`; [requirement A5.8](../requirements.md#a5-8), [A13.3](../requirements.md#a13-3) and [A13.4](../requirements.md#a13-4); [`const-referencing`](../../modules/const-referencing/MODULE.md#t12), item 5 of its deferred list; [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7), the link repaired after a renumbering or a rename; [rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), a renumbering that changes a record's id and file name only.
3. R3 — [rule 2 of plc-0005-research](../policies/plc-0005-research.md#r2) and [rule 7](../policies/plc-0005-research.md#r7), the scope of a new survey.
4. R4 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [rule 7 of plc-0011-install-guide](../policies/plc-0011-install-guide.md#r7); [rule 12 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12); [the module template](../../module-template/MODULE.md#t9), the enforcement paragraph of its section 9; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring.
5. R5 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI" and step 1 of "Developing a module"; [rule 12 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12); [check-gate-lists](../../scripts/check-gate-lists.py), its docstring.
6. R6 — [CLAUDE.md](../../CLAUDE.md), the section "Never in this repository".
7. R7 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [rule 12 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12); [the module template](../../module-template/MODULE.md#t10), the Runner line paragraph of section 10; [check-aspects](../../scripts/check-aspects.py), its docstring.
8. R8 — [kernel §1](../../kernel/CONVENTIONS.md#k1), the third exception; [requirement A5.8](../requirements.md#a5-8); [`const-referencing`](../../modules/const-referencing/MODULE.md#t12), item 5 of its deferred list; [`const-catalogs`](../../modules/const-catalogs/MODULE.md#t9), its limit 8.
