---
id: dec-0066-interaction-reader-dials-and-entry-matching
type: task-record
title: The shell gate's reader takes its wrappers and shells from two dials, an entry's words may stand apart by options, and an entry the reader cannot produce is refused
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shell gate's reader takes its wrappers and shells from two dials, an entry's words may stand apart by options, and an entry the reader cannot produce is refused

## Context

An audit of the kit's hardcoded logic on 2026-10-02 found three gaps in the shell gate of [`const-interaction`](../requirements.md#const-interaction). First, an entry of the dial `destructive` written as a path, `[./scripts/deploy.sh]`, or behind a wrapper, `[sudo, rm]`, loaded without a word and could never match. The reader takes those forms off a command before it compares. Second, an entry matched only when its words were the first words of a command, so `kubectl -n prod delete pod x` passed an entry `[kubectl, delete]`; only git's options before its verb were skipped. Third, the reader knew a fixed set of twelve wrappers and five shells, so `fish -c 'git push -f'` or `ionice -c3 rm -rf build` passed green. Two smaller findings came with them: a shell comment is read as a command, and on Windows without Git Bash, where the shell tool is `PowerShell`, the gate never runs.

The change this record rules is on one branch. The module is a draft at `0.0.1`, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). The decider kept the audit's recommended fix for the first two gaps when reading the change's plan on 2026-10-05; sections 1 and 3 hold them. Eleven more questions were put to the decider in chat, one per message, each with lettered options and one recommendation, the pick a letter; sections 2, 4 to 12 and 14 hold them. Section 13 holds what the change makes where no choice existed. The kit's own `constitution.yaml` sets no `destructive` entries, so nothing in the kit is refused.

## 1. An entry the reader can never produce

The audit argued four ways to treat an entry whose words the reader would never give back.

- **A. Refuse it when the dials load.** The reader itself is the test: an entry that does not read as itself is a configuration failure, and the message names the entry to write.
  - **Pros:** explicit; one rule covers paths, wrappers, assignments and shell words; the reader is its own test, so the two cannot drift; the fix names the exact entry.
  - **Cons:** a dials file that loaded before now fails; one new message to design.
- **B. Rewrite each entry through the reader when it loads, in silence.**
  - **Pros:** no new message; old dials files keep working.
  - **Cons:** the consumer wrote one thing and the gate holds another, unseen; `[sudo]` alone would become an empty entry that matches every command.
- **C. Match a path entry against the program as written.**
  - **Pros:** a consumer can gate one script and not another of the same name.
  - **Cons:** it overturns the base-name reading of R6 of [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md); three spellings of one path, each missed one a silent pass; it fixes the path case only.
- **D. Only state it as a limit.**
  - **Pros:** no code.
  - **Cons:** the gate stays a silent no-op for a consumer who misses the line, while the module already refuses a misspelt key for this reason.

**Recommendation.** A, by the audit's session on 2026-10-02: it turns a silent no-op into a teaching error and keeps the reading R6 rules.

**Choice.** A, kept by the decider when reading the change's plan on 2026-10-05.

**R1.** An entry of `destructive` whose words the reader, with the reader dials as loaded, does not read as themselves is a configuration failure at every entry point. The message names the reading and the entry to write. Where the reading is empty, or holds a word the base name empties, the fix asks for the command the wrapper or shell runs; where it hands a string on to be split again, the command the shell runs. A base-name entry such as `[deploy.sh]` still matches that program in every folder. When `destructive` is absent, each default entry is read the same way, and one that the reader dials keep from reading as itself is a configuration failure; its fix names the entry of `wrappers` or `shells` to remove or change.

## 2. Whether the change earns a new survey

Option-tolerant matching reopens the matching of [res-0008-const-interaction](../research/res-0008-const-interaction.md), and the `PowerShell` tool is a platform fact that comparison never names. [Rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) asks a new survey for a module revision that reopens a mechanism.

- **A. A new survey, limited to the reopened mechanisms.**
  - **Pros:** meets both triggers of rule 7; the PowerShell facts and the man pages' dates are checked before code; the later questions rest on checked facts.
  - **Cons:** one more agent run and a long document, about an hour more; the first replacement of a survey in the kit.
