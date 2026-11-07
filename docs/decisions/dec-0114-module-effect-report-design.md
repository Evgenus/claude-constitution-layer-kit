---
id: dec-0114-module-effect-report-design
type: task-record
title: 'The effect report: each module counts its own rules through a shared runner, reading the transcripts and a log that names what it examined'
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The effect report: each module counts its own rules through a shared runner, reading the transcripts and a log that names what it examined

## Context

Record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md) defines a module's efficiency as its effect. At each moment where one of the module's rules applies, the rule was applied, bypassed or missed. R7 of that record leaves two things to the report's own design: where the report runs, and what it needs from the gate logs. This record is that design. The decider asked to proceed with [item 9.33 of the rollout plan](../rollout-plan.md#s9-33), and the session put the questions in chat on 2026-11-07, one per message.

Before the first question, the session read the knowledge kit again, the project the report serves first. Its 8 session transcripts hold a record for every hook run, and each record carries the `toolUseID` of the tool call the hook examined. All 1,728 hook records from tool calls matched their call, and the call names its file. The transcripts also hold 390 shell commands, 48 skill loads and 61 blocks, 45 of them by the hooks of module [`const-language`](../requirements.md#const-language) and 16 by those of module [`const-referencing`](../requirements.md#const-referencing). Claude Code gives every hook the path of its session's transcript in the hook's input, but it does not document the transcript's format. The gate logs remain the only record of the scans.

## 1. Where the report lives and runs

- **A. A kit script, run by hand.** A script under the kit's `scripts/`, run on the machine that holds the transcripts, with the project folder and its transcript folder as arguments; its list of rules is a data file beside it.
  - **Pros:** no module changes, so no version bumps and no stale eval receipts; [law 2 of CLAUDE.md](../../CLAUDE.md#law-2) holds, since the project path is only an argument; it follows [the kit's metrics report](../../scripts/metrics.py), also a kit-only report.
  - **Cons:** a consumer without a kit clone cannot run it; the list of rules lives apart from the modules, so it can drift when a module's rule changes.
- **B. A new module.** A plugin with a command, shipped to consumers, with its own matrix rows and its own dials.
  - **Pros:** any project that installs it can run it; it uses the kit's normal module model.
  - **Cons:** it needs the whole routine of a module; to count other modules' rules it must know them, which [law 3 of CLAUDE.md](../../CLAUDE.md#law-3) forbids.
- **C. Each module counts its own rules.** Each module ships a small effect part for its own rules, run by a shared runner in the shared package.
  - **Pros:** each list of rules lives with the rules it counts, so it cannot drift; module independence is kept.
  - **Cons:** it touches every module and the shared package, so every eval receipt goes stale; the largest change of the three, for a report no consumer has asked for yet.

The session recommended A, as the least machinery for a report on one project, with B or C when a consumer asks to run it. The decider chose C in chat on 2026-11-07 and gave no other reason.

<a id="r1"></a>**R1.** Each module counts the effect of its own rules. Its plugin ships the code that finds each rule's moments and their outcomes, and a runner in the shared package runs that code over a project. The runner names no module, as [rule 3 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r3) asks of all shared code.

## 2. What the report needs from the gate logs

A green record of a gate does not name the file it examined, gap G1 of record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md).

- **A. The transcripts alone, no change to the log.** The runner matches each hook run to its tool call by the transcript's `toolUseID`; the logs are read only for the scans.
  - **Pros:** no change to [the shared log writer](../../shared/constitution_layer_kit/output.py) or to any gate; it matched all 1,728 hook records; the report needs the transcripts anyway, to see shell writes, the act after a red and skill loads.
  - **Cons:** it relies on a format Claude Code does not document, so a platform update can break the match; a session whose transcript was deleted leaves its hook runs unmatched.
- **B. The log names the file.** Each gate's record gains a field for the file or the command it examined.
  - **Pros:** the kit owns the format, so no platform update can break it; the log alone shows what each gate examined, even with no transcript.
  - **Cons:** every gate must pass what it examined to the writer, which changes the interface of [kit-shared-gate-code §2](../../shared/GATE.md#g2); the report still needs the transcripts, so B adds little more than a second source.
- **C. Both.** The log gains the field, and the report uses the transcripts first and the log where no transcript is left.
  - **Pros:** a fallback when a transcript is gone or its format changes; the two sources can check each other.
  - **Cons:** the cost of B, plus a second matching path to build and test; two sources that can disagree need a rule for which one wins.

The session recommended A: the transcripts hold what B would add, and B can follow when a platform update breaks the match. The decider chose C in chat on 2026-11-07 and gave no other reason. In the next message the session stated the rule for a disagreement, and the decider did not object.

<a id="r2"></a>**R2.** A record of the gate log gains two fields: `path`, the file or the command the gate examined, and `transcript`, the path of the session's transcript that the hook's input gives. Each is a field whose default keeps the behaviour, as [rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11) allows in a minor release, and a record with nothing to name leaves it empty, as a scan's record leaves `transcript`.

<a id="r3"></a>**R3.** The runner reads the transcripts first and matches each hook run to the tool call it examined by the call's id. A log record counts only where no transcript holds its session. Where a transcript and the log both hold one hook run and name another file, the report counts the transcript's and prints the disagreement as a line of its own, never hidden.

<a id="r4"></a>**R4.** The runner finds the transcripts through the field `transcript` of the logs. For the sessions logged before that field, the person names a transcript folder by a flag. No module and no shared code writes the path of the platform's own folder.

## 3. How the reader judge runs

R4 of record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md#r4) gives the rules no pattern can see to a fresh reader, a language model.

- **A. Defer the reader.** This change builds the pattern judge only; each moment of a rule for a reader is counted and shown as not judged.
  - **Pros:** a smaller change; the deterministic half lands first; the first reports show which rules need a reader most.
  - **Cons:** an accepted ruling stays unbuilt; the advisory rules hardest to see get no verdict yet.
- **B. The runner starts the reader.** With a flag, the runner sends each moment of a rule for a reader to `claude -p`, with the rule's text and an excerpt of the transcript around it.
  - **Pros:** R4 of that record is built whole; one command gives both counts, kept apart; without the flag a run costs nothing.
  - **Cons:** each run with the flag costs subscription time and is slow on long histories; its verdicts drift between runs and models; the shared package gains a call to `claude`, which no part of it makes today.
- **C. A reader agent in the session.** Each module ships an agent that reads the transcripts for its own rules when the person asks.
  - **Pros:** no new machinery in the shared package; the person sees the reader's reasoning as it works.
  - **Cons:** less repeatable; its counts are joined with the runner's report by no program; the session may judge its own transcript.

The session recommended B, since the reader is already accepted and B keeps its counts in the same report, in their own column. The decider chose B in chat on 2026-11-07.

<a id="r5"></a>**R5.** With the flag of the reader, the runner sends each moment of a rule whose judge is the reader to `claude -p`. It sends the rule's text and an excerpt of the transcript around the moment, and takes back one of applied, bypassed or missed. It runs on the person's own login, never billed by usage: it refuses to start the reader unless `claude auth status` reports a subscription login. The report names the model and the Claude Code version the reader ran on. Without the flag, the moments of those rules are counted and shown as not judged.

## 4. What admits the runner to the shared package

[Rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) admits code only when it implements a kernel section literally or a gate-script rule of [template §6](../../module-template/MODULE.md#t6). The runner does neither.

- **A. A new template section, and rule 2 widened to admit it.** The template gains a section in which every module lists its rules; rule 2 also admits code that implements a template section every module fills.
  - **Pros:** the duty sits where every other duty of each module sits; the kernel stays as it is; the widening names one kind of section.
  - **Cons:** a policy edit and a template edit in one change, each in its own audit scope; the template grows by one section.
- **B. A new kernel section on effect.** The kernel defines a rule's moment and its three outcomes, and the runner implements that section.
  - **Pros:** no policy edit; the three outcomes become kernel words every document can cite.
  - **Cons:** the kernel already stands over its ceiling; a kernel change needs a carry audit in full and reaches every consumer that copies the kernel; a report is no meaning every project must adopt.
- **C. No runner in the shared package.** Each module carries its own copy of the runner, and a kit check holds the copies equal.
  - **Pros:** no edit for admission; each module stands fully alone.
  - **Cons:** it brings back the copies that record [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md) removed; every fix is made many times; R1 names a shared runner.

The session recommended A, since a report is a duty of the kit's modules and no meaning every project must adopt. The decider chose A in chat on 2026-11-07.

<a id="r6"></a>**R6.** [The module template](../../module-template/MODULE.md) gains a numbered section titled "Effect", with its own anchor. Each module lists there every rule its effect part counts, one row per rule: a key, the rule's moment, its judge, `pattern` or `reader`, and the ways of B1 to B6 in R2 and R3 of record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md#r2) that it can fail.

<a id="r7"></a>**R7.** [Rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) also admits code that implements a section of the module template that every module fills; the runner of R1 is admitted so.

<a id="r8"></a>**R8.** [The requirements matrix](../requirements.md) gains aspect A14, "Module effect", homed in the template and the shared package as [aspect A12](../requirements.md#a12) is homed in the kernel and the template. Its rows are written by the change that builds them, under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2).

## 5. How a person runs the report

- **A. One command per module.** Each module ships an entry beside its scan that runs the runner over its own rules and prints its own report.
  - **Pros:** the same shape as the scans; nothing has to find the modules; [law 3 of CLAUDE.md](../../CLAUDE.md#law-3) is easy to test, since each module reports alone.
  - **Cons:** a full picture takes one command per module; the reader flag is given to each; no report sets the modules side by side.
- **B. One shared command for all modules.** One entry of the shared package asks `claude plugin list --json` for the enabled plugins and runs every one with an effect part.
  - **Pros:** one command and one report for the project; the reader runs once over all modules.
  - **Cons:** the shared package depends on the output of Claude Code's plugin list, which no part of it reads today; the runner reaches every module, close to the line of [law 3 of CLAUDE.md](../../CLAUDE.md#law-3).
- **C. Both.** Each module's entry, and a shared command that calls them in turn.
  - **Pros:** each module stays testable alone, and the person still gets one report.
  - **Cons:** two entry points to build, test and document; B's dependency on the plugin list.

The session recommended A, since R1 of record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md#r1) sums the counts per module and never across modules. The decider chose C in chat on 2026-11-07 and gave no other reason.

<a id="r9"></a>**R9.** Each module's plugin ships the entry `scripts/effect-report.sh`, which reports that module alone. The shared package ships the entry `python3 -m constitution_layer_kit.effect`, which asks `claude plugin list --json` for the enabled plugins and calls the entry of each one that ships it. It prints their reports as one, each module's counts apart, summed per module and never across modules.

<a id="r10"></a>**R10.** Both entries take the same three flags: `--reader` starts the reader of R5, `--transcripts <dir>` names the transcript folder of R4, and `--since <date>` limits the window. Neither entry's name starts with `check-`, since the report is never a gate, R6 of record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md#r6).

## 6. The names and the order of work

The session proposed the names of R2, R6, R8, R9 and R10 as defaults, and an order of work in four pull requests. The decider accepted them all in chat on 2026-11-07.

<a id="r11"></a>**R11.** The work lands in this order, each step one pull request or more. First, this record. Second, the shared part: the runner, the two fields of the log, the reader, the template section, the widening of rule 2 and aspect A14, with their tests. Third, the modules, a few in each pull request: each fills its section "Effect" and ships its entry, with a new eval receipt for every module it touches. Last, the first report on the knowledge kit.

## Applied

The change states R1 to R11 as intent in items 9.33a to 9.33c of [the rollout plan](../rollout-plan.md#s9-33), beside item 9.33, which holds R1 to R7 of record [dec-0113-module-effect-is-rules-applied-not-bypassed](dec-0113-module-effect-is-rules-applied-not-bypassed.md), with the rows of the status matrix. Every item has its home, so the record is `inactive`.

## Carry list

1. R1, R2, R3, R4, R5, R6, R7, R8 — pending: [item 9.33a of the rollout plan](../rollout-plan.md#s9-33a).
2. R9, R10 — pending: [item 9.33a of the rollout plan](../rollout-plan.md#s9-33a) and [item 9.33b](../rollout-plan.md#s9-33b).
3. R11 — pending: [items 9.33a, 9.33b and 9.33c of the rollout plan](../rollout-plan.md#s9-33a).
