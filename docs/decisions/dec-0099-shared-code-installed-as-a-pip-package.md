---
id: dec-0099-shared-code-installed-as-a-pip-package
type: task-record
title: Every module imports the shared code as the pip package constitution-layer-kit, pinned by a git tag and checked by version, and the tests keep their links
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Every module imports the shared code as the pip package constitution-layer-kit, pinned by a git tag and checked by version, and the tests keep their links

## Context

The code every gate shares has one source, `shared/constitution_layer_kit/`. Until this record, a module reached it only through relative symbolic links: `plugin/scripts/constitution_layer_kit` for its gates and `tests/constitution_layer_kit` for its fixtures (item 2 of the Ruling of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md), R1 of [dec-0096-shared-package-named-constitution-layer-kit](dec-0096-shared-package-named-constitution-layer-kit.md#r1), item 11 of R4 of [dec-0098-modules-install-from-a-plugin-subfolder](dec-0098-modules-install-from-a-plugin-subfolder.md#r4)). An install copies the target of a link only when the target lies in the same marketplace (limit 3 of [kit-shared-gate-code §4](../../shared/GATE.md#g4)). So a module of another repository could not reach this code. [§1 of that page](../../shared/GATE.md#g1) kept delivery through a package index deferred, with the signal "a reader of this code outside plugins appears".

The decider plans such a reader: a separate kit with modules of its own, built on the constitution kernel, with a dials file of its own. Two names in the shared code belonged to this kit alone: `DIALS_FILE = "constitution.yaml"` in `model.py` and `MODULE_PREFIX = "const-"` in `dials.py`.

Facts read on 2026-10-21 and 2026-10-22 with pip 24.0 and Python 3.12.4: a copy of `shared/` with a `pyproject.toml` installed from a `git+file:` URL pinned to a tag, from a wheel through `--find-links`, and from a local path. An install from source fetches the build tool, `setuptools`, from the package index: with `--no-index` it failed, and the developer's Python had no `setuptools` of its own. A folder named by a `.pth` file in a virtual environment was imported with no build and no network. pip's parser accepts the line `constitution-layer-kit @ git+https://…@<tag>#subdirectory=shared` and refuses the same form with a `git+file:` URL. The kit's repository stays private until [step 10 of the rollout plan](../rollout-plan.md#s10).

The session put the questions to the decider one per message, in chat on 2026-10-21 and 2026-10-22. Sections 1 to 8 hold them in order, and section 9 holds one that the change's documents raised.

## 1. The channel

How a project's `python3` gets the package.

- **A. A git URL pinned to a tag.** `python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@<tag>#subdirectory=shared"`.
  - **Pros:** the command names one exact version, the same on every machine; CI needs only a tag; git reads the private repository with the person's own credentials, as the plugin install does; the command stays the same once the repository is public.
  - **Cons:** pip takes no range here, so the module's own check holds it; each release is a tag pushed to GitHub, an outward act that needs the decider's go-ahead; pip builds from source on every install; another project's CI needs a token while the repository is private.
- **B. Wheels found by `--find-links`, from a folder or a GitHub release.** CI builds a wheel on a release tag and attaches it to the release.
  - **Pros:** pip resolves a version range; nothing is built at install time; the command has the form a package index would use.
  - **Cons:** a release workflow with write access; each release needs the decider's go-ahead; while the repository is private, pip cannot read a release's files, so a project first downloads them with a token.
- **C. A local path from the kit's clone.** `python3 -m pip install <the kit's clone>/shared`.
  - **Pros:** no tag, no release, no token beyond the clone the install guide asks for; the guide's check would install the change's own code with no extra step.
  - **Cons:** the version is whatever the clone has checked out, and nothing in the command names it; another project's CI checks out this kit too.
- **D. Keep the links, and the other project keeps a copy.**
  - **Pros:** nothing changes here; a project installs nothing more.
  - **Cons:** two copies drift, with a sync script and an equality check in the other project; it does not deliver the code through pip.
- **E. The package index PyPI, under the name R1 of [dec-0096-shared-package-named-constitution-layer-kit](dec-0096-shared-package-named-constitution-layer-kit.md#r1) reserved.**
  - **Pros:** the standard path; pip resolves ranges; no credentials and no clone.
  - **Cons:** it makes the code public while the repository is private, ahead of the decision step 10 keeps for that; each release is an outward act with an index account and a token; a published version can be withdrawn but never replaced.

The session recommended A: one command names the exact version, the kit needs no release machinery, and moving to E later changes only the command. The decider chose A in chat on 2026-10-21, and added three requirements: PyYAML becomes a dependency of the package; each module checks a minimal version; the shared code stays backward compatible from its first release, or the session proposes a reasonable behaviour. The session proposed the behaviour of R3 and the tag's form of R1. On 2026-10-22 the decider put the version check into the shared code, as one function that every module calls right after it imports `cli` and that checks both boundaries. The rest of the proposal stood.

<a id="r1"></a>**R1.** A project's `python3` gets the shared code as the Python distribution `constitution-layer-kit`, which pip installs from the kit's GitHub repository by a git URL pinned to a release tag: `python3 -m pip install "git+https://github.com/Evgenus/claude-constitution-layer-kit@constitution-layer-kit-v<version>#subdirectory=shared"`. The tag's form is `constitution-layer-kit-v<version>`, so that it never clashes with a module's version.

<a id="r2"></a>**R2.** `shared/pyproject.toml` describes the distribution, built by `setuptools`: its name; its version, read from `__version__` in `shared/constitution_layer_kit/__init__.py`, the version's one source; `requires-python` at the floor `FLOOR` of `preflight.py` names; one dependency, `PyYAML>=6.0`; one package, `constitution_layer_kit`, with a `py.typed` marker. `scripts/check-copies.py` holds the floor in `requires-python` with the other copies of `FLOOR`.

<a id="r3"></a>**R3.** The distribution follows semantic versioning, major.minor.patch, from its first release, `1.0.0`. Before that tag nothing is promised. From it on, a release keeps every module written for an earlier release of the same major working, because it only adds: a module, a function, an optional parameter or field whose default keeps the behaviour, a message key. A message's wording may change; its key and its parameters may not. A name that starts with `_` is no part of the promise. A change that breaks the promise is a new major, and a `process` decision of its own, made only when nothing else serves.

<a id="r4"></a>**R4.** A release is the tag `constitution-layer-kit-v<version>` on a commit of `main` whose `__version__` is that version. It is pushed only on the decider's go-ahead, since a tag is an outward act. A change to `shared/constitution_layer_kit/` or `shared/pyproject.toml` after a release raises `__version__` in the same change, by R3: the minor number for an addition, the patch number for any other. It does not when the version already stands above the last tag. Review holds the raise.

<a id="r5"></a>**R5.** Each Python entry file of a module states the version its module requires. Right after it imports `cli`, before it builds anything else, it calls one function of the shared code with its namespace, that version, the path of its install note and its closing clause. The function exists from the first release on, and its signature never changes. It returns nothing when the installed package serves the module, and otherwise one `BROKEN` line, which the entry file prints with its closing line before it exits 1, as for `C15`. The line is `C16` when the installed version is below the one required: the shared code is too old. It is `C17` when the required major is below the installed major: the module is too old for that major.

<a id="r6"></a>**R6.** A module of this kit requires `1.0.0` until it uses a name that a later release added. The change that makes it use such a name raises the version it requires to that release; review holds the raise. `scripts/check-copies.py` holds every required version at or below `__version__`, in the same major.

## 2. Where this kit's own modules get the code

- **A. Each plugin imports the package, and only the tests link to the working tree.** `plugin/scripts/constitution_layer_kit` is removed; the links in `tests/` stay.
  - **Pros:** every project gets the code one way; the version check guards every module for real; the kit's own sessions keep working gates while the working tree's shared code is broken in the middle of a change; fixtures and CI still test modules and shared code of one commit together; it matches the decider's stated intent of 2026-10-12.
  - **Cons:** every project runs one more pip command before any gate works; a module in the working tree that needs a name not yet released fails in the kit's own sessions until a release is installed; CI installs the change's own package before the install, session and guide checks, and the eval container does too; the first tag must exist right after the merge; [law 3 of CLAUDE.md](../../CLAUDE.md#law-3), the link and install checks, `C15` and every entry file change.
- **B. Each plugin keeps its link and carries the shared code, and the package serves only another kit's modules.**
  - **Pros:** projects install nothing new; the install, session and eval checks stay as they are; a module always runs the shared code of its own commit.
  - **Cons:** two ways to deliver the code; the kit's sessions run the whole working tree, so a broken shared change can stop the gates that guard its own fix; the version check is always met for this kit's modules.

The session first recommended B, as the cheaper path. The decider answered that local development needs one test of a change's impact on modules and shared code together, that the package is for other projects that use the constitution kit and not for the kit itself, and that the kit's own sessions may rely on the previous stable release. The session read that as A and recommended A. The decider chose A in chat on 2026-10-22.

<a id="r7"></a>**R7.** A module's plugin holds no shared code: nothing stands at `plugin/scripts/constitution_layer_kit`, no link, no copy and no file. Its entry files import the package that pip installed for `python3`, in every project, the kit's own sessions included. This replaces item 2 of the Ruling of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) for the plugin, with its principle that what the platform installs carries everything it runs, and the plugin's link in R1 of [dec-0096-shared-package-named-constitution-layer-kit](dec-0096-shared-package-named-constitution-layer-kit.md#r1) and in item 11 of R4 of [dec-0098-modules-install-from-a-plugin-subfolder](dec-0098-modules-install-from-a-plugin-subfolder.md#r4). Item 7 of the Ruling of dec-0025, the fallback to copies, and its widening by R4 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md#r4) to the link in an installed copy, have no object now.

<a id="r8"></a>**R8.** A module's tests keep their links to the shared package, to the shared test files and to the module's own packages. The harness puts the folder that holds the shared package on the `PYTHONPATH` of every gate it runs, after any folder a test puts there, so that a gate under test imports the shared code of its own commit and never an installed release. `scripts/check-shared-links.py` holds the links in `tests/` and is red for anything at `plugin/scripts/constitution_layer_kit`.

<a id="r9"></a>**R9.** The kit's own sessions run each module's code from the working tree with the release of the package that the developer installed. A module that requires a later version stops there with `C16`, which does not block in hook mode, until that release is installed or the developer installs `shared/` from the clone. The install guide asks every project to install the package as R1 says, beside PyYAML. This narrows the closing clause of R1 of [dec-0043-kit-plugins-through-project-settings](dec-0043-kit-plugins-through-project-settings.md#r1): a kit session runs under the kit's gates once the package is installed.

## 3. The name of the dials file

- **A. Two optional fields of the identity, `dials_file` and `module_prefix`, with today's values as defaults.** A gate reads all of its dials from its identity's file.
  - **Pros:** the smallest widening; no module of this kit changes; another kit's gate that reads only its own dials works on its own file.
  - **Cons:** such a gate that also resolves policies cannot read `root_policy` from `constitution.yaml` while its dials sit in its own file; the two field names are fixed from the first release on.
- **B. The kernel keys from `constitution.yaml`, the module's namespace from `dials_file`.**
  - **Pros:** it fits the other kit's own file and its rule that no key stands in both files; a gate there can resolve policies.
  - **Cons:** two files read and validated in each run; designed before the other kit's kernel exists; shared code that no module of this kit needs.
- **C. Keep both names, and add the fields when the other kit's first gate needs them.**
  - **Pros:** nothing is built before a reader exists; a field added later is a compatible minor release.
  - **Cons:** the first release cannot serve another kit's own file.

The session recommended A. Asked when the parameters help, it said only for another kit's gate that uses this package's pipeline with its own file, and changed its recommendation to C, since no such gate exists. The decider chose none of the three as put, in chat on 2026-10-22: the file's name becomes a context variable with no default, and no global variable is patched. The prefix followed, in sections 4 and 5. The session reads the choice as one file per gate, as in A, and keeps the two-file read of B deferred.

<a id="r10"></a>**R10.** The name of the dials file a gate reads is a context variable of the shared package, with no default. Each process declares it once, through one shared function, before its run. A second, different declaration is a defect, and so is a read before the first, as for the identity. A gate reads all of its dials from that one file, the kernel keys included, and every shared message names the file declared. No module-level name holds the file's name and nothing patches one: `DIALS_FILE` leaves `model.py`. Each module of this kit declares `constitution.yaml`.

<a id="r11"></a>**R11.** Deferred: a gate that reads the kernel keys and the policy namespaces from `constitution.yaml` and its own namespace from another file, option B. Signal: another kit's gate must resolve policies while its dials sit in its own file.

## 4. Where the module prefix lives

- **A. A top-level key inside the dials file**, `module_prefix: const-` in `constitution.yaml`.
  - **Pros:** the file says which of its keys are module namespaces; no code names the prefix; each layer's file states its own.
  - **Cons:** a third key owned by the kernel, so [kernel §6](../../kernel/CONVENTIONS.md#k6), the dials schema, the shared copy of the schema and the install guide's example change; a file written today lacks it; a project can set it wrong and change how every gate reads its file.
- **B. Inside the context variable, beside the file's name.**
  - **Pros:** no change to the kernel or the schema; no default anywhere; a project's file cannot change how the gates read it.
  - **Cons:** every entry point sets the pair; the file does not say which prefix its modules carry.

The session recommended B: strict, with nothing changed in the kernel or in a project's file. The decider chose A in chat on 2026-10-22: the prefix belongs to the modules, and a module's dials cannot sit in two files.

<a id="r12"></a>**R12.** `module_prefix` is a third key owned by the kernel, beside `root_policy` and `territory_dialect`: the prefix of the module namespaces in that dials file. A top-level key that starts with it and holds a mapping is a module's namespace, read leniently as before. `MODULE_PREFIX` leaves `dials.py`. [Kernel §6](../../kernel/CONVENTIONS.md#k6) and its schema name the key, and the shared reader's copy of the schema, `KERNEL_KEYS`, the kit's own `constitution.yaml` and the install guide's dials example carry it. This replaces the count of two kernel-owned keys in ruling 1 of [dec-0014-territory-dialect](dec-0014-territory-dialect.md).

## 5. Whether the prefix is required

- **A. Required.** Every dials file a gate reads names `module_prefix`; a file without it is a configuration failure that names the key to add.
  - **Pros:** no default anywhere, as for the file's name; a reader of the file always sees the prefix; another layer's file is never read with the wrong prefix.
  - **Cons:** even a minimal file names it; if it is forgotten, every gate stops until it is added, without blocking in hook mode.
- **B. Optional, with the default `const-` stated in [kernel §6](../../kernel/CONVENTIONS.md#k6)**, as `gitignore` is for `territory_dialect`.
  - **Pros:** every file written today stays valid; the code carries the kernel's default, not a name of this kit.
  - **Cons:** `const-` sits in the shared code again; another layer's file that forgets the key is read with `const-` in silence, its module namespaces taken for policy namespaces.

The session recommended A, since B's misreading would be a silent pass. The decider chose A in chat on 2026-10-22.

<a id="r13"></a>**R13.** A dials file a gate reads names `module_prefix`, a kebab-case word that ends in `-`. A file without it, or with another value, is a configuration failure of every gate that reads it, under a sub-key of `C5`. The namespace of the module that reads the file starts with the prefix, or the gate fails under another sub-key of `C5`, since it reads another layer's file.

## 6. What the package failures say

- **A. The exact command, with the tag.**
  - **Pros:** the exact fix that [law 6 of CLAUDE.md](../../CLAUDE.md#law-6) asks for; `scripts/check-copies.py` would hold every copy of the address equal.
  - **Cons:** the repository's address in every entry file and in the shared messages, so a rename changes them all; the tag's form becomes code.
- **B. The package and the version, and a pointer to the install guide.**
  - **Pros:** no address in code; a rename touches only documents.
  - **Cons:** not the exact fix that [law 6 of CLAUDE.md](../../CLAUDE.md#law-6) asks for; the person opens a file to find the command, and a hook shows one line.

The session recommended A, for the exact fix. The decider chose B in chat on 2026-10-22. The session kept the pointer as concrete as the code allows: the path of the module's own install note.

<a id="r14"></a>**R14.** `C15`, which the entry file prints when the package cannot be imported, and `C16` and `C17` of R5 name the package, the version the module requires, the version found where there is one, and the path of the module's own `INSTALL.md`, and close with the module's clause. A generator's three carry no clause, as its `C14` does. The texts stand in [§3 of kit-shared-gate-code](../../shared/GATE.md#g3).

<a id="r15"></a>**R15.** Each module's `INSTALL.md` gives the exact command of R1, at the tag of the version the module requires.

## 7. The rule on a missing library's install command

Writing this record, the session found that section 6's choice departs from a rule: a missing interpreter or library exits 1 with the install command in its message, from option B of section 1 of [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md), carried in step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md).

- **A. Keep section 6's choice, and record an exception to the rule for the shared package.**
  - **Pros:** it is what the decider chose; no message prescribes a command that installs one exact tag, which in one shared environment could replace a newer release that another module needs; the address stays out of code.
  - **Cons:** a rule now has an exception; the fix is one step further away than `C2`'s.
- **B. The exact command through `requirements.txt`.** Each module's `requirements.txt` names the package by its git URL at the tag it requires, and the failures say `run: python3 -m pip install -r '<requirements.txt>'`, as `C2` does.
  - **Pros:** the rule holds whole; the exact fix; the address in a data file.
  - **Cons:** the command installs exactly the module's tag, so it can replace a newer release that another module needs; eleven files carry the address; the shared item S137 must learn the line.

The session recommended A, for the replacement risk in one shared environment. The decider chose A in chat on 2026-10-22.

<a id="r16"></a>**R16.** The shared package is the one library whose failure points at its install note and not at a command. Every other missing library still exits 1 with its install command in its message, and a missing interpreter with where to get one.

## 8. How the kit's checks get the change's package

- **A. The checks set it up themselves.** A throwaway virtual environment, with the system's packages, whose `.pth` file names the change's `shared/`, its `python3` first on `PATH` for the sessions the checks start; the eval runner the same in its container; one more check builds the package.
  - **Pros:** a local run checks the working tree's shared code as CI does, and works offline but for the build check; nothing touches the release the developer installed; the build check proves that the package builds, installs and imports.
  - **Cons:** the install and session checks run the code from a folder and not from a built package, so only the build check sees a packaging mistake; more code in the checks.
- **B. The workflow installs it.** Each CI job runs `python3 -m pip install ./shared` first.
  - **Pros:** the least code.
  - **Cons:** a local run uses the release the developer installed, so a local green can hide a red.
- **C. CI builds one wheel per run, and every job installs it.**
  - **Pros:** one build, the same bytes in every job.
  - **Cons:** jobs depend on each other; local runs as in B.

The session first put A with a build in each check. Asked why that needed the network, it revised A to the `.pth` way, checked offline. It recommended A: only there does a local run check the code CI checks. The decider chose A in chat on 2026-10-22.

<a id="r17"></a>**R17.** The steps that the install and session checks share, in `scripts/kit_install.py`, and the install guide's check make a throwaway virtual environment from the `python3` they run under, with its system packages, whose `.pth` file names the change's own `shared/`. They put its `bin` first on `PATH` for every session and gate they start. Nothing is built, and nothing needs the network.

<a id="r18"></a>**R18.** The eval runner puts the change's `shared/` into each case's container and makes it importable the same way. The receipt's hash covers `shared/constitution_layer_kit/` beside the module's own files, since a session loads it.

<a id="r19"></a>**R19.** `scripts/check-shared-package.py`, an entry of the gate group with `--self-test` as its fixture, builds the distribution from `shared/`, installs it into a fresh virtual environment and imports it there. It holds the installed version equal to `__version__`, and PyYAML installed with it. It is the one check that needs the package index.

## Deferred and to come

<a id="r20"></a>**R20.** Deferred: publication on PyPI, option E of section 1. Signal: the repository goes public at step 10 of the rollout plan. Until then R1 serves every reader, and so replaces item 5 of the Ruling of [dec-0023-shared-gate-code-at-module-two](dec-0023-shared-gate-code-at-module-two.md), delivery by package index for readers outside plugins.

<a id="r21"></a>**R21.** Deferred: the shared test files of `shared/tests/` stay out of the distribution, so another kit's modules get no shared harness and no shared items through pip. Signal: another kit's first module needs them.

<a id="r22"></a>**R22.** Deferred: a check that `__version__` rose after a change to the shared code since the last tag, which R4 leaves to review. Signal: a release that missed its raise.

<a id="r23"></a>**R23.** The first release: once this change is merged, the decider tags `constitution-layer-kit-v1.0.0` on its merge commit and installs that release for the `python3` of the kit's own sessions.

## 9. A module's version after a change to the shared code

Writing the documents, the session found that rule 7 of [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r7), step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md) and rule 3 of [plc-0002-kernel](../policies/plc-0002-kernel.md#r3) said that a change to the shared code bumps the version of every published module that links or requires it. No plugin links the code now, and nothing above ruled what takes the clause's place.

- **A. A module's version moves only with its own files.** The package's `__version__` records the shared change, and a module that starts to need a later release raises its `REQUIRES`, which edits its entry files and so bumps it.
  - **Pros:** a module's version says what its plugin holds; no version moves when nothing installed changed; the package's version and the version check carry the shared change to a project.
  - **Cons:** a project that reads only module versions does not see a shared fix; the texts of [rule 3 of plc-0002-kernel](../policies/plc-0002-kernel.md#r3) and of R1 of [dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md#r1) no longer agree with the rule.
- **B. Every published module that requires the package bumps on every shared change.**
  - **Pros:** module versions keep tracking every change to what a gate runs; the texts barely change.
  - **Cons:** a version moves while none of the module's files changed; every shared fix means a release of every module beside the package's tag.

The session recommended A: a module's version then says what its plugin holds. The decider answered in chat on 2026-10-22 that a module's version is bumped when the module loses its consistency with the earlier shared code, most likely as an explicit act for that edge case rather than an automatic one. The session reads that as A.

<a id="r24"></a>**R24.** A change to the shared code bumps no module's version by itself. A module's version is bumped, as an explicit act of the change, when the module stops being consistent with the earlier shared code and raises the version it requires (R6). This replaces, for the shared code, the clause of R1 of [dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md#r1) that a change to the shared code bumps the version of every published module that links it; a draft still need not be bumped.

## Applied

The record was born `active`: its questions were decided one per message, and the change grew while it was applied, one commit per piece. The commit that adds section 9 states R24 in its documents and sets the record `inactive`: every item has its home.

## Carry list

1. R1 — [the install guide](../../INSTALL.md#s1), prerequisite 3; [kit-shared-gate-code §1](../../shared/GATE.md#g1), the paragraph on delivery; [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), rule 11; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module".
2. R2 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the paragraph on delivery; [the distribution's description](../../shared/pyproject.toml); [check-copies](../../scripts/check-copies.py), its docstring.
3. R3 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), rule 11.
4. R4 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), rules 11, [7](../policies/plc-0009-shared-code.md#r7) and [9](../policies/plc-0009-shared-code.md#r9).
5. R5 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `cli`, [§2](../../shared/GATE.md#g2) item 6 and [§3](../../shared/GATE.md#g3), the rows `C16` and `C17`; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [the template](../../module-template/MODULE.md#t6), rule 1; [cli](../../shared/constitution_layer_kit/cli.py), `version_failure`.
6. R6 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6; [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r11), rules 11 and [9](../policies/plc-0009-shared-code.md#r9); [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [check-copies](../../scripts/check-copies.py), its docstring.
7. R7 — [kit-shared-gate-code](../../shared/GATE.md), its opening note, [§2](../../shared/GATE.md#g2) item 7 and [§4](../../shared/GATE.md#g4) limit 3; [law 3 of CLAUDE.md](../../CLAUDE.md#law-3), and step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the intent page](../../INTENT.md#i3), its architecture; [the template](../../module-template/MODULE.md#t6), rule 1; [requirement A12.1](../requirements.md#a12-1); [check-shared-links](../../scripts/check-shared-links.py), its docstring. What it replaces, and what has no object now, is history.
8. R8 — [kit-shared-gate-code](../../shared/GATE.md), its opening note, [§2](../../shared/GATE.md#g2) items 7 and 8 and [§5](../../shared/GATE.md#g5), the row K1; [law 3 of CLAUDE.md](../../CLAUDE.md#law-3), and step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); [the harness](../../shared/tests/harness.py); [check-shared-links](../../scripts/check-shared-links.py), its docstring.
9. R9 — [CLAUDE.md](../../CLAUDE.md), the opening paragraph of "Session conduct"; [kit-shared-gate-code §4](../../shared/GATE.md#g4), limit 3; [the install guide](../../INSTALL.md#s1), prerequisite 3, and [its §4](../../INSTALL.md#s4). What it narrows or replaces is history.
10. R10 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`, [§2](../../shared/GATE.md#g2) items 1 and 5 and [§3](../../shared/GATE.md#g3), its opening; [identity](../../shared/constitution_layer_kit/identity.py), `declare_dials_file` and `dials_file`.
11. R11 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts.
12. R12 — [kernel §6](../../kernel/CONVENTIONS.md#k6); [the dials schema](../../kernel/schemas/constitution.schema.json); [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `dials`; [model](../../shared/constitution_layer_kit/model.py), `KERNEL_KEYS`; [the kit's dials file](../../constitution.yaml); [the install guide](../../INSTALL.md#s2), step 6. What it replaces is history.
13. R13 — [kernel §6](../../kernel/CONVENTIONS.md#k6); [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `dials`, and [§3](../../shared/GATE.md#g3), the rows `C5.11` and `C5.12`; [dials](../../shared/constitution_layer_kit/dials.py).
14. R14 — [kit-shared-gate-code §3](../../shared/GATE.md#g3), its opening and the rows `C15` to `C17`, and [§2](../../shared/GATE.md#g2) item 6.
15. R15 — [the install guide](../../INSTALL.md#s1), prerequisite 3; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6; [the template](../../module-template/MODULE.md#t6), the row of the install note, and [the template's install note](../../module-template/plugin/INSTALL.md); each module's `plugin/INSTALL.md`; [check-copies](../../scripts/check-copies.py), its docstring.
16. R16 — [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module", its sentences on the script runtime; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6; [the template](../../module-template/MODULE.md#t6), rule 7.
17. R17 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [kit-shared-gate-code §4](../../shared/GATE.md#g4), limit 3; [requirement A12.1](../requirements.md#a12-1); [kit_install](../../scripts/kit_install.py), its docstring.
18. R18 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [run-evals](../../scripts/run-evals.py) and [kit_evals](../../scripts/kit_evals.py), their docstrings; [the eval image](../../scripts/eval-container/Dockerfile), its opening comment.
19. R19 — [CLAUDE.md](../../CLAUDE.md), the bullet "The gate list and CI"; [kit-shared-gate-code §1](../../shared/GATE.md#g1), the paragraph on delivery; [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r9), rule 9; [check-shared-package](../../scripts/check-shared-package.py), its docstring.
20. R20 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts. What it replaces is history.
21. R21 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts.
22. R22 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the deferred parts; [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r9), rule 9.
23. R23 — pending: [the rollout plan](../rollout-plan.md#s10a), step 10a.
24. R24 — [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r7), rule 7; [CLAUDE.md](../../CLAUDE.md), step 4 of "Developing a module"; [plc-0002-kernel](../policies/plc-0002-kernel.md#r3), rule 3. That it replaces a clause of R1 of dec-0053-drafts-keep-their-versions is history.