- **B. No survey; this record's context carries the reasoning.**
  - **Pros:** faster; fewer documents; the audit had already measured the false prompts.
  - **Cons:** it arguably breaks rule 7; the PowerShell and man-page facts stay unchecked; the audit's measure came from local session files, not a dated public source; res-0008 stays active while it no longer describes the module.

**Recommendation.** A, by the session: both triggers hold, the PowerShell question turns on platform behaviour the kit never takes from memory, and an hour is cheaper than an audit round that finds an unchecked fact.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R2.** [res-0012-const-interaction](../research/res-0012-const-interaction.md) is the module's comparison for the five mechanisms it surveyed, and res-0008 for the rest; res-0008 is `inactive`.

## 3. Options between an entry's words

The survey weighed five ways in its section 2: skip option words between an entry's words; a field per entry listing its program's options that take a value; a dial of wrappers; match the entry anywhere in the command; or state the limit only. The dial of wrappers is the question of section 6, so four ways are argued here.

- **A. Skip options between an entry's words.**
  - **Pros:** closes the gap for every program without a new dial; lets an entry name a runner; on 1,281 commands it added one prompt, a true one.
  - **Cons:** a rare false prompt where an option's value equals the next entry word.
- **B. A field per entry listing its program's options that take a value.**
  - **Pros:** exact, no false prompt.
  - **Cons:** every entry must carry the list; a short list fails open in silence, the same failure as before.
- **C. Match the entry anywhere in the command.**
  - **Pros:** catches more without a list.
  - **Cons:** reads arguments as commands: `git rm -r --cached build` and `echo rm -rf build` prompt.
- **D. State the limit only.**
  - **Pros:** no code.
  - **Cons:** the common `kubectl` and `helm` form stays unmatched.

**Recommendation.** A, by the survey and the audit.

**Choice.** A, kept by the decider when reading the change's plan on 2026-10-05.

**R3.** An entry matches a command when its first word is the command's program and each later word follows in order, with only options, and the one value after an option written without `=`, between them. Any other word, or `--`, between them means no match. A word equal to the wanted entry word is read as that word. Flags are matched after the last entry word, as before. Where an option's value equals the next entry word, the gate prompts by design: `kubectl -n delete get pods`, `git -C restore status`.

## 4. Git's own option skip

The reader skipped git's global options before its verb by a fixed list. With R3, the matcher skips them for every program. Checked on a copy, R3 alone matched every git form the tests used, and it also caught `git --exec-path push -f`, which the list let through.

- **A. Remove git's skip; R3 covers it.**
  - **Pros:** one list and one special case fewer; git under the same rule as every program; the `--exec-path` miss fixed with no list to keep; an entry such as `[git, -C]` then reads as itself.
  - **Cons:** a contrived false prompt such as `git -C restore status`; the explain shows git's options; the survey had advised keeping the exact skip.
- **B. Keep the skip in code, its `--exec-path` fixed.**
  - **Pros:** exact; the explain reads as before; the survey's advice.
  - **Cons:** a second mechanism for one program; a list in code that is no dial; kept by hand.
- **C. A third dial of programs and their options.**
  - **Pros:** exact, and a consumer could add `kubectl -n`.
  - **Cons:** a third new dial; it repeats R3.

**Recommendation.** A, by the session: R3 already does the job for every program.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R4.** The reader no longer skips git's global options; R3 covers them. This reverses in part R6 of [dec-0042-interaction-module-rulings](dec-0042-interaction-module-rulings.md), its clause "git's global options before the verb skipped", as [rule 13 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r13) asks.

## 5. Which shells and wrappers the reader adds

Every candidate passed green before (res-0012, E2).

- **A. The survey's cheap and exact set:** shells `fish`, `ash`, `mksh`, `yash`, `posh`, `csh`, `tcsh`; wrappers `busybox`, `setsid`, `ionice`, `taskset`, `caffeinate`, the plain `flock`.
  - **Pros:** each exact on a dated page; no false prompt; with R1, an entry that starts with a newly listed wrapper becomes a teaching error.
  - **Cons:** `chrt` and `flock -c` stay unread; seven page sources to keep.
