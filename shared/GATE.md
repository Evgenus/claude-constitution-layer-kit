---
id: kit-shared-gate-code
type: current-state
title: The code every gate shares — interface, messages, limits, acceptance items
status: active
---

# The code every gate shares

*One source for what every write-time gate of the kit must have: `const_gate/` for the gates, `tests/` for their fixtures. A module reaches both through relative symbolic links — `scripts/const_gate` and three files in its `tests/` — so the kit holds one copy to read, fix and review, and the platform copies what a link points at into an installed plugin (decision [dec-0025-shared-gate-code-linked](../docs/decisions/dec-0025-shared-gate-code-linked.md)). This page is the home of every shared text; a module's document writes out its own messages and links here for the rest. Every list and table row carries a handle.*

<a id="g1"></a>
## 1. What is shared, and why it may be

Code is admitted here only when it implements a kernel section literally (class K) or a gate-script rule of [template §6](../module-template/MODULE.md#t6) (class R), and two or more modules need it.

| part | class | carries |
|---|---|---|
| `identity` | R | which gate this process is — namespace, gate name, plugin root — declared once by the entry point; the only global of the package |
| `model` | K, R | the kernel's closed vocabularies (meta-type, status, severity, the file tools), the typed structures that cross function boundaries, `Finding` and `Broken`, the keys of the shared configuration failures, the exit codes |
| `messages` | R | every shared text of [§3](#g3), as typed functions under their keys |
| `errors`, `preflight`, `cli` | R | the configuration-failure exception; the import check of each declared library; `argparse` with its exit 2 turned into 1, the single guard, no fail-open |
| `output` | R | every printed line also appended to a log, on the standard library's `logging` |
| `repository`, `territory` | K | git for the root and the file list; territory patterns evaluated by `git check-ignore` in a fresh null repository ([kernel §6](../kernel/CONVENTIONS.md#k6)) |
| `envelope` | K | the frontmatter block parsed once, every field kept as YAML read it ([kernel §1](../kernel/CONVENTIONS.md#k1)); which fields matter is the module's |
| `dials` | K | the dials file read and validated for the keys every gate reads: the two kernel-owned keys, `territory` of every policy namespace, `severity`, `log_dir`; the rest of the module's namespace handed over as read ([kernel §6](../kernel/CONVENTIONS.md#k6)) |
| `events` | R | the hook payload parsed into a typed event; the document as it will be after a `Write` or an `Edit` |
| `index`, `resolution` | K | the policies found in the root policy's territory and what each claims; which policy governs a document, path first, as a typed result with no message ([kernel §3](../kernel/CONVENTIONS.md#k3)) |
| `pipeline` | R | from the event, or the scan's directory, to the repository and its dials; from findings to the verdict the platform understands — block, warn as one JSON object, scan |
| `tests/harness`, `tests/consumer`, `tests/shared_items` | R | the case runner driving a module's real entry point; the throwaway three-policy consumer; the acceptance items of [§5](#g5) |

<a id="g2"></a>
## 2. The interface a module fills

1. **Identity.** The module's `start` builds one `Identity` and calls `cli.run(argv, identity, load_modes)`. The shared code never imports a module.
2. **Two modes.** `load_modes` returns the module's `hook` and `scan` functions; it is called after the preflight, because the module's code needs the declared libraries.
3. **The middle of a run is the module's.** A mode calls `pipeline.locate_write` or `pipeline.locate_scan`, which returns a target or a `Skip`; builds the index; examines documents with its own checks; and hands findings and notes to `pipeline.report_hook`, `report_scan`, `green_hook` or `skip`. Nothing in the pipeline calls back into the module.
4. **Own dials.** `Dials.own` is the module's namespace as YAML read it; the module parses it once into its own dataclass and raises the shared `ConfigurationFailure` with its own `C5` text when it is malformed.
5. **Own messages.** A module's findings, skip reasons, notes and dial failures live in the module's `messages`, written like the shared ones; its finding keys are its own enum.
6. **The entry file.** Parseable by any Python 3: the interpreter floor, then `import const_gate` guarded by the designed message `C15` of [§3](#g3), then the module's `start`.
7. **Links.** `scripts/const_gate` → `shared/const_gate`; `tests/harness.py`, `tests/consumer.py`, `tests/shared_items.py` → their sources in `shared/tests/`; all relative. The kit gate is `scripts/check-shared-links.py`: red for a copy, a plain file, a dangling, absolute or misdirected link; `--self-test` is its red→green fixture.

<a id="g3"></a>
## 3. Shared messages

Each row is one function of `const_gate/messages.py` under the same key, word for word; `{module}` is the namespace the entry point declared, other `{…}` are parameters. A configuration failure is one self-sufficient line — in hook mode only the first stderr line reaches the user — followed by the count line `C11`.

| key | text |
|---|---|
| G1 | `GREEN: {module}: 1 document examined, governed by {policy id}` / `GREEN: {module}: 0 documents examined — {reason}` / scan: `GREEN: {module}: {the module's count tail}` |
| G1.1 | reason: `tool '{t}' carries no file to examine` |
| G1.2 | reason: `{path} is not a Markdown document` |
| G1.3 | reason: `{path} is not inside a git repository; the constitution is silent there` |
| G1.4 | reason: `no constitution.yaml in {root}: nothing is claimed` |
| G1.5 | reason: `constitution.yaml has no root_policy: nothing is claimed` |
| G1.6 | reason: `the Edit cannot be applied to {path}; the tool will report it` |
| F9 | count: `RED: {n} finding(s) — 1 document examined ({path})` (hook) / `RED: {n} finding(s) — {the module's count tail}` (scan) |
| W1 | `severity: warn`: exit 0 with one JSON object on stdout and nothing else — `hookSpecificOutput.additionalContext` = any notes, the `RED` lines, the count line, and `{module}: severity is warn: the write proceeds, but the finding stands and recurs on every write until fixed`; `systemMessage` = `{module} (warn): {headline of the first finding}` |
| N1.1 | `note: {path} lies in the root policy's territory but carries no readable id; it claims nothing until it does` |
| N1.2 | `note: {a} and {b} both carry id '{id}'; the first claims, the second is ignored` |
| P1 | field-level parts of a module's finding: `{field} missing`; `{field} must be a quoted string (YAML read it as {yaml type})` |
| C1 | `BROKEN: {module} needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/) — until then Markdown writes pass unchecked` (printed by the module's POSIX entry point; no Python runs to print it) |
| C2 | `BROKEN: {module} needs {distribution} — fix: run: python3 -m pip install -r {the plugin's requirements.txt} — until then Markdown writes pass unchecked` |
| C3 | `BROKEN: {module} needs git on PATH — fix: install git (https://git-scm.com/downloads)` |
| C4 | `BROKEN: constitution.yaml is not valid YAML ({the parser's message, on one line}) — fix: fix the file; nothing is checked until it parses` |
| C4b | `BROKEN: constitution.yaml is not a mapping — fix: the file holds top-level keys: root_policy, then one namespace per policy or module` |
| C5.1 | `BROKEN: constitution.yaml: root_policy must be a repository-relative path — fix: root_policy: <path of the root policy, relative to the repository root>` |
| C5.2 | `BROKEN: constitution.yaml: territory_dialect must be a non-empty string — fix: remove the key (default gitignore) or name a dialect` |
| C5.3 | `BROKEN: constitution.yaml: territory_dialect '{d}' is not supported by {module} (supports: gitignore) — fix: set territory_dialect: gitignore, or remove the key` |
| C5.4 | `BROKEN: constitution.yaml: namespace '{k}' must be a mapping — fix: write it as {k}: {territory: [...]}` |
| C5.5 | `BROKEN: constitution.yaml: namespace '{module}' must be a mapping of this module's dials — fix: write this module's dials under it as a mapping, or remove the key` |
| C5.6 | `BROKEN: constitution.yaml: {k}.territory must be a list of non-empty strings — fix: write it as {k}: {territory: ["<pattern>", ...]}` |
| C5.7 | `BROKEN: constitution.yaml: {k}.territory holds a pattern git would not read as one: '{pattern}' — fix: a pattern may not start with '#' (a comment to git) nor contain a line break; escape or remove it` |
| C5.8 | `BROKEN: constitution.yaml: {module}.severity must be block or warn — fix: under {module}, set severity: block or severity: warn, or remove that line` |
| C5.9 | `BROKEN: constitution.yaml: {module}.log_dir must be a repository-relative directory — fix: under {module}, set log_dir: <a git-ignored directory>, or remove that line` |
| C6 | `BROKEN: constitution.yaml names root_policy '{path}' but no such file exists — fix: create it, or point root_policy at the policy for policies` |
| C7 | `BROKEN: root policy '{path}' carries no readable id in its envelope — fix: give it the envelope (id, type, title, status); its id names its namespace` |
| C8 | `BROKEN: root policy '{id}' claims no territory in constitution.yaml — fix: write {id}: {territory: [<where policies live, including the root itself>]} — nothing is governed until then` |
| C9 | `BROKEN: root policy '{path}' lies outside its own territory [{patterns}] — fix: every chain of governance ends at the root; widen {id}.territory to include it` |
| C11 | count: `BROKEN: the check could not run — 0 documents examined` |
| C12.1 | `BROKEN: git ls-files failed in {root} — fix: run the check from inside a git repository` |
| C12.2 | `BROKEN: git init of the scratch repository failed — fix: check that git works: git --version` |
| C12.3 | `BROKEN: git check-ignore failed: {stderr} — fix: territory patterns must be gitignore syntax; check constitution.yaml` |
| C12.4 | `BROKEN: hook input cannot be used ({detail}) — fix: this script reads one PreToolUse event, a JSON object, on stdin` — detail one of `it is not JSON: {the parser's message}`, `it is JSON, but the top level is not an object`, `a {tool} event must carry a string tool_input.{field}` |
| C12.5 | `BROKEN: git could not answer where the repository is: {git's first line} — fix: repair the git setup named in the message (configuration, ownership, installation)` |
| C12.6 | `BROKEN: {path} does not exist — fix: pass --scan an existing directory, or none for the current one` |
| C12.7 | `BROKEN: constitution.yaml cannot be read ({error}) — fix: check the file's permissions` |
| C12.8 | `BROKEN: {dir} is not inside a git repository — fix: run --scan from a repository, or pass its path` |
| C12.9 | `BROKEN: misinvocation: {argparse message} — fix: run with no arguments (hook) or --scan [<dir>]` |
| C12.10 | `BROKEN: {path} is listed by git but cannot be read — fix: check the file's permissions and encoding` |
| C12.11 | `BROKEN: unexpected failure inside the checker: {exception} — fix: this is a defect of the gate, not of the repository; report it with the traceback below` (the line first, the traceback after it) |
| C13 | `BROKEN: constitution.yaml: {module}.log_dir '{dir}' is not ignored by git — fix: a log inside the working tree must be git-ignored, or every verdict dirties the tree; add the directory to .gitignore, or remove the key` |
| C14 | `BROKEN: {module} needs Python 3.12 or newer, found {major}.{minor} — fix: install a current Python 3 (https://www.python.org/downloads/) and put it first on PATH — until then Markdown writes pass unchecked` (printed by the module's Python entry file, which any Python 3 can parse; its text lives there) |
| C15 | `BROKEN: {module} is installed without its shared code (scripts/const_gate is missing or is not a directory) — fix: install the plugin from its marketplace, or load it from a full checkout of the repository it comes from; a copy of the plugin's folder must be made with links followed (cp -RL) — until then Markdown writes pass unchecked` (printed by the module's Python entry file, for the same reason as C14) |

An envelope that is YAML but no mapping is reported by the module with the shared detail `the block is not a mapping of field: value`; a YAML error is the parser's whole message on one line, so the line and the column survive.

<a id="g4"></a>
## 4. Shared honest limits

Every module that links this code has these limits and states its own beside them.

1. **Shell writes and other actors.** A heredoc, `sed -i`, a human's editor, a merge, another server's file tool: none is a `Write` or `Edit`, and the hook never sees it. Backstop: the module's scan, on demand and in CI.
2. **A configuration failure, a timeout, and a hook that cannot start are non-blocking in hook mode.** Exit 1 shows the user the first stderr line and the write proceeds; the platform treats a hook past its timeout, or one whose script is missing, the same way. Backstop: the scan exits 1 with the same line, so CI turns red; the line lands in the output log.
3. **The link to this code may be dropped by an install.** The platform documents that a link leading outside a plugin is copied into a marketplace install, and skipped when a plugin is loaded from a local path in copy mode; on Claude Code 2.1.251 a plugin loaded with `--plugin-dir` runs in place and the link resolves (observed 2026-09-19). Backstop: `C15` — loud, exit 1, the same class as a missing library — with an absence fixture in every module; the kit gate on the links; `cp -RL` for a copy of a module's folder.
4. **`Edit` is reconstructed, not observed.** The edit is applied to the file on disk and the result judged; an absent `old_string` is a visible skip; an `old_string` occurring twice without `replace_all` is judged on its first occurrence though the tool will refuse the edit; an `Edit` of a missing file with an empty `old_string` is judged on what it creates. Backstop: the tool's own refusal comes after the hook, and the next real write is judged again.
5. **Symbolic links in the consumer.** The written path is resolved before it is matched, so a territory that names only a link does not claim what is written through it. Backstop: territories over real paths; the scan lists files under the paths git records.
6. **A key given twice in an envelope.** YAML keeps the last one. Backstop: review.
7. **Markdown means `.md`; git-ignored files are invisible to the scan,** which lists tracked files and untracked ones git does not ignore; a tracked file deleted from the working tree is left out. Backstop: the hook still judges such a file when it is written through the file tools.
8. **The envelope ends at the first line holding only `---`**; a block scalar containing such a line truncates it. Backstop: the module reports the truncated envelope as invalid.
9. **Patterns match case-sensitively on every platform,** so one repository gets one verdict everywhere. Backstop: the scan sees a file under the case git records.
10. **The output log is best-effort evidence, not a gate.** A logging failure never changes a verdict; `C1`, `C14` and `C15` are printed and not logged, since no shared code runs to log them. Backstop: stdout and stderr remain the record.
11. **No `--help`,** and no abbreviated flags: `argparse`'s own help exits past the guard and the log. Backstop: any unknown argument is a misinvocation whose fix line is the usage.
12. **With two gates installed, the model sees one block message at a time** when both exit 2 (observed on Claude Code 2.1.251, 2026-09-19; the documentation is silent). Backstop: the next write is judged again; both findings are in the output logs.

<a id="g5"></a>
## 5. Shared acceptance items

`tests/shared_items.py`, run by each module's runner through that module's real entry point, numbered from 101 there. A module hands over one write its gate passes and one it blocks.

| item | what it proves |
|---|---|
| S101–S110 | the exit-code split, each exit 1 with its line first on stderr: a malformed dials file; `C4b`; `C5.8`; `C5.5`; `C5.7`; `C5.3`; `C6`; `C7`; `C8`; `C9` |
| S111–S116 | absence: `python3`; an interpreter below the floor (reported as not exercised, with a zero count, where the machine has none); git; a declared library; the shared code itself (`C15`); and a git that fails for another reason is a configuration failure, never a green skip |
| S117–S124 | invocation and input: a misinvocation, `--help` and an abbreviated flag exit 1; input that is not JSON, JSON that is no object, and a `Write` event without its fields exit 1 and say which; another tool's event is a visible skip; `--scan` on a missing path exits 1 |
| S125–S130 | paths and skips, each a visible zero or a verdict: a non-Markdown file; a relative `file_path` resolved against `cwd`; a file outside any repository; no dials file; no `root_policy`; an `Edit` whose `old_string` is absent |
| S131 | `severity: warn`: exit 0 with the whole finding in `additionalContext` and `systemMessage` |
| S132–S136 | the output log: seven fields per line under the module's name; `log_dir` routes the whole run to a git-ignored directory; a `log_dir` git does not ignore is `C13`; rotation; a logging failure never changes the verdict |
| S137 | `requirements.txt` equals the preflight table |
| S138 | kit check: `scripts/check-shared-links.py --self-test` — the right link green; a copy, a plain file, a dangling link, a misdirected link and an absolute link each red |
