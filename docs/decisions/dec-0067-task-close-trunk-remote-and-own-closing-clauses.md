---
id: dec-0067-task-close-trunk-remote-and-own-closing-clauses
type: task-record
title: The task-close scan finds its trunk on a named remote at the fresher tip and reads trailers past signatures and old gits; every gate that is no write gate names and tests its own closing clause
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The task-close scan finds its trunk on a named remote at the fresher tip and reads trailers past signatures and old gits; every gate that is no write gate names and tests its own closing clause

## Context

An audit of the kit's hardcoded logic on 2026-10-02 found these gaps in [`const-task-close`](../requirements.md#const-task-close), each probed again on the trunk on 2026-10-06:

- **The trunk's remote.** A bare scan finds the trunk as a local branch or as `origin/<trunk>`. The name `origin` is fixed in code, so a fork whose real project is the remote `upstream` stops with a configuration failure whose fix names a dial that cannot help.
- **A stale local trunk.** When the local trunk exists, it wins, even when it is behind `origin/<trunk>`. A branch cut from the fresher tip then gets a red for commits other people landed. R5 of [dec-0036-task-close-module-rulings](dec-0036-task-close-module-rulings.md#r5) ruled the lookup and listed this as a con: "only more paths examined". The probe shows a false red.
- **Signature lines.** With `log.showSignature=true`, git prints the signature check before each line the trailer read parses, and a commit's label in a note or a red spans two lines.
- **An old git.** A git that does not know an option of the trailer read prints the placeholder as text. The scan then blames every commit for a declaration it never wrote.
- **The closing clause.** Every install-failure line of the gate ends "until then Markdown writes pass unchecked", while the gate checks the tree at a turn's end and a change's documents. The shared rule in [GATE.md §2](../../shared/GATE.md#g2) told a gate with a hook mode to keep that default, and the rule was already broken by the shell gate of [`const-interaction`](../requirements.md#const-interaction).

The audit also found that item 36 of the module's runner wrote a ref file by hand and crashed under the reftable ref store. It found that const-interaction's document writes out none of its two gates' own clauses.

The change this record rules is on one branch. Every module it touches is a draft, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)), and no shared code changes. The decider kept the audit's recommended fix for the remote, the stale trunk, the signature lines, the old git and the clause when reading the change's plan on 2026-10-06; sections 3 to 5 hold them as the audit argued them. Six questions were put to the decider in chat that day, one per message, each with lettered options and one recommendation, the pick a letter; sections 1, 2 and 6 to 9 hold them. Section 10 holds what the change makes where no choice existed.

## 1. One record for the change

The change has `process` stakes: it adds a dial a consumer types, reverses part of a recorded ruling, and changes a shared rule every gate's author follows. The question was how to cut the record.

- **A. One record for all of the change**, one carry audit, one yes on one pull request.
  - **Pros:** one record and one audit, the least work; the two topics meet in one module document, so one carry list covers both; a record for several topics has been written before.
  - **Cons:** the record holds two topics that are not related; reversing one later supersedes the record in part.
- **B. Two records, one pull request**: one for the trunk, one for the shared rule.
  - **Pros:** each record is one topic, easy to cite and to supersede.
  - **Cons:** two records and two carry lists; one more full reader and a second blind pass; about one more hour.
- **C. The trunk recorded; the shared rule routine**, treated as text brought to the tree.
  - **Pros:** a smaller record and audit; the new rule describes what the tree already does in part.
  - **Cons:** it changes a rule every module's author follows with no recorded yes; a reader of GATE.md cannot find why the rule changed; the session would price down a `process` call on its own.

The session recommended A: the two topics touch one module and one documents step, and one record with separate sections is still easy to cite by handle. The decider chose A in chat on 2026-10-06.

<a id="r1"></a>**R1.** One record holds the change's rulings. History only: it rules how this change was recorded.

## 2. Whether the stale-trunk fix goes first

The stale-trunk fix needs no new dial and hits plain `origin` setups, so it could have landed first, alone.

- **A. In the one change**, with the remote's dial.
  - **Pros:** one record, one audit, one merge, as section 1 chose; the two fixes change one function and are written and reviewed once.
  - **Cons:** the fix waits for the whole change; a stall elsewhere keeps the false red longer.
- **B. First alone**, its own pull request and record, the rest after.
  - **Pros:** the false red leaves the trunk within hours; a small change is easy to review.
  - **Cons:** two records and two carry audits; about 6 to 8 more agent runs and 2 to 3 more hours; the function is changed twice.

