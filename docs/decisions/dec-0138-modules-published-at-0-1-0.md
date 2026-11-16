---
id: dec-0138-modules-published-at-0-1-0
type: task-record
title: Modules are published at 0.1.0 and require the newest shared release that changed the shared pages
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Modules are published at 0.1.0 and require the newest shared release that changed the shared pages

Items 10.16 and 10.17 of the rollout plan publish the modules. Three questions came up on the way. Each has a section below.

## 1. The shared release a module requires at `0.1.0`

Every module was a draft at `0.0.1` or `0.0.2`. Their entry files asked for three different releases of the shared package. Three modules asked for the release 2.6.0 already. Four asked for 2.1.0 alone. Five mixed 2.0.0 and 2.1.0 across their entry files. Version `0.1.0` is what a project installs, so the number binds every project.

- **A. Every module requires 2.6.0.** One number for all twelve, in every entry file.
  - **Pros:** each module behaves as the shared page says. That page's limits on unreachable files and interrupts hold only from 2.6.0 on. A project installs one release anyway, and the mixed modules are mended in the same step.
  - **Cons:** nine modules raise their number without using a name that 2.6.0 added. A project on an older release must update it before any module runs.
- **B. Each module requires the lowest release its code needs.** The five mixed modules get one number each.
  - **Pros:** no module asks for more than it uses; fewer files change.
  - **Cons:** a module on an older release would not behave as the shared page says. Each module's document would then need a sentence on which limits hold from which release.
- **C. The numbers stay.** Only the versions move.
  - **Pros:** the smallest change.
  - **Cons:** the mix across entry files stays.

The orchestrating session recommended A: a published module should behave as its documents say. The decider picked A in that session's chat on 2026-11-16, with the words "A: all require 2.6.0".

<a id="r1"></a>**R1.** Every module of the kit is published at manifest version `0.1.0`. Its document opens with the sentence the template gives a published module. A new module still starts as a draft at `0.0.x`.

<a id="r2"></a>**R2.** At `0.1.0` every entry file of every module requires the release 2.6.0 of the shared package. Each plugin's install note names that release's tag.

## 2. The standing rule for the release a module requires

The pick of section 1 met a standing rule. R6 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r6) set the first release as a module's number. The module raised it only when it used a name that a later release added. Nine modules now require 2.6.0 without using such a name. So the rule had to say something else from here on.

- **A. The floor moves once.** Published modules require 2.6.0. After that the old rule holds again.
  - **Pros:** the smallest change to the rule; no further version bumps.
  - **Cons:** a later release that changes behaviour without a new name opens the same gap again.
- **B. Raise with the pages.** A change to the shared code that also changes the shared page or its messages raises every module's number.
  - **Pros:** a published module always behaves as its documents say; a release that only adds a test helper raises nothing.
  - **Cons:** each such change touches all the modules and needs fresh eval receipts; a project updates the shared package before the modules run.
- **C. Always the newest.** Every module always requires the newest release.
  - **Pros:** the simplest to state and to check.
  - **Cons:** every release raises every module, also one that no module can feel.

The orchestrating session recommended B: it keeps the promise behind the pick of section 1, and spares the bumps of C. The decider picked B in the same chat on 2026-11-16, with the words "B: raise with the pages".

<a id="r3"></a>**R3.** Every entry file of a module requires one release, the same in all of them. It is at least the newest release whose change to the shared code also changed the shared page or the page of shared messages. A change of that kind raises the release every module requires to the package's version, in the same change. A published module whose number rises is bumped in the same change. A change to the shared code that touches neither page raises no module's. A module that uses a name a later release added still requires that later release, in all its entry files. No other module follows it.

