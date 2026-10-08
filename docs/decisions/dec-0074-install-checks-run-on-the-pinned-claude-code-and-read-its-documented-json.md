---
id: dec-0074-install-checks-run-on-the-pinned-claude-code-and-read-its-documented-json
type: task-record
title: The install checks run on the Claude Code version one file pins, read the platform through its documented JSON commands, and fail to run, never blame a module, when a reply cannot be read
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The install checks run on the Claude Code version one file pins, read the platform through its documented JSON commands, and fail to run, never blame a module, when a reply cannot be read

## Context

Two kit checks drive the real `claude` command and judge what it did: `scripts/check-bare-install.py`, which installs one module on a bare repository ([dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md), [dec-0060-ci-installs-from-the-github-remote](dec-0060-ci-installs-from-the-github-remote.md)), and `scripts/check-install-guide.py`, which runs the commands of the install guide ([dec-0062-install-guide-governed-kind](dec-0062-install-guide-governed-kind.md), [dec-0071-projects-install-from-github](dec-0071-projects-install-from-github.md)). An audit of the kit's hardcoded logic on 2026-10-02 found that both read what Claude Code wrote on a version nothing tied to them, and it was probed again on the trunk on 2026-10-08:

- **The version.** The workflow installed Claude Code 2.1.282 as a literal; neither check asked which `claude` it ran. A run on this machine's 2.1.286 reported GREEN and said nothing of the version, and the kit's own sessions run the install entries of the gate list there.
- **The records.** Both checks read Claude Code's record files, `installed_plugins.json` and `known_marketplaces.json`, and the layout of its plugin folder. Most of what they read is documented, but the files' nesting is not, and the guide's check read any fault as an empty record: a renamed file or key gave a red finding against the install guide, and the uninstall claim lost half its test in silence.
- **The blame.** A timed-out install, or any non-zero exit of `plugin install`, was a finding against the module: "Claude Code refuses to install it".
- **The commit.** A remote install whose record named no commit was compared with the working folder, which on a pull request is the merge commit, not the branch installed.

Claude Code documents machine-readable commands for all of this: `plugin install --json`, `plugin list --json` and `plugin marketplace list --json`. On 2026-10-08 the session read the documentation's raw pages and probed the commands, with an empty configuration folder, on 2.1.286 and, at the decider's yes in chat that day, on 2.1.282 installed in a scratch folder beside the machine's own: every field the change reads is there on both, and the record's `gitCommitSha` is the one field the kit needs that no page documents. The decider read the change's plan the same day and kept the audit's recommended fix, its four parts: one pinned version, a version check, the documented commands, and the small fixes. Three questions were put to the decider in chat that day, one per message, each with lettered options and one recommendation, the pick a letter; sections 1 to 3 hold them.

The marketplace's name, typed in both checks, is now read from `.claude-plugin/marketplace.json`, and a hook that declares no `timeout` is waited for as the hooks reference gives a command hook on its event: both routine, noted in their commits. No module changes, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)).

## 1. One pull request and one record

The change narrows what [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md) calls a refusal, reverses part of R2 of [dec-0060-ci-installs-from-the-github-remote](dec-0060-ci-installs-from-the-github-remote.md) and adds a rule on when the checks may run: `process` stakes. The pin file and the small fixes alone would be routine. The question was how the change reaches the trunk.

- **A. One pull request, one `process` record** for all four parts, the routine pieces noted in their commits.
  - **Pros:** one carry audit, one independent verification, one yes; the version check stands before any new read of the platform, so every new read runs on the pinned version from its first commit; both checks' docstrings are written and audited once.
  - **Cons:** the routine half waits for the whole change, about one working day, though no one waits for it.
- **B. Two pull requests**, the pin file and the small fixes first as a routine change, then the version check and the documented reads with the record.
  - **Pros:** the routine half reaches the trunk a few hours sooner; the first pull request needs no carry audit.
  - **Cons:** both edit the same two scripts and their docstrings, so the second audit reads text the first changed; two gate-list runs, two CI runs and two merges; the pin file would land while only the workflow reads it.

