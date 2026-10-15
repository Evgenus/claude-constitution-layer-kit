---
id: dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names
type: task-record
title: Kit checks hold every list of the modules against the folders, the Python floor and each entry's clauses to one source, the shared item numbers, and no kit document named in a module
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Kit checks hold every list of the modules against the folders, the Python floor and each entry's clauses to one source, the shared item numbers, and no kit document named in a module

## Context

An audit of the kit's hardcoded logic on 2026-10-02 found several lists and copies that no check held. Each case was probed again on the trunk on 2026-10-07:

- **The lists of the modules.** The marketplace file, the `enabledPlugins` of the kit's committed settings and each module's manifest name the modules, and no check read them. A module left out of the marketplace, or a manifest naming another plugin, was caught late at best, in CI, as a refused install; one left out of the settings was never caught. No check held the kernel's `const-<aspect>` name ([kernel §7](../../kernel/CONVENTIONS.md#k7)). Six kit checks each decided on their own which folders are modules.
- **The Python floor and the entry clauses.** The floor, 3.12, is written in about ninety places, and nothing held them to each other. Shared item 112, the one test that runs an entry below the floor, looked for an older interpreter on the machine and reported "not exercised" in every CI job. Each entry's failure lines close with a clause saying what goes unchecked; the seven gates on the default clause held those lines by their opening words alone, and a change of the clause in all three lines of one of them left its fixtures green.
- **The shared item numbers.** A shared acceptance item's number was its place in the list. An item moved in place kept the numbers and gave each to another item, every check green; one inserted in the middle renumbered every item after it, though [rule 4 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r4) says a number is never reissued.
- **The kit's words in a module.** Three module runners each held their own list of kit document names that an install note must not carry; the three lists differed, and each matched `dec-00`, so from the hundredth record on a citation would pass.

The change is on one branch. The shared code changes, and every module that links it is a draft, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). The decider kept the audit's recommended fixes when reading the change's plan on 2026-10-07. Eight questions were put to the decider in chat that day, one per message, each with lettered options and one recommendation, the pick a letter; sections 1 to 8 hold them.

## 1. One pull request and one record

The holds on the module lists and on the copies move rules held by review to a gate, a change of class [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) asks to declare, as [dec-0049-module-links-held-by-a-kit-check](dec-0049-module-links-held-by-a-kit-check.md) did; they have `process` stakes. Pinning the shared item numbers holds a rule already written and is routine. The question was how the change reaches the trunk.

- **A. One pull request, one record** for the `process` rulings, the pinning noted in its commit.
  - **Pros:** one carry audit, one independent verification, one yes; CLAUDE.md is edited and audited once; all the pieces are kit tooling over the same lists.
  - **Cons:** the routine piece waits for the whole change, about one working day; one large regression scope, about 56 records.
- **B. Two pull requests**, the module lists with the pinning and a record first, then the copies with a second record.
  - **Pros:** each audit smaller; the marketplace and settings holds reach the trunk hours sooner.
  - **Cons:** both touch CLAUDE.md, so its records are read for regression twice; two records, two verifications, two yeses; about three more hours.
- **C. The module lists and the pinning only**; the copies logged.
  - **Pros:** the smallest change; no new kit script; one record.
  - **Cons:** the clause drift of the seven default-clause gates stays green; most entry floors stay held by nothing in CI.

The session recommended A: no consumer waits for either part, so B's speed buys nothing anyone uses and reads the CLAUDE.md records twice, and C leaves the one gap the probe showed live. The decider chose A in chat on 2026-10-07.

<a id="r1"></a>**R1.** One pull request and one record for the rulings of sections 2, 3 and 5 to 8; the rest of the change routine, noted in its commits.

## 2. Where the module-list holds live

`scripts/check-gate-lists.py` already held the gate list's modules against the module folders. The question was where the new holds go.

- **A. In check-gate-lists.**
  - **Pros:** the check that already lists the folders holds every other list of them; no new listing of the folders; one report names every module-list fault.
  - **Cons:** the check grows past its name, since the marketplace and the settings are not gate lists; its docstring and CLAUDE.md's sentence on it grow.
- **B. In the new copies check**, beside the floor and the clauses.
  - **Pros:** one check owns "every copy agrees with its source"; check-gate-lists keeps its subject.
  - **Cons:** that check must list the module folders itself, one more answer to which folders are modules; the "no module document" failure written twice.
