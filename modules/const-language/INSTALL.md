# Install — const-language

Requires: git, Python 3.12 or newer as `python3`, the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`), and Vale 3.23.0 or newer as
`vale` on PATH — `brew install vale` on macOS or Linuxbrew, the other routes at
https://vale.sh/docs/install. A missing `python3`, library or `vale`, or a `vale` below the
floor, is reported by the check with the fix on its first line; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). One hook, one scan, one skill. The hook runs after every `Write` and `Edit` of a
   covered Markdown document and hands the findings back to the model; it never refuses a write.
   The scan reads every covered document. The skill, `plain-language`, is offered to the model
   before prose is written and when a finding is read. A copy of this plugin's folder made outside
   the repository it comes from must follow links (`cp -RL`): `scripts/const_gate`, and
   `harness.py`, `consumer.py` and `shared_items.py` in `tests/`, are links to code the plugin
   shares with its siblings, and an install from the marketplace copies what they point at. A
   checkout made without symlink support leaves one-line text files in their place
   (`git config core.symlinks true`, then check out again).
2. **What is checked.** The prose of a covered document — the envelope, headings, code spans,
   code blocks and table cells left out of the grade — against five rules, each generated for
   Vale from the dials on every run: the document's Flesch–Kincaid grade against a ceiling; each
   sentence's words against a limit; a list of idioms and formal phrases plain language avoids;
   a list of words with one plain replacement, named in the finding; passive voice, reported as
   a note by default. A Vale comment in a document — `<!-- vale … -->` — outside a fence or a code
   span is blanked before the check reads and reported as a finding: nothing in a document
   switches a rule off. The check reads only the configuration it generates (`--config`,
   `--no-global`) and never a `.vale.ini` or a `StylesPath` of the repository, so Vale run by
   hand beside it sees a second configuration.
3. **Zero configuration works** in a repository that has a `constitution.yaml` with no key of this
   namespace: every Markdown file git lists is covered, the ceiling is grade 10, the limit 25
   words, the four rules red and the passive a note. Without that file every run is a visible skip
   naming it; an empty mapping, `{}`, is enough.
4. Calibration, all optional, in the project's `constitution.yaml`:
   ```yaml
   const-language:
     severity: block                              # block: the findings reach the model as a block after the write; warn: as context
     territories: ["*.md", "!docs/archive/**"]    # gitignore syntax; the documents checked; default ["*.md"]
     grade_ceiling: 10                            # Flesch–Kincaid; a document above it is a finding; default 10
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
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 8
   ```
   A key of this namespace that is none of the above, a ceiling that is not a number, a limit
   that is not a whole number, a level that is none of the three, every rule off, an exception
   no list holds, or a departure entry missing a field, holding an unknown one, naming a rule the check
   does not know, or carrying an empty or multi-line reason, is refused with exit 1 — a misspelt dial is never a setting ignored in silence. A departure
   whose paths match no covered document is reported as a note on every scan until it is removed.
5. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-language.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan is red on any finding whatever
   `severity` says; a rule at `warning` prints notes and never turns it red.
6. **Adoption onto a repository with many findings:** set `grade_ceiling` and `sentence_words` to
   what the documents bear today, the rules the project is not ready for to `warning`, rewrite
   the documents kind by kind, and lower the numbers in steps. A document that must not be edited
   is declared as a departure with its reason, allowing the rules it cannot meet; the check still
   reads it for the rest, and nothing is marked in the document.
7. **A departure is declared, never marked.** An exception, a level, a threshold, a departure: all
   in the dials file, where every reader sees them; a Vale comment in a document, outside a fence
   or a code span, is a finding.
8. Output log: everything the check prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-language.jsonl`. By default it lives in
   the platform's per-plugin data directory. Set `log_dir` to keep it inside the repository; the
   directory must be git-ignored, and the check refuses to run otherwise.
9. Verify the install: `python3 <plugin root>/tests/run.py` — every item green; the runner needs
   `vale` on PATH like the check.
10. CLAUDE.md pointer: none. The rules ride on the check and the skill.

What this module does not check: whether a term is defined at first use; whether a sentence
under the limit holds one idea; whether a passive was chosen; a phrase in a code span or a code
block, which is code; a heading's grade, which is left out, while a heading's length counts as
a sentence; a file written by a shell command or another program, which the hook does not see
and the scan does; a document outside `territories`; chat, which is no document. Two words that
only look like a passive — "is red", "is indeed" — are reported by the passive rule, which is why
it is a note by default.

Uninstall: remove the plugin; remove the `const-language:` namespace from `constitution.yaml`.
