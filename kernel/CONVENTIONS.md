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

Creation and modification history is the repository's job — no envelope field duplicates git metadata.

Additional fields are allowed and expected — upper layers (knowledge, binding) and individual modules extend the envelope; they never alter the meaning of the fields above. Schema: `schemas/document-frontmatter.schema.json`.

**Supersession rule:** the working tree holds only current truth; history is git's. Superseding a state description (a `current-state` document) means *editing the document in place* — id and path stay stable so every inbound reference keeps resolving to the current version; the previous version lives immutably in git history; the commit message names the change a supersession. No field or status duplicates this — git is the append-only layer. Records are not superseded in place: reversing a ruling is a new record (§5).

**Lifecycle rule:** `status` encodes lifecycle, one meaning for every meta-type: `active` = in force or current (a current-state document that binds; a task-record whose delta is being applied; a non-authoritative document that is the current account of its subject — the version a reader consults); `inactive` = historical — no authority, kept only as evidence while something references it (for a non-authoritative document: superseded by a later account). A document that nothing should reference is **deleted** — git history is the archive, reachable on explicit demand yet impossible to load or reference from the working tree. Authority is meta-type × status (§2); existence in the tree carries no authority by itself.

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
2. An **active** `task-record` is the write-head: within its scope it outranks the current-state documents it is changing. **Task close is a single act:** changes are applied to code *and* to the affected current-state documents together; then the record is set `inactive` and its working files are deleted (git remembers). An active task-record whose scope sees no commits is stalled drift — the halfway state must be committed back or rolled back, never left as de-facto truth.
3. Current-state documents outrank every `inactive` record. Closed tasks are evidence of their moment, nothing more.
4. **Planned** `task-record`s bind nothing; the further out, the less they even inform.

**The defect rule:** divergence between current-state documents and code outside any active task's scope is a defect — doc rot or an unrecorded change — to be resolved, never tolerated. Code is authoritative for *what is*; current-state documents add *what must not change and why*; intent that is not yet real rides in an open task's delta, never in a standing document.

<a id="k3"></a>
## 3. Governance binding

Policies claim **territories**: path patterns declared in the project's dials file (§6), each under the claiming policy's id. Within claimed territory, **every document resolves to exactly one governing policy**:

1. **By path** (primary): the canonical-location mapping binds the document to its policy. A policy is itself a governed document (`type: current-state`). **A document is a policy because it lies in the root policy's territory** — nothing declares itself a policy and nothing enumerates them. A policy governs exactly one **document kind** — documents sharing one shape and one rule set; documents of different kinds never share a policy, and a policy never enumerates the documents it governs: its territory is the enumeration. The dials file's kernel-owned key `root_policy` holds the root policy's path; the root's own namespace declares the territory where policies live, which contains the root itself, so every chain of governance ends there. A policy's machine-readable calibration, its territory included, lives in its dials namespace, which is its id; its body is prose for humans and agents — the kernel specifies no internal policy format. A namespace whose id has no document in the root's territory is not a policy's, whatever keys it carries; a document in the root's territory with no namespace is a policy that claims nothing.
2. **By frontmatter declaration** (secondary): permitted only where the path mapping is absent or ambiguous — typically mid-transition, while an active task-record covers the move.

A document in claimed territory resolving to no policy, to more than one, or carrying a declaration that contradicts its path mapping, is a **defect**. Outside claimed territory the constitution is silent. Which policy governs a document is exactly the semantics neither git nor the platform expresses — hence kernel; the catalog itself and territory boundaries are module and project concerns.

<a id="k4"></a>
## 4. Stakes triage

Every governed decision is one of:

| stakes | meaning | ceremony |
|---|---|---|
| `routine` | reversible, cheap to revert | act; note in the commit message; no record |
| `process` | harness, policy, or procedure ruling | decision record + one human yes on the change — PR approval where a PR flow exists, otherwise named in the commit message that lands it (the fast lane — a process fix never queues behind the full gate) |
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

The decision moment and ordering are git's: a decision is operative when committed, and commit sequence is the precedence clock — no date field duplicates it. A record is `active` while its ruling is being applied and `inactive` once applied — the ruling then lives in the current-state documents it changed, and the record remains as evidence of the options and reasoning (§1 lifecycle rule). A current-state document states every rule it binds in its own text; its references to records are provenance — where and why a rule was decided — never authority. A record whose ruling is applied in the same commit that creates it is born `inactive`. A record's body is edited in place in two cases only, and the commit names each; its status change is no such edit. **Before acceptance:** until the ceremony that §4 asks of its stakes is complete — the yes of a `process` record, the review of an `architecture` record; a `product` record, asked for neither, has no such window — whatever examines the record may still correct it: a ruling item tightened, added or withdrawn, with the current-state documents corrected in the same commit, so that the record's status stays true. What completes a review is the project's to say. **Mechanical edits,** which leave every ruling untouched, at any time: a typo, or a reference-form migration — rewriting how a record cites other documents — which the commit names a migration. Past that window, reversing or changing a ruling is a new record, never an in-place edit of the old one.

Body shape, when a real choice existed: the options considered, pros/cons per option, one recommendation with reasoning, the choice made. When no real choice existed, a record states the ruling and reasoning — no manufactured options. Schema: `schemas/decision-record.schema.json`.

<a id="k6"></a>
## 6. Dials file

Per-project calibration lives in **one** file at the repository root: `constitution.yaml`. Each module reads its own namespace (its plugin name) and ships defaults that apply when the file or namespace is absent — install-and-run must work with zero configuration. To resolve territory a module also reads the two kernel-owned keys, `root_policy` and `territory_dialect`, and the policy namespaces (§3); it reads no other module's namespace.

```yaml
# constitution.yaml
root_policy: docs/policies/root-policy.md   # kernel-owned: where the root policy is
# territory_dialect: gitignore              # kernel-owned, optional: the pattern dialect of every territory; default gitignore
root-policy:                                # a policy's namespace is its id
  territory: ["docs/policies/**"]           # where policies live; the root lies inside
some-policy:                                # a policy found in the root's territory
  territory: ["docs/notes/**"]              # never overlapping another policy's, the root's included
  some_calibration: value
const-example-aspect:                       # a module's namespace, named after the plugin
  some_dial: value
```

**Territory patterns** follow the dialect named by the kernel-owned key `territory_dialect`. The default, `gitignore`, is `.gitignore` syntax evaluated against paths relative to the repository root: `**` crosses directories, `*` does not. A reader that does not support the declared dialect reports a configuration failure, never a silent pass. Two territories matching one path is the multi-policy defect of §3, whatever the dialect.

Schema: `schemas/constitution.schema.json` — the kernel-owned keys and the keys of a policy's namespace; module namespaces are open. Every reader validates the keys it reads against it at each read; a malformed file is a configuration failure, never a silent pass.

Profiles (e.g. solo-agents, small-team, regulated) are nothing but prewritten `constitution.yaml` files shipped with the kit.

**Portability rule:** no file in a module references a project directly — no project paths, names, repositories, or values anywhere in a module's skills, hooks, scripts, or prose. Everything project-specific enters through the module's dials namespace at runtime. The test is mechanical: **a module must install and operate on an empty repository** using only its defaults; anything that breaks there is a binding leak.

<a id="k7"></a>
## 7. Naming

Modules are plugins named `const-<aspect>` (kebab-case). Module dial namespaces equal plugin names. Document ids, file names, and skill names: kebab-case. All sizes and budgets are measured in **characters**, never tokens.
