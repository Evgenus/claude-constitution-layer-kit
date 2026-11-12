# const-decision-records

<a id="a1"></a>
## What it gives you

Write-time gate on decision records: a document governed by a record policy carries type task-record, stakes (process | product | architecture) and a decider. Plus skills for pricing and recording a decision, and for promoting recurring commit notes.

In plain words: a decision record is a page that keeps a ruling and the reasons for it. A project names one policy, a page of rules, that says where its records live; a page there is the one the module checks. The check runs when the file is written, so a bad page is refused before it exists. Every record must carry three fields at its top. The first is its type, which is `task-record` for every record. The second is its stakes, which says how hard the ruling is to undo. The stakes are `process` for the way the project works, `product` for what users see, `architecture` for structure that is hard to change. The third is its decider, the person or role who made the choice. One skill helps decide whether a question deserves a record at all, and writes the record in a fixed shape. The other reads recent commit messages, finds the small calls that keep coming back, and proposes a record or a written procedure for them.

<a id="a2"></a>
## Why use it

A session and its user argue a ruling through, with options, objections and a pick, and the ruling stays in the chat. The next session finds the code changed, sees no reason why, and reopens the question. In the same project a naming nit gets the ceremony of a structural choice, until nobody writes anything up. A page that calls itself a decision record but names no stakes and no decider is no better than the chat it came from.

With the module installed, a record that names no stakes or no decider is refused at the write. The skill prices every decision first, so a cheap call stays a line in the commit and a real ruling gets its record. The next session reads the record, with its options and its reasoning, instead of reopening the question.

<a id="a3"></a>
## How Claude behaves with it

The project names, in its `constitution.yaml`, the policy that governs its decision records. A session that writes or edits a Markdown file in that policy's folders must give the file three fields at its top. The type is `task-record`; the stakes are `process`, `product` or `architecture`; the decider is the person or role who made the choice. When one is missing or wrong, the write is refused with a message that says what failed, why, and the fix. While no record policy is named, nothing is examined. The session is told so in one line at every session start.

```text
RED: docs/records/rec-0001-first.md: decision-record field(s) invalid: stakes missing; decider missing
  why: a decision record is a task-record whose envelope adds the stakes, which set the ceremony the ruling gets, and the decider, who is accountable for it; git can derive neither
  fix: set each named field: type = task-record (a record is a change delta); stakes = process (harness, policy or procedure) | product (user-visible behaviour) | architecture (structural, hard to reverse); decider = the person or role who made the choice, a non-empty string
```

Two skills load on their own. `record-decision` loads when a ruling is being made. It prices the decision by its stakes: a cheap call leaves one line in the commit message, and a real ruling gets a record. It writes the record in a fixed shape: the options, the pros and cons of each, one recommendation and the choice. `promote-recurring-notes` loads when commit messages are being reviewed. It finds the small calls that keep recurring on one theme and proposes a record or a written procedure for the theme.

<a id="a4"></a>
## How it works

**Before a write (hook on `PreToolUse`).** A hook runs before every `Write` and `Edit` of the platform's file tools. It reads the file as it would be after the write and finds whether a named record policy governs its path. It checks the three fields and lets the write through or refuses it. It cannot see a file written by a shell command, a script or another person. It does not judge the rest of the envelope, the body of the record, or whether a record was due at all.

**At session start (hook on `SessionStart`).** A hook prints one line into the session's context while no record policy is named. The line says that no document is examined and which dial to write. Once a policy is named it prints nothing.

**The scan.** The same check over every Markdown file git lists, run from the command line. It reports every finding with exit code 2 and says how many records it examined. Run it in CI and before a merge.

**The skill `record-decision`.** A procedure in prose, loaded when a ruling is made or has just been made in the dialog. It prices the decision, names the decider, writes the record from a template beside it, and says how to correct or reverse an earlier record. Nothing in it blocks a write. The shape of a record's body is the skill's, not the gate's.

**The skill `promote-recurring-notes`.** A procedure in prose, loaded when recent history is reviewed. It reads the commit messages and groups the routine calls by the question they answer. It proposes a record or a written procedure for a theme that keeps coming back. Where the project uses a commit trailer for these notes, it counts them with one git command. Nothing in it blocks a write.

**Settings.** The module works with no configuration beyond the one dial that switches it on: the list of record policies. Three more dials are read by the skills alone, as written. They hold the project's own examples of a routine call beside a recorded one. They name who may decide at each stakes level, and the commit trailer under which routine notes carry a theme. Two dials are every gate's: how loud a finding is, and where the log goes. The quieter setting reports the finding and lets the write through.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace: `claude plugin install const-decision-records@claude-constitution-layer-kit --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-decision-record.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
