---
id: dec-0064-shared-gate-defects-one-refusal-one-path-rule
type: task-record
title: The shared gate code takes the unknown-dial refusal and the helpers the modules wrote again, and a dial path is read with the platform's separator
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shared gate code takes the unknown-dial refusal and the helpers the modules wrote again, and a dial path is read with the platform's separator

## Context

An audit on 2026-10-02 looked for gate logic that modules wrote again instead of sharing. It found copies that had drifted apart, and the drift was where the defects were. A key with a line break in it split a BROKEN line in eight modules, and in hook mode only the first line reaches the user, so the fix half was lost. A long value flooded the screen in five places. The shared message for a pattern git misreads always added `.territory` to the dial's name, so it named a dial that does not exist for any module's own dial. Three modules disagreed on a `reason` that ends in a line break. The hook skipped a file named `.md` that the scan examined. Two modules each kept a copy of the platform's 10,000-character cap with no date. Four session printers cut a path at its first colon, so a repository under `client:acme` was named `client`. A message listed the kernel's keys without `territory_dialect`. Six styling messages spoke as if they stated the project's style guide, when the scan holds the shipped values.

The change that this record rules is on one branch. Every module is a draft at `0.0.x`, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). [Rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) admits code to the shared source only when it implements a kernel section or a gate-script rule of [template section 6](../../module-template/MODULE.md#t6) and two or more modules need it, and the record argues each admission. Five questions were put to the decider in chat, one per message, each with lettered options, the pick a letter. Section 6 holds what the change makes where no choice existed.

## 1. Whether the unknown-dial refusal is shared

Every module refuses a key in its own namespace that it does not read. The refusal exists in eleven modules in three forms. Referencing adds `shown`. Locations has its own wording. Four modules look at keys in file order and show a line break raw. Only two escape it. The refusal is not a kernel section, since [kernel section 6](../../kernel/CONVENTIONS.md#k6) leaves module namespaces open, and it is not a named gate-script rule either.

- **A. Share it under gate-script rule 8, no fail-open.** One shared text and one shared function replace the eleven forms.
  - **Pros:** a dial ignored in silence is a silent pass, which rule 8 forbids, so the refusal belongs to that rule; one text, sorted, escaped, cut; the eight modules with the two-line defect are fixed at once; a future module inherits it.
  - **Cons:** it reads rule 8 broadly, since rule 8 names exceptions and unparseable input and not misspelt dials; it is the one admission here that neither a kernel section nor a named rule makes plain.
- **B. Keep it in each module and share only `echoed`.** The modules keep their refusals and call the shared escape.
  - **Pros:** no stretch of rule 2; the modules keep their own wording.
  - **Cons:** eleven copies remain, with three forms; the next module copies one of them again, as styling copied the weakest.

**Recommendation.** A, by the session: the silent pass is the harm rule 8 names, and one text is what stops the forms from drifting again.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R1.** The refusal of a key of a module's namespace that the module does not read is shared code, of class R, admitted under rule 8 of [template section 6](../../module-template/MODULE.md#t6). It is the shared message C5.10, built by `messages.c5_unknown_dial`, and the shared function `dials.refuse_unknown_keys(own, known)`. Every module calls it, and it replaces the per-module forms in all eleven, locations' wording included. It names the first key outside the module's list in sorted order, cut at 80 characters with its backslashes and line breaks escaped. The list it gives is the module's, in the order the module lists it. A nested name a module checks the same way takes the whole name as the key.

## 2. A `reason` that ends in a line break

A departure's `reason` must be one line. Styling stripped the value before it looked for a line break, so it accepted what a YAML block scalar, `reason: |`, gives. Language and doc-budgets refused it.

- **A. Trim it, then accept.** A break at the end is removed. A break in the middle is refused.
  - **Pros:** a valid one-line reason written as a block scalar works; the rule matches styling, which already did so; the line that is still refused is the one that would split a message.
  - **Cons:** two modules accept what they refused before; the rule is two clauses, not one.
- **B. Refuse it.** Any line break is refused, styling included.
  - **Pros:** one literal rule, the stricter one; no trimming to explain.
  - **Cons:** a user who writes `reason: |` with one line gets a refusal for a value that is one line; styling gets stricter with no friction behind it.

**Recommendation.** A, by the session: the refusal protects the one-line message, and a trailing break does not break it.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R2.** A departure's `reason` that ends in a line break is trimmed and accepted, and one with a line break in the middle is refused, in [`const-language`](../requirements.md#const-language), [`const-doc-budgets`](../requirements.md#const-doc-budgets) and [`const-styling`](../requirements.md#const-styling) alike.

## 3. How a dial path is read

`root_policy`, `log_dir`, a template path and the `docs` paths of task-close each had a rule for "repository-relative". Task-close refused `..\x` and kept `./docs//core.md` as written, so a pair declared that way never saw its document updated. The shared reader and locations kept `..\x` and a leading space.

- **A. A backslash is a separator everywhere.** The value is rewritten with `/` first.
  - **Pros:** one verdict on every platform, as for a pattern, which every platform reads the same way; `..\x` is refused everywhere.
  - **Cons:** on macOS and Linux a backslash is a legal character in a file name, so the shared checks for `log_dir` and `root_policy` would change their verdicts there; it adds a rewrite rule that no platform asked for.
- **B. Keep the platform's separator, `os.sep`.** No rewrite; the file system's own reading decides.
  - **Pros:** a path means what the machine reads; no verdict changes on macOS and Linux; no new rewrite rule.
  - **Cons:** one dials file gets two verdicts on two machines for `..\x`, which is the cost the first option avoids.

**Recommendation.** A, by the session, for the single verdict.

**Choice.** B, by the decider, in chat on 2026-10-02. It differs from the recommendation. The session's objection stands as a shared limit: the two verdicts are written down, not removed.

**R3.** A dial path goes through the shared `dials.relative_path`: a blank value, an absolute one and one that leaves the repository by `..` are refused; `./` and `//` are normalised; the separator is the platform's own, so a backslash separates only where the platform says so. `..\x` leaves the repository on Windows and is one file name on macOS and Linux. The shared code states this as a limit, so no module's document claims one verdict everywhere.

**R4.** The consequence of R3, put to the decider in chat on 2026-10-02 and left without objection: task-close reads the `docs` paths of a coverage pair through the shared `relative_path`. It no longer refuses `..\x.md` on macOS and Linux, where it is one file name, and it normalises `./docs//core.md`. It keeps its own refusal of a trailing slash, since a pair's documents are files.

## 4. A file named `.md`

The hook decided what Markdown is by the path's suffix, and a file named just `.md` has none. It skipped the file as "not a .md file". The scan, which tests the name's ending, listed and examined it.

- **A. Examine it in both.** A name that ends in `.md` is Markdown, in any case, in the hook and in the scan.
  - **Pros:** the hook and the scan agree; one test, by the name's ending, is all that "Markdown document" needs.
  - **Cons:** a file with no stem is examined as a governed document, which is almost always a mistake of the author.
- **B. Skip it in both.** A name needs a stem.
  - **Pros:** a name with no stem is not a document in any sense.
  - **Cons:** the scan stops listing a file it lists today, so a stray `.md` would pass unseen.

**Recommendation.** A, by the session: the failure to examine is the worse one, and the scan already holds the file as a document.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R5.** Markdown means a name that ends in `.md`, in any case, a file named just `.md` included, in the hook and the scan alike. Both call the one function `repository.is_markdown`.

## 5. The shared-code page over its ceiling

The shared-code page, [kit-shared-gate-code](../../shared/GATE.md), grew from about 45,500 characters to about 50,900 with this change. Its ceiling `shared-code` is 49,000 at warning, so the length check reports a note and no finding.

- **A. Split its section 5 as the change's last step.** The acceptance items move to a page of their own.
  - **Pros:** the page is under its ceiling at once; the items have a home that holds only them.
  - **Cons:** a new document or kind inside a change that is already large; every link to that section changes, and an anchor is never renumbered under [rule 5 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r5).
- **B. Raise the ceiling.** One number in the dials file.
  - **Pros:** one line.
  - **Cons:** the ceiling was set from fourteen days of history plus ten percent; raising it each time the page grows empties it.
- **C. Leave it at warning and decide after the change lands.** The decider sees the page's final size and then picks A or B.
  - **Pros:** no cut made before the last edit of the change is known; the note stays visible.
  - **Cons:** the scan reports the note until the decider decides.

**Recommendation.** A, by the session.

**Choice.** C, by the decider, in chat on 2026-10-03. This defers the choice between A and B. It is no ruling on the page's length, and this record does not decide it.

**R6.** The ceiling `shared-code` stays at 49,000 characters at warning, and the page stays over it, until the decider decides. This change does not alter the ceiling.

**R7.** History only for the deferral itself: the decider will choose between splitting section 5 and raising the ceiling after this change lands. That decision is a later act, with its own record if it is a `process` ruling, and this record rules neither way.

## 6. What the change makes where no choice existed

These items carry no options. Each follows from the five answers above or from the kit's rules, and each stands open to the decider's override before the yes. The class of each shared part is the one [rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) asks for: K means the code implements a kernel section literally, R a gate-script rule of [template section 6](../../module-template/MODULE.md#t6).

**R8.** `messages.echoed(value)` is shared, of class R, a part of the shared `messages` beside `shown`. It cuts a value as `shown` does, then shows its backslashes and line breaks escaped, so that a BROKEN line stays one line. All eleven modules need it. A module echoes every key or value it takes from a document or from a dial through it, nested names included.

**R9.** The shared message C5.7, a pattern git would misread, takes the dial's whole path as `where`: `{k}.territory` for a policy's namespace, `{module}.{dial}` for a module's own dial. It cuts and escapes the pattern. This is class K, [kernel section 6](../../kernel/CONVENTIONS.md#k6) territory patterns, already admitted. It is a fix for every caller, not a widening for one module. [`const-language`](../requirements.md#const-language), [`const-doc-budgets`](../requirements.md#const-doc-budgets) and [`const-styling`](../requirements.md#const-styling) call the shared refusal and keep no check of their own.

**R10.** `dials.texts(value)`, the non-empty strings of a list, and `dials.GATE_KEYS`, the two dials every gate has, `severity` and `log_dir`, are shared, of class K: the first is the shape the shared territory reader already checks, the second names what the shared reader already reads. Five modules need `texts`, and all eleven use `GATE_KEYS`; a module that blocks nothing lists `LOG_DIR_KEY` alone.

**R11.** `dials.relative_path` of R3 is shared, of class K for `root_policy` ([kernel section 6](../../kernel/CONVENTIONS.md#k6)) and the same rule for `log_dir`. The shared reader, [`const-locations`](../requirements.md#const-locations) and [`const-task-close`](../requirements.md#const-task-close) use it.

**R12.** `repository.is_markdown` of R5 is shared, of class K. The hook, the scan, [`const-referencing`](../requirements.md#const-referencing), [`const-doc-budgets`](../requirements.md#const-doc-budgets) and [`const-locations`](../requirements.md#const-locations) call it, and none keeps a test of its own.

**R13.** `pipeline.within_the_cap(findings, most=None)` and `SHOWN_CHARACTERS`, 8,000, are shared, of class R, a widening of `pipeline` for the two modules that print findings after a write, [`const-language`](../requirements.md#const-language) and [`const-referencing`](../requirements.md#const-referencing). The other modules do not call it and change nothing. It always shows the first finding, then the ones that fit, never more than `most`. The platform fact behind the number is a shared limit with its version and date, read 2026-10-03 on Claude Code 2.1.286: a hook's text over 10,000 characters is replaced by a path and a preview.

**R14.** `pipeline.Skip` carries `kind`, a `model.SkipKind`, and `where`, the path, root, file or tool the reason names, whole. This is class R, a widening of a part already shared with typed fields that four modules need, the session printers of [`const-catalogs`](../requirements.md#const-catalogs), [`const-interaction`](../requirements.md#const-interaction), [`const-decision-records`](../requirements.md#const-decision-records) and [`const-doc-budgets`](../requirements.md#const-doc-budgets). A module that says a skip in its own words switches on `kind` and takes `where` whole, and never parses `reason`.

**R15.** The kernel's two key names, `ROOT_POLICY_KEY` and `DIALECT_KEY`, and the pair `KERNEL_KEYS`, stand in the shared `model`, of class K, and the shared C4b message builds its list from them. C4b now names `territory_dialect` as well as `root_policy`.

**R16.** The six styling messages that state a shipped value, Y1 to Y4, Y8 and Y10, say "the shipped default" and not "the default", and each fix ends with one clause: a project whose guide changed the default declares the departure over its whole tree and names the guide's entry in the reason. The structural messages stay as they were. R8 of [dec-0044-styling-module-rulings](dec-0044-styling-module-rulings.md) is unchanged: the twelve signatures and the fixed values stay, and only the wording and the declared limit change.

**R17.** A limit of [`const-styling`](../requirements.md#const-styling) is written down. The scan holds the shipped values of three defaults, three heading levels, the dash and the asterisk. A project that amends one declares a departure for that signature over its whole tree, and the scan then stops checking the signature and does not check the new value. The shipped style guides and the install note say the same in plain words.

**R18.** Deferred trigger: two value dials of [`const-styling`](../requirements.md#const-styling), the deepest heading level and the bullet marker, are built only when a consumer's commit note amends one of them in its guide and declares the whole-tree departure. Building them is a `process` ruling and needs a record of its own.

## Applied

The commits of this branch before the one that adds this record apply every item. They change the shared code, the eleven modules, the shared-code page, the module documents, the install note and the style guides of styling. The shared-code page states each shared part with its class, in the rows of its section 1 and in the limits of its section 4. The Windows branch of `relative_path` and of task-close's backslash test is written and has not been run on Windows. So this record is born `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `dials` row of section 1 for the class and the callers; [section 2](../../shared/GATE.md#g2), item 4, for the call; [section 3](../../shared/GATE.md#g3), the row C5.10, for the text.
2. R2 — [`const-language`](../../modules/const-language/MODULE.md#t7), [`const-doc-budgets`](../../modules/const-doc-budgets/MODULE.md#t7) and [`const-styling`](../../modules/const-styling/MODULE.md#t7), each its dial `departures`.
3. R3 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 15 of section 4; [section 1](../../shared/GATE.md#g1), the `dials` row.
4. R4 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t7), its dial `coverage`; [kit-shared-gate-code](../../shared/GATE.md#g4), limit 15 of section 4.
5. R5 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 7 of section 4; [section 1](../../shared/GATE.md#g1), the `repository, territory` row.
6. R6 — [the dials file](../../constitution.yaml), the ceiling `shared-code` of `const-doc-budgets`.
7. R7 — history only: the deferral of the decider's choice between a split and a raise; the ceiling itself is R6's.
8. R8 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `messages` row of section 1; [section 2](../../shared/GATE.md#g2), item 5.
9. R9 — [kit-shared-gate-code](../../shared/GATE.md#g3), the row C5.7 of section 3; [section 2](../../shared/GATE.md#g2), item 4; [section 1](../../shared/GATE.md#g1), the `dials` row.
10. R10 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `dials` row of section 1.
11. R11 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `dials` row of section 1; limit 15 of [section 4](../../shared/GATE.md#g4).
12. R12 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `repository, territory` row of section 1; limit 7 of [section 4](../../shared/GATE.md#g4).
13. R13 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `pipeline` row of section 1; limit 14 of [section 4](../../shared/GATE.md#g4).
14. R14 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `model` row of section 1; [section 2](../../shared/GATE.md#g2), item 3.
15. R15 — [kit-shared-gate-code](../../shared/GATE.md#g3), the row C4b of section 3.
16. R16 — [`const-styling`](../../modules/const-styling/MODULE.md#t6), the error messages of section 6.
17. R17 — [`const-styling`](../../modules/const-styling/MODULE.md#t9), limit 9 of section 9.
18. R18 — [`const-styling`](../../modules/const-styling/MODULE.md#t12), item 7 of section 12.
