---
name: catalog-item
description: >
  Load this skill first, before creating any document of a kind the project numbers — a decision
  record, a task, an RFC — every time, whether or not the next number seems known. It numbers the
  document: take the catalog's next number, name the file <prefix>-<nnnn>-<slug>.md with the same
  id, renumber after a collision at a pull request, list a catalog, cite an item. Use when a write
  was blocked for a file name, an id or a number already taken, when the scan reports two items
  under one number, when asked what a catalog holds or what a missing number was, or when a kind
  is about to become numbered. Advisory: it shapes allocation, renumbering and citation; the gate
  checks the name, the id and the number's uniqueness.
---

# A catalogued item

A project cites its decisions, tasks and the like by number. That works only while a number
means one document, and stands in the one name every reference resolves — the file's. It also
works only while the number never comes to mean another document later. A catalog is nothing
but the set of files that carry its prefix. There is no index, no register, no counter file to
keep in step, and none is ever written. A generated list drifts from the files, and the files
are the truth.

What is checked and what is not. For every catalog listed under `const-catalogs.catalogs` in
the project's `constitution.yaml`, this plugin's hook blocks a Markdown document in that
catalog's territory in three cases. The first is a file name that is not
`<prefix>-<number>-<slug>.md`. The second is an `id` that is not that name without `.md`.
The third, for a file that does not exist yet, is a number another item already carries. Where the project set `severity: warn`, the hook reports and lets the write through.
The scan adds: no two items of one catalog under one number. With no catalog listed, nothing
is checked, and every run says so. Which number to take, when it is final, who renumbers, how
to cite: that is judgment, and the rest of this page.

## 1. Find the catalog

Read `const-catalogs.catalogs` in `constitution.yaml`. Each entry is one numbered kind:
`prefix` (lowercase letters and digits), `territory` (where its documents live), `width` (how
many digits, 4 when absent). The document you are writing belongs to the catalog whose
territory holds its path.

If the kind is not listed and should be numbered, say so to the user before writing anything.
The prefix is sticky, because an id never changes. Numbering a kind that already has
documents means renaming every one of them, once, with every link to them. The entry to add:

```yaml
const-catalogs:
  catalogs:
    - {prefix: <short, lowercase>, territory: ["<pattern of the paths where the kind lives>"], width: 4}
```

## 2. Take the number

