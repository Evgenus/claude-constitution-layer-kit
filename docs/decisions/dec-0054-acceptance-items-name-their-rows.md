---
id: dec-0054-acceptance-items-name-their-rows
type: task-record
title: Each acceptance item names the matrix rows it proves, and scripts/check-aspects.py holds the tags as a gate and reports each row's result on request
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Each acceptance item names the matrix rows it proves, and scripts/check-aspects.py holds the tags as a gate and reports each row's result on request

## Context

The decider asked for every row of the matrix of [constitution-requirements](../requirements.md), [requirement A1.1](../requirements.md#a1-1) to [requirement A13.7](../requirements.md#a13-7), to have its own implementation status and an audit that gives that row its own result. Two links were missing. A module document's rows section ([template §3](../../module-template/MODULE.md#t3)) ties rows to modules, but its acceptance table ([template §10](../../module-template/MODULE.md#t10)) does not tie items to rows. And no tool read either link. The eleven module runners print one line per item, from one function of the shared harness, and report per module only. The questions below were put in chat, one per message, each with lettered options; the pick was the letter.

## 1. Where a row's status lives

- **A. A generated report; the matrix stays as it is.** A kit script derives each row's status; nothing is stored.
  - **Pros:** the matrix keeps its `current-state` type and states "what shipped" nowhere; the status cannot go stale.
  - **Cons:** the status is seen only by running the script.
- **B. A status column in the matrix.**
  - **Pros:** the status is read where the row stands.
  - **Cons:** it puts "when" into a document that holds only what a module must implement ([rule 1 of plc-0007-requirements](../policies/plc-0007-requirements.md#r1)), and states what shipped a second time beside the module document's enforcement section ([rule 7](../policies/plc-0007-requirements.md#r7)).
- **C. A committed `non-authoritative` snapshot.**
  - **Pros:** a status readable without running anything.
  - **Cons:** a new document kind, with its own policy, that goes stale at the next commit.

The session recommended A. <a id="r1"></a>**R1.** A, chosen by the decider in chat on 2026-09-29: a row's status is derived by a kit script on each run and stored nowhere; the matrix gains no column, and a module's progress stays in the rollout plan.

## 2. What proves a row

- **A. Structure only.** A row counts as covered when a module's rows section holds it.
  - **Pros:** no change to the module documents.
  - **Cons:** it reports documentation as proof ([law 5 of CLAUDE.md](../../CLAUDE.md#law-5)).
- **B. A module-level run, labelled per row.**
  - **Pros:** no tagging.
  - **Cons:** one red item marks all of a module's rows red.
- **C. Every acceptance item names the rows it proves; each row takes the result of its own items.**
  - **Pros:** a row's verdict comes from the items that prove it.
  - **Cons:** a template change, and judgment on every item of eleven modules.

The session recommended C. <a id="r2"></a>**R2.** C, chosen by the decider in chat on 2026-09-29: every acceptance item of a module document names the rows it proves; a row's result combines its items across every module that holds a part of it; a row a module's rows section holds and no item of that module names is a finding.

## 3. How an item names its rows

- **A. A `rows` column in the acceptance table**, each cell linking the rows the item proves.
  - **Pros:** the tag stands beside its item; the script reads one cell.
  - **Cons:** a link costs about 40 characters, since a bare row handle may stand only in the requirements document; about 1,000 to 2,000 characters per module document.
- **B. Row links inside the text of "what it proves".**
  - **Pros:** no change to the table's shape.
  - **Cons:** the script cannot tell a proved row from a row mentioned for context.
- **C. An `items` column in the rows table of [template §3](../../module-template/MODULE.md#t3).**
  - **Pros:** about 300 characters per module; item handles need no link.
  - **Cons:** the map stands far from the item it describes.

The session recommended A. <a id="r3"></a>**R3.** A, chosen by the decider in chat on 2026-09-29: the acceptance table is `| item | kind | rows | what it proves |`, and each `rows` cell links every row the item proves to its anchor in the requirements document, or holds the word of R5.

## 4. The shared acceptance items

The shared items of [kit-shared-gate-code §5](../../shared/ITEMS.md#g5) run through one entry point of a module and prove the shared machinery, not the text of a row.

- **A. They carry the rows of the gate they run through.**
  - **Pros:** a gate that fails open does not hold its row, and the row says so.
  - **Cons:** one red shared item turns every row of that gate red.
- **B. They carry the word `shared` and are reported apart.**
  - **Pros:** a row's verdict comes only from items that prove its own rule.
  - **Cons:** a row may be green while its gate's machinery is red.
- **C. The report leaves them out.**
  - **Pros:** the simplest script.
  - **Cons:** a red shared item is seen only in a separate run.

The session recommended B. <a id="r4"></a>**R4.** A, chosen by the decider in chat on 2026-09-29, against the session's recommendation, its wording corrected by the decider's second pick in chat on 2026-09-30, below: the line of the shared items carries every row that a fixture item of the module, run through the same entry point — the script its hook or its scan calls — names, and no other row. The session's concern stands: a red shared item turns every such row red, and only the item tells whether the row's own rule failed.

The carry audit found the first wording, "the rows of the gate whose entry point runs them", read two ways: one module gave its line only the rows of gate class, another its dial and definitional rows too, and two left out the rows of a scan that the same script runs. The session put the reading to the decider:

- **A. Every row a fixture item of the module, run through the same entry point, names.**
  - **Pros:** a rule anyone can check against the runner; a fail-open script stops holding everything it holds, and the line says so.
  - **Cons:** longer lines, so one red shared item turns more rows red.
- **B. Only those of them whose matrix class is gate or gate-lite.**
  - **Pros:** a red shared item touches only the rows that are gates.
  - **Cons:** the class is read from prose again, and a dial row the same script validates stays green when the script fails open.
- **C. Only the hook's rows.**
  - **Pros:** no table change for most modules.
  - **Cons:** the shared items run the scan too, so the line claims less than they prove.

The session recommended A, the one reading that needs no judgment. The decider chose A in chat on 2026-09-30, and R4 above is corrected in place to it, before the yes.

## 5. An item that proves no row

Some items prove packaging, not a row: the shape of the hooks file, the manifest, the install note.

- **A. The word `none`, reported apart.**
  - **Pros:** no row is claimed for a packaging check; an empty cell stays a finding.
  - **Cons:** an author can write `none` to skip the thought, and only review sees it.
- **B. Every item names a row of its module.**
  - **Pros:** no fixed word.
  - **Cons:** it stretches what an item proves, the blur [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) forbids.
- **C. Items may also name a row of [aspect A12](../requirements.md#a12), from any module.**
  - **Pros:** evidence for the portability rows.
  - **Cons:** it solves part of the slot, and the gate needs an exception.

The session recommended A. <a id="r5"></a>**R5.** A, chosen by the decider in chat on 2026-09-29: an item that proves no row of its module holds `none` in its `rows` cell; the report lists such items per module outside every row's verdict, and a red one still makes the run red.

## 6. How the script reads the runners

- **A. Parse the harness's lines, cross-checked.**
  - **Pros:** no change to the shared code, which ships to every consumer.
  - **Cons:** the script depends on a print format no document declares.
- **B. A machine-readable output in the shared harness.**
  - **Pros:** an exact contract.
  - **Cons:** it fails the admission test of [rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) as written, and ships kit-only code to consumers.

The session recommended A. <a id="r6"></a>**R6.** A, chosen by the decider in chat on 2026-09-29: the script reads each runner's `[ok]` and `[FAIL]` item lines and its last line; an item line out of that format, a count of item lines that differs from the total of the last line, or an exit other than 0 or 2 is a configuration failure, never a pass. A fixture item's handle is its runner number, bare or under `T` or `S`: `T12` and a bare `12` are item 12, `S101` is item 101. The shared harness does not change.

## 7. Gate or report

- **A. A report, run on request.**
  - **Pros:** no slot in the gate list.
  - **Cons:** the tags drift unseen.
- **B. The structure a gate, the full run on request.**
  - **Pros:** the tags are held on every commit that touches a document, in under a second.
  - **Cons:** a new gate, with its fixture and messages, and a line more in the gate list.
- **C. The full run a gate.**
  - **Pros:** every commit proves every row.
  - **Cons:** minutes added to every such commit.

The session recommended B. <a id="r7"></a>**R7.** B, chosen by the decider in chat on 2026-09-29: a plain run is a gate over the module documents and the matrix, running no runner, one line of the gate list. It is red on a row a module's rows section holds that no item of that module names; on an item whose `rows` cell is empty, or holds anything but row links or `none`; on a link to a row the matrix does not hold; and on an item that names a row its module's rows section does not hold. What the full run needs to read the tables is red too: an acceptance table without the `rows` column; an item cell that is not a list of handles and closed ranges, such as `T1–T4, T7`; a kind that is none of `fixture`, `kit check`, `live`, `live, deferred` and `review`; a fixture item whose handle is no runner number. So is a row the matrix gives a module that no module's rows section holds. The full run, with results, is on request, beside the module runners.

<a id="r8"></a>**R8.** The gate runs in the kit's CI with the other kit checks once CI is wired.

## 8. The script's name and flags

The session first proposed `scripts/check-rows.py`, a plain run the gate and `--run` the report, against the `report-rows.py … --no-run` of the planning session, since the kit's other gates are `check-*.py` run plain. The decider found "rows" too bound to the matrix's own context and proposed "aspects"; the session recommended `check-requirements.py`, since the unit judged is the row, which the kit cites as a requirement.

<a id="r9"></a>**R9.** `scripts/check-aspects.py`, chosen by the decider in chat on 2026-09-29: kit tooling, never shipped in a module. A plain run is the gate of R7; `--run` also runs the runners and prints the report; `--module <name>` limits `--run` to one module; `--self-test` is its fixture.

## 9. Defaults the session took

These follow the plan the decider saw, and stay open to override.

<a id="r10"></a>**R10.** The report gives each row its destination from the matrix, the modules that hold a part of it with their manifest versions, its items with their kind and result, and one verdict. A row is `red` when an item of it is red. It is `green` when at least one of its items was run and every item run was green, the items no run examines listed beside. A row whose items are none of them run takes their kinds: `live, done <date>`, `live` for a live item that names no date, `live, deferred`, `review`, `kit check`, or `fixture, not read` for a fixture item the runner did not print. A row a module holds and no item names is `no item`. A row no module holds is counted as `no module`, shows its destination and its enforcement cell as the matrix states them — definitional, config, review, a kit CI not yet built — and is never green.

<a id="r11"></a>**R11.** An item names a row only where it proves what the module's reading of that row in [template §3](../../module-template/MODULE.md#t3) says the module ships — a gate, a carrier, an assist. The judgment of an advisory row is proved by its boundary examples at the review item, never by a fixture, so a fixture green on an advisory row proves its carrier alone.

<a id="r12"></a>**R12.** In a full run, a runner's item that no row of the module's acceptance table names, and a fixture item a table names that the runner did not print, are findings.

## 10. A green on an advisory row

The first full run over the eleven runners gave 40 rows `green`, twelve of them rows whose matrix enforcement is advisory alone, green only because a fixture of a carrier passed: a session-start printer, a skill file, an assist. The session put R10 and R11 to the decider again.

- **A. Keep `green`.**
  - **Pros:** no change; the fixtures ran and passed.
  - **Cons:** a reader can take a green on an advisory row for a proof of the judgment, which [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) forbids.
- **B. Keep `green`, and print the matrix's enforcement cell beside every row.**
  - **Pros:** no parsing and no new verdict.
  - **Cons:** the verdict and the count still say green.
- **C. A verdict of its own, `carrier green`, for an advisory row.**
  - **Pros:** the verdict says what was proved, and the count keeps advisory rows apart.
  - **Cons:** the script reads the opening word of a cell of prose.
- **D. Fixtures never name an advisory row.**
  - **Pros:** nothing is green that a run did not prove.
  - **Cons:** the tables are edited again, and the proof that a carrier works leaves the row.

The session recommended C. <a id="r13"></a>**R13.** C, chosen by the decider in chat on 2026-09-29: a row whose enforcement cell in the matrix opens with the word `advisory` and holds the word `gate` or `gates` nowhere takes `carrier green` where R10 would give it `green`; the report counts it apart. The words are matched whole, so "ungateable" is no gate and "gate-lite" is one.

## Carry list

1. R1 — [rule 1](../policies/plc-0007-requirements.md#r1) and [rule 8 of plc-0007-requirements](../policies/plc-0007-requirements.md#r8); [the gate itself](../../scripts/check-aspects.py), its docstring.
2. R2, R3, R4, R5, R11 — [template §10](../../module-template/MODULE.md#t10), its paragraph on rows; the acceptance tables of the eleven module documents.
3. R6, R10, R12, R13 — [the gate itself](../../scripts/check-aspects.py), its docstring.
4. R7, R9 — [the gate itself](../../scripts/check-aspects.py), its docstring; [template §10](../../module-template/slot-guidance.md#s3); [rule 12 of plc-0006-module-documents](../policies/plc-0006-module-documents.md#r12); step 5 of "Developing a module" in [CLAUDE.md](../guide/developing-a-module.md#s5); the routine list of [pyproject.toml](../../pyproject.toml).
5. R8 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the CI wiring.
