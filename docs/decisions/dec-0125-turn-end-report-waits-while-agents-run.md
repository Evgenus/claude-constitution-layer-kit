---
id: dec-0125-turn-end-report-waits-while-agents-run
type: task-record
title: The turn-end report of const-task-close waits while an agent of the session still runs
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The turn-end report of const-task-close waits while an agent of the session still runs

## Context

The turn-end hook of module [`const-task-close`](../requirements.md#const-task-close) reads the working tree when a turn ends and reports a dirty tree once. It read the tree and nothing else. A session may start subagents that work in the same tree and commit their own files. While they work, the tree is dirty with their files, and the session can do nothing about that. Yet each turn end of the session got the report. A session that ran six implementer agents ended about eight turns in a row on this one report while it waited. [Item 9.25 of the rollout plan](../rollout-plan.md#s9-25) logged this on 2026-10-13, as a waiting item. The decider's ask of 2026-11-11 to finish the rollout plan started it before its signal recurred.

The question was what the platform gives the hook. The [hooks reference](https://code.claude.com/docs/en/hooks), read on 2026-11-11, lists a field of the `Stop` event that the module's research of 2026-09-23 did not hold: `background_tasks`, the session's tasks still in flight. Each entry has a `type` and a `status`. A headless run on Claude Code 2.1.286 the same day showed the field. A subagent started in the background read `"type": "subagent", "status": "running"` at the turn end, and had left the list at the next turn end, after its answer. No field of the event says which task changed which file. So the hook can know that agents still work, and cannot know whose the dirty files are.

The matrix's row, [requirement A4.7](../requirements.md#a4-7), asks that a tree is never left dirty at turn end and names the hook as its light gate. Its words stand under every option below.

## Options

- **A. Hold the report while agents work.** While the event lists a running agent, the hook does not report the dirty tree: it is green with a line that gives the count of paths and of agents, and it reports as before at the first turn end with none.
  - **Pros:**
    - **it ends the repeated report in the logged case**;
    - **the platform documents the field for this purpose**, and a run showed it;
    - **no state file and no new hook**;
    - **an event without the field behaves as before**.
  - **Cons:**
    - **the session's own uncommitted work also waits until the agents are done**;
    - **an agent that only reads holds the report too**;
    - **it narrows a ruling of the module's founding record**;
    - **the module must read the field from the event itself**, since the shared reader does not carry it.
- **B. Tell the files apart by a write log.** A new hook after each `Write` and `Edit` logs the path with the agent's id. The turn-end hook leaves out the dirty paths that the log gives to an agent still at work.
  - **Pros:** the session's own files are still reported at once.
  - **Cons:**
    - **it does not see files changed through the shell**, so those are still reported as the session's;
    - **it adds a hook on every write**, a state file for each session and its cleanup;
    - **it is not reliable**, and it is much code for a draft module.
- **C. No code change; state the limit.** The module's document gains a limit that nothing reliable tells the files apart. The skill advises running the subagents that write in their own worktrees.
  - **Pros:** honest; no ruling changes; a worktree removes the cause where it is used.
  - **Cons:** the report keeps repeating for agents that share the tree, which is the logged case; it is advice only.

## Recommendation

Option A, recommended by the session. It is the only option that stops the repeated report with a fact the platform states. Its cost is a delay of the report in a session that goes on. Only a session that is closed while its agents run loses it.

## Choice

Option A, chosen by the decider in chat on 2026-11-11, with the session's defaults:

- **the task types that count** are `subagent`, `teammate` and `workflow`;
- **only the status `running` counts**;
- **the hold is the same under both severities**.

## Ruling

<a id="r1"></a>**R1.** While the `Stop` event lists, in `background_tasks`, a task whose `type` is `subagent`, `teammate` or `workflow` and whose `status` is `running`, the turn-end hook of module [`const-task-close`](../requirements.md#const-task-close) does not report a dirty tree. It exits 0 with a green line. The first turn end with no such task reports the tree as before. The module's invariant says so.

<a id="r2"></a>**R2.** The hold is the same under both values of the `severity` dial. Under `block` the model receives nothing and the turn ends. Under `warn` the user's notice waits too.

<a id="r3"></a>**R3.** The held line gives the count of dirty paths and the count of agent tasks that run. It says that the report waits for the first turn end with none. It is a form of the module's message G1.

<a id="r4"></a>**R4.** The other outcomes of the hook keep their lines and their order. A clean tree is the clean line, whoever runs. The second stop of a turn is asked before the hold and keeps its own line.

<a id="r5"></a>**R5.** The hook fails towards the report. An event without the list, a list the hook cannot read, an entry of another shape, a task of another type, a shell task and a monitor among them, and an agent whose status is not `running` all leave the report as it was. None of them is a configuration failure, since the field is the platform's to send.

<a id="r6"></a>**R6.** The module states the limit of the hold as its own. The hook knows that agents run, never whose the dirty files are. So the session's own uncommitted work waits with the agents' files, an agent that only reads holds the report too, and a session that is closed while its agents run gets no report. The backstops are the first turn end with no agent running, the held line with its two counts, and the scan.

<a id="r7"></a>**R7.** The platform fact the hold relies on stands in the module's document with its source, its date and what breaks: the field, its entry's shape, the types of an agent's task, and that no field names a task's files.

<a id="r8"></a>**R8.** The module reads the list from the event's text itself, parsed once into typed entries, and hands the same text to the shared reader. No shared code carries the list. A shared reader that carries it is deferred. Its signal: a second module whose hook needs the session's tasks in flight.

<a id="r9"></a>**R9.** The hold has its fixture of [law 7 of CLAUDE.md](../../CLAUDE.md#law-7): one item that is red without the hold and green with it, the held line typed by hand, with the cases of R2, R4 and R5.

<a id="r10"></a>**R10.** The skill `commit-before-edit` and the module's install note tell that the report waits while an agent of the session runs. The skill adds that the writer commits their own work all the same.

<a id="r11"></a>**R11.** This record narrows one ruling of the module's founding record. Section 3 of that record says that the hook treats any line of the tree's status as dirty at every turn end. R4 of [dec-0036-task-close-module-rulings](dec-0036-task-close-module-rulings.md#r4) rules its severities. For a turn end while an agent of the session runs, R1 makes the outcome green. R4 of that record stands for every other turn end, and no other ruling of that record changes.

## Applied

The first commit of the change's branch changes the hook, its messages and its fixture. The commit that creates this record changes the module's document, its skill, its install note and its README. Every item has its home there, so the record is born `inactive`. The module is a draft and keeps its version ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## Carry list

1. R1 — [section 5 of the module's document](../../modules/const-task-close/MODULE.md#t5), the invariant; [section 3](../../modules/const-task-close/MODULE.md#t3), the row of the commit-before-edit rule; [section 9](../../modules/const-task-close/MODULE.md#t9), row E1 and limit 15.
2. R2 — [section 7 of the module's document](../../modules/const-task-close/MODULE.md#t7), the row `severity`; [section 9](../../modules/const-task-close/MODULE.md#t9), limit 15.
3. R3 — [section 6 of the module's document](../../modules/const-task-close/MODULE.md#t6), message G1 of the error messages.
4. R4, R5, R6 — [section 9 of the module's document](../../modules/const-task-close/MODULE.md#t9), limit 15.
5. R7 — [section 6 of the module's document](../../modules/const-task-close/MODULE.md#t6), platform fact 14.
6. R8 — [section 6 of the module's document](../../modules/const-task-close/MODULE.md#t6), the package row of the table; [section 12](../../modules/const-task-close/MODULE.md#t12), item 9.
7. R9 — [section 10 of the module's document](../../modules/const-task-close/MODULE.md#t10), item 47.
8. R10 — [the skill commit-before-edit](../../modules/const-task-close/plugin/skills/commit-before-edit/SKILL.md), its paragraph on what is checked, and [the module's install note](../../modules/const-task-close/plugin/INSTALL.md), step 1.
9. R11 — history only: the narrowing of one ruling of the founding record, an act of this record.
