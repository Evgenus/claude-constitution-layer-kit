# Install — const-questions

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported on the first `Write` or `Edit` of any file. A missing git is reported on the first one of a
Markdown file. Each is reported with the fix on the first line. Nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-questions needs the Python package constitution-layer-kit`,
`BROKEN: const-questions needs constitution-layer-kit` or
`BROKEN: const-questions was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). Two hooks. The shape of a decision message is printed into the session's context at
   every session start. That holds after a resume, a compaction and a clear too. The text is 648
   characters, advisory. It holds lettered options with **Pros:** and **Cons:** sub-bullets, one
   recommendation and the decider named. It also holds the instruction to load the skill before any
   choice is put. Before every `Write` and `Edit` of a Markdown file the document as it will be after
   the write is checked for open-question markers. A finding blocks the write.
2. Calibration, all optional, in the project's `constitution.yaml`. **Zero configuration works** in a
   repository whose `constitution.yaml` has `module_prefix` and no key of this namespace. There every
   Markdown file git lists is covered. There the markers looked for are `[decide:`, `TODO`, `TBD` and
   `FIXME`. Without that file every run is a visible skip naming it. `module_prefix: const-` alone is
   enough. A marker inside a code span or a fenced code block is a quotation and is never reported. A
   marker that begins or ends with a letter, a digit or an underscore counts only as a whole word. So
   `TODOs` and `TODO_LIST` pass. The match is case-sensitive. A deferred question written in prose
   carries no marker and is not seen: the skill's rule, not the gate's.
   ```yaml
   const-questions:
     territories: ["*.md", "!drafts/**"]   # gitignore syntax; default ["*.md"] — a negated pattern takes files out
     markers: ['[decide:', 'TODO', 'TBD', 'FIXME']   # the texts that mark an open question; single quotes
     boundary_examples: []   # the project's own ask / decide pairs: [{ask: "…", decide: "…"}]
     preferences: []         # per decider: [{decider: "…", ask: ["…"], decide: ["…"], pick: tool}]
     severity: block         # block (default) | warn
     # log_dir: .gate-logs   # optional, and the directory must be git-ignored; see step 5
   ```
   `territories` and `markers` are the gate's. An empty list for either is refused, since it would
   examine nothing in silence. So is a marker holding a line break, which could never match. A draft
   whose own convention keeps markers until it is delivered is taken out by a negated pattern
   (`!dir/**`, not `!dir/`) until it is delivered. Examples are a template and a working document with
   inline `[decide: …]` slots. `boundary_examples` and `preferences` are read by the skill as written
   and validated by nobody. A key of this namespace that is none of the six above is refused with
   exit 1. A misspelt dial is never a setting ignored in silence.
3. **Adoption** onto a repository whose documents already carry markers: run the scan (step 4),
   and resolve or exempt what it lists. Or set `severity: warn` meanwhile. The finding is then
   reported to the model and the user, and the write proceeds.
4. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-open-questions.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity` and always
   reports.
5. Output log: the hook and the scan append everything they print to `const-questions.jsonl` too.
   Each print is one JSON line (timestamp, module, gate, mode, session, path, transcript, stream, text). Blocked writes
   leave no trace in git. By default the log lives in the platform's per-plugin data directory. Set
   `log_dir` to keep it inside the repository. The directory must be git-ignored, and the gate
   refuses to run otherwise.
6. Optional, the fixtures: the install holds no tests. So run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`), with `python3 -m pytest <kit clone>/modules/const-questions/tests -p no:cacheprovider` — all green.
7. CLAUDE.md line: none. The session-start text carries the shape of a decision message in
   every session. The skill `/const-questions:ask-or-decide` carries the rest. Its description asks
   for it to be loaded before any message that puts a choice to the user. The rest is whether to
   ask at all, the tool or the letter, and the project's preferences. The rest also covers the open slots a
   question comes from, and the named blocker in place of a deferred question.

This module does not check whether a question should have been asked or decided. It does not check
the shape of a decision message, or a deferred question written in prose. It does not check a document
written through the shell or by a script, until the next scan. It does not check markers inside code,
which are quotations, or a document outside `territories`.

Uninstall: remove the plugin; remove the `const-questions:` namespace from `constitution.yaml`.
