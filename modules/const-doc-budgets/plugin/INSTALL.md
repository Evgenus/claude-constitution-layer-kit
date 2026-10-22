# Install — const-doc-budgets

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported by the check with the fix on its first line; nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v1.0.0#subdirectory=shared"
```
A line that starts `BROKEN: const-doc-budgets needs the Python package constitution-layer-kit`,
`BROKEN: const-doc-budgets needs constitution-layer-kit` or
`BROKEN: const-doc-budgets was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). One hook after every write, one line at session start while nothing is measured, one
   scan, one history report, one skill. The hook runs after every `Write` and `Edit` of a Markdown
   document a ceiling holds and hands an excess back to the model; it never refuses a write. The
   skill, `set-ceilings`, is offered to the model when a ceiling is set and when a finding is read.
2. **What is measured.** The length of a document in characters, as the project's conventions
   define one: Unicode code points of the file read as UTF-8, a CRLF counted as one, the whole
   file — envelope, code, tables and link targets — since a reader loads the whole file. Never
   tokens, never bytes, never lines.
3. **Zero configuration measures nothing.** With no ceiling set, the hook skips every write and
   says why, the scan counts zero, and one line at session start says that no document is
   measured. A number no data stand behind would be a target, so the module ships none. Without a
   `constitution.yaml` every run is a visible skip naming it.
4. **Set the first ceilings from data.** Write each group at `level: warning` with a generous
   `max`, then run the history report over the repository's history:
   ```bash
   sh <plugin root>/scripts/check-budgets.sh --scan --since 2026-01-01
   ```
   It prints, per day and per ceiling, the longest document on the first-parent line of HEAD,
   then per ceiling the window's longest document and the rule of thumb — that length plus 10 %,
   rounded up to a multiple of 1,000 — beside the number set now. Put the rule of thumb in `max`
   and the window's first and last day in `window`. A shallow clone is refused: fetch the whole
   history first (`git fetch --unshallow`, or `fetch-depth: 0` in CI).
5. Calibration, in the project's `constitution.yaml`:
   ```yaml
   const-doc-budgets:
     severity: block                  # block: a finding reaches the model as a block after the write; warn: as context
     ceilings:                        # default none: nothing is measured
       - name: records                # kebab-case, unique; a departure names it
         paths: ["docs/records/**"]   # gitignore syntax, or a policy's territory by a YAML alias
         max: 34000                   # characters
         level: warning               # warning: a note, never red; error: a finding
         window:                      # the days of data the number was set from
           from: 2026-01-01
           to: 2026-01-15             # level error needs to 30 days or more after from
       - name: guide
         paths: ["/CLAUDE.md"]
         max: 24000
         level: warning
         window: {from: 2026-01-01, to: 2026-01-15}
     departures:                      # what stands over its ceiling, where, and why; default none
       - paths: ["docs/records/rec-00[0-3]*.md"]   # a pattern for a kind, a number range, or one file by path
         allow: [records]             # the ceilings lifted there; the others still apply
         reason: accepted records stand as written
     # log_dir: .gate-logs            # optional, and the directory must be git-ignored; see step 9
   ```
   A document is held by one ceiling at most: two entries whose paths both match one document are
   refused, since the verdict would hang on the order of the list; take the file out of one entry
   with a file pattern and a negation (`docs/**/*.md`, `!docs/records/*.md`). A key of this
   namespace that is none of the above, or a value that is not of its shape — a name that is not
   kebab-case or given twice, an empty `paths`, a `max` below one, a level that is neither, a
   window that is not two dates written `YYYY-MM-DD`, a departure naming no ceiling or with an
   empty reason, a pattern git would read as a comment or as two lines — is refused with exit 1,
   and the message names the key and the fix.
6. **A ceiling blocks only on 30 days of data.** `level: error` on a window shorter than 30 days
   is refused as a configuration failure, at every read. After 30 days of data, run the report
   again, set the number from it, widen the window and move the level to `error`.
7. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-budgets.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan is red on any finding whatever
   `severity` says; a ceiling at `warning` prints notes and never turns it red. Every scan prints
   one note per ceiling: what it holds, the longest document and the margin left.
8. **A departure is declared, never marked.** A document that must stand over its ceiling is
   named in `departures` with its reason; nothing is marked in the document, and no pattern hides
   it from its ceiling. A departure that lifts nothing — its paths match no document that a
   ceiling it names holds — is a note on every scan until it is removed.
9. Output log: everything the check prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-doc-budgets.jsonl`. By default it lives
   in the platform's per-plugin data directory. Set `log_dir` to keep it inside the repository;
   the directory must be git-ignored, and the check refuses to run otherwise.
10. Optional, the fixtures: the install holds no tests, so run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`), `python3 -m pytest <kit clone>/modules/const-doc-budgets/tests -p no:cacheprovider` — all green.
11. CLAUDE.md pointer: none. The rules ride on the check and the skill.

What this module does not check: whether a long document says what it needs to; whether the
window a ceiling declares is the data its number came from; how much one write made a document
longer; a file written by a shell command or another program, which the hook does not see and the
scan does; a document no ceiling holds.

Uninstall: remove the plugin; remove the `const-doc-budgets:` namespace from `constitution.yaml`.
