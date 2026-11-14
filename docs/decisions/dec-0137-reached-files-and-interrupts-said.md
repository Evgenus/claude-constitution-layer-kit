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

<a id="r1"></a>**R1.** A path git lists is a file when `os.stat` says so, through any link. As before, a path that is gone is no file. Nor is a path behind a file, or a link that leads nowhere or loops. Any other error of `os.stat` is the shared C12.10, on every interpreter. The shared function is `repository.listed_file`, and the shared listing uses it.

<a id="r2"></a>**R2.** The mention listing of `const-referencing` keeps its own copy of that rule. So the module needs no later release of the shared package than the one it requires. A file it can reach and cannot read is still passed over, as before.

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

<a id="r3"></a>**R3.** The shared guard catches an interrupt wherever the run is. It prints the new shared line C12.15, then the entry's closing line, and exits 130, with no traceback.

<a id="r4"></a>**R4.** An interrupt while git moves the file, or moves it back, is asked of git's index. Moved, the file is moved back. Not moved, the folders the move made are removed. Moved back, those folders are removed too. Where the index and the disk disagree, or the move back was not made, a line says so and names the file. The midway line follows it.

<a id="r5"></a>**R5.** A second interrupt, a signal that ends the process at once, and an interrupt before the guard opens print no line of the kit. The shared limit 19 and limit 12 of `const-referencing` say so.

## Applied

The commits of this record's branch apply every ruling. The package takes the version 2.6.0, by the rule of versions of the shared code. The change adds a function, a message and a constant. No module's required release changes, since no module uses a name the new release adds. The record is born `inactive`.

## Carry list

1. R1 — [the shared limits](../../shared/GATE.md#g4), limit 7; [the shared messages](../../shared/MESSAGES.md#g3), row C12.10; [the listing in the code](../../shared/constitution_layer_kit/repository.py), `listed_file` and `list_markdown`.
2. R2 — [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the mention listing in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/mentions.py), `_listed_file`.
3. R3 — [the shared limits](../../shared/GATE.md#g4), limit 19; [the shared messages](../../shared/MESSAGES.md#g3), row C12.15; [the guard in the code](../../shared/constitution_layer_kit/cli.py), `guarded`.
4. R4 — [the mover's refusals](../../modules/const-referencing/MODULE.md#t6), row V5; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12; [the act in the code](../../modules/const-referencing/plugin/scripts/referencing_gate/moving.py), `_move`, `_move_back`, `_remove_made` and `_indexed`.
5. R5 — [the shared limits](../../shared/GATE.md#g4), limit 19; [the mover's limits](../../modules/const-referencing/MODULE.md#t9), limit 12.
