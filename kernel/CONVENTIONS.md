---
id: constitution-kernel
type: current-state
title: Constitution Kernel — Shared Conventions
status: active
---

# Constitution Kernel — Shared Conventions

*The semantic kernel. Everything here is vocabulary and shape — no machinery, no loading, no enforcement. Claude Code's own component model (plugins, skills, hooks, rules, config) is the mechanical kernel; this document defines only what the platform deliberately leaves undefined. A concept enters this document only when two or more modules need it; everything else belongs to the module that owns it. Modules reference these definitions and never redefine them.*

<a id="k1"></a>
## 1. Project document envelope

Every governed project document (Markdown) carries YAML frontmatter with at least:

```yaml
id: <stable-kebab-id>        # never changes after creation; never reused
type: <meta-type>            # see §2
title: <one line>
status: active               # active | inactive — lifecycle, see the lifecycle rule below
```

**Three exceptions to the `id` rule,** each for the items of a numbered kind. A number is provisional until its item lands on the main branch. First, an item not yet landed may meet, at a pull request, an item already on the main branch under its number. Then the one not yet landed takes a new number, in its file, its `id` and its references on its own branch. The item already landed keeps its number. Second, two items of one catalog — ids that share a prefix and a number — may both land on the main branch. Then the one that landed second takes a number the catalog has not held, in its file and its `id`. Every reference to it in the tree follows. Third, a kind that already has documents may become a catalog, or a catalog's form may change, as when its width grows. Then each of its documents not yet in that form takes it once, in its file and its `id`. Every reference to it in the tree follows. In each case the id it leaves is never reused.

Creation and modification history is the repository's job — no envelope field duplicates git metadata.

The envelope allows and expects more fields — upper layers (knowledge, binding) and individual modules extend it; they never alter the meaning of the fields above. Schema: `schemas/document-frontmatter.schema.json`.

**Supersession rule:** the working tree holds only current truth; history is git's. Superseding a state description (a `current-state` document) means *editing the document in place*. Its id and path stay stable, so every inbound reference keeps resolving to the current version. The previous version stays in git history, and the commit message names the change a supersession. No field or status duplicates this — git is the append-only layer. Records are not superseded in place: reversing a ruling is a new record (§5).

**Lifecycle rule:** `status` encodes lifecycle, with one meaning for every meta-type:

1. **`active`** — in force or current. That is a current-state document that binds, or a task-record whose delta the work still applies. So is a non-authoritative document that is its subject's current account, the version a reader consults.
2. **`inactive`** — historical: no authority, kept only as evidence while something references it. A non-authoritative document turns inactive when a later account supersedes it.

The project **deletes** a document that nothing should reference. Git history is the archive, reachable on explicit demand yet impossible to load or reference from the working tree. Authority is meta-type × status (§2); existence in the tree carries no authority by itself.

<a id="k2"></a>
## 2. Meta-types

Exactly one per document:

| type | meaning | authority |
|---|---|---|
| `current-state` | the reconciled truth: how the system is **and** should be, as of all completed work | authoritative; kept aligned with code at every task close |
| `task-record` | a change delta: the state agreed for a point in time, carrying its slice of not-yet-real intent while open | in-progress: outranks current-state within its scope; done: evidence |
| `non-authoritative` | explanation, investigation, research | carries no obligation |

**Precedence on conflict** — authority is meta-type × lifecycle:

1. Policies bind always.
2. An **active** `task-record` is the write-head: within its scope it outranks the current-state documents it is changing. **Task close is a single act:** the change lands in code *and* in the affected current-state documents together. Then the close sets the record `inactive` and deletes its working files (git remembers). An active task-record whose scope sees no commits counts as stalled drift. Its halfway state must go back into a commit or roll back, and never stand as de-facto truth.
3. Current-state documents outrank every `inactive` record. Closed tasks are evidence of their moment, nothing more.
4. **Planned** `task-record`s bind nothing; the further out, the less they even inform.

**The defect rule:** divergence between current-state documents and code outside any active task's scope is a defect — doc rot or an unrecorded change. The project must resolve it, and never tolerate it. Code is authoritative for *what is*. Current-state documents add *what must not change and why*. Intent that is not yet real rides in an open task's delta, never in a standing document.

<a id="k3"></a>
## 3. Governance binding

Policies claim **territories**: path patterns declared in the project's dials file (§6), each under the claiming policy's id. Within claimed territory, **every document resolves to exactly one governing policy**:

1. **By path** (primary): the canonical-location mapping binds the document to its policy. A policy is itself a governed document (`type: current-state`). **A document is a policy because it lies in the root policy's territory** — nothing declares itself a policy and nothing enumerates them. A policy governs exactly one **document kind**: documents sharing one shape and one rule set. Documents of different kinds never share a policy. A policy never enumerates the documents it governs: its territory is the enumeration. The dials file's kernel-owned key `root_policy` holds the root policy's path. The root's own namespace declares the territory where policies live. That territory contains the root itself, so every chain of governance ends there. A policy's machine-readable calibration, its territory included, lives in its dials namespace, which is its id. Its body is prose for humans and agents; the kernel specifies no internal policy format. A namespace whose id has no document in the root's territory is not a policy's, whatever keys it carries. A document in the root's territory with no namespace is a policy that claims nothing.
2. **By frontmatter declaration** (secondary): permitted only where the path mapping is absent or ambiguous — typically mid-transition, while an active task-record covers the move.

A document in claimed territory resolving to no policy, to more than one, or carrying a declaration that contradicts its path mapping, is a **defect**. Outside claimed territory the constitution is silent. Which policy governs a document is exactly the semantics neither git nor the platform expresses — hence kernel. The catalog itself and territory boundaries are module and project concerns.

