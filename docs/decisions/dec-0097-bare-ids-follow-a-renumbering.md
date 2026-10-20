---
id: dec-0097-bare-ids-follow-a-renumbering
type: task-record
title: A bare id in an accepted record or a frozen comparison follows a renumbering or a rename the kernel allows
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A bare id in an accepted record or a frozen comparison follows a renumbering or a rename the kernel allows

## Context

The carry audit of [dec-0096-shared-package-named-constitution-layer-kit](https://github.com/Evgenus/claude-constitution-layer-kit/pull/79), still open on 2026-10-21, had a confirming reader note an older tension. A session checked it on 2026-10-21 and found it real.

- **The kernel.** The second and third exceptions to the id rule of [kernel §1](../../kernel/CONVENTIONS.md#k1) say that "every reference to it in the tree is rewritten". The skill of module [`const-catalogs`](../requirements.md#const-catalogs), in its section on two items under one number, rewrites the bare form too, in the whole tree, and leaves only commit messages as they are.
- **Comparisons.** [Rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) let a frozen comparison take "five kinds of edit and no other". After a renumbering it let only a link be "rewritten to the item's new id". A bare id outside a link had no allowed edit, so the policy forbade what the kernel asks.
- **Records.** [Rule 14 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14) said a migration that follows a document renumbered "is the kernel's, at any time", but its next sentence named only a link. [Kernel §5](../../kernel/CONVENTIONS.md#k5) calls a reference-form migration a rewrite of *how* a record cites, and a wording edit alters no existing handle. So for a record the text was unclear rather than closed.
- **No case yet.** Git's history held three renumberings. Two were made on their own branch before they landed. Only one, dec-0076 to dec-0077 on 2026-10-09, renumbered an item already on the main branch, and no record or comparison held its id.
- **The exposure.** On 2026-10-21, outside links, fences and envelopes, the session counted 6 bare ids in the prose of two comparisons and 34 in code spans of comparisons, most of them examples of a form. It counted 159 in the prose of records, in about 34 files. A change to a catalog's form, the third exception, would rename every item and reach all of them at once.

## Options

- **A. Widen both policy rules to the kernel.** Rule 7 of plc-0005-research and rule 14 of plc-0004-decision-records each gain one sentence: after a renumbering or a rename the kernel allows, a bare id that means the item takes the new id, and an id used as an example stays as written.
  - **Pros:** the policies do what the kernel already says, which [law 1 of CLAUDE.md](../../CLAUDE.md#law-1) makes authoritative; it matches what the catalogs skill already teaches; two sentences, no kernel change.
  - **Cons:** a frozen document takes one more edit; each bare form must be read in place, since it may mean the item that kept the number.
- **B. A carve-out in the kernel.** [Kernel §1](../../kernel/CONVENTIONS.md#k1) would say that in a document a policy freezes, a bare id stays as written and only a link follows.
  - **Pros:** frozen prose stays exactly as frozen.
  - **Cons:** a kernel change, always recorded, with a full carry audit; the bare id would then name the wrong item, the one that kept the number; the catalogs skill would change too.
- **C. Every bare id becomes a link now.** One migration in all records and comparisons, so that the clause on links covers every later case.
  - **Pros:** every reference becomes one a machine can follow.
  - **Cons:** about 165 prose lines of frozen documents edited; it still needs a policy change, since rule 7 allowed no such change of form; new bare ids are not stopped.
- **D. Defer, with a signal.** The gap is logged and reopened when a renumbering or a change of a catalog's form first meets a bare id in a frozen document.
  - **Pros:** no work now; no case has happened.
  - **Cons:** a known contradiction between the kernel and two policies stays in the tree; the next collision on the main branch would meet it in the middle of a change.

## Recommendation

A, recommended by the session: the kernel already rules this and the kit's own skill already does it, so widening the two policies is the smallest change that ends the contradiction. The kit's rule against machinery for failures no one has hit is about new machinery, not about two texts that contradict each other.

## Choice

A, by the decider in chat on 2026-10-21.

## Ruling

<a id="r1"></a>**R1.** In a frozen comparison, the edit after a renumbering or a rename that [kernel §1](../../kernel/CONVENTIONS.md#k1) allows also rewrites, to the item's new id, each bare id that means the item, whether it stands in prose or in a code span outside a link. An id that stands as an example of a form, or that means another item, such as the one that kept the number, stays as written.

<a id="r2"></a>**R2.** In an accepted record, rewriting such a bare id, of a renumbered or renamed item of any catalog, is a reference-form migration in the kernel's sense, as rewriting a link is, with the same exceptions as R1. The commit names it a migration and names the renumbering or the rename.

## Applied

The commit that creates this record adds one sentence to rule 7 of plc-0005-research and one to rule 14 of plc-0004-decision-records, so the record is born `inactive`. No bare id is rewritten: no item that one names has been renumbered.

## Carry list

1. R1 — [plc-0005-research](../policies/plc-0005-research.md#r7), rule 7, the sentence after the five kinds of edit.
2. R2 — [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r14), rule 14, the sentence after the link to a renumbered record.
