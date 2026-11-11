# const-referencing

<a id="a1"></a>
## What it gives you

It gives references a machine can follow and a move can repair. It gives one written form per kind of reference, and anchors that do not depend on a heading's words. It gives a check of the whole tree after every write and in the scan. It gives a mover that repairs the links a move breaks. Plus a skill for citing, anchoring and moving, and two always-on sentences about references in chat.

In plain words: a reference is any place where one document points at another. A reference a machine can follow is a link with a target that exists. A written form is the one way the project writes that kind of reference. An anchor is a fixed name placed at a cited place in a document, so a link can name that place. It survives a reworded heading, which a heading's own generated name does not. The module checks links before and after a write. The scan is the same check over every Markdown file in the repository, run by hand or in CI. The whole tree is that set of files. The mover is a command that moves a document with git and repairs every link to it. The skill is a procedure the session loads when it writes a link, adds a cited section or moves a document. The two always-on sentences are printed at every session start and ask for the same in chat.

<a id="a2"></a>
## Why use it

A document is moved, a heading is reworded or a page is deleted. Every link that pointed there still reads as a link. But it leads nowhere, or to a neighbour that carries the old heading's words. Nobody notices at the edit, because the break is in other files, and a reader finds it weeks later. Beside it stands the reference that never was one. Such a reference is a bare "see section 4", an id in backticks or a path that exists only on the author's machine. No tool can follow it and a rename cannot find it.

With the module installed, a bad reference form is refused at the write, and a link that leads nowhere is reported right after it. A document is moved by the mover, which repairs every link to it. The scan in CI turns red on any link or anchor that does not resolve, so a broken reference never reaches the main branch.

<a id="a3"></a>
## How Claude behaves with it

Before a session writes or edits a Markdown file, the forms of its references are checked, and a bad form refuses the write. One bad form is a document's id in backticks where a link is due. Another is a link whose text is one document's id but which opens another. A third is a path into someone's home folder. The last is any bare form the project lists as a lane. One example: a requirement number that must be a link outside its home document. After the write, the whole tree is checked. It finds a link to a file that does not exist, and an anchor that does not exist. It also finds a link that resolves only through a heading's generated name. These are reported to the session, since the write has already happened. The scan is where they turn red.

```text
RED: docs/notes/refs.md:3: document id 'plc-notes' stands in backticks and is no link
  why: an id names a document that can move: only a link lets a reader reach it and lets a move repair it
  fix: write [plc-notes](../policies/plc-notes.md) — the path from this document to docs/policies/plc-notes.md
```

At every session start, two sentences are added to the session's context. In chat, every reference to a file, a section or a document is a markdown link. A number or a key is a handle local to its message, and it is named with its source when a cite crosses that boundary. The skill `referencing` teaches the forms when links are written, when a section others will cite is added, and when a document is moved. It has the session move a document with the module's mover, never by hand.

<a id="a4"></a>
## How it works

**Before a write.** A hook runs before every `Write` and `Edit` of a Markdown file. It reads the file as it would be after the write and checks the forms above. A finding refuses the write. It needs no network and no other tool.

**After a write.** A second hook runs after the write. It asks the link checker, the `lychee` tool, whether every link and anchor of the written file resolves. A break is reported to the session but cannot block, since the file is already written. Without `lychee` on the machine, the forms are still checked, and every write says that resolution was not.

**At session start.** A hook adds two things to the session's context: two sentences about references in chat, and a line that names the skill. It reads nothing and checks nothing, and a failure of it only prints nothing. It also runs again after a compaction or a clear.

**At a subagent's start.** A second hook gives the same line that names the skill to every subagent. A subagent starts with a context of its own and would not see the session's.

**The scan.** Both checks over every Markdown file git lists, plus one more. An id named in a script or a configuration file, where no link checker looks, must be the id of a document that exists. The scan exits with code 2 on a finding. Run it in CI on every pull request, on a runner that has `lychee`. It does not see a link that a template or a script builds, a remote address, or a link inside code.

**The skill.** The procedure for citing, anchoring and moving, loaded by the session when it writes a link, adds a cited section or moves a document. It teaches the forms, the anchor keys and the mover. The module names it at session start, at each subagent's start and after every red. It shapes judgment and blocks nothing.

**The mover.** A command that moves or renames a document with `git mv`. It repairs every link to the document and every link inside it. It lists the places that still name the old path in prose, without changing them, and ends with the scan. After a move made by hand, the same command repairs what the move broke.

**Settings.** The module works with no configuration: every Markdown file git lists is covered. Dials narrow coverage to governed documents, and allow links through headings, ids in backticks or local paths while a repository adopts the rule. Further dials add the project's own lanes, and the places outside Markdown where ids are named. Two dials are every gate's: how loud a finding is, and where the log goes.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace: `claude plugin install const-referencing@claude-constitution-layer-kit --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-references.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
