---
id: dec-0113-module-effect-is-rules-applied-not-bypassed
type: task-record
title: 'A module is measured by its effect: each of its rules applied, bypassed or missed, judged by a pattern where one can see it and by a reader only where none can'
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A module is measured by its effect: each of its rules applied, bypassed or missed, judged by a pattern where one can see it and by a reader only where none can

## Context

The decider asked how to measure the use and the efficiency of the kit's modules in a consumer project, with the knowledge kit as the example. The decider asked first for a definition of a module's efficiency. The session put two questions in chat, one per message: what efficiency is, on 2026-11-06, and how an advisory rule is judged, on 2026-11-07.

Before the first question, the session read what the knowledge kit already holds. Its gate logs, the output log each gate writes under the dial `log_dir` of its namespace in the project's `constitution.yaml`, held about 1,060 records, all from 2026-11-05 and 2026-11-06. Its 8 session transcripts held 240 writes of Markdown files through the tools `Write` and `Edit`, which the hooks see. They also held 36 shell commands that name a Markdown file and match a crude pattern of a write. Most of these wrote a scratch file or a commit message; some changed the tree, such as a `git mv`. The data could not tell which of them a hook saw, for three reasons:

- **G1.** A green record of a hook does not name the file it examined, so the logs cannot be joined with git or with the transcripts file by file.
- **G2.** The file that switches a module off for one clone, `.claude/settings.local.json`, is outside git, so a switch-off leaves no history.
- **G3.** A record of a block is not linked to the act that came after it; the transcripts can supply that link.

## 1. What a module's efficiency is

- **A. Outcome per cost.** Five measures: reach, catch, teach, noise and cost, where cost is the characters a module adds to a session, its hooks' time and the human turns it takes.
  - **Pros:** answers whether a module is worth its cost; tells a module that helps from one that nags; points at what to fix.
  - **Cons:** needs new fields in the log and a report that joins logs, transcripts and git; "found later" needs judgment.
- **B. Use only.** Count hook runs, skill loads and their timing, and characters.
  - **Pros:** the data mostly exists; cheap; deterministic.
  - **Cons:** says whether a module is used, not whether it helps; a noisy module reads as an active one.
- **C. Counterfactual.** Run the same tasks with the module on and off, and compare defects and cost.
  - **Pros:** the strongest evidence of value; isolates one module from the others.
  - **Cons:** costly in subscription runs; artificial tasks, not the project's real work; a small sample.

The session recommended A, since B is its first layer and C can follow for a module that A shows as doubtful. The decider chose none of the three as offered, in chat on 2026-11-06. Tokens and milliseconds matter little; the effect matters. The modules set rules for the model, so the measure checks that each rule is applied and not bypassed. That drops the cost side of A and keeps its outcome side, recast as rules applied.

<a id="r1"></a>**R1.** A module's efficiency in a project is its effect: at each moment where one of its rules applies, whether the rule was applied, bypassed or missed. It is counted per rule and summed per module, the counts of each judge apart, as R5 says. Cost is no part of it: characters, tokens and time are not counted against the effect, and the characters a module adds stay what [the kit's metrics report](../../scripts/metrics.py) gives.

<a id="r2"></a>**R2.** For a gate, the work can go around it in four ways, and the measure counts each:

- **B1 Path bypass.** A file in the gate's territory changed without its hook examining it: a shell write, a script, `git mv`, a merge or a checkout.
- **B2 Switch-off.** The module was switched off for a clone, its severity lowered to warn, or one of its dials loosened, such as a narrower territory or a new exception.
- **B3 Workaround after a red.** After a block, the next act is not the fix the message teaches but another path to the same end: the shell, a rename out of the territory, another file. A red followed by the taught fix, with no human turn between them, counts as applied.
- **B4 Escape.** The invariant is broken on the main branch anyway, as a later scan or the project's CI finds it.

<a id="r3"></a>**R3.** For an advisory rule, the measure counts two ways:

- **B5 Skill skipped.** The act took place at the skill's moment with no load of the skill before it.
- **B6 Shape missed.** The rule's visible form is absent where the rule asks for it, such as options without letters or an owed trailer missing.

## 2. How an advisory rule is judged

A pattern can check some of the misses of R3, such as the order of a skill load. Others, such as plain language in chat or a question priced right, only a reader can judge. The session asked which judge the measure uses for an advisory rule.

- **A. Patterns only.** Deterministic checks over the transcripts and git: the order of skill loads, the letters, the "Assumptions:" heading, the trailers.
  - **Pros:** reproducible; honest as a count; cheap to run again on every new session.
  - **Cons:** misses the rules no pattern can see, such as plain language in chat or whether a question was priced right; a well-formed bad answer counts as applied.
- **B. A reader only.** A fresh reader, a language model, reads each transcript against each rule and marks it applied, bypassed or missed.
  - **Pros:** covers every rule, the judgment ones included; can explain each miss.
  - **Cons:** a judgment that looks like a number, which [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) warns against; its results drift between runs and models.
- **C. A pattern where one can see the rule, a reader only where none can.** Each rule is tagged with its judge, and the report keeps the two kinds of count apart.
  - **Pros:** the split the kit already uses for its eval cases; deterministic numbers stay deterministic; the judgment rules are still covered.
  - **Cons:** two mechanisms to build and keep; each rule needs a tag, which is review work per module.

The session recommended C: it follows a rule the kit has already accepted for eval cases, and it keeps the honesty of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5). The decider chose C in chat on 2026-11-07.

<a id="r4"></a>**R4.** Each rule the measure counts is tagged with its judge. A rule is judged by a deterministic pattern over what the project already holds, such as its transcripts, its gate logs and its git history, wherever a pattern can see the rule. It is judged by a fresh reader, a language model, only where no pattern can see it.

<a id="r5"></a>**R5.** The report keeps the counts of patterns and the counts of readers apart and never adds them into one number, so that a reader's verdict never stands as a check.

<a id="r6"></a>**R6.** The measure is a report and never a gate: it blocks nothing, it sets no threshold, and no check holds its numbers.

<a id="r7"></a>**R7.** Where the report runs, and what it needs from the gate logs, such as the file a green record examined, are settled by the report's own design, at the stakes that design prices.

## Applied

The change adds the open item 9.33 to [the rollout plan](../rollout-plan.md#s9-33), which holds R1 to R7 until the report is built, with the rows of the status matrix. Every item has its home, so the record is `inactive`.

## Carry list

1. R1, R2, R3, R4, R5, R6, R7 — pending: [item 9.33 of the rollout plan](../rollout-plan.md#s9-33).
