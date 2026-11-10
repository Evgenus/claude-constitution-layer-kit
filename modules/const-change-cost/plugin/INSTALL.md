# Install — const-change-cost

Requires: git 2.54 or newer, which runs hooks set in its configuration; Node and npm, which run the
pinned ccusage that counts the tokens; Python 3.12 or newer as `python3`; and the libraries in
`requirements.txt` (`python3 -m pip install -r <plugin root>/requirements.txt`). The GitHub command
line `gh` is optional, for `cost-report.sh --pr` alone. A missing `python3`, library, Node or npm is
reported with the fix on the first line; nothing is silently skipped. With a git older than 2.54 the
sessions' starts are logged, the setup refuses, and no commit is logged.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.2.0#subdirectory=shared"
```
A line that starts `BROKEN: const-change-cost needs the Python package constitution-layer-kit`,
`BROKEN: const-change-cost needs constitution-layer-kit` or
`BROKEN: const-change-cost was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). Three hooks and one skill come with it. At every session start, a hook appends the
   session's id, its start time, its source and its transcript's path to the start log, and prints a
   line, below, while this clone logs no commit. A second `SessionStart` hook and a `Stop` hook run in
   the background and count every commit whose window is complete: after each turn, and at each
   start. The skill `share-costs` tells a session how to put the counts into a pull request and a
   merge commit, and to share them only when a person starts it: by a command, or by asking the session to
   open a pull request or make a merge. A hook never starts it. The pinned ccusage comes with the
   plugin as a manifest and a lockfile in its folder `ccusage/`, and the platform installs nothing for
   them. The count installs ccusage into the plugin's data folder, with `npm ci --ignore-scripts`, at the
   first pass that has a complete window to count. The start hook and the count record that data folder
   in the clone, so that a count you run by hand, in a shell that has no `CLAUDE_PLUGIN_DATA`, finds the
   same ccusage.
2. **Once per clone, a person runs the setup command.** It writes two hooks into the clone's git
   configuration, `hook.const-change-cost-commit` on `post-commit` and
   `hook.const-change-cost-merge` on `post-merge`, which log every commit with the session that made
   it:
   ```bash
   sh "<plugin root>/scripts/setup-commit-log.sh"
   ```
   Only a person runs it: a session changes git's configuration only when asked. While either hook is
   missing, the start line names it at every session start, and a commit made before the setup is
   never logged, so never counted. `--check` tells whether both hooks stand and exits 0 either way;
   `--remove` takes both out and keeps the logs and the counts.
3. **The count** runs by itself, after each turn and at each start. A person can run it:
   ```bash
   sh "<plugin root>/scripts/count-costs.sh" --all
   ```
   A commit is counted once its window is complete, which is when the session has a record dated after
   the commit. Each count is one line, written once and never made again. Where it knows no data folder
   to install ccusage into, it says so: start a session in this project, which records the data
   folder, and run it again.
4. **The report**, run by a person or by a session at their word, from anywhere in the clone:
   ```bash
   sh "<plugin root>/scripts/cost-report.sh" [<range>]
   sh "<plugin root>/scripts/cost-report.sh" --trailer <range>
   sh "<plugin root>/scripts/cost-report.sh" --pr <range>
   sh "<plugin root>/scripts/cost-report.sh" --notes <range>
   ```
   The range is such as `main..HEAD`. The plain report lists each commit with its tokens and cost and
   names each commit that is not counted, with the reason. `--trailer` prints the lines for the last
   paragraph of a merge commit's message. `--pr` writes a block into the pull request's description
   through `gh`, and prints it where `gh` finds no pull request. `--notes` writes one git note for each
   counted commit under `refs/notes/change-cost`. The module never pushes: share the notes by
   `git push <remote> refs/notes/change-cost`, which publishes every count and cost. Every cost is the
   list price of ccusage's table at the pinned version, not what anyone paid.
5. Where the logs live: the two logs and the file of counts, in the folder `const-change-cost/` of the
   clone's git common directory, shared by every worktree of the clone — the start log, the commit log and
   the file of counts. They are never committed or pushed, and the module writes no file in the working tree.
   Everything the hooks and commands print is also appended, one JSON line per print, to
   `const-change-cost.jsonl` in the platform's per-plugin data directory, where one is set.
6. Optional, the fixtures: the install holds no tests, so run them from a clone of the kit at the
   commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`),
   `python3 -m pytest <kit clone>/modules/const-change-cost/tests -p no:cacheprovider`. They need git
   2.54 or newer, Node, npm and the network once, to install the pinned ccusage into a scratch folder.
7. CLAUDE.md line: none. The skill `/const-change-cost:share-costs` is named by the start line, which
   is printed while a hook of the commit log is missing; no session has been found to skip it at a
   merge. This module has no dials of its own. Only the effect report reads the project's `constitution.yaml`,
   and then only the key `log_dir` that every module's namespace takes; no other entry reads it.

What this module does not check: it blocks nothing and no check holds its numbers. It does not count
a commit made before the setup, one made by a tool that runs no git hook, one made on a forge's page,
or one whose session started before the plugin was enabled. It does not count the tokens of a
compaction, which reach no transcript. It does not count a session whose transcript Claude Code's
cleanup removed (30 days by default) before the window was counted. A cost is the list price, not a bill.

Uninstall: run `sh "<plugin root>/scripts/setup-commit-log.sh" --remove` first, then remove the plugin.
The logs and the counts stay in the git common directory; delete the folder `const-change-cost/` there
to remove them. Trailers, blocks and notes already shared stay in history and mean what they said.
