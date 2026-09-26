---
name: style-defaults
description: >
  Apply the project's style defaults before writing a diagram, a table, a list, a formula, a
  heading below level three, a callout or a fenced block in a document, and declare a departure
  from a default in the dials file with its reason instead of marking the document. Use when
  about to draw a diagram, when choosing between prose, a list and a table, when about to write a
  formula, a fourth heading level or a note box, when writing or editing a template, when the
  style scan reports a signature, and when a repository has no style guide yet. Advisory: it
  shapes the choice; the scan checks only the twelve traces it knows.
---

# Style defaults

A style decision made in one document is made again in the next, differently. This procedure
reads the project's one style guide before the moment of choice, and puts a departure where it
belongs — in the dials file, with its reason — so that every document is uniform and every
exception is on record. It is judgment from start to finish, except the scan named in step 4.

## 1. Find the guide

The style guides are the documents the project names in `const-styling.guides` of
`constitution.yaml`, path patterns over the repository; where the key is absent, look for a
document titled "Style guide" in the project's documentation folder. Read the guide whole once
per session — it is short, one numbered entry per default, each defined by its examples.

Where the repository has no style guide, create one from `style-guide.md` beside this file:
fill its envelope — the `id` a stable kebab-case name — put it where the project's documents of
that kind live, and name its path in `const-styling.guides`. The file carries the founding
defaults: Mermaid for diagrams, character drawings for trivial cases only, pseudocode over
formulas, prose against lists against tables, list format, table format, heading levels, code
font and fence languages, emphasis, no callouts. A project that governs its documents by
policies gives the guide a policy of its own first, as its constitution asks for any new kind.

## 2. Before the choice

At each of these moments, apply the entry of the guide that rules on it:

- **A diagram.** Mermaid in a fenced block marked `mermaid`. Boxes drawn with characters
  only for a trivial case the guide's examples name; a PlantUML block only with a departure.
- **Prose, a list or a table.** Prose for reasoning; a list for items a reader will cite, each
  with a handle; a table only where every row has the same three or more fields, the key first.
- **A formula.** Pseudocode in a fenced block, or words and a code span.
- **A heading.** One title, sections at level two, level three at most, no skipped level.
- **A fenced block.** Its language after the fence; `text` for a tree or plain output.
- **Emphasis.** Bold for a label or a handle, italic for a note about the document or a term
  at first use, asterisks only.
- **A note, tip or warning.** A sentence in its paragraph, never a callout.
- **A template.** A template follows the guide as any document does, and shows a departure
  only where its kind's departure entry allows it.

## 3. Declare a departure, never mark it

Where a document must depart from a default — one diagram Mermaid cannot draw, a table whose
empty cells mean "none" by its own legend — do not mark the document. Add an entry to
`const-styling.departures` in `constitution.yaml`:

```yaml
const-styling:
  departures:
    - paths: ["/docs/design/timing.md"]   # one document by path, or a pattern for a kind
      allow: [plantuml]                    # the signature keys the scan may pass there
      reason: a timing diagram, which Mermaid has no form for
```

A departure for a whole kind of document names the kind's territory in `paths`. A second
document needing the same one-off departure is the signal to widen the entry to the kind, or to
change the default in the guide.

## 4. Read a finding

The scan, `check-style.sh --scan`, reports twelve traces of the defaults: a PlantUML block, a
formula, a callout, a heading of level four or deeper, a skipped heading level, a second title,
a fence without a language, a bullet marker other than a dash, an ordered item out of sequence,
emphasis by underscores, a table row with the wrong number of cells, an empty table cell. Each
finding names the file and line, why the default exists and the fix: follow the default, or
declare the departure as step 3 says. Everything else in the guide — whether prose was due, a
drawing trivial, a key column first — is judgment, and the scan does not claim it.

## 5. Add a default

A question the guide does not answer is answered once, through the project's decision path,
and added to the guide as the next numbered entry with its examples, born with the document
that needed it. It is never answered in one document, one template or one commit message alone.
