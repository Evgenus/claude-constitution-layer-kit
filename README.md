# Constitution Kit — Install Guide

A portable governance layer for Claude Code projects: a one-page semantic kernel plus modules shipped as plugins. This page is the install procedure only. For purpose read `INTENT.md`; for vocabulary read `kernel/CONVENTIONS.md`.

**Status today.** The kit ships the kernel and the module template. `modules/`, `profiles/`, and `.claude-plugin/marketplace.json` arrive in rollout Phase D (`docs/rollout-plan.md`). Part 1 works now; Part 2 describes both the development path that works now and the marketplace path that applies once the catalog exists.

## Prerequisites

1. Claude Code installed and authenticated (`claude --version`).
2. A local clone of this kit, e.g. `~/dev/constitution-kit/`.
3. The consumer project is a git repository (rollback points live in git).

## Part 1 — Install the constitution (kernel) into a project

Run from the consumer project root. Commit after each step. Install the accumulating modules (Part 2) in the same session, before any governed document beyond the kernel is written — their failures compound with every unguarded file (`docs/rollout-plan.md`, Phase B).

1. **Copy the kernel into the project.**
   ```bash
   mkdir -p docs/constitution && cp -r ~/dev/constitution-kit/kernel/. docs/constitution/
   ```
   Only the kernel is copied. Module source never lives in a project.
2. **Check the kernel's envelope.** `docs/constitution/CONVENTIONS.md` ships with its own frontmatter (`id: constitution-kernel`, `type: current-state`, `status: active`), so the kernel is the first document governed by its own rules. Nothing to add; confirm it survived the copy.
3. **Create the dials file** at the repository root, claiming exactly one territory:
   ```yaml
   # constitution.yaml
   territories:
     "docs/constitution/**": constitution-kernel
   ```
   Claim nothing else yet; territories grow only over documents that exist.
4. **Write decision record #1** — "Adopt constitution kernel", `type: task-record`, `stakes: process`, `decider: <you>`, born `inactive` since it is applied in the same commit ([kernel §5](kernel/CONVENTIONS.md#k5)). Validate against `docs/constitution/schemas/decision-record.schema.json`.
5. **Commit and merge** with one human yes. The kernel is installed.

## Part 2 — Install a module

Each module is one plugin named `const-<aspect>`. Repeat these steps per module. A module must work with zero configuration; steps 2–3 are optional calibration.

### 1. Load the plugin — pick one path

**A. Development path (works now).** Load from your kit clone for one session:

```bash
claude --plugin-dir ~/dev/constitution-kit/modules/const-<aspect>
```

Pass the flag once per module, or point it at the whole `modules/` folder to load every module that has a manifest (Claude Code v2.1.265+):

```bash
claude --plugin-dir ~/dev/constitution-kit/modules
```

After editing module source, run `/reload-plugins` inside the session.

**B. Marketplace path (once `marketplace.json` exists).** Register the kit as a marketplace, then install at project scope so every collaborator gets it via `.claude/settings.json`:

```bash
claude plugin marketplace add ~/dev/constitution-kit
```

A GitHub-hosted kit registers as `owner/repo` instead of a path. Then:

```bash
claude plugin install const-<aspect>@constitution-kit --scope project
```

The same two commands work as `/plugin marketplace add …` and `/plugin install …` inside a session.

**C. Team auto-registration.** Commit the marketplace to the project's `.claude/settings.json` so the catalog is added automatically when a teammate trusts the folder. Plugins from an external source still need one `claude plugin install` per person.

```json
{
  "extraKnownMarketplaces": {
    "constitution-kit": {
      "source": { "source": "github", "repo": "<owner>/constitution-kit" }
    }
  }
}
```

### 2. Calibrate (optional)

Add the module's namespace to `constitution.yaml`. The namespace equals the plugin name; the module reads nothing else. Defaults apply when the namespace is absent.
```yaml
const-<aspect>:
  some_dial: value
```
Profiles are prewritten `constitution.yaml` files under `profiles/`; copy one instead of writing dials by hand.

### 3. CLAUDE.md pointer (optional)

Only if the module's `MODULE.md` declares one: add the single line given in `modules/const-<aspect>/INSTALL.md` to the project's `CLAUDE.md`. Never more than one line per module.

### 4. Verify

1. `/plugin list` shows `const-<aspect>` enabled (`/plugin` → Errors tab if not).
2. Skills appear as `/const-<aspect>:<skill>` under `/help`.
3. Run the module's red→green fixture from `modules/const-<aspect>/tests/` against the project: the failing input must be blocked with a teaching error, the passing input must go through.

### 5. Commit

Commit `constitution.yaml`, `.claude/settings.json`, and any CLAUDE.md line. Note the install in the commit message; routine stakes, no record needed.

## Update and uninstall

**Update.** Modules are versioned; the consumer bumps by version. Nothing in the consumer repo needs editing when a module updates.

```bash
claude plugin marketplace update constitution-kit
```

Then `/reload-plugins`.

**Uninstall.** Remove the plugin, its namespace from `constitution.yaml`, and its CLAUDE.md line. The kernel copy in `docs/constitution/` stays; delete it only by a recorded `process` decision.

```bash
claude plugin uninstall const-<aspect>@constitution-kit --scope project
```

## Where to go next

- `kernel/CONVENTIONS.md` — the one page every participant reads.
- `docs/rollout-plan.md` — phases, module specs, traceability matrix.
- `module-template/` — how a module is shaped, if you intend to author one.
