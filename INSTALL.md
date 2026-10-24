---
id: kit-install-guide
type: current-state
title: Constitution Kit — Install Guide
status: active
---

# Install guide

How to install the constitution kit into a project, keep it up to date and remove it. For what the kit is and why, read the [README](README.md) and the [intent page](INTENT.md); for its vocabulary, the [kernel](kernel/CONVENTIONS.md).

Every module is a draft at manifest version `0.0.x` until Phase D of the [rollout plan](docs/rollout-plan.md#phase-d) publishes it, and no module has had its consumer-live proof yet: the first project's bootstrap is that proof, and a finding there is a fix in the kit. A draft is not offered for installation, save for its live proofs ([rule 4 of plc-0006-module-documents](docs/policies/plc-0006-module-documents.md#r4)): a project that installs the kit today is that proof, and loads the modules from the kit's path, a clone in live mode or with `--plugin-dir` ([§3](#s3)), so that a fix in the kit reaches it at once. Once the modules are published at `0.1.0` ([step 10 of the rollout plan](docs/rollout-plan.md#s10)), every project installs them from the kit's GitHub repository, `Evgenus/claude-constitution-layer-kit`, as [§2](#s2) says, the proof's project included ([step 11](docs/rollout-plan.md#s11)). The kit's `scripts/check-install-guide.py` runs the commands of this guide on the Claude Code version the kit's CI pins, on every pull request and on `main` after each merge, and tests what the guide says they do ([plc-0011-install-guide](docs/policies/plc-0011-install-guide.md#r4)). The commands write the kit's clone as `~/dev/claude-constitution-layer-kit` and the project as `~/dev/my-project`: put your own paths there.

<a id="s1"></a>
## Prerequisites

1. Claude Code installed and authenticated (`claude --version`).
2. Read access to the kit's GitHub repository, `Evgenus/claude-constitution-layer-kit`, from which the modules are installed: git clones it with your own credentials while the repository is private. And a local clone of it, for example at `~/dev/claude-constitution-layer-kit`: the commands below take the module names, the kernel, the scans and the fixtures from it.
3. git, and Python 3.12 or newer as `python3` with the shared distribution `constitution-layer-kit`, for every gate. No plugin carries its package, `constitution_layer_kit`: each gate imports it from the `python3` your hooks run, so install the distribution there once. It brings PyYAML with it. pip clones the kit's repository with git and your own credentials and builds the distribution at the release tag. A module that needs a later release says so on its first line and points at its own `INSTALL.md`: install that tag then. pytest is needed only to run a module's fixtures, which is optional; no module's `requirements.txt` names pytest or pytest-xdist, since no gate needs them:
   ```bash check=none
   python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v1.0.0#subdirectory=shared"
   python3 -m pip install pytest   # optional, for the fixtures
   ```
4. Vale 3.23.0 or newer for [`const-language`](docs/requirements.md#const-language), and lychee 0.24.2 or newer for [`const-referencing`](docs/requirements.md#const-referencing):
   ```bash check=none
   brew install vale lychee
   ```
   A missing tool stops a gate with exit 1, never with a silent pass. Each module's own `INSTALL.md` names what it needs.

<a id="s2"></a>
## Bootstrap a new project

The modules are loaded first, so that their gates see every document the session writes through its file tools: their failures compound with every unguarded file ([step 5 of the rollout plan](docs/rollout-plan.md#s5)). A file made through the shell passes no hook, the kernel copy of step 5 among them; the scans of step 8 check it. The bootstrap runs on a branch of its own, `work/adopt-kernel`, and you commit on it after each step. Decision record #1 is at `process` stakes, so its yes is named in the merge that lands the branch on `main`, the commit that lands it ([kernel §4](kernel/CONVENTIONS.md#k4)). Each block runs from the folder the one before it left you in.

1. **Create the repository and the branch.** Rollback points live in git.
   ```bash check=new-repo
   mkdir -p ~/dev/my-project && cd ~/dev/my-project && git init -b main && git commit --allow-empty -m "Initial commit" && git switch -c work/adopt-kernel
   ```
2. **Register the kit as a marketplace, from GitHub.** The platform clones the repository into its own configuration, and each install then copies a module's `plugin/` folder from there into its plugin cache, the copy a session runs. The marketplace goes to your user settings; with `--scope project` it goes to the project's `.claude/settings.json` instead, where a team shares it ([§3](#s3) has the team form). While the modules are drafts, a project is their live proof and loads them as the opening says: in live mode it registers its clone in place of this step, then enables the modules with the next, and a kit edit reaches it at once; with `--plugin-dir` it skips this step and the next. Do not register your local clone for a project's working install: a marketplace added from a local folder runs that folder's working files in place, whatever branch is checked out there ([§3](#s3), live mode).
   ```bash check=marketplace
   claude plugin marketplace add Evgenus/claude-constitution-layer-kit
   ```
3. **Install the modules at project scope.** Each install copies the module's `plugin/` folder into the plugin cache at its manifest version and enables it in the project's `.claude/settings.json`. The copy holds what a session runs, and never the module's tests, eval cases or documents. From the GitHub marketplace a session runs that copy, and a later edit in the kit reaches the project only as [§4](#s4) says; from a clone registered in live mode a session runs the clone instead ([§3](#s3)). All the modules at once, then commit `.claude/settings.json`:
   ```bash check=install
   for m in ~/dev/claude-constitution-layer-kit/modules/const-*; do claude plugin install "$(basename "$m")@claude-constitution-layer-kit" --scope project; done
   ```
   A session that runs this block may not load the modules until a later turn. Before step 4, check that the session lists the skill `/const-questions:ask-or-decide`; if it does not, start a new session in the project, since the gates guard nothing in a session that has not loaded them.
4. **Answer two questions, then write the dials file.** Each question is yours, asked one per message: the guide recommends yes to both, and your answer decides. Answer both before any policy exists, since a later change of answer touches every policy.
   - **Is the list of policies a catalog?** Yes: every policy is named `plc-<nnnn>-<slug>`, its id and its file name one name, and `const-catalogs.catalogs` holds, in the finished file, a second entry after `dec`, `prefix: plc`, `width: 4`, `territory: ["docs/policies/**"]`. The three ids in the block below then take that form, the root policy numbered first, and so do the `root_policy` path and the `record_policies` value that name them. No: each policy has a plain kebab-case id, as the block shows. Changing the answer later renames each policy, its key in the dials file and every citation of it ([kernel §1](kernel/CONVENTIONS.md#k1)). The guide recommends yes: the catalog gate then checks every policy's name from the first one, and the later change never comes.
   - **Does this project keep a style guide?** Yes: in step 6, after the first three policies, load the skill `/const-styling:style-defaults`. It creates the guide from the module's shipped text, gives it a policy of its own with its territory, and names it in `const-styling.guides`; the root policy asks every policy for a style rule, and each policy carries one. No: no guide is written, and the policies carry no style rule; record #1 says so, and the skill follows the module's shipped text and creates none. The scan of [`const-styling`](docs/requirements.md#const-styling) still reports the traces of its defaults. The guide recommends yes: at install only a few policies need a style rule, the shipped guide passes the defaults of [`const-language`](docs/requirements.md#const-language) as written, and a guide added later edits every policy.

   Record both answers, with the guide's recommendation, in decision record #1 (step 7). Then write the dials file at the repository's root. The block shows the file as step 6 leaves it, for the answer no to both questions, each policy's territory under its id:
   ```yaml check=dials
   # constitution.yaml
   root_policy: docs/policies/root-policy.md
   module_prefix: const-
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
   With the answer yes to both questions, the keys that change read as below, again as step 6 leaves them; the style guide's policy takes the next number, and its territory is the one path of the guide, both written by the skill in step 6. With a style guide and no catalog, its policy takes a plain id, such as `style-guide-policy`.
   ```yaml
   root_policy: docs/policies/plc-0001-root-policy.md
   plc-0001-root-policy:
     territory: ["docs/policies/**"]
   plc-0002-kernel-policy:
     territory: ["docs/constitution/**"]
   plc-0003-decision-records:
     territory: ["docs/decisions/**"]
   plc-0004-style-guide:
     territory: ["/docs/style-guide.md"]
   const-decision-records:
     record_policies: [plc-0003-decision-records]
   const-catalogs:
     catalogs:
       - prefix: dec
         width: 4
         territory: ["docs/decisions/**"]
       - prefix: plc
         width: 4
         territory: ["docs/policies/**"]
   const-styling:
     guides: ["/docs/style-guide.md"]
   ```
   In this step, write only the file's first lines, the root's: `root_policy`, `module_prefix`, the root policy's territory, the namespace of [`const-task-close`](docs/requirements.md#const-task-close), and, if the policies are a catalog, `const-catalogs` with its `plc` entry, so that the catalog gate checks the first policy's name. The file comes before the policies because without it every gate skips the write; with it, the gates examine the first writes, and the root's lines let the creation command and the checks of the root policy run. Claim nothing else yet: a territory is claimed once its kind has a policy, before its first document, and never without a policy behind it, so step 6 adds each further policy's lines after the policy. The root's territory is the one claimed before its policy, which step 6 writes first. The kernel copy needs no departure from [`const-language`](docs/requirements.md#const-language): it meets that module's default thresholds as written, and gives no passive-voice note. Commit the file.
5. **Copy the kernel,** before the policies, so that they can link its sections from their first write. It is the one document made before its policy: it stays outside claimed territory until step 6 claims `docs/constitution/**`, and the scans of step 8 check it. Only the kernel is copied, and the kit's `LICENSE` and `NOTICE` with it; module source never lives in a project. `docs/constitution/CONVENTIONS.md` carries its own envelope, so the kernel is the first document its own rules govern. The kit is under the Apache License 2.0, so its `LICENSE` and its credit, `NOTICE`, travel with the copy: the block puts both beside the kernel. They cover the kernel copy alone, never your project, and carry no envelope, which [kernel §1](kernel/CONVENTIONS.md#k1) asks of Markdown documents only. A project that passes its kernel copy on to others, as a public repository does, keeps both files there and says in each kernel file it changed that it changed it. The block takes the kernel as git holds it at the commit the clone has checked out, and not the clone's folder: an untracked file there, such as the `.DS_Store` that macOS leaves, would reach your project, and an edit not yet committed would too. On another branch than `main`, the copy is that branch's kernel. Commit the copy.
   ```bash check=kernel
   mkdir -p docs/constitution && git -C ~/dev/claude-constitution-layer-kit archive HEAD:kernel | tar -x -C docs/constitution
   cp ~/dev/claude-constitution-layer-kit/LICENSE ~/dev/claude-constitution-layer-kit/NOTICE docs/constitution/
   ```
6. **Write one policy per document kind** under `docs/policies/`, each with the kernel envelope ([kernel §1](kernel/CONVENTIONS.md#k1)): a root policy, the policy for policies, whose territory is `docs/policies/**`, itself included; a policy for the kernel copy, `docs/constitution/**`, with an id of its own, never [constitution-kernel](kernel/CONVENTIONS.md), which the kernel document already carries; a policy for decision records, `docs/decisions/**`. Write them in that order: the root policy first, whose lines step 4 wrote, then each other policy, adding its territory under its id right after it; and, after the policy for decision records, `const-decision-records.record_policies` naming it and the `dec` entry of `const-catalogs`, before the `plc` entry where there is one. One policy governs exactly one kind, and a policy never lists its documents: the territory does ([kernel §3](kernel/CONVENTIONS.md#k3)). Write them yourself; the kit's own policies are examples to read, not to copy, since they cite rules only the kit has. Policies are your project's content, never the kernel's or a module's. The skill `/const-locations:new-kind` walks the order: its "From zero" writes the root policy by hand, the one policy written without the creation command, and every further policy goes through the command, which needs the root's lines. With a style guide, the skill of step 4 comes after the three policies: it writes the guide, its policy and their lines in the dials file, and a style rule in the root policy and in each policy. Commit the policies.
7. **Write decision record #1** at `docs/decisions/dec-0001-adopt-constitution-kernel.md`: "Adopt constitution kernel", its `id` the file name without `.md`, `type: task-record`, `stakes: process`, `decider: <you>`, and `status: inactive` from birth. Its body holds one numbered section per question of step 4, each with its options and their pros and cons, the guide's recommendation with its reason, and your answer. By the commit that creates it, everything it rules is applied on the branch — the dials file, the kernel copy and the policies by the earlier steps — which is why it is born `inactive` ([kernel §5](kernel/CONVENTIONS.md#k5)), and it lands with them in the merge ([kernel §4](kernel/CONVENTIONS.md#k4)). Write it with the skill `/const-decision-records:record-decision`, which takes the record's home from the dry run of `/const-locations:new-document` (`--dry-run`) and its number from [`const-catalogs`](docs/requirements.md#const-catalogs). The creation command alone writes `status: active` and no `stakes` or `decider`, through the shell, where no hook sees it. Once `record_policies` names the record policy, the gates check a record written through the file tools: the envelope by [`const-meta-types`](docs/requirements.md#const-meta-types), and its type, stakes and decider by [`const-decision-records`](docs/requirements.md#const-decision-records). The kit ships no validator of its own for the kernel's record schema. Commit the record.
8. **Verify.** Open a new session with `claude` in the project, since one that started before step 3 shows none of what follows: the session-start text of [`const-questions`](docs/requirements.md#const-questions), [`const-referencing`](docs/requirements.md#const-referencing) and [`const-interaction`](docs/requirements.md#const-interaction) appears. In a terminal, `claude plugin list` shows every module enabled, and in a terminal session the Errors tab of `/plugin` is empty; the desktop app opens neither, so run the first from a terminal. A live proof loaded with `--plugin-dir` opens that session with the flags of [§3](#s3), one per module, and takes the session-start text as the sign the modules loaded; it enabled nothing in step 3, so it reads no list of enabled plugins. After a write, a gate that passes it with nothing to note prints its line where the session never reads it: the session sees a line only from a gate that is red or has notes, such as the passive-voice notes of [`const-language`](docs/requirements.md#const-language). The scans print the verdict of every gate that judges documents; the prompt before a destructive command and the dirty-tree check at turn end have no scan of their own. Run every module's scan from the project's root; each exits 0 when green, 2 on a finding and 1 when it could not run:
   ```bash check=scan
   for s in const-referencing/plugin/scripts/check-references.sh const-meta-types/plugin/scripts/check-governed-document.sh const-catalogs/plugin/scripts/check-catalog-item.sh const-decision-records/plugin/scripts/check-decision-record.sh const-questions/plugin/scripts/check-open-questions.sh const-styling/plugin/scripts/check-style.sh const-language/plugin/scripts/check-language.sh const-doc-budgets/plugin/scripts/check-budgets.sh const-interaction/plugin/scripts/check-list-handles.sh const-task-close/plugin/scripts/check-task-close.sh; do sh ~/dev/claude-constitution-layer-kit/modules/"$s" --scan; done
   ```
   [`const-locations`](docs/requirements.md#const-locations) has no scan. Running each module's fixtures is optional. The install holds no tests, so they run from your clone, on throwaway repositories, never on the project. For an install from GitHub, first check the clone out at the commit the install records, `gitCommitSha` in the platform's `installed_plugins.json`:
   ```bash check=none
   for m in ~/dev/claude-constitution-layer-kit/modules/const-*; do python3 -m pytest "$m/tests" -p no:cacheprovider; done
   ```
9. **Merge with the yes.** Record #1 is at `process` stakes: merge only after the decider's yes, and name it in the merge commit, the commit that lands the record ([kernel §4](kernel/CONVENTIONS.md#k4)). The block first commits whatever a step left uncommitted, then merges the branch. Until the yes, the branch holds the work, committed: a turn-end hook of [`const-task-close`](docs/requirements.md#const-task-close) that asks for a commit is answered on the branch, and the yes still comes before the merge.
   ```bash check=commit
   git add -A
   git diff --cached --quiet || git commit -m "Finish the bootstrap"
   git switch main && git merge --no-ff work/adopt-kernel -m "Adopt the constitution kernel" -m "Yes: <decider>, in chat on <date>, for dec-0001-adopt-constitution-kernel."
   ```

<a id="s3"></a>
## Install one module

Each module is one plugin named `const-<aspect>`; it works with its defaults alone once `constitution.yaml` names `module_prefix`, as step 4 of [§2](#s2) shows, and the steps after loading it are optional calibration.

1. **Load the plugin**, by one of four paths.
   - **Development.** For one session, from your clone: `claude --plugin-dir ~/dev/claude-constitution-layer-kit/modules/const-<aspect>/plugin`, the flag once per module. This reads the clone in place, so after an edit in the kit `/reload-plugins` in the session takes it. Do not point `--plugin-dir` at the `modules/` folder: on Claude Code below 2.1.265 that loads nothing and prints nothing; check your version with `claude --version`.
   - **Marketplace.** As steps 2 and 3 of [§2](#s2), with the one module's name. The same commands work as `/plugin marketplace add …` and `/plugin install …` in a session.
   - **Live mode.** `claude plugin marketplace add ~/dev/claude-constitution-layer-kit` registers your clone itself, and the install of step 3 of [§2](#s2), with the one module's name, enables the module. A session runs the module's `plugin/` folder from the clone's working files in place and never from the copy its install writes to the cache, so every edit, and every branch checked out there, reaches the project: a hook script at its next run, the plugin's hooks file, skills and session-start text at the next session or `/reload-plugins`. That a session runs the clone was seen on Claude Code 2.1.286 on 2026-10-07. Use it for the kit's own development and a module's live proof, never for a project's working install.
   - **Team.** Commit the marketplace to the project's `.claude/settings.json`, so the catalog is added when a teammate trusts the folder; each person still installs a plugin from an external source once. A repository that holds the marketplace itself, as the kit does, declares it with `{ "source": "directory", "path": "." }` and lists each plugin under `enabledPlugins` as `"<name>@claude-constitution-layer-kit": true`; its relative-path plugins then load with no install, once the folder is trusted.
     ```json
     {
       "extraKnownMarketplaces": {
         "claude-constitution-layer-kit": {
           "source": { "source": "github", "repo": "Evgenus/claude-constitution-layer-kit" }
         }
       }
     }
     ```
2. **Calibrate.** Add the module's namespace, which equals the plugin's name, to `constitution.yaml`, the file that names `module_prefix` (step 4 of [§2](#s2) shows it); the module's defaults apply while its own namespace is absent. Three dials switch a check on: `record_policies` of [`const-decision-records`](docs/requirements.md#const-decision-records), `catalogs` of [`const-catalogs`](docs/requirements.md#const-catalogs), and `coverage` for the range check of [`const-task-close`](docs/requirements.md#const-task-close); each gate says so on every run until its dial is written. The module's `INSTALL.md` lists its dials.
3. **The `CLAUDE.md` pointer.** Only if the module's `MODULE.md` declares one: the single line its `INSTALL.md` gives, never more than one line per module.
4. **Verify.** `claude plugin list`, from a terminal, shows the module enabled, its skills appear as `/const-<aspect>:<skill>` under `/help`, and its scan, as its `INSTALL.md` names it, exits 0 from the project's root. Optionally, its fixtures are green when run from your clone, at the commit the install records or, for a module loaded from the clone, as it is: `python3 -m pytest ~/dev/claude-constitution-layer-kit/modules/const-<aspect>/tests -p no:cacheprovider`.
5. **Commit** `constitution.yaml`, `.claude/settings.json` and any `CLAUDE.md` line, the install noted in the message: routine, no record. With [`const-task-close`](docs/requirements.md#const-task-close) loaded, a turn that ends with uncommitted changes is reported once and the model is asked to commit; a change that touches code named in `coverage` updates the paired document or carries a `No-Doc-Impact: <pair> — <reason>` trailer on one of its commits.

<a id="s4"></a>
## Update

Modules are versioned, and a project takes a new version without editing anything of its own. For a published module, refresh the marketplace and update each plugin, then run `/reload-plugins` in a session:

```bash check=update
claude plugin marketplace update claude-constitution-layer-kit && for m in ~/dev/claude-constitution-layer-kit/modules/const-*; do claude plugin update "$(basename "$m")@claude-constitution-layer-kit" --scope project; done
```

A draft need not change its version across changes (decision [dec-0053-drafts-keep-their-versions](docs/decisions/dec-0053-drafts-keep-their-versions.md)). The marketplace update takes the repository's newest commit, and the plugin update still reports a draft at its version as current even after the kit has changed it: seen on Claude Code 2.1.286 on 2026-10-07, and not run by the kit's check, which cannot put a change on GitHub. To take such a change, uninstall each module and install it again — or load it with `--plugin-dir`, which reads the clone in place:

```bash check=reinstall
for m in ~/dev/claude-constitution-layer-kit/modules/const-*; do claude plugin uninstall "$(basename "$m")@claude-constitution-layer-kit" --scope project && claude plugin install "$(basename "$m")@claude-constitution-layer-kit" --scope project; done
```

The shared package updates apart from the plugins. A plugin that needs a later release than the one installed stops its gates with a line that names the release and the plugin's own `INSTALL.md`: run the command of [prerequisite 3](#s1) at that tag.

<a id="s5"></a>
## Uninstall

Remove the plugins, then each module's namespace from `constitution.yaml` and its `CLAUDE.md` line. The kernel copy in `docs/constitution/` stays; delete it only by a recorded `process` decision.

```bash check=uninstall
for m in ~/dev/claude-constitution-layer-kit/modules/const-*; do claude plugin uninstall "$(basename "$m")@claude-constitution-layer-kit" --scope project; done
```

<a id="s6"></a>
## What the kit does not install

The kit's own tooling ships in no module: the branch-first commit hook, the agents under `.claude/agents/`, the carry audit and the checks under `scripts/` serve the kit's own development. A project gets only what the plugins carry, each module's `plugin/` folder: never its tests, eval cases, `MODULE.md` or `README.md`. Beside the plugins a project installs the shared package of [prerequisite 3](#s1), which no plugin carries. A module carries its license in its manifest alone: `LICENSE` and `NOTICE` stand at the kit's root, and whoever passes a module's folder, or its `plugin/` folder, on alone takes both from there. `profiles/`, prewritten dials files to copy instead of writing dials by hand, are planned for [step 10 of the rollout plan](docs/rollout-plan.md#s10).
