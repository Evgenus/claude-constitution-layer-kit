# Constitution Kit — Install Guide

A portable governance layer for Claude Code projects: a one-page semantic kernel plus modules shipped as plugins. This page is the install procedure only. For purpose read `INTENT.md`; for vocabulary read `kernel/CONVENTIONS.md`.

**Status today.** The kit ships the kernel, the module template and eleven modules under `modules/`, each a draft at manifest version `0.0.x` until Phase D publishes it (`docs/rollout-plan.md`). No module has had its consumer-live proof yet: the first project's bootstrap is that proof, and a finding there is a fix in the kit. `profiles/` arrives in Phase D. The kit's own tooling — the branch-first commit hook, the agents, the carry audit, the checks under `scripts/` — ships in no module.

## Prerequisites

1. Claude Code installed and authenticated (`claude --version`).
2. A local clone of this kit, e.g. `~/dev/constitution-kit/`.
3. The consumer project is a git repository (rollback points live in git).
4. For the gates: Python 3.12 or newer as `python3` with PyYAML (`python3 -m pip install 'PyYAML>=6.0'`); Vale 3.23.0 or newer for `const-language` and lychee 0.24.2 or newer for `const-referencing` (`brew install vale lychee`). A missing tool stops a gate with exit 1, never a silent pass.

## Part 1 — Install the constitution (kernel) into a project

Run from the consumer project root. Commit after each step. Load the modules first (Part 2, step 1), so that no governed document is written unguarded, the kernel copy included — their failures compound with every unguarded file (`docs/rollout-plan.md`, Phase B).

1. **Copy the kernel into the project.**
   ```bash
   mkdir -p docs/constitution && cp -r ~/dev/constitution-kit/kernel/. docs/constitution/
   ```
   Only the kernel is copied. Module source never lives in a project.
