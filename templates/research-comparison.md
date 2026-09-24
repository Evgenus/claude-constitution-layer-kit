---
id: <res-nnnn-const-name — the next number of the res catalog, the slug naming the module surveyed>
type: non-authoritative
title: Research comparison — const-<name> (<survey date>)
status: active
---

# Research comparison — const-<name> (<survey date>)

Surveyed <date>; local `claude --version` prints `<version>`. Experiments ran with <every tool and library used, each with its version>, on <the platform>, in a scratch directory outside any repository of the kit; <any live run: how it was invoked and with which model>. Official Claude Code pages were read in their Markdown form (`curl -sL https://code.claude.com/docs/en/<page>.md`), and every quotation below was checked against that text. A statement about a tool's behaviour is written only where the experiment that showed it is named, with the version tried; a tool read but not run is marked so.

Scope: the rows of the module surveyed, each cited by its link form as the earlier comparisons do, and what the matrix recommends for each; the records that already bind the module's shape, linked. Vocabulary: the kernel's terms by link. <What the kit's gates already share is surveyed only for fit, in its own section.> Sources by authority: official Claude Code documentation, tool documentation and repositories, experiments reported here. The earlier comparisons were a starting point, never evidence: every platform fact relied on here was re-read on the survey date.

The surveyed tools, keyed once; a date is the latest release on the survey date, from the repository's releases page or registry entry, or the last commit where no release exists:

- t1. <tool, linked> <version>, <date>: <runtime or kind>.
- t2. <…>

<One section per mechanism the module's rows need, numbered from 1; delete this paragraph. Each section names the row it serves, lists what was found as lettered items (a1, a2 … in the first section, b1, b2 … in the second), gives for each candidate approach its mechanism class, maturity and cost, and closes with one recommendation in bold with its reasoning — and, where the decider must choose, says what is left to the decider.>

## 1. <Mechanism> (<the row it serves, as a link>)

- a1. **<Finding.>** <What was found, with its source or experiment named.>
- a2. **<Finding.>** <…>

**Recommendation: <one mechanism, with reasoning; CONFIRMED or OVERTURNED against the matrix's recommended enforcement>.** <For the decider: …>

## <n>. Fit with the shared gate code

<How the module would use what the kit's gates share, part by part, and every strain it would put on it; described, not decided. Delete the section when the module ships no script.>

## <n+1>. Platform facts, re-verified, and discrepancies

- p1. **<Fact.>** <The page and what it says, verified on the survey date.> Breaks: <what fails if it changes>.

<Then what was stale, imprecise or missing in the earlier comparisons, lettered a, b, c …; say which, if any, changes a design.>

## Experiments

<Each in a scratch directory outside any repository of the kit, unless it read the kit's tree and wrote nothing, said so; the versions used once, here.>

- E1. <What was set up, what was run, what was observed — numbers, exit codes, lines — so that a reader could repeat it.>

## Recommendations summary

1. <Row, as a link> — **CONFIRMED** / **OVERTURNED** / **build** / **not needed**: <one line per mechanism, the reasoning's core>.
