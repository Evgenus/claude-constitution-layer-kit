---
id: dec-0105-template-gives-the-shapes-modules-fill
type: task-record
title: The module template gives the shapes every module fills and four rules its practice settled, and all eleven modules follow it
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The module template gives the shapes every module fills and four rules its practice settled, and all eleven modules follow it

## Context

Item 4.1 of [the rollout plan](../rollout-plan.md) asks to review the first four modules against [the module template](../../module-template/MODULE.md) and to fix the template where it failed them. On 2026-10-26 four fresh readers, one each for [`const-meta-types`](../requirements.md#const-meta-types), [`const-decision-records`](../requirements.md#const-decision-records), [`const-catalogs`](../requirements.md#const-catalogs) and [`const-referencing`](../requirements.md#const-referencing), read each module against the template, holding nothing of the authoring reasoning.

They found the template at fault in about thirty places, which the session sorted into three groups. First, shapes the template does not give, which every module invented the same way. All eleven modules write an enforcement table `| # | artifact | kind |`, which a kit check parses, and ten an error-message table `| key | first line | why | fix |`. All eleven have a `package` row in their artifacts table, a Requires paragraph in their install note and a Settings paragraph in their README. Second, template rules that the modules' practice had moved past. Third, skeleton files that contradict the template's own rules. Its `hooks.json` has no `args` and no `timeout`, against gate-script rule 11, and its example script is `bash`, not POSIX shell. They also found 38 places where a module departs from the template, among them two session-start printers that no enforcement table declares, against [law 5 of CLAUDE.md](../../CLAUDE.md#law-5).

The session put five questions, one per message, in chat on 2026-10-26.

## 1. The scope of the change

- **A. The template only, as item 4.1 says.** One change revises the template; the module departures go to a later item.
  - **Pros:** it matches the item's words; the review stays on one shape; no eval case changes.
  - **Cons:** the undeclared printers and two eval cases that guard nothing stay open meanwhile.
- **B. The template and the four modules' departures.**
  - **Pros:** item 4.1 closes the gap in one change.
  - **Cons:** a much larger change; two modules' eval runs need the decider's token before the merge.
- **C. The template, then all eleven modules brought to it.**
  - **Pros:** every module matches the template at the end.
  - **Cons:** the largest piece of work; seven modules were never in item 4.1; many eval runs.

The session recommended A, as the item's words and a focused review. The decider chose C, "in one PR", in chat on 2026-10-26.

<a id="r1"></a>**R1.** The template is revised by the findings of the review of item 4.1, and all eleven modules are brought to the revised template in the same change.

## 2. What the template writes down of the modules' practice

No real choice existed for these rulings. Each writes down a shape that the modules already share, or the one reading the platform and the kit's other rules allow.

<a id="r2"></a>**R2.** A module's copy replaces the template's italic note by one status line: its manifest version and its open markers, the template linked, and that every list and table row carries a handle. The line names no phase of the rollout plan.

<a id="r3"></a>**R3.** A bold label in the template is marked *(slot)*, where the module writes its own text, or *(template rule)*, which binds the module and is not copied into it.

<a id="r4"></a>**R4.** The rows section links each row to its anchor in the requirements document. One optional line after its table names each row of the aspect that another place homes, with that home and how the module meets it.

<a id="r5"></a>**R5.** The decisions section holds one record per entry, one line each, the record linked.

<a id="r6"></a>**R6.** A module with an invariant and advisory rules states the invariant, then its advisory rules. The advisory rules of any module stand in a list whose items carry the handles `<L>-a`, `<L>-b` in bold, each rule labeled `advisory`. A module keeps the letter its rules have, since rule 8 of plc-0006-module-documents makes `<L>-a` a prefix apart from a message key's `<L><n>`.

<a id="r7"></a>**R7.** Every row of the artifacts table stays: a component the module does not use reads `none`, with its reason in one line. A module with several skills has one skill row per skill. The table has rows for the POSIX entry point, the Python entry file, the package, the shared code, which is none in the plugin, the dependencies, a third-party tool's configuration, the manifest and the tests.

<a id="r8"></a>**R8.** The always-on budget counts the lines the module's `SessionStart` and `SubagentStart` hooks print and each skill's description as the skill listing carries it. A line that holds a value is sized as its fixed text, the placeholder named. The sub-slot ends with the pointer line, or `Pointer line: none` and its reason. The line a project may add to its own `CLAUDE.md` is called the CLAUDE.md line.

<a id="r9"></a>**R9.** A fourth sub-slot after the artifacts table, cost and budget, holds the hook budget, each wait's cap, each handler's timeout and each measured cost; the enforcement and acceptance sections cite it.

<a id="r10"></a>**R10.** The error-message table is `| key | first line | why | fix |`. A text that is no finding fills the cells it has and writes `—` in the others.

<a id="r11"></a>**R11.** The dials table is `| dial | default | read by | meaning |`.

<a id="r12"></a>**R12.** Each judgment-based boundary has at least three contrastive pairs, numbered straight through the section. A pair sets one side against the other, each with its verdict, where both sides may be allowed. A module with several advisory rules groups the pairs under the handles of the rules they serve, one group serving one or several rules. Pairs that a text the module ships already holds are cited, not copied.

<a id="r13"></a>**R13.** The enforcement table is `| # | artifact | kind |`, one artifact per row, for every artifact that runs or prints, the session-start printers included. The honest limits first cite the limits every gate shares and restate none, then list the module's own, each with its backstop or `none — accepted` and the reason.

<a id="r14"></a>**R14.** The Runner line names `python3 -m pytest tests`, the run the kit makes through `scripts/check-aspects.py --run --module <name>`, and the ranges of the fixture items the table holds. A fixture item's kind is `fixture, red→green`, `fixture, assertion`, or `fixture, shared` for the line of the shared items. A number once used is never used again, and a shared item the module does not claim is left out of the shared line. The template cites the policy's rule on handles and does not restate it.

<a id="r15"></a>**R15.** The siblings section names each external tool a gate preflights and what runs without it.

<a id="r16"></a>**R16.** The skeleton files follow the template's own rules. The hooks file uses the exec form with a timeout and carries the pointer line's `SessionStart` and `SubagentStart` entries. The example script is a POSIX wrapper that hands over to the Python entry file. A pointer printer stands beside it, and the tree names both and the session-start pair. The skill skeleton states kernel terms in plain words and cites no kit file, and names its supporting files and its `paths:` key.

<a id="r17"></a>**R17.** The install note template carries, in order: the Requires paragraph, the shared package's block, the install, the calibration or the switch-on dial, adoption through `severity: warn`, the scan in CI, the output log, the fixtures from a clone of the kit, the CLAUDE.md line or none, and what the module does not check.

<a id="r18"></a>**R18.** The README template's first section glosses each term of the description, its "How it works" closes with a Settings paragraph, and its install section gives the marketplace line in full.

<a id="r19"></a>**R19.** The research is confirmed or overturned before the artifacts table is written; the result stands in the Research sub-slot after the table.

## 3. Which rows an eval case proves

Every eval case that checks a skill names no row today, though the module's reading of the row says the module ships the skill.

- **A. An eval case names the rows whose reading names the skill, pointer line or start rule it checks.**
  - **Pros:** the matrix shows the row proved by its case; it matches what the rows section already says.
  - **Cons:** a row's green then rests partly on a receipt the kit does not see run; every module's eval items change.
- **B. An eval case names `none`, and the template says so.**
  - **Pros:** no module changes; a row's result stays with tests CI runs.
  - **Cons:** a row whose whole proof is the skill loading at its moment shows none.

The session recommended A: the kit already counts an `eval` item as run when its receipt is current. The decider chose A in chat on 2026-10-26.

<a id="r20"></a>**R20.** An `eval` item names each row whose reading names the skill, the pointer line or the start rule its case checks.

## 4. A fixture that proves an advisory row's carrier

The template said an advisory row's judgment is proved at review, "never by a fixture". Two modules have fixtures that check the exact text of an advisory rule's carrier, a printed line or a skill description, and name the row.

- **A. Such a fixture names the row, and the judgment stays with review.**
  - **Pros:** it matches two modules; a carrier that vanishes turns red in CI.
  - **Cons:** a green row could be read as the rule holding when only its text was checked.
- **B. "Never by a fixture" stands, and such fixtures name `none`.**
  - **Pros:** a row's result never suggests a judgment was tested.
  - **Cons:** a deleted carrier goes unseen by the row's status; two modules change.

The session recommended A: the carrier is deterministic, so a fixture is its honest proof. The decider chose A in chat on 2026-10-26.

<a id="r21"></a>**R21.** A fixture that checks an advisory row's carrier names the row: it proves that the carrier is shipped and reads as written, never that the rule is followed, whose judgment is proved by the boundary examples at the review item.

## 5. What a platform fact carries

The template asked a fact for its date and what breaks, and for no source.

- **A. A source per fact, and the kit-wide facts in the shared page.**
  - **Pros:** every fact can be checked; a shared fact is kept up to date in one place.
  - **Cons:** every fact is sourced again; the shared page, already over its ceiling, grows.
- **B. A source per fact, the facts staying in each module.**
  - **Pros:** every fact can be checked; most sources already stand in the modules' research comparisons.
  - **Cons:** a fact several modules share is kept up to date in each.
- **C. No source; an observation on a named version is admitted as a verification.**
  - **Pros:** the smallest change.
  - **Cons:** "nothing from memory" stays unchecked.

The session recommended B. The decider chose B in chat on 2026-10-26.

<a id="r22"></a>**R22.** Each platform fact carries its source: a page of the official documentation, the module's research comparison with the fact's handle, or `observed on Claude Code <version>` with what was run; a comparison that gives a fact no handle is cited by section and item. It also carries one date of its own and what breaks if it changes.

## 6. Where the deferrals every gate shares live

Three modules wrote the same deferral, "for every gate alike", in their own words, and eight said nothing of it.

- **A. In the deferred paragraph of the shared page's first section, which every module cites.**
  - **Pros:** one source for eleven modules, where the shared package's deferrals already stand.
  - **Cons:** the shared page, over its ceiling, grows by a few hundred characters.
- **B. Each module keeps its own copy.**
  - **Pros:** the shared page does not grow.
  - **Cons:** the copies drift.
- **C. Written nowhere.**
  - **Pros:** the smallest text.
  - **Cons:** the signal can fire unseen.

The session recommended A. The decider chose A in chat on 2026-10-26.

<a id="r23"></a>**R23.** The deferrals every gate shares stand once in the deferred paragraph of [kit-shared-gate-code §1](../../shared/GATE.md#g1): Windows without a POSIX shell, and a clone of the kit without symbolic links; a run past the handler's timeout; a governed document with another extension. Each module cites them in its deferred section and restates none.

## Applied

The change revised the template, its skeleton files, the deferred paragraph of the shared page, rule 10 of plc-0006-module-documents and two steps of "Developing a module" in [CLAUDE.md](../../CLAUDE.md). Each of the eleven modules was then brought to the template in one commit on a branch of its own, by a fresh implementer, and the branches were merged into the change. Item 4.1 of the plan is ticked in the change that lands this record.

## Carry list

1. R1 — history only: the scope of this change, applied by its commits.
2. R2, R3 — [the module template](../../module-template/MODULE.md), its italic preamble.
3. R4 — [the module template](../../module-template/MODULE.md#t3), section 3.
4. R5 — [the module template](../../module-template/MODULE.md#t4), section 4.
5. R6 — [the module template](../../module-template/MODULE.md#t5), section 5.
6. R7, R9, R10 — [the module template](../../module-template/MODULE.md#t6), section 6.
7. R8 — [the module template](../../module-template/MODULE.md#t6), section 6; [the install note template](../../module-template/plugin/INSTALL.md), its CLAUDE.md line.
8. R11 — [the module template](../../module-template/MODULE.md#t7), section 7.
9. R12 — [the module template](../../module-template/MODULE.md#t8), section 8.
10. R13 — [the module template](../../module-template/MODULE.md#t9), section 9.
11. R14 — [the module template](../../module-template/MODULE.md#t10), section 10.
12. R15 — [the module template](../../module-template/MODULE.md#t11), section 11.
13. R16 — [the module template](../../module-template/MODULE.md), its plugin skeleton; [the hooks skeleton](../../module-template/plugin/hooks/hooks.json); [the script skeleton](../../module-template/plugin/scripts/check-example.sh); [the pointer skeleton](../../module-template/plugin/scripts/print-skill-pointer.sh); [the skill skeleton](../../module-template/plugin/skills/example-procedure/SKILL.md).
14. R17 — [the install note template](../../module-template/plugin/INSTALL.md).
15. R18 — [the README template](../../module-template/README.md); step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md).
16. R19 — step 3 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the module template](../../module-template/MODULE.md#t6), its Research sub-slot.
17. R20, R21 — [the module template](../../module-template/MODULE.md#t10), section 10, its paragraph on rows.
18. R22 — [the module template](../../module-template/MODULE.md#t6), its platform facts; [rule 10 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r10).
19. R23 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts; [the module template](../../module-template/MODULE.md#t12), section 12.