2. **Check the kernel's envelope.** `docs/constitution/CONVENTIONS.md` ships with its own frontmatter (`id: constitution-kernel`, `type: current-state`, `status: active`), so the kernel is the first document governed by its own rules. Nothing to add; confirm it survived the copy.
3. **Create the root policy and one policy per document kind.** Markdown documents under `docs/policies/`, each with the kernel envelope: a root policy, the policy for policies, whose territory is `docs/policies/**` including itself; a policy for the kernel copy, `docs/constitution/**` (its id is its own, never [constitution-kernel](kernel/CONVENTIONS.md), which the kernel document already carries and [kernel §1](kernel/CONVENTIONS.md#k1) forbids reusing); a policy for decision records, `docs/decisions/**`. One policy governs exactly one kind, and a policy never lists its documents: the territory does ([kernel §3](kernel/CONVENTIONS.md#k3)). A document is a policy because it sits in the root's territory. Write them yourself; the kit's own policies under `docs/policies/` are examples to read, not to copy, since they cite kit-only rules. Bodies are prose, the kernel specifies no format. Policies are consumer content: never kernel, never shipped by a module.
4. **Create the dials file** at the repository root. Each policy's territory sits under its id:
   ```yaml
   # constitution.yaml
   root_policy: docs/policies/root-policy.md
   root-policy:
     territory: ["docs/policies/**"]
   kernel-policy:
     territory: ["docs/constitution/**"]
   decision-records:
     territory: ["docs/decisions/**"]
   const-decision-records:
     record_policies: [decision-records]   # the gate examines nothing until this names the record policy
   const-catalogs:
     catalogs:                             # the gate examines nothing until a catalog is listed
       - prefix: dec                       # a record is dec-<nnnn>-<slug>, its id the file name without .md
         width: 4
         territory: ["docs/decisions/**"]
   const-task-close:
     severity: block                       # a dirty tree at turn end is reported once per turn: block asks the model to commit, warn notifies the user
     coverage: []                          # code territories paired with the documents that describe them; zero pairs examined until written
   ```
   The three module namespaces are read only once the module is loaded (Part 2) and are harmless before. Claim nothing else yet: a territory is claimed once its kind has a policy, before the first document rather than after, and never without a policy behind it.
5. **Write decision record #1** at `docs/decisions/dec-0001-adopt-constitution-kernel.md` — "Adopt constitution kernel", `id` equal to the file name without `.md`, `type: task-record`, `stakes: process`, `decider: <you>`, born `inactive` since it is applied in the same commit ([kernel §5](kernel/CONVENTIONS.md#k5)). The kit ships no validator for `docs/constitution/schemas/decision-record.schema.json`; the record's fields are checked at write time by the gates of `const-meta-types` and `const-decision-records` once installed (Part 2) — the second only once `record_policies` names the records policy (step 4) — and by their scans afterwards.
6. **Commit and merge** with one human yes. The kernel is installed.

## Part 2 — Install a module

Each module is one plugin named `const-<aspect>`. Repeat these steps per module. A module must work with zero configuration; steps 2–3 are optional calibration.

### 1. Load the plugin — pick one path

**A. Development path (works now).** Load from your kit clone for one session:

```bash
claude --plugin-dir ~/dev/constitution-kit/modules/const-<aspect>
```

Pass the flag once per module. Do not point `--plugin-dir` at the `modules/` folder: on Claude Code below 2.1.265 that loads nothing and prints nothing (check with `claude --version`); the kit will offer the folder form once its CI verifies it on a pinned version.

After editing module source, run `/reload-plugins` inside the session.

**B. Marketplace path.** Register the kit as a marketplace, then install at project scope, which enables it in the project's `.claude/settings.json`:

```bash
claude plugin marketplace add ~/dev/constitution-kit
```

The marketplace goes to your user settings by default. With `--scope project` it goes to the project's `.claude/settings.json` as a `directory` source holding the clone's absolute path: right for one machine, not for a team. A GitHub-hosted kit registers as `owner/repo` instead of a path. Then, per module:

```bash
claude plugin install const-<aspect>@constitution-kit --scope project
```

The same two commands work as `/plugin marketplace add …` and `/plugin install …` inside a session. The install copies the module into the plugin cache at its manifest version; a later edit in the kit reaches the project only as Update below says. All eleven at once:

```bash
for m in ~/dev/constitution-kit/modules/const-*; do claude plugin install "$(basename "$m")@constitution-kit" --scope project; done
```

**C. Team auto-registration.** Commit the marketplace to the project's `.claude/settings.json` so the catalog is added automatically when a teammate trusts the folder. Plugins from an external source, such as a GitHub-hosted kit, still need one `claude plugin install` per person. A repository that holds the marketplace itself — the kit is its own consumer zero — declares it with `{ "source": "directory", "path": "." }` instead and lists each plugin under `enabledPlugins` as `"<name>@constitution-kit": true`; its relative-path plugins then load with no install at all, once the folder is trusted.

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
Profiles are prewritten `constitution.yaml` files under `profiles/`; copy one instead of writing dials by hand. Three dials switch a check on: `record_policies` of `const-decision-records`, `catalogs` of `const-catalogs`, and `coverage` for the range check of `const-task-close`; the example of Part 1 step 4 writes the first two and leaves the third empty, and each gate says so on every run until then.

### 3. CLAUDE.md pointer (optional)

Only if the module's `MODULE.md` declares one: add the single line given in `modules/const-<aspect>/INSTALL.md` to the project's `CLAUDE.md`. Never more than one line per module.

### 4. Verify

1. `/plugin list` shows `const-<aspect>` enabled (`/plugin` → Errors tab if not).
2. Skills appear as `/const-<aspect>:<skill>` under `/help`.
3. Run the module's scan against the project from the project root, as its `INSTALL.md` names it — `sh <plugin root>/scripts/check-<check>.sh --scan`, exit 0 green — and its fixtures: `python3 <plugin root>/tests/run.py`, every item green. The fixtures run on throwaway repositories of their own, never on the project; `const-locations` has no scan and no gate, so only its fixtures run.

### 5. Commit

Commit `constitution.yaml`, `.claude/settings.json`, and any CLAUDE.md line. Note the install in the commit message; routine stakes, no record needed. With `const-task-close` loaded, a turn that ends with uncommitted changes is reported once and the model is asked to commit; a change that touches code named in `coverage` updates the paired document or carries a `No-Doc-Impact: <pair> — <reason>` trailer on one of its commits.

## Update and uninstall

**Update.** Modules are versioned; the consumer bumps by version. Nothing in the consumer repo needs editing when a module updates.

```bash
claude plugin marketplace update constitution-kit
```

Then `claude plugin update const-<aspect>@constitution-kit --scope project` and `/reload-plugins`. A draft keeps its version across changes (decision [dec-0053-drafts-keep-their-versions](docs/decisions/dec-0053-drafts-keep-their-versions.md)), and the update command then reports it current even after a kit change (seen on Claude Code 2.1.282). To take such a change, uninstall the module and install it again, or load it with `--plugin-dir`, which reads the clone in place.

**Uninstall.** Remove the plugin, its namespace from `constitution.yaml`, and its CLAUDE.md line. The kernel copy in `docs/constitution/` stays; delete it only by a recorded `process` decision.

```bash
claude plugin uninstall const-<aspect>@constitution-kit --scope project
```

## Where to go next

- `kernel/CONVENTIONS.md` — the one page every participant reads.
- `docs/requirements.md` — traceability matrix and module specifications.
- `docs/rollout-plan.md` — phases.
- `module-template/` — how a module is shaped, if you intend to author one.
- `templates/` — the templates of the kit's own document kinds that live in no territory; the `templates` dial of `const-locations` in `constitution.yaml` names which kind each serves.
