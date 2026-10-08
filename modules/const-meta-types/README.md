# const-meta-types

<a id="a1"></a>
## What it gives you

Write-time guard of claimed territory: every Markdown document there carries the envelope (id, type, title, status) and resolves to exactly one governing policy. Plus a skill for choosing the meta-type.

<a id="a2"></a>
## Why use it

A session opens an old research note, or a page about a design the project has since changed. It treats the page as the truth, because nothing on the page says what it is. Another document sits in a folder that two rule sets claim, or in one that none claims. The rules that apply to it are whatever the reader assumes. Nobody notices at the write. Every such document raises the cost of the repair that comes later.

<a id="a3"></a>
## How Claude behaves with it

The project's `constitution.yaml` names a root policy and the folders each policy governs, its territory. A session that writes or edits a Markdown file inside a territory must give the file a short block at its top, the envelope. The block holds an `id`, a `type`, a `title` and a `status`. The type is one of three: `current-state` for how things are, `task-record` for where they should go, `non-authoritative` for a page that binds nothing. The write is refused when the block is missing or wrong, when the id is already taken, or when two policies claim the path. The refusal says what failed, why the rule exists, and the exact fix. The session makes the fix and writes again; nobody has to explain the rule. A file outside every territory is not examined, and the session is told so.

```text
RED: docs/notes/plan.md: no frontmatter envelope
  why: a governed document declares its authority in its envelope, or sessions guess it
  fix: start the file with a YAML block between two '---' lines carrying at least id: <kebab-id>, type: current-state | task-record | non-authoritative, title: <one line>, status: active | inactive — the fields every governed document carries; its kind may add fields of its own
```

The skill `choose-meta-type` loads on its own when a document is being created or sorted. It helps the session pick one of the three types from examples. It also helps split a page that mixes how things are with where they should go.

<a id="a4"></a>
## How it works

**Before a write.** A hook runs before every `Write` and `Edit` of the platform's file tools. It reads the file as it would be after the write and finds the policy whose territory holds the path. It checks the four fields, and that no other file in the tree carries the same id. Then it lets the write through or refuses it with the message above. It sees only writes made through the file tools. A file written by a shell command, a script or another person passes it unseen, which is what the scan is for.

**The scan.** The same check over every Markdown file git lists, run from the command line. It reports every finding and exits with code 2 when there is one. It says how many documents it examined, so a scan of nothing is never read as green. Run it in CI and before a merge.

**The skill.** A procedure in prose, loaded when the activity occurs. Nothing in it blocks a write.

**Settings.** The module works with no configuration of its own. It reads the project's `constitution.yaml` for the root policy and the territories, which every module of the kit shares, and nothing else. Two dials can be tuned under its own name there. One sets how loud a finding is: refuse the write, or report it and let the write through. The second is the path for a repository full of old documents. The other names where the module keeps its log of everything it printed. With no `constitution.yaml`, or no root policy in it, nothing is claimed and nothing is checked, and the module says so.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-meta-types@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-governed-document.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