Run the scan and read its last line:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/check-catalog-item.sh" --scan
```

It names every catalog's reach in one of three forms. The first is `<prefix> up to <prefix>-0028`.
The second is `<prefix> up to
<prefix>-0028, <prefix>-0031 in history`, when a higher number was held once. Such a number was
held by an item since deleted or renamed, or by a file of that name elsewhere in the
repository. The third is `<prefix> none
yet`, which may be followed by `in history` too. **The new number is one more than the highest
number that line names for the catalog**, history included. A number once held is never given
to another document, because somebody may still cite it. `none yet` with nothing after it
means number 1. If the line ends in `history incomplete in a shallow clone`, fetch the history
first (`git fetch --unshallow`). If it ends in `history could not be read`, find out why git
would not list it. In both cases a deleted top number may be out of sight. If the catalog is
marked `(full: the width can write no higher number)`, stop and tell the user: a wider width
renames every item.

If the user widens the catalog, every item takes the new width once. Rename each file with
`git mv` and set its `id` to the new name. Then rewrite every reference to it in the whole
tree, as for two landed items in section 4. An old id is never given to another item. Where
the project accepts items by a trailer naming the id, accept each renamed item again in the
change that renames it.

The number is **provisional until your branch lands on the main branch, and frozen from then
on**. There is one exception: two landed items under one number (section 4). Another branch may
take the same number meanwhile; whoever lands second renumbers (section 4). So cite a new
item outside your own branch only after it has landed.

## 3. Write the item

- **File.** `<prefix>-<number>-<slug>.md` inside the catalog's territory. The number has exactly
  `width` digits, zero-padded; the slug is lowercase words and digits joined by `-`, and says
  what the item is about.
- **`id`.** That file name without `.md`, exactly. One identifier per document: a reference by id
  and a search by file name then find the same document.
- **The rest** of the document — the other envelope fields, the body, the kind's template — follows
  the project's own rules for that kind. If the project provides a template or a creation
  procedure for the kind, start from it and bring this number and this name to it.

If the write is blocked, the message names the number to take. Take it; do not argue with a
count.

## 4. Two items under one number

The scan reports it, usually at a pull request: two branches each took the next number. It
reports it on the main branch too, when both branches have merged. Which case you are in
decides the steps.

**One item is on the main branch, the other is not yet.**

1. **The item already on the main branch keeps its number.** The other one renumbers — yours,
   if your branch is the one not yet landed.
2. Bring your branch up to date with the main branch, then take the number again as in
   section 2.
3. Rename the file with `git mv`. It also works where the file system ignores case, as a
   plain write to the new name does not. Then set its `id` to the new name.
4. Rewrite the references **made on your own branch**, and only those. The command
   `{ git diff -z --name-only "$(git merge-base <main branch> HEAD)"; git ls-files -z --others --exclude-standard; } | xargs -0 -r git grep -n -i --untracked '<prefix>-<old number>' --`
   finds both the full name and the bare form, in every file your branch touched. Those files
   may be committed, not yet committed, or not yet added. References elsewhere mean the other
   item.
5. Run the scan again. `git mv` and shell edits are not seen by the hook.

**Both items are on the main branch.** Both numbers are frozen, yet one number cannot name two
items. The one that landed second gives way, and a reference anywhere in the tree may mean it.

1. **Find which landed second.** For each item, once:
   `git log --first-parent --diff-filter=A --format='%h %cI' <main branch> -- <path of the item>`
   The item with the later line landed second. It renumbers; the other keeps its number.
2. Take the number again as in section 2: one more than the highest the scan's line names,
   history included.
3. Rename the file with `git mv` and set its `id` to the new name.
4. Rewrite the references in the **whole tree**, not only in the files of your branch. The
   command is:
   `git grep -n -i --untracked '<prefix>-<old number>' --`
   The full old name, slug included, means the item that renumbers. Rewrite it to the new
   name. The bare form, `<PREFIX>-<old number>`, may mean either item: read each place and
   rewrite only what means the item that renumbers. Commit messages stay as they are.
5. Run the scan again, and run the grep once more: it must find the old number only where it
   means the item that kept it.
6. Where the project accepts items by a trailer naming the id, the old trailer now names an
   id that no longer exists. Accept the renumbered item again under its new id, in the change
   that renumbers it.

## 5. List a catalog, find an item, explain a gap

- **List,** on demand, never into a file:
  `git ls-files --cached --others --exclude-standard -- ':(glob)**/<prefix>-[0-9]*-*.md' | sort`
  and, with the titles:
  `git ls-files --cached --others --exclude-standard -z -- ':(glob)**/<prefix>-[0-9]*-*.md' | sort -z | xargs -0 -r grep -m1 -H '^title:'`
  The list goes by the prefix, wherever a file lies. An item whose name lacks the form is not
  in it — the scan reports those.
- **Find** an item by its number, however the prefix was capitalized, committed or not:
  `git ls-files --cached --others --exclude-standard -- ':(icase,glob)**/<prefix>-<number>-*'`
- **A missing number** is legitimate: an item deleted, or renumbered before it landed. Never
  fill a gap with a placeholder, and never reuse the number. What it was:
  `git log --diff-filter=D --name-only --format='%h %s' -- ':(glob)**/<prefix>-<number>-*'`

## 6. Cite an item

- **Machine surfaces.** Where a machine reads the reference — an envelope field, a link target — write the **full
  name**: `<prefix>-<number>-<slug>`. It stays unambiguous whatever happens to the number.
- **In prose** the bare form is fine, in either case: `ADR-0007`, `adr-0007`. It resolves by the
  command in section 5.
- **Cite by number** only what has landed on the main branch.

## 7. Before you finish

If an item was created, renamed or edited through the shell (`git mv`, a heredoc, `sed`), the
hook did not see it. Run the scan of section 2 — exit 2 lists the findings with the same
messages the hook gives.
