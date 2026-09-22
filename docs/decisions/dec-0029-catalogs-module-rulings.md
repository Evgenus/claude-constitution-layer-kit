---
id: dec-0029-catalogs-module-rulings
type: task-record
title: Rulings of the const-catalogs authoring — catalogs declared in the module's own dial, independent of policies; a taken number refused at write time; history read for advice only
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-catalogs authoring

## Context

The third module, [`const-catalogs`](../requirements.md#const-catalogs), was authored on 2026-09-20 from its research comparison ([research-const-catalogs](../research/res-0003-const-catalogs.md)) and the rows of [aspect A13](../requirements.md#a13). It is the first real test of the shared gate code with a third consumer, and the first gate of the kit that resolves no policy. Four questions were put to the decider in chat, each with lettered options; the rest was derived by the authoring session and is listed in section 5 for the decider to override before the yes. Two of the four answers overturn the comparison's recommendation, and the first reverses an earlier ruling of the decider's own.

## 1. Where a numbered kind is declared

[dec-0004-catalogs-module](dec-0004-catalogs-module.md), item 5, chose the kind's policy as the default place — `catalog: {prefix, width}` in the policy's namespace — with the module's dial as the fallback for projects without policies. That ruling predates [dec-0008-policies-by-location](dec-0008-policies-by-location.md) and [dec-0011-one-policy-per-kind](dec-0011-one-policy-per-kind.md).

- **A. Both paths, as the row said.**
  - **Pros:** the row and both earlier rulings stand.
  - **Cons:** every cost of B and of D together, and a double-declaration check across two places.
- **B. Policy-declared only, the dial deferred.**
  - **Pros:** a kind's calibration stays with the kind's policy; no change to the shared pipeline.
  - **Cons:** a key with one reader stays in the kernel schema; a project without policies cannot number anything; every write pays for the whole policy index — 373 ms measured on this repository.
- **C. Both, the dial only where a root policy exists.**
  - **Pros:** avoids one pipeline change.
  - **Cons:** serves nobody: the dial's only named user is a project without policies.
- **D. Dial-declared only: `const-catalogs.catalogs`, a list of `{prefix, territory, width}`, independent of policies.**
  - **Pros:** the module reads its own namespace and nothing else, the most literal reading of [kernel §6](../../kernel/CONVENTIONS.md#k6); the kernel schema shrinks to what two modules need; no index, no resolution, 172 ms per write where B took 373; works in any repository; a double declaration is a duplicate in one list.
  - **Cons:** where a policy exists, the territory is declared twice and can drift — mitigated by YAML's own alias, which `yaml.safe_load` resolves; two mechanical changes to the shared code, touching the two accepted modules; the widest set of text amendments; reverses two earlier rulings.

The session first recommended B, against a dial it called "a second way to claim territory". The decider asked whether catalogs could be independent of policies; the probe showed the objection overstated — a catalog's territory binds no document to a policy, and [kernel §3](../../kernel/CONVENTIONS.md#k3) itself calls catalogs "module and project concerns" — and showed that no sibling reads the policy-side key, which therefore sat in the kernel schema against the kernel's own admission rule. Recommendation revised to D. Chosen D by the decider in chat on 2026-09-20.

**Ruling.** A numbered kind is an entry of `const-catalogs.catalogs`: `prefix`, `territory`, `width`. The `catalog` key leaves the kernel's dials schema. Item 5 of [dec-0004-catalogs-module](dec-0004-catalogs-module.md) is reversed, and the location fixed by ruling 1 of [dec-0017-records-numbered-now](dec-0017-records-numbered-now.md) moves: prefix `dec` and width 4 stand, the line leaves the policy's namespace for the module's. No id, number, prefix or width changes. A catalog declared by naming a policy is deferred with its signal.

## 2. Whether the hook refuses a number that is already taken

[Requirement A13.4](../requirements.md#a13-4) placed uniqueness in a CI script on a pull request.

- **A. Scan only.**
  - **Pros:** the row's enforcement stands; the hook matches one path.
  - **Cons:** allocation is advice, computed by a model counting files, and a miscount is found at the pull request, after references to the wrong number were written.
- **B. The hook also blocks a file that does not exist yet under a number another item in the working tree carries,** naming the holder and the next number.
  - **Pros:** a miscount is corrected in the turn it happens, with an exact fix; about 40 ms, for new items only.
  - **Cons:** extends the row's enforcement moment; a second path in the hook, creation against edit; must not be read as covering other branches.
- **C. The same, as a note that lets the write through.**
  - **Pros:** never blocks.
  - **Cons:** a deterministic check delivered as advice blurs gate and advisory; `severity: warn` already exists.

Recommendation B. Chosen B by the decider in chat on 2026-09-20.

**Ruling.** Finding K4, at write time, for a new file only. An item that exists is never judged on its number at write time: of two that collide the hook cannot tell which is frozen on the main branch. Collisions between existing items and across branches stay the scan's finding K3.

## 3. How the listing and the next number are produced

The matrix said "listing script"; the comparison recommended `--list` and `--next` modes, arguing that a named command cannot read the declarations.

- **A. `--list` and `--next` modes of the entry point.**
  - **Pros:** exact, one mechanism, the row as written.
  - **Cons:** module-defined modes in the shared command line, for an advisory assist whose errors the hook now catches.
- **B. A second, advisory entry point.**
  - **Pros:** no shared change.
  - **Cons:** its own parsing, guard and preflight: more code than A.
- **C. Two git-native commands the skill names.**
  - **Pros:** no code; matches the row's own definition of a catalog, the set of files carrying its prefix.
  - **Cons:** the model adds one; the glob lists by prefix, not by territory.
- **D. C, and the scan's count line names each catalog's highest number.**
  - **Pros:** the next number comes deterministically from the declared territory; about ten lines, no new mode; the line is useful in CI too.
  - **Cons:** the count line carries more than a count; the listing keeps C's looseness.

Recommendation D, against the comparison: after ruling 1 a catalog is identified by its prefix, so the listing needs no declaration, and the number comes from the scan, which reads them. Chosen D by the decider in chat on 2026-09-20.

**Ruling.** No listing script and no allocation mode. The scan's count line names every catalog's reach; the skill names the listing command, the title `grep`, and the case-insensitive resolver. The `--list` and `--next` modes are deferred with their signal.

## 4. Whether a deleted top number may be issued again

The row said "highest existing on the branch + 1"; the comparison's experiment E1 showed that this re-issues the number of a deleted highest item, so a bare citation written before the deletion would come to mean another document.

- **A. As written, stated as a limit.**
  - **Pros:** the same in every clone; full names stay unambiguous.
  - **Cons:** a bare number silently changes its target; records of this repository may be deleted once carried, and the newest is a likely one.
- **B. Advice reads history; refusals do not.** The number named is one more than the highest of the working tree and of every name the branch's history ever added.
  - **Pros:** a deleted top number is not suggested again; the gate's verdict is the same in every clone; one source of the number.
  - **Cons:** one `git log` per scan and per new item — 32 ms here, growing with history; a shallow clone falls back to the tree and must say so; extends the row's wording.
- **C. The gate refuses a number history held.**
  - **Pros:** re-issue blocked.
  - **Cons:** the verdict depends on clone depth.
- **D. Skill prose only.**
  - **Pros:** no code.
  - **Cons:** the model compares two numbers by hand, and the hook's fix would contradict the skill.

Recommendation B. Chosen B by the decider in chat on 2026-09-20.

**Ruling.** History is read for advice only: the fix text of K1 and K4 and the scan's count line. Rename detection is switched off when reading it, since a rename is otherwise no addition — sixteen of this repository's records would be missed. A shallow clone is named as such in the count line; a repository with no commit has no history and nothing fails. Refusing a number that history held is deferred with its signal.

## 5. Rulings taken by the authoring session

No real choice was put to the decider on these; each is the session's derivation, open to override before the yes.

1. **An item** is a Markdown document whose path lies in an entry's territory — by path alone, no declaration in the envelope. Where two territories hold one file, the catalog whose prefix the file name carries judges it, else the first listed.
2. **One name.** [Requirement A13.1](../requirements.md#a13-1) is read as "id equals stem", as the context of [dec-0017-records-numbered-now](dec-0017-records-numbered-now.md) reads it; a missing id and an unreadable envelope are reported here too, since the module must work with no sibling installed.
3. **A malformed entry and a prefix listed twice are configuration failures,** exit 1, after the precedent of the second module's dial failures and the row's own "fails load".
4. **One entry point:** the hook is the write-time gate and `--scan` the check for CI.
5. **A free number below the highest passes.** The gate asks for free, not for next; it cannot tell a deleted item's number from one renumbered away before it landed.
6. **The width is a ceiling:** past the last number it can write, the fix says the catalog is full and names no file; `width` itself stops at 9, where a fix line would outgrow what the platform shows.
7. **Who renumbers.** The row's "younger branch" is read as the branch that has not landed: the item already on the main branch keeps its number. Commit dates are no measure — the comparison's experiments E4 and E5 showed templated files and shallow checkouts misdating them. The row now says so.
8. **A file that exists keeps the number its name shows.** The fix of K1 tells a legacy item under a malformed name to keep its number, since it may be cited by it, and a new item is numbered above every number a name in the territory shows, formed or not; where another file shows the same number each is told of the other, and a number the width cannot write is named as such. Found by the fresh-context validation, the rivals by its second pass: the first text would have renumbered cited items on the adoption path.
9. **No verdict waits for advice.** The hook reads history only once a finding that names a number is certain, against one clock of five seconds, and the history reader raises nothing — the clock, a failing git and a vanished one all end in the working tree's answer; where history is incomplete or was not read the fix and the scan's line say so instead of claiming "deleted items included", while a repository with no commit has a complete, empty history. Found by the same validation, on a synthetic history of 20,000 commits; the vanished git and the silent scan line by its second pass.
10. **Digits are ASCII and the extension is lowercase `.md`:** what the skill's listing glob cannot see is not the form.
11. **The reference forms are carried by the skill,** not by a policy: a module ships none. The row's destination now says so.

## 6. The shared gate code, met by a third consumer

Four seams, each fixed at the source with the fixtures of all three modules green; [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) asked for exactly this evidence.

1. The pipeline skipped when the dials name no root policy. That is the question of a gate that resolves policies, which now answers it itself; the type of the index builder does not let one forget.
2. The green line named a governing policy. It now says what the examined document is, in the module's words where no policy is involved.
3. The fixture subject assumed a policy. It now carries the green words, the dials patch that re-declares its territory, and whether the gate resolves policies; a gate that resolves none leaves out the six items about the root policy and the policies' documents, every other item keeping its number.
4. One shared item wrote its deeply nested envelope to the path of the subject's blocked write, which for this module is blocked by its name; it now writes to the path of the write that passes.

One seam was opened and closed again: a policy's namespace handed over as read, needed only while option B of section 1 stood.

## Applied

In the commit that creates this record: the module's [MODULE.md](../../modules/const-catalogs/MODULE.md); the `catalog` key removed from `kernel/schemas/constitution.schema.json`; the kit's declaration moved in `constitution.yaml`; rows [A13.1](../requirements.md#a13-1), [A13.2](../requirements.md#a13-2), [A13.3](../requirements.md#a13-3), [A13.4](../requirements.md#a13-4), [A13.6](../requirements.md#a13-6) and [A13.7](../requirements.md#a13-7) amended and the module's specification replaced by its stub; rules 3 and 6 of [kit-decision-records](../policies/plc-0004-decision-records.md); one sentence each in the documents of the two accepted modules and one clause of the second module's skill. The module's scripts, fixtures, skill and install note, and the shared-code changes with [kit-shared-gate-code](../../shared/GATE.md), landed in the commits before it. The record is born `inactive`.

## Rulings carried

1. Catalogs are declared in the module's own dial, independent of policies — [requirement A13.7](../requirements.md#a13-7); [§3](../../modules/const-catalogs/MODULE.md#t3) and [§7](../../modules/const-catalogs/MODULE.md#t7) of the module's document; rule 3 of [kit-decision-records](../policies/plc-0004-decision-records.md). The kernel schema no longer holds the key: its absence is the carried state.
2. The YAML alias as the answer to a territory declared twice — the module's install note, and the kit's own `constitution.yaml`.
3. A new item's number is refused when taken; an existing item is never judged on its number at write time — [requirement A13.4](../requirements.md#a13-4); [§3](../../modules/const-catalogs/MODULE.md#t3), [§5](../../modules/const-catalogs/MODULE.md#t5) and limit 9 of [§9](../../modules/const-catalogs/MODULE.md#t9).
4. No listing script and no allocation mode; the count line names each catalog's reach — [requirement A13.2](../requirements.md#a13-2) and [A13.3](../requirements.md#a13-3); the artifacts table and the G1 row of [§6](../../modules/const-catalogs/MODULE.md#t6).
5. History is advice, never a verdict; rename detection off; a shallow clone named — [requirement A13.3](../requirements.md#a13-3); [§3](../../modules/const-catalogs/MODULE.md#t3), the advisory row and limit 7 of [§9](../../modules/const-catalogs/MODULE.md#t9), platform fact 11 of [§6](../../modules/const-catalogs/MODULE.md#t6).
6. Section 5, items 1 to 11 — [§3](../../modules/const-catalogs/MODULE.md#t3) of the module's document (items 1 to 4, 7 to 10), limits 3, 7 and 8 of its [§9](../../modules/const-catalogs/MODULE.md#t9) (items 5, 6 and 9), the K1 row of its [§6](../../modules/const-catalogs/MODULE.md#t6) (item 8); "id equals stem" also in [requirement A13.1](../requirements.md#a13-1), who renumbers in [A13.4](../requirements.md#a13-4), the carrier of the reference forms in [A13.6](../requirements.md#a13-6).
7. Section 6, seams 1 to 3 — [kit-shared-gate-code §2](../../shared/GATE.md#g2) items 3 and 8, the G1 and G1.5 rows of [§3](../../shared/GATE.md#g3), and the closing paragraph of [§5](../../shared/GATE.md#g5). Seam 4 and the seam opened and closed: history only. One limit of the territory dialect, found by the validation, is every gate's: a negated pattern takes a file out only where git can re-include it — item 13 of [§4](../../shared/GATE.md#g4).
8. The deferred items with their signals — a catalog declared by naming a policy, the `--list` and `--next` modes, refusing a number history held, the `--base` option — [§12](../../modules/const-catalogs/MODULE.md#t12) of the module's document.
9. The reversal of item 5 of [dec-0004-catalogs-module](dec-0004-catalogs-module.md) and the relocation of ruling 1 of [dec-0017-records-numbered-now](dec-0017-records-numbered-now.md): history only — both records are `inactive`, and the current texts of item 1 state what holds.
10. The session's first recommendation of B and its revision: history only.
