# const-change-cost

<a id="a1"></a>
## What it gives you

Tokens per commit: for every commit a Claude Code session makes, the tokens that session spent on it — input, output, cache write and cache read — with their total and list cost, counted by a pinned ccusage from the session's own transcripts, kept in the clone, and shared by merge trailer, pull request and git notes.

In plain words: a token is the unit a model reads and writes, and a session spends many of them on one change. Claude Code keeps a transcript of each session, a file with every reply and its token counts. This module works out how many of those tokens went into each commit, and keeps the answer in your clone. Cache write and cache read are tokens the model stores and reuses, and they have their own prices. ccusage is a public tool that reads such transcripts. The list cost is the price on the model's public price page, which may differ from what you pay. A merge trailer is a line at the end of a merge commit's message. A git note is text that git keeps beside a commit without changing it.

<a id="a2"></a>
## Why use it

You ask what a change cost, and nobody can say. Claude Code writes the counts into each session's transcript, and gives no count for a commit. Counting later fails in three ways. A forked session copies its parent's replies, so a tool that reads every transcript at once can give the parent's work to the fork. Nothing records which session made a commit, or when a session began, unless something writes it at that moment. And Claude Code deletes a command-line session's transcript after 30 days, without a message.

With the module installed, each session's start and each commit are logged as they happen. A count then reads one session alone, and cuts its replies at the commits. Each commit has its own figures, kept in the clone, so a deleted transcript later costs nothing already counted. When a person starts it, a session puts the figures of a branch into the pull request's description and into the merge commit's message. It can also write them as git notes. Nothing leaves the clone before that. The module blocks nothing and sets no limit: it reports what was spent.

<a id="a3"></a>
## How Claude behaves with it

At every session start the module logs the session. While your clone does not log commits yet, one line names the two git hooks that are missing, and the session tells you instead of changing your git settings. When you ask to open or merge a pull request, the skill `share-costs` loads, and the session runs the report for the branch. It puts the block in the pull request's description. It puts the trailer lines in the last paragraph of the merge commit's message. It writes git notes, and pushes them, only when you say so. It reads every cost as a list price, and every figure as a lower bound where a compaction or an unpriced model is named.

```text
CHANGE-COST: 2 commit(s) of main..work/report-total, 2 counted, 0 not counted — tokens counted by ccusage 20.0.48, cost at its list price
total, 2 counted commit(s): input 2,000, output 550, cache write 5,000, cache read 45,000, total 52,550 tokens; $0.07 at list price; 10 replies; models: claude-sonnet-4-5-20250929 52,550; compactions: 0; unpriced: none
```

<a id="a4"></a>
## How it works

**At session start.** One hook appends the session's id, its start time, how it began and where its transcript is to a log in the clone's git folder. It prints the line about the missing git hooks while there are any, and nothing otherwise. It reads nothing else, and outside a git repository it does nothing. A second hook, in the background, counts every commit whose count is ready.

**At turn end.** A background hook counts the commits of its own session whose window is complete. A window is the part of the session between one commit and the next. It is complete when the session wrote a record after the commit. Each count is one line, written once and never made again.

**The setup command.** `setup-commit-log.sh` writes two hooks into the clone's git settings, one on commit and one on merge. Each appends the commit, the time and the session's id to a log. A person runs it, or a session when the person asks. It can check that the hooks stand and remove them, and it leaves the logs.

**The count.** `count-costs.sh` copies one window of one session into a throwaway folder and runs the pinned ccusage over it. It keeps the four counts, their total, the cost, the number of replies, the tokens of each model, the compactions it saw and the models with no price. A compaction is the moment Claude Code shortens a session's history, and its work reaches no transcript, so it is named and not counted. It runs after each turn and at each start, and a person can run it too.

**The report.** `cost-report.sh` reads the kept counts and runs no ccusage. It lists a range of commits, names each commit that is not counted with the reason, and shows the total. `--trailer` prints the lines for a merge commit. `--pr` writes a block into a pull request's description through the GitHub command line, or prints it. `--notes` writes git notes. It never pushes.

**The skill `share-costs`.** A procedure in prose: set up the commit log only when asked, share the block and the trailers at the pull request and the merge, write notes only on your word, and read each figure as what it is. It checks nothing. The start line names it where it applies.

**Settings.** The module has no dials and works with no configuration. Only its effect report reads the project's settings file, and only for the keys every module takes; leave `log_dir` unset for this module. The ccusage version is pinned, so two clones count alike, and every cost is the list price at that version.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it. The module also needs git 2.54 or newer, and Node with npm for the pinned ccusage.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace: `claude plugin install const-change-cost@claude-constitution-layer-kit --scope project`. Then, once in each clone, a person runs the setup, and after commits the report:

```bash
sh <plugin root>/scripts/setup-commit-log.sh
sh <plugin root>/scripts/cost-report.sh main..HEAD
```

The full install procedure is in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
