# const-decision-records

<a id="a1"></a>
## What it gives you

Write-time gate on decision records: a document governed by a record policy carries type task-record, stakes (process | product | architecture) and a decider. Plus skills for pricing and recording a decision, and for promoting recurring commit notes.

<a id="a2"></a>
## Why use it

A session and its user argue a ruling through, with options, objections and a pick, and the ruling stays in the chat. The next session finds the code changed, sees no reason why, and reopens the question. In the same project a naming nit gets the ceremony of a structural choice, until nobody writes anything up. A page that calls itself a decision record but names no stakes and no decider is no better than the chat it came from.

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

**Before a write.** A hook runs before every `Write` and `Edit` of the platform's file tools. It reads the file as it would be after the write and finds whether a named record policy governs its path. It checks the three fields and lets the write through or refuses it. It cannot see a file written by a shell command, a script or another person. It does not judge the rest of the envelope, the body of the record, or whether a record was due at all.

**At session start.** A hook prints one line into the session's context while no record policy is named. The line says that no document is examined and which dial to write. Once a policy is named it prints nothing.

**The scan.** The same check over every Markdown file git lists, run from the command line. It reports every finding with exit code 2 and says how many records it examined. Run it in CI and before a merge.

**The two skills.** Procedures in prose, loaded when their activity occurs. Nothing in them blocks a write. The shape of a record's body is theirs, not the gate's.

**Settings.** The module works with no configuration beyond the one dial that switches it on: the list of record policies. Three more dials are read by the skills alone, as written. They hold the project's own examples of a routine call beside a recorded one. They name who may decide at each stakes level, and the commit trailer under which routine notes carry a theme. Two dials are every gate's: how loud a finding is, and where the log goes. The quieter setting reports the finding and lets the write through.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-decision-records@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-decision-record.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
