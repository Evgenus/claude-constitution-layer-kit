# const-styling

<a id="a1"></a>
## What it gives you

One style guide every governed document follows — diagrams, prose against lists and tables, list and table format, headings, code blocks, emphasis, callouts — with departures declared per territory or per document in the dials file with a reason; a scan reports the traces of the defaults that no departure allows. Plus a skill that applies the defaults before a diagram, a table, a formula or a template is written.

<a id="a2"></a>
## Why use it

Every document decides its own style at the moment of writing, and decides it differently. One page sets a comparison in a table, the next in a list; one fenced block names no language while its sibling does; a record holds an argument in a two-column table; a template grows a second title and every document born from it inherits one. The pages look uniform only while the same few hands write everything. The judgment that matters most, when prose, when a list, when a table, is one no linter reaches, and the format defaults every linter reaches are never written down.

<a id="a3"></a>
## How Claude behaves with it

Nothing here refuses a write. The project owns one style guide, created from the text the module ships: diagrams are Mermaid, drawings made of characters are for trivial cases only, pseudocode over formulas, prose carries reasoning and a list carries items and a table carries rows of the same fields, lists use dashes and count on, tables have a header row with the key first, headings are in sentence case with three levels at most, code font for what a reader types, every fenced block names its language, bold for a label and italic for a term at first use, and no callout boxes. Each default is defined by a pair of examples. The skill `style-defaults` loads on its own before a session draws a diagram, writes a table, a formula, a deep heading, a note box or a fenced block, or edits a template, and has the session follow the guide. A document that must depart from a default is not marked; the departure is declared in `constitution.yaml`, with the documents, the default and the reason.

The scan reads every covered document for twelve traces the defaults leave, such as a PlantUML block, a formula block, a callout, a heading of level four, a skipped level, a second title, a fence with no language, a bullet opening with an asterisk, a table row with the wrong number of cells, or an empty cell, and reports each that no departure allows.

```text
RED: docs/notes/style.md:3: a fenced block that names no language
  why: the language after the fence tells a renderer how to highlight the block and a reader what it is looking at; without it every viewer guesses
  fix: name the language after the opening fence — ```bash, ```yaml, ```text for a directory tree or plain output, or declare the departure with its reason: add to const-styling.departures in constitution.yaml an entry {paths: [<the file, or a pattern of the documents that depart>], allow: [fence-language], reason: <why no language fits this block, in one line>}
```

<a id="a4"></a>
## How it works

**The scan.** A command-line check over every Markdown file git lists. It reads line shapes, outside fenced blocks except where the fence is the trace, and outside code spans for emphasis; it exits with code 2 on a finding and says how many documents and signatures it examined. It reads twelve shapes, not the ten defaults: whether prose, a list or a table was the right form, whether a drawing is trivial, whether a heading is in sentence case, it cannot judge, and claims nothing about. Nothing runs it on a write or at a turn's end; it is a line of CI and a command before a merge.

**The skill.** A procedure in prose, loaded at the moment of choice. It reads the project's guide and falls back to the shipped text when none is named.

**The shipped guide.** A Markdown file inside the skill, with the ten defaults and their example pairs, which the project copies, gives an envelope and keeps as its own document. A project whose documents are governed by policies gives the guide a policy and has each kind's policy bind its documents to the guide.

**Settings.** The module works with no configuration: every Markdown file git lists is scanned, no departure is allowed, and the skill uses the shipped text. Dials name the documents scanned, the project's style guides for the skill, and the departures: each an entry of paths, the signatures it allows there, and a one-line reason, which is required. There is no loudness dial, since the scan blocks no write, only where the log goes.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-styling@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-style.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md); the complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
