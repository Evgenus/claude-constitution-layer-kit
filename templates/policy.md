---
id: <plc-nnnn-slug — the next number of the plc catalog, the slug naming the kind governed and never the kit>
type: current-state
title: <Kind> policy — <one clause saying what the kind is>
status: active
---

# <Kind> policy

Governs the document kind *<kind>*: <one sentence saying what a document of this kind is and what it is for, with the decision record that introduced the kind linked where one exists>. Territory under this policy's id in `constitution.yaml`.

## Rules

<Numbered rules, each opening with a bold name and stating one rule in prose: what the envelope of this kind fixes beyond the four fields, the shape a document must have, when one is created and changed and at what stakes, what counts as a defect. Link the kernel sections relied on — from this folder the conventions page is at ../../kernel/CONVENTIONS.md, its sections anchored k1 to k7 — and never restate them; never list the documents governed, since the territory is the enumeration. Delete this paragraph.>

1. **<Name>.** <The rule.>
2. **Enforcement.** <Which module guards which field of this kind at write time and in its scan — the envelope by module const-meta-types, a number by module const-catalogs, a record's fields by module const-decision-records — and what stays judgment, held by review. Say it plainly: nothing judgment-based is dressed as a check.>
3. **Number.** <For a numbered kind: id and filename stem are one name, <prefix>-<nnnn>-<slug>; prefix, width and territory are an entry of const-catalogs.catalogs in constitution.yaml, its territory this policy's own by a YAML alias; a new document takes one more than the highest number the catalog has held, deleted ones included, provisional until it lands on main. For a kind that is not numbered, delete this rule.>
