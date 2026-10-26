# Install — const-questions

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported on the first `Write` or `Edit` of any file, a missing git on the first one of a Markdown
file, each with the fix on the first line; nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v1.0.0#subdirectory=shared"
```
A line that starts `BROKEN: const-questions needs the Python package constitution-layer-kit`,
`BROKEN: const-questions needs constitution-layer-kit` or
`BROKEN: const-questions was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). Two hooks. At every session start — after a resume, a compaction and a clear too — the shape
   of a decision message is printed into the session's context, 648 characters, advisory: lettered
   options with **Pros:** and **Cons:** sub-bullets, one recommendation, the decider named, and
   the instruction to load the skill before any choice is put. Before every `Write` and `Edit` of
   a Markdown file the document as it will be after the write is checked for open-question
   markers, and a finding blocks the write.
2. Calibration, all optional, in the project's `constitution.yaml`. **Zero configuration works** in a
   repository whose `constitution.yaml` has `module_prefix` and no key of this namespace: every
   Markdown file git lists is covered, and the markers looked for are `[decide:`, `TODO`, `TBD` and
   `FIXME`. Without that file every run is a visible skip naming it; `module_prefix: const-` alone is
   enough. A marker inside a code span or a fenced code block is a quotation and is never reported; a
   marker that begins or ends with a letter, a digit or an underscore counts only as a whole word, so
   `TODOs` and `TODO_LIST` pass; the match is case-sensitive. A deferred question written in prose
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
   `territories` and `markers` are the gate's; an empty list for either is refused, since it would
   examine nothing in silence, and so is a marker holding a line break, which could never match. A draft whose own convention keeps markers until it is delivered —
   a template, a working document with inline `[decide: …]` slots — is taken out by a negated
   pattern (`!dir/**`, not `!dir/`) until it is delivered. `boundary_examples` and `preferences`
   are read by the skill as written and validated by nobody; a key of this namespace that is none
   of the six above is refused with exit 1 — a misspelt dial is never a setting ignored in silence.
3. **Adoption** onto a repository whose documents already carry markers: run the scan (step 4),
   resolve or exempt what it lists, or set `severity: warn` meanwhile — the finding is then
   reported to the model and the user and the write proceeds.
4. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-open-questions.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity` and always
   reports.
5. Output log: everything the hook and the scan print is also appended, one JSON line per print
   (timestamp, module, gate, mode, session, stream, text), to `const-questions.jsonl` — blocked
   writes leave no trace in git. By default it lives in the platform's per-plugin data directory.
   Set `log_dir` to keep it inside the repository; the directory must be git-ignored, and the gate
   refuses to run otherwise.
6. Optional, the fixtures: the install holds no tests, so run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`), `python3 -m pytest <kit clone>/modules/const-questions/tests -p no:cacheprovider` — all green.
7. CLAUDE.md line: none. The session-start text carries the shape of a decision message in
   every session; the skill `/const-questions:ask-or-decide` — whose description asks for it to
   be loaded before any message that puts a choice to the user — carries the rest: whether to
   ask at all, the tool or the letter, the project's preferences, the open slots a question comes
   from, and the named blocker in place of a deferred question.

What this module does not check: whether a question should have been asked or decided; the shape
of a decision message; a deferred question written in prose; a document written through the shell
or by a script, until the next scan; markers inside code, which are quotations; a document outside
`territories`.

Uninstall: remove the plugin; remove the `const-questions:` namespace from `constitution.yaml`.
