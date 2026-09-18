# Install — const-meta-types

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing one is reported on the
first Markdown write, with the fix on the first line; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). The hook fires on every `Write` and `Edit`; it examines Markdown files inside
   the territories declared in the repository's `constitution.yaml` and nothing else.
2. Optional calibration in the project's `constitution.yaml`; defaults apply otherwise —
   the module works with zero configuration (with no `constitution.yaml`, or no
   `root_policy` in it, nothing is claimed and nothing is checked):
   ```yaml
   const-meta-types:
     severity: block      # block (default) | warn — warn reports the finding and lets the write through
     log_dir: <a git-ignored directory>   # optional; see step 4
   ```
3. Backstop for writes the hook cannot see (shell edits, other tools, other people): run the
   scan on demand and in CI:
   ```bash
   sh <plugin root>/scripts/check-governed-document.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`.
4. Output log: every line the gate prints is also appended, as one JSON line (timestamp,
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
