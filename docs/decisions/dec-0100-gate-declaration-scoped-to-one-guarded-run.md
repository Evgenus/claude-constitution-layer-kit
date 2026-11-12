---
id: dec-0100-gate-declaration-scoped-to-one-guarded-run
type: task-record
title: A gate declares itself, its dials file included, in a context variable for one guarded run
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A gate declares itself, its dials file included, in a context variable for one guarded run

## Context

R10 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r10) made the name of the dials file a gate reads a context variable of the shared package with no default, declared once per process through `declare_dials_file`. The decider had asked for that on 2026-10-22: no default, and no patched global. Beside it, `identity.py` kept the gate's own declaration in a module global, `_declared`, which the guard sets once through `declare`: the `Identity`, the mode of the run and, in hook mode, the run's deadline. R3 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r3) calls it the package's one global of its own. A second, different declaration is a defect, as that ruling and R2 of [dec-0084-one-deadline-per-hook-run](dec-0084-one-deadline-per-hook-run.md#r2) say.

Reading the code, the decider asked on 2026-10-22 why the name is a context variable and the declaration is not, and why the name is not part of the declaration. Facts read that day:

1. The difference came from history, not from design: the change of dec-0099 left `_declared` as it was.
2. Each process runs one gate, and neither the shared code nor any plugin script uses threads or asyncio. The two behave alike in a gate.
3. The one practical difference is in the tests: the shared items try an undeclared, an empty and a second name inside `contextvars.Context().run`, which they cannot do for the identity.
4. Option A of section 3 of dec-0099 offered the name as an optional field of the identity with a default, which the decider turned down. A required field was never offered.
5. Before the first release nothing is promised. After it, a new required field of `Identity` breaks every caller (R3 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r3)).

The session put two questions, one per message, in chat on 2026-10-22 and 2026-10-23. Sections 1 and 2 hold them in order.

## 1. Where the name of the dials file lives

- **A. Keep it as it is.** The name is a context variable of its own, and the declaration a module global.
  - **Pros:** nothing changes; the eval run of that day stays valid.
  - **Cons:**
    - **every module's `start` makes two declarations**, and the defect of a second, different one is written twice;
    - **folding them in after the first release needs a new major**.
- **B. A required field of `Identity`, in the global declaration.**
  - **Pros:** one declaration and one rule in one place; a smaller change than C.
  - **Cons:**
    - **it drops the context variable the decider asked for**, so the name lives in a module global again, set once and never patched;
    - **the tests lose their isolation of the name**;
    - **the shared code changes**, so every eval receipt goes stale.
- **C. A required field of `Identity`, and the whole declaration in a context variable with no default.**
  - **Pros:**
    - **one declaration**;
    - **no module global holds a gate's state**;
    - **it keeps the decider's terms of 2026-10-22**, a context variable, no default, nothing patched;
    - **the tests can isolate an identity as they isolate the name**.
  - **Cons:** the widest change: `identity.py`, every module's `start`, the shared items on the declaration, the shared page, R10 of [dec-0099-shared-code-installed-as-a-pip-package](dec-0099-shared-code-installed-as-a-pip-package.md#r10), another confirming read and a new eval run of every module.

The session recommended C: it removes the difference and extends to the whole declaration what the decider asked for the name, at the last moment before the first release when a required field breaks no caller. The decider chose C in chat on 2026-10-22. The decider also asked where the variable is set and reset: a calling context in which the value exists, not one from a moment until the process ends.

<a id="r1"></a>**R1.** `Identity` has a required field `dials_file`, with no default, after `plugin_root`: the name of the dials file the gate reads, relative to the repository's top. Each module of this kit names `constitution.yaml` in it. The shared code reads the name from the declared identity alone; `declare_dials_file` and the context variable that held the name alone leave `identity.py`.

<a id="r2"></a>**R2.** The gate's declaration is held in one context variable of the shared package, with no default: the identity, the mode of the run and, in hook mode, the run's deadline. No module-level name holds it, and nothing patches it. This replaces "the package's one global of its own" in R3 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r3).

## 2. The scope of the declaration, and a scope inside another

The session proposed the scope. One context manager of the shared package sets the variable and resets it. The guard, which every entry point reaches, opens it around everything it does. The entry file's lines before the guard read no declaration, and a module's tests open one scope for their session. The session put the one choice the proposal left open: what a scope opened inside another one does.