The session recommended A: nobody waits for the routine half, so B's speed buys nothing anyone uses, and it splits two scripts between two changes. The decider chose A in chat on 2026-10-08.

**R1.** One pull request and one record for the rulings of sections 2 and 3; the marketplace's name and a hook's missing timeout routine, noted in their commits.

## 2. The pinned version, and a run on another

The plan the decider kept puts the version in one file, read by the workflow and by both checks, and has each check ask `claude --version` before any other `claude` command. The question was what a run on another version does. Claude Code's auto-updater moves a machine's version unasked, and the kit's sessions run the twelve install entries of the gate list locally.

- **A. Fail to run on any other version, everywhere**; the fix puts a pinned `claude` first on `PATH` for the run, installed beside one's own.
  - **Pros:** the strictest; every GREEN anywhere is on the pinned version; no variable to read or forget.
  - **Cons:** the twelve local entries fail to run on this machine until a pinned `claude` sits in a fixed place; every local gate-list run must carry that `PATH`; the set-up repeats at every pin bump.
- **B. Fail to run in CI only**: the workflow sets one variable in the jobs that run `claude`; elsewhere a mismatch adds a note naming both versions to every report line and the run goes on.
  - **Pros:** the verdict that guards the merge is always on the pin; local runs need no set-up and say which version they ran on.
  - **Cons:** a later edit of the workflow that drops the variable makes CI lax unseen; a local GREEN on another version is a weaker proof, said only by the note.
- **C. Fail to run unless a variable opts out**; then the run goes on and every report line carries the note naming both versions.
  - **Pros:** strict by default, so a missing variable fails loudly, never quietly; CI needs nothing new; a lax local run is asked for by name, and its report says so.
  - **Cons:** one new variable for people to type, held by review; the kit's sessions set it on every local run, so for local runs the opt-out becomes the habit.

The session recommended C, with the variable `CONSTITUTION_KIT_ANY_CLAUDE=1`: A's strictness wherever no one asked otherwise, B's local ease, without B's flaw of a lost variable weakening CI unseen. The decider chose C, the name as proposed, in chat on 2026-10-08.

**R2.** The Claude Code version the kit's two install checks drive has one home, `scripts/claude-code.version`: one line, the version, three numbers joined by dots. The kit's CI installs that version for the jobs that run `claude`. A file that is not one such line is a failure to run. The version stays 2.1.282; the pin that R3 of [dec-0059-bare-repo-install-in-ci](dec-0059-bare-repo-install-in-ci.md) records now lives in that file.

**R3.** Both install checks ask `claude --version` before any other `claude` command. On the pinned version they run as before. On another version they fail to run, with the fix of running on the pinned version installed beside one's own, unless the environment sets `CONSTITUTION_KIT_ANY_CLAUDE` to exactly `1`; then they run, and every headline line of the report after the version check — each finding's, each failure line, the closing line — ends with a note naming both versions. A reply that names no version is a failure to run, even with the opt-out set.

## 3. What the checks read, and an install whose record names no commit

The plan the decider kept has both checks read what Claude Code installed through its documented `--json` commands, and read a fault in a reply as a failure to run, never as a finding against a module or the guide. The commit an install came from is in no such reply: it stands only in the install record, as `gitCommitSha`, which no page documents. The question was what a remote install whose record names no commit does, which R2 of [dec-0060-ci-installs-from-the-github-remote](dec-0060-ci-installs-from-the-github-remote.md) answered with a comparison against the working folder.

