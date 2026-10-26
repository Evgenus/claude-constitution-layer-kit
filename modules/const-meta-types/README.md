# const-meta-types

<a id="a1"></a>
## What it gives you

Write-time guard of claimed territory: every Markdown document there carries the envelope (id, type, title, status) and resolves to exactly one governing policy. Plus a skill for choosing the meta-type.

In plain words: a policy is a document that holds the rules for one kind of page, and the folders it governs are its territory. A territory that a policy claims is claimed territory. Every Markdown page there starts with a short block, the envelope, that says what the page is. The envelope holds an id, a type, a title and a status. The type, also called the meta-type, is one of three: how things are now, where things should go, or a page that binds nothing. The module checks the envelope at the moment the page is written, which is why it is called a write-time guard, and checks that exactly one policy governs the page. A skill helps pick the type.

<a id="a2"></a>
## Why use it

A session opens an old research note, or a page about a design the project has since changed. It treats the page as the truth, because nothing on the page says what it is. Another document sits in a folder that two rule sets claim. The rules that apply to it are whichever the reader assumes. Nobody notices at the write. Every such document raises the cost of the repair that comes later.

With the module installed, that cannot happen in silence. A page in a governed folder is refused at the write until its block says what the page is. A page that two policies claim is refused until it declares one of them, or the territories are fixed. A page outside every territory, declaring no policy, is outside the module. A reader can then trust what a page says about itself, and a session knows which rules apply before it edits.

<a id="a3"></a>
## How Claude behaves with it

The project's `constitution.yaml` names a root policy and the folders each policy governs, its territory. A session that writes or edits a Markdown file inside a territory must give the file a short block at its top, the envelope. The block holds an `id`, a `type`, a `title` and a `status`. The type is one of three: `current-state` for how things are, `task-record` for where they should go, `non-authoritative` for a page that binds nothing. The write is refused when the block is missing or wrong, when the id is already taken, or when two policies claim the path. The refusal says what failed, why the rule exists, and the exact fix. The session makes the fix and writes again; nobody has to explain the rule. A file outside every territory, declaring no policy, is not examined.

```text
RED: docs/notes/plan.md: no frontmatter envelope
  why: a governed document declares its authority in its envelope, or sessions guess it
  fix: start the file with a YAML block between two '---' lines carrying at least id: <kebab-id>, type: current-state | task-record | non-authoritative, title: <one line>, status: active | inactive — the fields every governed document carries; its kind may add fields of its own
```

The skill `choose-meta-type` is there for the moment a document is created or sorted. It helps the session pick one of the three types from examples. It also helps split a page that mixes how things are with where they should go.

<a id="a4"></a>
## How it works

**Before a write.** A hook runs before every `Write` and `Edit` of the platform's file tools. It reads the file as it would be after the write and finds the policy whose territory holds the path. It checks the four fields, and that no other file in the tree carries the same id. Then it lets the write through or refuses it with the message above. It sees only writes made through the file tools. A file written by a shell command, a script or another person passes it unseen, which is what the scan is for.

**The pointer to the policy.** The same hook, on a write that passes. The first time in a session that a write passes for a document of some policy, it adds one short line to what the model reads next. The line names the policy's file and, where the policy has a rule named Enforcement, that rule's place in the file. The session can then open the rules review will hold before it edits further. The line is advice and blocks nothing. It is said once per session for each repository and policy, which the module remembers in a small file beside its log.

**At session start.** A hook that runs when a session starts prints one short line that names the skill and the moment to load it: before a governed document is created or its type changed, and when a write is refused for its envelope. It reads nothing, checks nothing and blocks nothing.

**At a subagent's start.** A hook on the start of each subagent gives the same line to that subagent, which starts with a context of its own and would not otherwise know the skill is there.

**The scan.** The same check over every Markdown file git lists, run from the command line. It reports every finding and exits with code 2 when there is one. It says how many documents it examined, so a scan of nothing is never read as green. Run it in CI and before a merge.

**The skill.** A procedure in prose, loaded when the activity occurs. Nothing in it blocks a write. The module names its skill at session start, at the start of each subagent and after every refusal, so the session knows to load it. It also advises a run of the scan after a document was written by a shell command.

**Settings.** The module works with no configuration of its own. It reads the project's `constitution.yaml` for the root policy and the territories, which every module of the kit shares, and nothing else. Two dials can be tuned under its own name there. One sets how loud a finding is: refuse the write, or report the finding and let the write through. Reporting is the path for a repository full of old documents. The other names where the module keeps its log of everything it printed. With no `constitution.yaml`, or no root policy in it, nothing is claimed and nothing is checked, and the module says so.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace: `claude plugin install const-meta-types@claude-constitution-layer-kit --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-governed-document.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
