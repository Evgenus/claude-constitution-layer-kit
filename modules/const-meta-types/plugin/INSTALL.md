# Install — const-meta-types

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing one is reported on the
first `Write` or `Edit` of any file, with the fix on the first line; nothing is silently skipped.

The shared code is the Python package `constitution-layer-kit`, which brings PyYAML with it. A project
installs it once, for the `python3` its hooks run, at the tag of the highest `REQUIRES` among the entry files:
```bash
python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v2.1.0#subdirectory=shared"
```
A line that starts `BROKEN: const-meta-types needs the Python package constitution-layer-kit`,
`BROKEN: const-meta-types needs constitution-layer-kit` or
`BROKEN: const-meta-types was written for constitution-layer-kit` points here.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>/plugin` for a
   session). It brings four parts.
   - The gate: a hook that fires before every `Write` and `Edit`. It examines Markdown files inside
     the territories declared in the repository's `constitution.yaml` and nothing else. Every red of
     the gate carries, after its count line, a line naming the skill.
   - The pointer to the skill: a hook at session start prints one pointer line, 182 characters,
     advisory, naming the skill `/const-meta-types:choose-meta-type` and its moment. A hook at each
     subagent's start gives the same line to that subagent.
   - The pointer to the governing policy: the first write of a session that passes for a document of
     a policy adds one advisory line to the model's context, naming the policy's path and, where the
     policy has a rule named Enforcement, that rule's anchor — a rule written
     `<a id="<anchor>"></a>**Enforcement.**`, the full stop optional, the first such rule in the
     policy; a policy without one earns the path alone. Once per session, repository and policy,
     remembered in the memo of step 5. With no log location, or an event that names no session, there
     is no memo entry and nothing is pointed.
   - The skill `choose-meta-type`, which helps to pick the type of a document.
2. Optional calibration in the project's `constitution.yaml`; defaults apply otherwise —
   the module works with zero configuration (with no `constitution.yaml`, or no
   `root_policy` in one that names `module_prefix`, nothing is claimed and nothing is checked):
   ```yaml
   const-meta-types:
     severity: block      # block (default) | warn — warn reports the finding and lets the write through
     # log_dir: .gate-logs   # optional, and the directory must be git-ignored; see step 5
   ```
3. Adoption: on a repository with documents written before the module, set `severity: warn`. The
   gate then reports each finding and lets the write through, while the old documents are fixed;
   `block` is the default.
4. Backstop for writes the hook cannot see (shell edits, other tools, other people): run the
   scan on demand and in CI and before a merge, from anywhere in the repository:
   ```bash
   sh <plugin root>/scripts/check-governed-document.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`.
5. Output log: everything the gate prints is also appended, one JSON line per print (timestamp,
   module, gate, mode, session, stream, text), to `const-meta-types.jsonl` — blocked writes,
   warnings and configuration failures leave no trace in git, so this is where they
   survive. By default it lives in the platform's per-plugin data directory, outside the
   repository. Set `log_dir` to keep it inside the repository instead; the directory must
   be git-ignored, and the gate refuses to run otherwise. The log rotates at 1 MiB.
   Beside the log lives `const-meta-types.pointed`, the memo of the pointers above: one line per
   pointer, the session, the repository and the policy, its last 200 lines kept.
6. Optional, the fixtures: the install holds no tests, so run them from a clone of the kit at the
   commit the install records (`gitCommitSha` in the platform's `installed_plugins.json`),
   `python3 -m pytest <kit clone>/modules/const-meta-types/tests -p no:cacheprovider` — all green.
7. CLAUDE.md line: none. The session-start hook already names the skill in every session and
   every subagent, so no line in the project's `CLAUDE.md` is needed.

What this module does not check: a Markdown file written by a shell command, a script or
another person is seen only by the scan; a file outside every territory that declares no policy
is left alone; whether a document's type is the right one of the three, which the skill helps
with; whether a `policy:` declaration in an envelope is still needed; an id reused in the past, since only
the present files are compared.

Uninstall: remove the plugin; remove the `const-meta-types:` namespace from
`constitution.yaml` if present.
