# Install — const-meta-types

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing one is reported on the
first `Write` or `Edit` of any file, with the fix on the first line; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). The hook fires on every `Write` and `Edit`; it examines Markdown files inside
   the territories declared in the repository's `constitution.yaml` and nothing else.
   A copy of this plugin's folder made outside the repository it comes from must follow links
   (`cp -RL`): `scripts/const_gate`, and `const_gate`, `harness.py`, `consumer.py` and `shared_items.py` in `tests/`, are
   links to code the plugin shares with its siblings, and an install from the marketplace copies
   what they point at; `tests/meta_types_gate` is a link to this plugin's own `scripts/meta_types_gate`, which an install from the marketplace keeps as a link. A checkout made without symlink support leaves one-line text files in
   their place (`git config core.symlinks true`, then check out again). A plugin without it says so on
   the first `Write` or `Edit` and checks nothing until repaired.
2. Optional calibration in the project's `constitution.yaml`; defaults apply otherwise —
   the module works with zero configuration (with no `constitution.yaml`, or no
   `root_policy` in it, nothing is claimed and nothing is checked):
   ```yaml
   const-meta-types:
     severity: block      # block (default) | warn — warn reports the finding and lets the write through
     # log_dir: .gate-logs   # optional, and the directory must be git-ignored; see step 4
   ```
3. Backstop for writes the hook cannot see (shell edits, other tools, other people): run the
   scan on demand and in CI:
   ```bash
   sh <plugin root>/scripts/check-governed-document.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`.
4. Output log: everything the gate prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-meta-types.jsonl` — blocked writes,
   warnings and configuration failures leave no trace in git, so this is where they
   survive. By default it lives in the platform's per-plugin data directory, outside the
   repository. Set `log_dir` to keep it inside the repository instead; the directory must
   be git-ignored, and the gate refuses to run otherwise. The log rotates at 1 MiB.
5. Verify the install: `python3 <plugin root>/tests/run.py` — every item green.
6. CLAUDE.md pointer: none. The skill `/const-meta-types:choose-meta-type` loads on its own
   when Markdown documents are being created or classified.

Uninstall: remove the plugin; remove the `const-meta-types:` namespace from
`constitution.yaml` if present.
