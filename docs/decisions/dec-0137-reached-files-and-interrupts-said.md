---
id: dec-0137-reached-files-and-interrupts-said
type: task-record
title: A file the gate cannot reach and an interrupt are said, the same on every interpreter
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A file the gate cannot reach and an interrupt are said, the same on every interpreter

The carry audit of items 9.42 and 9.43 of the rollout plan left two gaps of the shared gate code as stated limits. The decider picked on 2026-11-14, in the orchestrating session's chat, to close both before the release. They are item 9.44.

## 1. A file git lists that the gate cannot reach

The shared listing kept a path git lists only where `Path.is_file` held. Under a folder nobody may search, that call raises on the older interpreters the kit supports and returns False on later ones. So on the older ones a scan printed C12.11, the defect line of the shared code. On the later ones it passed the file over without a word. It could end green on a document it never read. The mention listing of [`const-referencing`](../requirements.md#const-referencing) had the same shape. No real choice existed: the verdict must not hang on the interpreter, and a silent skip is never a verdict.

<a id="r1"></a>**R1.** A path git lists is a file when `os.stat` says so, through any link. As before, what `Path.is_file` reads as absent on every interpreter is absent. That is a path that is gone, a path behind a file, a link that leads nowhere or loops, and a bad file descriptor. Any other error of `os.stat` is the shared C12.10, on every interpreter. That includes a name too long for the system, where the system does not first answer that a folder is missing. The shared functions are `repository.stat_or_none` and `repository.listed_file`, and the shared listing uses them. The dials file is asked the same way. A dials file linked into a folder nobody may search is the shared C12.7, never an absent file. A link that leads nowhere is still no dials file. The shared effect entry asks each plugin's entry the same way. One it cannot reach is the shared U6.4, a note after the headline, and is not run. The shared `repository.reached` makes any error but absent the shared C12.16, which names the path. Modules [`const-catalogs`](../requirements.md#const-catalogs) and [`const-change-cost`](../requirements.md#const-change-cost) ask the same way for the written file, the run's folder, the recorded data folder, and each transcript the count reads. A folder of transcripts the count cannot list is C12.16 too. Every line of this record that carries the system's reason in brackets has one fix, to repair what the brackets name. Those are C12.7, C12.10, C12.16 and the mover's refusal of R2. So the fix is true for every reason the system can give. A reader that keeps no reason prints C12.10 without brackets, and its fix asks for the reason by a command. The shared walk up to a repository, `repository.stand_in` in `repo_root`, goes up only past a path that is absent or no folder. A folder it cannot search, the path asked about or one above it, is the shared C12.16. It names that path, in a scan and in a hook alike. So the walk never stands in a repository above it, whose verdict is not this tree's. Before, the walk stopped at such a folder on every interpreter, and git could not run there: C12.11. The scan's own start is asked by `reached` too.

<a id="r2"></a>**R2.** The mention listing of `const-referencing` uses the shared `listed_file`, and keeps no copy of its own. So the module requires the release 2.6.0 of the shared package. The listing asks whether a path is a link before anything else, and a link is never read, wherever it leads. A file it can reach and cannot read is still passed over, as before. The mover asks the paths it was given the same way, by `stat_or_none`. Those are the old path and the new path, and in a move the folders above the new one. That holds for a move and for `--moved`. One it cannot reach is a refusal of its own, V5, that names the path and the system's reason. It is never read as absent, so `--moved` never goes on as if the old file were gone.

## 2. An interrupt

The shared guard caught no interrupt. After Ctrl-C an entry printed a traceback and no closing line, and the process ended by the signal. The mover of `const-referencing` then left five states unsaid. An interrupt in the plan moved the file back, but no line said so. If git then refused the move back, no line said where the file was. One during the writes printed no midway line. One while git moved the file, or moved it back, could leave the file moved or the made folders standing.

- **A. The shared guard alone.** It catches the interrupt and prints a line and the entry's closing line.
  - **Pros:** every entry of every module closes the same way; the closing line of the mover already knows the plan and the writes.
  - **Cons:** an interrupt that lands on a `git mv` leaves the move done or not, and no closing line can know which.
- **B. The mover's own entry alone.** The mover catches the interrupt and settles its own state.
  - **Pros:** the one act that changes files says exactly what was done.
  - **Cons:** every other entry still ends in a traceback.
- **C. Both.** The guard gives every entry its line, and the mover says the moments only it knows.
  - **Pros:** every entry closes, and the mover's state is said at each moment.
  - **Cons:** two places to keep; the mover asks git's index and the disk, more calls at each interrupt.

The session recommended C, because each layer closes what only it can. It follows the decider's standing lean to ask the thing itself rather than model it. The mover asks git's index and the disk where the file is. The yes is the wave's merge.

<a id="r3"></a>**R3.** The shared guard catches an interrupt raised while the entry's body runs. It prints the new shared line C12.15, whose text stands true with no line below it. The guard makes no claim of its own about what was done by then. It prints an entry's own line after C12.15 only where the entry's closing callable carries `interrupted`, a line made from the entry's own state. The failure closing line is not reused. The guard then flushes, restores the default action of the interrupt and sends it to the process itself. So the process dies by the interrupt, as Python does for one nobody caught, and a shell shows 130. Where the shell got the interrupt too, as a terminal's Ctrl-C sends it to the whole group, its loop over the entry stops. Where the signal does not end the process, the exit is 130.

<a id="r4"></a>**R4.** The mover's closing carries such a line. An interrupt in the plan still moves the file back. Anywhere else the mover settles nothing, since an interrupt can land between any two statements. Its line is made from what it observes when the guard asks for it. It asks where git's index and the disk hold the file, by its exact name, and which folders of the move stand. The paths of the move, and the folders it would make, are named to the line before the move begins. No look at the tree can tell whether a document was rewritten. So a flag says it, set before the first write opens. A document opened for its rewrite and not yet written is named. It may be cut short or empty, and git holds its text. The index and the disk can disagree, or a second interrupt can land while the mover looks. Then the line says the file may stand at either path, and names both.

<a id="r5"></a>**R5.** An interrupt the guard does not catch ends in the interpreter's own traceback, and the process dies by it. Such an interrupt comes before the guard opens, while the entry file imports the shared package. Or it comes while the guard writes its lines or the log. A second interrupt is one of them, and the lines printed before it stand above the traceback. A signal of another kind that ends the process prints no line of the kit. The shared limit 19 and limit 12 of `const-referencing` say so.

<a id="r6"></a>**R6.** R3 and R4 reverse the clause "save after an interrupt" in R6 of [dec-0135-mover-refuses-an-unwritable-document](dec-0135-mover-refuses-an-unwritable-document.md#r6). After an interrupt the mover's line says where the file stands, as the tree shows it when the line is made. A traceback or no line can still follow a second interrupt or a signal of another kind, as R5 says.

## 3. The end by an interrupt in the entries' texts

The end by an interrupt is the shared guard's, the same for every entry of every module. The item "the docstring as contract" of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md) has an entry's docstring state its exit codes. Some forty entry files and twelve module documents state them.

- **A. One statement.** Rule 4 of the gate-script rules states the end by an interrupt, and rule 10 says the entries need not repeat it.
  - **Pros:** one text to keep true, as [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) asks: duplication is a defect.
  - **Cons:** an entry's docstring no longer names every way its process can end.
- **B. A line in every entry.** Each Exit docstring and each module's line of exit codes names the end by an interrupt.
  - **Pros:** each docstring stays a full contract.
  - **Cons:** some fifty copies of one shared fact, each to keep true at every change of the guard.

The orchestrating session picked A on 2026-11-15, by [law 1 of CLAUDE.md](../../CLAUDE.md#law-1). The yes is the wave's merge.

<a id="r7"></a>**R7.** The end by an interrupt is the shared guard's, the same for every entry. It is stated once, in rule 4 of the gate-script rules. An entry's Exit docstring and its module's line of exit codes state the entry's own exit codes, and need not repeat that end. This narrows, for that one end, the item of [dec-0020-gate-script-rules](dec-0020-gate-script-rules.md) that has the docstring state the exit codes. That item's other demands stand, and so does the rest of that record.

## Applied

The commits of this record's branch apply every ruling. The package takes the version 2.6.0, by the rule of versions of the shared code. The change adds six functions, three messages and a constant to the package, and four names to its testing subpackage. The functions are `stat_or_none`, `reached`, `listed_file` and `stand_in` of `repository`, `die_by_interrupt` of `cli` and `reason_fix` of `messages`. The testing names are `interrupt_at` and `INTERRUPT_AT` of the harness, and `interrupted_loop` and `index_only` of the items. The message `c12_unreadable` gains an optional reason. Module [`const-referencing`](../requirements.md#const-referencing) uses `stat_or_none` and `listed_file`. So its entry files now require 2.6.0 as the shared release. Its install note and the install guide name the tag `constitution-layer-kit-v2.6.0` as the one to install. Modules [`const-catalogs`](../requirements.md#const-catalogs) and [`const-change-cost`](../requirements.md#const-change-cost) use `reached` or `stand_in`, so every entry file of both requires 2.6.0 too, and their install notes name the same tag. No other module's required release changes, since no other module's plugin code uses a name the new release adds. Two modules' fixtures use `interrupt_at`, through their link to the shared code. Rules 4 and 10 of the gate-script rules apply R7, and rule 3 names the guard's end beside the entry's exits. The record is born `inactive`.

## Carry list

1. R1 — [the shared limits](../../shared/GATE.md#g4), limit 7; [the shared messages](../../shared/MESSAGES.md#g3), rows C12.7, C12.10, C12.16 and U6.4; [the listing in the code](../../shared/constitution_layer_kit/repository.py), `stat_or_none`, `reached`, `listed_file`, `list_markdown`, `stand_in` and `repo_root`. Also [the scan's start in the code](../../shared/constitution_layer_kit/pipeline.py), `locate_scan`; [the fix in the code](../../shared/constitution_layer_kit/messages.py), `reason_fix`. Also [the dials in the code](../../shared/constitution_layer_kit/dials.py), `_read`; [the effect entry in the code](../../shared/constitution_layer_kit/effect.py), `main_all`. Also [the catalogs' write in the code](../../modules/const-catalogs/plugin/scripts/catalogs_gate/modes.py), `_examine_write`; [the count's paths in the code](../../modules/const-change-cost/plugin/scripts/change_cost_gate/git.py), `common_or_none`, with `recorded_plugin_data` of [logs](../../modules/const-change-cost/plugin/scripts/change_cost_gate/logs.py) and `transcripts_of` of [windows](../../modules/const-change-cost/plugin/scripts/change_cost_gate/windows.py).
2. R2 — [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mention listing in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/mentions.py), `other_files`; [the mover's checks in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `_found`.
3. R3 — [the shared limits](../../shared/GATE.md#g4), limit 19; [the shared messages](../../shared/MESSAGES.md#g3), row C12.15; [the guard in the code](../../shared/constitution_layer_kit/cli.py), `guarded` and `die_by_interrupt`. Also [the gate-script rules](../../module-template/gate-script-rules.md#r3), rules 3 and 4.
4. R4 — [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the act in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `act`, `_move`, `_move_back` and `_remove_made`; [the closing line](../../modules/const-referencing/plugin/scripts/referencing_gate/closing.py), `Closing`, `where`, `_indexed` and `_on_disk`.
5. R5 — [the shared limits](../../shared/GATE.md#g4), limit 19; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12.
6. R6 — history only: the reversal of a clause of an accepted record, which stays as it was accepted.
7. R7 — [the gate-script rules](../../module-template/gate-script-rules.md#r4), rule 4; [the same page](../../module-template/gate-script-rules.md#r10), rule 10.
