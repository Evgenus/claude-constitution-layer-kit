---
id: dec-0079-skills-named-at-their-moment
type: task-record
title: Module skills named at the moment they apply
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Module skills named at the moment they apply

## Context

The kit ships eleven modules as plugins, with thirteen skills. A usage study read the local session transcripts from 2026-09-14 to 2026-10-10 and the kit's CI. It found that the model loaded only five skills: `ask-or-decide` 45 times, `record-decision` 6, `new-document` 6, `set-ceilings` 2 and `new-kind` 1. All thirteen stood in full in the skill listing of 48 to 73 sessions, so no skill was hidden. The study named several causes. Three were judged acceptable and are out of scope: a gate message that already teaches the fix, the kit's own guide restating a procedure, and a rare trigger. Three are this record's:

- **C1.** Nothing outside the skill points to it. The skills that are loaded have such a pointer: the session-start text of module [`const-questions`](../requirements.md#const-questions) says to load `ask-or-decide` before any choice is put, and the kit's guide asks for `new-document`. The skills never loaded have none. No gate's red names its skill: module [`const-language`](../requirements.md#const-language) blocked 125 times and module [`const-referencing`](../requirements.md#const-referencing) 7 times, with no load of their skills. The one pointer that existed, in the turn-end report of module [`const-task-close`](../requirements.md#const-task-close), never fired: 0 dirty trees in 1,335 runs.
- **C5.** Subagents never load the skills. Subagents made 1,965 of the 3,304 hook runs on a write, 59%. None of the seven kit agents lists the `Skill` tool, and 482 general-purpose subagents had the listing and loaded no skill.
- **C6.** A description that opens "Use when…" may be weaker than one that gives an order. The one skill loaded often opens "Load this skill first…"; the unused ones open "Use when…". One case against twelve is a hypothesis, so it is put to a live proof before anything relies on it.

The platform's documentation, read on 2026-10-10 on its raw pages with Claude Code 2.1.286 installed, says four things this record relies on. A `SessionStart` hook's plain standard output is added to the model's context ([hooks](https://code.claude.com/docs/en/hooks#exit-code-0)). A `SubagentStart` hook cannot block a subagent, but its `additionalContext` is added to the subagent's context before its first prompt ([hooks](https://code.claude.com/docs/en/hooks#subagentstart)). The hooks of a plugin also run inside subagents. A subagent loads a skill only through the `Skill` tool, and leaving the tool out of an agent's `tools` stops skills entirely ([sub-agents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents)).

## 1. How a skill is named at its moment

A skill applies at one of two moments: before a write, as the styling, language, type, catalog and task skills do, or after a gate's red, when the gate has named the problem. A pointer costs characters in every session that carries it ([law 8 of CLAUDE.md](../../CLAUDE.md#law-8)).

- **A. A gate pointer only:** one shared line after the count line of every red of a gate whose module has a skill.
  - **Pros:** no cost in a session without a red, about 100 characters a red; it reaches the 125 and the 7 blocks at the moment they happen; one change of the shared code, which the fixtures take, since the harness counts only lines that open `RED:`.
  - **Cons:** nothing reaches the moment before a write; the styling skill, whose module has no hook, and the task skills, whose report never fired, stay unnamed.
- **B. The gate pointer and one session-start line per module whose skill applies before a write:** A, plus a line at session start that names the skill and its moment.
  - **Pros:** it reaches both moments; it copies the one pointer with proven reach, `ask-or-decide` with 45 loads; every skill in scope is covered.
  - **Cons:** every session pays about 1,050 characters; four modules gain their first session-start hook, with its script, its fixture and its always-on slot.
- **C. Session-start lines only:** B without the gate pointer.
  - **Pros:** it reaches the moment before a write and leaves the shared code alone.
  - **Cons:** it costs B's characters; a red still teaches its fix without naming the skill, the case with 125 blocks and no load.
- **D. A pointer line for the consumer's `CLAUDE.md`:** each module's one allowed install pointer, copied by hand.
  - **Pros:** no code; the guide's line for `new-document` shows that such a line works.
  - **Cons:** manual, and it drifts with each version; [template §6](../../module-template/MODULE.md#t6) ships always-on rules by hook, never this way; it grows the kit's own guide.

The session recommended B: A alone leaves the skills with no gate moment out, and C alone leaves out the moment with the most evidence. The decider chose B in chat on 2026-10-10.

**R1.** A gate whose module has a skill that teaches its rule names that skill in one shared line after the count line of every red the model reads: in the block, in the warn's context, in the reason of an `ask`, and in a scan's output. The user's notice on a turn's end at `warn`, which no model reads, does not carry it. The gate's identity maps each of its modes to the skill. Module [`const-interaction`](../requirements.md#const-interaction) has no skill, and its gate names none.

**R2.** Modules [`const-catalogs`](../requirements.md#const-catalogs), [`const-language`](../requirements.md#const-language), [`const-meta-types`](../requirements.md#const-meta-types), [`const-referencing`](../requirements.md#const-referencing), [`const-styling`](../requirements.md#const-styling) and [`const-task-close`](../requirements.md#const-task-close) each print one advisory pointer line at session start: `<module> (advisory): before <the moment>, load the skill <module>:<skill>.` The six lines hold 1,247 characters together, not the 1,050 of the estimate the choice was put with; the plugin-qualified skill names make most of the difference. A module whose skill applies only after its gate's red, or whose skill already has a pointer, prints none.

**R3.** The decider's choice of B carried a condition: if the live proof of section 3 showed that a description which gives an order brings the loads by itself, the session would put the removal of R2's lines to the decider before the yes. The proof showed it for one skill, the question was put in section 3, and the decider kept the lines.

## 2. How the skills reach subagents

Modules ship no agents, so a module cannot change a consumer's agent definitions ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2), [law 3](../../CLAUDE.md#law-3)). What it can ship is a hook, and its hooks also run inside the consumer's subagents. The kit's own agents are kit tooling, never shipped.

- **A. The kit's writing agent gets `Skill`; the modules repeat their pointer at `SubagentStart`:** `Skill` joins the tools of the implementer, the one kit agent that writes the kit's tracked files, and each module of R2 gives its line to every subagent.
  - **Pros:** it reaches every subagent, the general-purpose ones and the consumer's included, in the words the main session reads; no new text is written; the implementer can act on both pointers.
  - **Cons:** each subagent's start pays the same characters as a session's; the six modules gain a second hook event with a fixture; that the line brings a load is not yet proved live.
- **B. As A, with the implementer preloading the skills through `skills:`:** the implementer's frontmatter names `plain-language`, `style-defaults`, `referencing` and `commit-before-edit`.
  - **Pros:** the implementer reads the skills without a choice to make.
  - **Cons:** about 21,100 characters for each implementer's start, whatever its piece; kit tooling names module skills, and breaks when one is renamed.
- **C. The kit's agents only:** `Skill` for the implementer, no module hook.
  - **Pros:** the smallest change, with no cost per start.
  - **Cons:** the general-purpose and the consumer's subagents, most of the 1,965 runs, get no pointer before a write.
- **D. The modules' `SubagentStart` hooks only:** A without the kit's agents.
  - **Pros:** no change of kit tooling.
  - **Cons:** the implementer reads the pointer and cannot act on it.

The session recommended A: it alone reaches the subagents that make most of the writes, at the cost the session line already has. The decider chose A in chat on 2026-10-10.

**R4.** Each module of R2 gives its pointer line to every subagent through a `SubagentStart` hook, as the event's `additionalContext` in one JSON object, since that event adds no plain output to the context. The same script prints both forms.

**R5.** The kit's implementer agent lists the `Skill` tool and is told to load a skill that its start context or a hook's red names. The kit's other agents write no tracked file and keep their tools.

## 3. How a description asks to be loaded

The live proof ran on 2026-10-10 with Claude Code 2.1.286. Each run was one headless session in a fresh clone of the kit's trunk at the commit before this change, with the plugin loaded from a copy of its folder that held one variant. The prompts were two. "Add one paragraph that explains what a gate is, as a single sentence of about 120 words" makes prose the work without naming it, which is the moment of `plain-language`. "Add a short table comparing the three meta-types" names the moment of `style-defaults` outright. The loads:

| key | variant | `plain-language` | `style-defaults` |
|---|---|---|---|
| V0 | the description as it stood, opening with what the skill does and then "Use when…" | 0 of 3 | 3 of 3 |
| V1 | a description opening "Load this skill first, before…" | 3 of 3, each before the write | 3 of 3 |
| V2 | V0 and a session-start pointer line | 2 of 3 | 3 of 3 |
| V3 | V0 and a line naming the skill after the gate's red | 0 of 1 red | not run |
| V4 | V2 and the line at a subagent's start, the work given to a subagent | not run | 2 of 2, by the subagent |

The table prompt named the moment, so it could not tell the variants apart. Under V0, too, subagents loaded the skill, so they read the skill listing. The sample is three runs a cell and two skills of seven.

- **A. Reword the seven descriptions and keep the pointer lines:** the descriptions of `catalog-item`, `plain-language`, `choose-meta-type`, `referencing`, `style-defaults`, `close-task` and `commit-before-edit` open with "Load this skill first, before <the moment>…", and the lines of R2 and R4 stay.
  - **Pros:** two carriers for the moment before a write; a pointer line still stands where the platform drops the descriptions of skills seldom used, which it does when the listing overflows its budget, 1% of the context window.
  - **Cons:** 1,247 characters in every session and again at every subagent's start, for a gain the proof did not measure; six hooks, scripts and fixtures to keep.
- **B. Reword the seven descriptions and remove the pointer lines:** the same rewording; the hooks, scripts and fixtures of R2 and R4 leave the six modules, and the line after a red stays.
  - **Pros:** the variant that did best, at no cost per session or per subagent, since the listing already carries the description; subagents read the listing too; less to keep.
  - **Cons:** one rewording of seven is proved by a prompt that tells the variants apart; a description dropped from an overflowing listing leaves the skill only the line after a red; part of six module commits undone.
- **C. Keep the descriptions as they stood and keep the pointer lines:** section 1's choice as built.
  - **Pros:** no further change.
  - **Cons:** the pointer brought 2 of 3 where the order brought 3 of 3; the weak descriptions stay for every session the pointer does not reach.

The session recommended B: the pointer lines showed no gain over a description that gives an order, at 1,247 characters a session and a subagent. To cover what was not proved, B carried a live run with one fair prompt for each of the other rewordings, its module's line returning for a skill that is not loaded. The decider chose A in chat on 2026-10-10, giving no reason; A keeps both carriers.

**R6.** A module skill's description opens with an order: `Load this skill first, before <the moment> — every time, whether or not <the choice> seems known.` Then it says what the skill does, then, after `Use when`, its other moments, then its `Advisory:` line. The seven descriptions named in option A are reworded so; `plain-language` and `style-defaults` take the words the proof ran.

**R7.** The pointer lines of R2 and R4 stay beside the reworded descriptions.

## Applied

The commits of this branch apply every item. The message of each commit names what it changed and the evidence that it is red without the change and green with it. The record is born `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code](../../shared/GATE.md#g3), the row `F10` of section 3, the `identity` row of [its section 1](../../shared/GATE.md#g1) and item 1 of [its section 2](../../shared/GATE.md#g2); [the module template](../../module-template/MODULE.md#t6), the skill row of section 6.
2. R2 — [the module template](../../module-template/MODULE.md#t6), the skill row and the hook row of section 6; the always-on content of section 6 of [`const-catalogs`](../../modules/const-catalogs/MODULE.md#t6), [`const-language`](../../modules/const-language/MODULE.md#t6), [`const-meta-types`](../../modules/const-meta-types/MODULE.md#t6), [`const-referencing`](../../modules/const-referencing/MODULE.md#t6), [`const-styling`](../../modules/const-styling/MODULE.md#t6) and [`const-task-close`](../../modules/const-task-close/MODULE.md#t6).
3. R3 — history only: the condition was put to the decider in section 3 and answered there.
4. R4 — [the module template](../../module-template/MODULE.md#t6), the hook row of section 6; the hook rows of section 6 of the six modules of R2.
5. R5 — [CLAUDE.md](../../CLAUDE.md), the opening paragraph of "Session conduct"; the implementer's own file applies it.
6. R6 — [the module template](../../module-template/MODULE.md#t6), the skill row of section 6, and [its example skill](../../module-template/skills/example-procedure/SKILL.md), the description.
7. R7 — [the module template](../../module-template/MODULE.md#t6), the skill row of section 6, which asks for both the order and the pointer.
