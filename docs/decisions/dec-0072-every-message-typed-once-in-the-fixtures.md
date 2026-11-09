---
id: dec-0072-every-message-typed-once-in-the-fixtures
type: task-record
title: Every message a gate can print stands once in its fixtures as a line typed by hand, held by review with a listing aid
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Every message a gate can print stands once in its fixtures as a line typed by hand, held by review with a listing aid

## Context

A module's fixture runner builds many expected lines by calling the same message function the gate calls. Such an expectation proves that the gate chose the right message; it cannot catch a defect inside the message's own text, since gate and test print the same wrong line. A fixture covers the text only where it compares output with a line typed by hand.

On 2026-10-07 a subagent counted it for the kit as `main` then stood. For each message function of the shared code and of the eleven modules, it looked for the function's longest fixed text, 15 characters or more, as a string of the fixtures that run it, then checked at least five functions per module by hand; the hand check corrected four of the script's hits. Of 388 message functions, 341 had their text typed in a fixture and 47 were checked only through their own function: 12 shared, 10 of const-catalogs, 12 of const-referencing and 13 across seven other modules, most of them failures of a malformed dial. None was untested.

The decider was asked in chat on 2026-10-07 whether the kit should do more than fill the 47.

## Options

- **A. Fill the 47, no rule.**
  - **Pros:** the least work; closes the gap counted.
  - **Cons:** nothing stops the next message or module from repeating it.
- **B. Fill the 47, and a rule held by review.** The template's fixtures rule asks for one line typed by hand per message; the fresh-context review holds it, with the counting script as its aid.
  - **Pros:** the gap stays closed for new modules; honest under [law 5 of CLAUDE.md](../../CLAUDE.md#law-5), since the check needs judgment and is not dressed as a gate.
  - **Cons:** a record and its audit; review can miss a case.
- **C. Fill the 47, and a rule held by a kit check.**
  - **Pros:** mechanical and permanent.
  - **Cons:** the counting method needed hand corrections, so a gate built on it would give false reds and greens; the most code.

## Recommendation

B, since it keeps the gap closed and puts a check that needs judgment where judgment lives; the session recommended it.

## Choice

The decider chose B in chat on 2026-10-08.

## Ruling

<a id="r1"></a>**R1.** Every message a module's code can print stands, in the fixtures that run it, at least once as a line typed by hand — its fixed text written out, a value the test computes filled in. A shared message stands so in the shared items or in the fixtures of a module that runs it. The fresh-context review holds the rule; no gate does.

<a id="r2"></a>**R2.** The kit's `scripts/list-message-literals.py`, kit tooling never shipped in a module and never a gate, is the review's aid: for each message function it lists whether a piece of its fixed text, 15 characters or more, stands in a string of the fixtures that run it, and lists apart the functions whose text is too short to find. It decides nothing and exits 0 whatever it finds.

<a id="r3"></a>**R3.** The 47 messages counted are each given one line typed by hand in a fixture that already reaches them, with no new acceptance item.

## Applied

The commits of this branch apply every item: the shared items and one module's case for the shared messages, one commit per group of modules for theirs — each with a mutation of every function's text turning its item red — then the template's rule with the aid, then this record. The record is born `inactive`.

## Carry list

1. R1 — [template §6](../../module-template/gate-script-rules.md#r14), rule 14.
2. R2 — [the listing aid](../../scripts/list-message-literals.py), its docstring; [template §6](../../module-template/gate-script-rules.md#r14), rule 14; [pyproject.toml](../../pyproject.toml), its list of commands.
3. R3 — history only: the fixtures of the shared code and of each module, as the commits of this change typed them.
