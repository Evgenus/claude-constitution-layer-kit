---
id: dec-0047-decision-shape-printed-at-session-start
type: task-record
title: The shape of a decision message is printed at every session start by const-questions, and its skill asks to be loaded before any choice is put
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shape of a decision message is printed at every session start by const-questions, and its skill asks to be loaded before any choice is put

## Context

Row [A6.2](../requirements.md#a6-2) fixes the shape of a decision put to the user in chat: lettered options, each with **Pros:** and **Cons:** sub-bullets, one recommendation, the decider named. From 2026-09-14 the kit's guide carried it in its session-conduct block. On 2026-09-25 module [`const-questions`](../requirements.md#const-questions) landed with the shape in its skill `ask-or-decide`. On 2026-09-26 the guide's copy was trimmed, as R2 of [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md#r2) planned, leaving the skill as the shape's only home. The module printed nothing at session start: its comparison's live runs had shown the skill's description reaching the model when a choice arose (a5, a6 of [res-0007-const-questions](../research/res-0007-const-questions.md)), and the module deferred an always-on carrier behind the signal "a session that asked in the wrong shape without ever loading the skill, observed in a consumer twice" (item 4 of its deferred list, as it stood).

The kit's own sessions of 2026-09-26 showed the failure. The `const-styling` session, which had loaded the skill at 02:35 and kept the shape for twelve hours, put its last sub-bullet decision at 14:11 and its next one, at 18:54, with the pros and cons inline in prose. The `const-language` session, from 23:42 that day, put eight lettered decisions in the inline shape and never loaded the skill. Its only skill call was the carry audit. The decider noticed on 2026-09-27 and asked for a fix. Nothing in the repository had changed: the skill still stated the shape. The mechanism had failed, not the rule.

The shape has no fixture, by [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): it is advisory, and its one proof was a live run of 2026-09-25 whose first tool call was the skill. That run never covered a session that does not load it.

## Options

- **A. A `SessionStart` hook in `const-questions` that prints the shape.** The module gains a session-start hook, as `const-interaction` and `const-referencing` have, printing the shape in short and pointing to the skill for the rest. A fixture pins the printed text and its phrases to the skill's wording. A live item proves the shape in a session that never loads the skill.
  - **Pros:**
    - **the module keeps its own row** ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)) and stays independent ([law 3 of CLAUDE.md](../../CLAUDE.md#law-3));
    - **the carrier is one** the kit has proven in two modules;
    - **consumers get the fix** by version bump;
    - **the missing proof** becomes a standing item;
    - **the hook runs again** after a compaction, when the earlier context is gone.
  - **Cons:**
    - **a few hundred characters** in every session for every consumer;
    - **the module document's carrier reasoning** and the comparison's reading are overturned on the kit's evidence alone, one clean observation and one weak;
    - **the module's version bumps**.
- **B. One line in the `const-interaction` session-start text.** The shape rides on the sibling's existing carrier.
  - **Pros:** no new hook.
  - **Cons:**
    - **a row of** `const-questions` implemented by another module is scope creep on one side and incompleteness on the other ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)), and it couples the two ([law 3 of CLAUDE.md](../../CLAUDE.md#law-3));
    - **a consumer with only** `const-questions` installed gets nothing.
- **C. Sharpen the skill description so that it triggers on every decision.** No new carrier; the description is rewritten to ask for the skill to be loaded before any message that puts a choice.
  - **Pros:** the smallest change; no always-on cost; the skill, once loaded, carries the whole rule and the project's preferences.
  - **Cons:**
    - **the description already said** "Use when about to ask the user anything" and the `const-language` session never loaded it;
    - **alone, the same mechanism that failed**, with no way to prove it holds.
- **D. Put the shape back into the kit's guide.** CLAUDE.md carries it again, as before 2026-09-26.
  - **Pros:** immediate and certain for the kit.
  - **Cons:**
    - **it reverses R2 of** [dec-0041-questions-module-rulings](dec-0041-questions-module-rulings.md#r2) and fixes only consumer zero;
    - **every consumer keeps the drift**;
    - **the kit stops dogfooding** its own module.

## Recommendation

A: it fixes the failure where it was observed, in every consumer at once, and turns the one-time live proof into a standing one. The session recommended it.

## Choice

A and C together, chosen by the decider in chat on 2026-09-27: the always-on print for the shape, and the sharpened description so that the skill, which carries the rest, is loaded before a choice is put.

## Ruling

<a id="r1"></a>**R1.** Module [`const-questions`](../requirements.md#const-questions) prints the shape of a decision message at every session start: a `SessionStart` hook without a matcher, so that it runs again after a resume, a compaction and a clear, running a POSIX script that reads nothing and prints one fixed text — the lettered options, the **Pros:** and **Cons:** sub-bullets, never inline and never a table, one recommendation, the decider named, the one-fact exemption, and the instruction to load the skill before any choice is put. The text is advisory, stated in the module document with its size. The skill stays the full carrier of rules Q-a to Q-i.

<a id="r2"></a>**R2.** The fixture runner pins the printed text character for character, its size against the module document, and the phrases the text shares with the skill's shape section, so that the two carriers cannot drift apart. The hooks-file item covers both handlers. A live item proves the shape in a headless session that never loads the skill, and the skill's loading in one that is told nothing about skills.

<a id="r3"></a>**R3.** The description of the skill `ask-or-decide` asks for the skill to be loaded first, before the reply is written, every time a message will put options, a recommendation or a question to the user, whether or not the shape seems known.

<a id="r4"></a>**R4.** The enforcement of [A6.2](../requirements.md#a6-2) names both carriers: the skill and the `SessionStart` hook, advisory.

<a id="r5"></a>**R5.** The always-on carrier the module had deferred is added ahead of its signal, on the kit's evidence as consumer zero: one session that never loaded the skill and put eight decisions in another shape, and one that lost the shape twelve hours after loading it. The deferred item is closed. The comparison's reading (a5, a6 of [res-0007-const-questions](../research/res-0007-const-questions.md)) stands as written, frozen, and the module document says what later evidence showed.

<a id="r6"></a>**R6.** The module's manifest version is `0.0.2`.

## Applied

The commit that creates this record adds the script and the hook, sharpens the description, adds the fixture and reworks the hooks-file item, edits the module document — the purpose, the row, the decisions, Q-b, the artifacts, the always-on content, a platform fact, the research reading, the enforcement table, the acceptance items, the deferred list — the install note, the manifest and the matrix row. The record is born `inactive`, every item having its home, and awaits its yes.

## Carry list

1. R1 — [§6](../../modules/const-questions/MODULE.md#t6) of the module's document, the hook and script rows and the always-on content; [§9](../../modules/const-questions/MODULE.md#t9), item E4; [§5](../../modules/const-questions/MODULE.md#t5), rule Q-b.
2. R2 — [§10](../../modules/const-questions/MODULE.md#t10) of the module's document, items T15, T20 and L5.
3. R3 — the description of the skill `ask-or-decide`; [§6](../../modules/const-questions/MODULE.md#t6), the skill row; [§3](../../modules/const-questions/MODULE.md#t3), the row [A6.2](../requirements.md#a6-2).
4. R4 — the row [A6.2](../requirements.md#a6-2) of the requirements matrix, its enforcement column.
5. R5 — history only: the observation of 2026-09-26 and the closing of the deferred item; [§1](../../modules/const-questions/MODULE.md#t1) of the module's document names the observation.
6. R6 — the module's manifest; [§6](../../modules/const-questions/MODULE.md#t6) of the module's document, the manifest row, and its version line.
