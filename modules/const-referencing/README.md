# const-referencing

<a id="a1"></a>
## What it gives you

References a machine can follow and a move can repair: one written form per kind of reference, anchors that do not depend on a heading's words, a check of the whole tree after every write and in the scan, and a mover that repairs the links a move breaks. Plus a skill for citing, anchoring and moving, and two always-on sentences about references in chat.

<a id="a2"></a>
## Why use it

A document is moved, a heading is reworded, a page is deleted, and every link that pointed there still reads as a link and leads nowhere, or to a neighbour that happens to carry the old heading's words. Nobody notices at the edit, because the break is in other files; a reader finds it weeks later and can no longer tell what was meant. Beside the broken link stands the reference that never was one: a bare "see section 4", an id in backticks, a path that exists only on the author's machine. No tool can follow those, and a rename cannot find them.

<a id="a3"></a>
## How Claude behaves with it

Before a session writes or edits a Markdown file, the forms of its references are checked, and a bad form refuses the write: a document's id in backticks where a link is due, a link whose text is one document's id but which opens another, a path into someone's home folder, and any bare form the project lists as a lane, such as a requirement number that must be a link outside its home document. After the write, the whole tree is checked: a link to a file that does not exist, an anchor that does not exist, and a link that resolves only through a heading's generated name instead of an anchor written in the target. These are reported to the session, since the write has already happened; the scan is where they turn red.

```text
RED: docs/notes/refs.md:3: document id 'plc-notes' stands in backticks and is no link
  why: an id names a document that can move: only a link lets a reader reach it and lets a move repair it
  fix: write [plc-notes](../policies/plc-notes.md) — the path from this document to docs/policies/plc-notes.md
```

At every session start two sentences are added to the session's context: in chat, every reference to a file, a section or a document is a markdown link, and a number or a key is a handle local to its message, named with its source when a cite crosses that boundary. The skill `referencing` loads on its own when links are written, when a section others will cite is added, and when a document is moved: it has the session move a document with the module's mover, never by hand.

<a id="a4"></a>
## How it works

**Before a write.** A hook runs before every `Write` and `Edit` of a Markdown file. It reads the file as it would be after the write and checks the forms above; a finding refuses the write. It needs no network and no other tool.

**After a write.** A second hook runs after the write and asks the link checker, the `lychee` tool, whether every link and anchor of the written file resolves. A break is reported to the session but cannot block, since the file is already written. Without `lychee` on the machine, the forms are still checked, and every write says that resolution was not.

**The scan.** Both checks over every Markdown file git lists, plus one more: an id named in a script or a configuration file, where no link checker looks, must be the id of a document that exists. It exits with code 2 on a finding. Run it in CI on every pull request, on a runner that has `lychee`.

**The mover.** A command that moves or renames a document with `git mv`, repairs every link to it and every link inside it, lists the places that still name the old path in prose without changing them, and ends with the scan. After a move made by hand, the same command repairs what the move broke.

**At session start, and the skill.** The two sentences, printed by a hook; and the procedure for citing, anchoring and moving, loaded when the activity occurs. Nothing in either blocks.

**Settings.** The module works with no configuration: every Markdown file git lists is covered. Dials narrow coverage to governed documents, allow links through headings or ids in backticks or local paths while a repository adopts the rule, and add the project's own lanes and the places outside Markdown where ids are named. Two dials are every gate's: how loud a finding is, and where the log goes.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-referencing@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-references.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md); the complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
