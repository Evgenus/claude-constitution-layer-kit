# const-doc-budgets

<a id="a1"></a>
## What it gives you

A character ceiling per group of documents, measured after every write and in a scan: each ceiling names its documents by path patterns, its number and the days of data it was set from, and warns until 30 days of data stand behind it; a history report over git gives those data; a document that must stand over its ceiling is declared as a departure in the dials file. Plus a skill for setting a ceiling and reading a finding.

<a id="a2"></a>
## Why use it

A document a project keeps grows with every change that touches it. Nobody measures what that costs the reader, or the model that loads the document in every session. The kit saw its own session guide grow by a third in one week, and a reference page nearly double in another. Each change decides its own length. No one sees a kind of page getting longer until a reader gives up. A number per group of documents, set from what the group was seen to need, makes the growth visible at the write that causes it.

<a id="a3"></a>
## How Claude behaves with it

The project sets, in `constitution.yaml`, a ceiling per group of documents. Each ceiling has a name, the path patterns of the documents it holds, the maximum length in characters, and a level. It also names the first and last day of the data the number came from. After a session writes or edits a held document, its length is measured. Over the ceiling at level error, the finding is handed to the session beside the result, saying by how much and what to do. At level warning it is a note. Nothing refuses the write. A ceiling may be at level error only once 30 days of data stand behind it. Before that it warns, so a number no data support never blocks. While no ceiling is set, nothing is measured. The session is told so in one line at every session start.

```text
RED: docs/notes/long.md: 309 characters, over the ceiling 'notes' of 200 by 109
  why: a document longer than its kind was observed to need makes every reader, and every session that loads it, pay for text the kind did not need
  fix: shorten it by 109 characters or more, or split it into documents that each stay at or under 200; the ceiling for this repository is the entry 'notes' of const-doc-budgets.ceilings in constitution.yaml; for a document that must stand as written, declare the departure with its reason: add to const-doc-budgets.departures an entry {paths: [<the file, or a pattern of the documents that stand>], allow: [notes], reason: <why they stand, in one line>}
```

The skill `set-ceilings` loads on its own when a ceiling is set, raised or lowered, and when a finding is read. Its rules: a ceiling is set from the history report, never from a wish. The number is the window's longest document plus ten percent, rounded up to a thousand. It stays at warning until 30 days of data stand behind it. A document over its ceiling is split or cut, never squeezed. A document that must stand as written is declared as a departure with its reason, never marked and never hidden from its ceiling.

<a id="a4"></a>
## How it works

**After a write.** A hook runs after every `Write` and `Edit` of a Markdown file a ceiling holds. It counts the whole file in characters, as a reader loads it, never tokens or bytes, and compares the count with the ceiling. It cannot see a file written by a shell command or another person. It does not say how much this one write added.

**The scan.** The same measurement over every held document git lists, from the command line. It exits with code 2 on a finding at level error. It prints one note per ceiling: what it holds, the longest document, and the margin left. Run it in CI and before a merge.

**The history report.** The scan with a start date. It walks the repository's history and prints, per day and per ceiling, the longest held document. Then it prints the window's longest and the rule of thumb beside the number set now. It judges nothing and exits 0; it is where a ceiling's number comes from. A shallow clone is refused until the whole history is fetched.

**At session start, and the skill.** One line while nothing is measured, printed by a hook; and the procedure, loaded when the activity occurs.

**Settings.** The module ships no number: with no ceiling set, nothing is measured. One dial holds the ceilings, each with its name, paths, maximum, level and window. A document two ceilings hold is refused. Another holds the departures, each an entry of paths, the ceilings it lifts there, and a one-line reason. Two dials are every gate's: whether a finding reaches the session as a block or as context, and where the log goes.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-doc-budgets@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-budgets.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