<a id="k4"></a>
## 4. Stakes triage

Every governed decision is one of:

| stakes | meaning | ceremony |
|---|---|---|
| `routine` | reversible, cheap to revert | act; note in the commit message; no record |
| `process` | harness, policy, or procedure ruling | decision record + one human yes on the change, named in the commit that lands it. Where a PR flow exists, that is the commit that merges the pull request. The yes is its approval or, where no second human reviews it, the decider's own merge. This is the fast lane: a process fix never queues behind the full gate. |
| `product` | user-visible behavior | decision record |
| `architecture` | structural, hard to reverse | decision record + review |

The **enum is kernel; the boundary is a dial.** Where the routine/product line sits is per-project calibration, defined in the project's dials file (§6) by contrastive examples. Recurring commit notes on one theme are the standing signal to promote that theme to a recorded ruling or a documented procedure.

<a id="k5"></a>
## 5. Decision record

A decision record is a governed document (`type: task-record`) whose frontmatter additionally carries:

```yaml
stakes: process | product | architecture
decider: <person or role>   # kept because git cannot derive it: the committer is often not the decider
```

The decision moment and ordering are git's: a decision is operative when committed, and commit sequence is the precedence clock — no date field duplicates it. A record is `active` while the project applies its ruling, and `inactive` once the project has applied it. The ruling then lives in the current-state documents it changed, and the record remains as evidence of the options and reasoning (§1 lifecycle rule). A current-state document states every rule it binds in its own text. Its references to records are provenance — where and why someone decided a rule — never authority. A record is born `inactive` when the commit that creates it also applies its ruling. Only two cases allow an edit in place of a record's body, and the commit names each; its status change is no such edit.

**Before acceptance:** until the ceremony that §4 asks of its stakes is complete, whatever examines the record may still correct it. That ceremony is the yes of a `process` record, or the review of an `architecture` record. §4 asks neither of a `product` record, so it has no such window. A correction tightens, adds or withdraws a ruling item. The same commit corrects the current-state documents, so that the record's status stays true. What completes a review is the project's to say.

**Mechanical edits** leave every ruling untouched and may happen at any time. There are three kinds:

1. A typo, which the commit names a typo fix.
2. A reference-form migration — rewriting how a record cites other documents — which the commit names a migration.
3. A wording edit, which the commit names a wording edit. It changes the way a sentence or a list item reads. It leaves its meaning as it stands, with every fact, number and reference in it. The policy governing the project's records lists its kinds in a closed set.

Past the window of the first case, reversing or changing a ruling is a new record, never an in-place edit of the old one.

Body shape, when a real choice existed: the options considered, pros/cons per option, one recommendation with reasoning, the choice made. When no real choice existed, a record states the ruling and reasoning — no manufactured options. Schema: `schemas/decision-record.schema.json`.

<a id="k6"></a>
## 6. Dials file

Per-project calibration lives in **one** file at the repository root: `constitution.yaml`. Each module reads its own namespace (its plugin name). It ships defaults that apply when the file or namespace is absent: install-and-run must work with zero configuration. An existing file names, in the required kernel-owned key `module_prefix`, the prefix every module's namespace starts with: a kebab-case word ending in `-`. To resolve territory a module also reads the kernel-owned keys `root_policy` and `territory_dialect`, and the policy namespaces (§3); it reads no other module's namespace.

```yaml
# constitution.yaml
root_policy: docs/policies/root-policy.md   # kernel-owned: where the root policy is
module_prefix: const-                       # kernel-owned, required: the modules' prefix
# territory_dialect: gitignore              # kernel-owned, optional: every territory's pattern dialect; default gitignore
root-policy:                                # a policy's namespace is its id
  territory: ["docs/policies/**"]           # where policies live; the root lies inside
some-policy:                                # a policy found in the root's territory
  territory: ["docs/notes/**"]              # never overlapping another policy's, the root's included
  some_calibration: value
const-example-aspect:                       # a module's namespace, the plugin's name
  some_dial: value
```

**Territory patterns** follow the dialect named by the kernel-owned key `territory_dialect`. The default, `gitignore`, is `.gitignore` syntax evaluated against paths relative to the repository root: `**` crosses directories, `*` does not. A reader that does not support the declared dialect reports a configuration failure, never a silent pass. Two territories matching one path is the multi-policy defect of §3, whatever the dialect.

Schema: `schemas/constitution.schema.json` — the kernel-owned keys and the keys of a policy's namespace; module namespaces are open. Every reader validates the keys it reads against it at each read; a malformed file is a configuration failure, never a silent pass.

Profiles (e.g. solo-agents, small-team, regulated) are nothing but prewritten `constitution.yaml` files shipped with the kit.

**Portability rule:** no file in a module references a project directly. No project paths, names, repositories or values appear anywhere in a module's skills, hooks, scripts or prose. Everything project-specific enters through the module's dials namespace at runtime. The test is mechanical: **a module must install and operate on an empty repository** using only its defaults. Anything that breaks there is a binding leak.

<a id="k7"></a>
## 7. Naming

Modules are plugins named `const-<aspect>` (kebab-case). Module dial namespaces equal plugin names. Document ids, file names, and skill names: kebab-case. Every size and every budget counts **characters**, never tokens. A character is one Unicode code point of the file read as UTF-8. A CRLF line ending counts as one, and the count normalizes nothing and leaves nothing out. Bytes that are not valid UTF-8 count one per replacement character in their place. A decoder that follows the Unicode standard's recommended practice puts them there: one for each maximal subpart of an ill-formed subsequence.
