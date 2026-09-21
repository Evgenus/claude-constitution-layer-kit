---
id: dec-0010-module-research-per-module
type: task-record
title: Every module runs its own research round; design-phase material is a clue set, never a source; nothing here references a location outside this repository
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Every module runs its own research round; design-phase material is a clue set, never a source; nothing here references a location outside this repository

## Context

Decision [dec-0009-module-routine-validation-and-inputs](dec-0009-module-routine-validation-and-inputs.md) ruled, in its rulings 1 and 2, that the constitution design phase's comparisons be copied into the kit and cited by each module as the research its mechanism rests on. On 2026-09-18 the decider reversed that part in chat, with the reasoning below. Rulings 3 to 6 of that record stand.

## Ruling

No real choice was put: the decider ruled directly.

1. **Research is a step of the module routine, performed for each module at authoring time.** A subagent surveys how the module's matrix rows are addressed today: the official Claude Code documentation for the native surface, community harnesses, applicable tools. It returns one dated comparison written in kit vocabulary: candidate approaches, mechanism class, maturity, cost, one recommendation per mechanism with reasoning. The matrix's recommended enforcement is confirmed or overturned from that comparison, not from memory.
2. **The comparison lives at `docs/research/const-<name>.md`**, `non-authoritative`, in the kit-documents territory. Proposed by the session as the default: a comparison surveys prior art and binds nothing, so it belongs in the kit beside the record, not in the plugin that consumers install.
3. **Design-phase material is a clue set, never a source.** Its findings may point a research round at a candidate, but no sentence of it enters the kit unverified, and no fact enters without the public source that verified it. Its vocabulary (aspects numbered one to ten, D-numbers, register rulings) is foreign to the kit and does not enter at all.
4. **No document, script, or configuration in this repository references a location outside it**, other than a public URL: no local folder, no sibling repository, no absolute filesystem path. Placeholder paths in install instructions (a consumer's clone location, the platform's own configuration directory) are not references. `scripts/check-references.sh` gains a lane that turns red on an absolute local path or a `file:` link.
5. The copied comparisons and their index are deleted; git holds them at 32089c0 for anyone who wants the clues.

## Reasoning

Copied comparisons would be reused blindly: they were written for a different artifact, in a different vocabulary, against a platform surface verified on a different date, and citing them would dress that as the evidence behind a module. A research round per module is cheap relative to a module and produces evidence in the kit's own terms, dated to the module's authoring. A reference into another repository or a local folder resolves only on one machine and only while that folder exists, which is the dangling-reference failure the catalogs module exists to prevent.
