---
id: dec-0015-pre-module-audit-rulings
type: task-record
title: Procedure rulings from the pre-module audit of 2026-09-18
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Procedure rulings from the pre-module audit of 2026-09-18

## Context

Before the first module, the kit's governing documents were audited against each other and against the module routine on 2026-09-18. Kernel-touching findings got their own records ([dec-0012-record-references-are-provenance](dec-0012-record-references-are-provenance.md), [dec-0013-non-authoritative-status](dec-0013-non-authoritative-status.md), [dec-0014-territory-dialect](dec-0014-territory-dialect.md)). The procedure findings — rulings on how the kit works, each a sentence or two in `CLAUDE.md`, the template, or the plan — are gathered here, one section per item, decided one at a time in chat. The record is `active` while items remain open and is set `inactive` when the last one is applied ([kernel §5](../../kernel/CONVENTIONS.md#k5)).

## 1. Runtime for gate scripts

The template skeleton was bash, the [`const-meta-types`](../requirements.md#const-meta-types) spec said PyYAML, the kernel was silent. Every gate that reads the envelope or the dials file parses YAML, a dependency on the consumer's machine.

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

[`const-meta-types`](../requirements.md#const-meta-types) and [`const-locations`](../requirements.md#const-locations) fired on the same hook, at the same moment, over the same territory, and both needed the [kernel §3](../../kernel/CONVENTIONS.md#k3) lookup — root policy, documents in its territory, union of their territories. [Law 3 of CLAUDE.md](../../CLAUDE.md#law-3) forbids sharing code and the kernel ships no machinery. The matrix flagged the boundary with †.

- **A. Move [A2.3](../requirements.md#a2-3) into [`const-meta-types`](../requirements.md#const-meta-types).** One write-time guard of claimed territory: valid envelope and exactly one policy. [`const-locations`](../requirements.md#const-locations) keeps creation and the new-kind procedure, advisory.
  - **Pros:** the lookup is written once for write time; both modules pass the three boundary tests; kernel plus [`const-locations`](../requirements.md#const-locations) alone still works.
  - **Cons:** [`const-meta-types`](../requirements.md#const-meta-types) grows to three rows and four fixture classes; [`const-catalogs`](../requirements.md#const-catalogs) still writes its own lookup.
- **B. Merge [`const-meta-types`](../requirements.md#const-meta-types) and [`const-locations`](../requirements.md#const-locations) fully.**
  - **Pros:** one plugin for the write-time and creation surface.
  - **Cons:** the first module carries the undesigned creation-from-template mechanism; creation and write are different moments.
- **C. Keep the plan, a kernel reference library vendored into [`const-meta-types`](../requirements.md#const-meta-types), [`const-locations`](../requirements.md#const-locations), [`const-catalogs`](../requirements.md#const-catalogs)**, with an admission rule (implements a kernel section literally; two or more modules need it) and a copy gate.
  - **Pros:** one invariant per module; one source for the resolver.
  - **Cons:** two hooks parse one write; library, INTENT amendment and copy gate before [`const-meta-types`](../requirements.md#const-meta-types).
- **D. Defer to [`const-meta-types`](../requirements.md#const-meta-types)'s authoring.**
  - **Pros:** evidence from writing the lookup once.
  - **Cons:** [`const-meta-types`](../requirements.md#const-meta-types)'s row set unknown, so its research round cannot be scoped.
- **E. Decide A or C now; extract the library when [`const-catalogs`](../requirements.md#const-catalogs) is the second reader.**
  - **Pros:** no library before a second consumer proves its shape.
  - **Cons:** [`const-meta-types`](../requirements.md#const-meta-types)'s resolver written twice.
- **F. Kernel library as a pip package into system Python.**
  - **Pros:** one install, PyYAML included.
  - **Cons:** gate logic depends on machine state, so two developers can get different verdicts on one file; version skew across modules and machines; PEP 668 blocks the system install on Debian, Ubuntu and Homebrew.
- **G. Keep the plan, each module reimplements the lookup by hand.**
  - **Pros:** nothing new before [`const-meta-types`](../requirements.md#const-meta-types).
  - **Cons:** three drifting copies.
- **H. Move [A1.4](../requirements.md#a1-4) into [`const-locations`](../requirements.md#const-locations) instead**, [`const-meta-types`](../requirements.md#const-meta-types) keeps the type-choice skill only.
  - **Pros:** the envelope rule applies only to governed documents, so the check sits where the concept lives; [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) splits by module.
  - **Cons:** the first module authored becomes [`const-locations`](../requirements.md#const-locations) with the undesigned creation mechanism attached, or with rows marked deferred; [`const-meta-types`](../requirements.md#const-meta-types) is a one-skill plugin.

Recommendation A with E's terms: A and H are symmetric, and A keeps the undesigned piece in the module authored later. Chosen A with E by the decider in chat on 2026-09-18.

Rulings: (a) [A2.3](../requirements.md#a2-3) is [`const-meta-types`](../requirements.md#const-meta-types)'s; [`const-meta-types`](../requirements.md#const-meta-types) guards claimed territory at write time, envelope and resolution in one script, with a repository-scan mode as backstop; [`const-locations`](../requirements.md#const-locations) is advisory creation and claims no gate. (b) No shared library before a second reader exists. When [`const-catalogs`](../requirements.md#const-catalogs) needs the lookup, a kernel reference implementation is extracted, vendored into each module with a kit gate on copy equality, admitted only for functions that implement a kernel section literally and that two or more modules need; [INTENT.md](../../INTENT.md) is amended then. A pip package is the delivery for readers outside plugins, if one appears. Applied: matrix intro and row [A2.3](../requirements.md#a2-3); [`const-meta-types`](../requirements.md#const-meta-types) and [`const-locations`](../requirements.md#const-locations) spec text.

## 3. Live proof in a consumer project before a consumer exists

[CLAUDE.md](../../CLAUDE.md) step 5 requires two live proofs before the yes, in this repository and in a consumer project; the consumer is born in Phase B, after the four Phase A modules.

- **A. Two-stage proof, one yes.** The record and the yes follow the kit-live proof; the consumer-live proof is a named step of Phase B, and a finding there is a fix with a version bump.
  - **Pros:** matches the sequence of [dec-0006-accumulating-set-first](dec-0006-accumulating-set-first.md); drafts stay `0.0.x` until Phase D, so the yes accepts a draft; the consumer proof still precedes publication.
  - **Cons:** a yes can be followed by a rework.
- **B. Hold every yes until Phase B.**
  - **Pros:** one yes covers both proofs.
  - **Cons:** the consumer is born on four unapproved modules; Phase A closes nothing; the fast lane exists to avoid this queue.
- **C. Drop the consumer-live requirement for document-shaped modules.**
  - **Pros:** simplest wording.
  - **Cons:** the kit is an unusual consumer, no code and no tasks, so a leak toward kit habits surfaces only in a real project.
- **D. A synthetic consumer for the second proof.**
  - **Pros:** both proofs in Phase A.
  - **Cons:** rejected in accumulating-set-first; the bare-repo fixtures are that proof already.

Recommendation A. Chosen A by the decider in chat on 2026-09-18. Applied: [CLAUDE.md](../../CLAUDE.md) step 5; Phase B step 5 of `docs/rollout-plan.md`.

## 4. Where a module's description lives after it moves into `MODULE.md`

[dec-0003-module-spec-kind](dec-0003-module-spec-kind.md) moves each plan description into the module's draft `MODULE.md`; reference form R7 of [dec-0005-reference-forms](dec-0005-reference-forms.md) sends every module cite to the plan's anchor, and eleven records link there.

- **A. The plan keeps a one-line stub per module under the same anchor**, linking the module's `MODULE.md`; the anchor stays the canonical handle, authored or not.
  - **Pros:** no link migration ever; one stable handle per module; authored and unauthored modules cited alike.
  - **Cons:** a one-line stub is a second place, with nothing in it to drift.
- **B. Migrate every link to `MODULE.md` at the move; delete the plan section.**
  - **Pros:** one place.
  - **Cons:** eleven records edited per move; a changing draft as link target; two forms coexist while modules remain unauthored.
- **C. Descriptions stay in the plan; `MODULE.md` links to them.**
  - **Pros:** nothing moves.
  - **Cons:** reverses module-spec-kind; a module document without its own description fails the template.
- **D. Move at publication, not at draft.**
  - **Pros:** the plan stays complete during authoring.
  - **Cons:** two descriptions during the draft period, the drift the kernel calls a defect; the stub question returns at publication.

Recommendation A. Chosen A by the decider in chat on 2026-09-18. Applied: the module-specifications header of `docs/requirements.md`; [CLAUDE.md](../../CLAUDE.md) step 3.

## 5. The rollout plan was ungoverned and mixed

`docs/rollout-plan.md` was the requirements source of every module by [law 4 of CLAUDE.md](../../CLAUDE.md#law-4), yet carried no envelope, sat in no territory, and mixed normative content (the matrix, the module specifications) with intent not yet real (the phases), which [kernel §2](../../kernel/CONVENTIONS.md#k2) keeps out of standing documents.

- **A. Claim it whole as `current-state`, phases tolerated as a roadmap section.**
  - **Pros:** one policy, no move.
  - **Cons:** a standing document carrying unrealized intent; the kit's gate module would look away from the kit's central file.
- **B. Leave it ungoverned and say so.**
  - **Pros:** zero cost.
  - **Cons:** consumer zero exempts its most important document; [law 4 of CLAUDE.md](../../CLAUDE.md#law-4) rests on nothing the kernel expresses.
- **C. Split by normative content.** Matrix and specifications become `docs/requirements.md`, `current-state`, under a requirements policy; the phases stay in `docs/rollout-plan.md` as an `active` task-record under a rollout-plan policy. Anchors keep their keys; links are rewritten in one commit under the migration carve-out of [kernel §5](../../kernel/CONVENTIONS.md#k5).
  - **Pros:** each half has one meta-type and one lifecycle; the split is done on a real file before the first module exists.
  - **Cons:** two new policies; a large mechanical diff; two file names to learn.
- **D. Split as C, phases as a decision record.**
  - **Pros:** no rollout-plan policy.
  - **Cons:** a schedule is not a ruling; a record with no choice is the manufactured shape the kernel forbids.

Recommendation C. Chosen C by the decider in chat on 2026-09-18. Applied: the split; policies [plc-0007-requirements](../policies/plc-0007-requirements.md) and [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md), their territories in `constitution.yaml`; every anchored link migrated from `rollout-plan.md#` to `requirements.md#` across records, `CLAUDE.md`, `INTENT.md`, `README.md`, the template, and `scripts/check-references.sh`, whose `M<n>` exemption follows the specifications; bare mentions of the old path in inactive records are left as evidence of their moment, since nothing resolves through them. Found in passing and repaired in the preceding commit: the intent policy had reused the id of [INTENT.md](../../INTENT.md); it is now [plc-0003-intent-page](../policies/plc-0003-intent-page.md).

## 6. What the portability grep looks for

[Requirement A12.1](../requirements.md#a12-1) named a project-reference grep as half of the portability gate without defining a project reference; a list of consumer names cannot be the definition, being project content by [law 2 of CLAUDE.md](../../CLAUDE.md#law-2). The check arrives with CI in Phase D, but [CLAUDE.md](../../CLAUDE.md) step 5 runs it by hand from the first module on.

- **A. Absolute paths and links only**, as `scripts/check-references.sh` already does for kit documents.
  - **Pros:** zero false positives; implemented.
  - **Cons:** misses the leak that matters, a repository-relative path written into a skill or script.
- **B. Drop the grep; the bare-repo defaults-only run is the whole gate.**
  - **Pros:** no heuristic.
  - **Cons:** a hardcoded path that only acts when it exists passes a bare repo untouched.
- **C. Literal-path heuristic, no denylist.** Any absolute path, `file:` link, `~/`, or repository-relative path literal not prefixed by `${CLAUDE_PLUGIN_ROOT}` and not a public URL is a finding; the one repository path a module may name is `constitution.yaml`; no exemption marker.
  - **Pros:** targets the real leak class without naming any project; enforces the discipline the kernel's portability rule states.
  - **Cons:** noise on in-plugin paths in prose, resolved by writing them `${CLAUDE_PLUGIN_ROOT}`-relative or in words; a heuristic, so the bare-repo run stays the gate of record.
- **D. C plus an allowlist of kit-defined names.**
  - **Pros:** less noise.
  - **Cons:** the allowlist becomes the exemption marker C refuses.

Recommendation C. Chosen C by the decider in chat on 2026-09-18. Applied: [requirement A12.1](../requirements.md#a12-1); [CLAUDE.md](../../CLAUDE.md) step 5 names the by-hand form.

## 7. Severity posture of write-time gates

[`const-catalogs`](../requirements.md#const-catalogs) declared a block-or-warn dial for its write-time hook; [`const-meta-types`](../requirements.md#const-meta-types) declared none. A consumer adopting on a repository with legacy documents needs to see findings before every write is blocked, and only one of the two write-time gates offered it.

- **A. Template convention: every write-time gate exposes `severity`, `block` or `warn`, default `block`**; the scan mode ignores it.
  - **Pros:** one word, one meaning; an adoption path from the first module; the default keeps the gate a gate.
  - **Cons:** a dial for the first module before a consumer asked, though the same dial was already ruled for `const-catalogs`.
- **B. No dial for the first module.**
  - **Pros:** nothing added.
  - **Cons:** two postures; the first consumer meets the stricter one on the module that touches every document.
- **C. Remove the catalogs dial; write-time gates always block.**
  - **Pros:** no severity anywhere.
  - **Cons:** reverses part of [dec-0004-catalogs-module](dec-0004-catalogs-module.md); no adoption path for a legacy repository.
- **D. A kernel-owned severity key for all gates.**
  - **Pros:** one migration switch.
  - **Cons:** a kernel key for a module concern; a switch silencing every gate is the vacuous green the template forbids.

Recommendation A. Chosen A by the decider in chat on 2026-09-18. Applied: [template §7](../../module-template/MODULE.md#t7) and [§9](../../module-template/MODULE.md#t9); the `const-meta-types` specification's dials line.

## Close

Every item of the audit that needed a ruling is applied: items 1, 2, 13, 17 and 18 in their own records ([dec-0013](dec-0013-non-authoritative-status.md), [dec-0014](dec-0014-territory-dialect.md), [dec-0016](dec-0016-yes-on-the-change.md), [dec-0017](dec-0017-records-numbered-now.md), [dec-0018](dec-0018-dials-schema.md)), the procedure items in sections 1 to 7 above, the routine repairs in commits 8dc6ce6 and 18d2cc8. The remaining audit items were design slots of the first module (hook coverage, platform facts) and are its `MODULE.md` sections, not rulings. This record is set `inactive` with this section.