The session recommended A: the kit itself does not hit the case — every branch is cut after a pull of the trunk, and CI has no local trunk — and no consumer exists yet. The decider chose A in chat on 2026-10-06.

<a id="r2"></a>**R2.** The stale-trunk fix lands in the same change as the remote's dial. History only.

## 3. Where the scan finds the trunk

The audit argued four ways to let a bare scan find a trunk on a remote that is not `origin`.

- **A. A dial `trunk_remote`, default `origin`.**
  - **Pros:** explicit; it reads only the module's own namespace; one line fixes a fork; the default keeps every setup working.
  - **Cons:** a seventh dial; a `process` change.
- **B. Let `trunk` take a remote form, `upstream/main`.**
  - **Pros:** no new dial.
  - **Cons:** a branch name can hold a slash, so the value is ambiguous; the on-trunk test must strip the remote; a reader cannot tell which lookup won.
- **C. Search every remote**; one match wins, several fail.
  - **Pros:** no dial in the common case.
  - **Cons:** a fork has both `origin/main` and `upstream/main`, the very case to fix, so it needs a dial anyway; it is a guess, like the chain dec-0036 turned down.
- **D. Keep the code; fix only the message**, teaching `--since <remote>/<trunk>`.
  - **Pros:** routine; no new dial.
  - **Cons:** forks and other CI keep failing on the bare scan; the stale-trunk red stays.

The audit recommended A, with the fresher tip taken when both refs exist. The decider kept A when reading the change's plan on 2026-10-06.

<a id="r3"></a>**R3.** A dial `trunk_remote`, default `origin`, names the remote whose `<remote>/<trunk>` the scan looks up. It accepts a non-empty string with no white space and no control character — C0, DEL, C1 — that does not begin with a dash, kept as written, a slash included, since git allows one in a remote's name. Anything else is a configuration failure at every entry point, the hook included. Whether git knows the remote is learned at the lookup.

