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
