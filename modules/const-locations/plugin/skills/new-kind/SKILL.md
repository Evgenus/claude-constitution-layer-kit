---
name: new-kind
description: >
  Load this skill first, before a document is started that no policy covers, or a new directory of
  documents — every time, whether or not a kind seems to exist. It introduces a new document kind:
  its policy first — a process-stakes decision — then its territory line in constitution.yaml,
  then the first document, in that order. Use when the create-document command refuses a kind as
  "not a policy", and when a repository has no constitution.yaml yet and its first governed
  document is due. Advisory: nothing here blocks a write; the order is the rule.
---

# New kind

A document of a kind no policy covers is not created until the kind has its policy. The order
matters: a policy states what the kind is and what its documents hold, its territory says
where they live, and only then can a document be born at its home with a valid envelope. Doing
it backwards — the document first, the policy "later" — is how kinds without homes and
documents without governance accumulate. Adding, removing or re-scoping a policy is a
`process`-stakes decision under the constitution's conventions page the project adopted: a
decision record and one human yes.

## 1. Price it

State the kind in one sentence: what documents it holds, what shape they share, what rule set
governs them. If an existing policy already covers that — the same shape, the same rules — the
kind exists and the document goes there; use the `new-document` skill of this plugin. If not,
this is a `process` decision: write the record through the project's decision procedure if it
has one, otherwise as the conventions page describes, naming the decider, and get the yes.

## 2. Create the policy

A policy is a document in the root policy's territory. Create it with this plugin's command,
the root policy being its kind: the root policy is the file `root_policy` names in
`constitution.yaml`, and its `id` is the kind to give.

```bash
sh ${CLAUDE_PLUGIN_ROOT}/scripts/new-document.sh --kind <root policy id> --stem <policy stem> --title '<Kind> policy' --type current-state
```

(`--type` is not taken when the project's `const-locations.templates` names a template for
the root policy's kind; the template decides.) Run it alone, each value plain or in single
quotes: this plugin approves that form and no other. Fill the body: one paragraph saying which kind
it governs, then its rules, one per numbered item — the envelope its documents carry, their
shape, when they are created and changed, what is enforced by which check and what is
judgment. If the kind is numbered, say so and follow the project's numbering procedure for
the policy's own stem.

## 3. Claim the territory, by hand

Append to `constitution.yaml`, at the end of the file, a namespace keyed by the policy's `id`
with one `territory` line:

```yaml
<policy id>:
  territory: ["<dir>/**"]
```

The pattern is gitignore syntax, relative to the repository root. Write it as `<dir>/**` (or
`<dir>/**/*.md`) so that a home follows from it for every new document; a territory of one
path holds one document and nothing is born there. It must not overlap any other territory —
the root's included: two policies claiming one path is a defect every check reports. Do not
rewrite the file with a script: a YAML round trip loses its comments and renames its anchors.
Every check that reads the file validates it at its next run; if one reports the namespace,
the message names the line.

## 4. Create the first document

Now the `new-document` skill applies: `--kind <policy id>`, the stem, the title, and the
document is born at its home. If the kind has a template, name it first under
`const-locations.templates` in `constitution.yaml` — `{policy: <id>, template: <path>}` —
so the first document is written from it.

## From zero

A repository with no `constitution.yaml` governs nothing, and the command refuses until it
exists. Bootstrap by hand, once — this is the only time a policy is written without the
command; the paths below are an example, any layout inside the repository works:

1. `constitution.yaml` at the repository root:
   ```yaml
   root_policy: docs/policies/root-policy.md
   module_prefix: const-
   root-policy:
     territory: ["docs/policies/**"]
   ```
   `module_prefix` is required. It is the prefix that starts the name of every module's
   namespace in this file, `const-` for these modules. A file without it stops every check
   with a configuration failure that names the line to add.
2. The root policy at that path, with the envelope every governed document carries:
   ```markdown
   ---
   id: root-policy
   type: current-state
   title: Root policy — the policy for policies
   status: active
   ---

   # Root policy

   Governs the document kind *policy*: a document in this territory that governs one other
   kind. Rules: … (the envelope, one kind per policy, creation and change at process stakes)
   ```
3. From here the command works: every further policy is created by step 2 above, every
   further kind by steps 1 to 4.
