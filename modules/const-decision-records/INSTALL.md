# Install — const-decision-records

Requires: git, Python 3.12 or newer as `python3`, and the libraries in `requirements.txt`
(`python3 -m pip install -r <plugin root>/requirements.txt`). A missing one is reported on the
first Markdown write, with the fix on the first line; nothing is silently skipped.

1. Install the plugin (marketplace, or `claude --plugin-dir <path to this module>` for a
   session). The hook fires on every `Write` and `Edit`; it examines Markdown files governed
   by a record policy and nothing else.
2. **Switch the check on: name the record policy.** A document is a decision record because
   a policy for decision records governs it. The module ships no policy and guesses none:
   until `record_policies` names one, every run prints `0 documents examined` and says why.
   In the project's `constitution.yaml`:
   ```yaml
   <id of your decision-record policy>:      # the policy's own namespace: where records live
     territory: ["<pattern>"]
   const-decision-records:
     record_policies: [<id of your decision-record policy>]
     severity: block      # block (default) | warn — warn reports the finding and lets the write through
     log_dir: <a git-ignored directory>   # optional; see step 5
   ```
   With no `constitution.yaml`, or no `root_policy` in it, nothing is claimed and nothing is
   checked.
3. Optional calibration read by the skills, not by the gate — the agent reads these keys as
   written, and nothing validates their shape:
   ```yaml
   const-decision-records:
     boundary_examples:             # the project's own routine / recorded pairs
       - routine: <a call that is cheap to revert here>
         recorded: <its neighbour that is not>
     deciders:                      # who may decide at each stakes level
       process: [<person or role>]
       product: [<person or role>]
       architecture: [<person or role>]
     note_trailer: <Trailer-Key>    # if routine notes carry a theme trailer in commit messages
   ```
4. Backstop for writes the hook cannot see (shell edits, other tools, other people): run the
   scan on demand and in CI:
   ```bash
   sh <plugin root>/scripts/check-decision-record.sh --scan
   ```
   Exit 0 green, 2 findings, 1 the checker could not run. The scan ignores `severity`.
5. Output log: every line the gate prints is also appended, as one JSON line (timestamp,
   module, gate, mode, session, stream, text), to `const-decision-records.jsonl` — blocked
   writes, warnings and configuration failures leave no trace in git, so this is where they
   survive. By default it lives in the platform's per-plugin data directory, outside the
   repository. Set `log_dir` to keep it inside the repository instead; the directory must
   be git-ignored, and the gate refuses to run otherwise. The log rotates at 1 MiB.
6. Verify the install: `python3 <plugin root>/tests/run.py` — every item green.
7. CLAUDE.md pointer: none. The skills `/const-decision-records:record-decision` and
   `/const-decision-records:promote-recurring-notes` load on their own when a ruling is
   being made or commit notes are being reviewed.

What this module does not check: the rest of the envelope (`id`, `title`, `status`) and
which policy governs a document. Install module `const-meta-types`, which guards the envelope, beside this
one; alone, this gate lets a record with a malformed `id` through.

Uninstall: remove the plugin; remove the `const-decision-records:` namespace from
`constitution.yaml` if present.
