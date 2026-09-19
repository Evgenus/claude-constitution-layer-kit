---
id: constitution-rollout-plan
type: task-record
title: Constitution Rollout — phases
status: active
---

# Constitution Rollout — Actionable Plan

*The kit's own write-head ([kernel §2](../kernel/CONVENTIONS.md#k2)): the phases and their sequence, `active` while a phase remains, `inactive` when Phase E is reached. What a module must implement lives in [constitution-requirements](requirements.md), the traceability matrix and module specifications; nothing here is a requirement or a ruling.*

*Working rule throughout: author against real files, extract when proven, install everywhere else. No module is designed against imagined content.*

## Phase A — Kit as consumer zero: the document-shaped accumulating modules (~1 week)

*Accumulating failures compound with every unguarded artifact, so their modules exist before the first consumer document does (decision [dec-0006-accumulating-set-first](decisions/dec-0006-accumulating-set-first.md)). Four of the six have their objects in this repository already — envelopes, decision records, cross-references, a numbered kind — and are authored here against real files.*

1. Rule on how territories are declared — done: decisions [dec-0007-territory-declaration](decisions/dec-0007-territory-declaration.md) and [dec-0008-policies-by-location](decisions/dec-0008-policies-by-location.md), applied to [kernel §3](../kernel/CONVENTIONS.md#k3) and [kernel §6](../kernel/CONVENTIONS.md#k6).
2. Make the kit consumer zero: a root policy and one policy per document kind under `docs/policies/` — kernel, intent page, decision records, research comparisons, module documents (decision [dec-0011-one-policy-per-kind](decisions/dec-0011-one-policy-per-kind.md)); `constitution.yaml` at the kit root points at the root policy and carries each policy's territory under its id.
3. Author, in this order, each from the template and each proven twice — fixtures on a bare temp repo ([A12.1](requirements.md#a12-1)–[A12.2](requirements.md#a12-2) by hand) and live in this repository with the plugin loaded via `--plugin-dir`: [`const-meta-types`](requirements.md#const-meta-types), [`const-decision-records`](requirements.md#const-decision-records), [`const-catalogs`](requirements.md#const-catalogs), [`const-referencing`](requirements.md#const-referencing). One `process` record and one human yes per module; manifest `0.0.x` while any marker remains.
   - [`const-meta-types`](requirements.md#const-meta-types) — done 2026-09-18: authored at manifest `0.0.1`, fixtures and kit-live proof green, validated fresh-context twice, records [dec-0019-meta-types-module-rulings](decisions/dec-0019-meta-types-module-rulings.md) and [dec-0020-gate-script-rules](decisions/dec-0020-gate-script-rules.md), the yes given; its consumer-live proof is Phase B step 5.
   - [`const-decision-records`](requirements.md#const-decision-records) — authored 2026-09-18 and 2026-09-19 at manifest `0.0.1`: fixtures and kit-live proofs green, validated fresh-context, record [dec-0024-decision-records-module-rulings](decisions/dec-0024-decision-records-module-rulings.md); its consumer-live proof is Phase B step 5.
   - Shared gate code — extracted 2026-09-19 at the end of the second module's authoring, from the forced edits its copies needed (decisions [dec-0023-shared-gate-code-at-module-two](decisions/dec-0023-shared-gate-code-at-module-two.md) and [dec-0025-shared-gate-code-linked](decisions/dec-0025-shared-gate-code-linked.md), which holds that evidence): one source under `shared/`, described in [kit-shared-gate-code](../shared/GATE.md), each module linked to it, `scripts/check-shared-links.py` as the kit gate. The next module links from its first commit.
4. Review each against the template; fix the template where it failed you. Log every session annoyance as a commit note — the friction signal that earns [`const-questions`](requirements.md#const-questions) and [`const-interaction`](requirements.md#const-interaction).

## Phase B — Bootstrap the consumer project (~1 hour)

5. In the project: copy `kernel/` to `docs/constitution/`; a root policy and one policy per document kind under `docs/policies/` — at least a kernel policy for `docs/constitution/**` and a decision-record policy for `docs/decisions/**` (written for the project; the kit's policies under `docs/policies/` are examples to read, not to copy — policies are consumer content, never kernel, never module); `constitution.yaml` at the root with `root_policy` and each policy's territory under its id, `docs/policies/**` for the root ([kernel §3](../kernel/CONVENTIONS.md#k3)); the four Phase A modules loaded from the kit path from the first commit, so no governed document is ever written unguarded. This is each module's consumer-live proof, the second stage of [CLAUDE.md](../CLAUDE.md) step 5: run every module's fixtures against the project and log findings as fixes with a version bump (decision [dec-0015-pre-module-audit-rulings](decisions/dec-0015-pre-module-audit-rulings.md)).
6. Decision record #1 — "Adopt constitution kernel", `stakes: process`, `decider: <you>`, numbered by [`const-catalogs`](requirements.md#const-catalogs) — merged with your one yes: the fast lane's first run.
7. Commit each step with honest messages.

## Phase C — The consumer's first week: the remaining accumulating modules

8. [`const-locations`](requirements.md#const-locations) before the second territory is claimed; [`const-task-close`](requirements.md#const-task-close) before the first task closes against code. Authored in the kit, proven on fixtures and live in the project — against ten documents, not a thousand. Their dials (territory map, coverage map) grow with the project; the modules never wait for calibration.
9. Self-limiting modules ([`const-questions`](requirements.md#const-questions) through [`const-doc-budgets`](requirements.md#const-doc-budgets)) wait for their friction signal. Until [`const-interaction`](requirements.md#const-interaction) ships, the project's `CLAUDE.md` carries a copy of the kit's session-conduct block, labeled manual and version-drifting — the fallback that module's spec names.

## Phase D — Publish (~1 hour, only after the six are green)

10. A remote with protected main and a branch-per-change PR flow: the kit's yes moves from the commit message to PR approval (decision [dec-0016-yes-on-the-change](decisions/dec-0016-yes-on-the-change.md)). Then `profiles/`, `.claude-plugin/marketplace.json` (verify marketplace shape and private-repo team access in-session), CI wiring the [aspect A12](requirements.md#a12) gates — bare-repo install, kernel+single-module run, project-reference grep — and validation of the kit's own `constitution.yaml` against the kernel's dials schema. Modules go to `0.1.0`.
11. Switch the project from path load to marketplace install. From here every project is a consumer; all module development stays in the kit repo (`process` stakes, one human yes per change).

## Phase E — Steady state

Friction in a project → commit note → recurring notes on one theme → module authored/amended in the kit (`process` stakes, one human yes) → version bump → projects update. Never: a module for a failure no one has hit; a territory with no policy behind it (a territory precedes its first document, never its policy). Onboarding = clone, install, read one page of `CONVENTIONS.md`.
