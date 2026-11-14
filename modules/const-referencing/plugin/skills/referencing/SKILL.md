---
name: referencing
description: >
  Load this skill first, before writing a link between documents, adding a section, table row or
  rule that others will cite, or moving, renaming or deleting a document — every time, whether or
  not the form seems known. It writes references that a machine can follow and a move can repair:
  cite a document by its id as a link, give every cited place an explicit anchor with a short
  fixed key, cite code by symbol name, move or rename a document with the mover so that every link
  to it is repaired, repair links after a move made by hand. Use when a write was blocked for a
  bare handle, an id in backticks, an id link that opens another file or a path on one machine,
  and when the check after a write or the scan reports a link target that does not exist, an
  anchor that does not exist, or a link that resolves only through a heading. Advisory: it shapes
  how references are written and moved; the gate checks their form and that they resolve.
---

# References

A reference is worth writing only if the next reader can follow it and the next move cannot
silently break it. Two kinds fail. One is the link that once led somewhere: its target was moved, its
heading reworded. The break sits in *another* file than the one that was edited, so nobody
sees it. The other is the reference that never was a link: "see section 4", a row number, an id in
backticks. No tool can follow these forms and no move can find them.

What is checked and what is not. This plugin's hook blocks a Markdown document that cites by a
bare form the project declared (`const-referencing.lanes` in `constitution.yaml`). It blocks one that shows a
covered document's id in backticks outside a link. It blocks one that holds a link whose text is a document's
id and whose target is another file. Unless the project set `local_paths: allow`, it blocks one that names a path on one machine.
Such a path is a home-directory path or a `file:` link, and the hook blocks it inside code as well. After every write it
checks the whole tree and reports what the write broke. The report covers the breaks in the written document and in every
document that links to it. That report cannot undo the write: fix what it names in your next
step. The scan checks all of it for every covered document and is what a pull request runs.
Where the project set `severity: warn`, findings are reported and nothing is blocked. Some questions are
judgment: which form to choose, where an anchor goes, what to do with a sentence that names an old path.
The rest of this page is about them.

## 1. Cite by id, as a link

1. A document that opens with a YAML block carrying an `id` is cited by that id as the link's
   text: `[the-id](relative/path.md)`. Or it is cited as `[the-id][label]` with the path in a reference
   definition, which is judged the same. Not a description as the text: the id is what the id
   repair of section 4 works from, and what a reader can search for.
2. A file with no id — a script, a configuration file — is cited by its relative path, as a link.
3. A place inside a document is cited by path and anchor, with the place's own handle as the
   text: `[rule 3](policy.md#r3)`.
4. Inside its own document a handle may stand bare — "rule 3" within the policy that numbers
   its rules. Everywhere else it is a link. The project's `lanes` say which bare forms the
   hook refuses, and in which documents each is at home.
5. Code is cited by symbol name, qualified by its file — "`read_event` in `events.py`". A line
   range points at today's text and at something else tomorrow: use one only in a sentence
   about a diff.
6. A commit hash belongs in a commit message, a record of what was decided or a dated comparison.
   It belongs too in a dated statement of evidence or of done work, or in chat. It does not belong in a sentence that describes
   how things are: a rebuilt history leaves it pointing at nothing.
7. A pull request is cited with its repository — `owner/repo#n`, never a bare `#n`: a bare
   number names another pull request in every other repository.

## 2. Give every cited place an anchor of its own

1. Write `<a id="key"></a>` on its own line, directly before the heading or paragraph that will
   be cited. For a table row, put it inside the row's first cell. For a numbered rule or ruling
   that opens with a bold name or handle, put it right before that name or handle:
   `<a id="r3"></a>**R3.**`.
2. The key is short and fixed: a letter and a number, a row's own handle in lowercase — not the
   heading's words. It is for machines; it does not have to read well.
3. Never cite a heading's generated name (`#7-dials`). It changes when the heading is reworded,
   and every link through it breaks with nobody noticing. The scan reports such a link and
   names the fix. Do not write `{#key}` after a heading either: the link checker accepts it,
   a forge shows it as text.
4. An anchor's case counts: cite `#k1` as it is written.
5. A key that is cited is never renamed and never reused for another place. A wrong key that
   six documents cite stays.

## 3. Move or rename a document with the mover

Never `git mv` a document and search-and-replace its old name. That rewrites code samples and
sentences that mean the old place, and misses the moved document's own links. One act:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/move-document.sh" <old path> <new path>
```

Paths are given from where you stand. It moves the file with `git mv`. It rewrites every covered
document's links to it and the moved document's own relative links, and each keeps its anchor.
It leaves alone every link inside code, a comment, or the YAML block that opens a file. Then
it scans the whole tree and exits with the scan's verdict: 0 means no reference is broken.

1. Read every `MENTION:` line it prints. Each is a place that names the old path outside a
   link: a sentence, a code sample, a script. Nothing there was changed. Decide one by one. A
   sentence such as "this lived at `old/path.md` until March" means the old place and stays.
   A script that opens the old path needs the new one.
2. If it exits 2, the scan's findings follow the count line; fix them as they say. They may be
   older than the move.
3. If it refuses, nothing was changed. What can refuse without moving is asked first. A document
   it cannot read or rewrite after the move makes it move the file back, and its last line
   says so. If instead its last line says the act stopped midway, the file was
   moved and some links rewritten. Look at `git status`, repair what the message names, and run
   the scan of section 6.
4. Its rewrites are not staged. Look at `git diff` before committing, and say in the commit
   message that the commit is a move.
5. A document's `id` never changes with a move. The mover does not offer changing one.

## 4. Repair after a move made by hand

When the scan reports targets that do not exist because someone moved a file with `git mv`, the
shell, or another tool:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/move-document.sh" --moved <old path> <new path>
```

It makes the same repair for a move that has already happened. Many documents may have been moved
with their links carrying ids as text. Then one command repairs them all, with no path given. The YAML
block of each document says where it is:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/move-document.sh" --ids
```

It leaves alone an id that two documents carry: nothing says which one is meant.

## 5. Deleting a document

Delete it, then run the scan: every link to it is reported. Remove each link and say in its
place, in words, what the document was cited for — a link's text alone rarely carries that.

## 6. After anything the hook did not see

A shell command, another tool, another person's commit: none of them passes the hook. Run the
scan when you are done, and before a pull request:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/check-references.sh" --scan
```

Exit 0 green, 2 findings, 1 the checker could not run — a missing `lychee` among the causes,
with the install address in the message.

## 7. In chat

Every reference to a file, a section or a document is a markdown link wherever the file exists.
A number, a letter or a key is local to its message, its decision or its session. When you cite
one across that boundary, name where it came from: "option B of the decision on coverage", not
"B".
