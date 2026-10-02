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

The record answers three questions, each put in chat on 2026-10-02 with lettered options, the pick a letter: which license, how its two files reach a project's kernel copy, and whether an installed module carries them.

## 1. Which license the kit takes

The decider stated two wishes: the credit is kept, and no profit is needed. So every option below requires attribution and allows commercial use. The options differ in how strong the credit is, and in how well they fit a tree that is part prose and part scripts.

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

**Recommendation.** B, by the session. The credit is the decider's main wish, and `NOTICE` is the one mechanism that carries a credit line of the author's own wording into every derivative. The duty to mark changes keeps the author's name off a changed copy. It stays one license for the whole tree.

**Choice.** B, by the decider, in chat on 2026-10-02. The decider picked the license. The session set the rest as defaults, each open to the decider's override before the yes: the wording of `NOTICE`, the `author` field in every manifest, and no license header in any file.

**R1.** The kit is under the Apache License, Version 2.0. It is one license for the whole tree, documents and code alike. Its text is `LICENSE` at the kit's root, and no file takes a license header.

**R2.** `NOTICE` at the kit's root carries the credit: the kit's name, the copyright line with the author's name, and the address of the kit's repository. It holds no email address.

**R3.** Every module's manifest, and the template's, names the license in `license` as `Apache-2.0`. Every module's manifest names the kit's author in `author`; the template keeps a placeholder there.

## 2. How the two files reach a project's kernel copy

A project copies the kit's kernel into its own repository, and a public repository passes that copy on. The license then asks for its text and for `NOTICE` beside the copy. The first draft of this change left that to a sentence in the install guide, a step the reader takes by hand; the carry audit's blind reader named the gap, and the decider asked whether the files should be part of the kernel.

- **A. A hand step.** The install guide tells a project in prose to keep both files beside its kernel copy.
  - **Pros:** nothing more to build.
  - **Cons:** a hand step is easy to skip, so most kernel copies would carry no credit.
- **B. The guide's copy command takes both files.** The block that copies the kernel also copies `LICENSE` and `NOTICE` from the kit's root, and the guide's check holds that they arrived.
  - **Pros:** every bootstrapped project carries the credit; one source for each file, at the root; the kernel is untouched; the kit's CI proves the copy on every change.
  - **Cons:** the check and its fixture change; the two files stand in the project's kernel territory with no envelope, which the gates accept and the guide must say.
- **C. Both files live in the kernel folder too.** Real copies beside the conventions page, carried by the copy command as it stands.
  - **Pros:** no change to the guide or its check; the kernel folder is whole wherever it travels.
  - **Cons:** the root copies must stay, since the forge reads the license there and it covers the modules too, so the text exists twice and needs an equality check; a link in place of a copy would arrive broken in the project; a kernel change runs the carry audit in full, and the kernel policy, which names the conventions page and its schemas, would need an amendment.

**Recommendation.** B, by the session: it gives what C gives without a second copy of the text and without widening what the kernel is.

**Choice.** B, by the decider, in chat on 2026-10-02.

**R4.** The block of the install guide that copies the kernel also copies the kit's `LICENSE` and `NOTICE` beside it, and the guide's check holds both there, byte for byte. The guide says that the two files cover the kernel copy alone and carry no envelope. It also says what the license asks: a project that passes the copy on to others keeps both files there, and says in each kernel file it changed that it changed it.

## 3. What the record leaves open, and what it reverses

**R5.** Whether the author's email stays in the history is not ruled here. It stays a decision of the plan's step 10, made before the repository is public.

**R6.** The license is decided by this record, ahead of the step that makes the repository public. This reverses one part of R1 of [dec-0057-pr-flow-merge-names-the-yes](dec-0057-pr-flow-merge-names-the-yes.md): that the license is decided at that step. The rest of that item stands.

## 4. Whether an installed module carries the two files

A module never lands in a project's repository: an install copies it into the plugin cache on the user's machine. So a project does not pass a module on, and the license asks nothing of it there. The credit a user sees is the manifest's, in the platform's plugin list.

- **A. The manifest alone.** Each module names the author and the license in its manifest; the two files stand at the kit's root alone.
  - **Pros:** nothing to build; whoever gets a module through the marketplace gets it from a clone that holds the root files.
  - **Cons:** a module's folder passed on alone carries neither file; whoever passes it on takes both from the root.
- **B. Each module links to the root files.** Two relative links in every module, as a module links the shared gate code.
  - **Pros:** one source; an install turns a link inside the marketplace into a real file, which the kit's CI already holds for every link of a module.
  - **Cons:** twenty-two links and the template's; the link check, its fixture and the shared-code document change; a folder copied by hand from a clone gets two dangling links.
- **C. Each module holds real copies.** Both files in every module, held equal to the root by a new check.
  - **Pros:** a module's folder is whole however it is copied.
  - **Cons:** the license text exists twelve times; a new check to build.

**Recommendation.** A, by the session: no module has been passed on alone, and the kit adds machinery only for a failure someone has hit. B is the candidate once one is.

**Choice.** A, by the decider, in chat on 2026-10-02.

**R7.** A module carries no license file. Its manifest names the license, and `LICENSE` and `NOTICE` stand at the kit's root alone; whoever passes a module's folder on alone takes both from there.

**R8.** Linking both files into each module is reopened as a decision once a module is mirrored or vendored outside the kit's marketplace.

## Applied

The change that creates this record applies R1 to R4, R7 and R8. It adds `LICENSE` and `NOTICE`, and sets the two fields in the eleven manifests and the license in the template's; the template's was set in a later commit of the change than the record's first. It adds the sentences to `CLAUDE.md`, to the install guide and to the module template. The guide's kernel block copies the two files, and `scripts/check-install-guide.py` holds them there, with a case of its `--self-test` for a copy that leaves them out. The text of `LICENSE` is the one GitHub's license API gives for `apache-2.0`. The README gains a section "License", a routine edit of a page in no territory. The plan's step 10 marks the license done. So the record is `inactive`.

## Carry list

1. R1 — step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the license](../../LICENSE).
2. R2 — [the credit file](../../NOTICE), for the three parts it holds; step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md), for the file's place and for no email address.
3. R3 — step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the template's manifest](../../module-template/.claude-plugin/plugin.json).
4. R4 — [the install guide](../../INSTALL.md#s2), step 4 of its bootstrap; [the guide's check](../../scripts/check-install-guide.py), its docstring at the name `kernel`.
5. R5 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the decision on the author's email.
6. R6 — history only: the reversal of when the license is decided, a one-time act; the license itself is R1's.
7. R7 — [the module template](../../module-template/MODULE.md), its section "Plugin skeleton"; [the install guide](../../INSTALL.md#s6), its last section, for a module's folder passed on alone.
8. R8 — [the module template](../../module-template/MODULE.md), its section "Plugin skeleton".
