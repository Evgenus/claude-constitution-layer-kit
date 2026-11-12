# Install — const-styling

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported by the scan with the fix on its first line. Nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-styling needs the Python package constitution-layer-kit`,
`BROKEN: const-styling needs constitution-layer-kit` or
`BROKEN: const-styling was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). One skill, one scan, and two advisory hooks that name the skill. The skill, `style-defaults`, reads the project's style guide.
   The model is offered it before a diagram, a table, a formula or a heading below level three is
   written. It is also offered before a callout, a fenced block or a template is written. The scan reads the covered Markdown
   files for twelve traces of the defaults and reports each that no departure allows.
2. **The style guide,** when the project keeps one. A project that decided to keep none follows
   the shipped guide, as step 3 of this note says, and creates nothing. Create the project's guide from
   `skills/style-defaults/style-guide.md`.
   Fill its envelope, put it with the project's documents, and name its path in
   `const-styling.guides`. It carries the founding defaults, each defined by examples. They are Mermaid for
   diagrams, character drawings for trivial cases only, pseudocode over formulas, and prose against
   lists against tables. The rest are list format, table format, heading levels, code font and
   fence languages, emphasis, and no callouts. A project whose documents are governed by policies
   first gives the guide a policy of its own. Then it has its root policy ask every policy for a
   style rule. It also has each kind's policy carry one, binding that kind's documents to the guide. Where module `const-locations` is installed and the
   guide's territory is a directory, name the shipped file in `const-locations.templates` as the template of the
   guide's policy. Then create the guide through that module's command. A territory of one path
   is created by hand, once, with the session's file tools, so that the hooks see the write. A copy made in
   the shell passes no hook.
3. **Zero configuration works** in a repository whose `constitution.yaml` has `module_prefix`
   and no key of this namespace. There the scan covers every Markdown file git lists, allows no
   departure, and reports the twelve traces. The skill falls back to the shipped guide. Without
   that file every scan is a visible skip naming it. The line `module_prefix: const-` alone is
   enough.
4. Calibration, all optional, in the project's `constitution.yaml`:
   ```yaml
   const-styling:
     territories: ["*.md", "!docs/archive/**"]   # gitignore syntax; the documents the scan reads; default ["*.md"]
     guides: ["docs/style-guide.md"]              # the style guides, read by the skill; default none
     departures:                                  # what departs from a default, where, and why; default none
       - paths: ["docs/design/**"]                # a pattern for a kind of document, or one file by path
         allow: [plantuml]                        # the signature keys the scan passes there
         reason: sequence diagrams with timing, which Mermaid has no form for
       - paths: ["/docs/matrix.md"]
         allow: [table-empty-cell]
         reason: the group rows of the matrix hold nothing on purpose
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 6
   ```
   The signature keys are `plantuml` (a `plantuml` or `puml` fence, or a line opening with
   `@startuml`) and `formula` (a `math`, `latex` or `tex` fence, or a line opening with `$$`).
   Next are `callout` (a blockquote line opening with `[!`), `deep-heading` (level four or deeper)
   and `skipped-level` (a heading more than one level below the one before it). Then come
   `second-h1`, `fence-language` (a fence naming none) and `list-marker` (a bullet opening with `*`
   or `+`). Then comes `list-numbering`, an ordered item that is not the one before it plus one.
   The key `underscore-emphasis` follows it. Then comes `table-columns` (a row with more or fewer
   cells than the header, the delimiter row included). `table-empty-cell` is the last key. An
   entry needs all three fields. A `reason` that is empty is refused with exit 1. So is a key the
   scan does not know, and so is a key of this namespace that is none of the four above. A
   misspelt dial is never a setting ignored in silence. An entry whose paths match no covered
   document is reported as a note on every scan until it is removed.

   **A departure is declared, never marked.** Nothing is written into a document to excuse it.
   The entry in the dials file is the record, and the reason is required. The scan holds the
   shipped values of three defaults: three heading levels at most, the dash for a bullet, the
   asterisk for emphasis. If your guide changes one of them, declare a departure for that
   signature over your whole tree, with the reason naming the guide's entry. The scan then stops
   checking that signature and does not check your new value; the guide's entry and review hold
   it.
5. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-style.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. To adopt the scan on a repository with
   many findings, fix them, or declare the departures for the kinds that keep their form. Each
   departure is one entry with its reason. There is no warn mode, since the scan blocks no write.
6. Output log: the scan also appends everything it prints to `const-styling.jsonl`, one JSON line
   per print (timestamp, module, gate, mode, session, stream, text). By default it lives in
   the platform's per-plugin data directory. Set `log_dir` to keep it inside the repository. The
   directory must be git-ignored, and the scan refuses to run otherwise.
7. Optional, the fixtures: the install holds no tests. So run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`). The command `python3 -m pytest <kit clone>/modules/const-styling/tests -p no:cacheprovider` runs them, all green.
8. CLAUDE.md line: none. The skill is named by a pointer line of 196 characters, advisory, that the
   plugin prints at session start. The plugin also gives that line to every subagent at its start.
   The last line of every red of the scan names the skill too. The defaults ride on the skill and
   the traces on the scan. The scan itself
   runs no hook.

This module does not check whether prose, a list or a table was the right form. It does not
check whether a drawing is trivial, or whether a key column is first or a heading is in sentence
case. Nor does it check a callout written as a blockquote with a bold word instead of the alert
syntax. The module also does not check an emphasis marker inside a link's text or a heading. Nor
does it check a heading, an item or a fence indented four spaces or more outside a list. It does
not check a table whose header is not followed by a delimiter row, which is not a table. It does
not check a fence that is never closed, which hides everything after it. Nor does it check a
document that `territories` does not cover.

Uninstall: remove the plugin, and remove the `const-styling:` namespace from `constitution.yaml`.
The style guide stays, since it is the project's document.
