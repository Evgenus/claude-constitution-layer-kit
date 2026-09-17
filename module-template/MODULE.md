---
id: module-const-<aspect>
type: current-state
title: M<n> — const-<aspect>
status: active
---

# MODULE.md — `const-<aspect>`

*Template. Every constitution module is a Claude Code plugin with this document at its root, and this document is the module's **description** from the first draft on — there is no separate specification kind (decision [module-spec-kind](../docs/decisions/module-spec-kind.md)). A draft module carries manifest version `0.0.x`; it is published at `0.1.0` or higher, once every gate has its fixture and no open marker is left. Open slots in a draft are written inline as `[decide: <slot> — default <X> — stakes <level> — decider <who>]`; an authoring session derives its questions from these markers in document order, and a published module carries none.*

*Fill every section; a section that does not apply says "none" with one line of reasoning. The module depends on the kernel (`CONVENTIONS.md` + schemas) and on nothing else — if it seems to need a sibling module, the shared concept belongs in the kernel; raise that instead of coupling. **No file in the module references a project directly** (paths, names, values): project specifics arrive only through the dials namespace, and the module must install and operate on an empty repository using its defaults ([kernel §6](../kernel/CONVENTIONS.md#k6), portability rule). References to sibling modules are permitted **only as optional enhancements** ("when module `const-x` is installed, ..."); every rule must be executable with the kernel alone — the test: **kernel + this module on an empty repository is a functioning installation.** Every list and table row carries a handle so one item can be cited without quoting it.*

<a id="t1"></a>
## 1. Purpose

One paragraph: the failure pattern this module prevents, stated concretely — in terms someone has observed, not a category name. If the failure pattern cannot be named, the module is not ready to exist.

<a id="t2"></a>
## 2. Failure class

`accumulating` or `self-limiting`, with one line of reasoning; a module may be split honestly — name the accumulating slice and the self-limiting remainder. Then the **entry trigger**: accumulating modules belong in every project's day-one install set; a self-limiting module names the observed friction signal that earns its installation, stated so a consumer can recognize it.

<a id="t3"></a>
## 3. Rows

The requirement set, and nothing else ([law 4 of CLAUDE.md](../CLAUDE.md#law-4)): every matrix row homed in this module, by handle. The row's one-line text lives in the matrix and is not repeated; the table carries the *reading* the row needs beyond its line — interpretation, boundary rulings, the part of a shared row this module owns. A row under a boundary test (marked † in the matrix) states which of the three tests is open — *one invariant? one enforcement moment? one lifecycle trigger?* — and which sibling takes the row if the boundary moves.

| row | this module's reading |
|---|---|
| A<n>.<m> | … |

<a id="t4"></a>
## 4. Decisions

Rulings that bind this module, each a record id in `docs/decisions/` or, below recorded stakes, the commit that noted it. Nothing is restated; the record holds the options and reasoning.

1. `<record-id>` — one line naming what it fixes here.

<a id="t5"></a>
## 5. Invariant

The one rule the module guarantees, stated in a single testable sentence built only from kernel vocabulary and this module's own definitions. An advisory-only module claims no invariant; in its place stands the numbered rule list, each rule labeled `advisory` in its own text.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

What this plugin ships and what each part carries — only components the module actually uses exist. Native-first: platform component > repo script > third-party tool > new infrastructure; every step down from a platform component names, in one clause, what the native option cannot do.

| component | path | carries |
|---|---|---|
| skill | `skills/<name>/SKILL.md` | the procedure, loaded when the activity occurs |
| hook | `hooks/hooks.json` + `scripts/` | deterministic enforcement of the invariant; or, as a `SessionStart` hook printing rules to stdout, the always-on carrier for advisory content — declared `advisory`, never `gate` |
| command | `commands/<name>.md` | only for acts a human deliberately initiates — name the scenario where a human actually types it, or delete this row |
| agent | `agents/<name>.md` | only for a genuine delegation boundary |
| script | `scripts/<name>` | checks and generators; all paths via `${CLAUDE_PLUGIN_ROOT}` |
| install note | `INSTALL.md` | at most one pointer line for the project's own `CLAUDE.md`, for discoverability only. Always-on rules ship via a `SessionStart` hook (see hook row), never via a pointer or a plugin-root `CLAUDE.md` (not loaded); a copy-into-CLAUDE.md fallback may be offered, labeled as manual and version-drifting |

Two fixed sub-slots follow the table:

- **Always-on content:** the exact lines the `SessionStart` hook prints and their size in characters; or "none". This is the module's whole always-on budget.
- **Platform facts relied on:** each fact, the date it was verified against the official documentation, and what breaks if it changes. Nothing in this slot comes from memory; the [native surface map](../docs/research/native-surface-map.md) is the starting list, never the evidence.
- **Research inputs:** for each mechanism, the dated comparison in [`docs/research/`](../docs/research/README.md) it rests on, and whether the matrix's recommended enforcement for the row was confirmed or overturned here. A mechanism no comparison covers gets one written first, in the same shape (decision [module-routine-validation-and-inputs](../docs/decisions/module-routine-validation-and-inputs.md)).

Every check's **error message** is written here as part of the design — it is the highest-bandwidth channel for teaching an agent mid-session: state what failed, why the rule exists (one clause), and the exact fix. Reviewed like code; copied verbatim into the script.

**Installed components reference nothing in the kit.** A skill, hook, script, command, agent, error text, or install note never cites the rollout plan, a matrix row, a decision record, a research comparison, or this document: consumers install the module without the kit, so every such reference dangles there. Rules are stated in those components in plain words; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

The module's calibration surface. Namespace = plugin name in the project's `constitution.yaml`; every dial has a default; the module works with zero configuration.

| dial | default | meaning |
|---|---|---|
| `<dial>` | `<value>` | one line |

<a id="t8"></a>
## 8. Boundary examples

For every judgment-based boundary the module introduces (including its slice of the routine/product stakes line, if any): 3–4 contrastive pairs (violates / complies), numbered. The examples are the definition; no abstract criteria. The project's own pairs arrive through dials.

<a id="t9"></a>
## 9. Enforcement honesty

For each artifact: `gate` (deterministic — hook or script, red means fix) or `advisory` (judgment-shaping — skill prose, suggestions in review). Nothing advisory is dressed as a gate. A deterministic check whose blocking is a dial is a `gate` with its severity dial named — the check is still deterministic. Then the **honest limits**: every path the gate does not see (a tool that bypasses the hook's event, a moment outside its trigger), each with its backstop.

**Exit-code contract** for every check: a finding (the repository is wrong) and a configuration failure (the checker is broken, a pinned tool is missing, the invocation is malformed) are distinct exit codes with distinct messages, so a reader never mistakes one for the other. A missing tool is loud, never a silent pass; a check that could not run reports that it could not run.

<a id="t10"></a>
## 10. Acceptance

For each gate: the red→green fixture proving it (a fixture that fails without the check, passes with it) and its path under `tests/` ([law 7 of CLAUDE.md](../CLAUDE.md#law-7)), plus one fixture showing the exit-code split of [§9](#t9) (a missing tool or malformed invocation exits differently from a finding). For each advisory rule: the boundary examples above stand as its acceptance. Each item labeled by verification kind: `fixture` (bare temp repo), `live` (a consumer project, plugin loaded from this repo), `review` (the human, at the one yes).

**Examined count.** Every check reports how many items it examined in its green and red output alike. Zero is a visible count, never a failure and never a silent green: a check that inspected nothing must say so, because a vacuous green read as permission is the failure this rule exists for.

<a id="t11"></a>
## 11. Siblings

**Depends on:** the kernel sections used — nothing else. Then the kernel-alone statement: what the module does on a bare repository with the kernel only. Then each optional enhancement as "when module `const-<x>` is installed, …". A concept this module needs from a sibling is a kernel candidate, raised as a `process` decision, never coupled.

<a id="t12"></a>
## 12. Deferred

What this module deliberately does not ship yet, each with the friction signal that would earn it. Nothing here is a hidden requirement: a deferred item has no matrix row, or its row is marked deferred there.

---

# Plugin skeleton

```
const-<aspect-name>/
├── .claude-plugin/
│   └── plugin.json          # manifest — the ONLY file inside .claude-plugin/; version 0.0.x while draft
├── MODULE.md                # this document, filled in
├── INSTALL.md               # install/uninstall notes; the one CLAUDE.md pointer line if any
├── skills/
│   └── <name>/SKILL.md      # optional
├── commands/<name>.md       # optional
├── agents/<name>.md         # optional
├── hooks/hooks.json         # optional
├── scripts/                 # optional; reference via ${CLAUDE_PLUGIN_ROOT}
└── tests/                   # one red→green fixture per gate ([law 7 of CLAUDE.md](../CLAUDE.md#law-7))
```

Kebab-case everywhere. Only plugin.json lives inside `.claude-plugin/`; every component directory sits at plugin root. Verify the manifest fields against the current plugin reference at authoring time.
