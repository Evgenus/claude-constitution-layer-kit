# const-language

<a id="a1"></a>
## What it gives you

Plain prose in governed documents, checked by Vale after every write and in a scan: a Flesch–Kincaid grade ceiling, a words-per-sentence limit, idioms and formal phrases plain language avoids, formal words with a plain replacement, passive voice reported — every threshold and level a dial, a departure declared in the dials file and never marked in the document. Plus a skill that applies the rules while writing and reads a finding.

In plain words: after every write of a Markdown page, Vale, a free program that checks prose, reads it and reports what a non-native reader would stumble on. A Flesch–Kincaid grade is a score for how many years of school a text assumes; the ceiling is the highest grade a page may reach. The limit is the most words one sentence may hold. An idiom is a phrase whose meaning is not the meaning of its words. A formal phrase is a long way of saying something short. A passive is a sentence that hides who acts. A scan is the same check over every page at once. A dial is a setting, and the dials file is the project's one file of settings. A departure is a page declared there as one that must stand as written.

<a id="a2"></a>
## Why use it

The documents a project keeps are read by people whose first language is not English. A model reads them too, in every session. Nobody measures what that reading costs. Each page decides its own density at the moment of writing. A reader who cannot follow a sixty-word sentence has no number to point at. A writer who was never told the limit cannot keep it. The kit measured its own pages before any rule existed. A third of them were above the tenth grade, and three sentences in ten were over twenty-five words.

With the module installed, a session gets the findings right after it writes, with the plain word named, and rewrites before moving on. The scan in CI holds every page to the same numbers. A repository with many findings starts at the numbers its pages bear today and lowers them in steps. The prose gets plainer with every change.

<a id="a3"></a>
## How Claude behaves with it

After a session writes or edits a covered Markdown file, the file's prose is checked, and the findings are handed back to the session. Five rules apply. The document's reading grade is checked against a ceiling. Each sentence's length is checked against a limit. A list of idioms and formal phrases that plain language avoids is applied. A list of formal words is applied, each with one plain replacement, named in the finding. Passive voice is reported as a note by default. Nothing refuses the write: the findings arrive beside the result, as a block to act on or as context, and the session rewrites. A comment in the document that would switch a rule off is itself a finding. What departs from a rule is declared in the dials file, where every reader sees it.

```text
RED: docs/notes/dense.md:3: 'utilize' where the plain word is 'use'
  why: a long or formal word costs a non-native reader a dictionary where the plain one does not
  fix: write 'use'; a word this repository keeps on purpose is named in const-language.exceptions in constitution.yaml; for a document that must stand as written, declare the departure with its reason: add to const-language.departures in constitution.yaml an entry {paths: [<the file, or a pattern of the documents that stand>], allow: [simpler], reason: <why they stand, in one line>}
```

The skill `plain-language` is for loading before prose is written in a covered document, and when a finding is read. Its rules: one idea per sentence, and a long sentence is split at a clause, never squeezed. The plain word. No idiom. Name who acts. A term of the project's own is defined in one clause at first use. A phrase the project keeps on purpose is an exception in the dials file, never a mark in the document.

<a id="a4"></a>
## How it works

**The hook after a write.** This hook runs after every `Write` and `Edit` of a covered Markdown file. It blanks the file's front matter and every Vale comment, and copies the document to a temporary folder. It generates the five rules for Vale from the dials and runs Vale once. It maps each result back to the document's own line and prints the findings. It needs the `vale` tool on the machine, version 3.23 or newer. A missing tool is reported as a failure with the install command, never as a silent pass. The hook cannot see a file written by a shell command or another person. The grade is Flesch–Kincaid as Vale counts words, sentences and syllables, over the prose outside headings, code and tables, and a heading counts as a sentence for the word limit. Other tools give the same text a grade a year or two apart, so a ceiling means "grade N by Vale".

**The scan.** The same check over every covered document, from the command line. It exits with code 2 on a finding at level error. A rule at level warning prints notes and never turns it red. Run it in CI and before a merge, on a runner that has Vale.

**The skill.** A procedure in prose. Nothing in it blocks. After every red the check names it, so that it is loaded when a finding is read.

**The hook at session start.** It prints one line that names the skill and says when to load it: before prose is written in a covered document, and when the check reports a finding. It judges nothing and carries no rule.

**The hook at a subagent's start.** It gives the same line to each subagent as context, since a subagent starts without what the session was told.

**Settings.** The module works with no configuration. Every Markdown file git lists is covered, the ceiling is grade 10, the limit 25 words, the four rules red and the passive a note. Dials name the documents covered, the two numbers, and the level of each rule. Further dials add the project's own forbidden phrases and its own pairs of a formal word and its plain one. Another names the phrases of either list the project keeps on purpose. The departures are entries of paths, the rules allowed there, and a one-line reason. A repository with many findings adopts the module by setting the numbers to what its pages bear today, and lowering them in steps. Two dials are every gate's: whether a finding reaches the session as a block or as context, and where the log goes.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-language@claude-constitution-layer-kit --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-language.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
