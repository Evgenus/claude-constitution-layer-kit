---
id: dec-0026-imports-at-the-top
type: task-record
title: Gate-script rule 16 — imports stand at the top of a module; one inside a function needs an explicit necessity, stated at the import
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Gate-script rule 16 — imports stand at the top of a module

## Context

[dec-0020-gate-script-rules](dec-0020-gate-script-rules.md) fixed fifteen rules for the Python scripts a module ships, stated in [template §6](../../module-template/MODULE.md#t6). Reviewing the code after the shared gate code was extracted ([dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md)), the decider added one more, in chat on 2026-09-20: avoid runtime imports in functions and methods unless they are explicitly necessary. No real choice existed; this record states the ruling and the reasoning, with no manufactured options.

## Ruling

1. **Rule 16.** Every import stands at the top of its module. An import inside a function or a method is allowed only when it is explicitly necessary, and then the reason is written at the import.
2. **The check is the standard tool's.** `ruff` rule `PLC0415` (import outside the top level) is selected in the kit's `pyproject.toml`; a necessary exception carries `# noqa: PLC0415` with its reason in a comment beside it. The rule is deterministic, so it is held by a tool and not by review.
3. **The code as it stands has one necessary case,** twice: `load_modes` in each module's `start`, which imports the module's two modes after the shared preflight. At the top of the file the import would pull in the declared libraries before the preflight has run, and a missing library would reach the user as a traceback instead of the designed configuration failure. Both are marked and reasoned. No other import inside a function exists in `shared/`, `modules/` or `scripts/`.

## Reasoning

An import inside a function hides a dependency from three readers at once: the person reading the top of the file, the type checker and linter, which resolve cycles and unused names from module-level imports, and the preflight, whose promise is that every library a gate needs is imported — or reported missing — before any verdict is printed. It also moves an `ImportError` from start-up into the middle of a run, where in hook mode it is an unexpected failure: exit 1, non-blocking, the write proceeds. A gate should fail at the door, not halfway through a verdict. The exception is exactly the case where the order of imports is the design: what must not be imported before a check has made its failure teachable.

Not covered by the tool, and left to review: `importlib.import_module` called on purpose — the preflight's own job — is a call, not an import statement.

## Applied

In the commit that creates this record: rule 16 in [template §6](../../module-template/MODULE.md#t6); the count and the list in step 4 of "Developing a module" in [CLAUDE.md](../../CLAUDE.md); `PLC0415` in `pyproject.toml`; the two marked imports; the decisions sections of both module documents; item 2 of [kit-shared-gate-code §2](../../shared/GATE.md#g2). The record is born `inactive`.
