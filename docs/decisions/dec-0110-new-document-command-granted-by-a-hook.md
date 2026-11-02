---
id: dec-0110-new-document-command-granted-by-a-hook
type: task-record
title: Module const-locations grants its own create command by a hook, a third kind of artifact named grant
status: active
stakes: process
decider: Eugene Chernyshov
---

# Module const-locations grants its own create command by a hook, a third kind of artifact named grant

## Context

The skills `new-document` and `new-kind` of module [`const-locations`](../requirements.md#const-locations) tell the model to run the module's command, `sh ${CLAUDE_PLUGIN_ROOT}/scripts/new-document.sh …`. Each skill carried `allowed-tools` naming that command, so that the command would run without a prompt. On 2026-11-02 the consumer-live proof of [step 5 of the rollout plan](../rollout-plan.md#s5) loaded the modules by `--plugin-dir` in a headless session on a clone of the first consumer project. Every call of the command was refused: "This command requires approval".

The experiments of [res-0014-const-locations](../research/res-0014-const-locations.md) found why, on Claude Code 2.1.282. The grant of a skill's `allowed-tools` reaches the command when a person types the skill as a slash command, or approves its load at the prompt. It does not reach the command when a permission rule approves the load. Every headless session that loads the skill needs such a rule, and the prompt's own "Yes, and don't ask again" saves one, so a person who picks it would lose the grant too; that last step was inferred and not run. The changelog of Claude Code 2.1.295, a release after the kit's pin, names a fix of a skill's `allowed-tools` being dropped in `-p` runs, which may be the cause; the choice below does not depend on it. The field also makes the model's load of the skill ask for approval, which a skill without the field does not. With no rule at all, the model wrote the document by hand, the act the module exists to prevent. The module document already stated the limit for headless sessions, and its install note taught the allow rule. That rule names the plugin's install folder, which holds the version, so it stops matching at every version update.

The experiments compared four ways out. Option C needed one more ruling: [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) declares every artifact `gate` or `advisory`, and a hook that answers `allow` is neither.

## 1. How the module's command gets its permission

- **A. A command on the plugin's `bin/`, and no `allowed-tools`.** The consumer adds one rule that names no path.
  - **Pros:** one rule that survives every version update; no code that decides a permission.
  - **Cons:** the typed form needs the rule too; a program of the same name earlier on the `PATH` runs instead; `claude plugin eval` does not put `bin/` on the `PATH`, so the kit's eval cannot prove it; `bin/` is a part no module has yet.
- **B. No `allowed-tools`, the command as it is.** The skills load with no rule, and the consumer allows the command.
  - **Pros:** the smallest change.
  - **Cons:** the one rule a consumer can write either names the version's folder or, as a wildcard, also runs a script planted in the project.
- **C. A hook that answers `allow` for the module's own command alone, and no `allowed-tools`.** A `PreToolUse` hook on the shell tool matches the command by an allowlist and says nothing for any other call.
  - **Pros:** no rule for the consumer, in a headless or an interactive session, for the model's load and the typed form; a deny rule the consumer writes still wins; fixtures can prove both halves of its allowlist.
  - **Cons:** the module gains its first hook, which grants a permission the consumer did not write; the pattern is a safety boundary, since an answer of `allow` skips the platform's split of a compound command; the hook starts for every shell call that starts a subcommand with `sh`.
- **D. No change to the module.** The finding is closed as a proof that skipped the install note's rule.
  - **Pros:** no work beyond the documents.
  - **Cons:** consumers keep three rules, one of them tied to the version, and a person who picks "don't ask again" would lose the grant.

The session recommended C: it was the only option that worked in every setting tested with no rule from the consumer, and its risk is held by an allowlist, which grants nothing it does not name. The decider chose C in chat on 2026-11-02.

<a id="r1"></a>**R1.** Module [`const-locations`](../requirements.md#const-locations) ships a `PreToolUse` hook on the shell tool, the grant `grant-new-document`. It answers `allow` for a command that is exactly `sh <plugin root>/scripts/new-document.sh` followed by zero or more arguments, one space before each, each written plain — ASCII letters, digits and `_ . / : , @ + -` — or in single quotes with no single quote, line break, carriage return or NUL inside. The plugin root is the one the platform names to the hook in `CLAUDE_PLUGIN_ROOT`, an absolute path of ASCII letters, digits and `_ . / @ + -`; a trailing slash on it changes nothing. A root of any other characters is matched by nothing.

<a id="r2"></a>**R2.** For any other call the grant gives no answer and exits 0, and the platform's own permission flow decides it; it prints only its own configuration failures, which grant nothing. The grant runs the preflight of the module's libraries only once a call is its own command. It reads no dials file and no repository: its output log is the platform's data directory, else nowhere.

<a id="r3"></a>**R3.** Neither skill of the module carries `allowed-tools`. Each tells the model to run the command alone, each value plain or in single quotes, since the plugin approves that form and no other.

<a id="r4"></a>**R4.** A consumer needs no allow rule for the command or for the skills, in any permission mode; in plan mode, where the platform lets no hook approve a command that writes, the command is asked for as any other; the install note says so, and says that a deny or ask rule the consumer writes still wins over the grant.

## 2. How the hook is declared under the law of enforcement honesty

- **A. A third kind, `grant`.** [Law 5 of CLAUDE.md](../../CLAUDE.md#law-5), the template's table of enforcement kinds and its hook row name it.
  - **Pros:** says what the artifact is; keeps "never blurred" literally true; the next module that needs to approve its own command has a named place.
  - **Cons:** amends a law and the template inside a module fix, so the carry audit widens to the records that rule on that law and on the template.
- **B. Declared `advisory`.** It stands beside the module's command, with a note that it judges nothing.
  - **Pros:** no change to the law or the template.
  - **Cons:** advisory means judgment-shaping, and the hook shapes no judgment, so the label would be the blurring the law forbids.

The session recommended A, the explicit form. The decider chose A in chat on 2026-11-02.

<a id="r5"></a>**R5.** [Law 5 of CLAUDE.md](../../CLAUDE.md#law-5) names three kinds of artifact: `gate`, `advisory` and `grant`, and so do the template's table of enforcement kinds and its hook row. A grant is a deterministic answer of `allow`, given by a hook, for a command that the module itself ships. It judges nothing, blocks nothing and is never red.

<a id="r6"></a>**R6.** A grant matches by an allowlist alone, never by a list of forms to refuse, and says nothing for a call outside it. When it cannot run it grants nothing: it exits 1 with its configuration failure and a closing line of its own, and the platform asks for the call as for any other.

<a id="r7"></a>**R7.** The red→green fixture of [law 7 of CLAUDE.md](../../CLAUDE.md#law-7) reads for a grant as both halves: the forms it allows are answered `allow`, and forms outside its allowlist are answered with nothing: one value for each printable ASCII character the allowlist leaves out, a quote joined to a plain word, and another path. Its exit-code split is its configuration failure, exit 1 with nothing granted, against its silence on a call outside the allowlist, exit 0.

<a id="r8"></a>**R8.** A grant reads no dials file, so the location rule of the output log reads for it as the platform's data directory, else nowhere. It examines nothing, so it prints no count line. It runs the library preflight once a call is its own command, before its answer, and its entry's failure lines carry no clause, as a generator's carry none.

<a id="r9"></a>**R9.** The experiments of 2026-11-02 that found the cause and compared the options are history: they are the evidence of res-0014-const-locations.

<a id="r10"></a>**R10.** R1 narrows a default that the Context of [dec-0035-locations-module-rulings](dec-0035-locations-module-rulings.md) took, that the module ships no hook: it ships no hook that blocks or teaches, and one grant.

## Applied

The hook, its entry files, its fixtures and the two skills changed in the commits of the branch `work/new-document-grant-hook` before this record was written. The module document, its install note and README, [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) and the template follow on the same branch. The record is born `active` and is set `inactive` by the last commit of the branch.

## Carry list

1. R1 — [the module document's §6](../../modules/const-locations/MODULE.md#t6), the hook row, and [its §9](../../modules/const-locations/MODULE.md#t9), row E4; [granting](../../modules/const-locations/plugin/scripts/locations_gate/granting.py), `granted`.
2. R2 — [the module document's §6](../../modules/const-locations/MODULE.md#t6), the rows of the hook and of `grant-new-document.py`; [grant-new-document.py](../../modules/const-locations/plugin/scripts/grant-new-document.py), its docstring.
3. R3 — [the skill new-document](../../modules/const-locations/plugin/skills/new-document/SKILL.md), step 3; [the skill new-kind](../../modules/const-locations/plugin/skills/new-kind/SKILL.md), step 2; [the module document's §6](../../modules/const-locations/MODULE.md#t6), the skill rows.
4. R4 — [the module's install note](../../modules/const-locations/plugin/INSTALL.md), step 3.
5. R5 — [law 5 of CLAUDE.md](../../CLAUDE.md#law-5); [the template's §9](../../module-template/MODULE.md#t9) and [its §6](../../module-template/MODULE.md#t6), the hook row.
6. R6 — [the template's §6](../../module-template/MODULE.md#t6), the hook row.
7. R7 — [law 7 of CLAUDE.md](../../CLAUDE.md#law-7); [the template's §10](../../module-template/MODULE.md#t10).
8. R8 — [the template's §6](../../module-template/MODULE.md#t6), gate-script rules 3, 6 and 12, and [its §10](../../module-template/MODULE.md#t10), the examined count; [kit-shared-gate-code §2](../../shared/GATE.md#g2), item 6.
9. R9 — history only: the experiments that found the cause and compared the options.
10. R10 — history only: the narrowing of an earlier default, which binds nothing once R1 is carried.
