# Install — const-interaction

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported on the first shell command of a session and at session start. Each report has the fix on the
first line. Nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-interaction needs the Python package constitution-layer-kit`,
`BROKEN: const-interaction needs constitution-layer-kit` or
`BROKEN: const-interaction was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). Two hooks. At every session start — startup, resume, clear, compaction, fork — the plugin
   prints its rules for every reply into the model's context. They are about 2,400 characters with the verbosity line, and the
   transcript does not show them. The value of `verbosity` follows them. Then comes one line when the
   destructive-command gate examines nothing in the session's repository. Last comes one line for each
   default wrapper or shell your dials drop or replace. Before every `Bash` command the gate reads the command.
   Where a subcommand matches a listed destructive pattern, it asks the platform to prompt you with the
   reason, labelled with the plugin's name. The reason says what matched, why the act is hard to reverse
   and the reversible alternative. You confirm at the prompt, once per command. Where no prompt can be shown, in a
   headless session, the platform denies the command with that reason and the model waits.
2. **Zero configuration works** in a repository whose `constitution.yaml`
   has `module_prefix` and no key of this namespace. There the default list gates a forced push, a hard reset, a forced checkout, `git restore`,
   `git clean -f`, `git branch -D` and `-f`, `git stash drop` and `clear`, `git rebase`, `git filter-branch`,
   `git filter-repo`, `git reflog expire`, `git gc --prune=now` and a recursive `rm`. The list scan
   covers every Markdown file git lists with the default handle forms. Without that file every run
   is a visible skip naming it, and the session-start line says so. `module_prefix: const-` alone
   is enough. The command is read as the platform reads it for its own rules. It is split on `&&`, `||`,
   `;`, `|`, `&` and newlines outside quotes. The contents of `$(…)` and backticks and the string
   after the `-c` of a shell are examined too. The wrappers of the dial `wrappers` are stripped with their own
   options, and a shell keyword is stripped. A program path is reduced to its name, and the options between a
   program and its verb are stepped over. So `git -C . push --force` is a forced push, and so is
   `sudo -k /usr/bin/env git push -f`. The defaults of `wrappers` are `time`, `nohup`, `command`,
   `builtin`, `noglob`, `exec`, `xargs`, `sudo`, `doas`, `env`, `nice`, `stdbuf`, `timeout`,
   `busybox`, `setsid`, `ionice`, `taskset`, `caffeinate`, `flock` and `chrt`. Those of `shells` are
   `bash`, `sh`, `zsh`, `dash`, `ksh`, `fish`, `ash`, `mksh`, `yash`, `posh`, `csh` and `tcsh`, each
   with its options, which the module document lists. A command built from a variable, an `eval`, a
   here-string or an interpreter's `-c` string hides its verb. So does a wrapper or a shell no
   dial names, such as `uv run`. The explain (step 5) shows any reading. A flag matches anywhere after the words and before a `--`: a short one
   inside a cluster (`rm -rf`), a long one as the whole token (`--force`, never
   `--force-with-lease`).
3. Calibration, all optional, in the project's `constitution.yaml`:
   ```yaml
   const-interaction:
     destructive:              # the listed patterns; leave the key out for the default list; [] gates nothing
       - command: [git, push]
         flags: [--force, -f]  # optional: any one matching; without it the words alone match
         teach: a forced push rewrites the branch on the remote for every other clone
         alternative: push with --force-with-lease, or a new branch and a pull request
     wrappers: []              # the programs the reader strips; [] keeps the defaults; an entry adds one or, by its command, replaces one: {command: [uv, run], with_value: [--with]}; {command: [sudo], drop: true} removes one
     shells: []                # the shells whose -c strings are read, as for wrappers: {command: [elvish], command_flags: [-c]}
     territories: ["*.md", "!docs/archive/**"]   # gitignore syntax; the list scan's documents; default ["*.md"]
     handles: ['[0-9]+\.', '[A-Z]\.', '[a-z]\.', '[a-z][0-9]+\.', '[A-Z]+[0-9]+[a-z]?\b', '[A-Z]-[a-z]\b', '\*\*[^*]+\*\*']
     boundary_examples: []     # the project's own pairs, printed at session start: [{violates: "…", complies: "…"}]
     verbosity: triggered      # the one value: assumption and restatement lines only when triggered
     severity: block           # block (default) | warn
     # log_dir: .gate-logs     # optional; see step 7
   ```
   `destructive` is a list of entries — `command` a list of words, `flags` optional, `teach` and
   `alternative` texts. A malformed entry is refused naming it. So is an entry whose words the
   reader does not read as written, such as `[sudo, rm]` or a program path; write `[rm]`.
   `wrappers` and `shells` are lists of entries too. They are merged with their defaults by
   command, a default is removed only by `drop: true`, and each removal or replacement is said at
   session start. An entry that would load and do nothing is refused. `handles` are regular
   expressions matched at the start of an item's text, after an optional anchor and bold marker.
   A project whose documents key items by a bold label, a link or a code span adds those
   forms (`'\*\*[^*]+\*\*'`, `'\[[^\]]+\]\('`, `` '`[^`]+`' ``). `territories` takes a negated
   pattern to leave out a document a later rule may not edit. An empty `territories` or `handles`
   is refused, since it would examine nothing or find everything red in silence. A key of this
   namespace that is none of the nine above is refused with exit 1. A misspelt dial is never a
   setting ignored in silence.
4. **Adoption** onto a repository whose scripts the list would stop at every turn: set
   `severity: warn` meanwhile. The match is then reported to the model and the user, and the
   command runs. Or tune `destructive`. Onto a repository whose documents carry unhandled lists:
   run the scan (step 5), fix or exempt what it lists.
5. **Run the list scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-list-handles.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. To see what the list does to a
   command without running it:
   ```bash
   sh <plugin root>/scripts/check-destructive.sh --scan --command 'git push --force origin main'
   ```
6. CLAUDE.md line: none. The rules ride on the session-start hook; the gate on the shell hook. A
   consumer that cannot run hooks may copy `scripts/rules.txt` into the project's own `CLAUDE.md`
   by hand, as a fallback. The copy drifts on every version bump and the gate does not run — say so in the copy.
7. Output log: everything the hooks and the scans print is also appended to `const-interaction.jsonl`,
   one JSON line per print. The fields of a line are timestamp, module, gate, mode, session, path, transcript, stream and text. A prompt's reason and a denied command leave no trace in git. By default it lives in the
   platform's per-plugin data directory. Set `log_dir` to keep it inside the repository. The
   directory must be git-ignored, and the gate refuses to run otherwise.
8. Optional, the fixtures: the install holds no tests. So run them from a clone of the kit at the commit the install records (`gitCommitSha` in `installed_plugins.json`), `python3 -m pytest <kit clone>/modules/const-interaction/tests -p no:cacheprovider` — all green.

What this module does not check: a command given to the `PowerShell` tool, since the gate is wired
to `Bash` alone. It does not check a destructive act the list does not name. Such an act is an interpreter
one-liner, a script file, a shell function or alias. It is also a deletion through a file tool, or a database
statement inside a quoted argument. It does not check `git checkout -- .` and any pattern that needs an argument
value. It does not check whether a reply matched its question's shape, listed its assumptions or softened a
finding. Nor does it check an item keyed by prose alone, or by a form the `handles` dial does not name, or a document
outside `territories`.

Uninstall: remove the plugin; remove the `const-interaction:` namespace from `constitution.yaml`.
