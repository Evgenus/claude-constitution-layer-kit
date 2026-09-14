---
id: module-spec-template
type: current-state
title: Module specification — template
status: active
---

# M<n> — `const-<aspect>`

*Template for a **module specification**: the pre-authoring document for one module, one file per module at `docs/modules/const-<aspect>.md`. A spec is the write-head for its module (kernel §2): `type: task-record`, `active` from the moment the module's rows exist in the matrix until `modules/const-<aspect>/MODULE.md` ships; then `inactive`, and deleted once nothing references it (kernel §1, lifecycle rule) — by that point its durable content lives in `MODULE.md`, the matrix, and `docs/decisions/`. A spec never restates the kernel (law 1) and never references a project (law 2). Every section is filled or says "none" with one line of reasoning. Open slots are marked inline as `[decide: <slot> — default <X> — stakes <level> — decider <who>]`; an authoring session derives its questions from these markers in document order, and a spec with no marker left is authoring-ready. Every list and table row carries a handle so one item can be cited without quoting it.*

Frontmatter of a spec (kernel §1 envelope; nothing more — the module name is the id, the handle is in the title):

```yaml
id: spec-const-<aspect>
type: task-record
title: M<n> — const-<aspect>
status: active
```

## 1. Failure pattern

One paragraph, concrete: what goes wrong without this module, in terms someone has observed — not a category name. If the pattern cannot be stated concretely, the module is not ready to have a spec. Then two labeled lines:

- **Class:** `accumulating` or `self-limiting`, with one line of reasoning. A module may be split honestly — name the accumulating slice and the self-limiting remainder.
- **Entry trigger:** when a consumer installs it. Accumulating: day-one. Self-limiting: the observed friction signal that earns it, stated so a consumer can recognize it.

## 2. Rows

The requirement set, and nothing else (law 4): every matrix row homed in this module, by handle. The row's one-line text lives in the matrix and is not repeated; this table carries the *reading* the row needs beyond its line — interpretation, boundary rulings, the part of a shared row this module owns.

| row | this module's reading |
|---|---|
| A<n>.<m> | … |

A row under a boundary test (marked † in the matrix) states which of the three tests is open — *one invariant? one enforcement moment? one lifecycle trigger?* — and which sibling takes the row if the boundary moves.

## 3. Decisions

Rulings already made that bind this module's authoring. Each is a record id in `docs/decisions/` or, below recorded stakes, the commit that noted it. Nothing is restated; the record holds the options and reasoning.

1. `<record-id>` — one line naming what it fixes for this module.

## 4. Invariant

Gate-bearing module: the one rule the module guarantees, in a single testable sentence built from kernel vocabulary and this spec's own definitions. Advisory-only module: no invariant is claimed; in its place, the numbered rule list, each rule labeled `advisory` in its own text.

## 5. Mechanism (rule-to-artifact)

The native-first walk — platform component > repo script > third-party tool > new infrastructure — one row per rule. Every step down from native names, in one clause, what the native option cannot do. This table becomes the Artifacts table of `MODULE.md`.

| rule | carrier | step-down reason |
|---|---|---|
| A<n>.<m> | hook (`<event>`, matcher `<m>`) + script · skill · command · agent | none, or the one clause |

Two fixed sub-slots:

- **Always-on content:** the exact lines a `SessionStart` hook prints, and their size in characters; or "none". This is the module's whole always-on budget.
- **Platform facts relied on:** each fact, the date it was verified against the official documentation, and what breaks if it changes. Nothing in this slot comes from memory.

## 6. Error messages

For every gate, the designed text: what failed, why the rule exists (one clause), the exact fix. Written here, reviewed like code, copied verbatim into the script at authoring.

1. `<gate>` — "…"

## 7. Dials

Namespace = plugin name (kernel §6). Every dial has a default and the module works with zero configuration. "none" when the module has no calibration surface beyond the territory map.

| dial | default | meaning |
|---|---|---|
| `<dial>` | `<value>` | one line |

## 8. Boundary examples

For every judgment boundary this module introduces: 3–4 contrastive pairs (violates / complies), numbered. The pairs are the definition; no abstract criteria. Pairs founded here move into the module's skill at authoring; the project's own pairs arrive through dials.

## 9. Enforcement honesty

Per artifact: `gate` (deterministic, red = fix) or `advisory` (judgment-shaping), declared, never blurred (law 5). A deterministic check whose blocking is a dial is a `gate` with its severity dial named — the check is still deterministic. Then **honest limits**: every path the gate does not see (a tool that bypasses the hook's event, a moment outside its trigger), each with its backstop.

## 10. Acceptance

Per gate: the red→green fixture — one input that fails without the check and passes with it — and its path under `modules/const-<aspect>/tests/` (law 7). Per advisory rule: the boundary examples stand. Each item labeled by verification kind: `fixture` (bare temp repo), `live` (a consumer project, plugin loaded from this repo), `review` (the human, at the one yes).

## 11. Siblings

First the kernel-alone statement: what the module does on a bare repository with the kernel and nothing else (law 3). Then each optional enhancement as "when `const-<x>` is installed, …". A concept this module needs from a sibling is a kernel candidate, raised as a `process` decision, never coupled.

## 12. Sequencing

- **Depends on:** the kernel sections used, and the platform facts above — nothing else.
- **Enters:** the rollout phase or the entry trigger from §1.
- **Governs once installed:** what later authoring runs under it — the module's own contribution to the bootstrap.

## 13. Deferred

What this module deliberately does not ship yet, each with the friction signal that would earn it. Nothing here is a hidden requirement: a deferred item has no matrix row, or its row is marked deferred there.

---

# Closing a spec

At module close (kernel §2, task close is a single act): `MODULE.md` is filled from §§1, 4–10 and cites its rows; §5's platform facts land in `MODULE.md` or `INSTALL.md`; §3 already lives in `docs/decisions/`; §12 and §13 return to the rollout plan and the matrix. Then the spec is set `inactive` and deleted in the same commit unless something still references it. Amending a shipped module starts a new spec from this template, scoped to the delta.
