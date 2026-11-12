---
id: kit-intent
type: current-state
title: Constitution Kit — Intent
status: active
---

# Intent

<a id="i1"></a>
## What this repository is

This repository is a **portable constitution for AI-driven development with Claude Code**. It holds the rules, conventions, and mechanisms that govern how sessions produce documents, make decisions, and keep artifacts consistent. They are designed once, at the right level of abstraction. They are installed into any project, existing or new, when needed. Distribution unit: Claude Code plugins. Per-project cost of adoption: install, pick a profile, override a few dials. No design session, no re-derivation.

<a id="i2"></a>
## The problem it solves

Without a constitution, every project and every participant improvises. Documents have no declared authority, and decisions live in chat scrollback. Rulings are priced the same whether trivial or structural. Doc↔code drift has no owner, and session exhaust poses as knowledge. With a *heavyweight* constitution, the cure exceeds the disease. Ceremony has a fixed price for every doubt, and harness fixes are stuck behind the gates they fix. Hundreds of rules are built before the first product decision. This kit takes the middle on purpose. It is **a minimal semantic core, hard gates only where checks are deterministic, honesty everywhere else, and growth only from observed friction.**

<a id="i3"></a>
## Architecture

Three layers, strictly separated:

1. **Mechanical kernel — Claude Code itself.** Plugins, skills, hooks, agents, rules, settings are the component model. This repo never mirrors or wraps them. Wanting infrastructure the platform omitted is a design smell.
2. **Semantic kernel — `docs/constitution/CONVENTIONS.md` + schemas.** One page: document envelope, meta-types with lifecycle-aware precedence, governance binding by territory, stakes triage, decision-record shape, dials, naming. Only vocabulary two or more modules need. Nothing derivable from git (git owns history, ordering, authorship, supersession trails, archives).
3. **Modules — `modules/const-*`.** Invariant-shaped installation units, each a plugin: one invariant, one enforcement moment, one lifecycle trigger. Each depends on the kernel and nothing else. Each is project-blind, calibrated per project through a single `constitution.yaml`. Requirements are the traceability matrix in `docs/requirements.md` — a module implements exactly its rows. What every gate must have is written once, under `shared/`. It covers reading the hook event and the dials file, territories, the output log, the command line and its guard. It reaches a project as the Python package `constitution-layer-kit`, which each module's plugin imports and none carries. So a module still depends on the kernel and nothing else but that package (R7 of [dec-0099-shared-code-installed-as-a-pip-package](docs/decisions/dec-0099-shared-code-installed-as-a-pip-package.md#r7)).

**Consumer projects** hold the binding: territory maps, boundary examples, thresholds, deciders, and all governed content. The relationship is package-shaped: modules are versioned here, installed there. Friction flows back as commit notes, and recurring themes become kit changes.

<a id="i4"></a>
## Design principles (each earned, not assumed)

- <a id="p1"></a>**Native-first:** platform mechanisms > repo scripts > third-party tools > new infrastructure. Each step down names what the native option cannot do.
- <a id="p2"></a>**Invariant, not machinery:** what ships day one is the minimal deterministic guard against *accumulating* failures. Each unguarded artifact raises repair cost silently. *Self-limiting* frictions wait for observed pain. Governance sophistication is self-limiting by definition.
- <a id="p3"></a>**Ceremony scales with stakes:** routine → act and note in the commit; `process` → record plus one human yes; `product` → record; `architecture` → record plus review. The second is the fast lane: a harness fix never queues behind the gate it fixes. A constitution that prices a naming nit and a security ruling identically is defective.
- <a id="p4"></a>**Enforcement honesty:** gates are deterministic and red-means-fix; everything judgment-based is advisory and says so. Conversation is shaped, never gated.
- <a id="p5"></a>**Git-derivability razor:** no field, status, or record duplicates what the repository already expresses. The working tree holds current truth; history, ordering, and archives are git's.
- <a id="p6"></a>**Reconciliation model:** current-state documents are the truth reality converges to, aligned with code at every task close. In-progress tasks are the write-head. Divergence outside an active task's scope is a defect, and drift without commit-back is forbidden.
- <a id="p7"></a>**Boundaries by example:** judgment thresholds are defined by contrastive pairs, never abstract criteria.

<a id="i5"></a>
## What this repository is not

- **Not a project.** No project names, paths, content, or calibration anywhere ([kernel §6](docs/constitution/CONVENTIONS.md#k6)). The [aspect A12](docs/requirements.md#a12) gates the kit's CI runs hold this ([step 10 of the rollout plan](docs/rollout-plan.md#s10)). They are the bare-repo install of each module alone and the project-reference grep. The kit is still **consumer zero** of the document-shaped modules and of the kinds it creates. It is also consumer zero of the code territories its own current-state documents describe, and of its own session conduct. Its own records, intent page, and module documents sit under a claimed territory in a kit-root `constitution.yaml`. Its shared code, module scripts and git hooks sit under a coverage map there. Its sessions load its own modules as plugins from a committed settings file. So its own session conduct is the rules its guide keeps and the rules its modules carry. That is calibration of the kit, never of a project. The decisions are [dec-0006-accumulating-set-first](docs/decisions/dec-0006-accumulating-set-first.md), [dec-0035-locations-module-rulings](docs/decisions/dec-0035-locations-module-rulings.md) and [dec-0036-task-close-module-rulings](docs/decisions/dec-0036-task-close-module-rulings.md). They also include [dec-0041-questions-module-rulings](docs/decisions/dec-0041-questions-module-rulings.md) and [dec-0043-kit-plugins-through-project-settings](docs/decisions/dec-0043-kit-plugins-through-project-settings.md).
- **Not the knowledge layer.** Subject-shaped knowledge units, distillation, pointer generation, and staleness tracking are a separate layer built by consumers on top of these modules. They are out of scope here by design.
- **Not SDLC workflows.** Story implementation, review flows, and delivery pipelines live above the constitution.
- **Not complete by ambition.** The module set grows only when consumer friction recurs. A module for a failure nobody has hit is the failure.

<a id="i6"></a>
## Success criteria

A new project adopts the constitution in under an hour. A gate's error message teaches the fix without a human explaining it. A harness change lands with one yes. Nothing in a consumer repo needs editing when a module updates. And the kit's own history reads as evidence: every rule traceable to the friction that earned it.
