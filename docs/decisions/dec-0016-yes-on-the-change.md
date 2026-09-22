---
id: dec-0016-yes-on-the-change
type: task-record
title: The process-stakes yes is given on the change — PR approval where a PR flow exists, otherwise named in the commit message
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The `process`-stakes yes is given on the change — PR approval where a PR flow exists, otherwise named in the commit message

## Context

[Kernel §4](../../kernel/CONVENTIONS.md#k4) priced `process` stakes as a record plus "one human yes in the PR", and [law 9 of CLAUDE.md](../../CLAUDE.md#law-9) repeated it. The pre-module audit of 2026-09-18 found the kit itself with no remote and no branches: every commit lands on main, and every yes so far was given in chat and named in the commit message. The same gap awaits the first consumer, a greenfield solo project with no PR flow on its first day. [Requirement A3.3](../requirements.md#a3-3) leaned on a protected branch for the immutability of records.

## Options

- **A. Set up the PR flow now.** Remote, protected main, branch per change, the yes as PR approval.
  - **Pros:** the stated ceremony becomes real; immutability enforced.
  - **Cons:** branch and PR overhead on sentence-sized rulings for a solo decider; nobody depends on main before Phase D.
- **B. Kit regime: chat yes named in the commit; main unprotected.**
  - **Pros:** matches practice; zero overhead.
  - **Cons:** the kit tells consumers a ceremony it does not follow.
- **C. B until publication, A from Phase D.**
  - **Pros:** overhead arrives with the thing it protects.
  - **Cons:** the kernel text still names a PR for a solo consumer who has none.
- **D. Local branches merged `--no-ff` after the yes, no remote.**
  - **Pros:** history shows the approval point.
  - **Cons:** nothing stops a direct commit.
- **E. Generalize the kernel wording, follow C's schedule.** The yes is given on the change: PR approval where a PR flow exists, otherwise named in the commit message that lands it.
  - **Pros:** one rule a solo consumer can obey; the kit's practice becomes conforming rather than exempt; C's sunset kept.
  - **Cons:** a kernel edit and a record; a commit-message yes is weaker evidence than an approval.

## Recommendation

E: the gap is not the kit's alone, and a rule only teams can follow is a rule the kernel should not state.

## Choice

E, chosen by the decider in chat on 2026-09-18.

## Applied in the same commit

- [Kernel §4](../../kernel/CONVENTIONS.md#k4): the `process` row.
- [CLAUDE.md](../../CLAUDE.md): [law 9 of CLAUDE.md](../../CLAUDE.md#law-9) and step 6 of the module routine.
- [kit-decision-records](../policies/plc-0004-decision-records.md): rule 4, the kit's regime and its sunset at Phase D.
- Rollout plan Phase D: the remote, protected main, and PR flow become its first step.
- [Requirement A3.3](../requirements.md#a3-3): immutability by convention until a PR flow exists.
