---
id: <plc-nnnn-slug — the next number of the plc catalog, the slug naming the kind governed and never the kit>
type: current-state
title: <Kind, in full or by its short name> policy — <one clause saying what the kind is>
status: active
---

# <Kind, as in the title> policy

Governs the document kind *<kind>*: <one sentence saying what a document of this kind is and what it is for, with the decision record that introduced the kind linked where one exists>. Territory under this policy's id in `constitution.yaml`.

## Rules

<Numbered rules, each opening with a bold name and stating one rule in prose: what the envelope of this kind fixes beyond the four fields, the shape a document must have, when one is created and changed and at what stakes, what counts as a defect. Link the kernel sections relied on — from this folder the conventions page is at ../../kernel/CONVENTIONS.md, its sections anchored k1 to k7 — and never restate them; never list the documents governed, since the territory is the enumeration. Delete this paragraph.>

1. <a id="r1"></a>**<Name>.** <The rule. Every rule carries its anchor `r<n>` inside the item, before the bold name, and keeps its number for life (rule 7 of plc-0001-root-policy — from this folder, `plc-0001-root-policy.md#r7`).>
2. <a id="r2"></a>**Change.** <When a document of this kind is created and changed, and at what stakes: what is routine, what is a `process` decision, what is a mechanical edit.>
3. <a id="r3"></a>**Enforcement.** <Which module guards which field of this kind, at write time, in its scan, or both, the split named where the two differ: the envelope by module const-meta-types, a name, an id and a new item's number, free in the working tree, by module const-catalogs at write time and in its scan, and every collision between items that exist in the tree it scans, in its scan alone; a record's fields by module const-decision-records — and what stays judgment, held by review. Say it plainly: nothing judgment-based is dressed as a check.>
4. <a id="r4"></a>**Style.** <Documents of this kind follow the style guides the dial `guides` of module `const-styling` names in `constitution.yaml`, and depart from a default only where that module's dial `departures` names a departure for their territory, with its reason (rule 9 of plc-0001-root-policy — from this folder, `plc-0001-root-policy.md#r9`); the traces of the defaults are held as the enforcement rule says, the rest is review. Every policy carries this rule; the enforcement rule names the scan of module `const-styling` among the guards.>
5. <a id="r5"></a>**Number.** <For a numbered kind: id and filename stem are one name, <prefix>-<nnnn>-<slug>; prefix, width and territory are an entry of const-catalogs.catalogs in constitution.yaml, its territory this policy's own by a YAML alias; a new document takes one more than the highest number the catalog has held, deleted ones included, provisional until it lands on main. For a kind that is not numbered, delete this rule.>
