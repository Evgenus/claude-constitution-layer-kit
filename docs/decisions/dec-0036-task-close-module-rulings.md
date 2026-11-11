---
id: dec-0036-task-close-module-rulings
type: task-record
title: Rulings of the const-task-close authoring — a change that touches described code updates its documents or declares no impact; the Stop hook blocks once on a dirty tree
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-task-close authoring

## Context

The sixth module, [`const-task-close`](../requirements.md#const-task-close), is authored from 2026-09-23 in the kit, ahead of its Phase C slot in the rollout plan, as the decider chose in chat that day: the kit is consumer zero for the code territories its own current-state documents describe — the shared gate code and its page, each module's scripts and its document, the git hooks and the session rules — kept in step by hand across five modules, and its history shows the cost the module prevents. Its research comparison is [res-0006-const-task-close](../research/res-0006-const-task-close.md). Its rows are [requirement A4.1](../requirements.md#a4-1) to [requirement A4.7](../requirements.md#a4-7), every one confirmed by the comparison against the matrix, with one correction to the warn channel of [requirement A4.7](../requirements.md#a4-7). The questions of sections 1 to 4 were put to the decider in chat, one per message, each with lettered options. Section 5 records the reorder, which the fifth module's record found to extend an older ruling and which needs a handle here for the same reason. What the session derived without a choice — the stalled-drift assist deferred with its signal, two skills, a `working_files` dial read by the scan for a note, the close skill performing a record's status change that the record skill defines, a `declaration_key` dial, the body given as text — follows the comparison's recommendations and the laws of [CLAUDE.md](../../CLAUDE.md). It is stated in the module's document with its reasoning.

## 1. Where the no-impact declaration lives

The gate examines a change as a commit range and asks, per coverage pair the change touches, whether one of the pair's documents also changed. Where none did, the change must say so. The specification left the mechanism open — "PR body marker or commit trailer" — with the decider named.

- **A. A commit trailer, per change.** `No-Doc-Impact: <pair name> — <reason>`, one per pair, on any commit of the range, read with git's trailer parser; the body marker deferred with its precedence settled.
  - **Pros:**
    - **works in the kit today**, where no pull request exists before Phase D;
    - **the shape of the kit's `Accepted:` and `Carry-Audit:` trailers**, read by an existing gate;
    - **stays in git history** and is listed by one command;
    - **the local run, CI and the kit's merges** read the same thing with no network.
  - **Cons:**
    - **git's paragraph rules are unforgiving** — one colon-less line hides every trailer of its paragraph — so the fix must teach the shape;
    - **a squash merge keeps a trailer** only when its message lands last;
    - **a reviewer reads the pull request's body**, not the commits.
- **B. A pull-request body marker only.** A line in the description, read in CI from the event payload and locally through the forge's client.
  - **Pros:** where the reviewer reads; survives a squash; one place per change.
  - **Cons:**
    - **nothing to read in the kit before Phase D**, so no live proof here;
    - **a local run needs the network**, a client and an open pull request;
    - **the declaration lives outside the repository's history.**
- **C. Both from the start, either satisfying the gate.**
  - **Pros:** covers a consumer that squashes and a local run alike.
  - **Cons:**
    - **two readers**, one of which cannot be exercised live in the kit and has no consumer asking for it;
    - **more surface for the same verdict.**

The session recommended A, for the kit being consumer zero with `--no-ff` merges and a trailer reader already in place. <a id="r1"></a>**R1.** C, chosen by the decider in chat on 2026-09-23. Applied so that the module stays portable:

- **the gate never calls a forge client** and never touches the network;
- **the body is given as text** through `--body <file>`, which CI writes from the event payload and a local closer may pipe from the forge's client;
- **the marker is the same line as the trailer**, on its own line anywhere in the body, so one parser reads both sources;
- **without `--body` the trailers alone are read.**

The session's objection stands in the module's honest limits: the body half has no live proof in the kit before Phase D, and its fixtures are against text.

<a id="r2"></a>**R2.** The declaration's form, the session's defaults accepted with R1:

- **the key is `No-Doc-Impact`**, matched case-insensitively as git matches it, and is the module's dial `declaration_key`;
- **the value is the pair's name**, a dash, a reason the gate requires non-empty and never judges;
- **there is no wildcard** — a change touching several pairs writes one line per pair, and a value naming no pair is a finding, not a declaration;
- **the scope is the change** — any commit of the range counts, as with `Accepted:` — since the kit's own history would have been red nineteen times per commit and once per change.

## 2. The shape of the coverage map

The map says which current-state documents describe which code; the gate reads it on every change and the declaration names an entry of it.

- **A. Named pairs in the module's own namespace.**
  - `coverage: [{name, code: [<gitignore patterns>], docs: [<paths>]}]`, absent by default;
  - `code` through the shared matcher with the shared refusal of unreadable patterns;
  - `docs` exact paths, a missing one a configuration failure;
  - **overlap allowed, order meaningless.**
  - **Pros:**
    - **the module reads only its own namespace**, so the kernel-alone test holds with zero configuration;
    - **a name gives the declaration** something short and rename-proof to cite;
    - **the kit's map is a handful of entries.**
  - **Cons:** a name to invent per pair; one entry per module, since a pattern has no capture.
- **B. A mapping keyed by document path.** `coverage: {<doc path>: [<patterns>]}`, the declaration naming the path.
  - **Pros:** no names; one document, one entry.
  - **Cons:**
    - **a pair with two documents writes its patterns twice;**
    - **a document's rename** changes what every past declaration meant;
    - **a path in a trailer** is longer and easier to misspell.
- **C. Declared by the policies,** a key such as `describes` in each policy's namespace.
  - **Pros:** the policy that governs a document says what code it describes.
  - **Cons:**
    - **a module would read a policy-namespace key** beyond `territory` — a kernel change with one reader;
    - **a document outside every policy's territory**, such as `CLAUDE.md`, could not be covered.

<a id="r3"></a>**R3.** A, chosen by the decider in chat on 2026-09-23, with the session's defaults:

- `name` required, kebab-case and unique, a duplicate or a malformed one a configuration failure;
- **a pair with empty `docs` refused**, the sharper form deferred;
- **a `docs` path that also matches the pair's `code`** left out of the pair's code side, so a documentation-only change is never its own trigger;
- **deleted and renamed paths** count as touched on both sides;
- **an absent map is zero pairs examined**, said so.

## 3. The `Stop` hook's severities and default

The hook fires at every turn end, runs `git status --porcelain` from the event's directory, and treats any line as dirty. The comparison showed live that on `Stop` the shared warn channel — `additionalContext` with a `systemMessage` — continues the conversation to the platform's cap, so a warn here is a `systemMessage` alone, which the user sees and the model never does; and that a block is exit 2 on the first firing, after which `stop_hook_active` is true and the hook lets the turn end, so a block costs one continuation and never a standoff. The matrix's row says the hook "warns … blocking is a dial".

- **A. The fixed dial `severity`, default `block`,** as every gate of the kit:
  - `block`, the model receives the three-part message once and, in the live run, committed;
  - `warn`, the user gets the notice, the model nothing.
  - **Pros:**
    - **no shared change and no second dial**, since the shared reader already defaults `severity` to `block`;
    - **the model is taught at the moment it matters;**
    - **the kit's own rule**, never leave a turn dirty, is exactly `block`.
  - **Cons:**
    - **overturns the matrix's default**, keeping its shape;
    - **a block at the end of a turn** that was a question still asks for a commit, and a model that refuses is let go on the second firing — a request, not a wall.
- **B. Default `warn` through `severity`,** which needs the shared reader to take a per-module default.
  - **Pros:** the matrix's word; the quiet adoption path.
  - **Cons:** a shared change for one module's default; under warn the model never learns the rule from the hook; one namespace in six defaults differently.
- **C. A module-own dial `turn_end: warn | block`, default `warn`, and no `severity`.**
  - **Pros:** the specification's own wording; no shared change.
  - **Cons:**
    - **a gate with a hook mode and no `severity`** breaks the template's rule for gates and the shared fixture items that exercise the dial;
    - **the same cons as B** for what warn teaches.

<a id="r4"></a>**R4.** A, chosen by the decider in chat on 2026-09-23, with the session's defaults:

- **the kit calibrates `block`** in its own dials file;
- **the hook checks the tree only**, the range check running at close, on demand and in CI;
- **the block message names** the module's `commit-before-edit` skill and carries the commit command itself;
- `SubagentStop` is not wired;
- **the second firing of a turn** is exit 0 with a green line whatever the tree holds, so the platform's cap is never reached by this hook.

## 4. How the range check finds its base

`--since <ref>` names the base outright and `--change <commit>` examines one landed change by its first-parent diff — a `--no-ff` merge in the kit. The question is what a bare `--scan` does.

- **A. A dial `trunk`, default `main`.**
  - **The base is the merge-base** of the trunk and the head, the trunk looked up as a local branch, then as `origin/<trunk>`;
  - **a head that is the trunk** examines its last landed change;
  - **a trunk found nowhere** is a configuration failure teaching `--since` and the dial.
  - **Pros:**
    - **one lookup a reader can predict;**
    - **works in the kit**, in a fresh clone through the remote-tracking branch, and on a detached head;
    - **no chain to fixture.**
  - **Cons:** a consumer whose trunk is not `main` sets one line first; a stale local trunk widens the range, which is only more paths examined.
- **B. A chain:** the merge-base with the branch's upstream, then with `origin/HEAD`, then with the dial's trunk — the comparison's recommendation.
  - **Pros:** the most repository shapes without configuration.
  - **Cons:**
    - **the first step is wrong on a pushed feature branch**, whose upstream is its own remote copy: the merge-base is the head, the range is empty, and the green examined nothing while looking like a verdict;
    - **three steps, three fixtures, three messages.**
- **C. No default:** `--since` or `--change` required.
  - **Pros:** nothing guessed.
  - **Cons:** the bare scan every other module offers becomes a form to fill.

<a id="r5"></a>**R5.** A, chosen by the decider in chat on 2026-09-23, with the session's defaults:

- **the check compares committed changes only**, the working tree being the hook's business;
- **a `--since` or `--change` naming a ref** the repository does not have is a configuration failure, not a skip;
- `--change` on a non-merge commit examines that commit alone;
- `--history <n>` is deferred with its signal;
- **the count line names the pairs**, the commits and the range.

## 5. Where the module is authored

No options were put: the decider chose in chat on 2026-09-23, at the end of the fifth module's authoring, to author this module in the kit before the consumer's bootstrap. [dec-0006-accumulating-set-first](dec-0006-accumulating-set-first.md) names four modules for authoring in the kit and places this one in the consumer's first week. [dec-0035-locations-module-rulings](dec-0035-locations-module-rulings.md) extended that list once, with a handle, and this is the second extension.

<a id="r6"></a>**R6.** [`const-task-close`](../requirements.md#const-task-close) is authored in the kit as consumer zero, like the four accumulating modules of Phase A and the fifth, ahead of its Phase C slot — the kit being consumer zero for the code territories its own current-state documents describe. Its consumer-live proof is a step of the consumer's bootstrap, and a finding there is a fix with a version bump, as [dec-0015-pre-module-audit-rulings](dec-0015-pre-module-audit-rulings.md) rules for the four. Chosen by the decider in chat on 2026-09-23.

## Carry list

1. R1 — the row of [requirement A4.6](../requirements.md#a4-6) in [§3](../../modules/const-task-close/MODULE.md#t3) of the module's document, the invariant of its [§5](../../modules/const-task-close/MODULE.md#t5), the rows T2 and C12 of the error-message table in its [§6](../../modules/const-task-close/MODULE.md#t6), items 3 and 6 of its [§9](../../modules/const-task-close/MODULE.md#t9) — the second holding the objection: no forge client, no network, no live proof of the body before Phase D — and item 1 of its [§12](../../modules/const-task-close/MODULE.md#t12); steps 5 and 6 of [the install note](../../modules/const-task-close/plugin/INSTALL.md). That the session recommended A: history only.
2. R2 — the row `declaration_key` of [§7](../../modules/const-task-close/MODULE.md#t7) of the module's document, the rows T3 and T4 of its [§6](../../modules/const-task-close/MODULE.md#t6), the row of [requirement A4.1](../requirements.md#a4-1) in its [§3](../../modules/const-task-close/MODULE.md#t3) for the scope, and item 4 of its [§9](../../modules/const-task-close/MODULE.md#t9); step 5 of [the install note](../../modules/const-task-close/plugin/INSTALL.md) and step 3 of [the close skill](../../modules/const-task-close/plugin/skills/close-task/SKILL.md) for one line per pair.
3. R3 — the row `coverage` of [§7](../../modules/const-task-close/MODULE.md#t7) of the module's document, the rows X1 and C5 of its [§6](../../modules/const-task-close/MODULE.md#t6), item 8 of its [§9](../../modules/const-task-close/MODULE.md#t9), and item 5 of its [§12](../../modules/const-task-close/MODULE.md#t12).
4. R4 — the row `severity` of [§7](../../modules/const-task-close/MODULE.md#t7) of the module's document, the row of [requirement A4.7](../requirements.md#a4-7) in its [§3](../../modules/const-task-close/MODULE.md#t3), the row T1 and the `G1` hook forms of its [§6](../../modules/const-task-close/MODULE.md#t6), items 1, 2 and 11 of its [§9](../../modules/const-task-close/MODULE.md#t9), and item 6 of its [§12](../../modules/const-task-close/MODULE.md#t12); the kit's own calibration in [constitution.yaml](../../constitution.yaml); that a hook gate at a turn's end carries `severity` as a write-time gate does, [template §7](../../module-template/MODULE.md#t7) and [template §9](../../module-template/slot-guidance.md#s6). That the matrix's default was overturned: the research row of the module's [§6](../../modules/const-task-close/MODULE.md#t6).
5. R5 — the row `trunk` of [§7](../../modules/const-task-close/MODULE.md#t7) of the module's document, the row of [requirement A4.4](../requirements.md#a4-4) in its [§3](../../modules/const-task-close/MODULE.md#t3), the row C12 and the F9 tail of its [§6](../../modules/const-task-close/MODULE.md#t6), items 4, 7 and 10 of its [§9](../../modules/const-task-close/MODULE.md#t9), and item 4 of its [§12](../../modules/const-task-close/MODULE.md#t12).
6. R6 — the "not a project" bullet of [INTENT.md](../../INTENT.md), which names the kit consumer zero for the code territories its documents describe, and row L4 of [§10](../../modules/const-task-close/MODULE.md#t10) of the module's document, which names the consumer's bootstrap as the moment of the consumer-live proof and a finding there a fix with a version bump; the step itself is Phase B step 5 of the rollout plan, the kit's write-head, until that bootstrap closes.
