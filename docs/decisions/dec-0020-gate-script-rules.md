---
id: dec-0020-gate-script-rules
type: task-record
title: Gate-script rules at harness level — fifteen rules for the Python scripts a module ships
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Gate-script rules at harness level

## Context

The first gate script, written for [`const-meta-types`](../requirements.md#const-meta-types) on 2026-09-18, worked and was tested, yet the decider found it hard to read: one file of 600 lines, a 90-line check function, error texts scattered as inline format strings, which the fresh-context validation had to compare against the module document by hand. A restructuring the same day fixed the shape but left the question of what every later module's script should look like. Two surveys answered it. The public one read the code of community hook collections, Anthropic's own example plugins ([anthropics/claude-code plugins](https://github.com/anthropics/claude-code/tree/main/plugins)), three Python hook libraries, and the official [hooks reference](https://code.claude.com/docs/en/hooks) and [plugins reference](https://code.claude.com/docs/en/plugins-reference). The second was the decider's own earlier trial build of a constitution layer, used as a clue set in the sense of [dec-0010-module-research-per-module](dec-0010-module-research-per-module.md): its lessons enter here only where a public source or this session's evidence carries them.

Findings that shaped the rules:

1. The official documentation shows no Python and never mentions `uv`; Anthropic's Python plugins invoke plain `python3`, one through a shell shim that probes for the interpreter.
2. Every surveyed Python hook collection fails open — a broken hook exits 0 — justified as never breaking a session. The platform already gives that for free: any exit other than 0 and 2 is non-blocking and shows a notice ([hooks reference](https://code.claude.com/docs/en/hooks)). Two surveyed scripts use exit 1 to block, which the documentation warns does not block.
3. A package directory beside the entry point imports with no path manipulation, because Python puts the script's directory first on the import path ([sys.path initialization](https://docs.python.org/3/library/sys_path_init.html)); the path hacks seen in the wild come from importing sibling scripts.
4. `argparse` exits with status 2 on a usage error ([argparse, exiting methods](https://docs.python.org/3/library/argparse.html#exiting-methods)), the status reserved here for findings.
5. Error texts held as format templates fail at run time, on the rarely exercised red path, when a placeholder is misnamed; held as functions with typed parameters they fail under a type checker at development time.
6. This session's fixture runner asserted only that a red case was red, so a red failing for an unintended reason would have passed; and only `python3` had an absence fixture, not git or PyYAML.
7. Plugins get a persistent directory outside the repository, `${CLAUDE_PLUGIN_DATA}`, exported to hook processes ([plugins reference](https://code.claude.com/docs/en/plugins-reference)); `hooks.json` has an exec form (`command` plus `args`) that the documentation says to use whenever a path placeholder appears ([hooks reference](https://code.claude.com/docs/en/hooks)).

## Options

- **A. Adopt all fifteen rules** into [template §6](../../module-template/MODULE.md#t6), and conform the first module.
  - **Pros:** every rule is proven in a working build or in Anthropic's plugins; closes the two fixture gaps and the template-placeholder defect class; the next modules copy a sound example.
  - **Cons:** the largest rework, roughly a third more lines; a long sub-slot in the template.
- **B. Adopt only the rules that change verdicts or reviewability** (messages, exit codes, runtime, no fail-open, fixtures).
  - **Pros:** short; mechanically checkable.
  - **Cons:** leaves out the structural lessons; the script stays one long file.
- **C. No harness rules yet;** fix the gaps in the one module.
  - **Pros:** no template change before a second module tests the rules.
  - **Cons:** the friction had already appeared twice.

Recommendation A. Chosen A by the decider in chat on 2026-09-18, with these amendments of his: the Python floor is 3.12 (the session proposed 3.9, then 3.11 for `StrEnum`; 3.13 was set aside because the decider's own interpreter is 3.12 and no current long-term distribution ships it; 3.11 because it is in its last supported year, [Python release status](https://devguide.python.org/versions/)); dependencies are unrestricted but declared; no abstract dictionary crosses a function boundary; parameters are parsed with `argparse`. The session's rule "a gate writes no log files" was reversed — a blocked write leaves no trace in git, a `warn` finding and a configuration failure leave none either, so everything a gate prints is also appended to a log, which may sit in a git-ignored place inside the repository.

## Ruling

The fifteen rules are stated in [template §6](../../module-template/MODULE.md#t6) under "Gate-script rules", with the fixed dial `log_dir` in [template §7](../../module-template/MODULE.md#t7); [CLAUDE.md](../../CLAUDE.md) step 4 of "Developing a module" points there. In short: thin entry point over a package beside it; one messages module of typed functions; one exit point behind one guard; named exit codes with `argparse` overridden to exit 1; parse, check, report separated; plain `python3` at floor 3.12 with a preflight on every invocation; declared dependencies and `yaml.safe_load` only; no fail-open; dataclasses, enums and full annotations under `mypy --strict`; the docstring as contract; exec-form hook wiring with a timeout; an output log; paths taken from the tool input; fixtures as numbered case records asserting the taught message; an absence fixture per external tool. Python package and module names are snake_case because the language requires identifiers; entry-point files stay kebab-case ([kernel §7](../../kernel/CONVENTIONS.md#k7)). A `ruff` and `mypy` configuration at the kit root is a development routine of this repository, never visible to consumers.

Applied in the commit that creates this record: the template and [CLAUDE.md](../../CLAUDE.md). The first module conforms in the commits that follow.
