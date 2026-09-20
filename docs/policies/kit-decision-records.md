---
id: kit-decision-records
type: current-state
title: Decision-record policy — the kit's recorded rulings
status: active
---

# Decision-record policy

Governs the document kind *decision record* as [kernel §5](../../kernel/CONVENTIONS.md#k5) defines it, for the kit's own rulings. Territory under this policy's id in `constitution.yaml`.

## Rules

1. **When.** A record is written for every `process`, `product`, or `architecture` ruling of the kit ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)); routine calls leave a commit note, never a record. Carrying an already-ruled item into a policy or into `CLAUDE.md`, its ruling unchanged, is a repair and routine — the ruling's own record and yes cover it, and the commit note names that record. A matrix row is not covered by this: amending one stays under rule 2 of [kit-requirements](kit-requirements.md).
2. **Shape.** The kernel's record schema and body shape; a record applied in the commit that creates it is born `inactive`. A record's last section is its carry list: it pairs every ruling item with the current-state text that now states it. A deferred trigger and a fallback are items too, though they change no file on the day. An item that binds is always carried; "history only" is written for an item that binds nothing — a one-time act, a finding of the day. The carry check, before the yes: the author puts each item as a question, and a reader who holds the current-state documents and not the record answers it; an item that reader cannot answer is carried, or justified in the commit message that lands the record. The list and the check are advisory — whether a ruling is carried is judgment, held by review. Records numbered below `0027` were written before this rule and carry no list.
3. **Number.** Records are a numbered kind: id and filename stem are one name, `dec-<nnnn>-<slug>`; prefix, width and territory are an entry of `const-catalogs.catalogs` in `constitution.yaml`, its territory this policy's own by a YAML alias. A new record takes one more than the highest number the catalog has held, deleted records included, provisional until it lands on main ([requirement A13.1](../requirements.md#a13-1), [A13.3](../requirements.md#a13-3)).
4. **Reversal.** A ruling is reversed by a new record, never by editing the old one ([kernel §5](../../kernel/CONVENTIONS.md#k5)).
5. **Yes.** Until the kit publishes (rollout Phase D) the yes is given in chat and named in the commit message that lands the record; from then on it is PR approval on a protected main ([kernel §4](../../kernel/CONVENTIONS.md#k4)).
6. **Enforcement.** Module `const-decision-records` guards `type`, `stakes` and `decider` of every document in this territory — this policy's id is named in its dial `record_policies` in `constitution.yaml` — at write time when a session loads the plugin, and by its scan; the rest of the envelope is module `const-meta-types`'. Module `const-catalogs` guards the name, the id and the number's uniqueness the same two ways.
7. **Deletion.** No record has to be deleted. An `inactive` record whose ruling is carried binds nothing, and no rule depends on it ([kernel §5](../../kernel/CONVENTIONS.md#k5)); it is kept as evidence of the options and reasoning. Whether anything should still reference it ([kernel §1](../../kernel/CONVENTIONS.md#k1)) is the decider's judgment, not a count of links. Deleting one is routine and is one commit: every link to it is removed, the record is removed, and the commit message names the record and calls the change a deletion. Inside another record the link becomes the deleted record's title in plain words — never its id, so nothing in the tree points at what is gone — which is a reference-form migration in the kernel's sense, the ruling untouched, and the commit names it one. An `active` record is never deleted.
