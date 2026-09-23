# Install — const-task-close

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported at the first turn end, a missing git too, each with the fix on the first line; nothing is
silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). One hook: at the end of every turn the working tree of the session's repository is
   examined, and a dirty tree — any tracked change or untracked file git does not ignore — is
   reported once: under the default `severity: block` the model receives the finding and the
   turn continues once, for the commit; under `warn` the user is shown the finding as a notice
   and the model sees nothing. The second stop of a turn always lets it end. Under a permission
   mode that forbids `git commit`, a block costs that one continuation and leaves the tree dirty:
   allow the commit in the session's permission rules — the rule `Bash(git commit *)` — or set
   `severity: warn`. A copy of this
   plugin's folder made outside the repository it comes from must follow links (`cp -RL`):
   `scripts/const_gate`, and `harness.py`, `consumer.py` and `shared_items.py` in `tests/`, are
   links to code the plugin shares with its siblings, and an install from the marketplace copies
   what they point at. A checkout made without symlink support leaves one-line text files in
   their place (`git config core.symlinks true`, then check out again).
2. **Zero configuration works** in a repository that has a `constitution.yaml`, whatever it
   says: the turn-end hook judges the tree, and the range check examines zero pairs and says so.
   Without that file every run is a visible skip naming it; an empty mapping, `{}`, is enough.
3. **Switch the range check on: write the coverage map.** A pair names code and the
   current-state documents that describe it; a change that touches the code updates one of the
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
     declaration_key: No-Doc-Impact   # the trailer key of a no-impact declaration
     working_files: []          # patterns of a task's working files; tracked matches are listed at the scan
     severity: block            # block (default) | warn — the turn-end hook only
     # log_dir: .gate-logs      # optional, and the directory must be git-ignored; see step 7
   ```
   A key of this namespace that is none of those above is refused with exit 1 — a misspelt dial is
   never a setting ignored in silence. Pairs may overlap: one file may be described in two places,
   and both pairs then apply. A negated pattern takes a path out only where git can: `src/*` then
   `!src/vendor/` works, `src/**` then `!src/vendor/**` does not — git re-includes nothing under a
   directory an earlier pattern excluded. A document listed under `docs` that also matches the pair's `code` is
   not its own trigger. Each document is an existing file at HEAD: a path that does not exist, or
   that names a directory, is a configuration failure, not a finding.
4. **Run the range check before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-task-close.sh --scan
   ```
   On a branch it examines the commits since `trunk`; on the trunk itself, the last landed change —
   a merge, or the last commit where the trunk fast-forwards.
   `--since <ref>` names the base; `--change <commit>` examines one landed change — a merge by its
   first-parent diff. Exit 0 green, 2 findings, 1 the checker could not run. The check compares
   commits: an update still sitting in the working tree does not count until it is committed.
5. **Declare no impact where it is true.** One line per pair, either as a trailer on a commit of
   the change — in the message's last paragraph, where every line is `Key: value`; one line without
   a colon hides the whole paragraph from git — or on its own line in the pull request's
   description:
   ```
   No-Doc-Impact: api — comments reworded, no rule or message changed
   ```
   The reason is required and never judged by the check; a line naming no pair, or carrying no
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
7. Output log: every line the hook and the scan print is also appended, as one JSON line
   (timestamp, module, gate, mode, session, stream, text), to `const-task-close.jsonl` —
   blocked turn ends and warnings leave no trace in git. By default it lives in the platform's
   per-plugin data directory. Set `log_dir` to keep it inside the repository; the directory must
   be git-ignored, and the gate refuses to run otherwise.
8. Verify the install: `python3 <plugin root>/tests/run.py` — every item green.
9. CLAUDE.md pointer: none. The skills `/const-task-close:close-task` and
   `/const-task-close:commit-before-edit` load on their own when a task is being finished or a
   batch of edits begins; the hook's message names the second.

What this module does not check: whether a document update is right; whether a declaration is
true; whether a file is a working file (a `working_files` match is a note); a change merged into
the trunk without the scan, until the next scan of the trunk; a commit inside a change that touched
code without its document, when a later commit of the same change updated it; a turn ended by an
interrupt, or a subagent's own turn end; a tree in a session that has not loaded the plugin.

Uninstall: remove the plugin; remove the `const-task-close:` namespace from `constitution.yaml`.
The trailers stay in history and mean what they said.
