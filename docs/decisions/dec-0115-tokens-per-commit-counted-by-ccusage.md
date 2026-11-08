---
id: dec-0115-tokens-per-commit-counted-by-ccusage
type: task-record
title: 'Tokens per commit: a new module has ccusage count each commit window of one session, read from a folder that holds that session alone'
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Tokens per commit: a new module has ccusage count each commit window of one session, read from a folder that holds that session alone

## Context

The decider asked in chat on 2026-10-27 whether the kit can know how many tokens a session spent to make each commit, while several sessions work on the repository at once. On 2026-11-08 the decider stated what the count must do. A session's count for a commit must not change because other sessions exist, and it must hold all the work done in that session: its subagents, its workflow agents and its advisor model. A count of tokens here measures what a session spent, not the size of a document, so [law 8 of CLAUDE.md](../../CLAUDE.md#law-8) is not touched.

Claude Code writes one transcript per session, a file of JSON lines in the `projects` folder of its configuration folder. Each reply of the model stands there with its token counts, in a format the platform does not document. Two facts found on the kit's own transcripts shaped the design:

- **Copies across sessions.** A forked or resumed session copies the earlier session's records into its own transcript, with the same message id, request id and time; most copies take the new session's id. On 2026-10-28, 3,699 of the 18,607 replies in the kit's transcripts stood in two sessions or more, and no field said which session made them.
- **Partial records.** A subagent's reply can be written twice, first with a partial output count. In one session 94 replies were, and a count that kept the first record of each lost 73,172 tokens.

ccusage is a widely used open-source tool, under the MIT license, that reads these transcripts and reports tokens and cost by day, week, month and session. Its command `ccusage claude session --id <id> --json` lists every reply of one session with its time and its four counts. It offers no library: its npm package ships a command alone, and its Rust crates are not published. The session put the questions of this record in chat on 2026-11-08, one per message.

## 1. What counts the tokens, and how other sessions are kept out

- **A. A parser of the kit's own.** A kit script reads the transcripts and counts the tokens itself.
  - **Pros:** the kit holds every rule and sees every field; no tool from outside the kit.
  - **Cons:** the kit must follow every change of a format the platform does not document; the session's first parser kept the partial records and lost 73,172 tokens in one session.
- **B. ccusage over all the transcripts.** The kit runs ccusage's session command on the platform's own folder and splits its replies at the session's commits.
  - **Pros:** ccusage keeps up with the format and the prices; the least code in the kit.
  - **Cons:** of a copied reply ccusage keeps the copy whose file path sorts first, so a fork can take its parent's work; in a run on 2026-11-08, putting a parent's folder after its fork's dropped the parent from 2,083 replies to 1,763 and from $100.14 to $50.56.
- **C. ccusage over a folder that holds one session alone.** The kit copies one session's files, cut at the session's start and at its commits, into a throwaway folder, and runs ccusage there.
  - **Pros:** ccusage still does the reading and the pricing; no other session's files stand in the folder, so none can change the count; on 2026-11-08 it gave the same count in every folder order, and in six commit windows it matched a count made apart from it, reply for reply.
  - **Cons:** the kit must log each session's start and each commit as they happen; it copies files for every count; it depends on a command whose output carries no promise of stability, with 19 releases in the month to 2026-10-27.
- **D. Claude Code's telemetry.** The platform exports a token count for every request over OpenTelemetry, with the session's id, to a collector the kit runs.
  - **Pros:** a documented interface; it sees requests that may never reach a transcript, such as a compaction.
  - **Cons:** a collector must run from a session's first request; the commit's SHA reaches an event only with `OTEL_LOG_TOOL_DETAILS=1`, and reports on the platform's issue tracker, which the session did not test, say it is lost for some forms of `git commit`; no past session can be counted.

The session recommended A on 2026-10-28, since B fails the decider's rule. Once the decider asked to build on ccusage, the session read ccusage's source and recommended C: it keeps ccusage for the reading and the pricing, and keeps the other sessions out of the folder it reads.

The decider chose to build on ccusage, in chat on 2026-11-08, since a tool this widely used is likely to be kept up to date. The session then proposed C and ran it that day, and the decider asked for this record built on it.

<a id="r1"></a>**R1.** The tokens of a commit are counted by ccusage, at the version the kit pins, through `ccusage claude session --id <session> --json --offline`. The module's own code reads no token count from a transcript. It reads only a record's time, its session id and its ids, to cut and to copy.

