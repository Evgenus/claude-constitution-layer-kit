---
id: dec-0136-flock-string-read-as-shell-text
type: task-record
title: A wrapper entry may mark its command string as shell text, flock is marked by default, and its reading as words stays beside it
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A wrapper entry may mark its command string as shell text, flock is marked by default, and its reading as words stays beside it

## Context

The shell gate of [const-interaction](../requirements.md#const-interaction) reads the string of a wrapper's command option as words. That is right for `env -S`, which splits its string into arguments and runs no shell. A run on macOS showed it: `env -S 'echo a; echo b > /dev/null'` printed `a; echo b > /dev/null`. It is wrong for `flock -c`. Its manual page says that `-c` will "Pass a single command, without arguments, to the shell with -c". So `flock x -c "true; git push -f"` ran a forced push, and the gate let it through. The same held for a redirection or a `&&` in that string.

No other default wrapper has a command option. `sudo -s` and `sudo -i` do hand a command to a shell. But sudo's manual says they first escape each character except letters, digits, `_`, `-` and `$`. So a `;` or a `>` there is text, and a reading as words is right.

The `shells` dial cannot hold `flock`. A shell entry has no field for a positional word, so the lock file would end the reading before `-c`. The rollout plan logged the finding as item 9.43.

## Options

- **A. A field on a wrapper entry.** An optional `shell_text: true` marks a wrapper whose command string a shell runs, and the default `flock` entry has it.
  - **Pros:** exact for each tool, so no ask without need; a project can mark its own wrapper, such as `su -c`; the dials file says it.
  - **Cons:** the dial's shape changes, so its row, its defaults and its failures change too; one more field for a user to type.
- **B. No dial change: every wrapper's string read both ways.** The string is read as words and as shell text, each distinct reading one subcommand.
  - **Pros:** no new field; the hole closes for a project's wrapper too.
  - **Cons:** asks without need where no shell runs, as for `env -S "echo a; rm -rf b"`; two forms of one string can give two findings for one entry.
- **C. A fixed rule in the code for `flock`.** No dial says it.
  - **Pros:** the smallest change; no dial change and no ask without need.
  - **Cons:** a hidden rule a project cannot extend; nothing in the dials file shows why `flock` differs.

## Recommendation

A, as the session that found the hole recommended it. It alone is both exact and explicit, and the dial change is paid once.

## Choice

The decider picked A in that session's chat on 2026-11-13.

One step was added while it was applied, in the spirit of wave 4's reading of a redirection. A table of hard commands ran on main's code and on the new code. Read as shell text alone, `flock /tmp/l -c "rm -${x:+;}rf b"` passed, where main asked: a separator inside an unquoted `${…}` cuts the command. So the reading as words stays beside the new reading, and the change adds readings and takes none away.

## Ruling

<a id="r1"></a>**R1.** An entry of the dial `wrappers` takes an optional field `shell_text`, true or false, false when absent. `true` says a shell runs the string of the entry's command flags. It needs `command_flags`. A value that is not a boolean, or `true` with no `command_flags`, is a configuration failure, C5.

<a id="r2"></a>**R2.** The default `flock` entry has `shell_text: true`, from its manual page. `env -S` stays unmarked, since it runs no shell.

<a id="r3"></a>**R3.** The string of a marked wrapper is also read alone, from its text, as a shell's string is. The words after it are the wrapper's own. Its reading as words, with the words after it appended, stays beside it. So no command that asked before passes now.

<a id="r4"></a>**R4.** A string read in two forms is two pieces. So one command can give two findings for one entry, and it still asks once.

<a id="r5"></a>**R5.** Limit 4 of the module's section 9 no longer names `flock`. It names what still passes: the string of a wrapper that a shell runs, where the wrapper's entry lacks `shell_text: true`.

## Applied

The commit that creates this record applies every item. The record is born `inactive`.

## Carry list

1. R1 — [the module's §7](../../modules/const-interaction/MODULE.md#t7), the row of `wrappers`; [the install note](../../modules/const-interaction/plugin/INSTALL.md), the comment of `wrappers`.
2. R2 — [the module's §7](../../modules/const-interaction/MODULE.md#t7), the list of default wrappers, its item on `flock`; [the module's §5](../../modules/const-interaction/MODULE.md#t5), its sentences on a wrapper's string.
3. R3 — [the module's §5](../../modules/const-interaction/MODULE.md#t5), its sentences on a wrapper's string.
4. R4 — [the module's §5](../../modules/const-interaction/MODULE.md#t5), its last sentence on a wrapper's string.
5. R5 — [the module's §9](../../modules/const-interaction/MODULE.md#t9), limit 4, under "Not seen, and passes".