- **B. A, plus `chrt`, `flock -c`, and fish's `-C` and `--command=`.**
  - **Pros:** closes three more forms; the limit is shorter.
  - **Cons:** each needs code of its own; more edge cases in the reader; no consumer has asked.
- **C. The shells and `busybox` only.**
  - **Pros:** the smallest change.
  - **Cons:** `setsid`, `ionice`, `taskset` and `caffeinate` keep hiding `rm -rf`.

**Recommendation.** A, by the session.

**Choice.** B, by the decider, in chat on 2026-10-05. In the same message the decider asked whether these patterns could go into a dial a user extends; section 6 holds that question.

**R5.** The defaults hold the twelve wrappers the reader had, `exec` as a wrapper, and the set of option B. The module document names the page each entry of that set was read from and the date it was read: shells `fish`, with `-c`, `--command`, `-C` and `--init-command` as its command flags, `ash`, `mksh`, `yash`, `posh`, `csh`, `tcsh`; wrappers `busybox`, `setsid`, `ionice`, `taskset`, `caffeinate`, `flock` with `-c` after its lock file, `chrt`.

## 6. Whether a user can extend the lists

Asked after a probe on a copy: a wrapper named by its words alone, every place the command may start after options read, asked for each runner tried and passed the controls.

- **A. Keep the scope; log the dial for later.**
  - **Pros:** the scope stays as set; a smaller change, record and audit; no consumer has asked.
  - **Cons:** a later change needs its own record and audit over the same files.
- **B. Two dials that only add to built-in lists, a wrapper given by its words.**
  - **Pros:** what the decider asked; the probe removed the need for an option list; the built-in lists stay a floor.
  - **Cons:** about three more pieces; a rare false prompt; an option between a wrapper's own words still escapes.
- **C. Move the whole lists into dials whose defaults are the lists, each wrapper with its exact options; a consumer may extend or replace.**
  - **Pros:** every pattern in one visible place; exact.
  - **Cons:** a consumer could drop `sudo` and weaken the defaults in silence; a short option list fails open; the largest change.

**Recommendation.** B, by the session.

**Choice.** C, by the decider, in chat on 2026-10-05.

**R6.** The reader's wrappers and shells are the dials `wrappers` and `shells` of the module, whose defaults are the lists of R5.

## 7. How a given list relates to the defaults

- **A. Add by name; a default is never dropped.** A new name adds a wrapper; a default's name replaces that default's options.
  - **Pros:** extending is one short entry; one wrapper can be overridden; the gate never examines less than its defaults.
  - **Cons:** no way to turn a default off; not quite the "replace" of section 6.
- **B. Add by name; drop a default only by an explicit entry, each drop named at every session start.**
  - **Pros:** extend, override one, or drop; a short dials file for the usual case; a weaker gate is said aloud.
  - **Cons:** one more field and one more session line; two meanings an entry can carry.
- **C. A given list replaces the whole default list.**
  - **Pros:** one rule, the same as `destructive`.
  - **Cons:** adding one wrapper means copying about seventy options, which go stale in silence.

**Recommendation.** B, by the session.

**Choice.** B, by the decider, in chat on 2026-10-05.

**R7.** A given list is applied to the defaults by name: an entry whose command is a default's replaces that default whole, a new command is added, and `drop: true` removes a default. An empty list leaves the defaults. Session start names every dropped default, one line each.

## 8. The dials' fields and the option rule

Proposed as a shape to accept or override.

- **A. Two dials, `wrappers` and `shells`, with the proposed fields.**
  - **Pros:** every special case of the old reader becomes data a user can see; short entries; one clear difference between the two kinds.
  - **Cons:** five fields to check, each with a message; the module's dials go from seven to nine.
- **B. One dial holding both, a field marking a shell.**
  - **Pros:** one dial, one set of messages.
  - **Cons:** a shell entry that forgets the field reads its script file as a command.
