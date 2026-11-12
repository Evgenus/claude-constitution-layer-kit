---
name: style-defaults
description: >
  Load this skill first, before writing any table, diagram, list, formula, heading below level
  three, callout or fenced block in a document — every time, whether or not the style seems known:
  it applies the project's style defaults to that choice and declares a departure from a default
  in the dials file with its reason instead of marking the document. Load it also when writing or
  editing a template, when the style scan reports a signature, and when a repository has no style
  guide yet. Advisory: it shapes the choice; the scan checks only the twelve traces it knows.
---

# Style defaults

A style decision made in one document is made again in the next, differently. This procedure
reads the project's one style guide before the moment of choice. It puts a departure where it
belongs, in the dials file with its reason. That way every document is uniform and every
exception is on record. It is judgment from start to finish, except the scan named in step 4.

## 1. Find the guide

The style guides are the documents the project names in `const-styling.guides` of
`constitution.yaml`, path patterns over the repository. Where the key is absent, look for a
document titled "Style guide" in the project's documentation folder. Read the guide whole once
per session. It is short, one numbered entry per default, each defined by its examples. The
guide is the one statement of the defaults. This page restates none of them. Step 4 names the
scan's traces, which are the mechanical halves of some, not the defaults.

Where the repository has no style guide, the shipped text, `style-guide.md` beside this file,
applies meanwhile. Create the project's own from it, unless the project has decided to keep none.
That is the case when its decision records say so, or the user answered no while the project
is or was being set up. Such a project
follows the shipped text and creates nothing. To create one,
fill its envelope, with the `id` a stable kebab-case name. Put it where the project's documents of
that kind live. Name its path in `const-styling.guides`. Write it with the session's file
tools, never by a copy in the shell, so that every hook sees the write. That file carries the founding
entries. A project that governs its documents by policies first gives the guide a policy of its
own, as its constitution asks for any new kind. Then it has its root policy ask every policy for a
style rule. It also has each kind's policy carry one, binding that kind's documents to the guide.

## 2. Before the choice

At each of these moments, open the guide's entry that rules on it and follow it:

- **A diagram, or a drawing made of characters** — entries 1 and 2.
- **Prose, a list or a table** — entry 4.
- **A formula** — entry 3.
- **A list's marker, numbering or introduction** — entry 5.
- **A table's header, key column or empty cell** — entry 6.
- **A heading's level or case** — entry 7.
- **A fenced block or a name in prose** — entry 8.
- **Bold or italic** — entry 9.
- **A note, tip or warning** — entry 10.
- **A template** — every entry. A template follows the guide as any document does. It shows a
  departure only where its kind's departure entry allows it.

A project that added entries beyond the founding ten numbers them on. The guide is the list.

## 3. Declare a departure, never mark it

Where a document must depart from a default, do not mark the document. Examples are one diagram
Mermaid cannot draw, or a table whose empty cells mean "none" by its own legend. Add an entry to
`const-styling.departures` in `constitution.yaml`:

```yaml
const-styling:
  departures:
    - paths: ["/docs/design/timing.md"]   # one document by path, or a pattern for a kind
      allow: [plantuml]                    # the signature keys the scan may pass there
      reason: a timing diagram, which Mermaid has no form for
```

A departure for a whole kind of document names, in `paths`, the kind's territory. Some
documents are frozen by a rule of the project, say records accepted before the default existed.
A departure for them names their number range by a character class.
`docs/records/rec-00[0-3]*.md` is such a class. A frozen document takes first the wording edits
its policy allows, if any. The departure covers only what those cannot fix. The document is
never taken out of the scan's territory. A second document needing the same one-off departure
is the signal to widen the entry to the kind, or to change the guide's default.

## 4. Read a finding

The scan, `check-style.sh --scan`, reports twelve traces of the defaults. They are a PlantUML
block, a formula, a callout, a heading of level four or deeper, a skipped heading level and a
second title. Then come a fence without a language, a bullet marker other than a dash, an ordered
item out of sequence and emphasis by underscores. The last are a table row with the wrong number
of cells and an empty table cell. Each finding names the file and line, why the default exists
and the fix. The fix is to follow the default, or to declare the departure as step 3 says.
Everything else in the guide is judgment, and the scan does not claim it. That is whether prose
was due, a drawing trivial, or a key column first.

## 5. Add a default

A question the guide does not answer is answered once, through the project's decision path.
The answer is added to the guide as the next numbered entry with its examples. It is born with
the document that needed it. The question is never answered in one document, one template or one commit message alone.
