---
id: dec-0120-falling-grade-after-a-write-is-a-note
type: task-record
title: After a write, a grade above the ceiling that is below the grade of the last commit is a note, not a finding
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# After a write, a grade above the ceiling that is below the grade of the last commit is a note, not a finding

## Context

Module [`const-language`](../requirements.md#const-language) checks a covered document after every write. The grade rule is a rule over the whole document. So a long page above its grade ceiling was red after every edit, until one edit brought the whole page under the ceiling. A page cannot come down in one edit when it is long. Each step of the work got a `RED` block and the line that names the skill, though the step did what the finding asked.

The carry audit of [dec-0115-long-documents-split-and-carry-entries-follow-moved-text](dec-0115-long-documents-split-and-carry-entries-follow-moved-text.md) found this on 2026-11-09, and [item 9.34 of the rollout plan](../rollout-plan.md#s9-34) holds it. The kit's own descent to the module's defaults, [item 9.6 of that plan](../rollout-plan.md#s9-6), lowers the ceiling in steps and then edits many long pages. It waits on this change.

Three facts framed the choice. The hook runs after the write and refuses none, so the cost of the old design was the red message alone. The scan holds the ceiling whatever the hook says. And the hook cannot see the text before the edit: the shared pipeline gives a module the document after the write and nothing else, so "before the edit" needs a baseline that the module can read by itself.

## Options

- **A. Falling against the last commit is a note.** The hook also reads the written document as the last commit holds it. Above the ceiling, but below its grade there, the finding becomes a note that names both grades. A document that is new, that the commit holds at or under the ceiling, or that is not lower stays red.
  - **Pros:** no hidden state, since the verdict depends on the tree and the last commit alone; one edit at a time works; an edit that makes a committed page worse is still red; the note reaches the model with the numbers.
  - **Cons:** one more git call and one more file for Vale at a covered write; an edit that raises the grade, but leaves it below the last commit's, is only a note; a new page above the ceiling stays red at each edit until it is committed or under.
- **B. Falling against the last check of the session is a note.** The hook keeps the last grade it saw for each page in a state file and compares with that.
  - **Pros:** it compares edit with edit; it covers new pages that no commit holds.
  - **Cons:** the verdict depends on a hidden file, so the same write can be red or a note; there is no state where neither a log directory nor the plugin's data folder is set; more code and more limits to state.
- **C. After a write the grade is always a note.** The scan alone holds the ceiling, and the hook reds only the rules that read one line.
  - **Pros:** the simplest; no baseline and no added cost; no red between edits by construction.
  - **Cons:** an edit that pushes a good page over the ceiling is no longer red at write time; the module's invariant would hold for the grade at scan time alone.
- **D. No code change.** A page under descent gets a temporary entry in the dial `departures`, removed when the page is under the ceiling.
  - **Pros:** no gate change; it works today.
  - **Cons:** the dials file changes twice for each page; the hook is silent on that page's grade meanwhile, so a rise is not seen either; the defect stays.

## Recommendation

Option A, recommended by the session. It is the only option that removes the red between edits and still reds an edit that makes a committed page worse, with no hidden state. Its baseline fits the kit's rule to commit before the first edit and after each coherent change: the last commit is the page as the change found it.

## Choice

Option A, chosen by the decider in chat on 2026-11-11.

## Ruling

<a id="r1"></a>**R1.** After a write, the hook of module [`const-language`](../requirements.md#const-language) reports a covered document's grade above the ceiling as a note, not as the grade finding, when that grade is below the grade of the same document as the last commit holds it. The run is green where nothing else is found. The rule applies where the grade can be a finding: the grade rule at level error, and no departure that allows it for the document. It holds under either value of the dial `severity`, and for a hook that a consumer wires before the write.

<a id="r2"></a>**R2.** The grade finding stays, after a write, in every other case above the ceiling: a grade equal to the last commit's or higher; a document that the last commit holds at or under the ceiling; and a document that the last commit does not hold, a new document and any document in a repository with no commit among them.

<a id="r3"></a>**R3.** The scan is unchanged. It reads no commit, never gives the note, and is red on every document whose grade is a finding.

<a id="r4"></a>**R4.** The note names the document, its grade, the ceiling and the grade of the last commit. It says that it is reported and not red while the grade falls, what to do next, and that the scan stays red until the document is at or under the ceiling. It carries the key N4 among the module's messages.

<a id="r5"></a>**R5.** The baseline is the last commit, never the edit before. So an edit that raises the grade, but leaves it below the last commit's, is a note too. The module states this as a limit of its own, with the scan as the backstop.

<a id="r6"></a>**R6.** The hook reads the committed copy by one git call, `git cat-file`, as the commit stores it and with no filter of the working tree. The call runs under the cap the shared code gives every git call of a hook, and only where R1 can apply. The copy goes through the same Vale run as the written document, prepared the same way, for its grade alone. The hook's budget counts the call.

<a id="r7"></a>**R7.** The rule has its fixture of [law 7 of CLAUDE.md](../../CLAUDE.md#law-7): one item that is red on a write that does not lower a committed document's grade and green, with the note typed whole, on the write that lowers it.

<a id="r8"></a>**R8.** The skill and the install note of the module tell the writer that a long document may come down one edit at a time, and that the scan must be green before the change is merged.

<a id="r9"></a>**R9.** This record narrows one ruling of the module's founding record: R3 of [dec-0046-language-module-rulings](dec-0046-language-module-rulings.md#r3), by which a rule at level `error` is a finding. For the grade rule, after a write, R1 makes one case at that level a note. R3 stands for every other case, and no other ruling of that record changes: the note is no finding, so what that record rules for findings holds as written.

## Applied

The commit that creates this record changes the hook, its messages and its fixtures, the module's document, its skill, its install note and its README. Every item is applied there, so the record is born `inactive`. The module is a draft and keeps its version ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## Carry list

1. R1 — [section 5 of the module's document](../../modules/const-language/MODULE.md#t5), the invariant, its sentences on the one case reported after a write; [section 6](../../modules/const-language/MODULE.md#t6), the hook row and message N4; [section 9](../../modules/const-language/MODULE.md#t9), the exit codes.
2. R2, R5 — [section 9 of the module's document](../../modules/const-language/MODULE.md#t9), limit 12.
3. R3 — [section 9 of the module's document](../../modules/const-language/MODULE.md#t9), row E2 and the backstop of limit 12; [section 5](../../modules/const-language/MODULE.md#t5), the invariant's sentence on the scan.
4. R4 — [section 6 of the module's document](../../modules/const-language/MODULE.md#t6), message N4 of the error messages.
5. R6 — [section 6 of the module's document](../../modules/const-language/MODULE.md#t6), item 2 of the cost and budget, and the package row of the table; [section 9](../../modules/const-language/MODULE.md#t9), limit 12, for how the copy is read.
6. R7 — [section 10 of the module's document](../../modules/const-language/MODULE.md#t10), item T33.
7. R8 — [the skill plain-language](../../modules/const-language/plugin/skills/plain-language/SKILL.md), step 3, and [the module's install note](../../modules/const-language/plugin/INSTALL.md), step 1.
8. R9 — history only: the narrowing of one ruling of the founding record, an act of this record.
