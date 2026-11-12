---
id: dec-0022-output-log-through-logging
type: task-record
title: The output log of a gate is built on the standard library's logging
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The output log of a gate is built on the standard library's logging

## Context

Gate-script rule 12 of [template §6](../../module-template/gate-script-rules.md#r12) says what the output log holds and where it goes ([dec-0020-gate-script-rules](dec-0020-gate-script-rules.md)). It did not say how. The first implementation, in [`const-meta-types`](../requirements.md#const-meta-types), was a hand-written class that printed a line and appended a line, with its own rotation and, after a validation finding, its own buffering. The decider asked on 2026-09-18 why the standard library's `logging` had not been used. There was no reason: the session had not weighed it.

## Options

- **A. Keep the hand-written class**; leave the mechanism to each module.
  - **Pros:** nothing to change; both surveyed precedents, Anthropic's `security-guidance` plugin and the decider's trial build, print and append by hand.
  - **Cons:** rotation, buffering and failure handling are re-implemented and re-tested per module; not what a Python reader expects to find.
- **B. Build it on `logging`, and say so in the rule.**
  - **One named logger** with propagation off;
  - **two stream handlers** split by level;
  - **a [`MemoryHandler`](https://docs.python.org/3/library/logging.handlers.html#memoryhandler)** holding records until the log location is known;
  - **a [`RotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler)** as its target;
  - **[`logging.raiseExceptions`](https://docs.python.org/3/library/logging.html#logging.raiseExceptions) switched off**.
  - **Pros:**
    - **rotation and buffering** become library behaviour;
    - **about the same number of lines**;
    - **the familiar tool**;
    - **the module's five log fixtures** passed unchanged after the swap.
  - **Cons:**
    - **the stream a line goes to is protocol**, not severity, so the level only carries the caller's choice;
    - **`logging` is process-global state**, so the logger must be named and must not propagate, or another library's line could reach stdout and break the one-JSON-object contract of severity `warn`;
    - **`raiseExceptions` must be switched off explicitly**, because its default prints a traceback to stderr, whose first line is what the user sees in hook mode.

Recommendation B. Chosen B by the decider in chat on 2026-09-18 ("both": the swap in the module, and the rule).

## Ruling

Rule 12 names the mechanism and its three cautions. Applied in the commit that creates this record: [template §6](../../module-template/gate-script-rules.md#r12) rule 12, and the `output` module of `const-meta-types`.
