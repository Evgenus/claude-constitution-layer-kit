---
id: dec-0118-two-profiles-taken-in-the-guides-order
type: task-record
title: The kit ships two profiles, a project takes their lines in the guide's order, and a kit check holds them
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The kit ships two profiles, a project takes their lines in the guide's order, and a kit check holds them

## Context

Item 10.6 of [the rollout plan](../rollout-plan.md#s10-6) asked for `profiles/` in three words. Three sentences were all the kit said of profiles, and no record ruled on them:

1. **The kernel.** [Kernel §6](../constitution/CONVENTIONS.md#k6) calls profiles prewritten `constitution.yaml` files shipped with the kit, and names three as examples.
2. **The intent page.** [Its first section](../../INTENT.md#i1) gives the cost of adoption as install, pick a profile, override a few dials.
3. **The install guide.** [Its last section](../../INSTALL.md#s6) said profiles were planned.

On 2026-11-11 the session read section 7 of every module document, to learn what a project must write that no default gives. Four things came out of that reading:

1. **What must be written.** The schema requires `module_prefix`. A project writes `root_policy` and each policy's territory. Three dials switch a check on: `record_policies`, `catalogs` and `coverage`. Every other dial works at its default.
2. **What no profile can hold.** The ceilings of module [`const-doc-budgets`](../requirements.md#const-doc-budgets) come from the project's own history. The dials `deciders` and `preferences` name the project's people. The dial `log_dir` needs a folder that the project's git ignores.
3. **The cost of today's guide.** Step 4 of [the install guide](../../INSTALL.md#s2) showed the whole file for the answer no to its two questions, and only the changed keys for yes. The guide recommends yes. So a reader who followed it merged two blocks by hand, and nothing checked the result. The first consumer project took exactly that merged file.
4. **What the schema does not see.** The kernel's schema leaves a module's namespace open. A misspelt dial there is valid against the schema, and only the module's own reader refuses it.

## 1. Which profiles the kit ships

- **A. One profile, `new-project.yaml`.** The dials file as step 6 of the guide leaves it, with the policies a numbered kind.
  - **Pros:** it ends the merge by hand; it is the one shape a consumer has used; one file to keep valid.
  - **Cons:** "pick a profile" has one choice; a repository that already has documents gets no help.
- **B. Two profiles, `new-project.yaml` and `existing-repository.yaml`.** The second is the first with `severity: warn` on every gate that runs in a hook.
  - **Pros:** it covers both cases the intent page names, an existing project and a new one; the second file sets dials that are easy to miss by hand.
  - **Cons:** no project has yet adopted the kit onto existing documents, so the second profile is unproven; `warn` alone may not be enough there, since the scans still read every Markdown file.
- **C. Three profiles after the kernel's examples.** `solo-agents`, `small-team` and `regulated`, which would differ in severity and in who decides.
  - **Pros:** it matches the kernel's sentence word for word.
  - **Cons:** the dials that tell a team's shape name people, which no profile can hold; the differences would be invented, with no consumer behind them.
- **D. No profile yet.** The guide says that profiles wait for a consumer's need.
  - **Pros:** nothing to build or to keep valid.
  - **Cons:** the intent page's "pick a profile" stays untrue; the merge by hand stays.

Options A to C shared the form of a profile and the check that holds it, as R2 and R3 state them. The session recommended A: it fixes the one cost seen today, and it is the only profile with a consumer behind it. The decider chose B in chat on 2026-11-11.

The session keeps one objection. Two of the nine gates are not about documents written before the kit. With `warn`, module [`const-interaction`](../requirements.md#const-interaction) lets a listed destructive command run with no prompt, and module [`const-task-close`](../requirements.md#const-task-close) stops asking the model to commit a dirty tree. The session put this to the decider in chat on 2026-11-11, after the choice, and the choice stood.

<a id="r1"></a>**R1.** The kit ships two profiles in `profiles/`. `new-project.yaml` is the dials file as step 6 of the install guide leaves it, with the policies a numbered kind. `existing-repository.yaml` is the same file for a repository that already has documents when it adopts the kit. It also sets `severity: warn` for each of the nine modules whose gate runs in a hook: [`const-meta-types`](../requirements.md#const-meta-types), [`const-decision-records`](../requirements.md#const-decision-records), [`const-catalogs`](../requirements.md#const-catalogs), [`const-referencing`](../requirements.md#const-referencing), [`const-task-close`](../requirements.md#const-task-close), [`const-questions`](../requirements.md#const-questions), [`const-interaction`](../requirements.md#const-interaction), [`const-language`](../requirements.md#const-language) and [`const-doc-budgets`](../requirements.md#const-doc-budgets).

<a id="r2"></a>**R2.** A profile is a file `profiles/<kebab-case-name>.yaml`, and the folder holds profiles alone. It is a dials file in block style. It holds only what no default gives: the kernel-owned keys, the territory of the first three policies, and the dials that switch a check on. `existing-repository.yaml` holds its nine `severity` lines beside these. A profile names no style guide: the skill of module [`const-styling`](../requirements.md#const-styling) writes those lines in step 6 of the guide.

<a id="r3"></a>**R3.** The kit's `scripts/check-profiles.py` holds the profiles. It is the entry `profiles` of the gate list, with `--self-test` as its fixture. For every file of `profiles/` it holds that the file is a profile by its name, that it is YAML, that it is valid against the kernel's dials schema, that it is in block style, and that every key with the module prefix names a module folder. It then holds that every scan a module document declares exits 0 and prints no note on a throwaway repository, which holds the profile as its dials file and one policy for each namespace that claims a territory. It holds that the folder has a profile at all. Before the profiles, it runs every scan on a repository whose dials file is the module prefix alone, and a scan that is not green there stops the check as one that could not run. Three things stay review: that a profile writes no dial at its default, that two profiles agree where they should, and the dials of a module that has no scan.

<a id="r4"></a>**R4.** In the kit's own dials file, the `plc-` entry of the dial `mentions` of module [`const-referencing`](../requirements.md#const-referencing) reads every file but the profiles. A profile names the policies of the project that takes it, and the kit holds none of them.

<a id="r5"></a>**R5.** This change does not touch the kernel. Its three names of profiles are examples, and the kit ships none of them today.

## 2. How a project takes a profile

The session first told the decider that a project could copy a whole profile at step 4 of the guide. A probe on a scratch repository had shown that this works: a namespace written before its policy claims nothing until that policy exists, and the gates say so in a note. The session then found that this goes against R3 of [dec-0102-bootstrap-recommends-and-copies-the-kernel-first](dec-0102-bootstrap-recommends-and-copies-the-kernel-first.md#r3). That ruling has the bootstrap claim each further territory only once its kind has a policy.

- **A. In the guide's order.** Step 4 writes from the profile the lines that need no policy, and step 6 adds each policy's lines after that policy. A comment in the profile names the step that writes each line.
  - **Pros:** the earlier ruling stands; the guide agrees with the order that module [`const-locations`](../requirements.md#const-locations) teaches; the gates print no note about a policy that does not exist yet; the profile is still the checked, finished file, so the merge by hand ends.
  - **Cons:** taking a profile is several copies, not one.
- **B. Whole, at step 4.** The project copies the file once, and this record reverses the earlier ruling for a project that takes a profile.
  - **Pros:** one copy.
  - **Cons:** it reverses a ruling made on 2026-10-24; the territories stand before their policies, the exception the decider rejected then; the gates print a note on every write until each policy exists.

The session recommended A, since the order was the point of the earlier ruling. The decider chose A in chat on 2026-11-11.

<a id="r6"></a>**R6.** A project takes the lines of a profile in the order of the guide's steps. Step 4 writes the lines that need no policy, and from `existing-repository.yaml` each module's `severity` line too. Step 6 writes each further policy, and after it the lines of that policy. A comment in the profile names the step that writes each line. The guide names the two profiles in its step 4, in prose, in place of the block that showed the changed keys. Its `check=dials` block stays the one that its check writes.

## Applied

The change that creates this record applies every ruling. It adds the two profiles and the check, joins the check to the gate list, changes the `mentions` entry of the kit's dials file, and rewrites step 4 and the last section of the install guide. It adds a row for `profiles/` to the map of the root README, which binds nothing. The record is born `inactive`.

## Carry list

1. R1 — [the install guide](../../INSTALL.md#s2), step 4 of section 2; [the first profile](../../profiles/new-project.yaml) and [the second profile](../../profiles/existing-repository.yaml), which names the nine modules.
2. R2 — [the install guide](../../INSTALL.md#s2), step 4 of section 2, and [its last section](../../INSTALL.md#s6); [the check](../../scripts/check-profiles.py), its docstring, for the name and the folder.
3. R3 — [the check](../../scripts/check-profiles.py), its docstring; [the list script](../../scripts/gate-list.sh), its gate group; [the install guide](../../INSTALL.md#s6), its last section.
4. R4 — [the kit's dials file](../../constitution.yaml), the `mentions` dial of `const-referencing`.
5. R5 — history only: what this change left as it was.
6. R6 — [the install guide](../../INSTALL.md#s2), step 4 of section 2; [the first profile](../../profiles/new-project.yaml) and [the second profile](../../profiles/existing-repository.yaml), their comments.
