---
id: dec-0107-shared-test-files-in-the-distribution
type: task-record
title: The shared test files ship as the subpackage testing and hold for a gate of another layer
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shared test files ship as the subpackage testing and hold for a gate of another layer

## Context

A module proves the shared code through the shared acceptance items, which its tests run with the shared harness, consumer and marker. Those four files stood in `shared/tests/`, outside the distribution `constitution-layer-kit`, and each module of this kit reached them through four symbolic links. A module of another kit cannot link across repositories, so it got no harness and no items through pip, and a copy would drift from the items it must prove. The page of the shared code listed this as deferred, with the signal "another kit's first module needs them". The knowledge kit's inventory of 25 October 2026 names the change C2; its first module waits for it.

The files also held this kit's layout: one dials file, `constitution.yaml`, the prefix `const-`, and about a hundred hand-typed lines that named both. The same day, [dec-0106-two-dials-files-and-kernel-keys](dec-0106-two-dials-files-and-kernel-keys.md) let a gate of another layer read its own file beside the constitution's.

## 1. How the files ship

- **A. A subpackage, `constitution_layer_kit.testing`, in the one distribution.** pytest is an optional extra, `testing`.
  - **Pros:** the items always come at the release of the code they prove; one version, one tag, one build check; fewer links in every module.
  - **Cons:** every project's install carries about 215 KB of test code it never imports; the layout of `shared/` changes, and with it the link rules and their check; a change to the items now raises the version.
- **B. A second distribution, `constitution-layer-kit-testing`, from `shared/tests/`.**
  - **Pros:** a project that only runs gates installs no test code; `shared/tests/` stays where it is.
  - **Cons:** two versions to keep equal, and a check that they match; a second install line for the other kit to keep in step.

The session recommended A: the items exist to prove one release, and a subpackage cannot be paired with another. The decider chose A in chat on 2026-10-27.

<a id="r1"></a>**R1.** The shared test files are the subpackage `constitution_layer_kit.testing` of the distribution: `harness`, `consumer`, `acceptance` and `items`, the last the shared items that stood in `test_shared_items.py`, each importing the others relatively. No gate imports the subpackage, which review holds. pytest is the distribution's extra `testing`. R1 builds what R21 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r21) deferred, so that deferral ends. `scripts/check-shared-package.py` installs the wheel with that extra, since it imports every submodule.

<a id="r2"></a>**R2.** A module's `tests/` holds one link to the shared package, which holds the test files, beside its links to its own packages, and one plain file, `tests/test_shared_items.py`, which brings the shared items into its run with a star import from `constitution_layer_kit.testing.items`. Its own tests import from `constitution_layer_kit.testing`. `scripts/check-shared-links.py` owes no link to a shared test file, fails to run when the package or one of the four files of `testing/` is gone, and is red for a link of `tests/` into `shared/` that is not owed, its fix `git rm` of the link. This replaces R6 of [dec-0068-enforcement-tables-destination-classes-and-kit-checks-held](dec-0068-enforcement-tables-destination-classes-and-kit-checks-held.md#r6) and the links to the shared test files of R8 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r8). It narrows R2 of [dec-0073-packages-resolve-their-own-file](dec-0073-packages-resolve-their-own-file.md#r2), whose check now reads the test files with the package, and R4 of [dec-0061-ci-runs-one-job-per-module](dec-0061-ci-runs-one-job-per-module.md#r4), whose kit types now cover them with the package.

## 2. How far the files serve another layer

- **A. The harness and the numbering opened up, the items left as they are.**
  - **Pros:** small, and soon ready for the other kit's package.
  - **Cons:** no gate of another layer runs the shared items, so nothing proves that the shared code serves it; the other kit would copy the items.
- **B. Every shared item holds for a gate whose file, prefix and kernel keys differ.**
  - **Pros:** a module of another layer proves the shared code through its real entry point, from one source of the items.
  - **Cons:** about a hundred sites change; lines are built from the gate's file and prefix, not typed whole; a gate of another layer is needed here to prove it.

The session recommended B, which the inventory's need that each `know-` module runs the constitution package's items asks for. The decider chose B in chat on 2026-10-27.

<a id="r3"></a>**R3.** Every shared item holds for a gate of another layer as for one of this kit. The items read the gate's own dials file, its kernel keys and its prefix from the identity the session declares. A line about the gate's own file names that file. A line about the policies, a root policy or the constitution's kernel keys names the constitution's file, since such a gate reads its policies and resolves them in a scope of `reading` that file. The consumer writes the constitution's file, and the gate's own beside it, sending each key of a patch to the file it belongs in. The harness takes the gate's file, its kernel keys and the folders of its own kit's packages. Every module of this kit reads the same lines as before.