- **C. In a third new check.**
  - **Pros:** each check one subject.
  - **Cons:** one more kit script, gate entry and self-test; its own folder listing too.

The session recommended A: the new holds compare lists against the folders check-gate-lists already lists and holds, and B and C each add one more listing, the very drift this change is about. The decider chose A in chat on 2026-10-07.

<a id="r2"></a>**R2.** `scripts/check-gate-lists.py` holds, for each module folder: its name is `const-<aspect>` in full ([kernel §7](../../kernel/CONVENTIONS.md#k7)); its manifest is a JSON object naming it; the marketplace file lists it exactly once, with `source` `./modules/<name>`, and lists no plugin that is no module folder; the kit's committed settings enable it as `<name>@<marketplace name>`, set to `true`, and enable no plugin of that marketplace that is no module folder. The marketplace's name is read from its file and typed nowhere in the check. A file the check cannot read as the rule needs is a failure to run; a copy that disagrees is red with why and fix. The per-clone `settings.local.json` is never read: R4 of [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md#r4) stands, and a committed `false` is red.

## 3. The settings' declaration of the marketplace

The kit's committed settings also name the marketplace a third time, as the key under which they declare it, with a `directory` source at `.`; R1 of [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md#r1) rules both that and the enabled modules. If that key drifts, every kit session loads no plugin, seen by a person at session start and red in no check.

- **A. Hold it too**: the declaration has a key equal to the marketplace's name whose source is `directory` with path `.`; other marketplaces allowed.
  - **Pros:** R1 of [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md#r1) held whole; a partial rename caught in CI; a few cases inside a piece written anyway.
  - **Cons:** reads one level deeper into the platform's settings format; a move to another source kind needs a change to the check and a record.
- **B. Leave it out**; hold `enabledPlugins` alone.
  - **Pros:** the check never depends on how the platform writes a source.
  - **Cons:** half of R1 held by review; the drift it leaves switches every gate off at once while every check is green.

The session recommended A: a few cases close the one drift here that switches every gate off, and dec-0043 already rules the exact source. The decider chose A in chat on 2026-10-07.

<a id="r3"></a>**R3.** `scripts/check-gate-lists.py` holds that the kit's committed settings declare the marketplace under its name with the source `{"source": "directory", "path": "."}`, compared exactly; other marketplaces they declare are not read.

## 4. One listing of the module folders

Six kit checks each decided which folders are modules. On a tree where the holds of R2 are green they agree; they differ on a tree check-gate-lists already turns red or stops on.

- **A. Leave the six listings**, made equal on every green tree by the name rule of R2.
  - **Pros:** no change to five scripts and their self-tests; on any tree CI passes, the sets are equal.
  - **Cons:** six answers stay in the code; a future kit script picks its own.
- **B. One shared listing** in `scripts/kit_module_doc.py`, read by every kit check that lists modules.
  - **Pros:** one answer in code; a new kit script has a helper to reach for.
  - **Cons:** one more piece, about two hours; three checks behave differently on broken trees.

The session recommended A: the drift shows only on a tree check-gate-lists already flags with the fix, and B is the tidiness the audit had set aside; it named B a clean piece if one answer in code was wanted. The decider chose B in chat on 2026-10-07.

<a id="r4"></a>**R4.** One listing of the module folders, `module_folders` in `scripts/kit_module_doc.py` — the folders under `modules/` whose name opens with neither `.` nor `_`, sorted, each holding its `MODULE.md`, else a failure to run with the fix — read by check-gate-lists, check-aspects, check-portability, check-module-links, check-install-guide and check-copies, and by check-shared-links with its own filter on top. Kit tooling at routine stakes.

## 5. The floor's one source, and the copies held

The decider kept the audit's copies check when reading the plan: a kit check holds every copy of the floor, and each entry's three failure lines against its Identity's clause, as [GATE.md §2](../../shared/GATE.md#g2) items 1 and 6 rule them. The question was what the copies are held to, and whether shared item 112 is made to run in CI.

- **A. No named source**: every copy names one minor; item 112 left as it is.
  - **Pros:** no shared-code change; every drift of a single copy red in CI.
  - **Cons:** no one place states the floor; the message names the majority, not the intent; the entry's own refusal below the floor stays untested in CI for most entries.
- **B. `FLOOR` in the shared preflight as the source**; item 112 rewritten to run each entry with its version set one minor below it, on every machine.
  - **Pros:** one source in code, named by the message; the refusal below the floor proven in CI for every module.
  - **Cons:** a shared-code change, a constant no gate reads at run time; one more piece, rerunning every module's fixtures; one more ruling.
- **C. The source read from the template's rule on the floor.**
  - **Pros:** the rule's own home is the source.
  - **Cons:** a check that parses a prose sentence, the fragility the kit removed elsewhere.

The session recommended A: it catches every drift the audit described at no shared-code cost; it named B the pick if the refusal itself was wanted proven in CI. The decider chose B in chat on 2026-10-07.

<a id="r5"></a>**R5.** The interpreter floor's one source is `FLOOR` in `shared/const_gate/preflight.py`, read by no gate at run time; each entry file keeps its own literal, since it must parse on any Python 3. Shared item 112 runs the entry under the interpreter at hand with its version set one minor below that source and expects the line `C14` up to its clause; it runs on every machine and is never "not exercised". The constant is admitted to the shared code under [rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) as part of the floor rule of [template §6](../../module-template/MODULE.md#t6), which all eleven modules need through item 112.

<a id="r6"></a>**R6.** `scripts/check-copies.py`, kit tooling never shipped in a module, is an entry `copies` of the gate list with `--self-test` as its fixture. Every copy of the floor in the files git lists — links, binary files and the kit's `docs/decisions/` and `docs/research/` aside — names the source's minor, and its forms that name the minor below it name that one. Each entry's `C1`, `C14` and `C15` first lines close with its Identity's `until_installed`, the default read from the shared identity; a generator's, whose `C14` closes on neither `C11` nor `S1`, carry no clause.

## 6. The shared item numbers

The audit proposed that each shared item carry its number in the file. The question was whether, and what else holds them.

- **A. Pin the numbers**: unique and rising, checked when the list is built; a new item takes the next free number.
  - **Pros:** holds the rule as written; a swap keeps each number with its item; an insert moves nothing.
  - **Cons:** no check that a module's own items stay below the shared numbers.
- **B. A, plus the harness refuses a number a module's own item and a shared item both use.**
  - **Pros:** closes a collision one module is one item away from.
  - **Cons:** a shared-harness change, about half an hour more.
- **C. A, plus a kit check that the ranges of [GATE.md §5](../../shared/GATE.md#g5) name only numbers the list holds.**
  - **Pros:** the shared table can no longer name a gone item.
  - **Cons:** it reads a prose table; check-aspects already holds each module's cell against the numbers its runner prints.
- **D. Accept renumbering.**
  - **Pros:** no work.
  - **Cons:** breaks rule 4 of plc-0009 on the first insert in the middle.

The session recommended B: A holds the rule, and B closes the one collision that is close, for one case. The decider chose C in chat on 2026-10-07.

<a id="r7"></a>**R7.** The shared acceptance items carry their numbers in `shared/tests/shared_items.py`, unique and rising from 101, checked each time the list is built — routine, since rule 4 of plc-0009 already rules it. `scripts/check-aspects.py` holds those numbers, read from the file without running it, and every `S<n>` and range of [GATE.md §5](../../shared/GATE.md#g5) against them; a red beside those R7 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r7) lists, which stays as it is.

## 7. The kit's words in a module

Three module runners each held a list of kit document names an install note must not carry. The question was where that rule is held.

- **A. Leave it** with the audit's small items.
  - **Pros:** no growth; the blind spot opens only at the hundredth record.
  - **Cons:** three differing copies stay in shipped tests.
- **B. One pattern alike in all three runners.**
  - **Pros:** closes the blind spot now; test only.
  - **Cons:** still three copies, equal but held equal by nothing.
- **C. One kit check**: a new form of the portability check over every module's installed components; the three runner items lose that part.
  - **Pros:** one place; all eleven modules covered; test code out of shipped modules.
  - **Cons:** it moves an acceptance item out of three modules and extends a ruled set of forms; three module documents change.

The session recommended A: the change had already grown by three pieces, and B and C pull three modules into an audit already large. The decider chose C in chat on 2026-10-07.

<a id="r8"></a>**R8.** `scripts/check-portability.py` refuses a kit document's name in a module's installed components and in the shared code it reads, a red with why and fix; it extends the forms of R1 of [dec-0056-portability-grep-and-gate-lists](dec-0056-portability-grep-and-gate-lists.md#r1) and [requirement A12.1](../requirements.md#a12-1), and dec-0056 stays as it is. The three module items that held their own list of kit words — const-interaction's T41, const-language's T16, const-styling's T18 — lose that part and keep the rest. The list holds the kit's own names, never a project's: section 6 of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md), which refused a list of consumer names as the definition of a project reference, stands as it ruled.

## 8. What counts as a kit document's name

A probe of the runners' word list over every installed component hit one line: const-catalogs' skill uses `DEC-0007`, `dec-0007` as an example of a consumer's own numbered id.

- **A. A name a reader can follow to a kit file**: a full record name with its slug and the kit's fixed file names; a bare id passes.
  - **Pros:** no exception and no module edit; the three catalog prefixes need not be typed.
  - **Cons:** looser than the runners, which refused any `dec-00…`; a bare id in an install note passes.
- **B. Also any bare id of the kit's own catalogs**, the prefixes read from the kit's dials; the skill's example moves to a prefix the kit does not use.
  - **Pros:** as strict as the runners were, over every module; a new kit catalog covered by itself.
  - **Cons:** the portability check reads YAML; one more module edit; the check depends on another module's dial.
- **C. B's strictness in install notes only.**
  - **Pros:** the runners' strictness where they had it; no skill edit.
  - **Cons:** two rules by file kind.

The session recommended B: the strictness the runners held, widened to every module, with the prefixes read from the one place the kit declares them. The decider chose B in chat on 2026-10-07.

<a id="r9"></a>**R9.** The names refused are the kit's fixed file names — `MODULE.md`, `requirements.md`, `rollout-plan`, `CONVENTIONS.md`, `GATE.md`, `kernel/` — matched as written, and an id `<prefix>-<digits>` of each catalog under `const-catalogs.catalogs` in `constitution.yaml`, its digits the catalog's width, in either case, with or without a slug; fenced blocks, code spans and links are read like any other text. The check reads the dials with PyYAML and fails to run when they are missing or hold no `const-catalogs.catalogs` list it can read; an empty list declares no catalog. const-catalogs' skill gives its example with a prefix the kit does not use.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests and the documents; the message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The commit that adds this record adds a row for it in section 4 of three module documents, and corrects the sentences the review of the documents found incomplete or false; its message names them. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI", on what `scripts/check-gate-lists.py` holds, and step 1 of "Developing a module", the places a new module goes; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring; [the gate list](../../scripts/gate-list.sh), its header. R4 of dec-0043-kit-plugins-through-project-settings stands; that it stands is history.
3. R3 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring.
4. R4 — [the reader](../../scripts/kit_module_doc.py), its docstring of `module_folders`; the docstrings of the checks that read through it.
5. R5 — [GATE.md §1](../../shared/GATE.md#g1), the row `preflight`; [GATE.md §5](../../shared/GATE.md#g5), the row of items S111–S116; [template §6](../../module-template/MODULE.md#t6), rule 6; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
6. R6 — [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [GATE.md §3](../../shared/GATE.md#g3), the rows C14 and C15; [check-copies](../../scripts/check-copies.py), its docstring; [the gate list](../../scripts/gate-list.sh), its entry `copies`.
7. R7 — [GATE.md §5](../../shared/GATE.md#g5), its sentence on the numbers; [check-aspects](../../scripts/check-aspects.py), its docstring; [the shared items](../../shared/tests/test_shared_items.py), its docstring. The red added beside R7 of dec-0054-acceptance-items-name-their-rows is history.
8. R8 — [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [check-portability](../../scripts/check-portability.py), its docstring; [`const-interaction`](../../modules/const-interaction/MODULE.md#t10), its row T41; [`const-language`](../../modules/const-language/MODULE.md#t10), its row T16; [`const-styling`](../../modules/const-styling/MODULE.md#t10), its row T18. The extension of R1 of dec-0056-portability-grep-and-gate-lists is history.
9. R9 — [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [check-portability](../../scripts/check-portability.py), its docstring.