<a id="r2"></a>**R2.** ccusage reads a throwaway folder, named to it by `CLAUDE_CONFIG_DIR`, that holds only copies of one session's files: its own transcript, and every transcript under the folder named after it, its subagents and its workflow agents included. The copies are plain files, since ccusage's walk of a folder skips symbolic links.

<a id="r3"></a>**R3.** A session owns only the records dated at or after its start, as its start log gives it. So the history that a fork or a resume copies in stays with the session that made it.

<a id="r4"></a>**R4.** A commit of a session gets that session's replies dated after its previous commit and up to this commit. All the records of one reply, one message id and one request id, go into the window of its first record, so a reply that spans a commit is counted once.

<a id="r5"></a>**R5.** A commit is counted once its window is complete, that is once the session's transcript holds a record dated after the commit or the session has ended, since the platform writes the transcript later than the conversation. A count is written once and is not made again.

<a id="r6"></a>**R6.** For each commit the module keeps the four counts — input, output, cache write and cache read — with the total and the cost ccusage computes, the session's id and the ccusage version. The cost of each reply in ccusage's output is not used: it reads a field that the current transcripts do not have, and stands at 0.

<a id="r7"></a>**R7.** Two logs are written when things happen. A `SessionStart` hook writes the session's id, its start time and the start's source, which Claude Code gives the hook. A commit log writes each commit's SHA, its time and the session that made it, by the route R10 leaves to the module's rulings. A commit with no session is logged with none and gets no count, and the report names it.

<a id="r8"></a>**R8.** The module pins the version of ccusage it runs, in a file of its plugin. Before the pin moves, a small transcript with a known count is counted by the new version, and the pin moves only when it gives that count.

## 2. Where the count lives

The count must ship to every project that uses the kit, not serve the kit alone, the decider said in chat on 2026-11-08. A plugin can hold every part of it. Its `SessionStart` hook receives the session's id and the start's source, and its tool hooks fire inside subagents too, with the agent's id. ccusage needs Node and npm in the project, as module [`const-referencing`](../requirements.md#const-referencing) needs lychee and module [`const-language`](../requirements.md#const-language) needs Vale. A plugin cannot install a git hook, so the commit log of R7 takes one of two routes. Git's hooks set in its configuration run beside a project's own hooks and need one step per clone. A check after each tool call lists the commits made during it and needs no step, but two sessions that commit in one checkout at one moment would both claim the commit.