- **C. Two dials with only a name, the options that take a value, and `drop`; the special cases stay code.**
  - **Pros:** the smallest shape.
  - **Cons:** not every pattern a user can extend; the special cases stay hidden.

**Recommendation.** A, by the session.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R8.** A wrapper entry has `command` (one or more words), `with_value`, `positionals`, `numbers`, `command_flags` and `drop`; a shell entry has `command` (one word), `with_value`, `command_flags` and `drop`. For both, `--` ends the options and `--name=value` is one word. In a wrapper's short cluster the first letter that is in `with_value` or `command_flags` ends it, its value the rest of the word or else the next word. A wrapper's command follows its options, then `positionals` words, then up to `numbers` words that are numbers; a command flag's value and the words after it are the command. A shell's short cluster is read two ways, and every string either way finds is read: bash's, where each valued letter takes the next word, and the way of zsh and ksh, where the cluster's command-flag letters are taken out first and the first valued letter of those left takes the letters after it, else the next word. A command-flag letter anywhere in the cluster counts in both, and a command flag then takes its string (R10).

## 9. Whether a replaced default is named

A replaced default can weaken the gate: `{command: [sudo]}` takes away sudo's options, so `sudo -u root rm -rf b` reads `root` as the program.

- **A. Name every replacement too.**
  - **Pros:** any change to a default is visible; one rule, no comparison.
  - **Cons:** a safe replacement also prints a line.
- **B. Name a replacement only when it lists less than the default.**
  - **Pros:** fewer lines.
  - **Cons:** "less" is a comparison to design; an added option a program does not take also misreads.
- **C. Drops only.**
  - **Pros:** no more work.
  - **Cons:** a replacement can weaken the gate in silence.

**Recommendation.** A, by the session.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R9.** Session start names every replaced default too, one line each, beside the dropped ones in the dials' order; an added entry prints nothing.

## 10. A shell given two command strings

`fish -C 'set x 1' -c 'rm -rf b'` read only `set x 1`: fish gives `-c` and `-C` each a value, while the reader read a shell's command flag as a switch whose string is the first operand.

- **A. Fix it: each command flag takes the next word when it is no option, else the first operand.**
  - **Pros:** closes a miss on a default the decider chose; one rule for every shell; the bash forms already pinned.
  - **Cons:** one more round; more edge cases in the shell reader.
- **B. State it as a limit.**
  - **Pros:** no code.
  - **Cons:** a known miss on a default shell stays.

**Recommendation.** A, by the session.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R10.** For a shell, every command flag met yields a string: a long flag's attached value (`--command=x`), else the next word when that word is no option and no other option's value, else the first operand after the options end. Each string is read once.

## 11. A shell comment

- **A. Keep reading comments; state the false prompt.**
  - **Pros:** no new code in the reader's most fragile part; on 1,281 commands no verdict changed.
  - **Cons:** a comment holding a separator and a listed command prompts.
- **B. Drop comments exactly inside the splitter.**
  - **Pros:** the shell's own grammar.
  - **Cons:** a mistake hides a real command; a simpler drop hid `git push -f` in two forms.

**Recommendation.** A, by the session.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R11.** A comment is read as text: one that holds a separator and a listed command prompts.

## 12. The PowerShell tool

- **A. Widen the matcher to `Bash|PowerShell` and read with the same reader.**
  - **Pros:** never reads less than the silence before; catches the forms PowerShell shares with POSIX shells.
  - **Cons:** touches shared code; cmdlets, case and `.exe` unread; no Windows machine to prove it.
- **B. Widen with a reader of PowerShell's own.**
  - **Pros:** reads PowerShell as PowerShell.
  - **Cons:** a second parser; a large growth.
- **C. State the gap only.**
  - **Pros:** no code, no shared change.
  - **Cons:** the gate stays silent for Windows users with PowerShell on by default.

**Recommendation.** A, by the session.

**Choice.** "A, but no PowerShell for now", by the decider, in chat on 2026-10-05. Asked which reading was meant, the decider confirmed: no PowerShell in this change, the gap stated, the widening later.

**R12.** The gate's matcher stays `Bash`. Wherever the `PowerShell` tool is the shell, the gate examines nothing and says nothing; the module states this as a limit, and the widening is deferred with its signal.

