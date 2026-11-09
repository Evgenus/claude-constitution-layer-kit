---
id: plc-0012-guide-pages
type: current-state
title: Guide-page policy — the pages of the session guide read at their moment
status: active
---

# Guide-page policy

Governs the document kind *guide page*: a page of the kit's session guide that holds the rules of one activity of the kit's own work, which an agent needs only when it does that activity, so that `CLAUDE.md`, which every session loads, links the page in place of holding its text; introduced by decision [dec-0115-long-documents-split-and-carry-entries-follow-moved-text](../decisions/dec-0115-long-documents-split-and-carry-entries-follow-moved-text.md). Territory under this policy's id in `constitution.yaml`.

## Rules

1. <a id="r1"></a>**Type.** `current-state`, superseded in place ([kernel §1](../constitution/CONVENTIONS.md#k1)).
2. <a id="r2"></a>**Content.** A page states the rules of its activity whole, in its own text, as `CLAUDE.md` states its own ([kernel §5](../constitution/CONVENTIONS.md#k5)); it restates no rule of the kernel, of a law of `CLAUDE.md` or of another page, and links it. `CLAUDE.md` links each page from one line that says when the page is read. A page is kit tooling: no module ships it, and no module's file names it ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)).
3. <a id="r3"></a>**Anchors.** Every section, step and bullet that another document cites carries an explicit anchor, kept for life ([rule 7 of plc-0001-root-policy](plc-0001-root-policy.md#r7)).
4. <a id="r4"></a>**Change.** A change to a rule a page states is a `process`-stakes decision, as a change to a rule of `CLAUDE.md` is ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)); a wording edit that changes no rule is routine, noted in the commit. A new page, or text moved into a page from `CLAUDE.md`, is a change to this kind and takes a record.
5. <a id="r5"></a>**Enforcement.** The envelope by module [`const-meta-types`](../requirements.md#const-meta-types); links and anchors by module [`const-referencing`](../requirements.md#const-referencing); the twelve traces of the style defaults by module [`const-styling`](../requirements.md#const-styling) in its scan alone; the grade, the sentence length and the constructions of the prose by module [`const-language`](../requirements.md#const-language), after a write and in its scan; the length in characters by module [`const-doc-budgets`](../requirements.md#const-doc-budgets), after a write and in its scan, against the ceiling `guide-pages`. Whether a page states its rules whole, and whether `CLAUDE.md`'s line says when to read it, is judgment, held by review.
6. <a id="r6"></a>**Style.** Documents of this kind follow the style guides the dial `guides` of module [`const-styling`](../requirements.md#const-styling) names in `constitution.yaml`, and depart from a default only where that module's dial `departures` names a departure for their territory, with its reason ([rule 9 of plc-0001-root-policy](plc-0001-root-policy.md#r9)); the traces of the defaults are held as the enforcement rule says, the rest is review.
