---
id: dec-0028-carrying-a-ruling-is-routine
type: task-record
title: Carrying an already-ruled item into a policy or CLAUDE.md, its ruling unchanged, is routine
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Carrying an already-ruled item into a policy or CLAUDE.md is routine

## Context

The carry audit behind [dec-0027-record-citations-optional](dec-0027-record-citations-optional.md) found ruling items that lived only in their records. Writing them into the current-state documents raised a question of price: a policy's rule text and `CLAUDE.md` are harness text, and a harness ruling is `process` stakes — a record and a yes — under [kernel §4](../constitution/CONVENTIONS.md#k4). Read strictly, every such repair would need a new record for a ruling that already has one.

The session made the repairs as routine on a stated assumption, named in chat before and after the work, and the decider confirmed it in chat on 2026-09-20. Only accepting or rejecting the assumption was on the table, so this record states the ruling and the reasoning, with no manufactured options.

## Ruling

1. Carrying an already-ruled item into a policy or into `CLAUDE.md`, its ruling unchanged, is a repair and routine. The ruling's own record and yes cover it; the commit note names that record.
2. A matrix row is not covered: amending one stays `process` stakes under rule 2 of [plc-0007-requirements](../policies/plc-0007-requirements.md#r2).
3. Commits `cd04c14`, `053a0f6` and `138d142` were made on this reading and stand under it.

## Reasoning

A ruling that is recorded and approved but missing from the text is doc rot in the sense of the defect rule of [kernel §2](../constitution/CONVENTIONS.md#k2): something to be resolved, never a new choice. Nothing is decided when it is written down — the options were weighed and the yes was given when the ruling was made. Pricing the repair as `process` would put a second record and a second yes on one decision, and would make the repair dear enough to be postponed, which is how the items went missing in the first place. The limit is the unchanged ruling: the moment a repair adds a condition, picks between two readings, or drops a clause, it is a ruling and is priced as one. Matrix rows stay outside because their policy prices every amendment explicitly, and the decider confirmed the assumption as worded, for policies and `CLAUDE.md`.

## Carry list

1. Items 1 and 2 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md), rule 1.
2. Item 3 — history only: a one-time act.