## 13. What the change makes where no choice existed

These items carry no options. Each follows from the answers above or from the module's own rule that a dial which would be ignored in silence is refused. Each stands open to the decider's override before the yes.

**R13.** `--` ends a wrapper's or a shell's options, as the programs do. `exec` is a wrapper, its `-a` taking a value, and no longer a shell word.

**R14.** A reader dial that would load and do nothing is a configuration failure at every entry point. The shapes are: not a list or a mapping; an unknown field; a bad `command`; a wrapper or a shell whose word the reader takes off first, a shell word or an assignment; a bad option; one word in both `with_value` and `command_flags`; a shell with no `command_flags`; a count that is not a whole number; a bad `drop`, or one naming no default; one command twice; one word both a wrapper and a shell.

**R15.** The module states as limits what the reader does not see or reads more than runs: runners such as `uv run` unless a dial names them, `watch`, `script`, `nix-shell --run`, an option between a multi-word wrapper's words, an abbreviated long option, fish's attached short value (`fish -c'…'`), and a POSIX shell given `-c` twice, which reads the later string too.

## 14. The module document's length

The module document grew from 64,248 to about 85,000 characters, past its 66,000 `module-documents` ceiling, at warning. Most of the growth carries the rulings above.

- **A. Leave it at warning; shorten it as work of its own.**
  - **Pros:** this change keeps to the rulings it was opened for; nothing blocks; the shortening is audited on its own; the same call as for the shared-code page.
  - **Cons:** the document stands over its ceiling until then; the warning shows on every edit.
- **B. Shorten it inside this change.**
  - **Pros:** the change closes within its ceiling.
  - **Cons:** a second pass over the documents; cutting text that carries rulings risks the audit.
- **C. Raise the `module-documents` ceiling.**
  - **Pros:** one line; the warning goes.
  - **Cons:** a ceiling raised to fit holds nothing; it applies to every module document.

**Recommendation.** A, by the session.

**Choice.** A, by the decider, in chat on 2026-10-05.

**R16.** The module document stands over its ceiling at warning after this change; its shortening, which moves text that repeats the code or another section and keeps every ruling, is a work item of its own.

## Applied

The commits of this branch apply every item. The commits before the one that adds this record changed the code and wrote the documents' sentences; the message of each commit names what it changed and the sentences it added. The commit that adds this record adds the module document's row for it and the pending entry of R16. The record is born `inactive`.

## Carry list

1. R1 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t7), the row `destructive` of section 7; [its section 6](../../modules/const-interaction/MODULE.md#t6), the row C5 of the message table.
2. R2 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t6), the research item of section 6.
3. R3 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t5), "Matches" in section 5; [its section 9](../../modules/const-interaction/MODULE.md#t9), limit 4.
4. R4 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t5), section 5, which skips no program's options by name; the reversal of a clause of R6 of dec-0042-interaction-module-rulings is history.
5. R5 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t7), the default wrappers and shells of section 7.
6. R6 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t7), the rows `wrappers` and `shells` of section 7.
7. R7 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t7), the rows `wrappers` and `shells`; [its section 6](../../modules/const-interaction/MODULE.md#t6), the row S1 of the message table.
8. R8 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t7), the rows `wrappers` and `shells`; [its section 5](../../modules/const-interaction/MODULE.md#t5), "Reading".
9. R9 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t6), the row S1 of the message table.
10. R10 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t5), "Reading" in section 5.
11. R11 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t9), limit 4 of section 9.
12. R12 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t5), the invariant of section 5; [its section 9](../../modules/const-interaction/MODULE.md#t9), limit 9; [its section 12](../../modules/const-interaction/MODULE.md#t12), item 8.
13. R13 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t5), "Reading" in section 5.
14. R14 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t6), the row C5 of the message table.
15. R15 — [`const-interaction`](../../modules/const-interaction/MODULE.md#t9), limit 4 of section 9.
16. R16 — pending: [step 9 of the rollout plan](../rollout-plan.md#s9), the shortening of the module document.
