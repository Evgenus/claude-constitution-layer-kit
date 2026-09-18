---
id: dec-0014-territory-dialect
type: task-record
title: Territory patterns have a kernel-stated default dialect, gitignore, overridable by a kernel-owned key
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Territory patterns have a kernel-stated default dialect, gitignore, overridable by a kernel-owned key

## Context

[dec-0007-territory-declaration](dec-0007-territory-declaration.md) ruling 2 left the pattern dialect and overlap handling to the first module that reads the territory declarations. The pre-module audit of 2026-09-18 found the kit's own `constitution.yaml` already asserting gitignore-style globs, and three modules ([`const-meta-types`](../requirements.md#const-meta-types), [`const-locations`](../requirements.md#const-locations), [`const-catalogs`](../requirements.md#const-catalogs)) reading the same declarations: a dialect chosen per module lets two readers disagree about one path, and a consumer writing a territory finds no dialect in the kernel page. The [`const-meta-types`](../requirements.md#const-meta-types) spec names a Python script, whose `fnmatch` lets `*` cross `/` and has no `**`, so `modules/*/MODULE.md` would mean something else there. This record reverses ruling 2 of territory-declaration; it also supersedes the "one kernel-owned key" wording of [dec-0008-policies-by-location](dec-0008-policies-by-location.md) ruling 1, the file now having two.

## Options — the dialect

- **A. Rule it in the kernel: gitignore semantics.** [Kernel §6](../../kernel/CONVENTIONS.md#k6) states it in one sentence; overlaps need no extra rule, since two policies matching one path is already the multi-policy defect of [kernel §3](../../kernel/CONVENTIONS.md#k3).
  - **Pros:** one answer for every reader and every consumer, on the one page they read; git can evaluate the patterns itself, so no new dependency, subject to verification at authoring; the kit's dials file already assumes it.
  - **Cons:** reverses a standing ruling; the kernel gains a mechanical sentence.
- **B. Leave it to the first module, strip the comment from the dials file.**
  - **Pros:** follows the standing ruling.
  - **Cons:** the later readers copy the first module's choice with no kernel home for it, sibling coupling by convention; a consumer guesses.
- **C. Shell globs, `fnmatch` style.**
  - **Pros:** in every standard library.
  - **Cons:** `*` crosses `/` in some implementations; no `**` in POSIX; implementations disagree at the edges.
- **D. Regular expressions.**
  - **Pros:** unambiguous.
  - **Cons:** hostile to the humans who write territories.

Recommendation A. Chosen: A, as the **default** dialect only — the decider wants a project able to declare another.

## Options — where a project overrides the default

- **A. A `dialect` key in the root policy's namespace.**
  - **Pros:** one place; the root governs the policy layer whose territories these are; no second kernel-owned top-level key; readers already fetch the root's namespace first.
  - **Cons:** the kernel defines two keys of a policy namespace instead of one.
- **B. A second kernel-owned top-level key, `territory_dialect`.**
  - **Pros:** visible at the top of the file, beside `root_policy`.
  - **Cons:** breaks the "one kernel-owned key" wording settled in policies-by-location; reopens that debate for one value.
- **C. Wording only; each module documents the dialects it accepts.**
  - **Pros:** no key.
  - **Cons:** a per-module override, so readers can disagree — the failure the first ruling exists to prevent.

Recommendation A. Chosen: **B**, by the decider in chat on 2026-09-18, against the recommendation. The session's objection — a second top-level key reopens the one-key ruling — is recorded here; the decider's reading is that the dialect is a property of the whole file, not of one policy.

## Rulings carried

1. `constitution.yaml` has two kernel-owned keys: `root_policy` and the optional `territory_dialect`. Every territory in the file is read in the declared dialect.
2. The default dialect is `gitignore`: `.gitignore` syntax evaluated against paths relative to the repository root, `**` crossing directories and `*` not. A reader that does not support the declared dialect reports a configuration failure, never a silent pass.
3. Overlap is not a dialect concern: two territories matching one path is the kernel's multi-policy defect.

## Applied in the same commit

- [Kernel §3](../../kernel/CONVENTIONS.md#k3): "one kernel-owned key" wording dropped. [Kernel §6](../../kernel/CONVENTIONS.md#k6): the key in the example, the dialect paragraph, the read set of a module.
- `constitution.yaml`: comment names the default; the kit declares no key, proving the default path.
- [requirement A2.6](../requirements.md#a2-6): the optional key joins the declarations.
