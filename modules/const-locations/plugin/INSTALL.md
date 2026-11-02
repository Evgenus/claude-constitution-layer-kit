# Install — const-locations

Requires: git; Python 3.12 or newer as `python3`, with the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3`, library or git
is reported by the command with the fix on its first line and nothing is written; nothing is
silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its commands run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.0.0#subdirectory=shared"
```
A line that starts `BROKEN: const-locations needs the Python package constitution-layer-kit`,
`BROKEN: const-locations needs constitution-layer-kit` or
`BROKEN: const-locations was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). The plugin ships two skills, one command and one hook, and nothing here blocks a
   write. The skill `new-document` has the session create a document through the script; the
   skill `new-kind` carries the procedure for a kind no policy covers yet. The hook is a grant:
   it approves the plugin's own script, as step 3 says, and nothing else.
2. Calibration, optional: **zero configuration works** in a repository whose `constitution.yaml`
   names `module_prefix`, a `root_policy` and the policies' territories: every kind whose
   territory is `<dir>/**`, `<dir>/**/*.md` or `<dir>/*/NAME.md` gets its documents created at
   the home that follows, with the four-field envelope and the title's heading as the body.
   Without a `constitution.yaml`, or without a `root_policy`, the command refuses and says what
   to declare first; the `new-kind` skill carries the procedure from zero. To name a template
   per kind, add a `const-locations:` namespace to the project's `constitution.yaml`:
   ```yaml
   const-locations:
     templates:                # the kinds that have a template; none by default
       - {policy: <policy id>, template: <repository-relative path of the template>}
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 5
   ```
   A template is a Markdown file that opens with the envelope a document of the kind carries —
   `id`, `type`, `title`, `status`, and any field the kind adds — with placeholders where the
   writer fills; its `type` decides the created document's type. The command writes `id`,
   `title` and `status` as values, keeps every other envelope line and the whole body as they
   stand, and says on its `TEMPLATE:` line which file it used. A key of this namespace that is
   none of those above is refused with exit 1, `severity` among them: this plugin blocks
   nothing, so the key has no meaning here.
3. The command, from inside the repository:
   ```bash
   sh <plugin root>/scripts/new-document.sh --kind <policy id> --stem <stem> --title '<title>' [--type <meta-type>] [--segment <segment>] [--id <id>] [--dry-run]
   ```
   `--kind` is a policy's id; `--stem` the file name without `.md`, kebab-case, also the id
   unless `--id` is given; `--type` the meta-type when the kind has no template; `--segment`
   in place of `--stem` for a territory with one free segment (`<dir>/*/NAME.md`);
   `--dry-run` prints the home and the template and writes nothing. Exit 0 created or dry run;
   1 refused before anything was written, or the command could not run. It never exits 2:
   a generator has no findings. The skill `/const-locations:new-document <kind> <stem>` carries
   the procedure. No allow rule is needed, in any permission mode and in a session that cannot
   ask — `claude -p`, `dontAsk`, `--permission-prompts none` — for the model's own load of
   either skill or for the command it runs: neither skill pre-approves a tool, so the model
   loads them as any skill, and the plugin's hook on `PreToolUse` answers `allow` for the
   command. It answers for exactly `sh <plugin root>/scripts/new-document.sh` followed by
   values, one space before each, each plain — letters, digits and `_ . / : , @ + -` — or in
   single quotes with no quote and no line break inside; the plugin root is the one Claude Code
   names to the hook, and a root with a space or another character outside that set is matched
   by nothing. Any other call — a second command chained to it, a redirection, a value in
   double quotes, another path — gets no answer from the hook and is asked for as any other.
   A deny or ask rule you write for the command still wins over the hook. The hook runs a
   Python start, about 0.1 s, on each shell call that starts a command with `sh `.
4. Introducing a kind: the skill `/const-locations:new-kind` — the policy first, its territory
   line by hand at the end of `constitution.yaml`, then the first document. The command creates
   the policy itself when given the root policy's id as the kind.
5. Output log: everything the command prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-locations.jsonl` — refusals leave no
   trace in git. By default it lives in the platform's per-plugin data directory. Set `log_dir`
   to keep it inside the repository; the directory must be git-ignored, and the command refuses
   to run otherwise.
6. Optional, the fixtures: the install holds no tests, so run them from a clone of the kit at the
   commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`),
   `python3 -m pytest <kit clone>/modules/const-locations/tests -p no:cacheprovider` — all green.
7. CLAUDE.md line: none. The skill's description is in the session's skill listing, and the
   skill loads on its own when a document is about to be created, and its command needs no
   allow rule (step 3).

What this module does not check: a document written without the command — a heredoc, a
`Write`, an editor — which the write-time gate of module `const-meta-types` catches when
installed, while a document the command writes is no tool event, so that gate judges it in
its scan or at the document's next edit, never at creation; it does not derive a home from a
territory of two patterns, a negation or a `*` inside a file name — the command refuses and
names the shapes that work; it does not check or fill the body, edit `constitution.yaml`, or
allocate a number for a numbered kind. There is no scan, and no `severity: warn` step: the module
blocks nothing.

Uninstall: remove the plugin; remove the `const-locations:` namespace from
`constitution.yaml`. Documents keep their homes.
