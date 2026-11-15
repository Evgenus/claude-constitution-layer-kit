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

<a id="r1"></a>**R1.** A path git lists is a file when `os.stat` says so, through any link. As before, a path that is gone is no file. Nor is a path behind a file, or a link that leads nowhere or loops. Any other error of `os.stat` is the shared C12.10, on every interpreter. That includes a name too long for the system in a folder that exists. The text of C12.10 names that cause with the others. The shared functions are `repository.stat_or_none` and `repository.listed_file`, and the shared listing uses them. The dials file is asked the same way. A dials file linked into a folder nobody may search is the shared C12.7, never an absent file. A link that leads nowhere is still no dials file. The shared effect entry asks each plugin's entry the same way. One it cannot reach is the shared U6.4, a note after the headline, and is not run. The shared `repository.reached` makes any error but absent the shared C12.16, which names the path. The error's own number picks its fix, so a name too long never asks for permissions. Modules [`const-catalogs`](../requirements.md#const-catalogs) and [`const-change-cost`](../requirements.md#const-change-cost) ask by it the written file, the run's folder, the recorded data folder, and each transcript and folder of transcripts the count reads. The shared walk up to a repository passes over a folder nobody may search, as the later interpreters did. The gate then names the path itself.

<a id="r2"></a>**R2.** The mention listing of `const-referencing` uses the shared `listed_file`, and keeps no copy of its own. So the module requires the release 2.6.0 of the shared package. The listing asks whether a path is a link before anything else, and a link is never read, wherever it leads. A file it can reach and cannot read is still passed over, as before. The mover asks the paths it was given the same way, by `stat_or_none`: the old path, the new path and the folders above the new one. That holds for a move and for `--moved`. One it cannot reach is a refusal of its own, V5, that names the path and the system's reason. It is never read as absent, so `--moved` never goes on as if the old file were gone.

## 2. An interrupt

The shared guard caught no interrupt. After Ctrl-C an entry printed a traceback and no closing line, and the process ended by the signal. The mover of `const-referencing` then left five states unsaid. An interrupt in the plan moved the file back, but no line said so. If git then refused the move back, no line said where the file was. One during the writes printed no midway line. One while git moved the file, or moved it back, could leave the file moved or the made folders standing.

- **A. The shared guard alone.** It catches the interrupt and prints a line and the entry's closing line.
  - **Pros:** every entry of every module closes the same way; the closing line of the mover already knows the plan and the writes.
  - **Cons:** an interrupt that lands on a `git mv` leaves the move done or not, and no closing line can know which.
- **B. The mover's own entry alone.** The mover catches the interrupt and settles its own state.
  - **Pros:** the one act that changes files says exactly what was done.
  - **Cons:** every other entry still ends in a traceback.
- **C. Both.** The guard gives every entry its line, and the mover settles the moments only it knows.
  - **Pros:** every entry closes, and the mover's state is said at each moment.
  - **Cons:** two places to keep; the mover asks git's index, one more call at each interrupt.

The session recommended C, because each layer closes what only it can. It follows the decider's standing lean to ask the thing itself rather than model it: the mover asks git's index where the file is. The yes is the wave's merge.

<a id="r3"></a>**R3.** The shared guard catches an interrupt wherever the run is. It prints the new shared line C12.15, whose text stands true with no line below it. The guard makes no claim of its own about what was done by then. It prints an entry's own line after C12.15 only where the entry's closing callable carries `interrupted`, a line made from the entry's own state. The failure closing line is not reused. The guard then flushes, restores the default action of the interrupt and sends it to the process itself. So the process dies by the interrupt, as Python does for one nobody caught, and a shell shows 130 and stops a loop.

<a id="r4"></a>**R4.** The mover's closing carries such a line, and the mover counts as changed from before the first folder its move makes. An interrupt can come while the mover makes those folders, while git moves the file, or while git moves it back. One place settles a failure or an interrupt from the first folder to the plan's end, so no moment between them is left unsettled. The mover then settles it only where git's index and the disk agree. The disk is asked by the file's exact name. Both at the old path: the folders the move made are removed. Both at the new path: in a move the file is moved back. In a move back, the line says it is at the new path. Where they disagree, or a second interrupt lands while the mover asks, the line says the file may stand at either path and names both.

<a id="r5"></a>**R5.** A signal that ends the process at once, and an interrupt before the guard opens, print no line of the kit. So does a second interrupt in an entry that hands the guard no line of its own. The shared limit 19 and limit 12 of `const-referencing` say so.

<a id="r6"></a>**R6.** R3 and R4 reverse the clause "save after an interrupt" in R6 of [dec-0135-mover-refuses-an-unwritable-document](dec-0135-mover-refuses-an-unwritable-document.md#r6). After an interrupt, as after any failure, the mover's line says where the file is.

## Applied

The commits of this record's branch apply every ruling. The package takes the version 2.6.0, by the rule of versions of the shared code. The change adds four functions, three messages and a constant, and a helper of the testing subpackage. Module [`const-referencing`](../requirements.md#const-referencing) uses `stat_or_none` and `listed_file`. So its entry files now require 2.6.0 as the shared release. Its install note and the install guide name the tag v2.6.0 as the one to install. Modules [`const-catalogs`](../requirements.md#const-catalogs) and [`const-change-cost`](../requirements.md#const-change-cost) use `reached`, so every entry file of both requires 2.6.0 too, and their install notes name the same tag. No other module's required release changes, since no other module uses a name the new release adds. The record is born `inactive`.

## Carry list

1. R1 — [the shared limits](../../shared/GATE.md#g4), limit 7; [the shared messages](../../shared/MESSAGES.md#g3), rows C12.10, C12.16 and U6.4; [the listing in the code](../../shared/constitution_layer_kit/repository.py), `stat_or_none`, `reached`, `listed_file`, `list_markdown` and `repo_root`. Also [the dials in the code](../../shared/constitution_layer_kit/dials.py), `_read`; [the effect entry in the code](../../shared/constitution_layer_kit/effect.py), `main_all`. Also [the catalogs' write in the code](../../modules/const-catalogs/plugin/scripts/catalogs_gate/modes.py), `_examine_write`; [the count's paths in the code](../../modules/const-change-cost/plugin/scripts/change_cost_gate/git.py), `common_or_none`, with `recorded_plugin_data` of [logs](../../modules/const-change-cost/plugin/scripts/change_cost_gate/logs.py) and `transcripts_of` of [windows](../../modules/const-change-cost/plugin/scripts/change_cost_gate/windows.py).
2. R2 — [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mention listing in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/mentions.py), `other_files`; [the mover's checks in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `_found`.
3. R3 — [the shared limits](../../shared/GATE.md#g4), limit 19; [the shared messages](../../shared/MESSAGES.md#g3), row C12.15; [the guard in the code](../../shared/constitution_layer_kit/cli.py), `guarded` and `die_by_interrupt`.
4. R4 — [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the act in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `_move`, `_move_back`, `_settle`, `_where`, `_on_disk` and `_remove_made`; [the closing line](../../modules/const-referencing/plugin/scripts/referencing_gate/closing.py), `Closing`.
5. R5 — [the shared limits](../../shared/GATE.md#g4), limit 19; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12.
6. R6 — history only: the reversal of a clause of an accepted record, which stays as it was accepted.