- **A. A new module with an aspect of its own.** A plugin built through the kit's module routine, its rows a new aspect of the requirements matrix.
  - **Pros:** it passes the three boundary tests of the matrix; a project chooses to install it; its need for Node and ccusage touches no other module; it reads only its own dials.
  - **Cons:** the whole module routine, from the research round to both reviews; the aspect must state a failure class, since the [intent page](../../INTENT.md#i5) keeps out a module for a failure nobody has hit, and a count measures more than it governs.
- **B. New rows in module [`const-task-close`](../requirements.md#const-task-close).** The module whose object is the change gains the count, the start log and the commit log.
  - **Pros:** its object is already the change and its commits; one install fewer; it already ships the hooks the count needs.
  - **Cons:** it fails the one-invariant test, its invariant being documents kept in step with the code; every project that installs its gate would need Node and ccusage, or meet a configuration failure; every change to the count would bump that module and make its eval receipt stale.
- **C. Inside the effect report.** The shared runner of [aspect A14](../requirements.md#a14) also counts tokens per commit, by a record that reverses [A14.1](../requirements.md#a14-1), which keeps cost out of a module's effect.
  - **Pros:** it already reads transcripts, blocks nothing and takes a transcript folder and a start date.
  - **Cons:** the effect report counts each module's own rules, and a token count is no module's rule; the shared package, which every module installs, would need Node.

The session recommended A, the only option that passes the boundary tests and keeps ccusage away from a project that wants only the existing gates. The decider chose A in chat on 2026-11-08.

<a id="r9"></a>**R9.** The count ships as a new module of the kit, whose rows are a new aspect of the requirements matrix. No existing module carries any part of it.

<a id="r10"></a>**R10.** The module is built by the routine of "Developing a module" in [CLAUDE.md](../../CLAUDE.md), its research round first. Its own rulings record, written after that round, answers what this record leaves open: where the counts are kept, which route the commit log takes, how the work of a session's parallel agents is split between its commits, what a session from before its start log gets, and when the count runs, so that it is made before Claude Code deletes the transcript.

<a id="r11"></a>**R11.** The aspect states this failure class: a session's start and the session behind each commit are lost for good when no hook records them as they happen.

## 3. The module's name

The module's folder and its research comparison are named after it, so its name comes before the research round, as steps 1 and 2 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md) order them. The kit names a module `const-` and its aspect.

- **A. `const-change-cost`, the aspect "Change cost".** The name of the kit's own unit of work.
  - **Pros:** "change" is the word the kit uses for the unit module [`const-task-close`](../requirements.md#const-task-close) closes; the cost of a pull request is the sum of its changes.
  - **Cons:** a change can span several commits, while the module counts per commit.
- **B. `const-commit-cost`, the aspect "Commit cost".** The name of the unit the module counts.
  - **Pros:** it names exactly what is counted.
  - **Cons:** it names git's unit, not the kit's.

The session recommended A, the kit's own word for its unit of work. The decider chose A in chat on 2026-11-08.

<a id="r12"></a>**R12.** The new plugin is named `const-change-cost`, and its aspect is A15, "Change cost", of the requirements matrix.

## 4. The module's failure class

Every module's heading in the requirements matrix states its class, and [template §2](../../module-template/MODULE.md#t2) says what the class brings: an accumulating module belongs in every project's day-one install set, a self-limiting one waits for its friction signal, and a module may be split into an accumulating slice and a self-limiting rest. The count's evidence expires too. Claude Code deletes the transcripts of command-line sessions after `cleanupPeriodDays`, 30 days by default, without a message, as [its settings reference](https://code.claude.com/docs/en/settings-reference.md) says. It keeps the transcripts of desktop app sessions at any age unless `desktopSessionCleanupPeriodDays` is set.

- **A. Accumulating, the whole module.** It belongs in every project's day-one install set, and its logs and its count run from the first session.
  - **Pros:** no session is ever missed; every count is made while its transcript still exists.
  - **Cons:** every new project needs Node and ccusage on its first day, even one that never reads a count.
- **B. Accumulating logs, a self-limiting count.** The start log and the commit log are installed on the first day and need no Node; the count needs ccusage only when it runs.
  - **Pros:** the first day costs two small hooks; the part that can never be made later is always there; ccusage is needed only when a project wants its counts.
  - **Cons:** a count made more than 30 days late finds a command-line session's transcript gone, unless the module keeps its own copies; one module with two classes is more to explain.
- **C. Self-limiting, the whole module.** It enters when a project first asks what its changes cost.
  - **Pros:** nothing is installed until someone wants it; the simplest heading.
  - **Cons:** every session before the install is lost for good, the loss R11 names.

The session recommended B, which keeps the first day cheap and never loses what cannot be made later. The decider chose A in chat on 2026-11-08 and gave no other reason. The session keeps one cost in view: every new project now needs Node and npm on its first day.

<a id="r13"></a>**R13.** `const-change-cost` is accumulating as a whole. It belongs in every project's day-one install set, and its logs and its count run from the project's first session that commits.

## Applied

The change that holds this record adds aspect A15, rows [A15.1](../requirements.md#a15-1) to [A15.6](../requirements.md#a15-6), and the specification of `const-change-cost` to the requirements matrix: adding a row is a `process` ruling under [rule 2 of plc-0007-requirements](../policies/plc-0007-requirements.md#r2), and this record's yes covers it. The module itself is built by [item 9.34 of the rollout plan](../rollout-plan.md#s9-34).

## Carry list

1. R1, R2 — [row A15.2 of the requirements matrix](../requirements.md#a15-2).
2. R3, R4 — [row A15.3 of the requirements matrix](../requirements.md#a15-3).
3. R5, R6 — [row A15.4 of the requirements matrix](../requirements.md#a15-4).
4. R7 — [row A15.5 of the requirements matrix](../requirements.md#a15-5).
5. R8 — [row A15.2 of the requirements matrix](../requirements.md#a15-2) for the pin's place, and [row A15.6](../requirements.md#a15-6) for the known count.
6. R9, R11, R12, R13 — [the module's specification in the requirements matrix](../requirements.md#const-change-cost), its heading and its invariant, and [aspect A15](../requirements.md#a15).
7. R10 — pending: [item 9.34 of the rollout plan](../rollout-plan.md#s9-34).
