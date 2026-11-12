# Install — const-task-close

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported at the first turn end, a missing git too, each with the fix on the first line. Nothing is
silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-task-close needs the Python package constitution-layer-kit`,
`BROKEN: const-task-close needs constitution-layer-kit` or
`BROKEN: const-task-close was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). Two hooks print the pointer line, below, at session start and at each subagent's start. The third: at the end of every turn the working tree of the session's repository is
   examined. A dirty tree — any tracked change or untracked file git does not ignore — is
   reported once. Under the default `severity: block` the model receives the finding and the
   turn continues once, for the commit. Under `warn` the user is shown the finding as a notice
   and the model sees nothing. The second stop of a turn always lets it end. While a subagent,
   a teammate or a workflow of the session still runs, the report waits, since the tree may hold
   that agent's files. The first turn end with none running reports the tree. The scan, step 5,
   examines a change before a merge.
2. **Zero configuration works** in a repository whose `constitution.yaml` has `module_prefix`,
   whatever else it says. The turn-end hook judges the tree, and the range check examines zero pairs and says so.
   Without that file every run is a visible skip naming it; `module_prefix: const-` alone is enough.
3. **Switch the range check on: write the coverage map.** A pair names code and the
   current-state documents that describe it. A change that touches the code updates one of the
   documents or declares no impact. In the project's `constitution.yaml`:
   ```yaml
   const-task-close:
     coverage:
       - name: api                         # kebab-case, unique: what a declaration names
         code: ["src/api/**"]              # gitignore patterns of the code the documents describe
         docs: ["docs/design/api.md"]      # repository-relative paths; each an existing file
       - name: build
         code: ["Makefile", "scripts/**"]
         docs: ["docs/design/build.md"]
     trunk: main                # the branch changes land on; the base of a bare scan
     trunk_remote: origin       # the remote whose tracking branch of the trunk is read beside the local one
     declaration_key: No-Doc-Impact   # the trailer key of a no-impact declaration
     working_files: []          # patterns of a task's working files; tracked matches are listed at the scan
     severity: block            # block (default) | warn — the turn-end hook only
     # log_dir: .gate-logs      # optional, and the directory must be git-ignored; see step 7
   ```
   A key of this namespace that is none of those above is refused with exit 1. A misspelt dial is
   never a setting ignored in silence. Pairs may overlap: one file may be described in two places,
   and both pairs then apply. A negated pattern takes a path out only where git can: `src/*` then
   `!src/vendor/` works, `src/**` then `!src/vendor/**` does not. Git re-includes nothing under a
   directory an earlier pattern excluded. A document listed under `docs` that also matches the pair's `code` is
   not its own trigger. Each document is an existing file at HEAD. A path that does not exist, or
   that names a directory, is a configuration failure, not a finding.
4. **Adoption.** `severity: warn` shows the turn-end finding to the user as a notice and lets the
   turn end, the model seeing nothing. Use it in a session that must not be asked to commit. In a session that
   cannot ask — `claude -p`, `dontAsk`, `--permission-prompts none` — a block costs that one
   continuation. In such a session the block leaves the tree dirty unless the commit the
   finding teaches is allowed. That commit is the compound `git add -A && git commit …`, and
   a rule must match each part on its own. So both `Bash(git add *)` and `Bash(git commit *)`
   go in `permissions.allow` or `--allowedTools`; or set `severity: warn`. The range check ignores `severity` and always reports.
5. **Run the range check before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-task-close.sh --scan
   ```
   On a branch it examines the commits since `trunk`, and on the trunk itself the last landed change.
   That change is a merge, or the last commit where the trunk fast-forwards.
   `--since <ref>` names the base; `--change <commit>` examines one landed change — a merge by its
   first-parent diff. Exit 0 green, 2 findings, 1 the checker could not run. The check compares
   commits: an update still sitting in the working tree does not count until it is committed.
   Declare no impact where it is true, with one line per pair. The line is a trailer on a commit of
   the change, in the message's last paragraph. In that paragraph every line is `Key: value`, and one line without
   a colon hides the whole paragraph from git. Or the line stands on its own line in the pull request's
   description:
   ```text
   No-Doc-Impact: api — comments reworded, no rule or message changed
   ```
   The reason is required and never judged by the check. A line naming no pair, or carrying no
   reason, is a finding, and so is a wildcard: one line per pair. The dash is an em or en dash,
   spaced or not, or one or two hyphens spaced on both sides. Every declaration the check accepts is printed as a note, for the reviewer.
   A squash merge keeps a commit's trailer only when that message lands last; a project that
   squashes puts the line in the description.
6. **In CI, on a pull request**, with the whole history fetched (`fetch-depth: 0`), the base from
   the event, and the description written to a file:
   ```bash
   sh <plugin root>/scripts/check-task-close.sh --scan --since "$BASE_SHA" --body body.txt
   ```
   where `$BASE_SHA` is the pull request's base commit from the event payload and `body.txt` holds
   its description. A shallow clone whose history stops before the base cannot see the range, and
   the check relays git's refusal with the fix.
7. Output log: everything the hook and the scan print is also appended to `const-task-close.jsonl`,
   one JSON line per print. The fields of a line are timestamp, module, gate, mode, session, path, transcript, stream and text. Blocked
   turn ends and warnings leave no trace in git. By default it lives in the platform's
   per-plugin data directory. Set `log_dir` to keep it inside the repository. The directory must
   be git-ignored, and the gate refuses to run otherwise.
8. Optional, the fixtures: the install holds no tests. So run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`), `python3 -m pytest <kit clone>/modules/const-task-close/tests -p no:cacheprovider` — all green. The fixtures need
   git 2.45 or newer, since one of them builds a repository in each ref store. On an older git that fixture
   is red and the rest run.
9. CLAUDE.md line: none. The skills `/const-task-close:close-task` and
   `/const-task-close:commit-before-edit` are named at their moment. The pointer line printed at
   session start and at each subagent's start names them (326 characters, advisory). So does the line after the count line of every red of the turn-end hook the model reads, and of the scan.

This module does not check whether a document update is right, or whether a declaration is
true. It does not check whether a file is a working file (a `working_files` match is a note). It
does not check a change merged into the trunk without the scan, until the next scan of the trunk.
It does not check a commit inside a change that touched code without its document, when a later
commit of the same change updated it. It does not check a turn ended by an interrupt, or a
subagent's own turn end. It does not check a tree in a session that has not loaded the plugin.
Nor does it check whose the dirty files are while an agent of the session runs. Your own
uncommitted work waits with that agent's, and a session closed while its agents run gets no report.

Uninstall: remove the plugin; remove the `const-task-close:` namespace from `constitution.yaml`.
The trailers stay in history and mean what they said.
