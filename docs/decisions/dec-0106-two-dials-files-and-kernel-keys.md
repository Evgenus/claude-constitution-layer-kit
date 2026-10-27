---
id: dec-0106-two-dials-files-and-kernel-keys
type: task-record
title: A gate names its file's kernel keys and reads the constitution part of a second file; the package becomes 2.0.0
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A gate names its file's kernel keys and reads the constitution part of a second file; the package becomes 2.0.0

## Context

A second kit, the knowledge kit, builds modules with the prefix `know-` on the constitution's kernel. Each of them keeps its own dials in its own file, `knowledge.yaml`, beside `constitution.yaml`. Rule NC2 of that kit's plan says that no key stands in both files. The policies that govern knowledge documents are the project's policies, so their territories stand under their ids in `constitution.yaml`, as [kernel §3](../../kernel/CONVENTIONS.md#k3) says.

The shared package read every key from the one file the identity names. A `know-` gate that read `knowledge.yaml` found no policies there. One that read `constitution.yaml` stopped with `C5.12`, because that file's prefix, `const-`, does not start a `know-` namespace. A plain value at the top of `knowledge.yaml`, a key of the knowledge kernel, was refused as `C5.4`. The page of the shared code listed the two-file read as deferred, with the signal "another kit's gate must resolve policies while its dials sit in its own file". The knowledge kit's inventory of 25 October 2026 names the change C1, and that signal has fired.

## 1. How a gate reads the second file

- **A. A field `Identity.constitution_file`.** The package reads both files and joins them whenever the field is set.
  - **Pros:** one declaration in the identity; a third layer gets the two-file read with no code of its own.
  - **Cons:** the package that knows nothing else of other layers would hold their rule of which key comes from which file.
- **B. A parameter on each `locate_*` function and a new reader.** The knowledge package passes the second file on every call.
  - **Pros:** the second file is visible at each call; the identity does not grow.
  - **Cons:** four public signatures grow; a call that forgets the parameter reads one file in silence and passes a document it should have checked.
- **C. The package reads `constitution.yaml` whenever the identity names another file.**
  - **Pros:** no new public name.
  - **Cons:** it changes what existing code does, against shared item S177; it builds a file name into a source that names none; a gate cannot keep to its own file.
- **D. A reader of the constitution part alone.** The knowledge package reads each file in a scope of its own and joins the two reads.
  - **Pros:** the smallest change here; the package stays unaware of layers; each part is read where its layer owns it; `C5.12` stays for every normal read.
  - **Cons:** the knowledge package writes and tests the join, and a third layer writes its own; the inner scope must keep the run's deadline.

The decider proposed D in chat on 2026-10-27: a gate reads both files under different declarations and does what it needs with each part. A test that day showed the reason it could not be done yet: a `know-` scope that names `constitution.yaml` stops with `C5.12`, and the only way past it is a made-up `const-` namespace. The session recommended D, which leaves each layer's rule in the package of its own kernel. The decider chose D in chat on 2026-10-27. The prefix stays a key of each file and does not move into the identity: in each file it tells module namespaces from policy namespaces (R12 and R13 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r12)).

<a id="r1"></a>**R1.** A scope of `identity.reading(dials_file, kernel_keys)`, opened inside the run's scope, shadows the name of the dials file and its kernel keys and nothing else. The identity's other fields, the mode and the hook's deadline stay those of the run, so a hook keeps its one deadline. Every message opened inside it names the file being read. Outside every scope, with a name that is empty or empty once stripped, or with a list without `module_prefix`, it is the caller's defect, a `RuntimeError` raised as it opens. This narrows R1 of [dec-0100-gate-declaration-scoped-to-one-guarded-run](dec-0100-gate-declaration-scoped-to-one-guarded-run.md#r1): the shared code still reads the file's name from the declared identity, which a scope of `reading` shadows.

<a id="r2"></a>**R2.** `dials.load_kernel_part(root)` reads the constitution part of the file the identity names: `root_policy`, `territory_dialect`, the file's own `module_prefix` and the policy namespaces. It holds the prefix to its form, else `C5.14`, whose fix names no prefix of the reader's, and never to the reading module's namespace. It reads no namespace of the reader's, and gives None where the file is absent. A gate of another layer calls it in a scope of `reading` the constitution's file with `KERNEL_KEYS`, so that the messages name the three keys it reads whatever the scope lists, and joins it to the read of its own file itself; what it does when the file is absent is that layer's to decide. This narrows R13 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r13) to the read of the gate's own file: the constitution part of another layer's file is read by this reader alone. R1 and R2 build what R11 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r11) deferred, so that deferral ends.

