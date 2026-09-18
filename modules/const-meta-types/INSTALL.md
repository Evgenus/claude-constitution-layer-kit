# Install — const-meta-types

Requires: git, Python 3, PyYAML (`python3 -m pip install pyyaml`). A missing one is reported
on the first Markdown write, with the install command; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). The hook fires on every `Write` and `Edit`; it examines Markdown files inside
   the territories declared in the repository's `constitution.yaml` and nothing else.
2. Optional calibration in the project's `constitution.yaml`; defaults apply otherwise —
   the module works with zero configuration (with no `constitution.yaml`, or no
   `root_policy` in it, nothing is claimed and nothing is checked):
   ```yaml
   const-meta-types:
     severity: block   # block (default) | warn — warn reports the finding and lets the write through
   ```
3. Backstop for writes the hook cannot see (shell edits, other tools, other people): run the
   scan on demand and in CI:
   ```bash
   python3 <plugin root>/scripts/check-governed-document.py --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`.
4. CLAUDE.md pointer: none. The skill `/const-meta-types:choose-meta-type` loads on its own
   when Markdown documents are being created or classified.

Uninstall: remove the plugin; remove the `const-meta-types:` namespace from
`constitution.yaml` if present.
