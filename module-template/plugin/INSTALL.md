# Install — const-<aspect-name>

For a module with a Python entry file, keep this block and write the version; for a module with none, delete it.
The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v<version>#subdirectory=shared"
```
A line that starts `BROKEN: const-<aspect-name> needs the Python package constitution-layer-kit`,
`BROKEN: const-<aspect-name> needs constitution-layer-kit` or
`BROKEN: const-<aspect-name> was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace or `--plugin-dir`).
2. Optional calibration: add a `const-<aspect-name>:` namespace to the project's `constitution.yaml`. Defaults apply otherwise — the module works in a repository whose `constitution.yaml` names `module_prefix`.
3. CLAUDE.md pointer (only if MODULE.md declares one, max one line):
   `<the line, or delete this section>`

Uninstall: remove the plugin; remove the namespace from `constitution.yaml`; remove the pointer line.
