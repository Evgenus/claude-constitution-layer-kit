---
id: dec-0049-module-links-held-by-a-kit-check
type: task-record
title: A kit check holds the link to a module outside module prose
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# A kit check holds the link to a module outside module prose

## Context

The full carry audit of [dec-0048-frozen-documents-take-wording-edits](dec-0048-frozen-documents-take-wording-edits.md), pinned at `0670486` on 2026-09-28, found the plain form "module `const-x`" in kit documents at odds with [rule 4 of plc-0007-requirements](../policies/plc-0007-requirements.md#r4) and with ruling R11 of [dec-0005-reference-forms](dec-0005-reference-forms.md#r11): outside module prose, a kit document cites a module by a link to its specification anchor. The tree held 121 plain uses outside `modules/`, and no gate read the form. The decider chose on 2026-09-28 to keep the rule as written. The change merged at `8539c75` linked 110 of those uses by script, 28 of them in accepted records as a reference-form migration. It left the placeholder `const-x`, the seven uses in frozen comparisons, which no edit of [rule 7 of plc-0005-research](../policies/plc-0005-research.md#r7) reaches, and the three in the placeholder text of the policy template, where a link written for `templates/` breaks once the text is copied into `docs/policies/`.

What should hold the rule from now on was left open. The session had offered a lane of module [`const-referencing`](../requirements.md#const-referencing), and the lane turned out not to fit: the module's lint matches a lane on text whose code spans are blanked, so the plugin name in "module `const-x`" is never seen, and a pattern on the blank run matches the linked form too, since links are blanked as well.

## Options

- **A. Review only.** No gate; the rule is held by the reader of each change, as the other unchecked rules are.
  - **Pros:** nothing to build, record or test.
  - **Cons:** the same rule drifted 121 times with no gate, so it drifts again.
- **B. A lane that reads code spans.** Lanes of module [`const-referencing`](../requirements.md#const-referencing) gain one key under which the pattern is matched on text where code spans stay readable and links stay blanked, and the kit adds a lane for the form, its home module prose, the templates and the frozen comparisons.
  - **Pros:** the check runs at write time and in the scan, in the tool that already holds the kit's reference forms; a consumer whose handles stand in code spans gains it too.
  - **Cons:** a new lane key is a name others type, so a module change with fixtures and a carry audit; machinery in a module for one form of the kit's.
- **C. A kit-only check.** `scripts/check-module-links.py`, never shipped in a module, one line of the gate list beside `scripts/check-yaml-style.py`.
  - **Pros:** no module changes; small, with a narrow self-test.
  - **Cons:** it runs when the gate list runs, never at write time; the kit's reference forms are held by two tools.

## Recommendation

B, by the session: the kit declares its reference forms as lanes, so this form belongs there, and the module change is one key and one choice of masked text.

## Choice

C, chosen by the decider in chat on 2026-09-28, against the session's recommendation. The session's objection stands: the kit's reference forms are now held by the lanes and by a separate script, and a plain mention written in a session is found only when the gate list runs, not when it is written.

## Ruling

<a id="r1"></a>**R1.** Outside module prose — the files under `modules/` and `module-template/` — a kit document cites a module by a link to its specification anchor, with the plugin name as text. Two places are excepted. A kit template under `templates/` names the module plain and gives the link's path from the copy's folder in a code span, since its text is copied into another folder where a relative link would break. A frozen comparison keeps the form it was frozen with.

<a id="r2"></a>**R2.** The gate is `scripts/check-module-links.py`, kit development tooling never shipped in a module. It reads the Markdown files git lists outside `modules/`, `module-template/`, `docs/research/` and `templates/`, and there the plugin name after the word "module" or "modules", with a small or a capital m; a name standing alone, or the second of a plural, is left to review. It skips fenced code, a link, a code span that holds the mention, and a name that is no directory under `modules/`. It exits 2 with the file, the line and a teaching message on each plain mention, 0 with the counts examined, and 1 when it could not run; `--self-test` is its fixture. It is one line of the gate list, run before every commit that touches a document, never at write time, and by hand until the kit's CI runs it; it is listed in the routine of `pyproject.toml`.

<a id="r3"></a>**R3.** The check runs in the kit's CI with the other kit checks once CI is wired.

<a id="r4"></a>**R4.** The lanes of module [`const-referencing`](../requirements.md#const-referencing) are not widened to read code spans.

## Applied

The commit that creates this record adds the script, states R1 and R2 in rules 4 and 9 of [plc-0007-requirements](../policies/plc-0007-requirements.md) and in the reference bullet of [CLAUDE.md](../../CLAUDE.md), adds the check to the gate list of the `gate-list-runner` agent and to the routine of [pyproject.toml](../../pyproject.toml), and names it in step 10 of the [rollout plan](../rollout-plan.md#s10). The fix rounds of its carry audit corrected it in place before its yes. They widened the check to a small or a capital m and to the plural's first name, and linked the three mentions the widened check found — two in rule 6 of [plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6), one in an accepted record by a reference-form migration. They stated R1 for an accepted record in that rule 6, and named the check in the row of [requirement A5.6](../requirements.md#a5-6). They also sharpened the texts that state R1 and R2. The record is born `inactive`.

## Carry list

1. R1 — [rule 4 of plc-0007-requirements](../policies/plc-0007-requirements.md#r4); the reference bullet of [CLAUDE.md](../../CLAUDE.md); for an accepted record, [rule 6 of plc-0004-decision-records](../policies/plc-0004-decision-records.md#r6).
2. R2 — [the gate itself](../../scripts/check-module-links.py), its docstring stating what it reads, what it skips, its modes and its exits; [rule 4](../policies/plc-0007-requirements.md#r4) and [rule 9 of plc-0007-requirements](../policies/plc-0007-requirements.md#r9); the enforcement cell of [requirement A5.6](../requirements.md#a5-6); the reference bullet of [CLAUDE.md](../../CLAUDE.md); the routine list of [pyproject.toml](../../pyproject.toml).
3. R3 — pending: [step 10 of the rollout plan](../rollout-plan.md#s10), the CI wiring.
4. R4 — history only: the option not chosen, whose reason [rule 4 of plc-0007-requirements](../policies/plc-0007-requirements.md#r4) states.
