---
id: dec-0088-ruff-complexity-limit
type: task-record
title: The kit's lint holds ruff's C901 at a complexity of 15, today's offenders marked
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit's lint holds ruff's C901 at a complexity of 15, today's offenders marked

## Context

On 2026-10-13 the decider asked to turn on ruff's rule C901 in CI. C901 counts the cyclomatic complexity of each function, and it is red for a function above a limit. Until then, the kit's lint selected the rules E, F, B, UP, I and PLC0415 in `pyproject.toml`, and nothing held the complexity of a function.

The lint entries of the gate list already run `ruff check` in CI: `lint-<module>` for each module, and `lint` for `scripts/` and `shared/`. They read the one `pyproject.toml` at the kit root. One line of configuration turns the rule on for all of them, and no new entry or CI step is needed. A new rule that turns CI red is a gate, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9).

The choice is the limit. Every function above it on the day the rule comes in turns CI red, unless it carries a `# noqa: C901` mark. Counted by ruff, each function once:

| # | limit | over it | module code | shared code | kit scripts (self-tests) |
|---|---|---|---|---|---|
| L1 | 10, ruff's default | 60 | 19 | 1 | 40 (11) |
| L2 | 15 | 21 | 3 | 1 | 17 (9) |
| L3 | 25, today's worst module function | 11 | 0 | 0 | 11 (6) |

## Options

- **A. Limit 10, every current function above it marked.** Ruff's default; all new code is held to 10.
  - **Pros:** the strictest rule and the usual one; a reader knows the number without looking it up.
  - **Cons:** 60 marks, 19 of them in module code that ships to consumers; 60 marks teach that the rule can be ignored.
- **B. Limit 15, the 21 current functions above it marked.** A middle limit; most of today's code passes as it is.
  - **Pros:** only 3 functions of module code and 1 of the shared code carry a mark; still a real bound on new code.
  - **Cons:** 15 is the kit's own number, not ruff's default; 17 marks in the kit's scripts.
- **C. Limit 25, a ratchet at today's worst module function.** Nothing in module or shared code is marked; 11 functions of the kit's scripts are.
  - **Pros:** the fewest marks, none in code that ships; nothing grows more complex than today's worst.
  - **Cons:** a loose bound: a new function of complexity 24 passes.

## Recommendation

B, recommended by the session: it holds new code to a bound that bites, and marks only four functions of module and shared code.

## Choice

The decider chose B in chat on 2026-10-13.

## Ruling

<a id="r1"></a>**R1.** `pyproject.toml` selects ruff's C901 with a maximum complexity of 15. The kit's existing lint entries hold it in CI over the modules, the shared code and the kit's scripts. No module ships the setting, as no module ships tool configuration.

<a id="r2"></a>**R2.** Each function above 15 when the rule came in carries `# noqa: C901` on its `def` line, with the reason in plain words: 3 of module code, 1 of the shared tests and 17 of the kit's scripts. Module code names no record in the reason, since an installed component cites nothing of the kit.

<a id="r3"></a>**R3.** A new `# noqa: C901` mark is held by review, not by a check: the commit that adds it says why the function stays whole.

<a id="r4"></a>**R4.** A marked function is free of the limit at any complexity: ruff reads the mark, not the number. The functions marked today, and their complexity, stand in the commit that marked them.

## Applied

The commit before the one that creates this record set the limit and the marks. The commit that creates this record states R1 to R3 in [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module". The record is born `inactive`.

## Carry list

1. R1 — [`pyproject.toml`](../../pyproject.toml), `[tool.ruff.lint]` and `[tool.ruff.lint.mccabe]`; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
2. R2 — [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; the marks on the `def` lines of the 21 functions.
3. R3 — [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
4. R4 — history only: what a mark does is ruff's, and which functions were marked is the marking commit's fact.