## 3. Where the proof for another layer lives

- **A. A kit check, `scripts/check-layered-items.py`, on a fixture gate under `scripts/layered-fixture/`.** It is an entry of the gate group, with a `--self-test`.
  - **Pros:** a standing proof on every pull request; a regression shows here, not in another repository.
  - **Cons:** the most work: a new check, its self-test and a gate-list entry; more minutes in CI.
- **B. A proof run once by hand in this change, the other kit's modules the standing proof after it.**
  - **Pros:** no new tooling.
  - **Cons:** a later change can break the items for other layers with nothing red here.

The session recommended A, since only a standing check keeps R3 true after this change. The decider chose A in chat on 2026-10-27.

<a id="r4"></a>**R4.** `scripts/check-layered-items.py` runs every shared item for `know-check`, a gate of another layer that reads `layer.yaml` with the kernel keys `module_prefix` and `layer_dialect` and the policies of `constitution.yaml`. It is red with pytest's output when an item fails. The gate is kit tooling under `scripts/layered-fixture/`, laid out as a module, never shipped, and no module of this kit. The check is an entry of the gate group in the job `kit`, and the types of the fixture an entry of the extra group.

## 4. What the version promise covers

No choice was open here: it follows from R1.

<a id="r5"></a>**R5.** The subpackage `testing` is part of the package and of the promise of [rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), since a module of another kit builds its `Subject` and its `Harness` from it. A change to it raises the version as a change to the gates' code does; a change to `shared/GATE.md` alone raises nothing.

## 5. What the portability check reads of the test files

The check that holds [law 2 of CLAUDE.md](../../CLAUDE.md#law-2) by grep, `scripts/check-portability.py`, reads all of `shared/constitution_layer_kit/` as installed code, so after R1 it read the test files too: 56 findings. About fifty were the consumer's fixture data, relative paths and the kit's document folders such as `docs/policies/**`. Four were comments citing this kit's policy, script and test files, and two a policy id made up for item S190; those six were rewritten whatever the choice.

- **A. Leave `testing/` out of the scan, held by review.**
  - **Pros:** the smallest change, one exclusion with its reason.
  - **Cons:** a later comment that cites a kit record or script ships with nothing red; [law 2 of CLAUDE.md](../../CLAUDE.md#law-2) for shipped code rests on review alone.
- **B. Read `testing/` with the relative-path and kit-folder forms switched off there.** The catalog-id and kit-name forms stay on.
  - **Pros:** a kit id, record or file name in the test files stays red; only the forms fixture data cannot avoid go quiet.
  - **Cons:** new code and self-test cases in the check; a kit path written as a plain relative path passes unseen there.
- **C. Read it in full, and build every fixture path at run time so that no string matches.**
  - **Pros:** no change to the check.
  - **Cons:** it hides the data from the check instead of telling the check what the data is; the hand-typed lines suffer.

The session recommended B, which keeps held what a grep can hold there. The decider chose B in chat on 2026-10-27.

<a id="r6"></a>**R6.** The portability check reads the files under `shared/constitution_layer_kit/testing/` with two forms switched off, the relative path and the kit's document folder, since the consumer the items build must be given paths. Every other form stays on there, and every form stays on for the rest of the shared code. A path or a document folder of the kit written as a plain relative path in the test files is held by review.

## Applied

The record was born `active`: its rulings were applied in the commits of the branch `work/shared-package-two-layers` while its last question was still open. It was set `inactive` by the commit that applied R6 to [requirement A12.1](../requirements.md#a12-1), the last of its homes.

## Carry list

1. R1 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `testing`, the paragraph of the delivery and that of the deferred parts; [testing](../../shared/constitution_layer_kit/testing/__init__.py), its docstring; [the distribution](../../shared/pyproject.toml), `optional-dependencies`.
2. R2 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 7, and [§5](../../shared/ITEMS.md#g5), K1; [CLAUDE.md](../guide/developing-a-module.md#s4), step 4 of "Developing a module"; [rule 14 of template §6](../../module-template/MODULE.md#t6). What it replaces and narrows is history.
3. R3 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `testing`, and [§2](../../shared/GATE.md#g2), item 8.
4. R4 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 8, and [§5](../../shared/ITEMS.md#g5), K2; [CLAUDE.md](../guide/gate-list-and-ci.md), the gate list and CI.
5. R5 — [rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11).
6. R6 — [requirement A12.1](../requirements.md#a12-1); [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `testing`; [the portability check](../../scripts/check-portability.py), its docstring.
