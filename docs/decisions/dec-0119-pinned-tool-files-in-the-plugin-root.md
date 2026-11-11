---
id: dec-0119-pinned-tool-files-in-the-plugin-root
type: task-record
title: The files of a pinned tool stand at the plugin root, among the scripts or in a folder named for the tool, and the coverage pair lists them
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The files of a pinned tool stand at the plugin root, among the scripts or in a folder named for the tool, and the coverage pair lists them

## Context

A module may ship files of a pinned third-party tool in its plugin: the tool's configuration, and its pin, the files that name the exact version an install takes. Three texts say what stands in a plugin root, and they did not agree with what the modules do:

1. The configuration row of [section 6 of the module template](../../module-template/MODULE.md#t6) gave one path, `plugin/<file>`, for a tool's configuration.
2. R1 of [dec-0098-modules-install-from-a-plugin-subfolder](dec-0098-modules-install-from-a-plugin-subfolder.md#r1) lists the parts of a plugin root. [Step 4 of the module-development page](../guide/developing-a-module.md#s4) and the plugin skeleton of [kit-template-slot-guidance](../../module-template/slot-guidance.md#s1) carry that list. None of the three names a tool's files.
3. [Step 1 of that page](../guide/developing-a-module.md#s1) lists what a module's pair in the coverage map of the range check holds: five folders. It names no tool file.

Two modules ship such files, as their own documents describe. Module [`const-referencing`](../requirements.md#const-referencing) keeps its `lychee.toml` among its scripts. Module [`const-change-cost`](../requirements.md#const-change-cost) keeps one configuration file at its plugin root. It keeps its pin, a `package.json` with its lockfile, in the folder `ccusage/` of the plugin root: R8 of [dec-0117-change-cost-module-rulings](dec-0117-change-cost-module-rulings.md#r8) put the pin there so that no platform install acts on it. Its coverage pair lists the three files by path.

On 2026-11-10 the carry audit of that module's records found the gap ([item 9.37 of the rollout plan](../rollout-plan.md#s9-37)). The template's row and the list of parts name no folder for a pinned tool's files. The two steps of the page name no tool file at all. The plan item holds the two findings as two pieces. In chat on 2026-11-11 the decider chose to close both with one record and one change, since both edit the same sentence of step 4.

## Ruling

<a id="r1"></a>**R1.** A pinned third-party tool's own files are parts of the plugin root. They are of two kinds: its configuration, which the code that runs the tool reads or hands to the tool, and its pin, the files that name the exact version an install takes. This adds them to the parts that R1 of [dec-0098-modules-install-from-a-plugin-subfolder](dec-0098-modules-install-from-a-plugin-subfolder.md#r1) lists.

<a id="r2"></a>**R2.** Each such file stands in one of three places: at the plugin root, `plugin/<file>`; among the scripts, `plugin/scripts/<file>`; or in a folder of the plugin root named for the tool, `plugin/<tool>/<file>`.

<a id="r3"></a>**R3.** A file that the platform acts on when it stands at a plugin root stands in the tool's folder, never at the root. A `package.json` with its lockfile is the case the kit has met. The module's platform facts name what the platform does at a plugin root, with its source.

<a id="r4"></a>**R4.** The path cell of the configuration row of a module's artifacts table lists every such file by its path. Of a file in a tool's folder the row says why the file stands there.

<a id="r5"></a>**R5.** A module's pair in the coverage map of the range check lists, by its path, each such file that stands outside `plugin/scripts/`. Review holds this: of a pair's code patterns, the kit's `scripts/check-gate-lists.py` asks only for the pair's five folders.

<a id="r6"></a>**R6.** The module document of [`const-change-cost`](../requirements.md#const-change-cost) said in two places that this gap was open. Both now name the template's rule.

<a id="r7"></a>**R7.** The rule of R1 to R5 stands in a section of [kit-template-slot-guidance](../../module-template/slot-guidance.md#s13) that was written there and never stood in the template, whose ceiling leaves no room for it. The opening of that page names the section as its one text of that kind.

<a id="r8"></a>**R8.** [Step 4 of the module-development page](../guide/developing-a-module.md#s4) said that no module ships tool configuration, in its sentence on the kit's linter, formatter and type checker. It now says that no module ships a configuration of those tools: a pinned tool's own configuration is another thing, which R1 admits.

## Reasoning

No real choice existed. Every placement the ruling names is already in use in a module whose document describes it, and the coverage pair of [`const-change-cost`](../requirements.md#const-change-cost) already lists its files. The template and the page only catch up, so that the next module finds the rule where it looks for it. Moving the files to one common place would change two plugins, and a change to a plugin makes its eval receipt stale, for no gain. R3 states for every module the reason that R8 of [dec-0117-change-cost-module-rulings](dec-0117-change-cost-module-rulings.md#r8) gave for one. It leaves the platform fact itself to the module that meets it, whose slot for platform facts asks for the source.

The record is born `inactive`: this change applies every item.

## Carry list

1. R1 — [the module-development page](../guide/developing-a-module.md#s4), step 4, the sentence on the parts that install and the one on where the parts sit; [kit-template-slot-guidance](../../module-template/slot-guidance.md#s1), the plugin skeleton; [the module template](../../module-template/MODULE.md#t6), the configuration row of section 6. What it adds to is history.
2. R2, R3, R4 — [kit-template-slot-guidance](../../module-template/slot-guidance.md#s13), the section "The configuration row"; [the module template](../../module-template/MODULE.md#t6), the configuration row of section 6, its path cell.
3. R5 — [the module-development page](../guide/developing-a-module.md#s1), step 1, the words on the coverage pair; [kit-template-slot-guidance](../../module-template/slot-guidance.md#s13), the section "The configuration row".
4. R6 — history only: a one-time edit of that document.
5. R7 — [kit-template-slot-guidance](../../module-template/slot-guidance.md), its opening.
6. R8 — [the module-development page](../guide/developing-a-module.md#s4), step 4, the sentence on the linter, the formatter and the type checker.
