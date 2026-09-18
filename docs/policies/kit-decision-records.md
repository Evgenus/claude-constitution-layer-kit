---
id: kit-decision-records
type: current-state
title: Decision-record policy — the kit's recorded rulings
status: active
---

# Decision-record policy

Governs the document kind *decision record* as [kernel §5](../../kernel/CONVENTIONS.md#k5) defines it, for the kit's own rulings. Territory under this policy's id in `constitution.yaml`.

## Rules

1. **When.** A record is written for every `process`, `product`, or `architecture` ruling of the kit ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)); routine calls leave a commit note, never a record.
2. **Shape.** The kernel's record schema and body shape; a record applied in the commit that creates it is born `inactive`.
3. **Reversal.** A ruling is reversed by a new record, never by editing the old one ([kernel §5](../../kernel/CONVENTIONS.md#k5)).
4. **Yes.** Until the kit publishes (rollout Phase D) the yes is given in chat and named in the commit message that lands the record; from then on it is PR approval on a protected main ([kernel §4](../../kernel/CONVENTIONS.md#k4)).
5. **Enforcement.** Module `const-decision-records` once authored, numbering by `const-catalogs` once authored; review until then.
