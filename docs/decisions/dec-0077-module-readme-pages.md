---
id: dec-0077-module-readme-pages
type: task-record
title: Every module ships a README of the root README's kind, linked from the root README's module table
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Every module ships a README of the root README's kind, linked from the root README's module table

## Context

The module table of the root README linked each module to its anchor in the requirements document. Since the module specifications moved into the modules' own documents, that anchor is a one-line stub pointing at `MODULE.md`, a document of 40,000 to 90,000 characters written for the module's authors. A reader on GitHub who clicks a module in the kit's front page lands on a stub, then on an author's document. Each module's `INSTALL.md` is the consumer's procedure, not a description, and the install guide reads it so. Claude Code itself shows no README of a plugin: its plugin listing shows the manifest's `description`, and the manifest's `homepage` is a URL. So a page for a reader is for GitHub and for the kit's own pages, and nothing of the platform reads it. The decider asked in chat on 2026-10-08 for a user-facing page per module, and the question was what kind of page.

## Options

- **A. A landing page per module, of the root README's kind.** `README.md` beside `INSTALL.md`, user-facing and informational, in no policy's territory, with no envelope, binding nothing.
  - **Pros:**
    - **the page GitHub shows first** in a folder;
    - **a kind the kit already has**, so no policy and no envelope;
    - **a reader gets what the module gives**, why, how a session behaves with it, how it works and how to get it, in plain language, and the manifest's description as the first sentence keeps the two from differing.
  - **Cons:**
    - **a twelfth prose file per module**, held by the scans and by review rather than by a policy;
    - **the root README's table stops pointing** at the specification anchor, an exception to the citation rule of the kit guide.
- **B. A consumer-facing page, read by the portability check.** The same page written as an installed component: no name of the kit, no document of the kit, held by the kit's portability check as `INSTALL.md` is.
  - **Pros:** one rule for every file of a module's folder; the page could ship in an install unchanged.
  - **Cons:**
    - **the page could not name the kit**, its install guide or its marketplace, so its last section would have nothing to point at;
    - **the check would grow a read list** for a page that people read and no session runs.
- **C. Fold `INSTALL.md` into `README.md`.** One page per module, the description and the procedure together.
  - **Pros:** one file; nothing to drift between two.
  - **Cons:**
    - **the install note is an installed component** with rules of its own, read by the portability check and named by the install guide;
    - **a landing page** that opens with requirements and symbolic links is the page the decider wanted to replace.

## Recommendation

A, by the session: the kind exists and costs no policy, and it gives the reader on GitHub the right first page.

## Choice

A, chosen by the decider in chat on 2026-10-08, and narrowed there: user-facing, informational, non-authoritative, no envelope, no reference to the specification, the implementation told at a high level, one paragraph per tool.

## Ruling

<a id="r1"></a>**R1.** Every module ships `README.md` at its root beside `INSTALL.md`: a page of the root README's kind — user-facing, informational, in no policy's territory, with no envelope, binding nothing — in plain language for a reader whose first language is not English, each term defined where it is first used. It has five sections, each heading with its anchor `a1` to `a5`. The first, what it gives you, opens with the manifest's `description` copied as written, so that the two never differ. It then says in plain words what the module checks, refuses and brings. The second, why use it, is the problem in the user's own terms, and then how the module resolves it once installed. The third, how Claude behaves with it, is prose with one real message of the module in a `text` fence. The fourth, how it works, is one paragraph per tool the module ships — each hook by its event, the scan, each skill, each command — saying what the tool reads, what it decides, what it cannot see, and that the defaults work with no configuration, the dials named in words. The fifth, get it, is the install line for one session and the marketplace form, the module's own scan command, and one closing line linking the module's `INSTALL.md` and `MODULE.md`. The page restates no requirement row, cites no row number, no decision and no error-code handle. It links nothing of the kit beyond those two files. Every list and table row carries a handle. A change to the page is routine, as a change to the root README is.

<a id="r2"></a>**R2.** The module template carries `README.md` with the five sections as placeholders, each saying what goes there. The page links only inside its own folder, so a copy keeps its links. Its plugin skeleton lists the file, and step 4 of "Developing a module" in the kit guide names it beside `INSTALL.md`.

<a id="r3"></a>**R3.** The module table of the root README links each module to its `README.md`, the landing page: a third exception of the kit guide's reference bullet, beside the two it already holds for a kit template and a frozen comparison. Outside these three places and module prose, and in chat, the specification anchor stays the citation and the module's handle. The kit's module-links check reads no page under `modules/`, which is module prose.

<a id="r4"></a>**R4.** The pages stand under a ceiling of the length gate, `module-readmes` over `modules/*/README.md`, at warning, set from the pages' own days as the longest page plus 10 %, rounded up to 1,000, with those days as its window, like the install guide's ceiling before it.

<a id="r5"></a>**R5.** A module's `README.md` is reader prose like `MODULE.md`: outside the read list of the kit's portability check, which reads a module's installed components, and its docstring says so, held by a self-test case. The portability rule, [law 2 of CLAUDE.md](../../CLAUDE.md#law-2), holds for the page by review, and the guide's step 4 says so. A module's `README.md` is never the home of a ruling: the record policy's carry rule and the kit's carry-list check refuse it, as they refuse the root README, and the carry-audit skill's readers count it as no home.

<a id="r6"></a>**R6.** R3 narrows three earlier rulings, which stand as written:

- **R7 and R11 of [dec-0005-reference-forms](dec-0005-reference-forms.md#r7)**, that kit documents link a module to its specification anchor;
- **R1 of [dec-0049-module-links-held-by-a-kit-check](dec-0049-module-links-held-by-a-kit-check.md#r1)**, two places excepted, now three;
- **and R1 of [dec-0051-module-citation-rule-in-the-guide](dec-0051-module-citation-rule-in-the-guide.md#r1)**, the two exceptions in the reference bullet, now three.

## Applied

The change that adds this record applies every item: the eleven pages, the template's page and the line in its plugin skeleton, the table and the map row of the root README, the two clauses of the kit guide, the ceiling, the docstrings and the cases of the portability and module-links checks, and, from the carry audit's fixes, rule 2 of the record policy, the carry-audit skill's list of places, and the carry-list check's refusal with its docstring and cases. Every module is a draft at `0.0.x`, so no version moves. The record grew while its change was made and was born `active`. The carry audit's fixes applied the last of it. It is `inactive` from that commit.

## Carry list

1. R1 — [the template's page](../../module-template/README.md), its note and its five sections; [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module".
2. R2 — [the template's page](../../module-template/README.md), its note; [the template's module document](../../module-template/slot-guidance.md#s1), its plugin skeleton; [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module".
3. R3 — [the reference bullet of CLAUDE.md](../../CLAUDE.md#references); [the module-links check](../../scripts/check-module-links.py), its docstring.
4. R4 — [the dials file](../../constitution.yaml), the ceiling `module-readmes` of `const-doc-budgets`.
5. R5 — [the portability check](../../scripts/check-portability.py), its docstring and its self-test; [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module"; [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r2), rule 2; [the carry-list check](../../scripts/check-carry-lists.py), its docstring and its self-test; [the carry-audit skill](../../.claude/skills/carry-audit/SKILL.md), its prompt A.
6. R6 — history only: the narrowing of earlier rulings, which stand as written.
