---
name: new-document
description: >
  Load this skill first, before any new Markdown document is created in a repository that has a
  constitution.yaml — a policy, a record, a note, a comparison, a module document — every time,
  whether or not its home seems known. It creates the document in its canonical home, from its
  policy's template, with a valid envelope, through this plugin's command instead of writing the
  file by hand. Use when asked "write a policy for…", "add a note about…", "start a document on…",
  and when unsure where a new document goes or what its envelope must say. Advisory: it shapes how
  documents are born; nothing here blocks a write.
arguments: [kind, stem]
allowed-tools: Bash(sh ${CLAUDE_PLUGIN_ROOT}/scripts/new-document.sh *)
---

# New document

A document written where the conversation happens to be looking, with the frontmatter the
model last saw, is retrofit debt: nothing resolves it to a policy, its shape matches no
sibling, and the next document of its kind imitates it. This plugin's command makes creation
an act with a known outcome: it derives the home from the policy's territory, proves before
writing that the home lies in exactly that policy's territory, that nothing exists there and
that no document carries the id, and writes the file — from the kind's template when the
project names one, with `id`, `title` and `status` already filled, or from the envelope alone.
Everything else is yours to fill. Never write a governed document blind — by a shell heredoc,
by the `Write` tool, by copying a sibling — when this command can create it.

Kind: `$kind`. Stem: `$stem`. (Empty when invoked without them: derive both below.)

## 1. Name the kind

A kind is a policy: a document in the root policy's territory, whose `id` is a key of
`constitution.yaml` carrying that kind's `territory`. Read `constitution.yaml` and the policy
documents to find the one that governs what is asked for; the policy's body says what the kind
is and what its documents hold. If no policy covers it, the kind does not exist yet: stop, and
follow the `new-kind` skill of this plugin — the policy comes first, then the document.

## 2. Take the stem from where it is owned

The stem is the file name without `.md`, kebab-case (`a-z`, `0-9`, single hyphens). It is also
the document's `id` unless you give `--id`.

- **A numbered kind** — its stem carries a number, `<prefix>-<nnnn>-<slug>` — gets its stem from
  the project's numbering procedure for that kind; take the whole stem from there and give it
  as `--stem`. This command allocates no number.
- **A kind with a free segment** in its territory (`<dir>/*/NAME.md`) takes `--segment <name>`
  instead of `--stem`: the pattern fixes the file name, and the id becomes `name-<segment>`.
- **A kind with a single-path territory** has no home: that document already exists or is
  created by hand at exactly that path, once. The command says so.

## 3. Run the command

From inside the repository:

```bash
sh ${CLAUDE_PLUGIN_ROOT}/scripts/new-document.sh --kind <policy id> --stem <stem> --title '<title>'
```

- **`--type`** `current-state | task-record | non-authoritative` when the kind has no template in
  `const-locations.templates` of `constitution.yaml`: the policy says which its kind is. With a
  template, the template's own `type` decides and `--type` is not taken.
- **`--dry-run`** prints the home and the template and writes nothing. Use it first when another
  procedure writes the file itself — a record's procedure, a numbered kind's — and hand it the
  `HOME:` line.
- `--segment <name>` for a free-segment kind; `--id <id>` when the id must differ from the stem.

Read the lines it prints. `HOME:` is where the document is; `TEMPLATE:` is what it was written
from, or `none`; `CREATED:` and the count close a write. A `BROKEN:` line is a refusal with the
fix on the same line, and nothing was written: do what it says — for "is not a policy", the kind
needs its policy first (`new-kind`); for "two policies would govern it", the project's
territories overlap and a human narrows one; for "already exists", edit that document or choose
another stem.

## 4. Fill the body

Open the created file. The envelope is done: leave `id`, `type` and `status` as they are, and
change `title` only if the title was wrong. The body carries the template's placeholders — the
`<…>` prose — where you write; fill each, delete the alternatives the template marks for
deletion, and add nothing the template does not ask for. Where the kind has no template, the
body is the title's heading: write beneath it in the shape the policy describes. A kind whose
procedure owns fields of its own — a record's `stakes` and `decider`, its options and choice —
gets them from that procedure, not from here.

## 5. When the command is not there

In a repository with no `constitution.yaml`, nothing is governed and the command refuses; the
`new-kind` skill carries the procedure from zero. If the plugin's command cannot run — the first
`BROKEN:` line names a missing interpreter, library or git — install what it names; do not fall
back to writing the file by hand and calling it done.
