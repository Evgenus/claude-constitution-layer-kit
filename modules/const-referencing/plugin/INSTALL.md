# Install — const-referencing

Requires: git. It requires Python 3.12 or newer as `python3`, with the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). It also requires `lychee` 0.24.2 or newer on
`PATH` (<https://lychee.cli.rs/installation/>), in every session and on the CI runner.
That binary is needed there, since the check after a write and the scan both ask it whether links resolve. A missing `python3` or
library is reported on the first `Write` or `Edit` of any file. A missing git or `lychee` is reported on the
first one of a Markdown file. Each report has the fix on the first line; nothing is silently skipped.
Without `lychee` the forms of references are still checked and blocked. Whether they resolve is
not, and every write says so until it is installed.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks and commands run, at the tag of the highest `REQUIRES`
among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-referencing needs the Python package constitution-layer-kit`,
`BROKEN: const-referencing needs constitution-layer-kit` or
`BROKEN: const-referencing was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). It has three hooks. Before every `Write` and `Edit` of a Markdown file the forms of its
   references are checked, and a finding blocks the write. After it the whole tree is checked
   and what the write broke is reported. This cannot block, since the write has happened. At
   session start two sentences about references in chat are added to the session's context.
2. **Zero configuration works** in a repository whose `constitution.yaml` has `module_prefix`,
   whatever else it says: every Markdown file git lists is covered. Without that file every run is a visible
   skip naming it; `module_prefix: const-` alone is enough. Covered documents are checked for three forms. The first is a
   covered document's id in backticks outside a link. The second is a link whose text is such an id and
   whose target is another file. The third is a path on one machine. That is a path into a user's home directory as macOS, Linux and Windows lay it
   out, or a `file:` link. Other absolute paths are not judged. The third is read
   inside code and comments too, where every other check of form leaves code alone. Covered
   documents are checked too for three breaks. One is a link target that does not exist. One is an anchor that does not
   exist. The last is a link that resolves only through a heading's generated name instead of an anchor
   written in the target.
3. Calibration, all optional, in the project's `constitution.yaml`:
   ```yaml
   const-referencing:
     territories: ["*.md", "!vendor/**"]   # gitignore syntax; default ["*.md"]
     governed_only: false      # true: only documents a policy governs; needs root_policy
     heading_anchors: refuse   # refuse (default) | allow — see adoption, step 4
     bare_ids: refuse          # refuse (default) | allow — for ids that are everyday words
     local_paths: refuse       # refuse (default) | allow — for documents that must show a home directory
     severity: block           # block (default) | warn
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 7
     lanes:                    # the project's own bare forms; none by default
       - pattern: '\bREQ-[0-9]+\b'
         names: a requirement
         fix: '[REQ-7](<path to the document that defines them>#req-7)'
         home: ["<pattern of that document>"]
     mentions:                 # ids named outside Markdown; none by default; scan only
       - pattern: '\brfc-[0-9]{4}-[a-z0-9-]+'
         files: ["<patterns of the files that name documents>"]
   ```
   A key of this namespace that is none of those above is refused with exit 1. A misspelt dial
   is never a setting ignored in silence.
   A negated pattern takes documents out: `"!vendor/**"` after `"*.md"` leaves a whole tree
   uncovered. `"!vendor/"` does not — it names the directory, and the files inside it still
   match `"*.md"`.
   A lane declares a form the project writes as a link everywhere but in its home documents.
   Its key `pattern` finds it where it stands bare, outside links, code and the YAML block that opens
   a file. The keys `names` and `fix` fill the finding (`'REQ-7' cites a requirement by a bare handle` …
   `write it as a link: [REQ-7](…)`). The reason the finding gives is the plugin's own and
   cannot be replaced. **Write a pattern in single quotes**: there a backslash stands for
   itself. In double quotes YAML reads `\b` as a backspace. A pattern holding such a
   character is a configuration failure, since compiled it would match nothing and pass in
   silence. A pattern that is no regular expression is a configuration failure that quotes the
   compiler. A mention's `pattern` says how a document's id looks where a script or a
   configuration file names it. Its whole match must be the id of a covered document. Without
   `files` every file git lists that is no Markdown, no link and not binary is read.
   Fixtures and examples are read too, so name the places that mean it.
4. Adopting a repository whose links already exist: set `severity: warn` so that nothing is
   blocked. Set `heading_anchors: allow` too if its links go through headings, as most repositories'
   do. Run the scan; repair what does not resolve first. Then convert heading links at your own
   pace — an `<a id="key"></a>` line before the heading, the key cited — and remove `allow`
   when the scan is green without it.
5. Backstop for what the hooks cannot see: `git mv`, shell edits, other tools and other people.
   The scan is that backstop, and also **the gate for whether references resolve**. Run the scan on demand, and in CI on every
   pull request, on a runner with `lychee` installed:
   ```bash
   sh <plugin root>/scripts/check-references.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`. The
   plugin starts `lychee` itself, outside the repository and with its own configuration. A
   `lychee.toml` or a `.lycheeignore` of the project's has no effect on this check. None of
   the options of `lychee` is a dial.
6. Moving or renaming a document: `sh <plugin root>/scripts/move-document.sh <old> <new>` moves
   it with `git mv`. It repairs every covered document's links to it and its own. It lists, and does
   not change, what names the old path elsewhere in any text file git lists, covered or not.
   It ends with the scan. After a move made by hand: `--moved <old> <new>`. To point every
   link whose text is a document's id at that document: `--ids`. The skill `/const-referencing:referencing` carries the procedure.
7. Output log: everything the gate and the mover print is also appended, one JSON line per print
   (timestamp, module, gate, mode, session, stream, text), to `const-referencing.jsonl`. The log is kept since
   blocked writes and reports after a write leave no trace in git. By default it lives
   in the platform's per-plugin data directory. Set `log_dir` to keep it inside the repository.
   The directory must be git-ignored, and the gate refuses to run otherwise.
8. Optional, the fixtures: the install holds no tests. So run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`). The command is `python3 -m pytest <kit clone>/modules/const-referencing/tests -p no:cacheprovider`, and all are green.
9. CLAUDE.md line: none. The rule about chat arrives through the session-start hook. The skill
   is named by a pointer line of 209 characters printed at session start. The same line names it at the
   start of every subagent. The line after the count line of every red of the gate names it too.

This module does not check remote links, since the check is offline. It does not check links inside code, or links
a template or a script assembles. It does not check whether a path link should have been an id link. It does not check anchors
inside files that are not covered Markdown, or the rest of a document's YAML block. It does not check chat
replies themselves: the two sentences shape them, and nothing inspects them.

Uninstall: remove the plugin; remove the `const-referencing:` namespace from
`constitution.yaml`. Documents keep their links and anchors.
