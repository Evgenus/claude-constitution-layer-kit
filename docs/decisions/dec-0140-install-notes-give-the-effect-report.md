---
id: dec-0140-install-notes-give-the-effect-report
type: task-record
title: The install note of every module gives the effect report a step after its output log
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The install note of every module gives the effect report a step after its output log

## Context

Every module has shipped `scripts/effect-report.sh` since 2026-11-07. The report counts how often each of the module's rules was followed, bypassed or missed. A review of the install notes on 2026-11-19 found that no note gave its command. One note named it only inside its `CLAUDE.md` step. The template's install note has no step for it, so a new module would leave it out too.

The review found a second gap that the report depends on. A note says that the output log lives in the platform's per-plugin data directory. That directory is set only for hooks. A scan or a report run by hand finds no log unless `log_dir` is set. So a report run by hand reads no session unless the person names the folder of the project's transcripts.

The review also found smaller defects in single notes, in the install guide and in the module READMEs. Those fixes are routine and are not ruled here.

## Options

- **A. One change: this record, a template step and every fix.** The template's install note gains the step, and every module's note and its install-note row follow, with each module bumped once.
  - **Pros:** each module is bumped once; the template, the rows and the notes agree in one change; the next module inherits the step.
  - **Cons:** the routine fixes wait for this record's audit and the yes; it is the largest diff to review.
- **B. The step in the notes only, no template change.**
  - **Pros:** no record, so it lands fastest; one bump per module.
  - **Cons:** the template, its guidance and the rows still lack the step; the next module misses it again; the notes depart from their rows.
- **C. Two changes: the routine fixes first, then this record with the step.**
  - **Pros:** the wrong statements are fixed at once; the record's review sees only the step.
  - **Cons:** every module is bumped twice; two rounds of CI and merge.

## Recommendation

The session recommended A. The step belongs in the template, or the gap comes back with the next module. One bump per module also keeps the update simple for projects.

## Choice

The decider picked A in chat on 2026-11-19, with the word "A".

## Ruling

<a id="r1"></a>**R1.** The template's install note has a step "Optional, the effect report", right after the output log. The step gives the command, `--transcripts` with the folder named in words and never by its path, and `--since`. Where a rule of the module needs a reader, it names the rule and `--reader`. It says that the report blocks nothing and is never red, and gives its exit codes. The fixtures and the `CLAUDE.md` line follow it. A module that ships no effect report deletes the step.

<a id="r2"></a>**R2.** The template's output-log step says that the platform's per-plugin data directory is set only for hooks. A scan run by hand or in CI writes no log unless `log_dir` is set. The effect-report step says what a run by hand then needs to find a session.

<a id="r3"></a>**R3.** Each module's install note gives the step after its own output log. A step that an accepted record cites keeps its number, as R24 of [dec-0105-template-gives-the-shapes-modules-fill](dec-0105-template-gives-the-shapes-modules-fill.md#r24) already rules. The install-note row of each module document names the step.

<a id="r4"></a>**R4.** These rulings replace words of R17 of [dec-0105-template-gives-the-shapes-modules-fill](dec-0105-template-gives-the-shapes-modules-fill.md#r17). Its list of the template's steps gains the effect report between the output log and the fixtures. That record stays as it was accepted.

## Applied

The commits of this record's branch apply every ruling. The template's install note has the step, and its guidance in `slot-guidance.md` asks for it. All twelve module notes have it, after their output log, and every row names it. Each module is at manifest version `0.1.1`. The record is born `inactive`.

## Carry list

1. R1 — [the template's install note](../../module-template/plugin/INSTALL.md), step 6; [the slot guidance](../../module-template/slot-guidance.md#s10), the install note row.
2. R2 — [the template's install note](../../module-template/plugin/INSTALL.md), steps 5 and 6.
3. R3 — [the slot guidance](../../module-template/slot-guidance.md#s10), the install note row; each module's `plugin/INSTALL.md` and the install-note row of section 6 of its `MODULE.md`.
4. R4 — history only: which words of an accepted ruling this record replaces. That record stays as it was accepted.