<a id="r4"></a>**R4.** The trunk is the local branch `<trunk>` or `<remote>/<trunk>`. When only one exists, it is the trunk. When both exist, the tracked one is the trunk if the local one is its ancestor or equal to it; otherwise — the local one ahead, the two split, or an ancestry question git cannot answer — the local one. A head that is the trunk examines its last landed change: the branch of that name, or a detached HEAD equal to either tip. This reverses in part R5 of [dec-0036-task-close-module-rulings](dec-0036-task-close-module-rulings.md#r5), its lookup "as a local branch, then as `origin/<trunk>`", and corrects its con "only more paths examined", which the audit's probe showed to be a red for another person's commit.

<a id="r5"></a>**R5.** When the trunk is found nowhere, the configuration failure names `<remote>/<trunk>` and teaches `git fetch <remote> <trunk>`, both dials and `--since`. The values inside the fetch command are printed whole through `escaped`, since the reader types them, and the values that only point are cut through `echoed`, as R8 of [dec-0064-shared-gate-defects-one-refusal-one-path-rule](dec-0064-shared-gate-defects-one-refusal-one-path-rule.md#r8) asks.

## 4. An old git: detect or declare

The trailer read and the ref check use git options of uncertain age. The audit could not verify their release history and argued two ways.

- **A. Detect, do not declare.** A literal placeholder in the output is a configuration failure naming git; a ref that begins with a dash is refused before git runs, so the option that guarded it is dropped.
  - **Pros:** no version table enters the code, so nothing unverified does; the failure names the real fix.
  - **Cons:** it reacts to one known symptom, not to every way an old git may differ.
- **B. Declare a floor** in the install note and check `git version` at start.
  - **Pros:** one clear requirement.
  - **Cons:** it needs release facts no one verified; a version check belongs in shared code, which bumps every module that links it.

The audit recommended A. The decider kept it when reading the change's plan on 2026-10-06.

<a id="r6"></a>**R6.** An old git is detected, never declared. A commit whose trailer field comes back beginning with the literal `%(trailers` is a configuration failure that names git's own version line and the fix "install a newer git"; when `git version` itself fails, its first line stands in that place. No version floor is stated or checked. The guard reads the start of a commit's whole trailer field, so a reason that quotes the placeholder further in, or a later declaration of the same commit that begins with it, is read as before, while a commit whose first declaration begins with it gets the same failure. A ref that begins with a dash is refused before git is asked, with the unknown-ref failure and the detail "a ref cannot begin with a dash"; `--since -x` written as two words is the command line's own misinvocation.

## 5. The gate's closing clause

The audit argued four ways to treat the clause that ends the gate's install-failure lines.

- **A. The module's own clause, and the shared rule widened** to say what the failure leaves unchecked.
  - **Pros:** true words for every consumer; the shared rule matches the tree again, the shell gate included; a fixture holds it.
  - **Cons:** a `process` record and a carry audit for a short wording fix.
- **B. The module's own clause only**, the shared rule unchanged.
  - **Pros:** routine; one module.
  - **Cons:** the module then breaks the shared rule as written; the next author copies the wrong default again.
- **C. Keep it**, the module's limit explaining the words.
  - **Pros:** no work; the fix half of each line is already right.
  - **Cons:** the line names the wrong risk where it matters most, a CI job that cannot run; a limit is used for what the gate can do.
- **D. Also a count line of the module's own.**
  - **Pros:** the unit would match the scan's.
  - **Cons:** the count line is printed by the shared guard for every gate, so it widens shared code and bumps every linked module; "0 documents examined" still truly says nothing was examined.

The audit recommended A without D. The decider kept it when reading the change's plan on 2026-10-06.

<a id="r7"></a>**R7.** const-task-close names its own `until_installed` clause in its identity, and its entry files carry the same clause in `C1`, `C14` and `C15`; `until_fixed` stays the shared default, "until it is fixed this check does not run", true for this gate. The count line every configuration failure ends with, "0 documents examined", stays the shared one and is read as nothing examined.

## 6. The shared rule

The rule of [GATE.md §2](../../shared/GATE.md#g2) said the default clauses are a gate's, so a gate with a hook mode never names them, and only a scan alone names its own. The question was how to rewrite it.

- **A. A rule by what passes, the document only.** The default fits a gate whose hook runs on a Markdown write; any other gate names its own clause, carries it in its entry files and writes it out in its module's document.
  - **Pros:** every gate complies once the change lands; the rule states the real test, so a new kind of hook needs no exception; no shared code.
  - **Cons:** GATE.md, over its ceiling, grows a little; nothing checks a new gate's clause.
- **B. A, plus a fixture**: a gate with its own clause has an item of its runner that holds the clause in `C2` and in its entry files.
  - **Pros:** every such clause is held by a test; a later drift turns red.
  - **Cons:** const-styling has no such item, so the change grows by a piece in a third module; a duty added to the shared interface for wording.
- **C. No default**: every gate names its own clause, the write gates included.
  - **Pros:** no default can be wrong for a new kind of gate.
  - **Cons:** shared code and seven more modules change; the write gates gain nothing; the largest growth.

The session recommended A: it fixes the rule's error with a document edit, and a fixture for every clause could come as its own item. The decider chose B in chat on 2026-10-06.

<a id="r8"></a>**R8.** The default closing clauses fit a gate whose hook runs on a Markdown write, before it or after it; `until_fixed`'s default fits every gate. Any other gate — a scan alone, a hook on the shell, a hook at a turn's end — names `until_installed` with what its failure leaves unchecked. Its entry files carry the same clause in `C1`, `C14` and `C15`, its module's document writes the clause out, and an item of its runner holds it in `C2` and in the entry files. Generators and session-start printers keep their own rules.

<a id="r9"></a>**R9.** const-styling's clause, `until then no document is scanned for style`, is held by an item of its runner.

## 7. The clause's words

The clause tells a reader what is at risk while the fix waits. The gate checks the tree at a turn's end and a change's documents.

- **A. `until then no turn end and no change is checked`.**
  - **Pros:** short; true in both modes; it claims nothing "passes", which in CI would be false.
  - **Cons:** "checked" for what is left unsaid; it reads oddly.
- **B. `until then turn ends and changes pass unchecked`.**
  - **Pros:** the shape of the default and of the shell gate's clause.
  - **Cons:** false in CI, where the job fails; it does not say what goes unchecked.
- **C. `until then neither the tree at turn end nor a change's documents are checked`.**
  - **Pros:** a CI maintainer reads that the documents rule is off; a session user reads that the turn-end check is off; true in every mode.
  - **Cons:** four words longer; a shape unlike the other clauses.

The session recommended C: the clause is the only part of the line that says what is at risk, and only C names the documents. The decider chose C in chat on 2026-10-06.

<a id="r10"></a>**R10.** const-task-close's clause is `until then neither the tree at turn end nor a change's documents are checked`.

## 8. const-interaction's clauses

const-interaction's code already prints its two gates' own clauses, while its document writes out neither.

- **A. Leave it logged**, outside this change.
  - **Pros:** the change stays in one module; a document over its ceiling does not grow.
  - **Cons:** the rule this change rewrites is broken by a sibling the day it lands; the next author copies the gap.
- **B. Fold it in, the document only.**
  - **Pros:** the new rule holds across the tree; no new piece, about half an hour.
  - **Cons:** the carry audit reads more records; about 150 more characters in a document over its ceiling.
- **C. Fold it in, with a test** that pins both clauses in the identities and the entry files.
  - **Pros:** a later edit to a clause turns a fixture red; the same proof as const-task-close gets.
  - **Cons:** one more piece in a second module's runner; it guards wording no rule then asked to be tested.

The session recommended B: two clauses written out are the whole gap found, and a test can come if a clause ever drifts. The decider chose C in chat on 2026-10-06.

<a id="r11"></a>**R11.** const-interaction's document writes out its two gates' clauses — the shell gate's `until then shell commands pass unchecked`, the list check's `until then no list is scanned` — and an item of its runner holds both.

## 9. The kit's carry-list check

The kit's `scripts/check-carry-lists.py` reads the `Accepted:` and `Carry-Audit:` trailers with the same form of `git log`, so it has both exposures of section 4 and of the signature lines. It is kit tooling, never shipped.

- **A. Log it for later**, with its signal: a maintainer whose machine verifies signatures.
  - **Pros:** no growth; it follows the kit's rule against machinery for failures no one has hit.
  - **Cons:** the check that gates every recorded merge keeps a known false red; the same fix later needs its own branch.
- **B. Fold it in, routine**: the signature lines kept out, the literal placeholder named, a case of its self-test for each.
  - **Pros:** one pattern fixed everywhere it stands; small, about 45 minutes; no growth of the record's audit.
  - **Cons:** a third growth of the change; it guards a failure no one here hits today.

The session recommended A: no one is hit today, and the change had grown twice. The decider chose B in chat on 2026-10-06.

<a id="r12"></a>**R12.** The kit's carry-list check reads acceptances without signature lines and stops, naming git's version line, when a field of an acceptance comes back beginning with the literal placeholder. History only: kit tooling at routine stakes, its behaviour stated in the script itself; it rules nothing a document carries.

## 10. What the change makes where no choice existed

<a id="r13"></a>**R13.** The trailer read asks git without signature lines.

<a id="r14"></a>**R14.** Item 36 of const-task-close's runner holds a broken HEAD in each ref store: a zeroed ref file in a repository of the files store, and a ref to a commit whose object is gone in one of the reftable store. Each half checks the store it runs in, which needs git 2.45 or newer to run the fixtures; on an older git the half is red and the runner goes on.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests and the documents; the message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The commit that adds this record adds const-task-close's row for it in its section 4. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded.
2. R2 — history only: how this change was landed.
3. R3 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t7), the row `trunk_remote` of section 7; [its section 6](../../modules/const-task-close/MODULE.md#t6), the C5 row; [its install note](../../modules/const-task-close/INSTALL.md), the dials example; the kit's own `const-task-close` block of `constitution.yaml`.
4. R4 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t7), the row `trunk` of section 7; [its close skill](../../modules/const-task-close/skills/close-task/SKILL.md), its first step. The reversal in part of R5 of dec-0036-task-close-module-rulings is history.
5. R5 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t6), the C12 row and the paragraph on error messages of section 6.
6. R6 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t6), the C12 row of section 6; [its section 9](../../modules/const-task-close/MODULE.md#t9), limit 13.
7. R7 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t6), the row `C1, C2, C14, C15` and the two entry-file rows of section 6; [its section 9](../../modules/const-task-close/MODULE.md#t9), limit 12; [its section 10](../../modules/const-task-close/MODULE.md#t10), the row of item 40.
8. R8 — [GATE.md §2](../../shared/GATE.md#g2), items 1 and 6; [GATE.md §3](../../shared/GATE.md#g3), the `C1`, `C2`, `C14` and `C15` rows.
9. R9 — [`const-styling`](../../modules/const-styling/MODULE.md#t6), its row `C1, C2, C14, C15` of section 6; [its section 10](../../modules/const-styling/MODULE.md#t10), the row of item 20.
10. R10 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t6), the row `C1, C2, C14, C15` of section 6.
11. R11 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t6), its row `C1, C2, C14, C15` of section 6; [its section 10](../../modules/const-interaction/MODULE.md#t10), the row of item 42.
12. R12 — history only: kit tooling, stated in the script itself.
13. R13 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t6), the package row of section 6.
14. R14 — [`const-task-close`](../../modules/const-task-close/MODULE.md#t10), the row of items 36 and 37 of section 10.
