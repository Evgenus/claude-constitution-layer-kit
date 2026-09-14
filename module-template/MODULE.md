# MODULE.md — <const-aspect-name>

*Template. Every constitution module is a Claude Code plugin with this document at its root. Fill every section; a section that does not apply says "none" with one line of reasoning. The module depends on the kernel (`CONVENTIONS.md` + schemas) and on nothing else — if it seems to need a sibling module, the shared concept belongs in the kernel; raise that instead of coupling. **No file in the module references a project directly** (paths, names, values): project specifics arrive only through the dials namespace, and the module must install and operate on an empty repository using its defaults (kernel §6, portability rule). References to sibling modules are permitted **only as optional enhancements** ("when `const-x` is installed, ..."); every rule must be executable with the kernel alone — the test: **kernel + this module on an empty repository is a functioning installation.***

## Purpose

One paragraph: the failure pattern this module prevents, stated concretely. If the failure pattern cannot be named, the module is not ready to exist.

## Failure class

`accumulating` or `self-limiting`, with one line of reasoning. Accumulating modules belong in every project's day-one install set; self-limiting modules are installed when their friction is observed.

## Invariant

The one rule the module guarantees, stated in a single testable sentence built only from kernel vocabulary and this module's own definitions.

## Artifacts (rule-to-artifact mapping)

What this plugin ships and what each part carries — only components the module actually uses exist:

| component | path | carries |
|---|---|---|
| skill | `skills/<name>/SKILL.md` | the procedure, loaded when the activity occurs |
| hook | `hooks/hooks.json` + `scripts/` | deterministic enforcement of the invariant; or, as a `SessionStart` hook printing rules to stdout, the always-on carrier for advisory content — declared `advisory`, never `gate` |
| command | `commands/<name>.md` | only for acts a human deliberately initiates — name the scenario where a human actually types it, or delete this row |
| agent | `agents/<name>.md` | only for a genuine delegation boundary |
| script | `scripts/<name>` | checks and generators; all paths via `${CLAUDE_PLUGIN_ROOT}` |
| install note | `INSTALL.md` | at most one pointer line for the project's own `CLAUDE.md`, for discoverability only. Always-on rules ship via a `SessionStart` hook (see hook row), never via a pointer or a plugin-root `CLAUDE.md` (not loaded); a copy-into-CLAUDE.md fallback may be offered, labeled as manual and version-drifting |

Every check's **error message** is written here as part of the design — it is the highest-bandwidth channel for teaching an agent mid-session: state what failed, why the rule exists (one clause), and the exact fix.

## Dials

The module's calibration surface. Namespace = plugin name in the project's `constitution.yaml`; every dial has a default; the module works with zero configuration.

| dial | default | meaning |
|---|---|---|
| `<dial>` | `<value>` | one line |

## Boundary examples

For every judgment-based boundary the module introduces (including its slice of the routine/product stakes line, if any): 3–4 contrastive pairs (violates / complies). The examples are the definition; no abstract criteria.

## Enforcement honesty

For each artifact: `gate` (deterministic — hook or script, red means fix) or `advisory` (judgment-shaping — skill prose, suggestions in review). Nothing advisory is dressed as a gate.

## Acceptance

For each gate: the red→green fixture proving it (a fixture that fails without the check, passes with it). For each advisory rule: the boundary examples above stand as its acceptance.

---

# Plugin skeleton

```
const-<aspect-name>/
├── .claude-plugin/
│   └── plugin.json          # manifest — the ONLY file inside .claude-plugin/
├── MODULE.md                # this document, filled in
├── INSTALL.md               # install/uninstall notes; the one CLAUDE.md pointer line if any
├── skills/
│   └── <name>/SKILL.md      # optional
├── commands/<name>.md       # optional
├── agents/<name>.md         # optional
├── hooks/hooks.json         # optional
└── scripts/                 # optional; reference via ${CLAUDE_PLUGIN_ROOT}
```

Kebab-case everywhere. Only plugin.json lives inside `.claude-plugin/`; every component directory sits at plugin root. Verify the manifest fields against the current plugin reference at authoring time.
