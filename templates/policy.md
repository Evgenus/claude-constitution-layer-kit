---
id: <plc-nnnn-slug — the next number of the plc catalog, the slug naming the kind governed and never the kit>
type: current-state
title: <Kind, in full or by its short name> policy — <one clause saying what the kind is>
status: active
---

# <Kind, as in the title> policy

Governs the document kind *<kind>*: <one sentence saying what a document of this kind is and what it is for. Link the decision record that introduced the kind where one exists>. Territory under this policy's id in `constitution.yaml`.

## Rules

<Numbered rules, each opening with a bold name and stating one rule in prose. They say what the envelope of this kind fixes beyond the four fields and the shape a document must have. They say when one is created and changed and at what stakes, and what counts as a defect. Link the kernel sections relied on. From this folder the conventions page is at ../constitution/CONVENTIONS.md, its sections anchored k1 to k7. Never restate them. Never list the documents governed, since the territory is the enumeration. Delete this paragraph.>

1. <a id="r1"></a>**<Name>.** <The rule. Every rule carries its anchor `r<n>` inside the item, before the bold name. It keeps its number for life (rule 7 of plc-0001-root-policy — from this folder, `plc-0001-root-policy.md#r7`).>
2. <a id="r2"></a>**Change.** <When a document of this kind is created and changed, and at what stakes. Say what is routine, what is a `process` decision, what is a mechanical edit.>
3. <a id="r3"></a>**Enforcement.** <Which module guards which field of this kind, at write time, in its scan, or both. Name the split where the two differ. Module const-meta-types guards the envelope. Module const-catalogs guards a name, an id and a new item's number, free in the working tree, at write time and in its scan. It guards every collision between items that exist in the tree it scans in its scan alone. Module const-decision-records guards a record's fields. Module const-styling guards the twelve traces of the style defaults in its scan alone. Module const-language guards the grade, the sentence length and the constructions of the prose, after a write and in its scan. Module const-doc-budgets guards the length in characters, after a write and in its scan. Review holds what stays judgment. Say it plainly: nothing judgment-based is dressed as a check.>
4. <a id="r4"></a>**Style.** <Documents of this kind follow the style guides the dial `guides` of module `const-styling` names in `constitution.yaml`. They depart from a default only where that module's dial `departures` names a departure for their territory. It comes with its reason (rule 9 of plc-0001-root-policy — from this folder, `plc-0001-root-policy.md#r9`). The traces of the defaults are held as the enforcement rule says, and the rest is review. Every policy carries this rule. The enforcement rule names the scan of module `const-styling` and the gates of modules `const-language` and `const-doc-budgets` among the guards. Each module named is a link to its specification — from this folder, `../requirements.md#const-<name>`.>
5. <a id="r5"></a>**Number.** <For a numbered kind: id and filename stem are one name, <prefix>-<nnnn>-<slug>. Prefix, width and territory are an entry of const-catalogs.catalogs in constitution.yaml, its territory this policy's own by a YAML alias. A new document takes one more than the highest number the catalog has held, deleted ones included, provisional until it lands on main. For a kind that is not numbered, delete this rule.>
