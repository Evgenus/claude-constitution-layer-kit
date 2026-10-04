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

The change that this record rules is on one branch. Every module is a draft at `0.0.x`, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). [Rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) admits code to the shared source only when it implements a kernel section or a gate-script rule of [template section 6](../../module-template/MODULE.md#t6) and two or more modules need it, and the record argues each admission. Seven questions were put to the decider in chat, one per message, each with lettered options, the pick a letter: five in sections 1 to 5, and two more in sections 7 and 8, put while the carry audit ran. Section 6 holds what the change makes where no choice existed.

## 1. Whether the unknown-dial refusal is shared

Every module refuses a key in its own namespace that it does not read. The refusal exists in eleven modules in three forms. Referencing adds `shown`. Locations has its own wording. Four modules look at keys in file order and show a line break raw. Only two escape it. The refusal is not a kernel section, since [kernel section 6](../../kernel/CONVENTIONS.md#k6) leaves module namespaces open, and it is not a named gate-script rule either.

- **A. Admit it to shared code under gate-script rule 8, no fail-open.** One shared function with one message replaces the three forms in all eleven modules.
  - **Pros:** a dial that is silently ignored is a silent pass, so rule 8 fits; one fix reaches every module, future modules too; the three forms become one.
  - **Cons:** this record must argue the admission; it touches all eleven modules; locations loses its own wording.
- **B. Keep the refusal in each module, and share only a small `echoed()` helper.** `echoed()` escapes line breaks and cuts long values; each module keeps its own text but sends the key through it.
  - **Pros:** no admission question; the visible defect, split lines and lines of 12,000 characters, is still fixed everywhere.
  - **Cons:** the three forms of one message stay; the next module will copy one of them again.

**Recommendation.** A, by the session: the refusal exists to stop a silent pass, which is what rule 8 is about, and the split-line defect shows what copied code costs.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R1.** The refusal of a key of a module's namespace that the module does not read is shared code, of class R, admitted under rule 8 of [template section 6](../../module-template/MODULE.md#t6). It is the shared message C5.10, built by `messages.c5_unknown_dial`, and the shared function `dials.refuse_unknown_keys(own, known)`. Every module calls it, and it replaces the per-module forms in all eleven, locations' wording included. It names the first key outside the module's list in sorted order, cut at 80 characters with its backslashes and line breaks escaped. The list it gives is the module's, in the order the module lists it. A nested name a module checks the same way takes the whole name as the key.

## 2. A `reason` that ends in a line break

A departure's `reason` must be one line. Styling stripped the value before it looked for a line break, so it accepted what a YAML block scalar, `reason: |`, gives. Language and doc-budgets refused it.

- **A. Trim, then accept.** A single line break at the end is removed. A break in the middle is still refused.
  - **Pros:** `reason: |` is a normal YAML form; a user who writes it is not told off for a quirk of YAML; it matches what styling does today.
  - **Cons:** the value kept differs from the value as written; language and doc-budgets change from refusing to accepting.
- **B. Refuse.** Any line break is refused, a trailing one included.
  - **Pros:** strict and explicit; the value is checked exactly as written; it matches two of the three modules today.
  - **Cons:** `reason: |` is refused, and the user must switch to a plain or quoted string; styling changes from accepting to refusing.

**Recommendation.** A, by the session: the trailing break comes from the YAML block form, not from the user's text, and a break in the middle is still refused, so the reason stays one line.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R2.** A departure's `reason` is trimmed of white space and line breaks at both ends and then accepted, and one with a line break in the middle is refused, in [`const-language`](../requirements.md#const-language), [`const-doc-budgets`](../requirements.md#const-doc-budgets) and [`const-styling`](../requirements.md#const-styling) alike.

## 3. How a dial path is read

`root_policy`, `log_dir`, a template path and the `docs` paths of task-close each had a rule for "repository-relative". Task-close refused `..\x` and kept `./docs//core.md` as written, so a pair declared that way never saw its document updated. The shared reader and locations kept `..\x` and a leading space.

- **A. Treat a backslash as a separator everywhere.** `..\x`, `a\..\..\x` and `C:\x` are refused on every machine, and `a\b` is kept as `a/b`.
  - **Pros:** one verdict on every machine, as limit 9 of the shared-code page already promises for patterns; it closes a way out of the repository; it matches what task-close does today.
  - **Cons:** a file name that really holds a backslash can no longer be used in a path dial; the shared C5.1 and C5.9 verdicts change on macOS and Linux.
- **B. Use the platform's own separator, `os.sep`, as the shared code does today.** Each machine keeps its current behaviour.
  - **Pros:** no change in verdicts; file names with a backslash stay usable on macOS and Linux.
  - **Cons:** two verdicts for one file on two machines; `..\x` passes on macOS and Linux; task-close stays different from the rest.

**Recommendation.** A, by the session: the same dials file should get the same verdict on every machine, and a real file name with a backslash in a dial path is very unlikely.

**Choice.** B, by the decider, in chat on 2026-10-02. It differs from the recommendation. The two verdicts are written down as a shared limit.

**R3.** A dial path goes through the shared `dials.relative_path`: a blank value, an absolute one and one that leaves the repository by `..` are refused; `./` and `//` are normalised; the separator is the platform's own, so a backslash separates only where the platform says so. `..\x` leaves the repository on Windows and is one file name on macOS and Linux. The shared code states this as a limit, so no module's document claims one verdict everywhere.

**R4.** The consequence of R3, put to the decider in chat on 2026-10-02 and left without objection: task-close reads the `docs` paths of a coverage pair through the shared `relative_path`. It no longer refuses `..\x.md` on macOS and Linux, where it is one file name, and it normalises `./docs//core.md`. It keeps its own refusal of a trailing slash, since a pair's documents are files.

## 4. A file named `.md`

The hook decided what Markdown is by the path's suffix, and a file named just `.md` has none. It skipped the file as "not a .md file". The scan, which tests the name's ending, listed and examined it.

- **A. Examine it in both modes.** A name that ends in `.md` counts as Markdown, even when nothing comes before the dot.
  - **Pros:** it matches the scan and five of the six places in the code today; it is simple, since only the name's ending is tested; no Markdown file escapes a gate.
  - **Cons:** the hook starts judging a file it skips today; `.md` is a hidden file on Unix, and someone may not mean it as a document.
- **B. Skip it in both modes.** A file needs a name before `.md` to count as Markdown.
  - **Pros:** a hidden file stays outside the gates; it matches the hook today.
  - **Cons:** the scan stops examining a file it examines today, which loosens the check; it adds a rule beyond "Markdown means `.md`" in limit 7 of the shared-code page.

**Recommendation.** A, by the session: "Markdown means `.md`" is the rule the shared-code page already states, and a gate should not have a quiet exception for one file name.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R5.** Markdown means a name that ends in `.md`, in any case, a file named just `.md` included, in the hook and the scan alike. Both call the one function `repository.is_markdown`.

## 5. The shared-code page over its ceiling

The shared-code page, [kit-shared-gate-code](../../shared/GATE.md), grew from about 45,500 characters to about 50,900 with the first part of this change, and to about 55,700 by its end. Its ceiling `shared-code` is 49,000 at warning, so the length check reports a note and no finding.

- **A. Split along a seam the page already has, as the change's last step.** The long table of shared items, its section 5, moves to a document of its own, linked from the page, and the territory of [plc-0009-shared-code](../policies/plc-0009-shared-code.md) widens to hold it.
  - **Pros:** it is the fix the ceiling procedure names first; the page is back well under 49,000 with room to grow; the item table is the part only fixture authors read.
  - **Cons:** a structural change, which this record would have to rule; a new document to govern; every link to the items must move, which the mover of const-referencing repairs.
- **B. Raise the ceiling.** A new number by the rule of thumb, the longest document plus ten percent, about 57,000, with a new window of data.
  - **Pros:** one line in the dials file; no document moves.
  - **Cons:** the number then comes from the growth it should hold back, not from a window of data; the ceiling stops doing its job for this page.
- **C. Leave it at warning for now.** Decide after the change lands.
  - **Pros:** no work now; nothing is blocked.
  - **Cons:** the note repeats after every write; the decision is only postponed, and the next planned change touches the page too.

**Recommendation.** A, by the session, done after the last items of the change have added their lines, so the split happens once and is measured on the final page.

**Choice.** C, by the decider, in chat on 2026-10-03. This defers the choice between A and B. It is no ruling on the page's length, and this record does not decide it.

**R6.** The ceiling `shared-code` stays at 49,000 characters at warning, and the page stays over it, until the decider decides. This change does not alter the ceiling.

**R7.** A deferred choice, held pending by [step 9 of the rollout plan](../rollout-plan.md#s9): the decider will choose between splitting section 5 and raising the ceiling after this change lands. That decision is a later act, with its own record if it is a `process` ruling, and this record rules neither way.

## 6. What the change makes where no choice existed

These items carry no options. Each follows from the five answers above or from the kit's rules, and each stands open to the decider's override before the yes. The class of each shared part is the one [rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) asks for: K means the code implements a kernel section literally, R a gate-script rule of [template section 6](../../module-template/MODULE.md#t6).

**R8.** Two functions are shared, of class R, parts of the shared `messages` beside `shown`: `messages.escaped(value)`, new, and `messages.echoed(value)`. `escaped` shows a value's backslashes, line feeds and carriage returns escaped and never cuts it. `echoed` is `escaped(shown(value))`: it cuts a value as `shown` does, then escapes it. Both keep a BROKEN line on one line. All eleven modules need both. A message takes a value from a document, a dial, the envelope, the command line, the hook payload, the environment or a tool only through one of them. `escaped` is for a value the reader must open, copy or type into a fix, or that a later step reads: a repository path, an id or an anchor typed into a fix, the text of a dial that teaches, a tool's one-line diagnosis, a generator's output line. `echoed` is for a value that only points at something the reader can already see: a dial key, a pattern, a phrase, a command word, a match from a document, an event or tool name. A value is left alone only when the code or a check has fixed its shape before the message, when the system's own error text already escapes it, or when it stands inside a command the reader pastes. A pattern that checks an id is applied with `fullmatch`, so that no id ends in a line break.

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

## 7. Whether the echo rule is finished inside this change

The carry audit of this record ran four rounds of fixes on R8, and each round found the next site where a value was cut that a reader needs whole, or left raw where it can hold a line break. The cause was that R8 was written as a rule before anyone listed the sites where messages print outside values. The question was put on 2026-10-03.

- **A. Finish it inside this change.** One agent first lists every site in all eleven modules: where its value comes from, whether a later step needs it whole, whether it can hold a line break. Then a shared escape-only helper and one round of fixes made from that list.
  - **Pros:** R8 ends complete and true for every module; one round made from a full list should end the loop.
  - **Cons:** the change grows again before the yes; it touches findings in nearly every module, well beyond its first scope; more rounds of the carry audit.
- **B. Close this change on its own scope, and move the rest to a new item.** Fix only what the rounds broke, word R8 as exactly what the code holds, and log the sites that existed before the change as a new item that starts with the list.
  - **Pros:** it stops the loop now; the change lands what it set out to do; the remaining work starts from a list instead of a rule.
  - **Cons:** known line-break gaps stay in the code until the new item lands; R8 is narrower than "every value".

**Recommendation.** B, by the session: the remaining sites all existed before the change, so the change does not make them worse, and the new item should start from the list.

**Choice.** A, by the decider, in chat on 2026-10-03. The list was made: 224 sites, of which 144 differed from their target. Its ruling is R8.

## 8. How far the echo rule reaches

With the list made, the rule was put again. A first version, with three options, was too detailed; the decider asked for it in simple terms, and it was put again so:

- **A. Do all 144 sites now, inside this change.** Two helpers: one keeps a value on one line and never cuts it, for what the reader opens or copies; one keeps it on one line and cuts it, for what only points. Each site is given the right one, from the list. The cost: a large change that touches every module and many test lines before the yes.
- **B. Close this change small, and do the rest later as its own task.** Fix only what the change itself broke; the list makes the later task easy to do properly.

**Recommendation.** B, by the session, so that the change lands without growing further.

**Choice.** A, by the decider, in chat on 2026-10-03. Its ruling is R8. The session added two fixes of the same kind without asking and said so in chat, so that the decider could stop them: the id pattern applied whole, so that no id ends in a line break, and a generator's stem refused when it holds one. Both are in R8.

## Applied

The commits of this branch apply every item. R1 to R7 and R9 to R18 were applied by the commits before the one that adds this record. R8 was corrected in place before the yes, as the carry audit found the sites it missed, and was applied by the later commits of the branch, the four batches of the list among them. They change the shared code, the eleven modules, the shared-code page, the module documents, the install note and the style guides of styling. The shared-code page states each shared part with its class, in the rows of its section 1 and in the limits of its section 4. The Windows branch of `relative_path` and of task-close's backslash test is written and has not been run on Windows. So this record is born `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `dials` row of section 1 for the class and the callers; [section 2](../../shared/GATE.md#g2), item 4, for the call; [section 3](../../shared/GATE.md#g3), the row C5.10, for the text.
2. R2 — [`const-language`](../../modules/const-language/MODULE.md#t7), [`const-doc-budgets`](../../modules/const-doc-budgets/MODULE.md#t7) and [`const-styling`](../../modules/const-styling/MODULE.md#t7), each its dial `departures`.
3. R3 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 15 of section 4; [section 1](../../shared/GATE.md#g1), the `dials` row.
4. R4 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t7), its dial `coverage`; [kit-shared-gate-code](../../shared/GATE.md#g4), limit 15 of section 4.
5. R5 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 7 of section 4; [section 1](../../shared/GATE.md#g1), the `repository, territory` row.
6. R6 — [the dials file](../../constitution.yaml), the ceiling `shared-code` of `const-doc-budgets`.
7. R7 — pending: [step 9 of the rollout plan](../rollout-plan.md#s9), the decider's choice between a split and a raise; the ceiling itself is R6's.
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
