---
id: dec-0117-change-cost-module-rulings
type: task-record
title: Rulings of the const-change-cost authoring — commit log by a command, ccusage by its launcher, counts kept in the clone and shared by trailer, pull request and notes, no dials
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-change-cost authoring — commit log by a command, ccusage by its launcher, counts kept in the clone and shared by trailer, pull request and notes, no dials

## Context

Record [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md) rules what the module counts and how, and its [R10](dec-0116-tokens-per-commit-counted-by-ccusage.md#r10) leaves the rest to this record, after the module's research round. That round is [res-0015-const-change-cost](../research/res-0015-const-change-cost.md). It confirmed rows [A15.1](../requirements.md#a15-1) to [A15.6](../requirements.md#a15-6) of the requirements matrix and left some choices to the decider. The session puts them in chat from 2026-11-09, one per message, and each adds a section here.

## 1. How the commit log reaches each clone

The comparison recommends git's `post-commit` and `post-merge` hooks set in git's configuration, from git 2.54 on, reading the variable `CLAUDE_CODE_SESSION_ID`. It is the only route it found that names each commit's session with no guess when two sessions share a checkout. A plugin cannot install a git hook, and a git hook cannot find the plugin's folder, which moves with each version, so each hook is a whole command of its own. Someone must write the two keys into each clone's `.git/config`.

- **A. A step per clone.** The module ships a command, and its install note says to run it once in each clone, as the kit runs `sh scripts/setup-clone.sh`.
  - **Pros:** nothing changes a project's git configuration unless a person runs the command; easy to undo.
  - **Cons:** a clone that skips the step logs no commits, which are lost for good, the loss R11 of [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md#r11) names; every contributor's clone must remember it.
- **B. The start hook writes the keys itself.** At each session start the module's `SessionStart` hook writes the two keys into the clone's own `.git/config` when they are missing, says so in its output, and names the command that removes them.
  - **Pros:** no step for anyone; every clone logs from its first session, as the day-one install of [R13](dec-0116-tokens-per-commit-counted-by-ccusage.md#r13) asks; the write is announced, not hidden.
  - **Cons:** a plugin changes the project's git configuration without a person typing it; after an uninstall the keys stay until removed and keep appending to the log.
- **C. The start hook warns, a command writes.** At each session start the hook names the missing keys and the one command that writes them; it writes nothing itself.
  - **Pros:** only a person changes git's configuration, and no clone goes unnoticed, since the warning comes at the first session.
  - **Cons:** commits made before someone runs the command are lost; a headless or automated session shows the warning to nobody; the warning repeats in every session until the command runs.

The session recommended B, the only option that loses no commit. The decider chose C in chat on 2026-11-09 and gave no other reason. The session keeps its objection in view: a clone's commits before the command runs are not logged, and a session that no person watches warns no one.

<a id="r1"></a>**R1.** The commit log is git's `post-commit` and `post-merge` hooks, set in the clone's git configuration. Each is a whole command that appends the commit's SHA, the time in milliseconds and the value of `CLAUDE_CODE_SESSION_ID` to the log in the clone's git common directory, which every worktree of the clone shares.

<a id="r2"></a>**R2.** The module ships a command that writes the two keys into the clone's `.git/config`, and removes them when asked; it writes nothing else there. While either key is missing, the module's `SessionStart` hook names the missing keys and that command in its output at each session start. No hook of the module writes the keys.

## 2. How the module runs ccusage

The npm package of ccusage is a Node launcher and one native binary per platform. In the comparison's experiment E1 the native binary counted correctly with no Node on the `PATH`. Node and npm are needed anyway to install the pinned package, since Claude Code runs npm from the person's `PATH` when it copies a plugin, and [R13](dec-0116-tokens-per-commit-counted-by-ccusage.md#r13) already makes Node a need of the first day.

- **A. Through the launcher.** The module runs `ccusage` from the pinned package's `.bin` folder, as ccusage documents.
  - **Pros:** ccusage's own entry point; it picks the right binary for the platform; it survives a change in the package's layout.
  - **Cons:** Node must be present at every count, not only at the install.
- **B. The native binary directly.** The module finds the platform's binary inside the pinned package and runs it.
  - **Pros:** no Node at the count; one process fewer.
  - **Cons:** the binary's place inside `node_modules` is ccusage's own layout, not a promise, so a release can move it; the module must choose among six platform packages itself.

The session recommended A: Node is present wherever the package can be installed, so B saves nothing and leans on a layout ccusage never promised. The decider chose A in chat on 2026-11-09.

<a id="r3"></a>**R3.** The module runs ccusage through the launcher of its pinned package, from that package's `.bin` folder, and never calls a platform binary by its path.

## 3. Where the counts are kept

A count exists only after its commit's window closes, as [R5](dec-0116-tokens-per-commit-counted-by-ccusage.md#r5) says, so no commit can carry its own count. In the comparison's experiment E14, git notes were seen from a linked worktree; a plain push sent no notes, and a rebase lost them unless `notes.rewriteRef` named their ref. A squash or rebase merge on a forge makes new commits that no count names, though a report per pull request can still sum the branch's own commits. A commit trailer changes the commit's SHA, and a file in the tree would ride a later commit that must be counted too.

- **A. A local file in the clone's git common directory.** One JSON line per counted commit, beside the start log and the commit log.
  - **Pros:** shared by every worktree of the clone; never published; no ref that a person must remember not to push; kept when the module is uninstalled.
  - **Cons:** lost with the clone; other clones and other people never see it.
- **B. Git notes on each commit, under a ref of the module's own.**
  - **Pros:** git's own place for facts about a commit; `git log` can show them; a team can share them by pushing the ref.
  - **Cons:** a rebase loses them unless `notes.rewriteRef` is set in every clone; pushing the ref publishes every count and cost, and the kit's repository is public; a forge's squash merge leaves them on commits that never land.
- **C. Both: the local file by default, and git notes as an export.** The counts are kept as in A, and a command writes them as notes only when a person runs it.
  - **Pros:** A's safety by default, and a way to share when someone chooses to.
  - **Cons:** a second output to build and test; the exported notes still carry B's rebase and publishing limits.

The session recommended A: the comparison's recommendation, private costs, and no requirement yet asks for sharing; an export can come later by a new record. The decider chose A in chat on 2026-11-09.

<a id="r4"></a>**R4.** The counts are kept in one file of JSON lines in the clone's git common directory, beside the start log and the commit log, one line per counted commit. The module writes no file in the working tree, and writes a git note or a trailer only as R12 to R15 say.

## 4. When the count runs

A commit is counted once its window is complete, and only once, as [R5](dec-0116-tokens-per-commit-counted-by-ccusage.md#r5) says. The comparison found the transcript written late: at a commit's `PostToolUse` it did not yet hold the call's result, at `Stop` it held 31 of its final 34 lines, at `SessionEnd` all of them (E15). A plugin's `SessionEnd` hook has 1.5 seconds and cannot raise them, while an `async` hook runs in the background with no timeout enforced. A run of ccusage took at most 0.10 seconds (E10). Command-line transcripts are swept after 30 days by default.

- **A. After each turn, at each start, and by hand.** An async `Stop` hook counts every complete window of its session not yet counted, the same pass runs at `SessionStart` over every session in the clone's logs, and a command does it on demand.
  - **Pros:** a window is counted at the turn after its commit, long before any sweep; the start pass catches what a crashed or closed session left; no turn waits.
  - **Cons:** three ways in to build and test; a count in the background can still run when the next turn starts.
- **B. By hand only.** A command counts every complete window it finds.
  - **Pros:** the least machinery; nothing runs unasked.
  - **Cons:** windows wait until someone remembers, and a command-line transcript can be swept first, against the accumulating class of [R13](dec-0116-tokens-per-commit-counted-by-ccusage.md#r13).
- **C. At session end, and a pass at start.** A `SessionEnd` hook counts the session's windows, and the start pass catches the rest.
  - **Pros:** the transcript is complete at `SessionEnd`; one count per session.
  - **Cons:** 1.5 seconds is too short to copy and count a large session; a desktop session that lives for days rarely ends, so its windows wait for the next start.

The session recommended A, the comparison's recommendation and the only one that counts each window soon without making a turn wait. The decider chose A in chat on 2026-11-09.

<a id="r5"></a>**R5.** The count runs three ways, each counting every complete window not yet counted: an `async` `Stop` hook, over its own session, after each turn; a pass at `SessionStart`, over every session in the clone's logs; and a command a person runs. The module keeps no copy of a window's records.

## 5. How the work of parallel agents is split

Each subagent writes its own transcript, whose records carry `agentId` and the parent's session id, and the tool hooks inside a subagent carry `agent_id` (the comparison's E11 and E15). The commit log of R1 knows only the session: `CLAUDE_CODE_SESSION_ID` names the session, not the agent, and no variable names the agent, so a subagent's commit carries the main session's id.

- **A. Time windows over the whole session.** Every reply of the session, of the main thread and of every agent, goes to the session's next commit by time, as [R4](dec-0116-tokens-per-commit-counted-by-ccusage.md#r4) cuts it.
  - **Pros:** time is the one key every reply carries; it uses the commit log of R1 as it is, with no guess.
  - **Cons:** if agent X still works while agent Y commits, X's tokens until then go to Y's commit.
- **B. Windows per agent.** Each agent's replies go to the next commit that agent made, and the main thread's replies, and those of agents that never commit, go by time.
  - **Pros:** a commit made by one agent does not take in a parallel agent's work.
  - **Cons:** the commit log cannot tell which agent made a commit, so it would need a `PostToolUse` lister, which in the comparison's E13 claimed another session's commit in a shared checkout; it still falls back on time for the rest.

The session recommended A, the comparison's recommendation: B trades the commit log's certainty for an agent name and still splits most of the work by time, while the session's total is exact either way. The decider chose A in chat on 2026-11-09.

<a id="r6"></a>**R6.** A session's windows run over the whole session: every reply of its main thread, its subagents and its workflow agents goes to the session's next commit by time. No window is cut per agent.

## 6. A session from before the start log

A commit can name a session whose `SessionStart` hook never ran in this clone, since the session started before the plugin was enabled or in another folder (the comparison's section 8). With no logged start, [R3](dec-0116-tokens-per-commit-counted-by-ccusage.md#r3) cannot cut away the history a fork copied in.

- **A. Skip and name.** Such a commit gets no count, and the report names it with its reason, as it names a commit with no session.
  - **Pros:** it never claims work the session did not do; nothing is read beyond the session's own files; the case is narrow, since [R13](dec-0116-tokens-per-commit-counted-by-ccusage.md#r13) installs the module from a project's first session.
  - **Cons:** a project that enables the module after weeks of sessions gets no count for the commits of the sessions already running.
- **B. A stand-in start.** The start becomes the earliest record of the session's transcript that stands in no other session's transcript.
  - **Pros:** those commits are counted too; on the comparison's live fork the stand-in fell 20 milliseconds after the logged start and gave the same count (E19).
  - **Cons:** once the parent's transcript is swept, after 30 days by default, the fork's copies stand in no other transcript and look like its own, so it claims the parent's work; it reads every other transcript of the project, so a session's count depends on other sessions again, which the earlier record rules out.

The session recommended A, the comparison's recommendation: B breaks the rule that no other session changes a session's count, and fails without a sound once the sweep has run. The decider chose A in chat on 2026-11-09.

<a id="r7"></a>**R7.** A commit whose session has no start in the start log gets no count, and the report names it with that reason. The module never makes up a start from other sessions' transcripts.

## 7. How a project gets the pinned ccusage

When a plugin root holds a `package.json` with a lockfile, Claude Code installs the dependencies itself into each version folder it copies. It needs exact versions, `https` downloads and no overrides, runs no install scripts, stops after 60 seconds, and cannot be turned off; ccusage's lockfile meets those limits (the comparison's a17 and E1). For a plugin loaded in place from a marketplace on a local path, as the kit loads its own modules, it installs nothing. The plugin pages give a `SessionStart` hook that runs `npm install` into `${CLAUDE_PLUGIN_DATA}`, a folder kept across updates, as an example (a18). The survey read both installs, ran neither, and made no install from a marketplace.

- **A. Both installs, from one lockfile.** A `package.json` and its `package-lock.json` at the plugin root pin ccusage: Claude Code installs it where it copies the plugin, and a `SessionStart` hook installs the same lockfile into `${CLAUDE_PLUGIN_DATA}` where the plugin loads in place.
  - **Pros:** a project that installs the module from the marketplace gets the platform's own install, with nothing of the module's to fail; the kit's load in place is covered too; one pin serves both.
  - **Cons:** two paths to build and test; the survey did not run the platform's install; a first session in place needs the network.
- **B. The start hook's install only.** No `package.json` at the root, and a `SessionStart` hook installs into `${CLAUDE_PLUGIN_DATA}` everywhere.
  - **Pros:** one path to build and test, the same for every project.
  - **Cons:** it does by hand what the platform does itself, against the native-first principle of the [intent page](../../INTENT.md#p1); each person's first session needs the network and runs npm.
- **C. `npx` with the exact version at each count.**
  - **Pros:** the least code; no install step.
  - **Cons:** the first count needs the network, and again whenever npm's cache is cleared; no lockfile checks the platform binary's integrity.

The session recommended A, native first for every project installed from the marketplace while the kit's own load in place stays covered, with the module's fixtures to prove the install the survey did not run. The decider chose A in chat on 2026-11-09.

<a id="r8"></a>**R8.** A `package.json` and its `package-lock.json` at the plugin root pin ccusage to an exact version. Where Claude Code copies the plugin, its own install of that lockfile is the module's install. Where the plugin loads in place, the module's `SessionStart` hook installs the same lockfile into `${CLAUDE_PLUGIN_DATA}` when the copy there differs.

## 8. A model with no price

In the comparison's experiment E8, a reply under a model name missing from ccusage's price table kept its tokens and added no cost, and the `--id` output of [R1](dec-0116-tokens-per-commit-counted-by-ccusage.md#r1) said nothing, not even on standard error. The same folder read without `--id` marked that model `missingPricing: true`. A model newer than the pinned ccusage would so make every commit look cheaper than it was, with no sign.

- **A. Name the unpriced model.** The count also reads the same one-session folder without `--id`; where a commit's window holds a reply whose model ccusage marks `missingPricing`, the kept line says so, and the report names that commit's cost as a lower bound, with the model.
  - **Pros:** the tokens stay exact, and a cost that is too low is never shown as whole; ccusage still does all the pricing.
  - **Cons:** a second run of ccusage per count, about 0.1 seconds in E10; one more field in the kept line.
- **B. Keep ccusage's cost as it comes.** The cost is what ccusage computes, with no mark.
  - **Pros:** the simplest count; one run.
  - **Cons:** after a model's release the costs fall short without a sign until the pin moves, the kind of hidden gap [R14](dec-0116-tokens-per-commit-counted-by-ccusage.md#r14) refused for compactions.
- **C. Keep the tokens only.** The count keeps the four token counts and no cost.
  - **Pros:** no price can be wrong.
  - **Cons:** it drops the cost that [A15.1](../requirements.md#a15-1) asks for; a reader must price the tokens by hand.

The session recommended A: ccusage stays the only pricer, and a short cost is shown as short, as R14 does for compactions. The decider chose A in chat on 2026-11-09.

<a id="r9"></a>**R9.** Each count also runs ccusage's session command without `--id` over the same one-session folder, to learn which of the window's models it marks `missingPricing`. The kept line names those models, and the report shows that commit's cost as a lower bound, with the models named. The tokens are counted as R1 of [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md#r1) says.

## 9. The names of the commands

People type these names, so the decider fixes them. The module has three acts a person runs: writing and removing the commit log's keys (R2), counting by hand (R5), and printing the report, per commit or summed over a range such as a pull request's commits, with each skipped commit, compaction and unpriced model named. The kit's modules ship one script per act under their plugin's `scripts/` folder, such as `new-document.sh` and `move-document.sh`; the kit's own `setup-clone.sh` takes `--check`; and every module's report is `effect-report.sh`.

- **A. One entry with subcommands.** `change-cost.sh` with `setup`, `remove`, `count` and `report`.
  - **Pros:** one name to learn, one help text, one form for a hook to allow.
  - **Cons:** unlike every other module of the kit, which ships one script per act.
- **B. One script per act, in the kit's forms.** `setup-commit-log.sh` with `--remove` and `--check`, after the kit's `setup-clone.sh`; `count-costs.sh`; and `cost-report.sh`, after `effect-report.sh`.
  - **Pros:** each name says its act; it matches the forms the kit's modules and tooling already use.
  - **Cons:** three names to learn.

The session recommended B, which keeps the kit's own forms, so that a person who knows one module can guess another's commands. The decider chose B in chat on 2026-11-09.

<a id="r10"></a>**R10.** The module's commands, under its plugin's `scripts/` folder, are `setup-commit-log.sh`, which writes the commit log's two keys and takes `--remove` to remove them and `--check` to report whether they stand; `count-costs.sh`, which counts every complete window not yet counted; and `cost-report.sh`, which prints the kept counts.

## 10. Dials

[Law 2 of CLAUDE.md](../../CLAUDE.md#law-2) lets project specifics enter a module only through its dials, and a module must work on an empty repository with its defaults alone. Nothing in rows [A15.1](../requirements.md#a15-1) to [A15.6](../requirements.md#a15-6) asks a project to calibrate anything.

- **A. No dials.** Section 7 of the module document says none, with that reason.
  - **Pros:** nothing to configure or validate; the test on an empty repository holds at once; the kit grows a dial only when friction earns it.
  - **Cons:** a project that wants a behaviour changed, such as silencing the start hook's warning, cannot do so without a new record and a new version.
- **B. One dial to silence the warning.** `warn_missing_keys` under `const-change-cost`, `true` by default; `false` stops the start hook from naming the missing keys.
  - **Pros:** a clone whose person chose not to log commits stops seeing the same warning in every session.
  - **Cons:** a silenced warning hides the loss [R11](dec-0116-tokens-per-commit-counted-by-ccusage.md#r11) names; one more key to validate and test, for a friction nobody has reported.

The session recommended A. The decider chose A in chat on 2026-11-09 and asked the session to check every ruling of both records for a value a project may need to set. The session read each:

- **Fixed so that a count means the same in every project.** R2 to R7 and R14 of [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md#r2), and R1, R3, R6, R7 and R9 here: a folder of one session, the earliest start, the windows, the count once, the kept fields, the two logs, the compaction named, the route, the launcher, the windows over the whole session, the session with no start skipped, the unpriced model named. A dial on any of them would make two projects' counts mean different things.
- **Owned by the module, not the project.** The pin of R8 of [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md#r8) and R8 here, which moves only with the known-count test of [A15.6](../requirements.md#a15-6), and the names of R10.
- **The one value a project may hold for itself: its prices.** R1 of [dec-0116-tokens-per-commit-counted-by-ccusage](dec-0116-tokens-per-commit-counted-by-ccusage.md#r1) passes `--config` naming an empty file, so a project's own ccusage configuration cannot change the count. ccusage's configuration takes `pricingOverrides`, a price per model for each kind of token (its schema at 20.0.48). A project that pays other than the list price, through a cloud provider or a discount, would want them. No project has asked.
- **Behaviours a project might want switched, later.** The start hook's warning of R2, the count after each turn of R5, and counts shared beyond the clone of R4, each refused here or in an earlier section, or never asked for.

<a id="r11"></a>**R11.** The module has no dials. Every cost it keeps and reports is the list price of ccusage's table at the pinned version, and the report says so. The module document lists the candidates of this section as deferred, each with the signal that would earn it: prices of a project's own, when a project that pays other than the list price asks for its costs; silencing the warning, when a project reports it as noise where commits are left out on purpose; the count after each turn switched off, when a project reports it as slow. Sharing the counts beyond the clone, a fourth candidate when this section was written, was decided the same day in section 11.

## 11. Sharing the counts beyond the clone

Under R4 the counts stayed in the clone that made the commits, lost with it and seen by no one else. The decider asked in chat on 2026-11-09 whether they can reach the repository and the remote. Whatever is shared publishes costs, since the kit's repository is public, and each clone shares only its own counts.

- **A. A trailer on the merge commit.** `cost-report.sh` prints a trailer for a branch, such as `Change-Cost: 21,673,425 tokens, $15.08 list, 4 commits`, which the person or session puts into the merge message.
  - **Pros:** it lands in git history on the remote, written once, with no SHA rewritten; every clone gets it with an ordinary fetch; it fits the kit's merge flow, whose merge commits already carry trailers.
  - **Cons:** a branch's total only; it depends on someone adding it, so a merge made on the forge's page without it carries nothing.
- **B. Git notes, one per commit.** A command writes each counted commit's line as a note under `refs/notes/change-cost`, and a person pushes that ref by name.
  - **Pros:** each commit's own count, read with `git log --notes=change-cost`; it can be run for old commits while the local file holds them.
  - **Cons:** notes are pushed and fetched only by naming the ref; a rebase drops them unless `notes.rewriteRef` is set; in a project that squashes its merges, the notes sit on commits that never land.
- **C. Both A and B.**
  - **Pros:** the branch's total in the history reviewers read, and each commit's count for anyone who fetches the notes.
  - **Cons:** two exports to build and test, and two more moments to teach.
- **D. The pull request's description.** `cost-report.sh` writes the branch's total there through the forge's command line.
  - **Pros:** seen on the forge's page, where reviewers look.
  - **Cons:** not in git, which is why the kit never keeps a record only there; it ties the module to the forges whose command line it knows, against the portability of [law 2 of CLAUDE.md](../../CLAUDE.md#law-2).

The session recommended C. The decider chose A, B and D together in chat on 2026-11-09, and added that the file of counts, a log of history, is never committed. In the next message the decider asked to see the counts in depth, the cached tokens, input and output among them, wherever they are shown, and then asked for the same figures for each commit in the pull request and in the merge commit. The session keeps D's cost in view: the description lives outside git, so the trailer and the notes stay the record, and where the module knows no forge's command line it prints the description's text for a person to paste.

<a id="r12"></a>**R12.** The counts leave the clone only in the three ways of R13 to R15, each started by a person and never by a hook, each made from the file of counts. The module never pushes; a person pushes the notes ref by naming it.

<a id="r13"></a>**R13.** `cost-report.sh --trailer <range>` prints, for the message of the merge commit that lands the range, one `Change-Cost-Commit:` trailer for each counted commit of the range, in the order of the commits, and one `Change-Cost:` trailer with the range's total, each with the figures of R17.

<a id="r14"></a>**R14.** `cost-report.sh --pr <range>` writes a block with each counted commit of the range and their total, each with the figures of R17, into the pull request's description, through the forge's command line where the module knows it, and prints the block elsewhere.

<a id="r15"></a>**R15.** `cost-report.sh --notes <range>` writes each counted commit's line as a git note under `refs/notes/change-cost`.

<a id="r16"></a>**R16.** The file of counts and the two logs are never committed or pushed. They stay in the clone's git common directory as the history every export is made from.

<a id="r17"></a>**R17.** The report and every export show the counts in depth, for each commit and for a range's total: input, output, cache write and cache read each on its own, their total, the cost at list price, the number of replies, the tokens of each model, and the compactions and unpriced models by name. The merge commit's trailers of R13, the pull request's block of R14 and the notes of R15 hold the same figures for each commit as the report. The cost is never split by kind of token, since ccusage computes it for the window as a whole.

## Applied

The change that holds this record carries R9 and R12 to R17 into the requirements matrix too, a `process` ruling under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2) that this record's yes covers: row [A15.7](../requirements.md#a15-7), sharing, is added, and rows [A15.2](../requirements.md#a15-2) and [A15.4](../requirements.md#a15-4) name the second run of ccusage and the fields kept, as the module's fresh-context review of 2026-11-10 asked under [law 4 of CLAUDE.md](../../CLAUDE.md#law-4).

## Carry list

1. R1, R2 — [section 3 of the module's document](../../modules/const-change-cost/MODULE.md#t3), the reading of the logs' row, and [section 5](../../modules/const-change-cost/MODULE.md#t5), rule J-a.
2. R3, R8, R9 — [section 3 of the module's document](../../modules/const-change-cost/MODULE.md#t3), the reading of the counter's row, [section 6](../../modules/const-change-cost/MODULE.md#t6), the configuration row, and [row A15.2 of the requirements matrix](../requirements.md#a15-2).
3. R4, R10, R16 — [section 6 of the module's document](../../modules/const-change-cost/MODULE.md#t6), the rows of the scripts and of the package.
4. R5 — [section 3 of the module's document](../../modules/const-change-cost/MODULE.md#t3), the reading of the count's row.
5. R6, R7 — [section 3 of the module's document](../../modules/const-change-cost/MODULE.md#t3), the reading of the row of ownership and windows.
6. R11 — [section 7 of the module's document](../../modules/const-change-cost/MODULE.md#t7), and [section 12](../../modules/const-change-cost/MODULE.md#t12), items 1 to 3.
7. R12, R13, R14, R15 — [section 5 of the module's document](../../modules/const-change-cost/MODULE.md#t5), rules J-b and J-c, [section 6](../../modules/const-change-cost/MODULE.md#t6), the rows of the skill and the scripts, and [row A15.7 of the requirements matrix](../requirements.md#a15-7).
8. R17 — [section 3 of the module's document](../../modules/const-change-cost/MODULE.md#t3), the reading of the row of the count's reach, and [row A15.4 of the requirements matrix](../requirements.md#a15-4).