<a id="r4"></a>**R4.** R3 replaces the first sentence of R6 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r6). It also replaces the same sentence where R5 of [dec-0106-two-dials-files-and-kernel-keys](dec-0106-two-dials-files-and-kernel-keys.md#r5) states it for the current major. Three parts of those rulings stand. Review holds the raise. The copies check holds each number at or below the package's version. A new major raises every module's number to its first release, and that raise bumps a published module too. R3 also widens R24 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r24). That ruling bumps a module when it stops being consistent with the earlier shared code and raises its number. A change that also changes one of the two pages now counts as such a case for every module whose number it raises. Each such module's documents then describe the newer code.

<a id="r5"></a>**R5.** After a change of R3's kind lands, the kit's own sessions meet modules that require a release not yet made. So the release's tag follows the merge on the decider's go-ahead, the release is installed, and only then is a main checkout pulled. This is the order of the release 2.6.0.

## 3. What the install check holds of an update

R5 of [dec-0071-projects-install-from-github](dec-0071-projects-install-from-github.md#r5) left one fact of the guide untested. An update leaves a change at an unchanged version untaken. The guide stated it as seen on one day, since the check cannot put a change on GitHub. Item 10.17 of the rollout plan asked for a run again. An agent of the orchestrating session tested the platform's update on the Claude Code version the kit pins, in a throwaway home.

- **A. A probe on two fixed tags and the change.** The check registers the marketplace at project scope at one tag and installs two modules. It moves the marketplace to a second tag and then to the change, and updates one module each time.
  - **Pros:** both facts are held by a real run on every pull request; nothing is pushed; the two tags never move.
  - **Cons:** moving a marketplace at project scope is observed behaviour that the platform does not document. The run needs the network and about half a minute more.
- **B. The same probe at user scope.** The check edits the settings file between the two registrations.
  - **Pros:** it stays at the scope the guide uses.
  - **Cons:** it rests on a refusal of the platform and on where a settings file lies.
- **C. The fact stays stated.** No run.
  - **Pros:** no cost.
  - **Cons:** a release of the platform can change what an update takes, unseen.

The orchestrating session recommended A and had it built. No pick of these options was asked of the decider beforehand. The choice is the decider's yes on the change, named in the merge commit of the release's pull request.

<a id="r6"></a>**R6.** The install check holds by a run what a plugin update takes. A module whose files changed at an unchanged version is reported as up to date, and its cached copy stays as it was. A module whose manifest version rose is reported as updated, and its cached copy holds the change's files. The probe runs after the guide's own commands, in a configuration of its own. It uses the tags of the releases 2.5.0 and 2.6.0 of the shared package, and then the change itself. A fetch that failed, a reply it cannot read and a command that fails are each a failure to run, never a verdict. The platform leaves an empty folder named `.in_use` in a cached copy. Every comparison of the check sets it aside, the reinstall's among them. The probe reads the one JSON line of the platform's update command. The command's help names that line, and no documentation lists its fields. So this widens R4 of [dec-0074-install-checks-run-on-the-pinned-claude-code-and-read-its-documented-json](dec-0074-install-checks-run-on-the-pinned-claude-code-and-read-its-documented-json.md#r4). That ruling has the check read documented replies. This reverses two clauses of R5 of [dec-0071-projects-install-from-github](dec-0071-projects-install-from-github.md#r5). One has the guide state the fact with the version and the date it was seen. The other is "No run of the check exercises it". The rest of that R5 stands.

<a id="r7"></a>**R7.** The probe's limits are stated with it. Moving a marketplace at project scope is observed on the pinned version and not documented. A pull request from a fork, whose repository lacks the two tags, ends as a failure to run. What the probe does with a failed fetch is exercised by the self-test's stand-in alone. The platform's own reply to one was seen once by hand, on 2026-11-16.

## Applied

The commits of this record's branch apply every ruling. Each module's manifest says `0.1.0`, and each module's document opens with "Published at manifest version `0.1.0`". Every entry file states 2.6.0, and each plugin's install note names the tag `constitution-layer-kit-v2.6.0`. The shared page, the shared-code policy and the module-development page state R3, and the copies check's fix text follows it. The install guide and the README no longer call the modules drafts. The install check runs the probe of R6, and [§4 of the install guide](../../INSTALL.md#s4) says what it holds. The record is born `inactive`.

## Carry list

1. R1 — [the module template](../../module-template/MODULE.md), the status line of a published module; [the install guide](../../INSTALL.md), its opening. History only: the version of the day, which each module's manifest and document state.
2. R2 — history only: the release of the day, which each module's entry files, install note and document state; R3 is the rule that stands.
3. R3 — [the shared-code policy](../policies/plc-0009-shared-code.md#r11), rule 11; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6; [the module-development page](../guide/developing-a-module.md#s4), step 4. Also [the copies check](../../scripts/check-copies.py), the fix it gives for a number above the package's version.
4. R4 — [the shared-code policy](../policies/plc-0009-shared-code.md#r7), rules 7, [9](../policies/plc-0009-shared-code.md#r9) and [11](../policies/plc-0009-shared-code.md#r11); [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6. History only: which sentences of two accepted records it replaces, and those records stay as they were accepted.
5. R5 — [the shared-code policy](../policies/plc-0009-shared-code.md#r11), rule 11, on a release's tag. History only: the order kept for the release 2.6.0.
6. R6 — [§4 of the install guide](../../INSTALL.md#s4); [the gate-list page](../guide/gate-list-and-ci.md); [the install check](../../scripts/check-install-guide.py), its docstring and `update_probe`.
7. R7 — [the install check](../../scripts/check-install-guide.py), its docstring.