## 2. Which keys stand at the top of the gate's own file

- **A1. A field `kernel_keys` with the constitution's three as its default.**
  - **Pros:** additive, a release 1.1.0; no module of this kit changes.
  - **Cons:** a `know-` identity that forgets the list reads its file as the constitution's and accepts a stray `root_policy` in silence.
- **A2. A required field `kernel_keys`.**
  - **Pros:** every gate states what its file owns, as it states the file; forgetting is impossible.
  - **Cons:** a break of the promise of [rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), so a new major; every identity and every `REQUIRES` changes.
- **B. The knowledge kernel's keys under one mapping, `knowledge:`.**
  - **Pros:** no change here.
  - **Cons:** the knowledge package parses the file a second time with its own failure texts; a misspelt mapping key becomes a silent candidate policy; a stray `territory_dialect` passes.

The decider asked why the constitution kit itself does not load its dials the same way, and the answer made the list symmetric: the constitution's kernel keys are its layer's list, `KERNEL_KEYS`. The decider then asked whether release 1.0.0 could be amended with A2, since nothing outside used it yet. It could not: the installed 1.0.0 serves every session of this kit and the `const-` plugins the knowledge kit loads, pip keeps an installed version, and a module from an amended commit would meet the old code under the same number, which the version check cannot tell apart. The session recommended A1, since rule 11 makes a major the choice "only when nothing else serves" and the knowledge package can build every identity in one function. The decider chose A2 in chat on 2026-10-27. The session's objection stands as written here: A1 would have served. The case for A2 is that forgetting the list becomes impossible, which no function of another package can hold for every gate.

<a id="r3"></a>**R3.** `Identity` has a required field `kernel_keys`, with no default, right after `dials_file`: the top-level keys of that file that are no namespace. Every gate of this kit names `KERNEL_KEYS`, the constitution's three. A gate of another layer names its own file's list, and `module_prefix` stands in every list. A list without it is a defect of the entry point, a `RuntimeError` raised as the scope opens, which declares nothing.

<a id="r4"></a>**R4.** `load_dials` reads `root_policy`, and checks `territory_dialect`, only where the identity lists them. A constitution kernel key that the list leaves out is `C5.13`: a copy of it in the gate's own file would be ignored or contradict the one that counts. A key the list names beyond the constitution's three is passed over and handed on as YAML read it, in the new field `Dials.layer`, for its layer to validate. Any other top-level key that holds no mapping is `C5.4`, as before. `C4b` names the identity's own list where it is not `KERNEL_KEYS`.

<a id="r5"></a>**R5.** R3 breaks the version promise of [rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), so the package is 2.0.0. Every module's `REQUIRES` is 2.0.0, and every pip line names the tag `constitution-layer-kit-v2.0.0`, which is pushed only on the decider's go-ahead. A module requires the first release of the package's current major until it uses a name that a later release of that major added, and a new major raises every module's `REQUIRES` to its first release in the change that makes it. The release 1.0.0 is never amended: a release, once tagged, is never moved or made again.

## Applied

The rulings were applied in the commits of the branch `work/shared-package-two-layers` before this record was written: the shared code, every identity, entry file and install note of this kit, the shared items S177, S185 and S186, the new items S188 to S191, and the texts of the shared page and of the policy. The record is born `inactive`, every ruling having its home.

## Carry list

1. R1 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`; [identity](../../shared/constitution_layer_kit/identity.py), `reading`. That it narrows R1 of dec-0100-gate-declaration-scoped-to-one-guarded-run is history.
2. R2 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `dials`, and [§3](../../shared/GATE.md#g3), the row `C5.14`; [dials](../../shared/constitution_layer_kit/dials.py), `load_kernel_part`. That it narrows R13 and ends the deferral of R11 of dec-0099-shared-code-installed-as-a-pip-package is history.
3. R3 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`, and [§2](../../shared/GATE.md#g2), item 1; [identity](../../shared/constitution_layer_kit/identity.py), `Identity` and `declared`.
4. R4 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `dials`, and [§3](../../shared/GATE.md#g3), the rows `C4b`, `C5.4` and `C5.13`; [dials](../../shared/constitution_layer_kit/dials.py), `load_dials`; [model](../../shared/constitution_layer_kit/model.py), `Dials`.
5. R5 — [rule 11 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11); [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6, and [§4](../../shared/GATE.md#g4), limit 3. The push of its tag is the open step 10b of the rollout plan, which links this ruling.
