# Install — const-styling

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported by the scan with the fix on its first line; nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v1.0.0#subdirectory=shared"
```
A line that starts `BROKEN: const-styling needs the Python package constitution-layer-kit` (`C15`),
`BROKEN: const-styling needs constitution-layer-kit` (`C16`) or
`BROKEN: const-styling was written for constitution-layer-kit` (`C17`) points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). One skill, one scan, and two advisory hooks that name the skill. The skill, `style-defaults`, is offered to the model
   before a diagram, a table, a formula, a heading below level three, a callout, a fenced block or a
   template is written, and reads the project's style guide. The scan reads the covered Markdown
   files for twelve traces of the defaults and reports each that no departure allows.
2. **The style guide.** Create the project's guide from `skills/style-defaults/style-guide.md`:
   fill its envelope, put it with the project's documents, and name its path in
   `const-styling.guides`. It carries the founding defaults — Mermaid for diagrams, character
   drawings for trivial cases only, pseudocode over formulas, prose against lists against tables,
   list format, table format, heading levels, code font and fence languages, emphasis, no
   callouts — each defined by examples. A project whose documents are governed by policies gives
   the guide a policy of its own first, has its root policy ask every policy for a style rule,
   and has each kind's policy carry one, binding that kind's documents to the guide. Where module `const-locations` is installed and the
   guide's territory is a directory, name the shipped file as the template of the guide's policy in
   `const-locations.templates` and create the guide through its command; a territory of one path
   is created by hand, once.
3. **Zero configuration works** in a repository that has a `constitution.yaml` with no key of this
   namespace: the scan covers every Markdown file git lists, allows no departure, and reports the
   twelve traces; the skill falls back to the shipped guide. Without that file every scan is a
   visible skip naming it; an empty mapping, `{}`, is enough.
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
     # log_dir: .gate-logs     # optional, and the directory must be git-ignored; see step 7
   ```
   The signature keys: `plantuml` (a `plantuml` or `puml` fence, or a line opening with
   `@startuml`), `formula` (a `math`, `latex` or `tex` fence, or a line opening with `$$`),
   `callout` (a blockquote line opening with `[!`), `deep-heading` (level four or deeper),
   `skipped-level` (a heading more than one level below the one before it), `second-h1`,
   `fence-language` (a fence naming none), `list-marker` (a bullet opening with `*` or `+`),
   `list-numbering` (an ordered item that is not the one before it plus one), `underscore-emphasis`,
   `table-columns` (a row with more or fewer cells than the header, the delimiter row included),
   `table-empty-cell`. An entry needs all three fields, and a `reason` that is empty, a key the scan
   does not know, or a key of this namespace that is none of the four above is refused with exit 1
   — a misspelt dial is never a setting ignored in silence. An entry whose paths match no covered
   document is reported as a note on every scan until it is removed.
5. **Run the scan in CI and before a merge**, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-style.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. Adoption onto a repository with many
   findings: fix them, or declare the departures for the kinds that keep their form, one entry
   each with its reason; there is no warn mode, since the scan blocks no write.
6. **A departure is declared, never marked.** Nothing is written into a document to excuse it;
   the entry in the dials file is the record, and the reason is required. The scan holds the
   shipped values of three defaults: three heading levels at most, the dash for a bullet, the
   asterisk for emphasis. If your guide changes one of them, declare a departure for that
   signature over your whole tree, with the reason naming the guide's entry. The scan then stops
   checking that signature and does not check your new value; the guide's entry and review hold
   it.
7. Output log: everything the scan prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-styling.jsonl`. By default it lives in
   the platform's per-plugin data directory. Set `log_dir` to keep it inside the repository; the
   directory must be git-ignored, and the scan refuses to run otherwise.
8. Optional, the fixtures: the install holds no tests, so run them from a clone of the kit at the commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`), `python3 -m pytest <kit clone>/modules/const-styling/tests -p no:cacheprovider` — all green.
9. CLAUDE.md pointer: none. The skill is named by a pointer line of 196 characters, advisory, that the
   plugin prints at session start and gives to every subagent at its start, and by the last line of
   every red of the scan; the defaults ride on the skill and the traces on the scan. The scan itself
   runs no hook.

What this module does not check: whether prose, a list or a table was the right form; whether a
drawing is trivial; whether a key column is first or a heading is in sentence case; a callout
written as a blockquote with a bold word instead of the alert syntax. Nor does the module check:
an emphasis marker inside a link's text or a heading; a heading, an item or a fence indented four
spaces or more outside a list; a table whose header is not followed by a delimiter row, which is
not a table; a fence that is never closed, which hides everything after it; a document outside
`territories`.

Uninstall: remove the plugin; remove the `const-styling:` namespace from `constitution.yaml`; the
style guide stays, since it is the project's document.