- **A. Always a defect.** A scope opened inside an open one raises `RuntimeError`, even with the same declaration.
  - **Pros:** one run, one declaration, no exception to learn; nothing needs nesting today.
  - **Cons:** a later test of the guard in the tests' own process must run in a fresh context, not inside the tests' scope.
- **B. The same declaration reused, another a defect.** Today's rule, scoped: a nested scope of the same declaration keeps the outer deadline and resets nothing.
  - **Pros:** a test's scope and a guard's run in one process may declare the same identity.
  - **Cons:** it keeps a rule that existed only because test files declared at their top; two paths in the context manager.
- **C. A scope inside another shadows the outer one until it closes.** A stack, as the tokens of a context variable behave.
  - **Pros:** the simplest code; any nesting works.
  - **Cons:**
    - **a run inside an outer scope acts under its own declaration with no defect raised**;
    - **the check that one process is one gate is gone**.

The session recommended A: a second, identical declaration was tolerated only because test files and entry points declared in one process, which the scope removes. The decider took the proposal and chose C in chat on 2026-10-23, with no reason given. The session keeps no objection: only the guard, the tests and the kit's own tooling open a scope, the guard once per run.

<a id="r3"></a>**R3.** The declaration exists only inside a scope. A context manager of the shared package, `identity.declared(identity, mode)`, sets the variable when the scope opens and resets it when the scope closes, normally or by an exception. In hook mode the opening starts the run's deadline, as R2 of [dec-0084-one-deadline-per-hook-run](dec-0084-one-deadline-per-hook-run.md#r2) says of the declaration. Outside every scope, a read of the identity or of the dials file's name is a defect of the caller, a `RuntimeError`; the mode reads as none, and no wait has a deadline.

<a id="r4"></a>**R4.** The guard, `cli.guarded`, which every entry point reaches, opens the scope around all it does: the output, the parse of the arguments, the preflight, the import of the module's modes, the run, the failure lines and the flush. The scope closes before the guard returns the exit code. The entry file's own lines before the guard read no declaration: `C1`, `C14` and `C15`, and `C16` and `C17` from `cli.version_failure`.

<a id="r5"></a>**R5.** A scope opened inside another shadows the outer declaration until it closes, and the outer one holds again after it. A second declaration is no defect, whether it differs or not. This replaces the defect of a second, different declaration in R3 of [dec-0076-hooks-give-each-shared-git-call-a-budget](dec-0076-hooks-give-each-shared-git-call-a-budget.md#r3) and in R2 of [dec-0084-one-deadline-per-hook-run](dec-0084-one-deadline-per-hook-run.md#r2).

<a id="r6"></a>**R6.** A module's tests run inside one scope of the module's identity, with no mode. An autouse session fixture of the module's `tests/conftest.py` opens it for the test session, with the identity that the top of the test file names. The conftest also imports the test file inside a scope of that identity, since some test files build expected messages as they are imported, before any fixture runs. An item that needs another declaration opens its own scope inside it, and one that needs none runs in a fresh context. The declarations at the top of the test files leave. This narrows R2 of [dec-0091-module-fixtures-run-as-pytest](dec-0091-module-fixtures-run-as-pytest.md#r2): the conftest defines that fixture beside `subject`, and the top of the test file names the identity instead of declaring it.

## Applied

The record was born `active`: its questions were decided one per message, and its rulings were applied in the commits of the same change that followed it. Once every ruling had its home, the commit that fixes what the carry audit found sets it `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`, and [§2](../../shared/GATE.md#g2), item 1; [identity](../../shared/constitution_layer_kit/identity.py), `Identity`.
2. R2 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`; [identity](../../shared/constitution_layer_kit/identity.py), its docstring. That it replaces a clause of R3 of dec-0076-hooks-give-each-shared-git-call-a-budget is history.
3. R3 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`, and [§4](../../shared/GATE.md#g4), limit 16; [identity](../../shared/constitution_layer_kit/identity.py), `declared`.
4. R4 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), items 1 and 6; [cli](../../shared/constitution_layer_kit/cli.py), `guarded`.
5. R5 — [kit-shared-gate-code §1](../../shared/GATE.md#g1), the row of `identity`; [identity](../../shared/constitution_layer_kit/identity.py), `declared`. What it replaces is history.
6. R6 — [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 8. What it narrows is history.
