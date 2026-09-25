---
id: kit-intent
type: current-state
title: Constitution Kit — Intent
status: active
---

# Intent

<a id="i1"></a>
## What this repository is

A **portable constitution for AI-driven development with Claude Code**: the rules, conventions, and mechanisms that govern how sessions produce documents, make decisions, and keep artifacts consistent — designed once, at the right level of abstraction, and installed into any project (existing or new) when needed. Distribution unit: Claude Code plugins. Per-project cost of adoption: install, pick a profile, override a few dials. No design session, no re-derivation.

<a id="i2"></a>
## The problem it solves

Without a constitution, every project and every participant improvises: documents without declared authority, decisions living in chat scrollback, rulings priced identically whether trivial or structural, doc↔code drift with no owner, session exhaust posing as knowledge. With a *heavyweight* constitution, the cure exceeds the disease: fixed-price ceremony for every uncertainty, harness fixes deadlocked behind the gates they fix, hundreds of rules built before the first product decision. This kit is the deliberate middle: **a minimal semantic core, hard gates only where checks are deterministic, honesty everywhere else, and growth only from observed friction.**

<a id="i3"></a>
## Architecture

Three layers, strictly separated:

1. **Mechanical kernel — Claude Code itself.** Plugins, skills, hooks, agents, rules, settings are the component model. This repo never mirrors or wraps them; wanting infrastructure the platform omitted is a design smell.
2. **Semantic kernel — `kernel/CONVENTIONS.md` + schemas.** One page: document envelope, meta-types with lifecycle-aware precedence, governance binding by territory, stakes triage, decision-record shape, dials, naming. Only vocabulary two or more modules need; nothing derivable from git (git owns history, ordering, authorship, supersession trails, archives).
3. **Modules — `modules/const-*`.** Invariant-shaped installation units, each a plugin: one invariant, one enforcement moment, one lifecycle trigger; depending on the kernel and nothing else; project-blind, calibrated per project through a single `constitution.yaml`. Requirements are the traceability matrix in `docs/requirements.md` — a module implements exactly its rows. What every gate must have — reading the hook event and the dials file, territories, the output log, the command line and its guard — is written once, under `shared/`, and each module links to it; the platform copies what the link points at into the installed plugin, so a module still depends on the kernel and nothing else (decision [dec-0025-shared-gate-code-linked](docs/decisions/dec-0025-shared-gate-code-linked.md)).

**Consumer projects** hold the binding: territory maps, boundary examples, thresholds, deciders, and all governed content. The relationship is package-shaped: modules are versioned here, installed there; friction flows back as commit notes; recurring themes become kit changes.

<a id="i4"></a>
## Design principles (each earned, not assumed)

- <a id="p1"></a>**Native-first:** platform mechanisms > repo scripts > third-party tools > new infrastructure; each step down names what the native option cannot do.
- <a id="p2"></a>**Invariant, not machinery:** what ships day one is the minimal deterministic guard against *accumulating* failures (each unguarded artifact raises repair cost silently); *self-limiting* frictions wait for observed pain. Governance sophistication is self-limiting by definition.
- <a id="p3"></a>**Ceremony scales with stakes:** routine → act and note in the commit; `process` → record plus one human yes (the fast lane — a harness fix never queues behind the gate it fixes); `product` → record; `architecture` → record plus review. A constitution that prices a naming nit and a security ruling identically is defective.
- <a id="p4"></a>**Enforcement honesty:** gates are deterministic and red-means-fix; everything judgment-based is advisory and says so. Conversation is shaped, never gated.
- <a id="p5"></a>**Git-derivability razor:** no field, status, or record duplicates what the repository already expresses. The working tree holds current truth; history, ordering, and archives are git's.
- <a id="p6"></a>**Reconciliation model:** current-state documents are the truth reality converges to, aligned with code at every task close; in-progress tasks are the write-head; divergence outside an active task's scope is a defect; drift without commit-back is prohibited.
- <a id="p7"></a>**Boundaries by example:** judgment thresholds are defined by contrastive pairs, never abstract criteria.

<a id="i5"></a>
## What this repository is not

- **Not a project.** No project names, paths, content, or calibration anywhere ([kernel §6](kernel/CONVENTIONS.md#k6); held by the [aspect A12](docs/requirements.md#a12) gates — bare-repo install, single-module run, project-reference grep — run by hand until the kit's CI runs them, [step 10 of the rollout plan](docs/rollout-plan.md#s10)). The kit is nonetheless **consumer zero** of the document-shaped modules, of the kinds it creates, of the code territories its own current-state documents describe, and of the session conduct its own guide states: its own records, intent page, and module documents sit under a claimed territory in a kit-root `constitution.yaml`, and its shared code, module scripts and git hooks under a coverage map there, and its session guide carries by hand the rules a module ships as a skill — calibration of the kit, never of a project (decisions [dec-0006-accumulating-set-first](docs/decisions/dec-0006-accumulating-set-first.md), [dec-0035-locations-module-rulings](docs/decisions/dec-0035-locations-module-rulings.md), [dec-0036-task-close-module-rulings](docs/decisions/dec-0036-task-close-module-rulings.md), [dec-0041-questions-module-rulings](docs/decisions/dec-0041-questions-module-rulings.md)).
- **Not the knowledge layer.** Subject-shaped knowledge units, distillation, pointer generation, and staleness tracking are a separate layer built by consumers on top of these modules — out of scope here by design.
- **Not SDLC workflows.** Story implementation, review flows, and delivery pipelines live above the constitution.
- **Not complete by ambition.** The module set grows only when consumer friction recurs; a module for a failure nobody has hit is the failure.

<a id="i6"></a>
## Success criteria

A new project adopts the constitution in under an hour. A gate's error message teaches the fix without a human explaining it. A harness change lands with one yes. Nothing in a consumer repo needs editing when a module updates. And the kit's own history reads as evidence: every rule traceable to the friction that earned it.
