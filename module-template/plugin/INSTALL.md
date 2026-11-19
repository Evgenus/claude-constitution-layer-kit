# Install — const-<aspect-name>

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported by the check with the fix on its first line; nothing is silently skipped. Name only what
the module needs; for a module with no script, delete this paragraph.

For a module with a Python entry file, keep this block and write the version; for a module with none, delete it.
The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v<version>#subdirectory=shared"
```
A line that starts `BROKEN: const-<aspect-name> needs the Python package constitution-layer-kit`,
`BROKEN: const-<aspect-name> needs constitution-layer-kit` or
`BROKEN: const-<aspect-name> was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session), then one sentence on each hook, scan and skill it brings.
2. Calibration: add a `const-<aspect-name>:` namespace to the project's `constitution.yaml`.
   Defaults apply otherwise — the module works in a repository whose `constitution.yaml` names
   `module_prefix`. For a module whose defaults examine nothing until a dial is set, this step is
   "Switch the check on" and names that dial.
3. Adoption, for a module with a hook gate: `severity: warn` reports a finding and lets the write
   through, while the documents written before the module are fixed. The default is `block`.
4. Run the scan in CI and before a merge, from anywhere in the repository:
   `sh <plugin root>/scripts/<entry>.sh --scan`. Exit 0 green, 2 findings, 1 the checker could not
   run. Delete this step for a module with no scan.
5. Output log: everything the check prints is also appended, one JSON line per print, to
   `const-<aspect-name>.jsonl`, by default in the platform's per-plugin data directory. That
   directory is set only for hooks: a scan run by hand or in CI writes no log unless `log_dir` is
   set. Set `log_dir` to keep it inside the repository; the directory must be git-ignored, and the
   check refuses to run otherwise. Delete this step for a module with no gate.
6. Optional, the effect report. It counts how often each rule of this module was followed,
   bypassed or missed. Run it from the repository:
   `sh <plugin root>/scripts/effect-report.sh --transcripts <dir> --since <YYYY-MM-DD>`.
   `--transcripts` names the folder where Claude Code keeps this project's session transcripts.
   Without it, a run by hand finds sessions only through the output log, where `log_dir` is set. `--since`
   keeps what happened on or after that date. Where a rule needs judgment, name
   it and say that a language model judges it only with `--reader`, on the person's own
   subscription login. It blocks nothing and is never red: exit 0 once printed, 1 when it could
   not run. Delete this step for a module with no effect report.
7. Optional, the fixtures: the install holds no tests. Run them from a clone of the kit at the
   commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`),
   `python3 -m pytest <kit clone>/modules/const-<aspect-name>/tests -p no:cacheprovider`.
8. CLAUDE.md line, at most one, only where MODULE.md declares one: `<the line>`, or
   "CLAUDE.md line: none" with its reason.

What this module does not check: the paths its gate does not see, in plain words.

Uninstall: remove the plugin; remove the namespace from `constitution.yaml`; remove the CLAUDE.md line.
