---
id: dec-0063-apache-license-with-notice
type: task-record
title: The kit is under the Apache License 2.0, one license for the whole tree, with the credit in a NOTICE file
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit is under the Apache License 2.0, one license for the whole tree, with the credit in a NOTICE file

## Context

[Step 10 of the rollout plan](../rollout-plan.md#s10) makes the kit's repository public after the first consumer project's live proof. R1 of [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md) put two decisions at that step: the license, and whether the author's email stays in the history. The decider asked for the license ahead of it, in chat on 2026-10-02. Until this record the tree held no license file. Five module manifests and the template's manifest named `MIT`, a placeholder the template carried and no ruling chose; six manifests named no license and no author.

The decider stated two wishes in chat on 2026-10-02: the credit is kept, and no profit is needed. So every option below requires attribution and allows commercial use. The options differ in how strong the credit is, and in how well they fit a tree that is part prose and part scripts.

## Options

- **A. MIT.** A short permissive license: anyone may use, change and sell, and keeps the copyright line and the license text.
  - **Pros:** the most common license among Claude Code plugins; one short page; no duty beyond keeping the notice.
  - **Cons:** the credit is only the copyright line inside the license file; no duty to mark a changed file; no patent terms.
- **B. Apache License 2.0 with a `NOTICE` file.** A permissive license with a credit file: every copy passed on, and every derivative, carries the text of `NOTICE` and marks the files it changed.
  - **Pros:** the strongest credit among software licenses, in words the author writes; a changed copy cannot pass as the original; a patent grant; it fits code and prose alike.
  - **Cons:** a long text; a project that passes its kernel copy on must carry `NOTICE` along, so the install guide needs a sentence about it.
- **C. Creative Commons Attribution 4.0.** Every reuse names the author, links the source and says whether it was changed.
  - **Pros:** the most visible credit; made for prose, which is most of the kit.
  - **Cons:** Creative Commons advises against it for software; the scripts and hooks would stand under a license with no terms for source code; a manifest's license field expects a software license.
- **D. A split.** Apache License 2.0 for the code, Creative Commons Attribution 4.0 for the documents.
  - **Pros:** each part gets the license made for it.
  - **Cons:** two licenses to explain; the line between code and document is unclear for a skill and for a gate's message; a consumer must know which one applies to each file.

## Recommendation

B, recommended by the session. The credit is the decider's main wish, and `NOTICE` is the one mechanism that carries a credit line of the author's own wording into every derivative. The duty to mark changes keeps the author's name off a changed copy. It stays one license for the whole tree.

## Choice

B, by the decider, in chat on 2026-10-02. The decider picked the license. The session set the rest as defaults, each open to the decider's override before the yes: the wording of `NOTICE`, the `author` field in every manifest, no license header in any file, and the sentence in the install guide.

## Ruling

**R1.** The kit is under the Apache License, Version 2.0. It is one license for the whole tree, documents and code alike. Its text is `LICENSE` at the kit's root, and no file takes a license header.

**R2.** `NOTICE` at the kit's root carries the credit: the kit's name, the copyright line with the author's name, and the address of the kit's repository. It holds no email address.

**R3.** Every module's manifest, and the template's, names the license in `license` as `Apache-2.0`. Every module's manifest names the kit's author in `author`; the template keeps a placeholder there.

**R4.** The install guide tells a project what the license asks of its kernel copy. A project that passes the copy on to others keeps a copy of `LICENSE` and of `NOTICE` beside it, and says in each kernel file it changed that it changed it.

**R5.** Whether the author's email stays in the history is not ruled here. It stays a decision of the plan's step 10, made before the repository is public.

**R6.** The license is decided by this record, ahead of the step that makes the repository public. This reverses one part of R1 of [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md): that the license is decided at that step. The rest of that item stands.

## Applied

The change that creates this record applies R1 to R4: it adds `LICENSE` and `NOTICE`, sets the two fields in the eleven manifests and the license in the template's, and adds the sentences to `CLAUDE.md` and to the install guide. The text of `LICENSE` is the one GitHub's license API gives for `apache-2.0`. The README gains a section "License", a routine edit of a page in no territory. The plan's step 10 marks the license done. So the record is `inactive` from its first commit.

## Carry list

1. R1 — step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the license](../../LICENSE).
2. R2 — [the credit file](../../NOTICE), for the three parts it holds; step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md), for the file's place and for no email address.
3. R3 — step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the template's manifest](../../module-template/.claude-plugin/plugin.json).
4. R4 — [the install guide](../../INSTALL.md#s2), step 4 of its bootstrap.
5. R5 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the decision on the author's email.
6. R6 — history only: the reversal of when the license is decided, a one-time act; the license itself is R1's.