- **A. Fail to run, with the fix**; an install from a local folder is still compared with that folder.
  - **Pros:** never compares the copy with a tree it did not come from, which can be red on a file only the trunk changed or green on a copy it never matched; on the pinned version the record always names the commit, probed on 2.1.282 and 2.1.286 with the install from GitHub, so it fires only when the platform changed; the one undocumented read fails closed, as the rest of the reads do.
  - **Cons:** changes R2 of dec-0060-ci-installs-from-the-github-remote and the cell of [requirement A12.1](../requirements.md#a12-1); a future version that drops the field makes every module job fail to run until the read is replaced, which the pin's move finds at once.
- **B. Keep the fallback to the working folder**, and add a note line.
  - **Pros:** no ruling changes; a run goes on and still says something.
  - **Cons:** the wrong-blame case stays, red or green against the wrong tree with a note beside it; the one undocumented read stays open in the check a platform change reaches first.

The session recommended A: it never fires on the pinned version, and when it fires it names the real cause, the platform, not a module. The decider chose A in chat on 2026-10-08.

**R4.** The install checks read what Claude Code installed through its documented `--json` commands: `scripts/check-bare-install.py` the result of `plugin install` and the entry of `plugin list`, `scripts/check-install-guide.py` the entries of `plugin list` and `plugin marketplace list` and the project's settings. The guide's check reads no record file; the bare-install check reads the install record only for the commit of R5, finding the copy's entry there by its documented `installPath`. A reply of those commands the check cannot read — no JSON, another shape, and in the guide's check an entry without its `id` or `name` —, a project settings file the guide's check cannot read, replies that disagree, a list command that exits other than 0 or gives no result in its time, and the bare-install check's `plugin install` that gives no result in its time are a failure to run, never a finding against a module or the guide; an install Claude Code refuses, its result's `outcome` being `failed`, stays a finding against the module. The fix of a reply, a record or a settings file the check cannot read names, on the pinned version, the kit's reader to update, and off it, the run on the pinned version. The fix of the bare-install check's install that gives no result is to run the check again, and check that git can reach the source. The fix of a list command that gives no result is to run the check again, and of one that exits other than 0, to run that command by hand, read why it fails, then run the check again; off the pinned version both name the run on the pinned version.

**R5.** `scripts/check-bare-install.py` compares a remote install's copy with the kit's source at the commit the install record names, the `gitCommitSha` of the entry whose `installPath` is the copy's: the one field the kit reads that no page documents. A record that names no commit, or a value that is no git object id, is a failure to run; there is no fallback to the working folder. An install from a local folder reads no record and is compared with that folder.

**R6.** R5 reverses, in R2 of [dec-0060-ci-installs-from-the-github-remote](dec-0060-ci-installs-from-the-github-remote.md), the clause that a remote install whose record names no commit is compared with the working folder.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code, the tests and the documents; the message of each commit names what it changed and the sentences it added, with the code or test line that makes each true. The record is born `inactive`.

## Carry list

1. R1 — history only: how this change was recorded and landed.
2. R2 — [the workflow](../../.github/workflows/gates.yml), its step that installs Claude Code; [the reader](../../scripts/kit_module_doc.py), its docstring of `pinned_claude`; [check-bare-install](../../scripts/check-bare-install.py) and [check-install-guide](../../scripts/check-install-guide.py), their docstrings; [the gate list](../../scripts/gate-list.sh), its header. That the pin of R3 of dec-0059-bare-repo-install-in-ci moved to the file is history.
3. R3 — [the reader](../../scripts/kit_module_doc.py), its docstring of `claude_note`; [check-bare-install](../../scripts/check-bare-install.py) and [check-install-guide](../../scripts/check-install-guide.py), their docstrings; [requirement A12.1](../requirements.md#a12-1), its enforcement cell; [the gate list](../../scripts/gate-list.sh), its header.
4. R4 — [check-bare-install](../../scripts/check-bare-install.py) and [check-install-guide](../../scripts/check-install-guide.py), their docstrings; [the reader](../../scripts/kit_module_doc.py), its docstring of `platform_fix`; [requirement A12.1](../requirements.md#a12-1), its enforcement cell.
5. R5 — [check-bare-install](../../scripts/check-bare-install.py), its docstring; [requirement A12.1](../requirements.md#a12-1), its enforcement cell.
6. R6 — history only: the reversal of a clause of R2 of dec-0060-ci-installs-from-the-github-remote.
