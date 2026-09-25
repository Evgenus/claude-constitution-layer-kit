---
id: dec-0043-kit-plugins-through-project-settings
type: task-record
title: The kit loads its own plugins through its committed project settings, nothing per clone
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit loads its own plugins through its committed project settings, nothing per clone

## Context

R4 of [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md) ruled how the kit's own sessions load its plugins: a marketplace file at the kit root with one relative entry per module, the project's settings file enabling each, and the clone setup script registering the marketplace and installing the plugins once per clone — the registration written to the user's settings, or to the project's local settings file if one headless run proved that form loads the plugins in place. Its premise, verified on 2026-09-25 against the settings reference of the day: a `directory` marketplace source in a settings file needs an absolute path, so a committed settings file cannot point at its own clone.

On 2026-09-26, implementing that work, the platform's documentation said otherwise: the page on managing plugins for an organization states that a `directory` or `file` source with a relative path in a repository's `.claude/settings.json` resolves against the repository's main checkout, worktrees included, and that a plugin the marketplace lists by a relative path loads from the marketplace once those entries apply, with no install record; the settings reference states that such entries are honored only after the person has accepted the workspace trust dialog for the folder, a `-p` run in an untrusted folder ignoring them without a message; the same reference, under `enabledPlugins`, and the plugin loading reference state that a plugin enabled in the project's `.claude/settings.json` is opted out of on one machine by setting its id to `false` in `.claude/settings.local.json`, which takes precedence over the project file — the mechanism R4 relies on, verified 2026-09-26 against both pages. Two headless runs in the kit itself, Claude Code 2.1.282, confirmed it: with the marketplace file written and a `.claude/settings.json` declaring the marketplace `constitution-kit` with a `directory` source at path `.` and enabling the eight modules, the session's `init` event listed all eight plugins with their paths inside the kit's `modules/`, the four `SessionStart` hooks and the `Stop` hook fired, and the model quoted the session-start lines it had received. The marketplace was recorded on the machine by the platform itself, with the path resolved to the clone.

## Options

- **A. As R4 was written.** The committed settings file enables the eight plugins only; the clone setup script registers the clone as a marketplace per clone through the platform's add command, into the user's settings, and its `--check` reports it.
  - **Pros:** Matches the ruling verbatim, so no new record; the per-clone step already exists for the git settings.
  - **Cons:** One more per-clone step, writing into the user's global settings an absolute path that goes stale when the clone moves, doing what the platform now does on its own.
- **B. The proven form: the committed settings file carries the marketplace too, with the relative directory source, and nothing runs per clone.** The setup script keeps its git job; the guide gains one line saying the plugins load once the folder is trusted.
  - **Pros:** Documented for exactly this case, proven twice, no per-clone step, worktrees resolve to the main checkout, and it is the file Phase D publishes anyway.
  - **Cons:** Reverses part of R4, so it needs this record and its carry audit; in an untrusted folder nothing loads through settings, so the kit's headless proofs on scratch clones keep `--plugin-dir`.

## Recommendation

B, by the session: the extra record is cheap, the ruling's premise was verified against documentation that has since changed, and A would ship a step the platform has made redundant.

## Choice

B, chosen by the decider in chat on 2026-09-26.

## Ruling

**R1.** The kit's committed project settings file, `.claude/settings.json`, declares the marketplace `constitution-kit` with a `directory` source at the relative path `.` and enables each module as `<module>@constitution-kit`; the marketplace file `.claude-plugin/marketplace.json` at the kit root lists each module by a relative entry. Nothing is written per clone to load them: the plugins load in place from the kit's own `modules/` in every session started in a folder the person has trusted once, and every kit session runs under the kit's own modules, gates included.

**R2.** The part of R4 of [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md) that had the clone setup script register the marketplace and install the plugins per clone, in the user's settings or the project's local settings file, is reversed; the rest of R4 — the marketplace file at the kit root, its name, the relative entries, the project's settings file enabling each module — stands. The clone setup script keeps its git job alone.

**R3.** A headless run in a folder the platform has not been told to trust loads no plugin through settings, so the kit's live proofs on clones and copies in the scratch directory keep passing `--plugin-dir` per module.

**R4.** The exception: a module whose gate blocks its own fix is switched off for one clone — its skills and session-start text with it — by `"<module>@constitution-kit": false` under `enabledPlugins` in that clone's `.claude/settings.local.json`, the one per-clone write to the plugin settings, which the kit's `.gitignore` keeps out of the tree so that the dirty-tree stop of `const-task-close` never fires on it.

## Applied

The creating commit rewrites the opening sentence of the session-conduct block of [CLAUDE.md](../../CLAUDE.md) and adds the `--plugin-dir` clause to step 6 of its module routine, updates step 10 of the rollout plan, the consumer-zero bullet of [INTENT.md](../../INTENT.md) and the header of the kit's `constitution.yaml`; the marketplace file and the settings file landed in the commit before it on the same branch. The record is born `inactive`. R4 was added and R1 qualified in place before the yes, after round 2 of the carry audit, as the kernel allows. The trim of the session-conduct block to what no module carries follows on the same branch, the routine edit R2 of [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md) names.

## Carry list

1. R1 — the opening sentence of the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md), which states how the kit's sessions load its plugins and under what condition; [.claude/settings.json](../../.claude/settings.json) and [.claude-plugin/marketplace.json](../../.claude-plugin/marketplace.json), the files themselves.
2. R2 — history only: the reversal of a part of an accepted ruling, ordered by the kernel's precedence clock.
3. R3 — step 6 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md), which names the runners and the flag they pass.
4. R4 — the opening sentence of the "Session conduct" block of [CLAUDE.md](../../CLAUDE.md), which names the escape and its file; [.gitignore](../../.gitignore), which ignores that file.
