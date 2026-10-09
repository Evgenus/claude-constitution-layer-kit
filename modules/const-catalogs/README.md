# const-catalogs

<a id="a1"></a>
## What it gives you

Numbered kinds: a catalogued document's file name and id are one name, `<prefix>-<nnnn>-<slug>`; a new item's number must be free, and no two items of a catalog share one. Catalogs are declared in this module's own dial. Plus a skill for taking a number, renumbering after a collision, listing and citing.

In plain words: a numbered document, such as a decision record, carries its number in its file name and in its id. The module checks both at the write, refuses a number already taken, and finds two items under one number in a scan. The skill says how to take the next number and what to do when two branches took the same one.

<a id="a2"></a>
## Why use it

People cite decisions, tasks and incidents by number, "see D41". The numbers live wherever they were first typed: a register file, a heading, a chat message. Then the register moves, or an entry is renumbered, split or deleted. Every citation of the old number now points at nothing, or at something else, and nobody can tell which. Each citation written under a loose scheme is one more to repair when the scheme breaks. A number should mean one document for good.

With the module installed, a number is taken once and kept. A new document in a numbered folder is refused until its name carries a number no other item holds, and its id matches. A refusal over the number names the next one to take, while the width can still write one. Two branches that took one number are caught by the scan before the merge. A citation by number then leads to one document, for as long as the project lives.

<a id="a3"></a>
## How Claude behaves with it

The project declares its numbered kinds in `constitution.yaml`: a prefix, the folders where the kind lives, and how many digits a number has. A session that writes a Markdown file in one of those folders must name it `<prefix>-<number>-<slug>.md`. The number has exactly that many digits, and the file's `id` equals the name without `.md`. A new file must take a number no other item carries. Otherwise the write is refused. The refusal names the next free number, while the width can still write one, so the session can take it and write again. While no catalog is declared, nothing is examined. The session is told so in one line at every session start.

```text
RED: docs/records/second.md: file name 'second' is not rec-<4 digits>-<kebab-slug>, the form of catalog 'rec', whose territory holds this file
  why: an item of a numbered kind is cited by its number, and a citation resolves only when the number stands in the file's name, in one form for the whole catalog
  fix: rename the file to rec-<number>-<slug>.md: the number it is already cited by, or, if it has none, one more than the highest the catalog has held — the scan's last line names it — written with exactly 4 digit(s), zero-padded; the slug is lowercase words and digits joined by '-'; then set id to that name without .md
```

The skill `catalog-item` loads on its own when a numbered document is created, renumbered, listed or cited. It teaches the rules the gate cannot hold. A new item takes one more than the highest number the catalog has ever held, deleted items included. A number is provisional until its branch lands on the main branch. At a collision between two branches, the item already on the main branch keeps its number and the other renumbers. A gap is never filled. A catalog is listed with a git command, never kept in a register file.

<a id="a4"></a>
## How it works

**Before a write.** A hook runs before every `Write` and `Edit` of the platform's file tools. For a Markdown file in a declared catalog's folders it checks the name's form and that the id equals the name. For a file that does not exist yet, it checks that the number is free in the working tree. For the advice about the next number it also reads the branch's history. So a number a deleted item once held is not handed out again. It cannot see a rename made with `git mv`, a file written by a shell command, or two branches that took one number before they met.

**At session start.** A hook prints one line into the session's context while no catalog is declared. The line says that no document is examined and which dial to write. Once a catalog is declared it prints nothing.

**The scan.** The same checks over every Markdown file git lists, plus the one only a whole tree shows: two items of one catalog under one number. That is where two branches that each took a number meet. It exits with code 2 on a finding. Its last line names each catalog's highest number, the one a new item counts on from. Run it in CI on every pull request, where both branches are in the tree.

**The skill.** A procedure in prose, loaded when the activity occurs. Nothing in it blocks a write.

**Settings.** The module works with no configuration beyond the one dial that switches it on, the list of catalogs. It reads no policy and nothing else of the dials file. A folder's patterns can be shared with the policy that governs the kind by a YAML alias, so the two never drift apart. A file in a catalog's folders that is no item, such as an index page, is taken out by a negated pattern. Two dials are every gate's: how loud a finding is, and where the log goes. The quieter setting reports the finding and lets the write through, the path for adopting a kind that already has documents.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-catalogs@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-catalog-item.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
