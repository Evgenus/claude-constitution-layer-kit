---
id: dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders
type: task-record
title: 'Two landed records under one number: the one landed second renumbers; the kit''s checks hold item numbers, descriptions, namespaces, the types pair and the kit''s folders'
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Two landed records under one number: the one landed second renumbers; the kit's checks hold item numbers, descriptions, namespaces, the types pair and the kit's folders

## Context

The kit's hardcode audit grouped sixteen small findings as one change, the cheap batch: fixes of texts made true, tracebacks of kit checks made teaching lines, and tests that held too little. Most are routine and are noted in their commits. The decider was asked in chat on 2026-10-09, one question per message, each with lettered options and one recommendation, the pick a letter; the numbered sections below hold them.

The brief of the change, read on the trunk at `575b11c`, found the trunk red. Two records carried number dec-0076: [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md), landed in `d9bdc76`, and the record of the module README pages, landed in `23f7ef7` after it. The scan of [`const-catalogs`](../requirements.md#const-catalogs) was RED on the trunk and the kit's CI failed there. Each pull request had passed CI alone: the second one's run was made before the first one landed, and the ruleset of the trunk does not ask a branch to be up to date before it merges. The catalog rules covered a branch not yet landed, and they called a landed number frozen.

The routine pieces are each noted in their commit. The closing clause of the session-start printers is written out where only code stated it. The tie of the hooks files reads a handler's command as well as its arguments. Two kit checks give a teaching line for a module manifest that is no object, and a fix text of `scripts/check-gate-lists.py` offers a restore only where it can turn green. `scripts/check-bare-install.py` gives one line, the same on every Python, for a command it cannot start and for a path it cannot look at. The branch gate's fixture makes its folder under `TMPDIR`. A case pins the order of two configuration failures of [`const-referencing`](../requirements.md#const-referencing), and sentences of module documents are made true. Every module is a draft, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## 1. The collision folded into this change

The collision blocked this change's own merge, since the trunk's ruleset needs the CI check green. The question was whether to fix it in a change of its own or in this one.

- **A. Close small:** fix the collision in its own change first; build this change meanwhile, merge the trunk after that fix, then ask for the yes.
  - **Pros:** this change stays the cheap batch as frozen; the frozen-number question gets its own reasoning and record; the work goes on meanwhile.
  - **Cons:** this change's merge waits on the other change; one more pull request.
- **B. Fold it into this change as a piece:** renumber the record landed second, rewrite its references, and rule how its old acceptance trailer is read.
  - **Pros:** one pull request; this change's CI can turn green without waiting.
  - **Cons:** it grows the scope with a `process` ruling on renumbering an accepted, landed record inside a routine batch; it pulls the README pages' record and its readers into this change's audit.

The session recommended A: "close small, track the rest"; the renumbering rules on frozen numbers and accepted trailers, so it earns its own record; the merge is blocked either way until the fix lands. The decider chose B in chat on 2026-10-09.

<a id="r1"></a>**R1.** One pull request and one record; the collision of dec-0076 is fixed in this change; the routine pieces are noted in their commits.

## 2. One number, one item, in the shared harness

A module's runner sorts its own acceptance items and the shared ones, numbered from 101, together by number, and checked nothing across them. The module with the most items of its own was about one item from 101. An earlier change had pinned the shared numbers and had a kit check hold the ranges the shared document names; the decider had chosen that, option C, over option B, a refusal in the harness.

- **A. Add the earlier option B now, on top of C:** the harness refuses a number two items carry before any item runs, one line per number with the fix, exit 1.
  - **Pros:** "one number, one item" ([rule 4 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r4)) held where every runner passes; it closes the collision one item away; it adds to C and takes nothing from it.
  - **Cons:** a change of the shared harness, so every module's runner runs before its commit; it stops at the first collision instead of judging a range.
- **B. A range rule instead:** the harness refuses an item of a module's own numbered 101 or above.
  - **Pros:** a collision cannot happen; one comparison.
  - **Cons:** it caps every module at 100 items of its own, and the module nearest reaches the cap with its next item, which would force the shared numbers to move, which rule 4 forbids.
- **C. Keep the earlier pick as it stands:** no change of the harness.
  - **Pros:** no work; the earlier pick untouched.
  - **Cons:** the silent collision stays, one item away.

The session recommended A: it closes the one gap C left without undoing C; it is the only option that neither caps a module nor leaves the collision possible; the harness already refuses a malformed filter the same way. The decider chose A in chat on 2026-10-09.

<a id="r2"></a>**R2.** The shared harness refuses an item number two items carry, a module's own and a shared one or any two, before any item runs and before the runner's filter is read: one BROKEN line per number, in number order, naming the number and the items that carry it, with a fix a person can follow, then the runner's could-not-run line, exit 1.

## 3. New holds of the module lists

The record of this change existed once section 1 was answered. The question was whether three findings that a text fix would close for now get holds in `scripts/check-gate-lists.py`, each extending R2 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r2): a module's description in the marketplace that differed from its manifest's; the module namespaces of `constitution.yaml`, which [kernel §7](../constitution/CONVENTIONS.md#k7) says equal the plugin names; and the pair of modules whose scripts the kit's type check puts on `MYPYPATH`, typed in `scripts/check-schema-mirror.py`, in the type-check entry of `scripts/gate-list.sh` and in a comment of `pyproject.toml`. The first two drift silently; the third drifts loudly, as an import error of the type check.

- **A. No new holds:** the description made equal, the namespaces held by the kernel and review, a comment pointing to the type-check entry.
  - **Pros:** the smallest audit; the batch stays fixes of texts and crashes; the check unchanged.
  - **Cons:** a description and a namespace can drift again with every check green; the description comes back at the next manifest edit.
- **B. Three new holds in the check:** a marketplace description equal to its manifest's; every top-level `const-<aspect>` key of `constitution.yaml` names a module folder; the type-check entry's `MYPYPATH` names exactly the folders the schema-mirror check imports from.
  - **Pros:** every finding closed by a check; one check file, one record.
  - **Cons:** about three more ruling items and self-test cases; the third hold repeats what the import error already shows; the check reads a Python tuple out of another script.
- **C. Holds for the two silent drifts; the loud one by the comment of A.**
  - **Pros:** each silent drift gets a check, the loud one left to the failure that shows it; two ruling items in a record that exists anyway.
  - **Cons:** the pair stays typed in two places, tied only by the type check's failure; one more self-test case per hold.

The session recommended C: the record and the audit exist anyway, so a hold costs one ruling item and one case; worth it where drift is silent, not where a red entry already shows it. The decider chose B in chat on 2026-10-09.

<a id="r3"></a>**R3.** `scripts/check-gate-lists.py` holds each module's marketplace `description` equal to its manifest's.

<a id="r4"></a>**R4.** `scripts/check-gate-lists.py` holds every top-level key of the kit's `constitution.yaml` that has a module's form, `const-<aspect>`, to name a module folder.

<a id="r5"></a>**R5.** `scripts/check-gate-lists.py` holds the gate list's type-check entry to put on `MYPYPATH` exactly the module folders `scripts/check-schema-mirror.py` imports from, an empty element a difference too.

## 4. The kit's document folders in a module

One module's own acceptance item refused, in that module's install note, skill and manifest, both the ids of the kit's records and the kit's document folders named with no extension: `docs/decisions`, `docs/research`, `docs/policies`, `docs/requirements`. The ids had moved into `scripts/check-portability.py` with R8 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r8), for every module; the folders were held by that one item alone. Only one installed component of any module named such a folder, inside a fenced example the check exempts.

- **A. Keep the item; its row says why.**
  - **Pros:** no behaviour change; routine; no ruling item.
  - **Cons:** one module holds a form the other ten do not; a copy of a kit rule stays in one module, the kind an earlier change removed from three.
- **B. Move the folder form into the kit check, every module's installed components, with the check's existing exemptions; the item loses its own list of kit names and keeps the rest.**
  - **Pros:** one place for every kit name, all eleven modules alike; the shape the decider chose for the three earlier items; no installed component trips it.
  - **Cons:** the folder names are common defaults of a project, so a prose example outside a code span is refused; the check's text, its self-test, the module's row and the requirement's enforcement cell change.
- **C. Drop the item's list and add nothing.**
  - **Pros:** the ids stay held; the least code.
  - **Cons:** the folder form held by nothing, a regression.

The session recommended B: it ends the last copy of the kit-name rule in a module; the existing exemptions let fenced and inline examples pass. The decider chose B in chat on 2026-10-09.

<a id="r6"></a>**R6.** `scripts/check-portability.py` refuses the kit's document folders — `docs/decisions`, `docs/research`, `docs/policies`, `docs/requirements`, each pair of segments whole — in a module's installed components and in the shared code it reads, outside a public URL and outside Markdown code, as its path forms are. The module item that held its own list of kit names loses it and keeps the rest; R8 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r8) and R1 of [dec-0056-portability-grep-and-gate-lists](dec-0056-portability-grep-and-gate-lists.md#r1) stand as they ruled.

## 5. Two landed items under one number

The kernel said an `id` "never changes after creation; never reused"; the catalog requirements said a number is frozen once landed, that no two items share a number, and that the item already on the trunk keeps its number, with a procedure for the branch not yet landed only. Both records had landed, and the history cites each as "dec-0076", the merge `23f7ef7` with the trailer `Accepted:` and the README pages' id.

- **A. Renumber the record landed second, under an exception in the kernel:** the file by `git mv`, its `id`, its references; the kernel's id rule and the catalog rules gain one rule, that of two landed items under one number the one landed second renumbers; the old trailer reads as the note the carry check gives any id that names no record; the record accepted again in this change's merge, after this change's audit reads it in full.
  - **Pros:** one number, one item restored with no machinery; it follows the rule already written for the branch not yet landed, landing order deciding; the carry check already handles the old trailer.
  - **Cons:** a kernel change, recorded and audited, an exception to "never changes after creation"; the README pages' record joins this change's audit in full; a second yes for an accepted record.
- **B. Rename nothing; the catalog scan accepts this one pair as a recorded exception,** a dial listing it with the record that rules it.
  - **Pros:** the kernel's id rule untouched; no record accepted twice; every citation of either id resolves to a file.
  - **Cons:** a new dial and a new behaviour of the scan for a failure seen once; "dec-0076" ambiguous for good, in documents as in history; the uniqueness requirement gains a standing exception.

The session recommended A: it restores one number for one item, which every catalog check and reader relies on; the cost lands once, in a change that already has a record and an audit; B keeps the ambiguity and adds machinery the kit admits only for a failure that recurs. The decider chose A in chat on 2026-10-09.

<a id="r7"></a>**R7.** Of two items of one catalog that have both landed on the trunk under one number, the one landed second renumbers: its file by `git mv`, its `id` set to the new name, the next number its catalog has not held, and every reference to it in the tree rewritten, since both have landed and a reference anywhere may mean it. The renaming changes no word of a record's body. The catalog scan's fix for two items under one number says it. The README pages' record, landed in `23f7ef7` after dec-0076-hooks-give-each-shared-git-call-a-budget landed in `d9bdc76`, is renumbered by this change, to [dec-0077-module-readme-pages](dec-0077-module-readme-pages.md).

<a id="r8"></a>**R8.** A renumbered record's earlier `Accepted:` trailer names an id that no longer exists; the carry check reads it as the note it gives any such id, and the record is accepted again under its new id, with a receipt, in the merge commit of the change that renumbers it.

## 6. A third collision

Two pull requests each passed CI alone and landed one after the other; no run judged the merged tree until the push to the trunk. The ruleset needs the CI check green, and its setting that asks a branch to be up to date before it merges is off.

- **A. Make the ruleset strict, and say so in the guide:** a branch behind the trunk cannot merge until it has merged the trunk and its CI is green again.
  - **Pros:** CI always judges the tree as it will land, every break between pull requests caught, not only a doubled number; one setting and one sentence.
  - **Cons:** when the trunk moves, each open pull request takes one more merge of the trunk and one more CI run, about 2–3 minutes; sessions merging close together wait for each other.
- **B. A rule held by review, in the guide's "Before the merge":** before `gh pr merge`, the branch merges the trunk and waits for CI green again; no setting.
  - **Pros:** no repository setting; the same check as A where it is followed.
  - **Cons:** a person merging on the forge's page is not held; one forgotten step repeats the collision; [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) asks for a gate where one is possible.
- **C. No prevention; the renumbering of section 5 stays the remedy.**
  - **Pros:** no change and no waiting.
  - **Cons:** the trunk stays red until someone looks; each repeat costs a renumbering and a second acceptance.

The session recommended A: the platform holds it as a gate for free, and only merges close together pay. The decider chose B in chat on 2026-10-09.

<a id="r9"></a>**R9.** Before `gh pr merge`, a branch whose trunk has moved since its last CI run merges the trunk and waits for CI green again; review holds it, and the ruleset stays as it is.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests, the renumbered record's name and the documents; the commits after it correct the code, the documents and this record before its yes, on the findings of its validation and of its carry audit. The message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [kit-shared-items](../../shared/ITEMS.md#g5), the sentence of section 5 on the shared items' numbers, and [item 8 of its section 2](../../shared/GATE.md#g2); [the shared harness](../../shared/constitution_layer_kit/testing/harness.py), the docstring of `run_all`; [its section 3](../../shared/MESSAGES.md#g3), the rows of the runner's lines; [the module template](../../module-template/gate-script-rules.md#r14), rule 14.
3. R3 — [CLAUDE.md](../guide/gate-list-and-ci.md), the bullet "The gate list and CI"; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring.
4. R4 — [CLAUDE.md](../guide/gate-list-and-ci.md), the bullet "The gate list and CI"; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring.
5. R5 — [CLAUDE.md](../guide/gate-list-and-ci.md), the bullet "The gate list and CI"; [check-gate-lists](../../scripts/check-gate-lists.py), its docstring; [pyproject.toml](../../pyproject.toml), its comment on the type check.
6. R6 — [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [check-portability](../../scripts/check-portability.py), its docstring; [`const-doc-budgets`](../../modules/const-doc-budgets/MODULE.md#t10), row T21.
7. R7 — [kernel §1](../constitution/CONVENTIONS.md#k1), the exception to the `id` rule, and [the frontmatter schema](../constitution/schemas/document-frontmatter.schema.json), the description of `id`; [requirement A13.3](../requirements.md#a13-3), [requirement A13.4](../requirements.md#a13-4) and [requirement A5.8](../requirements.md#a5-8); [`const-referencing`](../../modules/const-referencing/MODULE.md#t11), item 1 of its siblings list, and [its deferred list](../../modules/const-referencing/MODULE.md#t12), item 5; [`const-catalogs`](../../modules/const-catalogs/MODULE.md#t5), rules C-b and C-c, and [its message K3](../../modules/const-catalogs/MODULE.md#t6); [its skill](../../modules/const-catalogs/plugin/skills/catalog-item/SKILL.md), sections 2 and 4; [rule 3 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r3) and [its rule 14](../policies/plc-0004-decision-records.md#r14); [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7). That dec-0077-module-readme-pages was renumbered by this change is history.
8. R8 — [check-carry-lists](../../scripts/check-carry-lists.py), its docstring, the receipt paragraph; [rule 5 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r5).
9. R9 — [CLAUDE.md](../../CLAUDE.md), the bullet "Before the merge".
