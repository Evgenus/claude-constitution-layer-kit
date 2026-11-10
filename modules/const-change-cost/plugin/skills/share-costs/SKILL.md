---
name: share-costs
description: >-
  Load this skill first, before a pull request is opened or merged in a clone where const-change-cost counts commits — every time, whether or not the cost seems wanted. It shares what each commit cost: the block of cost-report.sh --pr in the pull request's description, the lines of cost-report.sh --trailer in the merge commit's message, and git notes only on the person's word. Use when asked what a branch or a commit cost, when the session-start line says this clone logs no commit, or when a cost reads short. Advisory: it shapes what is shared and when; no gate holds it, and the module's commands make every figure.
---

# Share what a change cost

Claude Code writes the tokens of every reply into the session's transcript. This plugin logs each
session's start and each commit as they happen, counts the tokens of each commit's window with a
pinned ccusage, and keeps one line of counts per commit in the clone's git common directory. Nothing
leaves the clone by itself. A count reaches the team only when a person starts it, and this skill is
how a session does that at the two moments that matter: a pull request opened, and a change merged.

The report reads the file of counts. It runs no ccusage and reads no transcript, so it is quick and
safe to run. Its range is the commits of the change, such as `main..HEAD` or `<base>..<branch>`.

## 1. The start line says this clone logs no commit

The start line of this plugin appears at session start while git's configuration lacks one of its two
hooks of the commit log. Commits made before the hooks stand are never logged, and never counted.

1. Tell the person, once, in plain words: this clone logs no commit, so its commits get no count;
   `setup-commit-log.sh` writes the two hooks, and only a person changes git's configuration.
2. Run the setup only when the person asks for it:

   ```bash
   sh "${CLAUDE_PLUGIN_ROOT}/scripts/setup-commit-log.sh"
   sh "${CLAUDE_PLUGIN_ROOT}/scripts/setup-commit-log.sh" --check
   ```

   The check prints whether both hooks stand. Never write the keys with `git config` by hand.
3. When the person says this clone should not log commits, leave it, and do not raise it again in the
   session. When no person watches the session, say it in the final reply; a missing person is not a
   yes.

`setup-commit-log.sh --remove` takes the two hooks out again. The logs and the counts stay.

## 2. Before a pull request is opened

Run the report for the change and put its block in the description:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/cost-report.sh" --pr <base>..<branch>
```

Where `gh` finds the branch's pull request, the block is written into its description, between its two
markers, and a second run replaces the block and keeps the rest. Where there is no pull request yet,
or no `gh`, the block is printed: put it in the description you give to the forge, for example with
`gh pr create --body-file`. Never type a cost by hand.

## 3. Before a pull request is merged

1. Run `--pr <base>..<branch>` again, so the block holds every commit made since it was written.
2. Make the trailer lines:

   ```bash
   sh "${CLAUDE_PLUGIN_ROOT}/scripts/cost-report.sh" --trailer <base>..<branch>
   ```

   They are one `Change-Cost-Commit:` line for each counted commit, then one `Change-Cost:` line with
   the total. Print them even when some commits are not counted: the total line says how many were.
3. Put the lines in the **last paragraph** of the merge commit's message, where every line is
   `Key: value`. A merge you make yourself:

   ```bash
   git merge --no-ff <branch> -m "<subject>" -m "$(sh "${CLAUDE_PLUGIN_ROOT}/scripts/cost-report.sh" --trailer <base>..<branch>)"
   ```

   A merge on the forge's page has no local hook to see it: give the person the lines to paste into
   the merge message, as its last paragraph.

## 4. Git notes, only on the person's word

When the person asks to share each commit's count with the team:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/cost-report.sh" --notes <base>..<branch>
```

It writes one note for each counted commit under `refs/notes/change-cost`. Then name the push
command, `git push <remote> refs/notes/change-cost`, and run it only when the person says so: a pushed
ref publishes every count and cost, and in a public repository that is public. A person who asked only
for the pull request's block gets the block alone. A plain push sends no notes ref. A rebase leaves the
notes on the old commits unless `notes.rewriteRef` names their ref; say so before a rebase.

## 5. Read a figure for what it is

- Every cost is the **list price** of ccusage's table at the pinned version. Say "list price", never
  "the bill": a project may pay another price.
- A commit with a named **compaction** has at least the tokens shown. A compaction's own work reaches
  no transcript and is not counted. Say "at least", and name the compaction.
- A cost shown as "at least $…" has a model with no price in the table. Say "at least" and name the
  model; never give the number as the whole cost.
- A count is what a session spent, not all of a session's work and not a size of any document.
- The commits of a window run over the whole session. While one agent works and another commits, the
  first agent's tokens until then go to that commit. The session's total is exact.

## 6. A commit that is not counted

The report names each one, with the reason. Say what the line says; do not guess a count.

- **No line in the commit log:** the commit was made before the setup ran, by a tool that runs no git
  hook, or on a forge. It can never be counted.
- **The commit log names no session:** the commit was made outside Claude Code.
- **The session has no start in the start log:** it began before the plugin was enabled, or in another
  folder. No start is ever made up.
- **Its window is not complete:** no record of the session is dated after the commit yet. A later pass
  counts it; `sh "${CLAUDE_PLUGIN_ROOT}/scripts/count-costs.sh" --all` counts what is ready now.
- **No transcript of the session stands:** Claude Code's cleanup swept it, or it was never kept.

Share the report with the names in it. Do not hold the trailers back until every commit is counted.

## What this skill does not do

It changes nothing in git's configuration unasked, pushes nothing unasked, and holds no gate: no check
makes a merge fail for a missing trailer. The figures come from the commands alone.
