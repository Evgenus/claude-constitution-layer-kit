# const-language

<a id="a1"></a>
## What it gives you

Plain prose in governed documents, checked by Vale after every write and in a scan: a Flesch–Kincaid grade ceiling, a words-per-sentence limit, idioms and formal phrases plain language avoids, formal words with a plain replacement, passive voice reported — every threshold and level a dial, a departure declared in the dials file and never marked in the document. Plus a skill that applies the rules while writing and reads a finding.

<a id="a2"></a>
## Why use it

The documents a project keeps are read by people whose first language is not English, and by a model that reads them in every session, and nobody measures what that reading costs. Each page decides its own density at the moment of writing. A reader who cannot follow a sixty-word sentence has no number to point at, and a writer who was never told the limit cannot keep it. The kit measured its own pages before any rule existed: a third of them above the tenth grade, and three sentences in ten over twenty-five words.

<a id="a3"></a>
## How Claude behaves with it

After a session writes or edits a covered Markdown file, the file's prose is checked, and the findings are handed back to the session: the document's reading grade against a ceiling, each sentence's length against a limit, a list of idioms and formal phrases that plain language avoids, a list of formal words with one plain replacement, named in the finding, and passive voice, reported as a note by default. Nothing refuses the write: the findings arrive beside the result, as a block to act on or as context, and the session rewrites. A comment in the document that would switch a rule off is itself a finding; what departs from a rule is declared in the dials file, where every reader sees it.

```text
RED: docs/notes/dense.md:3: 'utilize' where the plain word is 'use'
  why: a long or formal word costs a non-native reader a dictionary where the plain one does not
  fix: write 'use'; a word this repository keeps on purpose is named in const-language.exceptions in constitution.yaml; for a document that must stand as written, declare the departure with its reason: add to const-language.departures in constitution.yaml an entry {paths: [<the file, or a pattern of the documents that stand>], allow: [simpler], reason: <why they stand, in one line>}
```

The skill `plain-language` loads on its own before prose is written in a covered document and when a finding is read. Its rules: one idea per sentence, and a long sentence is split at a clause, never squeezed; the plain word; no idiom; name who acts; a term of the project's own defined in one clause at first use; and a phrase the project keeps on purpose is an exception in the dials file, never a mark in the document.

<a id="a4"></a>
## How it works

**After a write.** A hook runs after every `Write` and `Edit` of a covered Markdown file. It blanks the file's front matter and every Vale comment, copies the document to a temporary folder, generates the five rules for Vale from the dials, runs Vale once, maps each result back to the document's own line, and prints the findings. It needs the `vale` tool on the machine, version 3.23 or newer, and reports its absence as a failure with the install command, never as a silent pass. It cannot see a file written by a shell command or another person.

**The scan.** The same check over every covered document, from the command line, exit code 2 on a finding at level error; a rule at level warning prints notes and never turns it red. Run it in CI and before a merge, on a runner that has Vale.

**The skill.** A procedure in prose. Nothing in it blocks.

**The numbers are Vale's.** The grade is Flesch–Kincaid as Vale counts words, sentences and syllables, over the prose outside headings, code and tables; a heading counts as a sentence for the word limit. Other tools give the same text a grade a year or two apart, so a ceiling means "grade N by Vale".

**Settings.** The module works with no configuration: every Markdown file git lists is covered, the ceiling is grade 10, the limit 25 words, the four rules red and the passive a note. Dials name the documents covered, the two numbers, the level of each rule, the project's own forbidden phrases and its own pairs of a formal word and its plain one, the phrases of either list it keeps on purpose, and the departures: each an entry of paths, the rules it allows there, and a one-line reason. A repository with many findings adopts the module by setting the numbers to what its pages bear today and lowering them in steps. Two dials are every gate's: whether a finding reaches the session as a block or as context, and where the log goes.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-language@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-language.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md); the complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
