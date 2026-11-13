---
id: dec-0134-line-counts-in-the-metrics-report
type: task-record
title: The metrics report counts the lines of the files the kit maintains, with cloc, in a mode run by hand
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The metrics report counts the lines of the files the kit maintains, with cloc, in a mode run by hand

## Context

On 2026-11-13 the decider asked for one command that counts, with `cloc`, the lines of the files the kit maintains. A file the kit maintains is one a person writes and keeps, as against a generated or pinned file. The decider asked for the files to be split into groups, and each group's file types to be counted apart.

The decider and a session agreed the groups in chat. The decider also asked for the count to be fast, and allowed it to be a mode of `scripts/metrics.py`. R1 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r1) says what that script measures. A new mode of it changes the kit's harness, so this is a `process` change under [law 9 of CLAUDE.md](../../CLAUDE.md#law-9).

A full `cloc --by-file --json` run over the kit takes under a second. One run, grouped by the script, is fast enough to run by hand at any time.

## 1. How detailed the output is

### Options

- **A. One table per group.** For each group, one row per file type, then a total.
  - **Pros:** short output; the default mode of the script already gives each module's code and test lines.
  - **Cons:** it does not show which module is large.
- **B. A tree of group, part and file type.** In the groups under `modules/` a part is a module folder; in the others it is a named part of the group.
  - **Pros:** the size of each module, and of each part of the kit's tooling and documents, by file type.
  - **Cons:** about four times longer; it partly repeats the default mode.

### Recommendation

A, recommended by the session: the default mode already gives the numbers per module.

### Choice

The decider chose B in chat on 2026-11-13. The decider asked to read the size of each module, and the tree reads at any depth.

## 2. Where the command lives

### Options

- **A. A mode of `scripts/metrics.py`.** The script gains `--loc`, and the `justfile` gains `loc`.
  - **Pros:** one report script; it reuses the script's git and JSON code; the mode sits beside the other numbers of the kit.
  - **Cons:** the script grows by about 270 lines; a change of a recorded report needs this record.
- **B. A script of its own.** A new `scripts/loc.py`, and the `justfile` gains `loc`.
  - **Pros:** a routine change, with no record; the metrics script stays as it is.
  - **Cons:** a second report script with its own git and JSON code.

### Recommendation

A, recommended by the session, since the decider allowed it: one report script keeps the kit's numbers in one place.

### Choice

The decider chose A in chat on 2026-11-13, in the message that chose the tree.

## Ruling

<a id="r1"></a>**R1.** `scripts/metrics.py --loc` counts the lines of the files the kit maintains, with `cloc`, and prints them as one tree: group, then part, then language. Each line gives files, blank, comment and code lines, and a totals line ends the tree. With `--json <path>` it also writes the same numbers as JSON, and with `--json -` it prints the JSON alone. The script's docstring defines the mode.

<a id="r2"></a>**R2.** The files are those git tracks. A symbolic link is left out, since it would count the shared code twice. So are the files of `GENERATED` in the script. They are the lock file of `ccusage`, the eval receipts, and the pins of Claude Code and of the eval model. They are also the empty marker `py.typed`, `LICENSE`, `NOTICE` and `.gitignore`.

<a id="r3"></a>**R3.** Five groups hold the files: `plugins`, `module-dev`, `shared`, `tooling` and `docs`. The table `PARTS` of the script gives each group's parts and their patterns. A file falls in the first part whose pattern matches it, so a narrow part stands before a broad one. In `plugins` and `module-dev` a part is a module folder, and `module-template` is one more part of `module-dev`. A file that no pattern matches falls in the group `other`, so a new folder shows up and is never lost.

<a id="r4"></a>**R4.** `cloc` runs once over the files, with `--skip-uniqueness`, so that the modules' identical files each count. It runs once more for each language of `NAMED_LANGUAGE` that names a tracked file, over those files, since `cloc` cannot tell them by name. The `justfile` is counted as make there. A file `cloc` knows no language of is left out of every count, and a note on stderr names it. The numbers are `cloc`'s, and so a Python docstring counts as comment.

<a id="r5"></a>**R5.** The mode is advisory in the sense of [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): no number is a threshold, and no check holds one. CI does not run it, and it is no entry of the gate list. It needs `cloc` on `PATH`. Where `cloc` does not start or gives no JSON, it exits 1 with a line that says what failed, why and the fix.

<a id="r6"></a>**R6.** The kit's `justfile` runs the mode as `just loc`, its arguments passed on to the script.

<a id="r7"></a>**R7.** The mode has no self-test, as R3 of [dec-0087-module-metrics-report](dec-0087-module-metrics-report.md#r3) rules for the whole script. No list runs it, so a self-test would be a test that nothing runs. CI runs the default mode and `--complexity`, and a person runs `--loc` by hand, where its output shows. The kit's `lint` and `types` entries hold its code.

## Applied

The commits before the one that creates this record built the mode and the recipe. The first commit built ten categories; the second replaced them with the five groups the decider agreed. The record is born `inactive`.

## Carry list

1. R1, R2, R3, R4, R5 — [`scripts/metrics.py`](../../scripts/metrics.py), its docstring of `--loc`, and the tables `GENERATED`, `NAMED_LANGUAGE`, `GROUPS` and `PARTS`.
2. R6 — [the `justfile`](../../justfile), the recipe `loc`.
3. R7 — [`scripts/metrics.py`](../../scripts/metrics.py), its docstring, the paragraph "No --self-test".
