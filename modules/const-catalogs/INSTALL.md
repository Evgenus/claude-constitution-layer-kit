# Install — const-catalogs

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing `python3` or library is
reported at session start and on the first `Write` or `Edit` of any file, a missing git on the first
one of a Markdown file, each with the fix on the first line; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). Two hooks. At every session start — startup, resume, clear, compaction, fork — the
   plugin prints one line into the model's context while `catalogs` lists nothing, saying so (the
   transcript does not show it), and nothing once a catalog is listed. The write-time hook fires on
   every `Write` and `Edit`; it examines Markdown files in a listed catalog's territory and nothing else.
   A copy of this plugin's folder made outside the repository it comes from must follow links
   (`cp -RL`): `scripts/const_gate`, and `const_gate`, `harness.py`, `consumer.py` and `shared_items.py` in `tests/`, are
   links to code the plugin shares with its siblings, and an install from the marketplace copies
   what they point at; `tests/catalogs_gate` is a link to this plugin's own `scripts/catalogs_gate`, which an install from the marketplace keeps as a link. A checkout made without symlink support leaves one-line text files in
   their place (`git config core.symlinks true`, then check out again). A plugin without it says so on
   the first `Write` or `Edit` and checks nothing until repaired.
2. **Switch the check on: list the catalogs.** A kind is numbered because an entry here says
   so. The module guesses none: until `catalogs` lists one, every run prints
   `0 documents examined` and says why. In the project's `constitution.yaml`:
   ```yaml
   const-catalogs:
     catalogs:
       - prefix: <short, lowercase letters and digits>   # sticky: an id never changes
         territory: ["<pattern of the paths where the kind lives>"]   # gitignore syntax
         width: 4         # digits in a number, 1 to 9; 4 when absent
     severity: block      # block (default) | warn — warn reports the finding and lets the write through
     # log_dir: .gate-logs   # optional, and the directory must be git-ignored; see step 5
   ```
   Nothing else is read: no policy, no `root_policy`. Where the kind also has a policy with
   the same territory, write the patterns once and use YAML's own alias, so the two cannot
   drift apart:
   ```yaml
   <id of the kind's policy>:
     territory: &<name> ["<pattern>"]
   const-catalogs:
     catalogs:
       - {prefix: <prefix>, territory: *<name>}
   ```
   Everything in a territory is an item: a README or an index there is blocked for its name.
   Take it out with a negated pattern — `"!<path of the file>"` after the pattern that holds it.
   That works for a file directly in the top directory of a territory written `"<dir>/**"` or
   `"<dir>/*"` — not `"<dir>/"`, which names the directory itself. For a file deeper down, the
   territory must match files, not directories — `"<dir>/**/*.md"` rather than `"<dir>/**"` —
   because git re-includes nothing under a directory a pattern has excluded.
3. Adopting a kind that already has documents: every one of them is renamed once, with every
   link to it — with `git mv`, which also works where the file system ignores case. Set
   `severity: warn` until that is done; the scan lists what is left, tells each document whose
   name shows a number to keep it, and names the other file where two show the same one. New
   items are numbered above every number a name shows, renamed yet or not. A dated legacy name
   under width 4 — `<prefix>-2026-09-22-<slug>` — already has the form and is an item numbered
   by its year; once committed, its year stays in the advice.
4. Backstop for what the hook cannot see — `git mv`, shell edits, other tools, other people,
   and two branches that took one number: run the scan on demand, and in CI on every pull
   request, where the checkout is the merge of both branches:
   ```bash
   sh <plugin root>/scripts/check-catalog-item.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`. Its last
   line names each catalog's highest number, and the highest in history where a deleted item
   went further; where history is incomplete — a shallow checkout — or could not be read, the
   line says so.
5. Output log: everything the gate prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-catalogs.jsonl` — blocked writes,
   warnings and configuration failures leave no trace in git, so this is where they survive.
   By default it lives in the platform's per-plugin data directory, outside the repository.
   Set `log_dir` to keep it inside the repository instead; the directory must be git-ignored,
   and the gate refuses to run otherwise. The log rotates at 1 MiB.
6. Verify the install: `python3 <plugin root>/tests/run.py` — every item green.
7. CLAUDE.md pointer: none. The skill `/const-catalogs:catalog-item` loads on its own when a
   numbered document is being created, renumbered, listed or cited.

What this module does not check: the rest of the envelope, which policy governs a document,
whether a number was skipped (a gap is legitimate), and a file that carries a catalog's prefix
outside its territory.

Uninstall: remove the plugin; remove the `const-catalogs:` namespace from `constitution.yaml`.
The files keep their names.
