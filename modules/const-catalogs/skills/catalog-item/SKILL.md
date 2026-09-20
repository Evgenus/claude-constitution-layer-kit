---
name: catalog-item
description: >
  Number a document of a numbered kind: take the catalog's next number, name the file
  <prefix>-<nnnn>-<slug>.md with the same id, renumber after a collision at a pull request,
  list a catalog, cite an item. Use when creating a document of a kind the project numbers —
  decision records, tasks, RFCs — when a write was blocked for a file name, an id or a number
  already taken, when the scan reports two items under one number, when asked what a catalog
  holds or what a missing number was, or when a kind is about to become numbered. Advisory:
  it shapes allocation, renumbering and citation; the gate checks the name, the id and the
  number's uniqueness.
---

# A catalogued item

A project cites its decisions, tasks and the like by number. That works only while a number
means one document, stands in the one name every reference resolves — the file's — and never
comes to mean another document later. A catalog is nothing but the set of files that carry
its prefix: there is no index, no register, no counter file to keep in step, and none is ever
written — a generated list drifts from the files, and the files are the truth.

What is checked and what is not. For every catalog listed under `const-catalogs.catalogs` in
the project's `constitution.yaml`, this plugin's hook blocks a Markdown document in that
catalog's territory whose file name is not `<prefix>-<number>-<slug>.md`, whose `id` is not
that name without `.md`, or — for a file that does not exist yet — whose number another item
already carries; where the project set `severity: warn` it reports and lets the write through.
The scan adds: no two items of one catalog under one number. With no catalog listed, nothing
is checked, and every run says so. Which number to take, when it is final, who renumbers, how
to cite: that is judgment, and the rest of this page.

## 1. Find the catalog

Read `const-catalogs.catalogs` in `constitution.yaml`. Each entry is one numbered kind:
`prefix` (lowercase letters and digits), `territory` (where its documents live), `width` (how
many digits, 4 when absent). The document you are writing belongs to the catalog whose
territory holds its path.

If the kind is not listed and should be numbered, say so to the user before writing anything:
the prefix is sticky, because an id never changes — numbering a kind that already has
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

It names every catalog's reach — `dec up to dec-0028`, or `dec up to dec-0028, dec-0031 in
history` when a higher item existed once and was deleted, or `dec none yet`. **The new number
is one more than the highest number that line names for the catalog**, history included: the
number of a deleted item is never given to another document, because somebody may still cite
it. `none yet` means number 1. If the line ends in `history not available in a shallow
clone`, the history part is missing: fetch the history first (`git fetch --unshallow`), or
accept that a deleted top number cannot be seen.

The number is **provisional until your branch lands on the main branch, and frozen from then
on.** Another branch may take the same number meanwhile; whoever lands second renumbers
(section 4). So cite a new item outside your own branch only after it has landed.

## 3. Write the item

- File: `<prefix>-<number>-<slug>.md` inside the catalog's territory. The number has exactly
  `width` digits, zero-padded; the slug is lowercase words and digits joined by `-`, and says
  what the item is about.
- `id`: that file name without `.md`, exactly. One identifier per document: a reference by id
  and a search by file name then find the same document.
- The rest of the document — the other envelope fields, the body, the kind's template — follows
  the project's own rules for that kind. If the project provides a template or a creation
  procedure for the kind, start from it and bring this number and this name to it.

If the write is blocked, the message names the number to take. Take it; do not argue with a
count.

## 4. Two items under one number

The scan reports it, usually at a pull request: two branches each took the next number.

1. **The item already on the main branch keeps its number.** The other one renumbers — yours,
   if your branch is the one not yet landed.
2. Bring your branch up to date with the main branch, then take the number again as in
   section 2.
3. Rename the file with `git mv`, and set its `id` to the new name.
4. Rewrite the references **made on your own branch**, and only those:
   `git grep -n -i '<prefix>-<old number>' -- $(git diff --name-only <main branch>...HEAD)`
   finds both the full name and the bare form. References elsewhere mean the other item.
5. Run the scan again. `git mv` and shell edits are not seen by the hook.

## 5. List a catalog, find an item, explain a gap

- List, on demand, never into a file:
  `git ls-files --cached --others --exclude-standard -- ':(glob)**/<prefix>-[0-9]*-*.md'`
  and, for the titles, the same list through `xargs grep -m1 -H '^title:'`.
- Find an item by its number, however the prefix was capitalized:
  `git ls-files -- ':(icase,glob)**/<prefix>-<number>-*'`
- A missing number is legitimate: an item deleted, or renumbered before it landed. Never
  fill a gap with a placeholder, and never reuse the number. What it was:
  `git log --diff-filter=D --name-only --format='%h %s' -- ':(glob)**/<prefix>-<number>-*'`

## 6. Cite an item

- Where a machine reads the reference — an envelope field, a link target — write the **full
  name**: `<prefix>-<number>-<slug>`. It stays unambiguous whatever happens to the number.
- In prose the bare form is fine, in either case: `DEC-0007`, `dec-0007`. It resolves by the
  command in section 5.
- Cite by number only what has landed on the main branch.

## 7. Before you finish

If an item was created, renamed or edited through the shell (`git mv`, a heredoc, `sed`), the
hook did not see it. Run the scan of section 2 — exit 2 lists the findings with the same
messages the hook gives.
