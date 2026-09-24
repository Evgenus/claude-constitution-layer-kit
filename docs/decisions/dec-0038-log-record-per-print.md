---
id: dec-0038-log-record-per-print
type: task-record
title: A gate's output log holds one record per print, never one per printed line
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A gate's output log holds one record per print, never one per printed line

## Context

Rule 12 of [template §6](../../module-template/MODULE.md#t6) said that every line a gate prints is appended to the output log as one JSON line, and the shared `output` split each printed text on its newlines to do so. The decider observed on 2026-09-24 that the log therefore behaved like `print`: one message was scattered over several records, though the log is JSON Lines and its lines are related. Three texts are printed with several lines at once: a block verdict, which joins the notes, every finding and the count into one stderr text; a finding printed by a scan, its headline and fix on separate lines; and the traceback that follows an unexpected failure, one record per frame line. JSON escapes a newline inside a string, so the split bought nothing a reader of JSON Lines needs.

## Options

- **A. One record per print call.** Each call of `out` or `err` is one record, its newlines kept inside `text`.
  - **Pros:** the unit the caller meant is the unit logged; a one-line change to `_emit`; the log still holds only what was printed, in the order printed, and the seven fields stay as they are.
  - **Cons:** a configuration failure is still three records — the BROKEN line, the count line and a traceback — because the guard prints three times; a plain `grep` no longer matches a whole record by a line of a verdict.
- **B. One record per run.** The whole run is one JSON line.
  - **Pros:** one event is always one record.
  - **Cons:** stdout and stderr mix in one record or the shape grows a second text field; the held-records design of [dec-0022-output-log-through-logging](dec-0022-output-log-through-logging.md) loses its point.
- **C. Keep one record per line,** and only say why in rule 12.
  - **Pros:** no change to code.
  - **Cons:** the observed defect stays.

## Recommendation

A, by the session: the unit a caller prints is the unit of meaning, and it keeps the mechanism and the fields of the log. Should the three records of a configuration failure trouble a reader, the remedy is a guard that prints once, not another unit.

## Choice

A, chosen by the decider in chat on 2026-09-24.

## Ruling

**R1.** One call that prints — `out` or `err` of the shared `output` — is one record of the output log, one JSON line; a text of several lines stays one record, its newlines escaped by JSON. The records of a run, their texts each followed by a newline, rebuild what the run printed on each stream exactly.

**R2.** The shared item S132 holds R1: its records rebuild both streams of a red run, and a gate's block verdict is one record of several lines.

**R3.** Pre-publication, every module still at `0.0.1`: no version bump (step 7 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md)).

## Carry list

1. R1 — rule 12 of [template §6](../../module-template/MODULE.md); the docstring and `_emit` of [the shared output](../../shared/const_gate/output.py); the `output` row of [kit-shared-gate-code](../../shared/GATE.md).
2. R2 — the S132–S136 row of [kit-shared-gate-code](../../shared/GATE.md) and the item itself in [the shared items](../../shared/tests/shared_items.py).
3. R3 — history only.
