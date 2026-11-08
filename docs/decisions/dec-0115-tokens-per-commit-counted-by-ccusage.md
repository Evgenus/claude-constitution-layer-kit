---
id: dec-0115-tokens-per-commit-counted-by-ccusage
type: task-record
title: 'Tokens per commit: ccusage counts each commit window of one session, read from a folder that holds that session alone'
status: active
stakes: process
decider: Eugene Chernyshov
---

# Tokens per commit: ccusage counts each commit window of one session, read from a folder that holds that session alone

## Context

The decider asked in chat on 2026-10-27 whether the kit can know how many tokens a session spent to make each commit, while several sessions work on the repository at once. On 2026-11-08 the decider stated what the count must do. A session's count for a commit must not change because other sessions exist, and it must hold all the work done in that session: its subagents, its workflow agents and its advisor model. A count of tokens here measures what a session spent, not the size of a document, so [law 8 of CLAUDE.md](../../CLAUDE.md#law-8) is not touched.

Claude Code writes one transcript per session, a file of JSON lines in the `projects` folder of its configuration folder. Each reply of the model stands there with its token counts, in a format the platform does not document. Two facts found on the kit's own transcripts shaped the design:

- **Copies across sessions.** A forked or resumed session copies the earlier session's records into its own transcript, with the same message id, request id and time; most copies take the new session's id. On 2026-10-28, 3,699 of the 18,607 replies in the kit's transcripts stood in two sessions or more, and no field said which session made them.
- **Partial records.** A subagent's reply can be written twice, first with a partial output count. In one session 94 replies were, and a count that kept the first record of each lost 73,172 tokens.

ccusage is a widely used open-source tool, under the MIT license, that reads these transcripts and reports tokens and cost by day, week, month and session. Its command `ccusage claude session --id <id> --json` lists every reply of one session with its time and its four counts. It offers no library: its npm package ships a command alone, and its Rust crates are not published. The session puts the other questions of this design in chat, one per message, and each adds a section here.

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

<a id="r1"></a>**R1.** The tokens of a commit are counted by ccusage, at the version the kit pins, through `ccusage claude session --id <session> --json --offline`. The kit's own code reads no token count from a transcript. It reads only a record's time, its session id and its ids, to cut and to copy.

<a id="r2"></a>**R2.** ccusage reads a throwaway folder, named to it by `CLAUDE_CONFIG_DIR`, that holds only copies of one session's files: its own transcript, and every transcript under the folder named after it, its subagents and its workflow agents included. The copies are plain files, since ccusage's walk of a folder skips symbolic links.

<a id="r3"></a>**R3.** A session owns only the records dated at or after its start, as its start log gives it. So the history that a fork or a resume copies in stays with the session that made it.

<a id="r4"></a>**R4.** A commit of a session gets that session's replies dated after its previous commit and up to this commit. All the records of one reply, one message id and one request id, go into the window of its first record, so a reply that spans a commit is counted once.

<a id="r5"></a>**R5.** A commit is counted once its window is complete, that is once the session's transcript holds a record dated after the commit or the session has ended, since the platform writes the transcript later than the conversation. A count is written once and is not made again.

<a id="r6"></a>**R6.** For each commit the kit keeps the four counts — input, output, cache write and cache read — with the total and the cost ccusage computes, the session's id and the ccusage version. The cost of each reply in ccusage's output is not used: it reads a field that the current transcripts do not have, and stands at 0.

<a id="r7"></a>**R7.** Two logs are written when things happen. A `SessionStart` hook writes the session's id, its start time and the start's source, which Claude Code gives the hook. A git `post-commit` hook writes the commit's SHA, its time and the session id from the variable `CLAUDE_CODE_SESSION_ID`, which Claude Code sets for the shell commands a session runs and does not document. A commit with no session id is logged with none and gets no count, and the report names it.

<a id="r8"></a>**R8.** The pinned version of ccusage stands in `scripts/ccusage.version`, beside the pin of Claude Code. Before the pin moves, a small transcript with a known count is counted by the new version, and the pin moves only when it gives that count.

## Carry list

1. R1, R2, R3, R4, R5, R6, R7, R8 — pending: [item 9.34 of the rollout plan](../rollout-plan.md#s9-34).
