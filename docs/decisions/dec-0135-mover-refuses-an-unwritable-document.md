---
id: dec-0135-mover-refuses-an-unwritable-document
type: task-record
title: The mover refuses a document it cannot read or rewrite, and a refused move is moved back
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The mover refuses a document it cannot read or rewrite, and a refused move is moved back

## 1. A document the mover cannot read or rewrite

The mover of [`const-referencing`](../requirements.md#const-referencing) moves a document and rewrites the links to it. Before this change, a covered document that could not be written stopped the act after the move. The user saw the defect line of the shared code, C12.11, with a traceback, and then the line that the act stopped midway. The file had moved, and some links were rewritten. A covered document that could not be read was passed over at the rewrite. The closing scan then failed on it, also after the move. The test session of wave 4 found the first case and put the right behaviour to the decider.

- **A. A refusal before the move.** The mover asks whether each document it would rewrite can be written, and refuses with a teaching line and nothing changed.
  - **Pros:** it fits the mover's other refusals, which all change nothing; no traceback reaches the user.
  - **Cons:** plugin code and a message change, so the eval receipt goes stale; a file can still change between the check and the write.
- **B. Keep the defect line.** The C12.11 line, then the line that the act stopped midway.
  - **Pros:** no change; the closing line already says what to do.
  - **Cons:** a common state of the user's own tree is reported as a defect of the plugin, with a traceback.
- **C. A designed line after the fact.** The write's failure is caught, the file named, and the act closes with the midway line.
  - **Pros:** a smaller change than A; no traceback.
  - **Cons:** the move has still happened, and the user repairs the tree by hand.

The session recommended A, as a later rollout item and not inside wave 4, because it keeps the mover's rule that a refusal changes nothing. The decider picked A in chat on 2026-11-13. On the same day the decider placed it in wave 5, as item 9.42 of the rollout plan, before the release.

<a id="r1"></a>**R1.** A document the act must read and cannot is a V5 refusal that names it and the system's reason. These are the covered documents, and the moved one when its new path is Markdown. A file that is not UTF-8 is no refusal: the act leaves it alone and says so.

<a id="r2"></a>**R2.** Each document whose rewrite would change a link is opened for writing and closed again, with nothing written. A document the system will not open so is a V5 refusal that names it and the system's reason. A read-only document the act would not rewrite is no refusal.

<a id="r3"></a>**R3.** The check runs in all three acts: the move, `--moved` and `--ids`. A refusal changes nothing, save the edges R8 names. No document is written before the check has passed: only the move comes first, and a refusal undoes it, as R5 says.

## 2. How the check knows the tree after a move

The first design asked before the move. It predicted the tree as git would list it after the move. That was the listing, the territories and the policies, with the moved file at its new path. Three rounds of the wave's carry audit, the last of them round 4, found that the prediction differed from what git lists. Round 4 found four needless refusals against main. They came from a file moved to `.GITIGNORE` in another case on a disk that ignores case, and from the `core.excludesFile` file in another case. They also came from git's default ignore file inside the repository, and from a symlink that names the moved file in another case.

- **A. Fold case, and add git's default ignore file.** The prediction learns the four cases.
  - **Pros:** the smallest change; the check stays before the move.
  - **Cons:** git's rules are wider than any copy of them, and each round of the audit found new ones.
- **B. State the four in limit 12.** The prediction stays, and the limit names its holes.
  - **Pros:** no code change.
  - **Cons:** four needless refusals stay, against the measure of the wave's carry audit that no case main passes may be refused without need.
- **C. Drop the prediction.** The mover makes the move with git, plans on the tree as git lists it, and moves the file back when the plan refuses.
  - **Pros:** the check reads exactly what the act reads, with the act's own code; no rule of git is copied.
  - **Cons:** a refusal moves the file twice; a move back can itself fail.

The orchestrating session put the three options to the decider in its chat. It recommended C, because A and B both keep a copy of git's rules that the audit's rounds kept catching out. The decider picked C on 2026-11-14 in that chat. The first design was left because its copy of git's rules kept falling short of git. So C keeps the rule of section 1's A that a refusal changes nothing, and gives up its refusal before the move.

<a id="r4"></a>**R4.** Everything that can refuse without moving is asked first. A move is then made with git. On the tree as git lists it after the move, the act lists and reads every document it reads. It works out every rewrite and every mention in memory, and makes the check of R1 and R2. Only then does it write.

<a id="r5"></a>**R5.** A failure of that plan moves the file back with git and removes the folders the move made. An interrupt does the same. A refusal then closes with the line that the file was moved back and nothing was changed. A refusal names the moved document by the path it was moved back to.

<a id="r6"></a>**R6.** A move back that fails says so and names where the file is, before the line that the act stopped midway, save after an interrupt. A folder the move made that cannot be removed is said the same way.

<a id="r7"></a>**R7.** `--moved` and `--ids` move nothing: they plan on the tree as it stands, and a refusal closes with the line that nothing was changed.

<a id="r8"></a>**R8.** What the check and the move back cannot hold stands in limit 12 of the module's section 9. Each edge is stated as wide as it is.

## Applied

The commits of this record's branch apply every ruling. The rulings of section 1 were applied first under the first design. Before the yes, the record was corrected in place to the design of section 2, and the code and the module's document with it. The record is `inactive`.

## Carry list

1. R1, R2, R3 — [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), rows V1–V4 and V5; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the check in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `act` and `_plan`.
2. R4, R5, R6, R7 — [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the act in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `act`, `_plan` and `_move_back`; [the closing line](../../modules/const-referencing/plugin/scripts/referencing_gate/closing.py), `Closing`.
3. R8 — [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12.
