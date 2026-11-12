# Install — const-language

Requires: git, Python 3.12 or newer as `python3`, the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`), and Vale 3.23.0 or newer as
`vale` on PATH. On macOS or Linuxbrew that is `brew install vale`, and the other routes are at
https://vale.sh/docs/install. A missing `python3`, library or `vale`, or a `vale` below the
floor, is reported by the check with the fix on its first line. Nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-language needs the Python package constitution-layer-kit`,
`BROKEN: const-language needs constitution-layer-kit` or
`BROKEN: const-language was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). One check hook, one scan, one skill, and two pointer hooks. The check hook runs after
   every `Write` and `Edit` of a covered Markdown document and hands the findings back to the
   model. It never refuses a write. The scan reads every covered document. The skill,
   `plain-language`, is for the model to load before prose is written and when a finding is read.
   The two pointer hooks, at session start and at each subagent's start, print one line naming
   it (183 characters, advisory). A line after the count line of every red names it too.
   **What is checked.** The prose of a covered document is checked against five rules. The
   envelope, headings, code spans, code blocks and table cells are left out of the grade. Each
   rule is generated for Vale from the dials on every run. One holds the document's
   Flesch–Kincaid grade against a ceiling, and one each sentence's words against a limit. One
   holds a list of idioms and formal phrases plain language avoids. One holds a list of words
   with one plain replacement, named in the finding. The last is passive voice, reported as a
   note by default. After a write, a grade above the ceiling is a note, not a finding, while it
   is below the document's grade in the last commit. So a long document comes down one edit at a
   time. The scan reads no commit and stays red until the document is at or under the ceiling.
   So run it green before the change is merged (step 4). A Vale comment in a document —
   `<!-- vale … -->` — outside a fence or a code span is blanked before the check reads. It is
   reported as a finding: nothing in a document switches a rule off. The check reads only the
   configuration it generates (`--config`, `--no-global`) and never a `.vale.ini` or a
   `StylesPath` of the repository. So Vale run by hand beside it sees a second configuration.
2. **Zero configuration works** in a repository whose `constitution.yaml` has `module_prefix`
   and no key of this namespace. Then every Markdown file git lists is covered, and the ceiling is
   grade 10. The limit is 25 words, the four rules are red and the passive is a note. Without that
   file every run is a
   visible skip naming it; `module_prefix: const-` alone is enough. Calibration, all optional, in
   the project's `constitution.yaml`:
   ```yaml
   const-language:
     severity: block                              # block: the findings reach the model as a block after the write; warn: as context
     territories: ["*.md", "!docs/archive/**"]    # gitignore syntax; the documents checked; default ["*.md"]
     grade_ceiling: 10                            # Flesch–Kincaid; a document above it is a finding, or after a write a note while its grade falls; default 10
     sentence_words: 25                           # words; a sentence over it is a finding; default 25
     levels:                                      # per rule: error (a finding, red), warning (a note), off; defaults below
       grade: error
       sentence: error
       forbidden: error
       simpler: error
       passive: warning
     forbidden: ["synergy"]                       # phrases of the project's own to avoid; default none
     simpler:                                     # pairs of the project's own; default none
       ascertain: find out
     exceptions: ["leverage"]                     # phrases of the two lists the project keeps; default none
     departures:                                  # what stands as written, where, and why; default none
       - paths: ["docs/records/rec-00[0-3]*.md"]  # a pattern for a kind, a number range, or one file by path
         allow: [grade, sentence]                 # the rule keys the check passes there; the rest still apply
         reason: accepted records stand as written
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 5
   ```
   A key of this namespace that is none of the above, or a value that is not of its shape, is
   refused with exit 1. Such a value is a ceiling below zero or not a finite number, a limit below
   one or not a whole number, a level that is none of the three, or every rule off. It is also a
   list holding an empty or multi-line phrase, a pattern git would read as a comment or as two
   lines, or an exception no list holds. It is also a departure entry that is not a mapping,
   misses a field or holds an unknown one. So is an entry that names a rule the check does not
   know or carries an empty or multi-line reason. The message names the key and the fix; a
   misspelt dial is never a setting ignored in silence. A departure
   whose paths match no covered document is reported as a note on every scan until it is removed.
3. **Adoption onto a repository with many findings:** set `severity: warn` while the documents
   written before the module are fixed. A finding then reaches the session as context, and the
   write goes through. `block` is the default. Set `grade_ceiling` and `sentence_words` to what
   the documents bear today. Set to `warning` the rules the project is not ready for. Rewrite the
   documents kind by kind, and lower the numbers in steps. A document that must not be edited
   takes first the wording edits its policy allows, if any. What they cannot meet is declared as a
   departure with its reason, allowing the rules it cannot meet. The check still reads it for the
   rest. A departure is declared, never marked. An exception, a level, a threshold and a departure
   all stand in the dials file, where every reader sees them. A Vale comment in a document,
   outside a fence or a code span, is a finding.
4. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-language.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan is red on any finding whatever
   `severity` says; a rule at `warning` prints notes and never turns it red.
5. Output log: everything the check prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, path, transcript, stream, text), to `const-language.jsonl`. By default it lives in
   the platform's per-plugin data directory. Set `log_dir` to keep it inside the repository; the
   directory must be git-ignored, and the check refuses to run otherwise.
6. Optional, the fixtures: the install holds no tests. So run them from a clone of the kit at the
   commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`). The
   command is `python3 -m pytest <kit clone>/modules/const-language/tests -p no:cacheprovider` —
   all green. The tests need `vale` on PATH like the check.
7. CLAUDE.md line: none. The skill is named by the pointer line at session start and by the same
   line at every subagent's start. The line after the count line of every red of the check names
   it too. So no line in CLAUDE.md is needed to reach it. The rules ride on the check and the skill.

This module does not check whether a term is defined at first use. It does not check whether a
sentence under the limit holds one idea, or whether a passive was chosen. It does not check a
phrase in a code span or a code block, which is code. It does not check a heading's grade, which
is left out, while a heading's length counts as a sentence. It does not check a file written by
a shell command or another program, which the hook does not see and the scan does. Nor does it
check a document outside `territories`, or chat, which is no document. Two words that only look
like a passive — "is red", "is indeed" — are reported by the passive rule. That is why it is a
note by default.

Uninstall: remove the plugin; remove the `const-language:` namespace from `constitution.yaml`.
