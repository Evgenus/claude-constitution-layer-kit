# Install — const-interaction

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported on the first shell command of a session and at session start, each with the fix on the
first line; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). Two hooks. At every session start — startup, resume, clear, compaction, fork — the plugin
   prints its rules for every reply into the model's context (about 2,400 characters with the verbosity line; the
   transcript does not show them), followed by the value of `verbosity`, by one line when the
   destructive-command gate examines nothing in the session's repository, and by one line for each
   default wrapper or shell your dials drop or replace. Before every `Bash` command the gate reads the command and,
   where a subcommand matches a listed destructive pattern, asks the platform to prompt you with the
   reason — what matched, why the act is hard to reverse, the reversible alternative — labelled with
   the plugin's name; you confirm at the prompt, once per command. Where no prompt can be shown, in a
   headless session, the platform denies the command with that reason and the model waits. A copy of
   this plugin's folder made outside the repository it comes from must follow links (`cp -RL`):
   `scripts/constitution_layer_kit`, and `constitution_layer_kit` and the shared test files in `tests/`, are
   links to code the plugin shares with its siblings, and an install from the marketplace copies
   what they point at; `tests/interaction_gate` is a link to this plugin's own `scripts/interaction_gate`, which an install from the marketplace keeps as a link. A checkout made without symlink support leaves one-line text files in their
   place (`git config core.symlinks true`, then check out again).
2. **Zero configuration works** in a repository that has a `constitution.yaml` with no key of this
   namespace: the default list gates a forced push, a hard reset, a forced checkout, `git restore`,
   `git clean -f`, `git branch -D` and `-f`, `git stash drop` and `clear`, `git rebase`, `git filter-branch`,
   `git filter-repo`, `git reflog expire`, `git gc --prune=now` and a recursive `rm`; the list scan
   covers every Markdown file git lists with the default handle forms. Without that file every run
   is a visible skip naming it, and the session-start line says so; an empty mapping, `{}`, is
   enough. The command is read as the platform reads it for its own rules: split on `&&`, `||`,
   `;`, `|`, `&` and newlines outside quotes, the contents of `$(…)` and backticks and the string
   after the `-c` of a shell examined too, the wrappers of the dial `wrappers` stripped with their own
   options, a shell keyword stripped, a program path reduced to its name, the options between a
   program and its verb stepped over — so `git -C . push --force` is a forced push, and so is
   `sudo -k /usr/bin/env git push -f`. The defaults of `wrappers` are `time`, `nohup`, `command`,
   `builtin`, `noglob`, `exec`, `xargs`, `sudo`, `doas`, `env`, `nice`, `stdbuf`, `timeout`,
   `busybox`, `setsid`, `ionice`, `taskset`, `caffeinate`, `flock` and `chrt`; those of `shells` are
   `bash`, `sh`, `zsh`, `dash`, `ksh`, `fish`, `ash`, `mksh`, `yash`, `posh`, `csh` and `tcsh`, each
   with its options, which the module document lists. A command built from a variable, an `eval`, a
   here-string or an interpreter's `-c` string hides its verb, and so does a wrapper or a shell no
   dial names, such as `uv run`; the explain (step 5) shows any reading. A flag matches anywhere after the words and before a `--`: a short one
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
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 7
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
   namespace that is none of the nine above is refused with exit 1: a misspelt dial is never a
   setting ignored in silence.
4. **Adoption** onto a repository whose scripts the list would stop at every turn: set
   `severity: warn` meanwhile — the match is then reported to the model and the user and the
   command runs — or tune `destructive`; onto a repository whose documents carry unhandled lists:
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
6. **Fallback** for a consumer that cannot run hooks: copy `scripts/rules.txt` into the project's
   own `CLAUDE.md`. This is a manual step; the copy drifts on every version bump and the gate does
   not run — say so in the copy.
7. Output log: everything the hooks and the scans print is also appended, one JSON line per print
   (timestamp, module, gate, mode, session, stream, text), to `const-interaction.jsonl` — a
   prompt's reason and a denied command leave no trace in git. By default it lives in the
   platform's per-plugin data directory. Set `log_dir` to keep it inside the repository; the
   directory must be git-ignored, and the gate refuses to run otherwise.
8. Verify with pytest: `python3 -m pytest <plugin root>/tests -p no:cacheprovider` — all green.
9. CLAUDE.md pointer: none. The rules ride on the session-start hook; the gate on the shell hook.

What this module does not check: a command given to the `PowerShell` tool, which no hook of this
plugin sees, since the gate is wired to `Bash` alone; a destructive act the list does not name — an interpreter
one-liner, a script file, a shell function or alias, a deletion through a file tool, a database
statement inside a quoted argument; `git checkout -- .` and any pattern that needs an argument
value; whether a reply matched its question's shape, listed its assumptions or softened a
finding; an item keyed by prose alone, or by a form the `handles` dial does not name; a document
outside `territories`.

Uninstall: remove the plugin; remove the `const-interaction:` namespace from `constitution.yaml`.
