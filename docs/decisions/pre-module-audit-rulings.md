---
id: pre-module-audit-rulings
type: task-record
title: Procedure rulings from the pre-module audit of 2026-09-18
status: active
stakes: process
decider: Eugene Chernyshov
---

# Procedure rulings from the pre-module audit of 2026-09-18

## Context

Before the first module, the kit's governing documents were audited against each other and against the module routine on 2026-09-18. Kernel-touching findings got their own records ([record-references-are-provenance](record-references-are-provenance.md), [non-authoritative-status](non-authoritative-status.md), [territory-dialect](territory-dialect.md)). The procedure findings — rulings on how the kit works, each a sentence or two in `CLAUDE.md`, the template, or the plan — are gathered here, one section per item, decided one at a time in chat. The record is `active` while items remain open and is set `inactive` when the last one is applied ([kernel §5](../../kernel/CONVENTIONS.md#k5)).

## 1. Runtime for gate scripts

The template skeleton was bash, the [`const-meta-types`](../rollout-plan.md#const-meta-types) spec said PyYAML, the kernel was silent. Every gate that reads the envelope or the dials file parses YAML, a dependency on the consumer's machine.

- **A. Bash and git only**, a hand-rolled YAML subset for the dials file.
  - **Pros:** no dependency beyond git, already required.
  - **Cons:** legal YAML outside the subset yields a wrong answer, not an error — the silent failure [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) forbids dressing as a gate.
- **B. Python 3 with PyYAML**; missing interpreter or library exits 1 with the install command; gitignore matching through `git check-ignore`, verified at authoring.
  - **Pros:** a real parser; Python 3 ships on macOS and most Linux; the spec assumed it; the missing case is loud by design.
  - **Cons:** one `pip install` on a bare machine; Windows needs Python installed.
- **C. Bash with a pinned `yq`.**
  - **Pros:** no interpreter.
  - **Cons:** a third-party binary with two incompatible implementations, pinned per module.
- **D. Node.js**, Claude Code's own runtime.
  - **Pros:** present where Claude Code came from npm.
  - **Cons:** the native installer may ship without Node; an npm package is still a dependency.
- **E. Per module, no convention.**
  - **Pros:** nothing to rule.
  - **Cons:** three modules, three runtimes, one YAML parsed three ways.

Recommendation B. Chosen B by the decider in chat on 2026-09-18. Applied: [CLAUDE.md](../../CLAUDE.md) step 4 of "Developing a module"; [template §6](../../module-template/MODULE.md#t6) script row.

## 2. The meta-types/locations boundary and the shared territory lookup

[`const-meta-types`](../rollout-plan.md#const-meta-types) and [`const-locations`](../rollout-plan.md#const-locations) fired on the same hook, at the same moment, over the same territory, and both needed the [kernel §3](../../kernel/CONVENTIONS.md#k3) lookup — root policy, documents in its territory, union of their territories. [Law 3 of CLAUDE.md](../../CLAUDE.md#law-3) forbids sharing code and the kernel ships no machinery. The matrix flagged the boundary with †.

- **A. Move [A2.3](../rollout-plan.md#a2-3) into [`const-meta-types`](../rollout-plan.md#const-meta-types).** One write-time guard of claimed territory: valid envelope and exactly one policy. [`const-locations`](../rollout-plan.md#const-locations) keeps creation and the new-kind procedure, advisory.
  - **Pros:** the lookup is written once for write time; both modules pass the three boundary tests; kernel plus [`const-locations`](../rollout-plan.md#const-locations) alone still works.
  - **Cons:** [`const-meta-types`](../rollout-plan.md#const-meta-types) grows to three rows and four fixture classes; [`const-catalogs`](../rollout-plan.md#const-catalogs) still writes its own lookup.
- **B. Merge [`const-meta-types`](../rollout-plan.md#const-meta-types) and [`const-locations`](../rollout-plan.md#const-locations) fully.**
  - **Pros:** one plugin for the write-time and creation surface.
  - **Cons:** the first module carries the undesigned creation-from-template mechanism; creation and write are different moments.
- **C. Keep the plan, a kernel reference library vendored into [`const-meta-types`](../rollout-plan.md#const-meta-types), [`const-locations`](../rollout-plan.md#const-locations), [`const-catalogs`](../rollout-plan.md#const-catalogs)**, with an admission rule (implements a kernel section literally; two or more modules need it) and a copy gate.
  - **Pros:** one invariant per module; one source for the resolver.
  - **Cons:** two hooks parse one write; library, INTENT amendment and copy gate before [`const-meta-types`](../rollout-plan.md#const-meta-types).
- **D. Defer to [`const-meta-types`](../rollout-plan.md#const-meta-types)'s authoring.**
  - **Pros:** evidence from writing the lookup once.
  - **Cons:** [`const-meta-types`](../rollout-plan.md#const-meta-types)'s row set unknown, so its research round cannot be scoped.
- **E. Decide A or C now; extract the library when [`const-catalogs`](../rollout-plan.md#const-catalogs) is the second reader.**
  - **Pros:** no library before a second consumer proves its shape.
  - **Cons:** [`const-meta-types`](../rollout-plan.md#const-meta-types)'s resolver written twice.
- **F. Kernel library as a pip package into system Python.**
  - **Pros:** one install, PyYAML included.
  - **Cons:** gate logic depends on machine state, so two developers can get different verdicts on one file; version skew across modules and machines; PEP 668 blocks the system install on Debian, Ubuntu and Homebrew.
- **G. Keep the plan, each module reimplements the lookup by hand.**
  - **Pros:** nothing new before [`const-meta-types`](../rollout-plan.md#const-meta-types).
  - **Cons:** three drifting copies.
- **H. Move [A1.4](../rollout-plan.md#a1-4) into [`const-locations`](../rollout-plan.md#const-locations) instead**, [`const-meta-types`](../rollout-plan.md#const-meta-types) keeps the type-choice skill only.
  - **Pros:** the envelope rule applies only to governed documents, so the check sits where the concept lives; [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) splits by module.
  - **Cons:** the first module authored becomes [`const-locations`](../rollout-plan.md#const-locations) with the undesigned creation mechanism attached, or with rows marked deferred; [`const-meta-types`](../rollout-plan.md#const-meta-types) is a one-skill plugin.

Recommendation A with E's terms: A and H are symmetric, and A keeps the undesigned piece in the module authored later. Chosen A with E by the decider in chat on 2026-09-18.

Rulings: (a) [A2.3](../rollout-plan.md#a2-3) is [`const-meta-types`](../rollout-plan.md#const-meta-types)'s; [`const-meta-types`](../rollout-plan.md#const-meta-types) guards claimed territory at write time, envelope and resolution in one script, with a repository-scan mode as backstop; [`const-locations`](../rollout-plan.md#const-locations) is advisory creation and claims no gate. (b) No shared library before a second reader exists. When [`const-catalogs`](../rollout-plan.md#const-catalogs) needs the lookup, a kernel reference implementation is extracted, vendored into each module with a kit gate on copy equality, admitted only for functions that implement a kernel section literally and that two or more modules need; [INTENT.md](../../INTENT.md) is amended then. A pip package is the delivery for readers outside plugins, if one appears. Applied: matrix intro and row [A2.3](../rollout-plan.md#a2-3); [`const-meta-types`](../rollout-plan.md#const-meta-types) and [`const-locations`](../rollout-plan.md#const-locations) spec text.
